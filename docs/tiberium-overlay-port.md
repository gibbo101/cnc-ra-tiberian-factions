# Tiberium as a harvestable overlay (coexisting with Ore) — feasibility + plan (2026-06-03)

**Status: feasibility research + plan. No code yet.** Goal: add TD-style
**Tiberium** as a harvestable resource in our RA mod, able to **coexist with Ore
on the same map**. Complements `classic-mode-palette-remap.md` (classic TD
rendering), `mix-file-format.md` (asset packing), and the heap-sizing gotcha in
`[[project-mod-type-heap-sizing]]`.

---

## TL;DR

- **RA's resource engine *is* Tiberium under the hood.** The code is littered with
  `IsTiberium` / `Reduce_Tiberium` / `LAND_TIBERIUM` / `Rule.IsTGrowth`. RA "Ore"
  (`OVERLAY_GOLD1-4`) and "Gems" (`OVERLAY_GEMS1-4`) are simply **two instances of
  harvestable Tiberium** — both flagged `IsTiberium=true` in `odata.cpp`.
- **Gems are the proof of concept.** Gems already are a *second* harvestable
  resource that coexists with Ore, is harvested by the same harvester and credited
  by the same refinery, is worth a different per-cell value, and **does not
  grow/spread**. "A map with Tiberium and Ore" ≈ "a map with Gems and Ore," which
  ships in vanilla today. **Coexistence: YES, low-risk.**
- **Adding Tiberium = define a new harvestable overlay modeled on Gems.** Static
  (placed-field) Tiberium is a contained job; TD-authentic growing/spreading
  Tiberium is a moderate add on top.

---

## Why this is feasible (the engine model)

Harvest + credit logic is **generic over the `IsTiberium` flag**, not hardcoded to
Ore:
- `CellClass::Reduce_Tiberium` (cell.cpp:1726) lowers a cell's `OverlayData`
  (the growth stage) — type-agnostic; the harvester calls it for whatever
  harvestable cell it's on.
- Overlays declare harvestability in their `OverlayTypeClass` ctor
  (`odata.cpp`): `LAND_TIBERIUM` + `IsTiberium=true`. Gold and Gems both set this;
  a new `OVERLAY_TIB*` set the same way is harvested and credited automatically.

The **only** Ore-hardcoded paths are growth/spread:
- `CellClass::Can_Tiberium_Grow` (cell.cpp:3114) and `Can_Tiberium_Spread`
  (cell.cpp:3153) both gate on `Overlay == OVERLAY_GOLD1..4` explicitly. That's
  *why* Gems are static. A new overlay is static-by-default too — fine for placed
  fields, and the exact hook to extend for TD spreading.

---

## Plan — three tiers

### Tier 1 — static harvestable Tiberium (modeled on Gems) — *small*
1. `defines.h`: add `OVERLAY_TIB1..OVERLAY_TIBn` before `OVERLAY_COUNT`
   (TD uses 12 growth stages; even 4 — Gold's count — works for static fields).
2. `odata.cpp`: define each `OverlayTypeClass` by copying the Gold block
   (odata.cpp:151) — `LAND_TIBERIUM`, **`IsTiberium=true`**, radar-visible. Set
   **"Theater specific art?" = false** for a single cross-theatre sprite (TD
   Tiberium looks the same everywhere; simpler than per-theatre art), or `true`
   if we want theatre-tinted variants.
3. `odata.cpp` `Init_Heap` (line 568): `new OverlayTypeClass(Tib1);` … register
   each, in enum order.
4. Heap sizing: bump the overlay heap to cover the new count
   (`[[project-mod-type-heap-sizing]]` — `Set_Heap` must match the enum count or
   `Alloc()` silently fails).

Result: harvester harvests it, refinery credits it, it shows on radar. No growth.

### Tier 2 — make it visible — *small/medium*
- **Classic mode:** add the TD Tiberium SHP (TI1-TI12 from TD assets), packed
  into TFASSETS and **palette-remapped** per `classic-mode-palette-remap.md`
  (the 176-191→80-95 path our other classic TD art uses).
- **HD mode:** map the overlay's INI name to the TD Tiberium textures in the
  tileset XML (TD-Assets has them) — the same name-mapping trick as our TD
  unit/building HD sprites.

### Tier 3 — TD-authentic growth/spread (optional) — *moderate*
- Extend `Can_Tiberium_Grow` / `Can_Tiberium_Spread` (cell.cpp:3114/3153) to
  include `OVERLAY_TIB*` alongside the Gold cases.
- Port TD's **blossom-tree** `TerrainType` (TD `TC1-TC5`) as the spore source so
  fields regrow/spread the way TD players expect. Without this, Tiberium behaves
  like Gems (finite, placed). Only worth it if "living" Tiberium is a goal.

---

## Coexistence with Ore — the concrete answer

Already how Gold + Gems work today:
- The **same harvester** grabs the nearest harvestable cell regardless of type;
  the **same refinery** credits it.
- Per-cell **value** is a dial (Gems are worth more than Gold) — Tiberium can be
  set equal to Ore (pure flavour) or richer/poorer as a balance lever.
- So a single `.mpr` can carry **Ore patches and Tiberium fields side by side**;
  place both in the editor like any overlay.

---

## Caveats / decisions to make

- **Universal harvest by default.** Any harvester harvests any `IsTiberium` cell.
  There is **no** "GDI/Nod harvest Tiberium, Allied/Soviet harvest Ore" split
  without custom faction-gating code (would touch the harvester target scan). By
  default it's just a second, visually-distinct resource everyone can use.
- **Value/identity:** decide whether Tiberium is economically identical to Ore
  (recommended for v1 of the feature) or differentiated.
- **Editor authoring:** the Mobius editor must know the overlay to let you paint
  it; otherwise place it via `.mpr` text or an editor config addition. Verify when
  the arc starts.
- **Heap-sizing gotcha** is the one real footgun — see Tier 1 step 4.

---

## Bottom line

Tiberium-as-harvestable, coexisting with Ore, is **genuinely achievable and
low-risk** — the engine is already a Tiberium engine and Gems de-risk the
multi-resource case. Tier 1+2 (placed, visible Tiberium) is a contained job;
Tier 3 (living Tiberium) is the only part that's real work, and it's optional.
Natural companion to `td-skirmish-map-import.md` — TD maps want Tiberium fields,
and both land in the same authoring pass.
