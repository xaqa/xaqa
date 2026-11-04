# xaqa profile kit

Live at **github.com/xaqa/xaqa** (public). That is the only public repo on the
account; the eleven private repos were not touched.

```
README.md                        -> the profile README (repo root), text only
scripts/commit-art.py            -> paints text into the contribution graph
data/*.txt                       -> one committed file per painted day
.github/workflows/commit-art.yml -> monthly repaint of the graph art
```

## README

Three lines of text: handle, languages, one clause. No banner, no badges, no
stats widgets, no emoji, no images. The profile's whole look is the painted
contribution graph plus the text next to it.

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
  the account can point anywhere. Add site / X / Telegram / mail here.
- **Status** — 🎯 with the message left blank, so only the glyph shows.

Leave *Settings → Profile → Contributions & Activity → Include private
contributions* **off**. It is off now, and the private repos have real commits
that would render as grey squares fighting the graph art.

## 2. Repo

```
xaqa/xaqa   public   default branch main
```

Public is required: a profile README only renders from a public repo, and only
public-repo commits count toward the contribution graph. Nothing else on the
account changed visibility. Workflow permissions were set to **Read and write**
via `PUT /repos/xaqa/xaqa/actions/permissions/workflow`.

If the README ever stops showing: repo name must equal the username, README must
sit in the root of the default branch, repo public, not a fork.

## 3. Actions

| workflow | writes | notes |
|---|---|---|
| `commit-art.yml` | this branch | 330 commits, monthly |

`commit-art.yml` is the only workflow left. `push_all()` in the script rebases
onto the remote and retries three times, so a concurrent push cannot leave the
art half-pushed; the workflow declares `concurrency: main-writer` for the same
reason.

## 4. Contribution art

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

"X A Q A" is 66 cells × 5 commits = 330 commits, 2026-01-04 → 2026-09-05,
centred in the 53×7 grid. Every commit is stamped 12:00 UTC so it lands on the
same calendar day in every timezone. **It has already run for this month** — do
not run it again now or you stack duplicate layers. The monthly job repaints as
the 12-month window slides.

Five commits per cell is the level-4 bucket because the account's busiest real
day in the last year is 1 commit, so nothing outranks the art.
