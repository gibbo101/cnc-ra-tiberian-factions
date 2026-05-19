'''
Machine source of truth for the v0.3 TD-prefixed building catalogue.

Each entry mirrors the master tables in `docs/catalogue.md` (flag table + wiring
table) and is what `scripts/add_building.py` reads to emit the rules.ini block.
The doc remains the human-readable reference; this file is the script's input.
If they drift, the script wins — fix the doc to match.

Field meanings and source:
  ininame      - canonical IniName, TD-prefixed (collides with vanilla otherwise)
  logic        - RA donor IniName for the engine alias (Logic= in rules.ini)
  image        - sprite + buildup asset name (unprefixed TD asset)
  footprint    - named preset in bdata.cpp _presets[] table (unprefixed)
  shape_size   - (W, H) tuple in pixels for the Remastered launcher render
                 scale. Convention: W = Width()*24, H = Height()*24. MANDATORY
                 for every mod entry — without it, w/h=0 falls through to
                 TGA-native scale, which varies per asset. See ShapeSize block
                 in bdata.cpp's Read_INI for the override path.
  name         - display name in the sidebar / select tooltip
  tech_level   - TD source "Build level" (sidebar gating)
  prereq       - TD-prefixed prerequisite IniName, or None for no prereq
  owner        - "GoodGuy", "BadGuy", or "GoodGuy,BadGuy"
  cost         - credits
  power        - signed: +N produces, -N consumes (engine converts -N to Drain=N)
  points       - TD-authentic RISK/RWRD value. MANDATORY or AI ignores the
                 building (see docs/ai-targeting.md).
  sight        - cell radius (TD-authentic; smaller than RA equivalents)
  adjacent     - allowed build-distance from existing base structures
  strength     - max HP
  armor        - one of: none, wood, aluminum, steel, concrete
  primary      - rules.ini weapon name for the primary slot, or None
  secondary    - rules.ini weapon name for the secondary slot, or None
  base_normal  - True for real base structures (always True in v0.3 catalogue)
  capturable   - engineer can capture
  crewed       - sell/destroy spawns infantry
  repairable   - wrench tool can target
  bib          - requires the cracked-dirt foundation bib
  idle_anim    - (start, count, rate) tuple for idle cycling, or None for static
  notes        - free-form, not emitted to rules.ini

License: GPL v3 (inherited from Vanilla Conquer base).
'''


# ---------------------------------------------------------------------------
# v0.3 catalogue entries
# ---------------------------------------------------------------------------

TDNUKE = {
    "ininame":     "TDNUKE",
    "logic":       "POWR",
    "image":       "NUKE",
    "footprint":   "NUKE",
    "shape_size":  (48, 48),
    "name":        "Power Plant",
    "tech_level":  0,
    "prereq":      None,
    "owner":       "GoodGuy,BadGuy",
    "cost":        300,
    "power":       100,
    "points":      50,
    "sight":       5,
    "adjacent":    1,
    "strength":    200,
    "armor":       "wood",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  True,
    "crewed":      True,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   (0, 4, 15),
    "notes":       "TD lvl 0; reference implementation for v0.3 phase-3a.",
}

TDNUK2 = {
    "ininame":     "TDNUK2",
    "logic":       "APWR",
    "image":       "NUK2",
    "footprint":   "NUK2",
    "shape_size":  (48, 48),
    "name":        "Advanced Power Plant",
    "tech_level":  5,
    "prereq":      "TDNUKE",
    "owner":       "GoodGuy,BadGuy",
    "cost":        700,
    "power":       200,
    "points":      75,
    "sight":       5,
    "adjacent":    1,
    "strength":    300,
    "armor":       "wood",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  True,
    "crewed":      True,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   (0, 4, 15),
    "notes":       "TD lvl 5; first manifest-driven generation.",
}


# ---------------------------------------------------------------------------
# Registry — add new entries here so --all picks them up.
# Order = rules.ini emission order when running with --all.
# ---------------------------------------------------------------------------

ALL = [
    TDNUKE,
    TDNUK2,
]


def by_name(ininame):
    '''Return the manifest entry for `ininame`, or raise KeyError.'''
    for entry in ALL:
        if entry["ininame"] == ininame:
            return entry
    raise KeyError(ininame)
