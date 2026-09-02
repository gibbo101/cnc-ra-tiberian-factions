# Per-faction radar crest — SOLVED (2026-09-02)

The in-game radar-slot crest (shown while the player has no radar building) now follows the
picked faction: **GDI → TD eagle, Nod → TD scorpion, Allied → RA chevron, Soviet → RA pentagon**. Backdrop follows too (TD plate for GDI/Nod, see below). Verified
in play across four skirmishes in ONE session (Nod, GDI, Allied, Soviet) with no relaunch; both
switch directions confirmed in the log. Ships in release builds; logging is `TF_DEV_BUILD`-only.
Code: `TF_Crest_*` in `redalert/dllinterface.cpp` (`TF_Crest_Tick` driven per frame from
`CNC_Advance_Instance`; `TF_Patch_ClientG_Crest` at match start only resets the scan window).

This reopens and closes the 2026-07-20 wall ("crest is side-keyed in `ClientG.exe`, not moddable"):
that finding was right on the DATA side and wrong on the RAM side, exactly like the EVA lines
(`eva-ram-patch-spike.md`).

## The mechanism (what actually works)

ClientG keeps **one small cached record per referenced atlas region** in ordinary writable heap:

```
float v0, u0, wn, hn;   // y/H, x/W, w/W, h/H of the region in MT_COMMANDBAR_COMMON.TGA (6871x6716)
```

The crest quad samples straight from this record every frame (the per-frame vertex buffers carry
the same UVs). ALLIES = `{1706/6716, 5698/6871, 794/6871, 713/6716}`. There is a persistent
master copy plus a per-match copy cloned from it (typically 2 records per slot, 4 total). Both
TD crests already ship inside the atlas as the never-referenced `UI_SIDEBAR_FACTIONLOGO_GDI`
(1,1875,718,706) and `_NOD` (3778,2221,660,660) regions. **Re-pointing the ALLIES record's 16
bytes at the GDI or NOD rect swaps the drawn crest instantly** — no pixel data, no new art.

The DLL (in InstanceServerG) does it cross-process, same infra as the EVA patch:
`CreateToolhelp32Snapshot` → `ClientG.exe` → `OpenProcess(VM_READ|VM_WRITE|VM_OPERATION)` →
`VirtualQueryEx` over `MEM_PRIVATE`/`PAGE_READWRITE` regions → 4-byte-aligned needle search for
any record holding a slot's stock rect or a TD rect → `WriteProcessMemory` of the wanted rect.
Records must be computed as **double divide then cast to float** to byte-match ClientG's copies.

## The three findings that shaped it (in the order they bit)

1. **Pixels are GPU-only after launch.** A 1.7 GB read of every readable ClientG mapping found the
   crest pixels in NO encoding (BGRA/RGBA/ARGB/ABGR/24-bit, even a 4-pixel run, and no TGA
   header) while the atlas *metadata* (region names, atlas name) was resident. The pixel-overwrite
   route from the original plan is dead. Corollary: the loose atlas is read **once per launch** —
   a marker painted into the crest region on disk was invisible across a new match in the same
   session and visible after exit-to-desktop + relaunch. A disk mailbox can only ever be
   per-launch.
2. **The record is created lazily, on the first radar draw, a few frames into the match.** A
   match-start-only patch (frame 0) found nothing on a fresh launch. Fix: `TF_Crest_Tick` runs a
   full scan every 6 frames for the first 450 frames of each match, remembers every record
   address it finds, and cheaply re-verifies the known addresses every frame.
3. **Nod draws the ALLIES slot too.** With only the SOVIET record re-pointed, a Nod player kept
   the ALLIES art. Which slot a faction draws is launcher-owned, so the DLL points **both** slots
   at the faction rect for GDI/Nod and both back to stock otherwise; whichever the launcher draws
   is right. (The 2026-07-20 "HOUSE_BAD → SOVIET region" claim was never testable: both regions
   held the same C&C logo.)

## The backdrop too (same day)

TD drew its crest over a scratched metallic plate (`UI_SIDEBAR_RADARBG`, 868x763); RA draws it
over a dark radar grid (`UI_RA_SIDEBAR_RADAR_UNDERBG_BLUE` for the ALLIES slot, `_UNDERBG` red
for SOVIET). Both under-screens have the same kind of cached record, so the DLL now carries
**four slots**: the two crests and the two under-screens. For GDI/Nod all four point at the TD
crest + TD plate; for RA sides all four are stock. Verified GDI → plate, Nod → plate, Allied →
blue grid restored, in one session. The launcher-drawn faction label under the crest goes
dark-on-grey over the plate (TD-authentic; not ours to recolour).

## Open / follow-ups

- **Aspect:** the slot is 794x713; GDI's region is 718x706 (~9% horizontal stretch, eagle fills
  its region edge to edge, so no crop is possible) and NOD's is 660x660 (scorpion has ~30 px of
  clear margin, so an aspect-correct window `y+33, h=593` is available if Luke's eye wants it).
  Luke saw both stretched and was happy; change is a 4-int edit in `TF_Crest_Slots`.
- **Allied and Soviet crests RESTORED (same day):** the shipped atlas had the C&C logo painted
  into both RA crest regions ("one logo for all"); the pristine 794x713 Allied chevron / Soviet
  pentagon were byte-copied back from `scripts/cameo_work/MT_COMMANDBAR_COMMON.TGA` (the base
  atlas) into `resources/.../MT_COMMANDBAR_COMMON.TGA` and the prefix copy (md5 `33780c7a…`),
  and `scripts/frontend_atlas_build.py` no longer repaints them (`apply_crest = False`).
  Verified in play: Allied → chevron, Soviet → pentagon. Also learned: **Soviet countries draw
  the SOVIET slot** (unpatched record), so the routing is GDI/Nod/Allied → ALLIES, Soviet → SOVIET.
  All four factions now show their own crest with the TD pair re-pointed and the RA pair stock.
- LAN clients keep the stock crest (no DLL there) — same limit as the EVA mailbox.
- Live-testing tool: with the game running headless, `/proc/<ClientG pid>/mem` is read/write
  from Bash (same uid), so a hypothesis costs one Python write + one screenshot, no DLL rebuild.
  That is how findings 1 and 3 were established in minutes.

## Standing rule (reaffirmed)

A wall proven dead on the data side is not proven dead on the RAM side. Before declaring a
launcher behaviour impossible: (1) grep CONFIG.MEG, (2) scan ClientG memory for the *structure*
that drives it (names, rects, UVs), not just the payload.
