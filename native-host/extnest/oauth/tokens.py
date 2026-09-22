import json
from ..secrets import save_secret, load_secret, delete_secret
from ..timeutil import now_ts

def save_tokens(provider, payload):
    data = dict(payload)
    data["obtained_at"] = now_ts()
    if data.get("expires_in"):
        data["expires_at"] = data["obtained_at"] + int(data["expires_in"])
    save_secret(f"oauth-{provider}", json.dumps(data).encode("utf-8"))
    return data

def load_tokens(provider):
    raw = load_secret(f"oauth-{provider}")
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None

def clear_tokens(provider):
    delete_secret(f"oauth-{provider}")

def expires_soon(tokens, seconds=120):
    expires_at = tokens.get("expires_at")
    return bool(expires_at and int(expires_at) <= now_ts() + seconds)
