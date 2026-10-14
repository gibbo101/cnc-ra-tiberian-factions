#!/usr/bin/env python3
"""Zip a packaged release for ModDB: the mod with its required asset packs beside it, which players unzip into
Mods/Red_Alert and enable together, and each required pack alone, for an add-on download.

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


def write_zip(path, folders):
    """A zip holding each folder under its own name."""
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
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
    write_zip(os.path.join(out, f"TiberianFactions-{version}.zip"), [mod] + packs)
    for pack in packs:
        p = manifest(pack)
        name = os.path.basename(os.path.normpath(pack))
        write_zip(os.path.join(out, f"{name}-{p['version_high']}.{p['version_low']}.zip"), [pack])


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
