"""
ISAAC UI — one file, stdlib + numpy. The honest discovery engine, for people.

    python isaac_ui.py          then open  http://127.0.0.1:8674

Give it data -> it finds the law, plots the fit, tells you how sure it is, and
says what it can't explain. One-click real datasets; a live plot; honest verdicts
(including refusal). The developer console (teach / converse / findings / minds)
is tucked into a collapsible panel at the bottom.
"""
import collections
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo-local isaac.py (repo root)
from isaac import Isaac, tokenize

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RDATA = ROOT / "research" / "data"   # real datasets (co2, sunspots) live here
MINDS = DATA / "minds"
MINDS.mkdir(parents=True, exist_ok=True)
LEDGER = DATA / "findings.jsonl"

STATE = {"isaac": Isaac(), "name": "unsaved mind"}
STATE["isaac"].ledger_path = str(LEDGER)
LOCK = threading.Lock()


def parse_table(text, target):
    rows = [r for r in text.strip().splitlines() if r.strip()]
    sep = "," if "," in rows[0] else None
    head = [h.strip() for h in rows[0].split(sep)]
    data = [[c.strip() for c in r.split(sep)] for r in rows[1:]]
    cols = {h: [] for h in head}
    for r in data:
        for h, v in zip(head, r):
            cols[h].append(float(v))
    if target not in cols:
        target = head[-1]
    y = np.array(cols.pop(target))
    names = list(cols)
    X = np.column_stack([cols[h] for h in names])
    return X, y, names, target


# ---------------------------------------------------------------- presets
def _co2_rows():
    rows = []
    for ln in (RDATA / "co2_mlo.csv").read_text().splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        parts = ln.split(",")
        try:
            yr, mo, av = int(parts[0]), int(parts[1]), float(parts[3])
        except (ValueError, IndexError):
            continue  # the header row
        if av > 0:
            rows.append((yr, mo, av))
    return rows


def preset(name):
    if name == "kepler":
        return dict(
            table="a,T\n0.387,0.241\n0.723,0.615\n1.0,1.0\n1.524,1.881\n"
                  "5.203,11.86\n9.537,29.46\n19.19,84.01\n30.07,164.8",
            target="T", name="kepler",
            blurb="Planet orbits (NASA): distance from the Sun (a) vs. length of "
                  "its year (T). Isaac should recover Kepler's law, T = a^1.5.")
    if name == "co2_rise":
        by = collections.defaultdict(list)
        for yr, mo, av in _co2_rows():
            by[yr].append(av)
        yrs = sorted(y for y in by if len(by[y]) >= 6)
        lines = ["years_since_1959,co2_ppm"] + [
            f"{yr-1959},{sum(by[yr])/len(by[yr]):.2f}" for yr in yrs]
        return dict(table="\n".join(lines), target="co2_ppm", name="co2_rise",
                    blurb="Real Mauna Loa CO2 (NOAA), yearly average — messy, real "
                          "climate data. Isaac reads out the rise as a legible law.")
    if name == "co2_season":
        rows = _co2_rows()
        arr = np.array([a for _, _, a in rows]); mon = np.array([m for _, m, _ in rows])
        ma = np.convolve(arr, np.ones(12) / 12, mode="same")   # remove the trend
        anom = (arr - ma)[6:-6]; mon = mon[6:-6]               # drop moving-avg edge artifacts
        phase = 2 * np.pi * mon / 12.0                         # position within the year, radians
        idx = np.sort(np.random.default_rng(0).choice(len(phase), 150, replace=False))
        lines = ["yearly_phase,co2_swing_ppm"] + [f"{phase[i]:.3f},{anom[i]:.2f}" for i in idx]
        return dict(table="\n".join(lines), target="co2_swing_ppm", name="co2_season",
                    blurb="The SAME CO2 data, seasonal part only — the planet's yearly "
                          "'breath' (x = position within the year). Isaac finds the repeating cycle.")
    if name == "noise":
        r = np.random.default_rng(7)
        x = r.uniform(0, 10, 60); y = r.normal(0, 1, 60)
        lines = ["x,y"] + [f"{x[i]:.3f},{y[i]:.3f}" for i in range(len(x))]
        return dict(table="\n".join(lines), target="y", name="noise",
                    blurb="Pure random noise — there is NO law here. Watch Isaac "
                          "REFUSE to invent one (a black box never will).")
    return dict(error="unknown preset")


def _plot_payload(isaac, name, X, y, names, target):
    try:
        n = len(y)
        idx = np.arange(n)
        if n > 400:
            idx = np.random.default_rng(0).choice(n, 400, replace=False)
        if X.shape[1] == 1:
            xs = X[idx, 0]; ys = y[idx]
            o = np.argsort(xs)
            pts = [[float(xs[o][i]), float(ys[o][i])] for i in range(len(o))]
            grid = np.linspace(float(X[:, 0].min()), float(X[:, 0].max()), 80).reshape(-1, 1)
            yh = isaac.apply_law(name, grid)
            fit = ([[float(grid[i, 0]), float(yh[i])] for i in range(len(grid))]
                   if yh is not None and np.all(np.isfinite(yh)) else [])
            return {"mode": "xy", "xlabel": names[0], "ylabel": target, "pts": pts, "fit": fit}
        yh = isaac.apply_law(name, X[idx])
        if yh is not None and np.all(np.isfinite(yh)):
            pts = [[float(y[idx][i]), float(yh[i])] for i in range(len(idx))]
            return {"mode": "pred", "xlabel": "actual " + target, "ylabel": "predicted", "pts": pts}
    except Exception:
        pass
    return {"mode": "none"}


# ---------------------------------------------------------------- api
def api(handler, body):
    isaac = STATE["isaac"]
    p = handler.path.split("?")[0]
    if p == "/api/status":
        laws = sorted(n for n in isaac.net.get_doors("law", tag="law"))
        return dict(mind=STATE["name"], nodes=len(isaac.net.all_nodes()),
                    findings=len(isaac.findings),
                    laws=[{"name": n[4:], "eq": (isaac.net.get_meta(n, "equation") or "")[:90]}
                          for n in laws],
                    minds=[f.name for f in MINDS.glob("*.isaac")])
    if p == "/api/preset":
        return preset(body.get("name", ""))
    if p == "/api/teach":
        isaac.teach(body["subject"], body["relation"], body["object"])
        return dict(ok=f"taught: {body['subject']} {body['relation']} {body['object']}")
    if p == "/api/observe":
        isaac.observe(tokenize(body["text"]))
        return dict(ok=f"observed {len(tokenize(body['text']))} tokens")
    if p == "/api/ask":
        toks = tokenize(body["text"])
        if len(toks) >= 2 and toks[-1] == "?":
            objs = isaac.fact_index.get((toks[0], toks[1]), [])
            return dict(answer=", ".join(map(str, objs)) or "(no fact — honest shrug)")
        nxt, conf = isaac.lookup(toks)
        return dict(answer=f"{nxt} (conf {conf:.2f})" if nxt else "(shrug — not enough experience)")
    if p == "/api/discover":
        X, y, names, target = parse_table(body["table"], body.get("target", ""))
        name = body.get("name") or target
        res = isaac.discover(X[:20000], y[:20000], name=name)
        res["columns"] = names
        res["target"] = target
        res["name"] = name
        res["plot"] = _plot_payload(isaac, name, X[:20000], y[:20000], names, target)
        return res
    if p == "/api/apply":
        rows = [r for r in body["table"].strip().splitlines() if r.strip()]
        try:
            [float(c) for c in rows[0].split(",")]
            data = rows
        except ValueError:
            data = rows[1:]
        vals = np.array([[float(c) for c in r.split(",")] for r in data])
        pred = isaac.apply_law(body["name"], vals)
        if pred is None:
            return dict(error="no such law / wrong column count")
        return dict(predictions=[round(float(v), 4) for v in pred])
    if p == "/api/findings":
        return dict(findings=isaac.recall_findings(kind=body.get("kind") or None,
                                                   contains=body.get("q") or None, limit=30))
    if p == "/api/save":
        name = (body.get("name") or "mind").replace(" ", "_")
        isaac.save(str(MINDS / f"{name}.isaac"))
        STATE["name"] = name
        return dict(ok=f"saved as {name}.isaac")
    if p == "/api/load":
        STATE["isaac"] = Isaac.load(str(MINDS / body["name"]))
        STATE["isaac"].ledger_path = str(LEDGER)
        STATE["name"] = body["name"].replace(".isaac", "")
        return dict(ok=f"loaded {body['name']}")
    if p == "/api/new":
        STATE["isaac"] = Isaac()
        STATE["isaac"].ledger_path = str(LEDGER)
        STATE["name"] = "unsaved mind"
        return dict(ok="fresh mind")
    if p == "/api/fork":
        STATE["isaac"] = isaac.fork()
        STATE["name"] = STATE["name"] + "-fork"
        return dict(ok=f"forked -> {STATE['name']}")
    return dict(error="unknown endpoint")


HTML = r"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Isaac — the honest discovery engine</title><style>
:root{--bg:#0e1216;--panel:#161c23;--ink:#dbe2ea;--dim:#8592a0;--acc:#5fb3a1;
--good:#5fb3a1;--warn:#d4a25a;--bad:#d46a6a;--line:#232c36}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 system-ui,Segoe UI,sans-serif}
header{padding:16px 22px;border-bottom:1px solid var(--line)}
header b{color:var(--acc);font-size:20px;letter-spacing:.02em}
header .tag{color:var(--dim);font-size:14px;margin-top:2px}
.presets{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:12px 22px;
border-bottom:1px solid var(--line)}
.presets .lab{color:var(--dim);font-size:13px;margin-right:2px}
.chip{background:transparent;color:var(--acc);border:1px solid var(--acc);
border-radius:20px;padding:6px 14px;font-weight:600;cursor:pointer;font-size:13px}
.chip:hover{background:var(--acc);color:#08110e}
main{display:grid;grid-template-columns:1fr 1.25fr;gap:14px;padding:16px 22px;max-width:1180px}
@media(max-width:820px){main{grid-template-columns:1fr}}
section{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px}
h2{margin:0 0 8px;font-size:12px;letter-spacing:.14em;color:var(--dim);text-transform:uppercase}
textarea{width:100%;min-height:190px;background:#0b0f13;border:1px solid var(--line);
color:var(--ink);border-radius:8px;padding:9px;font:12.5px/1.5 ui-monospace,Consolas,monospace;resize:vertical}
input,select{width:100%;background:#0b0f13;border:1px solid var(--line);color:var(--ink);
border-radius:7px;padding:8px;margin:4px 0;font:13px ui-monospace,Consolas,monospace}
.row{display:flex;gap:8px}.row>*{flex:1}
button.go{background:var(--acc);color:#08110e;border:0;border-radius:8px;padding:10px 16px;
margin-top:8px;font-weight:700;cursor:pointer;font-size:14px;width:100%}
#blurb{color:var(--dim);font-size:13px;margin:8px 0 0;min-height:18px}
.badge{display:inline-block;padding:8px 14px;border-radius:8px;font-weight:800;font-size:15px;letter-spacing:.02em}
.badge.good{background:rgba(95,179,161,.16);color:var(--good);border:1px solid var(--good)}
.badge.warn{background:rgba(212,162,90,.14);color:var(--warn);border:1px solid var(--warn)}
.badge.bad{background:rgba(212,106,106,.14);color:var(--bad);border:1px solid var(--bad)}
.sub{color:var(--dim);font-size:13px;margin:6px 0 10px}
.eq{font:15px ui-monospace,Consolas,monospace;background:#0b0f13;border:1px solid var(--line);
border-radius:7px;padding:10px;margin:8px 0;color:var(--ink);word-break:break-word}
.meta{color:var(--dim);font:12px ui-monospace,monospace;margin-top:6px}
.probe{border-left:3px solid var(--warn);padding:6px 10px;margin:8px 0;font-size:13px;background:rgba(212,162,90,.06)}
.plot{margin-top:10px}
details{margin:14px 22px;max-width:1180px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px 14px}
summary{cursor:pointer;color:var(--dim);font-size:12px;letter-spacing:.12em;text-transform:uppercase}
.devgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:12px}
@media(max-width:820px){.devgrid{grid-template-columns:1fr}}
.dev input{font-size:12px}.dev button{background:transparent;color:var(--acc);border:1px solid var(--acc);
border-radius:6px;padding:6px 10px;margin:3px 3px 0 0;cursor:pointer;font-weight:600}
#log,#fout{font:12px/1.5 ui-monospace,Consolas,monospace;white-space:pre-wrap;background:#0b0f13;
border-radius:6px;padding:8px;max-height:150px;overflow:auto;border:1px solid var(--line);margin-top:6px}
.laws div{font:12px ui-monospace,monospace;padding:2px 0;border-bottom:1px dotted var(--line)}
small{color:var(--dim)}
</style></head><body>
<header><b>ISAAC</b> <span class="tag">the honest discovery engine — give it data, get a readable law, an honest verdict, and what it can't explain</span></header>
<div class="presets"><span class="lab">Try a real dataset:</span>
<button class="chip" onclick="loadPreset('kepler')">Kepler's law</button>
<button class="chip" onclick="loadPreset('co2_rise')">CO₂ rising (real)</button>
<button class="chip" onclick="loadPreset('co2_season')">CO₂ seasons (real)</button>
<button class="chip" onclick="loadPreset('noise')">Pure noise →&nbsp;refusal</button>
</div>
<main>
<section><h2>Your data</h2>
<textarea id="table" placeholder="Paste a table (CSV with a header row), or click a dataset above."></textarea>
<div class="row"><input id="target" placeholder="answer column (default: last)">
<input id="lawname" placeholder="name this law"></div>
<button class="go" onclick="discover()">▶ Find the law</button>
<p id="blurb"></p></section>
<section><h2>What Isaac found</h2><div id="verdict"><small>Pick a dataset above, or paste your own, then “Find the law”.</small></div></section>
</main>
<details><summary>Developer console — teach · converse · remember · minds</summary>
<div class="devgrid dev">
<div><h2>Converse</h2>
<div class="row"><input id="ts" placeholder="subject"><input id="tr" placeholder="relation"><input id="to" placeholder="object">
<button onclick="post('/api/teach',{subject:val('ts'),relation:val('tr'),object:val('to')})">teach</button></div>
<div class="row"><input id="obs" placeholder="observe a sentence…">
<button onclick="post('/api/observe',{text:val('obs')})">observe</button></div>
<div class="row"><input id="ask" placeholder="ask: 'the cat sat on the'">
<button onclick="ask()">ask</button></div><div id="log"></div></div>
<div><h2>Remember</h2>
<div class="row"><input id="q" placeholder="search findings…"><button onclick="findings()">search</button></div>
<div id="fout"></div>
<h2 style="margin-top:12px">Laws he holds</h2><div class="laws" id="laws"></div></div>
<div><h2>Minds</h2>
<div class="row"><input id="savename" placeholder="name this mind"><button onclick="post('/api/save',{name:val('savename')})">save</button></div>
<div class="row"><select id="minds"></select><button onclick="post('/api/load',{name:val('minds')})">load</button></div>
<button onclick="post('/api/new',{})">new mind</button>
<button onclick="post('/api/fork',{})">fork</button>
<p><small id="stat"></small> · <span id="mind"></span></p></div>
</div></details>
<script>
const val=id=>document.getElementById(id).value;
const put=(id,h)=>document.getElementById(id).innerHTML=h;
function logln(s){const l=document.getElementById('log');if(!l)return;l.textContent+=s+"\n";l.scrollTop=l.scrollHeight}
async function post(p,b){const r=await fetch(p,{method:'POST',body:JSON.stringify(b)});
const j=await r.json();if(j.ok)logln("· "+j.ok);if(j.error)logln("! "+j.error);status();return j}
async function ask(){const j=await post('/api/ask',{text:val('ask')});logln("you: "+val('ask'));logln("isaac: "+(j.answer||"?"))}
async function loadPreset(nm){const j=await post('/api/preset',{name:nm});if(j.error)return;
document.getElementById('table').value=j.table;document.getElementById('target').value=j.target;
document.getElementById('lawname').value=j.name;put('blurb',j.blurb||'');discover()}
const VMAP={
'UNDERSTOOD':{c:'good',t:'✓ Understood',s:"a clean law that holds — even a bit beyond the data it saw"},
'PARTIAL':{c:'warn',t:'~ Partial',s:"a usable pattern, but not fully proven"},
'CAPTURED':{c:'warn',t:'≈ Captured',s:"only a rough shape — real, but weak"},
'NO RULE':{c:'bad',t:'— No rule found',s:"I can't find a law here — and I won't fake one"}};
function drawPlot(pl){
if(!pl||pl.mode==='none')return '';
const W=440,H=250,m=40;let pts=pl.pts||[],fit=pl.fit||[];
if(!pts.length)return '';
const ax=pts.map(a=>a[0]).concat(fit.map(a=>a[0])),ay=pts.map(a=>a[1]).concat(fit.map(a=>a[1]));
let x0=Math.min(...ax),x1=Math.max(...ax),y0=Math.min(...ay),y1=Math.max(...ay);
if(pl.mode==='pred'){const lo=Math.min(x0,y0),hi=Math.max(x1,y1);x0=y0=lo;x1=y1=hi}
const sx=v=>m+(v-x0)/((x1-x0)||1)*(W-1.4*m),sy=v=>H-m-(v-y0)/((y1-y0)||1)*(H-1.5*m);
let s=`<svg class="plot" viewBox="0 0 ${W} ${H}" width="100%" style="max-width:${W}px">`;
s+=`<rect x=0 y=0 width=${W} height=${H} fill="#0b0f13" rx=8/>`;
s+=`<line x1=${m} y1=${H-m} x2=${W-8} y2=${H-m} stroke="#2b3540"/><line x1=${m} y1=8 x2=${m} y2=${H-m} stroke="#2b3540"/>`;
if(pl.mode==='pred'){s+=`<line x1=${sx(x0)} y1=${sy(y0)} x2=${sx(x1)} y2=${sy(y1)} stroke="#5fb3a1" stroke-dasharray="4 3" opacity=.6/>`}
if(fit.length){s+=`<polyline fill=none stroke="#5fb3a1" stroke-width=2 points="${fit.map(a=>sx(a[0]).toFixed(1)+','+sy(a[1]).toFixed(1)).join(' ')}"/>`}
pts.forEach(a=>s+=`<circle cx=${sx(a[0]).toFixed(1)} cy=${sy(a[1]).toFixed(1)} r=3 fill="#dbe2ea" opacity=.85/>`);
s+=`<text x=${W/2} y=${H-6} fill="#8592a0" font-size=11 text-anchor=middle>${pl.xlabel||''}</text>`;
s+=`<text x=12 y=${H/2} fill="#8592a0" font-size=11 text-anchor=middle transform="rotate(-90 12 ${H/2})">${pl.ylabel||''}</text>`;
return s+`</svg>`}
async function discover(){put('verdict','<small>thinking…</small>');
const j=await post('/api/discover',{table:val('table'),target:val('target'),name:val('lawname')});
if(j.error){put('verdict','<div class="badge bad">error</div><div class="meta">'+j.error+'</div>');return}
const v=VMAP[j.verdict]||{c:'warn',t:j.verdict,s:''};
let riv=(j.rivals||[]).map(r=>`<div class=probe><b>Not sure yet:</b> could also be <b>${r.rival}</b>. To decide, measure a point near ${'x'+r.probe.feature}=${r.probe.x}.</div>`).join('');
let html=`<span class="badge ${v.c}">${v.t}</span><div class="sub">${v.s}</div>`;
if(j.verdict!=='NO RULE'){html+=`<div class="eq">${j.target} = ${j.equation}</div>`;}
html+=drawPlot(j.plot);
html+=`<div class="meta">fit R² ${(+j.r2).toFixed(3)} · holds-at-the-edges ${(+j.r2_edge).toFixed(3)} · scope: ${j.scope} · from ${j.columns.join(', ')}</div>`;
html+=riv;
put('verdict',html)}
async function findings(){const j=await post('/api/findings',{q:val('q')});
put('fout',(j.findings||[]).map(f=>`#${f.id} [${f.kind}] ${f.name} — ${f.verdict||f.status||''} ${f.equation?'· '+f.equation.slice(0,60):''}`).join("\n")||"(nothing)")}
async function status(){const r=await fetch('/api/status',{method:'POST',body:'{}'});const j=await r.json();
const md=document.getElementById('mind');if(md)md.textContent='⌂ '+j.mind;
const st=document.getElementById('stat');if(st)st.textContent=j.nodes+' nodes · '+j.findings+' findings';
const lw=document.getElementById('laws');if(lw)lw.innerHTML=j.laws.map(l=>`<div><b>${l.name}</b> <span style=color:#8592a0>${l.eq}</span></div>`).join('')||'<small>none yet</small>';
const m=document.getElementById('minds');if(m)m.innerHTML=j.minds.map(x=>`<option>${x}</option>`).join('')}
status();</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._send(200, HTML, "text/html; charset=utf-8")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        try:
            with LOCK:
                out = api(self, body)
            self._send(200, json.dumps(Isaac._jsonable(out), default=str))
        except Exception as e:
            self._send(200, json.dumps({"error": f"{type(e).__name__}: {e}"}))


if __name__ == "__main__":
    port = 8674
    print(f"Isaac is listening — open http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
