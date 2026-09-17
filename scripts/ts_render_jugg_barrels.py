#!/usr/bin/env python3
"""Render the Juggernaut's DJUGGBAR barrel bundle for scripts/ts_pack_jugg.py: 32 facings at the
fleet camera (yaw0 90, elev 30, 12 px/voxel, HVA frame 0), level (pitch 5, TS's resting
BarrelPitch) into renders_djuggbar and aiming (pitch 45) into renders_djuggbar_p45. The two
rearmost voxel slabs, the recoil rods behind the breech, are dropped: they sit inside the cabin
in TS and swing out below it when the bundle pitches. Inputs under TS_ART_DIR/.raw.
License: GPL v3.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vxl_render as v

ART = os.environ.get("TS_ART_DIR")
REAR_CLIP = 6          # voxel slabs dropped from the rear of the bundle
SETS = ((5, "renders_djuggbar"), (45, "renders_djuggbar_p45"))


def main():
    model = v.parse_vxl(f"{ART}/.raw/DJUGGBAR.VXL")
    hva = v.parse_hva(f"{ART}/.raw/DJUGGBAR.HVA")[0]
    for sec in model["sections"]:
        sec["occ"][:REAR_CLIP, :, :] = False
    v.set_elevation(30.0)
    for pitch, outdir in SETS:
        out = f"{ART}/{outdir}"
        os.makedirs(out, exist_ok=True)
        worst = 0
        for f in (0, 8):
            _, c = v.render_frame(model, 90 + f * 11.25, 12, (0, 200, 0), 0, hva_mats=hva, pitch_deg=pitch)
            worst = max(worst, c)
        for f in range(32):
            img, _ = v.render_frame(model, 90 + f * 11.25, 12, (0, 200, 0), 0, worst, hva_mats=hva, pitch_deg=pitch)
            img.save(f"{out}/frame-{f:04d}.png")
        print(f"rendered pitch {pitch} -> {out} (canvas {worst})")


if __name__ == "__main__":
    main()
