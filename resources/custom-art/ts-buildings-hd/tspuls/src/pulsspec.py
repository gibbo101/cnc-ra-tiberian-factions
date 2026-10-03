"""Package spec for the EMP Pulse Cannon (bdeliver.py)."""
import pulsrender as RR

HAND = '/home/claude/work/ts/ts-buildings-hd-handoff/13-TSPULS'
PKG = '/home/claude/work/out/ts-pulse-cannon-hd'


def readme():
    return open('/home/claude/work/r/pulsreadme.txt').read()


SPEC = dict(
    name='pulse-cannon', title='EMP Pulse Cannon', pkg=PKG, hand=HAND,
    ts='NAPULS', K=RR.ISO_K, O=RR.ISO_O, iso_size=RR.CANVAS['iso'], ra_size=RR.CANVAS['ra'], ra_head=RR.HEAD, ra_left=0,
    cells=(2, 2), state_dir='building',
    # the head turning through its 32 facings: one set over both states, as TS's NAPULS_A and the mod's TSPULST.ZIP
    overlays=[dict(folder='head', prefix='head', n=32, shared=True, ts_shp='NAPULS_A', ts_frame=lambda t, lv: t % 32)],
    loop=None,
    inmod=[('tspuls-0000.png', 0, 0, ('building', 'pulse-cannon-00')),
           ('tspulsmake-0012.png', 0, 0, ('build-up', 'pulse-cannon-build-23'))],
    build_n=24, ts_mk_n=20, ts_mk='NAPULSMK', idle_n=32, idle_label='building + head turning (NAPULS_A 00-31)',
    idle_ms=90,
    crop={'iso': (0, 40, 256, 256), 'ra': (0, 0) + tuple(RR.CANVAS['ra'])},
    zoom=2.0, green_zoom=2.0, gif_zoom=1.5, strip_w=150,
    extra_previews=[],
    src=['hd.py', 'walls2.py', 'wnoise.py', 'brender.py', 'pfinal.py', 'pdamage.py', 'bdeliver.py', 'ypreview.py',
         'weapdamage.py', 'weap.py', 'weapplace.py', 'tsgeo.py', 'cleanalpha.py', 'radr.py', 'dept.py',
         'puls.py', 'pulsmat.py', 'pulsdamage.py', 'pulsbuild.py', 'pulsrender.py', 'pulsfinal.py', 'pulsspec.py',
         'pulsplace.py', 'export3d.py', 'pulsexport.py', 'plug.py', 'plugs.py'],
    readme=readme,
)
