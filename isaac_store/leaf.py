"""LeafIsaac — the security-net worker (owner design, 2026-07-11).

"The older version of Isaac, all in one, integrated, for local
information": a full local Isaac at the leaf of the tier ladder
(Prime -> client overlay -> leaf). User-submitted information is
processed, learned from, and answered from HERE — and only here.

The quarantine is structural, not filtered:
- Reads LAYER one-way, local wins: the leaf pulls shared nodes from
  the client overlay, then Prime (via LiveCache, 30-min recheck), and
  GRAFTS them into its local net, tagging grafted doors with their
  origin tier. Private evidence then doors onto them locally.
- Writes go nowhere: this class holds NO orchestrator, NO submit
  channel. There is no code path from a leaf to any upstream queue.
- Two modes (owner spec): "ephemeral" — the mind lives in RAM only
  and save() REFUSES; "user-held" — packs persist only under the
  user's own directory. (Encryption-at-rest for user-held packs needs
  a vetted crypto library — never hand-rolled — and is an open item
  awaiting the owner's call on the dependency.)
"""
import os

from .cache import LiveCache
from . import bridge


class LeafIsaac:
    def __init__(self, prime_dir, client_dir=None, mode="ephemeral",
                 user_dir=None, isaac_module=None, clock=None):
        if mode not in ("ephemeral", "user-held"):
            raise ValueError(f"unknown mode {mode!r}")
        if mode == "user-held" and not user_dir:
            raise ValueError("user-held mode needs the USER'S directory")
        self.mode = mode
        self.user_dir = user_dir
        self.mod = isaac_module or bridge.load_isaac_module()

        kw = {"clock": clock} if clock else {}
        self.prime = LiveCache(os.path.join(prime_dir, "packs"),
                               os.path.join(prime_dir, "journal.jsonl"), **kw)
        self.client = (LiveCache(os.path.join(client_dir, "packs"),
                                 os.path.join(client_dir, "journal.jsonl"), **kw)
                       if client_dir else None)

        # resume a user-held mind if one exists; otherwise fresh
        self.mind = None
        if mode == "user-held":
            from .pack import latest_pack
            if latest_pack(os.path.join(user_dir, "packs"))[1]:
                self.mind = self.mod.Isaac.load_pack(os.path.join(user_dir, "packs"))
        if self.mind is None:
            self.mind = self.mod.Isaac()

    # ---- layered reads: local -> client -> Prime -------------------
    def _local_has(self, node):
        net = self.mind.net
        return node in net.doors or node in net.meta

    def pull(self, node):
        """Resolve a node with local-wins layering. If a shared tier
        has it, graft it into the local net (tagged with its origin)
        so private evidence can door onto it. Returns the tier that
        answered: 'local' | 'client' | 'prime' | None."""
        if self._local_has(node):
            return "local"
        for tier_name, tier in (("client", self.client), ("prime", self.prime)):
            if tier is None:
                continue
            rec = tier.get(f"node:{node}")
            if rec is not None:
                self._graft(node, rec, tier_name)
                return tier_name
        return None

    def _graft(self, node, rec, origin):
        net = self.mind.net
        for tgt in rec.get("doors", ()):
            net.doors[node].add(tgt)
            net.preds[tgt].add(node)
            net.door_tags[(node, tgt)].add(origin)  # provenance kept
        for tgt, tags in rec.get("tags", {}).items():
            net.door_tags[(node, tgt)] |= set(tags)
        for tgt, c in rec.get("counts", {}).items():
            net.door_counts[(node, tgt)] += c
        if "meta" in rec:
            merged = dict(rec["meta"])
            merged.update(net.meta.get(node, {}))  # local values WIN
            net.meta[node] = merged

    # ---- the local all-in-one Isaac does the rest ------------------
    # (teach/observe/discover/lookup run on self.mind directly; every
    #  write lands in the local net and nowhere else)

    def save(self):
        if self.mode != "user-held":
            raise RuntimeError(
                "ephemeral security net: nothing is EVER written to disk")
        return self.mind.save_pack(os.path.join(self.user_dir, "packs"))

    def close(self):
        self.prime.close()
        if self.client:
            self.client.close()
