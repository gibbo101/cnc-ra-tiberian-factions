# Mission Select / campaign tabs — how it works (SOLVED 2026-05-28)

The 2026-05-21 "research-only" version of this doc had four unresolved unknowns. They're now **resolved** by live testing on the Steam Deck (swapping a repacked base `CONFIG.MEG` and reading the result via screenshots). MEG extraction *and* repacking are solved; the Mission Select display pipeline is mapped.

Tools: `scripts/meg_extract.py` (read), **`scripts/meg_pack.py`** (repack — byte-identical round-trip, no integrity check), `scripts/mix_namedb.py` (CRC→name). Format detail: `mix-file-format.md`. Launcher boundary: `launcher-vs-dll-ownership.md`.

---

## TL;DR — the corrected model

**The Mission Select display is built from `DATA/XML/INSTANCES.XML`, not the campaign-structure files.** Each mission is an `<Instance>` carrying:

- `<LocationNameTextID>` (name) + `<MissionBriefingTextID>` (briefing) → localized strings
- **`<ShowOnMissionSelect>`** — visibility gate; `false` **hides the mission even if you've completed it** (proven)
- **`<IsUnlockedAtStart>`** — `true` ⇒ always shown; otherwise gated by player progress
- `<House>`, `<Mission>N</Mission>`, **`<ExternalGameID>`** (`RedAlert` | `TiberianDawn`), brief/action/win movies, `MissionSelectMapTexture`

The **structure files** — `RA_ALLIES.XML` (progression), `RA_ALLIES_MISSIONS.XML` (mission defs + `MapStageUnlock` chain), `RA_CAMPAIGNMAPS.XML`/`CAMPAIGNMAPS.XML` (`CampaignMapSelectMapClass` per tab + the territory-map-select flow) — control **progression and launch, NOT the displayed roster.** Editing them changes what *launches*, not what *shows*.

`CONFIG.MEG` has **no integrity check**, so a repacked archive with edited XML loads fine, and the game *does* read it (proven: breaking a mission def killed that mission's launch).

---

## What controls what (each row proven on the Deck)

| To change… | Edit | Evidence |
|---|---|---|
| Whether a mission **shows** | `INSTANCES.XML` `ShowOnMissionSelect` | set Allied 5A/5B/5C `false` → "Tanya's Tale" vanished despite being completed |
| Mission **name / briefing** | `INSTANCES.XML` `LocationNameTextID` / `MissionBriefingTextID` | data-confirmed (TextIDs → localized strings) |
| **Always visible** vs progress-gated | `IsUnlockedAtStart` | expansion missions are `true` → always show (never hide) |
| Whether a mission **launches** | `RA_*_MISSIONS.XML` def + `MapStageUnlock` | removed `RA_ALLIES_14` def → its "Start" did nothing; mission 1 still launched |
| Which **game's front-end** lists it | `ExternalGameID` | GDI instances are `TiberianDawn` ⇒ don't appear in RA mode |
| **Add / place** a mission in a tab | new `<Instance>` (target name + `Variant`, `ShowOnMissionSelect=true`, `IsUnlockedAtStart=true`) | ✅ injected `Mobius_Allied_Campaign_99_Map` → "Allies 99" appeared in the Allied tab (no def/`<Stages>` needed; name needs an RA-mode TextID; *launch* untested) |

### The experiments (base-CONFIG.MEG swap)
- Truncate all three structure files to 2 missions → **display still showed 14**; mission 14 un-launchable. ⇒ structure = launch, not display.
- Append expansion missions to `RA_ALLIES` `<Stages>` → **did not appear** under Allied. ⇒ roster isn't built from `<Stages>`.
- `ShowOnMissionSelect=false` on 3 completed Allied missions → **vanished**. ⇒ `INSTANCES.XML` is the display source, flag overrides progress.
- Ant tab shows **2 of 4** though all 4 are `ShowOnMissionSelect=true` ⇒ display is **progress-gated** (only unlocked missions show). A per-player completion/unlock record exists — *not* in `Player_RA_settings_1.bin` (no campaign strings); likely Steam cloud/stats.
- Inject a brand-new instance (`Mobius_Allied_Campaign_99_Map`, Allied variant, `ShowOnMissionSelect=true`, `IsUnlockedAtStart=true`, a deliberately-foreign GDI name TextID) → **a new "Allies 99" row appeared** in the Allied tab (name fell back to a placeholder because the TD TextID doesn't resolve in RA). ⇒ **placement is data-controllable.** So the "move" you want = **add-under-target-tab + hide-original** — both halves now proven. Caveats: name needs an RA-mode string; the *bare* instance displays but its launch isn't wired (no real scenario). For the launch half of the HIJACK path (existing slot, custom scenario), see the next section.

### Launch through a hijacked slot — ✅ RE-VERIFIED 2026-07-19 (desktop AND Steam Deck)

**A CS/AM mission slot launches OUR scenario INI via plain CCDATA shadow-by-name. Proven
end to end on the current v4.0.1 dev build** (overnight session 2026-07-19; Luke had
recalled an earlier untracked test — the recollection was right, and it now has a record).

**The probe:** stock `scg43ea.ini` (Aftermath Allied M1 "ITALY: Harbor Reclamation" —
instance `Mobius_Allied_Aftermath_Campaign_43_Map`, `<Mission>43</Mission>` → filename
`scg43ea.ini`) extracted from `CNCDATA/RED_ALERT/AFTERMATH/MAIN.MIX` → `general.mix`,
edited to wipe all 90 enemy entities (USSR + BadGuy across UNITS/SHIPS/INFANTRY/
STRUCTURES, indices renumbered), **`[Digest]` section REMOVED**, dropped as
`<mod>/CCDATA/scg43ea.ini` in the local Vanilla_RA mod. No CONFIG.MEG change at all.

**Result, reproduced twice:** mission launches from the Aftermath tab, loads our INI, and
**self-wins in ~30 s** (zero enemies → "destroy all" win trigger fires at start; DPTHCHRG
win movie plays, campaign advances to "In the Nick of Time", completion shield appears on
the roster). Dev-DLL freshness confirmed via live `tf_astar.log` writes; the probe INI
existed only in the local mod's CCDATA, so no other copy could have supplied the content.
Stock mission cannot be won unattended in seconds → the engine read our file. No crash on
either surface (the `535197b` desktop crash was INSTANCES.XML roster edits, not scenario
INIs).

**Confirmed on BOTH playtest surfaces (2026-07-19):** the Linux desktop (Claude, 2 runs)
and **Luke's Steam Deck** (Luke + son on aimee101's account) — same instant
mission-accomplished. The Deck result is the one that counts: vanilla Proton on the real
play hardware, so the hijack is not a desktop-prefix artefact. Deck delivery was nothing
more than an `scp` of the INI into the mod's `CCDATA/` (local v4.1 dev mod, no relaunch
needed — the file is read at scenario load). Probe INI removed from both machines after
the test; copies + desktop screenshots in the session scratchpad (`campaign-probe/`,
`ra-harbor-*.png`).

**Traps for the campaign implementation:**
- **`[Digest]`: strip it, don't leave it stale.** `RELEASE_VERSION` is defined
  (defines.h:72), so a WRONG digest aborts campaign scenario load (scenario.cpp:2282
  result==2 → return false). A MISSING digest skips validation entirely
  (ccini.cpp Load: `if (len > 0)`); community maps rely on the same hole.
- Scenario filename derives from the instance's `<Mission>` number + house letter
  (43 + Allied → `scg43ea.ini`); the display name lives in master-text, not the INI.
- In-engine briefing text comes from the launcher TextID path, not the INI `[Briefing]`,
  for the select-screen panel; the INI `[Briefing]` feeds the in-game briefing screen.

**Consequence for the campaign arc:** the hijack delivery = per-slot scenario INIs in
CCDATA (mod-shippable, no same-size rule) + cosmetic restyle (titles/briefings) via
CONFIG.MEG master-text where wanted. The unproven last mile is CLOSED; remaining work is
content (author the 17 RA-format missions) + presentation.

---

## CONFIG.MEG campaign files (catalogue)

```
DATA/XML/INSTANCES.XML            ~395 KB — MASTER INSTANCE DEFS = the display source
DATA/XML/CAMPAIGNS.XML            empty wrapper (real lists are the two manifests below)
DATA/XML/PROGRESSIVECAMPAIGNFILES.XML / PROGRESSIVECAMPAIGNMISSIONFILES.XML  — file manifests
DATA/XML/CAMPAIGNS/RA_ALLIES.XML  + RA_ALLIES_MISSIONS.XML    progression + defs
DATA/XML/CAMPAIGNS/RA_USSR.XML    + RA_USSR_MISSIONS.XML
DATA/XML/CAMPAIGNS/RA_AFTERMATH.XML + RA_AFTERMATH_MISSIONS.XML  (Counterstrike + Aftermath)
DATA/XML/CAMPAIGNS/GDI.XML  NOD.XML  CONSOLE.XML  FUNPARK.XML  ANT.XML  (+ *_MISSIONS.XML)
DATA/XML/CAMPAIGNS/CAMPAIGNMAPS.XML + RA_CAMPAIGNMAPS.XML   CampaignMapSelectMapClass per tab (GuiLayer)
DATA/ART/GUI/.../*_CAMPAIGN_SELECT.BUI, UI_MISSIONSELECT.BUI  UI layout (Unity binary; not edited)
```
Instances cluster by `Variant` (campaign base): 22 `Mobius_Allied_Campaign_Base`, 20 USSR, 8 Allied-Counterstrike, 9 Aftermath-Allied, etc. `Variant` is the **map base** (House, Faction, music), not a clean tab tag. Tabs themselves = `CampaignMapSelectMapClass` `GuiLayer` (`RA_ALLIES`, `RA_USSR`, `TD_GDI`, …).

---

## The engine wall (unchanged, and decisive)

GDI/Nod **campaign missions are `ExternalGameID=TiberianDawn`** — TD-game instances on a TD-mode tab (`GuiLayer="TD_GDI"`). They will **not** appear in our RA mod's Mission Select. A *playable* GDI/Nod campaign in the RA mod needs **new RA-mode instances**, because the TD scenario format won't run in the RA engine.

## Path to add GDI/Nod campaign sections

1. **Author RA-format scenario maps** for the GDI/Nod missions — the real content work.
2. Add `<Instance>` entries to `INSTANCES.XML`: `ExternalGameID=RedAlert`, `House=GDI`/`Nod` (HOUSE_GOOD/HOUSE_BAD), name/briefing TextIDs, `ShowOnMissionSelect=true`, `IsUnlockedAtStart=true` (or a `MapStageUnlock` chain).
3. Host them in a tab (`CampaignMapSelectMapClass`) — likely a repurposed RA tab; whether an RA-mode mission can ride a TD `GuiLayer` tab is **untested**.
4. Repack `CONFIG.MEG` with `meg_pack.py`.

---

## Two open issues

1. **Distribution — RESOLVED 2026-05-28.** A mod **can** ship its own `Data/CONFIG.MEG` and the launcher loads it over the base (proven on the Deck: a `MASTERTEXTFILE` country relabel `Turkey`→`Nod` shipped in the *mod folder* showed in the skirmish lobby picker + the in-game sidebar). The base install is never touched (Steam-verify-proof, mod-scoped — only active under the mod). So front-end edits ARE Workshop-distributable: ship the full repacked CONFIG.MEG (~44 MB). Canonical: **`config-meg-mod-delivery.md`**. (The loose `Data/` overlay still can't reach front-end data — the whole-MEG ship is what works.)
2. **The RA roster-build wrinkle (native code).** Editing the RA Allied tab's `<Stages>` never moved the displayed roster — only `ShowOnMissionSelect` did. So the exact RA left-panel roster build lives in `ClientG.exe`. Irrelevant for *adding* new instances; relevant only for cleanly *relocating* existing missions between RA tabs (would need more experiments or a targeted Ghidra dive).
