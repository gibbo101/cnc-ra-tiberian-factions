# Adding a TD building as a buildable in our RA mod

End-to-end recipe to add a new TD-themed building to the GDI or Nod faction. Verified against `NUK2` (Phase 1f, 2026-05-18) and re-verified against `TDNUKE` (v0.3 phase 3a, 2026-05-19, after the lessons below were absorbed).

## v0.3 lessons (must read before adding new entries)

Three non-obvious gotchas the recipe didn't originally cover. Skip these and the entry registers but doesn't behave correctly.

### 1. IniName collisions silently break the entry

`[NewBuildings]` registration in `rules.cpp` only creates a mod entry when `BuildingTypeClass::As_Pointer(buffer) == NULL`. So if your IniName matches a vanilla RA building (HPAD, GUN, SAM, AFLD, WEAP, FIX, PROC, SILO, FACT) the registration is skipped silently and your `[<NAME>]` section overrides the **vanilla** building instead.

Similarly, INI section names live in a flat namespace: warhead/animation/sound sections share it. `NUKE` is a vanilla RA WarheadType. If you register a building with that IniName, `[NewBuildings]` succeeds (warheads aren't BuildingTypes) but `TechnoTypeClass::Read_INI` then sees the warhead's 7 entries (`Spread`, `Wall`, `Wood`, `Ore`, `Verses`, `Explosion`, `InfDeath`) instead of your building's fields. Result: building appears in the heap with default-everything (Ownable=0, Level=-1) and never builds.

**Rule:** prefix every catalogue IniName with `TD` (e.g. `TDNUKE`, `TDPYLE`, `TDHAND`). `Image=` and `Footprint=` and the sprite ZIPs keep the unprefixed TD asset name — those don't collide.

### 2. Damaged-state shape is auto-derived from Anims[BSTATE_IDLE].Count

When `Health_Ratio() <= ConditionYellow`, `BuildingClass::Shape_Number()` shifts the rendered shape by `largest = max(Anims[*].Start + Count)` across IDLE/ACTIVE/AUX1/AUX2. So:

- **Static building (Count=1):** largest=1, shape 1 = damaged variant. The recipe's "remap shape 1 to nuke-0004.tga" trick works here.
- **Animated building (Count=N):** largest=N, shape N = damaged variant of shape 0, shape N+1 = damaged of shape 1, etc. **Do NOT remap shape 1** — it's a normal idle frame in the cycle. The TGA frames are already laid out 0..N-1 normal, N..2N-1 damaged; the engine handles the shift automatically.

### 3. Mod entries don't inherit the donor's idle animation

`Logic=POWR` inherits POWR's BuildingTypeClass static fields (Size, OccupyList, ImageData, etc.) and POWR's Anims[]. But POWR has no idle anim entry in the hardcoded `_anims[]` table in `One_Time()`, so Anims[BSTATE_IDLE] is `{0, 1, 0}` (static). For a TD building with a cyclic idle (NUKE blinks, PYLE animates, HQ rotates dish), set rules.ini override fields:

```ini
IdleAnimStart=0
IdleAnimCount=4
IdleAnimRate=15
```

Per-building TD-authentic values are in the master flag table in `docs/catalogue.md`. The override is applied after Logic= aliasing in `BuildingTypeClass::Read_INI`.

### 4. Crewed / Repairable inherit from neither

`TechnoTypeClass::Read_INI` parses `Crewed=` and `Repairable=` from rules.ini, defaulting to the current value. For mod entries the current value is the dynamic ctor default (false / unset). Vanilla buildings get these from their `[POWR]`-style rules.ini section. So you must set `Crewed=yes` and `Repairable=yes` (or per-building TD values) explicitly in every entry, otherwise sell/destroy produces no infantry and the wrench-tool can't target the building.

Per-building TD-authentic Crewed/Repairable/Capturable values: see master flag table in `docs/catalogue.md`. Notably: SILO/HPAD/SAM are Crew=no (TD canon); GTWR/ATWR/OBLI/GUN/SAM/EYE/TMPL are Capturable=no.

### 5. Points= is mandatory or the AI ignores the building

`TechnoTypeClass::Read_INI` (`redalert/techno.cpp:7067`) sets `Risk = Reward = Points = ini.Get_Int("Points", Points)`. The dynamic ctor initialises Points to 0 (`techno.cpp:6686-6687`). Logic= aliasing does **not** copy Risk/Reward/Points from the donor (`bdata.cpp:3731-3759`). So if you omit `Points=`, the building's `TechnoClass::Value()` (`techno.cpp:5171`) returns 0, and `Evaluate_Object`'s `if (value)` gate (`techno.cpp:1870`) silently rejects the candidate. **Symptom: enemy units walk past the building without engaging it; AI never sends attack waves at it.**

Fix: every TD entry needs `Points=N` where N is the TD-authentic RISK/RWRD value from the donor TD class in `tiberiandawn/bdata.cpp` (look for the `// RISK/RWRD: Risk/reward rating values.` comment in the BuildingTypeClass constructor). The full table is in `docs/catalogue.md`'s master flag table and reproduced in `docs/ai-targeting.md` with source-line citations.

Validated end-to-end 2026-05-19 on the Deck: with `Points=50` on `[TDNUKE]`, the AI sent its first attack wave directly at the player's TDNUKE.

### 6. MAKE-tileset shape 0 must be `<Frame />` (empty)

TD-source `*MAKE.ZIP` archives (the buildup animation) start internal frames at **0001**, not 0000. Frame index 0000 doesn't exist — it's the convention for "the empty placement marker" before construction starts.

If RA_STRUCTURES.XML emits shape 0 of a MAKE tileset pointing at `<Frame>tdfoomake\tdfoomake-0000.tga</Frame>`, the launcher tries to load a non-existent file the moment the building is placed → renders a **Petroglyph "missing asset" placeholder for one frame** → next frame proceeds to shape 1 (which exists) → buildup begins.

`scripts/bundle_assets.py` handles this automatically: MAKE tilesets emit `<Frame />` for shape 0 (`empty_first_shape=True` codepath). Vanilla RA's *MAKE.ZIPs have frame 0000 baked in, so the same XML pattern wouldn't break vanilla — but it would break us. **Anyone hand-editing a MAKE tileset block must use `<Frame />` for shape 0.**

### 7. Launcher derives ZIP filename from frame path's first segment

The launcher's tileset loader doesn't use the tileset `<Name>` to pick which ZIP to open. It uses the frame path's first segment (the part before the backslash):

```xml
<Frame>tdpyle\tdpyle-0000.tga</Frame>
```

→ Launcher looks for **TDPYLE.ZIP** in the `STRUCTURES/` folder, then for `tdpyle-0000.tga` inside it.

This has two consequences:

1. The **ZIP filename and the first frame-path segment must match** (case-insensitive on case-folding filesystems like wine, exact-match elsewhere).
2. **Internal frame filenames must use the same prefix** (`tdpyle-NNNN.tga`, not the original `pyle-NNNN.tga`). The MEG extraction produces unprefixed names, so `bundle_assets.py` repacks the ZIPs to apply the TD-prefix internally.

If you rename the outer ZIP but leave internal filenames untouched, the launcher loads the right ZIP but can't find the TGAs inside → Petroglyph placeholder for every frame.

### 8. Mod entries with TD-style sprites need Center_Coord() Sort_Y

`BuildingClass::Sort_Y` (`building.cpp:3476-3506`) has type-specific overrides for STRUCT_BARRACKS, STRUCT_REFINERY, STRUCT_HELIPAD, STRUCT_AIRSTRIP, STRUCT_REPAIR that return `Center_Coord()` (no south offset). Everything else falls through to a default that adds `Height * 256 / 3` to Y, pushing the sort point south of center.

For vanilla buildings the south offset is fine — their sprites don't extend visually past it. **For TD-style sprites which extend further south (the visual tail / bib), the default offset places the sort point ABOVE units standing in the building's visual extent, so the building draws on top of those units.**

`building.cpp` now has an explicit case: if `Class->ShapeWidth > 0 && Class->ShapeHeight > 0` (i.e. the entry has rules.ini `ShapeSize=`, which only mod entries do), use `Center_Coord()` instead of the offset. Vanilla buildings untouched; mod entries sort correctly.

### 9. HOUSE_GOOD detachment from HOUSEF_ALLIES gates Owner=

Since v0.2.0 detached `HOUSE_GOOD` from the `HOUSEF_ALLIES` bitmask (and same for HOUSE_BAD vs HOUSEF_SOVIET), `Owner=allies` on a vanilla unit no longer grants HOUSE_GOOD ownership. France/HOUSE_GOOD becomes unable to build anything except entries that explicitly include `GoodGuy` in their Owner= field.

For the interim (until we have TD-themed GDI/Nod infantry & vehicles), our mod's rules.ini bulk-patches every `Owner=allies` unit to `Owner=allies,GoodGuy` and every `Owner=soviet` unit to `Owner=soviet,BadGuy`. **Buildings are explicitly NOT patched** — the catalogue defines TD-prefixed building entries with explicit `Owner=GoodGuy` or `Owner=BadGuy`, so vanilla buildings shouldn't appear in either side's sidebar.

When introducing TD-specific infantry/units, revert the per-entry Owner expansion for those slots (remove `GoodGuy`/`BadGuy` from vanilla units that are being replaced by TD equivalents, so GDI/Nod only sees their own roster).

### 10. aftrmath.ini overrides rules.ini — patch both

`CCDATA/` ships two INI files: `rules.ini` and `aftrmath.ini` (Aftermath expansion overrides). The engine reads aftrmath.ini *after* rules.ini, so any entry present in aftrmath.ini wins — every field, including `Owner=`.

Symptom from the 2026-05-20 session: E3 (Rocket Soldier) wasn't buildable for GDI even though rules.ini's `[E3]` had `Owner=allies,soviet,GoodGuy,BadGuy`. The diagnostic showed E3's effective `Ownable=0xFF` (= `HOUSEF_ALLIES|HOUSEF_SOVIET`, no GDI/Nod bits) post-parse. Cause: aftrmath.ini's `[E3]` had `Owner=allies` and overwrote the rules.ini value.

When applying the Owner= bulk-patch (gotcha #9), apply the same rule to aftrmath.ini's units/infantry sections too. Same building exclusion list (FACF / WEAF / DOMF are decoy buildings; leave them untouched). See aftrmath.ini sections: STNK/CARR/CTNK/TTNK/DTRK/QTNK/MSUB/SHOK/MECH/LST/4TNK/4 (vehicles+vessels), E3/DOG (infantry), C2-C9/MISS/GNRL/CHAN/DELPHI (civilians).

Same trap will catch any future field-level override (TechLevel, Prerequisite, Cost, Strength, etc.). When adding a new vanilla-overrides patch, search both INIs for the section header.

### 11. RA armor strings ≠ TD armor enum names

RA's `ArmorName[]` (`const.cpp:138`) maps armor strings to enum values with only `none`, `wood`, `light`, `heavy`, `concrete`. TD source code refers to the same protection tiers as `ARMOR_ALUMINUM` / `ARMOR_STEEL` — material names. The C++ `enum` values (`ARMOR_ALUMINUM`, `ARMOR_STEEL`) exist in RA too (`defines.h:2769-2770`), they just map to different string spellings.

If a manifest uses `armor: "aluminum"` or `"steel"`, `CCINIClass::Get_ArmorType` → `Armor_From_Name` silently falls through to `ARMOR_NONE` — buildings take SA+HE bonus damage as if unarmored. Found 2026-05-20 by comparing against Reilsss's CnCinRA mod, which uses RA spellings.

Fix lives in `redalert/weapon.cpp:Armor_From_Name`: it now accepts `"aluminum"`/`"steel"` as aliases for `ARMOR_ALUMINUM`/`ARMOR_STEEL` so the manifest can read TD-naturally.

### 12. WEAP+WEAP2 two-layer compositing for Logic=WEAP

`BuildingClass::Draw_It` (`building.cpp:509`) hardcodes a second-layer draw for every building of `Type == STRUCT_WEAP`, passing the literal asset name `"WEAP2"` to `Techno_Draw_Object_Virtual`. RA's Allied War Factory is two-piece art: `WEAP.ZIP` is the foundation ramp, `WEAP2.ZIP` is the walls/roof + door-opening animation.

For `Logic=WEAP` mod entries, the donor's Type=STRUCT_WEAP triggers this overlay path even though our TD-sourced WEAP sprite is a single piece. Result: TD foundation rendered with vanilla RA walls/roof on top → hybrid building.

Fix: TD-prefixed entries now redirect the overlay lookup to `"TDWEAP2"` (`building.cpp:Draw_It`), and we bundle TD's `WEAP2.ZIP` as `TDWEAP2.ZIP` via the asset pipeline. TD's WEAP2 has 20 frames (full open-close animation); the 4-stage door model in RA's engine needs an XML remap so shape 3 lands on TD frame 9 (fully open) rather than frame 3 (1/3 open) — gotcha #13.

### 13. RA's 4-stage door model vs TD's 10-frame opening animation

`DoorClass::Door_Stage` (`door.cpp:177`) returns 0..N-1 where N is the number of stages declared when the door was opened (`Open_Door(DOOR_RATE, DOOR_STAGES)` in `Mission_Unload` — RA uses `DOOR_STAGES = 5`, so shape numbers 0..4 in normal state, +4 for damaged). TD's WEAP2 source has 20 frames: 0..9 is the normal opening sequence (closed → fully open), 10..19 is the damaged-state sequence.

If the XML tileset for `TDWEAP2` maps shape 0..3 to TD frames 0..3, the door only animates to 1/3 open before stopping. `bundle_assets.py` doesn't know about door stages — the remap has to be applied manually in `RA_STRUCTURES.XML`:

```
shape 0 → tdweap2-0000.tga (closed)
shape 1 → tdweap2-0003.tga (1/3 open)
shape 2 → tdweap2-0006.tga (2/3 open)
shape 3 → tdweap2-0009.tga (fully open)
shape 4 → tdweap2-0010.tga (damaged closed)
shape 5 → tdweap2-0013.tga
shape 6 → tdweap2-0016.tga
shape 7 → tdweap2-0019.tga (damaged open)
```

### 14. Vanilla RA's `Track13` is `#if (1)`-overridden to pure-south

`redalert/drive.cpp:1930` has two `Track13[]` definitions:

```cpp
#if (1)
DriveClass::TrackType const DriveClass::Track13[] = {
    {XYP_COORD(0, -35), DIR_S}, ...  // pure-south version, ACTIVE
};
#else
DriveClass::TrackType const DriveClass::Track13[] = {
    {XYP_COORD(10, -21), (DirType)(DIR_SW - 10)}, ...  // SW version, dead code
};
#endif
```

The active pure-south Track13 contradicts `TrackControl[66]`'s declared `DIR_SW` final facing — vanilla RA WEAP exits south but `Mission_Unload` then sets the unit's final facing to SW. The SW Track13 in the `#else` block is what TrackControl was designed for (and what TD's source uses). Took the per-tick `Coord` log (`tf_weap_track.log` diagnostic in `drive.cpp:While_Moving`) to spot — the math kept saying "no snap should happen" because I was reading the dead SW version while the engine ran the south one.

Final fix: keep RA's pure-south Track13 active (vanilla Allied AI exit unchanged), ADD a new Track14 = SW variant (replicates the old `#else` block), add new `TrackControl[67]` and `OUT_OF_WEAPON_FACTORY_TD` enum. Vanilla WEAP (vanilla Allied players, AI) uses Track13 south as RA shipped; our TD `Logic=WEAP` entries call `Force_Track(OUT_OF_WEAPON_FACTORY_TD)` from `BuildingClass::Mission_Unload` and get TD-authentic SW motion.

### 15. WEAP `Exit_Object` flow has its own STRUCT_WEAP case — separate from default

`BuildingClass::Exit_Object` (`building.cpp:2050`) has switch cases for vehicle factories. STRUCT_WEAP at `building.cpp:2146` is a SPECIFIC case that:

- Unlimbo's the vehicle at `Exit_Coord()` with hardcoded `DIR_S` (vanilla — we now gate to `DIR_SW` for TD-prefixed entries)
- Sets `IsTethered=true` on the vehicle via `RADIO_TETHER`
- Puts the BUILDING on `MISSION_UNLOAD` (not the vehicle)

The actual door-open + vehicle-drive-out logic runs in `BuildingClass::Mission_Unload` (`building.cpp:5009`), which:

1. Opens the door over `DOOR_STAGES * DOOR_RATE` ticks
2. Once `Is_Door_Open()`, calls `unit->Force_Track(OUT_OF_WEAPON_FACTORY, coord)` — this picks Track13 via `TrackControl[66]`

For TD entries we override the `coord` (Track13 destination) to `Adjacent_Cell(Center_Coord(), FACING_SW)`. Combined with SW Track13 (gotcha #14), `Track13[0]` lands at exactly the Unlimbo spawn position — zero snap. We also call `Assign_Destination(::As_Target(cell))` after Force_Track so the unit continues path-finding after Track13 ends (Track13 alone ends inside the building's SW corner cell).

If you add another vehicle-producing TD building (e.g., TDAFLD for Nod), expect to extend the STRUCT_WEAP case and Mission_Unload accordingly, or model the new behaviour after this case.

---

## What "adding" means here

A new `[NewBuildings]` entry in our mod's `CCDATA/rules.ini` that the engine treats as a Logic-aliased clone of a vanilla RA building (POWR, BARR, etc.) for behaviour, but presents to the player with custom identity:

- Custom sidebar icon
- Custom display name (e.g. "GDIPowerPlant")
- Custom cost / power / strength
- TD building sprite on the map (buildup → idle → damaged)
- TD building's actual placement footprint shape
- Configurable Owner= to restrict to GDI or Nod

The engine still thinks it's a power plant (or whatever donor we picked) — that's how we get factory queueing, prerequisite handling, AI behaviour, and crew/death mechanics for free.

## Pre-flight: identify the donor and the TD source

For each building, decide:

1. **Donor** — the closest vanilla RA building whose engine behaviour we want. POWR for power plants, BARR/TENT for barracks, PROC for refineries, etc. (See `tiberiandawn/bdata.cpp` for the full RA BuildingType list.)
2. **TD asset name** — the TD building's IniName. This is also our entry's IniName (e.g. `NUK2`, `HAND`, `PYLE`).
3. **TD footprint** — look up the TD building's Size/OccupyList/OverlapList in `tiberiandawn/bdata.cpp`.

## Step 1: rules.ini entry

In the mod's `CCDATA/rules.ini`:

```ini
[NewBuildings]
1=NUK2
; add more here as you build out the faction

[TDNUK2]
Logic=APWR             ; engine behaviour donor (RA building class)
Image=NUK2             ; sprite + buildup asset name (matches the TD IniName)
Footprint=NUK2         ; named preset; must exist in bdata.cpp's _presets[] table
Name=Advanced Power Plant
TechLevel=5            ; TD source "Build level" — sidebar gating
Prerequisite=TDNUKE    ; STRUCTF_POWER in TD source — chain off our own NUKE, not vanilla
Owner=GoodGuy,BadGuy   ; HOUSEF_GOOD|HOUSEF_BAD; both factions get the advanced plant
Cost=700
Power=200              ; +N = generates; -N = consumes
Points=75              ; TD-authentic RISK/RWRD; mandatory or AI can't target it (see lesson 5)
Sight=2
Adjacent=1
Strength=300
Armor=wood
BaseNormal=yes         ; counts as a real base structure for AI defense logic
Capturable=true
Crewed=true            ; sell/destroy spawns infantry (TD canon — see lesson 4)
Repairable=yes         ; wrench-tool can target (TD canon — see lesson 4)
Bib=yes
; Defensive entries (TDGTWR/TDATWR/TDOBLI/TDGUN/TDSAM) additionally need:
; Primary=<weapon>     ; RA donor's weapon — TD weapons don't exist in RA's table
; Secondary=<weapon>   ; only if the donor uses one (AGUN does)
```

Notes on field choices:
- `Owner=allies` includes HOUSE_GOOD via `HOUSEF_ALLIES` (per `defines.h:1158`). For GDI as eventual standalone faction, switch to `good` once `HOUSEF_GOOD` is its own owner set.
- The `[NewBuildings]` ordinal (1, 2, …) is the entry order. The DLL's dynamic ctor uses `BuildingTypes.Count() - 1` as the actual heap slot, not the ordinal, so ordinal values don't matter beyond uniqueness within the section.

## Step 2: RA_Structures.xml tile entries

Copy the TD building's `<Tile>` blocks from vanilla `TD_Structures.xml` (extracted via `scripts/meg_extract.py` from `CONFIG.MEG`) into the mod's `Data/XML/TILESETS/RA_STRUCTURES.XML`.

The blocks include both `<Name>NUK2</Name>` (idle shapes 0-N) and `<Name>NUK2MAKE</Name>` (buildup animation shapes). Insert them inside the existing `<TilesetTypeClass name="RA_Structures"><Tiles>...</Tiles>` block, before the closing `</Tiles>`.

The mod's RA_Structures.xml is wholesale-loaded by the launcher when present (no merge with vanilla). It must include the full vanilla RA tile list + your additions.

Workflow:

```bash
# Extract vanilla files (one-time)
python3 scripts/meg_extract.py extract ~/.steam/steam/steamapps/common/CnCRemastered/Data/CONFIG.MEG "RA_STRUCTURES.XML" /tmp/vanilla-xml/
python3 scripts/meg_extract.py extract ~/.steam/steam/steamapps/common/CnCRemastered/Data/CONFIG.MEG "TD_STRUCTURES.XML" /tmp/vanilla-xml/

# Extract the TD building's Tile blocks (NUK2 example)
awk '/<Tile>/{block=""; in_tile=1} in_tile{block=block$0"\n"} /<\/Tile>/{ if (block ~ /<Name>NUK2(MAKE)?<\/Name>/) printf "%s", block; in_tile=0; block="" }' /tmp/vanilla-xml/TD_STRUCTURES.XML > /tmp/td-blocks.xml

# Insert into mod's RA_Structures.xml before the closing </Tiles></TilesetTypeClass>
# (manual or scripted edit)
```

### Damaged shape remap (recommended)

After buildup, the engine renders shape 0 for full-health and shape 1 for damaged (when Health_Ratio <= ConditionYellow, per `BuildingClass::Shape_Number()`). Vanilla TD's tile blocks have shape 1 as the next frame of idle, not a damaged variant. To get a proper damaged sprite, remap the entry's `<Shape>1</Shape>` Frame to point at the TD damaged frame (usually index 4):

```xml
<Tile>
    <Key><Name>NUK2</Name><Shape>1</Shape></Key>
    <Value><Frames><Frame>nuk2\nuk2-0004.tga</Frame></Frames></Value>
</Tile>
```

Verify by viewing the frame TGAs after extracting the ZIP — TD's convention is frames 0-3 normal/idle, 4+ damaged.

### Don't fill NUK2MAKE shape 0

Vanilla TD's MAKE tile blocks have shape 0 as `<Frame />` (empty). That's intentional — it's the placement marker before buildup starts. Filling it causes the completed sprite to flash for a frame before buildup begins, which looks broken. Leave shape 0 empty.

## Step 3: Ship the sprite ZIPs

Extract the TD building's idle and buildup ZIPs from the vanilla TD PAK:

```bash
python3 scripts/meg_extract.py extract ~/.steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_TD_SRGB.MEG "NUK2" /tmp/nuk2-zips/
# Produces: NUK2.ZIP, NUK2MAKE.ZIP
```

Copy to the mod's `Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES/` (note: RA path, not TD — the launcher in RA mode resolves asset paths under current-game's root). Same convention as Reilsss's mod.

The ZIPs contain `<name>-NNNN.tga` files at root, which the launcher resolves via the tile entry's `<Frame>name\name-NNNN.tga</Frame>` path (the ZIP basename becomes the path segment).

## Step 4: Footprint preset in bdata.cpp

The Logic= donor inherits Size/OccupyList/OverlapList from POWR (or whatever donor), which won't match the TD building's actual shape. Override via the `Footprint=` named preset.

In `redalert/bdata.cpp` `BuildingTypeClass::Read_INI`, find the `_presets[]` table after the Logic= block and add an entry. Use TD's static list arrays as a reference for the shape:

```cpp
// Defined alongside the existing presets:
static short const List_HAND_OCCUPY[]  = {0, 1, MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL};
static short const List_HAND_OVERLAP[] = {REFRESH_EOL};

static FootprintPreset const _presets[] = {
    {"NUK2", BSIZE_22, List_NUK2_OCCUPY, List_NUK2_OVERLAP},
    {"HAND", BSIZE_22, List_HAND_OCCUPY, List_HAND_OVERLAP},  // ← new entry
    // ...
};
```

The lists come from `tiberiandawn/bdata.cpp`. Most TD buildings use shared lists like `List1011` (which is `{0, MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL}`) — you can copy the literal array contents, or define a single shared static and reference it from multiple presets.

Rebuild the DLL after adding a preset.

## Step 5: Sidebar XML entry

In the mod's `Data/XML/OBJECTS/UNITS/RABUILDABLES.XML`, append:

```xml
<ObjectTypeClass Name="RA_NUK2" Classification="CNCBuildableObject" CanInstantiate="False">
    <CNCEncyclopediaComponent>
        <ObjectNameTextID>TEXT_STRUCTURE_TITLE_GDI_POWER_PLANT</ObjectNameTextID>
        <ObjectDescriptionTextID>TEXT_STRUCTURE_DESC_GDI_POWER_PLANT</ObjectDescriptionTextID>
        <BuildIcon>BuildIcon_TD_PowerPlant</BuildIcon>
    </CNCEncyclopediaComponent>
</ObjectTypeClass>
```

The Name is `RA_<IniName>` — the launcher prepends the game-prefix automatically.

`<BuildIcon>` references a `BuildIcon_*.tga` filename. For TD buildings, vanilla TD's BuildIcon names work (e.g. `BuildIcon_TD_PowerPlant`, `BuildIcon_TD_HandOfNod`). The launcher's PAK contains these icons; no shipping needed unless we want a custom icon.

Text IDs can be vanilla too (`TEXT_STRUCTURE_TITLE_GDI_POWER_PLANT` already exists in the launcher's localized text). For custom names, ship a text override XML.

## Step 6: Test loop

```bash
# Build DLL (only if you added a Footprint preset)
CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake VC_CXX_FLAGS="-w;-fpermissive" cmake --workflow --preset remaster

# Deploy to Steam Deck
scp build/remaster/Vanilla_RA/Data/RedAlert.dll deck@steamdeck:/home/deck/.steam/steam/steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/CnCRemastered/Mods/Red_Alert/<mod-name>/Data/RedAlert.dll

# Data files (rules.ini, XML, ZIPs)
scp -r CCDATA Data deck@steamdeck:/home/deck/.steam/steam/steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/CnCRemastered/Mods/Red_Alert/<mod-name>/
```

Restart the game, build the new entry from the sidebar, check:

- Sidebar icon + display name + cost match
- Buildup animation plays correctly
- Idle sprite renders (TD-style)
- Damaged variant appears when attacked
- Placement footprint matches TD's actual shape
- Multiple instances can coexist with vanilla buildings

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Entry doesn't appear in sidebar | Owner= doesn't match player's house, or Prerequisite= not satisfied | Check `Owner=` vs current house, lower TechLevel, remove Prerequisite |
| Click on completed sidebar entry → cancels with "Cannot Comply" | Who_Can_Build_Me fails (Construction Yard's ActLike doesn't match Ownable) | Check Owner= bitmask covers the player's ActLike |
| Buildup plays, then invisible building | ImageData NULL | Verify `Logic=<donor>` is set and donor exists |
| Building visible but no damaged state | NUK2 shape 1 still points at idle frame | Remap to damaged frame in RA_Structures.xml |
| Premature sprite reveal before buildup | NUK2MAKE shape 0 has a real Frame instead of `<Frame />` | Restore empty `<Frame />` |
| Placement grid wrong shape | Inheriting donor's footprint, no preset override | Add `Footprint=<name>` to rules.ini + matching preset to bdata.cpp |
| `TileMapClass: Missing tile for <NAME>` in launcher log | Tile entries not in mod's RA_Structures.xml | Add `<Tile>` blocks from TD_Structures.xml |
| Launcher log shows `Failed to find texture "<name>-0000.tga"` | ZIP not shipped at RA path, or filename mismatch | Verify ZIP at `Red_Alert\Structures\<NAME>.ZIP` with `<name>-NNNN.tga` inside |

## Diagnostic re-enable

If you hit a new failure mode and need DLL-side visibility, all diagnostic hooks from the 2026-05-18 session are documented inline with `// Diagnostic hook removed 2026-05-18` comments showing where to re-insert and what to log. Search for the comment to find re-enable points.

Use absolute Wine path `C:\users\steamuser\Documents\CnCRemastered\MOD_DEBUG.txt` for fopen — relative paths fail silently under Wine.

Rate-limit per-frame logs (e.g., `static int count; if (count++ < 60)`) to avoid flooding.
