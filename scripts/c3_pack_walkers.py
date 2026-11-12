#!/usr/bin/env python3
"""Package the C&C3 walkers: GDI's Juggernaut (C3JUGG) and Nod's Avatar (C3AVATAR) with each piece it commandeers:
the beam cannon (C3AVATARBM), stealth detector (C3AVATARSD), stealth generator (C3AVATARSG) and flamethrower
(C3AVATARFL).

Tileset layouts, TF's TS walker gait (WalkFacings blocks of WalkFrames, facings CCW from north):
  C3JUGG    0-95 walk: 8 facings x 12 stages; 96-127 turret: 32 facings, no shadow (the TS Titan's layout, so the
            turret stays under the launcher's 128-shape cap for a second draw).
  C3AVATAR* 0-255 walk: 32 facings x 8 stages. The Avatar has no turret bone: its torso turns only in its clips, so
            it turns to fire, as the TS Mammoth Mk. II does.
The walk is one cycle of the C&C3 walk clip; its first stage is the pose at rest. The Juggernaut's turret bobs in
the clip but is drawn apart from it, so it is rendered at the cycle's mean height. Every walk frame carries its own
shadow, cast from the walk part onto the ground along the render light: a turret drawn apart casts none, so its
shadow never points the guns the wrong way.

Inputs (set C3_ART_DIR): model/<model>.npz from tools/cnc3/c3_extract_walker.py (workspace), cameo/<NAME>.png,
audio/<model>/<C&C3 name>.wav from tools/cnc3/c3_extract_audio.py. Renders cache in renders/<model>_walk/ and
renders/<model>_turret/: delete them after changing the model or the render settings.
Usage: c3_pack_walkers.py [NAME ...]; with no names, every walker. Run scripts/dedupe_tileset_frames.py afterwards.

License: GPL v3.
"""
import math
import multiprocessing
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_packs  # noqa: E402
import c3_pack_tanks as tanks  # noqa: E402
import c3_render  # noqa: E402

ART = tanks.ART
SHADOW_ALPHA = 191  # EA's baked ground shadows
RENDER_CANVAS = 1400  # holds a walker 48 C&C3 units tall at RENDER_PPU
TURRET_CANVAS = 1800  # the Juggernaut's barrels reach 55 units up the screen facing north
SHADOW_BLUR = 3

# name, model, ShapeSize, walk facings, walk stages, turret weapons' fire pivots (None: no turret), cameo
WALKERS = (
    ("C3JUGG", "juggernaut", 96, 8, 12, (("FXMUZZLE01", "FXMUZZLE02", "FXMUZZLE03"),), "C3JUGG"),
    ("C3AVATAR", "avatar", 80, 32, 8, None, "C3AVATAR"),
    ("C3AVATARBM", "avatar_beam", 80, 32, 8, None, None),
    ("C3AVATARSD", "avatar_detector", 80, 32, 8, None, None),
    ("C3AVATARSG", "avatar_generator", 80, 32, 8, None, None),
    ("C3AVATARFL", "avatar_flamer", 80, 32, 8, None, None),
)

SOUNDS = (
    tanks.takes("C3JSE", "juggernaut", "GUJugge_VoiSelect", "ABCDEFG")
    + tanks.takes("C3JMO", "juggernaut", "GUJugge_VoiMove", "ABCDEFG")
    + tanks.takes("C3JAT", "juggernaut", "GUJugge_VoiAttack", "ABCDEFGHIJ")
    + [("C3JGUN", "juggernaut", [f"GUJugge_wea3fire{c}" for c in "abcdefghijkl"])]
    + tanks.takes("C3QSE", "avatar", "NUAvata_VoiSelect", "ABCDE")
    + tanks.takes("C3QMO", "avatar", "NUAvata_VoiMove", "ABCDEFG")
    + tanks.takes("C3QAT", "avatar", "NUAvata_VoiAttack", "ABCDEF")
    + [("C3QGUN", "avatar", [f"NUAvata_weaLaser{c}" for c in "abcdefg"]),
       ("C3QBEAM", "avatar", [f"NUBeamC_wea1Fire{c}" for c in "abcdefg"]),
       ("C3QSTEP", "avatar", [f"NUAvata_footstep{c}" for c in "abcdefghij"])]
)
SFX_BEGIN = "  <!-- BEGIN C&C3 walker sounds (scripts/c3_pack_walkers.py) -->"
SFX_END = "  <!-- END C&C3 walker sounds -->"


def posed_model(model, pose):
    """The walker at a walk stage (None: the base pose), its hull centre kept at the base pose's."""
    path = f"{ART}/model/{model}.npz"
    m = c3_render.Model(path)
    if pose is not None:
        d = np.load(path)
        m.pos, m.nrm, m.tan, m.bin = (d[k][pose] for k in ("poses_pos", "poses_nrm", "poses_tan", "poses_bin"))
    return m


def render_walk(args):
    """The walker at a facing and walk stage, and its shadow cast along the render light onto the ground."""
    model, facing, facings, pose = args
    path = f"{ART}/renders/{model}_walk/f{facing:02d}-p{pose:02d}.png"
    shadow = path[:-4] + "-shadow.png"
    if os.path.exists(path) and os.path.exists(shadow):
        return path, shadow
    m = posed_model(model, pose)
    yaw = tanks.YAW0 + facing * 360.0 / facings
    os.makedirs(os.path.dirname(path), exist_ok=True)
    unclipped(c3_render.render(m, yaw, "hull", tanks.RENDER_PPU, RENDER_CANVAS, tanks.ELEV_DEG), path).save(path)
    a = math.radians(yaw)
    light = np.array([[math.cos(a), math.sin(a), 0], [-math.sin(a), math.cos(a), 0], [0, 0, 1]]) @ c3_render.LIGHT
    pos = m.pos.copy()
    m.pos = pos - light[None, :] * (np.maximum(pos[:, 2], 0) / light[2])[:, None]
    m.pos[:, 2] = 0.0
    cast = Image.new("RGBA", (RENDER_CANVAS, RENDER_CANVAS), (0, 0, 0, 0))
    cast.putalpha(c3_render.render(m, yaw, "hull", tanks.RENDER_PPU, RENDER_CANVAS, tanks.ELEV_DEG).getchannel("A"))
    cast.save(shadow)
    return path, shadow


def render_turret(args):
    model, facing = args
    path = f"{ART}/renders/{model}_turret/frame-{facing:04d}.png"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        unclipped(c3_render.render(posed_model(model, None), tanks.YAW0 + facing * 360.0 / 32, "turret",
                                   tanks.RENDER_PPU, TURRET_CANVAS, tanks.ELEV_DEG), path).save(path)
    return path


def unclipped(im, path):
    """The render, refused if the model reaches its edge (the canvas cut it off)."""
    a = np.asarray(im.getchannel("A"))
    if max(a[0].max(), a[-1].max(), a[:, 0].max(), a[:, -1].max()):
        raise SystemExit(f"{path}: the model reaches the {im.width} px render's edge -- grow its canvas")
    return im


def walk_frame(paths, canvas):
    """The walk render over its blurred cast shadow, packed on the canvas."""
    body = tanks.packed(paths[0], canvas, False)
    mask = tanks.packed(paths[1], canvas, False).getchannel("A")
    mask = mask.point(lambda v: SHADOW_ALPHA if v > 127 else 0).filter(ImageFilter.GaussianBlur(SHADOW_BLUR))
    fr = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    fr.putalpha(mask)
    fr.alpha_composite(body)
    return fr


def pack(name, model, shape, facings, stages, weapons, cameo):
    canvas = shape * 8
    jobs = [(model, f, facings, p) for f in range(facings) for p in range(stages)]
    with multiprocessing.Pool(tanks.RENDER_WORKERS) as pool:
        walk = pool.map(render_walk, jobs)
        turret = pool.map(render_turret, [(model, f) for f in range(32)]) if weapons else []
    frames = [walk_frame(p, canvas) for p in walk] + [tanks.packed(p, canvas, False) for p in turret]
    tanks.write_zip(asset_packs.art_zip(name, "UNITS"), name.lower(), frames)
    tanks.patch_tileset(name, len(frames))
    if cameo:
        tanks.write_cameo(cameo)


def header_units():
    """(name, model, weapons) of the walkers with a turret, for c3tanks.h."""
    return [(n, m, w) for n, m, _, _, _, w, _ in WALKERS if w]


def main(names):
    if not ART:
        raise SystemExit("set C3_ART_DIR (holding model/, cameo/, audio/)")
    unknown = set(names) - {w[0] for w in WALKERS}
    if unknown:
        raise SystemExit(f"unknown walker(s): {', '.join(sorted(unknown))}")
    for row in WALKERS:
        if not names or row[0] in names:
            pack(*row)
    tanks.write_header()
    tanks.write_audio({w[1].split("_")[0] for w in WALKERS if w[0] in names} if names else None, SOUNDS, SFX_BEGIN,
                      SFX_END)


if __name__ == "__main__":
    main(sys.argv[1:])
