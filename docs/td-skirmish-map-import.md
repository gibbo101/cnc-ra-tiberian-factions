# Importing TD skirmish maps into the RA mod — feasibility + plan (2026-06-03)

> **PARTLY SHIPPED (v2.0.0).** The temperate/winter tiers landed — the 31-map TD
> pack ships via `<mod>/CustomMaps/` (DLL self-installs to `Local_Custom_Maps`; see
> [[project-td-skirmish-map-import-findings]]). The "no clean importer" framing below
> is OBE — a transcoder pipeline did the import. **Desert/interior-slot tier: the
> pipeline is PROVEN end-to-end in-game (2026-07-19** — `scm05ea` transcoded
> Theater=INTERIOR, 0 unmapped, rendered full HD desert in a live skirmish; see the
> proof banner in `theatre-desert-feasibility.md`). Remaining for the tier: batch-convert
> the desert-matrix maps + curate interior out of the MP pool + decide shipping shape
> (cacti/rocks still dropped — no interior terrain-object art). Body retained for the
> per-map theatre matrix.

**Status (original 2026-06-03):** feasibility research + agreed direction.
Goal: bring Tiberian Dawn's original skirmish/multiplayer maps into our RA-based
mod so GDI/Nod can fight on their home terrain. Complements
`theatre-desert-feasibility.md` (the theatre lock, the decisive evidence) and
`coop-missions-design.md` (the editor + scenario pipeline).

---

## TL;DR

- **TD map imports are possible.** A TD map becomes an RA-format map by
  **recreating its layout in the Mobius editor** — there is no clean one-click
  importer (different scenario format + different terrain template model).
- **The tileset (theatre) is the gating factor, per map:**
  - TD **temperate** maps → RA **temperate** — no engine work, recreation only.
  - TD **winter** maps → RA **snow** — no engine work, recreation only.
  - TD **desert** maps → need a desert theatre RA doesn't have.
- **DECISION (Luke, 2026-06-03): add the desert theatre by REPLACING the
  interior theatre slot.** Interior is the least-used RA theatre (indoor campaign
  missions; effectively unused in skirmish), so spending its slot on desert is an
  accepted trade. This is the "interior-slot hijack" from
  `theatre-desert-feasibility.md`, now the committed approach rather than one
  option among several.

---

## Why there's no auto-importer

- TD scenarios are a **different format** from RA `.mpr` (TD `.ini` + `.bin`
  terrain, plus the Remaster meta files). The Mobius editor treats **TD and RA as
  separate games** with separate tile/template sets — it won't transcode one to
  the other.
- The honest pipeline is **recreation**: open the TD map as reference, rebuild
  the terrain + resource fields + start waypoints as an RA map, drop in the
  (now-ported) TD units/structures, save as `.mpr`. Tedious but mechanical, and
  it's a per-map content task, not an engine task.
- Upside: our GDI/Nod rosters already exist, so the placed objects are
  faction-correct out of the box.

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

---

## Effort tiers

1. **TD temperate/winter skirmish maps** — *content only.* Recreate in the
   editor against existing RA theatres. No DLL build. Best starting point.
2. **The desert theatre conversion** — *one-time DLL + data.* Interior→desert per
   above; gated by the CONFIG.MEG re-skin test.
3. **TD desert skirmish maps** — *content,* unlocked once (2) lands.

Pairs naturally with `tiberium-overlay-port.md` (TD maps often want Tiberium
fields, not Ore) and `coop-missions-design.md` (same editor + `.mpr` pipeline,
and the same maps can later carry mission scripting).

---

## Open items to verify when this arc starts

- Whether the RA `.mpr` / `INSTANCES.XML` carries a per-map theatre/climate field
  the editor sets, or whether theatre is implied by tileset (see
  `theatre-desert-feasibility.md` — flagged as needing an empirical map-format
  test).
- Desert template ID parity between TD's set and what `IsoTileTypeClass` needs to
  expose for the editor + engine to agree on tile vocabulary.
