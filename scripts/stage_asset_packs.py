#!/usr/bin/env python3
"""Stage the asset packs into a built mod folder.

Usage:  stage_asset_packs.py <mod dir> [--full]

Copies every pack's Data/ART and Data/AUDIO into <mod dir>/Data, then writes each of the mod's
XML files that packs contribute to: the mod's own file from resources/, with every pack's
entries in place of that pack's marker (before the closing tag when the file has no marker).
A file two packs carry (an HD cameo over its classic one) is copied from the later pack only, and a tileset
ZIP that copies another's frames is left out (scripts/share_tileset_zips.py).
The XML always starts from the source tree, so staging twice gives the same result.

--full first copies the mod's own tree (resources/remaster_mods/Vanilla_RA) over <mod dir>: a
data-only change is restaged without relinking the DLL. The CMake build runs this script after
its own copy of that tree.

License: GPL v3.
"""
import os
import re
import shutil
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs as A  # noqa: E402
import share_tileset_zips  # noqa: E402

TGA_RLE = 10


def is_rle_cameo(path):
    with open(path, "rb") as f:
        return f.read(3)[2:] == bytes([TGA_RLE])


def copy_newer(src, dst):
    """Copy unless dst already has src's size and is no older, keeping rsync-friendly mtimes. A sidebar cameo
    is written run-length encoded (the launcher reads RLE TGA), the same pixels at about four fifths the size."""
    cameo = os.path.basename(src).upper().startswith("BUILDICON_") and src.upper().endswith(".TGA")
    if os.path.exists(dst):
        a, b = os.stat(src), os.stat(dst)
        same = is_rle_cameo(dst) if cameo else a.st_size == b.st_size
        if same and b.st_mtime >= a.st_mtime:
            return dst
    if cameo:
        Image.open(src).save(dst, compression="tga_rle")
        shutil.copystat(src, dst)
        return dst
    return shutil.copy2(src, dst)


def copy_tree(src, dst, skip=frozenset()):
    """Copy src over dst, leaving out the paths (relative to src, upper case) in skip."""
    if os.path.isdir(src):
        def ignore(d, names):
            rel = os.path.relpath(d, src)
            return [n for n in names if os.path.normpath(os.path.join(rel, n)).upper() in skip]
        shutil.copytree(src, dst, copy_function=copy_newer, dirs_exist_ok=True, ignore=ignore)


def pack_files(pack, sub):
    """A pack's files under Data/<sub>, relative to that folder, upper case."""
    base = os.path.join(A.pack_data(pack), sub)
    return {os.path.relpath(os.path.join(d, f), base).upper() for d, _, fs in os.walk(base) for f in fs}


def pack_body(path, root):
    """A pack XML file's entries: everything between its root element's opening line and close."""
    text = open(path, encoding="utf-8", newline="").read()
    start = re.search(r"<%s\b[^>]*>[ \t]*\r?\n" % root, text).end()
    return text[start:text.rindex(f"</{root}>")]


def merged(rel, pack_file, root):
    text = open(os.path.join(A.MOD, "Data", rel), encoding="utf-8", newline="").read()
    for pack in A.PACKS:
        src = pack_file(pack)
        body = pack_body(src, root) if os.path.exists(src) else ""
        line = re.compile(r"[ \t]*" + re.escape(A.marker(pack)) + r"[ \t]*\r?\n")
        if line.search(text):
            text = line.sub(lambda _: body, text, count=1)
        elif body:
            cut = text.rindex(f"</{root}>")
            text = text[:cut] + body + text[cut:]
    return text


def stage(mod_dir, full=False):
    stray = A.split(dry_run=True)
    if stray:
        raise SystemExit("asset-pack files or XML entries are in resources/remaster_mods/Vanilla_RA: "
                         f"{', '.join(sorted(stray))}. Run scripts/asset_packs.py split, then build again.")
    texts = {rel: merged(rel, pack_file, root) for rel, pack_file, root, _ in A.XML_FILES}
    texts, shared = share_tileset_zips.share(texts, share_tileset_zips.zip_sources())
    if full:
        copy_tree(A.MOD, mod_dir, {os.path.join("DATA", rel) for rel in shared})
    data = os.path.join(mod_dir, "Data")
    for rel in shared:
        stale = os.path.join(data, rel)
        if os.path.exists(stale):
            os.remove(stale)
    packs = list(A.PACKS)
    for i, pack in enumerate(packs):
        for sub in ("ART", "AUDIO"):
            later = set().union(*(pack_files(p, sub) for p in packs[i + 1:]))
            skip = later | {os.path.relpath(rel, sub.upper()) for rel in shared if rel.startswith(sub.upper() + os.sep)}
            copy_tree(os.path.join(A.pack_data(pack), sub), os.path.join(data, sub), skip)
    for rel, text in texts.items():
        dst = os.path.join(data, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst) or open(dst, encoding="utf-8", newline="").read() != text:
            open(dst, "w", encoding="utf-8", newline="").write(text)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        raise SystemExit(__doc__)
    stage(os.path.abspath(args[0]), full="--full" in sys.argv)
