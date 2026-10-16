/*
**	The encyclopedia's data (docs/encyclopedia.md). ClientG never starts the game side of this DLL, so the
**	encyclopedia builds the type tables and processes the mod's rules itself, as a skirmish does.
*/
#include "function.h"
#include "tf_encyclopedia.h"

#include <algorithm>
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <vector>

namespace {

struct XmlEntry
{
    std::string NameKey;
    std::string DescKey;
    std::string Cameo;
};

std::map<std::string, XmlEntry> XmlEntries;
std::vector<std::string> XmlRoots;
bool Loaded = false;
bool LoadedOk = false;

/*
**	The mod's own folder: the DLL sits in its Data folder.
*/
bool Mod_Folder(char* out, size_t size)
{
    HMODULE self = NULL;
    GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                       (LPCSTR)&Mod_Folder,
                       &self);
    DWORD length = GetModuleFileNameA(self, out, (DWORD)size);
    if (length == 0 || length >= size) {
        return false;
    }
    for (int strip = 0; strip < 2; strip++) {
        char* slash = strrchr(out, '\\');
        if (slash == NULL) {
            return false;
        }
        *slash = 0;
    }
    return true;
}

/*
**	Loads an INI from an absolute path; false when the file is missing or empty.
*/
bool Load_Ini(CCINIClass& ini, const char* folder, const char* name)
{
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "%s\\CCDATA\\%s", folder, name);
    RawFileClass file(path);
    return file.Is_Available() && ini.Load(file, false);
}

/*
**	Applies an INI's values over the processed rules, as a skirmish applies mplayer.ini; the heaps stay as built.
*/
void Apply_Overrides(CCINIClass& ini)
{
    Rule.General(ini);
    Rule.Recharge(ini);
    Rule.AI(ini);
    Rule.Powerups(ini);
    Rule.Land_Types(ini);
    Rule.Themes(ini);
    Rule.IQ(ini);
    Rule.Objects(ini);
    Rule.Difficulty(ini);
}

/*
**	The text between <tag> and </tag> inside [from, to); empty when absent.
*/
std::string Tag_Text(const char* from, const char* to, const char* tag)
{
    char open[64], close[64];
    snprintf(open, sizeof(open), "<%s>", tag);
    snprintf(close, sizeof(close), "</%s>", tag);
    const char* a = std::search(from, to, open, open + strlen(open));
    if (a == to) {
        return std::string();
    }
    a += strlen(open);
    const char* b = std::search(a, to, close, close + strlen(close));
    return b == to ? std::string() : std::string(a, b);
}

/*
**	Reads every ObjectTypeClass entry of one buildables XML file: its name and description text keys and cameo.
*/
void Read_Buildables(const char* path)
{
    FILE* f = fopen(path, "rb");
    if (f == NULL) {
        return;
    }
    std::vector<char> text;
    char block[65536];
    size_t got;
    while ((got = fread(block, 1, sizeof(block), f)) > 0) {
        text.insert(text.end(), block, block + got);
    }
    fclose(f);
    const char* end = text.data() + text.size();
    static const char start[] = "<ObjectTypeClass Name=\"";
    static const char stop[] = "</ObjectTypeClass>";
    for (const char* p = text.data(); p < end;) {
        const char* entry = std::search(p, end, start, start + sizeof(start) - 1);
        if (entry == end) {
            break;
        }
        const char* name = entry + sizeof(start) - 1;
        const char* quote = std::find(name, end, '"');
        const char* close = std::search(quote, end, stop, stop + sizeof(stop) - 1);
        XmlEntry& e = XmlEntries[std::string(name, quote)];
        e.NameKey = Tag_Text(quote, close, "ObjectNameTextID");
        e.DescKey = Tag_Text(quote, close, "ObjectDescriptionTextID");
        e.Cameo = Tag_Text(quote, close, "BuildIcon");
        p = close;
    }
}

/*
**	Reads the buildables XML files of one mod folder.
*/
void Read_Root(const std::string& root)
{
    char pattern[MAX_PATH];
    snprintf(pattern, sizeof(pattern), "%s\\Data\\XML\\OBJECTS\\UNITS\\*BUILDABLES.XML", root.c_str());
    WIN32_FIND_DATAA found;
    HANDLE find = FindFirstFileA(pattern, &found);
    if (find == INVALID_HANDLE_VALUE) {
        return;
    }
    do {
        char path[MAX_PATH];
        snprintf(path, sizeof(path), "%s\\Data\\XML\\OBJECTS\\UNITS\\%s", root.c_str(), found.cFileName);
        Read_Buildables(path);
    } while (FindNextFileA(find, &found));
    FindClose(find);
}

/*
**	The XML entry the sidebar would show for `ini`: its badge-free variant, else its plain entry; NULL when none.
*/
const XmlEntry* Entry_For(const char* ini)
{
    std::string base = std::string("RA_") + ini;
    std::map<std::string, XmlEntry>::const_iterator it = XmlEntries.find(base + "_0");
    if (it == XmlEntries.end() || it->second.NameKey.empty()) {
        it = XmlEntries.find(base);
    }
    return it == XmlEntries.end() ? NULL : &it->second;
}

/*
**	The type named `ini` in any of the buildable heaps; NULL when none.
*/
TechnoTypeClass const* Type_For(const char* ini)
{
    for (int i = 0; i < InfantryTypes.Count(); i++) {
        if (stricmp(InfantryTypes.Ptr(i)->IniName, ini) == 0) {
            return InfantryTypes.Ptr(i);
        }
    }
    for (int i = 0; i < UnitTypes.Count(); i++) {
        if (stricmp(UnitTypes.Ptr(i)->IniName, ini) == 0) {
            return UnitTypes.Ptr(i);
        }
    }
    for (int i = 0; i < AircraftTypes.Count(); i++) {
        if (stricmp(AircraftTypes.Ptr(i)->IniName, ini) == 0) {
            return AircraftTypes.Ptr(i);
        }
    }
    for (int i = 0; i < VesselTypes.Count(); i++) {
        if (stricmp(VesselTypes.Ptr(i)->IniName, ini) == 0) {
            return VesselTypes.Ptr(i);
        }
    }
    for (int i = 0; i < BuildingTypes.Count(); i++) {
        if (stricmp(BuildingTypes.Ptr(i)->IniName, ini) == 0) {
            return BuildingTypes.Ptr(i);
        }
    }
    return NULL;
}

const int MAX_TECH_LEVEL = 20;

// Reserve tokens a sidebar builds to have units delivered: the encyclopedia lists the unit, or nothing for a mix.
struct Reserve
{
    const char* Token;
    const char* Unit;
};
const Reserve RESERVES[] = {{"TS4PAIR", "TS4TNK"}, {"TSMDIV", NULL}};

// Entries a faction can field in skirmish that its campaign roster doesn't have: the list leaves them out.
struct Unlisted
{
    const char* Ini;
    int Faction;
};
const Unlisted UNLISTED[] = {{"E7", TF_FACTION_SOVIET}};

/*
**	The unit a reserve token delivers, the token's own type for any other type, or NULL for a token of mixed units.
*/
TechnoTypeClass const* Listed_Type(TechnoTypeClass const* type)
{
    for (size_t i = 0; i < sizeof(RESERVES) / sizeof(RESERVES[0]); i++) {
        if (stricmp(type->IniName, RESERVES[i].Token) == 0) {
            return RESERVES[i].Unit != NULL ? Type_For(RESERVES[i].Unit) : NULL;
        }
    }
    return type;
}

/*
**	True when a player of `faction` can have `type`: the faction's bit, a named entry, and a tech level in reach
**	or a construction yard, which an MCV deploys into rather than the sidebar building it.
*/
bool In_Reach(TechnoTypeClass const* type, int faction)
{
    const XmlEntry* entry = Entry_For(type->IniName);
    bool yard = type->What_Am_I() == RTTI_BUILDINGTYPE && ((BuildingTypeClass const*)type)->Is_Construction_Yard();
    return (type->Level <= MAX_TECH_LEVEL || yard) && (TF_Entry_Faction_Mask(type) & faction) && entry != NULL
           && !entry->NameKey.empty();
}

/*
**	True when `faction` has a factory of its own (no other faction's) that builds `what`.
*/
bool Has_Own_Factory(int faction, RTTIType what)
{
    for (int i = 0; i < BuildingTypes.Count(); i++) {
        BuildingTypeClass const* b = BuildingTypes.Ptr(i);
        if (b->ToBuild == what && TF_Entry_Faction_Mask(b) == faction && In_Reach(b, faction)) {
            return true;
        }
    }
    return false;
}

/*
**	True when `type` is listed for `faction`: in reach, not on UNLISTED, and not a shared MCV or a shared factory
**	(yard, war factory, helipad) the faction has its own of.
*/
bool Buildable_By(TechnoTypeClass const* type, int faction)
{
    if (!In_Reach(type, faction)) {
        return false;
    }
    for (size_t i = 0; i < sizeof(UNLISTED) / sizeof(UNLISTED[0]); i++) {
        if (UNLISTED[i].Faction == faction && stricmp(type->IniName, UNLISTED[i].Ini) == 0) {
            return false;
        }
    }
    int mask = TF_Entry_Faction_Mask(type);
    if ((mask & (mask - 1)) == 0) {
        return true;
    }
    if (type->What_Am_I() == RTTI_UNITTYPE && ((UnitTypeClass const*)type)->Is_MCV()) {
        return false;
    }
    RTTIType what = type->What_Am_I() == RTTI_BUILDINGTYPE ? ((BuildingTypeClass const*)type)->ToBuild : RTTI_NONE;
    return what == RTTI_NONE || !Has_Own_Factory(faction, what);
}

/*
**	Names each construction yard no sidebar entry names (a yard isn't built from the sidebar): TEXT_STRUCTURE_<INI>
**	and its _DESC, with the cameo of the MCV of the same faction.
*/
void Name_Bare_Yards(void)
{
    for (int i = 0; i < BuildingTypes.Count(); i++) {
        BuildingTypeClass const* yard = BuildingTypes.Ptr(i);
        if (!yard->Is_Construction_Yard() || Entry_For(yard->IniName) != NULL) {
            continue;
        }
        for (int u = 0; u < UnitTypes.Count(); u++) {
            UnitTypeClass const* mcv = UnitTypes.Ptr(u);
            const XmlEntry* entry = Entry_For(mcv->IniName);
            if (mcv->Is_MCV() && entry != NULL && TF_Entry_Faction_Mask(mcv) == TF_Entry_Faction_Mask(yard)) {
                XmlEntry& named = XmlEntries[std::string("RA_") + yard->IniName];
                named.NameKey = std::string("TEXT_STRUCTURE_") + yard->IniName;
                named.DescKey = named.NameKey + "_DESC";
                named.Cameo = entry->Cameo;
                break;
            }
        }
    }
}

/*
**	Appends one stat line; lines past TF_ENC_STAT_LINES are dropped.
*/
void Add_Line(TFEncStats* out, const wchar_t* label, const wchar_t* format, ...)
{
    if (out->Count >= TF_ENC_STAT_LINES) {
        return;
    }
    wcsncpy(out->Label[out->Count], label, 15);
    out->Label[out->Count][15] = 0;
    out->Key[out->Count][0] = 0;
    out->Suffix[out->Count][0] = 0;
    va_list args;
    va_start(args, format);
    vswprintf(out->Value[out->Count], 48, format, args);
    va_end(args);
    out->Count++;
}

/*
**	A line naming a weapon: its INI name, with TEXT_TF_ENC_WEAPON_<INI in capitals> as the readable name.
*/
void Add_Weapon_Name(TFEncStats* out, const wchar_t* label, WeaponTypeClass const* weapon)
{
    int line = out->Count;
    Add_Line(out, label, L"%hs", weapon->IniName);
    if (out->Count > line) {
        snprintf(out->Key[line], sizeof(out->Key[line]), "TEXT_TF_ENC_WEAPON_%s", weapon->IniName);
        for (char* c = out->Key[line]; *c != 0; c++) {
            *c = (char)toupper((unsigned char)*c);
        }
    }
}

/*
**	A weapon's lines: its name, damage per shot (a beam's damage for beam weapons), range in cells and reload.
*/
void Add_Weapon(TFEncStats* out, const wchar_t* label, WeaponTypeClass const* weapon)
{
    if (weapon == NULL) {
        return;
    }
    Add_Weapon_Name(out, label, weapon);
    int damage = weapon->Attack != 0 ? weapon->Attack : weapon->AmbientDamage;
    if (weapon->Burst > 1) {
        Add_Line(out, L"DAMAGE", L"%d x %d", damage, weapon->Burst);
    } else {
        Add_Line(out, L"DAMAGE", L"%d", damage);
    }
    Add_Line(out, L"RANGE", L"%.2f cells", (int)weapon->Range / 256.0);
    Add_Line(out, L"RELOAD", L"%d", weapon->ROF);
}

#if TF_DEV_BUILD
/*
**	Writes every faction's entries to Documents/CnCRemastered/tf_encyclopedia.log once: their text keys for the
**	manual text, their art name (an Upgrade Centre plug's is the Upgrade Centre's), the body frame the game draws
**	facing south-west, and overlays as art:frame:x:y in classic pixels, seated as the classes' Draw_It seat them.
*/
void Dump_Entries(void);
#endif

} // namespace

void TF_Encyclopedia_Add_Root(const char* folder)
{
    if (std::find(XmlRoots.begin(), XmlRoots.end(), std::string(folder)) == XmlRoots.end()) {
        XmlRoots.push_back(folder);
        if (Loaded) {
            Read_Root(folder);
        }
    }
}

bool TF_Encyclopedia_Load(void)
{
    if (Loaded) {
        return LoadedOk;
    }
    Loaded = true;
    char folder[MAX_PATH];
    if (!Mod_Folder(folder, sizeof(folder))) {
        return false;
    }
    TF_Encyclopedia_Add_Root(folder);
    for (size_t i = 0; i < XmlRoots.size(); i++) {
        Read_Root(XmlRoots[i]);
    }

    // Trap: the type heaps take their sizes once; init.cpp does the same for the game, in this order.
    HouseTypes.Set_Heap(HOUSE_COUNT);
    BuildingTypes.Set_Heap(MAX_BUILDING_TYPES);
    AircraftTypes.Set_Heap(AIRCRAFT_COUNT);
    InfantryTypes.Set_Heap(INFANTRY_COUNT);
    BulletTypes.Set_Heap(BULLET_COUNT);
    AnimTypes.Set_Heap(ANIM_COUNT);
    UnitTypes.Set_Heap(MAX_UNIT_TYPES);
    VesselTypes.Set_Heap(VESSEL_COUNT);
    TemplateTypes.Set_Heap(TEMPLATE_COUNT);
    TerrainTypes.Set_Heap(TERRAIN_COUNT);
    OverlayTypes.Set_Heap(OVERLAY_COUNT);
    SmudgeTypes.Set_Heap(SMUDGE_COUNT);
    HouseTypeClass::Init_Heap();
    BuildingTypeClass::Init_Heap();
    AircraftTypeClass::Init_Heap();
    InfantryTypeClass::Init_Heap();
    BulletTypeClass::Init_Heap();
    AnimTypeClass::Init_Heap();
    UnitTypeClass::Init_Heap();
    VesselTypeClass::Init_Heap();
    TemplateTypeClass::Init_Heap();
    TerrainTypeClass::Init_Heap();
    OverlayTypeClass::Init_Heap();
    SmudgeTypeClass::Init_Heap();

    if (!Load_Ini(RuleINI, folder, "rules.ini")) {
        return false;
    }
    Rule.Process(RuleINI);
    // Trap: a second Rule.Process rebuilds the weapon and warhead heaps under the types' pointers to them.
    if (Load_Ini(AftermathINI, folder, "aftrmath.ini")) {
        Rule.MPlayer(AftermathINI);
        Apply_Overrides(AftermathINI);
    }
    static CCINIClass mplayer;
    if (Load_Ini(mplayer, folder, "mplayer.ini")) {
        Apply_Overrides(mplayer);
    }
    Name_Bare_Yards();
    LoadedOk = true;
#if TF_DEV_BUILD
    Dump_Entries();
#endif
    return true;
}

int TF_Encyclopedia_Entries(int faction, TFEncEntry* out, int max)
{
    std::vector<TechnoTypeClass const*> found;
    std::vector<int> groups;
    for (int i = 0; i < InfantryTypes.Count(); i++) {
        found.push_back(InfantryTypes.Ptr(i));
        groups.push_back(TF_ENC_INFANTRY);
    }
    for (int i = 0; i < UnitTypes.Count(); i++) {
        found.push_back(UnitTypes.Ptr(i));
        groups.push_back(TF_ENC_UNITS);
    }
    for (int i = 0; i < AircraftTypes.Count(); i++) {
        found.push_back(AircraftTypes.Ptr(i));
        groups.push_back(TF_ENC_AIRCRAFT);
    }
    for (int i = 0; i < VesselTypes.Count(); i++) {
        found.push_back(VesselTypes.Ptr(i));
        groups.push_back(TF_ENC_NAVAL);
    }
    for (int i = 0; i < BuildingTypes.Count(); i++) {
        found.push_back(BuildingTypes.Ptr(i));
        groups.push_back(TF_ENC_STRUCTURES);
    }
    std::vector<std::pair<std::pair<int, int>, int>> order;
    for (size_t i = 0; i < found.size(); i++) {
        if (Buildable_By(found[i], faction)) {
            order.push_back(std::make_pair(std::make_pair(groups[i], found[i]->Cost), (int)i));
        }
    }
    std::stable_sort(order.begin(), order.end());
    int count = 0;
    for (size_t i = 0; i < order.size() && count < max; i++) {
        TechnoTypeClass const* type = Listed_Type(found[order[i].second]);
        const XmlEntry* entry = type != NULL ? Entry_For(type->IniName) : NULL;
        if (entry == NULL || entry->NameKey.empty()) {
            continue;
        }
        TFEncEntry& e = out[count++];
        strncpy(e.Ini, type->IniName, sizeof(e.Ini) - 1);
        e.Ini[sizeof(e.Ini) - 1] = 0;
        e.Group = order[i].first.first;
        snprintf(e.NameKey, sizeof(e.NameKey), "%s", entry->NameKey.c_str());
        snprintf(e.DescKey, sizeof(e.DescKey), "%s", entry->DescKey.c_str());
        snprintf(e.Cameo, sizeof(e.Cameo), "%s", entry->Cameo.c_str());
    }
    return count;
}

void TF_Encyclopedia_Stats(const char* ini, TFEncStats* out)
{
    static const wchar_t* const ARMOUR[] = {L"None", L"Wood", L"Light", L"Heavy", L"Concrete"};
    out->Count = 0;
    TechnoTypeClass const* type = Type_For(ini);
    if (type == NULL) {
        return;
    }
    Add_Line(out, L"COST", L"%d", type->Cost);
    Add_Line(out, L"STRENGTH", L"%d", (int)type->MaxStrength);
    int armour = (int)type->Armor;
    Add_Line(out, L"ARMOUR", L"%ls", armour >= 0 && armour < 5 ? ARMOUR[armour] : L"?");
    if (type->What_Am_I() == RTTI_BUILDINGTYPE) {
        BuildingTypeClass const* building = (BuildingTypeClass const*)type;
        int power = building->Power - building->Drain;
        Add_Line(out, L"POWER", power > 0 ? L"+%d" : L"%d", power);
    } else {
        Add_Line(out, L"SPEED", L"%d", ((int)type->MaxSpeed * 100 + 128) / 256);
    }
    Add_Line(out, L"SIGHT", L"%d cells", type->SightRange);
    Add_Weapon(out, L"WEAPON", type->PrimaryWeapon);
    WeaponTypeClass const* second = type->SecondaryWeapon;
    if (second != NULL && second != type->PrimaryWeapon) {
        int line = out->Count;
        Add_Weapon_Name(out, L"2ND WEAPON", second);
        if (out->Count > line) {
            swprintf(out->Suffix[line], 16, L" (%d)", second->Attack != 0 ? second->Attack : second->AmbientDamage);
        }
    }
    if (type->MaxPassengers > 0) {
        Add_Line(out, L"SEATS", L"%d", type->MaxPassengers);
    }
}

int TF_Encyclopedia_Needs(const char* ini, char (*keys)[64], int max)
{
    TechnoTypeClass const* type = Type_For(ini);
    int count = 0;
    for (int i = 0; type != NULL && i < PREREQUISITE_MAX && count < max; i++) {
        int index = type->Prerequisite[i];
        if (index < 0 || index >= BuildingTypes.Count()) {
            continue;
        }
        const XmlEntry* entry = Entry_For(BuildingTypes.Ptr(index)->IniName);
        if (entry != NULL && !entry->NameKey.empty()) {
            snprintf(keys[count++], 64, "%s", entry->NameKey.c_str());
        }
    }
    return count;
}

#if TF_DEV_BUILD
namespace {
void Dump_Entries(void)
{
    const char* home = getenv("USERPROFILE");
    if (home == NULL) {
        return;
    }
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "%s/Documents/CnCRemastered/tf_encyclopedia.log", home);
    FILE* f = fopen(path, "w");
    if (f == NULL) {
        return;
    }
    static const int factions[] = {
        TF_FACTION_ALLIES, TF_FACTION_SOVIET, TF_FACTION_GDI, TF_FACTION_NOD, TF_FACTION_TSGDI};
    static TFEncEntry entries[200];
    for (size_t i = 0; i < sizeof(factions) / sizeof(factions[0]); i++) {
        int count = TF_Encyclopedia_Entries(factions[i], entries, 200);
        for (int e = 0; e < count; e++) {
            TFEncSprite sprite;
            if (!TF_Encyclopedia_Sprite(entries[e].Ini, factions[i], &sprite)) {
                continue;
            }
            char layers[96] = "-";
            for (int l = 0; l < sprite.Layers; l++) {
                size_t used = l == 0 ? 0 : strlen(layers);
                snprintf(layers + used,
                         sizeof(layers) - used,
                         "%s%s:%d:%d:%d",
                         l ? ";" : "",
                         sprite.Layer[l].Art,
                         sprite.Layer[l].Frame,
                         sprite.Layer[l].X,
                         sprite.Layer[l].Y);
            }
            fprintf(f,
                    "%d\t%d\t%s\t%s\t%s\t%s\t%d\t%d\t%s\n",
                    factions[i],
                    entries[e].Group,
                    entries[e].Ini,
                    entries[e].NameKey,
                    entries[e].Cameo,
                    sprite.Art,
                    sprite.Body,
                    sprite.Team,
                    layers);
        }
    }
    fclose(f);
}
} // namespace
#endif

namespace {
const int TDSAM_RAISED = 16;      // the TD SAM's first raised-facing frame (building.cpp)
const int TSPULS_TURRET_Y = 10;   // classic px: the EMP cannon's seat on its dome (building.cpp)
const int ROTOR_LANDED = 4;       // the first landed-blade frame (AircraftClass::Draw_Rotors)
const int ROTOR_LIFT = 2;         // classic px Draw_Rotors lifts the blades by
const int CHINOOK_STRETCH = 8;    // Draw_Rotors' rotor spacing facing north (its _stretch)

/*
**	Appends a layer to `out`; layers past TF_ENC_SPRITE_LAYERS are dropped.
*/
void Add_Layer(TFEncSprite* out, const char* art, int frame, int x, int y)
{
    if (out->Layers < TF_ENC_SPRITE_LAYERS) {
        TFEncLayer& layer = out->Layer[out->Layers++];
        snprintf(layer.Art, sizeof(layer.Art), "%s", art);
        layer.Frame = frame;
        layer.X = x;
        layer.Y = y;
    }
}
} // namespace

bool TF_Encyclopedia_Sprite(const char* ini, int faction, TFEncSprite* out)
{
    TechnoTypeClass const* type = Type_For(ini);
    if (type == NULL) {
        return false;
    }
    memset(out, 0, sizeof(*out));
    snprintf(out->Art, sizeof(out->Art), "%s", type->Graphic_Name());
    out->Body = -1;
    RTTIType rtti = type->What_Am_I();
    out->Group = rtti == RTTI_INFANTRYTYPE ? TF_ENC_INFANTRY
                 : rtti == RTTI_UNITTYPE   ? TF_ENC_UNITS
                 : rtti == RTTI_AIRCRAFTTYPE ? TF_ENC_AIRCRAFT
                 : rtti == RTTI_VESSELTYPE ? TF_ENC_NAVAL
                                           : TF_ENC_STRUCTURES;
    int facing = TechnoClass::BodyShape[Dir_To_32(DIR_SW)];
    bool nod_red = rtti == RTTI_BUILDINGTYPE;
    if (rtti == RTTI_VESSELTYPE) {
        VesselTypeClass const* vessel = (VesselTypeClass const*)type;
        if (vessel->Type != VESSEL_TRANSPORT) {
            out->Body = UnitClass::BodyShape[Dir_To_16(DIR_SW) * 2] >> 1;
        }
        bool cruiser = vessel->Type == VESSEL_CA || vessel->Type == VESSEL_TDCA;
        const char* art = cruiser ? "TURR" : vessel->Type == VESSEL_PT || vessel->Type == VESSEL_TDPT ? "MGUN" : "SSAM";
        for (int t = 0; vessel->IsTurretEquipped && t < (cruiser ? 2 : 1); t++) {
            int x = 0, y = 0;
            vessel->Turret_Adjust(DirType(Dir_To_16(DirType(DIR_SW + (t ? DIR_S : 0))) * 16), x, y);
            Add_Layer(out, art, facing, x, y);
        }
    } else if (rtti == RTTI_BUILDINGTYPE) {
        BuildingTypeClass const* building = (BuildingTypeClass const*)type;
        const char* top = building->Type == STRUCT_TSVULC   ? "TSVULCT"
                          : building->Type == STRUCT_TSROCK ? "TSROCKT"
                          : building->Type == STRUCT_TSCSAM ? "TSCSAMT"
                                                            : NULL;
        if (top != NULL) {
            Add_Layer(out, top, facing, 0, 0);
        } else if (building->IsTurretEquipped) {
            out->Body = facing + (building->Type == STRUCT_TDSAM ? TDSAM_RAISED : 0);
        }
        if (building->Type == STRUCT_TSPULS) {
            Add_Layer(out, "TSPULST", facing, 0, TSPULS_TURRET_Y);
        }
        int plug = TF_Plug_Layer_Frame(building->Type, 0, false);
        if (plug >= 0) {
            snprintf(out->Art, sizeof(out->Art), "TSPLUG");
            Add_Layer(out, "TSPLUGP", plug, 0, 0);
        }
    } else if (rtti == RTTI_AIRCRAFTTYPE && ((AircraftTypeClass const*)type)->IsRotorEquipped) {
        if (((AircraftTypeClass const*)type)->Type == AIRCRAFT_TRANSPORT) {
            out->Body = UnitClass::BodyShape[Dir_To_32(DIR_N)];
            short x = 0, y = 0;
            Move_Point(x, y, DIR_N, CHINOOK_STRETCH);
            Add_Layer(out, "RROTOR", ROTOR_LANDED, x, y - ROTOR_LIFT);
            Move_Point(x, y, DIR_S, CHINOOK_STRETCH * 2);
            Add_Layer(out, "LROTOR", ROTOR_LANDED, x, y - ROTOR_LIFT);
        } else {
            Add_Layer(out, "RROTOR", ROTOR_LANDED, 0, -ROTOR_LIFT);
        }
    } else if (rtti == RTTI_UNITTYPE) {
        UnitTypeClass const* unit = (UnitTypeClass const*)type;
        nod_red = unit->IsToHarvest || unit->Is_MCV();
        out->Body = unit->Type == UNIT_TSLIMP ? 0 : facing;
        int turret_base = 32;
        if (unit->WalkFrames > 1) {
            int wfacing = ((facing * unit->WalkFacings + 16) / 32) % unit->WalkFacings;
            out->Body = unit->FiringFrames > 1 && !unit->IsDeployToFire
                            ? unit->WalkFacings * unit->WalkFrames + wfacing * unit->FiringFrames + 1
                            : wfacing * unit->WalkFrames;
            turret_base = unit->WalkFacings * (unit->WalkFrames + unit->FiringFrames);
        }
        if (unit->IsTurretEquipped && !unit->IsDeployToFire) {
            int x = 0, y = 0;
            unit->Turret_Adjust(DIR_SW, x, y);
            Add_Layer(out, type->Graphic_Name(), facing + turret_base, x, y);
        }
    }
    out->Team = faction == TF_FACTION_ALLIES  ? TF_ENC_TEAM_GREECE
                : faction == TF_FACTION_SOVIET ? TF_ENC_TEAM_USSR
                : faction == TF_FACTION_NOD    ? (nod_red ? TF_ENC_TEAM_TD_BAD_STRUCTURE : TF_ENC_TEAM_TD_BAD_UNIT)
                                               : TF_ENC_TEAM_TD_GOOD;
    return true;
}

const char* TF_Encyclopedia_Root(int index)
{
    return index >= 0 && index < (int)XmlRoots.size() ? XmlRoots[index].c_str() : NULL;
}
