#!/usr/bin/env python3
"""Runtime-conditional superweapon badges: pristine bases + badged variants.

Re-bakes every BuildIcon_SW_* base as its PRISTINE atlas crop (single-faction
games show clean cameos) and bakes S<hex>_ variant TGAs + RABUILDABLES entries
for the keys TF_Apply_Special_Badge can write in mixed-faction games.
Idempotent: replaces the generated SW-variant XML block on re-run.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path("scripts").resolve()))
import cameo_badge_build as cb
from PIL import Image

region = cb.load_regions()
atlas = Image.open(cb.ATLAS)
XML = Path("resources/remaster_mods/Vanilla_RA/Data/XML/OBJECTS/UNITS/RABUILDABLES.XML")

# rest-of-key -> (pristine region, [badge masks], name text id, desc text id)
SPECIALS = {
    "SonarPulse":   ("BuildIcon_RA_SonarPulse",    [0x1],           "TEXT_UNIT_RA_SONAR",                    "TEXT_UNIT_RA_SONAR_DESC"),
    "Chrono":       ("BuildIcon_RA_ChronoShift",   [0x1],           "TEXT_UNIT_RA_CHRONO",                   "TEXT_UNIT_RA_CHRONO_DESC"),
    "Nuke":         ("BuildIcon_RA_AtomBomb",      [0x1, 0x2, 0x3], "TEXT_UNIT_RA_NUKE",                     "TEXT_UNIT_RA_NUKE_DESC"),
    "ParaBomb":     ("BuildIcon_RA_ParaBombs",     [0x2],           "TEXT_UNIT_RA_PARABOMB",                 "TEXT_UNIT_RA_PARABOMB_DESC"),
    "ParaInfantry": ("BuildIcon_RA_Paratroopers",  [0x2],           "TEXT_UNIT_RA_PARATROOPER",              "TEXT_UNIT_RA_PARATROOPER_DESC"),
    "SpyMission":   ("BuildIcon_RA_SpyPlane",      [0x2],           "TEXT_UNIT_RA_SPYPLANE",                 "TEXT_UNIT_RA_SPYPLANE_DESC"),
    "IronCurtain":  ("BuildIcon_RA_IronCurtain",   [0x2],           "TEXT_UNIT_RA_IRONCURTAIN",              "TEXT_UNIT_RA_IRONCURTAIN_DESC"),
    "GPS":          ("BuildIcon_RA_GPSSatellite",  [0x1, 0x4, 0x5], "TEXT_UNIT_RA_GPS",                      "TEXT_UNIT_RA_GPS_DESC"),
    "IonCannon":    ("BuildIcon_TD_IonCannon",     [0x4],           "TEXT_UNIT_TITLE_GDI_IONCANNON",         "TEXT_UNIT_DESC_GDI_IONCANNON"),
    "TDNuke":       ("BuildIcon_TD_NuclearStrike", [0x8],           "TEXT_UNIT_TITLE_NOD_NUCLEAR_STRIKE",    "TEXT_UNIT_DESC_NOD_NUCLEAR_STRIKE"),
    "TDParaInf":    ("BuildIcon_RA_Paratroopers",  [0x8],           "TEXT_UNIT_TITLE_NOD_PARATROOPERS",      "TEXT_UNIT_DESC_NOD_PARATROOPERS"),
    "TDSpyPlane":   ("BuildIcon_RA_SpyPlane",      [0x8],           "TEXT_UNIT_TITLE_NOD_RECON",             "TEXT_UNIT_DESC_NOD_RECON"),
}


def crop(region_name):
    box = region(region_name)
    if box is None:
        sys.exit(f"ERROR: region {region_name} not in atlas MTD")
    x, y, w, h = box
    return atlas.crop((x, y, x + w, y + h)).convert("RGBA")


def bake(pristine, mask, out_name):
    cameo = pristine.copy()
    if mask:
        count = bin(mask).count("1")
        size, spacing = cb.emblem_layout(count, cameo.width)
        slot = 0
        for bit, _, fn in cb.FACTIONS:
            if mask & bit:
                em = Image.open(cb.EMBLEMS / fn).convert("RGBA").resize((size, size), Image.LANCZOS)
                cameo.alpha_composite(em, (cb.EMBLEM_ORIGIN[0] + slot * spacing, cb.EMBLEM_ORIGIN[1]))
                slot += 1
    cameo.save(cb.OUT / f"{out_name}.tga")


entries = []
for rest, (region_name, masks, name_id, desc_id) in SPECIALS.items():
    pristine = crop(region_name)
    bake(pristine, 0, f"BuildIcon_SW_{rest.upper()}")  # pristine base
    for mask in masks:
        key = f"S{mask:X}_{rest}"
        icon = f"BuildIcon_{key.upper()}"
        bake(pristine, mask, icon)
        entries.append(
            f'\t<ObjectTypeClass Name="RA_{key.upper()}" Classification="CNCBuildableObject" CanInstantiate="False">\n'
            f"\t\t<CNCEncyclopediaComponent>\n"
            f"\t\t\t<ObjectNameTextID>{name_id}</ObjectNameTextID>\n"
            f"\t\t\t<ObjectDescriptionTextID>{desc_id}</ObjectDescriptionTextID>\n"
            f"\t\t\t<BuildIcon>{icon}</BuildIcon>\n"
            f"\t\t</CNCEncyclopediaComponent>\n"
            f"\t</ObjectTypeClass>\n"
        )

BEGIN = "\t<!-- BEGIN generated superweapon badge variants (scripts/sw_badge_variants.py) -->\n"
END = "\t<!-- END generated superweapon badge variants -->\n"
block = BEGIN + "".join(entries) + END

xml = XML.read_text(encoding="utf-8")
xml = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), "", xml, flags=re.S)
anchor = "\t<!-- BEGIN generated cameo mask variants"
if anchor not in xml:
    sys.exit("ERROR: buildables variant block anchor not found")
xml = xml.replace(anchor, block + "\n" + anchor, 1)
XML.write_text(xml, encoding="utf-8")
print(f"OK: {len(entries)} variant entries, {len(SPECIALS)} pristine bases re-baked")
