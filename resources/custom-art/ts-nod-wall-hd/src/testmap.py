"""Test map using every connection frame, plus contact sheets."""
from PIL import Image, ImageDraw
import sys

BG = (90, 100, 80, 255)
GRID = (82, 92, 72, 255)

# 9x5 cells: a window (all corners, T's and the cross), a vertical run with ends,
# a horizontal run with ends and a lone post.
LAYOUT = [
    "WWWWW.W..",
    "W.W.W.W.W",
    "WWWWW.W..",
    "W.W.W....",
    "WWWWW.WWW",
]


def masks(layout=LAYOUT):
    h, w = len(layout), len(layout[0])
    wall = lambda x, y: 0 <= x < w and 0 <= y < h and layout[y][x] == 'W'
    out = {}
    for y in range(h):
        for x in range(w):
            if wall(x, y):
                out[(x, y)] = (wall(x, y - 1) * 1 + wall(x + 1, y) * 2 +
                               wall(x, y + 1) * 4 + wall(x - 1, y) * 8)
    return out


def test_map(frame_path, title, layout=LAYOUT, stage=None):
    """frame_path(mask, (x, y)) -> path; stage lets each cell pick a damage row."""
    h, w = len(layout), len(layout[0])
    canvas = Image.new('RGBA', (w * 128, h * 128), BG)
    d = ImageDraw.Draw(canvas)
    for i in range(w + 1):
        d.line([(i * 128, 0), (i * 128, h * 128)], fill=GRID)
    for j in range(h + 1):
        d.line([(0, j * 128), (w * 128, j * 128)], fill=GRID)
    for (x, y), m in sorted(masks(layout).items(), key=lambda kv: (kv[0][1], kv[0][0])):
        path = frame_path(m, (x, y))
        if path:
            canvas.alpha_composite(Image.open(path).convert('RGBA'), (x * 128, y * 128))
    ImageDraw.Draw(canvas).text((6, 4), title, fill=(255, 255, 0, 255))
    return canvas


def contact(paths, labels, cols=8, scale=1.5):
    s = int(128 * scale)
    sheet = Image.new('RGBA', (cols * (s + 4), ((len(paths) + cols - 1) // cols) * (s + 4)), (40, 40, 40, 255))
    for i, (p, lab) in enumerate(zip(paths, labels)):
        t = Image.new('RGBA', (s, s), BG)
        if p:
            t.alpha_composite(Image.open(p).convert('RGBA').resize((s, s), Image.LANCZOS))
        ImageDraw.Draw(t).text((4, 2), lab, fill=(255, 255, 0, 255))
        sheet.paste(t, ((i % cols) * (s + 4), (i // cols) * (s + 4)))
    return sheet


def stack(images, gap=16):
    W = max(i.width for i in images)
    out = Image.new('RGBA', (W, sum(i.height for i in images) + gap * (len(images) - 1)), (40, 40, 40, 255))
    y = 0
    for i in images:
        out.paste(i, (0, y)); y += i.height + gap
    return out


if __name__ == '__main__':
    print(sorted(set(masks().values())))
