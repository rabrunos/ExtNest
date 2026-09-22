import base64
import json
import urllib.parse

from .oauth import github as github_oauth
from .http import api_json, api_bytes, json_request, request

API = "https://api.github.com"
EXTNEST_MARKER = ".extnest.json"

def _headers():
    return {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
        "User-Agent": "ExtNest/0.5"
    }

def _public_get(path):
    return json_request(API + path, headers=_headers())

def _account_get(path, account_id):
    return api_json(
        API + path,
        github_oauth.access_token(account_id),
        headers=_headers()
    )

def get(path, account_id=None):
    if account_id:
        return _account_get(path, account_id)
    return _public_get(path)

def repo_info(repo, account_id=None):
    qrepo = "/".join(urllib.parse.quote(part, safe="") for part in repo.split("/", 1))
    obj = get(f"/repos/{qrepo}", account_id)
    return {
        "full_name": obj["full_name"],
        "private": bool(obj.get("private")),
        "description": obj.get("description"),
        "default_branch": obj.get("default_branch") or "main",
        "html_url": obj.get("html_url")
    }

def _validate_extnest_metadata(data):
    if not isinstance(data, dict):
        return None
    if int(data.get("schema") or 0) != 1:
        return None
    if data.get("type") != "extension":
        return None
    if (data.get("entry") or ".") != ".":
        return None
    return {
        "schema": 1,
        "type": "extension",
        "displayName": data.get("displayName"),
        "entry": ".",
        "configBridge": bool(data.get("configBridge"))
    }

def extnest_metadata(repo, branch="main", account_id=None):
    try:
        raw = file_text(repo, EXTNEST_MARKER, branch, account_id)
        return _validate_extnest_metadata(json.loads(raw))
    except Exception:
        return None

def list_repos(account_id):
    if not account_id:
        raise RuntimeError("Selecione uma conta GitHub.")

    repos = []
    page = 1

    while True:
        batch = _account_get(
            f"/user/repos?per_page=100&page={page}"
            "&affiliation=owner,collaborator,organization_member"
            "&sort=updated",
            account_id
        ) or []

        for repo in batch:
            branch = repo.get("default_branch") or "main"
            metadata = extnest_metadata(repo["full_name"], branch, account_id)
            if not metadata:
                continue
            repos.append({
                "full_name": repo["full_name"],
                "private": bool(repo.get("private")),
                "description": repo.get("description"),
                "default_branch": branch,
                "html_url": repo.get("html_url"),
                "extnest": metadata
            })

        if len(batch) < 100 or page >= 10:
            break
        page += 1

    return repos

def file_text(repo, path, branch="main", account_id=None):
    qpath = urllib.parse.quote(path, safe="/")
    qbranch = urllib.parse.quote(branch, safe="")

    if account_id:
        obj = _account_get(
            f"/repos/{repo}/contents/{qpath}?ref={qbranch}",
            account_id
        )
    else:
        obj = _public_get(f"/repos/{repo}/contents/{qpath}?ref={qbranch}")

    if not obj or obj.get("encoding") != "base64":
        raise RuntimeError(f"GitHub não retornou {path} em base64.")

    return base64.b64decode(obj["content"]).decode("utf-8")

def archive_bytes(repo, ref="main", account_id=None):
    qrepo = "/".join(urllib.parse.quote(part, safe="") for part in repo.split("/", 1))
    qref = urllib.parse.quote(ref, safe="")
    url = f"{API}/repos/{qrepo}/zipball/{qref}"
    headers = _headers()

    if account_id:
        return api_bytes(
            url,
            github_oauth.access_token(account_id),
            headers=headers,
            timeout=120
        )

    with request(url, headers=headers, timeout=120) as response:
        return response.read()
