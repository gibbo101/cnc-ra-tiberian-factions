#!/usr/bin/env python3
"""Builds a data-only Red Alert mod that answers whether the launcher loads a whole terrain tileset into
video memory or only the tiles a map draws (docs/ts-theatres.md): RA's own Temperate tileset plus
dummy tiles no map uses, each a loose DDS frame.

Usage: tileset_vram_probe.py [--tiles N] [--out DIR]

Play one Temperate skirmish map with the mod off, then on, and compare the game's video memory.
Loading only drawn tiles shows no change; loading whole tilesets adds about N x 87 KB.
"""
import argparse
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import meg_extract  # noqa: E402
import steam_library  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# A 256x256 DXT5 terrain frame with mips that the mod already ships and the launcher already draws.
SAMPLE_DDS = os.path.join(REPO, "resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT/TERRAIN/"
                                "TEMPERATE/T17.TEM/T17.TEM-0000.DDS")
TILESET = "DATA\\XML\\TILESETS\\RA_TERRAIN_TEMPERATE.XML"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tiles", type=int, default=4000)
    parser.add_argument("--out", default=os.path.expanduser("~/Desktop/Tiberian Factions/ts-theatres/vram-probe"))
    args = parser.parse_args()
    mod = os.path.join(args.out, "TFTilesetProbe")
    if os.path.isdir(mod):
        sys.exit(f"{mod} exists: remove it first")
    config = str(steam_library.path("common/CnCRemastered/Data/CONFIG.MEG"))
    xml = meg_extract.read_member(config, TILESET).decode("utf-8")

    entries = []
    for i in range(args.tiles):
        entries.append(f"""			<Tile>
				<Key>
					<Name>TFPROBE{i:04d}</Name>
					<Shape>0</Shape>
				</Key>
				<Value>
					<Frames>
						<Frame>tfprobe.tem\\tfprobe.tem-{i:04d}.tga</Frame>
					</Frames>
				</Value>
			</Tile>""")
    closing = list(re.finditer(r"\s*</Tiles>", xml))[-1]
    xml = xml[:closing.start()] + "\n" + "\n".join(entries) + xml[closing.start():]

    xml_dir = os.path.join(mod, "Data", "XML", "TILESETS")
    os.makedirs(xml_dir)
    with open(os.path.join(xml_dir, "RA_TERRAIN_TEMPERATE.XML"), "w", encoding="utf-8") as f:
        f.write(xml)
    frames = os.path.join(mod, "Data", "ART", "TEXTURES", "SRGB", "RED_ALERT", "TERRAIN", "TEMPERATE", "TFPROBE.TEM")
    os.makedirs(frames)
    for i in range(args.tiles):
        shutil.copyfile(SAMPLE_DDS, os.path.join(frames, f"TFPROBE.TEM-{i:04d}.DDS"))
    with open(os.path.join(mod, "ccmod.json"), "w") as f:
        json.dump({"name": "TF tileset VRAM probe", "description": f"RA Temperate plus {args.tiles} unused tiles",
                   "author": "gibbo101", "load_order": 1, "version_high": 0, "version_low": 1,
                   "game_type": "RA"}, f, indent=4)
    size = os.path.getsize(SAMPLE_DDS) * args.tiles
    print(f"wrote {mod}: {args.tiles} unused tiles, {size / 2**20:.0f} MiB of frames")


if __name__ == "__main__":
    main()
