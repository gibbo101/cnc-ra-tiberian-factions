import bpy, sys, math, mathutils, os, bmesh
m=sys.argv[sys.argv.index("--")+1:][0]; out="/tmp/bandscan"; os.makedirs(out,exist_ok=True)
def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=m)
    return [x for x in bpy.context.scene.objects if x.type=="MESH"][0]
def render(o,name):
    mn=mathutils.Vector((1e9,)*3); mx=mathutils.Vector((-1e9,)*3)
    for c in o.bound_box:
        w=o.matrix_world@mathutils.Vector(c); mn=mathutils.Vector((min(mn[i],w[i]) for i in range(3))); mx=mathutils.Vector((max(mx[i],w[i]) for i in range(3)))
    piv=bpy.data.objects.new("P",None); bpy.context.scene.collection.objects.link(piv); o.parent=piv
    piv.location=-(mn+mx)/2; piv.scale=(2/max((mx-mn)),)*3
    sun=bpy.data.objects.new("s",bpy.data.lights.new("s","SUN")); sun.data.energy=4; bpy.context.scene.collection.objects.link(sun); sun.rotation_euler=(math.radians(50),0,math.radians(30))
    w=bpy.data.worlds.new("w"); bpy.context.scene.world=w; w.use_nodes=True; w.node_tree.nodes["Background"].inputs[1].default_value=0.5
    scn=bpy.context.scene; eng=[e.identifier for e in type(scn.render).bl_rna.properties['engine'].enum_items]
    scn.render.engine="BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in eng else "BLENDER_EEVEE"
    scn.render.resolution_x=scn.render.resolution_y=300; scn.render.film_transparent=True
    cam=bpy.data.objects.new("c",bpy.data.cameras.new("c")); cam.data.type="ORTHO"; cam.data.ortho_scale=2.3; bpy.context.scene.collection.objects.link(cam); scn.camera=cam
    cam.location=(0,0,10); cam.rotation_euler=(0,0,0)
    scn.render.filepath=f"{out}/{name}.png"; bpy.ops.render.render(write_still=True)
# reference (no delete)
o=setup(); render(o,"0_ref")
# delete bands (raised z, various Y)
bands=[("1_Yneg",-0.50,-0.15),("2_Ymid",-0.15,0.05),("3_Ymidpos",0.05,0.18),("4_Ypos",0.18,0.50)]
for name,ylo,yhi in bands:
    o=setup()
    zs=[(o.matrix_world@v.co).z for v in o.data.vertices]; minz,maxz=min(zs),max(zs); thr=minz+0.5*(maxz-minz)
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    td=[v for v in bm.verts if (o.matrix_world@v.co).z>thr and ylo<(o.matrix_world@v.co).y<yhi]
    bmesh.ops.delete(bm,geom=td,context='VERTS'); bm.to_mesh(o.data); bm.free()
    render(o,name)
print("done")
