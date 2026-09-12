#!/usr/bin/env python3
"""Package Tiberian Sun infantry as HD unit art: tileset, cameo, sidebar entry and text.

A TS infantry SHP holds the pose frames first and the same number of shadow frames
after them (shadow frame i + N belongs to pose frame i). Each pose is composited over
its own TS shadow, upscaled so the figure stands as tall as RA's Rifle Infantry and
the TD Minigunner (63 HD px), and placed on the Minigunner's HD canvas (267x208) with
the feet on the Minigunner's feet, so the E1 render box the DLL borrows as the donor
frames them. TS draws infantry facings anticlockwise from north, the order the
engine's HumanShape indexes, so frames keep TS's order and the DO table in idata.cpp
indexes them directly.

Writes, per unit: UNITS/<INI>.ZIP + its RA_UNITS.XML tile run, BuildIcon_TS_<Name>.tga
from the TS cameo, the base RA_<INI> / RA_<INI>_0 RABUILDABLES entries and the ModText
rows. The TS-badged _G variant comes from the TS-tree badge tooling, not from here.

Inputs (set TS_ART_DIR): shp_<shp> decoded against UNITTEM.PAL and shp_<cameo> against
CAMEO.PAL (scripts/ts_shp.py).

  ts_pack_infantry.py [INI ...]      default: every unit in UNITS

License: GPL v3.
"""
import io, json, os, sys, zipfile
from PIL import Image
import hqx

HERE = os.path.dirname(os.path.abspath(__file__))

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the extracted/rendered TS art directory")
MOD = os.environ.get("TF_MOD_DIR", os.path.normpath(os.path.join(HERE, "..", "resources/remaster_mods/Vanilla_RA")))
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
ICON_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB"
UNITS_XML = f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML"
RAB = f"{MOD}/Data/XML/OBJECTS/UNITS/RABUILDABLES.XML"
CSV = f"{MOD}/Data/ModText.csv"

CANVAS = (267, 208)          # the TD Minigunner's HD canvas
FEET_DST = (133.5, 111.0)    # the Minigunner's feet on that canvas
FEET_SRC = (31.0, 32.0)      # TS infantry feet on the 61x61 SHP canvas
SCALE = 3.25                 # a 19.5 px TS figure to the Minigunner's 63 px height
SHADOW_RGB = (170, 0, 170)   # how ts_shp.py decodes the TS shadow index
SHADOW_ALPHA = 128

# ini -> (SHP stem, pose frame count, cameo stem, icon name, display name, description)
UNITS = {
    "TSE1": ("e1", 292, "e1icon", "BuildIcon_TS_E1", "Light Infantry",
             "Basic GDI infantry armed with a minigun."),
    "TSE2": ("e2", 292, "e2icon", "BuildIcon_TS_E2", "Disc Thrower",
             "GDI infantry that lobs explosive discs over walls and cover."),
    "TSENGINEER": ("engineer", 292, "engnicon", "BuildIcon_TS_Engineer", "Engineer",
                   "Captures enemy structures outright and restores friendly ones to full strength."),
}

# ini -> (TS projectile SHP in $TS_ART_DIR/.raw, VFX tileset name). The projectile ships as
# a full 32-tile set, its frames cycled round, so any shape index the launcher asks for
# has a tile (the RPG tower canister's contract); its classic stub is in build_tfassets.sh.
PROJECTILES = {
    "TSE2": ("DISCUS.SHP", "TSDISCUS"),
}


def write_zip(path, name, frames):
    """TGA + meta per frame. The launcher anchors the canvas centre at the object's
    draw position; crops are kept centre-symmetric so the placement is the same
    whichever way a launcher path reads them (launcher-render-contracts.md #1)."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            w, h = img.size
            bb = img.getbbox() or (w // 2 - 1, h // 2 - 1, w // 2 + 1, h // 2 + 1)
            x0, y0 = min(bb[0], w - bb[2]), min(bb[1], h - bb[3])
            box = (x0, y0, w - x0, h - y0)
            buf = io.BytesIO()
            img.crop(box).save(buf, format="TGA")
            z.writestr(base + ".tga", buf.getvalue())
            z.writestr(base + ".meta", json.dumps({"size": [w, h], "crop": list(box)}))
    print(f"wrote {path} ({len(frames)} frames)")


def safe_paste(dst, src, x, y):
    """Paste with the source's alpha; negative offsets pre-crop the source, since
    Pillow's masked paste corrupts output for them."""
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy:
        src = src.crop((sx, sy, src.width, src.height))
        x, y = max(0, x), max(0, y)
    dst.paste(src, (x, y), src)


def frame(stem, i):
    return Image.open(f"{ART}/shp_{stem}/frame-{i:04d}.png").convert("RGBA")


def with_shadow(pose, shadow):
    """The pose over its TS shadow: shadow-index pixels become translucent black."""
    px = shadow.load()
    sh = Image.new("RGBA", shadow.size, (0, 0, 0, 0))
    spx = sh.load()
    for y in range(shadow.height):
        for x in range(shadow.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) == SHADOW_RGB:
                spx[x, y] = (0, 0, 0, SHADOW_ALPHA)
    sh.alpha_composite(pose)
    return sh


def place(img):
    """hq4x for edge quality, LANCZOS to the scale, feet on the Minigunner's feet."""
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    big = hqx.hq4x(rgb).convert("RGBA")
    big.putalpha(img.split()[3].resize((img.width * 4, img.height * 4), Image.LANCZOS))
    scaled = big.resize((round(img.width * SCALE), round(img.height * SCALE)), Image.LANCZOS)
    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    safe_paste(out, scaled, round(FEET_DST[0] - FEET_SRC[0] * SCALE), round(FEET_DST[1] - FEET_SRC[1] * SCALE))
    return out


def patch_tileset(name, count):
    xml = open(UNITS_XML, encoding="utf-8").read()
    if f"<Name>{name}</Name>" in xml:
        print(f"{name} already in RA_UNITS.XML, left as is")
        return
    tile = ("\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n"
            "\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n")
    blocks = "".join(tile % (name, s, f"{name.lower()}\\{name.lower()}-{s:04d}.tga") for s in range(count))
    idx = xml.rindex("</Tiles>")
    open(UNITS_XML, "w", encoding="utf-8").write(xml[:idx] + blocks + xml[idx:])
    print(f"patched RA_UNITS.XML: +{count} {name} tiles")


def cameo(stem, icon):
    icon_img = Image.open(f"{ART}/shp_{stem}/frame-0000.png").convert("RGBA")
    big = icon_img.resize((icon_img.width * 8, icon_img.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(f"{ICON_DIR}/{icon}.tga")
    print(f"wrote {icon}.tga")


HAND_END = "\t<!-- END hand-written TS-tree base cameo entries -->"


def sidebar(ini, icon):
    """The base RA_<INI> entry naming the pristine cameo, in the hand-written TS-tree
    block. The _0 and _G variants are generated from it: add the type to
    cameo_work/faction_masks.txt, run cameo_badge_build.py <INI> for the badged art,
    then cameo_variants_build.py."""
    xml = open(RAB, encoding="utf-8").read()
    key = f"RA_{ini}"
    if f'"{key}"' in xml:
        return
    if HAND_END not in xml:
        raise SystemExit("RABUILDABLES.XML has no hand-written TS-tree block; place the entry by hand")
    entry = ('\t<ObjectTypeClass Name="%s" Classification="CNCBuildableObject" CanInstantiate="False">\n'
             "\t\t<CNCEncyclopediaComponent>\n"
             "\t\t\t<ObjectNameTextID>TEXT_UNIT_%s</ObjectNameTextID>\n"
             "\t\t\t<ObjectDescriptionTextID>TEXT_UNIT_%s_DESC</ObjectDescriptionTextID>\n"
             "\t\t\t<BuildIcon>%s</BuildIcon>\n"
             "\t\t</CNCEncyclopediaComponent>\n"
             "\t</ObjectTypeClass>\n" % (key, ini, ini, icon))
    open(RAB, "w", encoding="utf-8").write(xml.replace(HAND_END, entry + HAND_END, 1))
    print(f"patched RABUILDABLES.XML: {key}")


def text_rows(ini, display, desc):
    raw = open(CSV, "rb").read()
    text = raw.decode("utf-16")
    eol = "\r\n" if "\r\n" in text else "\n"
    sample = next(l for l in text.splitlines() if l.startswith('"TEXT_UNIT_TDA10"'))
    tail = sample.split('"A-10 Warthog"', 1)[1]
    new = ""
    for key, val in ((f"TEXT_UNIT_{ini}", display), (f"TEXT_UNIT_{ini}_DESC", desc)):
        if f'"{key}"' not in text:
            new += f'"{key}",,,"{val}"{tail}{eol}'
    if new:
        if not text.endswith(eol):
            text += eol
        open(CSV, "wb").write((text + new).encode("utf-16"))
        print(f"patched ModText.csv: TEXT_UNIT_{ini}")


def pack(ini):
    stem, poses, cameo_stem, icon, display, desc = UNITS[ini]
    frames = [place(with_shadow(frame(stem, i), frame(stem, i + poses))) for i in range(poses)]
    write_zip(f"{UNITS_DIR}/{ini}.ZIP", ini.lower(), frames)
    patch_tileset(ini, poses)
    cameo(cameo_stem, icon)
    sidebar(ini, icon)
    text_rows(ini, display, desc)
    if ini in PROJECTILES:
        import ts_pack_towerfx, ts_shp
        shp, name = PROJECTILES[ini]
        pal = ts_shp.load_pal(f"{ART}/.raw/UNITTEM.PAL")
        ts_pack_towerfx.pack(shp, name, pal, order=lambda k, n: k % n, count=32)


if __name__ == "__main__":
    for ini in (sys.argv[1:] or list(UNITS)):
        pack(ini)
