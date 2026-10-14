/*
**	The mod's launcher layer: code that runs inside ClientG.exe 1.153.745903, installed when
**	the launcher loads the DLL at startup. Addresses are that build's. The campaign page it
**	drives is described in docs/campaigns-page.md.
*/
#include "function.h"
#include "tf_launcher.h"

extern "C" {
#include "puff.h"
}

#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <cctype>
#include <cstring>

namespace {

const SIZE_T WIDGET_FIND = 0xF0D980;
const int WIDGET_SET_HIDDEN = 0x78;

struct MsvcString
{
    char buf[16];
    unsigned size;
    unsigned capacity;
};

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

/*
**	The characters of an MSVC std::string, inline or on the heap.
*/
const char* String_Chars(const MsvcString* s)
{
    return s->capacity >= 16 ? *(char* const*)s->buf : s->buf;
}

typedef void*(__thiscall* WidgetFindFn)(void* scene, const MsvcString* name);
typedef void*(__thiscall* AsWidgetFn)(void* owner, int zero, void* widget);
typedef void(__thiscall* SetHiddenFn)(void* widget, int hidden);

/*
**	A named widget of a screen or list row, through ClientG's own find and type cast; NULL
**	when absent. Names fit the 15-character short-string form.
*/
void* Find_Widget(void* owner, const char* name, SIZE_T cast)
{
    MsvcString text = {};
    size_t length = strlen(name);
    if (length > 15) {
        return NULL;
    }
    memcpy(text.buf, name, length + 1);
    text.size = (unsigned)length;
    text.capacity = 15;
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
    if (!Call_Ready(EXPANSION_ALLIED_CALL, IS_ALLIED_SIDE) || !Call_Ready(EXPANSION_SOVIET_CALL, IS_SOVIET_SIDE)
        || memcmp((const void*)ROW_STYLE_BRANCH, style_stock, sizeof(style_stock)) != 0
        || !Detour_Ready(ROW_SELECT, select_stock, sizeof(select_stock), SELECT_CAVE)
        || !Detour_Ready(TAB_SWITCH, tab_stock, sizeof(tab_stock), TAB_CAVE)
        || !Detour_Ready(MISSION_LABEL, label_stock, sizeof(label_stock), LABEL_CAVE)) {
        return "campaign page: unknown launcher build, left alone";
    }
    unsigned char style[14] = {0x8B, 0xD3, 0x8B, 0xCF, 0xE8, 0, 0, 0, 0, 0xE9, 0, 0, 0, 0};
    TF_Put_Rel32(style + 5, ROW_STYLE_BRANCH + 9, (SIZE_T)&Row_Style);
    TF_Put_Rel32(style + 10, ROW_STYLE_BRANCH + 14, ROW_STYLE_DONE);
    if (!Redirect_Call(EXPANSION_ALLIED_CALL, (SIZE_T)&Expansion_Allied_Side)
        || !Redirect_Call(EXPANSION_SOVIET_CALL, (SIZE_T)&Expansion_Soviet_Side)
        || !TF_Write_Own_Code(ROW_STYLE_BRANCH, style, sizeof(style))
        || !Detour(ROW_SELECT, select_stock, sizeof(select_stock), SELECT_CAVE, (SIZE_T)&Row_Select)
        || !Detour(TAB_SWITCH, tab_stock, sizeof(tab_stock), TAB_CAVE, (SIZE_T)&Tab_Switch)
        || !Detour(MISSION_LABEL, label_stock, sizeof(label_stock), LABEL_CAVE, (SIZE_T)&Mission_Label)) {
        return "campaign page: write failed";
    }
    return "campaign page installed";
}


/*
**	The TS-HD-Assets pack as the launcher sees it: enabled (one of its mod roots carries the pack's
**	CCDATA marker), installed but switched off, or missing.
*/
const SIZE_T MOD_ROOTS = 0x1FE4C28;
const char PACK_MARKER[] = "CCDATA\\TSHDPACK.INI";

enum PackState
{
    PACK_ENABLED,
    PACK_INSTALLED_OFF,
    PACK_MISSING
};

struct MsvcStringVector
{
    MsvcString* First;
    MsvcString* Last;
    MsvcString* End;
};

#if TF_DEV_BUILD
/*
**	Appends a line to Documents/CnCRemastered/tf_launcher_pack.log.
*/
void Pack_Log(const char* format, ...)
{
    static int lines = 0;
    const char* up = getenv("USERPROFILE");
    if (up == NULL || lines++ > 400) {
        return;
    }
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "%s/Documents/CnCRemastered/tf_launcher_pack.log", up);
    FILE* f = fopen(path, "a");
    if (f == NULL) {
        return;
    }
    va_list args;
    va_start(args, format);
    vfprintf(f, format, args);
    va_end(args);
    fputc('\n', f);
    fclose(f);
}
#else
void Pack_Log(const char*, ...)
{
}
#endif

// The pack's Red Alert item on the Steam Workshop.
#define TS_HD_WORKSHOP_ID "3819642604"
const char TS_HD_WORKSHOP_PAGE[] = "https://steamcommunity.com/sharedfiles/filedetails/?id=" TS_HD_WORKSHOP_ID;

/*
**	True when `folder` holds the pack's marker.
*/
bool Has_Pack_Marker(const char* folder)
{
    char path[MAX_PATH];
    size_t length = strlen(folder);
    const char* slash = (length > 0 && (folder[length - 1] == '\\' || folder[length - 1] == '/')) ? "" : "\\";
    snprintf(path, sizeof(path), "%s%s%s", folder, slash, PACK_MARKER);
    return GetFileAttributesA(path) != INVALID_FILE_ATTRIBUTES;
}

/*
**	True when any folder directly under `parent` holds the pack's marker.
*/
bool Any_Pack_Under(const char* parent)
{
    char pattern[MAX_PATH];
    snprintf(pattern, sizeof(pattern), "%s\\*", parent);
    WIN32_FIND_DATAA found;
    HANDLE find = FindFirstFileA(pattern, &found);
    if (find == INVALID_HANDLE_VALUE) {
        return false;
    }
    bool any = false;
    do {
        if ((found.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) && found.cFileName[0] != '.') {
            char folder[MAX_PATH];
            snprintf(folder, sizeof(folder), "%s\\%s", parent, found.cFileName);
            any = any || Has_Pack_Marker(folder);
        }
    } while (!any && FindNextFileA(find, &found));
    FindClose(find);
    return any;
}

PackState Pack_State(void)
{
    const MsvcStringVector* roots = (const MsvcStringVector*)MOD_ROOTS;
    if (!IsBadReadPtr(roots, sizeof(*roots)) && roots->First != NULL && roots->Last >= roots->First
        && roots->Last - roots->First < 64) {
        for (const MsvcString* root = roots->First; root < roots->Last; root++) {
            Pack_Log("mod root: %s", String_Chars(root));
            if (Has_Pack_Marker(String_Chars(root))) {
                return PACK_ENABLED;
            }
        }
    }
    char folder[MAX_PATH];
    const char* up = getenv("USERPROFILE");
    if (up != NULL) {
        snprintf(folder, sizeof(folder), "%s\\Documents\\CnCRemastered\\Mods\\Red_Alert", up);
        if (Any_Pack_Under(folder)) {
            return PACK_INSTALLED_OFF;
        }
    }
    char game[MAX_PATH];
    DWORD length = GetModuleFileNameA(NULL, game, sizeof(game));
    char* name = length > 0 && length < sizeof(game) ? strrchr(game, '\\') : NULL;
    if (name != NULL) {
        *name = 0;
        snprintf(folder, sizeof(folder), "%s\\..\\..\\workshop\\content\\1213210\\" TS_HD_WORKSHOP_ID, game);
        Pack_Log("workshop item: %s", folder);
        if (Any_Pack_Under(folder)) {
            return PACK_INSTALLED_OFF;
        }
    }
    return PACK_MISSING;
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

void Free_WString(MsvcWString* s)
{
    if (s->Capacity >= 8) {
        ((ClientFreeFn)CLIENT_FREE)(s->Pointer);
    }
}

void Show_Message(const wchar_t* body)
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
    ((TextLookupFn)TEXT_LOOKUP)((void*)TEXT_MANAGER, &ok, "TEXT_OK");
    MsvcString f = {}, g = {}, h = {};
    f.capacity = g.capacity = h.capacity = 15;
    DialogCallback callback = {NULL, (SIZE_T)&Dialog_Closed};
    ((ShowDialogFn)SHOW_DIALOG)(&callback, &text, &none, &ok, &second, 1, 1, 0, 2, 3, &f, &g, &h);
    Free_WString(&text);
    Free_WString(&ok);
}

/*
**	The message box for a lobby slot playing Tiberian Sun GDI without the pack enabled; one box at
**	a time, so a lobby full of TS GDI slots, or the slot echoing the player's own pick, shows one.
*/
const DWORD PACK_POPUP_HOLD_MS = 10000;

void Pack_Popup(void)
{
    static DWORD shown = 0;
    PackState state = Pack_State();
    DWORD now = GetTickCount();
    if (state == PACK_ENABLED || (shown != 0 && now - shown < PACK_POPUP_HOLD_MS)) {
        return;
    }
    shown = now;
    Show_Message(state == PACK_INSTALLED_OFF ? L"Tiberian Sun GDI needs the Tiberian Sun HD Assets mod, which is installed but "
                                               L"switched off. Enable it in Mods and restart the game."
                                             : L"Tiberian Sun GDI needs the Tiberian Sun HD Assets mod. Subscribe to it on the "
                                               L"Steam Workshop, enable it in Mods and restart the game.");
}

/*
**	The lobby's faction pick: the stock handler, then the pack popup when the local player has
**	just picked Tiberian Sun GDI.
*/
const SIZE_T FACTION_PICKED = 0x676760;
const SIZE_T FACTION_PICKED_CAVE = 0x1BE95C0;
const SIZE_T LOBBY_FACTION = 0x20E0CF8;
const int LOBBY_TS_GDI = 7;

typedef void(__thiscall* FactionPickedFn)(void* slot, int event);

void __fastcall Faction_Picked(void* slot, void*, int event)
{
    int before = *(const int*)LOBBY_FACTION;
    ((FactionPickedFn)FACTION_PICKED_CAVE)(slot, event);
    int after = *(const int*)LOBBY_FACTION;
    Pack_Log("faction pick %d -> %d", before, after);
    if (after != before && after == LOBBY_TS_GDI) {
        Pack_Popup();
    }
}

/*
**	A lobby slot taking its faction from the lobby's settings, the player's own or an AI's, as
**	the lobby opens or updates: the pack popup when a slot turns to Tiberian Sun GDI.
*/
const SIZE_T SLOT_SET_FACTION = 0x677950;
const SIZE_T SLOT_SET_FACTION_CAVE = 0x1BE9650;
const DWORD SLOT_FACTION = 0x1DA8;

typedef void(__thiscall* SlotSetFactionFn)(void* slot, int faction);

void __fastcall Slot_Set_Faction(void* slot, void*, int faction)
{
    int before = *(const int*)((const char*)slot + SLOT_FACTION);
    ((SlotSetFactionFn)SLOT_SET_FACTION_CAVE)(slot, faction);
    int after = *(const int*)((const char*)slot + SLOT_FACTION);
    if (after != before) {
        Pack_Log("slot %p faction %d -> %d", slot, before, after);
    }
    if (after != before && after == LOBBY_TS_GDI) {
        Pack_Popup();
    }
}

/*
**	The pack's Workshop page in the Steam overlay.
*/

typedef void*(__cdecl* SteamFriendsFn)(void);
typedef void(__cdecl* OverlayToWebPageFn)(void* friends, const char* url, int mode);

void Open_Pack_Page(void)
{
    HMODULE steam = GetModuleHandleA("steam_api.dll");
    SteamFriendsFn get = steam ? (SteamFriendsFn)GetProcAddress(steam, "SteamAPI_SteamFriends_v017") : NULL;
    OverlayToWebPageFn open =
        steam ? (OverlayToWebPageFn)GetProcAddress(steam, "SteamAPI_ISteamFriends_ActivateGameOverlayToWebPage") : NULL;
    void* friends = get ? get() : NULL;
    Pack_Log("pack page: steam_api %p friends %p", (void*)steam, friends);
    if (friends != NULL && open != NULL) {
        open(friends, TS_HD_WORKSHOP_PAGE, 0);
    }
}

/*
**	The main menu's pack notice (scripts/bui_mainmenu_pack_notice.py): its button opens the pack's
**	page, and the line that fits the pack's state shows under the menu box.
*/
const SIZE_T MENU_BIND_HOOK = 0x6B185B;
const SIZE_T MENU_BIND_CAVE = 0x1BE95E0;
const SIZE_T AS_TEXT_BUTTON = 0x5EF8A0;
const SIZE_T BIND_EVENT = 0x6A9F50;
const int CLICK_EVENT = 0x21;

typedef void(__thiscall* BindEventFn)(void* menu, int event, void* widget, void* handler, int data);

void __stdcall Pack_Get_Click(void*)
{
    Open_Pack_Page();
}

void __stdcall Menu_Bound(const DWORD* regs)
{
    void* menu = (void*)regs[1];
    PackState state = Pack_State();
    Pack_Log("main menu: pack state %d", (int)state);
    Set_Hidden(Find_Widget(menu, "TF_Pack_Missing", AS_TEXT), state != PACK_MISSING);
    Set_Hidden(Find_Widget(menu, "TF_Pack_Off", AS_TEXT), state != PACK_INSTALLED_OFF);
    void* button = Find_Widget(menu, "TF_Pack_Get", AS_TEXT_BUTTON);
    if (button != NULL) {
        ((BindEventFn)BIND_EVENT)(menu, CLICK_EVENT, button, (void*)&Pack_Get_Click, 0);
        Set_Hidden(button, state != PACK_MISSING);
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
    HMODULE steam = GetModuleHandleA("steam_api.dll");
    SteamStorageFn get = steam ? (SteamStorageFn)GetProcAddress(steam, "SteamAPI_SteamRemoteStorage_v016") : NULL;
    StorageSizeFn file_size = steam ? (StorageSizeFn)GetProcAddress(steam, "SteamAPI_ISteamRemoteStorage_GetFileSize") : NULL;
    StorageReadFn read = steam ? (StorageReadFn)GetProcAddress(steam, "SteamAPI_ISteamRemoteStorage_FileRead") : NULL;
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
**	Whether this build can load a .sav: its DLL data must start with this build's marker and
**	version, and a save made with the TS-HD pack needs the pack enabled now. The file is ClientG's
**	chunk file: a zlib stream to the size at 0x10, a chunk index ending in a sync flush, then the
**	instance chunk (a 20-byte header with its size at +8, raw deflate) holding the DLL's data.
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
                check = (needs_pack && Pack_State() != PACK_ENABLED) ? SAVE_NEEDS_PACK : SAVE_LOADABLE;
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
    Pack_Log("save %s: check %d", name, (int)last_check);
    return last_check;
}

void __stdcall Load_Map_Checked(DWORD* regs)
{
    const MsvcString* file = (const MsvcString*)(regs[1] + ENTRY_FILE);
    SaveCheck check = Listed_Save_Check(String_Chars(file));
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
    return TF_Write_Own_Code(LOAD_REASON_CAVE, cave, sizeof(cave)) && TF_Write_Own_Code(LOAD_REASON, jump, sizeof(jump));
}

const char* Pack_Notice_Install(void)
{
    static const unsigned char picked_stock[6] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x24};
    static const unsigned char slot_stock[6] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x44};
    static const unsigned char bind_stock[7] = {0x6A, 0x15, 0x68, 0xF0, 0x7E, 0xC1, 0x01};
    if (!Detour_Ready(FACTION_PICKED, picked_stock, sizeof(picked_stock), FACTION_PICKED_CAVE)
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
        || !Snapshot_Hook(LOAD_MAP_CHECKED, checked_stock, sizeof(checked_stock), LOAD_MAP_CAVE, (SIZE_T)&Load_Map_Checked)) {
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
    bool swap = !IsBadReadPtr(name, sizeof(*name)) && name->size < 128 && strncmp(String_Chars(name), "TF_", 3) == 0;
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
    CarrierLaunchedKey = Name_Key(String_Chars(name));
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
    if (!Call_Ready(LAUNCH_SEND_CALL, LAUNCH_SEND) || !Call_Ready(CAMPAIGN_OVER_CALL, MENU_RETURN)
        || !Snapshot_Ready(KEY_LOOKUP, lookup_stock, sizeof(lookup_stock), KEY_LOOKUP_CAVE)
        || !Snapshot_Ready(STAGE_CHECK, stage_stock, sizeof(stage_stock), STAGE_CHECK_CAVE)) {
        return "carrier: unknown launcher build, left alone";
    }
    if (!Redirect_Call(LAUNCH_SEND_CALL, (SIZE_T)&Launch_Send) || !Redirect_Call(CAMPAIGN_OVER_CALL, (SIZE_T)&Campaign_Over)
        || !Snapshot_Hook(KEY_LOOKUP, lookup_stock, sizeof(lookup_stock), KEY_LOOKUP_CAVE, (SIZE_T)&Key_Lookup_Hit)
        || !Snapshot_Hook(STAGE_CHECK, stage_stock, sizeof(stage_stock), STAGE_CHECK_CAVE, (SIZE_T)&Stage_Check_Hit)) {
        return "carrier: write failed";
    }
    return "carrier installed";
}
#endif

} // namespace

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
    static char result[192];
#if TF_DEV_BUILD
    snprintf(result, sizeof(result), "%s; %s; %s", page, notice, Carrier_Install());
#else
    snprintf(result, sizeof(result), "%s; %s", page, notice);
#endif
    Pack_Log("install: %s", result);
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
