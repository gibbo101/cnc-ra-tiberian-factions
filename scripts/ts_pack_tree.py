#!/usr/bin/env python3
"""Package TS GDI tree art into the mod tree (docs/ts-gdi-tree-plan.md).

Per-entity sections accumulate as the tree grows; each guards on its render
inputs so the script can be re-run for any subset. Contracts honored
(docs/launcher-render-contracts.md + ts-asset-import-spike.md traps):
  - HD canvas = classic donor frame dims x 5.33 (FACT 72x72 -> 384, MCV 48 -> 384 @8x)
  - TGAs cropped to content; meta size = virtual canvas, crop = corner bounds
  - shape count mirrors the classic donor (FACT 52, FACTMAKE 32)
  - hq4x for TS-SHP buildings, voxel renders land pre-scaled from vxl_render.py

Inputs: $TS_ART_DIR holding shp_gtcnst/, shp_gtcnstmk/, shp_mcvicon/,
renders_tsmcv/ (ts_shp.py + vxl_render.py outputs).
"""
import io, json, os, zipfile
from PIL import Image
import hqx

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR")
MOD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "resources/remaster_mods/Vanilla_RA")
MOD = os.path.abspath(MOD)
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
STRUCT_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES"
ICON_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB"


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def hq_scale(img, factor):
    """hq4x the color (over black), NEAREST+LANCZOS the alpha, downsample to
    target factor (the ts_stealth_hq.py recipe)."""
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    up = hqx.hq4x(rgb)
    w, h = round(img.width * factor), round(img.height * factor)
    color = up.resize((w, h), Image.LANCZOS)
    alpha = img.split()[3].resize((img.width * 8, img.height * 8), Image.NEAREST).resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(color, (0, 0))
    out.putalpha(alpha.point(lambda a: 255 if a >= 128 else 0))
    return out


def scale_center(img, factor, canvas):
    nw, nh = round(img.width * factor), round(img.height * factor)
    scaled = img.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    out.paste(scaled, ((canvas - nw) // 2, (canvas - nh) // 2), scaled)
    return out


def write_zip(path, name, frames):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            b = img.getbbox() or (0, 0, img.width, img.height)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps(
                {"size": [img.width, img.height], "crop": [b[0], b[1], b[2], b[3]]}))
    print(f"wrote {path} ({len(frames)} frames)")


def tile_block(name, shape, frame_path):
    return ("\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n"
            "\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n"
            % (name, shape, frame_path))


def patch_tileset(xml_path, name, count):
    xml = open(xml_path, encoding="utf-8").read()
    if f"<Name>{name}</Name>" in xml:
        print(f"{name} already in {os.path.basename(xml_path)}, skipping")
        return
    blocks = "".join(tile_block(name, s, f"{name.lower()}\\{name.lower()}-{s:04d}.tga") for s in range(count))
    idx = xml.rindex("</Tiles>")
    xml = xml[:idx] + blocks + xml[idx:]
    open(xml_path, "w", encoding="utf-8").write(xml)
    print(f"patched {os.path.basename(xml_path)}: +{count} {name} tiles")


# ---- TSFACT (TS Construction Yard, GTCNST 144-canvas -> 384) ----
# GTCNST frames: 0 healthy, 1 damaged, 2 wrecked (unused), 3-5 palette-anim
# overlays (unused). Donor FACT = 52 shapes (26 healthy anim + 26 damaged) --
# the crane loop collapses to statics (custom launcher anims are dead anyway).
if os.path.isdir(f"{ART}/shp_gtcnst"):
    F = 384.0 / 144.0
    healthy = hq_scale(Image.open(f"{ART}/shp_gtcnst/frame-0000.png").convert("RGBA"), F)
    damaged = hq_scale(Image.open(f"{ART}/shp_gtcnst/frame-0001.png").convert("RGBA"), F)
    write_zip(f"{STRUCT_DIR}/TSFACT.ZIP", "tsfact", [healthy] * 26 + [damaged] * 26)

    picks = [round(i * 47 / 31) for i in range(32)]  # 48 TS buildup frames -> donor's 32
    mk = [hq_scale(Image.open(f"{ART}/shp_gtcnstmk/frame-{p:04d}.png").convert("RGBA"), F) for p in picks]
    write_zip(f"{STRUCT_DIR}/TSFACTMAKE.ZIP", "tsfactmake", mk)

    patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", "TSFACT", 52)
    patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", "TSFACTMAKE", 32)

# ---- TSMCV (MCV.VXL render, 32 facings, canvas 384 = classic 48 x 8) ----
if os.path.isdir(f"{ART}/renders_tsmcv"):
    CANVAS = 384
    side = Image.open(f"{ART}/renders_tsmcv/frame-0008.png")
    b = side.getbbox()
    factor = 280.0 / (b[2] - b[0])  # hull ~73% of canvas, the MLRS proportion
    frames = [scale_center(Image.open(f"{ART}/renders_tsmcv/frame-{i:04d}.png"), factor, CANVAS)
              for i in range(32)]
    write_zip(f"{UNITS_DIR}/TSMCV.ZIP", "tsmcv", frames)
    patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSMCV", 32)

# ---- BuildIcon for the (future-buildable) TSMCV ----
if os.path.isdir(f"{ART}/shp_mcvicon"):
    icon = Image.open(f"{ART}/shp_mcvicon/frame-0000.png")
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(f"{ICON_DIR}/BuildIcon_TS_MCV.tga")
    print(f"wrote {ICON_DIR}/BuildIcon_TS_MCV.tga")

print("DONE")
