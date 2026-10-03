"""Put the print-ready STL files (stlprint.py) in with each package's .glb: a README in each 3d/stl/ folder, then the
package's 3D zip again (<name>-3d.zip with 3d/ and 3d/stl/, split into -3d.zip and -3d-stl.zip if over 29.5 MiB).

    python3 stlpack.py [package dirs...]   (default: every package with a 3d/stl/ folder, and the GDI 3d-models)"""
import os, sys, glob, zipfile
import trimesh
import stlprint as SP

OUT = '/home/claude/work/out'
LIMIT = 29.5 * 2 ** 20


def readme(stl_dir, title):
    rows = []
    for f in sorted(glob.glob(f'{stl_dir}/*.stl')):
        m = trimesh.load(f)
        ok = m.is_watertight and m.is_winding_consistent and m.volume > 0
        ex = m.extents
        rows.append(f"  {os.path.basename(f):42s} {ex[0]:6.1f} x {ex[1]:6.1f} x {ex[2]:5.1f} mm  {len(m.faces):7d} triangles  "
                    f"{m.body_count} piece{'s' if m.body_count > 1 else ' '}  {'watertight' if ok else 'CHECK'}")
    txt = f"""{title}: print-ready STL files (for 3D printing), one per mesh of the .glb next to this folder, made from the
same model (not converted from the .glb's surface).

Scale     millimetres, 1 cell = {SP.MM_PER_CELL:g} mm (a 2x2 building is about {2 * SP.MM_PER_CELL:g} mm across). Scale it in your slicer as
          you like; thin parts were thickened for this size or bigger (see Thin parts).
Axes      Z up, the base flat on Z = 0 (it sits on the bed as it is); X east, Y north, as the building sits on the RA
          grid.
Solid     each file is one closed, watertight, manifold solid (checked: no holes, consistent winding, a positive
          volume): every part fused into one body, no faces inside, nothing self-intersecting.
Thin parts  anything thinner than {SP.MIN_FEATURE_MM:g} mm (railings, cables, aerials, a door's sheet, thin fins) is thickened to
          about that (FDM with a 0.4 mm nozzle prints it; resin manages finer, so print bigger rather than smaller).
          Plates lying on the bed (bibs, pads) are at least {SP.FLOOR_MM:g} mm thick.
Specks    loose rubble bits under {SP.MIN_ISLAND_MM3:g} mm3, and small bits floating off the bed, are left out (they would not
          print); bigger rubble chunks of the damaged versions stay as separate pieces on the bed.
Parts     the separate meshes (a door, a bib, the plugs, a dome on its arm...) print on their own and glue in place;
          each is dropped onto the bed (Z = 0), and keeps its X / Y place in the building.
Supports  overhangs (domes, arms, roofs, the undersides of lids) need your slicer's supports; the bases need none.
Detail    sampled at 0.25 mm and reduced to at most {SP.MAX_TRIS // 1000}k triangles a file (quadric decimation, re-checked).

Files:
""" + '\n'.join(rows) + '\n'
    open(f'{stl_dir}/README-stl.txt', 'w').write(txt)
    return all('CHECK' not in r for r in rows)


def zsize(f):
    import io
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(f, os.path.basename(f))
    return len(b.getvalue())


def write_zip(path, files, rel):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, os.path.relpath(f, rel))
    print(os.path.basename(path), '%.1f MiB' % (os.path.getsize(path) / 2 ** 20), flush=True)
    return path


def pack(stem, files, rel):
    """<stem>.zip with everything if it fits; else <stem>.zip without the STLs and <stem>-stl[-k].zip with them, each
    under the limit."""
    base = os.path.dirname(stem)
    for old in glob.glob(f'{stem}.zip') + glob.glob(f'{stem}-stl*.zip'):
        os.remove(old)
    sizes = {f: zsize(f) for f in files}
    if sum(sizes.values()) < LIMIT:
        return [write_zip(f'{stem}.zip', files, rel)]
    rest = [f for f in files if '/stl/' not in f]
    stl = [f for f in files if '/stl/' in f]
    outs = [write_zip(f'{stem}.zip', rest, rel)]
    groups, cur, tot = [], [], 0
    for f in stl:
        if cur and tot + sizes[f] > LIMIT * 0.97:
            groups.append(cur); cur, tot = [], 0
        cur.append(f); tot += sizes[f]
    if cur:
        groups.append(cur)
    for k, g in enumerate(groups):
        outs.append(write_zip(f'{stem}-stl.zip' if len(groups) == 1 else f'{stem}-stl-{k + 1}.zip', g, rel))
    return outs


def zip_3d(pkg):
    base, name = os.path.dirname(pkg), os.path.basename(pkg)
    for old in glob.glob(f'{base}/{name}-3d-stl*.zip'):
        os.remove(old)
    d3 = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(f'{pkg}/3d') for f in fs)
    return pack(f'{base}/{name}-3d', d3, base)


def zip_gdi():
    src = f'{OUT}/3d-models'
    files = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(src) for f in fs)
    return pack(f'{OUT}/ts-gdi-3d-models', files, OUT)


if __name__ == '__main__':
    pkgs = sys.argv[1:] or sorted(os.path.dirname(os.path.dirname(d)) for d in glob.glob(f'{OUT}/*/3d/stl') if '3d-models' not in d)
    allz = []
    for p in pkgs:
        ok = readme(f'{p}/3d/stl', os.path.basename(p))
        print(os.path.basename(p), 'ok' if ok else 'CHECK', flush=True)
        allz += zip_3d(p)
    if not sys.argv[1:] and os.path.isdir(f'{OUT}/3d-models/stl'):
        readme(f'{OUT}/3d-models/stl', 'GDI buildings (Construction Yard, Power Plant, Barracks, Tiberium Silo, Tech Center)')
        allz += zip_gdi()
    print('ZIPS', ' '.join(allz))
