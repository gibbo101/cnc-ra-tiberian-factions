#!/usr/bin/env python3
"""Probe: can Tiberian Factions take one TS unit from a separate data-only pack mod?

install moves the Wolverine (TSSMEC art and tiles, its RA_TSSMEC sidebar entry, both its cameos, the
TSGUN4 report and its two events) out of an installed Vanilla_RA into a pack folder beside it,
loaded through the pack's CCDATA/veterancy_mod.xml file list, as TD-Assets is. Everything it
changes in Vanilla_RA is copied to a backup folder first; restore copies it back and removes the pack.

Usage:  ts_hd_pack_spike.py install <Mods/Red_Alert dir> <backup dir>
        ts_hd_pack_spike.py restore <Mods/Red_Alert dir> <backup dir>
License: GPL v3.
"""
import json
import os
import re
import shutil
import sys

PACK = "TS-HD-Assets-Test"
MOD = "Vanilla_RA"
FILES = (
    "Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS/TSSMEC.ZIP",
    "Data/ART/TEXTURES/SRGB/BuildIcon_TS_Wolverine.tga",
    "Data/ART/TEXTURES/SRGB/BuildIcon_TSSMEC_G.tga",
    "Data/AUDIO/TSGUN4.WAV",
)
TILES = "Data/XML/TILESETS/RA_UNITS.XML"
OBJECTS = "Data/XML/OBJECTS/UNITS/RABUILDABLES.XML"
SFX = "Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML"
CUTS = (
    (TILES, re.compile(r"[ \t]*<Tile>\s*<Key>\s*<Name>TSSMEC</Name>.*?</Tile>[ \t]*\r?\n", re.S),
     "DATA/XML/TILESETS/TSHDTEST_UNITS.XML", "Tiles"),
    (OBJECTS, re.compile(r'[ \t]*<ObjectTypeClass Name="RA_TSSMEC"\s.*?</ObjectTypeClass>[ \t]*\r?\n', re.S),
     "DATA/XML/OBJECTS/UNITS/TSHDTestBuildables.xml", "ObjectTypeList"),
    (SFX, re.compile(r'[ \t]*<SFXEvent Name="RA[CR]_SFX_TSGUN4"\s.*?</SFXEvent>[ \t]*\r?\n', re.S),
     "DATA/XML/AUDIO/SFXEventsTSHDTest.xml", "SFXEvents"),
)
FILE_LIST = """<?xml version="1.0" encoding="utf-8"?>
<Files>
	<SFXEvents>SFXEventsTSHDTest.xml</SFXEvents>
	<LocalizedSFXEvents></LocalizedSFXEvents>
	<GameObjects>TSHDTestBuildables.xml</GameObjects>
	<TileSets>
		<Structures></Structures>
		<Units>TSHDTEST_UNITS.XML</Units>
		<Vfx></Vfx>
	</TileSets>
</Files>
"""


def install(root, backup):
    mod, pack = os.path.join(root, MOD), os.path.join(root, PACK)
    if os.path.exists(pack) or os.path.exists(backup):
        raise SystemExit(f"{pack} or {backup} already exists: restore first")
    for rel in FILES + tuple(c[0] for c in CUTS):
        os.makedirs(os.path.dirname(os.path.join(backup, rel)), exist_ok=True)
        shutil.copy2(os.path.join(mod, rel), os.path.join(backup, rel))
    for rel, entry, out, root_tag in CUTS:
        path = os.path.join(mod, rel)
        text = open(path, encoding="utf-8", newline="").read()
        blocks = entry.findall(text)
        if not blocks:
            raise SystemExit(f"{rel}: no Wolverine entries")
        open(path, "w", encoding="utf-8", newline="").write(entry.sub("", text))
        os.makedirs(os.path.dirname(os.path.join(pack, out)), exist_ok=True)
        body = f'<?xml version="1.0" encoding="utf-8"?>\n<{root_tag}>\n{"".join(blocks)}</{root_tag}>\n'
        open(os.path.join(pack, out), "w", encoding="utf-8", newline="").write(body)
        print(f"{rel}: {len(blocks)} entries moved to {out}")
    for rel in FILES:
        dst = os.path.join(pack, "DATA", rel.split("/", 1)[1])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(os.path.join(mod, rel), dst)
    os.makedirs(os.path.join(pack, "CCDATA"))
    open(os.path.join(pack, "CCDATA", "veterancy_mod.xml"), "w", encoding="utf-8").write(FILE_LIST)
    manifest = {"name": "TS-HD Assets (test)", "description": "Probe: the Wolverine from a separate pack.",
                "author": "gibbo101", "load_order": 2, "version_low": 1, "version_high": 0, "game_type": "RA"}
    json.dump(manifest, open(os.path.join(pack, "ccmod.json"), "w"), indent=4)
    print(f"installed {pack}; backup in {backup}")


def restore(root, backup):
    mod, pack = os.path.join(root, MOD), os.path.join(root, PACK)
    for rel in FILES + tuple(c[0] for c in CUTS):
        shutil.copy2(os.path.join(backup, rel), os.path.join(mod, rel))
    for dirpath, dirnames, filenames in os.walk(pack, topdown=False):
        for f in filenames:
            os.remove(os.path.join(dirpath, f))
        os.rmdir(dirpath)
    print(f"restored {mod}; removed {pack}")


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("install", "restore"):
        raise SystemExit(__doc__)
    (install if sys.argv[1] == "install" else restore)(os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3]))
