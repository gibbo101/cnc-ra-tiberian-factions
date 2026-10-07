"""
nvox.py - a TS voxel unit that is new to the mod, drawn from a small config (each unit's <name>spec.py): its VXL
sections posed by their HVAs, the RA-grid camera (orthographic, 32 degrees above the ground, looking north), 6.25
canvas px per voxel, the unit's position (TS's HVA origin) on the canvas: (192, 191) on a 384 canvas, and on a canvas
grown evenly on both sides, still at the centre ((W - 384) / 2 further right and down).

Ground units sit on the ground: TS's voxels that float above (or dip below) the HVA origin are moved so the lowest
voxel touches it (gz).  Aircraft keep the voxel's origin where it is, with no shadow, no grime and no ground occlusion.

    python3 nvox.py SPEC frames 0,8,16,24 [ss] [outdir]
"""
import os, sys, time, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR

ELEV = 32.0
TSN = float(os.environ.get('TSN', '0.6'))


class Cfg:
    """folder: the hand-off folder ('02-BIKE'); parts: [(VXL name, HVA name or None, extra (R, t) or None)];
    name: the frame prefix ('tsbike'); canvas: (W, H); aircraft: True for a flier; gz: 'auto' to put the lowest
    voxel on the ground, a number to lower by, or 0."""

    def __init__(self, folder, parts, name, canvas=(384, 384), ppu=6.25, aircraft=False, gz='auto', bounds=None,
                 shadow_len=1.0, grime_z=3.0, origin=None):
        self.folder, self.parts, self.name = folder, parts, name
        self.canvas, self.ppu, self.aircraft = tuple(canvas), ppu, aircraft
        self.gz_spec = 0.0 if aircraft else gz
        W, H = self.canvas
        self.origin = origin or (192.0 + (W - 384) / 2.0, 191.0 + (H - 384) / 2.0)
        self.bounds = bounds or (((-60, 60), (-60, 60), (-5, 40)) if aircraft else ((-45, 45), (-45, 45), (-25, 35)))
        self.shadow_len, self.grime_z = shadow_len, grime_z
        self.gz = None

    def dir(self):
        from paths import HANDOFF
        return os.path.join(HANDOFF, self.folder, 'ts-original') + '/'


def load(cfg):
    D = cfg.dir()
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    sections, mats, extra = [], [], []
    for vname, hname, ex in cfg.parts:
        secs = vxl.read_vxl(D + vname)
        names, M = vxl.read_hva(D + (hname or vname[:-4] + '.HVA'))
        for i, s in enumerate(secs):
            sections.append(VU.Section(s, pal, sigma=0.3, denoise=0.3))
            mats.append((M, i))
            extra.append(ex)
    u = VR.Unit(sections, mats)
    u.palette = pal
    if cfg.gz is None:
        cfg.gz = lowest(u) if cfg.gz_spec == 'auto' else float(cfg.gz_spec)
    u.extra_pose = [((ex[0] if ex else np.eye(3)), (np.asarray(ex[1], float) if ex else np.zeros(3)) - np.array([0, 0, cfg.gz]))
                    for ex in extra]
    return u


def lowest(u, hf=0):
    """the lowest voxel's bottom (unit frame z, voxels) over all sections, posed (before any lowering)."""
    z = []
    for i, s in enumerate(u.sections):
        R, t = u.pose(i, hf) if u.extra_pose is None else _raw_pose(u, i, hf)
        I = np.argwhere(s.col >= 0).astype(float)
        for dz in (0.0, 1.0):
            for dx in (0.0, 1.0):
                for dy in (0.0, 1.0):
                    loc = s.mn + (I + np.array([dx, dy, dz])) * s.scale
                    z.append((R @ loc.T + t[:, None])[2].min())
    return float(min(z))


def _raw_pose(u, i, hf):
    ep, u.extra_pose = u.extra_pose, None
    try:
        return u.pose(i, hf)
    finally:
        u.extra_pose = ep


def camera(cfg):
    return RR.Cam((0, -1), ELEV, cfg.ppu, cfg.origin)


def frame(cfg, unit, k, ss=4, sky=True):
    if cfg.aircraft:
        return VR.frame(unit, k, 0, camera(cfg), cfg.canvas, cfg.bounds, ss=ss, sky=sky, px_scale=1.5,
                        sharp={i: 2.0 for i in range(len(unit.sections))}, speckle=(0.75, 1.2), grime_z=0,
                        ts_normals=TSN, with_shadow=False, ground_ao=False)
    return VR.frame(unit, k, 0, camera(cfg), cfg.canvas, cfg.bounds, ss=ss, sky=sky, shadow_len=cfg.shadow_len,
                    px_scale=1.5, sharp={i: 2.0 for i in range(len(unit.sections))}, speckle=(0.75, 1.2),
                    grime_z=cfg.grime_z, ts_normals=TSN, with_shadow=True)


def to_unit(cfg, unit, sec, I, hf=0):
    """index-space points of section sec -> the unit frame (voxels, after lowering)."""
    s = unit.sections[sec]
    R, t = unit.pose(sec, hf)
    return (R @ (s.mn + np.asarray(I, float) * s.scale).T).T + t


def project(cfg, p_unit, facing):
    Mx = VR.facing_cw(VR.mod_to_cw(facing))
    x, y = camera(cfg).project(Mx @ np.asarray(p_unit, float))
    return float(x), float(y)


def flh_point(cfg, flh):
    """TS's FLH (leptons: forward, lateral (to the right), height) as a unit-frame point at this canvas's scale (192
    canvas px a cell, 256 leptons a cell)."""
    lep = (192.0 / 256.0) / cfg.ppu
    return np.array([flh[0], -flh[1], flh[2]], float) * lep


if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())
    spec = importlib.import_module(sys.argv[1])
    ks = [int(a) for a in sys.argv[3].split(',')]
    ss = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    out = sys.argv[5] if len(sys.argv) > 5 else 'out'
    os.makedirs(out, exist_ok=True)
    from frameio import save
    u = spec.load()
    for k in ks:
        t0 = time.time()
        img, trim = spec.frame(u, k, ss, True)
        save(img, trim, '%s/%s-%04d.png' % (out, spec.NAME, k))
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)


# ---------------------------------------------------------------------------------------------- spec helpers
def ref(cfg, u, k):
    """TS's voxels drawn as they are, frame k (the previews' left column)."""
    import tsvox
    return tsvox.splat(u, u.palette, k, camera(cfg), cfg.canvas)


FACING_NAMES = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']


def muzzle_table(cfg, header, cols, frames=32, facing_of=None):
    """muzzle.txt: header lines, then for each frame the canvas px of each (label, unit-frame point)."""
    lines = list(header) + ['', 'frame  facing  ' + '  '.join('%17s' % lab for lab, _ in cols)]
    lines.append('               ' + '  '.join('%8s %8s' % ('x', 'y') for _ in cols))
    for k in range(frames):
        f = facing_of(k) if facing_of else k
        row = '%5d  %6s  ' % (k, FACING_NAMES[f // 4] if f % 4 == 0 else '')
        row += '  '.join('%8.1f %8.1f' % project(cfg, p, f) for _, p in cols)
        lines.append(row)
    return '\n'.join(lines) + '\n'


def readme(cfg, title, ts_name, vxl_desc, ea_refs='', **over):
    """the README dict for npackage's template, with this unit's defaults."""
    W, H = cfg.canvas
    n = cfg.name
    grown = '' if (W, H) == (384, 384) else ' (grown from 384 x 384 so every facing fits)'
    R = dict(
        title=title, ts_name=ts_name, mod_name=n.upper(),
        frames="""frames/     %s-0000.png ... %s-0031.png, 32 frames on a %d x %d canvas%s, each with a -trim.png
            (white = house colour, antialiased): 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)%s""" % (
            n, n, W, H, grown, ', no shadow' if cfg.aircraft else ', each with its shadow'),
        previews="""previews/   8-facings.png    TS's voxels drawn as they are, beside HD, every 4th facing
            turn.gif         the 32 facings in turn, TS's voxels beside HD
            scale.png        %s""" % ('next to the Orca Fighter (HD), the HD harvester and EA\'s TD Orca, as the game draws them'
                                     if cfg.aircraft else 'next to the HD harvester and the Devil\'s Tongue, as the game draws them'),
        vxl=vxl_desc,
        look=_look(cfg),
        shadow=_shadow(cfg),
        glb_nodes='', glb_nodes_long='', judgement='', extra='', muzzle_line='')
    R.update(over)
    return R


def _look(cfg):
    W, H = cfg.canvas
    ox, oy = cfg.origin
    if cfg.aircraft:
        return ("""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; %.2f canvas px per voxel, the
  voxel's origin (TS's HVA origin) at canvas (%g, %g): the scale and place the hand-off gives (the Orca Fighter's).""" % (
            cfg.ppu, ox, oy))
    gz = cfg.gz
    if abs(gz) < 0.02:
        tail = "TS's lowest voxels already sit on the ground."
    elif gz > 0:
        tail = ("TS's voxels sit %.2f voxels above the HVA origin (the lowest voxels), so the model is lowered onto the\n"
                "  ground (by %.1f px): it stands on the ground and the shadow meets it." % (gz, gz * cfg.ppu * 0.848))
    else:
        tail = ("TS's lowest voxels dip %.2f voxels below the HVA origin, so the model is raised onto the ground (by\n"
                "  %.1f px)." % (-gz, -gz * cfg.ppu * 0.848))
    return ("""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; %.2f canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (%g, %g) on the ground: the scale and place the hand-off gives (the
  GDI voxel units').  %s""" % (cfg.ppu, ox, oy, tail))


def _shadow(cfg):
    if cfg.aircraft:
        return ("""None baked: in flight the game lifts the frame by the aircraft's height and draws its shadow from the same
frame, darkened, on the ground.  The outline is the units' dark outline, so the silhouette reads as a shadow too.""")
    return ("""Every frame has the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little towards the
camera, as long as the buildings', the harvester's and the Devil's Tongue's.  Within 14 px of the canvas edge it fades
out.""")
