"""composer.py — THE CODE COMPOSER (the code genesis, rung 1;
owner 2026-07-19: "lets try to get it going").

The growing-grammar boundary, pointed at code: hand-built stays
the COMBINATOR GENERATORS + the epistemics; what Isaac owns is
WHICH compositions exist, survive, and are offered. The knowledge
(idioms) comes TOLD from the lesson readme with its citation; the
composition search is his; the verdict is the grader's — no model
authors anything here.

Organs:
  read_lesson(readme)      -> idioms (fenced code, cited) +
                              assignment goals (numbered lines) +
                              named artifacts (`function()` names)
  eat_lesson(mind, ...)    -> idioms + goals land in the NET
                              (container-stamped, who = lesson)
  compose(goal, idioms, minted) -> candidate python artifacts,
                              each wearing its composition receipt
                              (which idioms, which combinators)
  mint(mind, ...)          -> a court-passed composition joins the
                              net (codeshape:<name>) and is
                              OFFERED FIRST on later lessons
The declared combinators (v1, named): DEF-WRAP, SLOT-UNIFY,
SEQUENCE, RETURN-INSERT, CALL-IN-MAIN, PRINT-LITERAL. Anything a
lesson needs beyond these is a DARK receipt, never a guess.
"""
import ast
import re

_FENCE = re.compile(r"```(?:py|python)\n(.*?)```", re.S)
_ASSIGN_HDR = re.compile(r"^#+\s*assignment", re.I | re.M)
_FUNCNAME = re.compile(r"`(\w+)\(\)`")
_ARGHINT = re.compile(r"takes? (?:an? )?(\w+)(?: string| path| int| number)? as (?:its )?(?:input|argument)", re.I)


def read_lesson(readme):
    """The lesson, read: taught idioms (cited code), the
    assignment's numbered goals, the named artifacts."""
    idioms = [m.strip() for m in _FENCE.findall(readme)]
    m = _ASSIGN_HDR.search(readme)
    assignment = readme[m.start():] if m else ""
    goals = [ln.strip(" -[]x.") for ln in assignment.split("\n")
             if re.match(r"^\s*(\d+\.|- \[)", ln)]
    funcs = list(dict.fromkeys(_FUNCNAME.findall(assignment)))
    arg = None
    am = _ARGHINT.search(assignment)
    if am:
        arg = am.group(1).lower()
    literals = re.findall(r'"([^"\n]{2,60})"', assignment)
    return dict(idioms=idioms, goals=goals, funcs=funcs, arg=arg,
                literals=literals, assignment=assignment)


def eat_lesson(mind, lesson_title, url, container, readme):
    """The idiom meal: taught content, container-stamped, cited.
    Returns what was read (the caller composes from it)."""
    got = read_lesson(readme)
    for i, code in enumerate(got["idioms"]):
        node = f"idiom:{container}:{lesson_title[:24]}:{i}"
        mind.net.set_meta(node, "code", code)
        mind.net.set_meta(node, "who",
                          f"{lesson_title} ({url})")
        mind.net.set_meta(node, "container", container)
        mind.net.add_door(f"world:{container}", node,
                          tag=f"in:{container}")
    for g in got["goals"]:
        mind.teach(f"goal:{lesson_title[:24]}", "asks", g[:80],
                   container=container)
    mind.record_finding("idiom_meal", lesson_title,
                        idioms=len(got["idioms"]),
                        goals=len(got["goals"]))
    return got


def _free_vars(code):
    """Names READ but never ASSIGNED (and not builtins) — the true
    placeholders an idiom leaves open."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()
    load, store = set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Name):
            (load if isinstance(n.ctx, ast.Load) else store).add(n.id)
    import builtins
    return {v for v in load - store if not hasattr(builtins, v)}


def _slot_unify(code, old, new):
    """SLOT-UNIFY: rename one free name across an idiom, by AST
    identity (never blind text replace)."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code

    class R(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == old:
                node.id = new
            return node
    return ast.unparse(R().visit(tree))


def compose_function(name, arg, idioms, minted=None):
    """DEF-WRAP + SLOT-UNIFY + SEQUENCE + RETURN-INSERT: build
    `def <name>(<arg>):` whose body is composed from taught
    idioms. Returns candidates, each with its receipt. The search
    is deliberately small and ENUMERATED — no guessing beyond the
    declared combinators."""
    cands = []
    pool = list(minted or []) + list(idioms)
    for i, a in enumerate(pool):
        for j, b in enumerate(pool):
            if i == j:
                continue
            body = a
            # nest b inside a's with-block if a ends with a colon
            # block opener; else SEQUENCE
            a_lines = a.rstrip().split("\n")
            if any(ln.rstrip().endswith(":") for ln in a_lines):
                inner = "\n".join("    " + ln for ln in
                                  b.strip().split("\n")
                                  if not ln.strip().startswith("#"))
                body_lines = []
                for ln in a_lines:
                    if ln.strip().startswith("#"):
                        continue
                    body_lines.append(ln)
                    if ln.rstrip().endswith(":"):
                        body_lines.append(inner)
                body = "\n".join(body_lines)
            else:
                body = a + "\n" + b
            # RETURN-INSERT: the last assigned name becomes the
            # return value
            try:
                tree = ast.parse(body)
            except SyntaxError:
                continue
            last_assigned = None
            for n in ast.walk(tree):
                if isinstance(n, ast.Assign) and \
                        isinstance(n.targets[0], ast.Name):
                    last_assigned = n.targets[0].id
            if last_assigned:
                body = body + f"\nreturn {last_assigned}"
            # SLOT-UNIFY: FREE names (read, never assigned) are
            # the idiom's true placeholders — they unify onto the
            # argument; locals are never touched
            if arg:
                for v in sorted(_free_vars(body)):
                    if v != arg:
                        body = _slot_unify(body, v, arg)
            src = f"def {name}({arg or ''}):\n" + "\n".join(
                "    " + ln for ln in body.split("\n") if ln.strip())
            try:
                ast.parse(src)
            except SyntaxError:
                continue
            cands.append(dict(
                code=src,
                receipt=f"DEF-WRAP({name}) + "
                        f"{'NEST' if i != j else 'SEQ'}"
                        f"[idiom {i} + idiom {j}] + RETURN-INSERT"
                        + (f" + SLOT-UNIFY->{arg}" if arg else "")))
    # single-idiom candidates too
    for i, a in enumerate(pool):
        body = a
        try:
            tree = ast.parse(body)
        except SyntaxError:
            continue
        last = None
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign) and \
                    isinstance(n.targets[0], ast.Name):
                last = n.targets[0].id
        if last:
            body += f"\nreturn {last}"
        if arg:
            for v in sorted(_free_vars(body)):
                if v != arg:
                    body = _slot_unify(body, v, arg)
        src = f"def {name}({arg or ''}):\n" + "\n".join(
            "    " + ln for ln in body.split("\n")
            if ln.strip() and not ln.strip().startswith("#"))
        try:
            ast.parse(src)
        except SyntaxError:
            continue
        cands.append(dict(code=src,
                          receipt=f"DEF-WRAP({name}) + "
                                  f"[idiom {i}] + RETURN-INSERT"))
    # dedupe by code
    seen, out = set(), []
    for c in cands:
        if c["code"] not in seen:
            seen.add(c["code"])
            out.append(c)
    return out


def compose_print_main(literals):
    """PRINT-LITERAL: the assignment names its own demanded output
    in quotes — main prints exactly those lines, receipted as the
    literal road (told by the assignment, not invented)."""
    body = "\n".join(f"    print({ln!r})" for ln in literals) \
        or "    pass"
    return f"def main():\n{body}\n\nmain()\n"


def compose_main(func_name, arg_value=None, print_result=True):
    """CALL-IN-MAIN + PRINT-LITERAL: the runnable face."""
    call = f"{func_name}({arg_value!r})" if arg_value is not None \
        else f"{func_name}()"
    body = f"print({call})" if print_result else call
    return (f"def main():\n    {body}\n\n"
            f"main()\n")


def mint(mind, name, code, receipt, container, court_receipt):
    """A court-passed composition joins his net — owned, cited,
    offered first on later lessons."""
    node = f"codeshape:{name}"
    mind.net.set_meta(node, "code", code)
    mind.net.set_meta(node, "receipt", receipt)
    mind.net.set_meta(node, "court", court_receipt)
    mind.net.set_meta(node, "container", container)
    mind.net.add_door(f"world:{container}", node,
                      tag=f"in:{container}")
    mind.record_finding("codeshape", name, receipt=receipt,
                        court=court_receipt)
    return node


def minted_shapes(mind):
    return [mind.net.get_meta(n, "code")
            for n in list(mind.net.meta)
            if str(n).startswith("codeshape:")
            and mind.net.get_meta(n, "code")]


def minted_names(mind):
    return [str(n)[len("codeshape:"):] for n in list(mind.net.meta)
            if str(n).startswith("codeshape:")
            and mind.net.get_meta(n, "code")]


def record_attempt(mind, lesson, candidate_receipt, court):
    """THE BUG-DETECTION + ROLLBACK LEDGER (owner 2026-07-19: "a
    perfect learning opportunity for him to figure out bug
    detection, and rollbacks"). Each candidate is a HYPOTHESIS
    courted by the spec; a red result names the exact failing
    check (bug detection) and the artifact ROLLS BACK to
    last-green — wrong-kept with its diagnosis, never a silent
    clobber. Green attempts are kept; red ones are learning."""
    green = court.get("green", False)
    mind.record_finding(
        "code_attempt", lesson,
        candidate=candidate_receipt[:80],
        verdict="GREEN" if green else "ROLLED-BACK",
        bug=(None if green else court.get("why", "")),
        rolled_back=not green)
    return green
