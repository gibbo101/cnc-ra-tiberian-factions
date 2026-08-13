# Subterranean units — locked design + arc tracker

> **⭐ RESUME HERE (2026-08-13 late session: STAGE 1 COMPLETE, deployed to Deck).**
> **Done:** design LOCKED; art regenerated + packed (`ts_pack_subterranean.py`:
> 112 shapes/unit = 32 driving + 40 dive + 40 emerge, 384 canvas, 48x48x112
> classic stubs in TFASSETS.MIX); `UNIT_TSSUBTANK`/`UNIT_TSSAPC` stamped
> (ctors, APC door/unload chains incl. Mission_Unload, rules.ini behind
> TSWEAP for testing, Tracked=yes both); DLL built + rsync'd to the Deck,
> md5-verified. **AWAITING Luke's drive test** (both buildable from the TS
> war factory; TS MCV spawns for every human at skirmish start).
> **Shape layout contract (DLL side):** driving = facing frame 0-31; dive =
> 32 + (facing/4)*5 + step (pitches 8/16/24/32/40 nose-down); emerge =
> 72 + (facing/4)*5 + step (40 down to 8 nose-up); 0-pitch steps reuse the
> driving frame.
> **Pick-up steps:**
> 1. Still pending: cherry-pick the `--pitch` fix (`de359bd7`) to `ts-units`
>    when convenient + check dropship/VTOL flare art wasn't rendered flat.
> 2. Pre-existing gap found (NOT ours): UNIT_TSAPC is missing from the
>    Mission_Unload case list — the Amphibious APC likely cannot unload
>    passengers. Belongs to the ts-units instance; flag to Luke.
> 3. Next work: the underground state machine (see "Remaining arc stages").
> **Open decisions (Luke):** detector unit (MRJ + ported Sensor Array vs one
> shared) · sensed = reveal-only vs attackable · water-click = nearest-shore
> emerge vs refuse order.
> **Deploy surface: the DECK (Luke, 2026-08-13)** — the other Claude instance
> works on the Linux desktop, so this arc deploys to `steamdeck` (100.68.30.94).
> Usual rules: pgrep the live game first, md5-verify after deploy.

**Origin (2026-08-13):** community challenge (Madrox8: "you're not going to fully
recreate the subterranean feature, just workarounds" — Luke: "Challenge....accepted").
Goal: a REAL underground subsystem in the DLL, not the air-unit/stealth workaround
chain used on INI-only engines. Nod-faction feature; crate-spawn + dev-gated GDI
war-factory entry for testing.

**Worktree:** `../tf-subterranean-worktree`, branch `subterranean` (based on
`ts-units` @ `20350226` for the TS art pipeline). Kept separate from the GDI tree
work per Luke.

## Locked design (all Luke-ratified in-session)

- **First-class subsystem, not clones.** Own state machine on the unit:
  `SURFACED → DIGGING_IN → UNDERGROUND → EMERGING`, plus `FORCE_EMERGE` (EMP).
  Own underground tracking (optionally own occupancy), own damage gate, own
  detection state. Nothing shared with cloak/limbo/sub systems — zero regression
  surface on subs, harvester dock, stealth generator.
- **Live object while under** (NOT limbo — limbo'd objects have no world presence,
  which breaks EMP and detection). Real `Coord`, ticked straight-line movement
  (distance/speed, no A*, no zones), pulled out of surface occupancy and normal
  target scans, immune to all damage except whitelisted (EMP).
- **Terrain rules:** underground travel ignores ALL terrain including water
  (TS-authentic — Luke: diggers could cross under water, "they just couldnt
  surface there"). The ONLY terrain rule is emerge validation: no water/rock/
  occupied/building; normal arrival scans outward for the nearest legal cell.
- **EMP interaction (the reason limbo died):**
  - Force-emerge on a legal cell → surfaces + disabled for the EMP timer.
  - Force-emerge on an unpassable cell (water, rock, under a building) →
    **DESTROYED** (Luke: "BOOM! Destroyed" — overrode the nearest-land option).
    Emergent counterplay: defender EMPs their own base footprint to execute
    lurking diggers. Present as muffled underground explosion (dirt burst, no wreck).
  - Player-ordered dig ENDING on water = the gentle case: emerge nearest legal
    cell to the click (convenience, not punishment).
- **Detection:** sensor-capable units set an `IsSensed` state; a sensed underground
  unit is exported to the launcher with `Cloak=CLOAKED` → shimmer silhouette +
  health bar + selection box for free (per-object Cloak crosses the DLL boundary,
  `dllinterface.cpp:5553` — presentation reuse only, the wire format is fixed).
  Undetected = not exported at all. MRJ's `IsJammer` radius scan is the skeleton
  to crib for the sensor tick.
- **EMP does not exist in the mod yet.** Arc order: underground system first with
  `Force_Emerge()` as a real function nothing calls; EMP arc second (TechnoClass
  disable timer gating fire/move/AI/production + TS EMP Pulse Cannon building
  port); wire the warhead's underground sweep last. Neither ships to the Workshop
  without the other — the counter must exist when the threat goes public.

## Open decisions (non-blocking)

- Detector unit: MRJ gains sensor duty for RA era + port TS Mobile Sensor Array
  for TS era, or one shared unit. (Lean: split.)
- Detected = reveal-only (TS-authentic, lean) vs attackable underground.
- Water-click orders: emerge-at-nearest vs refuse at order time.

## TS source data (extracted from Steam TS `TIBSUN.MIX` LOCAL.MIX RULES.INI)

| | SAPC (Subterranean APC) | SUBTANK (Devil's Tongue) |
|---|---|---|
| Prereq | NAWEAP,NATECH | NAWEAP,NATECH |
| Strength | 175 | 300 |
| Armor | heavy | light |
| TechLevel | 6 | 7 |
| Sight | 5 | 5 |
| Speed | 5 | 5 |
| Cost | 800 | 750 |
| ROT | 5 | 6 |
| Weapon | — (Passengers=5) | FireballLauncher, **NoMovingFire=yes** |
| Other | Crusher, PipScale=Passengers | Crusher, elite SELF_HEAL, TypeImmune |
| CrateGoodie | **yes** (canon supports the crate plan) | **yes** |

TS `[General]`: `TunnelSpeed=1`, `DigSound=SUBDRIL1`, `Dig=DIG` (dig-in AND emerge
anim). `[DIG]` art: `Surface=yes`. FireballLauncher is Damage=0 + fire particles
(ROF=50, Range=4.25, Burst=2, Warhead=Fire, Report=FLAMTNK1) — map onto our ported
TD Flame Tank weapon chain rather than porting the particle system.

## Art status (2026-08-13 — DONE, staged in session scratchpad `subterranean/`)

- `SUBTANK.VXL/HVA`, `SAPC.VXL/HVA` extracted; **both rendered clean** at the
  FLEET-STANDARD camera: `vxl_render.py --frames 32 --yaw0 90 --px-per-voxel 12
  --elev 32` (Luke's 2026-08-04 fleet angle per `ts_pack_units_wave.py` — NOT the
  54° spike default, which reads top-down; Luke caught a first render at 54).
  Devil's Tongue = twin flame prongs forward; SAPC = striped drill nose.
- `DIG.SHP` (37 frames): mound erupts → churns → collapses to a settling ring.
  ⚠ Decode anims with **remap=None** — `ts_shp.py`'s CLI hardcodes remap 16–31
  team paint, which turned the thrown-dirt highlights fake green (Luke caught it).
  In ANIM.PAL, 16–31 are real tan/ochre dirt tones; the anim is ALL earth (no
  baked grass), so it sits fine on any theater. True-color frames staged in
  `dig_frames_true/`.
- **Dive/emerge is NOT an asset — TS did it as an engine transform** (voxel
  pitched nose-down and sunk under the DIG mound; proof: the complete 282-entry
  `[Animations]` registry has only DIG + DIRTEXPL, SAPC.HVA = 1 static frame,
  and both units carry `IsTilter=yes` runtime-tilt flags). Recreated by baking
  pitched renders — **Luke signed off the 8-direction dive/emerge motion
  ("looks good!") 2026-08-13.** Approved ladder: dive `0/-8/-16/-24/-32/-40`,
  emerge `+40/+32/+24/+16/+8/0`, 8 main facings (DLL snaps facing at dig start),
  ~112 total shapes — under the 128 sub-object cap. DLL adds the sink offset and
  plays DIG over the top during DIGGING_IN/EMERGING.
  ⚠ `vxl_render.py` BUG FIXED here: `--pitch` was parsed but never forwarded to
  `render_frame` — every CLI pitch render ever made was silently FLAT.
  **Cherry-pick to `ts-units`** and check whether any dropship/VTOL art expected
  a flare pitch (it came out flat if rendered via the CLI).
- `DIRTEXPL.SHP` extracted — ready-made for the EMP-over-unpassable BOOM kill.
- Cameos `SUBTICON.SHP`/`SAPCICON.SHP` extracted. `SUBDRIL1.AUD` NOT in
  CONQUER.MIX — chase in a sound mix during the audio stage (MS-ADPCM re-encode
  rule applies, see launcher-render-contracts.md).
- Scratchpad is session-scoped: re-run the extraction (recipe above, tools/
  ts_extract.py) if starting fresh; contact sheets `sheet_subtank/sapc/dig.png`.

## Transition choreography (Luke-approved 2026-08-13, GIF v5 — the stage-2 spec)

Dialled over five preview rounds on the Desktop GIF; encode these rules in the
DIGGING_IN/EMERGING states, with tick counts as the tunables:

- **Angle leads, sink follows.** The 5-step pitch ladder plays AT SURFACE level
  (no submergence while tilting; only a small cosmetic settle, ~0→26px at pack
  scale across the steps).
- **Tilt starts clean** — no dirt for steps 1–3. The DIG anim fires at step 4,
  when the nose is well into the angle.
- **Into the soil = GONE.** The hull hides the instant step 5 completes, while
  the DIG mound is still solid. No slide-under, no tail poking out. The mound
  churns out alone over the hidden object.
- **Emerge mirrors it:** DIG erupts at the exit cell over the hidden object;
  the hull appears at the steepest emerge frame mid-churn; the soil settles
  while the ladder levels off, finishing clean before the unit drives away.
- Preview cadence (110ms GIF ticks, a starting point for engine frames):
  2 ticks per ladder step, DIG at tick 6, hidden at tick 10, DIG spans ~14.
- Preview artifacts: `~/Desktop/subterranean-underground-cycle.gif` (full
  cycle) and `subterranean-dive-preview.gif` (stationary close-up). Both
  regenerate from the packed zips + scratch DIG frames; the builder scripts
  live in the session transcript, but the rules above are the contract.

## Remaining arc stages

1. Pack art (`ts_pack_art.py` pattern: TGA/meta crop contract, classic stub for
   size, +8 voxel rotation convention) + stamp `UNIT_TSSAPC`/`UNIT_TSSUBTANK`
   through the units-wave pipeline (check `Tracked=` — 3rd-occurrence trap).
2. Underground subsystem (state machine, layer list, linear mover, damage gate,
   emerge validation, force-emerge, DIG anim + crate/dev-WF hookup).
3. Sensor detection + Cloak-export render path.
4. EMP arc (disable mechanic + Pulse Cannon port) and the force-emerge wiring.
5. Audio (SUBDRIL1 + voices), balance pass, Nod tech-tree placement.
