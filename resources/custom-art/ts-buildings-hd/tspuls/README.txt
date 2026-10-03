Tiberian Sun EMP Pulse Cannon (NAPULS; TSPULS / TSPULST in the mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (NAPULS, NAPULSMK, NAPULS_A), rendered two ways with the same renderer as the
Construction Yard, Power Plant, Barracks, Silo, Tech Center, Refinery, War Factory, Radar, Helipad, Service Depot,
Sensor Array, Component Tower and Upgrade Center: same materials, light, shadow (baked in at ~75% black) and outline.
TS draws it in the snow theatre (snow on its ridges); the mod's art has none, so neither has this.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite. CANVAS 256x256: the canvas, scale and place
           the cannon has in the mod now (TS's frame x3.475, TS px (0, 0) at canvas (-44, -51), fitted to
           in-mod/tspuls-0000.png). Drops in over the current frames.
ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north), TS's way round.
           CANVAS 256x320: the mod's 256x256 grown 32 px top and bottom so the head fits; the 2x2 plot is y 32-288,
           centred, the foundation's south edge on the plot's.
COLOUR     Green = house colour: the drum the head turns on and the small lamp at its foot. Exactly the yard's green.
           Every frame has a -trim.png (white = house colour, antialiased).

What it is (read from TS's frames; NAPULSMK shows it go up):
  base       a squat concrete star: four sloping arms (gabled, a narrow strip along each ridge) out to near the
             foundation's corners, turned a little off the diagonals, over a low cone; poured in courses, panel seams
             across the arms, radial seams on the cone
  collar     a cast ring round the top of the cone, bolted, the drum standing in it
  drum       the turntable: a house-green drum; a small house-green lamp on the cone at its foot (front left)
  head       NAPULS_A: the EMP cannon turning on the drum (v2, rebuilt from TS's 32 facings with Luke's two
             reference renders): a box body with a light-grey top, dark sides and a light back, its front top cut back;
             a short barrel out of its front with two coil rings and a muzzle (a dark bore with a pale ring at the back:
             TS's light ring on the head's front); two slanted dark yoke plates from the drum up the body's sides, a
             round light trunnion boss on each; a dark round tank under the body; two cables looping off the back down
             to the drum; hazard stripes low on each side. Raised 15 degrees, as in the references. TS's firing frames
             (NAPULS_A 32-55) show the discharge at the muzzle end, so that end is its front.

Each view has the same folders. Every frame is on the view's full canvas, in place, with a -trim.png.

building/pulse-cannon-00, -01     healthy and damaged (TS's NAPULS 0 and 1; RA has no destroyed state), without the
                                  head (it is its own set). Damaged, as TS breaks it: chunks bitten out of the arms'
                                  ridges and ends (rough broken concrete inside), cracks, soot, rubble chunks of the same
                                  concrete round the foot to the left, front and right. The drum is whole.
head/pulse-cannon-head-00..31     the head at NAPULS_A's 32 facings (00 north, turning anticlockwise: 08 west, 16 south,
                                  24 east), each cut against the healthy building (its shadow on the building
                                  included), like the mod's TSPULST.ZIP. One set over both states, as TS's.
build-up/pulse-cannon-build-00..23
                                  24 frames in NAPULSMK's order (TS draws 20, the mod's TSPULSMAKE.ZIP has 13: take
                                  every other frame, or play all 24): the collar grows round as an arc from its back and
                                  rises (00-04), the cone comes up round it with the crater inside (04-08), the drum
                                  rises out of the crater (07-10), the four arms rise out of the ground (10-19; TS's snow
                                  goes on over its frames 13-18), the lamp (21). 23 = the healthy building, no head.

Stacking: building, then head/ (any facing).

previews/  the building on its own; both states next to TS's; the build-up as a strip and a GIF against NAPULSMK; the
           head turning against TS's; next to the Construction Yard, the Power Plant, the Component Tower and a GDI
           wall run (RA grid); the house colour next to the yard's.
src/       Python 3 (numpy, scipy, Pillow). hd.py is the renderer, brender.py the views. puls.py (the model, its
           build-up controls), pulsmat.py (materials), pulsdamage.py, pulsbuild.py (NAPULSMK's order), pulsrender.py
           (views), pulsfinal.py (frames), pulsspec.py; plug.py / plugs.py are the Upgrade Center's model (the head's
           parts are packed into slabs with its packer).
             python3 pulsfinal.py states|head|build iso|ra [ss]   the frames (ss 4 used)

My calls (each easy to change):
  - No snow (the mod's art has none); TS's snow frames in the build-up are given to the arms rising.
  - The head's shape and size are read from NAPULS_A's 32 facings at 20 px tall (its outline matches TS's to ~0.84
    of the pixels over all 32); the details (coil rings, bore, bosses, stripes, panel lines) follow Luke's references.
  - The barrel and body are raised 15 degrees about the trunnions, as in both references; TS's own idle facings have
    it level (puls.py CANNON tilt = 0 puts it back).
  - TS's other NAPULS_A frames (32-55: a discharge with the barrel recoiling, at 8 facings; 56-60: the barrel pitching
    down) are not made: the mod uses the 32 facings only.
