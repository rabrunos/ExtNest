import json, urllib.parse
from .base import CloudProvider
from ..oauth import microsoft
from ..http import api_json, api_bytes, request

GRAPH = "https://graph.microsoft.com/v1.0"

def _child_by_name(parent_id, name, token):
    data = api_json(f"{GRAPH}/me/drive/items/{parent_id}/children?$select=id,name,folder,file", token)
    for item in (data or {}).get("value", []):
        if item.get("name") == name:
            return item
    return None

class OneDriveProvider(CloudProvider):
    name = "microsoft"

    def _token(self):
        return microsoft.access_token()

    def _approot(self):
        return api_json(f"{GRAPH}/me/drive/special/approot", self._token())

    def _ensure_folder(self, parent_id, name):
        token = self._token()
        existing = _child_by_name(parent_id, name, token)
        if existing:
            if not existing.get("folder"):
                raise RuntimeError(f"'{name}' existe no OneDrive mas não é uma pasta.")
            return existing

        return api_json(
            f"{GRAPH}/me/drive/items/{parent_id}/children",
            token,
            method="POST",
            body={
                "name": name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "fail"
            }
        )

    def _resolve_parent(self, logical_path):
        parts = [p for p in logical_path.split("/") if p]
        filename = parts.pop()
        current = self._approot()
        for folder in parts:
            current = self._ensure_folder(current["id"], folder)
        return current["id"], filename

    def put_text(self, logical_path, text):
        parent_id, filename = self._resolve_parent(logical_path)
        token = self._token()
        encoded = urllib.parse.quote(filename, safe="")
        url = f"{GRAPH}/me/drive/items/{parent_id}:/{encoded}:/content"
        body = text.encode("utf-8")
        api_bytes(url, token, method="PUT", body=body, content_type="application/json; charset=utf-8")
        return True

    def get_text(self, logical_path):
        parts = [p for p in logical_path.split("/") if p]
        filename = parts.pop()
        token = self._token()
        current = self._approot()

        for folder in parts:
            child = _child_by_name(current["id"], folder, token)
            if not child or not child.get("folder"):
                return None
            current = child

        file_item = _child_by_name(current["id"], filename, token)
        if not file_item or not file_item.get("file"):
            return None

        raw = api_bytes(f"{GRAPH}/me/drive/items/{file_item['id']}/content", token)
        return raw.decode("utf-8")
