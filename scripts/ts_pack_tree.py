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
                    canvas_w, canvas_h, target_w, bib_dir=None):
    """The Stealth Recipe compositor. anims = [(dirname, loop_len), ...]."""
    n = 1
    for _, ln in anims:
        n = n * ln // math.gcd(n, ln)
    base_h = load(base_dir, healthy_f)
    base_d = load(base_dir, damaged_f)
    if bib_dir is not None:
        # TS bib (concrete apron) is a separate *BB SHP drawn UNDER the
        # building -- the buildup includes it, so the built sprite must too.
        for base, bf in ((base_h, healthy_f), (base_d, damaged_f)):
            bib = load(bib_dir, bf)
            under = bib.copy()
            under.paste(base, (0, 0), base)
            base.paste(under, (0, 0))

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
    # Clamp so the union of EVERYTHING drawn (anims can rise above the base --
    # radar dish, barracks flag -- and MK scaffolds spread wider) still fits
    # the canvas; anchor at the union center so nothing clips.
    # MK frames are EXCLUDED from the fit: buildup scaffolding is wider than
    # the finished building, and letting it drive the clamp shrinks the built
    # state (the TS-refinery-smaller-than-TD bug). A transient buildup frame
    # clipping at the canvas edge is harmless; the built state must not.
    boxes = [f.getbbox() for f in healthy + damaged_frames]
    boxes = [b for b in boxes if b]
    ux0, uy0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    ux1, uy1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    factor = min(factor, float(canvas_w) / (ux1 - ux0), float(canvas_h) / (uy1 - uy0))
    cx, cy = (ux0 + ux1) / 2.0, (uy0 + uy1) / 2.0

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


def emit_sidebar_data(ini, display, desc, icon_dir):
    """BuildIcon TGA from the TS cameo + RABUILDABLES (name + pristine _0) +
    ModText rows. TS-tree entries are never faction-badged, so only _0 exists."""
    import re
    icon_name = f"BuildIcon_TS_{ini[2:].title()}"
    icon = Image.open(f"{ART}/{icon_dir}/frame-0000.png")
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(f"{ICON_DIR}/{icon_name}.tga")

    RAB = f"{MOD}/Data/XML/OBJECTS/UNITS/RABUILDABLES.XML"
    xml = open(RAB, encoding="utf-8").read()
    text_id = f"TEXT_STRUCTURE_{ini}"
    added = ""
    for key in (f"RA_{ini}", f"RA_{ini}_0"):
        if f'"{key}"' not in xml:
            added += ('\t<ObjectTypeClass Name="%s" Classification="CNCBuildableObject" CanInstantiate="False">\n'
                      "\t\t<CNCEncyclopediaComponent>\n"
                      "\t\t\t<ObjectNameTextID>%s</ObjectNameTextID>\n"
                      "\t\t\t<ObjectDescriptionTextID>%s_DESC</ObjectDescriptionTextID>\n"
                      "\t\t\t<BuildIcon>%s</BuildIcon>\n"
                      "\t\t</CNCEncyclopediaComponent>\n"
                      "\t</ObjectTypeClass>\n" % (key, text_id, text_id, icon_name))
    if added:
        idx = xml.rindex("</ObjectTypeClass>") + len("</ObjectTypeClass>")
        xml = xml[:idx] + "\n\n" + added.rstrip("\n") + xml[idx:]
        open(RAB, "w", encoding="utf-8").write(xml)

    CSV = f"{MOD}/Data/ModText.csv"
    raw = open(CSV, "rb").read()
    text = raw.decode("utf-16")
    eol = "\r\n" if "\r\n" in text else "\n"
    sample = next(l for l in text.splitlines() if l.startswith('"TEXT_UNIT_TDA10"'))
    tail = sample.split('"A-10 Warthog"', 1)[1]
    new = ""
    for key, val in ((text_id, display), (text_id + "_DESC", desc)):
        if f'"{key}"' not in text:
            new += f'"{key}",,,"{val}"{tail}{eol}'
    if new:
        if not text.endswith(eol):
            text += eol
        text += new
        open(CSV, "wb").write(text.encode("utf-16"))
    print(f"{ini}: sidebar data emitted ({icon_name})")


# ---- TS GDI tree wave 2: the eight production/economy buildings ----
# (ini, base_dir, anims_dirs, mk_dir, mk_count, canvas, target_w, cameo_dir, name, desc)
WAVE2 = [
    ("TSPILE", "shp_gtpile", ["shp_gtpile_a", "shp_gtpile_b", "shp_gtpile_c"],
     "shp_gtpilemk", 19, (256, 256), 256, "shp_brrkicon", "TS Barracks", "Trains Tiberian-era infantry."),
    ("TSPROC", "shp_ntrefn", ["shp_ntrefn_b"],  # NTREFN_C is a 144-canvas anim on a 192x168 building; needs offset compositing -- deferred
     "shp_ntrefnmk", 19, (384, 384), 384, "shp_reficon", "TS Tiberium Refinery", "Processes Tiberium into credits."),
    ("TSSILO", "shp_gtsilo", [],
     "shp_gtsilomk", 19, (256, 128), 250, "shp_siloicon", "TS Tiberium Silo", "Stores excess Tiberium."),
    ("TSWEAP", "shp_gtweap", ["shp_gtweap_a", "shp_gtweap_b", "shp_gtweap_c"],
     "shp_gtweapmk", 19, (384, 384), 376, "shp_weapicon", "TS War Factory", "Produces Tiberian-era vehicles."),
    ("TSRADR", "shp_gtradr", ["shp_gtradr_a"],
     "shp_gtradrmk", 20, (256, 256), 252, "shp_radricon", "TS Radar", "Provides radar coverage."),
    ("TSHPAD", "shp_gthpad", ["shp_gthpad_a"],
     "shp_gthpadmk", 19, (256, 256), 256, "shp_heliicon", "TS Helipad", "Rearms Tiberian-era aircraft."),
    ("TSTECH", "shp_gttech", ["shp_gttech_a"],
     "shp_gttechmk", 19, (256, 256), 251, "shp_techicon", "TS Tech Center", "Unlocks advanced Tiberian technology."),
    ("TSDEPT", "shp_gtdept", ["shp_gtdept_a", "shp_gtdept_b"],
     "shp_gtdeptmk", 19, (384, 384), 382, "shp_fixicon", "TS Service Depot", "Repairs vehicles and aircraft."),
]

BIBS = {"TSPROC": "shp_ntrefnbb", "TSWEAP": "shp_gtweapbb",
        "TSHPAD": "shp_gthpadbb", "TSDEPT": "shp_gtdeptbb"}

for ini, base, anim_dirs, mk, mkc, (cw, ch), tw, cameo, disp, desc in WAVE2:
    if not os.path.isdir(f"{ART}/{base}"):
        print(f"{ini}: SKIP (no {base})")
        continue
    anims = [(d, anim_len(d)) for d in anim_dirs]
    build_structure(ini, base, 0, 1, anims, mk, mkc, cw, ch, tw, bib_dir=BIBS.get(ini))
    emit_sidebar_data(ini, disp, desc, cameo)

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
