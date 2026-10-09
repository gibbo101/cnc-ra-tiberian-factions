# Launcher vs DLL — the ownership map

**Status:** Reference. The launcher/DLL boundary map, as of 5.0.0.

The launcher/DLL boundary map: is a behaviour owned by the launcher (`ClientG.exe`) or by our
DLL, and can a mod reach it? Check here before assuming either way. Four levers reach
launcher-owned behaviour: CONFIG.MEG data, loose texture files, the sim's writes into ClientG
memory, and code patches from the DLL copy ClientG loads at startup.

Complements `building-sound-routing.md` (per-event audio) and `td-audio-routing-recipe.md`
(SFXEvent mechanics and EVA voices).

---

## TL;DR — the governing principle

The Remastered front-end (Petroglyph "Mobius" engine, **native C++**) is **faction-blind**. It talks to the sim over a narrow, fixed C ABI. Three rules follow:

1. **The launcher only knows what crosses the boundary.** If a piece of state (faction/side, render mode, a specific sound trigger) isn't in an interface struct or the callback, the launcher cannot act on it.
2. **Faction-aware behaviour starts in the DLL.** The launcher plays audio and renders UI from the *name/value* the DLL hands it; it never branches on the player's faction itself. The lever for per-faction behaviour is **the DLL choosing the name/value (keyed on `ActLike`) before it crosses**, which is how the radar, EVA, unit-voice and credit-tick routing work.
3. **What the launcher does by itself needs one of the four levers below.** "Launcher-owned" does not mean "unmoddable"; it means the sim alone cannot change it.

**The data lever.** The data the launcher reads from `CONFIG.MEG` (faction defs in `FACTIONS.XML`, Mission Select in `INSTANCES.XML`, `MASTERTEXTFILE` strings, theatres, GUI lists, `.bui` screens) ships in the mod's own `Data/CONFIG.MEG`, which the launcher loads over the base; `Data/XML/GameConstants_Mod.xml` merges over GameConstants. Ask whether a behaviour is driven by data (moddable) before calling it a code lock. Canonical: `config-meg-mod-delivery.md`, `config-meg-lever-audit.md`.

**The image lever.** Launcher 2D UI images (the sidebar crest, lobby logos, flags, buttons, menus) come from the `MT_COMMANDBAR_COMMON.TGA` atlas or standalone textures, and a loose copy in `Data/ART/TEXTURES/SRGB/` overrides them in the shell and in game. Canonical: `ui-atlas-modding.md`.

**The RAM lever.** On the host, the sim's DLL opens ClientG (`TF_Open_ClientG`, `OpenProcess` + `ReadProcessMemory`/`WriteProcessMemory`) and rewrites its runtime state: the cached EVA sample blobs (`eva-ram-patch-spike.md`) and the cached per-region UV records behind the radar crest and sidebar (`radar-crest-ram-spike.md`). It changes what an existing launcher-drawn element samples or plays, never layout. Probe with `scripts/clientg_region_probe.py`.

**The code-patch lever.** ClientG loads our DLL at its own startup on every machine, and `DllMain` patches ClientG's code in-process: the superweapon click specials, the key dispatcher and the plugin-event hook. The same copy applies the RAM lever for its own player in LAN games. See "Launcher-resident patches" below.

---

## The process model

The Remastered runs **three processes**:

```
ClientLauncherG.exe   — outer bootstrap/menu shell; spawns the other two
        ├── ClientG.exe          — THE "LAUNCHER"/front-end: renderer, UI, input,
        │                          faction picker, hotkeys. Imports d3d11/d3d9/bink2/mss32.
        │                          Loads our RedAlert.dll at startup for a version handshake
        │                          (CNC_Version); our DllMain patches ClientG's code and pins
        │                          the DLL so it stays loaded.
        │        │  loopback TCP :16000 — encrypted + HMAC'd + CRC'd (CryptoPP), fixed message set
        │        ▼
        └── InstanceServerG.exe   — the SIM server. On the hosting machine it loads our DLL
                                   (.../Mods/Red_Alert/Vanilla_RA/Data/RedAlert.dll) and runs the
                                   full CNC_Init/Advance_Instance/Get_Game_State/Handle_* interface.
                                   No rendering or UI code.
```

The sim runs in InstanceServerG, which loads the DLL on the hosting machine only (in LAN, only the host simulates). ClientG loads the DLL at startup on every machine; `DllMain` there (`TF_Patch_Launcher_At_Load`) patches launcher code and pins the DLL, and a worker thread woken by the host's `@@TFL:` message applies the faction patches for that machine's own player. On the host, the sim's DLL also patches ClientG across processes.

`ClientG` dials **out** to `InstanceServerG` (the server on `CLIENT_PORT=16000`). The C&C payload on that socket is a **1:1 serialization of the CNC ABI**: the 13-member `EventCallback` union outbound (`GamePluginClass::Event_Callback` → `SERVER_TO_CLIENT_EXTERNAL_GAME_PLUGIN_EVENT`), and the `CNC_Get_Game_State` structs pulled inbound (`Export_State`/`Import_State`). ClientG's receiver (`IncomingExternalGamePluginEventClass::Execute`) is a **fixed compiled switch** over exactly those types, with no passthrough branch; unknown payloads are dropped.

**Consequence: the CNC ABI is the wire format between sim and launcher.** The BitStream is positional (appended fields desync and fail the CRC), so nothing the sim emits can create launcher behaviour ClientG has no handler for. Launcher behaviour changes only through the four levers above. ClientG's front-end embeds Lua 5.1 and a ClickScript VM, but no `.lua` ships in any MEG and the CNC callback has no ClickScript member (`bui-front-end-modding.md`).

---

## Binary facts (so we never re-investigate tooling)

- `ClientG.exe` (34 MB), `ClientLauncherG.exe`, `InstanceServerG.exe` are **native PE32 C++** — no CLR header (`mscoree` / `coreclr` / `hostfxr` all absent). **ILSpy/dnSpy do not apply.**
- The **only** managed .NET binary in the install is `CnCTDRAMapEditor.exe` (.NET Framework 4.6.2 WinForms; source is already public on GitHub). The `System.*` / `Newtonsoft.Json` / `Pfim` DLLs in `bin/` are **the map editor's** dependencies — *not* evidence that the launcher is managed.
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

- **`CNCSidebarStruct`** (`dllinterface.h:344`): `Credits`, **`CreditsCounter`** *(animated display value, `PlayerPtr->VisibleCredits.Current`)*, `Tiberium`, `PowerProduced/Drained`, `MissionTimer`, kill/loss counters, button-enable flags, `RadarMapActive`, + variable `Entries[]`.
- **`CNCObjectStruct` / `CNCDynamicMapStruct` / `CNCMapDataStruct` / `CNCShroudStruct`**: render data.
- **`CNCPlayerInfoStruct`** (`dllinterface.h`): `House` crosses here, **the only place faction-ish identity reaches the launcher**, but it is the raw RA country house. GDI, Nod and TS GDI ride country houses (Spain, Greece, Germany), so the launcher sees Allied or Soviet.

---

## Ownership map (the table that ends the guessing)

| Feature | Owner | Faction-routable from DLL? | Evidence |
|---|---|---|---|
| Gameplay SFX (weapons, placement, construction) | DLL emits by name | **Yes** — key on `ActLike` before `On_Sound_Effect` | `dllinterface.cpp:2553` |
| EVA / speech | DLL emits by name | **Yes** — `SpeechTD[]` | `On_Speech`; `td-audio-routing-recipe.md` |
| Radar on/off SFX | DLL emits by name | **Yes (shipped)** | `dllinterface.cpp:2553` (`VOC_RADAR_ON/OFF` branch) |
| Unit acknowledgment voices | DLL emits by name | **Yes (shipped)** | `dllinterface.cpp:2638` |
| Credit counter animation | Launcher | No | strings `GUI_Credits_Up_Tick` |
| Credit tick | DLL emits by name; the launcher's own `RAR_SFX_CASHUP1` is silenced | **Yes (shipped)**, addressed to the house whose credits moved | `CreditClass::AI` → `TF_Fire_Credit_Tick`; `building-sound-routing.md` |
| **Classic/remaster view toggle (spacebar)** | **Launcher** | No, but data locks it out (`CNCDisableLegacyGraphicsOption`); the DLL cannot *observe* it (see below) | `GameConstants_Mod.xml`; no input enum |
| Sidebar build icons / cost / progress | DLL supplies per-entry; launcher renders | **Partial** — DLL owns `AssetName`/cost/etc. | `CNCSidebarEntryStruct` |
| HUD credit/power/timer **values** | DLL supplies values; launcher renders | Values yes, rendering no | `CNCSidebarStruct` |
| Superweapon `$cost` line suppression | Launcher (keyed on the AssetName string) | Only by choosing the AssetName | see "Superweapon $cost line" below |
| **Superweapon targeted-vs-instant firing** | **Launcher** (compiled: the cameo left-click handler forks on the entry being a superweapon) | **Yes, by a runtime code patch of ClientG** (every player; see "Launcher-resident patches"). Data levers are dead; see below | `TF_Patch_ClientG_Click_Specials`; see below |
| Launcher-played EVA lines (mission won/lost, select target, low power, cannot deploy, battle control terminated, repairing, mission saved, building in progress) | Launcher (`Faction_Event_GUI_SFX_*`) | **Yes (shipped)**, by overwriting the cached samples at match start | `eva-ram-patch-spike.md` |
| Other launcher GUI stings | Launcher | No (Allied/Soviet only, see below) | strings |

---

### Sidebar build-tab icons: named in ClientG CODE, fixed by rewriting the prefix string (2026-09-04)

GDI/Nod on TD's HUD scene still drew RA's gold 130x64 tab icons squashed into TD's 100x60
tab widgets, in every state (off/on/bright/placement), while repair/sell/map/plates were TD.
**Why these four only:** every other sidebar element is named in the scene file, so the
TD scene swap fixed them. The tab icons are the one element the launcher names in code: it
appends the state to a per-game prefix baked into `ClientG.exe` (`strings` shows both sets:
`UI_Sidebar_TabIcon_Structure_` ... and `UI_RA_Sidebar_TabIcon_Structure_` ...) and looks the
region up by that name; RA mode picks the RA prefix regardless of scene.

**Fix (`TF_Patch_ClientG_Tab_Prefix`, called from `TF_Patch_ClientG_Crest` at match start):**
locate the four RA prefix slots in ClientG's IMAGE (MEM_IMAGE regions) and
`VirtualProtectEx` + `WriteProcessMemory` the TD prefix over them for TD-era players (shorter,
NUL-terminated, always fits); write the RA prefix back for RA sides. Locate on EVERY call and
by EITHER form: after a TD-era match a slot reads as the TD string with the RA tail still behind
its terminator (which is also what tells it from the genuine TD prefix elsewhere in the image),
and the DLL instance does not persist between matches, so nothing can be cached. Verified both
ways in one launch (GDI green in every state incl. placement, Allied gold).

**Two dead detours, recorded so nobody repeats them:** (1) re-pointing the drawn UV RECORDS
(12 crest-style slots) works but every state's record is created on demand (first hover, first
"ready", placement), so each shows gold until the next heap scan — and scanning often enough
to hide that lags the game; (2) patching the atlas TABLE entry (`{w,h,x,y}` int32, name ptr 68
bytes before the quad, second `{w,h}` copy 32 before) makes new records right at birth but
still misses states born before the patch and needs the same heap walk. A code-side string
is the cheapest lever when the launcher builds a name in code: **grep `strings ClientG.exe`
for the name family before touching records.**

## The one new lead: the launcher's `FactionType` audio table — and why it can't help us

`strings ClientG.exe` revealed a **real per-faction audio system** in pgaudio: a `FactionType` enum and a family of `Faction_Event_GUI_SFX_*` events (`Credits_Start_Gain`, `ConstructionComplete`, `Low_Power`, `HQUnderAttack`, `InsufficientFunds`, …) parsed from XML via `XMLTypeConverterClass::Convert<enum FactionTableAudioTypeEnum, SFXEventClass>`. At first glance this looks like a launcher-side faction hook we could exploit. **It is not usable for GDI/Nod**, for three independent reasons:

1. **No GDI/Nod faction exists in the launcher.** The only C&C faction tokens are `ALLIED` / `SOVIET`. The `GDI` string hits are Windows **G**raphics **D**evice **I**nterface — *"render target is not compatible with GDI"* — false positives; there is **no `NOD` token at all.**
2. **Much of `FactionType` is dormant cross-title engine code.** Sibling events like `Currency_Wood_Stolen`, `Animal_Stolen`, `EpicConstructed`, Metagame-AI build orders, `Coordinator_Quick_Match` are from Petroglyph's *other* Mobius-engine titles — present in the shared lib, not wired up for RA.
3. **Our factions are ActLike-hijacked**, so even where the launcher *is* faction-aware it sees Allied/Soviet, not GDI/Nod. And the launcher's credit **tick** (`RAR_SFX_CASHUP1`) is a single global event; the mod silences it and the DLL fires its own.

**Consequence for the future genuine-houses arc:** even if we someday add real `HOUSE_GDI`/`HOUSE_NOD` engine houses, the launcher still won't gain GDI/Nod faction-audio slots (they don't exist in the binary), so faction UI/audio would *still* be DLL-emitter-routed. The launcher's `FactionType` table is a dead end for our purposes regardless.

---

## Select-all (`a`) and Deploy (`/`): the DLL owns both keys

The launcher classifies units for these two hotkeys by hardcoded identity, and no data reaches it:

- **Component model:** ClientG maps each exported object into native components (`ResourceHarvesterComponentClass`, `LocomotorComponentClass`, `SelectBaseComponentClass`, `StructureConstructionComponentClass`) through an `ExportBits.*` bitfield. The commands are `COMMAND_CNC_SELECT_ALL_ON_SCREEN` / `_IN_WORLD` and `COMMAND_CNC_DEPLOY_SELECTED_MCV`, dispatched by `RTSInputManagerClass`. The mapping from `CNCObjectStruct` fields to components is compiled in.
- **No data lever:** the only per-unit table in CONFIG.MEG, `RABUILDABLES.XML`, has three fields per entry (name, description, build icon) and no role, deployable or harvester field. `OBJECTSTATES.XML` defines state classes but never binds them to units. `CNCObjectStruct.CanDeploy` / `IsDeployable` are never populated by EA or by us, and select-all does not read `CanHarvest`.
- **Deploy:** `COMMAND_CNC_DEPLOY_SELECTED_MCV` self-clicks the selected unit only when its exported `AssetName` and `TypeName` are both exactly "MCV"; the art follows `AssetName`, so aliasing is no fix. Instead `TF_Deploy_Key_Tick` reads backslash (`VK_OEM_5`, the launcher's default deploy binding) with `GetAsyncKeyState`, which works because InstanceServerG and ClientG share one Wine/Windows session, and runs `TF_Self_Action_Selected`. Each selected object whose self-click answers `ACTION_SELF` acts on it: MCVs deploy, transports unload, minelayers lay, a selected group deploys together (`TF_DeployKeyBatch`), and a deployed Mobile War Factory packs up by this key only. A press counts once per house, because on the host it also arrives through the launcher's patched deploy command.
- **Select-all:** ClientG picks the objects and hands them over through `CNC_Clear_Object_Selection` + `CNC_Select_Object`, excluding only the stock HARV and MCV by interned name id (an object holding "HARV" at +0xaf8 and "MCV" at +0xafc). `TF_Select_All_Excludes` drops harvesters (`IsToHarvest`) and any `Is_MCV()` from that hand-over for 10 frames after an A press (read from the keyboard) or after mod command 2, which the patched launcher sends just before its own select-all. The drag-box select is DLL-routed and filtered in `should_exclude_from_selection` (`display.cpp`).
- In LAN games every player's deploy and select-all keys reach the host through the launcher-resident key patch ("The keys", below).

ClientG facts for next time: command ids deploy = `0x1020`, select-all-on-screen = `0x101b`
(name-registered at 0x14b1xxx); `CNC_Handle_*` strings are NOT in ClientG (InstanceServerG calls
the DLL; ClientG talks over IPC); gdb attaches but neither hardware watchpoints nor int3
breakpoints fired on this Wine process — `/proc/<pid>/mem` is the reliable probe.

### Superweapon targeted-vs-instant firing: launcher code, reachable by a runtime patch (2026-09-30)

**Question:** can a superweapon cameo act on a single left click with no targeting cursor (the
Firestorm's on/off, the Hunter Seeker's launch)? **Yes, on the host, by patching the launcher's
click handler in memory, in every player's launcher. No data lever exists.**

**The launcher's cameo left-click handler** (ClientG `0x73E950`; right click is `0x73EDF0`) reads
its own copy of each sidebar entry: `+0x18` BuildableType, `+0x1C` BuildableID, `+0x20` Type
(DllObjectTypeEnum), `+0x24` SuperWeaponType, `+0x44` Completed, `+0x45` Constructing, `+0x46`
ConstructionOnHold, `+0x47` Busy. It forks at `0x73EA39` on `Type == SPECIAL`:
- **SPECIAL, Completed:** plays "select target" and calls `0x1689200`, which stores the entry's
  type/id/name/SW type and sets the input-mode global `0x20F1C90` to 4 (targeting). Nothing is
  sent to the DLL until the map click (`SUPERWEAPON_REQUEST_PLACE_SUPER_WEAPON`) or the cancel
  (`SIDEBAR_CANCEL_PLACE -1,-1`).
- **SPECIAL, not Completed:** local sound only (or nothing). Nothing is sent.
- **Any other Type:** the build path, which sends `START_CONSTRUCTION` (or `_MULTI`) with the
  entry's BuildableType/ID at `0x73ECE9`.

`0x20F1C90` is the launcher's input mode (0 idle, 4 superweapon targeting, 5 building placement);
it is a static global, since ClientG loads at its fixed base `0x400000` and has no relocations.
The DLL can also start targeting itself: `CALLBACK_EVENT_SPECIAL_WEAPON_TARGETTING` lands in
`0x1689130` (the Chronosphere's second step uses it).

**The patch** (`TF_Patch_ClientG_Click_Specials`, dllinterface.cpp, applied at every match start,
idempotent, lives as long as the launcher process): the 12 bytes at the fork become a jump into
the zero-filled tail of ClientG's last code page (`0x1BE91A0`), where a few instructions redo the
original test and send the entries listed in `TF_ClickSpecials` (`RTTI_SPECIAL` plus the Firestorm's
and the Hunter Seeker's ids) to the build send in every state. Every other entry runs the original
code. Both spots are checked byte for byte first; a different launcher build is left alone. The
request arrives in `CNC_Handle_Sidebar_Request`. The cameo stays in the superweapon tab with its
normal clock and "Ready!". To add a superweapon, add it to `TF_ClickSpecials` and give it an order
in `Place_Special_Blast`.

**What the Deck probe established (2026-09-30), for any future data-only idea:**
- The tab is chosen by `Type` alone. `UNIT_TYPE` goes to the vehicle tab even with an `SW_` type
  set; `UNKNOWN` and `OBJECT` make the cameo vanish. SuperWeaponType, Busy, Fake and a non-special
  BuildableType under a SPECIAL Type change nothing about the tab or the left click.
- In the superweapon tab the RIGHT click always reaches the DLL: `HOLD` when idle, `CANCEL` when
  ready or on hold. `ConstructionOnHold` draws the shared "Hold" word.
- A non-special Type's left click reaches the DLL as `START_CONSTRUCTION`, but in its own tab.

**LAN:** the patch also goes in at each launcher's own startup load of the DLL, so a joiner's
launcher gets it too (see "Launcher-resident patches" below).

### Launcher-resident patches: LAN joiners get every launcher patch (2026-09-30)

Only the host simulates a LAN game, so everything the DLL
did to a launcher (crest, TD tab icons, era EVA lines, click specials) used to reach the host's
launcher only. **But ClientG loads the mod's DLL itself, briefly, at its own startup, on every
machine** (dev `tf_dll_load.log`: `attach ... ClientG.exe`, then `detach` a moment later). That
load is the way in:

- `DllMain` -> `TF_Patch_Launcher_At_Load` (only when the process is ClientG.exe) writes the
  click-special patch in-process, pins the DLL (`GetModuleHandleEx` PIN) and hooks the launcher's
  plugin event dispatcher (`IncomingExternalGamePluginEventClass::Execute` 0x783B60, at its type
  switch 0x783B82; the hook code sits at 0x1BE9240 beside the click patch).
- At match start, and 45 and 150 frames later, the host sends every human player a direct message
  `@@TFL:<GlyphX id, 16 hex>:<house>` (`TF_Tell_Launchers`). In the launcher a message event is
  type 6 with its text as a std::string at +0x180; the hook sets its kind (+0x19C) past the four
  the launcher shows, so it never reaches the screen, and compares the id with the launcher's own
  player id (cached by ClientG at 0x1FB6D48, flagged at 0x1FB6D40).
- For its own player the hook wakes a worker thread in that launcher, which runs the same
  functions the host runs (`TF_Mailbox_Write_EVA_Voice`, `TF_Patch_ClientG_Crest`, then
  `TF_Crest_Tick` at 15 ticks a second for three minutes), with the house from the message
  (`TF_Local_ActLike`). The heap scans stay off the launcher's thread.
- Verified 2026-09-30 in a LAN game (Deck host, desktop joiner, both TS GDI): the joiner's tab
  icons, crest and launcher-played EVA lines all follow its faction, and no message text shows.

**The keys** (`TF_Patch_Launcher_Keys_In`, same startup load): the launcher's tactical command
dispatcher (0x168A1B0, command number at `[cmd+0x24]`) jumps through a table at 0x168AD74 for
commands 0x1006 on. Deploy (0x1020, slot 10) now runs a stub that becomes mod command 1 and joins the
mod-command send (0x168ABDB), so every player's deploy key reaches the host's generic
`TF_Self_Action_Selected` (debounced per house: on the host the keyboard read fires too).
Select all on screen (0x101B, slot 8) and in world (0x101A, slot 7) first re-run the dispatcher on
the same command numbered as mod command 2 (0x1033), which latches that house's harvester and MCV
filter on the host (`TF_Select_All_Excludes`), then run the stock handler. Verified in LAN
2026-09-30. Still host-only: the dev cheats (they follow the host's local player).

Dead routes for a one-click super: reading the click from the screen (`GetAsyncKeyState` +
`GetCursorPos`), and reporting the super as an unfinished build item.

**Aiming is invisible to the sim.** With all 44 exports hooked (probe 2026-09-27), the traffic
while a superweapon is being aimed matched idle: the sim hears only
`SUPERWEAPON_REQUEST_PLACE_SUPER_WEAPON`, or `SIDEBAR_CANCEL_PLACE (-1,-1)` when targeting ends.
Anything that must know a player is aiming (an aiming-only range ring for the E.M. Pulse) reads
the input-mode global `0x20F1C90` from inside that player's launcher, through the startup-load
copy of the DLL. How a reading there reaches the sim's drawing is not worked out.

**Cameo art is independent of the click-detect mechanism and is normal AssetName wiring**: give
the super its own `RA_SW_<name>` entry in `RABUILDABLES.XML` with its own `BuildIcon`, and export
that AssetName from `Convert_Special_Weapon_Type` while keeping whatever real `SW_` enum value
gives the launcher plumbing you need (`SW_SONAR_PULSE` for the Hunter Seeker -- an ordinary
targeted-super slot in the tab; the special is never ready long enough for targeting to run). This
does not touch the real superweapon sharing that `SW_` enum value -- its own AssetName/cameo is
untouched, and its own effect is keyed on its own `SPC_*` case, not the enum value.

Verified end to end: a single click spawns the droid, which flies to the AI and wins, with no
crash. Testing traps: the pause menu freezes the poll in a headless run, the LAN lobby's Start is
disabled under a mod, and the instant-superweapon dev cheat masks the real recharge.

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

### Classic-mode toggle: locked out by launcher DATA

**`GAMECONSTANTS.XML` → `<CNCDisableLegacyGraphicsOption network="client"> True </...>`
removes classic graphics from the game.** EA added it as a mod option in 2020 ("Community-
requested Mod option so that players can't access legacy graphics"). Verified on the desktop:
the toggle is gone from the Options menu **and the spacebar no longer switches modes**.

It ships in `Data/XML/GameConstants_Mod.xml`, which ClientG merges over the base GameConstants
(additive, no same-size rule).

**This is the trichotomy in action, and a caution about how the section below reads.** Every
finding under it remains true — the *DLL* still cannot detect, suppress, or even observe the
classic toggle. But "the DLL can't" was allowed to harden into "a mod can't", and three
DLL-side routes plus a RAM probe were spent before anyone checked the launcher's own data for
a switch that had been sitting there since 2020. When a behaviour is launcher-owned, search
`CONFIG.MEG` **first**; `ClientG.exe` code is the only real lock.

### The DLL cannot detect classic mode at all

A mod cannot tell whether classic mode is on screen, let alone react to it.

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
revisit only if classic-mode detection is ever needed for something substantial. It is moot
while classic mode is locked out.
