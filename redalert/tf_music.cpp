/*
**	Skirmish music by faction, inside ClientG.exe 1.153.745903. The launcher names a skirmish's
**	music `<prefix>_MUS_RA_MULTIPLAYER_MODE` (prefix RAR, RAC or RAB by audio setting); this asks
**	for `<prefix>_TF_MUS_<FACTION>` first and keeps the stock event when that one is missing.
*/
#include "function.h"
#include "tf_music.h"
#include "tf_launcher.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace {

struct MsvcString
{
    char buf[16];
    unsigned size;
    unsigned capacity;
};

const char* String_Chars(const MsvcString* s)
{
    return s->capacity >= 16 ? *(char* const*)s->buf : s->buf;
}

const SIZE_T AMBIENT_FIND_CALL = 0x169D018;
const SIZE_T MUSIC_FIND = 0xE92A90;
const SIZE_T LOBBY_FACTION = 0x20E0CF8;
const int LOBBY_TS_GDI = 7;
const char SKIRMISH_EVENT[] = "_MUS_RA_MULTIPLAYER_MODE";
const size_t PREFIX_LENGTH = 3;

typedef void*(__thiscall* MusicFindFn)(void* manager, const MsvcString* name);

/*
**	The playlist suffix for the local player's lobby faction, or NULL to keep the stock music.
*/
const char* Faction_Playlist(void)
{
    return *(const int*)LOBBY_FACTION == LOBBY_TS_GDI ? "TF_MUS_TSGDI" : NULL;
}

#if TF_DEV_BUILD
/*
**	One line per skirmish music lookup the hook answers, capped so a long match stays small.
*/
void Music_Log(const char* stock, const char* asked, bool found)
{
    static int lines = 0;
    const char* up = getenv("USERPROFILE");
    if (up == NULL || ++lines > 200) {
        return;
    }
    char path[512];
    snprintf(path, sizeof(path), "%s/Documents/CnCRemastered/tf_music.log", up);
    FILE* log = fopen(path, "a");
    if (log != NULL) {
        fprintf(log, "faction=%d stock=%s asked=%s %s\n", *(const int*)LOBBY_FACTION, stock, asked, found ? "FOUND" : "missing");
        fclose(log);
    }
}
#endif

/*
**	Stands in for the music manager's find-by-name at the ambient-music call: a skirmish event
**	is swapped for the faction playlist under the same prefix when that playlist exists.
*/
void* __fastcall Ambient_Find(void* manager, void*, const MsvcString* name)
{
    const char* chars = String_Chars(name);
    const char* playlist = Faction_Playlist();
    if (playlist != NULL && name->size == PREFIX_LENGTH + sizeof(SKIRMISH_EVENT) - 1
        && _stricmp(chars + PREFIX_LENGTH, SKIRMISH_EVENT) == 0) {
        static char text[64];
        int length = snprintf(text, sizeof(text), "%.3s_%s", chars, playlist);
        MsvcString ours = {};
        *(char**)ours.buf = text;
        ours.size = (unsigned)length;
        ours.capacity = sizeof(text) - 1;
        void* event = ((MusicFindFn)MUSIC_FIND)(manager, &ours);
#if TF_DEV_BUILD
        Music_Log(chars, text, event != NULL);
#endif
        if (event != NULL) {
            return event;
        }
    }
    return ((MusicFindFn)MUSIC_FIND)(manager, name);
}

/*
**	True when the `call` at `site` targets `stock_target`.
*/
bool Call_Ready(SIZE_T site, SIZE_T stock_target)
{
    unsigned char call[5] = {0xE8, 0, 0, 0, 0};
    TF_Put_Rel32(call + 1, site + 5, stock_target);
    return memcmp((const void*)site, call, sizeof(call)) == 0;
}

} // namespace

const char* TF_Music_Install(void)
{
    if (!Call_Ready(AMBIENT_FIND_CALL, MUSIC_FIND)) {
        return "music: ambient lookup not as expected, left alone";
    }
    unsigned char call[5] = {0xE8, 0, 0, 0, 0};
    TF_Put_Rel32(call + 1, AMBIENT_FIND_CALL + 5, (SIZE_T)&Ambient_Find);
    return TF_Write_Own_Code(AMBIENT_FIND_CALL, call, sizeof(call)) ? "music installed" : "music: write failed";
}
