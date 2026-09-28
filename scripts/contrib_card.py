# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27"]
# ///
"""Render a "contributor card" SVG for one repository.

Fetches live stars/forks/description from the GitHub API, verifies that
LOGIN is actually listed as a contributor, counts merged PRs, and writes an
SVG that can be embedded in a profile README.

Usage:
    GITHUB_TOKEN=... uv run scripts/contrib_card.py
    uv run scripts/contrib_card.py --repo mujocolab/mjlab --login sxngt --out assets/mjlab-card.svg
"""

from __future__ import annotations

import argparse
import base64
import html
import os
import re
import sys
from dataclasses import dataclass
from xml.sax.saxutils import escape

import httpx

API = "https://api.github.com"


@dataclass
class CardData:
    full_name: str
    description: str
    stars: int
    forks: int
    language: str
    login: str
    is_contributor: bool
    merged_prs: int
    commits: int
    og_data_uri: str = ""


def fetch(repo: str, login: str, token: str | None) -> CardData:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with httpx.Client(base_url=API, headers=headers, timeout=30) as c:
        r = c.get(f"/repos/{repo}")
        r.raise_for_status()
        meta = r.json()

        # Contributor verification: walk the contributors list until the login shows up.
        is_contributor = False
        commits = 0
        page = 1
        while page <= 20:
            rc = c.get(f"/repos/{repo}/contributors", params={"per_page": 100, "page": page, "anon": "false"})
            rc.raise_for_status()
            rows = rc.json()
            if not rows:
                break
            for row in rows:
                if row.get("login", "").lower() == login.lower():
                    is_contributor = True
                    commits = int(row.get("contributions", 0))
                    break
            if is_contributor:
                break
            page += 1

        rp = c.get("/search/issues", params={"q": f"repo:{repo} is:pr is:merged author:{login}", "per_page": 1})
        merged = int(rp.json().get("total_count", 0)) if rp.status_code == 200 else 0

    # Repo's social-preview image. If the maintainers uploaded a custom one in
    # repo settings, the page's og:image points to repository-images.githubusercontent.com;
    # otherwise GitHub serves an auto-generated card. Embedded as base64 because
    # GitHub's camo proxy blocks external hrefs inside SVGs in READMEs.
    og_uri = ""
    og_url = f"https://opengraph.githubassets.com/card/{repo}"
    try:
        page = httpx.get(f"https://github.com/{repo}", timeout=30, follow_redirects=True,
                         headers={"User-Agent": "contrib-card"})
        m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', page.text) if page.status_code == 200 else None
        if m:
            og_url = html.unescape(m.group(1))
        r = httpx.get(og_url, timeout=30, follow_redirects=True)
        if r.status_code == 200 and r.content:
            mime = r.headers.get("content-type", "image/png").split(";")[0]
            og_uri = f"data:{mime};base64," + base64.b64encode(r.content).decode()
            print(f"og image: {og_url} ({len(r.content)} bytes, {mime})")
    except httpx.HTTPError as e:
        print(f"warning: could not fetch OG image: {e}", file=sys.stderr)

    return CardData(
        og_data_uri=og_uri,
        full_name=meta["full_name"],
        description=meta.get("description") or "",
        stars=int(meta.get("stargazers_count", 0)),
        forks=int(meta.get("forks_count", 0)),
        language=meta.get("language") or "",
        login=login,
        is_contributor=is_contributor,
        merged_prs=merged,
        commits=commits,
    )


def fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n / 1_000:.1f}k".replace(".0k", "k")
    return str(n)


def truncate(s: str, limit: int) -> str:
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


STAR = "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"
FORK = "M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"
MERGE = "M5.45 5.154A4.25 4.25 0 0 0 9.25 7.5h1.378a2.251 2.251 0 1 1 0 1.5H9.25A5.734 5.734 0 0 1 5 7.123v3.505a2.25 2.25 0 1 1-1.5 0V5.372a2.25 2.25 0 1 1 1.95-.218ZM4.25 13.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm8.5-4.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM5 3.25a.75.75 0 1 0 0 .005V3.25Z"
CHECK = "M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"


def render(d: CardData, theme: str) -> str:
    dark = theme == "dark"
    bg = "#0d1117" if dark else "#ffffff"
    border = "#30363d" if dark else "#d0d7de"
    fg = "#e6edf3" if dark else "#1f2328"
    muted = "#8b949e" if dark else "#656d76"
    accent = "#2f81f7" if dark else "#0969da"
    ok_bg = "#238636" if dark else "#dafbe1"
    ok_fg = "#ffffff" if dark else "#1a7f37"
    warn_bg = "#9e6a03" if dark else "#fff8c5"
    warn_fg = "#ffffff" if dark else "#9a6700"
    merge_col = "#a371f7" if dark else "#8250df"

    owner, name = d.full_name.split("/", 1)
    desc = escape(truncate(d.description, 60))
    pill_bg, pill_fg, pill_text = (ok_bg, ok_fg, "Contributor") if d.is_contributor else (warn_bg, warn_fg, "Not verified")
    pill_w = 14 + 8 * len(pill_text) + 20

    stats = [
        (STAR, fmt(d.stars), "#e3b341"),
        (FORK, fmt(d.forks), muted),
    ]
    contrib_line = f"@{escape(d.login)} · {d.merged_prs} merged PR{'s' if d.merged_prs != 1 else ''} · {d.commits} commit{'s' if d.commits != 1 else ''}"

    W = 480
    IMG_H = 240 if d.og_data_uri else 0  # OG image is 1200x600 (2:1)
    H = IMG_H + 168
    x = 24
    og_block = (
        f'<clipPath id="og"><rect x="0.5" y="0.5" width="{W - 1}" height="{IMG_H + 10}" rx="10"/></clipPath>'
        f'<image clip-path="url(#og)" x="0" y="0" width="{W}" height="{IMG_H}" preserveAspectRatio="xMidYMid slice" href="{d.og_data_uri}"/>'
        f'<line x1="0.5" y1="{IMG_H + 0.5}" x2="{W - 0.5}" y2="{IMG_H + 0.5}" stroke="{border}"/>'
    ) if d.og_data_uri else ""
    stat_items = []
    sx = x
    for path, label, col in stats:
        stat_items.append(
            f'<g transform="translate({sx},{H - 68})">'
            f'<path fill="{col}" d="{path}"/>'
            f'<text x="22" y="12.5" font-size="13" fill="{fg}" font-weight="600">{label}</text></g>'
        )
        sx += 22 + 8.5 * len(label) + 22
    if d.language:
        stat_items.append(
            f'<g transform="translate({sx},{H - 68})">'
            f'<circle cx="7" cy="7.5" r="6" fill="{accent}"/>'
            f'<text x="20" y="12.5" font-size="13" fill="{fg}" font-weight="600">{escape(d.language)}</text></g>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(d.full_name)} contributor card for @{escape(d.login)}">
  <style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}</style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{bg}" stroke="{border}"/>
  {og_block}
  <!-- repo header -->
  <text x="{x}" y="{IMG_H + 38}" font-size="18" fill="{fg}"><tspan fill="{muted}" font-weight="400">{escape(owner)}/</tspan><tspan font-weight="700" fill="{accent}">{escape(name)}</tspan></text>
  <text x="{x}" y="{IMG_H + 62}" font-size="12.5" fill="{muted}">{desc}</text>
  <!-- contributor pill -->
  <g transform="translate({W - 24 - pill_w},{IMG_H + 18})">
    <rect width="{pill_w}" height="26" rx="13" fill="{pill_bg}"/>
    <path transform="translate(11,5)" fill="{pill_fg}" d="{CHECK}"/>
    <text x="30" y="17.5" font-size="12.5" font-weight="700" fill="{pill_fg}">{pill_text}</text>
  </g>
  <!-- divider -->
  <line x1="{x}" y1="{H - 84}" x2="{W - 24}" y2="{H - 84}" stroke="{border}"/>
  <!-- stats row -->
  {''.join(stat_items)}
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="{border}"/>
  <!-- contribution line -->
  <g transform="translate({x},{H - 22})">
    <path fill="{merge_col}" d="{MERGE}" transform="translate(0,-11)"/>
    <text x="22" y="1" font-size="12.5" fill="{fg}">{contrib_line}</text>
  </g>
</svg>
"""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default=os.environ.get("CARD_REPO", "mujocolab/mjlab"))
    p.add_argument("--login", default=os.environ.get("CARD_LOGIN", "sxngt"))
    p.add_argument("--out", default="assets/mjlab-card.svg")
    p.add_argument("--theme", choices=["light", "dark", "both"], default="both")
    args = p.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    data = fetch(args.repo, args.login, token)
    if not data.is_contributor:
        print(f"warning: {args.login} not found in contributors of {args.repo}", file=sys.stderr)

    themes = ["light", "dark"] if args.theme == "both" else [args.theme]
    for t in themes:
        out = args.out if args.theme != "both" else args.out.replace(".svg", f"-{t}.svg")
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(render(data, t))
        print(f"wrote {out}: ★{data.stars} ⑂{data.forks} contributor={data.is_contributor} prs={data.merged_prs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
