# The CAMPAIGNS page

**Status:** Reference. Built for 5.1.0: Mission Select becomes the CAMPAIGNS page, with a tab per
faction and every faction tab reading COMING SOON until its campaign lands.
**Open:** the mission carrier (dev builds only), Continue and Start over in the bottom bar, greying
Start on an empty tab, the TS Nod tab, a New Game campaign-select screen.

The stock Mission Select screen, rebuilt in data and steered by the DLL. ClientG still runs the
screen; the mod moves its widgets, repaints its art and hooks the few decisions that assume RA's
two sides. Addresses are ClientG.exe 1.153.745903 (`redalert/tf_launcher.cpp`).

## What the player sees

- The main menu's Mission Select button reads **CAMPAIGNS**, and so does the screen's title.
- Two columns in TD's green-on-gunmetal look: the campaign title and mission list on the left;
  the mission's name, label, briefing, Introduction / Completion and difficulty on the right.
- A tab row with game banners: **RED ALERT** over Allies and Soviets, **TIBERIAN DAWN** over GDI
  and Nod, **TIBERIAN SUN** over TS GDI, and Custom on its own.
- Each mission row carries its faction's crest, and its label reads the faction and number
  (`GDI 1`, `Nod 1`, `TS GDI 1`; RA missions keep their stock labels).
- A faction tab with no missions shows **COMING SOON**. Custom never does.

## Tabs

ClientG has six tab categories and files every mission into one of them. The page relabels the
expansion and Ant tabs as the TD and TS factions.

| Page tab | ClientG category | Stock tab reused | A mission lands here when |
|---|---|---|---|
| Allies | 6 | Allies | RA, no expansion, Allied house (Spain, Greece, England, France) |
| Soviets | 7 | Soviets | RA, no expansion, Soviet house (USSR, Ukraine) |
| GDI | 8 | Allied expansions | RA, Counterstrike or Aftermath base, Allied house **or GDI** |
| Nod | 9 | Soviet expansions | RA, Counterstrike or Aftermath base, Soviet house **or NOD** |
| TS GDI | 10 | Ant | RA, Ant base, any house |
| Custom | 11 | Custom | the player's own maps |

The bold parts are the mod's: stock ClientG drops a GDI or Nod mission from every RA tab. The
house is ClientG's ExternalFactionType: GDI 0, NOD 1, Jurassic 2, Spain 3, Greece 4, England 5,
France 6, USSR 7, Ukraine 8, Multi 9.

## The launcher hooks

| Where | What it does |
|---|---|
| Tab sort `0x633520`, side tests at `0x63382F` / `0x633878` | Counts GDI as Allied-side and NOD as Soviet-side for expansion missions. |
| Row style `0x632FFA` | Picks the row's crest group from the mission's house (stock: Allied-side or Soviet). |
| Row style, added groups | A mission on a tab listed in `ExtraRowStyles` shows that group (TS GDI on the Ant tab). |
| Row select `0x64E680` | Gives the added groups' buttons the selected look with the stock four. |
| Mission label `0x118D710` | GDI and Nod missions read `TEXT_TF_LABEL_*` plus their `<Mission>` number. |
| Tab switch `0x633E60` | Shows `TF_Coming_Soon` while the open campaign tab's list is empty. |

The hooks change nothing for stock missions, so the page behaves as stock wherever a mission is
RA's own.

## Adding missions to a tab

A mission is an instance in `scripts/campaigns_work/missions.xml`, text keys in
`resources/remaster_mods/Vanilla_RA/Data/ModText.csv`, and an entry in its tab's campaign files.

1. **The instance.** Add it to `missions.xml`; `campaigns_instances.py` appends it to the loose
   `INSTANCES.XML` after every stock instance, because ClientG reads that file in one pass and an
   instance placed before its `Variant` inherits nothing (its start markers log as `(0,0)` and it
   lists on no tab).

   ```xml
   <Instance Name="TF_GDI_1" Variant="Mobius_Aftermath_Allied_Map_Base">
       <LocationNameTextID>TEXT_TF_GDI_1</LocationNameTextID>
       <MissionBriefingTextID network="client">TEXT_TF_GDI_1_DESC</MissionBriefingTextID>
       <Mission>1</Mission>
       <ExternalGameID>RedAlert</ExternalGameID>
       <House>GDI</House>
       <IsUnlockedAtStart>true</IsUnlockedAtStart>
       <ShowOnMissionSelect>true</ShowOnMissionSelect>
       <DefaultToLegacyGraphics>true</DefaultToLegacyGraphics>
   </Instance>
   ```

   | Tab | `Variant` | `<House>` |
   |---|---|---|
   | Allies | `Mobius_Allied_Campaign_Base` | `Greece` (any Allied house) |
   | Soviets | `Mobius_USSR_Campaign_Base` | `USSR` or `Ukraine` |
   | GDI | `Mobius_Aftermath_Allied_Map_Base` | `GDI` |
   | Nod | `Mobius_Aftermath_USSR_Map_Base` | `NOD` |
   | TS GDI | `Mobius_Ant_Map_Base` | `GDI` |

   `<Mission>` is the number in the label. Only the first mission of a campaign is
   `IsUnlockedAtStart`; the rest unlock through the campaign chain.
2. **The text.** Add the name and briefing keys to `ModText.csv` (`"KEY",,,"English text",...`,
   matching the existing rows).
3. **The campaign.** Each tab's missions belong to one stock campaign: Allies `RA_ALLIES_CAMPAIGN`
   (`RA_ALLIES.XML`), Soviets `RA_USSR_CAMPAIGN` (`RA_USSR.XML`), GDI `RA_Aftermath_Allied_CAMPAIGN`
   and Nod `RA_Aftermath_USSR_CAMPAIGN` (both `RA_AFTERMATH.XML`), TS GDI `RA_Ant_CAMPAIGN`
   (`ANT.XML`). Add a `<CampaignMissions>` `<Entry>` there, and a
   `ProgressiveCampaignMissionTypeClass` in its `*_MISSIONS.XML` naming the instance, with
   `MapStageUnlock` set to the next stage (`-1` ends the campaign). Allies and Soviets pick missions
   on the campaign map, so they also need a stage in `RA_CAMPAIGNMAPS.XML`. The files ship loose in
   `Data/XML/CAMPAIGNS/`, starting from the stock copies in `CONFIG.MEG`.
4. **Rebuild** with `scripts/campaigns_page_build.sh`.

A list of 30 missions on one tab lists and scrolls as the stock lists do; there is no cap.

### Making a mission playable

The instance server only launches instances it knew at startup, so a new instance needs one of:

- **A hijacked stock slot**: keep a stock instance and ship its scenario as `CCDATA/<file>.ini`
  with `[Digest]` removed (`campaign-tabs-research.md`; proven for an unedited slot). The slot's
  tab follows its base, so an Aftermath Allied slot given `<House>GDI</House>` would land on the
  GDI tab; that edit is untested, and `campaigns_instances.py` hides every stock slot, so it would
  need to show the hijacked ones.
- **The mission carrier** (dev builds): a `TF_` instance launches under the name of
  `MOBIUS_ALLIED_CAMPAIGN_1_MAP`, its own map is handed to the DLL through
  `tf_carrier_mission.txt`, and its progress and medal are recorded under its own name. A
  one-mission campaign stage skips the map screen, and a finished campaign rolls the credits
  screen. It is hard-wired to one map until it reads its missions from data, and compiles only
  under `TF_DEV_BUILD`.

## Adding a faction's row crest

A crest group is a hidden clone of the GDI group in the row file. One more needs:
`MOD_GROUPS` in `scripts/campaigns_rows.py` (group and button names fit 15 characters),
`ROWS` in `scripts/campaigns_row_art.py`, `ROW_SETS` in `scripts/gui_texturesets_build.py`, and
an `ExtraRowStyles` entry in `redalert/tf_launcher.cpp` naming the house and tab. A sixth tab
(TS Nod) also needs a new tab button bound by the DLL and a category it borrows.

## Building it

`scripts/campaigns_page_build.sh` rebuilds everything from the stock copies in
`scripts/campaigns_work/` and the game's `TEXTURES_SRGB.MEG`; the CAMPAIGNS text and the TS GDI
texture set come from `build_config_meg.sh`.

| Output (mod `Data/`) | Script |
|---|---|
| `ART/GUI/RA/RA_MISSIONSELECT.BUI` | `campaigns_screen.py` |
| `ART/GUI/RA/RA_MISSIONSELECT_LISTENTRY.BUI` | `campaigns_rows.py` |
| `RA_UI_MISSIONSELECT_BG*.DDS`, `RA_UI_MISSIONSELECT_SCANLINES_*.DDS` | `campaigns_backgrounds.py` |
| tab icons and crested rows in `MT_COMMANDBAR_COMMON.TGA` | `campaigns_atlas.py` |
| `TF_UI_MISSIONSELECT_ITEMLIST_TSGDI_*.DDS` | `campaigns_row_art.py` |
| `XML/INSTANCES.XML` | `campaigns_instances.py` |

All of these ship loose, which overrides `CONFIG.MEG` at any size. The textures are gitignored;
`scripts/campaigns_work/textures.md5` records them and `package-for-workshop.sh` checks the staged
copies. The atlas painting runs on the existing atlas and can run again safely. `scripts/bui_dump.py`
prints a screen file's widget tree.
