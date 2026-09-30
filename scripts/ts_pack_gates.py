#!/usr/bin/env python3
"""Pack the HD gates (resources/custom-art/cnc-gates-hd) into their tilesets.

Each gate ships as two building types, horizontal (3x1) and vertical (1x3). The source frames
are exactly the footprint (384x128 / 128x384) and ship on a canvas of that size, centred on the
plot like every building. Frame sets written per type (RA_STRUCTURES.XML patched):

  <INI>       2 x stages  the door from shut (0) to open (stages-1), then the same damaged;
                          a gate in IDLE follows them with its shut loop (healthy, then damaged)
  <INI>MAKE   stages      the door rising out of its slot: the healthy run backwards
  <INI>X      the wall end pieces the engine draws over the gate (BuildingClass::Draw_It), one per
              end cell a joining wall runs into; wall 0 = TS GDI (also used for a component
              tower), 1 = TS Nod, 2 = RA concrete
                horizontal  wall*4 + end*2 + damaged          end 0 = west, 1 = east
                vertical    wall*2 + damaged                  the south end
                            6 + wall*frames + gate frame      the north end: it lies on the gate's
                                                              pad but behind everything standing on
                                                              it, yet draws after the gate, so each
                                                              frame carries the end piece with that
                                                              gate frame's standing parts over it
                                                              (<prefix>-v-NN-above.png, made by the
                                                              art's src/above_pad.py), cut to the
                                                              end piece's own pixels

  <INI>L      a component tower's connector reaching into the gate's end cell, drawn by the gate
              because a gate drawn after the tower covers it (the tower draws the rest):
                horizontal  end*2 + tower damaged                  end 0 = west, 1 = east
                vertical    tower damaged*frames + gate frame      the north end, behind the gate's
                                                                   standing parts like a wall's
              (the towers' own pieces: resources/custom-art/ts-gdi-component-tower-hd/gatelinks)

House colour: the trim masks (white = house colour) repaint their pixels pure green following the
pixel's own luminance, normalised over the gate's trim, which is what the launcher's hue remap
turns into the player's colour (docs/cnc3-to-remastered-sprites.md, section 7).

The TS gate's door sounds (GATEDWN1 opening, GATEUP1 closing) are converted to Data/AUDIO when
TS_ART_DIR is set (its .raw holds the AUDs, extracted by scripts/ts_rebuild_art.sh), and the Tesla
gate's wind-down (TSLACHG2R.WAV, the Tesla Coil charge-up reversed) is made from the game's SFX3D.MEG.

Usage: ts_pack_gates.py [GATE ...]      (default: every gate in GATES)
License: GPL v3.
"""
import io, json, os, subprocess, sys, zipfile
import numpy as np
from PIL import Image

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import ts_pack_walls as W

ART = os.path.join(SCRIPTS, "..", "resources", "custom-art")
SRC = os.path.join(ART, "cnc-gates-hd")
CELL = 128

# gate: (source dir, frame prefix, door stages, horizontal INI, vertical INI); a gate listed in IDLE
# also ships its shut-gate loop after the door frames: IDLE frames healthy, then IDLE damaged
GATES = {
    "ts-gdi": ("ts-gdi", "gdi-gate", 10, "TSGATEH", "TSGATEV"),
    "ts-nod": ("ts-nod", "nod-gate", 7, "TSNGATEH", "TSNGATEV"),
    "ra-allies": ("ra-allies", "allies-gate", 10, "ALGATEH", "ALGATEV"),
    "ra-soviets": ("ra-soviets", "soviet-gate", 10, "SVGATEH", "SVGATEV"),
    "td-gdi": ("td-gdi", "tdgdi-gate", 10, "TDGGATEH", "TDGGATEV"),
    "td-nod": ("td-nod", "tdnod-gate", 10, "TDNGATEH", "TDNGATEV"),
}

IDLE = {"ra-soviets": 3}   # the Tesla gate's arcs re-rolled (idle-extra), looped while it is shut

WALL_ENDS = [  # wall index -> (directory, file prefix)
    (os.path.join(SRC, "end-pieces", "ts-gdi-wall"), "end-gdi"),
    (os.path.join(ART, "ts-nod-wall-hd", "end-pieces", "ts-nod-wall"), "end-nod"),
    (os.path.join(SRC, "end-pieces", "ra-concrete-wall"), "end-brik"),
]
STATE_NAMES = ("ok", "damaged")
TOWER_LINKS = os.path.join(ART, "ts-gdi-component-tower-hd", "gatelinks")
TOWER_CELL = (24, 96)  # the tower cell's top-left on the tower art's 176x320 canvas


def tower_link(side, state, size, cell):
    """A tower's gate connector (side = where the gate is) on the gate's canvas, the tower standing
    in the cell whose top-left is at cell on that canvas."""
    piece = Image.open(os.path.join(TOWER_LINKS, f"gatelink-{side}-{state:02d}.png")).convert("RGBA")
    cv = Image.new("RGBA", size, (0, 0, 0, 0))
    cv.paste(piece, (cell[0] - TOWER_CELL[0], cell[1] - TOWER_CELL[1]), piece)
    return cv


def to_green(img, mask, mean_lum):
    """House-colour pixels become pure green; the rest keep their colour. The mask is taken hard
    (at half): a pixel blended part-way to green is neither, and the launcher leaves it green."""
    a = np.array(img).astype(np.float32)
    m = (np.array(mask.convert("L")) >= 128).astype(np.float32)[:, :, None]
    lum = 0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2]
    green = np.zeros_like(a[:, :, :3])
    green[:, :, 1] = np.clip(128.0 * lum / mean_lum, 0, 255)
    a[:, :, :3] = a[:, :, :3] * (1 - m) + green * m
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def gate_frames(folder, prefix, orient, stages):
    frames, masks = [], []
    for i in range(2 * stages):
        frames.append(Image.open(os.path.join(SRC, folder, f"{prefix}-{orient}-{i:02d}.png")).convert("RGBA"))
        masks.append(Image.open(os.path.join(SRC, folder, f"{prefix}-{orient}-{i:02d}-trim.png")))
    for state, shut in (("ok", 0), ("damaged", stages)):
        for k in range(1, IDLE.get(folder, 0) + 1):
            frames.append(Image.open(os.path.join(SRC, folder, "idle-extra",
                                                  f"{prefix}-{orient}-idle-{state}-{k}.png")).convert("RGBA"))
            masks.append(masks[shut])
    a = np.array(frames[0]).astype(np.float32)
    m = np.array(masks[0].convert("L")) > 128
    mean_lum = float((0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2])[m].mean())
    return [to_green(f, k, mean_lum) for f, k in zip(frames, masks)]


# RA's concrete wall runs its north-south arm this far west of the cell centre. On a north-south
# gate its end pieces bend onto the gate's centre line inside the gate's end cell: straight on
# the wall's own line at the cell edge, on the gate's line where they meet the gate.
BRIK_WEST = 14.0
BRIK_BEND = {"N": (2, 28, 0.0, BRIK_WEST), "S": (100, 126, BRIK_WEST, 0.0)}  # rows, shift at first/last


def bend(piece, y0, y1, dx0, dx1):
    """Each row slid east by an amount running from dx0 (rows up to y0) to dx1 (rows from y1),
    sub-pixel, on premultiplied colour so the edges blend."""
    a = np.array(piece).astype(np.float32)
    a[:, :, :3] *= a[:, :, 3:4] / 255.0
    out = np.zeros_like(a)
    for y in range(a.shape[0]):
        t = min(1.0, max(0.0, (y - y0) / float(y1 - y0)))
        dx = dx0 + (dx1 - dx0) * t
        ix = int(np.floor(dx))
        fr = dx - ix
        for k, wgt in ((ix, 1.0 - fr), (ix + 1, fr)):
            if wgt <= 0:
                continue
            row = np.zeros_like(a[y])
            if k >= 0:
                row[k:] = a[y, :a.shape[1] - k]
            else:
                row[:k] = a[y, -k:]
            out[y] += wgt * row
    alpha = out[:, :, 3:4]
    out[:, :, :3] = np.where(alpha > 0, out[:, :, :3] * 255.0 / np.maximum(alpha, 1e-3), 0)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def end_piece(wall, side, state, size, at):
    d, pre = WALL_ENDS[wall]
    piece = Image.open(os.path.join(d, f"{pre}-{side}-{STATE_NAMES[state]}.png")).convert("RGBA")
    if wall == 2 and side in BRIK_BEND:
        piece = bend(piece, *BRIK_BEND[side])
    cv = Image.new("RGBA", size, (0, 0, 0, 0))
    cv.alpha_composite(piece, at)
    return cv


def behind(piece, gate, above):
    """The end piece with the gate's standing parts drawn over it, kept only where the piece
    itself has pixels: drawn after the gate, it covers the pad and nothing standing on it."""
    g = np.array(gate)
    g[:, :, 3] = (g[:, :, 3].astype(np.float32) * np.array(above.convert("L"), np.float32) / 255.0).astype(np.uint8)
    cv = piece.copy()
    cv.alpha_composite(Image.fromarray(g))
    a = np.array(cv)
    a[np.array(piece)[:, :, 3] == 0] = 0
    return Image.fromarray(a)


def symmetric_crop(bbox, w, h):
    """The content box grown to be centred on the canvas. An off-centre crop (an end piece at
    the far end of the gate) is placed a few pixels out by the launcher; a centred one lands
    exactly (docs/launcher-render-contracts.md, contract 1)."""
    x0, y0, x1, y1 = bbox
    mx, my = min(x0, w - x1), min(y0, h - y1)
    return (mx, my, w - mx, h - my)


def write_zip(ini, frames):
    low = ini.lower()
    w, h = frames[0].size
    out_zip = f"{W.STRUCT_DIR}/{ini}.ZIP"
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for i, cv in enumerate(frames):
            bbox = symmetric_crop(cv.getbbox() or (0, 0, w, h), w, h)
            buf = io.BytesIO(); cv.crop(bbox).save(buf, format="TGA")
            z.writestr(f"{low}-{i:04d}.tga", buf.getvalue())
            z.writestr(f"{low}-{i:04d}.meta", json.dumps({"size": [w, h], "crop": list(bbox)}))
    print(f"wrote {out_zip} ({len(frames)} frames)")
    W.patch_tileset(W.TILESET, ini, len(frames))


def pack(gate):
    folder, prefix, stages, ini_h, ini_v = GATES[gate]
    dims = json.load(open(W.STUB_MANIFEST))
    for orient, ini in (("h", ini_h), ("v", ini_v)):
        frames = gate_frames(folder, prefix, orient, stages)
        size = frames[0].size
        write_zip(ini, frames)
        write_zip(ini + "MAKE", frames[stages - 1::-1])
        layers = []
        if orient == "h":
            for wall in range(3):
                for end, (side, x) in enumerate((("W", 0), ("E", 2 * CELL))):
                    for s in range(2):
                        layers.append(end_piece(wall, side, s, size, (x, 0)))
            towers = [tower_link(side, s, size, cell) for side, cell in (("E", (-CELL, 0)), ("W", (3 * CELL, 0)))
                      for s in range(2)]
        else:
            for wall in range(3):
                for s in range(2):
                    layers.append(end_piece(wall, "S", s, size, (0, 2 * CELL)))
            above = [Image.open(os.path.join(SRC, folder, f"{prefix}-v-{k:02d}-above.png")) for k in range(2 * stages)]
            idle = IDLE.get(folder, 0)
            # the arcs are light, not geometry: an idle frame stands where its shut frame does
            above += [above[0]] * idle + [above[stages]] * idle
            damaged = [k // stages for k in range(2 * stages)] + [0] * idle + [1] * idle
            for wall in range(3):
                for k, f in enumerate(frames):
                    layers.append(behind(end_piece(wall, "N", damaged[k], size, (0, 0)), f, above[k]))
            towers = [behind(tower_link("S", s, size, (0, -CELL)), f, above[k])
                      for s in range(2) for k, f in enumerate(frames)]
        write_zip(ini + "X", layers)
        write_zip(ini + "L", towers)
        dims[ini] = [size[0] * 3 // 16, size[1] * 3 // 16]
    json.dump(dims, open(W.STUB_MANIFEST, "w"), indent=1)
    open(W.STUB_MANIFEST, "a").write("\n")


def sounds():
    audio = os.path.join(SCRIPTS, "..", "resources", "remaster_mods", "Vanilla_RA", "Data", "AUDIO")
    # The Tesla gate winding down: RA's Tesla Coil charge-up played backwards.
    sfx = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data/SFX3D.MEG")
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "tf_gate_sfx")
    subprocess.run([sys.executable, os.path.join(SCRIPTS, "meg_extract.py"), "extract", sfx,
                    "RAR_SFX_TSLACHG2.WAV", tmp], check=True, stdout=subprocess.DEVNULL)
    src = next(os.path.join(d, f) for d, _, fs in os.walk(tmp) for f in fs if f.upper() == "RAR_SFX_TSLACHG2.WAV")
    out_wav = os.path.join(audio, "TSLACHG2R.WAV")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", "areverse",
                    "-acodec", "adpcm_ms", out_wav], check=True)
    print(f"wrote {out_wav}")
    raw = os.path.join(os.environ.get("TS_ART_DIR", ""), ".raw")
    if not os.environ.get("TS_ART_DIR"):
        print("TS_ART_DIR not set: TS gate sounds not converted")
        return
    for name in ("GATEDWN1", "GATEUP1"):
        out_wav = os.path.join(audio, f"TS{name}.WAV")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(raw, f"{name}.AUD"),
                        "-acodec", "adpcm_ms", out_wav], check=True)
        print(f"wrote {out_wav}")


if __name__ == "__main__":
    for gate in (sys.argv[1:] or list(GATES)):
        pack(gate)
    sounds()
