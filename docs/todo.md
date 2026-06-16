# TODO / backlog

Running list of things to do. Bugs/limitations live in `known-issues.md`; this is for chores,
maintenance, and queued tasks. Newest at top.

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
- **Recon Bike won't-turn-to-fire bug** — major combat bug, self-contained; next on the small-wins list. See `known-issues.md`.
- **Harvester logic workstream:** targeting / pathing / claiming / reachability / idle-stuck + the economy-equalise (tilted-bucket dwell) idea. See the checkpoint's spun-off section + `balance-deep-dive.md`.
