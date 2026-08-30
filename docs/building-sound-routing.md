# Building sound routing (TD-authentic audio for GDI/Nod)

How RA building audio is triggered, which events have TD equivalents worth
routing for GDI/Nod, and the routing pattern. Complements
`td-audio-routing-recipe.md` (the SFXEvent/launcher mechanics) and
`reference-td-eva-routing` (EVA voices).

## The routing pattern

The engine sends **one** VOC name per sound; the Remastered launcher just plays
the mapped clip and cannot know the player's faction. **Faction-routing must
happen in the DLL.** Two keys are available:

- **Building-keyed:** `Class->Type >= STRUCT_TDOBLI && Class->Type < STRUCT_COUNT`
  — true for all separated TD structures. Use when the sound belongs to a
  building (placement, construction).
- **Player-keyed:** `PlayerPtr->ActLike == HOUSE_GOOD || == HOUSE_BAD` — use for
  player-global UI sounds (credit tick).

Then add a new `VOC_TD_*` (`defines.h` enum + `audio.cpp` table — **append to
both, index-aligned**), dispatch the TD VOC in the gated branch, and register
`RAC_SFX_<NAME>` / `RAR_SFX_<NAME>` SFXEvents in `SFXEVENTSNONLOCALIZED.XML`
pointing at the TD WAVs (which already ship in the base MEGs).

## Event-by-event map

| Event | RA sound | TD equivalent | Status |
|---|---|---|---|
| **Placement slam** | `VOC_PLACE_BUILDING_DOWN`=`PLACBLDG` (`house.cpp` place, `unit.cpp` MCV deploy) | `VOC_SLAM`=`HVYDOOR1` (TD `HOUSE.CPP:2933`) | **Shipped** `VOC_TD_PLACE_BUILDING_DOWN`, building-keyed |
| **Construction loop** | `VOC_CONSTRUCTION`=`BUILD5` | `VOC_TD_CONSTRUCTION`=`CONSTRU2` (`building.cpp` Mission_Construction) | Shipped earlier |
| **Credit tick** | `VOC_MONEY_UP/DOWN`=`CASHUP1/CASHDN1` (`credits.cpp:104/106`) | `VOC_UP/DOWN`=`TONE15`/`TONE16` (TD `CREDITS.CPP:98/100`) | **NOT ACHIEVABLE — launcher-driven** (see below) |
| **Damaged** | *none* — RA plays no building hit-SFX | — | No action |
| **Sell** | `VOC_CASHTURN` + EVA voice | `VOC_CASHTURN` (TD `HOUSE.CPP:4761`) — same | No action |
| **Destroyed** | `VOC_KABOOM22` + `VOC_CRUMBLE` | none — TD's BUILDING/TECHNO play no building-death VOC; `KABOOM22` not in TD's table | Left as-is (user choice) |

## Two hard-won rules (2026-05-28)

**1. Every routed TD sound MUST have its WAV bundled in the mod's `Data/AUDIO/`.**
The Remastered launcher in RA mode loads only RA's asset set — it cannot read
the TD MEGs. A `RAC_SFX_<NAME>`/`RAR_SFX_<NAME>` SFXEvent whose `SampleNamesList`
names `TDC_SFX_X.WAV`/`TDR_SFX_X.WAV` is **silent** unless those WAVs are
extracted (from `SFX3D.MEG`) into `resources/remaster_mods/Vanilla_RA/Data/AUDIO/`.
Symptom of a missing WAV: the routed sound goes silent rather than erroring — which
can masquerade as "fixed" (e.g. the placement double vanished only because the new
`HVYDOOR1` had no sample). **Checklist:** when adding a routed TD VOC, always also
extract its WAV(s) into `Data/AUDIO/`.

**2. The credit tick — faction-routed via the silence-and-refire flank (IMPLEMENTED
2026-08-31, awaiting in-game verdict).** The 2026-05-28 findings stand and are the
foundation: the launcher fires `RA?_SFX_cashup1`/`cashdn1` itself, faction-blind
(`Graphic_Logic`'s sound path never runs — proven by the empty-diagnostic-file
technique), so no data wiring alone can faction-route it. BUT the DLL *drives the
roll the launcher displays*: `HouseClass::AI` runs `VisibleCredits.AI(false, this,
true)` per house, and `dllinterface.cpp:6966` exports `VisibleCredits.Current` as
the sidebar counter. So the mechanism is: (a) data-silence the launcher's stock
tick events (samples → `SILENTD.WAV`); (b) fire the tick from `CreditClass::AI`
at the exact roll step, keyed on `ActLike` — GDI/Nod get TD `TONE15`/`TONE16`
(VOC_TD_MONEY_UP/DOWN → RA?_SFX_TONE15/16 → TD?_SFX_TONE15/16.WAV, in-MEG),
Allied/Soviet get the original RA samples under DLL-fired aliases
(VOC_DLL_MONEY_UP/DOWN → RA?_SFX_CASHUPD/CASHDND → RA?_SFX_cashup1/cashdn1.WAV;
fresh names needed because the stock event names are the silenced ones). Sync is
exact by construction — the sound fires from the same step that moves the number.
Known limitation: MP clients lose the tick (silenced events, DLL fires
local-player-only) — see known-issues.
*Diagnostic technique worth reusing: when unsure whether a sound is DLL- or
launcher-driven, drop a `fopen`-append log at the DLL call site — an empty file
while the game runs proves the launcher owns it.*

## Gotcha that cost us a session

The "double construction sound" on GDI/Nod was **not** a bug in one trigger — it
was two *separate, legitimate* sounds stacking: the **placement slam** (`PLACBLDG`)
fires the instant you drop the building, then the **construction loop**
(`CONSTRU2`) starts over it. RA factions sounded fine only because `PLACBLDG` +
`BUILD5` are both RA-flavoured. The fix was routing the slam to TD's `HVYDOOR1`,
not silencing anything. **When chasing a "doubled" sound, first confirm whether
it's one trigger firing twice or two different triggers in the same flow.**
