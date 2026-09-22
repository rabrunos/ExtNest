from ..paths import AUTH
from ..jsonstore import load_json, save_json
from ..timeutil import now_iso

FILE = AUTH / "github-accounts.json"

def _data():
    data = load_json(FILE, None)
    if not isinstance(data, dict):
        data = None

    if not data or not isinstance(data.get("accounts"), list):
        data = {"schema": 1, "accounts": []}

    return data

def list_accounts():
    return _data()["accounts"]

def find(account_id):
    account_id = str(account_id)
    return next(
        (item for item in list_accounts() if str(item.get("account_id")) == account_id),
        None
    )

def upsert(profile):
    account_id = str(profile["account_id"])
    data = _data()

    existing = next(
        (item for item in data["accounts"] if str(item.get("account_id")) == account_id),
        None
    )

    public = {
        "account_id": account_id,
        "login": profile.get("login"),
        "name": profile.get("name"),
        "avatar_url": profile.get("avatar_url"),
        "updated_at": now_iso()
    }

    if existing:
        existing.update(public)
        result = existing
    else:
        data["accounts"].append(public)
        result = public

    save_json(FILE, data)
    return result

def remove(account_id):
    account_id = str(account_id)
    data = _data()
    before = len(data["accounts"])
    data["accounts"] = [
        item for item in data["accounts"]
        if str(item.get("account_id")) != account_id
    ]

    if len(data["accounts"]) != before:
        save_json(FILE, data)
        return True

    return False
