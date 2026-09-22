import os
from pathlib import Path

APP_NAME = "ExtNest"
LOCAL_APP_DATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
ROOT = LOCAL_APP_DATA / APP_NAME
DATA = ROOT / "Data"
EXTENSIONS = ROOT / "Extensions"
SECRETS = DATA / "secrets"
AUTH = DATA / "auth"
CACHE = DATA / "cache"
LOCAL_CONFIG_BACKUPS = DATA / "config-backups"

for path in (ROOT, DATA, EXTENSIONS, SECRETS, AUTH, CACHE, LOCAL_CONFIG_BACKUPS):
    path.mkdir(parents=True, exist_ok=True)
