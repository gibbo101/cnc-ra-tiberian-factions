# Launcher vs DLL — the ownership map

**Status:** Mapped 2026-05-28 from the GPL interface source (`redalert/dllinterface.{h,cpp}`) + `strings ClientG.exe`. No decompile required; every conclusion below is evidence-backed. This is the "ends the guessing" reference — when a behavior is unclear, check here before assuming whether it's launcher- or DLL-controlled.

Complements `building-sound-routing.md` (credit-tick / per-event audio detail), `td-audio-routing-recipe.md` (SFXEvent mechanics), and `reference-td-eva-routing` (EVA voices).

---

## TL;DR — the governing principle

The Remastered front-end (Petroglyph "Mobius" engine, **native C++**) is **faction-blind**. It talks to our DLL over a narrow, fixed C ABI. Three rules follow:

1. **The launcher only knows what crosses the boundary.** If a piece of state (faction/side, render mode, a specific sound trigger) isn't in an interface struct or the callback, the launcher cannot act on it.
2. **Faction-aware behavior is DLL-emitter-only.** The launcher plays audio and renders UI from the *name/value* the DLL hands it; it never branches on the player's faction itself. The single lever for GDI/Nod-specific behavior is **the DLL choosing the name/value (keyed on `ActLike`) before it crosses**. This is exactly how our shipped radar / EVA / unit-voice routing works.
3. **Whatever the launcher does autonomously is not mod-controllable from the DLL** — the credit-counter animation + tick, the classic/remaster view toggle, sidebar layout. (This is the *code* boundary — see the DATA caveat below.)

**The DATA lever (added 2026-05-28).** Rules 1–3 are about launcher *code*. The *data the launcher reads from `CONFIG.MEG`* — faction defs (`FACTIONS.XML`), Mission Select (`INSTANCES.XML`), localized strings (`MASTERTEXTFILE`), theatres/tilesets, GUI lists — **is moddable AND Workshop-shippable**: a mod ships its own `Data/CONFIG.MEG` and the launcher loads it over the base (proven on the Deck). So **"launcher-owned" ≠ "unmoddable"** — ask whether a behaviour is driven by CONFIG.MEG **data** (moddable) or hardcoded in `ClientG.exe` **code** (not). Canonical: `config-meg-mod-delivery.md`.

**The UI-image lever (added 2026-05-29).** Launcher 2D UI *images* — the sidebar faction crest, lobby logos, flags, buttons — live in the `MT_COMMANDBAR_COMMON.TGA` atlas and are **moddable** via a byte-edited loose `.TGA` in `Data/ART/TEXTURES/SRGB/` (vanilla, **no EMC**, proven on the Deck). So the real test is a **trichotomy**: CONFIG.MEG *data* and texture-atlas *images* are both moddable; only `ClientG.exe` *code* is the true lock. (The in-game sidebar emblem was first mis-filed as a code lock — it's an atlas image, `UI_SIDEBAR_FACTIONLOGO_ALLIES`.) Canonical: `ui-atlas-modding.md`.

---

## The process model (runtime-confirmed 2026-07-11)

The Remastered runs **three processes**, and this is the foundation under every row of the ownership map. Confirmed at runtime via `/proc` on the live game (Deck) + static RE + a 3-way adversarial spike ([[spike-launcher-process-model]]):

```
ClientLauncherG.exe   — outer bootstrap/menu shell; spawns the other two
        ├── ClientG.exe          — THE "LAUNCHER"/front-end: renderer, UI, input,
        │                          faction picker, hotkeys. Imports d3d11/d3d9/bink2/mss32.
        │                          Hosts NO game DLL — its ONLY contact with our RedAlert.dll
        │                          is a version handshake: LoadLibraryA → GetProcAddress("CNC_Version")
        │                          → compare 0x102 → FreeLibrary.
        │        │  loopback TCP :16000 — encrypted + HMAC'd + CRC'd (CryptoPP), fixed message set
        │        ▼
        └── InstanceServerG.exe   — the SIM server; the ONLY process that hosts our mod DLL
                                   (LoadLibrary of .../Mods/Red_Alert/Vanilla_RA/Data/RedAlert.dll +
                                   the full CNC_Init/Advance_Instance/Get_Game_State/Handle_* interface).
                                   Maps only our DLL + crypto/ssl/curl/steam_api/tbb — ZERO rendering/UI code.
```

`ClientG` dials **out** to `InstanceServerG` (the server on `CLIENT_PORT=16000`). The C&C payload on that socket is a **1:1 serialization of the CNC ABI**: the 13-member `EventCallback` union outbound (`GamePluginClass::Event_Callback` → `SERVER_TO_CLIENT_EXTERNAL_GAME_PLUGIN_EVENT`), and the `CNC_Get_Game_State` structs pulled inbound (`Export_State`/`Import_State`). ClientG's receiver (`IncomingExternalGamePluginEventClass::Execute`) is a **fixed compiled switch** over exactly those types — **no passthrough branch**; unknown payloads are dropped.

**Consequence — the CNC ABI *is* the process-boundary wire format, not a soft convention.** Our DLL runs only in `InstanceServerG` and cannot reach `ClientG`'s memory (separate process; no shared game-data segment — the only shared `/dev/shm` objects are Steam-IPC + wine-fsync infra). Our DLL can even patch its own host in-process, but that's inert: the receiver lives in the unmoddable `ClientG` binary and the BitStream is positional (appended fields desync + fail CRC). **Anything the front-end has no compiled handler for cannot be created by the running DLL, no matter what it emits** — new factions, new UI structure, new hotkey classification are all off the table at runtime. To "open up more options" you feed `ClientG` richer **data files at load** (CONFIG.MEG/FACTIONS.XML/textures) — there is no runtime channel. Adversarially verified 2026-07-11: 3 independent break attempts (socket-forge, data-file side-channel, in-process host-patch) all failed. Live lead for shell-UI reshaping: `ClientG`'s front-end is **Lua 5.1 + ClickScript VM + XML/.bui** data-driven — a *data* avenue, not a DLL one, and unprobed.

---

## Binary facts (so we never re-investigate tooling)

- `ClientG.exe` (34 MB), `ClientLauncherG.exe`, `InstanceServerG.exe` are **native PE32 C++** — no CLR header (`mscoree` / `coreclr` / `hostfxr` all absent). **ILSpy/dnSpy do not apply.**
- The **only** managed .NET binary in the install is `CnCTDRAMapEditor.exe` (.NET Framework 4.6.2 WinForms; source is already public on GitHub). The `System.*` / `Newtonsoft.Json` / `Pfim` DLLs in `bin/` are **the map editor's** dependencies — *not* evidence that the launcher is managed. (This was the false lead in the original "crack the launcher" memory note: .NET assemblies present in `bin/` ≠ managed launcher.)
- Engine identity from strings: `pgaudio` (`SFXEventManagerClass`, `SFXEventClass`), build paths `c:\buildsystem\...\mobius\qa\libs\pgaudio\...`.
- Native RE tooling on this machine: `objdump`, `strings` only (no Ghidra/rizin/wine). A *targeted* Ghidra dive is possible but currently unwarranted — see the last section.

---

## The interface contract

### Launcher → DLL: 30 `extern "C"` exports (`dllinterface.cpp:118-218`)

| Group | Exports |
|---|---|
| Lifecycle | `CNC_Version`, `CNC_Init` *(registers the one callback)*, `CNC_Config`, `CNC_Add_Mod_Path`, `CNC_Shutdown` |
| Game start | `CNC_Start_Instance` / `_Variation` / `_Custom_Instance`, `CNC_Set_Multiplayer_Data`, `CNC_Read_INI`, `CNC_Set_Difficulty`, `CNC_Restore_Carryover_Objects`, `CNC_Get_Start_Game_Info` |
| Per-frame | `CNC_Advance_Instance` *(the tick)*, `CNC_Get_Game_State` *(pull state)*, `CNC_Get_Visible_Page` *(classic framebuffer)*, `CNC_Get_Palette` |
| Input / commands | `CNC_Handle_Input`, `CNC_Handle_Sidebar_Request`, `CNC_Handle_Structure_Request`, `CNC_Handle_Unit_Request`, `CNC_Handle_SuperWeapon_Request`, `CNC_Handle_ControlGroup_Request`, `CNC_Handle_Beacon_Request`, `CNC_Handle_Game_Request`, `CNC_Handle_Game_Settings_Request`, `CNC_Handle_Debug_Request`, `CNC_Set_Home_Cell`, `CNC_Clear_Object_Selection`, `CNC_Select_Object` |
| Misc | `CNC_Save_Load`, `CNC_Handle_Player_Switch_To_AI`, `CNC_Handle_Human_Team_Wins`, `CNC_Start_Mission_Timer` |

There is **no** export and **no** input-enum value for a render-mode toggle. `INPUT_REQUEST_SPECIAL_KEYS` only carries Ctrl/Alt/Shift (`dllinterface.h:483`).

### DLL → Launcher: one callback (`EventCallbackStruct`, `dllinterface.h:592`)

Everything the DLL tells the launcher flows through the single `CNC_Event_Callback_Type EventCallback` registered in `CNC_Init` (`dllinterface.cpp:486, 718`). Union event types:

`CALLBACK_EVENT_SOUND_EFFECT`, `_SPEECH`, `_GAME_OVER`, `_DEBUG_PRINT`, `_MOVIE`, `_MESSAGE`, `_UPDATE_MAP_CELL`, `_ACHIEVEMENT`, `_STORE_CARRYOVER_OBJECTS`, `_SPECIAL_WEAPON_TARGETTING`, `_BRIEFING_SCREEN`, `_CENTER_CAMERA`, `_PING`.

- **Audio** (`SoundEffect` / `Speech`) carries a 16-char **name**; the launcher prepends `RAC_SFX_` / `RAR_SFX_` and resolves the SFXEvent from `SFXEVENTSNONLOCALIZED.XML`. Faction-blind unless the DLL picked the name.

### State pulled via `CNC_Get_Game_State`

- **`CNCSidebarStruct`** (`dllinterface.h:344`): `Credits`, **`CreditsCounter`** *(animated display value — `= PlayerPtr->VisibleCredits.Current`, `dllinterface.cpp:4829`)*, `Tiberium`, `PowerProduced/Drained`, `MissionTimer`, kill/loss counters, button-enable flags, `RadarMapActive`, + variable `Entries[]`.
- **`CNCObjectStruct` / `CNCDynamicMapStruct` / `CNCMapDataStruct` / `CNCShroudStruct`**: render data.
- **`CNCPlayerInfoStruct`** (`dllinterface.h:760`): `House` crosses here — **the only place faction-ish identity reaches the launcher** — but it's the raw RA house. GDI=`HOUSE_GOOD` / Nod=`HOUSE_BAD` collapse to Allied/Soviet for the launcher's purposes.

---

## Ownership map (the table that ends the guessing)

| Feature | Owner | Faction-routable from DLL? | Evidence |
|---|---|---|---|
| Gameplay SFX (weapons, placement, construction) | DLL emits by name | **Yes** — key on `ActLike` before `On_Sound_Effect` | `dllinterface.cpp:2553` |
| EVA / speech | DLL emits by name | **Yes** — `SpeechTD[]` | `On_Speech`; `reference-td-eva-routing` |
| Radar on/off SFX | DLL emits by name | **Yes (shipped)** | `dllinterface.cpp:2553` (`VOC_RADAR_ON/OFF` branch) |
| Unit acknowledgment voices | DLL emits by name | **Yes (shipped)** | `dllinterface.cpp:2638` |
| **Credit counter + tick** | **Launcher** | **No** — global; launcher fires `RAR_SFX_CASHUP1` itself | `credits.cpp:102`; strings `GUI_Credits_Up_Tick`, `RAR_SFX_CASHUP1`; `building-sound-routing.md` |
| **Classic/remaster view toggle (spacebar)** | **Launcher** | **No** — and the DLL cannot even *observe* it (see below) | `Legacy_Render_Enabled`; no input enum |
| Sidebar build icons / cost / progress | DLL supplies per-entry; launcher renders | **Partial** — DLL owns `AssetName`/cost/etc. | `CNCSidebarEntryStruct` |
| HUD credit/power/timer **values** | DLL supplies values; launcher renders | Values yes, rendering no | `CNCSidebarStruct` |
| Superweapon `$cost` line suppression | Launcher (`SW_` whitelist) | No | `reference-launcher-superweapon-cost-suppression` |
| Win/lose stings, "under attack", low-power GUI SFX | Launcher (`Faction_Event_GUI_SFX_*`) | No (Allied/Soviet only — see below) | strings |

---

## The one new lead: the launcher's `FactionType` audio table — and why it can't help us

`strings ClientG.exe` revealed a **real per-faction audio system** in pgaudio: a `FactionType` enum and a family of `Faction_Event_GUI_SFX_*` events (`Credits_Start_Gain`, `ConstructionComplete`, `Low_Power`, `HQUnderAttack`, `InsufficientFunds`, …) parsed from XML via `XMLTypeConverterClass::Convert<enum FactionTableAudioTypeEnum, SFXEventClass>`. At first glance this looks like a launcher-side faction hook we could exploit. **It is not usable for GDI/Nod**, for three independent reasons:

1. **No GDI/Nod faction exists in the launcher.** The only C&C faction tokens are `ALLIED` / `SOVIET`. The `GDI` string hits are Windows **G**raphics **D**evice **I**nterface — *"render target is not compatible with GDI"* — false positives; there is **no `NOD` token at all.**
2. **Much of `FactionType` is dormant cross-title engine code.** Sibling events like `Currency_Wood_Stolen`, `Animal_Stolen`, `EpicConstructed`, Metagame-AI build orders, `Coordinator_Quick_Match` are from Petroglyph's *other* Mobius-engine titles — present in the shared lib, not wired up for RA.
3. **Our factions are ActLike-hijacked**, so even where the launcher *is* faction-aware it sees Allied/Soviet, not GDI/Nod. And the credit **tick** (`RAR_SFX_CASHUP1`) is not faction-prefixed anyway — it's a single global event.

**Consequence for the future genuine-houses arc:** even if we someday add real `HOUSE_GDI`/`HOUSE_NOD` engine houses, the launcher still won't gain GDI/Nod faction-audio slots (they don't exist in the binary), so faction UI/audio would *still* be DLL-emitter-routed. The launcher's `FactionType` table is a dead end for our purposes regardless.

---

## Select-all (`a`) and Deploy (`/`) unit classification — RESOLVED (2026-06-03)

**Question:** the `a` "select all combat units" and `/` "deploy" hotkeys ignore our TD-faction harvester (`TDHARV`) and MCV (`TDMCV`) — recognising only RA's `HARV`/`MCV`. Is there a moddable lever?

**Both levers are closed. The classification is compiled into `ClientG.exe`.**

### The launcher's component-object model (`strings ClientG.exe`)
`ClientG.exe` runs Petroglyph's Mobius **component model**: it imports each game object from our DLL and maps it into native components via an `ExportBits.*` bitfield. Relevant components: `ResourceHarvesterComponentClass` (harvesters), `LocomotorComponentClass` (move), `TurretComponentBaseClass` (turret), `SelectBaseComponentClass` (selectable), `StructureConstructionComponentClass` (deploy/build). The hotkey commands exist as `COMMAND_CNC_SELECT_ALL_ON_SCREEN` / `_IN_WORLD` and `COMMAND_CNC_DEPLOY_SELECTED_MCV`, dispatched through `RTSInputManagerClass`. **The mapping from our narrow `CNCObjectStruct` fields → these components is hardcoded in the binary** — we control only the `CNCObjectStruct` fields, never the mapping.

### Data lever (CONFIG.MEG): DEAD — proven negative
Extracted + enumerated CONFIG.MEG (`scripts/meg_extract.py`). The only per-unit table is `DATA/XML/OBJECTS/UNITS/RABUILDABLES.XML`, and **all 189 entries share an identical 3-field schema** — `<CNCEncyclopediaComponent>` with `ObjectNameTextID` / `ObjectDescriptionTextID` / `BuildIcon` only. There is **no role / combat / deployable / harvester / selectable / category field on any entry**: `RA_HARV`, `RA_MCV`, the deployable `RA_MNLY`, and a plain `RA_1TNK` tank are byte-for-byte the same field set. `BUILDABLECATEGORIES.XML` = three sidebar display groups (no per-unit map). `OBJECTSTATES.XML` defines state-type *classes* (`Harvester`, `IsDeployed`, `Refinery`) but **never binds them to specific units** — that binding is made at runtime by the DLL/engine. **Conclusion: select-all/deploy classification is NOT in CONFIG.MEG data; shipping a modded `Data/CONFIG.MEG` cannot reach it.**

### Binary lever: hardcoded by identity, not a settable flag
The MCV is recognised by IniName/numeric type, not an exported capability bit: `CNCObjectStruct.CanDeploy` / `IsDeployable` are **declared but never populated** by us *or* EA (grepped both trees), yet RA's MCV deploys fine — so the launcher does **not** gate on them; they're vestigial. The MCV-deploy spike already tried the one DLL lever (spoof `TypeName="MCV"` for `TDMCV`) and the deploy key still ignored it ([[project-mcv-deploy-hotkey-spike]]).

### What this means
- **BOTH the harvester AND the MCV leak on `a`** — Deck-confirmed 2026-06-03 (Luke). This **disproves** the earlier guess that `CanHarvest=true` (exported for `TDHARV`) would get the harvester excluded. The launcher's `a`-exclusion does **not** read the `CanHarvest` bit; it recognises RA's `HARV`/`MCV` by **hardcoded identity** (which is why the RA units don't leak but `TDHARV`/`TDMCV` do). The `ResourceHarvesterComponent` mapping evidently drives other harvester behaviour (resource UI/cursor), not the select-all filter.
- **`a`-exclusion (both units) and `/`-deploy (MCV) are the closed-launcher wall** — same family as the MCV-deploy hotkey and the classic-mode spacebar.
- **The DLL-routed drag-box select IS fixed** — `should_exclude_from_selection` (display.cpp ~2827) now lists `UNIT_TDMCV`; `TDHARV` covered by `IsToHarvest`. Only the launcher-driven `a`/`/` army paths remain gated.

### Per-frame export spoofs are a DEAD END — TESTED & CONFIRMED 2026-06-03
Both `CNCObjectStruct.TypeName` (= `Class_Of().IniName`, dllinterface.cpp ~3755) and `AssetName` (= graphic name, ~3758-3760) are per-frame export fields. Spoofing them does **not** reach the launcher's `a`/`/` recognition:
- **`TypeName="MCV"` spoof** (MCV-deploy spike): deploy `/` still did nothing.
- **`AssetName`+`TypeName`→`"MCV"`/`"HARV"` spoof, Deck-tested 2026-06-03**: **no effect at all** — the GDI/Nod harvester/MCV **still rendered as their TD sprites** AND `a` **still selected them**. The launcher binds a unit's sprite + type identity **once, at object/type registration**, then references it by an internal handle; per-frame export-field overrides are simply ignored for an already-known unit. (This also means `AssetName` only matters at registration, not per-frame.)
- **Conclusion:** the `a`-exclusion and `/`-deploy recognition live at the registered-type level inside `ClientG.exe`, unreachable from the DLL's per-frame export. There is **no per-frame field we can spoof**. Shipped as a Known Limitation on the Workshop page (v1.11). Don't re-test export-field spoofs.
- **A Ghidra decompile of `ClientG.exe`** is the only route that could resolve it and is **not worth it** for cosmetic hotkey convenience — see the next section's cost/benefit bar.

---

## Diagnostic techniques that work here (reusable)

- **"Is this sound DLL- or launcher-driven?"** Drop an `fopen`-append log at the DLL call site; an *empty* file while the game runs proves the launcher owns it. (Used to prove the credit tick. Use `%USERPROFILE%` paths — `reference-diagnostic-paths`.)
- **"Does the launcher know about X?"** `strings -n N ClientG.exe | grep`. Demangled C++ symbols expose class/struct/enum names: `XMLTypeConverterClass<...>` shows exactly which XML→type conversions exist; `Faction_Event_GUI_SFX_*` enumerates the launcher's GUI-SFX vocabulary.
- **"What can cross the boundary?"** Read `dllinterface.h` — it is the complete contract, nothing else gets through.

---

## When a Ghidra dive WOULD be worth it

**Not now.** Source + strings answer every standing question, and the `FactionType` lead dead-ends on a negative a decompile would only re-confirm — at the cost of installing Ghidra and disassembling 34 MB of stripped, optimized native C++.

A decompile becomes worthwhile only if **both** hold: (a) we commit to genuine engine houses, **and** (b) we need the exact `House → FactionType/side` mapping logic — e.g., to learn whether new house slots could ever map to launcher faction/color/audio slots, or to extract the credit-counter animation parameters. Until then the value doesn't clear the cost.

---

## Engine gotchas migrated from cross-session memory (2026-07-15)

### `this == PlayerPtr` is ALWAYS TRUE inside HouseClass::AI (REMASTER_BUILD)
`HouseClass::AI()` opens with `Logic_Switch_Player_Context(this)` under `#ifdef REMASTER_BUILD`, so
`PlayerPtr` is reassigned to the current house every tick. Any `if (this == PlayerPtr)` later in
HouseClass::AI runs for EVERY house, not just the local player. Use `IsHuman` (skirmish) or the GlyphX
local-player index `DLLExportClass::CurrentLocalPlayerIndex` (MP) instead. Also: `ActiveBScan &
STRUCTF_RADAR` / `Map.IsRadarActive` oscillate 1/0 every frame (Recalc_Attributes quirk) — never
edge-detect on the radar scan bit; count the Buildings heap + `Power_Fraction()` and debounce.

### Superweapon $cost line: keyed on AssetName string, not the SW_ enum
The launcher suppresses the "Cost: $N" line only for AssetNames on its internal RA-context whitelist
("SW_Nuke","SW_Chrono","SW_GPS","SW_SonarPulse"...). `SW_ION_CANNON` (a TD-side DllSuperweaponTypeEnum
value) isn't whitelisted -> the Ion Cannon cameo shows $0. Engine-side `CNCSidebarEntryStruct.Cost` is
IGNORED for supers. Cosmetic, unfixable mod-side (closed ClientG binary). Accept the $0.

### Roster-scaling launcher CTD — NameOverride[25] table exhaustion
Adding the ~30th unit TYPE crashed the launcher (std::string(NULL) in InstanceServerG) on refinery
placement/MCV deploy. Root cause: every techno with a rules.ini `Name=` HD override registers into
`NameOverride[25]`, rules are read TWICE (rules.ini + aftrmath.ini) with no dedup -> the 25-slot table
exhausts; plus `Text_String` off-by-one rejected the last slot -> NULL -> CTD. Fix (all DLL): tables
25->128; dedup by id in TechnoTypeClass::Read_INI; inline.h `<`->`<=`; NULL-guard OverrideDisplayName in
dllinterface.cpp. Only after this could the roster keep growing.

### Classic-mode toggle: the DLL cannot detect it AT ALL (measured 2026-07-19)

Previously recorded as "launcher-owned, DLL only gates availability". In-game testing
hardened that considerably — a mod cannot even tell whether classic mode is on screen,
let alone react to it.

- **Refusing the page does not suppress the toggle.** Returning false from
  `CNC_Get_Visible_Page` makes the launcher switch to classic and render an empty
  viewport (HUD still drawn over it). The launcher decides toggle availability from its
  own lobby data and never consults us; EA simply implemented the same `num_humans < 2`
  rule independently on both sides, which is why it looks like one gate in MP.
- **The page is requested EVERY FRAME regardless of displayed mode** — the launcher
  keeps it warm so toggling is instant. So "is the page being asked for?" carries no
  information about what the player is looking at. Any heuristic built on call
  frequency, gaps, or streaks will fire during normal HD play.
- **The spacebar never reaches the DLL.** `DLLExportClass::Get_Input_Key_State` handles
  only `KN_LCTRL` / `KN_LSHIFT` / `KN_LALT` and returns false for everything else;
  `INPUT_REQUEST_SPECIAL_KEYS` carries the same three modifiers.

**Consequence:** a notice shown only when the player enters classic mode is not
implementable from a mod. The available options are an unconditional match-start
message, or nothing. Anything drawn INTO the classic page is also map-positioned
(`view_port_width = Map.MapCellWidth * CELL_PIXEL_W`), so it scrolls with the terrain
rather than sitting on screen; launcher messages via `On_Message` are screen-fixed, but
`On_Message` only lands when issued from `CNC_Advance_Instance` after the player context
is set.

**RAM route also tried and abandoned (2026-07-19).** ClientG's memory IS readable
cross-process (the difficulty scanner already does it), so the render-mode flag is in
principle findable by toggling and keeping bytes that track it. Attempted with 3 HD +
3 classic snapshots (~1.1GB each) of private writable regions: 13,515 bytes tracked the
toggle, 3,856 survived three pairs, 33 were isolated and boolean-shaped. Live-polling
those candidates while the player toggled 4 times showed **every one changing 100+ times
in 75 seconds** — all high-churn render state that coincidentally aligned. **No flag
found.**

The method is sound but misapplied: value-narrowing assumes a mostly-static process
between samples, and a running RTS changes vast amounts of memory for unrelated reasons,
so coincidental survivors swamp the signal. Doing it properly needs live iterative
filtering (hold the candidate set in memory, re-filter on every toggle, ~a dozen rounds)
rather than offline diffing of a few snapshots. Not worth it for a cosmetic notice;
revisit only if classic-mode detection is ever needed for something substantial.
Tooling kept: session scratchpad `ram_toggle_probe.py` + `watch_candidates.py`.
