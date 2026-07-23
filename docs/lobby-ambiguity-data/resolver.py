#!/usr/bin/env python3
# Exact port of TF_Resolve_Lobby_Ambiguity for offline validation.
import sys, re
from collections import Counter

def parse(path):
    cycles=[]; cur=None; site=None
    for line in open(path,errors='replace'):
        m=re.match(r'===CYCLE (\d+) v2=(\w+) gt=(\d+)',line)
        if m: cur={'n':int(m.group(1)),'gt':m.group(3),'sites':{}}; cycles.append(cur); site=None; continue
        m=re.search(r'LOBBYCAND site=(\d+) count=(\d+) disagree=(\d+)',line)
        if m and cur is not None: site=m.group(1); cur['sites'][site]={'disagree':int(m.group(3)),'c':[]}; continue
        m=re.search(r'CAND a=\d+ addr=\w+ region=\w+/\d+K prot=\w+ diff=(-?\d+) refs=(-?\d+)(?: refwin=(-?\d+))?',line)
        if m and cur is not None and site is not None:
            cur['sites'][site]['c'].append((m.group(1),int(m.group(2)),int(m.group(3) or m.group(2))))
    return cycles

def resolve(cands):
    # cands: list of (diffstr, refeq, refwin)
    # 1. exact referrer
    pos=set(d for d,eq,rw in cands if eq>0)
    if len(pos)==1: return ('R', next(iter(pos)))
    # 2. freshness cluster (low refwin)
    minrw=min(rw for _,_,rw in cands)
    thr=minrw*4+2
    fresh=set(d for d,_,rw in cands if rw<=thr)
    if len(fresh)==1: return ('F', next(iter(fresh)))
    # 3. strict majority
    cnt=Counter(d for d,_,_ in cands); mx=max(cnt.values())
    top=[d for d,n in cnt.items() if n==mx]
    if len(top)==1: return ('M', top[0])
    # 4. undecided
    return ('U', None)

allamb=0; passc=0; wrong=0; undec=0; bybranch=Counter()
for path in sys.argv[1:]:
    cyc=parse(path)
    for c in cyc:
        sd=c['sites'].get('0') or c['sites'].get('1')
        if not sd or not sd['c'] or sd['disagree']==0: continue
        allamb+=1
        branch,val=resolve(sd['c'])
        bybranch[branch]+=1
        if branch=='U': undec+=1; verdict='UNDECIDED'
        elif val==c['gt']: passc+=1; verdict='PASS'
        else: wrong+=1; verdict=f'WRONG({val}/{c["gt"]})'
        tag='' if verdict=='PASS' else '   <<< '+verdict
        cs=" ".join(f"{d}:{eq}:{rw}" for d,eq,rw in sd['c'])
        print(f"[{path.split('/')[-1][:14]:>14} c{c['n']:>2}] gt={c['gt']} -> {branch}:{val} {verdict}{tag}   | {cs}")
print(f"\n=== {allamb} ambiguous: PASS={passc} WRONG={wrong} UNDECIDED={undec} | branch usage {dict(bybranch)} ===")
