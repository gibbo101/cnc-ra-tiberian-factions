# The pack panel, lobby popup and save check

**Status:** Reference. What the launcher layer (`redalert/tf_launcher.cpp`) does for the required asset packs,
as of 5.5.0, against ClientG 1.153.745903.

A required pack (`asset-packs.md`, Required packs) is found by its CCDATA marker in the launcher's own mod list.
The launcher layer shows the player what is missing and fixes it in place: the main menu's panel, the lobby's
popup, and Load Game's check. Every launcher function it calls is checked by its opening bytes at install
(`Panel_Calls_Match`); on another launcher build none of it installs.

## Pack states

`Pack_State` reads, in order:

1. **Loaded:** one of this session's mod roots (`0x1FE4C28`) holds the marker.
2. **Switched on for the next start** or **switched off:** a record in the mod manager's list (getter `0x5E8CB0`,
   records of `0xBC` bytes: folder `+0x78`, ID `+0xA8`, on `+0xB9`) holds the marker.
3. **Downloaded:** the pack's Workshop item folder, beside the game's install, holds the marker and a
   `ccmod.json`, but the mod list hasn't seen it (the list only rescans on Mods > Refresh or a restart).
4. **Downloading:** Steam reports the item subscribed and downloading (`SteamAPI_ISteamUGC_GetItemState`); the
   panel shows `GetItemDownloadInfo`'s percentage.
5. **Missing.**

`PACKS` in `tf_launcher.cpp` has one row per required pack: its marker, logo widget, Workshop item and what needs
it.

## Main menu panel

`scripts/bui_mainmenu_pack_notice.py` lays the panel out top right, every piece hidden, straight in
`ScreenFitter_Group` (a cloned group carries the source group's tint and places its children differently).
`scripts/pack_panel_art.py` paints the frame from the menu box's steel at the box's own scale (the launcher draws
menu images without mipmaps, so a larger frame bands on the Deck) and a logo per pack.

The main menu is one object for the whole session, so a 2-second `SetTimer` on its UI thread refreshes the panel
while a pack needs the player. It shows the first such pack, with `+N MORE` when others wait:

- **GET IT ON THE STEAM WORKSHOP** opens the item's page in the Steam overlay.
- **ENABLE AND RESTART** switches every installed pack on with the Mods screen's own toggle (`0x7BB7A0`), adds a
  downloaded pack's ID to the profile's enabled list (`0x20E0D88`; the ID is zlib's CRC-32 of `ccmod.json`'s name
  followed by `high.low`), saves the profile (`0x14D8420` with 1, 0, 1), and posts the launcher's
  `CL_CLIENT_RESTART` message, as the Mods screen's RESTART NOW does. The game comes back with the pack loaded.

A `ccmod.json` version bump changes the ID, and the launcher drops enabled IDs that match no installed mod at
startup, so an update switches the pack off once; the panel then offers ENABLE AND RESTART.

## Lobby popup

Picking TS GDI for any slot, or a slot taking it from the lobby's settings, raises ClientG's message box when the
pack isn't loaded. Missing: **GET IT ON THE WORKSHOP** leaves the lobby through its own Back handler (`0x71C790`,
on the next UI tick), so the main menu's panel follows the download, then opens the page. Installed or
downloaded: **ENABLE AND RESTART**. The box reports its first button as 2 and OK as 3.

## Load Game check

The DLL writes `TFS2`, its save version and a flags word (bit 1: the TS-HD pack was on) first in its save data,
and refuses any other save. The launcher reads the selected save through Steam's remote storage and greys
**Load** with a reason, through the load screen's stock missing-custom-map path, when the marker or version
differs, or when the save needs a pack that isn't loaded.

A `.sav` is ClientG's chunk file: a zlib stream (metadata, the screenshot) whose compressed size is at `0x10`,
then a chunk index ending in a sync flush (`00 00 FF FF`), then the instance chunk: a 20-byte header with its size
at `+8`, and raw deflate holding the DLL's save data. `puff.c` (zlib's reference inflater) inflates its start.
