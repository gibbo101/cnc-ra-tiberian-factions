# TS factions in RA — feasibility (design-level, verified 2026-07-18)

**Status: FEASIBLE, design de-risked, NOT scheduled.** Luke's call: TS factions are
probably not for Tiberian Factions itself — they're the seed of a **future spin-off
mod: TD + RA + TS + RA2 factions in one mod** (see "The multi-era vision" below).
This doc records the verified mechanism so the design doesn't have to be re-derived.
Grew out of the TS asset-import spike (`ts-asset-import-spike.md`), which proved the
art pipeline end-to-end (voxel render, TS-SHP decode, hover locomotor, TSHVR +
TSPOWR signed off in-game).

## The mechanism: decouple country houses, don't mint new ones

Luke's insight, verified against the code: **no new `HousesType` values needed.**
Reuse existing country houses (e.g. Germany, France) and decouple them from the
Allied/Soviet side masks — the exact operation already performed once for
`HOUSE_GOOD`/`HOUSE_BAD` (see the comment at `defines.h:1196`: vanilla RA had GOOD
bundled into `HOUSEF_ALLIES`, BAD into `HOUSEF_SOVIET`; the mod pulled them out).
The masks are plain DLL-side macros (`defines.h:1198`):

```c
#define HOUSEF_ALLIES (HOUSEF_ENGLAND | HOUSEF_SPAIN | HOUSEF_GREECE | HOUSEF_GERMANY | HOUSEF_FRANCE | HOUSEF_TURKEY)
#define HOUSEF_SOVIET (HOUSEF_USSR | HOUSEF_UKRAINE)
#define HOUSEF_GDI    (HOUSEF_GOOD)
#define HOUSEF_NOD    (HOUSEF_BAD)
```

TS GDI = pull `HOUSEF_GERMANY` out of `HOUSEF_ALLIES`, add
`#define HOUSEF_TSGDI (HOUSEF_GERMANY)`, and give the house its own tech tree via
`Ownable=` masks in rules.ini. Same for TS Nod (France). Also touch: direct
`== HOUSE_GERMANY`-style comparisons (few), the audio accent branch
(`dllinterface.cpp:555` keys `.V*` vs `.R*` off `HOUSEF_ALLIES`), side-check
branches, and `hdata.cpp` personality entries (already exist for every country).

Why this beats new enum values: zero launcher exposure (launcher natively knows
Germany/France — colors, flags, position markers, loading screens), no
`[HOUSE_COUNT]` array audits, no remap needed at the DLL boundary, and the picker
slot you relabel IS the house you play.

(For the record: new enum values would ALSO work — bitfield has 20/32 slots used —
but is strictly more work for no gain.)

## The launcher boundary — no wall (traced 2026-07-18)

- **Inbound (lobby pick → DLL):** the launcher only ever sends country house
  values. The GDI/Nod remap happens DLL-side on receipt (`dllinterface.cpp:914`:
  Spain→GOOD, Turkey→BAD). With decoupled countries, no remap is needed at all.
- **Outbound (DLL → launcher):** house bytes sent back are owner houses — in
  skirmish/MP always `HOUSE_MULTI1–8` — or campaign-only paths (carryover list,
  `dllinterface.cpp:2187`). Skirmish ActLike never crosses the boundary.
- The `On_Sound_Effect` house param is consumed DLL-side (accent extension pick).

## The lobby picker — the only real ceiling (cosmetic)

Fixed 8-entry list; adding entries hard-crashes (`faction-select-identity.md`).
Currently 4 of 8 slots are meaningful (Spain→GDI, Turkey→Nod, rest are
Allies/Soviet dupes), so up to 4 more factions fit by relabeling dupes.

- **Names:** same-length in-place MASTERTEXT edits, pad with trailing spaces.
  "France" (6) → "TS Nod" is an exact fit; "Germany" (7) → "TS GDI ".
  Three strings per faction: `NAME_FACTION_NN` + `BONUS_<COUNTRY>` +
  `REDALERT_<COUNTRY>`.
- **Icons:** front-end-preloaded regions ONLY — GDI eagle (`_00`), Nod cobra
  (`_01`), 8 country flags (`_03`–`_10`). TS GDI wears the same eagle as TD GDI
  (or a flag). Bespoke front-end emblems are DEAD (`front-end-texture-meg-spike.md`).
  In-game sidebar crests + cameos are fully moddable as usual.

## Campaign exposure — accepted, with a cheap tiebreaker

Custom campaigns (the Inheritance War arc) override the Counterstrike/Aftermath
tabs, so those scenarios are moot. The main Allied/Soviet RA campaigns remain
playable: a mission scripting Germany/France as an active house would show
decoupled behavior there. Blast radius is small (pre-placed units ignore
`Ownable=`; only mid-mission AI production, accent, and side branches show).
**At implementation time: grep the extracted scenario INIs and take the two
least-used countries.** Not a design blocker.

## Content — the actual milestone (per-faction cost)

- **Solved by the spike:** voxel render at the mod camera, TS-SHP buildings +
  buildups, the TGA/meta crop contract, hover locomotion (`SPEED_HOVER` +
  `MZONE_HOVER`), team-color remap.
- **Straightforward:** most rosters — stat-and-art work on existing logic
  (Titan, Wolverine, tick tank, buggy, artillery, stealth tank, cyborgs,
  standard structures).
- **New mechanics, doable:** EMP, carryall lifts, drop pods, deployable units
  (RA has no non-MCV deploy).
- **Hard / defer from a first cut:** subterranean, jumpjet infantry, firestorm
  walls, veins/veinholes.

## The multi-era vision (the spin-off mod idea, 2026-07-18)

TD, RA, TS, and RA2 factions in one mod. Two facts make this uncannily viable:

1. **8 picker slots = 8 factions exactly.** TD GDI, TD Nod, RA Allies, RA Soviet,
   TS GDI, TS Nod, RA2 Allies, RA2 Soviet — zero dupes, every slot meaningful.
   Each faction takes one decoupled country house (8 country houses exist) with
   GOOD/BAD spare.
2. **RA2 uses the SAME asset formats as TS** (.vxl voxels + TS-format SHP), so the
   spike pipeline extends to RA2 extraction/render with modest work. RA2 was never
   open-sourced/GPL'd — its assets sit in the same tolerated category as the TS
   art (ship call is Luke's, per the spike's legal note).

RA2 mechanics tier like TS's: straightforward vehicles/structures first; prism
forwarding, mirage disguise, chrono/IFV logic are the hard tail. Tiberian
Factions itself is the base to fork from — it already carries the TD rosters,
the TS pipeline, and (post-AI-milestone) the faction-separated AI.

## ⭐ The cheap alternative: an ownership-gated TS tree (Luke, 2026-07-21)

**A TS tech tree does not have to be a faction.** Everything above solves "make TS GDI
selectable in the lobby" — country-house decoupling, picker ceilings, campaign exposure.
An easter-egg tree skips all of it: **the gate is owning the TS construction yard, not
being a TS player.** No new house, no `ActLike` value, no picker slot, no CONFIG.MEG
change. Pure DLL + rules.ini.

**The idea:** a rare crate drops a TS MCV. Deploy it and you get a TS construction yard,
and that yard unlocks the TS roster — for whoever found it, whatever side they are.

**Why it is close to free.** Every mechanism it needs already ships:

| Piece | Status |
|---|---|
| TS units on the crate table | **Live** — `cell.cpp` `CRATE_UNIT`, 1-in-8 rolls Hover MLRS / Titan / Mammoth Mk. II |
| Crates ignore faction | **Live** — crate spawns bypass `Owner=` and `Can_Build` entirely, so any side can already field a Mk. II |
| MCV type carries its own lineage | **Live** — W2 b3, four MCVs deploy four different yards and trees |
| Capture inherits the tree | **Live** — heritable lineage, no special case |
| TS art pipeline | **Proven** — voxel + TS-SHP, `ts-asset-import-spike.md` |
| Marquee units | **Ported** — Titan, Mammoth Mk. II, Hover MLRS, plus TSPOWR; all `TechLevel=-1` + `DevTechLevel=` |

**Implementation shape:** ship the TS types with a broad `Owner=` (all sides) and
`Prerequisite=TSFACT`, so the yard alone discriminates — the pattern finding 3 of
`ai-upgrade-plan.md` §W2 already calls the rule ("`Owner=` is not deleted, it's widened;
the faction-specific PREREQ building is the sole discriminator"). `Prerequisite` is an
array (`PREREQUISITE_MAX`), not the legacy 32-bit mask, so there is room. Every new
prereq token needs its `Can_Build` remap `continue` or the tree is silently unbuildable —
the known trap, same file.

**⚠️ The TS MCV must ride the RANDOM crate path only, never the comeback path.** The
`force_mcv` branch in `cell.cpp` deliberately hands a wiped player *their own* faction's
MCV, because at that moment an off-faction yard would be unrecoverable. A TS yard there
would be a punishment; as a lucky find it is a bonus.

**It needs the faction-agnostic AI to matter.** An AI that finds the crate today would
deploy the yard and then ignore the tree entirely — the same blindness it has to captured
factories. See `ai-upgrade-plan.md` §W2 "faction-agnostic base builder". Conversely TS is
the strongest argument for doing that work data-driven: it is the *fifth* lineage, and it
breaks any 4-way literal.

**Open decisions before building:**
- **Scope.** "TS GDI in its entirety" is a content project. Yard + power + refinery + war
  factory + four units is a genuine easter egg and is much nearer.
- **MP fairness.** A crate handing one player a whole *tree* compounds in a way a single
  Mk. II does not. Levers: rarity, crates-on only, Unholy Alliance only, or another
  hijacked lobby toggle (`SpawnVisceroids` is unclaimed).
- **Balanced or awesome?** TS units are a generation ahead by design. As a rare find,
  overpowered may be the point — but decide it rather than discover it.

## Sequencing

1. Finish the AI milestone — **design the faction-separation layer for N factions
   (6–8), not 4** (flagged in `ai-upgrade-plan.md` context; cheap now, expensive
   to retrofit).
2. **The ownership-gated TS tree above is the cheap first taste** — it needs no faction
   work at all, only the AI's role table to be lineage-agnostic.
3. TS factions (or the multi-era fork) as a later major, v5.0-scale, comparable
   to the original GDI/Nod arc.
