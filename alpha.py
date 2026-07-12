"""alpha.py — the alpha live launcher (dc, 2026-07-12).

Starts Prime as a service: orchestrator + identity gate + HTTP
doorway + ops ledger, from a data directory that persists across
restarts (journal + packs + ops.jsonl).

  python alpha.py                    # data/ next to this file, port 8675
  python alpha.py --dir D --port P --token T

Localhost-only. A token is REQUIRED to bind anything but 127.0.0.1.
Ctrl+C stops it; state survives (recovery invariant: pack + journal
tail == the mind as it was).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from isaac_store.scrubber import identity_gate, seed_skill  # noqa: E402
from isaac_store.server import PrimeServer                  # noqa: E402
from isaac_store.skills import publish_skill, pull_skill    # noqa: E402


def launch(directory, port=8675, host="127.0.0.1", token=None):
    if host != "127.0.0.1" and not token:
        raise SystemExit("REFUSED: non-localhost bind requires --token")
    server = PrimeServer(directory, admission=identity_gate(),
                         host=host, port=port, token=token)
    # first boot: educate Prime with the seed scrubber skill
    if server.orch.get("skill:scrubber") is None:
        publish_skill(server.orch, "scrubber", seed_skill(), who="alpha_boot")
    return server


def main():
    p = argparse.ArgumentParser(description="Isaac alpha live (Prime)")
    p.add_argument("--dir", default=os.path.join(HERE, "data", "prime"))
    p.add_argument("--port", type=int, default=8675)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--token", default=None)
    a = p.parse_args()
    server = launch(a.dir, port=a.port, host=a.host, token=a.token)
    url = server.start()
    o = server.orch
    print(f"  ISAAC ALPHA LIVE — Prime at {url}")
    print(f"  data: {a.dir}")
    print(f"  pack v{o.pack_version}, journal seq {o.journal.last_seq()}, "
          f"{len(o.state)} records, scrubber skill "
          f"v{(o.get('skill:scrubber') or {}).get('version', '?')}")
    print("  endpoints: /api/watermark /api/journal /api/record "
          "/api/submit /api/compact")
    print("  Ctrl+C to stop (state persists).")
    try:
        server._thread.join()
    except KeyboardInterrupt:
        print("\n  stopping — compacting final pack...")
        server.orch.compact(engine_version="alpha-shutdown")
        server.stop()
        print("  stopped clean.")


if __name__ == "__main__":
    main()
