# xaqa profile kit

Live at **github.com/xaqa/xaqa** (public). That is the only public repo on the
account; the eleven private repos were not touched.

```
README.md                        -> the profile README (repo root)
assets/banner.svg                -> animated header
profile-3d-settings.json         -> 3D contribution calendar, avatar palette
scripts/commit-art.py            -> paints text into the contribution graph
.github/workflows/snake.yml      -> animated snake over the contribution grid
.github/workflows/profile-3d.yml -> 3D voxel contribution calendar
.github/workflows/commit-art.yml -> monthly repaint of the graph art
demo/demo.tape                   -> vhs recording script -> demo/demo.gif
```

## Palette

Sampled straight off the avatar, so every asset matches it:

| role | value |
|---|---|
| sky (avatar background) | `#83bcd0` |
| facet highlights | `#93cbdd` / `#8ac3d6` (light), `#79b3c7` (dark) |
| body | `#ffffff` / `#f4fbfd` |
| hardware (headphones, mask) | `#0b0b0d` |

Banner motifs that come from the avatar: low-poly facets in the corners, white
word with a black outline (white body + black accessories), a black caret, a
white status pill, and three black **shadow paws** bolted under the word that
snap between positions instead of easing — the same "2D claws stuck on a 3D
body" quirk, done in SVG.

The banner is a single file used in both themes, the way the avatar is. No
`<picture>` swap, one thing to maintain.

## 1. Account settings — still manual

The `gh` token on this machine carries `gist, project, read:org, repo, workflow`
and **not** `user`, so `PATCH /user` returns 404. These have to be set by hand
(Settings → Public profile), or re-auth with `gh auth refresh -h github.com -s user`
first and then they can be scripted:

- **Name** — short. Renders above the username.
- **Bio** — one line: what you build + where. No emoji wall.
- **Company / Location / Website** — location renders a live local-time clock.
- **Social accounts** — the badge row in `README.md` currently links only to
  GitHub. Add site / X / Telegram / mail targets here *and* in the README, so
  the two agree.
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
| `snake.yml` | `output` branch → `snake.svg` | white snake, sky-ramp dots |
| `profile-3d.yml` | this branch → `profile-3d-contrib/profile-sky.svg` | `SETTING_JSON` limits it to that one file; without it the action writes ten |
| `commit-art.yml` | this branch | 330 commits, monthly |

All three have run once and their outputs verify (200 from raw). `commit-art.yml`
and `profile-3d.yml` share `concurrency: main-writer`, because both push to
`main`: the first dispatch of the art job lost that race mid-run
(`non-fast-forward`). `push_all()` in the script now rebases onto the remote and
retries three times, so a lost race cannot leave the art half-pushed.

`SETTING_JSON` accepts one settings object or an array; `fileName` is resolved
inside `profile-3d-contrib/`. The shipped file is the upstream voxel block
pattern with the five contribution levels recoloured to the sky ramp
`#f4fbfd`, `#cfe9f2`, `#a9d6e5`, `#6fb0c6`, `#2f7d99` on a `#83bcd0` canvas.

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

## 5. Terminal demo

`demo/demo.tape` is a template. `brew install vhs`, point `Type` at something
real, `vhs demo/demo.tape`, commit `demo/demo.gif`, reference it in the README.
Ten seconds of your own tool beats every badge in section 3.
