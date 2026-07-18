#!/usr/bin/env python3
"""Render a Tiberian Sun .VXL voxel model to per-facing transparent PNGs
suitable for the mod's pack_render_to_tileset.py pipeline.

Conventions (match the mod's naval 3D pipeline):
  - orthographic camera at 54 deg elevation (depth x sin54=0.81, height x cos54=0.59)
  - transparent background, light from the top-north-west
  - team-color: voxels in the VXL's remap range are painted as a green ramp
    (hue supplied by --team-green, brightness from the voxel's palette entry)

Normals: computed from local occupancy gradient (sum of empty-neighbor
directions), not the VXL normal-index tables — visually adequate and
table-free.

Usage:
  vxl_render.py <model.vxl> <outdir> [--frames N] [--px-per-voxel P]
                [--yaw0 DEG] [--team-green R,G,B] [--z-lift N]
"""
import math, os, struct, sys
import numpy as np
from PIL import Image

ELEV = math.radians(54.0)
SIN_E, COS_E = math.sin(ELEV), math.cos(ELEV)
SS = 4  # supersample factor

LIGHT = np.array([-0.5, 0.6, 0.75])  # top, slightly NW
LIGHT = LIGHT / np.linalg.norm(LIGHT)
AMBIENT = 0.35


def parse_vxl(path):
    data = open(path, 'rb').read()
    assert data[:16].rstrip(b'\x00') == b'Voxel Animation', 'not a VXL'
    n_sections = struct.unpack_from('<I', data, 20)[0]
    body_size = struct.unpack_from('<I', data, 28)[0]
    remap_start, remap_end = data[32], data[33]
    palette = np.frombuffer(data, dtype=np.uint8, count=768, offset=34).reshape(256, 3).astype(np.float32)
    if palette.max() <= 63:
        palette = palette * (255.0 / 63.0)
    hdr_end = 802
    body_start = hdr_end + n_sections * 28
    tail_start = body_start + body_size
    sections = []
    for s in range(n_sections):
        toff = tail_start + s * 92
        span_start_off, span_end_off, span_data_off = struct.unpack_from('<III', data, toff)
        scale = struct.unpack_from('<f', data, toff + 12)[0]
        transform = struct.unpack_from('<12f', data, toff + 16)
        min_b = struct.unpack_from('<3f', data, toff + 64)
        max_b = struct.unpack_from('<3f', data, toff + 76)
        sx, sy, sz = data[toff + 88], data[toff + 89], data[toff + 90]
        base = body_start
        starts = np.frombuffer(data, dtype=np.int32, count=sx * sy, offset=base + span_start_off)
        voxels = []  # (ix, iy, iz, color)
        occ = np.zeros((sx, sy, sz), dtype=bool)
        col = np.zeros((sx, sy, sz), dtype=np.uint8)
        for i in range(sx * sy):
            if starts[i] == -1:
                continue
            p = base + span_data_off + starts[i]
            ix, iy = i % sx, i // sx
            z = 0
            while z < sz:
                skip = data[p]; num = data[p + 1]; p += 2
                z += skip
                for v in range(num):
                    c = data[p]; p += 2  # color, normal (normal ignored)
                    occ[ix, iy, z] = True
                    col[ix, iy, z] = c
                    z += 1
                p += 1  # trailing count byte
        sections.append(dict(occ=occ, col=col, size=(sx, sy, sz),
                             min_b=np.array(min_b), max_b=np.array(max_b),
                             scale=scale, transform=transform))
    return dict(sections=sections, palette=palette,
                remap=(remap_start, remap_end))


def compute_normals(occ):
    """Normal per voxel = normalized sum of directions toward empty neighbors."""
    sx, sy, sz = occ.shape
    pad = np.zeros((sx + 2, sy + 2, sz + 2), dtype=bool)
    pad[1:-1, 1:-1, 1:-1] = occ
    n = np.zeros(occ.shape + (3,), dtype=np.float32)
    for d, (dx, dy, dz) in enumerate([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]):
        empty = ~pad[1 + dx:sx + 1 + dx, 1 + dy:sy + 1 + dy, 1 + dz:sz + 1 + dz]
        for axis, dv in enumerate((dx, dy, dz)):
            if dv:
                n[..., axis] += empty * dv
    norms = np.linalg.norm(n, axis=-1, keepdims=True)
    norms[norms == 0] = 1
    return n / norms


def team_ramp(palette, remap, team_green):
    """Return a 256x3 palette with the remap range recolored as a green ramp."""
    pal = palette.copy()
    r0, r1 = remap
    tg = np.array(team_green, dtype=np.float32)
    lum = palette[r0:r1 + 1].mean(axis=1)
    peak = max(lum.max(), 1.0)
    for i in range(r0, r1 + 1):
        pal[i] = np.clip(tg * (lum[i - r0] / peak) * 1.45, 0, 255)
    return pal


def render_frame(model, yaw_deg, px_per_voxel, team_green, z_lift, canvas=None):
    pal = team_ramp(model['palette'], model['remap'], team_green)
    yaw = math.radians(yaw_deg)
    cy, sy_ = math.cos(yaw), math.sin(yaw)
    pts_all, cols_all, shade_all = [], [], []
    for sec in model['sections']:
        occ, colv = sec['occ'], sec['col']
        sx, sy, sz = sec['size']
        normals = compute_normals(occ)
        idx = np.argwhere(occ)
        if len(idx) == 0:
            continue
        min_b, max_b = sec['min_b'], sec['max_b']
        span = (max_b - min_b)
        step = span / np.array([sx, sy, sz])
        # model space (x east, y north-ish, z up), centered
        pos = min_b + (idx + 0.5) * step
        nrm = normals[idx[:, 0], idx[:, 1], idx[:, 2]]
        pts_all.append(pos)
        cols_all.append(colv[idx[:, 0], idx[:, 1], idx[:, 2]])
        shade_all.append(nrm)
    pos = np.concatenate(pts_all)
    cols = np.concatenate(cols_all)
    nrm = np.concatenate(shade_all)

    # rotate about z by yaw (CCW positive)
    rx = pos[:, 0] * cy - pos[:, 1] * sy_
    ry = pos[:, 0] * sy_ + pos[:, 1] * cy
    rz = pos[:, 2]
    nx = nrm[:, 0] * cy - nrm[:, 1] * sy_
    ny = nrm[:, 0] * sy_ + nrm[:, 1] * cy
    nz = nrm[:, 2]

    # project: screen u = rx ; v = ry*sinE + rz*cosE (v up)
    u = rx
    v = ry * SIN_E + rz * COS_E
    depth = ry * COS_E - rz * SIN_E  # larger = farther behind

    scale = px_per_voxel * SS
    if canvas is None:
        ext = max(abs(u).max(), abs(v).max()) + 2
        canvas = int(math.ceil(ext * 2 * px_per_voxel / 4.0) * 4 + 8)
    W = H = canvas * SS
    cx_px, cz_px = W / 2.0, H / 2.0 + z_lift * SS

    su = (u * scale + cx_px).astype(np.int32)
    sv = (cz_px - v * scale).astype(np.int32)

    shade = AMBIENT + (1 - AMBIENT) * np.clip(
        nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
    rgb = pal[cols] * shade[:, None]

    img = np.zeros((H, W, 4), dtype=np.float32)
    zbuf = np.full((H, W), 1e9, dtype=np.float32)
    r = int(math.ceil(scale / 2)) + 1
    order = np.argsort(-depth)  # far to near
    box = range(-r, r + 1)
    for i in order:
        x0, y0, d = su[i], sv[i], depth[i]
        xlo, xhi = max(x0 - r, 0), min(x0 + r + 1, W)
        ylo, yhi = max(y0 - r, 0), min(y0 + r + 1, H)
        if xlo >= xhi or ylo >= yhi:
            continue
        region = zbuf[ylo:yhi, xlo:xhi]
        mask = region > d
        region[mask] = d
        tgt = img[ylo:yhi, xlo:xhi]
        tgt[mask, 0] = rgb[i, 0]
        tgt[mask, 1] = rgb[i, 1]
        tgt[mask, 2] = rgb[i, 2]
        tgt[mask, 3] = 255
    out = Image.fromarray(img.astype(np.uint8), 'RGBA').resize(
        (W // SS, H // SS), Image.LANCZOS)
    return out, canvas


def main():
    args = sys.argv[1:]
    vxl_path, outdir = args[0], args[1]
    opts = {'--frames': '32', '--px-per-voxel': '6', '--yaw0': '0',
            '--team-green': '0,200,0', '--z-lift': '0', '--canvas': '0'}
    i = 2
    while i < len(args):
        opts[args[i]] = args[i + 1]
        i += 2
    frames = int(opts['--frames'])
    ppv = float(opts['--px-per-voxel'])
    yaw0 = float(opts['--yaw0'])
    zlift = float(opts['--z-lift'])
    tg = tuple(int(x) for x in opts['--team-green'].split(','))
    canvas = int(opts['--canvas']) or None

    model = parse_vxl(vxl_path)
    os.makedirs(outdir, exist_ok=True)
    # first pass with fixed canvas: find biggest extent over all frames
    if canvas is None:
        worst = 0
        for f in (0, frames // 4):
            _, c = render_frame(model, yaw0 + f * (360.0 / frames), ppv, tg, zlift)
            worst = max(worst, c)
        canvas = worst
    for f in range(frames):
        yaw = yaw0 + f * (360.0 / frames)  # CCW per classic frame order
        img, _ = render_frame(model, yaw, ppv, tg, zlift, canvas)
        img.save(os.path.join(outdir, f'frame-{f:04d}.png'))
    print(f'rendered {frames} frames, canvas {canvas}px -> {outdir}')


if __name__ == '__main__':
    main()
