"""
hsrender.py - the Hunter-Seeker's HD frames for the mod (TSHUNT, 384 x 384, one facing, 8 frames, 3 ticks a frame): the
fitted model (hseek.py, fit_h.json) in the RA-grid camera (32 degrees) at the size and place the mod's frames have
(4 canvas px per TS px: TS's sprite x 4 exactly), lit as the buildings and units are.  No shadow (the game draws it
from the frame).  v3: house colour back on TS's remap parts (the wings, the strut, the fins), pure green 0,214,0 x
(1 + 1.1 grain), with -trim masks (Luke: "restore house colours"; v1-v2 had the mod's steel there).
The frames differ as TS's do: the star's light pulses (blue to white at frame 3 and back), and the fins flash white at
frame 0 (their upper faces, as TS's) and stay brighter through frames 1-3.  The bronze has TS's shine: the highlight
TS's sprite shows on the shoulder's front, from the light TS lit its sprites with (front left of the camera).

    python3 hsrender.py frames 0,3 [ss] [outdir]
"""
import json, os, sys, time
import numpy as np
from PIL import Image
import rc, rcrender as RR
import walls2 as W
import hseek as S
from frameio import save

HERE = os.path.dirname(os.path.abspath(__file__))
CANVAS = (384, 384)
PPU = 4.0
PX_SCALE = 1.0                 # this canvas is drawn 1:1 (4 canvas px a TS px; the outline as the units' at the game)
BOUNDS = ((-14, 14), (-14, 14), (-2, 36))

BRONZE = np.array([222, 172, 78.])        # TS's be913c lit, a58538 mid (lit as the Titan's yellow-brown)
STEEL = np.array([186, 191, 209.])        # v1-v2: the mod's steel on TS's remap parts (its wings 148, 153, 166)
GREEN = np.array([0, 214, 0.])            # v3: house colour on TS's remap parts (the wings, the strut, the fins)
HOUSE = None                              # set below, once hseek's ids are in
SLOT = np.array([46, 50, 46.])            # the wings' slots: dark (TS's 006500-007700, the remap's darkest), not house
STAR = np.array([124, 124, 220.])         # TS's star 85, 85, 137 on average
SPIKE = np.array([94, 94, 179.])          # TS's 55559d, 595971
STUB = np.array([78, 78, 82.])            # TS's 343434 under the light
MAST = np.array([96, 96, 134.])           # TS's 404059 (the mast and the neck's collar)
TIP = np.array([118, 118, 122.])          # TS's 4c4c4c
STRIP = np.array([125, 125, 215.])        # TS's 6969b6, 55559d
MARK = np.array([170, 98, 74.])           # TS's 754434
FILL = 0.32
# the bronze's shine: TS's highlight on the shoulder's front (white, its edge yellow and pink); lit from TS's own light
# for its sprites, front-left of the camera (hd.L_CAM_TS), put into this camera
SPEC_K, SPEC_P = 0.9, 10.0
# TS's star light (pixel (36, 11)) per frame, and the fins' flash (frame 0 white, 1-3 brighter, as TS's remap shades)
STAR_LIGHT = [(125, 125, 206), (149, 149, 230), (178, 178, 255), (255, 255, 255), (178, 178, 255), (149, 149, 230),
              (125, 125, 206), (105, 105, 182)]
FIN_FLASH = [1.0, 0.18, 0.18, 0.1, 0.0, 0.0, 0.0, 0.0]
ELEV = 32.0
HOUSE = (S.WING, S.STRUT, S.FIN)


FIT = 'fit_h.json'


def load(path=os.path.join(HERE, FIT)):
    js = json.load(open(path))
    P = dict(S.P0); P.update(js['P'])
    return P


def spec_light(cam):
    """TS's sprite light (camera space: right, up, towards the viewer) in this camera's world."""
    import hd
    l = hd.L_CAM_TS
    e = np.deg2rad(ELEV)
    right = np.array([1.0, 0, 0]); up = np.array([0, -np.sin(e), np.cos(e)]); view = np.array([0, np.cos(e), np.sin(e)])
    L = l[0] * right + l[1] * up + l[2] * view
    H = L / np.linalg.norm(L) + view
    return H / np.linalg.norm(H)


def render(P, k, origin, ss=4, sky=True):
    parts = S.parts(P)
    cam = RR.ra_cam(PPU, origin)
    r = RR.RCRender(parts, cam, CANVAS, (0, 0) + CANVAS, BOUNDS, ss=ss, shadow_len=1.0, px_scale=PX_SCALE)
    hm = r.hitmask; comp = r.comp
    grain = W.sample(W.NOISE_FINE, r.x * 4, r.z * 4) * 0.035
    g1 = (1 + 0.45 * grain)[..., None]
    alb = np.zeros(hm.shape + (3,), np.float32)
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    bronze = np.isin(comp, (S.BODY, S.CHEST, S.SHOULDER, S.LOBE, S.LUG, S.NECK, S.BAND))
    put(bronze, BRONZE * g1)
    house = np.isin(comp, HOUSE) & hm
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    put(comp == S.SLOT, SLOT * g1)
    put(comp == S.STAR, STAR * g1)
    put(comp == S.SPIKE, SPIKE * g1)
    put(comp == S.STUB, STUB * g1)
    put(np.isin(comp, (S.MAST, S.COLLAR)), MAST * g1)
    put(comp == S.TIP, TIP * g1)
    put(comp == S.STRIP, STRIP * g1)
    put(comp == S.MARK, MARK * g1)
    occ = r.sky_occlusion() if sky else None
    col = r.shade(alb, sky_occ=occ, ao=None)
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    col = col + alb * (FILL * nf)[..., None]
    # the bronze's shine
    H = spec_light(cam)
    nh = np.clip(r.nx * H[0] + r.ny * H[1] + r.nz * H[2], 0, 1)
    sp = SPEC_K * nh ** SPEC_P * (bronze & hm)
    if occ is not None:
        sp = sp * (1 - 0.6 * np.clip(occ, 0, 1))
    col = col + (np.array([255, 246, 228.]) - col) * np.clip(sp, 0, 1)[..., None]
    # the fins' flash (TS's frame 0): their upper faces go white, the faces looking down stay as they are; then their
    # steel a touch brighter while it fades (frames 1-3, TS's remap a shade or two up)
    f = FIN_FLASH[k % 8]
    fins = (comp == S.FIN) & hm
    flash = np.zeros(hm.shape, bool)
    if f >= 1.0:
        w = np.clip(0.35 + 1.1 * r.nz, 0, 1) * fins
        col = col + (np.array([248, 248, 248.]) - col) * (0.9 * w)[..., None]
        flash = w > 0.5                           # the flashed white: not house colour while it lasts
    elif f > 0:
        col = np.where(fins[..., None], np.minimum(col * (1 + f), 255.0), col)
    # the star's light: the point of the core facing the camera, TS's colour, unshaded, TS's pixel across
    P3 = np.stack([r.x, r.y, r.z], -1)
    q = S.star_light(P, ELEV)
    d = np.linalg.norm(P3 - q, axis=-1)
    a = np.clip((0.55 - d) / 0.15, 0, 1)[..., None] * ((comp == S.STAR) & hm)[..., None]
    col = col * (1 - a) + np.asarray(STAR_LIGHT[k % 8], float) * a
    img = r.compose(col, ground=None)
    tm = (house & ~flash).astype(np.float32)
    ss_ = r.ss
    trim = Image.fromarray((tm.reshape(CANVAS[1], ss_, CANVAS[0], ss_).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    return img, trim


def frame(k, P, place, ss=4, sky=True):
    return render(P, k, place['origin'], ss, sky)


if __name__ == '__main__':
    P = load(); place = json.load(open(os.path.join(HERE, 'place.json')))
    ks = [int(a) for a in sys.argv[2].split(',')]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else 'out'
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(k, P, place, ss)
        save(img, trim, f'{out}/tshunt-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
