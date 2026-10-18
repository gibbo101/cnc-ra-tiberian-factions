#!/usr/bin/env python3
"""Stage the asset packs into a built mod folder.

Usage:  stage_asset_packs.py <mod dir> [--full] [--strict]

Copies every pack's Data/ART and Data/AUDIO into <mod dir>/Data, except the PACK_ONLY objects and the packs a
Workshop mod in asset_packs.USED carries: that mod is built whole in the folder beside it (scripts/workshop_packs.py). Then
writes each of the mod's XML files that packs contribute to: the mod's own file from resources/,
with every pack's entries in place of that pack's marker (before the closing tag when the file has
no marker).
A file two packs carry is copied from the later pack only, and a tileset
ZIP that copies another's frames is left out (scripts/share_tileset_zips.py).
The XML always starts from the source tree, so staging twice gives the same result.

--full first copies the mod's own tree (resources/remaster_mods/Vanilla_RA) over <mod dir>: a
data-only change is restaged without relinking the DLL. The CMake build runs this script after
its own copy of that tree.
--strict stops when a Workshop mod in asset_packs.USED lacks a gitignored file; without it that mod is skipped
with a warning, so a checkout without the files still builds. deploy.sh and the packager pass it.

License: GPL v3.
"""
import os
import re
import shutil
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs as A  # noqa: E402
import share_tileset_zips  # noqa: E402
import workshop_packs  # noqa: E402

def copy_tree(src, dst, skip=frozenset()):
    """Copy src over dst, leaving out the paths (relative to src, upper case) in skip."""
    if os.path.isdir(src):
        def ignore(d, names):
            rel = os.path.relpath(d, src)
            return [n for n in names if os.path.normpath(os.path.join(rel, n)).upper() in skip]
        shutil.copytree(src, dst, copy_function=A.copy_newer, dirs_exist_ok=True, ignore=ignore)


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


def stage(mod_dir, full=False, strict=False):
    stray = A.split(dry_run=True)
    if stray:
        raise SystemExit("asset-pack files or XML entries are in resources/remaster_mods/Vanilla_RA: "
                         f"{', '.join(sorted(stray))}. Run scripts/asset_packs.py split, then build again.")
    texts = {rel: A.drop_pack_only(merged(rel, pack_file, root)) for rel, pack_file, root, _ in A.XML_FILES}
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
            src = os.path.join(A.pack_data(pack), sub)
            if A.used_mod(pack):
                for d, _, fs in os.walk(src):
                    for f in fs:
                        stale = os.path.join(data, sub, os.path.relpath(os.path.join(d, f), src))
                        if os.path.exists(stale):
                            os.remove(stale)
                continue
            later = set().union(*(pack_files(p, sub) for p in packs[i + 1:]))
            skip = later | {os.path.relpath(rel, sub.upper()) for rel in shared if rel.startswith(sub.upper() + os.sep)}
            skip |= {os.path.relpath(A.art_zip(name, "UNITS"), src).upper() for name in A.PACK_ONLY}
            copy_tree(src, os.path.join(data, sub), skip)
    for mod in A.USED:
        workshop_packs.build(mod, os.path.join(os.path.dirname(os.path.normpath(mod_dir)), mod), strict=strict)
    for rel, text in texts.items():
        dst = os.path.join(data, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst) or open(dst, encoding="utf-8", newline="").read() != text:
            open(dst, "w", encoding="utf-8", newline="").write(text)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        raise SystemExit(__doc__)
    stage(os.path.abspath(args[0]), full="--full" in sys.argv, strict="--strict" in sys.argv)
