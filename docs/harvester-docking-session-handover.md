# Harvester docking rework — session handover (2026-06-17)

Resume point for the harvester economy workstream. Canonical design = `harvester-docking-rework-plan.md`
(read it first; it has the governing rule + all four refinery pairings). This file is the live status +
exact next steps.

## Release gating (unchanged)
No more releases until the WHOLE harvester workstream is done → it all ships as **v3.0**
(`version_high=3`). Local stays on the 2.4.x dev bump. No interim Workshop pushes.

## Status board
| Item | State |
|---|---|
| **B2** RA harvester visible dust-loop unload | ✅ DONE + validated, **committed `686efa4`** |
| **B3** capturing an ore refinery grabs the unloading harvester | ✅ DONE + validated, **committed `0c5a040`** |
| **B4** RA harvester docks at a TD refinery (RA harv → TD ref) | ✅ DONE + validated ("perfect"), **committed `d923511`** |
| TF_DEV test-buildability (any house builds both refineries) | ✅ committed in `d923511` (TF_DEV-only, compiled out of release) |
| **Reverse case** TD harvester → RA refinery | 🟡 IMPLEMENTED + built + deployed (local prefix) — **UNCOMMITTED, awaiting Luke's in-game verdict** |
| Halve-dock-time dial | ⬜ deferred to the very end (re-eval after all harvester work) |

## START HERE next session — VERIFY the reverse case (TD harv → RA ref), then commit
The reverse case (TD harvester → RA refinery) is **implemented, built, and deployed to the local
prefix — UNCOMMITTED**. Next session: in-game verify, then commit (or tune). Use the committed
TF_DEV test-buildability to build BOTH refineries in one skirmish (fresh skirmish needed — build
options are set at scenario start), get a TD harvester to dock at an RA refinery, and watch the dock.

### What to check in-game
1. TD harvester drives to the RA refinery, **pulls up to the DIR_S dock cell and stays visible**
   (never disappears — no Limbo). It faces **DIR_N** (toward the refinery).
2. A small **dust puff** (`ANIM_SMOKE_PUFF`) pops at the intake each bail; credits tick up.
3. Total dock time ≈ a full TD load (the `TD_DOCK_OFFLOAD_DELAY = 21` ticks/bail dial in
   `Mission_Unload` `case UNIT_TDHARV`). Then it drives off and resumes harvesting.
4. Engineer-capture the RA refinery mid-unload → the docked TD harvester should change owner
   (B3 path: `IsDumping` + radio-tethered, `building.cpp:4284`).
5. Multi-harvester queue at one RA refinery doesn't jam.

### Tuning dials if the look/feel is off
- **Facing:** `RADIO_BACKUP_NOW` UNIT_TDHARV `STRUCT_REFINERY` branch (`unit.cpp` ~line 919) turns
  `DIR_N`. Change to `DIR_S` for a reversed-in / rear-to-intake look (Luke's "backs in" framing).
  *(Decision made this session: implemented the visually-safe pull-up — a visible, non-Limbo'd
  harvester driven INTO the RA refinery footprint would overlap the building sprite, which is exactly
  the "if back-in looks off" case Luke flagged. Pull-up = his blessed "option 1" fallback.)*
- **Dock time:** `TD_DOCK_OFFLOAD_DELAY` (ticks/bail) in `Mission_Unload`.
- **Dust anim:** swap `ANIM_SMOKE_PUFF` for another existing AnimType; spawn coord is
  `Coord_Add(Coord, XYP_Coord(0, -12))` (just north of the harvester).
- If the B4 dock *position* at the TD ramp ever needs nudging → tweak the DIR_SW pad cell (one-line
  offset in the STRUCT_TDPROC branch of the `RADIO_DOCKING` dock-cell calc, `building.cpp` ~line 439).

### Files touched this session (reverse case, all uncommitted)
- `unit.cpp Find_Best_Refinery` — both harvesters now consider both refinery types.
- `building.cpp RADIO_CAN_LOAD` — both refineries accept both harvesters.
- `building.cpp RADIO_IM_IN STRUCT_REFINERY` — comment only (TD harv lands in MISSION_UNLOAD too).
- `unit.cpp RADIO_BACKUP_NOW` — UNIT_TDHARV at a STRUCT_REFINERY uses the RA-style pull-up dock
  (DIR_N + RADIO_IM_IN), NOT the TD drive-in/attach (which stays for STRUCT_TDPROC).
- `unit.cpp Mission_Unload` — new `case UNIT_TDHARV`: timer offload (1 bail / `TD_DOCK_OFFLOAD_DELAY`
  ticks) + `ANIM_SMOKE_PUFF` per bail; `IsDumping` set (capture + park), `RADIO_UNLOADED` at the end.
- `unit.cpp AI()` safety net — clears `IsDumping` for a force-ordered UNIT_TDHARV (the dust-loop
  wrap stays HARV-only).

### What B4 changed (the cross-dock, RA harv → TD ref)
1. `unit.cpp Find_Best_Refinery` — RA harvester (`!is_td_harv`) now accepts `STRUCT_REFINERY` **or**
   `STRUCT_TDPROC`; TD harvester stays TDPROC-only.
2. `building.cpp RADIO_CAN_LOAD` — `STRUCT_TDPROC` now accepts `UNIT_TDHARV` **or** `UNIT_HARVESTER`.
3. `building.cpp RADIO_IM_IN` `STRUCT_TDPROC` — if the docker is `UNIT_HARVESTER`, route it to the RA
   path (`Assign_Mission(MISSION_UNLOAD)` + `RADIO_ROGER`, **no** Limbo/attach, **do NOT** fire the TD
   building animation — it has a TD harvester drawn into it); TD harvester keeps the attach path.
4. **Test-buildability (TF_DEV, test only):** `techno.cpp TechnoTypeClass::Get_Ownable` returns
   `0x7FFFFFFF` for `STRUCT_REFINERY`/`STRUCT_TDPROC` so both refineries are ownable/buildable by any
   house. This is THE lever — `Who_Can_Build_Me` gates the sidebar on `(1<<ActLike) & Get_Ownable()`
   (a direct ownership check, NOT `Can_Build`), so widening `Get_Ownable` is what actually works.
   **Both TF_DEV hacks are needed** (not redundant): `Get_Ownable` passes the ownership gate;
   `house.cpp Can_Build` TF_DEV `return true` for refineries bypasses the **prerequisite/tech-level**
   check (e.g. a GDI player lacking the Allied power plant prereq). Without the Can_Build bypass the
   cross-refinery shows but can't actually be built.
   ⚠️ Build options are set at scenario start — need a FRESH skirmish to see both refineries.
The RA harvester pulls up to the TD refinery's DIR_SW ramp and runs its normal dust-loop. Decision:
**keep this "pull up + dump" approach** (Luke) — backing in + rearward dump was rejected (needs new art).

## Next: reverse case — TD harvester → RA refinery (design DECIDED, not built)
TD harvester has no dump frames + RA refinery has no building anim, so neither carries a visual.
**Decided approach (Luke):** TD harvester **backs in but does NOT disappear** (stays visible, no Limbo)
and a **small dust AnimType plays at the dock** during a timer-driven offload — "imagine a pipe hooked
up to siphon it." **Fallback if back-in looks off:** harvester just **pulls up** to the RA south dock
(not backing in) + the same dust anim (this was "option 1"). To build:
- Relax the gates the *other* direction: `Find_Best_Refinery` (let TD harv consider `STRUCT_REFINERY`),
  `RADIO_CAN_LOAD` (`STRUCT_REFINERY` accept `UNIT_TDHARV`), `RADIO_IM_IN` `STRUCT_REFINERY` (TD harv →
  a timer-offload path, NOT the RA dust-loop since the TD sprite has no dump frames).
- Pick an **existing** dust/smoke `AnimType` to spawn at the dock (no new art — grep the AnimType enum;
  candidates like a smoke puff). Spawn it on a cadence during the offload; offload via a tick timer.
- TD harvester stays radio-tethered through the unload (same B3 pattern) so capture still works.

## Remaining harvester backlog (after the docking thread)
From `known-issues.md` + the two screenshots Luke flagged this session:
- **Field selection by travel distance** (his SS #1) — `Goto_Tiberium` ring-searches crow-flies, so a
  harvester picks an ore field that's near in a straight line but needs the long way around water/cliff.
- **Threat-aware field selection** (#2) — don't route through enemy territory for ore.
- **Harvesters blocked by infantry** (his SS #5) — two harvesters wedged by minigunners at the base.
- **Universal idle/stuck rescan** (#6), **target claiming / fleet spread**, **dock contention / queue**.

## Key technical learnings (carry forward — these bit us this session)
- **Mission funcs are NOT called every frame** (`Mission_Unload` returns `Normal_Delay`+jitter), but
  `StageClass::Graphic_Logic` advances the stage *every* frame. Any per-frame stage logic (the dust
  loop wrap + per-bail offload) MUST live in `UnitClass::AI`, or the stage overshoots (bucket bobbing).
- **A docked, unloading RA harvester had NO link to its refinery** — not cargo, radio contact dropped
  at unload start, `TiberiumUnloadRefinery` cleared every frame by the booking-cleanup (`unit.cpp`
  ~543). B3's proper fix = keep it radio-tethered through the unload (defer `RADIO_UNLOADED` from
  backup time to `Mission_Unload` Phase C). Don't reach for position scans.
- **`DOCK_DUMP_RATE=3`** ticks/frame (dedicated const in `Mission_Unload`, decoupled from global
  `Rule.OreDumpRate`=2): a full 28-bail load ≈ 588 ticks ≈ current TD dock time (the "match TD"
  decision). This is the dock-time dial.
- **The RA dump animation is a single fixed west-facing pose** (SHP 96–110); it can't be re-oriented
  without new art, so every RA harvester dumps facing west regardless of dock.
- **The TD refinery art (`PROC.SHP`) has a TD harvester drawn into its docking frames** (12–29) — so we
  never fire the TD building animation for an RA harvester (would show two trucks). Governing rule:
  **unload style follows the harvester** (TD-harv→TD-ref is the only "special case"; everything else
  uses the RA visible routine).
- **New art is out of scope**: I can do programmatic sprite edits (recolor/remap/composite existing
  frames) but not author original art; and custom **HD** art isn't mod-deliverable (launcher won't
  render new HD asset names). So solutions must reuse existing art/anims.

## Build / deploy / test workflow (this machine)
```
# build (from repo root):
CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake VC_CXX_FLAGS="-w;-fpermissive" \
  cmake --workflow --preset remaster
# deploy (ONLY if game not running — copying over the live mapped DLL crashes it):
pgrep -fa -i 'RedAlert|ClientG|InstanceServer'   # must be empty
cp build/remaster/Vanilla_RA/Data/RedAlert.dll \
  ~/.steam/steam/steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/CnCRemastered/Mods/Red_Alert/Vanilla_RA/Data/RedAlert.dll
```
Luke testing on the **Linux desktop** (local Proton prefix) this session. Diagnostic log (TF_DEV):
`…/CnCRemastered/tf_astar.log`. Luke OK'd auto-deploy during testing (still pgrep-guard).

## Reference assets generated this session (on Luke's Desktop)
- `~/Desktop/ra-harvester-unload-frames/` — HARV.SHP dump frames 96–110 + GIFs (the dust-loop frames).
- `~/Desktop/td-refinery-dock-frames/` — PROC.SHP docking frames 0–29 by BSTATE + GIFs (shows the TD
  harvester baked into the building art).
