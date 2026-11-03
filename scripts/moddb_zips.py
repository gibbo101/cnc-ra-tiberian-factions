#!/usr/bin/env python3
"""Zip a packaged release for ModDB: the mod with its required asset packs beside it and a README.txt saying how to
install them, which players unzip into Mods/Red_Alert and enable together, and each required pack alone.

usage: moddb_zips.py <out dir> <mod folder> <pack folder> ...

Names come from each folder's ccmod.json: the mod's version as X.Y.Z (version_low is Y * 10 + Z), a pack's as
high.low. package-for-workshop.sh runs it on the staged release.
License: GPL v3.
"""
import json
import os
import sys
import zipfile


def manifest(folder):
    with open(os.path.join(folder, "ccmod.json"), encoding="utf-8") as f:
        return json.load(f)


README = """{title} {version}

EA has not endorsed and does not support this product.

You need Command & Conquer Remastered Collection.

To install:
1. Open Documents/CnCRemastered/Mods/Red_Alert/ and create the Mods and Red_Alert folders if they're missing. On
   Linux or a Steam Deck, Documents is inside the game's Proton prefix:
   steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/
2. Copy {every} folder{s} from this zip into it: {folders}.
3. Launch Red Alert, go to Options > Mods, and enable {names}.
4. Restart the game. It only picks up a change to enabled mods after a restart.

To update, delete the old {old} folder{s} first, then copy in the new ones.

This is a DLL mod: disable other DLL mods, such as CFE Patch, first. It plays in HD graphics only.

Steam Workshop, with automatic updates: https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253
Source and full changelog: https://github.com/gibbo101/cnc-ra-tiberian-factions
"""


def readme(version, folders):
    """The install steps for a zip holding these mod folders."""
    pairs = [(os.path.basename(os.path.normpath(f)), manifest(f)["name"]) for f in folders]
    def join(items):
        return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]
    return README.format(title=pairs[0][1], version=version, every="both" if len(pairs) == 2 else "all",
                         s="s" if len(pairs) > 1 else "", folders=join([f"{d} ({n})" for d, n in pairs]),
                         names=join([n for _, n in pairs]), old=join([d for d, _ in pairs])).replace("\n", "\r\n")


def write_zip(path, folders, readme_text=None):
    """A zip holding each folder under its own name, and README.txt at its root when given."""
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        if readme_text:
            z.writestr("README.txt", readme_text)
        for folder in folders:
            base = os.path.dirname(os.path.normpath(folder))
            for d, _, files in os.walk(folder):
                for f in sorted(files):
                    full = os.path.join(d, f)
                    z.write(full, os.path.relpath(full, base))
    os.replace(tmp, path)
    print(f"wrote {path} ({os.path.getsize(path) // (1024 * 1024)} MB)")


def main(out, mod, packs):
    os.makedirs(out, exist_ok=True)
    m = manifest(mod)
    version = f"{m['version_high']}.{m['version_low'] // 10}.{m['version_low'] % 10}"
    write_zip(os.path.join(out, f"TiberianFactions-{version}.zip"), [mod] + packs, readme(version, [mod] + packs))
    for pack in packs:
        p = manifest(pack)
        name = os.path.basename(os.path.normpath(pack))
        write_zip(os.path.join(out, f"{name}-{p['version_high']}.{p['version_low']}.zip"), [pack])


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
