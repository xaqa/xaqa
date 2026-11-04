# xaqa profile kit

Everything here goes into a **public** repo named exactly `xaqa`.

```
README.md                       -> the profile README (repo root)
assets/banner.svg               -> animated header
profile-3d-settings.json        -> 3D contribution calendar, avatar palette
scripts/commit-art.py           -> paints text into the contribution graph
.github/workflows/snake.yml     -> animated snake over the contribution grid
.github/workflows/profile-3d.yml-> 3D voxel contribution calendar
.github/workflows/commit-art.yml-> monthly repaint of the graph art
demo/demo.tape                  -> vhs recording script -> demo/demo.gif
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

## 1. Account settings (do this first, it is free)

- **Avatar** — the one you pasted. Keep it, it is the identity.
- **Name** — short. Renders above the username.
- **Bio** — one line: what you build + where. No emoji wall.
- **Company / Location / Website** — location renders a live local-time clock.
- **Social accounts** — Settings → Public profile → Social accounts.
- **Status** — 🎯 with the message left blank, so only the glyph shows.
- **Settings → Profile → Contributions & Activity** — enable *Include private contributions on my profile*.
- No Pro needed for any of this.

## 2. Create the repo

1. New repo, name `xaqa`, **public**, initialise with a README.
2. Copy `README.md`, `assets/`, `scripts/`, `.github/`, `demo/`, `profile-3d-settings.json` in.
3. Replace `xaqa.dev`, `x.com/xaqa`, `t.me/xaqa`, `you@xaqa.dev` with real links.
4. Repo → Settings → Actions → General → Workflow permissions → **Read and write**.
5. Commit. The README shows on the profile Overview tab.

If nothing shows up: repo name must equal the username, README must sit in the
root of the default branch, repo public, not a fork.

## 3. Actions

| workflow | writes | notes |
|---|---|---|
| `snake.yml` | `output` branch → `snake.svg` | white snake, sky-ramp dots |
| `profile-3d.yml` | this branch → `profile-3d-contrib/profile-sky.svg` | `SETTING_JSON` limits it to that one file; without it the action writes ten |
| `commit-art.yml` | this branch | 330 commits, monthly |

Run each once from the Actions tab, then reload your profile.

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
same calendar day in every timezone. The workflow repaints monthly as the
12-month window slides. Do not run it more than once a month or you stack
duplicate layers.

## 5. Terminal demo

`demo/demo.tape` is a template. `brew install vhs`, point `Type` at something
real, `vhs demo/demo.tape`, commit `demo/demo.gif`, reference it in the README.
Ten seconds of your own tool beats every badge in section 3.
