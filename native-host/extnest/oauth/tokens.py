import json
import re
from ..secrets import save_secret, load_secret, delete_secret
from ..timeutil import now_ts

def _secret_name(provider, account_id=None):
    if account_id is None:
        return f"oauth-{provider}"

    safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(account_id)).strip("-")
    if not safe:
        raise RuntimeError("Identificador de conta OAuth inválido.")
    return f"oauth-{provider}-{safe}"

def save_tokens(provider, payload, account_id=None):
    data = dict(payload)
    data["obtained_at"] = now_ts()
    if data.get("expires_in"):
        data["expires_at"] = data["obtained_at"] + int(data["expires_in"])
    save_secret(_secret_name(provider, account_id), json.dumps(data).encode("utf-8"))
    return data

def load_tokens(provider, account_id=None):
    raw = load_secret(_secret_name(provider, account_id))
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None

def clear_tokens(provider, account_id=None):
    delete_secret(_secret_name(provider, account_id))

def expires_soon(tokens, seconds=120):
    expires_at = tokens.get("expires_at")
    return bool(expires_at and int(expires_at) <= now_ts() + seconds)
