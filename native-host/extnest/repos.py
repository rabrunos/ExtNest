import os, re, json, shutil, subprocess, hashlib, base64
from .paths import EXTENSIONS
from .registry import find_by_slug, upsert_repo, get_registry, save_registry
from .github_api import file_text
from .oauth import github as github_oauth

def sanitize_slug(repo):
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", repo.split("/")[-1]).strip("-").lower()

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
        return json.loads(file_text(item["repo"], "manifest.json", item.get("branch") or "main"))
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

def register_repo(repo, branch="main"):
    manifest = json.loads(file_text(repo, "manifest.json", branch))
    if int(manifest.get("manifest_version", 0)) < 3:
        raise RuntimeError("manifest.json não é Manifest V3.")

    item = {
        "slug": sanitize_slug(repo),
        "repo": repo,
        "branch": branch,
        "name": manifest.get("name") or sanitize_slug(repo),
        "expected_extension_id": expected_extension_id_from_key(manifest.get("key",""))
    }
    return upsert_repo(item)

def _git_exe():
    exe = shutil.which("git")
    if not exe:
        raise RuntimeError("Git não encontrado no PATH. Instale Git for Windows.")
    return exe

def _auth_header():
    token = github_oauth.access_token()
    raw = base64.b64encode(f"x-access-token:{token}".encode("utf-8")).decode("ascii")
    return f"Authorization: Basic {raw}"

def run_git(args, cwd=None, check=True):
    cmd = [_git_exe(), "-c", f"http.extraHeader={_auth_header()}", *args]
    proc = subprocess.run(
        cmd, cwd=str(cwd) if cwd else None,
        text=True, capture_output=True, encoding="utf-8", errors="replace"
    )
    if check and proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "Erro Git").strip())
    return proc

def install(slug):
    item = find_by_slug(slug)
    if not item:
        raise RuntimeError("Extensão não registrada.")

    target = EXTENSIONS / slug
    if target.exists():
        if (target / ".git").exists():
            return target
        shutil.rmtree(target)

    run_git([
        "clone",
        "--branch", item.get("branch") or "main",
        "--single-branch",
        f"https://github.com/{item['repo']}.git",
        str(target)
    ])
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
        raise RuntimeError("Há alterações locais. Envie ou reverta antes de atualizar.")

    run_git(["pull", "--ff-only", "origin", item.get("branch") or "main"], cwd=target)
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
        "local_exists": bool((EXTENSIONS / slug / "manifest.json").exists()),
        "local_path": str(EXTENSIONS / slug),
        "local_version": local_version,
        "remote_version": remote_version,
        "expected_extension_id": expected_id,
        "update_available": bool(local_version and remote_version and version_gt(remote_version, local_version)),
        "config_backup": bool(config_backup_exists)
    }
