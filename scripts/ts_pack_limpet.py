#!/usr/bin/env python3
"""Package the TS Limpet Drone (Firestorm) into the mod tree:
  TSLIMP.ZIP (units)            10 frames: the LIMPED.SHP crawl cycle with its own shadows,
                                no facings (unit.cpp Shape_Number cycles them by frame)
  TSDLIMP.ZIP (structures)      20 frames: DLIMPET body (healthy / damaged) under the
                                DLIMP_A blink, 10 healthy then 10 damaged
  TSDLIMPMAKE.ZIP (structures)  19 frames: the DLIMPMK build-up (42 TS frames resampled)
plus BuildIcon_TS_LimpetDrone.tga (Firestorm ships no LIMPICON: the gold mine on E1ICON's
backdrop), the base RA_TSLIMP / RA_TSDLIMP sidebar entries, the ModText rows and the
five LIMP*.AUD sounds as Data/AUDIO/TS<NAME>.WAV.
Scale: TS SHP px x 5.0 (hq4x then LANCZOS), the largest that keeps the build-up's standing
drone inside its canvas. Unit canvas 192 (ShapeSize 24 x 8): TS draws the hover drone well
above its shadow, so the body is dropped to a short hover and the pair centred. Building
canvases 256 (48x48 classic stub, a 1x1 plot): TS source (48,48), the mine's centre, lands on
the canvas centre for the mine and its build-up alike, so the ladder ends where the mine sits.
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
F = 5.0
UNIT_CANVAS = 192
BLDG_CANVAS = 256
HOVER_DROP = 0    # TS px the airborne LIMPED body comes down toward its shadow: none, TS draws it hovering two px clear
BLDG_ANCHOR = (48, 48)
SOUNDS = ("LIMPBOM1", "LIMPQ3", "LIMPQ4", "LIMPC3", "LIMPC4")


def frame(stem, i):
    return Image.open(f"{ART}/shp_{stem}/frame-{i:04d}.png").convert("RGBA")


def crisp(img, canvas, anchor=None):
    """hq4x then LANCZOS to F. The anchor (source px) lands on the canvas centre; by default
    the centre of the image's opaque bounding box."""
    if anchor is None:
        b = img.getbbox()
        anchor = ((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0)
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    big = hqx.hq4x(rgb).convert("RGBA")
    big.putalpha(img.split()[3].resize((img.width * 4, img.height * 4), Image.LANCZOS))
    scaled = big.resize((round(img.width * F), round(img.height * F)), Image.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    inf.safe_paste(out, scaled, round(canvas / 2 - anchor[0] * F), round(canvas / 2 - anchor[1] * F))
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
            out.append(crisp(comp, BLDG_CANVAS, BLDG_ANCHOR))
    return out


def make_frames(count=19):
    # DLIMPMK.SHP: 42 build-up frames then 42 shadows, resampled to RA's ladder length.
    total = 42
    picks = [round(i * (total - 1) / (count - 1)) for i in range(count)]
    return [crisp(inf.with_shadow(frame("dlimpmk", i), frame("dlimpmk", total + i)), BLDG_CANVAS, BLDG_ANCHOR)
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


def cameo():
    """No LIMPICON in Firestorm's archives: the settled mine in house gold on a TS cameo
    backdrop (E1ICON's steel wall and floor, the figure's slot stretched out)."""
    import ts_shp
    pal = ts_shp.load_pal(f"{ART}/.raw/UNITTEM.PAL")
    _, poses = ts_shp.decode_shp(f"{ART}/.raw/DLIMPET.SHP")
    body = ts_shp.frame_to_rgba(poses[0], pal, remap=(16, 31), team=(232, 190, 60))
    shadow = inf.with_shadow(Image.new("RGBA", body.size, (0, 0, 0, 0)), ts_shp.frame_to_rgba(poses[3], pal))
    comp = shadow
    comp.alpha_composite(body)
    comp = comp.crop(comp.getbbox())
    rgb = Image.new("RGB", comp.size, (0, 0, 0))
    rgb.paste(comp, (0, 0), comp)
    big = hqx.hq4x(rgb).convert("RGBA")
    big.putalpha(comp.split()[3].resize((comp.width * 4, comp.height * 4), Image.LANCZOS))
    big = big.resize((40, round(big.height * 40 / big.width)), Image.LANCZOS)
    scene = frame("e1icon", 0)
    w, h = scene.size
    back = Image.new("RGBA", (w, h))
    back.paste(scene.crop((0, 0, 16, h)).resize((w // 2, h), Image.BILINEAR), (0, 0))
    back.paste(scene.crop((w - 16, 0, w, h)).resize((w // 2, h), Image.BILINEAR), (w // 2, 0))
    back = back.filter(ImageFilter.GaussianBlur(0.35))
    back.alpha_composite(big, ((w - big.width) // 2, (h - big.height) // 2 + 5))
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
