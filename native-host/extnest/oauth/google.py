import urllib.parse, secrets
from .tokens import save_tokens, load_tokens, clear_tokens, expires_soon
from .loopback import LoopbackReceiver, pkce_pair
from ..config import provider_config
from ..http import form_post, api_json
from . import profiles

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

def _config():
    return provider_config("google")

def login():
    config = _config()
    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(24)

    with LoopbackReceiver(public_host="127.0.0.1") as receiver:
        redirect_uri = receiver.redirect_uri
        query = urllib.parse.urlencode({
            "client_id": config["client_id"],
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(config["scopes"]),
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        })
        result = receiver.open_and_wait(f"{AUTH_URL}?{query}")

    if result.get("state") != state:
        raise RuntimeError("Estado OAuth Google inválido.")
    if result.get("error"):
        raise RuntimeError(result.get("error_description") or result["error"])

    tokens = form_post(
        TOKEN_URL,
        {
            "client_id": config["client_id"],
            "code": result["code"],
            "code_verifier": verifier,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
    )
    save_tokens("google", tokens)
    return profiles.set("google", profile())

def _refresh(tokens):
    config = _config()
    response = form_post(
        TOKEN_URL,
        {
            "client_id": config["client_id"],
            "refresh_token": tokens["refresh_token"],
            "grant_type": "refresh_token"
        }
    )
    response["refresh_token"] = tokens["refresh_token"]
    return save_tokens("google", response)

def access_token():
    tokens = load_tokens("google")
    if not tokens:
        raise RuntimeError("Google Drive não conectado.")
    if expires_soon(tokens):
        if not tokens.get("refresh_token"):
            raise RuntimeError("Sessão Google expirada. Conecte novamente.")
        tokens = _refresh(tokens)
    return tokens["access_token"]

def profile():
    user = api_json("https://openidconnect.googleapis.com/v1/userinfo", access_token())
    return {
        "name": user.get("name"),
        "email": user.get("email"),
        "picture": user.get("picture")
    }

def connected_profile():
    if not load_tokens("google"):
        return None
    try:
        return profiles.set("google", profile())
    except Exception:
        return profiles.get("google")

def disconnect():
    clear_tokens("google")
    profiles.clear("google")
