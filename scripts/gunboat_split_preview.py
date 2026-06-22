import bpy, sys, math, mathutils, os, bmesh
a=sys.argv[sys.argv.index("--")+1:]
m=a[0]; mode=a[1]; out=a[2]   # mode: body | gun
ylo,yhi,zthr=0.11,0.34,-0.02
os.makedirs(out,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=m)
o=[x for x in bpy.context.scene.objects if x.type=="MESH"][0]
M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
def ingun(v):
    p=M@v.co; return (ylo<p.y<yhi) and p.z>zthr
if mode=="body":
    td=[v for v in bm.verts if ingun(v)]           # remove the gun
else:
    td=[v for v in bm.verts if not ingun(v)]        # keep only the gun
bmesh.ops.delete(bm,geom=td,context='VERTS'); bm.to_mesh(o.data); bm.free()
print(f"mode={mode} deleted {len(td)} verts; remaining {len(o.data.vertices)}")
mn=mathutils.Vector((1e9,)*3); mx=mathutils.Vector((-1e9,)*3)
for c in o.bound_box:
    w=M@mathutils.Vector(c); mn=mathutils.Vector((min(mn[i],w[i]) for i in range(3))); mx=mathutils.Vector((max(mx[i],w[i]) for i in range(3)))
piv=bpy.data.objects.new("P",None); bpy.context.scene.collection.objects.link(piv); o.parent=piv
piv.location=-(mn+mx)/2; piv.scale=(2/max((mx-mn)),)*3
sun=bpy.data.objects.new("s",bpy.data.lights.new("s","SUN")); sun.data.energy=4; bpy.context.scene.collection.objects.link(sun); sun.rotation_euler=(math.radians(45),0,math.radians(30))
w=bpy.data.worlds.new("w"); bpy.context.scene.world=w; w.use_nodes=True; w.node_tree.nodes["Background"].inputs[1].default_value=0.5
scn=bpy.context.scene; eng=[e.identifier for e in type(scn.render).bl_rna.properties['engine'].enum_items]
scn.render.engine="BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in eng else "BLENDER_EEVEE"
scn.render.resolution_x=scn.render.resolution_y=440; scn.render.film_transparent=True
cam=bpy.data.objects.new("c",bpy.data.cameras.new("c")); cam.data.type="ORTHO"; cam.data.ortho_scale=2.2; bpy.context.scene.collection.objects.link(cam); scn.camera=cam
import math as mm; el=mm.radians(54)
def shot(n,loc,rot):
    cam.location=loc; cam.rotation_euler=rot; scn.render.filepath=f"{out}/{n}.png"; bpy.ops.render.render(write_still=True)
shot("side",(10,0,0),(mm.radians(90),0,mm.radians(90)))
shot("hero",(0,-10*mm.cos(el),10*mm.sin(el)),(mm.radians(36),0,0))
shot("top",(0,0,10),(0,0,0))
print("done")
