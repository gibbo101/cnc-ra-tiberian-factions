# Startup intro

The mod replaces Red Alert's startup movie (the metal logo slam and targeting scope) with its own,
42.3 s, 1920x1080, 30 fps:

1. **Logo (0-3.8 s), to the stock intro's own logo tune.** The fire Tiberian Factions title slams in
   on the hit where the stock C&C logo appears; the six faction emblems pop in on the metal slams
   that land the RED ALERT letters.
2. **A breath (3.8-4.27 s).** The logo tune is cut where the stock intro moves on to its scope.
3. **Montage (from 4.27 s).** A flash cuts to a Red Alert / Tiberian Dawn / Tiberian Sun FMV montage
   in a steel-framed window, on Hell March's (Remastered) opening hit: 16 two-second shots, then
   eight half-second cuts from the band's entry.
4. **Ending.** On the final downbeat a white flash; Hell March fades out under it, and the main menu
   fades in its own music, the Hell March Retaliation remix (`scripts/musicevents_build.py`).

## Why the breath

On slower machines (the Steam Deck) the launcher freezes every startup movie, the stock one too,
for about a second some 3.85-4.1 s in: it handles its Workshop database reply as the movie starts
and then hashes every local custom map on the main thread (`log/EventsLog_0.txt`, `[pgugc]` lines;
backlog item in `docs/todo.md`). The freeze stops the movie's clock, so picture and sound pause and
then carry on. Cutting the logo tune just before that window and starting Hell March just after it
means the freeze lands in silence on a still frame and nothing audible is cut. Desktop PCs do the
hashing too fast to notice.

## Files

- `shots.tsv` is the montage: movie, first frame, length in beats (one beat = 15 frames at 30 fps).
- `intro_cut.py` renders it: `preview <out.mp4>` for a 720p review copy, `frames <dir>` for the
  1080p frames and the music the Bink encode takes. Timings (logo hits, the breath, Hell March's
  entry) are constants at its top.
- `build_intro.sh` does the whole build and installs the result as
  `resources/remaster_mods/Vanilla_RA/Data/ART/MOVIES/RA/REDINTRO.BK2`. It reproduces the movie byte
  for byte.
- `REDINTRO.md5` is the checksum of the shipping cut. The movie is gitignored, like the UI atlas;
  `package-for-workshop.sh` stops if the staged copy doesn't match.
- `fetch_sources.py` rebuilds the source library (below) from the game installs in seconds.

## How the launcher plays it

`ClientG.exe` names the movie `RA/REDINTRO` with no extension and reads the format from the
header. A loose `Data/ART/MOVIES/RA/REDINTRO.BK2` in the mod replaces the stock one. Bink 1 and
Bink 2 both play; Theora data hangs startup on a black screen, and a loose `.OGV` beside it is
ignored. We encode Bink 1 at 1.5 MB/s (about the stock intro's rate), because RAD Video Tools (free)
makes it. The launcher shows the movie darker in the shadows than a texture of the same value (a
dark tone v displays as about 1.08 v - 9); `menu_art.py` matches the menu's margins to that.

The launcher fits the movie inside the screen and, about 10 s in, reveals the main menu wherever
the movie doesn't cover it. The movie is 16:9; on 16:10 screens (the Steam Deck) the bands above
and below show the menu background's margins, which `menu_art.py` fills with the same smoke.

## The source library

The footage and music are not in the repo. `fetch_sources.py` builds what the cut needs at
`$TF_FMV_LIB` (default `~/Desktop/Tiberian Factions/tf-intro-lib`): a record per movie in
`shots.tsv` (Remastered Bink 2 movies read in place from their MEG, Tiberian Sun VQAs copied out of
their MIX), Hell March and the stock logo tune in `audio/`, and the decoding tools. `fmv_tools/` holds
their sources:

- `bk2dump.c`: decodes Bink 2 frames through the game's own `bink2w32.dll` under Wine (built with
  `i686-w64-mingw32-gcc`; the DLL comes from the game install and is not kept here).
- `fmvlib.py`, `meg.py`, `tsmix.py`: pull frames from the game archives (MEG for Remastered, MIX for
  Tiberian Sun).
- `radvideo.sh`: runs RAD Video Tools' `binkc`/`binkmix` unattended on a private Xvfb. RAD Video
  Tools itself is installed in a Wine prefix at `~/.local/opt/wine-fmv`.
