#!/usr/bin/env python3
"""Package TS GDI tree art into the mod tree (docs/ts-gdi-tree-plan.md §Stealth Recipe).

Per-building compositor: healthy run = base + active anims cycling (N = LCM of
anim lengths; TS anim SHPs carry N real frames + N EMPTY frames — damaged
buildings stop animating), damaged run = static damaged composite x N. One
affine per building (union content box -> scaled to the TD counterpart's
content size, centered on the donor-derived canvas). Buildup ships real frames
only (empties render as the launcher's purple placeholder), resampled to the
donor's construction-anim count.

Inputs: $TS_ART_DIR holding shp_* dirs from ts_shp.py + renders_* from
vxl_render.py.
"""
import io, json, math, os, zipfile
from PIL import Image
import hqx

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR")
MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources/remaster_mods/Vanilla_RA"))
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
STRUCT_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES"
ICON_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB"


def load(dirname, i):
    return Image.open(f"{ART}/{dirname}/frame-{i:04d}.png").convert("RGBA")


def frame_count(dirname):
    return len([f for f in os.listdir(f"{ART}/{dirname}") if f.endswith(".png")])


def real_frames(dirname):
    """Indices of frames with substantive content (skips empties/fragments)."""
    out = []
    for i in range(frame_count(dirname)):
        im = load(dirname, i)
        n = sum(1 for p in im.getdata() if p[3] > 0)
        if n > 800:
            out.append(i)
    return out


def anim_len(dirname):
    """Usable loop length: TS anim SHPs are N real + N empty frames."""
    n = 0
    for i in range(frame_count(dirname)):
        if load(dirname, i).getbbox() is not None:
            n = i + 1
    return n


def composite(base_img, anims, i):
    out = base_img.copy()
    for dirname, length in anims:
        f = load(dirname, i % length)
        out.paste(f, (0, 0), f)
    return out


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def hq_scale(img, factor):
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    up = hqx.hq4x(rgb)
    w, h = round(img.width * factor), round(img.height * factor)
    color = up.resize((w, h), Image.LANCZOS)
    alpha = img.split()[3].resize((img.width * 8, img.height * 8), Image.NEAREST).resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(color, (0, 0))
    out.putalpha(alpha.point(lambda a: 255 if a >= 128 else 0))
    return out


def place(img, factor, canvas_w, canvas_h, src_cx, src_cy):
    """Apply the building's single affine: hq-scale, then position so the
    (pre-scale) anchor point lands at the canvas center."""
    scaled = hq_scale(img, factor)
    out = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    ox = round(canvas_w / 2 - src_cx * factor)
    oy = round(canvas_h / 2 - src_cy * factor)
    src = scaled
    x0, y0 = max(0, -ox), max(0, -oy)
    if x0 or y0:
        src = scaled.crop((x0, y0, scaled.width, scaled.height))
        ox, oy = max(0, ox), max(0, oy)
    out.paste(src, (ox, oy), src)
    return out


def write_zip(path, name, frames):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            b = img.getbbox() or (0, 0, img.width, img.height)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps(
                {"size": [img.width, img.height], "crop": [b[0], b[1], b[2], b[3]]}))
    print(f"wrote {path} ({len(frames)} frames)")


def tile_block(name, shape):
    return ("\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n"
            "\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s\\%s-%04d.tga</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n"
            % (name, shape, name.lower(), name.lower(), shape))


def patch_tileset(xml_path, name, count):
    """Install exactly `count` tile entries for `name`, replacing any existing run."""
    import re
    xml = open(xml_path, encoding="utf-8").read()
    pat = re.compile(r"\t<Tile>\n\t\t<Key>\n\t\t\t<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n", re.S)
    xml, removed = pat.subn("", xml)
    blocks = "".join(tile_block(name, s) for s in range(count))
    idx = xml.rindex("</Tiles>")
    xml = xml[:idx] + blocks + xml[idx:]
    open(xml_path, "w", encoding="utf-8").write(xml)
    print(f"patched {os.path.basename(xml_path)}: {name} -> {count} tiles (replaced {removed})")


def resample(indices, target):
    return [indices[min(len(indices) - 1, round(i * (len(indices) - 1) / (target - 1)))] for i in range(target)]


def build_structure(ini, base_dir, healthy_f, damaged_f, anims, mk_dir, mk_count,
                    canvas_w, canvas_h, target_w):
    """The Stealth Recipe compositor. anims = [(dirname, loop_len), ...]."""
    n = 1
    for _, ln in anims:
        n = n * ln // math.gcd(n, ln)
    base_h = load(base_dir, healthy_f)
    base_d = load(base_dir, damaged_f)

    # Damaged run keeps the anims cycling over the damaged base — TS itself
    # freezes damaged buildings (the anim SHPs' damaged halves are empty),
    # but the mod's stealth-gen baseline animates damaged, and Luke prefers
    # that (2026-08-01).
    healthy = [composite(base_h, anims, i) for i in range(n)]
    damaged_frames = [composite(base_d, anims, i) for i in range(n)]

    # One affine for every frame, keyed to the HEALTHY BASE content only:
    # buildup scaffolding is often wider than the finished building, and a
    # union-box scale shrinks the built state to make room for it (the
    # "powerplant needs beefing up" bug). Base-keyed scale + base-centered
    # anchor keeps registration (all frames share the source canvas); MK
    # frames that overflow the canvas clip harmlessly in place().
    bb = base_h.getbbox()
    factor = float(target_w) / (bb[2] - bb[0])
    cx, cy = (bb[0] + bb[2]) / 2.0, (bb[1] + bb[3]) / 2.0

    frames = [place(f, factor, canvas_w, canvas_h, cx, cy) for f in healthy]
    frames += [place(f, factor, canvas_w, canvas_h, cx, cy) for f in damaged_frames]
    write_zip(f"{STRUCT_DIR}/{ini}.ZIP", ini.lower(), frames)

    mk = [place(load(mk_dir, i), factor, canvas_w, canvas_h, cx, cy)
          for i in resample(real_frames(mk_dir), mk_count)]
    write_zip(f"{STRUCT_DIR}/{ini}MAKE.ZIP", f"{ini.lower()}make", mk)

    patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", ini, 2 * n)
    patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", f"{ini}MAKE", mk_count)
    print(f"{ini}: N={n} (idle anim count for the _anims[] entry)")
    return n


# ---- TSFACT: TS Construction Yard (3x2, TDFACT donor 72x48 -> 384x256).
# Content scaled to the TD yard (TDGFACT content 381px). Anims: _A crane 20,
# _B light 10, _C crane-2 30 -> N=60. Damaged base = GTCNST frame 1.
if os.path.isdir(f"{ART}/shp_gtcnst"):
    build_structure("TSFACT", "shp_gtcnst", 0, 1,
                    [("shp_gtcnst_a", anim_len("shp_gtcnst_a")),
                     ("shp_gtcnst_b", anim_len("shp_gtcnst_b")),
                     ("shp_gtcnst_c", anim_len("shp_gtcnst_c"))],
                    "shp_gtcnstmk", 32, 384, 256, 381)

# ---- TSPOWR: TS Power Plant (2x2, POWR donor 48x48 -> 256x256).
# Content scaled to TDNUKE (content 256 full-width). Anims: _A fan 24, _B 12
# -> N=24. Damaged base = GTPOWR frame 2 (spike-established layout).
if os.path.isdir(f"{ART}/shp_gtpowr"):
    build_structure("TSPOWR", "shp_gtpowr", 0, 2,
                    [("shp_gtpowr_a", anim_len("shp_gtpowr_a")),
                     ("shp_gtpowr_b", anim_len("shp_gtpowr_b"))],
                    "shp_gtpowrmk", 13, 256, 256, 252)

# ---- TSMCV (MCV.VXL render, 32 facings, canvas 384 = classic 48 x 8) ----
if os.path.isdir(f"{ART}/renders_tsmcv") and not os.path.exists(f"{UNITS_DIR}/TSMCV.ZIP"):
    def scale_center(img, factor, canvas):
        nw, nh = round(img.width * factor), round(img.height * factor)
        scaled = img.resize((nw, nh), Image.LANCZOS)
        out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
        out.paste(scaled, ((canvas - nw) // 2, (canvas - nh) // 2), scaled)
        return out
    side = Image.open(f"{ART}/renders_tsmcv/frame-0008.png")
    b = side.getbbox()
    factor = 280.0 / (b[2] - b[0])
    frames = [scale_center(Image.open(f"{ART}/renders_tsmcv/frame-{i:04d}.png"), factor, 384)
              for i in range(32)]
    write_zip(f"{UNITS_DIR}/TSMCV.ZIP", "tsmcv", frames)
    patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML", "TSMCV", 32)

# ---- BuildIcon for the (future-buildable) TSMCV ----
if os.path.isdir(f"{ART}/shp_mcvicon") and not os.path.exists(f"{ICON_DIR}/BuildIcon_TS_MCV.tga"):
    icon = Image.open(f"{ART}/shp_mcvicon/frame-0000.png")
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(f"{ICON_DIR}/BuildIcon_TS_MCV.tga")
    print(f"wrote {ICON_DIR}/BuildIcon_TS_MCV.tga")

print("DONE")
