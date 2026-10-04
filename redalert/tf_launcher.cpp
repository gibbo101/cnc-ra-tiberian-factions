/*
**	The mod's launcher layer: code that runs inside ClientG.exe 1.153.745903, installed when
**	the launcher loads the DLL at startup. Addresses are that build's.
*/
#include "tf_launcher.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace {

const SIZE_T MENU_BIND_HOOK = 0x6B185B;
const SIZE_T MENU_BIND_RESUME = 0x6B1862;
const SIZE_T WIDGET_FIND = 0xF0D980;
const SIZE_T AS_TEXT_BUTTON = 0x5EF8A0;
const SIZE_T BIND_EVENT = 0x6A9F50;
const int CLICK_EVENT = 0x21;
const SIZE_T CAVE = 0x1BE9300;
const SIZE_T MISSION_SELECT_GET = 0x62DA90;
const SIZE_T MISSION_SELECT_SHOW = 0x62D450;
const int CAVE_SIZE = 0x20;

struct MsvcString
{
    char buf[16];
    unsigned size;
    unsigned capacity;
};

typedef void*(__thiscall* WidgetFindFn)(void* scene, const MsvcString* name);
typedef void*(__thiscall* AsTextButtonFn)(void* menu, int zero, void* widget);
typedef void(__thiscall* BindEventFn)(void* menu, int event, void* widget, void* handler, int data);
typedef void*(__cdecl* MissionSelectGetFn)(void);
typedef void(__thiscall* MissionSelectShowFn)(void* dialog);

void Probe_Log(const char* line)
{
    const char* up = getenv("USERPROFILE");
    if (up == NULL) {
        return;
    }
    char logpath[512];
    snprintf(logpath, sizeof(logpath), "%s/Documents/CnCRemastered/tf_menu_probe.log", up);
    FILE* log = fopen(logpath, "a");
    if (log != NULL) {
        SYSTEMTIME now;
        GetLocalTime(&now);
        fprintf(log, "%02d:%02d:%02d %s\n", now.wHour, now.wMinute, now.wSecond, line);
        fclose(log);
    }
}

/*
**	Click handler for the TF_Campaigns button: opens the Mission Select dialog the way its own
**	button does. ClientG calls it with one stack argument and no `this`.
*/
void __stdcall Campaigns_Click(void*)
{
    Probe_Log("TF_Campaigns clicked");
    void* dialog = ((MissionSelectGetFn)MISSION_SELECT_GET)();
    if (dialog == NULL) {
        Probe_Log("TF_Campaigns: no Mission Select dialog");
        return;
    }
    ((MissionSelectShowFn)MISSION_SELECT_SHOW)(dialog);
    Probe_Log("TF_Campaigns: Mission Select opened");
}

/*
**	Called from the main menu's button-binding code with the menu object, the way it binds
**	its own buttons: find the widget by name, take it as a text button, bind its click.
*/
void __stdcall Bind_Menu(void* menu)
{
    MsvcString name = {};
    static const char widget_name[] = "TF_Campaigns";
    memcpy(name.buf, widget_name, sizeof(widget_name));
    name.size = sizeof(widget_name) - 1;
    name.capacity = 15;

    void* scene = *(void**)((char*)menu + 4);
    void* widget = ((WidgetFindFn)WIDGET_FIND)(scene, &name);
    if (widget == NULL) {
        Probe_Log("menu bind: TF_Campaigns not in the scene");
        return;
    }
    void* button = ((AsTextButtonFn)AS_TEXT_BUTTON)(menu, 0, widget);
    if (button == NULL) {
        Probe_Log("menu bind: TF_Campaigns is not a text button");
        return;
    }
    ((BindEventFn)BIND_EVENT)(menu, CLICK_EVENT, button, (void*)&Campaigns_Click, 0);
    Probe_Log("menu bind: TF_Campaigns bound");
}

} // namespace

const char* TF_Launcher_Menu_Install(void)
{
    static const unsigned char stock[7] = {0x6A, 0x15, 0x68, 0xF0, 0x7E, 0xC1, 0x01};
    if (memcmp((const void*)MENU_BIND_HOOK, stock, sizeof(stock)) != 0) {
        Probe_Log("menu: unknown launcher build, left alone");
        return "menu: unknown launcher build, left alone";
    }
    for (int i = 0; i < CAVE_SIZE; i++) {
        if (((const unsigned char*)CAVE)[i] != 0) {
            Probe_Log("menu: cave in use, left alone");
            return "menu: cave in use, left alone";
        }
    }
    HMODULE self = NULL;
    if (!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_PIN,
                            (LPCSTR)&Bind_Menu,
                            &self)) {
        Probe_Log("menu: could not pin the DLL");
        return "menu: could not pin the DLL";
    }

    /*
    **	pushfd / pushad / push esi / call Bind_Menu / popad / popfd /
    **	push 0x15 / push 0x1C17EF0 / jmp MENU_BIND_RESUME
    */
    unsigned char stub[22] = {0x9C, 0x60, 0x56, 0xE8, 0, 0, 0, 0, 0x61, 0x9D, 0x6A,
                              0x15, 0x68, 0xF0, 0x7E, 0xC1, 0x01, 0xE9, 0, 0, 0, 0};
    TF_Put_Rel32(stub + 4, CAVE + 8, (SIZE_T)&Bind_Menu);
    TF_Put_Rel32(stub + 18, CAVE + 22, MENU_BIND_RESUME);
    unsigned char jump[7] = {0xE9, 0, 0, 0, 0, 0x90, 0x90};
    TF_Put_Rel32(jump + 1, MENU_BIND_HOOK + 5, CAVE);
    if (!TF_Write_Own_Code(CAVE, stub, sizeof(stub)) || !TF_Write_Own_Code(MENU_BIND_HOOK, jump, sizeof(jump))) {
        Probe_Log("menu: write failed");
        return "menu: write failed";
    }
    Probe_Log("menu: binding hook installed");
    return "menu: binding hook installed";
}
