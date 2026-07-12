"""RemoteCache — the Worker read side over the HTTP doorway.

Same contract as LiveCache (get / recheck / job pinning / the fixed
30-minute owner-settled interval), but Prime lives across the wire:
watermark for the cheap recheck, journal?since= for the delta,
record?key= for demand fetches. The server holds current state, so
no overlay is needed — a recheck just drops the touched keys and the
next get refetches truth.

With this, a worker or a whole leaf can run on a DIFFERENT MACHINE
from Prime: same laws (pin per job, staleness cannot corrupt because
admission still judges every proposal server-side).
"""
import json
import time
import urllib.request

from .cache import RECHECK_SECONDS
from .codec import dec


class RemoteCache:
    def __init__(self, base_url, token=None,
                 recheck_seconds=RECHECK_SECONDS, clock=time.monotonic):
        self.base = base_url.rstrip("/")
        self.token = token
        self.recheck_seconds = recheck_seconds
        self.clock = clock
        self._pinned = 0
        self.fetches = 0
        self.rechecks = 0
        self._cache = {}
        self.reader = None  # no file reader: we are remote
        w = self._call("/api/watermark")
        self.watermark = w["last_seq"]
        self.pack_version = w["pack_version"]
        self._last_recheck = self.clock()

    def _call(self, path):
        req = urllib.request.Request(self.base + path)
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                out = json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Prime refused {path}: HTTP {e.code}") from None
        if not out.get("ok", True) and "why" in out and \
                "no such record" not in out.get("why", ""):
            raise RuntimeError(f"Prime refused {path}: {out['why']}")
        return out

    def _maybe_recheck(self):
        if self._pinned:
            return  # pinned job: consistency beats freshness
        if self.clock() - self._last_recheck < self.recheck_seconds:
            return
        self.recheck()

    def get(self, key):
        self._maybe_recheck()
        if key in self._cache:
            return self._cache[key]
        self.fetches += 1
        from urllib.parse import quote
        out = self._call(f"/api/record?key={quote(key)}")
        val = dec(out["value"]) if out.get("ok") else None
        self._cache[key] = val
        return val

    def keys(self, prefix=""):
        from urllib.parse import quote
        return self._call(f"/api/keys?prefix={quote(prefix)}")["keys"]

    def recheck(self):
        """The 30-minute pull, remote form: read the journal tail past
        our watermark and drop ONLY the touched keys."""
        self.rechecks += 1
        self._last_recheck = self.clock()
        out = self._call(f"/api/journal?since={self.watermark}")
        for ev in out["events"]:
            e = dec(ev["e"])
            if e.get("verdict") == "admitted":
                key = e.get("edit", {}).get("key")
                self._cache.pop(key, None)
            self.watermark = ev["seq"]
        w = self._call("/api/watermark")
        self.pack_version = w["pack_version"]

    def job(self):
        cache = self

        class _Job:
            def __enter__(self):
                cache._pinned += 1
                return cache

            def __exit__(self, *exc):
                cache._pinned -= 1
                cache._maybe_recheck()
                return False

        return _Job()

    def close(self):
        pass
