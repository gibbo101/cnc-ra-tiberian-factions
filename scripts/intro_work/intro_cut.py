#!/usr/bin/env python3
"""Build the Tiberian Factions intro montage from a shot list, cut to the Remastered Hell March.

It opens in place of Red Alert's logo animation, with Hell March from its first note: the fire
Tiberian Factions title slams in on the opening hit and the six faction emblems pop in one per
beat. Two bars in, on the first big accent, a flash cuts to the montage. Each shot fills a
steel-bezelled window over
the menu's smoke backdrop (the low-res FMV stays sharp at window size, as Retaliation's framed
inset did) and lasts a whole number of beats (120 BPM: one beat is 15 frames at 30 fps), so
cuts land on the beat. The band's entry gets a flash on the cut it falls on. The last shot, the
finale, comes in with a flash on the phrase two bars after the quick cuts begin: Nod's flame
tanks, whose flames engulf the street on the next bar, where Hell March starts to fade. Over its
last beat the shot dissolves into the title and emblems, which hold and then fade out into the
menu's own background (ending 'menu': the launcher's menu then appears over the same picture) or
to black (ending 'black').
The launcher fits the movie inside the screen and, about 10 s in, reveals the menu wherever the
movie doesn't cover it. The movie is 16:9, so it fills 16:9 screens; elsewhere the menu
background's margins show beside it (16:10, the Steam Deck: above and below; wider screens:
either side). The backdrop is that background's own smoke at the same scale, brightened so that
once the launcher has drawn it, darker than a texture, it shows at the menu's shade and the
margins carry straight on from it.

The FMV library (decoded movies, frame cache, the Hell March WAV) lives outside the repo, at
$TF_FMV_LIB or ~/Desktop/Tiberian Factions/tf-intro-lib; see README.md beside this script.

usage: intro_cut.py <shots.tsv> preview <out.mp4> [menu|black]   720p H.264 + AAC for review
       intro_cut.py <shots.tsv> frames <out dir> [menu|black]   1920x1080 JPEGs (q95) + music WAV for the Bink encode
menu|black picks how the title fades out (see closing()); menu is the default.
"""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

LIB = Path(os.environ.get('TF_FMV_LIB', Path.home() / 'Desktop/Tiberian Factions/tf-intro-lib'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import logo_art  # noqa: E402
import menu_art  # noqa: E402
import title_art  # noqa: E402
import title_logo_build  # noqa: E402

FPS, W, H = 30, 1920, 1080
BEAT = 15                                  # frames per beat at 120 BPM
WINDOW = (240, 135, 1440, 810)             # x, y, w, h of the video window
# The launcher draws the (Bink 1) movie darker in the shadows than a texture of the same value: a
# dark tone v shows as about 1.08 v - 9, and from 112 up a tone shows as itself (measured on the
# desktop framebuffer and from a 32:9 screen recording against the movie file).
VIDEO_LEVELS = (1.08, -9.0)
HELL_MARCH_HIT = 0.279                     # the opening hit, which the title slams in on (s)
OPENING_FRAMES = 128                       # two bars later, the first big accent: the montage (4.267 s)
BAND_ENTRY = 32.276                        # the band comes in (s); a cut falls on it
FINALE = 40.281                            # the phrase the finale, the last shot, comes in on (s)
FADE_START = FINALE + 2.0                  # the next bar, where the finale's flames hit: Hell March fades
TITLE_HOLD = 75                            # the title and emblems hold after the finale, to the next bar
FADE_OUT = 30                              # then fade out
REST = 15                                  # and what they fade to holds until the launcher's menu
MUSIC = LIB / 'audio/RAR_MUS_HELL_MARCH_pcm16.wav'
CACHE = LIB / 'edit/cache'
EMBLEMS = ('allied.png', 'soviet.png', 'gdi.png', 'nod.png', 'tsgdi.png', 'tsnod.png')


def read_shots(path):
    shots = []
    for line in open(path):
        if line.strip() and not line.startswith('#'):
            movie, first, beats = line.split('\t')[:3]
            shots.append((movie, int(first), int(beats)))
    return shots


def movie_fps(movie):
    import json
    game, name = movie.split('/')
    return json.load(open(LIB / f'meta/{game}/{name}.json'))['fps']


def picture_box(files):
    """The area of a shot that holds picture: rows and columns that are ever brighter than
    black bars across a sample of its frames (many CGI movies are letterboxed in their frame)."""
    sample = [np.asarray(Image.open(f).convert('L')).astype(int) for f in files[::max(1, len(files) // 6)]]
    peak = np.max(sample, axis=0)
    rows = np.nonzero((peak > 24).mean(1) > 0.05)[0]
    cols = np.nonzero((peak > 24).mean(0) > 0.05)[0]
    return cols[0], rows[0], cols[-1] + 1, rows[-1] + 1


def shot_frames(movie, first, beats):
    """The source pictures for one shot, one per output frame (15 fps sources repeat), with the
    shot's picture area."""
    fps = movie_fps(movie)
    count = beats * BEAT
    need = int(np.ceil(count * fps / FPS))
    out = CACHE / f"{movie.replace('/', '_')}_{first}_{need}"
    if not out.exists() or len(list(out.iterdir())) < need:
        subprocess.run(['python3', str(LIB / 'tools/fmvlib.py'), 'fullres', movie, str(first),
                        str(first + need - 1), str(out), '--jpg'], check=True, capture_output=True)
    files = sorted(out.iterdir())
    return [files[min(len(files) - 1, int(i * fps / FPS))] for i in range(count)], picture_box(files)


def backdrop():
    hero = Image.open(menu_art.KEY_ART / 'remastered-library_hero_2x.jpg').convert('RGB')
    smoke = menu_art.smoke(hero).convert('RGB')
    return as_texture(core_of(smoke))


def core_of(menu_size_image):
    x, y = menu_art.CORE
    return menu_size_image.convert('RGB').crop((x, y, x + W, y + H))


def as_texture(picture):
    """The picture to put in the movie for it to show as the same picture in a texture would."""
    gain, offset = VIDEO_LEVELS
    return Image.eval(picture, lambda v: max(v, round((v - offset) / gain)))


def menu_picture():
    """The main menu's background where the movie covers it, as the launcher shows it next."""
    return as_texture(core_of(menu_art.background(menu_art.stock_bytes(title_logo_build.ATLAS))))


def framed(bg):
    """The backdrop with a steel bezel and drop shadow round the video window."""
    x, y, w, h = WINDOW
    canvas = bg.convert('RGBA')
    shadow = Image.new('L', (W, H), 0)
    shadow.paste(200, (x - 10, y - 4, x + w + 10, y + h + 20))
    shade = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shade.putalpha(shadow.filter(ImageFilter.GaussianBlur(18)))
    canvas.alpha_composite(shade)
    band = 14
    bezel = np.zeros((h + 2 * band, w + 2 * band, 4), dtype=float)
    ramp = np.linspace(165, 85, bezel.shape[0])[:, None]
    bezel[..., 0], bezel[..., 1], bezel[..., 2] = ramp * 0.95, ramp * 0.98, ramp * 1.04
    bezel[..., 3] = 255
    bezel[:3, :, :3] = 28
    bezel[-3:, :, :3] = 18
    bezel[:, :3, :3] = 28
    bezel[:, -3:, :3] = 18
    bezel[3:5, 3:-3, :3] = 205                          # top-edge highlight
    bezel[band - 3:band + h + 3, band - 3:band + w + 3, :3] = 10   # inner dark lip
    canvas.alpha_composite(Image.fromarray(np.clip(bezel, 0, 255).astype('uint8')), (x - band, y - band))
    return canvas.convert('RGB')


def in_window(base, picture):
    x, y, w, h = WINDOW
    frame = base.copy()
    s = max(w / picture.width, h / picture.height)
    fitted = picture.convert('RGB').resize((round(picture.width * s), round(picture.height * s)), Image.LANCZOS)
    left, top = (fitted.width - w) // 2, (fitted.height - h) // 2
    frame.paste(fitted.crop((left, top, left + w, top + h)), (x, y))
    return frame


def flash(frame, strength):
    return Image.blend(frame, Image.new('RGB', frame.size, (255, 255, 255)), strength) if strength > 0 else frame


def emblem(name, h):
    e = logo_art.load(name, h)
    if name == 'tsgdi.png':
        e = logo_art.tame(e, 0.80, 0.90)
    if name == 'tsnod.png':
        e = logo_art.blackout(e)
    return e


def title_parts():
    title = title_art.render()
    title = title.resize((1300, round(title.height * 1300 / title.width)), Image.LANCZOS)
    return title, [emblem(n, 170) for n in EMBLEMS]


def title_card(bg, title, marks, s=1.0, ks=None):
    """The title over the backdrop with the emblems in a row below it: the title at scale s, and
    emblem i at scale ks[i] (None: not shown yet)."""
    ks = [1.0] * len(marks) if ks is None else ks
    xs = [960 + (i - 2.5) * 230 for i in range(len(marks))]
    canvas = bg.convert('RGBA')
    t = title.resize((round(title.width * s), round(title.height * s)), Image.LANCZOS)
    canvas.alpha_composite(t, (960 - t.width // 2, 300 - t.height // 2))
    for x, mark, k in zip(xs, marks, ks):
        if k is None:
            continue
        m = mark.resize((round(mark.width * k), round(mark.height * k)), Image.LANCZOS)
        canvas.alpha_composite(m, (round(x - m.width / 2), round(760 - m.height / 2)))
    return canvas.convert('RGB')


def opening(bg, title, marks):
    """Black until the title slams in on Hell March's opening hit, then one emblem pops in per beat."""
    title_frame = round(HELL_MARCH_HIT * FPS)
    emblem_frames = [title_frame + BEAT * (i + 1) for i in range(len(EMBLEMS))]
    frames = []
    for f in range(OPENING_FRAMES):
        if f < title_frame:
            frames.append(Image.new('RGB', (W, H)))
            continue
        s = 1.0 + 0.12 * max(0.0, 1 - (f - title_frame) / 8)
        ks = [None if f < at else 1.0 + 0.3 * max(0.0, 1 - (f - at) / 5) for at in emblem_frames]
        frames.append(flash(title_card(bg, title, marks, s, ks), max(0.0, 1 - (f - title_frame) / 12)))
    return frames


def eased(f, frames):
    t = (f + 1) / frames
    return t * t * (3 - 2 * t)


def closing(card, ending):
    """The title and emblems hold, then fade out: into the main menu's background, so the menu the
    launcher shows next appears over the same picture ('menu'), or to black ('black')."""
    target = menu_picture() if ending == 'menu' else Image.new('RGB', (W, H))
    for _ in range(TITLE_HOLD):
        yield card
    for f in range(FADE_OUT):
        yield Image.blend(card, target, eased(f, FADE_OUT))
    for _ in range(REST):
        yield target


def render(shots, ending):
    bg = backdrop()
    base = framed(bg)
    title, marks = title_parts()
    card = title_card(bg, title, marks)
    yield from opening(bg, title, marks)
    start = OPENING_FRAMES
    finale = start + sum(beats for _, _, beats in shots[:-1]) * BEAT
    end = finale + shots[-1][2] * BEAT
    flashes = ((start, (0.6, 0.25)), (round(BAND_ENTRY * FPS), (0.7, 0.4, 0.15)), (finale, (0.6, 0.25)))
    n = start
    for movie, first, beats in shots:
        pictures, box = shot_frames(movie, first, beats)
        for picture in pictures:
            frame = in_window(base, Image.open(picture).crop(box))
            for cut, strengths in flashes:
                if 0 <= n - cut < len(strengths):
                    frame = flash(frame, strengths[n - cut])
            if end - n <= BEAT:
                frame = Image.blend(frame, card, eased(BEAT - (end - n), BEAT))
            yield frame
            n += 1
    yield from closing(card, ending)


def load_wav(path):
    """Any audio file as 44.1 kHz stereo float samples (the game's WAVs are MS-ADPCM)."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 's16le', '-ac', '2', '-ar', '44100', '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(float)


def music(seconds):
    """Hell March from its first note, fading out from the bar where the finale's flames hit (the
    menu's own music, the Retaliation remix, fades in after it)."""
    rate = 44100
    total = int(seconds * rate)
    tune = load_wav(MUSIC)[:total].copy()
    at = int(FADE_START * rate)
    tune[at:] *= (np.cos(np.linspace(0, np.pi / 2, total - at)) ** 2)[:, None]
    return np.clip(tune, -32768, 32767).astype(np.int16)


def write_wav(path, samples):
    import wave
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(samples.tobytes())


def main(shot_path, mode, out, ending='menu'):
    shots = read_shots(shot_path)
    total = OPENING_FRAMES + sum(b for _, _, b in shots) * BEAT + TITLE_HOLD + FADE_OUT + REST
    seconds = total / FPS
    if mode == 'preview':
        wav = Path(out).with_suffix('.wav')
        write_wav(wav, music(seconds))
        ff = subprocess.Popen(
            ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
             '-i', '-', '-i', str(wav), '-t', f'{seconds:.3f}', '-vf', 'scale=1280:720',
             '-c:v', 'libx264', '-crf', '22', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', out],
            stdin=subprocess.PIPE)
        for frame in render(shots, ending):
            ff.stdin.write(frame.tobytes())
        ff.stdin.close()
        ff.wait()
    else:
        Path(out).mkdir(parents=True, exist_ok=True)
        for i, frame in enumerate(render(shots, ending)):
            frame.save(Path(out) / f'frame_{i:05d}.jpg', quality=95)
        write_wav(Path(out) / 'music.wav', music(seconds))
    print(f'{mode}: {total} frames, {seconds:.2f} s -> {out}')


if __name__ == '__main__':
    if len(sys.argv) not in (4, 5) or sys.argv[2] not in ('preview', 'frames') or sys.argv[4:] not in ([], ['menu'], ['black']):
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
