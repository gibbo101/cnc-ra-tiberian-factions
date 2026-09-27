#!/usr/bin/env python3
"""Package the TS EMP Pulse Cannon special's art: the pulse ball, its impact rings, and the
special's sidebar cameo (docs/emp-cannon-design.md, stage B).

TS fires the cannon's special as a PULSBALL: the ball glows at the barrel for 32 frames, then
flies as the projectile [PulsPr] (Image=PULSBALL, High, Lobber) to the target, where the
[EMPuls] warhead's AnimList plays PULSEFX1 then PULSEFX2 (OpenTS building.cpp Mission_Missile,
bullet.cpp Detonate). All decoded against ANIM.PAL with no team remap, scaled x4 (TS cell
48 px -> RA cell 192 canvas px, as ts_pack_ion.py), canvas = classic stub x 8
(build_tfassets.sh: TSPULSBL 8x8, TSPULSF1 / TSPULSF2 152x88, TSEMPFX 20x18).

- TSPULSBL.ZIP: PULSBALL's 23 frames. One tileset serves both the charge-up anim at the
  barrel and the projectile (rules.ini [TSPulsBall] Image=TSPULSBL, Frames=23).
- TSPULSF1.ZIP / TSPULSF2.ZIP: PULSEFX1 (21 frames) and PULSEFX2 (15 frames), centred.
- TSEMPFX.ZIP: EMP_FX01's 27 frames, the sparks over a stunned object.
- BuildIcon_SW_TSEMP.tga: TS's PULSICON special cameo (CAMEO.PAL), flattened opaque (the
  launcher draws noise under transparent cameo pixels).
- Data/AUDIO/TSPLSECAN2.WAV: the cannon's report ([EMPulseWeapon] Report=PLSECAN2) under its
  own sample name, Westwood AUD -> MS-ADPCM WAV.

Inputs (set TS_ART_DIR): $TS_ART_DIR/.raw/{PULSBALL,PULSEFX1,PULSEFX2,PULSICON,EMP_FX01}.SHP,
PLSECAN2.AUD, ANIM.PAL, CAMEO.PAL -- TIBSUN.MIX conquer.mix / cache.mix via tools/ts_extract.py.

License: GPL v3.
"""
import os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_shp
from ts_pack_ion import write_zip, patch_tileset, MOD, VFX_DIR, ICON_DIR, XML, RAW, SCALE

# name, TS SHP, canvas (w, h)
ANIMS = (
    ("TSPULSBL", "PULSBALL.SHP", (64, 64)),
    ("TSPULSF1", "PULSEFX1.SHP", (1216, 704)),
    ("TSPULSF2", "PULSEFX2.SHP", (1216, 704)),
    ("TSEMPFX", "EMP_FX01.SHP", (160, 144)),
)


def main():
    anim_pal = ts_shp.load_pal(f"{RAW}/ANIM.PAL")
    for name, shp, (cw, ch) in ANIMS:
        (W, H), raw = ts_shp.decode_shp(f"{RAW}/{shp}")
        frames = []
        for f in raw:
            im = ts_shp.frame_to_rgba(f, anim_pal, remap=None)
            scaled = im.resize((round(W * SCALE), round(H * SCALE)), Image.LANCZOS)
            canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            ox, oy = round(cw / 2 - scaled.width / 2), round(ch / 2 - scaled.height / 2)
            if ox < 0 or oy < 0:
                raise SystemExit(f"{name}: {scaled.size} does not fit the {cw}x{ch} canvas")
            canvas.alpha_composite(scaled, (ox, oy))
            frames.append(canvas)
        write_zip(f"{VFX_DIR}/{name}.ZIP", name.lower(), frames)
        patch_tileset(XML, name, len(frames))

    cameo_pal = ts_shp.load_pal(f"{RAW}/CAMEO.PAL")
    (_, _), raw = ts_shp.decode_shp(f"{RAW}/PULSICON.SHP")
    icon = ts_shp.frame_to_rgba(raw[0], cameo_pal, remap=None)
    flat = Image.new("RGBA", icon.size, (0, 0, 0, 255))
    flat.alpha_composite(icon)
    big = flat.resize((flat.width * 8, flat.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(f"{ICON_DIR}/BuildIcon_SW_TSEMP.tga")
    print(f"wrote {ICON_DIR}/BuildIcon_SW_TSEMP.tga")

    out_wav = f"{MOD}/AUDIO/TSPLSECAN2.WAV"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{RAW}/PLSECAN2.AUD",
                    "-acodec", "adpcm_ms", out_wav], check=True)
    print(f"wrote {out_wav}")


if __name__ == "__main__":
    main()
