#!/usr/bin/env python3
import sys, re, struct

STRIDE=0xA8
FIELDS={0x50:"team",0x54:"house",0x64:"diff",0x68:"color"}

def parse_log(path):
    """Return list of scan-blocks; each is dict with meta + list of candidates."""
    blocks=[]
    cur=None
    cand=None
    for line in open(path,errors='replace'):
        s=line.strip()
        m=re.match(r'LOBBYCAND (?:site=(\d+) )?count=(\d+) disagree=(\d+) roster=([0-9a-f]+) frame=(-?\d+)',s)
        if m:
            cur={'site':(m.group(1) or '?'),'count':int(m.group(2)),'disagree':int(m.group(3)),'roster':m.group(4),
                 'frame':int(m.group(5)),'cands':[]}
            blocks.append(cur); cand=None; continue
        m=re.match(r'CAND a=(\d+) addr=([0-9a-f]+) region=([0-9a-f]+)/(\d+)K prot=([0-9a-f]+) diff=(-?\d+) refs=(-?\d+)',s)
        if m and cur is not None:
            cand={'a':int(m.group(1)),'addr':int(m.group(2),16),'region':int(m.group(3),16),
                  'regK':int(m.group(4)),'prot':m.group(5),'diff':int(m.group(6)),
                  'refs':int(m.group(7)),'pre':None,'rec':[None,None]}
            cur['cands'].append(cand); continue
        m=re.match(r'PRE ([0-9a-f]+)',s)
        if m and cand is not None: cand['pre']=bytes.fromhex(m.group(1)); continue
        m=re.match(r'REC(\d) ([0-9a-f]+)',s)
        if m and cand is not None: cand['rec'][int(m.group(1))]=bytes.fromhex(m.group(2)); continue
    return blocks

def i32(b,off): return struct.unpack_from('<i',b,off)[0] if b and off+4<=len(b) else None

def show_block(blk,idx):
    print(f"\n=== scan-block #{idx}  count={blk['count']} disagree={blk['disagree']} roster={blk['roster']} frame={blk['frame']} ===")
    cands=blk['cands']
    for c in cands:
        r=c['rec'][0]
        fields=" ".join(f"{n}@{off:#x}={i32(r,off)}" for off,n in FIELDS.items())
        print(f"  a={c['a']} addr={c['addr']:08x} reg={c['region']:08x}/{c['regK']}K refs={c['refs']}  {fields}")
    # byte-diff REC0 across candidates
    if len(cands)>=2 and all(c['rec'][0] for c in cands):
        recs=[c['rec'][0] for c in cands]
        L=min(len(r) for r in recs)
        diff_offs=[o for o in range(L) if len({r[o] for r in recs})>1]
        # group into runs
        runs=[]
        for o in diff_offs:
            if runs and o==runs[-1][1]+1: runs[-1][1]=o
            else: runs.append([o,o])
        print(f"  REC0 differs at {len(diff_offs)} byte offsets across {len(cands)} candidates:")
        for a,b in runs:
            vals=" ".join(c['rec'][0][a:b+1].hex() for c in cands)
            tag=""
            for off,n in FIELDS.items():
                if a<=off<=b or a<=off+3<=b: tag=f" <-includes {n}@{off:#x}"
            print(f"    [{a:#04x}-{b:#04x}] ({b-a+1}B): {vals}{tag}")
        # STABLE offsets (same across all) that are NON-ZERO and outside known fields -- candidate discriminators
        # (only meaningful when candidates are genuinely different copies)
    # within-candidate REC0 vs REC1 (per-slot vs constant) -- only if >1 roster AI; here usually 1 AI
    return

if __name__=="__main__":
    for path in sys.argv[1:]:
        print(f"########## {path}")
        blks=parse_log(path)
        for i,b in enumerate(blks): show_block(b,i)
