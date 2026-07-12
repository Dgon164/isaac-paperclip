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

    # ---- the Provenance Gate (owner, 2026-07-12) --------------------
    # "if its something that can be reconstructed exclusively from
    #  isaac source nodes, its game. if it requires any user nodes it
    #  should be banned" — shareability is ANCESTRY, not appearance.
    EXPORT_OK = {"prime", "public"}

    def tiers_of(self, node):
        """Source tiers of a node. FAIL-CLOSED: unknown = user."""
        t = self.mind.net.meta.get(node, {}).get("tiers")
        return set(t) if t else {"user"}

    def _set_tiers(self, node, tiers):
        self.mind.net.meta[node]["tiers"] = sorted(set(tiers))

    def leaf_discover(self, X, y, name, data_tiers=("user",)):
        """Discover with declared data provenance (default user —
        fail-closed). The law inherits the UNION of its data tiers."""
        self.mind.discover(X, y, name=name)
        self._set_tiers(f"law:{name}", data_tiers)
        return self.mind.findings[-1]

    def leaf_tell(self, name, equation, d=None, tiers=("user",)):
        """tell_law with declared provenance (default user)."""
        r = self.mind.tell_law(name, equation, d=d)
        if r.get("status") in ("TOLD-UNVERIFIED", "VARIANT"):
            self._set_tiers(f"law:{name}", tiers)
        return r

    def exportable(self, node):
        """The gate: closure within {prime, public} -> game; any user
        tier -> banned FROM EXPORT (never from local use)."""
        t = self.tiers_of(node)
        bad = t - self.EXPORT_OK
        if bad:
            return False, (f"Provenance Gate: requires {sorted(bad)} "
                           f"nodes — banned from export"), t
        return True, f"reconstructable from {sorted(t)} sources alone", t

    def share_candidate(self, law_name):
        """First defense on the share path (BEFORE the scrubber):
        returns the record only if the gate passes; verdict filed
        locally either way."""
        node = f"law:{law_name}"
        ok, why, t = self.exportable(node)
        self.mind.record_finding("provenance_gate", law_name,
                                 verdict="GAME" if ok else "BANNED",
                                 why=why, tiers=sorted(t))
        if not ok:
            return {"ok": False, "why": why, "tiers": sorted(t)}
        return {"ok": True, "why": why,
                "record": {"meta": {"model":
                                    self.mind.net.get_meta(node, "model")},
                           "provenance": sorted(t)}}

    def recreation_check(self, law_name):
        """Owner: 'it should see if it can recreate the information
        from public sources too.' Attempt the rebuild from
        prime/client-held knowledge alone: a form+constants match
        means the user data was NOT necessary — provenance upgrades
        and export unlocks. No match: the ban stands."""
        node = f"law:{law_name}"
        m = self.mind.net.get_meta(node, "model")
        if m is None:
            return {"recreated": False, "why": "no such law"}
        sig = self.mind._form_signature(m)
        for tier_name, tier in (("prime", self.prime), ("client", self.client)):
            if tier is None or tier.reader is None:
                continue
            keys = list(tier.reader.index) + list(tier._overlay)
            for key in keys:
                rec = tier.get(key)
                model = None
                if isinstance(rec, dict):
                    model = (rec.get("meta") or {}).get("model") \
                        if isinstance(rec.get("meta"), dict) else None
                    if model is None:
                        model = rec.get("model")
                if not isinstance(model, dict) or "terms" not in model:
                    continue
                try:
                    same = (self.mind._form_signature(model) == sig
                            and self.mind._coefs_match(m, model))
                except Exception:
                    continue
                if same:
                    new_tiers = {"public"} if rec.get("public") else {tier_name}
                    self._set_tiers(node, new_tiers)
                    self.mind.record_finding(
                        "recreation_check", law_name, recreated=True,
                        source=key, tiers=sorted(new_tiers))
                    return {"recreated": True, "source": key,
                            "tiers": sorted(new_tiers)}
        self.mind.record_finding("recreation_check", law_name,
                                 recreated=False,
                                 why="no prime/public source rebuilds it")
        return {"recreated": False,
                "why": "no prime/public source rebuilds it — ban stands"}

    def save(self):
        if self.mode != "user-held":
            raise RuntimeError(
                "ephemeral security net: nothing is EVER written to disk")
        return self.mind.save_pack(os.path.join(self.user_dir, "packs"))

    def close(self):
        self.prime.close()
        if self.client:
            self.client.close()
