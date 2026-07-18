#!/usr/bin/env python3
"""Package the TS-spike art into the mod tree:
  - TSHVR.ZIP        64 frames (body 0-31 + turret 32-63), 192px canvas
  - TSPOWR.ZIP       2 frames (healthy, damaged), 256px canvas
  - TSPOWRMAKE.ZIP   13 buildup frames, 256px canvas
  - RA_UNITS.XML / RA_STRUCTURES.XML tile runs
  - RABUILDABLES.XML entries + ModText.csv strings
  - loose BuildIcon_TS_*.tga cameos
"""
import io, json, os, re, zipfile
from PIL import Image

SCRATCH = os.environ.get("TS_RENDER_DIR", os.path.dirname(os.path.abspath(__file__)))
MOD = "/home/gibbo101/Documents/development/cnc-remastered-mods/cnc-ra-tiberian-factions/resources/remaster_mods/Vanilla_RA"
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
STRUCT_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES"
ICON_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB"


def crop_box(img):
    b = img.getbbox()
    if b is None:
        return [0, 0, img.width, img.height]
    return [b[0], b[1], b[2], b[3]]  # corner bounds x0,y0,x1,y1 — NOT w/h (2TNK: 59+134>192 proves it)


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def scale_center(img, factor, canvas):
    """Scale full source canvas by factor (center-anchored) onto canvas px square."""
    nw, nh = round(img.width * factor), round(img.height * factor)
    scaled = img.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    out.paste(scaled, ((canvas - nw) // 2, (canvas - nh) // 2), scaled)
    return out


def crisp_scale(img, factor, canvas):
    """Pixel-art friendly: NEAREST up 8x then LANCZOS to target, center-anchored."""
    big = img.resize((img.width * 8, img.height * 8), Image.NEAREST)
    nw, nh = round(img.width * factor), round(img.height * factor)
    scaled = big.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    out.paste(scaled, ((canvas - nw) // 2, (canvas - nh) // 2), scaled)
    return out


def write_zip(path, name, frames):
    # Launcher contract (verified vs vanilla 2TNK): the TGA is CROPPED to content;
    # meta "size" = the virtual canvas, "crop" = corner bounds where the cropped
    # image sits on that canvas. Shipping full-canvas TGAs makes the launcher
    # squeeze the whole canvas into the crop rect (slivers/sliding anims).
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            b = img.getbbox() or (0, 0, img.width, img.height)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps(
                {"size": [img.width, img.height], "crop": [b[0], b[1], b[2], b[3]]}))
    print(f"wrote {path} ({len(frames)} frames)")


# ---- TSHVR unit ----
CANVAS_U = 192
body8 = Image.open(f"{SCRATCH}/renders_hvr_body/frame-0008.png")
b8 = crop_box(body8)
factor = 140.0 / (b8[2] - b8[0])  # crop_box returns corner bounds, not w/h
frames = []
for i in range(32):
    frames.append(scale_center(Image.open(f"{SCRATCH}/renders_hvr_body/frame-{i:04d}.png"), factor, CANVAS_U))
for i in range(32):
    frames.append(scale_center(Image.open(f"{SCRATCH}/renders_hvr_tur/frame-{i:04d}.png"), factor, CANVAS_U))
write_zip(f"{UNITS_DIR}/TSHVR.ZIP", "tshvr", frames)

# ---- TSPOWR building ----
CANVAS_B = 256
bfactor = 256.0 / 96.0
pframes = [crisp_scale(Image.open(f"{SCRATCH}/shp_gtpowr/frame-{i:04d}.png"), bfactor, CANVAS_B) for i in (0, 2)]
write_zip(f"{STRUCT_DIR}/TSPOWR.ZIP", "tspowr", pframes)

MK_PICK = [0, 2, 3, 5, 6, 8, 10, 11, 13, 14, 16, 18, 19]
mframes = [crisp_scale(Image.open(f"{SCRATCH}/shp_gtpowrmk/frame-{i:04d}.png"), bfactor, CANVAS_B) for i in MK_PICK]
write_zip(f"{STRUCT_DIR}/TSPOWRMAKE.ZIP", "tspowrmake", mframes)

# ---- BuildIcons ----
for src, out in [("shp_hovricon", "BuildIcon_TS_HoverMLRS"), ("shp_powricon", "BuildIcon_TS_PowerPlant")]:
    icon = Image.open(f"{SCRATCH}/{src}/frame-0000.png")
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(f"{ICON_DIR}/{out}.tga")
    print(f"wrote {ICON_DIR}/{out}.tga")

# ---- Tileset XML ----
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

patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSHVR", 64)
patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", "TSPOWR", 2)
patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", "TSPOWRMAKE", 13)

# ---- RABUILDABLES ----
RAB = f"{MOD}/Data/XML/OBJECTS/UNITS/RABUILDABLES.XML"
xml = open(RAB, encoding="utf-8").read()
def buildable(name, text, icon):
    return ('\t<ObjectTypeClass Name="%s" Classification="CNCBuildableObject" CanInstantiate="False">\n'
            "\t\t<CNCEncyclopediaComponent>\n"
            "\t\t\t<ObjectNameTextID>%s</ObjectNameTextID>\n"
            "\t\t\t<ObjectDescriptionTextID>%s_DESC</ObjectDescriptionTextID>\n"
            "\t\t\t<BuildIcon>%s</BuildIcon>\n"
            "\t\t</CNCEncyclopediaComponent>\n"
            "\t</ObjectTypeClass>\n" % (name, text, text, icon))
added = ""
if "RA_TSHVR" not in xml:
    added += buildable("RA_TSHVR", "TEXT_UNIT_TSHVR", "BuildIcon_TS_HoverMLRS")
if "RA_TSPOWR" not in xml:
    added += buildable("RA_TSPOWR", "TEXT_STRUCTURE_TSPOWR", "BuildIcon_TS_PowerPlant")
if added:
    m = re.search(r"</ObjectTypeClass>\s*</AssetDeclaration>", xml)
    idx = xml.rindex("</ObjectTypeClass>") + len("</ObjectTypeClass>")
    xml = xml[:idx] + "\n\n" + added.rstrip("\n") + xml[idx:]
    open(RAB, "w", encoding="utf-8").write(xml)
    print("patched RABUILDABLES.XML")

# ---- ModText.csv (UTF-16) ----
CSV = f"{MOD}/Data/ModText.csv"
raw = open(CSV, "rb").read()
text = raw.decode("utf-16")
eol = "\r\n" if "\r\n" in text else "\n"
sample = next(l for l in text.splitlines() if l.startswith('"TEXT_UNIT_TDA10"'))
tail = sample.split('"A-10 Warthog"', 1)[1]  # the trailing empty-lang commas
rows = [
    ('TEXT_UNIT_TSHVR', 'Hover MLRS'),
    ('TEXT_UNIT_TSHVR_DESC', 'Hover platform firing twin anti-air capable missiles.'),
    ('TEXT_STRUCTURE_TSPOWR', 'Tiberian Power Plant'),
    ('TEXT_STRUCTURE_TSPOWR_DESC', 'Generates power.'),
]
new = ""
for key, val in rows:
    if f'"{key}"' not in text:
        new += f'"{key}",,,"{val}"{tail}{eol}'
if new:
    if not text.endswith(eol):
        text += eol
    text += new
    open(CSV, "wb").write(text.encode("utf-16"))
    print("patched ModText.csv (+%d rows)" % len(new.split(eol)[:-1]))
print("DONE")
