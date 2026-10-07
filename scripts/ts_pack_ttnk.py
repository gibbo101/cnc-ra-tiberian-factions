#!/usr/bin/env python3
"""The sidebar side of the TS Tick Tank (TSTTNK) and its dug-in form (TSTICK): TS's cameo, their buildables XML
entries and ModText rows. Their art is the HD rebuilds', packed by scripts/ts_pack_hd_buildings.py.

Inputs (set TS_ART_DIR to a folder holding them, from TIBSUN.MIX: CONQUER.MIX and CACHE.MIX):
  $TS_ART_DIR/TICKICON.SHP + CAMEO.PAL

Usage: TS_ART_DIR=... ts_pack_ttnk.py
License: GPL v3.
"""
import os
import sys

import hqx
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs
import ts_shp

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the folder holding TICKICON.SHP and CAMEO.PAL")
MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources", "remaster_mods", "Vanilla_RA"))
ICON = "BuildIcon_TS_TickTank"
ENTRIES = (("RA_TSTTNK", "TEXT_UNIT_TSTTNK"), ("RA_TSTICK", "TEXT_STRUCTURE_TSTICK"))
TEXT = (("TEXT_UNIT_TSTTNK", "Tick Tank"),
        ("TEXT_UNIT_TSTTNK_DESC", "Nod tank that digs in for heavy armour. Deploy to dig in."),
        ("TEXT_STRUCTURE_TSTICK", "Deployed Tick Tank"),
        ("TEXT_STRUCTURE_TSTICK_DESC", "A Tick Tank dug in. Deploy again to dig it out."))


def cameo():
    """TS's cameo through CAMEO.PAL as shipped (its 16-31 is Nod's red ramp), hq4x as the house policy."""
    pal = ts_shp.load_pal(f"{ART}/CAMEO.PAL")
    _, frames = ts_shp.decode_shp(f"{ART}/TICKICON.SHP")
    icon = ts_shp.frame_to_rgba(frames[0], pal, remap=None)
    big = hqx.hq4x(icon.convert("RGB")).convert("RGBA").resize((341, 256), Image.LANCZOS)
    big.save(asset_packs.cameo_tga(ICON))
    print(f"wrote {asset_packs.cameo_tga(ICON)}")


def buildables():
    rab = asset_packs.buildables_xml(ICON)
    xml = open(rab, encoding="utf-8").read()
    add = ""
    for name, text in ENTRIES:
        if f'Name="{name}"' in xml:
            continue
        add += ('\t<ObjectTypeClass Name="%s" Classification="CNCBuildableObject" CanInstantiate="False">\n'
                "\t\t<CNCEncyclopediaComponent>\n"
                "\t\t\t<ObjectNameTextID>%s</ObjectNameTextID>\n"
                "\t\t\t<ObjectDescriptionTextID>%s_DESC</ObjectDescriptionTextID>\n"
                "\t\t\t<BuildIcon>%s</BuildIcon>\n"
                "\t\t</CNCEncyclopediaComponent>\n"
                "\t</ObjectTypeClass>\n" % (name, text, text, ICON))
    if add:
        idx = xml.rindex("</ObjectTypeClass>") + len("</ObjectTypeClass>")
        xml = xml[:idx] + "\n\n" + add.rstrip("\n") + xml[idx:]
        open(rab, "w", encoding="utf-8").write(xml)
        print(f"patched {os.path.basename(rab)}")


def modtext():
    path = f"{MOD}/Data/ModText.csv"
    text = open(path, "rb").read().decode("utf-16")
    eol = "\r\n" if "\r\n" in text else "\n"
    sample = next(l for l in text.splitlines() if l.startswith('"TEXT_UNIT_TDA10"'))
    tail = sample.split('"A-10 Warthog"', 1)[1]
    new = "".join(f'"{key}",,,"{val}"{tail}{eol}' for key, val in TEXT if f'"{key}"' not in text)
    if new:
        if not text.endswith(eol):
            text += eol
        open(path, "wb").write((text + new).encode("utf-16"))
        print(f"patched ModText.csv (+{new.count(eol)} rows)")


if __name__ == "__main__":
    cameo()
    buildables()
    modtext()
