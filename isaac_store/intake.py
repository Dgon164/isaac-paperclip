"""Intake — files, folders, zips, raw text, rich text -> what Isaac
can work with (owner, 2026-07-12: "api calls, file formats and data
converters").

ingest(source) accepts:
  - a file path: .csv .tsv .json .jsonl .npy .npz .xlsx .txt .md
    .log .html .htm .rtf .docx
  - a folder (recursed), a .zip (walked in memory, nested folders ok)
  - raw text (a string with newlines): dispatched to table if it
    parses as delimited numbers, else text

and returns {"items": [...], "skipped": [...]} where every item is
  {"kind": "table", name, columns, rows(list of float-lists),
   dropped_columns, provenance{source, sha, bytes}}   or
  {"kind": "text", name, text, provenance{...}}

Door laws: budgets are physical (max files / max total bytes / max
bytes per zip entry — the zip-bomb guard); anything unsupported or
over budget is SKIPPED WITH ITS WHY, filed in "skipped", never
silent. Rich formats (.docx/.xlsx) are parsed as what they really
are — zips of XML — stdlib only.
"""
import csv as _csv
import hashlib
import io
import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile

import numpy as np

MAX_FILES = 200
MAX_TOTAL_BYTES = 200 * 1024 * 1024
MAX_ENTRY_BYTES = 50 * 1024 * 1024

TABLE_EXT = {".csv", ".tsv", ".json", ".jsonl", ".npy", ".npz", ".xlsx"}
TEXT_EXT = {".txt", ".md", ".log", ".html", ".htm", ".rtf", ".docx"}


def _prov(name, data):
    return dict(source=name, bytes=len(data),
                sha=hashlib.sha256(data).hexdigest()[:16])


def _num(v):
    try:
        float(v)
        return True
    except (ValueError, TypeError):
        return False


def _rows_to_table(name, rows, prov):
    """Rows of strings -> numeric table (header auto-detected;
    non-numeric columns dropped BUT ACCOUNTED)."""
    rows = [r for r in rows if any(str(v).strip() for v in r)]
    if len(rows) < 3:
        return None
    header = None
    if not all(_num(v) for v in rows[0]):
        header, rows = [str(h).strip() for h in rows[0]], rows[1:]
    width = max(len(r) for r in rows)
    names = header or [f"col{i}" for i in range(width)]
    keep, dropped = [], []
    for c in range(width):
        vals = [r[c] if c < len(r) else "" for r in rows]
        if sum(_num(v) for v in vals) >= 0.9 * len(vals):
            keep.append(c)
        else:
            dropped.append(names[c] if c < len(names) else f"col{c}")
    if len(keep) < 2:
        return None
    data = [[float(r[c]) if c < len(r) and _num(r[c]) else float("nan")
             for c in keep] for r in rows]
    data = [r for r in data if all(v == v for v in r)]  # drop NaN rows
    if len(data) < 3:
        return None
    return dict(kind="table", name=name,
                columns=[names[c] if c < len(names) else f"col{c}"
                         for c in keep],
                rows=data, dropped_columns=dropped, provenance=prov)


def _strip_html(b):
    text = re.sub(rb"<script.*?</script>|<style.*?</style>", b" ", b,
                  flags=re.S | re.I)
    return re.sub(rb"<[^>]+>", b" ", text).decode("utf-8", "replace")


def _strip_rtf(b):
    t = b.decode("latin-1", "replace")
    t = re.sub(r"\\'[0-9a-fA-F]{2}", " ", t)
    t = re.sub(r"\\[a-zA-Z]+-?\d* ?", " ", t)
    return t.replace("{", " ").replace("}", " ")


def _docx_text(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml = z.read("word/document.xml")
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    root = ET.fromstring(xml)
    paras = []
    for p in root.iter("{%s}p" % ns["w"]):
        paras.append("".join(t.text or ""
                             for t in p.iter("{%s}t" % ns["w"])))
    return "\n".join(paras)


def _local(tag):
    return tag.split("}")[-1]


def _xlsx_rows(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.iter()
                              if _local(t.tag) == "t")
                      for si in root]
        sheet = next(n for n in z.namelist()
                     if n.startswith("xl/worksheets/sheet"))
        root = ET.fromstring(z.read(sheet))
        rows = []
        for row in root.iter():
            if _local(row.tag) != "row":
                continue
            cells = {}
            for c in row:
                ref = c.attrib.get("r", "")
                col = sum((ord(ch) - 64) * 26 ** i for i, ch in
                          enumerate(reversed(re.sub(r"\d", "", ref)))) - 1
                v = next((el for el in c if _local(el.tag) == "v"), None)
                if v is None or v.text is None:
                    continue
                cells[col] = (shared[int(v.text)]
                              if c.attrib.get("t") == "s" else v.text)
            if cells:
                width = max(cells) + 1
                rows.append([cells.get(i, "") for i in range(width)])
        return rows


def _ingest_bytes(name, data, out, budget):
    ext = os.path.splitext(name)[1].lower()
    prov = _prov(name, data)
    try:
        if ext in (".csv", ".tsv") or (ext == "" and b"," in data[:2000]):
            delim = "\t" if ext == ".tsv" else ","
            rows = list(_csv.reader(
                io.StringIO(data.decode("utf-8-sig", "replace")),
                delimiter=delim))
            t = _rows_to_table(name, rows, prov)
            out["items"].append(t) if t else out["skipped"].append(
                dict(source=name, why="no numeric table found"))
        elif ext == ".jsonl":
            recs = [json.loads(ln) for ln in
                    data.decode("utf-8", "replace").splitlines()
                    if ln.strip()]
            _json_records(name, recs, out, prov)
        elif ext == ".json":
            _json_records(name, json.loads(data.decode("utf-8", "replace")),
                          out, prov)
        elif ext == ".npy":
            arr = np.load(io.BytesIO(data), allow_pickle=False)
            _array_table(name, arr, out, prov)
        elif ext == ".npz":
            z = np.load(io.BytesIO(data), allow_pickle=False)
            for key in z.files:
                _array_table(f"{name}:{key}", z[key], out, prov)
        elif ext == ".xlsx":
            t = _rows_to_table(name, _xlsx_rows(data), prov)
            out["items"].append(t) if t else out["skipped"].append(
                dict(source=name, why="no numeric table in sheet"))
        elif ext == ".docx":
            out["items"].append(dict(kind="text", name=name,
                                     text=_docx_text(data),
                                     provenance=prov))
        elif ext == ".rtf":
            out["items"].append(dict(kind="text", name=name,
                                     text=_strip_rtf(data),
                                     provenance=prov))
        elif ext in (".html", ".htm"):
            out["items"].append(dict(kind="text", name=name,
                                     text=_strip_html(data),
                                     provenance=prov))
        elif ext in (".txt", ".md", ".log"):
            out["items"].append(dict(kind="text", name=name,
                                     text=data.decode("utf-8", "replace"),
                                     provenance=prov))
        else:
            out["skipped"].append(dict(source=name,
                                       why=f"unsupported type {ext or '?'}"))
    except Exception as e:
        out["skipped"].append(dict(source=name,
                                   why=f"unreadable: {type(e).__name__}"))


def _json_records(name, recs, out, prov):
    if isinstance(recs, list) and recs and isinstance(recs[0], dict):
        cols = sorted({k for r in recs for k in r})
        rows = [cols] + [[r.get(c, "") for c in cols] for r in recs]
        t = _rows_to_table(name, rows, prov)
        if t:
            out["items"].append(t)
            return
    text = json.dumps(recs)[:200000]
    out["items"].append(dict(kind="text", name=name, text=text,
                             provenance=prov))


def _array_table(name, arr, out, prov):
    arr = np.asarray(arr)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    if arr.ndim != 2 or not np.issubdtype(arr.dtype, np.number):
        out["skipped"].append(dict(source=name,
                                   why=f"array shape {arr.shape} not a table"))
        return
    out["items"].append(dict(
        kind="table", name=name,
        columns=[f"col{i}" for i in range(arr.shape[1])],
        rows=np.asarray(arr, float).tolist(), dropped_columns=[],
        provenance=prov))


def ingest(source):
    """The one door. Returns {"items": [...], "skipped": [...]}."""
    out = {"items": [], "skipped": []}
    budget = {"files": 0, "bytes": 0}

    def take(name, data):
        budget["files"] += 1
        budget["bytes"] += len(data)
        if budget["files"] > MAX_FILES:
            out["skipped"].append(dict(source=name,
                                       why=f"over the {MAX_FILES}-file budget"))
            return
        if budget["bytes"] > MAX_TOTAL_BYTES:
            out["skipped"].append(dict(source=name,
                                       why="over the total-bytes budget"))
            return
        _ingest_bytes(name, data, out, budget)

    if isinstance(source, str) and "\n" in source:
        # raw text: table if it parses as one, else text
        rows = list(_csv.reader(io.StringIO(source)))
        t = _rows_to_table("raw_text", rows, _prov("raw_text",
                                                   source.encode()))
        if t:
            out["items"].append(t)
        else:
            out["items"].append(dict(kind="text", name="raw_text",
                                     text=source,
                                     provenance=_prov("raw_text",
                                                      source.encode())))
        return out
    if os.path.isdir(source):
        for dirpath, _dn, files in os.walk(source):
            for f in sorted(files):
                p = os.path.join(dirpath, f)
                take(os.path.relpath(p, source), open(p, "rb").read())
        return out
    if str(source).lower().endswith(".zip"):
        with zipfile.ZipFile(source) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                if info.file_size > MAX_ENTRY_BYTES:  # zip-bomb guard
                    out["skipped"].append(dict(
                        source=info.filename,
                        why=f"entry over the "
                            f"{MAX_ENTRY_BYTES // 2**20} MB cap"))
                    continue
                take(info.filename, z.read(info))
        return out
    take(os.path.basename(str(source)), open(source, "rb").read())
    return out


def table_csv(item):
    """A table item -> CSV text for report.challenge()."""
    lines = [",".join(item["columns"])]
    lines += [",".join(f"{v:.10g}" for v in row) for row in item["rows"]]
    return "\n".join(lines)
