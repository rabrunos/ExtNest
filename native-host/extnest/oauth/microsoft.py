import urllib.parse, secrets
from .tokens import save_tokens, load_tokens, clear_tokens, expires_soon
from .loopback import LoopbackReceiver, pkce_pair
from ..config import provider_config
from ..http import form_post, api_json
from . import profiles

AUTH_BASE = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0"

def _config():
    return provider_config("microsoft")

def login():
    config = _config()
    tenant = config.get("tenant") or "common"
    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(24)

    with LoopbackReceiver(public_host="localhost") as receiver:
        redirect_uri = receiver.redirect_uri
        query = urllib.parse.urlencode({
            "client_id": config["client_id"],
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": " ".join(config["scopes"]),
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": state,
            "prompt": "select_account"
        })
        result = receiver.open_and_wait(f"{AUTH_BASE.format(tenant=tenant)}/authorize?{query}")

    if result.get("state") != state:
        raise RuntimeError("Estado OAuth Microsoft inválido.")
    if result.get("error"):
        raise RuntimeError(result.get("error_description") or result["error"])

    tokens = form_post(
        f"{AUTH_BASE.format(tenant=tenant)}/token",
        {
            "client_id": config["client_id"],
            "grant_type": "authorization_code",
            "code": result["code"],
            "redirect_uri": redirect_uri,
            "code_verifier": verifier,
            "scope": " ".join(config["scopes"])
        }
    )
    save_tokens("microsoft", tokens)
    return profiles.set("microsoft", profile())

def _refresh(tokens):
    config = _config()
    tenant = config.get("tenant") or "common"
    response = form_post(
        f"{AUTH_BASE.format(tenant=tenant)}/token",
        {
            "client_id": config["client_id"],
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
            "scope": " ".join(config["scopes"])
        }
    )
    if "refresh_token" not in response:
        response["refresh_token"] = tokens["refresh_token"]
    return save_tokens("microsoft", response)

def access_token():
    tokens = load_tokens("microsoft")
    if not tokens:
        raise RuntimeError("OneDrive não conectado.")
    if expires_soon(tokens):
        if not tokens.get("refresh_token"):
            raise RuntimeError("Sessão Microsoft expirada. Conecte novamente.")
        tokens = _refresh(tokens)
    return tokens["access_token"]

def profile():
    user = api_json(
        "https://graph.microsoft.com/v1.0/me?$select=displayName,userPrincipalName,mail",
        access_token()
    )
    return {
        "name": user.get("displayName"),
        "email": user.get("mail") or user.get("userPrincipalName"),
        "user_principal_name": user.get("userPrincipalName")
    }

def connected_profile():
    if not load_tokens("microsoft"):
        return None
    try:
        return profiles.set("microsoft", profile())
    except Exception:
        return profiles.get("microsoft")

def disconnect():
    clear_tokens("microsoft")
    profiles.clear("microsoft")
