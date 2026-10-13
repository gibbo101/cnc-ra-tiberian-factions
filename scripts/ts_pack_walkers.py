#!/usr/bin/env python3
"""The sidebar side of the TS walkers:
  - TSTITN, TSHMEC  art packed from the HD rebuilds by scripts/ts_pack_hd_buildings.py; their
                 cameos, buildable entries and text are written here.
  - TSBUILDABLES.XML, ModText.csv, BuildIcons (TS cameos via CAMEO.PAL).
Cameos and XML go to the tree asset_packs.py routes each name to.

Inputs (set TS_ART_DIR):
  $TS_ART_DIR/shp_mmchicon2, shp_hmecicon2  decoded TS cameos (CAMEO.PAL!)
"""
import os, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the extracted/rendered TS art directory")
# The mod tree of this script's checkout (ModText.csv, custom cameos); TF_MOD_DIR overrides it.
MOD = os.environ.get("TF_MOD_DIR", asset_packs.MOD)


# TSTITN (Titan, with its muzzle table redalert/tstitn_muzzle.h), TSHMEC (Mammoth Mk. II) and
# TSHVR (Hover MLRS) are packed from their HD art by scripts/ts_pack_hd_buildings.py.

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
