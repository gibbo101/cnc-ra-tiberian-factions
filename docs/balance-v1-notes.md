# Balance feedback log

> **STATUS (2026-06-16):** v1.0 shipped long ago (now at v2.x). The "defer to v1.0" framing
> below is historical wording — the standing rule still holds (log playtest *balance* reports
> here, fix *fidelity* bugs immediately), but the analytical home for the balance pass is now
> **`balance-deep-dive.md`**. This file remains the raw running playtest-report log that feeds it.

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

## Nod SAM sites weak vs RA jets (2026-08-01)

**Report:** Docklands skirmish (Luke as Nod-era player vs 4 AIs): four SAM sites let an
attacking MIG complete **three attack runs** before finally dying. "Nod sams still pretty
bad."

**Context to check before tuning:** TDSAM was ported TD-authentic (`td-sam-deep-dive.md`),
where it was tuned against TD's slow helicopters (Orca/Apache); RA's MIG/YAK are much faster
targets with standoff missile release, so an authentic TDSAM may be structurally under-tuned
against RA-era air. Compare projectile speed / ROF / range vs RA's own SAM and AA gun, and
whether the open-close animation (firing window) is eating engagement time. Related ranked
finding: F6 "fragile TD air" in `balance-deep-dive.md` — this is the mirror case (TD ground AA
vs RA air).

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
