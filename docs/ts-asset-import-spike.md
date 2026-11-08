# Tiberian Sun asset import

**Status:** Reference; the pipeline shipped in 4.1.0.

The TS art pipeline, proven on the Hover MLRS and the TS Power Plant. Extraction, the crop
contract, the stub-size lever and the hover locomotor still hold; per-unit rules live in the
`unit-art-placement` and `ts-to-ra-hd-art` skills and in `ts-gdi-tree-plan.md`.

**Results that set the pattern:**
- **The Stealth Generator reskin:** TS NASTLH art (base + the 16-frame `NASTLH_A` ring composited,
  damaged run at shapes 16-31, all 19 TS buildup frames), a **2x1 footprint** (`BSIZE_21` +
  `List21`) and **`FACING_NONE`**, both for the reasons in the field manual's
  [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#placement-and-the-ai),
  no bib, `_td_bdonors` → `STRUCT_TDSILO`.
- **The Hover MLRS:** a 48x48 classic stub (`scripts/gen_stub_shp.py` via `build_tfassets.sh`), art
  content-cropped on a 192 canvas, body and turret placed by the shared voxel-origin maths (bbox or
  centroid centring jitters per facing). The turret's aft push must be engine-side: turret frames
  follow the aim, so an offset baked into the art slides round the hull.
- **On-screen size follows the classic ImageData box,** so a transparent stub
  (`scripts/gen_stub_shp.py`) is the size lever for HD-only units, never a draw scale (the field manual's
  [HD tilesets and ZIPs](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/hd-tilesets-and-zips.md#size-comes-from-the-classic-shape)).

## What shipped in the spike

| Entity | Engine type | Art source | Notes |
|---|---|---|---|
| **Hover MLRS** (`TSHVR`) | `UNIT_TSHVR` | `HVR.VXL` + `HVRTUR.VXL` (voxels, rendered) | turreted, fires `TSHoverMissile` (Burst=2, TS stats, `HOVRMIS1`). |
| **Tiberian Power Plant** (`TSPOWR`) | `STRUCT_TSPOWR` | `GTPOWR.SHP` + `GTPOWRMK.SHP` (TS-SHP, upscaled) | clone of RA POWR. Power=100, Cost=300, Str 750. |

The `TS` IniName prefix is deliberate: it dodges the `TD`-prefix building HP-doubling
hook (playbook §3.21) — TS Strength values are real HP.

## The pipeline (all scripts in `scripts/`)

1. **Extract** — the workspace's `tools/ts_extract.py` (reusing `ra_mix_extract.py`'s crypto)
   pulls files from the Steam TS install's `TIBSUN.MIX`; the archives and where each kind of file
   sits are in the field manual's [Porting art from other C&C games](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/porting-art-from-other-games.md#tiberian-sun).
   Building build-ups come from `ISOTEMP.MIX`.
2. **Render voxels** — `scripts/vxl_render.py <vxl> <outdir> --frames 32 --yaw0 90`,
   orthographic, with the model's own VXL normals through TS's normal tables (the default
   `--normals vxl`; `--normals geo` derives them from geometry) and the remap range
   painted as the launcher's team green. The fleet renders at the 32° camera with TS's own
   lighting (`--shade ts`); per-model settings are in `ts-gdi-tree-plan.md` and the skills.
   **Voxel +X = nose = east at yaw 0; `--yaw0 90` puts frame 0 north; frames advance
   CCW** (verified against vanilla 2TNK HD frames: 0=N, 8=W).
3. **Decode TS SHPs** — `scripts/ts_shp.py <shp> <pal> <outdir>` (TS-SHP format,
   RLE-zero scanlines, remap 16–31 → team-green). GTPOWR frames: 0 healthy, 1 damaged,
   2 more wrecked (TS never draws it: `Shape_Number` picks 0 or 1), 3–5 their shadows (unused); GTPOWRMK: 0–19 the build-up, 20–39 its
   shadows (unused). The frame rules are in the field manual's
   [Porting art from other C&C games](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/porting-art-from-other-games.md#tiberian-sun).
4. **Package** — `scripts/ts_pack_art.py` (set `TS_RENDER_DIR` to the render dir):
   TSHVR.ZIP (64 frames: body 0–31 + turret 32–63, 192px canvas, hull ≈140px,
   turret center-aligned to body canvas — model-space origins line up), TSPOWR.ZIP
   (2 frames, 256px canvas, 96→256 crisp upscale), TSPOWRMAKE.ZIP (13 frames
   resampled from the 20 to match POWR's 13 MAKE shapes), tile runs appended to
   `RA_UNITS.XML`/`RA_STRUCTURES.XML`, `RABUILDABLES.XML` entries, `ModText.csv`
   strings, and loose `BuildIcon_TS_HoverMLRS/PowerPlant.tga` (341×256, upscaled TS
   cameos `HOVRICON`/`POWRICON`).

## Engine touch points (all follow existing patterns)

- `defines.h`: `UNIT_TSHVR`, `STRUCT_TSPOWR`, `WEAPON_TSHOVERMISSILE` (each last
  before its `_COUNT`).
- `udata.cpp`: `UnitTsHvr` ctor (turreted, non-crusher, FRAG1, 2TNK render geometry)
  + Init_Heap tail + a One_Time NULL-guard donating **2TNK's ImageData** (no classic
  SHP exists; same pattern as bdata's `_td_bdonors`).
- `bdata.cpp`: `ClassTsPowr` (verbatim ClassPower clone) + Init_Heap tail +
  `{STRUCT_TSPOWR, STRUCT_POWER}` in `_td_bdonors[]` (ImageData/BuildupData/cameo +
  construction anim from POWR).
- `rules.cpp`: `new WeaponTypeClass("TSHoverMissile")` + `IsTDPort = true`.
- `CCDATA/rules.ini`: `[TSHVR]`, `[TSHoverMissile]`, `[TSPOWR]`.

## Hover locomotion

RA now has a real amphibious hover locomotor, and TSHVR uses it (`Hover=yes`), built by the method in the field
manual's [Hover and amphibious units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/hover-and-amphibious-units.md#the-method-in-red-alerts-dll):
`SPEED_HOVER` and `MZONE_HOVER` (`defines.h`), a `Hover=` column per land section (`rules.cpp Land_Types`; rules.ini carries
TS's table as 100% on everything passable including Water, Beach, River and Ore, 0% on Rock and Wall), a `Hover=yes`
unit key read in `UnitTypeClass::Read_INI` that overrides the Tracked/Wheel choice, the `MZone` derived in
`TechnoTypeClass::Read_INI`, `Can_Teleport_Here`, and `MZONEF_HOVER` in
the zone-reset callers (cell.cpp wall place, house.cpp wall sell/destroy, terrain.cpp crumble). The shared zone opens about 20
zone-equality gates; besides the manual's list they include `Mission_Move`, `Find_Spread_Cell` and the reinforcement
cells. Old skirmish saves won't load (`CellClass::Zones[]` grew by one).

## Traps

The canvas, the build-up's `BuildupData` box, the TGA/meta crop contract, the sample format and XML comments with
no `--` are in the field
manual's [HD tilesets and ZIPs](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/hd-tilesets-and-zips.md#size-comes-from-the-classic-shape),
[How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#the-frame-and-its-meta) and
[TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#samples-of-your-own).
What they cost here:

1. **Canvas = the classic donor's frame × 5.33.** A square canvas on the Stealth Generator's non-square donor gave
   the "pancake buildup". It donors both `ImageData` and `BuildupData` from TDSILO (48x24, its full TDSILOMAKE
   construction anim).
2. **Full-canvas TGAs** squeezed into the crop gave a per-frame squash (the MLRS sliver), per-frame drift (the
   Stealth Generator's sliding build-up) and undersized units; near-full-canvas content hid it (TSPOWR looked
   almost right). Fixed in `scripts/ts_pack_art.py::write_zip`.
3. **Audio:** a plain PCM WAV played a few times before it crashed the launcher.
4. **Unit drop shadows = the hull silhouette offset down-right** by a fixed 4,22 canvas px
   (8 per classic px, `scripts/ts_reshadow.py`), never a fraction of the sprite, and never a squashed strip at
   the bbox bottom, which detaches on diagonal facings. Rocket origin: `Fire_Coord` gets the same aft-along-body
   offset as the draw seat (draw-side `Turret_Adjust` is cosmetic only).

## Known deviations

- Building art is TS-isometric beside RA's near-top-down neighbours: inherent to TS SHPs (only
  voxels can be re-cameraed). The TS HD rebuilds (`ts-to-ra-hd-art` skill) address it.
- Voxel renders are blocky up close, authentic to the voxel source.
- The Hover MLRS has an engine bob but no tilt, no wake on water, and no draw-height lift over
  water.

## Legal note

TS assets are EA copyright (2010 freeware ≠ redistribution license; TS was never
GPL'd). EA's C&C modding guidelines license other C&C games' art, sounds and voices to
mods, revocably, but no music file from any C&C game (`ea-modding-guidelines.md`). The
mod ships TS art and sounds on that licence.
