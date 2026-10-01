#!/usr/bin/env python3
"""Package the TS walker units into the mod tree (walk-animation layout):
  - TSTITN       art packed by scripts/ts_pack_hd_buildings.py; its cameo,
                 buildable entry and text are written here.
  - TSHMEC.ZIP   256 frames: 32 facings x 8 walk stages from the HVA-posed
                 voxel renders (walk_hmec_<hva>/frame-<facing>.png).
                 rules.ini: WalkFrames=8 WalkFacings=32. No turret.
  - RAILFX pad   the spark tileset padded to 12 shapes (6 real + 6 blank):
                 WINDOW_VIRTUAL anim draws ignore the stage cap (anim.cpp:328),
                 so dying sparks request shapes >= Stages — blanks absorb them
                 instead of the launcher's white placeholder box.
  - TS_UNITS.XML / TS_VFX.XML tile runs (REPLACING any existing entries),
    TSBUILDABLES.XML, ModText.csv, BuildIcons (TS cameos via CAMEO.PAL).
Art, cameos and XML go to the tree asset_packs.py routes each name to (the TS-Graphics-Pack).

Inputs (set TS_ART_DIR):
  $TS_ART_DIR/walk_hmec_<f>/frame-NNNN.png  HMEC walk renders, f in WALK_HVA_FRAMES
  $TS_ART_DIR/shp_mmchicon2, shp_hmecicon2  decoded TS cameos (CAMEO.PAL!)
"""
import io, json, os, re, sys, zipfile
from PIL import Image
import hqx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the extracted/rendered TS art directory")
# The mod tree of this script's checkout (ModText.csv, custom cameos); TF_MOD_DIR overrides it.
MOD = os.environ.get("TF_MOD_DIR", asset_packs.MOD)

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


# TSTITN (Titan) is packed from its HD art by scripts/ts_pack_hd_buildings.py, with its
# muzzle table (redalert/tstitn_muzzle.h).

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
write_zip(asset_packs.art_zip("TSHMEC", "UNITS"), "tshmec", mframes)

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
    write_zip(asset_packs.art_zip("TSHVR", "UNITS"), "tshvr", hframes)

# ---- RAILFX: repack existing 6 real frames + 6 blank pad shapes ----
RAILFX_ZIP = asset_packs.art_zip("RAILFX", "VFX")
src = zipfile.ZipFile(RAILFX_ZIP)
real = []
for i in range(6):
    meta = json.loads(src.read(f"railfx-{i:04d}.meta"))
    tga = src.read(f"railfx-{i:04d}.tga")
    real.append((tga, meta))
blank = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
blank_tga = tga_bytes(blank.crop((0, 0, 2, 2)))
with zipfile.ZipFile(RAILFX_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
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
    # Hand-made art in resources/custom-cameos is canonical for its icon name.
    custom = os.path.abspath(f"{MOD}/../../custom-cameos/{out}.png")
    if os.path.exists(custom):
        Image.open(custom).convert("RGBA").resize((341, 256), Image.LANCZOS).save(
            asset_packs.cameo_tga(out))
        print(f"custom {asset_packs.cameo_tga(out)}")
        continue
    icon = Image.open(f"{ART}/{src_d}/frame-0000.png")
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(asset_packs.cameo_tga(out))
    print(f"wrote {asset_packs.cameo_tga(out)}")

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

patch_tileset(asset_packs.tileset_xml("TSHMEC", "UNITS"), "TSHMEC", 256)
patch_tileset(asset_packs.tileset_xml("RAILFX", "VFX"), "RAILFX", 12)
if os.path.isdir(f"{ART}/hq_hvr_body"):
    patch_tileset(asset_packs.tileset_xml("TSHVR", "UNITS"), "TSHVR", 64)

# ---- Sidebar entries, in the buildables XML of each cameo's tree ----
def buildable(name, text, icon):
    return ('\t<ObjectTypeClass Name="%s" Classification="CNCBuildableObject" CanInstantiate="False">\n'
            "\t\t<CNCEncyclopediaComponent>\n"
            "\t\t\t<ObjectNameTextID>%s</ObjectNameTextID>\n"
            "\t\t\t<ObjectDescriptionTextID>%s_DESC</ObjectDescriptionTextID>\n"
            "\t\t\t<BuildIcon>%s</BuildIcon>\n"
            "\t\t</CNCEncyclopediaComponent>\n"
            "\t</ObjectTypeClass>\n" % (name, text, text, icon))
added = {}
for ini, icon in [("TSTITN", "BuildIcon_TS_Titan"), ("TSHMEC", "BuildIcon_TS_MammothMk2")]:
    rab = asset_packs.buildables_xml(icon)
    if f"RA_{ini}" not in open(rab, encoding="utf-8").read():
        added[rab] = added.get(rab, "") + buildable(f"RA_{ini}", f"TEXT_UNIT_{ini}", icon)
for rab, entries in added.items():
    xml = open(rab, encoding="utf-8").read()
    idx = xml.rindex("</ObjectTypeClass>") + len("</ObjectTypeClass>")
    xml = xml[:idx] + "\n\n" + entries.rstrip("\n") + xml[idx:]
    open(rab, "w", encoding="utf-8").write(xml)
    print(f"patched {os.path.basename(rab)}")

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
