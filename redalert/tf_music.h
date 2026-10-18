#ifndef TF_MUSIC_H
#define TF_MUSIC_H

#include <windows.h>

/*
**	Installs the skirmish music and jukebox hooks; runs once when the launcher loads the DLL.
**	Returns a one-line result for the dev log.
*/
const char* TF_Music_Install(void);

/*
**	A faction's music choice (MIX, RA, TD or TS) from tf_music.ini, MIX when unset; `faction` is its key there:
**	ALLIES, SOVIETS, GDI, NOD or TSGDI.
*/
void TF_Music_Choice(const char* faction, char* value, DWORD size);

/*
**	Saves a faction's music choice; MIX clears its key, the default.
*/
void TF_Music_Set_Choice(const char* faction, const char* choice);

/*
**	True when an enabled mod supplies the TS-Music pack's tracks, so the launcher can play them.
*/
bool TF_TS_Music_Present(void);

#endif
