# EVA mailbox RAM patch

**Status:** Reference; shipped in 5.0.0. The launcher-owned EVA lines follow the faction across an
in-session switch by a RAM write into ClientG's cached samples.

Lifts the last limit of the EVA era-mailbox: ClientG caches each localized sample once per boot,
so a faction switch WITHOUT relaunching kept the stale voice on already-heard lines. The DLL now
overwrites the cached blob in ClientG's memory at match start, so all nine launcher-owned EVA
lines in `tf_eva_mailbox.h` (`BCT1`, `MISNLST1`, `MISNWON1`, `NODEPLY1`, `NOPOWR1`, `PROGRES1`,
`REPAIR1`, `SAVE1`, `SLCTTGT1`, each on both audio channels) follow the picked faction across an
in-session switch. Structure-sold is not one of them: the DLL routes it (`SpeechTD` / `SpeechTS` in
`audio.cpp`). **Verified in play, both directions, on cannot-deploy, mission-accomplished,
mission-failed and battle-control-terminated, no crash.** Promoted to shipping (runs in release builds; logging is
`TF_DEV_BUILD`-only). Code: `TF_Patch_ClientG_Cache` / `TF_Replace_File_In_Process`,
`dllinterface.cpp`.

## How it works

The method (seed files at launch, the cached copy as the whole WAV in ClientG's read-write heap, a 20-byte needle
per recording, the whole-recording compare before each write) and its traps are on the field manual's
[EVA voice lines the launcher plays](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/launcher-eva-lines-by-faction.md#part-two-overwrite-the-cached-copy), Part one, Part two and Traps. The cross-process
calls are on its [Re-pointing launcher UI art in memory](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#the-method), The method.
In TF, `TF_Replace_File_In_Process` does the compare and the write, the same cross-process shape as the
lobby resolver (`lobby-ambiguity-findings.md`). Linux's `ptrace_scope` doesn't apply: these
are Wine-internal calls between the two game processes.

## The findings, as TF applies them

1. **The cache holds raw file bytes**, so the patch overwrites in place.
2. **Same size or crash.** Each line's payloads are built to one byte length.
3. **The teardown loader wants `block_align` 70.** `NODEPLY`, `MISNWON` and `MISNLST` play mid-match, so their
   re-encoded payloads (mono, 44,100 Hz, equal length) are fine. `BCT` plays only at teardown, so every payload of
   it keeps `block_align` 70: the base file padded with trailing zeros to the common length, or
   `scripts/msadpcm.py`'s encode (`ts-gdi-faction.md`).
4. **ClientG picks loose or MEG at launch, and caches at first play.** TF ships static seeds on both channels
   (`Data/AUDIO/EN-US/RA{C,R}_SFX_EVA_*_EN-US.WAV`, seeded from the RA payloads): the nine lines plus
   structure-sold (`STRUSLD1`), which the DLL routes, so a fresh install
   caches TF's bytes. A deploy must never `--delete` them.
5. **A line is cacheable only after it has played.** `BCT` is fixed at the next match start.
6. **Never write on a needle alone.** The stale copies come from Wine's `CopyFile` and the patch's own file reads,
   which work through heap buffers; the patch zeroes its own buffers before freeing them. The crash this fixed:
   after a TS GDI match then a TD match, the TD write of `TF_MBX_TD_NODEPLY_R.WAV` at `0x378b9468` spanned the
   heap block at `+976`, and ClientG's heap tripped over it on the next skirmish load.

## Shipping notes

- The patch runs in release builds and degrades to the disk-mailbox voice (first-fire-correct,
  stale-on-switch) when the process, a needle or a whole payload is not found, or a write is
  refused. Its writes are memory writes into a live process, so the whole-payload check (finding
  6) is what keeps it from crashing ClientG. Diagnostic logging (`tf_cache_probe.log`) is
  `TF_DEV_BUILD`-only: `PATCH OK` = replaced, `PATCH FAIL` = left alone.
- `scripts/eva_mailbox_payload.py` builds one TD + RA payload pair and prints its needle lines.
- Needles/offsets are regenerated whenever a payload is re-padded (the re-encode/pad changes the
  bytes). The generator picks a high-entropy 20-byte slice from the real audio (never the leading
  silence) and records its file offset.
- Cross-process `WriteProcessMemory` in a shipped mod could in principle trip aggressive AV/anti-
  cheat, but it targets only positively-identified sample blobs in the sibling game process the
  DLL already reads. No issue observed.
