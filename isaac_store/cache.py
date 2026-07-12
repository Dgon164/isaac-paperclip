"""LiveCache — the Worker's read side (owner design, 2026-07-11).

Workers live-load anything from Prime's packs, keep it cached
locally, and operate on the cache. Recheck is FIXED at 30 minutes
(owner-settled: the workers are the ones producing updates, not the
net). Two standing rules:

- A worker PINS one version per job: inside `with cache.job():` no
  recheck happens, however overdue — consistency beats freshness.
- Staleness cannot corrupt: proposals are judged at the admission
  gate against current state (see the battery's stale-proposal test).

A recheck is a delta, not a reload: read the journal tail past our
watermark, drop only touched keys, adopt a newer pack if one was
published. Reads resolve overlay (journal tail) -> local cache ->
pack fetch (measured 0.04 ms/node).
"""
import os
import time

from .journal import Journal
from .pack import PackReader, latest_pack

RECHECK_SECONDS = 30 * 60  # owner-settled 2026-07-11; not adaptive


class LiveCache:
    def __init__(self, packs_dir, journal_path,
                 recheck_seconds=RECHECK_SECONDS, clock=time.monotonic):
        self.packs_dir = packs_dir
        self.journal = Journal(journal_path)
        self.recheck_seconds = recheck_seconds
        self.clock = clock
        self._pinned = 0
        self.fetches = 0        # pack reads, for the battery's counting
        self.rechecks = 0
        self._adopt_latest_pack()
        self._last_recheck = self.clock()

    # ---- internals -------------------------------------------------
    def _adopt_latest_pack(self):
        self.pack_version, path = latest_pack(self.packs_dir)
        self.reader = PackReader(path) if path else None
        self.watermark = self.reader.meta.get("watermark", 0) if self.reader else 0
        self._cache = {}
        self._overlay = {}
        self._deleted = set()
        self._replay_tail()

    def _replay_tail(self):
        for seq, event in self.journal.read_since(self.watermark):
            if event.get("verdict") != "admitted":
                continue
            edit = event["edit"]
            op, key = edit["op"], edit["key"]
            if op == "put":
                self._overlay[key] = edit["value"]
                self._deleted.discard(key)
            elif op == "inc":
                base = self._overlay.get(key)
                if base is None and key not in self._deleted:
                    base = self._fetch_base(key) or 0
                self._overlay[key] = (base or 0) + edit.get("value", 1)
            elif op == "del":
                self._overlay.pop(key, None)
                self._deleted.add(key)
            self._cache.pop(key, None)  # invalidate ONLY touched keys
            self.watermark = seq

    def _fetch_base(self, key):
        if self.reader is not None and key in self.reader.index:
            self.fetches += 1
            return self.reader.get(key)
        return None

    def _maybe_recheck(self):
        if self._pinned:
            return  # pinned job: consistency beats freshness
        if self.clock() - self._last_recheck < self.recheck_seconds:
            return
        self.recheck()

    # ---- worker API ------------------------------------------------
    def get(self, key):
        self._maybe_recheck()
        if key in self._deleted:
            return None
        if key in self._overlay:
            return self._overlay[key]
        if key not in self._cache:
            self._cache[key] = self._fetch_base(key)
        return self._cache[key]

    def recheck(self):
        """The 30-minute pull: adopt a newer pack if published, else
        replay the journal tail and invalidate only touched keys."""
        self.rechecks += 1
        self._last_recheck = self.clock()
        newest, _ = latest_pack(self.packs_dir)
        if newest != self.pack_version:
            if self.reader:
                self.reader.close()
            self._adopt_latest_pack()
        else:
            self._replay_tail()

    def job(self):
        """Context manager: pin the current view for one whole job."""
        cache = self

        class _Job:
            def __enter__(self):
                cache._pinned += 1
                return cache

            def __exit__(self, *exc):
                cache._pinned -= 1
                cache._maybe_recheck()  # overdue recheck runs BETWEEN jobs
                return False

        return _Job()

    def close(self):
        if self.reader:
            self.reader.close()
