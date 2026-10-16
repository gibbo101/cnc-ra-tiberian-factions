#!/usr/bin/env python3
"""Write the encyclopedia's descriptions into the mod's ModText.csv (docs/encyclopedia.md).

usage: encyclopedia_text.py

From scripts/encyclopedia_work/descriptions.json (each entry's text from the original manuals, or written for TF
where no manual has one, each faction's overview, and each weapon's readable name), writes TEXT_TF_ENC_<INI>,
TEXT_TF_ENC_ABOUT_<FACTION> and TEXT_TF_ENC_WEAPON_<WEAPON, in capitals> rows between this script's markers in
resources/.../Data/ModText.csv, replacing the block it wrote last time, and warns about any entry in
scripts/encyclopedia_work/entries.tsv still without a description, or a weapon (from the mod's CCDATA INIs)
without a name.
License: GPL v3.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / 'scripts/encyclopedia_work/descriptions.json'
ENTRIES = REPO / 'scripts/encyclopedia_work/entries.tsv'
CSV = REPO / 'resources/remaster_mods/Vanilla_RA/Data/ModText.csv'
CCDATA = REPO / 'resources/remaster_mods/Vanilla_RA/CCDATA'
BEGIN = '"// BEGIN generated encyclopedia text (scripts/encyclopedia_text.py)"'
END = '"// END generated encyclopedia text"'
LANGUAGES = 19   # columns after ENGLISH in the header row


def row(key, text):
    assert '"' not in text, key
    return f'"{key}",,,"{text}"' + ',' * LANGUAGES


def weapons_of(inis):
    """The Primary and Secondary weapons of `inis`, as rules.ini sets them and aftrmath.ini and mplayer.ini override."""
    found = {}
    for name in ('rules.ini', 'aftrmath.ini', 'mplayer.ini'):
        section = None
        for line in (CCDATA / name).read_text(encoding='latin-1').splitlines():
            line = line.split(';')[0].strip()
            head = re.match(r'\[(.+)\]', line)
            if head:
                section = head.group(1).upper()
            elif section in inis and '=' in line:
                key, value = (part.strip() for part in line.split('=', 1))
                if key.lower() in ('primary', 'secondary'):
                    found[(section, key.lower())] = value
    return {w for w in found.values() if w.lower() != 'none'}


def main():
    data = json.loads(SOURCE.read_text())
    rows = [row(f'TEXT_TF_ENC_ABOUT_{faction}', text) for faction, text in sorted(data['about'].items())]
    rows += [row(f'TEXT_TF_ENC_{ini}', entry['text']) for ini, entry in sorted(data['entries'].items())]
    rows += [row(f'TEXT_TF_ENC_WEAPON_{weapon.upper()}', name) for weapon, name in sorted(data['weapons'].items())]
    text = CSV.read_bytes().decode('utf-16')
    eol = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(eol)
    if BEGIN + ',' * (LANGUAGES + 3) in lines:
        start = lines.index(BEGIN + ',' * (LANGUAGES + 3))
        stop = lines.index(END + ',' * (LANGUAGES + 3))
        del lines[start:stop + 1]
    while lines and lines[-1] == '':
        lines.pop()
    lines += [BEGIN + ',' * (LANGUAGES + 3)] + rows + [END + ',' * (LANGUAGES + 3), '']
    CSV.write_bytes(eol.join(lines).encode('utf-16'))
    print(f'wrote {len(rows)} encyclopedia rows to {CSV.name}')
    listed = {line.split('\t')[2] for line in ENTRIES.read_text().splitlines() if line}
    untold = sorted(listed - set(data['entries']))
    if untold:
        print(f'WARNING: no description in {SOURCE.name} (the game\'s one-liner shows): {" ".join(untold)}')
    unnamed = sorted(weapons_of(listed) - set(data['weapons']))
    if unnamed:
        print(f'WARNING: no weapon name in {SOURCE.name} (the INI name shows): {" ".join(unnamed)}')


if __name__ == '__main__':
    main()
