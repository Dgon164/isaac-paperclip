# -*- coding: utf-8 -*-
"""Faithful Python port of the owner's Foundry generator (foundry.jsx).
Same mulberry32-family RNG, same consumption order, so the same seed
forges the same world. Verified by byte-matching truth_dag.csv."""
import numpy as np


def _imul(a, b):
    return ((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF)) & 0xFFFFFFFF


def rng(seed):
    a = seed & 0xFFFFFFFF

    def r():
        nonlocal a
        a = (a + 0x6d2b79f5) & 0xFFFFFFFF
        t = _imul(a ^ (a >> 15), (1 | a) & 0xFFFFFFFF)
        t = ((t + _imul(t ^ (t >> 7), (61 | t) & 0xFFFFFFFF)) ^ t) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return r


def build_world(n_atoms, layer_sizes, span_lo, span_hi, rand):
    layers = [list(range(n_atoms))]
    for L in range(1, len(layer_sizes) + 1):
        size = layer_sizes[L - 1]
        groups = []
        for _ in range(size):
            span = span_lo + int(rand() * (span_hi - span_lo + 1))
            members, seen = [], set()
            while len(members) < span:
                r = rand()
                if r < 0.6 or L == 1:
                    ml = L - 1
                elif r < 0.85 and L >= 2:
                    ml = L - 2
                else:
                    ml = int(rand() * L)
                mi = int(rand() * (n_atoms if ml == 0
                                   else layer_sizes[ml - 1]))
                key = (ml, mi)
                if key not in seen:
                    seen.add(key)
                    members.append((ml, mi))
            groups.append(members)
        layers.append(groups)
    # flattened extents
    extent = [[None] * (n_atoms if L == 0 else len(layers[L]))
              for L in range(len(layers))]

    def flat(L, i):
        if L == 0:
            return [i]
        if extent[L][i] is not None:
            return extent[L][i]
        s = set()
        for ml, mi in layers[L][i]:
            s.update(flat(ml, mi))
        extent[L][i] = sorted(s)
        return extent[L][i]

    for L in range(1, len(layers)):
        for i in range(len(layers[L])):
            flat(L, i)
    return dict(layers=layers, extent=extent)


def sample_view(world, detect, rand):
    layers = world["layers"]
    top = len(layers) - 1
    out = []

    def expand(L, i):
        if L == 0:
            out.append(i)
            return
        for ml, mi in layers[L][i]:
            if rand() < detect:
                expand(ml, mi)

    draws = 2 if rand() < 0.3 else 1
    for _ in range(draws):
        expand(top, int(rand() * len(layers[top])))
    return sorted(set(out))


def truth_dag_lines(world):
    lines = ["layer,group_id,member_layer,member_index"]
    layers = world["layers"]
    for L in range(1, len(layers)):
        for gi, members in enumerate(layers[L]):
            for ml, mi in members:
                lines.append(f"{L},{gi},{ml},{mi}")
    return lines


def forge(seed=1, atoms=500, layer_sizes=(60, 146, 292, 791),
          span_lo=3, span_hi=6, detect=0.55, views_n=188602):
    rand = rng(seed * 2654435761 + 13)
    world = build_world(atoms, list(layer_sizes), span_lo, span_hi, rand)
    views = []
    for _ in range(views_n):
        v = sample_view(world, detect, rand)
        if v:
            views.append(v)
    return world, views
