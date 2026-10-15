# /// script
# requires-python = ">=3.11"
# dependencies = ["curl_cffi>=0.7"]
# ///
"""Render a solved.ac (Baekjoon Online Judge) profile card SVG.

Uses the public solved.ac API (no auth) for tier / rating / solved count /
class / streak / rank, embeds the official tier icon as base64, and writes a
light + dark SVG plus a JSON copy.

Usage:
    uv run scripts/solvedac_card.py --handle injefol --out assets/solvedac-card.svg
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from curl_cffi import requests

API = "https://solved.ac/api/v3"
TIER_ICON = "https://static.solved.ac/tier_small/{tier}.svg"

TIER_GROUPS = ["Unrated", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ruby", "Master"]
TIER_COLORS = {
    "Unrated": "#2d2d2d",
    "Bronze": "#ad5600",
    "Silver": "#435f7a",
    "Gold": "#ec9a00",
    "Platinum": "#27e2a4",
    "Diamond": "#00b4fc",
    "Ruby": "#ff0062",
    "Master": "#b300e0",
}
ROMAN = ["", "V", "IV", "III", "II", "I"]


def tier_name(tier: int) -> tuple[str, str]:
    """solved.ac tier int (0-31) -> (display name, group)."""
    if tier <= 0:
        return "Unrated", "Unrated"
    if tier >= 31:
        return "Master", "Master"
    group = TIER_GROUPS[(tier - 1) // 5 + 1]
    return f"{group} {ROMAN[(tier - 1) % 5 + 1]}", group


@dataclass
class Card:
    handle: str
    tier: int
    rating: int
    solved: int
    klass: int
    class_deco: str
    max_streak: int
    rank: int
    bio: str
    icon_uri: str = ""


def fetch(handle: str) -> Card:
    # solved.ac sits behind a Cloudflare bot challenge that rejects plain HTTP
    # clients from datacenter IPs (GitHub Actions). curl_cffi impersonates a
    # real browser's TLS/HTTP2 fingerprint, which the managed challenge accepts.
    s = requests.Session(impersonate="chrome", timeout=30)
    r = s.get(f"{API}/user/show", params={"handle": handle}, headers={"Accept": "application/json"})
    if r.status_code != 200:
        print(f"::error::solved.ac API {r.status_code} for {handle}: {r.text[:200]!r}")
        raise RuntimeError(f"solved.ac API returned {r.status_code}")
    u = r.json()
    icon = ""
    try:
        ri = s.get(TIER_ICON.format(tier=u["tier"]))
        if ri.status_code == 200:
            icon = "data:image/svg+xml;base64," + base64.b64encode(ri.content).decode()
    except Exception as e:  # icon is decorative; never fail the card on it
        print(f"warning: tier icon fetch failed: {e}", file=sys.stderr)
    return Card(
        handle=u["handle"],
        tier=int(u.get("tier", 0)),
        rating=int(u.get("rating", 0)),
        solved=int(u.get("solvedCount", 0)),
        klass=int(u.get("class", 0)),
        class_deco=u.get("classDecoration", "none") or "none",
        max_streak=int(u.get("maxStreak", 0)),
        rank=int(u.get("rank", 0)),
        bio=u.get("bio", "") or "",
        icon_uri=icon,
    )


def fmt(n: int) -> str:
    return f"{n:,}"


def truncate(s: str, limit: int) -> str:
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


CHECK = "M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"
FLAME = "M9.533.753V.752c.217 2.385 1.463 3.626 2.653 4.81C13.37 6.74 14.498 7.863 14.498 10c0 3.5-3 6-6.5 6S1.5 13.512 1.5 10c0-1.298.536-2.56 1.425-3.286.376-.308.862 0 .862.5 0 .917.3 1.58.75 1.95.14.114.31.108.4-.05C5.667 8.09 6 6.5 6 5.5c0-2.148 1.213-3.783 3.1-4.891.397-.233.433.23.433.144Z"
TROPHY = "M3.217 6.962A3.75 3.75 0 0 1 0 3.25v-.5C0 1.56.56 1 1.75 1h1.5c.058-.5.496-1 1-1h7.5c.504 0 .942.5 1 1h1.5C15.44 1 16 1.56 16 2.75v.5a3.75 3.75 0 0 1-3.217 3.712 3.75 3.75 0 0 1-3.033 2.483V12h2.25a.75.75 0 0 1 0 1.5h-6a.75.75 0 0 1 0-1.5h2.25V9.445a3.75 3.75 0 0 1-3.033-2.483ZM3.25 2.5h-1.5a.25.25 0 0 0-.25.25v.5a2.25 2.25 0 0 0 1.75 2.19Zm9.5 0v2.94a2.25 2.25 0 0 0 1.75-2.19v-.5a.25.25 0 0 0-.25-.25Z"


def tiles(items, x0, y, width, fg, muted, bg_tile, border):
    """Equal-width stat tiles: big value, small caption. Centered text, so no width guessing."""
    n = len(items)
    gap = 10
    tw = (width - gap * (n - 1)) / n
    out = []
    for i, (value, label, col) in enumerate(items):
        tx = x0 + i * (tw + gap)
        out.append(
            f'<g transform="translate({tx:.1f},{y})">'
            f'<rect width="{tw:.1f}" height="58" rx="8" fill="{bg_tile}" stroke="{border}"/>'
            f'<text x="{tw / 2:.1f}" y="30" font-size="21" font-weight="800" fill="{col}" text-anchor="middle">{escape(str(value))}</text>'
            f'<text x="{tw / 2:.1f}" y="48" font-size="10.5" font-weight="600" fill="{muted}" text-anchor="middle" letter-spacing="0.6">{escape(label.upper())}</text>'
            f'</g>'
        )
    return "".join(out)


def render(d: Card, theme: str) -> str:
    dark = theme == "dark"
    bg = "#0d1117" if dark else "#ffffff"
    tile = "#161b22" if dark else "#f6f8fa"
    border = "#30363d" if dark else "#d0d7de"
    fg = "#e6edf3" if dark else "#1f2328"
    muted = "#8b949e" if dark else "#656d76"
    accent = "#2f81f7" if dark else "#0969da"
    ok = "#3fb950" if dark else "#1a7f37"

    name, group = tier_name(d.tier)
    tcol = TIER_COLORS[group]
    W, H, x = 480, 218, 24
    cw = W - 2 * x
    klass = f"{d.klass}" + ("" if d.class_deco == "none" else f"+")
    stat_items = [
        (fmt(d.solved), "solved", fg),
        (klass, "class", accent),
        (f"#{fmt(d.rank)}", "rank", fg),
        (f"{d.max_streak}d", "max streak", "#f0883e"),
    ]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="solved.ac {escape(name)} card for {escape(d.handle)}">
  <style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}</style>
  <clipPath id="card"><rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10"/></clipPath>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{bg}" stroke="{border}"/>
  <rect clip-path="url(#card)" x="0" y="0" width="6" height="{H}" fill="{tcol}"/>
  <!-- header -->
  <text x="{x}" y="34" font-size="15" fill="{fg}"><tspan fill="{muted}" font-weight="400">solved.ac/</tspan><tspan font-weight="700" fill="{accent}">{escape(d.handle)}</tspan></text>
  <text x="{W - x}" y="34" font-size="12" fill="{muted}" text-anchor="end">Baekjoon Online Judge</text>
  <!-- hero: tier + rating -->
  <text x="{x}" y="76" font-size="30" font-weight="800" fill="{tcol}">{escape(name)}</text>
  <text x="{W - x}" y="54" font-size="10.5" font-weight="600" fill="{muted}" text-anchor="end" letter-spacing="0.6">RATING</text>
  <text x="{W - x}" y="76" font-size="26" font-weight="800" fill="{fg}" text-anchor="end">{d.rating}</text>
  <!-- stat tiles -->
  {tiles(stat_items, x, 94, cw, fg, muted, tile, border)}
  <!-- footer -->
  <g transform="translate({x},{H - 22})">
    <path fill="{ok}" d="{CHECK}" transform="translate(0,-11)"/>
    <text x="22" y="1" font-size="12" fill="{muted}">@{escape(d.handle)} · {escape(name)} · {fmt(d.solved)} problems solved on solved.ac</text>
  </g>
</svg>
"""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--handle", default=os.environ.get("SOLVEDAC_HANDLE", "injefol"))
    p.add_argument("--out", default="assets/solvedac-card.svg")
    args = p.parse_args()

    json_out = os.path.splitext(args.out)[0] + ".json"
    try:
        d = fetch(args.handle)
    except Exception as e:
        if os.path.exists(json_out):
            # Keep the last good card rather than breaking the README.
            print(f"::warning::solved.ac fetch failed ({type(e).__name__}: {e}); keeping existing card")
            return 0
        print(f"::error::solved.ac fetch failed: {type(e).__name__}: {e}")
        raise
    os.makedirs(os.path.dirname(json_out) or ".", exist_ok=True)
    name, group = tier_name(d.tier)
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(
            {
                "handle": d.handle,
                "url": f"https://solved.ac/profile/{d.handle}",
                "tier": d.tier,
                "tierName": name,
                "rating": d.rating,
                "solvedCount": d.solved,
                "class": d.klass,
                "classDecoration": d.class_deco,
                "maxStreak": d.max_streak,
                "rank": d.rank,
                "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            },
            f, ensure_ascii=False, indent=2,
        )
        f.write("\n")
    print(f"wrote {json_out}")
    for t in ("light", "dark"):
        out = args.out.replace(".svg", f"-{t}.svg")
        with open(out, "w", encoding="utf-8") as f:
            f.write(render(d, t))
        print(f"wrote {out}: {name} rating={d.rating} solved={d.solved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
