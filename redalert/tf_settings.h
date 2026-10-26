#ifndef TF_SETTINGS_H
#define TF_SETTINGS_H

#include <stddef.h>

/*
**	The player's switches from Documents/CnCRemastered/tf_settings.ini (docs/player-settings.md), as the match
**	reads them: every site tests a member here and never the file.
*/
struct TF_SettingsType
{
    bool IsSortByPrice;
    bool IsFactionBadges;
};

extern TF_SettingsType TF_Settings;

/*
**	The full path of a file in Documents/CnCRemastered; false without a user profile.
*/
bool TF_Documents_Path(const char* file, char* path, size_t size);

/*
**	Reads tf_settings.ini into TF_Settings; runs as a match starts or a save loads.
*/
void TF_Settings_Load(void);

/*
**	One switch as the file holds it now: on unless its key says 0.
*/
bool TF_Setting_On(const char* section, const char* key);

/*
**	Saves one switch; on clears its key, the default. The match reads it at its next start.
*/
void TF_Setting_Set(const char* section, const char* key, bool on);

#endif
