#!/usr/bin/env python3
"""Build the Workshop asset-pack mods (asset_packs.WORKSHOP) from the asset-packs/ source folders.

Usage:  workshop_packs.py <out dir> [item ...]   (every Workshop item when none is named)

Each item is a data-only mod for one game (asset_packs.items: Red Alert, or Tiberian Dawn as <mod>-TD):
ccmod.json, README.md, every file of its source packs under Data/ART and Data/AUDIO (a later pack's copy
of a path wins; a TD item's art moves to TD's own folder), and its XML: one file per launcher XML, the
source packs' entries together, complete on their own (no ZIP shared with another mod), in that game's
names and texture roots; a DLL mod copies the entries into its own XML. A pack Tiberian Factions requires
also carries its marker in CCDATA, which the mod's DLL reads to know the pack is enabled.

scripts/stage_asset_packs.py builds the required packs beside the staged mod the same way.

License: GPL v3.
"""
import hashlib
import json
import os
import re
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs as A  # noqa: E402
import asset_pack_docs as D  # noqa: E402
import mix_tools  # noqa: E402

STUBS = os.path.join(A.MOD, "CCDATA", "TFASSETS.MIX")
C3_SEATS = os.path.join(A.REPO, "redalert", "c3tanks.h")
TS_SEATS = os.path.join(A.REPO, "redalert", "udata.cpp")
# Objects drawn at another object's classic size: the rail tanks are their tanks with other turrets
SHAPE_LIKE = {"C3MK3RAIL": "C3MK3", "C3PREDRAIL": "C3PRED"}
# Units with no classic stub that take a stock image's (idata.cpp, udata.cpp), and those images' classic sizes as
# Red Alert's own MIX files hold them (E1.SHP in REDALERT.MIX/HIRES.MIX, MCV.SHP in MAIN.MIX/CONQUER.MIX)
STOCK_IMAGE = {"TSE1": "E1", "TSE2": "E1", "TSE3": "E1", "TSENGINEER": "E1", "TSGHOST": "E1", "TSMEDIC": "E1",
               "TSMCV": "MCV"}
STOCK_SIZE = {"E1": (50, 39), "MCV": (48, 48)}
SHAPE_SECTION = {"UNITS": "Units", "STRUCTURES": "Structures", "VFX": "Animations"}

# Launcher XML -> (folder under Data/XML, the file name for a pack)
XML_NAMES = {
    os.path.join("XML", "TILESETS", "RA_UNITS.XML"): ("TILESETS", "{id}_UNITS.XML"),
    os.path.join("XML", "TILESETS", "RA_STRUCTURES.XML"): ("TILESETS", "{id}_STRUCTURES.XML"),
    os.path.join("XML", "TILESETS", "RA_VFX.XML"): ("TILESETS", "{id}_VFX.XML"),
    os.path.join("XML", "TILESETS", "RA_TERRAIN_TEMPERATE.XML"): ("TILESETS", "{id}_TERRAIN_TEMPERATE.XML"),
    os.path.join("XML", "TILESETS", "RA_TERRAIN_SNOW.XML"): ("TILESETS", "{id}_TERRAIN_SNOW.XML"),
    os.path.join("XML", "TILESETS", "RA_TERRAIN_INTERIOR.XML"): ("TILESETS", "{id}_TERRAIN_INTERIOR.XML"),
    os.path.join("XML", "OBJECTS", "UNITS", "RABUILDABLES.XML"): (os.path.join("OBJECTS", "UNITS"),
                                                                 "{id}Buildables.xml"),
    os.path.join("XML", "AUDIO", "SFXEVENTSNONLOCALIZED.XML"): ("AUDIO", "SFXEvents{id}.xml"),
    os.path.join("XML", "AUDIO", "SFXEVENTSLOCALIZED.XML"): ("AUDIO", "SFXEventsLocalized{id}.xml"),
}


def host_path(rel, host):
    """A path under Data/ART for the host game: Red Alert art moves to that game's folder and theatre. None for
    terrain of a theatre the game lacks, which no map of that game can use."""
    parts = rel.split(os.sep)
    if host == "RA" or parts[:3] != ["TEXTURES", "SRGB", "RED_ALERT"]:
        return rel
    h = A.HOSTS[host]
    if parts[3] == "TERRAIN":
        if parts[4] not in h["theatres"]:
            return None
        parts[4] = h["theatres"][parts[4]]
    return os.path.join("TEXTURES", "SRGB", h["art"], *parts[3:])


def copy_binaries(mod, folder, host):
    """Every file under the mod's source packs' Data/ART and Data/AUDIO, and no other; a later pack's copy of a
    path wins."""
    packs = A.WORKSHOP[mod]["packs"]
    wanted = set()
    for i, pack in enumerate(packs):
        for sub in ("ART", "AUDIO"):
            src = os.path.join(A.pack_data(pack), sub)
            later = {os.path.relpath(os.path.join(d, f), src).upper()
                     for p in packs[i + 1:] for d, _, fs in os.walk(os.path.join(A.pack_data(p), sub)) for f in fs}
            for d, _, fs in os.walk(src):
                for f in fs:
                    rel = os.path.relpath(os.path.join(d, f), src)
                    if rel.upper() in later:
                        continue
                    target = host_path(rel, host) if sub == "ART" else rel
                    if target is None:
                        continue
                    dst = os.path.join(folder, "Data", sub, target)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    A.copy_newer(os.path.join(d, f), dst)
                    wanted.add(os.path.normcase(dst))
    for sub in ("ART", "AUDIO"):
        for d, _, fs in os.walk(os.path.join(folder, "Data", sub)):
            for f in fs:
                if os.path.normcase(os.path.join(d, f)) not in wanted:
                    os.remove(os.path.join(d, f))


def combined_xml(mod, rel, pack_file, root):
    """The mod's source packs' entries for one launcher XML, in the first source file's wrapper; None if empty."""
    sources = [pack_file(p) for p in A.WORKSHOP[mod]["packs"] if os.path.exists(pack_file(p))]
    bodies, template = [], None
    for path in sources:
        text = open(path, encoding="utf-8-sig", newline="").read()
        opened = re.search(r"<%s\b[^>]*>[ \t]*\r?\n" % root, text)
        if opened is None:
            continue
        body = text[opened.end():text.rindex(f"</{root}>")]
        if body.strip():
            bodies.append(body)
            template = template or (text[:opened.end()], text[text.rindex(f"</{root}>"):])
    if not bodies:
        return None
    return template[0] + "".join(bodies) + template[1]


def write_if_changed(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path) or open(path, encoding="utf-8", newline="").read() != text:
        open(path, "w", encoding="utf-8", newline="").write(text)


def host_xml(rel, text, host):
    """A launcher XML's path and text for the host game: its tileset names and texture roots, its buildable names.
    (None, None) for the terrain of a theatre the game lacks."""
    if host == "RA":
        return rel, text
    h = A.HOSTS[host]
    if os.path.basename(rel) == "RABUILDABLES.XML":
        text = re.sub(r'(<ObjectTypeClass\s+Name=")RA_', r"\g<1>%s_" % h["prefix"], text)
        return os.path.join(os.path.dirname(rel), h["buildables"] + ".XML"), text
    if os.sep + "TILESETS" + os.sep not in rel:
        return rel, text
    kind = os.path.basename(rel)[len("RA_"):-len(".XML")]
    if kind.startswith("TERRAIN_"):
        theatre = kind[len("TERRAIN_"):]
        if theatre not in h["theatres"]:
            return None, None
        kind = "TERRAIN_" + h["theatres"][theatre]
    text = re.sub(r'(<TilesetTypeClass\s+name=")RA_\w+', lambda m: m.group(1) + h["prefix"] + "_" +
                  "_".join(w.capitalize() if w != "VFX" else w for w in kind.split("_")), text)
    text = re.sub(r"(<RootTexturePath>)Red_Alert\\[^<]*", lambda m: m.group(1) + h["root"] + "\\" +
                  "\\".join(w.capitalize() if w != "VFX" else w for w in A.kind_dir(kind).split(os.sep)), text)
    return os.path.join(os.path.dirname(rel), f"{h['prefix']}_{kind}.XML"), text


def write_xml(mod, folder, host):
    """The mod's XML files; returns {the host's launcher XML: the pack's file name} and the paths written."""
    files, written = {}, []
    for rel, pack_file, root, _ in A.XML_FILES:
        sub, pattern = XML_NAMES[rel]
        text = combined_xml(mod, rel, pack_file, root)
        if text is None:
            continue
        target, text = host_xml(rel, text, host)
        if target is None:
            continue
        name = pattern.format(id=A.WORKSHOP[mod]["xml_id"])
        if host != "RA" and sub == "TILESETS":
            name = os.path.basename(target).replace(A.HOSTS[host]["prefix"], A.WORKSHOP[mod]["xml_id"], 1)
        path = os.path.join(folder, "Data", "XML", sub, name)
        write_if_changed(path, text)
        files[target] = name
        written.append(path)
    return files, written


def write_manifest(mod, folder, host):
    """ccmod.json, and for a pack Tiberian Factions requires, the CCDATA marker carrying its version; returns the
    marker's path, or None."""
    w = A.WORKSHOP[mod]
    high, low = w["version"]
    manifest = {"name": A.mod_list_text(w["name"]),
                "description": A.mod_list_text(w["description"].format(host=A.HOSTS[host]["name"])),
                "author": "gibbo101", "load_order": 2, "version_high": high, "version_low": low, "game_type": host}
    write_if_changed(os.path.join(folder, "ccmod.json"), json.dumps(manifest, indent=4) + "\n")
    if not (w.get("marker") and host == "RA"):
        return None
    marker = os.path.join(folder, "CCDATA", w["marker"])
    write_if_changed(marker, f"[Pack]\nName={mod}\nVersion={high}.{low}\n")
    return marker


GAME = {"TS": "Tiberian Sun", "RA2": "Red Alert 2", "CNC3": "Command & Conquer 3: Tiberium Wars"}
TF_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253"
EA_EXAMPLE_URL = {
    "RA": "https://github.com/electronicarts/CnC_Remastered_Collection/blob/master/REDALERT/ADATA.CPP#L2590",
    "TD": "https://github.com/electronicarts/CnC_Remastered_Collection/blob/master/TIBERIANDAWN/UDATA.CPP#L1681",
}


def contents(mod):
    """Section title -> sorted names across the mod's source packs."""
    out = {}
    for pack in A.WORKSHOP[mod]["packs"]:
        for title, names in D.listing(pack).items():
            out.setdefault(title, set()).update(names)
    return {title: sorted(names) for title, names in out.items()}


def host_section(title, host):
    """A README section title for the host game: a terrain section under the host's theatre name, None for a
    theatre the host lacks."""
    m = re.match(r"Terrain \((\w+)\)$", title)
    if m is None:
        return title
    theatre = A.HOSTS[host]["theatres"].get(m.group(1).upper())
    return f"Terrain ({theatre.lower()})" if theatre else None


def music_readme(mod, host):
    """A music pack's README.md: what it is, how Tiberian Factions and other mods play it, and credits."""
    w = A.WORKSHOP[mod]
    h = A.HOSTS[host]
    lines = [f"# {w['name']}", "", w["description"].format(host=h["name"]) +
             " Built for Command & Conquer Remastered Collection.", "",
             "This is an asset pack: on its own it adds nothing to the game. A mod has to use it.", "",
             "## Playing Tiberian Factions", "",
             f"With this pack enabled beside [Tiberian Factions]({TF_URL}), its tracks join the skirmish music and "
             "the jukebox. Without it, Tiberian Factions plays its usual music.", "",
             "## Using the music in your own mod", "",
             "Enable this pack beside your mod: the game finds its WAVs in any enabled mod. Name them in your mod's "
             "`Data/XML/AUDIO/MUSICEVENTS.XML` playlists, and for the jukebox add an entry per track to "
             "`<MusicJukeboxTracksList>` in `AUDIO_SYSTEM_CONSTANTS.XML`, with its title in your `ModText.csv`.", ""]
    if w.get("contents"):
        lines += ["## Contents", ""] + [f"- {line}" for line in w["contents"]] + [""]
    lines += ["## Files", ""]
    for title, names in contents(mod).items():
        lines += [f"**{title}** ({len(names)}): " + ", ".join(names), ""]
    lines += ["## AI disclosure", "", "No AI made or changed the music: these are the original tracks, converted. "
              "The scripts that build this pack were written with AI assistance.", "",
              "## Credits", "", f"Original {GAME[w['game']]} and Firestorm music: Westwood Studios and Electronic Arts.",
              "Converted for Remastered by gibbo101.", "", "## My other C&C projects", ""] + [f"- {m}" for m in D.more_mods(mod)] + [""]
    return "\n".join(lines)


def readme(mod, listed, host):
    """The pack's README.md: what it is, how players and modders use it, contents and credits."""
    w = A.WORKSHOP[mod]
    if w.get("kind") == "music":
        return music_readme(mod, host)
    h = A.HOSTS[host]
    game = GAME[w["game"]]
    lines = [f"# {w['name']}", "", w["description"].format(host=h["name"]) +
             " Built for Command & Conquer Remastered Collection.", "",
             "This is an asset pack: on its own it adds nothing to the game. A mod has to use it.", ""]
    ids = w.get("workshop_ids", {})
    for other in (o for o in w["hosts"] if o != host):
        pack = f"[{other} pack]({D.WORKSHOP_URL}{ids[other]})" if other in ids else f"{other} pack"
        lines += [f"This pack is for {h['name']} only. Please see the {pack} if you want to use this for {other}.", ""]
    if w["required"] and host == "RA":
        lines += ["## Playing Tiberian Factions", "",
                  f"[Tiberian Factions]({TF_URL}) needs this pack for its {game} factions.", "",
                  "1. Subscribe to Tiberian Factions and to this pack.",
                  "2. In the game's Mods menu, enable both.",
                  "3. Restart the game: the game only picks up a change to enabled mods after a restart.", "",
                  f"Without the pack, Tiberian Factions still plays, but its {game} factions are locked.", ""]
    lines += ["If the game crashes on the splash screen, the extra art needs more video memory than it has: add "
              "`NOSPLASHPRELOAD` to the game's launch options.", ""]
    lines += ["## Using the assets in your own mod", "",
              f"Every object, cameo and sound is named with the `{w['prefix']}` prefix, so nothing clashes with the "
              "base game's own assets.", "",
              "Enable this pack beside your mod (the game finds its art and sounds in any enabled mod) and copy "
              "the entries you need from this pack's `Data/XML` files into your mod's "
              f"`{h['prefix']}_*.XML`, `{h['buildables']}.XML` and `SFXEVENTS*.XML`. Each object needs a classic-mode "
              "SHP with the same frame count (a transparent stub is enough) and its `ImageData` set in your DLL's "
              f"`Init` or `One_Time` ([EA's example]({EA_EXAMPLE_URL[host]})).", "",
              "Some stock tiles are animated: they hold several `<Frame>`s and an `<AnimationData>` FPS"
              + (" (the Red Alert Heavy Tank and Mammoth Tank turrets have 8 frames at 5 FPS)" if host == "RA" else "")
              + ". When you point an existing tile at this pack's art, replace its whole `<Frames>` list and remove its "
              f"`<AnimationData>`, or you'll see the {host} frames constantly switch with yours.", ""]
    if w["game"] == "TS":
        lines += ["Most units use the stock layout: one frame per facing, then a turret block where they have one. "
                  "Walkers, units with rolling treads, and buildings with doors, docks or add-ons "
                  "use Tiberian Factions' own layouts and need the matching DLL code, which is in its "
                  f"[source]({D.REPO_URL}).", ""]
    lines += layout(mod)
    if w.get("contents"):
        lines += ["## Contents", ""] + [f"- {line}" for line in w["contents"]] + ["", "More content to come.", ""]
    lines += ["## Files", ""]
    for title, names in contents(mod).items():
        title = host_section(title, host)
        if title:
            lines += [f"**{title}** ({len(names)}): " + ", ".join(names), ""]
    lines += ["XML files: " + ", ".join(f"`{n}`" for n in sorted(listed.values())) + ".", ""]
    shapes = shape_data(mod)
    lines += ["## Shape data", "", "Each object's classic-mode SHP: its size in classic pixels and its frame count."]
    if any("(" in row for rows in shapes.values() for row in rows):
        lines[-1] += (" A unit marked with a stock image takes that image's size; a layer has no SHP of its own and "
                      "is drawn with the object named.")
    lines += [""]
    for section, rows in shapes.items():
        section = host_section(section, host)
        if section:
            lines += [f"**{section}**", "", "```"] + rows + ["```", ""]
    lines += ["## AI disclosure", ""]
    if w["game"] in ("TS", "RA2"):
        lines += ["The HD art in this pack was made with AI assistance. The 3D models behind the sprites were built "
                  "and refined with AI tools, then rendered, checked and fitted to the game by hand, and every asset "
                  "was reviewed in play in Red Alert before release."]
    else:
        lines += ["These sprites were rendered from the game's own 3D models; no AI generated the art."]
    makers = "Electronic Arts'" if w["game"] == "CNC3" else "Westwood's and Electronic Arts'"
    code = "The scripts and tools that build this pack, and Tiberian Factions' code," if w["required"] else \
        "The scripts and tools that build this pack"
    lines += [f"{code} were written with AI assistance. The original designs, sounds and voices are {makers}.", ""]
    lines += ["## Credits", "", f"Original {game} art and sounds: Electronic Arts."]
    if w["game"] in ("TS", "RA2"):
        lines += [f"HD rebuilds of the {game} designs and preparation for Remastered: gibbo101."]
    else:
        lines += ["Rendered for Remastered from the game's own models by gibbo101."]
    lines += ["", "## My other C&C projects", ""] + [f"- {m}" for m in D.more_mods(mod)] + [""]
    return "\n".join(lines)


def layout(mod):
    """README notes on the order of a pack's unit frames, and where a C&C3 or off-centre TS turret seats."""
    game = A.WORKSHOP[mod]["game"]
    if game == "RA2":
        return ["## Frame layout", "",
                "R2APOC and R2PRIS use the stock tank layout: frames 0-31 are the hull and 32-63 the turret, "
                "32 facings each, counter-clockwise from north.", ""]
    if game == "TS":
        lines = ["## Turret seats", "",
                 "TSHVR's rack and TSSONIC's turret sit off the hull's centre: draw them over the hull moved by their "
                 "seat for the hull's facing, in classic pixels (x east, y south), for hull facings 0-31 "
                 "counter-clockwise from north:", ""]
        text = open(TS_SEATS, encoding="utf-8").read()
        for unit, method in (("TSHVR", "Hover_Rack_Seat"), ("TSSONIC", "Sonic_Turret_Seat")):
            seats = re.search(r"::%s\(.*?_seat\[32\]\[2\] = \{(.*?)\};" % method, text, re.S).group(1)
            pairs = " ".join(f"{x},{y}" for x, y in re.findall(r"\{(-?\d+), *(-?\d+)\}", seats))
            lines += [f"{unit}: `{pairs}`", ""]
        return lines
    if game != "CNC3":
        return []
    lines = ["## Frame layout", "",
             "C3MK3, C3PRED, C3MK3RAIL and C3PREDRAIL: frames 0-95 are the hull, 32 facings counter-clockwise from "
             "north with 3 tread steps each (frame = 3 x facing + step; step the treads while the tank drives), "
             "and 96-127 the turret, 32 facings. The turret frames are centred on the canvas: draw the turret over "
             "the hull moved by its seat for the hull's facing, in classic pixels (x east, y south), for hull facings "
             "0-31 counter-clockwise from north:",
             ""]
    text = open(C3_SEATS, encoding="utf-8").read()
    for tank in ("C3MK3", "C3PRED"):
        seats = re.search(r"_%s_seat_px\[32\]\[2\] = \{(.*?)\};" % tank.lower(), text).group(1)
        pairs = " ".join(f"{x},{y}" for x, y in re.findall(r"\{(-?\d+), (-?\d+)\}", seats))
        lines += [f"{tank} (and {tank}RAIL): `{pairs}`", ""]
    return lines


def shape_data(mod):
    """Section -> 'NAME width=W height=H frames=N' rows: the size of the object's classic stub, one frame per tile,
    in the source packs' tileset order."""
    _, _, entries, blob = mix_tools.read_mix(STUBS)
    stubs = {crc: offset for crc, offset, _ in entries}
    out = {}
    for pack in A.WORKSHOP[mod]["packs"]:
        for kind in A.KINDS:
            path = A.pack_tileset_path(pack, kind)
            if not os.path.exists(path):
                continue
            section = SHAPE_SECTION.get(kind, "Terrain (" + kind[len("TERRAIN_"):].lower() + ")")
            counts = {}
            for name in re.findall(r"<Name>\s*([^<\s]+)\s*</Name>", open(path, encoding="utf-8-sig").read()):
                counts[name.upper()] = counts.get(name.upper(), 0) + 1
            rows = out.setdefault(section, [])
            for name, frames in counts.items():
                offset = stubs.get(mix_tools.ww_crc(SHAPE_LIKE.get(name, name) + ".SHP"))
                if name in STOCK_IMAGE:
                    width, height = STOCK_SIZE[STOCK_IMAGE[name]]
                    row = f"{name} width={width} height={height} frames={frames} (stock {STOCK_IMAGE[name]} image)"
                elif offset is None:
                    parents = [n for n in counts if n != name and name.startswith(n)] + \
                        [n for n in all_names(mod) if n != name and name.startswith(n)]
                    parent = max(parents, key=len) if parents else name[:-1]
                    row = f"{name} frames={frames} (layer of {parent})"
                else:
                    width, height = struct.unpack("<2H", blob[offset + 6:offset + 10])
                    row = f"{name} width={width} height={height} frames={frames}"
                if row not in rows:
                    rows.append(row)
    return {section: rows for section, rows in out.items() if rows}


def all_names(mod):
    """Every object name in the mod's source packs' tilesets."""
    names = set()
    for pack in A.WORKSHOP[mod]["packs"]:
        for kind in A.KINDS:
            path = A.pack_tileset_path(pack, kind)
            if os.path.exists(path):
                names.update(n.upper() for n in re.findall(r"<Name>\s*([^<\s]+)\s*</Name>",
                                                            open(path, encoding="utf-8-sig").read()))
    return names


def prune(folder, sub, keep):
    """Delete every file under folder/sub that isn't one of the paths in keep, and the folders left empty."""
    keep = {os.path.normcase(p) for p in keep}
    for d, _, fs in os.walk(os.path.join(folder, sub), topdown=False):
        for f in fs:
            if os.path.normcase(os.path.join(d, f)) not in keep:
                os.remove(os.path.join(d, f))
        if not os.listdir(d):
            os.rmdir(d)


def check_md5(mod, folder):
    """What is wrong when a file the mod's md5 list names is missing from the built folder or differs, else "";
    a pack whose files are gitignored would otherwise ship empty."""
    listing = A.WORKSHOP[mod].get("md5")
    if not listing:
        return ""
    music = os.path.join(folder, "Data", "AUDIO", "MUSIC")
    bad = []
    for line in open(os.path.join(A.REPO, listing)):
        digest, name = line.split()
        path = os.path.join(music, name)
        if not os.path.exists(path) or hashlib.md5(open(path, "rb").read()).hexdigest() != digest:
            bad.append(name)
    if not bad:
        return ""
    return (f"{folder}: {len(bad)} file(s) missing or not as {listing} lists them, e.g. {bad[0]}. "
            "Build them first (scripts/ts_music_build.py).")


def build(mod, folder, host="RA", strict=True):
    """The whole Workshop folder for one asset-pack mod, for one game, and nothing an earlier build left. A file
    missing from the md5 list stops it, or with strict off skips the mod with a warning."""
    marker = write_manifest(mod, folder, host)
    copy_binaries(mod, folder, host)
    problem = check_md5(mod, folder)
    if problem and strict:
        raise SystemExit(problem)
    if problem:
        print("WARNING: skipped", mod, "--", problem, file=sys.stderr)
        return
    listed, written = write_xml(mod, folder, host)
    prune(folder, os.path.join("Data", "XML"), written)
    prune(folder, "CCDATA", [marker] if marker else [])
    write_if_changed(os.path.join(folder, "README.md"), readme(mod, listed, host))
    check(folder, host)


def check(folder, host):
    """Stop if a tile's frame has no file in the item, or a ZIP has no tile of its own name to open it."""
    art = os.path.join(folder, "Data", "ART", "TEXTURES", "SRGB", A.HOSTS[host]["art"])
    zips = {}
    for d, _, fs in os.walk(art):
        for f in fs:
            if f.upper().endswith(".ZIP"):
                rel = os.path.relpath(os.path.join(d, f), art).replace(os.sep, "\\").upper()
                with zipfile.ZipFile(os.path.join(d, f)) as z:
                    zips[rel[:-4]] = {n.upper() for n in z.namelist()}
    named, problems = set(), []
    tilesets = os.path.join(folder, "Data", "XML", "TILESETS")
    for f in sorted(os.listdir(tilesets)) if os.path.isdir(tilesets) else []:
        text = open(os.path.join(tilesets, f), encoding="utf-8-sig").read()
        found = re.search(r"<RootTexturePath>([^<]+)</RootTexturePath>", text)
        if found is None:
            problems.append(f"{f}: no RootTexturePath")
            continue
        root = found.group(1)
        if not root.upper().startswith(A.HOSTS[host]["root"].upper() + "\\"):
            problems.append(f"{f}: root {root} is not {A.HOSTS[host]['name']}'s")
        folder_key = root.split("\\", 1)[1].upper()
        for name, frames in re.findall(r"<Name>([^<]+)</Name>.*?<Frames>(.*?)</Frames>", text, re.S):
            named.add(f"{folder_key}\\{name.upper()}")
            for frame in re.findall(r"<Frame>([^<]+)</Frame>", frames):
                z, _, tga = frame.upper().partition("\\")
                if tga not in zips.get(f"{folder_key}\\{z}", ()):
                    problems.append(f"{f}: {name} frame {frame} is not in {folder_key}\\{z}.ZIP")
    problems += [f"{z}.ZIP has no tile named {z.rsplit(chr(92), 1)[1]}, so the game never opens it"
                 for z in zips if z not in named]
    if problems:
        raise SystemExit(f"{folder}:\n  " + "\n  ".join(problems[:20]))


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    out, wanted = argv[0], argv[1:]
    known = {i: (mod, host) for i, mod, host in A.items()}
    for name in wanted or list(known):
        if name not in known:
            raise SystemExit(f"not a Workshop item: {name} (items: {', '.join(known)})")
        mod, host = known[name]
        build(mod, os.path.join(out, name), host)
        print(f"built {os.path.join(out, name)}")


if __name__ == "__main__":
    main(sys.argv[1:])
