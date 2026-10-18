"""Probe run 4 on a deployed build: Common_UI and RA_RadarMap re-rooted at Tiberian_Dawn, each
holding one unit read from the base game's TD ZIP and one read from our own ZIP copied under it.

usage: td_gateway_probe.py <deployed Data> <backup dir holding the original XML and ZIPs>
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from meg_extract import read_member  # noqa: E402
from td_base_ref_probe import base_frames, load, save  # noqa: E402
from td_common_root_probe import CONFIG, opener, repoint, tiles  # noqa: E402

SRGB_MEGS = [os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data/%s.MEG" % m)
             for m in ("TEXTURES_COMMON_SRGB", "TEXTURES_RA_SRGB", "TEXTURES_SRGB")]


def texture(path):
    for meg in SRGB_MEGS:
        try:
            return read_member(meg, path)
        except KeyError:
            pass
    raise KeyError(path)


def gateway(data, member, old_root, units, groups):
    """Re-root <member> at Tiberian_Dawn, copy its own frames under it, move each group's tiles in."""
    text = read_member(CONFIG, "DATA\\XML\\TILESETS\\%s.XML" % member).decode("latin-1")
    text = text.replace("<RootTexturePath>%s</RootTexturePath>" % old_root, "<RootTexturePath>Tiberian_Dawn</RootTexturePath>")
    for f in sorted(set(re.findall(r"<Frame>([^<]+)</Frame>", text))):
        dest = os.path.join(data, "ART/TEXTURES/SRGB/TIBERIAN_DAWN", f.replace("\\", "/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").write(texture("DATA\\ART\\TEXTURES\\SRGB\\%s\\%s" % (old_root.upper(), f.replace("/", "\\"))))
    added = ""
    for stem, zip_stem, rename, names in groups:
        added += opener("Units\\%s" % zip_stem.upper(), "Units\\%s\\%s" % (zip_stem, sorted(rename.values())[0]))
        for n in names:
            blocks = tiles(units, n)
            assert blocks, n
            for b in blocks:
                units = units.replace(b, "")
            added += repoint(blocks, stem, "Units\\%s\\" % zip_stem, rename)
    text = re.sub(r"^(\s*)</Tiles>", lambda m: added + m.group(0), text, count=1, flags=re.M)
    save(os.path.join(data, "XML/TILESETS/%s.XML" % member), text)
    print(member, "tiles", text.count("<Tile>"))
    return units


def own_copy(data, backup, stem):
    """Our ZIP copied under Tiberian_Dawn\\Units, frames keeping their own names."""
    dest = os.path.join(data, "ART/TEXTURES/SRGB/TIBERIAN_DAWN/UNITS/%s.ZIP" % stem.upper())
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy(os.path.join(backup, "%s.ZIP" % stem.upper()), dest)
    import zipfile
    return {n.lower(): n for n in zipfile.ZipFile(dest).namelist() if n.lower().endswith(".tga")}


def view(backup):
    root = os.path.join(backup, "_data")
    for z in os.listdir(backup):
        if z.upper().endswith(".ZIP"):
            dest = os.path.join(root, "ART/TEXTURES/SRGB/RED_ALERT/UNITS", z)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if not os.path.exists(dest):
                shutil.copy(os.path.join(backup, z), dest)
    return root


def main(data, backup):
    units = load(os.path.join(backup, "RA_UNITS.XML"))
    v = view(backup)
    units = gateway(data, "COMMON_UI", "Common\\UI", units, [
        ("tdmtnk", "tdmtnk", own_copy(data, backup, "tdmtnk"), ["TDMTNK"]),
        ("tdjeep", "jeep", base_frames(v, "tdjeep", "Units", "jeep"), ["TDJEEP"]),
    ])
    units = gateway(data, "RA_RADARMAP", "Red_Alert\\RadarMap", units, [
        ("tdmlrs", "tdmlrs", own_copy(data, backup, "tdmlrs"), ["TDMLRS"]),
        ("tdgmcv", "mcv", base_frames(v, "tdgmcv", "Units", "mcv"), ["TDMCV", "TDGMCV", "TDNMCV"]),
    ])
    save(os.path.join(data, "XML/TILESETS/RA_UNITS.XML"), units)
    for z in ("TDJEEP", "TDMLRS"):
        os.remove(os.path.join(data, "ART/TEXTURES/SRGB/RED_ALERT/UNITS/%s.ZIP" % z))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
