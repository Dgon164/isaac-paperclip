"""composer_battery.py — PROMOTION GATE for THE CODE COMPOSER
(the code genesis rung 1; owner 2026-07-19: "lets try to get it
going" — after the honest frontier measurement).

Pins the night's receipt permanently:
  CB1 read_lesson: fenced idioms, numbered goals, `f()` names,
      arg hints, quoted literals — all extracted exactly.
  CB2 free vars: read-never-assigned minus builtins (the idiom's
      TRUE placeholders; locals are never renamed).
  CB3 THE RECEIPT: the real Read-File idioms compose to the exact
      function their server graded green — combinators named.
  CB4 compose_main / compose_print_main exact.
  CB5 a broken idiom never crashes the search.
  CB6 mint -> codeshape survives save/load; minted_shapes offers
      it back.
  CB7 eat_lesson: idioms land cited + container-stamped; goals
      land as facts.

Run: cd experiments && PYTHONHASHSEED=0 python composer_battery.py
"""
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))
import isaac as isaac_mod                          # noqa: E402
from isaac_store.composer import (read_lesson,     # noqa: E402
                                  compose_function, compose_main,
                                  compose_print_main, mint,
                                  minted_shapes, eat_lesson,
                                  _free_vars)

Isaac = isaac_mod.Isaac

README = '''# Read File

## with Block

```py
with open(path_to_file) as f:
    # do something with f (the file) here
```

## .read() Method

```py
# f is a file object
file_contents = f.read()
```

## Assignment

1. [ ] Delete your "greetings boots" message.
2. [ ] Write a new function called `get_book_text()`. It takes a filepath string as input and returns the contents.
3. [ ] Write a `main()` function.
'''

WANT = ('def get_book_text(filepath):\n'
        '    with open(filepath) as f:\n'
        '        file_contents = f.read()\n'
        '    return file_contents')


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(bool(ok))
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    g = read_lesson(README)
    check("CB1 read_lesson — idioms/goals/funcs/arg/literals",
          len(g["idioms"]) == 2 and len(g["goals"]) == 3
          and g["funcs"][0] == "get_book_text"
          and g["arg"] == "filepath"
          and "greetings boots" in g["literals"],
          f"{len(g['idioms'])} idioms, funcs {g['funcs'][:1]}, "
          f"arg {g['arg']}")

    fv = _free_vars("with open(path_to_file) as f:\n"
                    "    file_contents = f.read()")
    check("CB2 free vars — placeholder found, local untouched, "
          "builtins excluded",
          fv == {"path_to_file"}, f"free = {sorted(fv)}")

    cands = compose_function("get_book_text", "filepath",
                             g["idioms"])
    hit = next((c for c in cands if c["code"] == WANT), None)
    check("CB3 THE RECEIPT — the server-graded function composed "
          "exactly, combinators named",
          hit is not None and "DEF-WRAP" in hit["receipt"]
          and "SLOT-UNIFY" in hit["receipt"],
          hit["receipt"][:64] if hit else f"{len(cands)} cands, "
          "NONE exact")

    m4 = compose_main("get_book_text", "books/frankenstein.txt")
    p4 = compose_print_main(["Hello", "World"])
    check("CB4 mains — call-in-main + print-literal exact",
          "print(get_book_text('books/frankenstein.txt'))" in m4
          and "print('Hello')" in p4 and "print('World')" in p4
          and p4.rstrip().endswith("main()"),
          m4.split(chr(10))[1].strip())

    bad = compose_function("f", "x", ["this is not ) python ("])
    check("CB5 broken idiom — skipped, never a crash",
          isinstance(bad, list), f"{len(bad)} candidates")

    with tempfile.TemporaryDirectory() as td:
        mm = Isaac()
        mint(mm, "get_book_text", WANT, "receipt-x", "bootdev",
             "court-y")
        p = os.path.join(td, "m.isaac")
        mm.save(p)
        back = Isaac.load(p)
        shapes = minted_shapes(back)
        check("CB6 mint — codeshape survives save/load, offered "
              "back", shapes == [WANT]
              and back.net.get_meta("codeshape:get_book_text",
                                    "court") == "court-y",
              f"{len(shapes)} shape(s) offered")

    m7 = Isaac()
    got7 = eat_lesson(m7, "Read File", "https://x", "bookbot",
                      README)
    node = "idiom:bookbot:Read File:0"
    check("CB7 the idiom meal — cited, stamped, goals as facts",
          len(got7["idioms"]) == 2
          and m7.net.get_meta(node, "who").startswith("Read File")
          and m7.net.get_meta(node, "container") == "bookbot"
          and list(m7.fact_index.get(("goal:Read File", "asks"),
                                     [])),
          f"who = {m7.net.get_meta(node, 'who')[:28]}")

    # CB8 — THE VARIABLE AND THE VALUE (owner 2026-07-19): the
    # instance abstracts to topology + dimensions; new dimensions
    # make a NEW coexisting thing; roundtrip is exact
    from isaac_store.composer import abstract_form, instantiate
    form = abstract_form(WANT)
    back = instantiate(form["skeleton"], form["dims"])
    v2 = instantiate(form["skeleton"],
                     dict(name="get_first_line", arg="path",
                          methods=["readline"], constants=[]))
    ns = {}
    exec(back, ns)          # noqa: S102
    exec(v2, ns)            # noqa: S102
    ok = (back == WANT
          and "__NAME__" in form["skeleton"]
          and form["dims"]["methods"] == ["read"]
          and "readline()" in v2
          and "get_book_text" in ns and "get_first_line" in ns)
    check("CB8 the variable and the value — roundtrip exact; new "
          "dimensions = a new coexisting thing", ok,
          f"dims {form['dims']['name']}/{form['dims']['methods']}"
          f" -> get_first_line/readline")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} "
          f"failed of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
