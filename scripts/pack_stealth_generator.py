#!/usr/bin/env python3
"""Pack the Stealth Generator renders into TDSTEAL.ZIP (+ MAKE) game tilesets.

Masks the black background to alpha, aligns every frame on ONE shared canvas
(so buildup->idle never jumps), scales so the building is ~TARGET_W px wide
(~128px/cell), crops each frame to its own content bbox, and writes
<name>-NNNN.tga + .meta {"size":[W,H],"crop":[x0,y0,x1,y1]} into the ZIPs.
"""
import glob, json, os, zipfile
from PIL import Image, ImageDraw, ImageFilter

D = os.path.expanduser("~/Downloads")
OUT = os.path.dirname(os.path.abspath(__file__))
TARGET_W = 256          # 2 cells wide (2x2 footprint)

def find(stamp, n):
    m = glob.glob(f"{D}/ChatGPT Image Jul 14, 2026, {stamp}*({n}).png")
    return m[0] if m else None

BUILDUP = [find("11_15", n) for n in range(1, 10)]        # 9 assembly frames
HERO    = BUILDUP[-1]                                       # finished building
DAMAGED = find("11_18_48", 1)
DESTROY = find("11_18_48", 2)
assert all(BUILDUP) and DAMAGED and DESTROY, "missing source frames"

SENT = (255, 0, 255)    # flood sentinel (absent from the art)
THRESH = 34             # near-black tolerance for the connected background

def mask(im):
    """Remove ONLY the connected black background (flood-fill from all borders),
    so genuinely-dark parts of the building enclosed by the silhouette survive."""
    rgb = im.convert("RGB")
    W, H = rgb.size
    seeds = [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1),
             (W // 2, 0), (W // 2, H - 1), (0, H // 2), (W - 1, H // 2)]
    for s in seeds:
        r, g, b = rgb.getpixel(s)
        if max(r, g, b) <= THRESH:
            ImageDraw.floodfill(rgb, s, SENT, thresh=THRESH)
    out = im.convert("RGBA")
    op = out.load()
    fp = rgb.load()
    for y in range(H):
        for x in range(W):
            if fp[x, y] == SENT:
                r, g, b, _ = op[x, y]
                op[x, y] = (r, g, b, 0)
    # Drop floating islands (smoke fragments in the damaged/destroyed frames):
    # keep only the connected building blob, flood-filled from the platform base.
    alpha = out.getchannel("A")
    binm = alpha.point(lambda a: 255 if a > 40 else 0).convert("L")
    bb = binm.getbbox()
    if bb is not None:
        sx = (bb[0] + bb[2]) // 2
        sy = bb[1] + int((bb[3] - bb[1]) * 0.9)   # platform region, definitely building
        bpx = binm.load()
        if bpx[sx, sy] != 255:                     # nudge the seed onto an opaque pixel
            for yy in range(sy, bb[1], -1):
                if bpx[sx, yy] == 255:
                    sy = yy
                    break
        ImageDraw.floodfill(binm, (sx, sy), 128, thresh=0)
        keep = binm.point(lambda v: 255 if v == 128 else 0)
        alpha = Image.composite(alpha, Image.new("L", out.size, 0), keep)

    # Feather the boundary by 1px so edges aren't jagged.
    out.putalpha(alpha.filter(ImageFilter.GaussianBlur(0.6)))
    return out

def bbox(im):
    return im.getchannel("A").getbbox()

# Mask all, find a GLOBAL bbox so every frame shares the same coordinate frame.
frames = {}
gb = None
for tag, f in [("hero", HERO), ("dmg", DAMAGED), ("dead", DESTROY)] + \
              [(f"mk{i}", p) for i, p in enumerate(BUILDUP)]:
    im = mask(Image.open(f))
    frames[tag] = im
    bb = bbox(im)
    gb = bb if gb is None else (min(gb[0], bb[0]), min(gb[1], bb[1]),
                                max(gb[2], bb[2]), max(gb[3], bb[3]))

gx0, gy0, gx1, gy1 = gb
scale = TARGET_W / (gx1 - gx0)
CW = TARGET_W
CH = round((gy1 - gy0) * scale)
print(f"global bbox {gb} -> scale {scale:.4f} canvas {CW}x{CH}")

def prep(im):
    """Crop to shared global bbox, scale to canvas, return RGBA on CWxCH."""
    c = im.crop((gx0, gy0, gx1, gy1)).resize((CW, CH), Image.LANCZOS)
    return c

def write_zip(path, name, imgs, start=0):
    tmp = f"/tmp/_{name}"
    os.makedirs(tmp, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, im in enumerate(imgs):
            s = start + i
            # Full shared canvas + identical crop for EVERY frame, so the launcher
            # anchors them all the same way. Per-frame content-bbox cropping made the
            # base slide (mask/smoke edges shift the bbox frame-to-frame).
            tga = f"{tmp}/{name}-{s:04d}.tga"
            im.save(tga)     # PIL writes uncompressed 32-bit TGA
            meta = {"size": [CW, CH], "crop": [0, 0, CW, CH]}
            mp = f"{tmp}/{name}-{s:04d}.meta"
            open(mp, "w").write(json.dumps(meta))
            z.write(tga, f"{name}-{s:04d}.tga")
            z.write(mp, f"{name}-{s:04d}.meta")
    print("wrote", path, len(imgs), "frames")

# Idle/damaged ZIP: shape 0 = hero, shape 1 = damaged, shape 2 = destroyed.
write_zip(f"{OUT}/TDSTEAL.ZIP", "tdsteal",
          [prep(frames["hero"]), prep(frames["dmg"]), prep(frames["dead"])])

# Buildup ZIP: 9 assembly frames, 1-INDEXED (shape 0 is the empty tileset frame,
# matching the TDOBLIMAKE convention; BuildupAnimCount = 9 + 1 = 10).
write_zip(f"{OUT}/TDSTEALMAKE.ZIP", "tdstealmake",
          [prep(frames[f"mk{i}"]) for i in range(9)], start=1)

# Emit the RA_STRUCTURES.XML tileset blocks for both tilesets.
def tile_block(name, shape, frame):
    fr = f"<Frame>{frame}</Frame>" if frame else "<Frame />"
    return ("\t\t\t<Tile>\n\t\t\t\t<Key>\n"
            f"\t\t\t\t\t<Name>{name}</Name>\n\t\t\t\t\t<Shape>{shape}</Shape>\n"
            "\t\t\t\t</Key>\n\t\t\t\t<Value>\n\t\t\t\t\t<Frames>\n"
            f"\t\t\t\t\t\t{fr}\n\t\t\t\t\t</Frames>\n\t\t\t\t</Value>\n\t\t\t</Tile>\n")

xml = ""
for s in range(3):  # idle/damaged/destroyed shapes 0,1,2
    xml += tile_block("TDSTEAL", s, f"tdsteal\\tdsteal-{s:04d}.tga")
xml += tile_block("TDSTEALMAKE", 0, None)          # empty start frame
for s in range(1, 10):
    xml += tile_block("TDSTEALMAKE", s, f"tdstealmake\\tdstealmake-{s:04d}.tga")
open(f"{OUT}/tdsteal_tiles.xml", "w").write(xml)
print("wrote tdsteal_tiles.xml", len(xml), "bytes")
