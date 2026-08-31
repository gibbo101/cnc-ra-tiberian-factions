# Per-faction radar crest — RAM-patch spike (reopened 2026-09-01)

**Goal:** the in-game radar-slot faction crest (shown when the player has no radar building) is
side-only — the launcher routes `HOUSE_GOOD`→the ALLIES crest region and `HOUSE_BAD`→SOVIET,
collapsing GDI/Nod onto the two RA side crests. Make it show a real GDI eagle / Nod scorpion per
faction.

## Why this is worth reopening

The 2026-07-20 spike (memory `reference-radar-crest-per-faction-wall`) proved two things:
1. **Data can't route it.** Painting the unused `UI_SIDEBAR_FACTIONLOGO_GDI`/`_NOD` atlas regions
   does nothing — the RA launcher never references them; region selection is `ClientG.exe` code.
2. It explicitly weighed the RAM angle and **declined it**: "Redirecting the crest would need
   cross-process WRITES into ClientG.exe … a heavier, fragile, crash-prone mechanism … Not
   pursued."

That second point is exactly the capability the **EVA RAM patch just proved reliable** (see
`eva-ram-patch-spike.md`): cross-process `WriteProcessMemory` into ClientG.exe works under Proton,
we can locate a loaded asset in ClientG memory by a byte needle, and a same-size overwrite at
match start changes what the launcher renders — without a crash. So the wall's own stated escape
route is now a proven tool. Reopen on that basis.

## The approach — overwrite the loaded crest PIXELS (direct analog of the EVA win)

The launcher loads the ALLIES/SOVIET crest image from the loose atlas
(`MT_COMMANDBAR_COMMON.TGA` / the `UI_SIDEBAR_FACTIONLOGO_*` regions,
`docs/ui-atlas-modding.md`). Instead of trying to re-route which region is drawn (ClientG code),
overwrite the PIXELS of the region that IS drawn: at match start, for a GDI/Nod player, find the
loaded ALLIES/SOVIET crest pixels in ClientG memory and write the faction crest over them — same
mechanism family as the EVA sample-blob overwrite (`TF_Patch_ClientG_Cache`).

## Stage 1 — READ-ONLY probe (do this first)

Reuse the EVA patch's scan (`CreateToolhelp32Snapshot` → `ClientG.exe` → `VirtualQueryEx` →
`ReadProcessMemory`). Needle = a distinctive run of bytes from the ALLIES-crest region of the
loose atlas, tried in each plausible in-memory form:
- **raw BGRA/RGBA** (uncompressed decoded pixels) — most likely if ClientG keeps a CPU copy;
- **the TGA/atlas file bytes** (if it caches the loaded file like it does audio);
- **DXT/BCn block bytes** (if stored compressed).

Generate the needle from the exact pixels we ship in that atlas region. Log hits + region
protect flags, exactly like the EVA stage-1 probe.

**The decisive question the probe answers:** does a CPU-readable copy of the crest pixels exist in
ClientG memory at all?
- **Found, in a writable region** → stage 2 (overwrite with the faction crest, same-size) is very
  likely to work, just like EVA.
- **Not found** → the crest almost certainly lives only in GPU/VRAM after upload (the real risk
  textures carry that audio samples do not). A CPU-memory patch can't reach GPU-resident pixels;
  the spike would then pivot to patching the upload path or accept the wall. Determining this is
  the whole value of stage 1 — cheap, read-only, no crash risk.

## Stage 2 — the overwrite (only if stage 1 finds writable CPU pixels)

At match start, for GDI/Nod players, write the faction crest pixels over the located ALLIES/SOVIET
crest blob (same-size — keep the faction crest art at the exact region dimensions). Handle the
redraw-cadence question: the crest is drawn every frame, so unlike a one-shot audio sample the
patch may need to persist or re-apply if ClientG re-reads the source. Watch for a re-upload that
reverts our write (the GPU-cache failure mode).

## Known-good building blocks to reuse

- Cross-process scan + write: `TF_Patch_ClientG_Cache` / `TF_WriteFile_Into_Process`,
  dllinterface.cpp.
- Atlas region names, byte-edit recipe, loose-override delivery: `docs/ui-atlas-modding.md`,
  `docs/front-end-texture-meg-spike.md`.
- The faction NAME text under the crest is ALREADY per-faction (launcher-aware) — only the image
  is side-only, so a per-faction crest completes an identity that is already half-right.

## Standing rule this spike embodies

A wall proven dead on the DATA side (2026-07-20) is not proven dead on the **RAM** side. The EVA
arc turned three "launcher-owned, can't touch it" walls into shipped features with cross-process
memory work; the radar crest is the next candidate by the same method.
