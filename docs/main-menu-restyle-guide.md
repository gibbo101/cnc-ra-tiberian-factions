# How to restyle the Red Alert Remastered main menu

This is how Tiberian Factions replaced Red Alert's main menu in C&C Remastered: new background
art, a new title logo, a steel menu box with steel buttons and green labels, a reordered button
list, and a recoloured sheen and glow. All of it is plain data. It needs no DLL, no EMC and no
change to the base install, and it is only live while your mod is enabled.

The scripts named below are in this repo's [`scripts/`](../scripts) folder and are GPL v3, so take
whatever helps. They are Python 3 (Pillow and numpy) and were run on Linux; the Tools section
lists the one path to change on Windows.

## What you can and can't change

You can:
- replace any image the menu draws: background, title, radar grid, box, buttons, glows;
- move, resize, hide and retint any widget already on the screen, which is enough to reorder or
  remove buttons;
- switch the texture set, text style, effect or texture a widget uses, to any name the launcher
  already knows;
- add your own text styles and button texture sets.

You can't:
- add a button that does something new. What each button does is compiled into the launcher
  (`ClientG.exe`).
- change the splash card shown before the intro. It is a bitmap compiled into `ClientG.exe`.
- change the layout of the UI atlas. Its region boxes are fixed; only the pixels inside them are
  yours.

## The two delivery routes

Everything on the menu reaches the game one of two ways.

1. **Loose textures.** A file in `<your mod>/Data/ART/TEXTURES/SRGB/` replaces the stock texture
   of the same name. That covers the standalone screen images (`.DDS`) and the big UI atlas,
   `MT_COMMANDBAR_COMMON.TGA`. The stock files are in the base `Data/TEXTURES_SRGB.MEG`.
2. **Your own `CONFIG.MEG`.** A mod can ship `<your mod>/Data/CONFIG.MEG`, and the launcher uses
   it in place of the base one. That archive holds the screen layouts (`.BUI`), the button
   texture sets (`GUITEXTURESETS.XML`), the text styles (`FONTLIBRARY.BFD`) and `FACTIONS.XML`.
   Loose copies of these files are ignored: they only work from inside the MEG.

Both are whole-file replacements. Your `CONFIG.MEG` is a complete copy of the base one with your
edits in it, and your atlas is a complete copy of the stock atlas with your regions repainted.

## What's on the menu

The menu screen is `DATA\ART\GUI\RA_MAIN_MENU.BUI` inside `CONFIG.MEG`. Its parts:

| What you see | Widget | Drawn from | How to change it |
|---|---|---|---|
| Background | `RA_MainMenu_BG` | `RA_MAINMENUBG_02.DDS`, 2878×1200 | loose DDS |
| Red radar grid | `BG_Grid_Red`, `BG_Grid_Red_legacy` | `UI_RA_MAINMENU_GRID_RED_01.DDS` (1125×1125), `UI_RA_MAINMENU_GRID_RED.DDS` (1125×1080) | loose DDS (fully transparent removes it) |
| Title logo | `RA_Logo_Quad` | `UI_RA_MAINLOGO.DDS`, 1948×552 | loose DDS |
| Menu box | `Button_BG`, `Button_Scanlines` | atlas regions `UI_RA_MAINMENU_BUTTON_BG` (727,1818,723,557) and `UI_RA_MAINMENU_BUTTON_SCANLINES` (4788,1798,723,557) | repaint in the atlas |
| Buttons | 11 `Button_*` widgets | texture set `TacticalSidebarSellRepairButton` in `GUITEXTURESETS.XML` | give the menu its own set (step 5) |
| Button labels | the same widgets | text style `24 Point Regular Outline Red` in `FONTLIBRARY.BFD` | name another style |
| Sweep across the box | an effect in the `.BUI` | `Scanline_Sheen_Red` in `GUIEFFECTS.CFX` | name another effect |
| New-content pulse on Bonus Gallery | `BonusButtonGlow_Quad` | texture `ra_ui_bonusbuttonhighlight` (atlas) | name another texture |
| BUILD / VERSION lines | `Build`, `Version` | a tint in the `.BUI` | change the tint |
| EA, Lemon Sky, Petroglyph logos | `Button_*_Logo` | hover art drawn at fixed spots | keep their spots on your background |

Atlas regions are written (x, y, width, height), measured from the atlas's top-left corner.
Step 4 shows how to look up any other region.

## Rules that will save you hours

1. **Every file inside your `CONFIG.MEG` must keep its exact byte size.** The launcher reads your
   MEG's files at the *base* archive's offsets, so a file that grows or shrinks shifts every file
   after it, and the game crashes at boot. The crash names an innocent file further down the
   archive, not the one you changed. For a `.BUI`, recompress at zlib level 9 and pad with zeros
   back to the original size. For an XML, delete comments to make room and pad with spaces.
2. **Build your `CONFIG.MEG` from the base one.** It replaces the base archive whole rather than
   merging with it, so it has to contain every file. For the same reason, two mods that both ship
   a `CONFIG.MEG` (or both ship an atlas) can't both be in effect.
3. **Never repaint something the rest of the game shares.** The menu's button set is the in-game
   sidebar's sell/repair button set, and `24 Point Regular Outline Red` is used by all 19 RA
   screens. Repaint those and you restyle the game too. Make new ones instead. Before you repaint
   an atlas region, decompress every `.BUI` in `CONFIG.MEG` and search them for its name, to see
   what else draws it.
4. **Keep the stock image sizes.** The layout is built around them. Atlas regions can't move or
   grow (a loose `.MTD` is ignored), so your art has to fit the stock box.
5. **Check the file that actually reached the game.** A stale copy in the mod folder is the most
   common reason an edit "does nothing". Compare md5s of the deployed file and your build, then
   restart the launcher fully.
6. **Hide a widget by shrinking it, not by moving it off screen.** Off-screen positions are
   clamped, so a "removed" button peeks back in on ultrawide screens. Set its size to almost
   zero and its tint alpha to 0.
7. **A widget's rect and tint come before its name in the `.BUI`.** The tags after a widget's
   name belong to the *next* widget. Get this backwards and you move the button below the one you
   meant.
8. **Some text ignores your tint.** The launcher recolours text it fills in itself (player names,
   map names). Use a text style that is already the colour you want.
9. **A text style name that doesn't exist falls back to a small white default**, with no error.
   Copy names exactly.
10. **Bleed colour under transparent pixels.** The launcher filters textures, so fully transparent
    pixels with black RGB draw a dark fringe round your art. Fill them with the colour of the
    nearest opaque pixel (`bleed()` in `title_logo_build.py`).
11. **Test at more than one aspect ratio.** The background's central 1920×1080 is fitted to the
    screen and the rest shows as margins on wider or taller screens. A 16:10 screen such as the
    Steam Deck shows the full 1200-pixel height.

## Tools

- Python 3 with Pillow and numpy.
- From [`scripts/`](../scripts):
  - [`meg_extract.py`](../scripts/meg_extract.py) lists and extracts files from a `.MEG`.
  - [`meg_pack.py`](../scripts/meg_pack.py) rebuilds a `.MEG` with some files replaced, and
    compares two MEGs' file tables.
  - [`bui_tree.py`](../scripts/bui_tree.py) parses a `.BUI` into its node tree, lets you edit it,
    and writes it back at the original size.
  - [`title_logo_build.py`](../scripts/title_logo_build.py) holds the DDS writer (`dds_bytes`),
    the atlas painter (`paint_atlas`) and the colour bleed (`bleed`).
  - The worked examples: [`menu_art.py`](../scripts/menu_art.py),
    [`bui_mainmenu_build.py`](../scripts/bui_mainmenu_build.py),
    [`gui_texturesets_build.py`](../scripts/gui_texturesets_build.py),
    [`fontlib_build.py`](../scripts/fontlib_build.py), and
    [`build_config_meg.sh`](../scripts/build_config_meg.sh), which runs all of them for our mod.
- `menu_art.py` and `title_art.py` look for `TEXTURES_SRGB.MEG` at the Linux Steam path
  (`TEXTURES_MEG` near the top of each). On Windows, point it at
  `C:\Program Files (x86)\Steam\steamapps\common\CnCRemastered\Data\TEXTURES_SRGB.MEG`, or
  wherever your Steam library is.
- Your mod folder is `Documents\CnCRemastered\Mods\Red_Alert\<your mod>\`, beside its
  `ccmod.json`. On Linux it is the same path inside the game's Proton prefix,
  `steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/`.

## Step by step

### 1. Pull out the stock files

The `CONFIG.MEG` members are small, and `meg_extract.py` can take them directly. Its pattern
matches anywhere in the stored path, case-insensitively.

```bash
GAME="$HOME/.steam/steam/steamapps/common/CnCRemastered/Data"   # your install's Data folder
python3 scripts/meg_extract.py list "$GAME/CONFIG.MEG" MAIN_MENU
python3 scripts/meg_extract.py extract "$GAME/CONFIG.MEG" RA_MAIN_MENU.BUI work/
python3 scripts/meg_extract.py extract "$GAME/CONFIG.MEG" GUITEXTURESETS.XML work/
python3 scripts/meg_extract.py extract "$GAME/CONFIG.MEG" FONTLIBRARY.BFD work/
```

`TEXTURES_SRGB.MEG` is 2.4 GB, and `extract` reads a whole archive into memory, so take single
textures from it with `read_member`, which reads only the file you ask for:

```bash
python3 - <<'EOF'
import sys; sys.path.insert(0, 'scripts')
import meg_extract
MEG = '/path/to/CnCRemastered/Data/TEXTURES_SRGB.MEG'
for name in ('RA_MAINMENUBG_02.DDS', 'UI_RA_MAINLOGO.DDS',
             'MT_COMMANDBAR_COMMON.TGA', 'MT_COMMANDBAR_COMMON.MTD'):
    open('work/' + name, 'wb').write(
        meg_extract.read_member(MEG, 'DATA\\ART\\TEXTURES\\SRGB\\' + name))
EOF
```

Make your mod's texture folder and copy the stock atlas into it. You will paint into that copy.

```bash
mkdir -p "<your mod>/Data/ART/TEXTURES/SRGB"
cp work/MT_COMMANDBAR_COMMON.TGA "<your mod>/Data/ART/TEXTURES/SRGB/"
```

### 2. The background

Paint a 2878×1200 image. The launcher fits its central 1920×1080 (the "core", whose top-left is
at 479,60) to a 16:9 screen. The margins round the core only show on wider or taller screens, so
run your backdrop to every edge but keep anything important inside the core.

In core coordinates:
- The menu box covers (602,322) to (1314,944). Keep that area quiet so the buttons read.
- The publisher logos are engraved at about (78,1006) Petroglyph, (208,1004) Lemon Sky and
  (354,1008) EA. Their buttons draw colour hover art at those fixed spots, so keep a logo, or a
  faint silhouette of one, where each was. Otherwise the hover art appears over nothing.

Save it as `RA_MAINMENUBG_02.DDS` in your mod's `SRGB` folder, as an uncompressed 32-bit DDS
with no mipmaps. That is the stock file's format, and `dds_bytes()` in `title_logo_build.py`
writes exactly that.

To remove the red radar grid, ship `UI_RA_MAINMENU_GRID_RED.DDS` (1125×1080) and
`UI_RA_MAINMENU_GRID_RED_01.DDS` (1125×1125) as fully transparent images.

Worked example: `background()` in `menu_art.py`, which puts two soldiers from the game's Steam key
art either side of the box over a smoke backdrop.

### 3. The title logo

The RA title is drawn from two textures:
- `UI_RA_MAINLOGO.DDS`, 1948×552, on the main menu and the skirmish loading screen. Ship it
  loose.
- The atlas region `UI_RA_MAINMENU_LOGO` (4788,94,908,257), on the campaign select and loading
  screens. The stock region is a straight downscale of the big logo, so scale yours the same way
  and paint it in.

`python3 scripts/title_logo_build.py "<your mod>/Data/ART/TEXTURES/SRGB" my_title.png` does both
from a 1948×552 RGBA PNG, colour bleed included.

A third copy is baked into `UI_RA_LOADINGSCREEN_BG.DDS`. We never found a screen that shows it.

### 4. The atlas: box, buttons and glow

`MT_COMMANDBAR_COMMON.TGA` is 6871×6716, 32-bit BGRA, stored bottom row first, with an 18-byte
header and no footer. Pixel (x, y), counted from the top-left, starts at byte
`18 + ((6716 - 1 - y) * 6871 + x) * 4`. Write your pixels into the copy in place rather than
loading and saving the whole image through an image library; that keeps the rest of the file
byte-identical. `paint_atlas()` in `title_logo_build.py` does this.

To find a region, search `MT_COMMANDBAR_COMMON.MTD` for its name followed by `.TGA`, skip the zero
bytes after it (one or two), and read four little-endian int32s: x, y, width, height.

What we painted:
- **The box.** Both box regions, recoloured from red to steel with the stock alpha kept, so the
  box stays see-through. Red art carries all its shading in the red channel, so steel is that
  channel multiplied by a grey per channel (`steel()` in `menu_art.py`).
- **The buttons.** The stock button art is shared with the in-game sell/repair buttons, so we
  left it alone and painted steel copies into three regions that only Tiberian Dawn's own main
  menu draws: `UI_BUTTON_MAIN_06_MID` (normal), `UI_BUTTON_MAIN_07_MID` (hover) and
  `UI_BUTTON_MAIN_PRESSED_06_MID` (pressed), each 891×91. Step 5 points the menu's buttons at
  them. TD's pause menu uses other `UI_BUTTON_MAIN_*` regions, so check before taking one.
- **The glow.** Nothing to paint: step 6 points the Bonus Gallery pulse at TD's existing green
  `UI_BONUSBUTTONHIGHLIGHT` region.

### 5. Give the buttons their own texture set

Add a `TextureSet` for the menu buttons to `GUITEXTURESETS.XML`. Ours:

```xml
<TextureSet GUIType="Text_Button" Name="TF_MainMenuSteelButton_Textures">
  <Texture Quad="Background_Left"> UI_Sidebar_SellRepairButton_On_Edge.tga </Texture>
  <Texture Quad="Background_Middle"> UI_Button_Main_06_Mid.tga </Texture>
  <Texture Quad="Background_Right"> UI_Sidebar_SellRepairButton_On_Edge.tga </Texture>
  <!-- the same three quads for Mouse_Over (UI_Button_Main_07_Mid.tga),
       Mouse_Down (UI_Button_Main_Pressed_06_Mid.tga) and Toggled_On (the normal art) -->
  <Float Value="Mouse_Over_Modifier"> 0.0 </Float>
  <Float Value="Mouse_Down_Modifier"> 0.0 </Float>
  <Float Value="Disabled_Button_Alpha"> 0.1 </Float>
</TextureSet>
```

The edges reuse the stock set's transparent edge pieces. The name is exactly as long as
`TacticalSidebarSellRepairButton` (31 characters), which makes the `.BUI` edit a straight swap;
`bui_tree.py` handles a name of another length too. The XML must still keep its byte size, so
`gui_texturesets_build.py` deletes whole comment blocks from the end of the file to make room and
pads the rest with spaces before `</TextureSets>`.

### 6. Edit the menu layout (`RA_MAIN_MENU.BUI`)

A `.BUI` is a 36-byte header (starting `CH`) followed by a zlib stream. Decompressed, it is a
tree of nodes, each `[u32 id][u32 spec]`. If spec's top bit is set, the node is a container
holding `spec & 0x7fffffff` child nodes; otherwise it is a leaf of `spec` bytes. Containers count
children, not bytes, so a leaf can change length without touching anything round it. Widget
names, texture names, text keys (`TEXT_MISSION_LIST`) and style names are readable ASCII once
decompressed, which is the quickest way to find what to edit. Full format notes:
[`bui-front-end-modding.md`](bui-front-end-modding.md).

What we changed:

| Change | How |
|---|---|
| Reorder the buttons | Each button's rect is a `02 10` micro-chunk followed by four little-endian floats: x, y, width, height, in 0..1 screen units. Change y. Rows are 0.0995 apart. |
| Remove START NEW GAME | Its rect to (x, y, 0.0001, 0.0001), and its tint's alpha to 0. A tint is `03 10` followed by four floats, RGBA. |
| Keep the Bonus Gallery pulse on its button | Move the bonus notification rect by the same amount as the button. |
| Steel buttons | Texture set name `TacticalSidebarSellRepairButton` to `TF_MainMenuSteelButton_Textures` (11 places). |
| Green labels | Text style `24 Point Regular Outline Red` to `24 Point Regular Outline Green` (11 places). |
| Neutral sweep | Effect `Scanline_Sheen_Red` to `Scanline_Sheen`. |
| Green pulse | Texture `ra_ui_bonusbuttonhighlight` to `ui_bonusbuttonhighlight`. |
| Green BUILD / VERSION | Their tints from (0.6863, 0, 0) to (0.40, 0.85, 0.40). |

How the names are stored (all integers little-endian):
- text style or label text: a leaf `[u32 3][u32 len+2][u16 len][ascii]`
- texture: a leaf `[u32 2][u32 len+2][u16 len][ascii]`
- effect: a leaf `[u32 0x16][u32 len+4][byte 0x17][byte len+2][u16 len][ascii]`
- texture set: a micro-chunk `[byte 0x0f][byte len+2][u16 len][ascii]` inside a widget's header
  leaf. If its length changes, the header leaf's size changes with it;
  `bui_tree.replace_texture_set()` handles that.

The other effects in `GUIEFFECTS.CFX` are `Scanline_Sheen_Blue`, `Button_Sheen`, `Logo_Sheen`,
`Logo_Glow`, `Power_Sheen` and `MouseOver`.

Then write the file back:
1. Recompress the edited payload with zlib at level 9. The stock files are compressed at about
   level 6, so repacking at level 6 often comes out bigger.
2. Put the new compressed length at header offset `0x10`. Leave the hash at `0x08` as it is: the
   launcher never checks it.
3. Pad with zeros to the original file size (5274 bytes for `RA_MAIN_MENU.BUI`). If the stream
   doesn't fit, the edit is too big.

`bui_tree.write_same_size()` does all three. `bui_mainmenu_build.py` is our full main-menu edit:
it finds the rects by byte offset and checks their stock values first, so it stops rather than
edit the wrong widget if the base file is ever different. Our newer builders
(`bui_dialogbox_build.py`, `bui_lobby_build.py`) find widgets by name with `bui_tree.headers()`,
which is the easier way to start.

### 7. Text colours (`FONTLIBRARY.BFD`)

Text styles are named entries in `DATA\ART\GUI\FONTLIBRARY.BFD`: a flat list of
`[name, font face, properties]` nodes, with the colour as four RGBA floats after `0b 10` in the
properties. The coloured styles that ship are `18 Point Regular Green`, `20 Point Outline Green`,
`24 Point Regular Outline Green`, `30 Point Regular Green`, `24 Point Regular Outline Blue`,
`20 Point Outline Red` and `24 Point Regular Outline Red`.

For another size or colour, copy a white style and change its colour. `fontlib_build.py` adds four
green styles that way. The file keeps its byte size, the same as a `.BUI`. The main menu itself
only needed the existing `24 Point Regular Outline Green`.

### 8. Build your `CONFIG.MEG`

`repack` copies the base archive and replaces each file whose stored path ends with the name
before the `=`. `verify` then compares the result with the base.

```bash
python3 scripts/meg_pack.py repack "$GAME/CONFIG.MEG" "<your mod>/Data/CONFIG.MEG" \
    'DATA\ART\GUI\RA_MAIN_MENU.BUI=work/RA_MAIN_MENU.edited.BUI' \
    'DATA\ART\GUI\GUITEXTURESETS.XML=work/GUITEXTURESETS.edited.XML' \
    'DATA\ART\GUI\FONTLIBRARY.BFD=work/FONTLIBRARY.edited.BFD'
python3 scripts/meg_pack.py verify "$GAME/CONFIG.MEG" "<your mod>/Data/CONFIG.MEG"
```

`verify` must print `IDENTICAL file tables`. If it lists a file with a different size, that file
will crash the game at boot.

### 9. Test

1. Your mod folder now holds `ccmod.json`, `Data/CONFIG.MEG`, and `Data/ART/TEXTURES/SRGB/` with
   your DDS files and the atlas.
2. Enable the mod, restart the launcher fully, and open Red Alert.
3. If something didn't change, compare md5s of the files in the mod folder and your build.
4. Look at it at 16:9 and at least one other aspect ratio.
5. If the game crashes at boot, a `CONFIG.MEG` file changed size. Delete `CONFIG.MEG` from the
   mod folder to get back in; the base install is never touched.

## Going further

The same levers reach the rest of the front end. What we did with them:

- **Exit and confirm dialog.** The menu's dialog is `RA_DIALOGBOX_SOVIET.BUI`, chosen by the
  `DialogBox` key in `FACTIONS.XML`. The Soviet factions use the same box in game. See
  `bui_dialogbox_build.py`.
- **Whole screens.** The RA front end opens the screens named in the `GUIFileNames` of the Soviet
  entry (`Faction5`) in `FACTIONS.XML`. Point one at a Tiberian Dawn screen (its name without the
  `RA/` prefix) and the whole screen is swapped. We did that for the skirmish lobby, LAN lobby,
  LAN match list and Workshop map browser (`factions_build.py`, `bui_lobby_build.py`).
  `FACTIONS.XML` must keep its byte size too: pad the edited line with spaces.
- **Loading screen.** `RA_UI_LOADINGSCREEN.BUI` and the spinner sheet `ANIM_LOADTWIDDLE_RA.DDS`,
  a 4×4 grid of frames that always plays at 24 fps (`loading_art.py`,
  `bui_loadingscreen_build.py`).
- **Startup intro.** A loose `Data/ART/MOVIES/RA/REDINTRO.BK2` replaces Red Alert's intro movie.
  It must be Bink 1 or Bink 2; the player reads the file header, so a Bink 1 `.bik` renamed to
  `.BK2` works, and RAD Video Tools encodes Bink 1 for free. Any other format, Theora for one,
  hangs on a black screen that can't be skipped.
- **Motion.** Animations in a `.BUI` only play when the launcher starts them by name, and no Lua
  ships with the game, so there is no way to add new motion. The effects in `GUIEFFECTS.CFX`
  (sheens and glows) loop by themselves and can be attached to a widget.

## Shipping it

- `CONFIG.MEG` adds about 44 MB to your Workshop item and the atlas about 184 MB, however little
  you change in them.
- Only one mod's `CONFIG.MEG` and one mod's atlas can be in use at a time, so a player running
  your mod beside another that ships either file will see a clash.
- The scripts in this repo are GPL v3.
