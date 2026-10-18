"""Compare each TD* ZIP in resources/ with the base game's TEXTURES_TD_SRGB.MEG by frame md5.

usage: td_compare.py <repo>
"""
import sys, os, io, zipfile, hashlib, struct
sys.path.insert(0, sys.argv[1] + "/scripts")
from meg_extract import read_member
REPO=sys.argv[1]; MEG=os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_TD_SRGB.MEG")
# index once
with open(MEG,"rb") as f:
    head=f.read(8); off=8 if struct.unpack_from("<I",head,0)[0] in (0xFFFFFFFF,0x8FFFFFFF) else 0
    f.seek(off+4); nf,ns,sts=struct.unpack("<III",f.read(12)); t=f.read(sts+nf*20)
    strs=[];o=0
    for _ in range(ns):
        l=struct.unpack_from("<H",t,o)[0]; strs.append(t[o+2:o+2+l].decode("latin-1")); o+=2+l
    idx={}
    for i in range(nf):
        _a,_b,_c,size,doff,ni=struct.unpack_from("<HIiIIH",t,sts+i*20); idx[strs[ni].upper()]=(size,doff)
def base(path):
    s,d=idx[path.upper()]
    with open(MEG,"rb") as f: f.seek(d); return f.read(s)
art=REPO+"/resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT"
rows=[]
for root,_,files in os.walk(art):
    for fn in files:
        if not fn.upper().startswith("TD"): continue
        cat=os.path.relpath(root,art).replace("/","\\")
        p=os.path.join(root,fn); sz=os.path.getsize(p)
        stem=fn[2:]
        bp="DATA\\ART\\TEXTURES\\SRGB\\TIBERIAN_DAWN\\%s\\%s"%(cat,stem)
        if bp.upper() not in idx: rows.append(("NOBASE",cat,fn,sz,"")); continue
        if not fn.upper().endswith(".ZIP"):
            rows.append(("SAME" if open(p,"rb").read()==base(bp) else "DIFF",cat,fn,sz,"file")); continue
        mz=zipfile.ZipFile(p); bz=zipfile.ZipFile(io.BytesIO(base(bp)))
        mh={}; 
        for n in mz.namelist(): mh.setdefault(hashlib.md5(mz.read(n)).hexdigest(),[]).append(n)
        bh=set(hashlib.md5(bz.read(n)).hexdigest() for n in bz.namelist())
        shared=sum(len(v) for h,v in mh.items() if h in bh); tot=len(mz.namelist())
        status="SAME" if shared==tot and len(bz.namelist())==tot else ("SUPERSET" if shared==len(bz.namelist()) else ("PART" if shared else "DIFF"))
        rows.append((status,cat,fn,sz,"%d/%d of ours in base; base has %d"%(shared,tot,len(bz.namelist()))))
from collections import defaultdict
agg=defaultdict(lambda:[0,0])
for r in rows: agg[r[0]][0]+=1; agg[r[0]][1]+=r[3]
for k,(n,b) in agg.items(): print(k,n,"%.1f MB"%(b/1e6))
for r in sorted(rows):
    if r[0]!="SAME": print(*r)
