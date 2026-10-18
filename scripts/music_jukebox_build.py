#!/usr/bin/env python3
"""Writes the mod's loose AUDIO_SYSTEM_CONSTANTS.XML: the base file with a jukebox entry for every track in
the TS-Music pack, titled "(Tiberian Sun) <title>" or "(Firestorm) <title>", and those titles in ModText.csv.

Usage: music_jukebox_build.py <base AUDIO_SYSTEM_CONSTANTS.XML> <tracks.json> <out XML> <ModText.csv>
"""
import json
import re
import sys

GAME = "Red_Alert"
TRACK_TYPE = "Remaster"
SOURCE_TITLES = {"TS": "Tiberian Sun", "FS": "Firestorm"}
ENTRY = """\t\t\t<entry Name="{name}">
\t\t\t\t<FileName> {file}.WAV </FileName>
\t\t\t\t<TextID> TEXT_MUSIC_{file} </TextID>
\t\t\t\t<TrackType> {kind} </TrackType>
\t\t\t\t<TrackLengthSeconds> {seconds} </TrackLengthSeconds>
\t\t\t\t<Game> {game} </Game>
\t\t\t\t<BonusContentUnlock> False </BonusContentUnlock>
\t\t\t</entry>

"""


def entries(tracks, eol):
    """The jukebox entries of the pack's tracks, in the file's own line endings."""
    text = ""
    for t in tracks:
        name = "TS_" + re.sub(r"[^A-Za-z0-9]+", "_", t["title"]).strip("_")
        text += ENTRY.format(name=name, file=t["name"], kind=TRACK_TYPE, seconds=t["seconds"], game=GAME)
    return text.replace("\n", eol)


def text_rows(csv_path, tracks):
    """Rewrites ModText.csv's TEXT_MUSIC_TS_MUS_* rows from the pack's titles, so a retitled or removed track
    follows; returns the number of rows written."""
    text = open(csv_path, "rb").read().decode("utf-16")
    eol = "\r\n" if "\r\n" in text else "\n"
    columns = text.splitlines()[0].count(",")
    kept = [line for line in text.split(eol) if not line.startswith('"TEXT_MUSIC_TS_MUS_')]
    while kept and kept[-1] == "":
        kept.pop()
    rows = [f'"TEXT_MUSIC_{t["name"]}",,,"({SOURCE_TITLES[t["game"]]}) {t["title"]}"' + "," * (columns - 3)
            for t in tracks]
    out = eol.join(kept + rows) + eol
    if out != text:
        open(csv_path, "wb").write(out.encode("utf-16"))
    return len(rows)


def main(base_path, tracks_json, out_path, csv_path):
    raw = open(base_path, "rb").read().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"
    tracks = json.load(open(tracks_json))
    close = raw.index("\t\t</MusicJukeboxTracksList>")
    out = raw[:close] + entries(tracks, eol) + raw[close:]
    open(out_path, "wb").write(out.encode("utf-8"))
    rows = text_rows(csv_path, tracks)
    print(f"OK: {len(tracks)} jukebox entries -> {out_path}; {rows} ModText rows")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:5])
