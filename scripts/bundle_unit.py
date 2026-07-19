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


def clone_tileset_block(td_asset, ininame, donor=None, frame_count=None):
    """Clone the contiguous <donor> Tile run in RA_UNITS.XML into <ininame>.

    `donor` defaults to `td_asset` (the usual case: RA already ships a tileset
    block under the TD asset's name, e.g. E1/E4). When the TD unit has NO RA
    equivalent to clone (e.g. E5 chem warrior — RA never had one), pass a
    structurally-identical RA unit as `donor` (E4 flamethrower: TD's chem and
    flame share a byte-identical DO table + 660-frame layout). The cloned
    block is renamed to `ininame` and its frame paths re-pointed to
    `<ininame>\\...`, so the sprite still loads from our TD-prefixed ZIP.

    `frame_count` (when given) forces the emitted block to exactly that many
    Shape-ordered tiles — slicing a larger donor down. Use it when no RA unit
    has a tile run matching the TD asset's frame count (e.g. the Commando =
    468 frames; the closest donors are larger). The tiles are Shape-ordered
    0..N-1 and each re-points to <ininame>-NNNN, so frames==tiles always.
    """
    donor = donor or td_asset
    content = RA_UNITS_XML.read_text(encoding="utf-8")

    # Idempotent: strip any prior <ininame> tiles.
    content = re.sub(
        rf"[ \t]*<Tile>\s*<Key>\s*<Name>{ininame}</Name>.*?</Tile>\n",
        "", content, flags=re.DOTALL)

    tiles = re.findall(
        rf"[ \t]*<Tile>\s*<Key>\s*<Name>{donor}</Name>.*?</Tile>\n",
        content, flags=re.DOTALL)
    if not tiles:
        raise RuntimeError(f"No <Name>{donor}</Name> tiles found in RA_UNITS.XML")

    # When the donor's frame count doesn't match the TD asset, slice the
    # Shape-ordered run to the exact ZIP frame count (donor must have enough).
    if frame_count is not None:
        if len(tiles) < frame_count:
            raise RuntimeError(
                f"donor {donor} has {len(tiles)} tiles < {frame_count} needed for {ininame}")
        tiles = tiles[:frame_count]

    old_fp = f"{donor.lower()}\\{donor.lower()}-"
    new_fp = f"{ininame.lower()}\\{ininame.lower()}-"
    block = "".join(
        t.replace(f"<Name>{donor}</Name>", f"<Name>{ininame}</Name>")
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
    ap.add_argument("--tileset-donor", default=None,
                    help="RA_UNITS.XML block to clone when the TD asset has no RA "
                         "equivalent (e.g. E4 for E5 chem warrior). Defaults to td_asset.")
    ap.add_argument("--source", choices=["td", "ra"], default="td",
                    help="Which vanilla MEG the asset ZIP comes from: td = "
                         "TEXTURES_TD_SRGB.MEG (default), ra = TEXTURES_RA_SRGB.MEG "
                         "(for independent copies of RA units, e.g. the faction MCVs).")
    args = ap.parse_args()

    meg = source_meg_path()
    if args.source == "ra":
        meg = meg.with_name("TEXTURES_RA_SRGB.MEG")
    zip_dest, frames = repack_zip(args.td_asset, args.ininame, meg)
    tiles = clone_tileset_block(args.td_asset, args.ininame, donor=args.tileset_donor,
                                frame_count=frames)
    patch_rabuildables_xml(args.ininame, args.text_name, args.text_desc, args.build_icon)

    print(f"  ZIP:          {zip_dest}  ({frames} frames)")
    print(f"  RA_UNITS.XML: {tiles} <{args.ininame}> tiles")
    print(f"  RABUILDABLES: RA_{args.ininame}  (cameo {args.build_icon})")
    if frames != tiles:
        print(f"  WARNING: frame count ({frames}) != tile count ({tiles})")


if __name__ == "__main__":
    main()
