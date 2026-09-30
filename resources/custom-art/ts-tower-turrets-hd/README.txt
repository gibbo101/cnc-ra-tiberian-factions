TS GDI Component Tower turrets rebuilt for Red Alert Remastered (HD):
Vulcan (GTCTWR_B), RPG (GTCTWR_C) and SAM (GTCTWR_D). Each frame drops straight onto the HD component tower.

CANVAS   every frame is 176x320, transparent, straight alpha: the turret ALONE, drawn in place on the tower's
         canvas (the tower's cell is x 24-152, y 96-224, its ground centre (88, 160)). No offset.
TURNS    about the tower's middle: x 88.0 (87.5 counting pixel centres), through the in-mod pivot, y 83.7
         (83.2). Each sits down in the green ring with the ring's front rim showing, as now.
         (The in-mod sprites actually turned about a point 1-2 px right of the tower's middle; these are centred.)
FACINGS  turret-00 .. turret-31: 0 points north (up the screen), each next frame 11.25 degrees counter-
         clockwise (8 west, 16 south, 24 east), matching in-mod frame for frame - including where each facing
         lands on screen (TS's facings, carried through the camera change).
CAMERA   the tower's: orthographic, 32 degrees above the ground, looking north; the tower's light, material
         shading, ~75% baked shadow and outline. The tower is in the scene when a turret is rendered, so the
         ring hides the turret's foot where it should, and the turret's shadow on the tower's top and braces is
         baked into the turret frame (semi-transparent black). Past the tower, on the ground, it only adds what
         the tower frame's own shadow doesn't already cover.
SIZE     as in-mod (TS's own proportions: about three quarters of the tower's width, the Vulcan's barrels and
         the RPG's ammo box reaching past it).
COLOUR   house colour is pure green, only where TS has it: the Vulcan's two ammo drums, the RPG's ammo box, the
         SAM's collar under its radar plate. *-trim.png marks it (white = house colour) if you'd rather use a mask.
PLUG     the RPG and SAM stand on a khaki turntable that fills the ring, so the tower's grey top never shows
         round them (the Vulcan's body already covers it).

EACH TURRET FOLDER
  turret-NN.png                   healthy - for the healthy tower (component-tower-00)
  turret-damaged-NN.png           RA's damaged state - for the damaged tower (component-tower-01): soot, scorch,
                                  cracks, dust and chips knocked out of the edges, greys and browns only; the
                                  green parts stay green (only darkened)
  vulcan only:
  turret-recoil-NN.png            the barrels 4 px back, for the shot
  turret-damaged-recoil-NN.png    the same, damaged
  *-trim.png                      house-colour masks
  Vulcan 32 x 4 = 128 frames, RPG and SAM 32 x 2 = 64 - within the 128 a set can hold.

AIM POINTS  aim-points.txt (and aim-<turret>-<state>.json): canvas coordinates of the points the mod shoots
            from, per frame, measured off the models (pixel-edge coordinates: subtract 0.5 for pixel centres)
    Vulcan  the two muzzles, left then right barrel (recoil frames: 4 px further back)
    RPG     the launcher's two tube mouths, lower then upper (the launcher is the outer block; it fires)
    SAM     the middle of the launch face, then its eight cells (lower row left to right, then the upper
            row; left and right as the turret sees them)
  They are not where they were on the in-mod art: the new models match TS's silhouettes, not the scaled
  sprites' pixels, so take them from this table.

HOW THEY WERE MADE
  Each turret is a 3D model fitted to TS's 32 facings (the model is projected with TS's own camera and
  its outline and colour regions scored against the sprites; silhouette match: Vulcan 89%, RPG 93%,
  SAM 89%), then rendered with the tower's camera.
    Vulcan  a khaki gun box, twin Gatlings (six barrels round a spindle, clamp bands, a housing each) and two
            green ammo drums on its flanks
    RPG     three blocks side by side on a turntable: the launcher (outer), tilted up about 11 degrees on a
            trunnion with a rust-rimmed hub, two stacked tubes (bored mouths with steel lips, scorched rear
            ends); the targeting sensor (middle), level, a glass lens in its front; the green ammo box (right)
            on two struts
    SAM     a low khaki missile box on trunnions: a short upright strip at the front, then the launch face, a
            shallow slope about 54 degrees back from upright (2 rows of 4 cells, a missile nose in each); the
            top falls gently to a short back with four vents; set back and to the left on the top, a green
            collar carrying a flat, slotted grey radar plate

previews/   every facing on the tower (like in-mod's sheets): healthy, damaged, Vulcan recoil; HD beside
            in-mod; a spin GIF; the aim points marked
src/        Python 3 (numpy, scipy, Pillow). src/turrets/: tsdf.py (the models and ray-marcher), tren.py (the
            renderer), tfit.py (the fit to TS's facings), vulcan.py / rpg.py / sam.py (the models, their fitted
            numbers in *-fit*.json), tdamage.py, render_turret.py, tpreview.py; the tower's renderer one level up.
              cd src/turrets && python3 render_turret.py vulcan healthy   (| damaged | recoil | damaged-recoil)
              python3 tpreview.py vulcan
