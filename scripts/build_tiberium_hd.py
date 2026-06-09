#!/usr/bin/env python3
'''
build_tiberium_hd.py — build the HD (Remastered) art for the TIB01 Tiberium
overlay and wire it into the launcher tileset.

The launcher renders an overlay by AssetName = IniName ("TIB01") with
ShapeIndex = the cell's OverlayData (0-11 density). RA's own GOLD01 overlay
maps Shape 0-11 -> gold01.tem\\gold01.tem-NNNN.tga inside
DATA\\XML\\TILESETS\\RA_TERRAIN_TEMPERATE.XML. TD's TI1 overlay has the identical
12-shape structure, with HD frames shipped as loose DDS in TEXTURES_TD_SRGB.MEG.

So this script:
  1. Extracts TD TI1's 12 HD frames (TI1.TEM-0000..0011.DDS) from the vanilla
     TEXTURES_TD_SRGB.MEG.
  2. Converts each DDS -> TGA (RGBA) and writes a per-frame .meta JSON (full-size,
     no crop) matching the launcher's ZIP texture convention.
  3. Packs them into TIB01.TEM.ZIP under the mod's terrain/temperate texture dir.
  4. Patches a copy of base RA_TERRAIN_TEMPERATE.XML to add a TIB01 tile block
     (Shape 0-11) and writes it into the mod's TILESETS dir (full replacement,
     same delivery pattern as RA_STRUCTURES.XML).

Temperate only for now (the first TD maps we import are temperate); Snow/Interior
are a later copy. See memory project-tiberium-overlay-implementation.md.

License: GPL v3 (inherited from Vanilla Conquer base).
'''
import io
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
MOD_ROOT = REPO_ROOT / "resources/remaster_mods/Vanilla_RA"

GAME_DATA = Path(os.environ.get(
    "CNC_REMASTER_DATA",
    Path.home() / ".steam/steam/steamapps/common/CnCRemastered/Data"))
TD_TEX_MEG = GAME_DATA / "TEXTURES_TD_SRGB.MEG"
CONFIG_MEG = GAME_DATA / "CONFIG.MEG"

TD_TERRAIN_TEMP = r"DATA\ART\TEXTURES\SRGB\TIBERIAN_DAWN\TERRAIN\TEMPERATE"

# Temperate terrain HD assets to bundle into RA_TERRAIN_TEMPERATE.XML. Each:
#   (tileset Name, dot-free asset stem, MEG subdir, frame fmt, frame count)
# Dot-free stem (mirrors structure assets e.g. "tdobli" -> TDOBLI.ZIP): the
# launcher derives the ZIP key from the frame path's first component, and a dot
# there ("tib01.tem") gets truncated -> missing-texture placeholder. So no dot.
# Per-asset delivery mode:
#   "zip"   -> overlay-style: cropped TGA+meta packed into <NAME>.ZIP, frame ref
#             <stem>\<stem>-NNNN.tga. Works for OVERLAYS (TIB01).
#   "loose" -> Reilsss's terrain method: loose DDS in a <stem>.tem subfolder, frame
#             ref <stem>.tem\<stem>.tem-NNNN.tga. Required for TERRAIN OBJECTS
#             (SPLIT2 blossom tree) -- the zip path renders <Missing> for terrain.
ASSETS = [
    ("TIB01", "tib01", TD_TERRAIN_TEMP + r"\TI1", "TI1.TEM-{:04d}.DDS", 12, "zip"),
    # Blossom tree (TERRAIN_TDBLOSSOM, IniName SPLIT2) -- 55-frame bloom lifecycle.
    # DISABLED: HD custom *terrain* art isn't deliverable on our stack (loose ignored
    # for terrain, CONFIG.MEG inject crashes, mod texture-MEG not loaded). Re-enable
    # if a working terrain-art path is found. Keeps the loose-DDS code path intact.
    # ("SPLIT2", "split2", TD_TERRAIN_TEMP + r"\SPLIT2", "SPLIT2.TEM-{:04d}.DDS", 55, "loose"),
]
TERRAIN_TEX_DIR = MOD_ROOT / "Data/ART/TEXTURES/SRGB/RED_ALERT/TERRAIN/TEMPERATE"
TILESETS_DIR = MOD_ROOT / "Data/XML/TILESETS"
TILESET_XML = "RA_TERRAIN_TEMPERATE.XML"
TILESET_ENTRY_IN_MEG = r"DATA\XML\TILESETS\RA_TERRAIN_TEMPERATE.XML"


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def extract_from_meg(meg, entry, dest_dir):
    '''Extract one entry from a MEG via meg_extract.py CLI; return the file path.'''
    dest_dir.mkdir(parents=True, exist_ok=True)
    run([sys.executable, str(SCRIPT_DIR / "meg_extract.py"),
         "extract", str(meg), entry, str(dest_dir)])
    name = entry.split("\\")[-1]
    p = dest_dir / name
    if not p.exists():
        # meg_extract may preserve subdirs; search for the basename.
        hits = list(dest_dir.rglob(name))
        if not hits:
            raise FileNotFoundError(f"{entry} not extracted into {dest_dir}")
        p = hits[0]
    return p


def crop_to_opaque(im):
    '''Crop to the bounding box of non-fully-transparent pixels; return
    (cropped_image, meta) exactly like the launcher's structure assets do —
    meta = {size:[fullW,fullH], crop:[left,top,right,bottom]}. If the frame is
    fully opaque the crop is the whole frame.'''
    full_w, full_h = im.size
    bbox = im.getchannel("A").getbbox()  # bbox of non-zero alpha
    if bbox is None:                     # fully transparent frame
        bbox = (0, 0, full_w, full_h)
    cropped = im.crop(bbox)
    meta = {"size": [full_w, full_h], "crop": list(bbox)}
    return cropped, meta


def build_zip(name, stem, src_dir, src_frame, n_frames, work_dir):
    '''DDS -> cropped TGA(+meta) for all frames, packed into <name>.ZIP.'''
    TERRAIN_TEX_DIR.mkdir(parents=True, exist_ok=True)
    out_zip = TERRAIN_TEX_DIR / (name + ".ZIP")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in range(n_frames):
            dds = extract_from_meg(TD_TEX_MEG, f"{src_dir}\\{src_frame.format(i)}",
                                   work_dir)
            im = Image.open(dds).convert("RGBA")
            cropped, meta = crop_to_opaque(im)
            buf = io.BytesIO()
            cropped.save(buf, "TGA")
            fstem = f"{stem}-{i:04d}"
            zf.writestr(fstem + ".tga", buf.getvalue())
            zf.writestr(fstem + ".meta", json.dumps(meta))
    print(f"  wrote {out_zip} ({n_frames} frames)")
    return out_zip


def build_loose(name, stem, src_dir, src_frame, n_frames, work_dir):
    '''Reilsss terrain method: extract the source DDS frames LOOSE (no ZIP, no
    conversion) into <stem>.tem/<stem>.tem-NNNN.DDS under the temperate texture
    dir. Terrain objects resolve their art from these loose DDS at startup.'''
    out_dir = TERRAIN_TEX_DIR / f"{stem}.tem"
    out_dir.mkdir(parents=True, exist_ok=True)
    for i in range(n_frames):
        dds = extract_from_meg(TD_TEX_MEG, f"{src_dir}\\{src_frame.format(i)}",
                               work_dir)
        shutil.copyfile(dds, out_dir / f"{stem}.tem-{i:04d}.DDS")
    print(f"  wrote {out_dir}/ ({n_frames} loose DDS)")
    return out_dir


def tile_block(name, stem, shape, mode):
    '''One <Tile> entry, tab-indented to match base. Frame ref depends on mode:
    loose -> <stem>.tem\\<stem>.tem-NNNN.tga ; zip -> <stem>\\<stem>-NNNN.tga.'''
    if mode == "loose":
        frame = f"{stem}.tem\\{stem}.tem-{shape:04d}.tga"
    else:
        frame = f"{stem}\\{stem}-{shape:04d}.tga"
    return (
        "\t\t\t<Tile>\n"
        "\t\t\t\t<Key>\n"
        f"\t\t\t\t\t<Name>{name}</Name>\n"
        f"\t\t\t\t\t<Shape>{shape}</Shape>\n"
        "\t\t\t\t</Key>\n"
        "\t\t\t\t<Value>\n"
        "\t\t\t\t\t<Frames>\n"
        f"\t\t\t\t\t\t<Frame>{frame}</Frame>\n"
        "\t\t\t\t\t</Frames>\n"
        "\t\t\t\t</Value>\n"
        "\t\t\t</Tile>\n"
    )


def patch_tileset(work_dir):
    '''Extract base RA_TERRAIN_TEMPERATE.XML, inject all ASSETS' tiles, write to mod.'''
    base = extract_from_meg(CONFIG_MEG, TILESET_ENTRY_IN_MEG, work_dir / "xml")
    text = base.read_text(encoding="utf-8")
    blocks = ""
    for (name, stem, _src, _fmt, n_frames, mode) in ASSETS:
        blocks += "".join(tile_block(name, stem, s, mode) for s in range(n_frames))
    marker = "\t\t</Tiles>"
    if marker not in text:
        marker = "</Tiles>"
    text = text.replace(marker, blocks + marker, 1)
    TILESETS_DIR.mkdir(parents=True, exist_ok=True)
    out = TILESETS_DIR / TILESET_XML
    # Preserve CRLF line endings -- the base CONFIG.MEG XML is CRLF, and the
    # launcher's CONFIG.MEG XML parser CRASHES (ClientG AV) on LF-only content
    # when this tileset is injected into CONFIG.MEG. read_text() normalised the
    # base to LF, so re-emit as CRLF (binary write, no further normalisation).
    text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    out.write_bytes(text.encode("utf-8"))
    names = ", ".join(a[0] for a in ASSETS)
    print(f"  wrote {out} (+tiles for {names})")


def main():
    for p in (TD_TEX_MEG, CONFIG_MEG):
        if not p.exists():
            sys.exit(f"Source MEG not found: {p}\nSet CNC_REMASTER_DATA.")
    work = Path("/tmp/tib_hd_build")
    work.mkdir(parents=True, exist_ok=True)
    print("Building temperate terrain HD art...")
    for (name, stem, src_dir, src_frame, n_frames, mode) in ASSETS:
        if mode == "loose":
            build_loose(name, stem, src_dir, src_frame, n_frames, work)
        else:
            build_zip(name, stem, src_dir, src_frame, n_frames, work)
    patch_tileset(work)
    print("Done. Deploy the mod and run a skirmish to verify rendering.")


if __name__ == "__main__":
    main()
