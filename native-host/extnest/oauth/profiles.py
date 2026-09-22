from ..paths import AUTH
from ..jsonstore import load_json, save_json

FILE = AUTH / "profiles.json"

def get(provider):
    return (load_json(FILE, {}) or {}).get(provider)

def set(provider, profile):
    data = load_json(FILE, {}) or {}
    data[provider] = profile
    save_json(FILE, data)
    return profile

def clear(provider):
    data = load_json(FILE, {}) or {}
    data.pop(provider, None)
    save_json(FILE, data)
