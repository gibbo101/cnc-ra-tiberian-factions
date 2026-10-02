"""Final frames for the Service Depot (10-TSDEPT), both views, into PKG/<view>/...

    python3 deptfinal.py states iso|ra [ss]   bib/ 00, 01 (GTDEPTBB: the pad); building/ 00, 01 (GTDEPT: the gantry,
                                             cut against the pad, so bib + building = the whole depot);
                                             A-lights/ 20 (GTDEPT_A: 00-04 healthy, 05-09 damaged, 10-19 empty),
                                             B-glow/ 14 (GTDEPT_B: 00-06, 07-13 empty), D-flash/ 28 (GTDEPT_D: 00-06
                                             healthy, 07-13 damaged, 14-27 empty), each cut against bib + building;
                                             loop/ 70, the mod's TSDEPT.ZIP layout (35 healthy + 35 damaged: A and B
                                             playing together, A t%5, B t%7), straight renders
    python3 deptfinal.py arm iso|ra [ss]      C-arm/ 32 (GTDEPT_C: 00-15 the repair arm, 16-31 empty), cut against the
                                             healthy depot
    python3 deptfinal.py build iso|ra [ss]    build-up/ 17 frames in GTDEPTMK's order (the last is the whole depot)

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
from PIL import Image
import dept as M, deptrender as RR, deptbuild as DB
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-service-depot-hd')
NAME = 'depot'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
NA, NB, NC, ND = 5, 7, 16, 7


def canvas(img, vname):
    return RR.on_canvas(img, vname)


def empty(vname):
    return Image.new('RGBA', RR.canvas_of(vname), (0, 0, 0, 0)), Image.new('L', RR.canvas_of(vname), 0)


def states(vname, ss=4, levels=(0, 1)):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in levels:
        t0 = time.time()
        pb, v = RR.prep(vname, ss, level=level, pad=True)
        bib, btrim = pb.frame(want_trim=True)
        del pb
        bib, btrim = canvas(bib, vname), canvas(btrim, vname)
        save(bib, btrim, f'{out}/bib/{NAME}-bib-{level:02d}.png')
        pr, v = RR.prep(vname, ss, level=level)
        full, ftrim = pr.frame(want_trim=True)
        full, ftrim = canvas(full, vname), canvas(ftrim, vname)
        bld = overlay(bib, full)
        save(bld, ftrim, f'{out}/building/{NAME}-{level:02d}.png', alpha_from=bld)
        for t in range(NA):
            f, ft = pr.frame(want_trim=True, lights=t)
            f, ft = canvas(f, vname), canvas(ft, vname)
            ov = overlay(full, f)
            save(ov, ft, f'{out}/A-lights/{NAME}-lights-{t + NA * level:02d}.png', alpha_from=ov)
        for t in range(ND):
            f, ft = pr.frame(want_trim=True, flash=t)
            f, ft = canvas(f, vname), canvas(ft, vname)
            ov = overlay(full, f)
            save(ov, ft, f'{out}/D-flash/{NAME}-flash-{t + ND * level:02d}.png', alpha_from=ov)
        if level == 0:
            for t in range(NB):
                f, ft = pr.frame(want_trim=True, glow=t)
                f, ft = canvas(f, vname), canvas(ft, vname)
                ov = overlay(full, f)
                save(ov, ft, f'{out}/B-glow/{NAME}-glow-{t:02d}.png', alpha_from=ov)
        for t in range(NA * NB):
            f, ft = pr.frame(want_trim=True, lights=t % NA, glow=t % NB)
            save(canvas(f, vname), canvas(ft, vname), f'{out}/loop/{NAME}-loop-{t + NA * NB * level:02d}.png')
        del pr
        print(vname, 'level', level, '%.0fs' % (time.time() - t0), flush=True)
    e, et = empty(vname)
    for k in range(2 * NA, 4 * NA):
        save(e, et, f'{out}/A-lights/{NAME}-lights-{k:02d}.png')
    for k in range(NB, 2 * NB):
        save(e, et, f'{out}/B-glow/{NAME}-glow-{k:02d}.png')
    for k in range(2 * ND, 4 * ND):
        save(e, et, f'{out}/D-flash/{NAME}-flash-{k:02d}.png')


def arm_cut(base, frame, armmask, keep_dark=0.06):
    """the repair arm as an overlay that works over both states (TS's C has one set): the arm itself (and its outline)
    copied from the frame; its shadow as black with alpha (base x (1 - a) = frame), so on the damaged depot it darkens
    the damaged pad instead of pasting the healthy one; its shadow on bare ground as overlay() solves it.  Darkening
    under keep_dark is left out (the faint sky-occlusion change the arm makes on the pad)."""
    from scipy import ndimage
    ov = np.array(overlay(base, frame)).astype(np.float64)
    a = np.array(base).astype(np.float64); b = np.array(frame).astype(np.float64)
    m1 = ndimage.binary_dilation(armmask, iterations=2)
    out = np.zeros_like(ov)
    out[m1] = ov[m1]
    ab, af = a[..., 3] / 255.0, b[..., 3] / 255.0
    grow = ~m1 & (af > ab + 1e-3) & (af < 0.999)
    out[grow] = ov[grow]
    la = (a[..., :3] * np.array([0.3, 0.59, 0.11])).sum(-1); lb = (b[..., :3] * np.array([0.3, 0.59, 0.11])).sum(-1)
    dark = ~m1 & ~grow & (ab > 0.999) & (af > 0.999) & (lb < la * (1.0 - keep_dark))
    al = np.clip(1.0 - lb / np.maximum(la, 1e-6), 0, 0.85)
    out[dark, :3] = 0.0
    out[dark, 3] = al[dark] * 255.0
    return Image.fromarray(np.clip(out, 0, 255).round().astype(np.uint8), 'RGBA'), m1


def arm(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    full = Image.open(f'{out}/building/{NAME}-00.png').convert('RGBA')
    bib = Image.open(f'{out}/bib/{NAME}-bib-00.png').convert('RGBA')
    base = bib.copy(); base.alpha_composite(full)
    # the depot's own sky occlusion off the arm: the arm changes only what it covers and its shadow
    pr0, v = RR.prep(vname, ss)
    occ0 = pr0.occ
    del pr0
    for t in range(NC):
        t0 = time.time()
        pr, v = RR.prep(vname, ss, arm=t)
        armpx = pr.r.hitmask & np.isin(pr.r.comp, [M.ARM, M.TOOL, M.SPARK])
        pr.occ = np.where(armpx, pr.occ, occ0)
        f, ft = pr.frame(want_trim=True)
        ssv = v.ss
        H_, W_ = armpx.shape[0] // ssv, armpx.shape[1] // ssv
        am = armpx.reshape(H_, ssv, W_, ssv).mean(axis=(1, 3)) > 0.0
        del pr
        f, ft = canvas(f, vname), canvas(ft, vname)
        am = np.array(canvas(Image.fromarray((am * 255).astype(np.uint8), 'L'), vname)) > 0
        ov, m1 = arm_cut(base, f, am)
        tr = np.array(ft).astype(np.float64) * m1
        save(ov, Image.fromarray(tr.round().astype(np.uint8), 'L'), f'{out}/C-arm/{NAME}-arm-{t:02d}.png', alpha_from=ov)
        print(vname, 'arm', t, '%.0fs' % (time.time() - t0), flush=True)
    e, et = empty(vname)
    for k in range(NC, 2 * NC):
        save(e, et, f'{out}/C-arm/{NAME}-arm-{k:02d}.png')


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}/build-up'
    n = len(DB.SEQ)
    for i in (frames if frames is not None else range(n)):
        t0 = time.time()
        pr, v = RR.prep(vname, ss, prog=None if i == n - 1 else DB.SEQ[i])
        f, ft = pr.frame(want_trim=True)
        del pr
        save(canvas(f, vname), canvas(ft, vname), f'{out}/{NAME}-build-{i:02d}.png')
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    if what == 'states':
        lv = tuple(int(a) for a in sys.argv[4:]) or (0, 1)
        states(vname, ss, lv)
    elif what == 'arm':
        arm(vname, ss)
    elif what == 'build':
        fr = [int(a) for a in sys.argv[4:]] or None
        build(vname, ss, fr)
