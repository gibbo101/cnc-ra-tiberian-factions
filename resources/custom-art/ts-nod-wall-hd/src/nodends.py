"""
Gate end pieces for the TS Nod wall: the Nod wall's joint block, from the cell edge on `side` 28 px into
the gate's end cell, so every gate (gates2/3/4) joins a Nod wall the same way it joins the GDI wall.
  ok         the joint block at full height with its drips
  damaged    chipped, cracked and scorched
  destroyed  a broken, lower stub
The S piece also draws the start of the Nod wall continuing south (it shows above the gate cell's bottom
edge), exactly like the GDI and BRIK S pieces. Same draw order: N piece, gate, then W / E / S pieces.
"""
import numpy as np
from scipy import ndimage
import walls2 as W
import gates2 as G2
import nodwall as N
from walls2 import smoothstep, sample, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
from damage import Sampler

SOOT = np.array([30, 29, 28.])
FRESH = np.array([168, 166, 160.])


class NodEndPiece(G2.Render):
    def __init__(self, side, state='ok', length=28.0):
        self.side, self.state, self.length = side, state, length
        self.setup_grid(128, 128)
        X, Y = self.X, self.Y
        P = N.P
        if side in 'WE':
            v = Y - 64.0
            d_edge = X if side == 'W' else 128.0 - X
        else:
            v = X - 64.0
            d_edge = Y if side == 'N' else 128.0 - Y
        a = np.abs(v)
        inside = a <= P['ta']
        block = np.where(d_edge <= length - 2.5, P['H'], P['H'] - 2.2 * (d_edge - (length - 2.5)))
        neighbour = P['zc'] + (P['H'] - P['zc']) * np.clip((64.0 + d_edge) / 64.0, 0, 1)   # the next cell's arm
        h = np.where(d_edge >= 0, block, neighbour)
        stub = inside & (d_edge <= length) & (d_edge >= -64)
        Hs = np.where(stub, np.maximum(h, 0), 0.0)
        if state == 'destroyed':
            rng = np.random.default_rng(31 + 'NESW'.index(side))
            n = ndimage.gaussian_filter(rng.standard_normal(Hs.shape), 2.0 * G2.SS, mode='wrap')
            n /= n.std()
            k = length - d_edge                                   # distance back from the inner end
            keep = smoothstep(2, 16, k + 5 * n - 4)
            Hs = np.where(stub & (d_edge >= 0), Hs * (0.4 + 0.6 * keep), Hs)
        if state == 'damaged':
            rng = np.random.default_rng(41 + 'NESW'.index(side))
            n = ndimage.gaussian_filter(rng.standard_normal(Hs.shape), 2.4 * G2.SS, mode='wrap')
            n /= n.std()
            edge_band = (np.abs(a - P['ta']) < 3.5) | (d_edge > length - 5)
            chip = smoothstep(0.9, 1.4, n) * edge_band * (d_edge > 3) * (d_edge >= 0)
            Hs = np.where(stub, np.maximum(Hs - 6.0 * chip, 0), Hs)
        self.Hs = Hs
        self.Cs = np.where(stub, 1, 0).astype(np.int8)
        self.d_edge, self.vv = d_edge, v
        self.slot_depth = 0.0
        self.finish_geometry()

    def render(self):
        hit, zh, comp, ptop_hit, gj, gi, rows = self.raycast()
        x, y = self.X[gj, gi], self.Y[gj, gi]
        nx, ny, nz = self.hf_normals(self.Hs, gj, gi)
        sh = self.shadows(hit, zh, gj, gi)
        ndl = np.clip(nx * W.LIGHT[0] + ny * W.LIGHT[1] + nz * W.LIGHT[2], 0, None)
        shade = W.AMBIENT + W.SKY * (0.5 + 0.5 * nz) + W.DIFFUSE * ndl * (1 - 0.85 * sh)
        top_like = nz > 0.8
        ew_face = np.abs(ny) >= np.abs(nx)
        tu = np.where(top_like | ew_face, x, y)
        tv = np.where(top_like, y, zh * 0.35)
        grain = sample(NOISE_FINE, tu, tv) * 0.045 + sample(NOISE_MOTTLE, tu, tv) * 0.07
        albedo = N.CONC * (1 + grain)[..., None]
        top_h = self.Hs[gj, gi]
        below = np.clip(top_h - zh, 0, None)
        face_h = np.maximum(top_h, 1.0)
        # the joint block's two drips each side of the joint, as on the wall itself
        dj = np.abs(self.d_edge[gj, gi])
        drip = np.zeros_like(x)
        for k, (pos, wid) in enumerate(((6.0, 1.3), (17.0, 1.6))):
            hsh = np.mod(np.sin((3 + 'NESW'.index(self.side) + 1.7 * k + 3 * (self.d_edge[gj, gi] < 0)) * 12.9898) * 43758.5453, 1.0)
            length = 0.45 + 0.4 * hsh
            core = 1 - smoothstep(wid * 0.4, wid, np.abs(dj - (pos + 2.5 * (hsh - 0.5))))
            tip = 1 - smoothstep(0.6 * length, length, below / face_h)
            drip = np.maximum(drip, core * tip)
        drip = drip * ~top_like * smoothstep(0.5, 2.0, below + 2.0 * (below > 0.3))
        albedo = albedo * (1 - 0.85 * drip[..., None]) + N.DRIP * (0.85 * drip)[..., None]
        lip = (1 - smoothstep(0.4, 1.8, below)) * ~top_like
        albedo = albedo * (1 + 0.22 * lip)[..., None]
        seam = (1 - smoothstep(0.3, 1.2, dj)) * 1.0
        albedo = albedo * (1 - seam[..., None]) + N.SEAM * seam[..., None]
        if self.state in ('damaged', 'destroyed'):
            rng = np.random.default_rng(97)
            S_crack, S_cmask, S_rough, S_soot = Sampler(rng, 8.0), Sampler(rng, 12.0), Sampler(rng, 1.2), Sampler(rng, 5.0)
            bu, bv = tu % 256, tv % 256
            cn = S_crack(bu, bv) + 0.10 * S_rough(bu, bv)
            crack = (1 - smoothstep(0.015, 0.06, np.abs(cn))) * smoothstep(0.3, 0.6, S_cmask(bu, bv))
            albedo *= (1 - 0.6 * crack)[..., None]
            k = self.length - self.d_edge[gj, gi]
            heavy = self.state == 'destroyed'
            s = np.exp(-(k / (14.0 if heavy else 10.0)) ** 2) * (0.6 + 0.4 * S_soot(bu, bv))
            soot = smoothstep(0.2, 0.9, np.clip(s, 0, 1)) * (0.7 if heavy else 0.5)
            albedo = albedo * (1 - soot[..., None]) + SOOT * soot[..., None]
            if heavy:
                brk = (k < 14) & (self.d_edge[gj, gi] >= 0) & (top_h < N.P['H'] - 2)
                fresh = FRESH * np.clip(0.84 + 0.1 * S_rough(bu, bv), 0.6, 1.0)[..., None]
                albedo = np.where((brk & top_like)[..., None], albedo * 0.5 + fresh * 0.5, albedo)
        grime = np.clip(1 - zh / 12.0, 0, 1) ** 1.6 * np.clip(0.5 + 0.35 * sample(NOISE_GRIME, tu, tv), 0, 1)
        albedo = albedo * (1 - grime[..., None]) + N.GRIME * grime[..., None]
        ao = 0.78 + 0.22 * np.clip(zh / N.P['H'], 0, 1)
        col = albedo * (shade * ao)[..., None]
        band = (self.d_edge <= self.length + 3)
        ga = self.ground_alpha(rows, gi, clip_mask=band.astype(float))
        img, _ = self.compose(hit, col, ga, np.zeros(hit.shape), ring_alpha=0.55)
        return img


if __name__ == '__main__':
    import os
    os.makedirs('gates/out2', exist_ok=True)
    for side in 'NESW':
        for st in ('ok', 'damaged', 'destroyed'):
            NodEndPiece(side, st).render().save(f'gates/out2/end-nod-{side}-{st}.png')
            print('end', side, st, flush=True)
