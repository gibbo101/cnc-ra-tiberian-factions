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

## 4. New anim TYPES are launcher-dead; delayed anims are suspect

The launcher resolves anim-type objects against its own tables — a DLL-added
`AnimType` (ANIM_RAILFX) renders the white placeholder regardless of tileset
registration, and repointing a vanilla anim's tiles (TWINKLE2) at custom art
didn't take either. How mod-shipped anims DO reach launcher art (TDIONSFX
manages it — base-MEG-referenced frames?) is still unsolved; audit before
relying on any custom anim's visual. Also avoid the `AnimClass` ctor's
`timedelay` param — vanilla never uses it and delayed anims export in a
pre-start state.

**Rule:** for guaranteed-visible effects, spawn stock anims (the railgun helix
uses `ANIM_PIFFPIFF`). Custom-art anims need the TDIONSFX mechanism understood
first.

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
- **Audio policy (Luke, 2026-07-20): every TS unit ships its AUTHENTIC TS
  sounds** — weapon reports, and eventually voices — via the dormant-sample
  recipe (`td-audio-routing-recipe.md` + the HOVRMIS1 trap notes).
- **Dormant-sample audio hosts — 176 slots available** (censused 2026-07-20:
  221 TD-side samples in SFX3D.MEG, 47 referenced by RA-side events = in use).
  Rule: a TD?_SFX_* sample is a valid host iff no RAC_/RAR_ event in our
  shipped SFXEVENTSNONLOCALIZED.XML references it — TDC_/TDR_-named events
  only fire in TD game context, never in our mod. New sample names are
  IMPOSSIBLE (novel names crash ClientG); overriding is the only channel.
  Used so far: `BONUS_UNLOCK` (hover missile), `DINOATK1` (railgun),
  `DINODIE1` (Mk. II tusks), `DINOMOUT` (Titan 120mm). One host per sound;
  prefer clearly TD-gameplay names over generic UI-ish ones (BUTTON, BLEEP)
  as extra insurance. Census one-liner lives in the git history of this doc.
