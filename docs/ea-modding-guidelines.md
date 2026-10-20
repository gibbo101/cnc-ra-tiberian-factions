# EA's C&C modding guidelines

**Status:** Reference. The rules EA sets for every C&C mod (Franchise Modding Guidelines, revision 2, 27 February
2025, https://www.ea.com/games/command-and-conquer/news/modding-faq), and how the mod and its packs meet them.
Reread the page before each release; EA can change it and can revoke the licence at any time.

## The rules that bind us

| Rule | What it means here |
|---|---|
| Mods are non-commercial and free | No paid content, no transactions in game. Donations only on a site, never in the game, with no in-game reward. |
| No music files from any C&C game | Nothing we upload may hold a C&C soundtrack, from any game, Tiberian Sun's included although it is a free download. Music is used only where the player already has it: the Remastered install's own tracks, or files the mod builds from the player's own copy (`ts-music-import.md`). |
| The disclaimer, exactly: "EA has not endorsed and does not support this product." | Prominently at the top of every page: the mod's Workshop listing, every asset pack's listing, the ModDB page, and the repo's root README. |
| No EA artwork, logos or trademarks to promote the mod | Workshop previews, ModDB images and promotional art use our own art. Plain text ("for Command & Conquer Remastered") is allowed. |
| No suggestion that EA endorses or is affiliated with the mod | The disclaimer covers it; copy never implies more. |
| Other C&C assets (art, sounds, voices) | Licensed to mods, revocably. The asset packs ship them on that licence. |
| Nothing above the game's age rating, no infringing third-party IP, no breaking EA's content protection | Applies to everything we add. |

## How it is checked

`scripts/ea_guidelines_check.py` checks that a Workshop description and the README open with the disclaimer, and
that an upload folder holds no music file. `package-for-workshop.sh` runs it on the mod and refuses a release that
fails; `asset_pack_workshop.py` runs it on each pack and refuses the item. The runbook's step 0 asks for a reread of
EA's page against anything new in the release (`workshop-publish-runbook.md`).

The TS-Music pack broke the music rule and is withdrawn (Private on the Workshop).
