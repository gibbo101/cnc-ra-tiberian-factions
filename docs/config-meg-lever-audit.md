# CONFIG.MEG lever audit — what the launcher's own data unblocks

**Written 2026-07-21.** Prompted by the classic-graphics lockout: a wall we had spent four
DLL-side attempts on turned out to be one `GAMECONSTANTS.XML` constant EA shipped for mods in
2020. This is the sweep that asks what else is sitting in launcher data that we wrote off.

**Standing rule this establishes:** a wall proven on the *code* side is not proven on the *data*
side. Before declaring a launcher behaviour impossible, grep CONFIG.MEG.

**Coverage.** All 230 non-tilepatch XML members were extracted and profiled (size, root element,
element census, keyword scan for `TBD` / `not used` / `no longer used` / `Community-requested` /
`for Modding`). Everything plausibly behavioural was then read. Whole classes were dismissed on
their profile, and that dismissal is itself a finding — see "Dismissed by class". Companion:
`config-meg-mod-delivery.md` (how a mod ships its own CONFIG.MEG), `mix-file-format.md`
(`meg_pack.py`, the same-size rule).

**The constraint on everything below:** a mod can replace a member's *contents* at its exact
byte length. It cannot add a member, remove one, or change any size — offsets resolve against
the base archive. So every lever here is "rewrite in place, byte-for-byte", and growth must be
paid for from padding or comment text inside the same file.

---

## ⭐ Delivery: `GameConstants_Mod.xml` beats editing the member (2026-07-21)

`ClientG.exe` contains the literal `\XML\GameConstants_Mod.xml` and merges that file over the
base GameConstants. It is **additive**, so it needs no same-size juggling and no CONFIG.MEG
repack at all — a mod ships a dozen lines in `Data/XML/`. `overwrite="true"` on an element
replaces a list rather than appending to it. Documented by Kushan (ppmforums.com/topic-54809,
2020) and used by Vanilla Conquer's TD sample to switch on megamaps.

**Our constants moved to it** (classic-graphics lockout, mod hotkeys, the Unholy Alliance
default, CFE's zoom factors), retiring a 128KB same-size rewrite plus a repack of that member.
Fewer moving parts, and one less member that a rebuild can silently clobber — the failure mode
that cost the faction names earlier the same day.

**It is the only `_Mod` overlay.** No `InputTranslatorConfigurations_Mod.xml` exists in the
binary, which is the independent confirmation that mod hotkey *bindings* cannot be shipped and
must be bound by the player. See `todo.md`.

## Tier 1 — actionable levers

### 1. Mod hotkey commands (the big one; chain complete, untested)

EA built a mod hotkey path and left the hook in our own source. We have never connected it:

1. **`GAMECONSTANTS.XML`** — `CNCEnableModHotKeyGameCommands`, commented *"Community-requested
   Mod option so that players can have customized mod hotkey commands"*.
2. **`INPUTTRANSLATORCONFIGURATIONS.XML`** — four prepared bindings
   `GAME_COMMAND_CNC_MOD_COMMAND_1..4` in the `TACTICAL_CNC` context, each with an empty
   `<Key></Key> <!-- TBD -->`. Format is `<Key>VIRTUAL_KEY_F3</Key>`, as the bookmark commands
   directly above them use.
3. **`redalert/dllinterface.cpp` ~5374** — `INPUT_REQUEST_MOD_GAME_COMMAND_1..4_AT_POSITION`
   cases already exist, resolve the mouse position to a `CELL`, and hit EA's placeholder:
   `// TBD: For our ever-awesome Community Modders!` with a suggested
   `PlayerPtr->Handle_Mod_Game_Command(cell, index)`.

So the launcher will deliver four modder-defined keypresses **with a map cell**; only our handler
is missing. **First target: the MCV deploy hotkey**, currently a shipped known limitation.

**Test the binding half first.** Our edits to `INPUTTRANSLATORCONFIGURATIONS.XML` have never been
proven to take effect — the one attempt rebound the classic-mode spacebar and failed, which is
consistent with that key being client-hardcoded but is not evidence either way. Bind one key, log
from the DLL case, confirm arrival, then build.

### 2. Campaigns are a faction-bound data layer

`PROGRESSIVECAMPAIGNFILES.XML` is the live campaign registry (the similarly-named `CAMPAIGNS.XML`
is empty). It lists `Campaigns/GDI.xml`, `NOD.xml`, `RA_Allies.xml`, `RA_USSR.xml`,
`RA_Aftermath.xml`, `Ant.xml`, `Funpark.xml`, `Console.xml` — **and a commented-out
`RA_Counterstrike.xml`**, so EA folded a campaign out of this list by editing data.

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
reads like one. `FACTIONS.XML` defines exactly 11 faction objects: `Faction1` = TD GDI (icon
`_00`), `Faction2` = TD Nod (`_01`), `Faction3`–`Faction10` = the eight RA countries (flag icons
`_03`–`_10`), plus `Faction_Funpark`. So `Faction6` is an ordinary RA country slot that the Ant
campaign declares itself against — the same mechanism our GDI and Nod use, riding `Faction3` and
`Faction10` with their icons repointed to `_00`/`_01`. The binding is one-directional
(campaign names a faction), and none of the faction entries carry buildable structure or unit
lists — those are all empty, because the tech trees live in our DLL.

**Two things follow.** First, if we ever repoint `ANT.XML`, bind it to `Faction3` or `Faction10`
so a GDI/Nod campaign sits on the GDI/Nod faction slot instead of a leftover country. Second,
`Faction_Funpark` is an eleventh entry with a **non-numeric name**, which means the faction table
is a data list rather than a fixed `Faction1..10` enum. That is the only crack in the 5th-faction
wall this file offers, and it is a small one: it concerns the *launcher's* faction table, while
the real blocker is the DLL's hardcoded `HOUSE_*` enum (workspace CLAUDE.md, "houses are
hardcoded") plus the lobby picker's fixed slot count (`bui-front-end-modding.md`, W2 DEAD).
**`<CoopCampaignType>` is a cut feature, not a lever.** Every faction carries the field, empty,
as a sibling of `<CampaignType>`. `ClientG.exe` has the whole co-op campaign implementation
compiled in (`CoopCampaignMenuImplementationClass`, `Button_CoopCampaign`,
`Host_Coop_Campaign_Lobby(...)` with match-settings/ready/launch RPCs, per-mission star counts)
— but **no co-op data ships in either archive**: `UI_CampaignMenu_CoOp` is absent from our
CONFIG.MEG and from the pristine base, and no co-op campaign is defined. Since a mod cannot add
a member, the screen can never exist; and the hosting path runs through EA's online coordinator
while mods load in LAN only. Recorded in full in `coop-missions-design.md`.

**Why it matters:** our campaign plan hijacks Counterstrike/Aftermath *mission slots*
(`campaign-tabs-research.md`). This is the layer above. We cannot add a campaign file, but
`ANT.XML` is 461 bytes and `FUNPARK.XML` 553 — **repointing a low-value campaign may be a
cleaner hijack than borrowing Aftermath slots**, and it comes with its own faction binding.
Unknown: whether ClientG enumerates campaigns from this data at runtime or from a compiled list,
and whether campaign-select can surface the result (`bui-front-end-modding.md` says screen
*structure* is fixed). One test settles it: rewrite `ANT.XML`'s mission list, see if the Ant
campaign changes.

### 3. Team colours are data

`CNCRATEAMCOLORS.XML` (14.9 KB) and `CNCTDTEAMCOLORS.XML` define per-country colour transforms
(`LowerBounds`/`UpperBounds`/`HSVShift`/`InputLevels` against `TeamColorLarge.tga`), keyed by
country name — `SPAIN`, etc. Since GDI/Nod ride country slots, **their in-game colour identity is
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

- **`AUDIO_FACTIONS.XML` independently confirms the per-faction music finding.** It defines
  `<SFXMap>`, `<MusicMap>`, `<SpeechMap>` per faction and carries EA's own comment: *"We are not
  using these for C&C TD / RA, since we need to account for each game and SFX asset mode (Classic
  or Remastered)"*. Only `Faction1` exists and it is empty. `faction-music-feasibility.md`'s
  tested-dead conclusion now has a documentary reason behind it.
- **`CNCTDSupportMegamaps` = false** looks like it unlocks big maps; it does not. TD-scoped, and
  it enables TD's 128×128 megamaps — the cap RA already runs at. It explains why TD's 64×64 build
  carries the same `MAX_EXPORT_CELLS (128*128)`, which is the evidence `megamaps-feasibility.md`
  uses to prove the buffer belongs to the launcher. That negative stands.
- **`CNCTDMaxPlayers` = 6** — "more than 6 players in skirmish/LAN for TD if a modded DLL supports
  it". TD-only; RA already runs 8 (`CNCAllow8PlayersDefault`).
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
