"""Package spec for the Dropship Bay (bdeliver.py): the Service Depot's pad alone."""
HAND = '/home/claude/work/ts/ts-buildings-hd-handoff/11-TSDROP'


def readme():
    return """Tiberian Sun Dropship Bay (Westwood's cut GADROP; TSDROP in the mod) for Red Alert Remastered (HD).

TS has no art for it: in the mod it is the Service Depot's octagonal pad alone (GTDEPTBB), a landing pad for the Orca
dropship. This is the pad of my Service Depot model (one model, the same renderer, materials, light, shadow and outline
as the other buildings), on its own. No logo on it: TS's pad has none, and the mod's current one carries GDI's eagle,
which I don't draw. It keeps TS's pad as it is: the house-green band, the lavender-grey concrete with two steel gratings
along one side and guide lines of small lamps, the tan rim, the sloped sides.

ts-angle/  TS's own camera, lit from TS's side. CANVAS 768x512: the canvas, scale and place the bay has in the mod now
           (TS's frame x10.47, TS px (0, 0) at canvas (-360, -923), fitted to in-mod/tsdrop-0000.png, IoU 0.95: the
           mod's pad is drawn 2.36 times the depot's scale and fills the canvas's width; so does this one, its east and
           west tips touching the canvas's edges as the mod's do).
ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north), at the model's
           true size (the pad is 2.1 cells across), turned as the depot's RA frames are (the gratings at the back) and
           centred on the 3x3 plot: CANVAS 768x512, the plot x 192-576, y 64-448.
COLOUR     Green = house colour: the band. Exactly the yard's green. Every frame has a -trim.png (white = house colour,
           antialiased).

building/dropbay-00, -01        the pad, healthy and damaged (the mod's TSDROP.ZIP: 2 frames). Damaged as the depot's
                                pad: cracked all over, a blast in its north-east quarter (its slabs broken, sunk and
                                tilted, scorched, rubble on them), a smaller scorch on the gratings, two corners
                                knocked off. Greys and browns only.
build-up/dropbay-build-00..18   19 frames (the mod's TSDROPMAKE.ZIP has 19): the pad's part of GTDEPTMK, the depot's
                                build-up: laid from its south-west side across to the north-east in plain grey (00-10),
                                held (11-13), coloured with its band painted (14); 18 is the finished bay.

previews/  the bay on its own; both states next to TS's GTDEPTBB; the mod's frames (tsdrop-0000, tsdropmake-0018) next to
           the same HD frames; next to the Construction Yard, the Power Plant, the Component Tower and a GDI wall run (RA
           grid); the house colour next to the yard's; the build-up as a strip and a GIF against GTDEPTMK.
3d/        dropship-bay.glb (glTF 2.0 .glb): "pad" / "pad-damaged", marker "pad-centre", cameras "camera-ts-angle"
           (768x512) and "camera-ra-grid" (768x512). In TS's frame: x east, y up, z south; 1.0 = one cell = 128 px on the
           RA grid; origin the foundation's centre on the ground (TS's pad is centred 12.25 units south-east of it; the
           RA grid frames centre the pad on the plot). COLOR_0 = the materials' colours, COLOR_1 = house colour.
src/       Python 3. dept.py (the model; the bay is its pad: scene(pad=True)), deptmat.py, deptdamage.py, deptbuild.py,
           droprender.py (the bay's views), dropfinal.py (its frames), deptexport.py, dropspec.py.
             python3 dropfinal.py states|build iso|ra [ss]   the frames (ss 4 used)

My calls (made overnight; each easy to change):
  - The pad as TS draws it, no logo and no new markings: the depot's band, gratings and guide lines.
  - The TS-angle frames keep the mod's 2.36x scale; the RA grid frames keep the model's true size (the 3x3 plot holds
    it with room round it).
  - RA grid turned like the depot's, and centred.
"""


SPEC = dict(
    name='dropbay', title='Dropship Bay', pkg='/home/claude/work/out/ts-dropship-bay-hd', hand=HAND,
    ts='GTDEPTBB', ts_mk='GTDEPTMK', K=10.47, O=(-360.0, -923.0), iso_size=(768, 512), ra_size=(768, 512), ra_head=64,
    ra_left=192, cells=(3, 3), state_dir='building',
    overlays=[],
    loop=None,
    inmod=[('tsdrop-0000.png', 0, 0, ('building', 'dropbay-00')),
           ('tsdropmake-0018.png', 0, 0, ('build-up', 'dropbay-build-18'))],
    build_n=19, ts_mk_n=10, idle_n=1, idle_label='the pad (no overlays)', idle_ms=110,
    crop={'iso': (0, 0, 768, 450), 'ra': (176, 140, 592, 450)},
    zoom=0.75, green_zoom=0.75, gif_zoom=0.6, strip_w=200,
    extra_previews=[],
    src=['hd.py', 'walls2.py', 'wnoise.py', 'brender.py', 'pfinal.py', 'pdamage.py', 'export3d.py', 'bdeliver.py',
         'ypreview.py', 'weapdamage.py', 'weap.py', 'tsgeo.py', 'cleanalpha.py', 'radr.py',
         'dept.py', 'deptmat.py', 'deptdamage.py', 'deptbuild.py', 'droprender.py', 'dropfinal.py', 'deptexport.py',
         'dropspec.py', 'deptgeo.py'],
    readme=readme,
)
