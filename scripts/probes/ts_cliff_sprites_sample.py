#!/usr/bin/env python3
"""TS's own cliff art on RA's grid (docs/ts-theatres.md): the square autotile ground with every TS cliff
piece drawn over it as an object, the plateau top on its own cells and the face hanging south.

Usage: ts_cliff_sprites_sample.py [--map NAME] [--out DIR]
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ts_map  # noqa: E402
import ts_map_to_ra as conv  # noqa: E402
import ts_autotile_sample as auto  # noqa: E402
import ts_ground_sample  # noqa: E402

HD = auto.HD
TS_PX = HD / 48  # HD pixels per TS screen pixel across
LEVEL_PX = 15  # TS screen pixels per height level


def is_cliff(tileset, tile, rec):
    """Whether a TS cell is part of a cliff piece, drawn as an object rather than ground."""
    name = tileset.tiles[tileset.fixup(tile)][0].lower()
    return "cliff" in name or (rec["land"] == "rock" and rec["extra"] is not None)


def piece_top(tileset, tile, sub, level):
    """The plateau level a cliff cell's piece rises to: the piece's base plus its tallest sub-tile."""
    rec = tileset.record(tile, sub)
    tallest = max(r["height"] for r in tileset.records(tile) if r)
    return level - rec["height"] + tallest


def extra_image(tileset, rec, light):
    """A sub-tile's face image, lit."""
    ex, ey, ew, eh, data = rec["extra"]
    img = Image.new("RGBA", (ew, eh), (0, 0, 0, 0))
    put = img.load()
    for i, p in enumerate(data):
        if p:
            r, g, b = tileset.palette[p]
            put[i % ew, i // ew] = (min(255, int(r * light[0])), min(255, int(g * light[1])),
                                    min(255, int(b * light[2])), 255)
    return img


def cliff_layer(tsmap, tileset, layout, face_scale):
    """Every cliff cell's diamond and face, at HD over the whole converted map; faces at
    `face_scale` of TS's own height."""
    layer = Image.new("RGBA", (layout.width * HD, layout.height * HD), (0, 0, 0, 0))
    v_scale = TS_PX * face_scale
    cells = []
    for (x, y), (tile, sub, level) in tsmap.cells.items():
        rec = tileset.record(tile, sub)
        if is_cliff(tileset, tile, rec):
            cells.append((x + y, level, x, y, tile, sub, rec))
    for _dy, level, x, y, tile, sub, rec in sorted(cells):
        cx = (x - y - layout.x0) * HD / 2
        cy = (x + y - layout.y0) * HD / 2
        drop = (piece_top(tileset, tile, sub, level) - level) * LEVEL_PX * v_scale
        light = tsmap.light(level)
        diamond = tileset.diamond(rec, light).resize((HD, HD), Image.LANCZOS)
        layer.paste(diamond, (int(cx - HD / 2), int(cy - HD / 2 + drop)), diamond)
        if rec["extra"]:
            ex, ey, ew, eh, _data = rec["extra"]
            face = extra_image(tileset, rec, light).resize((max(1, int(ew * TS_PX)), max(1, int(eh * v_scale))),
                                                           Image.LANCZOS)
            left = cx - HD / 2 + (ex - rec["x"]) * TS_PX
            top = cy + drop + (ey - rec["y"] - 12) * v_scale
            layer.paste(face, (int(left), int(top)), face)
    return layer


def flat_ground(tsmap, tileset, layout, textures, rocks):
    """The converted map's square ground at HD with no cliffs drawn, lit by height as TS lights it."""
    ground = Image.new("RGB", (layout.width * HD, layout.height * HD))
    cache = {}
    for v in range(layout.height):
        for u in range(layout.width):
            corners = auto.region_corners(tsmap, tileset, layout, u, v)
            variant = (u * 7 + v * 13 + (u * v) % 3) % 4
            key = (tuple(c[:2] for c in corners), variant)
            if key not in cache:
                cache[key] = auto.to_image(auto.piece([c[0] for c in corners], [c[1] for c in corners], [0] * 4,
                                                      textures, rocks, variant, cliffs=False))
            ground.paste(cache[key], (u * HD, v * HD))
    return ground


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--map", default="Tiers of Sorrow")
    parser.add_argument("--zoom", default="4,20,14,11", help="u,v,w,h of the close-up, in RA cells")
    parser.add_argument("--out", default=os.path.expanduser("~/Desktop/Tiberian Factions/ts-theatres/cliff-sprites"))
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)
    install = ts_map.TsInstall()
    tsmap = ts_map.TsMap(install.maps()[args.map])
    tileset = ts_map.Tileset(install, tsmap.theatre)
    layout = conv.Layout(tsmap)
    light = tsmap.light(2)
    textures = {k: auto.seamless_texture(tileset, auto.tile_index(tileset, s, n), light) for k, s, n in auto.GROUND}
    clear = auto.tile_index(tileset, "Clear", 0)
    textures["."] = [auto.seamless_texture(tileset, clear, light, i) for i in range(4)]
    rock = auto.rock_texture(tileset)
    rocks = [rock] * 4
    ground = flat_ground(tsmap, tileset, layout, textures, rocks)
    slug = conv.slug(args.map)
    zu, zv, zw, zh = (int(v) for v in args.zoom.split(","))
    box = (zu * HD, zv * HD, (zu + zw) * HD, (zv + zh) * HD)
    zooms = []
    for face_scale, tag in ((1.0, "ts_height"), (0.5, "half_height")):
        img = ground.convert("RGBA")
        img.alpha_composite(cliff_layer(tsmap, tileset, layout, face_scale))
        img = img.convert("RGB")
        img.resize((layout.width * 32, layout.height * 32), Image.LANCZOS).save(
            os.path.join(args.out, f"{slug}_whole_{tag}.png"))
        zoom = img.crop(box)
        zoom.save(os.path.join(args.out, f"{slug}_zoom_{tag}.png"))
        zooms.append((f"TS cliff art, faces at {'TS height' if face_scale == 1 else 'half TS height'}", zoom))
    exact = ts_ground_sample.flat_hd(tsmap, tileset, layout, 0, 0, layout.width, layout.height)
    exact.alpha_composite(cliff_layer(tsmap, tileset, layout, 1.0))
    exact = exact.convert("RGB")
    exact.resize((layout.width * 32, layout.height * 32), Image.LANCZOS).save(
        os.path.join(args.out, f"{slug}_whole_ts_exact.png"))
    exact_zoom = exact.crop(box)
    exact_zoom.save(os.path.join(args.out, f"{slug}_zoom_ts_exact.png"))
    zooms.append(("TS's own ground tiles + TS cliffs (exact)", exact_zoom))
    procedural = os.path.join(os.path.dirname(args.out), "autotile-sample", f"{slug}_cliff_zoom_ra.png")
    if os.path.exists(procedural):
        zooms.insert(0, ("procedural cliffs (previous sample)", Image.open(procedural).convert("RGB")))
    width = zooms[0][1].width // 2
    sheet = Image.new("RGB", (len(zooms) * (width + 20), zooms[0][1].height // 2 + 30), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    for i, (title, img) in enumerate(zooms):
        sheet.paste(img.resize((width, img.height // 2), Image.LANCZOS), (i * (width + 20), 26))
        d.text((i * (width + 20), 6), title, fill=(255, 255, 255))
    sheet.save(os.path.join(args.out, f"{slug}_cliffs_compare.png"))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
