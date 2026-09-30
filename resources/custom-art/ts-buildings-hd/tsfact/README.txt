Tiberian Sun GDI Construction Yard (GACNST, TSFACT in the mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTCNST), rendered two ways with the Component Tower's renderer:
same materials, light, shadow (baked in at ~75% black) and outline.

ts-angle/  TS's own camera (30 degrees, looking north-west), lit from TS's side so it reads like the sprite.
           CANVAS 384x256, the same canvas, scale and place as the building in the mod now
           (in-mod/tsfact-0000.png: TS's frame x3). Drops in over the current frames.
ra-grid/   Turned to sit on RA's square grid: an orthographic camera 32 degrees above the ground, looking
           north (the tower's and the walls' camera). The arch faces south (the camera), the window box east.
           CANVAS 384x360: the 256 px of the plot plus 52 px top and bottom. The 3x2 plot is x 0-384,
           y 52-308, so its centre is the canvas centre (192, 180) and the game's centre-on-plot anchoring
           puts it right. The pad's south edge sits on the plot's south edge; the vault rises into the
           headroom above, and everything (shadow too) stays inside the canvas.
COLOUR     Green = house colour, kept green. Every frame has a -trim.png (white = house colour, antialiased),
           the same as the tower's.

Each view has the same folders:

yard/construction-yard-00.png      healthy
yard/construction-yard-01.png      damaged: the window box's coping smashed, the two north fans blown out,
                                   dents and holes in the cladding, torn panels, scorch, debris on the pad.
                                   Greys and browns only. No destroyed frame: RA has healthy and damaged only.

build-up/construction-yard-build-00..31.png
    32 frames (TSFACTMAKE.ZIP's count), in the order TS's GTCNSTMK builds it: the MCV (00); the pad spreads
    out from it and the foot rail slides out along the west edge (01-10); the ribs grow from the west foot
    up and over (09-14); the east half is clad from the north end (13-19); the panels and fans go in
    (18-22; the roof lamps come on at 20, as in TS, and the door lamp at 22); the MCV folds into the
    crane's base and the boom swings up (23-27); the window box and the stacks rise (27-30).
    31 is the finished building (exactly construction-yard-00).

Animation overlays: TS's four, frame for frame. Each is drawn on top of the building frame of the same state,
on the same canvas, and holds only the pixels it changes. TS's shadow frames are left out.
  A-fans/construction-yard-fans-00..19             GTCNST_A: the three roof fans turning (10-frame loop).
                                                   00-09 healthy, 10-19 damaged (only the south fan
                                                   still turns, as in TS).
  B-door-lamp/construction-yard-door-lamp-00..19   GTCNST_B: the door lamp (a small yellow lamp, its two
                                                   pale beams turning in the wall's plane, 18 degrees a
                                                   frame) and the light running along the threshold strip
                                                   from the door end to the arch's west foot (frames
                                                   05-08), with a small cool marker light at the west
                                                   foot. 00-09 healthy, 10-19 the same on the damaged
                                                   building (TS has one set, so you can use 00-09 for both).
  C-roof-lamps/construction-yard-roof-lamps-00..29 GTCNST_C: the seven roof lamps. A dimming pulse runs
                                                   from north to south, then they all stay on (15-frame
                                                   loop). 00-14 healthy, 15-29 damaged (three lamps dead).
  D-producing/construction-yard-producing-00..19   GTCNST_D: producing. The hangar lights up inside, the
                                                   claw builds a crate on the floor and sets it out on the
                                                   apron, then the lights go down. The roof stays shut, as
                                                   in TS. One set, like TS's.
  Draw order: the building, then A, B and C (they don't overlap each other). D covers the doorway where
  B draws, so while D plays leave B off, or draw D last.

loop/construction-yard-loop-00..59.png
    The idle overlays already baked into the building, laid out like TSFACT.ZIP's 60 frames: 00-29 healthy,
    30-59 damaged. A, B and C together loop every 30 frames (10 and 15). Use these instead of the A/B/C
    overlays if you bake the idle animation into the building frames.

previews/  the yard on its own; both states next to TS's; in the mod's canvas now vs HD; next to the
           Component Tower and a GDI wall run; the build-up as a strip and a GIF against GTCNSTMK; the idle
           loop (healthy and damaged) and producing against TS's own animations. The GIFs are built from
           this package's frames and overlays, drawn the way the game draws them.
src/       Python 3 (numpy, scipy, Pillow). hd.py is the renderer (generalised from the tower's ct_ra.py;
           walls2.py gives the light and materials). yard.py is the model, ymat.py the materials,
           ydamage.py the damage, yanim.py the animations, ybuild.py the build-up.
           python3 yfinal.py states|prod|build iso|ra [ss]   makes the frames (ss 4 = supersampling used here)
           python3 ydeliver.py previews                       makes the previews
