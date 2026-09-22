import os, ctypes, ctypes.wintypes
from pathlib import Path
from .paths import SECRETS

class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", ctypes.wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte))
    ]

def _blob(data: bytes):
    buf = ctypes.create_string_buffer(data)
    return DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte))), buf

def protect(data: bytes) -> bytes:
    if os.name != "nt":
        return b"DEV0" + data

    source, keepalive = _blob(data)
    target = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(source), None, None, None, None, 0, ctypes.byref(target)
    ):
        raise ctypes.WinError()

    try:
        return ctypes.string_at(target.pbData, target.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(target.pbData)

def unprotect(data: bytes) -> bytes:
    if data.startswith(b"DEV0"):
        return data[4:]
    if os.name != "nt":
        return data

    source, keepalive = _blob(data)
    target = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(source), None, None, None, None, 0, ctypes.byref(target)
    ):
        raise ctypes.WinError()

    try:
        return ctypes.string_at(target.pbData, target.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(target.pbData)

def secret_path(name: str) -> Path:
    return SECRETS / f"{name}.bin"

def save_secret(name: str, data: bytes):
    secret_path(name).write_bytes(protect(data))

def load_secret(name: str):
    path = secret_path(name)
    if not path.exists():
        return None
    try:
        return unprotect(path.read_bytes())
    except Exception:
        return None

def delete_secret(name: str):
    secret_path(name).unlink(missing_ok=True)
