# Known issues

**Status:** Tracker. Open bugs, and player-facing limitations a mod cannot fix.

The tracker for open bugs, and for player-facing limitations a mod cannot fix, so nobody
re-investigates them. Checked against main at the 5.0.0 release (2026-10-04).

Each entry gives a **severity** (blocker / major / minor / cosmetic) and where the detail lives.
When an issue is fixed, delete its entry: the commit message and `CHANGELOG.md` record the fix.
A dead end worth warning about stays as one line in the topic doc it belongs to.

---

## Units and buildings

### Infantry pushed aside in a narrow pass lose their orders (suspected)
- **Severity:** minor.
- When a vehicle drives through a one-cell pass, `DriveClass::Drain_Infantry_Along` (`drive.cpp`)
  gives each untethered friendly infantryman ahead a one-cell `MISSION_MOVE` out of the way, and
  nothing restores his order. A soldier walking through the pass, or an engineer on
  `MISSION_ENTER` heading to capture, would stop one cell aside and stay there. Not yet seen in play.
- Fix shape, once it is seen in play: re-issue the man's mission and destination once he has stepped
  aside. Pushing only men with no order brings back the head-on jam the shove exists to break.

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

### Localized SFX file overrides the German and French voice dubs
- **Severity:** minor (DE/FR players hear English voices).
- `Data/XML/AUDIO/SFXEVENTSLOCALIZED.XML` carries 985 events, every sample `_EN-US`, and replaces
  every player's localized voices. Fix: trim it to the events the mod changes. The EVA mailbox
  relies on the `RA*_SFX_EVA_*` names, so check those before cutting any RA event.

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

### First solo skirmish after a LAN session spawned the LAN lobby's AIs (seen once)
- **Severity:** minor, unreproduced.
- `CNC_Set_Multiplayer_Data` handed over the previous LAN lobby's roster (8 slots, 6 AIs against an
  actual 1 + 5) and six AI houses spawned. Re-test if it recurs.

---

## AI and pathfinding

### An AI ally's units clump at defeated bases (seen once)
- In a LAN game whose TS GDI and TD Nod enemies were wiped out, the human's AI ally (with GPS) kept
  sending units to the defeated bases and left them there instead of attacking the enemies still
  playing. Cause not found: the waves' objective and the blind-hunt probe (`TF_Scout_Destination`,
  which cycles every start position but the house's own) are the suspects.
- Next time: watch the host's `MOD_DEBUG_AI.txt` (WAVE and SCOUT lines) live from the first defeat.

### Sim froze once in a 4-Hard-AI Docklands match (2026-09-02)
- **Severity:** unknown, unreproduced.
- Every DLL log stopped inside frame 22357 (about 11 minutes); ClientG kept spinning at about 60%
  CPU; no minidump, no A* storm. A rerun of the same build and lobby ran to F45000 clean. Logs:
  `docs/ai-ab-2026-09-02/g4-docklands-4ai-hang-MOD_DEBUG_AI.txt`.
- Next time: poll the AI log size every 5 s and on a 20 s stall run
  `gdb -p <pid> -batch -ex 'thread apply all bt 30'` on the sim process (gdb attaches under Wine;
  breakpoints never fire).

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

- **Scan bits past 31 (minor):** `Tracking_Add`, `Recalc_Attributes` and each unlimbo shift `1L << type`
  for infantry and units past bit 31 (undefined; on x86 it wraps, so TSGHOST sets the TANYA bit). The
  wrap is load-bearing: the multiplayer defeat check, two `tevent.cpp` "any left" events, the AI's
  `AScan != 0` tests and `Suggested_New_Team`'s own shifts all read it. Change those first, then the shift.
- **Ferry (minor):** `TFF_SAIL` treats a transport idling offshore as arrived and unloads onto water,
  then waits out `TF_FERRY_TIMEOUT`.
- **Carryall (minor):** `TFCarryPickup` outlives a changed order, so a later landing can skip its LZ check
  or lift that vehicle unasked.
- **Give-way (minor):** `HOLD_TIMEOUT` (60) expires claim waits early against a 75-frame claim, and the
  patient queue drops claims at 40 frames; `Find_Give_Way_Cell` checks only each ray's end cell.
- **Sidebar (cosmetic):** the Mech Division isn't marked busy through the bay cooldown.
- **Small ones (cosmetic or latent):** the [TFTDTiles] reader is unchecked; the dormant TDLST indexes 16 facings on 4 frames; EA's own
  `Make_Enemy` uses `!` for `~` and CNC_Read_INI's `memset` has its arguments swapped (both also
  upstream).

## Limitations (cannot be fixed from a mod; do not re-investigate)

### Speech the DLL sends in the game-over window is dropped
- The launcher discards speech dispatched during or after `On_Multiplayer_Game_Over`
  (`TDACCOM1`, `TDFAIL1` and `RAOLOST1` all went out through valid chains and stayed silent),
  so the endgame lines ride the EVA mailbox. Mid-game stub-and-refire is unaffected.

### Classic graphics mode is unsupported
- The mod's terrain and units have no classic art, so the mod is HD-only.
  `CNCDisableLegacyGraphicsOption` in `Data/XML/GameConstants_Mod.xml` removes the option and the
  spacebar toggle.
