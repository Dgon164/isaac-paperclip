"""Bridge: a live Isaac instance <-> plain-data store records.

The Net is split into PER-NODE records ("node:<name>") so partial
loading works at node granularity; all other instance state becomes
"sys:<attr>" records. COMPLETE by construction: every attribute of
isaac.__dict__ and net.__dict__ is either explicitly mapped or
carried verbatim — nothing is silently dropped (keep-every-measurement
applies to the file format).

`preds` (the reverse index) is NOT stored: it is an index, not a
measurement, and the engine already rebuilds it on load.
"""
import importlib.util
import os
import sys
from collections import defaultdict

from .codec import register_module

# Both repos are self-contained (research=paperclip, live=dc): the
# engine normally sits at this package's parent. Resolution order:
# ISAAC_ENGINE env var > same-repo isaac.py > sibling isaac-paperclip.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOCAL_ENGINE = os.path.join(_REPO_ROOT, "isaac.py")
PAPERCLIP_ISAAC = os.environ.get("ISAAC_ENGINE") or (
    _LOCAL_ENGINE if os.path.exists(_LOCAL_ENGINE)
    else os.path.join(os.path.dirname(_REPO_ROOT), "isaac-paperclip", "isaac.py"))
_NET_MAPPED = ("doors", "door_tags", "meta", "door_counts", "preds")


def load_isaac_module(path=PAPERCLIP_ISAAC):
    spec = importlib.util.spec_from_file_location("isaac", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("isaac", mod)
    old_argv = sys.argv
    sys.argv = [path]  # engine self-test only runs under __main__; safe
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = old_argv
    register_module(mod)
    return mod


def extract(isaac_inst):
    """Isaac instance -> {record_name: plain value}."""
    net = isaac_inst.net
    nodes = set(net.doors) | set(net.meta)
    for src, tgts in net.doors.items():
        nodes |= set(tgts)
    for (src, tgt) in list(net.door_tags) + list(net.door_counts):
        nodes.add(src)
        nodes.add(tgt)

    # group tagged/counted edges by source once, then build records in
    # fully deterministic (sorted) order
    tags_by_src = {}
    for (src, tgt), v in net.door_tags.items():
        tags_by_src.setdefault(src, {})[tgt] = v
    counts_by_src = {}
    for (src, tgt), v in net.door_counts.items():
        counts_by_src.setdefault(src, {})[tgt] = v

    records = {}
    for n in sorted(nodes, key=repr):
        rec = {}
        if n in net.doors:
            rec["doors"] = sorted(net.doors[n], key=repr)
        if n in tags_by_src:
            rec["tags"] = {t: tags_by_src[n][t]
                           for t in sorted(tags_by_src[n], key=repr)}
        if n in counts_by_src:
            rec["counts"] = {t: counts_by_src[n][t]
                             for t in sorted(counts_by_src[n], key=repr)}
        if n in net.meta:
            rec["meta"] = net.meta[n]
        records[f"node:{n}"] = rec

    net_extras = {k: v for k, v in net.__dict__.items() if k not in _NET_MAPPED}
    if net_extras:
        records["sys:net_extras"] = net_extras

    for attr, value in isaac_inst.__dict__.items():
        if attr == "net":
            continue
        records[f"sys:{attr}"] = value
    return records


def rebuild(records, isaac_module):
    """{record_name: value} -> a live Isaac instance."""
    Isaac = isaac_module.Isaac
    Net = isaac_module.Net
    inst = Isaac.__new__(Isaac)
    net = Net.__new__(Net)
    net.doors = defaultdict(set)
    net.door_tags = defaultdict(set)
    net.meta = defaultdict(dict)
    net.door_counts = defaultdict(int)

    for name, rec in records.items():
        if name.startswith("node:"):
            n = name[len("node:"):]
            if "doors" in rec:
                net.doors[n]  # touch: an empty door set is still a fact
                for tgt in rec["doors"]:
                    net.doors[n].add(tgt)
            for tgt, tags in rec.get("tags", {}).items():
                net.door_tags[(n, tgt)] = tags
            for tgt, c in rec.get("counts", {}).items():
                net.door_counts[(n, tgt)] = c
            if "meta" in rec:
                net.meta[n] = rec["meta"]
        elif name == "sys:net_extras":
            for k, v in rec.items():
                setattr(net, k, v)
        elif name.startswith("sys:"):
            setattr(inst, name[len("sys:"):], rec)

    net.preds = defaultdict(set)  # index, rebuilt not stored
    for src, tgts in net.doors.items():
        for tgt in tgts:
            net.preds[tgt].add(src)
    inst.net = net
    return inst
