import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "oauth-clients.json"

LOCAL_APP_DATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
STABLE_DEV_ROOT = LOCAL_APP_DATA / "ExtNest" / "NativeHostDev"

PRIVATE_CONFIG_CANDIDATES = [
    STABLE_DEV_ROOT / "oauth-private.json",
    ROOT / "oauth-private.json",
]

def oauth_config():
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

def private_oauth_config():
    for path in PRIVATE_CONFIG_CANDIDATES:
        if not path.exists():
            continue
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}

def provider_config(name):
    config = oauth_config().get(name) or {}
    client_id = config.get("client_id", "")
    if not client_id or client_id.startswith("SET_"):
        raise RuntimeError(
            f"OAuth de {name} ainda não foi configurado. "
            "Preencha native-host/oauth-clients.json conforme docs/OAUTH_SETUP.md."
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
        f"Credencial privada de {name} ausente ({key}). "
        "Execute native-host/setup/set-dev-github-secret.ps1."
    )
