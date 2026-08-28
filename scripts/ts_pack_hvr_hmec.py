#!/usr/bin/env python3
"""Pack the Hover MLRS (TSHVR) and Mammoth Mk. II (TSHMEC) zips on their own.

These are the TSHVR and TSHMEC blocks of scripts/ts_pack_walkers.py, verbatim,
without that script's Titan / RAILFX / icon / XML work (which needs the Titan
SHP inputs). Use for voxel re-renders of the two units. Inputs (TS_ART_DIR):
  hq_hvr_body, hq_hvr_tur   HVR.VXL / HVRTUR.VXL renders per the render ledger
                            (docs/launcher-render-contracts.md); the rack is --z-clip 10
  ts35_hmec_<f>             HMEC.VXL posed by HMEC.HVA frame f, 35 degree camera
Follow with scripts/ts_reshadow.py TSHVR TSHMEC. License: GPL v3.
"""
import io, json, os, zipfile
from PIL import Image
ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the rendered TS art directory")
MOD = os.environ.get("TF_MOD_DIR", os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "resources", "remaster_mods", "Vanilla_RA")))
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
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


# ts_reshadow.py owns the shadow convention -- run it after any repack.
def drop_shadow(frame, dx, dy, alpha=191):
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
        hframes.append(drop_shadow(out, 5, 17))
    for im in ht:
        scaled = im.resize((round(im.width * F_H), round(im.height * F_H)), Image.LANCZOS)
        out = Image.new("RGBA", (CANVAS_H, CANVAS_H), (0, 0, 0, 0))
        safe_paste(out, scaled, round(96 - scaled.width / 2), round(96 - scaled.height / 2))
        hframes.append(out)
    write_zip(f"{UNITS_DIR}/TSHVR.ZIP", "tshvr", hframes)
