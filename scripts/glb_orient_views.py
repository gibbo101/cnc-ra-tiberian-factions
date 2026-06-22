import bpy, sys, math, mathutils, os
m=sys.argv[sys.argv.index("--")+1:][0]; out="/tmp/glb_orient"
os.makedirs(out,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=m)
objs=[o for o in bpy.context.scene.objects if o.type=="MESH"]
# center
import mathutils
mn=mathutils.Vector((1e9,)*3); mx=mathutils.Vector((-1e9,)*3)
for o in objs:
    for c in o.bound_box:
        w=o.matrix_world@mathutils.Vector(c)
        mn=mathutils.Vector((min(mn[i],w[i]) for i in range(3))); mx=mathutils.Vector((max(mx[i],w[i]) for i in range(3)))
ctr=(mn+mx)/2; size=max((mx-mn))
piv=bpy.data.objects.new("P",None); bpy.context.scene.collection.objects.link(piv)
for o in objs: o.parent=piv
piv.location=-ctr; piv.scale=(2/size,)*3
# light + world
sun=bpy.data.objects.new("s",bpy.data.lights.new("s","SUN")); sun.data.energy=4; bpy.context.scene.collection.objects.link(sun); sun.rotation_euler=(math.radians(40),0,math.radians(30))
w=bpy.data.worlds.new("w"); bpy.context.scene.world=w; w.use_nodes=True; w.node_tree.nodes["Background"].inputs[1].default_value=0.5
scn=bpy.context.scene; eng=[e.identifier for e in type(scn.render).bl_rna.properties['engine'].enum_items]
scn.render.engine="BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in eng else "BLENDER_EEVEE"
scn.render.resolution_x=scn.render.resolution_y=400; scn.render.film_transparent=True
cam=bpy.data.objects.new("c",bpy.data.cameras.new("c")); cam.data.type="ORTHO"; cam.data.ortho_scale=2.4; bpy.context.scene.collection.objects.link(cam); scn.camera=cam
def shot(name,loc,rot):
    cam.location=loc; cam.rotation_euler=rot; scn.render.filepath=f"{out}/{name}.png"; bpy.ops.render.render(write_still=True)
shot("top",(0,0,10),(0,0,0))            # looking straight down (+Z)
shot("side",(0,-10,0),(math.radians(90),0,0))  # looking along +Y (side)
shot("front",(10,0,0),(math.radians(90),0,math.radians(90))) # along +X
print("model bounds (centred):  X +/-%.2f  Y +/-%.2f  Z +/-%.2f"%((mx-mn).x/2,(mx-mn).y/2,(mx-mn).z/2))
