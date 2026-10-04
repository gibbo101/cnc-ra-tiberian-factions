# Subterranean units

**Status:** Reference; shipped in 5.0.0.
**Open:** the Devil's Tongue side-nozzle jet seats (`todo.md`); save/load of the tunnel state has
never been tested.

The Devil's Tongue (`UNIT_TSSUBTANK`) and Subterranean APC (`UNIT_TSSAPC`) are Nod units in TS, so
here they are crate-only finds (`_ts_goodies` in `cell.cpp` `Goodie_Check`, `TechLevel=-1`). They dig
on longer trips (a port of TS's `tunnel.cpp`), a Sensor Array reveals them, and the E.M. Pulse brings
them up at the nearest ground. Dev builds start the player with a Subterranean APC. Pairs with
`emp-cannon-design.md`: neither shipped without the other.

## What ships

**The port.** `reference/OpenTS/code/tunnel.cpp` is TS's `TunnelLocomotionClass`, and OpenTS
`unit.cpp` ~5220-5360 is TS's drive-vs-dig decision. TS digs on every move order unless a short
unbroken surface route exists (`Is_Route_Broken`: same zone, Chebyshev < 12, trial walk ≤ 15
steps); underground travel is a straight line at 19 leptons a tick through any terrain; arrival on a
blocked cell retargets with `Nearby_Location` (same zone first, then any); with no legal cell
anywhere it self-destructs; a stop order underground heads for the nearest surfaceable ground.

- **State machine** (`UnitClass::Tunnel_AI`, `unit.cpp`): `TUNNEL_IDLE / TURNING / DIGGING_IN /
  TUNNELING / EMERGING / ABORTING`. `Assign_Destination` runs `Should_Dig_To` (another zone, or a
  distance of at least `[General] TunnelDigThreshold=6`; never an adjacent cell).
- **While underground:** `UnitClass::Mark` keeps `IsDown` without cell occupancy;
  `TechnoClass::Is_Tunneling()` folds into `Is_Cloaked` for every non-ally query; the launcher
  export is `Cloak=CLOAKED` with `VisibleFlags` cleared for non-allies; `Take_Damage` is immune
  unless forced; `Can_Fire` returns FIRE_BUSY; no scatter and no unload. Water and cliff clicks
  are legal orders (`What_Action` → the nearest emerge cell).
- **The Subterranean APC** carries 5, digs with them, refuses to unload underground, and a stop
  order with cargo surfaces nearby.
- **The Devil's Tongue flame** is TS's: TSFire particles (FLAMEALL 4x19) in a FireStreamSys stream
  (2 per 4 frames x 30), twin prongs (one jet from each side nozzle, as the FMVs show), and TS's
  `[Fire]` verses. Damage is TS's `Modify_Damage` computed in the bullet (`BulletClass::AI`): distance
  / 10, the SpreadFactor scale at x1 for TS's 48 px cells, clamped to 16, MinDamage only inside 4.
  It is delivered unscaled through `WARHEAD_TSFLAMEHIT`, because RA's 24 px cells would scale the
  same formula by 400 instead of 80. A particle's state advance is sized so it reaches its target at
  state 14 and dies five states later. A dead target falls back to `TFDwell`: `As_Coord` on a dead
  target returns the map origin, which gave flames a map-wide lifetime. The jet seats are still `PrimaryOffset` 0x80 forward and 0x30 lateral
  (`udata.cpp`) and want measuring off the side nozzles of the packed N frame.
- **Detection:** the Mobile Sensor Array shows buried enemies in range to its owner only, as
  ghost copies that can be seen but not attacked (`emp-cannon-design.md`).
- **The E.M. Pulse** stuns a digger and reroutes it to the nearest emerge cell, exploding it only
  if there is none (`Tunnel_Explode`). `UnitClass::Force_Emerge` predates that and has no callers
  (dead code, `todo.md`).
- Dev builds trace the dig cycle to `MOD_DEBUG_TUNNEL.txt`.

## Design

- **A first-class subsystem, not clones:** its own state machine, underground tracking, damage gate
  and detection state; nothing shared with the cloak, limbo or submarine systems.
- **A live object while under, not limbo** (a limbo'd object has no world presence, which breaks
  the EMP and detection): a real `Coord`, ticked straight-line movement with no A* and no zones,
  out of surface occupancy and target scans.
- **Terrain:** underground travel ignores all terrain, water included; the only rule is where it
  may emerge (no water, rock, occupied cell or building). A dig ordered onto water emerges at the
  nearest legal cell.
- **Detected means seen, not attackable,** as in TS.

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

## Art

- `SUBTANK.VXL/HVA`, `SAPC.VXL/HVA` extracted; **both rendered clean** at the
  FLEET-STANDARD camera: `vxl_render.py --frames 32 --yaw0 90 --px-per-voxel 12
  --elev 32`, the fleet angle (54° reads top-down).
  Devil's Tongue = twin flame prongs forward; SAPC = striped drill nose.
- `DIG.SHP` (37 frames): mound erupts → churns → collapses to a settling ring.
  ⚠ Decode anims with **remap=None** — `ts_shp.py`'s CLI hardcodes remap 16–31
  team paint, which turned the thrown-dirt highlights fake green.
  In ANIM.PAL, 16–31 are real tan/ochre dirt tones; the anim is ALL earth (no
  baked grass), so it sits fine on any theater. Packed by `scripts/ts_pack_dig.py` as
  `ANIM_TS_DIG` (TSDIG.ZIP, 37 tiles, x4 on a 512 canvas, 64x64 stub).
- **Dive/emerge is NOT an asset — TS did it as an engine transform** (voxel
  pitched nose-down and sunk under the DIG mound; proof: the complete 282-entry
  `[Animations]` registry has only DIG + DIRTEXPL, SAPC.HVA = 1 static frame,
  and both units carry `IsTilter=yes` runtime-tilt flags). Recreated by baking
  pitched renders, 8 directions. The ladder: dive `0/-8/-16/-24/-32/-40`,
  emerge `+40/+32/+24/+16/+8/0`, 8 main facings (DLL snaps facing at dig start),
  ~112 total shapes — under the 128 sub-object cap. DLL adds the sink offset and
  plays DIG over the top during DIGGING_IN/EMERGING.
  ⚠ `vxl_render.py --pitch` was once parsed but never forwarded to `render_frame`, so every CLI
  pitch render was flat; fixed.
- `DIRTEXPL.SHP` is extracted but unused. Cameos `SUBTICON.SHP` / `SAPCICON.SHP`. SUBDRIL1 (dig)
  and FLAMTNK1 (flame) ship as MS-ADPCM WAVs (`td-audio-routing-recipe.md`).

## Transition choreography

Dialled over five preview rounds and encoded in the DIGGING_IN / EMERGING states; the tick counts
are the tunables:

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
