"""firestart.py UNIT [key=value ...]: the fire's start pose, the unit's standing pose with the given changes (the rifle
raised to the shoulder, say) -> UNIT_fire_start.json"""
import json, sys
u = sys.argv[1]
Q = dict(json.load(open('%s_shape.json' % u))['Q'])
for kv in sys.argv[2:]:
    k, v = kv.split('='); Q[k] = float(v)
json.dump({'Q': Q}, open('%s_fire_start.json' % u, 'w'), default=float)
print('fire start', {kv.split('=')[0]: Q[kv.split('=')[0]] for kv in sys.argv[2:]})
