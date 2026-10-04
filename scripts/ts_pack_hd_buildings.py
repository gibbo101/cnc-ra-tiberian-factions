#!/usr/bin/env python3
"""Pack the HD TS buildings (resources/custom-art/ts-buildings-hd/<src>/) and units
(resources/custom-art/ts-units-hd/<src>/) into the mod tree.

Each source folder holds buildings drawn on RA's square grid, the plot centred in the canvas
(-trim.png masks sit beside every frame and are not packed). A building's tileset frames are
either finished frames taken as they are, or composed: the building (healthy, damaged) with
overlays drawn over it, per state the runs in order (the idle loop, then the active run when the
building has one), each frame carrying every overlay's frame i mod its length, so a one-frame
overlay holds still. The damaged block starts where the healthy one ends, which is where
Shape_Number looks for it (the largest end of the IDLE and ACTIVE ranges in bdata.cpp).

Written per building, to the asset pack scripts/asset_packs.py routes each name to (the
TS-HD-Graphics-Pack), its tileset XML patched in place:
  <INI>.ZIP       the tileset frames
  <INI>MAKE.ZIP   the build-up, when the building builds up on the map
Units go to UNITS/, and a building's concrete apron is cut from its layer into 128 px ground
tiles, one per cell of its smudge, the same in every theatre. A unit whose shells
leave a barrel drawn in its frames also writes redalert/<ini>_muzzle.h: the barrel tip per
turret facing, in leptons from the unit's position, read from the art's muzzle table.

The canvas is padded evenly to a height that is a multiple of 16, so the classic stub
(canvas x 3/16, scripts/ts_stub_dims.json) is a whole number and the plot stays centred.
Pixels at alpha 4 or less are cleared: they are invisible, and a veil of them over the
canvas would stop every frame cropping.

Usage: ts_pack_hd_buildings.py [INI ...]   (buildings, units and aprons by ini; none = all)
License: GPL v3.
"""
import io, json, math, os, re, sys, zipfile
import numpy as np
from PIL import Image

import asset_packs

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(SCRIPTS, "..", "resources", "custom-art", "ts-buildings-hd")
UNITS_SRC = os.path.join(SCRIPTS, "..", "resources", "custom-art", "ts-units-hd")
REDALERT = os.path.join(SCRIPTS, "..", "redalert")
THEATRES = ("TEMPERATE", "SNOW", "INTERIOR")
STUB_MANIFEST = f"{SCRIPTS}/ts_stub_dims.json"
HAZE_ALPHA = 4

# GDI's weathered eagle, painted on the dropship bay's deck. It comes on a black field with no alpha of its own.
EAGLE = os.path.join(SCRIPTS, "..", "resources", "custom-cameos", "ts-gdi-logo.png")
# RA's camera looks down at 32 degrees, so a flat disc on the ground is drawn sin(32) as tall as it is wide.
GROUND_SQUASH = math.sin(math.radians(32))
LUMA = np.array([0.299, 0.587, 0.114], np.float32)
# Paint covers this much of the deck under it; the rest shows through as wear.
PAINT_COVER = 0.92

# The launcher recolours every green of a building to its owner's colour, so Tiberium seen in a
# building is drawn in the yellow-green TD's silo shows in game (hue ~77), luminance kept.
TIBERIUM = np.array([191.0, 231.0, 90.0])


# The war factory's hazard stripes, on the lane from its door (x 160-316, y 370-416 of its source canvas).
# The apron under them is ground art, which the launcher never recolours, so the stripes there and on the
# build-up that shows the same lane are all burnt to the gold the launcher makes of that green ramp,
# (v, 0.82v, 0), and the two meet without a seam. Hazard markings are yellow in TS whoever owns them.
WEAP_LANE = (160, 370, 316, 416)


def lane_gold(img):
    """The lane's house green, antialiased edges included, as gold: a pixel's green beyond its red
    and blue is the stripe's share of it, and that share turns from (0, e, 0) to (e, 0.82e, 0)."""
    a = np.asarray(img).copy()
    x0, y0, x1, y1 = WEAP_LANE
    box = a[y0:y1, x0:x1].astype(np.int32)
    r, g, b = box[..., 0].copy(), box[..., 1].copy(), box[..., 2].copy()
    e = g - np.maximum(r, b)
    hit = (box[..., 3] > 0) & (e > 4)
    box[hit, 0] = np.minimum(r[hit] + e[hit], 255)
    box[hit, 1] = np.maximum(r[hit], b[hit]) + np.round(e[hit] * 0.82)
    a[y0:y1, x0:x1] = box.astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def decal_art(path, width, squash=GROUND_SQUASH):
    """The emblem as a flat disc seen by RA's camera, width px across (squash=1: seen from straight above).
    Its black field is keyed out softly, so the edges stay antialiased."""
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    alpha = np.clip((rgb.sum(2) - 20) / 70, 0, 1) * 255
    art = Image.fromarray(np.dstack([rgb, alpha]).round().astype(np.uint8), "RGBA")
    art = art.crop(art.getbbox())
    return art.resize((width, round(width * squash)), Image.LANCZOS)


def paint_decal(img, decal, healthy=None):
    """The frame with the decal painted on its flat deck, centred at decal["centre"]: the paint takes the
    deck's own light and texture, and the deck's lamps shine through it. healthy, given for a damaged frame,
    is the same frame undamaged: the paint is gone where the deck is gone, under rubble and where the deck
    burnt black, and darkens with the scorch around that. The paint must not reach the house-colour band."""
    art = decal_art(decal["art"], decal["width"])
    d = np.asarray(art).astype(np.float32)
    h, w = d.shape[:2]
    x0 = round(decal["centre"][0] - w / 2)
    y0 = round(decal["centre"][1] - h / 2)
    out = np.asarray(img).astype(np.float32).copy()
    deck = out[y0:y0 + h, x0:x0 + w]
    ref = np.asarray(healthy if healthy is not None else img).astype(np.float32)[y0:y0 + h, x0:x0 + w]
    lum, ref_lum = deck[..., :3] @ LUMA, ref[..., :3] @ LUMA
    a = d[..., 3] / 255
    band = (ref[..., 3] > 0) & (ref[..., 1] - np.maximum(ref[..., 0], ref[..., 2]) > 30)
    if (band & (a > 0.01)).any():
        raise SystemExit(f"the decal at {decal['centre']} reaches the house-colour band")
    flat = np.median(ref_lum[a > 0])
    a = a * PAINT_COVER
    if healthy is not None:
        ratio = lum / np.maximum(ref_lum, 1)
        tint = np.abs(deck[..., :3] / np.maximum(lum, 1)[..., None]
                      - ref[..., :3] / np.maximum(ref_lum, 1)[..., None]).sum(2)
        a = (a * deck[..., 3] / 255
             * (1 - np.clip((lum - ref_lum - 15) / 20, 0, 1))     # rubble lying on the deck
             * (1 - np.clip((tint - 0.15) / 0.15, 0, 1))          # debris of other materials
             * np.clip((ratio - 0.45) / 0.35, 0, 1))              # deck burnt black
    paint = d[..., :3] * np.clip(lum / flat, 0, 1.3)[..., None]
    rgb = deck[..., :3] * (1 - a[..., None]) + paint * a[..., None]
    lamp = np.clip((ref_lum - flat - 12) / 20, 0, 1)[..., None]
    deck[..., :3] = rgb + lamp * (np.maximum(rgb, deck[..., :3]) - rgb)
    return Image.fromarray(out.round().clip(0, 255).astype(np.uint8), "RGBA")


def with_decal(tiles, make, decal):
    """Tiles healthy then damaged, each damaged frame against its healthy twin, and the build-up from frame
    decal["from_make"] on, all with the decal painted."""
    half = len(tiles) // 2
    tiles = ([paint_decal(t, decal) for t in tiles[:half]]
             + [paint_decal(t, decal, tiles[i]) for i, t in enumerate(tiles[half:])])
    make = make[:decal["from_make"]] + [paint_decal(m, decal) for m in make[decal["from_make"]:]]
    return tiles, make


def tiberium(img):
    a = np.asarray(img).astype(np.float32)
    lum = a[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)
    rgb = TIBERIUM[None, None, :] * (lum / (TIBERIUM @ np.array([0.299, 0.587, 0.114])))[..., None]
    a[..., :3] = np.clip(rgb, 0, 255)
    return Image.fromarray(a.round().astype(np.uint8), "RGBA")


# ini: the source folder, the build-up as (path prefix, frames) or None, and the tileset
# frames, either frames=(path prefix, count) or base=path prefix with runs=[(frames,
# overlays)], overlays as (path prefix, healthy frames, damaged frames[, recolour]), recolour
# a function applied to the overlay before it is drawn. blocks=[overlays, ...]
# repeats the whole healthy + damaged set once per entry with those overlays drawn first.
# pad_bottom / pad_top add that many transparent px under / over every frame and crop_top cuts
# that many empty px off the top, for art drawn on a plot of another depth than the building's own (the canvas
# centres on the building's plot); crop=(x0, y0, x1, y1) cuts every frame to that box, which holds all the art. repeat=n plays the frames n times over (one set for both states), and
# recolour / make_recolour apply a function to every tileset / build-up frame as it loads, and decal=dict(art, centre,
# width, from_make) paints a flat emblem on the deck (source canvas px), the build-up from frame from_make on.
# make_pick takes those build-up frames, in that order, instead of all of them.
# Paths take -NN.png.
BUILDINGS = {
    "TSFACT": dict(src="tsfact", make=("build-up/construction-yard-build", 32),
                   base="yard/construction-yard", runs=[
        # idle: fans turning, the door lamp sweeping, the roof lamps pulsing
        (30, [("A-fans/construction-yard-fans", range(0, 10), range(10, 20)),
              ("B-door-lamp/construction-yard-door-lamp", range(0, 10), range(10, 20)),
              ("C-roof-lamps/construction-yard-roof-lamps", range(0, 15), range(15, 30))]),
        # active, while a placed building goes up: the hangar lights up and the claw builds a
        # crate; the roof lamps hold steady and the door lamp is off (the producing art covers it)
        (20, [("A-fans/construction-yard-fans", range(0, 10), range(10, 20)),
              ("C-roof-lamps/construction-yard-roof-lamps", [8], [23]),
              ("D-producing/construction-yard-producing", range(0, 20), range(0, 20))]),
    ]),
    # one block per turbine level (1, 2, 3 pods), each 12 healthy then 12 damaged frames of
    # the tower's lights and the pods turning: the block Shape_Number picks by UpgradeLevel
    "TSPOWR": dict(src="tspowr", make=("build-up/power-plant-build", 24),
                   frames=("loop/power-plant-loop", 72)),
    # the turbine's placement ghost; it never stands on the map, it installs into a plant
    "TSTURB": dict(src="tspowr", make=None, frames=("pod-128/power-pod", 2)),
    # one block per fill level (empty, a third, two thirds, full: the Tiberium through the glass),
    # each the lamps' 16-frame loop healthy then damaged: the block Shape_Number picks by how
    # full the house's storage is
    # the bunkers on the 2x1 plot row: the art is drawn on a 2x2, its foundation's south edge on
    # the south edge, so 128 px under it centres the canvas on the 2x1 with the bib row in front.
    # Idle: the flag waving (7) under the entrance lamps and the mast's beacon (8): 56 frames
    "TSPILE": dict(src="tspile", make=("build-up/barracks-build", 24), base="building/barracks", runs=[
        (56, [("C-flag/barracks-flag", range(0, 7), range(7, 14)),
              ("A-lamps/barracks-lamps", range(0, 8), range(8, 16)),
              ("B-beacon/barracks-beacon", range(0, 8), range(8, 16))]),
    ], pad_bottom=128),
    # TS's wedge its own way round, drawn on a 3x1 row: 128 px over it centre the canvas on the 3x2
    # plot, the wedge on the south row, the fins and dome in the north row, the bib row in front.
    # Idle: the dome's panels pulse (8), healthy then damaged.
    "TSTECH": dict(src="tstech", make=("build-up/tech-center-build", 24),
                   frames=("loop/tech-center-loop", 16), pad_top=128),
    # The silo stands on its 2x1 plot row with the bib row in front, seated like the barracks.
    "TSSILO": dict(src="tssilo", make=("build-up/silo-build", 24), base="silo/silo",
                   blocks=[[("A-tiberium/silo-tiberium", [lv], [lv + 4], tiberium)] for lv in range(4)],
                   runs=[(16, [("B-lamps/silo-lamps", range(0, 16), range(16, 32))])], pad_bottom=128),
    # The refinery turned 22.5 degrees on its 4x3 plot. Idle: the dock lamps (16), healthy then
    # damaged; the flare stack's fire is its own layer (20 lit frames, then 20 empty).
    "TSPROC": dict(src="tsproc", make=("build-up/refinery-build", 24), frames=("loop/refinery-loop", 32)),
    "TSPROCFR": dict(src="tsproc", make=None, frames=("B-fire/refinery-fire", 40)),
    # its front: the building in front of the dock lane, the idle loop's frames masked to it, drawn over a docked
    # truck so it backs in under the deck
    "TSPROCNF": dict(src="tsproc", make=None, frames=("front/refinery-front", 32)),
    # The war factory on its 3x4 plot, door south: RA's 3x3 war factory slot with an empty row behind it, the art's
    # own 480x512 canvas centred on it (the build-up's raised poles reach into the empty row). Its body is
    # the door bay with the building's ground shadow, under units; the near face (the rest of the building,
    # with the door lamps (16, a four-lamp run), the roof lamps (8) and the fans (4) over 32 idle steps) and the roll-up door
    # draw over a vehicle in the bay. The under-door is the doorway seen with the door up, and its build-up the 26
    # frames of TS's GTWEAPMK order.
    "TSWEAP": dict(src="tsweap", make=("build-up/war-factory-build", 26), make_recolour=lane_gold,
                   base="building-bay/war-factory-bay", runs=[(32, [])]),
    "TSWEAPNF": dict(src="tsweap", make=None, base="2-over-units/war-factory-over", runs=[
        (32, [("A-lamps/war-factory-lamps", range(0, 16), range(16, 32)),
              ("B-lamps/war-factory-lamps-b", range(0, 8), range(8, 16)),
              ("C-fans/war-factory-fans", range(0, 4), range(4, 8))]),
    ]),
    "TSWEAPDR": dict(src="tsweap", make=None, frames=("D-door/war-factory-door", 9), repeat=2),
    "TSWEAPUD": dict(src="tsweap", make=None, frames=("1-under-door/war-factory-under", 2), repeat=2),
    # The radar on its 2x2 plot, the tower and its antennas rising into the headroom above. Idle: the dish
    # turning there and back (28), healthy then damaged.
    "TSRADR": dict(src="tsradr", make=("build-up/radar-build", 26), frames=("loop/radar-loop", 56)),
    # The deployed Mobile Sensor Array on its 1x1 plot, broadside, the mast at its west end. Idle: the
    # head's flash (5), healthy then damaged. The build-up is the vehicle settling and raising the mast.
    "TSDPSA": dict(src="tsdpsa", make=("build-up/sensor-array-build", 36), frames=("loop/sensor-array-loop", 10)),
    # The service depot turned a quarter on its 3x3 plot: the gantry across the back two rows, the pad in
    # front of it. Idle: the guide lights (5) and the hood's glow (7) together over 35 steps, healthy then
    # damaged; while it repairs, the pad's flash (7 healthy, 7 damaged) is its own layer.
    "TSDEPT": dict(src="tsdept", make=("build-up/depot-build", 19), frames=("loop/depot-loop", 70)),
    "TSDEPTRP": dict(src="tsdept", make=None, frames=("D-flash/depot-flash", 14)),
    # The helipad on its 2x2 plot, the machinery down the west side. Idle: the pad's lights (8), healthy
    # then damaged.
    "TSHPAD": dict(src="tshpad", make=("build-up/helipad-build", 24), frames=("loop/helipad-loop", 16)),
    # The dropship bay's pad, centred on its 3x2 plot: the art comes on a wider canvas round a 3x3, cut to
    # the 3x2 here so the pad's centre is the plot's. GDI's eagle is painted across the deck inside the band,
    # over the gratings, from the build-up frame that paints the band on.
    # The upgrade center on its 3x2 plot, turned a quarter (TS's east end to the camera). Its idle loop
    # is baked per plug combination in the order building.cpp's TF_Plug_Art_Block numbers them: none,
    # each plug alone in the right-hand socket, then each ordered pair (right, left), plugs taken
    # ion, pods, seeker. Each block is 40 healthy then 40 damaged frames of the dish, lamps and slot.
    "TSPLUG": dict(src="tsplug", make=("build-up/upgrade-center-build", 24),
                   combos=("none", "right-ion", "right-pods", "right-seeker", "right-ion_left-pods",
                           "right-ion_left-seeker", "right-pods_left-ion", "right-pods_left-seeker",
                           "right-seeker_left-ion", "right-seeker_left-pods"),
                   base="base/{combo}/upgrade-center-{combo}", loop=40,
                   overlays=(("A-dish/upgrade-center-dish", 20), ("B-lamps/upgrade-center-lamps", 10),
                             ("C-slot/upgrade-center-slot", 8))),
    # The plugs' placement ghosts (never on the map: a plug installs into an upgrade center), healthy
    # and damaged, standing in the right-hand socket's window.
    "TSPION": dict(src="tsplug", make=None, frames=("plugs/ion-cannon-uplink/ion-cannon-uplink", 16), pick=(0, 15)),
    "TSPODS": dict(src="tsplug", make=None, frames=("plugs/drop-pod-node/drop-pod-node", 16), pick=(0, 15)),
    "TSSEEK": dict(src="tsplug", make=None, frames=("plugs/seeker-control/seeker-control", 16), pick=(0, 15)),
    "TSDROP": dict(src="tsdrop", make=("build-up/dropbay-build", 19), frames=("building/dropbay", 2),
                   crop=(192, 226, 576, 482), decal=dict(art=EAGLE, centre=(384, 338), width=180, from_make=14)),
    # The EMP cannon's mound on its 2x2 plot, healthy and damaged, with the head as its own layer. The
    # build-up is every other frame of the 24 delivered, ending on the finished mound: 13 frames, the last
    # three of which carry the head (building.cpp seats it from build-up stage 10).
    "TSPULS": dict(src="tspuls", make=("build-up/pulse-cannon-build", 24), make_pick=[*range(0, 24, 2), 23],
                   frames=("building/pulse-cannon", 2)),
    # The head in 32 facings, drawn in place over the mound on the mound's canvas. building.cpp draws it
    # TSPULS_TURRET_Y (10 classic px, 53 canvas px) lower than the mound, so it is packed 53 px higher.
    "TSPULST": dict(src="tspuls", make=None, frames=("head/pulse-cannon-head", 32), crop_top=53, pad_bottom=53),
    # The Firestorm generator on its 3x2 plot: the dome raised, the pit's lightning and the fins' lamps
    # playing (48), healthy then damaged.
    "TSFGEN": dict(src="tsfgen", make=("build-up/firestorm-generator-build", 19),
                   frames=("loop/firestorm-generator-loop", 96)),
    # A Firestorm wall section on its cell, in the wall view: the neighbour mask (N1 E2 S4 W8), +16
    # damaged, +32 with the field on.
    "TSFSDF": dict(src="tsfsdf", make=None, frames=("wall/firestorm-wall", 64)),
    # The limpet mine dug in on its cell: its lens flashing (10), healthy then damaged. The build-up is
    # all 42 of TS's DLIMPMK frames, the drone landing and digging in.
    "TSDLIMP": dict(src="tsdlimp", make=("build-up/limpet-mine-build", 42), frames=("loop/limpet-mine-loop", 20)),
}
# The open-door near face is the same layer: the door is its own layer here.
BUILDINGS["TSWEAPNU"] = BUILDINGS["TSWEAPNF"]

# ini: the source folder and the frames (path prefix, count) on the unit's own canvas. root
# overrides the folder the source sits in, digits the frame number's width, and muzzle names the
# art's table of barrel tips (frame, facing, canvas x, canvas y) for the generated header. kind is
# the art folder (UNITS unless named); centred crops every frame about the canvas centre.
def _voxel_unit(src, count, **extra):
    return dict(root=UNITS_SRC, src=src, frames=(f"frames/{src}", count), digits=4, centred=True, **extra)


UNITS = {
    "TSHARV": dict(src="tsproc", frames=("harvester/harvester", 64)),
    "TSTITN": dict(root=UNITS_SRC, src="tstitn", frames=("frames/tstitn", 128), digits=4,
                   muzzle="3d/muzzle.txt"),
    "TSMCV": dict(root=UNITS_SRC, src="tsmcv", frames=("frames/tsmcv", 32), digits=4),
    "TSSMEC": dict(root=UNITS_SRC, src="tssmec", frames=("frames/tssmec", 128), digits=4),
    "TS4TNK": _voxel_unit("ts4tnk", 64),
    "TSAPC": _voxel_unit("tsapc", 64),
    "TSCARRY": _voxel_unit("tscarry", 32),
    "TSHMEC": _voxel_unit("tshmec", 256),
    "TSHVR": _voxel_unit("tshvr", 96),
    "TSLPST": _voxel_unit("tslpst", 32),
    "TSMEMP": _voxel_unit("tsmemp", 32),
    "TSMEMPFX": dict(root=UNITS_SRC, src="tsmemp", frames=("fx/tsmempfx", 12), digits=4, centred=True, kind="VFX"),
    "TSMWAR": _voxel_unit("tsmwar", 32),
    "TSORCA": _voxel_unit("tsorca", 32),
    "TSORCAB": _voxel_unit("tsorcab", 32),
    "TSSAPC": _voxel_unit("tssapc", 113),
    "TSSONIC": _voxel_unit("tssonic", 64),
    "TSSUBTANK": _voxel_unit("tssubtank", 113),
    "TSDSHP": dict(root=UNITS_SRC, src="tsdshp", frames=("frames/tsdshp", 4), digits=4, kind="VFX"),
    "TSHUNT": _voxel_unit("tshunt", 8),
    "TSLIMP": _voxel_unit("tslimp", 20),
    "TSJUGG": _voxel_unit("tsjugg", 202, lead_muzzle=dict(table="muzzle.txt", sets=((120, 32), (152, 32)))),
    "TSE1": _voxel_unit("tse1", 292),
    "TSE2": _voxel_unit("tse2", 292),
    "TSENGINEER": _voxel_unit("tsengineer", 292),
    "TSGHOST": _voxel_unit("tsghost", 292),
    "TSMEDIC": _voxel_unit("tsmedic", 307),
    "TSJUMPJET": _voxel_unit("tsjumpjet", 451),
    "R2APOC": _voxel_unit("r2apoc", 64),
    "R2PRIS": _voxel_unit("r2pris", 64),
}

# smudge ini: the source folder, the apron's layer on its building's canvas, where the smudge's
# north-west cell starts on that canvas, and the smudge's size in cells (sdata.cpp).
APRONS = {
    "TSPROCBB": dict(src="tsproc", layer="bib/refinery-bib-00", origin=(112, 272), cells=(5, 3)),
    "TSWEAPBB": dict(src="tsweap", layer="bib/war-factory-bib-00", origin=(48, 128), cells=(3, 3),
                     recolour=lane_gold),
}


def clean(img):
    a = np.asarray(img).copy()
    a[a[..., 3] <= HAZE_ALPHA] = 0
    return Image.fromarray(a, "RGBA")


def pad_to(img, w, h):
    if img.size == (w, h):
        return img
    if img.width > w or img.height > h or (w - img.width) % 2 or (h - img.height) % 2:
        raise SystemExit(f"cannot centre a {img.size} frame on {w}x{h}")
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(img, ((w - img.width) // 2, (h - img.height) // 2))
    return out


def crop_to(img, box):
    a = np.asarray(img)[..., 3].copy()
    x0, y0, x1, y1 = box
    a[y0:y1, x0:x1] = 0
    if a.max() > HAZE_ALPHA:
        raise SystemExit(f"cannot crop to {box}: art stands outside it")
    return img.crop(box)


def crop_above(img, px):
    if np.asarray(img)[:px, :, 3].max() > HAZE_ALPHA:
        raise SystemExit(f"cannot cut {px} px off the top: art stands there")
    return img.crop((0, px, img.width, img.height))


def pad_over(img, px):
    out = Image.new("RGBA", (img.width, img.height + px), (0, 0, 0, 0))
    out.paste(img, (0, px))
    return out


def pad_under(img, px):
    out = Image.new("RGBA", (img.width, img.height + px), (0, 0, 0, 0))
    out.paste(img, (0, 0))
    return out


def frames(src, spec):
    def load(path, i):
        return Image.open(os.path.join(src, f"{path}-{i:02d}.png")).convert("RGBA")

    if "frames" in spec:
        path, count = spec["frames"]
        tiles = [load(path, i) for i in spec.get("pick", range(count))] * spec.get("repeat", 1)
    elif "combos" in spec:
        # One block per combination: its base (healthy, then damaged) with the idle overlays looping
        # over it, each overlay's damaged frames following its healthy ones.
        tiles = []
        for combo in spec["combos"]:
            for state in (0, 1):
                base = load(spec["base"].format(combo=combo), state)
                for t in range(spec["loop"]):
                    img = base.copy()
                    for path, n in spec["overlays"]:
                        img.alpha_composite(load(path, t % n + n * state))
                    tiles.append(img)
    else:
        tiles = []
        for block in spec.get("blocks", [[]]):
            for state in (0, 1):
                base = load(spec["base"], state)
                for count, overlays in spec["runs"]:
                    for i in range(count):
                        img = base.copy()
                        for path, healthy, damaged, *recolour in block + overlays:
                            seq = (healthy, damaged)[state]
                            o = load(path, seq[i % len(seq)])
                            img.alpha_composite(recolour[0](o) if recolour else o)
                        tiles.append(img)
    make = []
    if spec["make"]:
        path, count = spec["make"]
        make = [load(path, i) for i in spec.get("make_pick", range(count))]
    if spec.get("recolour"):
        tiles = [spec["recolour"](i) for i in tiles]
    if spec.get("make_recolour"):
        make = [spec["make_recolour"](i) for i in make]
    return tiles, make


def canvas_for(imgs):
    w = max(i.width for i in imgs)
    h = max(i.height for i in imgs)
    return w + (-w % 16), h + (-h % 16)


def centred_box(b, width, height):
    """The smallest box holding b whose centre is the canvas centre."""
    rx = max(width / 2 - b[0], b[2] - width / 2)
    ry = max(height / 2 - b[1], b[3] - height / 2)
    x0, y0 = max(0, math.floor(width / 2 - rx)), max(0, math.floor(height / 2 - ry))
    return x0, y0, width - x0, height - y0


def write_zip(path, name, frames, centred=False):
    """Each frame cropped to its content, with a .meta giving the canvas and the crop box.
    centred crops each frame to a box centred on the canvas, so the frame lands in the same
    place whether the launcher anchors the canvas centre or the crop's centre.
    Entries carry a fixed date, so the same frames always pack to the same bytes."""
    def put(z, member, data):
        z.writestr(zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0)), data, zipfile.ZIP_DEFLATED)

    with zipfile.ZipFile(path, "w") as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            b = img.getbbox() or (0, 0, img.width, img.height)
            if centred:
                b = centred_box(b, img.width, img.height)
            buf = io.BytesIO()
            img.crop(b).save(buf, format="TGA")
            put(z, base + ".tga", buf.getvalue())
            put(z, base + ".meta", json.dumps(
                {"size": [img.width, img.height], "crop": [b[0], b[1], b[2], b[3]]}))
    print(f"wrote {os.path.relpath(path)} ({len(frames)} frames)")


def tile_block(name, shape):
    return ("\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n"
            "\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s\\%s-%04d.tga</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n"
            % (name, shape, name.lower(), name.lower(), shape))


def patch_in_place(name, count, xml_path):
    """Install exactly `count` tiles for `name` where its tiles already stand (appended when
    it has none), leaving every other tile of the file where it is."""
    with open(xml_path, encoding="utf-8", newline="") as f:
        xml = f.read()
    nl = "\r\n" if "\r\n" in xml else "\n"
    blocks = "".join(tile_block(name, s) for s in range(count)).replace("\n", nl)
    pat = re.compile(r"\t<Tile>" + nl + r"\t\t<Key>" + nl + r"\t\t\t<Name>" + re.escape(name)
                     + r"</Name>.*?</Tile>" + nl, re.S)
    runs = list(pat.finditer(xml))
    if runs:
        xml = xml[:runs[0].start()] + blocks + pat.sub("", xml[runs[0].start():])
    else:
        idx = xml.rindex("</Tiles>")
        xml = xml[:idx] + blocks + xml[idx:]
    with open(xml_path, "w", encoding="utf-8", newline="") as f:
        f.write(xml)
    print(f"patched {os.path.basename(xml_path)}: {name} -> {count} tiles (replaced {len(runs)})")


def pack(name, tiles, make, size):
    write_zip(asset_packs.art_zip(name, "STRUCTURES"), name.lower(), [clean(pad_to(i, *size)) for i in tiles])
    patch_in_place(name, len(tiles), asset_packs.tileset_xml(name, "STRUCTURES"))
    if make:
        write_zip(asset_packs.art_zip(f"{name}MAKE", "STRUCTURES"), f"{name.lower()}make",
                  [clean(pad_to(i, *size)) for i in make])
        patch_in_place(f"{name}MAKE", len(make), asset_packs.tileset_xml(f"{name}MAKE", "STRUCTURES"))


def pack_unit(name, spec):
    path, count = spec["frames"]
    src = os.path.join(spec.get("root", SRC), spec["src"])
    digits = spec.get("digits", 2)
    tiles = [Image.open(os.path.join(src, f"{path}-{i:0{digits}d}.png")).convert("RGBA") for i in range(count)]
    kind = spec.get("kind", "UNITS")
    write_zip(asset_packs.art_zip(name, kind), name.lower(), [clean(i) for i in tiles], spec.get("centred", False))
    patch_in_place(name, count, asset_packs.tileset_xml(name, kind))
    if spec.get("muzzle"):
        write_muzzle(name, os.path.join(src, spec["muzzle"]), tiles[0].size)
    if spec.get("lead_muzzle"):
        lead = spec["lead_muzzle"]
        write_lead_muzzle(name, os.path.join(src, lead["table"]), tiles[0].size, lead["sets"])


def write_muzzle(name, table, size):
    """The barrel tip per turret facing (counter-clockwise from north, the engine's frame order)
    as leptons east and south of the unit's position, which is the canvas centre. The canvas
    draws at 8 px per classic pixel, so one canvas px is 4/3 lepton."""
    rows = []
    with open(table) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 4 and all(re.fullmatch(r"-?\d+(\.\d+)?", p) for p in parts):
                rows.append((int(parts[1]), float(parts[2]), float(parts[3])))
    rows.sort()
    assert [r[0] for r in rows] == list(range(len(rows))), f"{table}: facings out of order"
    cx, cy = size[0] / 2, size[1] / 2
    var = f"_{name.lower()}_muzzle"
    out = [f"// GENERATED by scripts/ts_pack_hd_buildings.py from {os.path.relpath(table, os.path.join(SCRIPTS, '..'))}; do not hand-edit.",
           "// Per-CCW-turret-facing muzzle offsets (leptons from unit center).",
           f"static const short {var}[{len(rows)}][2] = {{"]
    out += [f"    {{{round((x - cx) * 4 / 3)}, {round((y - cy) * 4 / 3)}}}," for _, x, y in rows]
    out.append("};")
    path = os.path.join(REDALERT, f"{name.lower()}_muzzle.h")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"wrote {os.path.relpath(path)} ({len(rows)} facings)")


LEAD_TOLERANCE_PX = 8


def write_lead_muzzle(name, table, size, sets):
    """The fire point per facing for each set of frames (first frame, count), from the art's table of
    barrel tips (frame, then x y for each barrel, then their mean): the tips within LEAD_TOLERANCE_PX
    of the one furthest forward along the facing, averaged, so a broadside volley leaves from the
    middle of the barrels and an angled one from the leading barrel. Leptons east and south of the
    unit's position, the canvas centre, at 4/3 lepton per canvas px."""
    tips = {}
    with open(table) as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 5 and parts[0].isdigit():
                v = [float(p) for p in parts[1:]]
                tips[int(parts[0])] = [(v[i], v[i + 1]) for i in range(0, len(v) - 2, 2)]
    cx, cy = size[0] / 2, size[1] / 2
    blocks = []
    for first, count in sets:
        rows = []
        for facing in range(count):
            th = math.radians(facing * 11.25)
            fx, fy = -math.sin(th), -math.cos(th) / 2
            ahead = [x * fx + y * fy for x, y in tips[first + facing]]
            lead = [t for t, a in zip(tips[first + facing], ahead) if a >= max(ahead) - LEAD_TOLERANCE_PX]
            x = sum(t[0] for t in lead) / len(lead)
            y = sum(t[1] for t in lead) / len(lead)
            rows.append((round((x - cx) * 4 / 3), round((y - cy) * 4 / 3)))
        blocks.append(rows)
    var = f"_{name.lower()}_muzzle"
    out = [f"// GENERATED by scripts/ts_pack_hd_buildings.py from {os.path.relpath(table, os.path.join(SCRIPTS, '..'))}; do not hand-edit.",
           "// Leading barrel tips (leptons from the unit centre), per CCW facing, one set per frame set.",
           f"static const short {var}[{len(blocks)}][{len(blocks[0])}][2] = {{"]
    for rows in blocks:
        out.append("    {")
        out += [f"        {{{x}, {y}}}," for x, y in rows]
        out.append("    },")
    out.append("};")
    path = os.path.join(REDALERT, f"{name.lower()}_muzzle.h")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"wrote {os.path.relpath(path)} ({len(blocks)} x {len(blocks[0])} facings)")


def pack_apron(name, spec):
    """One full 128 px tile per smudge cell, row by row from the north-west, in every theatre's
    archive and tileset."""
    layer = Image.open(os.path.join(SRC, spec["src"], spec["layer"] + ".png")).convert("RGBA")
    layer = clean(spec["recolour"](layer) if spec.get("recolour") else layer)
    (x0, y0), (cols, rows) = spec["origin"], spec["cells"]
    tiles = [layer.crop((x0 + 128 * c, y0 + 128 * r, x0 + 128 * (c + 1), y0 + 128 * (r + 1)))
             for r in range(rows) for c in range(cols)]
    for theatre in THEATRES:
        path = asset_packs.art_zip(name, f"TERRAIN_{theatre}")
        with zipfile.ZipFile(path, "w") as z:
            for i, img in enumerate(tiles):
                buf = io.BytesIO()
                img.save(buf, format="TGA")
                for member, data in ((f"{name.lower()}-{i:04d}.tga", buf.getvalue()),
                                     (f"{name.lower()}-{i:04d}.meta",
                                      json.dumps({"size": [128, 128], "crop": [0, 0, 128, 128]}))):
                    z.writestr(zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0)), data, zipfile.ZIP_DEFLATED)
        print(f"wrote {os.path.relpath(path)} ({len(tiles)} tiles)")
        patch_in_place(name, len(tiles), asset_packs.tileset_xml(name, f"TERRAIN_{theatre}"))


def keep_centred(packed):
    """The vehicles scripts/unit_centring.py centres are centred again after a re-pack (their hull's
    offset measured and the drop recorded, as that script does), and art that rides with a vehicle
    (the deployed sensor) moves by its vehicle's recorded drop."""
    import unit_centring as uc
    drops = json.load(open(uc.DROPS_JSON))
    moved = False
    for name, (hull_frames, _, _, _, partners) in uc.UNITS.items():
        if name in packed:
            path = asset_packs.art_zip(name, "UNITS")
            _, data = uc.read_zip(path)
            offset = uc.hull_offset(data, hull_frames)
            if abs(offset) >= uc.TOLERANCE:
                dy = -round(offset * uc.UNIT_DENSITY)
                uc.shift_zip(path, dy)
                drops[name] = dy
                moved = True
                print(f"{name}: hull centred, moved {dy:+d} canvas px")
        for partner, kind, density in partners:
            if (partner in packed or partner.removesuffix("MAKE") in packed) and name in drops:
                uc.shift_zip(asset_packs.art_zip(partner, kind), round(drops[name] / uc.UNIT_DENSITY * density))
                print(f"{partner}: moved with {name}")
    if moved:
        with open(uc.DROPS_JSON, "w") as f:
            json.dump(dict(sorted(drops.items())), f, indent=2)
            f.write("\n")
        uc.write_header(drops)


def main(argv):
    every = list(BUILDINGS) + list(UNITS) + list(APRONS)
    asked = [a for a in argv if a in every] or every
    for name in asked:
        if name in UNITS:
            pack_unit(name, UNITS[name])
        elif name in APRONS:
            pack_apron(name, APRONS[name])
    names = [a for a in asked if a in BUILDINGS]
    with open(STUB_MANIFEST) as f:
        stubs = json.load(f)
    for ini in names:
        spec = BUILDINGS[ini]
        tiles, make = frames(os.path.join(SRC, spec["src"]), spec)
        if spec.get("decal"):
            tiles, make = with_decal(tiles, make, spec["decal"])
        if spec.get("crop"):
            tiles = [crop_to(i, spec["crop"]) for i in tiles]
            make = [crop_to(i, spec["crop"]) for i in make]
        if spec.get("crop_top"):
            tiles = [crop_above(i, spec["crop_top"]) for i in tiles]
            make = [crop_above(i, spec["crop_top"]) for i in make]
        if spec.get("pad_top"):
            tiles = [pad_over(i, spec["pad_top"]) for i in tiles]
            make = [pad_over(i, spec["pad_top"]) for i in make]
        if spec.get("pad_bottom"):
            tiles = [pad_under(i, spec["pad_bottom"]) for i in tiles]
            make = [pad_under(i, spec["pad_bottom"]) for i in make]
        size = canvas_for(tiles + make)
        pack(ini, tiles, make, size)
        stubs[ini] = [size[0] * 3 // 16, size[1] * 3 // 16]
        print(f"{ini}: canvas {size[0]}x{size[1]}, stub {stubs[ini][0]}x{stubs[ini][1]}")
    with open(STUB_MANIFEST, "w") as f:
        json.dump(stubs, f, indent=1)
        f.write("\n")
    keep_centred(asked)


if __name__ == "__main__":
    main(sys.argv[1:])
