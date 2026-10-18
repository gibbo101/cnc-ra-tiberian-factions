"""Probe: TD's Sand Trap and Hastings in RA's Official skirmish list, launched through the carrier.

usage: td_official_list_probe.py <deployed Vanilla_RA folder>
Writes the deployed build's INSTANCES.XML (from the repo's) and CNCMAPPREVIEWDATA.XML (from the
base game's), the two list thumbnails and CCDATA/TFTD902.INI. The DLL's carrier (tf_launcher.cpp,
dev builds) sends entry 9NN to the server as Hastings' D6 entry, whose client entry is hidden here.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from meg_extract import read_member  # noqa: E402

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
GAME = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data")
SAND_TRAP = os.path.join(REPO, "parked/td-maps/CustomMaps/UGC_F1BE000000000013_0000000000000013_MAPDATA")
CARRIER = "Mobius_Red_Alert_Multiplayer_D6_Map"


def instance(text, name):
    m = re.search(r'<Instance Name="%s" Variant="[^"]+">(.*?)</Instance>' % re.escape(name), text, re.S)
    return m


def preview(text, name):
    return re.search(r'(\s*<INIData Name="%s">.*?</INIData>)' % re.escape(name.upper()), text, re.S).group(1)


def main(mod):
    data = os.path.join(mod, "Data")
    inst = open(os.path.join(REPO, "resources/remaster_mods/Vanilla_RA/Data/XML/INSTANCES.XML"),
                encoding="utf-8", newline="").read()
    td = instance(read_member(os.path.join(GAME, "CONFIG.MEG"), "DATA\\XML\\INSTANCES.XML").decode("utf-8"),
                  "Mobius_Tiberian_Dawn_Multiplayer_2_Map").group(1)
    d6 = instance(inst, CARRIER).group(1)
    sand = td.replace("<Mission>2</Mission>", "<Mission>902</Mission>").replace("MUS_TD_", "MUS_RA_")
    hastings = re.sub(r"\s*<OverrideMapName>[^<]*</OverrideMapName>", "", d6).replace("<Mission>0</Mission>",
                                                                                     "<Mission>990</Mission>")
    entries = "".join('\t<Instance Name="Mobius_Red_Alert_Multiplayer_%d_Map" Variant="Mobius_Red_Alert_Multiplayer_Base">'
                      "%s</Instance>\n" % (n, body) for n, body in ((902, sand), (990, hastings)))
    inst = inst.replace('<Instance Name="%s"' % CARRIER, '<Instance Name="TF_Skirmish_Carrier_D6"', 1)
    at = inst.index('\t<Instance Name="Mobius_Red_Alert_Multiplayer_2_Map"')
    inst = inst[:at] + entries + inst[at:]
    open(os.path.join(data, "XML/INSTANCES.XML"), "w", encoding="utf-8", newline="").write(inst)

    pv = read_member(os.path.join(GAME, "CONFIG.MEG"), "DATA\\XML\\CNCMAPPREVIEWDATA.XML").decode("latin-1")
    sj = json.load(open(SAND_TRAP + ".JSON"))
    starts = "".join("\n\t\t\t\t\t<Entry>%d</Entry>" % w for w in sj["Waypoints"][:4])
    sand_pv = ('\n\t\t\t<INIData Name="MOBIUS_RED_ALERT_MULTIPLAYER_902_MAP">\n\t\t\t\t<MapTileX>%d</MapTileX>\n'
               "\t\t\t\t<MapTileY>%d</MapTileY>\n\t\t\t\t<MapTileWidth>%d</MapTileWidth>\n"
               "\t\t\t\t<MapTileHeight>%d</MapTileHeight>\n\t\t\t\t<Theater>DESERT</Theater>\n"
               "\t\t\t\t<Waypoints>%s\n\t\t\t\t</Waypoints>\n\t\t\t</INIData>"
               % (sj["MapTileX"], sj["MapTileY"], sj["MapTileWidth"], sj["MapTileHeight"], starts))
    hastings_pv = preview(pv, CARRIER).replace(CARRIER.upper(), "MOBIUS_RED_ALERT_MULTIPLAYER_990_MAP")
    pv = pv.replace("</CNCMapPreviewData>", sand_pv + hastings_pv + "\n\t\t</CNCMapPreviewData>", 1)
    open(os.path.join(data, "XML/CNCMAPPREVIEWDATA.XML"), "w", encoding="latin-1", newline="").write(pv)

    srgb = os.path.join(data, "ART/TEXTURES/SRGB")
    open(os.path.join(srgb, "MOBIUS_RED_ALERT_MULTIPLAYER_902_MAP.DDS"), "wb").write(read_member(
        os.path.join(GAME, "TEXTURES_SRGB.MEG"), "DATA\\ART\\TEXTURES\\SRGB\\MOBIUS_TIBERIAN_DAWN_MULTIPLAYER_2_MAP.DDS"))
    open(os.path.join(srgb, "MOBIUS_RED_ALERT_MULTIPLAYER_990_MAP.DDS"), "wb").write(
        open(os.path.join(srgb, CARRIER.upper() + ".DDS"), "rb").read())

    ini = open(SAND_TRAP + ".MPR", encoding="latin-1", newline="").read()
    ini = re.sub(r"^Theater=Interior", "Theater=Desert", ini, count=1, flags=re.M)
    open(os.path.join(mod, "CCDATA/TFTD902.INI"), "w", encoding="latin-1", newline="").write(ini)
    print("entries 902 (Sand Trap) and 990 (Hastings); carrier client entry hidden")


if __name__ == "__main__":
    main(sys.argv[1])
