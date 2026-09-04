#!/usr/bin/env python3
"""Harvest TikTok wallpaper posts -> downscaled JPEG thumbs + contact sheets.

Runs on a GitHub Actions runner (has open internet). Strategy per URL:
  1. yt-dlp (photo mode -> images, video -> mp4)
  2. fallback: tikwm.com API for image list / play url
Videos get 3 evenly spaced frames via ffmpeg.
All outputs are downscaled so they stay tiny in git.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(ROOT, "downloads")
THUMBS = os.path.join(ROOT, "thumbs")
MAX_IMAGES = 6
THUMB_W = 520

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def run(cmd, timeout=300):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001
        return 1, str(e)


def http_get(url, timeout=60):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Referer": "https://www.tiktok.com/",
        "Accept": "*/*",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def yt_dlp_get(url, outdir):
    os.makedirs(outdir, exist_ok=True)
    code, log = run([
        sys.executable, "-m", "yt_dlp", url,
        "-o", os.path.join(outdir, "post_%(id)s.%(ext)s"),
        "--no-warnings", "--playlist-end", str(MAX_IMAGES),
        "--user-agent", UA, "-N", "4",
    ], timeout=600)
    files = sorted(os.listdir(outdir)) if os.path.isdir(outdir) else []
    return files, log[-1500:]


def tikwm(url):
    api = "https://www.tikwm.com/api/?url=" + urllib.parse.quote(url, safe="")
    return json.loads(http_get(api).decode("utf-8", "replace"))


def tikwm_user(handle, count=8):
    api = ("https://www.tikwm.com/api/user/posts?unique_id=%s&count=%d"
           % (urllib.parse.quote(handle), count))
    return json.loads(http_get(api).decode("utf-8", "replace"))


def save_media_from_item(data, outdir, tag=""):
    """data = tikwm 'data' dict for one post."""
    os.makedirs(outdir, exist_ok=True)
    saved = []
    images = data.get("images") or []
    if images:
        for i, iu in enumerate(images[:MAX_IMAGES]):
            dst = os.path.join(outdir, "%simg_%02d.jpg" % (tag, i))
            try:
                with open(dst, "wb") as f:
                    f.write(http_get(iu))
                saved.append(dst)
            except Exception as e:  # noqa: BLE001
                print("   img fail", i, e)
    else:
        pu = data.get("play") or data.get("wmplay")
        if pu:
            dst = os.path.join(outdir, "%svideo.mp4" % tag)
            try:
                with open(dst, "wb") as f:
                    f.write(http_get(pu))
                saved.append(dst)
            except Exception as e:  # noqa: BLE001
                print("   vid fail", e)
    return saved


def video_frames(path, outdir, n=3):
    code, log = run(["ffprobe", "-v", "error", "-show_entries",
                     "format=duration", "-of", "csv=p=0", path])
    try:
        dur = float(log.strip().splitlines()[0])
    except Exception:  # noqa: BLE001
        dur = 6.0
    outs = []
    base = os.path.splitext(os.path.basename(path))[0]
    for i in range(n):
        t = max(0.1, dur * (i + 1) / (n + 1))
        dst = os.path.join(outdir, "%s_frame%d.jpg" % (base, i))
        run(["ffmpeg", "-y", "-v", "error", "-ss", "%.2f" % t, "-i", path,
             "-frames:v", "1", "-q:v", "3", dst])
        if os.path.exists(dst):
            outs.append(dst)
    return outs


def make_thumbs(paths, key):
    from PIL import Image
    os.makedirs(THUMBS, exist_ok=True)
    made = []
    ims = []
    for i, p in enumerate(paths[:MAX_IMAGES]):
        try:
            im = Image.open(p).convert("RGB")
        except Exception as e:  # noqa: BLE001
            print("   open fail", p, e)
            continue
        w, h = im.size
        nh = int(h * THUMB_W / w)
        im = im.resize((THUMB_W, nh), Image.LANCZOS)
        dst = os.path.join(THUMBS, "%s_%02d.jpg" % (key, i))
        im.save(dst, "JPEG", quality=82)
        made.append(dst)
        ims.append(im)
    if len(ims) > 1:
        cols = min(3, len(ims))
        rows = (len(ims) + cols - 1) // cols
        cw = 340
        ch = int(max(i.size[1] * cw / i.size[0] for i in ims))
        sheet = Image.new("RGB", (cols * cw, rows * ch), (16, 16, 16))
        for idx, im in enumerate(ims):
            t = im.copy()
            t.thumbnail((cw, ch), Image.LANCZOS)
            x = (idx % cols) * cw + (cw - t.size[0]) // 2
            y = (idx // cols) * ch
            sheet.paste(t, (x, y))
        dst = os.path.join(THUMBS, "%s_sheet.jpg" % key)
        sheet.save(dst, "JPEG", quality=80)
        made.append(dst)
    return made


def main():
    os.makedirs(DL, exist_ok=True)
    manifest = []
    with open(os.path.join(ROOT, "urls.txt")) as f:
        entries = [l.split(None, 1) for l in f.read().splitlines() if l.strip()]

    for key, url in entries:
        url = url.strip()
        print("=== %s %s" % (key, url))
        outdir = os.path.join(DL, key)
        shutil.rmtree(outdir, ignore_errors=True)
        os.makedirs(outdir, exist_ok=True)
        rec = {"key": key, "url": url, "method": None, "files": [],
               "images": 0, "notes": ""}

        is_channel = "/photo/" not in url and "/video/" not in url
        media = []

        if not is_channel:
            files, log = yt_dlp_get(url, outdir)
            if files:
                rec["method"] = "yt-dlp"
                media = [os.path.join(outdir, f) for f in files]
            else:
                rec["notes"] = "yt-dlp failed: " + log.replace("\n", " ")[-300:]

        if not media:
            try:
                if is_channel:
                    handle = url.rstrip("/").split("@")[-1]
                    j = tikwm_user(handle, 8)
                    vids = (j.get("data") or {}).get("videos") or []
                    rec["method"] = "tikwm-user"
                    picked = 0
                    for v in vids:
                        if picked >= 3:
                            break
                        det = v
                        if not det.get("images"):
                            try:
                                det = tikwm("https://www.tiktok.com/@%s/video/%s"
                                            % (handle, v.get("video_id")))["data"]
                            except Exception:  # noqa: BLE001
                                pass
                        got = save_media_from_item(det, outdir,
                                                   tag="p%d_" % picked)
                        if got:
                            media += got
                            picked += 1
                    rec["notes"] += " sampled %d recent posts" % picked
                else:
                    j = tikwm(url)
                    if j.get("code") == 0:
                        rec["method"] = (rec["method"] or "") + "+tikwm"
                        media = save_media_from_item(j["data"], outdir)
                    else:
                        rec["notes"] += " tikwm: %s" % j.get("msg")
            except Exception as e:  # noqa: BLE001
                rec["notes"] += " tikwm error: %s" % e

        # expand videos to frames
        expanded = []
        for m in media:
            if m.lower().endswith((".mp4", ".webm", ".mov")):
                expanded += video_frames(m, outdir)
            elif m.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".heic")):
                expanded.append(m)
        expanded = [p for p in expanded if os.path.getsize(p) > 2000]
        rec["images"] = len(expanded)
        rec["files"] = [os.path.relpath(p, ROOT) for p in expanded]
        made = make_thumbs(sorted(expanded), key) if expanded else []
        rec["thumbs"] = [os.path.relpath(p, ROOT) for p in made]
        print("   -> %d media, %d thumbs (%s)" % (len(expanded), len(made),
                                                  rec["method"]))
        manifest.append(rec)

    with open(os.path.join(ROOT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps([{k: r[k] for k in ("key", "method", "images")}
                      for r in manifest], indent=2))


if __name__ == "__main__":
    main()
