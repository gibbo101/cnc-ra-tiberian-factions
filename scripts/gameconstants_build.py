#!/usr/bin/env python3
"""Build our edited GAMECONSTANTS.XML from the pristine base copy.

Three edits are applied:

1. CFE Patch Redux's "Pixel-Perfect Zoom" factors (11 zoom steps,
   0.246875-1.975, vs vanilla's 8 steps 1.0-2.0). Values are bleid's,
   incorporated by ChthonVII in CFE commit ea2dde5. GPL v3.
2. `CNCDisableLegacyGraphicsOption` True — EA's mod-facing switch that denies
   players the legacy (classic) renderer. The mod is HD-only; its TD content
   has no classic art path.
3. `CNCEnableModHotKeyGameCommands` True — turns on the four modder hotkey
   commands bound by scripts/inputtranslator_build.py.

The output is kept at EXACTLY the base byte size so the same artifact can be
repacked into the mod's CONFIG.MEG (launcher reads inner files at base
offsets; any size change = boot crash — see docs/config-meg-mod-delivery.md).
Size is reclaimed by trimming asterisks from decorative comment banner lines,
which the XML parser ignores. The identical file also ships loose at
Data/XML/GAMECONSTANTS.XML (CFE's proven delivery path).

Usage: gameconstants_build.py <base.xml> <out.xml>
"""
import re
import sys
from xml.dom import minidom

ZOOM_FACTORS = [
    "0.246875", "0.37", "0.49375", "0.74", "0.9875", "1.11",
    "1.234375", "1.48", "1.728125", "1.85", "1.975",
]

# Whitespace inside the element is padding: the replacement is byte-for-byte
# the same length as the original, so it costs nothing against the size budget.
LEGACY_OPTION_OLD = b'<CNCDisableLegacyGraphicsOption network="client"> False </CNCDisableLegacyGraphicsOption>'
LEGACY_OPTION_NEW = b'<CNCDisableLegacyGraphicsOption network="client"> True  </CNCDisableLegacyGraphicsOption>'

# Enables GAME_COMMAND_CNC_MOD_COMMAND_1..4, which scripts/inputtranslator_build.py binds
# to keys and dllinterface.cpp handles.
MODKEYS_OPTION_OLD = b'<CNCEnableModHotKeyGameCommands network="client"> False </CNCEnableModHotKeyGameCommands>'
MODKEYS_OPTION_NEW = b'<CNCEnableModHotKeyGameCommands network="client"> True  </CNCEnableModHotKeyGameCommands>'



def main(base_path, out_path):
    data = open(base_path, "rb").read()
    base_len = len(data)

    for old, new, what in ((LEGACY_OPTION_OLD, LEGACY_OPTION_NEW, "legacy-graphics"),
                           (MODKEYS_OPTION_OLD, MODKEYS_OPTION_NEW, "mod-hotkey")):
        assert len(new) == len(old)
        assert data.count(old) == 1, f"{what} option not found in base"
        data = data.replace(old, new)

    start = data.find(b'<CNCZoomFactors network="client">')
    assert start != -1, "zoom block not found in base"
    start -= 2  # leading \t\t
    assert data[start:start + 2] == b"\t\t"
    end = data.find(b"</CNCZoomFactors>", start) + len(b"</CNCZoomFactors>")
    old_block = data[start:end]
    assert old_block.count(b"<ZoomFactor>") == 8, "base zoom block changed?"

    lines = [b'\t\t<CNCZoomFactors network="client" overwrite="true">']
    lines += [b"\t\t\t<ZoomFactor>" + v.encode() + b"</ZoomFactor>" for v in ZOOM_FACTORS]
    lines += [b"\t\t</CNCZoomFactors>"]
    new_block = b"\r\n".join(lines)

    data = data[:start] + new_block + data[end:]
    delta = len(data) - base_len
    assert delta >= 0, "new block smaller than old; padding not implemented"

    # Reclaim `delta` bytes from comment banner lines (runs of asterisks),
    # longest first, always leaving at least 10 asterisks per line.
    while delta > 0:
        runs = sorted(
            (m for m in re.finditer(rb"\*{11,}", data)),
            key=lambda m: m.end() - m.start(),
            reverse=True,
        )
        assert runs, "ran out of banner asterisks to trim"
        m = runs[0]
        take = min(delta, (m.end() - m.start()) - 10)
        data = data[: m.start()] + data[m.start() + take:]
        delta -= take

    assert len(data) == base_len, f"size mismatch: {len(data)} != {base_len}"
    # The BASE file is not strictly well-formed (unescaped '&' in a URL the
    # game's parser tolerates), so validate only the block we inserted.
    minidom.parseString(new_block)
    assert data.count(b"<ZoomFactor>") == len(ZOOM_FACTORS)
    assert data.count(LEGACY_OPTION_NEW) == 1
    assert data.count(MODKEYS_OPTION_NEW) == 1

    open(out_path, "wb").write(data)
    print(f"wrote {out_path}: {len(data)} bytes (== base), "
          f"{len(ZOOM_FACTORS)} zoom factors, legacy graphics off, mod hotkeys on")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
