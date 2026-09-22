import urllib.parse, base64
from .oauth import github as github_oauth
from .http import api_json

API = "https://api.github.com"

def _headers():
    return {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
        "User-Agent": "ExtNest/0.2"
    }

def get(path):
    return api_json(API + path, github_oauth.access_token(), headers=_headers())

def list_installations():
    installations = []
    page = 1

    while True:
        data = get(f"/user/installations?per_page=100&page={page}") or {}
        batch = data.get("installations", [])
        installations.extend(batch)

        if len(batch) < 100 or page >= 10:
            break
        page += 1

    return installations

def installation_status():
    installations = list_installations()

    return {
        "count": len(installations),
        "install_url": github_oauth.install_url(),
        "installations": [
            {
                "id": item.get("id"),
                "account": (item.get("account") or {}).get("login"),
                "account_type": (item.get("account") or {}).get("type"),
                "repository_selection": item.get("repository_selection"),
                "manage_url": item.get("html_url")
            }
            for item in installations
        ]
    }

def _repos_for_installation(installation):
    installation_id = installation["id"]
    repositories = []
    page = 1

    while True:
        data = get(
            f"/user/installations/{installation_id}/repositories"
            f"?per_page=100&page={page}"
        ) or {}
        batch = data.get("repositories", [])
        repositories.extend(batch)

        if len(batch) < 100 or page >= 10:
            break
        page += 1

    account = (installation.get("account") or {}).get("login")

    return [
        {
            "full_name": repo["full_name"],
            "private": bool(repo.get("private")),
            "description": repo.get("description"),
            "default_branch": repo.get("default_branch") or "main",
            "html_url": repo.get("html_url"),
            "installation_id": installation_id,
            "installation_account": account
        }
        for repo in repositories
    ]

def list_repos():
    # A GitHub App user access token can only see the intersection of:
    # 1) repositories selected during installation;
    # 2) permissions granted to the GitHub App;
    # 3) repositories the authenticated user can access.
    repos_by_name = {}

    for installation in list_installations():
        for repo in _repos_for_installation(installation):
            repos_by_name[repo["full_name"].lower()] = repo

    return sorted(
        repos_by_name.values(),
        key=lambda repo: repo["full_name"].lower()
    )

def file_text(repo, path, branch="main"):
    qpath = urllib.parse.quote(path, safe="/")
    qbranch = urllib.parse.quote(branch, safe="")
    obj = get(f"/repos/{repo}/contents/{qpath}?ref={qbranch}")

    if not obj or obj.get("encoding") != "base64":
        raise RuntimeError(f"GitHub não retornou {path} em base64.")

    return base64.b64decode(obj["content"]).decode("utf-8")
