# Faction-conditional skirmish music — feasibility

**Researched 2026-05-29. Mod-wide path PROVEN ON DECK 2026-05-30 (TD track played in an RA skirmish).**
- **Mod-wide custom skirmish music (TD-heavy, weighted) = ✅ PROVEN — data-only, no code, Workshop-shippable.** Edit the `RA_MULTIPLAYER_MODE` event playlists in a mod CONFIG.MEG. **CRITICAL: the edit MUST preserve the member's exact byte length (pad to original size) or the launcher CRASHES ON LAUNCH** — see "Same-size rule" below.
- **Per-faction split (GDI/Nod→TD, Allied/Soviet→RA) = a well-defined CONFIG.MEG spike** (hinges on whether the `MusicMap` faction hook is honored). Not yet tested.
- **DLL-driven music = genuinely dead** (kept below — still accurate, rules out the engine-side approach).

## ⚠️ Same-size rule (CRITICAL — proven by the 2026-05-30 spike crash)

**Any edited member of CONFIG.MEG must keep its EXACT original byte length.** When a member's
size changes, every subsequent file's offset shifts, and the launcher **crashes on launch**
(hard crash, minidump in `log/LogFileErrors_0.txt`) — even though the rebuilt MEG is structurally
valid (`meg_pack` round-trips byte-identical and recomputes offsets correctly; our own reader
parses it fine).

**MECHANISM (proven 2026-05-30 via the crash log):** the mod-CONFIG.MEG overlay resolves file
data at the **base archive's offsets** — it does NOT trust the mod MEG's own (correct, recomputed)
offset table. Proof: growing `MUSICEVENTS.XML` (base offset 37,872,455) by +1024 bytes made the
launcher crash reading a *different* file, `PlayerXPTable.xml` (base offset 39,439,790, i.e. AFTER
MUSICEVENTS) — `XMLDatabase::Skip_XML_Header -- Current_Char() != '?', c: 54`: it read 1024 bytes
too early (the file had shifted +1024 in the mod MEG but the launcher used the base offset) and hit
garbage. So every file must sit at its exact base offset → every edited member must keep its exact
size, or all files after it become unreadable. This is offset aliasing, not size validation. The shipped faction-select CONFIG.MEG is byte-for-byte the same total size as
base (44201888) for this reason. Method: make the edit, then **pad back to the original member
size** with trailing spaces inside an XML comment placed before the root close tag
(`<!-- pad        -->\n</MusicEvents>`). Verify member size == original AND total MEG ==
44201888 before deploying. This rule generalizes to ALL CONFIG.MEG XML edits (faction defs,
master-text, music, etc.) — see [[reference-config-meg-mod-delivery]].

**Spike record (2026-05-30):** Spike 1 replaced the three `RA_MULTIPLAYER_MODE` playlists with 5
TD tracks → member shrank 120187→112428, total MEG 44201888→44194129 → **crash on launch**. Spike
2 = identical content but padded back to 120187 (total 44201888) → **launched fine, TD track
played in an RA skirmish.** Same content, only size differed → size is definitively the cause.
TD-track references in an RA-game event are FINE (the RA launcher context can play TD music).

**The ask (Luke):** when playing GDI/Nod, opening skirmish track = TD, with strong preference
for subsequent tracks to also be TD (occasional RA OK); Allied/Soviet = the reverse. A
*weighted* per-faction playlist.

---

## The key discovery — in-game music is data-driven (`MUSICEVENTS.XML`)

`DATA\XML\AUDIO\MUSICEVENTS.XML` (120 KB, **inside the moddable CONFIG.MEG**) defines every
piece of game music as a named `<MusicEvent>` with a fully moddable playlist:

```xml
<MusicEvent Name="RAR_MUS_RA_MULTIPLAYER_MODE">
    <PlayList>
        <Entry> RAR_MUS_Arazoid.WAV </Entry>
        ... 38 RA tracks ...
    </PlayList>
    <VolumePercent> 40 </VolumePercent>
    <FadeInSeconds> 0.0 </FadeInSeconds>
    <ContinueLastSample> No </ContinueLastSample>
    <FadeOutPrevSeconds> 1.0 </FadeOutPrevSeconds>
    <GapDelayMinSeconds> 5.0 </GapDelayMinSeconds>
    <GapDelayMaxSeconds> 5.0 </GapDelayMaxSeconds>
    <LoopInfinitely> Yes </LoopInfinitely>
    <RandomizePlayList> True </RandomizePlayList>
</MusicEvent>
```

**RA skirmish/MP in-game music = the `RA_MULTIPLAYER_MODE` event** (variants `RAC_`/`RAR_`/`RAB_`
for Classic/Remastered/Bonus audio modes). `RA_MAP_THEME` is the single-track menu/transition
theme; `RA_CAMPAIGN`/`RA_EXPANSIONS` are campaign. The launcher fires the event by **game-state
name**; the playlist + behavior are pure data.

**There is NO faction/side/condition attribute anywhere in MusicEvents.** RA has one in-game
event (no Allied/Soviet split — the per-side jukebox BUIs `RA_UI_MUSICJUKEBOX_ALLIED/_SOVIET.BUI`
are just UI skins). TD, by contrast, ships faction-split events that **already exist** and are
ideal remap targets:

```xml
<MusicEvent Name="TDR_MUS_TD_GDI_MAP_THEME"> <PlayList><Entry>TDR_MUS_GDI_MAP_THEME.WAV</Entry></PlayList> ... </MusicEvent>
<MusicEvent Name="TDR_MUS_TD_NOD_MAP_THEME"> <PlayList><Entry>TDR_MUS_NOD_MAP_THEME.WAV</Entry></PlayList> ... </MusicEvent>
```

The full event taxonomy: `*_MAIN_MENU`, `*_MAP_THEME`, `*_SCORE_SCREEN`, `*_MISSION_01..15`
(TD), `*_CAMPAIGN`/`*_EXPANSIONS` (RA), `*_MULTIPLAYER_MODE`, `*_CREDITS`, plus TD
`*_GDI_*`/`*_NOD_*` faction variants — each in C/R/B audio-mode flavors.

---

## ① Mod-wide TD music — FEASIBLE (data-only)

Edit `RA_MULTIPLAYER_MODE`'s `<PlayList>` (all three of `RAC_`/`RAR_`/`RAB_` so it survives the
player's Classic↔Remastered audio toggle) in a mod `Data/CONFIG.MEG`: compose the `<Entry>` list
mostly of TD tracks + a few RA, keep `RandomizePlayList=True`. This delivers **exactly** the
"strong TD preference, occasional RA" behavior, for every skirmish while the mod is loaded.
Ships via the proven CONFIG.MEG mod-delivery path ([[reference-config-meg-mod-delivery]]); repack
with `meg_pack.py`. **No DLL change.**

Caveats:
- **Faction-blind.** The event is chosen by game (RA), not by who you picked — so an Allied/Soviet
  player in the mod gets the same TD-heavy mix. Acceptable for a TD-factions mod, but not the
  per-faction split. For that, see ②.
- **"Opening track" control is limited.** `RandomizePlayList=True` randomizes the first track
  from the pool. A fixed TD opener needs `RandomizePlayList=False` (plays in list order →
  deterministic opener, but then the whole rotation is fixed order, not weighted-random). No
  clean "fixed opener + random remainder" in the schema. Pick one.
- TD track filenames use mixed-case `.WAV` as written in MusicEvents (`TDR_MUS_Act_On_Instinct.WAV`);
  match the casing/extension the existing entries use.

---

## ② Per-faction split — a real spike (hinges on `MusicMap`)

Since MusicEvents has no faction key, per-faction music depends entirely on the one faction-aware
hook in the data:

- `FACTIONS.XML` → every `<Faction>` has `<AudioTableName network="client">Faction1</AudioTableName>`
  (all currently point at one shared table; GDI/Nod are distinct factions here, so they *can*
  point at their own tables — we already mod this file for picker icons).
- `AUDIO_FACTIONS.XML` → defines the tables. The `Faction1` template has empty `<SFXMap>`,
  **`<MusicMap>`**, `<SpeechMap>`, with EA's comment: *"We are not using these for C&C TD / RA,
  since we need to account for each game and SFX asset mode (Classic or Remastered)."*

**The spike (well-defined, ~1h):** create custom `GDI`/`Nod` audio tables in a mod
`AUDIO_FACTIONS.XML` with a populated `<MusicMap>` that remaps the in-game event
(`RA_MULTIPLAYER_MODE`) → a TD playlist event (the existing `TD_GDI_MAP_THEME`/`TD_NOD_MAP_THEME`,
or a new TD-heavy custom event); point GDI/Nod's `AudioTableName` at them in `FACTIONS.XML`; leave
Allied/Soviet on the default. Repack CONFIG.MEG, run a GDI skirmish on the Deck, listen.

- **If MusicMap is honored** → the full per-faction goal is achievable, and the weighted behavior
  is just the target event's playlist composition. Best outcome.
- **If it's a no-op** (EA's comment is literal) → fall back to ① (mod-wide).

Worth testing rather than trusting the comment: the rest of the music system is confirmed **live
and data-driven**, and `AudioTableName` is a real per-faction pointer the engine reads for every
faction. We don't even know `MusicMap`'s true capabilities, because RA's is empty (no populated
example exists anywhere in the shipped data — searched all MEGs). **Instrumentation note:**
CONFIG.MEG also contains debug-audio facilities (`DEBUGAUDIOSTATSDIALOG.BUI`,
`DEBUGAUDIOLOGFILTERSDIALOG.BUI`, `DEBUGAUDIOPRESETS.BUI`) — worth probing whether any can surface
whether `MusicMap` was consulted, since `ClientG.exe` is closed and the DLL has no music channel
to log from.

---

## Why the DLL path is dead (rules out the engine-side approach)

1. **Null audio backend in the remaster build.** `common/CMakeLists.txt` builds `commonr` from
   `COMMONR_SRC`, which includes **`soundio_null.cpp`** (lines 108-117, 186-189): there
   `File_Stream_Sample_Vol` is `return 1;` and `SampleType` is never set (stays 0). The real
   backends are only in the *vanilla* lib `commonv`.
2. **`ThemeClass` is therefore inert.** `Play_Song`/`Queue_Song` early-out on `SampleType==0`
   (theme.cpp:293/333); the in-game tick `conquer.cpp:1762` is `SampleType`-gated. Even its
   existing per-faction `Owner` filter (`(1<<PlayerPtr->ActLike)&_themes[i].Owner`, theme.cpp:494)
   never runs. Vestigial legacy code.
3. **No DLL→launcher music event.** `EventCallbackType` (dllinterface.h:539-555) has
   SOUND_EFFECT/SPEECH/MOVIE/… but no music/score event. Only music-adjacent field is `Theme` on
   `CALLBACK_EVENT_MOVIE` (cutscene music).

So the faction-aware component (DLL, knows `ActLike`) can't drive music; control lives in the
launcher + CONFIG.MEG data. The **SFX one-shot hack** (fire a TD track via
`CALLBACK_EVENT_SOUND_EFFECT` at scenario start, like faction radar SFX/voices) also fails — the
DLL can't silence the launcher's concurrent music, so it would clash, with no rotation control.

---

## Assets present

`Data/MUSIC.MEG` holds both soundtracks as `.WAV`, naming `{RA,TD}{C,R,B}_MUS_<TRACK>`:
- **`*C_`** = Classic (90s recordings) · **`*R_`** = Remastered (Klepacki re-records) · **`*B_`** = bonus/remix
- **Classic vs Remastered is the player's audio-mode toggle**; the launcher picks `*C_` vs `*R_`
  accordingly (this is what EA's "account for each game and SFX asset mode" comment means).
  **Any playlist edit must cover both flavors** (`RAC_`+`RAR_`+`RAB_` event variants), same
  dual-prefix pattern as our EVA/SFX routing — editing only the remastered set breaks Classic mode.
- TD faction tracks confirmed: `TDR_MUS_GDI_MAP_THEME`, `TDC_MUS_GDI_MAP_THEME`,
  `TDR_MUS_NOD_MAP_THEME`, `TDR_MUS_NOD_SCORE`, + full TD library.

---

## Verdict & recommendation

| Path | Result |
|---|---|
| DLL `ThemeClass` / engine-side | **Dead** — null soundio, no music callback |
| DLL SFX one-shot opener | **No** — can't mute launcher music; no rotation control |
| CONFIG.MEG `RA_MULTIPLAYER_MODE` playlist edit (mod-wide) | ✅ **FEASIBLE** — data-only, weighted, Workshop-shippable; faction-blind |
| CONFIG.MEG `MusicMap` per-faction remap | **Spike** — well-defined, ~1h; targets `TD_GDI/NOD` events; unproven (EA comment) |

**Recommendation:** if the mod-wide TD-heavy soundtrack (①) is acceptable, it's a quick data-only
win with no risk. If the per-faction split matters, run the `MusicMap` spike (②) first — it either
unlocks the full goal cleanly or confirms the fallback to ①. Either way this is a CONFIG.MEG/data
task, not a DLL task.

## Planned work (TODO — documented 2026-05-29, not yet started)

Luke queued both, in order:

**TODO-1 — ✅ DONE 2026-05-30: 50/50 RA/TD skirmish mix shipped in the mod CONFIG.MEG.**
Deck-verified (6 skirmish loads → 3 RA / 3 TD, no crash). Implementation: all three
`RA_MULTIPLAYER_MODE` variants (`RAC_`/`RAR_`/`RAB_`) set to 31 RA + 31 TD entries (62 total),
`RandomizePlayList=True`, per-flavor matched (classic event→`*C_` tracks, remastered→`*R_`,
bonus→`*B_`), so the split follows the player's Classic/Remastered/Bonus audio setting. Member
padded to exactly 120187 / total 44201888 (same-size rule). Baked into
`resources/remaster_mods/Vanilla_RA/Data/CONFIG.MEG`. Ratio is trivially tunable (change the RA/TD
counts). Original notes for reference:
- Edit `RA_MULTIPLAYER_MODE`'s `<PlayList>` in a mod `Data/CONFIG.MEG`, **all three audio-mode
  variants** (`RAC_`/`RAR_`/`RAB_MUS_RA_MULTIPLAYER_MODE`), to interleave TD `<Entry>` tracks with
  the existing RA ones (weight toward TD per Luke's preference; keep `RandomizePlayList=True`).
- Use the matching flavor per variant: classic event → `TDC_MUS_*`, remastered → `TDR_MUS_*`,
  bonus → `TDB_/TDR_` as available. Match filename casing as written in the file.
- Repack via `meg_pack.py`; deliver in the mod's CONFIG.MEG ([[reference-config-meg-mod-delivery]]).
- Scope note: **faction-blind** by design (this is the mod-wide mix, not the per-faction split —
  that's TODO-2). Deck listen-test to confirm TD tracks actually stream in skirmish.

**TODO-2 — Spike: true per-faction playlists (= ② above).** Determines whether GDI/Nod can get a
TD-weighted list while Allied/Soviet keep RA.
- Create custom `GDI`/`Nod` audio tables in a mod `AUDIO_FACTIONS.XML` with a populated
  `<MusicMap>` remapping `RA_MULTIPLAYER_MODE` → a TD playlist event (reuse/extend
  `TD_GDI_MAP_THEME`/`TD_NOD_MAP_THEME`, or author a new TD-heavy event).
- Point GDI/Nod `<AudioTableName>` at them in `FACTIONS.XML`; leave Allied/Soviet on default.
- Repack CONFIG.MEG, run a GDI skirmish on the Deck, listen. Try the debug-audio facilities
  (`DEBUGAUDIOSTATSDIALOG.BUI` / `DEBUGAUDIOLOGFILTERSDIALOG.BUI`) to instrument whether `MusicMap`
  is consulted.
- Outcome gate: **honored** → full per-faction goal (supersedes TODO-1's faction-blindness);
  **no-op** → keep TODO-1 as the shipped solution. Run this spike *before* polishing TODO-1's
  weighting, since success changes the delivery shape.

## Cross-references
- `config-meg-mod-delivery.md` / [[reference-config-meg-mod-delivery]] — mod ships its own CONFIG.MEG (delivery path for both ① and ②).
- `mix-file-format.md` — `meg_pack.py` byte-clean repack used to rebuild CONFIG.MEG.
- `launcher-vs-dll-ownership.md` — boundary map; music is launcher+data-owned, not DLL.
- `td-audio-routing-recipe.md` / `reference-ra-launcher-sfx-prefix` — the SFX-event channel (why the one-shot hack can't do music; dual classic/remastered prefix pattern).
