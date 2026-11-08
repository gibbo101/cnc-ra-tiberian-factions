# Per-faction radar crest: the RAM lever

**Status:** Reference; shipped. The per-faction radar crest by RAM patch of ClientG's region
records.

The radar-slot crest (shown while the player has no radar building) follows the picked faction:
GDI the TD eagle, Nod the TD scorpion, TS GDI its own eagle, Allied the RA chevron, Soviet the RA
pentagon. GDI, Nod and TS GDI play on TD's HUD scene (`faction-select-identity.md`), which picks
its logo by RA side, so the DLL re-points ClientG's two cached TD-logo records at the faction's
rect; Allied and Soviet draw RA's stock crests. It reaches every player: on the host the sim's DLL
patches ClientG across processes, and each launcher's startup-load copy of the DLL patches it for
its own player (`launcher-vs-dll-ownership.md`, "Launcher-resident patches").

Code: `TF_Crest_*` in `redalert/dllinterface.cpp`. `TF_Crest_Tick` runs every frame from
`CNC_Advance_Instance`: it re-points known records every fifth frame and requests full heap scans
on a worker thread (`TF_Crest_Scan_Thread`) at widening gaps over the first ~15 s of a match.
Logging is `TF_DEV_BUILD`-only.

The crest is side-keyed in ClientG's data, a wall that held on the data side and fell on the RAM
side, as the EVA lines did (`td-audio-routing-recipe.md`, "EVA lines the launcher plays").

## The mechanism

ClientG's cached region record (`float v0, u0, wn, hn`), its master and per-match copies, and the cross-process
scan and write that re-point it are on the field manual's
[Re-pointing launcher UI art in memory](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#the-record), The record and The method; the
TD crests' own regions (`UI_SIDEBAR_FACTIONLOGO_GDI` and `_NOD`, which RA's HUD never draws) are on its
[The UI atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#pick-the-right-region), Pick the right region. In TF, re-pointing a crest record's 16 bytes
at the GDI or Nod rect swaps the drawn crest on the next frame. TF finds about two records per slot, four in all,
and the per-frame vertex buffers carry the same UVs as the record. The sim's DLL makes the writes across processes,
as the EVA patch does, and each launcher's own copy of the DLL runs the same scan for its own player.

**The scan skips every thread stack** (`TF_Thread_Stacks`), as the field manual's
[Re-pointing launcher UI art in memory](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#the-method) describes (The method, step 2, and the fragility box).
Six stray writes from an earlier scan were found in the stack of a ClientG thread that crashed (the crash itself
was the EVA patch, `td-audio-routing-recipe.md`, "EVA lines the launcher plays", finding 6).

## The three findings that shaped it

See the field manual's [Re-pointing launcher UI art in memory](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#what-decides-the-timing), What decides the timing, Traps and
the fragility box. The pixel search tried BGRA, RGBA, ARGB, ABGR and 24-bit, a 4-pixel run and a TGA header. In TF,
`TF_Crest_Tick` requests the full scans, remembers every record address found and re-verifies them every fifth
frame; `TF_Crest_Scan_Thread` runs one scan at a time from a private copy of the slot table; `TF_Open_ClientG`
caches the pid. Nod draws the ALLIES slot too, so the DLL points both slots at the faction rect for GDI/Nod and
both back to stock otherwise.

The earlier claim that `HOUSE_BAD` draws the SOVIET region was never testable: both regions held the same C&C logo.

## The waypoint and rally markers

The launcher draws a player's waypoint and rally markers from `RA_UI_ALLIED_LOGO_SMALL` (25x19) or
`RA_UI_SOVIET_LOGO_SMALL` (21x18), picked by RA side, and GDI, Nod and TS GDI all ride Allied
countries. Both small-logo records are two more crest slots: for a GDI, Nod or TS GDI player they
point at that faction's radar crest (the TD eagle, the scorpion, the TS coin), stretched to the
marker's 25x19, so the round coin draws about a fifth wider than tall. The atlas around each crest is
packed with other art, so no wider rect keeps the coin round. Allied and Soviet keep their stock
logos. The patch only changes the local player's own client, the only one that draws their markers.

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
`UI_SIDEBAR_FACTIONLOGO_GDI` rect is re-pointed at `_NOD` (the patch's two remaining slots).
The skin table, the under-screen/bezel/rail/plate/power-fill slots, their paint script and the
table generator were removed; recover them from git history
(commit 2b7947fc) if a re-skin of RA's scene is ever wanted. The record below is the method.

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

**Restore trap:** two slots that share a target restored to the same stock rect (Allied got the red build bar,
Soviet got the chevron). Every written rect carries the per-slot `u0` nudge from the field manual's
[Re-pointing launcher UI art in memory](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#traps), Traps.

**Resize + position:** GDI and NOD point at the full stock TD rects, `UI_SIDEBAR_FACTIONLOGO_GDI`
(718x706) and `UI_SIDEBAR_FACTIONLOGO_NOD` (660x660). TS GDI's emblem is scaled to 380 high and
top-aligned in a 434x400 window over `UI_OBSERVER_MAP_BG`, clear of the label the launcher draws
across the foot of the crest. `scripts/crest_atlas_paint.py` paints everything the patch depends
on (pristine RA crests + the TS GDI emblem) into a shipped atlas.

## Tooling (the method, reusable)

- `scripts/clientg_region_probe.py` — the live lever. `list [REGEX]` shows which atlas regions
  the running ClientG holds records for (only drawn regions have one: the inventory step);
  `point RA_REGION TD_REGION|x,y,w,h` re-points every live record at another rect and shows on
  the next frame. Every finding in this doc was made with this loop before a line of DLL code.
- `scripts/crest_atlas_paint.py` — restores the pristine RA crests into a shipped atlas.
- `TF_Crest_*` in `dllinterface.cpp` — the shipped patch: `TF_Crest_Slots` (what each slot should
  show per faction), `TF_Crest_Full_Scan` (heap walk with a first-word filter, remembers record
  addresses), `TF_Crest_Reverify` (cheap re-point of known addresses), `TF_Crest_Tick` (the per-frame
  driver) and `TF_Crest_Scan_Thread` (scans off the game thread).

## Can the launcher HUD gain new buttons?

Not by this patch, and not by data; whether the main menu's route (`pack-panel.md`) works on the in-match HUD is
open. See the field manual's [Re-pointing launcher UI art in memory](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#traps), Traps, and
[What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md).
Until that route is tried, a future TS sidebar means re-skinning and re-arranging RA's widgets, not adding to them.

## Open / follow-ups

- Allied and Soviet draw the pristine RA crests in the shipped atlas; `scripts/frontend_atlas_build.py`
  leaves those regions alone (`apply_crest = False`). Soviet countries draw the SOVIET slot.
- TS GDI's eagle is painted over `UI_OBSERVER_MAP_BG` (TD-mode observer art an RA-mode match
  never draws), because the atlas had no free region (`scripts/crest_atlas_paint.py`). The atlas
  can grow instead (`ui-atlas-modding.md`, "Growing the atlas").
- Live-testing tool: the field manual's [Re-pointing launcher UI art in memory](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#a-quick-test-loop), A quick test loop.

## Standing rule

See the field manual's [What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#search-in-this-order), Search in this order. Scan ClientG for the
*structure* that drives a behaviour (names, rects, UVs), not just its payload.
