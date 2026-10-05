"""hvrpkg.py - assemble the Hover MLRS package from its finished frames: README (the version, the checks' numbers and the
seat table filled in), previews (the sheets, the GIFs, the shape sheet, the close-ups), src/, the 3D model in its own
folder and zip, and the two zips.

    python3 hvrpkg.py PKG_ROOT version
(PKG_ROOT holds ts-hvr-hd/ with frames/ already rendered.)
"""
import os, sys, shutil, subprocess, zipfile, re
import numpy as np
from PIL import Image, ImageDraw
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
VOX = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, VOX)
SRC = ['rc.py', 'rcrender.py', 'rcexport.py', 'glbtools.py', 'qparts.py', 'hvrmodel.py', 'hvrmat.py', 'hvrcam.py',
       'hvrrender.py', 'renderall.py', 'hvrseat.py', 'hvrspec2.py', 'hvrexport.py', 'glbcheck.py', 'hvcomp.py',
       'hvrclose.py', 'hvrclose2.py', 'hvrlook.py', 'hvox.py', 'vdump.py', 'hcls.py', 'frameio.py', 'paths.py',
       'hvrpkg.py', 'hvrtab.py']
FROM_VOX = ['vdeliver.py', 'vcheck.py']
RENDERER = ['hd.py', 'walls2.py', 'wnoise.py', 'export3d.py', 'vxl.py']
VALIDATE = os.environ.get('VALIDATE', 'validate.js')
PAD_FACINGS = [0, 28, 16, 12]
RACK_FRAMES = [44, 48, 52, 40]
TURN_HULL = 28


def run(cmd, **kw):
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(r.stdout + r.stderr)
    return r.stdout


def zipdir(root, name, out):
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        base = os.path.join(root, name)
        z.write(base, name + '/')
        for dp, dn, fn in os.walk(base):
            dn[:] = sorted(d for d in dn if d != '__pycache__')
            for d in dn:
                z.write(os.path.join(dp, d), os.path.relpath(os.path.join(dp, d), root) + '/')
            for f in sorted(fn):
                z.write(os.path.join(dp, f), os.path.relpath(os.path.join(dp, f), root))


def grid(tiles, labels, out, cols=2):
    import hvrclose as C
    w, h = tiles[0].size
    S = Image.new('RGB', (cols * (w + 6) - 6, ((len(tiles) + cols - 1) // cols) * (h + 6) - 6), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for i, (t, lab) in enumerate(zip(tiles, labels)):
        S.paste(t, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
        d.text(((i % cols) * (w + 6) + 6, (i // cols) * (h + 6) + 4), lab, font=C.FONT, fill=(240, 230, 180))
    S.save(out)


def pair_tile(spec, hd_fmt, f, text):
    """the mod's shadow, hull and rack as they lie on their canvas beside HD's with the rack seated on the pad."""
    from vdeliver import on_bg, layered, label
    crop = spec.CROP
    W, H = crop[2] - crop[0], crop[3] - crop[1]
    t = Image.new('RGB', (2 * W + 6, H + 16), (28, 30, 34))
    for j, (lab, fmt, ks) in enumerate((('in-mod', spec.INMOD, spec.unit(f, False)), ('HD', hd_fmt, spec.unit(f)))):
        t.paste(on_bg(layered(fmt, ks)).crop(crop).convert('RGB'), (j * (W + 6), 16))
        label(t, '%s  %s' % (lab, text), (j * (W + 6) + 4, 2))
    return t


def unit_sheet(spec, fmt, out, scale=0.8, cols=2):
    tiles = [pair_tile(spec, fmt, f, 'facing %d' % f) for f in range(0, 32, 4)]
    tiles = [t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS) for t in tiles]
    Wt, Ht = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    S = Image.new('RGB', (cols * (Wt + 8) + 8, rows * (Ht + 8) + 8), (20, 22, 26))
    for i, t in enumerate(tiles):
        S.paste(t, (8 + (i % cols) * (Wt + 8), 8 + (i // cols) * (Ht + 8)))
    S.save(out)


def unit_gif(spec, fmt, out, scale=1.0, ms=120):
    frames = []
    for f in range(32):
        t = pair_tile(spec, fmt, f, 'facing %d' % f)
        t = t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS)
        frames.append(t.convert('P', palette=Image.ADAPTIVE, colors=255))
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=int(ms), loop=0, disposal=1)


def rack_turn_gif(spec, fmt, out, f=TURN_HULL, z=2, ms=120, crop=(20, 20, 172, 160)):
    """the hull still, the rack turning through its 32 facings on the pad (seated by the hull's facing)."""
    from vdeliver import on_bg, layered, label
    k, dx, dy = spec.seat(f)
    frames = []
    for g in range(32):
        im = on_bg(layered(fmt, [64 + f, f, (32 + g, dx, dy)])).crop(crop)
        im = im.resize((im.width * z, im.height * z), Image.LANCZOS).convert('RGB')
        label(im, 'hull %d  rack %d' % (f, 32 + g), (6, 4))
        frames.append(im.convert('P', palette=Image.ADAPTIVE, colors=255))
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=int(ms), loop=0, disposal=1)


def closeups(pv):
    """the pad between the pontoons (hull and rack together) and the rack's faces, at 5x with the frames' look."""
    import hvrclose as C, hvrclose2 as C2
    grid([C2.assembled(f, 5) for f in PAD_FACINGS], ['hull %d + rack %d' % (f, 32 + f) for f in PAD_FACINGS],
         pv + '/pad-closeup.png')
    grid([C.close(k, 5, 2, (58, 22, 132, 100)) for k in RACK_FRAMES], ['rack %d' % k for k in RACK_FRAMES],
         pv + '/rack-closeup.png')


def seat_table():
    import hvrseat as HS
    rows = []
    for f in range(16):
        cells = []
        for g in (f, f + 16):
            k, dx, dy = HS.seat(g)
            cells.append('facing %2d  %+6.2f %+6.2f  (%+5.2f, %+5.2f)' % (g, dx, dy, dx / 4, dy / 4))
        rows.append('    ' + '      '.join(cells))
    return '\n'.join(rows)


def check_formula():
    """the README's formula against hvrseat."""
    import hvrseat as HS, hvrmodel as T
    for f in range(32):
        a = 2 * np.pi * ((32 - f) % 32) / 32
        ax, ay = -T.SEAT_U[0], T.SEAT_U[1]
        dx = -2.95 * (ax * np.sin(a) + ay * np.cos(a))
        dy = 2.95 * np.sin(np.deg2rad(32)) * (ax * np.cos(a) - ay * np.sin(a))
        k, sx, sy = HS.seat(f)
        assert abs(dx - sx) < 1e-6 and abs(dy - sy) < 1e-6, (f, dx, sx, dy, sy)


if __name__ == '__main__':
    root, ver = sys.argv[1], sys.argv[2]
    pkg = os.path.join(root, 'ts-hvr-hd')
    p3d = os.path.join(root, 'ts-hvr-hd-3d')
    pv = os.path.join(pkg, 'previews')
    os.makedirs(p3d, exist_ok=True)
    os.makedirs(pv, exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs'), exist_ok=True)
    import hvrspec2 as spec
    import vcheck, vdeliver
    import hvrmodel as T
    check_formula()
    fmt = os.path.join(pkg, 'frames', 'tshvr-%04d.png')
    # checks on the finished frames (the hull's overlap with the mod's: the rack's frames are drawn on the pivot now)
    bad, ious = vcheck.check(fmt, spec.INMOD, 96, spec.CANVAS, set(range(0, 64)))
    if bad:
        raise SystemExit('frame problems: %s' % bad[:10])
    final_hull = '%.2f' % np.mean(ious[:32])
    # previews
    unit_sheet(spec, fmt, pv + '/8-facings.png')
    for name, items in spec.SHEETS:
        vdeliver.sheet(spec, fmt, items, pv + '/' + name)
    unit_gif(spec, fmt, pv + '/turn.gif', scale=0.7)
    rack_turn_gif(spec, fmt, pv + '/rack-turn.gif')
    name, items = spec.LINEUP
    vdeliver.lineup(spec, fmt, items, pv + '/' + name)
    print('sheets and gifs done', flush=True)
    import hvcomp
    out = run([sys.executable, 'hvcomp.py', 'ext', ','.join(str(k) for k in list(range(0, 32, 4)) + list(range(32, 64, 4)))])
    ov = [float(x) for x in re.findall(r'overlap ([0-9.]+)', out)]
    shape_hull, shape_rack = '%.2f' % np.mean(ov[:8]), '%.2f' % np.mean(ov[8:16])
    hvcomp.diff(pv + '/shape-8-facings.png', [4, 12, 20, 28, 36, 44, 52, 60], 3, crop=(30, 22, 162, 162))
    closeups(pv)
    print('shape and close-ups done', flush=True)
    # the 3D model, checked through its camera over hull frame 24 with rack frame 56 seated, and by Khronos's validator
    glb = os.path.join(p3d, 'tshvr.glb')
    run([sys.executable, 'hvrexport.py', glb])
    from vdeliver import layered
    seated = os.path.join(HERE, 'logs', 'seated24.png')
    layered(fmt, [24, spec.seat(24)]).save(seated)
    g = run([sys.executable, 'glbcheck.py', glb, seated, os.path.join(HERE, 'logs', 'glbcheck.png'), '192'])
    glb_ov = g.strip().split()[-1]
    val = subprocess.run(['node', VALIDATE, glb], capture_output=True, text=True).stdout.strip().splitlines()[0]
    val = val.replace(' warnings', ', warnings').replace(' infos', ', infos').replace(' hints', ', hints')
    # README
    upc = 96.0 / 2.95
    cells = '%.3f cell aft, %.4f cell left' % (-T.SEAT_U[0] / upc, T.SEAT_U[1] / upc)
    txt = open(os.path.join(HERE, 'README_v2.txt')).read()
    txt = (txt.replace('VERSION', ver).replace('SHAPE_HULL', shape_hull).replace('SHAPE_RACK', shape_rack)
           .replace('FINAL_HULL', final_hull).replace('GLB_OVERLAP', glb_ov).replace('GLB_VALIDATOR', val)
           .replace('SEAT_TABLE', seat_table()).replace('SEAT_CELLS', cells))
    head = txt.splitlines()[0]
    txt = head + '\n' + '=' * len(head) + '\n' + '\n'.join(txt.splitlines()[2:]) + '\n'
    open(os.path.join(pkg, 'README.txt'), 'w').write(txt)
    i0 = txt.index('3D model (ts-hvr-hd-3d/tshvr.glb)'); i1 = txt.index('Judgement calls')
    t3 = 'ts-hvr-hd-3d: the 3D model of ts-hvr-hd (%s)' % ver
    open(os.path.join(p3d, 'README.txt'), 'w').write(t3 + '\n' + '=' * len(t3) + '\n\n' + txt[i0:i1].rstrip() + '\n')
    # src (the absolute paths to the shared scripts taken out: they sit next to the unit's own in src/)
    src = os.path.join(pkg, 'src')
    if os.path.isdir(src):
        shutil.rmtree(src)
    os.makedirs(src)
    for f in SRC:
        shutil.copy(os.path.join(HERE, f), src)
    for f in FROM_VOX:
        shutil.copy(os.path.join(VOX, f), src)
    for f in RENDERER:
        shutil.copy(os.path.join(HANDOFF, 'renderer', f), src)
    for f in os.listdir(src):
        p = os.path.join(src, f)
        s = open(p).read()
        s2 = s.replace("sys.path.insert(0, '/home/claude/units/work/vox')\n", '')
        s2 = s2.replace("os.environ.get('V1_FRAMES', 'v1/frames') + '/tshvr-%04d.png'",
                        "os.environ.get('V1_FRAMES', 'v1/frames') + '/tshvr-%04d.png'")
        s2 = s2.replace("os.environ.get('REVIEW', 'units-review')", "os.environ.get('REVIEW', 'units-review')")
        s2 = s2.replace("os.environ.get('REVIEW', 'units-review') + '/'", "os.environ.get('REVIEW', 'units-review') + '/'")
        s2 = s2.replace("VOX = os.path.dirname(os.path.abspath(__file__))", "VOX = os.path.dirname(os.path.abspath(__file__))")
        s2 = s2.replace("VALIDATE = os.environ.get('VALIDATE', 'validate.js')",
                        "VALIDATE = os.environ.get('VALIDATE', 'validate.js')")
        for qt in ('"', "'"):
            s2 = s2.replace('sys.path.insert(0, %s/home/claude/units/ts-units-hd-handoff/renderer%s)' % (qt, qt),
                            'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))')
        if s2 != s:
            if not re.search(r'^import (os|os, sys|sys, os)\b', s2, re.M) and 'os.' in s2:
                if re.search(r'^import sys\n', s2, re.M):
                    s2 = re.sub(r'^import sys\n', 'import os, sys\n', s2, count=1, flags=re.M)
                else:
                    s2 = re.sub(r'^(import [^\n]+\n)', r'import os\n\1', s2, count=1, flags=re.M)
            open(p, 'w').write(s2)
    left = [f for f in os.listdir(src) if '/home/claude' in open(os.path.join(src, f)).read()]
    print('src files still naming /home/claude:', left)
    # zips
    for name in ('ts-hvr-hd', 'ts-hvr-hd-3d'):
        out = os.path.join(root, name + '.zip')
        if os.path.exists(out):
            os.remove(out)
        zipdir(root, name, out)
        print(name + '.zip', '%.1f MB' % (os.path.getsize(out) / 1e6))
    print('shape hull', shape_hull, 'rack', shape_rack, 'final hull', final_hull, 'glb', glb_ov, val)
