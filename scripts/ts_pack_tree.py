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
                    overlay_dir=None, fit_w=None, dst_x_px=None, door_spec=None,
                    apron_cells=None, front_ring=None):
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
        src = load(overlay_dir, healthy_f)
        px = src.load()
        for y in range(src.height):
            for x in range(src.width):
                r, g, b, a = px[x, y]
                if a and g > 70 and g > r * 1.6 and g > b * 1.6:
                    px[x, y] = (g, round(g * 0.82), 0, a)
        apron = place(src, factor, canvas_w, canvas_h, cx, cy, dst_x, dst_y)
        gx, gy = left + off_c * cell_px, top + off_r * cell_px
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
        ax0, ay0, ax1, ay1 = ap
        region = Image.new("L", base_h.size, 0)
        draw = ImageDraw.Draw(region)
        draw.rectangle([ax0 - front_ring, ay0 - front_ring,
                        ax1 + front_ring - 1, ay1 + front_ring - 1], fill=255)
        draw.rectangle([0, ay1, base_h.size[0], base_h.size[1]], fill=255)
        draw.rectangle([ax0, ay0, ax1 - 1, ay1 - 1], fill=0)
        # The idle anims are lights mounted on that wall. Leave their
        # footprints behind in the base: carrying them forward would make the
        # overlay anim-frames x door-stages and need a new shapenum encoding,
        # and there are 147 lit pixels across all three anims.
        lights = Image.new("L", base_h.size, 0)
        for spec in anims:
            for idx in sorted(set(spec[1]) | set(spec[2])):
                a = load(spec[0], idx).split()[3].point(lambda v: 255 if v > 0 else 0)
                lights = ImageChops.lighter(lights, a)
        region = ImageChops.subtract(region, lights.filter(ImageFilter.MaxFilter(3)))
        front_masks = [ImageChops.multiply(b.split()[3].point(lambda v: 255 if v > 0 else 0), region)
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
        full = [[split_alpha(f, canvas_masks[r], False) for f in full[r]] for r in (0, 1)]

    frames = full[0] + full[1]
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

        door_frames = []
        for under_f in (0, 1):
            under = load(under_dir, under_f)
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
        write_zip(f"{STRUCT_DIR}/{ini}2.ZIP", f"{ini.lower()}2", door_frames)
        patch_tileset(f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML", f"{ini}2", len(door_frames))

    # TS buildups pour the concrete pad first and keep it throughout; with
    # the pad dropped from the finished art (grid-sized buildings + RA slab),
    # mask the pad's silhouette (its *BB sprite, same source canvas) out of
    # every buildup frame or construction shows a pad that then vanishes.
    if mk_mask_dir is not None:
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
    ("TSPROC", "shp_ntrefn", [("shp_ntrefn_b", list(range(2, 17)), list(range(2, 17)))],
     "shp_ntrefnmk", 19, (736, 928), 75, 1.0, "shp_reficon",
     "TS Tiberium Refinery", "Processes Tiberium into credits."),
    # 4x3 plot holding the hangar and nothing else. The hangar's width is set
    # by what has to drive through the bay door -- at the 3-cell width a
    # Mammoth Mk. II was 40x40 classic px against a 33.6x33.6 door and simply
    # could not fit -- and at 4 cells wide the art is 3.90x2.74 cells, so it
    # sits inside the plot without hanging over a neighbouring row. fit_w 512
    # pins the hangar at 4 cells, dst_x_px 448 centres it on the plot, and
    # margin 27 puts the art's bottom on the plot's south edge. The canvas is
    # 896x672 = stub 168x126 (x5.33) against a 96x72 box: the halo is what
    # carries the concrete, which lands wholly OUTSIDE the plot and is sliced
    # off into ground art. The pad is fit-excluded, so it cannot inflate the
    # building's size read.
    ("TSWEAP", "shp_gtweap", ["shp_gtweap_a", "shp_gtweap_b", "shp_gtweap_c"],
     "shp_gtweapmk", 19, (896, 672), 27, 1.0, "shp_weapicon",
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
    aprons = {"TSWEAP": ((4, 3), (5, 3), (1, 1)), "TSPROC": ((4, 3), (5, 3), (0, 0))}
    # TS drives the war factory bay with a separate 9-stage shutter over a
    # static interior (ART.INI: DoorAnim/DoorStages/UnderDoorAnim).
    doors = {"TSWEAP": ("shp_gtweap_d", "shp_gtweap_1", 9)}
    build_structure(ini, base, 0, 2, anims, mk, mkc, cw, ch,
                    bib_dir=BIBS.get(ini), bottom_margin=margin, overscale=oscale,
                    mk_mask_dir=masks.get(ini), overlay_dir=overlays.get(ini),
                    door_spec=doors.get(ini),
                    # 4-wide foundations whose building fills only the west 3
                    # columns: pin the building's width independently of the
                    # canvas, and anchor it on those columns rather than on
                    # the box centre.
                    fit_w={"TSPROC": 384, "TSWEAP": 512}.get(ini),
                    dst_x_px={"TSPROC": 304, "TSWEAP": 448}.get(ini),
                    apron_cells=aprons.get(ini),
                    # Source pixels of near wall kept around the bay opening.
                    # Wider tucks a vehicle deeper into the bay; tighter reads
                    # as a thin frame. Dialled by eye in play.
                    front_ring={"TSWEAP": 12}.get(ini))
    emit_sidebar_data(ini, disp, desc, cameo)

# ---- TSFACT: TS Construction Yard on the RA-conyard 3x3 plot (BSIZE_33 +
# bib, stub 72x72; the 4x3 tier read oversized -- Luke, 2026-08-04). Art
# union h/w = 0.67, so the plot-width fit stands ~48 classic inside the
# 72-box. Anims: _A crane 20, _B light 10, _C crane-2 30 -> N=60. Damaged
# base = GTCNST frame 2.
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
    build_structure("TSFACT", "shp_gtcnst", 0, 2,
                    [loop("shp_gtcnst_a"), light, loop("shp_gtcnst_c")],
                    "shp_gtcnstmk", 32, 384, 384, bottom_margin=0,
                    overscale=1.0)

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

with open(STUB_MANIFEST, "w") as f:
    json.dump(STUB_DIMS, f, indent=1, sort_keys=True)
    f.write("\n")
print(f"wrote {STUB_MANIFEST} ({len(STUB_DIMS)} buildings)")

print("DONE")
