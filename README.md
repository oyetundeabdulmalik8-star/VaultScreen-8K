# VaultScreen-8K

8K phone-wallpaper generation prompts, reverse-engineered from public wallpaper posts.

## Contents

- `prompts/batch-01-tiktok-sources.md` — 15 entries. Each has a visual breakdown of the
  source (subject, palette, lighting, composition, texture, mood) plus a ready-to-run
  prompt that reproduces the style with 1–3 deliberate swaps, so every prompt is a
  variation rather than a copy. All prompts end with `8K, phone wallpaper, vertical 9:19.5`.
- `work/harvest.py` + `.github/workflows/harvest.yml` — the sourcing pipeline. It runs
  `yt-dlp` against each post (falling back to a photo-mode metadata API when yt-dlp is
  blocked), pulls carousel images or 3 frames per video, and writes downscaled contact
  sheets to `work/thumbs/` for review.
- `work/urls.txt` — the source list, one `<key> <url>` per line. Push a change to it to
  re-run the harvest.

## House rules for prompts

- No captions, on-screen text, watermarks, logos or trademarked characters from sources.
- Every descriptor must be concrete and reproducible — no bare "aesthetic" or "vibe".
- Harvested source media is gitignored; only the derived prompts are committed.

## VaultScreen 8K — Wallpaper Pack Vol. 1 (`pack/`)

30 original wallpapers, 2778 × 6019 px (true 9:19.5), five curated collections of six:
Neon Noir Cities · Cosmic Gradients · Minimal Nature · Cinematic Dusk · Abstract Glass & Liquid.

Download the built product from the **`pack-v1` release**:

| Asset | Size | Use |
| --- | --- | --- |
| `VaultScreen-8K-Pack.zip` | ~353 MB | The sellable file: `/wallpapers` (30 PNG) + `README.txt`. No mockups inside. |
| `VaultScreen-8K-previews.zip` | ~13 MB | Marketing only: 30 gallery mockups, 5 hero shots, collection preview, contact grid. |

Repo contents:

- `pack/masters/` — 30 committed source renders (704 × 1520 JPEG q97), the input to the build.
- `pack/scripts/build_pack.py` — crops to 9:19.5, upscales to 2778 × 6019, composites all
  mockups procedurally (titanium rail, generic Dynamic Island, screen glare, drop shadow —
  no real iOS UI), and writes both zips.
- `pack/dist/previews/` — web-size previews, all under 3000 px.
- `.github/workflows/build-pack.yml` — push a change to `pack/masters/` or the build script
  and the runner rebuilds the full-res pack and republishes the release assets.

Rendering the full-res set locally takes ~16 min and ~360 MB of disk:
`cd pack && python3 scripts/build_pack.py walls gallery hero collection grid package`
