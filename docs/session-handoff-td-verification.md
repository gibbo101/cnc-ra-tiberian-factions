# Session handoff — TD-source verification pass (2026-05-22)

**Status as of 2026-05-23:** Cargo 1-7 shipped (commits `593a975`, `381045b`, v0.4.2 cut at `1c229a2`, plus M2 Tier 1 stat/dispatch work). Only TDSAM remains.

---

## What this session produced

| Doc | Buildings | Type |
|---|---|---|
| `docs/td-tier1-verification.md` | TDNUKE, TDNUK2, TDPYLE, TDSILO | Verification ✅ shipped |
| `docs/td-obli-verification.md` | TDOBLI | Verification ✅ shipped |
| `docs/td-gtwr-gun-verification.md` | TDGTWR, TDGUN | Verification ✅ shipped |
| `docs/td-atwr-deep-dive.md` | TDATWR | Deep dive ✅ shipped |
| `docs/td-sam-deep-dive.md` | TDSAM | Deep dive — **pending** |

---

## Remaining cargo

**TDSAM full port** (`td-sam-deep-dive.md` M1-M8). Biggest scope: dedicated `TdSamState` enum, port TD's 8-state Mission_Attack verbatim, Status-aware Shape_Number, `[TDNike]` + `[TDPatriot]` weapon/projectile, de-aliasing pass. **3-6 hours** + MP smoke (needs 2-Deck Tailscale setup).

---

## Open verifications during implementation (TDSAM only)

- **TDSAM `[TDPatriot]` `Speed=`** — what RA integer corresponds to TD's `MPH_VERY_FAST` for BULLET_SAM.
- **TDSAM `[TDPatriot]` `Homing=yes`** — confirm that's RA's rules.ini field name for `BulletTypeClass::IsHoming`.

---

## What's deferred (not part of this pass)

The 7 still-Logic=-aliased entries are known not separated:

```
TDHQ    (Logic=DOME)
TDPROC  (Logic=PROC)
TDFIX   (Logic=FIX)
TDWEAP  (Logic=WEAP)
TDHPAD  (Logic=HPAD)
TDEYE   (Logic=MSLO)
TDFACT  (Logic=FACT)
```

These get verified during their *individual separation* passes, not as part of this verification pass. Following the same M3-M5 plan in `docs/building-separation-plan.md`.

---

## Continuation guidance

**Start a new session** when back. The plan docs are self-contained with line numbers, exact constructor-arg values, rules.ini snippets, and TD-source citations. Future-Luke + memory entries will pick up cleanly. This conversation's research context isn't needed for implementation work.

If a future session needs to *revise* a plan (e.g. playtest reveals an unforeseen issue with a TD-authentic value), edit the relevant doc — they're living documents.
