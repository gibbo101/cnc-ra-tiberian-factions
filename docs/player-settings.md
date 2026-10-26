# Player settings

**Status:** Design. Built, unreleased: `tf_settings.ini`, the GENERAL page (AUDIO and SIDEBAR), sidebar sorting and
faction badges in skirmish. The other switch sites come from reading the source, unproven in play.
**Open:** each player's sidebar choices reaching the host in LAN; the AI page and its lobby line; Classic AI; the
decisions at the end.

Every behaviour the mod changes from vanilla Red Alert, other than balance, becomes a switch on the TIBERIAN
FACTIONS SETTINGS page. Every switch is on by default, so a player who never opens the page plays the mod as it
ships; a player who prefers vanilla behaviour, the sidebar's arrival order among them, turns it off.

## The file

- `Documents/CnCRemastered/tf_settings.ini`, one section per group (`[Sidebar] SortByPrice=0`). It holds only the
  keys the player changed; a missing key is on.
- `tf_settings.cpp` reads a key with `GetPrivateProfileIntA` (anything but 0 is on) and writes one with
  `WritePrivateProfileStringA`, deleting a key set back to on. It shares the Documents path with `tf_music.ini`.
- Workshop updates never touch `Documents`, so the choices survive mod updates.
- **The DLL reads the file once, at match start,** into one `TF_Settings` struct, and every site tests a member.
  Pathfinding, the sidebar export and the AI run every frame and never read the file. A loaded save takes the
  file as it stands at load: the switches change behaviour, not stored state.

## LAN: sidebar per player, the rest from the host

Only the host runs the sim (`launcher-vs-dll-ownership.md`), and the host's DLL also builds every player's sidebar
export. What ClientG does on each machine stays that player's own: the radar crest, the sidebar tab icons and music.

- **Sidebar switches are each player's own.** The host needs every joiner's choices: each launcher sends its
  player's sidebar switches to the host as a mod command at match start (the route the deploy and select-all keys
  take), and the host keeps them per house, re-sorting that house's strips if they land after its first cameos.
  Sending a mod command with no key press behind it is unproven. Until it works, the host's choices apply to all.
- **Sim switches follow the host's file**: controls, units and the AI. The AI page and the LAN lobby carry
  "Gameplay settings follow the host." Where the lobby can carry it is open: a MasterText string on an existing
  label (`scripts/loc_work/mastertext.edits.txt`), or a BUI text widget (`bui-front-end-modding.md`).
- **At match start** the host names its non-default sim switches to each human player in a direct message, as
  `game-rules.md` plans for custom values.
- Not planned: a lobby page where the players pick the switches together. The host's file covers it.

## Not switches

- **Bug fixes stay on, as balance does:** a refinery takes docking only from its own customer, a stale refinery
  booking is dropped, and a cameo leaves the sidebar when its prerequisite goes (the `Who_Can_Build_Me` check in
  `sidebarglyphx.cpp`, which closes a build exploit).
- **Content stays on:** any faction's harvester docks at any refinery; the faction EVA, voices and build sounds.
- **The AI's anti-air response** is vanilla Red Alert's (`HouseClass::AI_Building`: build AA when an enemy has
  aircraft). Ours only teaches it the GDI, Nod and TS SAMs and radars, so it has no switch.
- **The AI's build order, unit picks and economy gate** replaced vanilla's code rather than branching from it, so
  the AI page's switches with every one off still leave our AI. The Classic AI switch below is the way back.

## The switches

| Page | Switch | Off means | Where | Size |
|---|---|---|---|---|
| Sidebar | Sorting: Cost / Vanilla | vanilla: a new cameo joins the end of its strip | `TF_Sidebar_Sort_Key`, `sidebarglyphx.cpp` | built |
| Sidebar | Faction badges | plain cameos | `TF_Apply_Cameo_Badge` and `TF_Apply_Special_Badge`, `dllinterface.cpp` | built |
| Sidebar | Faction crest and tab icons (per machine) | RA's crest and icons | `TF_Patch_ClientG_Crest`, `TF_Patch_ClientG_Tab_Prefix` | small |
| Controls | Select-all skips harvesters and MCVs | vanilla select-all | `dllinterface.cpp` | small |
| Controls | Band-select skips MCVs | harvesters only, as vanilla | `display.cpp` | one branch |
| Controls | Group moves spread infantry | vanilla's shared cells | `display.cpp` | one branch |
| Controls | Attack-move | the keys do nothing | the event's input, `techno.cpp` and `event.cpp`; the order itself is spread over about 40 sites and stays | small |
| Controls | Rally points | no rally point | the input in `building.cpp` | small |
| Controls | Wall line-fill | one wall a placement | `house.cpp` | one branch |
| Units | Smarter pathfinding (A*) | vanilla's edge follower | `Find_Path_AStar`, `findpath.cpp` | one branch; give-way and claims assume A*, so they turn off with it |
| Units | Give way at chokepoints | no give-way or corridor claims | `drive.cpp`, `findpath.cpp`, `CellClass` claims | about five sites |
| Units | Give up on unreachable moves | units retry forever | `TF_Path_No_Progress`, `foot.cpp`, `drive.cpp`, `infantry.cpp` | about five sites |
| Units | Infantry avoid Tiberium | infantry walk straight through | the A* cost, `findpath.cpp` | one branch |
| Units | Smart harvesters | vanilla's refinery choice and waits | `Find_Best_Refinery`, queue-jump, full-load return, field blacklist, anti-stuck watchdog (`unit.cpp`, `building.cpp`) | medium; one switch for the set |
| Units | Smarter repair bay | vanilla's queue and exit | `unit.cpp`, `building.cpp` | medium |
| Units | SAMs retarget before lowering | vanilla's lower-then-raise | `building.cpp` | small |
| AI | Fair fog | the AI sees the whole map | `techno.cpp`, `house.cpp` | about five sites |
| AI | Scouting | no probing of start locations | `foot.cpp`, `house.cpp` | small |
| AI | Staged waves and home guard | units sent as built | `TF_Wave_AI`, `TF_Wave_Dials`, `house.cpp` | medium |
| AI | Naval | no patrols, massing or ferrying | `house.cpp`, `vessel.cpp` | medium |
| AI | Base placement | vanilla's placement | `house.cpp` | medium |
| AI | Sell logic | vanilla's selling | `house.cpp` | small |

AI switches apply where the AI changes do: skirmish and LAN, never the campaign.

### Classic AI

The AI page's master switch: **TF AI** (the default, the AI switches shown) or **Classic AI** (the AI switches
greyed out and off).

- Classic AI is vanilla's decisions with only what it needs to play every faction. Vanilla's AI knows only RA's
  buildings; ours maps each to the faction's own (`TF_Skirmish_Pick` / `TF_Skirmish_Type`, 36 sites in
  `house.cpp`), and Classic keeps that mapping.
- Vanilla's five choice functions, `AI_Building`, `AI_Unit`, `AI_Infantry`, `AI_Aircraft` and `AI_Vessel` (831
  lines in Vanilla Conquer against 1,334 in ours), go into `tf_ai_classic.cpp` with the mapping, behind one
  branch at the top of each. A vanilla branch inside every TF block of today's functions would be far messier.
- Classic AI keeps vanilla's one difficulty: `Assign_Handicap(Scen.Difficulty)` gives every house the match's
  stat biases (`Rule.Diff[]`), and the lobby's per-slot picks and our IQ tiers are not read.
- Stock RA's AI attacks sooner than ours (`todo.md`, the AI milestone), so Classic plays differently, and it is
  the baseline our AI is tuned against.

## The page

The Settings page (`scripts/bui_settings_build.py`, `Refresh_Settings` in `tf_launcher.cpp`) has three page tabs:
GENERAL, AI and GAME RULES. The last two read COMING SOON until their switches land.

- **GENERAL:** a category list on the left, AUDIO and SIDEBAR, and the picked category's options on the right.
  AUDIO shows the faction tabs and that faction's music rows (`skirmish-music.md`); SIDEBAR shows its switches.
- **A switch is one row:** its name, a line describing the picked choice, and two buttons in the page tabs' style,
  the picked one lit and the default on the left (COST / VANILLA, ON / OFF). A choice saves at once and takes
  effect from the next match.
- **DEFAULTS** resets the open category: every faction's music to MIX, or every switch on.
- A category holds at most four rows, so a group with more switches splits into categories.

## First slice

Sorting and faction badges, end to end: the INI, the struct, the SIDEBAR rows, each player's choices reaching the
host, and a LAN game with the host and a joiner set differently, each seeing their own sidebar. The other switches
follow the same pattern.

## Decisions

- The LAN lobby line's home: MasterText on an existing label, or a new widget.
- Whether attack-move and rally points get switches at all: off only blocks their keys.
- Smart harvesters as one switch or several.
