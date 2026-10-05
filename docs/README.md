# Docs

**Status:** Reference. The index of every doc in this folder, and the rules they are written to.

Start with `td-port-playbook.md` for any port, `launcher-vs-dll-ownership.md` before calling a
launcher behaviour impossible, `launcher-render-contracts.md` before shipping art, and `todo.md` /
`known-issues.md` for what is open.

## Rules

1. **Four kinds.** Every doc is one of:
   - **Reference**: how something works as it ships.
   - **Design**: planned or partly built.
   - **Parked**: taken out of the mod, kept for revival.
   - **Tracker**: `todo.md` and `known-issues.md`.
2. **A status line under the title.** The first line under the `#` title is
   `**Status:** <kind>`, then what ships and since which release. An optional `**Open:**` line
   lists what is left. Update both whenever the doc's subject changes.
3. **Write what ships, not how it got there.** No session diaries, handover docs or blocks telling
   the next session where to resume. When something turns out wrong, rewrite or delete the text; don't append a correction.
   The history is in git.
4. **State decisions, not who made them or when.** No personal names, no "decided on <date>".
5. **Links:** a doc is cited as `` `<name>.md` `` and must exist. No links into Claude's memory files and no star markers.
6. **Trackers stay short.** `todo.md` stays under 300 lines: finished work is deleted once its
   lessons are in a topic doc. A fixed bug is deleted from `known-issues.md`.
7. **Close out the docs:**
   - **At a branch merge**, update every doc the branch's work touches.
   - **At a release**, review each doc changed since the last tag
     (`git diff --stat vX.Y.Z -- docs/`), and check that its status line names the release.
8. **Every doc is listed below.** Subfolders hold data and are not checked.

`scripts/docs_check.py` enforces rules 2, 4, 5, 6 and 8, plus resume blocks and correction
sections, and `package-for-workshop.sh` runs it.

## Index

### Trackers
- `todo.md` — open work and the backlog.
- `known-issues.md` — open bugs and player-facing limitations.
- `code-tidy.md` — the code hygiene plan: the dead-code pass, comments left in branch ranges, phase 2.

### Porting TD units and buildings
- `td-port-playbook.md` — read first: architecture, recipe, every trap so far.
- `td-building-separation-recipe.md` — a TD building as its own `STRUCT_TDxxxx` type.
- `td-infantry-port-recipe.md` — the infantry pipeline.
- `td-vehicle-port-recipe.md` — the vehicle pipeline.
- `catalogue.md` — TD-source stats for every TD building.
- `naval-and-air-units.md` — GDI and Nod fleets, the A-10, the support powers, 3D ship art.
- `cargo-plane-port.md` — the Nod Airstrip's cargo-plane delivery.
- `td-atwr-deep-dive.md` — the Advanced Guard Tower.
- `td-sam-deep-dive.md` — the SAM site.
- `td-obli-verification.md` — the Obelisk of Light.
- `td-gtwr-gun-verification.md` — the Guard Tower and Gun Turret.
- `td-tier1-verification.md` — power plants, barracks, silo.
- `td-mlrs-deep-dive.md` — the MLRS and SSM Launcher.
- `td-attack-heli-deep-dive.md` — the Orca and Apache.

### Tiberian Sun and other eras
- `ts-gdi-faction.md` — TS GDI as the fifth faction; TS Nod and the multi-era ceiling.
- `ts-gdi-tree-plan.md` — every TS GDI entity, the engine facts and the open queue.
- `ts-asset-import-spike.md` — the TS asset pipeline: extraction, voxel renders, SHPs.
- `emp-cannon-design.md` — the EMP Pulse Cannon.
- `firestorm-design.md` — the Firestorm Defense.
- `subterranean-design.md` — the subterranean units.
- `stealth-generator-spec.md` — the Nod Stealth Generator.
- `cnc3-to-remastered-sprites.md` — C&C3 units as HD sprites.
- `asset-packs.md` — the TS, RA2 and C&C3 asset packs.

### Art and rendering
- `launcher-render-contracts.md` — how the launcher draws art; house rules for TS art.
- `td-tile-hd-loose-art-investigation.md` — TD terrain tiles in HD.
- `theatre-desert-feasibility.md` — HD desert in the interior theatre slot.
- `classic-mode-palette-remap.md` — classic graphics mode, locked out.
- `tiberium-ecosystem.md` — Tiberium, blossom trees, infantry damage and Visceroids.

### Audio
- `td-audio-routing-recipe.md` — routing a sound from the DLL to the launcher; sample formats.
- `building-sound-routing.md` — TD building, credit and UI sounds for GDI and Nod.
- `eva-ram-patch-spike.md` — EVA lines that follow the faction.
- `faction-music-feasibility.md` — skirmish and menu music; why per-faction music is dead.

### Launcher and front end
- `launcher-vs-dll-ownership.md` — the launcher/DLL boundary map.
- `config-meg-mod-delivery.md` — the mod's own CONFIG.MEG.
- `config-meg-lever-audit.md` — CONFIG.MEG data levers: in use, untried, dead.
- `bui-front-end-modding.md` — editing the `.bui` screens.
- `ui-atlas-modding.md` — the UI atlas.
- `faction-select-identity.md` — the lobby picker, HUD scenes and `ModText.csv` names.
- `radar-crest-ram-spike.md` — the per-faction radar crest.
- `main-menu-restyle-guide.md` — the main-menu restyle, written for other modders.
- `lobby-difficulty-ram-spike.md` — reading lobby difficulty from ClientG.
- `lobby-ambiguity-findings.md` — telling a stale lobby copy from the live one.
- `megamaps-feasibility.md` — why maps can't grow past 128x128.
- `mix-file-format.md` — the MIX and MEG formats and tools.

### AI, pathfinding and economy
- `ai-upgrade-plan.md` — the AI milestone: what shipped and what is left.
- `ai-improvements.md` — the AI problem inventory.
- `path-failure-livelock-design.md` — units retrying a doomed path.
- `chokepoint-reservation-design.md` — units queuing at a chokepoint.
- `harvester-recovery-design.md` — harvesters stuck in walled fields.
- `harvester-docking-rework-plan.md` — harvester docking across factions.
- `cfe-port-plan.md` — the CFE Patch Redux features ported.

### Balance
- `balance-deep-dive.md` — the stat audit and the playtest log.

### Maps, campaign and co-op
- `official-map-hybrids.md` — official maps as Tiberium/Ore hybrids.
- `official-map-hybrids-list.md` — the generated list of every map.
- `td-skirmish-map-import.md` — the converted TD maps (parked).
- `campaign-tabs-research.md` — the Mission Select pipeline and hijacked slots.
- `gdi-nod-campaign-story.md` — the GDI and Nod campaign story.
- `coop-missions-design.md` — co-op missions.

### Release
- `workshop-publish-runbook.md` — publishing the Workshop item and the asset packs.
- `moddb-page-copy.md` — the ModDB page text.
