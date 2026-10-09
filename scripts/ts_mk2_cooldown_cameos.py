#!/usr/bin/env python3
"""Bake the LOCKED sidebar cameos (dimmed, red X).

The sidebar has no text channel the DLL can write, but CNCSidebarEntryStruct::AssetName is re-read every
sidebar refresh, so the DLL swaps a cameo to <Ini>_LK while it can't be ordered: through the Dropship Bay's
delivery cooldown (every unit it delivers), at the Mk. II field cap, and for the one-per-house Ghost
Stalker, Mobile War Factory and Upgrade Center. A refused click says "Cannot comply".

Reads each unit's pristine BuildIcon from the tree scripts/asset_packs.py routes it to. Emits, in the
mod's own tree, Data/ART/TEXTURES/SRGB/BuildIcon_<Ini>_LK.tga and the RABUILDABLES.XML ObjectTypeClass
entries RA_<Ini>_LK. Idempotent: re-running replaces the generated XML block and overwrites the art.

License: GPL v3.
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

import asset_packs

XML = Path(asset_packs.buildables_xml_of(None))

# Types whose cameo gets a LOCKED variant: IniName -> (its pristine BuildIcon, its text ID prefix). Must
# mirror the _LK swaps in dllinterface.cpp: every unit TF_Is_Dropship_Delivered names (house.cpp), and the
# TF_Mk2_At_Cap / TF_Ghost_At_Cap / TF_Mwar_At_Cap / TF_Plug_At_Cap caps. IniName <= 12 chars (AssetName[16]).
LOCKED = {
    "TSHMEC": ("BuildIcon_TS_MammothMk2", "TEXT_UNIT"),
    "TSMDIV": ("BuildIcon_TS_MechDivision", "TEXT_UNIT"),
    "TSGHOST": ("BuildIcon_TS_Ghost", "TEXT_UNIT"),
    "TSMWAR": ("BuildIcon_TS_MobileWarFactory", "TEXT_UNIT"),
    "TSPLUG": ("BuildIcon_TS_Plug", "TEXT_STRUCTURE"),
}

OUTLINE = (0, 0, 0, 255)
RED = (220, 32, 32, 255)

BEGIN = "\t<!-- BEGIN generated locked cameos (scripts/ts_mk2_cooldown_cameos.py) -->"
END = "\t<!-- END generated locked cameos -->"

TEMPLATE = """\t<ObjectTypeClass Name="RA_{ini}_{tag}" Classification="CNCBuildableObject" CanInstantiate="False">
\t\t<CNCEncyclopediaComponent>
\t\t\t<ObjectNameTextID>{text}_{ini}</ObjectNameTextID>
\t\t\t<ObjectDescriptionTextID>{text}_{ini}_DESC</ObjectDescriptionTextID>
\t\t\t<BuildIcon>BuildIcon_{ini}_{tag}</BuildIcon>
\t\t</CNCEncyclopediaComponent>
\t</ObjectTypeClass>
"""


def bake_locked():
    for ini, (icon, _) in LOCKED.items():
        base = Image.open(asset_packs.cameo_source(icon)).convert("RGBA")
        img = ImageEnhance.Brightness(base).enhance(0.40)
        draw = ImageDraw.Draw(img)
        w, h = img.size
        ix, iy = int(w * 0.18), int(h * 0.18)
        strokes = [((ix, iy), (w - ix, h - iy)), ((w - ix, iy), (ix, h - iy))]
        # Dark casing first, red stroke on top, so the X reads on any cameo.
        for start, end in strokes:
            draw.line([start, end], fill=OUTLINE, width=max(2, int(h * 0.16)))
        for start, end in strokes:
            draw.line([start, end], fill=RED, width=max(1, int(h * 0.09)))
        out = asset_packs.cameo_tga(f"BuildIcon_{ini}_LK")
        img.save(out)
        print(f"baked locked cameo BuildIcon_{ini}_LK into {os.path.dirname(out)}")


def inject_xml():
    entries = "".join(TEMPLATE.format(ini=ini, tag="LK", text=text) for ini, (_, text) in LOCKED.items())
    block = f"{BEGIN}\n{entries}{END}\n"
    text = XML.read_text()
    if BEGIN in text:
        head, rest = text.split(BEGIN, 1)
        _, tail = rest.split(END + "\n", 1)
        text = head + block + tail
    else:
        # Append inside the document, just before the closing root tag.
        idx = text.rindex("</")
        text = text[:idx] + block + text[idx:]
    XML.write_text(text)
    print(f"injected {len(LOCKED)} XML entries into {XML.name}")


if __name__ == "__main__":
    bake_locked()
    inject_xml()
