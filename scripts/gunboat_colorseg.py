import bpy, sys, mathutils, os
m=sys.argv[sys.argv.index("--")+1:][0]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=m)
o=[x for x in bpy.context.scene.objects if x.type=="MESH"][0]
M=o.matrix_world
me=o.data
# Grab the base-color image texture
img=None
for ms in o.material_slots:
    if not ms.material or not ms.material.use_nodes: continue
    for n in ms.material.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image:
            img=n.image; break
    if img: break
print("texture:", img.name if img else None, img.size[:] if img else None)
px=list(img.pixels); IW,IH=img.size
def sample(u,v):
    u=u%1.0; v=v%1.0
    x=min(IW-1,int(u*IW)); y=min(IH-1,int(v*IH))
    i=(y*IW+x)*4
    return px[i],px[i+1],px[i+2]
# per-vertex UV (average of its loops)
uvlayer=me.uv_layers.active.data
vuv={}
for poly in me.polygons:
    for li in poly.loop_indices:
        vi=me.loops[li].vertex_index
        uv=uvlayer[li].uv
        vuv.setdefault(vi,[]).append((uv[0],uv[1]))
def classify(r,g,b):
    mx=max(r,g,b)
    if mx<0.18: return "black"
    if g>r*1.25 and g>b*1.15 and g>0.18: return "green"
    if b>r*1.1 and b>g*1.0 and mx<0.5: return "navy"
    return "other"
from collections import defaultdict
box=defaultdict(lambda:[1e9,-1e9,1e9,-1e9,1e9,-1e9]); cnt=defaultdict(int)
for vi,uvs in vuv.items():
    u=sum(a for a,_ in uvs)/len(uvs); v=sum(b for _,b in uvs)/len(uvs)
    r,g,b=sample(u,v); c=classify(r,g,b)
    p=M@me.vertices[vi].co; cnt[c]+=1
    bx=box[c]
    bx[0]=min(bx[0],p.x);bx[1]=max(bx[1],p.x);bx[2]=min(bx[2],p.y);bx[3]=max(bx[3],p.y);bx[4]=min(bx[4],p.z);bx[5]=max(bx[5],p.z)
for c in ["black","green","navy","other"]:
    if cnt[c]==0: continue
    bx=box[c]
    print(f"{c:6s} n={cnt[c]:6d}  X[{bx[0]:+.3f},{bx[1]:+.3f}] Y[{bx[2]:+.3f},{bx[3]:+.3f}] Z[{bx[4]:+.3f},{bx[5]:+.3f}]")
# Finer: black verts ABOVE deck (z>-0.02), where is the gun mass concentrated in Y?
import collections
yb=collections.Counter()
for vi,uvs in vuv.items():
    u=sum(a for a,_ in uvs)/len(uvs); v=sum(b for _,b in uvs)/len(uvs)
    r,g,b=sample(u,v)
    if classify(r,g,b)=="black":
        p=M@me.vertices[vi].co
        if p.z>-0.05: yb[round(p.y,1)]+=1
print("black(z>-0.05) Y-histogram:", dict(sorted(yb.items())))
