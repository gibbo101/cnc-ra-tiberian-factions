# Code tidy

**Status:** Design. The comment pass shipped on main (every comment of ours to the `CLAUDE.md`
rules, `scripts/code_check.py` in the packager); the dead-code pass and phase 2 are planned.
**Open:** the maintainer's calls on the dead-code list below; comments inside the ts-buildings-hd
branch's ranges; phase 2.

The rules are in the repo's `CLAUDE.md`. `scripts/code_check.py` fails a package on a personal name,
an ISO date or a missing `docs/*.md` in a comment; `scripts/code_check_baseline.txt` lists the known
exceptions, and each item below that clears one also deletes its baseline line.

## Dead-code pass

Deletions are code changes: dev-only blocks (`#if 0`, `#if TF_DEV_BUILD`) go in their own commits,
release-path items in others, and each larger removal in a commit of its own with its doc edits.
Build dev and release after each commit; a skirmish before merging.

### Needs a call first
- **`Logic=` / `[NewBuildings]` / `[NewUnits]`:** the dynamic type path in bdata.cpp and udata.cpp
  (constructors, One_Time per-entry loops, Init re-copy, Read_INI `Logic=` blocks), the rules.cpp
  registration loops, the rules.ini sections and their 15 commented `MIGRATED` lines, and
  add_building.py's emission. Nothing uses them: every listed name is a static type. Keep
  `As_Pointer`. Doc edits with it: `td-building-separation-recipe.md` Prerequisites item 6, Steps 9
  and 10, gotcha 3, and any `catalogue.md` `Logic=` row.
- **TS war factory Track19/20:** the tracks, `tsweap_exit_track*.inc`, `OUT_OF_WEAPON_FACTORY_TS(_TITAN)`,
  `TsExitSortClamp` and its clamp block in dllinterface.cpp, `On_TS_Exit_Track`/`On_TS_Titan_Exit_Track`.
  Unused since the factory exits on `Rail_To`. Removing the enum entries renumbers
  `ROLL_OFF_DOCK_SEAT`, which saves store: keep `TrackControl` and `RawTracks` aligned, or keep
  placeholders. Keep `tsweap_exit_seats.inc`. Wait for ts-buildings-hd (it edits the clamp's `if`).
- **TS refinery lid and harvester bed pose:** `Ts_Lid_*`, `TsLid*`, `TS_LID_ENABLED`, unit.cpp's
  `TS_HORV_ENABLED` branch. Never run. Delete unless the pose is wanted back.
- **`BULLET_TSHUNTER`:** enum slot, bbdata.cpp registration, bullet.cpp and dllinterface.cpp branches,
  `TF_HUNTER_DRAW_SIZE`. Nothing creates it; mind the bullet enum order.
- **`ANIM_TS_SONICPULSE`:** the retired ripple, its adata.cpp entry (order-coupled tail) and draw check.
- **Sonic band levers:** `TF_Sonic_Cloak_Mode_Refresh`, `tf_sonic_cloak.flag`, the tf_sonic logs; the
  shipped look becomes constants.
- **Hunter Seeker rise code** (decided: delete, behaviour unchanged): the EMERGE/ASCENT/DESCENT
  values, `emerging` and the Height step in `TF_Hunter_Seeker_AI`; keep `DETONATE_PROXIMITY` and the
  never-dive trap.
- **Unsure:** `TF_Dev_Tunneller` and the `tf_deploy_now.flag` lever; the `_hd_udonors` entries for
  units with stubs; `TF_Sidebar_Log`; `TF_LobbyRecHouseBySlot` (written in release, read only by a dev
  log); the lobby "confirm the client sends difficulty" log; foot.cpp's blind-hunt log; building.cpp's
  DEF-OFFLINE and PROD hold logs; the NAVAL census lines in AI_Building; the NOPROG abort in
  infantry.cpp; `Exit_Object`'s `STRUCT_TSPROC` case (looks unreachable).

### Clear deletes (features shipped or bugs fixed)
- **`#if 0` logs:** house.cpp (cargo convoy, Check_Pertinent_Structures), scenario.cpp (paths, smoke
  spawn, start location, MCV spawn, and the Juggernaut, Sensor Array, Limpet, deploy-key, TS aircraft
  and TS infantry harnesses), techno.cpp (fire_at, muzzle, flame, buildtime, primary_parse),
  building.cpp (UPDATE_BUILDABLES, AIR_ITER), infantry.cpp (visceroid, ENTERCHK), unit.cpp
  (fireanim), anim.cpp, bullet.cpp (Unlimbo), cell.cpp (crate), rules.cpp (newunits parse),
  dllinterface.cpp (paths, radar and voice dispatch, state_query, objlist, assetname,
  draw_intercept, asset_name, the Phase 1e proxy, sidebar entry, bib stub).
- **Dev logs for shipped work:** the Can_Build logger; EMP pulse and order logs; scout dispatch;
  Check_Pertinent; Carryall landing; tf_hunter; FIXEDWING-LAND; tdcargo unload; YARD-EXIT;
  exit_object; AI build state; orbit probe and `tf_orbit.flag` path; HARV-WAIT and HARV-REBAIL;
  `TF_Harv_Logfile`; TSUNITS dock logs; `TF_LIMP_TRACE`; tf_facing; `TF_Tunnel_Log`; TSFIRE BURN;
  JUGG-LAUNCH, JUGG-SHELL and JUGG-SPLASH; `TF_TDPortLog`; sidebar evict; free-harvester log; the
  crest, tab-icon, click-special and launcher logs; `TF_Probe_ClientG_*` (they also stall the game
  thread at match start); deploy-key logs; mod command 1 log; placement-anchor log; apron
  emission; `TF_BIB_DIAG` and `tf_owner_row` (drop the `stealth-generator-spec.md` sentence with
  it); `TF_AStar_Cap_Trips`; SPREAD lines; startup.cpp's DLL load log.
- **Always-on cost in release builds:** dead logs that still run `getenv`/`snprintf` (drive.cpp
  TDWEAP exit track, aircraft.cpp unload log, techno.cpp TF-DMG-TRACE on every hit) and
  `TF_Naval_Assessment`'s second scan, read only by a log.
- **Unused code:** `WarFactoryOverlayTs`; the footprint presets AFLD and WEAP; Roll_On_Seat;
  `Force_Track`'s `index`; Mission_Harvest_TD's TSPROC branch; Turret_Adjust's TSHVR case;
  `UnitClass::Force_Emerge`; our inert edits in the `KILL_PLAYER_ON_DISCONNECT` `#else`.
- **Keep while open:** the AI, wave, naval, ferry, PLACE-FAIL, eco-hold, jumpjet, A* tally and
  head-on logs, each until its `todo.md` or `known-issues.md` item closes; `TF_Dump_Faction_Masks`
  (tool input for cameo_badge_build.py).

## Comments inside the ts-buildings-hd ranges

The comment pass skipped every line that branch edits. Once it merges, these need the same
treatment, names first: defines.h's `UNIT_TSMDIV` legend; unit.cpp's dock and track blocks around
`Mission_Unload`, `Mission_Harvest` and the TS refinery seats; bdata.cpp's TS war factory, dropship
bay and refinery classes and `Height()`; dllinterface.cpp's TSPROC hole seeding, the shutter sort and
selection-box contract comments; building.cpp's TS refinery, war factory shutter, apron table and
`Is_Refinery_Dock_Cell` (which needs its header back); infantry.cpp, drive.cpp, techno.cpp and
udata.cpp's TS war factory, depot and Juggernaut notes; sdata.cpp's apron smudge notes; rules.ini's
`[TSHARV]`, `[TSPROC]` and `[TSWEAP]` comments; `tsweap_exit_seats.inc`'s hand lines. Also the
comment at dllinterface.cpp's include of tf_eva_mailbox.h, under the menu-buttons branch.

## Small flags
- `scripts/factions_build.py`: the docstring and `ORDER` treat `Faction10` as Nod; `TD_HUD`,
  `faction-select-identity.md` and the emblem painter say Nod is `Faction4`.
- `scripts/wf_spawn_preview.py` must not be run: it rewrites `tsweap_exit_seats.inc` without the
  hand-set mouth seats, then fails its own check. Emit the mouth seats or move them out first.
- A few script docstrings are stale: the walker frame count (12, not 15), the TSWEAPLT stub,
  "hand-tucked pad", the cameo crest count, a dangling memory pointer in
  build_missionselect_campaigns.py.
- Whether `SHAPE_GHOST` darkens the sonic discs is unsettled; check in game before anything claims it.

## Phase 2

No wholesale move of our code out of EA files: the mod does not merge Vanilla Conquer, and code
moves out only when reworked (`CLAUDE.md`). Planned instead:
- **Shared type helpers that fix bugs:** `Is_Refinery()`, `Is_Repair_Bay()`, `Is_Construction_Yard()`,
  `Is_Airstrip()`, `Is_Radar()`, `Is_Harvester()`, `Is_Submarine()`, `Is_TS_Tree()`, `Is_TD_Faction()`
  in place of hand lists that already miss TS types (Recalc_Center, the ferry MCV test and the
  enemy air cap leave out the TS yard or helipad).
- **Drifted duplicates:** the nine superweapon grant blocks in Super_Weapon_Handler; the cached
  TD-type `As_Pointer` lookups (now enum values); the ClientG region walk (four copies); the
  attack-move dispatch sequence; the dev-flag file probes; the diagnostic log boilerplate (one
  helper, if any logs survive the dead-code pass).
- **Testing:** Python checks on built data (same-size MEG, LOC and BUI members, MIX entry counts,
  rules.ini against `mapeditor.json` and the cameo XML, format-tool round trips) run by the
  packager; then a time-boxed spike of a soak test that loads the DLL under plain Wine and runs an
  AI skirmish to catch simulation crashes.
