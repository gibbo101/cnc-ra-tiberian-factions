# TODO / backlog

Running list of things to do. Bugs/limitations live in `known-issues.md`; this is for chores,
maintenance, and queued tasks. Newest at top.

---

## v4.0.0 SHIPPED 2026-07-16 (Workshop + GitHub). Remaining follow-ups:

Released: media captured (videos + screenshots in `~/Desktop/TiberianFactionsinRedAlert4.0 media/`),
CHANGELOG 4.0.0 written, tag `v4.0.0`, GitHub release with `TiberianFactions-v4.0.0.zip` (404MB),
Workshop item 3729834253 updated (new logo preview, pruned description with 4.0.0 changelog).
Local dev version bumped to 4.0.1.

1. ~~ModDB page~~ — ✅ UP (Luke, 2026-07-16; page copy archived in `docs/moddb-page-copy.md`).
   May still pass through staff authorisation before it's publicly visible.
2. ~~Reddit~~ — ✅ DONE (Luke, 2026-07-16).
3. **Workshop self-test:** subscribe update + smoke-test headline features (navy, A-10, stealth gen).

**Missed from v4.0 (caught post-release 2026-07-16): Soviet parabombs.** The power-grants batch
shipped GDI GPS + Nod spy plane + Nod paratroopers, but the Soviet parabombs grant (same held-list)
was never implemented — no PARA_BOMB commits since v3.0.0. Queue for the next release.

**Next milestone: the AI-focus pass** (air-build escalation retune + general skirmish-AI
improvements + the deferred stuck-in-base pathfinding).

- **BUG (Luke, live match 2026-07-16): Nod AI not reaching Temple → Stealth Generator in
  practice.** Static suspects: both slots gated `Power_Fraction() >= 1` (Nod hovers at marginal
  power; Obelisks -150) and both URGENCY_MEDIUM in a single-winner-per-cycle build-choice pool, so
  defence/factory picks starve the Temple indefinitely (house.cpp:6815 tech slot, :6607 stealth
  slot). Verify with a dev-build diagnostic session (release builds log nothing), then fix as part
  of the AI build-order rework (same thread as the eco-passivity item).

---


## Stood down — not doing (2026-07-15, Luke)

Cleared off the active backlog by decision (not implemented). Design docs retained for reference
only; do not resume without Luke re-opening.

- **ModText.csv fleet-wide naval naming** (Naval Yard, Sub Pen, Missile Sub) **+ classic SHPs for
  the RA-art naval clones** (TDPT/TDDD/TDCA/TDNSUB/TDMSUB). Was a navy-session "next candidate".
- **Harvester docking rework** (economy-balance; converge RA harvester onto the TD attach-dock
  mechanic). No code was written. Plan doc `harvester-docking-rework-plan.md` kept as reference.
- **Nod defensive-economy gap** (AGT vs Obelisk+SAM) — stood down; see the Defences-balance section
  below, left in place for context but not being actioned.

**AI-focus pass is POST-v4.0** (air-build escalation retune + skirmish-AI improvements + the deferred
stuck-in-base pathfinding) — not part of the current milestone.

---

## v4.0 air / paratroopers / balance — open threads (2026-07-13, live)

Spun out of the air-AI + power-grants session. The 2026-07-13 batch (airfield/A-10 AI routing,
3 power grants, AI air-responsiveness max-threat + limit-mirror, MCV/ConYard/AGT,
Nod-paratrooper-drops-minigunners) is **playtest-verified (Luke, 2026-07-16)**. Open items on top:

_(Nod SAM accuracy: ROT 10->20 shipped; no longer tracked as a discrete item — watch it during
the AI-focus pass.)_

**Done this milestone:** Nod Stealth Generator (shipped 2026-07-15, Gap-Generator art, cloak
field + bib-hide + helipad/aircraft cloak + teardown restore + 400 HP + organic Nod-AI build —
see `docs/stealth-generator-spec.md`); Nod paratrooper C-17 plane (`TDC17P`, targetable/radar-
visible support-drop twin of TDCARGO); AI air-build priority dropped to LOW (war factory first);
Nod Flame Bunker (`STRUCT_TDFBNK`, anti-infantry flame defence, Nod-AI build rule); **GDI GPS
full Allied parity** — flicker fixed (removal checks recognise TDEYE past the 32-bit BScan mask)
AND launch fixed (fire loop + `Mission_Missile` now launch the GPS satellite from TDEYE, so it
reveals + doesn't restart); Ion Cannon reverted to the TD-authentic 10-minute charge (dropped the
dev 1-second shortcut).

---

## Defences balance — Nod defensive-economy gap + optional Tesla chain (2026-07-13)

Spun out of the v4.0 building balance dive. Building HP is fine (the `MaxStrength*2` at load —
bdata.cpp Read_INI — equalises TD buildings to RA scale). Two open threads:

- **Nod defensive economy is much worse than GDI's.** GDI's Advanced Guard Tower is a cheap
  (1000 / −20 power), dual-purpose (AA+AG via TDSSM), **Burst=2** tower that covers ground *and*
  air in one building. Nod must pay for the Obelisk (1500 / −150, ground-only) **plus** a separate
  SAM (750 / −20, air) — ~2.25× cost, ~8.5× power for the same coverage — and Nod's light-vehicle +
  Apache roster is exactly what the AGT eats (1.7 eff DPS vs light, plus AA). **Lever:** AGT cost/power
  (curb cheap spam), or a Nod defensive-economy buff (cheaper Obelisk/SAM, or a dual-purpose Nod
  option). NOT the AGT warhead — vs-light is untouched by the reverted F8 buff. Test in a GDI-vs-Nod
  skirmish before tuning.
- **Optional: Tesla "chain" to low-HP targets (esp. infantry).** RA1's Tesla does NOT chain in this
  codebase (single-target, Spread=1); the group-clear feel is the Super warhead one-shotting infantry.
  Could be added as a code feature (arc to nearby targets) if we want the RA2-style behaviour — parked.
- **Done this session:** AGT vs-heavy reverted 50%→25% (it was already strong via Burst=2 + AA +
  cost/power). Obelisk range left at 7.5 (< Tesla 8.5) deliberately — higher damage, shorter reach.

---

## A-10 napalm bombs fall ~4x faster than TD (double falling physics) — ✅ DONE, playtest-verified (Luke, 2026-07-16)

TD-port Dropping bullets (BULLET_TDNAPALM) got falling physics applied twice per frame:
RA's `ObjectClass::AI()` integrated Height/Riser with `Rule.Gravity` (3/frame decay) AND
`BulletClass::AI_TD()`'s TD-verbatim Dropping branch integrated again with TD's 1/frame
decay. TD intended 1/frame only, so bombs hit the ground much earlier than TD's.

**Fix (bullet.cpp, uncommitted):** `Unlimbo_TD` no longer sets `IsFalling` for TD-port
ballistic bullets, so `ObjectClass::AI()` no longer runs its parallel integrator — the
`AI_TD` arcing/dropping branch is now the sole (TD-verbatim) integrator, giving TD's exact
fall (start Height = FLIGHT_LEVEL = 256 = TD's `Pixel_To_Lepton(24)`; 1/frame decay ⇒ ~22
frames vs the buggy ~9). Because `ObjectClass::Limbo()` removes the bullet from
`In_Which_Layer()` (Height-based) at detonation, `AI_TD` now mirrors the base's map-layer
transition (Map.Remove/Submit on layer change) so removal can't miss and dangle a pointer.
Verified: `In_Which_Layer()` reads only Height (not IsFalling), and TD-port bullets never
touch the native `AI()` path that keys landing off `IsFalling` — so dropping the flag is
side-effect-free on the TD path. Only affects TDNapalm today (only Dropping TD-port bullet);
fix is symmetric so any future Arcing TD-port bullet is covered too.

Committed as `7c07015`; bombing-run feel playtest-confirmed by Luke (2026-07-16).

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
- **Harvester logic workstream:** targeting / pathing / claiming / reachability / idle-stuck + the economy-equalise (tilted-bucket dwell) idea. See the checkpoint's spun-off section + `balance-deep-dive.md`. **(Docking rework STOOD DOWN 2026-07-15 — see top of file.)**

---

## Idea: post-v1 faction-specific MCV / ConYard split (parked)

GDI/Nod currently share `UNIT_TDMCV` / `STRUCT_TDFACT` (dual-ownership Unlimbo guard). A later split
into faction-specific MCVs + Construction Yards would fit v4.0's separated-types direction. Not
scheduled — noted so the intent isn't lost. (Migrated from memory 2026-07-15.)
