# Changelog

All notable changes to this mod will be documented here.

This project follows a `version_high.version_low.patch` scheme matching the `ccmod.json` fields.

## [Unreleased]

## [0.4.2] — 2026-05-22 — TDGTWR weapon port + TD-port bullet hardening

GDI Guard Tower now fires the TD-authentic chain gun instead of leaking RA's stronger `[Vulcan]` into the build. Bundles a critical fix for TD-port bullet damage that was silently zeroing TDOBLI and TDGUN hits.

### TDGTWR weapon port — TD-authentic chain gun

- `[TDChainGun]` weapon: Damage=25, ROF=50, Range=4, Warhead=HE (TD's `WEAPON_CHAIN_GUN`). Previously `Primary=Vulcan` was leaking RA's stronger 40/40/5 anti-infantry MG.
- `[TDSpreadfire]` invisible projectile (TD's `BULLET_SPREADFIRE`), with `ImpactAnim=PIFFPIFF` chain-gun puff.
- `VOC_TD_MINI` audio routing: `GUN8` chain-gun burst, extracted from `SFX3D.MEG` and aliased via `RAC_SFX_GUN8` / `RAR_SFX_GUN8` SFXEvents.
- `ClassTdGtwr` `VerticalOffset` corrected from `0x10` → `0x30` to match TD `ClassGTower::Fire_Coord`, so the muzzle is at the top of the lookout structure instead of the waist.
- Engine registration: `WEAPON_TD_CHAIN_GUN` + `BULLET_TDSPREADFIRE` added to defines.h, `new WeaponTypeClass("TDChainGun")` + `new BulletTypeClass("TDSpreadfire")` in `rules.cpp` / `bbdata.cpp`.

### TD-port bullet damage fix (TDOBLI + TDGUN + TDGTWR)

Three TD-port bullet sections — `[TDLaser]`, `[TDAPDS]`, `[TDSpreadfire]` — were missing the `Warhead=` field. Symptom: bullets visibly impacted but target HP didn't decrement. Root cause: TD's verbatim `BulletClass::AI_TD` detonation path (`bullet.cpp:1261`) uses `Class->ClassWarhead`, which defaults to `WARHEAD_NONE` without an explicit `Warhead=` entry — and `Explosion_Damage` at `combat.cpp:171` early-returns on `WARHEAD_NONE` without applying damage. Vanilla RA bullets don't bite this trap because they use the per-instance Warhead set from the weapon's pointer.

Fix:
- `[TDLaser] Warhead=TDLaser`
- `[TDAPDS] Warhead=AP` + `ImpactAnim=VEH-HIT3` (Nod Turret shells now explode on hit)
- `[TDSpreadfire] Warhead=HE` + `ImpactAnim=PIFFPIFF`

### Verifications + documentation

- TDATWR stats verified against TD source — `Damage=60`, `ROF=40`, `Range=6.5`, `TDHE Verses=87/75/56/25/100%` all TD-authentic per `tiberiandawn/const.cpp:88` + `const.cpp:113`. The "weak vs tanks" feel is TD-by-design (25% vs ARMOR_STEEL) and deferred to the post-v1.0 balance pass.
- Project memory rules formalised: balance work is post-v1.0; pre-v1 must stay TD-source-authentic.

## [0.4.1] — 2026-05-21 — TDOBLI separation + TD audio routing + recipe docs

First fully-separated TD building (Obelisk of Light) shipping the iconic charge-up + laser-beam experience. Also lands the audio-routing infrastructure that brings authentic TD weapon sounds (and building-construction sounds) into the RA engine. Architecturally the bigger story: the per-building separation pattern is validated end-to-end and documented as a canonical recipe, so the remaining 16 buildings + units become bounded engineering against the recipe.

### Obelisk of Light — iconic TD experience

- 4-frame gem charge animation when a target is acquired, played at TD-authentic OBELISK_ANIMATION_RATE.
- OBELPOWR warmup sound on charge start.
- Visible 3-line laser beam from gem to target (two thin outer at color 0x7D + bright center at 0x7F), 5 ticks duration.
- OBELRAY1 fire hum.
- Scorch smudge stamped at impact via SmudgeClass.
- Recharge cycle properly resets for the next fire.

### TD audio routing (foundation)

- `docs/td-audio-routing-recipe.md` — canonical recipe for routing TD `.WAV` assets through the Remastered launcher in an RA mod context. Extract from `SFX3D.MEG` → ship in `Data/AUDIO/` → register via `<SFXEvent>` aliases in merged `SFXEVENTSNONLOCALIZED.XML`.
- All three Phase W1 weapons (TowTwo for TDATWR, TdTurretGun for TDGUN, OblsLaser for TDOBLI) now play their authentic TD audio.
- TD building construction sound (`CONSTRU2.WAV`) plays for any STRUCT_TDxxxx building via a single range check in `building.cpp`.
- Reference precedent: Reilsss's CnCinRA workshop mod was the breakthrough source for the SFXEvent alias pattern.

### Engine-level building separation (TDOBLI)

- `STRUCT_TDOBLI` enum + `ClassObelisk` `BuildingTypeClass` + `Init_Heap` registration.
- `_anims[]` BSTATE_ACTIVE entry: 4 frames at rate 15.
- Per-type dispatch in `building.cpp` shape selection (line 656), crew spawn offset (line 4093), animation guard (line 6244). Vanilla engine idiom (matches existing `STRUCT_TESLA`, `STRUCT_SAM`, etc. checks).
- `Charges=yes` on `[TDOblsLaser]` wires the wielder into `BuildingClass::Charging_AI` state machine (same mechanism TD's `tiberiandawn/building.cpp:852-857` uses for the BULLET_LASER case).
- Per-building charge-start sound: OBELPOWR for STRUCT_TDOBLI, TSLAPOWR for Tesla Coil.

### Laser-beam render port

- `Lines[3][5]` / `LineCount` / `LineFrame` / `LineMaxFrames` as `TechnoClass` members — ported from `tiberiandawn/techno.h:195-198`.
- Per-frame draw block in `TechnoClass::Draw_It`.
- Per-tick countdown in `TechnoClass::AI`.
- `BULLET_LASER` branch in `Fire_At` uses validated `target_coord` (not `As_Coord(target)` — that returns world origin if target dies mid-fire; learned via Deck playtest).
- `CC_Draw_Line` wrapper in `conquer.cpp` + `DLL_Draw_Line_Intercept` export in `dllinterface.cpp` (RA's DLL didn't expose line drawing previously; we added the boundary).
- `Electric_Zap` suppression: any IsElectric weapon firing `BULLET_LASER` skips the lightning render. Bullet-type keyed, not building-type keyed — any future TD laser weapon auto-inherits.

### Classic-mode SHP shipping

- `scripts/mix_tools.py` (new) — Westwood MIX format reader/writer (the classic pre-RA-encryption layout). Implements the CRC32-ish filename hash from `common/crc.cpp`. Three commands: `list`, `extract`, `pack`.
- `resources/remaster_mods/Vanilla_RA/CCDATA/TFASSETS.MIX` (new) — mod-shipped mixfile containing `TDOBLI.SHP` + `TDOBLIMAKE.SHP` extracted from TD's `CONQUER.MIX` and renamed with TD prefix.
- `init.cpp` registers TFASSETS.MIX with `MFCD` (best-effort cache; missing file degrades gracefully).
- Removed the `bdata.cpp` `ImageData`/`BuildupData` borrow-from-STRUCT_TESLA stub.

### Country picker labels (description fix)

The v0.4 Workshop description incorrectly stated "France for GDI and Spain/Turkey for Nod". Corrected to **Spain for GDI** and **Turkey for Nod**, matching the actual hijack swap in `dllinterface.cpp:905-910`. France stays vanilla.

### Documentation

- `docs/td-building-separation-recipe.md` (new) — canonical 11-step recipe for porting a TD-themed mod entry from Logic=alias model to fully-separated `STRUCT_TDxxxx`. Distilled from TDOBLI. Per-tier cycle time estimates (1-2h Tier 1 → 4-6h Tier 5). 9 common gotchas.
- `docs/td-audio-routing-recipe.md` (new) — companion recipe for routing TD audio assets.
- `docs/building-separation-plan.md` — status header updated: COMMITTED → IN PROGRESS (TDOBLI = M5-tier vertical slice complete). Section 3.1 added covering HouseClass-side work folded into milestones.
- `docs/session-handoff-weapons-port.md` — rewritten for the TDOBLI milestone.
- `CHANGELOG.md` — this entry.

### Known limitations carried forward

- **Classic graphics mode**: TD-sourced SHPs render with a mild palette mismatch (TD color indices interpreted through RA palette). Deferred to a one-shot Format80-codec iteration that retrofits every TD SHP at once.
- **Spacebar classic toggle cannot be disabled from mod side**. Confirmed via two attempts (Legacy_Render_Enabled = false → black screen on toggle; INPUTTRANSLATORCONFIGURATIONS.XML override → launcher ignores mod XML for this binding). Player rebinds in Options → Controls if they want to disable.
- **OBELPOWR/OBELRAY1 play back-to-back** at fire time rather than warmup-then-fire delayed sequence. Minor polish.
- **GDI/Nod AI does not work yet** — same as v0.4.

### Tag

`v0.4.1-tdobli-separation`

## [0.3.0-phase5a] — 2026-05-20 — Asset pipeline + TDPYLE + 4 catalogue fixes

End-to-end rebuild of how mod buildings get from the manifest to the Deck. Adds TDPYLE as the first net-new entry that landed right first time after the pipeline was in place. Fixes four engine-edge-case bugs surfaced by extended catalogue use.

### Asset pipeline (one command per building, byte-mirror to Deck)

- **`scripts/bundle_assets.py` (new)** — given a manifest entry, extracts sprite ZIPs from `TEXTURES_TD_SRGB.MEG`, repacks with TD-prefixed internal frame filenames, patches `RA_STRUCTURES.XML` (idle + MAKE tilesets), patches `RABUILDABLES.XML` (sidebar wiring). Idempotent.
- **`scripts/add_building.py` (extended)** — orchestrates rules.ini emit + `[NewBuildings]` registration + asset bundling. `--skip-assets` flag for rules-only runs.
- **`deploy.sh` (rewritten)** — `rsync -av --delete` mirror to the Deck. Drift between local and Deck is now impossible.
- **Manifest schema**: renamed `image` → `td_asset` (source MEG asset name) with rules.ini `Image=` now derived from `ininame` (TD-prefixed uniformly). New fields: `shape_size`, `text_id_name`, `text_id_desc`, `build_icon`.

### Asset convention: TD-prefix uniformly

Renamed all sprite assets to TD-prefix convention:
- `NUKE.ZIP` → `TDNUKE.ZIP` containing `tdnuke-NNNN.tga`, referenced as `<Frame>tdnuke\tdnuke-0000.tga</Frame>`
- Same for NUK2, PYLE
- `Image=TDNUKE` (not `Image=NUKE`) in rules.ini
- `<Name>TDNUKE</Name>` in tileset XML

Avoids vanilla name collisions when we get to WEAP/FIX/HPAD/SAM which share IniNames with vanilla RA.

### Engine fixes

- **Petroglyph flash on placement → fixed.** TD-source MAKE ZIPs start frames at 0001, not 0000 (TD convention for "empty placement marker"). XML emit now uses `<Frame />` (empty) for shape 0 of MAKE tilesets. Without this fix, the launcher hits a missing TGA for one frame between placement and buildup → Petroglyph fallback. See `bundle_assets.py` `empty_first_shape=True` path.
- **Unit Z-order under TD buildings → fixed.** `BuildingClass::Sort_Y` (`building.cpp:3505`) now returns `Center_Coord()` for any entry with explicit `ShapeSize=` (i.e., mod entries). Vanilla default Sort_Y adds a south offset that places sort point above units in the building's visual extent, causing buildings to draw over units near their bottom row. Vanilla buildings untouched.
- **`bdata.cpp` PYLE footprint preset** — top-row occupy + bottom-row overlap (matches TD's `List22_1100`/`List22_0011`). Vanilla RA's BARR donor uses solid 2×2 occupy + NULL overlap; TDPYLE needs the TD-authentic alternative.
- **TDPYLE Logic=TENT (not BARR)** — Allied barracks donor for GDI. Soviet BARR donor (which we had initially) made TDPYLE engine-side a Soviet factory, so France/HOUSE_GOOD couldn't produce infantry.

### Catalogue: TDPYLE landed end-to-end

- TDPYLE (GDI Barracks) — Logic=TENT, donor TD asset PYLE, ShapeSize=48,48, Sight=5, Cost=300, Power=-20, Points=60, Prereq=TDNUKE, Owner=GoodGuy. Sidebar cameo, tooltip "Barracks", placement, buildup, idle, infantry production all functional on the Deck.

### Interim Owner= bulk patch

Since v0.2.0 decoupled HOUSE_GOOD/HOUSE_BAD from HOUSEF_ALLIES/HOUSEF_SOVIET, France/GDI couldn't build any vanilla Allied units. Bulk-patched every `Owner=allies` unit/infantry/aircraft/vessel entry in `rules.ini` to `Owner=allies,GoodGuy`, and every `Owner=soviet` to `Owner=soviet,BadGuy`. **Buildings explicitly excluded** — the catalogue defines TD-prefixed building entries with explicit single-faction Owner. Interim hack until TD-themed unit catalogue lands; will revert per-entry as TD units replace vanilla.

### Documentation

- `docs/adding-td-buildings.md` — gotchas 6-9 added (MAKE shape 0 must be `<Frame />`, launcher derives ZIP from frame path, mod entries need Center_Coord() Sort_Y, HOUSE_GOOD/allies Owner= patch context).
- `docs/catalogue.md` — full session pickup with this session's work + unresolved items + next-session pickup priorities.
- `docs/manifest-gaps.md` — referenced unchanged; still the source of truth for which fields the manifest can/can't emit.

### Known issues parked for next session

- **E3 (Rocket Soldier) not buildable for GDI** despite `Owner=allies,soviet,GoodGuy,BadGuy` + explicit `Prerequisite=tent`. Investigation TBD; may be vanilla `idata.cpp` overriding Ownable at class init before rules.ini override, or some other engine gate.

### NOT committed

- `redalert/scenario.cpp` reveal-all hack remains a working-tree-only diagnostic (per `docs/catalogue.md` "TEMPORARY DEV HACKS").

## [0.3.0-phase4a] — 2026-05-19 — Literal prerequisites for mod IniNames (D1.2 Phase 1)

Fixes the long-standing bug where `Prerequisite=TDxxxx` in rules.ini didn't actually require the named mod building. Vanilla RA stored prerequisites as a 32-bit `STRUCTF_*` bitmask; mod-defined Types past `STRUCT_COUNT` (e.g. TDNUKE at heap index 91+) couldn't be expressed in 32 bits, and `1L << Type` for those values was undefined behaviour. Result: TDNUK2's `Prerequisite=TDNUKE` either silently passed when it shouldn't, failed when it shouldn't, or aliased to whatever `StructType` happened to share the bottom 5 bits.

Smallest fix that unblocks the catalogue rollout. Phase 2 (deletion of the legacy `BScan`/`ActiveBScan`/`OldBScan` bitmask fields and migration of ~60 vanilla call sites to `BQuantity`/`ActiveBQuantity`) is deferred — see `docs/catalogue.md`.

### Engine changes

- **`Prerequisite` field is now a list of Type indices.** `type.h:493` changed `int Prerequisite` to `int Prerequisite[PREREQUISITE_MAX]` (=4 slots, sentinel -1). `techno.cpp` constructor zero-initialises. Save format auto-bumps via `sizeof(BuildingTypeClass)` change.
- **`CCINIClass::Get_Buildings` rewritten** (`ccini.h`/`ccini.cpp`) — was `int Get_Buildings(section, entry, defvalue)` returning a bitmask; now `bool Get_Buildings(section, entry, int* out, int max)` filling caller's array with heap-aware Type indices via `BuildingTypeClass::As_Pointer`. Unused slots filled with -1.
- **`HouseClass::Can_Build` prereq check** (`house.cpp:935-988`) — iterates the Prerequisite array, requires `Has_Building_Active(T) > 0` per slot. The `STRUCTF_ADVANCED_POWER`→`STRUCTF_POWER` and `STRUCTF_SOVIET_TECH`↔`STRUCTF_ADVANCED_TECH` equivalences are preserved as explicit Type-index checks. The unused human-vs-AI `OldBScan` distinction was dropped — in practice OldBScan == ActiveBScan after every `Recalc_Attributes`.
- **`HouseClass::ActiveBQuantity[MAX_BUILDING_TYPES]`** (`house.h:594-596`) — new heap-sized per-Type counter array mirroring `ActiveBScan` semantics (unlimbo'd + locked). Maintained at the same three sites where ActiveBScan was: `building.cpp` Unlimbo via the new `HouseClass::Active_Building_Add` helper, and `house.cpp` `Recalc_Attributes` full rebuild. Public `Has_Building_Active(int)` inline accessor.
- **`HouseClass::BQuantity`** resized from `[STRUCT_COUNT]` to `[MAX_BUILDING_TYPES]` (`house.h:592`). Existing `Tracking_Add`/`Tracking_Remove` writes now land in valid slots for mod Types (previously: silent one-past-array writes for TDNUKE/TDNUK2 → memory corruption of whatever sat after BQuantity in HouseClass).
- **`MAX_BUILDING_TYPES` constant** (`defines.h:1462`) defined as `STRUCT_COUNT + 50`, matching the `BuildingTypes.Set_Heap()` ceiling in `init.cpp:228` (now using the constant). Same for `PREREQUISITE_MAX = 4`.
- **`1L << Type` undefined-behaviour guards** in `building.cpp:1163-1165` (Unlimbo BScan/ActiveBScan writes) and `house.cpp:6786-6788` (Tracking_Add BScan write). `Recalc_Attributes` already had the guard at line 7124. Mod Types skip the bitmask write since no `STRUCTF_*` constant references them anyway; ActiveBQuantity handles the per-Type tracking.

### Manifest + tooling

- **`shape_size` field** added to `buildings_manifest.py` schema and `scripts/add_building.py` FIELD_SPEC. Closes the gap noted in the phase3d session pickup. Emits `ShapeSize=W,H` after `Footprint=`, matching the field order on the hand-written reference block.
- TDNUKE/TDNUK2 entries populated with `shape_size: (48, 48)` and `sight: 5` (up from TD-authentic 2; RA's reveal radius scale is bigger and 2 left the building's own footprint partially in fog).
- `resources/remaster_mods/Vanilla_RA/CCDATA/rules.ini` regenerated; ShapeSize line is now part of the manifest emit (was previously hand-maintained).

### Validation (Deck, 2026-05-19)

- Vanilla skirmish unaffected — AI grows full tech tree, sell/repair/radar/superweapons functional.
- TDNUKE builds; TDNUK2 stays locked at game start and **unlocks the instant TDNUKE finishes construction** — the literal prereq path is working end-to-end through the new array-based check.
- AI naturally attacks France-as-HOUSE_GOOD with both baited and unbaited harasses.
- Sight=5 reveal ring comfortably clears the 2×2 footprint. (Diagnostic `Sight=100` exposed the engine's cap at `map.cpp:587` — `sightrange > 10` silently no-ops; unrelated to Phase 1 but documented for future reference.)

### Note: Temporary dev hack in working tree

`redalert/scenario.cpp`'s `Start_Scenario` has a `#if 1`-gated reveal-all hook (skirmish only) for observing 7-AI matches without shroud. **Not committed**; tracked as a working-tree-only diagnostic per `docs/catalogue.md`'s new "TEMPORARY DEV HACKS" section.

## [0.3.0-phase2] — 2026-05-18 — Branch reconciliation

Combined the v0.2.0 faction-bitmask work (`feature/house-good-differentiation`) with the v0.3.0 phase-1 Logic-aliased mod-building pipeline (`feature/emc-integration`). Both branches diverged from `vanilla` independently; this consolidates them onto a single trunk.

### Cherry-picked from feature/house-good-differentiation

- `42ef816` Initial rebrand: README, `README-VANILLA-CONQUER.md`, `deploy.sh`, rebranded `ccmod.json`.
- `42f75ce` v0.2.0-alpha: `HOUSEF_GOOD`/`HOUSEF_BAD` detached from `HOUSEF_ALLIES`/`HOUSEF_SOVIET` in `defines.h`; `HOUSEF_GDI`/`HOUSEF_NOD` aliases added; France country slot routed to `HOUSE_GOOD` in `dllinterface.cpp`.
- `946fb9c` v0.2.0-beta: 4-side-aware Unlimbo dispatch in `building.cpp`; `CNC_Set_Multiplayer_Data` debug dump retained.

### Dropped (explicitly superseded)

- `2717861` v0.2.0 revert marker — CHANGELOG/version-only, no code.
- `7c24666` v0.3.0-alpha — the parked hardcoded-enum approach (`STRUCT_GDI_CONST`, `STRUCT_GDI_POWER`, `UNIT_GDI_MCV`) plus 17 MB of vendored TD-Assets ZIPs. Superseded by the Logic-aliased pipeline (phase 1a-f) which adds new building types via INI rather than DLL enum extension.
- `18b5e03` "Pivot to EMC" marker — obsolete now that the pipeline shipped.

### State after reconciliation

- Engine pipeline (phase 1a-f) is in place: INI-defined `[NewBuildings]` entries with `Logic=<donor>` aliasing produce buildable, sidebar-rendered, art-correct buildings. Verified with `NUK2` as GDIPowerPlant on 2026-05-18.
- Faction bitmasks are detached: `Owner=allies` no longer pulls in `HOUSE_GOOD`. Owner= semantics for the catalogue design can now target `good` / `bad` / `gdi` / `nod` for true faction separation. Effect on test data: existing `Owner=allies` entries (e.g. NUK2 testbed) need updating to target the GDI faction explicitly once catalogue design lands.
- France country selection still routes to `HOUSE_GOOD` at the DLL boundary. Launcher UI still shows "France".

### Verification

- Built clean with the mingw remaster preset (145/145 objects, no errors).
- Full Steam Deck regression test deferred until catalogue work begins — current testbed (`tiberian-factions-emc-test` Deck folder) is not affected by this consolidation since it ships its own DLL/data; the reconciled trunk deploys to a fresh `Vanilla_RA` folder per `deploy.sh`.

## [0.2.0-beta] — 2026-05-16

### Engine

- Updated `BuildingClass::Unlimbo` in `redalert/building.cpp` to be 4-side-aware. The TD-era dispatch only checked `HOUSEF_GOOD` / `HOUSEF_BAD` for the building's side identity, which collapsed to "Soviet placeholder" for *every* building once GDI/Nod were detached in v0.2.0-alpha. Now dispatches on the RA side bits (`HOUSEF_ALLIES`, `HOUSEF_SOVIET`) plus our new `HOUSEF_GDI` / `HOUSEF_NOD`, and preserves the building's initial `ActLike` (= owner's identity) when the building has no side bits set — letting HOUSE_GOOD / HOUSE_BAD players retain their own side identity through to the sidebar query.
- Verified end-to-end on the Steam Deck: vanilla Allied (England) and Soviet (USSR) players get their normal tech trees back; France → HOUSE_GOOD player gets an empty / sparse build menu (no buildings carry the HOUSEF_GOOD bit yet — that's v0.2.0 final).
- Retained the `CNC_Set_Multiplayer_Data` debug dump for the next investigation phase. Will remove once we no longer need per-building Ownable inspection.

### Known issues / next steps

- HOUSE_GOOD has no buildable items. v0.2.0 final will add HOUSEF_GOOD to a starter set (Power Plant, Construction Yard, Refinery, Barracks) so GDI has a real tech tree.
- Voice prefix issue persists: HouseGood's `'G'` prefix maps to Soviet voicelines (no `'G'`-prefixed RA voice files; falls back to Soviet). Separate fix.

## [0.2.0-alpha] — 2026-05-16

### Engine

- Detached `HOUSE_GOOD` from `HOUSEF_ALLIES` and `HOUSE_BAD` from `HOUSEF_SOVIET` in `redalert/defines.h`. Vanilla RA bundled the TD houses into the RA side bitmasks, causing them to silently inherit the Allied / Soviet tech trees. With this change, the TD houses form their own (initially empty) factions.
- Added `HOUSEF_GDI` and `HOUSEF_NOD` aliases for clarity in subsequent commits.

### Status

- France country slot is hijacked into HOUSE_GOOD at the DLL boundary via [[spike branch reference]] (not yet wired into `main`). Result: France player will see a near-empty build menu — proof of detachment. Re-granting buildables comes in v0.2.x.
- Nod (HOUSE_BAD) detachment is symmetric but untested in this commit — only HOUSE_GOOD has a launcher route via the swap.

## [0.1.0] — Initial scaffolding (not separately tagged)

- Forked Vanilla Conquer as the DLL build base.
- Rebranded `ccmod.json` for "Tiberian Factions for Red Alert".
- Added `deploy.sh` for build + Steam Deck deploy over Tailscale.
