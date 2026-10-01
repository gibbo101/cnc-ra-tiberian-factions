"""Final frames for the TS Harvester (with the refinery), into PKG/harvester/: 64 frames on the mod's 384x384 unit
canvas like TSHARV.ZIP (00-31 HARV's 32 facings, 32-63 HORV's: the truck with its tank off, drawn while it unloads),
each with a -trim.png.

    python3 harvfinal.py [ss] [frames]"""
import os, sys, time
import harvrender as HR
from pfinal import save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-tiberium-refinery-hd')

if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    ks = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else range(64)
    for k in ks:
        t0 = time.time()
        f, unl = HR.mod_frame(k)
        pr = HR.HarvPrep(f, unl, ss)
        img, trim = pr.frame_img()
        save(img, trim, f'{PKG}/harvester/harvester-{k:02d}.png')
        del pr
        print('harvester', k, '%.0fs' % (time.time() - t0), flush=True)
