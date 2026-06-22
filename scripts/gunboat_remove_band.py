import bpy, sys, math, mathutils, os, bmesh
a=sys.argv[sys.argv.index("--")+1:]
m=a[0]; out=a[1]; ylo=float(a[2]); yhi=float(a[3]); zfrac=float(a[4])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=m)
o=[x for x in bpy.context.scene.objects if x.type=="MESH"][0]
M=o.matrix_world
zs=[(M@v.co).z for v in o.data.vertices]; minz,maxz=min(zs),max(zs); thr=minz+zfrac*(maxz-minz)
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
td=[v for v in bm.verts if (o.matrix_world@v.co).z>thr and ylo<(o.matrix_world@v.co).y<yhi]
bmesh.ops.delete(bm, geom=td, context='VERTS'); bm.to_mesh(o.data); bm.free()
print(f"deleted {len(td)} verts in Y[{ylo},{yhi}] z>{thr:.3f}")
mn=mathutils.Vector((1e9,)*3); mx=mathutils.Vector((-1e9,)*3)
for c in o.bound_box:
    w=o.matrix_world@mathutils.Vector(c); mn=mathutils.Vector((min(mn[i],w[i]) for i in range(3))); mx=mathutils.Vector((max(mx[i],w[i]) for i in range(3)))
piv=bpy.data.objects.new("P",None); bpy.context.scene.collection.objects.link(piv); o.parent=piv
piv.location=-(mn+mx)/2; piv.scale=(2/max((mx-mn)),)*3
sun=bpy.data.objects.new("s",bpy.data.lights.new("s","SUN")); sun.data.energy=4; bpy.context.scene.collection.objects.link(sun); sun.rotation_euler=(math.radians(45),0,math.radians(30))
w=bpy.data.worlds.new("w"); bpy.context.scene.world=w; w.use_nodes=True; w.node_tree.nodes["Background"].inputs[1].default_value=0.5
scn=bpy.context.scene; eng=[e.identifier for e in type(scn.render).bl_rna.properties['engine'].enum_items]
scn.render.engine="BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in eng else "BLENDER_EEVEE"
scn.render.resolution_x=scn.render.resolution_y=400; scn.render.film_transparent=True
cam=bpy.data.objects.new("c",bpy.data.cameras.new("c")); cam.data.type="ORTHO"; cam.data.ortho_scale=2.4; bpy.context.scene.collection.objects.link(cam); scn.camera=cam
os.makedirs(out,exist_ok=True)
import math as mm; el=mm.radians(54)
def shot(n,az):
    cam.location=(0,-10*mm.cos(el),10*mm.sin(el)); cam.rotation_euler=(mm.radians(36),0,0); piv.rotation_euler=(0,0,mm.radians(az)); scn.render.filepath=f"{out}/{n}.png"; bpy.ops.render.render(write_still=True)
shot("e",0); shot("ne",-45)
cam.location=(0,0,10); cam.rotation_euler=(0,0,0); piv.rotation_euler=(0,0,0); scn.render.filepath=f"{out}/top.png"; bpy.ops.render.render(write_still=True)
