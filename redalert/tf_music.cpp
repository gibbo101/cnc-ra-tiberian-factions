/*
**	Skirmish music by faction, inside ClientG.exe 1.153.745903. The launcher names a skirmish's
**	music `<prefix>_MUS_RA_MULTIPLAYER_MODE` (prefix RAR, RAC or RAB by audio setting); this asks
**	for `<prefix>_TF_MUS_<LIST>` first, by the player's soundtrack setting and lobby faction, and
**	keeps the stock event when that one is missing.
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
const SIZE_T MOD_ROOTS = 0x1FE4C28;
const char SKIRMISH_EVENT[] = "_MUS_RA_MULTIPLAYER_MODE";
const size_t PREFIX_LENGTH = 3;
const char TS_MUSIC_PROBE[] = "\\Data\\AUDIO\\MUSIC\\TS_MUS_VALVES.WAV";

const SIZE_T JUKEBOX_INIT_CALL = 0x15CF40E;
const SIZE_T JUKEBOX_INIT = 0xEA3530;
const SIZE_T JUKEBOX_TRACKS_BEGIN = 0x2038734;
const SIZE_T JUKEBOX_TRACKS_END = 0x2038738;
const size_t JUKEBOX_TRACK_SIZE = 0x5C;
const DWORD JUKEBOX_TRACK_STRINGS[] = {0x00, 0x1C, 0x34};
const DWORD JUKEBOX_TRACK_FILE = 0x1C;
const SIZE_T CLIENT_FREE = 0x950B20;
const char TS_TRACK_PREFIX[] = "TS_MUS_";

typedef void*(__thiscall* MusicFindFn)(void* manager, const MsvcString* name);
typedef bool(__thiscall* JukeboxInitFn)(void* manager, bool start);
typedef void(__cdecl* ClientFreeFn)(void* block);

/*
**	The playlist each lobby faction value plays under the Faction setting: the lobby value is the
**	country row plus two (GDI, Nod, Soviet, Allies, then the duplicate rows, TS GDI on Germany's).
*/
const char* const FACTION_LISTS[] = {NULL, NULL, "TD", "TD", "RA", "RA", "RA", "TS", "RA", "RA"};

/*
**	True when an enabled mod supplies the TS-Music pack's tracks, so the launcher can play them.
*/
bool TS_Music_Present(void)
{
    const MsvcString* const* roots = (const MsvcString* const*)MOD_ROOTS;
    for (const MsvcString* root = roots[0]; root != NULL && root < roots[1]; root++) {
        char path[MAX_PATH];
        const char* chars = String_Chars(root);
        size_t length = root->size;
        while (length > 0 && (chars[length - 1] == '\\' || chars[length - 1] == '/')) {
            length--;
        }
        snprintf(path, sizeof(path), "%.*s%s", (int)length, chars, TS_MUSIC_PROBE);
        if (GetFileAttributesA(path) != INVALID_FILE_ATTRIBUTES) {
            return true;
        }
    }
    return false;
}

/*
**	The player's soundtrack setting (FACTION, MIX, RA, TD or TS) from Documents/CnCRemastered/
**	tf_music.ini, FACTION when unset.
*/
void Read_Soundtrack(char* setting, size_t size)
{
    snprintf(setting, size, "FACTION");
    const char* up = getenv("USERPROFILE");
    if (up == NULL) {
        return;
    }
    char path[512];
    snprintf(path, sizeof(path), "%s/Documents/CnCRemastered/tf_music.ini", up);
    FILE* file = fopen(path, "r");
    if (file == NULL) {
        return;
    }
    char line[64];
    char value[16];
    while (fgets(line, sizeof(line), file) != NULL) {
        if (sscanf(line, "Soundtrack=%15s", value) == 1) {
            snprintf(setting, size, "%s", value);
        }
    }
    fclose(file);
}

/*
**	The TF playlist to ask for (RA, TD, TS or MIX), or NULL to keep the stock rotation, which is
**	also what MIX falls back to without the TS music.
*/
const char* Wanted_Playlist(void)
{
    char setting[16];
    Read_Soundtrack(setting, sizeof(setting));
    bool ts = TS_Music_Present();
    int faction = *(const int*)LOBBY_FACTION;
    const char* by_faction = (faction >= 0 && faction < (int)ARRAY_SIZE(FACTION_LISTS)) ? FACTION_LISTS[faction] : NULL;
    if (_stricmp(setting, "RA") == 0) {
        return "RA";
    }
    if (_stricmp(setting, "TD") == 0) {
        return "TD";
    }
    if (_stricmp(setting, "MIX") == 0) {
        return ts ? "MIX" : NULL;
    }
    if (_stricmp(setting, "TS") == 0 && ts) {
        return "TS";
    }
    return (by_faction != NULL && (strcmp(by_faction, "TS") != 0 || ts)) ? by_faction : NULL;
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
        fprintf(log,
                "faction=%d ts_music=%d stock=%s asked=%s %s\n",
                *(const int*)LOBBY_FACTION,
                TS_Music_Present() ? 1 : 0,
                stock,
                asked,
                found ? "FOUND" : "missing");
        fclose(log);
    }
}
#endif

/*
**	Stands in for the music manager's find-by-name at the ambient-music call: a skirmish event
**	is swapped for the wanted TF playlist under the same prefix when that playlist exists.
*/
void* __fastcall Ambient_Find(void* manager, void*, const MsvcString* name)
{
    const char* chars = String_Chars(name);
    if (name->size == PREFIX_LENGTH + sizeof(SKIRMISH_EVENT) - 1 && _stricmp(chars + PREFIX_LENGTH, SKIRMISH_EVENT) == 0) {
        const char* playlist = Wanted_Playlist();
        static char text[64];
        snprintf(text, sizeof(text), "%.3s_TF_MUS_%s", chars, playlist != NULL ? playlist : "(stock)");
        void* event = NULL;
        if (playlist != NULL) {
            MsvcString ours = {};
            *(char**)ours.buf = text;
            ours.size = (unsigned)strlen(text);
            ours.capacity = sizeof(text) - 1;
            event = ((MusicFindFn)MUSIC_FIND)(manager, &ours);
        }
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
**	The jukebox manager's setup, after dropping the TS-Music tracks from the parsed jukebox list
**	when no enabled mod supplies them. It must run before setup: the jukebox screen needs the
**	parsed list and the manager's records to stay the same length.
*/
bool __fastcall Jukebox_Init(void* manager, void*, bool start)
{
    if (!TS_Music_Present()) {
        char* begin = *(char**)JUKEBOX_TRACKS_BEGIN;
        char* end = *(char**)JUKEBOX_TRACKS_END;
        char* kept = begin;
        for (char* track = begin; track != NULL && track < end; track += JUKEBOX_TRACK_SIZE) {
            if (_strnicmp(String_Chars((const MsvcString*)(track + JUKEBOX_TRACK_FILE)), TS_TRACK_PREFIX, sizeof(TS_TRACK_PREFIX) - 1)
                == 0) {
                for (size_t i = 0; i < ARRAY_SIZE(JUKEBOX_TRACK_STRINGS); i++) {
                    MsvcString* text = (MsvcString*)(track + JUKEBOX_TRACK_STRINGS[i]);
                    if (text->capacity >= 16) {
                        ((ClientFreeFn)CLIENT_FREE)(*(void**)text->buf);
                    }
                }
                continue;
            }
            if (kept != track) {
                memmove(kept, track, JUKEBOX_TRACK_SIZE);
            }
            kept += JUKEBOX_TRACK_SIZE;
        }
        if (begin != NULL) {
            *(char**)JUKEBOX_TRACKS_END = kept;
        }
    }
    return ((JukeboxInitFn)JUKEBOX_INIT)(manager, start);
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

/*
**	Points the `call` at `site` at `hook`. Call_Ready must hold.
*/
bool Redirect_Call(SIZE_T site, SIZE_T hook)
{
    unsigned char call[5] = {0xE8, 0, 0, 0, 0};
    TF_Put_Rel32(call + 1, site + 5, hook);
    return TF_Write_Own_Code(site, call, sizeof(call));
}

} // namespace

const char* TF_Music_Install(void)
{
    if (!Call_Ready(AMBIENT_FIND_CALL, MUSIC_FIND) || !Call_Ready(JUKEBOX_INIT_CALL, JUKEBOX_INIT)) {
        return "music: launcher calls not as expected, left alone";
    }
    return Redirect_Call(AMBIENT_FIND_CALL, (SIZE_T)&Ambient_Find) && Redirect_Call(JUKEBOX_INIT_CALL, (SIZE_T)&Jukebox_Init)
               ? "music installed"
               : "music: write failed";
}
