#!/usr/bin/env python3
'''
bundle_assets.py — assemble all on-disk asset files for one manifest entry.

Given a `buildings_manifest.py` entry, this script:

1. Extracts the TD sprite ZIPs (`<image>.ZIP` + `<image>MAKE.ZIP`) from the
   vanilla `TEXTURES_TD_SRGB.MEG` shipped with C&C Remastered.
2. Copies them into `resources/.../STRUCTURES/` with TD-prefixed filenames
   (`TD<image>.ZIP` / `TD<image>MAKE.ZIP`). Internal frame TGAs stay at their
   TD-original names — only the outer ZIP is renamed.
3. Patches `RA_STRUCTURES.XML` so the launcher knows the tileset under the
   TD-prefixed name. Frame paths inside the tileset still point at the
   unprefixed internal TGAs (matching what `meg_extract.py` produces).
4. Patches `RABUILDABLES.XML` to add the `RA_TDxxx` `ObjectTypeClass` block
   that wires the sidebar display name + cameo (`BuildIcon_*`) for the entry.
   Without this block the sidebar tooltip reads `<Missing> TDxxx`.

Idempotent: re-running on an entry replaces existing rows/blocks rather than
duplicating them. Safe to run after every manifest edit.

Typical usage (orchestrated by `add_building.py`):
  scripts/bundle_assets.py TDPYLE
  scripts/bundle_assets.py --all
  scripts/bundle_assets.py TDPYLE --dry-run

License: GPL v3 (inherited from Vanilla Conquer base).
'''
import argparse
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import buildings_manifest          # noqa: E402
import meg_extract                  # noqa: E402  -- reused for MEG reads

REPO_ROOT          = SCRIPT_DIR.parent
MOD_ROOT           = REPO_ROOT / "resources/remaster_mods/Vanilla_RA"
STRUCTURES_DIR     = MOD_ROOT / "Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES"
RA_STRUCTURES_XML  = MOD_ROOT / "Data/XML/TILESETS/RA_STRUCTURES.XML"
RABUILDABLES_XML   = MOD_ROOT / "Data/XML/OBJECTS/UNITS/RABUILDABLES.XML"

# Source MEG file. Default path is the standard Steam install; override with
# CNC_REMASTER_DATA env var when running from a different machine.
DEFAULT_GAME_DATA  = Path.home() / ".steam/steam/steamapps/common/CnCRemastered/Data"
SOURCE_MEG_NAME    = "TEXTURES_TD_SRGB.MEG"


def source_meg_path():
    base = Path(os.environ.get("CNC_REMASTER_DATA", DEFAULT_GAME_DATA))
    p = base / SOURCE_MEG_NAME
    if not p.exists():
        raise FileNotFoundError(
            f"Source MEG not found at {p}. Set CNC_REMASTER_DATA to the "
            f"directory containing {SOURCE_MEG_NAME}."
        )
    return p


# ---------------------------------------------------------------------------
# MEG extraction wrapper
# ---------------------------------------------------------------------------

def extract_named_zip(meg_path, zip_basename, dest_path):
    '''Extract one specific ZIP entry from a MEG to `dest_path`.

    `zip_basename` is the filename without path, e.g. "NUKE.ZIP". The MEG
    file table records full paths like `DATA\\ART\\...\\NUKE.ZIP`; we match
    on basename so the caller doesn't need to know the in-MEG directory.
    '''
    data, files = meg_extract.open_meg(str(meg_path))
    target = zip_basename.lower()
    for name, size, dat_off in files:
        if os.path.basename(name.replace("\\", "/")).lower() == target:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as out:
                out.write(data[dat_off:dat_off + size])
            return True
    return False


def repack_zip_with_prefix(source_zip, dest_zip, old_prefix, new_prefix):
    '''Read `source_zip`, rename every member matching `old_prefix-NNNN.*`
    to `new_prefix-NNNN.*`, and write the result to `dest_zip`.

    Required because the launcher's tileset loader derives the containing
    ZIP basename from the frame path's first segment (`<Frame>foo\\foo-0.tga</Frame>`
    → look for `FOO.ZIP`). If we want our tileset to live in `TDFOO.ZIP`,
    the internal filenames must be `tdfoo-NNNN.*` and frame paths must say
    `tdfoo\\tdfoo-NNNN.tga`. Keeping the originals in place would force the
    launcher to look for `FOO.ZIP` and miss our renamed file entirely.

    `.tga` and `.meta` sidecars are both repacked. Anything not matching
    the `{old_prefix}-NNNN.*` pattern is copied through unchanged (defensive).
    '''
    pattern = re.compile(
        r"^(" + re.escape(old_prefix) + r")-(\d{4})\.([^.]+)$",
        re.IGNORECASE,
    )
    with zipfile.ZipFile(source_zip, "r") as src, \
         zipfile.ZipFile(dest_zip,   "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            m = pattern.match(info.filename)
            if m:
                new_name = f"{new_prefix}-{m.group(2)}.{m.group(3)}"
            else:
                new_name = info.filename
            # Preserve the original date_time / external_attr so the launcher
            # doesn't see the file as suspiciously fresh; only the name changes.
            new_info = zipfile.ZipInfo(filename=new_name, date_time=info.date_time)
            new_info.external_attr = info.external_attr
            new_info.compress_type = zipfile.ZIP_DEFLATED
            dst.writestr(new_info, data)


def count_frames(zip_path):
    '''Return the highest frame index N in foo-NNNN.tga, +1 (i.e. the count).

    The TD sprite ZIPs from CnC Remastered always contain a contiguous run
    `foo-0000.tga ... foo-NNNN.tga`. Each TGA may have a sibling `.meta` file
    which we ignore. Used to know how many `<Shape>` entries to emit.
    '''
    pattern = re.compile(r".*-(\d{4})\.tga$", re.IGNORECASE)
    highest = -1
    with zipfile.ZipFile(zip_path, "r") as z:
        for entry in z.namelist():
            m = pattern.match(entry)
            if m:
                highest = max(highest, int(m.group(1)))
    if highest < 0:
        raise RuntimeError(f"No frame TGAs found in {zip_path}")
    return highest + 1


# ---------------------------------------------------------------------------
# XML helpers (string-based; XML libs aren't worth the round-trip overhead
# for these large hand-edited files where vanilla blocks must be preserved
# byte-for-byte to avoid spurious diffs).
# ---------------------------------------------------------------------------

def emit_structures_tileset(td_name, frame_basename, frame_count, *, empty_first_shape=False):
    '''Emit the `<Tile>` blocks for a tileset name (`td_name`) covering
    `frame_count` shapes. `frame_basename` is the lowercase internal asset
    name inside the ZIP (e.g. "nuke" for NUKE.ZIP containing nuke-NNNN.tga).

    `empty_first_shape=True` flags this as a TD-source MAKE tileset, where
    frames inside the ZIP start at index 0001 (not 0000) — the missing 0000
    slot is the "empty placement marker" convention. Emitting a real frame
    ref for shape 0 produces a one-frame Petroglyph flash on placement,
    because the launcher hits a missing TGA. With this flag, shape 0 emits
    `<Frame />` (transparent placeholder) and frames 0001..N map to shapes
    1..N (i.e. shape index == frame index when the offset is applied).
    '''
    lines = []
    for shape in range(frame_count):
        lines.append("\t\t\t<Tile>")
        lines.append("\t\t\t\t<Key>")
        lines.append(f"\t\t\t\t\t<Name>{td_name}</Name>")
        lines.append(f"\t\t\t\t\t<Shape>{shape}</Shape>")
        lines.append("\t\t\t\t</Key>")
        lines.append("\t\t\t\t<Value>")
        lines.append("\t\t\t\t\t<Frames>")
        if empty_first_shape and shape == 0:
            lines.append("\t\t\t\t\t\t<Frame />")
        else:
            lines.append(f"\t\t\t\t\t\t<Frame>{frame_basename}\\{frame_basename}-{shape:04d}.tga</Frame>")
        lines.append("\t\t\t\t\t</Frames>")
        lines.append("\t\t\t\t</Value>")
        lines.append("\t\t\t</Tile>")
    return "\n".join(lines) + "\n"


def strip_tileset_entries(content, td_name):
    '''Remove every `<Tile>` whose `<Key><Name>td_name</Name>` matches.

    Used for idempotency: before inserting fresh entries we drop any stale
    ones with the same name. The XML format wraps each Tile across multiple
    lines with consistent indentation:

        \\t\\t\\t<Tile>
        \\t\\t\\t\\t<Key>
        \\t\\t\\t\\t\\t<Name>...</Name>
        \\t\\t\\t\\t\\t<Shape>N</Shape>
        \\t\\t\\t\\t</Key>
        \\t\\t\\t\\t<Value>
            ...frame lines...
        \\t\\t\\t\\t</Value>
        \\t\\t\\t</Tile>

    The `<Name>` is anchored *immediately* after `<Tile>` + `<Key>` so a
    non-greedy regex can't lazily skip over upstream blocks (a previous bug
    that nuked ~95% of the vanilla XML).
    '''
    block_re = re.compile(
        r"\t\t\t<Tile>\s*\n"
        r"\t\t\t\t<Key>\s*\n"
        r"\t\t\t\t\t<Name>" + re.escape(td_name) + r"</Name>\s*\n"
        r"\t\t\t\t\t<Shape>\d+</Shape>\s*\n"
        r"\t\t\t\t</Key>\s*\n"
        r"\t\t\t\t<Value>\s*\n"
        r"(?:\t\t\t\t\t[^\n]*\n)+"  # one or more deeply-indented frame/inner lines
        r"\t\t\t\t</Value>\s*\n"
        r"\t\t\t</Tile>\s*\n"
    )
    return block_re.sub("", content)


def patch_ra_structures_xml(td_name, frame_basename, frame_count, *, dry_run=False, empty_first_shape=False):
    '''Insert/replace tileset entries for `td_name` in RA_STRUCTURES.XML.

    Inserts the new blocks before the closing `</Tiles>` of the
    `RA_Structures` TilesetTypeClass. Existing blocks for `td_name` are
    stripped first so re-runs don't accumulate duplicates.

    `empty_first_shape` — see emit_structures_tileset(). Set for MAKE tilesets.
    '''
    content = RA_STRUCTURES_XML.read_text(encoding="utf-8")
    original = content

    content = strip_tileset_entries(content, td_name)
    new_block = emit_structures_tileset(
        td_name, frame_basename, frame_count, empty_first_shape=empty_first_shape
    )

    # Find the closing </Tiles> tag belonging to the first <Tiles> block
    # (there's only one RA_Structures TilesetTypeClass in this file).
    close_match = re.search(r"\t\t</Tiles>", content)
    if close_match is None:
        raise RuntimeError("Couldn't find </Tiles> close tag in RA_STRUCTURES.XML")
    insert_at = close_match.start()
    content = content[:insert_at] + new_block + content[insert_at:]

    changed = (content != original)
    if changed and not dry_run:
        RA_STRUCTURES_XML.write_text(content, encoding="utf-8", newline="\n")
    return changed


# ---------------------------------------------------------------------------
# RABUILDABLES.XML patching
# ---------------------------------------------------------------------------

def emit_buildable_block(td_ininame, text_id_name, text_id_desc, build_icon):
    return (
        f'\t<ObjectTypeClass Name="RA_{td_ininame}" Classification="CNCBuildableObject" CanInstantiate="False">\n'
        f'\t\t<CNCEncyclopediaComponent>\n'
        f'\t\t\t<ObjectNameTextID>{text_id_name}</ObjectNameTextID>\n'
        f'\t\t\t<ObjectDescriptionTextID>{text_id_desc}</ObjectDescriptionTextID>\n'
        f'\t\t\t<BuildIcon>{build_icon}</BuildIcon>\n'
        f'\t\t</CNCEncyclopediaComponent>\n'
        f'\t</ObjectTypeClass>\n'
    )


def strip_buildable_block(content, td_ininame):
    '''Remove any existing `<ObjectTypeClass Name="RA_<td_ininame>">` block.'''
    block_re = re.compile(
        r"\t<ObjectTypeClass Name=\"RA_" + re.escape(td_ininame) + r"\".*?\n"
        r"(?:.*?\n)*?"
        r"\t</ObjectTypeClass>\n\n?",
        re.DOTALL,
    )
    return block_re.sub("", content)


def patch_rabuildables_xml(td_ininame, text_id_name, text_id_desc, build_icon, *, dry_run=False):
    '''Insert/replace the `RA_TDxxx` ObjectTypeClass block.

    Existing blocks for `td_ininame` are stripped first. Insertion point is
    immediately before the closing `</ObjectTypeList>`. Subsequent entries
    accumulate in source order, which matches the existing TDNUKE/TDNUK2 layout.
    '''
    content = RABUILDABLES_XML.read_text(encoding="utf-8")
    original = content

    content = strip_buildable_block(content, td_ininame)
    new_block = emit_buildable_block(td_ininame, text_id_name, text_id_desc, build_icon)

    close_idx = content.rfind("</ObjectTypeList>")
    if close_idx < 0:
        raise RuntimeError("Couldn't find </ObjectTypeList> close tag in RABUILDABLES.XML")

    # Preserve any existing comment header or blank line just before the close.
    # We insert with a leading blank line so multiple entries are visually
    # separated in source.
    content = content[:close_idx].rstrip() + "\n\n" + new_block + "\n" + content[close_idx:]

    changed = (content != original)
    if changed and not dry_run:
        RABUILDABLES_XML.write_text(content, encoding="utf-8", newline="\n")
    return changed


# ---------------------------------------------------------------------------
# Per-entry orchestrator
# ---------------------------------------------------------------------------

def bundle(entry, *, dry_run=False, meg_path=None):
    '''Run the full asset pipeline for one manifest entry.

    Returns a dict summarising what was changed.
    '''
    if meg_path is None:
        meg_path = source_meg_path()

    td_asset = entry["td_asset"]         # unprefixed TD asset name in MEG, e.g. "NUKE"
    ininame  = entry["ininame"]          # our IniName + tileset key, e.g. "TDNUKE"
    text_name = entry.get("text_id_name")
    text_desc = entry.get("text_id_desc")
    build_icon = entry.get("build_icon")

    if not (text_name and text_desc and build_icon):
        raise RuntimeError(
            f"Manifest entry {ininame} is missing text_id_name / text_id_desc / "
            "build_icon — required for sidebar wiring (see RABUILDABLES.XML)."
        )

    # Step 1+2: extract source ZIPs from MEG to temp paths, then repack
    # with TD-prefixed internal filenames into the mod's TD-prefixed
    # destination ZIP. The repack is REQUIRED because the launcher derives
    # the ZIP filename from each frame path's first segment — if frame
    # paths say `nuke\nuke-0.tga` the launcher looks for NUKE.ZIP, missing
    # our TDNUKE.ZIP entirely.
    main_src_name  = f"{td_asset}.ZIP"
    make_src_name  = f"{td_asset}MAKE.ZIP"
    main_dest = STRUCTURES_DIR / f"{ininame}.ZIP"
    make_dest = STRUCTURES_DIR / f"{ininame}MAKE.ZIP"

    if not dry_run:
        main_dest.parent.mkdir(parents=True, exist_ok=True)
        tmp_main = main_dest.with_suffix(".extracted.zip")
        tmp_make = make_dest.with_suffix(".extracted.zip")
        try:
            if not extract_named_zip(meg_path, main_src_name, tmp_main):
                raise RuntimeError(f"{main_src_name} not found in {meg_path}")
            if not extract_named_zip(meg_path, make_src_name, tmp_make):
                raise RuntimeError(f"{make_src_name} not found in {meg_path}")
            # Internal filenames: source is `<td_asset_lower>-NNNN.*` (e.g.
            # nuke-0000.tga). Destination is `<ininame_lower>-NNNN.*` (e.g.
            # tdnuke-0000.tga). Likewise for the MAKE archive.
            repack_zip_with_prefix(
                tmp_main, main_dest,
                old_prefix=td_asset.lower(),
                new_prefix=ininame.lower(),
            )
            repack_zip_with_prefix(
                tmp_make, make_dest,
                old_prefix=td_asset.lower() + "make",
                new_prefix=ininame.lower() + "make",
            )
        finally:
            for tmp in (tmp_main, tmp_make):
                if tmp.exists():
                    tmp.unlink()

    # Step 3: patch RA_STRUCTURES.XML.
    # Frame paths use the IniName-derived lowercase prefix so the launcher's
    # ZIP discovery resolves to our TD-prefixed ZIP file.
    frame_basename = ininame.lower()
    main_count = count_frames(main_dest) if not dry_run else 0
    make_count = count_frames(make_dest) if not dry_run else 0

    structures_changed_main = patch_ra_structures_xml(
        ininame, frame_basename, main_count, dry_run=dry_run,
        empty_first_shape=False,  # idle: shape 0 is the placed building
    ) if not dry_run else False
    structures_changed_make = patch_ra_structures_xml(
        f"{ininame}MAKE", frame_basename + "make", make_count, dry_run=dry_run,
        # TD-source MAKE ZIPs start at frame 0001 — shape 0 is the empty
        # placement marker (transparent), shapes 1..N are the buildup frames.
        # Without this, the launcher hits the missing *-0000.tga for one
        # frame on placement → Petroglyph flash.
        empty_first_shape=True,
    ) if not dry_run else False

    # Step 4: patch RABUILDABLES.XML.
    buildables_changed = patch_rabuildables_xml(
        ininame, text_name, text_desc, build_icon, dry_run=dry_run
    )

    return {
        "main_zip":            str(main_dest.relative_to(REPO_ROOT)),
        "make_zip":            str(make_dest.relative_to(REPO_ROOT)),
        "main_frame_count":    main_count,
        "make_frame_count":    make_count,
        "structures_changed":  structures_changed_main or structures_changed_make,
        "buildables_changed":  buildables_changed,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("names", nargs="*", help="IniName(s) to bundle (e.g. TDPYLE).")
    parser.add_argument("--all", action="store_true", help="Bundle every manifest entry.")
    parser.add_argument("--dry-run", action="store_true", help="Don't write any files; report intent.")
    args = parser.parse_args()

    if args.all:
        if args.names:
            parser.error("--all takes no positional args")
        entries = list(buildings_manifest.ALL)
    else:
        if not args.names:
            parser.error("specify at least one IniName, or pass --all")
        entries = [buildings_manifest.by_name(n) for n in args.names]

    meg_path = source_meg_path()
    for entry in entries:
        try:
            summary = bundle(entry, dry_run=args.dry_run, meg_path=meg_path)
        except Exception as e:
            print(f"[bundle_assets] {entry['ininame']}: FAILED: {e}", file=sys.stderr)
            return 1
        verb = "would write" if args.dry_run else "wrote"
        print(
            f"[bundle_assets] {entry['ininame']}: {verb} "
            f"{summary['main_zip']} ({summary['main_frame_count']} frames), "
            f"{summary['make_zip']} ({summary['make_frame_count']} frames), "
            f"structures_xml={'patched' if summary['structures_changed'] else 'unchanged'}, "
            f"buildables_xml={'patched' if summary['buildables_changed'] else 'unchanged'}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
