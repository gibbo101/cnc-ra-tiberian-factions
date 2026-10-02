#!/usr/bin/env python3
"""Write each asset pack's ccmod.json and README.md from what the pack holds.

Usage:  asset_pack_docs.py

The README lists the pack's objects and sounds, says which of the mod's files its XML entries go
into, and credits the source game. Run it after adding to or removing from a pack.

License: GPL v3.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs as A  # noqa: E402

REPO_URL = "https://github.com/gibbo101/cnc-ra-tiberian-factions"

MORE_MODS = [
    "**Tiberian Factions** adds GDI and Nod as playable factions to Red Alert Remastered: "
    "[Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253), "
    "[ModDB](https://www.moddb.com/mods/tiberian-factions-for-red-alert), "
    f"[GitHub]({REPO_URL})",
    "**OpenTS Pad** ports the OpenTS rebuild of Tiberian Sun to Linux and the Steam Deck, with "
    "controller play: [GitHub](https://github.com/gibbo101/opents-pad)",
    "**Renegade Pad** brings controller play to C&C Renegade (an OpenW3D fork, built for the Steam Deck): "
    "[GitHub](https://github.com/gibbo101/renegade-pad)",
    "**C&C Map Editor** is a Linux-native, mod-aware map editor for C&C Remastered (Red Alert and "
    "Tiberian Dawn): [GitHub](https://github.com/gibbo101/cnc-map-editor)",
    "**PS1 Link Cable** plays two-player link-cable PS1 games such as C&C Retaliation between two "
    "Steam Decks over LAN: [GitHub](https://github.com/gibbo101/ps1-lan-link)",
    "**Steam Workshop Uploader** publishes Workshop items natively on Linux; it is how these packs "
    "ship: [GitHub](https://github.com/gibbo101/steam-workshop-uploader)",
]

GAMES = {
    "TS": "Tiberian Sun",
    "RA2": "Red Alert 2",
    "CNC3": "Command & Conquer 3: Tiberium Wars",
}

ABOUT = {
    "TS-Graphics-Pack": "Tiberian Sun units, structures, effects and sidebar cameos as HD sprites",
    "TS-HD-Graphics-Pack": "Tiberian Sun GDI buildings, units, walls, gates and component towers, rebuilt as HD art",
    "TS-SFX-Pack": "Tiberian Sun weapon, unit and structure sound effects",
    "TS-EVA-eng": "Tiberian Sun EVA announcer lines (English)",
    "TS-Voices-eng": "Tiberian Sun unit voice lines (English)",
    "RA2-Graphics-Pack": "Red Alert 2 units and sidebar cameos as HD sprites",
    "RA2-SFX-Pack": "Red Alert 2 weapon and engine sound effects",
    "RA2-Voices-eng": "Red Alert 2 unit voice lines (English)",
    "CNC3-Graphics-Pack": "Command & Conquer 3 units and sidebar cameos as HD sprites",
    "CNC3-SFX-Pack": "Command & Conquer 3 weapon sound effects",
    "CNC3-Voices-eng": "Command & Conquer 3 unit voice lines (English)",
}

CREDIT = {
    "TS-HD-Graphics-Pack": "Built from Tiberian Sun's designs by gibbo101 for Tiberian Factions.",
}

KIND_LABEL = {"UNITS": "Units", "STRUCTURES": "Structures", "VFX": "Effects",
              "TERRAIN_TEMPERATE": "Terrain (temperate)", "TERRAIN_SNOW": "Terrain (snow)",
              "TERRAIN_INTERIOR": "Terrain (interior)"}


def listing(pack):
    """Section title -> sorted names, from the pack's files."""
    data = A.pack_data(pack)
    out = {}
    for kind in A.KINDS:
        d = os.path.join(data, "ART", "TEXTURES", "SRGB", "RED_ALERT", A.kind_dir(kind))
        if os.path.isdir(d):
            names = sorted(f[:-4] for f in os.listdir(d) if f.upper().endswith(".ZIP"))
            if names:
                out[KIND_LABEL[kind]] = names
    srgb = os.path.join(data, "ART", "TEXTURES", "SRGB")
    if os.path.isdir(srgb):
        icons = sorted(f[:-4] for f in os.listdir(srgb) if f.lower().endswith(".tga"))
        if icons:
            out["Sidebar cameos"] = icons
    for sub, label in ((os.path.join("AUDIO", "EN-US"), "Sounds (localised, Data/AUDIO/EN-US)"),
                       ("AUDIO", "Sounds (Data/AUDIO)")):
        d = os.path.join(data, sub)
        if os.path.isdir(d):
            names = sorted(f[:-4] for f in os.listdir(d) if f.upper().endswith(".WAV"))
            if names:
                out[label] = names
    return out


def models_of(pack):
    """The pack's 3D models (asset-packs/<Pack>/3d/*.glb), by name."""
    d = os.path.join(A.PACKS_DIR, pack, "3d")
    if not os.path.isdir(d):
        return []
    return sorted(f[:-4] for f in os.listdir(d) if f.lower().endswith(".glb"))


def xml_targets(pack):
    """(pack XML path relative to the pack, the mod file its entries go into)."""
    rows = []
    for rel, pack_file, _, _ in A.XML_FILES:
        f = pack_file(pack)
        if os.path.exists(f):
            rows.append((os.path.relpath(f, os.path.join(A.PACKS_DIR, pack)).replace(os.sep, "/"),
                         "Data/" + rel.replace(os.sep, "/")))
    return rows


def readme(pack):
    game = GAMES[A.PACKS[pack].replace("TSHD", "TS")]
    lines = [f"# {pack}", "",
             f"{ABOUT[pack]}, for Command & Conquer Remastered Collection mods (Red Alert). One of the "
             f"asset packs from [Tiberian Factions]({REPO_URL}).", ""]
    lines += ["## Contents", ""]
    for title, names in listing(pack).items():
        lines.append(f"**{title}** ({len(names)}): " + ", ".join(names))
        lines.append("")
    models = models_of(pack)
    if models:
        lines.append(f"**3D models** ({len(models)}): " + ", ".join(models) + ". The HD rebuilds as glTF models, "
                     "in `3d/`; `3d/README.md` lists their parts and conventions. The game does not use them.")
        lines.append("")
    lines += ["## Using it", "",
              "1. Copy the files under this pack's `Data/` folder into your mod's `Data/` folder, keeping the paths.",
              "2. Copy the entries you need from this pack's XML files into your mod's own XML files:", ""]
    lines += [f"   - `{src}` into `{dst}`" for src, dst in xml_targets(pack)]
    lines += ["",
              "   The launcher only reads the mod files on the right. This pack's own XML files are there to copy from, "
              "so enabling the pack by itself changes nothing in game.", ""]
    if "Graphics" in pack:
        lines += ["3. The game also needs a classic-mode SHP for every sprite, with the same frame count. A transparent stub "
                  f"is enough: Tiberian Factions makes its stubs with `scripts/gen_stub_shp.py` ([repo]({REPO_URL})).",
                  "4. Units with one frame per facing, plus a turret block where they have one, use the stock layout. Units "
                  "with rolling treads, walking gaits or offset turrets use Tiberian Factions' own layouts and need the "
                  "matching DLL code, which is in the repo.",
                  ""]
    lines += ["## Credits", "",
              f"Original {game} assets: Electronic Arts. Prepared for Remastered by gibbo101 for Tiberian Factions."]
    if pack in CREDIT:
        lines += ["", CREDIT[pack]]
    lines += ["", "## More C&C projects by gibbo101", ""]
    lines += [f"- {m}" for m in MORE_MODS]
    lines.append("")
    return "\n".join(lines)


def ccmod(pack):
    return {
        "name": pack,
        "description": ABOUT[pack] + ", for Red Alert Remastered mods.",
        "author": "gibbo101",
        "load_order": 2,
        "version_high": 1,
        "version_low": 0,
        "game_type": "RA",
    }


def main():
    for pack in A.PACKS:
        root = os.path.join(A.PACKS_DIR, pack)
        if not os.path.isdir(root):
            continue
        with open(os.path.join(root, "ccmod.json"), "w") as fh:
            json.dump(ccmod(pack), fh, indent=4)
            fh.write("\n")
        with open(os.path.join(root, "README.md"), "w") as fh:
            fh.write(readme(pack))
        print(f"wrote {pack}/ccmod.json, README.md")


if __name__ == "__main__":
    main()
