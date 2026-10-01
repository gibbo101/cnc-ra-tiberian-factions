"""3D models (.glb, export3d.py) of the buildings made before the refinery, healthy and damaged, in each one's own
frame (origin = its foundation's centre on the ground; x east, y up, z south; 1.0 = one cell):

    python3 export_all.py [names...]      barracks silo tech plant yard (default: all)"""
import os, sys, time
import numpy as np
import export3d as E

OUT = os.environ.get('OUT3D', '/home/claude/work/out/3d-models')
FILES = dict(barracks='barracks', silo='silo', tech='tech-center', plant='power-plant', yard='construction-yard')


def job(name):
    if name == 'barracks':
        import pile as M, pilemat as MM, piledamage as MD
        return dict(title='Barracks (GAPILE)', canvas=(256, 256, 60.2), parts=[('barracks', M.scene, {}, None, 0), ('barracks-damaged', MD.model(1), {}, MD, 1)],
                    mats=MM, xr=(-200, 200), yr=(-200, 200), zmax=240, foundation='2 x 2', mat_kw={}, h=1.0)
    if name == 'silo':
        import silo as M, silomat as MM, silodamage as MD
        mk = dict(layout='ra')
        return dict(title='Tiberium Silo (GASILO)', canvas=(256, 256, 60.2), parts=[('silo', M.scene, mk, None, 0), ('silo-damaged', MD.model(1), mk, MD, 1)],
                    mats=MM, xr=(-180, 180), yr=(-180, 180), zmax=120, foundation='2 x 2', mat_kw={})
    if name == 'tech':
        import tech as M, techmat as MM, techdamage as MD
        rot, ts = dict(layout='rot'), dict(layout='ts')
        return dict(title='Tech Center (GATECH)', canvas=(256, 512, 90.25), parts=[('tech-center', M.scene, rot, None, 0),
                                                         ('tech-center-damaged', MD.model(1), rot, MD, 1)],
                    mats=MM, xr=(-200, 200), yr=(-260, 260), zmax=240, foundation='2 x 3 (turned for the RA grid)',
                    mat_kw={})
    if name == 'plant':
        import powr as M, pmat as MM, pdamage as MD
        return dict(title='Power Plant (GAPOWR)', canvas=(256, 272, 60.2), parts=[('power-plant', M.scene, dict(turbines=(0,)), None, 0),
                                                         ('power-plant-3-pods', M.scene, dict(turbines=(0, 1, 2)), None, 0),
                                                         ('power-plant-damaged', MD.model(1), dict(turbines=(0,)), MD, 1)],
                    mats=MM, xr=(-170, 170), yr=(-170, 170), zmax=200, foundation='2 x 2', mat_kw={})
    if name == 'yard':
        import yard as M, ymat as MM, ydamage as MD
        return dict(title='Construction Yard (GACNST)', canvas=(384, 360, 26.3), parts=[('construction-yard', M.scene, {}, None, 0),
                                                               ('construction-yard-damaged', MD.model(1), {}, MD, 1)],
                    mats=MM, xr=(-200, 200), yr=(-200, 200), zmax=200, foundation='3 x 2', mat_kw={})
    raise KeyError(name)


def export(name, h=2.0):
    j = job(name)
    h = j.get('h', h)                       # finer where thin masts and poles would vanish (the barracks)
    g = E.GLB()
    for (part, fn, mk, dmg, level) in j['parts']:
        t0 = time.time()
        v, f, n, rgb, house = E.build_part(fn, j['mats'], j['xr'], j['yr'], h, j['zmax'], mk, damage=dmg, level=level,
                                           mat_kw=j['mat_kw'])
        g.mesh(part, v, f, n, rgb, house)
        print(name, part, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    W, Hc, up_px = j['canvas']
    up_ra = np.array([0.0, np.cos(np.radians(32)), -np.sin(np.radians(32))])
    g.camera('camera-ra-grid', 0.0, 32.0, up_ra * (up_px / 128.0), W / 2 / 128.0, Hc / 2 / 128.0,
             extras=dict(note=f'RA grid: orthographic, 32 degrees, looking north; render {W} x {Hc} px = the ra-grid frames'))
    up_ts = np.array([-0.3536, 0.8660, -0.3536])
    g.camera('camera-ts-angle', 315.0, 30.0, up_ts * 0.45, W / 2 / 128.0 * 1.15, Hc / 2 / 128.0 * 1.15,
             extras=dict(note='TS angle: orthographic, 30 degrees, looking north-west (the angle; frame to taste)'))
    g.save(f'{OUT}/{FILES[name]}.glb', extras=dict(title=j['title'], foundation=j['foundation'],
                                            units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the foundation centre on the ground'))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:] or ['barracks', 'silo', 'tech', 'plant', 'yard']
    for nm in names:
        try:
            export(nm)
        except Exception as e:
            import traceback; traceback.print_exc()
            print('FAILED', nm, e, flush=True)
