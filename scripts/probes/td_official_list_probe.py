"""Probe: TD's Sand Trap and Hastings in RA's Official skirmish list, launched through the carrier.

usage: td_official_list_probe.py <deployed Vanilla_RA folder> [--thumb-field]
--thumb-field: entry 902 names TD's own thumbnail in PreviewLoadingTextureName instead of a copied one.
Writes the deployed build's INSTANCES.XML (from the repo's) and CNCMAPPREVIEWDATA.XML (from the
base game's), the two list thumbnails and CCDATA/TFTD902.INI. The DLL's carrier (tf_launcher.cpp,
dev builds) sends entry 9NN to the server as Hastings' D6 entry, whose client entry is removed here.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import td_map_to_ra  # noqa: E402
from meg_extract import read_member  # noqa: E402

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
GAME = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data")
TD_GENERAL = os.path.join(GAME, "CNCDATA/TIBERIAN_DAWN/CD1/GENERAL.MIX")
CARRIER = "Mobius_Red_Alert_Multiplayer_D6_Map"


def instance(text, name):
    m = re.search(r'<Instance Name="%s" Variant="[^"]+">(.*?)</Instance>' % re.escape(name), text, re.S)
    return m


def preview(text, name):
    return re.search(r'(\s*<INIData Name="%s">.*?</INIData>)' % re.escape(name.upper()), text, re.S).group(1)


def sand_trap(work):
    """Sand Trap (TD's scm02ea) converted from TD's own files: the .mpr path, without its extension."""
    for ext in (".ini", ".bin"):
        subprocess.run([sys.executable, os.path.join(REPO, "scripts/mix_tools.py"), "extract", TD_GENERAL,
                        "scm02ea" + ext, work], check=True, stdout=subprocess.DEVNULL)
    td_map_to_ra.convert(os.path.join(work, "scm02ea.ini"), os.path.join(work, "sand_trap.mpr"), "Sand Trap")
    return os.path.join(work, "sand_trap")


def main(mod, thumb_field=False):
    sand_map = sand_trap(tempfile.mkdtemp())
    data = os.path.join(mod, "Data")
    inst = open(os.path.join(REPO, "resources/remaster_mods/Vanilla_RA/Data/XML/INSTANCES.XML"),
                encoding="utf-8", newline="").read()
    td = instance(read_member(os.path.join(GAME, "CONFIG.MEG"), "DATA\\XML\\INSTANCES.XML").decode("utf-8"),
                  "Mobius_Tiberian_Dawn_Multiplayer_2_Map").group(1)
    d6 = instance(inst, CARRIER).group(1)
    sand = td.replace("<Mission>2</Mission>", "<Mission>902</Mission>").replace("MUS_TD_", "MUS_RA_")
    if thumb_field:
        sand += "\t<PreviewLoadingTextureName>MOBIUS_TIBERIAN_DAWN_MULTIPLAYER_2_MAP.DDS</PreviewLoadingTextureName>\n\t"
    hastings = re.sub(r"\s*<OverrideMapName>[^<]*</OverrideMapName>", "", d6).replace("<Mission>0</Mission>",
                                                                                     "<Mission>999</Mission>")
    entries = "".join('\t<Instance Name="Mobius_Red_Alert_Multiplayer_%d_Map" Variant="Mobius_Red_Alert_Multiplayer_Base">'
                      "%s</Instance>\n" % (n, body) for n, body in ((902, sand), (999, hastings)))
    carrier = instance(inst, CARRIER)
    inst = inst[:carrier.start()] + inst[carrier.end():].lstrip("\r\n")
    at = inst.index('\t<Instance Name="Mobius_Red_Alert_Multiplayer_2_Map"')
    inst = inst[:at] + entries + inst[at:]
    open(os.path.join(data, "XML/INSTANCES.XML"), "w", encoding="utf-8", newline="").write(inst)

    pv = read_member(os.path.join(GAME, "CONFIG.MEG"), "DATA\\XML\\CNCMAPPREVIEWDATA.XML").decode("latin-1")
    sj = json.load(open(sand_map + ".json"))
    starts = "".join("\n\t\t\t\t\t<Entry>%d</Entry>" % w for w in sj["Waypoints"][:4])
    sand_pv = ('\n\t\t\t<INIData Name="MOBIUS_RED_ALERT_MULTIPLAYER_902_MAP">\n\t\t\t\t<MapTileX>%d</MapTileX>\n'
               "\t\t\t\t<MapTileY>%d</MapTileY>\n\t\t\t\t<MapTileWidth>%d</MapTileWidth>\n"
               "\t\t\t\t<MapTileHeight>%d</MapTileHeight>\n\t\t\t\t<Theater>DESERT</Theater>\n"
               "\t\t\t\t<Waypoints>%s\n\t\t\t\t</Waypoints>\n\t\t\t</INIData>"
               % (sj["MapTileX"], sj["MapTileY"], sj["MapTileWidth"], sj["MapTileHeight"], starts))
    hastings_pv = preview(pv, CARRIER).replace(CARRIER.upper(), "MOBIUS_RED_ALERT_MULTIPLAYER_999_MAP")
    pv = pv.replace("</CNCMapPreviewData>", sand_pv + hastings_pv + "\n\t\t</CNCMapPreviewData>", 1)
    open(os.path.join(data, "XML/CNCMAPPREVIEWDATA.XML"), "w", encoding="latin-1", newline="").write(pv)

    srgb = os.path.join(data, "ART/TEXTURES/SRGB")
    thumb = os.path.join(srgb, "MOBIUS_RED_ALERT_MULTIPLAYER_902_MAP.DDS")
    if thumb_field:
        if os.path.exists(thumb):
            os.remove(thumb)
    else:
        open(thumb, "wb").write(read_member(os.path.join(GAME, "TEXTURES_SRGB.MEG"),
                                            "DATA\\ART\\TEXTURES\\SRGB\\MOBIUS_TIBERIAN_DAWN_MULTIPLAYER_2_MAP.DDS"))
    open(os.path.join(srgb, "MOBIUS_RED_ALERT_MULTIPLAYER_999_MAP.DDS"), "wb").write(
        open(os.path.join(srgb, CARRIER.upper() + ".DDS"), "rb").read())

    ini = open(sand_map + ".mpr", encoding="latin-1", newline="").read()
    open(os.path.join(mod, "CCDATA/TFTD902.INI"), "w", encoding="latin-1", newline="").write(ini)
    print("entries 902 (Sand Trap) and 999 (Hastings); carrier client entry removed")


if __name__ == "__main__":
    main(sys.argv[1], "--thumb-field" in sys.argv)
