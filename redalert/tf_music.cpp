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
**	Each lobby faction value's key in tf_music.ini and its soundtrack by default: the lobby value is
**	the country row plus two (GDI, Nod, Soviets, Allies, then the duplicate rows, TS GDI on Germany's).
*/
struct FactionMusic
{
    const char* Key;
    const char* Default;
};

const FactionMusic FACTION_MUSIC[] = {{NULL, NULL},
                                      {NULL, NULL},
                                      {"GDI", "TD"},
                                      {"Nod", "TD"},
                                      {"Soviets", "RA"},
                                      {"Allies", "RA"},
                                      {"Soviets", "RA"},
                                      {"TSGDI", "TS"},
                                      {"Allies", "RA"},
                                      {"Allies", "RA"}};

/*
**	True when an enabled mod supplies the TS-Music pack's tracks, so the launcher can play them.
*/
bool TS_Music_Present(void)
{
    const MsvcString* const* roots = (const MsvcString* const*)MOD_ROOTS;
    for (const MsvcString* root = roots[0]; root != NULL && root < roots[1]; root++) {
        char path[MAX_PATH];
        const char* chars = TF_String_Chars(root);
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
**	A key of the [Music] section of Documents/CnCRemastered/tf_music.ini, which the Settings page
**	writes, or `fallback` when it is unset.
*/
void Music_Setting(const char* key, const char* fallback, char* value, DWORD size)
{
    snprintf(value, size, "%s", fallback);
    const char* up = getenv("USERPROFILE");
    if (up == NULL) {
        return;
    }
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "%s\\Documents\\CnCRemastered\\tf_music.ini", up);
    GetPrivateProfileStringA("Music", key, fallback, value, size, path);
}

/*
**	The TF playlist a soundtrack choice (RA, TD, TS or MIX) asks for, or NULL to keep the stock
**	rotation, which is also what a choice needing the missing TS music gets.
*/
const char* Playlist_For(const char* choice, bool ts)
{
    if (_stricmp(choice, "RA") == 0) {
        return "RA";
    }
    if (_stricmp(choice, "TD") == 0) {
        return "TD";
    }
    if (_stricmp(choice, "TS") == 0) {
        return ts ? "TS" : NULL;
    }
    if (_stricmp(choice, "MIX") == 0) {
        return ts ? "MIX" : NULL;
    }
    return NULL;
}

/*
**	The TF playlist for this skirmish: the Soundtrack setting (MIX by default), or under FACTION
**	the lobby faction's own choice.
*/
const char* Wanted_Playlist(void)
{
    char setting[16];
    Music_Setting("Soundtrack", "MIX", setting, sizeof(setting));
    bool ts = TS_Music_Present();
    if (_stricmp(setting, "FACTION") != 0) {
        return Playlist_For(setting, ts);
    }
    int faction = *(const int*)LOBBY_FACTION;
    if (faction < 0 || faction >= (int)ARRAY_SIZE(FACTION_MUSIC) || FACTION_MUSIC[faction].Key == NULL) {
        return NULL;
    }
    char choice[16];
    Music_Setting(FACTION_MUSIC[faction].Key, FACTION_MUSIC[faction].Default, choice, sizeof(choice));
    return Playlist_For(choice, ts);
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
    const char* chars = TF_String_Chars(name);
    if (name->size == PREFIX_LENGTH + sizeof(SKIRMISH_EVENT) - 1
        && _stricmp(chars + PREFIX_LENGTH, SKIRMISH_EVENT) == 0) {
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
            if (_strnicmp(TF_String_Chars((const MsvcString*)(track + JUKEBOX_TRACK_FILE)),
                          TS_TRACK_PREFIX,
                          sizeof(TS_TRACK_PREFIX) - 1)
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

} // namespace

const char* TF_Music_Install(void)
{
    if (!TF_Call_Ready(AMBIENT_FIND_CALL, MUSIC_FIND) || !TF_Call_Ready(JUKEBOX_INIT_CALL, JUKEBOX_INIT)) {
        return "music: launcher calls not as expected, left alone";
    }
    return TF_Redirect_Call(AMBIENT_FIND_CALL, (SIZE_T)&Ambient_Find)
                   && TF_Redirect_Call(JUKEBOX_INIT_CALL, (SIZE_T)&Jukebox_Init)
               ? "music installed"
               : "music: write failed";
}
