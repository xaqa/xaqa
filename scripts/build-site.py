#!/usr/bin/env python3
"""Build the profile site: a still of the contribution art.

Inputs:

  * the painted days, read off the filenames in ``data/`` (``YYYY-MM-DD.txt``)
  * the live repo numbers, read from the GitHub API when ``GITHUB_TOKEN`` is set

Output is one self-contained ``_site/index.html``: inline SVG, no JavaScript,
no third-party assets, no runtime API calls. If the API call fails the page is
still written without the live numbers - a stale number would be worse than a
missing one.

The canvas geometry mirrors GitHub's: 53 columns x 7 rows, oldest column first,
Sunday on top, column 52 holding the current week. Cells after today are
skipped, exactly like the graph does.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
DATA = ROOT / "data"

COLS, ROWS = 53, 7
CELL, GAP, PAD = 11, 3, 4
# keep in sync with LEVELS in scripts/commit-art.py
COMMITS_PER_CELL = 5

DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.txt$")
LAST_PAGE_RE = re.compile(r'[?&]page=(\d+)>; rel="last"')

PAGE = Template(
    """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>xaqa</title>
<style>
:root{
  --bg:#ffffff; --fg:#1f2328; --muted:#59636e; --empty:#ebedf0;
  --cell:#216e39; --today:#57606a; --rule:#d1d9e0;
}
@media (prefers-color-scheme: dark){
  :root{ --bg:#0d1117; --fg:#e6edf3; --muted:#8b949e; --empty:#161b22;
         --cell:#39d353; --today:#8b949e; --rule:#30363d; }
}
*{box-sizing:border-box}
body{margin:0;padding:56px 24px;background:var(--bg);color:var(--fg);
  font:14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
main{max-width:760px;margin:0 auto}
h1{font-size:18px;font-weight:600;margin:0 0 12px}
p{margin:0 0 32px;color:var(--muted)}
svg{width:100%;height:auto;display:block}
.cell{fill:var(--empty)}
.on{fill:var(--cell)}
.today{stroke:var(--today);stroke-width:1.2}
dl{display:flex;flex-wrap:wrap;gap:28px;margin:36px 0 0;padding:24px 0 0;
  border-top:1px solid var(--rule)}
dt{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.06em}
dd{margin:4px 0 0;font-size:16px;font-variant-numeric:tabular-nums}
footer{margin-top:32px;color:var(--muted);font-size:12px}
a{color:inherit}
</style>
</head>
<body>
<main>
<h1>xaqa</h1>
<p>$painted days of this repository's contribution graph are painted on purpose -
$per backdated commits each - and together they spell <strong>XAQA</strong>.
This page is a still of that graph; the live one is on the profile.</p>
$svg
<dl>
$stats
</dl>
<footer>built $stamp from <code>data/</code> &middot;
<a href="https://github.com/xaqa">github.com/xaqa</a></footer>
</main>
</body>
</html>
"""
)


def painted_days() -> list[dt.date]:
    days: list[dt.date] = []
    for path in sorted(DATA.glob("*.txt")):
        match = DATE_RE.match(path.name)
        if match:
            days.append(dt.date(*(int(part) for part in match.groups())))
    return days


def canvas_start(today: dt.date) -> dt.date:
    """Sunday of the week 52 weeks back, so today lands in the last column."""
    this_sunday = today - dt.timedelta(days=(today.weekday() + 1) % 7)
    return this_sunday - dt.timedelta(weeks=COLS - 1)


def request(path: str) -> urllib.request.Request:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "xaqa-profile-site",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(f"https://api.github.com{path}", headers=headers)


def repo_stats(repo: str, branch: str) -> dict[str, int]:
    """Live numbers, or an empty dict if the API is unreachable."""
    stats: dict[str, int] = {}
    try:
        with urllib.request.urlopen(request(f"/repos/{repo}"), timeout=20) as res:
            body = json.loads(res.read())
        stats["stars"] = body["stargazers_count"]
        stats["forks"] = body["forks_count"]
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
        print(f"warn: repo lookup failed ({exc}); no stars or forks on the page")

    try:
        url = f"/repos/{repo}/commits?per_page=1&sha={branch}"
        with urllib.request.urlopen(request(url), timeout=20) as res:
            link = res.headers.get("Link", "")
            res.read()
        match = LAST_PAGE_RE.search(link)
        stats["commits"] = int(match.group(1)) if match else 1
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"warn: commit count failed ({exc}); no commit total on the page")
    return stats


def canvas_svg(days: list[dt.date], start: dt.date, today: dt.date) -> str:
    painted = set(days)
    width = PAD * 2 + COLS * CELL + (COLS - 1) * GAP
    height = PAD * 2 + ROWS * CELL + (ROWS - 1) * GAP
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Contribution canvas spelling XAQA">'
    ]
    for col in range(COLS):
        for row in range(ROWS):
            day = start + dt.timedelta(days=col * 7 + row)
            if day > today:
                continue
            classes = ["cell"]
            if day in painted:
                classes.append("on")
            if day == today:
                classes.append("today")
            x = PAD + col * (CELL + GAP)
            y = PAD + row * (CELL + GAP)
            parts.append(
                f'<rect class="{" ".join(classes)}" x="{x}" y="{y}" '
                f'width="{CELL}" height="{CELL}" rx="2.5"/>'
            )
    parts.append("</svg>")
    return "\n".join(parts)


def stat_items(days: list[dt.date], stats: dict[str, int]) -> str:
    items = [
        ("painted days", len(days)),
        ("art commits", len(days) * COMMITS_PER_CELL),
        ("repo commits", stats.get("commits")),
        ("stars", stats.get("stars")),
        ("forks", stats.get("forks")),
    ]
    return "\n".join(
        f"<div><dt>{label}</dt><dd>{value}</dd></div>"
        for label, value in items
        if value is not None
    )


def main() -> None:
    repo = os.environ.get("GITHUB_REPOSITORY", "xaqa/xaqa")
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    today = dt.datetime.now(dt.timezone.utc).date()
    days = painted_days()
    start = canvas_start(today)
    inside = [day for day in days if start <= day <= today]
    outside = len(days) - len(inside)
    if outside:
        print(f"note: {outside} painted day(s) sit outside the trailing canvas")

    html = PAGE.substitute(
        painted=len(inside),
        per=COMMITS_PER_CELL,
        svg=canvas_svg(inside, start, today),
        stats=stat_items(inside, repo_stats(repo, branch)),
        stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )
    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {SITE / 'index.html'} ({len(html)} bytes, {len(inside)} painted cells)")


if __name__ == "__main__":
    main()
