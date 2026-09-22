import secrets
import urllib.parse

from .tokens import save_tokens, load_tokens, clear_tokens, expires_soon
from .loopback import pkce_pair
from . import github_accounts
from ..config import provider_config, provider_secret
from ..paths import AUTH
from ..jsonstore import load_json, save_json
from ..http import form_post, api_json
from ..timeutil import now_ts

AUTH_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"
SESSION_FILE = AUTH / "github-pkce.json"

def _config():
    return provider_config("github")

def _client_secret():
    return provider_secret("github")

def _validate_redirect_uri(redirect_uri):
    parsed = urllib.parse.urlparse(redirect_uri)
    host = (parsed.hostname or "").lower()

    if parsed.scheme != "https" or not host.endswith(".chromiumapp.org"):
        raise RuntimeError("Redirect URI do GitHub não pertence ao chrome.identity.")

    if not parsed.path.rstrip("/").endswith("/github"):
        raise RuntimeError("Redirect URI do GitHub possui caminho inesperado.")

def _profile_from_token(token):
    user = api_json(
        "https://api.github.com/user",
        token,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "ExtNest/0.3"
        }
    )

    if not user or user.get("id") is None:
        raise RuntimeError("GitHub não retornou a identidade da conta.")

    return {
        "account_id": str(user["id"]),
        "login": user.get("login"),
        "name": user.get("name"),
        "avatar_url": user.get("avatar_url")
    }

def list_accounts():
    return github_accounts.list_accounts()

def default_account_id():
    accounts = list_accounts()
    return accounts[0]["account_id"] if len(accounts) == 1 else None

def prepare(redirect_uri):
    _validate_redirect_uri(redirect_uri)

    config = _config()
    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(32)

    save_json(SESSION_FILE, {
        "state": state,
        "verifier": verifier,
        "redirect_uri": redirect_uri,
        "expires_at": now_ts() + 300
    })

    query = urllib.parse.urlencode({
        "client_id": config["client_id"],
        "redirect_uri": redirect_uri,
        "scope": " ".join(config.get("scopes") or ["repo", "read:user", "offline_access"]),
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "prompt": "select_account"
    })

    return {
        "authorization_url": f"{AUTH_URL}?{query}",
        "expires_in": 300
    }

def complete(callback_url):
    session = load_json(SESSION_FILE, None)
    if not session:
        raise RuntimeError("Sessão OAuth GitHub não encontrada. Tente conectar novamente.")

    if int(session.get("expires_at", 0)) <= now_ts():
        SESSION_FILE.unlink(missing_ok=True)
        raise RuntimeError("A autorização do GitHub expirou. Tente novamente.")

    expected = urllib.parse.urlparse(session["redirect_uri"])
    callback = urllib.parse.urlparse(callback_url)

    if (
        callback.scheme != expected.scheme
        or callback.netloc != expected.netloc
        or callback.path.rstrip("/") != expected.path.rstrip("/")
    ):
        raise RuntimeError("Redirect OAuth GitHub inválido.")

    query = urllib.parse.parse_qs(callback.query)
    state = (query.get("state") or [None])[0]
    code = (query.get("code") or [None])[0]
    error = (query.get("error") or [None])[0]
    error_description = (query.get("error_description") or [None])[0]
    issuer = (query.get("iss") or [None])[0]

    if state != session["state"]:
        raise RuntimeError("Estado OAuth GitHub inválido.")

    if issuer and issuer != "https://github.com/login/oauth":
        raise RuntimeError("Issuer OAuth GitHub inválido.")

    if error:
        raise RuntimeError(error_description or error)

    if not code:
        raise RuntimeError("GitHub não retornou authorization code.")

    config = _config()
    response = form_post(
        TOKEN_URL,
        {
            "client_id": config["client_id"],
            "client_secret": _client_secret(),
            "code": code,
            "redirect_uri": session["redirect_uri"],
            "code_verifier": session["verifier"]
        },
        headers={"Accept": "application/json"}
    )

    if response.get("error"):
        raise RuntimeError(response.get("error_description") or response["error"])

    profile = _profile_from_token(response["access_token"])
    save_tokens("github", response, profile["account_id"])
    account = github_accounts.upsert(profile)
    SESSION_FILE.unlink(missing_ok=True)
    return account

def _refresh(account_id, tokens):
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

    return save_tokens("github", response, account_id)

def access_token(account_id):
    if not account_id:
        raise RuntimeError("Conta GitHub não informada.")

    account_id = str(account_id)
    tokens = load_tokens("github", account_id)
    if not tokens:
        raise RuntimeError("Essa conta GitHub não está conectada.")

    if expires_soon(tokens):
        if not tokens.get("refresh_token"):
            raise RuntimeError("Sessão GitHub expirada. Conecte a conta novamente.")
        tokens = _refresh(account_id, tokens)

    return tokens["access_token"]

def refresh_profile(account_id):
    token = access_token(account_id)
    profile = _profile_from_token(token)
    return github_accounts.upsert(profile)

def disconnect(account_id):
    if not account_id:
        raise RuntimeError("Conta GitHub não informada.")

    account_id = str(account_id)
    clear_tokens("github", account_id)
    github_accounts.remove(account_id)

def disconnect_all():
    for account in list_accounts():
        clear_tokens("github", account["account_id"])
    for account in list_accounts():
        github_accounts.remove(account["account_id"])
    SESSION_FILE.unlink(missing_ok=True)
