"""Scale measurement — how big is a big mind on disk, and what does
partial loading buy? Synthetic nets at 10k and 100k nodes (~5 doors
each, counts + tags + meta measurements on 10%), measured against
pickle. Complete numbers, no dressing.
Run: python scale_test.py   (from isaac_store/)
"""
import os
import pickle
import random
import shutil
import sys
import tempfile
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import bridge
from isaac_store.pack import PackReader, write_pack


def build_mind(mod, n_nodes, seed=11):
    rng = random.Random(seed)
    i = mod.Isaac()
    net = i.net
    for k in range(n_nodes):
        src = f"n{k}"
        for _ in range(5):
            tgt = f"n{rng.randrange(n_nodes)}"
            net.doors[src].add(tgt)
            net.preds[tgt].add(src)
            net.door_tags[(src, tgt)].add("seq")
            net.door_counts[(src, tgt)] += rng.randrange(1, 40)
        if k % 10 == 0:  # kept measurements on 10% of nodes
            net.meta[src] = {"spread": rng.random(), "null_bar": rng.random(),
                             "n_obs": rng.randrange(5, 500)}
    return i


def measure(mod, n_nodes, tmp):
    i = build_mind(mod, n_nodes)
    label = f"{n_nodes:,} nodes / ~{5 * n_nodes:,} doors"
    print(f"\n  ── {label} ──")

    pkl = os.path.join(tmp, f"m{n_nodes}.isaac")
    t0 = time.perf_counter(); i.save(pkl); t_ps = time.perf_counter() - t0
    t0 = time.perf_counter(); mod.Isaac.load(pkl); t_pl = time.perf_counter() - t0
    print(f"  pickle: {os.path.getsize(pkl) / 1e6:8.1f} MB   save {t_ps:6.2f}s   full load {t_pl:6.2f}s")

    d = os.path.join(tmp, f"packs{n_nodes}")
    t0 = time.perf_counter(); p = i.save_pack(d); t_ks = time.perf_counter() - t0
    t0 = time.perf_counter(); mod.Isaac.load_pack(d); t_kl = time.perf_counter() - t0
    print(f"  pack  : {os.path.getsize(p) / 1e6:8.1f} MB   save {t_ks:6.2f}s   full load {t_kl:6.2f}s")

    t0 = time.perf_counter()
    r = PackReader(p)
    t_idx = time.perf_counter() - t0
    t0 = time.perf_counter()
    for name in ("node:n7", f"node:n{n_nodes // 2}", f"node:n{n_nodes - 1}"):
        r.get(name)
    t_get = (time.perf_counter() - t0) / 3
    r.close()
    print(f"  partial: index open {t_idx * 1000:7.1f} ms; one node {t_get * 1000:7.3f} ms "
          f"(vs full load {t_kl:.2f}s = {t_kl / max(t_get, 1e-9):,.0f}x)")


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_scale_")
    try:
        print("  loading engine...")
        mod = bridge.load_isaac_module()
        for n in (10_000, 100_000):
            measure(mod, n, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
