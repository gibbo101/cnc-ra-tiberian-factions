#!/usr/bin/env python3
"""Store each distinct frame of a tileset ZIP once: shapes whose image is byte-identical to an earlier one point
at that one in the tileset XML, and the copies (and their .meta) leave the ZIP. The launcher draws a shape from
the file its <Frame> names, so any number of shapes may name one file.

Runs over the mod's own tree and every asset pack (scripts/asset_packs.py), each tileset XML against the ZIPs in
its own Data folder. Re-run it after any packer that writes a ZIP; --check reports what it would change and
exits non-zero, which the packager uses to refuse a build with duplicates.

usage: dedupe_tileset_frames.py [--check]
License: GPL v3.
"""
import glob
import hashlib
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs  # noqa: E402

FRAME = re.compile(r"(<Frame>\s*)([^\\<\s]+)\\([^<\s]+?)(\s*</Frame>)")


def data_roots():
    yield asset_packs.data_root(None)
    for pack in asset_packs.PACKS:
        yield asset_packs.pack_data(pack)


def zips_in(root):
    """Lower-case ZIP stem -> path, for every tileset ZIP under a Data folder."""
    out = {}
    for path in glob.glob(os.path.join(root, "ART", "TEXTURES", "SRGB", "RED_ALERT", "**", "*.ZIP"), recursive=True):
        out[os.path.splitext(os.path.basename(path))[0].lower()] = path
    return out


def plan(zip_path):
    """Lower-case member name -> the earlier member it duplicates, for every .tga an earlier .tga matches byte for
    byte. The launcher matches <Frame> names to members without regard to case."""
    seen, dup = {}, {}
    with zipfile.ZipFile(zip_path) as z:
        for name in sorted(n for n in z.namelist() if n.lower().endswith(".tga")):
            h = hashlib.md5(z.read(name)).hexdigest()
            if h in seen:
                dup[name.lower()] = seen[h]
            else:
                seen[h] = name
    return dup


def rewrite_zip(zip_path, dup):
    """The ZIP without the duplicate frames and their .meta, members otherwise kept in order."""
    drop = set(dup) | {os.path.splitext(n)[0] + ".meta" for n in dup}
    tmp = zip_path + ".tmp"
    with zipfile.ZipFile(zip_path) as src, zipfile.ZipFile(tmp, "w") as dst:
        for info in src.infolist():
            if info.filename.lower() not in drop:
                dst.writestr(info, src.read(info.filename), compress_type=info.compress_type)
    os.replace(tmp, zip_path)


def main(argv):
    check = "--check" in argv
    total_saved = 0
    changes = []
    for root in data_roots():
        zips = zips_in(root)
        dups = {}
        xmls = glob.glob(os.path.join(root, "XML", "TILESETS", "*.XML"))
        texts = {x: open(x, encoding="utf-8", newline="").read() for x in xmls}
        referenced = {m.group(2).lower() for t in texts.values() for m in FRAME.finditer(t)}
        for stem in sorted(referenced & set(zips)):
            d = plan(zips[stem])
            if d:
                dups[stem] = d
        if not dups:
            continue
        for x, text in texts.items():
            def repoint(m):
                stem = m.group(2).lower()
                target = dups.get(stem, {}).get(m.group(3).lower())
                return m.group(0) if target is None else m.group(1) + m.group(2) + "\\" + target + m.group(4)
            new = FRAME.sub(repoint, text)
            if new != text:
                changes.append(os.path.relpath(x, asset_packs.REPO))
                if not check:
                    open(x, "w", encoding="utf-8", newline="").write(new)
        for stem, d in dups.items():
            before = os.path.getsize(zips[stem])
            changes.append("%s (%d duplicate frames)" % (os.path.relpath(zips[stem], asset_packs.REPO), len(d)))
            if not check:
                rewrite_zip(zips[stem], d)
                total_saved += before - os.path.getsize(zips[stem])
    for c in changes:
        print(("would change " if check else "changed ") + c)
    if check:
        if changes:
            sys.exit("tileset ZIPs hold duplicate frames: run scripts/dedupe_tileset_frames.py")
        print("dedupe_tileset_frames: no duplicate frames")
    else:
        print("saved %.1f MB" % (total_saved / 2**20))


if __name__ == "__main__":
    main(sys.argv[1:])
