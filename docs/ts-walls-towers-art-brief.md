# TS wall + component tower: art brief

Brief for whoever models the Tiberian Sun GDI concrete wall, component tower and its
three weapon plugs for the mod. The engine side is complete and shipping placeholder
meshes (2026-09-04, branch `ts-walls-towers`); this document is what an artist needs to
replace them. Everything below is fixed by the game, not by taste, unless marked.

## The ask: about seven meshes

Nothing here is drawn frame by frame. The pipeline places, rotates and renders these
pieces into every frame the game needs, so what is actually wanted is:

| Mesh | Notes |
|---|---|
| Wall segment | One straight run piece. North-south is this same mesh rotated 90 degrees, so it is modelled once. |
| Pier | The block that straddles a joined cell edge; the two neighbours each draw half of it. |
| End cap | Closes a run that has no neighbour on that side. |
| Lone piece | A wall segment with no neighbours at all. |
| Component tower | One mesh, one orientation, never rotates. Four feet on north/east/south/west so wall runs meet them flush. |
| Vulcan turret | One mesh. The renderer spins it through its facings. |
| RPG turret | One mesh. |
| SAM turret | One mesh. |

Optional extras, all currently generated and none of them blocking: damaged variants of
the wall and tower (damage is otherwise cut procedurally out of the healthy mesh), and a
hand-shaped construction sequence for the tower (otherwise it rises by scaling).

## Why not the TS sprites

TS drew its buildings for an isometric grid: wall segments run along the screen
diagonals and the tower's feet sit at the cell corners. This mod runs on Red Alert's
square grid, where walls run straight up/down and left/right on screen, and re-projecting
the iso sprites was tried and rejected. The wall and tower are therefore new 3D models,
rendered to sprites at the mod's camera. The plug turrets are round, so they could in
principle stay TS sprites, but matching models look better on a modelled tower.

## Reference

- TS sprites, decoded from `TIBSUN.MIX` (TEMPERAT.MIX / ISOTEMP.MIX) with **UNITTEM.PAL**:
  `GTWALL.SHP` (wall, 16 join states x 3 damage stages + shadows), `GTCTWR.SHP` (tower body:
  frame 0 healthy, 1 damaged, 2 wrecked), `GTCTWRMK.SHP` (buildup), `GTCTWR_B/_C/_D.SHP`
  (Vulcan / RPG / SAM turrets, 32 rotation frames each), `GTGATE_A/B.SHP` (gates).
  Extraction: `tools/ts_extract.py "<TIBSUN.MIX>" TEMPERAT.MIX extract <dir> GTWALL.SHP ...`,
  decode with `scripts/ts_shp.py <shp> UNITTEM.PAL <outdir>`.
- The look to match, sampled from those sprites: wall = light grey concrete slab with a
  rounded crest, one dark seam per segment, tan piers (105,97,68) at the joins, sloped end
  caps, no team colour. Tower = tan drum (157,141,89), grey feet, dark front ladder recess,
  platform on top; only the platform ring takes the team colour. Concrete grey ~ (129,129,129)
  faces / (161,161,161) crest.
- In-game TS screenshot for proportion: per 128 px cell the wall is about 53 px tall and 32 px
  thick on screen; the tower body about 90 px wide and 67 px tall.

## World and camera (fixed)

- 1 cell = 1 world unit = 128 HD pixels. The cell centre is the origin, ground is z = 0.
- Orthographic camera from the south, 32 degrees above the ground (the mod's TS vehicles
  use the same), +Y = north = screen up, +X = east = screen right.
- Light: sun from direction (-0.5, 0.6, 0.75) (west-north-up), with roughly 40% ambient. Only
  tops and south-facing surfaces are visible; north faces never are.
- The ground plane is drawn 1:1 in the game (the base game's own HD wall art cheats the same
  way), so renders are stretched vertically by 1/sin(32) ~ 1.89 after rendering. Model true
  heights; the pipeline handles the stretch. A unit of height ends up ~205 px tall on screen.
- Canvas per frame: 176 x 320 px, cell centre at the canvas centre. Joined wall arms run 1/6
  of a cell past the cell edge (into the neighbour) so runs never gap; that's why the canvas
  is wider than a cell.
- Team colour: paint the remap parts (the tower's platform ring) pure green (0,200,0) shades.
  The game recolours that hue per house.

## What to hand back

A Blender file, or OBJ/FBX/glTF, with those meshes as separate named objects in the world
units above. `scripts/ts_blender_walls.py` already holds the camera, light, assembly rules
and frame loop; pointing it at imported meshes instead of its procedural ones is a small
edit, and `scripts/ts_pack_blender.py` turns the renders into the game's files in about two
minutes.

Finished PNG frames are also accepted if someone would rather render themselves: square
pixels, transparent background, cell centre at image centre, 2x scale, named
`wall_j{joins:02d}_d{stage}`, `tower_d{0,1}`, `tower_make_{00..16}`,
`{vulc|rpg|sam}_f{facing:02d}_s{state}`.

## What the pipeline generates from them

For reference only, so the frame counts don't alarm anyone: 48 wall frames (16 join
combinations by 3 damage stages), 2 tower frames plus a 17 frame buildup, and 128 frames per
turret (32 facings by idle / recoil / damaged / damaged recoil) plus its buildup. All of it
comes from the meshes above.

## Where to find people

Project Perfect Mod forums (ppmforums.com, TS/RA2 voxel and SHP artists), the C&C Mod Haven
Discord art channels, and the Twisted Insurrection / Tiberian Sun Rising teams, who have
remade TS buildings at high resolution before. W3D Hub's Tiberian Sun Reborn is the closest
existing work: TS buildings already rebuilt as 3D meshes, so that is a permission
conversation rather than a modelling job.
