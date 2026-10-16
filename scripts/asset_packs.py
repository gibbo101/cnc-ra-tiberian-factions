#!/usr/bin/env python3
"""The asset packs: which of the mod's files belong to which Workshop pack, and where they live.

Every folder under asset-packs/ holds one kind of asset (the TD-Assets layout): ccmod.json,
README.md and a Data/ tree in the launcher's own layout, so another modder can copy any of it
straight into their mod. Tiberian Factions' own files stay in resources/remaster_mods/Vanilla_RA.
The build stages both (scripts/stage_asset_packs.py): each pack's XML entries are merged into the
mod's XML files, and its art and audio are copied into the staged mod, or, for the packs a
Workshop mod in USED carries, into that mod's folder beside it. The launcher finds a file in any
enabled mod, so the mod keeps only the XML naming them.

A file's pack follows from its name alone, so every pack script asks this module for its output
paths and a new TS, RA2 or C&C3 asset lands in its pack without a list to maintain:
  graphics   TS* (not TSLA*, RA's Tesla Coil), R2*, C3<letter> (bare C3 is RA's
             civilian). TS art goes to TS-HD, TS Nod's (TS_NOD) to TS-Nod.
  cameos     the plain BuildIcon of each of those objects; an HD cameo (scripts/ts_hd_cameos.py)
             replaces the classic one in the same file (save_classic_cameo). Badged, locked and faction-mask
             variants, and the superweapon icons, drive Tiberian Factions' sidebar and
             stay with the mod.
  sounds     TS_SFX_EVA_* EVA, TS_SFX_UNT_* unit voices, other TS* effects; RA2 and C&C3 crew
             lines (select, move, attack takes) apart from their weapon and engine sounds.
             TSLACHG2R is RA's Tesla charge and TF_MBX_* is the EVA mailbox: both stay.

Pack XML files mirror the mod's own: TILESETS/<PREFIX>_<KIND>.XML for RA_<KIND>.XML,
OBJECTS/UNITS/<PREFIX>BUILDABLES.XML for RABUILDABLES.XML and
AUDIO/SFXEVENTS[NON]LOCALIZED_<PREFIX>.XML for SFXEVENTS[NON]LOCALIZED.XML. The launcher never
loads them from a pack (its tileset list in CONFIG.MEG names only the RA_ files); they are the
entries a modder copies, and what the build merges into the staged mod.

License: GPL v3.
"""
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MOD = os.path.join(REPO, "resources", "remaster_mods", "Vanilla_RA")
PACKS_DIR = os.path.join(REPO, "asset-packs")

# pack -> prefix of its XML files
PACKS = {
    "TS-HD-Graphics-Pack": "TSHD",
    "TS-Nod-Graphics-Pack": "TSNOD",
    "TS-SFX-Pack": "TS",
    "TS-EVA-eng": "TS",
    "TS-Voices-eng": "TS",
    "RA2-Graphics-Pack": "RA2",
    "RA2-SFX-Pack": "RA2",
    "RA2-Voices-eng": "RA2",
    "CNC3-Graphics-Pack": "CNC3",
    "CNC3-SFX-Pack": "CNC3",
    "CNC3-Voices-eng": "CNC3",
    "TS-Music": "TS",
}

# The Workshop asset-pack mods, data only, each built from these source packs (scripts/workshop_packs.py).
# Tiberian Factions requires the ones marked required: it keeps only their XML entries, and its DLL reads
# their CCDATA marker; the others are libraries for other modders, and the mod keeps its own copies.
WORKSHOP = {
    "TS-HD-Assets": {
        "packs": ("TS-HD-Graphics-Pack", "TS-SFX-Pack", "TS-EVA-eng", "TS-Voices-eng"),
        "required": True, "marker": "TSHDPACK.INI", "xml_id": "TSHDAssets", "version": (1, 0), "game": "TS",
        "prefix": "TS", "hosts": ("RA",), "workshop_ids": {"RA": "3819642604", "TD": "3819642832"},
        "name": "Tiberian Sun HD Assets",
        "description": "Tiberian Sun units, buildings, effects, sounds and EVA for {host}, in HD.",
        "contents": ["**GDI infantry:** Light Infantry (TSE1), Disc Thrower (TSE2), Engineer (TSENGINEER), Medic "
                     "(TSMEDIC), Jumpjet Infantry (TSJUMPJET), Ghost Stalker (TSGHOST)",
                     "**GDI vehicles:** Wolverine (TSSMEC), Titan (TSTITN), Amphibious APC (TSAPC), Hover MLRS (TSHVR), "
                     "Mobile Sensor Array (TSLPST), Mobile EMP (TSMEMP), Juggernaut (TSJUGG), Disruptor (TSSONIC), "
                     "Mammoth Mk. I (TS4TNK), Mammoth Mk. II (TSHMEC), Limpet Drone (TSLIMP), Harvester (TSHARV), "
                     "MCV (TSMCV), Mobile War Factory (TSMWAR)",
                     "**GDI aircraft:** Orca Fighter (TSORCA), Orca Bomber (TSORCAB), Orca Transport (TSORCATRAN), "
                     "Carryall (TSCARRY), Hunter Seeker (TSHUNT), Dropship (TSDSHP)",
                     "**GDI buildings:** Construction Yard (TSFACT), Power Plant (TSPOWR) and Turbine (TSTURB), Barracks "
                     "(TSPILE), Tiberium Refinery (TSPROC), Silo (TSSILO), War Factory (TSWEAP), Radar (TSRADR), "
                     "Helipad (TSHPAD), Service Depot (TSDEPT), Tech Center (TSTECH), Dropship Bay (TSDROP), Upgrade "
                     "Center (TSPLUG) with the Ion Cannon Uplink (TSPION), Seeker Control (TSSEEK) and Drop Pod Node "
                     "(TSPODS), EMP Cannon (TSPULS), Firestorm Generator (TSFGEN), Sensor Array (TSDPSA), Limpet Mine "
                     "(TSDLIMP)",
                     "**GDI defences:** Concrete Wall (TSWALL), Gates (TSGATEH, TSGATEV), Firestorm Wall (TSFSDF), "
                     "Component Tower (TSCTWR) with its Vulcan (TSVULCT), RPG (TSROCKT) and SAM (TSCSAMT) tops",
                     "**Effects:** Tiberian Sun's explosions, muzzle flashes, smoke and fire, the Ion Cannon beam, the "
                     "drop pods, the EMP pulse, the Firestorm and the Disruptor's wave",
                     "A sidebar cameo for each unit and building",
                     "GDI's unit voices, weapon and building sounds, and the EVA"],
    },
    "RA2-HD-Assets": {
        "packs": ("RA2-Graphics-Pack", "RA2-SFX-Pack", "RA2-Voices-eng"),
        "required": False, "xml_id": "RA2HDAssets", "version": (1, 0), "game": "RA2", "prefix": "R2",
        "hosts": ("RA", "TD"), "workshop_ids": {"RA": "3819308290", "TD": "3819308459"},
        "name": "Red Alert 2 HD Assets",
        "description": "Red Alert 2 units, sounds and voices for {host}, in HD.",
        "contents": ["**Soviet:** Apocalypse Tank (R2APOC)", "**Allies:** Prism Tank (R2PRIS)",
                     "A sidebar cameo for each unit", "Each unit's voices and weapon sounds"],
    },
    "CNC3-Assets": {
        "packs": ("CNC3-Graphics-Pack", "CNC3-SFX-Pack", "CNC3-Voices-eng"),
        "required": False, "xml_id": "CNC3Assets", "version": (1, 0), "game": "CNC3", "prefix": "C3",
        "hosts": ("RA", "TD"), "workshop_ids": {"RA": "3819308545", "TD": "3819308668"},
        "name": "C&C3 Tiberium Wars Assets",
        "description": "Command & Conquer 3 units, effects, sounds and voices for {host}, in HD.",
        "contents": ["**GDI:** Mammoth Tank Mk. III (C3MK3), Predator Tank (C3PRED), and both with the railgun "
                     "upgrade (C3MK3RAIL, C3PREDRAIL)",
                     "**Effects:** the railgun shot, in blue (C3RAILGLOW, C3RAILMZ, C3RAILHIT) and in orange "
                     "(C3RAILGLOWO, C3RAILMZO, C3RAILHITO)",
                     "A sidebar cameo for each tank", "Each tank's voices and weapon sounds"],
    },
    "TS-Music": {
        "packs": ("TS-Music",),
        "required": False, "used": True, "marker": "TSMUSIC.INI", "xml_id": "TSMusic", "version": (1, 0),
        "game": "TS", "prefix": "TS", "hosts": ("RA",),
        "name": "Tiberian Sun Music",
        "description": "Tiberian Sun and Firestorm's soundtrack for {host}.",
        "contents": ["**Tiberian Sun:** the 18 in-game themes, from Valves to Pharotek",
                     "**Firestorm:** the 8 in-game themes, from Elusive to Deploy Machines",
                     "Each as a Remastered music WAV (TS_MUS_<TITLE>.WAV)"],
    },
}
REQUIRED = [mod for mod, w in WORKSHOP.items() if w["required"]]
# The Workshop mods Tiberian Factions uses as their own folders beside it: the required ones, and the optional ones
# whose content it plays when they are enabled.
USED = [mod for mod, w in WORKSHOP.items() if w["required"] or w.get("used")]

# The game a Workshop item is for: its ccmod game_type and art folder under ART/TEXTURES/SRGB, the prefix of its
# launcher XML and buildable names, and its terrain theatres by RA theatre. A game reads art only from its own folder.
HOSTS = {
    "RA": {"name": "Red Alert", "art": "RED_ALERT", "root": "Red_Alert", "prefix": "RA", "buildables": "RABUILDABLES",
           "theatres": {"TEMPERATE": "TEMPERATE", "SNOW": "SNOW", "INTERIOR": "INTERIOR"}},
    "TD": {"name": "Tiberian Dawn", "art": "TIBERIAN_DAWN", "root": "Tiberian_Dawn", "prefix": "TD",
           "buildables": "CNCBUILDABLES", "theatres": {"TEMPERATE": "TEMPERATE", "SNOW": "WINTER"}},
}


def mod_list_text(text):
    """Text for a ccmod.json name or description: the game's mod list reads & as a shortcut marker, && as one &."""
    return text.replace("&", "&&")


def item(mod, host):
    """The Workshop item (and mod folder) name of a Workshop pack for one game."""
    return mod if host == "RA" else f"{mod}-{host}"


def items():
    """(item, mod, host) for every Workshop item."""
    return [(item(mod, host), mod, host) for mod, w in WORKSHOP.items() for host in w["hosts"]]

# Objects only the Workshop packs carry: art for other mods that no Tiberian Factions type draws, so its build leaves
# out their ZIPs and tiles (scripts/stage_asset_packs.py).
PACK_ONLY = ("C3MK3RAIL", "C3PREDRAIL")


def drop_pack_only(text):
    """A tileset XML's text without the PACK_ONLY objects' tiles."""
    names = "|".join(map(re.escape, PACK_ONLY))
    return re.sub(r"[ \t]*<Tile>\s*<Key>\s*<Name>(?:%s)</Name>.*?</Tile>\r?\n?" % names, "", text, flags=re.S)


def used_mod(pack):
    """The Workshop mod in USED that carries a pack's art and audio, or None for the mod's own."""
    return next((mod for mod in USED if pack in WORKSHOP[mod]["packs"]), None)


# TS Nod's art, which the TS-HD-Assets pack leaves out until TS Nod ships whole. Tiberian Factions carries it meanwhile
# for its crate units. Every art name that starts with one of these, so an object's layers travel with it...
TS_NOD = ("TSTTNK", "TSTICK", "TSSUBTANK", "TSSAPC", "TSNWALL", "TSNGATEH", "TSNGATEV")
# ...these names exactly, and these sidebar cameos (BuildIcon_<name>)
TS_NOD_EXACT = ("TSE3",)
TS_NOD_CAMEOS = ("TS_TICKTANK", "TS_DEVILSTONGUE", "TS_SUBAPC", "TS_NWALL", "TS_ROCKETINFANTRY")
# TS-named cameos of the mod's own objects: TD Nod's Stealth Generator (TDSTEAL) is drawn from TS art
OWN_TS_CAMEOS = ("TS_STEALTHGEN",)

# tileset kinds: RA_<KIND>.XML in the mod; art folder under RED_ALERT/
KINDS = ("UNITS", "STRUCTURES", "VFX", "TERRAIN_TEMPERATE", "TERRAIN_SNOW", "TERRAIN_INTERIOR")


def hd_owned(name):
    """True for art that scripts/ts_pack_hd_buildings.py packs from the HD rebuilds; no other packer
    writes its zip, tiles or stub."""
    import ts_pack_hd_buildings as hd
    owned = set(hd.BUILDINGS) | set(hd.UNITS) | set(hd.APRONS)
    n = name.upper()
    return n in owned or (n.endswith("MAKE") and n[:-4] in owned)


def graphics_pack(name):
    """The pack an object's art belongs to (by IniName or art name), or None for the mod's own."""
    n = name.upper()
    if n.startswith("TSLA"):
        return None
    if n.startswith("TS"):
        if n.startswith(TS_NOD) or n in TS_NOD_EXACT:
            return "TS-Nod-Graphics-Pack"
        return "TS-HD-Graphics-Pack"
    if n.startswith("R2"):
        return "RA2-Graphics-Pack"
    if re.match(r"C3[A-Z]", n):
        return "CNC3-Graphics-Pack"
    return None


# the sidebar variants: one base-32 faction-mask digit (TS GDI alone is G), locked
CAMEO_VARIANT = re.compile(r"_([0-9A-V]|LK)$")


def cameo_pack(icon):
    """The pack a sidebar cameo belongs to: BuildIcon_<name>, with or without .tga."""
    stem = re.sub(r"\.tga$", "", os.path.basename(icon), flags=re.I)
    m = re.match(r"BuildIcon_(.+)$", stem, re.I)
    if not m:
        return None
    name = m.group(1)
    if CAMEO_VARIANT.search(name) or re.match(r"(SW|SG)_", name, re.I):
        return None
    if name.upper() in OWN_TS_CAMEOS:
        return None
    if name.upper() in TS_NOD_CAMEOS:
        return "TS-Nod-Graphics-Pack"
    if re.match(r"TS_", name, re.I):
        return "TS-HD-Graphics-Pack"
    return graphics_pack(name)


def sound_pack(sample):
    """The pack a sound sample belongs to (file name or stem, any extension or language suffix)."""
    s = re.sub(r"\.(WAV|MP3)$", "", os.path.basename(sample).upper())
    if s.startswith("TF_MBX_") or s == "TSLACHG2R":
        return None
    if s.startswith("TS_SFX_EVA_"):
        return "TS-EVA-eng"
    if s.startswith("TS_SFX_UNT_"):
        return "TS-Voices-eng"
    if s.startswith("TS"):
        return "TS-SFX-Pack"
    if s.startswith("R2V"):
        return "RA2-Voices-eng" if re.match(r"R2V(APO|PRI)(SE|MO|AT)[A-F]$", s) else "RA2-SFX-Pack"
    if s.startswith("C3"):
        return "CNC3-Voices-eng" if re.match(r"C3[MP](SE|MO|AT)[A-F]$", s) else "CNC3-SFX-Pack"
    return None


def pack_data(pack):
    return os.path.join(PACKS_DIR, pack, "Data")


def _made(path):
    """The path, with its folder created."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def _pack_xml(path, mod_file, root):
    """A pack XML path; a missing file is created empty, framed like the mod file it mirrors."""
    if not os.path.exists(path):
        text = open(mod_file, encoding="utf-8", newline="").read()
        head = re.match(r".*?<%s\b[^>]*>[ \t]*\r?\n" % root, text, re.S).group(0)
        open(_made(path), "w", encoding="utf-8", newline="").write(head + text[text.rindex(f"</{root}>"):])
    return path


def data_root(pack):
    """The Data/ folder a pack's files live in, or the mod's own for pack None."""
    return pack_data(pack) if pack else os.path.join(MOD, "Data")


def kind_dir(kind):
    """Art folder under ART/TEXTURES/SRGB/RED_ALERT for a tileset kind."""
    if kind.startswith("TERRAIN_"):
        return os.path.join("TERRAIN", kind[len("TERRAIN_"):])
    return kind


def art_zip(name, kind):
    """Path of an object's art ZIP: kind is UNITS, STRUCTURES, VFX or TERRAIN_<THEATRE>."""
    return _made(os.path.join(data_root(graphics_pack(name)), "ART", "TEXTURES", "SRGB", "RED_ALERT",
                              kind_dir(kind), f"{name.upper()}.ZIP"))


def art_dir(name, kind):
    return os.path.dirname(art_zip(name, kind))


def pack_tileset_path(pack, kind):
    """A pack's tileset XML path for a kind, whether or not the file exists."""
    return os.path.join(pack_data(pack), "XML", "TILESETS", f"{PACKS[pack]}_{kind}.XML")


def tileset_xml_of(pack, kind):
    mod_file = os.path.join(MOD, "Data", "XML", "TILESETS", f"RA_{kind}.XML")
    if pack is None:
        return mod_file
    return _pack_xml(pack_tileset_path(pack, kind), mod_file, "Tiles")


def tileset_xml(name, kind):
    """The tileset XML that holds an object's tiles."""
    return tileset_xml_of(graphics_pack(name), kind)


def shape_frames(name, kind):
    """Shape number -> the art ZIP member (no folder) its first frame names in the object's tileset XML.
    Deduplicated ZIPs share members between shapes, so a shape's member is never found by ZIP position."""
    text = open(tileset_xml(name, kind), encoding="utf-8").read()
    out = {}
    for tile in re.findall(r"<Tile>(.*?)</Tile>", text, re.S):
        key = re.search(r"<Name>\s*([^<\s]+)\s*</Name>\s*<Shape>\s*(\d+)\s*</Shape>", tile)
        frame = re.search(r"<Frame>\s*(?:[^\\<\s]+\\)?([^<\s]+?)\s*</Frame>", tile)
        if key and frame and key.group(1).upper() == name.upper():
            out[int(key.group(2))] = frame.group(1)
    return out


def cameo_tga(icon):
    stem = re.sub(r"\.tga$", "", os.path.basename(icon), flags=re.I)
    return _made(os.path.join(data_root(cameo_pack(stem)), "ART", "TEXTURES", "SRGB", f"{stem}.tga"))


TGA_RLE = 10


def is_rle_cameo(path):
    with open(path, "rb") as f:
        return f.read(3)[2:] == bytes([TGA_RLE])


def copy_newer(src, dst):
    """Copy unless dst already has src's size and is no older, keeping rsync-friendly mtimes. A sidebar cameo is
    written run-length encoded (the launcher reads RLE TGA) with src's mtime, and is current only at that mtime."""
    import shutil
    from PIL import Image
    cameo = os.path.basename(src).upper().startswith("BUILDICON_") and src.upper().endswith(".TGA")
    if os.path.exists(dst):
        a, b = os.stat(src), os.stat(dst)
        if cameo:
            same = is_rle_cameo(dst) and b.st_mtime_ns == a.st_mtime_ns
        else:
            same = a.st_size == b.st_size and b.st_mtime >= a.st_mtime
        if same:
            return dst
    if cameo:
        Image.open(src).save(dst, compression="tga_rle")
        shutil.copystat(src, dst)
        return dst
    return shutil.copy2(src, dst)


HD_CAMEO_ART = os.path.join(REPO, "resources", "custom-art", "ts-hd-cameos")


def save_classic_cameo(img, icon):
    """Save a cameo drawn from the source game's own icon, unless the HD cameo set (scripts/ts_hd_cameos.py) has
    art for that name: both go to the same file, and the HD one wins."""
    stem = re.sub(r"\.tga$", "", os.path.basename(icon), flags=re.I)
    if os.path.exists(os.path.join(HD_CAMEO_ART, f"{stem}.png")):
        print(f"kept the HD {stem}")
        return
    path = cameo_tga(stem)
    img.save(path)
    print(f"wrote {path}")


def buildables_xml_of(pack):
    mod_file = os.path.join(MOD, "Data", "XML", "OBJECTS", "UNITS", "RABUILDABLES.XML")
    if pack is None:
        return mod_file
    return _pack_xml(os.path.join(pack_data(pack), "XML", "OBJECTS", "UNITS", f"{PACKS[pack]}BUILDABLES.XML"),
                     mod_file, "ObjectTypeList")


def buildables_xml(icon):
    """The buildables XML that holds the sidebar entry showing this cameo."""
    return buildables_xml_of(cameo_pack(icon))


def sound_wav(sample, localized=False):
    """Path of a sound file: Data/AUDIO/<NAME>.WAV, or Data/AUDIO/EN-US/ when localized."""
    name = os.path.basename(sample)
    if not name.upper().endswith(".WAV"):
        name += ".WAV"
    parts = ["AUDIO", "EN-US"] if localized else ["AUDIO"]
    return _made(os.path.join(data_root(sound_pack(name)), *parts, name))


def sfx_xml_of(pack, localized):
    base = "SFXEVENTSLOCALIZED" if localized else "SFXEVENTSNONLOCALIZED"
    mod_file = os.path.join(MOD, "Data", "XML", "AUDIO", f"{base}.XML")
    if pack is None:
        return mod_file
    return _pack_xml(os.path.join(pack_data(pack), "XML", "AUDIO", f"{base}_{PACKS[pack]}.XML"),
                     mod_file, "LocalizedSFXEvents" if localized else "SFXEvents")


def sfx_xml(sample, localized):
    """The sound-event XML that holds the events playing this sample."""
    return sfx_xml_of(sound_pack(sample), localized)


# The mod's XML files a pack can contribute to, with each one's root element and the regex of one
# entry. Entries keep their exact text; a pack file is the mod file's header, the entries, and the
# closing tag.
XML_FILES = (
    [(os.path.join("XML", "TILESETS", f"RA_{k}.XML"), (lambda p, k=k: tileset_xml_of(p, k)), "Tiles",
      re.compile(r"[ \t]*<Tile>.*?</Tile>[ \t]*\r?\n", re.S)) for k in KINDS]
    + [(os.path.join("XML", "OBJECTS", "UNITS", "RABUILDABLES.XML"), buildables_xml_of, "ObjectTypeList",
        re.compile(r"[ \t]*<ObjectTypeClass\b.*?</ObjectTypeClass>[ \t]*\r?\n", re.S))]
    + [(os.path.join("XML", "AUDIO", "SFXEVENTSNONLOCALIZED.XML"), (lambda p: sfx_xml_of(p, False)), "SFXEvents",
        re.compile(r"[ \t]*<SFXEvent\b.*?</SFXEvent>[ \t]*\r?\n", re.S)),
       (os.path.join("XML", "AUDIO", "SFXEVENTSLOCALIZED.XML"), (lambda p: sfx_xml_of(p, True)), "LocalizedSFXEvents",
        re.compile(r"[ \t]*<LocalizedSFXEvent\b.*?</LocalizedSFXEvent>[ \t]*\r?\n", re.S))]
)


def marker(pack):
    """The comment line in a mod XML file where the build merges a pack's entries."""
    return f"<!-- asset-pack: {pack} -->"


ENTRY_NAME = {
    "Tiles": re.compile(r"<Name>\s*([^<\s]+)\s*</Name>"),
    "ObjectTypeList": re.compile(r'<ObjectTypeClass\s+Name="([^"]+)"'),
}
SAMPLE = re.compile(r"<entry>\s*([^<\s]+)\s*</entry>")
ICON = re.compile(r"<BuildIcon>\s*([^<\s]+)\s*</BuildIcon>")


def entry_pack(root, text):
    """The pack an XML entry belongs to, or None for the mod's own."""
    if root == "Tiles":
        m = ENTRY_NAME[root].search(text)
        return graphics_pack(m.group(1)) if m else None
    if root == "ObjectTypeList":
        m = ENTRY_NAME[root].search(text)
        if not m:
            return None
        pack = cameo_pack("BuildIcon_" + re.sub(r"^RA_", "", m.group(1)))
        icons = ICON.findall(text)
        return pack if pack and all(cameo_pack(i) == pack for i in icons) else None
    lists = re.findall(r"<SampleNamesList>(.*?)</SampleNamesList>", text, re.S)
    packs = {sound_pack(s) for lst in lists for s in SAMPLE.findall(lst)}
    return packs.pop() if len(packs) == 1 else None


BLOCK = re.compile(r"[ \t]*<!-- BEGIN (?:generated )?(.*?)-->[ \t]*\r?\n(.*?)[ \t]*<!-- END .*?-->[ \t]*\r?\n", re.S)


def entry_key(root, text):
    """What makes an entry the same object: a tile's object name (all its shapes are written
    together), or a sidebar entry's or sound event's name."""
    m = ENTRY_NAME["Tiles"].search(text) if root == "Tiles" else re.search(r'Name="([^"]+)"', text)
    return m.group(1).upper() if m else None


def replace_in_pack(cur, chunks, root, entry_re):
    """A pack file with the incoming chunks in place of what they supersede.

    A generated BEGIN/END block replaces the block with the same BEGIN line; loose entries
    replace every entry with the same key. Pack scripts rewrite an object whole, so this keeps
    a re-split after re-running one from duplicating anything.
    """
    loose = []
    for chunk in chunks:
        b = BLOCK.match(chunk)
        if b and b.end() == len(chunk):
            begin = chunk[:chunk.index("-->") + 3].strip()
            old = next((m for m in BLOCK.finditer(cur) if m.group(0).strip().startswith(begin)), None)
            if old:
                cur = cur[:old.start()] + chunk + cur[old.end():]
                continue
        loose.append(chunk)
    keys = {entry_key(root, e.group(0)) for c in loose for e in entry_re.finditer(c)} - {None}
    if keys:
        cur = entry_re.sub(lambda e: "" if entry_key(root, e.group(0)) in keys else e.group(0), cur)
    cut = cur.rindex(f"</{root}>")
    return cur[:cut] + "".join(loose) + cur[cut:]


def split_xml(rel, pack_file, root, entry_re, dry_run=False):
    """Move one mod XML file's pack entries into the packs' files, leaving a marker for each pack.

    Entries keep their text. A generated BEGIN/END block whose entries all move to one pack
    moves whole, so the script that regenerates it finds it in the pack file. Returns
    {pack: entry count}.
    """
    path = os.path.join(MOD, "Data", rel)
    text = open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in text else "\n"
    blocks = []
    for b in BLOCK.finditer(text):
        owners = {entry_pack(root, e.group(0)) for e in entry_re.finditer(b.group(2))}
        if len(owners) == 1 and None not in owners:
            blocks.append((b.start(), b.end(), owners.pop()))
    moved, out, pos, seen = {}, [], 0, set()
    spans = [(s, e, p, text[s:e]) for s, e, p in blocks]
    i = 0
    for m in entry_re.finditer(text):
        if any(s <= m.start() < e for s, e, _ in blocks):
            continue
        p = entry_pack(root, m.group(0))
        if p:
            spans.append((m.start(), m.end(), p, m.group(0)))
    spans.sort()
    for s, e, p, chunk in spans:
        out.append(text[pos:s])
        if p not in seen:
            indent = re.match(r"[ \t]*", chunk).group(0)
            out.append(f"{indent}{marker(p)}{nl}")
            seen.add(p)
        moved.setdefault(p, []).append(chunk)
        pos = e
    out.append(text[pos:])
    if not moved:
        return {}
    head = re.match(r".*?<%s\b[^>]*>[ \t]*\r?\n" % root, text, re.S).group(0)
    tail = text[text.rindex(f"</{root}>"):]
    counts = {}
    for p, chunks in moved.items():
        counts[p] = sum(len(list(entry_re.finditer(c))) for c in chunks)
        if dry_run:
            continue
        dst = pack_file(p)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            body = replace_in_pack(open(dst, encoding="utf-8", newline="").read(), chunks, root, entry_re)
        else:
            body = head + "".join(chunks) + tail
        open(dst, "w", encoding="utf-8", newline="").write(body)
    if not dry_run:
        new = "".join(out)
        # a marker already present from an earlier split is kept once
        for p in moved:
            first = new.find(marker(p))
            new = new[:first + 1] + re.sub(r"[ \t]*" + re.escape(marker(p)) + r"[ \t]*\r?\n", "", new[first + 1:])
        open(path, "w", encoding="utf-8", newline="").write(new)
    return counts


def mod_files():
    """Every file of the mod's own tree, relative to its Data/ folder."""
    base = os.path.join(MOD, "Data")
    for dirpath, _, files in os.walk(base):
        for f in files:
            yield os.path.relpath(os.path.join(dirpath, f), base)


def file_pack(rel):
    """The pack a file under Data/ belongs to, or None."""
    parts = rel.replace("\\", "/").split("/")
    name = parts[-1]
    if parts[:4] == ["ART", "TEXTURES", "SRGB", "RED_ALERT"] and name.upper().endswith(".ZIP"):
        return graphics_pack(name[:-4])
    if parts[:3] == ["ART", "TEXTURES", "SRGB"] and len(parts) == 4 and name.lower().startswith("buildicon_"):
        return cameo_pack(name)
    if parts[0] == "AUDIO" and name.upper().endswith(".WAV"):
        return sound_pack(name)
    return None


def split(dry_run=False):
    """Move every pack file and XML entry still in the mod's own tree into its pack."""
    moved = {}
    for rel in sorted(mod_files()):
        p = file_pack(rel)
        if p:
            moved.setdefault(p, [0, 0])
            moved[p][0] += 1
            if not dry_run:
                dst = os.path.join(pack_data(p), rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                os.replace(os.path.join(MOD, "Data", rel), dst)
    for rel, pack_file, root, entry_re in XML_FILES:
        for p, n in split_xml(rel, pack_file, root, entry_re, dry_run).items():
            moved.setdefault(p, [0, 0])
            moved[p][1] += n
    return moved


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd in ("required", "used"):
        print("\n".join(REQUIRED if cmd == "required" else USED))
        raise SystemExit(0)
    if cmd not in ("split", "check"):
        raise SystemExit("usage: asset_packs.py split | check | required | used")
    found = split(dry_run=(cmd == "check"))
    for p in PACKS:
        if p in found:
            print(f"{p:22s} {found[p][0]:5d} files {found[p][1]:6d} XML entries")
    if cmd == "check" and found:
        raise SystemExit("pack assets are still in the mod's own tree: run scripts/asset_packs.py split")
