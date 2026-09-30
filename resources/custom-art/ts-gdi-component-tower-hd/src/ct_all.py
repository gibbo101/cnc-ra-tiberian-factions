"""Render every component tower frame into ctwr/out with the delivery names."""
import sys, os
import ct_ra as R, ct_damage as D, ct_build as B
os.makedirs('ctwr/out', exist_ok=True)
what = sys.argv[1]
if what == 'tower':
    for lvl in (0, 1, 2):
        dmg = D.make(lvl, seed=10 + lvl) if lvl else None
        img, trim = R.render(damage=dmg, want_trim=True)
        img.save(f'ctwr/out/component-tower-{lvl:02d}.png'); trim.save(f'ctwr/out/component-tower-{lvl:02d}-trim.png')
        print('tower', lvl, flush=True)
    img, trim, lamps = R.render(want_trim=True, lamp=B.LAMP)
    for i, l in enumerate(lamps):
        l.save(f'ctwr/out/component-tower-light-{i:02d}.png')
    print('light', flush=True)
elif what == 'couplings':
    for lvl in [int(a) for a in sys.argv[2:]]:
        dmg = D.make(lvl, seed=10 + lvl) if lvl else None
        cd = D.coupling_damage(lvl) if lvl else None
        for s in 'NESW':
            R.render_coupling(s, damage=dmg, cdamage=cd).save(f'ctwr/out/coupling-{s}-{lvl:02d}.png')
        print('couplings', lvl, flush=True)
elif what == 'ends':
    # the wall coming into the tower's cell up to the sleeve, per kind of wall (tower canvas): from the
    # south to the sleeve's mouth (drawn after the couplings); from the north (drawn before the tower) to
    # the middle of the sleeve. 00 / 01 / 02 follow the tower.
    import numpy as np
    import gates2 as G2, nodends as NE, brik_ends as BE
    from PIL import Image
    kinds = sys.argv[2:] or ['gdi', 'nod', 'brik']
    y_mouth = 64.0 + R.sleeve_outer_u() * R.SYF - 1.7          # ground row of the wall's end, in the mouth
    length = dict(S=128.0 - y_mouth, N=64.0 - R.CPL['sl_c'] * R.SYF)
    foot = int(np.ceil(64.0 + R.sleeve_outer_u() * R.SYF))     # screen row of the sleeve's foot (cell)
    states = ((0, 'ok'), (1, 'damaged'), (2, 'destroyed'))

    def brik(side, lvl):
        """RA's concrete wall, cut from its own HD frames. South: the straight run up into the sleeve's
        mouth, its shadow kept off the sleeve; north: the gates' piece (BRIK's end cap ~30 px in)."""
        if lvl == 2:
            a = BE.destroyed(side)
        elif side == 'N':
            a = BE.piece('N', 16 * lvl)
        else:
            a = BE.load(16 * lvl + 5).copy()
            rows = np.arange(128)[:, None] * np.ones((1, 128))
            a[..., 3] = np.where(rows < round(y_mouth) - 24, 0, a[..., 3])
            shadow = (a[..., :3].max(axis=2) < 12) & (a[..., 3] < 250)
            a[..., 3] = np.where(shadow & (rows < foot), 0, a[..., 3])
        return Image.fromarray(np.clip(a, 0, 255).round().astype(np.uint8), 'RGBA')

    for kind in kinds:
        for side in 'NS':
            for lvl, st in states:
                if kind == 'gdi':
                    piece = G2.EndPiece(side, st, length=length[side]).render()
                elif kind == 'nod':
                    piece = NE.NodEndPiece(side, st, length=length[side]).render()
                else:
                    piece = brik(side, lvl)
                c = Image.new('RGBA', (R.CW, R.CH), (0, 0, 0, 0))
                c.paste(piece, (R.OX, R.OY))
                c.save(f'ctwr/out/end-{kind}-{side}-{lvl:02d}.png')
                print('end', kind, side, lvl, flush=True)
elif what == 'build':
    for i in [int(a) for a in sys.argv[2:]]:
        img, trim = R.render(prog=B.SEQ[i], want_trim=True)
        img.save(f'ctwr/out/component-tower-build-{i:02d}.png'); trim.save(f'ctwr/out/component-tower-build-{i:02d}-trim.png')
        print('build', i, flush=True)
