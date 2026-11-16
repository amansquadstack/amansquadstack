#!/usr/bin/env python3
"""Generate assets/header.svg with seasonal falling particles.

Season is picked from today's month (northern hemisphere) unless SEASON env is set:
  winter Dec-Feb · spring Mar-May · summer Jun-Aug · autumn Sep-Nov
Usage: python season_header.py [output_path]
"""
import datetime
import os
import random
import sys

W, H = 1200, 340

SEASONS = {
    "winter": {
        "blobs": ("#3b82f6", "#a5f3fc", "#c4b5fd"),
        "colors": ("#ffffff", "#e0f2fe", "#bae6fd"),
        "shape": "snow", "count": 46, "tag": "❄ winter",
    },
    "spring": {
        "blobs": ("#7C3AED", "#34d399", "#f9a8d4"),
        "colors": ("#fbcfe8", "#f9a8d4", "#fce7f3"),
        "shape": "petal", "count": 34, "tag": "🌸 spring",
    },
    "summer": {
        "blobs": ("#7C3AED", "#00E5FF", "#fbbf24"),
        "colors": ("#fde68a", "#fcd34d", "#fef3c7"),
        "shape": "firefly", "count": 30, "tag": "☀ summer",
    },
    "autumn": {
        "blobs": ("#7C3AED", "#f97316", "#dc2626"),
        "colors": ("#f97316", "#ea580c", "#dc2626", "#f59e0b", "#b45309"),
        "shape": "leaf", "count": 26, "tag": "🍁 autumn",
    },
}

SHAPES = """
    <g id="snow" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" fill="none">
      <path d="M0-9V9M-7.8-4.5L7.8 4.5M-7.8 4.5L7.8-4.5"/>
      <path d="M-2.5-7L0-4.5L2.5-7M-2.5 7L0 4.5L2.5 7M-7.3-1.2L-4-2.3L-4.8-5.5M7.3 1.2L4 2.3L4.8 5.5M-7.3 1.2L-4 2.3L-4.8 5.5M7.3-1.2L4-2.3L4.8-5.5" stroke-width="1.1"/>
    </g>
    <path id="leaf" fill="currentColor" d="M0-12L2.5-6L6-8.5L5-3L10.5-4.5L8.5 0L11.5 2L5.5 3.2L6.5 7.5L1.2 5.2L.8 12H-.8L-1.2 5.2L-6.5 7.5L-5.5 3.2L-11.5 2L-8.5 0L-10.5-4.5L-5-3L-6-8.5L-2.5-6Z"/>
    <path id="petal" fill="currentColor" d="M0-7C4.5-7 6-1 0 7C-6-1-4.5-7-1.2-6.2L0-4.6L1.2-6.2Z"/>
    <radialGradient id="ffglow"><stop offset="0" stop-color="#fff7c2"/><stop offset=".35" stop-color="#fcd34d" stop-opacity=".9"/><stop offset="1" stop-color="#fcd34d" stop-opacity="0"/></radialGradient>
"""


def season_for(today: datetime.date) -> str:
    m = today.month
    return {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
            6: "summer", 7: "summer", 8: "summer"}.get(m, "autumn")


def particles(cfg: dict, rng: random.Random) -> str:
    out = []
    shape = cfg["shape"]
    for _ in range(cfg["count"]):
        x = rng.uniform(10, W - 10)
        dur = rng.uniform(9, 18)
        begin = -rng.uniform(0, dur)  # negative begin = already mid-flight on load
        scale = rng.uniform(0.55, 1.35)
        color = rng.choice(cfg["colors"])
        opacity = rng.uniform(0.55, 0.95)
        sway = rng.uniform(15, 45) * rng.choice((-1, 1))
        spin_dur = rng.uniform(3, 8)
        spin_dir = rng.choice(("0;360", "360;0"))

        if shape == "firefly":
            # rise slowly, wander, pulse
            y0, y1 = H + 20, rng.uniform(-20, H * 0.4)
            path = f"{x:.0f} {y0:.0f}; {x + sway:.0f} {(y0 + y1) / 2:.0f}; {x - sway / 2:.0f} {y1:.0f}"
            r = 8 * scale
            out.append(
                f'<g><animateTransform attributeName="transform" type="translate" values="{path}" '
                f'dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
                f'<circle r="{r:.1f}" fill="url(#ffglow)">'
                f'<animate attributeName="opacity" values=".15;1;.15" dur="{rng.uniform(1.5, 3.5):.1f}s" '
                f'begin="{-rng.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle></g>'
            )
            continue

        path = f"{x:.0f} -30; {x + sway:.0f} {H / 2:.0f}; {x - sway / 2:.0f} {H + 30}"
        if shape == "snow" and rng.random() < 0.45:
            # mix in soft round flakes
            inner = f'<circle r="{1.5 * scale + 0.8:.1f}" fill="{color}" opacity="{opacity:.2f}"/>'
        else:
            inner = (
                f'<g><animateTransform attributeName="transform" type="rotate" values="{spin_dir}" '
                f'dur="{spin_dur:.1f}s" repeatCount="indefinite"/>'
                f'<use href="#{shape}" style="color:{color}" opacity="{opacity:.2f}" '
                f'transform="scale({scale:.2f})"/></g>'
            )
        out.append(
            f'<g><animateTransform attributeName="transform" type="translate" values="{path}" '
            f'dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>{inner}</g>'
        )
    return "\n    ".join(out)


def build(season: str) -> str:
    cfg = SEASONS[season]
    a, b, c = cfg["blobs"]
    rng = random.Random(season)  # deterministic per season -> no daily churn
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Aman Singh">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#07070f"/>
      <stop offset="0.55" stop-color="#120a2a"/>
      <stop offset="1" stop-color="#04121f"/>
    </linearGradient>
    <radialGradient id="blobA"><stop offset="0" stop-color="{a}" stop-opacity="0.7"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
    <radialGradient id="blobB"><stop offset="0" stop-color="{b}" stop-opacity="0.5"/><stop offset="1" stop-color="{b}" stop-opacity="0"/></radialGradient>
    <radialGradient id="blobC"><stop offset="0" stop-color="{c}" stop-opacity="0.45"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>
    <linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1200" y2="0" spreadMethod="repeat">
      <stop offset="0" stop-color="#a78bfa"/>
      <stop offset="0.25" stop-color="#00E5FF"/>
      <stop offset="0.5" stop-color="#ffffff"/>
      <stop offset="0.75" stop-color="#FF4FA3"/>
      <stop offset="1" stop-color="#a78bfa"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="-1200 0;0 0" dur="6s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="line" x1="0" x2="1">
      <stop offset="0" stop-color="#7C3AED" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#00E5FF"/>
      <stop offset="1" stop-color="#FF4FA3" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity="0.045"/>
    </pattern>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>{SHAPES}  </defs>

  <style>
    .title {{ font: 800 92px 'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif; letter-spacing: -2px;
             opacity: 0; animation: rise 1s cubic-bezier(.2,.8,.2,1) .2s forwards; }}
    .sub {{ font: 500 24px 'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif; fill: #c9d1d9; letter-spacing: 6px;
           opacity: 0; animation: rise 1s cubic-bezier(.2,.8,.2,1) .7s forwards; }}
    .prompt {{ font: 500 18px 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; fill: #8b949e;
              opacity: 0; animation: rise 1s ease 1.2s forwards; }}
    .tag {{ font: 500 13px 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; fill: #8b949e; opacity: .8; }}
    .accent {{ fill: #00E5FF }} .accent2 {{ fill: #a78bfa }}
    .cursor {{ fill: #00E5FF; animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0 }} }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px) }} to {{ opacity: 1; transform: translateY(0) }} }}
    .scan {{ animation: scan 4s ease-in-out infinite; }}
    @keyframes scan {{ 0%,100% {{ transform: translateX(-300px); opacity: 0 }} 50% {{ opacity: 1 }} 100% {{ transform: translateX(300px) }} }}
  </style>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>

    <ellipse cx="250" cy="80" rx="320" ry="220" fill="url(#blobA)">
      <animate attributeName="cx" values="250;420;250" dur="14s" repeatCount="indefinite"/>
      <animate attributeName="cy" values="80;160;80" dur="11s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="950" cy="260" rx="300" ry="200" fill="url(#blobB)">
      <animate attributeName="cx" values="950;780;950" dur="12s" repeatCount="indefinite"/>
      <animate attributeName="cy" values="260;190;260" dur="9s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="640" cy="330" rx="260" ry="160" fill="url(#blobC)">
      <animate attributeName="cx" values="640;520;760;640" dur="16s" repeatCount="indefinite"/>
    </ellipse>

    <!-- {season} particles -->
    {particles(cfg, rng)}

    <text class="title" x="600" y="160" text-anchor="middle" fill="url(#name)">Aman Singh</text>
    <text class="sub" x="600" y="210" text-anchor="middle">SOFTWARE ENGINEER · BUILDER · TINKERER</text>
    <rect x="450" y="232" width="300" height="2" fill="url(#line)" class="scan"/>
    <text class="prompt" x="600" y="280" text-anchor="middle"><tspan class="accent2">aman@github</tspan>:<tspan class="accent">~</tspan>$ building something new<tspan class="cursor">▍</tspan></text>
    <text class="tag" x="1176" y="322" text-anchor="end">{cfg["tag"]}</text>
  </g>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="#ffffff" stroke-opacity="0.08"/>
</svg>
"""


if __name__ == "__main__":
    season = os.environ.get("SEASON") or season_for(datetime.date.today())
    out = sys.argv[1] if len(sys.argv) > 1 else "assets/header.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write(build(season))
    print(f"wrote {out} ({season})")
