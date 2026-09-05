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

## The release switch — `TF_TS_GDI_FACTION`

The faction can sit finished on `main` without appearing in a release. The switch is
**build-time, not runtime**: the picker's row text and emblem are CONFIG.MEG data the
launcher reads at startup, long before the DLL has a say, so no flag file can hide them.

`package-for-workshop.sh` builds with `-DTF_TS_GDI_FACTION=0` and regenerates the staged
front-end to match. Flip both when it is time to ship it.

**Off means today's `main` behaviour, exactly:**

| | On (local dev builds) | Off (releases) |
|---|---|---|
| `HOUSEF_ALLIES` | without Germany | with Germany, as before |
| `HOUSEF_TSGDI` | `HOUSEF_GERMANY` | `HOUSEF_NONE` |
| `Is_TS_GDI()` | `house == HOUSE_GERMANY` | constant `false` |
| Picker row 6 | "TS GDI" + TS emblem, TD HUD scene | "Allies" + Allied crest, RA HUD scene |
| A TS yard | grants the TS tree | grants nothing (see below) |

`Is_TS_GDI()` going constant-false is what retires the starting roster, the EVA, the unit
voices, the side name and the crest — each of those branches simply never fires, so there is
no second code path to keep in step.

⚠ **The one thing that does not fall out for free** is `Yard_Factions()`. It must contribute
`HOUSEF_TSGDI`, never `HOUSEF_GERMANY` directly: with the faction off, Germany is an Allied
country again, so a Germany bit there would let a crate-found TS yard unlock **the entire
Allied tree**. Empty-when-off is what makes the line safe.

The data side is three toggles, all driven by `TF_TS_GDI_FACTION` in the environment:
`build_config_meg.sh` (master-text overrides back to "Allies"), `factions_build.py` (Faction8
drops out of the TD-HUD scene swap) and `picker_emblems_paint.py` (the `_08` plate goes back
to the Allied crest). `TF_MEG_TARGET` points the MEG build at the **staged** copy, so a
package run never leaves the repo in release shape; the two generated intermediates it
rewrites are snapshotted and restored by the packager.

The TS EVA and voice WAVs, their XML events, and the unbadged cameo entries ship either way.
They are inert with the faction off — nothing can route to them — and the cameo entries are a
genuine fix regardless: a crate-found TS yard whose owner has lost their own yard badges 0 too.

---

## The era mailbox, N eras wide

Six lines are fired by the launcher itself and never reach `On_Speech`: cannot deploy here,
battle control terminated, mission won, mission lost, select target, insufficient power. The
mailbox writes the era-correct recording over the launcher's own sample names at match start,
and overwrites ClientG's cached copy so an in-session switch is corrected too.

It was a TD/RA **pair**. It is now a table with one payload per era per line, generated whole by
`scripts/eva_mailbox_build.py` into `redalert/tf_eva_mailbox.h`. **Adding TS Nod's CABAL or RA2's
announcers is one entry in that script's `ERAS` plus its recordings** — no new branch in the DLL,
which asks `TF_Eva_Era()` for an index and looks the row up.

Why it could not stay a pair, and what that cost:

- **Every era's payload for a line must be the same byte length**, because the cache overwrite
  finds a blob by hunting the *wrong* era's needle and subtracting that era's file offset. So a
  new era re-pads every line and invalidates every needle — which is why the table is generated
  rather than pasted in by hand.
- ⚠ **The scan is now bucketed by first needle byte.** It used to re-scan each chunk of ClientG's
  heap once per row; at two eras that was 12 passes, at six it would be 60 over hundreds of MB.
  Bucketing keeps the per-byte cost flat however many eras exist.
- ⚠ **ffmpeg cannot encode the alignment the teardown line needs.** Its MS-ADPCM encoder demands
  a power-of-two block size; "battle control terminated" needs `block_align = 70`, which is why
  that line used to be byte-padded instead of re-encoded. `scripts/msadpcm.py` encodes at any
  alignment (35 dB SNR against the source), so every era's payload can now be produced properly.
- ⚠ **The shipped runtime seeds ARE the RA payloads, byte for byte.** ClientG caches whatever
  sits at the launcher's sample name when it starts, so on a fresh install the cached blob is the
  seed — and the overwrite can only find it if the seed is a current-length era payload. The
  builder rewrites the seeds for that reason; let them drift and a new install silently keeps
  RA's voice for its first session.
- ⚠ **The originals were never kept.** Only the padded outputs were in the repo, so RA's and TD's
  content is recovered by decoding those and trimming the pad — one extra ADPCM generation on
  those two eras. The frozen sources now live in `scripts/eva_work/src/` so the builder never
  reads its own output back (which would stack a generation per run). If the base recordings are
  ever re-extracted cleanly, replace that snapshot.

TS's recordings sit a little quieter than RA's (peaks ~15-25k against ~30k); worth a level pass
if it reads as quiet in play.

---

## What is left

- **The six launcher-fired EVA lines are now TS's own** (built 2026-09-05, not yet heard in
  play). The mailbox is N-way: see "The era mailbox, N eras wide" below.
- **TS GDI has no infantry of its own** — it fields the TD GDI riflemen. TS infantry is a
  content wave, not faction work.
- **TS Nod** is the same recipe with France: `HOUSEF_TSNOD (HOUSEF_FRANCE)`, `Faction9`, the
  CABAL announcer in `SPEECH02.MIX`, its own crest region (see the atlas trap above).
- **AI support**, per the trap above.
