import bpy, sys, math, mathutils, os
a=sys.argv[sys.argv.index("--")+1:]
m=a[0]; out=a[1] if len(a)>1 else "/tmp/gbviews"
# optional delete band: ylo yhi zthr (absolute Z)
dyl=dyh=dz=None
if len(a)>=5: dyl=float(a[2]); dyh=float(a[3]); dz=float(a[4])
os.makedirs(out,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=m)
o=[x for x in bpy.context.scene.objects if x.type=="MESH"][0]
M=o.matrix_world
if dyl is not None:
    import bmesh
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    td=[v for v in bm.verts if (M@v.co).z>dz and dyl<(M@v.co).y<dyh]
    bmesh.ops.delete(bm,geom=td,context='VERTS'); bm.to_mesh(o.data); bm.free()
    print(f"deleted {len(td)} verts Y[{dyl},{dyh}] z>{dz}")
mn=mathutils.Vector((1e9,)*3); mx=mathutils.Vector((-1e9,)*3)
for c in o.bound_box:
    w=M@mathutils.Vector(c); mn=mathutils.Vector((min(mn[i],w[i]) for i in range(3))); mx=mathutils.Vector((max(mx[i],w[i]) for i in range(3)))
piv=bpy.data.objects.new("P",None); bpy.context.scene.collection.objects.link(piv); o.parent=piv
piv.location=-(mn+mx)/2; piv.scale=(2/max((mx-mn)),)*3
sun=bpy.data.objects.new("s",bpy.data.lights.new("s","SUN")); sun.data.energy=4; bpy.context.scene.collection.objects.link(sun); sun.rotation_euler=(math.radians(45),0,math.radians(30))
w=bpy.data.worlds.new("w"); bpy.context.scene.world=w; w.use_nodes=True; w.node_tree.nodes["Background"].inputs[1].default_value=0.5
scn=bpy.context.scene; eng=[e.identifier for e in type(scn.render).bl_rna.properties['engine'].enum_items]
scn.render.engine="BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in eng else "BLENDER_EEVEE"
scn.render.resolution_x=scn.render.resolution_y=420; scn.render.film_transparent=True
cam=bpy.data.objects.new("c",bpy.data.cameras.new("c")); cam.data.type="ORTHO"; cam.data.ortho_scale=2.2; bpy.context.scene.collection.objects.link(cam); scn.camera=cam
def shot(n,loc,rot,prot=(0,0,0)):
    cam.location=loc; cam.rotation_euler=rot; piv.rotation_euler=prot; scn.render.filepath=f"{out}/{n}.png"; bpy.ops.render.render(write_still=True)
import math as mm
# side: camera along +X (look toward -X) -> see Y(horiz) Z(vert). Rotate piv so boat long axis horizontal.
shot("side",(10,0,0),(mm.radians(90),0,mm.radians(90)))
# top: straight down
shot("top",(0,0,10),(0,0,0))
# 3/4 hero at 54 elevation
el=mm.radians(54)
shot("hero",(0,-10*mm.cos(el),10*mm.sin(el)),(mm.radians(36),0,0))
print("done")
