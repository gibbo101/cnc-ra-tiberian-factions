#!/usr/bin/env python3
import sys, re
from collections import Counter

def parse(path):
    cycles=[]; cur=None; site=None
    for line in open(path,errors='replace'):
        m=re.match(r'===CYCLE (\d+) v2=(\w+) gt=(\d+)',line)
        if m: cur={'n':int(m.group(1)),'v2':m.group(2),'gt':m.group(3),'sites':{}}; cycles.append(cur); site=None; continue
        m=re.search(r'LOBBYCAND site=(\d+) count=(\d+) disagree=(\d+) roster=(\w+) frame=0',line)
        if m and cur is not None: site=m.group(1); cur['sites'][site]={'disagree':int(m.group(3)),'cands':[]}; continue
        m=re.search(r'CAND a=(\d+) addr=(\w+) region=(\w+)/\d+K prot=\w+ diff=(-?\d+) refs=(-?\d+)(?: refwin=(-?\d+))?',line)
        if m and cur is not None and site is not None:
            cur['sites'][site]['cands'].append({'diff':m.group(4),'refs':int(m.group(5)),'refwin':int(m.group(6)) if m.group(6) else int(m.group(5))})
    return cycles

def maxrule(cands, key, gt):
    mx=max(c[key] for c in cands)
    top=[c for c in cands if c[key]==mx]
    vals=set(c['diff'] for c in top)
    if mx<=0: return 'NOSIG'
    if len(vals)>1: return f'TIE{sorted(set((c["diff"],c[key]) for c in top))}'
    ch=next(iter(vals))
    return 'PASS' if ch==gt else f'WRONG({ch}/{gt})'



def minrule(cands, key, gt):
    mn=min(c[key] for c in cands)
    bot=[c for c in cands if c[key]==mn]
    vals=set(c['diff'] for c in bot)
    if len(vals)>1: return f'TIE'
    ch=next(iter(vals)); return 'PASS' if ch==gt else f'WRONG({ch}/{gt})'

def combined(cands, gt):
    # 1. exact-ref: candidates with refs>0; if a UNIQUE difficulty-value among them, use it
    pos=[c for c in cands if c['refs']>0]
    posv=set(c['diff'] for c in pos)
    if len(posv)==1:
        ch=next(iter(posv)); return ('PASS(R)' if ch==gt else f'WRONG(R {ch}/{gt})')
    if len(posv)>1:
        # conflicting exact refs -> fall through to majority (record it)
        pass
    # 2. majority
    from collections import Counter
    cnt=Counter(c['diff'] for c in cands); mx=max(cnt.values()); top=[v for v,n in cnt.items() if n==mx]
    if len(top)==1:
        ch=top[0]; return ('PASS(M)' if ch==gt else f'WRONG(M {ch}/{gt})')
    # 3. fail closed
    return 'FAILCLOSED'

def majrule(cands, gt):
    cnt=Counter(c['diff'] for c in cands); mx=max(cnt.values()); top=[v for v,n in cnt.items() if n==mx]
    if len(top)>1: return 'TIE'
    return 'PASS' if top[0]==gt else f'WRONG({top[0]}/{gt})'

cycles=parse(sys.argv[1]); tal=Counter(); amb=0
print(f"{'cyc':>3} {'gt':>3} {'cnt':>3} | {'majority':>8} | {'maxRefs':>8} | {'COMBINED':>10} | {'minRefwin':>10} | cands(diff:refs:refwin)")
for c in cycles:
    sd=c['sites'].get('0') or c['sites'].get('1')
    if not sd or not sd['cands']: 
        print(f"{c['n']:>3} {c['gt']:>3}  -  | (no data)"); continue
    cands=sd['cands']
    if sd['disagree']==0:
        v=set(x['diff'] for x in cands); ok=(v=={c['gt']})
        print(f"{c['n']:>3} {c['gt']:>3} {len(cands):>3} | {'noamb-OK' if ok else 'noamb-BAD':>10} |")
        tal['noamb']+=1; continue
    amb+=1
    mj=majrule(cands,c['gt']); mr=maxrule(cands,'refs',c['gt']); mw=maxrule(cands,'refwin',c['gt']); cb=combined(cands,c['gt']); mn=minrule(cands,'refwin',c['gt'])
    cs=" ".join(f"{x['diff']}:{x['refs']}:{x['refwin']}" for x in cands)
    print(f"{c['n']:>3} {c['gt']:>3} {len(cands):>3} | {mj:>8} | {mr:>8} | {cb:>10} | {mn:>10} | {cs}")
    tal['maj:'+mj.split('(')[0].split('[')[0]]+=1
    tal['refs:'+mr.split('(')[0].split('[')[0]]+=1
    tal['COMBINED:'+cb.split('(')[0].split(' ')[0]]+=1
    tal['minRefwin:'+mn.split('(')[0]]+=1
print(f"\n=== {amb} ambiguous cycles ===")
for k,v in sorted(tal.items()): print(f"  {k}: {v}")
