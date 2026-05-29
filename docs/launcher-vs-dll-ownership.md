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
| **Classic/remaster view toggle (spacebar)** | **Launcher** | **No** — DLL only gates *availability* | `Legacy_Render_Enabled` `dllinterface.cpp:8792`; no input enum |
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

## Diagnostic techniques that work here (reusable)

- **"Is this sound DLL- or launcher-driven?"** Drop an `fopen`-append log at the DLL call site; an *empty* file while the game runs proves the launcher owns it. (Used to prove the credit tick. Use `%USERPROFILE%` paths — `reference-diagnostic-paths`.)
- **"Does the launcher know about X?"** `strings -n N ClientG.exe | grep`. Demangled C++ symbols expose class/struct/enum names: `XMLTypeConverterClass<...>` shows exactly which XML→type conversions exist; `Faction_Event_GUI_SFX_*` enumerates the launcher's GUI-SFX vocabulary.
- **"What can cross the boundary?"** Read `dllinterface.h` — it is the complete contract, nothing else gets through.

---

## When a Ghidra dive WOULD be worth it

**Not now.** Source + strings answer every standing question, and the `FactionType` lead dead-ends on a negative a decompile would only re-confirm — at the cost of installing Ghidra and disassembling 34 MB of stripped, optimized native C++.

A decompile becomes worthwhile only if **both** hold: (a) we commit to genuine engine houses, **and** (b) we need the exact `House → FactionType/side` mapping logic — e.g., to learn whether new house slots could ever map to launcher faction/color/audio slots, or to extract the credit-counter animation parameters. Until then the value doesn't clear the cost.
