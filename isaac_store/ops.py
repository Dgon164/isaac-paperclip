"""OpsLedger — system/operational management (the sixth area).

The ledger organ, universally applied: every operation may append an
ops event (timing, counts, sizes, verdict tallies) to ops.jsonl.

THE CONTENT-FREE RULE (Identity Law applied to operations): Prime's
ops ledger describes Prime's OWN operation, never user behavior and
never content. Events carry numbers, short enums, and paths without
queries. The ledger REFUSES long strings at write time — a leak
can't happen by sloppiness, only by deliberate circumvention.
"""
import json
import os
import time

MAX_STR = 64  # anything longer is content, not an enum/path


class OpsLedger:
    def __init__(self, path):
        self.path = path

    def event(self, kind, **fields):
        for k, v in fields.items():
            if isinstance(v, str) and len(v) > MAX_STR:
                raise ValueError(
                    f"ops ledger is content-free: field {k!r} is {len(v)} chars")
            if not isinstance(v, (int, float, bool, str, type(None))):
                raise ValueError(
                    f"ops ledger is content-free: field {k!r} is {type(v).__name__}")
        line = json.dumps(dict(ts=time.strftime("%Y-%m-%d %H:%M:%S"),
                               kind=kind, **fields), ensure_ascii=False)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def read(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]
