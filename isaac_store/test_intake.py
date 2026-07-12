"""Intake battery — every format through the one door, budgets held.

T1 csv + tsv -> tables (headers, numeric coercion)
T2 json + jsonl records -> tables; non-tabular json -> text
T3 npy + npz arrays -> tables
T4 txt/md -> text; html -> tags stripped
T5 rich text: rtf stripped; docx (a real zip-of-XML) -> paragraphs
T6 xlsx (a real zip-of-XML) -> numeric table
T7 a folder of mixed files -> everything found, skips FILED with why
T8 a zip of mixed files -> same door, same laws; the zip-bomb guard
   refuses oversize entries cleanly
T9 raw text dispatch: delimited numbers -> table; prose -> text
T10 provenance on every item (sha/bytes/source); a table item feeds
    challenge() end-to-end and comes back UNDERSTOOD
Run: python test_intake.py   (from isaac_store/)
"""
import io
import os
import shutil
import sys
import tempfile
import zipfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import bridge
from isaac_store.intake import ingest, table_csv
from isaac_store.report import challenge

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


CSV = "alpha,beta,energy\n" + "\n".join(
    f"{a},{b},{3*a*b + a*a}" for a, b in
    [(x / 10, y / 10) for x in range(-19, 20, 2) for y in range(-19, 20, 4)])


def make_docx(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml",
                   '<w:document xmlns:w="http://schemas.openxmlformats.org/'
                   'wordprocessingml/2006/main"><w:body>'
                   "<w:p><w:r><w:t>Kepler noted the periods.</w:t></w:r></w:p>"
                   "<w:p><w:r><w:t>The square grows with the cube.</w:t></w:r>"
                   "</w:p></w:body></w:document>")


def make_xlsx(path):
    rows = "".join(
        f'<row r="{i+1}">' + "".join(
            f'<c r="{chr(65+j)}{i+1}"{" t=\"s\"" if i == 0 else ""}>'
            f"<v>{j if i == 0 else v}</v></c>"
            for j, v in enumerate(r)) + "</row>"
        for i, r in enumerate([["x", "y"], [1.0, 2.0], [2.0, 4.0],
                               [3.0, 6.0], [4.0, 8.0]]))
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/sharedStrings.xml",
                   "<sst><si><t>x</t></si><si><t>y</t></si></sst>")
        z.writestr("xl/worksheets/sheet1.xml",
                   f"<worksheet><sheetData>{rows}</sheetData></worksheet>")


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_intake_")
    try:
        d = tmp
        open(os.path.join(d, "data.csv"), "w").write(CSV)
        open(os.path.join(d, "data.tsv"), "w").write(
            CSV.replace(",", "\t"))
        open(os.path.join(d, "recs.jsonl"), "w").write(
            '{"u": 1, "v": 2}\n{"u": 2, "v": 4}\n{"u": 3, "v": 6}\n'
            '{"u": 4, "v": 8}\n')
        open(os.path.join(d, "prose.json"), "w").write(
            '{"note": "just an object"}')
        np.save(os.path.join(d, "arr.npy"),
                np.arange(12.0).reshape(4, 3))
        np.savez(os.path.join(d, "packs.npz"),
                 one=np.arange(8.0).reshape(4, 2))
        open(os.path.join(d, "notes.md"), "w").write("# notes\nplain words")
        open(os.path.join(d, "page.html"), "w").write(
            "<html><style>x{}</style><p>visible words</p></html>")
        open(os.path.join(d, "memo.rtf"), "w").write(
            r"{\rtf1\ansi Hello from \b rich\b0 text land.}")
        make_docx(os.path.join(d, "doc.docx"))
        make_xlsx(os.path.join(d, "book.xlsx"))
        open(os.path.join(d, "weird.xyz"), "w").write("???")

        print("T1. csv + tsv")
        r1 = ingest(os.path.join(d, "data.csv"))
        r1b = ingest(os.path.join(d, "data.tsv"))
        t = r1["items"][0]
        check("csv table with headers", t["kind"] == "table"
              and t["columns"] == ["alpha", "beta", "energy"])
        check("tsv table too", r1b["items"][0]["columns"] == t["columns"])

        print("T2. json roads")
        r2 = ingest(os.path.join(d, "recs.jsonl"))
        check("jsonl records -> table",
              r2["items"][0]["kind"] == "table"
              and r2["items"][0]["columns"] == ["u", "v"])
        r2b = ingest(os.path.join(d, "prose.json"))
        check("non-tabular json -> text", r2b["items"][0]["kind"] == "text")

        print("T3. numpy roads")
        check("npy -> table",
              ingest(os.path.join(d, "arr.npy"))["items"][0]["kind"] == "table")
        r3 = ingest(os.path.join(d, "packs.npz"))
        check("npz -> table per array", r3["items"][0]["name"].endswith(":one"))

        print("T4. text + html")
        check("md -> text", "plain words" in
              ingest(os.path.join(d, "notes.md"))["items"][0]["text"])
        h = ingest(os.path.join(d, "page.html"))["items"][0]["text"]
        check("html stripped", "visible words" in h and "<p>" not in h)

        print("T5. rich text")
        rtf = ingest(os.path.join(d, "memo.rtf"))["items"][0]["text"]
        check("rtf stripped", "rich" in rtf and "\\b" not in rtf)
        dx = ingest(os.path.join(d, "doc.docx"))["items"][0]["text"]
        check("docx paragraphs extracted",
              "Kepler noted the periods." in dx
              and "square grows with the cube" in dx)

        print("T6. xlsx")
        x = ingest(os.path.join(d, "book.xlsx"))["items"][0]
        check("xlsx -> numeric table", x["kind"] == "table"
              and x["columns"] == ["x", "y"] and x["rows"][1] == [2.0, 4.0])

        print("T7. a folder of everything")
        rf = ingest(d)
        kinds = [i["kind"] for i in rf["items"]]
        check("all tables and texts found",
              kinds.count("table") >= 6 and kinds.count("text") >= 4,
              f"{len(rf['items'])} items")
        check("the unsupported file is FILED, not silent",
              any("weird.xyz" in s["source"] and "unsupported" in s["why"]
                  for s in rf["skipped"]))

        print("T8. the zip door")
        zp = os.path.join(tmp, "bundle.zip")
        with zipfile.ZipFile(zp, "w") as z:
            z.write(os.path.join(d, "data.csv"), "inner/data.csv")
            z.write(os.path.join(d, "doc.docx"), "inner/doc.docx")
            z.write(os.path.join(d, "weird.xyz"), "weird.xyz")
        rz = ingest(zp)
        check("zip walked: table + rich text + filed skip",
              any(i["kind"] == "table" for i in rz["items"])
              and any(i["kind"] == "text" for i in rz["items"])
              and len(rz["skipped"]) == 1)
        import isaac_store.intake as ik
        old = ik.MAX_ENTRY_BYTES
        ik.MAX_ENTRY_BYTES = 10
        try:
            rb = ingest(zp)
            check("zip-bomb guard: oversize entries refused with why",
                  len(rb["items"]) == 0 and
                  all("cap" in s["why"] or "unsupported" in s["why"]
                      for s in rb["skipped"]))
        finally:
            ik.MAX_ENTRY_BYTES = old

        print("T9. raw text dispatch")
        check("delimited numbers -> table",
              ingest(CSV)["items"][0]["kind"] == "table")
        check("prose -> text",
              ingest("just some plain sentences\nnothing tabular here\n"
                     "at all")["items"][0]["kind"] == "text")

        print("T10. provenance + end-to-end to the report")
        check("every item carries provenance",
              all("sha" in i["provenance"] and i["provenance"]["bytes"] > 0
                  for i in rf["items"]))
        mod = bridge.load_isaac_module()
        rep = challenge(table_csv(t), mod=mod)
        check("intake table -> honest report UNDERSTOOD",
              rep["verdict"] == "UNDERSTOOD"
              and "alpha" in rep["equation"], rep["equation"][:60])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
