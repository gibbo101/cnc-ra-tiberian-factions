"""render frames part::n of 0..95 into PKG/frames (skipping finished ones)."""
import sys, os, time
import hvrrender as HR
from frameio import save
part, n, pkg = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
m = HR.model()
for k in list(range(96))[part::n]:
    out = '%s/frames/tshvr-%04d.png' % (pkg, k)
    if os.path.exists(out) and os.path.exists(out[:-4] + '-trim.png'):
        continue
    t0 = time.time()
    img, trim = HR.frame(k, 4, True, m=m)
    save(img, trim, out)
    print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
print('done', flush=True)
