# TODO / backlog

Running list of things to do. Bugs/limitations live in `known-issues.md`; this is for chores,
maintenance, and queued tasks. Newest at top.

---

## Docs update / prune pass (queued 2026-06-16 — do NOT do mid-session, dedicated pass)

Goal: update stale docs, prune superseded ones. A partial staleness survey was run 2026-06-16
(2 of 4 doc groups assessed). Findings below; **the other 2 groups still need assessing** before
acting (TD deep-dives/verifications, and engine/reference/audio docs — listed at the bottom).

### PRUNE candidates (superseded / fully done — confirm content is captured, then delete or relabel "historical")
- `session-handoff-mcv-conyard.md` — self-marked COMPLETED; shipped; covered by `catalogue.md` + memory.
- `session-handoff-td-verification.md` — self-marked CLOSED; the per-building verification docs are the durable record.
- `session-handoff-weapons-port.md` — self-marked ARCHIVED; the M2–M5 arc shipped.
- `manifest-gaps.md` — self-marked SUPERSEDED; all gap fields shipped.
- `tiberium-overlay-port.md` — "no code yet" plan, but Tiberium ecosystem SHIPPED v2.0.0 → replace with a 2-line SHIPPED stub.
- `building-separation-plan.md` — M1–M6 milestone PLAN, fully DONE (all 17 buildings shipped); reusable content lives in `td-building-separation-recipe.md`. Relabel "COMPLETE — historical" or prune.

### UPDATE needed (keep, but add a status banner / trim stale body)
- `theatre-desert-feasibility.md` — still valid (campaign-gated, unstarted); add banner + point to `td-tile-hd-loose-art-investigation.md` as newer HD-terrain ground truth.
- `td-skirmish-map-import.md` — "no clean importer" framing is OBE (31-map pack shipped via transcoder); add SHIPPED banner, mark temperate/winter tiers DONE, keep only desert/interior-slot tier open.
- `faction-music-feasibility.md` — verdict is final/correct; tighten the "per-faction spike" prose that reads as still-open (it's resolved DEAD).
- `td-tile-hd-loose-art-investigation.md` — keep (HD-terrain ground truth) but trim the post-banner "uncommitted tree" body that's now shipped/misleading.
- `adding-td-buildings.md` — add banner: alias-model recipe superseded by `td-building-separation-recipe.md` for new buildings; retained for gotcha reference (esp. #16 ShapeSize, #5 Points=); note gotchas #11–15 are obsolete post-separation.
- `weapon-ports.md` — already self-warns "not the spec"; add "STATUS: all listed weapon ports SHIPPED (v1.0–2.0), historical mapping only."

### CURRENT (keep as-is — verified accurate)
td-port-playbook, td-building-separation-recipe, td-infantry-port-recipe, td-vehicle-port-recipe,
cargo-plane-port, front-end-texture-meg-spike, campaign-tabs-research, coop-missions-design,
gdi-nod-campaign-story.

### STILL TO ASSESS (survey not yet run on these)
- TD deep-dives + verifications: `td-atwr-deep-dive`, `td-gtwr-gun-verification`, `td-obli-verification`, `td-sam-deep-dive`, `td-tier1-verification`, `td-mlrs-deep-dive`, `td-attack-heli-deep-dive`, `catalogue`, `ai-targeting`.
- Engine/format/UI/audio/misc: `mix-file-format`, `launcher-vs-dll-ownership`, `config-meg-mod-delivery`, `ui-atlas-modding`, `classic-mode-palette-remap`, `faction-select-identity`, `building-sound-routing`, `td-audio-routing-recipe`, `workshop-publish-runbook`, `balance-v1-notes`.
- Also: add the new docs (`known-issues.md`, `todo.md`) to the documentation-map router in the workspace CLAUDE.md.

---

## Active work threads (tracked in detail elsewhere — index only)
- **Chokepoint pathfinding — next task:** the deadlock-breaker is in the wrong branch (no-path vs execution-blocked head-on). Fix plan + 2 test specimens in `chokepoint-reservation-design.md` CHECKPOINT 2026-06-16. Also revert the 2 dev test toggles before the next code commit.
- **Harvester logic workstream:** targeting / pathing / claiming / reachability / idle-stuck + the economy-equalise (tilted-bucket dwell) idea. See the checkpoint's spun-off section + `balance-deep-dive.md`.
- **Recon Bike won't-turn-to-fire bug** — see `known-issues.md`.
