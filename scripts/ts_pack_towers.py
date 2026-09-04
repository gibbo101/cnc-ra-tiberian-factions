#!/usr/bin/env python3
"""Pack the TS component tower family (bare tower + Vulcan / RPG / SAM) as HD art.

The tower BODY is swappable art; the TURRETS are always TS's own GTCTWR_B/_C/_D
rotation sprites composited over it. TS's turrets are round, so their 32 frames
carry no isometric bias and drop onto any body.

Two body sources are supported and detected by size:

  low-res  a 48x48 TS building SHP frame set (TS's own GTCTWR). Upscaled with the
           tree's hq4x-hard path, the same look every other TS building ships.
  hi-res   a redrawn body at any larger size, downsampled with Lanczos. This is the
           route in use: TS drew GACTWR's wall connectors on the isometric
           diagonals, and this mod's grid needs them on north/east/south/west, so
           the body was redrawn cardinal-footed.

Everything registers off the TEAM-COLOUR RING on the platform, which both the TS
body and any redrawn body carry: the ring's width sets the turret's scale and the
ring's centre sets where the turret sits, so a new body needs no hand-dialled seat.

Frame sets written (RA_STRUCTURES.XML patched to match):
  TSCTWR       2      body healthy, body damaged
  TSCTWRMAKE   17     construction; from the body's own buildup frames if it has
                      them, otherwise a rise-from-the-ground mask reveal
  TSVULC / TSROCK / TSCSAM
               128    32 facings x {idle, recoil, damaged idle, damaged recoil},
                      the TDGUN layout Shape_Number expects (+32 recoil, +64 damaged)
  <ini>MAKE    17     the same construction frames

Env:
  TS_ART_DIR   required, holds the decoded sprite directories
  TS_BODY_DIR  body art directory (default shp_gpt_ctwr; TS's own is shp_gtctwr)
  TS_MAKE_DIR  buildup directory, used only with TS's own body (default shp_gtctwrmk)
  TS_BODY_W    body content width in final pixels. Default 128 = exactly one cell:
               the tower is a 1x1 building and its art stays inside its own square,
               overlapping no neighbour (Luke, 2026-09-04)
  TS_TURRET_K  turret size over the TS-authentic body ratio (default 1.0)
  TS_SEAT_DX / TS_SEAT_DY   nudge the turret seat, in TS pixels
License: GPL v3.
"""
import glob, io, json, math, os, sys, zipfile
import numpy as np
from PIL import Image
import hqx

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import ts_pack_walls as W

ART = os.environ.get("TS_ART_DIR", "")
CANVAS_W, CANVAS_H = W.CANVAS_W, W.CANVAS_H          # 176 x 320
CELL_PX = W.CELL_PX                                   # 128
# Where the body's lowest pixel sits, measured from the canvas centre (= the cell
# centre). The cell's south edge is 64 px away and that is exactly where it sits:
# wall arms now run to their own boundary and stop, so every piece stays inside its
# own cell and nothing is drawn over a neighbour.
GROUND_Y = CANVAS_H // 2 + int(os.environ.get("TS_GROUND_Y", "64"))
BODY_W = int(os.environ.get("TS_BODY_W", "128"))
BODY_DIR = os.environ.get("TS_BODY_DIR", "shp_gpt_ctwr")
MAKE_DIR = os.environ.get("TS_MAKE_DIR", "shp_gtctwrmk")
TURRETS = {"TSVULC": "shp_gtctwr_b", "TSROCK": "shp_gtctwr_c", "TSCSAM": "shp_gtctwr_d"}

# Each turret set rotates about its own point on TS's 48 canvas, and they differ by a
# couple of pixels -- which the body scale multiplies into a visible mis-seat. These
# are the mean of each set's 32 frame centroids, i.e. the axis the frames turn around.
TURRET_PIVOT = {"shp_gtctwr_b": (23.08, 13.69),
                "shp_gtctwr_c": (23.99, 11.37),
                "shp_gtctwr_d": (24.03, 11.12)}
MAKE_FRAMES = 17
RECOIL_PX = 3          # TS ships no recoil frames for these turrets; nudge the sprite back

# TS's own body is the reference every measurement is taken against (48 x 48 canvas):
# its platform ring is 19 px wide, and the turret sprites pivot on the tower's vertical
# axis a little above the platform surface. The seat is therefore the ring's centre
# lifted slightly, in TS pixels, scaled by the body's ring width. TS's own body wants
# a bigger lift (4.3) than a flatter, more top-down platform does; 1.5 suits the
# redrawn cardinal-footed body. Override per body art with TS_SEAT_DX / TS_SEAT_DY.
# Turret SIZE comes from the body, not the platform: TS drew its turrets on the same 48
# canvas as its 34 px body and let them overhang it, so scaling a turret by the body's
# own factor reproduces TS's relationship on any body art. Scaling to the ring instead
# shrinks them on a body whose platform is drawn proportionally smaller than TS's.
# Turret PLACEMENT still comes from the ring, which is what the turret stands on.
TS_RING_W = 19.0
TS_BODY_PX = 34.0
# 1.0 = TS's own relationship, measured off an in-game shot of all four towers
# (2026-09-04): the turret spans roughly three quarters of the tower's width and
# sits down in the platform ring. Anything less reads as a toy gun on a big tower.
TURRET_K = float(os.environ.get("TS_TURRET_K", "1.0"))
TS_TURRET_OFFSET = (float(os.environ.get("TS_SEAT_DX", "0.0")),
                    float(os.environ.get("TS_SEAT_DY", "-4.3")))


def _dir(name):
    return f"{ART}/{name}"


def load_frame(dirname, i):
    return Image.open(f"{_dir(dirname)}/frame-{i:04d}.png").convert("RGBA")


def ring_of(img):
    """(centre_x, centre_y, width) of the team-colour ring, in the image's own pixels."""
    a = np.array(img).astype(int)
    g = (a[:, :, 1] > 110) & (a[:, :, 1] > a[:, :, 0] * 1.5) & (a[:, :, 1] > a[:, :, 2] * 1.5) & (a[:, :, 3] > 128)
    ys, xs = np.nonzero(g)
    if len(xs) == 0:
        raise SystemExit(f"no team-colour ring found in the body art ({BODY_DIR}); the platform "
                         "ring must be painted pure green so the turret can register to it")
    # the ELLIPSE's centre, not the mean of its pixels: a ring whose near arc is painted
    # thicker than its far arc drags the pixel mean southward and seats the turret low
    return (xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0, float(xs.max() - xs.min())


def bleed_edges(img, rounds=3):
    """Extend sprite colour into the transparent margin so the resampler never mixes
    in the black behind alpha edges (ts_pack_tree.py's helper)."""
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


def rescale(img, factor, hard_alpha=True, smooth=False):
    """hq4x reconstruction when enlarging a low-res sprite, Lanczos when reducing.

    smooth=True forces the Lanczos path even when enlarging. hq4x reconstructs hard
    edges, which suits a big flat building but wrecks a small busy sprite: on the
    turrets it turns TS's single dark silhouette pixels into solid black blocks at
    the sides. Same trade-off the tree packer settled for TSPROC/TSWEAP."""
    img = bleed_edges(img)
    w, h = max(1, round(img.width * factor)), max(1, round(img.height * factor))
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img.convert("RGB"), (0, 0))
    alpha = img.split()[3]
    if factor > 1.0 and not smooth:
        color = hqx.hq4x(rgb).resize((w, h), Image.LANCZOS)
        alpha = alpha.resize((img.width * 8, img.height * 8), Image.NEAREST)
    else:
        color = rgb.resize((w, h), Image.LANCZOS)
        if factor > 1.0:
            alpha = alpha.resize((img.width * 8, img.height * 8), Image.NEAREST)
    alpha = alpha.resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(color, (0, 0))
    out.putalpha(alpha.point(lambda v: 255 if v >= 128 else 0) if hard_alpha else alpha)
    return out


class Body:
    """A body frame at its final size, carrying where its turret must sit."""

    def __init__(self, img, scale, anchor_bottom=None, ring=None):
        self.img = rescale(img, scale)
        self.ring = ring if ring is not None else ring_of(self.img)
        bb = self.img.getbbox() or (0, 0, self.img.width, self.img.height)
        self.bottom = anchor_bottom if anchor_bottom is not None else bb[3]

    def on_canvas(self, turret_spr=None):
        cv = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        ox = CANVAS_W // 2 - self.img.width // 2
        oy = GROUND_Y - self.bottom
        cv.paste(self.img, (ox, oy), self.img)
        if turret_spr is not None:
            spr, pivot = turret_spr
            k = self.ring[2] / TS_RING_W       # the turret pivots a fixed distance
            px = ox + self.ring[0] + TS_TURRET_OFFSET[0] * k     # above the ring centre,
            py = oy + self.ring[1] + TS_TURRET_OFFSET[1] * k     # measured in ring widths
            cv.paste(spr, (int(round(px - pivot[0])), int(round(py - pivot[1]))), spr)
        return cv


def body_scale(sample):
    """Factor that brings the body's content width to BODY_W."""
    bb = sample.getbbox() or (0, 0, sample.width, sample.height)
    return BODY_W / float(bb[2] - bb[0])


def turret(dirname, facing, ring_w=None, damaged=False, recoil=False):
    """A TS turret rotation frame at the body's scale, with its pivot."""
    im = load_frame(dirname, facing)
    if damaged:
        a = np.array(im).astype(np.float32)
        a[:, :, :3] *= 0.75
        im = Image.fromarray(a.astype(np.uint8), "RGBA")
    k = BODY_W / TS_BODY_PX * TURRET_K
    spr = rescale(im, k, smooth=True)
    px, py = TURRET_PIVOT.get(dirname, (24.0, 13.5))
    pivot = (px * k, py * k)
    if recoil:
        ang = math.radians(facing * 11.25)
        dx = -RECOIL_PX * math.sin(ang)
        dy = RECOIL_PX * math.cos(ang) * 0.5      # the sprite's vertical axis is iso-halved
        moved = Image.new("RGBA", spr.size, (0, 0, 0, 0))
        moved.paste(spr, (int(round(dx)), int(round(dy))), spr)
        spr = moved
    return spr, pivot


def _shim(img, like):
    s = Body.__new__(Body)
    s.img, s.ring, s.bottom = img, like.ring, like.bottom
    return s


def rising_buildup(body, count):
    """Reveal the body from the ground up, for art with no construction frames."""
    bb = body.img.getbbox() or (0, 0, body.img.width, body.img.height)
    top, bottom = bb[1], bb[3]
    out = []
    for k in range(count):
        keep = int(round((bottom - top) * (k + 1) / count))
        f = Image.new("RGBA", body.img.size, (0, 0, 0, 0))
        y = bottom - keep
        f.paste(body.img.crop((0, y, body.img.width, bottom)), (0, y))
        out.append(_shim(f, body).on_canvas())
    return out


def write_zip(ini, frames):
    low = ini.lower()
    out_zip = f"{W.STRUCT_DIR}/{ini}.ZIP"
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for i, cv in enumerate(frames):
            bbox = cv.getbbox() or (0, 0, CANVAS_W, CANVAS_H)
            buf = io.BytesIO(); cv.crop(bbox).save(buf, format="TGA")
            z.writestr(f"{low}-{i:04d}.tga", buf.getvalue())
            z.writestr(f"{low}-{i:04d}.meta", json.dumps({"size": [CANVAS_W, CANVAS_H], "crop": list(bbox)}))
    print(f"wrote {out_zip} ({len(frames)} frames)")
    W.patch_tileset(W.TILESET, ini, len(frames))


def cameo(icon_dir, name):
    src = f"{_dir(icon_dir)}/frame-0000.png"
    if not os.path.exists(src):
        print(f"no {icon_dir}: cameo {name} not written"); return
    icon = Image.open(src).convert("RGBA")
    icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS).save(
        f"{W.ICON_DIR}/{name}.tga")
    print(f"wrote {name}.tga")


def load_bodies():
    raw_h, raw_d = load_frame(BODY_DIR, 0), load_frame(BODY_DIR, 1)
    scale = body_scale(raw_h)
    healthy = Body(raw_h, scale)
    damaged = Body(raw_d, scale, anchor_bottom=healthy.bottom)   # never bob between states
    print(f"body {BODY_DIR}: {raw_h.size} px -> x{scale:.3f}, ring {healthy.ring[2]:.0f} px "
          f"(turret scale x{healthy.ring[2] / TS_RING_W:.2f})")
    return healthy, damaged


def buildup(healthy):
    """TS's GTCTWRMK construction frames, scaled by the TS-body factor so the tower
    under construction matches the finished one's footprint.

    Its tail frames are not construction stages: they are the small debris/fragment
    cels the engine uses elsewhere, and shipping them makes the last third of the
    animation flash tiny coloured scraps. Frames are therefore kept only while they
    carry real building-sized content, then resampled to the count the classic stub
    declares. Art with no construction frames rises out of the ground instead."""
    files = sorted(glob.glob(f"{_dir(MAKE_DIR)}/frame-*.png")) if BODY_DIR == "shp_gtctwr" else []
    areas = []
    for f in files:
        bb = Image.open(f).getbbox()
        areas.append(((bb[2] - bb[0]) * (bb[3] - bb[1])) if bb else 0)
    if not areas or max(areas) == 0:
        return rising_buildup(healthy, MAKE_FRAMES)
    keep = []
    for f, a in zip(files, areas):
        if a < 0.25 * max(areas):
            if keep:            # a runt after real frames = the debris tail, stop here
                break
            continue            # a runt before them = the first specks, skip
        keep.append(f)
    if not keep:
        return rising_buildup(healthy, MAKE_FRAMES)
    scale = BODY_W / TS_BODY_PX
    frames = [Body(Image.open(f).convert("RGBA"), scale, anchor_bottom=healthy.bottom,
                   ring=healthy.ring).on_canvas() for f in keep]
    # resample to the stub's frame count so the engine's timing stays put
    return [frames[min(len(frames) - 1, round(i * (len(frames) - 1) / (MAKE_FRAMES - 1)))]
            for i in range(MAKE_FRAMES)]


def pack():
    healthy, damaged = load_bodies()
    make = buildup(healthy)
    write_zip("TSCTWR", [healthy.on_canvas(), damaged.on_canvas()])
    write_zip("TSCTWRMAKE", make)
    for ini, tdir in TURRETS.items():
        frames = []
        for state in range(4):
            dmg = state >= 2
            base = damaged if dmg else healthy
            for f in range(32):
                frames.append(base.on_canvas(turret(tdir, f, base.ring[2], damaged=dmg, recoil=bool(state % 2))))
        write_zip(ini, frames)
        write_zip(ini + "MAKE", make)
    dims = json.load(open(W.STUB_MANIFEST))
    for ini in ("TSCTWR",) + tuple(TURRETS):
        dims[ini] = [CANVAS_W * 3 // 16, CANVAS_H * 3 // 16]
    json.dump(dims, open(W.STUB_MANIFEST, "w"), indent=1)
    cameo("shp_towricon", "BuildIcon_TS_Ctwr")
    cameo("shp_twr1icon", "BuildIcon_TS_Vulc")
    cameo("shp_twr2icon", "BuildIcon_TS_Rock")
    cameo("shp_twr3icon", "BuildIcon_TS_Csam")
    print(f"buildup frames: {len(make)} (build_tfassets.sh MAKE stubs must match)")


def preview(path):
    healthy, damaged = load_bodies()
    tiles = [healthy.on_canvas()]
    for tdir in TURRETS.values():
        tiles.append(healthy.on_canvas(turret(tdir, 4, healthy.ring[2])))
    tiles.append(damaged.on_canvas(turret("shp_gtctwr_b", 8, damaged.ring[2], damaged=True)))
    tiles.append(buildup(healthy)[MAKE_FRAMES // 2])
    g = Image.new("RGBA", (len(tiles) * CELL_PX, CANVAS_H), (150, 110, 70, 255))
    for k, t in enumerate(tiles):
        g.paste(t, (k * CELL_PX + CELL_PX // 2 - CANVAS_W // 2, 0), t)
    g.crop((0, 60, g.width, 280)).save(path)
    print("wrote", path)


if __name__ == "__main__":
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
    else:
        pack()
