# Player settings

**Status:** Design. Built, unreleased: `tf_settings.ini`, the GENERAL page (AUDIO and SIDEBAR) with sidebar sorting
and faction badges, and the GAMEPLAY page's TF AI switches and Classic AI. The controls and units switch sites come from reading
the source, unproven in play.
**Open:** a LAN game proving a joiner's sidebar choices reach the host; the LAN lobby line; the UNITS category;
the controls switches; the decisions at the end.

Every behaviour the mod changes from vanilla Red Alert, other than balance, becomes a switch on the TIBERIAN
FACTIONS SETTINGS page. Every switch is on by default, so a player who never opens the page plays the mod as it
ships; a player who prefers vanilla behaviour, the sidebar's arrival order among them, turns it off.

## The file

- `Documents/CnCRemastered/tf_settings.ini`, one section per group (`[Sidebar] SortByPrice=0`). It holds only the
  keys the player changed; a missing key is on.
- `tf_settings.cpp` reads a key with `GetPrivateProfileIntA` (anything but 0 is on) and writes one with
  `WritePrivateProfileStringA`, deleting a key set back to on. It shares the Documents path with `tf_music.ini`.
- Workshop updates never touch `Documents`, so the choices survive mod updates.
- **The DLL reads the file once, at match start** (`TF_Settings_Load`), and every site asks `tf_settings.h`.
  Pathfinding, the sidebar export and the AI run every frame and never read the file. A loaded save takes the
  file as it stands at load: the switches change behaviour, not stored state.

## LAN: sidebar per player, the rest from the host

Only the host runs the sim (`launcher-vs-dll-ownership.md`), and the host's DLL also builds every player's sidebar
export. What ClientG does on each machine stays that player's own: the radar crest, the sidebar tab icons and music.

- **Sidebar switches are each player's own.** When the host's `@@TFL` message reaches a launcher, it sends its
  player's sidebar switches as mod command 4 (x = `TF_SIDEBAR_CHOICE_MARK`, y = the bits), built and queued as the
  launcher's own mod-command send does. The host keeps them per house (`TF_Settings_Take_Sidebar`); a house with
  none yet, an older joiner's included, follows the host's file. A strip keeps vanilla's arrival order and the
  sidebar export orders each player's copy (`TF_Sidebar_Order`), so choices landing a few frames in apply at once.
  Proven in skirmish, where the host's own launcher sends them; a LAN joiner sending them is untested.
- **Sim switches follow the host's file**: controls, units and the AI. The GAMEPLAY page carries "In a LAN game the
  host's settings apply to every player.", and the LAN lobby is to carry "Gameplay settings follow the host." Where the lobby can carry it is open: a MasterText string on an existing
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
  the TF AI switches with every one off still leave our AI. The Classic AI switch below is the way back.

## The switches

| Page | Switch | Off means | Where | Size |
|---|---|---|---|---|
| Sidebar | Sorting: Cost / Vanilla | vanilla: a new cameo joins the end of its strip | `TF_Sidebar_Order`, `dllinterface.cpp` | built |
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
| AI | Fair fog | the AI sees the whole map and never scouts | `HouseClass::TF_Knows`, the hunt probe in `foot.cpp` | built |
| AI | Attack waves | vanilla's random hunts | `AI_Attack` runs `TF_Classic_AI_Attack` (`tf_ai_classic.cpp`) | built |
| AI | Naval | no ships, patrols or ferrying | `TF_Naval_Assessment` and `TF_Ferry_Assault` say no | built |

- **Fair fog and scouting are one switch.** Scouting exists because fair fog blinds the AI: with fog on and no
  scouting it never finds the enemy, and with fog off scouting has nothing to find. Off, every object counts as
  known (`TF_Knows`), so the waves' staging point and the naval coast check still find their targets.
- **Naval off** also stops the ferry: it needs the transports only a naval yard builds.
- **Base placement and sell logic are not switches.** They are bug fixes and support for our base builder (the
  naval and expansion-yard placement, the sell priorities of what it rebuilds), so Classic AI is their way back.
- The AI switches come from the host's file and hold for the match. The campaign keeps them all on
  (`TF_Settings_Load`), as the AI changes never reach it.

### Classic AI

The GAMEPLAY page's CLASSIC AI category holds the master switch, **TF AI** (the default) or **CLASSIC** (key
`TFAI=0`). With CLASSIC picked, TF AI's switches are off and read "Off with Classic AI".

- Classic AI is vanilla's decisions with only what it needs to play every faction. Vanilla's AI knows only RA's
  buildings; ours maps each to the faction's own (`TF_Skirmish_Pick` / `TF_Skirmish_Type`), and Classic keeps it.
- **The base builder** is vanilla's `AI_Building`, copied into `tf_ai_classic.cpp` (`TF_Classic_AI_Building`)
  with each RA building routed to the faction's own and counted with it (`TF_Classic_Count`).
- **Units, infantry, aircraft and ships** keep our pickers, which are vanilla's plus the mapping: with Classic
  picked they skip the economy hold and build one harvester a refinery, as vanilla did. Naval is off, so no ships.
- **Attacks** are vanilla's (`TF_Classic_AI_Attack`), and fair fog is off.
- **Selling** uses vanilla's urgencies (the Classic column of the `AI_Raise_Power` and `AI_Raise_Money` tables).
- **Difficulty** is vanilla's one for the match: every computer house gets `Rule.MaxIQ`
  (`TF_AI_IQ_From_Difficulty`), and the lobby's per-slot picks are not read.
- Stock RA's AI attacks sooner than ours (`todo.md`, the AI milestone), so Classic plays differently, and it is
  the baseline our AI is tuned against.
- Proven in skirmish against a Soviet and a Nod computer house: each built vanilla's order with its own buildings.

## The page

The Settings page (`scripts/bui_settings_build.py`, `Refresh_Settings` in `tf_launcher.cpp`) has three page tabs:
GENERAL, GAMEPLAY and GAME RULES. GAME RULES reads COMING SOON. Each page is a category list on the left (the code's
`SETTINGS_PAGE_INFO`) and the picked category's options on the right.

- **GENERAL:** AUDIO shows the faction tabs and that faction's music rows (`skirmish-music.md`); SIDEBAR shows its
  switches.
- **GAMEPLAY:** TF AI holds fair fog, attack waves and naval; CLASSIC AI the master switch; both over the LAN note.
  UNITS (A* pathfinding, chokepoint give-way, smart harvesters) joins the list with its slice.
- **A switch is one row:** its name, a line describing the picked choice, and two buttons in the page tabs' style,
  the picked one lit and the default on the left (COST / VANILLA, ON / OFF). A choice saves at once and takes
  effect from the next match.
- **DEFAULTS** resets the open category: every faction's music to MIX, or every switch on.
- A category holds at most four rows, so a group with more switches splits into categories. A switch's
  description fits about 26 characters before it runs under its buttons.
- The page is the CAMPAIGNS page's frame (`RA_MISSIONSELECT.BUI`) run by ClientG's SplashScreen, as the ADD-ONS
  screen is: its faction tabs stay, its era banners and campaign widgets are hidden, and Start becomes DEFAULTS.
  The builder's rects are pixels of a 1280x800 Deck screenshot.

## First slice

Sorting and faction badges, end to end: the INI, the struct, the SIDEBAR rows, each player's choices reaching the
host, and a LAN game with the host and a joiner set differently, each seeing their own sidebar. The other switches
follow the same pattern.

## Decisions

- The LAN lobby line's home: MasterText on an existing label, or a new widget.
- Whether attack-move and rally points get switches at all: off only blocks their keys.
- Smart harvesters as one switch or several.
