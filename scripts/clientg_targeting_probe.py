#!/usr/bin/env python3
"""Find the ClientG dword that flips while a superweapon is being targeted.

The launcher enters a targeting input mode when a ready super cameo is clicked and none of it
reaches the DLL. Toggle idle<->targeting and keep dwords whose value depends ONLY on that mode,
not on cursor position: each state is sampled at two mouse positions and must read identically at
both (kills cursor/target-pixel dwords), idle must differ from targeting, and it must hold across
every cycle. Stack regions (self-referential churn) are skipped.

  clientg_targeting_probe.py [cycles] [cameo_x cameo_y]
"""
import os
import subprocess
import sys
import time

import numpy as np

MAXREG = 96 << 20
POS1 = (900, 520)
POS2 = (520, 760)


def pid():
    o = subprocess.run(['pgrep', '-x', 'ClientG.exe'], capture_output=True, text=True).stdout.split()
    if not o:
        sys.exit('ClientG.exe not running')
    return int(o[0])


def regions(p):
    out = []
    for line in open(f'/proc/{p}/maps'):
        c = line.split()
        a, b = (int(v, 16) for v in c[0].split('-'))
        if c[1][:2] == 'rw' and c[1][3] == 'p' and (b - a) <= MAXREG:
            out.append((a, b))
    return out


def snap(p, regs):
    mem = open(f'/proc/{p}/mem', 'rb', 0)
    d = {}
    for a, b in regs:
        try:
            mem.seek(a)
            buf = mem.read(b - a)
        except OSError:
            continue
        n = len(buf) & ~3
        arr = np.frombuffer(buf[:n], dtype='<u4')
        lo, hi = a, a + n
        if n and ((arr >= lo) & (arr < hi)).mean() > 0.20:
            continue
        d[a] = arr.copy()
    mem.close()
    return d


def xdo(*a):
    subprocess.run(['xdotool', *a], env=dict(os.environ, DISPLAY=':2'))


def park(pos):
    xdo('mousemove', *map(str, pos))
    time.sleep(0.45)


def to_idle():
    xdo('key', 'Escape')
    time.sleep(0.25)
    xdo('key', 'Escape')
    time.sleep(0.25)


def enter_targeting(cx, cy):
    xdo('mousemove', str(cx), str(cy))
    time.sleep(0.4)
    xdo('click', '1')
    time.sleep(0.3)


def flips(A, B):
    """{addr:(A,B)} for dwords present in both regions where A != B (small set)."""
    out = {}
    for a in set(A) & set(B):
        x, y = A[a], B[a]
        n = min(len(x), len(y))
        for i in np.nonzero(x[:n] != y[:n])[0]:
            out[a + 4 * int(i)] = (int(x[i]), int(y[i]))
    return out


def val(snapshot, addr):
    base = addr & ~0
    # find region containing addr
    for a, arr in snapshot.items():
        if a <= addr < a + 4 * len(arr):
            return int(arr[(addr - a) // 4])
    return None


def main():
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    cx = int(sys.argv[2]) if len(sys.argv) > 2 else 1607
    cy = int(sys.argv[3]) if len(sys.argv) > 3 else 585
    p = pid()
    regs = regions(p)
    common = None
    for c in range(cycles):
        to_idle(); park(POS1); I1 = snap(p, regs)
        park(POS2); I2 = snap(p, regs)
        enter_targeting(cx, cy); park(POS1); T1 = snap(p, regs)
        park(POS2); T2 = snap(p, regs)
        to_idle()
        cand = flips(I1, T1)  # differ idle vs targeting at POS1 (small)
        cur = {}
        for a, (iv, tv) in cand.items():
            i2 = val(I2, a); t2 = val(T2, a)
            if i2 == iv and t2 == tv:  # position-independent in BOTH states
                cur[a] = (iv, tv)
        common = cur if common is None else {k: v for k, v in cur.items() if k in common and common[k] == v}
        print(f'cycle {c + 1}: flip@pos1 {len(cand)}, pos-independent {len(cur)}, intersection {len(common)}', flush=True)
    small = {k: v for k, v in common.items() if v[0] < 0x100000 and v[1] < 0x100000}
    print(f'\nstable position-independent flips: {len(common)}; small-valued: {len(small)}')
    for k in sorted(small, key=lambda k: (small[k][0], small[k][1])):
        print(f'  {k:#010x}  idle={small[k][0]:<8} targeting={small[k][1]}')
    big = {k: v for k, v in common.items() if k not in small}
    if big:
        print(f'\n(large-valued flips, likely pointers: {len(big)})')
        for k in sorted(big)[:20]:
            print(f'  {k:#010x}  idle={big[k][0]:#x} targeting={big[k][1]:#x}')


if __name__ == '__main__':
    main()
