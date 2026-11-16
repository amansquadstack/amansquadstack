#!/usr/bin/env python3
"""Generate all seasonal README SVGs into an assets directory.

Season is picked from today's month (northern hemisphere) unless SEASON env is set:
  winter Dec-Feb · spring Mar-May · summer Jun-Aug · autumn Sep-Nov

Writes: header.svg, divider.svg, terminal.svg, footer.svg,
        section-toolbox.svg, section-highlights.svg, section-motion.svg
Usage: python season_assets.py [assets_dir]
"""
import datetime
import os
import random
import sys

SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

SEASONS = {
    "winter": {
        "blobs": ("#3f5266", "#8fa9c0", "#5d6b7e"),
        "colors": ("#ece4d4", "#dfe6ea", "#b9c7d2"),
        "title": ("#c9d4dc", "#ece4d4", "#8fa9c0"),
        "shape": "snow", "density": 1.6, "tag": "❄ winter", "bye": "stay warm",
    },
    "spring": {
        "blobs": ("#6f7f5f", "#c99490", "#a7b494"),
        "colors": ("#ecc9c4", "#d8a3a0", "#f2e3dc"),
        "title": ("#b5c4a1", "#ece4d4", "#d29a94"),
        "shape": "petal", "density": 1.2, "tag": "🌸 spring", "bye": "fresh starts",
    },
    "summer": {
        "blobs": ("#5d8f8c", "#c9a24e", "#c47a52"),
        "colors": ("#f0d9a0", "#e2b857", "#f5e6c4"),
        "title": ("#8fbab6", "#ece4d4", "#e2b857"),
        "shape": "firefly", "density": 1.0, "tag": "☀ summer", "bye": "long days, short builds",
    },
    "autumn": {
        "blobs": ("#7a3427", "#b8623a", "#c99a3e"),
        "colors": ("#c56a3d", "#a8552f", "#d9a441", "#8a3b2e", "#b98a3e"),
        "title": ("#d9a441", "#ece4d4", "#c56a3d"),
        "shape": "leaf", "density": 1.0, "tag": "🍁 autumn", "bye": "falling for good code",
    },
}

SHAPE_DEFS = """
    <g id="snow" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" fill="none">
      <path d="M0-9V9M-7.8-4.5L7.8 4.5M-7.8 4.5L7.8-4.5"/>
      <path d="M-2.5-7L0-4.5L2.5-7M-2.5 7L0 4.5L2.5 7M-7.3-1.2L-4-2.3L-4.8-5.5M7.3 1.2L4 2.3L4.8 5.5M-7.3 1.2L-4 2.3L-4.8 5.5M7.3-1.2L4-2.3L4.8-5.5" stroke-width="1.1"/>
    </g>
    <path id="leaf" fill="currentColor" d="M0-12L2.5-6L6-8.5L5-3L10.5-4.5L8.5 0L11.5 2L5.5 3.2L6.5 7.5L1.2 5.2L.8 12H-.8L-1.2 5.2L-6.5 7.5L-5.5 3.2L-11.5 2L-8.5 0L-10.5-4.5L-5-3L-6-8.5L-2.5-6Z"/>
    <path id="petal" fill="currentColor" d="M0-7C4.5-7 6-1 0 7C-6-1-4.5-7-1.2-6.2L0-4.6L1.2-6.2Z"/>
    <radialGradient id="ffglow"><stop offset="0" stop-color="#fff7c2"/><stop offset=".35" stop-color="#fcd34d" stop-opacity=".9"/><stop offset="1" stop-color="#fcd34d" stop-opacity="0"/></radialGradient>"""


def season_for(today: datetime.date) -> str:
    return {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
            6: "summer", 7: "summer", 8: "summer"}.get(today.month, "autumn")


# ---------------------------------------------------------------- building blocks

def common_defs(cfg, w, h, rx):
    a, b, c = cfg["blobs"]
    t1, t2, t3 = cfg["title"]
    return f"""
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0f0e0c"/><stop offset="0.55" stop-color="#171410"/><stop offset="1" stop-color="#101111"/>
    </linearGradient>
    <radialGradient id="blobA"><stop offset="0" stop-color="{a}" stop-opacity="0.38"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
    <radialGradient id="blobB"><stop offset="0" stop-color="{b}" stop-opacity="0.26"/><stop offset="1" stop-color="{b}" stop-opacity="0"/></radialGradient>
    <radialGradient id="blobC"><stop offset="0" stop-color="{c}" stop-opacity="0.24"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>
    <linearGradient id="title" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="0" spreadMethod="repeat">
      <stop offset="0" stop-color="{t1}"/><stop offset="0.5" stop-color="{t2}"/><stop offset="1" stop-color="{t3}"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="0 0;{w} 0" dur="8s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" x2="1">
      <stop offset="0" stop-color="{t1}" stop-opacity="0"/><stop offset="0.5" stop-color="{t3}"/><stop offset="1" stop-color="{t1}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#ece4d4" stroke-opacity="0.035"/>
    </pattern>
    <clipPath id="card"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>{SHAPE_DEFS}"""


def blobs(w, h, strength=1.0):
    return f"""<g opacity="{strength}">
    <ellipse cx="{w * .2:.0f}" cy="{h * .25:.0f}" rx="{w * .27:.0f}" ry="{max(h * .65, 60):.0f}" fill="url(#blobA)">
      <animate attributeName="cx" values="{w * .2:.0f};{w * .35:.0f};{w * .2:.0f}" dur="14s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="{w * .8:.0f}" cy="{h * .75:.0f}" rx="{w * .25:.0f}" ry="{max(h * .6, 60):.0f}" fill="url(#blobB)">
      <animate attributeName="cx" values="{w * .8:.0f};{w * .65:.0f};{w * .8:.0f}" dur="12s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="{w * .53:.0f}" cy="{h:.0f}" rx="{w * .22:.0f}" ry="{max(h * .5, 50):.0f}" fill="url(#blobC)">
      <animate attributeName="cx" values="{w * .53:.0f};{w * .43:.0f};{w * .63:.0f};{w * .53:.0f}" dur="16s" repeatCount="indefinite"/>
    </ellipse></g>"""


def particles(cfg, rng, w, h, count, mode="fall", smin=0.55, smax=1.35, omin=0.55, omax=0.95):
    """mode: 'fall' (top -> bottom), 'drift' (left -> right, looping) or
    'gust' (one fast sweep across on page load, then gone)."""
    out = []
    shape = cfg["shape"]
    count = max(1, round(count * cfg["density"]))
    if mode == "gust":
        for _ in range(count):
            y = rng.uniform(10, h - 10)
            lift = rng.uniform(-60, 40)
            dur = rng.uniform(1.6, 2.6)
            begin = rng.uniform(0, 0.9)
            scale = rng.uniform(smin, smax)
            color = rng.choice(cfg["colors"])
            if shape == "firefly":
                glyph = f'<circle r="{8 * scale:.1f}" fill="url(#ffglow)"/>'
            elif shape == "snow" and rng.random() < 0.4:
                glyph = f'<circle r="{1.5 * scale + 0.8:.1f}" fill="{color}"/>'
            else:
                glyph = (f'<g><animateTransform attributeName="transform" type="rotate" values="0;{rng.choice((540, -540))}" '
                         f'dur="{dur:.1f}s" begin="{begin:.2f}s" fill="freeze"/>'
                         f'<use href="#{shape}" style="color:{color}" transform="scale({scale:.2f})"/></g>')
            out.append(
                f'<g transform="translate(-100 -100)"><animateTransform attributeName="transform" type="translate" '
                f'values="-40 {y:.0f}; {w * .45:.0f} {y + lift:.0f}; {w + 40} {y + lift / 2:.0f}" dur="{dur:.1f}s" '
                f'begin="{begin:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;.5;1" keySplines=".3 0 .7 1;.3 0 .7 1"/>'
                f'{glyph}</g>'
            )
        return "\n    ".join(out)
    for _ in range(count):
        dur = rng.uniform(9, 18) if mode == "fall" else rng.uniform(14, 26)
        begin = -rng.uniform(0, dur)  # negative begin: already mid-flight on load
        scale = rng.uniform(smin, smax)
        color = rng.choice(cfg["colors"])
        opacity = rng.uniform(omin, omax)
        sway = rng.uniform(15, 45) * rng.choice((-1, 1))

        if shape == "firefly":
            x, y = rng.uniform(10, w - 10), rng.uniform(6, h - 6)
            if mode == "fall":  # rise from below
                y0, y1 = h + 20, rng.uniform(-20, h * 0.4)
                path = f"{x:.0f} {y0:.0f}; {x + sway:.0f} {(y0 + y1) / 2:.0f}; {x - sway / 2:.0f} {y1:.0f}"
            else:  # wander in place
                dy = min(h / 3, 20)
                path = f"{x:.0f} {y:.0f}; {x + sway:.0f} {y - dy:.0f}; {x - sway / 2:.0f} {y + dy / 2:.0f}; {x:.0f} {y:.0f}"
            out.append(
                f'<g><animateTransform attributeName="transform" type="translate" values="{path}" '
                f'dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
                f'<circle r="{8 * scale:.1f}" fill="url(#ffglow)" opacity="{opacity:.2f}">'
                f'<animate attributeName="opacity" values=".1;{opacity:.2f};.1" dur="{rng.uniform(1.5, 3.5):.1f}s" '
                f'begin="{-rng.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle></g>'
            )
            continue

        if mode == "fall":
            x = rng.uniform(10, w - 10)
            path = f"{x:.0f} -30; {x + sway:.0f} {h / 2:.0f}; {x - sway / 2:.0f} {h + 30}"
        else:
            y = rng.uniform(6, h - 6)
            bob = min(h / 3, 14) * rng.choice((-1, 1))
            path = f"-30 {y:.0f}; {w / 3:.0f} {y + bob:.0f}; {2 * w / 3:.0f} {y - bob:.0f}; {w + 30} {y:.0f}"

        if shape == "snow" and rng.random() < 0.45:
            inner = f'<circle r="{1.5 * scale + 0.8:.1f}" fill="{color}" opacity="{opacity:.2f}"/>'
        else:
            spin = rng.choice(("0;360", "360;0"))
            inner = (
                f'<g><animateTransform attributeName="transform" type="rotate" values="{spin}" '
                f'dur="{rng.uniform(3, 8):.1f}s" repeatCount="indefinite"/>'
                f'<use href="#{shape}" style="color:{color}" opacity="{opacity:.2f}" transform="scale({scale:.2f})"/></g>'
            )
        out.append(
            f'<g><animateTransform attributeName="transform" type="translate" values="{path}" '
            f'dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>{inner}</g>'
        )
    return "\n    ".join(out)


def ground(cfg, rng, w, h):
    """Things that have settled along the bottom edge (footer)."""
    shape = cfg["shape"]
    out = []
    if shape == "snow":
        pts = " ".join(f"L{x} {h - 10 - 6 * ((x // 60) % 3)}" for x in range(0, w + 60, 60))
        out.append(f'<path d="M0 {h} {pts} L{w} {h}Z" fill="#e0f2fe" opacity=".18"/>')
    for x in range(14, w, 26):
        x += rng.uniform(-8, 8)
        y = h - rng.uniform(4, 14)
        color = rng.choice(cfg["colors"])
        if shape == "firefly":
            if rng.random() < 0.35:
                out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rng.uniform(3, 6):.1f}" fill="url(#ffglow)" opacity=".7"/>')
            continue
        if shape == "snow":
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rng.uniform(1, 2.5):.1f}" fill="#ffffff" opacity=".5"/>')
            continue
        out.append(
            f'<use href="#{shape}" style="color:{color}" opacity="{rng.uniform(.45, .85):.2f}" '
            f'transform="translate({x:.0f} {y:.0f}) rotate({rng.uniform(0, 360):.0f}) scale({rng.uniform(.5, .95):.2f})"/>'
        )
    return "\n    ".join(out)


def svg(w, h, label, defs, style, body, rx=22, border=True):
    edge = (f'\n  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="none" '
            f'stroke="#ffffff" stroke-opacity="0.08"/>') if border else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
  <defs>{defs}
  </defs>
  <style>{style}
  </style>
  {body}{edge}
</svg>
"""


ANIM_CSS = """
    @keyframes blink { 50% { opacity: 0 } }
    @keyframes rise { from { opacity: 0; transform: translateY(14px) } to { opacity: 1; transform: translateY(0) } }
    .cursor { animation: blink 1s steps(1) infinite; }"""


# ---------------------------------------------------------------- assets

def header(cfg, season):
    w, h = 1200, 340
    rng = random.Random(f"{season}-header")
    style = ANIM_CSS + f"""
    .name {{ font: 800 92px {SANS}; letter-spacing: -2px; }}
    .sub {{ font: 500 24px {SANS}; fill: #d6ccbb; letter-spacing: 6px; }}
    .prompt {{ font: 500 18px {MONO}; fill: #8f877a; opacity: 0; animation: rise 1s ease 2.6s forwards; }}
    .tag {{ font: 500 13px {MONO}; fill: #8f877a; opacity: .8; }}
    .accent {{ fill: {cfg["title"][0]} }} .accent2 {{ fill: {cfg["title"][2]} }}
    .cursor {{ fill: {cfg["title"][2]} }}
    .scan {{ animation: scan 4s ease-in-out infinite; }}
    @keyframes scan {{ 0%,100% {{ transform: translateX(-300px); opacity: 0 }} 50% {{ opacity: 1 }} 100% {{ transform: translateX(300px) }} }}"""
    acc = cfg["title"][2]
    defs = common_defs(cfg, w, h, 22) + f"""
    <linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1200" y2="0" spreadMethod="repeat">
      <stop offset="0" stop-color="#ece4d4"/><stop offset="0.4" stop-color="#ece4d4"/><stop offset="0.5" stop-color="{acc}"/>
      <stop offset="0.6" stop-color="#ece4d4"/><stop offset="1" stop-color="#ece4d4"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="-1200 0;0 0" dur="9s" repeatCount="indefinite"/>
    </linearGradient>"""
    body = f"""<g clip-path="url(#card)">
    <rect width="{w}" height="{h}" fill="url(#bg)"/>
    <rect width="{w}" height="{h}" fill="url(#grid)"/>
    {blobs(w, h)}
    {particles(cfg, rng, w, h, 28)}
    {particles(cfg, random.Random(f"{season}-gust"), w, h, 22, mode="gust", smin=.7, smax=1.4)}
    <text class="name" x="600" y="160" text-anchor="middle" fill="url(#name)">{drop_letters("Aman Singh", 160, start=.25)}</text>
    <clipPath id="typed"><rect x="190" y="180" width="0" height="40">
      <animate attributeName="width" dur="1.3s" begin="1.2s" fill="freeze" calcMode="discrete" values="{';'.join(str(int(820 * i / 38)) for i in range(39))}"/>
    </rect></clipPath>
    <text class="sub" x="600" y="210" text-anchor="middle" clip-path="url(#typed)">SOFTWARE ENGINEER · BUILDER · TINKERER</text>
    <rect x="450" y="232" width="300" height="2" fill="url(#edge)" class="scan"/>
    <text class="prompt" x="600" y="280" text-anchor="middle"><tspan class="accent2">aman@github</tspan>:<tspan class="accent">~</tspan>$ building something new<tspan class="cursor">▍</tspan></text>
    <text class="tag" x="1176" y="322" text-anchor="end">{cfg["tag"]}</text>
  </g>"""
    return svg(w, h, "Aman Singh", defs, style, body)


def divider(cfg, season):
    w, h = 1200, 40
    rng = random.Random(f"{season}-divider")
    body = f"""<rect x="0" y="{h / 2 - 1:.0f}" width="{w}" height="2" rx="1" fill="url(#edge)" opacity=".6"/>
  {particles(cfg, rng, w, h, 6, mode="drift", smin=.5, smax=.9)}"""
    return svg(w, h, "divider", common_defs(cfg, w, h, 0), "", body, border=False)


def footer(cfg, season):
    w, h = 1200, 170
    rng = random.Random(f"{season}-footer")
    style = f"""
    .t {{ font: 800 36px {SANS}; }}
    .s {{ font: 500 15px {MONO}; fill: #8f877a; }}"""
    body = f"""<g clip-path="url(#card)">
    <rect width="{w}" height="{h}" fill="url(#bg)"/>
    <rect width="{w}" height="{h}" fill="url(#grid)"/>
    {blobs(w, h, .8)}
    {particles(cfg, rng, w, h, 18, smin=.5, smax=1.1)}
    {ground(cfg, rng, w, h)}
    <text class="t" x="{w / 2:.0f}" y="78" text-anchor="middle" fill="url(#title)">Thanks for visiting!</text>
    <text class="s" x="{w / 2:.0f}" y="108" text-anchor="middle">{cfg["tag"]} · {cfg["bye"]}</text>
  </g>"""
    return svg(w, h, "Thanks for visiting", common_defs(cfg, w, h, 22), style, body)


def terminal(cfg, season):
    w, h = 900, 400
    rng = random.Random(f"{season}-terminal")
    style = f"""
    .mono {{ font: 500 17px {MONO}; }}
    .p {{ fill: {cfg["title"][2]} }} .t {{ fill: {cfg["title"][0]} }} .w {{ fill: #ece4d4 }} .m {{ fill: #8f877a }} .k {{ fill: {cfg["title"][2]} }} .g {{ fill: #9db89a }} .y {{ fill: #d9b77e }}
    .ln {{ opacity: 0; animation: show .01s linear forwards; }}
    @keyframes show {{ to {{ opacity: 1 }} }}
    .type {{ clip-path: inset(0 100% 0 0); animation: type .9s steps(28) forwards; }}
    @keyframes type {{ to {{ clip-path: inset(0 0 0 0) }} }}
    .cursor {{ fill: {cfg["title"][2]}; animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0 }} }}
    .glow {{ animation: glow 4s ease-in-out infinite; }}
    @keyframes glow {{ 0%,100% {{ stroke-opacity: .25 }} 50% {{ stroke-opacity: .7 }} }}"""
    t1, _, t3 = cfg["title"]
    defs = common_defs(cfg, w, h, 14) + f"""
    <linearGradient id="border" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="{t3}"/><stop offset=".5" stop-color="{t1}"/><stop offset="1" stop-color="{t3}"/>
    </linearGradient>"""
    body = f"""<g clip-path="url(#card)">
    <rect width="{w}" height="{h}" fill="#13120f"/>
    {blobs(w, h, .35)}
    {particles(cfg, rng, w, h, 12, smin=.45, smax=.9, omin=.25, omax=.5)}
  </g>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="none" stroke="url(#border)" stroke-width="2" class="glow"/>
  <path d="M1 15a14 14 0 0 1 14-14h870a14 14 0 0 1 14 14v25H1z" fill="#1b1915"/>
  <circle cx="26" cy="21" r="6.5" fill="#c9695c"/><circle cx="48" cy="21" r="6.5" fill="#d4a45a"/><circle cx="70" cy="21" r="6.5" fill="#8faa6a"/>
  <text x="450" y="26" text-anchor="middle" class="mono m" style="font-size:13px">aman — zsh — 90×24</text>

  <g class="mono">
    <g class="ln" style="animation-delay:.3s"><text x="28" y="80"><tspan class="p">➜ </tspan><tspan class="t">~ </tspan></text><text x="70" y="80" class="w type" style="animation-delay:.3s">whoami</text></g>
    <text x="28" y="108" class="ln w" style="animation-delay:1.3s">Aman Singh · software engineer · India 🇮🇳</text>

    <g class="ln" style="animation-delay:1.8s"><text x="28" y="146"><tspan class="p">➜ </tspan><tspan class="t">~ </tspan></text><text x="70" y="146" class="w type" style="animation-delay:1.8s">cat about.yml</text></g>
    <g class="ln" style="animation-delay:2.9s">
      <text x="28" y="174"><tspan class="k">loves:</tspan><tspan class="w">     backend · cloud · systems that scale</tspan></text>
      <text x="28" y="200"><tspan class="k">tinkers:</tspan><tspan class="w">   automation, dev tooling, side projects</tspan></text>
      <text x="28" y="226"><tspan class="k">past:</tspan><tspan class="w">      hackathon winner · research · problem solver</tspan></text>
      <text x="28" y="252"><tspan class="k">status:</tspan><tspan class="g">    ● building something new</tspan></text>
    </g>

    <g class="ln" style="animation-delay:3.5s"><text x="28" y="290"><tspan class="p">➜ </tspan><tspan class="t">~ </tspan></text><text x="70" y="290" class="w type" style="animation-delay:3.5s">echo $MOTTO</text></g>
    <text x="28" y="318" class="ln y" style="animation-delay:4.5s">"make it work, make it fast, make it boring"</text>

    <g class="ln" style="animation-delay:5s"><text x="28" y="356"><tspan class="p">➜ </tspan><tspan class="t">~ </tspan></text><rect x="70" y="341" width="10" height="20" class="cursor"/></g>
  </g>"""
    return svg(w, h, "whoami terminal", defs, style, body, rx=14, border=False)


# ---------------------------------------------------------------- entrance / data helpers

HERE = os.path.dirname(os.path.abspath(__file__))


def drop_letters(text, y, start=0.2, step=0.07, fall=0.8, frames=60):
    """Each letter falls into place one after another.

    Absolute y on a tspan starts a new text chunk (breaks centering), so we
    animate relative dy instead: dy_i(t) = offset_i(t) - offset_{i-1}(t),
    sampled on one shared timeline so every letter moves independently.
    """
    keys = [(0, -70), (.6, 8), (.8, -3), (1, 0)]

    def offset(t, s):
        if t <= s:
            return -70.0
        p = (t - s) / fall
        if p >= 1:
            return 0.0
        for (k0, v0), (k1, v1) in zip(keys, keys[1:]):
            if k0 <= p <= k1:
                return v0 + (v1 - v0) * (p - k0) / (k1 - k0)
        return 0.0

    starts = {i: start + i * step for i, ch in enumerate(text) if ch != " "}
    total = max(starts.values()) + fall
    times = [total * f / frames for f in range(frames + 1)]
    out, prev = [], None
    for i, ch in enumerate(text):
        if ch == " ":
            out.append(" ")
            continue
        s = starts[i]
        dys = [offset(t, s) - (offset(t, starts[prev]) if prev is not None else 0) for t in times]
        out.append(
            f'<tspan dy="{dys[0]:.1f}" fill-opacity="0">{ch}'
            f'<animate attributeName="dy" values="{";".join(f"{d:.1f}" for d in dys)}" dur="{total:.2f}s" fill="freeze"/>'
            f'<animate attributeName="fill-opacity" values="0;1" dur=".35s" begin="{s:.2f}s" fill="freeze"/></tspan>'
        )
        prev = i
    return "".join(out)


# ---------------------------------------------------------------- bento design system
# Data cards stay quiet: flat warm surface, 1px hairline, no glows/particles,
# ink-coloured text, ONE accent for the single data series.
INK, INK2, MUTED, FAINT = "#ece4d4", "#b9b0a2", "#8a8274", "#5c564d"
SURFACE, LINE = "#161512", "#ece4d4"


def bento_defs():
    return """
    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ece4d4" stop-opacity=".045"/><stop offset=".45" stop-color="#ece4d4" stop-opacity="0"/>
    </linearGradient>"""


BENTO_CSS = f"""
    .lbl {{ font: 500 11px {MONO}; fill: {MUTED}; letter-spacing: 1.6px; }}
    .sub {{ font: 400 13px {SANS}; fill: {MUTED}; }}
    .tick {{ font: 400 11px {MONO}; fill: {FAINT}; }}
    .h2 {{ font: 600 15px {SANS}; fill: {INK}; letter-spacing: -.1px; }}"""


def tile(x, y, w, h, r=18, delay=None):
    """A bento tile; optional fade-up entrance."""
    rect = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{SURFACE}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#sheen)"/>'
            f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{r}" fill="none" stroke="{LINE}" stroke-opacity=".09"/>')
    return rect


def enter(delay, body):
    """Fade + 10px rise, played once."""
    return (f'<g opacity="0" transform="translate(0 10)">'
            f'<animate attributeName="opacity" values="0;1" dur=".6s" begin="{delay:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 10;0 0" dur=".7s" begin="{delay:.2f}s" '
            f'fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/>{body}</g>')


def odometer(uid, value, x, y, size, color, begin=0.3, anchor="start", weight=600):
    """Digits roll like an odometer and settle on `value` (proportional-ish spacing)."""
    s = f"{value:,}"
    widths = [size * (0.27 if c == "," else 0.6) for c in s]
    width = sum(widths)
    x0 = x - width / 2 if anchor == "middle" else x
    lh = size * 1.2
    parts = [f'<clipPath id="od{uid}"><rect x="{x0 - 4:.1f}" y="{y - size * 0.92:.1f}" width="{width + 8:.1f}" height="{size * 1.14:.1f}"/></clipPath>',
             f'<g clip-path="url(#od{uid})" fill="{color}" style="font: {weight} {size}px {SANS}; letter-spacing: -.02em" text-anchor="middle">']
    cx = x0
    for i, ch in enumerate(s):
        mid = cx + widths[i] / 2
        cx += widths[i]
        if not ch.isdigit():
            parts.append(f'<text x="{mid:.1f}" y="{y}">{ch}</text>')
            continue
        d = int(ch)
        stack = "".join(f'<text x="{mid:.1f}" y="{y + k * lh:.1f}">{k % 10}</text>' for k in range(20))
        b = begin + (len(s) - i) * 0.07
        parts.append(
            f'<g>{stack}<animateTransform attributeName="transform" type="translate" values="0 0;0 {-(10 + d) * lh:.1f}" '
            f'dur="1.5s" begin="{b:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".15 .8 .25 1"/></g>')
    parts.append("</g>")
    return "".join(parts)


def section(cfg, season, key, title):
    """Quiet section label: index + title + hairline. Dark tile so it reads in light mode too."""
    w, h = 1200, 64
    idx = {"toolbox": "01", "highlights": "02", "motion": "03"}.get(key, "")
    acc = cfg["title"][2]
    body = f"""{tile(0, 0, w, h, 16)}
  {enter(.05, f'''<text x="28" y="39" style="font: 500 12px {MONO}; letter-spacing: 1.5px" fill="{acc}">{idx}</text>
    <text x="60" y="40" style="font: 600 20px {SANS}; letter-spacing: -.2px" fill="{INK}">{title}</text>
    <rect x="{60 + len(title) * 11 + 24:.0f}" y="32" width="{w - (60 + len(title) * 11 + 24) - 28:.0f}" height="1" fill="{LINE}" fill-opacity=".09"/>''')}"""
    return svg(w, h, title, bento_defs(), "", body, border=False)


def load_stats():
    path = os.path.join(HERE, "..", "data", "stats.json")
    try:
        with open(path) as f:
            return __import__("json").load(f)
    except FileNotFoundError:
        return None


def month_ticks(updated, n):
    end = datetime.date.fromisoformat(updated)
    ticks, last = [], None
    for i in range(n):
        d = end - datetime.timedelta(days=7 * (n - 1 - i))
        if d.month != last:
            if last is not None and d.month % 3 == 1:
                ticks.append((i, d.strftime("%b")))
            last = d.month
    return ticks


def stats_card(cfg, season, st):
    """Bento: hero tile (contributions + area chart) + 6 small stat tiles."""
    acc = cfg["title"][2]
    w, h, g = 1200, 452, 14
    hw = 700
    sw = (w - hw - g * 2) / 2
    sh = (h - g * 2) / 3
    parts = [enter(.05, tile(0, 0, hw, h))]

    # hero
    wk = st["weekly"] or [0]
    px0, px1, py0, py1 = 32, hw - 32, 210, h - 52
    mx = max(wk) or 1
    pts = [(px0 + (px1 - px0) * i / max(len(wk) - 1, 1), py1 - (py1 - py0) * v / mx) for i, v in enumerate(wk)]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    length = sum(((pts[i][0] - pts[i - 1][0]) ** 2 + (pts[i][1] - pts[i - 1][1]) ** 2) ** .5 for i in range(1, len(pts)))
    area = line + f" L{px1} {py1} L{px0} {py1}Z"
    pk = max(range(len(wk)), key=lambda i: wk[i])
    kx, ky = pts[pk]
    ticks = "".join(f'<text x="{pts[i][0]:.1f}" y="{py1 + 26}" class="tick" text-anchor="middle">{m}</text>'
                    f'<rect x="{pts[i][0]:.1f}" y="{py1}" width="1" height="5" fill="{LINE}" fill-opacity=".18"/>'
                    for i, m in month_ticks(st["updated"], len(wk)))
    grid = "".join(f'<rect x="{px0}" y="{py1 - (py1 - py0) * f:.1f}" width="{px1 - px0}" height="1" fill="{LINE}" fill-opacity=".05"/>'
                   for f in (.5, 1))
    parts.append(enter(.15, f"""
    <text x="32" y="48" class="lbl">CONTRIBUTIONS · LAST 12 MONTHS</text>
    {odometer("hero", st["contributions"], 30, 128, 76, INK, begin=.3)}
    <text x="34" y="164" class="sub">across {st["repos"]} repositories · busiest week: {wk[pk]} contributions</text>
    {grid}
    <rect x="{px0}" y="{py1}" width="{px1 - px0}" height="1" fill="{LINE}" fill-opacity=".14"/>
    {ticks}
    <path d="{area}" fill="url(#heroFill)" opacity="0"><animate attributeName="opacity" values="0;1" dur="1s" begin="2.1s" fill="freeze"/></path>
    <path d="{line}" fill="none" stroke="{acc}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"
          stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}">
      <animate attributeName="stroke-dashoffset" values="{length:.0f};0" dur="2s" begin=".5s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/></path>
    <g opacity="0"><animate attributeName="opacity" values="0;1" dur=".4s" begin="2.4s" fill="freeze"/>
      <circle cx="{kx:.1f}" cy="{ky:.1f}" r="6" fill="{acc}" stroke="{SURFACE}" stroke-width="2"/>
      <text x="{kx - 12:.1f}" y="{ky + 4:.1f}" text-anchor="end" style="font: 600 12px {SANS}" fill="{INK2}">{wk[pk]}</text></g>"""))

    small = [
        ("COMMITS", st["commits"], "past year"),
        ("PULL REQUESTS", st["prs"], "past year"),
        ("CURRENT STREAK", st["current_streak"], f"day{'s' if st['current_streak'] != 1 else ''} in a row"),
        ("REPOS", st["repos"], "contributed to"),
        ("LONGEST STREAK", st["longest_streak"], "days in a row"),
        ("PROFILE VIEWS", st["views"] or 0, "and counting"),
    ]
    for i, (label, val, sub) in enumerate(small):
        col, row = i % 2, i // 2
        x = hw + g + col * (sw + g)
        y = row * (sh + g)
        d = .25 + i * .08
        parts.append(enter(d, f"""{tile(x, y, sw, sh, 16)}
      <text x="{x + 22}" y="{y + 34}" class="lbl">{label}</text>
      {odometer(f"t{i}", val, x + 20, y + 88, 40, INK, begin=d + .2)}
      <text x="{x + 22}" y="{y + sh - 22}" class="sub">{sub}</text>"""))

    defs = bento_defs() + f"""
    <linearGradient id="heroFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{acc}" stop-opacity=".22"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/>
    </linearGradient>"""
    return svg(w, h, "GitHub stats", defs, BENTO_CSS, "\n  ".join(parts), border=False)


def languages_card(cfg, season, st):
    """Ranked thin bars, one series = one colour; names/values in ink."""
    acc = cfg["title"][2]
    langs = st["languages"][:6]
    w = 1200
    cols, per = 2, 3
    rows_h = 52
    h = 92 + rows_h * per + 18
    top = max((l["pct"] for l in langs), default=1) or 1
    colw = (w - 64 - 48) / cols
    parts = [tile(0, 0, w, h), f'<text x="32" y="48" class="lbl">LANGUAGES · SHARE OF COMMITS</text>',
             f'<text x="{w - 32}" y="48" class="lbl" text-anchor="end">INCL. PRIVATE REPOS</text>']
    for i, l in enumerate(langs):
        c, r = i // per, i % per
        x = 32 + c * (colw + 48)
        y = 92 + r * rows_h
        d = .2 + i * .1
        full = (colw) * l["pct"] / top
        parts.append(enter(d, f"""
      <text x="{x}" y="{y + 6}" style="font: 500 15px {SANS}" fill="{INK}">{l["name"]}</text>
      <text x="{x + colw}" y="{y + 6}" text-anchor="end" style="font: 500 13px {MONO}" fill="{INK2}">{l["pct"]:.1f}%</text>
      <rect x="{x}" y="{y + 18}" width="{colw:.1f}" height="4" rx="2" fill="{LINE}" fill-opacity=".07"/>
      <rect x="{x}" y="{y + 18}" width="0" height="4" rx="2" fill="{acc}">
        <animate attributeName="width" values="0;{max(full, 4):.1f}" dur="1.2s" begin="{d + .15:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/></rect>"""))
    return svg(w, h, "Languages", bento_defs(), BENTO_CSS, "\n  ".join(parts), border=False)


ORBITS = [
    (110, 34, ["python", "typescript", "django", "postgres", "aws", "docker"]),
    (185, -50, ["javascript", "bash", "nodejs", "redis", "kubernetes", "terraform", "prometheus", "grafana"]),
    (260, 70, ["cpp", "mysql", "rabbitmq", "kafka", "linux", "nginx", "sentry", "elasticsearch", "git", "githubactions"]),
]


def icon_uri(name):
    import base64
    with open(os.path.join(HERE, "icons", f"{name}.svg"), "rb") as f:
        return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()


def orbit_card(cfg, season):
    import math
    w, h = 1200, 620
    cx, cy = w / 2, h / 2
    acc = cfg["title"][2]
    rings, n = [], 0
    for r, period, icons in ORBITS:
        direction = 1 if period > 0 else -1
        period = abs(period)
        items = []
        for k, name in enumerate(icons):
            a = 2 * math.pi * k / len(icons) + r
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            b = 0.3 + n * 0.05
            n += 1
            items.append(f"""<g transform="translate({x:.1f} {y:.1f})"><g transform="scale(0)">
          <animateTransform attributeName="transform" type="scale" values="0;1.08;1" keyTimes="0;.7;1" dur=".5s" begin="{b:.2f}s" fill="freeze"/>
          <g><animateTransform attributeName="transform" type="rotate" values="0;{-360 * direction}" dur="{period}s" repeatCount="indefinite"/>
            <image href="{icon_uri(name)}" x="-22" y="-22" width="44" height="44"/></g></g></g>""")
        rings.append(f"""<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE}" stroke-opacity=".08"/>
      <g><animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};{360 * direction} {cx} {cy}" dur="{period}s" repeatCount="indefinite"/>
        {"".join(items)}</g>""")
    body = f"""{tile(0, 0, w, h, 20)}
  <text x="32" y="48" class="lbl">24 TOOLS I SHIP WITH</text>
  <circle cx="{cx}" cy="{cy}" r="34" fill="{SURFACE}" stroke="{LINE}" stroke-opacity=".14"/>
  <circle cx="{cx}" cy="{cy}" r="4" fill="{acc}"><animate attributeName="r" values="3;5;3" dur="3s" repeatCount="indefinite"/></circle>
  {"".join(rings)}"""
    return svg(w, h, "Tech stack", bento_defs(), BENTO_CSS, body, border=False)


HIGHLIGHTS = [
    ("HACKATHON", "Innohacks", "Winner, out of 100+ teams"),
    ("RESEARCH", "IIT Bombay", "Yoga × logical thinking study"),
    ("AWARD", "Delhi Govt.", "Excellence in Education award"),
    ("TEACHING", "Chegg SME", "100+ problems solved"),
]


def highlights_card(cfg, season):
    acc = cfg["title"][2]
    w, h, g = 1200, 168, 14
    tw = (w - g * 3) / 4
    parts = []
    for i, (kind, title, sub) in enumerate(HIGHLIGHTS):
        x = i * (tw + g)
        parts.append(enter(.15 + i * .12, f"""{tile(x, 0, tw, h, 16)}
      <circle cx="{x + 26}" cy="38" r="3.5" fill="{acc}"/>
      <text x="{x + 38}" y="42" class="lbl">{kind}</text>
      <text x="{x + 22}" y="{h - 52}" style="font: 600 22px {SANS}; letter-spacing: -.3px" fill="{INK}">{title}</text>
      <text x="{x + 22}" y="{h - 26}" class="sub">{sub}</text>"""))
    return svg(w, h, "Highlights", bento_defs(), BENTO_CSS, "\n  ".join(parts), border=False)

SECTIONS = {
    "toolbox": "Toolbox",
    "highlights": "Highlights",
    "motion": "GitHub in Motion",
}


def build_all(season):
    cfg = SEASONS[season]
    files = {
        "header.svg": header(cfg, season),
        "divider.svg": divider(cfg, season),
        "terminal.svg": terminal(cfg, season),
        "footer.svg": footer(cfg, season),
    }
    for key, title in SECTIONS.items():
        files[f"section-{key}.svg"] = section(cfg, season, key, title)
    files["orbit.svg"] = orbit_card(cfg, season)
    files["highlights.svg"] = highlights_card(cfg, season)
    st = load_stats()
    if st:
        files["stats.svg"] = stats_card(cfg, season, st)
        files["languages.svg"] = languages_card(cfg, season, st)
    return files


if __name__ == "__main__":
    season = os.environ.get("SEASON") or season_for(datetime.date.today())
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "assets"
    os.makedirs(out_dir, exist_ok=True)
    files = build_all(season)
    n = len(files)
    for name, content in files.items():
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            f.write(content)
    print(f"wrote {n} files to {out_dir} ({season})")
