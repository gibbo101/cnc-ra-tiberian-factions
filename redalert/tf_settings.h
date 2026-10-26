#ifndef TF_SETTINGS_H
#define TF_SETTINGS_H

#include <stddef.h>

/*
**	The player's switches in Documents/CnCRemastered/tf_settings.ini (docs/player-settings.md). The match reads the
**	file once at its start; per-frame sites ask the functions below and never read the file.
*/
const int TF_SETTINGS_MAX_HOUSES = 32;

/*
**	The full path of a file in Documents/CnCRemastered; false without a user profile.
*/
bool TF_Documents_Path(const char* file, char* path, size_t size);

/*
**	Reads tf_settings.ini for the match and clears every house's sent choices; runs as a match starts or a save loads.
*/
void TF_Settings_Load(void);

/*
**	A launcher's sidebar switches travel to the host as mod command 4 at x = this mark, y = these bits.
*/
const int TF_SIDEBAR_CHOICE_MARK = 0x7E57;
const int TF_SIDEBAR_SORT_BY_PRICE = 0x1;
const int TF_SIDEBAR_FACTION_BADGES = 0x2;
const int TF_SIDEBAR_SENT = 0x100;

/*
**	This machine's sidebar switches as the bits a launcher sends, read from the file now.
*/
int TF_Settings_Sidebar_Bits(void);

/*
**	Host side: keeps a house's sidebar bits from its launcher, for this match.
*/
void TF_Settings_Take_Sidebar(int house, int bits);

/*
**	Whether a house's player sorts the sidebar by cost and wants faction badges: its launcher's choice when sent
**	this match, else the host's file as the match read it.
*/
bool TF_Sidebar_Sorts_By_Price(int house);
bool TF_Sidebar_Has_Badges(int house);

/*
**	One switch as the file holds it now: on unless its key says 0.
*/
bool TF_Setting_On(const char* section, const char* key);

/*
**	Saves one switch; on clears its key, the default. The match reads it at its next start.
*/
void TF_Setting_Set(const char* section, const char* key, bool on);

#endif
