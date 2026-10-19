#!/usr/bin/env python3
"""TD's skirmish maps in RA's Official list (docs/td-base-art.md).

usage: td_official_maps.py
Writes into resources/remaster_mods/Vanilla_RA/, from TD's own instances, preview data and map files:
  - Data/XML/INSTANCES.XML: an entry Mobius_Red_Alert_Multiplayer_<n>_Map per TD map (TD's multiplayer map
    m is 9mm, community map k is 979+k) and Hastings' own entry 999, between TF_TD_MAPS markers; Hastings'
    D6 entry, the carrier, is removed so the lobby doesn't list it twice;
  - Data/XML/CNCMAPPREVIEWDATA.XML: the base game's, with each entry's bounds, climate and starts on RA's grid;
  - CCDATA/TFTD<n>.INI: each map converted by td_map_to_ra.py, played in its TD theatre.
The DLL's carrier (tf_launcher.cpp) launches an entry from 900 up and hands its map file over.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import td_map_to_ra  # noqa: E402
from meg_extract import read_member  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "resources/remaster_mods/Vanilla_RA")
GAME = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data")
TD_DATA = os.path.join(GAME, "CNCDATA/TIBERIAN_DAWN")
CONFIG = os.path.join(GAME, "CONFIG.MEG")
CARRIER = "Mobius_Red_Alert_Multiplayer_D6_Map"
HASTINGS = 999
BEGIN, END = "\t<!-- TF_TD_MAPS BEGIN -->\n", "\t<!-- TF_TD_MAPS END -->\n"
PREVIEW_BEGIN, PREVIEW_END = "\t\t\t<!-- TF_TD_MAPS BEGIN -->\n", "\t\t\t<!-- TF_TD_MAPS END -->\n"


def instances(text):
    pattern = r'\t*<Instance Name="([^"]+)" Variant="[^"]+"[^>]*>(.*?)</Instance>(?:\r?\n)?'
    return {m.group(1): m for m in re.finditer(pattern, text, re.S)}


def td_maps(td_instances):
    """(RA entry number, TD instance name, source map stem, MIX or folder) for each of TD's skirmish maps."""
    out = []
    for name in td_instances:
        m = re.fullmatch(r"Mobius_Tiberian_Dawn_Multiplayer_(\d+)_Map", name)
        if m:
            out.append((900 + int(m.group(1)), name, "scm%02dea" % int(m.group(1)), None))
        m = re.fullmatch(r"Mobius_Tiberian_Dawn_Multiplayer_Community_(\d)_Map", name)
        if m:
            out.append((979 + int(m.group(1)), name, "SCMC%dEA" % (int(m.group(1)) - 1), "COMMUNITY"))
    return sorted(out)


def fetch(stem, folder, work):
    """Copies a TD map's .ini and .bin into work; returns the .ini path."""
    for ext in (".ini", ".bin"):
        if folder:
            src = os.path.join(TD_DATA, folder, stem + ext.upper())
            with open(src, "rb") as f, open(os.path.join(work, stem + ext), "wb") as g:
                g.write(f.read())
            continue
        for mix in ("GENERAL.MIX", "SC-001.MIX"):
            r = subprocess.run([sys.executable, os.path.join(REPO, "scripts/mix_tools.py"), "extract",
                                os.path.join(TD_DATA, "CD1", mix), stem + ext, work],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if r.returncode == 0 and os.path.exists(os.path.join(work, stem + ext)):
                break
        else:
            raise SystemExit("%s%s not found in TD's MIX files" % (stem, ext))
    return os.path.join(work, stem + ".ini")


def entry(number, td_body):
    """An RA list entry from TD's: its text, players, size and ambience, with RA's music."""
    body = re.sub(r"<Mission>\d+</Mission>", "<Mission>%d</Mission>" % number, td_body)
    body = re.sub(r"\s*<OverrideMapName>[^<]*</OverrideMapName>", "", body).replace("MUS_TD_", "MUS_RA_")
    return ('\t<Instance Name="Mobius_Red_Alert_Multiplayer_%d_Map" Variant="Mobius_Red_Alert_Multiplayer_Base">'
            "%s</Instance>\n" % (number, body))


def preview(number, manifest, players):
    starts = "".join("\n\t\t\t\t\t<Entry>%d</Entry>" % w for w in manifest["Waypoints"][:players])
    return ('\t\t\t<INIData Name="MOBIUS_RED_ALERT_MULTIPLAYER_%d_MAP">\n\t\t\t\t<MapTileX>%d</MapTileX>\n'
            "\t\t\t\t<MapTileY>%d</MapTileY>\n\t\t\t\t<MapTileWidth>%d</MapTileWidth>\n"
            "\t\t\t\t<MapTileHeight>%d</MapTileHeight>\n\t\t\t\t<Theater>%s</Theater>\n"
            "\t\t\t\t<Waypoints>%s\n\t\t\t\t</Waypoints>\n\t\t\t</INIData>\n"
            % (number, manifest["MapTileX"], manifest["MapTileY"], manifest["MapTileWidth"],
               manifest["MapTileHeight"], manifest["Theater"], starts))


def splice(text, block, begin, end, anchor):
    """Replaces the marked block, or inserts it before anchor on the first run, in the text's own line
    endings: the launcher's XML reader crashes on a CRLF file's LF-only lines."""
    nl = "\r\n" if "\r\n" in text else "\n"
    block, begin, end = (x.replace("\r\n", "\n").replace("\n", nl) for x in (block, begin, end))
    if begin in text:
        a = text.index(begin)
        b = text.index(end, a) + len(end)
        return text[:a] + begin + block + end + text[b:]
    at = text.index(anchor)
    return text[:at] + begin + block + end + text[at:]


def main():
    base = read_member(CONFIG, "DATA\\XML\\INSTANCES.XML").decode("utf-8")
    base_instances = instances(base)
    path = os.path.join(MOD, "Data/XML/INSTANCES.XML")
    with open(path, encoding="utf-8", newline="") as f:
        inst = f.read()
    mod_instances = instances(inst)
    hastings = None
    if CARRIER in mod_instances:
        m = mod_instances[CARRIER]
        hastings = m.group(2)
        inst = inst[:m.start()] + inst[m.end():]
    elif BEGIN.strip() in inst:
        hastings = instances(inst)["Mobius_Red_Alert_Multiplayer_%d_Map" % HASTINGS].group(2)
    hastings = re.sub(r"\s*<OverrideMapName>[^<]*</OverrideMapName>", "", hastings)
    hastings = hastings.replace("<Mission>0</Mission>", "<Mission>%d</Mission>" % HASTINGS)

    pv_base = read_member(CONFIG, "DATA\\XML\\CNCMAPPREVIEWDATA.XML").decode("latin-1")
    d6_preview = re.search(r'\t*<INIData Name="%s">.*?</INIData>\r?\n' % CARRIER.upper(), pv_base, re.S).group(0)
    previews = [d6_preview.replace(CARRIER.upper(), "MOBIUS_RED_ALERT_MULTIPLAYER_%d_MAP" % HASTINGS)]
    entries = [entry(HASTINGS, hastings)]

    work = tempfile.mkdtemp()
    for number, td_name, stem, folder in td_maps(base_instances):
        td_body = base_instances[td_name].group(2)
        players = int(re.search(r"<MaxPlayers>\s*(\d+)", td_body).group(1))
        ini = fetch(stem, folder, work)
        name = dict(td_map_to_ra.get_sec(td_map_to_ra.read_ini(ini), "Basic")).get("Name", stem)
        out = os.path.join(work, "TFTD%03d" % number)
        td_map_to_ra.convert(ini, out + ".mpr", name)
        with open(out + ".mpr", "rb") as f, open(os.path.join(MOD, "CCDATA/TFTD%03d.INI" % number), "wb") as g:
            g.write(f.read())
        entries.append(entry(number, td_body))
        previews.append(preview(number, json.load(open(out + ".json")), players))
        print("%d  %-14s %s" % (number, stem, name))

    first = re.search(r'\t<Instance Name="Mobius_Red_Alert_Multiplayer_\w+_Map"', inst).group(0)
    inst = splice(inst, "".join(entries), BEGIN, END, first)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(inst)
    pv = splice(pv_base, "".join(previews), PREVIEW_BEGIN, PREVIEW_END, "\t\t</CNCMapPreviewData>")
    with open(os.path.join(MOD, "Data/XML/CNCMAPPREVIEWDATA.XML"), "w", encoding="latin-1", newline="") as f:
        f.write(pv)
    print("%d entries, Hastings at %d" % (len(entries), HASTINGS))


if __name__ == "__main__":
    main()
