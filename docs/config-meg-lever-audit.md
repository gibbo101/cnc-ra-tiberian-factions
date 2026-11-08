# CONFIG.MEG lever audit — what the launcher's own data unblocks

**Status:** Reference. Which CONFIG.MEG data levers are in use, untried, or dead.

Census of CONFIG.MEG's 230 XML members for launcher levers. In use: `GameConstants_Mod.xml`
(classic lockout, mod hotkeys, zoom), `FACTIONS.XML`, `MASTERTEXTFILE`, `MUSICEVENTS`,
`GUITEXTURESETS` and the `.bui` screens. Untried: campaign files, team colours, cursors, lobby
value lists, the bonus gallery, slash commands. The sweep started when the classic-graphics
lockout, after three DLL-side routes and a RAM probe, turned out to be one constant EA shipped for mods.

**Standing rule this establishes:** a wall proven on the *code* side is not proven on the *data*
side. Before declaring a launcher behaviour impossible, grep CONFIG.MEG.

**Coverage.** All 230 non-tilepatch XML members were extracted and profiled (size, root element,
element census, keyword scan for `TBD` / `not used` / `no longer used` / `Community-requested` /
`for Modding`). Everything plausibly behavioural was then read. Whole classes were dismissed on
their profile, and that dismissal is itself a finding — see "Dismissed by class". Companion:
`config-meg-mod-delivery.md` (how a mod ships its own CONFIG.MEG), `mix-file-format.md`
(`meg_pack.py`, the same-size rule).

**How each lever ships:** a loose copy of the file, at any size, or the member inside a replacement CONFIG.MEG at
its exact byte length, with no member added or removed: see the field manual's
[Overriding the launcher's data](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#three-ways-in), Three ways in.

---

## Delivery: `GameConstants_Mod.xml` beats editing the member

The overlay (merged over the base constants, `overwrite="true"` for a list, the only `_Mod` overlay, no input
overlay) is on the field manual's [Overriding the launcher's data](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#gameconstants_modxml), `GameConstants_Mod.xml`.
Kushan documented it (ppmforums.com/topic-54809), and Vanilla Conquer's TD sample uses it to switch on megamaps.

**TF's constants ship in it** (classic-graphics lockout, mod hotkeys, the Unholy Alliance default, CFE's zoom
factors), so the 128 KB `GAMECONSTANTS.XML` member needs no same-size rewrite and no repack, and a rebuild has
one less member to clobber. With no input overlay, the mod sends its commands from the launcher's own keys instead (Tier 1
item 1 below).

## Tier 1 — actionable levers

### 1. Mod hotkey commands (in use)

EA's mod hotkey path (the constant, four commands with empty keys, and the DLL input event that stops at EA's
placeholder) is on the field manual's [Mod hotkey commands](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/mod-hotkey-commands.md#what-ea-left-in), What EA left in (the
constant's comment and how a key is written included; the bookmark commands above them bind F1–F4 that way). TF's handler is the `INPUT_REQUEST_MOD_GAME_COMMAND_1..4_AT_POSITION` cases of `CNC_Handle_Input` in
`redalert/dllinterface.cpp`.

**What ships:** `CNCEnableModHotKeyGameCommands` is on in `GameConstants_Mod.xml`, and the handler
in `dllinterface.cpp` (`INPUT_REQUEST_MOD_GAME_COMMAND_1..4_AT_POSITION`) uses all four. The
patched launcher key code (`TF_Patch_Launcher_Keys_In`, `launcher-vs-dll-ownership.md`) sends
them from the launcher's own keys, so every player's press reaches the host with no binding:
Mod Command 1 is the deploy key and runs each selected object's self-action (MCVs deploy,
transports unload); Mod Command 2 comes just before the launcher's own select-all, so the DLL can
filter harvesters and MCVs out of the selection; Mod Command 3 is camera-to-yard (H). Mod Command 4
carries a launcher's sidebar switches for its own house (`TF_SIDEBAR_CHOICE_MARK`). A player can
still bind Mod Command 1 to a key of their own.

**A mod cannot ship a binding as data**: the four routes tried, and the player's settings file, are on the field
manual's [Mod hotkey commands](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/mod-hotkey-commands.md#why-a-mod-cant-ship-the-bindings), Why a mod can't ship the bindings, and
[Overriding the launcher's data](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#what-none-of-them-reach), What none of them reach. One detail they lack: a
first binding inserts 64 bytes into the settings file, so the same-size trick doesn't apply to it either.

### 2. Campaigns are a faction-bound data layer

The campaign registry and its files are on the field manual's
[Custom campaigns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-campaigns.md#how-the-campaign-files-fit-together), How the campaign files fit together.

Each campaign file is small and declarative:

```xml
<ProgressiveCampaignTypeClass Name="RA_Ant_CAMPAIGN">
    <Faction>Faction6</Faction>
    <IntroMovie>TD/GDI1.bk2</IntroMovie>
    <CampaignMissions><Entry>Mobius_Ant_Campaign_1_Map</Entry> ...</CampaignMissions>
</ProgressiveCampaignTypeClass>
```

Campaigns are **faction-bound**, carry their own intro movie, and list mission map instances.
`GAMECONSTANTS.XML` also holds `CNCFirstAntCampaignMapName` / `CNCFirstJurassicCampaignMapName`
as client-side entry points.

**The ants are not a faction of their own** — worth stating because `<Faction>Faction6</Faction>`
reads like one. `FACTIONS.XML`'s 11 faction objects are on the field manual's
[Adding a faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/adding-a-faction.md#the-launchers-data-for-the-row), The launcher's data for the row. `Faction6` is an ordinary RA country slot that the Ant
campaign declares itself against, the same mechanism our factions use: GDI rides `Faction3`
(Spain), Nod `Faction4` (Greece) and TS GDI `Faction8` (Germany). The binding is one-directional
(campaign names a faction), and none of the faction entries carry buildable structure or unit
lists — those are all empty, because the tech trees live in our DLL.

**Two things follow.** First, if we ever repoint `ANT.XML`, bind it to `Faction3` or `Faction4`
so a GDI or Nod campaign sits on that faction's slot instead of a leftover country. Second,
`Faction_Funpark` is an eleventh entry with a **non-numeric name**, so the launcher's faction
table is a data list rather than a fixed `Faction1..10` enum. New factions did not need it: TS GDI
rides an existing country slot (`ts-gdi-faction.md`).
**`<CoopCampaignType>` is a cut feature, not a lever**: see the field manual's
[What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#the-walls-and-the-way-through) (the co-op campaign row). The field sits beside `<CampaignType>` in every faction, and
ClientG's compiled co-op code also tracks per-mission star counts. Whether ClientG would open the co-op screen from a loose `.bui` alone is
untested; TF's verdict is in `coop-missions-design.md`.

**Why it matters:** our campaign plan hijacks Counterstrike/Aftermath *mission slots*
(`campaign-tabs-research.md`). This is the layer above. We cannot add a campaign file, but
`ANT.XML` is 461 bytes and `FUNPARK.XML` 553 — **repointing a low-value campaign may be a
cleaner hijack than borrowing Aftermath slots**, and it comes with its own faction binding.
What Mission Select shows comes from `INSTANCES.XML`, and the campaign files decide what launches: see the field
manual's [Custom campaigns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-campaigns.md#display-and-launch-are-separate), Display and launch are separate.

### 3. Team colours are data

The team-colour files are on the field manual's [Overriding the launcher's data](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#example-team-colours), Example: team colours
(`CNCRATEAMCOLORS.XML` is 14.9 KB; its transforms work against `TeamColorLarge.tga`). Since GDI/Nod ride country slots, **their in-game colour identity is
data-editable** without touching the DLL. Not something we have wanted yet, but it is the answer
if faction colour ever comes up.

### 4. Mouse cursors are data

`MOUSEPOINTERS.XML` / `MOUSEPOINTERSX2.XML` define 90 `MousePointerDataClass` entries with
`BaseTextureName`, `HotX`/`HotY`, `ControllerTargeting`. Cursor art is reachable through the
in-game loose-texture path (`ui-atlas-modding.md`), so a custom cursor — e.g. for a new mod
hotkey command — is a real option.

### 5. Lobby option value lists are data

`CNCStartingUnits`, `CNCRATechLevels`, `CNCStartingCredits`, `CNCGameSpeedMods`,
`CNCUnitCountDefault`, `CNCOreRegrowth` and friends are `<Entry>` lists and defaults — the values
the lobby dropdowns *offer*. We can change what is on the menu (more starting units than 9,
different credit tiers) without touching the launcher.

### 6. Bonus-content gallery is data

`CNCRABONUSCONTENT.XML` / `CNCTDBONUSCONTENT.XML` — 87 entries each with `TitleTextID`,
`ThumbnailName`, `InfoTextID`, `Unlock`, `UnlockOnMissionCompletions`. The extras gallery is
therefore mod-editable in place (thumbnails via the loose texture path). Cosmetic, but it is a
player-facing surface nobody has used.

---

## Tier 2 — unknowns worth one cheap test each

- **Slash commands.** `SLASHCOMMANDS.XML` holds 203 `<Command>` entries — `SHOWVISIBILITY`,
  `SHOWSTRUCTURECOLLISION`, `ADDTACTICAL`, matchmaking/server debug — each with a `<Help>` text ID
  and a `<Permissions>` letter set (`SU`, `SQMu`, `MCQSu`, …). **If ClientG gates them on this
  data rather than on a build flag, relaxing a permission string turns on a debug tool.** Would be
  a diagnostic aid, not a player feature. Test: relax one command, see if it runs.
- **UI hint system.** `UIHINTS.XML` ships with every `UIHintTypeClass` commented out, each having
  `HintCaptionTextID`, `HintImage`, `HintCategory`. If the system is live in ClientG, it is a
  channel for player-facing pop-ups the DLL cannot otherwise reach.
- **`CNCRULES.XML` — a launcher-side difficulty table.** Carries `RulesTypeClass Name="TD"` and
  `Name="RA"`, both `network="server"`, with per-difficulty `Firepower` / `Groundspeed` /
  `Airspeed` / `BuildTime` / `Armor` / `ROF` / `Cost` / `RepairDelay` / `BuildDelay` /
  `BuildSlowdown` / `DestroyWalls` / `ContentScan`. Probably an unused server-build artifact —
  but see the decision below, because the same table exists on the live DLL side.

---

## Tier 3 — confirmed dead, do not re-chase

- **`AUDIO_FACTIONS.XML`'s `<MusicMap>` is not a route to music by faction**: see the field manual's
  [Music by faction, and the jukebox](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/music-by-faction-and-the-jukebox.md#how-the-launcher-picks-skirmish-music), How the launcher picks skirmish music. EA's
  comment there continues "since we need to account for each game and SFX asset mode (Classic or Remastered)". The
  file also defines `<SFXMap>` and `<SpeechMap>`, and only `Faction1` exists, empty. Music by faction ships through a
  launcher hook instead (`skirmish-music.md`).
- **`CNCTDSupportMegamaps` = false** looks like it unlocks big maps; it does not. TD-scoped, and
  it enables TD's 128×128 megamaps — the cap RA already runs at. It explains why TD's 64×64 build
  carries the same `MAX_EXPORT_CELLS (128*128)`. That negative stands, but the 128x128 export
  arrays are not the launcher's wall: InstanceServerG copies them, and the `megamaps-spike` branch
  patches that copy to reach 253x253 (`megamaps-feasibility.md`).
- **`CNCTDMaxPlayers` = 6** — "more than 6 players in skirmish/LAN for TD if a modded DLL supports
  it". TD-only. RA's 8 players is a separate setting among the lobby defaults,
  `CNCAllow8PlayersDefault`, and its stock value is false.
- **`AISKIRMISHPERSONALITIES.XML`** defines one personality (`Balanced`) pointing at a CLIPS
  expert-system file (`BalancedPersonality.clp`) that is not in the archive. Petroglyph's generic
  AI, not C&C's — our DLL is the AI. Not a lever.

---

## Dismissed by class (and why that is safe)

- **27 files are effectively empty** — the engine's generic systems that C&C does not use:
  `MISSIONOBJECTIVES`, `RADAREVENTTYPES`, `MOVIES`, `CAMPAIGNS`, `DIFFICULTYFILES`,
  `DAMAGETOATTRIBUTE`, `HITEFFECTS`, `SURFACEFX`, `PLAYERXPTABLE`, `EXPERIENCEAWARDTABLE`,
  `LOOTSETS`, `JUNKITEMFILES`, `PIRATEFORCETYPEFILES`, `TUTORIALTYPE`, `UIHINTS`,
  `ANIMATIONOVERRIDENAMES`, `SHADOWBLOBMATERIALS`, `STRUCTUREVOTERS`, `SPEECHEVENTS` and others.
  An empty registry is not a lever — but it is a useful negative: there is no hidden objective,
  radar-event, or XP system waiting to be switched on.
- **~30 post-FX step files** (`BLOOMFILTER`, `FXAA`, `TONEMAPHDR`, `VOLUMETRICFOGOFWAR*` …) are
  render-pipeline plumbing, plus chains like `ALLEFFECTSCHAIN_DO_NOT_USE`. Cosmetic-only and
  risky; not pursued.
- **~20 `EnumDefinition` files** (`DAMAGETYPE`, `PASSABILITYCLASSTYPE`, `UGCTAGTYPE` …) define
  engine enums the compiled client already knows. Editing an enum list does not create engine
  behaviour.
- **Tilesets / audio-event / localisation members** are content we already know how to reach via
  their own documented pipelines (`td-tile-hd-loose-art-investigation.md`,
  `td-audio-routing-recipe.md`, `faction-select-identity.md`).
- **Engine leftovers from other Petroglyph titles** — `LIGHTNINGEFFECTTYPES` names
  `Air_Elemental_Lightning` / `Fusion_Beam_*`, `CAMERAS.XML` is marked "no longer used",
  `LASERBEAMS.XML` says its custom-render fields are "no longer used". Present but inert for C&C.

---

## Appendix — the full member census

Generated from the extracted archive; grouped by class, largest first within each group. Files
named in the tiers above are the ones whose contents were read in full.

`scripts/`-side reproduction: extract with `meg_extract.py list|extract`, then profile.
The working copies live in the session scratchpad (`meg/`), not in the repo.

**other** (108)

- `INSTANCES` (395,081b, `<Instances>`)
- `SFXEVENTSLOCALIZED` (378,700b, `<LocalizedSFXEvents>`)
- `GUITEXTURESETS` (257,776b, `<TextureSets>`)
- `INPUTTRANSLATORCONFIGURATIONS` (211,184b, `<InputTranslatorConfigurations>`)
- `FACTIONS` (151,302b, `<ObjectTypeList>`)
- `GAMECONSTANTS` (128,407b, `<GameConstants>`)
- `OBJECTCLASSIFICATIONS` (127,881b, `<ObjectClassifications>`)
- `CNCMAPPREVIEWDATA` (122,996b, `<OuterTag>`)
- `MUSICEVENTS` (120,187b, `<MusicEvents>`)
- `CNCTDBONUSCONTENT` (72,603b, `<CNC_Tiberian_Dawn_Bonus_Content>`)
- `RABUILDABLES` (67,724b, `<ObjectTypeList>`)
- `CNCRABONUSCONTENT` (67,109b, `<CNC_Red_Alert_Bonus_Content>`)
- `CNCBUILDABLES` (62,982b, `<ObjectTypeList>`)
- `DEFAULTANIMTEMPLATE` (60,440b, `<AnimTemplateList>`)
- `MAPLANGUAGESET` (57,573b, `<ClickScriptLanguageSet>`)
- `SLASHCOMMANDS` (50,230b, `<CommandList>`)
- `OBJECTCLASSIFICATIONTEMPLATES` (45,892b, `<ObjectClassificationTemplates>`)
- `OBJECTSTATES` (43,816b, `<ObjectStates>`)
- `STRUCTUREANIMTEMPLATE` (34,806b, `<AnimTemplateList>`)
- `MOUSEPOINTERS` (31,437b, `<MousePointers>`)
- `CAMPAIGNMAPS` (29,810b, `<Maps>`)
- `EFFECTCLASSES` (28,963b, `<EffectClasses>`)
- `GRAPHICDETAILS` (28,035b, `<GraphicDetails>`)
- `MOUSEPOINTERSX2` (26,188b, `<MousePointers>`)
- `CAMERAS` (23,249b, `<Cameras>`)
- `LIGHTNINGEFFECTTYPES` (17,502b, `<LightningEffects>`)
- `WEATHERSCENARIOS` (16,189b, `<WeatherScenarios>`)
- `DISSOLVEEFFECTTYPES` (14,943b, `<DissolveEffects>`)
- `CNCRATEAMCOLORS` (14,920b, `<CNCRATeamColors>`)
- `WEATHERMODIFIERS` (14,429b, `<WeatherSystem>`)
- `FACTIONREPLAY` (13,996b, `<ObjectTypeList>`)
- `SHARED_RULES_CAMPAIGN_INSTANCEMONITORS` (13,826b, `<InstanceMonitor>`)
- `VMINSTRUCTIONS` (12,444b, `<ClickScriptLanguageSet>`)
- `GDI_MISSIONS` (11,817b, `<CampaignMissions>`)
- `VIBRATIONEVENTS` (9,844b, `<VibrationEvents>`)
- `TACTICALLODCONFIG` (9,239b, `<TacticalLODConfig>`)
- `RA_AFTERMATH_MISSIONS` (9,026b, `<CampaignMissions>`)
- `NOD_MISSIONS` (8,956b, `<CampaignMissions>`)
- `GAMEBUDGET` (8,552b, `<TargetStats>`)
- `FACTIONRANDOM` (8,308b, `<ObjectTypeList>`)
- `RA_CAMPAIGNMAPS` (8,265b, `<Maps>`)
- `TERRAINEDITORBUDGET` (8,124b, `<TargetStats>`)
- `CNCTDTEAMCOLORS` (7,816b, `<CNCTDTeamColors>`)
- `CNCRULES` (5,610b, `<CNCRules>`)
- `PUBLICPARTICLEBUFFERS` (5,542b, `<PublicParticleBuffers>`)
- `RA_ALLIES_MISSIONS` (5,279b, `<CampaignMissions>`)
- `LASERBEAMS` (5,020b, `<LaserBeams>`)
- `RA_USSR_MISSIONS` (4,540b, `<CampaignMissions>`)
- `AVATAR_AI` (4,137b, `<ObjectTypeList>`)
- `MODELSBUDGET` (4,059b, `<Budget>`)
- `COORDINATORCONFIG` (3,755b, `<InstanceCoordinator>`)
- `LENSFLARES` (3,412b, `<LensFlares>`)
- `PLAYERS` (3,097b, `<ObjectTypeList>`)
- `LODSETTINGS` (2,970b, `<LODSettings>`)
- `ROADS` (2,943b, `<Roads>`)
- `DYNAMICTRACKFX` (2,786b, `<DynamicTracks>`)
- `AVATAR_DEFAULT` (2,734b, `<ObjectTypeList>`)
- `TEXTURESCONFIGS` (2,625b, `<TexturesConfigs>`)
- `GAMEOBJECTFILES` (2,618b, `<Game_Object_Files>`)
- `RA_AFTERMATH` (2,615b, `<Campaigns>`)
- `HOLOGRAMEFFECTTYPES` (2,525b, `<HologramEffects>`)
- `UICINEMATICS` (2,485b, `<UICinematics>`)
- `GDI` (2,484b, `<Campaigns>`)
- `NOD` (2,062b, `<Campaigns>`)
- `CONSOLE_MISSIONS` (2,035b, `<CampaignMissions>`)
- `CONSOLE` (1,893b, `<Campaigns>`)
- `RADARMAP` (1,863b, `<RadarMap>`)
- `OUTLINEEFFECTTYPES` (1,731b, `<OutlineEffects>`)
- `ATTRIBUTES` (1,566b, `<Attributes>`)
- `STEALTHEFFECTTYPES` (1,516b, `<StealthEffects>`)
- `BUILDABLECATEGORIES` (1,442b, `<ObjectTypeList>`)
- `RA_ALLIES` (1,361b, `<Campaigns>`)
- `DIFFICULTYADJUSTMENTS` (1,320b, `<Difficulty_Adjustments>`)
- `FUNPARK_MISSIONS` (1,279b, `<CampaignMissions>`)
- `RA_USSR` (1,254b, `<Campaigns>`)
- `AVATAR_BASE` (1,233b, `<ObjectTypeList>`)
- `GUIEFFECTTYPES` (1,036b, `<Shaders>`)
- `GUIPARTICLESETS` (1,018b, `<ParticleSets>`)
- `ANT_MISSIONS` (983b, `<CampaignMissions>`)
- `LOGICALEVENTTYPES` (930b, `<LogicalEventTypes>`)
- `SERVER` (737b, `<Server>`)
- `SERVERCONFIG` (674b, `<Servers>`)
- `ANIMTEMPLATEFILES` (653b, `<AnimTemplateFiles>`)
- `SCALEFORMCONFIGURATION` (630b, `<ScaleformConfiguration>`)
- `SERVERPERSISTENCESETTINGS` (583b, `<InstanceCoordinator>`)
- `SHARDCOORDINATORPERSISTENCESETTINGS` (557b, `<InstanceCoordinator>`)
- `FUNPARK` (553b, `<Campaigns>`)
- `PROGRESSIVECAMPAIGNFILES` (499b, `<Campaign_Files>`)
- `PROGRESSIVECAMPAIGNMISSIONFILES` (489b, `<Campaign_Files>`)
- `EXTERNAL_OBJECTS` (480b, `<ObjectTypeList>`)
- `ANT` (461b, `<Campaigns>`)
- `HARDPOINTS` (439b, `<HardPointsFile>`)
- `AISKIRMISHPERSONALITIES` (399b, `<AI_Personalities>`)
- `GLOBALCOORDINATORPERSISTENCESETTINGS` (388b, `<InstanceCoordinator>`)
- `CLIENT` (270b, `<Client>`)
- `MODELBOUNDS` (268b, `<ModelBounds>`)
- `GENERAL_INSTANCEMONITORS` (248b, `<InstanceMonitor>`)
- `LANDUNITANIMTEMPLATE` (226b, `<AnimTemplateList>`)
- `INSTANCEMONITORFILES` (225b, `<Instance_Monitor_Files>`)
- `ENUMFILES` (223b, `<Enum_Files>`)
- `TANKANIMTEMPLATE` (216b, `<AnimTemplateList>`)
- `PASSABILITYCLASSTYPEDEFS` (191b, `<MovementClassManager>`)
- `PERSONALITYTYPEFILES` (183b, `<Personality_Type_Files>`)
- `SPEECHEVENTFILES` (178b, `<SpeechEvent_Files>`)
- `LEVELTABLEFILES` (169b, `<Level_Table_Files>`)
- `ATTRIBUTE_SYSTEM_FILES` (113b, `<AttributeSystemFiles>`)
- `MOUSEPOINTERFILESX2` (106b, `<MousePointerFiles>`)
- `MOUSEPOINTERFILES` (104b, `<MousePointerFiles>`)

**empty** (27)

- `DAMAGETOATTRIBUTE` (338,858b, `<DamageToArmor>`)
- `SHADOWBLOBMATERIALS` (14,525b, `<Shadow_Blob_Materials>`)
- `SURFACEFX` (2,420b, `<SurfaceEffects>`)
- `UIHINTS` (1,487b, `<UIHints>`)
- `ANIMATIONOVERRIDENAMES` (354b, `<AnimationOverrideNames>`)
- `SPEECHEVENTS` (161b, `<SpeechEvents>`)
- `EXPERIENCEAWARDTABLE` (122b, `<LevelTableList>`)
- `PLAYERXPTABLE` (120b, `<LevelTableList>`)
- `UNITTEMPLATEUPGRADEFILES` (109b, `<Unit_Template_Upgrade_Files>`)
- `DAMAGEGROUPINGTYPE` (105b, `<EnumDefinition>`)
- `TUTORIALTYPE` (101b, `<EnumDefinition>`)
- `HITEFFECTS` (94b, `<DamageHitEffects>`)
- `PIRATEFORCETYPEFILES` (93b, `<Personality_Type_Files>`)
- `PERSONALITYFILES` (87b, `<Personality_Files>`)
- `DIFFICULTYFILES` (85b, `<Difficulty_Files>`)
- `ACSTYPEFILES` (79b, `<ACS_Type_Files>`)
- `JUNKITEMFILES` (73b, `<Junk_Item_Files>`)
- `GAMEOBJECTTABLEFILES` (71b, `<Game_Object_Files>`)
- `MISSIONOBJECTIVES` (69b, `<MissionObjectives>`)
- `LOGICALEVENTMAPS` (64b, `<LogicalEventMap>`)
- `RADAREVENTTYPES` (61b, `<RadarEvents>`)
- `LOOTSETS` (60b, `<Loot_Set_Files>`)
- `CAMPAIGNS` (59b, `<Campaign_Files>`)
- `LOGICALEVENTVARIANTMAP` (52b, `<LogicalEventVariantMap>`)
- `MOVIES` (48b, `<Movies>`)
- `NULLCHAIN` (47b, `<PostFxs>`)
- `STRUCTUREVOTERS` (44b, `<Root>`)

**tileset** (20)

- `RA_UNITS` (2,275,605b, `<Tilesets>`)
- `TD_UNITS` (1,994,503b, `<Tilesets>`)
- `RA_TERRAIN_TEMPERATE` (809,717b, `<Tilesets>`)
- `RA_TERRAIN_SNOW` (796,536b, `<Tilesets>`)
- `TD_TERRAIN_DESERT` (479,564b, `<Tilesets>`)
- `TD_TERRAIN_WINTER` (407,123b, `<Tilesets>`)
- `TD_TERRAIN_TEMPERATE` (389,552b, `<Tilesets>`)
- `RA_STRUCTURES` (359,588b, `<Tilesets>`)
- `TD_VFX` (330,418b, `<Tilesets>`)
- `RA_VFX` (281,623b, `<Tilesets>`)
- `TD_STRUCTURES` (256,153b, `<Tilesets>`)
- `RA_TERRAIN_INTERIOR` (115,260b, `<Tilesets>`)
- `COMMON_VFX` (77,245b, `<Tilesets>`)
- `RA_TERRAIN_SHROUD` (9,808b, `<Tilesets>`)
- `COMMON_MISC` (7,310b, `<Tilesets>`)
- `COMMON_UI` (4,627b, `<Tilesets>`)
- `TD_RADARMAP` (3,183b, `<Tilesets>`)
- `TD_TERRAIN_SHROUD` (2,702b, `<Tilesets>`)
- `RA_RADARMAP` (2,309b, `<Tilesets>`)
- `TILESETS` (941b, `<TilesetFiles>`)

**audio** (21)

- `MOVIEAUDIOEVENTS_ENGLISH` (389,280b, `<Movies>`)
- `MOVIEAUDIOEVENTS_GERMAN` (388,822b, `<Movies>`)
- `MOVIEAUDIOEVENTS_FRENCH` (388,390b, `<Movies>`)
- `SFXEVENTSNONLOCALIZED` (193,954b, `<SFXEvents>`)
- `AUDIO_SYSTEM_CONSTANTS` (78,642b, `<AudioSystem>`)
- `SFXEVENTPRESETS` (26,416b, `<SFXEvents>`)
- `WEATHERAUDIO` (24,505b, `<WeatherAudio>`)
- `AUDIO_CONSTANTS` (7,181b, `<AudioSystemFile>`)
- `AUDIO_GUI` (6,782b, `<AudioSystemFile>`)
- `SFXEVENTS` (6,362b, `<SFXEvents>`)
- `AMBIENTSFXAUDIO` (4,033b, `<AmbientSFXAudio>`)
- `SFXEVENTSDEFAULT` (3,404b, `<SFXEvents>`)
- `AUDIO_SYSTEM_FILES` (1,960b, `<AudioSystemFiles>`)
- `AUDIO_ABILITIES` (1,363b, `<AudioSystemFile>`)
- `AUDIO_INSTANCES` (948b, `<AudioSystemFile>`)
- `AUDIO_HUD` (820b, `<AudioSystemFile>`)
- `AUDIO_FACTIONS` (704b, `<AudioSystemFile>`)
- `SFXEVENTFILES` (667b, `<SFXEvent_Files>`)
- `MOVIEAUDIOEVENTFILES_ENGLISH` (125b, `<MovieAudioEventFiles>`)
- `MOVIEAUDIOEVENTFILES_FRENCH` (124b, `<MovieAudioEventFiles>`)
- `MOVIEAUDIOEVENTFILES_GERMAN` (124b, `<MovieAudioEventFiles>`)

**enum** (18)

- `EFFECTCATEGORYTYPE` (688b, `<EnumDefinition>`)
- `PASSABILITYCLASSTYPE` (470b, `<EnumDefinition>`)
- `OBJECTWEATHERCATEGORYTYPE` (367b, `<EnumDefinition>`)
- `VENDORCATEGORYTYPE` (349b, `<EnumDefinition>`)
- `DISCIPLINETYPE` (323b, `<EnumDefinition>`)
- `UNITTEMPLATECHASSISTYPE` (303b, `<EnumDefinition>`)
- `UNITTEMPLATETECHBRANCH` (267b, `<EnumDefinition>`)
- `ABILITYCATEGORYTYPE` (255b, `<EnumDefinition>`)
- `UGCTAGTYPE` (247b, `<EnumDefinition>`)
- `ITEMTIMERTYPE` (230b, `<EnumDefinition>`)
- `AIUNITCLASSTYPE` (207b, `<EnumDefinition>`)
- `EFFECTDURATIONMODIFIERTYPE` (198b, `<EnumDefinition>`)
- `OBJECTSTATECATEGORYTYPE` (190b, `<EnumDefinition>`)
- `ABILITYSUBCATEGORYTYPE` (170b, `<EnumDefinition>`)
- `UNIQUEEQUIPCATEGORYTYPE` (161b, `<EnumDefinition>`)
- `DAMAGETYPE` (156b, `<EnumDefinition>`)
- `VENDORSUPERCATEGORYTYPE` (135b, `<EnumDefinition>`)
- `MODELANIMSETTYPE` (119b, `<EnumDefinition>`)

**postfx** (36)

- `DEFAULTCHAIN` (16,640b, `<PostFxs>`)
- `DEFAULTCHAINNOFOW` (13,962b, `<PostFxs>`)
- `ALLEFFECTSCHAIN_DO_NOT_USE` (8,961b, `<PostFxs>`)
- `VOLUMETRICFOGOFWARUNLIT` (1,583b, `<PostFxStep>`)
- `VOLUMETRICFOGOFWAR` (1,461b, `<PostFxStep>`)
- `NOPOSTFXCHAINHDR` (1,070b, `<PostFxs>`)
- `CNCCHAIN` (927b, `<PostFxs>`)
- `LIGHTSCATTERING` (482b, `<PostFxStep>`)
- `DOFCOMPUTEDEPTHBLUR` (212b, `<PostFxStep>`)
- `SATURATIONCONTROL` (211b, `<PostFxStep>`)
- `HEATDISTORTION` (208b, `<PostFxStep>`)
- `COLORCORRECTION` (205b, `<PostFxStep>`)
- `BLOOMFILTER` (202b, `<PostFxStep>`)
- `COLORFILTER` (202b, `<PostFxStep>`)
- `BRIGHTFILTER` (201b, `<PostFxStep>`)
- `TONEMAPHDR` (195b, `<PostFxStep>`)
- `ADVANCEDCOLORFILTER` (177b, `<PostFxStep>`)
- `BLOOMCOMBINETONEMAPHDR` (172b, `<PostFxStep>`)
- `BLOOMCOMBINEHDR` (164b, `<PostFxStep>`)
- `BLOOMCOMBINE` (160b, `<PostFxStep>`)
- `CONTRASTCONTROL` (158b, `<PostFxStep>`)
- `VOLUMETRICFOGOFWARGBLURHORIZONTALMASKTEX` (137b, `<PostFxStep>`)
- `VOLUMETRICFOGOFWARGBLURVERTICALMASKTEX` (135b, `<PostFxStep>`)
- `VOLUMETRICFOGOFWARGBLUR3X3MASKTEX` (130b, `<PostFxStep>`)
- `STRETCHRECTOFFSCREENCOMPOSITION` (112b, `<PostFxStep>`)
- `STRETCHRECTALPHABLEND` (101b, `<PostFxStep>`)
- `GBLURHORIZONTAL` (94b, `<PostFxStep>`)
- `GBLURVERTICAL` (92b, `<PostFxStep>`)
- `DOWNSAMPLE2X` (91b, `<PostFxStep>`)
- `STRETCHRECT` (90b, `<PostFxStep>`)
- `DOFCOMBINE` (89b, `<PostFxStep>`)
- `DOFGBLUR` (87b, `<PostFxStep>`)
- `ADDIRT0` (86b, `<PostFxStep>`)
- `ADDIRT1` (86b, `<PostFxStep>`)
- `GBLUR` (83b, `<PostFxStep>`)
- `FXAA` (82b, `<PostFxStep>`)
