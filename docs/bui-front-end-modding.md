# .bui front-end UI modding — the ChunkFile scene-graph layer

**Status:** Reference. Editing the launcher's `.bui` screens inside CONFIG.MEG.

The launcher's screens are `.bui` ChunkFile scene graphs in the mod's CONFIG.MEG. The mod ships
edits to the main menu, dialog, loading screen, lobbies, faction combo box, tactical HUD and font
library, built by `scripts/build_config_meg.sh` through `scripts/bui_tree.py` and the
`scripts/bui_*_build.py` builders. Edits reshape, retint, retexture or extend existing widgets
within the member's size. Data alone cannot add options or behaviour ClientG has no code for; new
buttons and screens ship by pairing cloned widgets with launcher code from the DLL (`pack-panel.md`).
A `.bui` is data read by `ClientG.exe` at load, so the sim never touches it (`launcher-vs-dll-ownership.md`).

The format, what data can do and how to edit safely are on the field manual's
[BUI screens](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/bui-screens.md);
new buttons and screens are on its
[New screens and buttons](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/new-screens-and-buttons.md).

- TF's main-menu reorder ships, and a hide edit on `RA_TACTICAL_UI.BUI`'s Soviet faction-logo rect removed that
  logo live in a skirmish. The main menu's ADD-ONS button is a cloned widget whose click the DLL's launcher layer
  binds; it opens `TF_ADDONS.BUI` under ClientG's unused `SplashScreen` class (`pack-panel.md`).
- `.bui` editing is a polish and faction-identity capability, not a feature unlock. Factions and campaigns came by
  other routes (`ts-gdi-faction.md`, `campaign-tabs-research.md`).

## The format

The header and the node grammar are on the manual's
[The format](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/bui-screens.md#the-format).
Details it lacks:
- the version at `0x02` is checked against an allowlist of {2.0, 2.1}; bytes `0x05`-`0x07` are `ff ff ff`, `0x0C`
  holds the compression-type dword, 8 (bytes `08 00 00 00`), and `0x14`-`0x23` are 16 zero bytes;
- ClientG's `ChunkFile::ChunkFileReaderClass` load path (constructor near `0x98ba30`, `Read_Header` at `0x993f90`)
  validates only the magic and the version. The `0x08` dword is read into the reader and at most used as an offset
  to an optional trailing section that UI `.bui` files don't have. The only tamper checks are structural
  (`Open_Chunk`/`Close_Chunk` balance and `MAX_CHUNK_DEPTH`, reported as "Probable corrupted/tampered file") plus
  zlib's own adler32. The hash algorithm is uncracked and not load-bearing; TF's `RA_MAIN_MENU.BUI` keeps the
  stock hash `fb5deab3`;
- the network layer's `PG::ContainerClass::read(... ComSecurityContext ...)` with Sosemanuk and HMAC is the
  encrypted socket between InstanceServer and ClientG (`launcher-vs-dll-ownership.md`, "The process model"), not
  the `.bui` format. The `.bui` and `CONFIG.MEG` path has no encryption and no content hash.

### The scene graph

The widget header tag is `26 10`. `scripts/bui_work/hud_label_hide_build.py` hides the country name under the crest
(`Text_FactionSelected`): its own tint is the `03 10` just before its header, alpha 0.58. Zeroing the tint after
`Text_FactionSelected` instead hid the Allied logo, the next widget.

Widget elements are `C id=1 cnt=2` subtrees. Each widget's per-instance ID (`01 04 <u32>`) is a serialized pointer,
monotonic in file order, with no cross-references in the payload. A string leaf carries a u32 size and a u16 length
prefix; texture-set names are micro-chunks inside a header leaf (`0f <size> <u16 len>`), and `replace_texture_set`
rewrites one and its leaf's size.

The broader property vocabulary seen in scene graphs (especially `RA_TACTICAL_UI.BUI`): `POSITION SIZE TINT TEXTURE
RENDER_MODE ROTATION HIDDEN ALPHA POSX POSY SIZEX SIZEY TELETYPE BRIGHTNESS LINE_WIDTH OFFSETV REPEATV TEXSIZEV`,
plus groups (`AspectRatio_Group`) and animation states (`SlideIn`/`SlideOut`). The per-widget property grammar is
mapped only for rects, tints, strings, texture sets and whole cloned subtrees.

## The same-size rule

The rule and how a `.bui` keeps it are on the manual's
[Editing safely](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/bui-screens.md#editing-safely);
a loose copy may be any size (`campaigns-page.md`). The crash is in `config-meg-mod-delivery.md`. The loader reads
only the compressed length's bytes, so the pad is ignored: TF's shipped `RA_MAIN_MENU.BUI` is 5,274 bytes, base size,
with a trailing pad.

- Big, compressible screens have generous pad budgets (map-select about 316 B, tactical HUD about 421 B). Tiny files
  have almost none (`BUTTONFACTIONCOMBOBOX.BUI` about 3 B, `UI_CUSTOM_MAP_FILE_ENTRY.BUI` 0 B): float edits and
  shorter strings still fit, and emptying placeholder text the launcher overwrites frees more ("Screens, text and
  motion" below).
- **Growth is fine while it compresses under the cap.** A longer string, an extra leaf or a whole appended node is
  safe if the recompressed stream still fits the file's size. `scripts/bui_tree.py` parses the tree, lets you edit
  nodes, and writes it back at the base's size; containers count children, so only the edited leaf's size changes.
  A large addition (a whole new screen section) won't fit.

## The pipeline

`scripts/bui_mainmenu_build.py` is the worked, shipping example (removes START NEW GAME, promotes MISSION SELECT,
closes the gap). `scripts/build_config_meg.sh` orchestrates: rebuild the edited `.bui` and `GAMECONSTANTS.XML` from
pristine bases, then `scripts/meg_pack.py repack` them into the mod's `CONFIG.MEG` (replace-only, rebuilds offsets),
then verify the repacked member byte-matches. The recipe for a new byte-level edit:

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

Newer builders (`bui_dialogbox_build.py`, `bui_loadingscreen_build.py`, `bui_lobby_build.py`, `fontlib_build.py`)
use `scripts/bui_tree.py` instead of byte offsets: `load(base)`, edit nodes (`headers()` finds a widget by name,
`micro_floats()` its rect or tint, `replace_texture_set()` a set name), then `write_same_size(...)`.
`bui_mainmenu_build.py` asserts a table of expected rects, so it stops if the base ever shifts.

The safe envelope: edits through `bui_tree.py` (or in-place float and flag overwrites at verified `02 10`/`03 10`
tags), string leaves changing length, leaves added to a container (its count follows), and a result that recompresses
under the base's size. If the recompressed stream overflows, shrink the edit: it can't be padded down. Same-size edits
are proven in play on the main menu, dialog box, loading screen, lobbies, faction combo box, font library and
tactical HUD.

## What it unlocks: the wall map (W1–W5)

| Wall | Verdict | Why |
|---|---|---|
| **W1 picker emblems** | **Solved, not by `.bui`** | The loose atlas repaints the preloaded slot icons ([The UI atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#pick-the-right-region); `faction-select-identity.md`, `ui-atlas-modding.md`). |
| **W2 genuine new faction slot** | **DEAD** | `FactionType` is a compiled C++ enum in ClientG; the faction listbox is code-populated keyed by it. No data, `.bui` or script can mint an enum value. TS GDI is a fifth faction without one: it reuses the Germany country slot and decouples that house DLL-side (`ts-gdi-faction.md`). The 8 country slots are the ceiling. |
| **W3 campaign / map-select UI** | **Cosmetic only** | `.bui` can restyle, reposition and retexture `CNC_MAPSELECT` / `RA_CAMPAIGN_SELECT`; the roster comes from compiled `TypeManager<CampaignMapSelectMapClass>` and `INSTANCES.XML`. Campaign missions are delivered by hijacking an existing Counterstrike or Aftermath slot (`campaign-tabs-research.md`). |
| **W4 in-game tactical HUD** | **Solved by data** | `FACTIONS.XML` scene lists: GDI, Nod and TS GDI load TD's `Tactical_UI.bui`, RA sides keep `RA_Tactical_UI.bui` with the side label hidden (`hud_label_hide_build.py`, `faction-select-identity.md`). Per-faction crests in RA's scene need the RAM patch, not `.bui` (below). |
| **W5 `a` / `/` select-all/deploy classification** | **Solved on the DLL side, not via `.bui`** | Hardcoded in ClientG (`RTSInputManagerClass`); see [Launcher key commands and superweapon clicks](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/launcher-key-commands-and-clicks.md). The DLL reads the keys and filters the select-all hand-over (`launcher-vs-dll-ownership.md`). |

**The line to remember:** reshaping, retexturing and recolouring existing widgets, and adding nodes the launcher
already reads (effects, font styles), is reachable by data; new options or behaviour the launcher has no code for
need launcher code patched in from the DLL (`pack-panel.md`).

### ClickScript and Lua

The embedded interpreters and the missing `.lua` files are on the manual's
[How to tell who owns a behaviour](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#how-to-tell-who-owns-a-behaviour).
Details it lacks: the ClickScript interpreter is a bytecode VM and the Lua a full VM (pglua); there is a
`SERVER_TO_CLIENT_CLICK_SCRIPT_EVENT`, but it is host-originated only (the DLL's
callback has no clickscript member), and the list and roster population TF would want to change is compiled C++,
not script-driven. Every keyframe animation in a shipping `.bui` is started by name from ClientG. Scripting stays out
of reach until a specific need appears; it is the one unmapped thread if shell behaviour ever becomes a target.

## Screens, text and motion

- **Which screen opens is data:** see the manual's
  [Where screens live, and which one opens](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/bui-screens.md#where-screens-live-and-which-one-opens).
  `factions_build.py` FRONT_END points each key at TD's screen name (no `RA/` prefix), swapping the skirmish lobby,
  LAN lobby, LAN match list and Workshop browser for TD's.
- **Text colour:** `FONTLIBRARY.BFD`'s styles are on the manual's The format. Each style is a top-level node
  `[name, font face, properties]`, its colour the properties' `0b 10` RGBA (`fontlib_build.py`, which appends G16,
  G18, G18R and G15R, each a copy of a white stock style in the menu labels' green). The text widgets the launcher recolours include `Combo_Text` and `Map_Name_Text`, so a tint doesn't
  hold there: use a coloured style.
- **Bytes:** placeholder text the launcher overwrites (`Player_Name`, `A Path Beyond`, the dialog caption) can be
  emptied to free room in tiny files. Pure (0, 1, 0) tints compress best.
- **Motion:** the loading spinner is a fixed 4×4 grid at 24 fps (0.67 s loop). Keyframe animations play only when
  ClientG starts them by name (the manual's Traps). GUIEFFECTS sheens attach with an `id 0x16` leaf and loop by
  themselves. The fullscreen variant (`Logo_Sheen`) multiplies the widget's alpha by the texture's and adds its
  colour.
- **Atlas plates:** TD's lobby fills are about 10% alpha, and plates show about 1.47× brighter in game than their
  texture values (`lobby_art.py`).

## Combo-box drop-downs: mouse area and row height

The mouse area and the row height are on the manual's
[Traps](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/bui-screens.md#traps).
`bui_lobby_build.py slot_room` grows a lobby slot's `PlayerFactionGroup` (and, if needed, its
`Slot_Content_Group`). Growing the combo grows the rows unless the row height is scaled down to match. Property names
come from Petroglyph's 9-Bit Armies GUI editor (`ModTools/GUIEditor`: `GUI_LIST_BOX_ROW_HEIGHT_MICRO_CHUNK`,
`GUI_COMBO_BOX_MAX_ITEMS_SHOWN_CHUNK`, `GUI_COMBO_BOX_OPEN_UP_MICRO_CHUNK`), which reads the same chunk format.

## Per-faction logos in RA's HUD scene: not reachable by `.bui`

See the manual's
[What you can do](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/bui-screens.md#what-you-can-do).
ClientG maps every RA country to `SideBar_FactionLogo_Allies` or `_Soviet` by side. The `_GDI`/`_NOD` names are
looked up only for the TD FactionTypes (Faction1/Faction2), which the RA lobby can never produce (W2). Per-faction
crests come from TD's scene plus the RAM patch instead (`radar-crest-ram-spike.md`).

The probe that shows it: the `_Allies` widget retextured to the GDI eagle, and structurally valid `_GDI`/`_NOD`
widgets inserted pointing at the Nod scorpion. GDI, Nod and Allies all showed the eagle (all resolve to `_Allies`),
Soviets showed the wordmark (`_Soviet`), and the scorpion never appeared (`_GDI`/`_NOD` are never queried). The
inserted widgets parsed and the HUD rendered normally with them present.
`scripts/bui_work/faction_logos_build.py` is the worked example of structural insertion.

## Related docs

- `config-meg-mod-delivery.md`: the `CONFIG.MEG` shadow delivery and the same-size rule this depends on.
- `faction-select-identity.md`: the `FACTIONS.XML` and master-text faction-picker edits shipped alongside the `.bui`
  edits.
- `launcher-vs-dll-ownership.md`: the four levers that reach launcher-owned behaviour; `.bui` is the data one.
- `ui-atlas-modding.md`: the in-game atlas (loose-override) surface, distinct from `.bui`, and the dead
  texture-MEG route.
- `campaign-tabs-research.md`: how campaign missions are delivered (W3).
- Scripts: `scripts/bui_mainmenu_build.py` (worked example), `scripts/build_config_meg.sh`, `scripts/meg_pack.py`,
  `scripts/meg_extract.py`.
