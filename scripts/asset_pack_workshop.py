#!/usr/bin/env python3
"""Prepare the Workshop asset-pack items for upload: their folders, uploader manifests and previews.

Usage:  asset_pack_workshop.py [ITEM ...]      (no arguments: every item in asset_packs.items)

For each item (a Workshop pack for one game: <mod>, or <mod>-TD for Tiberian Dawn):
  dist/asset-pack-uploads/<Item>/<Item>/     the mod as scripts/workshop_packs.py builds it, inside a named
                                             subfolder, the layout the game's Workshop scanner needs for the
                                             item to show in the in-game mod list
  tools/workshop-uploader/packs/<Item>.json  the uploader manifest: title, BBCode description from the item's
                                             README, the game's tags and the upload folder. A manifest that
                                             exists keeps its publishedfileid and visibility; a new one starts
                                             Private (2), to be promoted after a self-test.
  tools/workshop-uploader/packs/<Item>.jpg   the preview, under the uploader's 1 MB limit: the pack's
                                             in-game shot from resources/workshop-previews/<mod>.jpg, or else
                                             its art tiled under its name.

Publish one with:  cd tools/workshop-uploader && dotnet run --no-build -- packs/<Item>.json "change note"

License: GPL v3.
"""
import io
import json
import os
import re
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs as A  # noqa: E402
import workshop_packs as W  # noqa: E402

UPLOADS = os.path.join(A.REPO, "dist", "asset-pack-uploads")
MANIFESTS = os.path.join(A.REPO, "tools", "workshop-uploader", "packs")
SHOTS = os.path.join(A.REPO, "resources", "workshop-previews")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SIZE = 1200
BG = (18, 22, 18)
GREEN = (92, 200, 92)
GREY = (190, 196, 190)
DESCRIPTION_LIMIT = 8000
TAGS = {"RA": ["RA", "RedAlertMod"], "TD": ["TD", "TiberianDawnMod"]}


def stage(item, mod, host):
    folder = os.path.join(UPLOADS, item, item)
    W.build(mod, folder, host)
    return folder, os.path.relpath(os.path.join(UPLOADS, item), MANIFESTS)


def inline(text):
    """Markdown links, bold and code spans as BBCode."""
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[url=\2]\1[/url]", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"[b]\1[/b]", text)
    return re.sub(r"`([^`]+)`", r"\1", text)


def bbcode(readme):
    """The item's README.md as a Workshop description."""
    out, in_list = [], None
    for line in readme.splitlines():
        bullet = re.match(r"(\d+\.|-) (.*)", line)
        if bullet:
            kind = "olist" if bullet.group(1)[0].isdigit() else "list"
            if in_list != kind:
                if in_list:
                    out.append(f"[/{in_list}]")
                out.append(f"[{kind}]")
                in_list = kind
            out.append("[*]" + inline(bullet.group(2)))
            continue
        if in_list and line.strip():
            out.append(f"[/{in_list}]")
            in_list = None
        heading = re.match(r"(#+) (.*)", line)
        if heading:
            out.append(f"[h{len(heading.group(1))}]{inline(heading.group(2))}[/h{len(heading.group(1))}]")
        elif line.strip() or (out and out[-1]):
            out.append(inline(line))
    if in_list:
        out.append(f"[/{in_list}]")
    return "\n".join(out).strip() + "\n"


def title(mod, host):
    return f"{A.WORKSHOP[mod]['name']} for {A.HOSTS[host]['name']}"


def manifest(item, mod, host, folder, content):
    path = os.path.join(MANIFESTS, f"{item}.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    description = bbcode(open(os.path.join(folder, "README.md"), encoding="utf-8").read())
    if len(description) > DESCRIPTION_LIMIT:
        raise SystemExit(f"{item}: description is {len(description)} characters, over the Workshop's "
                         f"{DESCRIPTION_LIMIT}")
    data = {
        "appid": 1213210,
        "publishedfileid": old.get("publishedfileid", ""),
        "contentfolder": content,
        "previewfile": f"{item}.jpg",
        "visibility": old.get("visibility", 2),
        "title": title(mod, host),
        "description": description,
        "tags": TAGS[host],
        "metadata": "",
    }
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    return path, len(description)


def cameos(pack):
    srgb = os.path.join(A.pack_data(pack), "ART", "TEXTURES", "SRGB")
    if not os.path.isdir(srgb):
        return []
    return sorted(os.path.join(srgb, f) for f in os.listdir(srgb) if f.lower().endswith(".tga"))


def sprite_frames(pack, limit):
    """The first frame of up to `limit` of the pack's sprite ZIPs, largest art first."""
    zips = []
    for kind in A.KINDS:
        d = os.path.join(A.pack_data(pack), "ART", "TEXTURES", "SRGB", "RED_ALERT", A.kind_dir(kind))
        if os.path.isdir(d):
            zips += [os.path.join(d, f) for f in os.listdir(d) if f.upper().endswith(".ZIP")
                     and not re.search(r"(MAKE|BB|L|X)\.ZIP$", f.upper())]
    zips.sort(key=os.path.getsize, reverse=True)
    frames = []
    for path in zips[:limit]:
        with zipfile.ZipFile(path) as z:
            tga = sorted(n for n in z.namelist() if n.lower().endswith(".tga"))
            if tga:
                frames.append(Image.open(io.BytesIO(z.read(tga[0]))).convert("RGBA"))
    return frames


# Mods whose tiled preview shows chosen objects (name, art kind) rather than their cameos
SHOWCASE = {
    "TS-HD-Assets": [("TSCTWR", "STRUCTURES"), ("TSVULCT", "STRUCTURES"), ("TSROCKT", "STRUCTURES"),
                     ("TSCSAMT", "STRUCTURES"), ("TSGATEH", "STRUCTURES"), ("TSNGATEH", "STRUCTURES")],
}


def first_frame(name, kind):
    with zipfile.ZipFile(A.art_zip(name, kind)) as z:
        tga = sorted(n for n in z.namelist() if n.lower().endswith(".tga"))
        return Image.open(io.BytesIO(z.read(tga[0]))).convert("RGBA")


def tile(images, box):
    """Images fitted into a grid inside box (x0, y0, x1, y1), each kept to its aspect."""
    x0, y0, x1, y1 = box
    n = len(images)
    cols = int(np.ceil(np.sqrt(n * (x1 - x0) / (y1 - y0))))
    rows = int(np.ceil(n / cols))
    cw, ch = (x1 - x0) // cols, (y1 - y0) // rows
    canvas = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    for i, im in enumerate(images):
        bb = im.getbbox() or (0, 0, im.width, im.height)
        im = im.crop(bb)
        k = min((cw - 16) / im.width, (ch - 16) / im.height)
        im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
        cx, cy = (i % cols) * cw + (cw - im.width) // 2, (i // cols) * ch + (ch - im.height) // 2
        canvas.alpha_composite(im, (cx, cy))
    return canvas


def tiled(mod, host):
    """The mod's art tiled under its name and game."""
    w = A.WORKSHOP[mod]
    img = Image.new("RGBA", (SIZE, SIZE), BG + (255,))
    d = ImageDraw.Draw(img)
    art = (60, 250, SIZE - 60, SIZE - 120)
    if mod in SHOWCASE:
        pictures = [first_frame(n, k) for n, k in SHOWCASE[mod]]
    else:
        pictures = [Image.open(p).convert("RGBA") for pack in w["packs"] for p in cameos(pack)][:12]
        if len(pictures) < 4:
            pictures += [f for pack in w["packs"] for f in sprite_frames(pack, 9 - len(pictures))]
    img.alpha_composite(tile(pictures, art), art[:2])
    d.text((60, 60), w["name"], font=ImageFont.truetype(FONT, 84), fill=GREEN)
    about = w["description"].format(host=A.HOSTS[host]["name"])
    size = 34
    while size > 18 and d.textlength(about, font=ImageFont.truetype(FONT_REGULAR, size)) > SIZE - 120:
        size -= 1
    d.text((60, 165), about, font=ImageFont.truetype(FONT_REGULAR, size), fill=GREY)
    d.text((60, SIZE - 70), "For C&C Remastered mods", font=ImageFont.truetype(FONT_REGULAR, 34), fill=GREY)
    return img


def preview(item, mod, host):
    shot = os.path.join(SHOTS, f"{mod}.jpg")
    img = Image.open(shot) if os.path.exists(shot) else tiled(mod, host)
    path = os.path.join(MANIFESTS, f"{item}.jpg")
    for quality in (92, 85, 80, 70):
        img.convert("RGB").save(path, quality=quality)
        if os.path.getsize(path) < 1_000_000:
            return path
    raise SystemExit(f"{item}: preview is over the uploader's 1 MB limit")


def main(wanted):
    os.makedirs(MANIFESTS, exist_ok=True)
    known = {i: (mod, host) for i, mod, host in A.items()}
    unknown = [i for i in wanted if i not in known]
    if unknown:
        raise SystemExit(f"unknown item(s): {', '.join(unknown)} (items: {', '.join(known)})")
    for item in wanted or list(known):
        mod, host = known[item]
        folder, content = stage(item, mod, host)
        path, chars = manifest(item, mod, host, folder, content)
        jpg = preview(item, mod, host)
        print(f"{item:20s} upload dist/asset-pack-uploads/{item}/  manifest {os.path.basename(path)} "
              f"({chars} chars)  preview {os.path.getsize(jpg) // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
