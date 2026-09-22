from datetime import datetime, timezone
import time

def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def now_ts():
    return int(time.time())
