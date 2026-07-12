"""Append-only JSONL journal — the findings-ledger organ generalized
to all state changes. One event per line, total order via seq numbers.
Crash-tolerant: a truncated final line (power loss mid-write) is
detected and ignored, never fatal.
"""
import json
import os

from .codec import enc, dec


class Journal:
    def __init__(self, path):
        self.path = path
        self._last_seq = 0
        if os.path.exists(path):
            for seq, _ in self._scan():
                self._last_seq = seq

    def _scan(self):
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.endswith("\n"):
                    break  # truncated tail from a crash — ignore
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    break  # corrupt tail — everything before it stands
                yield rec["seq"], rec["e"]

    def last_seq(self):
        return self._last_seq

    def append(self, event, fsync=False):
        """Assign the next seq and durably append one event. Returns seq."""
        self._last_seq += 1
        line = json.dumps({"seq": self._last_seq, "e": enc(event)},
                          ensure_ascii=False, sort_keys=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
            if fsync:
                os.fsync(f.fileno())
        return self._last_seq

    def read_since(self, watermark):
        """All (seq, event) with seq > watermark, in order."""
        if not os.path.exists(self.path):
            return []
        return [(seq, dec(e)) for seq, e in self._scan() if seq > watermark]

    def trim(self, keep_after_seq):
        """Retention (owner's restore-point cache): drop events with
        seq <= keep_after_seq — they are baked into a kept snapshot.
        Numbering is preserved; the rewrite is atomic. Returns the
        number of events dropped."""
        if not os.path.exists(self.path):
            return 0
        kept, dropped, last_line = [], 0, None
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.endswith("\n"):
                    break
                try:
                    seq = json.loads(line)["seq"]
                except (json.JSONDecodeError, KeyError):
                    break
                last_line = line
                if seq > keep_after_seq:
                    kept.append(line)
                else:
                    dropped += 1
        if not kept and last_line is not None:
            # NEVER trim to empty: the final event preserves the seq
            # counter (it is baked into the kept snapshot, so it never
            # replays — but losing it would restart numbering below
            # the pack watermark and recovery would skip new events).
            kept, dropped = [last_line], dropped - 1
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.writelines(kept)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)
        return dropped
