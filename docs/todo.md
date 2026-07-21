# TODO / backlog

Running list of things to do. Bugs/limitations live in `known-issues.md`; this is for chores,
maintenance, and queued tasks. Newest at top.

---

## ⭐ 2026-07-21 (evening) — AI teams VERIFIED, per-slot difficulty ROOT-CAUSED AND FIXED

Four desktop runs, Docklands, human + 3 AI. **All changes UNCOMMITTED, awaiting Luke's review.**

**1. AI lobby teams work. Proven, not inferred.** A new `TEAMS` diagnostic dumps each slot's
resolved ally mask after the `Make_Ally` pass (`dllinterface.cpp`, end of the team loop). Lobby
Team 1/Team 1/Team 2/Team 2 produced:

```
TEAMS slot=0 house=H12 team=0 allyslots=03      <- human + AIPLAYER1
TEAMS slot=1 house=H13 team=0 allyslots=03
TEAMS slot=2 house=H14 team=1 allyslots=0c      <- AIPLAYER2 + AIPLAYER3
TEAMS slot=3 house=H15 team=1 allyslots=0c
```

Lobby "Team N" arrives as `Team = N-1`; pairing is exact and mutual. `AllyFlags` in
`CNCPlayerInfoStruct` is always 0 and carries nothing — `Team` is the whole channel. The
lobby also has **no "no team" state**: every slot defaults to its own distinct team
(Team 1..8 or RANDOM), so the "everyone accidentally allied" failure mode cannot arise.

**2. THE PER-SLOT DIFFICULTY BUG — FOUND AND FIXED.** `+0x50` is **ZERO-based**
(AIPLAYER1 reads `slot=0`), but the validator's range gate was `slot < 1`. Since validation
stops at the first bad record and a candidate must cover the whole roster, the first record
being rejected threw away the entire array. Evidence, the record sitting there correct and
discarded:

```
LOBBYREC k=0 n=1 slot=0 diff=2 color=1 house=4 expect_color=1 -> REJECT range
LOBBYSCAN frame=0 procs=1/1 sighits=3 best_count=0 ambiguous=0 roster=0000000e
```

Fix = `slot < 1` becomes `slot < 0`. One character of intent, and the same lobby now reads
first scan, frame 0, no retries, with a colour deliberately changed to break slot order and
with mixed GDI/Nod/Allied factions:

```
HELLO IM H13 (ActLike=8) IN MEDIUM MODE (IQ=4) [slot 1]
HELLO IM H14 (ActLike=9) IN EASY   MODE (IQ=3) [slot 2]
HELLO IM H15 (ActLike=1) IN HARD   MODE (IQ=5) [slot 3]
ram_slots=3 s1=2 s2=1 s3=3
```

**Why it looked "unreliable" rather than broken.** With ONE AI the roster is a single record,
and a lobby whose only AI sat at a non-zero index passed the `>= 1` floor, so it worked. Add
AIs, or put an AI first, and it fails. That is DCJD's intermittency exactly.

**Corrections to the offset map** (`dllinterface.cpp` header comment updated):
- `+0x50` is zero-based AND not a usable identity: the three records read `slot = 0, 1, 1`.
  Range-check it, never key off it. This is the same trap as the old `slot == slot2` test.
- `+0x68` is the lobby colour (DCJD, confirmed here) and is the only reliable identity key.
- `+0x54` is **NOT** dependably the house. All-Soviet lobby: all three read 4. Mixed
  GDI/Nod/Allied lobby: 2 / 9 / 3. Stays logged-only; do not promote it to a validator.

**3. Unholy Alliance works.** Mode is a real fourth entry in the lobby's Mode dropdown
(Bases On - Destroy Structures / Bases On - Destroy All / Bases Off / Unholy Alliance), the
MASTERTEXTFILE relabel shows in both the summary panel and the dropdown, and **bases are ON**:
four MCVs spawned for the human, and the three AIs each deployed a yard of a faction other
than their own (`AFACT#0` for the GDI AI, `SFACT#2` for Nod, `TDNFACT#3` for Allied), so the
AI got its quartet too. The open question from the design note is closed.

**New diagnostics added (all `TF_DEV_BUILD`-gated, compile out of release):** `TEAMS`,
`LOBBYREC` (per-record dump with the rejecting gate named), `LOBBYSCAN` (per-scan outcome:
processes opened, signature hits, best_count, ambiguous, roster mask). The old failure was
invisible because a failed re-scan logged nothing at all; `LOBBYSCAN` now always logs.

**4. AI never built ANY air production — live since v4.0.0, now fixed.** Four AIs over ~33,000
frames built zero helipads and zero airstrips, so no house ever fielded a helicopter or a
plane. Not a prerequisite fault and **not** caused by the faction separation: each faction's
own pad was correctly offered and no foreign pad ever appeared. `7ee075e` (in `v4.0.0`) set
both the helipad and airstrip choices to `URGENCY_LOW` to stop air burying the war factory. But
a pick resolves among the highest urgency present, and power/refinery/defence keep a
`URGENCY_MEDIUM` candidate available indefinitely, so LOW is not deprioritised, it is
unreachable. Fix = escalate rather than demote: hold at LOW until `tf_economy_ready` (the
existing two-refineries-plus-war-factory predicate already computed in `AI_Building`), then
MEDIUM. Applied to both the helipad and airstrip blocks; the enemy-air count cap is untouched,
so the AI still only matches the strongest air opponent. **Built and deployed, NOT yet verified
in a match** — first run should confirm all four factions reach a pad and field aircraft, and
that nobody builds four pads before a war factory again.

**Still to do on the 4.1 test pass:** the faction-split AI items are NOT yet verified in a
clean run — Unholy Alliance was left on, which hands every AI all four trees and makes "does
the AI build its own faction's war factory / helipad" unreadable. Re-run on **Bases On -
Destroy All** for: AI builds own-faction WF + helipad and fields helicopters, (d) helipad
behaviour in play, and the stock-campaign regression check. The prereq scoping matrix was
audited statically this session and is clean against the locked policy (every production-token
equivalence in `Can_Build` is `own &`-scoped; only power/refinery/repair cross factions; the
legacy shared `HPAD`/`TDHPAD` are session-gated to campaign at `house.cpp:1025`).

---

## ⭐ NEXT SESSION: v4.1.0 release (decided by Luke 2026-07-20, ship after a testing pass)

**The release story: "the groundwork update" — pre-AI-milestone foundations with a little AI
thrown in.** 96 commits since v4.0.0. Headline content: separated tech trees (W2 b2/b3/(c)/(d):
per-faction construction yards, MCVs, war factories, helipads; capture carries the full tree),
the locked prerequisite policy (shared low-tier infrastructure, faction-identity everything
else, dome ≠ TDHQ), owner-set badges on ALL 126 buildable cameos (mod-logo emblems; shared
entries show every owning faction), the faction-block sidebar sort (shared first, then
Allied/Soviet/GDI/Nod, tech-ordered), per-slot AI lobby difficulty incl. LAN (and the
mid-rebuild read bug that made it fall back to all-Hard after the first match), AI Phase 0/1
fixes (blind-scout dispatcher, temple starvation, economy gates, harvester idle-home), the A*
heap + expansion budget, the Stealth Generator work, and **classic graphics now locked out**
so the HD-only mod can no longer be dropped into a renderer its content has no art for.

**Before shipping (test pass):** (d) helipad behaviour in play (free heli per pad, universal
landing), the prereq scoping matrix (each faction's defenses/AA need their own chain), AI
still builds faction WFs + pads and fields helicopters, one stock-campaign regression check
(vanilla MCV/WEAP/HPAD present, no faction types visible).

**Release steps** (per workspace CLAUDE.md): ccmod.json high=4 low=10; `## [4.1.0]` CHANGELOG
section; commit; `package-for-workshop.sh` (TF_DEV_BUILD=0 — dev cheats
compile out); Workshop publish per `workshop-publish-runbook.md` (restart Steam first);
GitHub release + tag v4.1.0; post-release local bump to 4.1.1.
**Don't forget:** credit Bast75 + xXMini FrankiXx in the Workshop acknowledgments (AI Phase 0
ideas); update Workshop "Known limitations" — the deploy hotkey is now lost for ALL four
factions in skirmish (mouse self-click deploys); no em dashes in any user-facing copy.

---

## ⭐ Mod hotkeys — handler WORKS; delivery of a default binding UNSOLVED. Investigate again before 4.1 ships (Luke, 2026-07-21)

**Proven end to end (2026-07-21):** `CNCEnableModHotKeyGameCommands` True exposes Mod Command
1-4 in Options > Controls; a player-bound key reaches
`INPUT_REQUEST_MOD_GAME_COMMAND_1_AT_POSITION` in `dllinterface.cpp` with a map cell; our
handler acted (`MOD_COMMAND_1 frame=110 selected=1 deployed=1`). The handler is deliberately
generic -- it asks each selected object for its own self-action and acts only on ACTION_SELF,
so MCVs deploy, APCs / transports / Chinooks unload, infantry (ACTION_NONE) and factories
(ACTION_TOGGLE_PRIMARY) are skipped, and future deployables are covered for free.

**The wall: we cannot ship a default binding.** Measured, in this order, all failures:
- binding written into `INPUTTRANSLATORCONFIGURATIONS.XML` inside the mod's CONFIG.MEG
- the same file shipped loose in `Data/XML/` (the path that works for GameConstants)
- after Options > Controls "Restore Defaults" (restores the client's compiled defaults)
- on a **freshly created profile** (settings .bin moved aside) -- still empty
Our *unbind* of the launcher's own deploy command was ignored too, which is the proof the
client reads none of it: the deploy key stayed on backslash (`#` on a UK layout) throughout.

**Independently confirmed as by-design.** Kushan's PPM guide (ppmforums.com/topic-54809, 2020)
describes exactly this: enable via `GameConstants_Mod.xml`, then *"if you just want to bind some
commands in the bindings screen, they'll be sent through as
INPUT_REQUEST_MOD_GAME_COMMAND_x_AT_POSITION"*. Player-bound is the intended flow.

**Shipped state:** the constant and the handler ship; the input-config edits do NOT (reverted in
both the MEG and loose, so nobody's deploy key is touched by a dormant unbind).

**Remaining route to investigate before release:** write the binding into
`Player_RA_settings_1.bin` (ChunkFile+zlib TLV, partly decoded by the difficulty spike). A clean
unbound profile was created and discarded during testing -- recreate it, bind one command, and
diff the two files to find the encoding. Caveats to weigh: our DLL only runs during a match, so
a write would apply from the *next* launch; the file is Steam Cloud synced; and corrupting a
player's settings is a worse outcome than a one-time manual bind. Fallback if it is not clean:
a one-off in-game message at first match telling the player to bind Mod Command 1 (people do
read what is on screen mid-game, unlike a Workshop page).

Audit of the launcher's own data (`docs/config-meg-lever-audit.md`, written after the
classic-graphics lockout) found EA's mod hotkey path fully built and never connected:
`CNCEnableModHotKeyGameCommands` → four prepared `GAME_COMMAND_CNC_MOD_COMMAND_1..4` bindings
with empty `<Key></Key>` slots in `INPUTTRANSLATORCONFIGURATIONS.XML` (CONFIG.MEG, which we
already repack) → `INPUT_REQUEST_MOD_GAME_COMMAND_n_AT_POSITION` cases sitting in
`dllinterface.cpp` ~5374 with EA's own `// TBD: For our ever-awesome Community Modders!`
placeholder and a suggested `Handle_Mod_Game_Command(cell, index)`. The launcher hands us the
key press **and the map cell**.

**First target: the MCV deploy hotkey**, currently a shipped known limitation (lost for all four
factions; players click the MCV to deploy). Then any other command wanting a key.

**Test the binding half FIRST** — our edits to `INPUTTRANSLATORCONFIGURATIONS.XML` have never
been proven to take effect (the one attempt, rebinding the classic-mode spacebar, failed; that
key is client-hardcoded, so it is not evidence either way). Bind one key to command 1, log from
the DLL case, confirm the press arrives, and only then build a real handler.

**The rest of the sweep** (all 230 CONFIG.MEG XML members profiled): `docs/config-meg-lever-audit.md`.
Other actionable levers found — campaigns are a faction-bound data layer (`ANT.XML` at 461 bytes
may be a cleaner hijack than borrowing Aftermath mission slots), team colours, mouse cursors,
lobby dropdown value lists, the bonus-content gallery. Three cheap unknowns queued there too
(slash-command permissions, the UI hint system, whether `CNCRULES.XML`'s launcher-side difficulty
multiplier table is consulted at all).

## Faction-agnostic AI + the TS easter-egg tree (Luke, 2026-07-21 — designed, not started)

Two linked ideas from the AI discussion, both documented rather than built:

- **Faction-agnostic base builder with a home-faction weight** → `ai-upgrade-plan.md` §W2.9.
  The AI currently only ever builds its own lineage, so **captured factories are invisible to
  it today** — a live bug, not just an Unholy Alliance gap. Unit/infantry/aircraft selection is
  already capability-filtered, so the work is the building side: aggregate role counts across
  all lineages (miss one → four barracks), then weight the home tree ahead of the rest.
- **TS tech tree as an ownership-gated easter egg** → `ts-factions-feasibility.md`. A rare crate
  drops a TS MCV; deploying it unlocks the TS roster for whoever found it, any side. Needs **no
  faction, no house, no picker slot** — the yard is the gate. Most of the machinery already
  ships. Only lands as a *tree* worth having once the AI above can see it.

## Flatten the difficulty stat multipliers — DECIDED (Luke, 2026-07-21), do it with the campaign work

Difficulty is meant to be behavioural (IQ, timing, aggression), never firepower/armour/cost
biases — see `feedback-difficulty-philosophy`. The stat-multiplier layer still exists and
contradicts that, so it gets knocked down when campaign work starts (campaigns are where the
difficulty picker is actually player-facing).

**The live lever is our own `CCDATA/rules.ini`,** whose `[Easy]` / `[Normal]` / `[Difficult]`
sections the DLL reads into `Rule.Diff[]` — currently the stock spread (`[Easy]` Firepower 1.2 /
Armor 1.2 / ROF .8 / Cost .8 / BuildTime .8, `[Difficult]` the mirror). `CNCRULES.XML` in
CONFIG.MEG holds the same table launcher-side (`network="server"`) and is probably an unused
server-build artifact; flatten it too if it turns out to be consulted.

**Check while doing it:** `CNC_Set_Difficulty` currently assigns `Scen.CDifficulty = diff`
alongside the per-house IQ. If that selection feeds `Rule.Diff[]` at any point, the per-slot
lobby difficulty work is already pulling stat multipliers in through the back door, which nobody
has verified either way.

## "Unholy Alliance" mode — BUILT 2026-07-21, awaiting a verification pass

Every player (AI included) starts with one MCV of all four factions, each deploying its own
faction's yard and tree. Carried by the lobby's Capture the Flag game type, relabelled in
MASTERTEXTFILE; `TF_UnholyAlliance` in scenario.cpp does the spawn.

**The `tf_mcv_test.flag` dev lever is gone** — flag file deleted and its code removed, since
this mode gives the same four-MCV start through a real lobby option. It also cost a test: the
lever spawns for the HUMAN only, so four yards for you and one for the AI means the lever fired,
not the mode. That ambiguity is why it was removed rather than left alongside.

**Still to verify:** whether choosing this game type leaves bases ON. The extra MCVs spawn in
the bases-on branch, so if the launcher pairs Capture the Flag with bases off, the mode does
nothing and the carrier moves back to a default-off checkbox (Shroud Regrows, label capped at
14 chars — though loc_relabel.py can now grow a slot, so the full name is available either way).

**⭐ DELIVERY SOLVED (2026-07-21) — it can be a real lobby option, no UI additions needed.**
The earlier framing ("lobby UI is launcher-owned, so pick between a rules.ini toggle, a flag
file, or a CustomMaps variant") missed that **the lobby's existing options already reach the
DLL**: `CNCMultiplayerOptionsStruct` (dllinterface.h:729) carries 8 booleans and 5 ints, and
`CaptureTheFlag` lands at `dllinterface.cpp:926` as `Special.IsCaptureTheFlag`.

So: **hijack a game mode we do not support.** Capture the Flag is the candidate — it needs flag
placement our maps never provide, and the text strings show the lobby has a game-mode selector
(`..._TOOLTIP_MODE_BASES_ON_DESTROY_ALL`, `..._TOOLTIP_MODE_CAPTURE_*`, `..._TOOLTIP_MODE_MOBILE_HQ`).

1. Relabel it: `Capture The Flag` is a 16-character string in `MASTERTEXTFILE`, and same-length
   in-place edits are proven (`faction-select-identity.md`). `Unholy Alliance` is 15 — it fits
   with one pad character. The mode tooltip wants the same treatment, under the same constraint.
2. In the DLL, treat `Special.IsCaptureTheFlag` as the Unholy Alliance switch: spawn the four
   faction MCVs, and gate off the real CTF behaviour so the old mode cannot half-run.

**Verify first (one glance at a lobby):** that the RA game-mode selector actually offers Capture
the Flag. The text IDs and `CNCCaptureTheFlagDefault` are shared between RA and TD, so their
presence is not proof RA shows the option. If it does not, `SpawnVisceroids` (TD-only, inert in
RA) is the fallback carrier — same technique, less honest label space.

## TS-walker leftovers (2026-07-21 — low priority; units are hidden behind DevTechLevel anyway)

Shipped and signed off in-game: Titan + Mk. II ports, muzzle table, railgun, MLRS balance +
shadow. Titan turret-seam and Mk. II E-facing top-clip checks CLOSED (Luke verified in play).
Still open:
- **Blue railgun spark art** — currently ANIM_PIFFPIFF stand-in; real TS-blue sparks blocked
  on understanding how TDIONSFX gets custom anim art past the launcher
  (launcher-render-contracts.md #4).
- **Audit older custom anims** (TibFumes, TDCHEM-*, TDFTFLAME-*) for the same launcher-dead
  rendering contract #4 describes — they may be drawing white placeholders in-game.

## Faction paratroops split (Luke, 2026-07-20 — queued; ride 4.1 if testing is quick, else 4.1.1)

**Observed:** owning the Soviet airfield AND Nod airstrip+Hand still gives ONE paratroop
option. Not a regression — superweapons are house-level singletons (one `SuperWeapon[SPC_*]`
slot per type; `SPC_PARA_INFANTRY` just has two grant paths, house.cpp:2437).

**The fix is the Temple-nuke pattern** (`SPC_TD_NUKE` coexisting with `SPC_NUCLEAR_BOMB`):
1. New `SPC_TD_PARA_INFANTRY` in defines.h (before `SPC_COUNT`; note `SPC_CHRONO2 = SPC_COUNT`
   alias shifts — check its users).
2. `HouseClass::Init_Data`: SuperClass init line (copy the para one).
3. Grant split at house.cpp:2437: existing `SPC_PARA_INFANTRY` becomes Soviet-airfield-only;
   the Nod path (TDAFLD+TDHAND) enables the new special.
4. Firing path: find the `SPC_PARA_INFANTRY` case in the special-fired dispatch; TD variant
   drops TD infantry (TDE1s) — ideally from the C-17 (`AIRCRAFT_TDCARGO`), Badger acceptable
   for v1.
5. `Convert_Special_Weapon_Type`: new case → `SW_PARA_INFANTRY` dll enum + a distinct asset
   name (e.g. `SW_TDParaInf`); matching `RA_SW_TDPARAINF` RABUILDABLES block (Nod-badged
   cameo, ModText name) — the launcher renders by AssetName, which is how the two nukes
   coexist today.
6. Sidebar sort table in `TF_Sidebar_Sort_Key` (`sidebarglyphx.cpp`): existing para-inf moves
   to the Soviet block, the new one to Nod.
7. Related 4.0 leftover in memory: "missed Soviet parabombs" rides the AI milestone's
   superweapon work — same neighborhood, maybe the same session.

---

## ⭐ RESUME HERE — W2(b) construction-yard split (2026-07-19)

**READ FIRST: `docs/w2b-conyard-split-postmortem.md`.** It has the full session record, the
falsified theories (do not re-chase), and the corrected plan. Summary:

**Nothing needs reverting.** Tree is clean, builds, deployed to the desktop prefix. The only
regression of the session (invisible MCV + construction yard, caused by renaming tileset
`<Name>` keys) was already fixed in `66af6c7`. Eight commits shipped and are good — W2(a)
prereq-aware eviction, b1 role predicate + unified BScan shadow table, the Tiberian-era enum
marker, 4 new types (`SFACT`/`TDNFACT`/`SMCV`/`TDNMCV`, inert at `TechLevel=-1`), IniName
migration.

**What was wrong was the APPROACH, not the code.** The split was hand-built (reused types,
`Image=` sharing, hand-edited XML) instead of going through
`scripts/bundle_ra_building.py` / `bundle_unit.py` + `td-port-playbook.md` — the pipeline that
built the GDI/Nod naval units and which produces genuinely independent entities. See
[[feedback-check-repo-docs-first]].

**Pick up by (Luke's direction):**
1. ~~Read `td-port-playbook.md` + both bundling scripts END TO END before coding.~~ ✅ DONE 2026-07-19.
2. ~~Resolve the open question in postmortem §4.~~ ✅ **RESOLVED 2026-07-19: `Data/ModText.csv`.**
   The launcher merges that CSV into its string table; pipeline entities have rows there, the
   MCVs/yards don't, and both hand-edited MCV IDs happen to resolve to the literal string 'MCV'
   in the base text. Full chain in postmortem §4. Naming for the 8 new entities = bundler
   `--text-name`/`--text-desc` + ModText.csv rows.
3. ~~Build all four MCVs and all four yards as fresh, fully independent entities.~~ ✅ **DONE
   2026-07-19 (built + staged, awaiting in-game verify + commit).** Vanilla
   `FACT`/`MCV`/`TDFACT`/`TDMCV` identities restored (From_Name aliases gone); 8 fresh types
   (`AFACT`/`SFACT`/`TDGFACT`/`TDNFACT`, `AMCV`/`SMCV`/`TDGMCV`/`TDNMCV`) with own pipeline
   art, tileset keys, RABUILDABLES blocks, ModText.csv names, rules.ini sections; all inert
   until b3. `bundle_unit.py` gained `--source ra`.
4. ~~Badged cameos.~~ ✅ **DONE 2026-07-19** — `BuildIcon_{AMCV,SMCV,TDGMCV,TDNMCV}.tga`
   (base MCV cameo cropped from the commandbar atlas + dot emblem badge, bottom-right).
5. ~~b3 functional split.~~ ✅ **SHIPPED 2026-07-19 late, live-verified on desktop** — `Owner=`
   narrowed per faction, faction MCVs `TechLevel=7`, six-way deploy/undeploy + four-way spawn,
   `Is_MCV()` role predicate (15 sites), skirmish↔campaign session gate in `Can_Build`
   (vanilla pair campaign-only, faction quartet skirmish-only), `[POWR]`'s
   `Prerequisite=fact` remapped to any-yard, crate MCV faction-correct + `UNITF_MCV`
   bit-test fixed. **Plus (same session):** cross-era infrastructure prereqs (either era's
   power/refinery/radar satisfies both eras' tokens; tech centres deliberately stay
   faction-unique — vanilla MP atek↔stek equivalence REMOVED, Luke's call), donor
   ImageData/MaxSize wiring for all 8 (the invisible-entity + tiny-selection-box fixes),
   `tf_mcv_test.flag` dev lever (one MCV of each faction at skirmish start), faction-badge
   cameos (mod-logo emblems, top-left) on 18 entries incl. war factories/airfields/naval +
   colliding tank pairs. Litmus test PASSED except Soviet-MCV-via-capture, which is the
   known (c) gap.
6. ~~(c) War Factory split.~~ ✅ **SHIPPED + PLAYER-VERIFIED 2026-07-19/20** (`5ffa98d`) —
   AWEAP/SWEAP fresh pipeline entities incl. AWEAP2/SWEAP2 door overlays; captured
   yard → faction war factory → faction MCV verified in play ("everything works well").
7. ~~(d) Helipad split.~~ ✅ **SHIPPED 2026-07-20 (`3492bf1`), deployed, awaiting play-verify** —
   AHPAD/SHPAD/TDGHPAD/TDNHPAD; free heli follows the PAD's faction; universal landing kept;
   `Is_Helipad()` predicate. **Every production building is now faction-split** — the capture
   chain runs yard → war factory → helipad in all four directions.
8. **Cameo badge wave (same sessions):** mod-logo emblems top-left on 32 cameos — 4 MCVs,
   yards' buildables, war factories, airstrips/airfields, naval, helipads, turret pair,
   pillbox/flame-bunker pair, tank pairs (Mammoth/Light/Medium). Rule: faction-unique
   entries only, shared entries stay clean. On-map sprite badges tried and REVERTED
   (Luke's call; `scripts/badge_sprite_art.py` kept for reuse).
9. **NEXT: b4 bonus-unit picker** (scenario.cpp:3023 known-issues fold-in), the W2 docs
   pass (rewrite ai-upgrade-plan §W2 b-blocks to match shipped reality), and the
   DOCKLANDS A* strong test. (The four-MCV dev lever was removed 2026-07-21; Unholy
   Alliance replaces it.)

⚠️ `ai-upgrade-plan.md` §W2 still contains superseded claims (the `Name=`-drives-sidebar naming
spec, the reuse-not-split MCV decision, the `UnitClass::ActLike` b3 note). Postmortem §6 lists
them; fix when picking up.

---

## Crate idea: enemy-faction construction yards (Luke, 2026-07-19) — BLOCKED on W2(b3)

Three extra crate types granting the OTHER factions' construction yards, so a wiped player
can come back as a different faction. **Mechanism (only works after b3):** hand out a normal
`UNIT_MCV`/`UNIT_TDMCV` with its instance `ActLike` stamped to the target faction —
`MCV_Deploy_Building` reads the unit's `ActLike` (see `ai-upgrade-plan.md` §W2 b3 note), so
it deploys that faction's yard, and `BuildingClass::Unlimbo`'s existing `Owner=`-driven
pinning gives the player that faction's sidebar for the rest of the match.

- **Does NOT work before b3** — with owner dispatch any MCV deploys YOUR yard, so the crate
  would silently do nothing.
- `CrateType` (defines.h:740) is a plain enum, extensible; needs weighting + the pick site.
- Art is automatically right: the TYPE carries the era/sprite (`MCV` vs `TDMCV`), the
  instance `ActLike` carries the faction within it, where the sprite is shared anyway.
- **Separate, decided:** the existing `force_mcv` crate (`cell.cpp:2662`) must be
  FACTION-CORRECT, not random — it fires when a player is already wiped, a poor moment for a
  coin flip. Its companion bug: the `UNITF_MCV` test at `cell.cpp:2520` only sees bit 11, so
  a GDI/Nod player who already owns a TDMCV still trips `force_mcv` and is gifted a
  redundant second MCV. Both are small and carry no design content.
- Deliberately NOT folded into W2(b) — it is a feature, it cannot work until b3 lands, and
  (b) is already 4 sub-steps + 2 enum values + the `Owner=` renarrowing.

---

## Campaign ("The Inheritance War") — pipeline PROVEN, authoring DEFERRED behind the AI pass

**Decision (Luke, 2026-07-19): no mission authoring until the AI milestone is done.** The
research risk is now zero — hijacked CS/AM slots launch our own scenario INIs via CCDATA,
verified on desktop AND Deck (`docs/campaign-tabs-research.md`); `INSTANCES.XML` drives the
roster; the Mobius fork is mod-aware for authoring; desert theatre works if TD terrain is
wanted. What remains is content, and it waits.

**First task when it resumes:** author GDI mission 1 ("First Light") for real in an Aftermath
slot — proper map, briefing, win/lose conditions — before committing to all 9. The throwaway
probe (empty map, instant win) did NOT exercise triggers, teamtypes, or how the briefing and
mission title present on screen; those are the unknowns a real first mission would settle.

## ⭐ SESSION 2026-07-19 (evening) — A* budget measured, economy gates SHIPPED, engineer livelock root-caused

**1. A* expansion budget: `captrips=0`, but only a WEAK pass.** Measured live on desktop
(4 GDI AI) and Deck simultaneously, both on the post-`23203d2` build: zero cap trips across
thousands of searches. So the 4096 budget never fires in normal play and there is no case for
raising it. **It has NOT been tested against the case it exists to bound** — a target that
looks reachable but is not. The engineer `src==dst` spam does not stress it (`dest==source`
breaks on the first loop iteration, costing zero expansions), and AIs on one connected
landmass always have reachable targets. **To actually close item 1: run DOCKLANDS with the
human isolated across the river**, so AI attack orders target something with no land route,
then read `captrips=`. Non-zero there is the GOOD outcome; act only if caps coincide with
units failing routes they should make.

> **Weak pass RE-CONFIRMED at larger scale, 2026-07-19 late (live human skirmish, b2 build):**
> `captrips=0` on all **8,728** fallback samples in an active play session. Fallback census
> matches the known livelock profile, nothing new: 1,890 are the literal `src==dst` shape
> (`path-failure-livelock-design.md`), and the top 8 wedged-repeat tuples (E2/TDE1/TDE6
> infantry re-running one route) account for ~38% of all fallbacks across only 725 distinct
> (unit,src,dst) tuples. Verdict: heap + budget healthy in normal play, no truncation, no
> budget raise warranted. The DOCKLANDS unreachable-target run remains the outstanding
> STRONG test before the item fully closes.

**2. Economy gate for GDI/Nod tier-2 — SHIPPED `04d3ef4`, verified in play.** Comm centre,
tech centre and repair bay now share one condition (2 refineries + a war factory, with a
tiberium-short escape hatch). Fixes both player reports: repair bay built before any
refinery, and teching to TDEYE with no war factory. The tech centre was the worst offender —
a bare `current < 1` commented "as soon as possible", racing the war factory at equal
urgency. Playtest confirmed: war factory first, repair bays still built, **and a Mammoth was
produced** (the starvation canary on the stricter gate). RA houses keep vanilla timing.

**3. Path-failure livelock — ROOT CAUSE CONFIRMED, NO FIX. One attempt CRASHED both
machines.** Full design note: **`docs/path-failure-livelock-design.md`** — read it before
touching this. Summary: units retry a doomed path forever because the give-up branch
(`infantry.cpp:4346`) aborts only when the destination is in a DIFFERENT movement zone, and
zones ignore buildings — so anything walled off never aborts, and a destination equal to the
unit's own cell can never mismatch at all. Vehicles have the same defect via the patient
queue (`drive.cpp:2180`) resetting `TryTryAgain` every cycle.

⚠️ **Two dead ends recorded so the next session does not repeat them:**
- Calling `Assign_Destination(TARGET_NONE)` from inside `Basic_Path()` **crashes the game**
  (desktop AND Deck, minutes in). It is virtual; the overrides run radio/mission logic that
  assumes an order-issuing context. Clear caller-side, where the engine already does
  (`drive.cpp:2192`).
- The `Nearby_Location` own-cell guard is **falsified** — shipped alone, self-cell came back
  at 790 (vs 706 before). The degenerate destination does not originate there.

**Framing correction:** self-cell (`src==dst`) was never the disease. The biggest livelocks
are ordinary destinations (`TDE1 (40,40)->(35,33)` x598 in one match). Both are the same bug:
a total path failure never clears `NavCom`.

**Next step is DESIGN, not code** — the open questions (retry threshold vs the v2.2.3 patient
queue, what a unit does after giving up) decide whether a fix is a win, and this code moves
every ground unit in the game. All surfaces are currently on clean `HEAD`.

**Diagnostic gap worth closing:** build order is not logged anywhere, so verifying build-order
changes needs a human watching. If more build-order work is coming, a small
`TF_AI_DIAG` line on building completion would pay for itself.

## ⭐ SESSION 2026-07-19 (afternoon) — phase B RESOLVED, next session resumes AI work

**Per-slot AI difficulty now works in LAN multiplayer.** Verified end to end:
Easy/Easy/Easy/Hard applied as IQ 3/3/3/5, `[slot n]` tagged, on screen on both peers.

**The finding that did it: only the HOST simulates a LAN match.** A joiner's client
renders streamed state and never executes the game DLL (proven by role swap on one
machine: silent for a full 10-min match as joiner, logging within 10s of hosting; the
sim lives in `InstanceServerG.exe`, which on a joiner has no game DLL mapped). So there
is no second sim to diverge from — the fix was deleting the `humans < 2` guard, not
building a mechanism. Retired: host-broadcast, mirrored-lobby read, live-model hex hunt,
the `PHASEB-ID` probe. `tf_ai_difficulty.txt` now applies in MP for the same reason.
Detail: `docs/lobby-difficulty-ram-spike.md` status block, [[reference-lan-mp-host-only-sim]].

Commits: `bb69419` (guard), `23203d2` (A*), `06ca30a` (probe removal), `f03c06f` +
`a4a6182` (flag file + docs), `7277705` (W3 note), `3447491` + `0eb83eb` (classic-mode).

**RESUME HERE next session — in priority order:**
1. **A* soak — WEAK PASS ×2, strong test outstanding.** `23203d2` (heap + 4096-node
   budget): `captrips=0` in the dual desktop/Deck measurement AND across 8,728 fallback
   samples in a live human skirmish (2026-07-19 late — census in the session block above;
   fallbacks = the known livelock profile, nothing new). No budget raise warranted. Left to
   fully close: the DOCKLANDS unreachable-target run (human isolated across the river) —
   the one case the budget exists to bound.
2. **Repair bay builds far too early** (player-observed). GDI sometimes builds it before
   its first refinery; both factions before vehicle production and a second refinery.
   Small fix: gate eligibility on having an economy at `house.cpp:6959` rather than
   lowering urgency (LOW = never built = no GDI Mammoths). See `ai-upgrade-plan.md` §W3.6.
3. **Then Phase 2 (W2 faction separation)** — the next real milestone chunk.

**Per-slot AI difficulty: root-caused and FIXED 2026-07-21 (needs a verification pass).** Matches
after a session's first one usually fell back to global Hard: the client rebuilds its `AIPLAYERn`
records at match launch and the scan was landing mid-rebuild. Fixed with a deferred re-scan
requiring two consecutive agreeing scans (`TF_Lobby_Difficulty_Retry`). Full account in
`known-issues.md`. **To verify:** two solo skirmishes in one launch, the second with the
difficulty dropdowns untouched — expect a `(deferred re-scan)` line and `[slot n retry]` tags
within ~10s, and watch for a stutter at the retry points (the scan runs on the game thread).

**⭐ CLASSIC GRAPHICS: LOCKED OUT FOR GOOD (2026-07-21) — the parked item below is CLOSED, and
not by any of the routes it lists.** `GAMECONSTANTS.XML` carries EA's own mod switch,
`CNCDisableLegacyGraphicsOption`; set `True` it removes the Options entry **and kills the
spacebar toggle** (verified in-game on the desktop). Shipped through the existing
`gameconstants_build.py` → loose `Data/XML/` + `Data/CONFIG.MEG` path, byte-length-neutral so
the same-size MEG rule holds. Credit: DontCryJustDie flagged the constant on the Workshop page.
No warning message is needed now — there is nothing to warn about. Details:
`launcher-vs-dll-ownership.md`.

**Lesson worth keeping:** the DLL-side conclusions were all correct and all irrelevant. Four
attempts went into detecting a mode we could simply deny, because "launcher-owned" was read as
"unmoddable". For any launcher behaviour, grep `CONFIG.MEG` before spending a spike.

## ⭐ AI milestone Phase 1 — MERGED to main + LIVE-VERIFIED 2026-07-18 (commit `e01bc35`)

**Full handover: `docs/ai-phase1-handover.md`.** W7 difficulty→IQ, W1.5 primary-factory,
W1.2 fair-fog intel, W1.3 scouting. Merged 2026-07-18; `Vanilla_RA_AI1` desktop mod
consolidated back into the single `Vanilla_RA` local mod. Live desktop diagnostic session
(2026-07-18) verified the headline paths and root-caused two design holes, both fixed
same-session:

- **W7 verdict (measured, 5 lobbies):** GlyphX sends `CNC_Set_Difficulty(1)` in skirmish
  UNCONDITIONALLY — per-slot lobby settings, all-Easy/all-Hard lobbies and the campaign
  difficulty option all still send 1. Slot dump confirms the interface structs carry no
  per-slot channel (AI names are bare `AIPLAYER1..4`, hex-verified). **Shipped lever:
  `Documents/CnCRemastered/tf_ai_difficulty.txt`** (`easy|normal|hard`, re-read each match
  start; ABSENT = hard/MaxIQ = shipped v4.0 strength). Both paths live-verified
  (default-hard IQ5; file-easy IQ3). NOT dev-gated — release feature; document in Workshop
  copy at next release.
- **Fair-fog turtle deadlock FIXED:** AI never attacked (player-observed + screenshot).
  Root cause: `AI_Attack` shuffles (no-ops) 67% of calls and was the only hunter source, so
  blind houses never scouted → never discovered → never attacked. Fix: `Expert_AI` keeps a
  2-unit scout detail on hunt while the house knows no enemy building. Live-verified: all
  four AIs scouting by ~F2500, real `WAVE-LAUNCH` after contact, player confirmed fighting.
- **Build-choice starvation: FIXED + LIVE-VERIFIED 2026-07-18 (commit `d4f3da7`).**
  Winner scan took the first pool entry at max urgency, starving late entries (TDTMPL
  zero tie wins in ~40k frames; TDOBLI/TDATWR/TDEYE similar). Top-urgency ties now break
  uniformly (reservoir pick on the synced RNG, MP-deterministic). Verified with 6 Hard
  AIs: 98/123 decisions were real ties, every starved building won cycles (TDTMPL 5,
  TDOBLI 12, TDATWR 2, TDEYE 1), temples confirmed standing in-game; economy priorities
  intact. Diag WIN lines print `ties=N`.

**✅ RAM per-slot difficulty phase A — SHIPPED + LIVE-VERIFIED 2026-07-18 (commit
`3e156a0`):** solo skirmish now applies each lobby slot's real Easy/Medium/Hard pick to
its AI house (RED confirmed all-same first, then GREEN: Hard/Medium/Easy/Hard lobby →
IQ 5/4/3/5 on the matching houses, on-screen + log). Scanner + slot map live in
`redalert/dllinterface.cpp` next to `CNC_Set_Difficulty`; the HELLO announcements (log +
on-screen via deferred flush, commit `45bf3b0`) print each house's mode tagged
`[slot n]`/`[global]` and are the standing verification readout. Implementation notes +
the IniName-rename trap: `docs/lobby-difficulty-ram-spike.md`. Remaining:
- **⭐ Phase B (MP per-slot difficulty) — RESUME HERE (rig night 2026-07-18, full
  findings in the spike doc phase-B section):**
  1. Host-broadcast design DEAD (verified: GlyphX has no DLL-side event transport —
     `Glyphx_Queue_AI` is local-only, no packet exports, callbacks are local
     presentation; MP determinism = client-side request replay).
  2. Mirrored-lobby read as scanned is ALSO DEAD: the `AIPLAYERn` record array is each
     account's **saved skirmish config**, not the live lobby. Proven on the 2-peer LAN
     rig — joiner read its own stale config 4 matches straight, and the host's read
     contradicted its own lobby UI (which both screens rendered identically and
     correctly, so a **live lobby model exists in every peer's client** — that's the
     real target). Scanner v2 (roster-name anchor, commit `4f2a1a1`) is still right
     for the solo path.
  3. **NEXT ACTION: run one probe-v3 match** — build `8ae684f6` (commit `c036d59`)
     is ALREADY DEPLOYED on desktop + Luke's Deck. Deck hosts LAN lobby, fresh
     difficulty mix (e.g. Hard/Easy/Med/Hard), desktop joins, start, quit. The probe
     dumps hex context around each AI GlyphxID (name-hash, identical cross-peer) in
     both clients → diff host-vs-joiner `PHASEB-ID` lines in the two
     `MOD_DEBUG_AI.txt` files → derive the live model's difficulty-int offset →
     scanner v4 reads the live model on every peer (deterministic, no broadcast).
  4. **BUG (shipped phase A, found by rig reasoning):** the per-slot apply gate is
     `humans < 2`, which includes a 1-human LAN lobby — there the saved-config records
     mismatch the live lobby, so stale difficulties get applied. Fix rides the v4
     live-model read (or gate solo-apply out of LAN lobbies if distinguishable).
  Rig: 2-peer (desktop Luke + Luke's Deck on daughter aimee101; son's Deck approved
  but benched). Watch the twin-mod trap: Workshop copy and local mod are both named
  the same — local shows the higher version (4.1). Daughter's playtime limit ended
  the night; extend it before the next rig session.
- **Workshop copy at next release:** document per-slot lobby difficulty as a feature
  (and `tf_ai_difficulty.txt` as the fallback lever). DontCryJustDie is already in the
  mod credits (TD-Assets); no new ack needed — though the release notes can mention the
  difficulty collab (their process-memory pointer; their implementation built from our
  published `lobby-difficulty-ram-spike.md`, Workshop thread 2026-07-18).
- **RAM is an extraction channel, NOT a launcher unblocker** (survey confirmed): reads
  lobby selections (faction-per-slot, map, difficulty); does not move compiled-behaviour
  walls. Don't over-scope it.

**Open follow-ups from the session:**
1. **Settings-file route for per-slot difficulty: RESOLVED NEGATIVE (2026-07-18,
   measured).** The client's persisted settings
   (`userdata/<id>/1213210/remote/Player_RA_settings_1.bin`, ChunkFile + zlib@0x24, TLV
   property stream — same family as .bui) contain NO per-slot difficulty; the one byte
   that moved during flips (tag 0x31 int32) is a match-start counter. Per-slot picker
   state is ClientG memory only — which the phase-A RAM read (shipped same day, see block
   above) now extracts; `tf_ai_difficulty.txt` is the fallback lever. Don't re-chase the
   settings file.
2. **W1.2 unit-visibility leak suspicion — ✅ DOES NOT REPRODUCE (overnight 2026-07-19,
   4 desktop matches):** blind-hunt scouting fired healthily every match (83 SCOUT-DISPATCH,
   130 blind probe moves; first dispatches ~F2290, probes to undiscovered dests). Enemy units
   are NOT evaluable at match start; the fair-fog gate behaves as designed. The 2026-07-18
   zero-probe observation was that session only — plausibly its lobby/stale-roster state (see
   the stale-apply note below). Documented residual stands (once-seen units stay evaluable
   while fogged — positionless mask); no new leak.
3. **H14 APWR loop observation:** USSR AI won `APWR(u2)` 20+ consecutive build decisions
   (turtle match). Legit power-hunger or overbuild loop — check base for APWR farms.
4. Rotate `MOD_DEBUG_AI.txt` between matches during diagnostic sessions (two matches
   interleaved in one file cost real analysis time; note: the shared diag FILE* stays open
   across matches within one game process, so rotate only at full game restarts).

## A* pathfinding: O(n²) open-list insert + no expansion cap (2026-07-18, from the megamaps spike)

Found while surveying pathfinding for `docs/megamaps-feasibility.md`. **Independent of map size —
live on the current 128x128 build**, and squarely in the AI milestone's path.

> **Live data (overnight diagnostic, 2026-07-19, 4 desktop matches — partial repro):**
> - **The wedged-repeat shape reproduces:** E6 engineers dominate the fallback log (1,180 of
>   ~1,300 fallback lines), with the SAME unit+src failing up to **196 consecutive times** at
>   fixed cells ((105,57), (91,118), (96,21), (99,23), (9,70)) — repeated failed searches from
>   stuck units, i.e. exactly the input the missing expansion cap makes expensive. Worth
>   asking WHY AI engineers path-fail on repeat (capture-target unreachable?) as its own lead.
> - Failure rates ran 12–47% of all A* searches per match (best on the small desert map,
>   worst in the final session: success=578 / fallback=518).
> - **No `src==dst` spins** (0 across all matches) and no harvester blacklists — but matches
>   only reached early-game: **a solo diagnostic match ends when the human is eliminated, and
>   post-Phase-1 Hard AIs rush an idle human inside 2–4 minutes** (Destroy Structures; razed
>   ConYard = match over, leading AI declared winner). **Fix for future long runs (Luke,
>   2026-07-19): use DOCKLANDS with the human alone on one side of the river and all AIs on
>   the other** — the water barrier is what let the July 17–18 sessions reach 40k+ frames
>   unattended. These runs used a fresh Super Bridgehead lobby (open land routes), which is
>   why they died early; that's a lobby-setup mistake, not a change in AI behaviour.
> - Full logs archived: session scratchpad `tf_astar.overnight.log` / `MOD_DEBUG_AI.overnight.txt`.

- **Open-list insert is O(n).** `findpath.cpp:715` uses `open_list.insert(std::lower_bound(...))`
  into a `std::vector` — a sorted-vector priority queue with linear insertion, so the search is
  O(n²) in nodes expanded. Fix: real binary heap (`std::priority_queue` / `push_heap`).
- **No node-expansion budget.** On a *failed* search (unreachable destination) it exhausts the
  entire reachable component — up to ~16K nodes at 128x128, each with an `unordered_map` node
  allocation. A single long-range failed path can stall a frame. Fix: explicit expansion cap with
  fallback to the legacy path.

Not yet reproduced in-game — flagged by static reading, so **confirm with a diagnostic run before
optimising** (unreachable-destination order across water/walls is the likely repro). The
`unordered_map` choice itself is correct and should stay: `prev` pointers into it must survive
rehashing.

Also spotted, harmless today: `defines.h:589` — `MAP_REGION_HEIGHT` uses `REGION_WIDTH` in its
rounding term instead of `REGION_HEIGHT`. Only masked because both are 4; a landmine if regions
ever go non-square.

## TS asset spike — CLOSED (2026-07-18); no follow-up work queued

The Tiberian Sun import spike is DONE and player-signed-off (see
`docs/ts-asset-import-spike.md` for recipes + the launcher-contract trap list):
Hover MLRS ("the golden child") + Stealth Generator TS reskin + hover locomotion
+ TS audio port. **Spike outcomes are parked, not in-flight (Luke, 2026-07-18):**
TSHVR + TSPOWR are off the build menus (TechLevel=-1, commit `adfca77`) and stay
in as a working TS-pipeline reference + map-maker easter egg. The TSPOWR art
pass is DROPPED from lined-up work — not to be picked up before mod completion
at the earliest; a real TS mod would revisit it via `ts-factions-feasibility.md`.
TS hover bob likewise waits for a real second hover unit. Resolved from the
spike session since: the cloaked-bib leak (fixed `58ae18f`) and the
Temple-starvation fix (`d4f3da7`).

## ⭐ RESUME HERE — AI milestone Phase 0 (2026-07-17)

**Code COMPLETE + committed** (`bb286b5` W1.1 fixes + AGT power + harvester idle-home;
`9069392` diag v3 + AI Boost scatter/send-percentage). Full status: `ai-upgrade-plan.md` §6
Phase 0 + §3 W1.1 STATUS notes. Two verification gates remain:

1. **Temple-starvation diagnostic session** — ATTEMPTED 2026-07-17, held: the game loaded the
   Workshop 4.0.0 copy (release DLL, no logging) because the Workshop self-test left it
   enabled. Everything else is staged: dev DLL (TF_AI_DIAG v3) deployed to the desktop
   prefix, old MOD_DEBUG_AI.txt rotated, lobby remembers GDI vs Nod-MEDIUM/Docklands.
   Next run: enable the LOCAL mod (Options → Mods → Mods Folder → Vanilla_RA), play/idle
   any Nod-AI match, read `drive_c/users/steamuser/MOD_DEBUG_AI.txt` (grep TDTMPL/TDSTEAL
   + POOL/WIN lines). Freshness check: dev DLL recreates tf_astar.log within seconds.
   Claude can drive it autonomously (recipe + traps in cross-session memory:
   desktop-diagnostic-run-recipe) — needs Luke's OK to unlock the desktop session.
2. **Phase 0 soak playtest** — player-visible changes to eyeball: AGT offline on low power,
   idle harvesters retreating to the refinery, attack waves with home garrison + launch
   scatter, better AI target picks. Then Phase 1 (intel layer + scouting + difficulty
   plumbing) per the plan.

## v4.0.0 SHIPPED 2026-07-16 (Workshop + GitHub). Remaining follow-ups:

Released: media captured (videos + screenshots in `~/Desktop/TiberianFactionsinRedAlert4.0 media/`),
CHANGELOG 4.0.0 written, tag `v4.0.0`, GitHub release with `TiberianFactions-v4.0.0.zip` (404MB),
Workshop item 3729834253 updated (new logo preview, pruned description with 4.0.0 changelog).
Local dev version bumped to 4.0.1.

1. ~~ModDB page~~ — ✅ UP (Luke, 2026-07-16; page copy archived in `docs/moddb-page-copy.md`).
   May still pass through staff authorisation before it's publicly visible.
2. ~~Reddit~~ — ✅ DONE (Luke, 2026-07-16).
3. ~~Workshop self-test~~ — ✅ DONE (Luke, 2026-07-17; subscribed 4.0.0 tested fine).

**Missed from v4.0 (caught post-release 2026-07-16): Soviet parabombs.** The power-grants batch
shipped GDI GPS + Nod spy plane + Nod paratroopers, but the Soviet parabombs grant (same held-list)
was never implemented — no PARA_BOMB commits since v3.0.0. Queue for the next release.

**Next-release obligations (accrued during AI Phase 0, 2026-07-17):**
- **Workshop acknowledgements: credit Bast75 & xXMini FrankiXx (AI Boost 3.2)** — first ported
  code (scatter-on-launch, send-percentage) is now in the tree. Licence verified GPL-compatible.
- Changelog lines owed: AGT goes offline on low power (TD-canon); AI target selection actually
  picks best target (bestval fix); idle harvesters retreat to the refinery; AI attack waves
  keep a home garrison scaled by base defences (AI Boost port); AI wave-launch scatter.

**Next milestone: the AI upgrade — plan complete, see `docs/ai-upgrade-plan.md` (2026-07-17).**
Design locked with Luke (one brain + faction-building separation + heritable capture-tech,
behavioural difficulty via IQ, intel layer + fog-cheat removal, blob attacks, naval + water
eval, transports, coordination, directional armour, reservation-table pathfinding). All six
research reports integrated. Start at the plan's Phase 0.

- **BUG (Luke, live match 2026-07-16): Nod AI not reaching Temple → Stealth Generator in
  practice.** Static suspects: both slots gated `Power_Fraction() >= 1` (Nod hovers at marginal
  power; Obelisks -150) and both URGENCY_MEDIUM in a single-winner-per-cycle build-choice pool, so
  defence/factory picks starve the Temple indefinitely (house.cpp:6815 tech slot, :6607 stealth
  slot). Verify with a dev-build diagnostic session (release builds log nothing), then fix as part
  of the AI build-order rework (same thread as the eco-passivity item).
  **Sequencing decided (Luke, 2026-07-17):** the fix rides the W3 build planner (plan §3 W3.1
  already subsumes it) — no interim Phase-0 patch unless the diagnostic reveals a one-liner. The
  diagnostic itself stays in Phase 0: it validates the root-cause hypothesis W3's design leans on,
  and the build-choice decision log it needs is the milestone's day-one instrumentation anyway.

---


## Stood down — not doing (2026-07-15, Luke)

Cleared off the active backlog by decision (not implemented). Design docs retained for reference
only; do not resume without Luke re-opening.

- **ModText.csv fleet-wide naval naming** (Naval Yard, Sub Pen, Missile Sub) **+ classic SHPs for
  the RA-art naval clones** (TDPT/TDDD/TDCA/TDNSUB/TDMSUB). Was a navy-session "next candidate".
- **Harvester docking rework** (economy-balance; converge RA harvester onto the TD attach-dock
  mechanic). No code was written. Plan doc `harvester-docking-rework-plan.md` kept as reference.
- **Nod defensive-economy gap** (AGT vs Obelisk+SAM) — stood down; see the Defences-balance section
  below, left in place for context but not being actioned.

**AI-focus pass is POST-v4.0** (air-build escalation retune + skirmish-AI improvements + the deferred
stuck-in-base pathfinding) — not part of the current milestone.

---

## v4.0 air / paratroopers / balance — open threads (2026-07-13, live)

Spun out of the air-AI + power-grants session. The 2026-07-13 batch (airfield/A-10 AI routing,
3 power grants, AI air-responsiveness max-threat + limit-mirror, MCV/ConYard/AGT,
Nod-paratrooper-drops-minigunners) is **playtest-verified (Luke, 2026-07-16)**. Open items on top:

_(Nod SAM accuracy: ROT 10->20 shipped; no longer tracked as a discrete item — watch it during
the AI-focus pass.)_

**Done this milestone:** Nod Stealth Generator (shipped 2026-07-15, Gap-Generator art, cloak
field + bib-hide + helipad/aircraft cloak + teardown restore + 400 HP + organic Nod-AI build —
see `docs/stealth-generator-spec.md`); Nod paratrooper C-17 plane (`TDC17P`, targetable/radar-
visible support-drop twin of TDCARGO); AI air-build priority dropped to LOW (war factory first);
Nod Flame Bunker (`STRUCT_TDFBNK`, anti-infantry flame defence, Nod-AI build rule); **GDI GPS
full Allied parity** — flicker fixed (removal checks recognise TDEYE past the 32-bit BScan mask)
AND launch fixed (fire loop + `Mission_Missile` now launch the GPS satellite from TDEYE, so it
reveals + doesn't restart); Ion Cannon reverted to the TD-authentic 10-minute charge (dropped the
dev 1-second shortcut).

---

## Defences balance — Nod defensive-economy gap + optional Tesla chain (2026-07-13)

Spun out of the v4.0 building balance dive. Building HP is fine (the `MaxStrength*2` at load —
bdata.cpp Read_INI — equalises TD buildings to RA scale). Two open threads:

- **Nod defensive economy is much worse than GDI's.** GDI's Advanced Guard Tower is a cheap
  (1000 / −20 power), dual-purpose (AA+AG via TDSSM), **Burst=2** tower that covers ground *and*
  air in one building. Nod must pay for the Obelisk (1500 / −150, ground-only) **plus** a separate
  SAM (750 / −20, air) — ~2.25× cost, ~8.5× power for the same coverage — and Nod's light-vehicle +
  Apache roster is exactly what the AGT eats (1.7 eff DPS vs light, plus AA). **Lever:** AGT cost/power
  (curb cheap spam), or a Nod defensive-economy buff (cheaper Obelisk/SAM, or a dual-purpose Nod
  option). NOT the AGT warhead — vs-light is untouched by the reverted F8 buff. Test in a GDI-vs-Nod
  skirmish before tuning.
- **Optional: Tesla "chain" to low-HP targets (esp. infantry).** RA1's Tesla does NOT chain in this
  codebase (single-target, Spread=1); the group-clear feel is the Super warhead one-shotting infantry.
  Could be added as a code feature (arc to nearby targets) if we want the RA2-style behaviour — parked.
- **Done this session:** AGT vs-heavy reverted 50%→25% (it was already strong via Burst=2 + AA +
  cost/power). Obelisk range left at 7.5 (< Tesla 8.5) deliberately — higher damage, shorter reach.

---

## A-10 napalm bombs fall ~4x faster than TD (double falling physics) — ✅ DONE, playtest-verified (Luke, 2026-07-16)

TD-port Dropping bullets (BULLET_TDNAPALM) got falling physics applied twice per frame:
RA's `ObjectClass::AI()` integrated Height/Riser with `Rule.Gravity` (3/frame decay) AND
`BulletClass::AI_TD()`'s TD-verbatim Dropping branch integrated again with TD's 1/frame
decay. TD intended 1/frame only, so bombs hit the ground much earlier than TD's.

**Fix (bullet.cpp, uncommitted):** `Unlimbo_TD` no longer sets `IsFalling` for TD-port
ballistic bullets, so `ObjectClass::AI()` no longer runs its parallel integrator — the
`AI_TD` arcing/dropping branch is now the sole (TD-verbatim) integrator, giving TD's exact
fall (start Height = FLIGHT_LEVEL = 256 = TD's `Pixel_To_Lepton(24)`; 1/frame decay ⇒ ~22
frames vs the buggy ~9). Because `ObjectClass::Limbo()` removes the bullet from
`In_Which_Layer()` (Height-based) at detonation, `AI_TD` now mirrors the base's map-layer
transition (Map.Remove/Submit on layer change) so removal can't miss and dangle a pointer.
Verified: `In_Which_Layer()` reads only Height (not IsFalling), and TD-port bullets never
touch the native `AI()` path that keys landing off `IsFalling` — so dropping the flag is
side-effect-free on the TD path. Only affects TDNapalm today (only Dropping TD-port bullet);
fix is symmetric so any future Arcing TD-port bullet is covered too.

Committed as `7c07015`; bombing-run feel playtest-confirmed by Luke (2026-07-16).

---

## DEFERRED: AI vehicles stuck in their own base (general pathfinding) (2026-06-18, Luke)

Observed live during harvester testing (blue AI base): several combat vehicles frozen in the base,
**not harvesters**. Deferred mid-session (focus is the harvester workstream); captured here so the
diagnostic data isn't lost. **NOT caused by the harvester field-selection/blacklist work** (that only
touches ore selection + `HARV-BLACKLIST`); this is pre-existing general unit pathing, almost certainly
the **known open chokepoint thread** (vehicle-vs-vehicle in a 1-tile gap; the gw==2 RETREAT path never
reaches the deadlock-breaker — see `chokepoint-reservation-design.md` + `cfe-port-plan.md`) plus raw
base congestion.

**Log evidence** (shared `tf_astar.log`, TF_DEV only; the `A* FALLBACK -> legacy` lines are the CFE-A*
port's instrumentation, not new):
- **A\* failing more than succeeding:** counters reached `success=4265 fallback=7860` in one match —
  units spam the legacy fallback every frame.
- **Two failure shapes:**
  1. **Wedged units** — e.g. `2TNK src=(126,52) dst=(123,47)`, `APC src=(126,51) dst=(122,54)` repeating
     with the **same src every frame** (not moving): trying to shuffle ~4 cells in a packed base, A* fails
     each frame, legacy doesn't resolve it.
  2. **src == dst spin** — e.g. `TDE6 src=(114,56) dst=(114,56)`, `src=(89,60) dst=(89,60)`: a unit
     ordered to its OWN cell; `Find_Path_AStar` returns 0 instantly for src==dest, so it spins in place.
     Likely a stale idle/guard order that never clears — a self-contained bug worth a look.
- **Hotspots** (most-failed dst cells): `(118,94)` 1682×, `(123,88)` 1163×, `(119,95)` 554×, `(112,56)`,
  `(89,59)` — all inside congested AI bases.

**When picked up:** start from the `src==dst` spin (smallest, self-contained) + the gw==2 breaker-gap
in the chokepoint thread. Reproduce = run a multi-AI skirmish, let bases fill, tail `A* FALLBACK` lines.

---

## Feature: cargo-coloured dock smoke for BOTH harvesters (2026-06-18, Luke)

Make the unload smoke colour reflect what the harvester is hauling, for **both** the RA harvester
(at its own refinery dust-loop) and the TD harvester (the `ANIM_TIB_FUMES` plume at an RA refinery):
- **Tiberium (TIB01) → green** (already what the TD harvester vents today via SMOKLAND).
- **Ore → grey** (SMOKEY / SMOKE_M).
- **Gems → (optional) a third tint** (e.g. blue) -- future.

**Prereq:** the TIB01-load-tracking item below (cargo currently can't tell Tiberium from ore -- both
bank as `Gold`). Ore-vs-gems is already free (`Gold` vs `Gems`).

**HD art is deliverable (corrected 2026-06-18 -- the earlier "new HD asset name never renders" was
overstated):** the mod already ships brand-new HD anim names as loose VFX ZIPs
(`Data/ART/TEXTURES/SRGB/RED_ALERT/VFX/TDFLAME-*.ZIP` etc.) registered in `RA_VFX.XML` -- that's how
the Flame Tank / chem / SAM muzzle anims render in HD. Recipe for a recoloured smoke variant:
1. Extract the HD frames: `SMOKE_M.ZIP` (TEXTURES_COMMON_SRGB.MEG), `SMOKEY.ZIP` / `SMOKLAND.ZIP`
   (TEXTURES_RA_SRGB.MEG) -- truecolor TGA, so ANY tint is possible (not limited to existing colours).
2. Recolour with `scripts/tgautil.py`; repack as a new-named VFX ZIP; drop it loose in the VFX folder.
3. Add `<Tile>` blocks to `RA_VFX.XML`; add DLL `AnimType`(s) selected by cargo + a donor-`ImageData`
   so the classic Draw_It NULL-guard is satisfied (we ignore the classic *look* -- HD-only mod).
⚠️ **Caveat:** a genuinely-new asset name can hit the FTFLAME "launcher caches the asset-name set at
install time" gremlin (see [[reference-launcher-new-asset-name-deadend]]) -- validate via a CLEAN mod
(re)install when the new ZIP first goes in, not an incremental DLL copy. Shipped Workshop versions are
a fresh install per subscriber, so release is unaffected.

---

## Idea: track TIB01 (Tiberium) load separately so harvester cargo can be told apart (2026-06-18, Luke)

Today a harvester's cargo is split only into `Gold` (ore) + `Gems` (`UnitClass`, unit.cpp). Our
Tiberium overlay `OVERLAY_TIB01` **banks as Gold** (unit.cpp:2965 -- "Tiberium banks as Ore, same
value"), so a harvester carrying real Tiberium is indistinguishable from one carrying ore. To support
e.g. **green Tiberium fumes ONLY when the harvester actually hauled TIB01** (vs grey/no smoke for plain
ore), add a per-harvester counter that increments on TIB01 pickup in `Mission_Harvest` (alongside the
`Gold += reducer` at the `OVERLAY_TIB01` case), and reset it on unload (where `Tiberium = Gold = Gems
= 0`). Small add (one bitfield member + Save/Load + the two reset sites). Ore-vs-gems is already free
(`Gold` vs `Gems`). Possible uses: cargo-specific dock smoke colour, or a UI/audio cue.

---

## Idea: passive chimney smoke on power plants + refineries (2026-06-18, Luke)

Spawn the `SMOKE_M` anim (`ANIM_SMOKE_M` -- a thin smoke column rising from the ground; 91 frames,
23x23, loops) continuously out of the chimneys/stacks of the **power plants and refineries** for
ambient life. Not the green Tiberium-fumes art (`SMOKLAND`) -- that's reserved for the harvester dock;
plain grey `SMOKE_M` for stacks.

Implementation sketch (when picked up):
- Per-building idle anim. Cleanest hook = spawn from `BuildingClass::AI` on a cadence (every N frames)
  at a per-building stack offset, OR a one-shot persistent looping anim parented to the building.
- Stack offset is per building type (the chimney pixel position on each SHP) -- a small table keyed by
  StructType (STRUCT_POWER/STRUCT_ADVANCED_POWER, STRUCT_REFINERY, and the TD equivalents
  STRUCT_TDPROC + any TD power). Reuse the `Attach_To(building)` z-order trick so smoke sits in front of
  the stack but behind anything south.
- Gate so it doesn't fire while in construction/deconstruction or when low-power/disabled (optional:
  no smoke when powered down = nice feedback).
- Cadence + lifetime tuned so stacks read as gently smoking, not belching. Lockstep-safe (no RNG, or
  seed off Frame+building ID deterministically).
- Reference art already extracted this session: `~/Desktop/harvester-puff-options/smoke_m.gif`.

---

## Docs update / prune pass — ✅ DONE 2026-06-16

Full survey (all 4 doc groups) run + acted on. Outcome:
- **Pruned (deleted, content captured elsewhere + git history):** `session-handoff-mcv-conyard.md`,
  `session-handoff-td-verification.md`, `session-handoff-weapons-port.md`, `manifest-gaps.md`,
  `tiberium-overlay-port.md`, `building-separation-plan.md`.
- **Updated (status banner / stale-body trim):** `theatre-desert-feasibility`, `td-skirmish-map-import`,
  `faction-music-feasibility`, `td-tile-hd-loose-art-investigation`, `adding-td-buildings`, `weapon-ports`,
  `td-tier1-verification`, `ui-atlas-modding`, `faction-select-identity`, `balance-v1-notes`.
  (`td-atwr`/`td-gtwr`/`td-obli` already carried RESOLVED banners — no change.)
- **Left CURRENT (verified accurate):** td-port-playbook, td-building-separation-recipe, the infantry/
  vehicle/cargo-plane recipes, td-sam/td-mlrs/td-attack-heli deep-dives, ai-targeting, mix-file-format,
  launcher-vs-dll-ownership, config-meg-mod-delivery, building-sound-routing, td-audio-routing-recipe,
  workshop-publish-runbook, campaign-tabs-research, coop-missions-design, gdi-nod-campaign-story,
  classic-mode-palette-remap (historical — classic unsupported), catalogue (self-labeled design-era).
- **Router updated:** workspace `CLAUDE.md` doc-map — removed the 6 deleted docs + the Session-handoffs
  section; added a Project-tracking group for `todo.md` + `known-issues.md`.

---

## CFE QoL first wave — ✅ COMPLETE 2026-06-16

All 8 first-wave items shipped: Pixel-Perfect Zoom, A*, Attack-Move, Rally Points, Harvester
Queue-Jump, Harvester Optimization, Smarter Repair Bay, and **Infantry Tiberium Aversion**
(commit `72b3a17`, Luke-verified). Everything CFE-related left is second-wave (`cfe-port-plan.md`
§2 candidates) or the bugfix inventory (§3) — none committed scope yet.

---

## Active work threads (tracked in detail elsewhere — index only)
- **Chokepoint / cooperative traffic — ✅ SHIPPED v2.3.0 (2026-06-16):** infantry give-way + vehicle-vs-MOVING-infantry freeze fix + open-ground hold-timeout + execution-branch head-on breaker all landed. **Open thread (minor):** vehicle-vs-vehicle head-on in a 1-tile gap with NO escape cell (gw==2 RETREAT path never reaches the breaker); self-resolves today, no gridlock — make the breaker reachable from the gw==2 path. See `chokepoint-reservation-design.md` + `cfe-port-plan.md`.
- **Harvester logic workstream:** targeting / pathing / claiming / reachability / idle-stuck + the economy-equalise (tilted-bucket dwell) idea. See the checkpoint's spun-off section + `balance-deep-dive.md`. **(Docking rework STOOD DOWN 2026-07-15 — see top of file.)**

---

## Idea: post-v1 faction-specific MCV / ConYard split (parked)

GDI/Nod currently share `UNIT_TDMCV` / `STRUCT_TDFACT` (dual-ownership Unlimbo guard). A later split
into faction-specific MCVs + Construction Yards would fit v4.0's separated-types direction. Not
scheduled — noted so the intent isn't lost. (Migrated from memory 2026-07-15.)
