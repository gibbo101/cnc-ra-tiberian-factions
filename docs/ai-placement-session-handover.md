# AI session handover — W4 cadence SHIPPED, base placement is the next bug (2026-07-23)

> **2026-07-31 UPDATE — ROOT CAUSE FOUND AND FIXED, verification pending.** The reject counters
> ran live and named the culprit: **`Recalc_Center` divides the unweighted distance sum by the
> cost-weighted count** (EA-original, 1995), so an expensive base computes a Radius 2-3x too
> small; `Which_Zone` rejects past `Radius*4`, collapsing the whole build-site search to a disc
> the base itself fills. Live proof: Nod at 7 buildings had `radius=518` (the 512-lepton floor)
> and its TDAFLD scan rejected all 16,384 cells (`zone=7888`, the 176 in-zone all
> footprint-blocked, `prox=0 ok=0`). Fixed in `6604354` (divide by building quantity); the
> `Cell_Coord` fallback bug below fixed in `eb5d6d8`. In the one pre-fix observation run with
> `eb5d6d8` only, GDI logged ZERO place-fails to F4600 (vs 12 in the baseline) — suggestive but
> not conclusive (different map, GDI got rushed). **Next: a full skirmish on the `6604354` build,
> confirm radius values look sane and `PLACE-FAIL` stays at zero for a growing base.**

---

## 1. RESUME POINT — why can't GDI place buildings?

**The question:** GDI repeatedly fails to place `TDPROC` / `TDWEAP` / `TDFIX` while holding
thousands of credits. Last run: **12 `PLACE-FAIL` lines, every one of them GDI**, versus zero for
Nod. In the run before it, GDI started `TDFIX` **16 times and completed it zero times**. Its base
stalls around `CurB=10` while the other house grows past 20. This is the bulk of the "GDI feels
sluggish" complaint: the faction cannot grow its base, so vehicle production, tech and army
composition are all starved downstream.

**What is already deployed and waiting:** the `PLACE-FAIL` line now carries per-predicate reject
counts from the `Find_Cell_In_Zone` sweep:

```
PLACE-FAIL TDFIX reason=no-location cell=-1 | rejects radar=N zone=N legal=N prox=N ok=N | center=N radius=N
```

**Read it like this:**

| Dominant reject | Meaning | Then do |
|---|---|---|
| `legal=` huge, `prox=` ~0 | Terrain/footprint. GDI's base area genuinely has no room for a 3x3+bib. | Compare `radius` against Nod's. Try a different map to confirm it is positional. |
| `prox=` huge | Cells are legal but nothing counts as an adjacent friendly building. | Suspect the `IsBase` / owner test in `Passes_Proximity_Check` (`display.cpp:753`) against TD-separated types. |
| `zone=` huge | The base zones exclude nearly everything. | `Which_Zone` admits out to `4 * Radius` (`house.cpp:8779`) — check whether `Radius` is collapsing. |
| `ok=` non-zero but still failing | A cell WAS found — the failure is downstream. | Look at `Unlimbo` / `Flush_For_Placement`, and expect `reason=unlimbo-refused`. |

**Run to get it:** launch a skirmish (Unholy Alliance, 1 GDI + 1 Nod) and watch
`MOD_DEBUG_AI.txt` for `PLACE-FAIL`. First one lands around F700.

### Two engine defects found on the way — both real, neither fixed, both need a decision

1. **EA's `Cell_Coord` bug — one word, all four factions, upstream-able.**
   `Find_Build_Location` (`house.cpp`) fallback loop does `return (zcell)` — a raw `CELL` where the
   caller expects a `COORDINATE`. The preferred-zone path above it correctly wraps in
   `Cell_Coord()`. Verbatim in EA's source at
   `CnC_Remastered_Collection/REDALERT/HOUSE.CPP:4669`, never touched by us, **broken since 1996**.
   So whenever the preferred zone is full, the AI gets a malformed coordinate and discards the
   building instead of placing it elsewhere. Worth contributing back to Vanilla Conquer.
   **FIXED in `eb5d6d8` (2026-07-31, Luke's call)** — not yet deployed or observed in-game;
   re-run the reject-counter diagnosis on a build that includes it, since it may change the
   placement picture on its own.

2. **The 5-zone fallback is a no-op.** `Find_Cell_In_Zone` (`house.cpp:9783`) takes a `zone`
   argument but **never filters by it** — it scans all `MAP_CELL_TOTAL` cells and uses the zone
   only to pick a distance reference for "nearest". So the "try anywhere" loop re-scans an
   identical candidate set five more times and can only fail identically. Six full map scans per
   failed attempt, guaranteed to agree. Fixing this is the *real* cure for a hemmed-in base, and
   also the riskiest change — do it after the counters say what is actually being rejected.

3. **A stalled factory is scrapped, not paused** (`building.cpp:7795`). Confirmed live:
   `PROD abandon TDPROC pct=0 cash=24` — Nod spent down to $24, the order could not start, and it
   was thrown away rather than held. Minor next to the placement bug but the same design flaw.

### FALSIFIED this session — do not re-chase

- *"TD buildings aren't valid proximity anchors."* No. The test needs `base->Class->IsBase`,
  `IsBase` defaults true, and `TDPROC`/`TDWEAP`/`TDFIX` all set `BaseNormal=yes` explicitly.
- *"Infantry spam starves the expensive builds of funds."* No. GDI's failures are all placement,
  with healthy cash; `PROD abandon` never fired for GDI at all.
- *"The search area is too small."* No. `Which_Zone` admits candidates out to 4x the base radius.
- *"The in-limbo `BQuantity` count is the primary cause."* No — it is real (see
  `known-issues.md`) but it only decides *which* building gets thrashed, not that one does.

### ⚠️ The reading error that caused three wrong conclusions

**`PROD start` proves only that an order BEGAN, not that anything was built.** Three claims were
made and retracted this session off the back of reading it as completion ("GDI has no war
factory", "GDI fields infantry-only armies", "the war factory completed at F10,000"). Always
confirm against `CurB`, the `ROLE` counts, or the player's eyes.

Related: **`TDMTNK` is the GDI *Medium* Tank, not the Mammoth** — the Mammoth is `TDHTNK`, and it
had zero production starts all match. Mislabelling it sent Luke checking for the wrong unit.

---

## 2. SHIPPED AND VERIFIED — W4 attack cadence (`0b168df`)

The AI sat on a 73-unit army for half an hour because the attack decision was a flat 33% roll
that, win or lose, then slept for the full attack interval. All of that arithmetic was EA's
original (`REDALERT/HOUSE.CPP:5295` and `:5343`); vanilla masks it with campaign TeamTypes that
skirmish never gets. Full design in `ai-upgrade-plan.md` W4.1.

**Verified live, first run:**

| | measured |
|---|---|
| First wave | **F3640**, against a **F27,502** baseline — 7.6x earlier |
| Recheck-on-decline | **943 / 946 frames** against **900** designed (the ~45 overshoot is `Expert_AI`'s 5 s poll granularity) |
| Branches exercised | `roll`, `roll-declined`, `ceiling` (twice), floor decay 10 -> 7 -> 5 -> 4 on schedule |
| Difficulty separation | confirmed across tiers — `iq=4 ceiling=30` and `iq=5 ceiling=26` in one match |

`why=massing` (the floor hold) is the one branch never seen, because both houses were already
past the floor of 10 at their first opportunity. Not a concern — it is the simplest branch — but
it remains formally unexercised.

## 3. VERIFIED — frame-based starvation ageing (`feab517`)

Was carried unverified into this session. Now confirmed: starved candidates aged in at
**8,087–9,402 frames** (`STARVE_FRAMES=7500`) and won **late** (F9.6k–F15k) rather than as an
early bloc. That is exactly what the retune was for — the decision-count version let 8 of 62
decisions jump the queue together and bought defences instead of a war factory.

---

## State of the tree

- `main` is **9 commits ahead of origin, deliberately unpushed** (Luke's standing instruction).
- Desktop Proton prefix carries the current build **including the reject counters**.
- Previous run logs preserved next to `MOD_DEBUG_AI.txt`:
  `MOD_DEBUG_AI.w4-cadence-run.txt` (cadence proof) and `MOD_DEBUG_AI.placement-run.txt`
  (12 GDI placement failures).
- AI diagnostics write to **`MOD_DEBUG_AI.txt` in USERPROFILE**, *not* `tf_astar.log` — that
  mistake cost time this session.
