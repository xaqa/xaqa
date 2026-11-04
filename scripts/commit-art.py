#!/usr/bin/env python3
"""Paint text into the GitHub contribution graph via backdated commits.

Commits only count toward the graph when ALL of these hold:
  * the repository is public and is not a fork
  * the commit's author email is attached to your GitHub account
  * the commit is on the repository's default branch
  * the commit date is inside the trailing 12-month window

The grid is always 53 columns x 7 rows, oldest column first, Sunday top.
Column 52 is the current week, so cells later than today are skipped
(they would land in the future and stay invisible until that day arrives).

Usage:
  python3 scripts/commit-art.py "X A Q A" --preview
  python3 scripts/commit-art.py "X A Q A" --dry-run
  python3 scripts/commit-art.py "X A Q A" --name xaqa \
      --email 307261345+xaqa@users.noreply.github.com --push
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

COLS = 53
ROWS = 7
# commits per intensity level; GitHub buckets by relative daily volume, so
# 4 distinct shades need 4 distinct counts. Text glyphs are all level 4, so a
# 66-cell "X A Q A" costs 66 x 5 = 330 commits. Raise the top value if your
# normal busiest day is already above it, or the art washes out.
LEVELS = (0, 1, 2, 3, 5)
FILL = {0: ".", 1: ":", 2: "+", 3: "#", 4: "@"}
# 12:00 UTC keeps a commit inside the same calendar day for every viewer
# timezone from UTC-11 to UTC+11.
HOUR = 12

FONT = {
    " ": ("...", "...", "...", "...", "...", "...", "..."),
    "A": (".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"),
    "B": ("XXXX.", "X...X", "X...X", "XXXX.", "X...X", "X...X", "XXXX."),
    "C": (".XXX.", "X...X", "X....", "X....", "X....", "X...X", ".XXX."),
    "D": ("XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."),
    "E": ("XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"),
    "F": ("XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "X...."),
    "G": (".XXX.", "X...X", "X....", "X.XXX", "X...X", "X...X", ".XXX."),
    "H": ("X...X", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"),
    "I": (".XXX.", "..X..", "..X..", "..X..", "..X..", "..X..", ".XXX."),
    "J": ("..XXX", "...X.", "...X.", "...X.", "...X.", "X..X.", ".XX.."),
    "K": ("X...X", "X..X.", "X.X..", "XX...", "X.X..", "X..X.", "X...X"),
    "L": ("X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"),
    "M": ("X...X", "XX.XX", "X.X.X", "X...X", "X...X", "X...X", "X...X"),
    "N": ("X...X", "XX..X", "X.X.X", "X..XX", "X...X", "X...X", "X...X"),
    "O": (".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."),
    "P": ("XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."),
    "Q": (".XXX.", "X...X", "X...X", "X...X", "X.X.X", "X..X.", ".XX.X"),
    "R": ("XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X...X"),
    "S": (".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."),
    "T": ("XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."),
    "U": ("X...X", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."),
    "V": ("X...X", "X...X", "X...X", "X...X", "X...X", ".X.X.", "..X.."),
    "W": ("X...X", "X...X", "X...X", "X.X.X", "X.X.X", "XX.XX", "X...X"),
    "X": ("X...X", "X...X", ".X.X.", "..X..", ".X.X.", "X...X", "X...X"),
    "Y": ("X...X", "X...X", ".X.X.", "..X..", "..X..", "..X..", "..X.."),
    "Z": ("XXXXX", "....X", "...X.", "..X..", ".X...", "X....", "XXXXX"),
    "0": (".XXX.", "X...X", "X..XX", "X.X.X", "XX..X", "X...X", ".XXX."),
    "1": ("..X..", ".XX..", "..X..", "..X..", "..X..", "..X..", ".XXX."),
    "2": (".XXX.", "X...X", "....X", "...X.", "..X..", ".X...", "XXXXX"),
    "3": ("XXXXX", "...X.", "..X..", "...X.", "....X", "X...X", ".XXX."),
    "4": ("...X.", "..XX.", ".X.X.", "X..X.", "XXXXX", "...X.", "...X."),
    "5": ("XXXXX", "X....", "XXXX.", "....X", "....X", "X...X", ".XXX."),
    "6": ("..XX.", ".X...", "X....", "XXXX.", "X...X", "X...X", ".XXX."),
    "7": ("XXXXX", "....X", "...X.", "..X..", ".X...", ".X...", ".X..."),
    "8": (".XXX.", "X...X", "X...X", ".XXX.", "X...X", "X...X", ".XXX."),
    "9": (".XXX.", "X...X", "X...X", ".XXXX", "....X", "...X.", ".XX.."),
}


def build_grid(text: str) -> list[list[int]]:
    """Render text into a COLS x ROWS grid of intensity levels."""
    glyphs = [FONT.get(ch, FONT[" "]) for ch in text.upper()]
    width = sum(len(g[0]) + 1 for g in glyphs) - 1
    if width > COLS:
        sys.exit(f"text is {width} cols wide, grid is {COLS}. shorten it.")

    grid = [[0] * COLS for _ in range(ROWS)]
    start = (COLS - width) // 2
    for row in range(ROWS):
        x = start
        for g in glyphs:
            for col in g[row]:
                if col == "X":
                    grid[row][x] = 4
                x += 1
            x += 1
    return grid


def week_start(today: dt.date) -> dt.date:
    """Most recent Sunday, i.e. the start of the grid's final column."""
    return today - dt.timedelta(days=(today.weekday() + 1) % 7)


def plan(grid: list[list[int]], today: dt.date) -> list[tuple[dt.datetime, int]]:
    """Map grid cells to (commit datetime, commit count)."""
    last_sunday = week_start(today)
    out: list[tuple[dt.datetime, int]] = []
    for col in range(COLS):
        sunday = last_sunday - dt.timedelta(weeks=COLS - 1 - col)
        for row in range(ROWS):
            level = grid[row][col]
            if not level:
                continue
            day = sunday + dt.timedelta(days=row)
            if day > today:
                continue
            for i in range(LEVELS[level]):
                stamp = dt.datetime.combine(day, dt.time(HOUR, 0, tzinfo=dt.timezone.utc))
                out.append((stamp + dt.timedelta(seconds=90 * i), i))
    return out


def preview(grid: list[list[int]]) -> None:
    for row in grid:
        print("".join(FILL[v] for v in row))
    cells = sum(1 for r in grid for v in r if v)
    print(f"\n{cells} cells, {sum(LEVELS[v] for r in grid for v in r)} commits planned")


def paint(rows: list[tuple[dt.datetime, int]], root: Path, name: str, email: str, push: bool) -> None:
    data = root / "data"
    data.mkdir(exist_ok=True)
    for stamp, seq in rows:
        iso = stamp.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        marker = data / f"{stamp.date().isoformat()}.txt"
        marker.write_text(f"{iso} #{seq}\n", encoding="utf-8")
        env = {
            **os.environ,
            "GIT_AUTHOR_DATE": iso,
            "GIT_COMMITTER_DATE": iso,
        }
        subprocess.run(["git", "add", str(marker)], cwd=root, check=True)
        subprocess.run(
            [
                "git", "-c", f"user.name={name}", "-c", f"user.email={email}",
                "commit", "--quiet", "--message", f"art {stamp.date()}",
            ],
            cwd=root, env=env, check=True,
        )
    if push:
        push_all(root, name, email)


def push_all(root: Path, name: str, email: str) -> None:
    """Another workflow may have pushed to the branch while we were committing."""
    ident = ["-c", f"user.name={name}", "-c", f"user.email={email}"]
    for attempt in range(1, 4):
        subprocess.run(["git", *ident, "pull", "--rebase", "--autostash", "--quiet"], cwd=root, check=False)
        if subprocess.run(["git", *ident, "push"], cwd=root, check=False).returncode == 0:
            return
        print(f"push attempt {attempt} rejected, rebasing and retrying", file=sys.stderr)
    raise SystemExit("git push failed after 3 attempts (branch still diverged)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", help="text to paint, e.g. \"X A Q A\"")
    ap.add_argument("--name", default="xaqa", help="git author name")
    ap.add_argument("--email", default="", help="git author email (must be attached to your GitHub account)")
    ap.add_argument("--repo", default=".", help="path to the git repo to write into")
    ap.add_argument("--today", default=None, help="override today's date (YYYY-MM-DD), for testing")
    ap.add_argument("--preview", action="store_true", help="print the grid only")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ap.add_argument("--push", action="store_true", help="git push when done")
    args = ap.parse_args()

    grid = build_grid(args.text)
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    rows = plan(grid, today)

    if args.preview:
        preview(grid)
        return

    if args.dry_run:
        preview(grid)
        by_day: dict[dt.date, int] = {}
        for stamp, _ in rows:
            by_day[stamp.date()] = by_day.get(stamp.date(), 0) + 1
        first, last = min(by_day), max(by_day)
        print(f"\nwindow {first} .. {last}  ({len(by_day)} active days, {len(rows)} commits)")
        for day in sorted(by_day)[:5]:
            print(f"  {day} ({day.strftime('%a')}) x{by_day[day]}")
        print("  ...")
        return

    if not args.email:
        sys.exit("--email is required to paint (it decides which account gets the squares)")
    paint(rows, Path(args.repo).resolve(), args.name, args.email, args.push)
    print(f"created {len(rows)} commits")


if __name__ == "__main__":
    main()
