# Known issues

**Status:** Tracker. Open bugs, and player-facing limitations a mod cannot fix.

The tracker for open bugs, and for player-facing limitations a mod cannot fix, so nobody
re-investigates them. Checked against main at the 5.0.0 release (2026-10-04).

Each entry gives a **severity** (blocker / major / minor / cosmetic) and where the detail lives.
When an issue is fixed, delete its entry: the commit message and `CHANGELOG.md` record the fix.
A dead end worth warning about stays as one line in the topic doc it belongs to.

---

## Units and buildings

### Deploy cursor shows on a construction yard when the player owns two or more
- **Severity:** cosmetic (the click does nothing).
- `BuildingClass::What_Action` keeps `ACTION_SELF` on a factory whose house has more than one of
  its kind (`Factory_Counter(ToBuild) > 1`), so another factory can be set primary. The switch has
  no case for `RTTI_BUILDINGTYPE`, so a yard keeps `ACTION_SELF` too, which the launcher draws as
  the deploy cursor, and `Active_Click_With` has no yard handler. EA's `STRUCT_CONST` code is the
  same, so any second yard shows it.
- Fix shape: `ACTION_NONE` for `RTTI_BUILDINGTYPE` in that switch. MCV undeploy goes through
  `ACTION_MOVE` and is not affected.

### Endgame auto-sonar ignores the TD subs
- **Severity:** minor (a Nod house down to cloaked TD subs can stall the endgame forever).
- The stall-breaker in `house.cpp` (`AutoSonarTimer`, 40 s) uncloaks every sub of a house that
  owns nothing else. Its gate is `VQuantity[VESSEL_SS] > 0` and its ping hits only `VESSEL_SS` and
  `VESSEL_MISSILESUB`, so TDNSUB, TDOBLISUB and TDMSUB never trip it. The "nothing but subs"
  census runs over the RA ranges (`UNIT_RA_COUNT`, `VESSEL_RA_COUNT`, infantry up to
  `INFANTRY_DOG`), so TD and TS units are not counted either.
- Fix shape: all five sub hulls in the gate and the ping, and the census over the full ranges.

### A sold or destroyed Tesla Coil leaves a TS rifleman
- **Severity:** minor.
- `BuildingClass::Crew_Type` (`building.cpp`) gives every building whose IniName starts with "TS" a TS
  Light Infantry (`INFANTRY_TSE1`) as its survivor. The RA Tesla Coil is `TSLA` and `Crewed=yes` in
  rules.ini, so it matches. Found in the code, not yet seen in play.
- Fix shape: test `Class->Is_TS_Era()` instead of the IniName prefix.

### Infantry pushed aside in a narrow pass lose their orders (suspected)
- **Severity:** minor.
- When a vehicle drives through a one-cell pass, `DriveClass::Drain_Infantry_Along` (`drive.cpp`)
  gives each untethered friendly infantryman ahead a one-cell `MISSION_MOVE` out of the way, and
  nothing restores his order. A soldier walking through the pass, or an engineer on
  `MISSION_ENTER` heading to capture, would stop one cell aside and stay there. Not yet seen in play.
- Fix shape: re-issue the man's mission and destination once he has stepped aside, or push only
  men with no order of their own.

---

## Audio and launcher art

### GDI and Nod players' RA special infantry answer in TD soldier voices (suspected)
- **Severity:** cosmetic.
- `InfantryClass::Response_Select`, `Response_Move` and `Response_Attack` (`infantry.cpp`) return
  TD's generic lines for every infantry type when `PlayerPtr->ActLike` is GDI or Nod, before EA's
  per-type answers for Tanya, dogs, spies, medics, thieves and Einstein. A GDI or Nod player holding
  an Allied or Soviet yard trains those units, so they would answer as TD riflemen. Not yet seen in
  play.
- Fix shape: take the GDI/Nod branch only for types without their own response set.

### Waypoint and rally markers show the Allied emblem for TS GDI
- **Severity:** cosmetic.
- The launcher draws both markers from `RA_UI_ALLIED_LOGO_SMALL` (`RA_UI_SOVIET_LOGO_SMALL` for
  the other side), chosen by side, and TS GDI rides an Allied country house. There is no marker
  draw code in the DLL. A loose atlas repaint is global, so real Allied players would get the
  eagle too.
- Route: the RAM lever in `radar-crest-ram-spike.md`, re-pointing ClientG's cached region record
  at match start. The crest patch handles two records today (`TF_CREST_SLOTS 2`).

### Localized SFX file overrides the German and French voice dubs
- **Severity:** minor (DE/FR players hear English voices).
- `Data/XML/AUDIO/SFXEVENTSLOCALIZED.XML` carries 985 events, every sample `_EN-US`, and replaces
  every player's localized voices. Fix: trim it to the events the mod changes. The EVA mailbox
  relies on the `RA*_SFX_EVA_*` names, so check those before cutting any RA event.

### Campaign sidebar cameos show both faction badges
- **Severity:** cosmetic (stock campaigns with the mod on).
- `TF_Compute_Producer_Masks` ORs each owned yard's owners into the badge mask, and the vanilla
  `[FACT]` is `Owner=allies,soviet`, so every cameo gets both badges. The tech tree is right; the
  badge code has no campaign awareness.

---

## Multiplayer

### LAN joiners' credit tick: untested
- **Severity:** minor.
- In LAN the host alone simulates, so the DLL's faction-routed tick (`credits.cpp`
  `CreditClass::AI`) fires on the host. `TF_Fire_Credit_Tick` addresses it to the house whose
  credits moved (`DLLExportClass::On_Sound_Effect(house, ...)`), as EA's beacon does.
- One LAN match settles it: either joiners hear their own faction's tick (done), or the host hears
  everyone's, which means the id is a local filter and the data-side route in
  `building-sound-routing.md` §2 is needed.

### The radar on/off sting never plays with two or more humans
- **Severity:** cosmetic.
- The debounce in `HouseClass::AI` (`tf_radar_on`, `tf_pending`, `tf_stable`) is function-static,
  shared by every human house. With two or more humans their states alternate, nothing holds the 8
  frames the debounce needs, and no sting plays (it never loops). Fix shape: per-house state.

### First solo skirmish after a LAN session spawned the LAN lobby's AIs (seen once)
- **Severity:** minor, unreproduced.
- `CNC_Set_Multiplayer_Data` handed over the previous LAN lobby's roster (8 slots, 6 AIs against an
  actual 1 + 5) and six AI houses spawned. Re-test if it recurs.

---

## Balance data

### The Allied artillery's range change never applies
- **Severity:** major (a balance change that shipped in name only).
- The mod's `CCDATA/aftrmath.ini` always loads after `rules.ini` (`Is_Aftermath_Installed()` is true in
  the remaster) and overrides field by field. Its `[155mm] Range=6` beats `rules.ini`'s 8, so the
  Allied Artillery plays at 6 while `balance-deep-dive.md` records 6 → 8. Its `[E3] Owner=allies`
  also beats `rules.ini`'s `allies,soviet`. Found in the data, not yet checked in play.
- Fix shape: set the intended values in `aftrmath.ini` too (`td-building-separation-recipe.md`,
  gotcha 16), after deciding what E3's owner should be.

### `Inaccurate=` does nothing on projectiles
- **Severity:** major (balance).
- EA's `BulletTypeClass::Read_INI` (`bbdata.cpp`) reads the misspelt key `Inaccuate`, so the eight
  `Inaccurate=yes` lines in `rules.ini` (`[Ballistic]`, `[TDSSM]`, `[TDSSM2]`, the TD missiles) are
  ignored: those shots are accurate unless the firer moves. The artillery's Range 8 was justified by
  that scatter. `[TDMSUB]`'s `Inaccurate=` is read by nothing.
- Fix shape: either key the entries as `Inaccuate=`, or fix the parser with a `// TF:` change. Both
  change balance, so it needs a play test.

## AI and pathfinding

### Sim froze once in a 4-Hard-AI Docklands match (2026-09-02)
- **Severity:** unknown, unreproduced.
- Every DLL log stopped inside frame 22357 (about 11 minutes); ClientG kept spinning at about 60%
  CPU; no minidump, no A* storm. A rerun of the same build and lobby ran to F45000 clean. Logs:
  `docs/ai-ab-2026-09-02/g4-docklands-4ai-hang-MOD_DEBUG_AI.txt`.
- Next time: poll the AI log size every 5 s and on a 20 s stall run
  `gdb -p <pid> -batch -ex 'thread apply all bt 30'` on the sim process (gdb attaches under Wine;
  breakpoints never fire).

### The economy gate counts buildings still in limbo
- **Severity:** minor.
- `tf_economy_ready` (`house.cpp`) counts refineries and war factories with
  `TF_Role_Quantity(BQuantity, ...)`. `BQuantity` rises when production starts, so an unbuilt war
  factory reads as owned and unlocks `TDFIX` early. Fix shape: gate on `ActiveBQuantity`; leave the
  "do I need another" counts on `BQuantity`, which must see in-flight orders.

### Lobby difficulty state survives into the next game
- **Severity:** minor, no symptom seen.
- `TF_Apply_AI_Difficulties` sets `TFLobbyAIDifficultySet` and `Scen.CDifficulty`, and nothing
  resets them, so a campaign started after a skirmish in the same session inherits them. Fix
  shape: reset both at match start.

### Thousands of genuine path failures per match: baseline not set
- **Severity:** unknown.
- With livelocks excluded, `src!=dst` path failures run about 2,800 to 3,200 per desktop match and
  1,500 per Deck match, harvesters prominent. A fallback to the legacy edge-follower is not
  automatically a unit that failed to move; set that baseline before treating it as a bug.
- One cheap target is known: the Amphibious APC (TSAPC) searched from its own cell 1,352 times
  in one headless AI match (`path-failure-livelock-design.md`).

### Head-on in a one-tile gap with no escape cell
- **Severity:** minor (self-resolves when one unit dies or clears).
- In `drive.cpp`, when give-way decides RETREAT (`gw == 2`) and `Find_Give_Way_Cell` finds no
  cell, the unit stops and returns, so neither `Try_Deadlock_Scatter` nor the vehicle no-progress
  detector runs. Fix shape: let that path reach the breaker. `chokepoint-reservation-design.md`.

### Deadlock-breaker churn on returners
- **Severity:** cosmetic.
- A unit can scatter, re-path straight back into the stuck spot and repeat (a `2TNK` did it 67
  times). `Try_Deadlock_Scatter` has no re-scatter cap, and the no-progress detector misses it
  because each scatter changes the source cell. Probably an unreachable goal. A recurring pinch on
  the old test snow map (about cell 90,63) looks the same.

### Harvester follow-ups
- **Severity:** minor. The unreachable-ore loop itself is fixed (`harvester-recovery-design.md`).
- Open: a field that stays walled is re-tried every 15 s (`HARV_BLACKLIST_TTL`, no backoff); two
  harvesters can pick the same patch (no claiming); ore beyond `TiberiumLongScan` is never found.

---

## Found in code review, not seen in play

Suspected from reading the code during the code tidy (`code-tidy.md`). Confirm in play, then promote
to a full entry above or delete. One line each: where, what, severity.

- **Ferry (minor):** `TFF_SAIL` treats a transport idling offshore as arrived and unloads onto water,
  then waits out `TF_FERRY_TIMEOUT`.
- **Carryall (minor):** `TFCarryPickup` outlives a changed order, so a later landing can skip its LZ check
  or lift that vehicle unasked.
- **Give-way (minor):** `HOLD_TIMEOUT` (60) expires claim waits early against a 75-frame claim, and the
  patient queue drops claims at 40 frames; `Find_Give_Way_Cell` checks only each ray's end cell.
- **Sidebar (cosmetic):** a dropship cameo is never evicted while any bay stands
  (sidebarglyphx.cpp ~546); the Mech Division isn't marked busy through the bay cooldown.
- **Small ones (cosmetic or latent):** MinelayerFindSpot's `>` should be `>=`; Mission_Repair looks only
  for a harvester's own refinery type; `Find_Passable_Position_Near` transposes x and y (from CFE); the
  [TFTDTiles] reader is unchecked; the dormant TDLST indexes 16 facings on 4 frames; EA's own
  `Make_Enemy` uses `!` for `~` and CNC_Read_INI's `memset` has its arguments swapped (both also
  upstream); `[TSPLUG]` lacks the Capturable/Crewed/Repairable/Bib keys its TS original has.

## Limitations (cannot be fixed from a mod; do not re-investigate)

### Speech the DLL sends in the game-over window is dropped
- The launcher discards speech dispatched during or after `On_Multiplayer_Game_Over`
  (`TDACCOM1`, `TDFAIL1` and `RAOLOST1` all went out through valid chains and stayed silent),
  so the endgame lines ride the EVA mailbox. Mid-game stub-and-refire is unaffected.

### The Dropship Bay's countdown cameo tooltip flickers once a second
- The 5:00 to 0:01 cooldown is a per-second AssetName swap (`%s_CD%03d`), and each swap rebuilds the launcher's sidebar
  button, closing an open tooltip. Tooltip and icon are one launcher widget. Per-second precision
  was chosen over coarser, flicker-free steps.

### Classic graphics mode is unsupported
- The mod's terrain and units have no classic art, so the mod is HD-only.
  `CNCDisableLegacyGraphicsOption` in `Data/XML/GameConstants_Mod.xml` removes the option and the
  spacebar toggle.
