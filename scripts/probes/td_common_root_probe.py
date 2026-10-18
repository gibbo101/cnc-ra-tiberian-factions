"""Probe run 3 on a deployed build: tiles found across tilesets, tile names with a path, and
Common_UI re-rooted at Tiberian_Dawn so its tiles open the base game's TD ZIPs.

usage: td_common_root_probe.py <deployed Data> <backup dir holding the original XML and ZIPs>
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from meg_extract import read_member  # noqa: E402
from td_base_ref_probe import base_frames, load, save  # noqa: E402

CONFIG = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data/CONFIG.MEG")
COMMON = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_COMMON_SRGB.MEG")


def tiles(text, name):
    return re.findall(r"\t\t\t<Tile>\s*<Key>\s*<Name>%s</Name>.*?</Tile>\n" % re.escape(name), text, re.S)


def opener(name, frame):
    return ("\t\t\t<Tile>\n\t\t\t\t<Key>\n\t\t\t\t\t<Name>%s</Name>\n\t\t\t\t\t<Shape>0</Shape>\n\t\t\t\t</Key>\n"
            "\t\t\t\t<Value>\n\t\t\t\t\t<Frames>\n\t\t\t\t\t\t<Frame>%s</Frame>\n\t\t\t\t\t</Frames>\n"
            "\t\t\t\t</Value>\n\t\t\t</Tile>\n" % (name, frame))


def repoint(blocks, stem, prefix, rename):
    out = "".join(blocks)
    return re.sub(r"<Frame>%s\\([^<]+)</Frame>" % re.escape(stem),
                  lambda m: "<Frame>%s%s</Frame>" % (prefix, rename[m.group(1).lower()]), out, flags=re.I)


def main(data, backup):
    art = os.path.join(data, "ART/TEXTURES/SRGB/RED_ALERT")
    units = load(os.path.join(backup, "RA_UNITS.XML"))
    structures = load(os.path.join(backup, "RA_STRUCTURES.XML"))

    # Hum-vee: its tiles and ZIP move to RA_Structures.
    jeep = tiles(units, "TDJEEP")
    for b in jeep:
        units = units.replace(b, "")
    structures = re.sub(r"^(\s*)</Tiles>", lambda m: "".join(jeep) + m.group(0), structures, count=1, flags=re.M)
    shutil.move(os.path.join(art, "UNITS/TDJEEP.ZIP"), os.path.join(art, "STRUCTURES/TDJEEP.ZIP"))

    # APC: its ZIP moves to UNITS/SUB, opened by a tile named SUB\TDAPC.
    apc = tiles(units, "TDAPC")
    first = re.search(r"<Frame>tdapc\\([^<]+)</Frame>", apc[0]).group(1)
    for b in apc:
        units = units.replace(b, re.sub(r"<Frame>tdapc\\", r"<Frame>sub\\tdapc\\", b))
    units = units.replace("\t\t<Tiles>\n", "\t\t<Tiles>\n" + opener("SUB\\TDAPC", "sub\\tdapc\\" + first), 1)
    os.makedirs(os.path.join(art, "UNITS/SUB"), exist_ok=True)
    shutil.move(os.path.join(art, "UNITS/TDAPC.ZIP"), os.path.join(art, "UNITS/SUB/TDAPC.ZIP"))

    # Medium tank and MCVs: tiles move to Common_UI, rooted at Tiberian_Dawn, reading base TD ZIPs.
    common = load_member("DATA\\XML\\TILESETS\\COMMON_UI.XML")
    common = common.replace("<RootTexturePath>Common\\UI</RootTexturePath>", "<RootTexturePath>Tiberian_Dawn</RootTexturePath>")
    ui_frames = sorted(set(re.findall(r"<Frame>([^<]+)</Frame>", common)))
    added = ""
    for stem, base, names in (("tdmtnk", "mtnk", ["TDMTNK"]), ("tdgmcv", "mcv", ["TDMCV", "TDGMCV", "TDNMCV"])):
        rename = base_frames(backup_data(backup), stem, "Units", base)
        added += opener("Units\\%s" % base.upper(), "Units\\%s\\%s" % (base, sorted(rename.values())[0]))
        for n in names:
            blocks = tiles(units, n)
            for b in blocks:
                units = units.replace(b, "")
            added += repoint(blocks, stem, "Units\\%s\\" % base, rename)
    common = re.sub(r"^(\s*)</Tiles>", lambda m: added + m.group(0), common, count=1, flags=re.M)

    save(os.path.join(data, "XML/TILESETS/RA_UNITS.XML"), units)
    save(os.path.join(data, "XML/TILESETS/RA_STRUCTURES.XML"), structures)
    save(os.path.join(data, "XML/TILESETS/COMMON_UI.XML"), common)
    for f in ui_frames:
        dest = os.path.join(data, "ART/TEXTURES/SRGB/TIBERIAN_DAWN", f.replace("\\", "/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").write(read_member(COMMON, "DATA\\ART\\TEXTURES\\SRGB\\COMMON\\UI\\" + f.replace("/", "\\")))
    print("jeep", len(jeep), "apc", len(apc), "ui frames", len(ui_frames), "common tiles", common.count("<Tile>"))


def load_member(name):
    return read_member(CONFIG, name).decode("latin-1")


def backup_data(backup):
    """A Data-shaped view of the backup's ZIPs for base_frames."""
    root = os.path.join(backup, "_data")
    for z in ("TDMTNK.ZIP", "TDGMCV.ZIP"):
        dest = os.path.join(root, "ART/TEXTURES/SRGB/RED_ALERT/UNITS", z)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if not os.path.exists(dest):
            shutil.copy(os.path.join(backup, z), dest)
    return root


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
