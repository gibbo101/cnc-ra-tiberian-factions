"""
tsvox.py - TS's voxels drawn as they are, for comparing with the HD frames when a unit has no in-mod frames yet: every
voxel TS stores (its surface voxels) as a square splat in its palette colour, lit by its own TS normal, through the same
camera as the HD frames (orthographic, 32 degrees, the unit's px per voxel and place), depth-tested.  House colour (TS's
remap voxels, 16-31) is drawn in the HD green with TS's remap shade.  No outline, no shadow: TS's data, nothing added.
"""
import numpy as np
from PIL import Image
import rcrender as RR
import voxrender as VR

GREEN = np.array([0, 214, 0.])


def splat(unit, pal, facing, cam, size, hf=0, light=None, amb=0.55, dif=0.62, grow=1.12):
    """an RGBA image (size) of the unit's voxels at the mod's facing."""
    W, H = size
    Mx = VR.facing_cw(VR.mod_to_cw(facing))
    L = cam.cam_to_world(RR.L_CAM) if light is None else np.asarray(light, float)
    pts, cols, nrms = [], [], []
    for i, s in enumerate(unit.sections):
        R, t = unit.pose(i, hf)
        f = s.col >= 0
        I = np.argwhere(f).astype(float)
        loc = s.mn + (I + 0.5) * s.scale
        P = (Mx @ (R @ loc.T + t[:, None])).T
        c = s.col[f].astype(int)
        n_idx = s.tsn[f]
        nw = (Mx @ R @ (n_idx / s.scale[None, :]).T).T
        nw = nw / (np.linalg.norm(nw, axis=1, keepdims=True) + 1e-9)
        pts.append(P); cols.append(c); nrms.append(nw)
    P = np.concatenate(pts); C = np.concatenate(cols); N = np.concatenate(nrms)
    base = pal[np.clip(C, 0, 255)].astype(np.float32)
    house = (C >= 16) & (C <= 31)
    ramp_max = pal[16:32].max(-1).max()
    base[house] = GREEN[None, :] * (pal[C[house]].max(-1) / ramp_max)[:, None]
    shade = amb + dif * np.clip(N @ L, 0, None)
    rgb = np.clip(base * shade[:, None], 0, 255)
    sx, sy = cam.project(P)
    depth = P @ cam.D                                   # along the view ray: smaller = nearer the camera
    order = np.argsort(-depth)                          # far first, near drawn last
    img = np.zeros((H, W, 4), np.float32)
    half = cam.ppu * grow / 2
    hy = cam.ppu * grow * (cam.sE + cam.cE) / 2 / 1.2
    for j in order:
        x0, x1 = int(np.floor(sx[j] - half)), int(np.ceil(sx[j] + half))
        y0, y1 = int(np.floor(sy[j] - hy)), int(np.ceil(sy[j] + hy))
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, W), min(y1, H)
        if x1 <= x0 or y1 <= y0:
            continue
        img[y0:y1, x0:x1, :3] = rgb[j]
        img[y0:y1, x0:x1, 3] = 255
    return Image.fromarray(img.round().astype(np.uint8), 'RGBA')
