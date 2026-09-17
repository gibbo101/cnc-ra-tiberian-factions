#!/usr/bin/env python3
"""Find ClientG's cached atlas-region records without knowing the atlas size.
A record is float32 {y/H, x/W, w/W, h/H}; x/w and y/h are size-independent, so match on those
and read the effective W = w / (w/W), H = h / (h/H) straight out of each hit.
usage (repo root, game running): clientg_ratio_scan.py [REGION_REGEX]"""
import re, struct, subprocess, sys
import numpy as np
MTD = 'scripts/cameo_work/MT_COMMANDBAR_COMMON.MTD'
mtd = open(MTD, 'rb').read()
regs = {}
for m in re.finditer(rb'([A-Za-z0-9_]+)\.TGA', mtd):
    j = m.end()
    while mtd[j] == 0: j += 1
    x, y, w, h = struct.unpack('<4i', mtd[j:j + 16])
    regs[m.group(1).decode()] = (x, y, w, h)
pat = re.compile(sys.argv[1] if len(sys.argv) > 1 else 'SIDEBAR_FACTIONLOGO|UI_SIDEBAR_RADARBG|TABICON')
targets = {n: r for n, r in regs.items() if pat.search(n) and r[0] > 0 and r[1] > 0 and 0 < r[2] < 4000 and 0 < r[3] < 4000}
pid = next(int(l.split()[0]) for l in subprocess.run(['ps', '-eo', 'pid,comm'], capture_output=True, text=True).stdout.splitlines()[1:] if l.split()[1] == 'ClientG.exe')
mem = open(f'/proc/{pid}/mem', 'rb', 0)
found = {}
for line in open(f'/proc/{pid}/maps'):
    p = line.split(); a, b = (int(v, 16) for v in p[0].split('-'))
    if p[1][:2] != 'rw' or p[1][3] != 'p' or b - a > (1 << 30) or b - a < 16: continue
    try: mem.seek(a); data = mem.read(b - a)
    except OSError: continue
    f = np.frombuffer(data[: len(data) // 4 * 4], np.float32)
    f0, f1, f2, f3 = f[:-3], f[1:-2], f[2:-1], f[3:]
    base = (f2 > 1e-5) & (f2 < 1.0) & (f3 > 1e-5) & (f3 < 1.0) & (f0 > 0) & (f0 < 1.0) & (f1 > 0) & (f1 < 1.0)
    idx = np.nonzero(base)[0]
    if not len(idx): continue
    g0, g1, g2, g3 = f0[idx], f1[idx], f2[idx], f3[idx]
    for n, (x, y, w, h) in targets.items():
        ok = (np.abs(g1 * w - g2 * x) < 2e-4 * g2 * x) & (np.abs(g0 * h - g3 * y) < 2e-4 * g3 * y)
        for k in np.nonzero(ok)[0]:
            We, He = w / float(g2[k]), h / float(g3[k])
            if 1000 < We < 40000 and 1000 < He < 40000:
                found.setdefault(n, []).append((hex(a + 4 * int(idx[k])), round(We, 2), round(He, 2)))
for n in sorted(found):
    print(f'{n:48} {regs[n]}  hits={len(found[n])}  ' + ' '.join(f'{addr}:W={We},H={He}' for addr, We, He in found[n][:4]))
print('targets', len(targets), 'matched', len(found))
