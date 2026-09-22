import json, urllib.parse, uuid
from .base import CloudProvider
from ..oauth import google
from ..http import api_json, api_bytes, request

API = "https://www.googleapis.com/drive/v3"
UPLOAD = "https://www.googleapis.com/upload/drive/v3"

def _remote_name(logical_path):
    # appDataFolder is hidden, so physical nesting is unnecessary.
    # Keep a deterministic readable name.
    return "extnest__" + logical_path.replace("/", "__")

def _escape_q(value):
    return value.replace("\\", "\\\\").replace("'", "\\'")

class GoogleDriveProvider(CloudProvider):
    name = "google"

    def _token(self):
        return google.access_token()

    def _find(self, logical_path):
        name = _remote_name(logical_path)
        q = urllib.parse.quote(
            f"name = '{_escape_q(name)}' and 'appDataFolder' in parents and trashed = false",
            safe=""
        )
        data = api_json(
            f"{API}/files?spaces=appDataFolder&q={q}&fields=files(id,name,modifiedTime)&pageSize=10",
            self._token()
        )
        files = (data or {}).get("files", [])
        return files[0] if files else None

    def put_text(self, logical_path, text):
        token = self._token()
        existing = self._find(logical_path)
        name = _remote_name(logical_path)

        boundary = "extnest-" + uuid.uuid4().hex
        metadata = {"name": name}
        if not existing:
            metadata["parents"] = ["appDataFolder"]

        body = (
            f"--{boundary}\r\n"
            "Content-Type: application/json; charset=UTF-8\r\n\r\n"
            + json.dumps(metadata, ensure_ascii=False)
            + f"\r\n--{boundary}\r\n"
            "Content-Type: application/json; charset=UTF-8\r\n\r\n"
            + text
            + f"\r\n--{boundary}--\r\n"
        ).encode("utf-8")

        if existing:
            url = f"{UPLOAD}/files/{existing['id']}?uploadType=multipart"
            method = "PATCH"
        else:
            url = f"{UPLOAD}/files?uploadType=multipart"
            method = "POST"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/related; boundary={boundary}"
        }
        with request(url, method=method, headers=headers, data=body) as response:
            response.read()
        return True

    def get_text(self, logical_path):
        existing = self._find(logical_path)
        if not existing:
            return None
        raw = api_bytes(f"{API}/files/{existing['id']}?alt=media", self._token())
        return raw.decode("utf-8")
