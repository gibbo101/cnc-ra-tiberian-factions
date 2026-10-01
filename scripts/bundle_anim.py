#!/usr/bin/env python3
'''
bundle_anim.py — bundle a TD directional muzzle-anim set into RA_VFX.XML.

TD weapons whose visual is a directional muzzle ANIMATION (not a flying
projectile) — the flamethrower (FLAME-*), the chem warrior (CHEM-*), the SAM
and gun muzzle flashes — store 8 facing-specific anim tiles `<BASE>-N ..
<BASE>-NW` in `TEXTURES_TD_SRGB.MEG`. To port one as its own TD-prefixed
engine anim set we must:

1. Extract each `<BASE>-<dir>.ZIP` from the vanilla `TEXTURES_TD_SRGB.MEG`.
2. Repack it with a TD-prefixed name (`<PREFIX>-<dir>.ZIP`) AND TD-prefixed
   internal frame filenames (`<prefix>-<dir>-NNNN.tga`). The rename is
   mandatory: the launcher derives the ZIP basename from each frame path's
   first segment, and the base game ships its OWN `FLAME-*`/`CHEM-*` tiles
   (CONFIG.MEG references them) — an unprefixed name resolves to the base
   def, not ours. (See playbook §3.26.)
3. Insert the matching `<Tile>` blocks into `RA_VFX.XML` so the launcher
   overlay can resolve `<PREFIX>-<dir>` by name at the firing facing.

The ZIPs and tile blocks land in the tree asset_packs assigns `<PREFIX>-<dir>`:
the mod's own (`RA_VFX.XML`) or an asset pack's (`<PACK PREFIX>_VFX.XML`).

The DLL side (8 `ANIM_<X>_*` types + the `techno.cpp` Fire_At dispatch +
the donor-ImageData fix in `AnimTypeClass::One_Time`) is hand-written; this
script only handles the on-disk art + tileset. Worked examples: TDFLAME
(E4 flamethrower), TDCHEM (E5 chem warrior).

Idempotent: re-running replaces existing tile blocks rather than duplicating.

Typical usage:
  scripts/bundle_anim.py CHEM TDCHEM
  scripts/bundle_anim.py CHEM TDCHEM --dry-run

License: GPL v3 (inherited from Vanilla Conquer base).
'''
import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import asset_packs                 # noqa: E402
import bundle_assets               # noqa: E402  -- reuse repack/count/emit/strip
import meg_extract                 # noqa: E402

REPO_ROOT  = SCRIPT_DIR.parent

# Facing order matches the engine's ANIM_<X>_N .. ANIM_<X>_NW enum block
# (Dir_Facing order: N, NE, E, SE, S, SW, W, NW).
DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def patch_ra_vfx_xml(td_name, frame_basename, frame_count, *, dry_run=False):
    '''Insert/replace `<Tile>` blocks for `td_name` in its VFX tileset XML.

    Reuses bundle_assets' format-identical emit/strip helpers (RA_VFX uses
    the same Tile/Key/Name/Shape/Value/Frames indentation as RA_STRUCTURES),
    inserting before the `</Tiles>` close of the RA_VFX TilesetTypeClass.
    '''
    vfx_xml = Path(asset_packs.tileset_xml(td_name, "VFX"))
    content = vfx_xml.read_text(encoding="utf-8")
    original = content

    content = bundle_assets.strip_tileset_entries(content, td_name)
    new_block = bundle_assets.emit_structures_tileset(
        td_name, frame_basename, frame_count, empty_first_shape=False
    )

    close_match = re.search(r"\t\t</Tiles>", content)
    if close_match is None:
        raise RuntimeError(f"Couldn't find </Tiles> close tag in {vfx_xml.name}")
    insert_at = close_match.start()
    content = content[:insert_at] + new_block + content[insert_at:]

    changed = (content != original)
    if changed and not dry_run:
        vfx_xml.write_text(content, encoding="utf-8", newline="\n")
    return changed


def bundle_direction(base, prefix, direction, meg_path, *, dry_run=False):
    '''Extract + repack one `<base>-<dir>.ZIP` → `<prefix>-<dir>.ZIP` and
    patch its VFX tileset tile blocks. Returns (frame_count, xml_changed).'''
    src_name  = f"{base}-{direction}.ZIP"          # e.g. CHEM-N.ZIP
    td_name   = f"{prefix}-{direction}"            # tileset key, e.g. TDCHEM-N
    dest_zip  = Path(asset_packs.art_zip(td_name, "VFX"))   # TDCHEM-N.ZIP
    old_pfx   = f"{base.lower()}-{direction.lower()}"   # chem-n
    new_pfx   = f"{prefix.lower()}-{direction.lower()}" # tdchem-n

    if not dry_run:
        dest_zip.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest_zip.with_suffix(".extracted.zip")
        try:
            if not bundle_assets.extract_named_zip(meg_path, src_name, tmp):
                raise RuntimeError(f"{src_name} not found in {meg_path}")
            bundle_assets.repack_zip_with_prefix(
                tmp, dest_zip, old_prefix=old_pfx, new_prefix=new_pfx
            )
        finally:
            if tmp.exists():
                tmp.unlink()

    frame_count = bundle_assets.count_frames(dest_zip) if not dry_run else 0
    xml_changed = patch_ra_vfx_xml(
        td_name, new_pfx, frame_count, dry_run=dry_run
    ) if not dry_run else False
    return frame_count, xml_changed


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("base",   help="TD anim base name in the MEG, e.g. CHEM")
    ap.add_argument("prefix", help="TD-prefixed tileset name, e.g. TDCHEM")
    ap.add_argument("--dry-run", action="store_true",
                    help="Don't write any files; report intent.")
    args = ap.parse_args()

    meg_path = bundle_assets.source_meg_path()
    total_xml_changed = False
    for d in DIRECTIONS:
        try:
            frames, changed = bundle_direction(
                args.base, args.prefix, d, meg_path, dry_run=args.dry_run
            )
        except Exception as e:
            print(f"[bundle_anim] {args.prefix}-{d}: FAILED: {e}", file=sys.stderr)
            return 1
        total_xml_changed = total_xml_changed or changed
        verb = "would write" if args.dry_run else "wrote"
        print(f"[bundle_anim] {args.prefix}-{d}: {verb} "
              f"{Path(asset_packs.art_zip(f'{args.prefix}-{d}', 'VFX')).relative_to(REPO_ROOT)} "
              f"({frames} frames), xml={'patched' if changed else 'unchanged'}")
    print(f"[bundle_anim] done — {Path(asset_packs.tileset_xml(f'{args.prefix}-{DIRECTIONS[0]}', 'VFX')).name} "
          f"{'patched' if total_xml_changed else 'unchanged'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
