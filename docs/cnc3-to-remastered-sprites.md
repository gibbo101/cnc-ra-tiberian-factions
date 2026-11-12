# C&C3 units to C&C Remastered sprites: a working recipe

**Status:** Reference. Pulling a C&C3 unit into HD Remastered sprites, as done for GDI's Mammoth
Mk. III, Predator, Pitbull, Guardian APC, Rig (with its Battle Base and the deploy between them), Juggernaut, Orca,
Firehawk, V-35 Ox and every Tiberium Wars infantryman, and Nod's Scorpion, Flame Tank, Stealth Tank, Beam Cannon,
Raider Buggy, Attack Bike, Avatar, Venom, Vertigo, Carryall, every Tiberium Wars infantryman and Kane's Wrath's
Militant and Cyborg.

How to pull a unit out of Command & Conquer 3: Tiberium Wars (models, textures, audio,
stats) and turn it into HD sprites for a C&C Remastered Collection mod. Written for an AI
coding agent to follow. Every fact here was verified on the GDI Mammoth Tank and Predator
Tank (Steam release, patch 1.9) and the Scorpion Tank, except where a line says it is unverified. No
external modding tools are needed: Python 3 with numpy and Pillow, plus ffmpeg for audio.

**Legal:** EA's assets come from your own install. Ship them in your mod on the same terms as
any other EA-derived art; never publish the extracted files on their own.

---

## 1. Where things live

In the C&C3 install:

| Archive | What you need from it |
|---|---|
| `Core/1.0/StaticStream.big` | the `static_common` stream: every model, texture and GameObject (unit stats) |
| `Core/1.5/patch5.big`, `Core/1.6/patch6.big`, `Core/1.7/patch7.big`, `Core/1.9/patch9.big` | `static_common_5`, `_6`, `_7`, `_9`: patch overrides (see TRAP 1b) |
| `Core/1.0/GlobalStream.big` | `global_common`: sound effect payloads |
| `EnglishAudio/1.0/EnglishAudio.big` | `global_english`: unit voice payloads |

Kane's Wrath is its own install (Steam app 24810) with the same layout: `Core/1.0/StaticStream.big` patched by
`Core/1.1/patch1.big` and `Core/1.2/patch2.big` (`static_common_1`, `_2`), and its audio chained the same way.
It adds its own units (the Cyborg, `NUSILENT`) and remakes some of Tiberium Wars' under the same asset names: its
Militant (`NUMILTNB_SKN`) has a new mesh and texture, so take a unit from the game whose version you want.

There are no W3X or DDS files on disk. EA's asset builder compiled everything into binary
"asset streams" packed inside the `.big` archives. (Audio has patch streams too, in
`Core/1.5`, `Core/1.7`, `EnglishAudio/1.5` and `EnglishAudio/1.7`: see Audio in section 5.)

## 2. Reading the archives

**BIG:** magic `BIGF` or `BIG4`, u32 LE total size, then **big-endian** u32 entry count and
u32 header length; entries are `{u32 BE offset, u32 BE size, NUL-terminated name}`.

**RefPack compression:** payloads starting with a byte pair where `data[1] == 0xFB` and
`(data[0] & 0x3E) == 0x10` are RefPack. Header u16 BE: flag `0x8000` = 4-byte size fields
(else 3), flag `0x0100` = a compressed-size field follows first (skip it). Then the
uncompressed size, then the standard RefPack opcodes. The whole 155 MB `static_common.bin`
is ONE RefPack stream (it decompresses to about 289 MB). A pure-Python decoder with a
slice-copy fast path does it in about 7 seconds; cache the result.

**Stream files** inside each BIG: `data\<stream>.manifest`, `.bin` (instance data),
`.relo`, `.imp`, and `data\<stream>\cdata\*.cdata` (bulk payloads such as audio).

**Stream cache:** the tools read each stream from `<stem>.assets.pkl` (the parsed manifest's asset list) and
`<stem>.bin` (the decompressed instance data) in one folder. Build them once per stream with
`assets, bin, relo, imp = manifest.load_stream(big_path, stem)` (`tools/cnc3/manifest.py`), pickling `assets` and
writing `bin` out; it takes about 7 s for `static_common`.

## 3. The manifest (version 5)

48-byte header of 12 u32 LE:
`flags, checksum, allTypesHash, assetCount, totalInstanceDataSize, maxInstanceChunkSize,
maxRelocationChunkSize, maxImportsChunkSize, assetReferenceBufferSize,
referencedManifestNameBufferSize, assetNameBufferSize, sourceFileNameBufferSize`.

Then `assetCount` entries of 11 u32 (44 bytes):
`typeId, instanceId, typeHash, instanceHash, assetRefOffset, assetRefCount, nameOffset,
sourceFileNameOffset, instanceDataSize, relocationDataSize, importsDataSize`.

Then the asset-reference buffer (pairs of `(typeId, instanceId)`), the referenced-manifest
names, the name buffer (`Type:InstanceName` C strings, e.g. `W3DMesh:GUPREDTANK_SKN.TURRET`)
and the source-file buffer. Instance data is packed into the `.bin` **in entry order**.

> **TRAP 1: the +4 rule.** The decompressed `.bin` starts with a 4-byte stream header (the
> manifest's `checksum` value), so its length is `totalInstanceDataSize + 4`.
> Asset N starts at `4 + sum(instanceDataSize of assets 0..N-1)`, and pointers inside an
> asset are offsets from that asset's true start. Get this wrong by 4 and every struct looks
> almost right, with the last field of each asset truncated.

> **TRAP 1b: patches are a chain, not one overlay.** A patch manifest lists every asset but
> carries instance data only for the ones it changed (`instanceDataSize` 0 otherwise). Each
> one names the stream it patches in its referenced-manifest buffer (the entry with a `0x02`
> first byte). For 1.9 the chain is `static_common_9` -> `_7` -> `_6` -> `_5` ->
> `static_common`: take each asset from the first stream in that order that has data.
> Reading only `_9` and falling back to 1.0 gets stale data: `GDIPredator` and all the tank
> weapons were changed in `_5`/`_7`, not `_9`, and `GDIMammothTankMissileFragmentWarhead`
> does 400 damage in 1.0 but 300 from patch 5 on.

## 4. Finding a unit's parts

Search asset names case-insensitively for the model prefix (the Predator is `GUPREDTANK`,
the Mammoth `GUMAMM`):

- `W3DHierarchy:<P>_SKL`: the skeleton.
- `W3DContainer:<P>_SKN`: which sub-mesh hangs off which bone.
- `W3DMesh:<P>_SKN.<PART>`: the sub-meshes (hull, turret, barrel, tread variants, muzzle
  flashes, `UGRAIL_*` railgun upgrade).
- The wreck and debris pieces: `GUMAMM_R.*` and `GUMAMM_R01..R05` for the Mammoth,
  `GUPREDTANKR.*` and `GUPREDTANKR01..R05` for the Predator (the underscore varies).
- `Texture:<name>`: diffuse, `D` = damaged diffuse, `_NRM`/`_Nrm` = normal map, `_SPM` =
  spec, `HC_<name>` = house-colour mask (GDI only, see House colour), plus a separate tread texture. `_K` variants also
  exist (unused here; purpose not checked).
- `GameObject:GDIMammoth`, `GameObject:GDIPredator`: the unit's gameplay object. Internal names can differ
  from the unit's: the Scorpion is `GameObject:NODRaiderTank` (from patch 7), model `NURADR` (meshes under
  `NURADR_SKN`), while `NODScorpionBuggy` is the Raider Buggy. Containers are not always `_SKN`: the Flame
  Tank's is `NUFLAMETANK` (skeleton `NUFLAMETANK_SKL`) and the Rig's `GURIG` (skeleton `GURIG`). The others:
  Stealth Tank `NUSTLTHTNK_SKN`, Beam Cannon `NUBEAM_SKN`, Pitbull `GUPITBULL_SKN`, Guardian APC `GUAPC_SKN`,
  Raider Buggy `NU_BUGGY_SKN`, Attack Bike `NUATKBIKE_SKN`, Juggernaut `GUJUGG_SKN`, Avatar `NUMECH_SKN`.
- `PackedTextureImage` portraits are named loosely (`Portrait_GDISniperTeam`, `PORTRAIT_NODSaboteur`,
  `Portrait_NODMilitantMissile` for the Rocket Militant): search them case-insensitively.
- A squad's soldiers are not asset references. Each payload entry in the squad's GameObject holds the soldier
  GameObject's instance ID (the manifest's `instanceId`) then a u32 count, and some squads carry two entries:
  Riflemen 3 + 3, Militants 4 + 5, Grenadiers 2 + 2, Fanatics 1 + 4, Black Hand 3 + 3, Shadows 2 + 2; Missile
  Soldiers 2, Zone Troopers 4, Rocket Militants 2, the Sniper 1. Patches 5 to 9 leave these unchanged.
- Every unit's construct command (`LogicCommand:Command_Construct<GameObject>`) references its GameObject: the
  quickest roster of what a side can build.
- `PackedTextureImage:PORTRAIT_GDIPredatorTank` / `Portrait_GDIMammothTank`: the sidebar
  portrait. Its asset reference is a `Texture:PackedImages_NNN` and its data holds the pixel
  rectangle (for both tanks `0, 0, 128, 128`, the whole texture).

The manifest's asset references are the cheapest way to follow links: a mesh's references
list its textures, a weapon's list its warhead, a container's list its skeleton and meshes.

## 5. Decoding each asset type

### Textures
Instance data = a 12-byte header `{u32 0, u32 12 (offset of the DDS), u32 DDS length}`,
then a **complete DDS file** (DXT1/DXT5). Pillow opens it directly.

### Skeleton (W3DHierarchy)
u32 pivot count at +0x04; pivot records at +0x14, stride 104:
`{i32 parent, float3 translation, float4 quaternion xyzw, float[12], 16 bytes,
u32 nameLength, u32 namePtr}`. The float[12] is NOT the pivot transform (it holds
scale-like diagonals such as 1.25 and 0.582); the tools ignore it and use only the
translation and quaternion. World transforms accumulate down the parent chain
(`world_t = parent_t + rotate(parent_q, t)`, `world_q = parent_q * q`).

> **TRAP 2: names are shifted by one.** The name stored in record i belongs to pivot i+1.
> Pivot 0 is the unnamed root. Transforms are at the right index; only the names slide.

### Container (W3DContainer)
u32 count at +0x08; records at +0x10, stride 16: `{u32 pivotIndex, u32 nameLength,
u32 namePtr, u32 index}`, mapping sub-mesh name to the pivot it is bound to.

### Mesh (W3DMesh)
- Header: u32 at +0x04 = offset of the geometry trailer (below); floats at +0x0c = bounding
  box min3, max3 (a free check on your decode: it matches the decoded positions exactly).
- Triangles: records at +0x60, stride 24: `{u32 3, ptr -> u32[3] indices, 16 bytes}`. The
  trailing 16 bytes are not a usable face normal; ignore them. The array ends where record 0's
  index triple starts (`ptr == 0x60 + 24*count`). `w3dmesh.py` reads the same records from
  +0x5c with a dummy leading field; it only uses the pointer. Apply the end rule, not a scan for
  `3` markers: the Scorpion's `GUN_UPGRADE` has 54 triangles, and a scan reads a 55th whose
  indices (4092 on a 74-vertex mesh) are garbage.
- Geometry trailer: 7 u32s `{vertexCount, stride, vbPtr, declBytes, declPtr, boneCount,
  bonePtr}` with `vbPtr + vertexCount*stride == declPtr`, `declPtr + declBytes == bonePtr`,
  and the declaration ending in the D3D `0xFF` terminator element. `w3dmesh.py` finds it by
  scanning for that pattern; in every tank mesh checked the scan agrees with the +0x04 offset.
- The declaration is a `D3DVERTEXELEMENT9[]` (`{u16 stream, u16 offset, u8 type, u8 method,
  u8 usage, u8 usageIndex}`); usage 0 POSITION, 1 BLENDWEIGHT, 2 BLENDINDICES, 3 NORMAL,
  5 TEXCOORD, 6 TANGENT, 7 BINORMAL, 10 COLOR; type 1 FLOAT2, 2 FLOAT3, 4 (D3DCOLOR in the
  D3D9 enum: 4 bytes, read raw).
- `bonePtr` holds a u16 remap list: byte 0 of a vertex's `BLENDINDICES` indexes it to get a
  pivot.
- **Vertices are local to their pivot.** Model space = `pivot_world_q * v + pivot_world_t`.
  Skinned meshes (with BLENDINDICES) pick the pivot per vertex; meshes without bones take
  the pivot from the container. The Mammoth hull is two-bone skinned (POSITION/NORMAL at
  usage index 0 and 1, plus BLENDWEIGHT); using index 0 with bone byte 0 is exact for all
  but about 0.2% of its vertices.
- The FX parameter block names the shader (`ObjectsGDI.fx` for bodies, `DefaultW3D.fx` for
  treads, `MuzzleFlash.fx`, `ObjectsNOD.fx` for `UGRAIL_*`). Texture names are not strings in
  the mesh: they are the mesh's manifest asset references, in the order diffuse, normal,
  spec, house-colour mask for bodies, and the tread texture for tread meshes.

> **TRAP 3: textures are per mesh.** The tread belts UV into their own tread texture. Painting
> them with the hull diffuse gives pale garbage stripes that are worst at the north facing.
> A body mesh can use another unit's sheet too: the Pitbull's spotlight and Mortar tube are painted on
> the Rig's (`GURig`, `HC_GURig`), the Raider Buggy's and Attack Bike's riders on the Militant's (`NUMiltnB`), the
> Avatar's commandeered beam cannon and flamethrower on the Beam Cannon's and Flame Tank's. The extractor tags such
> a mesh sheet n, and the renderer draws it from `body<n+1>`, `house<n+1>` and `normal<n+1>`, each sheet with its
> own house-colour level.

> The railgun-upgrade meshes (`UGRAIL_*`) decode with the same code (their bounding boxes
> match) but use `ObjectsNOD.fx` with a scrolling mask texture; they were never rendered.

### Hull and turret split
Tag each vertex by its pivot's ancestry: anything under the turret bone (`BONE_TURRET` on
the Mammoth, `TURRET` on the Predator, which includes the barrels, pods and muzzle bones) is
turret; tread meshes are treads; everything else is hull. The turret pivot is NOT always at
the hull centre (the Predator's is 4.2 C&C3 units aft of it, the Mammoth's 3.1 forward), so
keep its position: you need it to seat the turret sprite per hull facing. The Scorpion's
`NEWSKIN` mesh is skinned to `BONE_CHASSIS`, `BONE_TAIL` and `BONE_TURRET`: its whole upper body
is the turret, seated 7.8 units ahead of the hull centre.

**Upgrades** show and hide meshes; read which in the GameObject's model conditions
(`CurDrawableShowSubObject` / `CurDrawableHideSubObject` strings). A mesh's pivot decides which
part it joins:
- the railgun (`UGRAIL_*`) hides nothing and adds turret meshes;
- Laser Capacitors (`Upgrade_NODTechCenterLaserCapacitor`) hide `GUN` and show `GUN_UPGRADE`, `TURRET2`
  and `TURRET2_GUN`: a second turret on a tail mount, firing from `TurretMS` (the cannon fires from
  `TurretFX`). The engine draws one turret, and turret 0 has no weapon once the cannon is hidden, so the
  upper body is drawn fixed facing forward with the hull and `TURRET2` is the turret, seated 14.4 units aft;
- Dozer Blades show `DOZERBLADE`, bound to `BONE_TURRET`, so it turns with the upper body; on the laser
  tank it rides the fixed body.

- the Pitbull's Mortar (`Upgrade_GDIArmoryPitbullMortar`, at the Armory) shows `MORTORTUBE`, bound to its own
  pivot off the root, so it rides the hull, not the rocket pod.

The Flame Tank, Stealth Tank, Beam Cannon, Guardian APC, Rig and Attack Bike have no Tiberium Wars upgrade (the
Flame Tank's Purifying Flame is Kane's Wrath). The Raider Buggy's EMP coil (`Upgrade_NODEmpBurst`) shows `EMP`,
on its own pivot off the chassis: a hull fixture. Its Laser Capacitors change only the weapon.

Hull-mounted upgrade pieces (the fixed body, the tail mount, the blade on the laser tank, the Mortar tube) are
"fixtures": drawn with the hull but kept out of the hull's footprint, so every variant keeps its base
tank's hull centre and seat origin (`c3_render.py` part 3).

### Treads
C&C3 swaps whole tread meshes by state (`TREADSSTOP`, `TREADSMOVE`, `TREADSLEFT`,
`TREADSRIGHT`, plus `TREADSBACK` on the Mammoth only: same geometry, different UVs; the
Mammoth's LEFT/RIGHT also reorder the vertices). The scrolling itself is in the shader
(`DefaultW3D.fx` with `TexCoordTransform` parameters). For sprites, take the `TREADSSTOP`
mesh and scroll its U coordinate yourself:
- Belt direction: on the top run of the belt (vertices in the top tenth of the tread's
  height range), take the median dU/dx over edges joining two top-run vertices (x = forward,
  in model space). Driving forwards, a track's top run travels FORWARDS relative to the hull
  (its ground run is the part standing still on the ground), so scroll U by -sign as the
  tread step rises: that moves the top run towards the nose.
- Link pitch: autocorrelate the tread texture's column profile (mean luminance per column).

> **TRAP 4: take the FIRST strong autocorrelation peak.** Two links correlate as well as one.
> A step sized off the double pitch moves 2/3 of a link, and the eye reads it as the belt
> rolling the wrong way. (Mammoth: 43 px of 256, not 85, which scores slightly higher. Predator:
> 14 px.) The code searches from lag 4 and takes the first local maximum above 0.8 x the
> best peak.

### Animations (W3DAnimation)
`tools/cnc3/w3danim.py` (workspace) decodes them; its docstring holds the layout. Header: frame count at +0x08,
frames per second at +0x0c, channel count at +0x10, pointer to the channel pointers at +0x14. Each channel is
`{typeHash, kind, ...}`: kinds 0-2 translate X, Y, Z, 3 is a quaternion, 4 visibility, and the channel names its
pivot by W3DHierarchy index (TRAP 2's name shift does not apply). Two encodings: time-coded keys (hash
`0x60d8cf69`, floats then u16 frame times, interpolate linearly) and adaptive delta (hash `0x77f97305`, an initial
vector then 16-frame blocks of 4- or 8-bit deltas scaled by W3D's filter table, low nibble first). Channels hold
offsets from the bind pose: `world = parent * bind * T(anim) * R(anim)`, so frame 0 is the bind pose.

> **TRAP 5: a clip can hold several cycles.** The Rifleman's 73-frame run is three strides. Sampling six poses
> across the clip lands on two poses that alternate; find the period (the first frame whose pose returns near
> frame 0's) and sample that.

> **TRAP 6: a dropped weapon stretches.** An infantryman's gun hangs on a `PROPS` pivot that falls away in the
> death clips, but some of its vertices are bound to the hand, so its triangles stretch from the floor to the hand.
> Bind each connected piece that is mostly on a `PROPS` pivot wholly to it (`tools/cnc3/c3_extract_infantry.py`,
> workspace).

### House colour
The `HC_*` texture's **alpha** is the recolour mask (about 5% of the sheet). Its RGB is not
the colour. See step 7 for how to paint it for Remastered.

Nod units have no `HC_` texture. Their meshes use `ObjectsNOD.fx`, and the house mask is the
spec map's **blue** channel, which covers exactly the red markings on the diffuse
(`c3_extract_model.py` `house_from_spec`). In C&C3 those strips glow: the shader adds spec blue x a
scrolling mask x house colour x 3 as light. Painted by step 7's formula alone they read dim on the
Scorpion's dark panels (median G 96, luminance 64, under the target below).
A mask that sits part way (the Attack Bike's fairing at spec blue 93) blends the house green half into red and reads
orange; C&C3's x 3 glow paints it fully, so that model raises its mask (`house_gain`). The Rocket Militant's robe
trims are the same case in an `HC_` mask.

### Audio
`.cdata` audio is EA SNR/SNS (EA-XAS ADPCM). **ffmpeg has a built-in demuxer for exactly
this** (`ea_cdata`): save the payload with a `.cdata` extension and run
`ffmpeg -i x.cdata out.wav`. The result is 16-bit PCM at the source rate (the Mammoth voice
lines are 48 kHz mono). Filenames are
`data\<stream>\cdata\<typeId:08x>.<typeHash:08x>.<instanceId:08x>.<instanceHash:08x>.cdata`.
Resolve `AudioEvent` asset references (`(typeId, instanceId)` pairs) to `AudioFile` assets,
then to their cdata. The English stream repeats every non-localised `AudioFile` as a stub
(0 bytes of instance data, no cdata file): resolve against every stream and take the first
one whose cdata actually exists. Voices come from `global_english`, weapon sounds from
`global_common`. Takes are shared across units: the Pitbull's rockets fire `GUGuard_wea1fire*`, its rocket and
Mortar hits are both `NBBrown_wea1expl*`, and some select events mix in a create line (the APC's and Rig's
`VoiCreatea`). The audio patches (`Core/1.5`, `Core/1.7`, `EnglishAudio/1.5`, `EnglishAudio/1.7`) form a
chain like the static ones, but `global_common_5` holds a 548-byte, 19 ms placeholder for every unit
voice, so skip payloads that small and take the 1.0 English take. `tools/cnc3/c3_extract_audio.py`
(workspace) does all of this from AudioEvent names.

Follow a unit's sounds through its assets' references: the GameObject's references name its voice
events (`AudioEvent:NOD_ScorpionTank_VoiceSelect`, `...VoiceMove`, `...VoiceAttack`), and each
weapon's name its fire sound. The Scorpion's cannon fires `NOD_ScorpionTank_CannonFire` (9 takes);
its laser names `Multisound:NOD_ScorpionTank_BeamWeaponLoopMS`, which plays `NOD_ScorpionTank_BeamFire`
(5 one-shot takes) with a sparking loop. Internal names mislead here too: the `NURaide_*` files are the
Raider Buggy's; the Scorpion's are `NUScorp_*`/`NuScorp_*`.

### Stats (partial)
GameObjects are compiled structs with no field names, and module layouts vary per unit.
What worked: resolve each asset through the patch chain (TRAP 1b), scan it for values you
can confirm elsewhere, then check the same offsets in a sibling unit. Patches change struct
sizes, so an offset found in one copy can be wrong in another: the 1.9 `GDIMammoth` comes
from `_9` (13692 bytes, 12968 in 1.0), `GDIPredator` and the weapons from `_7`, and each of
the tanks' `WeaponTemplate`s is 12 bytes longer from patch 5 on.

| Field | Where it was found | Mammoth / Predator |
|---|---|---|
| Cost | u32 at GameObject +0x23c (every copy) | 2500 / 1100 |
| MaxHealth | float in the body module; Mammoth +0x31e8 (1.9) / +0x2f0c (1.0), Predator +0x211c | 10000 / 3400 |
| Speed | float in the LocomotorSet entry `{u32 condition=1, u32 0, float speed}`; Mammoth +0x3c0, Predator +0x2f8 | 40 / 60 |
| Vision | float 68 bytes before the end of the object (every copy) | 400 / 400 |
| Weapon range | `WeaponTemplate` float at +0x0c | 300 / 300 |
| Shot gap, reload (s) | four floats after the weapon's inline name: shot gap min/max, then reload min/max; +0x174..+0x180 in 1.0, +0x180..+0x18c from patch 5 (these two guns; the pods' sit 4 bytes later, so find them by value) | 0.3 then 2.0 / 0.3 then 1.9-2.1 |
| Shots per clip | not pinned; u32 at `WeaponTemplate` +0x70 reads 2 / 1 for the two guns in every copy (unconfirmed) | 2 / 1 |
| Damage | float in the warhead `WeaponTemplate` (the weapon's asset reference): `MammothTankShellWarhead` +0x1fc (1.0) / +0x208 (patch 5 on), `GDIPredatorTankCannonWarhead` +0x208 / +0x214 | 500 / 400 |

| Patch 1.9 (unconfirmed, found by the same patterns) | Cost | MaxHealth | Speed | Vision | Weapon |
|---|---|---|---|---|---|
| Flame Tank (`NODFlameTank`) | 1200 | 3700 | 75 | 350 | flamer, range 100, 0.1 s shots, warhead 500 |
| Stealth Tank (`NODStealthTank`) | 1500 | 1875 | 120 | 350 | rockets, range 275, warhead 375 |
| Beam Cannon (`NODBeamCannon`) | 1000 | 3000 | 75 | 500 | beam, range 500 |

Health sits in a run of floats `500, 80, 100, <health>, 200, 200`; find it by that run, not by offset.

The weapon name sits at +0x15c in 1.0 and +0x168 from patch 5 on, with its length at +0x04.
Cross-check anything you rely on; these offsets are proven only for these two units.

**Offsets move with the inline name.** Every field after the weapon's or object's inline name
shifts with its length. On the Scorpion (patch 7; names 4 bytes longer) the reload floats sit at
`WeaponTemplate` +0x180, the cannon warhead's damage at +0x210 (not +0x214), vision 72 bytes from
the end (not 68), and MaxHealth at GameObject +0x2c44. Its LocomotorSet entry is not `{1, 0, speed}`:
after the name come `1, 0, 2, 3, 8`, then the speed (90.0) at +0x308, unconfirmed. Find each value by
pattern, then confirm it on a sibling.

| Scorpion (`NODRaiderTank`) | Value |
|---|---|
| Cost, MaxHealth, vision | 800, 2400, 400 |
| Cannon `NODRaiderTankCannon` | range 275, 2.0 s between shots, warhead damage 240 |
| Laser `NODRaiderTankCannonLaser` | range 275, clip of 2 (u32 +0x70) 0.1 s apart, reload 2.36 s; 520 at +0x230 in its first nugget, the likely damage (the laser has no warhead asset to cross-check) |
| Dozer Blades | armour `NODRaiderTankArmorDozerBlades` adds one entry to the plain armour: damage type 31 at 0.01; `AttributeModifier:Modifier_NODDozerBlades` holds one modifier, type 23 x 0.75. The data names neither type. |

**Lasers.** C&C3 draws the Scorpion's laser with a draw module inside the GameObject, not a
separate laser object: three `Laser.fx` shader blocks whose `Texture1`/`Texture2` constants index
the object's asset references (`FXObeliskLaser` + `FXLaserOverlay`, the railgun's distortion pair,
and `FXObeliskLaserHeroic` + `FXLaserOverlay` for veterans), each after a run of floats (1, 0.5, 1,
0.03, 0, 0.2, 0, 1, 30, 30, 10) whose fields are not named in the data. `FXObeliskLaser` is the
Obelisk's own beam: 64 x 256, a red glow round a white-hot core, constant along its length. The
weapon's FX lists are `FX_NODSpitfireFire` (distortion and glow particles) and `FX_NODSpitfireHit`
(distortion, fire, glow and flash); particle-system layouts were not decoded. For the
record, the Mammoth's pods (`GDIMammothTankRocketPods`) read shot gap 0.1/0.25 and reload
10.2/9.8 at +0x178..+0x184 (1.0), and their warhead does 300 in 1.9.

## 6. Rendering sprites (the Remastered side)

Write a small software rasteriser (numpy is fine; about 2 s per frame at 3x supersampling)
rather than using Blender: you need exact control of camera, light and colour.

- **Camera:** orthographic. Screen `x = X`, screen `up = Y*sin(E) + Z*cos(E)`, depth
  `= Z*sin(E) - Y*cos(E)`, with **E = 32 degrees**. That matches the Remastered HD vehicle
  art; 54 degrees reads top-down beside it.
- **Facings:** 32, counter-clockwise, frame 0 = north. Yaw for frame f = `90 + f * 11.25`
  degrees with the model's +X as its nose.
- **Light:** one fixed world vector `normalize(-0.5, 0.6, 0.75)` (top, north-west).
  Brightness = Tiberian Sun's voxel ramp, sampled continuously (linear interpolation) at
  `n.L * 1.5 * 16`, with `n.L` clamped to 0..1 (so the index runs 0 to 24, 16 is neutral and
  the last seven values are never reached), from these 32 values:
  `0.619 0.662 0.701 0.736 0.777 0.889 0.925 0.975 1.000 1.023 1.066 1.106 1.142 1.169 1.204
  1.233 1.264 1.339 1.396 1.454 1.517 1.564 1.609 1.646 1.696 1.737 1.775 1.802 1.833 1.859
  1.893 1.922`. Clip RGB at 255 before converting to 8-bit or bright channels wrap.
  Plain ambient + Lambert renders read far too dark next to the game's units.
- **Normal maps:** apply C&C3's tangent-space `_NRM` maps using the vertex TANGENT and
  BINORMAL (`RGB/127.5 - 1` = components along tangent, binormal, normal, with tangent and
  binormal first made perpendicular to the normal). Body meshes only; treads have no
  tangents. They carry most of the panel detail at sprite size.
- **Scale:** pick one pixels-per-C&C3-unit value for all C&C3 units so they keep their
  relative sizes, render at 2x or more, then downscale with LANCZOS. Ours: render at 13 px
  per C&C3 unit, pack at 6.
- **Antialiasing:** supersample (3x), then box-average with premultiplied alpha.
- **Parts:** render hull frames (hull + treads) around the ground point under the centre of
  the hull's own bounding box, turret excluded. EA's hulls sit centred on the canvas. The
  model origin is the centre of the whole assembled model, barrels included, so a hull drawn
  around it sits off-centre towards the rear (about 3 classic px on both tanks). Render turret
  frames around the ground point under the turret pivot (the pivot's X and Y, Z = 0), so the
  turret's seat is a pure ground-plane offset and the turret keeps its height in the art.

## 7. Packing for Remastered

- **House colour:** Remastered hue-remaps team green to the player colour and keeps
  luminance. Paint masked texels pure green (red = blue = 0) that follows the texel's own
  luminance, **normalised per model**: `green = 128 * lum / mean_lum_under_mask`
  (lum = 0.299R + 0.587G + 0.114B on 0-255; the mean is taken over the diffuse texels where
  the HC alpha > 128, with the mask resized to the diffuse's size), blended over the diffuse
  by the mask alpha, then shaded as normal. C&C3 paints house colour over panels of very
  different brightness (Mammoth mask mean 136, Predator 96), so a fixed lift made the
  Mammoth glow while the Predator sat dim.
  Target, measured off shipped TS and RA2 voxel tanks in the same mod (green-dominant opaque
  pixels): post-shade median G about 118 to 169, green luminance about 70 to 111.
  Leave near-white, low-saturation texels white (unit numbers, the GDI eagle): the mask is
  scaled by `1 - clip((lum - 170)/40, 0, 1) * clip(1 - 3*sat, 0, 1)`, `sat = (max-min)/max`.
- **Sprite ZIP:** `ART/TEXTURES/SRGB/RED_ALERT/UNITS/<NAME>.ZIP` holding one
  `<name>-NNNN.tga` + `<name>-NNNN.meta` per frame, in the form and with the **canvas-centre**
  anchor of the field manual's
  [How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#the-frame-and-its-meta);
  the crops are also made centre-symmetric (the crop centre equals the canvas centre) as insurance.
  Canvas = ShapeSize x 8 (8x classic density) keeps real pixels for the zoom levels. Ours:
  Mammoth ShapeSize 64 (512 canvas), Predator 48 (384).
- **Tileset XML:** one `<Tile>` per shape number in `RA_UNITS.XML` (`<Key><Name>C3MK3</Name>
  <Shape>N</Shape></Key>`, frame `c3mk3\c3mk3-NNNN.tga`). Adding frames later does not add
  their tiles; missing tiles draw as white boxes.
- **Shadow:** ground units get no engine shadow. Bake EA's: every pixel with any alpha
  becomes a black silhouette at alpha 191, offset (4, 22) packed px (right, down), blurred by 3 and
  composited under the frame (`ts_reshadow.py`'s `drop_shadow`, which `c3_pack_tanks.py` calls). Turret frames get none. Leave that margin inside the canvas.
- **Cameo:** `ART/TEXTURES/SRGB/BuildIcon_<NAME>.tga`, 341x256 and **fully opaque** (noise
  shows through transparent pixels): composite the portrait onto opaque black. C&C3
  portraits are square: crop the centre 4:3 band, then resize.
- **Classic stub:** Remastered still needs a classic-mode SHP of the same frame count, sized
  canvas / 8 (ours: 64x64 and 48x48, 128 frames each).
- **Centring:** after packing, `scripts/unit_centring.py` moves every frame down by the hull's
  measured offset so the hull sits centred on the unit as EA's vehicles do, records the drop
  (`unit_art_drop.json`, `redalert/unit_art_drop.h`, which the fire points add) and prints the
  selection box. Ours: C3PRED 24 canvas px, C3MK3 32, C3SCORP 14 (its hull sat 1.81 classic px high), C3FLAME 11,
  C3STNK 7, C3BEAM 24, C3PITB 40, C3APC 26.
  Upgrade variants move with their base tank.
- **Wheels:** a wheeled vehicle (the Beam Cannon, Pitbull, Guardian APC) has no tread mesh, so it
  renders one hull frame per facing (`--tread-steps 1`) and its three step tiles name that one member.
- **Weapon effects:** `scripts/c3_tank_fx.py` builds each unit's firing effects (flame stream, rockets, beam
  charge, muzzle flashes, impacts) from the textures its weapon's FX lists name (`FXFireScroll`,
  `FXFireball4x4`, `FXLenzFlare*`, `FXMuzzle` and others, in `resources/custom-art/c3-tank-fx/`). Particle-system
  layouts are not decoded, so the timing is by eye. Projectiles (`NPMISSILE`'s `PMHELLMIS`, the Mortar's
  `NBRDEFMIS`) render through `c3_render.py` like a hull, 32 facings, at the effects' 4 px per C&C3 unit.
- **Packing one tank:** `c3_pack_tanks.py <NAME>` writes the tank's ZIP and tiles, then rebuilds `c3tanks.h`
  from every tank's model, so `C3_ART_DIR` must hold `model/<model>.npz` for all of them; with one missing, the
  packer names it and stops before writing anything.
- **Variants:** an upgrade that changes only one part packs only that part's frames; its other
  tiles name the base tank's ZIP members (`VARIANTS` in `c3_pack_tanks.py`). C3SCORPDZR owns turret
  frames only, C3SCORPLASDZR hull frames only. C3SCORPLAS owns both, as the laser changes the hull.
- **Railgun upgrade (`C3MK3RAIL`, `C3PREDRAIL`):** C&C3 shows the `UGRAIL` meshes (a sleeve round each
  barrel, a cable, a forked tip) and hides nothing. `scripts/c3_rail_turrets.py` adds them to the model
  (`extract`), renders the 32 turret facings with `c3_render.py --rails --glow` (`render`; a facing whose
  rail tip reaches the 1000 px canvas renders on 2000 px, packed on the same pixel grid) and writes each
  rail tank's ZIP with only those 32 turret frames (`pack`). Its hull tiles (0-95) name the plain tank's
  ZIP members, which the launcher has open because the plain tank's own tiles are in the same pack. The glow
  on the blue conduit is ours: C&C3's spec map leaves the rails unlit. Only the C&C3 pack carries them.

- **Aircraft:** one frame per facing, 32 facings, no baked shadow (the engine shadows aircraft in the air), centred
  on the model's own middle rather than its ground point, at the tanks' scale (`scripts/c3_pack_air.py`). At that
  one scale the Orca (35 C&C3 units long) is shorter than the Predator (44).
- **Deploying vehicles:** the Rig deploys with `GURIGUPAK_AN` (101 frames at 30 fps) on its own skeleton
  (`GURIGUPAK_SK`, meshes `GURIGUPAK_SN.*`); packing up plays it backwards, and the deployed base holds the last
  frame. `scripts/c3_pack_battlebase.py` packs the Battle Base as a turret building in the dug-in Tick Tank's
  layout (body, both guns in 32 facings turned about their own yaw pivots, 32 deploy frames: at 2 game ticks a
  frame they run C&C3's 3.37 s at the speed TF is played at, about 19 ticks a second), hull facing south,
  on a canvas centred on the Rig's ground point at 128 px a cell. Its three sets move with the Rig's art drop
  (`unit_centring.py` partners), so the deploy starts where the Rig's sprite stands. The pads start underground;
  geometry below the ground plane is cut away, as C&C3's terrain hides it.
- **Walkers:** `tools/cnc3/c3_extract_walker.py` (workspace) poses a walker through one cycle of its walk clip and
  `scripts/c3_pack_walkers.py` packs it in TF's TS walker layouts. The Juggernaut has a turret bone, so it takes the
  TS Titan's: 8 facings x 12 stages, the turret at 96-127; its turret bobs 2.5 units in the walk and is drawn at the
  cycle's mean height. The Avatar has none: its torso turns only in its clips, so it turns to fire, 32 facings x 8
  stages as the TS Mammoth Mk. II. Its commandeered pieces (`NUBEAM`, `S_DETECTOR`, `S_GENERATOR`, `FLAMETANK`) hang
  off the root and every clip carries them, so each is a whole variant of the walk. Each walk frame casts its own
  shadow from the walk part along the light. At the tanks' scale the Juggernaut is 48 units tall and its barrels
  reach 55 units up the screen facing north: it needs a 768 px canvas, the Avatar 640.
- **Infantry:** `scripts/c3_pack_infantry.py` poses each soldier into Tiberian Sun's light-infantry layout (292
  tiles) from its run, fire, idle and death clips, on the TS infantry's 267 x 208 canvas with the feet on its line.
  C&C3 infantry never go prone: the suppressed clips (crawl, prone fire, dive) stand in, and units
  without them stand. A squad is its soldiers in a wedge of up to six, each a few poses out of step; the squads
  after the first three are at C&C3's full payload (section 4), C3RIFLESQ and C3MILITSQ at their first entry's count.
  A soldier too big for the TS infantry canvas (the Zone Trooper's antenna and thrown deaths) gets a bigger one with
  the feet at the same place from its centre. A weapon can be a limb: the Cyborg's body mesh has no left arm, and his two weapon meshes (the EMP
  cannon and the particle-beam gauntlet) are his arms. Check a soldier against his portrait before leaving a mesh out.

## 8. DLL side (needs a Vanilla Conquer based DLL)

- **Turret seat:** the stock turret draws at the unit centre. For an off-centre turret pivot,
  generate a 32-entry table per hull facing (the pivot's ground point relative to the hull
  centre, rotated and projected, in classic px = packed px / 8) and add it in
  `UnitTypeClass::Turret_Adjust`, which is called with the hull facing. Order the table by
  `Dir_To_32`, clockwise from north, as EA's own turret tables are (the frames run the other way). Emit it from the
  packer so art and code cannot drift.
- **Rolling treads:** the stock engine has one body frame per facing. Add a per-type step count
  and pick `facing * steps + ((frame + unitID) / rate) % steps` while the unit is driving and
  not rotating in place (step 0 otherwise). Size the rate so a link travels about as fast as
  the ground (1 canvas px = 4/3 leptons). Unverified: no rate has been tuned in play yet.
- **Shape cap:** a second draw (the turret) renders nothing from shape 128 up (the field manual's
  [How the launcher draws sprites](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/how-the-launcher-draws-sprites.md#rules)).
  Keep turret frames below 128: 32 facings x 3 tread steps = 0-95, turret 96-127.
- **Fire points:** project each muzzle bone through the render camera per turret facing and
  emit leptons (1 packed canvas px = 4/3 leptons), measured from the turret's ground point
  (the muzzle's height folds into the north-south offset, as the camera draws it). Fire
  coordinate = unit centre + seat (in leptons, indexed by `Dir_To_32` of the hull facing) +
  muzzle offset (indexed by `Dir_To_32` of the turret facing).
- **Audio:** ffmpeg's cdata output is PCM, which crashes the Remastered client, so re-encode it
  and route it as the field manual's
  [TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#samples-of-your-own)
  sets out: the MS-ADPCM format and its ffmpeg line, the `RAC_SFX_`/`RAR_SFX_` events, and the VOC enum value
  and `audio.cpp` table row kept in the same order ([the method](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#the-method)).
  Check the format against a stock sample on the same channel before shipping. An event listing several
  `<entry>` WAVs plays one of them per trigger, which suits C&C3's many cannon takes. The RA2 tanks' voices
  and weapons ship this way as `R2*.WAV` in `Data/AUDIO/`.

## 9. Converting stats to RA scale

C&C3 HP runs far above RA's, and its timings are in real seconds. The plan: map one C&C3
unit onto its RA counterpart (Predator 3400 HP to a 400 HP main tank, speed 60 to 7, about
8.5x each) and apply that one factor to every other number, including damage. Reloads
convert at 15 game frames per second (RA's `TICKS_PER_SECOND`). What that gave (not yet
tuned in play): Predator 400 HP, speed 7, cannon 47 damage every 30 frames; Mammoth 1176 HP,
speed 5, cannon 59 x 2 every 35 frames, pods 35 x 4 every 150 frames; range 300 -> 4.75
cells, vision 400 -> 6. C&C3 kills much faster per second than classic RA, so expect to tune.
The Scorpion at the same scale: 282 HP, speed 10, cannon 28 every 30 frames, range 275 -> 4.35;
the laser 61 a shot, 2 a burst, every 35 frames. C&C3 draws its laser with the Obelisk's beam
texture and its draw module is not decoded, so a DLL's own Obelisk beam is the nearest match.

## 10. Checks before going in game

- A labelled sheet of all 32 facings with the turret seated as the engine will draw it.
- A line-up beside existing tanks at the same classic-pixel scale.
- A measured tread shift between consecutive steps (the belt's top run must move towards the nose).
- Nothing clipped at the canvas edge, shadow included.

---
Recipe by gibbo101 (Tiberian Factions for Red Alert Remastered), 2026.
