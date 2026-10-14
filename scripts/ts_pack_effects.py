#!/usr/bin/env python3
"""Package the TS effects the other TS packers leave out: deaths, debris, the bigger warhead impacts, fires,
infantry deaths, water splashes, the Firestorm overlay and the missile and shell in flight.

  Vehicle, aircraft and building deaths: TS [<unit>] Explosion=TWLT070,S_BANG48,S_BRNL58,S_CLSN58,S_TUMU60,
    picked at random (S_CLSN58 ships with ts_pack_towerfx.py as TSCLSN58).
  Debris: [General] MetallicDebris=DBRIS1LG..DBRS10SM, each a bouncing 15-frame tumble. The large ones burst as
    TWLT036; the small ones' TWLT024 is in none of TS's archives.
  Warhead impacts: [HE]/[ARTYHE] AnimList adds XGRYMED1, XGRYMED2, EXPLOMED, EXPLOLRG to the SAM set;
    [ORCAHE] is EXPLOMED, EXPLOLRG.
  Fires: [AudioVisual] OnFire=FIRE3,FIRE2,FIRE1 (art.ini FIRE1 Next=FIRE2, FIRE2 Next=FIRE3).
  Infantry: DeadBodies=DEATH_A..DEATH_F, FlamingInfantry=FLAMEGUY (InfDeath=4; the unit palette, its second half
    is the first half's shadows), ELECTRO (InfDeath=5).
  Water: SplashList=H2O_EXP3,H2O_EXP2,H2O_EXP1 (art.ini AltPalette=yes: the unit palette).
  Firestorm: FirestormActiveAnim=GAFSDF_A, temperate GTFSDF_A (NewTheater, the unit palette).
  In flight: [DRAGON] (32 facings, Trailer=SMOKEY2) and [120MM], against the unit palette as TS draws bullets.
  Damage: DamageParticleSystems=SparkSys,SmallGreySSys. SmallGreySmoke's SGRYSMK1 at TS's Translucency=25; TS
    draws sparks as pixels, so TSSPARKS renders a [SparkSys] burst from [Spark]'s velocities and ColorList.
  Reports: EXPNEW06/09/10/11/12/15, ELECTRO1, SSPLASH1-3, under TS-prefixed names.

Firestorm's DROPPODY and DROPPODY2 are byte-identical to DROPPOD and DROPPOD2 (TSDPOD1/2, ts_pack_pods.py).
Inputs (set TS_ART_DIR): $TS_ART_DIR/.raw/ from scripts/ts_rebuild_art.sh. Every anim upscales as
ts_pack_towerfx.py does (hq4x onto the TS canvas x 4, whole 8 px cells), so its classic stub is canvas / 8.
License: GPL v3.
"""
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_packs  # noqa: E402
import ts_shp  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
from ts_pack_pods import RAW, patch_tileset, write_zip  # noqa: E402
from ts_pack_towerfx import canvas_dims, frames_of, hq4x, pack  # noqa: E402

# TS art -> (our name, palette)
ANIMS = [
    ("TWLT070", "TSTWLT70", "anim"), ("TWLT036", "TSTWLT36", "anim"), ("S_BANG48", "TSBANG48", "anim"),
    ("S_BRNL58", "TSBRNL58", "anim"), ("S_TUMU60", "TSTUMU60", "anim"),
    ("XGRYMED1", "TSXGRYM1", "anim"), ("XGRYMED2", "TSXGRYM2", "anim"), ("EXPLOMED", "TSEXPMED", "anim"),
    ("EXPLOLRG", "TSEXPLRG", "anim"),
    ("FIRE1", "TSFIRE1", "anim"), ("FIRE2", "TSFIRE2", "anim"), ("FIRE3", "TSFIRE3", "anim"),
    *[(f"DEATH_{c}", f"TSDEATH{c}", "anim") for c in "ABCDEF"],
    ("ELECTRO", "TSELECTR", "anim"),
    ("H2O_EXP1", "TSH2O1", "unit"), ("H2O_EXP2", "TSH2O2", "unit"), ("H2O_EXP3", "TSH2O3", "unit"),
    ("GTFSDF_A", "TSFSDFA", "unit"),
    ("DRAGON", "TSDRAGON", "unit"), ("120MM", "TS120MM", "unit"),
    *[(f"DBRIS{i}LG" if i < 10 else "DBRS10LG", f"TSDBR{i:02d}L", "anim") for i in range(1, 11)],
    *[(f"DBRIS{i}SM" if i < 10 else "DBRS10SM", f"TSDBR{i:02d}S", "anim") for i in range(1, 11)],
]
SOUNDS = ("EXPNEW06", "EXPNEW09", "EXPNEW10", "EXPNEW11", "EXPNEW12", "EXPNEW15", "ELECTRO1",
          "SSPLASH1", "SSPLASH2", "SSPLASH3")


def pack_shadowed(shp, name, pal):
    """An anim whose second half holds the first half's shadows: each body frame over its shadow at half strength."""
    (w, h), raw = ts_shp.decode_shp(f"{RAW}/{shp}")
    half = len(raw) // 2
    cw, ch = canvas_dims(w, h)
    frames = []
    for body, shadow in zip(raw[:half], raw[half:]):
        mask = ts_shp.frame_to_rgba(shadow, pal, remap=None).getchannel("A").point(lambda a: 128 if a else 0)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        im.putalpha(mask)
        im.alpha_composite(ts_shp.frame_to_rgba(body, pal, remap=None))
        big = hq4x(im)
        c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        c.alpha_composite(big, ((cw - big.width) // 2, (ch - big.height) // 2))
        frames.append(c)
    write_zip(asset_packs.art_zip(name, "VFX"), name.lower(), frames)
    patch_tileset(asset_packs.tileset_xml(name, "VFX"), name, len(frames))
    print(f"SUMMARY {name} frames={len(frames)} canvas={cw}x{ch} stub={cw // 8}x{ch // 8}")


def pack_translucent(shp, name, pal, opacity):
    """An anim drawn see-through in TS (Translucency=), its alpha scaled to match."""
    frames, (cw, ch) = frames_of(shp, pal)
    for f in frames:
        f.putalpha(f.getchannel("A").point(lambda a: int(a * opacity)))
    write_zip(asset_packs.art_zip(name, "VFX"), name.lower(), frames)
    patch_tileset(asset_packs.tileset_xml(name, "VFX"), name, len(frames))
    print(f"SUMMARY {name} frames={len(frames)} canvas={cw}x{ch} stub={cw // 8}x{ch // 8}")


# TS [Spark]: XVelocity=10, YVelocity=10, MinZVelocity=40, ZVelocityRange=15, ColorSpeed=.13 (+0-.05 a tick),
# ColorList white, yellow, red, black; [SparkSys] ParticleCap=12; [General] Gravity=6.
SPARK_COLOURS = [(255, 255, 255), (200, 200, 80), (200, 10, 10), (0, 0, 0)]
SPARK_FRAMES = 20
LEPTON_TS_PX = 48 / 256


def render_sparks(name):
    """A [SparkSys] burst as frames: 12 sparks thrown from the frame centre two a tick, each falling under TS
    gravity back to its start height and fading through TS's ColorList."""
    rng = random.Random(1213210)
    w, h = 80, 80
    sparks = []
    for i in range(12):
        sparks.append(dict(t0=i // 2, vx=rng.uniform(-10, 10), vy=rng.uniform(-10, 10),
                           vz=40 + rng.uniform(0, 15), speed=0.13 + rng.uniform(0, 0.05)))
    frames = []
    for t in range(SPARK_FRAMES):
        im = Image.new("RGBA", (w * 4, h * 4), (0, 0, 0, 0))
        glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d, g = ImageDraw.Draw(im), ImageDraw.Draw(glow)
        for s in sparks:
            age = t - s["t0"]
            if age < 0:
                continue
            x, y, z, vz = 0.0, 0.0, 0.0, s["vz"]
            for _ in range(age + 1):
                vz -= 6
                x, y, z = x + s["vx"], y + s["vy"], z + vz
            if z < 0:
                continue
            ci = min(age * s["speed"], len(SPARK_COLOURS) - 1.001)
            a, b = SPARK_COLOURS[int(ci)], SPARK_COLOURS[int(ci) + 1]
            f = ci - int(ci)
            col = tuple(int(a[k] + (b[k] - a[k]) * f) for k in range(3))
            px = (w / 2 + x * LEPTON_TS_PX) * 4
            py = (h / 2 + (y - z) * LEPTON_TS_PX) * 4
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col + (255,))
            g.ellipse([px - 6, py - 6, px + 6, py + 6], fill=col + (110,))
        out = glow.filter(ImageFilter.GaussianBlur(3))
        out.alpha_composite(im)
        frames.append(out)
    write_zip(asset_packs.art_zip(name, "VFX"), name.lower(), frames)
    patch_tileset(asset_packs.tileset_xml(name, "VFX"), name, len(frames))
    print(f"SUMMARY {name} frames={len(frames)} canvas={w * 4}x{h * 4} stub={w // 2}x{h // 2}")


def main(only):
    pals = {"anim": ts_shp.load_pal(f"{RAW}/ANIM.PAL"), "unit": ts_shp.load_pal(f"{RAW}/UNITTEM.PAL")}
    for shp, name, pal in ANIMS:
        if not only or name in only:
            pack(f"{shp}.SHP", name, pals[pal])
    if not only or "TSFLMGUY" in only:
        pack_shadowed("FLAMEGUY.SHP", "TSFLMGUY", pals["unit"])
    if not only or "TSSGRYSM" in only:
        pack_translucent("SGRYSMK1.SHP", "TSSGRYSM", pals["anim"], 0.75)
    if not only or "TSSPARKS" in only:
        render_sparks("TSSPARKS")
    for aud in SOUNDS:
        if only and f"TS{aud}" not in only:
            continue
        pcm = f"{RAW}/{aud}.pcm.wav"
        out_wav = asset_packs.sound_wav(f"TS{aud}")
        subprocess.run([sys.executable, f"{HERE}/ts_aud_decode.py", f"{RAW}/{aud}.AUD", pcm],
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pcm,
                        "-c:a", "adpcm_ms", "-ar", "22050", "-ac", "1", out_wav], check=True)
        print(f"wrote {out_wav}")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
