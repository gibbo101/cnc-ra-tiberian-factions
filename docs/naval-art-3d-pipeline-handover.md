# Naval unit art — 3D-render pipeline + turret plan (SESSION HANDOVER 2026-06-22)

> **⛔ OUTCOME 2026-06-22: the 3D TD Gunboat (`VESSEL_TDGUNBOAT`) is SHELVED — non-buildable
> (`rules.ini [TDBOAT] TechLevel=-1`), turret code backed out of `vessel.cpp`/`vdata.cpp`,
> `IsTurretEquipped=false`. Engine type left DORMANT (removing the enum slot would renumber the
> other instances' TDPT/TDDD/TDCA/TDOBLISUB). Orphan `TDBOATTUR` XML tiles + ZIP left in place
> (don't re-edit RA_UNITS.XML — concurrent edits wiped it once this session). GDI's gunboat role is
> covered by the parallel TDPT (PT-clone) unit instead.**
>
> **Why it died (all real tool limits, documented so we don't re-chase):**
> 1. *Spinning turret seating* — solvable but fiddly: `Turret_Adjust` distance needs in-game
>    calibration (HD draw scales NMP ~4 screen-px/unit; the hull art was also 180° reversed so the
>    turret needed `dir+DIR_S`). Was ~1 nudge from seated (dist 15→26) when interrupted.
> 2. *OG TD turret won't extract cleanly* — the 192-frame sprite has the gun FUSED to the hull; the
>    base is static (reads as hull to a median) so background-subtraction only isolates the swinging
>    barrel, plus it's low-res 2D that clashes with the HD 3D hull.
> 3. *All-direction HD art* — image-gen (ChatGPT) makes nice boats but CANNOT hold precise even
>    rotations (got clustered angles, no clean south/diagonals); 2D-rotating a 3/4 sprite "lists"
>    (dead end); Tripo gives precise angles but "toy" geometry Luke disliked. Untried next step if
>    revived: TRELLIS / Hunyuan3D-2 (often less toy than Tripo) on a clean ChatGPT boat view.
> Revive only with a proper dedicated 3D GUN model (precise angles) on a nicer hull GLB.

**⭐ RESUME HERE for the GDI Gunboat (and Hovercraft) art.** Where we got to and the two
options to play with next session.

## The problem (settled facts)
- **TD gunboat (`TDBOAT`) only has EAST/WEST hull art.** Canonical — it moved on rails horizontally
  in TD, no other-direction sprites exist. Confirmed: wiki + TD source (`UNIT_GUNBOAT` IsChunkyShape)
  + the 192-frame sheet = 2 hulls × 3 damage × 32 *gun* facings (the 32 are the gun, not the hull).
- **Rotating the E/W sprite to fake facings → "listing".** The sprite is a 3/4 perspective view;
  2D-rotating spins the perspective, so non-E/W headings look tilted. Proven in-game. Dead end.
- **No mod anywhere adds a full-facing GDI gunboat** (checked 99 local Workshop mods, OpenRA, web).
- **RA vessels render as HULL + SEPARATE TURRET.** PT/DD/CA each have a 16-facing hull sprite + an
  independent rotating turret overlay (`vessel.cpp` Draw_It cases: PT→MGUN, DD→SSAM, CA→TURR). This
  is the clean path: native per-facing hull + bolt on our own turret.

## What's DEPLOYED right now
The gunboat currently in-game = **3D-rendered TD-gunboat hull, 16 facings, gun baked-in, NO spinning
turret** (`IsTurretEquipped=false`, `VesselClass::Shape_Number` returns `Dir_To_16` for it).
Luke's verdict: "ok, but the turret won't spin and missiles don't come from it." So the turret is the
open item. (Earlier rotation-synthesis attempt is superseded; the 3D render replaced it.)

## ⭐ TDGUNBOAT TURRET SPLIT — IMPLEMENTED 2026-06-22 (built green; NOT yet deployed/calibrated)
Done the BEST way (keeps the TD silhouette AND gives a spinning, target-tracking gun): the gun was
**split off the 3D hull** as its own 32-facing turret. The gun was located definitively — it's the
forward mass at **model Y +0.13..+0.30**, ahead of the green bridge (NOT the green block; that mislabel
burned the earlier band-scans). Key tool = `scripts/gunboat_ymap.py` (Y-gradient colour map; also
`gunboat_profile.py`, `gunboat_views.py`).
- **Art (new files, conflict-free):** `scripts/render_gunboat_split.py` (`body`/`turret` modes,
  `BOW_DEG=0 PITCH=0` validated vs deployed). `TDBOAT.ZIP` re-packed (16, gun removed,
  `pack_render_to_tileset.py … 258 280`) + new `TDBOATTUR.ZIP` (32, turret, new
  `pack_turret_to_tileset.py … 0.652 280` — turret uses the BODY's 0.652 scale so it overlays at the
  right size). Offline overlay (`/tmp/v_overlay2.png`) seats it on the foredeck across facings.
- **XML:** `TDBOATTUR` tileset (32 tiles) added to `RA_UNITS.XML` after the TDBOAT block (well-formed).
- **Engine:** `vdata.cpp` ctor `IsTurretEquipped` false→**true**; new `Turret_Adjust` `case
  VESSEL_TDGUNBOAT` (`Normal_Move_Point(dir, 30)` = **STARTING estimate, TUNE in-game**; raise = toward
  bow; lands at stern → flip `dir`→`dir+DIR_S`). `vessel.cpp Draw_It`: removed the TDGUNBOAT turret-skip
  + added `case VESSEL_TDGUNBOAT` (`turret_shape_name="TDBOATTUR"`, donor `Get_Image_Data()`,
  `shapenum=Dir_To_32(SecondaryFacing)` DIRECT index).
- **PENDING:** (1) deploy (the shared tree also held the Allied-boat-turret + Nod-Obelisk-sub WIP — my
  DLL already compiles all three in). (2) **in-game calibrate `Turret_Adjust` 30** via the desktop
  scrot+xdotool loop ([[reference-desktop-screen-control]]). (3) team-colour pass (still Tripo green).

## The 3D pipeline (WORKS — reuse for hovercraft)
1. **Image→3D**: feed a clean hull view to a free HF Space — **TRELLIS** (huggingface.co/spaces/microsoft/TRELLIS)
   or **Hunyuan3D-2** — download GLB. (Tripo/Meshy gate the *download* behind paywalls; the gunboat
   GLB we have came from Tripo after downgrading. It's at `~/Desktop/toy boat 3d model.glb`.)
   Input images prepped at `~/Desktop/gunboat-3d-input/` (east/west, transparent + white-bg).
2. **Render**: portable Blender at **`~/blender-portable/blender`** (4.2.21 LTS, no sudo).
   `scripts/render_gunboat_facings.py <glb> <outdir> [bow_deg] [pitch] [scale]` — orthographic camera
   at **54° elevation** (measured from the DD's foreshortening; this matches every other RA unit),
   spins the model for 16 facings, transparent PNGs. Calibration knobs in the script header.
3. **Package**: `scripts/pack_render_to_tileset.py <renderdir> <ININAME> <target_len_px> <canvas> <out.zip>`
   — scales so the east hull = target px (gunboat used 258), centres on a square canvas, writes
   `<name>-NNNN.tga` + `.meta` into the ZIP. Tileset already trimmed to 16 shapes in RA_UNITS.XML.
4. **Deploy**: build (or just `cp` the ZIP into build output) → rsync to the Linux prefix.

## ⭐⭐ NEXT SESSION PLAN — LOCKED 2026-06-22 (do these, in order)

> **STATUS 2026-06-22: item 1 DONE + built + deployed to the local Linux prefix.**
> `VESSEL_TDPT/TDDD/TDCA` added — fully-separated clones of RA PT/DD/CA, `Owner=GoodGuy`,
> `Prerequisite=syrd` (→TDGYARD remap), TechLevels 5/7/10, `IsTurretEquipped=true` so each draws
> its native spinning turret (TDPT→MGUN, TDDD→SSAM, TDCA→TURR — the turret art is GLOBAL, drawn by
> name in Draw_It, NOT in the hull ZIP). Own hull art cloned from the base PT/DD/CA ZIPs via
> `scripts/clone_vessel_art.py` (extract base ZIP from TEXTURES_RA_SRGB.MEG → rename inner frames →
> repack as loose TDPT/TDDD/TDCA.ZIP + 16 tileset blocks each appended to RA_UNITS.XML). Buildables
> entries (RA_TDPT/TDDD/TDCA, RA cameos) in RABUILDABLES.XML. Touch points: `defines.h` enum,
> `vdata.cpp` (ctors+Init_Heap+One_Time donor guards), `vessel.cpp` (Draw_It turret switch +
> Fire_Data/Fire_Coord PT/CA cases + CA threat/ACTION_NOMOVE filters), `rules.ini` [TDPT/TDDD/TDCA],
> RABUILDABLES.XML. UNCOMMITTED. The TD baked-gun gunboat (TDBOAT/VESSEL_TDGUNBOAT) is left
> untouched (item 3, parallel instance). **NEXT = in-game verify the 3 hulls render with spinning
> turrets, then iterate item 2 (turret swaps).** TDCA high-tech prereq (atek-equiv) is a TODO.

**1. Add ALL 3 Allied ships to the GDI roster as FULLY-SEPARATED CLONES.**
   New vessel types cloning PT (gunboat), DD (destroyer), CA (cruiser) — e.g. `VESSEL_TDPT` /
   `VESSEL_TDDD` / `VESSEL_TDCA`. Follow the existing vessel-port pattern (same as VESSEL_TDGUNBOAT/
   TDNSUB): own enum slot (defines.h) + `vdata.cpp` ctor templating the RA equivalent (KEEP
   `IsTurretEquipped=true` + the right turret) + Init_Heap append + One_Time donor (VESSEL_PT/DD/CA
   NULL-guard). **Own COPIED art** — clone PT/DD/CA `.ZIP` → `TD*`-named ZIPs + clone their tilesets
   in RA_UNITS.XML (keep hull frames 0-31 + turret frames; the turret draws via the engine's existing
   PT/DD/CA Draw_It cases). `rules.ini` Owner=GoodGuy, Prereq → STRUCT_TDGYARD (GDI Shipyard). These
   give native per-facing hulls + native spinning turrets out of the box (the green = house-colour →
   GDI). This REPLACES the broken rotation/3D-bake gunboat as the GDI surface fleet.

**2. Test each TURRET 1-by-1.** Swap turret art onto a chosen hull, build, deploy, eyeball. Catalogue
   on `~/Desktop/turret-options/`: naval MGUN/SSAM/TURR; tank turrets (Med/Heavy/Mammoth/Light);
   TD MLRS rocket-rack; Nod SSM box; Nuke Tank dual-cannon. Turret swap = repoint the vessel's turret
   tileset + offset (Draw_It turret case). Pick the best per ship.

**3. Re-open the 3D TD gunboat to REMOVE its turret** (the alternative hull, keeps the TD silhouette).
   The gun is welded into the AI mesh; a turret mounted over the spot hides the hole (+ optional flat
   deck patch). Use the band-scan harness `scripts/gunboat_band_scan.py` (renders the model with raised geometry
   deleted in 4 different Y-bands → identify which band IS the gun; earlier attempts wrongly deleted
   the +Y bridge and a mid trench). Once the gun band is found: delete it, patch the hole, re-render
   16 hull facings via `render_gunboat_facings.py`, then it can host a turret like the cloned ships.

**4. Names + cameos for ALL of the above** via the NEW `Data/ModText.csv` mechanism (see
   `faction-select-identity.md` correction) + LOOSE `BuildIcon_*.tga` cameos (render a hero frame per
   ship from a 3D model / the hull art). Real names at last: "GDI Naval Yard" etc. already work on-map;
   ModText.csv makes them work on the SIDEBAR too.

Turret wiring (shared): hull tileset + turret tileset + turret offset, `IsTurretEquipped=true`,
Draw_It case → spins + fires from the barrel (the PT/DD/CA cases already exist; clones reuse them).

## Turret catalogue (all on `~/Desktop/turret-options/`)
- **Naval (clean, no base):** RA_MGUN (PT MG), RA_SSAM (DD missile box), RA_TURR (CA gun). Best fits.
- **Vehicle turrets (15, extracted):** RA/TD Medium/Heavy/Mammoth/Light tank turrets (proper naval-gun
  look), TD **SSM Launcher** (missile box — great for the Tomahawk), Ranger/Hum-vee/Buggy MGs, Tesla.
  Extraction rule: turret = unit frames **32–63** (`<name>-0032.tga`…`-0063.tga`, or two-index
  `-0032-0000` when the unit has a firing anim e.g. 3TNK/4TNK). Body = frames 0–31.
- **Ground turrets (RA/TD GUN, AGUN, SAM, FTUR):** sit on a concrete base — NOT boat-usable as-is.
- Reference hull sprites on Desktop: `ra-ptboat-sprites/`, `ra-destroyer-sprites/`, `ra-cruiser-sprites/`.

## Hovercraft (TDLST) — same treatment queued
- No TD hovercraft cameo ever existed (unbuildable in TD); currently borrows `BuildIcon_RA_Transport`
  (a hovercraft icon, resolves fine, but not unique). Custom cameo = render one hero frame from a 3D
  model (nearly free once we have the model).
- Plan: same image→3D→render-16-facings→package pipeline. Hovercraft has no turret (simpler).

## Key numbers / gotchas
- Render camera: **54° elevation** (36° from top-down). DD foreshortening ratio 0.81 = sin(54°).
- Gunboat scale: east hull = **258 px**, canvas 280.
- `TechnoClass::BodyShape[32]` = {0,31,30,29,...} — facing→frame remap.
- House-colour: the **green** region in RA/TD sprites is the team-colour remap zone; our render's green
  (Tripo) lines up with that, but a from-scratch render needs the team area flagged. NOT yet handled
  for the 3D gunboat (it currently shows render colours — team-colour pass is a TODO).
- Custom sidebar NAMES + CAMEOS: use loose **`Data/ModText.csv`** (names) + loose `BuildIcon_*.tga`
  (cameos) — the official data-only path, proven by the Nuke Tank Sample Mod. (Earlier ".LOC is
  impossible" was the wrong tool; corrected in `faction-select-identity.md` 2026-06-22.)
