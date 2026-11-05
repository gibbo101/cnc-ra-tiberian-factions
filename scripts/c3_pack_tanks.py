#!/usr/bin/env python3
"""Package the C&C3 tanks: the Mammoth Mk. III (C3MK3), the Predator (C3PRED), the Scorpion (C3SCORP) with its
upgrades: Laser Capacitors (C3SCORPLAS), Dozer Blades (C3SCORPDZR) and both (C3SCORPLASDZR), the Flame Tank
(C3FLAME), the Stealth Tank (C3STNK) and the Beam Cannon (C3BEAM); the Pitbull (C3PITB) and with the Mortar
upgrade (C3PITBMOR), the Guardian APC (C3APC) and the Rig (C3RIG).

Tileset layout per tank (the walker gait layout, contract 2 keeps the turret under 128):
  0-95    hull: 32 facings (CCW, 0 = N) x 3 tread steps; the gait code steps the treads
          while the tank drives, so the belts roll instead of the hull gliding.
  96-127  turret: 32 facings, no shadow.
A wheeled tank (WHEELED) has one hull frame per facing: its three step tiles name that one member.
A vehicle with no turret (NO_TURRET, the Rig) has the hull frames only, and no seat or fire table.
Hull frames carry EA's baked drop shadow (ts_reshadow.py). Renders come from c3_render.py at
RENDER_PPU pixels per C&C3 unit and pack at PACK_PPU, on canvas = ShapeSize x 8.

Hull frames are centred on the hull's own footprint. The turret frames pivot on the turret
bone, which sits off that centre (the Mammoth's forward, the Predator's aft).
The Scorpion's turret is its whole upper body. Laser Capacitors fix that body facing forward and
seat a laser turret on a tail mount (the TURRET2 bone), so C3SCORPLAS has its own hull and turret
frames. Its fixtures keep the plain tank's hull centre (c3_render.py part 3).
A variant in VARIANTS packs only the frames its upgrade changes; its other tiles name its base
tank's ZIP members. The Dozer Blade turns with the Scorpion's upper body, so C3SCORPDZR owns turret
frames only; on the laser tank it rides the fixed body, so C3SCORPLASDZR owns hull frames only.
Pack every Scorpion together, then run unit_centring.py, which moves the variants with C3SCORP.
redalert/c3tanks.h carries, per hull facing, the turret seat in classic pixels for the draw and
in leptons for fire coordinates, and per turret facing each fire point relative to the seat
(projected through the render camera, 4/3 leptons per canvas px). Every table runs by Dir_To_32,
clockwise from north, as EA's own turret tables do.

Audio: each tank's own C&C3 crew voice and weapon takes, re-encoded MS-ADPCM
22050 Hz mono under C3 names. One sound event per VOC; a weapon event lists every take, and the
launcher picks one per shot. The events sit between markers in each pack's
SFXEVENTSNONLOCALIZED_CNC3.XML: the weapon takes in CNC3-SFX-Pack, the crew voices in
CNC3-Voices-eng.

Art ZIPs, tiles, cameos, WAVs and sound events land where scripts/asset_packs.py routes each name;
the build merges the packs into the mod.

Inputs (set C3_ART_DIR): renders/<model>_{hull,turret}/frame-NNNN.png and model/<model>.npz
from tools/cnc3/c3_extract_model.py (workspace), cameo/<NAME>.png, audio/<model>/<C&C3 name>.wav
from tools/cnc3/c3_extract_audio.py (workspace).
Usage: c3_pack_tanks.py [NAME ...] packs the named tanks and variants, their audio and the header;
with no names, every tank. c3_pack_tanks.py header | audio writes only that.

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
from c3_render import hull_centre  # noqa: E402

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
    ("C3SCORP", "scorpion", 48, (("TURRETFX",),)),
    ("C3SCORPLAS", "scorpion_laser", 48, (("TURRETMS",),)),
    ("C3FLAME", "flametank", 48, (("FXFIREL", "FXFIRER"),)),
    ("C3STNK", "stealthtank", 48, (("FXWEAPONL", "FXWEAPONR"),)),
    ("C3BEAM", "beamcannon", 48, (("FX_WEAPON",),)),
    ("C3PITB", "pitbull", 48, (("FXWEAPON01", "FXWEAPON02"),)),
    ("C3APC", "apc", 48, (("FXWEAPON01", "FXWEAPON02"),)),
    ("C3RIG", "rig", 48, ()),
)
# Tanks on wheels: their renders have one hull frame per facing (c3_render.py --tread-steps 1)
WHEELED = {"C3BEAM", "C3PITB", "C3APC"}
NO_TURRET = {"C3RIG"}
# name, base tank, model, the part whose frames it owns (the rest are its base's)
VARIANTS = (
    ("C3SCORPDZR", "C3SCORP", "scorpion_dozer", "turret"),
    ("C3SCORPLASDZR", "C3SCORPLAS", "scorpion_laser_dozer", "hull"),
    ("C3PITBMOR", "C3PITB", "pitbull_mortar", "hull"),
)
HULL_FRAMES = 32 * TREAD_STEPS


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


def write_zip(path, name, frames, first=0, numbers=None):
    """The frames as <name>-NNNN members numbered from first (or by numbers), each cropped symmetrically round its
    art."""
    numbers = numbers or range(first, first + len(frames))
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in zip(numbers, frames):
            base = f"{name}-{i:04d}"
            W, H = img.width, img.height
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0 = min(bb[0], W - bb[2])
            y0 = min(bb[1], H - bb[3])
            b = (x0, y0, W - x0, H - y0)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps({"size": [W, H], "crop": list(b)}))
    print(f"wrote {path} ({len(frames)} frames)")


def patch_tileset(name, count, frames=None):
    """The object's tiles in its UNITS tileset: shape i takes frames[i] (zip\\member), or its own ZIP's member i."""
    import re
    sub = name.lower()
    units_xml = asset_packs.tileset_xml(name, "UNITS")
    xml = open(units_xml, encoding="utf-8").read()
    xml = re.sub(r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?", "", xml, flags=re.S)
    block = ('\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n'
             '\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n')
    frames = frames or [f"{sub}\\{sub}-{i:04d}.tga" for i in range(count)]
    blocks = "".join(block % (name, i, frames[i]) for i in range(count))
    idx = xml.rindex("</Tiles>")
    open(units_xml, "w", encoding="utf-8").write(xml[:idx] + blocks + xml[idx:])
    print(f"patched {os.path.basename(units_xml)}: {name} -> {count} tiles")


# VOC stem -> (model, C&C3 sample names). TF's own tanks' stems (C3M, C3P) are VOCs in audio.cpp; the rest are
# pack-only and must be in asset_packs.PACK_ONLY_SOUNDS.
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
    + [(f"C3SSE{c}", "scorpion", [f"NuScorp_VoiSelect{c.lower()}"]) for c in "ABCDEF"]
    + [(f"C3SMO{c}", "scorpion", [f"NuScorp_VoiMove{c.lower()}"]) for c in "ABCDEF"]
    + [(f"C3SAT{c}", "scorpion", [f"NUScorp_VoiAttack{c.lower()}"]) for c in "ABCDEF"]
    + [("C3SGUN", "scorpion", [f"NUScorp_cannFire{c}" for c in "abcdefghi"]),
       ("C3SLAS", "scorpion", [f"NUScorp_BeamFire{c}" for c in "abcde"])]
    + [(f"C3FSE{c}", "flametank", [f"NUFlame_VoiSelect{c.lower()}"]) for c in "ABCDEFGHIJ"]
    + [(f"C3FMO{c}", "flametank", [f"NUFlame_VoiMove{c.lower()}"]) for c in "ABCDEF"]
    + [(f"C3FAT{c}", "flametank", [f"NUFlame_VoiAttack{c.lower()}"]) for c in "ABCDEF"]
    + [("C3FGUN", "flametank", [f"NUFlame_weaFlaml{n}{c}" for n, takes in ((1, "abcde"), (2, "abcdef"), (3, "abcdef"))
                                for c in takes])]
    + [(f"C3TSE{c}", "stealthtank", [f"NuSteal_VoiSelect{c.lower()}"]) for c in "ABCDEFG"]
    + [(f"C3TMO{c}", "stealthtank", [f"NuSteal_VoiMove{c.lower()}"]) for c in "ABCDEFG"]
    + [(f"C3TAT{c}", "stealthtank", [f"NuSteal_VoiAttack{c.lower()}"]) for c in "ABCDE"]
    + [("C3TGUN", "stealthtank", [f"NUSteal_rockLaun{c}" for c in "abcdef"]),
       ("C3THIT", "stealthtank", [f"NUSteal_rockExpl{c}" for c in "abcdefgh"]),
       ("C3TCLK", "stealthtank", [f"NUSteal_stealOn{c}" for c in "abcde"]),
       ("C3TUNC", "stealthtank", [f"NUSteal_stealOff{c}" for c in "abcde"])]
    + [(f"C3BSE{c}", "beamcannon", [f"NuBeamC_VoiSelect{c.lower()}"]) for c in "ABCDEF"]
    + [(f"C3BMO{c}", "beamcannon", [f"NuBeamC_VoiMove{c.lower()}"]) for c in "ABCDEF"]
    + [(f"C3BAT{c}", "beamcannon", [f"NuBeamC_VoiAttack{c.lower()}"]) for c in "ABCDEF"]
    + [("C3BGUN", "beamcannon", [f"NUBeamC_wea1Fire{c}" for c in "abcdefg"]),
       ("C3BCHG", "beamcannon", [f"NUBeamC_wea1Swel{c}" for c in "abcdef"])]
    + [(f"C3USE{c}", "pitbull", [f"GUPitbu_VoiSelect{c.lower()}"]) for c in "ABCDEFG"]
    + [(f"C3UMO{c}", "pitbull", [f"GUPitbu_VoiMove{c.lower()}"]) for c in "ABCDEFGHIJ"]
    + [(f"C3UAT{c}", "pitbull", [f"GUPitbu_VoiAttack{c.lower()}"]) for c in "ABCDEFG"]
    + [(f"C3UAM{c}", "pitbull", [f"GUPitbu_VoiAttMor{c.lower()}"]) for c in "ABCD"]
    + [("C3UGUN", "pitbull", [f"GUGuard_wea1fire{c}" for c in "abc"]),
       ("C3UMOR", "pitbull", [f"GUPitbu_wea2fire{c}" for c in "abcdef"]),
       ("C3UHIT", "pitbull", [f"NBBrown_wea1expl{c}" for c in "abcdefgh"])]
    + [(f"C3ASE{c}", "apc", [t])
       for c, t in zip("ABCDE", [f"GUAPC_VoiSelect{c}" for c in "abcd"] + ["GUAPC_VoiCreatea"])]
    + [(f"C3AMO{c}", "apc", [f"GUAPC_VoiMove{t}"]) for c, t in zip("ABCDEF", "abdefg")]
    + [(f"C3AAT{c}", "apc", [f"GUAPC_VoiAttack{c.lower()}"]) for c in "ABCDE"]
    + [("C3AGUN", "apc", [f"GUGuard_gun8Fire{c}" for c in "abcdefghijklmnopq"])]
    + [(f"C3RSE{c}", "rig", [t])
       for c, t in zip("ABCDEFG", [f"GURig_VoiSelect{c}" for c in "abcdef"] + ["GURig_VoiCreatea"])]
    + [(f"C3RMO{c}", "rig", [f"GURig_VoiMove{c.lower()}"]) for c in "ABCDEFG"]
    + [("C3RPKA", "rig", ["GURig_VoiCreateb"])]
)
SFX_BEGIN = "  <!-- BEGIN C&C3 tank sounds (scripts/c3_pack_tanks.py) -->"
SFX_END = "  <!-- END C&C3 tank sounds -->"


def write_audio(models=None, sounds=SOUNDS, begin=SFX_BEGIN, end=SFX_END):
    """Each event goes in the sound-event XML of the pack its takes belong to, one block per file between the
    begin and end markers. Only the named models' takes are re-encoded (all when None)."""
    import subprocess
    unlisted = [s for s, _, _ in sounds if s[:3] not in ("C3M", "C3P") and s not in asset_packs.PACK_ONLY_SOUNDS]
    if unlisted:
        raise SystemExit(f"pack-only stems missing from asset_packs.PACK_ONLY_SOUNDS: {', '.join(unlisted)}")
    events = {}
    for stem, model, samples in sounds:
        files = []
        for i, sample in enumerate(samples):
            wav = stem if len(samples) == 1 else f"{stem}{i + 1}"
            dst = asset_packs.sound_wav(wav)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if models is None or model in models:
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
        block = begin + "\n" + "".join(file_events) + end + "\n"
        if begin in xml:
            a = xml.index(begin)
            b = xml.index(end) + len(end) + 1
            xml = xml[:a] + block + xml[b:]
        else:
            idx = xml.rindex("</")
            xml = xml[:idx] + block + xml[idx:]
        open(sfx_xml, "w", encoding="utf-8").write(xml)
    print(f"wrote {len(sounds)} sound events ({sum(len(x[2]) for x in sounds)} samples) "
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


def clockwise(rows):
    """Rows per frame (counter-clockwise from north) reordered by Dir_To_32 (clockwise), as EA's tables run."""
    return [rows[(32 - d) % 32] for d in range(32)]


def tables(model, weapons):
    """The turret seat per hull facing and each weapon's fire points per turret facing, both by Dir_To_32."""
    d = np.load(f"{ART}/model/{model}.npz")
    pivots = dict(zip(d["pivot_names"], d["pivot_pos"]))
    tp = d["turret_pivot"]
    hc = hull_centre(d)
    seat = [project((tp[0] - hc[0], tp[1] - hc[1], 0.0), facing_yaw(f)) for f in range(32)]
    fire = []
    for sides in weapons:
        fire.append([[project(pivots[p] - np.array([tp[0], tp[1], 0.0]), facing_yaw(f)) for f in range(32)]
                     for p in sides])
    return clockwise(seat), [[clockwise(side) for side in w] for w in fire]


def rows_c(rows, scale):
    return "{" + ", ".join(f"{{{round(x * scale)}, {round(y * scale)}}}" for x, y in rows) + "}"


def write_header():
    out = ["// GENERATED by scripts/c3_pack_tanks.py -- do not hand-edit.",
           "// C&C3 tanks: turret seat per hull facing and fire points per turret facing, by Dir_To_32 (CW, 0 = N).",
           "// _seat_px = classic px from the unit centre (draw); _seat_lep = the same in leptons.",
           "// _fire = leptons from the seat, [weapon][side][turret facing][east, south].", ""]
    for name, model, _, weapons in UNITS:
        if name in NO_TURRET:
            continue
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


def hull_shapes(name):
    """The hull shapes that own a frame: every one, or each facing's first on wheels."""
    return range(0, HULL_FRAMES, TREAD_STEPS) if name in WHEELED else range(HULL_FRAMES)


def hull_frames(model, name, canvas):
    """The hull's packed frames for hull_shapes(name), from renders with 3 steps a facing (1 on wheels)."""
    shapes = hull_shapes(name)
    return [packed(f"{ART}/renders/{model}_hull/frame-{i // (HULL_FRAMES // len(shapes)):04d}.png", canvas, True)
            for i in shapes]


def owner(name, i):
    """The shape whose frame shape i draws: on wheels, the facing's first."""
    return i - i % TREAD_STEPS if name in WHEELED and i < HULL_FRAMES else i


def pack_variant(name, base, model, part):
    """The frames of the variant's own part in its ZIP, at their shape numbers; its tiles name the rest in its base's."""
    canvas = dict((u[0], u[2]) for u in UNITS)[base] * 8
    if part == "hull":
        numbers = list(hull_shapes(base))
        own = hull_frames(model, base, canvas)
    else:
        numbers = list(range(HULL_FRAMES, HULL_FRAMES + 32))
        own = [packed(f"{ART}/renders/{model}_turret/frame-{i:04d}.png", canvas, False) for i in range(32)]
    write_zip(asset_packs.art_zip(name, "UNITS"), name.lower(), own, numbers=numbers)
    shapes = asset_packs.shape_frames(base, "UNITS")
    sub = name.lower()
    count = HULL_FRAMES + (0 if base in NO_TURRET else 32)
    frames = [f"{sub}\\{sub}-{owner(base, i):04d}.tga" if owner(base, i) in numbers
              else f"{base.lower()}\\{shapes[i]}" for i in range(count)]
    patch_tileset(name, count, frames)


def family(names):
    """The named tanks with every tank unit_centring.py moves alongside them, so a family is always packed whole."""
    import unit_centring
    unknown = set(names) - {u[0] for u in UNITS} - {v[0] for v in VARIANTS}
    if unknown:
        raise SystemExit(f"unknown tank(s): {', '.join(sorted(unknown))}")
    groups = [{leader} | {p for p, kind, _ in row[4] if kind == "UNITS"} for leader, row in unit_centring.UNITS.items()]
    return set(names).union(*(g for g in groups if g & set(names)))


def main(names):
    if not ART:
        raise SystemExit("set C3_ART_DIR (holding renders/, model/, cameo/)")
    names = family(names)
    for name, model, shape, _ in UNITS:
        if names and name not in names:
            continue
        canvas = shape * 8
        turret = 0 if name in NO_TURRET else 32
        frames = hull_frames(model, name, canvas)
        frames += [packed(f"{ART}/renders/{model}_turret/frame-{i:04d}.png", canvas, False) for i in range(turret)]
        numbers = list(hull_shapes(name)) + list(range(HULL_FRAMES, HULL_FRAMES + turret))
        write_zip(asset_packs.art_zip(name, "UNITS"), name.lower(), frames, numbers=numbers)
        sub = name.lower()
        patch_tileset(name, HULL_FRAMES + turret,
                      [f"{sub}\\{sub}-{owner(name, i):04d}.tga" for i in range(HULL_FRAMES + turret)])
        write_cameo(name)
    for name, base, model, part in VARIANTS:
        if not names or name in names:
            pack_variant(name, base, model, part)
    write_header()
    write_audio({u[1] for u in UNITS if u[0] in names} if names else None)


if __name__ == "__main__":
    if sys.argv[1:] == ["header"]:
        write_header()
    elif sys.argv[1:] == ["audio"]:
        write_audio()
    else:
        main(sys.argv[1:])
