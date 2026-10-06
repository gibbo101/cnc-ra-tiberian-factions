"""
jtrender.py - the Juggernaut's walk frames (TSJUGG 0-119) on the Titan's legs, and the lighting the Titan's legs get in
every frame they are in (the walk, the deploy, the deployed piece):

  - the Juggernaut's own parts as jrender.py draws them (its camera, canvas, light, sky, materials, fill, shadow);
  - the Titan's legs as the HD Titan's leg frames draw them (titanrender.leg_frame): lit on their own, taking shadow
    and sky cover from the legs only (TS lights its leg sprite on its own, and below the body JUGGER's pixels are
    MMCH's), with the Titan's paint and highlight, their edges left sharp;
  - the Titan's waist under the body in the body's shadow and cover (the Titan's: it reads dark, as TS's does).

    python3 jtrender.py frames 0,30,60 [ss] [outdir] [sky]
"""
import os, sys, time
import numpy as np
from PIL import Image
import rcrender as RR
import jugg as JG
import jrender as JR
import jtlegs as TL
import jtwalker as TW
from frameio import save

HERE = os.path.dirname(os.path.abspath(__file__))
WALK = os.path.join(HERE, 'fit_walk_e.json')
HOUSE_COMPS = JR.HOUSE_COMPS


def setup(parts, cam, canvas, win, bounds, ss):
    """the render of all the parts, its own shadow map and sky made from the Titan's parts only (the legs' light)."""
    legs = [p for p in parts if p.comp in TL.COMPS]
    r = RR.RCRender(parts, cam, canvas, win, bounds, ss=ss, frames=TL.frames_of(parts),
                    occluders=legs if legs else None, shadow_len=JR.SHADOW_LEN, px_scale=JR.PX_SCALE)
    r.all_parts = parts
    return r


def lighting(r, sky):
    """(shadow_extra, sky occlusion): the Titan's legs keep the legs-only shadow and sky; every other hit (the
    Juggernaut's own parts, the Titan's waist) takes the whole scene's."""
    parts = r.all_parts
    legs_px = np.isin(r.comp, TL.LEG_COMPS) & r.hitmask
    rest = r.hitmask & ~legs_px
    sh_extra = np.zeros(r.x.shape, np.float32)
    whole = len(r.occluders) == len(parts)
    if rest.any() and not whole:
        sm = RR.LightMap(parts, r.Ls, r.bounds, r.sm.step)
        P = np.stack([r.x[rest], r.y[rest], r.z[rest]], 1)
        sh_extra[rest] = sm.test(P, bias=0.15, pcf=1)
    occ = None
    if sky:
        occ_legs = r.sky_occlusion() if legs_px.any() and not whole else None
        own = r.occluders
        r.occluders = parts
        occ_all = r.sky_occlusion()
        r.occluders = own
        occ = occ_all if occ_legs is None else np.where(legs_px, occ_legs, occ_all)
    return sh_extra, occ


def finish(r, alb, occ, sh_extra, ao=None):
    """shade (the Juggernaut's ambient occlusion on its own parts, the Titan's on its legs and waist), the camera fill
    (none where the waist is in the body's shadow, as on the Titan) and the Titan's highlight on its gold."""
    titan = np.isin(r.comp, TL.COMPS)
    waist = np.isin(r.comp, TL.WAIST_COMPS)
    ao = 0.86 + 0.14 * np.clip(r.z / 14.0, 0, 1) if ao is None else ao
    ao_t = (0.86 + 0.14 * np.clip(r.z / 12.0, 0, 1)) * np.where(waist, 1 - 0.35 * sh_extra, 1.0)
    ao = np.where(titan, ao_t, ao)
    col = r.shade(alb, sky_occ=occ, ao=ao, shadow_extra=sh_extra)
    cam = r.cam
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    nf = nf * np.where(waist, 1 - 0.9 * sh_extra, 1.0)
    col = col + alb * (JR.FILL * nf)[..., None]
    return col + TL.spec(r)


def trim_of(r, house):
    ss = r.ss
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = house
    return Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')


def walker_parts(model, k):
    f, s = divmod(k, 15)
    M = JG.facing_matrix(JR.mod_to_cw(f))
    own, legs, pose = TW.body_parts(model['P'], s)
    return TL.move(own + legs, M)


def frame(k, model, ss=4, sky=True):
    parts = walker_parts(model, k)
    cam = JR.camera(model)
    win = JR.find_window(parts, cam)
    r = setup(parts, cam, JR.CANVAS, win, JR.BOUNDS, ss)
    JR.round_edges(r)
    sh_extra, occ = lighting(r, sky)
    alb = TL.materials(r, JR.materials(r, model['P']))
    col = finish(r, alb, occ, sh_extra)
    g = r.ground_alpha_full(shadow_parts=parts)
    img = r.compose(col, ground=g)
    trim = trim_of(r, (np.isin(r.comp, HOUSE_COMPS) & r.hitmask).astype(np.float32))
    return img, trim


def load():
    return JR.load(WALK)


if __name__ == '__main__':
    model = load()
    ks = [int(a) for a in sys.argv[2].split(',')]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else 'out_t'
    sky = bool(int(sys.argv[5])) if len(sys.argv) > 5 else True
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(k, model, ss, sky)
        save(img, trim, f'{out}/tsjugg-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
