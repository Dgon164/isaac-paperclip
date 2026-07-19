"""plot.py — THE PLOT FACE (the specifics layer, owner 2026-07-18:
"plot data points, error bars all the standard data analysis stuff
you would need").

Stdlib SVG, the observed-maps precedent — no new dependency, and a
plot is a RECEIPT: every mark on it is a number the dossier or the
court already said. Deterministic: the same inputs write the same
bytes (the artifact claim, again).

  plot_series(path, t, y, ...)  ->  path
    points        every (t, y) as a dot
    err           error bars (scalar or per-point; the residual rms
                  or the floor — the caller says which in err_why)
    trend         the court's trend curve, dashed, drawn only where
                  the court said one
    steps         frame averages (e.g. yearly) as a step line
    anomalies     indices ringed — flagged, never judged
"""

from xml.sax.saxutils import escape as _esc

_W, _H = 860, 460
_L, _R, _T, _B = 64, 16, 34, 44  # margins


def _nice(lo, hi, n=5):
    """Tick positions the ordinary way: 1/2/5 x 10^k steps."""
    span = (hi - lo) or 1.0
    import math
    raw = span / max(1, n)
    mag = 10.0 ** math.floor(math.log10(abs(raw)))
    step = min((s for s in (1, 2, 5, 10)
                if s * mag >= raw), default=10) * mag
    t0 = math.ceil(lo / step) * step
    out = []
    v = t0
    while v <= hi + 1e-9 * span:
        out.append(0.0 if abs(v) < 1e-12 * span else v)
        v += step
    return out


def _f(v):
    return f"{v:.6g}"


def plot_series(path, t, y, title="", xlabel="t", ylabel="y",
                err=None, err_why=None, trend=None, steps=None,
                anomalies=None):
    t = [float(v) for v in t]
    y = [float(v) for v in y]
    ys = list(y)
    if err is not None:
        e = ([float(err)] * len(y) if isinstance(err, (int, float))
             else [float(v) for v in err])
        ys += [a + b for a, b in zip(y, e)] + \
              [a - b for a, b in zip(y, e)]
    else:
        e = None
    if steps:
        ys += [float(v) for _tv, v in steps]
    xlo, xhi = min(t), max(t)
    ylo, yhi = min(ys), max(ys)
    xpad = (xhi - xlo or 1.0) * 0.04
    ypad = (yhi - ylo or 1.0) * 0.08
    xlo, xhi = xlo - xpad, xhi + xpad
    ylo, yhi = ylo - ypad, yhi + ypad

    def X(v):
        return _L + (v - xlo) / (xhi - xlo) * (_W - _L - _R)

    def Y(v):
        return _H - _B - (v - ylo) / (yhi - ylo) * (_H - _T - _B)

    S = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{_W}" '
         f'height="{_H}" font-family="monospace" font-size="11">',
         f'<rect width="{_W}" height="{_H}" fill="white"/>',
         f'<text x="{_L}" y="18" font-size="13">{_esc(title)}</text>']
    # axes + ticks
    S.append(f'<line x1="{_L}" y1="{_H - _B}" x2="{_W - _R}" '
             f'y2="{_H - _B}" stroke="black"/>')
    S.append(f'<line x1="{_L}" y1="{_T}" x2="{_L}" y2="{_H - _B}" '
             f'stroke="black"/>')
    for v in _nice(xlo + xpad, xhi - xpad):
        x = X(v)
        S.append(f'<line x1="{_f(x)}" y1="{_H - _B}" x2="{_f(x)}" '
                 f'y2="{_H - _B + 4}" stroke="black"/>')
        S.append(f'<text x="{_f(x)}" y="{_H - _B + 16}" '
                 f'text-anchor="middle">{_f(v)}</text>')
    for v in _nice(ylo + ypad, yhi - ypad):
        yy = Y(v)
        S.append(f'<line x1="{_L - 4}" y1="{_f(yy)}" x2="{_L}" '
                 f'y2="{_f(yy)}" stroke="black"/>')
        S.append(f'<text x="{_L - 7}" y="{_f(yy + 3)}" '
                 f'text-anchor="end">{_f(v)}</text>')
    S.append(f'<text x="{(_L + _W - _R) // 2}" y="{_H - 8}" '
             f'text-anchor="middle">{_esc(xlabel)}</text>')
    S.append(f'<text x="14" y="{(_T + _H - _B) // 2}" '
             f'text-anchor="middle" transform="rotate(-90 14 '
             f'{(_T + _H - _B) // 2})">{_esc(ylabel)}</text>')
    # error bars beneath the points
    if e is not None:
        for tv, yv, ev in zip(t, y, e):
            x = X(tv)
            S.append(f'<line x1="{_f(x)}" y1="{_f(Y(yv - ev))}" '
                     f'x2="{_f(x)}" y2="{_f(Y(yv + ev))}" '
                     f'stroke="#999" stroke-width="1" '
                     f'class="errbar"/>')
        if err_why:
            S.append(f'<text x="{_W - _R}" y="18" text-anchor="end" '
                     f'fill="#555">error bars: {_esc(err_why)}</text>')
    # frame steps (e.g. yearly averages)
    if steps:
        pts = " ".join(f"{_f(X(tv))},{_f(Y(v))}" for tv, v in steps)
        S.append(f'<polyline points="{pts}" fill="none" '
                 f'stroke="#c33" stroke-width="2" class="steps"/>')
    # the court's trend, dashed
    if trend is not None:
        pts = " ".join(f"{_f(X(tv))},{_f(Y(v))}"
                       for tv, v in zip(t, trend))
        S.append(f'<polyline points="{pts}" fill="none" '
                 f'stroke="#36c" stroke-width="1.5" '
                 f'stroke-dasharray="6 4" class="trend"/>')
    # the points themselves
    for tv, yv in zip(t, y):
        S.append(f'<circle cx="{_f(X(tv))}" cy="{_f(Y(yv))}" '
                 f'r="2.4" fill="black" class="pt"/>')
    # anomalies ringed — flagged, never judged
    for i in (anomalies or []):
        S.append(f'<circle cx="{_f(X(t[i]))}" cy="{_f(Y(y[i]))}" '
                 f'r="6" fill="none" stroke="#c33" '
                 f'stroke-width="1.5" class="anomaly"/>')
    S.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(S))
    return path
