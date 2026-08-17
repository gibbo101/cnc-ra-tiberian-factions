#!/usr/bin/env python3
"""The TS war factory exit loop: Aseprite markers -> engine tracks + preview GIF.

Two spawn markers on the sheet drive everything:

  SPAWN -- MOVE ME   (magenta)  the DEFAULT seat, every unit except the Titan
  SPAWN TSTITN       (orange)   the Titan's own seat

Each seat gets its own straight exit rail to the centre of TILE 13 (Luke,
2026-08-18) -- the pad corner cell (3,2) in the sheet's numbered grid, the
engine's reserved handover cell. The hull faces its line's direction the
whole way; both rails sit within a few DirType units of pure SE, so both
hulls render SE for the entire glide. Only a cell centre hands over to
normal driving slide-free, which is why the destination is fixed to the
tile centre. Units vacate tile 13 via the rally point or the next unit's
doorway scatter.

One run produces:
  1. redalert/tsweap_exit_track.inc        -- Track19, the default rail
  2. redalert/tsweap_exit_track_titan.inc  -- Track20, the Titan rail
  3. redalert/tsweap_exit_seats.inc        -- TSWEAP_SEAT_DEFAULT / _TSTITN
     macros, consumed by BOTH bdata.cpp (class exit point) and building.cpp
     (spawn seat pick), so seat and track can never drift apart.
  4. ~/Desktop/wf-art/spawn-preview.gif    -- the honest preview: door
     reveal, glide along the rail with per-facing sprites, door close.
     Both rails are drawn as ground art (yellow = default, orange = Titan)
     and stamped into the sheet as a RAILS -- GENERATED layer.

Drag a marker, save, re-run, rebuild -- that is the whole loop.

Usage: wf_spawn_preview.py [TSTITN|TSHARV]   (default TSTITN)
"""
import io, json, math, os, re, shutil, subprocess, sys, zipfile
from PIL import Image, ImageDraw

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RA = f"{REPO}/resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT"
SHEET = os.path.expanduser("~/Desktop/wf-art/wf-pad-edit.aseprite")
OUT = os.path.expanduser("~/Desktop/wf-art/spawn-preview.gif")
INC = f"{REPO}/redalert/tsweap_exit_track.inc"
INC_TITAN = f"{REPO}/redalert/tsweap_exit_track_titan.inc"
INC_SEATS = f"{REPO}/redalert/tsweap_exit_seats.inc"
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
# Tile 13 in the sheet's numbered grid = plot cell (3,2), the pad corner:
# the reserved handover cell every rail ends on.
DEST_CELL = (3, 2)
DEST = (DEST_CELL[0] * 24 + 12, DEST_CELL[1] * 24 + 12)
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


def marker_from_sheet(layer, magenta_only=False):
    tmp = "/tmp/wf-marker.png"
    r = subprocess.run([ASEPRITE, "-b", SHEET, "--layer", layer,
                        "--save-as", tmp], capture_output=True)
    if r.returncode != 0:
        return None
    import numpy as np
    m = np.array(Image.open(tmp).convert("RGBA")).astype(int)
    mask = m[..., 3] > 128
    if magenta_only:
        mask &= (m[..., 0] > 200) & (m[..., 2] > 200) & (m[..., 1] < 100)
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return int(round(xs.mean())), int(round(ys.mean()))


def to_classic(canvas_xy):
    return (round((canvas_xy[0] - PLOT[0]) * 3 / 16),
            round((canvas_xy[1] - PLOT[1]) * 3 / 16))


def dirtype(dx, dy):
    """DirType (0=N, 64=E, 128=S, clockwise) of a travel vector."""
    return int(round(math.atan2(dx, -dy) * 128 / math.pi)) % 256


def build_track(seat, label):
    """Straight glide seat -> tile 13 centre in ~1px steps, hull facing the
    line the whole way. Returns the track table."""
    sx, sy = seat
    dx, dy = DEST
    if dx <= sx or dy <= sy:
        sys.exit(f"{label} seat {seat} is not NW of tile 13 centre {DEST} -- "
                 f"the bay door points SE; move the marker back inside the bay.")
    d = dirtype(dx - sx, dy - sy)
    note = "" if abs(d - DIR_SE) <= 6 else "  (WARNING: visibly off the SE diagonal)"
    print(f"{label} rail: seat {seat} -> {DEST}, dir {d}{note}")
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


def emit_track(path, label, seat, track):
    rows = "".join(f"    {{XYP_COORD({ox}, {oy}), (DirType){d}}},\n"
                   for (ox, oy), d in track[:-1])
    with open(path, "w") as f:
        f.write(
            "// GENERATED by scripts/wf_spawn_preview.py from the Aseprite\n"
            "// spawn markers -- do not hand-edit; move a marker and re-run.\n"
            f"// {label}: seat XYP({seat[0]}, {seat[1]}) -> cell {DEST_CELL} "
            f"centre XYP{DEST}, dir {track[-1][1]}, {len(track)} entries.\n"
            f"{rows}"
            f"    {{0x00000000L, (DirType){track[-1][1]}}}\n")
    print(f"wrote {os.path.basename(path)} ({len(track)} entries)")


def emit_seats(seat_def, seat_titan):
    with open(INC_SEATS, "w") as f:
        f.write(
            "// GENERATED by scripts/wf_spawn_preview.py from the Aseprite\n"
            "// spawn markers -- do not hand-edit; move a marker and re-run.\n"
            "// Offsets from the building origin (plot NW corner), classic px.\n"
            f"#define TSWEAP_SEAT_DEFAULT XYP_COORD({seat_def[0]}, {seat_def[1]})\n"
            f"#define TSWEAP_SEAT_TSTITN  XYP_COORD({seat_titan[0]}, {seat_titan[1]})\n")
    print(f"wrote {os.path.basename(INC_SEATS)}: default {seat_def}, "
          f"titan {seat_titan}")


def check_sources():
    """The generated macros must actually be consumed -- a hand-typed seat
    or destination in the C sources is drift waiting to happen."""
    bsrc = open(BDATA).read()
    m = re.search(r"ClassTsWeap\(.*?(TSWEAP_SEAT_DEFAULT|XYP_COORD\([^)]*\))",
                  bsrc, re.S)
    if not m or m.group(1) != "TSWEAP_SEAT_DEFAULT":
        sys.exit("bdata.cpp ClassTsWeap must pass TSWEAP_SEAT_DEFAULT (from "
                 "tsweap_exit_seats.inc) as its exit point, not a literal.")
    gsrc = open(BUILDING).read()
    m = re.search(r"XYCELL\((\d+),\s*(\d+)\)[^\n]*TSWEAP exit-track destination",
                  gsrc)
    if not m:
        sys.exit("could not find the TSWEAP exit-track destination pin in "
                 "building.cpp (marker comment 'TSWEAP exit-track destination')")
    have = (int(m.group(1)), int(m.group(2)))
    if have != DEST_CELL:
        sys.exit(f"DESTINATION MISMATCH: rails end on cell {DEST_CELL} but "
                 f"building.cpp pins XYCELL{have}.")
    print("bdata.cpp consumes TSWEAP_SEAT_DEFAULT; building.cpp pin matches "
          f"XYCELL{DEST_CELL}")


def stamp_rails_layer(rail_sets):
    """Write the exit rails into the Aseprite sheet as a generated layer so
    the lines are visible next to the markers while editing. The layer is
    deleted and re-stamped every run; a sheet backup is taken first."""
    shutil.copy2(SHEET, SHEET + ".bak")
    lua = "/tmp/wf-rails-stamp.lua"
    sets = []
    for pts, rgb in rail_sets:
        pt_rows = ",".join(f"{{{x},{y}}}" for x, y in pts)
        sets.append(f"{{pts={{{pt_rows}}}, r={rgb[0]}, g={rgb[1]}, b={rgb[2]}}}")
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
local sets = {{{",".join(sets)}}}
for _, s in ipairs(sets) do
  local col = app.pixelColor.rgba(s.r, s.g, s.b, 255)
  if spr.colorMode ~= ColorMode.RGB then col = 255 end
  for _, p in ipairs(s.pts) do
    for dx = -1, 1 do
      for dy = -1, 1 do
        local X, Y = p[1] + dx, p[2] + dy
        if X >= 0 and Y >= 0 and X < spr.width and Y < spr.height then
          img:putPixel(X, Y, col)
        end
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


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "TSTITN"
    uz, upre, stride, has_turret, target_h = UNITS[which]

    m = marker_from_sheet("SPAWN -- MOVE ME", magenta_only=True)
    if m is None:
        sys.exit("no SPAWN -- MOVE ME marker found on the sheet")
    seat_def = to_classic(m)
    print(f"default marker: canvas {m}  classic {seat_def}")
    t = marker_from_sheet("SPAWN TSTITN")
    if t is None:
        seat_titan = seat_def
        print("no SPAWN TSTITN marker -- titan uses the default seat")
    else:
        seat_titan = to_classic(t)
        print(f"titan marker:   canvas {t}  classic {seat_titan}")

    track_def = build_track(seat_def, "default")
    track_titan = build_track(seat_titan, "titan")
    emit_track(INC, "default rail (Track19)", seat_def, track_def)
    emit_track(INC_TITAN, "titan rail (Track20)", seat_titan, track_titan)
    emit_seats(seat_def, seat_titan)
    check_sources()

    pad = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    bbz = f"{RA}/TERRAIN/TEMPERATE/TSWEAPBB.ZIP"
    for r in range(3):
        for c in range(4):
            tt = frame(bbz, "tsweapbb", r * 4 + c)
            pad.paste(tt, (192 + c * 128, 144 + r * 128), tt)
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

    def rail_pts(seat, track):
        return [canvas_pt(*seat)] + \
               [canvas_pt(DEST[0] + ox, DEST[1] + oy) for (ox, oy), _ in track]

    pts_def = rail_pts(seat_def, track_def)
    pts_titan = rail_pts(seat_titan, track_titan)
    rails = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    dr = ImageDraw.Draw(rails)
    for pts, col in ((pts_def, (255, 220, 0, 190)), (pts_titan, (255, 130, 0, 190))):
        dr.line(pts, fill=col, width=3)
    ex, ey = pts_def[-1]
    dr.ellipse([ex-7, ey-7, ex+7, ey+7], outline=(255, 60, 60, 255), width=3)
    stamp_rails_layer([(pts_def, (255, 220, 0)), (pts_titan, (255, 130, 0))])

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
    # into the bay FIRST at its type's seat, tethered and stationary, then
    # the shutter runs up -- revealed as the door opens. Then Force_Track
    # plays the type's rail. At track end the unit stands on tile 13's
    # centre (rally point, if set, takes it from there); the shutter closes.
    seat, track = (seat_titan, track_titan) if which == "TSTITN" else (seat_def, track_def)
    end_dir = track[-1][1]
    frames = []
    for s in range(9):                       # door opens over the waiting unit
        frames.append(compose(s, canvas_pt(*seat), end_dir))
    for (ox, oy), d in track[::2] + [track[-1]]:   # the authored glide
        frames.append(compose(8, canvas_pt(DEST[0] + ox, DEST[1] + oy), d))
    for _ in range(3):                       # free on tile 13
        frames.append(compose(8, canvas_pt(*DEST), end_dir))
    for s in range(8, -1, -1):               # door closes
        frames.append(compose(s, canvas_pt(*DEST), end_dir))

    crop = (100, 60, 896, 672)
    frames = [f.crop(crop).convert("P", palette=Image.ADAPTIVE) for f in frames]
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=90, loop=0)
    print(f"wrote {OUT}")


main()
