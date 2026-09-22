import json
from .onedrive import OneDriveProvider
from .google_drive import GoogleDriveProvider
from ..settings import get_settings, update_settings
from ..registry import get_registry, replace_from_cloud
from ..timeutil import now_iso

PROVIDERS = {
    "microsoft": OneDriveProvider,
    "google": GoogleDriveProvider
}

def primary_name():
    return get_settings().get("primary_cloud") or ""

def provider(name=None):
    name = name if name is not None else primary_name()
    if not name:
        return None
    cls = PROVIDERS.get(name)
    if not cls:
        raise RuntimeError("Provedor de nuvem desconhecido.")
    return cls()

def set_primary(name):
    if name and name not in PROVIDERS:
        raise RuntimeError("Provedor inválido.")
    return update_settings({"primary_cloud": name})

def put_json(path, value, provider_name=None):
    target = provider(provider_name)
    if not target:
        return False
    target.put_text(path, json.dumps(value, ensure_ascii=False, indent=2))
    return True

def get_json(path, provider_name=None):
    target = provider(provider_name)
    if not target:
        return None
    text = target.get_text(path)
    return json.loads(text) if text else None

def sync_vault():
    target = provider()
    if not target:
        raise RuntimeError("Nenhum provedor principal configurado.")

    settings = get_settings().copy()
    settings.pop("primary_cloud", None)

    put_json("vault/settings.json", {
        "schema": 1,
        "saved_at": now_iso(),
        "settings": settings
    })
    put_json("vault/extensions.json", get_registry())
    return True

def pull_registry():
    data = get_json("vault/extensions.json")
    if not data:
        return None
    return replace_from_cloud(data)


def bootstrap():
    """On a fresh machine, restore Vault registry/settings if cloud already has them.
    On a configured machine, publish the current local state."""
    from ..registry import get_registry
    from ..settings import get_settings, update_settings

    remote_registry = get_json("vault/extensions.json")
    remote_settings = get_json("vault/settings.json")
    local_registry = get_registry()

    pulled = False
    if remote_registry and not local_registry.get("extensions"):
        replace_from_cloud(remote_registry)
        pulled = True

    if remote_settings and pulled:
        incoming = remote_settings.get("settings") or {}
        allowed = {
            k: incoming[k] for k in (
                "auto_check", "check_interval", "auto_config_backup", "ask_restore"
            ) if k in incoming
        }
        if allowed:
            update_settings(allowed)

    sync_vault()
    return {"pulled": pulled}
