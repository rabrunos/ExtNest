import json
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parent.parent / "oauth-clients.json"

def oauth_config():
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

def provider_config(name):
    config = oauth_config().get(name) or {}
    client_id = config.get("client_id", "")
    if not client_id or client_id.startswith("SET_"):
        raise RuntimeError(
            f"OAuth de {name} ainda não foi configurado. "
            "Preencha native-host/oauth-clients.json conforme docs/OAUTH_SETUP.md."
        )
    return config
