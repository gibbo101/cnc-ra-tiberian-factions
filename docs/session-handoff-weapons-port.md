# Session state — TDOBLI separation milestone

> **ARCHIVED — superseded by `building-separation-plan.md` (M2+M3 complete) and
> `classic-mode-palette-remap.md`.** This is a point-in-time handoff from
> 2026-05-21; the entire M2–M5 building-separation arc and the classic-mode
> palette remap have since shipped (v0.50). Retained as a historical record.

**Last updated:** 2026-05-21 (evening, ~10h after Phase W1 audio breakthrough)
**Working tree:** clean (all changes committed)
**Latest commit:** `classic-mode: ship TD SHPs via TFASSETS.MIX (palette remap deferred)`

> **OUTDATED on the palette point (2026-05-28):** "Door 3" below (Format80 codec +
> closest-colour palette remap) is **DONE and shipped** — see
> `classic-mode-palette-remap.md`. Ignore the "deferred / 95% / classic-mode
> polish" notes in this historical handoff. The rest stands as a point-in-time record.

---

## What landed since the last handoff

Big arc this session. From "Phase W1 audio working" through "first fully-separated TD building shipped" with all the architectural infrastructure that future buildings will reuse.

### TDOBLI: first fully-separated TD building (TIER 5, hardest in catalogue)

Started as Logic=TSLA-aliased entry, ended as a `STRUCT_TDOBLI` heap entry with own everything. Pieces landed:

- **`STRUCT_TDOBLI` enum** + `ClassObelisk` BuildingTypeClass + `Init_Heap()` registration
- **Own `_anims[]` BSTATE_ACTIVE** — 4-frame charge at OBELISK_ANIMATION_RATE=15
- **Charges=yes** wires into the engine's IsCharging/IsCharged state machine (same mechanism TD uses)
- **OBELPOWR + OBELRAY1 sounds** via the proven SFXEvent recipe (`docs/td-audio-routing-recipe.md`)
- **TD construction sound** (CONSTRU2) for all STRUCT_TDxxxx buildings via range check in `building.cpp:3940`
- **3-line laser-beam render** ported from `tiberiandawn/techno.cpp:2481-2514`:
  - `Lines[3][5]` / `LineCount` / `LineFrame` / `LineMaxFrames` as TechnoClass members
  - Per-frame draw block in `Draw_It`
  - Per-tick countdown in `AI()`
  - `BULLET_LASER` branch in `Fire_At` (uses validated `target_coord` not `As_Coord(target)` — learned via Deck playtest when target deaths caused laser-to-origin)
  - Scorch smudge stamp on impact
- **`CC_Draw_Line`** wrapper + **`DLL_Draw_Line_Intercept`** export (RA's DLL didn't expose line drawing; we added it)
- **Electric_Zap suppression** for any IsElectric weapon firing BULLET_LASER (bullet-type-keyed, not building-type-keyed — auto-applies to future TD laser weapons)
- **Per-building dispatch** in `building.cpp` lines 656 / 4093 / 6244 — STRUCT_TDOBLI joined the Tesla-pattern checks (vanilla engine idiom, not a hack)
- **OBELPOWR plays at charge-start** via per-Type branch in `Charging_AI` (replaces TSLAPOWR for STRUCT_TDOBLI; future cleanup: per-weapon `ChargeSound=` field)

### Classic-mode SHP routing

- **`scripts/mix_tools.py`** (new) — Westwood MIX format reader/writer, implementing the CRC32-ish filename hash from `common/crc.cpp`
- **`Vanilla_RA/CCDATA/TFASSETS.MIX`** — mod-shipped mixfile containing TDOBLI.SHP + TDOBLIMAKE.SHP (extracted from TD's CONQUER.MIX, renamed with TD prefix)
- **`init.cpp` MFCD registration** — best-effort cache of TFASSETS.MIX
- **Removed `bdata.cpp` ImageData/BuildupData stub-borrow** from STRUCT_TESLA — was the last "real shortcut" in the TDOBLI separation. Engine now finds the actual TD SHPs.

### What did NOT work (so future sessions don't waste time re-trying)

- **Disabling classic mode via `Legacy_Render_Enabled = false`** → causes black screen when user presses space (launcher's toggle UI is independent of the DLL's legacy-data population)
- **Overriding `INPUTTRANSLATORCONFIGURATIONS.XML` to remove SPACE → COMMAND_CNC_LEGACY_RENDERING_TOGGLE** → launcher ignores the mod XML for this binding (either hardcoded in launcher binary or merged-with-base-wins)
- **Remapping SPACE to a different command in the mod XML** → same result, launcher ignored it

Verdict: the spacebar classic-mode toggle is launcher-side, cannot be disabled from the mod. Player must rebind in Options → Controls if they want to disable it.

---

## Where we are right now

- **Phase W1 audio (3 weapons + recipe doc):** ✅ committed
- **TD audio routing recipe:** ✅ proven and documented (`docs/td-audio-routing-recipe.md`)
- **TD prefix convention:** ✅ established (`[[project-td-prefix-convention]]`)
- **Building separation strategic commitment:** ✅ recorded (`[[project-building-separation-committed]]`)
- **TDOBLI fully separated (first vertical slice, M5-tier):** ✅ shipped — Remastered mode 100% TD-authentic
- **TD building separation recipe doc:** ✅ written (`docs/td-building-separation-recipe.md`)
- **Classic-mode polish for TDOBLI:** 95% — palette mismatch on SHP rendering, deferred to a one-shot Format80-codec iteration that retrofits all TD SHPs at once when classic-mode polish becomes a priority

---

## Known limitations (documented, not blocking)

1. **Classic graphics mode color mismatch** on TDOBLI (and any future TD-sourced SHP). TD's color indices interpreted through RA's PALETTE.PAL → mild visual mismatch. Fix: implement Westwood Format80 codec + closest-color palette remap in `mix_tools.py`. Estimated 3-4 focused hours. Deferred to a "classic-mode polish" iteration that processes all TD-sourced SHPs in one batch.

2. **Spacebar classic toggle cannot be disabled** from the mod (as documented above). Mod README should recommend Remastered graphics for the cleanest experience.

3. **OBELPOWR/OBELRAY1 still play back-to-back** at fire time, not the TD-authentic "warmup-then-fire" delayed sequence. Could be fixed by hooking the charge animation's completion frame to trigger fire (rather than firing at Fire_At). Minor polish, low priority.

4. **Mid-campaign saves from previous builds will not load** — new STRUCT_TDOBLI enum value changes `BuildingTypeClass` array indices. Not yet a concern (no campaigns shipped); flag for future campaign work.

5. **Country stat modifiers** (France Phase Tank, Germany Demolitionist, Ukraine Parabombs, Turkey +10% build speed) — Turkey/Spain are hijacked by HOUSE_GOOD/HOUSE_BAD launcher swap so their modifiers auto-bypass. The others remain active. Per `[[project-country-modifiers-removal]]`, slated for eventual removal once faction work stabilises.

---

## Three doors for next session

### Door 1: Continue scaling separation — pick the next building

Recipe is validated. Cycle time per building is bounded (1-6 hours per tier). Recommended order from the building-separation-plan §5:

- **Tier 1 first** (TDNUKE, TDNUK2, TDSILO, TDPYLE) — pure data ports, ~1-2h each, builds confidence the recipe is solid
- Then **Tier 2 defensive turrets** (TDGTWR, TDATWR, TDGUN, TDSAM) — reuse the weapons + audio infrastructure
- Etc.

This is the highest-momentum option. Each building shipped = irreversible architectural progress.

### Door 2: AI base-build order arrays for HOUSE_GOOD / HOUSE_BAD

Per the separation plan §3.1 H2. RA's AI base-build sequences are STRUCT_*-indexed. Adding parallel sequences referencing STRUCT_TDxxxx would give GDI and Nod proper AI behavior (currently they inherit Allied/Soviet's vanilla build orders, which now reference buildings that don't exist for them).

Worth ~1-2 days. Doable after a few Tier 1 buildings land.

### Door 3: Format80 codec + classic-mode SHP pixel-perfect

Implement WW Format80 LZSS in `mix_tools.py`, add a `--remap-palette` flag to `pack` that decompresses each frame, applies a closest-color remap from TD palette to RA palette, recompresses or stores as Format0. Apply retroactively to all TD-sourced SHPs in TFASSETS.MIX.

Worth ~3-4 hours. Best done as a one-shot after several TD buildings have shipped (so the retroactive pass covers many assets at once).

### Recommendation

Door 1 first (scale separation, validate recipe across multiple buildings), Door 2 after a handful land (so AI behaviour catches up to the new content), Door 3 when classic-mode polish becomes a player-facing concern.

---

## Memory entries that anchor this state

- `[[project-td-audio-routing-recipe]]` — audio recipe with load-bearing gotchas
- `[[project-td-prefix-convention]]` — TD prefix on every ported entity
- `[[project-building-separation-committed]]` — strategic decision
- `[[project-td-building-separation-recipe-validated]]` *(NEW)* — TDOBLI as worked example, the canonical recipe doc
- `[[feedback-no-tradeoffs-with-tools]]` — when infrastructure exists, build the right thing
- `[[feedback-review-td-source-first]]` — read TD's implementation as the spec
- `[[feedback-push-back-on-errors]]` — user has pushed back hard on shortcuts this session; honour that going forward

---

## Canonical docs

- `docs/td-building-separation-recipe.md` *(NEW this session)* — per-building port recipe, distilled from TDOBLI
- `docs/td-audio-routing-recipe.md` — audio pipeline
- `docs/building-separation-plan.md` — M1-M6 milestone plan (TDOBLI = M5-tier vertical slice complete)
- `docs/catalogue.md` — building catalogue + bug list (most bugs deferred to separation milestones)
- `docs/weapon-ports.md` — Phase W1/W2/W3 weapon scope (W1 data-complete + audio-complete)
- `docs/cargo-plane-port.md` — TDAFLD reference (pre-separation; will migrate)
- `docs/adding-td-buildings.md` — alias-mode recipe being superseded by the new separation recipe

---

## Commit history this session (most recent first)

```
classic-mode: ship TD SHPs via TFASSETS.MIX (palette remap deferred)
fix: wire TDOBLI charge animation via Charging_AI state machine
v0.4.1-phase-w1f: TDOBLI laser-beam render + charge state machine
v0.4.1-phase-w1e: STRUCT_TDOBLI — first fully-separated TD building (WIP)
docs: full session state — Phase W1 + audio routing breakthrough + next steps
audio: TowTwo + TdTurretGun TD sounds (Phase W1 audio complete)
v0.4.1-phase-w1d: TD audio routing PROVEN — Obelisk plays iconic laser
refactor: prefix all TD-ported weapon/bullet/warhead IniNames with TD
diagnostic: tf_primary_parse.log for TechnoTypeClass::Read_INI
fix: Logic= alias no longer silently inherits donor Primary/Secondary weapons
v0.4.1-phase-w1bc: TdTurretGun + OblsLaser weapon data ports
docs: commit to full building separation; defer alias bugs to milestones
v0.4.1-phase-w1a: TOW_TWO weapon port — TDATWR fires TD-authentic AA+AG missile
```

(Plus the recipe doc + handoff updates landing right after this writes.)
