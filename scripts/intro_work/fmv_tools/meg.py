#!/usr/bin/env python3
"""Streaming reader for C&C Remastered .MEG archives (reads only the index,
then seeks to each entry, so multi-GB MEGs never load into RAM).

  meg.py list    <meg> [substring]
  meg.py extract <meg> <exact-or-substring> <outdir>   (copies in 16 MB chunks)

Format mirrors scripts/meg_extract.py in the Tiberian Factions repo."""
import os, struct, sys

REC = 20

def index(path):
    with open(path, 'rb') as f:
        head = f.read(24)
        off = 0
        magic = struct.unpack_from('<I', head, 0)[0]
        if magic in (0xFFFFFFFF, 0x8FFFFFFF):
            off += 8
        off += 4
        nfiles, nstrings, stsize = struct.unpack_from('<III', head, off)
        off += 12
        f.seek(off)
        st = f.read(stsize)
        strings = []
        p = 0
        for _ in range(nstrings):
            n = struct.unpack_from('<H', st, p)[0]; p += 2
            strings.append(st[p:p+n].decode('latin-1')); p += n
        f.seek(off + stsize)
        tab = f.read(nfiles * REC)
        out = []
        for i in range(nfiles):
            _fl, _crc, _idx, size, doff, ni = struct.unpack_from('<HIiIIH', tab, i*REC)
            out.append((strings[ni], size, doff))
        return out

def extract(path, pattern, outdir):
    os.makedirs(outdir, exist_ok=True)
    ents = index(path)
    exact = [e for e in ents if e[0].lower() == pattern.lower()]
    sel = exact or [e for e in ents if pattern.lower() in e[0].lower()]
    res = []
    with open(path, 'rb') as f:
        for name, size, doff in sel:
            dst = os.path.join(outdir, os.path.basename(name.replace('\\', '/')))
            f.seek(doff)
            left = size
            with open(dst, 'wb') as o:
                while left:
                    chunk = f.read(min(left, 16 << 20))
                    if not chunk:
                        raise IOError('short read')
                    o.write(chunk); left -= len(chunk)
            res.append(dst)
            print(f'extracted {name} ({size} bytes) -> {dst}')
    return res

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'list':
        pat = sys.argv[3].lower() if len(sys.argv) > 3 else None
        for n, s, _ in index(sys.argv[2]):
            if pat is None or pat in n.lower():
                print(f'{s:>12}  {n}')
    elif cmd == 'extract':
        extract(sys.argv[2], sys.argv[3], sys.argv[4])
