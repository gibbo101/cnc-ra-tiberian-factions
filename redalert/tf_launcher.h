#ifndef TF_LAUNCHER_H
#define TF_LAUNCHER_H

#include <windows.h>

/*
**	Patch helpers for code running inside ClientG.exe: write over the launcher's own code,
**	and encode a rel32 jump or call operand.
*/
bool TF_Write_Own_Code(SIZE_T at, const unsigned char* bytes, size_t len);
void TF_Put_Rel32(unsigned char* at, SIZE_T next, SIZE_T target);

/*
**	An MSVC std::string as ClientG lays it out: inline when capacity is under 16, else a heap pointer
**	in the first four bytes.
*/
struct MsvcString
{
    char buf[16];
    unsigned size;
    unsigned capacity;
};

/*
**	The characters of an MSVC std::string, inline or on the heap.
*/
const char* TF_String_Chars(const MsvcString* s);

/*
**	This session's mod roots as ClientG lists them: their count, with the first in `first`; 0 when unreadable.
*/
int TF_Mod_Roots(const MsvcString** first);

/*
**	True when the `call` at `site` in ClientG targets `stock_target`; TF_Redirect_Call then points it
**	at `hook`.
*/
bool TF_Call_Ready(SIZE_T site, SIZE_T stock_target);
bool TF_Redirect_Call(SIZE_T site, SIZE_T hook);

/*
**	Installs the mod's launcher hooks; runs once when the launcher loads the DLL. Returns a
**	one-line result for the dev log.
*/
const char* TF_Launcher_Install(void);

/*
**	Takes the map a carrier campaign launch asked for (written by the launcher side, under a
**	minute old); false when there is none, and always in a Workshop build. Consumes the request.
*/
bool TF_Launcher_Take_Carrier_Map(char* map, size_t size);

#endif
