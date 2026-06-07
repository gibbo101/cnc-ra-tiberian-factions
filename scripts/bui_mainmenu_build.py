#!/usr/bin/env python3
"""
Rebuild RA_MAIN_MENU.BUI with our custom main-menu layout:
  - remove START NEW GAME (no GDI/Nod campaign exists)
  - promote MISSION SELECT to the top
  - close the gap so the remaining 9 buttons are a contiguous list

HOW THE .BUI WORKS (see memory: project-main-menu-bui-spike)
  File = 0x24-byte "CH" header + zlib stream.
    [0x08] u32 hash  -- NOT validated by the launcher (can be left stale)
    [0x10] u32       -- compressed length (must equal len(zlib stream))
  Decompressed payload = tag-based scene graph. Each menu button has a frame
  rect tag `02 10` (16 bytes = 4 LE floats x,y,w,h, screen-normalized) and a
  tint tag `03 10` (RGBA). Editing a button's rect Y repositions the whole
  button (frame + label move together).

THE KEY CONSTRAINT
  The launcher CRASHES on load if the BUI file size changes. So every edit must
  keep the DECOMPRESSED length constant (edit floats in place; never add/remove
  bytes), and after recompressing we PAD the file back to the original byte size
  with trailing zeros. zlib stops at its own stream end, so the pad is ignored.

GOTCHAS
  - Tag offsets must be found by exact `b'\x02\x10'` position; eyeballing is off.
  - Far-off-screen / negative coords get clamped (aspect-dependent, e.g. a button
    "peeks" at ultrawide), so we HIDE START by zero-size + alpha 0, not by moving
    it off-screen.
  - The frame rect that controls a given visible row is NOT inside that row's
    text block (off-by-one). We address rects by their absolute file offset,
    verified against expected values below.
"""
import sys, zlib, struct

BASE = sys.argv[1] if len(sys.argv) > 1 else 'scripts/bui_work/RA_MAIN_MENU.base.BUI'
OUT  = sys.argv[2] if len(sys.argv) > 2 else 'scripts/bui_work/RA_MAIN_MENU.edited.BUI'

d = open(BASE, 'rb').read()
ORIG_SIZE = len(d)
raw = bytearray(zlib.decompress(d[0x24:]))

def rd(off):
    return tuple(round(x, 4) for x in struct.unpack_from('<4f', raw, off + 2))

def set_rect(off, x, y, w, h):
    assert raw[off:off+2] == b'\x02\x10', f'no rect tag at {off}'
    struct.pack_into('<4f', raw, off + 2, x, y, w, h)

def set_y(off, y):
    assert raw[off:off+2] == b'\x02\x10', f'no rect tag at {off}'
    struct.pack_into('<f', raw, off + 2 + 4, y)

def set_alpha(off, a):
    assert raw[off:off+2] == b'\x03\x10', f'no tint tag at {off}'
    struct.pack_into('<f', raw, off + 2 + 12, a)

# --- verify we're operating on the expected base BUI -------------------------
EXPECT = {2739:(0.0052,0.0,0.9896,0.1049), 3128:(0.0052,0.0995,0.9896,0.1049),
          3517:(0.0052,0.1989,0.9896,0.1049), 3907:(0.0052,0.2984,0.9896,0.1049),
          8740:(0.0052,0.3978,0.9896,0.1049), 4293:(0.0052,0.4973,0.9896,0.1049),
          4685:(0.0052,0.5967,0.9896,0.1049), 7171:(0.0052,0.6962,0.9896,0.1049),
          7579:(0.0052,0.7957,0.9896,0.1049), 7966:(0.0052,0.8951,0.9896,0.1049)}
for off, exp in EXPECT.items():
    got = rd(off)
    assert got == exp, f'rect@{off} expected {exp} got {got} -- base BUI changed; re-derive offsets'

# --- hide START NEW GAME (rect@2739): zero-size + transparent ----------------
set_rect(2739, 0.0052, 0.0, 0.0001, 0.0001)   # ~zero size, in-range coords (no clamp)
set_alpha(2757, 0.0)                           # its tint alpha -> fully transparent

# --- reposition the 9 remaining buttons into a contiguous list --------------
# offset -> original row label -> new Y (0.0995 row spacing from 0.0)
set_y(3517, 0.0)      # MISSION SELECT   -> row 0 (top)
set_y(3128, 0.0995)   # LOAD GAME        -> row 1
set_y(3907, 0.1989)   # SKIRMISH & ONLINE-> row 2
set_y(8740, 0.2984)   # LAN MODE         -> row 3
set_y(4293, 0.3978)   # REPLAY / OBSERVER-> row 4
set_y(4685, 0.4973)   # BONUS GALLERY    -> row 5
set_y(7171, 0.5967)   # OPTIONS          -> row 6
set_y(7579, 0.6962)   # HELP             -> row 7
set_y(7966, 0.7957)   # EXIT GAME        -> row 8

# --- recompress, fix header, pad back to the ORIGINAL file size --------------
comp = zlib.compress(bytes(raw), 9)
hdr = bytearray(d[:0x24])
struct.pack_into('<I', hdr, 0x10, len(comp))
body = bytes(hdr) + comp
pad = ORIG_SIZE - len(body)
assert pad >= 0, f'edited BUI larger than original ({len(body)} > {ORIG_SIZE}); cannot pad'
open(OUT, 'wb').write(body + b'\x00' * pad)
print(f'wrote {OUT}: {len(body)+pad} bytes (orig {ORIG_SIZE}, pad {pad}, complen {len(comp)})')
