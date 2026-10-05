"""
mcv2export.py - the MCV v2's 3D model as a .glb: every part as a node under the unit (facing east, the mod's frame
24), the meshes exact (each convex part cut from its planes and curved surfaces), vertex colours the frames' paint
(ochre, orange, the spine's greys and white, the dark track; house colour on the covers and panels: COLOR_1 white),
and the RA-grid camera that frames the mod's 384 canvas.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
Origin: the unit's position on the ground.

    python3 mcv2export.py out.glb
"""
import sys
import numpy as np
from export3d import GLB, orient
import rcexport as RX
import mcv2 as M, mcv2mat as MM
from mcv2cam import facing_cw, mod_to_cw, camera, PPU

UNITS_PER_CELL = 192.0 / PPU                # voxels per cell: the MCV's canvas has 192 px a cell, 6.1 px a voxel
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # model (x east, y south, z up) -> glTF (x east, y up, z south)
GROUPS = {}
for _g, _names in (('tracks', ('cover', 'lip', 'apron', 'skirt', 'skirt_in', 'undercover', 'belt_end', 'belt_top',
                               'belt_bottom', 'core', 'hub', 'road', 'road_hub')),
                   ('hull', ('hull', 'under', 'hull_side', 'bumper')),
                   ('right_deck', ('deck', 'rail', 'wall', 'block', 'block_back', 'block_side', 'opening', 'hpanel',
                                   'hatch')),
                   ('front_block', ('cab', 'cabstep', 'nose', 'vent', 'roof', 'cabhatch', 'step')),
                   ('spine', ('channel', 'pedestal', 'saddle', 'cap', 'housing', 'rib', 'boom_g', 'boom_w', 'collar',
                              'front', 'band', 'tip', 'pulley', 'sheave', 'ramp')),
                   ('crate_rack', ('ldeck', 'rack_in', 'rack_out', 'crate', 'lid', 'divider', 'lamp', 'lrail')),
                   ('cockpit', ('flblock', 'cabin', 'fltop', 'glass', 'bonnet', 'nose_front'))):
    for _n in _names:
        GROUPS[_n] = _g
# parts whose vertex colours vary across a face (two-tone paint, grime from the ground): subdivided
VARIED = (M.BLOCK, M.BOOM_W, M.BOOM_G, M.GLASS, M.CAB, M.NOSE, M.VISOR, M.CPLATE, M.HULL, M.UNDER, M.BUMPER, M.LDECK, M.DECK,
          M.CRATE, M.FLBLOCK, M.HITCH)


def subdivide(P, F, N, max_len=0.75):
    """split flat-shaded triangles (per-face vertices) at the midpoint of their longest edge until no edge is longer
    than max_len (voxels): the vertex colours then follow TS's colours across each face."""
    t = P[F]
    n = N[F[:, 0]]
    done_t, done_n = [], []
    while len(t):
        L = np.stack([np.linalg.norm(t[:, 1] - t[:, 0], axis=1), np.linalg.norm(t[:, 2] - t[:, 1], axis=1),
                      np.linalg.norm(t[:, 0] - t[:, 2], axis=1)], 1)
        k = L.argmax(1)
        ok = L.max(1) <= max_len
        done_t.append(t[ok]); done_n.append(n[ok])
        t, n, k = t[~ok], n[~ok], k[~ok]
        if not len(t):
            break
        # rotate each triangle so its longest edge is v0-v1, then split it at that edge's midpoint
        idx = np.stack([k, (k + 1) % 3, (k + 2) % 3], 1)
        r = np.take_along_axis(t, idx[:, :, None], 1)
        a, b, c = r[:, 0], r[:, 1], r[:, 2]
        m = (a + b) / 2
        t = np.concatenate([np.stack([a, m, c], 1), np.stack([m, b, c], 1)], 0)
        n = np.concatenate([n, n], 0)
    T = np.concatenate(done_t, 0); Nn = np.concatenate(done_n, 0)
    V = T.reshape(-1, 3); NV = np.repeat(Nn, 3, axis=0)
    # share the vertices a face's triangles have in common (same place, same face normal)
    key = np.concatenate([np.round(V * 1e4), np.round(NV * 1e3)], 1).astype(np.int64)
    uk, inv = np.unique(key, axis=0, return_inverse=True)
    first = np.zeros(len(uk), int); first[inv[::-1]] = np.arange(len(V))[::-1]
    return V[first], inv.reshape(-1, 3), NV[first]


def colours(part, V, N):
    """vertex colours (body frame V, N): the frames' paint for the part (albedo, no light), house green on house parts."""
    if part.comp in M.HOUSE:
        return np.tile(MM.GREEN, (len(V), 1)), np.ones(len(V))
    x = V[:, 0] + M.CX; y = M.CY - V[:, 1]; z = V[:, 2]
    base = np.tile(np.asarray(MM.PAINT.get(part.comp, MM.OCHRE), float), (len(V), 1))
    up = N[:, 2] > 0.55
    if part.comp == M.BLOCK:
        base[x < 5.6] = MM.ORANGE
    elif part.comp == M.BOOM_W:
        base[up] = MM.WHITE
    elif part.comp == M.BOOM_G:
        base[up] = MM.GREY * 1.12
    elif part.comp == M.CAB:
        base[(N[:, 0] > 0.7) & (x > 38.95) & (z < 7.45)] = MM.ORANGE
    elif part.comp == M.NOSE:
        f = N[:, 0] > 0.7
        base[f & (((z > 3.15) & (z < 4.0)) | ((z > 6.0) & (z < 6.75)))] = MM.ORANGE
    elif part.comp == M.VISOR:
        s_ = MM.phase(y, 1.0, 6.95) < 0.3
        base[s_] = MM.ORANGE
        base[~s_] = MM.OCHRE * 0.55
    elif part.comp == M.GLASS:
        t = np.clip((z - 5.15) / 2.45, 0, 1)
        base = np.array([28, 34, 42.]) * (1 - t)[:, None] + np.array([80, 94, 110.]) * t[:, None]
    elif part.comp == M.FRAME:
        base[:] = MM.ORANGE
    elif part.comp == M.GRILLE:
        base[:] = MM.BROWN * 0.55
    elif part.comp == M.CPLATE:
        base[(N[:, 2] < 0.3) & (z < 4.0)] = MM.ORANGE
    elif part.comp == M.WHEEL:
        base[np.abs(N[:, 1]) < 0.7] = MM.DARK * 1.1
    if part.comp in (M.HULL, M.UNDER, M.BUMPER, M.LDECK, M.DECK, M.CRATE, M.FLBLOCK, M.HITCH):
        d = np.clip((4.2 - z) / 3.4, 0, 1) * 0.45
        base = base * (1 - d[:, None]) + MM.GRIME * d[:, None]
    return np.minimum(base, 255.0), np.zeros(len(V))


def to_g_pos(p):
    return A @ np.asarray(p, float) / UNITS_PER_CELL


def quat(Rg):
    t = np.trace(Rg)
    if t > 0:
        q = np.array([Rg[2, 1] - Rg[1, 2], Rg[0, 2] - Rg[2, 0], Rg[1, 0] - Rg[0, 1], t + 1.0])
    else:
        i = int(np.argmax(np.diag(Rg))); j, k = (i + 1) % 3, (i + 2) % 3
        q = np.zeros(4); q[i] = Rg[i, i] - Rg[j, j] - Rg[k, k] + 1.0
        q[j] = Rg[j, i] + Rg[i, j]; q[k] = Rg[k, i] + Rg[i, k]; q[3] = Rg[k, j] - Rg[j, k]
    return q / np.linalg.norm(q)


class Tree(GLB):
    def __init__(self):
        super().__init__()
        self.children = {}

    def group(self, name, parent=None, rotation=(0, 0, 0, 1)):
        self.nodes.append(dict(name=name, rotation=[float(v) for v in rotation]))
        i = len(self.nodes) - 1
        if parent is not None:
            self.children.setdefault(parent, []).append(i)
        return i

    def part(self, name, parent, v, f, n, rgb, house):
        self.mesh(name, v, f, n, rgb, house)
        i = len(self.nodes) - 1
        self.children.setdefault(parent, []).append(i)

    def finish(self):
        for p, ch in self.children.items():
            self.nodes[p]['children'] = ch

    def save(self, path, extras=None):
        import json, struct
        child = {c for ch in self.children.values() for c in ch}
        roots = [i for i in range(len(self.nodes)) if i not in child]
        while len(self.buf) % 4:
            self.buf.append(0)
        gl = dict(asset=dict(version='2.0', generator='TS-to-RA HD (rcexport)'), scene=0,
                  scenes=[dict(nodes=roots, extras=extras or {})], nodes=self.nodes, meshes=self.meshes,
                  materials=self.materials, accessors=self.accessors, bufferViews=self.views,
                  buffers=[dict(byteLength=len(self.buf))])
        if getattr(self, 'cameras', None):
            gl['cameras'] = self.cameras
        js = json.dumps(gl, separators=(',', ':')).encode()
        while len(js) % 4:
            js += b' '
        out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(self.buf))
        out += struct.pack('<II', len(js), 0x4E4F534A) + js
        out += struct.pack('<II', len(self.buf), 0x004E4942) + bytes(self.buf)
        open(path, 'wb').write(out)


def export(path):
    glb = Tree()
    root = glb.group('MCV')
    Mx = facing_cw(mod_to_cw(24))                           # facing east
    Rg = A @ Mx @ A.T
    unit = glb.group('unit_facing_east', root, rotation=quat(Rg))
    groups = {}
    seen = {}
    nverts = 0
    for p in M.parts():
        m = RX.part_mesh(p)
        if m is None:
            continue
        V, F = m
        curved = any(c.kind != 'plane' for c in p.cons)
        if curved:
            V, F = RX.curved_mesh(p, n=24)
            P, Fi, N = RX.smooth_shaded(V, F)          # (one colour across a curved part: no need to subdivide)
        elif p.comp in VARIED:
            P, Fi, N = subdivide(*RX.flat_shaded(V, F), 1.0)
        else:
            P, Fi, N = RX.flat_shaded(V, F)
        rgb, house = colours(p, P, N)
        Pg = (P @ A.T) / UNITS_PER_CELL; Ng = N @ A.T
        Fi = orient(Pg, Fi, Ng)
        g = GROUPS.get(p.name, 'other')
        if p.name in ('frame', 'grille', 'lamp'):
            cy = M.CY - (p.sphere[0][1] if p.sphere is not None else 0.0)
            g = 'cockpit' if (cy > 18.5 and p.sphere[0][0] + M.CX > 30) else ('crate_rack' if p.name == 'lamp' else 'front_block')
        if g not in groups:
            groups[g] = glb.group(g, unit)
        seen[p.name] = seen.get(p.name, 0) + 1
        nm = p.name if seen[p.name] == 1 else '%s_%d' % (p.name, seen[p.name])
        glb.part(nm, groups[g], Pg.astype(np.float32), Fi, Ng.astype(np.float32), rgb, house)
        nverts += len(Pg)
    glb.finish()
    cam = camera()
    gx, gy = cam.ground(np.array([192.0]), np.array([192.0]))
    glb.camera('camera_ra_grid', 0.0, 32.0, list(to_g_pos([gx[0], gy[0], 0.0])), 1.0, 1.0,
               extras=dict(note='orthographic, 32 degrees above the ground, looking north; frames the 384 x 384 canvas'))
    glb.save(path, extras=dict(units='1.0 = one cell (128 px in the game; 192 px on the canvas)', facing='east'))
    return path, nverts


if __name__ == '__main__':
    print(export(sys.argv[1]))
