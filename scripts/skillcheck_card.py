# /// script
# requires-python = ">=3.11"
# ///
"""Render a static Programmers skill-check level card (light + dark).

Programmers skill-check results are only visible to the logged-in owner and
have no public API, so this card is hand-maintained: edit LEVEL / TITLE and
re-run.

Usage:
    uv run scripts/skillcheck_card.py --out assets/programmers-skillcheck.svg
"""

from __future__ import annotations

import argparse
import base64
import os
from xml.sax.saxutils import escape

STAR = "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"
TROPHY = "M3.217 6.962A3.75 3.75 0 0 1 0 3.25v-.5C0 1.56.56 1 1.75 1h1.5c.058-.5.496-1 1-1h7.5c.504 0 .942.5 1 1h1.5C15.44 1 16 1.56 16 2.75v.5a3.75 3.75 0 0 1-3.217 3.712 3.75 3.75 0 0 1-3.033 2.483V12h2.25a.75.75 0 0 1 0 1.5h-6a.75.75 0 0 1 0-1.5h2.25V9.445a3.75 3.75 0 0 1-3.033-2.483ZM3.25 2.5h-1.5a.25.25 0 0 0-.25.25v.5a2.25 2.25 0 0 0 1.75 2.19Zm9.5 0v2.94a2.25 2.25 0 0 0 1.75-2.19v-.5a.25.25 0 0 0-.25-.25Z"
CHECK = "M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"

LEVEL = 5
MAX_LEVEL = 5
TITLE = "Master"
LOGIN = "sxngt"
NAME = "윤상현"
EMBLEM = os.path.join(os.path.dirname(__file__), "..", "assets", "programmers-level5.png")


def emblem_uri() -> str:
    with open(EMBLEM, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def render(theme: str) -> str:
    dark = theme == "dark"
    bg = "#0d1117" if dark else "#ffffff"
    tile = "#161b22" if dark else "#f6f8fa"
    border = "#30363d" if dark else "#d0d7de"
    fg = "#e6edf3" if dark else "#1f2328"
    muted = "#8b949e" if dark else "#656d76"
    accent = "#2f81f7" if dark else "#0969da"
    purple = "#a371f7" if dark else "#8250df"
    star_on = "#e3b341"
    star_off = "#30363d" if dark else "#d0d7de"
    ok = "#3fb950" if dark else "#1a7f37"

    W, H, x = 480, 218, 24
    cw = W - 2 * x
    e = 64  # emblem size, sits in the hero row on the right

    # Three tiles: level, max level, stars
    gap, n = 10, 3
    tw = (cw - gap * (n - 1)) / n
    star_row = "".join(
        f'<path transform="translate({tw / 2 - 5 * 9 + i * 18:.1f},18) scale(0.85)" fill="{star_on if i < LEVEL else star_off}" d="{STAR}"/>'
        for i in range(MAX_LEVEL)
    )
    tiles = [
        (f'<text x="{tw / 2:.1f}" y="30" font-size="21" font-weight="800" fill="{purple}" text-anchor="middle">Lv.{LEVEL}</text>', "level"),
        (f'<text x="{tw / 2:.1f}" y="30" font-size="21" font-weight="800" fill="{fg}" text-anchor="middle">{LEVEL} / {MAX_LEVEL}</text>', "max level"),
        (star_row, "skill check"),
    ]
    tile_svg = "".join(
        f'<g transform="translate({x + i * (tw + gap):.1f},94)">'
        f'<rect width="{tw:.1f}" height="58" rx="8" fill="{tile}" stroke="{border}"/>{body}'
        f'<text x="{tw / 2:.1f}" y="48" font-size="10.5" font-weight="600" fill="{muted}" text-anchor="middle" letter-spacing="0.6">{label.upper()}</text></g>'
        for i, (body, label) in enumerate(tiles)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Programmers skill check Level {LEVEL} ({TITLE}) for @{LOGIN}">
  <style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}</style>
  <clipPath id="card"><rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10"/></clipPath>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{bg}" stroke="{border}"/>
  <rect clip-path="url(#card)" x="0" y="0" width="6" height="{H}" fill="{purple}"/>
  <!-- header -->
  <text x="{x}" y="34" font-size="15" fill="{fg}"><tspan fill="{muted}" font-weight="400">programmers/</tspan><tspan font-weight="700" fill="{accent}">skill-check</tspan></text>
  <text x="{W - x}" y="34" font-size="12" fill="{muted}" text-anchor="end">코딩테스트 역량 인증</text>
  <!-- hero: title + emblem -->
  <text x="{x}" y="76" font-size="30" font-weight="800" fill="{purple}">{TITLE}</text>
  <text x="{x + 8 * len(TITLE) + 86}" y="76" font-size="13" fill="{muted}">최고 레벨</text>
  <image x="{W - x - e}" y="40" width="{e}" height="{e}" href="{emblem_uri()}"/>
  <!-- tiles -->
  {tile_svg}
  <!-- footer -->
  <g transform="translate({x},{H - 22})">
    <path fill="{ok}" d="{CHECK}" transform="translate(0,-11)"/>
    <text x="22" y="1" font-size="12" fill="{muted}">@{LOGIN} ({escape(NAME)}) · Level {LEVEL} {TITLE} · school.programmers.co.kr</text>
  </g>
</svg>
"""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="assets/programmers-skillcheck.svg")
    args = p.parse_args()
    for t in ("light", "dark"):
        out = args.out.replace(".svg", f"-{t}.svg")
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(render(t))
        print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
