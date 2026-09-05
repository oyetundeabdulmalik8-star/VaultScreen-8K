# Somi Steam Car Wash — website

Single-page marketing site for **Somi Steam Car Wash**, Plot 90 Kudirat Abiola Way, Oregun, Ikeja, Lagos — built in the Claude Fable 5 design style: dark canvas, one accent colour, glass surfaces, editorial typography and restrained motion.

Zero dependencies. No build step. Plain HTML, CSS and JavaScript.

## Structure

```
index.html                  the whole site (one page, sectioned)
assets/css/styles.css       design tokens (:root) + all styles; §15 is business-specific
assets/js/main.js           progressive enhancement (nav, reveal, count-up, FAQ, tilt…)
assets/img/                 hero / interior / lounge photos (2 sizes each), favicon, OG image
.github/workflows/          auto-deploy to GitHub Pages on push to main
CONTENT-GUIDE.md            what's still open to fill in
```

## Sections

| Anchor       | Section                                                                 |
| ------------ | ----------------------------------------------------------------------- |
| `#top`       | Sticky header · tap-to-call CTA · mobile menu                           |
| —            | Hero: staggered headline, photo in glass frame, floating chips, tilt    |
| —            | Services ticker                                                         |
| `#services`  | Bento grid — steam exterior, interior, engine bay, detailing, team      |
| `#lounge`    | Bar, restaurant & laundry — the "relax while we work" differentiator    |
| `#process`   | Drive in → pick a service → relax & collect                             |
| —            | Stats: 20-car capacity · 4.0 rating · 164 reviews · 7 days              |
| `#reviews`   | Three real Google reviews + link to all reviews                         |
| `#faq`       | Six FAQs (steam safety, booking, duration, price, location, SUVs)       |
| `#visit`     | Address, phone, WhatsApp, hours · dark-tinted Google Map · directions   |
| —            | Footer · mobile sticky Call / WhatsApp / Directions bar                 |

## Run locally

```bash
python3 -m http.server 8080      # or: npx serve .
```

## Editing

- **Copy** — everything lives in `index.html`; search for `EDIT:` for the spots still waiting on real info.
- **Colours / fonts** — the tokens at the top of `assets/css/styles.css`. `--accent` drives the whole site.
- **Photos** — the current images are AI-generated placeholders. Drop real photos into `assets/img/` with the same filenames (`hero-1600.jpg` / `hero-800.jpg`, `interior-1200.jpg` / `interior-600.jpg`, `lounge-1600.jpg` / `lounge-800.jpg`) and they'll slot straight in.
- **Map / directions** — all links use the Google Place ID `ChIJd1pBMEWSOxARdOuVdtgQo38`; no API key required.
- **Structured data** — `AutoWash` JSON-LD in `<head>` gives Google the address, phone, rating and map.

## Deploy

Push to `main` → the included workflow publishes to GitHub Pages. One-time: *Settings → Pages → Source: GitHub Actions*. Also works on Netlify / Vercel / Cloudflare Pages with no build command and publish directory `/`.
