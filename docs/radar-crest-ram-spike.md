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
   match-start-only patch (frame 0) found nothing on a fresh launch. Fix: `TF_Crest_Tick`
   requests full scans at frames 0, 6, 12, 24, 48, 96, 192 and 384 of each match, remembers every
   record address found, and re-verifies the known addresses every fifth frame.
   **The scan must not run on the game thread:** each one reads the launcher's whole heap
   (hundreds of MB cross-process), and the first version, 75 scans on the game thread, stalled
   matches for up to a minute at the start. It now runs on a worker thread (`TF_Crest_Scan_Thread`,
   one at a time, from a private copy of the slot table); `TF_Open_ClientG` caches the pid.
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

## The whole TD sidebar — superseded the same evening by the TD scene swap

**GDI and Nod now load TD's own HUD scene** (`FACTIONS.XML` scene-list swap, see
`faction-select-identity.md`), so none of the RA-scene re-pointing below runs for them any more:
TD's scene draws `UI_SIDEBAR_*` directly. What the crest patch still does under the TD scene is one
thing: TD's scene chooses its logo by RA side, so for Nod (Allied side) the record holding the
`UI_SIDEBAR_FACTIONLOGO_GDI` rect is re-pointed at `_NOD` (slots 9 and 10). The skin table, the
under-screen/bezel/rail/plate/power-fill slots and `scripts/td_sidebar_extras_paint.py` are idle
for GDI/Nod and are kept only until the TD scene has more play time behind it; strip them then.
The record below stands as the method record.

### The RA-scene skin (how it was done before the scene swap)

Every RA sidebar region the launcher draws has a same-named TD region in the atlas (`UI_RA_SIDEBAR_*`
→ `UI_SIDEBAR_*`, `RA_UI_FRAME_TOOLTIP_SIDEBAR_*` → `UI_FRAME_TOOLTIP_SIDEBAR_*`), and the big
pieces match in size. `TF_SidebarSkin[]` (54 pairs, generated from the `.MTD`) extends the same
patch: for GDI/Nod every pair is re-pointed at its TD counterpart (build-bar plates, power bar,
top button, tab icons, tooltip frame, small buttons), for RA sides restored. Verified all four
factions in one session. Two exclusions: the RA radar **bezel** stays (TD's plate is opaque and
covered the crest when the bezel was re-pointed), and the square **sell/repair/map** buttons stay
RA at first (121x121 vs TD's 260x78; a squash) — solved the same day by sampling a centred
square (78x78) window of each TD button bar: icon on the grille with the top/bottom bevels, all
14 states, no repaint. Live inventory method: scan ClientG for the record of every candidate
region — only drawn regions have one.

**Restore trap + fix:** two slots that share a target (blue and red build bar → one TD plate;
ALLIES/SOVIET crest → one TD crest) were indistinguishable on the way back, so the first slot won
(Allied got the red build bar, Soviet got the chevron). Every written rect now carries a per-slot
sub-pixel nudge on u0 (`slot * 1e-6` UV ≈ 0.007 px), so each record restores to its own stock.

**Resize + position:** GDI's eagle is aspect-correct and sits clear of the launcher's "GDI"
label — scaled to 396 high, centred horizontally and top-aligned in a 495x444 window (the
slot's 794:713; the bottom ~11% stays transparent) painted into the unused DINO region; NOD
samples a 660x593 window of its own region. `scripts/crest_atlas_paint.py` paints everything the
patch depends on (pristine RA crests + the DINO eagle) into a shipped atlas.

## Tooling (the method, reusable)

- `scripts/clientg_region_probe.py` — the live lever. `list [REGEX]` shows which atlas regions
  the running ClientG holds records for (only drawn regions have one: the inventory step);
  `point RA_REGION TD_REGION|x,y,w,h` re-points every live record at another rect and shows on
  the next frame. Every finding in this doc was made with this loop before a line of DLL code.
- `scripts/sidebar_skin_table.py` — regenerates `TF_SidebarSkin[]` in `dllinterface.cpp` from
  the `.MTD` (pairing rules + the bezel/button exceptions live there). Run after any atlas
  metadata change, then rebuild.
- `scripts/crest_atlas_paint.py` — the atlas edits the patch depends on, reproducible.
- `TF_Crest_*` in `dllinterface.cpp` — the shipped patch: `TF_Crest_Slots` (what each slot should
  show per faction), `TF_Crest_Full_Scan` (heap walk with a first-word filter, remembers record
  addresses), `TF_Crest_Reverify` (per-frame cheap re-point of known addresses), `TF_Crest_Tick`
  (6-frame cadence for the first 450 frames of each match).

## Can the launcher HUD gain new buttons? (Luke, 2026-09-02)

No. This patch only changes which atlas pixels an EXISTING widget samples. The widget set — how
many buttons, where they sit, their hit-tests and what they do — is compiled `ClientG.exe` code
plus the `RA_TACTICAL_UI.BUI` scene graph, and the BUI can only reshape/hide/retexture existing
widgets under the same-size rule (`bui-front-end-modding.md`). A future TS sidebar therefore
means re-skinning and re-arranging RA's widgets, not adding to them.

## Open / follow-ups

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
