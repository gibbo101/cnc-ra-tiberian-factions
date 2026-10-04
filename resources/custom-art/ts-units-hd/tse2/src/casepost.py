"""casepost.py - a unit that carries a case (the Engineer's toolbox, the Medic's case): crawling, the case stands on the
ground ahead of his hand (pose key tbg 1), lying down carries it there from his hand over the two in-betweens (1/3,
2/3), getting up back (2/3, 1/3).   python3 casepost.py UNIT"""
import json, sys
unit = sys.argv[1]
cr = json.load(open('%s_crawl_frames.json' % unit))
for k, v in cr.items():
    v['Q']['tbg'] = 1.0
json.dump(cr, open('%s_crawl_frames.json' % unit, 'w'))
for name, first, vals in (('lie_down', 260, (1.0 / 3, 2.0 / 3)), ('get_up', 276, (2.0 / 3, 1.0 / 3))):
    d = json.load(open('%s_%s_frames.json' % (unit, name)))
    for k, v in d.items():
        v['Q']['tbg'] = vals[(int(k) - first) % 2]
    json.dump(d, open('%s_%s_frames.json' % (unit, name), 'w'))
print(unit, 'case on the ground: crawl', len(cr))
