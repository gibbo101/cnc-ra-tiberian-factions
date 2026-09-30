#!/usr/bin/env python3
"""Sidebar cameos for the gates: each gate's shut frame (its own trim colours) on the TS cameo scene,
the east-west gate lying across it, the north-south gate standing up it. Writes the hand-made cameo
PNGs to resources/custom-cameos (install them with scripts/apply_custom_cameos.py), then bakes each
TS-badged variant BuildIcon_<INI>_G.tga by copying the badge from the TS wall's own pair.

The scene is the TS Concrete Wall cameo's, with the wall painted out from the empty columns at its
left edge.

Usage: gate_cameos.py
License: GPL v3.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CUSTOM = os.path.join(ROOT, "resources", "custom-cameos")
SRGB = os.path.join(ROOT, "resources", "remaster_mods", "Vanilla_RA", "Data", "ART", "TEXTURES", "SRGB")
ART = os.path.join(ROOT, "resources", "custom-art", "cnc-gates-hd")

GATES = [  # folder, frame prefix, INI stem, cameo stems (east-west, north-south)
    ("ts-gdi", "gdi-gate", "TSGATE", ("BuildIcon_TS_GateH", "BuildIcon_TS_GateV")),
    ("ts-nod", "nod-gate", "TSNGATE", ("BuildIcon_TSNGATEH", "BuildIcon_TSNGATEV")),
    ("ra-allies", "allies-gate", "ALGATE", ("BuildIcon_ALGATEH", "BuildIcon_ALGATEV")),
    ("ra-soviets", "soviet-gate", "SVGATE", ("BuildIcon_SVGATEH", "BuildIcon_SVGATEV")),
    ("td-gdi", "tdgdi-gate", "TDGGATE", ("BuildIcon_TDGGATEH", "BuildIcon_TDGGATEV")),
    ("td-nod", "tdnod-gate", "TDNGATE", ("BuildIcon_TDNGATEH", "BuildIcon_TDNGATEV")),
]


def scene():
    a = np.array(Image.open(os.path.join(CUSTOM, "BuildIcon_TS_Wall.png")).convert("RGBA"))
    bg = a.copy()
    src = a[100:215, 0:22]
    for x in range(20, 336, 22):
        w = min(22, 341 - x)
        bg[100:215, x:x + w] = src[:, :w]
    return Image.fromarray(bg)


def main():
    bg = scene()
    plain = np.array(Image.open(os.path.join(SRGB, "BuildIcon_TS_Wall.tga")).convert("RGBA")).astype(int)
    badged = np.array(Image.open(os.path.join(SRGB, "BuildIcon_TSWALL_G.tga")).convert("RGBA")).astype(int)
    badge = np.abs(plain - badged).sum(2) > 0
    for folder, prefix, ini, (icon_h, icon_v) in GATES:
        h = Image.open(os.path.join(ART, folder, f"{prefix}-h-00.png")).convert("RGBA")
        h = h.crop(h.getbbox())
        h = h.resize((300, round(h.height * 300 / h.width)), Image.LANCZOS)
        cameo_h = bg.copy()
        cameo_h.alpha_composite(h, ((341 - h.width) // 2, 150 - h.height // 2))
        v = Image.open(os.path.join(ART, folder, f"{prefix}-v-00.png")).convert("RGBA")
        v = v.crop(v.getbbox())
        v = v.resize((round(v.width * 200 / v.height), 200), Image.LANCZOS)
        cameo_v = bg.copy()
        cameo_v.alpha_composite(v, ((341 - v.width) // 2, 250 - v.height - 8))
        for cameo, icon, key in ((cameo_h, icon_h, ini + "H"), (cameo_v, icon_v, ini + "V")):
            cameo.save(os.path.join(CUSTOM, icon + ".png"))
            b = np.array(cameo)
            b[badge] = badged[badge]
            Image.fromarray(b.astype(np.uint8)).save(os.path.join(SRGB, f"BuildIcon_{key}_G.tga"))
            print("wrote", icon, "and", f"BuildIcon_{key}_G")


if __name__ == "__main__":
    main()
