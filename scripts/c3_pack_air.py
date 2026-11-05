#!/usr/bin/env python3
"""Package the C&C3 aircraft: GDI's Orca (C3ORCA) and with its Sensor Pod (C3ORCAPOD), Firehawk (C3FHAWK) and V-35
Ox (C3OX); Nod's Venom (C3VENOM) and with its Signature Generator (C3VENOMSG), Vertigo (C3VERT) and Carryall
(C3CARRY).

Tileset layout per aircraft (as the TS aircraft): 0-31, one frame per facing (CCW, 0 = N), on a square canvas of
ShapeSize x 8 centred on the model's own middle. No baked shadow: the engine shadows aircraft in the air. Renders
come from c3_render.py (--part hull --tread-steps 1) at c3_pack_tanks.RENDER_PPU and pack at its PACK_PPU, so the
aircraft keep their size against the C&C3 tanks.

Audio: each aircraft's own C&C3 crew voice and weapon takes, re-encoded MS-ADPCM 22050 Hz mono under C3 names, in
their own marked block of each pack's SFXEVENTSNONLOCALIZED_CNC3.XML.

Inputs (set C3_ART_DIR): renders/<model>_hull/frame-NNNN.png from c3_render.py, cameo/<NAME>.png, and
audio/<model>/<C&C3 name>.wav from tools/cnc3/c3_extract_audio.py (workspace).
Usage: c3_pack_air.py [NAME ...] packs the named aircraft and their audio; with no names, all of them.
c3_pack_air.py audio writes only the audio.

License: GPL v3.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_packs  # noqa: E402
import c3_pack_tanks as tanks  # noqa: E402

FRAMES = 32

# name, model, ShapeSize, cameo (None: an upgrade variant, which keeps its base aircraft's cameo)
AIRCRAFT = (
    ("C3ORCA", "orca", 48, "C3ORCA"),
    ("C3ORCAPOD", "orca_probe", 48, None),
    ("C3FHAWK", "firehawk", 48, "C3FHAWK"),
    ("C3OX", "ox", 80, "C3OX"),
    ("C3VENOM", "venom", 48, "C3VENOM"),
    ("C3VENOMSG", "venom_siggen", 48, None),
    ("C3VERT", "vertigo", 48, "C3VERT"),
    ("C3CARRY", "carryall", 80, "C3CARRY"),
)


def _takes(stem, model, sample, letters):
    """One sound event per take letter: C3<stem><LETTER> plays <sample><letter>."""
    return [(f"{stem}{c}", model, [f"{sample}{c.lower()}"]) for c in letters]


# VOC stem -> (model, C&C3 sample names). Every stem is pack-only, so it is listed in asset_packs.PACK_ONLY_SOUNDS.
SOUNDS = (
    _takes("C3OSE", "orca", "GUOrca_VoiSelect", "ABCDEFGHI") + _takes("C3OMO", "orca", "GUOrca_VoiMove", "ABCDEFGHIJKL")
    + _takes("C3OAT", "orca", "GUOrca_VoiAttack", "ABCDE")
    + [("C3OGUN", "orca", [f"GUOrca_rockFire{c}" for c in "abcdefghij"]),
       ("C3OHIT", "orca", [f"GUOrca_rockExpl{c}" for c in "abcdefghijk"])]
    + _takes("C3HSE", "firehawk", "GUFireh_VoiSelect", "ABCDEF")
    + _takes("C3HMO", "firehawk", "GUFireh_VoiMove", "ABCDEFG")
    + _takes("C3HAT", "firehawk", "GUFireh_VoiAttack", "ABCDEFGHI")
    + [("C3HGUN", "firehawk", [f"GUFireH_wea1fire{c}" for c in "abc"]),
       ("C3HBMB", "firehawk", ["GUFireh_firebomb1a"])]
    + _takes("C3VSE", "venom", "NUVenom_VoiSelect", "ABCDEF") + _takes("C3VMO", "venom", "NUVenom_VoiMove", "ABCDEFGHI")
    + _takes("C3VAT", "venom", "NUVenom_VoiAttack", "ABCDEF")
    + [("C3VGUN", "venom", [f"NUVenom_gunFire6{c}" for c in "abcdef"]),
       ("C3VLAS", "venom", [f"NUVenom_capaFire{c}" for c in "abcdefg"])]
    + _takes("C3WSE", "vertigo", "NuVerti_VoiSelect", "ABCDEF")
    + _takes("C3WMO", "vertigo", "NuVerti_VoiMove", "ABCDEF")
    + _takes("C3WAT", "vertigo", "NuVerti_VoiMovAtt", "ABCDEF")
    + [("C3WBMB", "vertigo", [f"NUVertigo_bombDrop{c}" for c in "abcdef"]),
       ("C3WHIT", "vertigo", [f"NUVerti_bombExpl{c}" for c in "abcdef"])]
    + _takes("C3XSE", "ox", "GUOxTra_VoiSelect", "ABCDEFG") + _takes("C3XMO", "ox", "GUOxTra_VoiMove", "ABCDEFG")
    + _takes("C3XPK", "ox", "GUOxTra_VoiPickup", "ABCDEFGH") + _takes("C3XDO", "ox", "GUOxTra_VoiDropo", "ABCDE")
    + _takes("C3CSE", "carryall", "NuCarry_VoiSelect", "ABCDE")
    + _takes("C3CMO", "carryall", "NuCarry_VoiMove", "ABCDEFG")
    + _takes("C3CPK", "carryall", "NUCarry_VoiPickup", "ABCD")
)
SFX_BEGIN = "  <!-- BEGIN C&C3 aircraft sounds (scripts/c3_pack_air.py) -->"
SFX_END = "  <!-- END C&C3 aircraft sounds -->"


def write_audio(models=None):
    tanks.write_audio(models, SOUNDS, SFX_BEGIN, SFX_END)


def main(names):
    if not tanks.ART:
        raise SystemExit("set C3_ART_DIR (holding renders/, cameo/, audio/)")
    unknown = set(names) - {a[0] for a in AIRCRAFT}
    if unknown:
        raise SystemExit(f"unknown aircraft: {', '.join(sorted(unknown))}")
    for name, model, shape, cameo in AIRCRAFT:
        if names and name not in names:
            continue
        canvas = shape * 8
        frames = [tanks.packed(f"{tanks.ART}/renders/{model}_hull/frame-{i:04d}.png", canvas, False)
                  for i in range(FRAMES)]
        tanks.write_zip(asset_packs.art_zip(name, "UNITS"), name.lower(), frames)
        tanks.patch_tileset(name, FRAMES)
        if cameo:
            tanks.write_cameo(cameo)
    write_audio({a[1].split("_")[0] for a in AIRCRAFT if a[0] in names} if names else None)


if __name__ == "__main__":
    if sys.argv[1:] == ["audio"]:
        write_audio()
    else:
        main(sys.argv[1:])
