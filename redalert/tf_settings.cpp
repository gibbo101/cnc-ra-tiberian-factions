/*
**	The player settings file, Documents/CnCRemastered/tf_settings.ini, described in docs/player-settings.md.
*/
#include "tf_settings.h"

#include <windows.h>

#include <cstdio>
#include <cstdlib>

namespace {

const char SETTINGS_FILE[] = "tf_settings.ini";

} // namespace

TF_SettingsType TF_Settings = {true, true};

bool TF_Documents_Path(const char* file, char* path, size_t size)
{
    const char* up = getenv("USERPROFILE");
    if (up == NULL) {
        return false;
    }
    snprintf(path, size, "%s\\Documents\\CnCRemastered\\%s", up, file);
    return true;
}

bool TF_Setting_On(const char* section, const char* key)
{
    char path[MAX_PATH];
    if (!TF_Documents_Path(SETTINGS_FILE, path, sizeof(path))) {
        return true;
    }
    return GetPrivateProfileIntA(section, key, 1, path) != 0;
}

void TF_Setting_Set(const char* section, const char* key, bool on)
{
    char path[MAX_PATH];
    if (TF_Documents_Path(SETTINGS_FILE, path, sizeof(path))) {
        WritePrivateProfileStringA(section, key, on ? NULL : "0", path);
    }
}

void TF_Settings_Load(void)
{
    TF_Settings.IsSortByPrice = TF_Setting_On("Sidebar", "SortByPrice");
    TF_Settings.IsFactionBadges = TF_Setting_On("Sidebar", "FactionBadges");
}
