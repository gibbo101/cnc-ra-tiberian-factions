# Game rules editor

**Status:** Design. Nothing ships; the engine route and the value limits come from reading the source, unproven in play.
**Open:** the one-value `tf_rules.ini` skirmish check; the number-entry widget probe; the decisions at the end.

Players change each faction's unit values and a short list of match rules from inside the game,
with no INI editing. No other Remastered mod reaches the front end for this: the mods that offer
options ship hand-edited INIs in `CCDATA`, which a Workshop update overwrites.

## Player files

- `Documents/CnCRemastered/tf_rules.ini` holds the player's custom values, in `rules.ini` form
  (`[MTNK] Cost=900`, `[90mm] Damage=35`). It only ever holds keys the player changed.
- `Documents/CnCRemastered/tf_rules_mode.ini` holds `Mode=DEFAULT|CUSTOM`. DEFAULT ignores
  `tf_rules.ini` but keeps it, so switching back restores the custom values.
- Reset to defaults clears one object's keys, or the whole file.
- Workshop updates never touch `Documents`, so custom values survive mod updates.

## Engine route

- **Skirmish and LAN only.** Campaign missions keep their own balance.
- **Where:** in `Read_Scenario` (`redalert/scenario.cpp`), after the `MPLAYER.INI` pass and before
  `Fill_In_Data`. The order of a skirmish load is `rules.ini`, `aftrmath.ini`, the map INI, then
  `MPLAYER.INI`; a pass before `MPLAYER.INI` would lose the keys it sets (`[BRIK]` among them).
- **How:** the same `Rule.General` ... `Rule.Difficulty` passes the map INI gets, on a `CCINIClass`
  loaded with a `RawFileClass` on the full path (the `tf_ai_difficulty.txt` pattern).
- **Heaps:** every weapon, warhead and bullet object is created once at startup
  (`Heap_Maximums`). Name lookups in a later pass only search, so a player file never grows a heap.
- **Save games:** the type tables are not saved. Loading re-reads `rules.ini`, `aftrmath.ini`, the
  scenario INI and, for network loads, `MPLAYER.INI` (`redalert/saveload.cpp`), so the player pass
  goes there too. A save must load with the values it was played with, or saved units' strength no
  longer matches the type's maximum. Proposed: the save stores a copy of the player block.
- **LAN:** only the host simulates (`lobby-difficulty-ram-spike.md`), so the host's file is the
  match's rules and nothing needs syncing.

## Telling the other players

At match start the host sends each human player a direct message through `On_Message`, as
`TF_Tell_Launchers` does for the faction (`launcher-vs-dll-ownership.md`): a visible line naming
the mode and the edited objects. A hidden `@@TFR:` message plus the joiner-side worker is the
richer form, for a styled line. Neither reaches the lobby: the sim starts at match start.

## What a player may edit

Every unit, infantry, vessel, aircraft and building reads through `TechnoTypeClass::Read_INI`, and
each key defaults to its current value, so a file changes only the keys it names.

| Kind | Keys | Limits |
|---|---|---|
| All | `Cost`, `Strength`, `Armor` (a picker), `Sight` | Strength 10 to 32767 (repair cost divides by it; object strength is a `short`); Sight 1 to 10 (`Sight_From` reveals nothing above 10) |
| Moving | `Speed`, `ROT` | |
| Aircraft | `Ammo` | |
| Buildings | `Power` | the sign stays: a drain edited positive keeps the old drain |
| Weapons | `Damage`, `ROF`, `Range`, `Burst`; `AmbientDamage` for the railgun, Disruptor and prism weapons | ROF and projectile Speed at least 1 (division) |
| Warheads (advanced) | `Verses`, `Spread` | Verses needs all five values; a missing one reads 0% |

Never exposed: `Primary`, `Secondary`, `Warhead`, `Projectile` (a bad name silently removes the
weapon), `Owner`, `TechLevel`, `Prerequisite`, `DoubleOwned`, `Image`, `Name`, footprint and art
keys, and the movement-type flags.

## Traps

- **TD buildings double on every pass.** `BuildingTypeClass::Read_INI` doubles `Strength` and adds
  3 to `Sight` for every `TD*` section it reads. A player `Strength=800` gives 1600, and a section
  with no `Strength` key doubles the already-doubled value. The doubling moves to the `rules.ini`
  pass only, or the editor writes half the shown value; limits for TD buildings halve (Strength
  16383, Sight 7).
- **Keys leak between matches.** No pass restores the constructor defaults: a key the player file
  sets that `rules.ini`, `aftrmath.ini` and the map don't set keeps its value into the next match and
  the campaign. Core keys are set everywhere; `Secondary`, `Ammo`, infantry `ROT`, `GuardRange` and
  `Burst` on 72 weapons are not. Proposed: the editor writes only keys `rules.ini` already sets, so
  every match's base passes reset them; a snapshot of the type tables is the fallback.
- **Shared weapons and warheads.** 22 of the 96 weapons in use belong to more than one type
  (`DepthCharge` 5, `Pistol` 4, `TDM60mg` on the APC, Hum-vee and Buggy); warhead `AP` serves 21
  weapons. Weapons are edited as weapons, and the editor names every unit that fires one.
- **Values code owns.** The Ion Cannon's damage is fixed in `anim.cpp`; TD-port weapons wait 9
  frames before a salvo's first shot whatever `ROF` says, and read projectile `Speed` raw (0-255);
  a refinery's price and GDI and Nod build times subtract the harvester's `Cost`. The editor shows
  these as fixed or explains the coupling.

## Match rules

Existing `[General]` and `[Recharge]` keys, no new code: `BuildSpeed`, `RefundPercent`,
`RepairPercent`, `GoldValue`, `GemValue`, `SurvivorRate`, `ShroudRate`, `ChronoDuration`,
`IronCurtain`, `AtomDamage`, the crate keys and the superweapon recharge times. Lobby settings
(credits, Tiberium growth, crates on or off) stay in the lobby.

New DLL features, each its own job: bounty (credits for kills), friendly fire off, AI personality
per match (balanced, tank rush, air, naval, turtle).

## The screen

The editor lives in the Faction Encyclopedia: the same faction tabs, grouped list and live stats,
which the encyclopedia already reads from the mod's rules inside ClientG. The custom layer applies
there too, so the shown values are the ones the next match uses.

- A DEFAULT / CUSTOM switch and a reset-to-defaults button on every page; a reset per object.
- Edited values in their own colour.
- A weapon's page lists every unit that fires it.

### Number entry

Read from ClientG 1.153.745903, none of it run yet:

- **Slider (first choice):** `GUISliderBarClass`, the lobby's credits row (`UI_Credits_Group` in
  `RA_UI_MATCHDETAILS_ALLIES.BUI`: title, value text, slider with − and + buttons). Cast 0x610140,
  `Set_Steps` 0xF8B0F0, `Set_Current_Step_Index` 0xF8AC70 (index, notify), position at +0x208.
  It sends value changed 0x36 and released 0x35 through `BIND_EVENT`. Each stat gets its own step
  size; the end buttons make the fine moves. No gamepad events: on the Deck it takes touch or the
  trackpad.
- **Text box:** `GUIEditBoxClass` (`SaveGameUserName_EditBox` in `RA_UI_SAVEGAMEPOPUP.BUI`), digits
  only through its IS_NUMERIC property, so no minus sign or decimal point. ClientG never opens the
  Deck's keyboard; `ISteamUtils::ShowFloatingGamepadTextInput` on focus (0x33) might.
- **Stepper (fallback):** two buttons and a text widget, the ADD-ONS screen's parts. Clicks fire on
  release, so hold-to-repeat needs a timer between mouse down (0x04) and up (0x05).
- Traps: a handler that sets the slider passes notify 0, or 0x36 fires again; cloned rows need
  unique names and instance ids, and names over 15 characters take the lend-in-place lookup.

## Decisions

- TD buildings: move the doubling to the base pass, or halve in the editor.
- Save games: store the player block in the save (proposed), or load with the current file.
- Leaking keys: write only keys `rules.ini` sets (proposed), or snapshot and restore the type tables.
- Which match rules ship first.
