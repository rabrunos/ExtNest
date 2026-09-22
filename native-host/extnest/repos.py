import os
import re
import json
import shutil
import subprocess
import hashlib
import base64
import urllib.parse
import sys
from pathlib import Path

from .paths import EXTENSIONS
from .registry import find_by_slug, upsert_repo, get_registry, save_registry
from .github_api import file_text, repo_info
from .oauth import github as github_oauth

def normalize_repo(value):
    value = str(value or "").strip()
    if not value:
        raise RuntimeError("Informe um repositório GitHub.")

    if "://" in value:
        parsed = urllib.parse.urlparse(value)
        if parsed.hostname not in {"github.com", "www.github.com"}:
            raise RuntimeError("A URL precisa ser de github.com.")
        value = parsed.path.strip("/")

    if value.endswith(".git"):
        value = value[:-4]

    parts = [part for part in value.split("/") if part]
    if len(parts) != 2:
        raise RuntimeError("Use owner/repo ou uma URL https://github.com/owner/repo.")

    owner, name = parts
    allowed = re.compile(r"^[A-Za-z0-9_.-]+$")
    if not allowed.match(owner) or not allowed.match(name):
        raise RuntimeError("Nome de repositório GitHub inválido.")

    return f"{owner}/{name}"

def sanitize_slug(repo):
    # owner--repo avoids collisions between repositories with the same name.
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", repo.replace("/", "--")).strip("-").lower()

def expected_extension_id_from_key(key_b64):
    try:
        raw = base64.b64decode(key_b64)
        digest = hashlib.sha256(raw).digest()[:16]
        alphabet = "abcdefghijklmnop"
        return "".join(alphabet[b >> 4] + alphabet[b & 15] for b in digest)
    except Exception:
        return None

def remote_manifest(item):
    try:
        return json.loads(file_text(
            item["repo"],
            "manifest.json",
            item.get("branch") or "main",
            item.get("account_id")
        ))
    except Exception:
        return None

def local_manifest(slug):
    path = EXTENSIONS / slug / "manifest.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def _version_tuple(version):
    values = [int(x) for x in re.findall(r"\d+", str(version))[:4]]
    return tuple(values + [0] * (4 - len(values)))

def version_gt(a, b):
    return _version_tuple(a) > _version_tuple(b)

def register_repo(repo, branch=None, account_id=None):
    repo = normalize_repo(repo)

    try:
        info = repo_info(repo, account_id)
    except Exception as error:
        if not account_id:
            raise RuntimeError(
                "Não foi possível acessar esse repositório sem conta. "
                "Se ele for privado, conecte a conta que possui acesso."
            ) from error
        raise

    # Public repositories deliberately do not retain/use an account token.
    effective_account_id = str(account_id) if info["private"] and account_id else None

    if info["private"] and not effective_account_id:
        raise RuntimeError("Repositório privado exige uma conta GitHub conectada.")

    effective_branch = branch or info["default_branch"] or "main"

    manifest = json.loads(file_text(
        repo,
        "manifest.json",
        effective_branch,
        effective_account_id
    ))

    if int(manifest.get("manifest_version", 0)) < 3:
        raise RuntimeError("manifest.json não é Manifest V3.")

    item = {
        "slug": sanitize_slug(repo),
        "repo": repo,
        "branch": effective_branch,
        "name": manifest.get("name") or repo.split("/")[-1],
        "private": bool(info["private"]),
        "account_id": effective_account_id,
        "source": "github",
        "expected_extension_id": expected_extension_id_from_key(manifest.get("key", ""))
    }
    return upsert_repo(item)

def _git_exe():
    if getattr(sys, "frozen", False):
        root = Path(sys.executable).resolve().parent
        for candidate in (
            root / "git" / "cmd" / "git.exe",
            root / "git" / "bin" / "git.exe",
        ):
            if candidate.exists():
                return str(candidate)

    exe = shutil.which("git")
    if exe:
        return exe

    raise RuntimeError(
        "Git interno do ExtNest Helper não foi encontrado. "
        "Atualize ou reinstale o componente local."
    )

def _auth_header(account_id):
    token = github_oauth.access_token(account_id)
    raw = base64.b64encode(f"x-access-token:{token}".encode("utf-8")).decode("ascii")
    return f"Authorization: Basic {raw}"

def run_git(args, cwd=None, check=True, account_id=None):
    cmd = [_git_exe()]
    if account_id:
        cmd.extend(["-c", f"http.extraHeader={_auth_header(account_id)}"])
    cmd.extend(args)

    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace"
    )
    if check and proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "Erro Git").strip())
    return proc

def _disable_push(path):
    # Defense in depth for every ExtNest-managed clone, public or private.
    run_git(
        ["remote", "set-url", "--push", "origin", "no_push://extnest-read-only"],
        cwd=path
    )

def install(slug):
    item = find_by_slug(slug)
    if not item:
        raise RuntimeError("Extensão não registrada.")

    target = EXTENSIONS / slug
    if target.exists():
        if (target / ".git").exists():
            _disable_push(target)
            return target
        shutil.rmtree(target)

    run_git([
        "clone",
        "--branch", item.get("branch") or "main",
        "--single-branch",
        f"https://github.com/{item['repo']}.git",
        str(target)
    ], account_id=item.get("account_id"))

    _disable_push(target)
    return target

def update(slug):
    item = find_by_slug(slug)
    if not item:
        raise RuntimeError("Extensão não registrada.")

    target = EXTENSIONS / slug
    if not (target / ".git").exists():
        raise RuntimeError("Repositório ainda não foi instalado.")

    dirty = run_git(["status", "--porcelain"], cwd=target).stdout.strip()
    if dirty:
        raise RuntimeError("Há alterações locais. Reverta ou salve suas alterações antes de atualizar.")

    _disable_push(target)
    run_git(
        ["pull", "--ff-only", "origin", item.get("branch") or "main"],
        cwd=target,
        account_id=item.get("account_id")
    )
    return target

def open_folder(slug):
    item = find_by_slug(slug)
    if not item:
        raise RuntimeError("Extensão não registrada.")
    target = EXTENSIONS / slug
    if os.name == "nt":
        os.startfile(str(target))
    else:
        subprocess.Popen(["xdg-open", str(target)])

def status(slug, config_backup_exists=False):
    item = find_by_slug(slug)
    if not item:
        raise RuntimeError("Extensão não registrada.")

    local = local_manifest(slug)
    remote = remote_manifest(item)
    local_version = (local or {}).get("version")
    remote_version = (remote or {}).get("version")
    key = (local or remote or {}).get("key")
    expected_id = expected_extension_id_from_key(key) if key else item.get("expected_extension_id")

    if expected_id and item.get("expected_extension_id") != expected_id:
        data = get_registry()
        for row in data["extensions"]:
            if row.get("slug") == slug:
                row["expected_extension_id"] = expected_id
        save_registry(data)

    return {
        "slug": slug,
        "name": (remote or local or {}).get("name") or item.get("name") or slug,
        "repo": item.get("repo"),
        "private": bool(item.get("private")),
        "account_id": item.get("account_id"),
        "local_exists": bool((EXTENSIONS / slug / "manifest.json").exists()),
        "local_path": str(EXTENSIONS / slug),
        "local_version": local_version,
        "remote_version": remote_version,
        "expected_extension_id": expected_id,
        "update_available": bool(
            local_version and remote_version and version_gt(remote_version, local_version)
        ),
        "config_backup": bool(config_backup_exists)
    }
