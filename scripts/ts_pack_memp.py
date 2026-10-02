#!/usr/bin/env python3
"""The sidebar side of the TS Mobile EM-Pulse (Firestorm [MOBILEMP], TSMEMP):
BuildIcon_TS_MobileEMP.tga, the base RA_TSMEMP sidebar entry (in TSBUILDABLES.XML, next to
RA_TSAPC) and the ModText rows. Its art (TSMEMP, and TSMEMPFX, the pulse blast) is the HD
rebuild's, packed by scripts/ts_pack_hd_buildings.py. The cameo goes to the tree asset_packs.py
routes it to.

Inputs (set TS_ART_DIR): $TS_ART_DIR/.raw/MEMPICON.SHP and CAMEO.PAL. MEMPICON sits in the TS
install's ECACHE01.MIX (tools/ts_extract.py).

License: GPL v3.
"""
import os
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_shp
import asset_packs
from ts_pack_pods import RAW

CSV = f"{asset_packs.MOD}/Data/ModText.csv"
TEXT = (
    ("TEXT_UNIT_TSMEMP", "Mobile EMP"),
    ("TEXT_UNIT_TSMEMP_DESC", "Unarmed support vehicle. Charges up, then deploys to disable nearby "
                              "vehicles and buildings for a few seconds, friend and foe alike."),
)


def cameo():
    pal = ts_shp.load_pal(f"{RAW}/CAMEO.PAL")
    (_, _), raw = ts_shp.decode_shp(f"{RAW}/MEMPICON.SHP")
    icon = ts_shp.frame_to_rgba(raw[0], pal, remap=None)
    flat = Image.new("RGBA", icon.size, (0, 0, 0, 255))
    flat.alpha_composite(icon)
    big = flat.resize((flat.width * 8, flat.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    path = asset_packs.cameo_tga("BuildIcon_TS_MobileEMP")
    big.save(path)
    print(f"wrote {path}")


def sidebar_entry():
    rab = asset_packs.buildables_xml("BuildIcon_TS_MobileEMP")
    xml = open(rab, encoding="utf-8").read()
    if 'Name="RA_TSMEMP"' in xml:
        return
    anchor = '\t<ObjectTypeClass Name="RA_TSAPC" '
    start = xml.index(anchor)
    end = xml.index("</ObjectTypeClass>\n", start) + len("</ObjectTypeClass>\n")
    entry = ('\t<ObjectTypeClass Name="RA_TSMEMP" Classification="CNCBuildableObject" CanInstantiate="False">\n'
             "\t\t<CNCEncyclopediaComponent>\n"
             "\t\t\t<ObjectNameTextID>TEXT_UNIT_TSMEMP</ObjectNameTextID>\n"
             "\t\t\t<ObjectDescriptionTextID>TEXT_UNIT_TSMEMP_DESC</ObjectDescriptionTextID>\n"
             "\t\t\t<BuildIcon>BuildIcon_TS_MobileEMP</BuildIcon>\n"
             "\t\t</CNCEncyclopediaComponent>\n"
             "\t</ObjectTypeClass>\n")
    open(rab, "w", encoding="utf-8").write(xml[:end] + entry + xml[end:])
    print(f"added RA_TSMEMP to {os.path.basename(rab)}")


def text_rows():
    text = open(CSV, "rb").read().decode("utf-16")
    eol = "\r\n" if "\r\n" in text else "\n"
    sample = next(l for l in text.splitlines() if l.startswith('"TEXT_UNIT_TSAPC"'))
    tail = sample.split('"Amphibious APC"', 1)[1]
    new = ""
    for key, val in TEXT:
        if f'"{key}"' not in text:
            new += f'"{key}",,,"{val}"{tail}{eol}'
    if new:
        if not text.endswith(eol):
            text += eol
        open(CSV, "wb").write((text + new).encode("utf-16"))
        print(f"added {len(TEXT)} ModText rows")


def main():
    cameo()
    sidebar_entry()
    text_rows()


if __name__ == "__main__":
    main()
