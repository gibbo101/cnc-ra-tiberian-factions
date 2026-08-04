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
    """Indices of frames with substantive content. TS buildup SHPs carry the
    real run, then EMPTY frames, then debris FRAGMENTS (GTCNSTMK: real 0-23,
    empty 24-31, fragments 32-47). The pixel-count floor drops the empties;
    the post-peak area cut drops the fragment tail (a fragment is a small
    corner piece appearing after the fully-built peak frame — shipping one
    made the radar buildup 'snap to a shard' at the end, 2026-08-03)."""
    counts = []
    for i in range(frame_count(dirname)):
        im = load(dirname, i)
        counts.append(sum(1 for p in im.getdata() if p[3] > 0))
    peak = max(counts)
    peak_i = counts.index(peak)
    out = []
    for i, n in enumerate(counts):
        if i > peak_i and n < peak * 2 // 5:
            break
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


def composite(base_img, anims, i, which):
    """anims = [(dirname, healthy_indices, damaged_indices), ...]; `which`
    selects the window (1=healthy, 2=damaged). Most TS anims only carry a
    healthy loop, but GTRADR_A packs a torn-dish damaged loop in its second
    half — cycling the right window per run keeps the healthy idle clean."""
    out = base_img.copy()
    for spec in anims:
        idx = spec[which]
        f = load(spec[0], idx[i % len(idx)])
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


def place(img, factor, canvas_w, canvas_h, src_cx, src_cy, dst_x=None, dst_y=None):
    """Apply the building's single affine: hq-scale, then position so the
    (pre-scale) anchor point lands at (dst_x, dst_y) — canvas center by
    default."""
    if dst_x is None:
        dst_x = canvas_w / 2
    if dst_y is None:
        dst_y = canvas_h / 2
    scaled = hq_scale(img, factor)
    out = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    ox = round(dst_x - src_cx * factor)
    oy = round(dst_y - src_cy * factor)
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
                    canvas_w, canvas_h, target_w=None, bib_dir=None,
                    bottom_margin=None, overscale=1.0, mk_mask_dir=None):
    """The Stealth Recipe compositor.
    anims = [(dirname, healthy_indices, damaged_indices), ...].
    Two fit modes:
    - legacy (target_w): base-keyed scale clamped to the canvas, union-centered.
    - size-pass (bottom_margin, classic px): scale = full canvas width for the
      composite union, union bottom anchored bottom_margin above the canvas
      bottom, x-centered. The launcher maps the canvas onto the classic stub
      box CENTERED on the BSIZE box (launcher-render-contracts rule 1 +
      CenterOffset geometry), so a stub taller than the box extends the art
      symmetrically — content placed low lands on the passable row below the
      plot (the TS apron row)."""
    n = 1
    for spec in anims:
        ln = len(spec[1])
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
    healthy = [composite(base_h, anims, i, 1) for i in range(n)]
    damaged_frames = [composite(base_d, anims, i, 2) for i in range(n)]

    boxes = [f.getbbox() for f in healthy + damaged_frames]
    boxes = [b for b in boxes if b]
    ux0, uy0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    ux1, uy1 = max(b[2] for b in boxes), max(b[3] for b in boxes)

    if bottom_margin is not None:
        # Size-pass fit: composite union spans the full canvas width, anchored
        # low. MK frames share the affine and may clip — harmless transients.
        # overscale > 1 trades the apron's side tips (clipped at the canvas
        # edge) for a beefier structure — the WF-vs-Titan mass fix.
        factor = float(canvas_w) / (ux1 - ux0) * overscale
        cx, cy = (ux0 + ux1) / 2.0, float(uy1)
        dst_x, dst_y = canvas_w / 2.0, canvas_h - bottom_margin * 16.0 / 3.0
    else:
        # One affine for every frame, keyed to the HEALTHY BASE content only:
        # buildup scaffolding is often wider than the finished building, and a
        # union-box scale shrinks the built state to make room for it (the
        # "powerplant needs beefing up" bug). Base-keyed scale + base-centered
        # anchor keeps registration (all frames share the source canvas); MK
        # frames that overflow the canvas clip harmlessly in place().
        # Clamp so the union of EVERYTHING drawn (anims can rise above the
        # base -- radar dish, barracks flag) still fits the canvas; anchor at
        # the union center so nothing clips. MK frames are EXCLUDED from the
        # fit: letting scaffolding drive the clamp shrinks the built state
        # (the TS-refinery-smaller-than-TD bug).
        bb = base_h.getbbox()
        factor = float(target_w) / (bb[2] - bb[0])
        factor = min(factor, float(canvas_w) / (ux1 - ux0), float(canvas_h) / (uy1 - uy0))
        cx, cy = (ux0 + ux1) / 2.0, (uy0 + uy1) / 2.0
        dst_x = dst_y = None

    frames = [place(f, factor, canvas_w, canvas_h, cx, cy, dst_x, dst_y) for f in healthy]
    frames += [place(f, factor, canvas_w, canvas_h, cx, cy, dst_x, dst_y) for f in damaged_frames]
    write_zip(f"{STRUCT_DIR}/{ini}.ZIP", ini.lower(), frames)

    # TS buildups pour the concrete pad first and keep it throughout; with
    # the pad dropped from the finished art (grid-sized buildings + RA slab),
    # mask the pad's silhouette (its *BB sprite, same source canvas) out of
    # every buildup frame or construction shows a pad that then vanishes.
    if mk_mask_dir is not None:
        from PIL import ImageChops
        msk = load(mk_mask_dir, 0)
        m2 = load(mk_mask_dir, 2)
        msk.paste(m2, (0, 0), m2)
        msk = msk.split()[3].point(lambda a: 255 if a > 0 else 0)

        def mk_load(i):
            img = load(mk_dir, i)
            img.putalpha(ImageChops.subtract(img.split()[3], msk))
            return img

        imgs = [mk_load(i) for i in range(frame_count(mk_dir))]
        counts = [sum(1 for p in im.getdata() if p[3] > 0) for im in imgs]
        peak = max(counts)
        peak_i = counts.index(peak)
        real = []
        for i, cnt2 in enumerate(counts):
            if i > peak_i and cnt2 < peak * 2 // 5:
                break
            if cnt2 > 800:
                real.append(i)
        mk = [place(imgs[i], factor, canvas_w, canvas_h, cx, cy, dst_x, dst_y)
              for i in resample(real, mk_count)]
    else:
        mk = [place(load(mk_dir, i), factor, canvas_w, canvas_h, cx, cy, dst_x, dst_y)
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


def loop(d):
    """TS anims pack HEALTHY frames then DAMAGED frames inside the usable
    window (radar dish, tech dome, depot pad, barracks flag all confirmed
    2026-08-03). Even count -> split halves; odd -> no damaged half, same
    window both runs."""
    ln = anim_len(d)
    if ln % 2 == 0:
        return (d, list(range(ln // 2)), list(range(ln // 2, ln)))
    idx = list(range(ln))
    return (d, idx, idx)


# ---- TS GDI tree wave 2: the legacy-fit buildings (size-pass buildings
# moved to SIZEPASS below) ----
# (ini, base_dir, anims_dirs, mk_dir, mk_count, canvas, target_w, cameo_dir, name, desc)
WAVE2 = [
    ("TSSILO", "shp_gtsilo", [],
     "shp_gtsilomk", 19, (256, 256), 250, "shp_siloicon", "TS Tiberium Silo", "Stores excess Tiberium."),
    ("TSHPAD", "shp_gthpad", ["shp_gthpad_a"],
     "shp_gthpadmk", 19, (256, 256), 256, "shp_heliicon", "TS Helipad", "Rearms Tiberian-era aircraft."),
    ("TSTECH", "shp_gttech", ["shp_gttech_a"],
     "shp_gttechmk", 19, (384, 256), 375, "shp_techicon", "TS Tech Center", "Unlocks advanced Tiberian technology."),
    ("TSDEPT", "shp_gtdept", ["shp_gtdept_a", "shp_gtdept_b"],
     "shp_gtdeptmk", 19, (384, 384), 382, "shp_fixicon", "TS Service Depot", "Repairs vehicles and aircraft."),
]

# TSPROC/TSWEAP apron plates dropped with the 3x3 conversion (2026-08-03
# late): structure-only composites fill the box, engine Bib=yes lays the RA
# slab like every other refinery/factory.
BIBS = {"TSHPAD": "shp_gthpadbb", "TSDEPT": "shp_gtdeptbb"}

for ini, base, anim_dirs, mk, mkc, (cw, ch), tw, cameo, disp, desc in WAVE2:
    if not os.path.isdir(f"{ART}/{base}"):
        print(f"{ini}: SKIP (no {base})")
        continue
    # Damaged base = frame 2: TS building SHPs are 0 healthy, 1 a healthy
    # VARIANT (WF door-open, radar mast), 2 damaged, 3-5 rubble fragments.
    build_structure(ini, base, 0, 2, [loop(d) for d in anim_dirs], mk, mkc, cw, ch, tw,
                    bib_dir=BIBS.get(ini))
    emit_sidebar_data(ini, disp, desc, cameo)

# ---- Size pass (2026-08-03, docs/ts-gdi-tree-plan.md top block): the four
# buildings Luke rejected as too small, rebuilt with taller classic stubs and
# the width-fit + bottom-anchor mode. Stubs (build_tfassets.sh) must match:
# TSPROC 72x72 (RA-refinery 3x3 geometry clone), TSWEAP 96x72 (TDWEAP-parity
# 3x3, hangar art overhangs the box sides), TSPILE 72x48 (2x2 plot, wide
# stub for mass), TSRADR 48x96 (Obelisk treatment: dish rises ~1 row over
# the 2x2 plot), TSFACT 96x72 (TS-authentic BSIZE_43).
# bottom_margin = classic px from canvas bottom up to the composite's bottom.
# (ini, base, anims, mk, mkc, canvas, bottom_margin, overscale, cameo, name, desc)
SIZEPASS = [
    # NTREFN_C is a 144-canvas anim on a 192x168 building; needs offset
    # compositing -- still deferred.
    ("TSPROC", "shp_ntrefn", ["shp_ntrefn_b"],
     "shp_ntrefnmk", 19, (512, 544), 0, 1.0, "shp_reficon",
     "TS Tiberium Refinery", "Processes Tiberium into credits."),
    ("TSWEAP", "shp_gtweap", ["shp_gtweap_a", "shp_gtweap_b", "shp_gtweap_c"],
     "shp_gtweapmk", 19, (512, 384), 2, 1.0, "shp_weapicon",
     "TS War Factory", "Produces Tiberian-era vehicles."),
    ("TSPILE", "shp_gtpile", ["shp_gtpile_a", "shp_gtpile_b", "shp_gtpile_c"],
     "shp_gtpilemk", 19, (320, 256), 0, 1.0, "shp_brrkicon",
     "TS Barracks", "Trains Tiberian-era infantry."),
    ("TSRADR", "shp_gtradr", ["shp_gtradr_a"],
     "shp_gtradrmk", 20, (384, 800), 48, 1.0, "shp_radricon",
     "TS Radar", "Provides radar coverage."),
]

for ini, base, anim_dirs, mk, mkc, (cw, ch), margin, oscale, cameo, disp, desc in SIZEPASS:
    if not os.path.isdir(f"{ART}/{base}"):
        print(f"{ini}: SKIP (no {base})")
        continue
    if ini == "TSRADR":
        # GTRADR_A packs 15 healthy rotation frames + 15 torn-dish damaged
        # frames in its 30-frame usable window (the engine's shapes-N..2N-1
        # damaged convention applied inside the anim SHP). Cycling all 30 as
        # the healthy idle was Luke's "broken animation". The 15 frames are
        # HALF a sweep (frame 14 = opposite extreme of frame 0), so bake the
        # return sweep too — forward + reverse = a seamless 28-frame ping-pong
        # (the TS dish scans back and forth; a plain loop teleports the dish).
        fwd, back = list(range(0, 15)), list(range(13, 0, -1))
        dfwd, dback = list(range(15, 30)), list(range(28, 15, -1))
        anims = [("shp_gtradr_a", fwd + back, dfwd + dback)]
    else:
        anims = [loop(d) for d in anim_dirs]
    masks = {"TSPROC": "shp_ntrefnbb", "TSWEAP": "shp_gtweapbb"}
    build_structure(ini, base, 0, 2, anims, mk, mkc, cw, ch,
                    bib_dir=BIBS.get(ini), bottom_margin=margin, overscale=oscale,
                    mk_mask_dir=masks.get(ini))
    emit_sidebar_data(ini, disp, desc, cameo)

# ---- TSFACT: TS Construction Yard, size pass: TS-authentic 4x3 (BSIZE_43,
# stub 96x72 = the full 3-row box; content fits inside it, no halo needed).
# Anims: _A crane 20, _B light 10, _C crane-2 30 -> N=60. Damaged base =
# GTCNST frame 2.
if os.path.isdir(f"{ART}/shp_gtcnst"):
    # GTCNST_B (rotating light) breaks the healthy+damaged half convention:
    # its 10 content frames are ONE full rotation (equal 614px every frame,
    # continuous sweep) and its damaged form is the empty second half of the
    # SHP. Halving it played half a rotation + snap-back — the radar-dish
    # symptom. _A (crane) and _C (roof lights) halves ARE damaged variants.
    light = ("shp_gtcnst_b", list(range(10)), list(range(10)))
    # overscale 0.94: full grid width read "still slightly big" (Luke,
    # 2026-08-04) -- the hangar sits just inside the 4-cell plot.
    build_structure("TSFACT", "shp_gtcnst", 0, 2,
                    [loop("shp_gtcnst_a"), light, loop("shp_gtcnst_c")],
                    "shp_gtcnstmk", 32, 512, 384, bottom_margin=2,
                    overscale=0.94)

# ---- TSPOWR: TS Power Plant (2x2, POWR donor 48x48 -> 256x256).
# Content scaled to TDNUKE (content 256 full-width). Anims: _A fan 24, _B 12
# -> N=24. Damaged base = GTPOWR frame 2 (spike-established layout).
if os.path.isdir(f"{ART}/shp_gtpowr"):
    build_structure("TSPOWR", "shp_gtpowr", 0, 2,
                    [loop("shp_gtpowr_a"), loop("shp_gtpowr_b")],
                    "shp_gtpowrmk", 13, 256, 256, bottom_margin=0)

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
