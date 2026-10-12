#!/usr/bin/env python3
"""Print-ready STL files from the asset packs' .glb models, one per model (each root node of the .glb): the parts fused
into one watertight solid, as the HD art chat's building STLs are (1 cell = 32 mm, Z up, the base on Z = 0).

The parts are voxelised at 0.25 mm and filled, anything under 1 mm thick is thickened to about that, loose specks
under 3 mm3 are left out, and each separate piece is dropped onto the bed in place. Writes OUT_DIR/<model>.stl.
Needs trimesh, scipy and scikit-image.
usage: glb_to_stl.py OUT_DIR GLB[:root,root...][@base] ...
License: GPL v3.
"""
import os
import sys

import numpy as np
import trimesh
from scipy import ndimage
from skimage import measure

MM_PER_CELL = 32.0
PITCH = 0.25  # mm per voxel
THIN = 2  # voxels: parts thinner than 2 x THIN + 1 voxels (about 1 mm) are thickened
SPECK_MM3 = 3.0
BASE_MM = 1.5  # an @base model (an infantryman) stands on a round base this thick, 1 mm wider than him all round
MAX_FACES = 180000
Y_UP_TO_Z_UP = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])


def model_meshes(scene, root):
    """Every mesh under one root node, in millimetres with Z up."""
    out = []
    for node in scene.graph.nodes_geometry:
        if root is not None and not under(scene, node, root):
            continue
        transform, geometry = scene.graph[node]
        mesh = scene.geometry[geometry].copy()
        mesh.apply_transform(transform)
        mesh.apply_transform(Y_UP_TO_Z_UP)
        mesh.apply_scale(MM_PER_CELL)
        out.append(mesh)
    return out


def under(scene, node, root):
    """Whether node is root or hangs below it."""
    while node is not None:
        if node == root:
            return True
        parents = scene.graph.transforms.parents
        node = parents.get(node)
    return False


def solid(meshes):
    """The meshes as one voxel solid: (occupancy grid, origin of voxel 0 in mm)."""
    lo = np.min([m.bounds[0] for m in meshes], axis=0) - 4 * PITCH
    hi = np.max([m.bounds[1] for m in meshes], axis=0) + 4 * PITCH
    shape = np.ceil((hi - lo) / PITCH).astype(int) + 1
    grid = np.zeros(shape, bool)
    for mesh in meshes:
        vox = mesh.voxelized(PITCH)
        part = np.zeros(shape, bool)
        idx = np.round((vox.points - lo) / PITCH).astype(int)
        idx = idx[(idx >= 0).all(1) & (idx < shape).all(1)]
        part[tuple(idx.T)] = True
        grid |= ndimage.binary_fill_holes(part)
    grid = ndimage.binary_fill_holes(grid)
    ball = ndimage.generate_binary_structure(3, 1)
    ball = ndimage.iterate_structure(ball, THIN)
    thin = grid & ~ndimage.binary_opening(grid, ball)
    grid |= ndimage.binary_dilation(thin, ball)
    return grid, lo


def pieces(grid):
    """The solid's separate pieces bigger than a speck, each dropped to the grid's floor in place."""
    labels, n = ndimage.label(grid)
    sizes = ndimage.sum(grid, labels, range(1, n + 1))
    keep = [i + 1 for i, s in enumerate(sizes) if s * PITCH ** 3 >= SPECK_MM3]
    floor = min(np.nonzero(labels == k)[2].min() for k in keep)
    out = np.zeros_like(grid)
    for k in keep:
        piece = labels == k
        drop = np.nonzero(piece)[2].min() - floor
        out |= np.roll(piece, -drop, axis=2)
    return out, len(keep)


def on_base(grid):
    """The solid standing on a round base: a disc under its feet, as a miniature's."""
    thick = int(round(BASE_MM / PITCH))
    xs, ys, _ = np.nonzero(grid)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    r = max(xs.max() - xs.min(), ys.max() - ys.min()) / 2 + 1.0 / PITCH
    pad = int(np.ceil(r - min(cx, cy, grid.shape[0] - cx, grid.shape[1] - cy))) + 1
    grid = np.pad(grid, ((max(pad, 0),) * 2, (max(pad, 0),) * 2, (thick, 0)))
    cx, cy = cx + max(pad, 0), cy + max(pad, 0)
    floor = np.nonzero(grid.any((0, 1)))[0].min()
    gx, gy = np.mgrid[:grid.shape[0], :grid.shape[1]]
    disc = (gx - cx) ** 2 + (gy - cy) ** 2 <= r * r
    grid[:, :, floor - thick:floor] |= disc[:, :, None]
    return grid


def to_mesh(grid, lo):
    """The solid's surface, smoothed a little, at the finest marching-cubes step that stays under MAX_FACES (a
    coarser step keeps it watertight, where decimating does not)."""
    field = ndimage.gaussian_filter(np.pad(grid, 2).astype(np.float32), 0.7)
    for step in (1, 2, 3, 4):
        verts, faces, _, _ = measure.marching_cubes(field, 0.5, step_size=step)
        if len(faces) <= MAX_FACES:
            break
    mesh = trimesh.Trimesh((verts - 2) * PITCH + lo, faces, process=True)
    trimesh.repair.fix_normals(mesh)
    mesh.apply_translation([-mesh.bounds[0][0] - mesh.extents[0] / 2, -mesh.bounds[0][1] - mesh.extents[1] / 2,
                            -mesh.bounds[0][2]])
    return mesh


def main(out_dir, specs):
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for spec in specs:
        spec, base, _ = spec.partition("@")
        path, _, roots = spec.partition(":")
        scene = trimesh.load(path, force="scene")
        names = roots.split(",") if roots else [None]
        for root in names:
            name = root or os.path.splitext(os.path.basename(path))[0]
            grid, lo = solid(model_meshes(scene, root))
            grid, count = pieces(grid)
            if base:
                grid = on_base(grid)
            mesh = to_mesh(grid, lo)
            mesh.export(os.path.join(out_dir, f"{name}.stl"))
            x, y, z = mesh.extents
            row = (f"  {name + '.stl':40s} {x:6.1f} x {y:6.1f} x {z:6.1f} mm  {len(mesh.faces):7d} triangles  "
                   f"{count} piece{'s' if count > 1 else ' '}  {'watertight' if mesh.is_watertight else 'NOT watertight'}")
            rows.append(row)
            print(row, flush=True)
    return rows


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2:])
