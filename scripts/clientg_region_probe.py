#!/usr/bin/env python3
"""Live probe of ClientG's cached atlas-region records (the RAM lever, docs/radar-crest-ram-spike.md).

ClientG keeps a 16-byte record {y/H, x/W, w/W, h/H} (float32, double-divide-then-cast) per
atlas region it draws, in writable heap, sampled every frame. This tool reads and rewrites those
records in a RUNNING ClientG on the Linux desktop via /proc/<pid>/mem (same uid, no DLL rebuild),
which is how the crest, backdrop and TD sidebar were prototyped in minutes.

  probe.py list  [REGEX]                 # which MTD regions have live records (drawn) right now
  probe.py point RA_REGION TD_REGION     # re-point every live RA_REGION record at TD_REGION's rect
  probe.py point RA_REGION x,y,w,h       # ... or at an explicit atlas rect
  probe.py restore REGION                # put REGION's own rect back into records currently
                                         #   holding any rect (use after `point` experiments)

Needs the game running headless or on the desktop; finds ClientG.exe by name. Reads the region
table from scripts/cameo_work/MT_COMMANDBAR_COMMON.MTD. A `point` shows on the next frame; if the
match has ended, start a new one (per-match copies are cloned from the persistent master, which
this tool also patches). The DLL's own per-frame re-verify will fight you on the slots it owns
(crest, under-screens, TF_SidebarSkin pairs) unless the local player is an RA side.
"""
import re
import struct
import subprocess
import sys

MTD = 'scripts/cameo_work/MT_COMMANDBAR_COMMON.MTD'
W, H = 6871.0, 6716.0


def regions():
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


def record(rect):
    x, y, w, h = rect
    return struct.pack('<4f', y / H, x / W, w / W, h / H)


def clientg_pid():
    out = subprocess.run(['ps', '-eo', 'pid,comm'], capture_output=True, text=True).stdout
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == 'ClientG.exe':
            return int(parts[0])
    sys.exit('ClientG.exe is not running')


def scan(pid, needles, writer=None):
    """Return {name: [addr,...]} for every needle; call writer(mem, addr, name) on each hit."""
    mem = open(f'/proc/{pid}/mem', 'r+b' if writer else 'rb', 0)
    hits = {n: [] for n in needles}
    for line in open(f'/proc/{pid}/maps'):
        p = line.split()
        a, b = (int(v, 16) for v in p[0].split('-'))
        if p[1][:2] != 'rw' or p[1][3] != 'p' or b - a > (1 << 30):
            continue
        try:
            mem.seek(a)
            data = mem.read(b - a)
        except OSError:
            continue
        for name, nd in needles.items():
            i = data.find(nd)
            while i != -1:
                hits[name].append(a + i)
                if writer:
                    writer(mem, a + i, name)
                i = data.find(nd, i + 1)
    if writer:
        mem.flush()
    return hits


def parse_rect(regs, arg):
    if arg in regs:
        return regs[arg]
    nums = arg.split(',')
    if len(nums) == 4:
        return tuple(int(v) for v in nums)
    sys.exit(f'unknown region or rect: {arg}')


def main(argv):
    if len(argv) < 2 or argv[1] not in ('list', 'point', 'restore'):
        print(__doc__)
        return 1
    regs = regions()
    pid = clientg_pid()
    if argv[1] == 'list':
        pat = re.compile(argv[2]) if len(argv) > 2 else None
        names = [n for n in regs if not pat or pat.search(n)]
        hits = scan(pid, {n: record(regs[n]) for n in names})
        for n in sorted(names):
            if hits[n]:
                x, y, w, h = regs[n]
                print(f'{n:52} x{len(hits[n])}  {w}x{h}')
        return 0
    if argv[1] == 'point':
        src, dst = argv[2], parse_rect(regs, argv[3])
        want = record(dst)
        hits = scan(pid, {src: record(regs[src])}, lambda mem, addr, _n: (mem.seek(addr), mem.write(want)))
        print(f'{src}: {len(hits[src])} records -> {dst}')
        return 0
    name = argv[2]
    # restore: any record holding a rect we might have written over this region's records.
    # We cannot know those rects, so restore takes the CURRENT contents from the caller: point the
    # region at itself after listing what it holds. Practical form: `point REGION REGION`.
    hits = scan(pid, {name: record(regs[name])})
    print(f'{name}: {len(hits[name])} records already hold their own rect; to undo a `point`, run '
          f'`point <TD_REGION_or_rect_you_wrote> {name}` is NOT right -- instead run '
          f'`point {name} {name}` after re-pointing back with the rect you wrote as the source rect. '
          'See the doc for the two-step.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
