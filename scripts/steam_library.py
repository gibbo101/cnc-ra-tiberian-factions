#!/usr/bin/env python3
"""Where Steam keeps a game, its Proton prefix and its Workshop downloads on this machine.

Steam can spread games over several libraries (config/libraryfolders.vdf), and a game's install,
its Proton prefix (compatdata) and its Workshop content all live in the library it went to. Scripts
ask this module instead of naming a library, so they work wherever the games are installed:
  steam_library.path("common/CnCRemastered/Data")         from Python
  python3 scripts/steam_library.py path compatdata/1213210  from a shell script
  python3 scripts/steam_library.py library compatdata/1213210   the library root holding it

License: GPL v3.
"""
import os
import re
import sys
from pathlib import Path

STEAM_FOLDERS = ("~/.steam/steam", "~/.local/share/Steam")


def libraries():
    """Every library root Steam lists, the Steam folder's own library first, no duplicates."""
    roots = []
    for folder in STEAM_FOLDERS:
        folder = os.path.realpath(os.path.expanduser(folder))
        roots.append(folder)
        vdf = os.path.join(folder, "config", "libraryfolders.vdf")
        if os.path.isfile(vdf):
            with open(vdf, encoding="utf-8") as f:
                roots += re.findall(r'"path"\s+"([^"]+)"', f.read())
    unique = []
    for root in roots:
        root = os.path.realpath(root)
        if root not in unique:
            unique.append(root)
    return unique


def library(relative):
    """The library root whose steamapps/ holds `relative`, else the Steam folder's own."""
    found = libraries()
    for root in found:
        if os.path.exists(os.path.join(root, "steamapps", relative)):
            return Path(root)
    return Path(found[0])


def path(relative):
    """<library>/steamapps/<relative> in the library that holds it, e.g. "common/CnCRemastered"."""
    return library(relative) / "steamapps" / relative


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("path", "library"):
        sys.exit("usage: steam_library.py path|library <path under steamapps/>")
    print(path(sys.argv[2]) if sys.argv[1] == "path" else library(sys.argv[2]))
