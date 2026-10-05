# Naval and air units for GDI and Nod

**Status:** Reference; shipped in 4.0.0, the Nod paratroops and recon flight as their own
superweapons in 5.0.0.

TD only ever had naval units in scripted missions, and its A-10 was a support power. GDI and Nod
need buildable fleets on water maps (the skirmish AI builds navies, `ai-upgrade-plan.md` W5), so
this is a deliberate step past TD-authentic. Live stats are in rules.ini.

## The rule: separated types, never owner-opened RA ones

Each faction gets its own production building and units. The RA buildings and units stay with
their RA owners: `[SYRD] Owner=allies`, `[SPEN] Owner=soviet`, `[AFLD] Owner=soviet`,
`[SS] Owner=soviet`. Opening a shared RA building or unit to GDI or Nod leaks its whole roster and
its superweapon grants (the first navy and A-10 builds did, and were reverted); give the faction
its own type instead. The one shared piece is the RA transport, `[LST]`, owned by every side.

## Roster

| Faction | Building | Units |
|---|---|---|
| GDI | GDI Naval Yard (`TDGYARD`, prerequisite `powr`) | clones of the three Allied ships with their native turrets: `TDPT` Gunboat (RA PT, MGUN turret, `2Inch` + `DepthCharge`), `TDDD` Destroyer (RA DD, SSAM turret on a fore mount, `Stinger` + `DepthCharge`), `TDCA` Cruiser (RA CA, twin TURR guns, `8Inch`, needs TDEYE) |
| Nod | Nod Sub Pen (`TDNPEN`, prerequisite `powr`) | `TDNSUB` Submarine (RA's SS hull: TD had no submarine art), `TDMSUB` Missile Sub (Temple-gated) |
| both | | the RA `LST` transport |
| GDI | GDI Airfield (`TDGAFLD`, behind TDHQ) | `TDA10` A-10 Warthog: fixed-wing napalm strafer, 60 HP, 3 runs a sortie, TD's `A10.ZIP` (32 frames) |

**Dormant** (`TechLevel=-1`; enum slots, art and turret seat tables kept for revival): the TD
Gunboat `TDBOAT`, the Hovercraft `TDLST`, the Obelisk Sub `TDOBLISUB` and a Helicarrier. The
Obelisk Sub carries a working charge wind-up: it surfaces, plays the Obelisk power-up hum and is
exposed for about 3 s before the laser fires (`VesselClass::AI`, gated in `Can_Fire`, the
`ObeliskCharge` timer); its laser is a clone (`[TDObeliskSubLaser]`) so it tunes apart from the
building's.

## Support powers

All granted by a host building, the Ion Cannon pattern, in `HouseClass` (`house.cpp`):
- **Parabombs** (`SPC_PARA_BOMB`): any house with an active real airstrip (`STRUCT_AIRSTRIP`).
- **GPS** (`SPC_GPS`): the Allied tech centre, or GDI's TDEYE, which is GDI's tech-centre
  equivalent.
- **Nod paratroops** (`SPC_TD_PARA_INFANTRY`): the Nod Airstrip plus the Hand of Nod. TD
  Minigunners drop from the targetable TD C-17 (`AIRCRAFT_TDPARADROP`, `TDC17P`), as many as it
  carries. The special that fired decides the delivery, so a captured cross-era pair drops that
  era's troops.
- **Nod recon flight** (`SPC_TD_SPY_MISSION`): the Nod Airstrip; the U2 flyover on its own timer.

## Ship art from 3D models

- **Image to model:** a clean hull view fed to an image-to-3D service (TRELLIS or Hunyuan3D-2) for a
  GLB. Running TRELLIS locally needs more VRAM than this machine has.
- **Render:** portable Blender (`~/blender-portable/blender`), `scripts/render_gunboat_facings.py <glb>
  <outdir> [bow_deg] [pitch] [scale]`: an orthographic camera at 54° elevation (a destroyer's
  foreshortening, 0.81 = sin 54°), 16 facings, transparent PNGs. The voxel fleet uses 32° instead
  (`ts-gdi-tree-plan.md`).
- **Package:** `scripts/pack_render_to_tileset.py <renderdir> <ININAME> <target_len_px> <canvas>
  <out.zip>` scales the east hull to the target length and writes the tileset ZIP.
- **Clone-ship HD art runs counter-clockwise:** heading → frame = (16 − s) % 16.
- **Turret seats come from marked dots:** a pure-red dot at the mount point on N/NE/E stills (blue
  for an aft mount), and `scripts/bake_turret_seats.py` fits the orbit and emits the per-facing
  `Turret_Adjust` tables.
- **Team colour:** the green region is the house-remap zone. Team green needed a 1.45x lift for the
  launcher's brightness-preserving remap, capped at deck brightness (higher drew halos round the
  cabin). A shadow baked into a GLB texture is not a render shadow; re-render with a fill light
  rather than painting over it (`scripts/tdboat_hull_postprocess.py`).
- HD draw scales classic pixels by about 5.33 (128/24).
