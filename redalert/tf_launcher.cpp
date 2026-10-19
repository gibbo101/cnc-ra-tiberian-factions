/*
**	The mod's launcher layer: code that runs inside ClientG.exe 1.153.745903, installed when
**	the launcher loads the DLL at startup. Addresses are that build's. The campaign page it
**	drives is described in docs/campaigns-page.md.
*/
#include "function.h"
#include "tf_launcher.h"
#include "tf_encyclopedia.h"
#include "tf_asset_pack.h"
#include "tf_music.h"

extern "C" {
#include "puff.h"
}

#include <cstdio>
#include <cstdlib>
#include <cctype>
#include <cstring>
#include <d3d11.h>

const char* TF_String_Chars(const MsvcString* s)
{
    return s->capacity >= 16 ? *(char* const*)s->buf : s->buf;
}

bool TF_Call_Ready(SIZE_T site, SIZE_T stock_target)
{
    unsigned char call[5] = {0xE8, 0, 0, 0, 0};
    TF_Put_Rel32(call + 1, site + 5, stock_target);
    return memcmp((const void*)site, call, sizeof(call)) == 0;
}

bool TF_Redirect_Call(SIZE_T site, SIZE_T hook)
{
    unsigned char call[5] = {0xE8, 0, 0, 0, 0};
    TF_Put_Rel32(call + 1, site + 5, hook);
    return TF_Write_Own_Code(site, call, sizeof(call));
}

namespace {

const SIZE_T WIDGET_FIND = 0xF0D980;
const int WIDGET_SET_HIDDEN = 0x78;

struct MsvcWString
{
    union
    {
        wchar_t Buffer[8];
        wchar_t* Pointer;
    };
    unsigned Size;
    unsigned Capacity;
};

typedef void*(__thiscall* WidgetFindFn)(void* scene, const MsvcString* name);
typedef void*(__thiscall* AsWidgetFn)(void* owner, int zero, void* widget);
typedef void(__thiscall* SetHiddenFn)(void* widget, int hidden);

/*
**	A named widget of a screen or list row, through ClientG's own find and type cast; NULL
**	when absent. A name over 15 characters is lent in place: the find only reads it.
*/
void* Find_Widget(void* owner, const char* name, SIZE_T cast)
{
    MsvcString text = {};
    size_t length = strlen(name);
    if (length > 15) {
        *(const char**)text.buf = name;
        text.capacity = (unsigned)length;
    } else {
        memcpy(text.buf, name, length + 1);
        text.capacity = 15;
    }
    text.size = (unsigned)length;
    void* widget = ((WidgetFindFn)WIDGET_FIND)(*(void**)((char*)owner + 4), &text);
    return widget == NULL ? NULL : ((AsWidgetFn)cast)(owner, 0, widget);
}

/*
**	Hides or shows a widget through its own virtual call; NULL is ignored.
*/
void Set_Hidden(void* widget, bool hidden)
{
    if (widget != NULL) {
        ((SetHiddenFn)(*(SIZE_T**)widget)[WIDGET_SET_HIDDEN / 4])(widget, hidden ? 1 : 0);
    }
}

/*
**	True when `size` bytes at `cave`, in ClientG's code padding, are still unused.
*/
bool Cave_Is_Free(SIZE_T cave, int size)
{
    for (int i = 0; i < size; i++) {
        if (((const unsigned char*)cave)[i] != 0) {
            return false;
        }
    }
    return true;
}

/*
**	True when `function` starts with `stock` (position independent, 5 to 27 bytes) and `cave`
**	has room for them and a jump back, so Detour can move them there.
*/
bool Detour_Ready(SIZE_T function, const unsigned char* stock, size_t length, SIZE_T cave)
{
    return length >= 5 && length <= 27 && memcmp((const void*)function, stock, length) == 0
           && Cave_Is_Free(cave, (int)(length + 5));
}

/*
**	Moves a function's first instructions into `cave` with a jump back, then points the function
**	at `hook`; the cave becomes the stock function. Detour_Ready must hold.
*/
bool Detour(SIZE_T function, const unsigned char* stock, size_t length, SIZE_T cave, SIZE_T hook)
{
    unsigned char trampoline[32];
    memcpy(trampoline, stock, length);
    trampoline[length] = 0xE9;
    TF_Put_Rel32(trampoline + length + 1, cave + length + 5, function + length);
    unsigned char jump[32];
    memset(jump, 0x90, length);
    jump[0] = 0xE9;
    TF_Put_Rel32(jump + 1, function + 5, hook);
    return TF_Write_Own_Code(cave, trampoline, length + 5) && TF_Write_Own_Code(function, jump, length);
}

/*
**	True when `at` starts with `stock` (position independent, 5 to 17 bytes) and `cave` has
**	room for a register-snapshot stub around them.
*/
bool Snapshot_Ready(SIZE_T at, const unsigned char* stock, size_t length, SIZE_T cave)
{
    return length >= 5 && length <= 17 && memcmp((const void*)at, stock, length) == 0
           && Cave_Is_Free(cave, (int)(15 + length));
}

/*
**	A register-snapshot hook: pushfd / pushad / push esp / call `hit` / popad / popfd /
**	displaced instructions / jmp back. `hit` reads the pushad block (edi first).
*/
bool Snapshot_Hook(SIZE_T at, const unsigned char* stock, size_t length, SIZE_T cave, SIZE_T hit)
{
    unsigned char stub[32] = {0x9C, 0x60, 0x54, 0xE8};
    TF_Put_Rel32(stub + 4, cave + 8, hit);
    stub[8] = 0x61;
    stub[9] = 0x9D;
    memcpy(stub + 10, stock, length);
    stub[10 + length] = 0xE9;
    TF_Put_Rel32(stub + 11 + length, cave + 15 + length, at + length);
    unsigned char jump[32];
    memset(jump, 0x90, length);
    jump[0] = 0xE9;
    TF_Put_Rel32(jump + 1, at + 5, cave);
    return TF_Write_Own_Code(cave, stub, 15 + length) && TF_Write_Own_Code(at, jump, length);
}

/*
**	Instance fields the campaign page reads. The house is ClientG's ExternalFactionType.
*/
const DWORD INSTANCE_FACTION = 0x488;
const DWORD INSTANCE_MISSION = 0x48C;
const DWORD INSTANCE_EXPANSION = 0x54C;
const DWORD INSTANCE_CUSTOM = 0x6A4;
const DWORD INSTANCE_NO_LABEL = 0x1B2;
const DWORD INSTANCE_GAME = 0x4C8;
const DWORD GAME_RED_ALERT = 2;
const DWORD EXPANSION_ANT = 3;
enum
{
    FACTION_GDI = 0,
    FACTION_NOD = 1,
    FACTION_SPAIN = 3,
    FACTION_FRANCE = 6,
    FACTION_USSR = 7,
    FACTION_UKRAINE = 8
};

/*
**	A 32-bit field of a ClientG instance record.
*/
DWORD Instance_Field(const void* instance, DWORD offset)
{
    return *(const DWORD*)((const char*)instance + offset);
}

const SIZE_T EXPANSION_ALLIED_CALL = 0x63382F;
const SIZE_T EXPANSION_SOVIET_CALL = 0x633878;
const SIZE_T IS_ALLIED_SIDE = 0x118E830;
const SIZE_T IS_SOVIET_SIDE = 0x118E840;

/*
**	Side tests for expansion missions on the campaign page: GDI missions join the Allied
**	expansion tab and Nod missions the Soviet one, which the page shows as GDI and Nod.
*/
bool __fastcall Expansion_Allied_Side(const void* instance)
{
    DWORD faction = Instance_Field(instance, INSTANCE_FACTION);
    return faction == FACTION_GDI || (faction >= FACTION_SPAIN && faction <= FACTION_FRANCE);
}

bool __fastcall Expansion_Soviet_Side(const void* instance)
{
    DWORD faction = Instance_Field(instance, INSTANCE_FACTION);
    return faction == FACTION_NOD || faction == FACTION_USSR || faction == FACTION_UKRAINE;
}

const SIZE_T ROW_STYLE_BRANCH = 0x632FFA;
const SIZE_T ROW_STYLE_DONE = 0x633013;
const SIZE_T STYLE_GDI = 0x64E740;
const SIZE_T STYLE_NOD = 0x64E770;
const SIZE_T STYLE_ALLIED = 0x64E710;
const SIZE_T STYLE_SOVIET = 0x64E7A0;
const SIZE_T AS_GROUP = 0x5EA140;
const SIZE_T AS_ICON_BUTTON = 0x5F90E0;
const SIZE_T SET_NO_INPUT = 0xF80BC0;
const SIZE_T SET_TOGGLED = 0xF80920;
const SIZE_T ROW_SELECT = 0x64E680;
const SIZE_T SELECT_CAVE = 0x1BE9570;
const DWORD ROW_GROUPS[4] = {0x74, 0x78, 0x7C, 0x80};

typedef void(__thiscall* RowStyleFn)(void* row);
typedef bool(__thiscall* SideTestFn)(const void* instance);
typedef void(__thiscall* SetFlagFn)(void* button, bool value);
typedef void(__thiscall* SetToggledFn)(void* button, bool on, int a, int b);
typedef void(__thiscall* RowSelectFn)(void* row, bool selected);

/*
**	Crest groups the row file adds beyond the stock four, each shown for one house on one tab.
*/
struct ExtraRowStyle
{
    DWORD Faction;
    DWORD Expansion;
    const char* Group;
    const char* Button;
};

const ExtraRowStyle ExtraRowStyles[] = {
    {FACTION_GDI, EXPANSION_ANT, "TF_Row_TSGDI", "TF_Row_TSGDI_B"},
};
const int EXTRA_ROW_STYLES = sizeof(ExtraRowStyles) / sizeof(ExtraRowStyles[0]);

/*
**	Campaign page row style (crest art) from the mission's own house and tab, so any faction's
**	mission looks like its faction on any tab; unknown houses keep the stock choice.
*/
void __fastcall Row_Style(void* row, const void* instance)
{
    DWORD faction = Instance_Field(instance, INSTANCE_FACTION);
    DWORD expansion = Instance_Field(instance, INSTANCE_EXPANSION);
    int extra = -1;
    for (int i = 0; i < EXTRA_ROW_STYLES; i++) {
        if (ExtraRowStyles[i].Faction == faction && ExtraRowStyles[i].Expansion == expansion) {
            extra = i;
        }
    }
    for (int i = 0; i < EXTRA_ROW_STYLES; i++) {
        void* button = Find_Widget(row, ExtraRowStyles[i].Button, AS_ICON_BUTTON);
        if (button != NULL) {
            ((SetFlagFn)SET_NO_INPUT)(button, false);
        }
        Set_Hidden(Find_Widget(row, ExtraRowStyles[i].Group, AS_GROUP), i != extra);
    }
    if (extra >= 0) {
        for (int i = 0; i < 4; i++) {
            Set_Hidden(*(void**)((char*)row + ROW_GROUPS[i]), true);
        }
        return;
    }
    SIZE_T style;
    if (faction == FACTION_GDI) {
        style = STYLE_GDI;
    } else if (faction == FACTION_NOD) {
        style = STYLE_NOD;
    } else if (faction == FACTION_USSR || faction == FACTION_UKRAINE) {
        style = STYLE_SOVIET;
    } else {
        style = ((SideTestFn)IS_ALLIED_SIDE)(instance) ? STYLE_ALLIED : STYLE_SOVIET;
    }
    ((RowStyleFn)style)(row);
}

/*
**	Row selection: the stock four buttons, then the added crest groups' buttons.
*/
void __fastcall Row_Select(void* row, void*, bool selected)
{
    ((RowSelectFn)SELECT_CAVE)(row, selected);
    for (int i = 0; i < EXTRA_ROW_STYLES; i++) {
        void* button = Find_Widget(row, ExtraRowStyles[i].Button, AS_ICON_BUTTON);
        if (button != NULL) {
            ((SetToggledFn)SET_TOGGLED)(button, selected, 0, 1);
        }
    }
}

const SIZE_T TAB_SWITCH = 0x633E60;
const SIZE_T TAB_CAVE = 0x1BE9580;
const SIZE_T TAB_RECORD = 0x62CEE0;
const SIZE_T LIST_COUNT = 0xF6E320;
const SIZE_T AS_TEXT = 0x5A1110;
const DWORD SCREEN_TAB_RECORDS = 0x12C;
const DWORD SCREEN_CURRENT_TAB = 0x154;
const DWORD RECORD_LIST = 0x20;
const int CUSTOM_TAB = 11;

typedef void(__thiscall* TabSwitchFn)(void* screen, int tab);
typedef void*(__thiscall* TabRecordFn)(void* records, const int* tab);
typedef int(__thiscall* ListCountFn)(void* list);

/*
**	Campaign page tab switch: the stock switch, then COMING SOON over the list while the open
**	campaign tab has no missions. The Custom tab holds players' own missions and never shows it.
*/
void __fastcall Tab_Switch(void* screen, void*, int tab)
{
    ((TabSwitchFn)TAB_CAVE)(screen, tab);
    char* base = (char*)screen;
    int current = *(const int*)(base + SCREEN_CURRENT_TAB);
    int count = 0;
    if (current != 0) {
        char* record = (char*)((TabRecordFn)TAB_RECORD)(base + SCREEN_TAB_RECORDS, &current);
        void* list = record == NULL ? NULL : *(void**)(record + RECORD_LIST);
        count = list == NULL ? 0 : ((ListCountFn)LIST_COUNT)(list);
    }
    Set_Hidden(Find_Widget(screen, "TF_Coming_Soon", AS_TEXT), count > 0 || current == CUSTOM_TAB);
}

const SIZE_T MISSION_LABEL = 0x118D710;
const SIZE_T LABEL_CAVE = 0x1BE9560;
const SIZE_T TEXT_MANAGER = 0x1FE4CE8;
const SIZE_T TEXT_LOOKUP = 0x9C1590;
const SIZE_T WSTRING_ASSIGN = 0x578DF0;

typedef MsvcWString*(__thiscall* MissionLabelFn)(const void* instance, MsvcWString* out);
typedef MsvcWString*(__thiscall* TextLookupFn)(void* manager, MsvcWString* out, const char* key);
typedef void(__thiscall* WStringAssignFn)(MsvcWString* self, const wchar_t* text, unsigned size);

/*
**	The mission's label on the campaign page: a GDI or Nod mission reads as its faction and
**	number ("GDI 1", "TS GDI 1" on the Tiberian Sun tab); any other mission, Tiberian Dawn's own
**	included, keeps the stock label.
*/
MsvcWString* __fastcall Mission_Label(const void* instance, void*, MsvcWString* out)
{
    DWORD faction = Instance_Field(instance, INSTANCE_FACTION);
    bool ours = (faction == FACTION_GDI || faction == FACTION_NOD) && Instance_Field(instance, INSTANCE_GAME) == GAME_RED_ALERT
                && Instance_Field(instance, INSTANCE_CUSTOM) == 0 && ((const char*)instance)[INSTANCE_NO_LABEL] == 0;
    if (!ours) {
        return ((MissionLabelFn)LABEL_CAVE)(instance, out);
    }
    const char* key = "TEXT_TF_LABEL_NOD";
    if (faction == FACTION_GDI) {
        key = Instance_Field(instance, INSTANCE_EXPANSION) == EXPANSION_ANT ? "TEXT_TF_LABEL_TSGDI" : "TEXT_TF_LABEL_GDI";
    }
    ((TextLookupFn)TEXT_LOOKUP)((void*)TEXT_MANAGER, out, key);
    wchar_t text[64];
    const wchar_t* name = out->Capacity >= 8 ? out->Pointer : out->Buffer;
    int length = _snwprintf(text, 63, L"%.40ls %lu", name, Instance_Field(instance, INSTANCE_MISSION));
    text[63] = 0;
    if (length < 0) {
        length = (int)wcslen(text);
    }
    ((WStringAssignFn)WSTRING_ASSIGN)(out, text, (unsigned)length);
    return out;
}

/*
**	Installs the campaign page's hooks, every site checked before any is written. The RA row
**	style choice becomes: mov edx,ebx (instance) / mov ecx,edi (row) / call Row_Style / jmp.
*/
const char* Campaign_Page_Install(void)
{
    static const unsigned char style_stock[14] = {0x8B, 0xCB, 0xE8, 0x2F, 0xB8, 0xB5, 0x00, 0x8B, 0xCF, 0x84, 0xC0, 0x74, 0x07, 0xE8};
    static const unsigned char select_stock[6] = {0x55, 0x8B, 0xEC, 0x56, 0x8B, 0xF1};
    static const unsigned char tab_stock[7] = {0x55, 0x8B, 0xEC, 0x51, 0x8B, 0x45, 0x08};
    static const unsigned char label_stock[9] = {0x55, 0x8B, 0xEC, 0x81, 0xEC, 0x84, 0x01, 0x00, 0x00};
    if (!TF_Call_Ready(EXPANSION_ALLIED_CALL, IS_ALLIED_SIDE) || !TF_Call_Ready(EXPANSION_SOVIET_CALL, IS_SOVIET_SIDE)
        || memcmp((const void*)ROW_STYLE_BRANCH, style_stock, sizeof(style_stock)) != 0
        || !Detour_Ready(ROW_SELECT, select_stock, sizeof(select_stock), SELECT_CAVE)
        || !Detour_Ready(TAB_SWITCH, tab_stock, sizeof(tab_stock), TAB_CAVE)
        || !Detour_Ready(MISSION_LABEL, label_stock, sizeof(label_stock), LABEL_CAVE)) {
        return "campaign page: unknown launcher build, left alone";
    }
    unsigned char style[14] = {0x8B, 0xD3, 0x8B, 0xCF, 0xE8, 0, 0, 0, 0, 0xE9, 0, 0, 0, 0};
    TF_Put_Rel32(style + 5, ROW_STYLE_BRANCH + 9, (SIZE_T)&Row_Style);
    TF_Put_Rel32(style + 10, ROW_STYLE_BRANCH + 14, ROW_STYLE_DONE);
    if (!TF_Redirect_Call(EXPANSION_ALLIED_CALL, (SIZE_T)&Expansion_Allied_Side)
        || !TF_Redirect_Call(EXPANSION_SOVIET_CALL, (SIZE_T)&Expansion_Soviet_Side)
        || !TF_Write_Own_Code(ROW_STYLE_BRANCH, style, sizeof(style))
        || !Detour(ROW_SELECT, select_stock, sizeof(select_stock), SELECT_CAVE, (SIZE_T)&Row_Select)
        || !Detour(TAB_SWITCH, tab_stock, sizeof(tab_stock), TAB_CAVE, (SIZE_T)&Tab_Switch)
        || !Detour(MISSION_LABEL, label_stock, sizeof(label_stock), LABEL_CAVE, (SIZE_T)&Mission_Label)) {
        return "campaign page: write failed";
    }
    return "campaign page installed";
}


/*
**	The asset packs the mod requires, as the launcher sees them in its own mod list: loaded (one of this
**	session's mod roots holds the pack's marker), switched on for the next start, switched off, or missing.
*/
const SIZE_T MOD_ROOTS = 0x1FE4C28;
const SIZE_T MOD_MANAGER_GET = 0x5E8CB0;
const DWORD MOD_RECORD_SIZE = 0xBC;
const DWORD MOD_FOLDER = 0x78;
const DWORD MOD_ID = 0xA8;
const DWORD MOD_ENABLED = 0xB9;

enum AddOnKind
{
    KIND_ASSETS,
    KIND_THEATRES,
    KIND_CAMPAIGNS,
    KIND_COUNT
};

struct PackInfo
{
    const char* Marker;              // the file every copy of the pack carries, from its folder
    const char* Id;                  // its logo's id (scripts/pack_panel_art.py PACK_LOGOS)
    const char* WorkshopId;          // its Red Alert Workshop item
    const wchar_t* NeededFor;        // the faction that needs it; NULL when none does
    const wchar_t* Name;             // as the ADD-ONS screen lists it; the font reads & as a shortcut, && as one &
    const wchar_t* Description[2];   // the ADD-ONS screen's two lines on it, & written as &&
    AddOnKind Kind;                  // its tab on the ADD-ONS screen
    const char* Needs[2];            // the Ids of the packs it can't work without
};

// One row per pack on the ADD-ONS screen, in PACK_LOGOS order (asset_packs.WORKSHOP); the menu's notice shows while
// any of them is not on.
const PackInfo PACKS[] = {
    {"CCDATA\\TSHDPACK.INI",
     "TSHD",
     "3819642604",
     L"THE TIBERIAN SUN GDI FACTION",
     L"TIBERIAN SUN HD ASSETS",
     {L"Units, buildings, effects, voices and EVA", L"from Tiberian Sun, rebuilt in HD."},
     KIND_ASSETS,
     {NULL, NULL}},
    {"CCDATA\\TSMUSIC.INI",
     "TSMUSIC",
     "3822605221",
     NULL,
     L"TIBERIAN SUN MUSIC",
     {L"Tiberian Sun and Firestorm's 26 in-game themes,", L"for the skirmish music and the jukebox."},
     KIND_ASSETS,
     {NULL, NULL}},
};
const int PACK_COUNT = sizeof(PACKS) / sizeof(PACKS[0]);
const int TS_HD_PACK = 0;

enum PackState
{
    PACK_ENABLED,
    PACK_OUTDATED,      // loaded, but older than this build's XML needs
    PACK_OFF_NEXT_START, // loaded, but switched off for the next start
    PACK_ON_NEXT_START,
    PACK_INSTALLED_OFF,
    PACK_DOWNLOADED,  // in its Workshop folder and this account subscribes, but not yet in the launcher's mod list
    PACK_DOWNLOADING, // subscribed, and Steam is still downloading it
    PACK_MISSING
};

struct MsvcStringVector
{
    MsvcString* First;
    MsvcString* Last;
    MsvcString* End;
};

typedef void*(__cdecl* ModManagerFn)(void);

/*
**	True when the mod folder `folder` holds `marker`.
*/
bool Has_Pack_Marker(const char* folder, const char* marker)
{
    char path[MAX_PATH];
    size_t length = strlen(folder);
    const char* slash = (length > 0 && (folder[length - 1] == '\\' || folder[length - 1] == '/')) ? "" : "\\";
    snprintf(path, sizeof(path), "%s%s%s", folder, slash, marker);
    return GetFileAttributesA(path) != INVALID_FILE_ATTRIBUTES;
}

/*
**	The launcher's mod manager, whose mod list the Mods screen shows; NULL on another launcher build.
*/
char* Mod_Manager(void)
{
    static const unsigned char getter[7] = {0xA1, 0x10, 0x45, 0xFA, 0x01, 0x85, 0xC0};
    if (memcmp((const void*)MOD_MANAGER_GET, getter, sizeof(getter)) != 0) {
        return NULL;
    }
    return (char*)((ModManagerFn)MOD_MANAGER_GET)();
}

/*
**	The folder of the pack's Workshop download (the item folder's subfolder holding the marker), beside the
**	game's install; false when it hasn't downloaded.
*/
bool Downloaded_Pack_Folder(int pack, char* out, size_t size)
{
    char item[MAX_PATH];
    DWORD length = GetModuleFileNameA(NULL, item, sizeof(item));
    char* name = length > 0 && length < sizeof(item) ? strrchr(item, '\\') : NULL;
    if (name == NULL) {
        return false;
    }
    snprintf(name, sizeof(item) - (name - item), "\\..\\..\\workshop\\content\\1213210\\%s", PACKS[pack].WorkshopId);
    char pattern[MAX_PATH];
    snprintf(pattern, sizeof(pattern), "%s\\*", item);
    WIN32_FIND_DATAA found;
    HANDLE find = FindFirstFileA(pattern, &found);
    if (find == INVALID_HANDLE_VALUE) {
        return false;
    }
    bool any = false;
    do {
        if ((found.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) && found.cFileName[0] != '.') {
            snprintf(out, size, "%s\\%s", item, found.cFileName);
            any = Has_Pack_Marker(out, PACKS[pack].Marker) && Has_Pack_Marker(out, "ccmod.json");
        }
    } while (!any && FindNextFileA(find, &found));
    FindClose(find);
    return any;
}

/*
**	Steam's progress on a subscribed pack still downloading, in percent (0 before the size is known); -1 when
**	Steam isn't downloading it.
*/
typedef void*(__cdecl* SteamUgcFn)(void);
typedef unsigned(__cdecl* ItemStateFn)(void* ugc, unsigned long long item);
typedef bool(__cdecl* ItemDownloadInfoFn)(void* ugc,
                                          unsigned long long item,
                                          unsigned long long* done,
                                          unsigned long long* total);
const unsigned ITEM_SUBSCRIBED = 1;
const unsigned ITEM_INSTALLED = 4;
const unsigned ITEM_DOWNLOADING = 16;
const unsigned ITEM_DOWNLOAD_PENDING = 32;

/*
**	A function steam_api.dll exports; NULL without Steam.
*/
FARPROC Steam_Export(const char* name)
{
    HMODULE steam = GetModuleHandleA("steam_api.dll");
    return steam != NULL ? GetProcAddress(steam, name) : NULL;
}

/*
**	Steam's Workshop interface; NULL without Steam.
*/
void* Steam_Ugc(void)
{
    SteamUgcFn get = (SteamUgcFn)Steam_Export("SteamAPI_SteamUGC_v018");
    return get != NULL ? get() : NULL;
}

int Pack_Download_Percent(int pack)
{
    ItemStateFn state = (ItemStateFn)Steam_Export("SteamAPI_ISteamUGC_GetItemState");
    ItemDownloadInfoFn info = (ItemDownloadInfoFn)Steam_Export("SteamAPI_ISteamUGC_GetItemDownloadInfo");
    void* ugc = Steam_Ugc();
    if (ugc == NULL || state == NULL || info == NULL) {
        return -1;
    }
    unsigned long long item = strtoull(PACKS[pack].WorkshopId, NULL, 10);
    unsigned flags = state(ugc, item);
    if (!(flags & ITEM_SUBSCRIBED) || !(flags & (ITEM_DOWNLOADING | ITEM_DOWNLOAD_PENDING))) {
        return -1;
    }
    unsigned long long done = 0, total = 0;
    if (!info(ugc, item, &done, &total) || total == 0) {
        return 0;
    }
    return (int)(done * 100 / total);
}

/*
**	True when the signed-in Steam account subscribes to the pack, or Steam can't say: the launcher lists only its
**	account's subscriptions, though every account on the machine shares the Workshop folder.
*/
bool Pack_Subscribed(int pack)
{
    ItemStateFn state = (ItemStateFn)Steam_Export("SteamAPI_ISteamUGC_GetItemState");
    void* ugc = Steam_Ugc();
    if (ugc == NULL || state == NULL) {
        return true;
    }
    return (state(ugc, strtoull(PACKS[pack].WorkshopId, NULL, 10)) & ITEM_SUBSCRIBED) != 0;
}

/*
**	Subscribes the player to a pack's Workshop item and asks Steam for it at high priority, which downloads it
**	while the game runs (Steam otherwise holds downloads until the game quits). False without Steam.
*/
typedef unsigned long long(__cdecl* SubscribeItemFn)(void* ugc, unsigned long long item);
typedef bool(__cdecl* DownloadItemFn)(void* ugc, unsigned long long item, bool high_priority);

bool Subscribe_Pack(int pack)
{
    SubscribeItemFn subscribe = (SubscribeItemFn)Steam_Export("SteamAPI_ISteamUGC_SubscribeItem");
    DownloadItemFn download = (DownloadItemFn)Steam_Export("SteamAPI_ISteamUGC_DownloadItem");
    void* ugc = Steam_Ugc();
    if (subscribe == NULL || ugc == NULL) {
        return false;
    }
    unsigned long long item = strtoull(PACKS[pack].WorkshopId, NULL, 10);
    subscribe(ugc, item);
    if (download != NULL) {
        download(ugc, item, true);
    }
    return true;
}

// Packs downloaded this session and added to the profile's enabled list, which the mod list shows on the next start.
bool PackQueued[PACK_COUNT];

/*
**	A pack as the launcher's mod list has it: switched on for the next start if any copy is, switched off if
**	every copy is, or missing when it lists none.
*/
PackState Listed_State(const char* marker)
{
    PackState state = PACK_MISSING;
    char* mm = Mod_Manager();
    if (mm != NULL) {
        char* last = *(char**)(mm + 0x1C);
        for (char* r = *(char**)(mm + 0x18); r != NULL && r < last; r += MOD_RECORD_SIZE) {
            if (Has_Pack_Marker(TF_String_Chars((const MsvcString*)(r + MOD_FOLDER)), marker)) {
                PackState found = *(const unsigned char*)(r + MOD_ENABLED) ? PACK_ON_NEXT_START : PACK_INSTALLED_OFF;
                state = found < state ? found : state;
            }
        }
    }
    return state;
}

/*
**	A pack's state, from this session's mod roots, the launcher's mod list, its Workshop folder and Steam.
*/
PackState Pack_State(int pack)
{
    const char* marker = PACKS[pack].Marker;
    const MsvcString* roots = NULL;
    int count = TF_Mod_Roots(&roots);
    for (const MsvcString* root = roots; root < roots + count; root++) {
        if (Has_Pack_Marker(TF_String_Chars(root), marker)) {
            char path[MAX_PATH];
            snprintf(path, sizeof(path), "%s\\%s", TF_String_Chars(root), marker);
            int high = -1, low = -1;
            bool current = PACKS[pack].NeededFor == NULL
                           || (TF_Read_Pack_Marker(path, &high, &low) && TF_Pack_Version_Current(high, low));
            if (!current) {
                return PACK_OUTDATED;
            }
            return Listed_State(marker) == PACK_INSTALLED_OFF ? PACK_OFF_NEXT_START : PACK_ENABLED;
        }
    }
    PackState state = Listed_State(marker);
    char folder[MAX_PATH];
    if (state == PACK_MISSING && Pack_Subscribed(pack) && Downloaded_Pack_Folder(pack, folder, sizeof(folder))) {
        state = PackQueued[pack] ? PACK_ON_NEXT_START : PACK_DOWNLOADED;
    }
    if (state == PACK_MISSING && Pack_Download_Percent(pack) >= 0) {
        state = PACK_DOWNLOADING;
    }
    return state;
}

/*
**	True when this session has the pack loaded: on, out of date, or switched off only from the next start.
*/
bool Pack_Loaded(PackState state)
{
    return state == PACK_ENABLED || state == PACK_OUTDATED || state == PACK_OFF_NEXT_START;
}

/*
**	ClientG's message box: body text and one OK button, closed by the player.
*/
const SIZE_T SHOW_DIALOG = 0x1502EA0;
const SIZE_T CLIENT_FREE = 0x950B20;

struct DialogCallback
{
    void* Target;
    SIZE_T Invoker;
};

typedef void(__cdecl* ShowDialogFn)(const DialogCallback* callback,
                                    const MsvcWString* body,
                                    const MsvcWString* button_key,
                                    const MsvcWString* button_text,
                                    const MsvcWString* second_key,
                                    int a,
                                    int b,
                                    int c,
                                    int d,
                                    int e,
                                    const MsvcString* f,
                                    const MsvcString* g,
                                    const MsvcString* h);
typedef void(__cdecl* ClientFreeFn)(void* block);

void __fastcall Dialog_Closed(void*, void*, int)
{
}

// The action a two-button message box runs when its action button is clicked; the box reports that button as 2.
const int DIALOG_ACTION_BUTTON = 2;
void (*DialogAction)(void) = NULL;

void __fastcall Dialog_Choice(void*, void*, int button)
{
    void (*action)(void) = DialogAction;
    DialogAction = NULL;
    if (button == DIALOG_ACTION_BUTTON && action != NULL) {
        action();
    }
}

void Free_WString(MsvcWString* s)
{
    if (s->Capacity >= 8) {
        ((ClientFreeFn)CLIENT_FREE)(s->Pointer);
    }
}

/*
**	ClientG's message box with `action_text` on its first button, which runs `action`, and OK on the second;
**	with no action, OK alone.
*/
void Show_Message(const wchar_t* body, const wchar_t* action_text = NULL, void (*action)(void) = NULL)
{
    MsvcWString text = {};
    text.Capacity = 7;
    ((WStringAssignFn)WSTRING_ASSIGN)(&text, body, (unsigned)wcslen(body));
    MsvcWString none = {};
    none.Capacity = 7;
    MsvcWString second = {};
    second.Capacity = 7;
    MsvcWString ok = {};
    ok.Capacity = 7;
    MsvcString f = {}, g = {}, h = {};
    f.capacity = g.capacity = h.capacity = 15;
    if (action == NULL) {
        ((TextLookupFn)TEXT_LOOKUP)((void*)TEXT_MANAGER, &ok, "TEXT_OK");
        DialogCallback callback = {NULL, (SIZE_T)&Dialog_Closed};
        ((ShowDialogFn)SHOW_DIALOG)(&callback, &text, &none, &ok, &second, 1, 1, 0, 2, 3, &f, &g, &h);
    } else {
        ((WStringAssignFn)WSTRING_ASSIGN)(&ok, action_text, (unsigned)wcslen(action_text));
        ((WStringAssignFn)WSTRING_ASSIGN)(&second, L"TEXT_OK", 7);
        DialogAction = action;
        static int target = 0;
        DialogCallback callback = {&target, (SIZE_T)&Dialog_Choice};
        ((ShowDialogFn)SHOW_DIALOG)(&callback, &text, &none, &ok, &second, 1, 0, 0, 0, 3, &f, &g, &h);
    }
    Free_WString(&text);
    Free_WString(&ok);
    Free_WString(&second);
}

/*
**	The message box for a lobby slot playing Tiberian Sun GDI without the pack enabled; one box at
**	a time, so a lobby full of TS GDI slots, or the slot echoing the player's own pick, shows one.
*/
const DWORD PACK_POPUP_HOLD_MS = 10000;

void Open_AddOns(int pack);

/*
**	Leaves the skirmish lobby as its Back button does: cancels the game, closes the lobby and returns to the main
**	menu, which stays alive underneath. True with no lobby open; false when one is but its Back button is unusable.
*/
const SIZE_T LOBBY_HOLDER = 0x1FA8050;
const SIZE_T LOBBY_BACK = 0x71C790;
const DWORD LOBBY_SCREEN = 0x4;
const DWORD LOBBY_OBJECT = 0x330;
const DWORD LOBBY_CLOSED_FLAGS = 0xBF;
const DWORD LOBBY_BACK_BUTTON = 0x5C;
const DWORD WIDGET_USABLE = 0x70;

typedef void(__thiscall* LobbyBackFn)(void* lobby, int unused);
typedef bool(__thiscall* WidgetUsableFn)(void* widget);

bool Leave_Lobby(void)
{
    char* holder = *(char**)LOBBY_HOLDER;
    unsigned char* screen = holder != NULL ? *(unsigned char**)(holder + LOBBY_SCREEN) : NULL;
    if (screen == NULL || (screen[LOBBY_CLOSED_FLAGS] & 8)) {
        return true;
    }
    char* lobby = *(char**)(screen + LOBBY_OBJECT);
    void* back = lobby != NULL ? *(void**)(lobby + LOBBY_BACK_BUTTON) : NULL;
    if (back == NULL || !((WidgetUsableFn)(*(SIZE_T**)back)[WIDGET_USABLE / 4])(back)) {
        return false;
    }
    ((LobbyBackFn)LOBBY_BACK)(lobby, 0);
    return true;
}

/*
**	The lobby popup's GO TO ADD-ONS: on the next UI tick, outside the message box's own click, back to the main
**	menu, then the ADD-ONS screen over it with the Tiberian Sun pack selected.
*/
const UINT LOBBY_LEAVE_DELAY_MS = 50;

void CALLBACK Lobby_AddOns_Tick(HWND, UINT, UINT_PTR timer, DWORD)
{
    KillTimer(NULL, timer);
    if (Leave_Lobby()) {
        Open_AddOns(TS_HD_PACK);
    }
}

void Lobby_AddOns(void)
{
    SetTimer(NULL, 0, LOBBY_LEAVE_DELAY_MS, Lobby_AddOns_Tick);
}

void Pack_Popup(void)
{
    static DWORD shown = 0;
    PackState state = Pack_State(TS_HD_PACK);
    DWORD now = GetTickCount();
    if (Pack_Loaded(state) || (shown != 0 && now - shown < PACK_POPUP_HOLD_MS)) {
        return;
    }
    shown = now;
    const wchar_t* body =
        state == PACK_OUTDATED ? L"Tiberian Sun GDI needs a newer Tiberian Sun HD Assets mod. Let Steam update it, "
                                 L"then restart the game."
        : state == PACK_DOWNLOADING ? L"Tiberian Sun GDI needs the Tiberian Sun HD Assets mod, which Steam is still "
                                      L"downloading."
        : state == PACK_MISSING ? L"Tiberian Sun GDI needs the Tiberian Sun HD Assets mod, free on the Steam Workshop."
                                : L"Tiberian Sun GDI needs the Tiberian Sun HD Assets mod, which is installed but not "
                                  L"loaded.";
    Show_Message(body, L"GO TO ADD-ONS", &Lobby_AddOns);
}

/*
**	The lobby's faction pick, the player's own or for an AI slot: the stock handler, then the pack popup when
**	the pick turned a slot to Tiberian Sun GDI.
*/
const SIZE_T FACTION_PICKED = 0x676760;
const SIZE_T FACTION_PICKED_CAVE = 0x1BE95C0;
const SIZE_T LOBBY_FACTION = 0x20E0CF8;
const DWORD SLOT_FACTION = 0x1DA8;
const int LOBBY_TS_GDI = 7;

typedef void(__thiscall* FactionPickedFn)(void* slot, int event);

void __fastcall Faction_Picked(void* slot, void*, int event)
{
    int before = *(const int*)LOBBY_FACTION;
    int slot_before = *(const int*)((const char*)slot + SLOT_FACTION);
    ((FactionPickedFn)FACTION_PICKED_CAVE)(slot, event);
    int after = *(const int*)LOBBY_FACTION;
    int slot_after = *(const int*)((const char*)slot + SLOT_FACTION);
    if ((after != before && after == LOBBY_TS_GDI) || (slot_after != slot_before && slot_after == LOBBY_TS_GDI)) {
        Pack_Popup();
    }
}

/*
**	A lobby slot taking its faction from the lobby's settings, the player's own or an AI's, as
**	the lobby opens or updates: the pack popup when a slot turns to Tiberian Sun GDI.
*/
const SIZE_T SLOT_SET_FACTION = 0x677950;
const SIZE_T SLOT_SET_FACTION_CAVE = 0x1BE9650;

typedef void(__thiscall* SlotSetFactionFn)(void* slot, int faction);

void __fastcall Slot_Set_Faction(void* slot, void*, int faction)
{
    int before = *(const int*)((const char*)slot + SLOT_FACTION);
    ((SlotSetFactionFn)SLOT_SET_FACTION_CAVE)(slot, faction);
    int after = *(const int*)((const char*)slot + SLOT_FACTION);
    if (after != before && after == LOBBY_TS_GDI) {
        Pack_Popup();
    }
}

/*
**	A pack's Workshop page in the Steam overlay.
*/
typedef void*(__cdecl* SteamFriendsFn)(void);
typedef void(__cdecl* OverlayToWebPageFn)(void* friends, const char* url, int mode);

void Open_Pack_Page(int pack)
{
    char url[96];
    snprintf(url, sizeof(url), "https://steamcommunity.com/sharedfiles/filedetails/?id=%s", PACKS[pack].WorkshopId);
    SteamFriendsFn get = (SteamFriendsFn)Steam_Export("SteamAPI_SteamFriends_v017");
    OverlayToWebPageFn open = (OverlayToWebPageFn)Steam_Export("SteamAPI_ISteamFriends_ActivateGameOverlayToWebPage");
    void* friends = get ? get() : NULL;
    if (friends != NULL && open != NULL) {
        open(friends, url, 0);
    }
}

/*
**	Switching packs on, as the Mods screen's checkbox does, and restarting the game, as its RESTART NOW does.
*/
const SIZE_T SET_MOD_ENABLED = 0x7BB7A0;
const SIZE_T PROFILE = 0x20E0CB0;
const SIZE_T PROFILE_SAVE = 0x14D8420;
const SIZE_T RESTART_MESSAGE = 0x1177810;
const SIZE_T POST_TO_LAUNCHER = 0x11790F0;
const SIZE_T LAUNCHER_LINK = 0x1FAD3CC;
const DWORD RESTART_WAIT_MS = 5000;

const SIZE_T PROFILE_ENABLED_MODS = 0x20E0D88;
const SIZE_T CLIENT_NEW = 0x9509A0;

typedef void(__thiscall* SetModEnabledFn)(void* mm, DWORD id, int on);
typedef void*(__cdecl* ClientNewFn)(size_t size);

struct DwordVector
{
    DWORD* First;
    DWORD* Last;
    DWORD* End;
};

/*
**	The launcher's ID for a mod folder: zlib's CRC-32 of its ccmod.json name followed by "high.low"; 0 if unreadable.
*/
DWORD Mod_Id(const char* folder)
{
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "%s\\ccmod.json", folder);
    FILE* f = fopen(path, "r");
    if (f == NULL) {
        return 0;
    }
    char text[2048];
    size_t length = fread(text, 1, sizeof(text) - 1, f);
    fclose(f);
    text[length] = 0;
    const char* name = strstr(text, "\"name\"");
    const char* high = strstr(text, "\"version_high\"");
    const char* low = strstr(text, "\"version_low\"");
    const char* colon = name != NULL ? strchr(name + 6, ':') : NULL;
    name = colon != NULL ? strchr(colon, '"') : NULL;
    const char* name_end = name != NULL ? strchr(name + 1, '"') : NULL;
    high = high != NULL ? strchr(high, ':') : NULL;
    low = low != NULL ? strchr(low, ':') : NULL;
    int h = -1, l = -1;
    if (name_end == NULL || high == NULL || low == NULL || sscanf(high + 1, "%d", &h) != 1
        || sscanf(low + 1, "%d", &l) != 1) {
        return 0;
    }
    char key[256];
    int size = snprintf(key, sizeof(key), "%.*s%d.%d", (int)(name_end - name - 1), name + 1, h, l);
    if (size <= 0 || size >= (int)sizeof(key)) {
        return 0;
    }
    DWORD crc = 0xFFFFFFFF;
    for (int i = 0; i < size; i++) {
        crc ^= (unsigned char)key[i];
        for (int bit = 0; bit < 8; bit++) {
            crc = (crc >> 1) ^ (0xEDB88320 & (0 - (crc & 1)));
        }
    }
    return ~crc;
}

/*
**	Adds a mod ID to the profile's enabled list, growing it on the launcher's own heap, so the next start loads
**	a mod the launcher hasn't listed yet.
*/
void Profile_Enable(DWORD id)
{
    DwordVector* list = (DwordVector*)PROFILE_ENABLED_MODS;
    for (DWORD* p = list->First; p != NULL && p < list->Last; p++) {
        if (*p == id) {
            return;
        }
    }
    size_t size = list->First != NULL ? list->Last - list->First : 0;
    size_t capacity = list->First != NULL ? list->End - list->First : 0;
    if (size == capacity) {
        size_t grown = capacity < 8 ? 8 : capacity * 2;
        DWORD* block = (DWORD*)((ClientNewFn)CLIENT_NEW)(grown * sizeof(DWORD));
        if (block == NULL) {
            return;
        }
        if (size > 0) {
            memcpy(block, list->First, size * sizeof(DWORD));
        }
        if (list->First != NULL) {
            ((ClientFreeFn)CLIENT_FREE)(list->First);
        }
        list->First = block;
        list->Last = block + size;
        list->End = block + grown;
    }
    *list->Last++ = id;
}
/*
**	Takes a mod ID out of the profile's enabled list.
*/
void Profile_Remove(DWORD id)
{
    DwordVector* list = (DwordVector*)PROFILE_ENABLED_MODS;
    for (DWORD* p = list->First; p != NULL && p < list->Last; p++) {
        if (*p == id) {
            memmove(p, p + 1, (list->Last - p - 1) * sizeof(DWORD));
            list->Last--;
            return;
        }
    }
}

typedef void(__thiscall* ProfileSaveFn)(void* profile, int a, int notify, int immediate);
typedef void*(__cdecl* RestartMessageFn)(void);
typedef void(__thiscall* PostToLauncherFn)(void* link, void* message);

/*
**	Switches on the packs in `packs` (a bit per pack) that are installed but off or downloaded, and saves the
**	profile; the next start loads them.
*/
void Enable_Packs(unsigned packs)
{
    char* mm = Mod_Manager();
    if (mm == NULL) {
        return;
    }
    PackState states[PACK_COUNT];
    for (int pack = 0; pack < PACK_COUNT; pack++) {
        states[pack] = Pack_State(pack);
    }
    for (int pack = 0; pack < PACK_COUNT; pack++) {
        if (!(packs & (1u << pack)) || (states[pack] != PACK_INSTALLED_OFF && states[pack] != PACK_OFF_NEXT_START)) {
            continue;
        }
        char* last = *(char**)(mm + 0x1C);
        for (char* r = *(char**)(mm + 0x18); r != NULL && r < last; r += MOD_RECORD_SIZE) {
            if (Has_Pack_Marker(TF_String_Chars((const MsvcString*)(r + MOD_FOLDER)), PACKS[pack].Marker)) {
                ((SetModEnabledFn)SET_MOD_ENABLED)(mm, *(const DWORD*)(r + MOD_ID), 1);
                break;
            }
        }
    }
    // Set_Mod_Enabled rebuilds the profile list from the mod list, so downloaded packs' IDs go in after it.
    for (int pack = 0; pack < PACK_COUNT; pack++) {
        char folder[MAX_PATH];
        bool wanted = (packs & (1u << pack)) && states[pack] == PACK_DOWNLOADED;
        if ((wanted || PackQueued[pack]) && Downloaded_Pack_Folder(pack, folder, sizeof(folder))) {
            DWORD id = Mod_Id(folder);
            if (id != 0) {
                Profile_Enable(id);
                PackQueued[pack] = true;
            }
        }
    }
    ((ProfileSaveFn)PROFILE_SAVE)((void*)PROFILE, 1, 0, 1);
}

/*
**	Switches off the packs in `packs` (a bit per pack) for the next start, as the Mods screen's checkbox does, and
**	saves the profile; their files stay.
*/
void Disable_Packs(unsigned packs)
{
    char* mm = Mod_Manager();
    if (mm == NULL) {
        return;
    }
    for (int pack = 0; pack < PACK_COUNT; pack++) {
        if (!(packs & (1u << pack))) {
            continue;
        }
        char folder[MAX_PATH];
        if (PackQueued[pack] && Downloaded_Pack_Folder(pack, folder, sizeof(folder))) {
            Profile_Remove(Mod_Id(folder));
        }
        PackQueued[pack] = false;
        char* last = *(char**)(mm + 0x1C);
        for (char* r = *(char**)(mm + 0x18); r != NULL && r < last; r += MOD_RECORD_SIZE) {
            if (Has_Pack_Marker(TF_String_Chars((const MsvcString*)(r + MOD_FOLDER)), PACKS[pack].Marker)) {
                ((SetModEnabledFn)SET_MOD_ENABLED)(mm, *(const DWORD*)(r + MOD_ID), 0);
            }
        }
    }
    Enable_Packs(0);
}

/*
**	Asks the launcher to restart the game.
*/
void Restart_Game(void)
{
    void* link = *(void**)LAUNCHER_LINK;
    if (link != NULL) {
        ((PostToLauncherFn)POST_TO_LAUNCHER)(link, ((RestartMessageFn)RESTART_MESSAGE)());
        Sleep(RESTART_WAIT_MS);
    }
}

/*
**	The main menu's add-ons notice (scripts/bui_mainmenu_pack_notice.py), top right: the title over ADD-ONS, a
**	fixed two-line notice and ENABLE ADD-ONS.
*/
const SIZE_T MENU_BIND_HOOK = 0x6B185B;
const SIZE_T MENU_BIND_CAVE = 0x1BE95E0;
const SIZE_T AS_TEXT_BUTTON = 0x5EF8A0;
const SIZE_T AS_QUAD = 0x5ED0F0;
const SIZE_T SET_TEXT = 0xF1D270;
const SIZE_T BIND_EVENT = 0x6A9F50;
const int CLICK_EVENT = 0x21;

typedef void(__thiscall* BindEventFn)(void* menu, int event, void* widget, void* handler, int data);
typedef void(__thiscall* SetTextFn)(void* widget, const MsvcWString* text);

int PanelPack = -1;

/*
**	Sets a text widget's text; NULL is ignored.
*/
void Set_Text(void* widget, const wchar_t* text)
{
    if (widget == NULL) {
        return;
    }
    MsvcWString s = {};
    s.Capacity = 7;
    ((WStringAssignFn)WSTRING_ASSIGN)(&s, text, (unsigned)wcslen(text));
    ((SetTextFn)SET_TEXT)(widget, &s);
    Free_WString(&s);
}

bool Pack_On(PackState state);

/*
**	Shows the notice while any add-on is not on, whether never subscribed to or switched off; its button opens
**	ADD-ONS at the first such add-on.
*/
void Refresh_Panel(void* menu)
{
    PanelPack = -1;
    for (int pack = 0; pack < PACK_COUNT && PanelPack < 0; pack++) {
        PanelPack = Pack_On(Pack_State(pack)) ? -1 : pack;
    }
    const struct
    {
        const char* Name;
        SIZE_T Cast;
    } pieces[] = {{"TF_Pack_Frame", AS_QUAD},
                  {"TF_Pack_Sheen", AS_QUAD},
                  {"TF_Pack_Logo", AS_QUAD},
                  {"TF_Pack_Status", AS_TEXT},
                  {"TF_Pack_Status2", AS_TEXT},
                  {"TF_Pack_Open", AS_TEXT_BUTTON}};
    for (const auto& piece : pieces) {
        Set_Hidden(Find_Widget(menu, piece.Name, piece.Cast), PanelPack < 0);
    }
}

/*
**	The main menu lives for the whole session, so a 2-second timer on its UI thread refreshes the notice while
**	it shows: an add-on switched on meanwhile hides it without a restart.
*/
const UINT PANEL_POLL_MS = 2000;
void* PanelMenu = NULL;
UINT_PTR PanelTimer = 0;

void CALLBACK Panel_Poll(HWND, UINT, UINT_PTR, DWORD)
{
    if (PanelMenu != NULL && PanelPack >= 0) {
        Refresh_Panel(PanelMenu);
    }
}

/*
**	The mod's version from its ccmod.json, as the release names it: version_high.(version_low / 10).(version_low % 10).
*/
void Mod_Version(wchar_t* out, size_t size)
{
    char path[MAX_PATH] = "";
    HMODULE self = NULL;
    GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                       (LPCSTR)&Mod_Version,
                       &self);
    DWORD length = GetModuleFileNameA(self, path, sizeof(path));
    char* data = length > 0 && length < sizeof(path) ? strrchr(path, '\\') : NULL;
    if (data != NULL) {
        *data = 0;
        data = strrchr(path, '\\');
    }
    int high = -1, low = -1;
    if (data != NULL) {
        snprintf(data, sizeof(path) - (data - path), "\\ccmod.json");
        FILE* f = fopen(path, "r");
        char line[160];
        while (f != NULL && fgets(line, sizeof(line), f) != NULL) {
            const char* at = strstr(line, "\"version_high\"");
            at = at != NULL ? strchr(at, ':') : NULL;
            if (at != NULL) {
                sscanf(at + 1, "%d", &high);
            }
            at = strstr(line, "\"version_low\"");
            at = at != NULL ? strchr(at, ':') : NULL;
            if (at != NULL) {
                sscanf(at + 1, "%d", &low);
            }
        }
        if (f != NULL) {
            fclose(f);
        }
    }
    if (high < 0 || low < 0) {
        swprintf(out, size, L"TIBERIAN FACTIONS");
    } else {
        swprintf(out, size, L"TIBERIAN FACTIONS %d.%d.%d", high, low / 10, low % 10);
    }
}

/*
**	The ADD-ONS screen (scripts/bui_addons_build.py, docs/pack-panel.md): a scene of our own, run by ClientG's
**	SplashScreen class, which binds nothing itself, drawn over the main menu until BACK closes it.
*/
const SIZE_T GUI_MANAGER = 0x5ED5D0;
const SIZE_T CREATE_SCENE = 0xF2CB70;
const SIZE_T SCENE_FOCUS = 0xF0E1D0;
const SIZE_T SCENE_RELEASE = 0x55FE10;
const SIZE_T AS_BUTTON = 0x606990;
const int SCENE_CLOSE = 0x2CC;
const int SCENE_IMPL = 0x330;
const UINT ADDONS_POLL_MS = 1000;
const DWORD SUBSCRIBE_WAIT_MS = 20000;
const int BAR_SEGMENTS = 20;
const int ADDON_ROWS = 4;   // rows per tab: ROW_SLOTS in scripts/bui_addons_build.py
const int DETAIL_LINES = 4; // DETAIL_LINES in scripts/bui_addons_build.py
const wchar_t* const KIND_NAMES[KIND_COUNT] = {L"ASSETS", L"THEATRES", L"CAMPAIGNS"};

typedef void*(__cdecl* GuiManagerFn)(void);
typedef void**(__thiscall* CreateSceneFn)(void* manager, void** out, const MsvcString* name, int layer);
typedef void(__thiscall* SceneFn)(void* scene);

/*
**	A scene's behaviour object, which owns its widgets and events; NULL while it is closed.
*/
void* Scene_Impl(void* scene)
{
    return scene != NULL ? *(void**)((char*)scene + SCENE_IMPL) : NULL;
}

/*
**	Closes and releases a scene of ours and clears its holder; the main menu under it carries on.
*/
void Scene_Close(void** scene)
{
    void* open = *scene;
    *scene = NULL;
    if (open != NULL) {
        ((SceneFn)(*(SIZE_T**)open)[SCENE_CLOSE / 4])(open);
        ((SceneFn)SCENE_RELEASE)(open);
    }
}

MsvcString Lent_String(const char* text);

/*
**	Opens the scene `name` (its .BUI, as "RA/<name>") over the main menu and focuses it; returns its behaviour
**	object, or NULL with the holder cleared when the launcher can't build it.
*/
void* Scene_Open(void** scene, const char* name)
{
    *scene = NULL;
    MsvcString text = Lent_String(name);
    ((CreateSceneFn)CREATE_SCENE)(((GuiManagerFn)GUI_MANAGER)(), scene, &text, -1);
    if (*scene == NULL) {
        return NULL;
    }
    ((SceneFn)SCENE_FOCUS)(*scene);
    void* impl = Scene_Impl(*scene);
    if (impl == NULL) {
        Scene_Close(scene);
    }
    return impl;
}

void* AddOnsScene = NULL;
bool AddOnsTicked[PACK_COUNT];
bool AddOnsKnockOn[PACK_COUNT]; // ticked or unticked by another pack's checkbox, not its own
int AddOnsTab = KIND_ASSETS;
int AddOnsSelected = 0;
unsigned AddOnsWanted = 0; // the packs APPLY AND RESTART is fetching, a bit per pack
DWORD AddOnsAsked = 0;
UINT_PTR AddOnsTimer = 0;

/*
**	The ADD-ONS screen's behaviour object, which owns its widgets and events; NULL while it is closed.
*/
void* AddOns_Screen(void)
{
    return Scene_Impl(AddOnsScene);
}

/*
**	A button of a screen whichever button class it is; NULL when absent.
*/
void* Find_Button(void* owner, const char* name)
{
    static const SIZE_T casts[] = {AS_BUTTON, AS_ICON_BUTTON, AS_TEXT_BUTTON};
    for (size_t i = 0; i < sizeof(casts) / sizeof(casts[0]); i++) {
        void* button = Find_Widget(owner, name, casts[i]);
        if (button != NULL) {
            return button;
        }
    }
    return NULL;
}

/*
**	A widget of a screen named `name` followed by `index`.
*/
void* Indexed_Widget(void* screen, const char* name, int index, SIZE_T cast)
{
    char full[32];
    snprintf(full, sizeof(full), "%s%d", name, index);
    return Find_Widget(screen, full, cast);
}

/*
**	Shows `text` in a green text widget or, when `warn`, in its amber twin, hiding the other; NULL text hides both.
*/
void Set_Twin_Text(void* screen, const char* green, const char* amber, const wchar_t* text, bool warn)
{
    void* shown = Find_Widget(screen, warn ? amber : green, AS_TEXT);
    if (text != NULL) {
        Set_Text(shown, text);
    }
    Set_Hidden(shown, text == NULL);
    Set_Hidden(Find_Widget(screen, warn ? green : amber, AS_TEXT), true);
}

/*
**	Sets and shows a text widget; NULL text hides it.
*/
void Show_Text(void* screen, const char* name, const wchar_t* text)
{
    void* widget = Find_Widget(screen, name, AS_TEXT);
    if (text != NULL) {
        Set_Text(widget, text);
    }
    Set_Hidden(widget, text == NULL);
}

/*
**	True when a pack is on (an out-of-date one included: only Steam's update changes it), or on from the next start.
*/
bool Pack_On(PackState state)
{
    return state == PACK_ENABLED || state == PACK_OUTDATED || state == PACK_ON_NEXT_START;
}

/*
**	The index of the pack with `id`; -1 when none.
*/
int Pack_Index(const char* id)
{
    for (int pack = 0; id != NULL && pack < PACK_COUNT; pack++) {
        if (strcmp(PACKS[pack].Id, id) == 0) {
            return pack;
        }
    }
    return -1;
}

/*
**	True when `pack` can't work without `needed`.
*/
bool Pack_Needs(int pack, int needed)
{
    for (int i = 0; i < 2; i++) {
        if (Pack_Index(PACKS[pack].Needs[i]) == needed && needed >= 0) {
            return true;
        }
    }
    return false;
}

/*
**	The pack on row `row` of the open tab; -1 for an empty row.
*/
int Tab_Pack(int row)
{
    for (int pack = 0; pack < PACK_COUNT; pack++) {
        if (PACKS[pack].Kind == AddOnsTab && row-- == 0) {
            return pack;
        }
    }
    return -1;
}

/*
**	Ticks a pack and what it needs, or unticks it and what needs it; `knock_on` marks a pack changed for another's.
*/
void Tick_Pack(int pack, bool ticked, bool knock_on)
{
    if (AddOnsTicked[pack] == ticked) {
        return;
    }
    AddOnsTicked[pack] = ticked;
    AddOnsKnockOn[pack] = knock_on;
    for (int other = 0; other < PACK_COUNT; other++) {
        if ((ticked && Pack_Needs(pack, other)) || (!ticked && Pack_Needs(other, pack))) {
            Tick_Pack(other, ticked, true);
        }
    }
}

/*
**	The pack whose own checkbox caused `pack`'s knock-on change; -1 when none.
*/
int Knock_On_Cause(int pack, const PackState* states)
{
    for (int other = 0; other < PACK_COUNT; other++) {
        bool changing = AddOnsTicked[other] != Pack_On(states[other]);
        if (other != pack && changing && !AddOnsKnockOn[other]
            && (AddOnsTicked[pack] ? Pack_Needs(other, pack) : Pack_Needs(pack, other))) {
            return other;
        }
    }
    return -1;
}

/*
**	A pack's row text on the ADD-ONS screen: the change its checkbox asks for, else its state; `warn` when it
**	keeps a faction from playing.
*/
void AddOns_State_Text(int pack, const PackState* states, wchar_t* line, size_t size, bool* warn)
{
    PackState state = states[pack];
    int percent = state == PACK_DOWNLOADING ? Pack_Download_Percent(pack) : 0;
    bool change = AddOnsWanted == 0 && AddOnsTicked[pack] != Pack_On(state) && state != PACK_DOWNLOADING;
    *warn = PACKS[pack].NeededFor != NULL && !change && (!Pack_On(state) || state == PACK_OUTDATED)
            && state != PACK_DOWNLOADING;
    int cause = change && AddOnsKnockOn[pack] ? Knock_On_Cause(pack, states) : -1;
    if (cause >= 0) {
        swprintf(line,
                 size,
                 AddOnsTicked[pack] ? L"TICKED: NEEDED BY %ls" : L"WILL SWITCH OFF: NEEDS %ls",
                 PACKS[cause].Name);
        return;
    }
    swprintf(line,
             size,
             change && !AddOnsTicked[pack]     ? L"WILL SWITCH OFF"
             : change && state == PACK_MISSING ? L"WILL DOWNLOAD AND SWITCH ON"
             : change && state == PACK_OFF_NEXT_START ? L"WILL STAY ON"
             : change                          ? L"WILL SWITCH ON"
             : state == PACK_ENABLED           ? L"LOADED"
             : state == PACK_OUTDATED          ? L"OUT OF DATE: LET STEAM UPDATE IT"
             : state == PACK_OFF_NEXT_START    ? L"SWITCHED OFF: GONE AFTER A RESTART"
             : state == PACK_ON_NEXT_START     ? L"READY: RESTART TO LOAD IT"
             : state == PACK_INSTALLED_OFF     ? L"INSTALLED BUT SWITCHED OFF"
             : state == PACK_DOWNLOADED        ? L"DOWNLOADED, NOT SWITCHED ON"
             : state == PACK_DOWNLOADING       ? (percent > 0 ? L"DOWNLOADING %d%%" : L"DOWNLOADING...")
                                               : L"NOT INSTALLED",
             percent);
}

/*
**	Appends `name` to a comma-separated list in `line`.
*/
void Append_Name(wchar_t* line, size_t size, const wchar_t* name)
{
    size_t used = wcslen(line);
    swprintf(line + used, size - used, L"%ls%ls", line[used - 1] == L' ' ? L"" : L", ", name);
}

/*
**	The top panel: the changes waiting for APPLY AND RESTART, knock-ons with their cause, or how to use the screen.
*/
void Refresh_Changes(void* screen, const PackState* states)
{
    wchar_t on[256] = L"WILL SWITCH ON: ", off[256] = L"WILL SWITCH OFF: ";
    size_t on_empty = wcslen(on), off_empty = wcslen(off);
    for (int pack = 0; pack < PACK_COUNT; pack++) {
        if (AddOnsTicked[pack] == Pack_On(states[pack]) || states[pack] == PACK_DOWNLOADING) {
            continue;
        }
        wchar_t name[128];
        int cause = AddOnsKnockOn[pack] ? Knock_On_Cause(pack, states) : -1;
        if (cause >= 0) {
            swprintf(name,
                     128,
                     AddOnsTicked[pack] ? L"%ls (NEEDED BY %ls)" : L"%ls (NEEDS %ls)",
                     PACKS[pack].Name,
                     PACKS[cause].Name);
        } else {
            swprintf(name, 128, L"%ls", PACKS[pack].Name);
        }
        Append_Name(AddOnsTicked[pack] ? on : off, 256, name);
    }
    bool any_on = wcslen(on) > on_empty, any_off = wcslen(off) > off_empty;
    if (AddOnsWanted != 0) {
        Show_Text(screen, "TF_AO_Intro1", L"Getting your add-ons from the Steam Workshop.");
        Show_Text(screen, "TF_AO_Intro2", L"The game restarts by itself when every download has finished.");
    } else if (any_on || any_off) {
        Show_Text(screen, "TF_AO_Intro1", any_on ? on : off);
        Show_Text(screen, "TF_AO_Intro2", any_on && any_off ? off : NULL);
    } else {
        Show_Text(screen, "TF_AO_Intro1", L"Tick the add-ons you want on and untick the ones you want off, then");
        Show_Text(screen,
                  "TF_AO_Intro2",
                  L"APPLY AND RESTART. Ticking an add-on ticks what it needs; unticking it unticks what needs it.");
    }
}

/*
**	The right-hand panel: the selected pack's name, logo, description, what it needs or what needs it, its status
**	and its download bar; empty when the open tab is.
*/
void Refresh_Detail(void* screen, const PackState* states)
{
    int pack = PACKS[AddOnsSelected].Kind == AddOnsTab ? AddOnsSelected : -1;
    for (int other = 0; other < PACK_COUNT; other++) {
        char logo[32];
        snprintf(logo, sizeof(logo), "TF_AO_DLogo_%s", PACKS[other].Id);
        Set_Hidden(Find_Widget(screen, logo, AS_QUAD), other != pack);
    }
    Show_Text(screen, "TF_AO_DName", pack >= 0 ? PACKS[pack].Name : NULL);
    Show_Text(screen, "TF_AO_DDesc1", pack >= 0 ? PACKS[pack].Description[0] : NULL);
    Show_Text(screen, "TF_AO_DDesc2", pack >= 0 ? PACKS[pack].Description[1] : NULL);
    wchar_t lines[DETAIL_LINES][128];
    bool warns[DETAIL_LINES] = {};
    int count = 0;
    bool needs = false;
    for (int other = 0; pack >= 0 && other < PACK_COUNT; other++) {
        needs |= Pack_Needs(pack, other);
    }
    if (pack >= 0 && needs) {
        swprintf(lines[count++], 128, L"NEEDS:");
        for (int other = 0; other < PACK_COUNT && count < DETAIL_LINES; other++) {
            if (Pack_Needs(pack, other)) {
                bool on = Pack_On(states[other]);
                swprintf(lines[count],
                         128,
                         L"  %ls: %ls",
                         PACKS[other].Name,
                         on && AddOnsTicked[other]  ? L"LOADED"
                         : AddOnsTicked[other]      ? L"TICKED, WILL SWITCH ON"
                         : on                       ? L"WILL SWITCH OFF"
                                                    : L"NOT TICKED");
                warns[count++] = !AddOnsTicked[other];
            }
        }
    } else if (pack >= 0) {
        int first = count;
        swprintf(lines[count++], 128, L"NEEDED BY:");
        if (PACKS[pack].NeededFor != NULL) {
            swprintf(lines[count++], 128, L"  %ls", PACKS[pack].NeededFor);
        }
        for (int other = 0; other < PACK_COUNT && count < DETAIL_LINES; other++) {
            if (Pack_Needs(other, pack)) {
                bool going = !AddOnsTicked[other] && Pack_On(states[other]);
                swprintf(lines[count], 128, going ? L"  %ls: WILL SWITCH OFF TOO" : L"  %ls", PACKS[other].Name);
                warns[count++] = going;
            }
        }
        count = count == first + 1 ? first : count;
    }
    for (int line = 0; line < DETAIL_LINES; line++) {
        char green[16], amber[16];
        snprintf(green, sizeof(green), "TF_AO_DLine%d", line);
        snprintf(amber, sizeof(amber), "TF_AO_DLineW%d", line);
        Set_Twin_Text(screen, green, amber, line < count ? lines[line] : NULL, line < count && warns[line]);
    }
    wchar_t line[96] = L"";
    bool warn = false;
    if (pack >= 0) {
        AddOns_State_Text(pack, states, line, 96, &warn);
    }
    Set_Twin_Text(screen, "TF_AO_Status", "TF_AO_StatusW", pack >= 0 ? line : NULL, warn);
    int percent = pack >= 0 && states[pack] == PACK_DOWNLOADING ? Pack_Download_Percent(pack) : -1;
    for (int i = 0; i < BAR_SEGMENTS; i++) {
        Set_Hidden(Indexed_Widget(screen, "TF_AO_Bar", i, AS_QUAD), percent < 0 || i >= percent * BAR_SEGMENTS / 100);
    }
}

/*
**	Fills the ADD-ONS screen from the packs' states: the tabs and their change badges, the open tab's rows or
**	COMING SOON, the selected pack, the top panel and the bottom bar.
*/
void Refresh_AddOns(void)
{
    void* screen = AddOns_Screen();
    if (screen == NULL) {
        return;
    }
    PackState states[PACK_COUNT];
    int changes = 0, ready = 0, tab_changes[KIND_COUNT] = {};
    for (int pack = 0; pack < PACK_COUNT; pack++) {
        states[pack] = Pack_State(pack);
        bool change = AddOnsTicked[pack] != Pack_On(states[pack]) && states[pack] != PACK_DOWNLOADING;
        changes += change;
        tab_changes[PACKS[pack].Kind] += change;
        ready += states[pack] == PACK_ON_NEXT_START || states[pack] == PACK_OFF_NEXT_START;
    }
    wchar_t line[96];
    bool warn;
    for (int tab = 0; tab < KIND_COUNT; tab++) {
        Set_Hidden(Indexed_Widget(screen, "TF_AO_TabGlow", tab, AS_QUAD), tab != AddOnsTab);
        Set_Hidden(Indexed_Widget(screen, "TF_AO_TabOn", tab, AS_TEXT), tab != AddOnsTab);
        Set_Hidden(Indexed_Widget(screen, "TF_AO_TabText", tab, AS_TEXT), tab == AddOnsTab);
        void* badge = Indexed_Widget(screen, "TF_AO_Badge", tab, AS_TEXT);
        swprintf(line, 96, tab_changes[tab] == 1 ? L"1 CHANGE" : L"%d CHANGES", tab_changes[tab]);
        Set_Text(badge, line);
        Set_Hidden(badge, tab_changes[tab] == 0);
    }
    Show_Text(screen, "TF_AO_ListHead", KIND_NAMES[AddOnsTab]);
    Set_Hidden(Find_Widget(screen, "TF_AO_Soon", AS_TEXT), Tab_Pack(0) >= 0);
    for (int row = 0; row < ADDON_ROWS; row++) {
        int pack = Tab_Pack(row);
        Set_Hidden(Indexed_Widget(screen, "TF_AO_Glow", row, AS_QUAD), pack < 0 || pack != AddOnsSelected);
        Set_Hidden(Indexed_Widget(screen, "TF_AO_Row", row, AS_ICON_BUTTON), pack < 0);
        void* check = Indexed_Widget(screen, "TF_AO_Check", row, AS_BUTTON);
        if (check != NULL && pack >= 0) {
            ((SetToggledFn)SET_TOGGLED)(check, AddOnsTicked[pack], 0, 1);
        }
        Set_Hidden(check, pack < 0);
        for (int other = 0; other < PACK_COUNT; other++) {
            char logo[32];
            snprintf(logo, sizeof(logo), "TF_AO_Logo%d_%s", row, PACKS[other].Id);
            Set_Hidden(Find_Widget(screen, logo, AS_QUAD), other != pack);
        }
        char name[16], green[16], amber[16];
        snprintf(name, sizeof(name), "TF_AO_Name%d", row);
        snprintf(green, sizeof(green), "TF_AO_State%d", row);
        snprintf(amber, sizeof(amber), "TF_AO_Warn%d", row);
        Show_Text(screen, name, pack >= 0 ? PACKS[pack].Name : NULL);
        if (pack >= 0) {
            AddOns_State_Text(pack, states, line, 96, &warn);
        }
        Set_Twin_Text(screen, green, amber, pack >= 0 ? line : NULL, pack >= 0 && warn);
    }
    Refresh_Detail(screen, states);
    Refresh_Changes(screen, states);
    bool idle = AddOnsWanted == 0 && changes == 0 && ready == 0;
    void* label = Find_Widget(screen, "StartButton_Text", AS_TEXT);
    Set_Text(label,
             AddOnsWanted != 0 ? L"WORKING..."
             : changes == 0    ? L"RESTART NOW"
                               : L"APPLY AND RESTART");
    Set_Hidden(label, idle);
    Set_Hidden(Find_Button(screen, "Start_Button"), idle);
    Set_Hidden(Find_Widget(screen, "TF_AO_UndoText", AS_TEXT), AddOnsWanted != 0 || changes == 0);
    Set_Hidden(Find_Button(screen, "TF_AO_Undo"), AddOnsWanted != 0 || changes == 0);
    Set_Text(Find_Widget(screen, "BackButton_Text", AS_TEXT), AddOnsWanted != 0 ? L"CANCEL" : L"BACK");
}

/*
**	Closes and releases the ADD-ONS scene; the main menu under it carries on.
*/
void Close_AddOns(void)
{
    Scene_Close(&AddOnsScene);
    if (AddOnsTimer != 0) {
        KillTimer(NULL, AddOnsTimer);
        AddOnsTimer = 0;
    }
}

/*
**	Once a second while the screen is open: when every pack being fetched has arrived, switches them on and
**	restarts; a pack Steam never starts on opens its Workshop page instead.
*/
void CALLBACK AddOns_Poll(HWND, UINT, UINT_PTR, DWORD)
{
    if (AddOnsWanted != 0) {
        bool waiting = false;
        for (int pack = 0; pack < PACK_COUNT; pack++) {
            if (!(AddOnsWanted & (1u << pack))) {
                continue;
            }
            PackState state = Pack_State(pack);
            bool asked = state == PACK_MISSING && GetTickCount() - AddOnsAsked < SUBSCRIBE_WAIT_MS;
            if (state == PACK_DOWNLOADING || asked) {
                waiting = true;
            } else if (state == PACK_MISSING) {
                AddOnsWanted &= ~(1u << pack);
                Open_Pack_Page(pack);
            }
        }
        if (!waiting && AddOnsWanted != 0) {
            unsigned packs = AddOnsWanted;
            AddOnsWanted = 0;
            Enable_Packs(packs);
            Refresh_AddOns();
            Restart_Game();
            return;
        }
    }
    Refresh_AddOns();
}

/*
**	BACK closes the screen; while packs are on their way it reads CANCEL and stops waiting for them instead, so
**	nothing switches on and nothing restarts (Steam still finishes the downloads).
*/
void __stdcall AddOns_Back_Click(void*)
{
    if (AddOnsWanted != 0) {
        AddOnsWanted = 0;
        Refresh_AddOns();
        return;
    }
    Close_AddOns();
}

/*
**	The row a click on row `screen_plus_row` came from: the event's data is the row, so ClientG calls with the
**	screen object plus the row. Returns its pack, or -1.
*/
int Clicked_Pack(char* screen_plus_row)
{
    void* screen = AddOns_Screen();
    int row = screen != NULL ? (int)(screen_plus_row - (char*)screen) : -1;
    return row >= 0 && row < ADDON_ROWS ? Tab_Pack(row) : -1;
}

/*
**	A row, outside its checkbox: shows that pack on the right.
*/
void __fastcall AddOns_Row_Click(char* screen_plus_row, void*, void*)
{
    int pack = Clicked_Pack(screen_plus_row);
    AddOnsSelected = pack >= 0 ? pack : AddOnsSelected;
    Refresh_AddOns();
}

/*
**	A row's checkbox: ticks its pack and what it needs, or unticks it and what needs it.
*/
void __fastcall AddOns_Check_Click(char* screen_plus_row, void*, void*)
{
    int pack = Clicked_Pack(screen_plus_row);
    if (pack >= 0 && AddOnsWanted == 0) {
        Tick_Pack(pack, !AddOnsTicked[pack], false);
        AddOnsSelected = pack;
    }
    Refresh_AddOns();
}

/*
**	A tab: shows its kind of add-on and selects its first.
*/
void __fastcall AddOns_Tab_Click(char* screen_plus_tab, void*, void*)
{
    void* screen = AddOns_Screen();
    int tab = screen != NULL ? (int)(screen_plus_tab - (char*)screen) : -1;
    if (tab >= 0 && tab < KIND_COUNT) {
        AddOnsTab = tab;
        AddOnsSelected = Tab_Pack(0) >= 0 ? Tab_Pack(0) : AddOnsSelected;
    }
    Refresh_AddOns();
}

/*
**	UNDO CHANGES: every checkbox back to whether its pack is on in this load or the next.
*/
void __stdcall AddOns_Undo_Click(void*)
{
    for (int pack = 0; pack < PACK_COUNT && AddOnsWanted == 0; pack++) {
        AddOnsTicked[pack] = Pack_On(Pack_State(pack));
        AddOnsKnockOn[pack] = false;
    }
    Refresh_AddOns();
}

/*
**	APPLY AND RESTART: switches off the unticked packs that are on, keeps re-ticked loaded packs on, subscribes to
**	the ticked missing ones, then the poll switches each on once it has arrived and restarts. With nothing to fetch,
**	restarts at once if anything changed.
*/
void __stdcall AddOns_Apply_Click(void*)
{
    if (AddOnsWanted != 0) {
        return;
    }
    unsigned wanted = 0, off = 0, kept = 0;
    bool restart = false;
    for (int pack = 0; pack < PACK_COUNT; pack++) {
        PackState state = Pack_State(pack);
        bool back_on = AddOnsTicked[pack] && state == PACK_OFF_NEXT_START;
        restart |= state == PACK_ON_NEXT_START || (state == PACK_OFF_NEXT_START && !back_on);
        if (back_on) {
            kept |= 1u << pack;
            continue;
        }
        if (!AddOnsTicked[pack]) {
            off |= Pack_On(state) ? 1u << pack : 0;
            continue;
        }
        if (Pack_On(state)) {
            continue;
        }
        if (state == PACK_MISSING && !Subscribe_Pack(pack)) {
            Open_Pack_Page(pack);
            continue;
        }
        wanted |= 1u << pack;
    }
    if (kept != 0) {
        Enable_Packs(kept);
    }
    if (off != 0) {
        Disable_Packs(off);
        restart = true;
    }
    if (wanted == 0) {
        if (restart) {
            Restart_Game();
        }
        Refresh_AddOns();
        return;
    }
    AddOnsWanted = wanted;
    AddOnsAsked = GetTickCount();
    AddOns_Poll(NULL, 0, 0, 0);
}

/*
**	Binds `handler` to a screen button's click with `data`, ClientG's offset from the screen object to the
**	handler's first argument; an absent button is skipped.
*/
void Bind_Click(void* screen, void* button, void* handler, int data)
{
    if (button != NULL) {
        ((BindEventFn)BIND_EVENT)(screen, CLICK_EVENT, button, handler, data);
    }
}

/*
**	Opens the ADD-ONS screen over the main menu with `pack` selected on its tab; -1 selects the first add-on that is
**	off. Only the add-ons that are on start ticked: the player ticks the rest.
*/
void Open_AddOns(int pack)
{
    if (AddOnsScene == NULL) {
        void* screen = Scene_Open(&AddOnsScene, "RA/TF_AddOns");
        if (screen == NULL) {
            return;
        }
        Bind_Click(screen, Find_Button(screen, "Back_Button"), (void*)&AddOns_Back_Click, 0);
        Bind_Click(screen, Find_Button(screen, "Start_Button"), (void*)&AddOns_Apply_Click, 0);
        Bind_Click(screen, Find_Button(screen, "TF_AO_Undo"), (void*)&AddOns_Undo_Click, 0);
        for (int tab = 0; tab < KIND_COUNT; tab++) {
            char name[16];
            snprintf(name, sizeof(name), "TF_AO_Tab%d", tab);
            Bind_Click(screen, Find_Button(screen, name), (void*)&AddOns_Tab_Click, tab);
        }
        for (int row = 0; row < ADDON_ROWS; row++) {
            char name[16];
            snprintf(name, sizeof(name), "TF_AO_Row%d", row);
            Bind_Click(screen, Indexed_Widget(screen, "TF_AO_Check", row, AS_BUTTON), (void*)&AddOns_Check_Click, row);
            Bind_Click(screen, Find_Button(screen, name), (void*)&AddOns_Row_Click, row);
        }
        AddOnsWanted = 0;
        AddOnsSelected = 0;
        for (int other = PACK_COUNT - 1; other >= 0; other--) {
            bool on = Pack_On(Pack_State(other));
            AddOnsTicked[other] = on;
            AddOnsKnockOn[other] = false;
            AddOnsSelected = on ? AddOnsSelected : other;
        }
        AddOnsTab = PACKS[AddOnsSelected].Kind;
    }
    if (pack >= 0 && pack < PACK_COUNT) {
        AddOnsSelected = pack;
        AddOnsTab = PACKS[pack].Kind;
    }
    Refresh_AddOns();
    if (AddOnsTimer == 0) {
        AddOnsTimer = SetTimer(NULL, 0, ADDONS_POLL_MS, AddOns_Poll);
    }
}

void __stdcall AddOns_Menu_Click(void*)
{
    Open_AddOns(-1);
}

void __stdcall Pack_Open_Click(void*)
{
    Open_AddOns(PanelPack);
}

/*
**	The encyclopedia (scripts/bui_encyclopedia_build.py, docs/encyclopedia.md): the CAMPAIGNS page's frame run by
**	SplashScreen, a tab per faction, the faction's entries in the stock list, and the selected entry's details.
*/
const SIZE_T AS_LISTBOX = 0x5F48A0;
const SIZE_T AS_EXAMPLE = 0x5EF5C0;
const SIZE_T LIST_CLEAR = 0xF6AF60;
const SIZE_T LIST_ADD_ROW = 0xF6A620;
const SIZE_T ROW_SET_ITEM = 0xF73CB0;
const SIZE_T LIST_SELECT_INDEX = 0xF74EA0;
const SIZE_T QUAD_SET_TEXTURE = 0xF604C0;
const SIZE_T FIND_TEXTURE = 0xF301F0;   // GUIManager's texture for a name, as Quad_Set_Texture resolves it
const int ENGINE_TEXTURE = 0x84;        // the ID3D11Texture2D in the engine texture the handle points at
const char* const LIVE_PICTURE = "TF_ENC_LIVE"; // the blank canvas each selected entry's sprite is drawn into
const int LIVE_WIDTH = 256;
const int LIVE_HEIGHT = 192;
const char* const LIST_COLUMN = "MissionColumn"; // the CAMPAIGNS list's only column
const int ROW_EVENT_CLICKED = 4;
const int ROW_CELL_SCENE = 0x1F4;
const int ROW_FLAG = 0x71;      // cleared on every row the stock lists add
const int CELL_LAYOUT = 0x6C;   // the cell's virtual the stock lists call with 1 once it is shown
const int ENC_MAX_ENTRIES = 160;
const int ENC_MAX_ROWS = ENC_MAX_ENTRIES + TF_ENC_GROUP_COUNT + 1;
const int DESC_RIGHT = 7;  // description lines beside the picture: DESC_RIGHT in scripts/bui_encyclopedia_build.py
const int DESC_BELOW = 3;  // and under it: DESC_BELOW
const int DESC_RIGHT_CHARS = 33;
const int DESC_BELOW_CHARS = 59;
const int STAT_SLOTS = 12; // two columns of STAT_ROWS
const int ENC_TABS = 5;

typedef void(__thiscall* ListClearFn)(void* list);
typedef void*(__thiscall* ListAddRowFn)(void* list);
typedef void*(__thiscall* RowSetItemFn)(void* row, const MsvcString* column, void* example, bool show);
typedef void(__thiscall* ListSelectIndexFn)(void* list, int index, bool notify);
typedef bool(__thiscall* QuadSetTextureFn)(void* quad, const MsvcString* name, bool refresh);
typedef void*(__thiscall* FindTextureFn)(void* gm, const MsvcString* name);

struct EncTabInfo
{
    const char* Button;   // the CAMPAIGNS tab it borrows
    int Faction;          // a TF_FACTION_ bit
    const wchar_t* Name;
    const char* Suffix;   // of its overview's text key and its logo (TF_ENC_ABOUT_<Suffix>)
    const char* Crest;    // the tab's crest in the UI atlas
};

const EncTabInfo ENC_TABS_INFO[ENC_TABS] = {
    {"CampaignSelect_Ally_Button", TF_FACTION_ALLIES, L"ALLIES", "ALLIES",
     "UI_MissionSelect_TabIcon_CovertOps_On"},
    {"CampaignSelect_USSR_Button", TF_FACTION_SOVIET, L"SOVIETS", "SOVIETS",
     "UI_MissionSelect_TabIcon_Controller_On"},
    {"CampaignSelect_Aftermath_Allied_Button", TF_FACTION_GDI, L"GDI", "GDI",
     "UI_MissionSelect_TabIcon_GDI_On"},
    {"CampaignSelect_Aftermath_USSR_Button", TF_FACTION_NOD, L"NOD", "NOD",
     "UI_MissionSelect_TabIcon_NOD_On"},
    {"CampaignSelect_Ant_Button", TF_FACTION_TSGDI, L"TIBERIAN SUN GDI", "TSGDI",
     "UI_MissionSelect_TabIcon_Dino_On"},
};

const wchar_t* const GROUP_NAMES[TF_ENC_GROUP_COUNT] = {L"INFANTRY", L"UNITS", L"AIRCRAFT", L"NAVAL", L"STRUCTURES"};

enum EncRowKind
{
    ENC_ROW_ABOUT,
    ENC_ROW_HEADING,
    ENC_ROW_ENTRY
};

struct EncRow
{
    EncRowKind Kind;
    int Index; // the group for a heading, the entry otherwise
};

void* EncScene = NULL;
int EncTab = 0;
TFEncEntry EncEntries[ENC_MAX_ENTRIES];
int EncEntryCount = 0;
EncRow EncRows[ENC_MAX_ROWS];
void* EncButtons[ENC_MAX_ROWS]; // each row's background button, toggled on for the selected row
int EncRowCount = 0;
int EncSelected = -1;

/*
**	The encyclopedia's behaviour object; NULL while it is closed.
*/
void* Enc_Screen(void)
{
    return Scene_Impl(EncScene);
}

/*
**	An MSVC std::string over `text`, inline when short, lent in place when long: ClientG's callers here only read it.
*/
MsvcString Lent_String(const char* text)
{
    MsvcString s = {};
    size_t length = strlen(text);
    if (length > 15) {
        *(const char**)s.buf = text;
        s.capacity = (unsigned)length;
    } else {
        memcpy(s.buf, text, length + 1);
        s.capacity = 15;
    }
    s.size = (unsigned)length;
    return s;
}

/*
**	Points an image widget at a texture by name (a loose file, an atlas region or a stock texture); false when
**	the launcher fell back to its default.
*/
bool Set_Picture(void* quad, const char* texture)
{
    if (quad == NULL) {
        return false;
    }
    MsvcString name = Lent_String(texture);
    return ((QuadSetTextureFn)QUAD_SET_TEXTURE)(quad, &name, false);
}

/*
**	Draws `ini`'s sprite for `faction` into the live canvas texture and points `picture` at it; false when its art
**	can't be read or the canvas isn't the size and format it is drawn for.
*/
bool Show_Live_Sprite(void* picture, const char* ini, int faction)
{
    static const GUID TEXTURE_2D = {0x6f15aaf2, 0xd208, 0x4e89, {0x9a, 0xb4, 0x48, 0x95, 0x35, 0xd3, 0x4f, 0x9c}};
    static unsigned char rgba[LIVE_WIDTH * LIVE_HEIGHT * 4];
    if (!TF_Encyclopedia_Render(ini, faction, rgba, LIVE_WIDTH, LIVE_HEIGHT) || !Set_Picture(picture, LIVE_PICTURE)) {
        return false;
    }
    MsvcString name = Lent_String(LIVE_PICTURE);
    void* handle = ((FindTextureFn)FIND_TEXTURE)(((GuiManagerFn)GUI_MANAGER)(), &name);
    const unsigned char* engine = handle != NULL ? *(const unsigned char* const*)handle : NULL;
    if (engine == NULL || IsBadReadPtr(engine + ENGINE_TEXTURE, 4)
        || *(void* const*)(engine + ENGINE_TEXTURE) == NULL) {
        return false;
    }
    ID3D11Texture2D* texture = NULL;
    IUnknown* unknown = *(IUnknown* const*)(engine + ENGINE_TEXTURE);
    if (FAILED(unknown->QueryInterface(TEXTURE_2D, (void**)&texture)) || texture == NULL) {
        return false;
    }
    D3D11_TEXTURE2D_DESC desc;
    texture->GetDesc(&desc);
    bool fits = desc.Width == LIVE_WIDTH && desc.Height == LIVE_HEIGHT
                && (desc.Format == DXGI_FORMAT_R8G8B8A8_UNORM || desc.Format == DXGI_FORMAT_R8G8B8A8_UNORM_SRGB);
    ID3D11Device* device = NULL;
    ID3D11DeviceContext* context = NULL;
    if (fits) {
        texture->GetDevice(&device);
    }
    if (device != NULL) {
        device->GetImmediateContext(&context);
        device->Release();
    }
    if (context != NULL) {
        context->UpdateSubresource(texture, 0, NULL, rgba, LIVE_WIDTH * 4, 0);
        context->Release();
    }
    texture->Release();
    return context != NULL;
}

/*
**	A text key's string from the launcher's table into `out`; false, and `out` empty, when the table has no such key.
*/
bool Lookup_Text(const char* key, wchar_t* out, size_t size)
{
    out[0] = 0;
    if (key == NULL || key[0] == 0) {
        return false;
    }
    MsvcWString text = {};
    text.Capacity = 7;
    ((TextLookupFn)TEXT_LOOKUP)((void*)TEXT_MANAGER, &text, key);
    const wchar_t* chars = text.Capacity >= 8 ? text.Pointer : text.Buffer;
    swprintf(out, size, L"%ls", chars);
    Free_WString(&text);
    wchar_t wide_key[96];
    swprintf(wide_key, 96, L"%hs", key);
    if (wcscmp(out, wide_key) == 0) {
        out[0] = 0;
    }
    return out[0] != 0;
}

/*
**	Splits `text` at spaces into lines of up to `widths[i]` characters; returns how many lines it filled.
*/
int Wrap_Text(const wchar_t* text, const int* widths, int lines, wchar_t (*out)[128])
{
    int line = 0;
    while (*text != 0 && line < lines) {
        while (*text == L' ') {
            text++;
        }
        int width = widths[line] < 127 ? widths[line] : 127;
        int take = (int)wcslen(text);
        if (take > width) {
            take = width;
            while (take > 0 && text[take] != L' ') {
                take--;
            }
            take = take > 0 ? take : width;
        }
        wcsncpy(out[line], text, take);
        out[line][take] = 0;
        text += take;
        line++;
    }
    return line;
}

/*
**	A widget inside one list row's own scene.
*/
void* Row_Widget(void* row_scene, const char* name, SIZE_T cast)
{
    void* owner[2] = {NULL, row_scene};
    return Find_Widget(owner, name, cast);
}

/*
**	The open tab's faction logo picture (scripts/encyclopedia_logos.py).
*/
const char* About_Picture(void)
{
    static char name[40];
    snprintf(name, sizeof(name), "TF_ENC_ABOUT_%s", ENC_TABS_INFO[EncTab].Suffix);
    return name;
}

/*
**	True when the open tab is TS GDI's and the TS-HD add-on isn't loaded, so its art is missing.
*/
bool Enc_Tab_Needs_Pack(void)
{
    return ENC_TABS_INFO[EncTab].Faction == TF_FACTION_TSGDI && !Pack_Loaded(Pack_State(TS_HD_PACK));
}

/*
**	The details side: the faction's overview for the About row, an entry's picture, description and stats
**	otherwise; empty for a heading.
*/
void Enc_Show_Row(int row)
{
    void* screen = Enc_Screen();
    if (screen == NULL) {
        return;
    }
    for (int i = 0; i < EncRowCount; i++) {
        if (EncButtons[i] != NULL) {
            ((SetToggledFn)SET_TOGGLED)(EncButtons[i], i == row, 0, 1);
        }
    }
    EncSelected = row;
    const EncRow* r = row >= 0 && row < EncRowCount ? &EncRows[row] : NULL;
    bool entry = r != NULL && r->Kind == ENC_ROW_ENTRY;
    bool about = r != NULL && r->Kind == ENC_ROW_ABOUT;
    const TFEncEntry* e = entry ? &EncEntries[r->Index] : NULL;
    wchar_t name[96] = L"";
    if (entry && !Lookup_Text(e->NameKey, name, 96)) {
        swprintf(name, 96, L"%hs", e->Ini);
    } else if (about) {
        swprintf(name, 96, L"%ls", ENC_TABS_INFO[EncTab].Name);
    }
    Show_Text(screen, "TF_EN_Name", entry || about ? name : NULL);
    void* picture = Find_Widget(screen, "TF_EN_Pic", AS_QUAD);
    bool shown = false;
    if (entry) {
        shown = Show_Live_Sprite(picture, e->Ini, ENC_TABS_INFO[EncTab].Faction) || Set_Picture(picture, e->Cameo);
    } else if (about) {
        shown = Set_Picture(picture, About_Picture()) || Set_Picture(picture, ENC_TABS_INFO[EncTab].Crest);
    }
    Set_Hidden(picture, !shown);
    wchar_t text[2048] = L"";
    if (entry) {
        char key[64];
        snprintf(key, sizeof(key), "TEXT_TF_ENC_%s", e->Ini);
        if (!Lookup_Text(key, text, 2048)) {
            Lookup_Text(e->DescKey, text, 2048);
        }
    } else if (about) {
        char key[64];
        snprintf(key, sizeof(key), "TEXT_TF_ENC_ABOUT_%s", ENC_TABS_INFO[EncTab].Suffix);
        Lookup_Text(key, text, 2048);
    }
    int widths[DESC_RIGHT + DESC_BELOW];
    for (int i = 0; i < DESC_RIGHT + DESC_BELOW; i++) {
        widths[i] = i < DESC_RIGHT ? DESC_RIGHT_CHARS : DESC_BELOW_CHARS;
    }
    wchar_t lines[DESC_RIGHT + DESC_BELOW][128];
    int filled = Wrap_Text(text, widths, DESC_RIGHT + DESC_BELOW, lines);
    for (int i = 0; i < DESC_RIGHT + DESC_BELOW; i++) {
        char widget[16];
        snprintf(widget, sizeof(widget), "TF_EN_Desc%d", i);
        Show_Text(screen, widget, i < filled ? lines[i] : NULL);
    }
    TFEncStats stats = {};
    wchar_t list[160] = L"";
    if (entry) {
        TF_Encyclopedia_Stats(e->Ini, &stats);
        char needs[PREREQUISITE_MAX][64];
        int count = TF_Encyclopedia_Needs(e->Ini, needs, PREREQUISITE_MAX);
        for (int i = 0; i < count; i++) {
            wchar_t building[48];
            Lookup_Text(needs[i], building, 48);
            size_t used = wcslen(list);
            swprintf(list + used, 160 - used, L"%ls%ls", i > 0 ? L", " : L"", building);
        }
    }
    Show_Text(screen, "TF_EN_NeedsL", list[0] != 0 ? L"NEEDS" : NULL);
    Show_Text(screen, "TF_EN_Needs", list[0] != 0 ? list : NULL);
    for (int i = 0; i < STAT_SLOTS; i++) {
        char label[16], value[16];
        snprintf(label, sizeof(label), "TF_EN_SL%d", i);
        snprintf(value, sizeof(value), "TF_EN_SV%d", i);
        wchar_t shown[96] = L"";
        if (i < stats.Count) {
            wchar_t named[64];
            const wchar_t* value = Lookup_Text(stats.Key[i], named, 64) ? named : stats.Value[i];
            swprintf(shown, 96, L"%ls%ls", value, stats.Suffix[i]);
        }
        Show_Text(screen, label, i < stats.Count ? stats.Label[i] : NULL);
        Show_Text(screen, value, i < stats.Count ? shown : NULL);
    }
}

/*
**	A row clicked; the event's data is the row, so ClientG calls with the screen object plus the row. A heading
**	keeps the current selection.
*/
void __fastcall Enc_Row_Click(char* screen_plus_row, void*, void*)
{
    void* screen = Enc_Screen();
    int row = screen != NULL ? (int)(screen_plus_row - (char*)screen) : -1;
    if (row >= 0 && row < EncRowCount && EncRows[row].Kind != ENC_ROW_HEADING) {
        Enc_Show_Row(row);
    }
}

/*
**	Fills the list for the open tab: the About row, then each group's heading and its entries, with their
**	cameos; or, for TS GDI without its add-on, the gate to the ADD-ONS screen.
*/
void Enc_Fill_List(void)
{
    void* screen = Enc_Screen();
    if (screen == NULL) {
        return;
    }
    for (int tab = 0; tab < ENC_TABS; tab++) {
        void* button = Find_Button(screen, ENC_TABS_INFO[tab].Button);
        if (button != NULL) {
            ((SetToggledFn)SET_TOGGLED)(button, tab == EncTab, 0, 1);
        }
    }
    Show_Text(screen, "UI_CampaignSelect_Header_Text", ENC_TABS_INFO[EncTab].Name);
    bool gate = Enc_Tab_Needs_Pack();
    void* list = Find_Widget(screen, "MissionList_Box", AS_LISTBOX);
    Set_Hidden(list, gate);
    Show_Text(screen,
              "TF_EN_GateNote",
              gate ? L"Tiberian Sun GDI's units need the Tiberian Sun HD Assets add-on." : NULL);
    Set_Hidden(Find_Button(screen, "TF_EN_Gate"), !gate);
    Set_Hidden(Find_Widget(screen, "TF_EN_GateText", AS_TEXT), !gate);
    EncRowCount = 0;
    if (list == NULL || gate) {
        Enc_Show_Row(-1);
        return;
    }
    ((ListClearFn)LIST_CLEAR)(list);
    EncEntryCount = TF_Encyclopedia_Entries(ENC_TABS_INFO[EncTab].Faction, EncEntries, ENC_MAX_ENTRIES);
    EncRows[EncRowCount++] = {ENC_ROW_ABOUT, 0};
    for (int i = 0; i < EncEntryCount && EncRowCount < ENC_MAX_ROWS - 1; i++) {
        if (i == 0 || EncEntries[i].Group != EncEntries[i - 1].Group) {
            EncRows[EncRowCount++] = {ENC_ROW_HEADING, EncEntries[i].Group};
        }
        EncRows[EncRowCount++] = {ENC_ROW_ENTRY, i};
    }
    memset(EncButtons, 0, sizeof(EncButtons));
    void* example = Find_Widget(screen, "MissionList_SampleEntry", AS_EXAMPLE);
    MsvcString column = Lent_String(LIST_COLUMN);
    for (int i = 0; i < EncRowCount && example != NULL; i++) {
        char* row = (char*)((ListAddRowFn)LIST_ADD_ROW)(list);
        if (row == NULL) {
            continue;
        }
        row[ROW_FLAG] = 0;
        void* cell = ((RowSetItemFn)ROW_SET_ITEM)(row, &column, example, true);
        if (cell == NULL) {
            continue;
        }
        Set_Hidden(cell, false);
        ((SetFlagFn)(*(SIZE_T**)cell)[CELL_LAYOUT / 4])(cell, true);
        void* row_scene = *(void**)((char*)cell + ROW_CELL_SCENE);
        const EncRow& r = EncRows[i];
        void* button = Row_Widget(row_scene, "MissionElementButton_GDI", AS_ICON_BUTTON);
        if (button != NULL) {
            ((SetFlagFn)SET_NO_INPUT)(button, false);
        }
        EncButtons[i] = r.Kind == ENC_ROW_HEADING ? NULL : button;
        ((BindEventFn)BIND_EVENT)(screen, ROW_EVENT_CLICKED, cell, (void*)&Enc_Row_Click, i);
        Set_Hidden(Row_Widget(row_scene, "MissionFrameBG_GDI_Group", AS_GROUP), r.Kind == ENC_ROW_HEADING);
        wchar_t name[96] = L"";
        if (r.Kind == ENC_ROW_ENTRY && !Lookup_Text(EncEntries[r.Index].NameKey, name, 96)) {
            swprintf(name, 96, L"%hs", EncEntries[r.Index].Ini);
        } else if (r.Kind == ENC_ROW_ABOUT) {
            swprintf(name, 96, L"ABOUT THE %ls", ENC_TABS_INFO[EncTab].Name);
        }
        void* title = Row_Widget(row_scene, "MissionTitle_Text", AS_TEXT);
        Set_Text(title, name);
        Set_Hidden(title, r.Kind == ENC_ROW_HEADING);
        void* heading = Row_Widget(row_scene, "TF_Enc_Heading", AS_TEXT);
        Set_Text(heading, r.Kind == ENC_ROW_HEADING ? GROUP_NAMES[r.Index] : L"");
        Set_Hidden(heading, r.Kind != ENC_ROW_HEADING);
        void* cameo = Row_Widget(row_scene, "TF_Enc_Cameo", AS_QUAD);
        bool pictured = r.Kind == ENC_ROW_ENTRY ? Set_Picture(cameo, EncEntries[r.Index].Cameo)
                        : r.Kind == ENC_ROW_ABOUT ? Set_Picture(cameo, About_Picture())
                                                  : false;
        Set_Hidden(cameo, !pictured);
    }
    ((ListSelectIndexFn)LIST_SELECT_INDEX)(list, 0, false);
    Enc_Show_Row(0);
}

/*
**	Closes and releases the encyclopedia's scene; the main menu under it carries on.
*/
void Close_Encyclopedia(void)
{
    Scene_Close(&EncScene);
}

void __stdcall Enc_Back_Click(void*)
{
    Close_Encyclopedia();
}

/*
**	The TS GDI tab's gate: on to the ADD-ONS screen with the Tiberian Sun pack selected.
*/
void __stdcall Enc_Gate_Click(void*)
{
    Close_Encyclopedia();
    Open_AddOns(TS_HD_PACK);
}

/*
**	A faction tab; the event's data is the tab, so ClientG calls with the screen object plus the tab.
*/
void __fastcall Enc_Tab_Click(char* screen_plus_tab, void*, void*)
{
    void* screen = Enc_Screen();
    int tab = screen != NULL ? (int)(screen_plus_tab - (char*)screen) : -1;
    if (tab >= 0 && tab < ENC_TABS && tab != EncTab) {
        EncTab = tab;
        Enc_Fill_List();
    }
}

/*
**	Opens the encyclopedia over the main menu on the Allies tab, loading the rules the first time.
*/
void Open_Encyclopedia(void)
{
    if (EncScene != NULL) {
        return;
    }
    const MsvcString* roots = NULL;
    int count = TF_Mod_Roots(&roots);
    for (const MsvcString* root = roots; root < roots + count; root++) {
        TF_Encyclopedia_Add_Root(TF_String_Chars(root));
    }
    if (!TF_Encyclopedia_Load()) {
        Show_Message(L"The encyclopedia couldn't read the mod's rules.");
        return;
    }
    void* screen = Scene_Open(&EncScene, "RA/TF_Ency");
    if (screen == NULL) {
        return;
    }
    Bind_Click(screen, Find_Button(screen, "Back_Button"), (void*)&Enc_Back_Click, 0);
    Bind_Click(screen, Find_Button(screen, "TF_EN_Gate"), (void*)&Enc_Gate_Click, 0);
    for (int tab = 0; tab < ENC_TABS; tab++) {
        Bind_Click(screen, Find_Button(screen, ENC_TABS_INFO[tab].Button), (void*)&Enc_Tab_Click, tab);
    }
    Set_Hidden(Find_Widget(screen, "MissionList_SampleEntry", AS_EXAMPLE), true);
    EncTab = 0;
    Enc_Fill_List();
}

void __stdcall Encyclopedia_Menu_Click(void*)
{
    Open_Encyclopedia();
}

/*
**	The Settings page (scripts/bui_settings_build.py, docs/skirmish-music.md): the CAMPAIGNS page's frame run by
**	SplashScreen, page tabs, and on AUDIO a faction tab per faction with that faction's skirmish music.
*/
const int SETTINGS_PAGES = 2;   // PAGES in scripts/bui_settings_build.py
const int SETTINGS_AUDIO = 0;
const int MUSIC_ROWS = 4;       // MUSIC_ROWS in scripts/bui_settings_build.py
const int MUSIC_MIX_ROW = 0;
const int MUSIC_TS_ROW = 3;
const char* const BANNERS[] = {"TF_Banner_RA", "TF_Banner_TD", "TF_Banner_TS"};

struct MusicChoiceInfo
{
    const char* Value; // as tf_music.ini stores it (tf_music.h)
    const wchar_t* About;
};

const MusicChoiceInfo MUSIC_CHOICES[MUSIC_ROWS] = {{"MIX", L"Every soundtrack, shuffled (the default)"},
                                                   {"RA", L"Red Alert's tracks only"},
                                                   {"TD", L"Tiberian Dawn's tracks only"},
                                                   {"TS", L"Tiberian Sun and Firestorm's tracks only"}};

void* SettingsScene = NULL;
int SettingsPage = SETTINGS_AUDIO;
int SettingsTab = 0;

void* Settings_Screen(void)
{
    return Scene_Impl(SettingsScene);
}

/*
**	The open faction tab's music row: its saved choice, MIX for anything unknown.
*/
int Music_Row(void)
{
    char choice[16];
    TF_Music_Choice(ENC_TABS_INFO[SettingsTab].Suffix, choice, sizeof(choice));
    for (int row = 0; row < MUSIC_ROWS; row++) {
        if (_stricmp(choice, MUSIC_CHOICES[row].Value) == 0) {
            return row;
        }
    }
    return 0;
}

/*
**	Shows the open page: on AUDIO the faction tabs, the faction's crest and its music rows with the saved choice
**	ticked; GET ADD-ON in place of Tiberian Sun while the TS-Music add-on is off; COMING SOON on an empty page.
*/
void Refresh_Settings(void)
{
    void* screen = Settings_Screen();
    if (screen == NULL) {
        return;
    }
    bool audio = SettingsPage == SETTINGS_AUDIO;
    for (int page = 0; page < SETTINGS_PAGES; page++) {
        Set_Hidden(Indexed_Widget(screen, "TF_ST_PageGlow", page, AS_QUAD), page != SettingsPage);
        Set_Hidden(Indexed_Widget(screen, "TF_ST_PageOn", page, AS_TEXT), page != SettingsPage);
        Set_Hidden(Indexed_Widget(screen, "TF_ST_PageText", page, AS_TEXT), page == SettingsPage);
    }
    for (int tab = 0; tab < ENC_TABS; tab++) {
        void* button = Find_Button(screen, ENC_TABS_INFO[tab].Button);
        if (button != NULL) {
            ((SetToggledFn)SET_TOGGLED)(button, tab == SettingsTab, 0, 1);
        }
        Set_Hidden(button, !audio);
    }
    for (size_t i = 0; i < ARRAY_SIZE(BANNERS); i++) {
        Set_Hidden(Find_Widget(screen, BANNERS[i], AS_TEXT), !audio);
    }
    Show_Text(screen, "TF_ST_Faction", audio ? ENC_TABS_INFO[SettingsTab].Name : NULL);
    void* crest = Find_Widget(screen, "TF_ST_Crest", AS_QUAD);
    char picture[40];
    snprintf(picture, sizeof(picture), "TF_ENC_ABOUT_%s", ENC_TABS_INFO[SettingsTab].Suffix);
    Set_Hidden(crest, !audio || !Set_Picture(crest, picture));
    Set_Hidden(Find_Widget(screen, "TF_ST_Soon", AS_TEXT), audio);
    Set_Hidden(Find_Widget(screen, "TF_ST_Music", AS_TEXT), !audio);
    Set_Hidden(Find_Widget(screen, "TF_ST_Plate", AS_QUAD), !audio);
    bool ts = TF_TS_Music_Present();
    int chosen = Music_Row();
    chosen = chosen == MUSIC_TS_ROW && !ts ? MUSIC_MIX_ROW : chosen;
    for (int row = 0; row < MUSIC_ROWS; row++) {
        bool missing = row == MUSIC_TS_ROW && !ts;
        Set_Hidden(Indexed_Widget(screen, "TF_ST_Glow", row, AS_QUAD), !audio || row != chosen);
        Set_Hidden(Indexed_Widget(screen, "TF_ST_Row", row, AS_ICON_BUTTON), !audio || missing);
        void* check = Indexed_Widget(screen, "TF_ST_Check", row, AS_BUTTON);
        if (check != NULL) {
            ((SetToggledFn)SET_TOGGLED)(check, row == chosen, 0, 1);
        }
        Set_Hidden(check, !audio || missing);
        Set_Hidden(Indexed_Widget(screen, "TF_ST_Name", row, AS_TEXT), !audio);
        char green[16], amber[16];
        snprintf(green, sizeof(green), "TF_ST_Desc%d", row);
        snprintf(amber, sizeof(amber), "TF_ST_Warn%d", row);
        Set_Twin_Text(screen,
                      green,
                      amber,
                      !audio      ? NULL
                      : missing   ? L"Needs its add-on"
                                  : MUSIC_CHOICES[row].About,
                      missing);
    }
    Set_Hidden(Find_Button(screen, "TF_ST_Get"), !audio || ts);
    Set_Hidden(Find_Widget(screen, "TF_ST_GetText", AS_TEXT), !audio || ts);
    Set_Hidden(Find_Button(screen, "Start_Button"), !audio);
    Set_Hidden(Find_Widget(screen, "StartButton_Text", AS_TEXT), !audio);
}

void Close_Settings(void)
{
    Scene_Close(&SettingsScene);
}

void __stdcall Settings_Back_Click(void*)
{
    Close_Settings();
}

/*
**	A page tab; the event's data is the page, so ClientG calls with the screen object plus the page.
*/
void __fastcall Settings_Page_Click(char* screen_plus_page, void*, void*)
{
    void* screen = Settings_Screen();
    int page = screen != NULL ? (int)(screen_plus_page - (char*)screen) : -1;
    if (page >= 0 && page < SETTINGS_PAGES) {
        SettingsPage = page;
        Refresh_Settings();
    }
}

/*
**	A faction tab, called as a page tab is.
*/
void __fastcall Settings_Tab_Click(char* screen_plus_tab, void*, void*)
{
    void* screen = Settings_Screen();
    int tab = screen != NULL ? (int)(screen_plus_tab - (char*)screen) : -1;
    if (tab >= 0 && tab < ENC_TABS) {
        SettingsTab = tab;
        Refresh_Settings();
    }
}

/*
**	A music row or its checkbox: saves that choice for the open faction, from the next track it plays.
*/
void __fastcall Settings_Row_Click(char* screen_plus_row, void*, void*)
{
    void* screen = Settings_Screen();
    int row = screen != NULL ? (int)(screen_plus_row - (char*)screen) : -1;
    if (row >= 0 && row < MUSIC_ROWS && (row != MUSIC_TS_ROW || TF_TS_Music_Present())) {
        TF_Music_Set_Choice(ENC_TABS_INFO[SettingsTab].Suffix, MUSIC_CHOICES[row].Value);
    }
    Refresh_Settings();
}

/*
**	DEFAULTS: every faction back to MIX.
*/
void __stdcall Settings_Defaults_Click(void*)
{
    for (int tab = 0; tab < ENC_TABS; tab++) {
        TF_Music_Set_Choice(ENC_TABS_INFO[tab].Suffix, MUSIC_CHOICES[0].Value);
    }
    Refresh_Settings();
}

/*
**	GET ADD-ON: on to the ADD-ONS screen with the TS-Music pack ticked.
*/
void __stdcall Settings_Get_Click(void*)
{
    Close_Settings();
    Open_AddOns(Pack_Index("TSMUSIC"));
}

/*
**	Opens the Settings page over the main menu on AUDIO's first faction tab.
*/
void Open_Settings(void)
{
    if (SettingsScene != NULL) {
        return;
    }
    void* screen = Scene_Open(&SettingsScene, "RA/TF_Settings");
    if (screen == NULL) {
        return;
    }
    Bind_Click(screen, Find_Button(screen, "Back_Button"), (void*)&Settings_Back_Click, 0);
    Bind_Click(screen, Find_Button(screen, "Start_Button"), (void*)&Settings_Defaults_Click, 0);
    Bind_Click(screen, Find_Button(screen, "TF_ST_Get"), (void*)&Settings_Get_Click, 0);
    for (int page = 0; page < SETTINGS_PAGES; page++) {
        char name[16];
        snprintf(name, sizeof(name), "TF_ST_Page%d", page);
        Bind_Click(screen, Find_Button(screen, name), (void*)&Settings_Page_Click, page);
    }
    for (int tab = 0; tab < ENC_TABS; tab++) {
        Bind_Click(screen, Find_Button(screen, ENC_TABS_INFO[tab].Button), (void*)&Settings_Tab_Click, tab);
    }
    for (int row = 0; row < MUSIC_ROWS; row++) {
        Bind_Click(screen, Indexed_Widget(screen, "TF_ST_Row", row, AS_ICON_BUTTON), (void*)&Settings_Row_Click, row);
        Bind_Click(screen, Indexed_Widget(screen, "TF_ST_Check", row, AS_BUTTON), (void*)&Settings_Row_Click, row);
    }
    SettingsPage = SETTINGS_AUDIO;
    SettingsTab = 0;
    Refresh_Settings();
}

void __stdcall Settings_Menu_Click(void*)
{
    Open_Settings();
}

/*
**	The main menu built: binds ADD-ONS, ENCYCLOPEDIA, SETTINGS and the panel's button, shows the mod's version,
**	fills the panel and starts its poll.
*/
void __stdcall Menu_Bound(const DWORD* regs)
{
    void* menu = (void*)regs[1];
    void* addons = Find_Widget(menu, "TF_AddOns", AS_TEXT_BUTTON);
    void* open = Find_Widget(menu, "TF_Pack_Open", AS_TEXT_BUTTON);
    void* encyclopedia = Find_Widget(menu, "TF_Encyclopedia", AS_TEXT_BUTTON);
    void* settings = Find_Widget(menu, "TF_Settings", AS_TEXT_BUTTON);
    if (encyclopedia != NULL) {
        ((BindEventFn)BIND_EVENT)(menu, CLICK_EVENT, encyclopedia, (void*)&Encyclopedia_Menu_Click, 0);
    }
    if (settings != NULL) {
        ((BindEventFn)BIND_EVENT)(menu, CLICK_EVENT, settings, (void*)&Settings_Menu_Click, 0);
    }
    if (addons != NULL) {
        ((BindEventFn)BIND_EVENT)(menu, CLICK_EVENT, addons, (void*)&AddOns_Menu_Click, 0);
    }
    if (open != NULL) {
        ((BindEventFn)BIND_EVENT)(menu, CLICK_EVENT, open, (void*)&Pack_Open_Click, 0);
    }
    wchar_t version[64];
    Mod_Version(version, 64);
    Set_Text(Find_Widget(menu, "TF_Version", AS_TEXT), version);
    PanelMenu = menu;
    Refresh_Panel(menu);
    if (PanelTimer == 0) {
        PanelTimer = SetTimer(NULL, 0, PANEL_POLL_MS, Panel_Poll);
    }
}

/*
**	The load screen's check of the selected save: a save this build can't load (no TF save marker,
**	or another version's) takes the stock path for a missing custom map, with our reason.
*/
const SIZE_T LOAD_MAP_CHECKED = 0x64E4D6;
const SIZE_T LOAD_MAP_CAVE = 0x1BE9600;
const SIZE_T LOAD_REASON = 0x64E540;
const SIZE_T LOAD_REASON_RESUME = 0x64E547;
const SIZE_T LOAD_REASON_CAVE = 0x1BE9620;
const DWORD ENTRY_FILE = 0x40;
const size_t SAVE_HEAD_BYTES = 0x40000;

unsigned char SaveRefused = 0;
const char SaveOtherVersionText[] = "THIS SAVE IS FROM ANOTHER VERSION OR MOD AND CAN'T BE LOADED";
const char SaveNeedsPackText[] = "THIS SAVE NEEDS THE TIBERIAN SUN HD ASSETS MOD: ENABLE IT AND RESTART";
const char* SaveRefusedText = SaveOtherVersionText;
DWORD SaveRefusedLength = sizeof(SaveOtherVersionText) - 1;

enum SaveCheck
{
    SAVE_LOADABLE,
    SAVE_OTHER_VERSION,
    SAVE_NEEDS_PACK
};

typedef void*(__cdecl* SteamStorageFn)(void);
typedef int(__cdecl* StorageSizeFn)(void* storage, const char* name);
typedef int(__cdecl* StorageReadFn)(void* storage, const char* name, void* data, int size);

/*
**	A cloud save's bytes through Steam's remote storage, in a malloc'd block; NULL when unreadable.
*/
unsigned char* Read_Save(const char* name, size_t* size)
{
    SteamStorageFn get = (SteamStorageFn)Steam_Export("SteamAPI_SteamRemoteStorage_v016");
    StorageSizeFn file_size = (StorageSizeFn)Steam_Export("SteamAPI_ISteamRemoteStorage_GetFileSize");
    StorageReadFn read = (StorageReadFn)Steam_Export("SteamAPI_ISteamRemoteStorage_FileRead");
    void* storage = get ? get() : NULL;
    if (storage == NULL || file_size == NULL || read == NULL) {
        return NULL;
    }
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "save_game/%s", name);
    int bytes = file_size(storage, path);
    if (bytes <= 0) {
        snprintf(path, sizeof(path), "%s", name);
        bytes = file_size(storage, path);
    }
    if (bytes <= 0) {
        return NULL;
    }
    unsigned char* data = (unsigned char*)malloc(bytes);
    if (data != NULL && read(storage, path, data, bytes) != bytes) {
        free(data);
        data = NULL;
    }
    *size = (size_t)bytes;
    return data;
}

/*
**	Whether this build can load a .sav: this build's marker and version, and the TS-HD pack loaded if the save
**	needs it. The chunk-file layout it walks is in docs/pack-panel.md.
*/
SaveCheck Save_Loadable(const unsigned char* d, size_t n)
{
    if (n < 0x24 || d[0] != 'C' || d[1] != 'H') {
        return SAVE_OTHER_VERSION;
    }
    size_t p = 0x24 + *(const DWORD*)(d + 0x10);
    size_t k = 0;
    for (size_t i = p; i + 4 <= n && i < p + 4096; i++) {
        if (d[i] == 0 && d[i + 1] == 0 && d[i + 2] == 0xFF && d[i + 3] == 0xFF) {
            k = i + 4;
            break;
        }
    }
    if (k == 0 || k + 20 > n) {
        return SAVE_OTHER_VERSION;
    }
    unsigned long source = *(const DWORD*)(d + k + 8);
    if (source > n - k - 20) {
        source = (unsigned long)(n - k - 20);
    }
    unsigned char* out = (unsigned char*)calloc(SAVE_HEAD_BYTES, 1);
    if (out == NULL) {
        return SAVE_OTHER_VERSION;
    }
    unsigned long length = SAVE_HEAD_BYTES;
    puff(out, &length, d + k + 20, &source);
    SaveCheck check = SAVE_OTHER_VERSION;
    for (size_t i = 0; i + 12 <= SAVE_HEAD_BYTES; i++) {
        if (memcmp(out + i, TF_SAVE_MARKER, 4) == 0) {
            if (*(const DWORD*)(out + i + 4) == TF_Save_Version()) {
                bool needs_pack = (*(const DWORD*)(out + i + 8) & TF_SAVE_TS_PACK) != 0;
                check = (needs_pack && !Pack_Loaded(Pack_State(TS_HD_PACK))) ? SAVE_NEEDS_PACK : SAVE_LOADABLE;
            }
            break;
        }
    }
    free(out);
    return check;
}

/*
**	Save_Loadable for a listed save, read once per file name.
*/
SaveCheck Listed_Save_Check(const char* name)
{
    static char last[MAX_PATH] = "";
    static SaveCheck last_check = SAVE_OTHER_VERSION;
    if (strcmp(name, last) == 0) {
        return last_check;
    }
    size_t size = 0;
    unsigned char* data = Read_Save(name, &size);
    last_check = data != NULL ? Save_Loadable(data, size) : SAVE_OTHER_VERSION;
    free(data);
    snprintf(last, sizeof(last), "%s", name);
    return last_check;
}

/*
**	The load screen's selected save: one this build can't load takes the missing-map path, with our reason.
*/
void __stdcall Load_Map_Checked(DWORD* regs)
{
    const MsvcString* file = (const MsvcString*)(regs[1] + ENTRY_FILE);
    SaveCheck check = Listed_Save_Check(TF_String_Chars(file));
    SaveRefused = check != SAVE_LOADABLE ? 1 : 0;
    SaveRefusedText = check == SAVE_NEEDS_PACK ? SaveNeedsPackText : SaveOtherVersionText;
    SaveRefusedLength = (DWORD)strlen(SaveRefusedText);
    if (SaveRefused) {
        regs[7] = 0;
    }
}

/*
**	At the missing-map reason: cmp byte [SaveRefused],0 / je stock / push [length] / push [text] /
**	jmp back; stock: the original push 0x1C / push "TEXT_LOAD_MISSING_CUSTOM_MAP" / jmp back.
*/
bool Load_Reason_Install(void)
{
    static const unsigned char stock[7] = {0x6A, 0x1C, 0x68, 0x1C, 0x20, 0xC1, 0x01};
    if (memcmp((const void*)LOAD_REASON, stock, sizeof(stock)) != 0 || !Cave_Is_Free(LOAD_REASON_CAVE, 38)) {
        return false;
    }
    unsigned char cave[38] = {0x80, 0x3D, 0, 0, 0, 0, 0x00, 0x74, 0x11, 0xFF, 0x35, 0, 0, 0, 0, 0xFF, 0x35, 0, 0,
                              0, 0, 0xE9, 0, 0, 0, 0, 0x6A, 0x1C, 0x68, 0x1C, 0x20, 0xC1, 0x01, 0xE9};
    *(DWORD*)(cave + 2) = (DWORD)(SIZE_T)&SaveRefused;
    *(DWORD*)(cave + 11) = (DWORD)(SIZE_T)&SaveRefusedLength;
    *(DWORD*)(cave + 17) = (DWORD)(SIZE_T)&SaveRefusedText;
    TF_Put_Rel32(cave + 22, LOAD_REASON_CAVE + 26, LOAD_REASON_RESUME);
    TF_Put_Rel32(cave + 34, LOAD_REASON_CAVE + 38, LOAD_REASON_RESUME);
    unsigned char jump[7] = {0xE9, 0, 0, 0, 0, 0x90, 0x90};
    TF_Put_Rel32(jump + 1, LOAD_REASON + 5, LOAD_REASON_CAVE);
    return TF_Write_Own_Code(LOAD_REASON_CAVE, cave, sizeof(cave))
           && TF_Write_Own_Code(LOAD_REASON, jump, sizeof(jump));
}

/*
**	True when the launcher functions the pack panel calls still start as this launcher build's do.
*/
bool Panel_Calls_Match(void)
{
    struct Prologue
    {
        SIZE_T Address;
        unsigned char Bytes[6];
    };
    static const Prologue calls[] = {
        {SET_MOD_ENABLED, {0x55, 0x8B, 0xEC, 0x51, 0x8B, 0xC1}},
        {PROFILE_SAVE, {0x55, 0x8B, 0xEC, 0x8B, 0x45, 0x10}},
        {RESTART_MESSAGE, {0x6A, 0x08, 0xE8, 0x89, 0x91, 0x7D}},
        {POST_TO_LAUNCHER, {0x55, 0x8B, 0xEC, 0xFF, 0x75, 0x08}},
        {SET_TEXT, {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x1C}},
        {AS_QUAD, {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x64}},
        {MOD_MANAGER_GET, {0xA1, 0x10, 0x45, 0xFA, 0x01, 0x85}},
        {LOBBY_BACK, {0x56, 0x8B, 0xF1, 0xE8, 0xB8, 0xFB}},
        {SHOW_DIALOG, {0x55, 0x8B, 0xEC, 0xA1, 0xD8, 0x83}},
        {CLIENT_NEW, {0x55, 0x8B, 0xEC, 0x5D, 0xE9, 0xD7}},
        {CLIENT_FREE, {0xE9, 0x4B, 0x09, 0x00, 0x00, 0xCC}},
        {BIND_EVENT, {0x55, 0x8B, 0xEC, 0x51, 0x53, 0x8B}},
        {AS_TEXT_BUTTON, {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x64}},
        {GUI_MANAGER, {0xA1, 0xB8, 0x3F, 0xFA, 0x01, 0x85}},
        {CREATE_SCENE, {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x1C}},
        {SCENE_FOCUS, {0x53, 0x56, 0x57, 0x8B, 0xF9, 0xE8}},
        {SCENE_RELEASE, {0x53, 0x8B, 0xD9, 0x83, 0x7B, 0x04}},
        {AS_BUTTON, {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x4C}},
        {SET_TOGGLED, {0x55, 0x8B, 0xEC, 0x0F, 0xB6, 0x45}},
        {AS_LISTBOX, {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x64}},
        {AS_EXAMPLE, {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x64}},
        {LIST_CLEAR, {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x0C}},
        {LIST_ADD_ROW, {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x3C}},
        {ROW_SET_ITEM, {0x55, 0x8B, 0xEC, 0x83, 0x3D, 0x98}},
        {LIST_SELECT_INDEX, {0x55, 0x8B, 0xEC, 0x56, 0x8B, 0xF1}},
        {QUAD_SET_TEXTURE, {0x55, 0x8B, 0xEC, 0x80, 0x3D, 0x68}},
        {FIND_TEXTURE, {0x55, 0x8B, 0xEC, 0x53, 0x8B, 0x5D}},
    };
    for (size_t i = 0; i < sizeof(calls) / sizeof(calls[0]); i++) {
        if (memcmp((const void*)calls[i].Address, calls[i].Bytes, sizeof(calls[i].Bytes)) != 0) {
            return false;
        }
    }
    return true;
}

/*
**	Installs the pack panel, the lobby popup, the save check and the menu's ADD-ONS and FACTION ENCYCLOPEDIA
**	buttons; leaves them all out on another launcher build.
*/
const char* Pack_Notice_Install(void)
{
    static const unsigned char picked_stock[6] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x24};
    static const unsigned char slot_stock[6] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x44};
    static const unsigned char bind_stock[7] = {0x6A, 0x15, 0x68, 0xF0, 0x7E, 0xC1, 0x01};
    if (!Panel_Calls_Match() || !Detour_Ready(FACTION_PICKED, picked_stock, sizeof(picked_stock), FACTION_PICKED_CAVE)
        || !Detour_Ready(SLOT_SET_FACTION, slot_stock, sizeof(slot_stock), SLOT_SET_FACTION_CAVE)
        || !Snapshot_Ready(MENU_BIND_HOOK, bind_stock, sizeof(bind_stock), MENU_BIND_CAVE)) {
        return "pack notice: unknown launcher build, left alone";
    }
    if (!Detour(FACTION_PICKED, picked_stock, sizeof(picked_stock), FACTION_PICKED_CAVE, (SIZE_T)&Faction_Picked)
        || !Detour(SLOT_SET_FACTION, slot_stock, sizeof(slot_stock), SLOT_SET_FACTION_CAVE, (SIZE_T)&Slot_Set_Faction)
        || !Snapshot_Hook(MENU_BIND_HOOK, bind_stock, sizeof(bind_stock), MENU_BIND_CAVE, (SIZE_T)&Menu_Bound)) {
        return "pack notice: write failed";
    }
    static const unsigned char checked_stock[5] = {0x8B, 0x4F, 0x74, 0x85, 0xC0};
    if (!Snapshot_Ready(LOAD_MAP_CHECKED, checked_stock, sizeof(checked_stock), LOAD_MAP_CAVE) || !Load_Reason_Install()
        || !Snapshot_Hook(
            LOAD_MAP_CHECKED, checked_stock, sizeof(checked_stock), LOAD_MAP_CAVE, (SIZE_T)&Load_Map_Checked)) {
        return "pack notice installed; save check: unknown launcher build, left alone";
    }
    return "pack notice installed";
}

#if TF_DEV_BUILD
/*
**	The mission carrier, unfinished (docs/campaigns-page.md): a mod mission launches under a
**	stock instance's name, so the instance server accepts it, and plays the mod's own map.
*/
const SIZE_T LAUNCH_SEND_CALL = 0x6284B0;
// Every other call of the launch send: skirmish, lobby, load, resume and restart starts.
const SIZE_T OTHER_LAUNCH_CALLS[] = {0x633A5E, 0x715E8D, 0x72003B, 0x723C16, 0x72D9B8, 0x72DED9, 0x7E8A8D};
const SIZE_T LAUNCH_SEND = 0x7F1C40;
const SIZE_T CAMPAIGN_OVER_CALL = 0x627BA0;
const SIZE_T MENU_RETURN = 0x6ABCD0;
const SIZE_T SHOW_CREDITS = 0x6E4890;
const SIZE_T KEY_LOOKUP = 0x14FE820;
const SIZE_T KEY_LOOKUP_CAVE = 0x1BE9380;
const SIZE_T STAGE_CHECK = 0x627BF1;
const SIZE_T STAGE_CHECK_CAVE = 0x1BE93A0;
const DWORD CARRIER_KEY = 0x96C5CC5F;
const DWORD MISSION_LIST_ROW_CALLER = 0x64A02A;
const DWORD MISSION_LIST_OPEN_CALLER = 0x63358C;
const DWORD MISSION_LIST_SELECT_CALLER = 0x632A99;
const DWORD HANDOFF_MAX_AGE_MS = 60000;

bool CarrierSession = false;
DWORD CarrierLaunchedKey = 0;
DWORD SkirmishCarrierKey = 0;
DWORD SkirmishLaunchedKey = 0;

/*
**	An instance name as the launch message reads it: the string, then the name's key.
*/
struct InstanceNameView
{
    MsvcString name;
    DWORD key;
};

typedef char(__thiscall* LaunchSendFn)(void* ipc, const void* name, void* settings, int mode, int a, int b);
typedef void(__thiscall* MenuReturnFn)(void* menu);
typedef void(__stdcall* ShowCreditsFn)(void* unused);

/*
**	An instance's key as ClientG computes it: the CRC32 of the upper-case name.
*/
DWORD Name_Key(const char* name)
{
    DWORD crc = 0xFFFFFFFF;
    for (; *name; name++) {
        crc ^= (unsigned char)toupper((unsigned char)*name);
        for (int bit = 0; bit < 8; bit++) {
            crc = (crc >> 1) ^ (0xEDB88320 & (0 - (crc & 1)));
        }
    }
    return ~crc;
}

/*
**	A dword of ClientG memory, or 0 when it can't be read.
*/
DWORD Read_Dword(DWORD at)
{
    return IsBadReadPtr((const void*)at, 4) ? 0 : *(const DWORD*)at;
}

/*
**	The file a carrier launch hands its map to the DLL's scenario load through.
*/
bool Handoff_Path(char* out, size_t size)
{
    const char* up = getenv("USERPROFILE");
    if (up == NULL) {
        return false;
    }
    snprintf(out, size, "%s/Documents/CnCRemastered/tf_carrier_mission.txt", up);
    return true;
}

/*
**	Sends the launch message; a TF_ instance goes to the server under the carrier's name and
**	key with its map handed over, while ClientG keeps the instance it launched.
*/
char __fastcall Launch_Send(void* ipc, void*, const MsvcString* name, void* settings, int mode, int a, int b)
{
    // An official-list TD map (Mobius_Red_Alert_Multiplayer_9NN_Map) launches as a stock RA map with
    // TFTD9NN.INI handed over: the server knows only the base game's instances.
    static const char td_prefix[] = "MOBIUS_RED_ALERT_MULTIPLAYER_9";
    {
        // TF: probe: every launch name, to tf_scenario.log.
        const char* up = getenv("USERPROFILE");
        char path[MAX_PATH];
        snprintf(path, sizeof(path), "%s/Documents/CnCRemastered/tf_scenario.log", up ? up : ".");
        FILE* lf = fopen(path, "a");
        if (lf != NULL) {
            bool ok = !IsBadReadPtr(name, sizeof(*name)) && name->size < 128;
            fprintf(lf, "launch name=%s size=%d\n", ok ? TF_String_Chars(name) : "?", ok ? (int)name->size : -1);
            fclose(lf);
        }
    }
    if (!IsBadReadPtr(name, sizeof(*name)) && name->size < 128
        && _strnicmp(TF_String_Chars(name), td_prefix, sizeof(td_prefix) - 1) == 0) {
        int number = atoi(TF_String_Chars(name) + sizeof(td_prefix) - 2);
        static char skirmish_text[] = "MOBIUS_RED_ALERT_MULTIPLAYER_D6_MAP";
        InstanceNameView skirmish = {};
        *(char**)skirmish.name.buf = skirmish_text;
        skirmish.name.size = sizeof(skirmish_text) - 1;
        skirmish.name.capacity = sizeof(skirmish_text) - 1;
        skirmish.key = Name_Key(skirmish_text);
        char handoff[MAX_PATH];
        if (Handoff_Path(handoff, sizeof(handoff))) {
            FILE* f = fopen(handoff, "w");
            if (f != NULL) {
                // A stock map listed through its own entry keeps its map file; a TD map is TFTD9NN.INI.
                static const struct
                {
                    int number;
                    const char* map;
                } own_files[] = {{999, "SCMD6EA.INI"}};
                const char* map = NULL;
                for (size_t i = 0; i < sizeof(own_files) / sizeof(own_files[0]); i++) {
                    if (own_files[i].number == number) {
                        map = own_files[i].map;
                    }
                }
                if (map != NULL) {
                    fputs(map, f);
                } else {
                    fprintf(f, "TFTD%03d.INI", number);
                }
                fclose(f);
            }
        }
        CarrierSession = false;
        SkirmishCarrierKey = skirmish.key;
        SkirmishLaunchedKey = Name_Key(TF_String_Chars(name));
        return ((LaunchSendFn)LAUNCH_SEND)(ipc, &skirmish, settings, mode, a, b);
    }
    bool swap = !IsBadReadPtr(name, sizeof(*name)) && name->size < 128 && strncmp(TF_String_Chars(name), "TF_", 3) == 0;
    CarrierSession = false;
    if (!swap) {
        return ((LaunchSendFn)LAUNCH_SEND)(ipc, name, settings, mode, a, b);
    }

    static char carrier_text[] = "MOBIUS_ALLIED_CAMPAIGN_1_MAP";
    InstanceNameView carrier = {};
    *(char**)carrier.name.buf = carrier_text;
    carrier.name.size = sizeof(carrier_text) - 1;
    carrier.name.capacity = sizeof(carrier_text) - 1;
    carrier.key = CARRIER_KEY;

    char handoff[MAX_PATH];
    if (Handoff_Path(handoff, sizeof(handoff))) {
        FILE* f = fopen(handoff, "w");
        if (f != NULL) {
            fputs("SCG01EA.INI", f);
            fclose(f);
        }
    }
    char sent = ((LaunchSendFn)LAUNCH_SEND)(ipc, &carrier, settings, mode, a, b);
    CarrierSession = sent != 0;
    if (!sent && Handoff_Path(handoff, sizeof(handoff))) {
        DeleteFileA(handoff);
    }
    CarrierLaunchedKey = Name_Key(TF_String_Chars(name));
    return sent;
}

/*
**	Runs where ClientG leaves a finished campaign for the menu; a mod campaign then rolls the
**	credits screen.
*/
void __fastcall Campaign_Over(void* menu, void*)
{
    ((MenuReturnFn)MENU_RETURN)(menu);
    if (CarrierSession) {
        CarrierSession = false;
        ((ShowCreditsFn)SHOW_CREDITS)(NULL);
    }
}

/*
**	At the instance lookup by key: during a carrier session the carrier's key reads as the mod
**	mission's, so its progress and medal land on it; the mission list keeps the real lookup.
*/
void __stdcall Key_Lookup_Hit(const DWORD* regs)
{
    DWORD stack = regs[3] + 4;
    DWORD ret = *(const DWORD*)stack;
    // The carrier's own entry is hidden from the map list, so its key always reads as the last TD map launched.
    if (SkirmishCarrierKey != 0 && *(const DWORD*)(stack + 4) == SkirmishCarrierKey) {
        *(DWORD*)(stack + 4) = SkirmishLaunchedKey;
        return;
    }
    if (CarrierSession && *(const DWORD*)(stack + 4) == CARRIER_KEY && ret != MISSION_LIST_ROW_CALLER
        && ret != MISSION_LIST_OPEN_CALLER && ret != MISSION_LIST_SELECT_CALLER) {
        *(DWORD*)(stack + 4) = CarrierLaunchedKey;
    }
}

/*
**	At the campaign map's stage check: a carrier campaign stage holding one mission skips the
**	map the way the stock single-mission stages do.
*/
void __stdcall Stage_Check_Hit(const DWORD* regs)
{
    if (!CarrierSession) {
        return;
    }
    DWORD stage = Read_Dword(regs[0] + 0x78);
    DWORD count = (Read_Dword(stage + 0x78) - Read_Dword(stage + 0x74)) / 32;
    if (count == 1) {
        *(unsigned char*)(stage + 0x70) = 1;
    }
}

/*
**	Installs the carrier's hooks, every site checked before any is written.
*/
const char* Carrier_Install(void)
{
    static const unsigned char lookup_stock[6] = {0x55, 0x8B, 0xEC, 0x56, 0x8B, 0xF1};
    static const unsigned char stage_stock[7] = {0x8B, 0x47, 0x78, 0x80, 0x78, 0x70, 0x00};
    if (!TF_Call_Ready(LAUNCH_SEND_CALL, LAUNCH_SEND) || !TF_Call_Ready(CAMPAIGN_OVER_CALL, MENU_RETURN)
        || !Snapshot_Ready(KEY_LOOKUP, lookup_stock, sizeof(lookup_stock), KEY_LOOKUP_CAVE)
        || !Snapshot_Ready(STAGE_CHECK, stage_stock, sizeof(stage_stock), STAGE_CHECK_CAVE)) {
        return "carrier: unknown launcher build, left alone";
    }
    if (!TF_Redirect_Call(LAUNCH_SEND_CALL, (SIZE_T)&Launch_Send)
        || !TF_Redirect_Call(CAMPAIGN_OVER_CALL, (SIZE_T)&Campaign_Over)
        || !Snapshot_Hook(KEY_LOOKUP, lookup_stock, sizeof(lookup_stock), KEY_LOOKUP_CAVE, (SIZE_T)&Key_Lookup_Hit)
        || !Snapshot_Hook(STAGE_CHECK, stage_stock, sizeof(stage_stock), STAGE_CHECK_CAVE, (SIZE_T)&Stage_Check_Hit)) {
        return "carrier: write failed";
    }
    int others = 0;
    for (size_t i = 0; i < sizeof(OTHER_LAUNCH_CALLS) / sizeof(OTHER_LAUNCH_CALLS[0]); i++) {
        if (TF_Call_Ready(OTHER_LAUNCH_CALLS[i], LAUNCH_SEND)
            && TF_Redirect_Call(OTHER_LAUNCH_CALLS[i], (SIZE_T)&Launch_Send)) {
            others++;
        }
    }
    {
        // TF: probe: the install result, to tf_scenario.log.
        const char* up = getenv("USERPROFILE");
        char path[MAX_PATH];
        snprintf(path, sizeof(path), "%s/Documents/CnCRemastered/tf_scenario.log", up ? up : ".");
        FILE* lf = fopen(path, "a");
        if (lf != NULL) {
            fprintf(lf, "carrier installed, %d of %d other launch calls hooked\n", others,
                    (int)(sizeof(OTHER_LAUNCH_CALLS) / sizeof(OTHER_LAUNCH_CALLS[0])));
            fclose(lf);
        }
    }
    return "carrier installed";
}
#endif

} // namespace

int TF_Mod_Roots(const MsvcString** first)
{
    const MsvcStringVector* roots = (const MsvcStringVector*)MOD_ROOTS;
    if (IsBadReadPtr(roots, sizeof(*roots)) || roots->First == NULL || roots->Last < roots->First
        || roots->Last - roots->First >= 64) {
        return 0;
    }
    *first = roots->First;
    return (int)(roots->Last - roots->First);
}

const char* TF_Launcher_Install(void)
{
    /*
    **	Every hook calls into this DLL, so it stays loaded once they are in.
    */
    HMODULE self = NULL;
    if (!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_PIN,
                            (LPCSTR)&TF_Launcher_Install,
                            &self)) {
        return "launcher: could not pin the DLL, left alone";
    }
    const char* page = Campaign_Page_Install();
    const char* notice = Pack_Notice_Install();
    const char* music = TF_Music_Install();
    static char result[224];
#if TF_DEV_BUILD
    snprintf(result, sizeof(result), "%s; %s; %s; %s", page, notice, music, Carrier_Install());
#else
    snprintf(result, sizeof(result), "%s; %s; %s", page, notice, music);
#endif
    return result;
}

bool TF_Launcher_Take_Carrier_Map(char* map, size_t size)
{
#if !TF_DEV_BUILD
    return false;
#else
    char handoff[MAX_PATH];
    if (!Handoff_Path(handoff, sizeof(handoff))) {
        return false;
    }
    WIN32_FILE_ATTRIBUTE_DATA info;
    if (!GetFileAttributesExA(handoff, GetFileExInfoStandard, &info)) {
        return false;
    }
    FILETIME now_ft;
    GetSystemTimeAsFileTime(&now_ft);
    ULARGE_INTEGER now, written;
    now.LowPart = now_ft.dwLowDateTime;
    now.HighPart = now_ft.dwHighDateTime;
    written.LowPart = info.ftLastWriteTime.dwLowDateTime;
    written.HighPart = info.ftLastWriteTime.dwHighDateTime;
    bool fresh = now.QuadPart >= written.QuadPart && (now.QuadPart - written.QuadPart) / 10000 < HANDOFF_MAX_AGE_MS;

    bool got = false;
    FILE* f = fopen(handoff, "r");
    if (f != NULL) {
        got = fresh && fgets(map, (int)size, f) != NULL && map[0] != 0;
        fclose(f);
    }
    DeleteFileA(handoff);
    if (got) {
        map[strcspn(map, "\r\n")] = 0;
    }
    return got && map[0] != 0;
#endif
}
