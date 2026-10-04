# TD skirmish maps in the RA mod

**Status:** Parked. The 31 converted TD maps and the TD terrain art (temperate, winter, desert) are
out of the mod from 5.0.0, in `parked/td-maps/` (`TF_TD_MAPS` 0 in `redalert/defines.h`): they
raised video-memory use for everyone, and some were broken. They are planned as their own Workshop
item; the folder's README says how to bring them back.

`scripts/td_map_to_ra.py` converts TD maps to RA format (temperate, winter and desert), and the DLL
installs a mod's `CustomMaps/` triplets into `Local_Custom_Maps/` itself when `TF_TD_MAPS` is on.
Desert maps play on the interior theatre slot (`theatre-desert-feasibility.md`); TD's cacti and
rocks are dropped, since the interior slot has no terrain-object art. This doc keeps the per-map
theatre matrix.

---

## The per-map theatre matrix

| TD theatre | RA target | Engine work | Per-map work |
|---|---|---|---|
| Temperate | `THEATER_TEMPERATE` | none | recreate layout |
| Winter | `THEATER_SNOW` | none | recreate layout |
| Desert | **interior slot → desert** | **one-time DLL + data** | recreate layout |

So **temperate/winter TD maps are the low-hanging fruit** — start there; they
need zero engine changes. Desert maps wait behind the theatre conversion.

---

## What "replace interior with desert" entails

The theatre seam (from `theatre-desert-feasibility.md`): the launcher renders HD
terrain from a tileset it picks by a **hardcoded name** per (game, theatre) —
RA's three are `RA_Terrain_Temperate/Snow/Interior`, baked into `ClientG.exe`.
We can't *add* a 4th name, but we **can change what the `Interior` slot
contains** and how our DLL models it. Hence: keep the slot, swap its meaning.

**DLL side (our code — fully ours to change):**
- `defines.h` `TheaterType` — repurpose `THEATER_INTERIOR` as desert (swap its
  `TheaterDataType{Name,Root,Suffix}` in `const.cpp` `Theaters[]` to the desert
  root/suffix). `THEATER_COUNT` stays 3.
- `IsoTileTypeClass` — provide the desert **template model** (which template IDs
  / sizes exist) so the engine knows the desert tile vocabulary.
- Classic terrain rendering draws from the DLL, so classic-mode desert comes
  along for free once the templates exist.

**Data side (CONFIG.MEG master key — mod-shippable):**
- The launcher renders the interior slot from the **`RA_Terrain_Interior`**
  tileset by name. Swap that tileset's **content** (textures/template defs) to
  desert tiles via the mod's own `Data/CONFIG.MEG` (`config-meg-mod-delivery.md`).
  Same lever that reskins any front-end/tileset content.
- TD desert tiles are available as source art (TD assets); they map into the
  tileset like our TD unit/building HD sprites.

**Go/no-go gate (cheap, do this first):** reskin a handful of
`RA_Terrain_Interior` tiles to desert in a test `CONFIG.MEG` and confirm the HD
launcher renders them on an interior map. If the slot re-skins cleanly, the full
conversion is "just" content + the DLL template model.

**Cost of the trade:** any RA map authored for the *interior* theatre would now
render with desert tiles. In a GDI/Nod-focused skirmish/campaign mod that's a
non-issue — interior is an indoor-campaign theatre, not a skirmish one.
