# SPIKE: front-end texture delivery via a mod MEG

**Status:** **CLOSED — spike abandoned (2026-05-29).** Step 0 (static RE of `ClientG.exe`) resolved it: a mod texture MEG *is* read by the front-end, but only as a **whole-file SHADOW** (the mod's `Textures_SRGB.meg` *replaces* base entirely → **2.4 GB**). **No merge-per-file → a tiny atlas-only MEG does NOT work.** Luke's call (2026-05-29): **accept the verdict, use the `CONFIG.MEG` fallback** — Allied/Soviet keep their country flags as side stand-ins; GDI/Nod emblems + all-8 names already ship via `CONFIG.MEG`. No texture MEG shipped; Deck untouched. Detail in "## VERDICT" below.
**One-line:** Can a mod deliver custom **front-end** (launcher-shell) textures by shipping its own copy of a base texture MEG (e.g. `Data/TEXTURES_SRGB.MEG`), the way a mod already ships `Data/CONFIG.MEG`? If yes, **all** front-end imagery becomes moddable without EMC.

This doc is self-contained — you should not need the originating chat. Read it top to bottom before touching the Deck.

---

## VERDICT (Step 0 — static, 2026-05-29)

**Shadow-whole, not merge. The lightest texture delivery is 2.4 GB. Recommend NOT pursuing it — use the proven `CONFIG.MEG` fallback for Allied/Soviet.**

### How front-end MEG loading actually works (from `ClientG.exe`)
1. The launcher front-end mounts MEGs through `MegaFileManagerClass::Megafile_Add(const std::string&, MegaFileOpenType, AccessType, OverrideType)` into **one combined FNV-1a `name→entry` hash index** (resolver `Subfile_Find_Data_Image` → helper at `0xa7d7c0` hashes the normalised path with FNV-1a constants `0x811c9dc5`/`0x1000193` and does a single index lookup). Two mount sources, both at base startup: the `Data\MEGAFILES.XML` manifest (Music, **Config**, Shaders, Maps, Movies×6, Models, Textures, **Textures_SRGB**, Textures_Common/TD/RA/Patches_SRGB, UI) and a **hardcoded array** (audio: `SFX2D_*`/`SFX3D`/`Patch_SFX`).
2. The manager *can* resolve duplicate paths across mounted MEGs (proven: `SFX2D_ALL.MEG` and `SFX3D.MEG` both contain `_TEST_1/2/3.WAV`; the `OverrideType` arg exists) — so per-file override is a real capability, **decided at add-time** by mount order / `OverrideType`.
3. **But the mod system never uses it.** `ModManagerClass::Load_Mod` (modmanager.cpp) ingests only **loose** files from the mod's `Data\AUDIO\`, `Data\XML\` (`.XML`), `Data\MAPS\` — it makes **zero `Megafile_Add` calls** (none of the 28 `Megafile_Add` call sites fall in the mod-loader code range `0x7ba700–0x7be000`). No mod code mounts any MEG — CONFIG or texture.
4. The proven `Data/CONFIG.MEG` delivery therefore works via the **generic manifest loader resolving each relative MEG path against the active mod folder first, base install second** (launcher sets its working dir — `Set_Working_Directory`, `SetCurrentDirectoryA/W`; `Init_Mods` builds the `Mods\Red_Alert\…` root). Opening `Data\Config.meg` finds the **mod's whole copy** and mounts it *instead of* base → **shadow-whole by filename**, NOT a merge. (That's why shipping the full repacked 44 MB CONFIG.MEG is what works.)

### Consequences for textures
- A mod `Data/Textures_SRGB.meg` shadows the base **2.4 GB** MEG **whole**: to avoid breaking the front-end it must contain all **1,358** base entries (incl. the **176 MB** `MT_COMMANDBAR_COMMON.TGA`, edited) → **2.4 GB Workshop payload**.
- A **tiny** atlas-only `Textures_SRGB.meg` mounts *alone* → the front-end loses the other 1,357 textures → **breakage**, not a clean swap. (That is the predicted result of the Step-1 tiny probe — the CRASH/missing-textures outcome, not SUCCESS.)
- The atlas lives **only** in `Textures_SRGB.meg`; the five texture MEGs are **fully disjoint** (`PATCHES ∩ base = 0`; PATCHES is purely additive HD content, 23,293 files). So there is **no smaller manifest MEG that already carries the atlas** to shadow instead. (A ~400–580 MB variant — shadow `Textures_Patches_SRGB.meg` whole, inject the atlas, rely on last-mounted-wins for the duplicated path — is *theoretically* possible but unconfirmed and still large.)

### Real-world corroboration
- **0 of 96** subscribed Workshop mods ship **any** `.meg`. The established texture-override surface is **loose files** (8,587 DDS / 351 TGA across the cache) — which the **front-end shell ignores** (PROVEN #4; matches memory `reference-ui-atlas-modding` "IN-GAME ONLY").
- The one mod that changes front-end art — **Reilsss CnCinRA** — does it with a **wholesale loose 176 MB atlas TGA** (`184,582,588 B`, ≈ the full base atlas) and ccmod.json **"(Requiers EMC)"**. **Correction (2026-07-11 spike):** Reilsss ships **no DLL and no MEG** — it is a pure data mod; its `"(Requiers EMC)"` refers only to its CCDATA `[New*]` sections needing EMC's **sim-side** DLL to parse them. EMC is a `RedAlert.dll` loaded by `InstanceServerG` — a *different* process from the `ClientG` front-end (CNC-only exports, no d3d/graphics imports) — so it **cannot** hook the front-end texture read; the original "EMC's DLL hook" claim here was mechanically impossible. Reilsss's art reaches the game as **loose files `ClientG` reads itself**, and per PROVEN #4 that is the **in-game** render path only. See [[spike-launcher-process-model]] / `launcher-vs-dll-ownership.md`. So "wholesale" is the only known shape: whole-atlas-loose+EMC, or whole-MEG-shadow.

### Recommendation
- **Do not pursue the texture-MEG route for Allied/Soviet emblems.** 2.4 GB (or a fragile ~400 MB) per subscriber is wildly disproportionate to two emblems, and GDI/Nod emblems + all-8 faction names already ship via the proven ~42 MB `CONFIG.MEG` path. For Allied/Soviet use the **Fallback** at the bottom of this doc.
- **Optional confirmation only:** the Step-1 tiny probe would settle merge-vs-shadow empirically, but it is a **Deck write** (needs Luke's OK) and the analysis predicts breakage/no-op, not a win. **Do not ship the 2.4 GB MEG** (Step 2) unless Luke explicitly decides the two emblems justify that payload.

---

## Why this matters (the concrete payoff)

Immediate driver: **faction-picker emblems** in the RA skirmish lobby. We want the 4-faction set to read as GDI / Nod / Allied / Soviet.

- GDI + Nod emblems are **DONE** (shipped, proven) — see "Proven" #1.
- **Allied + Soviet emblems are blocked** by the texture-delivery wall this spike targets.

If the spike succeeds it unlocks far more than the picker: custom main-menu art, custom faction logos, any front-end image — all Workshop-shippable, no EMC. It is the *image* sibling of the `config-meg-mod-delivery` breakthrough.

**Concrete texture surfaces this spike would fix at once** (all are atlas regions the launcher picks by faction/country — NO CONFIG.MEG field repoints them, confirmed; the data path can't touch any of these):
- Allies/Soviet **picker emblems** (the dropdown only has stock GDI/Nod `_00`/`_01`; Allies/Soviet fall back to country flags).
- **Map position-select** marker flag (shows the player's country flag, e.g. Spain for GDI).
- **Skirmish loading-screen** flag (same country flag).
- Bespoke GDI/Nod logos (replacing the stock `_00`/`_01`).
A good spike test edits the `_04`/`_05` (or a map-select/flag) regions and checks **both** the picker dropdown **and** the map-position/loading marker change — they likely share the same flag regions.

---

## PROVEN already — do NOT re-investigate these

1. **Picker icon = `FACTIONS.XML` → `EncyclopediaComponent/DefaultIcons/SmallIconName`** (FACTIONS.XML lives inside `CONFIG.MEG`). Repointing it works via a mod `Data/CONFIG.MEG` — **no EMC**. Proven on the Deck: Spain→GDI (`_00`), Turkey→Nod (`_01`). Faction→icon map: `Faction1`=GDI→`_00`, `Faction2`=Nod→`_01`, `Faction3`=Spain→`_03`, `Faction4`=Greece→`_04`, `Faction5`=USSR→`_05`, … `Faction10`=Turkey→`_10` (the `_NN` is `UI_Multiplayer_PlayerSlot_Faction_NN.tga`). `_02` is absent.
2. **`SmallIconName` resolves to an ATLAS REGION** inside `MT_COMMANDBAR_COMMON`, not a standalone file (there are **no** standalone faction-icon `.tga` files in any texture MEG — checked all five).
3. **The front-end preloads ONLY the `UI_Multiplayer_PlayerSlot_Faction_NN` regions.** Pointing `SmallIconName` at any *other* region (`UI_SIDEBAR_FACTIONLOGO_*`, `RA_UI_MULTIPLAYER_*_LOGO`) → **hard CRASH at launcher startup**. Confirmed twice (FACTIONLOGO_GDI; then MP_ALLIED/SOVIET_LOGO). So the only crash-safe `SmallIconName` targets are `_00`,`_01`,`_03`–`_10`. That set contains **no Allied/Soviet emblem** — hence this spike.
4. **The front-end IGNORES loose `Data/ART/TEXTURES/SRGB/*` overrides.** In-game *does* honor them (the in-game radar crest works via a loose `MT_COMMANDBAR_COMMON.TGA`), but the front-end shell does not — proven: a loose atlas with the picker flags repainted never changed after a confirmed full restart. **So we cannot change the loaded regions' PIXELS via the loose path.**
5. **`MT_COMMANDBAR_COMMON.TGA` lives ONLY in `TEXTURES_SRGB.MEG` (2.4 GB).** No other texture MEG holds it; no standalone copy anywhere.
6. **`CONFIG.MEG` (42 MB) carries ZERO textures** → can't smuggle the atlas in there (the front-end won't resolve a texture path out of CONFIG.MEG), and `meg_pack.py` is **replace-only** (can't add new files).
7. **`Data/CONFIG.MEG` mod-delivery works** — a mod's CONFIG.MEG *shadows* the base and the front-end reads it. This is the precedent the spike generalizes.
8. **EMC route is not usable — and the "EMC changes front-end textures" framing was wrong (corrected 2026-07-11).** EMC is a **sim-side** `RedAlert.dll` (loaded by `InstanceServerG`, a separate process from the `ClientG` front-end; export table byte-identical to base, no d3d/graphics imports) — it **cannot** hook ClientG's texture reads. Reilsss's CnCinRA ships **no DLL**; its art is plain **loose files ClientG reads itself** (in-game render path only, per #4). Still not a front-end lever for us — but not via any "EMC hook." **New open question:** Reilsss also ships ~140 *individual* front-end-screen DDS (`RA_MAINMENUBG_*`, `RA_UI_MISSIONSELECT_*`, `RA_UI_MULTIPLAYER_*`, …) whose inner paths mirror base `TEXTURES_SRGB.MEG`; whether such **non-atlas** front-end textures loose-override is **unverified** — one cheap Deck probe would settle it, and if positive PROVEN #4 narrows to "atlas pixels only."

---

## The hypothesis

> A mod's `Data/TEXTURES_SRGB.MEG` shadows the base `TEXTURES_SRGB.MEG` exactly as `Data/CONFIG.MEG` shadows base CONFIG.MEG, and the front-end reads the atlas from it.

If true, we change the *pixels* of the already-loaded `_NN` regions (e.g. paint the Allied emblem into `_04`, Soviet into `_05`) and Greece/USSR show emblems instead of flags — **with no FACTIONS.XML change** (they already point at `_04`/`_05`).

---

## Investigation order — CHEAPEST FIRST (do not jump to the 2.4 GB ship)

### Step 0 — STATIC (no ship, no Deck): answer shadow-vs-merge from the binary
The single most valuable question: does the launcher load an arbitrary mod `Data/*.MEG`, and does it **shadow-whole** (mod MEG replaces base entirely → must contain all ~thousands of base textures → 2.4 GB) or **merge-per-file** (mod MEG overlays only the files it contains → a *tiny* MEG with just the atlas works)?
- `strings ClientG.exe | grep -iE "megafile|\.meg|mod|texture|mount|loadorder|override"` and trace the mod-asset mount logic.
- Determine whether it globs `Mods/.../Data/*.MEG` or hardcodes `CONFIG.MEG`.
- If merge-per-file: the whole spike becomes a **tiny** ship (atlas-only MEG) — huge.

### Step 1 — TINY PROBE (small ship): atlas-only mod MEG
Build a mod `Data/TEXTURES_SRGB.MEG` containing **only** the modified `MT_COMMANDBAR_COMMON.TGA` (+ `.MTD`/`.MTM` if needed). Ship, full-restart, open dropdown.
- Greece/USSR show emblems **and** the rest of the front-end renders fine → **merge-per-file** → cheap delivery, done.
- Front-end loses other textures / crashes → likely **shadow-whole** (ambiguous with "not read at all"; cross-check with Step 0). Proceed to Step 2 only if Step 0 says shadow-whole *is* read.
- No change, lobby fine → mod texture MEG **not read** at all → spike fails, go to Fallback.

### Step 2 — FULL (2.4 GB ship): definitive shadow-whole test
Only if Step 0/1 indicate shadow-whole is the model. Repack the **entire** base `TEXTURES_SRGB.MEG` with the atlas swapped, ship all 2.4 GB.
⚠️ A 2.4 GB Workshop payload is a real cost (every subscriber re-downloads). Confirm with Luke before committing to this as the *shipping* mechanism even if it works.

---

## Build recipe (atlas with Allied/Soviet emblems baked into `_04`/`_05`)

Script already written: **`/tmp/build_spike_atlas.py`** (output `/tmp/atlas_spike.tga`). Logic:
- Load base atlas `MT_COMMANDBAR_COMMON.TGA` (extract from `TEXTURES_SRGB.MEG` if not cached).
- Crop the clean stock emblems `UI_SIDEBAR_FACTIONLOGO_ALLIES` (gold chevron) and `_SOVIET` (red pentagon) from the same atlas; fit (preserve-aspect, transparent pad) into the `_04` (Greece) and `_05` (USSR) regions; write back.
- Atlas format: **6871×6716, 32-bit BGRA, bottom-origin, `desc=0x00`, 18-byte header, no footer.** File offset for image pixel (x,y): `18 + (H-1-y)*W*4 + x*4`, bytes `B,G,R,A`.

Repack into the MEG:
```
python3 scripts/meg_pack.py repack <TEXTURES_SRGB.MEG> <out.MEG> MT_COMMANDBAR_COMMON.TGA=/tmp/atlas_spike.tga
```
(`meg_pack` mirrors EA's MegafileBuilder byte-format; the reader validates nothing.)

---

## Key paths, coords, tooling

- Base texture MEG: `~/.steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_SRGB.MEG` (2.4 GB)
- Atlas inner path: `DATA\ART\TEXTURES\SRGB\MT_COMMANDBAR_COMMON.TGA` (184,582,562 B); siblings `.MTD` (110,654 B), `.MTM` (250,810 B)
- `.MTD` region record: `NAME.TGA` + variable null padding + 4×LE-int32 `(x,y,w,h)` top-left origin
- Region coords (base atlas):
  - `UI_Multiplayer_PlayerSlot_Faction_04` (Greece) = `(4940,5394,150,80)`
  - `UI_Multiplayer_PlayerSlot_Faction_05` (USSR)  = `(5249,5399,150,80)`
  - `UI_Multiplayer_PlayerSlot_Faction_00` (GDI)   = `(3862,5483,66,56)`
  - `UI_Multiplayer_PlayerSlot_Faction_01` (Nod)   = `(3862,5541,66,56)`
  - `UI_SIDEBAR_FACTIONLOGO_ALLIES` = `(5698,1706,794,713)`  (gold chevron, clean)
  - `UI_SIDEBAR_FACTIONLOGO_SOVIET` = `(2684,1709,794,713)`  (red pentagon, clean)
- Deck mod Data dir (scp target): `deck@steamdeck:/home/deck/.steam/steam/steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/CnCRemastered/Mods/Red_Alert/Vanilla_RA/Data`
- Tooling: `scripts/meg_pack.py` (repack/verify), `scripts/meg_extract.py` (list/extract). System `python3` has PIL; **no numpy** (use PIL raw `BGRA` + per-row byte writes).
- The mod's working `Data/CONFIG.MEG` (Spain→`_00`, Turkey→`_01`) must stay shipped alongside any texture MEG.

## Success / fail criteria
- **SUCCESS** = Greece → Allied chevron, USSR → Soviet hammer-sickle in the dropdown (Spain/Turkey already GDI/Nod). Front-end otherwise intact.
- **NO-OP** = Greece/USSR still flags → front-end ignores the mod texture MEG.
- **CRASH** = mod texture MEG rejected / shadow-whole with missing files.
Recovery from a bad ship: `ssh deck@steamdeck "rm <Data>/TEXTURES_SRGB.MEG"` then relaunch.

## Fallback if the spike fails
Ship the stock result (no texture MEG): GDI/Nod emblems via CONFIG.MEG `SmallIconName`→`_00`/`_01`, Greece/USSR keep their country flags as Allied/Soviet stand-ins, and relabel all four names + blank the bonus line via `MASTERTEXTFILE`. ~42 MB total, fully proven.

## Related docs
- `ui-atlas-modding.md` — loose atlas override = **in-game only** (the wall this spike routes around)
- `config-meg-mod-delivery.md` — the CONFIG.MEG front-end **data** delivery this generalizes
- `launcher-vs-dll-ownership.md` — the launcher/DLL boundary; add the result of this spike there when known
- `mix-file-format.md` — MEG/MTD format + tooling
