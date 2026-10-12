# C&C3 railgun shot

**Status:** Reference. The Mammoth Mk. II fires with C&C3's railgun shot; any weapon can, with `RailBeam=yes`.

C&C3's upgraded Mammoth and Predator fire `FX_RailGunFire` and hit with `FX_RailGunHit`: a white-hot core in a blue
glow, pale threads in long slow waves around it, a flare at the muzzle and a white bloom with sparks at the impact.
The values below come from C&C3 1.9's compiled data, checked against footage of the upgraded Mammoth firing.

## How it is drawn

The launcher draws every exported sprite unrotated, whatever `CNCObjectStruct::Rotation` says: as an anim, as a
unit-typed export, with or without `SHAPE_FADING`. So no piece of the shot is turned art; it is built from round
pieces laid along the line, plus the launcher's own beam line.

- **Core:** the launcher's beam line from muzzle to target (`TechnoClass::Set_Beam_Line`, palette colour `0x0A`),
  drawn at any angle with a flare at each end, for 5 render frames.
- **Glow:** `C3RAILGLOW` dots every 16 leptons along the core, a soft blue glow fading over 12 frames.
- **Threads:** two lines of `C3RAILTHRD` dots every 12 leptons on sine paths, one wave per 3 cells, swinging out to
  80 leptons by the fourth cell from the muzzle (the second thread at 75% of the first).
- **Muzzle and impact:** `C3RAILMZ` (5 frames) and `C3RAILHIT` (12 frames), round, the impact's sparks thrown all
  round.

`TF_Railgun_Beam` (`anim.cpp`) lays the dots, flash and impact; it returns 75 frames, TS's coil life, which a
railgun (`IsRailgun`) holds before it may fire again, so the Mk. II's rate of fire is TS's. A weapon with a
projectile and `RailBeam=yes` draws the shot as it fires, alongside its (usually `Invisible`) bullet.

A shot lays some 300 anims, so `AnimMax` is at least 2048 (`rules.cpp`).

## Art

`scripts/c3_rail_beam.py` renders the four sets into the C&C3 graphics pack from C&C3's own textures
(`resources/custom-art/c3-railgun-beam/`: `FXRailgunThread`, `FXLenzFlare01`, `FXFireBlast04`). The launcher
blends straight alpha only, so the additive light is baked to RGBA (alpha is the brightest channel). Classic stubs
are in `TFASSETS.MIX` (`build_tfassets.sh`).

## C&C3 values

- `MammothTankRailCannon`: range 300, 2 shots 0.8 s apart, reload 2.7-2.8 s, damage 1200.
  `GDIPredatorTankRailgun`: range 300, 1 shot, reload 1.6 s, damage 572. Both instant, no projectile.
- Core streak: lifetime 25 particle frames, white to black from half its life. Threads: 3 sine bolts, lifetime 30,
  amplitude growing toward the target, white through (32,71,255) to black. Particle frames run at 30 Hz.
- Muzzle `FXLenzFlare01`, lifetime 10, size 15-25. Impact: 8 `FXFireBlast04` glows (lifetime 30, size 20-30,
  shrinking) and 20 short sparks.
- A veteran's shot is red. The heat-shimmer ribbon (`Laser.fx`) only refracts and has no colour; Remastered cannot
  draw it.
