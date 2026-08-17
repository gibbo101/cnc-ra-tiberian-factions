#!/usr/bin/env python3
"""The TS war factory exit loop: Aseprite marker -> engine track + preview GIF.

Reads the spawn seat from the SPAWN layer of the Aseprite sheet (drag the
magenta crosshair, save, re-run this) and produces BOTH sides of the loop:

  1. redalert/tsweap_exit_track.inc -- the generated Track19 waypoint table
     (offsets relative to the track destination, hull facing per waypoint).
     The engine plays this via Force_Track(OUT_OF_WEAPON_FACTORY_TS), so the
     vehicle glides out of the bay in one authored motion: no cell-recentre
     leg, no turn-in-place.
  2. ~/Desktop/wf-art/spawn-preview.gif -- the honest preview of that exact
     motion (door reveal, glide, door close), with the exit rails drawn as
     ground art. The same rails are stamped into the Aseprite sheet as a
     "RAILS -- GENERATED" layer so the line is visible next to the marker.

THE TRACK IS A STRAIGHT SHOT from the SPAWN marker to the centre of TILE 13
(Luke, 2026-08-18) -- the pad corner cell (3,2) in the sheet's numbered
grid, one SE diagonal from the door. The hull faces the line's direction
the whole way; with the seat on the 45-degree diagonal that is pure SE,
spawn facing to arrival. Tile 13 is the engine's reserved handover cell:
the unit arrives on its centre (only a cell centre hands over slide-free)
and vacates when the rally point or the next unit's doorway-scatter pushes
it on. An off-SE line is warned about loudly, never silently bent.

The script asserts bdata.cpp's ClassTsWeap exit point matches the marker and
building.cpp's pinned unload cell matches the computed destination -- seat,
destination and track MUST move together or the track start reads as a
teleport (the refinery-dock lesson). On mismatch it prints the exact value
to update and exits nonzero.

Usage: wf_spawn_preview.py [TSTITN|TSHARV]   (default TSTITN)
"""
import io, json, math, os, re, shutil, subprocess, sys, zipfile
from PIL import Image, ImageDraw

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RA = f"{REPO}/resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT"
SHEET = os.path.expanduser("~/Desktop/wf-art/wf-pad-edit.aseprite")
OUT = os.path.expanduser("~/Desktop/wf-art/spawn-preview.gif")
INC = f"{REPO}/redalert/tsweap_exit_track.inc"
BDATA = f"{REPO}/redalert/bdata.cpp"
BUILDING = f"{REPO}/redalert/building.cpp"
ASEPRITE = os.path.expanduser("~/.steam/steam/steamapps/common/Aseprite/aseprite")

CANVAS = (896, 672)
PLOT = (192, 144, 704, 528)          # 4x3 plot on the canvas
BASE_KEY = PLOT[1]                   # bay interior: plot north edge
OVER_KEY = 336 + 64                  # hangar south edge (Sort_Y + 128 leptons)
TITAN_H = 278                        # 52.2 classic px on this canvas
CV = 16 / 3                          # canvas px per classic px
DIR_SE = 96
# Blocked plot cells (col,row): the 3x2 hangar + the front-row cells under
# its drawn SW corner. Mirrors TsWeapList in bdata.cpp.
BLOCKED_CELLS = {(c, r) for r in range(2) for c in range(3)} | {(0, 2), (1, 2)}
PLOT_CELLS_W, PLOT_CELLS_H = 4, 3
# facing order in the packed art (preview_to_desktop SPECS): N NW W SW S SE E NE.
# DirType is clockwise from north, so facing index = (8 - dir/32) % 8.
UNITS = {"TSTITN": ("TSTITN.ZIP", "tstitn", 12, True, TITAN_H),
         "TSHARV": ("TSHARV.ZIP", "tsharv", 4, False, 170)}


def frame(zpath, pre, s):
    z = zipfile.ZipFile(zpath)
    meta = json.loads(z.read(f"{pre}-{s:04d}.meta"))
    tga = Image.open(io.BytesIO(z.read(f"{pre}-{s:04d}.tga"))).convert("RGBA")
    c = Image.new("RGBA", tuple(meta["size"]), (0, 0, 0, 0))
    c.paste(tga, (meta["crop"][0], meta["crop"][1]), tga)
    return c


def marker_from_sheet(layer, is_magenta):
    tmp = "/tmp/wf-marker.png"
    r = subprocess.run([ASEPRITE, "-b", SHEET, "--layer", layer,
                        "--save-as", tmp], capture_output=True)
    if r.returncode != 0:
        return None
    import numpy as np
    m = np.array(Image.open(tmp).convert("RGBA")).astype(int)
    if is_magenta:
        mask = (m[..., 3] > 128) & (m[..., 0] > 200) & (m[..., 2] > 200) & (m[..., 1] < 100)
    else:
        mask = (m[..., 3] > 128) & (m[..., 1] > 200) & (m[..., 2] > 200) & (m[..., 0] < 100)
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return int(round(xs.mean())), int(round(ys.mean()))


def dirtype(dx, dy):
    """DirType (0=N, 64=E, 128=S, clockwise) of a travel vector."""
    return int(round(math.atan2(dx, -dy) * 128 / math.pi)) % 256


def snap_to_centre(pt):
    """Nearest walkable plot-cell centre to a classic-px point."""
    cx = round((pt[0] - 12) / 24) * 24 + 12
    cy = round((pt[1] - 12) / 24) * 24 + 12
    cell = ((cx - 12) // 24, (cy - 12) // 24)
    if not (0 <= cell[0] < PLOT_CELLS_W and 0 <= cell[1] < PLOT_CELLS_H):
        sys.exit(f"EXIT marker {pt} snaps to cell {cell}, outside the 4x3 "
                 f"plot -- move it onto the plot's walkable concrete.")
    if cell in BLOCKED_CELLS:
        sys.exit(f"EXIT marker {pt} snaps to cell {cell}, a blocked hangar "
                 f"cell -- move it onto the walkable concrete (door corridor "
                 f"or pad column).")
    if (cx, cy) != pt:
        print(f"EXIT marker snapped to cell {cell} centre ({cx},{cy}) "
              f"(was {pt}) -- track ends must sit on a cell centre or the "
              f"engine's handover slides.")
    return (cx, cy), cell


def build_track(seat, dest):
    """Straight glide seat -> dest in ~1px steps, hull facing the line the
    whole way. Returns the track table."""
    sx, sy = seat
    dx, dy = dest
    if dx <= sx or dy <= sy:
        sys.exit(f"EXIT {dest} is not SE of the seat {seat} -- the bay door "
                 f"points SE; put the exit marker south-east of the spawn.")
    d = dirtype(dx - sx, dy - sy)
    if abs(d - DIR_SE) > 6:
        print(f"WARNING: line direction {d} deviates from pure SE ({DIR_SE}) "
              f"-- hull renders SE but motion is off-diagonal. Align the "
              f"markers on the 45-degree diagonal for a pure SE shot.")
    n = max(1, round(math.hypot(dx - sx, dy - sy)))
    track, seen = [], None
    for i in range(n):
        off = (round(sx + (dx - sx) * i / n) - dx,
               round(sy + (dy - sy) * i / n) - dy)
        if off == (0, 0) or off == seen:   # (0,0) is the engine's terminator
            continue
        seen = off
        track.append((off, d))
    track.append(((0, 0), d))              # arrive on the centre, same facing
    return track


def emit_inc(seat, dest, track):
    dcell = ((dest[0] - 12) // 24, (dest[1] - 12) // 24)
    end_dir = track[-1][1]
    rows = "".join(f"    {{XYP_COORD({ox}, {oy}), (DirType){d}}},\n"
                   for (ox, oy), d in track[:-1])
    with open(INC, "w") as f:
        f.write(
            "// GENERATED by scripts/wf_spawn_preview.py from the Aseprite SPAWN\n"
            "// and EXIT markers -- do not hand-edit; move a marker and re-run.\n"
            f"// Straight glide: seat XYP({seat[0]}, {seat[1]}) -> cell "
            f"{dcell} centre XYP{dest}, dir {end_dir}, {len(track)} entries.\n"
            f"{rows}"
            f"    {{0x00000000L, (DirType){end_dir}}}\n")
    print(f"wrote {INC} ({len(track)} entries, dir {end_dir}, start offset "
          f"({track[0][0][0]},{track[0][0][1]}), dest cell {dcell})")
    return dcell


def check_bdata_seat(seat):
    src = open(BDATA).read()
    m = re.search(r"ClassTsWeap\(.*?XYP_COORD\(\s*(-?\d+),\s*(-?\d+)\s*\)",
                  src, re.S)
    if not m:
        sys.exit("could not find ClassTsWeap exit point in bdata.cpp")
    have = (int(m.group(1)), int(m.group(2)))
    if have != seat:
        sys.exit(f"SEAT MISMATCH: marker says XYP_COORD({seat[0]}, {seat[1]}) "
                 f"but bdata.cpp ClassTsWeap has XYP_COORD{have}. Update "
                 f"bdata.cpp to the marker value and rebuild -- track and "
                 f"seat must move together or the glide starts with a snap.")
    print(f"bdata.cpp seat matches marker: XYP_COORD({seat[0]}, {seat[1]})")


def check_building_dest(dcell):
    src = open(BUILDING).read()
    m = re.search(r"XYCELL\((\d+),\s*(\d+)\)[^\n]*TSWEAP exit-track destination",
                  src)
    if not m:
        sys.exit("could not find the TSWEAP exit-track destination pin in "
                 "building.cpp (marker comment 'TSWEAP exit-track destination')")
    have = (int(m.group(1)), int(m.group(2)))
    if have != dcell:
        sys.exit(f"DESTINATION MISMATCH: the SE ray lands on cell {dcell} but "
                 f"building.cpp pins XYCELL{have}. Update the pinned cell to "
                 f"XYCELL({dcell[0]}, {dcell[1]}) and rebuild -- track and "
                 f"destination must move together.")
    print(f"building.cpp pinned cell matches track dest: XYCELL{dcell}")


def stamp_rails_layer(pts):
    """Write the exit rails into the Aseprite sheet as a generated layer so
    the line is visible right next to the SPAWN marker while editing. The
    layer is deleted and re-stamped every run; a sheet backup is taken first."""
    shutil.copy2(SHEET, SHEET + ".bak")
    lua = "/tmp/wf-rails-stamp.lua"
    pt_rows = ",".join(f"{{{x},{y}}}" for x, y in pts)
    with open(lua, "w") as f:
        f.write(f"""
local spr = app.activeSprite
for _, l in ipairs(spr.layers) do
  if l.name == "RAILS -- GENERATED" then spr:deleteLayer(l) end
end
local layer = spr:newLayer()
layer.name = "RAILS -- GENERATED"
layer.opacity = 200
local img = Image(spr.spec)
local pts = {{{pt_rows}}}
local col = app.pixelColor.rgba(255, 220, 0, 255)
if spr.colorMode ~= ColorMode.RGB then col = 255 end
for _, p in ipairs(pts) do
  for dx = -1, 1 do
    for dy = -1, 1 do
      local X, Y = p[1] + dx, p[2] + dy
      if X >= 0 and Y >= 0 and X < spr.width and Y < spr.height then
        img:putPixel(X, Y, col)
      end
    end
  end
end
spr:newCel(layer, 1, img, Point(0, 0))
spr:saveAs(spr.filename)
""")
    r = subprocess.run([ASEPRITE, "-b", SHEET, "--script", lua],
                       capture_output=True, text=True)
    if r.returncode != 0:
        shutil.copy2(SHEET + ".bak", SHEET)
        print(f"RAILS layer stamp FAILED (sheet restored from backup): "
              f"{r.stderr.strip() or r.stdout.strip()}")
    else:
        print(f"stamped RAILS -- GENERATED layer into {SHEET} "
              f"(backup at {SHEET}.bak)")


# Tile 13 in the sheet's numbered grid = plot cell (3,2), the pad corner:
# the reserved handover cell the glide ends on.
DEST_CELL = (3, 2)
DEST = (DEST_CELL[0] * 24 + 12, DEST_CELL[1] * 24 + 12)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "TSTITN"
    uz, upre, stride, has_turret, target_h = UNITS[which]

    m = marker_from_sheet("SPAWN -- MOVE ME", is_magenta=True)
    if m is None:
        sys.exit("no SPAWN marker found on the sheet")
    mx, my = m
    seat = (round((mx - PLOT[0]) * 3 / 16), round((my - PLOT[1]) * 3 / 16))
    print(f"spawn marker: canvas ({mx},{my})  classic {seat}")
    print(f"rails: seat {seat} -> tile 13 (cell {DEST_CELL}) centre {DEST}")

    dest, dcell = DEST, DEST_CELL
    track = build_track(seat, dest)
    emit_inc(seat, dest, track)
    check_bdata_seat(seat)
    check_building_dest(dcell)

    pad = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    bbz = f"{RA}/TERRAIN/TEMPERATE/TSWEAPBB.ZIP"
    for r in range(3):
        for c in range(4):
            t = frame(bbz, "tsweapbb", r * 4 + c)
            pad.paste(t, (192 + c * 128, 144 + r * 128), t)
    base = frame(f"{RA}/STRUCTURES/TSWEAP.ZIP", "tsweap", 0)
    door = [frame(f"{RA}/STRUCTURES/TSWEAP2.ZIP", "tsweap2", s) for s in range(9)]

    ref = frame(f"{RA}/UNITS/{uz}", upre, 5 * stride)
    scale = target_h / ref.crop(ref.getbbox()).height
    sprites = {}

    def sprite(d):
        f_idx = (8 - round(d / 32)) % 8
        if f_idx not in sprites:
            u = frame(f"{RA}/UNITS/{uz}", upre, f_idx * stride)
            if has_turret:
                u.alpha_composite(frame(f"{RA}/UNITS/{uz}", upre, 96 + f_idx * 4))
            u = u.crop(u.getbbox())
            sprites[f_idx] = u.resize((max(1, round(u.width * scale)),
                                       max(1, round(u.height * scale))),
                                      Image.LANCZOS)
        return sprites[f_idx]

    def canvas_pt(cx, cy):
        return (round(PLOT[0] + cx * CV), round(PLOT[1] + cy * CV))

    # The rails: the authored track drawn as ground art -- seat through every
    # waypoint to the destination centre. Under the sprites in the GIF, and
    # stamped into the Aseprite sheet as its own generated layer.
    rail_pts = [canvas_pt(*seat)] + \
               [canvas_pt(dest[0] + ox, dest[1] + oy) for (ox, oy), _ in track]
    rails = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    dr = ImageDraw.Draw(rails)
    dr.line(rail_pts, fill=(255, 220, 0, 190), width=3)
    for p in rail_pts[::4]:
        dr.ellipse([p[0]-4, p[1]-4, p[0]+4, p[1]+4], fill=(255, 130, 0, 220))
    ex, ey = rail_pts[-1]
    dr.ellipse([ex-7, ey-7, ex+7, ey+7], outline=(255, 60, 60, 255), width=3)
    stamp_rails_layer(rail_pts)

    def compose(door_stage, upos, udir):
        bg = Image.new("RGBA", CANVAS, (225, 225, 232, 255))
        bg.alpha_composite(pad)
        bg.alpha_composite(rails)
        layers = [(BASE_KEY, base), (OVER_KEY, door[door_stage])]
        if upos is not None:
            ux, uy = upos
            u = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
            s = sprite(udir)
            u.paste(s, (ux - s.width // 2, uy - s.height // 2), s)
            layers.append((uy, u))
        for _, im in sorted(layers, key=lambda t: t[0]):
            bg.alpha_composite(im)
        return bg

    # Engine order (building.cpp STRUCT_TSWEAP): the vehicle is unlimbo'd
    # into the bay FIRST, tethered and stationary, then the shutter runs up
    # -- revealed as the door opens. Then Force_Track plays Track19: the
    # pure-SE glide. At track end the unit stands on the destination centre
    # still facing SE (rally point, if set, takes it from there); the
    # shutter closes over the empty bay.
    frames = []
    seat_cv = canvas_pt(*seat)
    for s in range(9):                       # door opens over the waiting unit
        frames.append(compose(s, seat_cv, DIR_SE))
    for (ox, oy), d in track[::2] + [track[-1]]:   # the authored glide
        frames.append(compose(8, canvas_pt(dest[0] + ox, dest[1] + oy), d))
    for _ in range(3):                       # free on the pad corner, SE
        frames.append(compose(8, canvas_pt(*dest), DIR_SE))
    for s in range(8, -1, -1):               # door closes
        frames.append(compose(s, canvas_pt(*dest), DIR_SE))

    crop = (100, 60, 896, 672)
    frames = [f.crop(crop).convert("P", palette=Image.ADAPTIVE) for f in frames]
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=90, loop=0)
    print(f"wrote {OUT}")


main()
