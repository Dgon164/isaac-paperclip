"""Immutable indexed pack files — the snapshot format. NO database.

Layout:  MAGIC (12 bytes) | index-offset (20 ascii digits) | records
         (each utf-8 JSON of an encoded value) | index JSON.
The loader reads MAGIC + offset + index only (tiny); records are
fetched by seek on demand — this is what makes partial net loading a
property of the format instead of an engine.

Published by write-temp-then-atomic-rename. A pack, once published,
is NEVER modified; a new version supersedes it (old kept).
"""
import json
import os

from .codec import enc, dec

MAGIC = b"ISAACPACK1\n\n"
_OFF_LEN = 20


def pack_path(directory, version):
    return os.path.join(directory, f"mind.v{version}.isaacpack")


def latest_pack(directory):
    """(version, path) of the highest published pack, or (0, None)."""
    best, best_path = 0, None
    if os.path.isdir(directory):
        for name in os.listdir(directory):
            if name.startswith("mind.v") and name.endswith(".isaacpack"):
                try:
                    v = int(name[len("mind.v"):-len(".isaacpack")])
                except ValueError:
                    continue
                if v > best:
                    best, best_path = v, os.path.join(directory, name)
    return best, best_path


def write_pack(directory, version, records, meta):
    """Write records {name: value} + meta as an immutable pack. Returns path."""
    os.makedirs(directory, exist_ok=True)
    final = pack_path(directory, version)
    if os.path.exists(final):
        raise FileExistsError(f"pack v{version} already published — packs are immutable")
    tmp = final + ".tmp"
    index = {}
    with open(tmp, "wb") as f:
        f.write(MAGIC)
        f.write(b"0" * _OFF_LEN)  # placeholder for index offset
        for name, value in records.items():
            blob = json.dumps(enc(value), ensure_ascii=False,
                              sort_keys=True).encode("utf-8")
            index[name] = [f.tell(), len(blob)]
            f.write(blob)
        index_off = f.tell()
        f.write(json.dumps({"meta": meta, "index": index},
                           ensure_ascii=False).encode("utf-8"))
        f.seek(len(MAGIC))
        f.write(str(index_off).rjust(_OFF_LEN, "0").encode("ascii"))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, final)
    return final


class PackReader:
    """Opens header + index only. Records load on demand via get()."""

    def __init__(self, path):
        self.path = path
        self._f = open(path, "rb")
        if self._f.read(len(MAGIC)) != MAGIC:
            raise ValueError(f"{path}: not an isaacpack")
        index_off = int(self._f.read(_OFF_LEN))
        self._f.seek(index_off)
        tail = json.loads(self._f.read().decode("utf-8"))
        self.meta = tail["meta"]
        self.index = tail["index"]

    def names(self):
        return list(self.index.keys())

    def get(self, name):
        off, length = self.index[name]
        self._f.seek(off)
        return dec(json.loads(self._f.read(length).decode("utf-8")))

    def load_all(self):
        return {name: self.get(name) for name in self.index}

    def close(self):
        self._f.close()
