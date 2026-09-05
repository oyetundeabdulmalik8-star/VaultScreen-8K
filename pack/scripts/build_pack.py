#!/usr/bin/env python3
"""VaultScreen-8K pack builder.

raw/  ->  dist/wallpapers/  (full-res sellable PNGs, true 9:19.5)
      ->  dist/previews/    (marketing mockups: gallery, hero, collection grid)

Mockups are composited procedurally (no AI, no real iOS UI) so framing and
lighting are identical across the whole listing.
"""
import glob
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("VS_RAW_DIR") or os.path.join(ROOT, "raw")
DIST = os.path.join(ROOT, "dist")
WALLS = os.path.join(DIST, "wallpapers")
PREV = os.path.join(DIST, "previews")
GALLERY = os.path.join(PREV, "gallery")
HERO = os.path.join(PREV, "hero")

OUT_W, OUT_H = 2778, 6019          # exact 9:19.5 at the requested 2778 width
RATIO = 9 / 19.5

THEMES = {
    "neon-noir": "Neon Noir Cities",
    "cosmic": "Cosmic Gradients",
    "minimal-nature": "Minimal Nature",
    "cinematic-dusk": "Cinematic Dusk",
    "motivation": "Motivation",
}


def theme_of(name):
    stem = os.path.splitext(os.path.basename(name))[0]
    return stem.rsplit("-", 1)[0]


# ---------------------------------------------------------------- wallpapers
def crop_to_ratio(im, ratio=RATIO):
    w, h = im.size
    if w / h > ratio:
        nw = int(round(h * ratio))
        left = (w - nw) // 2
        im = im.crop((left, 0, left + nw, h))
    else:
        nh = int(round(w / ratio))
        top = (h - nh) // 2
        im = im.crop((0, top, w, top + nh))
    return im


def upscale(im, w=OUT_W, h=OUT_H):
    """Two-step Lanczos with a light detail pass; keeps gradients clean."""
    im = im.convert("RGB")
    mid = (int(w * 0.55), int(h * 0.55))
    im = im.resize(mid, Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=3))
    im = im.resize((w, h), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2.4, percent=42, threshold=4))
    return ImageEnhance.Color(im).enhance(1.03)


def source_images(d):
    """Masters may be .png (local raw) or .jpg (committed, git-friendly)."""
    files = glob.glob(os.path.join(d, "*.png")) + glob.glob(os.path.join(d, "*.jpg"))
    return sorted(files)


def build_wallpapers():
    os.makedirs(WALLS, exist_ok=True)
    made = []
    for f in source_images(RAW):
        dst = os.path.join(WALLS,
                           os.path.splitext(os.path.basename(f))[0] + ".png")
        out = upscale(crop_to_ratio(Image.open(f)))
        out.save(dst, "PNG", optimize=True)
        mb = os.path.getsize(dst) / 1e6
        print("  wallpaper %-24s %s  %.1f MB" % (os.path.basename(dst), out.size, mb))
        made.append(dst)
    return made


# ------------------------------------------------------------------- mockups
def rounded_mask(size, radius, supersample=4):
    w, h = size
    m = Image.new("L", (w * supersample, h * supersample), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        (0, 0, w * supersample - 1, h * supersample - 1),
        radius=radius * supersample, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def phone_render(wallpaper, screen_w=880):
    """Return an RGBA phone (frame + screen + island + glare), no shadow."""
    screen_h = int(round(screen_w / RATIO))
    bezel = max(6, int(screen_w * 0.016))
    band = max(10, int(screen_w * 0.026))          # titanium rail thickness
    body_w, body_h = screen_w + 2 * (bezel + band), screen_h + 2 * (bezel + band)
    corner = int(screen_w * 0.155)

    phone = Image.new("RGBA", (body_w, body_h), (0, 0, 0, 0))

    # brushed titanium rail with a soft vertical sheen
    rail = Image.new("RGB", (body_w, body_h), (108, 108, 112))
    rg = Image.new("L", (body_w, 1))
    for x in range(body_w):
        t = x / max(1, body_w - 1)
        v = 90 + 130 * (0.5 + 0.5 * __import__("math").sin(3.1 * t + 0.6)) ** 2
        rg.putpixel((x, 0), int(min(255, v)))
    rail = Image.composite(Image.new("RGB", (body_w, body_h), (196, 196, 200)),
                           rail, rg.resize((body_w, body_h)))
    phone.paste(rail, (0, 0), rounded_mask((body_w, body_h), corner + band))

    # black bezel
    bez = Image.new("RGBA", (screen_w + 2 * bezel, screen_h + 2 * bezel),
                    (12, 12, 14, 255))
    phone.paste(bez, (band, band),
                rounded_mask(bez.size, corner + bezel // 2))

    # screen
    scr = crop_to_ratio(wallpaper.convert("RGB")).resize(
        (screen_w, screen_h), Image.LANCZOS)
    phone.paste(scr, (band + bezel, band + bezel),
                rounded_mask((screen_w, screen_h), corner))

    ov = Image.new("RGBA", (body_w, body_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    # Dynamic Island (generic pill cutout, no UI elements)
    iw, ih = int(screen_w * 0.30), int(screen_w * 0.088)
    ix = band + bezel + (screen_w - iw) // 2
    iy = band + bezel + int(screen_h * 0.019)
    d.rounded_rectangle((ix, iy, ix + iw, iy + ih), radius=ih // 2,
                        fill=(6, 6, 8, 255))
    d.ellipse((ix + iw - ih + 6, iy + 6, ix + iw - 6, iy + ih - 6),
              fill=(16, 18, 24, 255))

    # diagonal screen glare
    gl = Image.new("L", (body_w, body_h), 0)
    gd = ImageDraw.Draw(gl)
    gd.polygon([(band, band + int(body_h * 0.10)),
                (band + int(body_w * 0.72), band),
                (band + int(body_w * 0.98), band + int(body_h * 0.22)),
                (band, band + int(body_h * 0.52))], fill=42)
    gd.polygon([(band, band + int(body_h * 0.58)),
                (band + int(body_w * 0.34), band + int(body_h * 0.44)),
                (band + int(body_w * 0.10), band + int(body_h * 0.86))], fill=16)
    gl = gl.filter(ImageFilter.GaussianBlur(26))
    gl = Image.composite(gl, Image.new("L", gl.size, 0),
                         rounded_mask((body_w, body_h), corner + band))
    ov = Image.alpha_composite(ov, Image.merge(
        "RGBA", (Image.new("L", gl.size, 255),) * 3 + (gl,)))

    phone = Image.alpha_composite(phone, ov)

    # crisp edge highlight
    edge = Image.new("RGBA", (body_w, body_h), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle(
        (0, 0, body_w - 1, body_h - 1), radius=corner + band,
        outline=(232, 232, 236, 150), width=max(2, body_w // 340))
    return Image.alpha_composite(phone, edge)


def backdrop(size, dark=False):
    w, h = size
    top = (26, 27, 30) if dark else (243, 242, 239)
    bot = (12, 12, 14) if dark else (222, 221, 217)
    g = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        g.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t)
                                 for i in range(3)))
    bg = g.resize((w, h))
    # soft radial vignette / light pool behind the phone
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse(
        (int(w * 0.08), int(h * 0.02), int(w * 0.92), int(h * 0.98)),
        fill=54 if not dark else 40)
    glow = glow.filter(ImageFilter.GaussianBlur(int(min(w, h) * 0.12)))
    return Image.composite(Image.new("RGB", (w, h),
                                     (255, 255, 255) if not dark else (60, 62, 70)),
                           bg, glow)


def drop_shadow(phone, blur, offset, opacity=120, spread=1.02):
    a = phone.split()[3].point(lambda v: min(255, int(v * opacity / 255)))
    sw, sh = int(phone.width * spread), int(phone.height * spread)
    sh_img = Image.new("RGBA", (sw + blur * 4, sh + blur * 4), (0, 0, 0, 0))
    tint = Image.new("RGBA", (sw, sh), (8, 8, 12, 255))
    tint.putalpha(a.resize((sw, sh)))
    sh_img.paste(tint, (blur * 2, blur * 2), tint)
    return sh_img.filter(ImageFilter.GaussianBlur(blur)), offset


def compose_single(wall_path, out_path, canvas=(1400, 1900), screen_w=760,
                   dark=False, quality=90):
    bg = backdrop(canvas, dark=dark)
    phone = phone_render(Image.open(wall_path), screen_w=screen_w)
    x = (canvas[0] - phone.width) // 2
    y = (canvas[1] - phone.height) // 2
    sh_img, off = drop_shadow(phone, blur=34, offset=(0, int(phone.height * 0.035)))
    bg.paste(sh_img, (x - 68 + off[0], y - 68 + off[1]), sh_img)
    bg.paste(phone, (x, y), phone)
    bg.save(out_path, "JPEG", quality=quality, optimize=True)
    return out_path


def preview_sources():
    """Previews are built from the raw renders (identical content, cheaper)."""
    src = RAW if source_images(RAW) else WALLS
    return source_images(src)


def build_gallery():
    os.makedirs(GALLERY, exist_ok=True)
    for f in preview_sources():
        out = os.path.join(GALLERY, os.path.splitext(os.path.basename(f))[0] + ".jpg")
        compose_single(f, out)
        print("  gallery   ", os.path.basename(out))


def build_heroes():
    os.makedirs(HERO, exist_ok=True)
    seen = {}
    for f in preview_sources():
        t = theme_of(f)
        seen.setdefault(t, f)
    for t, f in seen.items():
        out = os.path.join(HERO, "hero-%s.jpg" % t)
        compose_single(f, out, canvas=(1800, 2400), screen_w=980, dark=True,
                       quality=92)
        print("  hero      ", os.path.basename(out))
    return seen


def build_collection(seen, out_name="collection-preview.jpg",
                     canvas=(2800, 1600)):
    """Fanned row of one phone per theme, sized to fit the canvas height."""
    bg = backdrop(canvas, dark=True)
    items = [seen[k] for k in THEMES if k in seen]
    n = max(1, len(items))
    cw, ch = canvas

    # size from height first, then shrink if the row is too wide
    body_h = ch * 0.76
    screen_h = body_h / 1.085
    screen_w = int(screen_h * RATIO)
    gap_ratio = 0.16
    est_w = n * screen_w * 1.085 + (n - 1) * screen_w * gap_ratio
    if est_w > cw * 0.92:
        screen_w = int(screen_w * (cw * 0.92) / est_w)
    screen_w = max(160, screen_w)

    phones = [phone_render(Image.open(p), screen_w=screen_w) for p in items]
    gap = int(screen_w * gap_ratio)
    total = sum(p.width for p in phones) + gap * (n - 1)
    x = (cw - total) // 2
    mid = (n - 1) / 2
    for i, ph in enumerate(phones):
        lift = int((abs(i - mid) - mid / 2) * screen_w * 0.09)
        y = (ch - ph.height) // 2 + lift
        sh_img, off = drop_shadow(ph, blur=40,
                                  offset=(0, int(ph.height * 0.045)), opacity=165)
        bg.paste(sh_img, (x - 80 + off[0], y - 80 + off[1]), sh_img)
        bg.paste(ph, (x, y), ph)
        x += ph.width + gap
    out = os.path.join(PREV, out_name)
    bg.save(out, "JPEG", quality=92, optimize=True)
    print("  collection", os.path.basename(out), bg.size, "phones:", n)
    return out


def build_grid(out_name="all-wallpapers-grid.jpg", cols=6, cell_w=420):
    files = preview_sources()
    if not files:
        return None
    cell_h = int(cell_w / RATIO)
    rows = (len(files) + cols - 1) // cols
    pad = int(cell_w * 0.10)
    W = cols * cell_w + (cols + 1) * pad
    H = rows * cell_h + (rows + 1) * pad
    sheet = backdrop((W, H), dark=True)
    for i, f in enumerate(files):
        im = crop_to_ratio(Image.open(f).convert("RGB")).resize(
            (cell_w, cell_h), Image.LANCZOS)
        m = rounded_mask((cell_w, cell_h), int(cell_w * 0.09))
        x = pad + (i % cols) * (cell_w + pad)
        y = pad + (i // cols) * (cell_h + pad)
        sheet.paste(im, (x, y), m)
    if sheet.width > 2800:
        sheet = sheet.resize((2800, int(sheet.height * 2800 / sheet.width)),
                             Image.LANCZOS)
    out = os.path.join(PREV, out_name)
    sheet.save(out, "JPEG", quality=90, optimize=True)
    print("  grid      ", os.path.basename(out), sheet.size)
    return out


README = """VaultScreen 8K — Wallpaper Pack Vol. 1
=========================================

30 original wallpapers in five curated collections:
  Neon Noir Cities        neon-noir-01 .. 06
  Cosmic Gradients        cosmic-01 .. 06
  Minimal Nature          minimal-nature-01 .. 06
  Cinematic Dusk          cinematic-dusk-01 .. 06
  Motivation              motivation-01 .. 06

FILES
  Format      PNG, 24-bit RGB
  Resolution  2778 x 6019 px
  Aspect      9:19.5 vertical

COMPATIBILITY
  Built for iPhone 15 / 15 Pro / 15 Pro Max / 16 / 16 Pro / 16 Pro Max and any
  9:19.5 display. They also fit 19.5:9 phones from other makers; on shorter
  screens (18:9, 20:9) iOS/Android will crop slightly top and bottom - every
  image keeps its subject away from the extreme edges so cropping stays safe.
  Each wallpaper leaves clear space near the top for the clock and near the
  bottom for the dock.

HOW TO SET
  Save to Photos -> open the image -> Share -> Use as Wallpaper.
  For the sharpest result transfer the original PNG (AirDrop, iCloud Drive or
  cable) rather than sending it through a messaging app, which recompresses.

NOTES
  All artwork is original, AI-assisted and produced for this pack. No text,
  logos or interface elements are baked into the images.

TERMS
  Personal use. Wallpapers may not be resold, redistributed or bundled into
  another pack.
"""


def package():
    """Buyer zip (wallpapers + README) and a separate marketing preview zip."""
    import zipfile
    os.makedirs(DIST, exist_ok=True)
    walls = sorted(glob.glob(os.path.join(WALLS, "*.png")))
    buyer = os.path.join(DIST, "VaultScreen-8K-Pack.zip")
    with zipfile.ZipFile(buyer, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in walls:
            z.write(f, "wallpapers/" + os.path.basename(f))
        z.writestr("README.txt", README)
    print("  zip        %s  %.1f MB  (%d wallpapers)"
          % (os.path.basename(buyer), os.path.getsize(buyer) / 1e6, len(walls)))

    prev = os.path.join(DIST, "VaultScreen-8K-previews.zip")
    with zipfile.ZipFile(prev, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in sorted(glob.glob(os.path.join(PREV, "**", "*.jpg"),
                                  recursive=True)):
            z.write(f, "previews/" + os.path.relpath(f, PREV))
    print("  zip        %s  %.1f MB"
          % (os.path.basename(prev), os.path.getsize(prev) / 1e6))
    return buyer, prev


def main():
    steps = sys.argv[1:] or ["walls", "gallery", "hero", "collection", "grid"]
    if "walls" in steps:
        build_wallpapers()
    if "gallery" in steps:
        build_gallery()
    seen = {}
    if "hero" in steps:
        seen = build_heroes()
    if "collection" in steps:
        if not seen:
            for f in preview_sources():
                seen.setdefault(theme_of(f), f)
        build_collection(seen)
    if "grid" in steps:
        build_grid()
    if "package" in steps:
        package()
    counts = {}
    for f in preview_sources():
        counts[theme_of(f)] = counts.get(theme_of(f), 0) + 1
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
