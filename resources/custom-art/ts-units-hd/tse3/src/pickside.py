"""pickside.py UNIT - of the crawl fitted on TS's west side and on its east side (crawlbio.py, SIDE=w / e:
UNIT_crawlbio_w.json, UNIT_crawlbio_e.json), keep the one that matches TS's frames better (its mean loss over the
6 steps' rendered facings) as UNIT_crawlfit.json, and note the side in it."""
import json, shutil, sys
import numpy as np
u = sys.argv[1]
best = None
for side in ('w', 'e'):
    try:
        r = json.load(open('%s_crawlbio_%s.json' % (u, side)))
    except FileNotFoundError:
        continue
    f = float(np.mean([r[str(s)]['f'] for s in range(6) if 'f' in r[str(s)]]))
    io = float(np.mean([np.mean(list(r[str(s)]['iou'].values())) for s in range(6)]))
    print(u, side, 'loss %.4f' % f, 'iou %.3f' % io)
    if best is None or f < best[0]:
        best = (f, side, r)
f, side, r = best
r['side'] = side
json.dump(r, open('%s_crawlfit.json' % u, 'w'), default=float)
print(u, 'kept side', side)
