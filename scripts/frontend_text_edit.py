import struct, re

d = bytearray(open('/tmp/loc/MASTERTEXTFILE_EN-US.LOC', 'rb').read())
orig = len(d)
count = struct.unpack_from('<I', d, 0)[0]
VB = 4 + 12 * count
recs = []
vo = VB
for i in range(count):
    h, vl, b = struct.unpack_from('<3I', d, 4 + 12 * i)
    recs.append([vo, vl, b])
    vo += 2 * vl
ko = vo
for r in recs:
    r.append(ko)
    ko += r[2]

# country -> faction name
M = {'SPAIN': 'GDI', 'TURKEY': 'Nod', 'GREECE': 'Allies', 'RUSSIA': 'Soviet',
     'ENGLAND': 'Allies', 'GERMANY': 'Allies', 'FRANCE': 'Allies', 'UKRAINE': 'Soviet'}
NN = {'3': 'SPAIN', '4': 'GREECE', '5': 'RUSSIA', '6': 'ENGLAND',
      '7': 'UKRAINE', '8': 'GERMANY', '9': 'FRANCE', '10': 'TURKEY'}


def target(key):
    m = re.fullmatch(r'TEXT_FACTION_NAME_FACTION_(\d+)', key)
    if m and m.group(1) in NN:
        return M[NN[m.group(1)]]
    m = re.fullmatch(r'TEXT_FACTION_(?:BONUS|REDALERT)_([A-Z]+)', key)
    if m and m.group(1) in M:
        return M[m.group(1)]
    return None


edited = 0
skipped = []
for vo, vl, b, ko_ in recs:
    key = d[ko_:ko_ + b].decode('latin1', 'replace')
    t = target(key)
    if t is None:
        continue
    if len(t) > vl:
        skipped.append((key, t, vl))
        continue
    old = d[vo:vo + 2 * vl].decode('utf-16-le', 'replace')
    d[vo:vo + 2 * vl] = t.ljust(vl).encode('utf-16-le')
    print(f"  {key:34} {old[:32]!r:36} -> {t!r}")
    edited += 1

assert len(d) == orig, (len(d), orig)
open('/tmp/loc_full.LOC', 'wb').write(bytes(d))
print(f"edited {edited}, size {len(d)} (unchanged)")
if skipped:
    print("SKIPPED (target longer than slot — kept original):")
    for k, t, vl in skipped:
        print(f"  {k}: '{t}' needs {len(t)} > slot {vl}")
