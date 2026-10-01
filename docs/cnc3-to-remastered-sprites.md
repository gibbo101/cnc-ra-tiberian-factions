# C&C3 units to C&C Remastered sprites: a working recipe

How to pull a unit out of Command & Conquer 3: Tiberium Wars (models, textures, audio,
stats) and turn it into HD sprites for a C&C Remastered Collection mod. Written for an AI
coding agent to follow. Every fact here was verified on the GDI Mammoth Tank and Predator
Tank (Steam release, patch 1.9, 2026), except where a line says it is unverified. No
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

There are no W3X or DDS files on disk. EA's asset builder compiled everything into binary
"asset streams" packed inside the `.big` archives. (Audio has patch streams too, in
`Core/1.5`, `Core/1.7`, `EnglishAudio/1.5` and `EnglishAudio/1.7`; the 1.0 audio was enough
for these two units, and the audio patch chain was not checked.)

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
  spec, `HC_<name>` = house-colour mask, plus a separate tread texture. `_K` variants also
  exist (unused here; purpose not checked).
- `GameObject:GDIMammoth`, `GameObject:GDIPredator`: the unit's gameplay object.
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
  +0x5c with a dummy leading field; it only uses the pointer.
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

> The railgun-upgrade meshes (`UGRAIL_*`) decode with the same code (their bounding boxes
> match) but use `ObjectsNOD.fx` with a scrolling mask texture; they were never rendered.

### Hull and turret split
Tag each vertex by its pivot's ancestry: anything under the turret bone (`BONE_TURRET` on
the Mammoth, `TURRET` on the Predator, which includes the barrels, pods and muzzle bones) is
turret; tread meshes are treads; everything else is hull. The turret pivot is NOT always at
the hull centre (the Predator's is 4.2 C&C3 units aft of it, the Mammoth's 3.1 forward), so
keep its position: you need it to seat the turret sprite per hull facing.

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

### House colour
The `HC_*` texture's **alpha** is the recolour mask (about 5% of the sheet). Its RGB is not
the colour. See step 7 for how to paint it for Remastered.

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
`global_common`.

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

The weapon name sits at +0x15c in 1.0 and +0x168 from patch 5 on, with its length at +0x04.
Cross-check anything you rely on; these offsets are proven only for these two units. For the
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
  `<name>-NNNN.tga` + `<name>-NNNN.meta` per frame. The meta is
  `{"size": [W, H], "crop": [x0, y0, x1, y1]}`. The launcher anchors the **canvas centre**
  on the unit, so compose each frame centred on the canvas; the crops are also made
  centre-symmetric (the crop centre equals the canvas centre) as insurance.
  Canvas = ShapeSize x 8 (8x classic density) keeps real pixels for the zoom levels. Ours:
  Mammoth ShapeSize 64 (512 canvas), Predator 48 (384).
- **Tileset XML:** one `<Tile>` per shape number in `RA_UNITS.XML` (`<Key><Name>C3MK3</Name>
  <Shape>N</Shape></Key>`, frame `c3mk3\c3mk3-NNNN.tga`). Adding frames later does not add
  their tiles; missing tiles draw as white boxes.
- **Shadow:** ground units get no engine shadow. Bake EA's: every pixel with any alpha
  becomes a black silhouette at alpha 191, offset (2, 6) packed px (right, down), composited
  under the frame. Turret frames get none. Leave that margin inside the canvas.
- **Cameo:** `ART/TEXTURES/SRGB/BuildIcon_<NAME>.tga`, 341x256 and **fully opaque** (noise
  shows through transparent pixels): composite the portrait onto opaque black. C&C3
  portraits are square: crop the centre 4:3 band, then resize.
- **Classic stub:** Remastered still needs a classic-mode SHP of the same frame count, sized
  canvas / 8 (ours: 64x64 and 48x48, 128 frames each).

## 8. DLL side (needs a Vanilla Conquer based DLL)

- **Turret seat:** the stock turret draws at the unit centre. For an off-centre turret pivot,
  generate a 32-entry table per hull facing (the pivot's ground point relative to the hull
  centre, rotated and projected, in classic px = packed px / 8) and add it in
  `UnitTypeClass::Turret_Adjust`, which is called with the hull facing. Emit it from the
  packer so art and code cannot drift.
- **Rolling treads:** the stock engine has one body frame per facing. Add a per-type step count
  and pick `facing * steps + ((frame + unitID) / rate) % steps` while the unit is driving and
  not rotating in place (step 0 otherwise). Size the rate so a link travels about as fast as
  the ground (1 canvas px = 4/3 leptons). Unverified: no rate has been tuned in play yet.
- **Shape cap:** a second draw on an object (the turret) renders NOTHING for shape numbers
  128 and above. Keep turret frames below 128: 32 facings x 3 tread steps = 0-95, turret
  96-127.
- **Fire points:** project each muzzle bone through the render camera per turret frame and
  emit leptons (1 packed canvas px = 4/3 leptons), measured from the turret's ground point
  (the muzzle's height folds into the north-south offset, as the camera draws it). Fire
  coordinate = unit centre + seat (in leptons, indexed by hull facing) + muzzle offset
  (indexed by turret facing).
- **Audio:** loose WAVs under their own (new) sample names resolve; the WAV must be
  MS-ADPCM, because plain PCM crashes the Remastered client. ffmpeg's cdata output is PCM, so
  re-encode: `ffmpeg -i in.wav -c:a adpcm_ms -ar 22050 -ac 1 out.wav` matches the weapon-SFX
  channel. Check the format against a stock sample on the same channel before shipping.
  New names are proven in play for other games' units (the RA2 tanks' voices and weapons
  ship as `R2*.WAV` in `Data/AUDIO/`). Each sound needs `RAC_SFX_<NAME>` and `RAR_SFX_<NAME>`
  events in `SFXEVENTSNONLOCALIZED.XML`; an event listing several `<entry>` WAVs plays one of
  them per trigger, which suits C&C3's many cannon takes. The DLL side is a VOC enum value
  plus a row in `audio.cpp`'s sound table, and the two are ORDER-COUPLED: append to both in
  the same order or every later sound shifts.

## 9. Converting stats to RA scale

C&C3 HP runs far above RA's, and its timings are in real seconds. The plan: map one C&C3
unit onto its RA counterpart (Predator 3400 HP to a 400 HP main tank, speed 60 to 7, about
8.5x each) and apply that one factor to every other number, including damage. Reloads
convert at 15 game frames per second (RA's `TICKS_PER_SECOND`). What that gave (not yet
tuned in play): Predator 400 HP, speed 7, cannon 47 damage every 30 frames; Mammoth 1176 HP,
speed 5, cannon 59 x 2 every 35 frames, pods 35 x 4 every 150 frames; range 300 -> 4.75
cells, vision 400 -> 6. C&C3 kills much faster per second than classic RA, so expect to tune.

## 10. Checks before going in game

- A labelled sheet of all 32 facings with the turret seated as the engine will draw it.
- A line-up beside existing tanks at the same classic-pixel scale.
- A measured tread shift between consecutive steps (the belt's top run must move towards the nose).
- Nothing clipped at the canvas edge, shadow included.

---
Recipe by gibbo101 (Tiberian Factions for Red Alert Remastered), 2026.
