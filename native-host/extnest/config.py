import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "oauth-clients.json"
PRIVATE_CONFIG_FILE = ROOT / "oauth-private.json"

def oauth_config():
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

def private_oauth_config():
    if not PRIVATE_CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(PRIVATE_CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
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
        "Configure native-host/oauth-private.json conforme docs/OAUTH_SETUP.md."
    )
