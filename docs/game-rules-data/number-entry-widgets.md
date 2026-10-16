# Numeric-entry widgets for a SplashScreen BUI (ClientG 1.153.745903)

Read-only research, 2026-10-17. "Proven" = read from ClientG disassembly or stock BUI bytes. "Inferred" = follows
from that but has not run on a machine. Read with a capstone disassembly of ClientG.exe and a dump of
its GUI event-name table.

## GUI event ids (GUIEventDataType registration, fn 0x19E15C0, each `push id; call 0x5680B0`) - proven
| Event | id |
|---|---|
| Mouse_Left_Down / Up | 0x04 / 0x05 |
| Button_Clicked | 0x21 (= CLICK_EVENT in tf_launcher.cpp, cross-check) |
| Key_Press / Key_Up | 0x2F / 0x31 |
| Key_Focus_Gained / Lost | 0x33 / 0x34 |
| Slider_Bar_Released | 0x35 |
| Slider_Bar_Value_Changed | 0x36 |
| List_Selected_Index_Changed | 0x37 |
| Controller_A_Button_Press | 0x3F; DPad Left/Right Press 0x4B / 0x4D |
| Edit_Box_Return | 0x9E |
| Edit_Box_Text_Changed | 0x9F |
| Edit_Box_Cursor_Changed | 0xA0 |
Full list: `clientg-gui-events.txt` in this folder (284 lines).

## Binding
BIND_EVENT 0x6A9F50 is a generic template body (functor vtable 0x1C18A80, handler +8, data +0xC, event id pushed by
caller). The skirmish lobby's own bind 0x629360 is byte-identical bar the vtable, and binds every match-details slider
for 0x36 (handler 0x62A6F0) and 0x35 (0x62B730) at 0x62B050..0x62B211. So BIND_EVENT(screen, 0x36, slider, h, data)
uses the same path as stock sliders: inferred-high.

## Option 1: slider (GUISliderBarClass, component type 0x0E) - natives proven
- Cast: AS_SLIDER = 0x610140 (Safe_Cast_Component<GUISliderBarClass>, checks vtable+0x28 == 0x0E). Lobby does
  Find 0xF0D980 then 0x610140 for "Credits_Slider" (0x62AB2B), stores at lobby+0x7C.
- Fields: +0x200 steps (max index), +0x208 current index, +0x20C button step delta, +0x210 mouse-hold scroll delta (float).
- Set_Steps 0xF8B0F0 thiscall(slider, int steps), ignored if < 1, clamps the index. ret 4.
- Set_Current_Step_Index 0xF8AC70 thiscall(slider, int index, bool notify). Clamps to 0..steps, returns early if
  unchanged; with notify and an owner (+0x14) it posts event 0x36 with the slider as source. ret 8.
- Get index: read int at slider+0x208 (the Lua Get_Current_Step_Index 0x105DED0 does exactly this).
- Stock helper 0x155AE70 cdecl(slider, valueText, count, index, value): Set_Steps(count-1), Set_Current_Step_Index(i, 0),
  formats `value` and sets the text with 0xF1D050. With count < 2 it calls vtable+0x6C(0) (disables, inferred).
- Positions = steps+1 (0..steps). Lobby passes count-1.
- Quads (GUISliderBarClass::QuadIDType): Left 0, Middle 1, Right 2, Filled_Middle 3, Up_Button 4, Down_Button 5,
  Slider_Button 6. Up/Down are the +/- end buttons; BUI props: micro 02 STEPS, 04 BUTTON_STEP_DELTA, 05
  BUTTON_MOUSE_HOLD_SCROLL_DELTA (writer 0xF8AA50). Stock value 30.0 (default set at 0xF8925E). Holding +/- repeats:
  inferred from the property name (not traced).
- Gamepad: no DPad/A ids appear in the slider's code (0xF88000-0xF8C000), so no native pad control. On the Deck it works
  by touch or trackpad-as-mouse (inferred).
- Stock template to clone: RA_UI_MATCHDETAILS_ALLIES.BUI (and _SOVIET, UI_MATCHDETAILS) in CONFIG.MEG. Each row:
  `UI_Credits_Group` {Credits_Title_Text, Credits_Value_Text, Credits_Slider {Bar, Up_Button (+ right), Down_Button
  (- left), Slider_Button (ball)}}. Texture set RA_Option_Menu_Slider_Allied; quads UI_Options_SliderBar_Plus/_Minus,
  RA_UI_Options_SliderBar_Ball_Blue. Slider prop leaf: steps 99, step delta 1, hold delta 30.0.
- Handler: our bound data identifies the slider. The stock handler instead fetches the source with 0xF49680(event).

## Option 2: edit box (GUIEditBoxClass, component type 0x0D) - natives proven
- Cast: AS_EDIT_BOX = 0x5F45C0 (checks type 0x0D).
- Text is the wstring at +0x1F0 (size at +0x200).
- Get_Text 0xF626C0 thiscall(edit, MsvcWString* out) -> out, ret 4 (copies from a +0x290 offset when that is nonzero).
- Set_Text 0xF63E20 thiscall(edit, const MsvcWString*, bool), ret 8, applies the case type. The narrow version is
  0xF63D80(std::string*, bool).
- Set_Editable 0xF63710 thiscall(edit, bool) -> +0x272. Text limit u16 at +0x270 (the Lua Set_Text_Limit writes it).
- BUI property leaf id 3 (writer 0xF63150): 06 JUSTIFICATION u32, 07 PASSWORD u8, 08 TEXT_LIMIT u16 (+0x270),
  09 EDITABLE (+0x272), 0A MULTILINE (+0x273), 0B ACCEPTS_RETURN (+0x274), 0C IS_NUMERIC (+0x275), 0D CASE_TYPE u32
  (+0x278). Font is leaf id 2 ("24 Point Regular").
- IS_NUMERIC is enforced at character insert (0xF612C0): the char must pass iswctype(c, _DIGIT) (0x9D05B0), so
  digits only, no '-' or '.'. The length limit is checked there too. '|' is always refused.
- Events: 0x9F text changed, 0x9E return, 0x33/0x34 focus. The click-to-focus path is the GUIManager focus (0xF2F9B0
  compared in Set_Editable): inferred.
- Stock template: RA_UI_SAVEGAMEPOPUP.BUI `SaveGameUserName_EditBox` (limit 30, editable, not numeric) with child
  quad (type 0x0C) and cursor (type 0x04), plus EditBox_BG_ALLIED/SOVIET quads. Others: Password_Edit_Box
  (RA_UI_MULTIPLAYERMENU), Game_Name_Edit_Box / HostNameEditBox (UI_MENU_MINIMAP), Edit_Box_Search (workshop browse).
- Deck keyboard: ClientG has no ShowGamepadTextInput reference (only the "SteamUtils010" interface string). The 32-bit
  steam_api.dll exports SteamAPI_SteamUtils_v010, ISteamUtils_ShowFloatingGamepadTextInput,
  _IsSteamRunningOnSteamDeck, _ShowGamepadTextInput and _GetEnteredGamepadTextInput, reachable through tf_launcher's
  Steam_Export. Without a call the player must press STEAM+X. With a call on Key_Focus_Gained, the floating keyboard
  types into the focused window: inferred, unproven.

## Option 3: stepper - known working
- Text: Set_Text (tf_launcher.cpp) = WSTRING_ASSIGN 0x578DF0 then SET_TEXT 0xF1D270 thiscall(widget, MsvcWString*).
  The stock slider helper uses 0xF1D050 for the same job (variant, not compared).
- Click is 0x21, which fires on release, so there is no auto-repeat. A hold-repeat needs our own SetTimer between
  Mouse_Left_Down 0x04 and Mouse_Left_Up 0x05 (plus Mouse_Off as a safety). That bind path is already used: the
  encyclopedia's rows take event 4.

## Traps
- Find_Widget names over 15 chars use the lend-in-place path: Credits_Value_Text (18), SaveGameUserName_EditBox (24).
  Name clones uniquely, and give each widget a fresh instance id (bui_tree renumber).
- Set_Current_Step_Index(notify=1) inside a 0x36 handler re-posts 0x36. Set from code with notify=0.
- With 500 steps on a short bar, a drag is coarse. Use +/- (step delta) for fine moves, or set the step size per stat
  (Cost by 10s and so on).
- IS_NUMERIC allows no negative numbers or decimals.
- Every address belongs to 1.153.745903: add their opening bytes to Panel_Calls_Match.

## Smallest probes (later, on a real machine)
1. Slider: clone UI_Credits_Group from RA_UI_MATCHDETAILS_ALLIES.BUI into TF_ENCY.BUI (loose, any size). On open:
   Find(Credits_Slider, 0x610140) -> Set_Steps 0xF8B0F0(50) -> Set_Current_Step_Index 0xF8AC70(10, 0) ->
   BIND_EVENT(screen, 0x36, slider, h, 0). h reads +0x208 and Set_Text's Credits_Value_Text. Pass: drag, +/-,
   hold +/- and Deck touch all update the number.
2. Edit box: clone SaveGameUserName_EditBox and its bg, set micro 0C = 1 and 08 = 5. Bind 0x9F and 0x9E, read with
   0xF626C0, log. On 0x33 call ShowFloatingGamepadTextInput if IsSteamRunningOnSteamDeck. Pass: letters refused, the
   Deck keyboard types into it.
