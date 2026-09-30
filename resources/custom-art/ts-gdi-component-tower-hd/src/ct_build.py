"""Build-up (17 frames) and the blinking lamp overlay (6 frames) for the component tower."""
import os
import ct_ra as R

# follows TS's GTCTWRMK: pad grows, pad with its sockets, the steel frame rises, the body is clad over it,
# the top plate goes on, it gets painted, and the house-colour ring comes on last
SEQ = [dict(pad=0.15, frame=0, clad=0, plate=0, paint=0, ring=0),
       dict(pad=0.30, frame=0, clad=0, plate=0, paint=0, ring=0),
       dict(pad=0.50, frame=0, clad=0, plate=0, paint=0, ring=0),
       dict(pad=0.70, frame=0, clad=0, plate=0, paint=0, ring=0),
       dict(pad=0.88, frame=0, clad=0, plate=0, paint=0, ring=0),
       dict(pad=1.00, frame=0, clad=0, plate=0, paint=0, ring=0),
       dict(pad=1.00, frame=0.20, clad=0, plate=0, paint=0, ring=0),
       dict(pad=1.00, frame=0.45, clad=0, plate=0, paint=0, ring=0),
       dict(pad=1.00, frame=0.70, clad=0, plate=0, paint=0, ring=0),
       dict(pad=1.00, frame=1.00, clad=0, plate=0, paint=0, ring=0),
       dict(pad=1.00, frame=1.00, clad=0.35, plate=0, paint=0, ring=0),
       dict(pad=1.00, frame=1.00, clad=0.70, plate=0, paint=0, ring=0),
       dict(pad=1.00, frame=1.00, clad=1.00, plate=0, paint=0, ring=0),
       dict(pad=1.00, frame=1.00, clad=1.00, plate=1, paint=0, ring=0),
       dict(pad=1.00, frame=1.00, clad=1.00, plate=1, paint=0.5, ring=0),
       dict(pad=1.00, frame=1.00, clad=1.00, plate=1, paint=1.0, ring=0),
       dict(pad=1.00, frame=1.00, clad=1.00, plate=1, paint=1.0, ring=1)]
LAMP = [0.05, 0.45, 1.0, 0.72, 0.30, 0.10]      # TS GTCTWR_A brightness, frame by frame

if __name__ == '__main__':
    import sys
    os.makedirs('ctwr/out', exist_ok=True)
    what = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if what == 'build':
        frames = [int(f) for f in sys.argv[2:]] or range(len(SEQ))
        for i in frames:
            img, trim = R.render(prog=SEQ[i], want_trim=True)
            img.save(f'ctwr/out/tower-build-{i:02d}.png'); trim.save(f'ctwr/out/tower-build-{i:02d}-trim.png')
            print('build', i, flush=True)
    elif what == 'lamp':
        img, trim, lamps = R.render(want_trim=True, lamp=LAMP)
        for i, l in enumerate(lamps):
            l.save(f'ctwr/out/tower-light-{i:02d}.png')
        print('lamp done')
