# Startup intro

The mod replaces Red Alert's startup movie (the metal logo slam and targeting scope) with its own:
the fire Tiberian Factions title slams in on Hell March's first hit, the six faction emblems pop
in one per beat, then a montage of Red Alert, Tiberian Dawn and Tiberian Sun FMV cut to the beat
in a steel-framed window, ending in a white flash to the main menu. 37.3 s, 1920x1080, 30 fps.

- `shots.tsv` is the cut: movie, first frame, length in beats (one beat = 15 frames at 30 fps).
- `intro_cut.py` renders it: `preview <out.mp4>` for a 720p review copy, `frames <dir>` for the
  1080p frames and the music cut that the Bink encode takes.
- `build_intro.sh` does the whole build and installs the result as
  `resources/remaster_mods/Vanilla_RA/Data/ART/MOVIES/RA/REDINTRO.BK2`.
- `REDINTRO.md5` is the checksum of the locked cut. The movie is gitignored (about 136 MB, over
  GitHub's 100 MB file limit); `package-for-workshop.sh` stops if the staged copy doesn't match.

## How the launcher plays it

`ClientG.exe` names the movie `RA/REDINTRO` with no extension and reads the format from the
header. A loose `Data/ART/MOVIES/RA/REDINTRO.BK2` in the mod replaces the stock one. Bink 1 and
Bink 2 both play; Theora data hangs startup on a black screen, and a loose `.OGV` beside it is
ignored. We encode Bink 1, because RAD Video Tools (free) makes it.

## The FMV library

The source footage is not in the repo. It is a decoded library of every C&C Remastered, Tiberian
Dawn and Tiberian Sun movie, with contact sheets and a catalog, kept at `~/Desktop/tf-intro-fmv`
(override with `TF_FMV_LIB`). Its own README covers rebuilding it. `fmv_tools/` here is a snapshot
of its tool sources:

- `bk2dump.c`: decodes Bink 2 frames through the game's own `bink2w32.dll` under Wine
  (cross-compile with `i686-w64-mingw32-gcc`; the DLL is RAD's and comes from the game install,
  so it is not kept here).
- `fmvlib.py`, `meg.py`, `tsmix.py`: decode, sample and pull frames from the game archives
  (MEG for Remastered, MIX for Tiberian Sun).
- `radvideo.sh`: runs RAD Video Tools' `binkc`/`binkmix` unattended on a private Xvfb.
