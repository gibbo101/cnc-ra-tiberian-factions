# Changelog

All notable changes to this mod will be documented here.

This project follows a `version_high.version_low.patch` scheme matching the `ccmod.json` fields.

## [Unreleased]

## [0.2.0-alpha] — 2026-05-16

### Engine

- Detached `HOUSE_GOOD` from `HOUSEF_ALLIES` and `HOUSE_BAD` from `HOUSEF_SOVIET` in `redalert/defines.h`. Vanilla RA bundled the TD houses into the RA side bitmasks, causing them to silently inherit the Allied / Soviet tech trees. With this change, the TD houses form their own (initially empty) factions.
- Added `HOUSEF_GDI` and `HOUSEF_NOD` aliases for clarity in subsequent commits.

### Status

- France country slot is hijacked into HOUSE_GOOD at the DLL boundary via [[spike branch reference]] (not yet wired into `main`). Result: France player will see a near-empty build menu — proof of detachment. Re-granting buildables comes in v0.2.x.
- Nod (HOUSE_BAD) detachment is symmetric but untested in this commit — only HOUSE_GOOD has a launcher route via the swap.

## [0.1.0] — Initial scaffolding (not separately tagged)

- Forked Vanilla Conquer as the DLL build base.
- Rebranded `ccmod.json` for "Tiberian Factions for Red Alert".
- Added `deploy.sh` for build + Steam Deck deploy over Tailscale.
