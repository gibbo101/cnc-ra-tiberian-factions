/*
**	The mod's launcher layer: code that runs inside ClientG.exe 1.153.745903, installed when
**	the launcher loads the DLL at startup. Addresses are that build's. The campaign page it
**	drives is described in docs/campaigns-page.md.
*/
#include "tf_launcher.h"
#include "function.h"

#include <cstdio>
#include <cstdlib>
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

void Set_Hidden(void* widget, bool hidden)
{
    if (widget != NULL) {
        ((SetHiddenFn)(*(SIZE_T**)widget)[WIDGET_SET_HIDDEN / 4])(widget, hidden ? 1 : 0);
    }
}

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
**	Moves a function's first instructions (`stock`, position independent) into `cave` with a
**	jump back, then points the function at `hook`; the cave becomes the stock function.
*/
bool Detour(SIZE_T function, const unsigned char* stock, size_t length, SIZE_T cave, SIZE_T hook)
{
    unsigned char trampoline[32];
    if (length < 5 || length + 5 > sizeof(trampoline) || memcmp((const void*)function, stock, length) != 0
        || !Cave_Is_Free(cave, (int)(length + 5))) {
        return false;
    }
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
**	Points a `call` at `site` from `stock_target` to `hook`; false when the site differs.
*/
bool Redirect_Call(SIZE_T site, SIZE_T stock_target, SIZE_T hook)
{
    unsigned char call[5] = {0xE8, 0, 0, 0, 0};
    TF_Put_Rel32(call + 1, site + 5, stock_target);
    if (memcmp((const void*)site, call, sizeof(call)) != 0) {
        return false;
    }
    TF_Put_Rel32(call + 1, site + 5, hook);
    return TF_Write_Own_Code(site, call, sizeof(call));
}

/*
**	Instance fields the campaign page reads. The house is ClientG's ExternalFactionType.
*/
const DWORD INSTANCE_FACTION = 0x488;
const DWORD INSTANCE_MISSION = 0x48C;
const DWORD INSTANCE_EXPANSION = 0x54C;
const DWORD INSTANCE_CUSTOM = 0x6A4;
const DWORD INSTANCE_NO_LABEL = 0x1B2;
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
**	number ("GDI 1", "TS GDI 1" on the Tiberian Sun tab); any other mission keeps the stock label.
*/
MsvcWString* __fastcall Mission_Label(const void* instance, void*, MsvcWString* out)
{
    DWORD faction = Instance_Field(instance, INSTANCE_FACTION);
    bool ours = (faction == FACTION_GDI || faction == FACTION_NOD) && Instance_Field(instance, INSTANCE_CUSTOM) == 0
                && ((const char*)instance)[INSTANCE_NO_LABEL] == 0;
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

const char* Campaign_Page_Install(void)
{
    if (!Redirect_Call(EXPANSION_ALLIED_CALL, IS_ALLIED_SIDE, (SIZE_T)&Expansion_Allied_Side)
        || !Redirect_Call(EXPANSION_SOVIET_CALL, IS_SOVIET_SIDE, (SIZE_T)&Expansion_Soviet_Side)) {
        return "campaign page: unknown launcher build, left alone";
    }

    /*
    **	The RA row style choice becomes: mov edx,ebx (instance) / mov ecx,edi (row) /
    **	call Row_Style / jmp ROW_STYLE_DONE.
    */
    static const unsigned char style_stock[13] = {0x8B, 0xCB, 0xE8, 0x2F, 0xB8, 0xB5, 0x00, 0x8B, 0xCF, 0x84, 0xC0, 0x74, 0x07};
    if (memcmp((const void*)ROW_STYLE_BRANCH, style_stock, sizeof(style_stock)) != 0) {
        return "campaign page: row style, unknown launcher build";
    }
    unsigned char style[14] = {0x8B, 0xD3, 0x8B, 0xCF, 0xE8, 0, 0, 0, 0, 0xE9, 0, 0, 0, 0};
    TF_Put_Rel32(style + 5, ROW_STYLE_BRANCH + 9, (SIZE_T)&Row_Style);
    TF_Put_Rel32(style + 10, ROW_STYLE_BRANCH + 14, ROW_STYLE_DONE);
    if (!TF_Write_Own_Code(ROW_STYLE_BRANCH, style, sizeof(style))) {
        return "campaign page: row style write failed";
    }

    static const unsigned char select_stock[6] = {0x55, 0x8B, 0xEC, 0x56, 0x8B, 0xF1};
    static const unsigned char tab_stock[7] = {0x55, 0x8B, 0xEC, 0x51, 0x8B, 0x45, 0x08};
    static const unsigned char label_stock[9] = {0x55, 0x8B, 0xEC, 0x81, 0xEC, 0x84, 0x01, 0x00, 0x00};
    if (!Detour(ROW_SELECT, select_stock, sizeof(select_stock), SELECT_CAVE, (SIZE_T)&Row_Select)
        || !Detour(TAB_SWITCH, tab_stock, sizeof(tab_stock), TAB_CAVE, (SIZE_T)&Tab_Switch)
        || !Detour(MISSION_LABEL, label_stock, sizeof(label_stock), LABEL_CAVE, (SIZE_T)&Mission_Label)) {
        return "campaign page: hooks not installed";
    }
    return "campaign page installed";
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

const char* String_Chars(const MsvcString* s)
{
    return s->capacity >= 16 ? *(char* const*)s->buf : s->buf;
}

DWORD Name_Key(const char* name)
{
    DWORD crc = 0xFFFFFFFF;
    for (; *name; name++) {
        crc ^= (unsigned char)*name;
        for (int bit = 0; bit < 8; bit++) {
            crc = (crc >> 1) ^ (0xEDB88320 & (0 - (crc & 1)));
        }
    }
    return ~crc;
}

DWORD Read_Dword(DWORD at)
{
    return IsBadReadPtr((const void*)at, 4) ? 0 : *(const DWORD*)at;
}

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
    DWORD stage = Read_Dword(regs[0] + 0x78);
    DWORD count = (Read_Dword(stage + 0x78) - Read_Dword(stage + 0x74)) / 32;
    if (count == 1 && CarrierSession) {
        *(unsigned char*)(stage + 0x70) = 1;
    }
}

/*
**	A register-snapshot hook: pushfd / pushad / push esp / call `hit` / popad / popfd /
**	displaced instructions / jmp back. `hit` reads the pushad block (edi first).
*/
bool Snapshot_Hook(SIZE_T at, const unsigned char* stock, size_t length, SIZE_T cave, SIZE_T hit)
{
    unsigned char stub[32] = {0x9C, 0x60, 0x54, 0xE8};
    if (length < 5 || 15 + length > sizeof(stub) || memcmp((const void*)at, stock, length) != 0
        || !Cave_Is_Free(cave, (int)(15 + length))) {
        return false;
    }
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

const char* Carrier_Install(void)
{
    static const unsigned char lookup_stock[6] = {0x55, 0x8B, 0xEC, 0x56, 0x8B, 0xF1};
    static const unsigned char stage_stock[7] = {0x8B, 0x47, 0x78, 0x80, 0x78, 0x70, 0x00};
    if (!Redirect_Call(LAUNCH_SEND_CALL, LAUNCH_SEND, (SIZE_T)&Launch_Send)
        || !Redirect_Call(CAMPAIGN_OVER_CALL, MENU_RETURN, (SIZE_T)&Campaign_Over)
        || !Snapshot_Hook(KEY_LOOKUP, lookup_stock, sizeof(lookup_stock), KEY_LOOKUP_CAVE, (SIZE_T)&Key_Lookup_Hit)
        || !Snapshot_Hook(STAGE_CHECK, stage_stock, sizeof(stage_stock), STAGE_CHECK_CAVE, (SIZE_T)&Stage_Check_Hit)) {
        return "carrier: not installed";
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
#if TF_DEV_BUILD
    const char* carrier = Carrier_Install();
    if (strcmp(carrier, "carrier installed") != 0) {
        return carrier;
    }
#endif
    return Campaign_Page_Install();
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
