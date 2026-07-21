#!/usr/bin/env python3
"""Parse every loose XML the mod ships, so a malformed one cannot reach a device.

The launcher does not skip a bad override -- it asserts and the game dies at startup
(`pglib\\xml.cpp:1227`). That is what a `--` inside an XML comment did to
GameConstants_Mod.xml on 2026-07-21: illegal in XML, fatal to the client, and invisible
until launch because plain resources are copied rather than built.

Files inherited from the game are checked too but only warned about: some ship
technically malformed (an unescaped '&' in a URL) and the game's own parser tolerates
them. Only files the mod authors are treated as errors, since those are the ones we
control and the ones that have broken.

Usage: validate_shipped_xml.py <resources-root> [more roots...]
"""
import os
import sys
import xml.dom.minidom

# Files we author or rewrite. Anything else came from the game and is advisory only.
OURS = (
    "gameconstants_mod.xml",
)


def main(roots):
    errors, warnings, checked = [], [], 0
    for root in roots:
        for dirpath, _dirnames, filenames in os.walk(root):
            for name in sorted(filenames):
                if not name.lower().endswith(".xml"):
                    continue
                path = os.path.join(dirpath, name)
                checked += 1
                try:
                    xml.dom.minidom.parse(path)
                except Exception as exc:
                    (errors if name.lower() in OURS else warnings).append((path, exc))

    for path, exc in warnings:
        print(f"  warn (game-inherited): {path}: {exc}")
    for path, exc in errors:
        print(f"  ERROR: {path}: {exc}")

    print(f"validated {checked} XML files: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
