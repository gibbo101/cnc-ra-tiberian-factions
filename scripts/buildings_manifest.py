'''
Machine source of truth for the v0.3 TD-prefixed building catalogue.

Each entry mirrors the master tables in `docs/catalogue.md` (flag table + wiring
table) and is what `scripts/add_building.py` reads to emit the rules.ini block.
The doc remains the human-readable reference; this file is the script's input.
If they drift, the script wins — fix the doc to match.

Field meanings and source:
  ininame      - canonical IniName, TD-prefixed (collides with vanilla otherwise).
                 Also used as the rules.ini Image= and XML tileset Name —
                 TD-prefix everywhere on the consumer side prevents collisions
                 with vanilla RA entries (e.g. WEAP, FIX, HPAD, SAM).
  logic        - RA donor IniName for the engine alias (Logic= in rules.ini)
  td_asset     - Original TD asset name in TEXTURES_TD_SRGB.MEG (e.g. "NUKE"
                 for the TD power plant). Drives MEG extraction in
                 bundle_assets.py and the internal `foo-NNNN.tga` frame
                 paths. Never appears in rules.ini.
  footprint    - named preset in bdata.cpp _presets[] table (unprefixed)
  shape_size   - (W, H) tuple in pixels for the Remastered launcher render
                 scale. Convention: W = Width()*24, H = Height()*24. MANDATORY
                 for every mod entry — without it, w/h=0 falls through to
                 TGA-native scale, which varies per asset. See ShapeSize block
                 in bdata.cpp's Read_INI for the override path.
  text_id_name - Launcher localization key for the sidebar display name
                 (e.g. TEXT_STRUCTURE_TITLE_GDI_POWER_PLANT). Missing
                 produces "<Missing> TDxxx" in the tooltip. Wired via
                 RABUILDABLES.XML; see scripts/bundle_assets.py.
  text_id_desc - Launcher localization key for the building description
                 (e.g. TEXT_STRUCTURE_DESC_GDI_POWER_PLANT).
  build_icon   - Tileset name resolving to the sidebar cameo TGA
                 (e.g. BuildIcon_TD_PowerPlant).
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
    "td_asset":       "NUKE",
    "footprint":   "NUKE",
    "shape_size":  (48, 48),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_POWER_PLANT",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_POWER_PLANT",
    "build_icon":  "BuildIcon_TD_PowerPlant",
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
    "td_asset":       "NUK2",
    "footprint":   "NUK2",
    "shape_size":  (48, 48),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_ADV_POWER_PLANT",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_ADV_POWER_PLANT",
    "build_icon":  "BuildIcon_TD_AdvPowerPlant",
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


TDPYLE = {
    "ininame":     "TDPYLE",
    "logic":       "TENT",
    "td_asset":       "PYLE",
    "footprint":   "PYLE",
    "shape_size":  (48, 48),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_BARRACKS",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_BARRACKS",
    "build_icon":  "BuildIcon_TD_Barracks",
    "name":        "Barracks",
    "tech_level":  1,
    "prereq":      "TDNUKE",
    "owner":       "GoodGuy",
    "cost":        300,
    "power":       -20,
    "points":      60,
    "sight":       4,
    "adjacent":    1,
    "strength":    400,
    "armor":       "wood",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  True,
    "crewed":      True,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   None,
    "notes":       "TD GDI Barracks. Donor BARR provides factory + infantry-build behaviour. Owner: HOUSE_GOOD only (Nod gets TDHAND later). Sight bumped 3->4 for RA reveal scale.",
}


# ---------------------------------------------------------------------------
# Registry — add new entries here so --all picks them up.
# Order = rules.ini emission order when running with --all.
# ---------------------------------------------------------------------------

ALL = [
    TDNUKE,
    TDNUK2,
    TDPYLE,
]


def by_name(ininame):
    '''Return the manifest entry for `ininame`, or raise KeyError.'''
    for entry in ALL:
        if entry["ininame"] == ininame:
            return entry
    raise KeyError(ininame)
