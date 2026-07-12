"""face.py — the alpha's face: a web page where a person drops a CSV
and Isaac answers (spoken if learned, the honest report always).

  python face.py [--port 8676]     # localhost only, stdlib only

Separate from PrimeServer on purpose: the orchestrator's doorway
stays thin and locked; the face does the heavy per-request work
(discover can take seconds) without blocking workers.

Door rules carried over: upload size capped BEFORE the body is read
(Content-Length), access log is method+path only, refusals are
answers (a NO RULE arrives as a 200 with the refusal spoken).
"""
import argparse
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from isaac_store import bridge                         # noqa: E402
from isaac_store.report import challenge, render_text  # noqa: E402
from isaac_store.speech_learn import (learn_speech,    # noqa: E402
                                      speak_learned)

MAX_UPLOAD = 20 * 1024 * 1024  # 20 MB — the door checks before reading

PAGE = """<!doctype html><meta charset="utf-8">
<title>Isaac — the honest report</title>
<style>body{font-family:system-ui,sans-serif;max-width:780px;margin:2rem auto;
padding:0 1rem}textarea{width:100%;height:10rem}pre{background:#f4f4f4;
padding:1rem;overflow-x:auto;white-space:pre-wrap}#spoken{font-size:1.1rem;
border-left:4px solid #446;padding:.6rem 1rem;background:#f8f8ff}
small{color:#666}</style>
<h2>Ask Isaac</h2>
<p>Drop a CSV (last column is the target, or name one below). Isaac
answers honestly: an equation he can defend, or a refusal with a
diagnosis. <small>Nothing you upload leaves this machine.</small></p>
<input type="file" id="f"> or paste:<br>
<textarea id="t" placeholder="alpha,beta,energy&#10;0.5,1.2,2.05&#10;..."></textarea><br>
target column (optional): <input id="target" size="12">
<button onclick="go()">Ask Isaac</button>
<div id="out"></div>
<script>
async function go(){
  let csv = document.getElementById('t').value;
  const f = document.getElementById('f').files[0];
  if (f) csv = await f.text();
  if (!csv.trim()) return;
  const tgt = document.getElementById('target').value.trim();
  document.getElementById('out').innerHTML = '<p>Isaac is working…</p>';
  const r = await fetch('/api/challenge' + (tgt ? '?target=' +
    encodeURIComponent(tgt) : ''), {method: 'POST', body: csv});
  const j = await r.json();
  let h = '';
  if (j.spoken) h += '<p id="spoken">' + j.spoken + '</p>';
  if (j.unspoken && j.unspoken.length)
    h += '<p><small>not yet taught to speak: ' + j.unspoken.join(', ')
       + ' — see the report</small></p>';
  h += '<pre>' + j.report_text + '</pre>';
  document.getElementById('out').innerHTML = h;
}
</script>"""


class Face:
    def __init__(self, host="127.0.0.1", port=8676):
        self.mod = bridge.load_isaac_module()
        self.speech_mind = self.mod.Isaac()
        corpus = open(os.path.join(HERE, "isaac_store",
                                   "speech_corpus.txt"),
                      encoding="utf-8").read()
        learn_speech(self.speech_mind, corpus)
        self._lock = threading.Lock()  # one challenge at a time (alpha)
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                print(f"  [face] {self.command} {urlparse(self.path).path}")

            def _json(self, code, obj):
                body = json.dumps(obj, ensure_ascii=False).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                body = PAGE.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                url = urlparse(self.path)
                if url.path != "/api/challenge":
                    return self._json(400, {"ok": False,
                                            "why": "unknown path"})
                n = int(self.headers.get("Content-Length", "0"))
                if n > MAX_UPLOAD:  # refused BEFORE the body is read
                    return self._json(413, {
                        "ok": False,
                        "why": f"upload over the {MAX_UPLOAD // 2**20} MB cap"})
                csv_text = self.rfile.read(n).decode("utf-8", "replace")
                target = (parse_qs(url.query).get("target", [None])[0]
                          or None)
                try:
                    with outer._lock:
                        rep = challenge(csv_text, target=target,
                                        mod=outer.mod)
                        spoken = speak_learned(outer.speech_mind, rep)
                except Exception as e:
                    return self._json(400, {"ok": False,
                                            "why": f"could not read that "
                                                   f"CSV: {type(e).__name__}"})
                self._json(200, {
                    "ok": True, "verdict": rep["verdict"],
                    "spoken": (spoken["response"]
                               if spoken["can_speak"] else None),
                    "unspoken": spoken.get("unspoken", []),
                    "report": {k: v for k, v in rep.items()
                               if k != "finding"},
                    "report_text": render_text(rep)})

        self.httpd = ThreadingHTTPServer((host, port), Handler)
        self.host = self.httpd.server_address[0]
        self.port = self.httpd.server_address[1]
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self.httpd.serve_forever,
                                        daemon=True)
        self._thread.start()
        return f"http://{self.host}:{self.port}"

    def stop(self):
        if self._thread is not None:
            self.httpd.shutdown()
        self.httpd.server_close()


def main():
    p = argparse.ArgumentParser(description="Isaac's face (localhost)")
    p.add_argument("--port", type=int, default=8676)
    a = p.parse_args()
    face = Face(port=a.port)
    url = face.start()
    print(f"  ISAAC'S FACE — open {url}")
    print("  drop a CSV, get the honest answer. Ctrl+C to stop.")
    try:
        face._thread.join()
    except KeyboardInterrupt:
        face.stop()
        print("\n  stopped.")


if __name__ == "__main__":
    main()
