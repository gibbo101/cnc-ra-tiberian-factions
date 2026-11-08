# Launcher vs DLL — the ownership map

**Status:** Reference. The launcher/DLL boundary map, as of 5.0.0.

The launcher/DLL boundary map: is a behaviour owned by the launcher (`ClientG.exe`) or by our
DLL, and can a mod reach it? Check here before assuming either way. Four levers reach
launcher-owned behaviour: CONFIG.MEG data, loose texture files, the sim's writes into ClientG
memory, and code patches from the DLL copy ClientG loads at startup.

Complements `building-sound-routing.md` (per-event audio) and `td-audio-routing-recipe.md`
(SFXEvent mechanics and EVA voices).

---

## The governing principle

The launcher is faction-blind, knows only what crosses the DLL interface, and needs a lever for anything it does by
itself: see the field manual's [What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#how-to-tell-who-owns-a-behaviour), How to tell who owns a behaviour.
TF keys every such choice on `ActLike` before it crosses: the radar, EVA, unit-voice and credit-tick routing.

**The data lever.** The launcher's data ships loose, in the mod's own `Data/CONFIG.MEG` or through `GameConstants_Mod.xml`: see the field manual's [Overriding the launcher's data](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#three-ways-in), Three ways in, and search the data before calling anything a code lock (What the launcher owns, Search in this order). TF's: `config-meg-mod-delivery.md`, `config-meg-lever-audit.md`.

**The image lever.** A loose atlas or texture overrides the launcher's 2D UI images, in the menus and in the match: see the field manual's [The UI atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#shipping-a-repainted-atlas), Shipping a repainted atlas. TF's: `ui-atlas-modding.md`.

**The RAM lever.** On the host, the sim's DLL opens ClientG (`TF_Open_ClientG`, `OpenProcess` + `ReadProcessMemory`/`WriteProcessMemory`) and rewrites its runtime state: the cached EVA sample blobs (`td-audio-routing-recipe.md`, "EVA lines the launcher plays") and the cached per-region UV records behind the radar crest and sidebar (`radar-crest-ram-spike.md`). It changes what an existing launcher-drawn element samples or plays, never layout. Probe with `scripts/clientg_region_probe.py`.

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
        │        │  loopback TCP :16000 — encrypted + HMAC'd (CryptoPP), fixed message set
        │        ▼
        └── InstanceServerG.exe   — the SIM server. On the hosting machine it loads our DLL
                                   (.../Mods/Red_Alert/Vanilla_RA/Data/RedAlert.dll) and runs the
                                   full CNC_Init/Advance_Instance/Get_Game_State/Handle_* interface.
                                   No rendering or UI code.
```

The sim runs in InstanceServerG, which loads the DLL on the hosting machine only (in LAN, only the host simulates). ClientG loads the DLL at startup on every machine; `DllMain` there (`TF_Patch_Launcher_At_Load`) patches launcher code and pins the DLL, and a worker thread woken by the host's `@@TFL:` message applies the faction patches for that machine's own player. On the host, the sim's DLL also patches ClientG across processes.

The socket, what crosses it and why a new kind of event from the DLL has nowhere to land (the receiver,
`IncomingExternalGamePluginEventClass::Execute`, is a compiled switch over the callback's types; Lua and ClickScript
are no way in either) are on the field manual's [What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#how-to-tell-who-owns-a-behaviour), How to tell who owns a behaviour.
Outbound, the DLL's callback lands in InstanceServerG's `GamePluginClass::Event_Callback`, which forwards it as
`SERVER_TO_CLIENT_EXTERNAL_GAME_PLUGIN_EVENT`; inbound, the server pulls the `CNC_Get_Game_State` structs (all three
names are strings in the executables). Launcher behaviour changes only through the four levers above.

---

## Binary facts (so we never re-investigate tooling)

- Native executables, and the map editor as the only .NET program: see the field manual's [What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#how-to-tell-who-owns-a-behaviour) (The tools). The details it lacks: `ClientG.exe` is 34 MB with no CLR imports (`mscoree`, `coreclr`, `hostfxr` all absent); the editor is .NET Framework 4.6.2 WinForms, and the `System.*`, `Newtonsoft.Json` and `Pfim` DLLs in `bin/` are its dependencies, not the launcher's.
- Engine identity from strings: `pgaudio` (`SFXEventManagerClass`, `SFXEventClass`), build paths `c:\buildsystem\...\mobius\qa\libs\pgaudio\...`.
- Native RE tooling on this machine: `objdump`, `strings` only (no Ghidra/rizin/wine). A *targeted* Ghidra dive is possible but currently unwarranted — see the last section.

---

## The interface contract

### Launcher → DLL: 33 `extern "C"` exports (`dllinterface.cpp:118-218`)

The game's 33 exports below, plus 11 `CNC_Editor_*` map-editor exports in `dllinterfaceeditor.cpp`: 44 in all, as in EA's DLL. There is no shutdown export.

| Group | Exports |
|---|---|
| Lifecycle | `CNC_Version`, `CNC_Init` *(registers the one callback)*, `CNC_Config`, `CNC_Add_Mod_Path` |
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
| Superweapon `$cost` line suppression | Launcher (its test is not found) | Not by data; a code patch is untried | see "Superweapon $cost line" below |
| **Superweapon targeted-vs-instant firing** | **Launcher** (compiled: the cameo left-click handler forks on the entry being a superweapon) | **Yes, by a runtime code patch of ClientG** (every player; see "Launcher-resident patches"). Data levers are dead; see below | `TF_Patch_ClientG_Click_Specials`; see below |
| Launcher-played EVA lines (mission won/lost, select target, low power, cannot deploy, battle control terminated, repairing, mission saved, building in progress) | Launcher (`Faction_Event_GUI_SFX_*`) | **Yes (shipped)**, by overwriting the cached samples at match start | `td-audio-routing-recipe.md`, "EVA lines the launcher plays" |
| Other launcher GUI stings | Launcher | No (Allied/Soviet only, see below) | strings |

---

### Sidebar build-tab icons: rewriting the prefix string

The tab icons are the one sidebar element the launcher names in code, so the TD scene swap left them RA's. The fix,
rewriting the four RA prefix strings in ClientG's image, is on the field manual's
[Rewriting launcher strings in memory](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/rewriting-launcher-strings.md#the-example-sidebar-tab-icons).
TF's is `TF_Patch_ClientG_Tab_Prefix`, called from `TF_Patch_ClientG_Crest` at match start for every side (TD's
prefix for TD-era players, RA's back for RA sides). It searches on every call, because the DLL instance doesn't
persist between matches.

**Two dead detours** (re-pointing the twelve tab records, and patching the atlas lookup table) are on the same page's
[Two routes that didn't work](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/rewriting-launcher-strings.md#two-routes-that-didnt-work). The lookup
table's entry, for the record: `{w,h,x,y}` as int32, the name pointer 68 bytes before the quad, a second `{w,h}`
copy 32 bytes before.

## The one new lead: the launcher's `FactionType` audio table — and why it can't help us

`strings ClientG.exe` revealed a **real per-faction audio system** in pgaudio: a `FactionType` enum and a family of `Faction_Event_GUI_SFX_*` events (`Credits_Start_Gain`, `ConstructionComplete`, `Low_Power`, `HQUnderAttack`, `InsufficientFunds`, …) parsed from XML via `XMLTypeConverterClass::Convert<enum FactionTableAudioTypeEnum, SFXEventClass>`. At first glance this looks like a launcher-side faction hook we could exploit. **It is not usable for GDI/Nod**, for three independent reasons:

1. **No GDI/Nod faction exists in the launcher.** The faction tokens beside the audio events are `ALLIED` / `SOVIET`. The `GDI` string hits are Windows **G**raphics **D**evice **I**nterface — *"render target is not compatible with GDI"* — false positives. `NOD` does appear, bare and in TD's own campaign front end (`_MUS_TD_NOD_MAP_THEME`, `CampaignSelect_NOD_Button`, `TEXT_NOD_CAMPAIGN`); which table the bare token belongs to is unchecked.
2. **Much of `FactionType` is dormant cross-title engine code.** Sibling events like `Currency_Wood_Stolen`, `Animal_Stolen`, `EpicConstructed`, Metagame-AI build orders, `Coordinator_Quick_Match` are from Petroglyph's *other* Mobius-engine titles — present in the shared lib, not wired up for RA.
3. **Our factions are ActLike-hijacked**, so even where the launcher *is* faction-aware it sees Allied/Soviet, not GDI/Nod. And the launcher's credit **tick** (`RAR_SFX_CASHUP1`) is a single global event; the mod silences it and the DLL fires its own.

**Consequence for the future genuine-houses arc:** even if we someday add real `HOUSE_GDI`/`HOUSE_NOD` engine houses, the launcher still won't gain GDI/Nod faction-audio slots (they don't exist in the binary), so faction UI/audio would *still* be DLL-emitter-routed. The launcher's `FactionType` table is a dead end for our purposes regardless.

---

## Select-all (`a`) and Deploy (`/`): the DLL owns both keys

The launcher classifies units for these two hotkeys by hardcoded identity, and no data reaches it:

- **Component model:** ClientG maps each exported object into native components (`ResourceHarvesterComponentClass`, `LocomotorComponentClass`, `SelectBaseComponentClass`, `StructureConstructionComponentClass`) through an `ExportBits.*` bitfield. The commands are `COMMAND_CNC_SELECT_ALL_ON_SCREEN` / `_IN_WORLD` and `COMMAND_CNC_DEPLOY_SELECTED_MCV`, dispatched by `RTSInputManagerClass`. The mapping from `CNCObjectStruct` fields to components is compiled in.
- **No data lever:** the only per-unit table in CONFIG.MEG, `RABUILDABLES.XML`, has three fields per entry (name, description, build icon) and no role, deployable or harvester field. `OBJECTSTATES.XML` defines state classes but never binds them to units. `CNCObjectStruct.CanDeploy` / `IsDeployable` are never populated by EA or by us, and select-all does not read `CanHarvest`.
- **Deploy:** `COMMAND_CNC_DEPLOY_SELECTED_MCV` self-clicks the selected unit only when its exported `AssetName` and `TypeName` are both exactly "MCV"; the art follows `AssetName`, so aliasing is no fix. Instead `TF_Deploy_Key_Tick` reads backslash (`VK_OEM_5`, the launcher's default deploy binding) with `GetAsyncKeyState`, which works because InstanceServerG and ClientG share one Wine/Windows session, and runs `TF_Self_Action_Selected`. Each selected object whose self-click answers `ACTION_SELF` acts on it: MCVs deploy, transports unload, minelayers lay, a selected group deploys together (`TF_DeployKeyBatch`), and a deployed Mobile War Factory packs up by this key only. A press counts once per house, because on the host it also arrives through the launcher's patched deploy command.
- **Camera to the yard (H):** `COMMAND_CNC_CAMERA_TO_CONSTRUCTION_YARD` (0x100B) looks for a building named `FACT` (ClientG holds `MCV`, `FACT` and `HARV` as one name table), so it finds no faction yard. Each player's launcher sends it as mod command 3 instead ("The keys", below), and `TF_Home_Camera` centres that player's camera on their next yard each press. `TF_Home_Key_Tick` also reads H from the keyboard when one human plays; the game loop runs as the lobby's first player, so in LAN the keyboard reads of H, the deploy key and A would act for that player and are off.
- **Select-all:** ClientG picks the objects and hands them over through `CNC_Clear_Object_Selection` + `CNC_Select_Object`, excluding only the stock HARV and MCV by interned name id (an object holding "HARV" at +0xaf8 and "MCV" at +0xafc). `TF_Select_All_Excludes` drops harvesters (`IsToHarvest`) and any `Is_MCV()` from that hand-over for 10 frames after an A press (read from the keyboard) or after mod command 2, which the patched launcher sends just before its own select-all. The drag-box select is DLL-routed and filtered in `should_exclude_from_selection` (`display.cpp`).
- In LAN games every player's deploy and select-all keys reach the host through the launcher-resident key patch ("The keys", below).

ClientG facts for next time: command ids deploy = `0x1020`, select-all-on-screen = `0x101b`
(name-registered at 0x14b1xxx); `CNC_Handle_*` strings are NOT in ClientG (InstanceServerG calls
the DLL; ClientG talks over IPC); gdb attaches but neither hardware watchpoints nor int3
breakpoints fired on this Wine process — `/proc/<pid>/mem` is the reliable probe.

### Superweapon targeted-vs-instant firing: launcher code, reachable by a runtime patch

**Question:** can a superweapon cameo act on a single left click with no targeting cursor (the
Firestorm's on/off, the Hunter Seeker's launch)? **Yes, on the host, by patching the launcher's
click handler in memory, in every player's launcher. No data lever exists.**

**The launcher's cameo click handler, the input-mode global and the patch** are on the field manual's
[Launcher key commands and superweapon clicks](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/launcher-key-commands-and-clicks.md#superweapon-cameos-one-click-no-cursor), Superweapon cameos. One detail it lacks: the build path can send
`START_CONSTRUCTION_MULTI` as well as `START_CONSTRUCTION`.

**TF's patch** is `TF_Patch_ClientG_Click_Specials` (dllinterface.cpp), applied at every match start, idempotent,
living as long as the launcher process. Its cave is at `0x1BE91A0`, and it sends the entries listed in
`TF_ClickSpecials` (`RTTI_SPECIAL` plus the Firestorm's and the Hunter Seeker's ids) to the build send. To add a
superweapon, add it to `TF_ClickSpecials` and give it an order in `Place_Special_Blast`.

**What the Deck probe established, for any future data-only idea:**
- The tab is chosen by `Type` alone. `UNIT_TYPE` goes to the vehicle tab even with an `SW_` type
  set; `UNKNOWN` and `OBJECT` make the cameo vanish. SuperWeaponType, Busy, Fake and a non-special
  BuildableType under a SPECIAL Type change nothing about the tab or the left click.
- In the superweapon tab the RIGHT click always reaches the DLL: `HOLD` when idle, `CANCEL` when
  ready or on hold. `ConstructionOnHold` draws the shared "Hold" word.
- A non-special Type's left click reaches the DLL as `START_CONSTRUCTION`, but in its own tab.

**LAN:** the patch also goes in at each launcher's own startup load of the DLL, so a joiner's
launcher gets it too (see "Launcher-resident patches" below).

### Launcher-resident patches: LAN joiners get every launcher patch

Only the host simulates a LAN game, so everything the DLL did to a launcher (crest, TD tab icons, era EVA lines,
click specials) used to reach the host's launcher only. The way round it (ClientG's own start-up load of the DLL,
pinning it, and a hidden message the hooked event dispatcher picks up for its own player) is on the field manual's
[Patching the launcher's code from your DLL](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/patching-the-launchers-code.md#telling-each-players-launcher-something), The way in, Keeping the DLL loaded and Telling each player's launcher something.

- `DllMain` -> `TF_Patch_Launcher_At_Load` (only when the process is ClientG.exe) writes the click-special patch
  in-process, pins the DLL and hooks the dispatcher; TF's hook code sits at `0x1BE9240`, beside the click patch.
- `TF_Tell_Launchers` sends each human player `@@TFL:<GlyphX id, 16 hex>:<house>` at match start and 45 and 150
  frames later.
- For its own player the hook wakes a worker thread in that launcher, which runs the same functions the host runs
  (`TF_Mailbox_Write_EVA_Voice`, `TF_Patch_ClientG_Crest`, then `TF_Crest_Tick` at 15 ticks a second for three
  minutes), with the house from the message (`TF_Local_ActLike`).
- Verified in a LAN game (Deck host, desktop joiner, both TS GDI): the joiner's tab icons, crest and
  launcher-played EVA lines all follow its faction, and no message text shows.

**The keys** (`TF_Patch_Launcher_Keys_In`, same startup load) re-route the deploy, camera-to-yard and select-all
commands to mod commands, as on the field manual's [Launcher key commands and superweapon clicks](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/launcher-key-commands-and-clicks.md#re-routing-a-key-to-a-mod-command), Re-routing a key to a mod command.
Mod command 1 (deploy) runs the host's `TF_Self_Action_Selected`, debounced per house since the host's keyboard read
fires too; mod command 3 (camera to yard) runs `TF_Home_Camera`; mod command 2 (`0x1033`), sent before the stock
select-all, latches that house's harvester and MCV filter (`TF_Select_All_Excludes`). Still host-only: the dev
cheats, which follow the host's local player.

Dead routes for a one-click super: reading the click from the screen (`GetAsyncKeyState` +
`GetCursorPos`), and reporting the super as an unfinished build item.

**Aiming is invisible to the sim** (all 44 exports hooked, the traffic while aiming matched idle), so anything that must know a player is aiming reads the launcher's input-mode
global from inside that launcher: see the field manual's [Launcher key commands and superweapon clicks](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/launcher-key-commands-and-clicks.md#superweapon-cameos-one-click-no-cursor). How a reading there
reaches the sim's drawing (an aiming-only range ring for the E.M. Pulse) is not worked out.

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

### `this == PlayerPtr` is always true inside HouseClass::AI
See the field manual's [Adding a faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/adding-a-faction.md#traps), Traps. TF's local-player test in
multiplayer is `DLLExportClass::CurrentLocalPlayerIndex` (`IsHuman` suffices in skirmish). Also: `ActiveBScan & STRUCTF_RADAR` / `Map.IsRadarActive`
oscillate 1/0 every frame (Recalc_Attributes quirk) — never edge-detect on the radar scan bit; count the Buildings
heap + `Power_Fraction()` and debounce.

### Superweapon $cost line
A new superweapon's cameo shows "Cost: $0" where the stock ones show no cost line, and the launcher's test for that
isn't found: see the field manual's [What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#the-walls-and-the-way-through) (the "Cost: $0" row).
TF sends the Ion Cannon as `SW_IonCannon` (enum `SW_ION_CANNON`), and its cameo shows $0; a cost set in
`CNCSidebarEntryStruct.Cost` for a superweapon changes nothing. Cosmetic, and no code patch has been tried.

### Roster-scaling CTD — NameOverride[25] table exhaustion
See the field manual's [Known engine traps](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/troubleshooting/known-engine-traps.md#about-25-named-types-fill-the-name-table), About 25 named types fill the name table. TF's fix,
all in the DLL: the tables grown from 25 to 256 (`globals.cpp`), a dedup by id in `TechnoTypeClass::Read_INI`,
`inline.h`'s `<` made `<=`, and a NULL guard on `OverrideDisplayName` in `dllinterface.cpp`.

### Classic-mode toggle: locked out by launcher data

One launcher constant removes classic graphics, menu option and spacebar alike: see the field manual's
[HD-only mods](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/getting-started/hd-only-mods.md#the-switch), The switch. EA added it in 2020, commented "Community-requested Mod
option so that players can't access legacy graphics". TF ships it in
`Data/XML/GameConstants_Mod.xml`. The DLL still cannot detect, suppress or observe the toggle (below); the lockout
is the data lever the field manual's [What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#search-in-this-order), Search in this order, puts first.

### The DLL cannot detect classic mode at all

A mod cannot tell whether classic mode is on screen, let alone react to it.

- **Refusing the page does not suppress the toggle.** Returning false from
  `CNC_Get_Visible_Page` makes the launcher switch to classic and render an empty
  viewport (HUD still drawn over it). The launcher decides toggle availability from its
  own lobby data and never consults us; EA simply implemented the same `num_humans < 2`
  rule independently on both sides, which is why it looks like one gate in MP.
- The page is requested every frame in both modes, and the spacebar never reaches the DLL: see the field
  manual's [HD-only mods](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/getting-started/hd-only-mods.md#porting-tds-classic-art-why-not-support-classic-mode-as-well), the last point under Porting TD's classic art.

**Consequence:** a notice shown only when the player enters classic mode is not
implementable from a mod. The available options are an unconditional match-start
message, or nothing. Anything drawn INTO the classic page is also map-positioned
(`view_port_width = Map.MapCellWidth * CELL_PIXEL_W`), so it scrolls with the terrain
rather than sitting on screen; launcher messages via `On_Message` are screen-fixed, but
`On_Message` only lands when issued from `CNC_Advance_Instance` after the player context
is set.

**RAM route also tried and abandoned.** ClientG's memory IS readable
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
