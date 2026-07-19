#!/usr/bin/env python3
'''badge_sprite_art.py — composite a faction emblem onto an entity's HD sprite frames.

Rebuilds the entity's idle ZIP from the pristine vanilla MEG source (so re-runs
never stack badges), renames the frames to the entity's IniName, and composites
the emblem at a fixed WORLD position on every frame — the TGA/meta crop contract
means frames are cropped sub-regions of a logical canvas, so the emblem is
placed on the uncropped canvas and each frame is re-emitted full-size with
crop=[0,0,W,H]. MAKE (buildup) archives are left untouched: the emblem arrives
with the finished building.

Used by the W2 faction split: the four construction yards and four MCVs share
era art, and the on-map emblem is what tells twins apart (Luke, 2026-07-19).

Usage: scripts/badge_sprite_art.py            # all eight yard/MCV entities
       scripts/badge_sprite_art.py AFACT AMCV # a subset

License: GPL v3.
'''
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundle_assets import extract_named_zip, MOD_ROOT  # noqa: E402

RA_MEG = Path.home() / ".steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_RA_SRGB.MEG"
TD_MEG = Path.home() / ".steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_TD_SRGB.MEG"
ART = MOD_ROOT / "Data/ART/TEXTURES/SRGB/RED_ALERT"
EMBLEMS = Path(__file__).resolve().parent / "tab_emblems"

# ininame: (meg, source zip basename, dest subdir, emblem file, emblem px, world center)
JOBS = {
    "AFACT":   (RA_MEG, "FACT.ZIP", "STRUCTURES", "allied.png", 72, (192, 120)),
    "SFACT":   (RA_MEG, "FACT.ZIP", "STRUCTURES", "soviet.png", 72, (192, 120)),
    "TDGFACT": (TD_MEG, "FACT.ZIP", "STRUCTURES", "gdi.png",    64, (255, 85)),
    "TDNFACT": (TD_MEG, "FACT.ZIP", "STRUCTURES", "nod.png",    64, (255, 85)),
    "AMCV":    (RA_MEG, "MCV.ZIP",  "UNITS",      "allied.png", 40, (126, 130)),
    "SMCV":    (RA_MEG, "MCV.ZIP",  "UNITS",      "soviet.png", 40, (126, 130)),
    "TDGMCV":  (TD_MEG, "MCV.ZIP",  "UNITS",      "gdi.png",    40, (130, 132)),
    "TDNMCV":  (TD_MEG, "MCV.ZIP",  "UNITS",      "nod.png",    40, (130, 132)),
}


def load_emblem(name, box):
    im = Image.open(EMBLEMS / name).convert("RGBA")
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    r = min(box / im.width, box / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def badge(ininame):
    meg, src_name, sub, emb_name, emb_px, (cx, cy) = JOBS[ininame]
    emb = load_emblem(emb_name, emb_px)
    tmp = Path(tempfile.gettempdir()) / f"_badge_{src_name}"
    if not extract_named_zip(meg, src_name, tmp):
        raise SystemExit(f"{src_name} not found in {meg}")
    src_base = src_name[:-4].lower()          # frame prefix inside the source zip
    dst_base = ininame.lower()
    dest = ART / sub / f"{ininame}.ZIP"
    with zipfile.ZipFile(tmp) as s, zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as d:
        metas = {}
        for info in s.infolist():
            low = info.filename.lower()
            if low.endswith(".meta"):
                metas[low[:-5]] = json.loads(s.read(info))
        for info in s.infolist():
            low = info.filename.lower()
            if not low.endswith(".tga"):
                if not low.endswith(".meta"):
                    d.writestr(info.filename, s.read(info))
                continue
            stem = low[:-4]
            meta = metas[stem]
            W, H = meta["size"]
            x0, y0 = meta["crop"][0], meta["crop"][1]
            full = Image.new("RGBA", (W, H))
            full.alpha_composite(Image.open(io.BytesIO(s.read(info))).convert("RGBA"), (x0, y0))
            full.alpha_composite(emb, (cx - emb.width // 2, cy - emb.height // 2))
            out_stem = stem.replace(src_base, dst_base, 1)
            buf = io.BytesIO()
            full.save(buf, format="TGA")
            d.writestr(out_stem + ".tga", buf.getvalue())
            d.writestr(out_stem + ".meta", json.dumps({"size": [W, H], "crop": [0, 0, W, H]}))
    tmp.unlink()
    frames = len(metas)
    print(f"  {ininame}: {frames} frames badged ({emb_name} @{cx},{cy}) -> {dest.relative_to(MOD_ROOT)}")


def main():
    names = sys.argv[1:] or list(JOBS)
    for n in names:
        badge(n)


if __name__ == "__main__":
    main()
