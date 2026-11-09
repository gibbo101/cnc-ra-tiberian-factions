# Per-faction radar crest: the RAM lever

**Status:** Reference; shipped. The per-faction radar crest and marker logos by RAM patch of ClientG's region
records.

The radar-slot crest (shown while the player has no radar building) follows the picked faction:
GDI the TD eagle, Nod the TD scorpion, TS GDI its own eagle, Allied the RA chevron, Soviet the RA
pentagon. GDI, Nod and TS GDI play on TD's HUD scene (`faction-select-identity.md`), which picks
its logo by RA side, so the DLL re-points ClientG's two cached TD-logo records at the faction's
rect; Allied and Soviet draw RA's stock crests. It reaches every player: on the host the sim's DLL
patches ClientG across processes, and each launcher's startup-load copy of the DLL patches it for
its own player (`launcher-vs-dll-ownership.md`, "Launcher-resident patches").

The method (the record, the scan, the timing, the traps and the fragility box) is on the field manual's
[Re-pointing launcher UI art in memory](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md);
the TD crests' own regions (`UI_SIDEBAR_FACTIONLOGO_GDI` and `_NOD`, which RA's HUD never draws) are on its
[Pick the right region](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#pick-the-right-region).
The crest is side-keyed in ClientG's data, a wall that held on the data side and fell on the RAM
side, as the EVA lines did (`td-audio-routing-recipe.md`, "EVA lines the launcher plays").

## The code

`TF_Crest_*` in `redalert/dllinterface.cpp`. Logging is `TF_DEV_BUILD`-only.

- `TF_Crest_Slots` builds the four slots (`TF_CREST_SLOTS`) for the local player: the TD GDI and NOD logo records
  (the radar crest) and the RA small logos (the waypoint and rally markers), each with its stock, GDI, Nod and TS GDI
  rect. Every written rect carries the per-slot `u0` nudge from the manual's
  [Traps](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#traps).
- `TF_Crest_Tick` runs every frame from `CNC_Advance_Instance`: it re-points known records every fifth frame
  (`TF_Crest_Reverify`) and requests full heap scans at widening gaps over the first 384 frames of a match (`_scan_at`, about 25 s at 15
  ticks a second).
- `TF_Crest_Scan_Thread` runs one scan at a time (`TF_Crest_Full_Scan`, a heap walk with a first-word filter that
  remembers record addresses), off the game thread, from a private copy of the slot table. `TF_Open_ClientG`
  caches the pid; `TF_Thread_Stacks` lists the stacks the scan skips.

TF found about two records for each of the two TD logo slots, four in all (the two under-screen slots weren't
counted), and the per-frame vertex buffers carry the same UVs as the record. TD's scene
draws the GDI-logo record for every Allied-side player, Nod included, so the DLL points both TD logo slots at the
faction's rect for GDI, Nod and TS GDI, and both back to stock otherwise. The pixel search that showed the atlas
never returns to RAM tried BGRA, RGBA, ARGB, ABGR and 24-bit, a 4-pixel run and a TGA header. Six stray writes from a
scan that didn't skip stacks were found in the stack of a ClientG thread that crashed; that crash was the EVA patch
(`td-audio-routing-recipe.md`).

## The rects

GDI and Nod point at the full stock TD rects, `UI_SIDEBAR_FACTIONLOGO_GDI` (718x706) and
`UI_SIDEBAR_FACTIONLOGO_NOD` (660x660). TS GDI's emblem is scaled to 380 high and top-aligned in a 434x400 window at
4220,2883 over `UI_OBSERVER_MAP_BG` (TD-mode observer art an RA-mode match never draws, because the atlas had no
free region), clear of the label the launcher draws across the foot of the crest. `scripts/crest_atlas_paint.py`
paints everything the patch depends on (the pristine RA crests and the TS GDI emblem) into a shipped atlas; the atlas
could grow instead (`ui-atlas-modding.md`, "Growing the atlas").

Allied and Soviet draw the pristine RA crests in the shipped atlas; `scripts/frontend_atlas_build.py` leaves those
regions alone (`apply_crest = False`). Soviet countries draw the SOVIET region.

## The waypoint and rally markers

The launcher draws a player's waypoint and rally markers from `RA_UI_ALLIED_LOGO_SMALL` (25x19) or
`RA_UI_SOVIET_LOGO_SMALL` (21x18), picked by RA side, and GDI, Nod and TS GDI all ride Allied
countries. Both small-logo records are two more crest slots: for a GDI, Nod or TS GDI player they
point at that faction's radar crest (the TD eagle, the scorpion, the TS coin), stretched to the
marker's 25x19, so the round coin draws about a fifth wider than tall. The atlas around each crest is
packed with other art, so no wider rect keeps the coin round. Allied and Soviet keep their stock
logos. The patch only changes the local player's own client, the only one that draws their markers.

## Retired: re-skinning RA's sidebar scene

GDI and Nod load TD's own HUD scene, which draws `UI_SIDEBAR_*` directly, so the RA-scene re-skin no longer ships.
The skin table, its slots, paint script and table generator are in git history (commit 2b7947fc) if a re-skin of
RA's scene is ever wanted. The manual's
[Re-skinning the whole sidebar](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#re-skinning-the-whole-sidebar)
is the method; what TF's version held:

- Every RA sidebar region the launcher draws has a same-named TD region (`UI_RA_SIDEBAR_*` → `UI_SIDEBAR_*`,
  `RA_UI_FRAME_TOOLTIP_SIDEBAR_*` → `UI_FRAME_TOOLTIP_SIDEBAR_*`), and the big pieces match in size.
  `TF_SidebarSkin[]` held 54 pairs generated from the `.MTD`, re-pointed for GDI and Nod and restored for RA sides,
  checked for all four factions.
- The radar backdrop: TD draws its crest over a scratched metallic plate (`UI_SIDEBAR_RADARBG`, 868x763), RA over
  a dark radar grid (`UI_RA_SIDEBAR_RADAR_UNDERBG_BLUE` for the ALLIES slot, `_UNDERBG` red for SOVIET). Both
  under-screens have cached records. Verified in one session: GDI and Nod got the plate, and Allied got its blue grid
  back. Over the plate the launcher-drawn faction label under the crest goes dark-on-grey, as in TD, and was left
  that way.
- Two pieces stayed RA's: the radar bezel (TD's plate is opaque and covered the crest when the bezel was
  re-pointed), and the square sell/repair/map buttons, 121x121 against TD's 260x78, drawn from a centred 78x78
  window of each TD button bar: icon on the grille with the top and bottom bevels, all 14 states, no repaint.
- Without the per-slot nudge, two slots sharing a target restored wrong: Allied got the red build bar, Soviet the
  chevron.

## Tooling

- `scripts/clientg_region_probe.py`: the live lever (the manual's
  [A quick test loop](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#a-quick-test-loop)).
  `list [REGEX]` shows which atlas regions the running ClientG holds records for (only drawn regions have one);
  `point RA_REGION TD_REGION|x,y,w,h` re-points every live record at another rect, shown on the next frame.
- `scripts/crest_atlas_paint.py`: restores the pristine RA crests and paints the TS GDI emblem into a shipped atlas.

## Can the launcher HUD gain new buttons?

Not by this patch, and not by data; whether the main menu's route (`pack-panel.md`) works on the in-match HUD is
open. See the manual's
[Traps](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#traps)
and [What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md).
Until that route is tried, a future TS sidebar means re-skinning and re-arranging RA's widgets, not adding to them.

## Standing rule

See the manual's
[Search in this order](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#search-in-this-order).
Scan ClientG for the *structure* that drives a behaviour (names, rects, UVs), not just its payload.
