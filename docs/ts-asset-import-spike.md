# Tiberian Sun asset import

**Status:** Reference; the pipeline shipped in 4.1.0.

The TS art pipeline, proven on the Hover MLRS and the TS Power Plant. Extraction, the crop
contract, the stub-size lever and the hover locomotor still hold; per-unit rules live in the
`unit-art-placement` and `ts-to-ra-hd-art` skills and in `ts-gdi-tree-plan.md`.

**Results that set the pattern:**
- **The Stealth Generator reskin:** TS NASTLH art (base + the 16-frame `NASTLH_A` ring composited,
  damaged run at shapes 16-31, all 19 TS buildup frames), a **2x1 footprint** (`BSIZE_21` +
  `List21`; `StoreList` is a 1-cell list and left a phantom footprint), **`FACING_NONE`** (FACING_S
  made attackers aim one cell south), no bib, `_td_bdonors` → `STRUCT_TDSILO`.
- **The Hover MLRS:** a 48x48 classic stub (`scripts/gen_stub_shp.py` via `build_tfassets.sh`), art
  content-cropped on a 192 canvas, body and turret placed by the shared voxel-origin maths (bbox or
  centroid centring jitters per facing). The turret's aft push must be engine-side: turret frames
  follow the aim, so an offset baked into the art slides round the hull.
- **On-screen size follows the classic ImageData box;** the launcher fits the art to it, so a
  transparent stub SHP is the size lever for HD-only units.

## What shipped in the spike

| Entity | Engine type | Art source | Notes |
|---|---|---|---|
| **Hover MLRS** (`TSHVR`) | `UNIT_TSHVR` | `HVR.VXL` + `HVRTUR.VXL` (voxels, rendered) | turreted, fires `TSHoverMissile` (Burst=2, TS stats, `HOVRMIS1`). |
| **Tiberian Power Plant** (`TSPOWR`) | `STRUCT_TSPOWR` | `GTPOWR.SHP` + `GTPOWRMK.SHP` (TS-SHP, upscaled) | clone of RA POWR. Power=100, Cost=300, Str 750. |

The `TS` IniName prefix is deliberate: it dodges the `TD`-prefix building HP-doubling
hook (playbook §3.21) — TS Strength values are real HP.

## The pipeline (all scripts in `scripts/`)

1. **Extract** — `~/Documents/development/cnc-remastered-mods/tools/ts_extract.py`
   pulls files from the Steam TS install's `TIBSUN.MIX` (RA container + Blowfish
   header, reuses `ra_mix_extract.py` crypto; TS filename hash = padded CRC32).
   Voxels + INIs live in `LOCAL.MIX`; unit/cameo SHPs in `CONQUER.MIX`; building
   SHPs in the theater mixes (`TEMPERAT.MIX` — NewTheater 'T' names, `GTPOWR`);
   buildups in `ISOTEMP.MIX`; palettes in `CACHE.MIX`.
2. **Render voxels** — `scripts/vxl_render.py <vxl> <outdir> --frames 32 --yaw0 90`,
   orthographic, with geometry-derived normals (no VXL normal tables) and the remap range
   painted as the launcher's team green. The fleet renders at the 32° camera with TS's own
   lighting (`--shade ts`); per-model settings are in `ts-gdi-tree-plan.md` and the skills.
   **Voxel +X = nose = east at yaw 0; `--yaw0 90` puts frame 0 north; frames advance
   CCW** (verified against vanilla 2TNK HD frames: 0=N, 8=W).
3. **Decode TS SHPs** — `scripts/ts_shp.py <shp> <pal> <outdir>` (TS-SHP format,
   RLE-zero scanlines, remap 16–31 → team-green). GTPOWR frames: 0=healthy,
   2=damaged; 3–5 are palette-anim overlays (unused). GTPOWRMK: frames 0–19 real
   buildup, 20–39 magenta anim overlays (unused).
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

RA now has a real amphibious hover locomotor, and TSHVR uses it (`Hover=yes`):

- **`SPEED_HOVER`** appended to SpeedType (defines.h) — TD had this slot, RA had
  dropped it. Ground costs parsed from a new `Hover=` key in each land section
  (`rules.cpp Land_Types`); rules.ini carries the TS-authentic table: **100% on
  everything passable including Water/Beach/River/Ore, 0% on Rock/Wall**.
- **`MZONE_HOVER`** appended to MZoneType with its own flood-fill in
  `MapClass::Zone_Reset`/`Zone_Span` using SPEED_HOVER passability — one zone
  spans land AND water, so all ~20 zone-equality gates (Basic_Path, Mission_Move,
  Active_Click_With, Approach_Target, Greatest_Threat, Nearby_Location,
  Find_Spread_Cell, reinforcement cells…) pass for cross-shoreline orders without
  touching any of them individually. `TechnoTypeClass::Read_INI` derives
  `MZone = MZONE_HOVER` from `Speed == SPEED_HOVER`; Chronosphere teleport
  (`Can_Teleport_Here`) extended likewise.
- Wall/terrain Zone_Reset callers (cell.cpp wall place, house.cpp wall sell/destroy,
  terrain.cpp crumble) now include `MZONEF_HOVER` so hover zones track wall changes.
- `UnitTypeClass::Read_INI`: new `Hover=yes` key overrides the Tracked/Wheel binary.
- **Save-format note:** `CellClass::Zones[]` grew by one — old skirmish saves won't
  load (standard consequence of any enum addition here; accepted).

## Traps

1. **HD canvas must equal the classic donor's frame dims × 5.33.** The launcher's
   render box comes from `Get_Build_Frame_Width/Height(ImageData/BuildupData)`.
   WEAP classic 72×48 → 384×256 canvas (NOT square 384); POWR 48×48 → 256×256.
   Shipping a square canvas for a non-square classic donor squashes the art
   (the stealth-gen "pancake buildup"). Corollary: EVERY donor field with
   dimensions must match the footprint — ImageData (idle scale), BuildupData
   (buildup scale). The Stealth Generator donors both from TDSILO (48x24, its full
   TDSILOMAKE construction anim).
2. **The TGA/meta contract (the big one — three symptoms, one cause).** Verified
   against vanilla 2TNK (`tga=(75,95)`, `size=[192,192]`, `crop=[59,57,134,152]`):
   - the TGA file is **cropped to content**, not full-canvas;
   - meta `size` = the virtual canvas dimensions;
   - meta `crop` = corner bounds `[x0,y0,x1,y1]` giving where the cropped image
     sits on that canvas (59+134 > 192 proves it's bounds, not w/h).
   Shipping full-canvas TGAs makes the launcher squeeze the whole canvas into the
   crop rect → per-frame squash (MLRS sliver/needle), per-frame drift (stealth-gen
   "sliding" buildup), and undersized units. Near-full-canvas content hides the bug
   (why TSPOWR looked almost right). Fixed in `scripts/ts_pack_art.py::write_zip`.
3. **Unit on-screen size is NOT an art property.** The launcher fits unit art to
   the classic ImageData box; the honest size lever for an HD-only unit is a
   transparent classic stub SHP with the wanted dimensions (`gen_stub_shp.py`).
   Draw-scale (`Techno_Draw_Object` arg) also works but shears turret alignment
   (scales about the ground anchor per draw) and doesn't scale the health-bar/
   selection UI.
4. **Audio:** the launcher resolves novel sample names from loose files; the rule is format, an
   MS-ADPCM WAV matching the channel's shape (`launcher-render-contracts.md`). A plain PCM WAV
   plays a few times, then crashes ClientG's mixer. XML comments must not contain `--`.
5. **Unit drop shadows = the hull silhouette offset down-right** by a fixed 2,6 px
   (`scripts/ts_reshadow.py`), never a fraction of the sprite, and never a squashed strip at
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
GPL'd). Same tolerated category as the extracted TD-Remastered art the mod already
ships; CCHyper's TS/RA2 soundtrack mods are long-standing Workshop precedent. The mod
ships it.
