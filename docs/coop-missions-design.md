# Co-op missions — design & feasibility

**Status:** Design, not built. Research is complete; no code exists. Co-op skirmish works today.

Scripted co-op missions: a LAN skirmish on a map flagged co-op, with the DLL opening the
single-player win/lose and briefing gates for that map only. For example Player 1 = GDI, Player 2
= Allies, CPU = Soviets, with a pre-placed enemy base, triggered attack waves, a briefing and real
objectives.

**The launcher's own co-op campaign feature exists as code only and is not usable.** Worth knowing before anyone finds the traces and gets hopeful:

- `ClientG.exe` contains a compiled co-op campaign implementation — `CoopCampaignMenuImplementationClass`,
  `Button_CoopCampaign`, `CoOp_MissionDetails_Group`, `Faction5CoOpCampaign1Star..3Star`, and a
  hosting path `CoordinatorMultiplayerManagerClass::Host_Coop_Campaign_Lobby(ClientProgressiveCampaignMissionTypeClass*, ProgressiveCampaignDifficultyTypeEnum, ...)`
  with match-settings / player-ready / launch RPCs.
- `FACTIONS.XML` carries the matching data field, `<CoopCampaignType>`, as a sibling of
  `<CampaignType>` — **empty on all 11 factions.**
- **No co-op data ships.** `UI_CampaignMenu_CoOp` (the screen the menu class would load) is
  absent from our CONFIG.MEG *and* from the pristine base archive — zero members match "coop" in
  either. No co-op campaign is defined in `PROGRESSIVECAMPAIGNFILES.XML`.

So it is a cut feature: code without content.

**Can we finish it? No — three independent walls, and two are things already proven impossible:**

1. **The screen cannot be supplied.** `UI_CampaignMenu_CoOp` is not a member of either archive, and
   a mod cannot add a member. A loose `Data/ART/GUI/*.bui` overrides an archive member at any size (`campaigns-page.md`);
   whether ClientG opens a screen with no member is untested, and even if it did we
   would be authoring a whole ChunkFile scene graph to match what the compiled class expects.
2. **The entry point does not ship either.** The campaign menu that does ship
   (`UI_CAMPAIGNMENU.BUI`) contains no `Button_CoopCampaign` and no `CoOp_MissionDetails_Group`;
   those names live only in `ClientG.exe`. Widgets can be inserted (`bui-front-end-modding.md`),
   but whether ClientG wires an inserted button to the co-op class is unproven. There is no slash
   command that could host a co-op lobby directly (all 203 checked).
3. **It would launch the wrong thing anyway.** Hosting runs through EA's online coordinator, and
   mods load in LAN games only — so a working co-op button would start an *unmodded* match.

**And we do not need it.** Tier 2 below reaches the same gameplay through a LAN skirmish plus a
map flag plus opening the win/lose and briefing gates in our own DLL — entirely in code we
control. **This closes the "maybe there is a built-in co-op we can switch on" question.**

One encouraging signal, though not an actionable one: the hosting signature is
`Host_Coop_Campaign_Lobby(ClientProgressiveCampaignMissionTypeClass*, ...)` — a **campaign
mission launched through the multiplayer lobby path**. That is exactly Tier 2's shape, which
suggests the sim was expected to cope with a campaign scenario inside an MP session rather than
Path B fighting the engine's grain.

---

## 1. Two tiers — and why only Tier 2 is a feature

The engine already supports multiple factions + team alliances in one multiplayer game, so
two distinct experiences fall out:

### Tier 1 — Co-op skirmish (works today, zero code)
Two humans on the same lobby team vs an AI on a different team, on any custom MP map. Win =
last team standing (`MPlayer_Defeated`). **No DLL change, no scripting.** This is literally a
team skirmish — not worth special engineering. Caveat: factions are *lobby-picked*, not
map-forced (see §3).

### Tier 2 — Co-op scripted mission (the actual feature)
Same human/AI setup, but the `.mpr` carries a pre-placed enemy base, scripted attack teams
(Teamtypes + Triggers), a mission briefing, and **scripted objective** win/lose
(`TACTION_WIN` / `TACTION_LOSE` — "destroy the Soviet HQ", "survive 20 min", "your ally's
base must hold"). This is the "play a campaign mission with a friend" experience and is the
**only part that needs engine work** — because the scripted win/lose and briefing paths are
gated to single-player. Removing those gates (for co-op maps only) is "Path B".

---

## 2. How factions map to houses (the mechanism that makes 4-faction games possible)

The lobby picker's country slots carry the factions (`faction-select-identity.md`):

- **Spain → `HOUSE_GOOD` (GDI)** and **Greece → `HOUSE_BAD` (Nod)**, remapped on receipt in
  `CNC_Start_Instance`;
- **Germany = TS GDI** (`Is_TS_GDI`, no remap: the country house is the faction).

Then in `GlyphX_Assign_Houses` (`dllinterface.cpp`), **every MP player — human or AI — gets a
real house slot `HOUSE_MULTI1 + i`**, and their picked faction is written as that house's
**`ActLike`** via `Init_Data`. `ActLike` is the faction-identity lever:
it gates the buildable tech tree (`Owner=` lists), unit voices, radar SFX, classic-palette
remap — everything faction-specific keys off it. Alliances come from lobby **team IDs** —
same team → `Make_Ally`.

**Consequence:** GDI (`ActLike=HOUSE_GOOD`), Allied (`ActLike=HOUSE_GREECE`/`ENGLAND`/…), and
Soviet (`ActLike=HOUSE_USSR`) are just different `ActLike` values on Multi houses.
The engine already runs all five factions together in skirmish. A co-op mission is therefore not a new house system;
it's scripting + a small win/lose-in-MP patch on top of the existing faction plumbing.

---

## 3. Map discovery (RESOLVED — disk + editor-source evidence)

**Discovery directory (confirmed on the Deck):**
`Documents/CnCRemastered/Local_Custom_Maps/Red_Alert/` — holds 73 real `.mpr` maps.

Each map = a **triplet**:
- `<name>.mpr` — the full scenario INI (briefing, triggers, teams, houses, win/lose)
- `<name>.tga` — preview thumbnail
- `<name>.json` — launcher discovery manifest: `{MapTileX/Y/Width/Height, Theater, Waypoints[]}`

Two naming families coexist: local-authored short names (`RDS06.mpr`) and Workshop-synced
(`UGC_<itemid>_<hash>_MAPDATA.MPR`; RA's meta suffix is `MAPDATA`, per editor source
`GameInfoRedAlert.cs:364`). `Custom_Maps/` + `Custom_Map_Previews/` also exist (Workshop
cache). The dev-machine prefix has the dirs but they're empty (game never ran there).

**The `.json` has no "co-op"/category field** — the lobby list is built from geometry +
`Waypoints[]` (= start positions / max players; RDS01=8, a sample UGC map=4). So co-op-ness is
NOT discovery metadata; it lives in the `.mpr` content + our gate-patch.

**DLL entry point:** `CNC_Start_Custom_Instance` (`dllinterface.cpp`) receives
`directory_path` + `scenario_name` from the launcher, does `snprintf("%s%s.mpr", …)`, loads
via `CCFileClass`, and **already parses the file as an INI** (`ini.Load`, reads `[Basic]
Name` + `[Digest]`). The directory choice is launcher-owned (closed `ClientG.exe`), but the
on-disk evidence pins it to `Local_Custom_Maps/Red_Alert/`.

**Distribution:** co-op maps can ship inside the mod. The DLL copies the mod's `CustomMaps/`
triplets into `Local_Custom_Maps/Red_Alert/` itself (the TD map pack shipped this way before it was parked;
the `CustomMaps\\*` scan in `dllinterface.cpp`), and an official map can be replaced by name
from the mod's `CCDATA/` (`official-map-hybrids.md`). Workshop publishing from the editor stays
an option.

**Faction-forcing caveat:** factions are lobby-picked, not map-forced. The `.mpr` sets
positions, alliances, and the scripted enemy house, but it can't cleanly force a human to be
GDI vs Allied — the GlyphX house-assignment overrides `House` from the picker. So "P1=GDI,
P2=Allies" is a lobby convention (players pick those slots), and the scripted Soviet enemy is
authored into the map. The safe enemy implementation is a **Multi-slot AI house** with
`ActLike=HOUSE_USSR` (triggers target `HOUSE_MULTI3` etc.) rather than a pre-placed non-Multi
`HOUSE_USSR`/"BadGuy" house — whether a non-Multi scenario house activates in MP is the one
open empirical question (§6).

---

## 4. Authoring

The workspace's native Linux editor (`cnc-map-editor/`, mod-aware through the mod's
`mapeditor.json`) or `reference/MobiusMapEditor`. The latter is Nyerguds' actively-maintained fork of EA's open-source `CnCTDRAMapEditor` — same EA-source→improved-fork lineage
as our DLL↔Vanilla-Conquer. (We also have EA stock in the game install `SOURCECODE/` and two
local checkouts: `~/Documents/development/CnC_Remastered_Collection` (EA) and `.../EMC_Workshop`
(JohnnyJigglez EMC fork).)

Relevant capabilities (from its source + MANUAL):
- SP/MP toggle = **`BasicSection.SoloMission`** → `[Basic] SoloMission=`. Validation:
  `!SoloMission && numWaypoints<2` → error (MP needs ≥2 starts); `SoloMission && no Home
  waypoint` → error.
- **Co-op map shape = `SoloMission=false`** (surfaces in LAN lobby, 2+ human starts) **+
  hand-authored Teamtypes/Triggers** (the editor writes triggers into *any* map).
- The MANUAL caveat — *"scripting is mostly a singleplayer thing, severely limited in
  multiplayer"* — describes the **engine's** MP win/lose gates (exactly the 4 we patch), NOT
  an editor limitation on writing the triggers.
- Editor auto-writes the `.json`+`.tga` meta files for MP maps (unless ClassicFiles mode,
  `ClassicProducesNoMetaFiles`). Built-in Steam Workshop publish (`SteamworksUGC.cs`), needs
  the Remaster installed. WinForms .NET — runs via Proton/Wine, or v1.5.0.0+ "Classic mode"
  without the Remaster.

---

## 5. Path B — the win/lose-in-MP patch (the 4 gates)

The four gates, with line numbers as of 5.0.0:

**Win/lose (the essential pair) — `house.cpp`:**
- `HouseClass::AI`, `house.cpp:2283` — `if (Session.Type == GAME_NORMAL && IsToWin && BorrowedTime == 0 && Blockage <= 0)` → sets `PlayerWins`/`PlayerLoses`
- `HouseClass::AI`, `house.cpp:2295` — `if (Session.Type == GAME_NORMAL && IsToLose && BorrowedTime == 0)` → sets `PlayerLoses`/`PlayerWins`

**Briefing (nice-to-have) — `scenario.cpp`:**
- `Start_Scenario`, `scenario.cpp:522` — `if (Session.Type != GAME_NORMAL) briefing = false;`
- `Start_Scenario`, `scenario.cpp:592` — `if (Session.Type == GAME_NORMAL && Scen.BriefMovie == VQ_NONE) Display_Briefing_Text_GlyphX();`
- `Start_Scenario`, `scenario.cpp:600` — text/movie availability fallback, same SP gate

**Key observation:** each gate is **already self-gating on map content.** Win/lose only fire
if the map carries `TACTION_WIN`/`LOSE` triggers (`IsToWin` stays false otherwise); the
briefing text only shows if the map has briefing text. So relaxing them is *fairly* safe even
unconditionally — but "fairly" is why we want a discriminator (§7).

The backstop is preserved either way: `IsDefeated` / `MPlayer_Defeated` (called from
`HouseClass::AI`) remains the last-team-standing safety net if a mission's scripted win never
fires.

---

## 6. Discriminator decision — how the engine tells "co-op mission" from "skirmish"

All three options below share one fact: `CNC_Start_Custom_Instance` already has the `.mpr`
open as an INI, so reading a map flag is free, and it's the single entry point co-op maps come
through.

### Option 1 — Map flag in the `.mpr` *(RECOMMENDED)*
Read e.g. `ini.Get_Bool("Basic", "CoopMission", false)` in `CNC_Start_Custom_Instance`; store
on **`Scen.IsCoopMission`** (new `ScenarioClass` field — `Scen` is wiped by `Clear_Scenario`
each load, so no state leak into the next skirmish). Gates become
`(Session.Type == GAME_NORMAL || Scen.IsCoopMission)`.
- **Pros:** opt-in → **zero blast radius** (flag absent = byte-identical to today for every
  existing map, ours and Workshop's); data-driven (co-op-ness travels with the map); self-
  contained in the DLL; migration-friendly (can be promoted to drive Option 3 later).
- **Cons:** Mobius has no "co-op" checkbox → the key is added by hand / post-process (one
  `[Basic]` line). Must verify the `Clear_Scenario` reset path actually runs between an MP
  game and the next.
- **Cost:** ~6 lines (4 gates + read + field).

### Option 2 — Relax the gates for all MP
Flip the 4 gates to `(== GAME_NORMAL || == GAME_GLYPHX_MULTIPLAYER)`. No flag, no new state.
- **Pros:** simplest; no per-map authoring step.
- **Cons:** changes behavior for **every** MP game, including the hundreds of Workshop maps we
  don't own. Self-gating on map content makes it low-probability, but a competitive map with a
  stray win trigger or leftover briefing text would silently change behavior → an
  unreproducible bug report. "Probably fine," not "fine by construction."
- **Cost:** ~6 lines, but uncontrolled surface.

### Option 3 — New `GAME_GLYPHX_COOP` Session.Type
Add a session-type value; set it ourselves in `CNC_Start_Custom_Instance` **based on a map
flag** (so it *contains* Option 1). Then audit every `Session.Type` check — ~20 in `house.cpp`
alone, dozens across `scenario.cpp`/`display.cpp`/`sidebar.cpp`/scoring — to decide whether
COOP matches the MP (networking) or NORMAL (scripting) branch.
- **Pros:** semantically cleanest; obvious home for future co-op-specific behavior.
- **Cons:** by far most invasive; **missing one check = a subtle mode-specific bug**
  (networking doesn't engage, score screen miscounts, …); still needs the map flag anyway;
  harder to revert.
- **Cost:** many sites, audit-driven.

### Verdict

| Option | Risk to existing maps | Lines | Authoring cost | Future-proof |
|---|---|---|---|---|
| **1 — map flag** | none (opt-in) | ~6 | 1 INI key/map | promotes to #3 |
| **2 — relax gates** | low but uncontrolled | ~6 | none | dead-end |
| **3 — new type** | high (audit-driven) | many | 1 INI key/map | n/a (is the ceiling) |

**Option 1** — same line-count as the "simple" option but risk-free by construction,
data-driven, and a clean stepping stone to Option 3 if co-op ever outgrows these 4 gates.

---

## 7. Open items (next phase, when code work starts)

1. **Empirical: scripted enemy house in MP.** Confirm whether a pre-placed non-Multi house
   (`HOUSE_USSR`/"BadGuy") activates in an MP session, or whether the Soviet enemy must be a
   Multi-slot AI house (`HOUSE_MULTI3`, triggers target it). Multi-slot is the safe bet.
2. **Empirical: LAN smoke test.** Author a minimal `SoloMission=false` map with one scripted
   win trigger (e.g. timed or destroy-target), apply the chosen discriminator + win/lose
   patch, host a 2-human LAN game on the Deck, confirm the scripted win fires (vs falling back
   to last-team-standing). Two humans needed.
3. **First milestone proposal:** Option-1 flag + the two `house.cpp` win/lose gates + a trivial
   test `.mpr` → smoke test. Defer briefing gates + real mission design until that proves out.
4. **TD story NPCs available for mission scripting.** TD's `InfantryType` enum includes three
   scripted story characters — **Dr. Moebius** (`INFANTRY_MOEBIUS`), **Agent "Delphi"**
   (`INFANTRY_DELPHI`), **Dr. Chan** (`INFANTRY_CHAN`) — deliberately out of scope for the
   buildable faction roster (not faction-buildable, no sidebar entry), but they're ready-made
   **escort / rescue / capture / VIP mission objectives** if a GDI/Nod campaign is authored.
   They'd port like any TD infantry (sprite bundle via `bundle_unit.py` + an `idata.cpp` ctor)
   but be **placed via the Mobius editor (§4), not built**. TD assets exist in the MEG; not yet
   ported. Their voices/cameos would only matter if a mission surfaces them in the UI.

---

## Cross-references
- `campaign-tabs-research.md` — Mission Select and the front-end campaign display (a different
  lever: CONFIG.MEG front-end data; co-op maps are `Local_Custom_Maps` + DLL).
- `launcher-vs-dll-ownership.md` — the launcher/DLL boundary map.
