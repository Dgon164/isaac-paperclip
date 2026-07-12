"""Face battery — the web door, held to the same laws.

F1 GET / serves the page (upload form, the honesty promise)
F2 POST a real CSV -> verdict + SPOKEN answer + report text
F3 POST noise -> the refusal arrives as an ANSWER (200, spoken
   refusal, report attached)
F4 the upload cap refuses oversize BEFORE reading the body (413)
F5 garbage input -> clean 400 with a why, no stack trace
F6 the access log carries method+path only (no query, no content)
Run: python test_face.py   (from isaac_store/)
"""
import io
import json
import os
import sys
import urllib.error
import urllib.request
from contextlib import redirect_stdout

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import face as face_mod  # noqa: E402

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def post(base, path, body, headers=None):
    req = urllib.request.Request(base + path, data=body.encode(),
                                 method="POST",
                                 headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def make_csv(rng, law=True, n=300):
    a = rng.uniform(-2, 2, n)
    b = rng.uniform(-2, 2, n)
    y = 3.0 * a * b + a ** 2 if law else rng.normal(0, 1, n)
    return "\n".join(["alpha,beta,energy"] +
                     [f"{a[i]:.6f},{b[i]:.6f},{y[i]:.6f}" for i in range(n)])


def main():
    rng = np.random.default_rng(53)
    print("  booting the face (engine + speech training)...")
    log = io.StringIO()
    face = face_mod.Face(port=0)
    base = face.start()
    try:
        print("F1. the page")
        with urllib.request.urlopen(base + "/", timeout=30) as r:
            html = r.read().decode()
        check("upload form served",
              "Ask Isaac" in html and "textarea" in html)
        check("the honesty promise is on the page",
              "refusal" in html and "leaves this machine" in html)

        print("F2. a real CSV through the web door")
        with redirect_stdout(log):
            code, j = post(base, "/api/challenge", make_csv(rng, True))
        check("verdict + spoken + report",
              code == 200 and j["verdict"] == "UNDERSTOOD"
              and "I understand this data about energy" in (j["spoken"] or "")
              and "energy = " in j["report_text"])

        print("F3. noise: the refusal is an answer")
        with redirect_stdout(log):
            code, j2 = post(base, "/api/challenge", make_csv(rng, False))
        check("200 with the refusal SPOKEN",
              code == 200 and j2["verdict"] == "NO RULE"
              and "will not pretend" in (j2["spoken"] or ""))

        print("F4. the upload cap holds the door")
        with redirect_stdout(log):
            code, j3 = post(base, "/api/challenge", "x",
                            headers={"Content-Length":
                                     str(face_mod.MAX_UPLOAD + 1)})
        check("oversize refused 413 before the body is read",
              code == 413 and "cap" in j3["why"])

        print("F5. garbage gets a clean why")
        with redirect_stdout(log):
            code, j4 = post(base, "/api/challenge",
                            "this,is\nnot,numbers,at,all\n???")
        check("400 with a readable why, no stack trace",
              code == 400 and "could not read" in j4["why"]
              and "Traceback" not in json.dumps(j4))

        print("F6. the log is content-free")
        with redirect_stdout(log):
            post(base, "/api/challenge?target=secret_column_name",
                 make_csv(rng, True))
        logged = log.getvalue()
        check("method+path only — no query, no content",
              "/api/challenge" in logged
              and "secret_column_name" not in logged
              and "alpha" not in logged)
    finally:
        face.stop()
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
