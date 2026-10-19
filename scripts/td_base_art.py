#!/usr/bin/env python3
"""TD art drawn from the base game's own files in a staged build (docs/td-base-art.md).

A TD tile whose every frame is byte for byte a frame of a ZIP in TEXTURES_TD_SRGB.MEG moves into RA_VFX, which
staging re-roots at the texture root: its frames name the base game's (Tiberian_Dawn\\Units\\mtnk\\mtnk-0000.tga),
RA_VFX's own frames gain their old root, and an opener tile per ZIP folder makes the launcher open that ZIP. A TD
ZIP no frame names any more is left out of the build. The source tree is unchanged; stage_asset_packs.py calls
reroute() after share_tileset_zips.share().

Usage: td_base_art.py   (reports what staging would move and leave out; changes nothing)
License: GPL v3.
"""
import io
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs as A  # noqa: E402
from meg_extract import member_index  # noqa: E402
import steam_library  # noqa: E402

TD_MEG = str(steam_library.path("common/CnCRemastered/Data/TEXTURES_TD_SRGB.MEG"))
RA_MEG = str(steam_library.path("common/CnCRemastered/Data/TEXTURES_RA_SRGB.MEG"))
CATEGORY = {"UNITS": "Units", "STRUCTURES": "Structures", "VFX": "VFX"}
HOST = os.path.join("XML", "TILESETS", "RA_VFX.XML")
TILE = re.compile(r"[ \t]*<Tile>\s*<Key>\s*<Name>([^<]+)</Name>.*?</Tile>[ \t]*\r?\n", re.S)
FRAME = re.compile(r"<Frame>\s*([^<\s]+)\\([^\\<\s]+)\s*</Frame>")


def identities(z):
    """Lower-case .tga name -> (its name, identity key) for a ZIP: the .tga's and .meta's CRC and size."""
    info = {i.filename.lower(): i for i in z.infolist()}
    out = {}
    for low, i in info.items():
        if low.endswith(".tga"):
            meta = info.get(low[:-4] + ".meta")
            out[low] = (i.filename, (i.CRC, i.file_size, meta.CRC if meta else 0, meta.file_size if meta else 0))
    return out


def base_frames():
    """Identity key -> (folder, frame name) for every frame of TD's unit, building and effect ZIPs, where the
    folder is the ZIP's path from the texture root (Tiberian_Dawn\\Units\\mtnk)."""
    prefix = "DATA\\ART\\TEXTURES\\SRGB\\TIBERIAN_DAWN\\"
    out = {}
    index = member_index(TD_MEG)
    with open(TD_MEG, "rb") as f:
        for path in sorted(index):
            parts = path[len(prefix):].split("\\") if path.startswith(prefix) else []
            if len(parts) < 2 or parts[0] not in CATEGORY or not path.endswith(".ZIP"):
                continue
            size, data_off = index[path]
            f.seek(data_off)
            z = zipfile.ZipFile(io.BytesIO(f.read(size)))
            folder = "\\".join(["Tiberian_Dawn", CATEGORY[parts[0]]] + parts[1:-1] + [parts[-1][:-4].lower()])
            for _low, (name, key) in sorted(identities(z).items()):
                out.setdefault(key, (folder, name))
    return out


def opener(folder, frame):
    """A tile that only makes the launcher open the ZIP at `folder`; it is never drawn."""
    return ("\t\t\t<Tile>\n\t\t\t\t<Key>\n\t\t\t\t\t<Name>%s</Name>\n\t\t\t\t\t<Shape>0</Shape>\n\t\t\t\t</Key>\n"
            "\t\t\t\t<Value>\n\t\t\t\t\t<Frames>\n\t\t\t\t\t\t<Frame>%s\\%s</Frame>\n\t\t\t\t\t</Frames>\n"
            "\t\t\t\t</Value>\n\t\t\t</Tile>\n" % (folder.upper(), folder, frame))


def loose_folders():
    """Upper-case name -> path from the texture root for each loose frame folder the mod and its packs ship
    (the rally-point dots), outside the terrain tree."""
    out = {}
    for data in [os.path.join(A.MOD, "Data")] + [A.pack_data(p) for p in A.PACKS]:
        art = os.path.join(data, "ART", "TEXTURES", "SRGB", "RED_ALERT")
        for d, dirs, _files in os.walk(art):
            rel = os.path.relpath(d, art).split(os.sep)
            if rel[0].upper() not in CATEGORY:
                continue
            for name in dirs:
                parts = rel + [name]
                out[name.upper()] = "\\".join(["Red_Alert", CATEGORY[parts[0].upper()]] + parts[1:])
    return out


def mod_folder(stem, sources, ra_vfx, loose):
    """The path from the texture root of the ZIP or loose folder a frame folder names, and whether it is a ZIP:
    the mod's own, else RA's base VFX one."""
    if stem.upper() in loose and stem.upper() not in sources:
        return loose[stem.upper()], False
    if stem.upper() in sources:
        rel = sources[stem.upper()][0]
        parts = rel.split(os.sep)
        i = parts.index("RED_ALERT")
        return "\\".join(["Red_Alert", CATEGORY.get(parts[i + 1], parts[i + 1])] + parts[i + 2:-1] + [stem]), True
    if "DATA\\ART\\TEXTURES\\SRGB\\RED_ALERT\\VFX\\%s.ZIP" % stem.upper() in ra_vfx:
        return "Red_Alert\\VFX\\" + stem, True
    raise SystemExit("RA_VFX frame folder %s has no ZIP in the mod or under the base game's Red_Alert\\VFX" % stem)


def reroute(texts, sources):
    """The tileset texts with TD tiles drawn from the base game, and the Data-relative paths of the TD ZIPs no
    frame names any more."""
    base = base_frames()
    ids = {}

    def frame_id(stem, name):
        if stem not in ids:
            ids[stem] = {}
            if stem in sources:
                with zipfile.ZipFile(sources[stem][1]) as z:
                    ids[stem] = identities(z)
        hit = ids[stem].get(name.lower())
        return base.get(hit[1]) if hit else None

    tilesets = [rel for rel in texts if os.path.normpath(rel).upper().startswith(os.path.join("XML", "TILESETS"))
                and os.path.basename(rel).upper() in ("RA_UNITS.XML", "RA_STRUCTURES.XML", "RA_VFX.XML")]
    blocks = {}
    for rel in tilesets:
        for m in TILE.finditer(texts[rel]):
            blocks.setdefault(m.group(1).strip().upper(), []).append(m)
    movable = set()
    for name, ms in blocks.items():
        if not name.startswith("TD"):
            continue
        refs = [f for m in ms for f in FRAME.findall(m.group(0))]
        if refs and all(s.upper().startswith("TD") and frame_id(s.upper(), n) for s, n in refs):
            movable.add(name)

    def to_base(m):
        folder, name = frame_id(m.group(1).upper(), m.group(2))
        used_base.setdefault(folder, name)
        return "<Frame>%s\\%s</Frame>" % (folder, name)

    used_base = {}
    moved = []
    out = dict(texts)
    for rel in tilesets:
        kept = []
        last = 0
        for m in TILE.finditer(texts[rel]):
            if m.group(1).strip().upper() in movable:
                kept.append(texts[rel][last:m.start()])
                moved.append(FRAME.sub(to_base, m.group(0)))
                last = m.end()
        kept.append(texts[rel][last:])
        out[rel] = "".join(kept)

    ra_vfx = member_index(RA_MEG)
    loose = loose_folders()
    host = next(rel for rel in tilesets if os.path.basename(rel).upper() == "RA_VFX.XML")
    folders = {}

    def reroot(m):
        folder, is_zip = mod_folder(m.group(1), sources, ra_vfx, loose)
        if is_zip:
            folders.setdefault(folder, m.group(2))
        return "<Frame>%s\\%s</Frame>" % (folder, m.group(2))

    text = re.sub(r"<RootTexturePath>[^<]*</RootTexturePath>", "<RootTexturePath></RootTexturePath>", out[host], 1)
    text = FRAME.sub(reroot, text)
    openers = "".join(opener(f, n) for f, n in sorted(folders.items()) + sorted(used_base.items()))
    at = text.index("<Tiles>") + len("<Tiles>\n")
    end = text.rindex("</Tiles>")
    end = text.rindex("\n", 0, end) + 1
    out[host] = text[:at] + openers + text[at:end] + "".join(moved) + text[end:]

    before, after = named_zips(texts, tilesets), named_zips(out, tilesets)
    dropped = sorted(sources[s][0] for s in before - after if s.startswith("TD") and s in sources)
    return out, dropped, sorted(movable)


def named_zips(texts, tilesets):
    """Upper-case stems of the ZIP folders the tilesets' frames name."""
    out = set()
    for rel in tilesets:
        for m in re.finditer(r"<Frame>\s*([^<\s]+)\\[^\\<\s]+\s*</Frame>", texts[rel]):
            out.add(m.group(1).split("\\")[-1].upper())
    return out


if __name__ == "__main__":
    import share_tileset_zips  # noqa: E402
    import stage_asset_packs  # noqa: E402
    texts = {rel: stage_asset_packs.merged(rel, pf, root) for rel, pf, root, _ in A.XML_FILES}
    sources = share_tileset_zips.zip_sources()
    texts, shared = share_tileset_zips.share(texts, sources)
    _, dropped, moved = reroute(texts, sources)
    size = sum(os.path.getsize(sources[os.path.splitext(os.path.basename(r))[0]][1]) for r in dropped)
    print("%d TD tiles from the base game; %d ZIPs, %.1f MB, left out" % (len(moved), len(dropped), size / 2**20))
    for r in dropped:
        print("left out:", r)
