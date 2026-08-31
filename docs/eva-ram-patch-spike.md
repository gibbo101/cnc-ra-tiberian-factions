# EVA mailbox RAM-patch spike

**Goal:** lift the one residual limit of the EVA era-mailbox (`known-issues.md`): ClientG
lazy-loads each localized sample at its FIRST FIRE of the launcher session and caches it for the
whole boot, so an in-session faction switch keeps the earlier voice on already-heard lines. The
disk mailbox (`TF_Mailbox_Write_EVA_Voice`, `dllinterface.cpp`) fixes first-fire-per-boot; this
spike patches the *cached* copy so every subsequent fire is correct too.

Opened 2026-08-31 right after the EVA arc merged (origin/main `962a4797`). Design only so far —
no probe code built (the prefix surface was busy with the drop-pods round).

## Architecture

The cache lives in **ClientG.exe**, a separate process from the DLL (which runs inside
**InstanceServerG.exe**). This is the SAME cross-process shape the lobby resolver already ships:
`CreateToolhelp32Snapshot` → find `ClientG.exe` → `OpenProcess` → scan writable regions
(`dllinterface.cpp` `TF_Read_Lobby_AI_Difficulties` + `TF_Count_Referrers`, Route B). Reuse that
machinery verbatim; add `PROCESS_VM_WRITE | PROCESS_VM_OPERATION` to the open flags and
`WriteProcessMemory` for the patch.

Linux-host `ptrace_scope=1` is irrelevant — Wine implements OpenProcess/Read/WriteProcessMemory
between the two in-session game processes; the proven lobby reads confirm it works under Proton.
`WriteProcessMemory` under Proton is the one unproven Windows API here (reads are proven).

## Stage 1 — READ-ONLY probe (do this first, no writes)

At match start, scan ClientG's writable private memory for known sample needles and log what is
found. Needles below are from `RAR_SFX_EVA_MISNLST1_EN-US.WAV` (RA) and `TDR_SFX_EVA_FAIL1`
(TD) — the two payloads for the mission-failed line, chosen because they DIFFER, so a hit also
reads which faction is currently cached. Slice = 24 bytes from the data chunk (offset past
`data`+8):

| where in data chunk | RA (MISNLST1) hex | TD (FAIL1) hex |
|---|---|---|
| +4000 | `0cf0110037511ecf011cbe011323321231f9edbce0421f03` | `ddeedd11332200ee116611bbaaee003333eebbee000033ff` |
| +8000 | `fdf140ef0c902410ce0611f011cd152220cd3711011ff221` | `11eeddffffccff226611222200110011ee0033ffcc226611` |

(The file heads are silence/ADPCM-header — all zeros — so never needle the start.)

Log per needle: hit count, addresses, region protect flags. **Decision the probe answers:**
- ADPCM slice found → cache holds FILE BYTES → in-place same-size patch is trivial (our TD and
  RA payloads are the base samples; pad the pair to equal length once and every write is
  same-size).
- ADPCM slice NOT found → cache likely holds DECODED PCM. Re-probe with an ffmpeg-decoded
  s16le slice from the same mid-data region. PCM copies differ in length between payloads, so a
  same-size write needs equal-length (silence-padded) PCM, or patch only the overlapping prefix.
- Multiple hits → patch them all (decoded + file copy may coexist; or per-variant slots).

Needle generator: `meg_extract.py` pulls the base samples; the slice offsets above regenerate
from any of the `TF_MBX_*` payloads in `resources/.../Data/AUDIO/EN-US/`.

## Stage 2 — the patch (only after stage 1)

At match start, for each of the 4 mailbox lines: find the cached blob by needle, overwrite the
data region with the era-correct payload via `WriteProcessMemory` (same-size). Keep the disk
write too — it covers the first fire before anything is cached. Gate everything on `TF_DEV_BUILD`
for the probe logging; the shipping patch runs unconditionally but silently.

## Risks / open questions

- WriteProcessMemory under Proton: unproven. Stage 1 stays read-only until a build confirms the
  reads land where expected; only then attempt a write.
- Cache lifetime vs match-start timing: the disk rewrite already happens at `CNC_Start_Instance*`
  tails; the memory patch can ride the same call, but the sample may not be cached until its
  first fire THIS boot — so a patch at match start only helps lines cached in a PRIOR match
  (exactly the stale-switch case we target). First-ever fire is still disk-served. Good.
- Same-size discipline: pad each TD/RA payload pair to identical byte length in the repo so the
  writer never changes a blob's size (a resize would corrupt ClientG's length bookkeeping).
