#!/usr/bin/env python3
"""Build the Tiberian Factions intro montage from a shot list, cut to the Remastered Hell March.

It opens in place of Red Alert's logo animation, to that animation's own logo tune (the stock
REDINTRO's audio): the fire Tiberian Factions title slams in where the C&C logo did, and the six
faction emblems pop in on the metal hits that land the RED ALERT letters. Where the stock intro
moves on to its targeting scope, a flash cuts to the montage on Hell March's opening hit. Each
shot fills a steel-bezelled window over
the menu's smoke backdrop (the low-res FMV stays sharp at window size, as Retaliation's framed
inset did) and lasts a whole number of beats (120 BPM: one beat is 15 frames at 30 fps), so
cuts land on the beat. The band's entry gets a flash; the last shot ends on a bar downbeat where
Hell March fades out under a white flash to the menu.
The launcher fits the movie inside the screen and, about 10 s in, reveals the menu wherever the
movie doesn't cover it. The movie is 16:9, so it fills 16:9 screens; on 16:10 (the Steam Deck)
the bands above and below show the menu background's margins, which menu_art.py makes the same
smoke at the same shade as this backdrop, the same texture at the same scale.

The FMV library (decoded movies, frame cache, the Hell March WAV) lives outside the repo, at
$TF_FMV_LIB or ~/Desktop/Tiberian Factions/tf-intro-lib; see README.md beside this script.

usage: intro_cut.py <shots.tsv> preview <out.mp4> [A|B|C]   720p H.264 + AAC for review
       intro_cut.py <shots.tsv> frames <out dir> [A|B|C]   1920x1080 JPEGs (q95) + music WAV for the Bink encode
A|B|C picks the music ending (see music()); C, the fade, is the default.
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

FPS, W, H = 30, 1920, 1080
BEAT = 15                                  # frames per beat at 120 BPM
WINDOW = (240, 135, 1440, 810)             # x, y, w, h of the video window
LOGO_TUNE = LIB / 'audio/REDINTRO_logo.wav'
TITLE_HIT = 0.505                          # logo tune hit the title slams in on (s)
EMBLEM_HITS = (1.596, 1.73, 1.811, 1.898, 2.032, 2.264)   # the RED ALERT letter slams
# The launcher stalls every startup movie for about a second on the Steam Deck (the stock intro
# too), freezing picture and sound, at a moment that has fallen 3.85-4.1 s in. The logo tune is
# cut just before that and Hell March comes in just after, so the stall lands in the breath
# between them and nothing audible is cut.
LOGO_TUNE_END = 3.80                       # where the logo tune is cut (s)
OPENING_FRAMES = 128                       # Hell March's opening hit and the montage at 4.267 s
HELL_MARCH_HIT = 0.279                     # the opening hit's time in Hell March (s)
OUTRO_FRAMES = 60                          # white flash on the final hit, fading to black with its tail
FINAL_HIT = 36.281                         # the bar downbeat the last shot ends on (s)
FKTS = LIB / 'audio/RAB_MUS_HELL_MARCH_FKTS.WAV'
FKTS_STAB, FKTS_GAIN = 211.835, 0.665      # its final stab, scaled to the Remastered level
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
    core = smoke.crop((menu_art.CORE[0], menu_art.CORE[1], menu_art.CORE[0] + W, menu_art.CORE[1] + H))
    return Image.eval(core, lambda v: int(v * menu_art.MARGIN_SHADE))


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


def opening(bg):
    """Black until the title slams in on its hit, then each emblem pops in on its letter slam."""
    title = title_art.render()
    title = title.resize((1300, round(title.height * 1300 / title.width)), Image.LANCZOS)
    marks = [emblem(n, 170) for n in EMBLEMS]
    xs = [960 + (i - 2.5) * 230 for i in range(6)]
    title_frame = round(TITLE_HIT * FPS)
    emblem_frames = [round(t * FPS) for t in EMBLEM_HITS]
    frames = []
    for f in range(OPENING_FRAMES):
        if f < title_frame:
            frames.append(Image.new('RGB', (W, H)))
            continue
        canvas = bg.convert('RGBA')
        s = 1.0 + 0.12 * max(0.0, 1 - (f - title_frame) / 8)
        t = title.resize((round(title.width * s), round(title.height * s)), Image.LANCZOS)
        canvas.alpha_composite(t, (960 - t.width // 2, 300 - t.height // 2))
        for i, mark in enumerate(marks):
            age = f - emblem_frames[i]
            if age < 0:
                continue
            k = 1.0 + 0.3 * max(0.0, 1 - age / 5)
            m = mark.resize((round(mark.width * k), round(mark.height * k)), Image.LANCZOS)
            canvas.alpha_composite(m, (round(xs[i] - m.width / 2), round(760 - m.height / 2)))
        frames.append(flash(canvas.convert('RGB'), max(0.0, 1 - (f - title_frame) / 12)))
    return frames


def outro(last):
    """A white flash off the last shot, fading to black."""
    white = Image.new('RGB', (W, H), (255, 255, 255))
    for f in range(OUTRO_FRAMES):
        if f < 3:
            yield Image.blend(last, white, (f + 1) / 3)
        else:
            yield Image.blend(white, Image.new('RGB', (W, H)), (f - 2) / (OUTRO_FRAMES - 3))


def render(shots):
    bg = backdrop()
    base = framed(bg)
    yield from opening(bg)
    start = OPENING_FRAMES
    band_entry = start + sum(b for _, _, b in shots if b >= 4) * BEAT
    n = start
    for movie, first, beats in shots:
        pictures, box = shot_frames(movie, first, beats)
        for picture in pictures:
            frame = in_window(base, Image.open(picture).crop(box))
            for cut, strengths in ((start, (0.6, 0.25)), (band_entry, (0.7, 0.4, 0.15))):
                if 0 <= n - cut < len(strengths):
                    frame = flash(frame, strengths[n - cut])
            yield frame
            n += 1
    yield from outro(frame)


def load_wav(path):
    """Any audio file as 44.1 kHz stereo float samples (the game's WAVs are MS-ADPCM)."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 's16le', '-ac', '2', '-ar', '44100', '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(float)


def music(seconds, ending):
    """The logo tune, a breath, then Hell March from its opening hit to the final downbeat, then
    the ending:
    A: the Remastered downbeat hit itself rings out through a short echo;
    B: Frank Klepacki and the Tiberian Sons' final stab (FKTS) lands on the downbeat;
    C: Hell March plays on through the white flash and fades out (the menu's own music, the
       Retaliation remix, fades in after it)."""
    rate = 44100
    logo = load_wav(LOGO_TUNE)[:int(LOGO_TUNE_END * rate)].copy()
    logo[-int(0.06 * rate):] *= np.linspace(1, 0, int(0.06 * rate))[:, None]
    hell_march_in = OPENING_FRAMES / FPS
    breath = np.zeros((int(hell_march_in * rate) - len(logo), 2))
    rar = np.concatenate([logo, breath, load_wav(MUSIC)[int(HELL_MARCH_HIT * rate):]])
    cut = int((hell_march_in + FINAL_HIT - HELL_MARCH_HIT) * rate)
    body = rar[:cut].copy()
    body[-176:] *= np.linspace(1, 0, 176)[:, None]
    tail_len = int(seconds * rate) - cut
    t = np.arange(tail_len) / rate
    if ending == 'C':
        fade = np.cos(np.linspace(0, np.pi / 2, tail_len)) ** 2
        return np.clip(np.concatenate([rar[:cut], rar[cut:cut + tail_len] * fade[:, None]]),
                       -32768, 32767).astype(np.int16)
    if ending == 'A':
        hit = rar[cut:cut + tail_len] * np.where(t < 0.06, 1.0, np.exp(-(t - 0.06) / 0.10))[:, None]
        tail = hit.copy()
        for k in range(1, 12):
            d = int(k * 0.11 * rate)
            tail[d:] += hit[:tail_len - d] * (0.5 ** k)
    else:
        fk = load_wav(FKTS)
        start = int((FKTS_STAB - 0.004) * rate)
        tail = fk[start:start + tail_len] * FKTS_GAIN
    tail *= np.clip((tail_len - np.arange(tail_len)) / (0.3 * rate), 0, 1)[:, None]
    return np.clip(np.concatenate([body, tail]), -32768, 32767).astype(np.int16)


def write_wav(path, samples):
    import wave
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(samples.tobytes())


def main(shot_path, mode, out, ending='C'):
    shots = read_shots(shot_path)
    total = OPENING_FRAMES + sum(b for _, _, b in shots) * BEAT + OUTRO_FRAMES
    seconds = total / FPS
    if mode == 'preview':
        wav = Path(out).with_suffix('.wav')
        write_wav(wav, music(seconds, ending))
        ff = subprocess.Popen(
            ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
             '-i', '-', '-i', str(wav), '-t', f'{seconds:.3f}', '-vf', 'scale=1280:720',
             '-c:v', 'libx264', '-crf', '22', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', out],
            stdin=subprocess.PIPE)
        for frame in render(shots):
            ff.stdin.write(frame.tobytes())
        ff.stdin.close()
        ff.wait()
    else:
        Path(out).mkdir(parents=True, exist_ok=True)
        for i, frame in enumerate(render(shots)):
            frame.save(Path(out) / f'frame_{i:05d}.jpg', quality=95)
        write_wav(Path(out) / 'music.wav', music(seconds, ending))
    print(f'{mode}: {total} frames, {seconds:.2f} s -> {out}')


if __name__ == '__main__':
    if len(sys.argv) not in (4, 5) or sys.argv[2] not in ('preview', 'frames') or sys.argv[4:] not in ([], ['A'], ['B'], ['C']):
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
