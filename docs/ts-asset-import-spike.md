# Tiberian Sun asset import — spike record (2026-07-17)

> **LIVE-SESSION OUTCOME (same evening, iterated with Luke in-game):**
> - **Stealth Generator reskin: SIGNED OFF ("PERFECT").** Final recipe: TS NASTLH art
>   (base + 16-frame `NASTLH_A` ring anim composited, damaged run at shapes 16–31, all
>   19 TS buildup frames), **2x1 footprint** (`BSIZE_21` + `List21` — NOT `StoreList`,
>   which is a 1-cell list and left a phantom footprint), **`FACING_NONE`** (FACING_S
>   made attackers aim one cell south — the "tanks shoot the bib" bug), no bib,
>   `_td_bdonors` → `STRUCT_TDSILO` (2x1 classic dims + construction anim).
> - **Hover MLRS: SIGNED OFF ("I think you've cracked it!", 00:07).** Final recipe:
>   48x48 classic stub (`scripts/gen_stub_shp.py` via `build_tfassets.sh`) = med-tank
>   box; art on 192 canvas with **112px hull** (content-cropped TGAs, model-space
>   turret alignment — body and turret placed via the shared voxel-origin math, NOT
>   centroid/bbox centering, which jitters per facing); flat skirt-hugging shadow
>   (18% silhouette height, alpha 160, half-tucked) + 3px lift + engine bob; turret
>   aft seat = precomputed 32-entry table in `UnitTypeClass::Turret_Adjust`, ground
>   distance 9 projected with the render camera's 13/16 vertical foreshortening
>   (NOT Normal_Move_Point — its classic vertical halving mismatches this art).
>   Calibration converged by Luke's compass-formation screenshot loop (10→40→22→
>   18→15→9). Key lesson: the aft push MUST be engine-side (turret frames follow
>   the turret's aim, so art-baked offsets slide around the hull).
> - **Scaling model (proven by calibration):** on-screen size follows the CLASSIC
>   ImageData box dimensions — the launcher fits art to that box; content pixel size
>   is secondary. A transparent stub SHP is the size lever for HD-only units.

**Status: IMPLEMENTED, built + deployed to the LOCAL Linux prefix, awaiting first
in-game verification.** One TS unit + one TS building, end-to-end from the Steam TS
install to the mod's HD pipeline. All changes UNCOMMITTED for Luke's review.

## What shipped in the spike

| Entity | Engine type | Art source | Notes |
|---|---|---|---|
| **Hover MLRS** (`TSHVR`) | `UNIT_TSHVR` | `HVR.VXL` + `HVRTUR.VXL` (voxels, rendered) | GDI, turreted, fires `TSHoverMissile` (TDSSM AA+AG chain, Burst=2, TS stats). Prereq `weap,dome`, TechLevel 7. |
| **Tiberian Power Plant** (`TSPOWR`) | `STRUCT_TSPOWR` | `GTPOWR.SHP` + `GTPOWRMK.SHP` (TS-SHP, upscaled) | GDI, clone of RA POWR (2x2, static). Power=100, Cost=300, Str 750. TechLevel 1. |

The `TS` IniName prefix is deliberate: it dodges the `TD`-prefix building HP-doubling
hook (playbook §3.21) — TS Strength values are real HP.

## The pipeline (all scripts in `scripts/`)

1. **Extract** — `~/Documents/development/cnc-remastered-mods/tools/ts_extract.py`
   pulls files from the Steam TS install's `TIBSUN.MIX` (RA container + Blowfish
   header, reuses `ra_mix_extract.py` crypto; TS filename hash = padded CRC32).
   Voxels + INIs live in `LOCAL.MIX`; unit/cameo SHPs in `CONQUER.MIX`; building
   SHPs in the theater mixes (`TEMPERAT.MIX` — NewTheater 'T' names, `GTPOWR`);
   buildups in `ISOTEMP.MIX`; palettes in `CACHE.MIX`.
2. **Render voxels** — `scripts/vxl_render.py <vxl> <outdir> --frames 32 --yaw0 90
   --px-per-voxel 6 --team-green 0,200,0`. Orthographic at the mod's 54° camera,
   geometry-derived normals (no VXL normal tables), remap palette range painted as
   the launcher's team-green (1.45x brightness lift per the naval findings).
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

## In-game verification checklist (next session / when Luke is home)

- [ ] GDI skirmish: TSPOWR cameo + name in sidebar at TechLevel 1; builds; buildup
      anim plays (13 HD frames via POWR's donor construction anim); idle renders;
      damaged frame at yellow; sell/refund; power contributes.
- [ ] TSHVR cameo after war factory + radar; builds; body renders at all facings;
      turret tracks targets independently; missiles fire (2-shot salvo), hit ground
      AND air; death explosion; crew survivor.
- [ ] House-color remap: the green zones recolor per player color and aren't
      olive/muddy (if dark, raise the 1.45 lift or brighten `--team-green`).
- [ ] Turret seat: rack sits on the deck at all 8 main facings (tune the ctor's
      vertical offset or re-render if not).
- [ ] Scale check vs neighbors (TDMTNK, RA 2TNK): hull ≈140px on 192 canvas — the
      right ballpark, adjust `ts_pack_art.py` target if it reads big/small.

## Hover locomotion — IMPLEMENTED (same session, evening pass)

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

Extra hover verification items:
- [ ] Order TSHVR from land onto open water and back — paths across the shoreline,
      no zone refusal, correct speed on water (100%).
- [ ] Attack-order a target across a lake — unit crosses rather than hugging shore.
- [ ] Cliffs and walls still block it; it can't climb LAND_ROCK.
- [ ] Enemy tanks do NOT try to chase it onto water (their zone gates reject).
- [ ] AI-owned TSHVR behaves (Guard/Hunt) without pathing stalls.
- [ ] Wall built/destroyed near it updates its pathing (zone recompute).

## Traps discovered during live testing (2026-07-17 evening, Luke's session)

1. **HD canvas must equal the classic donor's frame dims × 5.33.** The launcher's
   render box comes from `Get_Build_Frame_Width/Height(ImageData/BuildupData)`.
   WEAP classic 72×48 → 384×256 canvas (NOT square 384); POWR 48×48 → 256×256.
   Shipping a square canvas for a non-square classic donor squashes the art
   (the stealth-gen "pancake buildup"). Corollary: EVERY donor field with
   dimensions must match the footprint — ImageData (idle scale), BuildupData
   (buildup scale). The stealth gen donors both from WEAP; its 15-frame
   construction anim now drives a 15-shape TDSTEALMAKE.
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
4. **TS audio port (HOVRMIS1, the ClientG crash pair).** The launcher CANNOT
   resolve novel SFXEvent sample names — a sample not in its audio MEGs crashes
   `ClientG` in `SOUND_EFFECT_EVENT` (EIP 0xEB5E69, deterministic). Loose
   `Data/AUDIO` WAVs can only OVERRIDE same-named MEG samples. And the override
   WAV must be **MS-ADPCM** (wFormatTag=2, like every MEG sample) — a plain PCM
   override plays a few times then crashes the mixer. Working recipe: decode the
   TS `.AUD` (Westwood IMA-ADPCM; decoder in the session scripts), encode
   `adpcm_ms` via ffmpeg, ship under the name of a MEG sample that RA never
   plays (`TDR_SFX_BONUS_UNLOCK.WAV`), point both `RAC_/RAR_SFX_HOVRMIS1`
   events at it. Also: XML comments must not contain `--` (cost two deploys).
5. **Unit drop shadows = the hull silhouette offset down-right** (2TNK does
   exactly this), NOT a squashed strip at the bbox bottom — a strip detaches on
   diagonal facings. Rocket origin: `Fire_Coord` gets the same aft-along-body
   offset as the draw seat (draw-side `Turret_Adjust` is cosmetic only).

## Known deviations / accepted for the spike

- TS `TurretOffset=-64` (rear-mount) not modeled — RA land-unit turrets draw
  center-mounted; ~quarter-cell cosmetic difference.
- Building art is TS-isometric next to RA near-top-down neighbors — inherent to
  TS SHPs (only voxels can be re-camera'd); acceptance is the point of the spike.
- `Report=ROCKET1` (TD sound) instead of TS `HOVRMIS1` — TS audio routing is more
  extraction+SFX-XML work; queue if the spike is adopted.
- Voxel render is blocky up close (authentic to voxel source). If adopted, consider
  higher `--px-per-voxel` + stronger downsample, or per-voxel cube faces.
- Hover cosmetics not modeled: no bob/tilt animation, no wake on water, and the
  unit sits at ground height over water (no draw-height lift). All polish-tier.

## Legal note

TS assets are EA copyright (2010 freeware ≠ redistribution license; TS was never
GPL'd). Same tolerated category as the extracted TD-Remastered art the mod already
ships; CCHyper's TS/RA2 soundtrack mods are long-standing Workshop precedent. Ship
call is Luke's.
