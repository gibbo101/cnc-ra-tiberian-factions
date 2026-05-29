#!/usr/bin/env python3
"""Bundle a TD unit/infantry sprite into the RA mod (units-tileset analogue of
bundle_assets.py, which only handles buildings / RA_STRUCTURES.XML).

For a TD entity NAME (e.g. E1) and our IniName (e.g. TDE1):
  1. Extract <NAME>.ZIP from TEXTURES_TD_SRGB.MEG and repack it with TD-prefixed
     internal frame filenames into Data/.../UNITS/<ININAME>.ZIP (the launcher
     derives the ZIP name from each frame path's first segment, so the repack is
     mandatory — same rule as buildings).
  2. Clone the existing <NAME> tileset block in RA_UNITS.XML into a <ININAME>
     block (verbatim structure, frame paths re-pointed to <ininame>\\...), so the
     format is guaranteed identical. Idempotent.
  3. Wire the sidebar cameo via bundle_assets.patch_rabuildables_xml — the SAME
     path the buildings use. Per docs/adding-td-buildings.md the <BuildIcon> just
     references a vanilla TD BuildIcon name already in the launcher PAK
     (e.g. BuildIcon_TD_Minigunner); nothing is shipped.

Usage:
  scripts/bundle_unit.py E1 TDE1 \\
    --build-icon BuildIcon_TD_Minigunner \\
    --text-name TEXT_UNIT_TITLE_GDI_MINIGUNNER \\
    --text-desc TEXT_UNIT_DESC_GDI_MINIGUNNER
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundle_assets import (  # noqa: E402  reuse the proven, documented helpers
    extract_named_zip,
    repack_zip_with_prefix,
    count_frames,
    source_meg_path,
    patch_rabuildables_xml,
    MOD_ROOT,
)

UNITS_DIR    = MOD_ROOT / "Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
RA_UNITS_XML = MOD_ROOT / "Data/XML/TILESETS/RA_UNITS.XML"


def repack_zip(td_asset, ininame, meg_path):
    dest = UNITS_DIR / f"{ininame}.ZIP"
    tmp = dest.with_suffix(".extracted.zip")
    if not extract_named_zip(meg_path, f"{td_asset}.ZIP", tmp):
        raise RuntimeError(f"{td_asset}.ZIP not found in {meg_path}")
    try:
        repack_zip_with_prefix(tmp, dest, td_asset.lower(), ininame.lower())
    finally:
        if tmp.exists():
            tmp.unlink()
    return dest, count_frames(dest)


def clone_tileset_block(td_asset, ininame):
    """Clone the contiguous <td_asset> Tile run in RA_UNITS.XML into <ininame>."""
    content = RA_UNITS_XML.read_text(encoding="utf-8")

    # Idempotent: strip any prior <ininame> tiles.
    content = re.sub(
        rf"[ \t]*<Tile>\s*<Key>\s*<Name>{ininame}</Name>.*?</Tile>\n",
        "", content, flags=re.DOTALL)

    tiles = re.findall(
        rf"[ \t]*<Tile>\s*<Key>\s*<Name>{td_asset}</Name>.*?</Tile>\n",
        content, flags=re.DOTALL)
    if not tiles:
        raise RuntimeError(f"No <Name>{td_asset}</Name> tiles found in RA_UNITS.XML")

    old_fp = f"{td_asset.lower()}\\{td_asset.lower()}-"
    new_fp = f"{ininame.lower()}\\{ininame.lower()}-"
    block = "".join(
        t.replace(f"<Name>{td_asset}</Name>", f"<Name>{ininame}</Name>")
         .replace(old_fp, new_fp)
        for t in tiles)

    # Insert before the (single) </Tiles> close, preserving its indentation.
    m = re.search(r"\n[ \t]*</Tiles>", content)
    if not m:
        raise RuntimeError("No </Tiles> close tag in RA_UNITS.XML")
    content = content[:m.start()] + "\n" + block.rstrip("\n") + content[m.start():]
    RA_UNITS_XML.write_text(content, encoding="utf-8", newline="\n")
    return len(tiles)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("td_asset", help="TD asset name in the MEG, e.g. E1")
    ap.add_argument("ininame", help="our IniName / tileset key, e.g. TDE1")
    ap.add_argument("--build-icon", required=True, help="vanilla TD BuildIcon_* region")
    ap.add_argument("--text-name", required=True, help="ObjectNameTextID")
    ap.add_argument("--text-desc", required=True, help="ObjectDescriptionTextID")
    args = ap.parse_args()

    meg = source_meg_path()
    zip_dest, frames = repack_zip(args.td_asset, args.ininame, meg)
    tiles = clone_tileset_block(args.td_asset, args.ininame)
    patch_rabuildables_xml(args.ininame, args.text_name, args.text_desc, args.build_icon)

    print(f"  ZIP:          {zip_dest}  ({frames} frames)")
    print(f"  RA_UNITS.XML: {tiles} <{args.ininame}> tiles")
    print(f"  RABUILDABLES: RA_{args.ininame}  (cameo {args.build_icon})")
    if frames != tiles:
        print(f"  WARNING: frame count ({frames}) != tile count ({tiles})")


if __name__ == "__main__":
    main()
