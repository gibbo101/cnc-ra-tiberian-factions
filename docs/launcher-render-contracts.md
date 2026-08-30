# Launcher render contracts — discoveries from the TS walker ports (2026-07-20)

Six hard-won rules from porting the TS Titan (`UNIT_TSTITN`) and Mammoth Mk. II
(`UNIT_TSHMEC`) with a working railgun. Every one of these cost a build-test
cycle to find; check this list BEFORE shipping any new unit art, anim, or
beam weapon. Fix-site comments exist in code; this doc is the collected story.

## 1. Sprites anchor by the VIRTUAL CANVAS CENTER — place content accordingly

The launcher anchors the meta `size` canvas's CENTER at the object's draw
position; the meta `crop` only places the TGA on that canvas. So a unit's
visual mass must be composed CENTERED on the canvas — content placed low
draws low:

- the Titan's feet-at-174-of-192 placement drew the mech ~45px below its cell
  (selection box floating above it, "med tank shells missing" — they hit the
  real, undrawn spot). The fix was placement (assembly centered), not crops.
- ⚠️ A "crop-rect-center anchoring" theory was briefly believed (it fits the
  Titan evidence equally — for tight crops, crop center == content center) and
  was FALSIFIED by the Hover MLRS remake: content-centering its high-riding
  rocket rack sank the rack into the platform; restoring model-space
  (canvas-center) placement fixed it. Don't re-adopt that theory.

**Rule:** compose every frame with its visual center (for voxel renders: the
render canvas = model origin) at the tileset canvas center. `write_zip` in
`scripts/ts_pack_walkers.py` additionally makes every crop center-symmetric,
which is kept as insurance — it makes both anchoring interpretations coincide.

## 2. Sub-object draws drop shape indexes ≥ 128

A second draw call on the same object (turrets; also radar dishes, harvester
stage overlays) silently renders NOTHING for shape numbers ≥ 128 ("cannon
missing" #2 — the walk-layout turret block sat at 120–151). Base-object draws
are NOT capped (the Mk. II body uses shapes up to 255 fine).

**Rule:** any tileset whose shapes are drawn as a second draw on the object
must keep those indexes ≤ 127. The Titan ships 8 facings × 12 walk frames
(96) + 32 turret = exactly 128 shapes for this reason.

## 3. The line renderer supports animation frames 0–4 only

`CC_Draw_Line`'s Frame param (fed from `TechnoClass::LineFrame`) indexes a
5-entry launcher table. Frames ≥ 5 render as GIANT squares at the line's two
endpoints, in the line's own color — the railgun "white boxes" saga (they
turned red when the beam did, which was the giveaway). The Obelisk never hit
it because TD's `LineMaxFrames = 5` sends 0–4.

**Rule:** `LineMaxFrames <= 5` for anything using the `Lines[]` beam path.
Related: `MAX_OBJECT_LINES = 3` (dllinterface.h ABI — cannot grow).

## 4. Custom anim types DO render; the white box is the sub-object endpoint bug

⚠️ **Corrected 2026-08-22.** This entry used to read "new anim TYPES are
launcher-dead — a DLL-added `AnimType` renders the white placeholder regardless
of tileset registration". That is falsified by our own Ion Cannon:

- `ANIM_TD_ION_CANNON` is a **DLL-added** anim type (`adata.cpp`).
- Its art is **mod-shipped**, not base-MEG: `TDIONSFX.ZIP`, 5.6MB, in the mod's
  own `RED_ALERT/VFX/` directory. The code comment claiming it resolves to the
  base game's `ionsfx` frames is wrong.
- It is registered exactly like any other tile, 32 shapes in `RA_VFX.XML`.
- It renders, play-verified in the superweapon arc.

So a DLL-added anim type with mod-shipped art and a tileset entry is a working
combination. `RAILFX` failed for a different, separately-documented reason: an
anim spawned inside the firer's or the target's own cell attaches to that object
and exports through the launcher's **sub-object** path, which draws the white
placeholder box (`techno.cpp`, the "endpoint-box bug"). The fix — start the
helix a full cell clear of both endpoints — was applied to `ANIM_PIFFPIFF` and
**RAILFX was never retried after it**. RAILFX's art is fine: 12 frames, valid
meta, real pixels, all 12 shapes registered, correct XML scope (checked).

Still true: avoid the `AnimClass` ctor's `timedelay` param — vanilla never uses
it and delayed anims export in a pre-start state.

**Corrected again 2026-08-24: the cell rule is FALSE.** The white box is drawn
for any anim STAGE that has no tile in the tileset XML (proven: bumping
TSSONICW to 25 stages with 8 tiles declared boxed stages 8-24; the sonic
discs now spawn inside the firer's own cell and draw no box). RAILFX at the
time had fewer tiles declared than stages, which is what the "endpoint box"
was. The export loop draws every layer object, anims included, as its own
root (`dllinterface.cpp`, `CurrentDrawCount = 0` per object) — a free anim
never becomes a sub-object by position.

**Rule:** custom-art anims are viable anywhere. Declare exactly as many tiles
as the anim has stages (have the generator patch the XML, as
`ts_gen_sonicwave.py` does), and write STRAIGHT alpha: PIL `paste(colour,
mask)` onto a transparent canvas darkens the RGB toward black and the launcher
draws the darkened sprite faithfully (read as grey/gold before it was caught).

## 5. Hull-fixed direct-fire units need `IsLockTurret = true`

`unit.cpp`'s FIRE_FACING handler only rotates the BODY toward the target when
`IsLockTurret` is set (the ARTY/V2 convention — the flag doubles as "turn the
hull to aim"). Without it, a turretless unit aims its nonexistent turret
forever and never fires ("won't turn to shoot", the Mk. II).

## 6. Pillow `paste` with an RGBA mask corrupts at negative offsets

Pillow 10.2: pasting with a negative position and a mask produces
interleaved-strip garbage, not a clean clip — this silently shredded the
Titan's turret frames for several builds (only the thin antenna survived,
"cannon missing" #0). Use `safe_paste()` (pre-crops the source) everywhere in
the art pipeline.

## 7. Building selection boxes: the launcher owns POSITION, we own only SIZE

Proven over five probe rounds (2026-08-13, ~one build-test cycle each — never
spend another): the launcher centres a building's selection box on the
building's plot by its own internal reckoning and takes ONLY `DimensionX/Y`
(the box size, classic px) from the DLL's object export. Every position
candidate was falsified live:

- `CenterCoordY` bias — ignored (two bias-only moves, zero pixels).
- Dimension-change "anchoring" — height changes grow the box symmetrically
  around the plot centre; there is no fixed-edge growth.
- `CellY` bias — ignored.
- A doctored render-side `OccupyList` (bounding-box centring theory) — ignored.
- `PositionY` bias — moves the SPRITE, not the box: the exported draw rect is
  the art's anchor (the probe visibly detached the refinery from its
  building-derived apron). Art and box cannot be decoupled by any export field.

Corollaries: a box reads wrong exactly when the ART is seated off its plot
centre (the TSFACT slab reseat is what "broke" its box — the box never moved).
TDFACT (correct box, same 3x3 plot, same pipeline) vs TSFACT (box a tile high)
is the standing control pair for the one unexplored lever: classic stub /
canvas geometry. Open boxes as of 2026-08-13: TSFACT (1 tile high), TSDROP
(1 tile low), TSPROC (Luke wants 2 tiles more headroom than a plot-centred box
can give). Fix path: diff TDFACT's stub/canvas content geometry against
TSFACT's and transplant the relationship, art compensated to stay put.

## 8. Anim exports honour `Rotation`, but the rotated texture is clipped to the UNROTATED frame

Proven 2026-08-27 on the Disruptor band (fx bit 128 in `tf_sonic_cloak.flag`): setting
`CNCObjectStruct::Rotation` on an anim export turns the sprite onto that DirType (E, N and SE
all verified in play), which the 2026-08 "spawned anims draw unrotated" note did not know.
The catch: the launcher rotates the texture inside the sprite's quad but keeps the quad at
the packed frame's unrotated size, so anything outside that rectangle is cut off. A 64x112
strip frame drew as a 64-wide bar at N/S and a sawtooth of axis-aligned rectangles on the
diagonal; a near-square 124x72 oblong survived. **Rule: a sprite that will be exported
rotated must be packed as a SQUARE frame (no bbox crop) with the art inside the inscribed
circle.** `ts_gen_sonicwave.py::write_zip(square=True)` did this; the strip itself was
rejected in play, the contract stands.

## 9. Overlapping-sprite chains can never give a hard edge or keep a texture

Measured offline against the TS Disruptor footage before the strip attempt: a chain of
discs overlapping 6-7 deep (a) ramps its alpha at the strip edge whatever the disc edge
does, because chord coverage falls off toward the edge (35-75 px ramps for every variant),
and (b) smears any per-disc mottle along the chain (best interior std 7 vs TS's 19.5). If
a hard edge or a preserved texture is the requirement, the primitive must be a single
rotated sprite per span (§8), not a chain.

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

## 11. Voxel units are lit the way Tiberian Sun lights them — and a relight never re-places a sprite (2026-08-28, signed off "night and day")

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
  reads as **blotches across flat decks** (Luke: "patchy"). Real normals light decks evenly and brighter.
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
  the surface, as RA's ships do — Luke: "much better"). **Never run `ts_reshadow.py` over the water
  frames.**
- Titan and Wolverine are TS SHPs (MMCH/SMECH), not renders, with TS's light baked per facing (a mech
  turned away from the light read a step darker: Wolverine SE vs S, Titan N a quarter under NE).
  `scripts/ts_equalise_shp_facings.py` levels each facing block to the brightest block's mean body
  luminance (idempotent; in-frame shading and shadows untouched). The Titan's cannon barrel
  (`MMCHBARL.VXL`, 30° render inside the walkers script) is still legacy-lit — needs the Titan inputs.
- **Voxel-mesh upscale: SPIKED AND REJECTED (2026-08-28, harvester A/B in-game).** `scripts/vxl_mesh_render.py`
  (marching cubes + Taubin smoothing + denoised vertex colours, TS lighting) renders a smoother hull,
  but at game sprite scale the 1-voxel ribs and panel lines ARE the detail, and any smoothing that
  rounds the staircase rounds them away — Luke: "the smaller one has more detail", "lost some side
  panelling". The voxel render with real normals stays. Script kept for reference only (needs a
  scikit-image venv). Don't re-chase unless units are drawn larger than the game does.

## House quality policy for TS-sourced assets (Luke, 2026-07-20)

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

- **TS art palettes:** units/buildings decode with `UNITTEM.PAL`; cameos with
  `CAMEO.PAL`; `ISOTEM`/`TEMPERAT` are terrain-only and produce noise.
- **TS walker anatomy:** the SHP "turret" frames are the whole upper torso;
  the Titan's cannon is a separate voxel (`MMCHBARL.VXL`) composited at
  runtime (`art.ini` PBarrelLength) — it is NOT in the SHP.
- **MMCH.SHP facing order is CLOCKWISE**; the engine's frame space
  (`BodyShape[]`) is CCW 0=N. Voxel renders via `vxl_render.py --yaw0 90` are
  already CCW.
- **Launcher alpha cutoff ~128:** sprite pixels below roughly half alpha are
  discarded — soft low-alpha shadows render as nothing; bake shadows
  mostly-solid (~135+).
- **⭐ THE SHADOW CONVENTION (measured off EA's art 2026-08-20, `ts_reshadow.py`).**
  Ground units get NO engine shadow — the DLL only shadows things in the air
  (`bullet.cpp:848`, `IsShadow` → `DisplayClass::UnitShadow`). Every ground
  shadow is baked into the sprite, EA's included. Fitting a shifted copy of the
  body against EA's actual shadow region scores **IoU 0.72–0.88** across their
  whole TD vehicle set, so EA bakes an offset silhouette exactly like we do.
  Their tuning, measured off the BASE GAME's own art (`TEXTURES_RA_SRGB.MEG`:
  2TNK/3TNK/MCV/JEEP) and independently confirmed against the **TD Medium Tank,
  which is Luke's reference unit** — RA and TD share one convention:
  **dx = 0.028 × body width, dy = 0.120 × body width, alpha 191.**
  ⚠ A first pass used means taken off our repacked TD art (0.042 / 0.138) and
  the in-game verdict was "way over done" on every ground unit. **Alpha was
  never the problem** — 191 pure black is exactly what RA and TD both bake —
  the throw was simply ~50% too far sideways and ~20% too far down, and the
  visible shadow band inflates in proportion. Measure against base-game art,
  not against our own ports.
  **Exception, `OFFSET_OVERRIDE`: the Hover MLRS keeps the longer (5,17)
  throw** — Luke passed it at the TD-derived numbers while rejecting every
  ground unit, and it is the roster's only true hover unit, so a shadow thrown
  further than a ground hull's reads as float rather than as error.
  Both offsets scale off **WIDTH, never height** — width tracks the ground
  footprint, height also carries how tall the thing stands, and height-scaling
  threw the Wolverine's and Mk. II's shadows clear of their feet. The ratio
  (dy/dx ≈ 3.3) reproduces EA's measured dy/dx ≈ 3 independently, so the light
  direction falls out of the data: **high and near-south, only slightly east.**
  Our TS art had shipped at dy/dx ≈ 1.3 — a 45° throw that reads as a hard
  black duplicate of the hull rather than as ground shade.
  ⚠ **Alpha is a cliff, not a dial:** the launcher discards below ~128, and
  three TS units were rendering NO shadow at all — TSHARV (alpha 66) and
  TSHMEC (71) had been diluted under the cutoff by a resize applied AFTER
  `drop_shadow`, and TSMCV had no shadow layer whatsoever. `ts_reshadow.py`
  runs on the PACKED zips as the authoritative final pass, after any resize,
  and is safe to re-run: it strips the old shadow before applying its own,
  preserves body pixels byte-for-byte, and the center-symmetric crop keeps the
  body's on-screen position invariant. Turret frames carry no shadow, which is
  what keeps TSHVR's dialled rack seats out of its reach.
- **Baked shadows: always the offset-silhouette (`drop_shadow`), never a
  bottom-anchored shape.** Both bottom-anchored recipes tried on the Hover
  MLRS (whole-hull squash at the bbox bottom, then the Mk. II bottom-slice)
  collapse into a detached floating nub at diagonal facings — a diagonal
  hull's bbox bottom is one pointy corner, so anything anchored there
  concentrates at the corner instead of following the skirt. The full
  silhouette offset down-right and composited UNDER the sprite hugs the whole
  lower edge at every facing; scale the walker offset (14,18 @ 448 canvas) to
  the unit's canvas. (The Mk. II bottom-slice works there only because a
  mech's FEET genuinely span its bbox bottom.)
- **Walker gait system:** `WalkFrames=` / `WalkFacings=` / `WalkRate=` unit
  keys, walker branch in `UnitClass::Shape_Number`, turret block at
  `WalkFacings × WalkFrames`. Per-unit camera elevation is a legitimate dial
  (`vxl_render.py --elev` — the Mk. II renders at 35° for its TS stance vs the
  54° house camera).
- **⭐ VOXEL RENDER LEDGER (2026-08-18 — keep this current; its absence cost
  an evening).** RA/TD Remastered HD unit sprites match a **~32° camera**
  (Luke's pick, commit 51469c8c: "the 54-degree default read top-down"), so
  EVERY ground-vehicle voxel renders at `--elev 32`; the vxl_render default
  is 54 and reads alien next to RA art. Current renders, all
  `--px-per-voxel 12 --team-green 0,200,0 --elev 32`:
  TSHARV (yaw0 0 + wave face_fix, pack scale 0.75), TSAPC (yaw0 0 + face_fix; water hull
  `apcw.vxl` same camera → `ts_pack_tsapc_water.py`), TSSONIC (yaw0 90, no reorder, `--canvas 628`)
  + SONICTUR (**`--hva SONICTUR.HVA`** — the turret's pose is in the HVA; without it the render is
  38 px taller and sits 78 px lower, `--canvas 624`), TSMCV (yaw0 90, no reorder →
  `ts_pack_tsmcv.py`), TSHVR (yaw0 90, `--canvas 500`) + HVRTUR (**`--z-clip 10`** drum clip,
  `--canvas 660`) → `ts_pack_hvr_hmec.py`, TSHMEC (yaw0 90, **`--elev 35`**, `--hva HMEC.HVA
  --hva-frame f` for f in 0 2 4 6 8 11 13 15, `--canvas 1000`, dirs `ts35_hmec_<f>`) → same script.
  Aircraft: DSHP dropship `--yaw0 180 --elev 32 --canvas 656 --px-per-voxel 6.4 --team-green
  255,204,51` → `ts_pack_dropship.py`. After ANY repack: `ts_reshadow.py` (not on water frames), then
  `ts_recrop_to_shipped.py` — see contract 11. VXLs
  re-extractable from TIBSUN.MIX LOCAL.MIX via tools/ts_extract.py.
  Frame-0 convention: yaw0 90 ⇒ frame 0 = N advancing CCW (zip-native);
  yaw0 0 ⇒ E-start, needs the wave's +8 face_fix.
- **Audio policy (Luke, 2026-07-20): every TS unit ships its AUTHENTIC TS
  sounds** — weapon reports, and eventually voices — via the dormant-sample
  recipe (`td-audio-routing-recipe.md` + the HOVRMIS1 trap notes).
- **Dormant-sample audio hosts — ~176 slots, count needs a re-census**
  (2026-07-20: 221 TD-side samples in SFX3D.MEG, 47 referenced by RA-side
  events; the true free count is lower because that census missed
  GUI-referenced samples — see the rule below).
  Rule: a TD?_SFX_* sample is a valid host iff no RAC_/RAR_ **and no
  SFX_GUI_*** event in our shipped SFXEVENTSNONLOCALIZED.XML references it —
  TDC_/TDR_-named events only fire in TD game context, never in our mod, but
  GUI events are game-agnostic and DO fire in RA mode (proven 2026-07-22:
  SFX_GUI_Generic_Bad_Sound plays SCOLD1, which the RAC_/RAR_-only census had
  marked dormant). ⭐ **THE DORMANT-HOST CONSTRAINT IS FALSIFIED (2026-08-31,
  controlled live probe): NOVEL sample names RESOLVE from loose files.** A
  novel-named copy of known-good bytes played on the EVA channel
  (RAR_SFX_TDCONSTRU1 → "TSEVA_PROBE2_EN-US.MP3" → loose file, played), and a
  same-name loose override of a localized sample played in the same run. Every
  historical "novel name" failure was file FORMAT: the old crash was plain-PCM
  hitting the ADPCM math (EIP 0x400000+0xAB5E69), and two 08-30 probes failed
  as an actual MP3 / wrong-shape WAV. **The real rules: (1) format must be
  MS-ADPCM WAV (the localized "MP3" entries are a lie — MEG members are
  ADPCM WAVs, e.g. EVA lines stereo 44077 Hz align 140; SFX 22050 mono align
  1024); (2) localized samples live under a locale dir (Data/AUDIO/EN-US/) and
  the XML .MP3 extension maps to a .WAV member; (3) bad format fails silent or
  crashes — md5+fmt-check files against a base sample of the same channel.**
  Dormant hosts are now just a legacy technique (the 6 shipped ones keep
  working); new audio ships under its OWN names. **END-TO-END PROVEN
  2026-08-31: an actual TS EVA line played in-game** — TIBSUN.MIX SPEECH01.MIX
  `00-I018.AUD` → ts_aud_decode.py → `ffmpeg -ac 2 -ar 44077 -c:a adpcm_ms`
  (default align 1024 IS accepted on the EVA channel) → loose novel name →
  localized event repoint. Proven on the localized/EVA channel; nonlocalized
  weapon-SFX expected identical (its old failure was the PCM confound) —
  one-shot confirm when the next weapon sound ships. Probe
  side-lesson: never probe audio via the launcher-fired credit tick (any loose
  override silences it — bad vehicle).
  Used so far: `BONUS_UNLOCK` (hover missile), `DINOATK1` (railgun),
  `DINODIE1` (Mk. II tusks), `DINOMOUT` (Titan 120mm), `DINOYES` (dropship
  landing DROPDWN1), `STRUGGLE` (dropship takeoff DROPUP1).
  ⚠ **The override WAV must be MS-ADPCM (fmt tag 2, like every TD?_SFX_ host
  sample), NOT plain PCM.** A PCM (tag 1) override CRASHES ClientG with an
  integer divide-by-zero in its audio path (deterministic, ClientG+0xAB5E69;
  two live crashes 2026-08-13, `RAR_SFX_DROPUP1` on the crash stack) — the
  client runs ADPCM block math against the file's header. Encode with
  `ffmpeg -c:a adpcm_ms -ar 22050 -ac 1`. One host per sound;
  prefer clearly TD-gameplay names over generic UI-ish ones (BUTTON, BLEEP)
  as extra insurance. Census one-liner lives in the git history of this doc.
