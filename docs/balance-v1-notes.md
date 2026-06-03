# Balance feedback log — deferred to v1.0

Per the standing rule (pre-v1 stays TD-source-authentic; "feels too strong/weak/fast"
playtest reports get **logged here** and batched for the v1.0 balance pass, NOT patched
piecemeal in rules.ini). Fidelity bugs (wrong stat vs TD source) are fixed immediately and
do **not** belong here — only deliberate balance deviations from TD-authentic do.

> **See also `balance-deep-dive.md`** — the analytical cross-faction stat audit
> (verified v1.0 numbers, matchup tables, ranked findings F1–F6, and the phased
> v1.x balance plan). This file is the running *playtest-report log*; the
> deep-dive is the *analysis + plan*. New reports land here; tuning decisions
> trace back to the deep-dive.

---

## Tank movement pace feels too fast (2026-05-31)

**Report:** Playtest race of Nod Light Tank vs Flame Tank — the tracked speed felt "waaay
too fast"; the (buggy) wheeled pace felt better.

**TD-authentic reality (kept):** all four TD tanks — Light (LTNK), Medium (MTNK), Mammoth
(HTNK), Flame (FTNK) — are `MPH_MEDIUM` **and** `SPEED_TRACK` in TD, i.e. identical speed at
the tracked terrain rate (Clear 80% / Rough 70%). So they're *meant* to be equal and at the
faster pace. The slow feel came from a **fidelity bug** (LTNK/MTNK/HTNK were missing
`Tracked=yes` → wheeled 60%/40%), now fixed — that fix is correct and stays.

**Deferred balance question for v1.0:** does the whole TD-tank line move too fast for this
mod's feel? Since they're TD-equal, this is a *line-wide pace* call, not per-unit. Options to
weigh at v1.0:
- Lower `Speed=` across the TD tank line (e.g. 9 → 7), keeping them equal to each other.
- Or accept TD-authentic pace and leave as-is.
- (Rejected for now: making Flame slower than Light — a deliberate non-TD differentiation.)

Decision: **keep TD-authentic for pre-v1**; revisit pace in the v1.0 balance pass.
