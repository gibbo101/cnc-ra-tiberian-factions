#!/usr/bin/env python3
"""Pack TSHARV.ZIP as 64 frames: 0-31 the HARV body facings (the shipped
pipeline: ledger render, +8 face fix, orbit recentre, pack scale 0.75,
baked shadow), 32-63 the HORV body -- TS's UnloadingHarvester, the same
truck with its bed lowered, drawn while the harvester unloads (TS swaps the
image class at draw time; here Shape_Number adds 32).

HORV rides HARV's per-facing recentre shifts (the orbit fit is taken from
HARV's bboxes and applied to both) so the two bodies sit on the same pivot
and the swap is a pure pose change. After packing, run
  scripts/ts_recrop_to_shipped.py <rev> TSHARV
so frames 0-31 keep the shipped crop rects; 32-63 are new and keep their
own centre-symmetric crops (same anchoring contract).

Usage: TS_ART_DIR=~/Desktop/ts-art scripts/ts_pack_tsharv_horv.py
"""
import io, json, math, os, re, zipfile
from PIL import Image

ART = os.environ["TS_ART_DIR"]
MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources", "remaster_mods", "Vanilla_RA"))
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
F_VOX = 6.4 / 12.0
CANVAS, SCALE, SHADOW = 384, 0.75, (6, 25)


def safe_paste(dst, src, x, y):
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy:
        src = src.crop((sx, sy, src.width, src.height))
        x, y = max(0, x), max(0, y)
    dst.paste(src, (x, y), src)


def drop_shadow(frame, dx, dy, alpha=191):
    sil = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    mask = frame.split()[3].point(lambda a: alpha if a > 0 else 0)
    black = Image.new("RGBA", frame.size, (0, 0, 0, 255))
    sil.paste(black, (dx, dy), mask)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.alpha_composite(sil)
    out.alpha_composite(frame)
    return out


def vox_frames(dirname):
    out = []
    for i in range(32):
        im = Image.open(f"{ART}/{dirname}/frame-{i:04d}.png").convert("RGBA")
        f = F_VOX * SCALE
        scaled = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
        fr = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        safe_paste(fr, scaled, round(CANVAS / 2 - scaled.width / 2), round(CANVAS / 2 - scaled.height / 2))
        out.append(fr)
    return out


def face_fix(frames):
    return [frames[(i + 8) % 32] for i in range(32)]


def orbit_shifts(frames):
    n = len(frames)
    boxes = [f.getbbox() for f in frames]
    def fit(vals):
        a = sum(vals) / n
        b = sum(v * math.cos(2 * math.pi * i / n) for i, v in enumerate(vals)) * 2 / n
        c = sum(v * math.sin(2 * math.pi * i / n) for i, v in enumerate(vals)) * 2 / n
        return lambda i: a + b * math.cos(2 * math.pi * i / n) + c * math.sin(2 * math.pi * i / n)
    fx = fit([(b[0] + b[2]) / 2 for b in boxes])
    fy = fit([(b[1] + b[3]) / 2 for b in boxes])
    return [(round(CANVAS / 2 - fx(i)), round(CANVAS / 2 - fy(i))) for i in range(n)]


def shift(frames, shifts):
    out = []
    for f, (dx, dy) in zip(frames, shifts):
        fr = Image.new("RGBA", f.size, (0, 0, 0, 0))
        safe_paste(fr, f, dx, dy)
        out.append(fr)
    return out


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def write_zip(path, name, frames):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            W, H = img.width, img.height
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0, y0 = min(bb[0], W - bb[2]), min(bb[1], H - bb[3])
            b = (x0, y0, W - x0, H - y0)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps({"size": [W, H], "crop": list(b)}))
    print(f"wrote {path} ({len(frames)} frames)")


def tile_block(name, shape, path):
    return (f"\t<Tile>\n\t\t<Key>\n\t\t\t<Name>{name}</Name>\n\t\t\t<Shape>{shape}</Shape>\n\t\t</Key>\n"
            f"\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>{path}</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n")


def patch_tileset(xml_path, name, count):
    sub = name.lower()
    xml = open(xml_path, encoding="utf-8").read()
    xml = re.sub(r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?", "", xml, flags=re.S)
    blocks = "".join(tile_block(name, s, f"{sub}\\{sub}-{s:04d}.tga") for s in range(count))
    idx = xml.rindex("</Tiles>")
    open(xml_path, "w", encoding="utf-8").write(xml[:idx] + blocks + xml[idx:])
    print(f"patched {os.path.basename(xml_path)}: {name} -> {count} tiles")


harv = face_fix(vox_frames("renders_harv"))
horv = face_fix(vox_frames("renders_horv"))
shifts = orbit_shifts(harv)
harv = [drop_shadow(f, *SHADOW) for f in shift(harv, shifts)]
horv = [drop_shadow(f, *SHADOW) for f in shift(horv, shifts)]
write_zip(f"{UNITS_DIR}/TSHARV.ZIP", "tsharv", harv + horv)
patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSHARV", 64)
