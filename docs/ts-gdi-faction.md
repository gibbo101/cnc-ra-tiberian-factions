# Tiberian Sun GDI — the fifth playable faction

**Status:** Reference; shipped in 5.0.0.
**Open:** TS Nod (below), and the TS GDI AI gaps in `todo.md`.

Tiberian Sun GDI is the fifth playable faction. The lobby's TS GDI starts on a TS yard with a TS
army, Tiberian Sun's EVA, voices and crest, and skirmish AIs play it. `TF_TS_GDI_FACTION` defaults
to 1 and releases ship it; built with 0, Germany goes back to being an Allied duplicate. The tree
itself is `ts-gdi-tree-plan.md`. No new `HousesType` value and no launcher wall: one country house,
decoupled. Read this before adding a sixth faction.

---

## The mechanism: one country house, decoupled

`HOUSE_GERMANY` leaves `HOUSEF_ALLIES` and becomes its own side:

```c
#define HOUSEF_ALLIES (HOUSEF_ENGLAND | HOUSEF_SPAIN | HOUSEF_GREECE | HOUSEF_FRANCE | HOUSEF_TURKEY)
#define HOUSEF_TSGDI  (HOUSEF_GERMANY)
```

`Is_TS_GDI(HousesType)` (defines.h) is the single predicate every side-flavoured branch asks,
so no other file names the country. Germany was chosen because its picker row was one of the
four Allied/Soviet duplicates, the slot set aside for the first new faction
(`faction-select-identity.md`), and because the launcher already knows it natively (colour, flag, start
markers, loading screens), which is what makes a fifth faction free of launcher work.

**No DLL remap is needed** (route 2 in the field manual's
[Adding a faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/adding-a-faction.md#how-a-pick-becomes-a-house)), unlike GDI and Nod,
which `CNC_Set_Multiplayer_Data` remaps on receipt (Spain→`HOUSE_GOOD`, Greece→`HOUSE_BAD`).

---

## What each piece cost

Every piece rides the pipeline the other four factions already use. Nothing here is bespoke.

| Piece | How | File |
|---|---|---|
| The house | `HOUSEF_TSGDI`, `Is_TS_GDI()` | `redalert/defines.h` |
| Tech tree | `Yard_Factions()` returns `HOUSEF_TSGDI` for a standing `TSFACT`; every TS entity's `Owner=` gains `Germany` | `house.cpp`, `CCDATA/rules.ini` |
| Starting roster | a `TsGdiType` column in `Create_Units`' table: Titan + Wolverine, Amphibious APC, Hover MLRS + Wolverine, Disruptor | `scenario.cpp` |
| Starting MCV | the `ActLike` switch in the start-unit code picks `UNIT_TSMCV` for `HOUSE_GERMANY` | `scenario.cpp` |
| Picker row | `Faction8` joins `TD_HUD`; master-text `FACTION_NAME_FACTION_8` / `BONUS_GERMANY` / `REDALERT_GERMANY` = "TS GDI" (6 chars, an exact fit for "Allies") | `factions_build.py`, `mastertext.edits.txt` |
| Picker emblem + map badge | `_08` plate painted from `scripts/tab_emblems/tsgdi.png` (the painter now accepts a `file:` source as well as an atlas region) | `picker_emblems_paint.py` |
| TD sidebar | the same `TopLevelGUIList` / `…Alt` scene-name swap GDI and Nod get | `factions_build.py` |
| Radar crest | a fourth rect in the crest RAM patch | `dllinterface.cpp`, `crest_atlas_paint.py` |
| EVA | `SpeechTS[]` beside `SpeechTD[]`; 27 lines extracted from TS | `audio.cpp`, `ts_eva_build.py` |
| Unit voices | the TD dispatch table with a TS base-name swap; 52 samples | `dllinterface.cpp`, `ts_voices_build.py` |
| Cameos | base `RA_<IniName>` entries for the 14 older TS types, then the normal generator | `cameo_variants_build.py` |

**The emblem.** `scripts/tab_emblems/tsgdi.png` is Tiberian Sun's glowing campaign-select coin,
cut at 320 px from a SteamGridDB icon by **hazelnut** (credited in the README, Workshop and ModDB text).
It feeds the radar crest (`crest_atlas_paint.py`), the picker plate and map badge
(`picker_emblems_paint.py`), every TS-badged cameo (`cameo_badge_build.py`) and the Hunter
Seeker's badged cameo (`ts_pack_seeker.py`; without the raw TS art, composite the emblem at 90 px
onto `BuildIcon_SW_TSHUNT.tga` at (12,12), which reproduces the shipped file exactly). Changing
it means re-running those and deploying the atlas plus the changed cameos. The barracks flag and
the dropship bay's console carry the eagle rendered into their art from `gdi_eagle.png`; the patched
renderer file beside it (`resources/custom-art/ts-buildings-hd/tspile/src/`, `tsdrop/src/`) goes over
the art package's `src/` to render it again when that art is redone. `tsnod.png` is the matching Nod hexagon from the same icon, trimmed to its silver
frame, for TS Nod.

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

⚠ **The atlas has no free region for another crest** (99% covered; the `_DINO` slot was already
spent on the GDI eagle). The TS eagle is painted over **`UI_OBSERVER_MAP_BG`**, a plain metal panel
only TD-mode observer view draws. The atlas can grow instead (`ui-atlas-modding.md`, "Growing the
atlas"); otherwise the next crest needs the same kind of sacrifice (survey in
`crest_atlas_paint.py`'s docstring).

⚠ **A crest variant goes in four places:** the bloom filter, the full-scan attribution chain, the
per-frame re-verify, and the scan thread's copy of `want` (`TF_Crest_Request_Scan`). A missing case
does not fail: it falls through to a plausible default (stock), the patch stops recognising its own
writes, the scan log's `want=` is wrong, and the crest flickers for the first seconds of a match.

**The AI runs the TS tree** (`c7a5a404`): `TF_TS_Equivalent` in `house.cpp` mirrors each base role
onto its TS building, defences are the tower two-step, and the turbine rides the power role. It
builds no transports or navy and never uses the Firestorm or the EMP Cannon (`todo.md`).

⚠ **TS keys unit voices to numbered sets, not named events,** and each RA response event needs four
TS recordings, two infantry and two vehicle (the field manual's
[Porting art from other C&C games](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/porting-art-from-other-games.md#tiberian-sun), sound and music).
Set 15 includes the jump jet.

---

## How it was verified (no human at the machine)

The whole arc was driven headless — Xvfb + Steam under `systemd-run --user`, xdotool/scrot on
`DISPLAY=:2` — with the placement-grid and audio methods in the field manual's
[Testing under Proton](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/getting-started/testing-under-proton.md#testing-with-no-one-at-the-screen)
(the grid shows white when it's ready to click). Tiberium blocks placement, so a long match can leave no legal
cell near the yard ([The Tiberium ecosystem](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/tiberium-ecosystem.md#a-new-resource-is-its-own-overlay)).
The sink monitor was recorded with `pw-record --target auto_null.monitor`, which is how the EVA and unit voices
below were confirmed as *played*, not merely dispatched.

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

The switch is **build-time, not runtime**: the picker's row text and emblem are CONFIG.MEG data the
launcher reads at startup, before the DLL has a say. It defaults to 1 (`redalert/defines.h`) and
`package-for-workshop.sh` keeps it, so the repo's DLL, CONFIG.MEG and picker art are in release
shape. Building with 0 restores the four-faction mod exactly:

| | On (default, releases) | Off |
|---|---|---|
| `HOUSEF_ALLIES` | without Germany | with Germany |
| `HOUSEF_TSGDI` | `HOUSEF_GERMANY` | `HOUSEF_NONE` |
| `Is_TS_GDI()` | `house == HOUSE_GERMANY` | constant `false` |
| Picker row 6 | "TS GDI" + TS emblem, TD HUD scene | "Allies" + Allied crest, RA HUD scene |
| A TS yard | grants the TS tree | grants nothing (see below) |

`Is_TS_GDI()` going constant-false retires the starting roster, the EVA, the unit voices, the side
name and the crest: each branch simply never fires.

⚠ **`Yard_Factions()` must contribute `HOUSEF_TSGDI`, never `HOUSEF_GERMANY` directly,** or with the
faction off a TS yard unlocks the Allied tree (the field manual's
[Adding a faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/adding-a-faction.md#traps), traps).

The data side follows `TF_TS_GDI_FACTION` in the environment: `build_config_meg.sh` (master-text
overrides), `factions_build.py` (Faction8 in the TD-HUD scene swap) and `picker_emblems_paint.py`
(the `_08` plate). `TF_MEG_TARGET` points the MEG build at the staged copy, so a package run never
leaves the repo changed. The TS EVA and voice WAVs, their XML events and the unbadged cameo entries
ship either way; with the faction off nothing routes to them.

---

## The era mailbox, N eras wide

The launcher fires nine EVA lines itself; the mailbox is the two-part method in the field manual's
[EVA voice lines the launcher plays, by faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/launcher-eva-lines-by-faction.md):
the era-correct recording over each seed at match start, then over ClientG's cached copy. An era that never
recorded a line gets inaudible noise (`SILENT` in the builder).

It was a TD/RA **pair**. It is now a table with one payload per era per line, generated whole by
`scripts/eva_mailbox_build.py` into `redalert/tf_eva_mailbox.h`. **Adding TS Nod's CABAL or RA2's
announcers is one entry in that script's `ERAS` plus its recordings** — no new branch in the DLL,
which asks `TF_Eva_Era()` for an index and looks the row up.

Why it could not stay a pair, and what that cost (the rules are the manual's, part two and traps):

- **Every era's payload for a line is the same byte length,** so a new era re-pads every line and
  invalidates every needle — which is why the table is generated rather than pasted in by hand.
- ⚠ **The scan is bucketed by first needle byte.** One pass per row would be 12 passes over
  ClientG's heap at two eras and 60 at six.
- ⚠ **ffmpeg can't write the teardown line's `block_align` 70,** so `scripts/msadpcm.py` encodes at
  any alignment (35 dB SNR against the source) and every era's payload is produced properly.
- ⚠ **The shipped runtime seeds ARE the RA payloads, byte for byte.** ClientG picks the loose
  file over the base MEG once, at launch, so the seeds must exist then. It reads and caches a
  line's bytes the first time the line plays (`td-audio-routing-recipe.md`, "EVA lines the launcher plays", findings 4 and 5), by
  which point the match-start copy has already put an era payload over the seed. The builder
  still rewrites the seeds as current-length RA payloads, so that a line ever cached from the
  seed itself (a failed copy) stays one the overwrite can find. Untested: whether a drifted seed
  is ever cached in practice.
- ⚠ **The originals were never kept.** Only the padded outputs were in the repo, so RA's and TD's
  content is recovered by decoding those and trimming the pad — one extra ADPCM generation on
  those two eras. The frozen sources now live in `scripts/eva_work/src/` so the builder never
  reads its own output back (which would stack a generation per run). If the base recordings are
  ever re-extracted cleanly, replace that snapshot.

The teardown line's `scripts/msadpcm.py` payload plays in game, which proves the launcher accepts
the hand-rolled encoder's output. TS's recordings sit a little quieter than RA's (peaks ~15-25k against ~30k); worth a level pass
if it reads as quiet in play.

---

## TS Nod, the sixth faction

The same recipe on France: `HOUSEF_TSNOD (HOUSEF_FRANCE)`, `Faction9`, the CABAL announcer from
`SPEECH02.MIX` as one more `ERAS` entry in `scripts/eva_mailbox_build.py`, the emblem at
`scripts/tab_emblems/tsnod.png`, and a crest (a grown atlas, or another sacrificed region). The TS
Nod wall and gates are already in, dormant (`ts-gdi-tree-plan.md`). Relabelled side names fit
exactly: "Allies" (6 characters) → "TS GDI", and "TS Nod" likewise.

**The multi-era ceiling:** the picker has 8 country slots, so TD GDI, TD Nod, RA Allies, RA Soviet,
TS GDI, TS Nod, RA2 Allies and RA2 Soviet would fill it with no duplicates, each on a decoupled
country house. RA2 uses TS's asset formats (voxels and TS-format SHPs), so the TS pipeline extends
to it (the RA2 Apocalypse and Prism tanks already ride it as crate finds); its mechanics tier like
TS's, with prism forwarding, mirage disguise and the chrono and IFV logic as the hard tail.
