"""The orchestrator — sole writer of the mind (owner design 2026-07-11).

Workers submit PROPOSED edits; the orchestrator applies them in queue
order behind the admission gate, journals every verdict (rejections
wrong-kept with their why), and periodically compacts the journal into
an immutable pack. Recovery invariant: latest pack + journal tail
replays to exactly the current state — verified by the battery.

THIN by design: queue + admission + journal + compaction. No thinking.
"""
import os
import threading
import time

from .journal import Journal
from .ops import OpsLedger
from .pack import PackReader, latest_pack, write_pack


def _admit_all(edit, state):
    return True, "default admission (no gate installed)"


class Orchestrator:
    def __init__(self, directory, admission=None, retention_keep=3):
        """retention_keep: the owner's restore-point cache (2026-07-12)
        — keep the newest N pack snapshots (default 3 supersession
        layers) + the journal tail spanning them. None = full log,
        nothing ever pruned."""
        self.dir = directory
        self.retention_keep = retention_keep
        os.makedirs(directory, exist_ok=True)
        self.packs_dir = os.path.join(directory, "packs")
        self.journal = Journal(os.path.join(directory, "journal.jsonl"))
        self.ops = OpsLedger(os.path.join(directory, "ops.jsonl"))
        self.admission = admission or _admit_all
        self.state = {}
        self._queue = []
        self._lock = threading.Lock()  # workers may submit from threads
        self._load()

    # ---- read side -------------------------------------------------
    def _load(self):
        version, path = latest_pack(self.packs_dir)
        self.pack_version = version
        watermark = 0
        if path:
            r = PackReader(path)
            self.state = r.load_all()
            watermark = r.meta["watermark"]
            r.close()
        for _seq, event in self.journal.read_since(watermark):
            if event.get("verdict") == "admitted":
                self._apply(event["edit"])

    def get(self, key):
        return self.state.get(key)

    # ---- write side (sole writer) ----------------------------------
    def submit(self, edit):
        """Queue a proposed edit. edit = {op, key, value?, who, why?}."""
        with self._lock:
            self._queue.append(edit)

    def process(self):
        """Drain the queue in order through the admission gate.
        Returns (admitted, rejected) counts."""
        with self._lock:
            batch, self._queue = self._queue, []
        t0 = time.perf_counter()
        admitted = rejected = 0
        for edit in batch:
            # optimistic concurrency for parallel workers: an edit may
            # carry "expect" — what the worker believed current when it
            # decided. Queue order arbitrates races (job claims): the
            # first claim changes the record, later claims mismatch.
            if "expect" in edit and self.state.get(edit["key"]) != edit["expect"]:
                self.journal.append({"verdict": "rejected", "edit": edit,
                                     "why": "based on superseded evidence "
                                            "(expect != current)"})
                rejected += 1
                continue
            ok, why = self.admission(edit, self.state)
            if ok:
                self._apply(edit)
                self.journal.append({"verdict": "admitted", "edit": edit, "why": why})
                admitted += 1
            else:
                # wrong-kept: the rejection and its why are ledger material —
                # but wrong-kept applies to the JUDGMENT, never to PII: an
                # Identity Law refusal keeps op/key/who, not the content.
                # (Found by the learning battery 2026-07-12: a verbatim
                # rejected edit put private bytes in Prime's journal.)
                kept = edit
                if "Identity Law" in why:
                    kept = {k: v for k, v in edit.items() if k != "value"}
                    kept["value_redacted"] = "Identity Law: content not retained"
                self.journal.append({"verdict": "rejected", "edit": kept, "why": why})
                rejected += 1
        if batch:
            self.ops.event("process", admitted=admitted, rejected=rejected,
                           ms=round((time.perf_counter() - t0) * 1000, 3))
        return admitted, rejected

    def _apply(self, edit):
        op, key = edit["op"], edit["key"]
        if op == "put":
            self.state[key] = edit["value"]
        elif op == "inc":
            self.state[key] = self.state.get(key, 0) + edit.get("value", 1)
        elif op == "del":
            # supersession, not erasure: the journal keeps the history
            self.state.pop(key, None)
        elif op == "restore":
            # rewind as an APPEND: state becomes the named restore
            # point; the rewind itself is on the record
            r = PackReader(os.path.join(self.packs_dir,
                                        f"mind.v{edit['value']}.isaacpack"))
            self.state = r.load_all()
            r.close()
        else:
            raise ValueError(f"unknown op {op!r}")

    def compact(self, engine_version="unknown"):
        """Publish the current state as the next immutable pack."""
        t0 = time.perf_counter()
        version = self.pack_version + 1
        path = write_pack(self.packs_dir, version, self.state, meta={
            "version": version,
            "watermark": self.journal.last_seq(),
            "engine_version": engine_version,
            "written": time.strftime("%Y-%m-%d %H:%M:%S"),
            "records": len(self.state),
        })
        self.pack_version = version
        self.ops.event("compact", version=version, records=len(self.state),
                       bytes=os.path.getsize(path),
                       ms=round((time.perf_counter() - t0) * 1000, 3))
        self._retention()
        return path

    def _retention(self):
        """The restore-point cache: prune snapshots beyond the kept
        supersession layers and trim the journal to the span of the
        oldest kept one. Full-log mode (retention_keep=None) prunes
        nothing, ever."""
        if self.retention_keep is None:
            return
        versions = []
        for name in os.listdir(self.packs_dir):
            if name.startswith("mind.v") and name.endswith(".isaacpack"):
                try:
                    versions.append(int(name[len("mind.v"):-len(".isaacpack")]))
                except ValueError:
                    pass
        versions.sort()
        keep = versions[-self.retention_keep:]
        pruned = 0
        for v in versions:
            if v in keep:
                continue
            try:
                os.remove(os.path.join(self.packs_dir, f"mind.v{v}.isaacpack"))
                pruned += 1
            except OSError:
                pass  # a reader holds it open (Windows lock): next time
        oldest = PackReader(os.path.join(self.packs_dir,
                                         f"mind.v{keep[0]}.isaacpack"))
        floor = oldest.meta.get("watermark", 0)
        oldest.close()
        trimmed = self.journal.trim(floor)
        if pruned or trimmed:
            self.ops.event("retention", pruned_packs=pruned,
                           trimmed_events=trimmed, kept=len(keep))

    def restore(self, version):
        """Rewind to a kept restore point. The restore is an ADMITTED
        JOURNAL EVENT — history is appended to, never rewritten."""
        edit = {"op": "restore", "key": f"restore:v{version}",
                "value": version, "who": "operator"}
        self._apply(edit)
        self.journal.append({"verdict": "admitted", "edit": edit,
                             "why": f"operator restore to snapshot v{version}"})
        self.ops.event("restore", version=version, records=len(self.state))
        return len(self.state)
