#!/usr/bin/env python3
"""Package the C&C3 tanks: the Mammoth Mk. III (C3MK3) and the Predator (C3PRED).

Tileset layout per tank (the walker gait layout, contract 2 keeps the turret under 128):
  0-95    hull: 32 facings (CCW, 0 = N) x 3 tread steps; the gait code steps the treads
          while the tank drives, so the belts roll instead of the hull gliding.
  96-127  turret: 32 facings, no shadow.
Hull frames carry EA's baked drop shadow (ts_reshadow.py). Renders come from c3_render.py at
RENDER_PPU pixels per C&C3 unit and pack at PACK_PPU, on canvas = ShapeSize x 8.

The turret frames pivot on the turret bone, which sits off the hull centre (the Predator's by
7.6 C&C3 units aft). redalert/c3tanks.h carries, per hull facing, the turret seat in classic
pixels for the draw and in leptons for fire coordinates, and per turret frame each fire point
relative to the seat (projected through the render camera, 4/3 leptons per canvas px).

Audio: each tank's own C&C3 crew voice and weapon takes, re-encoded MS-ADPCM
22050 Hz mono under C3 names. One sound event per VOC; a weapon event lists every take, and the
launcher picks one per shot. The events sit between markers in each pack's
SFXEVENTSNONLOCALIZED_CNC3.XML: the weapon takes in CNC3-SFX-Pack, the crew voices in
CNC3-Voices-eng.

Art ZIPs, tiles, cameos, WAVs and sound events land where scripts/asset_packs.py routes each name;
the build merges the packs into the mod.

Inputs (set C3_ART_DIR): renders/<model>_{hull,turret}/frame-NNNN.png and model/<model>.npz
from tools/cnc3/c3_extract_model.py (workspace), cameo/<NAME>.png, audio/<model>/<C&C3 name>.wav.

License: GPL v3.
"""
import io
import json
import math
import os
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ts_reshadow import drop_shadow, EA_DX, EA_DY  # noqa: E402
import asset_packs  # noqa: E402

ART = os.environ.get("C3_ART_DIR")
HEADER = os.path.join(HERE, "..", "redalert", "c3tanks.h")

RENDER_PPU = 13.0
PACK_PPU = 6.0
ELEV = math.radians(32)
YAW0 = 90.0
TREAD_STEPS = 3
LEPTONS_PER_PX = 4 / 3

# name, model, ShapeSize, fire-point pivots per weapon (each a list of alternating sides)
UNITS = (
    ("C3MK3", "mammoth", 64, (("MUZZLEFX01", "MUZZLEFX02"), ("ROCKETLAUNCH01", "ROCKETLAUNCH02"))),
    ("C3PRED", "predator", 48, (("FXMUZZLEFLASH",),)),
)


def packed(path, canvas, shadow):
    im = Image.open(path).convert("RGBA")
    f = PACK_PPU / RENDER_PPU
    scaled = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    fr = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    ox, oy = round(canvas / 2 - scaled.width / 2), round(canvas / 2 - scaled.height / 2)
    b = scaled.getbbox()
    if b and (ox + b[0] < 0 or oy + b[1] < 0 or ox + b[2] > canvas - EA_DX or oy + b[3] > canvas - EA_DY):
        raise SystemExit(f"{path}: content clipped -- grow ShapeSize")
    fr.alpha_composite(scaled, (max(ox, 0), max(oy, 0)), (max(-ox, 0), max(-oy, 0)))
    return drop_shadow(fr, EA_DX, EA_DY) if shadow else fr


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def write_zip(path, name, frames):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            W, H = img.width, img.height
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0 = min(bb[0], W - bb[2])
            y0 = min(bb[1], H - bb[3])
            b = (x0, y0, W - x0, H - y0)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps({"size": [W, H], "crop": list(b)}))
    print(f"wrote {path} ({len(frames)} frames)")


def patch_tileset(name, count):
    import re
    sub = name.lower()
    units_xml = asset_packs.tileset_xml(name, "UNITS")
    xml = open(units_xml, encoding="utf-8").read()
    xml = re.sub(r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?", "", xml, flags=re.S)
    block = ('\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n'
             '\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n')
    blocks = "".join(block % (name, i, f"{sub}\\{sub}-{i:04d}.tga") for i in range(count))
    idx = xml.rindex("</Tiles>")
    open(units_xml, "w", encoding="utf-8").write(xml[:idx] + blocks + xml[idx:])
    print(f"patched {os.path.basename(units_xml)}: {name} -> {count} tiles")


# VOC stem -> (model, C&C3 sample names). The stems are the VOC table names in audio.cpp.
SOUNDS = (
    [(f"C3MSE{c}", "mammoth", [f"GUMammo_VoiSelect{c.lower()}"]) for c in "ABCDEF"]
    + [(f"C3MMO{c}", "mammoth", [f"GUMammo_VoiMove{c.lower()}"]) for c in "ABCDEF"]
    + [(f"C3MAT{c}", "mammoth", [f"GUMammo_VoiAttack{c.lower()}"]) for c in "ABCDEF"]
    + [("C3MGUN", "mammoth", [f"GUMammo_wea1fire{c}" for c in "abcdefghijkl"]),
       ("C3MPOD", "mammoth", [f"GUMammo_wea2fire{c}" for c in "abcd"])]
    + [(f"C3PSE{c}", "predator", [f"GUPreda_VoiSelect{c.lower()}"]) for c in "ABCDEF"]
    + [(f"C3PMO{c}", "predator", [f"GUPreda_VoiMove{c.lower()}"]) for c in "ABCDE"]
    + [(f"C3PAT{c}", "predator", [f"GUPreda_VoiAttack{c.lower()}"]) for c in "ABCDEF"]
    + [("C3PGUN", "predator", [f"GUPreda_wea1fire{c}" for c in "abcdefghi"])]
)
SFX_BEGIN = "  <!-- BEGIN C&C3 tank sounds (scripts/c3_pack_tanks.py) -->"
SFX_END = "  <!-- END C&C3 tank sounds -->"


def write_audio():
    """Each event goes in the sound-event XML of the pack its takes belong to, one marked block
    per file."""
    import subprocess
    events = {}
    for stem, model, samples in SOUNDS:
        files = []
        for i, sample in enumerate(samples):
            wav = stem if len(samples) == 1 else f"{stem}{i + 1}"
            dst = asset_packs.sound_wav(wav)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{ART}/audio/{model}/{sample}.wav",
                            "-c:a", "adpcm_ms", "-ar", "22050", "-ac", "1", dst], check=True)
            files.append(f"{wav}.WAV")
        entries = "".join(f"      <entry> {f} </entry>\n" for f in files)
        sfx_xml = asset_packs.sfx_xml(files[0], localized=False)
        for side in ("RAC", "RAR"):
            events.setdefault(sfx_xml, []).append(
                f'  <SFXEvent Name="{side}_SFX_{stem}" Preset="_PRESET_MD_MOBIUS_2D">\n'
                "    <IsPreset> False </IsPreset>\n    <MinPitch>100</MinPitch>\n"
                "    <MaxPitch>100</MaxPitch>\n    <SampleNamesList>\n"
                f"{entries}    </SampleNamesList>\n  </SFXEvent>\n")
    for sfx_xml, file_events in events.items():
        xml = open(sfx_xml, encoding="utf-8").read()
        block = SFX_BEGIN + "\n" + "".join(file_events) + SFX_END + "\n"
        if SFX_BEGIN in xml:
            a = xml.index(SFX_BEGIN)
            b = xml.index(SFX_END) + len(SFX_END) + 1
            xml = xml[:a] + block + xml[b:]
        else:
            idx = xml.rindex("</")
            xml = xml[:idx] + block + xml[idx:]
        open(sfx_xml, "w", encoding="utf-8").write(xml)
    print(f"wrote {len(SOUNDS)} sound events ({sum(len(x[2]) for x in SOUNDS)} samples) "
          f"into {len(events)} files")


def write_cameo(name):
    src = f"{ART}/cameo/{name}.png"
    if not os.path.exists(src):
        print(f"no cameo at {src}; skipped")
        return
    icon = Image.open(src).convert("RGBA")
    flat = Image.new("RGBA", icon.size, (0, 0, 0, 255))
    flat.alpha_composite(icon)
    # C&C3 portraits are square; the sidebar cameo is 4:3, so keep the centre band
    band = round(flat.width * 3 / 4)
    top = (flat.height - band) // 2
    flat = flat.crop((0, top, flat.width, top + band))
    flat.resize((341, 256), Image.LANCZOS).save(asset_packs.cameo_tga(f"BuildIcon_{name}"))
    print(f"wrote BuildIcon_{name}.tga")


def facing_yaw(f):
    return math.radians(YAW0 + f * 360.0 / 32)


def project(v, yaw):
    """Model-space offset (fwd, left, up) in C&C3 units -> canvas px (east, south)."""
    c, s = math.cos(yaw), math.sin(yaw)
    rx = v[0] * c - v[1] * s
    ry = v[0] * s + v[1] * c
    return rx * PACK_PPU, -(ry * math.sin(ELEV) + v[2] * math.cos(ELEV)) * PACK_PPU


def tables(model, weapons):
    d = np.load(f"{ART}/model/{model}.npz")
    pivots = dict(zip(d["pivot_names"], d["pivot_pos"]))
    tp = d["turret_pivot"]
    seat = [project((tp[0], tp[1], 0.0), facing_yaw(f)) for f in range(32)]
    fire = []
    for sides in weapons:
        fire.append([[project(pivots[p] - np.array([tp[0], tp[1], 0.0]), facing_yaw(f)) for f in range(32)]
                     for p in sides])
    return seat, fire


def rows_c(rows, scale):
    return "{" + ", ".join(f"{{{round(x * scale)}, {round(y * scale)}}}" for x, y in rows) + "}"


def write_header():
    out = ["// GENERATED by scripts/c3_pack_tanks.py -- do not hand-edit.",
           "// C&C3 tanks: turret seat per hull facing and fire points per turret frame (CCW, 0 = N).",
           "// _seat_px = classic px from the unit centre (draw); _seat_lep = the same in leptons.",
           "// _fire = leptons from the seat, [weapon][side][turret frame][east, south].", ""]
    for name, model, _, weapons in UNITS:
        seat, fire = tables(model, weapons)
        low = name.lower()
        out.append(f"static const signed char _{low}_seat_px[32][2] = {rows_c(seat, 1 / 8)};")
        out.append(f"static const short _{low}_seat_lep[32][2] = {rows_c(seat, LEPTONS_PER_PX)};")
        sides = max(len(s) for s in fire)
        out.append(f"static const short _{low}_fire[{len(fire)}][{sides}][32][2] = {{")
        for w in fire:
            out.append("    {")
            for side in range(sides):
                out.append("        " + rows_c(w[side % len(w)], LEPTONS_PER_PX) + ",")
            out.append("    },")
        out.append("};")
        out.append("")
    with open(HEADER, "w") as fh:
        fh.write("\n".join(out))
    print(f"wrote {os.path.normpath(HEADER)}")


def main():
    if not ART:
        raise SystemExit("set C3_ART_DIR (holding renders/, model/, cameo/)")
    for name, model, shape, _ in UNITS:
        canvas = shape * 8
        frames = [packed(f"{ART}/renders/{model}_hull/frame-{i:04d}.png", canvas, True)
                  for i in range(32 * TREAD_STEPS)]
        frames += [packed(f"{ART}/renders/{model}_turret/frame-{i:04d}.png", canvas, False)
                   for i in range(32)]
        write_zip(asset_packs.art_zip(name, "UNITS"), name.lower(), frames)
        patch_tileset(name, len(frames))
        write_cameo(name)
    write_header()
    write_audio()


if __name__ == "__main__":
    if sys.argv[1:] == ["header"]:
        write_header()
    elif sys.argv[1:] == ["audio"]:
        write_audio()
    else:
        main()
