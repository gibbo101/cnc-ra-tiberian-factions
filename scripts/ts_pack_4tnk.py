#!/usr/bin/env python3
"""Package the old TS Mammoth Tank (TS [4TNK], TechLevel -1 in TS) as TS4TNK.

TS4TNK.ZIP is 64 frames: hull 0-31 + turret 32-63 (the TSSONIC layout), on a 448
canvas (ShapeSize 56), each render scaled by the TS voxel density 6.4/12 around the
voxel origin at the canvas centre (the vox_frames recipe in ts_pack_units_wave.py).
The turret renders carry the barrel in the same depth-sorted pass (vxl_render.py
--attach), so it hides and is hidden correctly at every facing. Also writes the
RA_UNITS.XML tile run and the cannon + tusk reports under their own names.

Renders (the voxel ledger in docs/launcher-render-contracts.md, one canvas for both):
  vxl_render.py 4TNK.VXL    renders_4tnk    --frames 32 --yaw0 90 --px-per-voxel 12
      --team-green 0,105,0 --elev 32 --hva 4TNK.HVA --canvas 720
  vxl_render.py 4TNKTUR.VXL renders_4tnktur (same) --hva 4TNKTUR.HVA
      --attach 4TNKBARL.VXL --attach-hva 4TNKBARL.HVA
TS painted 77% of this hull in remap (the Disruptor: 24%), so at the fleet's 0,200,0 its
team colour reads far louder than the rest; 0,105,0 puts its team pixels at the Wolverine's
median brightness (0.50 vs 0.49). The all-team look is TS's own and was kept (Luke,
2026-09-12, over ochre-hull, cameo-gold and team-accent alternatives).
Follow with scripts/ts_reshadow.py TS4TNK.

Inputs (set TS_ART_DIR): $TS_ART_DIR/renders_4tnk*, $TS_ART_DIR/.raw/{120MMX9,MISL1}.AUD.

License: GPL v3.
"""
import os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ts_pack_pods import ART, MOD, RAW, write_zip, patch_tileset

UNITS_DIR = f"{MOD}/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
UNITS_XML = f"{MOD}/XML/TILESETS/RA_UNITS.XML"
CANVAS = 448
F_VOX = 6.4 / 12
def vox_frames(dirname):
    out = []
    for i in range(32):
        im = Image.open(f"{ART}/{dirname}/frame-{i:04d}.png").convert("RGBA")
        scaled = im.resize((round(im.width * F_VOX), round(im.height * F_VOX)), Image.LANCZOS)
        fr = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        ox, oy = round(CANVAS / 2 - scaled.width / 2), round(CANVAS / 2 - scaled.height / 2)
        b = scaled.getbbox()
        if b and (ox + b[0] < 0 or oy + b[1] < 0 or ox + b[2] > CANVAS or oy + b[3] > CANVAS):
            raise SystemExit(f"{dirname} frame {i}: content clipped -- grow the canvas")
        fr.alpha_composite(scaled, (max(ox, 0), max(oy, 0)))
        out.append(fr)
    return out


def main():
    frames = vox_frames("renders_4tnk") + vox_frames("renders_4tnktur")
    write_zip(f"{UNITS_DIR}/TS4TNK.ZIP", "ts4tnk", frames)
    patch_tileset(UNITS_XML, "TS4TNK", len(frames))
    for aud in ("120MMX9", "MISL1"):
        pcm = f"{RAW}/{aud}.pcm.wav"
        out_wav = f"{MOD}/AUDIO/TS{aud}.WAV"
        subprocess.run([sys.executable, f"{HERE}/ts_aud_decode.py", f"{RAW}/{aud}.AUD", pcm],
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pcm,
                        "-c:a", "adpcm_ms", "-ar", "22050", "-ac", "1", out_wav], check=True)
        print(f"wrote {out_wav}")


if __name__ == "__main__":
    main()
