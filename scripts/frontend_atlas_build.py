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

# --- Map-select start-position markers (2026-06-07) -------------------------
# The skirmish lobby pins a faction marker to each chosen start position on the
# map preview, drawn from the UI_MAPSELECT_FACTION_NN region set (separate from
# the RA_UI_FLAG_ICON_<country> regions above). The launcher indexes that marker
# by the player's ActLike COUNTRY, not the picker faction -- our GDI plays as
# Spain (_03) and Nod as Turkey (_10), which hold country flags, so the markers
# showed Spain/Turkey flags instead of the GDI/Nod emblems. The GDI/Nod marker
# art already lives in the atlas at _01/_02; copy it into the country slots our
# factions actually use. (No new art; same loose atlas.)
def crop_clean(region):
    rx, ry, rw, rh = region
    rows = []
    for iy in range(rh):
        fr = H - 1 - (ry + iy)
        off = HDR + fr * ROW + rx * 4
        rows.append(bytes(atlas[off:off + rw * 4]))
    return Image.frombytes('RGBA', (rw, rh), b''.join(rows), 'raw', 'BGRA')


mapselect_copy = [
    ('UI_MAPSELECT_FACTION_01', 'UI_MAPSELECT_FACTION_03'),  # GDI eagle -> Spain slot
    ('UI_MAPSELECT_FACTION_02', 'UI_MAPSELECT_FACTION_10'),  # Nod cobra -> Turkey slot
]
for src, dst in mapselect_copy:
    sc, dc = coords(src), coords(dst)
    img = crop_clean(sc)
    if (sc[2], sc[3]) != (dc[2], dc[3]):
        img = img.resize((dc[2], dc[3]), Image.LANCZOS)
    place(dc, img)
    print("mapselect:", src, "->", dst, dc)

# --- Mission-select campaign tabs (2026-06-07) ------------------------------
# RA mission-select has 6 tabs: Allied, Soviet, Counterstrike(CS), Aftermath,
# Ant, Custom. Repurpose the unused-by-this-mod CS (tab 3) and Aftermath (tab 4)
# as GDI and Nod -> the row reads Allies / Soviets / GDI / Nod. Keep the native
# RA silver tab frame and composite our GDI/Nod emblem onto it (rather than
# pasting TD's whole green tab), so the tabs match the Allied/Soviet look.
# All four campaign tabs get matching faction emblems sliced+keyed from
# factions_4logo.png (scripts/tab_emblems/). On-screen tab order is Allied,
# Soviet, AFTERMATH(tab3), CS(tab4) -> GDI on AFTERMATH, Nod on CS, so the row
# reads Allies / Soviets / GDI / Nod. Composited over the native RA silver
# frame; the emblems are larger than the old symbols so they fully cover them.
# PARKED 2026-06-07: the Mission Select page is restored to stock until the
# campaign-roster work can be tested properly on the Steam Deck (the roster edits
# crash the desktop launcher -- see memory project-missionselect-roster-poc).
# Flip this to True to re-apply the GDI/Nod campaign-tab emblems. The art + logic
# below are preserved intact so it's a one-line re-enable.
ENABLE_MISSIONSELECT_TABS = False

TABDIR = 'scripts/tab_emblems'
tab_emblem = {
    'ALLIED':    f'{TABDIR}/allied.png',
    'SOVIET':    f'{TABDIR}/soviet.png',
    'AFTERMATH': f'{TABDIR}/gdi.png',   # tab 3 -> GDI
    'CS':        f'{TABDIR}/nod.png',   # tab 4 -> Nod
}
def erase_symbol(frame, rw, rh):
    """Wipe the native tab symbol off the silver inset so a smaller emblem can't
    reveal it (e.g. CS's gold key peeking beside the Nod hex). The inset has
    horizontal scanlines, so take a symbol-free vertical column at the inset's
    left edge and stretch it horizontally across the inset -- this preserves the
    scanline texture exactly (each row keeps its value) with no banding."""
    bx, by = 11, 10                  # frame-border thickness (px)
    col = frame.crop((bx, by, bx + 1, rh - by))            # 1px column, full inset height
    fill = col.resize((rw - 2 * bx, rh - 2 * by), Image.NEAREST)
    frame.paste(fill, (bx, by))
    return frame

if ENABLE_MISSIONSELECT_TABS:
    for ra_tab, logo in tab_emblem.items():
        for state in ('OFF', 'ON', 'HOVER', 'PRESSED', 'DISABLED'):
            dc = coords(f'RA_UI_MISSIONSELECT_TABICON_{ra_tab}_{state}')
            rw, rh = dc[2], dc[3]
            frame = erase_symbol(crop_clean(dc), rw, rh)   # native RA silver tab, symbol wiped
            em = fit(logo, int(rh * 0.72), int(rh * 0.72))
            if state == 'DISABLED':
                em.putalpha(em.getchannel('A').point(lambda v: int(v * 0.45)))
            frame.alpha_composite(em, ((rw - em.width) // 2, (rh - em.height) // 2))
            place(dc, frame)
        print("tab:", ra_tab, "<- emblem", os.path.basename(logo))
else:
    print("mission-select tabs: PARKED (stock) -- set ENABLE_MISSIONSELECT_TABS=True to re-apply")

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
