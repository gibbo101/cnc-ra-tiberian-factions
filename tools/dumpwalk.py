#!/usr/bin/env python3
"""Minimal Windows minidump walker for the 32-bit InstanceServerG crashes.
Prints the exception, locates RedAlert.dll, and scan-walks the faulting
thread's stack for return addresses inside the DLL."""
import struct, sys, subprocess

dmp_path, dll_path = sys.argv[1], sys.argv[2]
d = open(dmp_path, 'rb').read()

sig, ver, nstreams, dir_rva = struct.unpack_from('<IIII', d, 0)
assert sig == 0x504D444D, hex(sig)

streams = {}
for i in range(nstreams):
    stype, size, rva = struct.unpack_from('<III', d, dir_rva + i * 12)
    streams.setdefault(stype, []).append((rva, size))

def mdstring(rva):
    n, = struct.unpack_from('<I', d, rva)
    return d[rva + 4:rva + 4 + n].decode('utf-16-le')

# Modules (stream 4)
mods = []
rva, size = streams[4][0]
count, = struct.unpack_from('<I', d, rva)
off = rva + 4
for i in range(count):
    base, msize, _chk = struct.unpack_from('<QII', d, off)
    name_rva, = struct.unpack_from('<I', d, off + 0x14)
    mods.append((base, msize, mdstring(name_rva)))
    off += 108
def mod_of(addr):
    for base, msize, name in mods:
        if base <= addr < base + msize:
            return name, base
    return None, None

# Memory ranges (stream 5 = MemoryListStream)
mem = []
if 5 in streams:
    rva, size = streams[5][0]
    count, = struct.unpack_from('<I', d, rva)
    off = rva + 4
    for i in range(count):
        start, dsize, drva = struct.unpack_from('<QII', d, off)
        mem.append((start, dsize, drva))
        off += 16
def read_mem(addr, ln):
    for start, dsize, drva in mem:
        if start <= addr and addr + ln <= start + dsize:
            o = drva + (addr - start)
            return d[o:o + ln]
    return None

# Exception (stream 6)
rva, size = streams[6][0]
tid, _pad = struct.unpack_from('<II', d, rva)
code, flags, rec, addr = struct.unpack_from('<IIQQ', d, rva + 8)
nparams, _p2 = struct.unpack_from('<II', d, rva + 32)
params = struct.unpack_from('<8Q', d, rva + 40)[:nparams]
ctx_size, ctx_rva = struct.unpack_from('<II', d, rva + 8 + 152)
# x86 CONTEXT: Eip at offset 0xB8, Esp at 0xC4, Ebp at 0xB4
eip, = struct.unpack_from('<I', d, ctx_rva + 0xB8)
esp, = struct.unpack_from('<I', d, ctx_rva + 0xC4)
ebp, = struct.unpack_from('<I', d, ctx_rva + 0xB4)

print(f'exception code=0x{code:08X} at 0x{addr:08X} thread={tid}')
if nparams >= 2 and code == 0xC0000005:
    kind = {0: 'READ', 1: 'WRITE', 8: 'EXEC'}.get(params[0], params[0])
    print(f'  access violation: {kind} of address 0x{params[1]:08X}')
print(f'  eip=0x{eip:08X} esp=0x{esp:08X} ebp=0x{ebp:08X}')
name, base = mod_of(eip)
print(f'  eip in module: {name} base=0x{base:X}' if name else '  eip not in any module')

# link-time image base of the DLL
out = subprocess.run(['i686-w64-mingw32-objdump', '-p', dll_path],
                     capture_output=True, text=True).stdout
link_base = 0
for line in out.splitlines():
    if 'ImageBase' in line:
        link_base = int(line.split()[1], 16)
print(f'DLL link base 0x{link_base:X}')

ra_base = None
for b, s, n in mods:
    if 'REDALERT' in n.upper():
        ra_base = b
        print(f'RedAlert.dll runtime base 0x{b:X} size 0x{s:X}')
if ra_base is None:
    print('RedAlert.dll NOT in module list!')
    sys.exit(1)

def sym(vaddr):
    out = subprocess.run(['i686-w64-mingw32-addr2line', '-e', dll_path, '-f', '-C', hex(vaddr)],
                         capture_output=True, text=True).stdout.strip().splitlines()
    return ' '.join(out)

candidates = []
if name and 'REDALERT' in name.upper():
    candidates.append(('EIP', link_base + (eip - ra_base)))

# scan-walk the stack
stack = read_mem(esp, 0x3000)
if stack:
    for i in range(0, len(stack) - 3, 4):
        val, = struct.unpack_from('<I', stack, i)
        m, b = mod_of(val)
        if m and 'REDALERT' in m.upper():
            candidates.append((f'stack+{i:#x}', link_base + (val - ra_base)))
else:
    print('no stack memory captured for esp')

for tag, va in candidates[:40]:
    print(f'{tag:>12}: {hex(va)}  {sym(va)}')
