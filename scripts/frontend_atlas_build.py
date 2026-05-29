import os, struct
from PIL import Image

W, H = 6871, 6716
HDR = 18
ROW = W * 4
mtd = open('/tmp/mt_commandbar_common.mtd', 'rb').read()

# Prefer atlas_v2 (already has the approved C&C radar crest) so we only add flags.
if os.path.exists('/tmp/atlas_v2.tga'):
    base, apply_crest = '/tmp/atlas_v2.tga', False
else:
    base, apply_crest = '/tmp/mt_commandbar_common.tga', True
print("base:", base, "| re-apply crest:", apply_crest)

atlas = bytearray(open(base, 'rb').read())
hdr = atlas[:HDR]
assert len(atlas) == HDR + H * W * 4, f"unexpected size {len(atlas)}"


def coords(name):
    nb = (name + '.TGA').encode()
    i = mtd.find(nb)
    o = i + len(nb)
    while mtd[o] == 0:
        o += 1
    return struct.unpack_from('<4i', mtd, o)


def fit(path, rw, rh):
    img = Image.open(path).convert('RGBA')
    canvas = Image.new('RGBA', (rw, rh), (0, 0, 0, 0))
    iw, ih = img.size
    s = min(rw / iw, rh / ih)
    nw, nh = max(1, int(iw * s)), max(1, int(ih * s))
    canvas.paste(img.resize((nw, nh), Image.LANCZOS), ((rw - nw) // 2, (rh - nh) // 2))
    return canvas


def place(region, canvas):
    rx, ry, rw, rh = region
    bgra = canvas.tobytes('raw', 'BGRA')          # top-down, rh*rw*4
    for iy in range(rh):
        fr = H - 1 - (ry + iy)                     # bottom-origin file row
        off = HDR + fr * ROW + rx * 4
        atlas[off:off + rw * 4] = bgra[iy * rw * 4:(iy + 1) * rw * 4]


def crop(region):
    rx, ry, rw, rh = region
    rows = []
    for iy in range(rh):
        fr = H - 1 - (ry + iy)
        off = HDR + fr * ROW + rx * 4
        rows.append(bytes(atlas[off:off + rw * 4]))
    return Image.frombytes('RGBA', (rw, rh), b''.join(rows), 'raw', 'BGRA').resize((rw * 3, rh * 3), Image.NEAREST)


D = '/home/gibbo101/Desktop'

if apply_crest:
    cc = f'{D}/cnc_menu_art/ui_candc_logo.png'
    for reg in ['UI_SIDEBAR_FACTIONLOGO_ALLIES', 'UI_SIDEBAR_FACTIONLOGO_SOVIET']:
        c = coords(reg)
        place(c, fit(cc, c[2], c[3]))
        print("crest:", reg, c)

flagmap = {
    'RA_UI_FLAG_ICON_GREECE': f'{D}/cnc_logos/RA_UI_MULTIPLAYER_ALLIED_LOGO_LARGE_NORMAL.png',
    'RA_UI_FLAG_ICON_SPAIN':  f'{D}/cnc_logos/logo_factions_gdi.png',
    'RA_UI_FLAG_ICON_TURKEY': f'{D}/cnc_logos/logo_factions_nod.png',
    'RA_UI_FLAG_ICON_RUSSIA': f'{D}/cnc_logos/RA_UI_MULTIPLAYER_SOVIET_LOGO_LARGE_NORMAL.png',
}
prev = []
for reg, logo in flagmap.items():
    c = coords(reg)
    place(c, fit(logo, c[2], c[3]))
    prev.append((reg, c))
    print("flag:", reg, c, "<-", os.path.basename(logo))

open('/tmp/atlas_v3.tga', 'wb').write(bytes(atlas))
print("atlas_v3 written:", len(atlas), "bytes")

imgs = [crop(c) for _, c in prev]
sheet = Image.new('RGBA', (sum(i.width for i in imgs) + 10 * (len(imgs) + 1),
                           max(i.height for i in imgs) + 20), (35, 35, 40, 255))
x = 10
for i in imgs:
    sheet.paste(i, (x, 10), i)
    x += i.width + 10
sheet.convert('RGB').save('/tmp/flag_preview.png')
print("preview written: /tmp/flag_preview.png")
