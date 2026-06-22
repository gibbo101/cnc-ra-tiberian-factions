import bpy, sys, mathutils
m=sys.argv[sys.argv.index("--")+1:][0]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=m)
objs=[o for o in bpy.context.scene.objects if o.type=="MESH"]
print(f"MESH OBJECTS: {len(objs)}")
for o in objs:
    bb=[o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    mats=[s.material.name for s in o.material_slots if s.material]
    print(f"  '{o.name}' verts={len(o.data.vertices)} mats={mats}")
    print(f"     bounds X[{min(xs):.2f},{max(xs):.2f}] Y[{min(ys):.2f},{max(ys):.2f}] Z[{min(zs):.2f},{max(zs):.2f}]")
# count loose parts in the biggest mesh (separable chunks)
if objs:
    big=max(objs,key=lambda o:len(o.data.vertices))
    print(f"materials in '{big.name}':", [s.material.name if s.material else None for s in big.material_slots])
