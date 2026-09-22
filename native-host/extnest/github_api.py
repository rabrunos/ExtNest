import urllib.parse, base64
from .oauth import github as github_oauth
from .http import api_json

API = "https://api.github.com"

def _headers():
    return {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ExtNest/0.2"
    }

def get(path):
    return api_json(API + path, github_oauth.access_token(), headers=_headers())

def list_repos():
    repos = []
    page = 1
    while True:
        batch = get(
            f"/user/repos?per_page=100&page={page}"
            "&affiliation=owner,collaborator,organization_member&sort=updated"
        ) or []
        for repo in batch:
            repos.append({
                "full_name": repo["full_name"],
                "private": bool(repo.get("private")),
                "description": repo.get("description"),
                "default_branch": repo.get("default_branch") or "main",
                "html_url": repo.get("html_url")
            })
        if len(batch) < 100 or page >= 10:
            break
        page += 1
    return repos

def file_text(repo, path, branch="main"):
    qpath = urllib.parse.quote(path, safe="/")
    qbranch = urllib.parse.quote(branch, safe="")
    obj = get(f"/repos/{repo}/contents/{qpath}?ref={qbranch}")
    if not obj or obj.get("encoding") != "base64":
        raise RuntimeError(f"GitHub não retornou {path} em base64.")
    return base64.b64decode(obj["content"]).decode("utf-8")
