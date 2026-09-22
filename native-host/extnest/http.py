import json, urllib.request, urllib.parse, urllib.error

def _error_message(error):
    try:
        raw = error.read().decode("utf-8", "replace")
        try:
            obj = json.loads(raw)
            return obj.get("error_description") or obj.get("message") or obj.get("error", {}).get("message") or raw
        except Exception:
            return raw
    except Exception:
        return str(error)

def request(url, method="GET", headers=None, data=None, timeout=30):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"HTTP {error.code}: {_error_message(error)}") from error

def json_request(url, method="GET", headers=None, data=None, timeout=30):
    with request(url, method, headers, data, timeout) as response:
        raw = response.read()
        return json.loads(raw.decode("utf-8")) if raw else None

def form_post(url, fields, headers=None, timeout=30):
    final_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        **(headers or {})
    }
    body = urllib.parse.urlencode(fields).encode("utf-8")
    return json_request(url, "POST", final_headers, body, timeout)

def api_json(url, token, method="GET", body=None, headers=None, timeout=30):
    final_headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        **(headers or {})
    }
    data = None
    if body is not None:
        final_headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    return json_request(url, method, final_headers, data, timeout)

def api_bytes(url, token, method="GET", body=None, content_type=None, headers=None, timeout=30):
    final_headers = {
        "Authorization": f"Bearer {token}",
        **(headers or {})
    }
    if content_type:
        final_headers["Content-Type"] = content_type
    with request(url, method, final_headers, body, timeout) as response:
        return response.read()
