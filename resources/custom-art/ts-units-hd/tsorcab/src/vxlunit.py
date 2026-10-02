"""
vxlunit.py - a TS voxel unit (VXL sections, posed by an HVA) as convex parts for the rc ray caster, built straight
from the voxels: each section's filled voxels merged into boxes (every step TS has, exactly), shaded with normals
from the section's solid smoothed a little (so its edges read rounded and the joins between its boxes vanish),
coloured with TS's own palette colours of the voxels at each point, house colour where TS's remap voxels are.

A Section holds one VXL section: its voxel grid, its boxes, its smoothed field and its colour volume.  Coordinates:
'index space' has voxel (i, j, k) spanning i..i+1 etc.; the section's local space is min + index * scale; the HVA
frame maps local space to the unit's frame (x forward, y left, z up): p = R local + t * det.
"""
import numpy as np
from scipy import ndimage
import rc

HOUSE_LO, HOUSE_HI = 16, 31


def greedy_boxes(solid):
    """cover the True voxels of a 3D bool grid with axis-aligned boxes (inclusive index ranges), greedily: grow
    along x, then y, then z."""
    S = solid.copy()
    X, Y, Z = S.shape
    out = []
    for k in range(Z):
        for j in range(Y):
            i = 0
            while i < X:
                if not S[i, j, k]:
                    i += 1
                    continue
                i1 = i
                while i1 + 1 < X and S[i1 + 1, j, k]:
                    i1 += 1
                j1 = j
                while j1 + 1 < Y and S[i:i1 + 1, j1 + 1, k].all():
                    j1 += 1
                k1 = k
                while k1 + 1 < Z and S[i:i1 + 1, j:j1 + 1, k1 + 1].all():
                    k1 += 1
                S[i:i1 + 1, j:j1 + 1, k:k1 + 1] = False
                out.append((i, i1, j, j1, k, k1))
                i = i1 + 1
    return out


class Section:
    def __init__(self, sec, pal, sigma=0.55, fill=True, denoise=0.0, dn_sigma=0.8):
        self.name = sec['name']
        self.col = sec['col']
        self.size = np.array(sec['size'])
        self.mn = np.asarray(sec['min'], float)
        self.scale = (np.asarray(sec['max'], float) - self.mn) / self.size
        self.det = sec['det']
        filled = self.col >= 0
        self.solid = ndimage.binary_fill_holes(filled) if fill else filled
        self.boxes = greedy_boxes(self.solid)
        pad = 2
        F = ndimage.gaussian_filter(np.pad(self.solid.astype(np.float32), pad), sigma)
        self.pad = pad
        self.grad = np.stack(np.gradient(F), -1)                       # (X+2p, Y+2p, Z+2p, 3), index space
        house = (self.col >= HOUSE_LO) & (self.col <= HOUSE_HI)
        P = np.asarray(pal, np.float32)
        self.rgb = np.where(filled[..., None], P[np.clip(self.col, 0, 255)], 0.0).astype(np.float32)
        self.wcol = (filled & ~house).astype(np.float32)
        if denoise > 0:
            # TS speckles its paint voxel by voxel: mix each voxel's colour with its coloured neighbours'
            wb = ndimage.gaussian_filter(self.wcol, dn_sigma) + 1e-4
            blur = np.stack([ndimage.gaussian_filter(self.rgb[..., c] * self.wcol, dn_sigma) / wb for c in range(3)], -1)
            self.rgb = np.where(self.wcol[..., None] > 0, (1 - denoise) * self.rgb + denoise * blur, self.rgb).astype(np.float32)
        self.whouse = house.astype(np.float32)
        # the colour round each voxel (its luminance, blurred over its coloured neighbours): TS's single dark or
        # light voxels are held near it
        lum = self.rgb.mean(-1) * self.wcol
        wb = ndimage.gaussian_filter(self.wcol, 1.5) + 1e-4
        self.lmean = (ndimage.gaussian_filter(lum, 1.5) / wb).astype(np.float32)
        # TS draws detail on its house-colour parts with the remap ramp's shades (16 light .. 31 dark): each house
        # voxel's shade against the shade round it, so the house green keeps its base brightness over a face and its
        # seams, vents and edges show darker or lighter
        hl = np.where(house, P[np.clip(self.col, 0, 255)].max(-1), 0.0).astype(np.float32)
        hw = ndimage.gaussian_filter(self.whouse, 1.5) + 1e-4
        hm = ndimage.gaussian_filter(hl, 1.5) / hw
        self.hshade = np.where(house, np.clip(hl / np.maximum(hm, 1e-3), 0.5, 1.2), 1.0).astype(np.float32)
        # TS's own normal per voxel (the artist's shading: bevels, vents, rounded hulls), in index-space axes
        # (RA2's voxels use normal mode 4, 244 normals: ra2normals.py; TS's mode 2, 36: tsnormals.py)
        if sec.get('normal_mode', 2) == 4:
            from ra2normals import NORMALS as TABLE
        else:
            from tsnormals import TS_NORMALS as TABLE
        nrm = np.clip(sec['nrm'], 0, len(TABLE) - 1)
        self.tsn = np.where(filled[..., None], TABLE[nrm], 0.0).astype(np.float32)

    # ------------------------------------------------------------------ geometry
    def _air(self, i0, i1, j0, j1, k0, k1):
        """True where the index range (clipped to the grid) holds no solid voxel; outside the grid is air."""
        X, Y, Z = self.solid.shape
        a0, a1 = max(i0, 0), min(i1, X - 1); b0, b1 = max(j0, 0), min(j1, Y - 1); c0, c1 = max(k0, 0), min(k1, Z - 1)
        if a0 > a1 or b0 > b1 or c0 > c1:
            return True
        return not self.solid[a0:a1 + 1, b0:b1 + 1, c0:c1 + 1].any()

    def box_info(self, b):
        """which of a box's six faces are exposed (fully open to air) and which of its twelve edges are convex
        edges of the solid (both faces exposed and the voxels beyond the edge empty)."""
        i0, i1, j0, j1, k0, k1 = b
        lo = (i0, j0, k0); hi = (i1, j1, k1)
        rng = [(i0, i1), (j0, j1), (k0, k1)]
        faces = {}
        for ax in range(3):
            for sgn in (-1, 1):
                r = [list(x) for x in rng]
                v = (lo[ax] - 1) if sgn < 0 else (hi[ax] + 1)
                r[ax] = [v, v]
                faces[(ax, sgn)] = self._air(r[0][0], r[0][1], r[1][0], r[1][1], r[2][0], r[2][1])
        edges = {}
        for a1 in range(3):
            for a2 in range(a1 + 1, 3):
                for s1 in (-1, 1):
                    for s2 in (-1, 1):
                        if not (faces[(a1, s1)] and faces[(a2, s2)]):
                            continue
                        r = [list(x) for x in rng]
                        r[a1] = [(lo[a1] - 1) if s1 < 0 else (hi[a1] + 1)] * 2
                        r[a2] = [(lo[a2] - 1) if s2 < 0 else (hi[a2] + 1)] * 2
                        if self._air(r[0][0], r[0][1], r[1][0], r[1][1], r[2][0], r[2][1]):
                            edges[(a1, s1, a2, s2)] = True
        return faces, edges

    def parts(self, R, t, comp, name=None, chamfer=0.3):
        """the section's boxes as rc parts in the unit's frame, posed by (R, t) (t already scaled by det): each box
        cut at 45 degrees along the solid's convex edges only, so joins between boxes leave no grooves; each part
        remembers which of its planes face the air (for the shading's rounded edges)."""
        out = []
        axes = R / np.linalg.norm(R, axis=0, keepdims=True)
        A = R * self.scale[None, :]
        if not hasattr(self, '_info'):
            self._info = [self.box_info(b) for b in self.boxes]
        for b, (faces, edges) in zip(self.boxes, self._info):
            i0, i1, j0, j1, k0, k1 = b
            lo = np.array([i0, j0, k0], float); hi = np.array([i1 + 1, j1 + 1, k1 + 1], float)
            c = A @ ((lo + hi) / 2) + R @ self.mn + t
            h = (hi - lo) / 2 * self.scale
            cons = []; exposed = []
            for ax in range(3):
                for sgn in (-1, 1):
                    n = sgn * axes[:, ax]
                    cons.append(rc.Plane(n, n @ c + h[ax])); exposed.append(faces[(ax, sgn)])
            for (a1, s1, a2, s2) in edges:
                ch = min(chamfer, h[a1] * 1.2, h[a2] * 1.2)
                n = s1 * axes[:, a1] + s2 * axes[:, a2]; n = n / np.linalg.norm(n)
                cons.append(rc.Plane(n, n @ c + (h[a1] + h[a2] - ch) / np.sqrt(2.0))); exposed.append(True)
            p = rc.Part(cons, comp, name or self.name, sphere=(c, float(np.linalg.norm(h)) + 1e-3))
            p.exposed = np.array(exposed)
            p.box = b
            out.append(p)
        return out

    def to_index(self, P, R, t):
        """unit-frame points -> index space."""
        loc = np.linalg.solve(R, (P - t).T).T
        return (loc - self.mn) / self.scale

    def normal(self, I, R):
        """the smoothed solid's outward normal at index-space points I, in the unit frame."""
        g = trilinear(self.grad, I + self.pad - 0.5)
        n_idx = -g
        n = (R @ (n_idx / self.scale).T).T
        return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)

    # ------------------------------------------------------------------ colour
    def sample(self, I, nI, sharp=1.0, depth=3):
        """TS's colour across the face at index-space points I with face normals nI (index space): (rgb, weight of
        coloured voxels, weight of house voxels)."""
        N = nI
        k = np.argmax(np.abs(N), axis=-1)
        s = np.sign(N[np.arange(len(N)), k]); s[s == 0] = 1
        out = np.zeros((len(I), 3), np.float32); wout = np.zeros(len(I), np.float32)
        hout = np.zeros(len(I), np.float32); mout = np.zeros(len(I), np.float32); sout = np.ones(len(I), np.float32)
        nout = np.zeros((len(I), 3), np.float32)
        todo = np.ones(len(I), bool)
        dims = self.size
        for d in range(depth):
            idx = np.nonzero(todo)[0]
            if not len(idx):
                break
            p = I[idx]; kk = k[idx]; ss = s[idx]
            lay = np.floor(p[np.arange(len(p)), kk] - ss * (0.35 + d)).astype(int)
            a1 = (kk + 1) % 3; a2 = (kk + 2) % 3
            u = p[np.arange(len(p)), a1] - 0.5; v = p[np.arange(len(p)), a2] - 0.5
            u0 = np.floor(u).astype(int); v0 = np.floor(v).astype(int)
            fu = _sharp(u - u0, sharp); fv = _sharp(v - v0, sharp)
            acc = np.zeros((len(p), 3), np.float32); wacc = np.zeros(len(p), np.float32); hacc = np.zeros(len(p), np.float32)
            macc = np.zeros(len(p), np.float32); sacc = np.zeros(len(p), np.float32)
            nacc = np.zeros((len(p), 3), np.float32)
            rows = np.arange(len(p))
            for du, wu in ((0, 1 - fu), (1, fu)):
                for dv, wv in ((0, 1 - fv), (1, fv)):
                    J = np.zeros((len(p), 3), int)
                    J[rows, kk] = lay; J[rows, a1] = u0 + du; J[rows, a2] = v0 + dv
                    ok = np.all((J >= 0) & (J < dims[None, :]), axis=1)
                    Jc = np.clip(J, 0, dims[None, :] - 1)
                    w = wu * wv * ok
                    wc = w * self.wcol[Jc[:, 0], Jc[:, 1], Jc[:, 2]]
                    wh = w * self.whouse[Jc[:, 0], Jc[:, 1], Jc[:, 2]]
                    acc += wc[:, None] * self.rgb[Jc[:, 0], Jc[:, 1], Jc[:, 2]]
                    macc += wc * self.lmean[Jc[:, 0], Jc[:, 1], Jc[:, 2]]
                    sacc += wh * self.hshade[Jc[:, 0], Jc[:, 1], Jc[:, 2]]
                    nacc += (wc + wh)[:, None] * self.tsn[Jc[:, 0], Jc[:, 1], Jc[:, 2]]
                    wacc += wc; hacc += wh
            got = (wacc + hacc) > 0.15
            sel = idx[got]
            tot = (wacc + hacc)[got]
            out[sel] = np.where(wacc[got, None] > 1e-6, acc[got] / np.maximum(wacc[got], 1e-6)[:, None], 0.0)
            mout[sel] = macc[got] / np.maximum(wacc[got], 1e-6)
            sout[sel] = np.where(hacc[got] > 1e-6, sacc[got] / np.maximum(hacc[got], 1e-6), 1.0)
            nn = nacc[got]; nout[sel] = nn / (np.linalg.norm(nn, axis=1, keepdims=True) + 1e-6)
            wout[sel] = wacc[got] / tot
            hout[sel] = hacc[got] / tot
            todo[sel] = False
        return out, wout, hout, mout, sout, nout


def _sharp(f, s):
    if s <= 1.0:
        return f
    return np.clip((f - 0.5) * s + 0.5, 0.0, 1.0)


def trilinear(G, Q):
    """sample a (X, Y, Z, C) grid at continuous index points Q (cell centres at integers)."""
    X, Y, Z = G.shape[:3]
    q0 = np.floor(Q).astype(int); f = Q - q0
    out = np.zeros((len(Q), G.shape[3]), np.float32)
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                ix = np.clip(q0[:, 0] + dx, 0, X - 1); iy = np.clip(q0[:, 1] + dy, 0, Y - 1); iz = np.clip(q0[:, 2] + dz, 0, Z - 1)
                out += w[:, None] * G[ix, iy, iz]
    return out
