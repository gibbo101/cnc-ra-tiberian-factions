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

**Rule:** custom-art anims are viable. Keep every spawn a full cell clear of any
object's own cell, or it exports as a sub-object and draws the white box.

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
  TSHARV (yaw0 0 + wave face_fix, scale 0.85), TSAPC (yaw0 0 + face_fix),
  TSSONIC + SONICTUR (yaw0 90, no reorder — its wave line applies NO face_fix), TSMCV (yaw0 90, no reorder),
  TSHVR + HVRTUR (yaw0 90, no reorder). Aircraft: DSHP dropship
  `--yaw0 180 --elev 32 --canvas 656 --px-per-voxel 6.4`. VXLs
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
  marked dormant). New sample names are IMPOSSIBLE (novel names crash
  ClientG); overriding is the only channel.
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
