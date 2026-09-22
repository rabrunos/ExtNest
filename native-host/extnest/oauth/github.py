import json, urllib.parse, urllib.request
from pathlib import Path
from .tokens import save_tokens, load_tokens, clear_tokens, expires_soon
from ..config import provider_config
from ..paths import AUTH
from ..jsonstore import load_json, save_json
from ..http import form_post, api_json
from ..timeutil import now_ts
from . import profiles

SESSION_FILE = AUTH / "github-device.json"

def _config():
    return provider_config("github")

def begin():
    config = _config()
    response = form_post(
        "https://github.com/login/device/code",
        {
            "client_id": config["client_id"],
            "scope": " ".join(config.get("scopes") or ["repo", "read:user", "offline_access"])
        },
        headers={"Accept": "application/json"}
    )
    save_json(SESSION_FILE, {
        "device_code": response["device_code"],
        "expires_at": now_ts() + int(response.get("expires_in", 900)),
        "interval": int(response.get("interval", 5))
    })
    return {
        "user_code": response["user_code"],
        "verification_uri": response["verification_uri"],
        "expires_in": response.get("expires_in", 900),
        "interval": response.get("interval", 5)
    }

def poll():
    config = _config()
    session = load_json(SESSION_FILE, None)
    if not session:
        raise RuntimeError("Nenhuma autenticação GitHub em andamento.")
    if int(session["expires_at"]) <= now_ts():
        SESSION_FILE.unlink(missing_ok=True)
        return {"connected": False, "status": "expired_token"}

    response = form_post(
        "https://github.com/login/oauth/access_token",
        {
            "client_id": config["client_id"],
            "device_code": session["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        },
        headers={"Accept": "application/json"}
    )

    if response.get("error"):
        return {"connected": False, "status": response["error"]}

    save_tokens("github", response)
    SESSION_FILE.unlink(missing_ok=True)
    current = profiles.set("github", profile())
    return {"connected": True, "profile": current}

def _refresh(tokens):
    config = _config()
    response = form_post(
        "https://github.com/login/oauth/access_token",
        {
            "client_id": config["client_id"],
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"]
        },
        headers={"Accept": "application/json"}
    )
    if response.get("error"):
        raise RuntimeError(response.get("error_description") or response["error"])
    return save_tokens("github", response)

def access_token():
    tokens = load_tokens("github")
    if not tokens:
        raise RuntimeError("GitHub não conectado.")
    if expires_soon(tokens) and tokens.get("refresh_token"):
        tokens = _refresh(tokens)
    return tokens["access_token"]

def profile():
    token = access_token()
    user = api_json(
        "https://api.github.com/user",
        token,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ExtNest/0.2"
        }
    )
    return {
        "login": user.get("login"),
        "name": user.get("name"),
        "avatar_url": user.get("avatar_url")
    }

def connected_profile():
    if not load_tokens("github"):
        return None
    try:
        return profiles.set("github", profile())
    except Exception:
        return profiles.get("github")

def disconnect():
    clear_tokens("github")
    profiles.clear("github")
    SESSION_FILE.unlink(missing_ok=True)
