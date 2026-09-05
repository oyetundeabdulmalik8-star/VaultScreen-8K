# VaultScreen 8K

A premium, single-page marketing website in the **Claude Fable 5 design style** — dark canvas, one accent colour doing all the work, glass surfaces, editorial typography (grotesk + italic serif), and restrained motion that respects `prefers-reduced-motion`.

Zero dependencies. No build step. Plain HTML, CSS and JavaScript — open `index.html` and it works.

## Project structure

```
VaultScreen-8K/
├── index.html                 # The whole site (one page, sectioned)
├── assets/
│   ├── css/styles.css         # Design tokens + all styles (edit :root to re-skin)
│   ├── js/main.js             # Progressive enhancement (nav, reveal, FAQ, form…)
│   └── img/
│       ├── favicon.svg
│       └── og-image.png       # Social share preview (1200×630)
├── CONTENT-GUIDE.md           # ← Fill this in with your business details
└── .github/workflows/
    └── deploy-pages.yml       # Auto-deploys to GitHub Pages on push to main
```

## Sections

| Section       | Anchor          | What it does                                                    |
| ------------- | --------------- | --------------------------------------------------------------- |
| Header        | `#top`          | Sticky, frosts on scroll; mobile menu; scroll-spy active links   |
| Hero          | —               | Staggered headline reveal, CSS-only product visual, floating chips, pointer tilt |
| Ticker        | —               | Infinite marquee of highlights (pauses on hover)                |
| Features      | `#features`     | Bento grid with pointer-tracked spotlight + animated 99 % ring   |
| How it works  | `#process`      | 3-step process                                                  |
| Stats         | —               | Count-up numbers on scroll                                      |
| Reviews       | `#testimonials` | Testimonial cards                                               |
| FAQ           | `#faq`          | Accessible accordion (`aria-expanded`, animated with CSS grid)  |
| Contact       | `#contact`      | Validated form — `mailto:` fallback or POST to any endpoint     |
| Footer        | —               | Links, socials, auto-updating year                              |

## Run locally

Any static server works:

```bash
npx serve .            # or: python3 -m http.server 8080
```

Then open the URL it prints (usually `http://localhost:3000`).

## Customise

1. **Business content** — search `index.html` for `<!-- EDIT:` comments; every editable block is labelled. `CONTENT-GUIDE.md` lists exactly what information is needed.
2. **Brand colours / fonts** — edit the tokens at the top of `assets/css/styles.css` (`--accent`, `--bg`, `--font-display`, …). One accent colour drives the whole site.
3. **Contact form** — by default it opens the visitor's email app (`data-mailto`). To post to a real service, add `data-endpoint="https://formspree.io/f/XXXX"` to the `<form>` in `index.html`.
4. **Social preview image** — replace `assets/img/og-image.png` (1200×630).

## Deploy

**GitHub Pages (included):** push to `main` and the workflow in `.github/workflows/deploy-pages.yml` publishes the site. Enable it once under *Settings → Pages → Source: GitHub Actions*.

Also drops straight onto Netlify, Vercel, Cloudflare Pages or any static host — no build command, publish directory `/`.

## Accessibility & performance

- Semantic landmarks, skip link, visible focus rings, labelled controls
- Works without JavaScript (nav, FAQ and form all degrade gracefully)
- Honours `prefers-reduced-motion`
- Fonts are the only external requests; everything else is inline or local
