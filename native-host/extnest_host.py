#!/usr/bin/env python3
import json, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from extnest.protocol import dispatch

def read_message():
    raw = sys.stdin.buffer.read(4)
    if not raw:
        return None
    length = struct.unpack("=I", raw)[0]
    payload = sys.stdin.buffer.read(length)
    return json.loads(payload.decode("utf-8"))

def send_message(obj):
    payload = json.dumps(obj, ensure_ascii=False, separators=(",",":")).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("=I", len(payload)))
    sys.stdout.buffer.write(payload)
    sys.stdout.buffer.flush()

def main():
    if os.name == "nt":
        try:
            import msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        except Exception:
            pass

    while True:
        request = read_message()
        if request is None:
            break
        try:
            response = dispatch(request)
        except Exception as error:
            response = {"ok":False, "error":str(error)}
        send_message(response)

if __name__ == "__main__":
    main()
