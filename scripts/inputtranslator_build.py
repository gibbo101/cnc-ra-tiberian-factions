#!/usr/bin/env python3
"""Bind the mod hotkey commands in INPUTTRANSLATORCONFIGURATIONS.XML.

EA ships four unbound modder commands (GAME_COMMAND_CNC_MOD_COMMAND_1..4) in the
tactical context, each holding an empty `<Key></Key> <!-- TBD -->` placeholder. Three
things are needed to make one actually fire:

1. **Take the key off the launcher's own command.** The deploy key belongs to
   COMMAND_CNC_DEPLOY_SELECTED_MCV, which cannot deploy our faction MCV types -- that is
   why the deploy hotkey went missing for all four factions. Clearing it hands the key
   over cleanly instead of relying on both commands firing.
2. **Give the key to the mod command.**
3. **Make the binding fixed.** A command listed in a `<KeyConfig>` block is
   user-rebindable, and the player's saved keymap (Player_RA_settings_*.bin) wins over
   the XML -- a command the profile holds as unbound stays unbound, which is exactly what
   happened on the first test. EA hit this too and solved it by commenting the KeyConfig
   block out, annotated "Now a fixed key..." (COMMAND_CNC_FORCE_MOVE, FORCE_FIRE). The
   cost is that players cannot rebind it either.

Size is held exactly (the CONFIG.MEG offset rule) by padding or trimming indentation
whitespace, which the XML parser ignores.

Requires `CNCEnableModHotKeyGameCommands` True in GAMECONSTANTS.XML, and a handler for
INPUT_REQUEST_MOD_GAME_COMMAND_n_AT_POSITION in dllinterface.cpp.

Usage: inputtranslator_build.py <base.xml> <out.xml>
"""
import re
import sys

KEY = b"VIRTUAL_KEY_BACKSLASH"

# The launcher's own deploy command surrenders the key.
LAUNCHER_DEPLOY_OLD = b"<Key>VIRTUAL_KEY_BACKSLASH</Key> <!-- TBD by Design -->"
LAUNCHER_DEPLOY_NEW = b"<Key></Key>"

# Command 1 = deploy the selected MCV, whatever faction it belongs to.
PLACEHOLDER = b"<Key></Key> <!-- TBD -->"
BOUND = b"<Key>" + KEY + b"</Key>"

def keyconfig_span(data):
    """Byte range of the <KeyConfig> block registering MOD_COMMAND_1 as rebindable.

    Located structurally rather than by literal: the file is CRLF and indented with tabs,
    so a hand-written literal is easy to get subtly wrong.
    """
    marker = b"GAME_COMMAND_CNC_MOD_COMMAND_1"
    at = data.find(marker)
    while at != -1:
        open_at = data.rfind(b"<KeyConfig>", 0, at)
        close_at = data.find(b"</KeyConfig>", at)
        if open_at != -1 and close_at != -1 and b"<InputMapping" not in data[open_at:at]:
            return open_at, close_at + len(b"</KeyConfig>")
        at = data.find(marker, at + 1)
    raise AssertionError("MOD_COMMAND_1 KeyConfig block not found")


def resize(data, target_len):
    """Pad or trim indentation whitespace until the file is exactly target_len bytes."""
    delta = len(data) - target_len
    while delta > 0:
        m = re.search(rb"\n\t{3,}", data)
        assert m, "ran out of indentation to trim"
        data = data[:m.start() + 1] + data[m.start() + 2:]
        delta -= 1
    if delta < 0:
        m = re.search(rb"\n\t{3,}", data)
        assert m, "nowhere to pad"
        data = data[:m.start() + 1] + b" " * (-delta) + data[m.start() + 1:]
    return data


def main(base_path, out_path):
    data = open(base_path, "rb").read()
    base_len = len(data)

    assert data.count(LAUNCHER_DEPLOY_OLD) == 1, "launcher deploy binding not found"
    data = data.replace(LAUNCHER_DEPLOY_OLD, LAUNCHER_DEPLOY_NEW)
    print(f"  COMMAND_CNC_DEPLOY_SELECTED_MCV -> unbound (key handed to the mod command)")

    anchor = data.find(b"GAME_COMMAND_CNC_MOD_COMMAND_1")
    assert anchor != -1, "MOD_COMMAND_1 not found"
    slot = data.find(PLACEHOLDER, anchor)
    assert slot != -1, "MOD_COMMAND_1 placeholder already filled?"
    data = data[:slot] + BOUND + data[slot + len(PLACEHOLDER):]
    print(f"  MOD_COMMAND_1 -> {KEY.decode()}")

    start, end = keyconfig_span(data)
    data = data[:start] + b"<!-- Now a fixed key... " + data[start:end] + b" -->" + data[end:]
    print("  MOD_COMMAND_1 KeyConfig commented out (fixed key, profile cannot override)")

    data = resize(data, base_len)
    assert len(data) == base_len, f"size mismatch: {len(data)} != {base_len}"
    assert data.count(BOUND) == 1
    open(out_path, "wb").write(data)
    print(f"wrote {out_path}: {len(data)} bytes (== base)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
