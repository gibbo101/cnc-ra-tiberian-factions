#!/usr/bin/env python3
"""Builds the TS-Music pack's audio from an installed Tiberian Sun: every in-game theme of Tiberian Sun
and Firestorm, as Remastered music WAVs (44.1 kHz stereo MS-ADPCM), and the track list the music builder reads.

Usage: ts_music_build.py [<Tiberian Sun install folder>]

Writes asset-packs/TS-Music/Data/AUDIO/MUSIC/TS_MUS_<NAME>.WAV (gitignored), asset-packs/TS-Music/tracks.json
(name, title, game, side, seconds) and the WAVs' checksums in scripts/ts_music_work/music.md5.
"""
import configparser
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ra_mix_extract as ra  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(REPO, "asset-packs", "TS-Music")
MUSIC = os.path.join(PACK, "Data", "AUDIO", "MUSIC")
MD5 = os.path.join(REPO, "scripts", "ts_music_work", "music.md5")
DEFAULT_TS = os.path.expanduser("~/.local/share/Steam/steamapps/common/Command & Conquer Tiberian Sun")

# (game, archive holding THEME.INI, the archive inside it or None, its INI, the archive of its scores)
SOURCES = [("TS", "TIBSUN.MIX", "LOCAL.MIX", "THEME.INI", "SCORES.MIX"),
           ("FS", "expand01.mix", None, "THEME01.INI", "SCORES01.MIX")]


def ts_id(name):
    """Tiberian Sun's MIX name hash: CRC32 of the upper-cased name, padded to a multiple of four."""
    n = name.upper()
    length = len(n)
    whole = length & ~3
    if length & 3:
        n += chr(length - whole)
        n += n[whole] * (3 - (length & 3))
    return zlib.crc32(n.encode("ascii")) & 0xFFFFFFFF


def entries(blob):
    """(entries, data start, bytes the offsets index) of an encrypted, flagged or bare MIX blob."""
    first, second = struct.unpack_from("<hh", blob, 0)
    if first == 0 and second & 0x02:
        parsed = ra._parse_mix_blob(blob)
        if parsed:
            return parsed
    base = 4 if first == 0 else 0
    count = struct.unpack_from("<H", blob, base)[0]
    table = base + 6
    return [struct.unpack_from("<iII", blob, table + i * 12) for i in range(count)], table + count * 12, blob


def member(blob, name):
    """A named member's bytes, or None."""
    found, start, raw = entries(blob)
    want = ts_id(name)
    for crc, offset, size in found:
        if crc & 0xFFFFFFFF == want:
            return raw[start + offset:start + offset + size]
    return None


def stem(title):
    """TS_MUS_<TITLE> in upper case, words joined by underscores."""
    return "TS_MUS_" + re.sub(r"[^A-Z0-9]+", "_", title.upper()).strip("_")


def themes(ts):
    """(game, section, title, side, scores archive) for every theme a player hears in game."""
    out = []
    for game, archive, inner, ini, scores in SOURCES:
        blob = open(os.path.join(ts, archive), "rb").read()
        if inner:
            blob = member(blob, inner)
        parser = configparser.ConfigParser(inline_comment_prefixes=(";",), strict=False)
        parser.read_string(member(blob, ini).decode("latin-1"))
        for key in parser["Themes"]:
            section = parser["Themes"][key].strip()
            data = parser[section]
            if data.get("Normal", "yes").strip().lower() == "no":
                continue
            out.append((game, section, data["Name"].strip(), data.get("Side", "").strip(), scores))
    return out


def main():
    ts = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TS
    os.makedirs(MUSIC, exist_ok=True)
    os.makedirs(os.path.dirname(MD5), exist_ok=True)
    tracks, sums = [], []
    archives = {}
    with tempfile.TemporaryDirectory() as tmp:
        for game, section, title, side, scores in themes(ts):
            if scores not in archives:
                archives[scores] = open(os.path.join(ts, scores), "rb").read()
            aud = member(archives[scores], section + ".AUD")
            if aud is None:
                sys.exit(f"{section}.AUD missing from {scores}")
            source = os.path.join(tmp, section + ".AUD")
            open(source, "wb").write(aud)
            name = stem(title)
            wav = os.path.join(MUSIC, name + ".WAV")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", source, "-ar", "44100", "-ac", "2",
                            "-c:a", "adpcm_ms", wav], stderr=subprocess.DEVNULL)
            seconds = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                            "-of", "csv=p=0", wav], capture_output=True, text=True).stdout)
            tracks.append({"name": name, "title": title, "game": game, "side": side, "seconds": round(seconds)})
            sums.append(f"{hashlib.md5(open(wav, 'rb').read()).hexdigest()}  {name}.WAV")
            print(f"{name:40s} {game} {side or '-':4s} {round(seconds):4d}s")
    json.dump(tracks, open(os.path.join(PACK, "tracks.json"), "w"), indent=1)
    open(MD5, "w").write("\n".join(sums) + "\n")
    print(f"{len(tracks)} tracks -> {MUSIC}")


if __name__ == "__main__":
    main()
