"""Seeker battery — one question, one lifetime, receipts or refusal.

K1 corroborated answer: 3 sources agree (1 dissents) -> ANSWER with
   support counts and per-source receipts (url + hash)
K2 LOOP BAIT: every fetched page is stuffed with links to more pages
   — the Seeker fetches exactly the search results, zero links
   followed (the server's own request log is the proof)
K3 budgets are physical: a tight byte budget stops fetching early,
   cleanly, and the budget_used is reported
K4 conflict -> AMBIGUOUS refusal with the dossier (2 vs 2 sources)
K5 nothing found -> NONE (a refusal, not a guess)
K6 dead sources are skipped, the rest still answer
K7 provenance: the answer record is public-tier with receipts —
   ready for the Provenance Gate
Run: python test_seeker.py   (from isaac_store/)
"""
import os
import shutil
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store.seeker import Seeker

PASS = FAIL = 0
LINKS = "".join(f'<a href="/bait{i}.html">more</a>' for i in range(20))
PAGES = {
    "/a.html": f"<html>Jupiter surface gravity is 24.79 m/s squared.{LINKS}</html>",
    "/b.html": f"<html>The surface gravity of Jupiter: 24.79.{LINKS}</html>",
    "/c.html": f"<html>gravity on jupiter measures 24.8 at the surface{LINKS}</html>",
    "/d.html": f"<html>jupiter gravity is 25.9 (an old wrong figure){LINKS}</html>",
    "/x1.html": "<html>the answer is gravity 10.0 here</html>",
    "/x2.html": "<html>gravity equals 10.0 certainly</html>",
    "/y1.html": "<html>no, gravity is 20.0 instead</html>",
    "/y2.html": "<html>gravity: 20.0 confirmed</html>",
    "/empty.html": "<html>nothing relevant lives on this page at all</html>",
}
for i in range(20):
    PAGES[f"/bait{i}.html"] = f"<html>bait gravity 99.9 {LINKS}</html>"

REQUESTS = []


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


class MockWeb(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        REQUESTS.append(self.path)
        body = PAGES.get(self.path)
        if body is None:
            self.send_response(404); self.end_headers(); return
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), MockWeb)
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        print("K1. corroborated answer with receipts")
        REQUESTS.clear()
        s = Seeker(lambda q: [f"{base}/a.html", f"{base}/b.html",
                              f"{base}/c.html", f"{base}/d.html"])
        r = s.seek("what is the surface gravity of jupiter")
        check("ANSWER 24.79 by 3-source agreement",
              r["verdict"] == "ANSWER" and abs(r["answer"] - 24.79) < 0.02
              and r["support"] == 3, r.get("why", ""))
        check("receipts: url + hash per source",
              len(r["sources"]) == 4 and all("sha" in x for x in r["sources"]))
        check("the dissenting 25.9 is IN the dossier, not hidden",
              any(abs(d["value"] - 25.9) < 0.1 for d in r["dossier"]))

        print("K2. loop bait: zero links followed")
        fetched = set(REQUESTS)
        check("fetched exactly the 4 search results",
              fetched == {"/a.html", "/b.html", "/c.html", "/d.html"},
              f"{len(REQUESTS)} requests total")
        check("no bait page was ever requested",
              not any(p.startswith("/bait") for p in REQUESTS))

        print("K3. budgets are physical")
        REQUESTS.clear()
        s2 = Seeker(lambda q: [f"{base}/a.html", f"{base}/b.html",
                               f"{base}/c.html", f"{base}/d.html"],
                    budget=dict(max_total_bytes=700))
        r2 = s2.seek("what is the surface gravity of jupiter")
        check("tight byte budget stops fetching early, cleanly",
              r2["budget_used"]["sources"] < 4
              and len(REQUESTS) == r2["budget_used"]["sources"],
              f"fetched {r2['budget_used']['sources']}, "
              f"{r2['budget_used']['bytes']} bytes")

        print("K4. conflict -> AMBIGUOUS with the dossier")
        s3 = Seeker(lambda q: [f"{base}/x1.html", f"{base}/x2.html",
                               f"{base}/y1.html", f"{base}/y2.html"])
        r3 = s3.seek("what is the gravity value")
        check("2-vs-2 refuses with disagreement stated",
              r3["verdict"] == "AMBIGUOUS" and "disagree" in r3["why"])
        check("dossier shows both camps",
              len(r3["dossier"]) >= 2
              and {d["support"] for d in r3["dossier"][:2]} == {2})

        print("K5. nothing found -> NONE")
        s4 = Seeker(lambda q: [f"{base}/empty.html"])
        r4 = s4.seek("what is the surface gravity of jupiter")
        check("empty sources refuse, never guess", r4["verdict"] == "NONE")

        print("K6. dead sources skipped")
        s5 = Seeker(lambda q: [f"{base}/missing.html", f"{base}/a.html",
                               f"{base}/b.html"])
        r5 = s5.seek("what is the surface gravity of jupiter")
        check("404 skipped, the rest still corroborate",
              r5["verdict"] == "ANSWER" and r5["support"] == 2)

        print("K7. public provenance, gate-ready")
        check("answer record is public-tier with receipts",
              r["provenance"] == ["public"] and r["budget_used"]["bytes"] > 0)
    finally:
        httpd.shutdown(); httpd.server_close()
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
