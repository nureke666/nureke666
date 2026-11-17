"""Generates the animated profile header: assets/header-dark.svg and assets/header-light.svg.

Run: python3 assets/build_header.py  (stdlib only). Edit PHRASES / TERMINAL and re-run.
"""

import math
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 900, 260
PHRASES = [
    "Backend developer · Python",
    "FastAPI · aiogram · PostgreSQL",
    "Telegram bots & AI integrations",
    "Learning DevOps: Linux, Git, Bash",
]
# (kind, text): "cmd" lines get a "$" prompt, "out" lines are command output.
TERMINAL = [
    ("cmd", "whoami"),
    ("out", "nurdaulet · backend dev"),
    ("cmd", "cat learning.txt"),
    ("out", "linux ✓  git ✓  bash …"),
]

THEMES = {
    "dark": dict(
        bg1="#0d1117", bg2="#141a2e", bg3="#1e1640", border="#30363d",
        text="#e6edf3", muted="#8b949e", a1="#2dd4bf", a2="#a78bfa",
        term_bg="#0b0f17", term_border="#30363d", glow=0.28, wave=(0.20, 0.14), dots=0.30,
    ),
    "light": dict(
        bg1="#ffffff", bg2="#f3f6ff", bg3="#f1ecff", border="#d0d7de",
        text="#1f2328", muted="#57606a", a1="#0d9488", a2="#7c3aed",
        term_bg="#ffffff", term_border="#d0d7de", glow=0.16, wave=(0.12, 0.09), dots=0.35,
    ),
}

SANS = "'Segoe UI', Ubuntu, -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, 'DejaVu Sans Mono', 'Liberation Mono', monospace"

# Typing line geometry: monospace 20px, every glyph is forced to CW wide via textLength.
TYPE_X, TYPE_Y, FS, CW = 74, 186, 20, 12.0
T_TYPE, T_HOLD, T_DEL, T_GAP = 0.075, 1.9, 0.035, 0.4


def timeline():
    """Per-phrase (time, visible_chars) steps over one full cycle, plus cycle length."""
    t, steps = 0.0, []
    for p in PHRASES:
        n, s = len(p), []
        s.append((t, 0))
        for k in range(1, n + 1):
            s.append((t + k * T_TYPE, k))
        t += n * T_TYPE + T_HOLD
        for k in range(n - 1, -1, -1):
            t += T_DEL
            s.append((t, k))
        t += T_GAP
        steps.append(s)
    return steps, t


def discrete(steps, total, fmt):
    """SMIL values/keyTimes for a discrete animation; steps start at t>=0 and go up."""
    pts = [(0.0, 0)] + [st for st in steps if st[0] > 0]
    times = ";".join(f"{tt / total:.5f}" for tt, _ in pts)
    vals = ";".join(fmt(v) for _, v in pts)
    return vals, times


def wave(base, amp, period, width=W * 2):
    pts = [f"{x},{base + amp * math.sin(2 * math.pi * x / period):.1f}" for x in range(0, width + 1, 10)]
    return f"M0,{H} L" + " L".join(pts) + f" L{width},{H} Z"


def build(c):
    steps, total = timeline()
    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'role="img" aria-label="Nurdaulet — backend developer (Python), learning DevOps">')
    a("<title>Nurdaulet — backend developer (Python), learning DevOps</title>")
    a("<defs>")
    a(f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c["bg1"]}"/>'
      f'<stop offset=".55" stop-color="{c["bg2"]}"/><stop offset="1" stop-color="{c["bg3"]}"/></linearGradient>')
    a(f'<linearGradient id="name" gradientUnits="userSpaceOnUse" x1="46" y1="0" x2="330" y2="0">'
      f'<stop offset="0" stop-color="{c["a1"]}"/><stop offset="1" stop-color="{c["a2"]}"/></linearGradient>')
    a(f'<radialGradient id="glow"><stop offset="0" stop-color="{c["a2"]}" stop-opacity="{c["glow"]}"/>'
      f'<stop offset="1" stop-color="{c["a2"]}" stop-opacity="0"/></radialGradient>')
    a(f'<pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">'
      f'<circle cx="2" cy="2" r="1.2" fill="{c["muted"]}"/></pattern>')
    a('<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
      '<stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>')
    a(f'<mask id="dotmask"><rect x="420" y="0" width="{W - 420}" height="{H}" fill="url(#fade)"/></mask>')
    a(f'<clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>')
    for i, p in enumerate(PHRASES):
        vals, times = discrete(steps[i], total, lambda v: f"{v * CW:.1f}")
        a(f'<clipPath id="c{i}"><rect x="{TYPE_X}" y="{TYPE_Y - FS}" height="{FS + 8}" width="0">'
          f'<animate attributeName="width" dur="{total:.3f}s" repeatCount="indefinite" calcMode="discrete" '
          f'values="{vals}" keyTimes="{times}"/></rect></clipPath>')
    a("</defs>")

    a('<g clip-path="url(#card)">')
    a(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    a(f'<rect width="{W}" height="{H}" fill="url(#dots)" opacity="{c["dots"]}" mask="url(#dotmask)"/>')
    a('<circle cx="190" cy="120" r="230" fill="url(#glow)"/>')
    for (base, amp, period, dur, op, col) in (
        (224, 9, 450, 16, c["wave"][0], c["a2"]),
        (234, 6, 300, 10, c["wave"][1], c["a1"]),
    ):
        a(f'<path d="{wave(base, amp, period)}" fill="{col}" opacity="{op}">'
          f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{W} 0" '
          f'dur="{dur}s" repeatCount="indefinite"/></path>')

    # Greeting and name, fading in once.
    a(f'<g font-family="{SANS}"><animate attributeName="opacity" from="0" to="1" dur="0.9s" fill="freeze"/>')
    a(f'<text x="48" y="80" font-size="20" fill="{c["muted"]}">Hi there, I’m</text>')
    a(f'<text x="45" y="136" font-size="56" font-weight="700" fill="url(#name)">Nurdaulet</text>')
    a("</g>")

    # Typing line.
    a(f'<g font-family="{MONO}" font-size="{FS}">')
    a(f'<text x="48" y="{TYPE_Y}" fill="{c["a1"]}" font-weight="700">❯</text>')
    for i, p in enumerate(PHRASES):
        a(f'<text x="{TYPE_X}" y="{TYPE_Y}" fill="{c["text"]}" textLength="{len(p) * CW:.1f}" '
          f'lengthAdjust="spacing" clip-path="url(#c{i})" xml:space="preserve">{escape(p)}</text>')
    cur = sorted(st for s in steps for st in s)
    vals, times = discrete(cur, total, lambda v: f"{TYPE_X + v * CW + 1:.1f}")
    a(f'<rect x="{TYPE_X}" y="{TYPE_Y - FS + 2}" width="10" height="{FS + 2}" fill="{c["a1"]}">'
      f'<animate attributeName="x" dur="{total:.3f}s" repeatCount="indefinite" calcMode="discrete" '
      f'values="{vals}" keyTimes="{times}"/>'
      f'<animate attributeName="opacity" values="1;0" dur="1s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    a("</g>")

    # Terminal card: lines appear one by one, loop every 12s.
    tx, ty, tw, th = 572, 46, 290, 146
    a(f'<g font-family="{MONO}" font-size="13">')
    a(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="10" fill="{c["term_bg"]}" '
      f'stroke="{c["term_border"]}" opacity="0.92"/>')
    for j, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        a(f'<circle cx="{tx + 18 + j * 16}" cy="{ty + 16}" r="5" fill="{col}"/>')
    a(f'<text x="{tx + tw / 2 + 20}" y="{ty + 20}" fill="{c["muted"]}" font-size="12" text-anchor="middle">'
      f"~/nureke666</text>")
    a(f'<line x1="{tx}" y1="{ty + 32}" x2="{tx + tw}" y2="{ty + 32}" stroke="{c["term_border"]}"/>')
    loop = 12.0
    for k, (kind, txt) in enumerate(TERMINAL):
        y = ty + 58 + k * 24
        t0 = 0.6 + k * 0.9
        a(f'<g opacity="0"><animate attributeName="opacity" dur="{loop}s" repeatCount="indefinite" '
          f'values="0;0;1;1;0" keyTimes="0;{t0 / loop:.4f};{(t0 + 0.25) / loop:.4f};{10.8 / loop:.4f};1"/>')
        if kind == "cmd":
            a(f'<text x="{tx + 16}" y="{y}" fill="{c["a1"]}">$</text>')
            a(f'<text x="{tx + 32}" y="{y}" fill="{c["text"]}">{escape(txt)}</text>')
        else:
            a(f'<text x="{tx + 16}" y="{y}" fill="{c["muted"]}">{escape(txt)}</text>')
        a("</g>")
    a("</g>")
    a("</g>")
    a(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="none" stroke="{c["border"]}"/>')
    a("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    for name, colors in THEMES.items():
        (here / f"header-{name}.svg").write_text(build(colors), encoding="utf-8")
        print(f"wrote assets/header-{name}.svg")
