#!/usr/bin/env python3
"""Regenerate the TF_SidebarSkin[] table in redalert/dllinterface.cpp from the atlas metadata.

The DLL's crest/sidebar patch (docs/radar-crest-ram-spike.md) re-points every RA sidebar region
the launcher draws at its same-named TD counterpart for GDI/Nod players. The pairs come from
MT_COMMANDBAR_COMMON.MTD (scripts/cameo_work/), by name:

  UI_RA_SIDEBAR_<x>                 -> UI_SIDEBAR_<x>
  RA_UI_FRAME_TOOLTIP_SIDEBAR_<x>   -> UI_FRAME_TOOLTIP_SIDEBAR_<x>   (ALLIED_ variants too)
  UI_RA_SIDEBAR_BUILDBARBG_BLUE     -> UI_SIDEBAR_BUILDBARBG           (no TD blue variant)

Rules baked in: the RA radar bezel (UI_RA_SIDEBAR_RADARBG) is never paired (TD's plate is opaque
and covers the crest); the square SELL/REPAIR/MAP buttons pair with a centred square window of
TD's 260x78 bar (icon on the grille, bevels kept). Rewrites the table in place; the C++ around it
is untouched. Run from the repo root, then rebuild.
"""
import re
import struct
import sys

MTD = 'scripts/cameo_work/MT_COMMANDBAR_COMMON.MTD'
CPP = 'redalert/dllinterface.cpp'
BEZEL = 'UI_RA_SIDEBAR_RADARBG'
SQUARE_BUTTONS = ('BUTTON_SELL', 'BUTTON_REPAIR', 'BUTTON_MAP')


def read_regions():
    mtd = open(MTD, 'rb').read()
    regs = {}
    for m in re.finditer(rb'([A-Za-z0-9_]+)\.TGA', mtd):
        name = m.group(1).decode()
        j = m.end()
        while mtd[j] == 0:
            j += 1
        x, y, w, h = struct.unpack('<4i', mtd[j:j + 16])
        if 0 < w < 4000 and 0 < h < 4000:
            regs[name] = (x, y, w, h)
    return regs


def pairs(regs):
    out = []
    for n in sorted(regs):
        if n.startswith('UI_RA_SIDEBAR'):
            t = n.replace('UI_RA_SIDEBAR', 'UI_SIDEBAR')
            if t not in regs or n == BEZEL:
                continue
            if any(k in n for k in SQUARE_BUTTONS):
                tx, ty, tw, th = regs[t]
                out.append((n, t + ' (centred square window)', regs[n], (tx + (tw - th) // 2, ty, th, th)))
            else:
                out.append((n, t, regs[n], regs[t]))
        elif n.startswith('RA_UI_FRAME_TOOLTIP_SIDEBAR_'):
            t = n.replace('RA_UI_FRAME_TOOLTIP_SIDEBAR', 'UI_FRAME_TOOLTIP_SIDEBAR').replace('_ALLIED', '')
            if t in regs:
                out.append((n, t, regs[n], regs[t]))
    out.append(('UI_RA_SIDEBAR_BUILDBARBG_BLUE', 'UI_SIDEBAR_BUILDBARBG',
                regs['UI_RA_SIDEBAR_BUILDBARBG_BLUE'], regs['UI_SIDEBAR_BUILDBARBG']))
    return out


def main():
    regs = read_regions()
    rows = pairs(regs)
    lines = ['    {{%d, %d, %d, %d}, {%d, %d, %d, %d}}, // %s -> %s' % (*a, *b, n, t) for n, t, a, b in rows]
    src = open(CPP).read()
    head = 'static const TF_SkinPair TF_SidebarSkin[] = {'
    start = src.index(head)
    end = src.index('};', start) + 2
    new = head + '\n' + '\n'.join(lines) + '\n};'
    if src[start:end] == new:
        print('table unchanged (%d pairs)' % len(rows))
        return 0
    open(CPP, 'w').write(src[:start] + new + src[end:])
    print('table rewritten: %d pairs' % len(rows))
    return 0


if __name__ == '__main__':
    sys.exit(main())
