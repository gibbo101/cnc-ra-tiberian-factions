# Code tidy

**Status:** Design. The comment pass shipped on main (every comment of ours to the `CLAUDE.md`
rules, `scripts/code_check.py` in the packager); the dead-code pass has removed the stubbed and
shipped-work logs; the rest of it and phase 2 are planned.
**Open:** the maintainer's calls on the dead-code list below; the rest of the clear deletes; the logs
held for open items; comments inside the ts-buildings-hd branch's ranges; phase 2.

The rules are in the repo's `CLAUDE.md`. `scripts/code_check.py` fails a package on a personal name,
an ISO date or a missing `docs/*.md` in a comment; `scripts/code_check_baseline.txt` lists the known
exceptions, and each item below that clears one also deletes its baseline line.

## Dead-code pass

Deletions are code changes: dev-only blocks (`#if 0`, `#if TF_DEV_BUILD`) go in their own commits,
release-path items in others, and each larger removal in a commit of its own with its doc edits.
Build dev and release after each commit; a skirmish before merging.

### Needs a call first
- **Kept:** `TF_Dev_Tunneller` and its tick, the `tf_deploy_now.flag` lever, and the EVA cache
  patch's `tf_cache_probe.log` lines in dllinterface.cpp.

### Clear deletes (features shipped or bugs fixed)
- **Keep while open:** the AI, wave, naval, ferry, PLACE-FAIL, eco-hold, jumpjet, A* tally and
  head-on logs, each until its `todo.md` or `known-issues.md` item closes; `TF_Dump_Faction_Masks`
  (tool input for cameo_badge_build.py).
- **Keep until their fixes are signed off in play:** HARV-UNSTICK, HARV-BLACKLIST, HARV-FIELD and
  `TF_Harv_Logfile` (the harvester follow-ups in `known-issues.md`); `TF_LIMP_TRACE` (Tick Tank and
  Mobile War Factory deploys); JUGG-LAUNCH, JUGG-SHELL and JUGG-SPLASH (Juggernaut scatter); sidebar
  evict (Mammoth Mk. II and Mech Division cameos leaving with the Tech Center); the DEPLOY-KEY,
  DEPLOY-FLAG and mod command 1 logs (Mobile War Factory pack-up); the placement-anchor PLACE lines
  (tower plugs); tf_mwf; tf_sort (the war factory bay).

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
