#!/usr/bin/env python3
"""Generate faction-badged sidebar cameos for every buildable.

The sidebar badges a cameo with the emblems of whichever of the PLAYER'S
factions can build it, so a badge always answers "which of my factions makes
this". That set is only known at runtime, so this tool bakes one cameo per
possible emblem combination and the DLL picks between them by writing the
matching key into CNCSidebarEntryStruct::AssetName.

Pristine art comes from the launcher's UI atlas, MT_COMMANDBAR_COMMON.TGA in
TEXTURES_SRGB.MEG, whose .MTD sidecar maps region-name -> (x, y, w, h). Cameos
exist ONLY as regions of that atlas; there is no per-cameo file anywhere in the
game install. Rebuilding from the atlas every run is what keeps this idempotent
-- re-badging an already-badged file would stack emblems.

Naming, kept inside AssetName[16]:
  buildables    <IniName>_<mask>     e.g. TDNUKE_C
  superweapons  S<mask>_<rest>       e.g. SC_TDNUKE   (prefix swap, same length)
where <mask> is a hex digit of the faction bits below. The unbadged case is not
generated: those entries point straight at the base atlas region, which costs
no disk at all.

Usage: scripts/cameo_badge_build.py [--dry-run] [ININAME ...]

License: GPL v3.
"""
import json
import re
import struct
import sys
from itertools import combinations
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "scripts/cameo_work"
EMBLEMS = ROOT / "scripts/tab_emblems"
OUT = ROOT / "resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB"
RULES = ROOT / "resources/remaster_mods/Vanilla_RA/CCDATA/rules.ini"
MASKS = WORK / "faction_masks.txt"
XML = ROOT / "resources/remaster_mods/Vanilla_RA/Data/XML/OBJECTS/UNITS/RABUILDABLES.XML"
ICON_MAP = WORK / "plain_icon_map.json"
ATLAS = WORK / "MT_COMMANDBAR_COMMON.TGA"
MTD = WORK / "MT_COMMANDBAR_COMMON.MTD"

# Faction bit -> (rules.ini Owner token, emblem art). Order defines the order
# emblems are drawn in, matching the existing badged cameos.
FACTIONS = [
    (0x1, "allies", "allied.png"),
    (0x2, "soviet", "soviet.png"),
    (0x4, "GoodGuy", "gdi.png"),
    (0x8, "BadGuy", "nod.png"),
]

# Measured from the shipped badged cameos against their pristine atlas crops.
# EMBLEM_SIZE / EMBLEM_SPACING are the one- to three-emblem layout; four emblems
# scale down to stay inside the cameo (see emblem_layout) so a fourth crest is
# never clipped off the right edge.
EMBLEM_SIZE = 90
EMBLEM_ORIGIN = (12, 12)
EMBLEM_SPACING = 96
EMBLEM_GAP = EMBLEM_SPACING - EMBLEM_SIZE


def emblem_layout(count, cameo_width):
    """(size, spacing) for `count` emblems that fits inside cameo_width.

    Keeps the base size until the row would overrun, then shrinks size and the
    proportional gap together so every emblem stays fully on the cameo.
    """
    avail = cameo_width - 2 * EMBLEM_ORIGIN[0]
    gap_ratio = EMBLEM_GAP / EMBLEM_SIZE
    size = min(EMBLEM_SIZE, avail / (count + (count - 1) * gap_ratio))
    size = int(size)
    spacing = int(round(size * (1 + gap_ratio)))
    return size, spacing


def load_regions():
    """region-name -> (x, y, w, h) from the atlas .MTD sidecar."""
    raw = MTD.read_bytes()

    def lookup(name):
        key = name.upper().encode() + b".TGA"
        i = raw.find(key)
        if i < 0:
            return None
        p = i + len(key)
        while p < len(raw) and raw[p] == 0:  # trailing null padding, 1-2 bytes
            p += 1
        return struct.unpack_from("<4i", raw, p)

    return lookup


def owner_sets():
    """IniName -> faction bitmask, from the runtime dump (authoritative).

    tf_faction_masks.txt is written by TF_Dump_Faction_Masks in a dev build:
    each type's mask straight from Get_Ownable(), collapsed to the four faction
    bits by the SAME function the DLL uses at runtime. Reading it here is what
    guarantees the baked art covers exactly the keys the DLL will request -- the
    faction-split types carry their ownership in C++ defaults, not rules.ini, so
    this is the only complete and drift-free source.
    """
    out = {}
    for line in MASKS.read_text(encoding="utf-8", errors="replace").splitlines():
        if "\t" not in line:
            continue
        name, mask = line.split("\t", 1)
        try:
            m = int(mask)
        except ValueError:
            continue
        if m:
            out[name.strip().upper()] = m
    return out


def pristine_sources(plain):
    """Entry name -> the unbadged art it should be built from.

    Entries that were repointed when the cameos were first badged take their
    ORIGINAL icon name from the map; their current loose file is already badged
    and would stack emblems. Everything else is still pointing at unbadged art,
    so its current BuildIcon is the pristine source.
    """
    xml = XML.read_text(encoding="utf-8")
    xml = re.sub(
        r"\t<!-- BEGIN generated.*?END generated unbadged cameo variants -->\n?", "", xml, flags=re.S
    )
    out = {}
    for m in re.finditer(
        r'<ObjectTypeClass Name="(RA_[A-Za-z0-9_]+)" Classification="CNCBuildableObject".*?</ObjectTypeClass>',
        xml,
        re.S,
    ):
        icon = re.search(r"<BuildIcon>([^<]+)</BuildIcon>", m.group(0))
        if icon:
            out[m.group(1)] = plain.get(m.group(1), icon.group(1).strip())
    return out


def variant_key(asset, mask):
    """The AssetName the DLL writes to request this emblem combination."""
    digit = "%X" % mask
    if asset.startswith("SW_"):
        return "S" + digit + "_" + asset[3:]
    return asset + "_" + digit


def subsets(mask):
    """Every non-empty subset of a faction bitmask."""
    bits = [b for b, _, _ in FACTIONS if mask & b]
    for size in range(1, len(bits) + 1):
        for combo in combinations(bits, size):
            yield sum(combo)


def main(argv):
    dry_run = "--dry-run" in argv
    wanted = {a.upper() for a in argv if not a.startswith("--")}

    for path in (ATLAS, MTD, ICON_MAP, MASKS):
        if not path.exists():
            sys.exit(
                f"ERROR: missing {path.name}. Extract the atlas first:\n"
                f"  python3 scripts/meg_extract.py extract "
                f"~/.steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_SRGB.MEG "
                f'"MT_COMMANDBAR_COMMON" {WORK}'
            )

    region = load_regions()
    owners = owner_sets()
    plain = json.loads(ICON_MAP.read_text(encoding="utf-8"))
    atlas = Image.open(ATLAS)
    sources = pristine_sources(plain)

    emblem_src = {bit: Image.open(EMBLEMS / filename).convert("RGBA") for bit, _, filename in FACTIONS}
    resized = {}

    def emblem(bit, size):
        key = (bit, size)
        if key not in resized:
            resized[key] = emblem_src[bit].resize((size, size), Image.LANCZOS)
        return resized[key]

    written = skipped = 0
    for entry_name, region_name in sorted(sources.items()):
        asset = entry_name[3:]  # strip the RA_ game prefix
        if wanted and asset not in wanted:
            continue

        mask = owners.get(asset)
        if mask is None:
            skipped += 1
            continue

        # Base cameos live only as atlas regions. Entities this mod added carry
        # their own loose art instead, which never went through the badger.
        box = region(region_name)
        if box is not None:
            x, y, w, h = box
            pristine = atlas.crop((x, y, x + w, y + h)).convert("RGBA")
        else:
            loose = OUT / f"{region_name}.tga"
            if not loose.exists():
                print(f"  WARN {asset}: no atlas region and no loose {region_name}.tga")
                skipped += 1
                continue
            pristine = Image.open(loose).convert("RGBA")

        for combo in subsets(mask):
            key = variant_key(asset, combo)
            if len(key) > 15:
                print(f"  WARN {asset}: key '{key}' exceeds AssetName[16], skipped")
                continue
            cameo = pristine.copy()
            count = bin(combo).count("1")
            size, spacing = emblem_layout(count, cameo.width)
            slot = 0
            for bit, _, _ in FACTIONS:
                if combo & bit:
                    cameo.alpha_composite(
                        emblem(bit, size),
                        (EMBLEM_ORIGIN[0] + slot * spacing, EMBLEM_ORIGIN[1]),
                    )
                    slot += 1
            if not dry_run:
                cameo.save(OUT / f"BuildIcon_{key}.tga")
            written += 1

    verb = "would write" if dry_run else "wrote"
    print(f"OK: {verb} {written} badged cameos ({skipped} entries skipped, no Owner= or region)")


if __name__ == "__main__":
    main(sys.argv[1:])
