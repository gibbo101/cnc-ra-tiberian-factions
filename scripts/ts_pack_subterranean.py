#!/usr/bin/env python3
"""The sidebar side of the subterranean pair (TSSUBTANK Devil's Tongue / TSSAPC Sub APC): their
cameos, TSBUILDABLES.XML entries and ModText rows. Their art is the HD rebuilds', packed by
scripts/ts_pack_hd_buildings.py, 113 shapes per unit (under the 128 sub-object cap):
  0-31    driving facings
  32-71   dive ladder:   8 facings x 5 steps, pitch -8/-16/-24/-32/-40
          (shape 32 + facing*5 + step; facing = driving frame / 4;
           the 0-pitch step IS the driving frame, not duplicated here)
  72-111  emerge ladder: 8 facings x 5 steps, pitch +40/+32/+24/+16/+8
          (shape 72 + facing*5 + step; ends on the driving frame at 0)
  112     the disturbed-earth marker the owner sees while it tunnels

The DLL snaps facing at dig start, steps the ladder during DIGGING_IN /
EMERGING, and adds the sink offset; frames are origin-centred only.

Inputs (set TS_ART_DIR to the extraction/render dir):
  $TS_ART_DIR/{SUBTICON,SAPCICON}.SHP + CAMEO.PAL

Cameos and TSBUILDABLES.XML entries go to the tree asset_packs.py routes each name to; the
ModText rows to the mod's own ModText.csv.
"""
import os, sys
from PIL import Image

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the extracted/rendered TS art directory")
MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources", "remaster_mods", "Vanilla_RA"))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs
import ts_shp

# ---- BuildIcons (CAMEO.PAL decodes) ----
pal = ts_shp.load_pal(f"{ART}/CAMEO.PAL")
for shp, out in [("SUBTICON", "BuildIcon_TS_DevilsTongue"),
                 ("SAPCICON", "BuildIcon_TS_SubAPC")]:
    # Palette colours as shipped: CAMEO.PAL 16-31 is already the Nod red ramp,
    # and repainting it flat green speckled the icon. hq4x per the house policy.
    import hqx
    size, frs = ts_shp.decode_shp(f"{ART}/{shp}.SHP")
    icon = ts_shp.frame_to_rgba(frs[0], pal, remap=None)
    big = hqx.hq4x(icon.convert("RGB")).convert("RGBA").resize((341, 256), Image.LANCZOS)
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
for ini, icon in [("TSSUBTANK", "BuildIcon_TS_DevilsTongue"),
                  ("TSSAPC", "BuildIcon_TS_SubAPC")]:
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
