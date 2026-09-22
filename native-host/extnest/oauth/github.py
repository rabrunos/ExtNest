import secrets
import urllib.parse

from .tokens import save_tokens, load_tokens, clear_tokens, expires_soon
from .loopback import LoopbackReceiver, pkce_pair
from ..config import provider_config, provider_secret
from ..http import form_post, api_json
from . import profiles

AUTH_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"

def _config():
    return provider_config("github")

def _client_secret():
    return provider_secret("github")

def login():
    config = _config()
    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(32)

    with LoopbackReceiver(public_host="127.0.0.1") as receiver:
        redirect_uri = receiver.redirect_uri
        query = urllib.parse.urlencode({
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": " ".join(config.get("scopes") or ["repo", "read:user", "offline_access"]),
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "prompt": "select_account"
        })
        result = receiver.open_and_wait(f"{AUTH_URL}?{query}")

    if result.get("state") != state:
        raise RuntimeError("Estado OAuth GitHub inválido.")
    if result.get("error"):
        raise RuntimeError(result.get("error_description") or result["error"])

    code = result.get("code")
    if not code:
        raise RuntimeError("GitHub não retornou authorization code.")

    response = form_post(
        TOKEN_URL,
        {
            "client_id": config["client_id"],
            "client_secret": _client_secret(),
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": verifier
        },
        headers={"Accept": "application/json"}
    )

    if response.get("error"):
        raise RuntimeError(response.get("error_description") or response["error"])

    save_tokens("github", response)
    return profiles.set("github", profile())

def _refresh(tokens):
    config = _config()
    response = form_post(
        TOKEN_URL,
        {
            "client_id": config["client_id"],
            "client_secret": _client_secret(),
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"]
        },
        headers={"Accept": "application/json"}
    )
    if response.get("error"):
        raise RuntimeError(response.get("error_description") or response["error"])
    if "refresh_token" not in response and tokens.get("refresh_token"):
        response["refresh_token"] = tokens["refresh_token"]
    return save_tokens("github", response)

def access_token():
    tokens = load_tokens("github")
    if not tokens:
        raise RuntimeError("GitHub não conectado.")
    if expires_soon(tokens):
        if not tokens.get("refresh_token"):
            raise RuntimeError("Sessão GitHub expirada. Conecte novamente.")
        tokens = _refresh(tokens)
    return tokens["access_token"]

def profile():
    user = api_json(
        "https://api.github.com/user",
        access_token(),
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
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
