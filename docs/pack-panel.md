# Add-ons: the ADD-ONS screen, menu notice, lobby popup and save check

**Status:** Reference. What the launcher layer (`redalert/tf_launcher.cpp`) does for the asset packs, against
ClientG 1.153.745903: the popup and save check ship in 5.5.0; the ADD-ONS screen and the menu notice ship in the
next release.

An add-on is found by a marker file in the launcher's own mod list: a required pack's CCDATA marker
(`asset-packs.md`, Required packs), any file unique to it otherwise. The ADD-ONS screen gets, switches on and
switches off add-ons; the main menu's notice and the lobby's popup send the player there; Load Game checks saves.
Every launcher function they call is checked by its opening bytes at install (`Panel_Calls_Match`); on another
launcher build none of it installs.

## The ADD-ONS screen

TIBERIAN FACTIONS ADD-ONS, between LAN MODE and FACTION ENCYCLOPEDIA on the main menu, opens a screen of the mod's
own: `TF_ADDONS.BUI` (`scripts/bui_addons_build.py`), the CAMPAIGNS page's frame with its class set to ClientG's
`SplashScreen`, so the launcher layer binds every widget. It opens as the scene `RA/TF_AddOns`, as the field manual's
[New screens and buttons](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/new-screens-and-buttons.md#a-new-screen) describes, with one click handler, bound with each row's or tab's number,
serving them all.

- **Tabs** ASSETS, THEATRES and CAMPAIGNS (`PackInfo.Kind`), each a clone of BACK with a glow when open and a badge
  counting its changes. An empty tab shows COMING SOON.
- **Ticks** start as what is on; every other screen that sends the player here selects its add-on, never ticks it.
- **Rows**, four a tab: a checkbox (TD's, from Bonus Gallery), the pack's logo, name and state. A click on a row
  outside its checkbox selects it; the checkbox means "on".
- **The selected pack**, on the right: name, logo, description, what it needs or what needs it, its status and a
  20-segment download bar.
- **The top panel** lists the changes waiting (WILL SWITCH ON / WILL SWITCH OFF, knock-on changes with their
  cause), or how to use the screen.
- **Dependencies** (`PackInfo.Needs`): ticking a pack ticks what it needs, unticking one unticks what needs it.
- **APPLY AND RESTART** switches unticked packs off (`0x7BB7A0` with 0), subscribes to ticked packs that are missing
  (`SteamAPI_ISteamUGC_SubscribeItem`, then `DownloadItem` at high priority, as Steam holds a plain subscription's
  download while the game runs), and once every ticked pack has arrived switches them on and restarts.
  While packs download it reads WORKING... and BACK reads CANCEL, which stops the wait without switching anything
  on; the screen covers the menu, so no game starts meanwhile. A pack Steam never starts on within 20 seconds
  opens its Workshop page. UNDO CHANGES puts every tick back to what is on. Unsubscribing is the Workshop's.

## Pack states

`Pack_State` reads, in order (the launcher's lists and their addresses: the field manual's
[New screens and buttons](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/new-screens-and-buttons.md#switching-mods-on-and-off-from-your-screen), Switching mods on and off from your screen):

1. **Loaded:** one of this session's mod roots holds the marker.
2. **Switched on for the next start** or **switched off:** a record in the mod manager's list holds the marker.
3. **Downloaded:** the pack's Workshop item folder, beside the game's install, holds the marker and a
   `ccmod.json`, but the mod list hasn't seen it yet. Only when the signed-in account subscribes
   (`GetItemState`); another account's download reads as missing.
4. **Downloading:** Steam reports the item subscribed and downloading (`SteamAPI_ISteamUGC_GetItemState`); the
   ADD-ONS screen shows `GetItemDownloadInfo`'s percentage.
5. **Missing.**

A pack downloaded and switched on in this session, not yet in the mod list, reads as switched on for the next
start; one switched off but still loaded reads as switched off for the next start.

`PACKS` in `tf_launcher.cpp` has one row per add-on, in `scripts/pack_panel_art.py` `PACK_LOGOS` order: its marker,
logo id, Workshop item, the faction that needs it (none for an optional pack), name, description, kind and needs.

## Main menu notice

`scripts/bui_mainmenu_pack_notice.py` lays the notice out top right, every piece hidden, straight in
`ScreenFitter_Group` (a cloned group carries the source group's tint and places its children differently).
`scripts/pack_panel_art.py` paints the frame from the menu box's steel at the box's own scale (a frame painted larger banded on the Deck, which looks like the launcher drawing menu
images without mipmaps: the field manual's
[BUI screens](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/bui-screens.md#traps), Paint menu art at the size it's drawn) and the logo: the mod's title over ADD-ONS. A
clone of the menu box's `Button_Scanlines` runs its moving sheen over the frame.

It shows while any add-on is not on (`Pack_On`): never subscribed, downloading, downloaded or switched off. The text
is fixed: YOU HAVE TIBERIAN FACTIONS ADD-ONS / AVAILABLE THAT ARE NOT ENABLED. The main menu is one object for the
whole session, so a 2-second `SetTimer` on its UI thread refreshes it while it shows.

**ENABLE ADD-ONS** opens the ADD-ONS screen with the first such add-on selected.

Switching on, and why an update changes a pack's ID: see the field manual's
[New screens and buttons](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/new-screens-and-buttons.md#switching-mods-on-and-off-from-your-screen). TF restarts by posting the launcher's
`CL_CLIENT_RESTART` message; after a pack update the pack is off once, so the notice shows.

## Lobby popup

Picking TS GDI for any slot, or a slot taking it from the lobby's settings, raises ClientG's message box when the
pack isn't loaded. **GO TO ADD-ONS** leaves the lobby through its own Back handler (`0x71C790`, on the next UI
tick) and opens the ADD-ONS screen with the pack selected. The box reports its first button as 2 and OK as 3.

In multiplayer every player needs the same add-ons: see the field manual's
[LAN games](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/lan-games.md#every-player-needs-the-same-mods), Every player needs the same mods.

## Load Game check

The DLL writes `TFS2`, its save version and a flags word (bit 1: the TS-HD pack was on) first in its save data,
and refuses any other save. The launcher reads the selected save through Steam's remote storage and greys
**Load** with a reason, through the load screen's stock missing-custom-map path, when the marker or version
differs, or when the save needs a pack that isn't loaded.

The `.sav` layout and how to reach the DLL's data: see the field manual's
[Save files (.sav)](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/formats/save-files.md#the-layout).
