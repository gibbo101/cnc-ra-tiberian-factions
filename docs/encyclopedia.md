# The faction encyclopedia

**Status:** Design; shipped in 5.6.0 with the ADD-ONS screen.
**Open:** the manual lines flagged in `scripts/encyclopedia_work/descriptions.json`.

FACTION ENCYCLOPEDIA, under TIBERIAN FACTIONS ADD-ONS on the main menu, opens a tab per faction, the faction's units and structures
in a scrolling list, and the selected entry's in-game picture, description from the original manuals and stats read
live from the mod's rules. Addresses are ClientG.exe 1.153.745903.

## What the player sees

- The CAMPAIGNS page's frame (`campaigns-page.md`): its crest tabs under RED ALERT, TIBERIAN DAWN and TIBERIAN SUN
  banners, for Allies, Soviets, GDI, Nod and TS GDI.
- The list: ABOUT THE <FACTION> first (the faction's overview from its manual, its crest as the picture), then the
  groups INFANTRY, UNITS, AIRCRAFT, NAVAL and STRUCTURES as headings, each entry with its sidebar cameo and name,
  cheapest first. A group the faction has nothing in doesn't show.
- The selected entry: its name, its HD sprite in the faction's house colour (the cameo when it has no sprite), its
  description, what it needs on a line of its own, and its stats in the same green box: cost, strength, armour, speed (or power for a structure), sight, weapon, damage,
  range in cells, reload, a second weapon and seats (passengers). A weapon shows its readable name
  (`TEXT_TF_ENC_WEAPON_<INI>`, from the `weapons` table in `descriptions.json`), else its INI name.
- TS GDI without the Tiberian Sun HD Assets add-on loaded: GET TIBERIAN SUN HD ASSETS in place of the list, which
  opens the ADD-ONS screen with the pack selected (`pack-panel.md`).
- The README credits EA's original manuals for the descriptions.

## Live stats

ClientG only ever calls the DLL's `CNC_Version`; the game side (type heaps, rules, mix files) starts in
InstanceServerG. So `TF_Encyclopedia_Load` (`redalert/tf_encyclopedia.cpp`) builds the type heaps as `init.cpp`
does, then processes the mod's own rules from `<mod>\CCDATA\` with a `RawFileClass`, as a skirmish does:
`rules.ini` through `Rule.Process`, then `aftrmath.ini` and `mplayer.ini` as overrides (General, Recharge, AI,
Powerups, Land_Types, Themes, IQ, Objects, Difficulty). A second `Rule.Process` would rebuild the weapon and
warhead heaps under the types' pointers to them.

`mplayer.ini` ships loose in `CCDATA`, where the game's skirmish load finds it before `EXPAND2.MIX`: the stock
copy without its `[BRIK]` override, so walls cost `rules.ini`'s 100. The encyclopedia shows the same skirmish
values (GUN, TurretGun, GAP and TSLA differ from `rules.ini`). Scenario INIs and difficulty are not applied.

An entry is a buildable type whose `TF_Entry_Faction_Mask` (the sidebar badge mask, `function.h`) has the tab's
faction, whose tech level is 20 or less or that is a construction yard, and that has a sidebar XML entry. A
construction yard with no XML entry (TS GDI's) is named `TEXT_STRUCTURE_<INI>` from ModText, with the cameo of its
faction's MCV.

## Names, cameos and text

The DLL reads every `Data\XML\OBJECTS\UNITS\*BUILDABLES.XML` of the mod and of each loaded mod root (the asset
packs) for `RA_<INI>_0` (the badge-free variant), else `RA_<INI>`: its `ObjectNameTextID`, `ObjectDescriptionTextID`
and `BuildIcon`. ClientG's text table resolves the keys, ModText included.

The description is `TEXT_TF_ENC_<INI>`, else the game's one-liner (`ObjectDescriptionTextID`); the overview is
`TEXT_TF_ENC_ABOUT_<ALLIES|SOVIETS|GDI|NOD|TSGDI>`. Both come from `scripts/encyclopedia_work/descriptions.json`:
the manuals' text verbatim (cut at whole sentences to 370 characters), or, for a unit no manual has, a short entry
in their style (`"source": "tf"`). `scripts/encyclopedia_text.py` writes them between its markers in `ModText.csv`.
Text there has no double quotes, and `&` is written `&&` (the font reads a single `&` as a shortcut marker).

The description wraps at spaces into 7 lines beside the picture and 3 under it (`DESC_RIGHT_CHARS`,
`DESC_BELOW_CHARS` in `tf_launcher.cpp`).

## Adding or changing an entry

The list, names, cameos, stats and pictures follow the game's own data and art with no step. A new entry's
description needs one: add its text to `descriptions.json` (and any new weapon's name to its `weapons` table) and
run `scripts/encyclopedia_build.sh`. Until then it shows the game's one-liner and the weapon's INI name. The build
warns about what is missing from `scripts/encyclopedia_work/entries.tsv`, a copy of the dev build's
`Documents/CnCRemastered/tf_encyclopedia.log`, written when the encyclopedia opens: each faction's entries, their
art, body frame, house colour and layers.

## Pictures

The picture is drawn live from the game's sprite art when an entry is selected. `TF_Encyclopedia_Sprite`
(`redalert/tf_encyclopedia.cpp`) says how the game draws the type facing south-west, from its class data:

- a vehicle: its body frame (a walker's standing frame; the Limpet Drone's first crawl frame), and its turret at
  its seat (`Turret_Adjust`, as `UnitClass::Draw_It` draws it; a deploy-to-fire walker shows none while mobile);
- a ship: facing 12 of 32, with each turret overlay at its seat as `VesselClass::Draw_It` draws it;
- infantry: standing frame 3; aircraft: facing 12 of 32, a helicopter with its landed blades (`RROTOR`,
  `LROTOR`) as `AircraftClass::Draw_Rotors` seats them, the Chinook facing north as it lands (Draw_Rotors' spacing
  fits its hull only there);
- a structure: the last frame of its build-up (`<art>MAKE`), its stray dust specks dropped; a turreted one its
  frame facing south-west, the EMP Cannon with its cannon (`TSPULST`), a TS tower with its top, an Upgrade Centre
  plug on the Upgrade Centre.

`TF_Encyclopedia_Render` (`redalert/tf_encyclopedia_art.cpp`) finds each art's frames in the tileset XMLs of the
mod and the asset packs, then the game's RA and common ones in CONFIG.MEG (temperate first). A frame's folder is
the tileset's root plus the frame's own folders, as the launcher opens it, so `RA_VFX`'s empty root reaches TD's
art in the base game (`td-base-art.md`). The frame is read from that folder's ZIP, or as a loose whole-canvas DDS
in a folder of that name (`sprite-memory.md`): the packs', the mod's, else `TEXTURES_RA_SRGB.MEG`,
`TEXTURES_COMMON_SRGB.MEG` (the rotors) or `TEXTURES_TD_SRGB.MEG`. Each is placed by its `.meta` crop, layers are
seated at classic pixels x 128/24, and the house colour is applied before the result is fitted to 256x192.

House colour is the client's own team-colour rule (`CNCRATEAMCOLORS.XML`, `CNCTDTEAMCOLORS.XML` in CONFIG.MEG; the
maths is `TextureManager.cs` in the game's SOURCECODE map editor): in linear light, green with a hue between the
house's bounds takes its hue, saturation and value shift. Each faction is drawn as its campaign draws it: Allies as
Greece, Soviets as the USSR, GDI as TD's GOOD, Nod's structures, harvesters and MCVs as BAD_STRUCTURE (red; ClientG
names HARV and MCV beside the buildings) and its other units as BAD_UNIT (blue-grey).

The launcher only loads textures it indexed at startup, before it loads the DLL: a file written later, or a full
path, never loads. So the mod ships one blank canvas, `TF_ENC_LIVE.TGA` (256x192), and the DLL writes each picture
into its GPU texture:

| Step | Call |
|---|---|
| Point the picture at the canvas | `Quad_Set_Texture` `0xF604C0` |
| The canvas's texture handle | GUIManager `0xF301F0` (thiscall, name), as `Quad_Set_Texture` resolves it |
| The `ID3D11Texture2D` | the engine texture the handle points at, `+0x84` (`+0x80` is its shader view) |
| Write the pixels | `UpdateSubresource` on the device's immediate context, on the launcher's UI thread |

A picture that can't be drawn shows the cameo. The About row shows the faction's logo,
`TF_ENC_ABOUT_<FACTION>.TGA`, written with the canvas by `scripts/encyclopedia_logos.py`.

The list leaves out shared MCVs, and a shared factory (Construction Yard, War Factory, Helipad) wherever the faction
has its own factory building the same kind. `UNLISTED` (`tf_encyclopedia.cpp`) keeps a skirmish-only entry off a
faction's list: Tanya for the Soviets.

## The screen

`scripts/bui_encyclopedia_build.py` writes `TF_ENCY.BUI` from the CAMPAIGNS page with its class set to
`SplashScreen` (as the ADD-ONS screen, `pack-panel.md`), and `TF_ENC_ROW.BUI` from the mission row: the GDI frame
group on the plain `Mission_Select_ListElement` set, a cameo, a name and a heading. `scripts/encyclopedia_art.py`
paints the detail box, `TF_UI_ENC_STATS.DDS`, from the list box's rim and scanlines: one box over the page's
briefing box and the slot under it. `scripts/encyclopedia_build.sh`
runs them with `encyclopedia_logos.py` and `encyclopedia_text.py`.

The list is the page's own `MissionList_Box`; the sample entry names `TF_Enc_Row.bui`. Per row:

| Step | Call |
|---|---|
| Clear | `0xF6AF60` |
| Add a row, clear its `+0x71` | `0xF6A620` |
| Clone the sample into column `MissionColumn` (the list's only column; `Column0` gives no layout) | `0xF73CB0` |
| Show the cell, then its virtual `+0x6C` with 1 | vtable `+0x78`, `+0x6C` |
| Row widgets | the cell's own scene at `+0x1F4`, found with a `{0, scene}` owner |
| The row button takes no input, so the list gets the click | `0xF80BC0` |
| Click | event 4 on the cell, the row as the event's data |
| Select row 0 after filling | `0xF74EA0` |

The selected row's button is toggled on (`0xF80920`). A tab is the page's tab button, bound with its index as data.

## Menu

`scripts/bui_mainmenu_pack_notice.py` puts FACTION ENCYCLOPEDIA (`TF_Encyclopedia`) under TIBERIAN FACTIONS ADD-ONS,
REPLAY / OBSERVER in BONUS GALLERY's row, and moves the gallery's button and new-content badge off screen: the
launcher shows them again, and shrunk to nothing the badge stretched into view.
