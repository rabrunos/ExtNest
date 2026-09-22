import os
import shutil
import subprocess
from pathlib import Path

LOCAL_APP_DATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
DEV_POINTER = LOCAL_APP_DATA / "ExtNest" / "NativeHostDev" / "repo-path.txt"

def _repo_root():
    candidates = []
    env = os.environ.get("EXTNEST_DEV_REPO", "").strip()
    if env:
        candidates.append(Path(env))
    if DEV_POINTER.exists():
        try:
            raw = DEV_POINTER.read_text(encoding="utf-8").strip()
            if raw:
                candidates.append(Path(raw))
        except Exception:
            pass
    candidates.append(Path("C:/Dev/ExtNest"))

    for candidate in candidates:
        try:
            root = candidate.expanduser().resolve()
        except Exception:
            continue
        if (
            (root / ".git").exists()
            and (root / "extension" / "manifest.json").exists()
            and (root / "native-host").exists()
        ):
            return root

    raise RuntimeError(
        "Checkout DEV do ExtNest não encontrado. "
        "Esperado em C:\\Dev\\ExtNest ou no ponteiro NativeHostDev."
    )

def _git_exe():
    exe = shutil.which("git")
    if exe:
        return exe
    for candidate in (
        Path("C:/Program Files/Git/cmd/git.exe"),
        Path("C:/Program Files/Git/bin/git.exe"),
    ):
        if candidate.exists():
            return str(candidate)
    raise RuntimeError("Git não encontrado neste computador de desenvolvimento.")

def _run(root, *args, check=True):
    proc = subprocess.run(
        [_git_exe(), "-C", str(root), *args],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace"
    )
    if check and proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "Erro Git").strip())
    return proc

def update():
    root = _repo_root()
    branch = _run(root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != "main":
        raise RuntimeError(
            f"O auto-update DEV exige a branch main. Branch atual: {branch or 'desconhecida'}."
        )

    dirty = _run(root, "status", "--porcelain").stdout.strip()
    if dirty:
        raise RuntimeError(
            "Existem alterações locais no ExtNest. "
            "Salve ou descarte essas alterações antes de atualizar."
        )

    before = _run(root, "rev-parse", "HEAD").stdout.strip()
    pull = _run(root, "pull", "--ff-only", "origin", "main")
    after = _run(root, "rev-parse", "HEAD").stdout.strip()

    return {
        "changed": before != after,
        "before": before,
        "after": after,
        "branch": branch,
        "path": str(root),
        "message": (pull.stdout or pull.stderr or "").strip()
    }
