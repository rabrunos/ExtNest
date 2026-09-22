from .paths import DATA
from .jsonstore import load_json, save_json

SETTINGS_FILE = DATA / "settings.json"

DEFAULTS = {
    "auto_check": True,
    "check_interval": 360,
    "auto_config_backup": True,
    "ask_restore": True,
    "primary_cloud": ""
}

def get_settings():
    data = dict(DEFAULTS)
    data.update(load_json(SETTINGS_FILE, {}) or {})
    return data

def update_settings(values):
    data = get_settings()
    for key in DEFAULTS:
        if key in values:
            data[key] = values[key]
    save_json(SETTINGS_FILE, data)
    return data
