# AI Phase 1 — session handover (2026-07-17/18)

**Status: code COMPLETE + pushed + desktop-deployed. NOT merged, NOT soaked, NOT verified
in-game.** Written while the parallel TS-spike session (hover MLRS) owned the desktop, so
no live testing happened this session.

## What exists where

| Thing | Where |
|---|---|
| Branch | `ai-phase1`, pushed to origin. 5 commits: `60fb0b3` W7, `5efca8c` W1.5, `8e25a32` W1.2, `6328960` W1.3, `c52fb51` docs. |
| Worktree | `.claude/worktrees/ai-phase1` (branch is pushed, so the worktree is disposable after merge: `git worktree remove .claude/worktrees/ai-phase1`) |
| Desktop deploy | Separate mod folder `Vanilla_RA_AI1` in the desktop Proton prefix, launcher name **"Tiberian Factions (AI Phase 1 test)"**. Deliberately did NOT touch `Vanilla_RA` (the TS session's live build; RA client was running). |
| Deck | NOT deployed. Both Decks were offline 2026-07-17 late evening. |
| Design/status | `ai-upgrade-plan.md` §6 Phase 1 STATUS block (same content as below, condensed). |

## What Phase 1 changed (one commit per workstream)

1. **W7 — difficulty → IQ plumbing.** `CNC_Set_Difficulty` was campaign-gated; the skirmish
   lobby value was silently dropped (ai-improvements.md Problem 10). Now: skirmish value →
   `Scen.CDifficulty` → `TF_AI_IQ_From_Difficulty` (house.cpp): Easy=3, Normal=4,
   Hard=`Rule.MaxIQ`. Retro-applies to live AI houses (client call-order unknown) and is
   TF_AI_DIAG-logged. **Fallback: until a lobby value is actually seen
   (`TFLobbyAIDifficultySet`), everything runs vanilla MaxIQ** — a silent client can't
   demote the AI. Stat handicaps stay 1.0× at every tier (dllinterface re-assigns
   DIFF_NORMAL after the house constructor; verified no bias leak). `IQProduction` 5→3 in
   engine default AND `rules.ini` (else Easy IQ3 would never base-build, house.cpp:1281).
   Existing IQ knobs already tier correctly: supers/aircraft/guard-area/content-scan gate
   at 4 (Easy loses them), economy behaviours ≤3 (all tiers keep them),
   `Computer_Paranoid` fires only at MaxIQ (now Hard-only).
2. **W1.5 — primary-factory.** `Factory_AI` (building.cpp): a computer house now runs at
   most ONE production order per factory category, like the human sidebar. The vanilla
   cheat was quadratic: every factory ran a parallel order AND `Time_To_Build` divides by
   `Factory_Count`, so 3 war factories = 3 tanks each at 3× speed. Also fixes the
   FactoryMax=20 heap exhaustion behind late-game "sidebar can't build". Money-suspended
   orders still hit the vanilla abandon path, so the category can't deadlock.
3. **W1.2 — fair-fog intel layer.** `TechnoClass::Revealed` now records discovery for
   computer houses in `IsDiscoveredByPlayerMask` (was human-only; all AIs shared one
   `IsDiscoveredByComputer` bit and the second AI house skipped recording entirely). The
   reveal plumbing (`Occupy_Down`, `Map_Cell`→`Revealed(house)`) already ran per session
   player including AIs — recording was the only gap. Gated on the mask:
   `Evaluate_Object` (aircraft exempt, mirroring the campaign gate) and
   `Special_Weapon_AI` — which covers ALL six supers (RA nuke, TD Ion, TD Nuke, spy,
   parabombs, para-infantry dispatch through it). `Take_Damage` reveals the attacker to
   the victim's house (fire out of fog = seen tracers), so retaliation can't deadlock.
   **Residuals (accepted v1, revisit with W3):** once-seen enemy UNITS stay evaluable
   while fogged (the mask is positionless — buildings are fully fair since their position
   never changes); build-choice reads of enemy quantities (e.g. `enemy->AScan` airstrip
   counting) are still fog-blind — W3 routes those.
4. **W1.3 — blind-hunt scouting.** With fair fog, a blind `Mission_Hunt` used to
   `Random_Animate` in place forever → AI would stall in base. Blind AI ground hunters now
   probe multiplayer start locations (`TF_Scout_Destination`: `Scen.Waypoint[0..25]`,
   skip within 12 cells of home `Center`, unmapped-by-this-house first, nearest first;
   all-mapped → re-probe nearest). Start points are public map knowledge = fair. IQ
   tiers: Easy probes only until `TF_Knows_Any_Enemy_Building()`, Medium/Hard whenever
   blind. Aircraft keep vanilla hunt (fog-exempt); naval blind-hunt deferred to W5.
   Deeper always-on map-warming ties into W3's stage-aware value model — not built.

## Pickup checklist (next session)

1. **Merge.** Precondition: TS-spike work committed (it was uncommitted on
   `house.cpp`/`techno.cpp`/`foot.cpp`/`defines.h` — shared files, disjoint regions; merge
   should be clean but eyeball those four). Then `git merge ai-phase1` on main, rebuild,
   redeploy to the normal `Vanilla_RA` target, delete the `Vanilla_RA_AI1` folder AND the
   worktree.
   *Testing before the merge is also fine* — the `Vanilla_RA_AI1` build is self-contained
   (includes all of Phase 0 + 1, lacks only the TS spike).
2. **One diagnostic session covers Phase 0 + Phase 1.** Setup per the Phase 0 recipe
   (cross-session memory: desktop-diagnostic-run-recipe): rotate `MOD_DEBUG_AI.txt`,
   **enable exactly ONE mod** — there are now TWO local TF mods in the launcher
   (`Vanilla_RA` + `Vanilla_RA_AI1`); the Phase 0 diagnostic was already burned once by
   the wrong-mod trap. Freshness check: dev DLL recreates `tf_astar.log` within seconds.
3. **What to look for, in priority order:**
   - `grep CNC_Set_Difficulty MOD_DEBUG_AI.txt` — **the single most important line.**
     Present = W7 live (note the value + whether it arrives before or after match start).
     Absent = the client never sends difficulty in skirmish → all tiers dormant
     (harmless: vanilla MaxIQ fallback) and W7 needs a different lever; investigate what
     the lobby's per-slot "MEDIUM" label actually transmits.
   - Phase 0 temple gate: `grep -E "TDTMPL|TDSTEAL|POOL|WIN" MOD_DEBUG_AI.txt` — the
     build-choice starvation hypothesis (todo.md Phase 0 block).
   - Fair fog + scouting sanity: AI units head for start locations early, AI attacks
     begin AFTER first contact, no standing-in-base stall, superweapons only hit
     discovered buildings.
   - Primary factory: AI with 2+ war factories produces one vehicle at a time (watch the
     build cadence / heap: late-game sidebar starvation should be gone).
   - Phase 0 soak items: AGT offline on low power, idle harvesters retreating to the
     refinery, wave launch scatter + home garrison.
4. **Difficulty spot-check (only if CNC_Set_Difficulty appears):** one Easy match — AI
   should never fire supers, never rebuild aircraft, units stay plain-guard, scouting
   stops after first contact; one Hard match — full behaviour set.

## Known caveats / accepted risks

- `TFLobbyAIDifficultySet` is never reset between matches: a stale `Scen.CDifficulty`
  carries into a later skirmish if the client only sends on change. Benign (it mirrors
  the persistent lobby setting) — revisit only if the log shows odd call patterns.
- Multi-human MP + AI determinism assumes all clients call `CNC_Set_Difficulty`
  identically (same assumption vanilla makes for `CNC_Config`). Solo skirmish: no risk.
- Blind hunter with the whole map mapped camps the nearest non-home start point
  (re-probe returns its own location). Mediocre, not pathological; W3/W4 supersede.
- `Hidden()` clears AI-owned objects' discovery bits when they re-shroud; self-heals on
  next reveal via `Occupy_Down`. Known flapping, no action needed.

## After that

Phase 2 (W2 faction separation + buildability — engineering survey already in plan §3 W2)
or W8 directional armour (independent, can land any time). Sequencing in plan §6.
