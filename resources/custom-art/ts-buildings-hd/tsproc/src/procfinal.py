"""Final frames for the Tiberium Refinery (04-TSPROC), both views, into PKG/<view>/...

    python3 procfinal.py states iso|ra [ss]   the building (00 healthy, 01 damaged) with the dock lamps at NTREFN_C's
                                             frame 0; C (the lamps' 16 frames, healthy then damaged) and the 32-frame
                                             loop like TSPROC.ZIP (00-15 healthy, 16-31 damaged)
    python3 procfinal.py bib iso|ra [ss]      the bib (NTREFNBB): 00 healthy, 01 damaged
    python3 procfinal.py dock iso|ra [ss]     D: the harvester docked (HARV, HORV), healthy and damaged, in the scene
    python3 procfinal.py lid iso|ra [ss]      A (NTREFN_A): the harvester's tank sliding into the dock, 10 frames
                                             (after dock: cut against the building with HORV docked)
    python3 procfinal.py fire iso|ra [ss]     B (NTREFN_B): the flare stack's fire, 40 frames (20 lit)
    python3 procfinal.py build iso|ra [ss]    the build-up, 24 frames (with the bib; the last is the building on it)

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, proc as PR, procrender as PRR, procbuild as PB, procfire2 as PF, harv as HV
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-tiberium-refinery-hd')
SCR = os.environ.get('SCR', '/home/claude/work/scratch/proc/final')
NAME = 'refinery'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid', 'ra22': 'ra-grid-22'}
C_N = 16


def prep(vname, ss, win=None, **kw):
    v = PRR.view(vname, ss, win)
    return PRR.ProcPrep(PRR.BLD, v, vname=vname, **kw), v


def canvas(img, vname, win=None):
    return PRR.on_canvas(img, vname, win)


def states(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in (0, 1):
        t0 = time.time()
        pr, v = prep(vname, ss, level=level)
        base, trim = pr.frame(want_trim=True, lights=0)
        base, trim = canvas(base, vname), canvas(trim, vname)
        save(base, trim, f'{out}/building/{NAME}-{level:02d}.png')
        for t in range(C_N):
            f, ft = pr.frame(want_trim=True, lights=t)
            f, ft = canvas(f, vname), canvas(ft, vname)
            o = overlay(base, f)
            save(o, ft, f'{out}/C-lamps/{NAME}-lamps-{t + level * C_N:02d}.png', alpha_from=o)
            save(f, ft, f'{out}/loop/{NAME}-loop-{t + level * C_N:02d}.png')
        del pr
        print(vname, 'level', level, '%.0fs' % (time.time() - t0), flush=True)


def bib(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in (0, 1):
        t0 = time.time()
        pb, v = prep(vname + '-bib', ss, pad=True, level=level)
        col, tm = pb.shade()
        img = pb.r.compose(col, ground=False, outline=False)
        ssv = v.ss
        H_, W_ = tm.shape[0] // ssv, tm.shape[1] // ssv
        trim = Image.fromarray((tm.reshape(H_, ssv, W_, ssv).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
        save(canvas(img, vname + '-bib'), canvas(trim, vname + '-bib'), f'{out}/bib/{NAME}-bib-{level:02d}.png')
        del pb
        print(vname, 'bib', level, '%.0fs' % (time.time() - t0), flush=True)


def dock(vname, ss=4):
    """the harvester docked, rendered into the refinery's scene (the building hides what it should of it, their
    shadows fall on each other), cut against the building it is drawn over:
      D-docked/  00 HARV (loaded, as it arrives) and 01 HORV (unloading, its tank off) on the healthy building,
                 02 and 03 the same on the damaged building.
    Also keeps the full frame building + HORV (healthy) for the lid's cut."""
    out = f'{PKG}/{VIEWS[vname]}'
    lay = PRR.LAYOUT[vname]
    os.makedirs(SCR, exist_ok=True)
    for level in (0, 1):
        base = Image.open(f'{out}/building/{NAME}-{level:02d}.png').convert('RGBA')
        for unl in (False, True):
            t0 = time.time()
            pr, v = prep(vname, ss, level=level, truck=PR.truck_args(lay, unl, HV))
            f, ft = pr.frame(want_trim=True, lights=0)
            f, ft = canvas(f, vname), canvas(ft, vname)
            del pr
            o = overlay(base, f)
            save(o, ft, f'{out}/D-docked/{NAME}-docked-{2 * level + int(unl):02d}.png', alpha_from=o)
            if level == 0 and unl:
                f.save(f'{SCR}/{vname}-building-horv.png')
            print(vname, 'dock', level, unl, '%.0fs' % (time.time() - t0), flush=True)


def lid(vname, ss=4):
    """NTREFN_A: the tank sliding off the docked HORV into the building, cut against the healthy building (lamps at
    frame 0) with HORV docked in front of it (what it is drawn over: the mod's HORV unit, or D-docked/01)."""
    out = f'{PKG}/{VIEWS[vname]}'
    lay = PRR.LAYOUT[vname]
    base = Image.open(f'{SCR}/{vname}-building-horv.png').convert('RGBA')
    for k in range(10):
        t0 = time.time()
        la = PR.lid_args(lay, k, HV)
        if la is None:
            empty = Image.new('RGBA', PRR.CANVAS, (0, 0, 0, 0))
            save(empty, Image.new('L', PRR.CANVAS, 0), f'{out}/A-lid/{NAME}-lid-{k:02d}.png')
            continue
        pr, v = prep(vname, ss, lid=la, truck=PR.truck_args(lay, True, HV))
        f, ft = pr.frame(want_trim=True, lights=0)
        f, ft = canvas(f, vname), canvas(ft, vname)
        del pr
        o = overlay(base, f)
        save(o, ft, f'{out}/A-lid/{NAME}-lid-{k:02d}.png', alpha_from=o)
        print(vname, 'lid', k, '%.0fs' % (time.time() - t0), flush=True)


def unit_at():
    """where the mod's harvester sprite (its 384x384 canvas) sits on the refinery's canvas when docked on the RA grid:
    the truck's position (DOCK['ra']) projected, less the sprite's pivot."""
    import harvrender as HR
    v = hd.ra_view(PRR.CANVAS, PRR.origin('ra'), ss=1)
    px, py = v.project(PR.DOCK['ra']['pos'][0], PR.DOCK['ra']['pos'][1], 0.0)
    return int(round(float(px) - HR.PIVOT[0])), int(round(float(py) - HR.PIVOT[1]))


def lid_unit(ss=4):
    """RA grid, for the mod's way now (the HORV unit drawn over the building): the lid as a layer over the unit -
    HORV with its tank sliding off it, nothing of the tank past the truck's back end, cut against HORV alone; on the
    refinery's canvas where the docked unit's sprite is (unit_at())."""
    import harvrender as HR
    out = f'{PKG}/ra-grid/A-lid-unit'
    ux, uy = unit_at()
    hp = HR.HarvPrep(PR.DOCK['ra']['frame'], True, ss)
    base, _ = hp.frame_img()
    del hp
    for k in range(10):
        can = Image.new('RGBA', PRR.CANVAS, (0, 0, 0, 0)); ct = Image.new('L', PRR.CANVAS, 0)
        if k < 5:
            hp = HR.HarvPrep(PR.DOCK['ra']['frame'], True, ss, lid_off=k * PR.TANK_LEN / 4.6)
            f, ft = hp.frame_img()
            del hp
            o = overlay(base, f)
            can.paste(o, (ux, uy)); ct.paste(ft, (ux, uy))
        save(can, ct, f'{out}/{NAME}-lid-unit-{k:02d}.png', alpha_from=can)
        print('lid-unit', k, flush=True)


def fire_mouth(vname):
    """where TS's stack mouth (TS px (77, 47)) is on the canvas, and screen px per TS px."""
    if vname == 'iso':
        return (PF.MOUTH_TS[0] * PRR.ISO_K + PRR.ISO_O[0], PF.MOUTH_TS[1] * PRR.ISO_K + PRR.ISO_O[1]), PRR.ISO_K
    p = PR.params('ra')
    st = p['stack']
    if vname == 'ra22':
        v = PRR.view('ra22', 1, (0, 0) + PRR.CANVAS)
        mx, my = v.project(st['c'][0], st['c'][1], st['top'] + 3.0)
        return (float(mx), float(my) - 1.0), PRR.RA22['scale'] / hd.TS_PPU
    v = hd.ra_view(PRR.CANVAS, PRR.origin('ra'), ss=1)
    mx, my = v.project(st['c'][0], st['c'][1], st['top'] + 3.0)
    return (float(mx), float(my) - 1.0), 1.0 / hd.TS_PPU          # RA's camera: 1 px per unit; TS: TS_PPU


def fire(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    mouth, scale = fire_mouth(vname)
    for k in range(PF.N_ALL):
        img = PF.layer(k, PRR.CANVAS, mouth, scale, ss=ss)
        save(img, Image.new('L', PRR.CANVAS, 0), f'{out}/B-fire/{NAME}-fire-{k:02d}.png')
    print(vname, 'fire', mouth, scale, flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}'
    n = len(PB.SEQ)
    for i in (frames if frames is not None else range(n)):
        t0 = time.time()
        last = i == n - 1
        g = None if last else PB.SEQ[i]
        # the bib layer as far as it has got, then the building over it
        pb, v = prep(vname + '-bib', ss, pad=True, prog=g)
        col, tm = pb.shade()
        bimg = canvas(pb.r.compose(col, ground=False, outline=False), vname + '-bib')
        ssv = v.ss
        H_, W_ = tm.shape[0] // ssv, tm.shape[1] // ssv
        btrim = canvas(Image.fromarray((tm.reshape(H_, ssv, W_, ssv).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L'),
                       vname + '-bib')
        del pb
        pr, v = prep(vname, ss, prog=g)
        img, trim = pr.frame(want_trim=True, lights=0)
        img, trim = canvas(img, vname), canvas(trim, vname)
        del pr
        comp = bimg.copy(); comp.alpha_composite(img)
        a = np.array(img)[..., 3:4].astype(np.float32) / 255.0
        t = np.array(trim).astype(np.float32)[..., None] / 255.0
        bt = np.array(btrim).astype(np.float32)[..., None] / 255.0
        tt = (t * a + bt * (1 - a))[..., 0]
        save(comp, Image.fromarray((tt * 255).round().astype(np.uint8), 'L'), f'{out}/build-up/{NAME}-build-{i:02d}.png')
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    fr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    {'states': lambda: states(vname, ss), 'bib': lambda: bib(vname, ss), 'lid': lambda: lid(vname, ss),
     'dock': lambda: dock(vname, ss), 'lidunit': lambda: lid_unit(ss), 'fire': lambda: fire(vname, ss),
     'build': lambda: build(vname, ss, fr)}[what]()
