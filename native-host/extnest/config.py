import json
import os
import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_ROOT = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else SOURCE_ROOT
)
BUNDLE_ROOT = Path(getattr(sys, "_MEIPASS", RUNTIME_ROOT))

LOCAL_APP_DATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
STABLE_DEV_ROOT = LOCAL_APP_DATA / "ExtNest" / "NativeHostDev"
STABLE_RELEASE_ROOT = LOCAL_APP_DATA / "ExtNest" / "NativeHost"

CONFIG_CANDIDATES = [
    RUNTIME_ROOT / "oauth-clients.json",
    BUNDLE_ROOT / "oauth-clients.json",
    SOURCE_ROOT / "oauth-clients.json",
]

PRIVATE_CONFIG_CANDIDATES = [
    STABLE_RELEASE_ROOT / "oauth-private.json",
    STABLE_DEV_ROOT / "oauth-private.json",
    RUNTIME_ROOT / "oauth-private.json",
    SOURCE_ROOT / "oauth-private.json",
]

def _load_first_json(paths, default=None):
    for path in paths:
        if not path.exists():
            continue
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
    return default

def oauth_config():
    config = _load_first_json(CONFIG_CANDIDATES, None)
    if not isinstance(config, dict):
        raise RuntimeError("oauth-clients.json não foi encontrado no ExtNest Helper.")
    return config

def private_oauth_config():
    config = _load_first_json(PRIVATE_CONFIG_CANDIDATES, {})
    return config if isinstance(config, dict) else {}

def provider_config(name):
    config = oauth_config().get(name) or {}
    client_id = config.get("client_id", "")
    if not client_id or client_id.startswith("SET_"):
        raise RuntimeError(
            f"OAuth de {name} ainda não foi configurado no ExtNest Helper."
        )
    return config

def provider_secret(name, key="client_secret"):
    env_name = f"EXTNEST_{name.upper()}_{key.upper()}"
    value = os.environ.get(env_name, "").strip()
    if value:
        return value

    private = private_oauth_config().get(name) or {}
    value = str(private.get(key) or "").strip()
    if value and not value.startswith("SET_"):
        return value

    raise RuntimeError(
        f"Credencial interna de {name} ausente ({key}). "
        "Atualize ou reinstale o ExtNest Helper."
    )
