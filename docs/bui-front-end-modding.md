# .bui front-end UI modding — the ChunkFile scene-graph layer

**Status:** Format fully reverse-engineered + **production-proven** (2026-07-11). The launcher's front-end screens are `.bui` files inside the mod-shippable `CONFIG.MEG`; a mod can edit them and ClientG renders the change. We **already ship one** (the main-menu reorder — see `scripts/bui_mainmenu_build.py`), which is the live proof the whole pipeline works. This doc is the canonical format + capability reference; it consolidates the existing main-menu pipeline with a systematic RE of the format and a map of what the layer can and cannot unlock.

**One-line:** `.bui` = a Petroglyph **ChunkFile** container (`CH` magic + zlib) wrapping a tag-based UI scene graph. It is **data**, delivered via the proven `CONFIG.MEG` shadow — so it is entirely independent of the DLL/process boundary (see `launcher-vs-dll-ownership.md` / [[spike-launcher-process-model]]; our sim DLL never touches it — `ClientG.exe` reads the modded MEG at front-end load).

---

## TL;DR — what this buys us (and what it doesn't)

- **YES — cosmetic reshape of EXISTING widgets** on any front-end/HUD screen: reposition, resize, hide/show, retint, and same-length texture/text-key swaps. **Proven on both surfaces:** the front-end (main-menu reorder ships in production) **and** the in-game HUD (Deck-confirmed 2026-07-11 — a hide edit on `RA_TACTICAL_UI.BUI`'s Soviet faction-logo rect removed that logo live in a skirmish).
- **NO — adding new options/structure.** You cannot add a widget/row/screen, because (a) any payload growth violates the same-size rule below, and (b) the things we'd *want* to add are code-populated from compiled C++ enums/type-managers in `ClientG.exe`, not from `.bui` data.
- Treat this as a **polish / faction-identity** capability, not a feature unlock. It does **not** revive the 5th-faction or playable-GDI/Nod-campaign goals — those stay dead on engine walls.

---

## The format (36-byte CH header + zlib) — confirmed by disassembly AND a shipping artifact

```
offset  size  field
[0x00]   2    magic 'C''H'            (0x43 0x48) — ChunkFile. MUST stay.
[0x02]   2    version major.minor     (02 01 = v2.1) — allowlist {2.0, 2.1}. MUST stay.
[0x04]   1    flags                    low nibble = compression type (1 = zlib). MUST stay.
[0x05]   3    ff ff ff  reserved
[0x08]   4    hash u32                 NOT validated by the launcher — leave byte-for-byte stale.
[0x0C]   4    00 00 00 08              compression-type dword
[0x10]   4    csize u32                compressed-stream length == filelen - 0x24. PATCH on edit.
[0x14]  16    zeros                    reserved (uncompressed size is NOT stored anywhere)
[0x24]   …    zlib stream ('78 9c …')  → the widget scene graph
```

**The `[0x08]` hash is never checked.** Proven two ways: (1) disassembly of ClientG's `ChunkFile::ChunkFileReaderClass` load path (constructor ~`0x98ba30` → `Read_Header` `0x993f90`) shows the header is validated **only** on the 2-byte magic and the `[0x02]` version allowlist; the `[0x08]` dword is read into the reader object and at most used as an offset to an optional trailing section that UI `.bui` don't have — it is never recomputed/compared. The only tamper checks are **structural** (`Open_Chunk`/`Close_Chunk` balance + `MAX_CHUNK_DEPTH` → *"Probable corrupted/tampered file"*) plus zlib's own adler32. (2) Our shipped `RA_MAIN_MENU.BUI` carries a **stale** hash (`fb5deab3`, identical to base) over an edited payload and renders fine. So: keep `[0x08]` unchanged; the hash algorithm is uncracked but **non-load-bearing**.

Do **not** confuse this file format with the network layer: `PG::ContainerClass::read(... ComSecurityContext ...)` with Sosemanuk + HMAC is the **encrypted socket** between InstanceServer and ClientG (see the process-model doc), *not* the `.bui` on-disk format. The `.bui`/`CONFIG.MEG` path has **no encryption and no content hash**.

### The decompressed payload = a tag-based scene graph

Widgets carry ASCII names (`ButtonFactionComboBox`, `Combo_Listbox`, `Side_Bar_Group`), texture refs (`ui_multiplayer_playerslot_faction_00`, `ui_sidebar_factionlogo_allies`), text keys (`TEXT_PLAYER_SLOT_FACTION_CHOICE`), and typed property tags. Known tags (from the shipped main-menu work):

- **`02 10` = rect/frame tag** — 16 bytes = 4 LE floats `x, y, w, h`, screen-normalized (0..1). Editing a widget's rect `Y` moves the whole widget (frame + label together).
- **`03 10` = tint tag** — RGBA floats; alpha at tag `+12`. Set alpha 0 to hide.

The broader property vocabulary seen in scene graphs (esp. `RA_TACTICAL_UI.BUI`): `POSITION SIZE TINT TEXTURE RENDER_MODE ROTATION HIDDEN ALPHA POSX POSY SIZEX SIZEY TELETYPE BRIGHTNESS LINE_WIDTH OFFSETV REPEATV TEXSIZEV`, plus groups (`AspectRatio_Group`) and animation states (`SlideIn`/`SlideOut`). The full per-widget grammar is only **partially** reversed — enough for rect/tint/same-length-string edits, not yet for confident structural insertion.

---

## THE governing constraint — the same-size rule

**Every member of a mod-shipped `CONFIG.MEG` must keep its EXACT original byte size, or ClientG crashes at boot** (twice-Deck-proven in `config-meg-mod-delivery.md`; the crash is an `ACCESS_VIOLATION` that misleadingly names an innocent *downstream* member — a stale-offset symptom). For `.bui` this means:

1. Keep the **decompressed length constant** — edit floats/flags in place and swap strings for **equal-length** strings; never add/remove payload bytes.
2. Recompress at **zlib level 9** (base files are ~level-6, so re-editing at level 6 routinely *grows* the stream; L9 buys headroom). Assert the new compressed stream is **≤ the original compressed size**.
3. **Pad the file back to the exact original member size** with trailing `0x00`. The loader reads only `csize` bytes, so the pad is ignored (verified: our shipped 5274-byte `RA_MAIN_MENU.BUI` is base-size with trailing pad, over a same-length edited payload).

Consequences:
- Big/compressible screens have generous pad budgets (map-select ~316 B, tactical HUD ~421 B). Tiny files have almost none — `BUTTONFACTIONCOMBOBOX.BUI` has only ~3 B of L9 headroom, so it is nearly unmoddable even for same-length edits.
- **Structural growth is impossible** — a new widget/row grows the payload past the cap, so it cannot use the pad path at all. This is the hard wall against "add an option."

---

## The pipeline (proven) — how we already do it

`scripts/bui_mainmenu_build.py` is the worked, shipping example (removes START NEW GAME, promotes MISSION SELECT, closes the gap). `scripts/build_config_meg.sh` orchestrates: rebuild the edited `.bui` + `GAMECONSTANTS.XML` from pristine bases, then `scripts/meg_pack.py repack` them into the mod's `CONFIG.MEG` (replace-only, rebuilds offsets), then verify the repacked member byte-matches. General recipe for a new edit:

```
1. meg_extract.py extract <base>/Data/CONFIG.MEG <NAME>.BUI out/     # pristine base member
2. d = open(member,'rb').read();  raw = bytearray(zlib.decompress(d[0x24:]))
3. edit raw IN PLACE  (rect '02 10' floats / tint '03 10' floats / equal-length string swaps)
4. comp = zlib.compress(bytes(raw), 9)                              # level 9, not 6
5. assert len(comp) <= (len(d) - 0x24)                              # must fit under original
6. hdr = bytearray(d[:0x24]); struct.pack_into('<I', hdr, 0x10, len(comp))   # keep [0x08] hash stale
7. body = bytes(hdr)+comp;  out = body + b'\x00'*(len(d)-len(body)) # pad to EXACT original size
8. meg_pack.py repack a COPY of the mod CONFIG.MEG, "<NAME>.BUI=out"; verify member size == original AND total MEG size == base
9. ship that CONFIG.MEG in the mod
```

Always edit from the **pristine base** member and re-derive offsets against expected values (the base can shift between game patches) — `bui_mainmenu_build.py` asserts a table of expected rects for exactly this reason.

---

## What it unlocks — the wall map (W1–W5)

| Wall | Verdict | Why |
|---|---|---|
| **W1 Allied/Soviet picker emblems** | **PARTIAL / weak** | Can retexture existing combo/listbox widgets and repoint `FACTIONS.XML SmallIconName` at **already-preloaded** regions. Cannot supply **new emblem pixels** (front-end custom textures resolved-negative — `front-end-texture-meg-spike.md`). "Add a hidden widget to force-preload `UI_SIDEBAR_FACTIONLOGO_*` then repoint" needs payload growth → blocked by same-size rule + startup-crash risk. |
| **W2 genuine 5th faction slot** | **DEAD** | `FactionType` is a compiled C++ enum in ClientG; the faction listbox is code-populated keyed by it. No data/`.bui`/script can mint an enum value. |
| **W3 campaign / map-select UI** | **PARTIAL (cosmetic only)** | Can restyle/reposition/retexture `CNC_MAPSELECT` / `RA_CAMPAIGN_SELECT`. The real prize — a selectable, *playable* GDI/Nod campaign — is DEAD on a separate wall: missions are `ExternalGameID=TiberianDawn` and the roster comes from compiled `TypeManager<CampaignMapSelectMapClass>`. `.bui` only restyles the screen. See `campaign-tabs-research.md`. |
| **W4 in-game tactical HUD** | **PROVEN LIVE (2026-07-11) — but per-faction logos DEAD (2026-07-12)** | Cosmetic edits (reposition/retint/hide/retexture) of existing HUD widgets are real and shippable, and structural widget insertion now works too (format cracked — see the RESOLVED NEGATIVE section). But **per-faction GDI/Nod crests are engine-walled**: ClientG's compiled mapping sends all RA Allied-side countries (incl. our GDI=Spain, Nod=Turkey) to `SideBar_FactionLogo_Allies` and Soviet-side to `_Soviet`; `_GDI`/`_NOD` are TD-mode-only lookups. HUD identity via `.bui` is limited to **side-level or mod-wide** styling. Builder: `scripts/bui_work/faction_logos_build.py`. |
| **W5 `a` / `/` select-all/deploy hotkey classification** | **DEAD** | Hardcoded in ClientG (`RTSInputManagerClass`, registered-type identity); not expressed in any `.bui` or shipped script. Per-frame export spoofs already Deck-proven no-op. |

**The line to remember:** cosmetic reshape of existing widgets = reachable; new options/structure = not.

### ClickScript / Lua

ClientG embeds a ClickScript bytecode VM and a full Lua (pglua) VM, and there's a `SERVER_TO_CLIENT_CLICK_SCRIPT_EVENT`. This is a **behaviour** layer, but: it is not a DLL lever (our CNC callback has no clickscript member — host-originated only), and list/roster population that we'd want to change is compiled-C++, not script-driven. Treat scripting as out of reach for our goals until a specific, evidence-backed need appears. (Not fully mapped — the one remaining thread if shell-*behaviour* ever becomes a target.)

---

## Risks & the safe-edit envelope

- **Boot crash on size change** is the dominant risk — never let a member's outer byte size drift from base. The pad-to-exact-size step is mandatory.
- **Recompress overflow** — if `len(comp) > original_csize` you cannot pad down; rework/shrink the edit. Thin budgets on small files.
- **Structural corruption** — unbalanced/over-deep chunks trip ChunkFile's depth/close guards → load abort. Don't restructure; edit in place.
- **Safe envelope** = same-decompressed-length only: in-place rect/tint float overwrites at verified `02 10`/`03 10` tags, 1-byte flag flips, and equal-length ASCII string swaps. Length-changing string edits require patching the local `u16` length prefix **and** any enclosing chunk-size field — traceable but not zero-risk given the partial grammar.
- **Residual uncertainty (now small):** the main-menu artifact proves pad-tolerance + same-size-safety **for a `.bui`**, so the earlier "Deck-unconfirmed" caveats are largely retired. What remains unproven is that *other* screens (HUD/map-select) render correctly in-context after a same-size edit — mechanically identical to the proven case, but not yet observed.

---

## Cheapest way to prove W4 (HUD) generalizes

The main-menu case already proves the pipeline. To confirm it extends to the in-game HUD, a **ready-to-run probe is built and validated**: `scripts/bui_work/hud_probe_build.py` produces `scripts/bui_work/CONFIG.hud-probe.MEG` (a copy of the mod's `CONFIG.MEG` with one same-length swap in `RA_TACTICAL_UI.BUI`: `ui_sidebar_factionlogo_allies` → `ui_sidebar_factionlogo_soviet`, equal length = zero size risk). It self-validates the whole round-trip (member size unchanged, payload length unchanged, MEG size unchanged, swap applied). To run the probe:

1. `python3 scripts/bui_work/hud_probe_build.py`  → regenerates + validates the probe MEG (44 MB, gitignored).
2. `scp` it to the Deck mod folder's `Data/CONFIG.MEG` (deploy command is in the script's docstring).
3. Launch a skirmish **as GDI** (an Allied-based faction) and look at the sidebar crest.

Interpretation: crest shows the Soviet/Nod logo = **W4 proven end-to-end**. No change = wrong member/delivery. Boot crash = size drift (shouldn't happen for a same-length edit). Recovery: redeploy the mod's unmodified `CONFIG.MEG` (command in the docstring). **The base install is never touched.** This is a probe, not a feature — revert after observing.

---

## Per-faction HUD logos — RESOLVED NEGATIVE (2026-07-12). Do not re-chase.

**Verdict: per-faction sidebar crests for GDI/Nod are engine-walled in RA mode.**
ClientG's compiled FactionType→logo-widget mapping collapses ALL RA countries to
the two side widgets — `SideBar_FactionLogo_Allies` for Allied-side countries
(incl. Spain = our GDI and Turkey = our Nod) and `_Soviet` for Soviet-side. The
`_GDI`/`_NOD` widget names (present in ClientG, exact-match verified by strings)
are only queried for the TD FactionTypes (Faction1/Faction2), which the RA lobby
can never produce (the W2 wall). The mod's shipped all-factions
"COMMAND & CONQUER" wordmark is the correct end state.

**Discriminator probe that proved it (Linux, 2026-07-12):** `_Allies` widget
retextured to the GDI eagle; structurally-valid `_GDI`/`_NOD` widgets inserted
(cracked format, unique instance IDs — see below) pointing at the Nod scorpion.
Result: GDI, Nod, AND Allies all showed the eagle (→ all resolve to `_Allies`);
Soviets showed the wordmark (→ `_Soviet`); the scorpion never appeared (→
`_GDI`/`_NOD` never queried). This also retro-explains the 2026-07-11 "hide
`_Allies` changed nothing" puzzle only partially — those offsets were misaligned
mid-node (see next section); trust only the 2026-07-12 probe.

**What the chase yielded anyway (both real capabilities):**
1. **The chunk grammar is fully cracked** — `node = [u32 id][u32 spec]`, spec
   MSB set → container holding `spec & 0x7fffffff` CHILD NODES (a count, not a
   byte size); else leaf of `spec` data bytes. Validated by exact full-file
   parse of `RA_TACTICAL_UI.BUI` (6,497 nodes). Widget elements are
   `C id=1 cnt=2` subtrees; each widget's first micro-chunk (`01 04 <u32>`) is a
   per-instance unique ID (serialized pointers — monotonic in file order, no
   cross-references in the payload).
2. **Structural widget insertion WORKS** (revising this doc's earlier "cannot
   add widgets" claim): copy a complete element subtree, rewrite its string
   leaves (u32 size + u16 len prefixes), give it a fresh unique ID, insert as a
   sibling, and bump the direct parent's child count — the tree parses and the
   HUD renders normally with the extra widgets present (Linux-verified; they
   were simply never *queried* for this use case). The same-size compressed
   budget still applies. Builder/worked example:
   `scripts/bui_work/faction_logos_build.py`. What remains impossible is making
   the ENGINE use new widgets it has no compiled lookup for — walls W2/W5
   unchanged.

## Per-faction HUD logos — the original structural-add WIP (2026-07-11, superseded by the above)

**Goal:** 4 distinct radar-splash logos, one per faction (Allied / GDI / Nod / Soviet). This is the frontier case — it needs a **structural add** (new widgets), not just in-place edits.

**What we discovered:**
- ClientG selects the sidebar logo by widget **name**, keyed on the compiled `FactionType` enum, and looks for **five** names: `SideBar_FactionLogo_{GDI,NOD,Allies,Soviet,DINO}`. `RA_TACTICAL_UI.BUI` only *defines* `_Allies` and `_Soviet`, so GDI/Nod fall back to the generic "COMMAND & CONQUER" wordmark. **The engine has GDI/Nod logo slots that were never populated.**
- The **real emblems already ship** in the mod's in-game atlas: regions `ui_sidebar_factionlogo_gdi` (gold eagle) and `_nod` (red scorpion), untouched from base TD art. New widgets just point at them (tint 1,1,1,1) → authentic art, no new pixels. (Only the Allies/Soviet atlas regions were overwritten by the mod with the wordmark.)
- `.bui` string property layout: `[u32 fieldsize = len+2][u16 len][ascii]`. Widget header = `26 10` + 16 zero bytes + `2b 01 01` + `2c 01 01` + `05 00 00 00` (05 = property count). No per-widget total-size field. Duplicating a widget block is well-defined; the `26 10` headers are identical between widgets (no unique per-widget ID → no collision).

**The attempt (`scripts/bui_work/faction_logos_build.py`):** duplicate the `_Allies` block twice → `_GDI`/`_NOD` pointing at the real emblems, retint `_Allies` blue / `_Soviet` orange, insert the 2 blocks (+602 B) before the `RadarMap` widget. Builds cleanly, fits the budget (10725 ≤ 11071), MEG size preserved.

**The failure (Deck-tested, GDI):** the **entire in-game sidebar disappeared** — the tactical view rendered full-screen with no sidebar. **No crash** (graceful degrade). Diagnosis: a **parent chunk bounds its children by a size/count field**; inserting 602 bytes without updating it made ChunkFile mis-parse the rest of `Side_Bar_Group` and drop it.

**The one missing piece for next session:** find the parent chunk enclosing the faction-logo group (candidates: `Side_Bar_Group` @864, `AspectRatio_Group`, `Tactical_UI`) and update its **size and child-count** field(s) by the inserted byte count (+2 children), then re-test. Once the sidebar renders, we also confirm the **faction→widget mapping** (open puzzle: an earlier hide-test showed the `_Soviet` edit affected only Soviet, but the `_Allies` edit affected *nothing* — so it's unconfirmed that the mod's Allies faction resolves to `_Allies`, or GDI/Nod to `_GDI`/`_NOD`). Resolve that via the DLL `FactionType`/`FACTIONS.XML` mapping. The RE workflow (`bui-add-faction-logos`) was rate-limited mid-run — its `chunkfile-insertion-format` and `faction-to-widget-mapping` agents should be re-run first (subagent session limit reset ~21:30 Europe/London on 2026-07-11).

**Confirmed en route:** in-place retints and hide edits on the HUD render live (this is how W4 was proven); structural insertion is safe to iterate (fails graceful, no crash); recovery = restore the mod's `CONFIG.MEG`.

## Related docs

- `config-meg-mod-delivery.md` — the `CONFIG.MEG` shadow delivery + the same-size rule this depends on.
- `faction-select-identity.md` — the `FACTIONS.XML`/master-text faction-picker edits shipped alongside the `.bui` edits.
- `launcher-vs-dll-ownership.md` / [[spike-launcher-process-model]] — why this is a data avenue and the DLL can't reach the front-end.
- `front-end-texture-meg-spike.md` — why new front-end *pixels* aren't deliverable (bounds W1).
- `ui-atlas-modding.md` — the in-game atlas (loose-override) surface, distinct from `.bui`.
- `campaign-tabs-research.md` — why W3's playable-campaign prize is engine-walled.
- Scripts: `scripts/bui_mainmenu_build.py` (worked example), `scripts/build_config_meg.sh`, `scripts/meg_pack.py`, `scripts/meg_extract.py`.
