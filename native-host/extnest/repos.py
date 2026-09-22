import base64
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.parse
import zipfile
from pathlib import Path, PurePosixPath

from .paths import EXTENSIONS, CACHE
from .registry import find_by_slug, upsert_repo, get_registry, save_registry
from .github_api import file_text, repo_info, archive_bytes, extnest_metadata

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

    effective_account_id = str(account_id) if info["private"] and account_id else None

    if info["private"] and not effective_account_id:
        raise RuntimeError("Repositório privado exige uma conta GitHub conectada.")

    effective_branch = branch or info["default_branch"] or "main"

    metadata = extnest_metadata(repo, effective_branch, effective_account_id)
    if not metadata:
        raise RuntimeError(
            "Esse repositório não é compatível com ExtNest. "
            "Adicione um .extnest.json válido na raiz."
        )

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
        "transport": "archive",
        "extnest": metadata,
        "expected_extension_id": expected_extension_id_from_key(manifest.get("key", ""))
    }
    return upsert_repo(item)

def _safe_extract_zip(blob, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    destination_resolved = destination.resolve()

    try:
        archive = zipfile.ZipFile(io.BytesIO(blob))
    except zipfile.BadZipFile as error:
        raise RuntimeError("O GitHub retornou um arquivo ZIP inválido.") from error

    with archive:
        files = [
            info for info in archive.infolist()
            if info.filename and not info.is_dir()
        ]

        if not files:
            raise RuntimeError("O ZIP do repositório está vazio.")

        roots = set()
        parsed = []

        for info in files:
            if "\\" in info.filename:
                raise RuntimeError("O ZIP do repositório contém caminho inválido.")

            parts = PurePosixPath(info.filename).parts
            if len(parts) < 2:
                continue

            roots.add(parts[0])
            parsed.append((info, parts))

        if len(roots) != 1:
            raise RuntimeError("Estrutura inesperada no ZIP retornado pelo GitHub.")

        root = next(iter(roots))

        for info, parts in parsed:
            if parts[0] != root:
                raise RuntimeError("Estrutura inconsistente no ZIP do repositório.")

            relative_parts = parts[1:]
            if not relative_parts:
                continue

            if any(part in {"", ".", ".."} for part in relative_parts):
                raise RuntimeError("O ZIP do repositório contém caminho inseguro.")

            target = destination.joinpath(*relative_parts)
            target_resolved = target.resolve()

            try:
                target_resolved.relative_to(destination_resolved)
            except ValueError as error:
                raise RuntimeError("O ZIP tentou gravar fora da pasta da extensão.") from error

            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info, "r") as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)

def _deploy_archive(item):
    blob = archive_bytes(
        item["repo"],
        item.get("branch") or "main",
        item.get("account_id")
    )

    target = EXTENSIONS / item["slug"]
    backup = EXTENSIONS / f".{item['slug']}.previous"

    with tempfile.TemporaryDirectory(prefix="extnest-", dir=str(CACHE)) as temp_dir:
        stage = Path(temp_dir) / "payload"
        _safe_extract_zip(blob, stage)

        manifest_path = stage / "manifest.json"
        if not manifest_path.exists():
            raise RuntimeError("O repositório não possui manifest.json na raiz.")

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as error:
            raise RuntimeError("manifest.json baixado é inválido.") from error

        if int(manifest.get("manifest_version", 0)) < 3:
            raise RuntimeError("A extensão baixada não é Manifest V3.")

        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)

        had_previous = target.exists()

        if had_previous:
            target.replace(backup)

        try:
            shutil.move(str(stage), str(target))
        except Exception:
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
            if had_previous and backup.exists():
                backup.replace(target)
            raise
        else:
            if backup.exists():
                shutil.rmtree(backup, ignore_errors=True)

    return target

def install(slug):
    item = find_by_slug(slug)
    if not item:
        raise RuntimeError("Extensão não registrada.")

    return _deploy_archive(item)

def update(slug):
    item = find_by_slug(slug)
    if not item:
        raise RuntimeError("Extensão não registrada.")

    target = EXTENSIONS / slug
    if not (target / "manifest.json").exists():
        raise RuntimeError("A extensão ainda não foi instalada.")

    return _deploy_archive(item)

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
        "transport": "archive",
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
