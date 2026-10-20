#!/usr/bin/env python3
"""Checks what we publish against EA's C&C modding guidelines (docs/ea-modding-guidelines.md): the required
disclaimer opens every Workshop description and the repo README, and no upload folder holds a music file.

Usage: ea_guidelines_check.py [--manifest <uploader json>]... [--content <upload folder>]... [--readme <file>]...
Prints each problem and exits 1 when there is one.
"""
import json
import os
import re
import sys

DISCLAIMER = "EA has not endorsed and does not support this product."
MUSIC_EXTENSIONS = (".wav", ".aud", ".mp3", ".ogg", ".flac", ".wma")
LEAD_IN = 300  # characters a page may spend on its title and markup before the disclaimer


def opens_with_disclaimer(text):
    """True when the disclaimer appears near the top, once markup is stripped."""
    plain = re.sub(r"\[/?[a-z0-9]+(=[^\]]*)?\]|\*\*|^#.*$", "", text, flags=re.I | re.M)
    at = plain.find(DISCLAIMER)
    return 0 <= at <= LEAD_IN


def check_manifest(path):
    text = json.load(open(path, encoding="utf-8"))["description"]
    return [] if opens_with_disclaimer(text) else [f"{path}: the description doesn't open with \"{DISCLAIMER}\""]


def check_readme(path):
    text = open(path, encoding="utf-8").read()
    return [] if opens_with_disclaimer(text) else [f"{path}: doesn't open with \"{DISCLAIMER}\""]


def check_content(folder):
    """Every music file under an AUDIO\\MUSIC folder: the guidelines forbid music from any C&C game."""
    found = []
    for d, _, files in os.walk(folder):
        if "music" not in d.lower().replace("\\", "/").split("/"):
            continue
        found += [os.path.join(d, f) for f in files if f.lower().endswith(MUSIC_EXTENSIONS)]
    if not found:
        return []
    return [f"{folder}: {len(found)} music file(s), e.g. {found[0]}; mods must not include C&C music"]


def main(args):
    problems = []
    for flag, value in zip(args[::2], args[1::2]):
        problems += {"--manifest": check_manifest, "--content": check_content, "--readme": check_readme}[flag](value)
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) % 2 == 0:
        raise SystemExit(__doc__)
    sys.exit(main(sys.argv[1:]))
