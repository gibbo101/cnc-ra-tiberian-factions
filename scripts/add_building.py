#!/usr/bin/env python3
'''
Emit or refresh a `[TDxxxx]` block in rules.ini from `buildings_manifest.py`.

Idempotent: if the section already exists, its body is replaced in place; if
not, a new block is inserted just before the `; End of Rules.INI` sentinel.
Vanilla sections and ordering are never touched. Always operates on the
mod's CCDATA/rules.ini, not the game's vanilla file.

Typical usage:

  scripts/add_building.py TDNUK2          # write TDNUK2 to rules.ini
  scripts/add_building.py --all           # write every manifest entry
  scripts/add_building.py TDNUK2 --diff   # show what would change, no write
  scripts/add_building.py TDNUK2 --dry-run  # print emitted block to stdout

Field order and boolean formatting are pinned to match the v0.3 phase-3a
TDNUKE block (hand-written, validated on the Deck) so re-emitting TDNUKE is
a no-op diff. See docs/adding-td-buildings.md for the canonical field
recipe and docs/ai-targeting.md for the Points= rationale.

License: GPL v3 (inherited from Vanilla Conquer base).
'''
import argparse
import difflib
import os
import sys
from pathlib import Path

# Make the manifest importable regardless of cwd.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import buildings_manifest  # noqa: E402


REPO_ROOT = SCRIPT_DIR.parent
RULES_INI = REPO_ROOT / "resources/remaster_mods/Vanilla_RA/CCDATA/rules.ini"
END_MARKER = "; End of Rules.INI"
NEW_BUILDINGS_SECTION = "[NewBuildings]"


# Field order and per-field formatter. Tuple is (manifest_key, ini_key, formatter).
# `formatter` is called only when the manifest value is non-None and non-empty;
# returning None skips the field entirely. This is how Prerequisite/Primary/
# Secondary get omitted for buildings that don't have one.
def _yes_no(v):  return "yes" if v else "no"
def _true_false(v): return "true" if v else "false"
def _identity(v): return v
def _str(v): return str(v)

def _shape_size(v): return "%d,%d" % (v[0], v[1])

FIELD_SPEC = [
    # identity
    ("logic",       "Logic",        _identity),
    # Image= in rules.ini = the IniName (TD-prefixed) so the launcher's
    # tileset lookup hits the per-entry <Name>TDxxx</Name> we put in
    # RA_STRUCTURES.XML. Source asset name (unprefixed) lives in
    # manifest['td_asset'] and is consumed by bundle_assets.py only.
    ("ininame",     "Image",        _identity),
    ("footprint",   "Footprint",    _identity),
    ("shape_size",  "ShapeSize",    _shape_size),
    ("name",        "Name",         _identity),
    # build hookup
    ("tech_level",  "TechLevel",    _str),
    ("prereq",      "Prerequisite", _identity),
    ("owner",       "Owner",        _identity),
    # economy
    ("cost",        "Cost",         _str),
    ("power",       "Power",        _str),
    ("storage",     "Storage",      _str),
    ("points",      "Points",       _str),
    # tactical
    ("sight",       "Sight",        _str),
    ("adjacent",    "Adjacent",     _str),
    ("sensors",     "Sensors",      _yes_no),
    # defence
    ("strength",    "Strength",     _str),
    ("armor",       "Armor",        _identity),
    # combat (defensive structures only)
    ("primary",     "Primary",      _identity),
    ("secondary",   "Secondary",    _identity),
    # flags
    ("base_normal", "BaseNormal",   _yes_no),
    ("capturable",  "Capturable",   _true_false),
    ("crewed",      "Crewed",       _true_false),
    ("repairable",  "Repairable",   _yes_no),
    ("bib",         "Bib",          _yes_no),
]


def emit_block(entry):
    '''Render the [TDxxxx] section text for one manifest entry.'''
    lines = ["[%s]" % entry["ininame"]]
    for manifest_key, ini_key, fmt in FIELD_SPEC:
        value = entry.get(manifest_key)
        if value is None:
            continue
        # bool fields always emit (False is still a valid value)
        if not isinstance(value, bool) and value == "":
            continue
        lines.append("%s=%s" % (ini_key, fmt(value)))
    # Idle anim block: comment + three IdleAnim* keys. Skip entirely when None.
    idle = entry.get("idle_anim")
    if idle is not None:
        start, count, rate = idle
        last_idle = start + count - 1
        lines.append(
            "; Idle animation: cycle frames %d-%d, then frame %d+ are damaged variants."
            % (start, last_idle, last_idle + 1)
        )
        lines.append(
            "; Rate is game-ticks per frame (15 ticks/sec base), scaled by GameSpeed via Normalize_Delay."
        )
        lines.append("IdleAnimStart=%d" % start)
        lines.append("IdleAnimCount=%d" % count)
        lines.append("IdleAnimRate=%d"  % rate)
    return "\n".join(lines) + "\n"


def replace_or_insert(content, ininame, new_block):
    '''Return updated rules.ini content with [ininame] replaced or inserted.

    Replacement: scan from the `[ininame]` header forward until the next
    `[OtherSection]` header or the End-Of-INI sentinel; replace that range
    with `new_block`. Insertion: place `new_block` immediately before the
    sentinel (with a blank line separator). Always preserves a single
    trailing blank line between sections.
    '''
    header = "[%s]" % ininame
    if header in content:
        start = content.index(header)
        # Find the end of this section: the earliest of "\n[" or "\n; End ...".
        rest = content[start + len(header):]
        candidates = []
        idx = rest.find("\n[")
        if idx != -1:
            candidates.append(idx)
        idx = rest.find("\n" + END_MARKER)
        if idx != -1:
            candidates.append(idx)
        if candidates:
            end_offset = min(candidates) + 1  # keep the leading newline before the next section
            full_end = start + len(header) + end_offset
        else:
            full_end = len(content)
        # Trim any trailing blank lines from `new_block` and re-add one for separation.
        body = new_block.rstrip("\n") + "\n\n"
        return content[:start] + body + content[full_end:]

    # Insertion path: place before the End-Of-INI sentinel.
    if END_MARKER in content:
        idx = content.index(END_MARKER)
        # Walk backwards through whitespace so we don't accumulate blank lines.
        prefix_end = idx
        while prefix_end > 0 and content[prefix_end - 1] in "\n":
            prefix_end -= 1
        body = new_block.rstrip("\n") + "\n\n"
        return content[:prefix_end] + "\n\n" + body + content[idx:]

    # No sentinel found — append at end with a separator.
    return content.rstrip("\n") + "\n\n" + new_block.rstrip("\n") + "\n"


def register_in_new_buildings(content, ininame):
    '''Append `<n>=<ininame>` to the [NewBuildings] section if absent.

    The engine only reads sections listed here, so an unregistered [TDxxxx]
    block is dead weight. Ordinals are allocated as `max(existing) + 1`; the
    script-side note in docs/adding-td-buildings.md confirms the ordinal value
    itself is decorative (the heap slot comes from BuildingTypes.Count()).
    Re-registration is a no-op.
    '''
    if NEW_BUILDINGS_SECTION not in content:
        raise RuntimeError(
            "rules.ini missing %s section — add one manually (see "
            "docs/adding-td-buildings.md step 1)." % NEW_BUILDINGS_SECTION
        )

    sec_start = content.index(NEW_BUILDINGS_SECTION)
    # Find end of section: next "\n[Section]" or EOF
    rest = content[sec_start + len(NEW_BUILDINGS_SECTION):]
    next_section = rest.find("\n[")
    end_marker_rel = rest.find("\n" + END_MARKER)
    candidates = [c for c in (next_section, end_marker_rel) if c != -1]
    if candidates:
        sec_end = sec_start + len(NEW_BUILDINGS_SECTION) + min(candidates)
    else:
        sec_end = len(content)

    section_body = content[sec_start:sec_end]

    # Already registered? Bail without changes.
    for line in section_body.splitlines():
        if "=" in line:
            _ord, _, name = line.partition("=")
            if name.strip() == ininame:
                return content

    # Find highest existing ordinal.
    highest = 0
    for line in section_body.splitlines():
        if "=" in line:
            ord_str, _, _ = line.partition("=")
            try:
                highest = max(highest, int(ord_str.strip()))
            except ValueError:
                pass  # ignore non-numeric ordinals (shouldn't appear in vanilla format)
    new_ordinal = highest + 1
    new_line = "%d=%s\n" % (new_ordinal, ininame)

    # Insert just before the section ends — strip trailing whitespace from the
    # section body, append our line, then a single blank-line separator before
    # the next section.
    trimmed = section_body.rstrip("\n")
    new_body = trimmed + "\n" + new_line
    return content[:sec_start] + new_body + content[sec_end:]


def _atomic_write(path, content):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def _show_diff(original, updated, path):
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        updated.splitlines(keepends=True),
        fromfile=str(path),
        tofile=str(path) + " (new)",
        n=3,
    )
    body = "".join(diff)
    if body:
        sys.stdout.write(body)
    else:
        print("(no changes)")


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("names", nargs="*", help="IniName(s) to emit (e.g. TDNUK2). Omit with --all.")
    parser.add_argument("--all", action="store_true", help="Emit every manifest entry.")
    parser.add_argument("--dry-run", action="store_true", help="Print emitted block(s) to stdout; do not modify rules.ini.")
    parser.add_argument("--diff", action="store_true", help="Show unified diff vs current rules.ini; do not modify.")
    parser.add_argument("--rules", default=str(RULES_INI), help="Path to rules.ini (default: mod's CCDATA path).")
    parser.add_argument("--skip-assets", action="store_true",
                        help="Only emit rules.ini; don't run the asset bundler "
                             "(skip ZIP extraction + XML patching).")
    args = parser.parse_args()

    if args.all:
        if args.names:
            parser.error("--all takes no positional args")
        entries = list(buildings_manifest.ALL)
    else:
        if not args.names:
            parser.error("specify at least one IniName, or pass --all")
        entries = [buildings_manifest.by_name(n) for n in args.names]

    rules_path = Path(args.rules)

    # Dry-run: emit blocks to stdout and exit before touching the file.
    if args.dry_run:
        for entry in entries:
            sys.stdout.write(emit_block(entry))
            sys.stdout.write("\n")
        return 0

    original = rules_path.read_text(encoding="utf-8")
    updated = original
    for entry in entries:
        block = emit_block(entry)
        updated = replace_or_insert(updated, entry["ininame"], block)
        updated = register_in_new_buildings(updated, entry["ininame"])

    if args.diff:
        _show_diff(original, updated, rules_path)
        return 0

    if updated == original:
        print("[add_building] rules.ini already up to date — %s" % rules_path)
    else:
        _atomic_write(rules_path, updated)
        print("[add_building] wrote %d entr%s to %s"
              % (len(entries), "y" if len(entries) == 1 else "ies", rules_path))

    # Continue to asset bundling regardless of whether rules.ini changed —
    # the bundler is responsible for ZIPs + XML state, and those can drift
    # even when rules.ini is up to date.
    if args.skip_assets:
        return 0

    # Sprite ZIPs + RA_STRUCTURES.XML + RABUILDABLES.XML — delegated to
    # bundle_assets.py so the binary asset work is testable in isolation
    # and doesn't pollute the rules.ini emitter with MEG/ZIP/XML concerns.
    import bundle_assets
    meg_path = bundle_assets.source_meg_path()
    for entry in entries:
        try:
            summary = bundle_assets.bundle(entry, meg_path=meg_path)
        except Exception as e:
            print(f"[add_building] {entry['ininame']}: asset bundling FAILED: {e}",
                  file=sys.stderr)
            return 1
        print(
            f"[add_building] {entry['ininame']}: assets bundled — "
            f"main={summary['main_frame_count']}f, "
            f"make={summary['make_frame_count']}f, "
            f"structures_xml={'patched' if summary['structures_changed'] else 'unchanged'}, "
            f"buildables_xml={'patched' if summary['buildables_changed'] else 'unchanged'}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
