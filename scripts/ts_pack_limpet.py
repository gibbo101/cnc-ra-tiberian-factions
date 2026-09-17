#!/usr/bin/env python3
"""Package the TS Limpet Drone (Firestorm) into the mod tree:
  TSLIMP.ZIP (units)            10 frames: the LIMPED.SHP crawl cycle with its own shadows,
                                no facings (unit.cpp Shape_Number cycles them by frame)
  TSDLIMP.ZIP (structures)      20 frames: DLIMPET body (healthy / damaged) under the
                                DLIMP_A blink, 10 healthy then 10 damaged
  TSDLIMPMAKE.ZIP (structures)  19 frames: the DLIMPMK build-up (42 TS frames resampled)
plus BuildIcon_TS_LimpetDrone.tga (Firestorm ships no LIMPICON: the gold drone on TS's
vehicle cameo plate, rebuilt from the cameos that share it), the base RA_TSLIMP / RA_TSDLIMP sidebar entries, the ModText rows and the
five LIMP*.AUD sounds as Data/AUDIO/TS<NAME>.WAV.
Scale: the drone runs at the mod-wide TS SHP factor F_UNIT (hq4x then LANCZOS) on a 192
canvas (ShapeSize 24 x 8, the unit density); the mine and its build-up run at F_BLDG on 256
canvases over a 48x48 classic stub, the building density being 5.33x rather than 8x, so both
states come out the same TS-relative size on screen. TS draws the hover drone well above its
shadow, so the body is dropped to a short hover and the pair centred. TS source (48,48), the
mine's centre, lands on the canvas centre for the mine and its build-up alike, so the ladder
ends where the mine sits.
Inputs (set TS_ART_DIR): shp_limped, shp_dlimpet, shp_dlimp_a, shp_dlimpmk (ts_shp.py with
UNITTEM.PAL), shp_xxicon (CAMEO.PAL, --no-remap), .raw/LIMP*.AUD.
License: GPL v3.
"""
import os
import subprocess
import sys
from PIL import Image, ImageFilter
import hqx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_pack_infantry as inf

ART = inf.ART
MOD = inf.MOD
STRUCT_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES"
STRUCT_XML = f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML"
RAB = f"{MOD}/Data/XML/OBJECTS/UNITS/RABUILDABLES.XML"
F_UNIT = 6.4              # the mod-wide TS SHP factor (ts_pack_units_wave.py), at 8x-classic unit density
F_BLDG = F_UNIT * 2.0 / 3.0  # buildings ship at 5.33x-classic, so their art scales by 2/3 to match on screen
UNIT_CANVAS = 192
BLDG_CANVAS = 256
HOVER_DROP = 0    # TS px the airborne LIMPED body comes down toward its shadow: none, TS draws it hovering two px clear
# The mine's base lands where the drone's shadow does, 11.6 classic px below the cell centre,
# which is also where TS's other 1x1 buildings sit (TSPION +12, TSSEEK +10.3, TSPODS +9.4).
# Anything higher and the mine jumps north of the drone the moment it deploys.
BLDG_DROP = 31.0                                  # canvas px the mine and its build-up come down
BLDG_ANCHOR = (48, 48 - BLDG_DROP / F_BLDG)
SOUNDS = ("LIMPBOM1", "LIMPQ3", "LIMPQ4", "LIMPC3", "LIMPC4")


def frame(stem, i):
    return Image.open(f"{ART}/shp_{stem}/frame-{i:04d}.png").convert("RGBA")


def crisp(img, canvas, anchor=None, factor=None):
    """hq4x then LANCZOS to the given factor. The anchor (source px) lands on the canvas
    centre; by default the centre of the image's opaque bounding box."""
    if factor is None:
        factor = F_UNIT
    if anchor is None:
        b = img.getbbox()
        anchor = ((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0)
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    big = hqx.hq4x(rgb).convert("RGBA")
    big.putalpha(img.split()[3].resize((img.width * 4, img.height * 4), Image.LANCZOS))
    scaled = big.resize((round(img.width * factor), round(img.height * factor)), Image.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    inf.safe_paste(out, scaled, round(canvas / 2 - anchor[0] * factor), round(canvas / 2 - anchor[1] * factor))
    return out


def drone_frames():
    # LIMPED.SHP: 10 poses then their 10 shadows. Every frame shares one anchor so the
    # crawl cycle does not wander: the union box of the dropped bodies and shadows.
    pairs = []
    for i in range(10):
        body = frame("limped", i)
        dropped = Image.new("RGBA", body.size, (0, 0, 0, 0))
        dropped.alpha_composite(body, (0, HOVER_DROP))
        pairs.append(inf.with_shadow(dropped, frame("limped", 10 + i)))
    boxes = [p.getbbox() for p in pairs]
    anchor = ((min(b[0] for b in boxes) + max(b[2] for b in boxes)) / 2.0,
              (min(b[1] for b in boxes) + max(b[3] for b in boxes)) / 2.0)
    return [crisp(p, UNIT_CANVAS, anchor) for p in pairs]


def mine_frames():
    # DLIMPET.SHP: 3 poses (healthy, damaged, spare) then 3 shadows. DLIMP_A: 10 blink
    # frames then 10 shadows; TS anims pack healthy then damaged in the usable window.
    out = []
    for pose in (0, 1):
        base = inf.with_shadow(frame("dlimpet", pose), frame("dlimpet", 3 + pose))
        for b in range(10):
            comp = base.copy()
            comp.alpha_composite(frame("dlimp_a", b))
            out.append(crisp(comp, BLDG_CANVAS, BLDG_ANCHOR, F_BLDG))
    return out


def make_frames(count=19):
    # DLIMPMK.SHP: 42 build-up frames then 42 shadows, resampled to RA's ladder length.
    total = 42
    picks = [round(i * (total - 1) / (count - 1)) for i in range(count)]
    return [crisp(inf.with_shadow(frame("dlimpmk", i), frame("dlimpmk", total + i)), BLDG_CANVAS, BLDG_ANCHOR, F_BLDG)
            for i in picks]


def patch_struct_tileset(name, count):
    import re
    xml = open(STRUCT_XML, encoding="utf-8").read()
    pat = re.compile(r"\t<Tile>\n\t\t<Key>\n\t\t\t<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n", re.S)
    xml, removed = pat.subn("", xml)
    tile = ("\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n"
            "\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s\\%s-%04d.tga</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n")
    blocks = "".join(tile % (name, s, name.lower(), name.lower(), s) for s in range(count))
    idx = xml.rindex("</Tiles>")
    open(STRUCT_XML, "w", encoding="utf-8").write(xml[:idx] + blocks + xml[idx:])
    print(f"patched RA_STRUCTURES.XML: {name} -> {count} tiles (replaced {removed})")


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


def sidebar_building(ini, icon):
    """Base RA_<INI> entry for a structure that never reaches the sidebar (name/description
    lookups only), in the hand-written TS-tree block like the unit entries."""
    xml = open(RAB, encoding="utf-8").read()
    key = f"RA_{ini}"
    if f'"{key}"' in xml:
        return
    entry = ('\t<ObjectTypeClass Name="%s" Classification="CNCBuildableObject" CanInstantiate="False">\n'
             "\t\t<CNCEncyclopediaComponent>\n"
             "\t\t\t<ObjectNameTextID>TEXT_STRUCTURE_%s</ObjectNameTextID>\n"
             "\t\t\t<ObjectDescriptionTextID>TEXT_STRUCTURE_%s_DESC</ObjectDescriptionTextID>\n"
             "\t\t\t<BuildIcon>%s</BuildIcon>\n"
             "\t\t</CNCEncyclopediaComponent>\n"
             "\t</ObjectTypeClass>\n" % (key, ini, ini, icon))
    open(RAB, "w", encoding="utf-8").write(xml.replace(inf.HAND_END, entry + inf.HAND_END, 1))
    print(f"patched RABUILDABLES.XML: {key}")


def text_rows_building(ini, display, desc):
    raw = open(inf.CSV, "rb").read()
    text = raw.decode("utf-16")
    eol = "\r\n" if "\r\n" in text else "\n"
    sample = next(l for l in text.splitlines() if l.startswith('"TEXT_UNIT_TDA10"'))
    tail = sample.split('"A-10 Warthog"', 1)[1]
    new = ""
    for key, val in ((f"TEXT_STRUCTURE_{ini}", display), (f"TEXT_STRUCTURE_{ini}_DESC", desc)):
        if f'"{key}"' not in text:
            new += f'"{key}",,,"{val}"{tail}{eol}'
    if new:
        if not text.endswith(eol):
            text += eol
        open(inf.CSV, "wb").write((text + new).encode("utf-16"))
        print(f"patched ModText.csv: TEXT_STRUCTURE_{ini}")


def sounds():
    for aud in SOUNDS:
        pcm = f"{ART}/.raw/{aud}.pcm.wav"
        subprocess.run([sys.executable, f"{HERE}/ts_aud_decode.py", f"{ART}/.raw/{aud}.AUD", pcm],
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pcm, "-c:a", "adpcm_ms",
                        "-ar", "22050", "-ac", "1", f"{MOD}/Data/AUDIO/TS{aud}.WAV"], check=True)
        print(f"wrote TS{aud}.WAV")


def main():
    drone = drone_frames()
    inf.write_zip(f"{inf.UNITS_DIR}/TSLIMP.ZIP", "tslimp", drone)
    inf.patch_tileset("TSLIMP", len(drone))
    mine = mine_frames()
    inf.write_zip(f"{STRUCT_DIR}/TSDLIMP.ZIP", "tsdlimp", mine)
    patch_struct_tileset("TSDLIMP", len(mine))
    make = make_frames()
    inf.write_zip(f"{STRUCT_DIR}/TSDLIMPMAKE.ZIP", "tsdlimpmake", make)
    patch_struct_tileset("TSDLIMPMAKE", len(make))
    cameo()
    inf.sidebar("TSLIMP", "BuildIcon_TS_LimpetDrone")
    inf.text_rows("TSLIMP", "Limpet Drone",
                  "Unarmed hover drone. Deploys into a cloaked mine that latches onto the next enemy "
                  "vehicle, slowing it and revealing what it sees until it visits a repair bay.")
    sidebar_building("TSDLIMP", "BuildIcon_TS_LimpetDrone")
    text_rows_building("TSDLIMP", "Limpet Mine",
                       "A settled Limpet Drone. Cloaked; leaps onto the next enemy vehicle to pass. "
                       "Deploy again to pick it up.")
    sounds()
    out = os.environ.get("TSLIMP_SHEET")
    if out:
        cols = drone + mine[::2] + make[::3]
        w = 256
        sh = Image.new("RGBA", (w * 10, w * ((len(cols) + 9) // 10)), (70, 110, 70, 255))
        for k, fr in enumerate(cols):
            fr = fr.resize((w, w)) if fr.width != w else fr
            sh.alpha_composite(fr, ((k % 10) * w, (k // 10) * w))
        sh.save(out)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
