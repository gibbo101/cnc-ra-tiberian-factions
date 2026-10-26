/*
**	The player settings file, Documents/CnCRemastered/tf_settings.ini, described in docs/player-settings.md.
*/
#include "tf_settings.h"

#include <windows.h>

#include <cstdio>
#include <cstdlib>

namespace {

const char SETTINGS_FILE[] = "tf_settings.ini";

int HostSidebar = TF_SIDEBAR_SENT | TF_SIDEBAR_SORT_BY_PRICE | TF_SIDEBAR_FACTION_BADGES;
int HouseSidebar[TF_SETTINGS_MAX_HOUSES];
bool AIClassic = false;
bool AIFairFog = true;
bool AIStagedWaves = true;
bool AINaval = true;
bool AIEarlyRadar = true;

/*
**	A house's sidebar bits: its launcher's when sent this match, else the host's file as the match read it.
*/
int Sidebar_Bits(int house)
{
    bool sent = house >= 0 && house < TF_SETTINGS_MAX_HOUSES && (HouseSidebar[house] & TF_SIDEBAR_SENT) != 0;
    return sent ? HouseSidebar[house] : HostSidebar;
}

} // namespace

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

void TF_Settings_Load(bool campaign)
{
    HostSidebar = TF_Settings_Sidebar_Bits();
    AIClassic = !campaign && !TF_Setting_On("AI", "TFAI");
    AIFairFog = campaign || (!AIClassic && TF_Setting_On("AI", "FairFog"));
    AIStagedWaves = campaign || (!AIClassic && TF_Setting_On("AI", "StagedWaves"));
    AINaval = campaign || (!AIClassic && TF_Setting_On("AI", "Naval"));
    AIEarlyRadar = campaign || (!AIClassic && TF_Setting_On("AI", "EarlyRadar"));
    for (int house = 0; house < TF_SETTINGS_MAX_HOUSES; house++) {
        HouseSidebar[house] = 0;
    }
}

int TF_Settings_Sidebar_Bits(void)
{
    return TF_SIDEBAR_SENT | (TF_Setting_On("Sidebar", "SortByPrice") ? TF_SIDEBAR_SORT_BY_PRICE : 0)
           | (TF_Setting_On("Sidebar", "FactionBadges") ? TF_SIDEBAR_FACTION_BADGES : 0);
}

void TF_Settings_Take_Sidebar(int house, int bits)
{
    if (house >= 0 && house < TF_SETTINGS_MAX_HOUSES && (bits & TF_SIDEBAR_SENT) != 0) {
        HouseSidebar[house] = bits;
    }
}

bool TF_Sidebar_Sorts_By_Price(int house)
{
    return (Sidebar_Bits(house) & TF_SIDEBAR_SORT_BY_PRICE) != 0;
}

bool TF_Sidebar_Has_Badges(int house)
{
    return (Sidebar_Bits(house) & TF_SIDEBAR_FACTION_BADGES) != 0;
}

bool TF_AI_Classic(void)
{
    return AIClassic;
}

bool TF_AI_Fair_Fog(void)
{
    return AIFairFog;
}

bool TF_AI_Staged_Waves(void)
{
    return AIStagedWaves;
}

bool TF_AI_Naval(void)
{
    return AINaval;
}

bool TF_AI_Early_Radar(void)
{
    return AIEarlyRadar;
}
