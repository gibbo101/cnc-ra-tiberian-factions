# Subterranean units — locked design + arc tracker

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

## Remaining arc stages

1. Pack art (`ts_pack_art.py` pattern: TGA/meta crop contract, classic stub for
   size, +8 voxel rotation convention) + stamp `UNIT_TSSAPC`/`UNIT_TSSUBTANK`
   through the units-wave pipeline (check `Tracked=` — 3rd-occurrence trap).
2. Underground subsystem (state machine, layer list, linear mover, damage gate,
   emerge validation, force-emerge, DIG anim + crate/dev-WF hookup).
3. Sensor detection + Cloak-export render path.
4. EMP arc (disable mechanic + Pulse Cannon port) and the force-emerge wiring.
5. Audio (SUBDRIL1 + voices), balance pass, Nod tech-tree placement.
