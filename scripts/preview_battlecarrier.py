"""Offline preview: composite the cruiser hull + helideck overlay across 16 facings
into ~/Desktop/battlecarrier-preview/ so the deck art can be reviewed WITHOUT
reloading the game. Placement approximates the engine (iso-aft direction, 2:1
y-compression) -- good for judging look/colour/rotation; exact placement is
engine-locked. Re-run after each deck re-render.
Usage: python3 scripts/preview_battlecarrier.py [deck_render_dir] [R] [D] [LIFT]
"""
from PIL import Image
import json, math, os, sys
DECK = sys.argv[1] if len(sys.argv)>1 else '/tmp/deckrender'
R    = float(sys.argv[2]) if len(sys.argv)>2 else 95
D    = int(sys.argv[3])   if len(sys.argv)>3 else 150
LIFT = float(sys.argv[4]) if len(sys.argv)>4 else 8
SIZE=384; CX=CY=192
src='/tmp/vesselzips/ca_all'
OUT=os.path.expanduser('~/Desktop/battlecarrier-preview'); os.makedirs(OUT,exist_ok=True)
def hull(s):
    b=f'ca-{s:04d}-0000'; t=Image.open(f'{src}/{b}.tga').convert('RGBA')
    x0,y0,_,_=json.load(open(f'{src}/{b}.meta'))['crop']
    c=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0)); c.alpha_composite(t,(x0,y0)); return c
def comp(s):
    c=hull(s); aft=math.radians(s*22.5+180)
    dx=R*math.sin(aft); dy=-R*math.cos(aft)*0.5
    d=Image.open(f'{DECK}/facing-{s:02d}.png').convert('RGBA'); d=d.crop(d.getbbox())
    d=d.resize((D,max(1,round(d.height*D/d.width))),Image.LANCZOS)
    c.alpha_composite(d,(int(CX+dx-d.width/2),int(CY+dy-d.height/2-LIFT))); return c
M=Image.new('RGBA',(200*4,200*4),(60,90,120,255))
for s in range(16):
    c=comp(s); sh=c.crop(c.getbbox())
    c.crop(c.getbbox()).save(f'{OUT}/facing-{s:02d}.png')
    th=sh.copy(); th.thumbnail((195,195))
    M.alpha_composite(th,((s%4)*200+(200-th.width)//2,(s//4)*200+(200-th.height)//2))
M.save(f'{OUT}/_ALL-facings.png')
print('wrote', OUT)
