# Launcher render contracts

**Status:** Reference. How the launcher draws unit, building, anim and beam art, and the house
rules for TS-sourced art. Check it before shipping any new unit art, anim or beam weapon.

Each contract cost a build-test cycle to find, most of them while porting the TS walkers.

## 1. Sprites anchor by the VIRTUAL CANVAS CENTER — place content accordingly

The launcher anchors the canvas centre, not the crop: see the field manual's
[How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#the-frame-and-its-meta),
the frame and its `.meta`. The Titan's feet at 174 of 192 drew it about 45 px below its cell. The crop-centre
theory fits that equally (for a tight crop, the crop centre is the content centre); the Hover MLRS rack is the
test that ruled it out.

**Rule:** compose every frame with its visual center (for voxel renders: the
render canvas = model origin) at the tileset canvas center. `write_zip` in
`scripts/ts_pack_walkers.py` additionally makes every crop center-symmetric,
which is kept as insurance — it makes both anchoring interpretations coincide.

## 2. Sub-object draws drop shape indexes ≥ 128

Turrets, radar dishes and harvester overlays are second draws, and draw nothing from shape 128 up: see the
field manual's [How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#rules),
rules. The Titan ships exactly 128 shapes for this (8 facings × 12 walk frames + 32 turret), and the Mk. II
body uses shapes up to 255.

## 3. The line renderer supports animation frames 0–4 only

TF ports TD's line path (`CC_Draw_Line`, `TechnoClass::LineFrame`), and its limits are in the field manual's
[How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#beams),
beams: frames 0 to 4, three lines an object. The railgun's beam drew giant squares (red when the beam was) until
its frame count dropped, so keep `LineMaxFrames <= 5` on the `Lines[]` path.

## 4. Custom anim types render; a stage without a tile draws the white box

A DLL-added `AnimType` with mod-shipped art and a tileset entry renders like any other: the Ion Cannon's
`TDIONSFX.ZIP`, the C&C3 railgun shot. The tile-per-stage, free-anim, `timedelay` and straight-alpha rules are in
the field manual's [How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#rules),
rules. Vanilla passes a `timedelay` only for a few fades and fires (`bullet.cpp`, `terrain.cpp`). Have the
generator patch the tile count into the XML, as `ts_gen_sonicwave.py` does.

## 5. Untracked hull-fixed direct-fire units need `IsLockTurret = true`

See the field manual's [Turrets](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/turrets.md#a-turretless-unit-that-fires-forward-may-need-islockturret),
a turretless unit that fires forward. Stock RA sets the flag on no unit; the Mk. II needs it.

## 6. Pillow `paste` with an RGBA mask corrupts at negative offsets

Pillow 10.2: pasting with a negative position and a mask produces
interleaved-strip garbage, not a clean clip — this silently shredded the
Titan's turret frames for several builds (only the thin antenna survived,
"cannon missing" #0). Use `safe_paste()` (pre-crops the source) everywhere in
the art pipeline.

## 7. Building selection boxes: the launcher owns POSITION, we own only SIZE

The launcher centres the box on the plot and takes only `DimensionX/Y`; no position field moves the box
(`PositionY` moves the sprite). See the field manual's [Building selection boxes](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/building-selection-boxes.md).
The TSFACT slab reseat is what moved its art off the box. TDFACT (correct box) and TSFACT (a tile high) are TF's
control pair for the unexplored stub and canvas lever. Open boxes: TSFACT (1 tile high), TSDROP
(1 tile low), TSPROC (wants 2 tiles more headroom than a plot-centred box
can give). Fix path: diff TDFACT's stub/canvas content geometry against
TSFACT's and transplant the relationship, art compensated to stay put.

## 8. The launcher draws every exported sprite unrotated

See the field manual's [How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#rules),
rules (the logged `Rotation` was 158). TF's railgun shot is built from dots along the line
(`cnc3-railgun-beam.md`).

## 9. Overlapping-sprite chains can never give a hard edge or keep a texture

See the field manual's [How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#worked-example-a-beam-the-launcher-cant-draw),
the worked example. Measured offline against the TS Disruptor footage: discs overlapping 6-7 deep ramp their alpha
over 35-75 px at the strip edge for every variant (chord coverage falls off toward the edge), and the best interior
mottle was std 7 against TS's 19.5.

## 10. The chronal vortex is a launcher-drawn screen warp the DLL can position — but nothing else

Proven 2026-08-27 (Disruptor ripple spike): `Get_Dynamic_Map_State` exports
`VortexActive/X/Y/Width/Height` every frame, and the launcher will render its vortex
distortion wherever the DLL points it — the ONLY true per-pixel warp the Remastered renderer
offers a mod. The catches, all observed in play: the launcher IGNORES the exported
Width/Height (our 64 px request drew a ~350 px whirlpool), anchors the effect at the
coordinate's top-left rather than its centre, always draws the full chrono whirlpool styling
(heavy swirl, not a subtle haze), and keeps churning for as long as the flag stays true.
Useless for a beam ripple; potentially useful for a deliberate large one-off screen warp.
The real `ChronalVortex` always owns the slot when active.

## 11. Voxel units are lit the way Tiberian Sun lights them, and a relight never re-places a sprite

**The shading model (`scripts/vxl_render.py`, default `--shade ts --normals vxl`):**
- Light: one fixed world vector at 45° elevation (OpenTS `_voxel.h Set_Voxel_Light_Angle`), length
  **1.5** (`voxlib.cpp Precalculate_Normal_Lookup`). Per voxel, `n·L` is truncated to a table index
  (`int(n·L × 16)`, negative → 0, so 16 = neutral, 24 = fully lit) into **VOXELS.VPL** (TIBSUN.MIX,
  `tools/ts_extract.py`). Each VPL table is a fixed brightness scale of the palette; the 32 measured
  luminance ratios are `TS_VPL_SCALE`: **0.62 (facing away) → 1.26 (neutral) → 1.70 (lit)**. The old
  ambient-plus-Lambert blend ran 0.35 → 1.0 — a 1.6–1.8× gap across the whole curve, which was every
  "too dark" report since the units wave. `--shade legacy --ambient N` reproduces old renders.
- Normals: **the VXL's own per-voxel normal index**, resolved through TS's tables
  (`scripts/ts_vxl_normals.py` = OpenTS `VoxelNormals1..4`, chosen by the section's normal mode byte).
  Geometry-derived normals (`--normals geo`) quantise to 26 directions; under TS's stepped table that
  reads as **blotches across flat decks**. Real normals light decks evenly and brighter.
- Team colour: the remap ramp keeps its **1.45× lift under either model** — the launcher's hue-remap
  preserves luminance, and remap-heavy hulls (APC, Disruptor, harvester) read dark without it.
- Shaded RGB is clipped at 255 before the uint8 cast, or bright channels wrap into green fringe pixels.

**The placement rule (the part that "butchered the turrets"):** the pack scripts **do not reproduce
where the shipped zips put things** — the Disruptor hull and the MLRS rack were moved at zip level in
later sessions, and a re-render's crop can grow (the rack's antenna pole no longer cut by the pack
canvas, a shadow one pass taller). The launcher anchors on the crop centre, so a grown crop or a
bbox-centred paste **moves the sprite** even when every body pixel is in the same place. So:
- **A relight goes through `scripts/ts_recrop_to_shipped.py <rev> NAME…`** after packing and
  reshadowing: it slides each new canvas onto the shipped frame's alpha mask (FFT cross-correlation)
  and cuts the shipped crop rect. Verify: overlap ≈ old pixel count, 0 residual shift.
- Turret blocks (TSHVR 32–63, TSSONIC 32–63) are relit the same way and placed by the alignment —
  verified 100% (Disruptor) / 94–99.7% (rack, the cut pole) mask overlap with the shipped frames.
- The APC water hull (32–63) is relit, then levelled to the land hull's mean luminance (`apcw.vxl`
  shades brighter on its own table), and **carries no shadow** (a hull in water keeps its shadow under
  the surface, as RA's ships do). **Never run `ts_reshadow.py` over the water
  frames.**
- Every TS unit and the RA2 tanks are HD rebuilds, rendered from 3D models with one light for every
  facing (`scripts/ts_pack_hd_buildings.py` UNITS; the models are in the TS-HD pack's `3d/`). The
  relight rules above don't apply to them.
- **Voxel-mesh upscale: tried and rejected (harvester A/B in game).** `scripts/vxl_mesh_render.py`
  (marching cubes + Taubin smoothing + denoised vertex colours, TS lighting) renders a smoother hull,
  but at game sprite scale the 1-voxel ribs and panel lines ARE the detail, and any smoothing that
  rounds the staircase rounds them away (the side panelling went). The voxel render with real normals stays. Script kept for reference only (needs a
  scikit-image venv). Don't re-chase unless units are drawn larger than the game does.

## 12. A new stub line does nothing until TFASSETS.MIX is rebuilt and committed

Adding a stub line to `scripts/build_tfassets.sh` does nothing until the script is run and
`CCDATA/TFASSETS.MIX` is committed. Until then a new HD bullet draws at its `bbdata.cpp` donor's size (see the
field manual's [HD tilesets and ZIPs](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/hd-tilesets-and-zips.md#size-comes-from-the-classic-shape),
size comes from the classic shape): the Disc Thrower's TSDISCUS flew at ~70x80 px on the Heat Seeker's
`ImageData`. The rebuilt archive lists new entries by CRC, not name, so check the
entry count against the committed copy (`mix_tools.py list`) rather than grepping for the name.

## 13. Art px to leptons is canvas px x 4/3

A packed unit ships at 8x-classic density (canvas = ShapeSize x 8), so one canvas pixel is 4/3 leptons (the
field manual's [HD tilesets and ZIPs](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/hd-tilesets-and-zips.md#size-comes-from-the-classic-shape)
has the conversion), and one TS SHP pixel at x6.4 is 8.53. Derive fire points and muzzle offsets in the packer and emit a table
(`tstitn_muzzle.h`, `ts4tnk_muzzle.h`, `tsjugg_muzzle.h`, and `tshmec_muzzle.h` from
`scripts/ts_hmec_muzzle.py`, read off the Mk. II's 3D model) so the art and the offset cannot
drift; a hand-dialled constant will read right beside the unit and miss by cells at range.

The Juggernaut's first fire point was a trig formula built on "1 TS px = 2 leptons", a quarter
of the real rate: its shells left from near the hull centre in every pose, which looks close
enough on screen at point-blank and is a cell and a half out at range 18.

## 14. A unit and the building it deploys into must share a ground line

The launcher centres a selection box on the object and draws its health bar above that box, and
a unit's art anchors on its canvas centre. So where the art's lowest pixels sit relative to that
centre is the unit's ground line, and it decides three things at once: whether the box brackets
the feet, whether the bar clears the hull, and whether the sprite appears to jump when the object
is replaced by another one on the same cell.

Two stances of one entity, or a deployable and the building it becomes, must therefore agree:

- The Juggernaut's walk frames sat 10 classic px north of its deployed frames, which read as a
  gap under the box, a bar across the hull, and a hop north on pack-up. Fixed by dropping the
  walk frames onto the deployed ground line (`WALK_DROP` in `scripts/ts_pack_jugg.py`).
- The Limpet Mine sits on the drone's shadow line, 11.6 classic px below the cell centre: a mine
  higher than that hops north the moment the drone deploys.

Measure, do not eyeball, as the field manual's
[How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#the-frame-and-its-meta)
says for the ground line. For reference, TS's 1x1 buildings sit about +10 to
+12 classic px below the cell centre, and unit shadows sit further out again the taller the unit
(Wolverine +13.9, Juggernaut deployed +18, Titan +22.8).

## 15. Vehicle hulls are centred on the unit

EA's HD vehicles centre the hull's opaque pixels on the unit to within 1.5 classic px (21 RA and
TD vehicles measured; the Mammoths sit 2.6 high). Turrets and barrels stick up past it, and art
bottoms vary from +6 to +14 classic px with size. The launcher centres the box on the unit, so a
centred hull gets a box that hugs it. Our voxel packers put the model's ground point at the canvas
centre, which drew hulls 3 to 7 px high: above EA's vehicles in the same row, with the box's slack
below. `scripts/unit_centring.py` centres them after packing and records the drop for
`Fire_Coord`. Size boxes from its printout (width = art width, height = 2 × the art's reach from
centre). Measuring only the two Mammoths gives a misleading ground-line rule. The
`unit-art-placement` skill (`.claude/skills/`) walks through a new or re-packed unit.

The launcher places a unit's box at the unit's centre and ignores
`CenterCoordY` and `Altitude` for it, alone or together (as it ignores them for buildings,
contract 7); only `DimensionX/Y` is ours. The airborne Jumpjet's lifted `CenterCoordY` does move
its box, but that path is infantry in flight and does not carry over to a ground vehicle. Buildings differ: see contract 7, where the box is the
plot's and the art must be seated on the plot.

## House quality policy for TS-sourced assets

**Every unit, building, and weapon pulled from Tiberian Sun ships at the
highest quality the pipeline can produce.** Concretely:

- **Voxels:** render at 12 px/voxel (`vxl_render.py --px-per-voxel 12`), pack
  at 8×-classic canvas density (canvas = stub × 8: MK2 480/60, MLRS 192/48 at
  hull parity, Titan 448/56) — same on-screen size, real pixels for the CFE
  zoom levels. Per-unit camera elevation is a legitimate dial (`--elev` — the
  Mk. II uses 35° for its TS stance).
- **TS SHPs:** upscale via hq4x (never bare NEAREST/LANCZOS), then LANCZOS to
  the target factor.
- **Voxel barrels/attachments:** render separately at 12 px/voxel and
  composite at the minimum downscale the canvas allows.
- **Buildings:** hq4x the decoded SHP frames (the Stealth Generator pattern,
  `scripts/ts_stealth_hq.py`).

## Also learned here (smaller, still binding)

- **Hand-anchored attachments need a generated muzzle table:** when barrel art
  is hand-tuned per facing (the Titan's Aseprite anchors), no single rotated
  `PrimaryOffset` can track the muzzle — flashes/shells drift per facing. The
  packer emits `redalert/tstitn_muzzle.h` (32-facing lepton offsets from the
  actual barrel-tip pixels) and `Fire_Coord` reads it. Re-tuning anchors =
  repack **then rebuild the DLL** (the table is compiled in).

- **TS art palettes:** the terrain palettes that give noise are `ISOTEM` and `TEMPERAT`; see the field manual's
  [Porting art from other C&C games](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/porting-art-from-other-games.md#tiberian-sun).
- **TS walker anatomy:** the SHP "turret" frames are the whole upper torso;
  the Titan's cannon is a separate voxel (`MMCHBARL.VXL`) composited at
  runtime (`art.ini` PBarrelLength) — it is NOT in the SHP.
- **MMCH.SHP facing order is CLOCKWISE**; the engine's frame space
  (`BodyShape[]`) is CCW 0=N. Voxel renders via `vxl_render.py --yaw0 90` are
  already CCW.
- **Launcher alpha cutoff ~128** (the field manual's
  [How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#rules)):
  bake shadows mostly-solid (~135+).
- **THE SHADOW CONVENTION (measured off EA's art, `ts_reshadow.py`).** Only things in the air get an engine
  shadow (`bullet.cpp:848`, `IsShadow` → `DisplayClass::UnitShadow`); ground shadows are baked, as the field
  manual's [How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#shadows-are-baked-in)
  says, soft-edged. On what the launcher draws
  (alpha 128 and up) EA's Mammoths throw about 3.8 classic px down and 4.8
  across, 19% of the hull; the medium tanks about two thirds as far. Our vehicles
  are Mammoth-sized, so `drop_shadow` is fitted to the Mammoths: offset
  (4, 22) at 8 canvas px per classic px, Gaussian blur 3, one setting for
  every vehicle. The HD packer (`ts_pack_hd_buildings.py`, `contact_shadow`)
  swaps the HD vehicles' own cast shadows, drawn as long as a building's, for
  it; `ts_reshadow.py` re-shadows the C&C3 tanks' packed ZIPs. The walkers keep
  their HD art's own shadows, and the Hover MLRS its separate shadow frames
  (5,17 throw: it hovers).
  ⚠ **Alpha is a cliff, not a dial:** the launcher discards below ~128, so a
  shadow diluted under it (a resize after `drop_shadow`) renders as nothing,
  and a blur's faint fringe never shows: measure shadows on the pixels at 128
  and up. Turret frames carry no shadow, which is what keeps TSHVR's rack
  seat out of its reach.
- **Baked shadows: always the offset-silhouette (`drop_shadow`), never a
  bottom-anchored shape** (why: the field manual's shadows section above). Both
  bottom-anchored recipes tried on the Hover MLRS (whole-hull squash at the bbox
  bottom, then the Mk. II bottom-slice) collapsed at the diagonal facings: a
  diagonal hull's bbox bottom is one pointy corner, so anything anchored there
  gathers at the corner instead of following the skirt. Scale
  the walker offset (14,18 @ 448 canvas) to the unit's canvas. (The Mk. II
  bottom-slice works there only because a mech's FEET genuinely span its bbox
  bottom.)
- **Walker gait system:** `WalkFrames=` / `WalkFacings=` / `WalkRate=` unit
  keys, walker branch in `UnitClass::Shape_Number`, turret block at
  `WalkFacings × WalkFrames`. Per-unit camera elevation is a legitimate dial
  (`vxl_render.py --elev` — the Mk. II renders at 35° for its TS stance vs the
  54° house camera).
- **Voxel turreted units** lay out hull frames 0-31 and turret 32-63 (TS4TNK, R2APOC, R2PRIS,
  TSSONIC); the layout lives in their pack scripts.
- **Voxel renders.** RA/TD Remastered HD unit sprites match a **~32° camera** (the 54°
  `vxl_render.py` default reads top-down beside RA art), so a ground-vehicle voxel renders at
  `--px-per-voxel 12 --team-green 0,200,0 --elev 32`. Every TS unit and the RA2 tanks ship as HD
  rebuilds instead, packed, seated and shadowed by `ts_pack_hd_buildings.py` (UNITS): nothing
  reshadows or re-crops them after a repack. VXLs are re-extractable from TIBSUN.MIX LOCAL.MIX via
  `tools/ts_extract.py`. Frame-0 convention: yaw0 90 ⇒ frame 0 = N advancing CCW (zip-native);
  yaw0 0 ⇒ E-start, needs the +8 face_fix.
- **Audio:** every TS unit ships its authentic TS sounds (weapon reports, and voices in time), under
  their own sample names; the format rules are in `td-audio-routing-recipe.md`.
