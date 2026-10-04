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
**	Binds the mod's own main-menu buttons, by widget name, to the mod's handlers; runs once
**	when the launcher loads the DLL. Returns a one-line result for the dev log.
*/
const char* TF_Launcher_Menu_Install(void);

#endif
