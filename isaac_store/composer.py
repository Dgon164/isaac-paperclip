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
    # METHOD-FROM-HINT: methods the readme NAMES are told knowledge
    hints = list(dict.fromkeys(re.findall(r"\.(\w+)\(\)", readme)))
    # TEMPLATE-FILL: a plain fence holding {slot} is a TOLD output
    # template ("Replace {num_words} with the actual number")
    templates = [t.strip() for t in
                 re.findall(r"```\n([^`]*?\{\w+\}[^`]*?)```",
                            readme, re.S)]
    return dict(idioms=idioms, goals=goals, funcs=funcs, arg=arg,
                literals=literals, hints=hints,
                templates=templates, assignment=assignment)


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


BORN_BUILTINS = ("print", "len")   # the born code vocabulary,
#                                    declared and tiny — len is to
#                                    code what plus is to the vet's
#                                    number-words


def compose_transform(name, arg, hints, wants_number):
    """METHOD-FROM-HINT (+ BUILTIN-LEN when the goal says 'number
    of'): a transform function from the readme's OWN named
    methods. Every atom is told (the hint) or born-declared."""
    cands = []
    for h in hints[:3]:
        body = [f"parts = {arg}.{h}()"]
        rec = f"METHOD-FROM-HINT(.{h}())"
        if wants_number:
            body.append("n = len(parts)")
            rec += " + BUILTIN-LEN"
        body.append(f"return {'n' if wants_number else 'parts'}")
        src = f"def {name}({arg}):\n" + "\n".join(
            "    " + ln for ln in body)
        try:
            ast.parse(src)
            cands.append(dict(code=src,
                              receipt=f"DEF-WRAP({name}) + {rec}"))
        except SyntaxError:
            continue
    return cands


def compose_chain_main(steps, template=None, literals=()):
    """CALL-BIND chain + TEMPLATE-FILL: main as a dataflow — each
    minted/new function's result feeds the next; the readme's told
    template prints with its slot filled by the LAST computed
    value (never by the spec's answer — that would be the shallow
    road)."""
    lines, last = [], None
    for i, (fn, argv) in enumerate(steps):
        var = f"v{i}"
        call_arg = last if last is not None else (
            repr(argv) if argv is not None else "")
        lines.append(f"    {var} = {fn}({call_arg})")
        last = var
    if template is not None and last is not None:
        t = re.sub(r"\{\w+\}", "{" + last + "}", template)
        lines.append(f"    print(f{t!r})")
    else:
        for ln in literals[:3]:
            lines.append(f"    print({ln!r})")
    body = "\n".join(lines) or "    pass"
    return f"def main():\n{body}\n\nmain()\n"


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
    # THE VARIABLE AND THE VALUE: every instance abstracts to its
    # FORM (topology) + DIMENSIONS; same skeleton = one family,
    # many coexisting instances — the lawform ontology at code
    try:
        form = abstract_form(code)
        import zlib
        fid = (f"codeform:"
               f"{zlib.crc32(form['skeleton'].encode()):08x}")
        held = mind.net.get_meta(fid, "skeleton")
        mind.net.set_meta(fid, "skeleton", form["skeleton"])
        mind.net.add_door(fid, node, tag="instance")
        mind.net.set_meta(node, "form", fid)
        mind.net.set_meta(node, "dims", form["dims"])
        if held:
            mind.record_finding("codeform_variant", name,
                                family=fid)
    except (SyntaxError, StopIteration):
        pass
    mind.record_finding("codeshape", name, receipt=receipt,
                        court=court_receipt)
    return node


def abstract_form(code):
    """THE VARIABLE AND THE VALUE (owner 2026-07-19: "he has a
    pattern, a topology, and he needs to set the dimensions").
    A passed composition abstracts into its FORM — the skeleton
    (topology) with named dimension slots — plus THIS instance's
    dimension values. One form, many possible instances; each is
    one thing at a time; many coexist. The same ontology as
    lawforms and their variants."""
    tree = ast.parse(code)
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef))
    dims = dict(name=fn.name,
                arg=(fn.args.args[0].arg if fn.args.args
                     else None),
                methods=[], constants=[])

    class Abs(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.name = "__NAME__"
            self.generic_visit(node)
            return node

        def visit_arg(self, node):
            if node.arg == dims["arg"]:
                node.arg = "__ARG__"
            return node

        def visit_Name(self, node):
            if node.id == dims["arg"]:
                node.id = "__ARG__"
            return node

        def visit_Call(self, node):
            self.generic_visit(node)
            if isinstance(node.func, ast.Attribute) \
                    and node.func.attr not in dims["methods"]:
                dims["methods"].append(node.func.attr)
            if isinstance(node.func, ast.Attribute):
                node.func.attr = (
                    f"__M{dims['methods'].index(node.func.attr)}__"
                    if not node.func.attr.startswith("__M")
                    else node.func.attr)
            return node

        def visit_Constant(self, node):
            if isinstance(node.value, (str, int, float)) \
                    and not isinstance(node.value, bool):
                dims["constants"].append(node.value)
                return ast.copy_location(ast.Constant(
                    value=f"__C{len(dims['constants']) - 1}__"),
                    node)
            return node
    skel = ast.unparse(Abs().visit(ast.parse(code)))
    return dict(skeleton=skel, dims=dims)


def instantiate(skeleton, dims):
    """INSTANTIATE-FORM: the held topology with NEW dimensions set
    — shape the shape. Validity is courted (parse), fitness is the
    grader's business."""
    src = skeleton.replace("__NAME__", dims.get("name", "f"))
    if dims.get("arg"):
        src = src.replace("__ARG__", dims["arg"])
    for i, m in enumerate(dims.get("methods", [])):
        src = src.replace(f"__M{i}__", m)
    for i, c in enumerate(dims.get("constants", [])):
        src = src.replace(f"'__C{i}__'", repr(c))
        src = src.replace(f'"__C{i}__"', repr(c))
    try:
        ast.parse(src)
    except SyntaxError:
        return None
    return src


def minted_shapes(mind):
    return [mind.net.get_meta(n, "code")
            for n in list(mind.net.meta)
            if str(n).startswith("codeshape:")
            and mind.net.get_meta(n, "code")]


def minted_names(mind):
    return [str(n)[len("codeshape:"):] for n in list(mind.net.meta)
            if str(n).startswith("codeshape:")
            and mind.net.get_meta(n, "code")]


TOOLSET = ("DEF-WRAP", "SLOT-UNIFY", "SEQUENCE", "RETURN-INSERT",
           "CALL-IN-MAIN", "PRINT-LITERAL", "METHOD-FROM-HINT",
           "BUILTIN-LEN", "TEMPLATE-FILL", "CALL-BIND",
           "MODULE-SPLIT")


def ledger_set(mind, uuid, title, status, road="", bug="",
               artifact_hash=""):
    """THE STUDY LEDGER (owner 2026-07-19: "a section that can
    tell what has been tracked and checked. he seems to start from
    the beginning every time"). One node per lesson in HIS net:
    status, the road that won (or the bug that stands), the
    artifact hash, and the TOOLSET at attempt time — so a DARK is
    retried only when the tools have actually grown."""
    node = f"lesson:{uuid}"
    mind.net.set_meta(node, "title", title)
    mind.net.set_meta(node, "status", status)
    mind.net.set_meta(node, "road", road)
    mind.net.set_meta(node, "bug", bug)
    mind.net.set_meta(node, "artifact", artifact_hash)
    mind.net.set_meta(node, "toolset", list(TOOLSET))
    mind.net.add_door("world:study", node, tag="in:study")


def ledger_get(mind, uuid):
    node = f"lesson:{uuid}"
    st = mind.net.get_meta(node, "status")
    if st is None:
        return None
    return dict(status=st,
                title=mind.net.get_meta(node, "title"),
                road=mind.net.get_meta(node, "road"),
                bug=mind.net.get_meta(node, "bug"),
                artifact=mind.net.get_meta(node, "artifact"),
                toolset=mind.net.get_meta(node, "toolset") or [])


def ledger_report(mind):
    """What has been tracked and checked — said plainly."""
    L = []
    for n in sorted(list(mind.net.meta)):
        if not str(n).startswith("lesson:"):
            continue
        st = mind.net.get_meta(n, "status")
        t = mind.net.get_meta(n, "title")
        road = mind.net.get_meta(n, "road") or ""
        bug = mind.net.get_meta(n, "bug") or ""
        L.append(f"  [{st:6}] {t}"
                 + (f" — via {road[:44]}" if road else "")
                 + (f" — standing bug: {bug[:40]}" if bug else ""))
    return "\n".join(L) if L else "  (nothing tracked yet)"


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
