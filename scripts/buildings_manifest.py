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
  storage      - credit-storage capacity for refineries/silos. Integer; omit
                 (None) for non-storage buildings. RA-authentic baseline:
                 refinery 2000, silo 1500. (Vanilla RA rules.ini ships with
                 NightFalcon101's MODERATE_WARFARE 10× values; reverted in
                 our copy. TD-authentic refinery is 1000 but we stay with
                 RA values for parity with the rest of the mod's economy.)
  points       - TD-authentic RISK/RWRD value. MANDATORY or AI ignores the
                 building (see docs/ai-targeting.md).
  sight        - cell radius (TD-authentic; smaller than RA equivalents)
  adjacent     - allowed build-distance from existing base structures
  sensors      - True for buildings that act as radar (reveal terrain in fog
                 + minimap). Emits Sensors=yes. Set on TDHQ (Comm Center) and
                 TDEYE (Adv Comm). None/False = no sensors.
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
  active_anim  - (start, count, rate) tuple for BSTATE_ACTIVE (producing) cycling,
                 or None to inherit donor. Use to clamp BARR/TENT-class donors
                 whose hardcoded _anims[] cycles 10 frames — set count=1 to force
                 a static active sprite when the TGA pack only has 3 frames.
  notes        - free-form, not emitted to rules.ini

License: GPL v3 (inherited from Vanilla Conquer base).
'''


# ---------------------------------------------------------------------------
# v0.3 catalogue entries
# ---------------------------------------------------------------------------

TDNUKE = {
    "ininame":     "TDNUKE",
    # MIGRATED to STRUCT_TDNUKE in bdata.cpp Init_Heap (M2 Tier 1, 2026-05-21).
    "logic":       None,
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
    # MIGRATED to STRUCT_TDNUK2 in bdata.cpp Init_Heap (M2 Tier 1, 2026-05-21).
    "logic":       None,
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


TDHQ = {
    "ininame":     "TDHQ",
    # MIGRATED to STRUCT_TDHQ in bdata.cpp Init_Heap (M4 Tier 3, 2026-05-26).
    "logic":       None,
    "td_asset":    "HQ",
    "footprint":   "HQ",
    "shape_size":  (48, 48),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_COMM_CENTER",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_COMM_CENTER",
    "build_icon":  "BuildIcon_TD_CommCenter",
    "name":        "Communications Center",
    "tech_level":  2,
    "prereq":      "TDPROC",
    "owner":       "GoodGuy,BadGuy",
    "cost":        1000,
    "power":       -40,
    "storage":     None,
    "points":      20,
    "sight":       10,
    "adjacent":    1,
    "sensors":     True,
    "strength":    500,
    "armor":       "wood",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  True,
    "crewed":      True,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   (0, 16, 4),
    "notes":       "TD Comm Center / Radar. STRUCT_TDHQ with own BuildingTypeClass (ClassTdHq) modeled on TD's ClassCommand. Non-factory (ToBuild=RTTI_NONE), BSIZE_22 (ComList+OComList), ARMOR_WOOD, Sight=10, Power=-40, Strength=500. Radar/minimap activation: BuildingClass::Unlimbo + HouseClass recompute shadow STRUCTF_RADAR for STRUCT_TDHQ so the existing ActiveBScan & STRUCTF_RADAR tests at house.cpp:1502+ activate the minimap. Prereq equivalence in house.cpp lets RA buildings keyed to Prerequisite=dome (Chronosphere/Iron Curtain/etc.) build off a TDHQ. Shared GDI+Nod (TD didn't differentiate visually). Classic SHP ships via TFASSETS.MIX (TDHQ.SHP + TDHQMAKE.SHP).",
}


TDPROC = {
    "ininame":     "TDPROC",
    "logic":       "PROC",
    "td_asset":    "PROC",
    "footprint":   None,  # RA PROC donor is 3x3 (BSIZE_33); inherit donor shape.
    "shape_size":  (72, 72),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_REFINERY",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_REFINERY",
    "build_icon":  "BuildIcon_TD_Refinery",
    "name":        "Tiberium Refinery",
    "tech_level":  1,
    "prereq":      "TDNUKE",
    "owner":       "GoodGuy,BadGuy",
    "cost":        2000,
    "power":       -40,
    "storage":     2000,
    "points":      55,
    "sight":       4,
    "adjacent":    1,
    "sensors":     None,
    "strength":    900,
    "armor":       "wood",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  True,
    "crewed":      True,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   (0, 6, 4),
    "notes":       "TD Tiberium Refinery. Shared GoodGuy/BadGuy. Logic=PROC inherits free-harvester-on-build + dock/siphon cycles. First entry exercising Storage= field.",
}


TDSILO = {
    "ininame":     "TDSILO",
    # MIGRATED to STRUCT_TDSILO in bdata.cpp Init_Heap (M2 Tier 1, 2026-05-21).
    "logic":       None,
    "td_asset":    "SILO",
    # RA SILO donor is BSIZE_11 (1×1) which made TDSILO render 1×1; override to
    # TD-authentic BSIZE_21 via the SILO preset. Bib=yes adds the extra row
    # visually so placement preview reads as 2 wide × 2 rows. shape_size
    # 48×24 matches the TD silo sprite's native 2-wide × 1-tall canvas.
    "footprint":   "SILO",
    "shape_size":  (48, 24),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_SILO",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_SILO",
    "build_icon":  "BuildIcon_TD_Silo",
    "name":        "Tiberium Silo",
    "tech_level":  1,
    "prereq":      "TDPROC",
    "owner":       "GoodGuy,BadGuy",
    "cost":        150,
    "power":       -10,
    "storage":     1500,
    "points":      16,
    "sight":       2,
    "adjacent":    1,
    "sensors":     None,
    "strength":    300,
    "armor":       "wood",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  True,
    "crewed":      False,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   None,
    "notes":       "TD Silo. No idle anim (capacity-based shape, not cycle). Crew=no per TD canon.",
}


TDFIX = {
    "ininame":     "TDFIX",
    # MIGRATED to STRUCT_TDFIX in bdata.cpp Init_Heap (M4 Tier 3, 2026-05-25).
    "logic":       None,
    "td_asset":    "FIX",
    "footprint":   None,  # RA FIX donor is 3x3 (BSIZE_33); inherit donor shape.
    "shape_size":  (72, 72),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_REPAIR_FACILITY",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_REPAIR_FACILITY",
    "build_icon":  "BuildIcon_TD_RepairFacility",
    "name":        "Repair Facility",
    "tech_level":  5,
    "prereq":      "TDNUKE",
    "owner":       "GoodGuy,BadGuy",
    "cost":        1200,
    "power":       -30,
    "storage":     None,
    "points":      46,
    "sight":       3,
    "adjacent":    1,
    "sensors":     None,
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
    "notes":       "TD Service Depot. STRUCT_TDFIX with own BuildingTypeClass (ClassTdFix) modeled on TD's ClassRepair. Non-factory (ToBuild=RTTI_NONE), BSIZE_33 cross-shape (ListFix+OListFix reused from RA's vanilla FIX), ARMOR_WOOD, Strength=400 (TD-authentic; RA's REPAIR has 800 — leaked through Logic=FIX alias). Engine dispatches: 13 STRUCT_REPAIR cases in building.cpp + 5 unit.cpp + 2 aircraft.cpp updated to accept STRUCT_TDFIX. Find_Docking_Bay (techno.cpp:6486) extended with TDFIX fallback so vehicles/aircraft find TDFIX when looking for STRUCT_REPAIR. Classic SHP ships via TFASSETS.MIX (TDFIX.SHP + TDFIXMAKE.SHP).",
}


TDWEAP = {
    "ininame":     "TDWEAP",
    "logic":       None,         # M4 Tier 3 separated 2026-05-27 — STRUCT_TDWEAP native, no engine alias.
    "td_asset":    "WEAP",
    "footprint":   None,         # ClassTdWeap uses RA's ExitWeap/ListWeap/OListWeap (same shape as TD WEAP).
    "shape_size":  (72, 72),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_WEAPONS_FACTORY",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_WEAPONS_FACTORY",
    "build_icon":  "BuildIcon_TD_WeaponsFactory",
    "name":        "Weapons Factory",
    "tech_level":  2,
    "prereq":      "TDPROC",
    "owner":       "GoodGuy",
    "cost":        2000,
    "power":       -30,
    "storage":     None,
    "points":      86,
    "sight":       3,
    "adjacent":    1,
    "sensors":     None,
    "strength":    1000,
    "armor":       "aluminum",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  True,
    "crewed":      True,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   None,
    "notes":       "TD GDI Weapons Factory. STRUCT_TDWEAP with own BuildingTypeClass (ClassTdWeap) modeled on RA/TD's ClassWeapon. RTTI_UNITTYPE factory, 3x2 BSIZE_32, ARMOR_ALUMINUM, Strength=1000 (matches both TD ADVANCED and RA). TD-authentic SW vehicle exit via Track14 (drive.cpp) + DIR_SW Unlimbo. Engine dispatches: STRUCT_WEAP|STRUCT_TDWEAP fall-through in Exit_Object + Mission_Unload (building.cpp), Door overlay swap (Draw_It) selects TDWEAP2.ZIP for STRUCT_TDWEAP. Can_Build prereq equivalence (STRUCT_WEAP satisfied by TDWEAP) uses dynamic IniName lookup.",
}


TDHPAD = {
    "ininame":     "TDHPAD",
    # MIGRATED to STRUCT_TDHPAD in bdata.cpp Init_Heap (M4 Tier 3, 2026-05-25).
    "logic":       None,
    "td_asset":    "HPAD",
    "footprint":   None,  # RA HPAD donor matches TD (2x2 BSIZE_22).
    "shape_size":  (48, 48),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_HELIPAD",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_HELIPAD",
    "build_icon":  "BuildIcon_TD_Helipad",
    "name":        "Helipad",
    "tech_level":  6,
    "prereq":      "TDPYLE",
    "owner":       "GoodGuy,BadGuy",
    "cost":        1500,
    "power":       -10,
    "storage":     None,
    "points":      65,
    "sight":       3,
    "adjacent":    1,
    "sensors":     None,
    "strength":    400,
    "armor":       "wood",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  True,
    "crewed":      False,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   None,
    "notes":       "TD Helipad. STRUCT_TDHPAD with own BuildingTypeClass (ClassTdHpad) modeled on TD's ClassHelipad. RTTI_AIRCRAFTTYPE factory, 2x2 BSIZE_22, ARMOR_WOOD, Strength=400 (TD-authentic; RA's HELIPAD has 800 — leaked through Logic=HPAD alias). Engine dispatches: 8 STRUCT_HELIPAD cases in building.cpp updated to accept STRUCT_TDHPAD (Receive_Message x3, sidebar refresh, Grand_Opening free-aircraft, Docking_Coord, Exit_Coord, Mission_Unload). Find_Docking_Bay (techno.cpp:6486) extended with helipad fallback so rotary aircraft find TDHPAD when looking for STRUCT_HELIPAD. Raw_Cost cost-adjust includes TDHPAD. Classic SHP ships via TFASSETS.MIX (TDHPAD.SHP + TDHPADMAKE.SHP).",
}


TDGTWR = {
    "ininame":     "TDGTWR",
    # MIGRATED to STRUCT_TDGTWR in bdata.cpp Init_Heap (M3 Tier 2, 2026-05-21).
    "logic":       None,
    "td_asset":    "GTWR",
    "footprint":   None,  # 1x1 (BSIZE_11) — matches TD ClassGTower.
    "shape_size":  (24, 24),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_GUARD_TOWER",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_GUARD_TOWER",
    "build_icon":  "BuildIcon_TD_GuardTower",
    "name":        "Guard Tower",
    "tech_level":  2,
    "prereq":      "TDPYLE",
    "owner":       "GoodGuy",
    "cost":        500,
    "power":       -10,
    "storage":     None,
    "points":      25,
    "sight":       3,
    "adjacent":    1,
    "sensors":     None,
    "strength":    200,
    "armor":       "wood",
    # TD-authentic chain gun (25 dmg / ROF 50 / Range 4 / GUN8 audio).
    # Fires [TDSpreadfire]. See docs/td-gtwr-gun-verification.md.
    "primary":     "TDChainGun",
    "secondary":   None,
    "base_normal": True,
    "capturable":  False,
    "crewed":      True,
    "repairable":  True,
    "bib":         False,
    "idle_anim":   None,
    "notes":       "TD GDI Guard Tower (STRUCT_TDGTWR, fully separated M3 Tier 2). Primary=TDChainGun fires [TDSpreadfire] for TD-authentic 25-damage chain-gun behaviour. Cap=no, bib=no (1x1).",
}


TDATWR = {
    "ininame":     "TDATWR",
    # MIGRATED to STRUCT_TDATWR in bdata.cpp Init_Heap (M3 Tier 2, 2026-05-21).
    "logic":       None,
    "td_asset":    "ATWR",
    "footprint":   None,  # RA AGUN donor is 1x2 (BSIZE_12); matches TD.
    "shape_size":  (24, 48),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_ADV_GUARD_TOWER",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_ADV_GUARD_TOWER",
    "build_icon":  "BuildIcon_TD_AdvGuardTower",
    "name":        "Advanced Guard Tower",
    "tech_level":  4,
    "prereq":      "TDHQ",
    "owner":       "GoodGuy",
    "cost":        1000,
    "power":       -20,
    "storage":     None,
    "points":      30,
    "sight":       4,
    "adjacent":    1,
    "sensors":     None,
    "strength":    300,
    "armor":       "aluminum",
    # TD-authentic TOW_TWO ported per docs/weapon-ports.md Phase W1. Single
    # missile slot, AA + AG capable via new BULLET_SSM bullet type. Replaces
    # the Hellfire/ZSU-23 dual-role interim.
    "primary":     "TDTowTwo",
    "secondary":   None,
    "base_normal": True,
    "capturable":  False,
    "crewed":      True,
    "repairable":  True,
    "bib":         False,
    "idle_anim":   None,
    "notes":       "TD GDI Advanced Guard Tower. Logic=AGUN (anti-air gun donor). TD-authentic is dual-role anti-armor + anti-air (TurretGun + Nike). Interim: Primary=TeslaZap (ground) + Secondary inherits AGUN's ZSU-23 (AA) via Logic= alias. Weapon port is in weapon-ports.md.",
}


TDEYE = {
    "ininame":     "TDEYE",
    # MIGRATED to STRUCT_TDEYE in bdata.cpp Init_Heap (M5 Tier 4, 2026-05-26).
    # Logic=MSLO previously granted RA AtomBomb super as a placeholder; the
    # Ion Cannon superweapon proper lands in Phase E2/E3 (see
    # docs/building-separation-plan.md M5 entries). Phase E1 (this commit)
    # ships the building structurally only — no super, no Ion Cannon visual.
    "logic":       None,
    "td_asset":    "EYE",
    # RA MSLO donor is BSIZE_21 (2x1); TD EYE is BSIZE_22 with the L-shape
    # NUK2 pattern (occupy {0, MCW, MCW+1}, overlap {1}). EYE preset reuses
    # NUK2's lists since tiberiandawn/bdata.cpp ComList/OComList are identical.
    "footprint":   "EYE",
    "shape_size":  (48, 48),
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_ADV_COMM_CENTER",
    "text_id_desc": "TEXT_STRUCTURE_DESC_GDI_ADV_COMM_CENTER",
    "build_icon":  "BuildIcon_TD_AdvCommCtr",
    "name":        "Advanced Communications Center",
    "tech_level":  7,
    "prereq":      "TDHQ",
    "owner":       "GoodGuy",
    "cost":        2800,
    "power":       -200,
    "storage":     None,
    "points":      100,
    "sight":       10,
    "adjacent":    1,
    "sensors":     True,
    "strength":    500,
    "armor":       "wood",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  False,
    "crewed":      True,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   (0, 16, 4),
    "notes":       "TD GDI Advanced Comm / Ion Cannon host. MIGRATED to STRUCT_TDEYE; Logic= dropped. Ion Cannon weapon effects + HouseClass machinery land in Phase E2/E3. Cap=no per TD canon (superweapon hosts can't be captured). -200 power drain is TD-authentic and intentional.",
}


TDFACT = {
    "ininame":     "TDFACT",
    "logic":       "FACT",
    "td_asset":    "FACT",
    "footprint":   None,  # RA FACT donor is BSIZE_33 (3x3); matches TD FACT.
    "shape_size":  (72, 72),
    # No DESC variant in launcher localization (sidebar cameo is rarely shown
    # — TechLevel=99 makes it sidebar-unbuildable; ConYard only spawns via
    # MCV deploy). Reuse MCV's desc + cameo for the encyclopedia panel.
    "text_id_name": "TEXT_STRUCTURE_TITLE_GDI_CONSTRUCTION_YARD",
    "text_id_desc": "TEXT_UNIT_DESC_GDI_MCV",
    "build_icon":  "BuildIcon_TD_MCV",
    "name":        "Construction Yard",
    "tech_level":  99,
    "prereq":      None,
    "owner":       "GoodGuy,BadGuy",
    "cost":        5000,
    # TD/RA-authentic: ConYard neither produces nor consumes power. Vanilla
    # RA [FACT] is Power=0 in rules.ini. Catalogue's earlier -30 was wrong.
    "power":       0,
    "storage":     None,
    "points":      70,
    "sight":       3,
    "adjacent":    1,
    "sensors":     None,
    "strength":    400,
    "armor":       "wood",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  True,
    "crewed":      True,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   (0, 4, 3),
    "notes":       "TD Construction Yard. Closing v0.3 slice — paired with TDMCV deploy. Production target: TechLevel=99 (not sidebar-buildable; MCV-deploy only). Shared GoodGuy/BadGuy until per-faction variants split in v0.4. Donor RA FACT is 3x3; vanilla FACT is TechLevel=-1 (uncbuildable) — same semantic as TD lvl 99. Power=0 per vanilla RA [FACT].",
}


TDPYLE = {
    "ininame":     "TDPYLE",
    # MIGRATED to STRUCT_TDPYLE in bdata.cpp Init_Heap (M2 Tier 1, 2026-05-21).
    "logic":       None,
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


TDGUN = {
    "ininame":     "TDGUN",
    # MIGRATED to STRUCT_TDGUN in bdata.cpp Init_Heap (M3 Tier 2, 2026-05-21).
    "logic":       None,
    "td_asset":    "GUN",
    "footprint":   "",
    "shape_size":  (24, 24),
    "text_id_name": "TEXT_STRUCTURE_TITLE_NOD_TURRET",
    "text_id_desc": "TEXT_STRUCTURE_DESC_NOD_TURRET",
    "build_icon":  "BuildIcon_TD_Turret",
    "name":        "Turret",
    "tech_level":  2,
    "prereq":      "TDHAND",
    "owner":       "BadGuy",
    "cost":        600,
    "power":       -20,
    "points":      26,
    "sight":       5,
    "adjacent":    1,
    "strength":    200,
    "armor":       "steel",
    # TD-authentic cannon: ROF=60 (vs RA TurretGun ROF=50), Damage=40, Range=6.
    # Separate from RA's [TurretGun] so vanilla Allied Turret balance stays
    # untouched and Nod balance is independently tunable. Phase W1.
    "primary":     "TDTurretGun",
    "secondary":   None,
    "base_normal": True,
    "capturable":  False,
    "crewed":      True,
    "repairable":  True,
    "bib":         False,
    "idle_anim":   (0, 1, 0),
    "active_anim": (0, 1, 0),
    "notes":       "TD Nod Turret (1x1 rotating gun). Donor RA GUN (Soviet Turret) provides matching 1x1 BSIZE_11 footprint. Primary=TDTurretGun for TD-authentic stats. Defensive (0,1,0) clamps on idle/active until TGA frame counts verified.",
}


TDSAM = {
    "ininame":     "TDSAM",
    # MIGRATED to STRUCT_TDSAM in bdata.cpp Init_Heap (M3 Tier 2, 2026-05-21).
    "logic":       None,
    "td_asset":    "SAM",
    "footprint":   "",
    "shape_size":  (48, 24),
    "text_id_name": "TEXT_STRUCTURE_TITLE_NOD_SAM_SITE",
    "text_id_desc": "TEXT_STRUCTURE_DESC_NOD_SAM_SITE",
    "build_icon":  "BuildIcon_TD_SamSite",
    "name":        "SAM Site",
    "tech_level":  6,
    "prereq":      "TDHAND",
    "owner":       "BadGuy",
    "cost":        750,
    "power":       -20,
    "points":      40,
    "sight":       3,
    "adjacent":    1,
    "strength":    200,
    "armor":       "steel",
    "primary":     "TDNike",
    "secondary":   None,
    "base_normal": True,
    "capturable":  False,
    "crewed":      False,
    "repairable":  True,
    "bib":         False,
    "idle_anim":   (0, 1, 0),
    "active_anim": (0, 1, 0),
    "notes":       "TD Nod SAM Site (BSIZE_21 underground launcher with 8-state "
                   "rise/rotate/fire/fire/lock/lower cycle). Wholesale port of "
                   "tiberiandawn/ STRUCT_SAM per docs/td-sam-deep-dive.md. "
                   "Weapon=TDNike (TD WEAPON_NIKE), projectile=TDPatriot "
                   "(TD BULLET_SAM/'MISSILE').",
}


# SEPARATED 2026-05-21: TDOBLI is the first fully-separated building.
# It now exists as STRUCT_TDOBLI in defines.h with ClassObelisk in
# bdata.cpp's Init_Heap. The [TDOBLI] rules.ini section is still
# Read_INI'd to populate Cost/Power/etc, but no Logic= alias.
# Asset bundling via this manifest entry still applies (extract ZIPs,
# patch RA_STRUCTURES.XML + RABUILDABLES.XML). When/if we re-run
# scripts/add_building.py for TDOBLI, the emitter must NOT re-add
# TDOBLI to [NewBuildings] index nor emit Logic=. Set logic=None here.
TDOBLI = {
    "ininame":     "TDOBLI",
    "logic":       None,
    "td_asset":    "OBLI",
    "footprint":   "",
    "shape_size":  (24, 48),
    "text_id_name": "TEXT_STRUCTURE_TITLE_NOD_OBELISK",
    "text_id_desc": "TEXT_STRUCTURE_DESC_NOD_OBELISK",
    "build_icon":  "BuildIcon_TD_Obelisk",
    "name":        "Obelisk of Light",
    "tech_level":  4,
    "prereq":      "TDHQ",
    "owner":       "BadGuy",
    "cost":        1500,
    "power":       -150,
    "points":      35,
    "sight":       5,
    "adjacent":    1,
    "strength":    200,
    "armor":       "aluminum",
    # TD-authentic OBELISK_LASER ported per Phase W1 (data piece only —
    # laser-line render lands in separation M5). Replaces the TSLA-donor
    # inherited TeslaZap stopgap. Damage=200, Range=7.5, Warhead=Laser
    # (100%-vs-all-armor), Sound=OBELRAY1. Until M5, the projectile is
    # invisible (Inviso=yes) so the Obelisk looks like it's not firing —
    # known limitation, accept until visual port lands.
    "primary":     "TDOblsLaser",
    "secondary":   None,
    "base_normal": True,
    "capturable":  False,
    "crewed":      True,
    "repairable":  True,
    "bib":         False,
    "idle_anim":   (0, 1, 0),
    "active_anim": (0, 4, 15),
    "notes":       "TD Nod Obelisk of Light (1x2 beam tower). Donor RA TSLA (Tesla Coil) provides matching BSIZE_12 footprint. Primary=TDOblsLaser (Phase W1 data port; render in M5). active_anim=(0,4,15) is TD-authentic OBELISK_ANIMATION_RATE=15 — 4-frame charge cycle.",
}


TDTMPL = {
    "ininame":     "TDTMPL",
    # MIGRATED to STRUCT_TDTMPL in bdata.cpp Init_Heap (M5 Tier 4, 2026-05-26).
    # Logic=MSLO previously granted RA AtomBomb as the placeholder super; the
    # Nuclear Strike (SPC_TD_NUKE) proper lands in Phase T2 via HouseClass.
    # Phase T1 ships the building structurally only — no super attached.
    "logic":       None,
    "td_asset":    "TMPL",
    "footprint":   "TMPL",
    "shape_size":  (72, 72),
    "text_id_name": "TEXT_STRUCTURE_TITLE_NOD_TEMPLE_OF_NOD",
    "text_id_desc": "TEXT_STRUCTURE_DESC_NOD_TEMPLE_OF_NOD",
    "build_icon":  "BuildIcon_TD_TempleOfNod",
    "name":        "Temple of Nod",
    "tech_level":  7,
    "prereq":      "TDHQ",
    "owner":       "BadGuy",
    "cost":        3000,
    "power":       -150,
    "points":      20,
    "sight":       4,
    "adjacent":    1,
    "strength":    1000,
    "armor":       "aluminum",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  False,
    "crewed":      True,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   (0, 1, 0),
    "active_anim": (0, 5, 1),
    "buildup_anim": (0, 36, 2),
    "notes":       "TD Nod Temple of Nod (3x3 superweapon host). MIGRATED to STRUCT_TDTMPL; Logic= dropped. Nuclear Strike super lands in Phase T2 via SPC_TD_NUKE on HouseClass. idle_anim=(0,1,0) + active_anim=(0,5,1) match TD-authentic _anims[] values (STRUCT_TEMPLE BSTATE_IDLE 0/1/0, BSTATE_ACTIVE 0/5/1). buildup_anim=(0,36,2) drives the 36-frame temple-assembly sequence from TDTMPLMAKE.ZIP.",
}


TDAFLD = {
    "ininame":     "TDAFLD",
    "logic":       "WEAP",
    "td_asset":    "AFLD",
    "footprint":   "AFLD",
    "shape_size":  (96, 48),
    "text_id_name": "TEXT_STRUCTURE_TITLE_NOD_AIRFIELD",
    "text_id_desc": "TEXT_STRUCTURE_DESC_NOD_AIRFIELD",
    "build_icon":  "BuildIcon_TD_Airstrip",
    "name":        "Airstrip",
    "tech_level":  2,
    "prereq":      "TDPROC",
    "owner":       "BadGuy",
    "cost":        2000,
    "power":       -30,
    "points":      86,
    "sight":       5,
    "adjacent":    1,
    "strength":    500,
    "armor":       "steel",
    "primary":     None,
    "secondary":   None,
    "base_normal": True,
    "capturable":  True,
    "crewed":      True,
    "repairable":  True,
    "bib":         True,
    "idle_anim":   (0, 16, 3),
    "active_anim": (0, 1, 0),
    "notes":       "TD Nod Airstrip. Logic=WEAP donor + TDC17 cargo-plane delivery (v0.3.1-phase2d, 2026-05-21). Vehicles produced from TDAFLD are flown in by a C-17 cargo plane that enters from the east edge, drops the vehicle on a strip-adjacent exit cell, and continues west off-map. Replaces the v0.3.1-phase1 stopgap where vehicles emerged mid-strip via WEAP's TD-SW exit track. Canonical port writeup in docs/cargo-plane-port.md — the cargo-plane delivery activates 10 dormant mechanics in RA (Mission_Unload state machine port, Enter_Idle_Mode in-air cargo branch, Edge_Of_World_AI vestigial AIRCRAFT_CARGO clause, Find_Docking_Bay IniName + CAN_LOAD bypass, etc.). 4x2 footprint (AFLD preset in bdata.cpp). idle_anim=(0,16,3) TD-authentic (STRUCT_AIRSTRIP _anims[] in TD source). active_anim still clamped to (0,1,0) since WEAP donor's door-open ACTIVE animation doesn't apply to a doorless airstrip — and is now irrelevant since cargo arrives by air, not by door.",
}


TDHAND = {
    "ininame":     "TDHAND",
    # MIGRATED to STRUCT_TDHAND in bdata.cpp Init_Heap (M4 Tier 3, 2026-05-25).
    "logic":       None,
    "td_asset":    "HAND",
    "footprint":   "HAND",
    "shape_size":  (48, 72),
    "text_id_name": "TEXT_STRUCTURE_TITLE_NOD_HAND_OF_NOD",
    "text_id_desc": "TEXT_STRUCTURE_DESC_NOD_HAND_OF_NOD",
    "build_icon":  "BuildIcon_TD_HandOfNod",
    "name":        "Hand of Nod",
    "tech_level":  1,
    "prereq":      "TDNUKE",
    "owner":       "BadGuy",
    "cost":        300,
    "power":       -20,
    "points":      61,
    "sight":       3,
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
    "idle_anim":   (0, 1, 0),
    "active_anim": (0, 1, 0),
    "notes":       "TD Nod Barracks. STRUCT_TDHAND with own BuildingTypeClass (ClassTdHand) modeled on TD's ClassHand. RTTI_INFANTRYTYPE factory, 2x3 L-shape footprint, ARMOR_WOOD, Sight=3 (TD-authentic). Engine dispatches: Exit_Object case at building.cpp:2348 (alongside STRUCT_BARRACKS/TENT/KENNEL/TDPYLE). Classic SHP ships via TFASSETS.MIX (TDHAND.SHP + TDHANDMAKE.SHP, packed by scripts/build_tfassets.sh). idle_anim=(0,1,0) + active_anim=(0,1,0) match TD source which has no STRUCT_HAND _anims[] entries.",
}


# ---------------------------------------------------------------------------
# Registry — add new entries here so --all picks them up.
# Order = rules.ini emission order when running with --all.
# ---------------------------------------------------------------------------

ALL = [
    TDNUKE,
    TDNUK2,
    TDPROC,
    TDSILO,
    TDPYLE,
    TDHAND,
    TDAFLD,
    TDGUN,
    TDSAM,
    TDOBLI,
    TDTMPL,
    TDHQ,
    TDFIX,
    TDWEAP,
    TDHPAD,
    TDGTWR,
    TDATWR,
    TDEYE,
    TDFACT,
]


def by_name(ininame):
    '''Return the manifest entry for `ininame`, or raise KeyError.'''
    for entry in ALL:
        if entry["ininame"] == ininame:
            return entry
    raise KeyError(ininame)
