# TODO / backlog

Running list of things to do. Bugs/limitations live in `known-issues.md`; this is for chores,
maintenance, and queued tasks. Newest at top.

---

## DEFERRED: AI vehicles stuck in their own base (general pathfinding) (2026-06-18, Luke)

Observed live during harvester testing (blue AI base): several combat vehicles frozen in the base,
**not harvesters**. Deferred mid-session (focus is the harvester workstream); captured here so the
diagnostic data isn't lost. **NOT caused by the harvester field-selection/blacklist work** (that only
touches ore selection + `HARV-BLACKLIST`); this is pre-existing general unit pathing, almost certainly
the **known open chokepoint thread** (vehicle-vs-vehicle in a 1-tile gap; the gw==2 RETREAT path never
reaches the deadlock-breaker — see `chokepoint-reservation-design.md` + `cfe-port-plan.md`) plus raw
base congestion.

**Log evidence** (shared `tf_astar.log`, TF_DEV only; the `A* FALLBACK -> legacy` lines are the CFE-A*
port's instrumentation, not new):
- **A\* failing more than succeeding:** counters reached `success=4265 fallback=7860` in one match —
  units spam the legacy fallback every frame.
- **Two failure shapes:**
  1. **Wedged units** — e.g. `2TNK src=(126,52) dst=(123,47)`, `APC src=(126,51) dst=(122,54)` repeating
     with the **same src every frame** (not moving): trying to shuffle ~4 cells in a packed base, A* fails
     each frame, legacy doesn't resolve it.
  2. **src == dst spin** — e.g. `TDE6 src=(114,56) dst=(114,56)`, `src=(89,60) dst=(89,60)`: a unit
     ordered to its OWN cell; `Find_Path_AStar` returns 0 instantly for src==dest, so it spins in place.
     Likely a stale idle/guard order that never clears — a self-contained bug worth a look.
- **Hotspots** (most-failed dst cells): `(118,94)` 1682×, `(123,88)` 1163×, `(119,95)` 554×, `(112,56)`,
  `(89,59)` — all inside congested AI bases.

**When picked up:** start from the `src==dst` spin (smallest, self-contained) + the gw==2 breaker-gap
in the chokepoint thread. Reproduce = run a multi-AI skirmish, let bases fill, tail `A* FALLBACK` lines.

---

## Feature: cargo-coloured dock smoke for BOTH harvesters (2026-06-18, Luke)

Make the unload smoke colour reflect what the harvester is hauling, for **both** the RA harvester
(at its own refinery dust-loop) and the TD harvester (the `ANIM_TIB_FUMES` plume at an RA refinery):
- **Tiberium (TIB01) → green** (already what the TD harvester vents today via SMOKLAND).
- **Ore → grey** (SMOKEY / SMOKE_M).
- **Gems → (optional) a third tint** (e.g. blue) -- future.

**Prereq:** the TIB01-load-tracking item below (cargo currently can't tell Tiberium from ore -- both
bank as `Gold`). Ore-vs-gems is already free (`Gold` vs `Gems`).

**HD art is deliverable (corrected 2026-06-18 -- the earlier "new HD asset name never renders" was
overstated):** the mod already ships brand-new HD anim names as loose VFX ZIPs
(`Data/ART/TEXTURES/SRGB/RED_ALERT/VFX/TDFLAME-*.ZIP` etc.) registered in `RA_VFX.XML` -- that's how
the Flame Tank / chem / SAM muzzle anims render in HD. Recipe for a recoloured smoke variant:
1. Extract the HD frames: `SMOKE_M.ZIP` (TEXTURES_COMMON_SRGB.MEG), `SMOKEY.ZIP` / `SMOKLAND.ZIP`
   (TEXTURES_RA_SRGB.MEG) -- truecolor TGA, so ANY tint is possible (not limited to existing colours).
2. Recolour with `scripts/tgautil.py`; repack as a new-named VFX ZIP; drop it loose in the VFX folder.
3. Add `<Tile>` blocks to `RA_VFX.XML`; add DLL `AnimType`(s) selected by cargo + a donor-`ImageData`
   so the classic Draw_It NULL-guard is satisfied (we ignore the classic *look* -- HD-only mod).
⚠️ **Caveat:** a genuinely-new asset name can hit the FTFLAME "launcher caches the asset-name set at
install time" gremlin (see [[reference-launcher-new-asset-name-deadend]]) -- validate via a CLEAN mod
(re)install when the new ZIP first goes in, not an incremental DLL copy. Shipped Workshop versions are
a fresh install per subscriber, so release is unaffected.

---

## Idea: track TIB01 (Tiberium) load separately so harvester cargo can be told apart (2026-06-18, Luke)

Today a harvester's cargo is split only into `Gold` (ore) + `Gems` (`UnitClass`, unit.cpp). Our
Tiberium overlay `OVERLAY_TIB01` **banks as Gold** (unit.cpp:2965 -- "Tiberium banks as Ore, same
value"), so a harvester carrying real Tiberium is indistinguishable from one carrying ore. To support
e.g. **green Tiberium fumes ONLY when the harvester actually hauled TIB01** (vs grey/no smoke for plain
ore), add a per-harvester counter that increments on TIB01 pickup in `Mission_Harvest` (alongside the
`Gold += reducer` at the `OVERLAY_TIB01` case), and reset it on unload (where `Tiberium = Gold = Gems
= 0`). Small add (one bitfield member + Save/Load + the two reset sites). Ore-vs-gems is already free
(`Gold` vs `Gems`). Possible uses: cargo-specific dock smoke colour, or a UI/audio cue.

---

## Idea: passive chimney smoke on power plants + refineries (2026-06-18, Luke)

Spawn the `SMOKE_M` anim (`ANIM_SMOKE_M` -- a thin smoke column rising from the ground; 91 frames,
23x23, loops) continuously out of the chimneys/stacks of the **power plants and refineries** for
ambient life. Not the green Tiberium-fumes art (`SMOKLAND`) -- that's reserved for the harvester dock;
plain grey `SMOKE_M` for stacks.

Implementation sketch (when picked up):
- Per-building idle anim. Cleanest hook = spawn from `BuildingClass::AI` on a cadence (every N frames)
  at a per-building stack offset, OR a one-shot persistent looping anim parented to the building.
- Stack offset is per building type (the chimney pixel position on each SHP) -- a small table keyed by
  StructType (STRUCT_POWER/STRUCT_ADVANCED_POWER, STRUCT_REFINERY, and the TD equivalents
  STRUCT_TDPROC + any TD power). Reuse the `Attach_To(building)` z-order trick so smoke sits in front of
  the stack but behind anything south.
- Gate so it doesn't fire while in construction/deconstruction or when low-power/disabled (optional:
  no smoke when powered down = nice feedback).
- Cadence + lifetime tuned so stacks read as gently smoking, not belching. Lockstep-safe (no RNG, or
  seed off Frame+building ID deterministically).
- Reference art already extracted this session: `~/Desktop/harvester-puff-options/smoke_m.gif`.

---

## Docs update / prune pass — ✅ DONE 2026-06-16

Full survey (all 4 doc groups) run + acted on. Outcome:
- **Pruned (deleted, content captured elsewhere + git history):** `session-handoff-mcv-conyard.md`,
  `session-handoff-td-verification.md`, `session-handoff-weapons-port.md`, `manifest-gaps.md`,
  `tiberium-overlay-port.md`, `building-separation-plan.md`.
- **Updated (status banner / stale-body trim):** `theatre-desert-feasibility`, `td-skirmish-map-import`,
  `faction-music-feasibility`, `td-tile-hd-loose-art-investigation`, `adding-td-buildings`, `weapon-ports`,
  `td-tier1-verification`, `ui-atlas-modding`, `faction-select-identity`, `balance-v1-notes`.
  (`td-atwr`/`td-gtwr`/`td-obli` already carried RESOLVED banners — no change.)
- **Left CURRENT (verified accurate):** td-port-playbook, td-building-separation-recipe, the infantry/
  vehicle/cargo-plane recipes, td-sam/td-mlrs/td-attack-heli deep-dives, ai-targeting, mix-file-format,
  launcher-vs-dll-ownership, config-meg-mod-delivery, building-sound-routing, td-audio-routing-recipe,
  workshop-publish-runbook, campaign-tabs-research, coop-missions-design, gdi-nod-campaign-story,
  classic-mode-palette-remap (historical — classic unsupported), catalogue (self-labeled design-era).
- **Router updated:** workspace `CLAUDE.md` doc-map — removed the 6 deleted docs + the Session-handoffs
  section; added a Project-tracking group for `todo.md` + `known-issues.md`.

---

## CFE QoL first wave — ✅ COMPLETE 2026-06-16

All 8 first-wave items shipped: Pixel-Perfect Zoom, A*, Attack-Move, Rally Points, Harvester
Queue-Jump, Harvester Optimization, Smarter Repair Bay, and **Infantry Tiberium Aversion**
(commit `72b3a17`, Luke-verified). Everything CFE-related left is second-wave (`cfe-port-plan.md`
§2 candidates) or the bugfix inventory (§3) — none committed scope yet.

---

## Active work threads (tracked in detail elsewhere — index only)
- **Chokepoint / cooperative traffic — ✅ SHIPPED v2.3.0 (2026-06-16):** infantry give-way + vehicle-vs-MOVING-infantry freeze fix + open-ground hold-timeout + execution-branch head-on breaker all landed. **Open thread (minor):** vehicle-vs-vehicle head-on in a 1-tile gap with NO escape cell (gw==2 RETREAT path never reaches the breaker); self-resolves today, no gridlock — make the breaker reachable from the gw==2 path. See `chokepoint-reservation-design.md` + `cfe-port-plan.md`.
- **Harvester logic workstream:** targeting / pathing / claiming / reachability / idle-stuck + the economy-equalise (tilted-bucket dwell) idea. See the checkpoint's spun-off section + `balance-deep-dive.md`.
