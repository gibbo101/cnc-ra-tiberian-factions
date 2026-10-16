#ifndef TF_ENCYCLOPEDIA_H
#define TF_ENCYCLOPEDIA_H

#include <cstddef>

/*
**	The encyclopedia's data, read live from the mod's rules inside ClientG (docs/encyclopedia.md): each
**	faction's buildable types by group, their stats, and the XML entries naming them and their cameos.
*/
enum TFEncGroup
{
    TF_ENC_INFANTRY,
    TF_ENC_UNITS,
    TF_ENC_AIRCRAFT,
    TF_ENC_NAVAL,
    TF_ENC_STRUCTURES,
    TF_ENC_GROUP_COUNT
};

struct TFEncEntry
{
    char Ini[24];
    int Group;
    char NameKey[64]; // the XML entry's ObjectNameTextID
    char DescKey[64]; // its ObjectDescriptionTextID, the game's one-liner
    char Cameo[64];   // its BuildIcon
};

const int TF_ENC_STAT_LINES = 16;

struct TFEncStats
{
    int Count;
    wchar_t Label[TF_ENC_STAT_LINES][16];
    wchar_t Value[TF_ENC_STAT_LINES][48];
    char Key[TF_ENC_STAT_LINES][48];      // a text key that names the value, when the table has it
    wchar_t Suffix[TF_ENC_STAT_LINES][16]; // shown after the value or its named text
};

const int TF_ENC_SPRITE_LAYERS = 3;

struct TFEncLayer
{
    char Art[24]; // the tileset art name
    int Frame;
    int X, Y; // classic pixels from the body's centre
};

/*
**	How the game draws an entry facing south-west: its art, a body frame (-1 for the default view) and the layers
**	drawn over it, as the classes' Draw_It seat them.
*/
struct TFEncSprite
{
    char Art[24];
    int Body;
    int Group;
    int Team; // a TF_ENC_TEAM_ house colour
    int Layers;
    TFEncLayer Layer[TF_ENC_SPRITE_LAYERS];
};

// House colours as the client draws each faction's campaign (CONFIG.MEG CNCRATEAMCOLORS / CNCTDTEAMCOLORS.XML).
enum TFEncTeam
{
    TF_ENC_TEAM_GREECE,
    TF_ENC_TEAM_USSR,
    TF_ENC_TEAM_TD_GOOD,
    TF_ENC_TEAM_TD_BAD_UNIT,
    TF_ENC_TEAM_TD_BAD_STRUCTURE
};

/*
**	Adds a mod folder whose Data/XML/OBJECTS/UNITS/*BUILDABLES.XML name the types; the DLL's own mod is added
**	on load. An asset pack's folder adds its types' entries.
*/
void TF_Encyclopedia_Add_Root(const char* folder);

/*
**	Builds the type tables and processes the mod's rules.ini, aftrmath.ini and mplayer.ini once, as the game
**	does for a skirmish; false when the rules can't be read. Runs on the launcher's UI thread.
*/
bool TF_Encyclopedia_Load(void);

/*
**	The entries a faction (a TF_FACTION_ bit) can build, by group, cheapest first, a reserve token listed as the
**	unit it delivers; returns how many were written.
*/
int TF_Encyclopedia_Entries(int faction, TFEncEntry* out, int max);

/*
**	An entry's stats as label and value lines, read from the processed rules.
*/
void TF_Encyclopedia_Stats(const char* ini, TFEncStats* out);

/*
**	How the game draws `ini` for `faction` (a TF_FACTION_ bit), a helicopter with its landed blades and the Chinook
**	facing north as it lands (docs/encyclopedia.md); false for an unknown type.
*/
bool TF_Encyclopedia_Sprite(const char* ini, int faction, TFEncSprite* out);

/*
**	The mod folders added, the DLL's own last; NULL past the end.
*/
const char* TF_Encyclopedia_Root(int index);

/*
**	Draws `ini` for `faction` from the game's own sprite art into `rgba` (`width` x `height`, straight alpha),
**	fitted and centred; false when its art can't be read (tf_encyclopedia_art.cpp).
*/
bool TF_Encyclopedia_Render(const char* ini, int faction, unsigned char* rgba, int width, int height);

/*
**	The prerequisites of `ini`: up to `max` XML name keys of the buildings it needs; returns how many.
*/
int TF_Encyclopedia_Needs(const char* ini, char (*keys)[64], int max);

#endif
