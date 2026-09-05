# Tiberian Sun GDI — the fifth playable faction (2026-09-05)

**Status: BUILT AND VERIFIED IN A LIVE SKIRMISH** on branch `ts-gdi-faction`. Pick "TS GDI" in
the lobby and you start with a TS construction yard's MCV and a TS army, build the TS tree from
the TD sidebar, hear Tiberian Sun's EVA and unit crews, and fly the TS GDI eagle on the radar.

The mechanism is the one `ts-factions-feasibility.md` traced in July and never scheduled. It
worked as written: **no new `HousesType` value, no launcher wall.** This doc records what the
implementation actually took, which is a little more than the feasibility note predicted.

---

## The mechanism: one country house, decoupled

`HOUSE_GERMANY` leaves `HOUSEF_ALLIES` and becomes its own side:

```c
#define HOUSEF_ALLIES (HOUSEF_ENGLAND | HOUSEF_SPAIN | HOUSEF_GREECE | HOUSEF_FRANCE | HOUSEF_TURKEY)
#define HOUSEF_TSGDI  (HOUSEF_GERMANY)
```

`Is_TS_GDI(HousesType)` (defines.h) is the single predicate every side-flavoured branch asks,
so no other file names the country. Germany was chosen because its picker row was one of the
four Allied/Soviet duplicates — exactly the slot `project-lobby-picker-layout` earmarked for
the first new faction — and because the launcher already knows it natively (colour, flag, start
markers, loading screens), which is what makes a fifth faction free of launcher work.

**No DLL remap is needed.** GDI and Nod are remapped on receipt in `CNC_Start_Instance`
(Spain→`HOUSE_GOOD`, Greece→`HOUSE_BAD`); TS GDI needs nothing, because the picker row the
player clicks *is* the house they play.

---

## What each piece cost

Every piece rides the pipeline the other four factions already use. Nothing here is bespoke.

| Piece | How | File |
|---|---|---|
| The house | `HOUSEF_TSGDI`, `Is_TS_GDI()` | `redalert/defines.h` |
| Tech tree | `Yard_Factions()` returns `HOUSEF_TSGDI` for a standing `TSFACT`; every TS entity's `Owner=` gains `Germany` | `house.cpp`, `CCDATA/rules.ini` |
| Starting roster | a `TsGdiType` column in `Create_Units`' table: Titan + Wolverine, Amphibious APC, Hover MLRS + Wolverine, Disruptor | `scenario.cpp` |
| Starting MCV | `TF_Roster_Side()` picks `UNIT_TSMCV`, and the free bonus TS MCV every other human gets is suppressed | `scenario.cpp` |
| Picker row | `Faction8` joins `TD_HUD`; master-text `FACTION_NAME_FACTION_8` / `BONUS_GERMANY` / `REDALERT_GERMANY` = "TS GDI" (6 chars, an exact fit for "Allies") | `factions_build.py`, `mastertext.edits.txt` |
| Picker emblem + map badge | `_08` plate painted from `scripts/tab_emblems/tsgdi.png` (the painter now accepts a `file:` source as well as an atlas region) | `picker_emblems_paint.py` |
| TD sidebar | the same `TopLevelGUIList` / `…Alt` scene-name swap GDI and Nod get | `factions_build.py` |
| Radar crest | a fourth rect in the crest RAM patch | `dllinterface.cpp`, `crest_atlas_paint.py` |
| EVA | `SpeechTS[]` beside `SpeechTD[]`; 27 lines extracted from TS | `audio.cpp`, `ts_eva_build.py` |
| Unit voices | the TD dispatch table with a TS base-name swap; 52 samples | `dllinterface.cpp`, `ts_voices_build.py` |
| Cameos | base `RA_<IniName>` entries for the 14 older TS types, then the normal generator | `cameo_variants_build.py` |

---

## The one real surprise: a TS-only base had never existed

The sidebar rendered `<Missing> TSPILE_0` for most of the TS tree.

The DLL appends `_<badge>` to every sidebar `AssetName`, where the badge is the set of the
player's own factions that can build the entry — and **0 when only one faction can**, which is
the normal case. Before TS GDI, the TS tree was always a *second* tree beside a TD or RA one, so
the badge was never 0 for it and only the `_G` (TS-badged) variants were ever written. A house
whose only construction yard is the TS one asks for a key that never existed.

The fix is the pipeline's own shape, not a hand-written block: give each of the 14 older TS
types the **base `RA_<IniName>` entry** naming its pristine cameo (the newer walls/towers types
already had one), then let `cameo_variants_build.py` emit `_0` and `_G` from it, exactly as it
does for every RA, GDI and Nod entity. The pristine art was already shipped under its own names
(`BuildIcon_TS_Pile.tga` and friends).

**Rule this leaves behind:** a new faction whose tree is *only* reachable from its own yard needs
its entities' unbadged `_0` cameo variants, and those come from a base entry, never by hand.

---

## Traps

⚠ **The atlas has no free space for a fifth crest** (99% covered; the `_DINO` slot was already
spent on the GDI eagle). The TS eagle is painted over **`UI_OBSERVER_MAP_BG`** — a plain metal
panel only TD-mode observer view draws, which an RA-mode match never renders. Any further faction
crest needs the same kind of sacrifice; the survey is in `crest_atlas_paint.py`'s docstring.

⚠ **The crest scan matches records against every known rect.** Adding a variant means adding it
to the bloom filter, the full-scan attribution chain *and* the per-frame re-verify, or the patch
stops recognising its own writes after the first match.

⚠ **A computer house cannot run the TS tree** (its base builder has no TS roles). `TF_Roster_Side`
hands an AI that draws TS GDI the TD GDI roster instead of standing it on a yard it cannot use.
Revisit when the AI milestone's faction layer lands — it was designed for N factions.

⚠ **TS keys unit voices to numbered sets, not named events** (set 15 = GDI rifleman, set 25 = GDI
vehicle crew, both in `SOUNDS.MIX`). RA fires a named `VOC_` event and picks the extension from
the response variation, so each RA event needs four TS recordings: two infantry (`.V01`/`.V03`),
two vehicle (`.V00`/`.V02`).

---

## How it was verified (no human at the machine)

The whole arc was driven headless — Xvfb + Steam under `systemd-run --user`, xdotool/scrot on
`DISPLAY=:2` (`reference-headless-desktop-game-run`). Findings worth keeping:

- **Absolute pointer warps do not reach the placement cursor.** `xdotool mousemove` works for
  the HUD and for issuing orders, but the building-placement grid tracks *relative* motion only;
  steer it with `mousemove_relative` and screenshot to confirm the grid is white before clicking.
- **Tiberium blocks building placement**, so a match left running long enough to let the field
  spread has no legal cell left near the yard. Place early or restart.
- **Audio can be verified without ears.** Capture the sink monitor (`pw-record --target
  auto_null.monitor`) and matched-filter the capture against the shipped WAVs. Lines that
  actually played score 0.5–0.9 normalised; lines that never fired sit at 0.24 and below. This is
  how the EVA and unit voices below were confirmed as *played*, not merely dispatched.

**Confirmed in a live skirmish (TS GDI vs a Soviet AI, Docklands):**

1. Picker row 6 reads "TS GDI" with the TS GDI emblem, and starts a match as TS GDI.
2. Start: TS MCV, Titan, Wolverine, Amphibious APC, Hover MLRS, Disruptor.
3. Deploy: TS Construction Yard; sidebar on **TD's HUD scene**.
4. Tree: Tiberian Power Plant alone off a bare yard, then Power Turbine + TS Barracks + TS
   Tiberium Refinery once it stands — correctly named, correctly iconed.
5. Radar crest: the TS GDI eagle. A GDI player in the same build still gets TD's eagle.
6. EVA: `tf_speech.log` shows `actlike=5` dispatching `TSCONSTRU1` / `TSBLDGING1` while the
   Soviet AI still gets RA's lines; the capture matches those two recordings at 0.51 and 0.71.
7. Unit voices: TS crew samples match the capture at 0.89–0.91.

---

## What is left

- **The six launcher-fired EVA lines** (cannot deploy here, battle control terminated, mission
  won/lost, select target, insufficient power) still play **TD's** recordings for TS GDI. They do
  not pass through `On_Speech`; they come from the era mailbox, which currently pads a TD/RA
  *pair* to equal length and carries hardcoded needles for the ClientG cache overwrite
  (`eva_mailbox_payload.py`). A third era means a three-way pad and fresh needles.
- **TS GDI has no infantry of its own** — it fields the TD GDI riflemen. TS infantry is a
  content wave, not faction work.
- **TS Nod** is the same recipe with France: `HOUSEF_TSNOD (HOUSEF_FRANCE)`, `Faction9`, the
  CABAL announcer in `SPEECH02.MIX`, its own crest region (see the atlas trap above).
- **AI support**, per the trap above.
