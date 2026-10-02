#!/usr/bin/env python3
"""Write the sidebar side of the TS units wave: the cameos of TSHARV, TSSMEC, TSSONIC and TSAPC,
their sidebar entries and their text. Their art is the HD rebuilds', packed by
scripts/ts_pack_hd_buildings.py.
  - BuildIcon_TS_{Harvester,Wolverine,Disruptor,AmphAPC}.tga (TS cameos, CAMEO.PAL)
  - TSBUILDABLES.XML entries, ModText.csv rows
Cameos and XML go to the tree asset_packs.py routes each name to.

Inputs (set TS_ART_DIR to the extraction dir):
  $TS_ART_DIR/{HARVICON,SMCHICON,SONIICON,APCICON}.SHP + CAMEO.PAL
"""
import os, sys
from PIL import Image

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the extracted/rendered TS art directory")
# Mod tree relative to this script's repo checkout (worktree-safe; never a
# hardcoded absolute repo path -- the parallel-instance rule).
MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources", "remaster_mods", "Vanilla_RA"))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs
import ts_shp

# ---- BuildIcons (CAMEO.PAL decodes) ----
if os.path.exists(f"{ART}/CAMEO.PAL"):
    pal = ts_shp.load_pal(f"{ART}/CAMEO.PAL")
    for shp, out in [("HARVICON", "BuildIcon_TS_Harvester"),
                     ("SMCHICON", "BuildIcon_TS_Wolverine"),
                     ("SONIICON", "BuildIcon_TS_Disruptor"),
                     ("APCICON", "BuildIcon_TS_AmphAPC")]:
        if not os.path.exists(f"{ART}/{shp}.SHP"):
            print(f"{shp}: SKIP (absent)")
            continue
        size, frs = ts_shp.decode_shp(f"{ART}/{shp}.SHP")
        icon = ts_shp.frame_to_rgba(frs[0], pal, (16, 31), (0, 200, 0))
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
for ini, icon in [("TSHARV", "BuildIcon_TS_Harvester"), ("TSSMEC", "BuildIcon_TS_Wolverine"),
                  ("TSSONIC", "BuildIcon_TS_Disruptor"), ("TSAPC", "BuildIcon_TS_AmphAPC")]:
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
    ('TEXT_UNIT_TSHARV', 'Harvester'),
    ('TEXT_UNIT_TSHARV_DESC', 'Tiberium harvester.'),
    ('TEXT_UNIT_TSSMEC', 'Wolverine'),
    ('TEXT_UNIT_TSSMEC_DESC', 'Light scout mech.'),
    ('TEXT_UNIT_TSSONIC', 'Disruptor'),
    ('TEXT_UNIT_TSSONIC_DESC', 'Sonic beam tank.'),
    ('TEXT_UNIT_TSAPC', 'Amphibious APC'),
    ('TEXT_UNIT_TSAPC_DESC', 'Amphibious armored personnel carrier.'),
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
