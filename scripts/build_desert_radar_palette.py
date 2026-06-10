#!/usr/bin/env python3
r"""
Desert radar palette (Tiberian Factions mod).

TD desert maps live in RA's INTERIOR theatre slot. The launcher's radar (and
the static ground under our dynamic TD tiles) renders the per-cell stand-in
templates reported by CellClass::Get_Template_Info -- and the 2026-06-10 W1
spike PROVED the radar samples loose path-shadowed pixels (Reilsss mechanism,
no EMC). Interior has no outdoor templates to stand in with, so we sacrifice
interior art (nothing multiplayer uses interior; only stock-campaign indoor
missions + the final ant mission render with it):

  - CLEAR1.INT (16 frames)  -> TD desert sand        (radar class 'C' + the
                               static layer under every TD cell)
  - ARRO0001.INT (6 frames) -> TD desert water       ('W')
  - ARRO0002.INT (6 frames) -> TD desert pavement    ('B' bright coast/sand)
  - ARRO0003.INT (6 frames) -> TD desert water       ('R' river -- desert
                               rivers carry water; refine later if it reads
                               poorly)

cell.cpp's interior branch reports these per the TF_TdTileRadarClass row, so
the desert minimap shows sand ground + blue water + bright coastlines at cell
resolution. The overrides ship in the mod's loose Data/ART tree and shadow
the base TEXTURES_RA_SRGB.MEG entries by exact path.

Usage: python3 scripts/build_desert_radar_palette.py
"""
import os, re, shutil, sys, tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_tiberium_hd import extract_from_meg, TD_TEX_MEG, TD_TERRAIN, GAME_DATA, MOD_ROOT

RA_TEX_MEG = GAME_DATA / "TEXTURES_RA_SRGB.MEG"
RA_INTERIOR = r"DATA\ART\TEXTURES\SRGB\RED_ALERT\TERRAIN\INTERIOR"
OUT_ROOT = MOD_ROOT / "Data/ART/TEXTURES/SRGB/RED_ALERT/TERRAIN/INTERIOR"

# (RA interior victim, TD desert source template, per-frame source mapping)
# mapping "1:1"   = victim frame i <- source icon i (CLEAR1: same 16-icon
#                   positional convention in both games)
# mapping "first" = every victim frame <- source icon 0
PALETTE = [
    ("CLEAR1", "CLEAR1", "1:1"),
    ("ARRO0001", "W1", "first"),    # 'W' water
    ("ARRO0002", "P01", "first"),   # 'B' bright coast/sand (bleached pavement)
    ("ARRO0003", "W1", "first"),    # 'R' river water
    # 'K' rock/cliff: S03 icon 3 = the darkest fully-opaque desert rock face
    # (brightness 63 vs sand ~120; the B1 boulder at 90 was too low-contrast
    # to read on the minimap).
    ("ARRO0004", "S03:3", "first"),
    # NOTE: no BIB rows here -- bibs aren't path-shadows (interior has no base
    # bib art to shadow); they're ADDED assets: build_tiberium_hd ships BIB*
    # HD tiles into the interior tileset XML and build_tfassets stages the
    # classic .INT iconsets that make the engine emit the smudge entries.
]


def ra_frames(listing, victim):
    pat = re.compile(re.escape(RA_INTERIOR) + r"\\" + re.escape(victim)
                     + r"\.INT\\" + re.escape(victim) + r"\.INT-(\d+)\.DDS", re.I)
    out = {}
    for line in listing:
        m = pat.search(line)
        if m:
            out[int(m.group(1))] = line.strip().split(None, 1)[1]
    return out


def td_desert_dds(src, icon, work):
    sub = f"{src}.DES"
    # desert frames may be plain (NAME.DES-0000.DDS) or animated
    # (NAME.DES-0000-0000.DDS); prefer the plain frame, else anim frame 0.
    for suffix in (f"{src}.DES-{icon:04d}.DDS", f"{src}.DES-{icon:04d}-0000.DDS",
                   f"{src}.DES-{icon:04d}-00.DDS"):
        try:
            return extract_from_meg(TD_TEX_MEG, f"{TD_TERRAIN}\\DESERT\\{sub}\\{suffix}", work)
        except Exception:
            continue
    raise SystemExit(f"no desert DDS found for {src} icon {icon}")


def main():
    import subprocess
    listing = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "meg_extract.py"),
         "list", str(RA_TEX_MEG)], capture_output=True, text=True).stdout.split("\n")
    work = Path(tempfile.mkdtemp())
    for victim, src, mapping in PALETTE:
        frames = ra_frames(listing, victim)
        if not frames:
            raise SystemExit(f"no base frames found for {victim}.INT")
        out_dir = OUT_ROOT / f"{victim}.INT"
        out_dir.mkdir(parents=True, exist_ok=True)
        # "NAME:N" pins the source icon for "first"-mapped palette tiles
        src_icon = 0
        if ":" in src:
            src, src_icon = src.split(":")[0], int(src.split(":")[1])
        for i in sorted(frames):
            icon = i if mapping == "1:1" else src_icon
            dds = td_desert_dds(src, icon, work)
            shutil.copyfile(dds, out_dir / f"{victim}.INT-{i:04d}.DDS")
        print(f"  {victim}.INT <- desert {src} ({len(frames)} frames, {mapping})")
    print(f"palette written under {OUT_ROOT}")


if __name__ == "__main__":
    main()
