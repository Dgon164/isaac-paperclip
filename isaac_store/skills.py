"""Skills — the worker model (owner design, 2026-07-12).

"Roles are loadouts, not species": every worker IS Prime with a
checkbox of skills loaded. A skill is a named record in Prime's net
(`skill:<name>`) holding learned things + preloaded structures; a
worker pulls it through the SAME path as any node (LiveCache /
PrimeServer /api/record) and processes with it directly. There is
deliberately almost no machinery here — a skill is just a record,
which is the point.

Educating Prime = publishing a new version of the skill record
(supersession through the normal queue). Workers pick it up at their
recheck; a pinned job keeps its loadout to the job boundary.
"""
SKILL_PREFIX = "skill:"


def publish_skill(orchestrator, name, record, who="education"):
    """Publish (or supersede) a skill in Prime through the normal
    queue — a skill update faces admission like any other edit."""
    orchestrator.submit({"op": "put", "key": f"{SKILL_PREFIX}{name}",
                         "value": record, "who": who})
    admitted, rejected = orchestrator.process()
    return admitted == 1 and rejected == 0


def pull_skill(cache, name):
    """Load a skill from Prime via a worker's LiveCache. Returns the
    record or None. Same caching, same 30-min recheck, same job
    pinning as every other record — skills ARE records."""
    return cache.get(f"{SKILL_PREFIX}{name}")
