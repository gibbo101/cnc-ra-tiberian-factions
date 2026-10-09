"""pronestart.py UNIT: the prone fire's start pose, the crawl's first step (frame 86, facing north) -> UNIT_prone_fire_start.json"""
import json, sys
u = sys.argv[1]
fr = json.load(open('%s_crawl_frames.json' % u))
k = min(int(x) for x in fr)
json.dump({'Q': fr[str(k)]['Q']}, open('%s_prone_fire_start.json' % u, 'w'), default=float)
print('prone start from frame', k)
