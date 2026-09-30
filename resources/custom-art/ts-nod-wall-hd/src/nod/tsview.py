"""Tiny Tiberian Sun isometric renderer for testing 3D hypotheses against the NTWALL sprites.

World: e = east, s = south, z = up, in cells, origin = cell ground centre.
TS screen (48x48 frame): x = 24 + 24(e - s), y = 36 + 12(e + s) - 29.4 z.
Solids are unions of convex pieces given as lists of half-spaces a.p <= b (p = (e, s, z)).
"""
import numpy as np
from PIL import Image, ImageDraw

ZS = 29.4


def box(e0, e1, s0, s1, z0, z1):
    return [((-1, 0, 0), -e0), ((1, 0, 0), e1), ((0, -1, 0), -s0), ((0, 1, 0), s1), ((0, 0, -1), -z0), ((0, 0, 1), z1)]


def render(pieces, S=4, zmax=1.2, dz=None, light=(-0.55, -0.35, 0.75)):
    n = 48 * S
    xs = (np.arange(n) + 0.5) / S
    X, Y = np.meshgrid(xs, xs)
    es = (X - 24) / 24.0
    dz = dz or 1.0 / (ZS * S * 2)
    hit = np.zeros((n, n), bool)
    zh = np.zeros((n, n)); ph = np.full((n, n), -1)
    for z in np.arange(zmax, -1e-9, -dz):
        ep = (Y - 36 + ZS * z) / 12.0
        e = (ep + es) / 2; s = (ep - es) / 2
        for k, pc in enumerate(pieces):
            inside = ~hit
            for (a, b) in pc:
                inside &= (a[0] * e + a[1] * s + a[2] * z) <= b + 1e-9
            if inside.any():
                zh[inside] = z; ph[inside] = k; hit |= inside
    # 3D points for normals
    ep = (Y - 36 + ZS * zh) / 12.0
    E = (ep + es) / 2; Sx = (ep - es) / 2
    P = np.dstack([E, Sx, zh])
    dx = np.gradient(P, axis=1); dy = np.gradient(P, axis=0)
    N = np.cross(dx, dy)
    N /= np.linalg.norm(N, axis=-1, keepdims=True) + 1e-9
    N = np.where((N[..., 2:3] < 0), -N, N)          # face the camera-ish
    L = np.array(light); L = L / np.linalg.norm(L)
    sh = 0.25 + 0.75 * np.clip((N * L).sum(-1), 0, 1)
    return hit, zh, ph, sh


def overlay(ref_path, pieces, S=8, title=''):
    hit, zh, ph, sh = render(pieces, S=S // 2 if S > 4 else S)
    ref = Image.open(ref_path).convert('RGBA').resize((48 * S, 48 * S), Image.NEAREST)
    bg = Image.new('RGBA', ref.size, (90, 100, 80, 255)); bg.alpha_composite(ref)
    m = Image.fromarray((hit * 255).astype(np.uint8)).resize(ref.size, Image.NEAREST)
    mm = np.array(m) > 127
    edge = mm ^ np.roll(mm, 1, 0) | mm ^ np.roll(mm, 1, 1)
    a = np.array(bg)
    a[edge] = [255, 40, 200, 255]
    out = Image.fromarray(a)
    # shaded model view next to it
    g = (sh * 200 + 30) * hit
    mv = Image.fromarray(np.dstack([g, g, g, np.full(g.shape, 255)]).astype(np.uint8)).resize(ref.size, Image.NEAREST)
    mvb = Image.new('RGBA', ref.size, (90, 100, 80, 255))
    mvb.paste(mv, (0, 0), Image.fromarray((hit * 255).astype(np.uint8)).resize(ref.size, Image.NEAREST))
    c = Image.new('RGBA', (ref.width * 2 + 6, ref.height), (30, 30, 30, 255))
    c.paste(out, (0, 0)); c.paste(mvb, (ref.width + 6, 0))
    ImageDraw.Draw(c).text((4, 4), title, fill=(255, 255, 0, 255))
    return c


def iou(ref_path, pieces, S=4):
    hit = render(pieces, S=S)[0]
    ref = np.array(Image.open(ref_path).convert('RGBA'))[..., 3] > 0
    ref = np.kron(ref, np.ones((S, S), bool))
    return (hit & ref).sum() / max((hit | ref).sum(), 1)
