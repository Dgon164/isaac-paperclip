"""Seeker — the one-question search worker (owner design, 2026-07-12).

"It acts like a search agent... does a quick web crawl for a few
sources, chews on the information, then gives its best answer."

The no-curiosity law holds: a Seeker's entire lifetime is ONE task,
handed in from outside. It cannot loop or explode by construction:
- DEPTH ZERO: it fetches what the search returned, never a link
  found inside a page (no recursion exists anywhere in this file);
- budgets are physical (max sources / bytes per page / total bytes),
  exhaustion is a clean stop;
- it has no task queue and no way to add to one — seek() returns and
  the Seeker is done.

The chew (v1, honest scope): cross-source corroboration for numeric
questions — find numbers near the question's keywords, cluster them
(2% tolerance), count independent supporting sources. An answer
needs a majority AND >= 2 sources; anything less is a REFUSAL with
the dossier (what was found, where, how much they disagree).
Refusals are answers. Every claim carries receipts (url + content
hash) and PUBLIC-tier provenance — exportable through the
Provenance Gate.

The search provider is pluggable (a callable: question -> [urls]).
The real-web backend is an owner dependency decision; batteries use
a local mock web.
"""
import hashlib
import re
import time
import urllib.request

DEFAULT_BUDGET = dict(max_sources=4, max_bytes_per=200_000,
                      max_total_bytes=600_000, max_seconds=30)


class Seeker:
    def __init__(self, search, budget=None, fetch=None):
        self.search = search          # callable: question -> [urls]
        self.budget = dict(DEFAULT_BUDGET, **(budget or {}))
        self._fetch = fetch or self._http_fetch

    def _http_fetch(self, url, cap):
        req = urllib.request.Request(url, headers={"User-Agent": "isaac-seeker"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read(cap + 1)

    @staticmethod
    def _keywords(question):
        stop = {"what", "is", "the", "of", "on", "a", "an", "in", "to",
                "for", "how", "much", "many", "does", "do", "value"}
        return [w for w in re.findall(r"[a-z]+", question.lower())
                if w not in stop and len(w) > 2]

    @staticmethod
    def _numbers_near(text, keywords, window=120):
        """Numbers within `window` chars of any keyword hit."""
        text = text.lower()
        spots = [m.start() for kw in keywords
                 for m in re.finditer(re.escape(kw), text)]
        out = []
        for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)(?!\.?\d)", text):
            if any(abs(m.start() - s) <= window for s in spots):
                out.append(float(m.group(1)))
        return out

    def seek(self, question):
        """One task, one lifetime. Returns the answer record:
        {verdict, answer?, support, sources, dossier, budget_used}."""
        t0 = time.time()
        b = self.budget
        urls = list(self.search(question))[:b["max_sources"]]
        sources, total = [], 0
        for url in urls:
            if total >= b["max_total_bytes"] or \
                    time.time() - t0 > b["max_seconds"]:
                break  # budget exhausted: clean stop, no exception
            try:
                raw = self._fetch(url, b["max_bytes_per"])
            except Exception:
                continue  # a dead source is skipped, never retried forever
            raw = raw[:b["max_bytes_per"]]
            total += len(raw)
            text = re.sub(r"<[^>]+>", " ", raw.decode("utf-8", "replace"))
            sources.append(dict(url=url, text=text,
                                sha=hashlib.sha256(raw).hexdigest()[:16]))

        kws = self._keywords(question)
        votes = []  # (value, url, sha)
        for s in sources:
            for v in set(self._numbers_near(s["text"], kws)):
                votes.append((v, s["url"], s["sha"]))
        clusters = []  # [rep_value, [(url, sha), ...]]
        for v, url, sha in sorted(votes):
            for c in clusters:
                if abs(v - c[0]) <= 0.02 * max(abs(c[0]), 1e-9):
                    if url not in [u for u, _ in c[1]]:
                        c[1].append((url, sha))
                    break
            else:
                clusters.append([v, [(url, sha)]])
        clusters.sort(key=lambda c: -len(c[1]))

        used = dict(sources=len(sources), bytes=total,
                    seconds=round(time.time() - t0, 2))
        receipts = [dict(url=s["url"], sha=s["sha"]) for s in sources]
        dossier = [dict(value=c[0], support=len(c[1]),
                        sources=[u for u, _ in c[1]]) for c in clusters[:4]]
        base = dict(question=question, sources=receipts, dossier=dossier,
                    provenance=["public"], budget_used=used)
        if not clusters:
            return dict(base, verdict="NONE",
                        why="no candidate values found near the question's "
                            "terms in the fetched sources")
        best = clusters[0]
        others = sum(len(c[1]) for c in clusters[1:])
        if len(best[1]) < 2 or len(best[1]) <= others:
            return dict(base, verdict="AMBIGUOUS",
                        why=f"sources disagree: best value {best[0]:g} has "
                            f"{len(best[1])} source(s) vs {others} dissenting")
        return dict(base, verdict="ANSWER", answer=best[0],
                    support=len(best[1]),
                    why=f"{len(best[1])} independent sources agree "
                        f"within 2%")
