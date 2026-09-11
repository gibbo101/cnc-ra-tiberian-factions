#!/usr/bin/env python3
"""Package the TS component tower weapon art and sound.

TS [VulcanTower] Anim=MGUN-N..MGUN-NW (one muzzle flash per facing). The tower
warheads pick their impact from AnimList in 25-point damage bands ([SA] PIFFPIFF,
[RPG] S_CLSN16-58, [SAMWH] XGRYSML1, XGRYSML2, EXPLOSML), and those anims carry
art.ini Report=EXPNEW14 (S_CLSN*) and EXPNEW13 (XGRYSML*, EXPLOSML). [Lobbed2]
flies Image=CANISTER; [AAHeatSeeker] flies Image=DRAGON with art.ini
Trailer=SMOKEY2. The reports are [VulcanTower] CHAINGN1, [RPGTower] GLNCH4 and
[RedEye2] SAMSHOT1.

Anims decode against ANIM.PAL, projectiles against UNITTEM.PAL (TS draws a bullet
with the unit palette unless it sets AnimPalette). Every frame is hq4x-upscaled
onto a canvas of the TS canvas x 4, rounded up to whole 8 px classic cells, so the
classic stub in build_tfassets.sh is canvas / 8. The summary this prints (frames,
stub, biggest frame) is what the stubs and the AnimTypeClass entries follow.

DRAGON's 32 frames run clockwise from north; the engine draws a rotating bullet
as BodyShape[Dir_To_32(facing)] = (32 - d) % 32, so frame k takes TS frame
(32 - k) % 32.

Sounds decode with ts_aud_decode.py (ffmpeg's own AUD reader errors at end of
file), then encode MS-ADPCM WAV, 22050 Hz mono, under their own
TS-prefixed names (the proven novel-name format).

Inputs (set TS_ART_DIR): $TS_ART_DIR/.raw/ from scripts/ts_rebuild_art.sh.

License: GPL v3.
"""
import os, subprocess, sys
from PIL import Image
import hqx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_shp
from ts_pack_pods import MOD, RAW, VFX_DIR, XML, write_zip, patch_tileset


def hq4x(im):
    big = hqx.hq4x(im.convert("RGB")).convert("RGBA")
    big.putalpha(im.split()[3].resize(big.size, Image.LANCZOS))
    return big


def canvas_dims(w, h):
    return (-(-w * 4 // 8) * 8, -(-h * 4 // 8) * 8)


def frames_of(shp, pal, drop_empty=False):
    (w, h), raw = ts_shp.decode_shp(f"{RAW}/{shp}")
    cw, ch = canvas_dims(w, h)
    out = []
    for f in raw:
        im = ts_shp.frame_to_rgba(f, pal, remap=None)
        if drop_empty and im.getbbox() is None:
            continue
        big = hq4x(im)
        c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        c.alpha_composite(big, ((cw - big.width) // 2, (ch - big.height) // 2))
        out.append(c)
    return out, (cw, ch)


def pack(shp, name, pal, drop_empty=False, order=None, count=None):
    frames, (cw, ch) = frames_of(shp, pal, drop_empty)
    if order is not None:
        frames = [frames[order(k, len(frames))] for k in range(count or len(frames))]
    write_zip(f"{VFX_DIR}/{name}.ZIP", name.lower(), frames)
    patch_tileset(XML, name, len(frames))
    biggest = max(range(len(frames)), key=lambda i: sum(1 for a in frames[i].getdata(3) if a >= 128))
    print(f"SUMMARY {name} frames={len(frames)} canvas={cw}x{ch} stub={cw // 8}x{ch // 8} biggest={biggest}")


def main():
    anim = ts_shp.load_pal(f"{RAW}/ANIM.PAL")
    unit = ts_shp.load_pal(f"{RAW}/UNITTEM.PAL")

    for d in ("N", "NE", "E", "SE", "S", "SW", "W", "NW"):
        pack(f"MGUN-{d}.SHP", f"TSMGUN{d}", anim, drop_empty=True)
    pack("PIFFPIFF.SHP", "TSPIFF", anim)
    for size in (16, 22, 30, 42, 58):
        pack(f"S_CLSN{size}.SHP", f"TSCLSN{size}", anim)
    pack("XGRYSML1.SHP", "TSXGRY1", anim)
    pack("XGRYSML2.SHP", "TSXGRY2", anim)
    pack("EXPLOSML.SHP", "TSEXPSML", anim)
    # SMOKEY2's edges use ANIM.PAL's cool blue-greys (195, 237, 239), which TS only ever
    # blends in at half strength; drawn opaque they read as purple specks. Grey them at
    # their own brightness so the puff keeps its edge.
    smoke = list(anim)
    for i in (195, 237, 239):
        r, g, b = smoke[i]
        y = round(0.299 * r + 0.587 * g + 0.114 * b)
        smoke[i] = (y, y, y)
    pack("SMOKEY2.SHP", "TSSMOKY2", smoke)

    # The canister tumbles through 15 frames, but it ships as a full 32-tile set (the
    # frames cycled round) so any shape index the launcher asks for has a tile.
    pack("CANISTER.SHP", "TSCANIST", unit, order=lambda k, n: k % n, count=32)
    pack("DRAGON.SHP", "TSDRAGON", unit, order=lambda k, n: (n - k) % n)

    for aud in ("CHAINGN1", "GLNCH4", "SAMSHOT1", "EXPNEW13", "EXPNEW14"):
        pcm = f"{RAW}/{aud}.pcm.wav"
        out_wav = f"{MOD}/AUDIO/TS{aud}.WAV"
        subprocess.run([sys.executable, f"{HERE}/ts_aud_decode.py", f"{RAW}/{aud}.AUD", pcm],
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pcm,
                        "-c:a", "adpcm_ms", "-ar", "22050", "-ac", "1", out_wav], check=True)
        print(f"wrote {out_wav}")


if __name__ == "__main__":
    main()
