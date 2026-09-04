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
