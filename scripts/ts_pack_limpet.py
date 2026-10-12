#!/usr/bin/env python3
"""The sidebar side and sounds of the TS Limpet Drone (TSLIMP) and its mine (TSDLIMP):
BuildIcon_TS_LimpetDrone.tga (Firestorm ships no LIMPICON: the gold drone on TS's vehicle cameo
plate, rebuilt from the cameos that share it), the base RA_TSLIMP / RA_TSDLIMP sidebar entries, the
ModText rows and the five LIMP*.AUD sounds as TS<NAME>.WAV. Cameo, sidebar entries and sounds go
to the tree asset_packs.py routes each name to (the TS-Graphics-Pack and TS-SFX-Pack); the ModText
rows to the mod's own ModText.csv. The drone's and the mine's art is the HD rebuilds', packed by
scripts/ts_pack_hd_buildings.py.
Inputs (set TS_ART_DIR): .raw/LIMPED.SHP, UNITTEM.PAL and CAMEO.PAL, the vehicle cameo SHPs in
VEHICLE_CAMEOS, .raw/LIMP*.AUD.
License: GPL v3.
"""
import os
import subprocess
import sys
from PIL import Image
import hqx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_packs
import ts_pack_infantry as inf

ART = inf.ART
SOUNDS = ("LIMPBOM1", "LIMPQ3", "LIMPQ4", "LIMPC3", "LIMPC4")
VEHICLE_CAMEOS = ("SMCHICON", "SONIICON", "APCICON", "HARVICON", "MCVICON", "JUGGICON",
                  "OTRNICON", "SEEKICON")
CAMEO_FIT = 32   # the drone's height on the 48px plate: the fill TS's own vehicle cameos have


def cameo_plate():
    """TS's vehicle cameo backdrop, rebuilt from the cameos that share it: the darkest value
    at each pixel drops every vehicle off its plate, and what the pile of them leaves in the
    dark band is replaced with the quiet colour of its own row."""
    import ts_shp
    pal = ts_shp.load_pal(f"{ART}/.raw/CAMEO.PAL")
    plates = []
    for name in VEHICLE_CAMEOS:
        _, frames = ts_shp.decode_shp(f"{ART}/.raw/{name}.SHP")
        plates.append(ts_shp.frame_to_rgba(frames[0], pal).convert("RGB"))
    w, h = plates[0].size
    px = [p.load() for p in plates]
    plate = Image.new("RGB", (w, h))
    pp = plate.load()
    for y in range(h):
        for x in range(w):
            pp[x, y] = sorted((sum(p[x, y]), p[x, y]) for p in px)[0][1]
    for y in range(h):
        edge = sorted((pp[x, y] for x in list(range(0, w // 6)) + list(range(w - w // 6, w))), key=sum)
        quiet = edge[len(edge) // 2]
        for x in range(w):
            if sum(pp[x, y]) > sum(quiet) + 60 and (h * 0.18 < y < h * 0.74):
                pp[x, y] = quiet
    return plate.convert("RGBA")


def cameo():
    """No LIMPICON in Firestorm's archives: the drone in house gold, standing on TS's own
    vehicle cameo plate rebuilt from the cameos that share it. The sidebar builds the drone,
    so the drone is what the icon shows; it stands taller than it is wide and is fitted by
    height."""
    import ts_shp
    pal = ts_shp.load_pal(f"{ART}/.raw/UNITTEM.PAL")
    _, poses = ts_shp.decode_shp(f"{ART}/.raw/LIMPED.SHP")
    comp = ts_shp.frame_to_rgba(poses[0], pal, remap=(16, 31), team=(232, 190, 60))
    comp = comp.crop(comp.getbbox())
    rgb = Image.new("RGB", comp.size, (0, 0, 0))
    rgb.paste(comp, (0, 0), comp)
    big = hqx.hq4x(rgb).convert("RGBA")
    big.putalpha(comp.split()[3].resize((comp.width * 4, comp.height * 4), Image.LANCZOS))
    big = big.resize((round(big.width * CAMEO_FIT / big.height), CAMEO_FIT), Image.LANCZOS)
    back = cameo_plate()
    w, h = back.size
    back.alpha_composite(big, ((w - big.width) // 2, (h - big.height) // 2 + 3))
    os.makedirs(f"{ART}/shp_limpicon", exist_ok=True)
    back.save(f"{ART}/shp_limpicon/frame-0000.png")
    inf.cameo("limpicon", "BuildIcon_TS_LimpetDrone")


def sounds():
    for aud in SOUNDS:
        pcm = f"{ART}/.raw/{aud}.pcm.wav"
        subprocess.run([sys.executable, f"{HERE}/ts_aud_decode.py", f"{ART}/.raw/{aud}.AUD", pcm],
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pcm, "-c:a", "adpcm_ms",
                        "-ar", "22050", "-ac", "1", asset_packs.sound_wav(f"TS{aud}")], check=True)
        print(f"wrote TS{aud}.WAV")


def main():
    cameo()
    inf.sidebar("TSLIMP", "BuildIcon_TS_LimpetDrone")
    inf.text_rows("TSLIMP", "Limpet Drone",
                  "Unarmed hover drone. Deploys into a cloaked mine that latches onto the next enemy "
                  "vehicle, slowing it and revealing what it sees until it visits a repair bay.")
    inf.sidebar("TSDLIMP", "BuildIcon_TS_LimpetDrone", kind="STRUCTURE")
    inf.text_rows("TSDLIMP", "Limpet Mine",
                  "A settled Limpet Drone. Cloaked; leaps onto the next enemy vehicle to pass. "
                  "Deploy again to pick it up.", kind="STRUCTURE")
    sounds()


if __name__ == "__main__":
    main()
