# .bui front-end UI modding — the ChunkFile scene-graph layer

**Status:** Reference. Editing the launcher's `.bui` screens inside CONFIG.MEG.

The launcher's screens are `.bui` ChunkFile scene graphs in the mod's CONFIG.MEG. The mod ships
edits to the main menu, dialog, loading screen, lobbies, faction combo box, tactical HUD and font
library, built by `scripts/build_config_meg.sh` through `scripts/bui_tree.py` and the
`scripts/bui_*_build.py` builders. Edits reshape, retint, retexture or extend existing widgets
within the member's size; they cannot add options or behaviour ClientG has no code for.

**One-line:** `.bui` = a Petroglyph **ChunkFile** container (`CH` magic + zlib) wrapping a tag-based UI scene graph. It is **data**, delivered through the `CONFIG.MEG` shadow and read by `ClientG.exe` at load, so the sim never touches it (`launcher-vs-dll-ownership.md`).

---

## TL;DR — what this buys us (and what it doesn't)

- **YES — cosmetic reshape of EXISTING widgets** on any front-end/HUD screen: reposition, resize, hide/show, retint, retexture and restyle text (strings may change length), plus nodes the launcher already reads (effects, font styles). Whole front-end screens can be swapped for TD's through `FACTIONS.XML` (2026-10-01 section). **Proven on both surfaces:** the front-end (main-menu reorder ships in production) **and** the in-game HUD (Deck-confirmed 2026-07-11 — a hide edit on `RA_TACTICAL_UI.BUI`'s Soviet faction-logo rect removed that logo live in a skirmish).
- **NO — adding new options or behaviour.** The things we'd *want* to add are code-populated from compiled C++ enums/type-managers in `ClientG.exe`, not from `.bui` data. (Payload growth itself is fine while it recompresses under the file's size.)
- Treat this as a **polish / faction-identity** capability, not a feature unlock. Factions and campaigns came by other routes (`ts-gdi-faction.md`, `campaign-tabs-research.md`).

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
- **A widget's rect and tint tags come BEFORE its `26 10` header + name.** The tags that follow a
  name belong to the NEXT widget. (2026-09-02: zeroing the tint after `Text_FactionSelected`
  hid the Allied logo; the label's own tint is the `03 10` just before its header, alpha 0.58.)
  Shipped hide: `scripts/bui_work/hud_label_hide_build.py` (the country name under the crest).

The broader property vocabulary seen in scene graphs (esp. `RA_TACTICAL_UI.BUI`): `POSITION SIZE TINT TEXTURE RENDER_MODE ROTATION HIDDEN ALPHA POSX POSY SIZEX SIZEY TELETYPE BRIGHTNESS LINE_WIDTH OFFSETV REPEATV TEXSIZEV`, plus groups (`AspectRatio_Group`) and animation states (`SlideIn`/`SlideOut`). The full per-widget grammar is only **partially** reversed — enough for rect/tint/same-length-string edits, not yet for confident structural insertion.

---

## THE governing constraint — the same-size rule

**Every member of a mod-shipped `CONFIG.MEG` must keep its EXACT original byte size, or ClientG crashes at boot** (twice-Deck-proven in `config-meg-mod-delivery.md`; the crash is an `ACCESS_VIOLATION` that misleadingly names an innocent *downstream* member — a stale-offset symptom). For `.bui` this means:

1. Keep the **decompressed length constant** — edit floats/flags in place and swap strings for **equal-length** strings; never add/remove payload bytes.
2. Recompress at **zlib level 9** (base files are ~level-6, so re-editing at level 6 routinely *grows* the stream; L9 buys headroom). Assert the new compressed stream is **≤ the original compressed size**.
3. **Pad the file back to the exact original member size** with trailing `0x00`. The loader reads only `csize` bytes, so the pad is ignored (verified: our shipped 5274-byte `RA_MAIN_MENU.BUI` is base-size with trailing pad, over a same-length edited payload).

Consequences:
- Big/compressible screens have generous pad budgets (map-select ~316 B, tactical HUD ~421 B). Tiny files have almost none (`BUTTONFACTIONCOMBOBOX.BUI` ~3 B, `UI_CUSTOM_MAP_FILE_ENTRY.BUI` 0 B): float edits and shorter strings still fit, and emptying placeholder text the launcher overwrites frees more (see the 2026-10-01 section).
- **Growth is fine while it compresses under the cap.** A longer string, an extra leaf or a whole appended node is safe if the recompressed stream still fits the file's size. `scripts/bui_tree.py` parses the tree, lets you edit nodes, and writes it back at the base's size; containers count children, so only the edited leaf's size changes. A large addition (a whole new screen section) still won't fit.

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

Newer builders (`bui_dialogbox_build.py`, `bui_loadingscreen_build.py`, `bui_lobby_build.py`, `fontlib_build.py`) use `scripts/bui_tree.py` instead of byte offsets: `load(base)`, edit nodes (`headers()` finds a widget by name, `micro_floats()` its rect or tint, `replace_texture_set()` a set name), then `write_same_size(...)`.

Always edit from the **pristine base** member and re-derive offsets against expected values (the base can shift between game patches) — `bui_mainmenu_build.py` asserts a table of expected rects for exactly this reason.

---

## What it unlocks — the wall map (W1–W5)

| Wall | Verdict | Why |
|---|---|---|
| **W1 picker emblems** | **Solved, not by `.bui`** | `FACTIONS.XML` `SmallIconName` can point only at preloaded regions, and the loose atlas repaints their pixels (`faction-select-identity.md`, `ui-atlas-modding.md`). |
| **W2 genuine new faction slot** | **DEAD** | `FactionType` is a compiled C++ enum in ClientG; the faction listbox is code-populated keyed by it. No data, `.bui` or script can mint an enum value. TS GDI is a fifth faction without one: it reuses the Germany country slot and decouples that house DLL-side (`ts-gdi-faction.md`). The 8 country slots are the ceiling. |
| **W3 campaign / map-select UI** | **Cosmetic only** | `.bui` can restyle, reposition and retexture `CNC_MAPSELECT` / `RA_CAMPAIGN_SELECT`; the roster comes from compiled `TypeManager<CampaignMapSelectMapClass>` and `INSTANCES.XML`. Campaign missions are delivered by hijacking an existing Counterstrike or Aftermath slot (`campaign-tabs-research.md`). |
| **W4 in-game tactical HUD** | **Solved by data** | `FACTIONS.XML` scene lists: GDI, Nod and TS GDI load TD's `Tactical_UI.bui`, RA sides keep `RA_Tactical_UI.bui` with the side label hidden (`hud_label_hide_build.py`, `faction-select-identity.md`). Cosmetic edits and structural widget insertion both work, but in RA's scene ClientG maps every Allied-side country to `SideBar_FactionLogo_Allies` and every Soviet-side one to `_Soviet`, so per-faction crests there need the RAM patch, not `.bui` (below). |
| **W5 `a` / `/` select-all/deploy classification** | **Solved on the DLL side, not via `.bui`** | Hardcoded in ClientG (`RTSInputManagerClass`, registered-type identity); the DLL reads the keys and filters the select-all hand-over (`launcher-vs-dll-ownership.md`). |

**The line to remember:** reshaping, retexturing and recolouring existing widgets, and adding nodes the launcher already reads (effects, font styles), is reachable; new options or behaviour the launcher has no code for is not.

### ClickScript / Lua

ClientG embeds a ClickScript bytecode VM and a full Lua (pglua) VM, and there's a `SERVER_TO_CLIENT_CLICK_SCRIPT_EVENT`. This is a **behaviour** layer, but: it is not a DLL lever (our CNC callback has no clickscript member — host-originated only), and list/roster population that we'd want to change is compiled-C++, not script-driven. Treat scripting as out of reach for our goals until a specific, evidence-backed need appears. (Not fully mapped — the one remaining thread if shell-*behaviour* ever becomes a target.) No `.lua` ships in any MEG (checked 2026-10-01), and every keyframe animation in a shipping `.bui` is started by name from ClientG, so neither is a route to new motion.

## Front-end screens, text and motion (2026-10-01)

- **Which screen opens is data.** The RA front end takes its screens from the Soviet entry (Faction5) `GUIFileNames` in `FACTIONS.XML` (lobbies, LAN, Workshop browser, loading screen, DialogBox…). Pointing a key at TD's screen name (no `RA/` prefix) swaps the whole screen. Proven for the skirmish lobby, LAN lobby, LAN match list and Workshop browser (`factions_build.py` FRONT_END).
- **Text colour:** `FONTLIBRARY.BFD` is a flat list of named styles `[name, face, props]`, colour at `0b 10`. New styles can be appended (`fontlib_build.py`: G16/G18/G18R/G15R). The launcher recolours some text widgets it names (`Combo_Text`, `Map_Name_Text`), so a tint doesn't hold there. Use a coloured style.
- **Bytes:** placeholder text the launcher overwrites (`Player_Name`, `A Path Beyond`, the dialog caption) can be emptied to free room in tiny files. Pure (0, 1, 0) tints compress best.
- **Motion:** the loading spinner is a fixed 4×4 grid at 24 fps (0.67 s loop). Keyframe animations in `.bui` files only play when ClientG starts them by name, and no `.lua` ships. GUIEFFECTS sheens attach with an `id 0x16` leaf and loop by themselves. The fullscreen variant (Logo_Sheen) multiplies the widget's alpha by the texture's and adds its colour.
- **Atlas plates:** TD's lobby fills are about 10% alpha, and plates show about 1.47× brighter in game than their texture values (`lobby_art.py`).

---

## Combo-box drop-downs: mouse area and row height (2026-10-02)

A combo box's list answers the mouse only inside the group that holds the combo (in a lobby slot,
`PlayerFactionGroup` and its siblings). A list stretched past that group draws fine but its lower
rows close the list and take no clicks. The fix is to grow the group (and, if needed, the slot's
`Slot_Content_Group`), scaling the other widgets' y and height so nothing moves on screen
(`bui_lobby_build.py slot_room`). The list's row height is list-box micro-chunk `05` in the list's
property leaf (id 4): a fraction of the **combo's** height (TD 0.1711, RA 0.0975). Grow the combo
and the rows grow with it unless that value is scaled down to match. Property names come from
Petroglyph's 9-Bit Armies GUI editor (`ModTools/GUIEditor` on the M.2:
`GUI_LIST_BOX_ROW_HEIGHT_MICRO_CHUNK`, `GUI_COMBO_BOX_MAX_ITEMS_SHOWN_CHUNK`,
`GUI_COMBO_BOX_OPEN_UP_MICRO_CHUNK`), which reads the same chunk format.

## Risks & the safe-edit envelope

- **Boot crash on size change** is the dominant risk — never let a member's outer byte size drift from base. The pad-to-exact-size step is mandatory.
- **Recompress overflow** — if `len(comp) > original_csize` you cannot pad down; rework/shrink the edit. Thin budgets on small files.
- **Structural corruption** — unbalanced/over-deep chunks trip ChunkFile's depth/close guards → load abort. Don't restructure; edit in place.
- **Safe envelope** = edits through `scripts/bui_tree.py` (or in-place float and flag overwrites at verified `02 10`/`03 10` tags): string leaves may change length, leaves may be added to a container (its count follows), and the result must recompress under the base's size. Texture-set names are micro-chunks inside a header leaf (`0f <size> <u16 len>`); `replace_texture_set` rewrites one and its leaf's size.
- Same-size edits are proven in play on the main menu, dialog box, loading screen, lobbies, faction combo box, font library and tactical HUD.

---

## Per-faction logos in RA's HUD scene: not reachable by `.bui`. Do not re-chase.

**ClientG never queries `SideBar_FactionLogo_GDI` / `_NOD` in RA's scene.** Its compiled
FactionType→logo-widget mapping collapses every RA country to the two side widgets:
`SideBar_FactionLogo_Allies` for Allied-side countries (Spain, Greece and Germany included) and
`_Soviet` for Soviet-side. The `_GDI`/`_NOD` names are looked up only for the TD FactionTypes
(Faction1/Faction2), which the RA lobby can never produce (W2). Per-faction crests come from TD's
scene plus the RAM patch instead (`radar-crest-ram-spike.md`).

**Discriminator probe that proved it (Linux, 2026-07-12):** `_Allies` widget
retextured to the GDI eagle; structurally-valid `_GDI`/`_NOD` widgets inserted
(cracked format, unique instance IDs — see below) pointing at the Nod scorpion.
Result: GDI, Nod, AND Allies all showed the eagle (→ all resolve to `_Allies`);
Soviets showed the wordmark (→ `_Soviet`); the scorpion never appeared (→
`_GDI`/`_NOD` never queried).

**What the chase yielded anyway (both real capabilities):**
1. **The chunk grammar is fully cracked** — `node = [u32 id][u32 spec]`, spec
   MSB set → container holding `spec & 0x7fffffff` CHILD NODES (a count, not a
   byte size); else leaf of `spec` data bytes. Validated by exact full-file
   parse of `RA_TACTICAL_UI.BUI` (6,497 nodes). Widget elements are
   `C id=1 cnt=2` subtrees; each widget's first micro-chunk (`01 04 <u32>`) is a
   per-instance unique ID (serialized pointers — monotonic in file order, no
   cross-references in the payload).
2. **Structural widget insertion works:** copy a complete element subtree, rewrite its string
   leaves (u32 size + u16 len prefixes), give it a fresh unique ID, insert as a
   sibling, and bump the direct parent's child count — the tree parses and the
   HUD renders normally with the extra widgets present (Linux-verified; they
   were simply never *queried* for this use case). The same-size compressed
   budget still applies. Builder/worked example:
   `scripts/bui_work/faction_logos_build.py`. What remains impossible is making
   the ENGINE use new widgets it has no compiled lookup for — walls W2/W5
   unchanged.

## Related docs

- `config-meg-mod-delivery.md` — the `CONFIG.MEG` shadow delivery + the same-size rule this depends on.
- `faction-select-identity.md` — the `FACTIONS.XML`/master-text faction-picker edits shipped alongside the `.bui` edits.
- `launcher-vs-dll-ownership.md` — the four levers that reach launcher-owned behaviour; `.bui` is the data one.
- `ui-atlas-modding.md` also records the dead texture-MEG route; front-end pixels ship as loose files.
- `ui-atlas-modding.md` — the in-game atlas (loose-override) surface, distinct from `.bui`.
- `campaign-tabs-research.md` — how campaign missions are delivered (W3).
- Scripts: `scripts/bui_mainmenu_build.py` (worked example), `scripts/build_config_meg.sh`, `scripts/meg_pack.py`, `scripts/meg_extract.py`.
