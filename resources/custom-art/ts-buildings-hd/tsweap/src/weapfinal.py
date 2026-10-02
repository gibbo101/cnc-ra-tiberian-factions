"""Final frames for the War Factory (06-TSWEAP), both views, into PKG/<view>/...

    python3 weapfinal.py states iso|ra [ss]   building/ 00 healthy, 01 damaged (door shut, lamps dark, like GTWEAP);
                                             building-bay/ the door bay alone (like the mod's TSWEAP.ZIP: GTWEAP less
                                             _2) and 2-over-units/ the rest (GTWEAP_2: 00, 01, 02-03 empty);
                                             A-lamps/ 32 (GTWEAP_A: 16 healthy, 16 empty), B-lamps/ 16 (8 + 8 empty),
                                             C-fans/ 8 (4 + 4 empty), cut against the building
    python3 weapfinal.py door iso|ra [ss]     D-door/ the door rolling up (GTWEAP_D): 00-08, both states (TS's door is
                                             the same on the damaged building)
    python3 weapfinal.py under iso|ra [ss]    1-under-door/ (GTWEAP_1): the bay seen with the door up, and the apron:
                                             00 healthy, 01 damaged
    python3 weapfinal.py bib iso|ra [ss]      bib/ (GTWEAPBB): 00 healthy, 01 damaged
    python3 weapfinal.py build iso|ra [ss]    build-up/ 26 frames in GTWEAPMK's order (the last is the building on
                                             its bib)

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage
import hd, weap as M, weaprender as WR, weapbuild as WB, weapmat as MM
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-war-factory-hd')
SCR = os.environ.get('SCR', '/home/claude/work/scratch/weap/final')
NAME = 'war-factory'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
NA, NB, NC, ND = 16, 8, 4, 9


def canvas(img, vname):
    return WR.on_canvas(img, vname)


def empty(vname):
    return Image.new('RGBA', WR.canvas_of(vname), (0, 0, 0, 0)), Image.new('L', WR.canvas_of(vname), 0)


def down(mask_ss, ss):
    H_, W_ = mask_ss.shape[0] // ss, mask_ss.shape[1] // ss
    return mask_ss.reshape(H_, ss, W_, ss).mean(axis=(1, 3))


def bay_mask(r, vname):
    """the door bay on screen (canvas px, bool): the door, and in the TS angle the north fender and its cap behind it
    (TS's GTWEAP less GTWEAP_2)."""
    lay = WR.LAYOUT[WR.base(vname)]
    x, y = M.to_local(r.x, r.y, lay)
    m = r.hitmask & np.isin(r.comp, [M.DOOR, M.FLOOR])     # the floor's edge at the door's foot: units drive over it
    if WR.base(vname) == 'iso':
        m |= r.hitmask & np.isin(r.comp, [M.JAMB, M.NCAP]) & (y < 0)
    cov = down(m.astype(np.float32), r.view.ss)
    full = down(r.hitmask.astype(np.float32), r.view.ss)
    bay = cov > 0.5 * np.maximum(full, 1e-6)
    # the outline ring round it goes with it where it borders nothing else of the building
    return canvas(Image.fromarray((bay * 255).astype(np.uint8), 'L'), vname)


def ring_mask(r, vname):
    """the outline ring round the building's silhouette, on the canvas (coverage > 0: a pixel with some outline)."""
    ss = r.view.ss
    ring = ndimage.binary_dilation(r.hitmask, iterations=max(1, int(0.9 * ss))) & ~r.hitmask
    cov = down(ring.astype(np.float32), ss)
    return canvas(Image.fromarray((np.clip(cov, 0, 1) * 255).round().astype(np.uint8), 'L'), vname)


def split(img, trim, bay, ring=None):
    """img -> (the door bay and every see-through pixel on the ground: drawn under units; the rest of the building and
    its own outline: drawn over units), each pixel to one of them.  ring: the outline ring's coverage (ring_mask);
    its pixels go with the nearer of the two (without it: within 1.6 px of the rest)."""
    a = np.array(img); t = np.array(trim)
    b = np.array(bay) > 127
    solid = a[..., 3] >= 250
    over_solid = solid & ~b
    d_over = ndimage.distance_transform_edt(~over_solid)
    if ring is None:
        ring_ = ~solid & (d_over < 1.6)
    else:
        d_bay = ndimage.distance_transform_edt(~(solid & b))
        ring_ = ~solid & (np.array(ring) > 0) & (d_over <= d_bay) & (d_over < 4.0)
    over = over_solid | ring_
    inb = ~over
    p1 = a.copy(); p1[~inb] = 0
    p2 = a.copy(); p2[inb] = 0
    t1 = t.copy(); t1[~inb] = 0
    t2 = t.copy(); t2[inb] = 0
    return (Image.fromarray(p1, 'RGBA'), Image.fromarray(t1, 'L')), (Image.fromarray(p2, 'RGBA'), Image.fromarray(t2, 'L'))


def states(vname, ss=4, levels=(0, 1)):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in levels:
        t0 = time.time()
        pr, v = WR.prep(vname, ss, level=level)
        base, trim = pr.frame(want_trim=True)
        base, trim = canvas(base, vname), canvas(trim, vname)
        save(base, trim, f'{out}/building/{NAME}-{level:02d}.png')
        bay = bay_mask(pr.r, vname)
        bay.save(f'{SCR}/{vname}-bay-{level}.png') if os.path.isdir(SCR) else None
        ring = ring_mask(pr.r, vname)
        ring.save(f'{SCR}/{vname}-ring-{level}.png') if os.path.isdir(SCR) else None
        (b1, t1), (b2, t2) = split(base, trim, bay, ring)
        save(b1, t1, f'{out}/building-bay/{NAME}-bay-{level:02d}.png')
        save(b2, t2, f'{out}/2-over-units/{NAME}-over-{level:02d}.png')
        if level == 0:
            for k in range(NA):
                f, ft = pr.frame(want_trim=True, lampsA=k)
                f, ft = canvas(f, vname), canvas(ft, vname)
                o = overlay(base, f)
                save(o, ft, f'{out}/A-lamps/{NAME}-lamps-{k:02d}.png', alpha_from=o)
            for k in range(NB):
                f, ft = pr.frame(want_trim=True, lampsB=k)
                f, ft = canvas(f, vname), canvas(ft, vname)
                o = overlay(base, f)
                save(o, ft, f'{out}/B-lamps/{NAME}-lamps-b-{k:02d}.png', alpha_from=o)
            for k in range(NC):
                f, ft = pr.frame(want_trim=True, fans=k)
                f, ft = canvas(f, vname), canvas(ft, vname)
                o = overlay(base, f)
                save(o, ft, f'{out}/C-fans/{NAME}-fans-{k:02d}.png', alpha_from=o)
        else:
            e, et = empty(vname)
            for k in range(NA):
                save(e, et, f'{out}/A-lamps/{NAME}-lamps-{NA + k:02d}.png')
            for k in range(NB):
                save(e, et, f'{out}/B-lamps/{NAME}-lamps-b-{NB + k:02d}.png')
            for k in range(NC):
                save(e, et, f'{out}/C-fans/{NAME}-fans-{NC + k:02d}.png')
            for k in (2, 3):
                save(e, et, f'{out}/2-over-units/{NAME}-over-{k:02d}.png')
        del pr
        print(vname, 'states', level, '%.0fs' % (time.time() - t0), flush=True)


def resplit(vname, ss=4):
    """re-cut building/ into building-bay/ and 2-over-units/ with the current bay_mask (and save the masks for under)."""
    out = f'{PKG}/{VIEWS[vname]}'
    for level in (0, 1):
        t0 = time.time()
        pr, v = WR.prep(vname, ss, level=level)
        bay = bay_mask(pr.r, vname)
        ring = ring_mask(pr.r, vname)
        del pr
        bay.save(f'{SCR}/{vname}-bay-{level}.png'); ring.save(f'{SCR}/{vname}-ring-{level}.png')
        base = Image.open(f'{out}/building/{NAME}-{level:02d}.png').convert('RGBA')
        trim = Image.open(f'{out}/building/{NAME}-{level:02d}-trim.png').convert('L')
        (b1, t1), (b2, t2) = split(base, trim, bay, ring)
        save(b1, t1, f'{out}/building-bay/{NAME}-bay-{level:02d}.png')
        save(b2, t2, f'{out}/2-over-units/{NAME}-over-{level:02d}.png')
        print(vname, 'resplit', level, '%.0fs' % (time.time() - t0), flush=True)


def door(vname, ss=4):
    """GTWEAP_D: 9 frames, rendered on the healthy building. TS's door is the same on the damaged building (GTWEAP 1
    leaves it untouched, and GTWEAP_D has no damaged half), so one set serves both states."""
    out = f'{PKG}/{VIEWS[vname]}'
    for level in (0,):
        for k in range(ND):
            t0 = time.time()
            pr, v = WR.prep(vname, ss, level=level, door=k / (ND - 1))
            col, tm = pr.shade()
            only = pr.r.hitmask & (pr.r.comp == M.DOOR)
            img = pr.r.compose(col, ground=False, outline=True, only=only)
            ssv = v.ss
            tmm = tm * only
            trim = Image.fromarray((down(tmm, ssv) * 255).round().astype(np.uint8), 'L')
            img, trim = canvas(img, vname), canvas(trim, vname)
            save(img, trim, f'{out}/D-door/{NAME}-door-{k + ND * level:02d}.png', alpha_from=img)
            del pr
            print(vname, 'door', level, k, '%.0fs' % (time.time() - t0), flush=True)


def bib_frame(vname, ss, level=0, prog=None):
    wn = vname + '-bib'
    win = WR.WIN.get(wn + '-build', WR.WIN[wn]) if prog is not None else WR.WIN[wn]     # the slab is bigger
    pb, v = WR.prep(wn, ss, pad=True, level=level, prog=prog, win=win)
    col, tm = pb.shade()
    img = pb.r.compose(col, ground=False, outline=False)
    trim = Image.fromarray((down(tm, v.ss) * 255).round().astype(np.uint8), 'L')
    del pb
    return WR.on_canvas(img, wn, win=win), WR.on_canvas(trim, wn, win=win)


def bib(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in (0, 1):
        t0 = time.time()
        img, trim = bib_frame(vname, ss, level)
        save(img, trim, f'{out}/bib/{NAME}-bib-{level:02d}.png')
        print(vname, 'bib', level, '%.0fs' % (time.time() - t0), flush=True)


def under(vname, ss=4, reuse=False):
    """GTWEAP_1: what shows in the door bay with the door rolled away (the bay, its rails and lights; in the TS angle
    the north fender and its cap too, as TS's), on a copy of the bib as TS's, with the building's ground shadow on that
    bib as building-bay has it: drawn over building-bay it changes only the bay (no shadow lost under the bib copy, none
    doubled).  reuse: take the open bay from SCR (saved by an earlier run) instead of rendering it again."""
    out = f'{PKG}/{VIEWS[vname]}'
    for level in (0, 1):
        t0 = time.time()
        bay = Image.open(f'{SCR}/{vname}-bay-{level}.png') if os.path.exists(f'{SCR}/{vname}-bay-{level}.png') else None
        if bay is None:
            pr, v = WR.prep(vname, ss, level=level)
            bay = bay_mask(pr.r, vname)
            del pr
        bm = np.array(bay) > 127
        cache = f'{SCR}/{vname}-open-{level}.png'
        if reuse and os.path.exists(cache):
            b1 = Image.open(cache).convert('RGBA'); t1 = Image.open(cache[:-4] + '-trim.png').convert('L')
        else:
            pr, v = WR.prep(vname, ss, level=level, door=None)
            f, ft = pr.frame(want_trim=True)
            f, ft = canvas(f, vname), canvas(ft, vname)
            del pr
            fa = np.array(f); fa[~bm] = 0
            fta = np.array(ft); fta[~bm] = 0
            b1, t1 = Image.fromarray(fa, 'RGBA'), Image.fromarray(fta, 'L')
            b1.save(cache); t1.save(cache[:-4] + '-trim.png')
        # the bib copy: only its solid inside (its antialiased rim is the bib layer's: drawn twice it would thicken)
        ba = np.array(Image.open(f'{out}/bib/{NAME}-bib-{level:02d}.png').convert('RGBA'))
        onbib = ba[..., 3] >= 250
        ba[~onbib] = 0
        bimg = Image.fromarray(ba, 'RGBA')
        # outside the door's own opening (the north fender and its cap, in the TS angle) keep the building's own pixels,
        # so _1 over building-bay changes nothing until the door moves
        dshut = np.array(Image.open(f'{out}/D-door/{NAME}-door-00.png').convert('RGBA'))[..., 3] > 0
        dreg = dshut
        bayl = np.array(Image.open(f'{out}/building-bay/{NAME}-bay-{level:02d}.png').convert('RGBA'))
        bayt = np.array(Image.open(f'{out}/building-bay/{NAME}-bay-{level:02d}-trim.png').convert('L'))
        keep = bm & ~dreg
        solid_keep = keep & (bayl[..., 3] >= 250)
        b1a = np.array(b1); t1a = np.array(t1)
        b1a[keep] = 0; t1a[keep] = 0                      # see-through edges there: building-bay draws them already
        b1a[solid_keep] = bayl[solid_keep]; t1a[solid_keep] = bayt[solid_keep]
        b1, t1 = Image.fromarray(b1a, 'RGBA'), Image.fromarray(t1a, 'L')
        btrim = np.array(Image.open(f'{out}/bib/{NAME}-bib-{level:02d}-trim.png').convert('L')).astype(np.float32)
        btrim[~onbib] = 0
        # on the bib copy, everything see-through that building-bay draws there (the ground shadow, edges), outside
        # the door's opening: so over the bib, _1 is exactly bib + building-bay until the door moves
        bb = bayl
        sh = bb.copy(); sh[~((bb[..., 3] < 250) & onbib & ~dreg)] = 0
        comp = bimg.copy(); comp.alpha_composite(Image.fromarray(sh, 'RGBA')); comp.alpha_composite(b1)
        ash = sh[..., 3].astype(np.float32) / 255.0
        a1 = np.array(b1)[..., 3].astype(np.float32) / 255.0
        tt = btrim * (1 - ash)
        tt = np.array(t1).astype(np.float32) * a1 + tt * (1 - a1)
        if M.LAYOUTS[WR.LAYOUT[WR.base(vname)]].get('sym', False):
            # RA round 2 (as the mod cut it): only the doorway, the shut door's outline 2 px wider; the apron copy
            # round it dropped (bib + building-bay already draw it)
            reg = ndimage.binary_dilation(dshut, iterations=2)
            ca = np.array(comp); ca[~reg] = 0
            comp = Image.fromarray(ca, 'RGBA'); tt = np.where(reg, tt, 0.0)
        save(comp, Image.fromarray(tt.round().astype(np.uint8), 'L'), f'{out}/1-under-door/{NAME}-under-{level:02d}.png')
        print(vname, 'under', level, '%.0fs' % (time.time() - t0), flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}'
    n = len(WB.SEQ)
    wb = WR.WIN.get(vname + '-build')            # a wider window where the build-up's poles reach further
    for i in (frames if frames is not None else range(n)):
        t0 = time.time()
        last = i == n - 1
        g = None if last else WB.SEQ[i]
        bimg, btrim = bib_frame(vname, ss, 0, prog=g)
        pr, v = WR.prep(vname, ss, prog=g, win=wb)
        img, trim = pr.frame(want_trim=True)
        img, trim = WR.on_canvas(img, vname, win=wb), WR.on_canvas(trim, vname, win=wb)
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
    os.makedirs(SCR, exist_ok=True)
    {'states': lambda: states(vname, ss, tuple(fr) if fr else (0, 1)), 'door': lambda: door(vname, ss), 'under': lambda: under(vname, ss),
     'bib': lambda: bib(vname, ss), 'build': lambda: build(vname, ss, fr), 'resplit': lambda: resplit(vname, ss),
     'under2': lambda: under(vname, ss, reuse=True)}[what]()
