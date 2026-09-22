from .paths import LOCAL_CONFIG_BACKUPS
from .jsonstore import load_json, save_json
from .timeutil import now_iso
from .registry import find_by_slug
from .cloud import manager as cloud

def _local_path(slug):
    return LOCAL_CONFIG_BACKUPS / f"{slug}.json"

def backup(slug, extension_id, extension_version, reason, payload):
    wrapper = {
        "schema": 1,
        "slug": slug,
        "extension_id": extension_id,
        "extension_version": extension_version,
        "saved_at": now_iso(),
        "reason": reason,
        "payload": payload
    }
    save_json(_local_path(slug), wrapper)

    if cloud.primary_name():
        cloud.put_json(f"extensions/{slug}/config.json", wrapper)
        item = find_by_slug(slug) or {}
        cloud.put_json(f"extensions/{slug}/metadata.json", {
            "schema": 1,
            "slug": slug,
            "repo": item.get("repo"),
            "saved_at": wrapper["saved_at"]
        })
    return wrapper

def restore(slug):
    if cloud.primary_name():
        remote = cloud.get_json(f"extensions/{slug}/config.json")
        if remote:
            save_json(_local_path(slug), remote)
            return remote
    return load_json(_local_path(slug), None)

def exists(slug):
    if cloud.primary_name():
        try:
            return cloud.get_json(f"extensions/{slug}/config.json") is not None
        except Exception:
            pass
    return _local_path(slug).exists()
