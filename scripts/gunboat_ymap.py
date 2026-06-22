import bpy, sys, math, mathutils, os, bmesh
m=sys.argv[sys.argv.index("--")+1:][0]; out="/tmp/gbymap"; os.makedirs(out,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=m)
o=[x for x in bpy.context.scene.objects if x.type=="MESH"][0]
M=o.matrix_world; me=o.data
ys=[(M@v.co).y for v in me.vertices]; miny,maxy=min(ys),max(ys)
# vertex color layer mapping Y -> rainbow
import colorsys
vc=me.color_attributes.new(name="Ycol",type='FLOAT_COLOR',domain='POINT')
for i,v in enumerate(me.vertices):
    t=((M@v.co).y-miny)/(maxy-miny)
    r,g,b=colorsys.hsv_to_rgb(t*0.83,1.0,1.0)
    vc.data[i].color=(r,g,b,1)
# emission material from vertex color
mat=bpy.data.materials.new("vc"); mat.use_nodes=True; nt=mat.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
em=nt.nodes.new("ShaderNodeEmission"); at=nt.nodes.new("ShaderNodeVertexColor"); at.layer_name="Ycol"
op=nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(at.outputs["Color"],em.inputs["Color"]); nt.links.new(em.outputs["Emission"],op.inputs["Surface"])
o.data.materials.clear(); o.data.materials.append(mat)
mn=mathutils.Vector((1e9,)*3); mx=mathutils.Vector((-1e9,)*3)
for c in o.bound_box:
    w=M@mathutils.Vector(c); mn=mathutils.Vector((min(mn[i],w[i]) for i in range(3))); mx=mathutils.Vector((max(mx[i],w[i]) for i in range(3)))
piv=bpy.data.objects.new("P",None); bpy.context.scene.collection.objects.link(piv); o.parent=piv
piv.location=-(mn+mx)/2; piv.scale=(2/max((mx-mn)),)*3
ww=bpy.data.worlds.new("w"); bpy.context.scene.world=ww; ww.use_nodes=True; ww.node_tree.nodes["Background"].inputs[1].default_value=0.0
scn=bpy.context.scene; eng=[e.identifier for e in type(scn.render).bl_rna.properties['engine'].enum_items]
scn.render.engine="BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in eng else "BLENDER_EEVEE"
scn.render.resolution_x=scn.render.resolution_y=500; scn.render.film_transparent=True
cam=bpy.data.objects.new("c",bpy.data.cameras.new("c")); cam.data.type="ORTHO"; cam.data.ortho_scale=2.2; bpy.context.scene.collection.objects.link(cam); scn.camera=cam
import math as mm
def shot(n,loc,rot):
    cam.location=loc; cam.rotation_euler=rot; scn.render.filepath=f"{out}/{n}.png"; bpy.ops.render.render(write_still=True)
shot("side",(10,0,0),(mm.radians(90),0,mm.radians(90)))
shot("top",(0,0,10),(0,0,0))
print(f"Ymap: miny={miny:.3f} maxy={maxy:.3f}  HUE 0(red)=miny -> 0.83(violet)=maxy")
print("legend: red=-0.5 .. orange=-0.33 .. yellow=-0.17 .. green=0.0 .. cyan=+0.17 .. blue=+0.33 .. violet=+0.5")
