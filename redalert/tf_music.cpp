/*
**	The skirmish music and jukebox hooks inside ClientG.exe 1.153.745903, described in
**	docs/skirmish-music.md.
*/
#include "function.h"
#include "tf_music.h"
#include "tf_launcher.h"
#include "tf_settings.h"

#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace {

const SIZE_T AMBIENT_FIND_CALL = 0x169D018;
const SIZE_T MUSIC_FIND = 0xE92A90;
const SIZE_T LOBBY_FACTION = 0x20E0CF8;
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
**	Each lobby faction value's key in tf_music.ini: the lobby value is the country row plus two (GDI,
**	Nod, Soviets, Allies, then the duplicate rows, TS GDI on Germany's).
*/
const char* const FACTION_KEYS[] =
    {NULL, NULL, "GDI", "NOD", "SOVIETS", "ALLIES", "SOVIETS", "TSGDI", "ALLIES", "ALLIES"};

/*
**	The full path of Documents/CnCRemastered/tf_music.ini; false without a user profile.
*/
bool Settings_Path(char* path, size_t size)
{
    return TF_Documents_Path("tf_music.ini", path, size);
}

} // namespace

bool TF_TS_Music_Present(void)
{
    const MsvcString* roots = NULL;
    int count = TF_Mod_Roots(&roots);
    for (const MsvcString* root = roots; root < roots + count; root++) {
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

void TF_Music_Choice(const char* faction, char* value, DWORD size)
{
    snprintf(value, size, "MIX");
    char path[MAX_PATH];
    if (!Settings_Path(path, sizeof(path))) {
        return;
    }
    GetPrivateProfileStringA("Music", faction, "MIX", value, size, path);
    char* end = strchr(value, ';');
    end = (end != NULL) ? end : value + strlen(value);
    while (end > value && isspace((unsigned char)end[-1])) {
        end--;
    }
    *end = '\0';
}

void TF_Music_Set_Choice(const char* faction, const char* choice)
{
    char path[MAX_PATH];
    if (Settings_Path(path, sizeof(path))) {
        WritePrivateProfileStringA("Music", faction, _stricmp(choice, "MIX") == 0 ? NULL : choice, path);
    }
}

namespace {

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
**	The TF playlist for this skirmish: the lobby faction's own choice, MIX when unset.
*/
const char* Wanted_Playlist(void)
{
    int faction = *(const int*)LOBBY_FACTION;
    const char* key = (faction >= 0 && faction < (int)ARRAY_SIZE(FACTION_KEYS)) ? FACTION_KEYS[faction] : NULL;
    char choice[16] = "MIX";
    if (key != NULL) {
        TF_Music_Choice(key, choice, sizeof(choice));
    }
    return Playlist_For(choice, TF_TS_Music_Present());
}

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
        if (playlist != NULL) {
            static char text[64];
            snprintf(text, sizeof(text), "%.3s_TF_MUS_%s", chars, playlist);
            MsvcString ours = {};
            *(char**)ours.buf = text;
            ours.size = (unsigned)strlen(text);
            ours.capacity = sizeof(text) - 1;
            void* event = ((MusicFindFn)MUSIC_FIND)(manager, &ours);
            if (event != NULL) {
                return event;
            }
        }
    }
    return ((MusicFindFn)MUSIC_FIND)(manager, name);
}

/*
**	The jukebox manager's setup, after dropping the TS-Music tracks from the parsed list when no
**	enabled mod supplies them; never after setup, which must see the same length (docs/skirmish-music.md).
*/
bool __fastcall Jukebox_Init(void* manager, void*, bool start)
{
    if (!TF_TS_Music_Present()) {
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
