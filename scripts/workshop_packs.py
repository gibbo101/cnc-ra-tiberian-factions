#!/usr/bin/env python3
"""Build the Workshop asset-pack mods (asset_packs.WORKSHOP) from the asset-packs/ source folders.

Usage:  workshop_packs.py <out dir> [mod ...]   (every Workshop pack when none is named)

Each mod is a data-only Red Alert mod folder: ccmod.json, README.md, every file of its source packs
under Data/ART and Data/AUDIO (a later pack's copy of a path wins), and its XML: one file per
launcher XML, the source packs' entries together, complete on their own (no ZIP shared with another
mod); a DLL mod copies the entries into its own XML. A pack Tiberian Factions requires also
carries its marker in CCDATA, which the mod's DLL reads to know the pack is enabled.

scripts/stage_asset_packs.py builds the required packs beside the staged mod the same way.

License: GPL v3.
"""
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs as A  # noqa: E402
import asset_pack_docs as D  # noqa: E402

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


def copy_newer(src, dst):
    """Copy unless dst already has src's size and mtime."""
    if os.path.exists(dst):
        a, b = os.stat(src), os.stat(dst)
        if a.st_size == b.st_size and int(a.st_mtime) == int(b.st_mtime):
            return dst
    return shutil.copy2(src, dst)


def copy_binaries(mod, folder):
    """Every file under the mod's source packs' Data/ART and Data/AUDIO; a later pack's copy of a path wins."""
    packs = A.WORKSHOP[mod]["packs"]
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
                    dst = os.path.join(folder, "Data", sub, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    copy_newer(os.path.join(d, f), dst)


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


def write_xml(mod, folder):
    """The mod's XML files; returns {launcher XML: the pack's file name}."""
    files = {}
    for rel, pack_file, root, _ in A.XML_FILES:
        sub, pattern = XML_NAMES[rel]
        text = combined_xml(mod, rel, pack_file, root)
        if text is None:
            continue
        name = pattern.format(id=A.WORKSHOP[mod]["xml_id"])
        write_if_changed(os.path.join(folder, "Data", "XML", sub, name), text)
        files[rel] = name
    return files


def write_manifest(mod, folder):
    """ccmod.json, and for a pack Tiberian Factions requires, the CCDATA marker carrying its version."""
    w = A.WORKSHOP[mod]
    high, low = w["version"]
    manifest = {"name": w["name"], "description": w["description"], "author": "gibbo101", "load_order": 2,
                "version_high": high, "version_low": low, "game_type": "RA"}
    write_if_changed(os.path.join(folder, "ccmod.json"), json.dumps(manifest, indent=4) + "\n")
    if w.get("marker"):
        write_if_changed(os.path.join(folder, "CCDATA", w["marker"]),
                         f"[Pack]\nName={mod}\nVersion={high}.{low}\n")


GAME = {"TS": "Tiberian Sun", "RA2": "Red Alert 2", "CNC3": "Command & Conquer 3: Tiberium Wars"}
TF_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253"
EA_EXAMPLE_URL = "https://github.com/electronicarts/CnC_Remastered_Collection/blob/master/REDALERT/ADATA.CPP#L2590"


def contents(mod):
    """Section title -> sorted names across the mod's source packs."""
    out = {}
    for pack in A.WORKSHOP[mod]["packs"]:
        for title, names in D.listing(pack).items():
            out.setdefault(title, set()).update(names)
    return {title: sorted(names) for title, names in out.items()}


def readme(mod, listed):
    """The pack's README.md: what it is, how players and modders use it, contents and credits."""
    w = A.WORKSHOP[mod]
    game = GAME[w["game"]]
    lines = [f"# {w['name']}", "", w["description"] + " Built for Command & Conquer Remastered Collection.", "",
             "This is an asset pack: on its own it adds nothing to the game. A mod has to use it.", ""]
    if w["required"]:
        lines += ["## Playing Tiberian Factions", "",
                  f"[Tiberian Factions]({TF_URL}) needs this pack for its {game} factions.", "",
                  "1. Subscribe to Tiberian Factions and to this pack.",
                  "2. In the game's Mods menu, enable both.",
                  "3. Restart the game: the game only picks up a change to enabled mods after a restart.", "",
                  f"Without the pack, Tiberian Factions still plays, but its {game} factions are locked.", ""]
    lines += ["If the game crashes on the splash screen, the extra art needs more video memory than it has: add "
              "`NOSPLASHPRELOAD` to the game's launch options.", ""]
    lines += ["## Using the assets in your own mod", "",
              f"Every object, cameo and sound is named with the `{w["prefix"]}` prefix, so nothing clashes with the "
              "base game's own assets.", "",
              "Enable this pack beside your mod (the game finds its art and sounds in any enabled mod) and copy "
              "the entries you need from this pack's `Data/XML` files into your mod's "
              "`RA_*.XML`, `RABUILDABLES.XML` and `SFXEVENTS*.XML`. Each object needs a classic-mode SHP with the "
              "same frame count (a transparent stub is enough) and its `ImageData` set in your DLL's `Init` or "
              f"`One_Time` ([EA's example]({EA_EXAMPLE_URL})).", ""]
    if w["game"] == "TS":
        lines += ["Most units use the stock layout: one frame per facing, then a turret block where they have one. "
                  "Walkers, units with rolling treads or offset turrets, and buildings with doors, docks or add-ons "
                  "use Tiberian Factions' own layouts and need the matching DLL code, which is in its "
                  f"[source]({D.REPO_URL}).", ""]
    lines += ["## Contents", ""]
    for title, names in contents(mod).items():
        lines += [f"**{title}** ({len(names)}): " + ", ".join(names), ""]
    lines += ["XML files: " + ", ".join(f"`{n}`" for n in sorted(listed.values())) + ".", ""]
    lines += ["## AI disclosure", ""]
    if w["game"] in ("TS", "RA2"):
        lines += ["The HD art in this pack was made with AI assistance. The 3D models behind the sprites were built "
                  "and refined with AI tools, then rendered, checked and fitted to the game by hand, and every asset "
                  "was reviewed in play before release."]
    else:
        lines += ["These sprites were rendered from the game's own 3D models; no AI generated the art."]
    lines += ["The scripts and tools that build this pack, and Tiberian Factions' code, were written with AI "
              "assistance. The original designs, sounds and voices are Westwood's and Electronic Arts'.", ""]
    lines += ["## Credits", "", f"Original {game} art and sounds: Electronic Arts."]
    if w["game"] in ("TS", "RA2"):
        lines += [f"HD rebuilds of the {game} designs and preparation for Remastered: gibbo101."]
    else:
        lines += ["Rendered for Remastered from the game's own models by gibbo101."]
    lines += ["", "## More C&C projects by gibbo101", ""] + [f"- {m}" for m in D.MORE_MODS] + [""]
    return "\n".join(lines)


def build(mod, folder):
    """The whole Workshop folder for one asset-pack mod."""
    write_manifest(mod, folder)
    copy_binaries(mod, folder)
    listed = write_xml(mod, folder)
    write_if_changed(os.path.join(folder, "README.md"), readme(mod, listed))


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    out, mods = argv[0], argv[1:] or list(A.WORKSHOP)
    for mod in mods:
        if mod not in A.WORKSHOP:
            raise SystemExit(f"not a Workshop pack: {mod}")
        build(mod, os.path.join(out, mod))
        print(f"built {os.path.join(out, mod)}")


if __name__ == "__main__":
    main(sys.argv[1:])
