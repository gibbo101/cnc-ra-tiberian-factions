# Harvester unreachable-ore recovery — design & decision (2026-06-17)

> ⚠️ **PLAN REVISED 2026-06-17 (later same day).** The "proper" zone-recompute fix below was
> **falsified by the code** before any of it was written — see **"Why the zone fix can't be just
> a Zone_Reset call"** immediately under the bug description. **NEW DECISION (Luke): HARDEN THE
> SYMPTOM-PATCH instead** (lowest risk, proven detector, no global zone-semantics change). The two
> recovery refinements were implemented + built clean this session — see **"What shipped this
> session."** The zone-recompute design is retained below as the rejected alternative + rationale.

## The bug
A harvester ordered/heading to an ore patch that has been **walled off by a BUILDING** (a turret,
or the AI fencing its own gems) gets stuck forever: it never reaches the ore, burns A* fallbacks,
and its economy is dead. Reproduced reliably (Luke: build a turret blocking the only approach to an
ore patch while a harvester is en route).

## Two root causes (confirmed this session — the durable findings)

1. **Building placement does NOT recompute movement zones.** `MapClass::Zone_Reset` (map.cpp:1801)
   is the full-map flood-fill that rebuilds `CellClass::Zones[MZONE_*]` (the connected-region map all
   reachability checks use). Its callers are: **walls** (overlay.cpp:179 place, cell.cpp:1938 +
   house.cpp:5017 destroy), **terrain/trees** (terrain.cpp:577), **bridges** (map.cpp:2227/2311/2374),
   and **scenario load** (scenario.cpp:725/860). **Ordinary buildings are NOT in that list.** So when
   you wall an ore patch with a turret, the zone map is never updated — those ore cells keep their old
   "connected" zone id. Every zone-based reachability check therefore reads STALE data and believes the
   patch is reachable: `Tiberium_Check`'s zone filter (unit.cpp:2519), `Is_In_Same_Zone`
   (techno.cpp:5781), `Find_Path_AStar`'s zone gate (findpath.cpp:533). **This is the core bug.**

2. **The legacy pathfinder always "succeeds."** When A* fails (it correctly refuses the blocked
   cell), `FootClass::Find_Path` falls back to the legacy crash-and-turn edge-follower, which returns
   *some* wandering path that heads toward the wall and never arrives. So `Basic_Path` rarely returns
   "no path", the drive no-path/ABANDON branch rarely fires, and **any fix hooked to a failure EVENT
   can't see the stuck state.** Only the *symptom* — "not getting closer to the ore" — is reliable.
   (We burned 3 attempts learning this: LOOKING-only detection, NavCom-goes-clear detection, and
   no-path-branch detection all missed for this reason.)

## ❌ Why the zone fix can't be "just a `Zone_Reset` call" (the falsifying finding, 2026-06-17)
The whole "make buildings call `Zone_Reset` → every zone check just works" plan rested on an
assumption that turned out to be **false**: that the zone flood-fill counts building cells as
impassable. **It does not — by deliberate design.**

- `Zone_Reset` → `Zone_Span` (map.cpp:1895) tests each cell with
  `Is_Clear_To_Move(SPEED_TRACK, ignoreinfantry=true, **ignorevehicles=true**, -1, check)`
  (map.cpp:1917).
- In `Is_Clear_To_Move` (cell.cpp:3091), `ignorevehicles` runs `composite &= 0x5F` — and the
  original devs commented it **"Drop the vehicle/building bit."** The **Building** occupy bit is
  `0x80` (cell.h:228, little-endian); `0x5F` clears it. A building footprint cell also keeps its
  normal land type, so `Ground[land].Cost` is non-zero → the cell reads **clear**.
- Net: **the zone flood walks straight through building footprints.** Even if buildings called
  `Zone_Reset` on every place/sell, a building-walled ore patch stays in the **same zone** — zones
  never disconnect it. (Walls work because they're *overlay*, checked separately at cell.cpp:3145
  via `overlay->IsWall`, not via the occupy bits.)
- **Why the original design does this:** zones are a *coarse* terrain+wall connectivity map. Buildings
  are meant to be dynamic obstacles that fine-grained A* routes around at the cell level, so they're
  intentionally not zone-dividers (else every structure would shatter the map into tiny zones needing
  a rebuild on every build/sell). The harvester bug is exactly this mismatch: **A* respects buildings,
  zones don't.**
- **The bib is NOT the reason** (Luke asked): a building's bib is a separate passable `SmudgeClass`
  apron on cells *outside* the `Occupy_List`; it sets no occupy bits. The footprint cells themselves
  are fully blocked (`Occupy_Down` sets `Flag.Occupy.Building`, cell.cpp:650). Buildings are ignored
  in zones because of the `0x5F` mask, full stop.

**Consequence:** making the zone fix actually work would *also* require making the flood honor the
Building bit (a `Zone_Span`-only variant of `Is_Clear_To_Move` that keeps `0x80`). That changes the
global meaning of `Zones[]` and touches **every** consumer — AI target selection, the A* zone gate,
`Is_In_Same_Zone`, base placement — i.e. an MP-determinism-sensitive, regression-prone change needing
a full playtest cycle. **Too big for the payoff vs. the proven symptom-patch.**

## ✅ REVISED DECISION (Luke, 2026-06-17): harden the symptom-patch (NOT the zone fix)
Keep the pathfinder-agnostic **no-progress detector** (already proven), and add the two recovery
refinements that were previously listed as "still wanted." No zone semantics touched; blast radius =
harvester code only; ships this session. The rejected zone design is preserved below for the record.

### What shipped this session (built clean, `TF_DEV_BUILD`-gated logs)
1. **Flood-fill blacklist the WHOLE contiguous ore field, not a radius-3 box.** `Blacklist_Harvest_Cell`
   now 8-connectivity flood-fills `LAND_TIBERIUM` from the failed cell (bounded by `HARV_FLOOD_CAP=256`)
   and stores the field's **bounding box** per blacklist slot (`HarvBadMin`/`HarvBadMax`, replacing the
   single `HarvBadCell` + ±3 box). One detection now covers the whole walled field, so a big patch can't
   let the harvester give up on one cell and re-pick another cell of the same dead field (the AI
   `HARV(1,41)` spin). `Is_Harvest_Blacklisted` = point-in-bbox (+1-cell margin).
2. **Retreat to a refinery instead of waiting at the wall.** The `HARV-WAIT` branch in `Mission_Harvest`
   (LOOKING) now `Find_Best_Refinery()` → `Nearby_Location(refinery)` (a clear cell in the refinery's
   zone = known-reachable) and `Assign_Destination` there if we're >4 cells away; on arrival LOOKING
   re-scans from near base. If already near the refinery (or none exists) it just waits + re-scans in
   place. Self-recovers for human + AI (stays in MISSION_HARVEST, not GUARD).

### ⬇️ REJECTED ALTERNATIVE (retained for rationale): fix it at the source — zones must reflect buildings
Make building **place and sell/destroy** trigger a zone recompute (the same way walls already do), so
the `Zones[]` map is correct. Then **every existing zone-based check just works**: `Goto_Tiberium`
skips the walled patch, the harvester naturally redirects to reachable ore or idles correctly, and we
delete the symptom-patch entirely. This is the clean root-cause fix.

### What to implement (3 steps — refined with Luke 2026-06-17)
1. **Buildings call `Zone_Reset` on place + sell/destroy.** Likely homes: `BuildingClass::Unlimbo` /
   `Mark(MARK_DOWN)` (place) and `BuildingClass::Limbo` / `Mark(MARK_UP)` / destruction (remove) — where
   buildings stamp/clear occupation bits — mirroring the wall pattern (`wall.IsCrushable ?
   Zone_Reset(MZONEF_NORMAL) : Zone_Reset(MZONEF_CRUSHER|MZONEF_NORMAL)`). Add the dirty-flag (recompute
   once per logic frame) to kill any multi-building-same-tick spike. Confirm `Zone_Span`/`Is_Clear_To_Move`
   (map.cpp:1895, uses `Is_Clear_To_Move(SPEED_TRACK,true,true,-1,check)`) counts building cells as
   impassable so a recompute actually disconnects a fully-walled patch.

2. **⭐ KEY INSIGHT (Luke): with correct zones, "drop the dead patch + rescan another field" is mostly
   FREE.** `Goto_Tiberium`/`Tiberium_Check` ALREADY zone-filter candidate ore (unit.cpp:2519 — only
   counts ore in the harvester's own zone). The filter only fails today because the zone data is stale.
   Once buildings update zones, a walled patch drops into a different zone → `Goto_Tiberium` stops
   offering it → the harvester auto-picks the next reachable field. No wait-function surgery, no
   blacklist needed. Truly-cut-off (no ore in zone) → the existing `GOINGTOIDLE` path = correct.

3. **The one gap step 2 leaves = the MID-TRANSIT case.** If a wall goes up *while the harvester is
   already en route* (NavCom locked on the now-walled cell, patient-retry keeping it), it won't re-scan
   until it next clears. Close it with ONE cheap check in the harvester: **if the current ore NavCom is
   no longer in our zone (`Is_In_Same_Zone(As_Cell(NavCom))` — now MEANINGFUL because zones are
   accurate), drop it (`Assign_Destination(TARGET_NONE)`) and let `Mission_Harvest` re-scan.** This is
   Luke's "drop the zone it wants and rescan for another field", done reliably.

Then **delete most of the uncommitted symptom-patch** (no-progress detector / blacklist / `HARV-WAIT`):
it exists only because zones lied. Keep at most a tiny safety net for NON-building unreachable cases
(a same-zone cell permanently blocked by a parked unit), or drop it entirely — decide once steps 1-3
are in and tested. This is cleaner than tonight's code AND gives the redirect behaviour (vs sit-at-wall).

### The catch to evaluate FIRST (why this wasn't just done)
- **Perf: LOW — measured, not a blocker.** `Zone_Reset` (map.cpp:1801) is O(map cells): one clear pass
  over `MAP_CELL_TOTAL` (128×128 = **16,384**) + a flood-fill pass visiting each cell once. A building
  event triggers `NORMAL|CRUSHER` ≈ 2 zone passes ≈ **~50K cell-ops per call**, i.e. **sub-millisecond**
  on modern hardware. Frequency saves us: building place/sell are *events*, not per-frame (a few/sec at
  most vs 30–60 fps). **Walls already call `Zone_Reset` per segment** (overlay.cpp:179) — dragging a wall
  line fires many in a row and has shipped fine since 1996; buildings are *rarer* than wall segments, so
  this adds strictly LESS load than already exists. Only real risk = a multi-building-same-tick spike
  (base wiped → 10+ recomputes = a few-ms blip). **Mitigation = one dirty-flag:** mark zones dirty on a
  building change, recompute once per logic frame max → caps it at one `Zone_Reset`/frame regardless.
  Bottom line: not a reason to avoid the proper fix; add the dirty-flag and even the spike is gone.
- **Lockstep/MP determinism:** `Zone_Reset` writes shared `Map` cell state deterministically (no RNG),
  so it's sync-safe *as long as it's called at the same point in the sim on all clients* — keep it in
  the deterministic logic path, not in any render/UI path.
- **Save/load:** zones are recomputed on load already (scenario.cpp); transient, no format change.

## Two recovery refinements — ✅ DONE this session (2026-06-17)
Both implemented + built clean (details under "What shipped this session" above):
1. ✅ **Blacklist the whole contiguous ore field** (flood-fill bbox), not a radius-3 box. Fixes the AI
   `HARV(1,41)` re-pick-same-field spin.
2. ✅ **Pull back toward the refinery + re-scan** instead of waiting in place at the wall.

## Tree state — ✅ COMMITTED + SHIPPED in v2.4.0 (commits `554835d` + `a705ef6`)
**CORRECTION 2026-06-17:** this section previously said UNCOMMITTED — that was stale. The
no-progress detector + both hardening refinements were committed (`554835d`) along with the
ArchiveTarget zone-guard (`a705ef6`) and shipped in **v2.4.0**. Working tree is clean. The code
lives in `redalert/unit.cpp`, `redalert/unit.h`, `redalert/drive.cpp`:
- `UnitClass::AI` (unit.cpp ~448): every tick, while a harvester pursues an ore NavCom, track the best
  (closest) distance achieved; if it hasn't improved for `HARV_STALL_FRAMES` (5s), `Blacklist_Harvest_Cell`
  + drop the target. Pathfinder-agnostic. **Proven working** in the log (`HARV-BLACKLIST` fired for the
  walled harvester + 3 AI ones; spin stopped).
- Blacklist storage + `Is_Harvest_Blacklisted`/`Has_Active_Harvest_Blacklist`/`Blacklist_Harvest_Cell`
  (unit.cpp, members in unit.h: `HarvTargetCell`, `HarvBestDist`, `HarvStallFrame`, **`HarvBadMin[4]` +
  `HarvBadMax[4]`** (field bbox, replaced the old single `HarvBadCell[4]`), `HarvBadExpiry[4]`).
  `Goto_Tiberium` skips blacklisted cells. `Mission_Harvest` LOOKING else-branch has the
  retreat-to-refinery-vs-idle logic + `HARV-WAIT` log. `Player_Assign_Mission` resets tracking on fresh orders.
- **This session's two refinements** (see "What shipped this session"): bbox flood-fill blacklist
  (`HARV_FLOOD_CAP=256`, `HARV_BLACKLIST_MARGIN=1`) + retreat to `Find_Best_Refinery()`/`Nearby_Location`.
- Also UNCOMMITTED: the `mission=`/`status=` additions to the drive.cpp CHOKE log (keep — useful).
  (The ArchiveTarget zone-guard is already COMMITTED, `a705ef6`.)
- **`HARV-BLACKLIST`/`HARV-WAIT` logs are `TF_DEV_BUILD`-gated** → compiled out of release.

**Status:** the no-progress detector is a cheap, robust **safety net** for *any* unreachable-target case
(buildings *and* e.g. a same-zone cell blocked by a permanent parked unit). This is now THE approach
(the zone fix was rejected — see above). **Playtested + shipped in v2.4.0.** The broader harvester
workstream (claiming, dock contention, reachability edge cases, economy-balance docking) continues —
see `docs/harvester-docking-rework-plan.md` (the economy-balance docking chunk, planned 2026-06-17).

## Out of scope tonight (already committed + confirmed, NOT in the harvester segment)
Tiberium aversion `72b3a17`, Smarter SAMs + Harvester Self-Repair `14bcca9`, Recon Bike `bdb7533`,
ArchiveTarget walled-field zone-guard `a705ef6`. A release of this batch is **deferred** (Luke,
2026-06-17) — release can wait; harvester segment comes first.

## Diagnostic instrument
`tf_astar.log` (TF_DEV_BUILD): `HARV-BLACKLIST` / `HARV-WAIT` (harvester recovery), `CHOKE: ... mission=N
status=M` (drive no-path branch, now with mission/status), `A* FALLBACK` tally. An idle harvester that
has stopped pathing emits nothing — the no-progress detector in `UnitClass::AI` is the instrument that
sees it.
