from .paths import DATA
from .jsonstore import load_json, save_json
from .timeutil import now_iso

REGISTRY_FILE = DATA / "registry.json"

def get_registry():
    data = load_json(REGISTRY_FILE, None)
    if not data:
        data = {"schema":1, "extensions":[]}
    return data

def save_registry(data):
    save_json(REGISTRY_FILE, data)
    return data

def list_extensions():
    return get_registry()["extensions"]

def find_by_slug(slug):
    return next((x for x in list_extensions() if x.get("slug") == slug), None)

def find_by_extension_id(extension_id):
    return next((
        x for x in list_extensions()
        if extension_id in {x.get("extension_id"), x.get("expected_extension_id")}
    ), None)

def upsert_repo(item):
    data = get_registry()
    existing = next((x for x in data["extensions"] if x.get("repo","").lower() == item["repo"].lower()), None)
    if existing:
        existing.update(item)
        result = existing
    else:
        result = {
            "added_at": now_iso(),
            "extension_id": None,
            **item
        }
        data["extensions"].append(result)
    save_registry(data)
    return result

def link_extension(slug, extension_id):
    data = get_registry()
    for item in data["extensions"]:
        if item.get("slug") == slug:
            item["extension_id"] = extension_id
            save_registry(data)
            return item
    return None

def replace_from_cloud(cloud_registry):
    if not cloud_registry or not isinstance(cloud_registry.get("extensions"), list):
        raise RuntimeError("extensions.json da nuvem é inválido.")
    save_registry(cloud_registry)
    return cloud_registry
