# Mission Select and campaign tabs

**Status:** Reference. No campaign ships yet (`gdi-nod-campaign-story.md`; it waits behind the AI
milestone).

Mission Select reads `INSTANCES.XML`. A campaign mission is delivered by shadowing an existing
Counterstrike or Aftermath slot's scenario INI from the mod's `CCDATA/`, with `[Digest]` stripped
(proven on the desktop and the Deck). The CAMPAIGNS page (`campaigns-page.md`) now owns the
roster: it hides the stock missions and places the mod's own on each tab.

Tools: `scripts/meg_extract.py` (read), **`scripts/meg_pack.py`** (repack — byte-identical round-trip, no integrity check), `scripts/mix_namedb.py` (CRC→name). Format detail: `mix-file-format.md`. Launcher boundary: `launcher-vs-dll-ownership.md`.

---

## Display, launch and the hijack

What Mission Select shows comes from `INSTANCES.XML`; what launches comes from the campaign files; a stock slot
plays a scenario INI of its name shadowed from the mod's `CCDATA/`, with `[Digest]` removed. All of it, with the
experiments and the probe that proved it, is on the field manual's
[Custom campaigns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-campaigns.md#display-and-launch-are-separate) (Display and launch
are separate, Replacing an official mission, Traps, How it was verified); `CONFIG.MEG`'s missing integrity check is
on [Overriding the launcher's data](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#a-replacement-configmeg).
Beyond the manual:

- The expansion missions are `IsUnlockedAtStart` true, so they always show.
- The truncation experiment cut all three structure files (`RA_ALLIES.XML`, `RA_ALLIES_MISSIONS.XML`,
  `RA_CAMPAIGNMAPS.XML`) to two missions: all 14 still showed, and mission 14 no longer launched.
- The progress record isn't in `Player_RA_settings_1.bin`, which holds no campaign strings.
- The probe won itself because, with no enemies left, its "destroy all" win trigger fired at the start.
- The probe's `scg43ea.ini` came from `CNCDATA/RED_ALERT/AFTERMATH/MAIN.MIX` → `general.mix`, and ran on a dev
  build whose fresh `tf_astar.log` writes showed the DLL was current, with no crash on either machine.
- The digest abort and skip in TF's tree: `RELEASE_VERSION` at `defines.h:72`, the abort at `scenario.cpp:2282`
  (result 2 → return false), the skip in `ccini.cpp` `Load` (`if (len > 0)`).

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

## The engine wall and new instances

TD's GDI and Nod campaigns can't be borrowed, and a new instance displays but won't launch: see the field manual's
[Custom campaigns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-campaigns.md#traps) (Traps, and Adding a mission). TF's way round is the mission carrier or a hijacked
slot (`campaigns-page.md`).

---

## Notes

1. **Distribution:** a mod's own `Data/CONFIG.MEG`, or loose files, override the base: see the field manual's [Overriding the launcher's data](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#three-ways-in). TF's proof: a `MASTERTEXTFILE` relabel `Turkey`→`Nod` showed in the skirmish lobby picker and the in-game sidebar. TF's delivery: `config-meg-mod-delivery.md`.
2. **The RA roster build:** the tab sort is on the field manual's [Custom campaigns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-campaigns.md#tabs-and-houses), Tabs and houses; `campaigns-page.md` has TF's hooks.
