#!/usr/bin/env python3
"""The sidebar side of the TS walkers, and the rail spark tileset:
  - TSTITN, TSHMEC  art packed from the HD rebuilds by scripts/ts_pack_hd_buildings.py; their
                 cameos, buildable entries and text are written here.
  - RAILFX pad   the spark tileset padded to 12 shapes (6 real + 6 blank):
                 WINDOW_VIRTUAL anim draws ignore the stage cap (anim.cpp:328),
                 so dying sparks request shapes >= Stages — blanks absorb them
                 instead of the launcher's white placeholder box.
  - TS_VFX.XML tile run (REPLACING any existing entries), TSBUILDABLES.XML, ModText.csv,
    BuildIcons (TS cameos via CAMEO.PAL).
Cameos and XML go to the tree asset_packs.py routes each name to.

Inputs (set TS_ART_DIR):
  $TS_ART_DIR/shp_mmchicon2, shp_hmecicon2  decoded TS cameos (CAMEO.PAL!)
"""
import io, json, os, re, sys, zipfile
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the extracted/rendered TS art directory")
# The mod tree of this script's checkout (ModText.csv, custom cameos); TF_MOD_DIR overrides it.
MOD = os.environ.get("TF_MOD_DIR", asset_packs.MOD)


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


# TSTITN (Titan, with its muzzle table redalert/tstitn_muzzle.h), TSHMEC (Mammoth Mk. II) and
# TSHVR (Hover MLRS) are packed from their HD art by scripts/ts_pack_hd_buildings.py.

# ---- RAILFX: repack existing 6 real frames + 6 blank pad shapes ----
RAILFX_ZIP = asset_packs.art_zip("RAILFX", "VFX")
src = zipfile.ZipFile(RAILFX_ZIP)
real = []
for i in range(6):
    meta = json.loads(src.read(f"railfx-{i:04d}.meta"))
    tga = src.read(f"railfx-{i:04d}.tga")
    real.append((tga, meta))
blank = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
blank_tga = tga_bytes(blank.crop((0, 0, 2, 2)))
with zipfile.ZipFile(RAILFX_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for i, (tga, meta) in enumerate(real):
        z.writestr(f"railfx-{i:04d}.tga", tga)
        z.writestr(f"railfx-{i:04d}.meta", json.dumps(meta))
    for i in range(6, 12):
        z.writestr(f"railfx-{i:04d}.tga", blank_tga)
        z.writestr(f"railfx-{i:04d}.meta", json.dumps({"size": [128, 128], "crop": [0, 0, 2, 2]}))
print("repacked RAILFX.ZIP (6 real + 6 blank shapes)")

# ---- BuildIcons (CAMEO.PAL decodes) ----
for src_d, out in [("shp_mmchicon2", "BuildIcon_TS_Titan"),
                   ("shp_hmecicon2", "BuildIcon_TS_MammothMk2")]:
    # Hand-made art in resources/custom-cameos is canonical for its icon name.
    custom = os.path.abspath(f"{MOD}/../../custom-cameos/{out}.png")
    if os.path.exists(custom):
        Image.open(custom).convert("RGBA").resize((341, 256), Image.LANCZOS).save(
            asset_packs.cameo_tga(out))
        print(f"custom {asset_packs.cameo_tga(out)}")
        continue
    icon = Image.open(f"{ART}/{src_d}/frame-0000.png")
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(asset_packs.cameo_tga(out))
    print(f"wrote {asset_packs.cameo_tga(out)}")

# ---- Tileset XML (replace-capable) ----
def tile_block(name, shape, frame_path):
    return ("\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n"
            "\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n"
            % (name, shape, frame_path))

def patch_tileset(xml_path, name, count, subdir=None):
    sub = subdir or name.lower()
    xml = open(xml_path, encoding="utf-8").read()
    # drop any existing Tile blocks for this name (any indentation)
    xml = re.sub(
        r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?",
        "", xml, flags=re.S)
    blocks = "".join(tile_block(name, s, f"{sub}\\{sub}-{s:04d}.tga") for s in range(count))
    idx = xml.rindex("</Tiles>")
    xml = xml[:idx] + blocks + xml[idx:]
    open(xml_path, "w", encoding="utf-8").write(xml)
    print(f"patched {os.path.basename(xml_path)}: {name} -> {count} tiles")

patch_tileset(asset_packs.tileset_xml("RAILFX", "VFX"), "RAILFX", 12)

# ---- Sidebar entries, in the buildables XML of each cameo's tree ----
def buildable(name, text, icon):
    return ('\t<ObjectTypeClass Name="%s" Classification="CNCBuildableObject" CanInstantiate="False">\n'
            "\t\t<CNCEncyclopediaComponent>\n"
            "\t\t\t<ObjectNameTextID>%s</ObjectNameTextID>\n"
            "\t\t\t<ObjectDescriptionTextID>%s_DESC</ObjectDescriptionTextID>\n"
            "\t\t\t<BuildIcon>%s</BuildIcon>\n"
            "\t\t</CNCEncyclopediaComponent>\n"
            "\t</ObjectTypeClass>\n" % (name, text, text, icon))
added = {}
for ini, icon in [("TSTITN", "BuildIcon_TS_Titan"), ("TSHMEC", "BuildIcon_TS_MammothMk2")]:
    rab = asset_packs.buildables_xml(icon)
    if f"RA_{ini}" not in open(rab, encoding="utf-8").read():
        added[rab] = added.get(rab, "") + buildable(f"RA_{ini}", f"TEXT_UNIT_{ini}", icon)
for rab, entries in added.items():
    xml = open(rab, encoding="utf-8").read()
    idx = xml.rindex("</ObjectTypeClass>") + len("</ObjectTypeClass>")
    xml = xml[:idx] + "\n\n" + entries.rstrip("\n") + xml[idx:]
    open(rab, "w", encoding="utf-8").write(xml)
    print(f"patched {os.path.basename(rab)}")

# ---- ModText.csv (UTF-16) ----
CSV = f"{MOD}/Data/ModText.csv"
raw = open(CSV, "rb").read()
text = raw.decode("utf-16")
eol = "\r\n" if "\r\n" in text else "\n"
sample = next(l for l in text.splitlines() if l.startswith('"TEXT_UNIT_TDA10"'))
tail = sample.split('"A-10 Warthog"', 1)[1]
rows = [
    ('TEXT_UNIT_TSTITN', 'Titan'),
    ('TEXT_UNIT_TSTITN_DESC', 'GDI walking assault mech.'),
    ('TEXT_UNIT_TSHMEC', 'Mammoth Mk. II'),
    ('TEXT_UNIT_TSHMEC_DESC', 'Heavy assault walker with twin railguns.'),
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
