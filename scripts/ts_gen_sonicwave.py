#!/usr/bin/env python3
"""Generate the TS Disruptor sonic-wave anim art (TSSONICW.ZIP).

There is NO sonic-wave art in Tiberian Sun to port: TS generates the effect in
its own engine as a live screen distortion of whatever is behind the wave. We
cannot distort, so the wave is faked with translucent sprites.

WHAT THE REAL THING LOOKS LIKE (measured off TS footage, 2026-08-24)
-------------------------------------------------------------------
Not rings, and not a beam: a WIDE TRANSLUCENT BAND that sweeps out from the
tank along the firing line. Measured on a 834x465 capture:

  * band thickness ~39px against a 108px unit selection box -> the band is
    ~0.36 of the unit's own width. For our 56px ShapeSize Disruptor that is
    ~20 classic px, and at the 5.33 canvas-per-classic-px VFX ratio (RAILFX:
    128px canvas, 24 classic dim) that is ~107px inside a 128px canvas.
  * mean band colour (121,176,105) over (122,94,59) terrain. Solving the
    alpha composite gives roughly (130,235,140) at ~60% alpha.
  * the interior is mottled rather than flat -- it reads as rippling pressure.
  * the band EXTENDS outward from the muzzle, it does not appear all at once.

WHY DISCS AND NOT ONE BAND SPRITE
---------------------------------
A spawned AnimClass draws UNROTATED, so a band sprite would only line up at one
of the eight beam angles. A soft disc is rotationally symmetric; spawning a
dense overlapping chain of them along the line builds the band at ANY angle,
with the band's thickness coming from the disc diameter.

The outward sweep comes from each disc's stage offset, not from a spawn delay
(the AnimClass ctor's timedelay param is off-limits -- delayed anims export to
the launcher in a pre-start state). The first LEAD_STAGES stages are fully
transparent. The engine starts the muzzle disc at stage LEAD_STAGES and the far
disc at stage 0 (SONIC_SWEEP_STAGES in techno.cpp), so the band grows out of
the hull over the lead-in, every disc then holds for the same span, and the
band retracts from the muzzle end -- the grow / hold / retract envelope
measured off TS: ~0.7s out, ~2s held, ~0.7s retract, ~3.3s in all at 2 ticks
per stage.

TIMING (measured off the same TS footage, 6fps frames): the whole band lives
~20 frames = ~3.3s. 50 ticks (25 stages x 2) ran in 1.2s on Luke's game speed,
so the game runs ~40 ticks/s there and the stage delay is 5.

Tuning lives entirely in the constants below.

Usage:  ts_gen_sonicwave.py [OUTDIR]
"""
import io, json, math, os, re, sys, zipfile
from PIL import Image, ImageDraw, ImageFilter

CANVAS = 128          # 5.33 canvas px per classic px -> 24 classic dim, as RAILFX
FRAMES = 25           # anim stages at 5 ticks each (adata.cpp): ~3.2s at Luke's ~40 tick/s game speed, the TS band's life
LEAD_STAGES = 5       # fully transparent lead-in = the outward sweep (SONIC_SWEEP_STAGES)
DIAMETER = 80.0       # ~15 classic px: 25% under the TS polygon (+-100 leptons = 18.75 px) at Luke's call, 2026-08-27
COLOR = (105, 228, 200)   # teal: TS's solved green (130,235,140) pulled toward its cyan highlights; Luke twice: 'too green', 'definitely more blue'
A_PEAK = 46           # per DISC. Discs overlap ~5 deep at 32-lepton spacing with the 80px
                      # disc, and the band's ~60% measured alpha is the STACK:
                      # 1-(1-46/255)^5 = 0.63. 153 here (60% per disc) compounds to an opaque mud.
EDGE_SOFT = 5.0       # gaussian blur on the disc edge, in px
MOTTLE = 0.5          # 0 = flat fill, 1 = heavily rippled interior. The 6-7 deep disc
                      # stack is a blur along the line: per-disc texture cannot survive
                      # it (simulated 2026-08-24: every design measured flat), so this is
                      # only edge softening. Full strength halved the band's alpha.
MOTTLE_SCALE = 3.0    # blur radius of the noise clumps, px on the 128 canvas
MOTTLE_SEED = 20260824
PULSE_COLOR = (235, 255, 250)  # paler/whiter than the band: TS's ripple lifts the green/blue of what's underneath
PULSE_ALPHA = 35          # per disc at PEAK amplitude; the discs stack ~6-7 deep along the band
PULSE_FRAMES = 13         # amplitude ladder, frame = ripple level 0-12 (TS WaveClass); the DLL drives the stage per tick
RISE_STAGES = 1       # stages from dark to full once the lead-in ends
FALL_STAGES = 2       # stages from full to dark at the end


def lerp(a, b, t):
    return a + (b - a) * t


def _mottle(stage):
    """Noise field for one stage. A different field per stage makes the band's
    interior shimmer over time -- the nearest a sprite gets to TS's live
    distortion of the ground under the wave."""
    import random
    rnd = random.Random(MOTTLE_SEED + stage)
    n = Image.new('L', (CANVAS, CANVAS))
    n.putdata([rnd.randrange(256) for _ in range(CANVAS * CANVAS)])
    # Blur to clumps rather than per-pixel static, then normalise to 0..255.
    n = n.filter(ImageFilter.GaussianBlur(MOTTLE_SCALE))
    lo, hi = n.getextrema()
    span = max(1, hi - lo)
    return n.point(lambda v: (v - lo) * 255 // span)


def wave(i):
    """One stage: a soft mottled disc, fading in then out across the frames."""

    # Envelope: transparent lead-in, short rise, HOLD, short fall. The hold is
    # most of the life: a triangle spent most of its stages nearly invisible
    # and killed the far half of the band once the discs were staged along it.
    lit = i - LEAD_STAGES + 1          # 1 on the first lit stage
    lit_span = FRAMES - LEAD_STAGES
    if lit <= 0:
        env = 0.0
    elif lit <= RISE_STAGES:
        env = lit / (RISE_STAGES + 1)
    elif lit > lit_span - FALL_STAGES:
        env = (lit_span - lit + 1) / (FALL_STAGES + 1)
    else:
        env = 1.0
    alpha = int(round(A_PEAK * min(1.0, env)))
    if alpha <= 0:
        return Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))

    ss = 4
    big = Image.new('L', (CANVAS * ss, CANVAS * ss), 0)
    d = ImageDraw.Draw(big)
    c = CANVAS * ss / 2.0
    r = DIAMETER * ss / 2.0
    d.ellipse([c - r, c - r, c + r, c + r], fill=255)
    mask = big.resize((CANVAS, CANVAS), Image.LANCZOS).filter(ImageFilter.GaussianBlur(EDGE_SOFT))

    # Modulate the disc by the noise field so the interior ripples.
    if MOTTLE > 0:
        m = mask.load()
        nz = _mottle(i).load()
        for y in range(CANVAS):
            for x in range(CANVAS):
                if m[x, y]:
                    f = 1.0 - MOTTLE + MOTTLE * (nz[x, y] / 255.0)
                    m[x, y] = int(m[x, y] * f)

    # Straight alpha: full-strength COLOR in RGB, the disc in the alpha channel
    # only. Pasting through the mask onto a transparent canvas instead blends
    # the RGB toward black by the mask, which ships a near-black sprite that
    # renders as a grey ghost whatever the alpha.
    out = Image.new('RGBA', (CANVAS, CANVAS), COLOR + (0,))
    out.putalpha(mask.point(lambda v: v * alpha // 255))
    return out


def pulse(i):
    """Ripple level i of the amplitude ladder: the wave's disc shape in a pale
    tint, alpha proportional to i/12. The DLL sets each ripple disc's stage per
    tick from TS's |sin| formula, so the band brightens in travelling crests
    exactly as TS's screen-space ripple does."""
    alpha = PULSE_ALPHA * i // (PULSE_FRAMES - 1)
    if alpha <= 0:
        return Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    ss = 4
    big = Image.new('L', (CANVAS * ss, CANVAS * ss), 0)
    d = ImageDraw.Draw(big)
    c = CANVAS * ss / 2.0
    r = DIAMETER * ss / 2.0
    d.ellipse([c - r, c - r, c + r, c + r], fill=255)
    mask = big.resize((CANVAS, CANVAS), Image.LANCZOS).filter(ImageFilter.GaussianBlur(EDGE_SOFT))
    out = Image.new('RGBA', (CANVAS, CANVAS), PULSE_COLOR + (0,))
    out.putalpha(mask.point(lambda v: v * alpha // 255))
    return out


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format='TGA')
    return buf.getvalue()


def write_zip(path, name, frames, square=False):
    """Center-symmetric crop + meta -- identical contract to the other packers.
    square=True keeps the full square frame: a sprite exported with Rotation
    is clipped to the UNROTATED frame rectangle (contract 8), so rotated art
    must never be bbox-cropped."""
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f'{name}-{i:04d}'
            W, H = img.width, img.height
            if square:
                b = (0, 0, W, H)
            else:
                bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
                x0 = min(bb[0], W - bb[2])
                y0 = min(bb[1], H - bb[3])
                b = (x0, y0, W - x0, H - y0)
            z.writestr(base + '.tga', tga_bytes(img.crop(b)))
            z.writestr(base + '.meta', json.dumps(
                {'size': [W, H], 'crop': [b[0], b[1], b[2], b[3]]}))


def patch_tileset(xml_path, name, count):
    """Declare exactly `count` shapes for `name`: a stage with no tile draws as
    the launcher's white placeholder box, so the tileset must always match the
    frame count packed here."""
    sub = name.lower()
    xml = open(xml_path, encoding='utf-8').read()
    xml = re.sub(r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?",
                 '', xml, flags=re.S)
    block = ('\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n'
             '\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n')
    blocks = ''.join(block % (name, i, f'{sub}\\{sub}-{i:04d}.tga') for i in range(count))
    idx = xml.rindex('</Tiles>')
    open(xml_path, 'w', encoding='utf-8').write(xml[:idx] + blocks + xml[idx:])
    print(f'patched {os.path.basename(xml_path)}: {name} -> {count} tiles')


def main():
    mod = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                       'resources', 'remaster_mods', 'Vanilla_RA', 'Data')
    outdir = sys.argv[1] if len(sys.argv) > 1 else (
        os.path.join(mod, 'ART', 'TEXTURES', 'SRGB', 'RED_ALERT', 'VFX'))
    outdir = os.path.abspath(outdir)
    frames = [wave(i) for i in range(FRAMES)]
    path = os.path.join(outdir, 'TSSONICW.ZIP')
    write_zip(path, 'tssonicw', frames)
    print(f'wrote {path} ({len(frames)} frames, {CANVAS}px canvas)')
    pframes = [pulse(i) for i in range(PULSE_FRAMES)]
    ppath = os.path.join(outdir, 'TSSONICP.ZIP')
    write_zip(ppath, 'tssonicp', pframes)
    print(f'wrote {ppath} ({len(pframes)} frames)')
    if len(sys.argv) <= 1:
        patch_tileset(os.path.join(mod, 'XML', 'TILESETS', 'RA_VFX.XML'), 'TSSONICW', FRAMES)
        patch_tileset(os.path.join(mod, 'XML', 'TILESETS', 'RA_VFX.XML'), 'TSSONICP', PULSE_FRAMES)


if __name__ == '__main__':
    main()
