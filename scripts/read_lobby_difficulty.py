#!/usr/bin/env python3
"""Read the skirmish lobby's per-slot AI difficulty out of ClientG.exe RAM (Linux dev).

This is the host-side PoC that proved per-slot difficulty is recoverable (2026-07-18).
The DLL will do the equivalent read in-process (InstanceServerG -> ClientG via
ReadProcessMemory) in phase A; this script is the reference + a live sanity check.
Design + full context: docs/lobby-difficulty-ram-spike.md.

Usage:
    # find the stable in-match ClientG pid (NOT the transient wrapper pids):
    pgrep -f "ClientG.exe GAME_INDEX=0 REDALERT"
    python3 scripts/read_lobby_difficulty.py <pid>

Requirements: run against the STABLE in-match ClientG process (the one that survives
the whole match). ptrace_scope=1 on this machine denies /proc/<pid>/mem for freshly
spawned/transient pids; the in-match game process reads fine.

Record layout (empirically stable, from the frozen Jan-2025 client):
    ASCII 'AIPLAYERn\\0' at record start
    +0x50  int32  slot index (1-based)
    +0x64  int32  DIFFICULTY  (1=Easy, 2=Medium, 3=Hard)   <-- the field
    +0x68  int32  slot index (repeat)
    record stride = 0xA8; array holds one record per AI slot.
No hardcoded addresses: the array is found by signature (name + validated fields).
"""
import sys, re, struct

DIFF = {1: "EASY", 2: "MEDIUM", 3: "HARD"}
STRIDE = 0xA8
OFF_SLOT = 0x50
OFF_DIFF = 0x64


def rw_regions(pid):
    out = []
    with open(f"/proc/{pid}/maps") as f:
        for line in f:
            m = re.match(r"([0-9a-f]+)-([0-9a-f]+) (\S+)", line)
            if m and "rw" in m.group(3):
                s, e = int(m.group(1), 16), int(m.group(2), 16)
                if e - s <= 512 * 1024 * 1024:
                    out.append((s, e))
    return out


def find_array(mem, regions):
    """Return the address of the AIPLAYER1 record whose fields validate, else None."""
    for s, e in regions:
        try:
            mem.seek(s)
            data = mem.read(e - s)
        except (OSError, ValueError):
            continue
        for m in re.finditer(rb"AIPLAYER1\x00", data):
            i = m.start()
            if i + OFF_DIFF + 4 > len(data):
                continue
            slot = struct.unpack_from("<i", data, i + OFF_SLOT)[0]
            diff = struct.unpack_from("<i", data, i + OFF_DIFF)[0]
            if slot == 1 and diff in DIFF:
                return s + i
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    pid = int(sys.argv[1])
    with open(f"/proc/{pid}/mem", "rb", 0) as mem:
        base = find_array(mem, rw_regions(pid))
        if base is None:
            print("AIPLAYER record array not found (is a match loaded? right pid?)")
            return 1
        print(f"record array @ {base:#x}")
        for k in range(8):  # max AI slots; stop at first non-record
            mem.seek(base + k * STRIDE)
            r = mem.read(STRIDE)
            name = r[:12].split(b"\x00")[0].decode("latin1")
            if not name.startswith("AIPLAYER"):
                break
            slot = struct.unpack_from("<i", r, OFF_SLOT)[0]
            diff = struct.unpack_from("<i", r, OFF_DIFF)[0]
            print(f"  slot {slot}: {DIFF.get(diff, '?' + str(diff))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
