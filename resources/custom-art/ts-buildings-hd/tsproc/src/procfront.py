"""The refinery's front layer (TSPROCNF): the parts of the building in front of anything standing in the dock lane,
so a docked truck drawn under it backs in under the deck. The TS Harvester docks where the mod parks the trucks;
the building pixels that hide it, in each state, mask the idle loop's frames.

    python3 procfront.py ra22 [ss]   -> PKG/<view>/front/refinery-front-00..31 (+ trims)"""
import os, sys, time
import numpy as np
from PIL import Image
import hd, proc as PR, procrender as PRR, harv as HV
from pfinal import save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-tiberium-refinery-hd')
VIEWS = {'ra22': 'ra-grid-22'}
# the truck at its size on screen: the sprite is drawn full size over a building drawn at the view's scale
STAND_IN = 1.0 / PRR.RA22['scale']
# the TS and TD trucks park this far deeper into the bay than TS's own spot (along the lane, to the west): a
# quarter of the truck under the deck, 8 short of the back wall
SEAT_DEEPER = 38.0
# ...and this far north of the lane's middle, so the truck's top corner clears the rib framing the opening's south side
SEAT_NORTH = 3.0
H_BOUNDS = ((-260.0, 340.0), (-220.0, 220.0), 170)
# canvas px the mask reaches past the stand-in's hidden outline, over building with no truck behind it: a truck
# sprite's antialiased edge spreads a little wider than the model's silhouette
FRINGE = 3
# canvas px: hairline cracks in the hidden region (seams between the model's parts) closed up to this width
CRACK = 2


def grow(m, r):
    """m grown by r pixels (a disc)."""
    out = m.copy()
    H_, W_ = m.shape
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy > r * r:
                continue
            src = m[max(0, -dy):H_ - max(0, dy), max(0, -dx):W_ - max(0, dx)]
            out[max(0, dy):H_ - max(0, -dy), max(0, dx):W_ - max(0, -dx)] |= src
    return out


def occluder(vname, ss, level):
    """fraction of each canvas pixel where the building hides the stand-in truck, or stands just past its hidden
    outline with no truck behind it (0..1)."""
    v = PRR.view(vname, ss)
    dk = PR.DOCK['ra']
    pos = (dk['pos'][0] - SEAT_DEEPER, dk['pos'][1] - SEAT_NORTH)
    truck = dict(model=HV, frame=dk['frame'], pos=pos, s=HV.S * STAND_IN, unloading=False)
    pr = PRR.ProcPrep(PRR.BLD, v, vname=vname, level=level, truck=truck)
    shown = pr.r.hitmask & (pr.r.comp >= PR.TRUCK_BASE)
    building = pr.r.hitmask & (pr.r.comp > 0) & (pr.r.comp < PR.TRUCK_BASE)
    del pr
    alone = hd.Render(lambda X, Y, **k: HV.merge_slabs(HV.scene(X, Y, **k)), v, H_BOUNDS, 170.0,
                      frame=dk['frame'], unloading=False, s=HV.S * STAND_IN, pos=pos)
    hidden = alone.hitmask & ~shown & building
    closed = ~grow(~grow(hidden, CRACK * ss), CRACK * ss)
    hidden |= closed & alone.hitmask
    hidden |= grow(hidden, FRINGE * ss) & ~alone.hitmask & building
    del alone
    H_, W_ = hidden.shape[0] // ss, hidden.shape[1] // ss
    frac = hidden.reshape(H_, ss, W_, ss).mean(axis=(1, 3))
    x0, y0, x1, y1 = PRR.WIN[vname]
    can = np.zeros((PRR.CANVAS[1], PRR.CANVAS[0]), np.float32)
    can[y0:y0 + H_, x0:x0 + W_] = frac
    return can


def front(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in (0, 1):
        t0 = time.time()
        # hard-edged: the building's own antialiased edge blends against the truck, so no seam shows where the
        # mask's soft edge would let the truck's outline through
        m = (occluder(vname, ss, level) > 0.5).astype(np.float32)
        Image.fromarray((m * 255).round().astype(np.uint8), 'L').save(f'{out}/front-mask-{level:02d}.png')
        for t in range(16):
            k = t + level * 16
            f = np.asarray(Image.open(f'{out}/loop/refinery-loop-{k:02d}.png').convert('RGBA')).astype(np.float32)
            tr = np.asarray(Image.open(f'{out}/loop/refinery-loop-{k:02d}-trim.png').convert('L')).astype(np.float32)
            f[..., 3] *= m
            img = Image.fromarray(f.round().astype(np.uint8), 'RGBA')
            trim = Image.fromarray((tr * m).round().astype(np.uint8), 'L')
            save(img, trim, f'{out}/front/refinery-front-{k:02d}.png')
        print(vname, 'front', level, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    front(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 4)
