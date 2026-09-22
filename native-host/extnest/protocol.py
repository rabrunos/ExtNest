from .paths import EXTENSIONS, DATA
from .settings import get_settings, update_settings
from .registry import list_extensions, find_by_extension_id, link_extension
from . import repos
from . import github_api
from . import config_backup
from .oauth import github, microsoft, google
from .cloud import manager as cloud

HOST_VERSION = "0.2.6"
PROTOCOL_VERSION = 2

def _auth_state():
    return {
        "github": github.connected_profile(),
        "microsoft": microsoft.connected_profile(),
        "google": google.connected_profile()
    }

def dispatch(request):
    op = request.get("op")

    if op == "ping":
        return {"ok": True, "name": "ExtNest Native Host", "version": HOST_VERSION, "protocol_version": PROTOCOL_VERSION}

    if op == "state_get":
        settings = get_settings()
        return {
            "ok": True,
            "host": {"version": HOST_VERSION, "protocol_version": PROTOCOL_VERSION},
            "registry": list_extensions(),
            "auth": _auth_state(),
            "cloud": {"primary": settings.get("primary_cloud") or ""},
            "settings": settings,
            "paths": {"extensions": str(EXTENSIONS), "data": str(DATA)}
        }

    if op == "oauth_github_prepare":
        return {"ok": True, **github.prepare(request["redirect_uri"])}

    if op == "oauth_github_complete":
        return {"ok": True, "profile": github.complete(request["callback_url"])}

    if op == "oauth_interactive_login":
        provider = request.get("provider")
        if provider == "microsoft":
            profile = microsoft.login()
        elif provider == "google":
            profile = google.login()
        else:
            raise RuntimeError("Provedor OAuth interativo inválido.")
        return {"ok": True, "profile": profile}

    if op == "oauth_disconnect":
        provider = request.get("provider")
        handlers = {"github": github.disconnect, "microsoft": microsoft.disconnect, "google": google.disconnect}
        if provider not in handlers:
            raise RuntimeError("Provedor inválido.")
        handlers[provider]()
        return {"ok": True}

    if op == "github_list_repos":
        return {"ok": True, "repos": github_api.list_repos()}

    if op == "repo_register":
        item = repos.register_repo(request["repo"], request.get("branch") or "main")
        if cloud.primary_name():
            try: cloud.sync_vault()
            except Exception: pass
        return {"ok": True, "item": item}

    if op == "repo_install":
        path = repos.install(request["slug"])
        return {"ok": True, "path": str(path), **repos.status(request["slug"], config_backup.exists(request["slug"]))}

    if op == "repo_update":
        repos.update(request["slug"])
        return {"ok": True, **repos.status(request["slug"], config_backup.exists(request["slug"]))}

    if op == "repo_status":
        return {"ok": True, **repos.status(request["slug"], config_backup.exists(request["slug"]))}

    if op == "repo_check_all":
        items = []
        for item in list_extensions():
            status = repos.status(item["slug"], config_backup.exists(item["slug"]))
            status["installed"] = status["local_exists"]
            items.append(status)
        return {"ok": True, "items": items}

    if op == "repo_open":
        repos.open_folder(request["slug"])
        return {"ok": True}

    if op == "registry_find_extension":
        return {"ok": True, "item": find_by_extension_id(request["extension_id"])}

    if op == "registry_link_extension":
        item = link_extension(request["slug"], request["extension_id"])
        if cloud.primary_name():
            try: cloud.sync_vault()
            except Exception: pass
        return {"ok": True, "item": item}

    if op == "cloud_set_primary":
        provider = request.get("provider") or ""
        cloud.set_primary(provider)
        result = {"pulled": False}
        if provider:
            result = cloud.bootstrap()
        return {"ok": True, "cloud": {"primary": provider}, **result}

    if op == "cloud_sync_vault":
        cloud.sync_vault()
        return {"ok": True}

    if op == "cloud_pull_registry":
        return {"ok": True, "registry": cloud.pull_registry()}

    if op == "settings_set":
        settings = update_settings(request.get("settings") or {})
        if cloud.primary_name():
            try: cloud.sync_vault()
            except Exception: pass
        return {"ok": True, "settings": settings}

    if op == "config_backup":
        wrapper = config_backup.backup(
            request["slug"], request.get("extension_id"), request.get("extension_version"),
            request.get("reason") or "manual", request.get("payload")
        )
        return {"ok": True, "saved_at": wrapper["saved_at"]}

    if op == "config_restore":
        backup = config_backup.restore(request["slug"])
        if not backup:
            return {"ok": False, "error": "Backup de configurações não encontrado."}
        return {"ok": True, "payload": backup.get("payload"), "saved_at": backup.get("saved_at")}

    raise RuntimeError(f"Operação desconhecida: {op}")
