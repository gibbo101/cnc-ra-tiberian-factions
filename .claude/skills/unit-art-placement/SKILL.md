---
name: unit-art-placement
description: Use when adding, re-packing or auditing a unit's HD art in Tiberian Factions (TS, RA2, C&C3 or any new voxel unit), or when a unit's selection box, health bar or shots look out of place, or when units don't line up with EA's in the same cell row. Measures the art against EA's own units, centres vehicle hulls, and keeps the fire points and selection boxes in step with the art.
---

# Unit art placement

The launcher draws a unit frame with its canvas centre on the unit and centres the selection box
on the unit too. So where the art sits on its canvas decides whether the unit lines up with its
neighbours, whether the box fits it, and where its shots appear to leave from.

## The rules, measured off EA's own art

- **Vehicles: the hull is centred on the unit.** Across 21 EA vehicles (RA and TD tanks, APCs,
  jeeps, harvesters, MCVs, artillery) the hull's opaque pixels are centred to within 1.5 classic px
  (the Mammoths sit 2.6 high). Turrets and barrels stick up past it. Art bottoms then vary with
  size, from +6 to +14 classic px, so there is no shared ground line to match.
- **Infantry stand on EA's feet line**, about +1.3 classic px. They ship at EA's density
  (208 canvas), and ours already match.
- **Walkers and aircraft** follow their own rules (`docs/launcher-render-contracts.md` 14).
  Neither has been audited against EA. Don't run the hull rule on them.
- **Buildings** are seated on their plot (contract 7). A unit and the building it deploys into
  share a ground line (contract 14), so a building that takes its anchor from its vehicle moves
  with it.

Our voxel packers put the model's ground point at the canvas centre, which draws the hull 3 to 7
classic px high. `scripts/unit_centring.py` fixes that after packing.

## A new or re-packed vehicle

1. **Measure.** `scripts/unit_centring.py --audit` lists every packed TS, RA2 and C&C3 unit and
   flags any vehicle hull off centre.
2. **List it.** Add the unit to `UNITS` in `scripts/unit_centring.py`: its hull frame count,
   hull frames per facing (3 for the C&C3 tread steps), first turret frame, turret seat (any
   per-facing draw seat the DLL applies), and any building that takes its anchor from it.
3. **Centre it.** `scripts/unit_centring.py` moves every frame of its ZIP down by the hull's
   offset (crop offsets only, pixels untouched). It records the drop in
   `scripts/unit_art_drop.json` and `redalert/unit_art_drop.h`, and prints the unit's selection
   box.
4. **Box.** Put the printed width and height in `_art_boxes` (`UnitTypeClass::Dimensions`,
   `redalert/udata.cpp`).
5. **Shots.** `TechnoClass::Fire_Coord` adds the drop for every unit, so fire points generated
   by a packer (measured on the art before the move) stay on the barrels. A new per-unit
   `Fire_Coord` branch must start from `centre_art`, not `Center_Coord()`.
6. **Sign-off stills before any deploy.**
   `scripts/unit_placement_sheet.py OUT.png --facing N` draws the units beside EA's Medium Tank,
   Mammoth, APC and MCV, with boxes and centre marks, before (main) and after (working tree).
   Put it in `~/Desktop/Tiberian Factions/<topic>/` and show Luke.
7. **In game:** the unit lines up with EA's in a cell row, the box hugs it, the health bar
   clears it, shots leave the barrels, and any deploy doesn't hop.

`package-for-workshop.sh` runs `unit_centring.py --check` and refuses to package if a listed
unit is off centre, so a re-pack that skipped step 3 can't ship.

## Traps

- **Re-running the packer resets the art.** The packer writes the hull high again. Run
  `unit_centring.py` after it; it measures again and records the same drop.
- **Frames padded to the canvas edge.** Some packers pad crops symmetrically out to the canvas.
  The tool trims fully transparent rows to make room, and stops if real pixels would be lost.
  Grow the canvas then.
- **Density.** Packed units are 8 canvas px per classic px (canvas = ShapeSize x 8). EA's art and
  the TD units are 128/24. Measuring at the wrong density gives false offsets.
