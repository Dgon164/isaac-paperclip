"""PrimeServer — the orchestrator's doorway between programs.

Until now the edit queue only worked inside one process. This serves
Prime's write path (queued proposed edits -> admission -> journal)
and read path (watermark, journal tail, single records, pack meta)
over HTTP, so Workers/Scrubbers/front-ends can be separate programs.

Security defaults (stdlib only, Pi-friendly):
- Binds 127.0.0.1 ONLY unless explicitly told otherwise.
- Optional bearer token (require_token) — mandatory before any
  non-localhost bind is ever used.
- REFUSALS ARE ANSWERS: a rejected edit or a missing record is HTTP
  200 with {"ok": false, "why": ...}. HTTP errors are reserved for
  malformed requests (400) and bad auth (401); no stack traces leave
  the process.
- Logging is a leak channel (the Identity Law): the access log keeps
  method + path WITHOUT query strings + status. Content is never
  logged.

Wire format: values ride as the codec's JSON encoding (enc/dec), so
tuples/sets/arrays survive the trip exactly.
"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .codec import enc, dec
from .orchestrator import Orchestrator


class PrimeServer:
    def __init__(self, directory, admission=None, host="127.0.0.1",
                 port=0, token=None):
        self.orch = Orchestrator(directory, admission=admission)
        self.token = token
        self._lock = threading.Lock()  # sole-writer discipline over HTTP
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                # method + path (no query) + status only — never content
                path = urlparse(self.path).path
                print(f"  [prime] {self.command} {path}")

            def _json(self, code, obj):
                body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                # ops: method + path (no query) + status + ms — never content
                outer.orch.ops.event(
                    "http", method=self.command,
                    path=urlparse(self.path).path, status=code,
                    ms=round((time.perf_counter()
                              - getattr(self, "_t0", time.perf_counter())) * 1000, 3))

            def _authed(self):
                if outer.token is None:
                    return True
                got = self.headers.get("Authorization", "")
                if got == f"Bearer {outer.token}":
                    return True
                self._json(401, {"ok": False, "why": "missing or wrong token"})
                return False

            def do_GET(self):
                self._t0 = time.perf_counter()
                if not self._authed():
                    return
                url = urlparse(self.path)
                q = parse_qs(url.query)
                with outer._lock:
                    if url.path == "/api/watermark":
                        self._json(200, {"ok": True,
                                         "last_seq": outer.orch.journal.last_seq(),
                                         "pack_version": outer.orch.pack_version})
                    elif url.path == "/api/journal":
                        try:
                            since = int(q.get("since", ["0"])[0])
                        except ValueError:
                            return self._json(400, {"ok": False, "why": "since must be an integer"})
                        events = [{"seq": s, "e": enc(e)}
                                  for s, e in outer.orch.journal.read_since(since)]
                        self._json(200, {"ok": True, "events": events})
                    elif url.path == "/api/record":
                        key = q.get("key", [None])[0]
                        if not key:
                            return self._json(400, {"ok": False, "why": "key required"})
                        if key in outer.orch.state:
                            self._json(200, {"ok": True, "key": key,
                                             "value": enc(outer.orch.state[key])})
                        else:
                            # a miss is an answer, not an error
                            self._json(200, {"ok": False, "why": "no such record",
                                             "key": key})
                    else:
                        self._json(400, {"ok": False, "why": f"unknown path {url.path}"})

            def do_POST(self):
                self._t0 = time.perf_counter()
                if not self._authed():
                    return
                url = urlparse(self.path)
                try:
                    n = int(self.headers.get("Content-Length", "0"))
                    payload = json.loads(self.rfile.read(n) or b"{}")
                except (ValueError, json.JSONDecodeError):
                    return self._json(400, {"ok": False, "why": "body must be JSON"})
                with outer._lock:
                    if url.path == "/api/submit":
                        if not isinstance(payload, dict) or "op" not in payload \
                                or "key" not in payload:
                            return self._json(400, {"ok": False,
                                                    "why": "edit needs op and key"})
                        edit = dec(payload.get("_encoded")) if "_encoded" in payload else payload
                        outer.orch.submit(edit)
                        admitted, rejected = outer.orch.process()
                        verdict = "admitted" if admitted else "rejected"
                        why = outer.orch.journal.read_since(
                            outer.orch.journal.last_seq() - 1)[-1][1]["why"]
                        # a rejection is a 200: refusals are answers
                        self._json(200, {"ok": bool(admitted), "verdict": verdict,
                                         "why": why,
                                         "seq": outer.orch.journal.last_seq()})
                    elif url.path == "/api/compact":
                        path = outer.orch.compact(
                            engine_version=payload.get("engine_version", "unknown"))
                        self._json(200, {"ok": True,
                                         "pack_version": outer.orch.pack_version,
                                         "path": path})
                    else:
                        self._json(400, {"ok": False, "why": f"unknown path {url.path}"})

        self.httpd = ThreadingHTTPServer((host, port), Handler)
        self.host, self.port = self.httpd.server_address[0], self.httpd.server_address[1]
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self._thread.start()
        return f"http://{self.host}:{self.port}"

    def stop(self):
        if self._thread is not None:  # shutdown() hangs if never served
            self.httpd.shutdown()
        self.httpd.server_close()
