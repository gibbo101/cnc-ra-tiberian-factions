#!/usr/bin/env python3
'''
build_blossom_building.py -- HD art for the TD blossom tree rendered as a BUILDING
(STRUCT_TDBLOSSOM, IniName TDBLOSSOM). Terrain objects can't take custom HD art on
our stack, but buildings render via the loose RA_STRUCTURES ZIP pipeline (same as
every TD building). So we package the TD SPLIT2 blossom frames as a structure asset:

  1. Extract SPLIT2's 55 HD frames from TEXTURES_TD_SRGB.MEG (loose DDS, terrain dir).
  2. DDS -> cropped TGA + per-frame .meta (the launcher's structure-ZIP convention).
  3. Pack as TDBLOSSOM.ZIP under .../STRUCTURES/ (frame ref tdblossom\tdblossom-NNNN.tga).
  4. Patch RA_STRUCTURES.XML with a TDBLOSSOM tileset block (55 shapes).

Reuses extract_from_meg / crop_to_opaque from build_tiberium_hd.py.
License: GPL v3.
'''
import io
import json
import sys
import zipfile
from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import build_tiberium_hd as hd  # noqa: E402  -- reuse extract_from_meg / crop_to_opaque

MOD_ROOT = hd.MOD_ROOT
TD_TEX_MEG = hd.TD_TEX_MEG
SRC_DIR = r"DATA\ART\TEXTURES\SRGB\TIBERIAN_DAWN\TERRAIN\TEMPERATE\SPLIT2"
SRC_FRAME = "SPLIT2.TEM-{:04d}.DDS"
N_FRAMES = 55
ASSET = "tdblossom"
ZIP_NAME = "TDBLOSSOM.ZIP"
STRUCT_TEX_DIR = MOD_ROOT / "Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES"
RA_STRUCTURES_XML = MOD_ROOT / "Data/XML/TILESETS/RA_STRUCTURES.XML"


def build_zip(work_dir):
    STRUCT_TEX_DIR.mkdir(parents=True, exist_ok=True)
    out_zip = STRUCT_TEX_DIR / ZIP_NAME
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in range(N_FRAMES):
            dds = hd.extract_from_meg(TD_TEX_MEG, f"{SRC_DIR}\\{SRC_FRAME.format(i)}", work_dir)
            im = Image.open(dds).convert("RGBA")
            cropped, meta = hd.crop_to_opaque(im)
            buf = io.BytesIO()
            cropped.save(buf, "TGA")
            stem = f"{ASSET}-{i:04d}"
            zf.writestr(stem + ".tga", buf.getvalue())
            zf.writestr(stem + ".meta", json.dumps(meta))
    print(f"  wrote {out_zip} ({N_FRAMES} frames)")


def tile_block(shape):
    frame = f"{ASSET}\\{ASSET}-{shape:04d}.tga"
    return (
        "\t\t\t<Tile>\n"
        "\t\t\t\t<Key>\n"
        "\t\t\t\t\t<Name>TDBLOSSOM</Name>\n"
        f"\t\t\t\t\t<Shape>{shape}</Shape>\n"
        "\t\t\t\t</Key>\n"
        "\t\t\t\t<Value>\n"
        "\t\t\t\t\t<Frames>\n"
        f"\t\t\t\t\t\t<Frame>{frame}</Frame>\n"
        "\t\t\t\t\t</Frames>\n"
        "\t\t\t\t</Value>\n"
        "\t\t\t</Tile>\n"
    )


def patch_tileset():
    # RA_STRUCTURES.XML is loose (not CONFIG.MEG) and LF -- buildings tolerate LF.
    text = RA_STRUCTURES_XML.read_text(encoding="utf-8")
    if "<Name>TDBLOSSOM</Name>" in text:
        import re
        text = re.sub(r"\t\t\t<Tile>\n(?:(?!</Tile>).)*?<Name>TDBLOSSOM</Name>.*?</Tile>\n",
                      "", text, flags=re.S)
    blocks = "".join(tile_block(s) for s in range(N_FRAMES))
    marker = "\t\t</Tiles>"
    if marker not in text:
        marker = "</Tiles>"
    text = text.replace(marker, blocks + marker, 1)
    RA_STRUCTURES_XML.write_text(text, encoding="utf-8")
    print(f"  wrote {RA_STRUCTURES_XML} (+{N_FRAMES} TDBLOSSOM tiles)")


def main():
    if not TD_TEX_MEG.exists():
        sys.exit(f"Source MEG not found: {TD_TEX_MEG}")
    work = Path("/tmp/tdblossom_build")
    work.mkdir(parents=True, exist_ok=True)
    print("Building TDBLOSSOM (blossom-tree-as-building) HD art...")
    build_zip(work)
    patch_tileset()
    print("Done.")


if __name__ == "__main__":
    main()
