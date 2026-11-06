# Building sound routing (TD-authentic audio for GDI/Nod)

**Status:** Reference. Which RA building, credit and UI sound events have TD sounds for GDI and
Nod, and how each is routed; shipped.

How RA building audio is triggered, which events have TD equivalents worth
routing for GDI/Nod, and the routing pattern. Complements
`td-audio-routing-recipe.md` (the SFXEvent/launcher mechanics and EVA voices).

## The routing pattern

The engine sends **one** VOC name per sound; the Remastered launcher just plays
the mapped clip and cannot know the player's faction. **Faction-routing must
happen in the DLL.** Two keys are available:

- **Building-keyed:** `Class->Type >= STRUCT_TDOBLI && Class->Type < STRUCT_COUNT`
  — true for all separated TD structures. Use when the sound belongs to a
  building (placement, construction).
- **Player-keyed:** `PlayerPtr->ActLike == HOUSE_GOOD || == HOUSE_BAD` — use for
  player-global UI sounds (credit tick).

Then dispatch a new `VOC_TD_*` in the gated branch, added and routed as on the field manual's
[TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#the-method), The method.

## Event-by-event map

| Event | RA sound | TD equivalent | Status |
|---|---|---|---|
| **Placement slam** | `VOC_PLACE_BUILDING_DOWN`=`PLACBLDG` (`house.cpp` place, `unit.cpp` MCV deploy) | `VOC_SLAM`=`HVYDOOR1` (TD `HOUSE.CPP:2933`) | **Shipped** `VOC_TD_PLACE_BUILDING_DOWN`, building-keyed |
| **Construction loop** | `VOC_CONSTRUCTION`=`BUILD5` | `VOC_TD_CONSTRUCTION`=`CONSTRU2` (`building.cpp` Mission_Construction) | Shipped earlier |
| **Radar on/off** | `VOC_RADAR_ON/OFF`=`RADARON2`/`RADARDN1`, launcher auto-fire silenced, DLL re-fires | `TFRADRON`/`TFRADROF` (TD Comm Center / Power Down) | **Shipped**, player-keyed. TS GDI has its OWN pair from 2026-09-06: `TSCOMMUP1`/`TSRADARDN1` (TS rules `[AudioVisual] RadarOn=COMMUP1`, `RadarOff=RADARDN1`) — it was borrowing TD's, which is the wrong era. |
| **Credit tick** | `VOC_MONEY_UP/DOWN`=`CASHUP1/CASHDN1` (`credits.cpp:104/106`) | `VOC_UP/DOWN`=`TONE15`/`TONE16` (TD `CREDITS.CPP:98/100`) | **Shipped** via silence-and-refire (see below). TS GDI joined 2026-09-05: `VOC_TS_MONEY_UP/DOWN` = TS's own `CREDUP1`/`CREDDWN1` (TS rules `[AudioVisual] CreditTicks=`), bundled under their own names. |
| **Damaged** | *none* — RA plays no building hit-SFX | — | No action |
| **Sell** | `VOC_CASHTURN` + EVA voice | `VOC_CASHTURN` (TD `HOUSE.CPP:4761`) — same | No action |
| **Destroyed** | `VOC_KABOOM22` + `VOC_CRUMBLE` | none — TD's BUILDING/TECHNO play no building-death VOC; `KABOOM22` not in TD's table | Left as-is (user choice) |

## Two rules

**1. Hear every routed TD sound in game.** Why a routed sound can be silent, and the workaround, are in the field
manual's [TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#how-it-was-verified), How it was verified.
A silent route raises no error, so it can pass for a fix: the placement double once vanished only because the new
`HVYDOOR1` was silent.

**2. The credit tick is silenced in data and re-fired by the DLL**, as on the field manual's
[Credit tick and radar sounds by faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/credit-tick-and-radar-by-faction.md).
TF's stock tick events point at `SILENTD.WAV`. `CreditClass::AI` (`credits.cpp`) plays the local player's tick
inline through `Sound_Effect`, keyed on `ActLike`: GDI/Nod get `VOC_TD_MONEY_UP/DOWN` → `RA?_SFX_TONE15/16`, TS GDI
`VOC_TS_MONEY_UP/DOWN`, Allied/Soviet get `VOC_DLL_MONEY_UP/DOWN` → `RA?_SFX_CASHUPD/CASHDND`. For each human LAN
joiner (`player_ptr != PlayerPtr`, `IsHuman`, not `GAME_NORMAL`) it calls `TF_Fire_Credit_Tick` (`dllinterface.cpp`)
instead, which picks the same pair and addresses it to the joiner's house. Whether a joiner hears it is untested
(`known-issues.md`).

## Gotcha that cost us a session

The "double construction sound" on GDI/Nod was **not** a bug in one trigger — it
was two *separate, legitimate* sounds stacking: the **placement slam** (`PLACBLDG`)
fires the instant you drop the building, then the **construction loop**
(`CONSTRU2`) starts over it. RA factions sounded fine only because `PLACBLDG` +
`BUILD5` are both RA-flavoured. The fix was routing the slam to TD's `HVYDOOR1`,
not silencing anything. **When chasing a "doubled" sound, first confirm whether
it's one trigger firing twice or two different triggers in the same flow.**
