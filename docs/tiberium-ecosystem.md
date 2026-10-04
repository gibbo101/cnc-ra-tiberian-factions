# Tiberium ecosystem

**Status:** Reference; shipped in 2.0.0. Tiberium on RA maps: the overlay, blossom trees, the
damage it does to infantry, and Visceroids.

## The overlay

Tiberium is its own overlay, `OVERLAY_TIB01`, last in the overlay enum (`odata.cpp`). Every rule
below keys on that overlay, never on `Land_Type() == LAND_TIBERIUM`: RA's Ore and Gems share that
land type and are harmless. Spreading runs on `Rule.GrowthRate`, in multiplayer only when the
lobby's Tiberium option is on. Tiberium and Ore never convert each other where their fields meet
(`CellClass::Spread_Tiberium`); the official-map hybrids rely on that (`official-map-hybrids.md`).

The launcher's minimap keys resource pips off the vanilla resource range, so TIB01 is exported as
`OVERLAY_GEMS3` for the overlay model and radar, with AssetName `TIB01` so the map still draws
Tiberium. `Get_Map_Cell`'s `IsResource` check names TIB01, so a new resource overlay has to be added
there too.

## Blossom trees

A blossom tree is a building, `STRUCT_TDBLOSSOM`, owned by `HOUSE_NEUTRAL`. On each growth tick it
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

About 1% of infantry killed by Tiberium become a Visceroid (`UNIT_TDVICE`), owned by `HOUSE_JP`.
RA skirmish creates only the playing houses, so `HOUSE_JP` is created on the first spawn, allied
with itself and made a mutual enemy of every house. `HOUSE_NEUTRAL` would not work: every house
allies it, so nothing would target the Visceroid. The dying soldier still occupies its cell, so the
Visceroid is placed with `Scan_Place_Object`, and it needs an explicit `MISSION_HUNT` or it idles.
Visceroids are immune to the EMP.
