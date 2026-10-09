#!/usr/bin/env python3
"""Share identical frames across tileset ZIPs in a staged build, so a type whose art is another type's copy (the
tower plugs, the faction yards and clones) ships no ZIP of its own. The source tree keeps every copy, each
separately editable; staging (scripts/stage_asset_packs.py) calls share() on the merged tileset XML.

A frame whose .tga and .meta match an earlier ZIP's byte for byte is drawn from that ZIP: the launcher resolves a
<Frame>'s folder to any ZIP, whatever the tile's name. A ZIP no frame names any more is left out of the build,
unless the base game has art by that name (frame_share_work/base_game_stems.txt), which the launcher would draw.

Usage: share_tileset_zips.py   (reports what staging would share; changes nothing)
License: GPL v3.
"""
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs as A  # noqa: E402

FRAME = re.compile(r"(<Frame>\s*)([^\\<\s]+)\\([^<\s]+?)(\s*</Frame>)")
ART = os.path.join("ART", "TEXTURES", "SRGB", "RED_ALERT")
BASE_GAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frame_share_work", "base_game_stems.txt")


def zip_sources():
    """Upper-case ZIP stem -> (its path under a mod's Data folder, upper case; the source file staging copies)."""
    out = {}
    for data in [os.path.join(A.MOD, "Data")] + [A.pack_data(p) for p in A.PACKS]:
        for d, _, files in os.walk(os.path.join(data, ART)):
            for f in files:
                if f.upper().endswith(".ZIP"):
                    path = os.path.join(d, f)
                    out[os.path.splitext(f)[0].upper()] = (os.path.relpath(path, data).upper(), path)
    return out


def frames(path):
    """Lower-case .tga name -> (its name, identity key) for every frame in a ZIP; the key pairs the .tga's and
    .meta's CRC and size, which equal bytes always share."""
    with zipfile.ZipFile(path) as z:
        info = {i.filename.lower(): i for i in z.infolist()}
    out = {}
    for low, i in info.items():
        if low.endswith(".tga"):
            meta = info.get(low[:-4] + ".meta")
            out[low] = (i.filename, (i.CRC, i.file_size, meta.CRC if meta else 0, meta.file_size if meta else 0))
    return out


def same_bytes(a, b):
    """Whether two (ZIP path, .tga name) frames hold the same .tga and .meta bytes."""
    def read(path, name):
        with zipfile.ZipFile(path) as z:
            names = {n.lower(): n for n in z.namelist()}
            meta = names.get(name.lower()[:-4] + ".meta")
            return z.read(name), z.read(meta) if meta else b""
    return read(*a) == read(*b)


def share(texts, sources):
    """The tileset XML texts (path -> text) with each frame drawn from the first ZIP holding its bytes, and the
    Data-relative paths of the ZIPs no frame names any more."""
    tileset = {rel for rel in texts if os.path.normpath(rel).upper().startswith(os.path.join("XML", "TILESETS"))}
    named = sorted({m.group(2).upper() for rel in tileset for m in FRAME.finditer(texts[rel])} & set(sources))
    canon, classes = {}, {}
    for stem in named:
        path = sources[stem][1]
        for low, (name, key) in sorted(frames(path).items()):
            for first in classes.setdefault(key, []):
                if same_bytes(first[1:], (path, name)):
                    canon[(stem, low)] = first[0]
                    break
            else:
                classes[key].append((stem.lower() + "\\" + name, path, name))
                canon[(stem, low)] = classes[key][-1][0]
    used = set()

    def repoint(m):
        ref = canon.get((m.group(2).upper(), m.group(3).lower()))
        if ref is None:
            used.add(m.group(2).upper())
            return m.group(0)
        used.add(ref.split("\\")[0].upper())
        return m.group(1) + ref + m.group(4)

    out = dict(texts)
    for rel in tileset:
        out[rel] = FRAME.sub(repoint, texts[rel])
    base = {line.strip() for line in open(BASE_GAME) if line.strip()}
    dropped = sorted(sources[s][0] for s in named if s not in used and s not in base)
    return out, dropped


if __name__ == "__main__":
    import stage_asset_packs  # noqa: E402
    texts = {rel: stage_asset_packs.merged(rel, pf, root) for rel, pf, root, _ in A.XML_FILES}
    sources = zip_sources()
    _, dropped = share(texts, sources)
    size = sum(os.path.getsize(sources[os.path.splitext(os.path.basename(r))[0]][1]) for r in dropped)
    for r in dropped:
        print("left out:", r)
    print("%d ZIPs, %.1f MB, left out of the build" % (len(dropped), size / 2**20))
