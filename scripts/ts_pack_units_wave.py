#!/usr/bin/env python3
"""Package the TS units wave (TSSONIC / TSAPC, and the cameos of TSHARV and TSSMEC, whose art is
the HD rebuilds' in scripts/ts_pack_hd_buildings.py) into the mod tree:
  - TSSONIC.ZIP  64 frames (body 0-31 + turret 32-63, TSHVR layout), 448 canvas, ShapeSize 56
  - TSAPC.ZIP    32 frames (voxel body facings), 384 canvas, ShapeSize 48
  - BuildIcon_TS_{Harvester,Wolverine,Disruptor,AmphAPC}.tga (TS cameos, CAMEO.PAL)
  - TS_UNITS.XML tile runs (REPLACING any existing entries), TSBUILDABLES.XML, ModText.csv
Art, cameos and XML go to the tree asset_packs.py routes each name to (the TS-Graphics-Pack).

Density: all TS units ship at 8x-classic (canvas = ShapeSize * 8). 1 TS voxel at
12 px/voxel ~= 1 TS SHP px * 6.4 (the Titan F_T), so voxel renders scale by
6.4/12 and SHP frames by 6.4 -- every unit lands TS-relative-size-consistent.

Inputs (set TS_ART_DIR to the extraction dir):
  $TS_ART_DIR/renders_apc|renders_sonic|renders_sonictur/frame-NNNN.png
      (scripts/vxl_render.py at --px-per-voxel 12, 32 frames)
  $TS_ART_DIR/{HARVICON,SMCHICON,SONIICON,APCICON}.SHP + CAMEO.PAL
"""
import io, json, os, re, sys, zipfile
from PIL import Image

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the extracted/rendered TS art directory")
# Mod tree relative to this script's repo checkout (worktree-safe; never a
# hardcoded absolute repo path -- the parallel-instance rule).
MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources", "remaster_mods", "Vanilla_RA"))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs
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


# AFTER ANY REPACK, RUN scripts/ts_reshadow.py. It owns the shadow convention
# (EA's TD/RA baked offset-silhouette: dx = 0.028*w, dy = 0.120*w, alpha 191)
# and it strips whatever shadow is here before applying its own, so it is the
# authoritative pass and it corrects any dilution a later resize introduces
# (that dilution is exactly how TSHARV ended up at alpha 66, under the
# launcher's ~128 cutoff, rendering no shadow at all). The offsets below are
# kept in step with it so a fresh pack already looks close.
def drop_shadow(frame, dx, dy, alpha=191):
    sil = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    mask = frame.split()[3].point(lambda a: alpha if a > 0 else 0)
    black = Image.new("RGBA", frame.size, (0, 0, 0, 255))
    sil.paste(black, (dx, dy), mask)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.alpha_composite(sil)
    out.alpha_composite(frame)
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


# ---- TSAPC: a plain 32-facing voxel body ----
# These renders start at EAST and advance CCW; RA frame space is 0=N CCW,
# so rotate by +8 (cardinal-verified 2026-08-04: without it the hull drives
# 90 degrees off its heading).
def face_fix(frames):
    return [frames[(i + 8) % 32] for i in range(32)]

if os.path.isdir(f"{ART}/renders_apc"):
    write_zip(asset_packs.art_zip("TSAPC", "UNITS"), "tsapc", face_fix(vox_frames("renders_apc", 384, shadow=(7, 30))))
else:
    print("TSAPC: SKIP (no renders_apc)")

# ---- TSSONIC: body 0-31 + turret 32-63, one shared scale ----
if os.path.isdir(f"{ART}/renders_sonic"):
    sonic = vox_frames("renders_sonic", 448, shadow=(8, 36))
    # Turret: no shadow, canvas-centered, same frame order as the body.
    tur = vox_frames("renders_sonictur", 448)
    sonic += tur  # turret renders line up with the hull renders index-for-index (facing sheet, 2026-08-25)
    write_zip(asset_packs.art_zip("TSSONIC", "UNITS"), "tssonic", sonic)
else:
    print("TSSONIC: SKIP (no renders_sonic)")

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
        big.save(asset_packs.cameo_tga(out))
        print(f"wrote {asset_packs.cameo_tga(out)}")

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

patch_tileset(asset_packs.tileset_xml("TSSONIC", "UNITS"), "TSSONIC", 64)
patch_tileset(asset_packs.tileset_xml("TSAPC", "UNITS"), "TSAPC", 32)

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
for ini, icon in [("TSHARV", "BuildIcon_TS_Harvester"), ("TSSMEC", "BuildIcon_TS_Wolverine"),
                  ("TSSONIC", "BuildIcon_TS_Disruptor"), ("TSAPC", "BuildIcon_TS_AmphAPC")]:
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
