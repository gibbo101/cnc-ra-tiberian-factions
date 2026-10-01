#!/usr/bin/env python3
"""Package the Firestorm Defense's field effects (docs/firestorm-design.md, stage D).

TS's [AudioVisual] anims, decoded against ANIM.PAL, scaled x4 like the other TS effects
(TS cell 48 px -> RA cell 192 canvas px), canvas = classic stub x 8 (build_tfassets.sh):

- TSFSIDLE.ZIP: FSIDLE, the crackling blue column over a live section (TS draws it 50%
  translucent; the alpha is baked in). It rises from the ground, so its base sits on the
  canvas centre, which is the anim's coordinate.
- TSFSGRND.ZIP: FSGRND, the sparks where something on the ground meets the field; base on
  the canvas centre.
- TSFSAIR.ZIP: FSAIR, the sparks where something in the air meets it; centred.

Frame 0 of each is empty in TS and is dropped, leaving 19. TS's anim palette paints a few
spark pixels in the remap greens; they are folded into the fire ramp so they never read as
house colour.

- AUDIO/TSFIRSTRM1.WAV: FIRSTRM1, "Firestorm defense burning", the Report= all three anims
  play, Westwood AUD -> MS-ADPCM WAV.

Anims, their TS_VFX.XML tile runs and the sound go to the tree asset_packs.py routes each
name to (the TS packs).

Inputs (set TS_ART_DIR): $TS_ART_DIR/.raw/{FSIDLE,FSGRND,FSAIR}.SHP, FIRSTRM1.AUD and ANIM.PAL
(TIBSUN.MIX conquer.mix / cache.mix via tools/ts_extract.py).

License: GPL v3.
"""
import os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_packs
import ts_shp
from ts_pack_ion import write_zip, patch_tileset, RAW, SCALE

# name, TS SHP, canvas (w, h), base on the canvas centre (True) or centred (False), alpha
ANIMS = (
    ("TSFSIDLE", "FSIDLE.SHP", (96, 1088), True, 0.5),
    ("TSFSGRND", "FSGRND.SHP", (96, 528), True, 1.0),
    ("TSFSAIR", "FSAIR.SHP", (96, 224), False, 1.0),
)


def unremap(im):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and g > r and g > b:
                px[x, y] = (g, round(g * 0.55), 0, a)
    return im


def main():
    pal = ts_shp.load_pal(f"{RAW}/ANIM.PAL")
    for name, shp, (cw, ch), base, alpha in ANIMS:
        (W, H), raw = ts_shp.decode_shp(f"{RAW}/{shp}")
        frames = []
        for f in raw[1:20]:
            im = unremap(ts_shp.frame_to_rgba(f, pal, remap=None))
            if alpha < 1.0:
                im.putalpha(im.split()[3].point(lambda v: round(v * alpha)))
            scaled = im.resize((round(W * SCALE), round(H * SCALE)), Image.LANCZOS)
            canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            ox = round(cw / 2 - scaled.width / 2)
            oy = (ch // 2 - scaled.height) if base else round(ch / 2 - scaled.height / 2)
            if ox < 0 or oy < 0:
                raise SystemExit(f"{name}: {scaled.size} does not fit the {cw}x{ch} canvas")
            canvas.alpha_composite(scaled, (ox, oy))
            frames.append(canvas)
        write_zip(asset_packs.art_zip(name, "VFX"), name.lower(), frames)
        patch_tileset(asset_packs.tileset_xml(name, "VFX"), name, len(frames))

    out_wav = asset_packs.sound_wav("TSFIRSTRM1")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{RAW}/FIRSTRM1.AUD",
                    "-acodec", "adpcm_ms", out_wav], check=True)
    print(f"wrote {out_wav}")


if __name__ == "__main__":
    main()
