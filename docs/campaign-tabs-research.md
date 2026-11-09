# Mission Select and campaign tabs

**Status:** Reference. No campaign ships yet (`gdi-nod-campaign-story.md`; it waits behind the AI
milestone).

Mission Select reads `INSTANCES.XML`. A campaign mission is delivered by shadowing an existing
Counterstrike or Aftermath slot's scenario INI from the mod's `CCDATA/`, with `[Digest]` stripped
(proven on the desktop and the Deck). The CAMPAIGNS page (`campaigns-page.md`) owns the
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

- The truncation experiment cut all three structure files (`RA_ALLIES.XML`, `RA_ALLIES_MISSIONS.XML`,
  `RA_CAMPAIGNMAPS.XML`) to two missions: all 14 still showed, and mission 14 no longer launched.
- The probe won itself because, with no enemies left, its "destroy all" win trigger fired at the start.
- The probe ran on a dev
  build whose fresh `tf_astar.log` writes showed the DLL was current, with no crash on either machine.
- The digest abort and skip in TF's tree: `RELEASE_VERSION` in `defines.h`, the abort in `Read_Scenario_INI`
  (`scenario.cpp`, result 2 → return false), the skip in `CCINIClass::Load` (`ccini.cpp`, `if (len > 0)`).

**Consequence for the campaign arc:** the delivery is per-slot scenario INIs in CCDATA
(mod-shippable, no same-size rule), with each mission's name and select-screen briefing as new
`ModText.csv` keys on its instance (`campaigns-page.md`). What remains is content (the 17
RA-format missions) and presentation.

---

## CONFIG.MEG campaign files (catalogue)

`INSTANCES.XML`, the manifests, each tab's campaign and mission files, the campaign maps and their `GuiLayer`s, and
the instance counts per `Variant`: see the field manual's
[Custom campaigns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-campaigns.md#how-the-campaign-files-fit-together),
How the campaign files fit together. Beyond the manual: TD's `GDI.XML`, `NOD.XML`, `CONSOLE.XML` and `FUNPARK.XML`
each have a `*_MISSIONS.XML` beside them, a `Variant` also carries its base's Faction and music, and
the screens are `DATA/ART/GUI/RA/RA_CAMPAIGN_SELECT.BUI` and `RA_MISSIONSELECT.BUI` (TD's: `GUI/CNC/CNC_CAMPAIGN_SELECT.BUI`,
`UI_MISSIONSELECT.BUI`); TF ships an edited `RA_MISSIONSELECT.BUI`. Mission Select's tabs come from ClientG's tab
sort by game, expansion and house (`campaigns-page.md`).

---

## The engine wall and new instances

TD's GDI and Nod campaigns can't be borrowed, and a new instance displays but won't launch: see the field manual's
[Custom campaigns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-campaigns.md#traps) (Traps, and Adding a mission). TF's way round is the mission carrier or a hijacked
slot (`campaigns-page.md`).

---

## Notes

1. **Distribution:** a mod's own `Data/CONFIG.MEG`, or loose files, override the base: see the field manual's [Overriding the launcher's data](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#three-ways-in). TF's proof: a `MASTERTEXTFILE` relabel `Turkey`→`Nod` showed in the skirmish lobby picker and the in-game sidebar. TF's delivery: `config-meg-mod-delivery.md`.
2. **The RA roster build:** the tab sort is on the field manual's [Custom campaigns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-campaigns.md#tabs-and-houses), Tabs and houses; `campaigns-page.md` has TF's hooks.
