# Building sound routing (TD-authentic audio for GDI/Nod)

**Status:** Reference. Which RA building, credit and UI sound events have TD and TS sounds for GDI, Nod and TS GDI,
and how each is routed; shipped.

How RA building audio is triggered, which events have TD or TS equivalents, and the routing pattern. Complements
`td-audio-routing-recipe.md` (the SFXEvent/launcher mechanics and EVA voices).

## The routing pattern

The DLL sends **one** VOC name per sound; the launcher plays the mapped clip and can't know the player's faction, so
faction routing happens in the DLL. Two keys:

- **Building-keyed:** `BuildingTypeClass::Is_TS_Era()` and `Is_Tiberian_Era()` (`redalert/bdata.cpp`; the TD
  structures from `STRUCT_TDOBLI` on, the TS trees, the Tiberium tick, and gates by their era). Used for sounds that
  belong to a building (placement, construction), sent to the building's own house with `TF_Sound_Effect_For`, since
  in LAN the game loop runs as the lobby's first player, who may be another human.
- **Player-keyed:** `ActLike == HOUSE_GOOD || HOUSE_BAD` for GDI and Nod, `Is_TS_GDI(ActLike)` for TS GDI. Used for
  player-global UI sounds (the credit tick, radar on/off).

Then dispatch a new `VOC_TD_*` or `VOC_TS_*` in the gated branch, added and routed as on the field manual's
[TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#the-method), The method.
TS samples ship bundled under their own `TS`-prefixed names.

## Event-by-event map

| Event | RA sound | TD and TS equivalents | Routing |
|---|---|---|---|
| **Placement slam** | `VOC_PLACE_BUILDING_DOWN`=`PLACBLDG` (`house.cpp` place, `unit.cpp` MCV deploy) | TD: `VOC_SLAM`=`HVYDOOR1` (TD `HOUSE.CPP:2933`), as `VOC_TD_PLACE_BUILDING_DOWN`. TS: `VOC_TS_PLACE_BUILDING_DOWN`=`TSPLACE2` (TS `BuildingSlam=` PLACE2) | Building-keyed |
| **Construction loop** | `VOC_CONSTRUCTION`=`BUILD5` | TD: `VOC_TD_CONSTRUCTION`=`CONSTRU2` (`building.cpp` Mission_Construction). TS buildings rise in silence: no TS structure defines a build-up sound | Building-keyed |
| **Radar on/off** | `VOC_RADAR_ON/OFF`=`RADARON2`/`RADARDN1`; the launcher's auto-fire is silenced, the DLL re-fires | TD: `TFRADRON`/`TFRADROF` (TD Comm Center / Power Down). TS: `TSCOMMUP1`/`TSRADARDN1` (TS rules `[AudioVisual] RadarOn=COMMUP1`, `RadarOff=RADARDN1`). RA: `RAORADON`/`RAORADOF` | Player-keyed, in `On_Sound_Effect` (`dllinterface.cpp`) |
| **Credit tick** | `VOC_MONEY_UP/DOWN`=`CASHUP1/CASHDN1` (`credits.cpp:104/106`) | TD: `VOC_UP/DOWN`=`TONE15`/`TONE16` (TD `CREDITS.CPP:98/100`). TS: `VOC_TS_MONEY_UP/DOWN`=`TSCREDUP1`/`TSCREDDWN1`, TS's `CREDUP1`/`CREDDWN1` (TS rules `[AudioVisual] CreditTicks=`) | Player-keyed, silence-and-refire (below) |
| **Damaged** | *none*: RA plays no building hit sound | — | None |
| **Sell** | `VOC_CASHTURN` + EVA voice | `VOC_CASHTURN` (TD `HOUSE.CPP:4761`), the same | None |
| **Destroyed** | `VOC_KABOOM22` + `VOC_CRUMBLE` | none: TD's BUILDING/TECHNO play no building-death VOC, and `KABOOM22` is not in TD's table | Left as RA's |

## Two rules

**1. Hear every routed TD sound in game.** Why a routed sound can be silent, and the workaround, are in the field
manual's [TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#how-it-was-verified), How it was verified.
A silent route raises no error, so it can pass for a fix: the doubled placement sound (below) once seemed fixed only
because the new `HVYDOOR1` route was silent.

**2. The credit tick is silenced in data and re-fired by the DLL**, as on the field manual's
[Credit tick and radar sounds by faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/credit-tick-and-radar-by-faction.md).
TF's stock tick events point at `SILENTD.WAV`. `CreditClass::AI` (`credits.cpp`) plays the local player's tick
inline through `Sound_Effect`, keyed on `ActLike`: GDI/Nod get `VOC_TD_MONEY_UP/DOWN` → `RA?_SFX_TONE15/16`, TS GDI
`VOC_TS_MONEY_UP/DOWN`, Allied/Soviet get `VOC_DLL_MONEY_UP/DOWN` → `RA?_SFX_CASHUPD/CASHDND`. For each human LAN
joiner (`player_ptr != PlayerPtr`, `IsHuman`, not `GAME_NORMAL`) it calls `TF_Fire_Credit_Tick` (`dllinterface.cpp`)
instead, which picks the same pair and addresses it to the joiner's house. Whether a joiner hears it is untested
(`known-issues.md`).

## Doubled sounds

GDI and Nod's "double construction sound" was two separate sounds stacking, not one trigger firing twice: the
**placement slam** fires the instant the building drops, then the **construction loop** starts over it. RA factions
sound right because `PLACBLDG` and `BUILD5` are both RA's. The fix was routing the slam to TD's `HVYDOOR1`, not
silencing anything. When chasing a doubled sound, first check whether it is one trigger firing twice or two
different triggers in the same flow.
