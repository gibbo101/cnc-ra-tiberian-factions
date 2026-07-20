#!/usr/bin/env python3
"""Generate the faction-mask sidebar cameo variants in RABUILDABLES.XML.

Every buildable gets a sibling ObjectTypeClass per faction-badge combination it
can display. The DLL writes `<IniName>_<hex>` into CNCSidebarEntryStruct::
AssetName on each sidebar refresh, where <hex> is the set of the player's own
factions that can build the entry (0 = none, so no emblems). The launcher then
resolves that key to the matching baked cameo.

  <hex> bit values: Allied=1, Soviet=2, GDI=4, Nod=8. So TDNUKE_C = GDI+Nod,
  SBAG_5 = Allied+GDI, POWR_0 = pristine Power Plant with no badge.

For each entry the emitted variants are:
  _0                          -> the pristine (unbadged) cameo
  _<S> for every non-empty S  -> the baked cameo carrying S's emblems,
       subset of the entry's      art produced by scripts/cameo_badge_build.py
       owner mask

Owner masks come from the runtime dump scripts/cameo_work/faction_masks.txt
(see cameo_badge_build.py) so XML, art, and the DLL all agree. Pristine icon
names come from scripts/cameo_work/plain_icon_map.json.

Idempotent. Re-running replaces the generated block rather than stacking it.

License: GPL v3.
"""
import json
import re
import struct
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XML = ROOT / "resources/remaster_mods/Vanilla_RA/Data/XML/OBJECTS/UNITS/RABUILDABLES.XML"
MAP = ROOT / "scripts/cameo_work/plain_icon_map.json"
MASKS = ROOT / "scripts/cameo_work/faction_masks.txt"
MTD = ROOT / "scripts/cameo_work/MT_COMMANDBAR_COMMON.MTD"
ART = ROOT / "resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB"

FACTION_BITS = [0x1, 0x2, 0x4, 0x8]

BEGIN = "\t<!-- BEGIN generated cameo mask variants (scripts/cameo_variants_build.py) -->"
END = "\t<!-- END generated cameo mask variants -->"

TEMPLATE = """\t<ObjectTypeClass Name="{name}" Classification="CNCBuildableObject" CanInstantiate="False">
\t\t<CNCEncyclopediaComponent>
\t\t\t<ObjectNameTextID>{text_id}</ObjectNameTextID>
\t\t\t<ObjectDescriptionTextID>{desc_id}</ObjectDescriptionTextID>
\t\t\t<BuildIcon>{icon}</BuildIcon>
\t\t</CNCEncyclopediaComponent>
\t</ObjectTypeClass>
"""


def art_resolver():
    """Return a predicate: does this BuildIcon name resolve to real art?

    Real = a named region in the launcher UI atlas, or a loose .tga this mod
    ships. An entry whose pristine art resolves to neither cannot render, so its
    variants are omitted rather than left as dangling references.
    """
    raw = MTD.read_bytes()

    def resolves(icon):
        if raw.find(icon.upper().encode() + b".TGA") >= 0:
            return True
        return (ART / f"{icon}.tga").exists()

    return resolves


def load_masks():
    out = {}
    for line in MASKS.read_text(encoding="utf-8", errors="replace").splitlines():
        if "\t" not in line:
            continue
        name, mask = line.split("\t", 1)
        try:
            out[name.strip().upper()] = int(mask)
        except ValueError:
            pass
    return out


def subsets(mask):
    bits = [b for b in FACTION_BITS if mask & b]
    for size in range(1, len(bits) + 1):
        for combo in combinations(bits, size):
            yield sum(combo)


def main():
    xml = XML.read_text(encoding="utf-8")
    plain = json.loads(MAP.read_text(encoding="utf-8"))
    masks = load_masks()
    resolves = art_resolver()

    # Drop any previously generated block so re-runs never stack. Matches both
    # this generator's block and the earlier "unbadged cameo variants" block it
    # superseded.
    xml = re.sub(
        r"\t<!-- BEGIN generated (?:unbadged cameo variants|cameo mask variants).*?"
        r"<!-- END generated (?:unbadged cameo variants|cameo mask variants) -->\n?",
        "",
        xml,
        flags=re.S,
    )

    blocks = []
    for m in re.finditer(
        r'<ObjectTypeClass Name="(RA_[A-Za-z0-9_]+)" Classification="CNCBuildableObject".*?</ObjectTypeClass>',
        xml,
        re.S,
    ):
        entry_name = m.group(1)
        src = m.group(0)
        current_icon = re.search(r"<BuildIcon>([^<]*)</BuildIcon>", src)
        text_id = re.search(r"<ObjectNameTextID>([^<]*)</ObjectNameTextID>", src)
        desc_id = re.search(r"<ObjectDescriptionTextID>([^<]*)</ObjectDescriptionTextID>", src)
        if not (current_icon and text_id and desc_id):
            continue

        asset = entry_name[3:]  # strip the RA_ game prefix

        # Superweapons resolve their cameo through a separate DLL path
        # (Convert_Special_Weapon_Type sets a bespoke AssetName), and their long
        # IniNames overflow the mask suffix. They keep their existing badges.
        if asset.startswith("SW_"):
            continue

        pristine = plain.get(entry_name, current_icon.group(1).strip())

        # No renderable pristine art (e.g. a spawn-only type never on the
        # sidebar) -> emit nothing, so RABUILDABLES carries no dangling icon ref.
        if not resolves(pristine):
            continue

        def add(suffix, icon):
            key = "RA_" + asset + "_" + suffix
            if len(asset) + len(suffix) + 1 > 15:
                sys.exit(f"ERROR: variant key '{asset}_{suffix}' exceeds AssetName[16]")
            blocks.append(
                TEMPLATE.format(
                    name=key,
                    text_id=text_id.group(1),
                    desc_id=desc_id.group(1),
                    icon=icon,
                )
            )

        # _0 is always the pristine cameo. Baked emblem variants exist only for
        # the entry's owner subsets; an entry with no owner mask gets _0 alone.
        add("0", pristine)
        for combo in subsets(masks.get(asset, 0)):
            icon = f"BuildIcon_{asset}_{combo:X}"
            if resolves(icon):
                add("%X" % combo, icon)

    generated = BEGIN + "\n" + "\n".join(blocks) + END + "\n"
    if "</ObjectTypeList>" not in xml:
        sys.exit("ERROR: root close tag </ObjectTypeList> not found")
    xml = xml.replace("</ObjectTypeList>", generated + "\n</ObjectTypeList>", 1)

    XML.write_text(xml, encoding="utf-8")
    print(f"OK: wrote {len(blocks)} cameo mask-variant entries into {XML.name}")


if __name__ == "__main__":
    main()
