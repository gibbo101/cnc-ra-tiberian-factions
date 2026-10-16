# Add-ons: the ADD-ONS screen, pack panel, lobby popup and save check

**Status:** Reference. What the launcher layer (`redalert/tf_launcher.cpp`) does for the asset packs, against
ClientG 1.153.745903: the panel, popup and save check ship in 5.5.0; the ADD-ONS screen ships in the next release.

An add-on is found by a marker file in the launcher's own mod list: a required pack's CCDATA marker
(`asset-packs.md`, Required packs), any file unique to it otherwise. The ADD-ONS screen gets, switches on and
switches off add-ons; the main menu's panel and the lobby's popup send the player there; Load Game checks saves.
Every launcher function they call is checked by its opening bytes at install (`Panel_Calls_Match`); on another
launcher build none of it installs.

## The ADD-ONS screen

TIBERIAN FACTIONS ADD-ONS, between LAN MODE and FACTION ENCYCLOPEDIA on the main menu, opens a screen of the mod's
own: `TF_ADDONS.BUI` (`scripts/bui_addons_build.py`), the CAMPAIGNS page's frame with its class set to ClientG's
`SplashScreen`. A screen's `.BUI` names the C++ class that runs it; `SplashScreen` is registered, used by no stock
screen and binds nothing, so the launcher layer binds every widget. Opening: `GUIManager()` (`0x5ED5D0`), then
`Create_Scene_Instance` (`0xF2CB70`, the name `RA/TF_AddOns`), focus (`0xF0E1D0`), and the scene's behaviour object
at `+0x330` owns the widgets and events. BACK closes the scene (vtable `+0x2CC`) and releases it (`0x55FE10`); the
main menu stays alive under it. A click handler bound with data `n` is called with the behaviour object plus `n`
in `ecx`, so one handler serves every row or tab.

- **Tabs** ASSETS, THEATRES and CAMPAIGNS (`PackInfo.Kind`), each a clone of BACK with a glow when open and a badge
  counting its changes. An empty tab shows COMING SOON.
- **Rows**, four a tab: a checkbox (TD's, from Bonus Gallery), the pack's logo, name and state. A click on a row
  outside its checkbox selects it; the checkbox means "on".
- **The selected pack**, on the right: name, logo, description, what it needs or what needs it, its status and a
  20-segment download bar.
- **The top panel** lists the changes waiting (WILL SWITCH ON / WILL SWITCH OFF, knock-on changes with their
  cause), or how to use the screen.
- **Dependencies** (`PackInfo.Needs`): ticking a pack ticks what it needs, unticking one unticks what needs it.
- **APPLY AND RESTART** switches unticked packs off (`0x7BB7A0` with 0), subscribes to ticked packs that are missing
  (`SteamAPI_ISteamUGC_SubscribeItem`), and once every ticked pack has arrived switches them on and restarts.
  While packs download it reads WORKING... and BACK reads CANCEL, which stops the wait without switching anything
  on; the screen covers the menu, so no game starts meanwhile. A pack Steam never starts on within 20 seconds
  opens its Workshop page. UNDO CHANGES puts every tick back to what is on. Unsubscribing is the Workshop's.

## Pack states

`Pack_State` reads, in order:

1. **Loaded:** one of this session's mod roots (`0x1FE4C28`) holds the marker.
2. **Switched on for the next start** or **switched off:** a record in the mod manager's list (getter `0x5E8CB0`,
   records of `0xBC` bytes: folder `+0x78`, ID `+0xA8`, on `+0xB9`) holds the marker.
3. **Downloaded:** the pack's Workshop item folder, beside the game's install, holds the marker and a
   `ccmod.json`, but the mod list hasn't seen it (the list only rescans on Mods > Refresh or a restart). Only when
   the signed-in account subscribes (`GetItemState`): every account on a machine shares the Workshop folder, but
   the launcher lists only its own account's subscriptions, so another account's download reads as missing.
4. **Downloading:** Steam reports the item subscribed and downloading (`SteamAPI_ISteamUGC_GetItemState`); the
   panel shows `GetItemDownloadInfo`'s percentage.
5. **Missing.**

A pack downloaded and switched on in this session, not yet in the mod list, reads as switched on for the next
start; one switched off but still loaded reads as switched off for the next start.

`PACKS` in `tf_launcher.cpp` has one row per add-on, in `scripts/pack_panel_art.py` `PACK_LOGOS` order: its marker,
logo id, Workshop item, the faction that needs it (none for an optional pack), name, description, kind and needs.

## Main menu panel

`scripts/bui_mainmenu_pack_notice.py` lays the panel out top right, every piece hidden, straight in
`ScreenFitter_Group` (a cloned group carries the source group's tint and places its children differently).
`scripts/pack_panel_art.py` paints the frame from the menu box's steel at the box's own scale (the launcher draws
menu images without mipmaps, so a larger frame bands on the Deck) and a logo per pack.

The main menu is one object for the whole session, so a 2-second `SetTimer` on its UI thread refreshes the panel
while a pack needs the player. It shows the first such pack, with `+N MORE` when others wait:

**GO TO ADD-ONS** opens the ADD-ONS screen with that pack selected and ticked.

Switching on uses the Mods screen's own toggle (`0x7BB7A0`) for an installed pack and adds a downloaded pack's ID
to the profile's enabled list (`0x20E0D88`; the ID is zlib's CRC-32 of `ccmod.json`'s name followed by
`high.low`), saves the profile (`0x14D8420` with 1, 0, 1), and restarts by posting the launcher's
`CL_CLIENT_RESTART` message, as the Mods screen's RESTART NOW does.

A `ccmod.json` version bump changes the ID, and the launcher drops enabled IDs that match no installed mod at
startup, so an update switches the pack off once; the panel then offers GO TO ADD-ONS.

## Lobby popup

Picking TS GDI for any slot, or a slot taking it from the lobby's settings, raises ClientG's message box when the
pack isn't loaded. **GO TO ADD-ONS** leaves the lobby through its own Back handler (`0x71C790`, on the next UI
tick) and opens the ADD-ONS screen with the pack ticked. The box reports its first button as 2 and OK as 3.

## Load Game check

The DLL writes `TFS2`, its save version and a flags word (bit 1: the TS-HD pack was on) first in its save data,
and refuses any other save. The launcher reads the selected save through Steam's remote storage and greys
**Load** with a reason, through the load screen's stock missing-custom-map path, when the marker or version
differs, or when the save needs a pack that isn't loaded.

A `.sav` is ClientG's chunk file: a zlib stream (metadata, the screenshot) whose compressed size is at `0x10`,
then a chunk index ending in a sync flush (`00 00 FF FF`), then the instance chunk: a 20-byte header with its size
at `+8`, and raw deflate holding the DLL's save data. `puff.c` (zlib's reference inflater) inflates its start.
