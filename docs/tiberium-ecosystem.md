# Tiberium ecosystem

**Status:** Reference; shipped in 2.0.0. Tiberium on RA maps: the overlay, blossom trees, the
damage it does to infantry, and Visceroids.

## The overlay

Tiberium is its own overlay, `OVERLAY_TIB01`, after the vanilla overlays and before the TS walls (`defines.h`, `odata.cpp`), and
every rule below keys on it. `Can_Tiberium_Grow` and `Can_Tiberium_Spread` (`cell.cpp`) list TIB01 beside
the ore, so it grows and spreads as ore does. Tiberium and Ore never convert each other where their fields meet
(`CellClass::Spread_Tiberium`); the official-map hybrids rely on that (`official-map-hybrids.md`).

TF exports TIB01 as `OVERLAY_GEMS3` with AssetName `TIB01`, and `Get_Map_Cell`'s `IsResource` names
TIB01. See the field manual's [The Tiberium ecosystem](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/tiberium-ecosystem.md#a-new-resource-is-its-own-overlay)
for why a new resource needs its own overlay, both launcher fixes, and how growth follows `GrowthRate` and the
lobby's Tiberium option.

## Blossom trees

A blossom tree is a building, `STRUCT_TDBLOSSOM`, owned by `HOUSE_NEUTRAL`, drawn with TD's SPLIT2
sprite (`build_tiberium_hd.py`). On each growth tick it
spreads a neighbouring Tiberium cell, or failing that seeds an empty one (`building.cpp`). An
ordinary tree with Tiberium in six or more of its eight neighbours turns into a blossom tree
(`terrain.cpp`). The blossom tree's frame comes from `Frame` plus an ID-based stagger, so it needs
no saved state and never conflicts with the building's static (rate-0) animation.

## Damage to infantry

Infantry standing in Tiberium take 2 damage (`WARHEAD_SA`) every 50 frames, so a minigunner
survives about 28 tiles, as in TD; a 16-frame cadence killed in about 9. Every infantry type is hurt,
with no chem-warrior exemption, and A* steers infantry around Tiberium (`cfe-port-plan.md`, item 7).
The Ghost Stalker is immune: it heals a point every 9 ticks in Tiberium below green health, snapping
to full past green, and spills Tiberium into its cell and the four beside it when it dies.

## Visceroids

About 1% of infantry killed by Tiberium become a Visceroid (`UNIT_TDVICE`). TF uses `HOUSE_JP`,
`Scan_Place_Object` and `MISSION_HUNT`; see the field manual's
[The Tiberium ecosystem](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/tiberium-ecosystem.md#visceroids) for why each is needed.
Visceroids are immune to the EMP.
