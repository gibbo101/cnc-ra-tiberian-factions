"""Probe run 5 on a deployed build: RA_VFX re-rooted at the SRGB root (empty RootTexturePath), so
one world tileset reaches both Red_Alert\\ and Tiberian_Dawn\\; the APC moves into Common_UI.

usage: td_empty_root_probe.py <deployed Data> <backup dir holding the original XML and ZIPs>
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
from td_gateway_probe import view  # noqa: E402


def reroot_empty(text, old_root):
    """Prefix every frame with the old root and add an opener for each ZIP folder it named."""
    text = text.replace("<RootTexturePath>%s</RootTexturePath>" % old_root, "<RootTexturePath></RootTexturePath>")
    dirs = {}

    def sub(m):
        dirs.setdefault(m.group(1).split("\\")[0].upper(), m.group(1))
        return "<Frame>%s\\%s</Frame>" % (old_root, m.group(1))

    text = re.sub(r"<Frame>([^<]+)</Frame>", sub, text)
    openers = "".join(opener("%s\\%s" % (old_root, d), "%s\\%s" % (old_root, f)) for d, f in sorted(dirs.items()))
    return text.replace("\t\t<Tiles>\n", "\t\t<Tiles>\n" + openers, 1), len(dirs)


def main(data, backup):
    units = load(os.path.join(backup, "RA_UNITS.XML"))
    v = view(backup)

    # APC into Common_UI at its own root, its ZIP copied under Common\UI.
    common = read_member(CONFIG, "DATA\\XML\\TILESETS\\COMMON_UI.XML").decode("latin-1")
    apc = tiles(units, "TDAPC")
    for b in apc:
        units = units.replace(b, "")
    first = re.search(r"<Frame>tdapc\\([^<]+)</Frame>", apc[0]).group(1)
    common = re.sub(r"^(\s*)</Tiles>", lambda m: opener("TDAPC", "tdapc\\" + first) + "".join(apc) + m.group(0),
                    common, count=1, flags=re.M)
    dest = os.path.join(data, "ART/TEXTURES/SRGB/COMMON/UI/TDAPC.ZIP")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy(os.path.join(backup, "TDAPC.ZIP"), dest)
    save(os.path.join(data, "XML/TILESETS/COMMON_UI.XML"), common)

    # RA_VFX at the empty root, holding the Hum-vee (our ZIP) and the medium tank and MCVs (base TD ZIPs).
    vfx, n = reroot_empty(load(os.path.join(backup, "RA_VFX.XML")), "Red_Alert\\VFX")
    added = ""
    for stem, prefix, zip_name, rename, names in (
            ("tdjeep", "Red_Alert\\Units\\tdjeep\\", "Red_Alert\\Units\\TDJEEP",
             {k: k for k in base_frames(v, "tdjeep", "Units", "jeep")}, ["TDJEEP"]),
            ("tdmtnk", "Tiberian_Dawn\\Units\\mtnk\\", "Tiberian_Dawn\\Units\\MTNK",
             base_frames(v, "tdmtnk", "Units", "mtnk"), ["TDMTNK"]),
            ("tdgmcv", "Tiberian_Dawn\\Units\\mcv\\", "Tiberian_Dawn\\Units\\MCV",
             base_frames(v, "tdgmcv", "Units", "mcv"), ["TDMCV", "TDGMCV", "TDNMCV"])):
        added += opener(zip_name, prefix + sorted(rename.values())[0])
        for name in names:
            blocks = tiles(units, name)
            assert blocks, name
            for b in blocks:
                units = units.replace(b, "")
            added += repoint(blocks, stem, prefix, rename)
    vfx = re.sub(r"^(\s*)</Tiles>", lambda m: added + m.group(0), vfx, count=1, flags=re.M)
    save(os.path.join(data, "XML/TILESETS/RA_VFX.XML"), vfx)
    save(os.path.join(data, "XML/TILESETS/RA_UNITS.XML"), units)
    for z in ("TDMTNK", "TDGMCV"):
        path = os.path.join(data, "ART/TEXTURES/SRGB/RED_ALERT/UNITS/%s.ZIP" % z)
        if os.path.exists(path):
            os.remove(path)
    print("vfx zip folders", n, "apc tiles", len(apc), "vfx tiles", vfx.count("<Tile>"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
