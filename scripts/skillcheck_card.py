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


def render(theme: str) -> str:
    dark = theme == "dark"
    bg = "#0d1117" if dark else "#ffffff"
    border = "#30363d" if dark else "#d0d7de"
    fg = "#e6edf3" if dark else "#1f2328"
    muted = "#8b949e" if dark else "#656d76"
    accent = "#2f81f7" if dark else "#0969da"
    pill_bg = "#8957e5" if dark else "#fbefff"
    pill_fg = "#ffffff" if dark else "#8250df"
    star_on = "#e3b341"
    star_off = "#30363d" if dark else "#d0d7de"
    ok = "#3fb950" if dark else "#1a7f37"

    W, H, x = 480, 168, 24
    pill_text = f"Level {LEVEL} · {TITLE}"
    pill_w = 14 + 8 * len(pill_text) + 20

    stars = "".join(
        f'<path transform="translate({x + i * 24},{H - 68})" fill="{star_on if i < LEVEL else star_off}" d="{STAR}"/>'
        for i in range(MAX_LEVEL)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Programmers skill check Level {LEVEL} ({TITLE}) for @{LOGIN}">
  <style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}</style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{bg}" stroke="{border}"/>
  <!-- header -->
  <text x="{x}" y="38" font-size="18" fill="{fg}"><tspan fill="{muted}" font-weight="400">programmers/</tspan><tspan font-weight="700" fill="{accent}">skill-check</tspan></text>
  <text x="{x}" y="62" font-size="12.5" fill="{muted}">코딩테스트 역량 인증 · {escape(NAME)} (GitHub 연동 계정)</text>
  <!-- level pill -->
  <g transform="translate({W - 24 - pill_w},18)">
    <rect width="{pill_w}" height="26" rx="13" fill="{pill_bg}"/>
    <path transform="translate(11,5)" fill="{pill_fg}" d="{TROPHY}"/>
    <text x="30" y="17.5" font-size="12.5" font-weight="700" fill="{pill_fg}">{pill_text}</text>
  </g>
  <!-- divider -->
  <line x1="{x}" y1="{H - 84}" x2="{W - 24}" y2="{H - 84}" stroke="{border}"/>
  <!-- level stars -->
  {stars}
  <text x="{x + MAX_LEVEL * 24 + 6}" y="{H - 55.5}" font-size="13" fill="{fg}" font-weight="600">Level {LEVEL} / {MAX_LEVEL}</text>
  <!-- footer line -->
  <g transform="translate({x},{H - 22})">
    <path fill="{ok}" d="{CHECK}" transform="translate(0,-11)"/>
    <text x="22" y="1" font-size="12.5" fill="{fg}">@{LOGIN} · 최고 레벨({TITLE}) 달성 · school.programmers.co.kr</text>
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
