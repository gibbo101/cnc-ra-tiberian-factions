#!/usr/bin/env python3
"""The sidebar side of the first TS units (the TS spike): the Hover MLRS and the Power Plant.
  - TSBUILDABLES.XML entries + ModText.csv strings
  - loose BuildIcon_TS_*.tga cameos
Their art (TSHVR, TSPOWR, TSPOWRMAKE) is the HD rebuilds', packed by
scripts/ts_pack_hd_buildings.py. Cameos and XML go to the tree asset_packs.py routes each name to.
"""
import os, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs

SCRATCH = os.environ.get("TS_RENDER_DIR", os.path.dirname(os.path.abspath(__file__)))
MOD = asset_packs.MOD


# ---- BuildIcons ----
for src, out in [("shp_hovricon", "BuildIcon_TS_HoverMLRS"), ("shp_powricon", "BuildIcon_TS_PowerPlant")]:
    icon = Image.open(f"{SCRATCH}/{src}/frame-0000.png")
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(asset_packs.cameo_tga(out))
    print(f"wrote {asset_packs.cameo_tga(out)}")

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
for key, text_id, icon in [("RA_TSHVR", "TEXT_UNIT_TSHVR", "BuildIcon_TS_HoverMLRS"),
                           ("RA_TSPOWR", "TEXT_STRUCTURE_TSPOWR", "BuildIcon_TS_PowerPlant")]:
    rab = asset_packs.buildables_xml(icon)
    if key not in open(rab, encoding="utf-8").read():
        added[rab] = added.get(rab, "") + buildable(key, text_id, icon)
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
tail = sample.split('"A-10 Warthog"', 1)[1]  # the trailing empty-lang commas
rows = [
    ('TEXT_UNIT_TSHVR', 'Hover MLRS'),
    ('TEXT_UNIT_TSHVR_DESC', 'Hover platform firing twin anti-air capable missiles.'),
    ('TEXT_STRUCTURE_TSPOWR', 'GDI Power Plant'),
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
