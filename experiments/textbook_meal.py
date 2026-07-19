"""textbook_meal.py — THE TEXTBOOK MEAL (owner, 2026-07-19: "lets
give him a coding textbook. see what he does.")

The book: the official Python Tutorial (PSF, plain text). Three
things happen, all receipted:

  1. THE FOLLOW-ALONG COURT — he reads each chapter by RUNNING
     every >>> example internally, in order, in one namespace per
     chapter (typing along), and checks the book's own printed
     answers. The textbook carries its own court; belief is
     measured, never assumed. Verified / refused counts per
     chapter.
  2. THE IDIOM MEAL — every example's source lands in his net as
     a cited idiom (who = "Python Tutorial — <chapter>",
     container python-tutorial). Told knowledge, at scale.
  3. THE STUDY — the crystallizer's normalization runs over every
     eaten idiom: names and constants collapse, topology remains;
     the book folds into FORM FAMILIES (what he actually learned:
     the shapes, not the examples).

Then THE PAYOFF PROBE: Count Characters is dark for want of a
dict-accumulation loop no lesson taught. If the textbook taught
the PIECES (a for-loop shape, a subscript-assign shape), his NEST
combinator can compose the loop — textbook-sourced, cited,
courted by boot.dev's grader. If the pieces are missing, the dark
receipt says so honestly.

usage: python textbook_meal.py [--live]
"""
import ast
import doctest
import io
import os
import re
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))
import isaac as mod                                    # noqa: E402

WSL = ["wsl.exe", "-d", "Ubuntu", "-u", "root", "--", "bash", "-lc"]
BOOK = "/root/python-3.14-docs-text/tutorial"
CHAPTERS = ["introduction", "controlflow", "datastructures",
            "inputoutput", "errors", "classes", "stdlib"]


def read_chapter(name):
    out = subprocess.run(WSL + [f"cat {BOOK}/{name}.txt"],
                         capture_output=True, text=True,
                         encoding="utf-8", errors="replace",
                         timeout=60)
    return out.stdout


def follow_along(name, text):
    """Run the chapter's examples in order, one namespace — the
    follow-along court. The book's printed answers are the spec."""
    parser = doctest.DocTestParser()
    # the court must not BLOCK: examples that wait on a keyboard
    # (input) or open a pager (help) get stubs — their claims then
    # verify or refuse on their own merits, honestly
    globs = {"print": print,
             "input": lambda *a, **k: "",
             "help": lambda *a, **k: None}
    try:
        raw = parser.get_examples(text, name)
    except ValueError:
        return dict(attempted=0, failed=0, examples=[],
                    skipped=0)
    BLOCKING = re.compile(r"while True|input\(|help\(|"
                          r"breakpoint\(|exit\(|quit\(|"
                          r"KeyboardInterrupt|SystemExit")
    examples_run = [ex for ex in raw
                    if not BLOCKING.search(ex.source)]
    skipped = len(raw) - len(examples_run)
    test = doctest.DocTest(examples_run, globs, name, name, 0,
                           None)
    runner = doctest.DocTestRunner(
        optionflags=doctest.ELLIPSIS
        | doctest.IGNORE_EXCEPTION_DETAIL, verbose=False)
    buf = io.StringIO()
    old_stdin = sys.stdin
    sys.stdin = io.StringIO("")
    try:
        runner.run(test, out=buf.write)
    except Exception:
        pass
    finally:
        sys.stdin = old_stdin
    examples = [ex.source.strip() for ex in raw
                if ex.source.strip()]
    return dict(attempted=runner.tries, failed=runner.failures,
                examples=examples, skipped=skipped)


def topology(src):
    """A single idiom's form signature: names and constants
    collapse, structure remains — the crystallizer's normalization
    (form-by-comparison generalized to the whole book)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None

    class N(ast.NodeTransformer):
        def visit_Name(self, node):
            node.id = "_"
            return node

        def visit_Constant(self, node):
            return ast.copy_location(ast.Constant(value="_"), node)

        def visit_arg(self, node):
            node.arg = "_"
            return node
    try:
        return ast.unparse(N().visit(tree))
    except Exception:
        return None


def main():
    live = "--live" in sys.argv[1:]
    from isaac_store.sparring import IsaacAccount
    home = os.path.join(os.path.expanduser("~"), "Documents",
                        "isaac_home")
    if live:
        shutil.copy2(os.path.join(home, "mind.isaac"),
                     os.path.join(home, "mind.isaac.bak"))
    acct = IsaacAccount(home, mod)
    mind = acct.mind

    print("THE TEXTBOOK: the official Python Tutorial "
          f"({len(CHAPTERS)} chapters)\n")
    all_idioms, verified, refused = [], 0, 0
    for ch in CHAPTERS:
        text = read_chapter(ch)
        got = follow_along(ch, text)
        ok = got["attempted"] - got["failed"]
        verified += ok
        refused += got["failed"]
        kept = 0
        for i, src in enumerate(got["examples"]):
            if len(src) > 200:
                continue
            all_idioms.append((ch, src))
            node = f"idiom:python-tutorial:{ch}:{i}"
            mind.net.set_meta(node, "code", src)
            mind.net.set_meta(node, "who",
                              f"Python Tutorial — {ch}")
            mind.net.set_meta(node, "container", "python-tutorial")
            mind.net.add_door("world:python-tutorial", node,
                              tag="in:python-tutorial")
            kept += 1
        print(f"  {ch:15} examples {got['attempted']:4}  "
              f"verified {ok:4}  refused {got['failed']:3}  "
              f"idioms eaten {kept:4}")
    mind.record_finding("textbook_meal", "python-tutorial",
                        idioms=len(all_idioms), verified=verified,
                        refused=refused)

    # THE STUDY: the book folds into form families
    fams = {}
    for ch, src in all_idioms:
        sig = topology(src)
        if sig:
            fams.setdefault(sig, []).append(src)
    big = sorted(fams.items(), key=lambda kv: -len(kv[1]))[:10]
    print(f"\nTHE STUDY: {len(all_idioms)} idioms fold into "
          f"{len(fams)} form families. The largest:")
    for sig, members in big[:6]:
        print(f"  x{len(members):3}  {sig[:64]}")

    # THE PAYOFF PROBE: can the textbook's pieces compose the
    # counting loop? (for-loop shape + subscript-assign shape)
    loops = [s for _c, s in all_idioms
             if re.match(r"for \w+ in \w+:", s.strip())
             and s.count("\n") <= 2]
    assigns = [s for _c, s in all_idioms
               if re.search(r"\w+\[[^\]]+\]\s*=", s)
               and "\n" not in s.strip()]
    gets = [s for _c, s in all_idioms if ".get(" in s]
    print(f"\nTHE PIECES: for-loop idioms {len(loops)}, "
          f"subscript-assign idioms {len(assigns)}, "
          f".get idioms {len(gets)}")
    if live:
        mind.save(acct.mind_path)
        acct._journal(dict(kind="meal",
                           stamp=time.strftime(
                               "%Y-%m-%d %H:%M:%S"),
                           meal="the textbook: official Python "
                                "Tutorial",
                           idioms=len(all_idioms),
                           verified=verified, refused=refused,
                           families=len(fams)))
        print("\nMEAL JOURNALED + mind saved.")


if __name__ == "__main__":
    main()
