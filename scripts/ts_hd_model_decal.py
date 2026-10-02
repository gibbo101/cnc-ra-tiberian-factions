#!/usr/bin/env python3
"""Paint a building's deck decal (ts_pack_hd_buildings.py's decal=) into its 3D model in the TS-HD pack's 3d/,
so the model carries what the game draws.

The decal goes into the deck's own vertex colours (COLOR_0, the materials' unlit colours), at the place the
building's frames show it: each vertex of the deck is placed through the model's camera-ra-grid, which frames
the frames' source canvas exactly, and takes the decal's colour there. The deck's vertices lie 1 px apart on
that grid, the frames' own resolution. On the paint go the deck's own colour variation and its lamps, as in the
frames. On a damaged mesh the paint keeps only to deck still in its healthy place and colour: it is gone where
the deck is broken, sunk, burnt black or under rubble, and darkens with the scorch around that. The house-colour
mask (COLOR_1) is left as it is; the decal must not reach it.

A model takes its decal once: the scene's extras record it, and a model that has one is refused.

Usage: ts_hd_model_decal.py [INI ...]   (none = every model listed)
License: GPL v3.
"""
import json, math, os, struct, sys
import numpy as np

import ts_pack_hd_buildings as hd

MODELS_DIR = os.path.join(hd.SCRIPTS, "..", "asset-packs", "TS-HD-Graphics-Pack", "3d")
CANVAS = (768, 512)

# ini: the model, and each mesh painted with the healthy mesh it is compared against (None for a healthy one)
MODELS = {
    "TSDROP": ("dropship-bay.glb", {"pad": None, "pad-damaged": "pad"}),
}

COMPONENTS = {5126: np.float32, 5121: np.uint8, 5123: np.uint16, 5125: np.uint32}
WIDTHS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    json_len = struct.unpack("<I", data[12:16])[0]
    doc = json.loads(data[20:20 + json_len])
    at = 20 + json_len
    bin_len = struct.unpack("<I", data[at:at + 4])[0]
    return doc, bytearray(data[at + 8:at + 8 + bin_len])


def write_glb(path, doc, blob):
    text = json.dumps(doc, separators=(",", ":")).encode()
    text += b" " * (-len(text) % 4)
    blob = bytes(blob) + b"\0" * (-len(blob) % 4)
    total = 12 + 8 + len(text) + 8 + len(blob)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(text), 0x4E4F534A) + text)
        f.write(struct.pack("<II", len(blob), 0x004E4942) + blob)


def accessor(doc, blob, index):
    """The accessor's values as an array, and the byte offset they start at in the buffer."""
    a = doc["accessors"][index]
    view = doc["bufferViews"][a["bufferView"]]
    if view.get("byteStride"):
        raise SystemExit("interleaved buffer views are not handled")
    at = view.get("byteOffset", 0) + a.get("byteOffset", 0)
    n = WIDTHS[a["type"]]
    values = np.frombuffer(blob, COMPONENTS[a["componentType"]], a["count"] * n, at).reshape(a["count"], n)
    return values, at


def mesh(doc, blob, name):
    node = next(n for n in doc["nodes"] if n["name"] == name)
    attrs = doc["meshes"][node["mesh"]]["primitives"][0]["attributes"]
    if any(node.get(k) for k in ("rotation", "scale")) or any(node.get("translation", [0, 0, 0])):
        raise SystemExit(f"{name}: a mesh node off the origin is not handled")
    return {k: accessor(doc, blob, attrs[k]) for k in ("POSITION", "NORMAL", "COLOR_0", "COLOR_1")}


def quat_matrix(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def to_canvas(doc, points):
    """Points in the model as px on camera-ra-grid's canvas, the frames' source canvas."""
    node = next(n for n in doc["nodes"] if n["name"] == "camera-ra-grid")
    view = doc["cameras"][node["camera"]]["orthographic"]
    local = (points - np.array(node["translation"])) @ quat_matrix(node["rotation"])
    return ((local[:, 0] / view["xmag"] + 1) / 2 * CANVAS[0],
            (1 - local[:, 1] / view["ymag"]) / 2 * CANVAS[1])


def sample(img, x, y):
    """img (h x w x 4, alpha premultiplied) at fractional px, bilinear, clear outside it."""
    h, w = img.shape[:2]
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = (x - x0)[:, None], (y - y0)[:, None]
    out = np.zeros((len(x), 4), np.float32)
    for dx, dy, wt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xi, yi = x0 + dx, y0 + dy
        ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
        out[ok] += img[yi[ok], xi[ok]] * wt[ok]
    return out


def deck_key(points):
    return [tuple(k) for k in np.round(points[:, [0, 2]] * 512).astype(int)]


def paint(doc, blob, original, decal, name, healthy_name):
    """Paint the decal into mesh name's colours in blob; original is the buffer before any mesh was painted,
    which the healthy mesh is read from."""
    m = mesh(doc, blob, name)
    pos = m["POSITION"][0].astype(np.float64)
    normal, (colour, colour_at), house = m["NORMAL"][0], m["COLOR_0"], m["COLOR_1"][0]
    x, y = to_canvas(doc, pos)

    # the decal seen from straight above, 1 px per px of the canvas's width (and of the deck's depth)
    width = decal["width"]
    art = np.asarray(hd.decal_art(decal["art"], width, 1.0)).astype(np.float32)
    art[..., :3] *= art[..., 3:] / 255
    depth = width * hd.GROUND_SQUASH
    u = (x - decal["centre"][0]) / width * art.shape[1] + art.shape[1] / 2 - 0.5
    v = (y - decal["centre"][1]) / depth * art.shape[0] + art.shape[0] / 2 - 0.5
    s = sample(art, u, v)
    a = s[:, 3] / 255
    paint_rgb = s[:, :3] / np.maximum(s[:, 3:], 1e-3) * 255

    up = normal[:, 1] > 0.95
    a[~up] = 0
    if (a[house[:, 0] > 0] > 0.01).any():
        raise SystemExit(f"{name}: the decal at {decal['centre']} reaches the house-colour mask")
    hit = a > 0
    lum = colour[:, :3].astype(np.float32) @ hd.LUMA
    if healthy_name:
        h = mesh(doc, original, healthy_name)
        h_pos, h_up = h["POSITION"][0].astype(np.float64), h["NORMAL"][0][:, 1] > 0.95
        h_lum = h["COLOR_0"][0][:, :3].astype(np.float32) @ hd.LUMA
        index = {k: i for i, k in enumerate(deck_key(h_pos)) if h_up[i]}
        twin = np.array([index.get(k, -1) if hit[i] else -1 for i, k in enumerate(deck_key(pos))])
        found = twin >= 0
        in_place = np.zeros(len(pos), bool)
        in_place[found] = np.abs(pos[found, 1] - h_pos[twin[found], 1]) < 0.002
        a[~in_place] = 0
        ref_lum = np.where(in_place, h_lum[np.maximum(twin, 0)], lum)
        tint = np.abs(colour[:, :3] / np.maximum(lum, 1)[:, None]
                      - np.where(in_place[:, None], h["COLOR_0"][0][np.maximum(twin, 0), :3], colour[:, :3])
                      / np.maximum(ref_lum, 1)[:, None]).sum(1)
        a *= ((1 - np.clip((tint - 0.15) / 0.15, 0, 1))
              * np.clip((lum / np.maximum(ref_lum, 1) - 0.45) / 0.35, 0, 1))
    else:
        ref_lum = lum

    # The deck's colour where the decal lies, and how much brighter it renders than it is coloured, from the
    # frames: the paint's colour is the decal's on screen, before that light.
    flat = np.median(ref_lum[(a > 0) & up])
    shown = shown_flat(decal)
    a *= hd.PAINT_COVER
    base = colour[:, :3].astype(np.float32)
    coat = paint_rgb * (flat / shown) * (lum / flat)[:, None]
    rgb = base * (1 - a[:, None]) + coat * a[:, None]
    lamp = np.clip((ref_lum - flat - 12 * flat / shown) / (20 * flat / shown), 0, 1)[:, None]
    rgb = rgb + lamp * (np.maximum(rgb, base) - rgb)
    painted = colour.copy()
    painted[:, :3] = np.clip(np.round(rgb), 0, 255).astype(np.uint8)
    blob[colour_at:colour_at + painted.nbytes] = painted.tobytes()
    print(f"{name}: {int((a > 0).sum())} vertices painted")


def shown_flat(decal):
    """The deck's luminance on screen where the decal lies, from the healthy frame."""
    from PIL import Image
    spec = next(s for s in hd.BUILDINGS.values() if s.get("decal") is decal)
    path, _ = spec["frames"]
    frame = np.asarray(Image.open(os.path.join(hd.SRC, spec["src"], f"{path}-00.png")).convert("RGBA"))
    art = np.asarray(hd.decal_art(decal["art"], decal["width"]))
    h, w = art.shape[:2]
    x0 = round(decal["centre"][0] - w / 2)
    y0 = round(decal["centre"][1] - h / 2)
    under = frame[y0:y0 + h, x0:x0 + w]
    return float(np.median(under[art[..., 3] > 0][:, :3].astype(np.float32) @ hd.LUMA))


def main(argv):
    for ini in [a for a in argv if a in MODELS] or list(MODELS):
        model, meshes = MODELS[ini]
        decal = hd.BUILDINGS[ini]["decal"]
        path = os.path.join(MODELS_DIR, model)
        doc, blob = read_glb(path)
        extras = doc["scenes"][doc.get("scene", 0)].setdefault("extras", {})
        if "decal" in extras:
            raise SystemExit(f"{model} already carries its decal: {extras['decal']}")
        original = bytes(blob)
        for name, healthy in meshes.items():
            paint(doc, blob, original, decal, name, healthy)
        extras["decal"] = (f"{os.path.basename(decal['art'])} painted on the deck in COLOR_0, "
                           f"{decal['width']} px across at {list(decal['centre'])} on camera-ra-grid's canvas")
        write_glb(path, doc, blob)
        print(f"wrote {os.path.relpath(path)}")


if __name__ == "__main__":
    main(sys.argv[1:])
