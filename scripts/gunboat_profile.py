import bpy, sys, math, mathutils, os
m=sys.argv[sys.argv.index("--")+1:][0]; out="/tmp/gbprofile"; os.makedirs(out,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=m)
o=[x for x in bpy.context.scene.objects if x.type=="MESH"][0]
M=o.matrix_world
V=[M@v.co for v in o.data.vertices]
xs=[p.x for p in V]; ys=[p.y for p in V]; zs=[p.z for p in V]
minx,maxx=min(xs),max(xs); miny,maxy=min(ys),max(ys); minz,maxz=min(zs),max(zs)
print(f"BOUNDS X[{minx:.3f},{maxx:.3f}] Y[{miny:.3f},{maxy:.3f}] Z[{minz:.3f},{maxz:.3f}]")
# Height profile along Y on the centerline strip (|x|<0.04): max Z per Y-bin.
import collections
NB=40
binmax=[-1e9]*NB; binmaxall=[-1e9]*NB
def yb(y): return min(NB-1,int((y-miny)/(maxy-miny)*NB))
for p in V:
    b=yb(p.y)
    if p.z>binmaxall[b]: binmaxall[b]=p.z
    if abs(p.x)<0.04 and p.z>binmax[b]: binmax[b]=p.z
print("Y-bin  Ycenter  maxZ(center)  maxZ(all)")
for b in range(NB):
    yc=miny+(b+0.5)/NB*(maxy-miny)
    c=binmax[b] if binmax[b]>-1e8 else float('nan')
    a=binmaxall[b]
    bar="#"*int(max(0,(c-minz)/(maxz-minz)*30)) if c==c else ""
    print(f"{b:2d}  {yc:+.3f}  {c:+.3f}  {a:+.3f}  {bar}")
