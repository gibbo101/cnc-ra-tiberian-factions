#!/usr/bin/env python3
"""Package the TS aircraft (Orca Fighter, Orca Bomber, Carryall) into the mod tree:
  - UNITS/<INI>.ZIP: 32 voxel-render facings, model-space placement on a square canvas
    (canvas = ShapeSize x 8), no baked shadow: aircraft get the engine's air shadow.
  - BuildIcon_TS_<Name>.tga from the TS cameo (CAMEO.PAL, no remap), the base RA_<INI>
    entry in RABUILDABLES.XML's hand-written TS block, and the ModText rows.
Inputs (set TS_ART_DIR):
  $TS_ART_DIR/renders_orca|renders_orcab|renders_trnsport/frame-NNNN.png
      (scripts/vxl_render.py --frames 32 --yaw0 90 --px-per-voxel 12 --elev 32 --hva)
  $TS_ART_DIR/shp_orcaicon|shp_obmbicon|shp_otrnicon/frame-0000.png (ts_shp.py --no-remap)
Then: faction_masks.txt <INI> 16, cameo_badge_build.py <INI>, cameo_variants_build.py.
License: GPL v3.
"""
import os
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_pack_infantry as inf   # write_zip, patch_tileset, cameo, sidebar, text_rows

ART = inf.ART
UNITS_DIR = inf.UNITS_DIR
F_VOX = 6.4 / 12.0   # 12 px/voxel renders -> canvas px (the fleet factor)

# ini -> (render dir, canvas px, cameo stem, icon name, display name, description)
AIRCRAFT = {
    "TSORCA": ("renders_orca", 384, "orcaicon", "BuildIcon_TS_OrcaFighter", "Orca Fighter",
               "VTOL gunship. Fires Hellfire missiles at ground and air, and rearms at the TS Helipad."),
    "TSORCAB": ("renders_orcab", 384, "obmbicon", "BuildIcon_TS_OrcaBomber", "Orca Bomber",
                "Heavy VTOL bomber. Drops its bombs from over the target and rearms at the TS Helipad."),
    "TSCARRY": ("renders_trnsport", 448, "otrnicon", "BuildIcon_TS_Carryall", "Carryall",
                "Unarmed VTOL transport. Lifts one vehicle and sets it down where you send it."),
}


def vox_frames(dirname, canvas, count=32):
    """Model-space placement: each render canvas (centre = voxel origin) scaled by F_VOX and
    centred, so the launcher's canvas-centre anchor puts the model where the voxel data has it."""
    out = []
    for i in range(count):
        im = Image.open(f"{ART}/{dirname}/frame-{i:04d}.png").convert("RGBA")
        scaled = im.resize((round(im.width * F_VOX), round(im.height * F_VOX)), Image.LANCZOS)
        fr = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
        ox, oy = round(canvas / 2 - scaled.width / 2), round(canvas / 2 - scaled.height / 2)
        b = scaled.getbbox()
        if b and (ox + b[0] < 0 or oy + b[1] < 0 or ox + b[2] > canvas or oy + b[3] > canvas):
            raise SystemExit(f"{dirname}: frame {i} clips the {canvas} canvas; grow it")
        inf.safe_paste(fr, scaled, ox, oy)
        out.append(fr)
    return out


def face_fix(frames):
    """The renders start at NORTH and advance CCW, which is RA's frame order (0=N, 8=W, 16=S,
    24=E), so they ship as rendered. Checked against the shipped sheet in play: an eight-frame
    offset flew every aircraft 90 degrees off its nose."""
    return list(frames)


def pack(ini):
    dirname, canvas, cameo_stem, icon, display, desc = AIRCRAFT[ini]
    frames = face_fix(vox_frames(dirname, canvas))
    inf.write_zip(f"{UNITS_DIR}/{ini}.ZIP", ini.lower(), frames)
    inf.patch_tileset(ini, len(frames))
    inf.cameo(cameo_stem, icon)
    inf.sidebar(ini, icon)
    inf.text_rows(ini, display, desc)


if __name__ == "__main__":
    for ini in (sys.argv[1:] or list(AIRCRAFT)):
        pack(ini)
