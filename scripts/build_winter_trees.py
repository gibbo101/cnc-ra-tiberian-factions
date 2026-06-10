#!/usr/bin/env python3
r"""Snowy trees for converted TD WINTER maps (HD side).

TD winter maps live in RA's TEMPERATE theatre (the TDW* template family), so
their terrain-object trees render with green temperate art. The tileset's
RootTexturePath pins every <Frame> to Red_Alert\Terrain\Temperate, so entries
can't reach the base snow textures by path (tried: Petroglyph placeholder).
What DOES work is the same loose-ZIP delivery the TDW* templates use: a
dot-free <NAME>.ZIP of cropped TGAs + meta in the mod's TEMPERATE texture dir.

This script extracts TD's own remastered winter tree art (10 frames per tree)
from TEXTURES_TD_SRGB.MEG (TERRAIN\WINTER\<NAME>.WIN\), bundles each tree as
TDW<NAME>.ZIP, and splices matching <Tile> entries into the mod's loose
RA_TERRAIN_TEMPERATE.XML between TF_WINTER_TREES markers (idempotent, CRLF
preserved). The engine swaps tree AssetNames T01 -> TDWT01 on winter maps
(dllinterface.cpp; TF_TDWinterMap), and classic mode gets the matching
WINTER.MIX art via TerrainClass::Get_Image_Data + build_tfassets.sh.

Usage: scripts/build_winter_trees.py
Then:  rebuild (packaging copies Data/ via POST_BUILD).

License: GPL v3 (inherited from Vanilla Conquer base).
"""
import io
import json
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_tiberium_hd import extract_from_meg, crop_to_opaque, TD_TEX_MEG  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
TEX_DIR = REPO / "resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT/TERRAIN/TEMPERATE"
TEMPERATE_XML = REPO / "resources/remaster_mods/Vanilla_RA/Data/XML/TILESETS/RA_TERRAIN_TEMPERATE.XML"

BEGIN = "<!-- TF_WINTER_TREES xml BEGIN -->"
END = "<!-- TF_WINTER_TREES xml END -->"

# RA tree/clump terrain objects used by the converted TD winter maps. All 20
# have 10-frame TD winter HD art in the TD MEG. Keep in sync with the
# AssetName swap in dllinterface.cpp and the classic list in build_tfassets.sh.
TREE_NAMES = (
    ["T%02d" % i for i in (1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17)]
    + ["TC%02d" % i for i in range(1, 6)]
)
FRAMES_PER_TREE = 10


def meg_tree_frames():
    """Map tree name -> sorted list of its DDS entry paths in the TD MEG.
    Discovered rather than assumed: frame numbering isn't always contiguous
    (T15 ships 0-8 then 10, no 9); shape index = position in the sorted list."""
    import subprocess
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts/meg_extract.py"), "list",
         str(TD_TEX_MEG), "WINTER\\T"],
        capture_output=True, text=True, check=True).stdout
    frames = {}
    for line in out.splitlines():
        m = re.search(r"(DATA\\ART\\TEXTURES\\SRGB\\TIBERIAN_DAWN\\TERRAIN"
                      r"\\WINTER\\(TC?\d+)\.WIN\\TC?\d+\.WIN-\d{4}\.DDS)",
                      line.upper())
        if m:
            frames.setdefault(m.group(2), []).append(m.group(1))
    return {k: sorted(v) for k, v in frames.items()}


def main():
    TEX_DIR.mkdir(parents=True, exist_ok=True)
    tree_frames = meg_tree_frames()
    xml_tiles = []
    with tempfile.TemporaryDirectory(prefix="tdwtrees-") as workdir:
        work = Path(workdir)
        for name in TREE_NAMES:
            ra = "TDW" + name           # engine/tileset name, e.g. TDWT01
            stem = ra.lower()           # zip + frame file stem, e.g. tdwt01
            zip_path = TEX_DIR / f"{ra}.ZIP"
            entries = tree_frames.get(name, [])
            if len(entries) != FRAMES_PER_TREE:
                sys.exit(f"{name}: expected {FRAMES_PER_TREE} winter frames "
                         f"in the TD MEG, found {len(entries)}")
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for n, entry in enumerate(entries):
                    dds = extract_from_meg(TD_TEX_MEG, entry, work)
                    im = Image.open(dds).convert("RGBA")
                    cropped, meta = crop_to_opaque(im)
                    fn = f"{stem}-{n:04d}"
                    buf = io.BytesIO()
                    cropped.save(buf, "TGA")
                    zf.writestr(fn + ".tga", buf.getvalue())
                    zf.writestr(fn + ".meta", json.dumps(meta))
                    xml_tiles.append(
                        "\t\t\t<Tile>\r\n\t\t\t\t<Key>\r\n"
                        f"\t\t\t\t\t<Name>{ra}</Name>\r\n"
                        f"\t\t\t\t\t<Shape>{n}</Shape>\r\n"
                        "\t\t\t\t</Key>\r\n\t\t\t\t<Value>\r\n\t\t\t\t\t<Frames>\r\n"
                        f"\t\t\t\t\t\t<Frame>{stem}\\{fn}.tga</Frame>\r\n"
                        "\t\t\t\t\t</Frames>\r\n\t\t\t\t</Value>\r\n\t\t\t</Tile>")
            print(f"  {ra}.ZIP ({FRAMES_PER_TREE} frames)")

    injected = BEGIN + "\r\n" + "\r\n".join(xml_tiles) + "\r\n" + END

    # newline='' preserves the file's CRLF endings (the base-game convention);
    # plain text mode silently rewrote the whole 70k-line file to LF.
    with open(TEMPERATE_XML, encoding="utf-8", newline="") as f:
        temperate = f.read()

    if BEGIN in temperate:
        # lambda replacement: frame paths contain backslashes that re.sub
        # would otherwise treat as escape sequences.
        temperate = re.sub(
            re.escape(BEGIN) + ".*?" + re.escape(END), lambda m: injected,
            temperate, flags=re.S)
    else:
        anchor = "<!-- TF_TD_TILES xml END -->"
        if anchor not in temperate:
            sys.exit("TF_TD_TILES end marker not found in temperate XML")
        temperate = temperate.replace(anchor, anchor + "\r\n" + injected)

    with open(TEMPERATE_XML, "w", encoding="utf-8", newline="") as f:
        f.write(temperate)

    print(f"injected {len(xml_tiles)} TDW tree tile entries "
          f"({len(TREE_NAMES)} trees x {FRAMES_PER_TREE} frames)")


if __name__ == "__main__":
    main()
