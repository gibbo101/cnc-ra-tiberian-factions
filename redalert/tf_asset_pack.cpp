/*
**	The TS-HD-Assets dependency: the mod keeps the XML for its TS objects and the required pack
**	mod carries their art and audio (docs/asset-packs.md).
*/
#include "function.h"
#include "tf_asset_pack.h"

#include <cstdio>
#include <cstring>

extern void On_Message(const char* message, float timeout_seconds, long long message_id);

namespace {

// The oldest pack this build's XML can use: the art it names must exist in the pack.
const int PACK_NEEDS_HIGH = 1;
const int PACK_NEEDS_LOW = 0;
const char PACK_MARKER[] = "TSHDPACK.INI";

int PackHigh = -1;
int PackLow = -1;

char Notice[256];
bool NoticePending = false;

} // namespace

void TF_Note_Mod_Path(const char* mod_path)
{
    if (mod_path == NULL) {
        return;
    }
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "%s", mod_path);
    size_t len = strlen(path);
    while (len > 0 && (path[len - 1] == '\\' || path[len - 1] == '/')) {
        path[--len] = 0;
    }
    snprintf(path + len, sizeof(path) - len, "\\%s", PACK_MARKER);
    int high = -1, low = -1;
    if (TF_Read_Pack_Marker(path, &high, &low)) {
        PackHigh = high;
        PackLow = low;
    }
}

bool TF_Read_Pack_Marker(const char* marker_path, int* high, int* low)
{
    FILE* f = fopen(marker_path, "r");
    if (f == NULL) {
        return false;
    }
    bool found = false;
    char line[128];
    while (fgets(line, sizeof(line), f) != NULL) {
        found = found || sscanf(line, "Version=%d.%d", high, low) == 2;
    }
    fclose(f);
    return found;
}

bool TF_Pack_Version_Current(int high, int low)
{
    return (high > PACK_NEEDS_HIGH || (high == PACK_NEEDS_HIGH && low >= PACK_NEEDS_LOW));
}

bool TF_TS_Pack_Present(void)
{
    return TF_Pack_Version_Current(PackHigh, PackLow);
}

bool TF_Is_TS_Pack_Type(TechnoTypeClass const* type)
{
    return (type != NULL && _strnicmp(type->IniName, "TS", 2) == 0 && _strnicmp(type->IniName, "TSLA", 4) != 0);
}

void TF_Queue_Pack_Notice(const char* instead)
{
    const char* why = (PackHigh < 0) ? "need the Tiberian Sun HD Assets mod" : "need a newer Tiberian Sun HD Assets mod";
    snprintf(Notice,
             sizeof(Notice),
             "Tiberian Sun factions %s (version %d.%d or later): subscribe, enable it in Mods and restart. "
             "You are playing %s.",
             why,
             PACK_NEEDS_HIGH,
             PACK_NEEDS_LOW,
             instead);
    NoticePending = true;
}

void TF_Clear_Pack_Notice(void)
{
    NoticePending = false;
}

void TF_Pack_Notice_Tick(void)
{
    // Messages sent before the match renders are dropped, as the difficulty announcements' are.
    if (NoticePending && Frame >= 30) {
        On_Message(Notice, 30.0f, -1);
        NoticePending = false;
    }
}
