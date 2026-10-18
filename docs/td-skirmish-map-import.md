# TD skirmish maps in the RA mod

**Status:** Parked. The 31 converted TD maps and the TD terrain art (temperate, winter, desert) are
out of the mod from 5.0.0, in `parked/td-maps/` (`TF_TD_MAPS` 0 in `redalert/defines.h`): they
raised video-memory use for everyone, and some were broken. They are planned as their own Workshop
item; the folder's README says how to bring them back.

`scripts/td_map_to_ra.py` converts TD maps to RA format (temperate, winter and desert), and the DLL
installs a mod's `CustomMaps/` triplets into `Local_Custom_Maps/Red_Alert/` itself when `TF_TD_MAPS`
is on (`TF_Install_Bundled_Maps`, when the launcher registers the mod's CCDATA path, overwriting
earlier copies; with `TF_TD_MAPS` 0 the installed copies are deleted). It has to: a Workshop mod
can't ship files into Documents. The Official list takes new maps through the carrier
(`td-base-art.md`), which is where the TD maps go next.
The parked maps play desert on the interior theatre slot, with TD's cacti and rocks dropped. Their
replacement is TD's own theatres, desert, temperate and winter, as theatres of their own
(`td-base-art.md`).

