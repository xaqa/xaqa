# xaqa profile kit

Live at **github.com/xaqa/xaqa** (public). That is the only public repo on the
account; the eleven private repos were not touched.

```
README.md                        -> the profile README (repo root), two badges
LICENSE                          -> MIT
.gitattributes                   -> keeps the painter out of the language stats
.gitignore                       -> ignores the site build output
scripts/commit-art.py            -> paints text into the contribution graph
scripts/build-site.py            -> renders the site from data/ + the API
data/*.txt                       -> one committed file per painted day
.github/workflows/commit-art.yml -> monthly repaint of the graph art
.github/workflows/pages.yml      -> builds and deploys the site
.github/workflows/star-ping.yml  -> DMs a Telegram ping on star or fork
```

## README

One line, two live badges. The first is the `shields.io` commits counter
(`github/commit-activity/t`), read off the repo rather than typed in — it is the
only place the total should appear. The second is GitHub's own status badge for
`commit-art.yml`, which cannot rot the way a third-party host can. Nothing else
renders — no banner, no streak card, no stats widgets, no emoji. The usual
widget hosts were probed 2026-11-04: `github-readme-stats` answers 503, and both
`github-readme-activity-graph` and `github-profile-trophy` answer 402, so those
three cannot be used.

The repo card under "Popular repositories" is deliberately bare: the description
was cleared, the wiki and projects tabs are off, and `.gitattributes` marks
`scripts/commit-art.py` as `linguist-generated`, which drops the repo's language
map to `{}` and with it the Python dot.

Removed 2026-11-04, as clutter: the animated banner (`assets/banner.svg`), the
snake (`.github/workflows/snake.yml` and its `output` branch), the 3D voxel
calendar (`profile-3d.yml`, `profile-3d-settings.json`, `profile-3d-contrib/`),
and the terminal demo template (`demo/demo.tape`).

## 1. Account settings — still manual

The `gh` token on this machine carries `gist, project, read:org, repo, workflow`
and **not** `user`, so `PATCH /user` returns 404. These have to be set by hand
(Settings → Public profile), or re-auth with `gh auth refresh -h github.com -s user`
first and then they can be scripted:

- **Name** — short. Renders above the username.
- **Bio** — one line: what you build. No emoji wall.
- **Company / Location / Website** — location renders a live local-time clock.
- **Social accounts** — the README carries no links, so this is the only place
  the account can point anywhere. Currently `@7800` (X) plus `zrpc` and `tolr`,
  both Instagram links, which look like leftovers; add site / X / Telegram / mail.
- **Status** — reads `🎯 Focusing` right now ("Focusing" is the busy preset, not
  a typed message). Either leave the glyph bare or clear the status entirely.
- **Pinned repositories** — six slots. Pinning a private repo publishes its name,
  so pin public work first; a private pin renders as a grey card with a lock.
- **Social preview** — Settings → Social preview → upload
  `~/Downloads/xaqa-social-preview.png` (1280×640). There is no API for this one.
- **Sponsor** — the *Public Sponsor* achievement needs a real $1/mo sponsorship
  paid to someone else's account. Unscriptable, and the only achievement here
  that costs money.

Leave *Settings → Profile → Contributions & Activity → Include private
contributions* **off**. It is off now, and the private repos have real commits
that would render as grey squares fighting the graph art.

## 2. Repo

```
xaqa/xaqa   public   default branch main
```

Public is required: a profile README only renders from a public repo, and only
public-repo commits count toward the contribution graph (while "Include private
contributions" stays off). Making this repo private would blank the README area
*and* zero the graph, so it stays public. Nothing else on the
account changed visibility. Workflow permissions were set to **Read and write**
via `PUT /repos/xaqa/xaqa/actions/permissions/workflow`.

If the README ever stops showing: repo name must equal the username, README must
sit in the root of the default branch, repo public, not a fork.

## 3. Actions

| workflow | writes | notes |
|---|---|---|
| `commit-art.yml` | this branch | monthly repaint of the art |
| `pages.yml` | nothing | builds `_site/` and deploys it as an artifact |
| `star-ping.yml` | nothing | Telegram DM on `watch` and `fork` |

`commit-art.yml` is the only workflow that commits anything. `push_all()` in the
script rebases onto the remote and retries three times, so a concurrent push
cannot leave the art half-pushed, and it declares `concurrency: main-writer` for
the same reason. The other two hold `permissions: {}` or `contents: read` and
never write history — deliberately, because any commit they made would land
inside the canvas.

## 4. Site

Live at **https://xaqa.github.io/xaqa/**, served by GitHub Pages with
`build_type=workflow`. It is a still of the same canvas the profile shows:
`data/*.txt` says which days are painted, and the API fills in live commit /
star / fork counts at build time. One file, inline SVG, no JavaScript, no
third-party assets, theme-aware through `prefers-color-scheme`.

It redeploys on any push touching `data/**`, `scripts/build-site.py` or
`pages.yml`, or on `workflow_dispatch`. The deploy uploads an artifact, so
nothing is committed and the graph stays untouched.

```bash
gh api -X POST repos/xaqa/xaqa/pages -f build_type=workflow   # enable or repair
python3 scripts/build-site.py                                 # build locally into _site/
```

The repo's website field points at the site URL, which is the only chrome on the
repository page that is not the README.

## 5. Star ping

`star-ping.yml` DMs the Telegram chat when someone stars or forks the repo. Two
Actions secrets feed it, and their values must never be printed:

```bash
gh secret set TELEGRAM_BOT_TOKEN --repo xaqa/xaqa --body "$TG_TOKEN"
gh secret set TELEGRAM_CHAT_ID  --repo xaqa/xaqa --body "$TG_CHAT"
```

Both live in `~/warroom-clean/state/telegram.env` — that is the scanner bot, not
the unrelated token under `~/.paperclip/telegram/`. Inside the workflow the token
is only interpolated into a URL that is never echoed, and GitHub masks secret
values in logs as a second line of defence.

## 6. Contribution art

```bash
python3 scripts/commit-art.py "X A Q A" --preview        # see the shape
python3 scripts/commit-art.py "X A Q A" --dry-run        # dates + counts, writes nothing
python3 scripts/commit-art.py "X A Q A" \
  --name xaqa --email 307261345+xaqa@users.noreply.github.com --push
```

GitHub only counts a square if all four hold: repo public, repo not a fork,
commit on the default branch, author email attached to the account. The email
above is the numeric `users.noreply.github.com` form for user ID 307261345, so
it always matches, even if the account email changes.

"X A Q A" is 66 cells × 5 commits = 330 art commits, 2026-01-04 → 2026-09-05,
centred in the 53×7 grid. Every commit is stamped 12:00 UTC so it lands on the
same calendar day in every timezone. Work commits share the same window and the
same noreply author, so they deepen the day they land on; the repo total is
whatever the badge reports (341 at the time of writing) and it moves with every
commit — never pin it in prose. **It has already run for this month** — do
not run it again now or you stack duplicate layers. The monthly job repaints as
the 12-month window slides.

Five commits per cell used to be the level-4 bucket, back when the busiest real
day in the last year held 1 commit. The busiest day the graph can see now is
2026-11-03 with 8, so the art cells sit one bucket below the top and that one
real day renders darker than the letters. The private repos are busier still
(2026-10-31 holds 41 commits), but they are invisible while "Include private
contributions" stays off — switching it on would light 15 blank cells inside the
art's canvas, three of them darker than the art itself.
