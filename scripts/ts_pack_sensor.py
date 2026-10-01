#!/usr/bin/env python3
"""Package the TS Mobile Sensor Array ([LPST]) and the sensor it deploys into ([GADPSA]).

  TSLPST.ZIP (units)            32 frames: the LPST.VXL hull, one per facing, on a 384 canvas
                                (ShapeSize 48) at the TS voxel density 6.4/12 (ts_pack_memp.py).
  TSDPSA.ZIP (structures)       10 frames: the GTDPSA body under its GTDPSA_A beacon (5 healthy),
                                then the damaged body, which TS leaves unlit (5 damaged).
  TSDPSAMAKE.ZIP (structures)   19 frames: the GTDPSAMK build-up (36 TS frames resampled).
  BuildIcon_TS_SensorArray.tga, the base RA_TSLPST / RA_TSDPSA entries and the ModText rows.
Art, cameo, tiles and sidebar entries go to the tree asset_packs.py routes each name to (the
TS-Graphics-Pack); the ModText rows to the mod's own ModText.csv.

Scale: the building runs at the Limpet mine's F_BLDG (4.27 HD px per TS px, 0.8 classic px per
TS px, the same TS-relative size as the voxel units), so the sensor keeps its vehicle's size when
it deploys. Its canvas is 256 x 416 over a 48 x 78 classic stub (building density 5.33): the mast
rises about a cell above the plot, the radar's treatment. The base is seated on the vehicle's
ground line (contract 14 in docs/launcher-render-contracts.md): the lowest body pixel lands the
same distance below the cell centre as the packed vehicle's median lowest pixel.

Render (the voxel ledger in docs/launcher-render-contracts.md):
  vxl_render.py LPST.VXL renders_lpst --frames 32 --yaw0 90 --px-per-voxel 12
      --team-green 0,380,0 --elev 32 --hva LPST.HVA --canvas 720
(0,380,0: TS painted it in dark remap shades; the fleet's 0,200,0 read at half the APC's team colour)
Follow with scripts/ts_reshadow.py TSLPST, then the cameo badge and variant scripts.

Inputs (set TS_ART_DIR): renders_lpst, shp_gtdpsa, shp_gtdpsa_a, shp_gtdpsamk (ts_shp.py with
UNITTEM.PAL), .raw/LPSTICON.SHP and CAMEO.PAL (scripts/ts_rebuild_art.sh extracts them all).

License: GPL v3.
"""
import io
import json
import os
import statistics
import sys
import zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hqx
import asset_packs
import ts_shp
import ts_pack_infantry as inf
import ts_pack_limpet as limp
from ts_pack_memp import vox_frames, CANVAS as UNIT_CANVAS

ART = inf.ART
RAW = f"{ART}/.raw"
F_BLDG = limp.F_BLDG
BLDG_W, BLDG_H = 256, 416
BLDG_DENSITY = 256 / 48          # canvas px per classic px for buildings
UNIT_DENSITY = 8                 # canvas px per classic px for units
BODY_BOTTOM = 70                 # GTDPSA's lowest body pixel (TS px, frames 0-2)
BODY_CX = 48                     # the 96-wide SHP's centre column


def vehicle_ground_line(frames):
    """Median lowest opaque pixel below the canvas centre, in classic px."""
    lows = []
    for fr in frames:
        a = fr.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
        b = a.getbbox()
        lows.append((b[3] - UNIT_CANVAS / 2) / UNIT_DENSITY)
    return statistics.median(lows)


def crisp_tall(img, anchor):
    """hq4x then LANCZOS to F_BLDG; the anchor (source px) lands on the canvas centre."""
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    big = hqx.hq4x(rgb).convert("RGBA")
    big.putalpha(img.split()[3].resize((img.width * 4, img.height * 4), Image.LANCZOS))
    scaled = big.resize((round(img.width * F_BLDG), round(img.height * F_BLDG)), Image.LANCZOS)
    out = Image.new("RGBA", (BLDG_W, BLDG_H), (0, 0, 0, 0))
    x, y = round(BLDG_W / 2 - anchor[0] * F_BLDG), round(BLDG_H / 2 - anchor[1] * F_BLDG)
    b = scaled.getbbox()
    if b and (x + b[0] < 0 or y + b[1] < 0 or x + b[2] > BLDG_W or y + b[3] > BLDG_H):
        raise SystemExit("sensor art clipped -- grow the canvas")
    inf.safe_paste(out, scaled, x, y)
    return out


def sensor_frames(anchor):
    out = []
    for pose in (0, 1):
        base = inf.with_shadow(limp.frame("gtdpsa", pose), limp.frame("gtdpsa", 3 + pose))
        for b in range(5):
            comp = base.copy()
            if pose == 0:
                comp.alpha_composite(limp.frame("gtdpsa_a", b))
            out.append(crisp_tall(comp, anchor))
    return out


def make_frames(anchor, count=19):
    total = 36
    picks = [round(i * (total - 1) / (count - 1)) for i in range(count)]
    return [crisp_tall(inf.with_shadow(limp.frame("gtdpsamk", i), limp.frame("gtdpsamk", total + i)), anchor)
            for i in picks]


def cameo():
    pal = ts_shp.load_pal(f"{RAW}/CAMEO.PAL")
    (_, _), raw = ts_shp.decode_shp(f"{RAW}/LPSTICON.SHP")
    icon = ts_shp.frame_to_rgba(raw[0], pal, remap=None)
    flat = Image.new("RGBA", icon.size, (0, 0, 0, 255))
    flat.alpha_composite(icon)
    big = flat.resize((flat.width * 8, flat.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    path = asset_packs.cameo_tga("BuildIcon_TS_SensorArray")
    big.save(path)
    print(f"wrote {path}")


def main():
    unit = vox_frames("renders_lpst")
    inf.write_zip(asset_packs.art_zip("TSLPST", "UNITS"), "tslpst", unit)
    inf.patch_tileset("TSLPST", len(unit))

    ground = vehicle_ground_line(unit)
    anchor = (BODY_CX, BODY_BOTTOM - ground * BLDG_DENSITY / F_BLDG)
    print(f"vehicle ground line {ground:.1f} classic px below centre -> building anchor {anchor[1]:.1f}")
    sensor = sensor_frames(anchor)
    inf.write_zip(asset_packs.art_zip("TSDPSA", "STRUCTURES"), "tsdpsa", sensor)
    limp.patch_struct_tileset("TSDPSA", len(sensor))
    make = make_frames(anchor)
    inf.write_zip(asset_packs.art_zip("TSDPSAMAKE", "STRUCTURES"), "tsdpsamake", make)
    limp.patch_struct_tileset("TSDPSAMAKE", len(make))

    cameo()
    inf.sidebar("TSLPST", "BuildIcon_TS_SensorArray")
    inf.text_rows("TSLPST", "Mobile Sensor Array",
                  "Unarmed support vehicle. Deploys into a sensor that shows you cloaked and "
                  "underground enemies nearby. Deploy again to move it.")
    limp.sidebar_building("TSDPSA", "BuildIcon_TS_SensorArray")
    limp.text_rows_building("TSDPSA", "Sensor Array",
                            "A deployed Mobile Sensor Array. Shows you cloaked and underground "
                            "enemies nearby. Deploy again to pack it up.")


if __name__ == "__main__":
    main()
