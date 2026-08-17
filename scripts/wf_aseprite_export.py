#!/usr/bin/env python3
"""Export the TS war factory's packed art as full-canvas-aligned layers into
~/Desktop/wf-art/ for Aseprite work (the docking-art pattern: every file
shares the 896x672 canvas, so layers stack pixel-perfect when dragged into
one document).

Layers exported: assembled TSWEAPBB pad (from the shipped terrain tiles,
re-seated on the canvas grid), sandwich base (bay interior), hangar overlay
at door-shut and door-open, buildup final frame, and a grid-reference layer
marking cells, plot and apron extents. Plus a labelled pad-tile contact
sheet (tile index = tx + ty*5, the ShapeIndex the DLL emits per cell).

Run after any ts_pack_tree.py run: wf_aseprite_export.py
"""
import io, json, os, zipfile
from PIL import Image, ImageDraw

MOD = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "resources", "remaster_mods", "Vanilla_RA")
RA = os.path.normpath(f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT")
OUT = os.path.expanduser("~/Desktop/wf-art")

CANVAS = (896, 672)
CELL = 128                      # 24 classic px * 16/3
PLOT_COLS, PLOT_ROWS = 4, 3     # BSIZE_43
GRID_COLS, GRID_ROWS = 4, 3     # TSWEAPBB smudge grid (hand-tucked pad, 2026-08-17 evening)
LEFT = (CANVAS[0] - PLOT_COLS * CELL) // 2   # 192 -- grid/plot origin x
TOP = (CANVAS[1] - PLOT_ROWS * CELL) // 2    # 144 -- grid/plot origin y


def frame(zip_path, prefix, s):
    z = zipfile.ZipFile(zip_path)
    meta = json.loads(z.read(f"{prefix}-{s:04d}.meta"))
    tga = Image.open(io.BytesIO(z.read(f"{prefix}-{s:04d}.tga"))).convert("RGBA")
    c = Image.new("RGBA", tuple(meta["size"]), (0, 0, 0, 0))
    c.paste(tga, (meta["crop"][0], meta["crop"][1]), tga)
    return c


def save(img, name):
    img.save(f"{OUT}/{name}")
    print(f"wrote {OUT}/{name}")


os.makedirs(OUT, exist_ok=True)

# -- assembled pad: the shipped terrain tiles re-seated on the canvas grid --
bb = f"{RA}/TERRAIN/TEMPERATE/TSWEAPBB.ZIP"
pad = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
tiles = []
for r in range(GRID_ROWS):
    for c in range(GRID_COLS):
        t = frame(bb, "tsweapbb", r * GRID_COLS + c)
        tiles.append(t)
        pad.paste(t, (LEFT + c * CELL, TOP + r * CELL), t)
save(pad, "10-pad-assembled.png")

# -- sandwich layers --
base = f"{RA}/STRUCTURES/TSWEAP.ZIP"
over = f"{RA}/STRUCTURES/TSWEAP2.ZIP"
mk = f"{RA}/STRUCTURES/TSWEAPMAKE.ZIP"
save(frame(base, "tsweap", 0), "20-base-interior-healthy.png")
save(frame(over, "tsweap2", 0), "30-hangar-door-shut.png")
save(frame(over, "tsweap2", 8), "31-hangar-door-open.png")
save(frame(mk, "tsweapmake", 18), "40-buildup-final.png")

# -- everything stacked, as the launcher composes the built state --
comp = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
for layer in (pad, frame(base, "tsweap", 0), frame(over, "tsweap2", 0)):
    comp = Image.alpha_composite(comp, layer)
save(comp, "50-composite-built-door-shut.png")

# -- grid reference: cells, plot extent, apron extent --
grid = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
d = ImageDraw.Draw(grid)
for r in range(GRID_ROWS + 1):
    d.line([(LEFT, TOP + r * CELL), (LEFT + GRID_COLS * CELL, TOP + r * CELL)],
           fill=(255, 255, 0, 180), width=1)
for c in range(GRID_COLS + 1):
    d.line([(LEFT + c * CELL, TOP), (LEFT + c * CELL, TOP + GRID_ROWS * CELL)],
           fill=(255, 255, 0, 180), width=1)
d.rectangle([LEFT, TOP, LEFT + PLOT_COLS * CELL, TOP + PLOT_ROWS * CELL],
            outline=(255, 64, 64, 255), width=3)
d.rectangle([LEFT, TOP, LEFT + GRID_COLS * CELL, TOP + GRID_ROWS * CELL],
            outline=(64, 160, 255, 255), width=2)
for r in range(GRID_ROWS):
    for c in range(GRID_COLS):
        d.text((LEFT + c * CELL + 4, TOP + r * CELL + 3),
               f"{r * GRID_COLS + c}", fill=(255, 255, 0, 220))
save(grid, "90-grid-reference.png")

# -- labelled pad-tile contact sheet --
padd = 8
sheet = Image.new("RGB", (GRID_COLS * (CELL + padd) + padd,
                          GRID_ROWS * (CELL + 24 + padd) + padd), (40, 40, 44))
ds = ImageDraw.Draw(sheet)
for r in range(GRID_ROWS):
    for c in range(GRID_COLS):
        x = padd + c * (CELL + padd)
        y = padd + r * (CELL + 24 + padd)
        ds.text((x, y + 4), f"tile {r * GRID_COLS + c}  (col {c}, row {r})",
                fill=(255, 255, 120))
        sheet.paste(tiles[r * GRID_COLS + c], (x, y + 20),
                    tiles[r * GRID_COLS + c])
save(sheet, "60-pad-tiles-contact-sheet.png")

with open(f"{OUT}/INDEX.txt", "w") as f:
    f.write(f"""wf-art -- TS war factory reference exports for the Aseprite session
All PNGs except the contact sheet share the packed art's 896x672 canvas and
stack pixel-perfect as Aseprite layers. Cell = 128px on this canvas
(24 classic px). Plot/grid origin = canvas ({LEFT},{TOP}).

10-pad-assembled.png        the 15 shipped TSWEAPBB terrain tiles re-seated
                            on the canvas grid (5 cols x 3 rows from origin;
                            this IS what the game draws per cell, index =
                            col + row*5). Edit here, then re-slice on the
                            same grid.
20-base-interior-healthy    sandwich BASE (bay interior), TSWEAP frame 0.
30-hangar-door-shut         sandwich OVERLAY (whole hangar), TSWEAP2 frame 0.
31-hangar-door-open         door stage 9 of 9, TSWEAP2 frame 8.
40-buildup-final            TSWEAPMAKE frame 18 (last buildup frame; the
                            handoff comparison for the built composite).
50-composite-built-door-shut  pad + base + hangar stacked as the launcher
                            composes the built state.
60-pad-tiles-contact-sheet  the 15 tiles individually, labelled with the
                            ShapeIndex the DLL emits (col + row*5).
90-grid-reference           overlay layer: yellow cell grid + tile indices,
                            RED = the 4x3 BSIZE plot, BLUE = the 5x3 apron
                            grid (taper column east of the plot).

Geometry (2026-08-17 respec, deployed): fit_w 460 hangar on the west 3
columns, ghost 5x3, spawn XYP(56,33), ensemble box 104x58.
Regenerate: scripts/wf_aseprite_export.py (after any ts_pack_tree.py run).
""")
print(f"wrote {OUT}/INDEX.txt")
