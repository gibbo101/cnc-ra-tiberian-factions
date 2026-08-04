#!/usr/bin/env python3
"""Package the TS units wave (TSHARV / TSSMEC / TSSONIC / TSAPC) into the mod tree:
  - TSHARV.ZIP   32 frames (voxel body facings), 384 canvas, ShapeSize 48
  - TSSMEC.ZIP   96 frames (12-step walk x 8 facings, Titan walker layout), 384 canvas
  - TSSONIC.ZIP  64 frames (body 0-31 + turret 32-63, TSHVR layout), 448 canvas, ShapeSize 56
  - TSAPC.ZIP    32 frames (voxel body facings), 384 canvas, ShapeSize 48
  - BuildIcon_TS_{Harvester,Wolverine,Disruptor,AmphAPC}.tga (TS cameos, CAMEO.PAL)
  - RA_UNITS.XML tile runs (REPLACING any existing entries), RABUILDABLES.XML, ModText.csv

Density: all TS units ship at 8x-classic (canvas = ShapeSize * 8). 1 TS voxel at
12 px/voxel ~= 1 TS SHP px * 6.4 (the Titan F_T), so voxel renders scale by
6.4/12 and SHP frames by 6.4 -- every unit lands TS-relative-size-consistent.

Inputs (set TS_ART_DIR to the extraction dir):
  $TS_ART_DIR/renders_harv|renders_apc|renders_sonic|renders_sonictur/frame-NNNN.png
      (scripts/vxl_render.py at --px-per-voxel 12, 32 frames)
  $TS_ART_DIR/shp_smech/frame-NNNN.png   decoded SMECH.SHP (ts_shp.py, UNITTEM.PAL)
  $TS_ART_DIR/{HARVICON,SMCHICON,SONIICON,APCICON}.SHP + CAMEO.PAL
"""
import io, json, os, re, sys, zipfile
from PIL import Image
import hqx

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the extracted/rendered TS art directory")
# Mod tree relative to this script's repo checkout (worktree-safe; never a
# hardcoded absolute repo path -- the parallel-instance rule).
MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources", "remaster_mods", "Vanilla_RA"))
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
ICON_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ts_shp

F_SHP = 6.4          # TS SHP px -> canvas px (the Titan house factor)
F_VOX = 6.4 / 12.0   # 12 px/voxel renders -> canvas px (1 voxel ~= 1 SHP px)


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def write_zip(path, name, frames):
    # Launcher contract: virtual-canvas-CENTER anchoring; center-symmetric
    # crops keep both anchoring interpretations coincident (walkers recipe).
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
    print(f"wrote {path} ({len(frames)} frames)")


def safe_paste(dst, src, x, y):
    """Pillow negative-offset RGBA-mask paste corrupts output -- pre-crop."""
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy:
        src = src.crop((sx, sy, src.width, src.height))
        x, y = max(0, x), max(0, y)
    dst.paste(src, (x, y), src)


def drop_shadow(frame, dx, dy, alpha=130):
    sil = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    mask = frame.split()[3].point(lambda a: alpha if a > 0 else 0)
    black = Image.new("RGBA", frame.size, (0, 0, 0, 255))
    sil.paste(black, (dx, dy), mask)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.alpha_composite(sil)
    out.alpha_composite(frame)
    return out


def crisp_place(img, factor, canvas, anchor_src, anchor_dst):
    """hq4x upscale then LANCZOS; anchor_src (source px) lands at anchor_dst."""
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


def vox_frames(dirname, canvas, count=32, shadow=None, scale=1.0):
    """Model-space placement: each render canvas (center = voxel origin)
    scaled by F_VOX and centered -- the launcher anchors the canvas center at
    the draw position, so the model rides where the voxel data puts it
    (the TSHVR recipe; content-bbox centering sank the MLRS rack)."""
    out = []
    clipped = 0
    for i in range(count):
        im = Image.open(f"{ART}/{dirname}/frame-{i:04d}.png").convert("RGBA")
        f = F_VOX * scale
        scaled = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
        fr = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
        ox, oy = round(canvas / 2 - scaled.width / 2), round(canvas / 2 - scaled.height / 2)
        b = scaled.getbbox()
        if b and (ox + b[0] < 0 or oy + b[1] < 0 or ox + b[2] > canvas or oy + b[3] > canvas):
            clipped += 1
        safe_paste(fr, scaled, ox, oy)
        if shadow:
            fr = drop_shadow(fr, *shadow)
        out.append(fr)
    if clipped:
        print(f"  WARNING: {dirname}: content clipped on {clipped} frames -- grow the canvas")
    return out


# ---- TSHARV / TSAPC: plain 32-facing voxel bodies ----
# These renders start at EAST and advance CCW; RA frame space is 0=N CCW,
# so rotate by +8 (cardinal-verified 2026-08-04: without it the hull drives
# 90 degrees off its heading).
def face_fix(frames):
    return [frames[(i + 8) % 32] for i in range(32)]


def recenter_orbit(frames):
    """The HARV voxel model is origin-offset, so origin-at-centre placement
    makes the hull ORBIT the front cab across facings instead of turning in
    place. Fit the per-facing bbox centres to c + (A cos t, B sin t) and
    shift each frame onto the fitted circle — smooth (no bbox-noise jitter,
    the MLRS trap) yet exactly rigid-body. Run scripts/ts_recenter_tsharv.py
    for the zip-level equivalent when render sources are absent."""
    import math
    n = len(frames)
    boxes = [f.getbbox() for f in frames]
    def fit(vals):
        a = sum(vals) / n
        b = sum(v * math.cos(2 * math.pi * i / n) for i, v in enumerate(vals)) * 2 / n
        c = sum(v * math.sin(2 * math.pi * i / n) for i, v in enumerate(vals)) * 2 / n
        return lambda i: a + b * math.cos(2 * math.pi * i / n) + c * math.sin(2 * math.pi * i / n)
    fx = fit([(b[0] + b[2]) / 2 for b in boxes])
    fy = fit([(b[1] + b[3]) / 2 for b in boxes])
    out = []
    for i, f in enumerate(frames):
        fr = Image.new("RGBA", f.size, (0, 0, 0, 0))
        safe_paste(fr, f, round(f.width / 2 - fx(i)), round(f.height / 2 - fy(i)))
        out.append(fr)
    return out
# TSHARV: recentred 384/ShapeSize 48 (the orbit fix pulls the rotation
# envelope back inside the 48-class canvas). Renders = vxl_render.py
# --elev 32 (Luke's angle pick, 2026-08-04 — the 54-default read top-down
# next to the TD harvester) and pack scale 0.75 (Luke, final size call 2026-08-05; 0.533 read ridiculously
# small in the field; 0.80 read big — Luke's split, 2026-08-05).
if os.path.isdir(f"{ART}/renders_harv"):
    write_zip(f"{UNITS_DIR}/TSHARV.ZIP", "tsharv",
              recenter_orbit(face_fix(vox_frames("renders_harv", 384, shadow=(10, 13), scale=0.75))))
else:
    print("TSHARV: SKIP (no renders_harv)")
if os.path.isdir(f"{ART}/renders_apc"):
    write_zip(f"{UNITS_DIR}/TSAPC.ZIP", "tsapc", face_fix(vox_frames("renders_apc", 384, shadow=(10, 13))))
else:
    print("TSAPC: SKIP (no renders_apc)")

# ---- TSSONIC: body 0-31 + turret 32-63, one shared scale ----
if os.path.isdir(f"{ART}/renders_sonic"):
    sonic = vox_frames("renders_sonic", 448, shadow=(12, 15))
    sonic += vox_frames("renders_sonictur", 448)  # turret: no shadow, canvas-centered
    write_zip(f"{UNITS_DIR}/TSSONIC.ZIP", "tssonic", sonic)
else:
    print("TSSONIC: SKIP (no renders_sonic)")

# ---- TSSMEC: SHP walker, 12-step walk x 8 facings ----
# SMECH.SHP: walk 0-95 (12/facing, CW facing blocks, 0=N), standing 96-103,
# firing 104-135, shadows 136-271 (unused). Engine frame space is CCW 0=N:
# out facing f <- src block (8-f)%8 (the MMCH reorder).
CANVAS_S = 384
if os.path.isdir(f"{ART}/shp_smech"):
    sm = lambda i: Image.open(f"{ART}/shp_smech/frame-{i:04d}.png").convert("RGBA")
    ux0, uy0, ux1, uy1 = 1e9, 1e9, -1e9, -1e9
    for i in range(96):
        b = sm(i).getbbox()
        if b:
            ux0, uy0 = min(ux0, b[0]), min(uy0, b[1])
            ux1, uy1 = max(ux1, b[2]), max(uy1, b[3])
    # Feet-row anchoring (no per-frame bob jitter): union feet row lands so the
    # union content box centers on the canvas center.
    feet_src = uy1
    content_h = (uy1 - uy0) * F_SHP
    feet_dst = CANVAS_S / 2 + content_h / 2
    frames = []
    for f in range(8):
        src_block = (8 - f) % 8
        for s in range(12):
            fr = crisp_place(sm(src_block * 12 + s), F_SHP, CANVAS_S,
                             (47.5, feet_src), (CANVAS_S / 2, feet_dst))
            frames.append(drop_shadow(fr, 12, 15))
    write_zip(f"{UNITS_DIR}/TSSMEC.ZIP", "tssmec", frames)
else:
    print("TSSMEC: SKIP (no shp_smech)")

# ---- BuildIcons (CAMEO.PAL decodes) ----
if os.path.exists(f"{ART}/CAMEO.PAL"):
    pal = ts_shp.load_pal(f"{ART}/CAMEO.PAL")
    for shp, out in [("HARVICON", "BuildIcon_TS_Harvester"),
                     ("SMCHICON", "BuildIcon_TS_Wolverine"),
                     ("SONIICON", "BuildIcon_TS_Disruptor"),
                     ("APCICON", "BuildIcon_TS_AmphAPC")]:
        if not os.path.exists(f"{ART}/{shp}.SHP"):
            print(f"{shp}: SKIP (absent)")
            continue
        size, frs = ts_shp.decode_shp(f"{ART}/{shp}.SHP")
        icon = ts_shp.frame_to_rgba(frs[0], pal, (16, 31), (0, 200, 0))
        big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
        big.save(f"{ICON_DIR}/{out}.tga")
        print(f"wrote {ICON_DIR}/{out}.tga")

# ---- Tileset XML (replace-capable) ----
def tile_block(name, shape, frame_path):
    return ("\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n"
            "\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n"
            % (name, shape, frame_path))

def patch_tileset(xml_path, name, count):
    sub = name.lower()
    xml = open(xml_path, encoding="utf-8").read()
    xml = re.sub(
        r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?",
        "", xml, flags=re.S)
    blocks = "".join(tile_block(name, s, f"{sub}\\{sub}-{s:04d}.tga") for s in range(count))
    idx = xml.rindex("</Tiles>")
    xml = xml[:idx] + blocks + xml[idx:]
    open(xml_path, "w", encoding="utf-8").write(xml)
    print(f"patched {os.path.basename(xml_path)}: {name} -> {count} tiles")

patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSHARV", 32)
patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSSMEC", 96)
patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSSONIC", 64)
patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSAPC", 32)

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
for ini, icon in [("TSHARV", "BuildIcon_TS_Harvester"), ("TSSMEC", "BuildIcon_TS_Wolverine"),
                  ("TSSONIC", "BuildIcon_TS_Disruptor"), ("TSAPC", "BuildIcon_TS_AmphAPC")]:
    if f"RA_{ini}" not in xml:
        added += buildable(f"RA_{ini}", f"TEXT_UNIT_{ini}", icon)
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
    ('TEXT_UNIT_TSHARV', 'Harvester'),
    ('TEXT_UNIT_TSHARV_DESC', 'Tiberium harvester.'),
    ('TEXT_UNIT_TSSMEC', 'Wolverine'),
    ('TEXT_UNIT_TSSMEC_DESC', 'Light scout mech.'),
    ('TEXT_UNIT_TSSONIC', 'Disruptor'),
    ('TEXT_UNIT_TSSONIC_DESC', 'Sonic beam tank.'),
    ('TEXT_UNIT_TSAPC', 'Amphibious APC'),
    ('TEXT_UNIT_TSAPC_DESC', 'Amphibious armored personnel carrier.'),
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
