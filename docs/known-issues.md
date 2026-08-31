# Known issues

Canonical in-repo tracker for known bugs and limitations. Started 2026-06-16.

Each entry: **severity** (blocker / major / minor / cosmetic), **status**, and a pointer to detail.
Player-facing limitations that cannot be fixed from a mod are listed too, so we stop re-investigating
them. When an issue is fixed, move it to the "Resolved" section with the fix commit.

---

## Launcher drops DLL speech dispatched in the game-over window (2026-08-31)

- **Severity:** limitation (worked around). **Status:** confirmed — do not retry refire there.
- Play-proven (tf_speech.log + ears, 2026-08-31): speech events the DLL dispatches during /
  after `On_Multiplayer_Game_Over` are discarded by the launcher — `TDACCOM1`, `TDFAIL1` and
  `RAOLOST1` all logged going out through fully valid chains (events registered, samples
  present) and stayed inaudible, while every mid-game dispatch plays. Stub + refire therefore
  can never voice the endgame lines; they ride the era mailbox instead (below). Mid-game
  stub + refire (structure sold) is unaffected and proven audible.

---

## RESOLVED: mailbox EVA lines now follow the picked faction across an in-session switch (2026-09-01)

- Was: ClientG caches each localized sample once per boot, so a faction switch without
  relaunching kept the stale voice. FIXED by the RAM patch — the DLL overwrites the cached blob
  in ClientG's memory at match start (`TF_Patch_ClientG_Cache`, dllinterface.cpp). All five
  launcher-owned lines verified faction-correct both directions, no crash. Full record and the
  five findings that made it work: `eva-ram-patch-spike.md`.

---

## MP clients keep RA voice on the mailbox-routed EVA lines (2026-08-31)

- **Severity:** minor. **Status:** open, by design for now — same shape as the credit-tick limit.
- "Cannot deploy here", "battle control terminated", "mission accomplished" and "your mission
  has failed" are faction-voiced by the **era mailbox**: the launcher fires these at moments the
  DLL never sees (client-side placement reject, teardown, the game-over window drop above), so
  the DLL instead rewrites the loose `Data/AUDIO/EN-US/` sample files those events resolve,
  copying era-correct bytes (`TF_MBX_*` payloads) at every match start
  (`TF_Mailbox_Write_EVA_Voice`, dllinterface.cpp). In LAN MP only the host runs the DLL, so
  client machines keep the shipped/base RA samples on those names. Structure sold is exempt —
  it uses stub + mid-game dispatch, which the launcher routes per player, reaching clients.

---

## MP clients hear no credit tick (faction-routed tick, 2026-08-31)

- **Severity:** minor. **Status:** open, by design for now.
- The faction-routed credit tick silences the launcher's stock `cashup1`/`cashdn1`
  events and re-fires from the DLL for the local player only (`credits.cpp`
  `CreditClass::AI`). In LAN MP the sim is host-only, so client HUDs get the
  silenced events and no DLL fire — silent tick. Fix would need per-player sound
  targeting (`DLLExportClass::On_Sound_Effect` takes a `player_ptr`; the global
  `Sound_Effect` wrapper hardcodes `PlayerPtr`). Detail:
  `building-sound-routing.md` §2.

## TS building placement (ts-units branch)

### TS power plant and TS radar placement — FIXED 2026-08-28 (Luke: "fixed!")
- Root cause: the 08-18 override made the launcher ghost the tall towers' 2x2 *box* (art headroom
  + pads) instead of their *ground* (pads + bib), so the RA bib always stamped one row south of
  the ghost and could sit on a neighbour. Now: ghost = the two ground rows with the cursor on its
  top-left (`BuildingTypeClass::Placement_Ghost_Rows_Above`; the sidebar export drops headroom
  rows and `DLLExportClass::Place` re-anchors the plot above the ghost), and legality is the
  ghost's cells only — a white ghost always places; headroom rows are never checked.

---

## Dropship bay (ts-units branch)

### ClientG crash at the dropship takeoff sound — ✅ FIX DEPLOYED 2026-08-13, VERIFY IN PLAY
- **Severity:** blocker (game exits to desktop mid-match). Two live crashes 2026-08-13
  (00:24, 00:30), both at a Mech Division delivery's takeoff.
- **Root cause:** the DROPDWN1/DROPUP1 override WAVs shipped plain PCM; dormant-host
  overrides must be MS-ADPCM like the MEG samples they impersonate, or ClientG's ADPCM
  block math divides by zero (deterministic `ClientG+0xAB5E69`, `RAR_SFX_DROPUP1` on the
  crash stack). Full record: `ts-gdi-tree-plan.md` top block; rule:
  `launcher-render-contracts.md`.
- **Fix:** `2f70e2b5` re-encodes both WAVs `adpcm_ms`. Deployed desktop (`042a01e0`).
  State-dependent crash, so several clean takeoffs = good signal, not proof.

### Countdown cameo tooltip flickers once per second — ACCEPTED (Luke, 2026-08-12)
- **Severity:** cosmetic. The 5:00→0:01 cooldown countdown is per-second baked-art
  AssetName swaps; each swap rebuilds the client's sidebar button, killing an open
  tooltip. No DLL-side fix exists (tooltip and icon are one client widget). Luke chose
  per-second precision over flicker-free coarser steps.

### Mk. II cameo reads clickable at the field cap; EVA acks refused orders — OPEN
- **Severity:** minor. At `TF_MK2_CAP` the order is correctly refused (play-confirmed),
  but the cameo looks live and a click plays the EVA "Building" acknowledgment. Wanted:
  locked look (red X / grey) via the AssetName-swap channel + gate the ack on
  `Begin_Production`'s verdict. Next-session list, `ts-gdi-tree-plan.md` top.

---

## AI difficulty

### Per-slot AI difficulty fell back to global Hard on most matches — ✅ FIXED 2026-07-21 (verification pass outstanding)
- **Symptom:** a mixed-difficulty lobby produced all-Hard AIs, logging `ram_slots=0` and HELLO
  lines tagged `[global]` instead of `[slot n]`. Affected solo skirmish and LAN alike, from the
  second match of a session onward; the first match after launching the game was always correct.
  Changing any difficulty dropdown before starting made it work, which is what made the failures
  look alternating and random.
- **⭐ PRIMARY ROOT CAUSE (DontCryJustDie, 2026-07-21): the record field at `+0x68` is the
  slot's COLOUR, not a second copy of the slot index.** Our validator required
  `slot == slot2`, so it threw away perfectly good arrays whenever an AI's colour did not
  happen to equal its slot number. Default lobbies assign colours in slot order, which is
  exactly why it worked at first and failed once anyone touched a colour. His evidence: with
  `slot == slot2` he gets no hits after changing an AI's colour, while a colour-range test
  keeps working. Corroborated on our side -- a Python dump that checked only names and
  difficulty found healthy candidate arrays during a match the DLL had rejected.
  - **Fix:** range-check the field as a colour, and require it to match the colours
    `CNC_Set_Multiplayer_Data` hands us for the current match. That doubles as the liveness
    key -- an array carrying another lobby's colours is stale by definition, which is the
    discriminator the falsified `GlyphxID` idea was reaching for.
  - Awaiting a verification pass (mixed lobby, then a second match with an AI's colour
    changed).
- **Secondary: the read can also land mid-rebuild.** The client tears down and rebuilds its `AIPLAYERn`
  records as a match launches. A scan inside that window finds nothing, or finds a fresh array
  that disagrees with a not-yet-freed stale one, and the unanimity requirement correctly rejects
  it. The values are correct and unanimous either side of the window — a match that logged
  `ram_slots=0` had three resident copies all agreeing on the right values a minute later.
  Touching a dropdown makes the client write the records during lobby editing, so the rebuild is
  settled before launch rather than racing it.
- **Fix:** a failed read arms a deferred re-scan from `CNC_Advance_Instance`
  (`TF_Lobby_Difficulty_Retry`, 4 attempts 90 frames apart) which re-tiers the AI houses on
  success. `TF_Read_Lobby_AI_Difficulties` and its validation are unchanged.
- **Two consecutive scans must agree before a re-scan is applied.** The rebuild passes through
  half-written states that are briefly self-consistent — a lobby set to `E M H M` was caught
  reading `E M M M` — so one confident-looking read is not enough. The final attempt accepts an
  unconfirmed read rather than discarding it.
- **Evidence:** five back-to-back solo matches on the desktop (correct / `ram_slots=0` / correct /
  `ram_slots=0` / correct), plus live candidate dumps from ClientG (`dump_candidates.py`,
  `poll_candidates.py`) showing the arrays vanish and reappear across a match launch. No stale
  values were ever applied in those runs — every failure was a clean bail.
- **Falsified:** `GlyphxID` cannot discriminate live from stale arrays; the IDs are fixed per slot
  index (slot 1 read `1055504538` in two sessions hours apart), not generated per lobby.
- **Related, still unexplained:** the first solo skirmish after a LAN session once received a
  roster in `CNC_Set_Multiplayer_Data` describing the *previous* LAN lobby (8 slots, 6 AIPLAYERs
  against an actual 1+5 lobby) and spawned 6 AI houses. Same rebuild-lag family, but on the
  roster the client hands us rather than on the RAM read; re-test if it recurs.

### Hiding a cloaked building's bib frees its cell for enemy placement — ✅ FIXED 2026-07-15
- **Severity:** minor (placement exploit; enemy could build one row into a cloaked base's bib strip).
- **Root cause:** the `TF_Sync_Bib` bib-hide (building.cpp) `Disown`ed the bib `SmudgeClass`, but a bib
  smudge also **blocks placement** (`CellClass::Is_Clear_To_Build`, cell.cpp:494). Removing it both
  hid the bib AND opened the cell for the (blind) enemy.
- **Fix:** removed `TF_Sync_Bib` entirely — it was redundant. A **render-time** bib-hide already exists
  in the Remaster draw path (`dllinterface.cpp` `tf_hide_bib`, from the original stealth-gen commit
  `cd8bd17`): it keeps the smudge (placement stays blocked) and suppresses only the *draw* when the
  covering building is `VISUAL_HIDDEN` (enemy view) — transparent to the enemy, bib still shown to the
  owner. Now that the cloak driver settles buildings to `CLOAKED` reliably, this handles the hide.
  Playtest-confirmed (Luke, 2026-07-16): enemy-side bibs stay hidden.

---

## Campaign (mod enabled over stock missions)

### Tanya can't board / evac a campaign transport (no enter cursor) — ✅ FIXED 2026-07-22 (verified in-game; shipped 4.1.0, `8c69c3b`)
- **Symptom:** in stock campaigns (Tanya's Tale 5a; also Allied 1) Tanya could not be ordered
  into the evac Chinook -- no green enter cursor appeared. Einstein evac'd from the same Chinook
  fine; Tanya boarded a Chinook fine in skirmish. So: Tanya-specific, campaign-specific.
- **ROOT CAUSE:** our Tiberian Factions gate in `InfantryClass::What_Action` (`infantry.cpp`)
  restricted the enter path to `action == ACTION_SELECT`. `FootClass::What_Action` returns
  `ACTION_SELECT` for a **same-house** techno but `ACTION_NONE` for an **allied, different-house**
  one. The campaign evac Chinook is `HOUSE_GOOD` (owner 8) while the player is Greece (owner 1) --
  allied, not same house -- so for armed Tanya the base action was `ACTION_NONE` and the gate
  silently skipped the enter path. Einstein (unarmed) and skirmish (player owns the Chinook) both
  yield `ACTION_SELECT`, so they were unaffected. Proven with an `ENTERCHK` diag:
  `unit=E7 myowner=1 objowner=8 isally=1 canload=1(ROGER) action=0(NONE)` -- everything green
  except the action state the gate demanded.
- **FIX:** gate on `action != ACTION_ATTACK` instead of `== ACTION_SELECT` -- preserves the
  Ctrl-force-fire exclusion the gate was added for, restores vanilla enter for every other hover
  state. Vanilla has no action gate here at all. **Verified in-game 2026-07-22:** loaded the
  mission-1 save, selected Tanya, ordered her into the allied Chinook, she boarded (gone from map).
  Diagnostic left dormant under `#if 0` in `infantry.cpp`.
- **Sibling gates (aircraft.cpp) — FIXED 2026-07-22, shipped 4.1.0 (`46f01f3`); a skirmish
  heli-dock eyeball is still owed.** The two `Is_Ally`-gated dock overrides (helipad building ~2801, aircraft carrier
  ~2807) had the identical flaw and blocked docking at an allied different-house pad -- against the
  agreed universal-landing design (`docs/ai-upgrade-plan.md`: ANY heli may land/rearm/repair at
  ANY pad). Changed both to `!= ACTION_ATTACK`. Same-house docking (all of skirmish, any faction
  pad type) is unchanged (still `ACTION_SELECT`); only allied-house docking is newly enabled.
  ⚠️ The **repair-factory gate (~2841) was deliberately LEFT as `== ACTION_SELECT`**: it has NO
  `Is_Ally` check and relies on `ACTION_SELECT` as its implicit same-house restriction -- relaxing
  it to `!= ACTION_ATTACK` would let an unarmed aircraft dock an *enemy* repair bay. `unit.cpp`
  (~5045+) is same-house gated, not affected. Verify a skirmish helicopter still docks its own
  helipad before committing.


### Stock campaign enemy plays like a skirmish AI (over-produces, sells buildings) — ✅ FIXED 2026-07-22 (5a + skirmish-Easy-AI both verified; shipped 4.1.0, `5414de6`)
- **ROOT CAUSE:** `[IQ] Production` lowered from vanilla 5 to 3 (for skirmish Easy AIs) is global,
  so campaign enemies with a modest scenario IQ tripped the master wake-up at `house.cpp:1370`
  (`IsBaseBuilding/IsStarted/IsAlerted = true`) — waking the whole AI (build + produce + power
  manage/sell + attack). One switch = all the symptoms.
- **FIX:** `house.cpp:1370` uses the vanilla threshold (`Rule.MaxIQ`) in campaign
  (`Session.Type == GAME_NORMAL`), `Rule.IQProduction` (3) in skirmish. Verified in 5a: enemy sits
  as EA scripted. Skirmish path is byte-identical to before (else branch), sanity-check pending.
  `RepairSell=1` is stock RA, not ours. The AI_Attack aggression theory was wrong (reverted).
  Original diagnosis retained below for reference.
- **Severity:** minor (campaign is not a supported surface with the mod enabled; the mod ships
  no campaigns). Observed in **Tanya's Tale (Allied 5a)** by Luke 2026-07-21.
- **Symptoms (all "didn't used to do this"):** the Soviet enemy mass-produces infantry from
  frame 2, builds a refinery + flame towers (verified screenshot), sold power plants, and hunts
  **civilians** (neutral house) in 5a. All consistent with the campaign house running full
  skirmish-grade AI (build economy → produce → hunt everything). Only base-builder-enemy missions
  affected (5b/5c looked ok).
- **Fix approach:** our AI *enhancements* (build-choice tie-break + economy gates in
  `AI_Building`/`house.cpp` ~5897-7282; Phase-0 hunt-dispatch send-percentage + scatter; targeting)
  run for all non-human houses incl. campaign fixed houses. Gate them on
  `Session.Type != GAME_NORMAL` so campaign defers to vanilla AI. ⚠️ Do NOT disable base-building
  wholesale — some campaigns rely on the enemy rebuilding; the goal is *vanilla parity*, not a
  dormant enemy. Needs multi-mission in-game verification. NOT a blind one-line gate.
- **Diagnosis (partial):** `MOD_DEBUG_AI.txt` shows the campaign Soviet/Nod houses
  (`H2 AL2` = `HOUSE_USSR`, `H9` = `HOUSE_BAD`) running our AI build-choice pool
  (`POOL(9) -> WIN ...`) and continuous `PROD start` from frame 2, on a **fresh launch**
  (ruled out the cross-match difficulty-state leak below). NOT an IQ-forcing bug: both houses
  are below `HOUSE_MULTI1`, so `TF_Apply_AI_Difficulties` (which only touches `>= HOUSE_MULTI1`)
  never re-tiers them; they keep their scenario `Read_INI` IQ. The building-sale itself is
  **not instrumented** (zero sell/paranoid events logged), so that half is unconfirmed.
- **Why only one mission:** unknown; points to something scenario-specific in Tanya's Tale
  rather than a blanket campaign regression. Investigate under the campaign milestone.
- **Related latent defect:** our difficulty globals (`TFLobbyAIDifficultySet`, `Scen.CDifficulty`)
  are set by a skirmish match and **never reset**, so a campaign started in the same game session
  after a skirmish inherits polluted difficulty state. Not the cause here (fresh launch still
  reproduces) but worth a match-start reset.

### Campaign sidebar cameos show both faction logos — ⏳ OPEN (cosmetic, low priority)
- Deploying the vanilla campaign yard shows Allied+Soviet badges on the buildable cameos. The
  tech tree is correct (Allied-only, verified); the badge just paints each building's full
  owner-set ({Allied, Soviet} for shared vanilla buildings) with no campaign-context awareness.
  Cosmetic only. Fix when the campaign-AI work lands.

### Overlay index shift turns stock-campaign fences into crates — ✅ FIXED 2026-07-21 (verified in-game; shipped 4.1.0, `e2ce6d6`; Mobius-fork renumber still pending)
- **Fix shipped in code:** `OVERLAY_TIB01` moved to the enum END (25), vanilla indices 0-24
  restored; `odata.cpp` heap init reordered to match; `dllinterface.cpp` resource check explicit;
  `td_map_to_ra.py` synced (`TIB01=25`) and all 31 TD maps re-transcoded + redeployed. Verified
  in-game: stock fences render as fences (no heal-crate), our maps' Tiberium still renders/harvests.
- **Remaining:** renumber the Mobius editor fork
  (`../mobius-editor` `RedAlert/OverlayTypes.cs`, `TIB01=13`→25, V-fields back to vanilla) so
  hand-authored maps aren't misread. Below is the original diagnosis, retained for reference.
- **Severity:** minor (campaign not a supported surface; pre-existing since v2.0.0, shipped in
  v4.0.0 — NOT a 4.1 regression). Observed in a stock Soviet mission 2026-07-21.
- **Symptom:** wire-fence lines render and behave as goodie crates in stock campaign maps.
- **Root cause:** `OVERLAY_TIB01` (Tiberium ecosystem, commit `693bb25`, v2.0.0) was inserted
  after `OVERLAY_GEMS4`, pushing every later overlay up by one. Stock maps store overlays by
  index, so a map's `OVERLAY_FENCE` (vanilla 23) is read by our engine as index 23 =
  `OVERLAY_STEEL_CRATE`. Same shift misreads haystacks/fields/other crates.
- **Fix (Luke wants this resolved, 2026-07-21):** move `OVERLAY_TIB01` to the end of the enum
  (fresh index, unused by stock maps), restoring vanilla alignment, and change the resource-range
  check at `dllinterface.cpp:8525` to
  `(Type >= OVERLAY_GOLD1 && Type <= OVERLAY_GEMS4) || Type == OVERLAY_TIB01`.
- **⚠️ Blast radius CONFIRMED — not a code-only fix.** `scripts/td_map_to_ra.py` hardcodes
  `OVERLAY_TIB01 = 13` and `OVERLAY_CARRY = {"V12": 14, ...}` (the shifted indices), so the
  **31 shipped TD maps** were transcoded against index 13. The fix therefore also requires:
  update the transcoder (TIB01 → new index, `OVERLAY_CARRY` back to vanilla `V12=13`…),
  **re-transcode and re-verify all shipped TD maps** (Tiberium fields must still render), check
  `build_tiberium_hd.py` / `build_td_tiles.py` for index deps, and check the mod-aware Mobius
  editor fork (may also write `TIB01=13`). Its own dedicated task, not a release-eve patch.

---

## UI / interaction

### Deploy cursor appears when hovering the faction construction yards — ⏳ OPEN (queued for 4.2)
- **Severity:** minor (cosmetic/interaction; no functional effect).
- **Status:** OPEN — observed by Luke 2026-07-21, deferred to 4.2.
- **Symptom:** hovering the mouse over one of our new faction construction yards (the
  W2-split GDI/Nod/Soviet yards) shows a **deploy cursor that does nothing** when clicked. The
  vanilla yard does not do this.
- **Suspected cause (unconfirmed):** the split yard types inherited an `ACTION_SELF` /
  deployable trait path that the vanilla construction yard does not expose, so the cursor logic
  offers deploy but there is no deploy action to run. Investigate the new `STRUCT_*FACT`
  entities' action/self-action wiring against the vanilla `STRUCT_CONST`.

---

## Combat / units

### Endgame auto-sonar doesn't know the TD subs exist (found 2026-08-01, unfixed)
- Vanilla's endgame stall-breaker (`house.cpp` FIXIT_VERSION_3 block, `AutoSonarTimer` 40s
  cadence): when a house owns nothing but submarines, every sub is force-uncloaked for 15s so
  opponents can find and finish it. Both halves are hardcoded to the RA hulls only:
  - The trigger gate is `VQuantity[VESSEL_SS] > 0` (SS/MSUB share the slot count) — a Nod
    house reduced to only TDNSUB/TDOBLISUB/TDMSUB never trips it, so a cloaked TD sub can
    stall the endgame FOREVER (the exact stall the mechanism exists to prevent).
  - The "nothing but subs" census loops run over the RA-era ranges (`UNIT_RA_COUNT`,
    `VESSEL_RA_COUNT`), so TD ground units aren't counted either — a Soviet-teamed house
    with TD remnants could get pinged while it still has an army.
- Fix shape when picked up: treat all five sub hulls (SS/MSUB/TDNSUB/TDOBLISUB/TDMSUB) as
  subs in both the gate and the ping loop, and run the census over the full type ranges.
- Related context: sub concealment is the standard cloak system (`Cloakable=yes` on all five
  hulls); the only passive detection in the engine is the 1-cell adjacency shimmer
  (`foot.cpp` scanner check — all vessels and infantry are `IsScanner`), which is cosmetic
  and never acted on by the AI. Sub-detection improvements are a design discussion
  (2026-08-01), not yet a workstream.

### AI built A-10s at helipads (parked-on-pad / fly-in-and-explode) — ✅ FIXED 2026-08-01
- **Symptoms (both player-observed, Docklands skirmishes):** a GDI A-10 parked dead-center on
  a helipad; later the same day, an AI A-10 "flying in like a helicopter" to a loaded helipad
  and self-destructing on arrival. AI economy bleed: money spent on aircraft that explode.
- **Root cause (proven by TF_AI_DIAG):** `PROD start TDA10 ... at factory TDGHPAD#86` — the
  per-building factory logic asks `Suggest_New_Object(RTTI_AIRCRAFTTYPE)`, and the house-level
  `BuildAircraft` choice does not know which factory is asking, so whichever aircraft factory
  ticks first takes the order — including a helipad taking a fixed-wing. `Exit_Object` then
  spawns it parked on a free pad (`Docking_Coord`, Height=0), or map-edge-flies it in when the
  pad is tethered; an undockable fixed-wing self-destructs at touchdown (`Landing_Takeoff_AI`).
  All the docking/`Who_Can_Build_Me` chains were audited type-correct — production assignment
  was the one unguarded path.
- **Fix:** the wrong-family factory DECLINES the order (helipads take rotary only, the
  airstrip family fixed-wing only) and leaves it for a sibling; an order cannot strand because
  `Can_Build` already requires the airfield prerequisite for fixed-wing types.
- **Related fix, same session (`0c12624`):** the out-of-ammo rearm search was hardcoded
  `Find_Docking_Bay(STRUCT_HELIPAD)`, which fixed-wing can never satisfy — an AI A-10 with
  empty ammo never found its airfield and flew disarmed forever. Now searches the aircraft's
  home-building family (airstrip family matching made symmetric).
- `FIXEDWING-LAND` touchdown census (TF_DEV_BUILD) left in for regression-watching.

### AI superweapon targeting ignores stealth-generator cloak — ✅ FIXED + PLAYER-VERIFIED 2026-08-01
- **Was:** GDI AI ion-cannoned the player's airfield while it sat inside a Nod stealth
  generator field. Vanilla AI superweapon target selection predates building cloak and never
  checked visibility.
- **Fix (`0164b7f`):** `Special_Weapon_AI` skips any building `Is_Cloaked(this)` — discovery
  stays sticky intel, but the live cloak veils the strike, forcing target displacement exactly
  like direct fire. Cloak state already encodes detector coverage (a detector forces the
  uncloak), so no separate detector check is needed.
- **Verified in play the same day:** "enemy going for the unstealthed stuff" (Luke, live
  Docklands match with stealth generator up).

### Recon Bike (TDBIKE) won't turn to fire at off-axis targets — ✅ FIXED 2026-06-16
- **Severity:** major (unit was much less effective; affected Nod harass doctrine).
- **Status:** RESOLVED — `UnitClass::Rotation_AI` (unit.cpp:601).
- **Root cause:** for turretless vehicles, RA only rotates the hull to face a target if the unit is
  **tracked** ("wheeled vehicles never rotate to face the target — not maneuverable enough"). TDBIKE is
  wheeled, so it never turned and only fired at whatever it already faced. TD's source special-cases its
  wheeled bike to rotate anyway (`tiberiandawn/tarcom.cpp:166`, `|| *this == UNIT_BIKE`); RA left that
  clause commented out (vanilla RA has no bike). Fix = restore the exemption for `UNIT_TDBIKE`. Now uses
  the same body-rotate-in-place path as the (tracked, turretless) Artillery, which always worked.

---

## AI base building

### A house that cannot place a building retries the same doomed search forever — ✅ FIXED 2026-07-31
- **Was:** major. GDI repeatedly failed to place `TDPROC` / `TDWEAP` / `TDFIX` while holding
  thousands of credits (one match: `TDFIX` started 16 times, completed zero; base stalled at
  `CurB≈10`). The bulk of the "sluggish GDI" feel. Nod showed a second mode: a broke order
  logged `PROD abandon TDPROC pct=0 cash=24` and vanished.
- **Root cause (named by the per-predicate reject counters, `b3152de`):** `Recalc_Center`
  (`house.cpp`) divides the **unweighted** sum of building distances by the **cost-weighted**
  count it builds for the centroid, so an expensive base computes a `Radius` 2-3x too small —
  a live Nod base of 7 buildings sat at `radius=518` leptons, the 512 floor. `Which_Zone`
  returns `ZONE_NONE` past `Radius * 4`, so the whole build-site search collapsed to a disc
  the base itself filled (airfield scan: 16,384 cells, 7,888 out-of-zone, the 176 in-zone all
  footprint-blocked, `ok=0`). EA-original 1995 arithmetic; worst for expensive wide-footprint
  TD bases.
- **Fixes (all three EA-original defects):**
  1. `6604354` — Radius divides by the building quantity; cost weighting stays centroid-only.
  2. `eb5d6d8` — the try-any-zone fallback in `Find_Build_Location` returned a raw `CELL`
     where the caller expects a `COORDINATE`; now wrapped in `Cell_Coord()` like the
     preferred-zone path (broken since 1996, `REDALERT/HOUSE.CPP:4669`).
  3. `265d632` — an unstarted computer order (Start() refuses when the first tick is
     unaffordable) is held on the 3-second retry timer while the house has income
     (`TF_Has_Income`: refinery + live harvester + tiberium), instead of being scrapped on
     the next pass. Mirrors the human sidebar, where a broke order pauses.
- **Verified 2026-07-31** (full skirmish to F11,944, log `MOD_DEBUG_AI.radius-after.txt` vs
  `.radius-before.txt`): **0 `PLACE-FAIL`, 0 `PROD abandon`**; at 7 buildings radius read
  850-950 instead of 518; GDI peaked `CurB=14`, `Rad=2111`, past the old stall.
- **Zone filter made real in `85883e1` and VERIFIED (2026-08-01):** `Find_Cell_In_Zone` now
  restricts the sweep to the requested zone, so the defence-rated zone is the actual placement
  target and each fallback pass searches fresh ground. Verified on the DOCKLANDS run: zero
  `PLACE-FAIL` across ~12,800 frames, radii healthy to 1,756 leptons. Corroborated the same
  night by the autonomous soak: **zero `PLACE-FAIL` across 43 matches** (Docklands + Deep Six
  Mega, GDI at Easy/Medium/Hard, deepest F11,507 with GDI at 22,400 gathered) —
  `docs/lobby-ambiguity-data/overnight-2026-08-01-results.md`.
- **FALSIFIED — do not re-chase:**
  - *"TD buildings aren't valid proximity anchors."* No: the ownership test needs
    `base->Class->IsBase`, `IsBase` defaults true, and `TDPROC`/`TDWEAP`/`TDFIX` all set
    `BaseNormal=yes` explicitly.
  - *"Infantry spam starves the expensive builds of funds."* No: GDI's failures were all
    placement with healthy cash, and `PROD abandon` never fired for GDI.
  - *"The 4x zone multiplier is too narrow."* The multiplier is fine — the **Radius feeding
    it** was collapsed (see root cause).
  - *"`PROD start` means a build completed."* No — it only means an order began. Reading it as
    completion produced three wrong conclusions in one session; always confirm against `CurB`,
    the `ROLE` counts, or the player's eyes.

### The economy gate counts buildings that are still in limbo (2026-07-23)
- **Severity:** minor on its own, but it decides *which* building gets thrashed above.
- **Status:** root-caused, confirmed in code, **not fixed** (it is the passenger, not the driver).
- **Cause:** `house.cpp:7143/7152` gate `tf_economy_ready` on `TF_Role_Quantity(BQuantity, ...)`.
  `BQuantity[]` increments in `Tracking_Add` when the object is **created in limbo** — the moment
  production starts — whereas `ActiveBQuantity` "mirrors ActiveBScan semantics (unlimbo'd +
  locked)" per its declaration comment in `house.h`. So starting a war factory immediately reads as
  *owning* one, which unlocks `TDFIX` at a higher urgency; when `TDFIX` takes over the count drops
  back to zero and `TDWEAP` wins again. A two-state oscillator, visible in the log as `ROLE`
  flipping `weap=1/1 fix=0/0` <-> `weap=0/0 fix=1/1` every decision cycle. `CurBuildings` shares the
  property, which is why `CurB` counts buildings that were never placed.
- **Fix direction:** gate `tf_economy_ready` on `ActiveBQuantity` (completed only); leave the
  "do I need another one of these" counts at 7310/7381/7421/7599/7624 on `BQuantity`, since those
  *should* see in-flight orders or the AI will queue duplicates.

## Pathfinding / AI cooperation

### Units livelock retrying a doomed path forever — ✅ CLOSED 2026-08-01 (crash fixed+verified; wedges cured; storm deferred to naval)
- **Final status:** the give-way recursion CRASH is fixed and verified (two long matches, no
  artifacts). The in-base wedge livelock is cured by the no-progress detector. The
  unreachable-target retry storm is NOT curable by give-up logic (measured 8.96 vs 8.4
  fallbacks/frame with detector v2 + scan-limit) — those units simply have no ground route;
  the cure is AI naval transport (`ai-upgrade-plan.md`), Luke's call 2026-08-01. Full verdict
  + falsification history: `path-failure-livelock-design.md`.
- **The 2026-08-01 DOCKLANDS `EXCEPTION_STACK_OVERFLOW` was a SEPARATE defect the livelock merely
  fed.** Walking the crash minidump (`InstanceServerG.exe_2026-08-01_00-17-47_T472.dmp`, raw
  stack scan + addr2line) showed ~1,500 repetitions of one cycle: `Start_Of_Move` give-way
  RETREAT (`drive.cpp` gw==2) → `Assign_Destination(back)` → nested `Start_Of_Move` (engine calls
  it for a stationary unit) → RETREAT again — unbounded mutual recursion in OUR v2.2.3 give-way
  code whenever a pinch is so jammed the retreat decision repeats. The earlier "stack death is in
  the legacy fallback under retry-storm volume" reading was wrong (the legacy pathfinder is
  iterative). Fixed with a call-stack re-entrancy guard: a retreat-triggered nested
  `Start_Of_Move` skips give-way evaluation and paths straight to the retreat cell.
- **Status:** livelock root cause CONFIRMED 2026-07-19; **both fixes implemented 2026-08-01**
  (recursion guard above + the no-progress detector below, `FootClass::TF_Path_No_Progress`:
  infantry give-up branch aborts after 8s of zero progress on the same (cell, destination) pair;
  the vehicle patient queue yields to the abandon branch after 60s of literally zero movement —
  a genuinely queued column advances cells, which restarts the window). Old savegames break
  (FootClass grew), accepted like the SuperWeapon-enum growth. Two earlier dead ends are recorded
  in the design doc: never call the virtual `Assign_Destination()` from inside `Basic_Path()`
  (crashed both machines), and the `Nearby_Location` guard alone (falsified).
  **Verification pending:** DOCKLANDS-style rerun on the fixed build.
- **⭐ Full detail: `docs/path-failure-livelock-design.md`. Read it before touching this** — it
  records both dead ends, and both are easy to walk straight back into.
- **Symptom:** the same `(unit, src, dst)` triple repeats in `tf_astar.log` hundreds of times in
  one match: `TDE1 src=(40,40) dst=(35,33)` x598, `TDE6 src=(28,77) dst=(28,77)` x260. Retry
  cadence is `PathDelay` ≈ 14 ticks, so ~4 attempts/second/unit. Predates the A* heap work
  (visible in pre-heap logs).
- **Cause:** the give-up branch at `infantry.cpp:4346` clears `NavCom` **only when the destination
  is in a different movement zone**. Movement zones ignore buildings by design, so anything walled
  off is "same zone" but unreachable and never aborts — and a cell is always in its own zone, so
  the `src==dst` case can never satisfy the test at all. Vehicles have the same defect by a
  different route: the patient queue at `drive.cpp:2180` resets `TryTryAgain` every cycle whenever
  a neighbour holds traffic, which inside a busy base is ~always.
- **Framing correction (important):** `src==dst` is NOT the bug, just its most visible subtype.
  The largest livelocks are ordinary reachable-looking destinations. Anything scoped only to
  self-cell addresses a minority of the problem.
- **Recommended cure:** a no-progress detector (N consecutive identical failures -> abort
  regardless of zone), the same pattern already shipped in `harvester-recovery-design.md`. Not a
  zone fix — zones ignoring buildings is by design and was rejected as a target once already.
- **Success signal:** repeated-`(unit,src,dst)` counts collapse to single digits while total
  `src!=dst` failures stay near baseline (~2800-3200/match desktop, ~1500 Deck).
- **Probably the same root cause as "Deadlock-breaker micro-churn on returners" below** (a `2TNK`
  observed doing 67× `src==dst`); re-check that entry when this is fixed.

### Thousands of genuine path failures per match — UNINVESTIGATED 2026-07-19
- **Severity:** unknown, potentially major (larger in volume than the livelock above).
- **Detail:** with livelock cases excluded, genuine `src!=dst` path failures still run ~2800-3200
  per desktop match and ~1500 per Deck match, harvesters prominent (`TDHARV` at 1584 and climbing
  in one Deck match). Surfaced while measuring the livelock; never investigated on its own.
  Unclear how much is normal churn (a fallback to the legacy edge-follower is not automatically a
  failure to move) versus real lost unit-time. **Establish that baseline before treating it as a
  bug.**

### Vehicle-vs-vehicle head-on in a 1-tile gap with no escape cell (breaker unreachable from gw==2)
- **Severity:** minor (self-resolves — the boxed unit eventually dies/clears; never escalates to gridlock).
- **Status:** OPEN — remaining give-way loose end after v2.3.0.
- **Detail:** when `Give_Way_Decision` returns gw==2 (RETREAT) but `Find_Give_Way_Cell` finds no free
  escape cell, the unit holds and never reaches `Try_Deadlock_Scatter`, so the breaker can't fire on
  that case. Fix = make the breaker reachable from the gw==2 path. NOTE: the original "breaker is in the
  WRONG BRANCH" issue (it only lived in the no-path branch, missing execution-time head-on `MOVE_NO`
  clumps) was FIXED in v2.3.0 — `Try_Deadlock_Scatter` is now called from the execution head-on path
  (`drive.cpp ~2301`) as well as the no-path branch. See `docs/chokepoint-reservation-design.md`.

### Deadlock-breaker micro-churn on returners
- **Severity:** minor (cosmetic jiggle; unit not lost).
- **Status:** OPEN — noted 2026-06-16.
- **Detail:** a unit can scatter then re-path straight back into the stuck spot and spin (observed a
  `2TNK` doing 67× `src==dst`). Consider capping re-scatter when a unit keeps returning (likely an
  unreachable goal, not a breakable deadlock). See the checkpoint doc.

### Recurring west map pinch (~cell x90, y63 on the test snow map)
- **Severity:** minor (units congest there repeatedly; never escalates to map-wide gridlock).
- **Status:** OPEN — noted 2026-06-16; watch whether the breaker-branch fix resolves it.

---

## Harvester logic / economy (own workstream)

### Harvesters spin forever on an unreachable resource
- **Severity:** major (idle harvesters = dead economy for those units).
- **Status:** OPEN — own workstream (deferred to a dedicated segment, Luke 2026-06-16). Targeting /
  pathing / claiming / reachability.
- **Detail:** when ore/Tiberium is unreachable (e.g. the AI walls its own gems field with buildings) a
  harvester A*-fails → `ABANDON-giveup` → AI re-orders → loops forever instead of re-selecting a
  reachable field. Same root hit a tank ordered into a base-blocked cell. Also: 2 harvesters jammed at a
  refinery dock (contention). **Diagnostic note:** an idle/abandoned harvester emits NOTHING to
  `tf_astar.log` — this workstream needs its own instrument. See `docs/chokepoint-reservation-design.md`
  CHECKPOINT 2026-06-16 (spun-off workstreams) + memory `project-cfe-port-plan`.
- **✅ LARGELY FIXED 2026-06-17 (symptom-patch hardened + playtest-validated; canonical write-up
  `docs/harvester-recovery-design.md`).** The "fix it properly via zone recompute on building events"
  plan was **REJECTED** after reading the code: `Zone_Span` ignores buildings *by design* (the
  `ignorevehicles` mask `0x5F` drops the Building occupy bit `0x80`, cell.cpp:3125), so making buildings
  call `Zone_Reset` is a no-op, and the building-aware variant that would be needed changes the global
  meaning of `Zones[]` (AI targeting / A* gate / `Is_In_Same_Zone` / base placement) — MP-determinism-
  risky, not worth it. **Chosen instead = harden the proven pathfinder-agnostic no-progress detector:**
  (1) `Blacklist_Harvest_Cell` flood-fills the whole contiguous ore field and blacklists its bounding
  box (was a single cell ±3, which let big walled fields keep re-spinning); (2) on no reachable ore the
  harvester pulls back toward a refinery + re-scans instead of idling at the wall. Playtest 2026-06-17:
  whole-field bboxes captured (28/66/45 cells) and harvesters redirected to a different reachable patch
  — Luke accepted as-is. Detector is a robust safety net for *any* unreachable-target case (not just
  buildings). Logs `HARV-BLACKLIST`/`HARV-WAIT` are `TF_DEV_BUILD`-gated (compiled out of release).
- **✅ FIELD SELECTION + BLACKLIST OVER-FIRING 2026-06-18 (commits `2465ae9` + the follow-up, on `main`,
  v3.0-gated). Desktop-validated across several AI matches.** Three linked fixes to `Goto_Tiberium` /
  the no-progress detector:
  1. **Travel-distance field pick.** The ring search returned the densest cell in the FIRST crow-flies
     ring with ore, so a field near in a straight line but only reachable the long way around water/cliff
     beat a closer-by-road one (Luke's SS #1). The LOOKING-state pick now gathers the NEAREST ore cell of
     each of the closest `HARV_FIELD_CANDIDATES`=10 rings and chooses the shortest ACTUAL A* path
     (`Find_Path_AStar`, null `resultPath` = cheap length-only query), density only a tiebreak.
  2. **Candidates by PROXIMITY, not density.** First cut picked each ring's *densest* cell — but a thin
     near field (low value) loses to a thick far/contested one, so harvesters drove across the map past
     close ore (the "ignored the field by the refinery, went south" reports). Proximity + A*-min-path
     fixed it; density-as-primary was the bug, NOT depletion (the near fields were full, just lower-value).
  3. **A* threshold = `MOVE_MOVING_BLOCK`, and the blacklist gated on real reachability.** The v2.4.0
     no-progress detector blacklisted any field a harvester couldn't approach for 5s — but base traffic /
     parked vehicles / friendly infantry produce that same symptom, so reachable home fields got
     blacklisted and harvesters fled (343 blacklists/session). Now the 5s stall consults A*: a path exists
     (congestion) → don't blacklist, grant up to 3 windows (~15s) then a bounded backstop; A* returns 0
     (genuinely walled) → blacklist as before. Querying at `MOVE_MOVING_BLOCK` (not the strict
     `PathThreshhold`) treats units-on-the-route as passable (they move / give-way pushes them) while
     walls/buildings/water still block — so unit-blocked near fields stop reading `apath=0`. Result:
     **343 → ~3 blacklists/session, all legitimate** (AI walling its own field with buildings; 1-cell
     remnant patches). New member `HarvReachableResets` (serialized with the unit). TF_DEV `HARV-FIELD`
     dumps each candidate's zone/value/apath + the nearest-ore/blacklist state.
  ⬜ STILL OPEN (follow-ups, not blockers): **exponential blacklist backoff** (a persistently building-
  walled field un-blacklists every 15s and gets re-poked — give repeat failures a longer TTL);
  **threat-aware selection** (don't route through enemy fire).
- **✅ ADDRESSED 2026-06-18 — harvester stuck/idle recovery + dock contention (#5, #6, dock).** Shipped
  (committed, v3.0-gated): `525910b`/`2d46def`/`49f8157`. See `harvester-docking-session-handover.md`
  (⭐ 2026-06-18 section) for the full write-up. Summary:
  - **Anti-stuck watchdog** (`UnitClass::AI`, position-stagnation, any mission): recovers wedged AND
    gave-up/idle harvesters (3s shove infantry → 6s `Try_Deadlock_Scatter` → 12s restart). Exempts only a
    HUMAN's manual MOVE/GUARD park. **Field-blacklisting stays owned by the ore-pursuit detector** (the
    watchdog must NOT blacklist — it can't tell "field walled" from "harvester wedged"; that poisoned
    good fields, `blskips=151`). Validated 83→4 blacklists, no loops.
  - **Field-richness gate** (`Goto_Tiberium`): prefer a field with ≥ half a load over a closer lone
    regrown block; tier-2 fallback = richest reachable. `Field_Tiberium_Value` + `HARV_FIELD_LOAD_DIVISOR`.
  - **Layer B harvester-only dock pad** + **dock staging** (per-harvester `Nearby_Location` locationmod).
  - **Corrected belief:** on the real maps the dominant "stuck" cause is **terrain** (cliff/water-split
    ore + narrow gaps) and **the AI walling its own ore/harvester with buildings**, NOT idle infantry
    (the 2026-06-17 "scatter friendly infantry" hypothesis was wrong — a 91-event sample was
    terrain/building-dominated, ally-infantry pins ≈ 0). A genuinely AI-box-in harvester (turret placed
    trapping it against the refinery+water) is OUT OF SCOPE — an AI placement problem.
  ⬜ STILL OPEN: **threat-aware field selection** (don't route through enemy fire). ⚠ BLOCKER: the engine
  region-threat map (`Cell_Threat`) is `Session.Type==GAME_NORMAL`-gated (`object.cpp:1859`) so it is
  INERT in skirmish — must build on a custom enemy-proximity scan instead. Design in the handover doc.
- **(earlier) ROOT CAUSE FOUND + partial fix for the walled-field loop (2026-06-16):** the autonomous scan
  `UnitClass::Tiberium_Check` (unit.cpp:2519) ALREADY zone-filters (`Map[Coord].Zones[MZone] !=
  Map[center].Zones[MZone] → 0`), so `Goto_Tiberium` correctly finds "no reachable tiberium" when the
  only field is walled off. The infinite spin was the **`ArchiveTarget` fallback** in `Mission_Harvest`
  LOOKING (unit.cpp:3291): it re-dispatches the harvester to its last-mined cell **with no reachability
  check** and (unlike the sibling site at 3256) never clears it. So path-fail → NavCom clears → re-scan
  finds nothing reachable → archive still legal → re-dispatch to the same unreachable cell → loop (the
  "256 fallbacks"). **FIX (commit pending):** guard that reassignment with
  `Is_In_Same_Zone(As_Cell(ArchiveTarget))`; if the archive is gone/unreachable, clear it and fall to
  GOINGTOIDLE instead of charging it forever. Surgical — only changes behaviour in the exact failure
  case (archive in a different zone), identical in normal harvesting. **STILL FOR THE SEGMENT:** target
  CLAIMING (two harvesters picking the same patch), refinery dock contention, the same-zone-but-
  dynamically-blocked case (a partial wall / unit blocking a reachable-by-zone route), and finding a
  reachable field beyond TiberiumLongScan range. This fix only kills the walled-off-field spin.

### Economy asymmetry: GDI/Nod dock (slow) vs RA auto-dump (fast)
- **Severity:** balance (intended TD-authentic behaviour, not a bug — but a candidate to equalise).
- **Status:** PROPOSAL — make RA also dock (dwell on the tilted-bucket unload frame) for a matched time.
- **Detail + balance interaction:** see `docs/balance-deep-dive.md` (economy asymmetry section) — note
  equalising removes the GDI/Nod slower-economy counterweight to their cheaper army + the Mammoth.

---

## Launcher / engine limitations (cannot be fixed from a mod — do not re-investigate)

### Select-all (A) and Deploy (/) hotkeys ignore GDI/Nod harvester + MCV
- **Severity:** minor, player-facing.
- **Status:** WON'T FIX (launcher-hardcoded unit identity; not reachable from the DLL/mod).
- **Workaround:** drag-box to select army; click the MCV with the deploy cursor to deploy. Documented in
  the Workshop "Known limitations". MCV deploy hotkey spike resolved-negative (memory
  `project-mcv-deploy-hotkey-spike`).
- **Scope widens at W2 b3 (accepted by Luke, 2026-07-19):** the MCV split replaces the vanilla
  `MCV`/`TDMCV` with four faction MCV types (`AMCV`/`SMCV`/`TDGMCV`/`TDNMCV`) in skirmish, so
  the deploy hotkey stops working for **Allied and Soviet too** — the GlyphX gate keys on
  vanilla enum identity and no new type can have it. Mouse self-click deploy remains for all.

### Classic graphics mode dropped (HD-only)
- **Severity:** by-design, player-facing.
- **Status:** WON'T FIX — classic completely dropped once the TD theatre tilesets were added (no classic
  art path → terrain/units render broken). HD is the only supported mode. The classic spacebar toggle
  can't be locked from the mod side (launcher-owned; clean lockout is network-games-only). Memory
  `feedback-classic-graphics-unsupported`.

---

## Localization

### Localized SFX file clobbers DE/FR voice dub
- **Severity:** minor, non-fatal (German/French players hear English voices).
- **Status:** OPEN backlog.
- **Detail:** our `SFXEVENTSLOCALIZED.XML` is a 981-event all-`_EN-US` file overriding every player's
  localized voices. Fix = trim to TD-only events. Memory `project-localized-sfx-clobbers-dub`.

---

## Multiplayer / LAN

### LAN crashes with crates enabled
- **Severity:** major for LAN (single-player skirmish unaffected).
- **Status:** OPEN, uninvestigated.
- **Workaround:** turn crates off for LAN play (per the Workshop "Known limitations"). Not yet root-caused.

---

## Resolved
<!-- Move fixed issues here with the fix commit, e.g.:
- Immortal-claim whole-map gridlock — FIXED 6f35ea9 (claim-on-crossing). -->
- Immortal-claim whole-map chokepoint gridlock — FIXED `6f35ea9` (claim-on-crossing). See
  `docs/chokepoint-reservation-design.md` CHECKPOINT 2026-06-16.
- TD temperate coastal tiles rendered as white squares (shores/bridges) — FIXED `ede7ca1`.
  The `TDSH*`/`TDBRIDGE*` `<Tile>` blocks were missing from `RA_TERRAIN_TEMPERATE.XML` so the
  launcher couldn't resolve their AssetNames. Cause: `build_td_tiles.py` spliced the shared
  `TF_TD_TILES` marker once **per theatre letter**, but `T` (temperate) and `S` (winter) both
  target the temperate XML and `splice()` replaces the whole block — the winter pass (added with
  the winter/desert theatres, `7c80fde`) overwrote the temperate shore/bridge block. Only visible
  on TD temperate coastal maps (e.g. TD Lost Arena); winter/desert maps were unaffected, so it
  shipped unnoticed. Fix: group the XML splice by destination file + restore the dropped blocks.

---

## Skirmish setup

### GDI/Nod skirmish "starting units" bonus gives RA units, not TD
- **Severity:** minor.
- **Status:** OPEN (post-1.0, unverified since; migrated from memory 2026-07-15).
- **Detail:** with UnitCount>0, the MCV spawn is faction-correct (Create_Units spawns UNIT_TDMCV) but
  the bonus combat units (tot_units = UnitCount*2/3; tot_infantry = remainder, scenario.cpp:3023) fill
  from RA's unit-selection logic with no TD-faction branch -> GDI/Nod get RA vehicles/infantry. Fix: add
  a TD-faction branch to the bonus-unit picker, mirroring AI_Unit/AI_Infantry's Can_Build approach.
