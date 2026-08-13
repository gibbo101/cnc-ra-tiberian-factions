#!/usr/bin/env python3
"""Package the subterranean pair (TSSUBTANK Devil's Tongue / TSSAPC Sub APC).

Frame layout per unit (112 shapes, under the 128 sub-object cap):
  0-31    driving facings (voxel renders, +8 rotation fix)
  32-71   dive ladder:   8 facings x 5 steps, pitch -8/-16/-24/-32/-40
          (shape 32 + facing*5 + step; facing = driving frame / 4;
           the 0-pitch step IS the driving frame, not duplicated here)
  72-111  emerge ladder: 8 facings x 5 steps, pitch +40/+32/+24/+16/+8
          (shape 72 + facing*5 + step; ends on the driving frame at 0)

The DLL snaps facing at dig start, steps the ladder during DIGGING_IN /
EMERGING, and adds the sink offset; frames here are origin-centred only.

Inputs (set TS_ART_DIR to the extraction/render dir):
  $TS_ART_DIR/renders_subtank|renders_sapc/frame-NNNN.png          (32, fleet cam)
  $TS_ART_DIR/renders_{unit}_{dive|emerge}_{8,16,24,32,40}/frame-NNNN.png (8 each)
  $TS_ART_DIR/{SUBTICON,SAPCICON}.SHP + CAMEO.PAL
"""
import io, json, os, re, sys, zipfile
from PIL import Image

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the extracted/rendered TS art directory")
MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources", "remaster_mods", "Vanilla_RA"))
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
ICON_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ts_shp

F_VOX = 6.4 / 12.0   # 12 px/voxel renders -> canvas px (1 voxel ~= 1 TS SHP px)
CANVAS = 384          # 48x48 classic stub x 8


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def write_zip(path, name, frames):
    # Launcher contract: virtual-canvas-CENTER anchoring; center-symmetric
    # crops keep both anchoring interpretations coincident.
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            W, H = img.width, img.height
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0 = min(bb[0], W - bb[2])
            y0 = min(bb[1], H - bb[3])
            b = (x0, y0, W - x0, H - y0)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps(
                {"size": [W, H], "crop": [b[0], b[1], b[2], b[3]]}))
    print(f"wrote {path} ({len(frames)} frames)")


def safe_paste(dst, src, x, y):
    """Pillow negative-offset RGBA-mask paste corrupts output -- pre-crop."""
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy:
        src = src.crop((sx, sy, src.width, src.height))
        x, y = max(0, x), max(0, y)
    dst.paste(src, (x, y), src)


def drop_shadow(frame, dx, dy, alpha=130):
    sil = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    mask = frame.split()[3].point(lambda a: alpha if a > 0 else 0)
    black = Image.new("RGBA", frame.size, (0, 0, 0, 255))
    sil.paste(black, (dx, dy), mask)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.alpha_composite(sil)
    out.alpha_composite(frame)
    return out


def place(im, shadow=None):
    """Model-space placement: render canvas centre (= voxel origin) lands on
    the pack canvas centre, so all pitches/facings stay rigidly registered."""
    scaled = im.resize((round(im.width * F_VOX), round(im.height * F_VOX)),
                       Image.LANCZOS)
    fr = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ox = round(CANVAS / 2 - scaled.width / 2)
    oy = round(CANVAS / 2 - scaled.height / 2)
    b = scaled.getbbox()
    if b and (ox + b[0] < 0 or oy + b[1] < 0 or ox + b[2] > CANVAS or oy + b[3] > CANVAS):
        print("  WARNING: content clipped -- grow the canvas")
    safe_paste(fr, scaled, ox, oy)
    if shadow:
        fr = drop_shadow(fr, *shadow)
    return fr


def load(dirname, i):
    return Image.open(f"{ART}/{dirname}/frame-{i:04d}.png").convert("RGBA")


def unit_frames(render_base, rot32, rot8):
    """rot32/rot8: per-model rotation fix. The verified TS-voxel convention
    (APC/HARV chain) is nose on -X: those models take +8 (of 32) / +2 (of 8).
    SAPC is authored nose-on-+X -- 180 degrees opposite -- so it takes +24/+6
    (Deck-verified 2026-08-13: with +8 it drove drill-backwards). The pitch
    ladders are rendered nose-axis-aware (dive dirs always hold nose-DOWN art:
    positive pitch for -X-nose models, negative for +X-nose)."""
    frames = []
    # Driving frames carry the ground drop shadow; ladder frames don't (the
    # hull is part-buried and the DIG mound anim plays over the top).
    for i in range(32):
        frames.append(place(load(f"renders_{render_base}", (i + rot32) % 32),
                            shadow=(10, 13)))
    # 32-71 dive: facing f = driving frame f*4.
    for f in range(8):
        for pitch in (8, 16, 24, 32, 40):
            frames.append(place(load(f"renders_{render_base}_dive_{pitch}", (f + rot8) % 8)))
    # 72-111 emerge: steepest first, easing to the surface.
    for f in range(8):
        for pitch in (40, 32, 24, 16, 8):
            frames.append(place(load(f"renders_{render_base}_emerge_{pitch}", (f + rot8) % 8)))
    return frames


write_zip(f"{UNITS_DIR}/TSSUBTANK.ZIP", "tssubtank", unit_frames("subtank", 8, 2))
write_zip(f"{UNITS_DIR}/TSSAPC.ZIP", "tssapc", unit_frames("sapc", 24, 6))

# ---- BuildIcons (CAMEO.PAL decodes) ----
pal = ts_shp.load_pal(f"{ART}/CAMEO.PAL")
for shp, out in [("SUBTICON", "BuildIcon_TS_DevilsTongue"),
                 ("SAPCICON", "BuildIcon_TS_SubAPC")]:
    size, frs = ts_shp.decode_shp(f"{ART}/{shp}.SHP")
    icon = ts_shp.frame_to_rgba(frs[0], pal, (16, 31), (0, 200, 0))
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(f"{ICON_DIR}/{out}.tga")
    print(f"wrote {ICON_DIR}/{out}.tga")

# ---- Tileset XML (replace-capable) ----
def tile_block(name, shape, frame_path):
    return ("\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n"
            "\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n"
            % (name, shape, frame_path))

def patch_tileset(xml_path, name, count):
    sub = name.lower()
    xml = open(xml_path, encoding="utf-8").read()
    xml = re.sub(
        r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?",
        "", xml, flags=re.S)
    blocks = "".join(tile_block(name, s, f"{sub}\\{sub}-{s:04d}.tga") for s in range(count))
    idx = xml.rindex("</Tiles>")
    xml = xml[:idx] + blocks + xml[idx:]
    open(xml_path, "w", encoding="utf-8").write(xml)
    print(f"patched {os.path.basename(xml_path)}: {name} -> {count} tiles")

patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSSUBTANK", 112)
patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSSAPC", 112)

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
for ini, icon in [("TSSUBTANK", "BuildIcon_TS_DevilsTongue"),
                  ("TSSAPC", "BuildIcon_TS_SubAPC")]:
    if f"RA_{ini}" not in xml:
        added += buildable(f"RA_{ini}", f"TEXT_UNIT_{ini}", icon)
if added:
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
tail = sample.split('"A-10 Warthog"', 1)[1]
rows = [
    ('TEXT_UNIT_TSSUBTANK', "Devil's Tongue"),
    ('TEXT_UNIT_TSSUBTANK_DESC', 'Subterranean flame tank.'),
    ('TEXT_UNIT_TSSAPC', 'Subterranean APC'),
    ('TEXT_UNIT_TSSAPC_DESC', 'Underground armored personnel carrier.'),
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
