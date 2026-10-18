"""Repoint a deployed build's TD tiles at the base game's TEXTURES_TD_SRGB.MEG art.

usage:
  td_base_ref_probe.py base <Data> <xml> <stem> <TD category> <base stem> <frame prefix> [opener tile]
      frames <stem>\\X.tga become <frame prefix>Y.tga, Y being the base frame with X's bytes;
      an opener tile name adds a one-frame tile of that name, so the launcher opens <root>\\<name>.zip
  td_base_ref_probe.py fixed <Data> <xml> <tile> <frame>
      every frame of <tile> becomes <frame>
"""
import hashlib
import io
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from meg_extract import read_member  # noqa: E402

MEG = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_TD_SRGB.MEG")


def load(path):
    return open(path, encoding="latin-1", newline="").read()


def save(path, text):
    open(path, "w", encoding="latin-1", newline="").write(text)


def base_frames(data, stem, category, base_stem):
    ours = zipfile.ZipFile(os.path.join(data, "ART/TEXTURES/SRGB/RED_ALERT", category.upper(), stem.upper() + ".ZIP"))
    base = zipfile.ZipFile(io.BytesIO(read_member(
        MEG, "DATA\\ART\\TEXTURES\\SRGB\\TIBERIAN_DAWN\\%s\\%s.ZIP" % (category.upper(), base_stem.upper()))))
    by_md5 = {hashlib.md5(base.read(n)).hexdigest(): n for n in base.namelist() if n.lower().endswith(".tga")}
    return {n.lower(): by_md5[hashlib.md5(ours.read(n)).hexdigest()]
            for n in ours.namelist() if n.lower().endswith(".tga")}


def cmd_base(data, xml, stem, category, base_stem, prefix, opener=None):
    rename = base_frames(data, stem, category, base_stem)
    path = os.path.join(data, "XML/TILESETS", xml)
    text, n = re.subn(r"<Frame>%s\\([^<]+)</Frame>" % re.escape(stem),
                      lambda m: "<Frame>%s%s</Frame>" % (prefix, rename[m.group(1).lower()]), load(path), flags=re.I)
    if opener:
        first = "%s%s" % (prefix, sorted(rename.values())[0])
        tile = ("\t\t\t<Tile>\n\t\t\t\t<Key>\n\t\t\t\t\t<Name>%s</Name>\n\t\t\t\t\t<Shape>0</Shape>\n\t\t\t\t</Key>\n"
                "\t\t\t\t<Value>\n\t\t\t\t\t<Frames>\n\t\t\t\t\t\t<Frame>%s</Frame>\n\t\t\t\t\t</Frames>\n"
                "\t\t\t\t</Value>\n\t\t\t</Tile>\n" % (opener, first))
        text = text.replace("\t\t<Tiles>\n", "\t\t<Tiles>\n" + tile, 1)
    save(path, text)
    print(xml, stem, "->", prefix, n, "frames", "opener " + opener if opener else "")


def cmd_fixed(data, xml, tile, frame):
    path = os.path.join(data, "XML/TILESETS", xml)
    text = load(path)
    blocks = re.compile(r"<Tile>\s*<Key>\s*<Name>%s</Name>.*?</Tile>" % re.escape(tile), re.S)
    count = [0]

    def sub(m):
        count[0] += 1
        return re.sub(r"<Frame>[^<]*</Frame>", "<Frame>%s</Frame>" % frame.replace("\\", "\\\\"), m.group(0))

    save(path, blocks.sub(sub, text))
    print(xml, tile, "->", frame, count[0], "tiles")


if __name__ == "__main__":
    {"base": cmd_base, "fixed": cmd_fixed}[sys.argv[1]](*sys.argv[2:])
