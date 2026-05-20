# Building catalogue — Tiberian Factions for Red Alert

Design spec for the new buildings we're adding via the Logic-aliased mod-building pipeline (see `docs/adding-td-buildings.md` for the per-building implementation recipe). Stats below are pulled from `tiberiandawn/bdata.cpp` — TD-authentic by default. See `docs/manifest-gaps.md` for which engine rules.ini fields the manifest emitter can/can't currently produce, and the recommended add order before the catalogue rollout broadens.

## TEMPORARY DEV HACKS — remove before v1.0 / public release

These are local-only diagnostics that must not ship. Each lives behind a `#if 1`
so disabling is a one-line flip; deletion is also fine.

- **Skirmish reveal-all** — `redalert/scenario.cpp` at the tail of
  `Start_Scenario` (just before `BEnd(BENCH_SCENARIO); return (true);`).
  Mirrors `TACTION_REVEAL_ALL` from `taction.cpp`: sets
  `PlayerPtr->IsVisionary = true` and maps every cell to the player for any
  non-campaign session. Added 2026-05-19 to observe 7-AI skirmish behaviour
  during D1.2 Phase 1 validation. Turn off: flip the `#if 1` to `#if 0`, or
  delete the whole block. Search for `TEMPORARY DEV HACK — reveal the full map`.

- **`Can_Build` diagnostic logger** — `redalert/house.cpp:838-872`.
  Writes `MOD_DEBUG_CANBUILD.txt` to the user's Documents/CnCRemastered folder
  whenever `Can_Build` runs against an IniName starting with `TD`. Per
  [[feedback-keep-diagnostics-until-v1]], stub the body under `if (0)` instead
  of deleting so re-enable is a one-line flip.

- **`tf_*` log files** — various `fopen` diagnostics under
  `%USERPROFILE%/Documents/CnCRemastered/` (`tf_draw_intercept.log`,
  `tf_mod_one_time.log`, `tf_can_build.log`, etc.). Each is per-IniName rate-
  limited. Same retention policy as Can_Build above.

- **Instant build for GDI / Nod** — `redalert/techno.cpp` in
  `TechnoTypeClass::Time_To_Build`. Forces 15 ticks (~1 s) return for any
  build queued by `HOUSE_GOOD` / `HOUSE_BAD` (France→GDI / USSR→Nod players
  via the launcher swap). Vanilla houses keep their full Cost-derived build
  times so AI cadence is unaffected. Added 2026-05-20 for catalogue rollout
  testing. Search for `TEMPORARY DEV HACK — instant build` to remove; flip
  `#if 1` to `#if 0` to disable without deleting.

## Session pickup

### End of 2026-05-20 — Pipeline rebuild + 3 buildings + GDI playable

**This session's wins (uncommitted at write time; commit imminent):**

- **`scripts/bundle_assets.py` (new ~280 lines)** — end-to-end asset bundler. Extracts sprite ZIPs from `TEXTURES_TD_SRGB.MEG`, repacks with TD-prefixed internal frame filenames, patches `RA_STRUCTURES.XML` tilesets (with empty `<Frame />` for MAKE shape 0), patches `RABUILDABLES.XML` for sidebar wiring. Idempotent — re-running replaces in place.
- **`scripts/add_building.py` (extended)** — now orchestrates the full pipeline: rules.ini emit → `[NewBuildings]` reg → asset bundling. One command per building, right first time. `--skip-assets` flag for rules-only runs.
- **`deploy.sh` (rewritten)** — `rsync -av --delete` mirror to the Deck. Drift between local and Deck is now impossible; orphan files on the Deck get cleaned automatically. Confirmation prompt on first run (skip with `--yes`).
- **Manifest schema extended** — added `td_asset` (was `image`; semantic split: source MEG asset name vs rules.ini `Image=` value, which now uses IniName uniformly). New fields: `shape_size`, `text_id_name`, `text_id_desc`, `build_icon`.
- **TD-prefix convention applied uniformly** — ZIP filenames, XML tileset `<Name>`, rules.ini `Image=`, internal frame filenames, and frame path prefixes all consistently TD-prefixed (`TDNUKE.ZIP` containing `tdnuke-NNNN.tga`, referenced as `<Frame>tdnuke\tdnuke-0000.tga</Frame>`). Avoids vanilla name collisions for WEAP/FIX/HPAD/SAM when we get to those.
- **Three buildings landing right first time**: TDNUKE, TDNUK2, TDPYLE all render correctly, correct cameos, correct tooltips ("Power Plant" / "Adv Power Plant" / "Barracks"), buildup animations, idle animations.
- **TDPYLE infantry production works** — Logic=TENT (Allied barracks, not Soviet BARR — important).
- **Petroglyph flash on placement → fixed** — TD-source MAKE ZIPs start frames at 0001, not 0000. XML shape 0 must emit `<Frame />` (empty). Documented as gotcha #6 in `docs/adding-td-buildings.md`. Pipeline handles it via `empty_first_shape=True` on MAKE tilesets.
- **Unit Z-order under TD buildings → fixed** — `BuildingClass::Sort_Y` in `building.cpp` now returns `Center_Coord()` for any entry with explicit `ShapeSize=` (mod entries only; vanilla untouched). TD sprites extend further south than vanilla's default offset accounts for.
- **Owner= bulk patch** — every vanilla `Owner=allies` unit/infantry now `Owner=allies,GoodGuy`, every `Owner=soviet` now `Owner=soviet,BadGuy`. Buildings explicitly excluded. Interim until we have TD-themed infantry/vehicles; gives GDI/Nod a playable unit roster from vanilla.
- **D1.2 Phase 1 (literal prereqs for mod IniNames) still landed** — committed earlier (`cddc856` `v0.3.0-phase4a`). TDNUK2 actually requires TDNUKE.

**Working tree state at session end:**

```
Modified DLL sources:
  redalert/bdata.cpp           — PYLE footprint preset (top-row occupy + bottom-row overlap)
  redalert/building.cpp        — Sort_Y mod-entry fix
  redalert/dllinterface.cpp    — diagnostic logging (TD-prefix Draw + AssetName)
  redalert/scenario.cpp        — TEMPORARY reveal-all hack, NOT for commit

New scripts:
  scripts/bundle_assets.py
  scripts/buildings_manifest.py  (extended)
  scripts/add_building.py        (extended)

Data:
  resources/.../rules.ini                   — Owner bulk patch + E3 explicit + TDPYLE entries
  resources/.../RA_STRUCTURES.XML           — 99 new TD tileset shape entries
  resources/.../RABUILDABLES.XML            — RA_TDNUKE/TDNUK2/TDPYLE blocks
  resources/.../STRUCTURES/{TD*}.ZIP        — 6 repacked sprite ZIPs

Other:
  deploy.sh                    — rewritten as rsync mirror
  docs/adding-td-buildings.md  — gotchas 6-9 added
  docs/catalogue.md            — this pickup
```

### Next session — pick up here

**This session (2026-05-20, post-pipeline-rebuild) wins:**

- **E3 (Rocket Soldier) now buildable for GDI.** Root cause was `aftrmath.ini` overriding rules.ini's `Owner=allies,soviet,GoodGuy,BadGuy` with its own `Owner=allies` (Aftermath expansion INI loads after rules.ini and wins per-key). Diagnostic (`MOD_DEBUG_CANBUILD.txt`) showed E3's effective `Ownable=0xFF` = `HOUSEF_ALLIES|HOUSEF_SOVIET` only. Fix: bulk-patched aftrmath.ini's 23 non-building Owner= lines following rules.ini convention. New gotcha #10 in `docs/adding-td-buildings.md`.

- **Manifest schema extended**: `sensors` (bool) and `storage` (int) fields added to FIELD_SPEC. Documented in manifest.

- **Full GDI building roster shipped** (12 entries total — 8 new this session): TDPROC, TDSILO, TDFIX, TDWEAP, TDHPAD, TDGTWR, TDATWR, TDEYE on top of TDNUKE/TDNUK2/TDPYLE/TDHQ. All build, all render with TD-authentic sprites, all functional on the Deck.

- **TDWEAP exit deep-dive.** What looked like a simple Logic=WEAP entry turned into 5+ engine-level fixes (8 hours of investigation, six rebuilds). Documented as gotchas #11-15:
  - **#11**: Armor parser strings — RA uses `light`/`heavy`, TD uses `aluminum`/`steel`. Manifest "aluminum"/"steel" was silently falling to `ARMOR_NONE`. Fixed in `Armor_From_Name` with aliases.
  - **#12**: `WEAP2` two-layer compositing — `BuildingClass::Draw_It` hardcodes a second-layer draw of `"WEAP2"` for any STRUCT_WEAP. Our TD WEAP sprite is single-piece so vanilla RA's yellow roof was rendering over TD's foundation. Fix: TD entries redirect overlay to `"TDWEAP2"`; TDWEAP2.ZIP bundled from TD source.
  - **#13**: Door-stage XML remap — RA uses 4 door stages, TD's WEAP2 has 20 frames (10 normal + 10 damaged). Tileset shapes 0-3 must map to TD frames 0,3,6,9 so the door fully opens.
  - **#14**: **The smoking gun** — `redalert/drive.cpp:1930` has TWO `Track13[]` definitions under `#if (1) / #else`. The pure-south version is active despite `TrackControl[66]` declaring `DIR_SW` final facing. The SW Track13 in the `#else` block is dead code that matches TD's authentic SW exit. Initially flipped to `#if (0)` — caused vanilla Allied WEAP to also use SW (which is not what RA shipped). Final fix: kept Track13 as RA's pure-south, ADDED Track14 (= old #else SW version), added `OUT_OF_WEAPON_FACTORY_TD = 67` enum, added `TrackControl[67] = {14, 14, DIR_SW, F_}`. Vanilla Allied AI WEAP exit is now bit-identical to RA original (confirmed via 2026-05-20 playtest); TD entries get TD-authentic SW exit. Eight hours of "but the math says zero snap" because we kept reading the SW version while the engine ran the south one. Per-tick `Coord` diagnostic in `drive.cpp:While_Moving` finally caught it.
  - **#15**: `Exit_Object` STRUCT_WEAP case + `Mission_Unload` interaction. Documented the door-open → Force_Track(SW Track13) → continued Assign_Destination chain. TD entries get TD-authentic SW exit; vanilla WEAP kept south-exit behaviour for Allied AI compatibility.

- **1-second-build dev hack** for HOUSE_GOOD/HOUSE_BAD players. `TechnoTypeClass::Time_To_Build` returns 15 ticks for testing iteration. Documented in TEMPORARY DEV HACKS section.

- **`scenario.cpp` reveal-all dev hack** preserved from earlier session (`#if 1`).

**Diagnostics added this session and kept active per [[feedback-keep-diagnostics-until-v1]]:**
- `MOD_DEBUG_CANBUILD.txt` extended with E*-prefix infantry tracking
- `tf_exit_object.log` (Exit_Object default-case capture)
- `tf_weap_unlimbo.log` (TDWEAP Mission_Unload Force_Track capture)
- `tf_weap_track.log` (per-tick Coord during Track13 — voluminous; consider disabling under `#if 0` if log volume becomes a problem)

### Building bugs found during 2026-05-20 playtest (parked for next session)

User playtest after the GDI roster shipped surfaced these — bundled into a
"next session" list rather than fixed inline so we can close this session
cleanly. All are GDI building issues (harvester behaviour, powers etc. are
deferred until the unit catalogue work). Numbers match the user's report:

1. **TDPROC / TDSILO storage values 10× too high.** Currently TDPROC stores
   20000, TDSILO 15000. User reports they should be 2000 and 1500. Check the
   rules.ini emit — our manifest has `storage: 1000` / `storage: 1500`
   respectively but `Storage=` is being emitted with an extra zero somewhere.
   Suspect: NightFalcon101's MODERATE_WARFARE patches in vanilla RA rules.ini
   bumped storage 10×; our manifest emit may be inheriting that base. Search
   `Storage=15000` / `Storage=20000` in rules.ini and trace.

2. **TDPROC idle animation breaks after first harvester return.** Refinery
   animates normally on build. When the harvester returns and docks, the
   `IdleAnim` cycle stops and never restarts. Likely the donor's BSTATE
   transitions (`BSTATE_ACTIVE`/`BSTATE_AUX1` siphoning cycles in TD's source
   per `tiberiandawn/bdata.cpp:3814`) take over and our `IdleAnim*` override
   never re-engages. Also (parked): there should be a *visible* "returning"
   indicator on TDPROC when a harvester is on its way back, so the player
   knows ore is incoming.

3. **TDSILO renders with a 1×1 placement grid, should be 2×2.** Our manifest
   has `shape_size: (48, 24)` (2 wide × 1 tall) but no `footprint` override,
   so it inherits the RA SILO donor's BSIZE_21 footprint. TD-authentic is
   2×2. Needs both a new `SILO` Footprint= preset in `bdata.cpp` (BSIZE_22
   with appropriate occupy/overlap lists) AND `shape_size: (48, 48)` in the
   manifest so the launcher renders the sprite at the correct 2-cell-tall
   scale. Cross-check against TD's source `tiberiandawn/bdata.cpp` ClassSilo
   for the authentic ListSilo / OListSilo cell pattern.

4. **TDEYE renders no on-map sprite + has a 2×2 placement grid, should be
   L-shape (top-row overlap + bottom-row occupy, like NUK2).** Two bugs:
   (a) sprite invisibility — TDEYE.ZIP is bundled and tileset XML wired
   (verified during deploy), so the rendering failure is engine-side. Check
   if the Logic=MSLO donor's `ImageData` inheritance produces something the
   launcher can't resolve (similar to gotcha #1 IniName collisions class).
   (b) footprint — Logic=MSLO inherits BSIZE_21 (2×1 missile silo), not the
   2×2 L-shape TD's EYE actually has. Needs a new `EYE` preset in bdata.cpp
   matching NUK2's `List_NUK2_OCCUPY` / `List_NUK2_OVERLAP` pattern.

5. **TDGTWR and TDATWR have no weapons.** Towers exist on the map but don't
   fire. Logic=PBOX and Logic=AGUN donors do have weapons in their
   constructors, but the Logic= alias may not be copying `PrimaryWeapon` /
   `SecondaryWeapon` pointers. Quick fix: explicitly set `primary=` in the
   TDGTWR / TDATWR manifest entries (matching docs/catalogue.md's weapon-port
   placeholder table — Vulcan for GTWR, TurretGun+Nike for ATWR). If that
   doesn't take effect, the deeper issue is `BuildingTypeClass::Read_INI`'s
   weapon-pointer lookup vs. our Logic= ImageData inheritance path.

**Immediate next work — finish GDI building roster:**

Remaining catalogue entries per the master flag table:
- **TDHQ** (Communication Center) — Logic=DOME. Needs `sensors=true` field in manifest (radar). See `docs/manifest-gaps.md` Priority-2 list.
- **TDEYE** (Advanced Comm / Ion Cannon host) — Logic=ATEK or similar. `sensors=true`. Superweapon binding TBD.
- **TDWEAP** (Weapons Factory) — Logic=WEAP. Donor IniName collides — `Image=TDWEAP` (not `WEAP`) is critical here.
- **TDFIX** (Repair Facility) — Logic=FIX. Same collision concern.
- **TDGTWR** / **TDATWR** (Guard Tower / Advanced Guard Tower) — Logic=PBOX or TURR. `primary=` weapon needed.
- **TDHPAD** (Helipad) — Logic=HPAD. Collision.
- **TDPROC** (Refinery, shared GoodGuy,BadGuy) — Logic=PROC. Needs `storage=N` field.
- **TDSILO** (Storage, shared) — Logic=SILO. Needs `storage=N`.

**Manifest schema additions needed before that batch:**
- `sensors` (bool) — for TDHQ, TDEYE
- `storage` (int) — for TDPROC, TDSILO

Both are simple FIELD_SPEC additions in `scripts/add_building.py`. Per `docs/manifest-gaps.md`.

**TDAFLD (Nod airstrip) engine work — learning from TDWEAP:**

The TDWEAP investigation (gotchas #11-15) established a template for any vehicle-producing TD building. TDAFLD will need its own version:

- Separate `Track15` (or whatever the next slot is) for the airstrip cargo-plane delivery animation, with its own `TrackControl` entry and `OUT_OF_AIRSTRIP_TD` enum. Vanilla doesn't have an `OUT_OF_AIRSTRIP` track — vehicles spawn on the airstrip tile directly in RA. TD's airstrip animates a cargo plane landing → unloading → leaving.
- Its own STRUCT_WEAP-like case in `BuildingClass::Exit_Object` (or extend the existing case to also fire for TDAFLD).
- Its own door-stage XML remap if the airstrip-open animation has different frame ranges than RA's.
- Possibly a custom Unlimbo direction for the cargo plane drop.

Reilsss's CnCinRA mod gave up on this and reused the GDI weapons factory for Nod — we can do better with the split-track pattern we've now proven works. Plan: when we get to Nod, replicate the TDWEAP split (Track14/Track15 + enum + Mission_Unload branch) for the airstrip.

**Then Nod buildings:**
- TDHAND (Logic=BARR — Soviet barracks), TDGUN, TDSAM, TDOBLI, TDTMPL. Bib note for TDHAND: per catalogue table it's `2×3 footprint`, needs its own `_presets[]` entry in `bdata.cpp`.

**Then unit catalogue:**
- TD-themed infantry (TDE1, TDE2, TDE3, etc.) replacing the temporary `Owner=allies,GoodGuy` patch on vanilla units. New `scripts/add_infantry.py` (or extend `add_building.py` for RTTI_INFANTRYTYPE).
- TD-themed vehicles + aircraft similarly.

**Deferred architectural items still parked:**
- D1.2 Phase 2 — delete BScan/ActiveBScan/OldBScan, migrate all consumers. See task `#8`.
- Classic-mode TD SHPs — bundle CONQUER.MIX assets into a mod mixfile for LAN play. See ImageData inheritance note in this file.
- HOUSE_BAD launcher swap — France→HOUSE_GOOD is wired (dllinterface.cpp:899), but Nod has no equivalent. Probably USSR→HOUSE_BAD or Germany→HOUSE_BAD as the next paired swap.

### End of 2026-05-19 — Pre-pipeline state (archived)

**Current state (end of 2026-05-19, v0.3.0-phase3d committed — D1.1/D1.1b done, D1.2 pending fresh session):**

What works end-to-end on the Deck:
- **TDNUKE** — sidebar icon, TD sprite, 2×2 footprint, buildup → idle anim cycling, damaged auto-shift, sell/destroy spawns crew, AI targets it (Points=50), prereq chain works, **correct scale (ShapeSize=48,48)**
- **TDNUK2** — sidebar entry, prereq gate (requires power plant), placement, AI targets it (Points=75), **correct scale matching TDNUKE (ShapeSize=48,48)** — visually verified on Deck 2026-05-19
- `scripts/add_building.py` + `scripts/buildings_manifest.py` — manifest-driven rules.ini emission, idempotent, [NewBuildings] auto-registration. Smoke-tested on TDNUKE round-trip and TDNUK2 first generation. **Needs ShapeSize column added.**
- Prereq parser fix: `CCINIClass::Get_Buildings` now uses `BuildingTypeClass::As_Pointer` (heap-aware) instead of `From_Name` (vanilla enum range only), so `Prerequisite=TDxxxx` actually resolves.
- AI targeting fix: `Points=` mandatory field, all 19 entries in master table populated with TD-authentic RISK/RWRD values.
- **ShapeSize override (v0.3.0-phase3d, commit d69d09b):** EMC-style `ShapeSize=W,H` rules.ini directive overrides the `width`/`height` passed to `DLL_Draw_Intercept`. Without it, mod-entry SHPs aren't in `REDALERT.MIX` → `Get_Build_Frame_Width` returns 0 → launcher falls back to TGA-native scale → inconsistent rendering per asset. **Mandatory for every new TD entry**, convention W=Width()×24, H=Height()×24.
- Diagnostic infrastructure extended: `tf_draw_intercept.log` now per-IniName rate-limited (30 each) and logs `ImageData/BuildupData/CameoData` pointers; new `tf_mod_one_time.log` shows whether `MFCD::Retrieve` returned NULL for each mod entry's SHP. Confirmed `NUKE.SHP` / `NUK2.SHP` are NOT in `REDALERT.MIX` (legacy SHP path is effectively dead for mod entries — launcher uses AssetName+TGA pipeline directly).
- Deploy target consolidated: only `Mods/Red_Alert/Vanilla_RA/` on the Deck.

### What we learned this session about the launcher's render pipeline

The original D1.1 plan assumed "per-entry ImageData/BuildupData load fixes the scale" — that hypothesis was **wrong**. Diagnostic confirmed:
- After my D1.1 One_Time mod-entry loop: `ImageData=BuildupData=CameoData=NULL` (all `MFCD::Retrieve` calls returned NULL — neither `NUKE.SHP` nor `NUK2.SHP` lives in `REDALERT.MIX`).
- At Draw_It time, `ImageData`/`BuildupData` are *somehow* non-NULL — different pointers per entry, populated by an unidentified mechanism between One_Time and first draw (not blocking, but worth investigating later).
- `DLL_Draw_Intercept` receives `w=0 h=0` for **both** TDNUKE and TDNUK2 — same Size/W()/H()/Dim values, yet they rendered at very different scales pre-fix. So **width/height args weren't the scale driver**.
- The launcher's actual fallback when `w=h=0`: TGA-native pixel mapping. TD-Assets's NUKE and NUK2 TGAs are similar in canvas dimensions (~256×250) and opaque-pixel ratio (~80%), but the **building's bounding box within each TGA** is bigger for NUK2 — making it render ~50% larger on screen at identical CNCObjectStruct values.
- The fix (D1.1b): force the launcher to use **explicit dimensions** by passing non-zero w/h derived from `ShapeSize=` rather than from SHP data. Validated visually — TDNUKE and TDNUK2 now render at identical 2×2 scale.

The TD-Assets workshop docs ([Steam Workshop 3003163891](https://steamcommunity.com/sharedfiles/filedetails/?id=3003163891)) confirm this is the EMC-canonical approach: *"The mod does NOT automatically scale sprites... you must set the dimensions (width, height) manually."* Example shown: `ShapeSize=48,72` for HAND (2×3 foundation). DontCryJustDie's discussion thread has authoritative shape sizes for the full TD catalogue; XCC Mixer can extract the same data from TD's `CONQUER.MIX`. Subscribed to DontCryJustDie's example mod (3003174395) for canonical rules.ini patterns when we do the catalogue rollout.

### Known limitation — classic graphics mode

Mod entries still render their **donor sprites** in classic mode (POWR for TDNUKE, APWR for TDNUK2) because the legacy SHP renderer reads `ImageData` and our `ImageData` resolves to donor data (or NULL). Real fix would be bundling TD's `NUKE.SHP`/`NUK2.SHP`/etc. in a mod-specific mixfile (extract from `CONQUER.MIX`, register via `new MFCD("tiberian_factions.mix")` in init). **Deferred** — Remastered is the play target, LAN mode forces Remastered, low impact. README/CHANGELOG should note "Remastered graphics mode required for correct TD sprites."

### Next session — D1.2 full BScan replace

Originally scoped as half-day; grep showed actual surface is bigger (~6 files, 30+ references — `house.cpp` AI/sell/radar/save-load, `building.cpp` construction reg, `cell.cpp` crate spawning, `display.cpp` minimap, `tevent.cpp` event triggers, plus the prereq parser). Worth doing as a clean full session rather than a surgical hack.

**D1.2 scope:**

1. **Replace `BScan`/`ActiveBScan`/`OldBScan` 32-bit bitmasks with heap-sized counter arrays** indexed by Type (size = `BuildingTypes.Count()`).
2. **Update every BScan consumer** to use the new array. Most callers want "do I have any of type X?" — translates to `BuildingsOwned[X] > 0`. Group queries like `BScan & (STRUCTF_REFINERY | STRUCTF_CONST)` become explicit OR checks over the relevant Type slots.
3. **Prereq parser**: convert `Prerequisite=TDxxxx` from bitmask production to a literal `int PrerequisiteList[N]` of Type indices. `Can_Build` loops: `for each T in list: require BuildingsOwned[T] > 0`.
4. **Save/load migration** for the new HouseClass field layout (or `#ifdef`-gate the size change until format is bumped).
5. **Type-equality checks** (`if (building->Type == STRUCT_POWER) {...}`) — D2 territory via `BehavesLike=`, leave as-is for D1.

**Files to touch (verified via grep 2026-05-19):**
- `redalert/house.h`, `redalert/house.cpp` — HouseClass fields + all consumers
- `redalert/building.cpp:1159-1160` — registration on construction; corresponding decrement on destroy/sell
- `redalert/cell.cpp:2312, 2388, 2401, 2518` — crate spawning checks
- `redalert/display.cpp:4341, 4387` — minimap state checks
- `redalert/tevent.cpp:347, 357-358, 373, 464, 481` — event trigger predicates
- `redalert/type.h` — TechnoTypeClass `Prerequisite` field becomes a list
- `redalert/tdata.cpp` / `redalert/techno.cpp` — prereq parser (locate the actual function)

**D1.2 success criteria:**
- `Prerequisite=TDNUKE` literally requires TDNUKE built (not just any STRUCTF_POWER) — verify by trying to build TDNUK2 with only a vanilla POWR placed; should be blocked.
- TDNUKE/TDNUK2 don't regress in any vanilla-coupled path (AI behaviour, sell flow, radar, crate logic).
- Save/load round-trips cleanly.
- All vanilla buildings still resolve their own prereqs correctly (Tech Center → ATEK presence, etc.)

**D2 deliverables (parked):**
- `BehavesLike=` rules.ini field for Type-equality special cases (Iron Curtain, MSLO, GPS, etc.)
- `BQuantity` extension to mod heap
- Audit and clean up the `Logic=` aliasing code in `bdata.cpp:3731-3759` (most becomes obsolete after D1.2)

**Deploy target reminder:** scp to `Mods/Red_Alert/Vanilla_RA/`. Testbed folder is gone. See [[project-mod-building-pipeline]] memory for build/deploy recipe.

---

## Master flag table (TD-authentic, v0.3 source of truth)

Per-building flags extracted from `tiberiandawn/bdata.cpp`. These are the values `add_building.py` reads. **IniName** is the catalogue IniName (TD-prefixed); **Image/Footprint/sprite ZIPs** keep the unprefixed TD asset names.

| IniName | Faction | Donor | Cost | Power | HP | Sight | Adj | Armor | Bib | Cap | Crew | Repair | Idle:Start/Count/Rate | Points | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TDNUKE | both  | POWR | 300  | +100 | 200  | 2 | 1 | wood     | yes | yes | yes | yes | 0/4/15  | 50  | TD lvl 0 |
| TDNUK2 | both  | APWR | 700  | +200 | 300  | 2 | 1 | wood     | yes | yes | yes | yes | 0/4/15  | 75  | TD lvl 5, prereq TDNUKE |
| TDPROC | both  | PROC | 2000 | -40  | 900  | 4 | 1 | wood     | yes | yes | yes | yes | 0/6/4   | 55  | TD lvl 1, has dock/siphon cycles — keep RA donor behaviour |
| TDSILO | both  | SILO | 150  | -10  | 300  | 2 | 1 | wood     | yes | yes | no  | yes | —       | 16  | TD lvl 1 — capacity-based shape, not a cycle |
| TDPYLE | GDI   | TENT | 300  | -20  | 800  | 3 | 1 | wood     | yes | yes | yes | yes | 0/10/3  | 60  | TD lvl 0 |
| TDHAND | Nod   | BARR | 300  | -20  | 800  | 3 | 1 | wood     | yes | yes | yes | yes | 0/10/3  | 61  | TD lvl 0, 2×3 footprint |
| TDWEAP | GDI   | WEAP | 2000 | -30  | 1000 | 3 | 1 | aluminum | yes | yes | yes | yes | 0/1/0   | 86  | TD lvl 2, static idle |
| TDAFLD | Nod   | WEAP | 2000 | -30  | 1000 | 5 | 1 | steel    | yes | yes | yes | yes | 0/16/3  | 86  | TD lvl 2, 4×2, AIRSTRIP anim spec |
| TDHQ   | both  | DOME | 1000 | -40  | 1000 | 10| 1 | wood     | yes | yes | yes | yes | 0/16/4  | 20  | TD lvl 2, radar |
| TDEYE  | GDI   | MSLO | 2800 | -200 | 500  | 10| 1 | wood     | yes | **no** | yes | yes | 0/16/4 | 100 | TD lvl 7, GDI superweapon host |
| TDTMPL | Nod   | MSLO | 3000 | -150 | 1000 | 4 | 1 | aluminum | yes | **no** | yes | yes | 0/1/0  | 20  | TD lvl 7, Nod superweapon host |
| TDFIX  | both  | FIX  | 1200 | -30  | 800  | 3 | 1 | wood     | yes | yes | yes | yes | 0/1/0   | 46  | TD lvl 5, ACTIVE 0/7/2 |
| TDHPAD | both  | HPAD | 1500 | -10  | 800  | 3 | 1 | wood     | yes | yes | **no** | yes | 0/0/0 | 65  | TD lvl 6, no idle anim |
| TDGTWR | GDI   | PBOX | 500  | -10  | 200  | 3 | 1 | wood     | no  | **no** | yes | yes | —     | 25  | TD lvl 2, 1×1 |
| TDATWR | GDI   | AGUN | 1000 | -20  | 300  | 4 | 1 | aluminum | no  | **no** | yes | yes | —     | 30  | TD lvl 4, 1×2 |
| TDOBLI | Nod   | TSLA | 1500 | -150 | 200  | 5 | 1 | aluminum | no  | **no** | yes | yes | —     | 35  | TD lvl 4, 1×2, ACTIVE 0/4/RATE |
| TDGUN  | Nod   | GUN  | 600  | -20  | 200  | 5 | 1 | steel    | no  | **no** | yes | yes | —     | 26  | TD lvl 2, 1×1 |
| TDSAM  | Nod   | SAM  | 750  | -20  | 200  | 3 | 1 | steel    | no  | **no** | **no** | yes | — | 40  | TD lvl 6, 2×1, turret-based |
| TDFACT | both  | FACT | 5000 | **0** | 400  | 3 | 1 | wood     | yes | yes | yes | yes | 0/4/3   | 70  | TD lvl 99, ✅ shipped v0.3.0-phase5e — Power=0 per vanilla RA [FACT] |

**Reading the table:**
- Empty `Idle` column = no idle animation (engine renders shape 0 statically). Damaged state = shape 1 in that case (the engine's `largest = max(Anims[*].Start + Count) = 1` auto-shift).
- `Crew=no` means selling/destroying spawns zero infantry (TD canon for SILO/HPAD/SAM).
- `Cap=no` (bold) marks entries where TD authentic differs from the original catalogue spec — defensive structures and superweapon hosts can't be captured. **TMPL and EYE are NOT capturable per TD.**
- `Points` is the TD-authentic Risk/Reward value extracted from `tiberiandawn/bdata.cpp` per-class constructor (the line commented `// RISK/RWRD: Risk/reward rating values`). Both `Risk` and `Reward` fields are set from the rules.ini `Points=` key (`redalert/techno.cpp:7067`), and the value feeds `TechnoClass::Value()` (`redalert/techno.cpp:5171`). Without it the AI can't see the building — see [[ai-targeting]] for the full path. **Mandatory field for every TD entry.**
- `Sight` values are TD-authentic (extracted from each `tiberiandawn/bdata.cpp` class's `// SIGHTRANGE: Range of sighting.` line). **TD buildings have systematically smaller sight radii than RA equivalents** (roughly -2 cells across the board — e.g., NUKE=2 vs POWR=4, PYLE=3 vs TENT=5). This is by design while we stay vanilla-faithful; expect GDI/Nod bases to feel "shrouded" next to Allied/Soviet ones until scouting units are deployed. Revisit if balance demands it.
- Logic= aliases the engine donor; field overrides come via rules.ini per the recipe.

**Note on TDHQ:** TD's `RADAR` (HQ) has Points=20, which is lower than RA's `DOME` (Points=30, the engine donor). Using TD-authentic = 20 here means the AI weighs HQs slightly less than vanilla. If skirmishes show HQ being ignored relative to the rest of the base, consider bumping to 30 to match the RA donor — document any deviation here.

---

## Master wiring table (engine hookups, v0.3 source of truth)

Values that **must be set in rules.ini per-entry** because the Logic= alias does *not* copy them from the donor (`bdata.cpp:3731-3759` lists what *is* copied — everything below isn't). Omitting any of these reproduces the same class of bug as the `Points=` issue: the building constructs but the engine treats it as a vanilla-default placeholder for the missing field.

| IniName | TechLevel | Prereq (TD-prefixed) | Primary | Secondary | BaseNormal | Owner | TD source line |
|---|---|---|---|---|---|---|---|
| TDNUKE | 0  | —      | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:892` |
| TDNUK2 | 5  | TDNUKE | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:943` |
| TDPROC | 1  | TDNUKE | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:585` |
| TDSILO | 1  | TDPROC | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:636` |
| TDPYLE | 0  | TDNUKE | —         | — | yes | GoodGuy        | `bdata.cpp:1097` |
| TDHAND | 0  | TDNUKE | —         | — | yes | BadGuy         | `bdata.cpp:1148` |
| TDWEAP | 2  | TDPROC | —         | — | yes | GoodGuy        | `bdata.cpp:264` |
| TDAFLD | 2  | TDPROC | —         | — | yes | BadGuy         | `bdata.cpp:841` |
| TDHQ   | 2  | TDPROC | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:739` |
| TDEYE  | 7  | TDHQ   | —         | — | yes | GoodGuy        | `bdata.cpp:213` |
| TDTMPL | 7  | TDHQ   | —         | — | yes | BadGuy         | `bdata.cpp:162` |
| TDFIX  | 5  | TDNUKE | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:1250` |
| TDHPAD | 6  | TDPYLE / TDHAND | — | — | yes | GoodGuy,BadGuy | `bdata.cpp:688` |
| TDGTWR | 2  | TDPYLE | Vulcan    | — | yes | GoodGuy        | `bdata.cpp:320` |
| TDATWR | 4  | TDHQ   | TurretGun | Nike | yes | GoodGuy      | `bdata.cpp:372` |
| TDOBLI | 4  | TDHQ   | HellFire  | — | yes | BadGuy         | `bdata.cpp:424` |
| TDGUN  | 2  | TDHAND | TurretGun | — | yes | BadGuy         | `bdata.cpp:475` |
| TDSAM  | 6  | TDHAND | Nike      | — | yes | BadGuy         | `bdata.cpp:790` |
| TDFACT | 99 | —      | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:534` |

**Column derivation:**

- **TechLevel** — TD source's "Build level" line. Drives sidebar gating. `redalert/techno.cpp:7063` loads from `TechLevel=`.
- **Prereq** — TD source's STRUCTF_* mapped to the TD-prefixed equivalent. STRUCTF_POWER → TDNUKE; STRUCTF_REFINERY → TDPROC; STRUCTF_RADAR → TDHQ; STRUCTF_BARRACKS → TDPYLE (GDI) / TDHAND (Nod) — split by faction so each side's chain is internally consistent. `techno.cpp:7060` loads from `Prerequisite=`.
- **Primary / Secondary** — RA donor's weapon name, because TD's `WEAPON_OBELISK_LASER` / `WEAPON_TOW_TWO` / `WEAPON_CHAIN_GUN` don't exist in RA's weapon table. The TD-authentic intent is preserved in the donor choice. `techno.cpp:7052-7055` loads from `Primary=` / `Secondary=`.
- **BaseNormal** — all 19 entries are real base structures, so `yes` across the board. (Decorative/civilian buildings would be `no`, but none of ours are.) `bdata.cpp:3717` loads from `BaseNormal=`.
- **Owner** — TD source's HOUSEF_GOOD/HOUSEF_BAD flags mapped to our `Owner=GoodGuy,BadGuy` syntax. GoodGuy = GDI (HOUSE_GOOD), BadGuy = Nod (HOUSE_BAD).

**TD weapon → RA placeholder analogs** (v0.3 — pending proper TD weapon ports; full plan in [[weapon-ports]]):

| TD weapon | v0.3 RA placeholder | Notes |
|---|---|---|
| WEAPON_CHAIN_GUN (GTWR) | Vulcan | Anti-infantry chaingun → anti-infantry vulcan. Close match. |
| WEAPON_TOW_TWO (ATWR) | TurretGun + Nike | TD's ATWR is dual-role anti-armor + anti-air. RA has no single weapon for that, so we use **Primary=TurretGun** (anti-armor from GUN donor) and **Secondary=Nike** (anti-air from Soviet SAM). Engine selects per target type. Closer to authentic than pure-AA AGUN/ZSU-23. |
| WEAPON_OBELISK_LASER (OBLI) | HellFire | RA has no laser weapon. HellFire is a heavy anti-armor missile — keeps the slow-firing/high-damage feel without the wrong-looking Tesla lightning. Real port covered in [[weapon-ports]]. |
| WEAPON_TURRET_GUN (GUN) | TurretGun | Same name in both engines. Behaviour identical. |
| WEAPON_NIKE (SAM) | Nike | Same name in both engines. |

---


**Status legend:** ✅ built & verified on Deck · 🔨 implemented, untested · 📝 designed, not yet built · ❓ open design question · 🚧 needs engine work

**Visual reference:** `~/Desktop/cnc-buildings/{TD,RA}/` — idle-frame PNGs.

**TD prereq → RA Prerequisite= mapping** (TD-prefixed because our IniNames are prefixed to avoid vanilla collisions):

| TD prereq enum | TD building | Our entry uses |
|---|---|---|
| STRUCTF_NONE | nothing | (omit `Prerequisite=` line) |
| STRUCTF_POWER | NUKE | `Prerequisite=TDNUKE` |
| STRUCTF_BARRACKS | PYLE (GDI) / HAND (Nod) | `Prerequisite=TDPYLE` or `TDHAND` per faction |
| STRUCTF_REFINERY | PROC | `Prerequisite=TDPROC` |
| STRUCTF_RADAR | HQ | `Prerequisite=TDHQ` |
| STRUCTF_HOSPITAL | HOSP | `Prerequisite=TDHOSP` (not in v0.3 catalogue) |

---

## Donor cheat-sheet (RA buildings → engine behaviour)

| Donor | Role / behaviour | Notes |
|---|---|---|
| POWR | Power plant — generates power | |
| APWR | Advanced Power Plant — bigger generator | 3×3 footprint by default — override |
| TENT | Allied Barracks — infantry production | |
| BARR | Soviet Barracks — infantry production | |
| PROC | Ore Refinery — spawns free Ore Truck on build | |
| SILO | Ore Silo — increases credit cap | |
| WEAP | War Factory — vehicle production | |
| HPAD | Helipad — helicopter production / landing | |
| DOME | Radar Dome — map reveal, tech prereq | |
| FIX | Service Depot — vehicle repair | |
| FACT | Construction Yard — building production | tied to MCV deploy |
| ATEK | Allied Tech Center | |
| STEK | Soviet Tech Center | |
| GUN | Allied Turret — anti-vehicle | powered |
| PBOX | Allied Pillbox — anti-infantry | manned by GI |
| FTUR | Soviet Flame Turret — anti-infantry | |
| TSLA | Tesla Coil — heavy anti-everything | power-hungry |
| SAM | RA SAM Site — anti-air | |
| AGUN | Anti-Aircraft Gun — fast AA | |
| MSLO | Missile Silo (superweapon — Atom Bomb) | |
| IRON | Iron Curtain (superweapon — invuln beam) | |
| PDOX | Chronosphere (superweapon — teleport) | |
| AFLD | Airfield (Soviet vehicle delivery via plane) | |

---

## Per-entry sections — design rationale

The sections below capture **design rationale and donor choice** for each catalogue entry. The flag values shown in per-entry field tables are illustrative — the **master flag table above is the canonical source** the script reads. Where they disagree, the master table wins.

Entry names below use the TD asset name (e.g. "PYLE", "HAND") for readability; the actual IniName in rules.ini is TD-prefixed (`TDPYLE`, `TDHAND`, etc.) to avoid the vanilla-RA collision class documented in `docs/adding-td-buildings.md`.

---

## GDI catalogue

GDI: Allied-flavoured engine donors where there's a choice. Armoured, ordered, Western.

### PYLE — GDI Barracks 📝
Faction: GDI · Donor: **TENT** (Allied barracks) · TD lvl 0, $300, -20 power, 400 HP, 2×2 wood, prereq NUKE

| Field | Value |
|---|---|
| Logic= | TENT |
| Image= | PYLE |
| Footprint= | PYLE (2×2, to add) |
| Name= | Barracks |
| TechLevel | 0 |
| Prerequisite | NUKE |
| Owner= | GoodGuy |
| Cost | 300 |
| Power | -20 |
| Strength | 400 |
| Armor | wood |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** GDI inherits Allied infantry roster (GI, Rocket Soldier, Engineer, Medic, Spy, Tanya) via the TENT donor for v0.3. Custom GDI infantry types are v0.4+.

### HPAD — Helipad 📝
Faction: **both** · Donor: **HPAD** · TD lvl 6, $1500, -10 power, 400 HP, 2×2 wood, prereq Barracks

| Field | Value |
|---|---|
| Logic= | HPAD |
| Image= | HPAD |
| Footprint= | HPAD (2×2) |
| Name= | Helipad |
| TechLevel | 6 |
| Prerequisite | PYLE\|HAND |
| Owner= | GoodGuy,BadGuy |
| Cost | 1500 |
| Power | -10 |
| Strength | 400 |
| Armor | wood |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** Both factions share HPAD per TD canon (GDI Orca, Nod Apache). Helicopter roster inherits from HPAD donor — RA Longbow for Allied-side, Hind for Soviet-side. TD-flavoured helicopters land in v0.4 with the unit roster work.

### HQ — Communications Center / Radar 📝
Faction: **both** · Donor: **DOME** · TD lvl 2, $1000, -40 power, 500 HP, 2×2 wood, sight **10**, prereq PROC

| Field | Value |
|---|---|
| Logic= | DOME |
| Image= | HQ |
| Footprint= | HQ (2×2) |
| Name= | Communications Center |
| TechLevel | 2 |
| Prerequisite | PROC |
| Owner= | GoodGuy,BadGuy |
| Cost | 1000 |
| Power | -40 |
| Strength | 500 |
| Armor | wood |
| Sight | 10 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** TD didn't differentiate visually — both factions shared HQ. Single shared entry.

### EYE — Advanced Communications Center (hosts Ion Cannon) 📝 🚧
Faction: GDI · Donor: **MSLO** (RA Missile Silo — for superweapon hosting) · TD lvl 7, $2800, -**200** power, 500 HP, 2×2 wood, sight 10, prereq HQ

| Field | Value |
|---|---|
| Logic= | MSLO |
| Image= | EYE |
| Footprint= | EYE (2×2) |
| Name= | Advanced Communications Center |
| TechLevel | 7 |
| Prerequisite | HQ |
| Owner= | GoodGuy |
| Cost | 2800 |
| Power | -200 |
| Strength | 500 |
| Armor | wood |
| Sight | 10 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Design (2026-05-19):** EYE is GDI's superweapon host — building it grants the Ion Cannon strike. Mirrors Nod's TMPL (Temple of Nod hosts nuclear strike). Use Logic=MSLO so the engine grants a generic superweapon timer/picker.

**🚧 v0.3 caveat:** MSLO's default superweapon is the Atom Bomb visual (mushroom cloud). The actual Ion Cannon beam-strike effect is a separate engine implementation in v0.4. For v0.3, EYE grants a working superweapon with placeholder visuals — the mechanic works, the art doesn't match yet.

**-200 power drain** is huge — players will need NUK2 (or two NUKEs) to support EYE. TD's design intent.

### GTWR — Guard Tower 📝
Faction: GDI · Donor: **PBOX** (Allied Pillbox) · TD lvl 2, $500, -10 power, 200 HP, **1×1** wood, prereq PYLE

| Field | Value |
|---|---|
| Logic= | PBOX |
| Image= | GTWR |
| Footprint= | GTWR (1×1, to add) |
| Name= | Guard Tower |
| TechLevel | 2 |
| Prerequisite | PYLE |
| Owner= | GoodGuy |
| Cost | 500 |
| Power | -10 |
| Strength | 200 |
| Armor | wood |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | no (1×1 = no bib) |

### ATWR — Advanced Guard Tower 📝
Faction: GDI · Donor: **AGUN** (Anti-Aircraft Gun) or **GUN** · TD lvl 4, $1000, -20 power, 300 HP, **1×2** aluminum, prereq HQ

| Field | Value |
|---|---|
| Logic= | AGUN |
| Image= | ATWR |
| Footprint= | ATWR (1×2, to add) |
| Name= | Advanced Guard Tower |
| TechLevel | 4 |
| Prerequisite | HQ |
| Owner= | GoodGuy |
| Cost | 1000 |
| Power | -20 |
| Strength | 300 |
| Armor | aluminum |
| Sight | 4 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | no |

**Donor choice:** TD's ATWR fires rockets at both ground & air. AGUN (anti-air only) is closer to the "anti-air rocket" feel. Alternative: GUN (anti-vehicle gun) for a pure anti-ground tower. Pick **AGUN** as default — TD's ATWR was anti-air-capable.

---

## Nod catalogue

Nod: Soviet-flavoured engine donors. Aggressive, asymmetric, distinctive defence.

### HAND — Hand of Nod (barracks) 📝
Faction: Nod · Donor: **BARR** (Soviet barracks) · TD lvl 0, $300, -20 power, 400 HP, **2×3** wood, prereq NUKE

| Field | Value |
|---|---|
| Logic= | BARR |
| Image= | HAND |
| Footprint= | HAND (2×3, to add — bigger than PYLE) |
| Name= | Hand of Nod |
| TechLevel | 0 |
| Prerequisite | NUKE |
| Owner= | BadGuy |
| Cost | 300 |
| Power | -20 |
| Strength | 400 |
| Armor | wood |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** Footprint is 2×3 (BSIZE_23) — bigger than PYLE's 2×2. Nod barracks: Conscript, Grenadier, Engineer, Spy, Tesla Trooper, Flamethrower via BARR donor.

### GUN — Nod Gun Turret 📝
Faction: Nod · Donor: **GUN** (Allied Turret) · TD lvl 2, $600, -20 power, 200 HP, **1×1** steel, prereq HAND

| Field | Value |
|---|---|
| Logic= | GUN |
| Image= | GUN |
| Footprint= | GUN (1×1) |
| Name= | Nod Turret |
| TechLevel | 2 |
| Prerequisite | HAND |
| Owner= | BadGuy |
| Cost | 600 |
| Power | -20 |
| Strength | 200 |
| Armor | steel |
| Sight | 5 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | no |

**Note:** Same IniName as RA's GUN — but our entry shadows the donor via Logic=. Display name disambiguates ("Nod Turret" vs "Turret").

### SAM — SAM Site (Nod anti-air) 📝
Faction: Nod · Donor: **SAM** (RA's own SAM) · TD lvl 6, $750, -20 power, 200 HP, **2×1** steel, prereq HAND

| Field | Value |
|---|---|
| Logic= | SAM |
| Image= | SAM |
| Footprint= | SAM (2×1) |
| Name= | SAM Site |
| TechLevel | 6 |
| Prerequisite | HAND |
| Owner= | BadGuy |
| Cost | 750 |
| Power | -20 |
| Strength | 200 |
| Armor | steel |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | no |

**Donor choice:** SAM (donor = SAM) makes the engine pop-up missile launcher fire. Alternative: AGUN for continuous fire. Stick with SAM-as-donor for the iconic pop-up feel.

### OBLI — Obelisk of Light 📝
Faction: Nod · Donor: **TSLA** · TD lvl 4, $1500, -**150** power, 200 HP, **1×2** aluminum, prereq HQ

| Field | Value |
|---|---|
| Logic= | TSLA |
| Image= | OBLI |
| Footprint= | OBLI (1×2, to add) |
| Name= | Obelisk of Light |
| TechLevel | 4 |
| Prerequisite | HQ |
| Owner= | BadGuy |
| Cost | 1500 |
| Power | -150 |
| Strength | 200 |
| Armor | aluminum |
| Sight | 5 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | no |

**Note:** -150 power drain is the design tax for the devastating weapon. Matches TD's design — Obelisk-spam is gated by power.

### AFLD — Nod Airstrip (vehicle factory with cargo-plane delivery) 📝 🚧
Faction: Nod · Donor: **WEAP** (TD's Airstrip is Nod's vehicle factory) · TD lvl 2, $2000, -30 power, 500 HP, **4×2** steel, prereq PROC, **is_factory=yes**

| Field | Value |
|---|---|
| Logic= | WEAP |
| Image= | AFLD |
| Footprint= | AFLD (4×2, to add — big!) |
| Name= | Nod Airstrip |
| TechLevel | 2 |
| Prerequisite | PROC |
| Owner= | BadGuy |
| Cost | 2000 |
| Power | -30 |
| Strength | 500 |
| Armor | steel |
| Sight | 5 |
| Adjacent | 1 |
| Factory | yes |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Design (2026-05-19):** TD-faithful split — GDI=WEAP, Nod=AFLD. Both Logic=WEAP so both behave as vehicle factories. Same vehicle roster (whatever WEAP donor produces) until v0.4 brings TD-flavoured tanks.

**Engine work needed (scoped for v0.3, in Nod's portion of the build):**

1. **Exit cell for 4×2 footprint.** WEAP's `ExitList[0]` offset assumes a 3×3 footprint and lands south of row 2. For AFLD's 4×2 it may land inside or beyond the AFLD cells. Test first — if WEAP's offset works for 4×2 (lucky alignment), no change needed. If not, add an `ExitList=` rules.ini override field analogous to the existing `Footprint=` pipeline (1 small DLL change in `BuildingTypeClass::Read_INI`).

2. **Cargo plane delivery mechanic.** Replace the "vehicle teleports to exit coord" behaviour with TD-style "cargo plane flies in → lands → vehicle drives off → plane departs." Engine work in `BuildingClass::Exit_Object` (`redalert/building.cpp:2030`):
   - Add a check at the start of `case STRUCT_WEAP` (or earlier): if the BuildingTypeClass has an `IsAirDelivered=yes` flag (new rules.ini field), take the air-delivery path instead.
   - Air-delivery path: spawn a cargo aircraft (new TD AircraftType, donor=BADGER or new) at the closest map edge, carrying the unit as cargo. Aircraft mission flies to the AFLD's center cell, lands (similar to HPAD's `Helper_Find_Cell` for helicopter landing), unloads the vehicle (similar to existing transport-unload code), then takes off and exits the map.
   - Plumbing: `AircraftClass::Paradrop_Cargo` exists for infantry; vehicle delivery follows the same general arc but needs new code for the "land and unload vehicle" step (RA's Hind/Chinook transport unload is the closest existing path).
   - Asset: TD's cargo plane sprite (`CARGO.ZIP` from `TEXTURES_TD_SRGB.MEG`).

**Timing:** Don't block. GDI catalogue (NUKE/NUK2/PYLE/HQ/EYE/WEAP/FIX/GTWR/ATWR/HPAD) ships first using the existing Logic-aliased pipeline. When we move into Nod's portion (HAND/GUN/SAM/OBLI/TMPL), AFLD becomes its own focused slice with the two engine pieces above. Estimated 1-2 sessions for the air-delivery work, then AFLD plugs in like any other catalogue entry.

### TMPL — Temple of Nod (superweapon) 📝 🚧
Faction: Nod · Donor: **MSLO** (RA Missile Silo) · TD lvl 7, $3000, -150 power, **1000** HP, 3×3 aluminum, prereq HQ

| Field | Value |
|---|---|
| Logic= | MSLO |
| Image= | TMPL |
| Footprint= | TMPL (3×3, to add) |
| Name= | Temple of Nod |
| TechLevel | 7 |
| Prerequisite | HQ |
| Owner= | BadGuy |
| Cost | 3000 |
| Power | -150 |
| Strength | 1000 |
| Armor | aluminum |
| Sight | 4 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** TMPL fires Nod's nuclear strike in TD. MSLO is RA's Atom Bomb (functionally identical superweapon — long cooldown, launch animation, target picker). 🚧 because superweapon behaviour through Logic= aliasing isn't verified.

---

## Shared (both factions) catalogue

Production-chain buildings without strong faction-identity differences.

### NUKE — Power Plant (tier 1) 📝
Faction: **both** · Donor: **POWR** · TD lvl 0, $300, +100 power, 200 HP, 2×2 wood

| Field | Value |
|---|---|
| Logic= | POWR |
| Image= | NUKE |
| Footprint= | NUKE (2×2, to add — same shape as NUK2) |
| Name= | Power Plant |
| TechLevel | 0 |
| Owner= | GoodGuy,BadGuy |
| Cost | 300 |
| Power | +100 |
| Strength | 200 |
| Armor | wood |
| Sight | 2 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

### NUK2 — Advanced Power Plant (tier 2) ✅→📝
Faction: **both** · Donor: **APWR** (was POWR in POC) · TD lvl 5, $700, +200 power, 300 HP, 2×2 wood, prereq NUKE

| Field | POC value | TD-authentic target |
|---|---|---|
| Logic= | POWR | **APWR** |
| Image= | NUK2 | NUK2 |
| Footprint= | NUK2 | NUK2 |
| Name= | GDIPowerPlant | Advanced Power Plant |
| TechLevel | 1 | **5** |
| Prerequisite | — | **NUKE** |
| Owner= | GoodGuy | **GoodGuy,BadGuy** |
| Cost | 350 | **700** |
| Power | +100 | **+200** |
| Strength | 400 | **300** |
| Armor | wood | wood |
| Sight | 3 | 2 |

**Status:** POC verified on Deck. Migration to TD-authentic values is a v0.3 task — covered when we run the buildout.

### PROC — Refinery 📝
Faction: **both** · Donor: **PROC** · TD lvl 1, $2000, -40 power, 450 HP, 3×3 wood, prereq NUKE

| Field | Value |
|---|---|
| Logic= | PROC |
| Image= | PROC |
| Footprint= | PROC (3×3) |
| Name= | Tiberium Refinery |
| TechLevel | 1 |
| Prerequisite | NUKE |
| Owner= | GoodGuy,BadGuy |
| Cost | 2000 |
| Power | -40 |
| Strength | 450 |
| Armor | wood |
| Sight | 4 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** TD calls the refinery's output "Tiberium" rather than "Ore". Display name reflects that.

### SILO — Ore Silo 📝
Faction: **both** · Donor: **SILO** · TD lvl 1, $150, -10 power, 150 HP, 2×1 wood, prereq PROC

| Field | Value |
|---|---|
| Logic= | SILO |
| Image= | SILO |
| Footprint= | SILO (2×1) |
| Name= | Tiberium Silo |
| TechLevel | 1 |
| Prerequisite | PROC |
| Owner= | GoodGuy,BadGuy |
| Cost | 150 |
| Power | -10 |
| Strength | 150 |
| Armor | wood |
| Sight | 2 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

### WEAP — Weapons Factory (GDI vehicle factory) 📝
Faction: **GDI** · Donor: **WEAP** · TD lvl 2, $2000, -30 power, 500 HP, **3×3** aluminum, prereq PROC

| Field | Value |
|---|---|
| Logic= | WEAP |
| Image= | WEAP |
| Footprint= | WEAP (3×3) |
| Name= | Weapons Factory |
| TechLevel | 2 |
| Prerequisite | PROC |
| Owner= | GoodGuy |
| Cost | 2000 |
| Power | -30 |
| Strength | 500 |
| Armor | aluminum |
| Sight | 3 |
| Adjacent | 1 |
| Factory | yes |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** TD-faithful: GDI builds vehicles here, Nod builds at AFLD. Both Logic=WEAP, both produce the same vehicle roster until v0.4's TD vehicle work.

### FIX — Service Depot 📝
Faction: **both** · Donor: **FIX** · TD lvl 5, $1200, -30 power, 400 HP, 3×3 wood, prereq NUKE

| Field | Value |
|---|---|
| Logic= | FIX |
| Image= | FIX |
| Footprint= | FIX (3×3) |
| Name= | Service Depot |
| TechLevel | 5 |
| Prerequisite | NUKE |
| Owner= | GoodGuy,BadGuy |
| Cost | 1200 |
| Power | -30 |
| Strength | 400 |
| Armor | wood |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

### FACT — Construction Yard (paired with TD MCV) 📝 🚧
Faction: **both, split into GDI / Nod variants** · Donor: **FACT** · TD lvl 99 (MCV deploys into it), $5000, -30 power, 400 HP, 3×2 wood

| Field | GDIFACT | NODFACT |
|---|---|---|
| Logic= | FACT | FACT |
| Image= | FACT (TD art) | FACT (TD art — same — visual differentiation via remap colour) |
| Footprint= | FACT (3×2) | FACT (3×2) |
| Name= | Construction Yard | Construction Yard |
| TechLevel | 99 | 99 |
| Owner= | GoodGuy | BadGuy |
| Cost | 5000 | 5000 |
| Power | -30 | -30 |
| Strength | 400 | 400 |
| Armor | wood | wood |
| Sight | 3 | 3 |

**Direction (locked 2026-05-19):** v0.3 builds out the standalone TD buildings first, then closes with the MCV+CY pair as the final v0.3 slice. We can't keep starting in a vanilla RA con yard — the visual mismatch is too jarring once the rest of the base is TD-themed.

**Sequencing:** TD buildings (NUKE, NUK2, PROC, SILO, PYLE, HAND, HQ, WEAP, AFLD, EYE, TMPL, FIX, GTWR, ATWR, OBLI, GUN, SAM, HPAD) → then MCV/CY pair → ship v0.3.

**Engine work for MCV/CY pair (v0.3 closing slice):**
- Add `GDIMCV` / `NODMCV` unit types via the Logic-aliased pipeline (extends pipeline from BuildingType to UnitType — pipeline hasn't been validated for units yet, that's prereq work).
- Modify MCV deploy logic so it creates the faction-appropriate CY type by reading Owner (or a new field on UnitTypeClass like `DeploysInto=`).
- Modify initial-units placement in `house.cpp` so GDI/Nod players start with their respective MCV instead of the vanilla one.
- New CY entries above are then the deploy targets.

This is one cohesive slice — likely a 1-2 session implementation.

---

## Skipped for v0.3 (revisit later)

- **HOSP** — Hospital. TD lvl 99 (not normally buildable). Skip.
- **BIO** — Bio Lab. TD lvl 99 (not normally buildable). Skip.
- **ARCO** — Tanker. TD lvl 99, $0. Civilian/scenery. Skip.

---

## Walkthrough status

| IniName | Faction | Donor | Stats? | Status |
|---|---|---|---|---|
| TDNUKE | both | POWR | ✓ | ✅ manual ref impl 2026-05-19 |
| TDNUK2 | both | APWR | ✓ | ✅ (Phase-1 POC) → 📝 migrate to TD-authentic |
| TDPROC | both | PROC | ✓ | 📝 |
| TDSILO | both | SILO | ✓ | 📝 |
| TDPYLE | GDI | TENT | ✓ | 📝 |
| TDHAND | Nod | BARR | ✓ | 📝 |
| TDHPAD | both | HPAD | ✓ | 📝 |
| TDWEAP | GDI | WEAP | ✓ | 📝 |
| TDAFLD | Nod | WEAP | ✓ | 📝 🚧 (cargo-plane engine slice within Nod buildout) |
| TDHQ | both | DOME | ✓ | 📝 |
| TDEYE | GDI | MSLO | ✓ | 📝 🚧 (Ion Cannon visual v0.4) |
| TDTMPL | Nod | MSLO | ✓ | 📝 🚧 |
| TDFIX | both | FIX | ✓ | 📝 |
| TDGTWR | GDI | PBOX | ✓ | 📝 |
| TDATWR | GDI | AGUN | ✓ | 📝 |
| TDOBLI | Nod | TSLA | ✓ | 📝 |
| TDGUN | Nod | GUN | ✓ | 📝 |
| TDSAM | Nod | SAM | ✓ | 📝 |
| TDFACT | both | FACT | ✓ | ✅ v0.3.0-phase5e (per-faction split deferred to v0.4) |
| TDMCV | GoodGuy only | MCV (unit) | — | ✅ v0.3.0-phase5e (Nod TDNODMCV deferred to v0.4) |
| HOSP/BIO/ARCO | — | — | — | skip for v0.3 |

---

## Design decisions log

All seven of the original open questions were resolved 2026-05-19:

1. ✅ **HPAD** — both factions share, Owner=GoodGuy,BadGuy.
2. ✅ **HQ** — both factions share, Owner=GoodGuy,BadGuy.
3. ✅ **WEAP/AFLD vehicle factory** — TD-faithful split. GDI=WEAP, Nod=AFLD, both Logic=WEAP. Nod's cargo-plane delivery is a 🚧 sub-task.
4. ✅ **Infantry rosters** — v0.3 accepts donor rosters (GDI=Allied infantry via TENT, Nod=Soviet infantry via BARR). TD-flavoured infantry types come in v0.4 using the Logic-aliased pipeline extended to InfantryType.
5. ✅ **Vehicle rosters** — same approach as #4. v0.3 uses WEAP donor roster; TD vehicles in v0.4. **Exception: MCV** — needed in v0.3 to pair with the TD CY.
6. ✅ **GDI superweapon** — Ion Cannon, hosted on EYE (Logic=MSLO). Placeholder mushroom-cloud visual in v0.3; proper Ion Cannon beam in v0.4.
7. ✅ **Walls** — reuse vanilla RA walls (SBAG/CYCL/BRIK/FENC) for v0.3.

## v0.3 implementation sequence

1. **GDI catalogue buildings** — NUKE, NUK2, PYLE, HQ, WEAP, FIX, GTWR, ATWR, HPAD, EYE. Pure content; use existing Logic-aliased pipeline. Helper script worth writing here.
2. **Nod catalogue buildings + AFLD engine slice** — HAND, GUN, SAM, OBLI, TMPL, plus the AFLD air-delivery engine work (ExitList override + cargo-plane mechanic in `Exit_Object`). AFLD is the Nod vehicle factory, so it lands with the rest of Nod's tree.
3. **TD MCV/CY pair (closing slice)** — adds Logic-aliased UnitType support, GDI/Nod MCV variants, faction-aware deploy logic, faction-specific CYs.
4. **v0.3 release** — TD-themed bases, fully playable skirmish on the Deck, vanilla-RA art only on infantry/non-Nod vehicles. Workshop publish (or wait until v0.4).

## v0.4+ roadmap (not yet specced)

- TD-themed infantry per faction (Minigunner, Engineer, Grenadier, Flamethrower, etc.).
- TD-themed vehicles per faction (Light Tank, Medium Tank, Mammoth Tank, Buggy, Recon Bike, etc.).
- Ion Cannon proper visual effect (engine work).
- TD-themed walls (if v0.3's vanilla-walls compromise feels wrong).
- TD-themed Hospital / Bio Lab if there's player demand.

---

## Footprint presets — ready to paste into `redalert/bdata.cpp`

Each TD building needs a `Footprint=` preset registered in the `_presets[]` table in `BuildingTypeClass::Read_INI` (currently around line 3780). The shapes below are decoded from `tiberiandawn/bdata.cpp` — TD uses `MCW` (Map Cell Width), RA's equivalent is `MAP_CELL_W`. Substitution is mechanical.

**Shared shapes:** HQ, EYE, NUKE, NUK2 all share the same 2×2 L-shape (3-cell occupy + 1-cell overlap). GTWR and GUN share 1×1. ATWR and OBLI share 1×2.

### Static array declarations

```cpp
// 2×2 L-shape (3 occupied + 1 visual overlap) — shared by NUKE, NUK2, HQ, EYE
static short const List_NUK2_OCCUPY[]  = {0, MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL};        // existing
static short const List_NUK2_OVERLAP[] = {1, REFRESH_EOL};                                     // existing
// (NUKE/HQ/EYE can reference these directly via aliasing in _presets[].)

// 2×2 split (top occupied, bottom overlap) — PYLE
static short const List_PYLE_OCCUPY[]  = {0, 1, REFRESH_EOL};
static short const List_PYLE_OVERLAP[] = {MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL};

// 2×3 — HAND (Nod barracks, bigger than PYLE)
static short const List_HAND_OCCUPY[]  = {MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W * 2 + 1, REFRESH_EOL};
static short const List_HAND_OVERLAP[] = {0, 1, MAP_CELL_W * 2, MAP_CELL_W, REFRESH_EOL};

// 2×2 full-fill — HPAD
static short const List_HPAD_OCCUPY[]  = {0, 1, MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL};

// 3×3 — PROC, WEAP, TMPL, FIX (different shapes per building)
static short const List_PROC_OCCUPY[]  = {1, MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2, REFRESH_EOL};
static short const List_PROC_OVERLAP[] = {0, 2, MAP_CELL_W * 2, MAP_CELL_W * 2 + 1, MAP_CELL_W * 2 + 2, REFRESH_EOL};

static short const List_WEAP_OCCUPY[]  = {MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2,
                                          MAP_CELL_W * 2, MAP_CELL_W * 2 + 1, MAP_CELL_W * 2 + 2, REFRESH_EOL};
static short const List_WEAP_OVERLAP[] = {0, 1, 2, REFRESH_EOL};

static short const List_TMPL_OCCUPY[]  = {MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2,
                                          MAP_CELL_W * 2, MAP_CELL_W * 2 + 1, MAP_CELL_W * 2 + 2, REFRESH_EOL};
static short const List_TMPL_OVERLAP[] = {0, 1, 2, REFRESH_EOL};

static short const List_FIX_OCCUPY[]   = {1, MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2,
                                          MAP_CELL_W + MAP_CELL_W + 1, REFRESH_EOL};
static short const List_FIX_OVERLAP[]  = {0, 2, MAP_CELL_W + MAP_CELL_W, MAP_CELL_W + MAP_CELL_W + 2, REFRESH_EOL};

// 3×2 — FACT (note: opposite orientation from 2×3 HAND)
static short const List_FACT_OCCUPY[]  = {0, 1, 2, MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2, REFRESH_EOL};

// 4×2 — AFLD (big!)
static short const List_AFLD_OCCUPY[]  = {0, 1, 2, 3, MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2, MAP_CELL_W + 3, REFRESH_EOL};

// 2×1 — SILO, SAM
static short const List_SILO_OCCUPY[]  = {0, 1, REFRESH_EOL};

static short const List_SAM_OCCUPY[]   = {0, 1, REFRESH_EOL};
static short const List_SAM_OVERLAP[]  = {-MAP_CELL_W, -(MAP_CELL_W - 1), REFRESH_EOL};
// ⚠️ SAM's overlap uses NEGATIVE offsets — extends above the bounding box. Verify renderer handles this in RA.

// 1×2 — ATWR, OBLI
static short const List_ATWR_OCCUPY[]  = {MAP_CELL_W, REFRESH_EOL};
static short const List_ATWR_OVERLAP[] = {0, REFRESH_EOL};

// 1×1 — GTWR, GUN
static short const List_1x1_OCCUPY[]   = {0, REFRESH_EOL};
```

### `_presets[]` table entries

```cpp
static FootprintPreset const _presets[] = {
    {"NUKE", BSIZE_22, List_NUK2_OCCUPY,  List_NUK2_OVERLAP},   // shares NUK2's L-shape
    {"NUK2", BSIZE_22, List_NUK2_OCCUPY,  List_NUK2_OVERLAP},   // existing
    {"HQ",   BSIZE_22, List_NUK2_OCCUPY,  List_NUK2_OVERLAP},   // shares NUK2's L-shape
    {"EYE",  BSIZE_22, List_NUK2_OCCUPY,  List_NUK2_OVERLAP},   // shares NUK2's L-shape
    {"PYLE", BSIZE_22, List_PYLE_OCCUPY,  List_PYLE_OVERLAP},
    {"HAND", BSIZE_23, List_HAND_OCCUPY,  List_HAND_OVERLAP},
    {"HPAD", BSIZE_22, List_HPAD_OCCUPY,  NULL},
    {"PROC", BSIZE_33, List_PROC_OCCUPY,  List_PROC_OVERLAP},
    {"WEAP", BSIZE_33, List_WEAP_OCCUPY,  List_WEAP_OVERLAP},
    {"TMPL", BSIZE_33, List_TMPL_OCCUPY,  List_TMPL_OVERLAP},
    {"FIX",  BSIZE_33, List_FIX_OCCUPY,   List_FIX_OVERLAP},
    {"FACT", BSIZE_32, List_FACT_OCCUPY,  NULL},
    {"AFLD", BSIZE_42, List_AFLD_OCCUPY,  NULL},
    {"SILO", BSIZE_21, List_SILO_OCCUPY,  NULL},
    {"SAM",  BSIZE_21, List_SAM_OCCUPY,   List_SAM_OVERLAP},
    {"ATWR", BSIZE_12, List_ATWR_OCCUPY,  List_ATWR_OVERLAP},
    {"OBLI", BSIZE_12, List_ATWR_OCCUPY,  List_ATWR_OVERLAP},   // shares ATWR's 1×2
    {"GTWR", BSIZE_11, List_1x1_OCCUPY,   NULL},
    {"GUN",  BSIZE_11, List_1x1_OCCUPY,   NULL},
};
```

### Visual reference (occupied vs overlap)

ASCII shapes — `▓` = occupied cell, `░` = visual overlap, `·` = bounding box only.

| Bldg | Shape | BSIZE |
|---|---|---|
| NUKE/NUK2/HQ/EYE | `▓░`<br>`▓▓` | 2×2 |
| PYLE | `▓▓`<br>`░░` | 2×2 |
| HPAD | `▓▓`<br>`▓▓` | 2×2 (full) |
| HAND | `░░`<br>`▓▓`<br>`░▓` | 2×3 |
| FACT | `▓▓▓`<br>`▓▓▓` | 3×2 |
| AFLD | `▓▓▓▓`<br>`▓▓▓▓` | 4×2 |
| PROC | `·░·`<br>`▓▓▓·`<br>`░░░` *(approx)* | 3×3 |
| WEAP/TMPL | `░░░`<br>`▓▓▓`<br>`▓▓▓` | 3×3 |
| FIX | `░░░`<br>`░▓▓▓·`<br>`░░` *(approx)* | 3×3 |
| SILO/SAM | `▓▓` | 2×1 (SAM has overhang) |
| ATWR/OBLI | `░`<br>`▓` | 1×2 |
| GTWR/GUN | `▓` | 1×1 |

*(ASCII approximations — refer to the array definitions for exact cells.)*

---

## Workflow per entry

1. Pick decisions for the entry (faction, donor, stats — all decided above for v0.3).
2. Run the 6-step recipe in `docs/adding-td-buildings.md`.
3. Update status: 📝 → 🔨 (built, untested) → ✅ (Deck-verified).
