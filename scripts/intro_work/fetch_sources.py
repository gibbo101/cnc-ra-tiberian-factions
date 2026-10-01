#!/usr/bin/env python3
"""Rebuild the part of the FMV library the startup intro needs, straight from the game installs.

For every movie named in the shot list it writes the record fmvlib.py's `fullres` reads
(meta/<GAME>/<MOVIE>.json): Remastered Bink 2 movies are read in place from their MEG archive,
and Tiberian Sun VQAs are copied out of their MIX (or the loose file) into sources/TS/. It also
extracts the music the cut uses into audio/ (Hell March), installs the decoding tools into tools/ and builds
tools/bk2dump/bk2dump.exe, which decodes Bink 2 through the game's own bink2w32.dll under Wine.

The library lives at $TF_FMV_LIB, default ~/Desktop/Tiberian Factions/tf-intro-lib.

usage: fetch_sources.py [shots.tsv]
"""
import json
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'fmv_tools'))
sys.path.insert(0, str(HERE.parent))
import meg  # noqa: E402
import tsmix  # noqa: E402

LIB = Path(os.environ.get('TF_FMV_LIB', Path.home() / 'Desktop/Tiberian Factions/tf-intro-lib'))
REMASTERED = Path.home() / '.steam/steam/steamapps/common/CnCRemastered'
TS_INSTALL = Path.home() / '.local/share/Steam/steamapps/common/Command & Conquer Tiberian Sun'
MOVIE_MEGS = {'RA': 'MOVIES_RA.MEG', 'TD': 'MOVIES_TD.MEG'}
TS_MIXES = ('MOVIES01.MIX', 'MOVIES02.MIX', 'movies03.mix')
MUSIC = {'RAR_MUS_HELL_MARCH.WAV': 'RAR_MUS_HELL_MARCH_pcm16.wav',
         'RAB_MUS_HELL_MARCH_FKTS.WAV': 'RAB_MUS_HELL_MARCH_FKTS.WAV'}


def shot_movies(path):
    movies = []
    for line in open(path):
        if line.strip() and not line.startswith('#'):
            movie = line.split('\t')[0]
            if movie not in movies:
                movies.append(movie)
    return movies


def bink2_record(game, name):
    archive = REMASTERED / 'Data' / MOVIE_MEGS[game]
    entry = f'DATA\\ART\\MOVIES\\{game}\\{name}.BK2'
    for ename, size, offset in meg.index(str(archive)):
        if ename.upper() == entry:
            with open(archive, 'rb') as f:
                f.seek(offset)
                head = f.read(0x24)
            frames = struct.unpack_from('<I', head, 8)[0]
            w, h, num, den = struct.unpack_from('<IIII', head, 0x14)
            return {'container': str(archive), 'offset': offset, 'source_bytes': size,
                    'source_entry': entry, 'codec': 'Bink 2', 'width': w, 'height': h,
                    'fps': round(num / den, 3), 'frames': frames}
    sys.exit(f'{entry} not found in {archive}')


def ts_vqa(name):
    out = LIB / 'sources/TS' / f'{name}.VQA'
    out.parent.mkdir(parents=True, exist_ok=True)
    loose = TS_INSTALL / f'{name}.VQA'
    if loose.exists():
        shutil.copyfile(loose, out)
        return out
    want = tsmix.ts_id(f'{name}.VQA')
    for mix in TS_MIXES:
        entries, base, raw = tsmix.entries(str(TS_INSTALL / mix), True)
        for crc, off, size, _kind, _n, _d in entries:
            if crc == want:
                out.write_bytes(raw[base + off:base + off + size])
                return out
    sys.exit(f'{name}.VQA not found in the Tiberian Sun install')


def vqa_record(name):
    path = ts_vqa(name)
    probe = json.loads(subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries',
         'stream=width,height,r_frame_rate,nb_read_packets', '-of', 'json', str(path)],
        capture_output=True, text=True, check=True).stdout)['streams'][0]
    num, den = (int(x) for x in probe['r_frame_rate'].split('/'))
    return {'container': str(path), 'offset': 0, 'source_bytes': path.stat().st_size,
            'source_entry': path.name, 'codec': 'VQA', 'width': int(probe['width']),
            'height': int(probe['height']), 'fps': round(num / den, 3),
            'frames': int(probe['nb_read_packets'])}


def install_tools():
    tools = LIB / 'tools'
    (tools / 'bk2dump').mkdir(parents=True, exist_ok=True)
    for f in ('fmvlib.py', 'meg.py', 'radvideo.sh'):
        shutil.copy2(HERE / 'fmv_tools' / f, tools / f)
    shutil.copyfile(REMASTERED / 'bink2w32.dll', tools / 'bk2dump/bink2w32.dll')
    subprocess.run(['i686-w64-mingw32-gcc', '-O2', '-o', str(tools / 'bk2dump/bk2dump.exe'),
                    str(HERE / 'fmv_tools/bk2dump.c')], check=True)


def fetch_music():
    audio = LIB / 'audio'
    audio.mkdir(parents=True, exist_ok=True)
    archive = REMASTERED / 'Data/MUSIC.MEG'
    for src, dst in MUSIC.items():
        entry = f'DATA\\AUDIO\\MUSIC\\{src}'
        for ename, size, offset in meg.index(str(archive)):
            if ename.upper() == entry:
                with open(archive, 'rb') as f:
                    f.seek(offset)
                    data = f.read(size)
                tmp = audio / (dst + '.src')
                tmp.write_bytes(data)
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(tmp), '-c:a', 'pcm_s16le',
                                '-ar', '44100', '-ac', '2', str(audio / dst)], check=True)
                tmp.unlink()
                break
        else:
            sys.exit(f'{entry} not found in {archive}')


def main(shots):
    install_tools()
    fetch_music()
    for movie in shot_movies(shots):
        game, name = movie.split('/')
        record = vqa_record(name) if game == 'TS' else bink2_record(game, name)
        out = LIB / 'meta' / game / f'{name}.json'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=1))
        print(f"{movie:14s} {record['codec']:6s} {record['width']}x{record['height']} "
              f"{record['fps']} fps {record['frames']} frames")
    print(f'library ready at {LIB}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else str(HERE / 'shots.tsv'))
