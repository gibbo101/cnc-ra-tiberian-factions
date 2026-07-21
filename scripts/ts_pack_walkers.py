#!/usr/bin/env python3
"""Package the TS walker units into the mod tree (walk-animation layout):
  - TSTITN.ZIP   152 frames: body walk 0-119 (8 facings x 15 walk frames,
                 1:1 with MMCH.SHP frames 0-119) + turret 120-151 (32 facings).
                 One shared source-canvas transform keeps the turret registered
                 on the hull. rules.ini: WalkFrames=15 WalkFacings=8.
  - TSHMEC.ZIP   256 frames: 32 facings x 8 walk stages from the HVA-posed
                 voxel renders (walk_hmec_<hva>/frame-<facing>.png).
                 rules.ini: WalkFrames=8 WalkFacings=32. No turret.
  - RAILFX pad   the spark tileset padded to 12 shapes (6 real + 6 blank):
                 WINDOW_VIRTUAL anim draws ignore the stage cap (anim.cpp:328),
                 so dying sparks request shapes >= Stages — blanks absorb them
                 instead of the launcher's white placeholder box.
  - RA_UNITS.XML / RA_VFX.XML tile runs (REPLACING any existing entries),
    RABUILDABLES.XML, ModText.csv, BuildIcons (TS cameos via CAMEO.PAL).

Inputs (set TS_ART_DIR):
  $TS_ART_DIR/shp_mmch/frame-NNNN.png       decoded MMCH.SHP (ts_shp.py, UNITTEM.PAL)
  $TS_ART_DIR/walk_hmec_<f>/frame-NNNN.png  HMEC walk renders, f in WALK_HVA_FRAMES
  $TS_ART_DIR/shp_mmchicon2, shp_hmecicon2  decoded TS cameos (CAMEO.PAL!)
"""
import io, json, os, re, zipfile
from PIL import Image
import hqx

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the extracted/rendered TS art directory")
MOD = "/home/gibbo101/Documents/development/cnc-remastered-mods/cnc-ra-tiberian-factions/resources/remaster_mods/Vanilla_RA"
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
VFX_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/VFX"
ICON_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB"

WALK_HVA_FRAMES = [0, 2, 4, 6, 8, 11, 13, 15]  # 8 stages sampled from the 17-frame HVA gait


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def write_zip(path, name, frames):
    # Launcher contract (settled 2026-07-20 after one false turn): the launcher
    # anchors the VIRTUAL CANVAS CENTER at the object's draw position; the meta
    # crop only places the TGA on that canvas. (A "crop-center anchoring"
    # theory was briefly held and falsified by the MLRS rack sinking into its
    # deck — see launcher-render-contracts.md #1.) Center-symmetric crops are
    # kept anyway: they make the two anchoring interpretations coincide, so
    # frames stay correct even if some launcher path differs.
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            W, H = img.width, img.height
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0 = min(bb[0], W - bb[2])
            y0 = min(bb[1], H - bb[3])
            b = (x0, y0, W - x0, H - y0)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps(
                {"size": [W, H], "crop": [b[0], b[1], b[2], b[3]]}))
    print(f"wrote {path} ({len(frames)} frames, center-symmetric crops)")


def safe_paste(dst, src, x, y):
    """Image.paste with an RGBA mask CORRUPTS output for negative offsets
    (Pillow 10.2 — interleaved-strip garbage). Pre-crop the source instead."""
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy:
        src = src.crop((sx, sy, src.width, src.height))
        x, y = max(0, x), max(0, y)
    dst.paste(src, (x, y), src)


def crisp_place(img, factor, canvas, anchor_src, anchor_dst):
    """Pixel-art upscale (hq4x for edge quality, then LANCZOS to target) of the
    full source canvas, placed so anchor_src lands at anchor_dst (output px)."""
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    big = hqx.hq4x(rgb).convert("RGBA")
    alpha = img.split()[3].resize((img.width * 4, img.height * 4), Image.LANCZOS)
    big.putalpha(alpha)
    nw, nh = round(img.width * factor), round(img.height * factor)
    scaled = big.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    ox = round(anchor_dst[0] - anchor_src[0] * factor)
    oy = round(anchor_dst[1] - anchor_src[1] * factor)
    safe_paste(out, scaled, ox, oy)
    return out


def drop_shadow(frame, dx, dy, alpha=130):
    """2TNK technique: hull silhouette offset down-right, composited under."""
    sil = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    mask = frame.split()[3].point(lambda a: alpha if a > 0 else 0)
    black = Image.new("RGBA", frame.size, (0, 0, 0, 255))
    sil.paste(black, (dx, dy), mask)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.alpha_composite(sil)
    out.alpha_composite(frame)
    return out


# ---- TSTITN (Titan): walk layout, one shared transform ----
# 448 canvas at the 56x56 stub = the 8x-classic density all TS units ship at
# (house policy: maximum quality). Same on-screen size; double pixels for the
# CFE zoom levels, and the voxel cannon renders at half the downscale.
CANVAS_T = 448
F_T = 6.4
ANCHOR_SRC = (47.5, 55.0)   # source canvas center x, feet row
ANCHOR_DST = (224.0, 386.0) # feet placed so the whole assembly centers on the
                            # canvas center (the launcher's draw anchor) —
                            # feet-low placement was the floating-selection-box bug

mm = lambda i: Image.open(f"{ART}/shp_mmch/frame-{i:04d}.png").convert("RGBA")
frames = []
# MMCH.SHP orders facings CLOCKWISE (0=N); the engine's frame space (BodyShape)
# is CCW 0=N — reorder both the body facing blocks and the turret run.
# 12 of the 15 walk frames per facing: total tileset = 8*12 + 32 = 128 shapes,
# keeping every index <= 127 (larger indexes die in the launcher sub-object path).
WALK_PICK = [0, 1, 2, 4, 5, 6, 8, 9, 10, 11, 13, 14]
for f in range(8):                        # body: out facing f (CCW) <- src block (8-f)%8 (CW)
    src_block = (8 - f) % 8
    for s in WALK_PICK:
        fr = crisp_place(mm(src_block * 15 + s), F_T, CANVAS_T, ANCHOR_SRC, ANCHOR_DST)
        frames.append(drop_shadow(fr, 14, 18))
# Turret = SHP torso + the VOXEL cannon barrel composited per facing. TS draws
# the Titan's cannon from MMCHBARL.VXL at runtime (art.ini PBarrelLength) — it
# is NOT in the SHP frames, which is why the ported torso had no gun. The
# barrel render's canvas center is the voxel origin = the mount point, so we
# place that at the torso's barrel port. Barrel goes UNDER the torso when
# pointing away (N half), OVER when toward the camera.
import math as _math
MUZZLE_TABLE = []  # (dx, dy) leptons from unit center, per CCW turret facing
# hand-corrections to the auto-estimated muzzle tip (px, compass anchors
# N,NW,W,SW,S,SE,E,NE — interpolated across 32 facings like FACING_TWEAKS).
# N: the away-facing barrel foreshortens the along-aim tip estimate.
MUZZLE_TWEAKS = [(7, -3), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
BARL_SCALE = 0.55          # 1 voxel ≈ 1 TS SHP px: barrel at 12px/voxel * 0.29 ≈ SHP px * 3.2 (F_T)
PORT_FWD = 32              # gun port: forward of the turret anchor along the aim
PORT_LAT = 18             # onto the right flank (TS FLH lateral -50)
PORT_UP = 30               # ...and up at the pod's gun height (final px)
# (dx, dy) per compass anchor N,NW,W,SW,S,SE,E,NE — CCW index s/4
FACING_TWEAKS = [(21, 46), (46, 29), (53, 46), (20, -12), (-34, -26), (-63, 18), (-53, 46), (-7, 52)]
VERT = 0.50                # ground-plane vertical foreshortening at the TS-native ~30° camera (the barrel renders at 30° to MATCH the TS SHP torso's own drawing camera — a 54° barrel on 30° art reads long and over-vertical at N/S)
for s in range(32):                       # out s (CCW) <- src (32-s)%32 (CW)
    torso = crisp_place(mm(120 + (32 - s) % 32), F_T, CANVAS_T, ANCHOR_SRC, ANCHOR_DST)
    bar = Image.open(f"{ART}/ts30_titanbarl/frame-{s:04d}.png").convert("RGBA")
    # TS's own renderer draws toward-viewer (south-arc) barrels longer than a
    # pure orthographic 30° projection — stretch vertically to match the
    # reference (S barrel reaches past the pod's bottom in TS).
    # uniform scale at every facing (Luke 2026-07-20 — the earlier south-arc
    # stretch made S barrels longer than the rest; removed)
    bar = bar.resize((round(bar.width * BARL_SCALE),
                      round(bar.height * BARL_SCALE)), Image.LANCZOS)
    # Attach the barrel's REAR to the pod's gun port (rotated per facing).
    # The voxel's own origin offsets don't line up with the SHP torso's port,
    # so anchor empirically: aim vector on screen, port = anchor + aim*fwd - up,
    # barrel rear = content center - aim * half-length-along-aim.
    theta = _math.radians(s * 11.25)                  # CCW from N
    ax, ay = -_math.sin(theta), -_math.cos(theta) * VERT
    bb = bar.getbbox()
    if bb:
        # exact rear point: the barrel pixels most opposite the aim direction
        # (the bbox-projection approximation left the barrel floating off the
        # pod at diagonal facings)
        import numpy as _np
        alpha = _np.array(bar)[..., 3]
        ys, xs = _np.nonzero(alpha > 40)
        proj = xs * ax + ys * ay
        cut = _np.percentile(proj, 8)
        sel = proj <= cut
        rear_x, rear_y = float(xs[sel].mean()), float(ys[sel].mean())
        # lateral mount: the cannon sits on the Titan's RIGHT flank (TS
        # PrimaryFireFLH lateral -50). Screen-space right-of-aim rotates with
        # the facing: (cos th, -sin th * VERT). At S this puts the cannon on
        # the viewer's left; at N it tucks behind the pod.
        rx_, ry_ = _math.cos(theta), -_math.sin(theta) * VERT
        port_x = CANVAS_T / 2 + ax * PORT_FWD + rx_ * PORT_LAT
        port_y = CANVAS_T / 2 + ay * PORT_FWD + ry_ * PORT_LAT - PORT_UP
        # per-facing hand tweaks (dx, dy in final px) at the 8 compass anchors,
        # linearly interpolated across the 32 turret facings — tuned one facing
        # at a time against the TS reference with Luke
        a8 = s / 4.0
        i0, i1 = int(a8) % 8, (int(a8) + 1) % 8
        frac = a8 - int(a8)
        tw0, tw1 = FACING_TWEAKS[i0], FACING_TWEAKS[i1]
        port_x += tw0[0] * (1 - frac) + tw1[0] * frac
        port_y += tw0[1] * (1 - frac) + tw1[1] * frac
        # away-facings: tuck the barrel deeper behind the pod (the rear-point
        # estimate runs high on near-vertical barrels, leaving a float gap)
        tuck = 30 if (s <= 4 or s >= 28) else 0
        bx = round(port_x - rear_x - ax * tuck)
        by = round(port_y - rear_y - ay * tuck)
    else:
        bx = by = 0
    # record the muzzle tip (extreme barrel pixels along the aim) for the
    # generated Fire_Coord table — art and fire-point stay in lockstep
    if bb:
        tip_sel = proj >= _np.percentile(proj, 97)
        tip_x = float(xs[tip_sel].mean()) + bx
        tip_y = float(ys[tip_sel].mean()) + by
        mtw0, mtw1 = MUZZLE_TWEAKS[i0], MUZZLE_TWEAKS[i1]
        tip_x += mtw0[0] * (1 - frac) + mtw1[0] * frac
        tip_y += mtw0[1] * (1 - frac) + mtw1[1] * frac
        MUZZLE_TABLE.append((round((tip_x - CANVAS_T / 2) * 4 / 3), round((tip_y - CANVAS_T / 2) * 4 / 3)))
    else:
        MUZZLE_TABLE.append((0, 0))
    comp = Image.new("RGBA", (CANVAS_T, CANVAS_T), (0, 0, 0, 0))
    # The cannon mounts on the Titan's RIGHT flank (Luke, from the TS ref):
    # when the unit faces the EASTERN compass half we see its LEFT side, so
    # the cannon is on the far flank and draws UNDER the body; western half
    # (right flank toward camera) draws OVER. (CCW index s: 1-15 = facing
    # NNW..SSW-through-west? no — s maps CCW so 1..15 = the compass EAST half.)
    right_flank_away = (s <= 15)  # includes N (s=0): barrel points away, tip peeks over the pod (TS close-up ref 2026-07-20 23:13)
    if right_flank_away:
        safe_paste(comp, bar, bx, by)
        comp.alpha_composite(torso)
    else:
        comp.alpha_composite(torso)
        safe_paste(comp, bar, bx, by)
    frames.append(comp)
write_zip(f"{UNITS_DIR}/TSTITN.ZIP", "tstitn", frames)

# generated per-facing muzzle table (leptons, world x-east/y-south) — included
# by techno.cpp Fire_Coord for UNIT_TSTITN so shells + muzzle flash track the
# hand-tuned barrel anchors exactly
hdr = "// GENERATED by scripts/ts_pack_walkers.py — do not hand-edit.\n"
hdr += "// Per-CCW-turret-facing muzzle offsets (leptons from unit center).\n"
hdr += "static const short _tstitn_muzzle[32][2] = {\n"
for dx, dy in MUZZLE_TABLE:
    hdr += f"    {{{dx}, {dy}}},\n"
hdr += "};\n"
open("/home/gibbo101/Documents/development/cnc-remastered-mods/cnc-ra-tiberian-factions/redalert/tstitn_muzzle.h", "w").write(hdr)
print("wrote redalert/tstitn_muzzle.h (muzzle table)")

# ---- TSHMEC (Mammoth Mk II): 32 facings x 8 walk stages ----
# Render set preference: ts35_hmec (12 px/voxel at 35° elevation — the TS
# stance: legs read long like the original; deliberate exception to the 54°
# house camera) > hq_hmec (12 px/voxel, 54°) > walk_hmec (6 px/voxel).
# UNION-FIT transform: one affine for all 256 frames (model-space registration,
# no per-frame jitter), scaled so the union of every frame's content bbox fits
# the canvas with shadow margin — the centered-per-frame paste it replaces
# clipped the tall N/NE/NW facings.
for cand, canvas in (("br_hmec", 480), ("ts35_hmec", 480), ("hq_hmec", 480), ("walk_hmec", 240)):
    if os.path.isdir(f"{ART}/{cand}_0"):
        MDIR, CANVAS_M = cand, canvas
        break
ux0, uy0, ux1, uy1 = 1e9, 1e9, -1e9, -1e9
for hf in WALK_HVA_FRAMES:
    for i in range(32):
        b = Image.open(f"{ART}/{MDIR}_{hf}/frame-{i:04d}.png").getbbox()
        ux0, uy0 = min(ux0, b[0]), min(uy0, b[1])
        ux1, uy1 = max(ux1, b[2]), max(uy1, b[3])
MARGIN = CANVAS_M // 16  # room for the drop shadow + a little air
F_M = min((CANVAS_M - MARGIN) / (ux1 - ux0), (CANVAS_M - MARGIN) / (uy1 - uy0))
ox = round(CANVAS_M / 2 - (ux0 + ux1) / 2 * F_M)
oy = round(CANVAS_M / 2 - (uy0 + uy1) / 2 * F_M)
# Ground shadow (Luke, 2026-07-20, take 3): the FRAME'S OWN silhouette squashed
# onto the ground plane — shaped like the mech at that exact facing and stride,
# anchored at the ground line under the feet. Mostly-solid alpha because the
# launcher discards pixels below ~128 alpha (soft gradients render as nothing).
SQUASH = 0.22
SH_ALPHA = 135
mframes = []
for facing in range(32):
    for hf in WALK_HVA_FRAMES:
        im = Image.open(f"{ART}/{MDIR}_{hf}/frame-{facing:04d}.png").convert("RGBA")
        scaled = im.resize((round(im.width * F_M), round(im.height * F_M)), Image.LANCZOS)
        out = Image.new("RGBA", (CANVAS_M, CANVAS_M), (0, 0, 0, 0))
        # squashed own-silhouette shadow, HALF-TUCKED at THIS frame's feet line
        # (anchoring to the union ground line floated the mech — the union
        # bottom belongs to the deepest mid-stride frame, not this one)
        bbs = scaled.getbbox()
        if bbs:
            feet_y = oy + bbs[3]                       # this frame's feet on the canvas
            content_h = bbs[3] - bbs[1]
            # FEET-ONLY shadow (Luke): the bottom ~13% of the silhouette IS the
            # feet — each foot casts its own small pad exactly beneath itself.
            feet_strip = scaled.split()[3].crop((bbs[0], bbs[1] + round(content_h * 0.87), bbs[2], bbs[3]))
            sh_h = max(4, round(feet_strip.height * 0.7))
            sil = feet_strip.resize((bbs[2] - bbs[0], sh_h), Image.LANCZOS)
            sil = sil.point(lambda a: SH_ALPHA if a > 50 else 0)
            sh_img = Image.new("RGBA", (bbs[2] - bbs[0], sh_h), (0, 0, 0, 0))
            sh_img.paste(Image.new("RGBA", sh_img.size, (0, 0, 0, 255)), (0, 0), sil)
            safe_paste(out, sh_img, ox + bbs[0] + 2, feet_y - sh_h + 3)
        safe_paste(out, scaled, ox, oy)
        mframes.append(out)
write_zip(f"{UNITS_DIR}/TSHMEC.ZIP", "tshmec", mframes)

# ---- TSHVR (Hover MLRS): HQ remake, body 0-31 + turret 32-63, 192 canvas ----
# Reproduces the SIGNED-OFF geometry from the 12 px/voxel renders: hull width
# 115px at E/W (matches the shipped ZIP), body content centered at (96, 98),
# turret canvas-centered (the engine aft-seat table in Turret_Adjust places
# the rack; under center-symmetric crops the centered render IS the same
# visual the old off-center-crop frames produced via crop-center anchoring).
# Skirt shadow = the walkers' drop_shadow (offset silhouette under the hull);
# bottom-anchored recipes detach into a nub at diagonal facings.
if os.path.isdir(f"{ART}/hq_hvr_body"):
    CANVAS_H = 192
    hb = [Image.open(f"{ART}/hq_hvr_body/frame-{i:04d}.png").convert("RGBA") for i in range(32)]
    ht = [Image.open(f"{ART}/hq_hvr_tur/frame-{i:04d}.png").convert("RGBA") for i in range(32)]
    b8 = hb[8].getbbox()
    F_H = 115.0 / (b8[2] - b8[0])
    # MODEL-SPACE placement: paste each render with its CANVAS (= voxel origin)
    # centered — the launcher anchors the virtual-canvas center at the draw
    # position, so the model rides exactly where the voxel data puts it (the
    # rack sits ON the deck because its model extends up from the origin).
    # Content-bbox centering here SANK the rack into the platform — that
    # regression is what falsified the short-lived "crop-center anchoring"
    # theory (see launcher-render-contracts.md #1).
    hframes = []
    for im in hb:
        scaled = im.resize((round(im.width * F_H), round(im.height * F_H)), Image.LANCZOS)
        ox2, oy2 = round(96 - scaled.width / 2), round(98 - scaled.height / 2)
        out = Image.new("RGBA", (CANVAS_H, CANVAS_H), (0, 0, 0, 0))
        # skirt shadow: the walkers' drop_shadow (full silhouette offset
        # down-right, under the hull) — it hugs the ENTIRE lower edge at every
        # facing. Both bottom-anchored schemes (whole-hull squash, bottom-slice)
        # collapse to a detached nub at diagonals, where the bbox bottom is one
        # pointy corner. Offset = walker (14,18) scaled 448→192 canvas; the
        # small gap reads as hover float.
        safe_paste(out, scaled, ox2, oy2)
        hframes.append(drop_shadow(out, 6, 8))
    for im in ht:
        scaled = im.resize((round(im.width * F_H), round(im.height * F_H)), Image.LANCZOS)
        out = Image.new("RGBA", (CANVAS_H, CANVAS_H), (0, 0, 0, 0))
        safe_paste(out, scaled, round(96 - scaled.width / 2), round(96 - scaled.height / 2))
        hframes.append(out)
    write_zip(f"{UNITS_DIR}/TSHVR.ZIP", "tshvr", hframes)

# ---- RAILFX: repack existing 6 real frames + 6 blank pad shapes ----
src = zipfile.ZipFile(f"{VFX_DIR}/RAILFX.ZIP")
real = []
for i in range(6):
    meta = json.loads(src.read(f"railfx-{i:04d}.meta"))
    tga = src.read(f"railfx-{i:04d}.tga")
    real.append((tga, meta))
blank = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
blank_tga = tga_bytes(blank.crop((0, 0, 2, 2)))
with zipfile.ZipFile(f"{VFX_DIR}/RAILFX.ZIP", "w", zipfile.ZIP_DEFLATED) as z:
    for i, (tga, meta) in enumerate(real):
        z.writestr(f"railfx-{i:04d}.tga", tga)
        z.writestr(f"railfx-{i:04d}.meta", json.dumps(meta))
    for i in range(6, 12):
        z.writestr(f"railfx-{i:04d}.tga", blank_tga)
        z.writestr(f"railfx-{i:04d}.meta", json.dumps({"size": [128, 128], "crop": [0, 0, 2, 2]}))
print("repacked RAILFX.ZIP (6 real + 6 blank shapes)")

# ---- BuildIcons (CAMEO.PAL decodes) ----
for src_d, out in [("shp_mmchicon2", "BuildIcon_TS_Titan"),
                   ("shp_hmecicon2", "BuildIcon_TS_MammothMk2")]:
    icon = Image.open(f"{ART}/{src_d}/frame-0000.png")
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(f"{ICON_DIR}/{out}.tga")
    print(f"wrote {ICON_DIR}/{out}.tga")

# ---- Tileset XML (replace-capable) ----
def tile_block(name, shape, frame_path):
    return ("\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n"
            "\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n"
            % (name, shape, frame_path))

def patch_tileset(xml_path, name, count, subdir=None):
    sub = subdir or name.lower()
    xml = open(xml_path, encoding="utf-8").read()
    # drop any existing Tile blocks for this name (any indentation)
    xml = re.sub(
        r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?",
        "", xml, flags=re.S)
    blocks = "".join(tile_block(name, s, f"{sub}\\{sub}-{s:04d}.tga") for s in range(count))
    idx = xml.rindex("</Tiles>")
    xml = xml[:idx] + blocks + xml[idx:]
    open(xml_path, "w", encoding="utf-8").write(xml)
    print(f"patched {os.path.basename(xml_path)}: {name} -> {count} tiles")

patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSTITN", 128)
patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSHMEC", 256)
patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_VFX.XML", "RAILFX", 12)
if os.path.isdir(f"{ART}/hq_hvr_body"):
    patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSHVR", 64)

# ---- RABUILDABLES ----
RAB = f"{MOD}/Data/XML/OBJECTS/UNITS/RABUILDABLES.XML"
xml = open(RAB, encoding="utf-8").read()
def buildable(name, text, icon):
    return ('\t<ObjectTypeClass Name="%s" Classification="CNCBuildableObject" CanInstantiate="False">\n'
            "\t\t<CNCEncyclopediaComponent>\n"
            "\t\t\t<ObjectNameTextID>%s</ObjectNameTextID>\n"
            "\t\t\t<ObjectDescriptionTextID>%s_DESC</ObjectDescriptionTextID>\n"
            "\t\t\t<BuildIcon>%s</BuildIcon>\n"
            "\t\t</CNCEncyclopediaComponent>\n"
            "\t</ObjectTypeClass>\n" % (name, text, text, icon))
added = ""
if "RA_TSTITN" not in xml:
    added += buildable("RA_TSTITN", "TEXT_UNIT_TSTITN", "BuildIcon_TS_Titan")
if "RA_TSHMEC" not in xml:
    added += buildable("RA_TSHMEC", "TEXT_UNIT_TSHMEC", "BuildIcon_TS_MammothMk2")
if added:
    idx = xml.rindex("</ObjectTypeClass>") + len("</ObjectTypeClass>")
    xml = xml[:idx] + "\n\n" + added.rstrip("\n") + xml[idx:]
    open(RAB, "w", encoding="utf-8").write(xml)
    print("patched RABUILDABLES.XML")

# ---- ModText.csv (UTF-16) ----
CSV = f"{MOD}/Data/ModText.csv"
raw = open(CSV, "rb").read()
text = raw.decode("utf-16")
eol = "\r\n" if "\r\n" in text else "\n"
sample = next(l for l in text.splitlines() if l.startswith('"TEXT_UNIT_TDA10"'))
tail = sample.split('"A-10 Warthog"', 1)[1]
rows = [
    ('TEXT_UNIT_TSTITN', 'Titan'),
    ('TEXT_UNIT_TSTITN_DESC', 'GDI walking assault mech.'),
    ('TEXT_UNIT_TSHMEC', 'Mammoth Mk. II'),
    ('TEXT_UNIT_TSHMEC_DESC', 'Heavy assault walker with twin railguns.'),
]
new = ""
for key, val in rows:
    if f'"{key}"' not in text:
        new += f'"{key}",,,"{val}"{tail}{eol}'
if new:
    if not text.endswith(eol):
        text += eol
    text += new
    open(CSV, "wb").write(text.encode("utf-16"))
    print("patched ModText.csv (+%d rows)" % len(new.split(eol)[:-1]))
print("DONE")
