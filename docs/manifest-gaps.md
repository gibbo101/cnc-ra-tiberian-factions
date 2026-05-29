# Manifest field gaps — catalogue readiness

> **SUPERSEDED — all listed fields shipped + in use as of v0.50.** The four gap
> fields tracked below (`Sensors=`, `Storage=`, `GuardRange=`, `Explodes=`) are
> all present and in active use in `resources/remaster_mods/Vanilla_RA/CCDATA/rules.ini`,
> and every catalogue entry this doc gated on (TDHQ/TDEYE/TDPROC/TDSILO/TDGTWR/
> TDATWR/TDGUN/TDSAM/TDOBLI/TDTMPL) has shipped as a fully-separated `STRUCT_TD*`
> engine type. Retained for history.

Audit done 2026-05-19 of `buildings_manifest.py` / `add_building.py` FIELD_SPEC vs
the rules.ini keys the engine actually reads (`TechnoTypeClass::Read_INI`
techno.cpp:7016+; `BuildingTypeClass::Read_INI` bdata.cpp:3797+).

Currently the manifest emits 22 fields + `idle_anim` triplet. That's enough
for the remaining GDI production chain (TDPYLE, TDWEAP, TDFIX, TDHPAD,
plus the simple defenses TDGTWR/TDATWR). Gaps below land before the rest.

## Priority 2 — needed before radar & resource buildings

| Field | Catalogue entries blocked | Notes |
|---|---|---|
| `sensors` (bool) | TDHQ (radar), TDEYE (superweapon-host) | Hardcoded `IsSensor=false` today; superweapon radar comes from the donor (DOME/MSLO). Adding lets us decouple. |
| `storage` (int) | TDPROC (refinery), TDSILO | Ore/credit capacity. Donor inherits but balance values may need TD-authentic overrides (PROC ≈ 2000, SILO ≈ 2500). |

Both are leaf fields — just append to FIELD_SPEC with the standard `_str`/`_true_false` formatters and emit on the entries that need them. Omit on entries that don't.

## Priority 3 — needed before Nod elite/defensive structures

| Field | Catalogue entries | Notes |
|---|---|---|
| `guard_range` (int) | TDGTWR, TDATWR, TDOBLI, TDGUN, TDSAM | Threat radius for AI targeting. Defaults to Sight if omitted; emit only when divergent. |
| `explodes` (bool) | TDTMPL, TDOBLI (likely), TDEYE (maybe) | Triggers explosion on destruction (chain damage + debris). Cosmetic but matches TD authenticity. |

## Priority 4 — defer unless need arises

| Field | Reason it's parked |
|---|---|
| `powered` | Redundant with signed `power` for TD production buildings. Engine default (`IsPowered=false`) matches all current entries. |
| `water_bound` | No amphibious buildings in v0.3. |
| `unsellable`, `invisible`, `self_healing`, `cloakable`, `crushable` | Niche; no v0.3 catalogue entry needs them. |
| `ammo`, `rot`, `passengers` | Vehicle/infantry-only fields — would never appear on a building entry. |

## TDPYLE-ready check

The next catalogue entry (TDPYLE = GDI Barracks) is fully supported by today's
FIELD_SPEC. Reference shape from `tiberiandawn/bdata.cpp`: `Logic=BARR`,
`Image=PYLE`, `Footprint=PYLE` (2×2), `Cost=300`, `Power=-20`, `Points=40`,
`Sight=3`, `Strength=400`, `Armor=wood`, `BaseNormal=yes`, `Bib=yes`,
`Capturable=true`, `Crewed=true`, `Repairable=yes`. ShapeSize per convention
`(48, 48)`.

No manifest changes needed before adding TDPYLE.

## Recommended sequence

1. **TDPYLE** — proceed now, exercises the manifest as-is on a new entry.
2. **Add `sensors` + `storage`** — small FIELD_SPEC additions. Unblocks TDHQ, TDEYE, TDPROC, TDSILO simultaneously.
3. **TDHQ / TDEYE / TDPROC / TDSILO** — next batch of catalogue entries.
4. **Add `guard_range` + `explodes`** — unblocks the defensive-structure batch.
5. **TDGTWR / TDATWR / TDGUN / TDSAM / TDOBLI / TDTMPL** — final Nod/defensive batch.

Each FIELD_SPEC add is bounded: a tuple in `add_building.py`, a doc line in the
manifest header, and a default decision. Safe to interleave with content work.
