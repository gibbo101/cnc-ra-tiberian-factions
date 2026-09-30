"""Above-pad masks for the vertical gate frames.

A wall joining a north-south gate from the north ends on the gate's pad, behind whatever of the
gate stands up off it. Walls draw before buildings, so the mod draws that end piece after the gate
and needs to know which of the gate's pixels stand in front of it: above the pad, on ground south
of where the wall's end piece stops. This re-renders each vertical
frame, checks it matches the shipped frame (same alpha, colours within rounding), and writes <prefix>-v-NN-above.png beside it
(white = the ray hit something higher than the pad's own surface, averaged down from the
supersampled render).

    python3 above_pad.py [gate ...]        gate = ts-gdi ts-nod ra-allies ra-soviets td-gdi td-nod
Needs numpy, scipy, Pillow; run from this directory.
"""
import os, sys
import numpy as np
from PIL import Image
import gates2, gates3, gates4

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.dirname(HERE)
GATES = {  # folder: (file prefix, frame count, make the renderer for a frame)
    "ts-gdi": ("gdi-gate", 20, lambda f: gates2.Gate("gdi", "v", f)),
    "ts-nod": ("nod-gate", 14, lambda f: gates2.Gate("nod", "v", f)),
    "ra-allies": ("allies-gate", 20, lambda f: gates4.DESIGNS["allies"]("v", f, gates4.TRIMS["allies"])),
    "ra-soviets": ("soviet-gate", 20, lambda f: gates4.DESIGNS["soviet"]("v", f, gates4.TRIMS["soviet"])),
    "td-gdi": ("tdgdi-gate", 20, lambda f: gates4.DESIGNS["tdgdi"]("v", f, gates4.TRIMS["tdgdi"])),
    "td-nod": ("tdnod-gate", 20, lambda f: gates3.DESIGNS["tdnod"]("v", f, gates3.TRIMS["tdnod"])),
}
SLACK = 0.5  # height above the pad surface that still counts as pad
WALL_END = 30.5  # the joining wall's end piece stands on the ground down to this row of the gate's north cell


def above_mask(gate):
    captured = {}
    raycast = gate.raycast

    def keep():
        captured["rc"] = raycast()
        return captured["rc"]

    gate.raycast = keep
    out = gate.render()
    img = out[0] if isinstance(out, tuple) else out
    hit, zh, comp, _, gj = captured["rc"][:5]
    pad = np.median(zh[hit & (comp == gates2.BASE) & (zh >= 0)])
    ground_y = (gj - gates2.M * gates2.SS) / float(gates2.SS)
    above = (hit & (zh > pad + SLACK) & (ground_y > WALL_END)).astype(np.float32)
    ss = above.shape[0] // img.size[1]
    small = above.reshape(img.size[1], ss, img.size[0], ss).mean(axis=(1, 3))
    return img, Image.fromarray((small * 255).round().astype(np.uint8), "L")


def main(names):
    for name in names:
        prefix, frames, make = GATES[name]
        for f in range(frames):
            img, mask = above_mask(make(f))
            shipped = Image.open(os.path.join(ART, name, f"{prefix}-v-{f:02d}.png")).convert("RGBA")
            d = np.abs(np.array(img.convert("RGBA")).astype(int) - np.array(shipped).astype(int))
            if d[:, :, 3].max() > 0 or d.max() > 4:
                raise SystemExit(f"{name} frame {f}: the render no longer matches the shipped frame")
            mask.save(os.path.join(ART, name, f"{prefix}-v-{f:02d}-above.png"))
            print(name, f, flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or list(GATES))
