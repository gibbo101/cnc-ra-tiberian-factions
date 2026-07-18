# TODO / backlog

Running list of things to do. Bugs/limitations live in `known-issues.md`; this is for chores,
maintenance, and queued tasks. Newest at top.

---

## ⭐ AI milestone Phase 1 — MERGED to main + LIVE-VERIFIED 2026-07-18 (commit `e01bc35`)

**Full handover: `docs/ai-phase1-handover.md`.** W7 difficulty→IQ, W1.5 primary-factory,
W1.2 fair-fog intel, W1.3 scouting. Merged 2026-07-18; `Vanilla_RA_AI1` desktop mod
consolidated back into the single `Vanilla_RA` local mod. Live desktop diagnostic session
(2026-07-18) verified the headline paths and root-caused two design holes, both fixed
same-session:

- **W7 verdict (measured, 5 lobbies):** GlyphX sends `CNC_Set_Difficulty(1)` in skirmish
  UNCONDITIONALLY — per-slot lobby settings, all-Easy/all-Hard lobbies and the campaign
  difficulty option all still send 1. Slot dump confirms the interface structs carry no
  per-slot channel (AI names are bare `AIPLAYER1..4`, hex-verified). **Shipped lever:
  `Documents/CnCRemastered/tf_ai_difficulty.txt`** (`easy|normal|hard`, re-read each match
  start; ABSENT = hard/MaxIQ = shipped v4.0 strength). Both paths live-verified
  (default-hard IQ5; file-easy IQ3). NOT dev-gated — release feature; document in Workshop
  copy at next release.
- **Fair-fog turtle deadlock FIXED:** AI never attacked (player-observed + screenshot).
  Root cause: `AI_Attack` shuffles (no-ops) 67% of calls and was the only hunter source, so
  blind houses never scouted → never discovered → never attacked. Fix: `Expert_AI` keeps a
  2-unit scout detail on hunt while the house knows no enemy building. Live-verified: all
  four AIs scouting by ~F2500, real `WAVE-LAUNCH` after contact, player confirmed fighting.
- **Build-choice starvation: FIXED + LIVE-VERIFIED 2026-07-18 (commit `d4f3da7`).**
  Winner scan took the first pool entry at max urgency, starving late entries (TDTMPL
  zero tie wins in ~40k frames; TDOBLI/TDATWR/TDEYE similar). Top-urgency ties now break
  uniformly (reservoir pick on the synced RNG, MP-deterministic). Verified with 6 Hard
  AIs: 98/123 decisions were real ties, every starved building won cycles (TDTMPL 5,
  TDOBLI 12, TDATWR 2, TDEYE 1), temples confirmed standing in-game; economy priorities
  intact. Diag WIN lines print `ties=N`.

**✅ RAM per-slot difficulty phase A — SHIPPED + LIVE-VERIFIED 2026-07-18 (commit
`3e156a0`):** solo skirmish now applies each lobby slot's real Easy/Medium/Hard pick to
its AI house (RED confirmed all-same first, then GREEN: Hard/Medium/Easy/Hard lobby →
IQ 5/4/3/5 on the matching houses, on-screen + log). Scanner + slot map live in
`redalert/dllinterface.cpp` next to `CNC_Set_Difficulty`; the HELLO announcements (log +
on-screen via deferred flush, commit `45bf3b0`) print each house's mode tagged
`[slot n]`/`[global]` and are the standing verification readout. Implementation notes +
the IniName-rename trap: `docs/lobby-difficulty-ram-spike.md`. Remaining:
- **⭐ Phase B (MP per-slot difficulty) — RESUME HERE (rig night 2026-07-18, full
  findings in the spike doc phase-B section):**
  1. Host-broadcast design DEAD (verified: GlyphX has no DLL-side event transport —
     `Glyphx_Queue_AI` is local-only, no packet exports, callbacks are local
     presentation; MP determinism = client-side request replay).
  2. Mirrored-lobby read as scanned is ALSO DEAD: the `AIPLAYERn` record array is each
     account's **saved skirmish config**, not the live lobby. Proven on the 2-peer LAN
     rig — joiner read its own stale config 4 matches straight, and the host's read
     contradicted its own lobby UI (which both screens rendered identically and
     correctly, so a **live lobby model exists in every peer's client** — that's the
     real target). Scanner v2 (roster-name anchor, commit `4f2a1a1`) is still right
     for the solo path.
  3. **NEXT ACTION: run one probe-v3 match** — build `8ae684f6` (commit `c036d59`)
     is ALREADY DEPLOYED on desktop + Luke's Deck. Deck hosts LAN lobby, fresh
     difficulty mix (e.g. Hard/Easy/Med/Hard), desktop joins, start, quit. The probe
     dumps hex context around each AI GlyphxID (name-hash, identical cross-peer) in
     both clients → diff host-vs-joiner `PHASEB-ID` lines in the two
     `MOD_DEBUG_AI.txt` files → derive the live model's difficulty-int offset →
     scanner v4 reads the live model on every peer (deterministic, no broadcast).
  4. **BUG (shipped phase A, found by rig reasoning):** the per-slot apply gate is
     `humans < 2`, which includes a 1-human LAN lobby — there the saved-config records
     mismatch the live lobby, so stale difficulties get applied. Fix rides the v4
     live-model read (or gate solo-apply out of LAN lobbies if distinguishable).
  Rig: 2-peer (desktop Luke + Luke's Deck on daughter aimee101; son's Deck approved
  but benched). Watch the twin-mod trap: Workshop copy and local mod are both named
  the same — local shows the higher version (4.1). Daughter's playtime limit ended
  the night; extend it before the next rig session.
- **Workshop copy at next release:** document per-slot lobby difficulty as a feature
  (and `tf_ai_difficulty.txt` as the fallback lever). DontCryJustDie is already in the
  mod credits (TD-Assets); no new ack needed — though the release notes can mention the
  difficulty collab (their process-memory pointer; their implementation built from our
  published `lobby-difficulty-ram-spike.md`, Workshop thread 2026-07-18).
- **RAM is an extraction channel, NOT a launcher unblocker** (survey confirmed): reads
  lobby selections (faction-per-slot, map, difficulty); does not move compiled-behaviour
  walls. Don't over-scope it.

**Open follow-ups from the session:**
1. **Settings-file route for per-slot difficulty: RESOLVED NEGATIVE (2026-07-18,
   measured).** The client's persisted settings
   (`userdata/<id>/1213210/remote/Player_RA_settings_1.bin`, ChunkFile + zlib@0x24, TLV
   property stream — same family as .bui) contain NO per-slot difficulty; the one byte
   that moved during flips (tag 0x31 int32) is a match-start counter. Per-slot picker
   state is ClientG memory only — which the phase-A RAM read (shipped same day, see block
   above) now extracts; `tf_ai_difficulty.txt` is the fallback lever. Don't re-chase the
   settings file.
2. **W1.2 unit-visibility leak suspicion:** zero blind-hunt SCOUT probe lines ever fired —
   dispatched scouts always found targets instantly, suggesting enemy UNITS are evaluable
   from match start (mask positionless / pre-seeded?). Buildings fog correctly. Verify.
3. **H14 APWR loop observation:** USSR AI won `APWR(u2)` 20+ consecutive build decisions
   (turtle match). Legit power-hunger or overbuild loop — check base for APWR farms.
4. Rotate `MOD_DEBUG_AI.txt` between matches during diagnostic sessions (two matches
   interleaved in one file cost real analysis time; note: the shared diag FILE* stays open
   across matches within one game process, so rotate only at full game restarts).

## A* pathfinding: O(n²) open-list insert + no expansion cap (2026-07-18, from the megamaps spike)

Found while surveying pathfinding for `docs/megamaps-feasibility.md`. **Independent of map size —
live on the current 128x128 build**, and squarely in the AI milestone's path.

- **Open-list insert is O(n).** `findpath.cpp:715` uses `open_list.insert(std::lower_bound(...))`
  into a `std::vector` — a sorted-vector priority queue with linear insertion, so the search is
  O(n²) in nodes expanded. Fix: real binary heap (`std::priority_queue` / `push_heap`).
- **No node-expansion budget.** On a *failed* search (unreachable destination) it exhausts the
  entire reachable component — up to ~16K nodes at 128x128, each with an `unordered_map` node
  allocation. A single long-range failed path can stall a frame. Fix: explicit expansion cap with
  fallback to the legacy path.

Not yet reproduced in-game — flagged by static reading, so **confirm with a diagnostic run before
optimising** (unreachable-destination order across water/walls is the likely repro). The
`unordered_map` choice itself is correct and should stay: `prev` pointers into it must survive
rehashing.

Also spotted, harmless today: `defines.h:589` — `MAP_REGION_HEIGHT` uses `REGION_WIDTH` in its
rounding term instead of `REGION_HEIGHT`. Only masked because both are 4; a landmine if regions
ever go non-square.

## TS asset spike — CLOSED (2026-07-18); no follow-up work queued

The Tiberian Sun import spike is DONE and player-signed-off (see
`docs/ts-asset-import-spike.md` for recipes + the launcher-contract trap list):
Hover MLRS ("the golden child") + Stealth Generator TS reskin + hover locomotion
+ TS audio port. **Spike outcomes are parked, not in-flight (Luke, 2026-07-18):**
TSHVR + TSPOWR are off the build menus (TechLevel=-1, commit `adfca77`) and stay
in as a working TS-pipeline reference + map-maker easter egg. The TSPOWR art
pass is DROPPED from lined-up work — not to be picked up before mod completion
at the earliest; a real TS mod would revisit it via `ts-factions-feasibility.md`.
TS hover bob likewise waits for a real second hover unit. Resolved from the
spike session since: the cloaked-bib leak (fixed `58ae18f`) and the
Temple-starvation fix (`d4f3da7`).

## ⭐ RESUME HERE — AI milestone Phase 0 (2026-07-17)

**Code COMPLETE + committed** (`bb286b5` W1.1 fixes + AGT power + harvester idle-home;
`9069392` diag v3 + AI Boost scatter/send-percentage). Full status: `ai-upgrade-plan.md` §6
Phase 0 + §3 W1.1 STATUS notes. Two verification gates remain:

1. **Temple-starvation diagnostic session** — ATTEMPTED 2026-07-17, held: the game loaded the
   Workshop 4.0.0 copy (release DLL, no logging) because the Workshop self-test left it
   enabled. Everything else is staged: dev DLL (TF_AI_DIAG v3) deployed to the desktop
   prefix, old MOD_DEBUG_AI.txt rotated, lobby remembers GDI vs Nod-MEDIUM/Docklands.
   Next run: enable the LOCAL mod (Options → Mods → Mods Folder → Vanilla_RA), play/idle
   any Nod-AI match, read `drive_c/users/steamuser/MOD_DEBUG_AI.txt` (grep TDTMPL/TDSTEAL
   + POOL/WIN lines). Freshness check: dev DLL recreates tf_astar.log within seconds.
   Claude can drive it autonomously (recipe + traps in cross-session memory:
   desktop-diagnostic-run-recipe) — needs Luke's OK to unlock the desktop session.
2. **Phase 0 soak playtest** — player-visible changes to eyeball: AGT offline on low power,
   idle harvesters retreating to the refinery, attack waves with home garrison + launch
   scatter, better AI target picks. Then Phase 1 (intel layer + scouting + difficulty
   plumbing) per the plan.

## v4.0.0 SHIPPED 2026-07-16 (Workshop + GitHub). Remaining follow-ups:

Released: media captured (videos + screenshots in `~/Desktop/TiberianFactionsinRedAlert4.0 media/`),
CHANGELOG 4.0.0 written, tag `v4.0.0`, GitHub release with `TiberianFactions-v4.0.0.zip` (404MB),
Workshop item 3729834253 updated (new logo preview, pruned description with 4.0.0 changelog).
Local dev version bumped to 4.0.1.

1. ~~ModDB page~~ — ✅ UP (Luke, 2026-07-16; page copy archived in `docs/moddb-page-copy.md`).
   May still pass through staff authorisation before it's publicly visible.
2. ~~Reddit~~ — ✅ DONE (Luke, 2026-07-16).
3. ~~Workshop self-test~~ — ✅ DONE (Luke, 2026-07-17; subscribed 4.0.0 tested fine).

**Missed from v4.0 (caught post-release 2026-07-16): Soviet parabombs.** The power-grants batch
shipped GDI GPS + Nod spy plane + Nod paratroopers, but the Soviet parabombs grant (same held-list)
was never implemented — no PARA_BOMB commits since v3.0.0. Queue for the next release.

**Next-release obligations (accrued during AI Phase 0, 2026-07-17):**
- **Workshop acknowledgements: credit Bast75 & xXMini FrankiXx (AI Boost 3.2)** — first ported
  code (scatter-on-launch, send-percentage) is now in the tree. Licence verified GPL-compatible.
- Changelog lines owed: AGT goes offline on low power (TD-canon); AI target selection actually
  picks best target (bestval fix); idle harvesters retreat to the refinery; AI attack waves
  keep a home garrison scaled by base defences (AI Boost port); AI wave-launch scatter.

**Next milestone: the AI upgrade — plan complete, see `docs/ai-upgrade-plan.md` (2026-07-17).**
Design locked with Luke (one brain + faction-building separation + heritable capture-tech,
behavioural difficulty via IQ, intel layer + fog-cheat removal, blob attacks, naval + water
eval, transports, coordination, directional armour, reservation-table pathfinding). All six
research reports integrated. Start at the plan's Phase 0.

- **BUG (Luke, live match 2026-07-16): Nod AI not reaching Temple → Stealth Generator in
  practice.** Static suspects: both slots gated `Power_Fraction() >= 1` (Nod hovers at marginal
  power; Obelisks -150) and both URGENCY_MEDIUM in a single-winner-per-cycle build-choice pool, so
  defence/factory picks starve the Temple indefinitely (house.cpp:6815 tech slot, :6607 stealth
  slot). Verify with a dev-build diagnostic session (release builds log nothing), then fix as part
  of the AI build-order rework (same thread as the eco-passivity item).
  **Sequencing decided (Luke, 2026-07-17):** the fix rides the W3 build planner (plan §3 W3.1
  already subsumes it) — no interim Phase-0 patch unless the diagnostic reveals a one-liner. The
  diagnostic itself stays in Phase 0: it validates the root-cause hypothesis W3's design leans on,
  and the build-choice decision log it needs is the milestone's day-one instrumentation anyway.

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
