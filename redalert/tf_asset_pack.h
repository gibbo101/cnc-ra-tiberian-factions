#ifndef TF_ASSET_PACK_H
#define TF_ASSET_PACK_H

class TechnoTypeClass;

/*
**	Notes a mod path the launcher registers; a TS-HD-Assets CCDATA folder carries TSHDPACK.INI,
**	which says the pack is enabled and gives its version.
*/
void TF_Note_Mod_Path(const char* mod_path);

/*
**	True when the TS-HD-Assets mod is enabled and new enough for this build: the TS art and audio
**	the mod's XML names live there, so without it every TS object draws as a missing tile.
*/
bool TF_TS_Pack_Present(void);

/*
**	Reads a pack marker file's Version=high.low; false when it is missing or has none. A pack is current when its
**	version is at least the one this build's XML needs.
*/
bool TF_Read_Pack_Marker(const char* marker_path, int* high, int* low);
bool TF_Pack_Version_Current(int high, int low);

/*
**	True for a type whose art and audio the TS-HD-Assets pack carries (IniName TS*, not RA's
**	Tesla TSLA*).
*/
bool TF_Is_TS_Pack_Type(TechnoTypeClass const* type);

/*
**	Queues the on-screen notice that TS factions need the pack, naming the side the player plays
**	instead; TF_Pack_Notice_Tick shows it once the match renders.
*/
void TF_Queue_Pack_Notice(const char* instead);
void TF_Pack_Notice_Tick(void);

#endif
