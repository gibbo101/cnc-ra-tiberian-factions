#!/usr/bin/env python3
"""Bake the Mammoth Mk. II delivery-cooldown countdown cameos.

The sidebar has no text channel the DLL can write -- the client renders its own
fixed overlays -- but CNCSidebarEntryStruct::AssetName is re-read every sidebar
refresh (the faction-badge system already relies on this). So the countdown is
ART: one dimmed Mk. II cameo per remaining second, "5:00" down to "0:01",
stamped in gold, and the DLL swaps the asset key once a second while
TFDropBayTimer runs.

Also bakes the field-cap LOCKED cameos (dimmed + red X): while a house fields
its full Mk. II allowance, or its one Ghost Stalker, the DLL swaps the cameo to
<Ini>_LK the same way, and the click is refused with "Cannot comply" instead of
a false "Building" / "Training" ack.

Reads each unit's pristine BuildIcon from the tree scripts/asset_packs.py routes
it to (the TS cameos are in TS-Graphics-Pack). Emits, in the mod's own tree:
  Data/ART/TEXTURES/SRGB/BuildIcon_TSHMEC_CD<sss>.tga   (sss = 001..300)
  Data/ART/TEXTURES/SRGB/BuildIcon_<Ini>_LK.tga         (field-cap locked)
  RABUILDABLES.XML ObjectTypeClass entries RA_TSHMEC_CD<sss> / RA_<Ini>_LK

Idempotent: re-running replaces the generated XML block and overwrites the art.

License: GPL v3.
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

import asset_packs

XML = Path(asset_packs.buildables_xml_of(None))
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Every unit the dropship bay delivers: IniName -> its pristine BuildIcon.
# Must mirror TF_Is_Dropship_Delivered (house.cpp). IniName <= 9 chars, or the
# "<Ini>_CDnnn" key overflows CNCSidebarEntryStruct::AssetName[16].
UNITS = {
    "TSHMEC": "BuildIcon_TS_MammothMk2",
    "TSMDIV": "BuildIcon_TS_MechDivision",
}

# Units whose cameo also gets a field-cap LOCKED variant: IniName -> its
# pristine BuildIcon. Must mirror the TF_Mk2_At_Cap / TF_Ghost_At_Cap / TF_Mwar_At_Cap
# sidebar swaps in dllinterface.cpp (the Mk. II field cap, the one-per-house Ghost
# Stalker and Mobile War Factory), not everything the bay delivers.
LOCKED = {
    "TSHMEC": UNITS["TSHMEC"],
    "TSGHOST": "BuildIcon_TS_Ghost",
    "TSMWAR": "BuildIcon_TS_MobileWarFactory",
}

SECONDS = 300  # 5:00
GOLD = (255, 204, 51, 255)
OUTLINE = (0, 0, 0, 255)
RED = (220, 32, 32, 255)

BEGIN = "\t<!-- BEGIN generated Mk2 cooldown countdown cameos (scripts/ts_mk2_cooldown_cameos.py) -->"
END = "\t<!-- END generated Mk2 cooldown countdown cameos -->"

TEMPLATE = """\t<ObjectTypeClass Name="RA_{ini}_{tag}" Classification="CNCBuildableObject" CanInstantiate="False">
\t\t<CNCEncyclopediaComponent>
\t\t\t<ObjectNameTextID>TEXT_UNIT_{ini}</ObjectNameTextID>
\t\t\t<ObjectDescriptionTextID>TEXT_UNIT_{ini}_DESC</ObjectDescriptionTextID>
\t\t\t<BuildIcon>BuildIcon_{ini}_{tag}</BuildIcon>
\t\t</CNCEncyclopediaComponent>
\t</ObjectTypeClass>
"""


def bake_art():
    for ini, icon in UNITS.items():
        base = Image.open(asset_packs.cameo_tga(icon)).convert("RGBA")
        dimmed = ImageEnhance.Brightness(base).enhance(0.40)
        font = ImageFont.truetype(FONT, int(base.height * 0.42))
        for secs in range(1, SECONDS + 1):
            text = f"{secs // 60}:{secs % 60:02d}"
            img = dimmed.copy()
            draw = ImageDraw.Draw(img)
            bb = draw.textbbox((0, 0), text, font=font, stroke_width=6)
            draw.text(((img.width - (bb[2] - bb[0])) // 2 - bb[0],
                       (img.height - (bb[3] - bb[1])) // 2 - bb[1]),
                      text, font=font, fill=GOLD,
                      stroke_width=6, stroke_fill=OUTLINE)
            out = asset_packs.cameo_tga(f"BuildIcon_{ini}_CD{secs:03d}")
            img.save(out)
        print(f"baked {SECONDS} countdown cameos for {ini} into {os.path.dirname(out)}")


def bake_locked():
    for ini, icon in LOCKED.items():
        base = Image.open(asset_packs.cameo_tga(icon)).convert("RGBA")
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
    entries = "".join(TEMPLATE.format(ini=ini, tag=f"CD{secs:03d}")
                      for ini in UNITS
                      for secs in range(1, SECONDS + 1))
    entries += "".join(TEMPLATE.format(ini=ini, tag="LK") for ini in LOCKED)
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
    print(f"injected {len(UNITS) * SECONDS + len(LOCKED)} XML entries into {XML.name}")


if __name__ == "__main__":
    bake_art()
    bake_locked()
    inject_xml()
