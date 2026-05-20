#!/usr/bin/env python3
'''
One-off TDMCV asset pipeline.

Hand-coded counterpart to scripts/bundle_assets.py for the v0.3 closing
slice (kids playtest). Units differ from buildings in three ways that make
generalizing bundle_assets.py more friction than it's worth for one entry:

- No MAKE/buildup ZIP (units spawn directly, no construction animation).
- Different on-disk dir (`UNITS/` vs `STRUCTURES/`).
- Different tileset XML (`RA_UNITS.XML` vs `RA_STRUCTURES.XML`) — and
  unlike RA_STRUCTURES.XML, the mod doesn't ship a copy of RA_UNITS.XML
  yet, so this script seeds the override from the vanilla CONFIG.MEG
  extract on first run.

When we add a second vehicle in v0.4, fold this into bundle_assets.py with
a `kind=unit|structure` field on the manifest entries.

License: GPL v3 (inherited from Vanilla Conquer base).
'''
import os
import re
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import meg_extract  # noqa: E402

REPO_ROOT = SCRIPT_DIR.parent
MOD_ROOT = REPO_ROOT / "resources/remaster_mods/Vanilla_RA"
UNITS_DIR = MOD_ROOT / "Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
RA_UNITS_XML = MOD_ROOT / "Data/XML/TILESETS/RA_UNITS.XML"
RABUILDABLES_XML = MOD_ROOT / "Data/XML/OBJECTS/UNITS/RABUILDABLES.XML"

GAME_DATA = Path.home() / ".steam/steam/steamapps/common/CnCRemastered/Data"
CONFIG_MEG = GAME_DATA / "CONFIG.MEG"
TD_TEX_MEG = GAME_DATA / "TEXTURES_TD_SRGB.MEG"

TD_MCV_BASENAME = "MCV.ZIP"        # name inside TEXTURES_TD_SRGB.MEG
OUR_INI = "TDMCV"
OUR_ZIP = "TDMCV.ZIP"
OUR_FRAME_PREFIX = "tdmcv"


def extract_named_zip(meg_path, zip_basename, dest_path):
    data, files = meg_extract.open_meg(str(meg_path))
    target = zip_basename.lower()
    for name, size, off in files:
        if os.path.basename(name.replace("\\", "/")).lower() == target:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(data[off:off + size])
            return True
    return False


def extract_file_from_meg(meg_path, in_meg_path_substr, dest_path):
    '''Extract by path substring match (case-insensitive). Used for the
    RA_UNITS.XML seed, where the MEG entry name is the full backslashed
    DATA\\XML\\TILESETS\\RA_UNITS.XML path.'''
    data, files = meg_extract.open_meg(str(meg_path))
    needle = in_meg_path_substr.lower()
    for name, size, off in files:
        if needle in name.lower():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(data[off:off + size])
            return True
    return False


def repack_zip_with_prefix(src_zip, dst_zip, old_prefix, new_prefix):
    '''Identical to bundle_assets.py:repack_zip_with_prefix — rename every
    `<old_prefix>-NNNN.<ext>` member to `<new_prefix>-NNNN.<ext>`. See that
    function's docstring for the rationale (launcher derives ZIP basename
    from frame paths).'''
    pattern = re.compile(
        r"^(" + re.escape(old_prefix) + r")-(\d{4})\.([^.]+)$",
        re.IGNORECASE,
    )
    with zipfile.ZipFile(src_zip, "r") as src, \
         zipfile.ZipFile(dst_zip, "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            m = pattern.match(info.filename)
            new_name = (
                f"{new_prefix}-{m.group(2)}.{m.group(3)}"
                if m else info.filename
            )
            new_info = zipfile.ZipInfo(filename=new_name, date_time=info.date_time)
            new_info.external_attr = info.external_attr
            new_info.compress_type = zipfile.ZIP_DEFLATED
            dst.writestr(new_info, data)


def count_frames(zip_path):
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


def emit_tileset_block(td_name, frame_prefix, frame_count):
    '''Emit `<Tile>` blocks for `frame_count` shapes — same indentation as
    the vanilla RA_UNITS.XML body (4 tabs for `<Tile>`).'''
    lines = []
    for shape in range(frame_count):
        lines.append("\t\t\t<Tile>")
        lines.append("\t\t\t\t<Key>")
        lines.append(f"\t\t\t\t\t<Name>{td_name}</Name>")
        lines.append(f"\t\t\t\t\t<Shape>{shape}</Shape>")
        lines.append("\t\t\t\t</Key>")
        lines.append("\t\t\t\t<Value>")
        lines.append("\t\t\t\t\t<Frames>")
        lines.append(f"\t\t\t\t\t\t<Frame>{frame_prefix}\\{frame_prefix}-{shape:04d}.tga</Frame>")
        lines.append("\t\t\t\t\t</Frames>")
        lines.append("\t\t\t\t</Value>")
        lines.append("\t\t\t</Tile>")
    return "\n".join(lines) + "\n"


def strip_tileset_entries(content, td_name):
    block_re = re.compile(
        r"\t\t\t<Tile>\s*\n"
        r"\t\t\t\t<Key>\s*\n"
        r"\t\t\t\t\t<Name>" + re.escape(td_name) + r"</Name>\s*\n"
        r"\t\t\t\t\t<Shape>\d+</Shape>\s*\n"
        r"\t\t\t\t</Key>\s*\n"
        r"\t\t\t\t<Value>\s*\n"
        r"(?:\t\t\t\t\t[^\n]*\n)+"
        r"\t\t\t\t</Value>\s*\n"
        r"\t\t\t</Tile>\s*\n"
    )
    return block_re.sub("", content)


def patch_ra_units_xml(td_name, frame_prefix, frame_count):
    content = RA_UNITS_XML.read_text(encoding="utf-8")
    original = content
    content = strip_tileset_entries(content, td_name)
    new_block = emit_tileset_block(td_name, frame_prefix, frame_count)
    close_match = re.search(r"\t\t</Tiles>", content)
    if close_match is None:
        raise RuntimeError("Couldn't find </Tiles> close tag in RA_UNITS.XML")
    insert_at = close_match.start()
    content = content[:insert_at] + new_block + content[insert_at:]
    if content != original:
        RA_UNITS_XML.write_text(content, encoding="utf-8", newline="\n")
        return True
    return False


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
    block_re = re.compile(
        r"\t<ObjectTypeClass Name=\"RA_" + re.escape(td_ininame) + r"\".*?\n"
        r"(?:.*?\n)*?"
        r"\t</ObjectTypeClass>\n\n?",
        re.DOTALL,
    )
    return block_re.sub("", content)


def patch_rabuildables_xml(td_ininame, text_id_name, text_id_desc, build_icon):
    content = RABUILDABLES_XML.read_text(encoding="utf-8")
    original = content
    content = strip_buildable_block(content, td_ininame)
    new_block = emit_buildable_block(td_ininame, text_id_name, text_id_desc, build_icon)
    close_idx = content.rfind("</ObjectTypeList>")
    if close_idx < 0:
        raise RuntimeError("Couldn't find </ObjectTypeList> in RABUILDABLES.XML")
    content = content[:close_idx].rstrip() + "\n\n" + new_block + "\n" + content[close_idx:]
    if content != original:
        RABUILDABLES_XML.write_text(content, encoding="utf-8", newline="\n")
        return True
    return False


def main():
    # Step 1: seed RA_UNITS.XML from CONFIG.MEG if our mod doesn't have one
    # yet. We override the vanilla 2.2MB file rather than try to ship a
    # diff — the launcher resolves tileset XMLs as full-file overrides.
    if not RA_UNITS_XML.exists():
        if not CONFIG_MEG.exists():
            raise FileNotFoundError(f"CONFIG.MEG not found at {CONFIG_MEG}")
        ok = extract_file_from_meg(CONFIG_MEG, "ra_units.xml", RA_UNITS_XML)
        if not ok:
            raise RuntimeError("RA_UNITS.XML not found in CONFIG.MEG")
        print(f"[setup_tdmcv_assets] seeded {RA_UNITS_XML.relative_to(REPO_ROOT)} from CONFIG.MEG")
    else:
        print(f"[setup_tdmcv_assets] {RA_UNITS_XML.relative_to(REPO_ROOT)} already present, skipping seed")

    # Step 2: extract TD MCV asset, repack with TDMCV prefix
    UNITS_DIR.mkdir(parents=True, exist_ok=True)
    dst_zip = UNITS_DIR / OUR_ZIP
    tmp_zip = dst_zip.with_suffix(".extracted.zip")
    try:
        if not extract_named_zip(TD_TEX_MEG, TD_MCV_BASENAME, tmp_zip):
            raise RuntimeError(f"{TD_MCV_BASENAME} not found in {TD_TEX_MEG}")
        repack_zip_with_prefix(
            tmp_zip, dst_zip,
            old_prefix="mcv",
            new_prefix=OUR_FRAME_PREFIX,
        )
    finally:
        if tmp_zip.exists():
            tmp_zip.unlink()
    frame_count = count_frames(dst_zip)
    print(f"[setup_tdmcv_assets] wrote {dst_zip.relative_to(REPO_ROOT)} ({frame_count} frames)")

    # Step 3: patch RA_UNITS.XML with TDMCV tileset block
    changed = patch_ra_units_xml(OUR_INI, OUR_FRAME_PREFIX, frame_count)
    print(f"[setup_tdmcv_assets] RA_UNITS.XML: {'patched' if changed else 'unchanged'}")

    # Step 4: patch RABUILDABLES.XML with the RA_TDMCV ObjectTypeClass
    # TechLevel=99 means this is never sidebar-built, but the encyclopedia
    # /select tooltip still keys on this block. Reuse the GDI MCV text
    # IDs + cameo (only the TD-themed sidebar has BuildIcon_TD_MCV, but
    # we already verified its presence in CONFIG.MEG strings).
    changed = patch_rabuildables_xml(
        OUR_INI,
        text_id_name="TEXT_UNIT_TITLE_GDI_MCV",
        text_id_desc="TEXT_UNIT_DESC_GDI_MCV",
        build_icon="BuildIcon_TD_MCV",
    )
    print(f"[setup_tdmcv_assets] RABUILDABLES.XML: {'patched' if changed else 'unchanged'}")


if __name__ == "__main__":
    sys.exit(main() or 0)
