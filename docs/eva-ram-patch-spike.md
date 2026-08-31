# EVA mailbox RAM-patch — SOLVED (2026-09-01)

Lifts the last limit of the EVA era-mailbox: ClientG caches each localized sample once per boot,
so a faction switch WITHOUT relaunching kept the stale voice on already-heard lines. The DLL now
overwrites the cached blob in ClientG's memory at match start, so all five launcher-owned EVA
lines follow the picked faction across an in-session switch. **Verified in play, both directions,
all five lines (cannot-deploy, structure-sold, mission-accomplished, mission-failed, battle-
control-terminated), no crash.** Promoted to shipping (runs in release builds; logging is
`TF_DEV_BUILD`-only). Code: `TF_Patch_ClientG_Cache` / `TF_WriteFile_Into_Process`,
`dllinterface.cpp`.

## How it works

The sample cache lives in **ClientG.exe**, a separate process from the DLL (which runs in
**InstanceServerG.exe**). Same cross-process shape as the lobby resolver — reuse
`CreateToolhelp32Snapshot` → find `ClientG.exe` → `OpenProcess` → `VirtualQueryEx` walk. The
patch adds `PROCESS_VM_WRITE | PROCESS_VM_OPERATION` and `WriteProcessMemory`. Linux-host
`ptrace_scope` is irrelevant — these are Wine-internal APIs between the two game processes, and
`WriteProcessMemory` works under Proton (proven here).

At match start, for each line the DLL scans ClientG's `PAGE_READWRITE` regions for the WRONG
faction's 20-byte needle, computes the cached blob start (`hit − needle_fileoff`), and writes the
desired faction's payload over it. The blob is the whole WAV file (RIFF header included), so the
write replaces header + data and the sample plays in the new voice.

## The findings that made it work (in the order they bit us)

1. **Cache format = raw ADPCM file bytes**, in a `PAGE_READWRITE` region (stage-1 probe). So an
   in-place same-size overwrite is the mechanism — not decoded PCM.
2. **Writes must be same-size or ClientG crashes.** The TD and RA payload of a line differ in
   length; a longer-over-shorter write overran the blob and crashed ClientG (proven). Fix: pad
   each line's TD/RA pair to EQUAL byte length.
3. **`ffmpeg`'s power-of-two `block_align` (1024) loads mid-match but is SILENT at teardown.**
   The base game samples use `block_align=70` (classic C&C block). The mid-match sample loader
   tolerates 1024; the teardown loader silently rejects it. ffmpeg cannot emit block_align 70
   (it requires a power of two).
   - **NODEPLY / WON / LST** fire mid-match, so the re-encoded (mono, 44100, equal-length) payload
     is fine for them.
   - **BCT fires only at teardown**, so it must keep the BASE-format (block-70) payload. To make
     it equal-length without re-encoding, pad the base file with **trailing zero bytes after the
     data chunk** (the `data`-size header still bounds playback, so audio is untouched; the file
     grows to a common length so the cache write stays same-size). ClientG caches the whole
     padded file, so the same-size write holds.
4. **ClientG resolves the loose sample at LAUNCH — loose file if present, else base MEG — and
   caches it once.** Per-match disk writes do NOT refresh an already-cached sample in-session.
   A deploy that `rsync --delete`d the loose runtime files left them absent at launch, so ClientG
   cached the BASE MEG bytes; our needles (from our files) then could not match. **Fix: the loose
   runtime files (`RA{C,R}_SFX_EVA_{NODEPLY1,BCT1,MISNWON1,MISNLST1}_EN-US.WAV`) must exist at
   launch** — they now ship static (seeded from the RA payloads) so a fresh install caches our
   bytes. Never `--delete` them on deploy.
5. **A line is only cacheable after it has fired once.** BCT's first fire is at teardown, so it
   is not cached during its own match — but it persists after that first teardown, so the NEXT
   match's start-patch flips it. That is why the in-session switch works even for BCT.

## Shipping notes

- The patch runs in release builds and fails safe at every step (process not found, needle not
  found, write refused) — degrading to the disk-mailbox voice (first-fire-correct, stale-on-
  switch), never a crash. Diagnostic logging (`tf_cache_probe.log`) is `TF_DEV_BUILD`-only.
- Needles/offsets are regenerated whenever a payload is re-padded (the re-encode/pad changes the
  bytes). The generator picks a high-entropy 20-byte slice from the real audio (never the leading
  silence) and records its file offset.
- Cross-process `WriteProcessMemory` in a shipped mod could in principle trip aggressive AV/anti-
  cheat, but it targets only positively-identified sample blobs in the sibling game process the
  DLL already reads. No issue observed.
