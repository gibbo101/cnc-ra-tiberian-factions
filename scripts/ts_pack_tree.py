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
import io, json, math, os, sys, zipfile
from PIL import Image, ImageChops, ImageDraw, ImageFilter
import hqx

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR")
MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources/remaster_mods/Vanilla_RA"))
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
STRUCT_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES"
ICON_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB"


SCRIPTS = os.path.dirname(os.path.abspath(__file__))
STUB_MANIFEST = f"{SCRIPTS}/ts_stub_dims.json"

# Classic stub dimensions each packed canvas requires, filled in as buildings
# are packed and written out at the end. The launcher maps a building's canvas
# onto the stub box, so a canvas that grows without its stub growing to match
# is drawn at the wrong scale -- silently, with nothing else looking wrong.
# build_tfassets.sh checks its stub literals against this file.
STUB_DIMS = {}
CANVAS_PER_CLASSIC_PX = 16.0 / 3.0


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
        # TS draws building anims SHAPE_CENTER on the building: an anim SHP on
        # a smaller canvas than the base (NTREFN_C 144x144 on 192x168) sits
        # centred, not at the corner.
        out.paste(f, ((out.width - f.width) // 2, (out.height - f.height) // 2), f)
    return out


def centre_on(img, size):
    """img centred on a transparent canvas of `size` (TS SHAPE_CENTER)."""
    if img.size == tuple(size):
        return img
    out = Image.new("RGBA", tuple(size), (0, 0, 0, 0))
    out.paste(img, ((size[0] - img.width) // 2, (size[1] - img.height) // 2), img)
    return out


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def bake_hazard_gold(img):
    """Burn TS's hazard stripes to their final gold, in place of the launcher.

    The stripes are drawn in TS's house-REMAP range, so they arrive raw green.
    Ground art is never remapped and building art always is, which puts the
    apron's stripes and the ramp's on two different colour paths -- they meet
    at the door-to-pad junction and do not match. Baking both to the gold the
    launcher itself produces from that ramp, (v, 0.82v, 0) measured off a
    rendered frame, takes the launcher out of it and they join up.

    The green ramp runs 36..200 in eleven steps. An earlier cut at g > 70
    dropped the darkest three, which is what banded the stripes yellow and
    green; 30 takes the lot while still ignoring the olive-brown hull.

    Hazard markings are a fixed yellow in TS whoever owns the building, so a
    baked colour costs nothing."""
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and g > 30 and g > r * 1.6 and g > b * 1.6:
                px[x, y] = (g, round(g * 0.82), 0, a)
    return img


def bleed_edges(img, rounds=3):
    """Extend the sprite's colour outwards into its transparent margin.

    hq4x and LANCZOS both mix in whatever colour sits beside a pixel, and a
    transparent margin left at black drags every alpha edge towards black. On
    a whole sprite that is a faint dark rim nobody notices; along a seam where
    two layers of one building meet, the two rims add up and read as a drawn
    black line. Filling the margin with the neighbouring colour first means
    the interpolation has nothing dark to find. Alpha is untouched -- these
    pixels stay invisible, they only stop poisoning their neighbours."""
    import numpy as np
    a = np.array(img)
    rgb = a[:, :, :3].astype(np.float32)
    solid = a[:, :, 3] > 0
    for _ in range(rounds):
        acc = np.zeros_like(rgb)
        cnt = np.zeros(solid.shape, np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                m = np.roll(np.roll(solid, dy, 0), dx, 1)
                v = np.roll(np.roll(rgb, dy, 0), dx, 1)
                acc += v * m[:, :, None]
                cnt += m
        grow = (~solid) & (cnt > 0)
        rgb[grow] = (acc[grow] / cnt[grow][:, None])
        solid = solid | grow
    out = a.copy()
    out[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    return Image.fromarray(out)


# Per-building upscale mode (default "hq4x-hard", the tree's shipped look):
#   hq4x-hard  hq4x edge reconstruction, Lanczos to size, 1-bit alpha.
#   hq4x-soft  same colour path, Lanczos-resampled (soft) alpha.
#   lanczos    plain Lanczos colour + soft alpha: the smooth, filtered look
#              of TS at native pixels (Luke's TS-refinery screencast, 08-28).
#   lanczos-hard  Lanczos colour, 1-bit alpha: a soft silhouette over snow
#              reads as a pale outline on a dark building (08-28 SS), so the
#              edge stays hard and only the interior is smoothed.
SCALER_MODE = {"TSPROC": "lanczos-hard"}
CURRENT_INI = [None]


def hq_scale(img, factor):
    mode = SCALER_MODE.get(CURRENT_INI[0], "hq4x-hard")
    img = bleed_edges(img)
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img.convert("RGB"), (0, 0))
    w, h = round(img.width * factor), round(img.height * factor)
    if mode.startswith("lanczos"):
        color = rgb.resize((w, h), Image.LANCZOS)
    else:
        color = hqx.hq4x(rgb).resize((w, h), Image.LANCZOS)
    alpha = img.split()[3].resize((img.width * 8, img.height * 8), Image.NEAREST).resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(color, (0, 0))
    if mode.endswith("-hard"):
        alpha = alpha.point(lambda a: 255 if a >= 128 else 0)
    out.putalpha(alpha)
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


_EMBLEM_CACHE = {}


def stamp_emblem(img, path, frac, squash, dx=0, dy=0, ref=None):
    """Paint a flat emblem onto a finished frame, centred on its content.

    Applied AFTER the building's affine: at source resolution the artwork is
    only ~45 px across and the hq upscale destroys it, so it has to meet the
    canvas at full size. The squash is what makes it read as painted on the
    deck rather than standing up facing the camera -- it is the isometric
    projection of a flat disc, matching the pad's own ratio.

    ref, when given, is the HEALTHY frame and marks img as a damaged frame:
    geometry comes from ref (the damaged content box shrinks where edges are
    blown off, and re-deriving from it shrank and shifted the emblem), the
    emblem is erased wherever the deck itself is gone, and it chars wherever
    the deck burned (darker-than-healthy = scorch, carried onto the paint).
    """
    if path not in _EMBLEM_CACHE:
        src = Image.open(os.path.expanduser(path)).convert("RGBA")
        px = src.load()
        # The artwork ships on a black field with no alpha of its own.
        for y in range(src.height):
            for x in range(src.width):
                r, g, b, _ = px[x, y]
                if r + g + b < 60:
                    px[x, y] = (r, g, b, 0)
        _EMBLEM_CACHE[path] = src.crop(src.getbbox())
    em = _EMBLEM_CACHE[path]

    bb = (ref if ref is not None else img).getbbox()
    if bb is None:
        return img
    w = int(round((bb[2] - bb[0]) * frac))
    h = max(1, int(round(w / squash)))
    # dx/dy are eye-dial offsets in canvas pixels: bbox-centring is only the
    # starting point (the bbox includes the deck's skirt and shadow, so its
    # centre is not the visible face's centre).
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.alpha_composite(em.resize((w, h), Image.LANCZOS),
                          (bb[0] + ((bb[2] - bb[0]) - w) // 2 + dx,
                           bb[1] + ((bb[3] - bb[1]) - h) // 2 + dy))

    if ref is not None:
        # Scorch: where the damaged deck is darker than the healthy one, char
        # the emblem paint with it. The threshold ignores compression noise;
        # the x3 gain ramps real burns to full char quickly.
        burn = ImageChops.subtract(ref.convert("L"), img.convert("L"))
        burn = burn.point(lambda v: min(255, max(0, (v - 40) * 3)))
        char = Image.new("RGBA", img.size, (24, 18, 12, 255))
        char.putalpha(ImageChops.multiply(burn, layer.split()[3]))
        layer.alpha_composite(char)
        # No deck, no paint: clear the emblem over destroyed sections.
        layer.putalpha(ImageChops.multiply(layer.split()[3], img.split()[3]))

    out = img.copy()
    out.alpha_composite(layer)
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


# Every RA theatre's terrain tileset, and the texture folder its
# RootTexturePath points at. A TS apron is registered in all three: it is
# TERRAIN art, and terrain art is what the launcher draws on the ground.
TERRAIN_THEATRES = [("TEMPERATE", "RA_TERRAIN_TEMPERATE.XML"),
                    ("SNOW", "RA_TERRAIN_SNOW.XML"),
                    ("INTERIOR", "RA_TERRAIN_INTERIOR.XML")]

GAME_DATA = os.environ.get("CNC_REMASTER_DATA",
                           os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data"))


def ensure_tileset(xml_name):
    """Path to the mod's copy of a terrain tileset, extracting the vanilla one
    from CONFIG.MEG the first time. A mod tileset REPLACES the base file, so a
    theatre we want to add one tile to has to ship the whole thing."""
    import subprocess
    path = f"{MOD}/Data/XML/TILESETS/{xml_name}"
    if not os.path.exists(path):
        subprocess.run([sys.executable, f"{SCRIPTS}/meg_extract.py", "extract",
                        f"{GAME_DATA}/CONFIG.MEG", rf"DATA\XML\TILESETS\{xml_name}",
                        os.path.dirname(path)], check=True, stdout=subprocess.DEVNULL)
        print(f"extracted vanilla {xml_name} from CONFIG.MEG")
    return path


def resample(indices, target):
    return [indices[min(len(indices) - 1, round(i * (len(indices) - 1) / (target - 1)))] for i in range(target)]


def build_structure(ini, base_dir, healthy_f, damaged_f, anims, mk_dir, mk_count,
                    canvas_w, canvas_h, target_w=None, bib_dir=None,
                    bottom_margin=None, overscale=1.0, mk_mask_dir=None,
                    mk_clip_dir=None,
                    overlay_dir=None, fit_w=None, dst_x_px=None, door_spec=None,
                    apron_cells=None, front_ring=None, emblem=None,
                    apron_canvas=None, pingpong=False):
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
    CURRENT_INI[0] = ini
    STUB_DIMS[ini] = [round(canvas_w / CANVAS_PER_CLASSIC_PX), round(canvas_h / CANVAS_PER_CLASSIC_PX)]

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

    # The bay INTERIOR belongs to the base, the way TD's does. TS ships it as
    # UnderDoorAnim, which reads like an overlay, but it is the BACK of the
    # bay: a vehicle standing in the doorway is in front of it. Packed into
    # the overlay it sorts above that vehicle and swallows it the moment the
    # shutter stops hiding it. Only the shutter and the hangar's near face
    # belong above a unit.
    #
    # Clipped to the building's own outline: TS's under-door art carries the
    # whole bay surround, ramp and concrete included, and most of it falls
    # outside the building on ground the apron already draws.
    hangar_h, hangar_d = base_h.copy(), base_d.copy()
    if door_spec is not None:
        for run, base in enumerate((base_h, base_d)):
            interior = bake_hazard_gold(load(door_spec[1], run))
            interior.putalpha(ImageChops.multiply(
                interior.split()[3], base.split()[3].point(lambda v: 255 if v > 0 else 0)))
            base.paste(interior, (0, 0), interior)

    # Damaged run keeps the anims cycling over the damaged base — TS itself
    # freezes damaged buildings (the anim SHPs' damaged halves are empty),
    # but the mod's stealth-gen baseline animates damaged, and Luke prefers
    # that (2026-08-01).
    healthy = [composite(base_h, anims, i, 1) for i in range(n)]
    damaged_frames = [composite(base_d, anims, i, 2) for i in range(n)]

    if pingpong and n > 2:
        # Forward then reverse, the TSRADR treatment applied at the composite
        # level: the cycle reads as a sweep that returns instead of a loop
        # that jumps. Every downstream layer (base, lamps) inherits the same
        # order, so the Shape_Number index stays locked across them. The
        # _anims[] Count must match the new n.
        order = list(range(n)) + list(range(n - 2, 0, -1))
        healthy = [healthy[i] for i in order]
        damaged_frames = [damaged_frames[i] for i in order]
        n = len(order)

    boxes = [f.getbbox() for f in healthy + damaged_frames]
    boxes = [b for b in boxes if b]
    ux0, uy0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    ux1, uy1 = max(b[2] for b in boxes), max(b[3] for b in boxes)

    if bottom_margin is not None:
        # Size-pass fit: composite union spans the full canvas width, anchored
        # low. MK frames share the affine and may clip — harmless transients.
        # overscale > 1 trades the apron's side tips (clipped at the canvas
        # edge) for a beefier structure — the WF-vs-Titan mass fix.
        # fit_w decouples the building's width target from the canvas when
        # the canvas is widened to carry a ground overlay (TSPROC apron).
        factor = float(fit_w or canvas_w) / (ux1 - ux0) * overscale
        cx, cy = (ux0 + ux1) / 2.0, float(uy1)
        dst_x, dst_y = (dst_x_px or canvas_w / 2.0), canvas_h - bottom_margin * 16.0 / 3.0
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

    mk_pad_erase = None
    mk_building_sil = None

    if overlay_dir is not None and apron_cells is None:
        # Ground overlay (TS concrete apron / dock bay): drawn UNDER the
        # building but EXCLUDED from the fit, so it rides into the canvas
        # halo at the building's scale without inflating the building's
        # size read (the reason aprons were dropped in the first place).
        # Passability is untouched -- sprite pixels are not occupancy.
        for base, bf in ((base_h, healthy_f), (base_d, damaged_f)):
            ov = load(overlay_dir, bf)
            under = ov.copy()
            under.paste(base, (0, 0), base)
            base.paste(under, (0, 0))
        healthy = [composite(base_h, anims, i, 1) for i in range(n)]
        damaged_frames = [composite(base_d, anims, i, 2) for i in range(n)]

    if apron_cells is not None:
        # The apron as GROUND ART: sliced per plot cell into its own tileset
        # instead of being composited into the building sprite. Sprite pixels
        # sort against units and answer the launcher's hit-test, so an apron
        # inside the sprite swallows vehicles driving off it and cannot be
        # ordered onto; ground art does neither. The engine stamps it cell by
        # cell as SMUDGE_<INI>BB (sdata.cpp) and draws it on the overlay layer.
        #
        # Sliced through the BUILDING's affine, so the concrete lands exactly
        # where it did in the sprite. The launcher centres a building's canvas
        # on its BSIZE box, so the plot's north-west corner sits half the
        # canvas-minus-box overhang in from the canvas corner, and one cell is
        # 24 classic px of canvas.
        # The tile grid may be larger than the plot: TS concrete tapers a few
        # pixels past the plot edge, and a bib is allowed to lie outside the
        # footprint it belongs to. The grid must match the SmudgeTypeClass in
        # sdata.cpp, so the apron's real extent is checked against it here --
        # art that outgrows the grid is a silent clip otherwise.
        # The tile grid is offset from the plot's north-west corner as well as
        # sized, because the engine stamps EVERY cell of a smudge's rectangle
        # whether or not its tile carries art -- and a blank stamp overwrites
        # whatever smudge was on that cell, eating a neighbouring building's
        # bib. The grid must therefore hug the concrete, not the plot.
        (cols, rows), (grid_cols, grid_rows), (off_c, off_r) = apron_cells
        cell_px = 24.0 * CANVAS_PER_CLASSIC_PX
        left = (canvas_w - cols * cell_px) / 2.0
        top = (canvas_h - rows * cell_px) / 2.0
        if abs(left - round(left)) > 1e-6 or abs(top - round(top)) > 1e-6:
            raise SystemExit(f"{ini}: apron plot origin ({left},{top}) is not a whole pixel")
        left, top, cell_px = round(left), round(top), round(cell_px)
        # The apron's hazard stripes are drawn in TS's house-REMAP range (raw
        # green in the source art). The launcher remaps building sprites and
        # leaves ground art alone, so those stripes have to carry their final
        # colour here or they render green. Baked to the gold the launcher
        # itself produces from that ramp, measured off a rendered frame:
        # value preserved, (v, 0.82v, 0). Hazard markings are a fixed yellow in
        # TS whoever owns the building, so a baked colour is no loss.
        src = bake_hazard_gold(load(overlay_dir, healthy_f))
        # The apron is terrain art with thin curb lines: hq4x keeps them crisp
        # where Lanczos smears them into a visible rim, so it always takes the
        # default scaler whatever the building itself uses.
        saved_ini = CURRENT_INI[0]
        CURRENT_INI[0] = None
        apron = place(src, factor, canvas_w, canvas_h, cx, cy, dst_x, dst_y)
        CURRENT_INI[0] = saved_ini
        if apron_canvas is not None:
            # Hand-authored pad: a canvas-space RGBA in FINAL position (grid
            # colours and hazard gold already baked) replaces the affine'd
            # source. The affine'd original still defines, together with the
            # new pad, the region erased from the buildup frames below: the
            # ground tiles draw beneath the buildup sprite from placement, so
            # a buildup carrying NO pad pixels of its own hands off to the
            # built state with nothing to jump.
            mk_pad_erase = apron.split()[3].point(lambda v: 255 if v > 0 else 0)
            apron = Image.open(apron_canvas).convert("RGBA")
            if apron.size != (canvas_w, canvas_h):
                raise SystemExit(f"{ini}: apron canvas {apron.size} != canvas "
                                 f"{(canvas_w, canvas_h)}")
            mk_pad_erase = ImageChops.lighter(
                mk_pad_erase, apron.split()[3].point(lambda v: 255 if v > 0 else 0))
        gx, gy = left + off_c * cell_px, top + off_r * cell_px
        if ini in globals().get("APRON_CLIP", set()):
            clipped = Image.new("RGBA", apron.size, (0, 0, 0, 0))
            rect = apron.crop((gx, gy, gx + grid_cols * cell_px, gy + grid_rows * cell_px))
            clipped.paste(rect, (gx, gy))
            apron = clipped
        bb = apron.getbbox()
        if bb and (bb[0] < gx or bb[1] < gy
                   or bb[2] > gx + grid_cols * cell_px or bb[3] > gy + grid_rows * cell_px):
            raise SystemExit(
                f"{ini}: apron spans {bb} but the {grid_cols}x{grid_rows} tile grid at cell offset "
                f"({off_c},{off_r}) covers "
                f"{(gx, gy, gx + grid_cols * cell_px, gy + grid_rows * cell_px)}. "
                f"Move or grow the grid here, the SmudgeTypeClass in sdata.cpp and the "
                f"Bib_And_Offset offset in bdata.cpp together.")
        # Every emitted tile costs a stamped cell, so warn on any that is blank:
        # it is a cell taken off a neighbour for nothing.
        tiles = []
        blank = 0
        for r in range(grid_rows):
            for c in range(grid_cols):
                x, y = gx + c * cell_px, gy + r * cell_px
                t = apron.crop((x, y, x + cell_px, y + cell_px))
                if t.getbbox() is None:
                    blank += 1
                tiles.append(t)
        if blank:
            print(f"{ini}: WARNING {blank}/{len(tiles)} apron tiles are blank and will still "
                  f"stamp (overwriting neighbours' bibs) -- tighten the grid")
        # Registered as TERRAIN, in every theatre. The launcher decides what
        # goes on the ground from the entry's IsTheaterShape flag, and a
        # theatre shape is resolved out of RA_TERRAIN_<theatre>; ship it as a
        # structure instead and it renders in the sorted sprite pass, where it
        # draws over a vehicle standing on it. Concrete looks the same in every
        # theatre, so all three get the same art.
        for theatre, xml_name in TERRAIN_THEATRES:
            tex_dir = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/TERRAIN/{theatre}"
            os.makedirs(tex_dir, exist_ok=True)
            write_zip(f"{tex_dir}/{ini}BB.ZIP", f"{ini.lower()}bb", tiles)
            patch_tileset(ensure_tileset(xml_name), f"{ini}BB", len(tiles))
        # A same-named structure tile would shadow the terrain one.
        patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", f"{ini}BB", 0)

    # THE BAY FRONT PIECE. Tiberian Sun resolves occlusion with a per-pixel
    # depth buffer (ART.INI NormalZAdjust / ZShapePointMove), so GAWEAP is a
    # single sprite with no layer in front of a vehicle standing in the bay.
    # RA's WEAP and TD's WEAP2 have no depth buffer and instead carry the
    # hangar's near face in the overlay, which is what sandwiches an emerging
    # vehicle. Cut that near face out of the base here and hand it to the door
    # overlay so the Remastered engine gets the same read.
    #
    # The face is the wall the opening is cut into: a ring of building art
    # around the aperture, plus everything at or below the bay threshold (the
    # near lip and the buttress feet a vehicle passes behind coming down the
    # ramp).
    front_masks = None
    if door_spec is not None and front_ring is not None:
        door_dir, under_dir, stages = door_spec
        # The aperture is whatever the shutter uncovers: the pixels that
        # differ between the shut stage and the open one. Measured rather than
        # written down, so re-cut door art cannot silently move the frame.
        diff = ImageChops.difference(load(door_dir, 0), load(door_dir, stages - 1))
        acc = None
        for band in diff.split():
            acc = band if acc is None else ImageChops.add(acc, band)
        ap = acc.point(lambda v: 255 if v > 12 else 0).getbbox()
        if ap is None:
            raise SystemExit(f"{ini}: door stages 0 and {stages - 1} are identical, "
                             f"so the aperture cannot be located")
        # The WHOLE hangar goes in front, and the opening is a hole in it.
        # A ring around the aperture is not enough: a Mammoth Mk. II stands
        # about 58 classic pixels tall against a 33-pixel opening, so its back
        # clears the aperture entirely and lands on the roof, outside any ring
        # that could reasonably be drawn. RA and TD both solve this the same
        # way -- their base is the bay interior and their overlay is the whole
        # building -- so a vehicle in the bay is seen THROUGH the opening and
        # is covered everywhere else.
        #
        # The hole is the SHAPE of the opening, not its bounding box. The
        # doorway is a diamond in this projection, so a rectangular hole leaves
        # the wall in its corners behind the vehicle instead of in front, and
        # the vehicle shows through them beside the door.
        #
        # The shut shutter is exactly the door leaf, so its silhouette is the
        # opening -- a solid shape, unlike the stage-to-stage difference, which
        # is full of gaps wherever two stages happen to share a colour.
        #
        # front_ring is how far the near face encroaches into that opening; 0
        # leaves the hole exactly the size the shutter uncovers.
        aperture = load(door_dir, 0).split()[3].point(lambda v: 255 if v > 0 else 0)
        if front_ring:
            aperture = aperture.filter(ImageFilter.MinFilter(2 * front_ring + 1))
        region = ImageChops.invert(aperture)
        # Nothing BELOW the opening goes in front. That strip is the ramp and
        # the door-to-pad join, and it is ground the vehicle drives over on
        # its way out -- carried in the near face it cuts a band across the
        # vehicle exactly during the exit. It earns its keep only while the
        # door is shut, hiding a little of the feet, and that is the idle
        # state nobody watches. Measured: the strip is 7% of the near face and
        # moving it back costs 189 pixels of Titan foot on a shut door.
        _, _, _, ap_bottom = aperture.getbbox()
        draw = ImageDraw.Draw(region)
        # Cut 3 rows ABOVE the aperture bottom as well: the door/floor seam's
        # antialiased edge rides those rows, and any face pixel renders over a
        # unit sort-clamped onto an exit rail. Moved to the base they draw
        # identically on an idle building (nothing sorts between the layers
        # there) and stay under an exiting unit.
        draw.rectangle([0, ap_bottom - 3, region.width, region.height], fill=0)
        # DO NOT punch the idle lights out of the near face. They are lamps
        # mounted on the hangar -- 147 pixels of it, and 117 of those sit
        # ABOVE the opening -- so cutting them out of solid roof art leaves
        # three windows straight through the ceiling at the seam where the
        # door meets the roof, and anything in the bay shows through them
        # whatever its size. A Hover MLRS stands 11 classic pixels tall
        # against a 66 pixel building and still bled, which is what proved
        # this was a hole rather than a unit too big for its bay.
        #
        # The cost is that the lamps stop pulsing: the near face is one static
        # image per damage run, so they freeze at frame 0. That is a
        # brightness cycle on 147 pixels against holes in the roof. Restoring
        # it means indexing the overlay by animation frame as well as door
        # stage -- 8 x 9 x 2 frames, past the launcher's 128-shape cap -- so
        # it needs a different mechanism, not a bigger tileset.
        # Cut from the FULL base -- hangar AND bay interior. Everything of the
        # building that is not inside the opening belongs in front, the ramp
        # below the door included: a vehicle deep in the bay is behind that
        # ramp, and leaving it in the base is what showed its feet under a
        # shut door. What stays behind is exactly the patch of building framed
        # by the doorway.
        # The near face spans the building's SOLID outline, not merely the
        # pixels that happen to carry art. Where the door leaf meets the
        # hangar the two arts do not quite abut, and those few transparent
        # rows are a window straight through the building: a vehicle's feet
        # show under a shut door and a Mammoth Mk. II's rear pods show at the
        # seam. Filling the outline's interior holes closes them, and
        # bleed_edges has already put the neighbouring colour in those pixels,
        # so they paint as building rather than as a hard patch.
        def solid_outline(img):
            a = img.split()[3].point(lambda v: 255 if v > 0 else 0)
            # Flood the OUTSIDE from every border pixel; whatever the flood
            # cannot reach is an interior hole, so add it back.
            inv = ImageChops.invert(a)
            flood = inv.copy()
            fd = ImageDraw.floodfill
            for x in range(0, inv.width, 1):
                for yy in (0, inv.height - 1):
                    if flood.getpixel((x, yy)) == 255:
                        fd(flood, (x, yy), 128)
            for y in range(0, inv.height, 1):
                for xx in (0, inv.width - 1):
                    if flood.getpixel((xx, y)) == 255:
                        fd(flood, (xx, y), 128)
            holes = flood.point(lambda v: 255 if v == 255 else 0)
            return ImageChops.lighter(a, holes)

        front_masks = [ImageChops.multiply(solid_outline(b), region)
                       for b in (base_h, base_d)]

    # SPLIT AFTER SCALING, NEVER BEFORE. hq_scale composites onto a black RGB
    # canvas, so every alpha edge bleeds towards black. Cutting the source art
    # in two puts a new alpha edge down the seam in BOTH pieces, and the two
    # dark fringes meet as a black line across the finished building. Scaling
    # the whole frame once and dividing the RESULT by a mask carried through
    # the same affine creates no new edge in the colour domain: the two layers
    # recomposite to exactly the pixels the unsplit building would have drawn.
    def scaled(img):
        return place(img, factor, canvas_w, canvas_h, cx, cy, dst_x, dst_y)

    def split_alpha(img, mask, keep):
        """img with its alpha restricted to (or cleared of) mask."""
        out = img.copy()
        a = out.split()[3]
        out.putalpha(ImageChops.multiply(a, mask) if keep else ImageChops.subtract(a, mask))
        return out

    full = [[scaled(f) for f in healthy], [scaled(f) for f in damaged_frames]]
    # The building over its own apron: any partial-coverage pixel along the
    # join becomes opaque, so the silhouette GROWS onto the pad and no seam of
    # terrain shows between the two (soft edges showed the pad through as a
    # stair-step; the plain 128-threshold edge left single specks of snow).
    # Applied only where the building overlaps the apron mask.
    if apron_cells is not None and SCALER_MODE.get(ini, "hq4x-hard") != "hq4x-hard":
        pad_mask = apron.split()[3].point(lambda v: 255 if v > 0 else 0)
        # Seam band: pixels within 2 px of the pad that the pad does not cover.
        # Where the building comes within 2 px of that band there is a hairline
        # of terrain between the two pieces of art; those pixels join the
        # building (alpha 255, colour = the bled margin the scaler already laid).
        pad_near = pad_mask.filter(ImageFilter.MaxFilter(5))
        seam_band = ImageChops.subtract(pad_near, pad_mask)
        def harden_over_pad(img):
            a = img.split()[3]
            hard = a.point(lambda v: 255 if v >= 16 else 0)  # grow, never erode: the pad rim must stay covered
            solid = a.point(lambda v: 255 if v > 0 else 0)
            near_building = solid.filter(ImageFilter.MaxFilter(5))
            fill = ImageChops.multiply(seam_band, near_building)
            # Overlap: the launcher anchors the building on its crop centre and
            # the pad on cell corners, so the two can land a pixel apart in-game
            # and open a hairline that no offline composite shows. Grow the
            # building 3 px over the pad along the seam so drift cannot open it.
            overlap = ImageChops.multiply(solid.filter(ImageFilter.MaxFilter(7)), pad_near)
            # The grown pixels must wear the building's edge colour: the scaled
            # canvas's transparent margin is black by now (masked paste), so
            # bleed the edge colour outward first, 4 px to cover the 3 px growth.
            out = bleed_edges(img, rounds=4)
            out.putalpha(ImageChops.lighter(ImageChops.lighter(Image.composite(hard, a, pad_mask), fill), overlap))
            return out
        full = [[harden_over_pad(f) for f in run] for run in full]
    # Sub-object layers on the building's own affine: TS anims that are not
    # part of the idle cycle (one-shots, event-driven). Each becomes
    # <INI><SUFFIX>.ZIP with the frames in source order, so the DLL indexes
    # them directly (healthy run first, damaged run second, TS convention).
    for suffix, dirname, indices in globals().get("EXTRA_LAYERS", {}).get(ini, []):
        layer = [scaled(centre_on(load(dirname, i), base_h.size)) for i in indices]
        write_zip(f"{STRUCT_DIR}/{ini}{suffix}.ZIP", f"{ini.lower()}{suffix.lower()}", layer)
        patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", f"{ini}{suffix}", len(layer))
    front_canvas = None
    if front_masks is not None:
        white = Image.new("RGB", base_h.size, (255, 255, 255))
        canvas_masks = []
        for m in front_masks:
            carrier = white.convert("RGBA")
            carrier.putalpha(m)
            canvas_masks.append(scaled(carrier).split()[3])
        # Taken off frame 0 of each run: the face excludes the anim footprints,
        # so it is identical across the cycle.
        front_canvas = [split_alpha(full[r][0], canvas_masks[r], True) for r in (0, 1)]
        # The idle lamps live INSIDE the face, so the static face freezes them
        # at phase 0. Keep the face region of EVERY phase as well: it becomes
        # the <INI>LT lamp layer, drawn just above the door overlay, carrying
        # each phase's lamp pixels over the frozen ones.
        lamp_runs = [[split_alpha(f, canvas_masks[r], True) for f in full[r]] for r in (0, 1)]
        # Full-face frames (the play-approved look). A changing-pixels trim
        # was tried 2026-08-18 and REVERTED 2026-08-19: it left the red
        # glow's dilated halo as isolated smudges over the roof. Its
        # motivation -- the double-blended door/floor seam -- was removed
        # separately when the seam rows moved into the BASE layer, so the
        # full face re-covers itself with identical pixels everywhere.
        full = [[split_alpha(f, canvas_masks[r], False) for f in full[r]] for r in (0, 1)]

    # Luke's red-pixel markup (2026-08-18, edit 3): a leftover hazard-stripe
    # skirt from the source GTWEAP art rides in the BASE below the overlay's
    # bottom edge, west of the bay mouth, on top of the hand-tucked pad.
    # Erase the marked patch (+2px margin); the pad ground art beneath is the
    # intended surface. Canvas space, so the coordinates are the markup's.
    # (A wider remap-green sweep of the whole south skirt was tried 2026-08-18
    # and REVERTED on Luke's instruction -- the band is wanted art there.)
    if ini == "TSWEAP":
        for run in full:
            for f in run:
                f.paste((0, 0, 0, 0), (353, 402, 370, 443))

    frames = full[0] + full[1]
    if emblem is not None:
        # Built frames only: during construction there is no deck to paint.
        # Damaged-run frames stamp against the healthy reference: same
        # geometry, erased over destroyed deck, scorched where it burned.
        n_healthy = len(full[0])
        healthy_ref = frames[0]
        frames = [stamp_emblem(f, *emblem, ref=(healthy_ref if i >= n_healthy else None))
                  for i, f in enumerate(frames)]
    write_zip(f"{STRUCT_DIR}/{ini}.ZIP", ini.lower(), frames)

    if door_spec is not None:
        # Door overlay, the WEAP2 scheme: TS draws a roll-up shutter
        # (DoorAnim) over a static bay interior (UnderDoorAnim), both above
        # the finished building. Compositing the pair into one tileset keeps
        # the engine's single overlay draw per door stage.
        #
        # Shares this building's affine and canvas, so the overlay lands on
        # the bay whatever the base fit resolved to. Stages run 0 (shut) to
        # stages-1 (open); the damaged run repeats them over the damaged
        # interior, since TS ships no wrecked-door art (the frames past the
        # real stages are magenta placeholders, as in GTPOWRMK).
        door_dir, under_dir, stages = door_spec

        # Clipped to the building's own silhouette. TS's under-door art carries
        # the whole bay surround -- ramp and concrete included -- and 71% of it
        # falls outside the building, where it is a duplicate of ground the
        # apron already draws. Left in, that surplus is BUILDING art covering
        # the cells vehicles stand on, which is what made units vanish beside
        # the factory. Everything that actually moves between door stages is
        # inside the silhouette, so nothing of the door itself is lost.
        #
        # Taken from the FULL base run, before the front piece is cut out of
        # it: the silhouette is the building's true outline, and clipping to a
        # base that has already lost its near face would erase that face from
        # the overlay it is being moved into.
        def silhouette(run):
            m = None
            for f in run:
                a = f.split()[3].point(lambda v: 255 if v > 0 else 0)
                m = a if m is None else ImageChops.lighter(m, a)
            return m

        sils = [silhouette(healthy), silhouette(damaged_frames)]
        mk_building_sil = ImageChops.lighter(sils[0], sils[1])

        door_frames = []
        for under_f in (0, 1):
            # The interior is in the base now; this layer is shutter + face.
            under = Image.new("RGBA", base_h.size, (0, 0, 0, 0))
            # The near face rides on top of the shutter in every stage, so it
            # is in front of both the bay interior and anything standing in
            # it. Composited in CANVAS space, after each layer has been through
            # the affine on its own: it was cut from the scaled building and
            # has to go back exactly where it came from.
            for s in range(stages):
                shutter = load(door_dir, s)
                cell = under.copy()
                cell.paste(shutter, (0, 0), shutter)
                cell.putalpha(ImageChops.multiply(cell.split()[3], sils[under_f]))
                out = place(cell, factor, canvas_w, canvas_h, cx, cy, dst_x, dst_y)
                if front_canvas is not None:
                    out = Image.alpha_composite(out, front_canvas[under_f])
                door_frames.append(out)

        # The overlay's FLOOR BAND -- ramp lip, door-frame feet, wall bases --
        # splits into its own layer (<INI>2L), sorted one notch UNDER the exit
        # clamp: a unit gliding out must draw over the floor furniture while
        # the roof and upper walls stay above it for the whole rail (a single
        # overlay key cannot serve both, which put the frame's foot over an
        # emerging hull). Units parked deep in the bay sort below the band's
        # key, so the shut-door composite is unchanged. Split in canvas space
        # on the finished frames: the band top sits a fixed distance above the
        # overlay's lowest opaque row, derived per pack so a respec moves it
        # automatically. 62 canvas rows ~= 26 source px at the current fit --
        # deep enough for the east frame's upright foot (Luke's red-pixel
        # markup, canvas y329, band bottom y390).
        if front_canvas is not None:
            y_last = max(f.getbbox()[3] for f in door_frames if f.getbbox())
            band_top = y_last - 62
            band = Image.new("L", (canvas_w, canvas_h), 0)
            ImageDraw.Draw(band).rectangle([0, band_top, canvas_w, canvas_h], fill=255)
            low_frames = [split_alpha(f, band, True) for f in door_frames]
            door_frames = [split_alpha(f, band, False) for f in door_frames]
            write_zip(f"{STRUCT_DIR}/{ini}2L.ZIP", f"{ini.lower()}2l", low_frames)
            patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", f"{ini}2L", len(low_frames))
        write_zip(f"{STRUCT_DIR}/{ini}2.ZIP", f"{ini.lower()}2", door_frames)
        patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", f"{ini}2", len(door_frames))

        if front_canvas is not None:
            # The lamp layer (see the lamp_runs cut above): the full face per
            # phase, healthy run then damaged, indexed by the SAME shape number
            # as the body draw (Fetch_Stage + damaged offset in Shape_Number).
            lamp_frames = lamp_runs[0] + lamp_runs[1]
            write_zip(f"{STRUCT_DIR}/{ini}LT.ZIP", f"{ini.lower()}lt", lamp_frames)
            patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", f"{ini}LT", len(lamp_frames))

    # TS buildups pour the concrete pad first and keep it throughout; with
    # the pad dropped from the finished art (grid-sized buildings + RA slab),
    # mask the pad's silhouette (its *BB sprite, same source canvas) out of
    # every buildup frame or construction shows a pad that then vanishes.
    if mk_mask_dir is not None or mk_clip_dir is not None:
        mk_degreen = lambda img: img
        if mk_mask_dir is not None:
            msk = load(mk_mask_dir, 0)
            m2 = load(mk_mask_dir, 2)
            msk.paste(m2, (0, 0), m2)
            msk = msk.split()[3].point(lambda a: 255 if a > 0 else 0)

            def mk_alpha(a):
                return ImageChops.subtract(a, msk)
        else:
            # A buildup borrowed from a bigger building raises structure this
            # one doesn't have: keep only what falls inside the clip sprite's
            # own silhouette (same source canvas, so registration is free).
            # The borrowed structure also leans OVER that silhouette in some
            # frames; its pixels are remap-green, so green inside the clip
            # that isn't part of the clip art's own green (the rim ring) is
            # foreign — inpaint it from the surrounding slab.
            import numpy as np
            # The healthy frame alone defines the clip: the damaged frame's
            # silhouette bulges past it and would let foreign pixels through.
            clip_img = load(mk_clip_dir, 0)
            clip = clip_img.split()[3].point(lambda a: 255 if a > 0 else 0)
            ca = np.array(clip_img).astype(int)
            c2a = np.array(load(mk_clip_dir, 2)).astype(int)
            own_green = ((ca[..., 1] > ca[..., 0] + 20) & (ca[..., 1] > ca[..., 2] + 20)) | \
                        ((c2a[..., 1] > c2a[..., 0] + 20) & (c2a[..., 1] > c2a[..., 2] + 20))

            def mk_alpha(a):
                return ImageChops.multiply(a, clip)

            def mk_degreen(img):
                a = np.array(img).astype(int)
                green = (a[..., 3] > 0) & (a[..., 1] > a[..., 0] + 20) & \
                        (a[..., 1] > a[..., 2] + 20)
                # The clip art's own green (the rim ring) is only protected in
                # frames actually drawing it: position alone would shield
                # foreign green that happens to cross the ring's path.
                ring_drawn = (a[..., :3] == ca[..., :3]).all(-1)[own_green].mean() > 0.5 \
                    if own_green.any() else False
                if ring_drawn:
                    green &= ~own_green
                if not green.any():
                    return img
                good = (a[..., 3] > 0) & ~green
                out = a.astype(float)
                shifts = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                          if (dy, dx) != (0, 0)]
                while green.any():
                    ssum = np.zeros(out[..., :3].shape)
                    scnt = np.zeros(green.shape)
                    for dy, dx in shifts:
                        gsh = np.roll(np.roll(good, dy, 0), dx, 1)
                        csh = np.roll(np.roll(out[..., :3], dy, 0), dx, 1)
                        ssum += csh * gsh[..., None]
                        scnt += gsh
                    fill = green & (scnt > 0)
                    if not fill.any():
                        break
                    out[fill, :3] = ssum[fill] / scnt[fill, None]
                    good |= fill
                    green &= ~fill
                return Image.fromarray(np.clip(out, 0, 255).astype("uint8"))

        def mk_load(i):
            img = load(mk_dir, i)
            img.putalpha(mk_alpha(img.split()[3]))
            return mk_degreen(img)

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
    if mk_pad_erase is not None:
        # Hand-authored pad (apron_canvas): strip every pad pixel -- old
        # position and new -- from the buildup, except where the building's
        # own silhouette stands (walls rise from the pad; erasing those
        # unbuilds the building bottom-up). The ground tiles supply the
        # concrete beneath the whole animation.
        erase = mk_pad_erase
        if mk_building_sil is not None:
            s = Image.new("RGBA", mk_building_sil.size, (255, 255, 255, 0))
            s.putalpha(mk_building_sil)
            keep = place(s, factor, canvas_w, canvas_h, cx, cy,
                         dst_x, dst_y).split()[3].point(lambda v: 255 if v > 127 else 0)
            erase = ImageChops.subtract(erase, keep)
        for f in mk:
            f.putalpha(ImageChops.subtract(f.split()[3], erase))
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
    # Hand-made art in resources/custom-cameos is canonical for its icon name;
    # only generate from the TS cameo when no override exists.
    custom = os.path.abspath(f"{MOD}/../../custom-cameos/{icon_name}.png")
    if os.path.exists(custom):
        Image.open(custom).convert("RGBA").resize((341, 256), Image.LANCZOS).save(
            f"{ICON_DIR}/{icon_name}.tga")
    else:
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
    window both runs. Convention-breakers (GTCNST_B light, NTREFN_B plume:
    one continuous cycle, damaged form = the empty half) pass a pre-built
    (dir, healthy, damaged) tuple instead, returned untouched."""
    if isinstance(d, tuple):
        return d
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
    # The dropship bay is the depot's apron plate promoted to a building of its
    # own: GTDEPTBB carries the octagonal deck, GTDEPT the gantry that stands
    # beside it. Passing only the plate leaves nothing to patch, since the
    # gantry never overlaps the deck. No anims -- a static pad by design.
    ("TSDROP", "shp_gtdeptbb", [],
     "shp_gtdeptmk", 19, (384, 256), 382, "shp_fixicon", "Dropship Bay", "Receives the Mammoth Mk. II by dropship."),
]

# TSPROC/TSWEAP apron plates dropped with the 3x3 conversion (2026-08-03
# late): structure-only composites fill the box, engine Bib=yes lays the RA
# slab like every other refinery/factory.
BIBS = {"TSHPAD": "shp_gthpadbb", "TSDEPT": "shp_gtdeptbb"}

# (artwork, width fraction of content, squash ratio, dx, dy). Fill-the-pad
# dial (Luke's pick off a 4-way sheet, 2026-08-13): the ring's inner ellipse
# measures 292x136 centred at (197.6, 103.2) on the healthy frame, so squash
# matches the ring's own 2.15 (not the deck skirt's 1.95) and (+6, -6)
# corrects the bbox-centre bias -- the bbox includes the skirt, whose centre
# sits left and low of the ring's. 0.74 (284px) leaves ~4px to the remap
# band; crossing it speckles house colour through the emblem edge.
# APRON_CLIP: clip a building's concrete to its tile grid. Tried on TSWEAP
# 2026-08-17 and REJECTED ("cutting the pad off looks like garbage" -- the
# same hard-edge failure recorded 2026-08-05); the ghost grew to 5x3 instead.
APRON_CLIP = set()

# EXTRA_LAYERS: event-driven TS anims shipped as sub-object layers (see
# build_structure). TSPROC: FR = NTREFN_B fireball, 20 healthy + 20 damaged,
# one burst per DLL trigger; LD = NTREFN_A dock lid, 5 healthy + 5 damaged,
# played forward at dock start and reversed at dock end.
EXTRA_LAYERS = {
    "TSPROC": [("FR", "shp_ntrefn_b", list(range(40))),
               ("LD", "shp_ntrefn_a", list(range(10)))],
}

# Emblem art lives IN the repo (resources/custom-cameos) — a Desktop copy
# got Trash-cleaned 2026-08-16 and broke the pack.
EMBLEMS = {"TSDROP": (os.path.join(os.path.dirname(__file__), "..",
                                   "resources/custom-cameos/ts-gdi-logo.png"),
                      0.74, 2.15, 6, -6)}

# Per-entry bottom anchor (classic px), switching that entry to the size-pass
# fit. TSDROP: the plot is the deck's own 3x2 (2026-08-13), canvas 384x256
# mapped onto it; margin 9 keeps the deck's bottom at the same 39cl below the
# origin the 3x3-era margin 33 gave it, so the art does not move on screen.
BOTTOM_MARGINS = {"TSDROP": 9}

# The bay borrows the depot's buildup, which also raises the gantry the bay
# doesn't have: clip every frame to the deck's own silhouette so only the
# pad's construction survives.
MK_CLIPS = {"TSDROP": "shp_gtdeptbb"}

for ini, base, anim_dirs, mk, mkc, (cw, ch), tw, cameo, disp, desc in WAVE2:
    if not os.path.isdir(f"{ART}/{base}"):
        print(f"{ini}: SKIP (no {base})")
        continue
    # Damaged base = frame 1: TS building SHPs are 0 healthy, 1 LIGHT damage,
    # 2 HEAVY damage, 3-5 rubble fragments (the old "frame 1 = healthy
    # variant" claim was falsified 2026-08-06). Luke picked LIGHT as the
    # damaged state off the Desktop sheets, 2026-08-13. TSDROP keeps HEAVY:
    # its weathered damaged deck was approved in play 2026-08-13.
    build_structure(ini, base, 0, (2 if ini == "TSDROP" else 1),
                    [loop(d) for d in anim_dirs], mk, mkc, cw, ch,
                    None if ini in BOTTOM_MARGINS else tw,
                    bib_dir=BIBS.get(ini), emblem=EMBLEMS.get(ini),
                    bottom_margin=BOTTOM_MARGINS.get(ini),
                    mk_clip_dir=MK_CLIPS.get(ini))
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
    # NTREFN_B = one continuous 20-frame smoke-puff cycle (forms, rises,
    # dissipates -- NO damaged half; convention-breaker like GTCNST_B), so
    # the full window plays in both runs. The no-bib union is only 94 src px
    # wide -> full-width factor 5.45x -> 643 HD px tall: the canvas must be
    # 672 or the plume tip clips (512/544/576 all did).
    # Width-fit to the full 3x3 PLOT (72 classic; the 4-cell/512 fit read
    # oversized next to the 2x2 tier -- Luke, 2026-08-04). Stub 138x174:
    # the BSIZE_43 foundation (2 building rows + apron row; the art's top
    # row OVERHANGS the row north of the plot, radar treatment) puts the
    # draw anchor (= foundation centre) a full cell south of where the
    # old 3x3's sat relative to the art, so the canvas carries two extra
    # cells (48 classic / 256 HD) at the BOTTOM to keep the content
    # pixel-static -- margin 27+48=75 keeps the disc bottom on the
    # building rows' south edge, and the plume keeps its full 27-classic
    # headroom above the art top. The wide canvas carries the NTREFNBB
    # apron OVERLAY (dock bay incl. the hazard-striped ramp, Luke's TS
    # screenshot) riding east/south into the halo -- fit-excluded, so the
    # building size is unchanged.
    # Plume cycle = frames 2-16 only: 0-1/17-19 carry 10-57 src px and
    # scale to "dead pixel" specks at the chimney tip (Luke, 23:17 SS).
    # Idle = the NTREFN_C deck lights (16 healthy + 16 damaged). The chimney
    # fireball (NTREFN_B) and the dock lid (NTREFN_A) are NOT baked: TS plays
    # the fireball as a one-shot burst with a random pause between bursts and
    # the lid only while a harvester docks/undocks, so both ship as their own
    # sub-object layers (EXTRA_LAYERS below) driven by the DLL.
    ("TSPROC", "shp_ntrefn", [("shp_ntrefn_c", list(range(16)), list(range(16, 32)))],
     "shp_ntrefnmk", 19, (736, 928), 75, 1.0, "shp_reficon",
     "TS Tiberium Refinery", "Processes Tiberium into credits."),
    # 4x3 plot, descaled 2026-08-16 (Luke): the Mk. II arrives by dropship
    # bay now, so the hangar no longer has to pass a 40px sprite -- fit_w 460:
    # Luke's split-the-difference between the 416 APC floor and the old 512
    # (416 read barely bigger than the power plant, 2026-08-16 SS).
    # 3x2 PLOT, hangar CENTRED (dst_x 448 = canvas centre): the 70x44 art
    # fills the 72x48 plot, so the launcher's plot-centred box hugs it with
    # NO export case -- TDFACT/TDWEAP parity. Concrete = wholly outside the
    # plot (east col + front row), the TD-bib arrangement. The hangar shrinks onto
    # the WEST THREE columns (dst_x_px 384 = their centre) and the concrete
    # pad comes INSIDE the plot, TSPROC-style: east column + south row are
    # walkable ground the apron art covers. margin 39 seats the hangar's
    # bottom 12 classic into the south row so the door face meets the
    # concrete and the art roughly centres on the plot-centred selection
    # box. Canvas/stub unchanged (896x672 = 168x126).
    # margin 40.5 (2026-08-17 evening, Luke's Aseprite pass): building union
    # bottom at canvas 456, which centres the ENSEMBLE (hangar + hand-tucked
    # pad, bbox 205-467) on the 4x3 plot (144-528). Art centred on plot =
    # the launcher's plot-centred selection box hugs it at 96x49 with a size
    # dial only (contract #7). The door front dips into the top half of the
    # walkable bottom row; units drive out through it.
    ("TSWEAP", "shp_gtweap", ["shp_gtweap_a", "shp_gtweap_b", "shp_gtweap_c"],
     "shp_gtweapmk", 19, (896, 672), 40.5, 1.0, "shp_weapicon",
     "TS War Factory", "Produces Tiberian-era vehicles."),
    # 2x1 plot + bib: the 48-tall stub centres on the 24-tall box, so the
    # canvas bottom is 12 classic below the plot edge. Margin 12 = building
    # ON the top (plot) row, slab owns the entire bottom row (Luke, 23:40).
    ("TSPILE", "shp_gtpile", ["shp_gtpile_a", "shp_gtpile_b", "shp_gtpile_c"],
     "shp_gtpilemk", 19, (256, 256), 12, 1.0, "shp_brrkicon",
     "TS Barracks", "Trains Tiberian-era infantry."),
    # Back to the TS-authentic 2x2 plot (stub 48x96, Obelisk treatment);
    # the 3x2 size-up made the 2x2 power plant "look like a toy" (Luke,
    # 2026-08-04). Margin 21 = art bottom 3 classic below the plot's south
    # edge, same tuck as the 3x2 tuning had.
    ("TSRADR", "shp_gtradr", ["shp_gtradr_a"],
     "shp_gtradrmk", 20, (256, 512), 21, 1.0, "shp_radricon",
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
    # Buildups pour and keep their pads. That double-draws the war factory's
    # concrete over the ground apron beneath it, which costs nothing (identical
    # art, identical place) and is the only thing colouring its hazard stripes
    # during construction: the stripes sit in the house-REMAP range, buildings
    # are remapped by the launcher and ground art is not, so an apron left to
    # supply them on its own shows them raw green. Once built the door overlay
    # covers them, which is why it only ever showed while building.
    masks = {}
    # Full apron (the 4x3-rectangle clip sliced hard edges through the
    # stripes -- Luke, 2026-08-05 01:20; the cliff-edge drape is a queued
    # design question, not solvable with a rectangle cut).
    overlays = {"TSPROC": "shp_ntrefnbb", "TSWEAP": "shp_gtweapbb"}
    # Aprons ship as ground art, one tile per cell: (plot, tile grid), the grid
    # matching the building's SmudgeTypeClass in sdata.cpp.
    aprons = {"TSWEAP": ((4, 3), (4, 3), (0, 0)), "TSPROC": ((4, 3), (5, 3), (0, 0))}
    # TS drives the war factory bay with a separate 9-stage shutter over a
    # static interior (ART.INI: DoorAnim/DoorStages/UnderDoorAnim).
    doors = {"TSWEAP": ("shp_gtweap_d", "shp_gtweap_1", 9)}
    build_structure(ini, base, 0, 1, anims, mk, mkc, cw, ch,
                    bib_dir=BIBS.get(ini), bottom_margin=margin, overscale=oscale,
                    mk_mask_dir=masks.get(ini), overlay_dir=overlays.get(ini),
                    door_spec=doors.get(ini),
                    # 4-wide foundations whose building fills only the west 3
                    # columns: pin the building's width independently of the
                    # canvas, and anchor it on those columns rather than on
                    # the box centre.
                    fit_w={"TSPROC": 384, "TSWEAP": 460}.get(ini),
                    dst_x_px={"TSPROC": 304, "TSWEAP": 392}.get(ini),
                    apron_cells=aprons.get(ini),
                    # TSWEAP's pad is hand-authored (Luke, Aseprite, 2026-08-17):
                    # the committed canvas replaces the affine'd GTWEAPBB.
                    apron_canvas={"TSWEAP": os.path.abspath(os.path.join(
                        MOD, "..", "..", "custom-art",
                        "tsweap-pad-canvas.png"))}.get(ini),
                    # How far the near face encroaches into the bay opening.
                    # 0 = the hole is exactly what the shutter uncovers, so a
                    # vehicle is visible through the full opening and hidden
                    # everywhere else. Raise it to tuck the vehicle further
                    # behind the door frame.
                    front_ring={"TSWEAP": 0}.get(ini),
                    # The lamp cycle sweeps and returns (8 -> 14 frames);
                    # _anims[] Count and the TSWEAPLT stub must match.
                    pingpong={"TSWEAP": True}.get(ini, False))
    emit_sidebar_data(ini, disp, desc, cameo)

# ---- TSFACT: TS Construction Yard on the RA-conyard 3x3 plot (BSIZE_33 +
# bib, stub 72x72; the 4x3 tier read oversized -- Luke, 2026-08-04). Art
# union h/w = 0.67, so the plot-width fit stands ~48 classic inside the
# 72-box. Anims: _A crane 20, _B light 10, _C crane-2 30 -> N=60. Damaged
# base = GTCNST frame 1 (LIGHT).
if os.path.isdir(f"{ART}/shp_gtcnst"):
    # GTCNST_B (rotating light) breaks the healthy+damaged half convention:
    # its 10 content frames are ONE full rotation (equal 614px every frame,
    # continuous sweep) and its damaged form is the empty second half of the
    # SHP. Halving it played half a rotation + snap-back — the radar-dish
    # symptom. _A (crane) and _C (roof lights) halves ARE damaged variants.
    light = ("shp_gtcnst_b", list(range(10)), list(range(10)))
    # Flat art sits ON the bib slab like the TD conyard (Luke, 22:03 SS
    # verdict; the centred experiment floated it off the slab). Foundation
    # brackets extending over the empty north plot are accepted -- the
    # selection box is launcher-fixed to the foundation.
    # Canvas 384x256 since the 3x2 plot (2026-08-13): frame = plot, content
    # flush bottom = art on the slab exactly as approved, box hugs the art.
    build_structure("TSFACT", "shp_gtcnst", 0, 1,
                    [loop("shp_gtcnst_a"), light, loop("shp_gtcnst_c")],
                    "shp_gtcnstmk", 32, 384, 256, bottom_margin=0,
                    overscale=1.0)

# ---- TSPOWR: TS Power Plant (2x2, POWR donor 48x48 -> 256x256).
# Content scaled to TDNUKE (content 256 full-width). Anims: _A fan 24, _B 12
# -> N=24. Damaged base = GTPOWR frame 1 (LIGHT).
if os.path.isdir(f"{ART}/shp_gtpowr"):
    build_structure("TSPOWR", "shp_gtpowr", 0, 1,
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

with open(STUB_MANIFEST, "w") as f:
    json.dump(STUB_DIMS, f, indent=1, sort_keys=True)
    f.write("\n")
print(f"wrote {STUB_MANIFEST} ({len(STUB_DIMS)} buildings)")

print("DONE")
