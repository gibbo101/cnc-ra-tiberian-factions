#!/usr/bin/env python3
"""Prepare the asset packs for the Steam Workshop: upload folders, uploader manifests, previews.

Usage:  asset_pack_workshop.py [PACK ...]      (no arguments: every pack)

For each pack in asset-packs/:
  dist/asset-pack-uploads/<Pack>/<Pack>/   the upload: the pack folder inside a named subfolder,
                                           the layout the game's Workshop scanner needs for the
                                           pack to show in the in-game mod list (as TD-Assets does)
  tools/workshop-uploader/packs/<Pack>.json  the uploader manifest: BBCode description built from
                                           the pack's contents, the RA tags, and the upload folder.
                                           A manifest that exists keeps its publishedfileid and
                                           visibility; a new one starts Private (2), to be
                                           promoted after a self-test.
  tools/workshop-uploader/packs/<Pack>.jpg   a 1200x1200 preview under the uploader's 1 MB limit:
                                           the pack's cameos or sprites, or for a sound pack the
                                           waveform of one of its own sounds, under its name.

Publish one with:  cd tools/workshop-uploader && dotnet run --no-build -- packs/<Pack>.json "change note"

License: GPL v3.
"""
import io
import json
import os
import re
import subprocess
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs as A  # noqa: E402
import asset_pack_docs as DOCS  # noqa: E402

UPLOADS = os.path.join(A.REPO, "dist", "asset-pack-uploads")
MANIFESTS = os.path.join(A.REPO, "tools", "workshop-uploader", "packs")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SIZE = 1200
BG = (18, 22, 18)
GREEN = (92, 200, 92)
GREY = (190, 196, 190)
DESCRIPTION_LIMIT = 8000


def stage(pack):
    dst = os.path.join(UPLOADS, pack, pack)
    os.makedirs(dst, exist_ok=True)
    subprocess.run(["rsync", "-a", "--delete", os.path.join(A.PACKS_DIR, pack) + "/", dst + "/"], check=True)
    return os.path.relpath(os.path.join(UPLOADS, pack), MANIFESTS)


def bbcode(pack):
    """The Workshop description: what the pack is, its contents, how to use it, credits, links."""
    game = DOCS.GAMES[A.PACKS[pack].replace("TSHD", "TS")]
    out = [f"[h1]{pack}[/h1]",
           f"{DOCS.ABOUT[pack]}, for Command & Conquer Remastered Collection mods (Red Alert). One of the "
           f"asset packs from [url={DOCS.REPO_URL}]Tiberian Factions[/url].",
           "",
           "You do not need this pack to play Tiberian Factions: the mod already includes everything in it. "
           "It is here for other modders to use in their own mods.",
           "", "[h2]Contents[/h2]", "[list]"]
    for title, names in DOCS.listing(pack).items():
        out.append(f"[*][b]{title}[/b] ({len(names)}): " + ", ".join(names))
    out += ["[/list]", "", "[h2]Using it[/h2]", "[olist]",
            "[*]Copy the files under this pack's Data folder into your mod's Data folder, keeping the paths.",
            "[*]Copy the entries you need from this pack's XML files into your mod's own XML files:", "[list]"]
    out += [f"[*]{src} into {dst}" for src, dst in DOCS.xml_targets(pack)]
    out += ["[/list]The launcher only reads the mod's own files, so enabling the pack by itself changes nothing in game."]
    if "Graphics" in pack:
        out += ["[*]The game also needs a classic-mode SHP for every sprite, with the same frame count. A transparent "
                f"stub is enough: Tiberian Factions makes its stubs with scripts/gen_stub_shp.py "
                f"([url={DOCS.REPO_URL}]GitHub[/url]).",
                "[*]Units with one frame per facing, plus a turret block where they have one, use the stock layout. "
                "Units with rolling treads, walking gaits or offset turrets use Tiberian Factions' own layouts and "
                "need the matching DLL code, which is in the repo."]
    out += ["[/olist]",
            f"The pack's README on [url={DOCS.REPO_URL}/tree/main/asset-packs/{pack}]GitHub[/url] has the same notes.",
            "", "[h2]Credits[/h2]",
            f"Original {game} assets: Electronic Arts. Prepared for Remastered by gibbo101 for Tiberian Factions."]
    if pack in DOCS.CREDIT:
        out.append(DOCS.CREDIT[pack])
    out += ["", "[h2]More C&C projects by gibbo101[/h2]", "[list]"]
    for mod in DOCS.MORE_MODS:
        out.append("[*]" + re.sub(r"\*\*(.+?)\*\*", r"[b]\1[/b]", re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[url=\2]\1[/url]", mod)))
    out.append("[/list]")
    text = "\n".join(out)
    if len(text) > DESCRIPTION_LIMIT:
        raise SystemExit(f"{pack}: description is {len(text)} characters, over the Workshop's {DESCRIPTION_LIMIT}")
    return text


def manifest(pack, content):
    path = os.path.join(MANIFESTS, f"{pack}.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    data = {
        "appid": 1213210,
        "publishedfileid": old.get("publishedfileid", ""),
        "contentfolder": content,
        "previewfile": f"{pack}.jpg",
        "visibility": old.get("visibility", 2),
        "title": pack,
        "description": bbcode(pack),
        "tags": ["RA", "RedAlertMod"],
        "metadata": "",
    }
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    return path, len(data["description"])


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


# Packs whose preview shows chosen objects (name, art kind) rather than its cameos
SHOWCASE = {
    "TS-HD-Graphics-Pack": [("TSCTWR", "STRUCTURES"), ("TSVULCT", "STRUCTURES"), ("TSROCKT", "STRUCTURES"),
                            ("TSCSAMT", "STRUCTURES"), ("TSGATEH", "STRUCTURES"), ("TSNGATEH", "STRUCTURES")],
}


def first_frame(name, kind):
    with zipfile.ZipFile(A.art_zip(name, kind)) as z:
        tga = sorted(n for n in z.namelist() if n.lower().endswith(".tga"))
        return Image.open(io.BytesIO(z.read(tga[0]))).convert("RGBA")


def waveform(pack):
    """A sound from the pack as (samples, name), decoded to 8 kHz mono."""
    data = A.pack_data(pack)
    wavs = []
    for sub in (os.path.join("AUDIO", "EN-US"), "AUDIO"):
        d = os.path.join(data, sub)
        if os.path.isdir(d):
            wavs += [os.path.join(d, f) for f in os.listdir(d) if f.upper().endswith(".WAV")]
    if not wavs:
        return None, ""
    wav = max(wavs, key=os.path.getsize)
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-f", "s16le", "-ac", "1", "-ar", "8000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, dtype=np.int16).astype(float), os.path.basename(wav)[:-4]


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


def preview(pack):
    img = Image.new("RGBA", (SIZE, SIZE), BG + (255,))
    d = ImageDraw.Draw(img)
    art = (60, 250, SIZE - 60, SIZE - 120)
    if pack in SHOWCASE:
        img.alpha_composite(tile([first_frame(n, k) for n, k in SHOWCASE[pack]], art), art[:2])
    elif "Graphics" in pack:
        pictures = [Image.open(p).convert("RGBA") for p in cameos(pack)[:12]]
        if len(pictures) < 4:
            pictures += sprite_frames(pack, 9 - len(pictures))
        img.alpha_composite(tile(pictures, art), art[:2])
    else:
        samples, name = waveform(pack)
        if samples is not None and len(samples):
            w, h = art[2] - art[0], art[3] - art[1]
            mid = art[1] + h // 2
            cols = np.array_split(np.abs(samples), w // 4)
            peak = max(float(np.max(np.abs(samples))), 1.0)
            for i, c in enumerate(cols):
                a = int((float(c.max()) / peak) * (h * 0.45)) if len(c) else 0
                x = art[0] + i * 4
                d.rectangle((x, mid - a, x + 2, mid + a), fill=GREEN)
            d.text((art[0], art[3] + 10), name, font=ImageFont.truetype(FONT_REGULAR, 26), fill=GREY)
    title = ImageFont.truetype(FONT, 84)
    sub = ImageFont.truetype(FONT_REGULAR, 34)
    d.text((60, 60), pack, font=title, fill=GREEN)
    size = 34
    while size > 18 and d.textlength(DOCS.ABOUT[pack], font=ImageFont.truetype(FONT_REGULAR, size)) > SIZE - 120:
        size -= 1
    d.text((60, 165), DOCS.ABOUT[pack], font=ImageFont.truetype(FONT_REGULAR, size), fill=GREY)
    d.text((60, SIZE - 70), "For C&C Remastered mods  |  from Tiberian Factions", font=sub, fill=GREY)
    path = os.path.join(MANIFESTS, f"{pack}.jpg")
    for quality in (90, 85, 80, 70):
        img.convert("RGB").save(path, quality=quality)
        if os.path.getsize(path) < 1_000_000:
            break
    return path


def main(packs):
    os.makedirs(MANIFESTS, exist_ok=True)
    for pack in packs:
        content = stage(pack)
        path, chars = manifest(pack, content)
        jpg = preview(pack)
        print(f"{pack:22s} upload dist/asset-pack-uploads/{pack}/  manifest {os.path.basename(path)} "
              f"({chars} chars)  preview {os.path.getsize(jpg) // 1024} KB")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(A.PACKS)
    unknown = [p for p in wanted if p not in A.PACKS]
    if unknown:
        raise SystemExit(f"unknown pack(s): {', '.join(unknown)}")
    main(wanted)
