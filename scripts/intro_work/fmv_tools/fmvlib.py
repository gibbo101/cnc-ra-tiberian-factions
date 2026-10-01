#!/usr/bin/env python3
"""Tiberian Factions intro FMV library builder.

Decodes movies, writes browse frames + contact sheets + metadata, and
re-extracts chosen frame ranges at full resolution later.

Library root: ~/Desktop/tf-intro-fmv
  meta/<GAME>/<MOVIE>.json            one record per movie (source, size, fps...)
  frames/<GAME>/<MOVIE>/fNNNNN_SSSS.SSs.jpg   browse frames (<= 960 px wide)
  sheets/<GAME>/<MOVIE>.jpg           contact sheet (or <MOVIE>_partN.jpg)
  sheets/<GAME>/_index/index_NN.jpg   16-frame overview strips, 6 movies a page

Frame numbers are 0-based everywhere (frame 0 is the first picture), so
time = frame / fps.

Decoders
  Bink 2 (.bk2)        tools/bk2dump/bk2dump.exe under Wine (RAD's bink2w32.dll)
  VQA / Bink 1 / OGV   ffmpeg

Commands
  fmvlib.py bk2 <GAME> <MEG> <entry> [--id NAME] [--rate R]
  fmvlib.py file <GAME> <path> [--id NAME] [--source TEXT] [--rate R]
  (bulk runs: tools/build_all.py, which calls cmd_range for every movie)
  fmvlib.py index <GAME>
  fmvlib.py fullres <GAME>/<MOVIE> <first> <last> <outdir> [--step N] [--jpg]
  fmvlib.py headers <MEG>          (frames/size/fps straight from Bink headers)
"""
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.expanduser('~/Desktop/tf-intro-fmv')
TOOLS = os.path.join(ROOT, 'tools')
BK2DUMP_DIR = os.path.join(TOOLS, 'bk2dump')
WINEPREFIX = os.path.expanduser('~/.local/opt/wine-fmv')
WORK = os.environ.get('FMV_WORK', '/tmp/claude-1000/fmvwork')
BROWSE_W = 960
THUMB_W = 240
SHEET_COLS = 8
SHEET_MAX_THUMBS = 400

sys.path.insert(0, TOOLS)
import meg as megmod  # noqa: E402

FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf', 13)
FONT_BIG = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf', 18)


# ---------------------------------------------------------------- probing

def bink_header(blob):
    """(frames, width, height, fps_num, fps_den) from the first 0x24 bytes of a
    Bink 1 ('BIK') or Bink 2 ('KB2') file."""
    frames = struct.unpack_from('<I', blob, 8)[0]
    w, h, num, den = struct.unpack_from('<IIII', blob, 0x14)
    return frames, w, h, num, den


def ffprobe(path):
    out = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets',
         '-show_entries', 'stream=codec_name,width,height,r_frame_rate,nb_frames,nb_read_packets,duration',
         '-of', 'json', path], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)['streams'][0]
    num, den = (int(x) for x in s['r_frame_rate'].split('/'))
    frames = int(s.get('nb_frames') or 0) or int(s.get('nb_read_packets') or 0)
    return s['codec_name'], int(s['width']), int(s['height']), num, den, frames


# ---------------------------------------------------------------- decoders

def wine_env():
    env = dict(os.environ)
    env.pop('DISPLAY', None)
    env.pop('WAYLAND_DISPLAY', None)
    env['WINEPREFIX'] = WINEPREFIX
    env['WINEDEBUG'] = '-all'
    return env


def winpath(p):
    return 'Z:' + os.path.abspath(p).replace('/', '\\')


def decode_bk2(path, frame_list):
    """Yield (frame, PIL.Image RGB) for each 0-based frame in frame_list."""
    fd, listfile = tempfile.mkstemp(suffix='.txt', dir=WORK)
    with os.fdopen(fd, 'w') as f:
        f.write(' '.join(str(x) for x in frame_list))
    proc = subprocess.Popen(
        ['wine', os.path.join(BK2DUMP_DIR, 'bk2dump.exe'), 'dumplist', winpath(path), winpath(listfile)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=wine_env(), cwd=BK2DUMP_DIR)
    try:
        while True:
            hdr = proc.stdout.read(16)
            if len(hdr) < 16:
                break
            magic, frame, w, h = struct.unpack('<4I', hdr)
            if magic != 0x52464b42:
                raise RuntimeError('bad frame header from bk2dump')
            data = proc.stdout.read(w * h * 4)
            if len(data) < w * h * 4:
                raise RuntimeError('short frame from bk2dump')
            yield frame, Image.frombuffer('RGB', (w, h), data, 'raw', 'BGRX', 0, 1)
    finally:
        proc.stdout.close()
        err = proc.stderr.read().decode(errors='replace')
        rc = proc.wait()
        os.unlink(listfile)
        if rc != 0:
            raise RuntimeError(f'bk2dump failed rc={rc}: {err.strip()}')


def decode_ffmpeg(path, frame_list, w, h):
    """Yield (frame, PIL.Image RGB) for each 0-based frame in frame_list."""
    want = set(frame_list)
    last = max(frame_list)
    proc = subprocess.Popen(
        ['ffmpeg', '-v', 'error', '-i', path, '-map', '0:v:0', '-vsync', 'passthrough',
         '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    n = 0
    size = w * h * 3
    try:
        while n <= last:
            data = proc.stdout.read(size)
            if len(data) < size:
                break
            if n in want:
                yield n, Image.frombytes('RGB', (w, h), data)
            n += 1
    finally:
        proc.stdout.close()
        proc.kill()
        proc.wait()


# ---------------------------------------------------------------- outputs

def sample_frames(frames, fps, rate):
    """0-based frame numbers at `rate` samples per second."""
    out = []
    k = 0
    while True:
        f = int(math.floor(k * fps / rate + 0.5))
        if f >= frames:
            break
        if not out or f != out[-1]:
            out.append(f)
        k += 1
    if not out:
        out = [0]
    return out


def browse_size(w, h):
    if w <= BROWSE_W:
        return w, h
    return BROWSE_W, max(2, int(round(h * BROWSE_W / w)))


def frame_name(frame, fps):
    return f'f{frame:05d}_{frame / fps:07.2f}s.jpg'


def fmt_time(t):
    m, s = divmod(t, 60)
    return f'{int(m)}:{s:04.1f}' if m else f'{s:.1f}s'


def make_sheets(game, movie, items, fps, title):
    """items: list of (frame, PIL image at browse size). Writes sheet(s)."""
    sdir = os.path.join(ROOT, 'sheets', game)
    os.makedirs(sdir, exist_ok=True)
    for old in os.listdir(sdir):
        if old == f'{movie}.jpg' or (old.startswith(f'{movie}_part') and old.endswith('.jpg')):
            os.unlink(os.path.join(sdir, old))
    if not items:
        return []
    bw, bh = items[0][1].size
    tw = THUMB_W
    th = max(2, int(round(bh * tw / bw)))
    label_h = 17
    cell_w, cell_h = tw + 4, th + label_h + 4
    parts = [items[i:i + SHEET_MAX_THUMBS] for i in range(0, len(items), SHEET_MAX_THUMBS)]
    names = []
    for pi, part in enumerate(parts):
        rows = (len(part) + SHEET_COLS - 1) // SHEET_COLS
        head = 30
        sheet = Image.new('RGB', (SHEET_COLS * cell_w + 4, head + rows * cell_h + 4), (24, 24, 24))
        d = ImageDraw.Draw(sheet)
        ptxt = f'  (part {pi + 1}/{len(parts)})' if len(parts) > 1 else ''
        d.text((6, 5), f'{title}{ptxt}', font=FONT_BIG, fill=(240, 200, 80))
        for i, (frame, img) in enumerate(part):
            x = 4 + (i % SHEET_COLS) * cell_w
            y = head + (i // SHEET_COLS) * cell_h
            sheet.paste(img.resize((tw, th), Image.BILINEAR), (x, y))
            d.text((x + 2, y + th + 1), f'{fmt_time(frame / fps)}  #{frame}', font=FONT, fill=(230, 230, 230))
        name = f'{movie}.jpg' if len(parts) == 1 else f'{movie}_part{pi + 1}.jpg'
        sheet.save(os.path.join(sdir, name), quality=82)
        names.append(f'sheets/{game}/{name}')
    return names


def process(game, movie, decoder, frames, fps_num, fps_den, w, h, source, rate):
    fps = fps_num / fps_den
    fdir = os.path.join(ROOT, 'frames', game, movie)
    if os.path.isdir(fdir):
        shutil.rmtree(fdir)
    os.makedirs(fdir)
    picks = sample_frames(frames, fps, rate)
    duration = frames / fps
    sheet_rate = 2.0 if duration < 20 else 1.0
    sheet_set = set(sample_frames(frames, fps, sheet_rate))
    bwh = browse_size(w, h)
    sheet_items = []
    written = 0
    for frame, img in decoder(picks):
        if img.size != bwh:
            factor = img.width // bwh[0]
            if factor >= 2:
                img = img.reduce(factor)
            if img.size != bwh:
                img = img.resize(bwh, Image.LANCZOS)
        img.save(os.path.join(fdir, frame_name(frame, fps)), quality=85)
        written += 1
        if frame in sheet_set or rate < sheet_rate:
            sheet_items.append((frame, img.copy()))
    title = f'{game} / {movie}   {w}x{h}  {fps:.3f} fps  {frames} frames  {fmt_time(duration)}'
    sheets = make_sheets(game, movie, sheet_items, fps, title)
    meta = dict(game=game, id=movie, width=w, height=h, fps_num=fps_num, fps_den=fps_den,
                fps=round(fps, 3), frames=frames, duration=round(duration, 2),
                browse_frames=written, browse_rate=rate, browse_size=list(bwh),
                sheets=sheets, frames_dir=f'frames/{game}/{movie}', **source)
    mdir = os.path.join(ROOT, 'meta', game)
    os.makedirs(mdir, exist_ok=True)
    with open(os.path.join(mdir, f'{movie}.json'), 'w') as f:
        json.dump(meta, f, indent=1)
    print(f'{game}/{movie}: {w}x{h} {fps:.3f}fps {frames}f {duration:.1f}s -> {written} frames, {len(sheets)} sheet(s)',
          flush=True)
    return meta


# ---------------------------------------------------------------- commands

def sanitize(name):
    return name.replace(' ', '_')


def copy_range(container, offset, size, dst):
    with open(container, 'rb') as f, open(dst, 'wb') as o:
        f.seek(offset)
        left = size
        while left:
            chunk = f.read(min(left, 16 << 20))
            if not chunk:
                raise IOError('short read from ' + container)
            o.write(chunk)
            left -= len(chunk)


def cmd_range(game, movie, container, offset, size, source_archive, source_entry, rate=2.0, extra=None):
    """Decode the movie stored at container[offset:offset+size] (a loose file
    has offset 0 and its full size). Archive members are copied to a temp
    file first and deleted afterwards."""
    os.makedirs(WORK, exist_ok=True)
    with open(container, 'rb') as f:
        f.seek(offset)
        head = f.read(64)
    src = dict(source_archive=source_archive, source_entry=source_entry, source_bytes=size,
               container=container, offset=offset)
    if extra:
        src.update(extra)
    tmpdir = None
    if offset == 0 and size == os.path.getsize(container):
        path = container
    else:
        tmpdir = tempfile.mkdtemp(dir=WORK)
        ext = os.path.splitext(source_entry)[1] or '.bin'
        path = os.path.join(tmpdir, 'movie' + ext)
        copy_range(container, offset, size, path)
    try:
        if head[:3] == b'KB2':
            frames, w, h, num, den = bink_header(head)
            src['codec'] = 'Bink 2'
            return process(game, movie, lambda picks: decode_bk2(path, picks), frames, num, den, w, h, src, rate)
        codec, w, h, num, den, frames = ffprobe(path)
        src['codec'] = codec
        return process(game, movie, lambda picks: decode_ffmpeg(path, picks, w, h), frames, num, den, w, h, src, rate)
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


def meg_entry(meg_path, entry):
    for name, size, off in megmod.index(meg_path):
        if name == entry:
            return off, size
    raise SystemExit(f'{entry} not in {meg_path}')


def load_meta(game):
    mdir = os.path.join(ROOT, 'meta', game)
    out = []
    for fn in sorted(os.listdir(mdir)):
        if fn.endswith('.json'):
            with open(os.path.join(mdir, fn)) as f:
                out.append(json.load(f))
    return out


def cmd_index(game, per_page=6, per_movie=16):
    """Overview pages: each movie gets 16 evenly spaced browse frames."""
    metas = load_meta(game)
    idir = os.path.join(ROOT, 'sheets', game, '_index')
    if os.path.isdir(idir):
        shutil.rmtree(idir)
    os.makedirs(idir)
    tw, cols = 150, 8
    pages = [metas[i:i + per_page] for i in range(0, len(metas), per_page)]
    written = []
    for pi, page in enumerate(pages):
        blocks = []
        for m in page:
            fdir = os.path.join(ROOT, m['frames_dir'])
            files = sorted(os.listdir(fdir))
            if len(files) > per_movie:
                step = len(files) / per_movie
                files = [files[int(i * step + step / 2)] for i in range(per_movie)]
            bw, bh = m['browse_size']
            th = int(round(bh * tw / bw))
            th = min(th, 110)
            rows = (len(files) + cols - 1) // cols
            blk = Image.new('RGB', (cols * (tw + 2) + 2, 24 + rows * (th + 16)), (24, 24, 24))
            d = ImageDraw.Draw(blk)
            d.text((4, 3), f"{m['id']}   {m['width']}x{m['height']}  {fmt_time(m['duration'])}",
                   font=FONT_BIG, fill=(240, 200, 80))
            for i, fn in enumerate(files):
                im = Image.open(os.path.join(fdir, fn)).resize((tw, th), Image.BILINEAR)
                x = 2 + (i % cols) * (tw + 2)
                y = 24 + (i // cols) * (th + 16)
                blk.paste(im, (x, y))
                fr = int(fn[1:6])
                d.text((x + 1, y + th), f"{fmt_time(fr / m['fps'])} #{fr}", font=FONT, fill=(220, 220, 220))
            blocks.append(blk)
        H = sum(b.height for b in blocks) + 4 * len(blocks)
        page_img = Image.new('RGB', (max(b.width for b in blocks), H), (60, 60, 60))
        y = 0
        for b in blocks:
            page_img.paste(b, (0, y))
            y += b.height + 4
        name = os.path.join(idir, f'index_{pi + 1:02d}.jpg')
        page_img.save(name, quality=80)
        written.append((name, [m['id'] for m in page]))
    with open(os.path.join(idir, 'pages.txt'), 'w') as f:
        for name, ids in written:
            f.write(f"{os.path.basename(name)}: {', '.join(ids)}\n")
    print(f'{game}: {len(written)} index pages')


def cmd_fullres(gm, first, last, outdir, step=1, jpg=False):
    """Write frames first..last (0-based, inclusive; last=-1 for the end) of a
    catalogued movie at native resolution as PNG (or JPEG q95 with --jpg)."""
    game, movie = gm.split('/')
    with open(os.path.join(ROOT, 'meta', game, f'{movie}.json')) as f:
        m = json.load(f)
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    last = m['frames'] - 1 if last < 0 else min(last, m['frames'] - 1)
    picks = list(range(first, last + 1, step))
    container, offset, size = m['container'], m['offset'], m['source_bytes']
    tmpdir = None
    if offset == 0 and size == os.path.getsize(container):
        path = container
    else:
        tmpdir = tempfile.mkdtemp(dir=WORK)
        path = os.path.join(tmpdir, 'movie' + (os.path.splitext(m['source_entry'])[1] or '.bin'))
        copy_range(container, offset, size, path)
    try:
        if m['codec'] == 'Bink 2':
            dec = decode_bk2(path, picks)
        else:
            dec = decode_ffmpeg(path, picks, m['width'], m['height'])
        ext = 'jpg' if jpg else 'png'
        n = 0
        for frame, img in dec:
            img.save(os.path.join(outdir, f'{movie}_f{frame:05d}.{ext}'), **({'quality': 95} if jpg else {'compress_level': 1}))
            n += 1
        print(f'wrote {n} full-res frames ({m["width"]}x{m["height"]}) to {outdir}')
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


def main(argv):
    def opt(flag, default=None, conv=str):
        if flag in argv:
            i = argv.index(flag)
            v = conv(argv[i + 1])
            del argv[i:i + 2]
            return v
        return default
    movie_id = opt('--id')
    rate = opt('--rate', 2.0, float)
    source = opt('--source')
    step = opt('--step', 1, int)
    jpg = '--jpg' in argv
    if jpg:
        argv.remove('--jpg')
    cmd = argv[1]
    if cmd == 'bk2':
        game, meg_path, entry = argv[2], argv[3], argv[4]
        off, size = meg_entry(meg_path, entry)
        movie = movie_id or sanitize(os.path.splitext(entry.split('\\')[-1])[0])
        cmd_range(game, movie, meg_path, off, size, os.path.basename(meg_path), entry, rate)
    elif cmd == 'file':
        path = argv[3]
        movie = movie_id or sanitize(os.path.splitext(os.path.basename(path))[0])
        cmd_range(argv[2], movie, path, 0, os.path.getsize(path), source or path, os.path.basename(path), rate)
    elif cmd == 'index':
        cmd_index(argv[2])
    elif cmd == 'fullres':
        cmd_fullres(argv[2], int(argv[3]), int(argv[4]), argv[5], step, jpg)
    elif cmd == 'headers':
        with open(argv[2], 'rb') as f:
            for name, size, off in megmod.index(argv[2]):
                f.seek(off)
                head = f.read(64)
                if head[:3] in (b'KB2', b'BIK'):
                    fr, w, h, num, den = bink_header(head)
                    print(f'{name}\t{w}x{h}\t{fr}\t{num / den:.3f}\t{fr / (num / den):.1f}s')
                else:
                    print(f'{name}\t(not bink: {head[:4]!r})')
    else:
        print(__doc__)


if __name__ == '__main__':
    main(sys.argv)
