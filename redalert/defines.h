//
// Copyright 2020 Electronic Arts Inc.
//
// TiberianDawn.DLL and RedAlert.dll and corresponding source code is free
// software: you can redistribute it and/or modify it under the terms of
// the GNU General Public License as published by the Free Software Foundation,
// either version 3 of the License, or (at your option) any later version.

// TiberianDawn.DLL and RedAlert.dll and corresponding source code is distributed
// in the hope that it will be useful, but with permitted additional restrictions
// under Section 7 of the GPL. See the GNU General Public License in LICENSE.TXT
// distributed with this program. You should have received a copy of the
// GNU General Public License along with permitted additional restrictions
// with this program. If not, see https://github.com/electronicarts/CnC_Remastered_Collection

/* $Header: /CounterStrike/DEFINES.H 4     3/07/97 9:55a Joe_bostic $ */
/***********************************************************************************************
 ***              C O N F I D E N T I A L  ---  W E S T W O O D  S T U D I O S               ***
 ***********************************************************************************************
 *                                                                                             *
 *                 Project Name : Command & Conquer                                            *
 *                                                                                             *
 *                    File Name : DEFINES.H                                                    *
 *                                                                                             *
 *                   Programmer : Joe L. Bostic                                                *
 *                                                                                             *
 *                   Start Date : September 10, 1993                                           *
 *                                                                                             *
 *                  Last Update : September 10, 1993   [JLB]                                   *
 *                                                                                             *
 *---------------------------------------------------------------------------------------------*
 * - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
#ifndef DEFINES_H
#define DEFINES_H

#include "endianness.h"

/**********************************************************************
**	TF dev-build switch.
**	  1 (default) = local development build. The dev cheats (instant-build,
**	      reveal-all) and the A* diagnostic log are compiled in. The cheats
**	      default ON but can be turned off at runtime by creating the file
**	      Documents/CnCRemastered/tf_dev_off.flag (read once at startup, so set
**	      it before launching). See TF_Dev_Cheats().
**	  0   = release / Workshop build. All of the above are compiled out
**	      entirely. package-for-workshop.sh builds with -DTF_DEV_BUILD=0, so
**	      the shipped DLL never contains cheat code. Nothing else to flip.
*/
#ifndef TF_DEV_BUILD
#define TF_DEV_BUILD 1
#endif

/**********************************************************************
**	Language control: define the desired language for this build.
*/
//#define ENGLISH 1
//#define FRENCH 1
//#define GERMAN 1
//#define SPAIN 1	(never used)
//	- Language define is now passed in from the makefile. -

/**********************************************************************
**	Controls the nature of the game and its abilities. Only define
**	one of these values.
**
**	Internal version -- complete with scenario editor.
**	Playtest version -- no editor but does have minimal cheat keys.
**	Release version -- no editor or cheat keys -- all debugging info removed.
*/
//#define	INTERNAL_VERSION
//#define	PLAYTEST_VERSION
#define RELEASE_VERSION

// Enable 640x400 VQ movie capability in WIN32 mode
#define MOVIE640

//#if (GERMAN | FRENCH)
//#define	BOGUSCD
//#endif

#define FIXIT_SCORE_CRASH   // Fixes score screen crash
#define FIXIT_MULTI_SAVE    // Fixes multiplayer save/load
#define FIXIT_NO_COMP_ALLY  // Prevent ally with computer
#define FIXIT_DESTNET       // Fixes -destnet parameter in Win95
#define FIXIT_RANDOM_GAME   // Fixes random seed at start of multiplayer games
#define FIXIT_FORCE_CD      // Forces correct CD load after scenario #1
#define FIXIT_IP_CRASH      // Fixes crash if internet game aborts too quickly
#define FIXIT_IP_STATS      // Fixes so vessels show up in internet stat info
#define FIXIT_NAME_OVERRIDE // Allows changing of unit names
#define FIXIT_RADAR_JAMMED  // Fixes unjamming by merely starting to build a radar facility
#define FIXIT_CAPTURE_BIB   // Fixes so that if fake is captured, you still can't build off of it.
#define FIXIT_BASE_ANNOUNCE // Fixes so player controlled buildings count as base when attacked.
#define FIXIT_APTIVA_MODEM  // Fixes crash with Aptiva modem.
#define FIXIT_FLAG_CHECK    // Disable placing building over a flag.

#define FIXIT_ANTS // Adds Ant Units

#define FIXIT_CSII // Adds Aftermath CounterStrike II units
//	ajw 9/28/98 - Note about FIXIT_CSII. Changes seem to have been made for Aftermath ("Counterstrike II") that: a) were
//	bug fixes that should never be rolled back, b) change the nature of the game, at least in multi-player. This meant
//	that the "Red Alert" executable ( == Counterstrike executable ) could no longer be built. Apparently, at the time,
//	this was justified, as it was believed that no further patches to the RA executable would ever be necessary.
//	Given that Denzil's DVD changes and my WOLAPI integration are essentially a patch, we've got a problem.
//	We've decided to level the field and make sure every who gets or patches to the new version of Red Alert, CS, AM,
//(and 	their DVD equivalent(s)) will have the same executable. So we're assuming that all of the FIXIT_CSII changes are
//	permanent (as, in fact, all prior FIXIT_'s are - makes me wonder why the old non-compiling code has to hang around
//	forever), and fixing the code so that the assumption "this is an Aftermath game" is no longer hard-coded, but can
//	change at runtime. (Which is what should have been done when Aftermath was created.)
//	<This goes for the following three defines as well.>
#define FIXIT_CARRIER        // Adds Aftermath aircraft carrier
#define FIXIT_PHASETRANSPORT // Adds Aftermath cloaking APC
//	ajw - Discovered that engineer changing fields were specifically left out of aftrmath.ini, thus this has no effect.
//	Engineer changes (and other game rule changes) are in mplayer.ini, which was loaded before aftermath-only mplayer
//games.
#define FIXIT_ENGINEER // Adds Engineer rules.ini overrides

//#define	FIXIT_FAST_LOAD			// Enables faster INI loading

// These fixes will cause the game to go out of sync.
#define FIXIT_ENGINEER_CAPTURE // If building allied, will still capture if engineer not allied with building.
//#define	FIXIT_HELI_LANDING	// Fixes so new helicopters land at free helipad
//#define	FIXIT_MINE_PASSABLE	// Fixes units not driving onto mines

/* Turn on these changes for the 1.08 patch */
#define FIXIT_PATCH_108

#ifdef FIXIT_PATCH_108
#define STEVES_LOAD_OVERRIDE   // Allows loading of CONQUER.ENG instead of from mix file.
#define FIXIT_DIFFICULTY       // Fixes no difficulty level for CStrike missions
#define FIXIT_VERSION          // Fixes version playability for 1.04, 1.07 & 1.08
#define FIXIT_MODEM_LOAD_CRASH // Fixes crash after loading a modem game when names are the same
#define FIXIT_PHONELIST_CRASH  // Fixes crash when clicking on an empty phonelist
#endif

//	Denotes changes made for version 3 - reunification of all existing versions and undoing of Aftermath divergence. -
//ajw
#define FIXIT_VERSION_3
#define DVD

// Test to see if partial object drawing is any faster.
#ifdef REMASTER_BUILD
//#define	PARTIAL
#define SORTDRAW
#else
#define PARTIAL
//#define SORTDRAW
#endif

/**********************************************************************
**	If the scenario editor to to be active in this build then uncomment
**	the following #define line.
*/
#ifdef INTERNAL_VERSION
#define SCENARIO_EDITOR
#endif

/**********************************************************************
**	This define enables the full set of cheat keys and special
**	command line options.
*/
#if defined(INTERNAL_VERSION) || defined(PLAYTEST_VERSION)
#define CHEAT_KEYS
#endif

/**********************************************************************
**	If this is defined, the special Virgin limited cheat keys
**	are enabled. This allows the "cheat" parameter and then only
**	allows the ALT-W to win the mission.
*/
#ifdef PLAYTEST_VERSION
#define VIRGIN_CHEAT_KEYS
#endif

/**********************************************************************
**	If this is defined, then the network code will be enabled.
*/
#define NETWORK
#define TIMING_FIX 1

/**********************************************************************
**	If this is defined, the DoList is "mirrored", for memory trasher
** detection.
*/
#ifdef CHEAT_KEYS
//#define MIRROR_QUEUE
#endif

/**********************************************************************
**	This define tells the Version Number class to use the date/time-based
** version numbering system.  If this define is not set, the actual
** major/minor version numbers will be used.
*/
//#define DEV_VERSION
//#define DEV_VER_NAME

/**********************************************************************
** This define enables a special additional foreign-version-number
** after the other version number, for display purposes only.
*/
#if !defined(ENGLISH)
#define FOREIGN_VERSION
#define FOREIGN_VERSION_NUMBER 7
#endif

/**********************************************************************
** This is the multiplier factor to convert low resution coordinates
**	into their actual resolution counterparts.
*/
extern int RESFACTOR;

#define SIDEBAR_WID 80

/**********************************************************************
**	Optional parameter control for special options.
*/

/*
**	Enable the set of limited cheat key options.
*/
#ifdef VIRGIN_CHEAT_KEYS
#define PARM_PLAYTEST 0xF7DDC227 // "PLAYTEST"
#endif

/*
**	Enable the full set of cheat key options.
*/
#ifdef CHEAT_KEYS
#ifndef PARM_PLAYTEST
#define PARM_PLAYTEST 0xF7DDC227 // "PLAYTEST"
#endif
#endif

#define PARM_INSTALL 0xD95C68A2 //	"FROMINSTALL"

/**********************************************************************
**	Defines for verifying free disk space
*/
#define INIT_FREE_DISK_SPACE 8388608
#define SAVE_GAME_DISK_SPACE (INIT_FREE_DISK_SPACE - (1024 * 4096))
//#define	SAVE_GAME_DISK_SPACE		 100000

/**********************************************************************
**	This is the complete list of VQs allowed to be played in the game.
*/
typedef enum VQType
{
    VQ_NONE = -1,
    VQ_AAGUN,
    VQ_MIG,
    VQ_SFROZEN,
    VQ_AIRFIELD,
    VQ_BATTLE,
    VQ_BMAP,
    VQ_BOMBRUN,
    VQ_DPTHCHRG,
    VQ_GRVESTNE,
    VQ_MONTPASS,
    VQ_MTNKFACT,
    VQ_CRONTEST,
    VQ_OILDRUM,
    VQ_ALLYEND,
    VQ_RADRRAID,
    VQ_SHIPYARD,
    VQ_SHORBOMB,
    VQ_SITDUCK,
    VQ_SLNTSRVC,
    VQ_SNOWBASE,
    VQ_EXECUTE,
    VQ_TITLE, // Low res.
    VQ_NUKESTOK,
    VQ_V2ROCKET,
    VQ_SEARCH,
    VQ_BINOC,
    VQ_ELEVATOR,
    VQ_FROZEN,
    VQ_MCV,
    VQ_SHIPSINK,
    VQ_SOVMCV,
    VQ_TRINITY,
    VQ_ALLYMORF,
    VQ_APCESCPE,
    VQ_BRDGTILT,
    VQ_CRONFAIL,
    VQ_STRAFE,
    VQ_DESTROYR,
    VQ_DOUBLE,
    VQ_FLARE,
    VQ_SNSTRAFE,
    VQ_LANDING,
    VQ_ONTHPRWL,
    VQ_OVERRUN,
    VQ_SNOWBOMB,
    VQ_SOVCEMET,
    VQ_TAKE_OFF,
    VQ_TESLA,
    VQ_SOVIET8,
    VQ_SPOTTER,
    VQ_SCENE1,
    VQ_SCENE2,
    VQ_SCENE4,
    VQ_SOVFINAL,
    VQ_ASSESS,
    VQ_SOVIET10,
    VQ_DUD,
    VQ_MCV_LAND,
    VQ_MCVBRDGE,
    VQ_PERISCOP,
    VQ_SHORBOM1,
    VQ_SHORBOM2,
    VQ_SOVBATL,
    VQ_SOVTSTAR,
    VQ_AFTRMATH,
    VQ_SOVIET11,
    VQ_MASASSLT,
    VQ_REDINTRO, // High res
    VQ_SOVIET1,
    VQ_SOVIET2,
    VQ_SOVIET3,
    VQ_SOVIET4,
    VQ_SOVIET5,
    VQ_SOVIET6,
    VQ_SOVIET7,
    VQ_INTRO_MOVIE,
    VQ_AVERTED,
    VQ_COUNTDWN,
    VQ_MOVINGIN,
    VQ_ALLIED10,
    VQ_ALLIED12,
    VQ_ALLIED5,
    VQ_ALLIED6,
    VQ_ALLIED8,
    VQ_TANYA1,
    VQ_TANYA2,
    VQ_ALLY10B,
    VQ_ALLY11,
    VQ_ALLY14,
    VQ_ALLY9,
    VQ_SPY,
    VQ_TOOFAR,
    VQ_SOVIET12,
    VQ_SOVIET13,
    VQ_SOVIET9,
    VQ_BEACHEAD,
    VQ_SOVIET14,
    VQ_SIZZLE,
    VQ_SIZZLE2,
    VQ_ANTEND,
    VQ_ANTINTRO,

    // 2019/11/12 JAS - Added for Retaliation movies
    VQ_RETALIATION_ALLIED1,
    VQ_RETALIATION_ALLIED2,
    VQ_RETALIATION_ALLIED3,
    VQ_RETALIATION_ALLIED4,
    VQ_RETALIATION_ALLIED5,
    VQ_RETALIATION_ALLIED6,
    VQ_RETALIATION_ALLIED7,
    VQ_RETALIATION_ALLIED8,
    VQ_RETALIATION_ALLIED9,
    VQ_RETALIATION_ALLIED10,

    VQ_RETALIATION_SOVIET1,
    VQ_RETALIATION_SOVIET2,
    VQ_RETALIATION_SOVIET3,
    VQ_RETALIATION_SOVIET4,
    VQ_RETALIATION_SOVIET5,
    VQ_RETALIATION_SOVIET6,
    VQ_RETALIATION_SOVIET7,
    VQ_RETALIATION_SOVIET8,
    VQ_RETALIATION_SOVIET9,
    VQ_RETALIATION_SOVIET10,
    VQ_RETALIATION_WINA,
    VQ_RETALIATION_WINS,
    VQ_RETALIATION_ANTS,

    VQ_COUNT,
    VQ_FIRST = 0
} VQType;

/**********************************************************************
**	These enumerations are used to implement RTTI. The target system
**	uses these and thus there can be no more RTTI types than can fit
**	in the exponent of a target value.
*/
typedef enum RTTIType : unsigned char
{
    RTTI_NONE = 0,
    RTTI_AIRCRAFT,
    RTTI_AIRCRAFTTYPE,
    RTTI_ANIM,
    RTTI_ANIMTYPE,
    RTTI_BUILDING,
    RTTI_BUILDINGTYPE,
    RTTI_BULLET,
    RTTI_BULLETTYPE,
    RTTI_CELL,
    RTTI_FACTORY,
    RTTI_HOUSE,
    RTTI_HOUSETYPE,
    RTTI_INFANTRY,
    RTTI_INFANTRYTYPE,
    RTTI_OVERLAY,
    RTTI_OVERLAYTYPE,
    RTTI_SMUDGE,
    RTTI_SMUDGETYPE,
    RTTI_SPECIAL,
    RTTI_TEAM,
    RTTI_TEAMTYPE,
    RTTI_TEMPLATE,
    RTTI_TEMPLATETYPE,
    RTTI_TERRAIN,
    RTTI_TERRAINTYPE,
    RTTI_TRIGGER,
    RTTI_TRIGGERTYPE,
    RTTI_UNIT,
    RTTI_UNITTYPE,
    RTTI_VESSEL,
    RTTI_VESSELTYPE,

    RTTI_COUNT
} RTTIType;

/**********************************************************************
**	These are the difficulty settings of the game.
*/
typedef enum DiffType : unsigned char
{
    DIFF_EASY,
    DIFF_NORMAL,
    DIFF_HARD,

    DIFF_COUNT,
    DIFF_FIRST = 0
} DiffType;

/**********************************************************************
**	This is the size of the speech buffer. This value should be as large
**	as the largest speech sample, plus a few bytes for overhead
**	(16 bytes is sufficient).
*/
#define SPEECH_BUFFER_SIZE 50000L

/**********************************************************************
**	The theater mixfiles are cached into a buffer of this size. Ensure
**	that the size specified is at least as large as the largest
**	theater mixfile data block.
*/
#define THEATER_BUFFER_SIZE 1100000L

/**********************************************************************
**	This is the size of the shape buffer. This buffer is used as a staging
**	buffer for the shape drawing technology. It MUST be as big as the
**	largest shape (uncompressed) that will be drawn. If this value is
**	changed, be sure to update the makefile and rebuild all of the shape
**	data files.
*/
#define SHAPE_BUFFER_SIZE 131072L

/**********************************************************************
**	Filenames of the data files it can create at run time.
*/
#define FAME_FILE_NAME     "HALLFAME.DAT"
#define NET_SAVE_FILE_NAME "SAVEGAME.NET"
#define CONFIG_FILE_NAME   "REDALERT.INI"

/**********************************************************************
**	Map controls. The map is composed of square elements called 'cells'.
**	All larger elements are build upon these.
*/

#define HIGH_COORD_MASK 0x80008000L

// Size of the map in cells.
#define MAP_CELL_W     128
#define MAP_CELL_H     128
#define MAP_CELL_TOTAL (MAP_CELL_W * MAP_CELL_H)

#define REFRESH_EOL     32767 // This number ends a refresh/occupy offset list.
#define REFRESH_SIDEBAR 32766 // This number flags that sidebar needs refreshing.

/****************************************************************************
**	These are custom C&C specific types. The CELL is used for map coordinate
**	with cell resolution. The COORDINATE type is used for map coordinates that
**	have a lepton resolution. CELL is more efficient when indexing into the map
**	and when size is critical. COORDINATE is more efficient when dealing with
**	accuracy and object movement.
*/
typedef unsigned short LEPTON;
typedef union
{
    LEPTON Raw;
    struct
    {
#ifdef __BIG_ENDIAN__
        unsigned char Cell;
        unsigned char Lepton;
#else
        unsigned char Lepton;
        unsigned char Cell;
#endif
    } Sub;
} LEPTON_COMPOSITE;

typedef unsigned COORDINATE;
typedef union
{
    COORDINATE Coord;
    struct
    {
#ifdef __BIG_ENDIAN__
        LEPTON_COMPOSITE Y;
        LEPTON_COMPOSITE X;
#else
        LEPTON_COMPOSITE X;
        LEPTON_COMPOSITE Y;
#endif
    } Sub;
} COORD_COMPOSITE;

typedef signed short CELL;
typedef union
{
    CELL Cell;
    struct
    {
#ifdef __BIG_ENDIAN__
        /*
        **	Unused upper bits will cause problems on a big-endian machine unless they
        **	are deliberately accounted for.
        */
        unsigned short sluff : 2;
        unsigned short Y : 7;
        unsigned short X : 7;
#else
        unsigned short X : 7;
        unsigned short Y : 7;
#endif
    } Sub;
} CELL_COMPOSITE;

typedef int WAYPOINT;

/**********************************************************************
**	This is the target composit information. Notice that with an RTTI_NONE
**	and an index value of 0, the target value returned is identical with
**	TARGET_NONE. This is by design and is necessary.
*/
typedef int TARGET;

/* Safe cast to target type */
#define TARGET_SAFE_CAST(x) (static_cast<TARGET>(reinterpret_cast<intptr_t>((void*)(x))))

#define TARGET_MANTISSA 24 // Bits of value precision.
#define TARGET_EXPONENT 8
#pragma pack(push, 1)
typedef union
{
    TARGET Target;
    struct BITFIELD_STRUCT
    {
#ifdef __BIG_ENDIAN__
        unsigned Exponent : TARGET_EXPONENT;
        unsigned Mantissa : TARGET_MANTISSA;
#else
        unsigned Mantissa : TARGET_MANTISSA;
        unsigned Exponent : TARGET_EXPONENT;
#endif
    } Sub;
} TARGET_COMPOSITE;
#pragma pack(pop)
inline TARGET Build_Target(RTTIType kind, int value)
{
    TARGET_COMPOSITE target;

    target.Target = 0;
    target.Sub.Exponent = kind;
    target.Sub.Mantissa = value;
    return (target.Target);
}

#define TARGET_NONE ((TARGET)0)

/*
**	The map is broken down into regions of this specified dimensions.
*/
#define REGION_WIDTH      4
#define REGION_HEIGHT     4
#define MAP_REGION_WIDTH  (((MAP_CELL_W + (REGION_WIDTH - 1)) / REGION_WIDTH) + 2)
#define MAP_REGION_HEIGHT (((MAP_CELL_H + (REGION_WIDTH - 1)) / REGION_HEIGHT) + 2)
#define MAP_TOTAL_REGIONS (MAP_REGION_WIDTH * MAP_REGION_HEIGHT)

/**********************************************************************
**	This enumerates the various known fear states for infantry units.
**	At these stages, certain events or recovery actions are performed.
*/
typedef enum FearType : unsigned char
{
    FEAR_NONE = 0,     // No fear at all (default state).
    FEAR_ANXIOUS = 10, // Something makes them scared.
    FEAR_SCARED = 100, // Scared enough to take cover.
    FEAR_PANIC = 200,  // Run away! Run away!
    FEAR_MAXIMUM = 255 // Scared to death.
} FearType;

/**********************************************************************
**	When a moving object moves, the Per_Cell_Process function is called
**	at various times during the move. Certain operations must be
**	performed at different stages of the move. This enum specifies the
**	different conditions under which the Per_Cell_Process function is
**	called.
*/
typedef enum PCPType : unsigned char
{
    PCP_ROTATION, // When sitting in place and performing rotations.
    PCP_DURING,   // While moving between two cells.
    PCP_END,      // When the 'center' of a cell is reached during movement.
} PCPType;

/**********************************************************************
**	A base is broken up into several zones. This type enumerates the
**	various zones.
*/
typedef enum ZoneType : char
{
    ZONE_CORE,  // Center of base.
    ZONE_NORTH, // North section.
    ZONE_EAST,  // East section.
    ZONE_SOUTH, // South section.
    ZONE_WEST,  // West section.

    ZONE_COUNT,
    ZONE_FIRST = 0,
    ZONE_NONE = -1
} ZoneType;

/**********************************************************************
**	The map is prescanned to mark of movement zones according to certain
**	movement characteristics. This enum specifies those characteristics
**	and movement zones kept track of.
*/
typedef enum MZoneType : unsigned char
{
    MZONE_NORMAL,    // Normal terrestrial objects (can't crush walls).
    MZONE_CRUSHER,   // Can crush crushable wall types.
    MZONE_DESTROYER, // Can destroy walls.
    MZONE_WATER,     //	Water based objects.
    MZONE_HOVER,     // Hover objects (TS-spike): flood-filled with SPEED_HOVER passability, so one zone spans land AND water. NOTE: grows CellClass::Zones[] — breaks old skirmish saves (accepted, same as any enum addition).

    MZONE_COUNT,
    MZONE_FIRST = 0
} MZoneType;

#define MZONEF_NORMAL    (1 << MZONE_NORMAL)
#define MZONEF_CRUSHER   (1 << MZONE_CRUSHER)
#define MZONEF_DESTROYER (1 << MZONE_DESTROYER)
#define MZONEF_WATER     (1 << MZONE_WATER)
#define MZONEF_HOVER     (1 << MZONE_HOVER)
#define MZONEF_ALL       (MZONEF_NORMAL | MZONEF_CRUSHER | MZONEF_DESTROYER | MZONEF_WATER | MZONEF_HOVER)

/**********************************************************************
**	This records the current state of the computer controlled base. The
**	AI will respond according to this state in order to control
**	production and unit orders.
*/
typedef enum StateType : unsigned char
{
    STATE_BUILDUP,    // Base is building up (defensive buildup stage).
    STATE_BROKE,      // Low on money, need cash or income source.
    STATE_THREATENED, // Enemy units are designated to move close by.
    STATE_ATTACKED,   // Base is under direct attack.
    STATE_ENDGAME     //	Resistance is futile.
} StateType;

/**********************************************************************
**	Urgency rating used to determine what action to perform. The greater
**	the urgency the more likely the corresponding action will be chosen.
**	These values are assigned to each potential desired action the house
**	is to perform.
*/
typedef enum UrgencyType : unsigned char
{
    URGENCY_NONE,     // No action on this matter is needed or desired.
    URGENCY_LOW,      // Minimal attention requested.
    URGENCY_MEDIUM,   //	Normal attention requested.
    URGENCY_HIGH,     // High attention requested.
    URGENCY_CRITICAL, // This matter must be addressed immediately.

    URGENCY_COUNT,
    URGENCY_FIRST = URGENCY_CRITICAL
} UrgencyType;

/**********************************************************************
**	These are the various actions a house may perform. These actions refer
**	to global events that encompass selling and production. Low level house
**	specific actions of choosing targets is handled elsewhere.
*/
typedef enum StrategyType : unsigned char
{
    STRATEGY_BUILD_POWER,    // Power is low, build more.
    STRATEGY_BUILD_DEFENSE,  // Defense needs boosting.
    STRATEGY_BUILD_INCOME,   // Income is low or in jeopardy, raise it.
    STRATEGY_FIRE_SALE,      // Situation hopeless, sell and attack.
    STRATEGY_BUILD_ENGINEER, // An engineer is needed.
    STRATEGY_BUILD_OFFENSE,  // Offensive weapons are needed.
    STRATEGY_RAISE_MONEY,    // Money is low, emergency raise cash.
    STRATEGY_RAISE_POWER,    // Money is low, raise power by selling.
    STRATEGY_LOWER_POWER,    // Too much power, sell power plants.
    STRATEGY_ATTACK,         // General charge the enemy attack logic.

    STRATEGY_COUNT,
    STRATEGY_FIRST = STRATEGY_BUILD_POWER
} StrategyType;

/**********************************************************************
**	These are the various return conditions that production may
**	produce.
*/
typedef enum ProdFailType : unsigned char
{
    PROD_OK,      // Production request successful.
    PROD_LIMIT,   // Failed with production capacity limit reached.
    PROD_ILLEGAL, // Failed because of illegal request.
    PROD_CANT     // Failed because unable to comply (busy or occupied).
} ProdFailType;

/**********************************************************************
**	When performing a landing operation, the aircraft must pass through
**	navigation checkpoints. These enumerations specify the check points.
*/
typedef enum CheckPointType : unsigned char
{
    CHECK_STACK,    // Holding area far away from airfield.
    CHECK_DOWNWIND, // Downwind leg of approach.
    CHECK_CROSSWIND // Crosswind leg of approach.
} CheckPointType;

/**********************************************************************
**	These enumerate the various crate powerups that are available.
*/
typedef enum CrateType : unsigned char
{
    CRATE_MONEY,
    CRATE_UNIT,
    CRATE_PARA_BOMB,
    CRATE_HEAL_BASE,
    CRATE_CLOAK,
    CRATE_EXPLOSION,
    CRATE_NAPALM,
    CRATE_SQUAD,
    CRATE_DARKNESS,
    CRATE_REVEAL,
    CRATE_SONAR,
    CRATE_ARMOR,
    CRATE_SPEED,
    CRATE_FIREPOWER,
    CRATE_ICBM,
    CRATE_TIMEQUAKE,
    CRATE_INVULN,
    CRATE_VORTEX,

    CRATE_COUNT,
    CRATE_FIRST = 0
} CrateType;

/**********************************************************************
**	These are the special weapons that can be used in the game. The common thread
**	with these weapons is that they are controlled through the sidebar
**	mechanism.
*/
typedef enum SpecialWeaponType : char
{
    SPC_NONE = -1,
    SPC_SONAR_PULSE,   // Momentarily reveals submarines.
    SPC_NUCLEAR_BOMB,  //	Tactical nuclear weapon.
    SPC_CHRONOSPHERE,  // Paradox device, for teleportation
    SPC_PARA_BOMB,     // Parachute bomb delivery.
    SPC_PARA_INFANTRY, // Parachute reinforcement delivery.
    SPC_SPY_MISSION,   // Spy plane to take photo recon mission.
    SPC_IRON_CURTAIN,  // Bestow invulnerability on a unit/building
    SPC_GPS,           // give allies free unjammable radar.

    // Tiberian Factions mod superweapons.
    SPC_TD_ION_CANNON, // GDI Ion Cannon strike (ANIM_TD_ION_CANNON, sourced from STRUCT_TDEYE)
    SPC_TD_NUKE,       // Nod Nuclear Strike (BULLET_NUKE_DOWN + ANIM_ATOM_BLAST, sourced from STRUCT_TDTMPL)

    SPC_COUNT,
    SPC_FIRST = 0,
    SPC_ANY = 1
} SpecialWeaponType;
#define SPC_CHRONO2 (SPC_COUNT)

/**********************************************************************
**	The computer AI is categorized by the following enumerations. If
**	the player is controlling a house, then the IQ rating is zero. When
**	the IQ rating is at maximum, then the computer has complete control
**	of the house.
*/
// typedef enum IQType {
//	IQ_DEAD=0x0000,			// Player controlled (computer does nothing).
//	IQ_IDIOT=0x0040,
//	IQ_IMBECILE=0x0080,
//	IQ_MORON=0x00C0,
//	IQ_MENSA=0x0100			// Complete computer control -- look out!
//} IQType;

/**********************************************************************
**	These are the response values when checking to see if an object
**	can enter or exist at a specified location. By examining this
**	return value, appropriate action may be chosen.
**	NOTE: If this changes, update the static array in Find_Path module.
*/
typedef enum MoveType : unsigned char
{
    MOVE_OK,           // No blockage.
    MOVE_CLOAK,        // A cloaked blocking enemy object.
    MOVE_MOVING_BLOCK, // Blocked, but only temporarily.
    MOVE_DESTROYABLE,  // Enemy unit or building is blocking.
    MOVE_TEMP,         // Blocked by friendly unit.
    MOVE_NO,           // Strictly prohibited terrain.

    MOVE_COUNT
} MoveType;

/**********************************************************************
**	These are the themes that the game can play. They must be in exact
**	same order as specified in the CONQUER.TXT file as well as the filename
**	list located in the ThemeClass.
*/
typedef enum ThemeType : char
{
    THEME_QUIET = -3,
    THEME_PICK_ANOTHER = -2,
    THEME_NONE = -1,
    THEME_BIGF,
    THEME_CRUS,
    THEME_FAC1,
    THEME_FAC2,
    THEME_HELL,
    THEME_RUN1,
    THEME_SMSH,
    THEME_TREN,
    THEME_WORK,
    THEME_AWAIT,
    THEME_DENSE_R,
    THEME_FOGGER1A,
    THEME_MUD1A,
    THEME_RADIO2,
    THEME_ROLLOUT,
    THEME_SNAKE,
    THEME_TERMINAT,
    THEME_TWIN,
    THEME_VECTOR1A,

    THEME_MAP,
    THEME_SCORE,
    THEME_INTRO,
    THEME_CREDITS,

    THEME_2ND_HAND,
    THEME_ARAZOID,
    THEME_BACKSTAB,
    THEME_CHAOS2,
    THEME_SHUT_IT,
    THEME_TWINMIX1,
    THEME_UNDER3,
    THEME_VR2,

#ifdef FIXIT_CSII //	checked - ajw 9/28/98
    THEME_BOG,
    THEME_FLOAT_V2,
    THEME_GLOOM,
    THEME_GRNDWIRE,
    THEME_RPT,
    THEME_SEARCH,
    THEME_TRACTION,
    THEME_WASTELND,
#endif

    THEME_COUNT,
    THEME_LAST = (int)THEME_COUNT - 1,
    THEME_FIRST = 0
} ThemeType;

// PG inline ThemeType operator++(ThemeType &, int);

/**********************************************************************
**	This is the various threat scan methods that can be used when looking
**	for targets.
*/
typedef enum ThreatType : unsigned short
{
    THREAT_NORMAL = 0x0000,       // Any distance threat scan?
    THREAT_RANGE = 0x0001,        // Limit scan to weapon range?
    THREAT_AREA = 0x0002,         // Limit scan to general area (twice weapon range)?
    THREAT_AIR = 0x0004,          // Scan for air units?
    THREAT_INFANTRY = 0x0008,     // Scan for infantry units?
    THREAT_VEHICLES = 0x0010,     // Scan for vehicles?
    THREAT_BUILDINGS = 0x0020,    // Scan for buildings?
    THREAT_TIBERIUM = 0x0040,     // Limit scan to Tiberium processing objects?
    THREAT_BOATS = 0x0080,        // Scan for gunboats?
    THREAT_CIVILIANS = 0x0100,    // Consider civilians to be primary target?
    THREAT_CAPTURE = 0x0200,      // Consider capturable buildings only?
    THREAT_FAKES = 0x0400,        // Consider fake buildings a greater target?
    THREAT_POWER = 0x0800,        // Consider power generating facilities a greater target?
    THREAT_FACTORIES = 0x1000,    // Consider factories a greater target?
    THREAT_BASE_DEFENSE = 0x2000, // Consider base defense buildings a greater target?
} ThreatType;
// PG
// inline ThreatType operator |(ThreatType, ThreatType);
// inline ThreatType operator &(ThreatType, ThreatType);
// inline ThreatType operator ~(ThreatType);

inline ThreatType operator|(ThreatType a, ThreatType b)
{
    return static_cast<ThreatType>(static_cast<int>(a) | static_cast<int>(b));
}

inline ThreatType operator&(ThreatType a, ThreatType b)
{
    return static_cast<ThreatType>(static_cast<int>(a) & static_cast<int>(b));
}

inline ThreatType operator~(ThreatType a)
{
    return static_cast<ThreatType>(~static_cast<int>(a));
}

#define THREAT_GROUND (THREAT_VEHICLES | THREAT_BUILDINGS | THREAT_INFANTRY)

/**********************************************************************
**	These return values are used when determine if firing is legal.
**	By examining this value it can be determined what should be done
**	to fix the reason why firing wasn't allowed.
*/
typedef enum FireErrorType : unsigned char
{
    FIRE_OK,       // Weapon is allowed to fire.
    FIRE_AMMO,     // No ammo available to fire?
    FIRE_FACING,   // Not correctly facing target?
    FIRE_REARM,    // It is busy rearming?
    FIRE_ROTATING, // Is it in process of rotating?
    FIRE_ILLEGAL,  // Is it targeting something illegal?
    FIRE_CANT,     // Is this unit one that cannot fire anything?
    FIRE_MOVING,   // Is it moving and not allowed to fire while moving?
    FIRE_RANGE,    // Is the target out of range?
    FIRE_CLOAKED,  // Is the shooter currently cloaked?
    FIRE_BUSY      // Is shooter currently doing something else?
} FireErrorType;

/**********************************************************************
**	If an object can cloak, then it will be in one of these states.
**	For objects that cannot cloak, they will always be in the
**	UNCLOAKED state. This state controls how the object transitions between
**	cloaked and uncloaked conditions.
*/
typedef enum CloakType : unsigned char
{
    UNCLOAKED, // Completely visible (normal state).
    CLOAKING,  // In process of cloaking.
    CLOAKED,   // Completely cloaked (invisible).
    UNCLOAKING // In process of uncloaking.
} CloakType;

/**********************************************************************
**	For units that are cloaking, these value specify the visual character
**	of the object.
*/
typedef enum VisualType : unsigned char
{
    VISUAL_NORMAL,     // Completely visible -- normal.
    VISUAL_INDISTINCT, // The edges shimmer and become indistinct.
    VISUAL_DARKEN,     // Color and texture is muted along with shimmering.
    VISUAL_SHADOWY,    // Body is translucent in addition to shimmering.
    VISUAL_RIPPLE,     // Just a ripple (true predator effect).
    VISUAL_HIDDEN      // Nothing at all is visible.
} VisualType;

/**********************************************************************
**	These missions enumerate the various state machines that can apply to
**	a game object. Only one of these state machines is active at any one
**	time.
*/
typedef enum MissionType : char
{
    MISSION_NONE = -1,

    MISSION_SLEEP,          // Do nothing whatsoever.
    MISSION_ATTACK,         // Attack nearest enemy.
    MISSION_MOVE,           // Guard location or unit.
    MISSION_QMOVE,          // A queue list movement mission.
    MISSION_RETREAT,        // Return home for R & R.
    MISSION_GUARD,          // Stay still.
    MISSION_STICKY,         // Stay still -- never recruit.
    MISSION_ENTER,          // Move into object cooperatively.
    MISSION_CAPTURE,        //	Move into in order to capture.
    MISSION_HARVEST,        // Hunt for and collect nearby Tiberium.
    MISSION_GUARD_AREA,     // Active guard of area.
    MISSION_RETURN,         // Head back to refinery.
    MISSION_STOP,           // Sit still.
    MISSION_AMBUSH,         // Wait until discovered.
    MISSION_HUNT,           // Active search and destroy.
    MISSION_UNLOAD,         // Search for and deliver cargo.
    MISSION_SABOTAGE,       //	Move into in order to destroy.
    MISSION_CONSTRUCTION,   // Building buildup operation.
    MISSION_DECONSTRUCTION, // Building builddown operation.
    MISSION_REPAIR,         // Repair process mission.
    MISSION_RESCUE,
    MISSION_MISSILE,
    MISSION_HARMLESS, // Sit around and don't appear like a threat.

    /*
    **	TF: attack-move (ported from CFE Patch Redux, GPL v3). Pseudo-missions so the
    **	attack-move order can ride the multiplayer event queue; event.cpp converts them
    **	back to MISSION_MOVE plus the per-unit AttackMove flag on receipt.
    */
    MISSION_ATTACKMOVE,
    MISSION_QATTACKMOVE, // attack-move combined with the client's queued-movement toggle

    MISSION_COUNT,
    MISSION_FIRST = 0
} MissionType;

/**********************************************************************
**	These are the enumerated animation sequences that a building may
**	be processing. These serve to control the way that a building
**	appears.
*/
typedef enum BStateType : char
{
    BSTATE_NONE = -1,
    BSTATE_CONSTRUCTION, // Construction animation.
    BSTATE_IDLE,         // Idle animation.
    BSTATE_ACTIVE,       // Animation when building is "doing its thing".
    BSTATE_FULL,         // Special alternate active state.
    BSTATE_AUX1,         // Auxiliary animation.
    BSTATE_AUX2,         // Auxiliary animation.

    BSTATE_COUNT
} BStateType;

/**********************************************************************
**	Whenever a unit is selected and a click occurs over another object
**	or terrain element, there is some action to initiate. This specifies
**	the different types of actions possible. This also controls how the
**	mouse cursor looks when "hovering" over the spot that clicking would
**	occur at.
*/
typedef enum ActionType : unsigned char
{
    ACTION_NONE,          // Either undefined action or "do nothing".
    ACTION_MOVE,          // Can move there or at least try to.
    ACTION_NOMOVE,        // Special case for movable object, but illegal mouse position.
    ACTION_ENTER,         // Special case for infantry->APC or vehicle->Repair facility.
    ACTION_SELF,          // Self select special case.
    ACTION_ATTACK,        // Can attack or fire upon it in some fashion.
    ACTION_HARVEST,       // Special harvest mode.
    ACTION_SELECT,        // Would change selection to specified object.
    ACTION_TOGGLE_SELECT, // Toggles select state of the object.
    ACTION_CAPTURE,       // The unit will try to capture the object.
    ACTION_REPAIR,        // The target object should be repaired.
    ACTION_SELL,          // The target building should be sold back.
    ACTION_SELL_UNIT,     // The target unit should be sold back.
    ACTION_NO_SELL,       // No sell or no repair.
    ACTION_NO_REPAIR,     // No sell or no repair.
    ACTION_SABOTAGE,      // The unit will try to sabotage/destroy the object.
    ACTION_PARA_BOMB,     // Parachute bomb strike.
    ACTION_PARA_INFANTRY, // Parachute infantry strike.
    ACTION_PARA_SABOTEUR, // Parachute saboteur strike.
    ACTION_NUKE_BOMB,     // That target object should be blasted.
    ACTION_AIR_STRIKE,    // That target object should be blasted.
    ACTION_CHRONOSPHERE,  // That target object should be teleported.
    ACTION_CHRONO2,       // Teleport it to the given coordinates now.
    ACTION_IRON_CURTAIN,  // That target object should be invulnerable.
    ACTION_SPY_MISSION,   // Photo recon mission.
    ACTION_GUARD_AREA,    // Guard the area/object clicked on.
    ACTION_HEAL,          // Heal the infantryman clicked on.
    ACTION_DAMAGE,        // Enter and damage building.
    ACTION_GREPAIR,       // Enter and complete repair building.
    ACTION_NO_DEPLOY,
    ACTION_NO_ENTER,
    ACTION_NO_GREPAIR,
    ACTION_TOGGLE_PRIMARY, // Toggle the primary status of the factory.
    ACTION_ATTACKMOVE,     // TF: attack-move (CFE port) -- own action so the click-to-mission path stays clean.

    ACTION_COUNT
} ActionType;

/**********************************************************************
**	When a unit gets damaged, the result of the damage is returned as
**	this type. It can range from no damage taken to complete destruction.
*/
typedef enum ResultType : unsigned char
{
    RESULT_NONE,     // No damage was taken by the target.
    RESULT_LIGHT,    // Some damage was taken, but no state change occurred.
    RESULT_HALF,     // Damaged to below half strength (only returned on transition).
    RESULT_MAJOR,    // Damaged down to 1 hit point.
    RESULT_DESTROYED // Damaged to complete destruction.
} ResultType;

#ifdef OBSOLETE
/**********************************************************************
**	These are the special concrete control defines. They enumerate the
**	sequence order of the concrete icons in the concrete art file.
*/
// DEBUG === convert this to be zero based so that a nulled cell is the
//			 	 default cell.
enum ConcreteEnum
{
    C_NONE = -1,
    C_LEFT = 0,
    C_RIGHT = 1,
    C_RIGHT_UPDOWN = 2,
    C_LEFT_UPDOWN = 3,
    C_UP_RIGHT = 4,
    C_UP_LEFT = 5,
    C_DOWN_RIGHT = 6,
    C_DOWN_LEFT = 7,
    C_RIGHT_DOWN = 8,
    C_LEFT_DOWN = 9,
    C_RIGHT_UP = 10,
    C_LEFT_UP = 11,
    C_UPDOWN_RIGHT = 12,
    C_UPDOWN_LEFT = 13
};
#endif

/**********************************************************************
**	Units that move can move at different speeds. These enumerate the
**	different speeds that a unit can move.
*/
// The trailing comment on each line is the equivalent rules.ini `Speed=` value.
// CRITICAL: rules.ini `Speed=` is a 1..100 PERCENTAGE, scaled back to this 0..255
// MPHType by the engine via _Scale_To_256 (techno.cpp): MaxSpeed = Speed * 256 / 100.
// So to reproduce a TD MPHType in rules.ini, `Speed = round(MPHType * 100 / 256)`
// (i.e. divide by ~2.56). Do NOT use MPHType/2 -- that runs every unit ~28% too fast
// (the original TD-port speed bug, fixed 2026-05-31). The low-value comments below were
// previously wrong (used /2); corrected here.
typedef enum MPHType : unsigned char
{
    MPH_IMMOBILE = 0,
    MPH_VERY_SLOW = 5,      // Speed=2
    MPH_KINDA_SLOW = 6,     // Speed=2
    MPH_SLOW = 8,           // Speed=3
    MPH_SLOW_ISH = 10,      // Speed=4
    MPH_MEDIUM_SLOW = 12,   // Speed=5
    MPH_MEDIUM = 18,        // Speed=7
    MPH_MEDIUM_FAST = 30,   // Speed=12
    MPH_MEDIUM_FASTER = 35, // Speed=14
    MPH_FAST = 40,          // Speed=16
    MPH_ROCKET = 60,        // Speed=23
    MPH_VERY_FAST = 100,    // Speed=39
    MPH_LIGHT_SPEED = 255   // Speed=100
} MPHType;

/**********************************************************************
**	The houses that can be played are listed here. Each has their own
**	personality and strengths.
*/
typedef enum HousesType : char
{
    HOUSE_NONE = -1,
    HOUSE_SPAIN,   //	Gold (unremapped)
    HOUSE_GREECE,  // LtBlue
    HOUSE_USSR,    // Red
    HOUSE_ENGLAND, // Green
    HOUSE_UKRAINE, // Orange
    HOUSE_GERMANY, // Grey
    HOUSE_FRANCE,  // Blue
    HOUSE_TURKEY,  // Brown
    HOUSE_GOOD,    // Global Defense Initiative
    HOUSE_BAD,     // Brotherhood of Nod
    HOUSE_NEUTRAL, // Civilians
    HOUSE_JP,      // Disaster Containment Team
    HOUSE_MULTI1,  // Multi-Player house #1
    HOUSE_MULTI2,  // Multi-Player house #2
    HOUSE_MULTI3,  // Multi-Player house #3
    HOUSE_MULTI4,  // Multi-Player house #4
    HOUSE_MULTI5,  // Multi-Player house #5
    HOUSE_MULTI6,  // Multi-Player house #6
    HOUSE_MULTI7,  // Multi-Player house #7
    HOUSE_MULTI8,  // Multi-Player house #8
    HOUSE_COUNT,
    HOUSE_FIRST = 0
} HousesType;

// inline HousesType operator++(HousesType &, int) {return (HousesType)(int;
inline HousesType operator++(HousesType& ht)
{
    ht = (HousesType)(((int)ht) + 1);
    return ht;
}

// Tiberian Factions mod: GDI (HOUSE_GOOD) and Nod (HOUSE_BAD) detached from
// the Allied / Soviet umbrella so they form their own factions. Vanilla RA
// had HOUSE_GOOD bundled into HOUSEF_ALLIES and HOUSE_BAD into HOUSEF_SOVIET,
// causing the TD houses to silently inherit RA's tech trees.
#define HOUSEF_ALLIES                                                                                                  \
    (HOUSEF_ENGLAND | HOUSEF_SPAIN | HOUSEF_GREECE | HOUSEF_GERMANY | HOUSEF_FRANCE | HOUSEF_TURKEY)
#define HOUSEF_SOVIET (HOUSEF_USSR | HOUSEF_UKRAINE)
#define HOUSEF_GDI    (HOUSEF_GOOD)
#define HOUSEF_NOD    (HOUSEF_BAD)
#define HOUSEF_OTHERS                                                                                                  \
    (HOUSEF_NEUTRAL | HOUSEF_JP | HOUSEF_MULTI1 | HOUSEF_MULTI2 | HOUSEF_MULTI3 | HOUSEF_MULTI4 | HOUSEF_MULTI5        \
     | HOUSEF_MULTI6 | HOUSEF_MULTI7 | HOUSEF_MULTI8)
#define HOUSEF_NONE 0

#define HOUSEF_ENGLAND (1L << HOUSE_ENGLAND)
#define HOUSEF_SPAIN   (1L << HOUSE_SPAIN)
#define HOUSEF_GREECE  (1L << HOUSE_GREECE)
#define HOUSEF_USSR    (1L << HOUSE_USSR)
#define HOUSEF_UKRAINE (1L << HOUSE_UKRAINE)
#define HOUSEF_GERMANY (1L << HOUSE_GERMANY)
#define HOUSEF_FRANCE  (1L << HOUSE_FRANCE)
#define HOUSEF_TURKEY  (1L << HOUSE_TURKEY)
#define HOUSEF_GOOD    (1L << HOUSE_GOOD)
#define HOUSEF_BAD     (1L << HOUSE_BAD)
#define HOUSEF_NEUTRAL (1L << HOUSE_NEUTRAL)
#define HOUSEF_JP      (1L << HOUSE_JP)
#define HOUSEF_MULTI1  (1L << HOUSE_MULTI1)
#define HOUSEF_MULTI2  (1L << HOUSE_MULTI2)
#define HOUSEF_MULTI3  (1L << HOUSE_MULTI3)
#define HOUSEF_MULTI4  (1L << HOUSE_MULTI4)
#define HOUSEF_MULTI5  (1L << HOUSE_MULTI5)
#define HOUSEF_MULTI6  (1L << HOUSE_MULTI6)
#define HOUSEF_MULTI7  (1L << HOUSE_MULTI7)
#define HOUSEF_MULTI8  (1L << HOUSE_MULTI8)

typedef enum PlayerColorType : char
{
    PCOLOR_NONE = -1,
    PCOLOR_GOLD,
    PCOLOR_LTBLUE,
    PCOLOR_RED,
    PCOLOR_GREEN,
    PCOLOR_ORANGE,
#ifdef REMASTER_BUILD
    PCOLOR_BLUE, // This is actually the red scheme used in the dialogs
    PCOLOR_GREY,
#else
    PCOLOR_GREY,
    PCOLOR_BLUE,
#endif
    PCOLOR_BROWN,
    PCOLOR_TYPE,
    PCOLOR_REALLY_BLUE,
    PCOLOR_DIALOG_BLUE,

    PCOLOR_COUNT,
    PCOLOR_FIRST = 0,
    PCOLOR_LAST = PCOLOR_COUNT - 1
} PlayerColorType;

/**********************************************************************
**	This enumerates the remap logic to be applied to an object type when
**	it appears in the construction sidebar.
*/
typedef enum RemapType : unsigned char
{
    REMAP_NONE,
    REMAP_NORMAL,
    REMAP_ALTERNATE
} RemapType;

/**********************************************************************
** These are the types of games that can be played.  GDI & NOD are the
** usual human-vs-computer games; 2-Player games are network or modem,
** with 2 players; multi-player games are network with > 2 players.
*/
typedef enum ScenarioPlayerEnum : char
{
    SCEN_PLAYER_NONE = -1,
    SCEN_PLAYER_SPAIN,
    SCEN_PLAYER_GREECE,
    SCEN_PLAYER_USSR,
    SCEN_PLAYER_JP,
    SCEN_PLAYER_2PLAYER,
    SCEN_PLAYER_MPLAYER,
    SCEN_PLAYER_COUNT,
    SCEN_PLAYER_FIRST = 0
} ScenarioPlayerType;

inline ScenarioPlayerType operator++(ScenarioPlayerType&, int);

/**********************************************************************
** These are the directional parameters for a scenario.
*/
typedef enum ScenarioDirEnum : char
{
    SCEN_DIR_NONE = -1,
    SCEN_DIR_EAST,
    SCEN_DIR_WEST,
    SCEN_DIR_COUNT,
    SCEN_DIR_FIRST = 0
} ScenarioDirType;

inline ScenarioDirType operator++(ScenarioDirType&, int);

/**********************************************************************
** These are the random variations of a scenario.
*/
typedef enum ScenarioVarEnum : char
{
    SCEN_VAR_NONE = -1,
    SCEN_VAR_A,
    SCEN_VAR_B,
    SCEN_VAR_C,
    SCEN_VAR_D,
    SCEN_VAR_COUNT, // comes before the Lose value!
    SCEN_VAR_LOSE,
    SCEN_VAR_FIRST = 0
} ScenarioVarType;

// inline ScenarioVarType operator++(ScenarioVarType &, int);
inline ScenarioVarType operator++(ScenarioVarType& n)
{
    n = (ScenarioVarType)(((int)n) + 1);
    return n;
}

/**********************************************************************
**	The objects to be drawn on the map are grouped into layers. These
**	enumerated values specify those layers. The ground layer is sorted
**	from back to front.
*/
typedef enum LayerType : char
{
    LAYER_NONE = -1,
    LAYER_SURFACE, // Flat on the ground (no sorting or apparent vertical height).
    LAYER_GROUND,  // Touching the ground type object (units & buildings).
    LAYER_AIR,     // Flying above the ground (explosions & flames).
    LAYER_TOP,     // Topmost layer (aircraft & bullets).

    LAYER_COUNT,
    LAYER_FIRST = 0
} LayerType;

// PG inline LayerType operator++(LayerType &, int);
inline LayerType operator++(LayerType& n)
{
    n = (LayerType)(((int)n) + 1);
    return n;
}

/**********************************************************************
**	This enumerates the various bullet types. These types specify bullet's
**	visual and explosive characteristics.
*/
typedef enum BulletType : char
{
    BULLET_NONE = -1,

    BULLET_INVISIBLE,
    BULLET_CANNON,
    BULLET_ACK,
    BULLET_TORPEDO,
    BULLET_FROG,
    BULLET_HEAT_SEEKER,
    BULLET_LASER_GUIDED,
    BULLET_LOBBED,
    BULLET_BOMBLET,
    BULLET_BALLISTIC,
    BULLET_PARACHUTE,
    BULLET_FIREBALL,
    BULLET_DOG,
    BULLET_CATAPULT,
    BULLET_AAMISSILE,
    BULLET_GPS_SATELLITE,
    BULLET_NUKE_UP,
    BULLET_NUKE_DOWN,

    // Tiberian Factions mod bullets ported from TD (tiberiandawn/defines.h
    // BULLET_*). Each maps to a [Name] section in rules.ini.
    BULLET_SSM,   // Surface-to-surface missile — homing, AA + AG capable.
    BULLET_LASER, // Obelisk instant-hit beam (Inviso, light_speed, no rotation).
    BULLET_TDAPDS, // TD Nod Turret 120mm shell (visually mirrors [Cannon]).
    BULLET_TDSPREADFIRE, // TD GDI Guard Tower chain-gun pellet (Inviso, light_speed).
    BULLET_TDPATRIOT, // TD SAM Site Patriot missile (Homing, AA-only, MPH_VERY_FAST).
    BULLET_TDBULLET, // TD small-arms invisible round ("50cal") — Pistol/M16/M60MG; warhead set on the weapon.
    BULLET_TDTOW, // TD Rocket Soldier missile (E3 Dragon/TOW) — Homing, visible 32-frame rotating, WARHEAD_TDAP.
    BULLET_TDFLAME, // TD Flamethrower round (E4) — invisible; the visible effect is the ANIM_FLAME_N muzzle jet.
    BULLET_TDCHEM, // TD Chem Warrior spray (E5) — invisible; the visible effect is the ANIM_CHEM_N muzzle jet. Warhead=TDHE.
    BULLET_TDSSM2, // TD Rocket Launcher missile (MLRS, BULLET_SSM2) — Homing, AA+AG, visible TDDRAGON sprite, WARHEAD_TDHE. = TDSSM but Arm=9/ROT=7.
    BULLET_TDMISSILE, // TD SSM Launcher Honest John (BULLET_HONEST_JOHN) — NON-homing, accurate, visible TDMISSILE sprite (32-frame rotating), WARHEAD_TDFIRE, ANIM_NAPALM3 impact.
    BULLET_TDNAPALM,  // TD A-10 napalm bomblet (BULLET_NAPALM/ClassNapalm verbatim) — Dropping, Arm 24, BOMBLET sprite, WARHEAD_TDFIRE, ANIM_NAPALM2 impact (bullet ImpactAnim; TDFire warhead Explosion=0).

    BULLET_COUNT,
    BULLET_FIRST = 0
} BulletType;

// PG inline BulletType operator++(BulletType &, int);
inline BulletType operator++(BulletType& n)
{
    n = (BulletType)(((int)n) + 1);
    return n;
}

/**********************************************************************
**	All game buildings (structures) are enumerated here. This includes
**	civilian structures as well.
*/
typedef enum StructType : char
{
    STRUCT_NONE = -1,
    STRUCT_ADVANCED_TECH,
    STRUCT_IRON_CURTAIN,
    STRUCT_WEAP,
    STRUCT_CHRONOSPHERE,
    STRUCT_PILLBOX,
    STRUCT_CAMOPILLBOX,
    STRUCT_RADAR,
    STRUCT_GAP,
    STRUCT_TURRET,
    STRUCT_AAGUN,
    STRUCT_FLAME_TURRET,
    STRUCT_CONST, // RA Construction Yard "FACT" — stock-campaign type; skirmish uses the faction yards (AFACT/SFACT) after the W2 split.
    STRUCT_REFINERY,
    STRUCT_STORAGE,
    STRUCT_HELIPAD,
    STRUCT_SAM,
    STRUCT_AIRSTRIP,
    STRUCT_POWER,
    STRUCT_ADVANCED_POWER,
    STRUCT_SOVIET_TECH,
    STRUCT_HOSPITAL,
    STRUCT_BARRACKS,
    STRUCT_TENT,
    STRUCT_KENNEL,
    STRUCT_REPAIR,
    STRUCT_BIO_LAB,
    STRUCT_MISSION,
    STRUCT_SHIP_YARD,
    STRUCT_SUB_PEN,
    STRUCT_MSLO,
    STRUCT_FORWARD_COM,
    STRUCT_TESLA,

    /*
    **	All buildings that are never used as a prerequisite
    **	for construction, follow this point. Typically, this is
    **	limited to civilian structures. Also, the following
    **	buildings are NEVER used in the availability bit field
    **	record that each house maintains. i.e., STRUCTF_????
    **	bit checking will never occur with the following
    **	building types.
    */
    STRUCT_FAKEWEAP,
    STRUCT_FAKECONST,
    STRUCT_FAKE_YARD,
    STRUCT_FAKE_PEN,
    STRUCT_FAKE_RADAR,

    STRUCT_SANDBAG_WALL,
    STRUCT_CYCLONE_WALL,
    STRUCT_BRICK_WALL,
    STRUCT_BARBWIRE_WALL,
    STRUCT_WOOD_WALL,
    STRUCT_FENCE,

    STRUCT_AVMINE,
    STRUCT_APMINE,
    STRUCT_V01,
    STRUCT_V02,
    STRUCT_V03,
    STRUCT_V04,
    STRUCT_V05,
    STRUCT_V06,
    STRUCT_V07,
    STRUCT_V08,
    STRUCT_V09,
    STRUCT_V10,
    STRUCT_V11,
    STRUCT_V12,
    STRUCT_V13,
    STRUCT_V14,
    STRUCT_V15,
    STRUCT_V16,
    STRUCT_V17,
    STRUCT_V18,
    STRUCT_PUMP,
    STRUCT_V20,
    STRUCT_V21,
    STRUCT_V22,
    STRUCT_V23,
    STRUCT_V24,
    STRUCT_V25,
    STRUCT_V26,
    STRUCT_V27,
    STRUCT_V28,
    STRUCT_V29,
    STRUCT_V30,
    STRUCT_V31,
    STRUCT_V32,
    STRUCT_V33,
    STRUCT_V34,
    STRUCT_V35,
    STRUCT_V36,
    STRUCT_V37,
    STRUCT_BARREL,
    STRUCT_BARREL3,

#ifdef FIXIT_ANTS
    STRUCT_QUEEN,
    STRUCT_LARVA1,
    STRUCT_LARVA2,
#endif

    // Tiberian Factions mod buildings — fully separated STRUCT_TDxxxx
    // entries with own BuildingTypeClass instances, own _anims[], own
    // _presets[], own ImageData routing. No Logic= alias inheritance from
    // vanilla RA donors — see docs/building-separation-plan.md for the
    // committed strategic direction (2026-05-21).
    //
    // First vertical slice: STRUCT_TDOBLI (Nod Obelisk of Light).
    // Subsequent buildings (TDATWR, TDGUN, TDPROC, etc.) land per-tier
    // in the building-separation milestones.
    STRUCT_TDOBLI,
    // M2 Tier 1 — pure data ports (power plants, GDI barracks, ore silo).
    STRUCT_TDNUKE,
    STRUCT_TDNUK2,
    STRUCT_TDPYLE,
    STRUCT_TDSILO,
    // M3 Tier 2 — defensive turrets.
    STRUCT_TDGTWR,
    STRUCT_TDATWR,
    STRUCT_TDGUN,
    STRUCT_TDSAM,
    // M4 Tier 3 — production/economy buildings.
    STRUCT_TDHAND,
    STRUCT_TDHPAD,
    STRUCT_TDFIX,
    STRUCT_TDHQ,
    STRUCT_TDWEAP,
    STRUCT_TDAFLD,
    STRUCT_TDFACT, // TD Construction Yard "TDFACT" — classic shared GDI/Nod type; skirmish uses the faction yards (TDGFACT/TDNFACT) after the W2 split.
    STRUCT_TDPROC,

    // M5 Tier 4 — superweapon hosts.
    STRUCT_TDEYE,
    STRUCT_TDTMPL,
    STRUCT_TDBLOSSOM, // TD blossom tree rendered as a building (terrain can't take custom HD art). Neutral, unselectable, invulnerable, seeds Tiberium. bdata.cpp.
    // v4.0 separated faction naval/air production buildings (clone RA art via Image=; faction-logo
    // reskins later). Owner-locked so each yields ONLY its faction roster (the proven TDHPAD pattern,
    // NOT the owner-open shortcut). See docs/navy-4.0-design.md + docs/air-additions-4.0-design.md.
    STRUCT_TDGYARD,   // GDI Naval Yard (clone of SYRD, Owner=GoodGuy, RTTI_VESSELTYPE) — Gunboat + Hovercraft.
    STRUCT_TDNPEN,    // Nod Sub Pen (clone of SPEN, Owner=BadGuy, RTTI_VESSELTYPE) — Submarine + Obelisk Sub + Hovercraft.
    STRUCT_TDGAFLD,   // GDI Airfield (clone of AFLD, Owner=GoodGuy, RTTI_AIRCRAFTTYPE) — A-10.
    STRUCT_TDSTEALTH, // Nod Stealth Generator (reuses GAP sprite; cloaks friendly buildings+units in radius). bdata.cpp / building.cpp driver.
    STRUCT_TDFBNK,    // Nod Flame Bunker (clone of PBOX, Owner=BadGuy) — anti-infantry TDFire flame weapon (range 4). bdata.cpp ClassFlameBunker.
    STRUCT_TSPOWR,    // TS-spike: Tiberian Sun GDI Power Plant (GAPOWR art) — clone of ClassPower (2x2, Power in rules.ini). HD-only art from the TS SHP; POWR donor ImageData/BuildupData.
    STRUCT_TDNFACT,   // Nod Construction Yard — own pipeline-built art (TDNFACT keys); separate type so the BUILDING carries the faction.
    STRUCT_TDGFACT,   // GDI Construction Yard — sibling of STRUCT_TDNFACT. LAST Tiberian-era entry — see STRUCT_TIBERIAN_LAST.

    /*
    **	Red Alert side additions go BELOW the Tiberian-era marker, so they do not inherit
    **	TD construction/place-down audio by enum position.
    */
    STRUCT_SFACT, // Soviet Construction Yard — own pipeline-built art (SFACT keys); separate type so the BUILDING carries the faction.
    STRUCT_AFACT, // Allied Construction Yard — sibling of STRUCT_SFACT.

    STRUCT_COUNT,
    STRUCT_FIRST = 0,

    /*
    **	Last entry of the Tiberian-era block (the TD ports plus the TS spike), which runs
    **	unbroken from STRUCT_TDOBLI. Tiberian-era buildings share TD's construction and
    **	place-down audio; see BuildingTypeClass::Is_Tiberian_Era.
    **
    **	Enum values may only ever be APPENDED (Type numbers are serialized raw and there is
    **	no save-version constant), so anything added later lands past this marker and is NOT
    **	Tiberian-era by default -- which is what an Allied or Soviet addition wants. Move this
    **	marker only when appending another TD/TS entity. Testing the block by IniName prefix
    **	instead would be wrong: RA's own Tesla coil is "TSLA".
    */
    STRUCT_TIBERIAN_LAST = STRUCT_TDGFACT
} StructType;

/*
**	Upper bound on the BuildingTypes heap (vanilla enum entries + mod heap
**	slots reserved by `BuildingTypes.Set_Heap()` in init.cpp). Used to size
**	per-Type counter arrays on HouseClass so mod-defined IniNames index
**	safely past STRUCT_COUNT. Keep in sync with init.cpp's Set_Heap call.
*/
#define MAX_BUILDING_TYPES (STRUCT_COUNT + 50)

/*
**  Same as MAX_BUILDING_TYPES but for UnitTypes — gives [NewUnits] entries
**  in rules.ini room past UNIT_COUNT. Without this, UnitTypes.Set_Heap()
**  sizes the heap to exactly UNIT_COUNT and Alloc() for a mod entry silently
**  fails (heap full), making `As_Pointer("TDMCV")` return NULL despite
**  [NewUnits] parsing the section. Headroom of 50 matches the building side.
*/
#define MAX_UNIT_TYPES (UNIT_COUNT + 50)

/*
**	Maximum number of comma-separated entries in a Prerequisite= line.
**	Vanilla never exceeds 2; 4 is comfortable headroom for mods.
*/
#define PREREQUISITE_MAX 4

// PG inline StructType operator++(StructType &, int);
inline StructType operator++(StructType& n)
{
    n = (StructType)(((int)n) + 1);
    return n;
}

#define STRUCTF_NONE           0L
#define STRUCTF_ADVANCED_TECH  (1L << STRUCT_ADVANCED_TECH)
#define STRUCTF_IRON_CURTAIN   (1L << STRUCT_IRON_CURTAIN)
#define STRUCTF_WEAP           (1L << STRUCT_WEAP)
#define STRUCTF_CHRONOSPHERE   (1L << STRUCT_CHRONOSPHERE)
#define STRUCTF_PILLBOX        (1L << STRUCT_PILLBOX)
#define STRUCTF_CAMOPILLBOX    (1L << STRUCT_CAMOPILLBOX)
#define STRUCTF_RADAR          (1L << STRUCT_RADAR)
#define STRUCTF_GAP            (1L << STRUCT_GAP)
#define STRUCTF_TURRET         (1L << STRUCT_TURRET)
#define STRUCTF_AAGUN          (1L << STRUCT_AAGUN)
#define STRUCTF_FLAME_TURRET   (1L << STRUCT_FLAME_TURRET)
#define STRUCTF_CONST          (1L << STRUCT_CONST)
#define STRUCTF_REFINERY       (1L << STRUCT_REFINERY)
#define STRUCTF_STORAGE        (1L << STRUCT_STORAGE)
#define STRUCTF_HELIPAD        (1L << STRUCT_HELIPAD)
#define STRUCTF_SAM            (1L << STRUCT_SAM)
#define STRUCTF_AIRSTRIP       (1L << STRUCT_AIRSTRIP)
#define STRUCTF_POWER          (1L << STRUCT_POWER)
#define STRUCTF_ADVANCED_POWER (1L << STRUCT_ADVANCED_POWER)
#define STRUCTF_SOVIET_TECH    (1L << STRUCT_SOVIET_TECH)
#define STRUCTF_HOSPITAL       (1L << STRUCT_HOSPITAL)
#define STRUCTF_BARRACKS       (1L << STRUCT_BARRACKS)
#define STRUCTF_TENT           (1L << STRUCT_TENT)
#define STRUCTF_KENNEL         (1L << STRUCT_KENNEL)
#define STRUCTF_REPAIR         (1L << STRUCT_REPAIR)
#define STRUCTF_BIO_LAB        (1L << STRUCT_BIO_LAB)
#define STRUCTF_MISSION        (1L << STRUCT_MISSION)
#define STRUCTF_SHIP_YARD      (1L << STRUCT_SHIP_YARD)
#define STRUCTF_SUB_PEN        (1L << STRUCT_SUB_PEN)
#define STRUCTF_MSLO           (1L << STRUCT_MSLO)
#define STRUCTF_FAKECONST      (1L << STRUCT_FAKECONST)
#define STRUCTF_FAKEWEAP       (1L << STRUCT_FAKEWEAP)

/**********************************************************************
**	The overlays are enumerated here. An overlay functions similarly to
**	a transparent icon. It is placed over the terrain but usually falls
**	"under" buildings, trees, and units.
*/
typedef enum OverlayType : char
{
    OVERLAY_NONE = -1,
    OVERLAY_SANDBAG_WALL,  // Piled sandbags.
    OVERLAY_CYCLONE_WALL,  // Chain-link fence.
    OVERLAY_BRICK_WALL,    // Solid concrete wall.
    OVERLAY_BARBWIRE_WALL, // Barbed-wire wall.
    OVERLAY_WOOD_WALL,     // Wooden fence.
    OVERLAY_GOLD1,
    OVERLAY_GOLD2,
    OVERLAY_GOLD3,
    OVERLAY_GOLD4,
    OVERLAY_GEMS1,
    OVERLAY_GEMS2,
    OVERLAY_GEMS3,
    OVERLAY_GEMS4,
    // Tiberian Factions -- TD-style harvestable Tiberium, coexisting with Ore/Gems.
    // MUST stay immediately after OVERLAY_GEMS4 so the launcher's contiguous
    // "is this a resource cell" range check (dllinterface.cpp ~7126,
    // GOLD1..<last resource>) keeps covering it. Single visual type; the 12
    // density frames live in the SHP and are indexed by OverlayData (like Gold).
    // Static by default (NOT added to Can_Tiberium_Grow/Spread). Value = Ore.
    OVERLAY_TIB01,
    OVERLAY_V12,         // Haystacks
    OVERLAY_V13,         // Haystack
    OVERLAY_V14,         // Wheat field
    OVERLAY_V15,         // Fallow field
    OVERLAY_V16,         //	Corn field
    OVERLAY_V17,         // Celery field
    OVERLAY_V18,         // Potato field
    OVERLAY_FLAG_SPOT,   // Flag start location.
    OVERLAY_WOOD_CRATE,  // Wooden goodie crate.
    OVERLAY_STEEL_CRATE, //	Steel goodie crate.
    OVERLAY_FENCE,       // New fangled fence.
    OVERLAY_WATER_CRATE, //	Water goodie crate.

    OVERLAY_COUNT,
    OVERLAY_FIRST = 0
} OverlayType;

// PG inline OverlayType operator++(OverlayType &, int);

/**********************************************************************
**	This specifies the infantry in the game. The "E" designation is
**	similar to the army classification of enlisted soldiers.
*/
typedef enum InfantryType : char
{
    INFANTRY_NONE = -1,
    INFANTRY_E1,        // Mini-gun armed.
    INFANTRY_E2,        // Grenade thrower.
    INFANTRY_E3,        // Rocket launcher.
    INFANTRY_E4,        // Flame thrower equipped.
    INFANTRY_RENOVATOR, // Engineer.
    INFANTRY_TANYA,     // Saboteur.
    INFANTRY_SPY,       // Spy.
    INFANTRY_THIEF,     // Thief.
    INFANTRY_MEDIC,     // Field Medic.
    INFANTRY_GENERAL,   // Field Marshal.
    INFANTRY_DOG,       // Soviet attack dog

    INFANTRY_C1,       // Civilian
    INFANTRY_C2,       // Civilian
    INFANTRY_C3,       // Civilian
    INFANTRY_C4,       // Civilian
    INFANTRY_C5,       // Civilian
    INFANTRY_C6,       // Civilian
    INFANTRY_C7,       // Civilian
    INFANTRY_C8,       // Civilian
    INFANTRY_C9,       // Civilian
    INFANTRY_C10,      // Nikumba
    INFANTRY_EINSTEIN, // Einstein
    INFANTRY_DELPHI,   // Agent "Delphi"
    INFANTRY_CHAN,     // Dr. Chan

#ifdef FIXIT_CSII   //	checked - ajw 9/28/98                                                                           \
                    // CounterStrike II only!
    INFANTRY_SHOCK, // Shock Trooper
    INFANTRY_MECHANIC,
#endif

    // Tiberian Factions mod infantry ported from TD (tiberiandawn/idata.cpp).
    INFANTRY_TDE1, // TD Minigunner (E1) — basic rifleman, GDI+Nod, fires TDM16.
    INFANTRY_TDE2, // TD Grenadier (E2) — GDI-only, lobs TDGrenade (visible arc).
    INFANTRY_TDE3, // TD Rocket Soldier (E3) — GDI+Nod, fires TDDragon homing missile (anti-armor/air).
    INFANTRY_TDE4, // TD Flamethrower (E4) — Nod-only, fires TDFlame (invisible round + directional flame jet).
    INFANTRY_TDE5, // TD Chem Warrior (E5) — Nod-only, fires TDChem (invisible round + directional chem-spray jet).
    INFANTRY_TDE6,   // TD Engineer (E6) — no weapon; captures buildings (Infiltrate). GDI+Nod, barracks-level.
    INFANTRY_TDRMBO, // TD Commando (RMBO) — 125-dmg sniper (one-shots infantry) + C4 building-destroy. GDI+Nod, tech-center gated.

    INFANTRY_COUNT,
    INFANTRY_FIRST = 0
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
    ,
    INFANTRY_RA_COUNT = INFANTRY_SHOCK
#endif
} InfantryType;

#define INFANTRYF_DOG (1L << INFANTRY_DOG)

// PG inline InfantryType operator++(InfantryType &, int);

/**********************************************************************
**	The game units are enumerated here. These include not only traditional
**	vehicles, but also hovercraft and gunboats.
*/
typedef enum UnitType : char
{
    UNIT_NONE = -1,
    UNIT_HTANK,       // Mammoth tank.
    UNIT_MTANK,       // Heavy tank.
    UNIT_MTANK2,      // Medium tank.
    UNIT_LTANK,       // Light tank ('Bradly').
    UNIT_APC,         // APC.
    UNIT_MINELAYER,   // Mine-laying vehicle.
    UNIT_JEEP,        // 4x4 jeep replacement.
    UNIT_HARVESTER,   // Resource gathering vehicle.
    UNIT_ARTY,        // Artillery unit.
    UNIT_MRJ,         // Mobile Radar Jammer.
    UNIT_MGG,         // Mobile Gap Generator
    UNIT_MCV,         // RA MCV "MCV" (deploys to STRUCT_CONST) — stock-campaign type; skirmish uses the faction MCVs (AMCV/SMCV) after the W2 split.
    UNIT_V2_LAUNCHER, // V2 rocket launcher.
    UNIT_TRUCK,       // Convoy truck

#ifdef FIXIT_ANTS
    UNIT_ANT1, // Warrior ant.
    UNIT_ANT2, // Warrior ant.
    UNIT_ANT3, // Warrior ant.
#endif

#ifdef FIXIT_CSII           //	checked - ajw 9/28/98                                                                   \
                            // CS II ONLY!
    UNIT_CHRONOTANK,        // Chrono-shifting tank
    UNIT_TESLATANK,         // Tesla-equipped tank
    UNIT_MAD,               // Timequake tank
    UNIT_DEMOTRUCK,         // Jihad truck
#ifdef FIXIT_PHASETRANSPORT //	checked - ajw 9/28/98
    UNIT_PHASE,             // cloaking APC for special missions
#endif
#endif

    // Tiberian Factions mod — fully-separated TD-source unit ports.
    UNIT_TDMCV,             // TD MCV "TDMCV" (deploys to STRUCT_TDFACT) — classic shared GDI/Nod type; skirmish uses the faction MCVs (TDGMCV/TDNMCV) after the W2 split.
    UNIT_TDHARV,            // TD Tiberium Harvester (docks at STRUCT_TDPROC).
    UNIT_TDMTNK,            // TD Medium Tank (MTNK) — GDI-only, turret, fires TD105mm. udata.cpp:264.
    UNIT_TDLTNK,            // TD Light Tank (LTNK) — Nod-only, turret, fires TD75mm. udata.cpp:211.
    UNIT_TDHTNK,            // TD Mammoth Tank (HTNK) — GDI-only, dual weapon (TD120mm + TDTusk AA), gigundo. udata.cpp:317.
    UNIT_TDFTNK,            // TD Flame Tank (FTNK) — Nod-only, turret-less, fires TDFlameTongue (directional flame jet). udata.cpp UnitFTank.
    UNIT_TDBIKE,            // TD Recon Bike (BIKE) — Nod-only, wheeled, turret-less, fires TDDragon (reuses E3's homing rocket). udata.cpp:797.
    UNIT_TDJEEP,            // TD Hum-vee (JEEP) — GDI-only, wheeled, MG turret, fires TDM60mg. udata.cpp:691.
    UNIT_TDBGGY,            // TD Nod Buggy (BGGY) — Nod-only, wheeled, MG turret, fires TDM60mg. udata.cpp:744.
    UNIT_TDAPC,             // TD APC (APC) — GDI-only (faction-canon; TD src bits permissive), tracked transport, no turret, fires TDM60mg, carries 5. udata.cpp:907.
    UNIT_TDSTNK,            // TD Stealth Tank (STNK) — Nod-only, CLOAKABLE (RA's inherited cloak system), invisible-to-radar, turret-less, fires TDStnkDragon (2-shot). udata.cpp UnitSTank.
    UNIT_TDMLRS,            // TD Rocket Launcher (MLRS, "Rocket Launcher") — GDI-only (EYE-gated), turret + lock-while-moving, 2-shot, fires TDMlrsRocket (BULLET_TDSSM2, range 6). Uses the MSAM sprite (TD cross-wiring). udata.cpp:854.
    UNIT_TDMSAM,            // TD SSM Launcher (MSAM, "S.S.M. Launcher") — Nod-only, Temple-gated, turret + lock-while-moving, fires TDHonestJohn (BULLET_TDMISSILE, non-homing, range 10, fire warhead). Uses the MLRS sprite (TD cross-wiring). udata.cpp:477.
    UNIT_TDARTY,            // TD Artillery (ARTY, "Nod Artillery") — Nod-only, no prereq (build level 6), turret-less (body aims, slow ROT 2), fires TD155mm (BULLET_TDHESHELL arcing, dmg 150). udata.cpp UnitArty.
    UNIT_TDVICE,            // TD Visceroid (VICE) — tiberium creature, NOT buildable; spawns when infantry die in tiberium. Tracked, turret-less, squashes infantry, constant anim, WEAPON_TDCHEM spray, ARMOR_WOOD, STR 150, MISSION_HUNT. HEALS on tiberium. udata.cpp UnitVisceroid.
    UNIT_TSHVR,             // TS-spike: Tiberian Sun Hover MLRS (HVR) — GDI, turreted missile rack, fires TSHoverMissile (TDSSM AA+AG chain). Art = voxel-rendered HD tileset (tools/ts_extract.py + vxl_render.py pipeline); no classic SHP (2TNK donor ImageData).
    UNIT_SMCV,              // Soviet MCV (deploys to STRUCT_SFACT) — own pipeline-built art (SMCV keys); separate type so the UNIT carries the faction.
    UNIT_TDNMCV,            // Nod MCV (deploys to STRUCT_TDNFACT) — own pipeline-built art (TDNMCV keys).
    UNIT_TDGMCV,            // GDI MCV (deploys to STRUCT_TDGFACT) — sibling of UNIT_TDNMCV.
    UNIT_AMCV,              // Allied MCV (deploys to STRUCT_AFACT) — sibling of UNIT_SMCV.

    UNIT_COUNT,
    UNIT_FIRST = 0
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
    ,
    UNIT_RA_COUNT = UNIT_CHRONOTANK
#endif
} UnitType;

// PG inline UnitType operator++(UnitType &, int);

#define UNITF_HTANK     (1L << UNIT_HTANK)
#define UNITF_MTANK     (1L << UNIT_MTANK)
#define UNITF_MTANK2    (1L << UNIT_MTANK2)
#define UNITF_LTANK     (1L << UNIT_LTANK)
#define UNITF_STANK     (1L << UNIT_STANK)
#define UNITF_APC       (1L << UNIT_APC)
#define UNITF_MLRS      (1L << UNIT_MLRS)
#define UNITF_JEEP      (1L << UNIT_JEEP)
#define UNITF_HARVESTER (1L << UNIT_HARVESTER)
#define UNITF_ARTY      (1L << UNIT_ARTY)
#define UNITF_MCV       (1L << UNIT_MCV)

/**********************************************************************
**	The naval vessels are enumerated below.
*/
typedef enum VesselType : char
{
    VESSEL_NONE = -1,

    VESSEL_SS,         // Submarine
    VESSEL_DD,         // Medium weapon patrol craft
    VESSEL_CA,         // Heavy weapon patrol craft
    VESSEL_TRANSPORT,  // Unit transporter
    VESSEL_PT,         // Light weapon patrol craft
#ifdef FIXIT_CSII      //	checked - ajw 9/28/98                                                                        \
                       // CS II ONLY
    VESSEL_MISSILESUB, // Missile-equipped submarine
#endif
#ifdef FIXIT_CARRIER //	checked - ajw 9/28/98
    VESSEL_CARRIER,
#endif
    VESSEL_TDGUNBOAT, // v4.0: TD Gunboat (GDI) — own vessel type, TD art (TDBOAT), TD missile (TDTomahawk) + DepthCharge ASW + Sensors. First TD vessel port. vdata.cpp VesselTdGunBoat.
    VESSEL_TDLST,     // v4.0: TD Hovercraft transport (GDI+Nod shared) — own vessel type, TD art (TDLST), 5 passengers. Modeled on VESSEL_TRANSPORT. vdata.cpp VesselTdLST.
    VESSEL_TDOBLISUB, // v4.0: Nod Obelisk Attack Sub — own vessel type, cloakable SS-like hull + the TD Obelisk laser. Temple-gated. vdata.cpp VesselTdObeliskSub.
    VESSEL_TDNSUB,    // v4.0: Nod Submarine — own vessel type (clone of SS; NOT the SS owner-opened), own art copy, Owner=BadGuy. vdata.cpp VesselTdNodSub.
    // v4.0 GDI surface fleet (turret-test): fully-separated CLONES of the three Allied ships, Owner=GoodGuy,
    // built from the GDI Naval Yard (TDGYARD via the syrd-> remap). They keep IsTurretEquipped=true so they
    // render with the native spinning turret (MGUN/SSAM/TURR drawn by name via the launcher — global, not
    // part of the hull ZIP) — this is the path to a GDI warship whose turret spins + fires from the barrel.
    // Own copied hull art (TDPT/TDDD/TDCA ZIPs). See docs/naval-art-3d-pipeline-handover.md.
    VESSEL_TDPT,      // GDI gunboat — clone of RA PT (MGUN turret). vdata.cpp VesselTdPT.
    VESSEL_TDDD,      // GDI destroyer — clone of RA DD (SSAM turret). vdata.cpp VesselTdDD.
    VESSEL_TDCA,      // GDI cruiser — clone of RA CA (TURR turret). vdata.cpp VesselTdCA.
    VESSEL_TDMSUB,    // v4.0: Nod Missile Sub — clone of Soviet MSUB (SubSCUD shore bombardment), Owner=BadGuy, Temple-gated. vdata.cpp VesselTdMSub.

    VESSEL_COUNT,
    VESSEL_FIRST = 0
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
    ,
    VESSEL_RA_COUNT = VESSEL_MISSILESUB
#endif
} VesselType;

// inline VesselType operator++(VesselType &, int);

#define VESSELF_SS        (1L << VESSEL_SS)
#define VESSELF_DD        (1L << VESSEL_DD)
#define VESSELF_CA        (1L << VESSEL_CA)
#define VESSELF_TRANSPORT (1L << VESSEL_TRANSPORT)
#define VESSELF_PT        (1L << VESSEL_PT)

/**********************************************************************
**	The various aircraft types are enumerated here. These include helicopters
**	as well as traditional aircraft.
*/
typedef enum AircraftType : char
{
    AIRCRAFT_TRANSPORT, // Transport helicopter.
    AIRCRAFT_BADGER,    // Badger bomber.
    AIRCRAFT_U2,        // Photo recon plane.
    AIRCRAFT_MIG,       // Mig attack plane.
    AIRCRAFT_YAK,       // Yak attack plane.
    AIRCRAFT_LONGBOW,   // Apache gunship.
    AIRCRAFT_HIND,      // Soviet attach helicopter.
    AIRCRAFT_TDCARGO,   // TD C-17 cargo plane (Nod airstrip vehicle delivery).
    AIRCRAFT_TDAPACHE,  // TD Apache attack helicopter (HELI) — Nod, single rotor, chain gun (TDApacheGun), Ammo 15, helipad-built. aadata.cpp AttackHeli.
    AIRCRAFT_TDORCA,    // TD Orca (ORCA) — GDI, NO rotor (VTOL), DRAGON missiles (TDStnkDragon), Ammo 6, helipad-built. aadata.cpp OrcaHeli.
    AIRCRAFT_TDA10,     // v4.0: TD A-10 Warthog — GDI, fixed-wing napalm strafer, Ammo 3, airfield-built (AFLD owner-opened). DTA-style divergence (TD's A-10 was a support power). aadata.cpp TdA10.
    AIRCRAFT_TDPARADROP, // v4.0: targetable support-drop C-17 (Nod Paratroopers delivery). Twin of TDCARGO but attackable + Passengers=5; reuses the TDC17 sprite via RA_UNITS.XML alias. aadata.cpp TDParaDropPlane.

    AIRCRAFT_COUNT,
    AIRCRAFT_NONE = -1,
    AIRCRAFT_FIRST = 0
} AircraftType;

#define AIRCRAFTF_TRANSPORT (1L << AIRCRAFT_TRANSPORT)
#define AIRCRAFTF_BADGER    (1L << AIRCRAFT_BADGER)
#define AIRCRAFTF_U2        (1L << AIRCRAFT_U2)
#define AIRCRAFTF_MIG       (1L << AIRCRAFT_MIG)
#define AIRCRAFTF_YAK       (1L << AIRCRAFT_YAK)
#define AIRCRAFTF_LONGBOW   (1L << AIRCRAFT_LONGBOW)
#define AIRCRAFTF_HIND      (1L << AIRCRAFT_HIND)
#define AIRCRAFTF_TDCARGO   (1L << AIRCRAFT_TDCARGO)
#define AIRCRAFTF_TDA10     (1L << AIRCRAFT_TDA10)

// PG inline AircraftType operator++(AircraftType &, int);

/**********************************************************************
**	The game templates are enumerated here. These are the underlying
**	terrain art. This includes everything from water to cliffs. If the
**	terrain is broken up into icons, is not transparent, and is drawn
**	as the bottom most layer, then it is a template.
*/
typedef enum TemplateType : unsigned short
{
    TEMPLATE_CLEAR1,
    TEMPLATE_WATER, // This must be the first non-clear template.
    TEMPLATE_WATER2,
    TEMPLATE_SHORE01,
    TEMPLATE_SHORE02,
    TEMPLATE_SHORE03,
    TEMPLATE_SHORE04,
    TEMPLATE_SHORE05,
    TEMPLATE_SHORE06,
    TEMPLATE_SHORE07,
    TEMPLATE_SHORE08,
    TEMPLATE_SHORE09,
    TEMPLATE_SHORE10,
    TEMPLATE_SHORE11,
    TEMPLATE_SHORE12,
    TEMPLATE_SHORE13,
    TEMPLATE_SHORE14,
    TEMPLATE_SHORE15,
    TEMPLATE_SHORE16,
    TEMPLATE_SHORE17,
    TEMPLATE_SHORE18,
    TEMPLATE_SHORE19,
    TEMPLATE_SHORE20,
    TEMPLATE_SHORE21,
    TEMPLATE_SHORE22,
    TEMPLATE_SHORE23,
    TEMPLATE_SHORE24,
    TEMPLATE_SHORE25,
    TEMPLATE_SHORE26,
    TEMPLATE_SHORE27,
    TEMPLATE_SHORE28,
    TEMPLATE_SHORE29,
    TEMPLATE_SHORE30,
    TEMPLATE_SHORE31,
    TEMPLATE_SHORE32,
    TEMPLATE_SHORE33,
    TEMPLATE_SHORE34,
    TEMPLATE_SHORE35,
    TEMPLATE_SHORE36,
    TEMPLATE_SHORE37,
    TEMPLATE_SHORE38,
    TEMPLATE_SHORE39,
    TEMPLATE_SHORE40,
    TEMPLATE_SHORE41,
    TEMPLATE_SHORE42,
    TEMPLATE_SHORE43,
    TEMPLATE_SHORE44,
    TEMPLATE_SHORE45,
    TEMPLATE_SHORE46,
    TEMPLATE_SHORE47,
    TEMPLATE_SHORE48,
    TEMPLATE_SHORE49,
    TEMPLATE_SHORE50,
    TEMPLATE_SHORE51,
    TEMPLATE_SHORE52,
    TEMPLATE_SHORE53,
    TEMPLATE_SHORE54,
    TEMPLATE_SHORE55,
    TEMPLATE_SHORE56,
    TEMPLATE_SHORECLIFF01,
    TEMPLATE_SHORECLIFF02,
    TEMPLATE_SHORECLIFF03,
    TEMPLATE_SHORECLIFF04,
    TEMPLATE_SHORECLIFF05,
    TEMPLATE_SHORECLIFF06,
    TEMPLATE_SHORECLIFF07,
    TEMPLATE_SHORECLIFF08,
    TEMPLATE_SHORECLIFF09,
    TEMPLATE_SHORECLIFF10,
    TEMPLATE_SHORECLIFF11,
    TEMPLATE_SHORECLIFF12,
    TEMPLATE_SHORECLIFF13,
    TEMPLATE_SHORECLIFF14,
    TEMPLATE_SHORECLIFF15,
    TEMPLATE_SHORECLIFF16,
    TEMPLATE_SHORECLIFF17,
    TEMPLATE_SHORECLIFF18,
    TEMPLATE_SHORECLIFF19,
    TEMPLATE_SHORECLIFF20,
    TEMPLATE_SHORECLIFF21,
    TEMPLATE_SHORECLIFF22,
    TEMPLATE_SHORECLIFF23,
    TEMPLATE_SHORECLIFF24,
    TEMPLATE_SHORECLIFF25,
    TEMPLATE_SHORECLIFF26,
    TEMPLATE_SHORECLIFF27,
    TEMPLATE_SHORECLIFF28,
    TEMPLATE_SHORECLIFF29,
    TEMPLATE_SHORECLIFF30,
    TEMPLATE_SHORECLIFF31,
    TEMPLATE_SHORECLIFF32,
    TEMPLATE_SHORECLIFF33,
    TEMPLATE_SHORECLIFF34,
    TEMPLATE_SHORECLIFF35,
    TEMPLATE_SHORECLIFF36,
    TEMPLATE_SHORECLIFF37,
    TEMPLATE_SHORECLIFF38,
    TEMPLATE_BOULDER1,
    TEMPLATE_BOULDER2,
    TEMPLATE_BOULDER3,
    TEMPLATE_BOULDER4,
    TEMPLATE_BOULDER5,
    TEMPLATE_BOULDER6,
    TEMPLATE_PATCH01,
    TEMPLATE_PATCH02,
    TEMPLATE_PATCH03,
    TEMPLATE_PATCH04,
    TEMPLATE_PATCH07,
    TEMPLATE_PATCH08,
    TEMPLATE_PATCH13,
    TEMPLATE_PATCH14,
    TEMPLATE_PATCH15,
    TEMPLATE_RIVER01,
    TEMPLATE_RIVER02,
    TEMPLATE_RIVER03,
    TEMPLATE_RIVER04,
    TEMPLATE_RIVER05,
    TEMPLATE_RIVER06,
    TEMPLATE_RIVER07,
    TEMPLATE_RIVER08,
    TEMPLATE_RIVER09,
    TEMPLATE_RIVER10,
    TEMPLATE_RIVER11,
    TEMPLATE_RIVER12,
    TEMPLATE_RIVER13,
    TEMPLATE_FALLS1,
    TEMPLATE_FALLS1A,
    TEMPLATE_FALLS2,
    TEMPLATE_FALLS2A,
    TEMPLATE_FORD1,
    TEMPLATE_FORD2,
    TEMPLATE_BRIDGE1,
    TEMPLATE_BRIDGE1D,
    TEMPLATE_BRIDGE2,
    TEMPLATE_BRIDGE2D,
    TEMPLATE_SLOPE01,
    TEMPLATE_SLOPE02,
    TEMPLATE_SLOPE03,
    TEMPLATE_SLOPE04,
    TEMPLATE_SLOPE05,
    TEMPLATE_SLOPE06,
    TEMPLATE_SLOPE07,
    TEMPLATE_SLOPE08,
    TEMPLATE_SLOPE09,
    TEMPLATE_SLOPE10,
    TEMPLATE_SLOPE11,
    TEMPLATE_SLOPE12,
    TEMPLATE_SLOPE13,
    TEMPLATE_SLOPE14,
    TEMPLATE_SLOPE15,
    TEMPLATE_SLOPE16,
    TEMPLATE_SLOPE17,
    TEMPLATE_SLOPE18,
    TEMPLATE_SLOPE19,
    TEMPLATE_SLOPE20,
    TEMPLATE_SLOPE21,
    TEMPLATE_SLOPE22,
    TEMPLATE_SLOPE23,
    TEMPLATE_SLOPE24,
    TEMPLATE_SLOPE25,
    TEMPLATE_SLOPE26,
    TEMPLATE_SLOPE27,
    TEMPLATE_SLOPE28,
    TEMPLATE_SLOPE29,
    TEMPLATE_SLOPE30,
    TEMPLATE_SLOPE31,
    TEMPLATE_SLOPE32,
    TEMPLATE_SLOPE33,
    TEMPLATE_SLOPE34,
    TEMPLATE_SLOPE35,
    TEMPLATE_SLOPE36,
    TEMPLATE_SLOPE37,
    TEMPLATE_SLOPE38,
    TEMPLATE_ROAD01,
    TEMPLATE_ROAD02,
    TEMPLATE_ROAD03,
    TEMPLATE_ROAD04,
    TEMPLATE_ROAD05,
    TEMPLATE_ROAD06,
    TEMPLATE_ROAD07,
    TEMPLATE_ROAD08,
    TEMPLATE_ROAD09,
    TEMPLATE_ROAD10,
    TEMPLATE_ROAD11,
    TEMPLATE_ROAD12,
    TEMPLATE_ROAD13,
    TEMPLATE_ROAD14,
    TEMPLATE_ROAD15,
    TEMPLATE_ROAD16,
    TEMPLATE_ROAD17,
    TEMPLATE_ROAD18,
    TEMPLATE_ROAD19,
    TEMPLATE_ROAD20,
    TEMPLATE_ROAD21,
    TEMPLATE_ROAD22,
    TEMPLATE_ROAD23,
    TEMPLATE_ROAD24,
    TEMPLATE_ROAD25,
    TEMPLATE_ROAD26,
    TEMPLATE_ROAD27,
    TEMPLATE_ROAD28,
    TEMPLATE_ROAD29,
    TEMPLATE_ROAD30,
    TEMPLATE_ROAD31,
    TEMPLATE_ROAD32,
    TEMPLATE_ROAD33,
    TEMPLATE_ROAD34,
    TEMPLATE_ROAD35,
    TEMPLATE_ROAD36,
    TEMPLATE_ROAD37,
    TEMPLATE_ROAD38,
    TEMPLATE_ROAD39,
    TEMPLATE_ROAD40,
    TEMPLATE_ROAD41,
    TEMPLATE_ROAD42,
    TEMPLATE_ROAD43,
    TEMPLATE_ROUGH01,
    TEMPLATE_ROUGH02,
    TEMPLATE_ROUGH03,
    TEMPLATE_ROUGH04,
    TEMPLATE_ROUGH05,
    TEMPLATE_ROUGH06,
    TEMPLATE_ROUGH07,
    TEMPLATE_ROUGH08,
    TEMPLATE_ROUGH09,
    TEMPLATE_ROUGH10,
    TEMPLATE_ROUGH11,
    TEMPLATE_ROAD44,
    TEMPLATE_ROAD45,
    TEMPLATE_RIVER14,
    TEMPLATE_RIVER15,
    TEMPLATE_RIVERCLIFF01,
    TEMPLATE_RIVERCLIFF02,
    TEMPLATE_RIVERCLIFF03,
    TEMPLATE_RIVERCLIFF04,
    TEMPLATE_BRIDGE_1A,
    TEMPLATE_BRIDGE_1B,
    TEMPLATE_BRIDGE_1C,
    TEMPLATE_BRIDGE_2A,
    TEMPLATE_BRIDGE_2B,
    TEMPLATE_BRIDGE_2C,
    TEMPLATE_BRIDGE_3A,
    TEMPLATE_BRIDGE_3B,
    TEMPLATE_BRIDGE_3C,
    TEMPLATE_BRIDGE_3D,
    TEMPLATE_BRIDGE_3E,
    TEMPLATE_BRIDGE_3F,
    TEMPLATE_F01,
    TEMPLATE_F02,
    TEMPLATE_F03,
    TEMPLATE_F04,
    TEMPLATE_F05,
    TEMPLATE_F06,

    // Custom interior pieces.
    TEMPLATE_ARRO0001,
    TEMPLATE_ARRO0002,
    TEMPLATE_ARRO0003,
    TEMPLATE_ARRO0004,
    TEMPLATE_ARRO0005,
    TEMPLATE_ARRO0006,
    TEMPLATE_ARRO0007,
    TEMPLATE_ARRO0008,
    TEMPLATE_ARRO0009,
    TEMPLATE_ARRO0010,
    TEMPLATE_ARRO0011,
    TEMPLATE_ARRO0012,
    TEMPLATE_ARRO0013,
    TEMPLATE_ARRO0014,
    TEMPLATE_ARRO0015,
    TEMPLATE_FLOR0001,
    TEMPLATE_FLOR0002,
    TEMPLATE_FLOR0003,
    TEMPLATE_FLOR0004,
    TEMPLATE_FLOR0005,
    TEMPLATE_FLOR0006,
    TEMPLATE_FLOR0007,
    TEMPLATE_GFLR0001,
    TEMPLATE_GFLR0002,
    TEMPLATE_GFLR0003,
    TEMPLATE_GFLR0004,
    TEMPLATE_GFLR0005,
    TEMPLATE_GSTR0001,
    TEMPLATE_GSTR0002,
    TEMPLATE_GSTR0003,
    TEMPLATE_GSTR0004,
    TEMPLATE_GSTR0005,
    TEMPLATE_GSTR0006,
    TEMPLATE_GSTR0007,
    TEMPLATE_GSTR0008,
    TEMPLATE_GSTR0009,
    TEMPLATE_GSTR0010,
    TEMPLATE_GSTR0011,
    TEMPLATE_LWAL0001,
    TEMPLATE_LWAL0002,
    TEMPLATE_LWAL0003,
    TEMPLATE_LWAL0004,
    TEMPLATE_LWAL0005,
    TEMPLATE_LWAL0006,
    TEMPLATE_LWAL0007,
    TEMPLATE_LWAL0008,
    TEMPLATE_LWAL0009,
    TEMPLATE_LWAL0010,
    TEMPLATE_LWAL0011,
    TEMPLATE_LWAL0012,
    TEMPLATE_LWAL0013,
    TEMPLATE_LWAL0014,
    TEMPLATE_LWAL0015,
    TEMPLATE_LWAL0016,
    TEMPLATE_LWAL0017,
    TEMPLATE_LWAL0018,
    TEMPLATE_LWAL0019,
    TEMPLATE_LWAL0020,
    TEMPLATE_LWAL0021,
    TEMPLATE_LWAL0022,
    TEMPLATE_LWAL0023,
    TEMPLATE_LWAL0024,
    TEMPLATE_LWAL0025,
    TEMPLATE_LWAL0026,
    TEMPLATE_LWAL0027,
    TEMPLATE_STRP0001,
    TEMPLATE_STRP0002,
    TEMPLATE_STRP0003,
    TEMPLATE_STRP0004,
    TEMPLATE_STRP0005,
    TEMPLATE_STRP0006,
    TEMPLATE_STRP0007,
    TEMPLATE_STRP0008,
    TEMPLATE_STRP0009,
    TEMPLATE_STRP0010,
    TEMPLATE_STRP0011,
    TEMPLATE_WALL0001,
    TEMPLATE_WALL0002,
    TEMPLATE_WALL0003,
    TEMPLATE_WALL0004,
    TEMPLATE_WALL0005,
    TEMPLATE_WALL0006,
    TEMPLATE_WALL0007,
    TEMPLATE_WALL0008,
    TEMPLATE_WALL0009,
    TEMPLATE_WALL0010,
    TEMPLATE_WALL0011,
    TEMPLATE_WALL0012,
    TEMPLATE_WALL0013,
    TEMPLATE_WALL0014,
    TEMPLATE_WALL0015,
    TEMPLATE_WALL0016,
    TEMPLATE_WALL0017,
    TEMPLATE_WALL0018,
    TEMPLATE_WALL0019,
    TEMPLATE_WALL0020,
    TEMPLATE_WALL0021,
    TEMPLATE_WALL0022,
    TEMPLATE_WALL0023,
    TEMPLATE_WALL0024,
    TEMPLATE_WALL0025,
    TEMPLATE_WALL0026,
    TEMPLATE_WALL0027,
    TEMPLATE_WALL0028,
    TEMPLATE_WALL0029,
    TEMPLATE_WALL0030,
    TEMPLATE_WALL0031,
    TEMPLATE_WALL0032,
    TEMPLATE_WALL0033,
    TEMPLATE_WALL0034,
    TEMPLATE_WALL0035,
    TEMPLATE_WALL0036,
    TEMPLATE_WALL0037,
    TEMPLATE_WALL0038,
    TEMPLATE_WALL0039,
    TEMPLATE_WALL0040,
    TEMPLATE_WALL0041,
    TEMPLATE_WALL0042,
    TEMPLATE_WALL0043,
    TEMPLATE_WALL0044,
    TEMPLATE_WALL0045,
    TEMPLATE_WALL0046,
    TEMPLATE_WALL0047,
    TEMPLATE_WALL0048,
    TEMPLATE_WALL0049,
    TEMPLATE_BRIDGE1H,
    TEMPLATE_BRIDGE2H,
    TEMPLATE_BRIDGE_1AX,
    TEMPLATE_BRIDGE_2AX,
    TEMPLATE_BRIDGE1X,
    TEMPLATE_BRIDGE2X,

    TEMPLATE_XTRA0001,
    TEMPLATE_XTRA0002,
    TEMPLATE_XTRA0003,
    TEMPLATE_XTRA0004,
    TEMPLATE_XTRA0005,
    TEMPLATE_XTRA0006,
    TEMPLATE_XTRA0007,
    TEMPLATE_XTRA0008,
    TEMPLATE_XTRA0009,
    TEMPLATE_XTRA0010,
    TEMPLATE_XTRA0011,
    TEMPLATE_XTRA0012,
    TEMPLATE_XTRA0013,
    TEMPLATE_XTRA0014,
    TEMPLATE_XTRA0015,
    TEMPLATE_XTRA0016,

#ifdef FIXIT_ANTS
    TEMPLATE_HILL01,
#endif

// >>> TF_TD_TILES enum >>>
    TEMPLATE_TDSH1,  // id 401
    TEMPLATE_TDWSH1,  // id 402
    TEMPLATE_TDSH2,  // id 403
    TEMPLATE_TDWSH2,  // id 404
    TEMPLATE_TDSH3,  // id 405
    TEMPLATE_TDWSH3,  // id 406
    TEMPLATE_TDSH4,  // id 407
    TEMPLATE_TDWSH4,  // id 408
    TEMPLATE_TDSH5,  // id 409
    TEMPLATE_TDWSH5,  // id 410
    TEMPLATE_TDSH6,  // id 411
    TEMPLATE_TDWSH6,  // id 412
    TEMPLATE_TDSH7,  // id 413
    TEMPLATE_TDWSH7,  // id 414
    TEMPLATE_TDSH8,  // id 415
    TEMPLATE_TDWSH8,  // id 416
    TEMPLATE_TDSH9,  // id 417
    TEMPLATE_TDWSH9,  // id 418
    TEMPLATE_TDSH10,  // id 419
    TEMPLATE_TDWSH10,  // id 420
    TEMPLATE_TDSH11,  // id 421
    TEMPLATE_TDWSH11,  // id 422
    TEMPLATE_TDSH12,  // id 423
    TEMPLATE_TDWSH12,  // id 424
    TEMPLATE_TDSH13,  // id 425
    TEMPLATE_TDWSH13,  // id 426
    TEMPLATE_TDSH14,  // id 427
    TEMPLATE_TDWSH14,  // id 428
    TEMPLATE_TDSH15,  // id 429
    TEMPLATE_TDWSH15,  // id 430
    TEMPLATE_TDSH16,  // id 431
    TEMPLATE_TDWSH16,  // id 432
    TEMPLATE_TDSH17,  // id 433
    TEMPLATE_TDWSH17,  // id 434
    TEMPLATE_TDSH18,  // id 435
    TEMPLATE_TDWSH18,  // id 436
    TEMPLATE_TDBRIDGE1,  // id 437
    TEMPLATE_TDWBRIDGE1,  // id 438
    TEMPLATE_TDBRIDGE2,  // id 439
    TEMPLATE_TDWBRIDGE2,  // id 440
    TEMPLATE_TDSH32,  // id 441
    TEMPLATE_TDWSH32,  // id 442
    TEMPLATE_TDSH33,  // id 443
    TEMPLATE_TDWSH33,  // id 444
    TEMPLATE_TDSH34,  // id 445
    TEMPLATE_TDWSH34,  // id 446
    TEMPLATE_TDSH35,  // id 447
    TEMPLATE_TDWSH35,  // id 448
    TEMPLATE_TDWP16,  // id 449
    TEMPLATE_TDWP17,  // id 450
    TEMPLATE_TDWP18,  // id 451
    TEMPLATE_TDWP19,  // id 452
    TEMPLATE_TDWP20,  // id 453
    TEMPLATE_TDCLEAR1,  // id 454
    TEMPLATE_TDWCLEAR1,  // id 455
    TEMPLATE_TDW1,  // id 456
    TEMPLATE_TDWW1,  // id 457
    TEMPLATE_TDWW2,  // id 458
    TEMPLATE_TDS01,  // id 459
    TEMPLATE_TDWS01,  // id 460
    TEMPLATE_TDS02,  // id 461
    TEMPLATE_TDWS02,  // id 462
    TEMPLATE_TDS03,  // id 463
    TEMPLATE_TDWS03,  // id 464
    TEMPLATE_TDS04,  // id 465
    TEMPLATE_TDWS04,  // id 466
    TEMPLATE_TDS05,  // id 467
    TEMPLATE_TDWS05,  // id 468
    TEMPLATE_TDS06,  // id 469
    TEMPLATE_TDWS06,  // id 470
    TEMPLATE_TDS07,  // id 471
    TEMPLATE_TDWS07,  // id 472
    TEMPLATE_TDS08,  // id 473
    TEMPLATE_TDWS08,  // id 474
    TEMPLATE_TDS09,  // id 475
    TEMPLATE_TDWS09,  // id 476
    TEMPLATE_TDS10,  // id 477
    TEMPLATE_TDWS10,  // id 478
    TEMPLATE_TDS11,  // id 479
    TEMPLATE_TDWS11,  // id 480
    TEMPLATE_TDS12,  // id 481
    TEMPLATE_TDWS12,  // id 482
    TEMPLATE_TDS13,  // id 483
    TEMPLATE_TDWS13,  // id 484
    TEMPLATE_TDS14,  // id 485
    TEMPLATE_TDWS14,  // id 486
    TEMPLATE_TDS15,  // id 487
    TEMPLATE_TDWS15,  // id 488
    TEMPLATE_TDS16,  // id 489
    TEMPLATE_TDWS16,  // id 490
    TEMPLATE_TDS17,  // id 491
    TEMPLATE_TDWS17,  // id 492
    TEMPLATE_TDS18,  // id 493
    TEMPLATE_TDWS18,  // id 494
    TEMPLATE_TDS19,  // id 495
    TEMPLATE_TDWS19,  // id 496
    TEMPLATE_TDS20,  // id 497
    TEMPLATE_TDWS20,  // id 498
    TEMPLATE_TDS21,  // id 499
    TEMPLATE_TDWS21,  // id 500
    TEMPLATE_TDS22,  // id 501
    TEMPLATE_TDWS22,  // id 502
    TEMPLATE_TDS23,  // id 503
    TEMPLATE_TDWS23,  // id 504
    TEMPLATE_TDS24,  // id 505
    TEMPLATE_TDWS24,  // id 506
    TEMPLATE_TDS25,  // id 507
    TEMPLATE_TDWS25,  // id 508
    TEMPLATE_TDS26,  // id 509
    TEMPLATE_TDWS26,  // id 510
    TEMPLATE_TDS27,  // id 511
    TEMPLATE_TDWS27,  // id 512
    TEMPLATE_TDS28,  // id 513
    TEMPLATE_TDWS28,  // id 514
    TEMPLATE_TDS29,  // id 515
    TEMPLATE_TDWS29,  // id 516
    TEMPLATE_TDS30,  // id 517
    TEMPLATE_TDWS30,  // id 518
    TEMPLATE_TDS31,  // id 519
    TEMPLATE_TDWS31,  // id 520
    TEMPLATE_TDS32,  // id 521
    TEMPLATE_TDWS32,  // id 522
    TEMPLATE_TDS33,  // id 523
    TEMPLATE_TDWS33,  // id 524
    TEMPLATE_TDS34,  // id 525
    TEMPLATE_TDWS34,  // id 526
    TEMPLATE_TDS35,  // id 527
    TEMPLATE_TDWS35,  // id 528
    TEMPLATE_TDS36,  // id 529
    TEMPLATE_TDWS36,  // id 530
    TEMPLATE_TDS37,  // id 531
    TEMPLATE_TDWS37,  // id 532
    TEMPLATE_TDS38,  // id 533
    TEMPLATE_TDWS38,  // id 534
    TEMPLATE_TDP07,  // id 535
    TEMPLATE_TDWP07,  // id 536
    TEMPLATE_TDWP08,  // id 537
    TEMPLATE_TDWP13,  // id 538
    TEMPLATE_TDWP14,  // id 539
    TEMPLATE_TDWP15,  // id 540
    TEMPLATE_TDB1,  // id 541
    TEMPLATE_TDWB1,  // id 542
    TEMPLATE_TDB2,  // id 543
    TEMPLATE_TDWB2,  // id 544
    TEMPLATE_TDWB3,  // id 545
    TEMPLATE_TDD01,  // id 546
    TEMPLATE_TDWD01,  // id 547
    TEMPLATE_TDD02,  // id 548
    TEMPLATE_TDWD02,  // id 549
    TEMPLATE_TDD03,  // id 550
    TEMPLATE_TDWD03,  // id 551
    TEMPLATE_TDD04,  // id 552
    TEMPLATE_TDWD04,  // id 553
    TEMPLATE_TDD05,  // id 554
    TEMPLATE_TDWD05,  // id 555
    TEMPLATE_TDD06,  // id 556
    TEMPLATE_TDWD06,  // id 557
    TEMPLATE_TDD07,  // id 558
    TEMPLATE_TDWD07,  // id 559
    TEMPLATE_TDD08,  // id 560
    TEMPLATE_TDWD08,  // id 561
    TEMPLATE_TDD09,  // id 562
    TEMPLATE_TDWD09,  // id 563
    TEMPLATE_TDD10,  // id 564
    TEMPLATE_TDWD10,  // id 565
    TEMPLATE_TDD11,  // id 566
    TEMPLATE_TDWD11,  // id 567
    TEMPLATE_TDD12,  // id 568
    TEMPLATE_TDWD12,  // id 569
    TEMPLATE_TDD13,  // id 570
    TEMPLATE_TDWD13,  // id 571
    TEMPLATE_TDD14,  // id 572
    TEMPLATE_TDWD14,  // id 573
    TEMPLATE_TDD15,  // id 574
    TEMPLATE_TDWD15,  // id 575
    TEMPLATE_TDD16,  // id 576
    TEMPLATE_TDWD16,  // id 577
    TEMPLATE_TDD17,  // id 578
    TEMPLATE_TDWD17,  // id 579
    TEMPLATE_TDD18,  // id 580
    TEMPLATE_TDWD18,  // id 581
    TEMPLATE_TDD19,  // id 582
    TEMPLATE_TDWD19,  // id 583
    TEMPLATE_TDD20,  // id 584
    TEMPLATE_TDWD20,  // id 585
    TEMPLATE_TDD21,  // id 586
    TEMPLATE_TDWD21,  // id 587
    TEMPLATE_TDD22,  // id 588
    TEMPLATE_TDWD22,  // id 589
    TEMPLATE_TDD23,  // id 590
    TEMPLATE_TDWD23,  // id 591
    TEMPLATE_TDD24,  // id 592
    TEMPLATE_TDWD24,  // id 593
    TEMPLATE_TDD25,  // id 594
    TEMPLATE_TDWD25,  // id 595
    TEMPLATE_TDD26,  // id 596
    TEMPLATE_TDWD26,  // id 597
    TEMPLATE_TDD27,  // id 598
    TEMPLATE_TDWD27,  // id 599
    TEMPLATE_TDD28,  // id 600
    TEMPLATE_TDWD28,  // id 601
    TEMPLATE_TDD29,  // id 602
    TEMPLATE_TDWD29,  // id 603
    TEMPLATE_TDD30,  // id 604
    TEMPLATE_TDWD30,  // id 605
    TEMPLATE_TDD31,  // id 606
    TEMPLATE_TDWD31,  // id 607
    TEMPLATE_TDD32,  // id 608
    TEMPLATE_TDWD32,  // id 609
    TEMPLATE_TDD33,  // id 610
    TEMPLATE_TDWD33,  // id 611
    TEMPLATE_TDD34,  // id 612
    TEMPLATE_TDWD34,  // id 613
    TEMPLATE_TDD35,  // id 614
    TEMPLATE_TDWD35,  // id 615
    TEMPLATE_TDD36,  // id 616
    TEMPLATE_TDWD36,  // id 617
    TEMPLATE_TDD37,  // id 618
    TEMPLATE_TDWD37,  // id 619
    TEMPLATE_TDD38,  // id 620
    TEMPLATE_TDWD38,  // id 621
    TEMPLATE_TDD39,  // id 622
    TEMPLATE_TDWD39,  // id 623
    TEMPLATE_TDD40,  // id 624
    TEMPLATE_TDWD40,  // id 625
    TEMPLATE_TDD41,  // id 626
    TEMPLATE_TDWD41,  // id 627
    TEMPLATE_TDD42,  // id 628
    TEMPLATE_TDWD42,  // id 629
    TEMPLATE_TDD43,  // id 630
    TEMPLATE_TDWD43,  // id 631
    TEMPLATE_TDWRV01,  // id 632
    TEMPLATE_TDWRV02,  // id 633
    TEMPLATE_TDWRV03,  // id 634
    TEMPLATE_TDWRV04,  // id 635
    TEMPLATE_TDWRV05,  // id 636
    TEMPLATE_TDWRV06,  // id 637
    TEMPLATE_TDWRV07,  // id 638
    TEMPLATE_TDWRV08,  // id 639
    TEMPLATE_TDWRV09,  // id 640
    TEMPLATE_TDWRV10,  // id 641
    TEMPLATE_TDWRV11,  // id 642
    TEMPLATE_TDWRV12,  // id 643
    TEMPLATE_TDWRV13,  // id 644
    TEMPLATE_TDFORD1,  // id 645
    TEMPLATE_TDWFORD1,  // id 646
    TEMPLATE_TDFORD2,  // id 647
    TEMPLATE_TDWFORD2,  // id 648
    TEMPLATE_TDFALLS1,  // id 649
    TEMPLATE_TDWFALLS1,  // id 650
    TEMPLATE_TDFALLS2,  // id 651
    TEMPLATE_TDWFALLS2,  // id 652
    TEMPLATE_TDWBRIDGE1D,  // id 653
    TEMPLATE_TDWBRIDGE2D,  // id 654
    TEMPLATE_TDSH20,  // id 655
    TEMPLATE_TDSH21,  // id 656
    TEMPLATE_TDSH22,  // id 657
    TEMPLATE_TDSH23,  // id 658
    TEMPLATE_TDBR1,  // id 659
    TEMPLATE_TDBR2,  // id 660
    TEMPLATE_TDBR3,  // id 661
    TEMPLATE_TDBR4,  // id 662
    TEMPLATE_TDBR6,  // id 663
    TEMPLATE_TDBR7,  // id 664
    TEMPLATE_TDBR8,  // id 665
    TEMPLATE_TDBR9,  // id 666
    TEMPLATE_TDP01,  // id 667
    TEMPLATE_TDP02,  // id 668
    TEMPLATE_TDP03,  // id 669
    TEMPLATE_TDP04,  // id 670
    TEMPLATE_TDP05,  // id 671
    TEMPLATE_TDP06,  // id 672
    TEMPLATE_TDSH19,  // id 673
    TEMPLATE_TDRV14,  // id 674
    TEMPLATE_TDRV15,  // id 675
    TEMPLATE_TDRV16,  // id 676
    TEMPLATE_TDRV17,  // id 677
    TEMPLATE_TDRV18,  // id 678
    TEMPLATE_TDRV19,  // id 679
    TEMPLATE_TDRV20,  // id 680
    TEMPLATE_TDRV21,  // id 681
    TEMPLATE_TDRV22,  // id 682
    TEMPLATE_TDRV23,  // id 683
    TEMPLATE_TDRV24,  // id 684
    TEMPLATE_TDRV25,  // id 685
    TEMPLATE_TDBRIDGE3,  // id 686
    TEMPLATE_TDBRIDGE3D,  // id 687
    TEMPLATE_TDBRIDGE4,  // id 688
    TEMPLATE_TDBRIDGE4D,  // id 689
    TEMPLATE_TDSH24,  // id 690
    TEMPLATE_TDSH25,  // id 691
    TEMPLATE_TDSH26,  // id 692
    TEMPLATE_TDSH27,  // id 693
    TEMPLATE_TDSH28,  // id 694
    TEMPLATE_TDSH29,  // id 695
    TEMPLATE_TDSH30,  // id 696
    TEMPLATE_TDSH31,  // id 697
    TEMPLATE_TDSH36,  // id 698
    TEMPLATE_TDSH37,  // id 699
    TEMPLATE_TDSH38,  // id 700
    TEMPLATE_TDSH39,  // id 701
    TEMPLATE_TDSH40,  // id 702
    TEMPLATE_TDSH41,  // id 703
    TEMPLATE_TDSH42,  // id 704
    TEMPLATE_TDSH43,  // id 705
    TEMPLATE_TDSH44,  // id 706
    TEMPLATE_TDSH45,  // id 707
    TEMPLATE_TDSH46,  // id 708
    TEMPLATE_TDSH47,  // id 709
    TEMPLATE_TDSH48,  // id 710
    TEMPLATE_TDSH49,  // id 711
    TEMPLATE_TDSH50,  // id 712
    TEMPLATE_TDSH51,  // id 713
    TEMPLATE_TDSH52,  // id 714
    TEMPLATE_TDSH53,  // id 715
    TEMPLATE_TDSH54,  // id 716
    TEMPLATE_TDSH55,  // id 717
    TEMPLATE_TDSH56,  // id 718
    TEMPLATE_TDSH57,  // id 719
    TEMPLATE_TDSH58,  // id 720
    TEMPLATE_TDSH59,  // id 721
    TEMPLATE_TDSH60,  // id 722
    TEMPLATE_TDSH61,  // id 723
    TEMPLATE_TDSH62,  // id 724
    TEMPLATE_TDSH63,  // id 725
// <<< TF_TD_TILES enum <<<
    TEMPLATE_COUNT,
    TEMPLATE_NONE = 65535,
    TEMPLATE_FIRST = 0
} TemplateType;

// PG inline TemplateType operator++(TemplateType &, int);
inline TemplateType operator++(TemplateType& n)
{
    n = (TemplateType)(((int)n) + 1);
    return n;
}

/**********************************************************************
**	The three dimensional terrain objects are enumerated here. These
**	objects function similar to buildings in that they can be driven
**	behind and can take damage on an individual basis.
*/
typedef enum TerrainType : char
{
    TERRAIN_NONE = -1,
    TERRAIN_TREE1,
    TERRAIN_TREE2,
    TERRAIN_TREE3,
    TERRAIN_TREE5,
    TERRAIN_TREE6,
    TERRAIN_TREE7,
    TERRAIN_TREE8,
    TERRAIN_TREE10,
    TERRAIN_TREE11,
    TERRAIN_TREE12,
    TERRAIN_TREE13,
    TERRAIN_TREE14,
    TERRAIN_TREE15,
    TERRAIN_TREE16,
    TERRAIN_TREE17,
    TERRAIN_CLUMP1,
    TERRAIN_CLUMP2,
    TERRAIN_CLUMP3,
    TERRAIN_CLUMP4,
    TERRAIN_CLUMP5,

    TERRAIN_ICE01,
    TERRAIN_ICE02,
    TERRAIN_ICE03,
    TERRAIN_ICE04,
    TERRAIN_ICE05,

    TERRAIN_BOXES01,
    TERRAIN_BOXES02,
    TERRAIN_BOXES03,
    TERRAIN_BOXES04,
    TERRAIN_BOXES05,
    TERRAIN_BOXES06,
    TERRAIN_BOXES07,
    TERRAIN_BOXES08,
    TERRAIN_BOXES09,

    TERRAIN_MINE,

    // Tiberian Factions note: the TD blossom tree is NOT a terrain type. Terrain
    // objects can't take our custom HD art (the launcher preloads terrain textures
    // from the base MEG and crashes on a new AssetName), so the blossom is a Neutral
    // BUILDING instead -- STRUCT_TDBLOSSOM (bdata.cpp). Trees mutate into it in
    // TerrainClass::AI; its spore-shed + Tiberium seeding live in BuildingClass::AI.

    TERRAIN_COUNT,
    TERRAIN_FIRST = 0
} TerrainType;

// PG inline TerrainType operator++(TerrainType &, int);

/**********************************************************************
**	Smudges are enumerated here. Smudges are transparent icons that are
**	drawn over the underlying terrain in order to give the effect of
**	alterations to the terrain. Craters are a good example of this.
*/
typedef enum SmudgeType : char
{
    SMUDGE_NONE = -1,
    SMUDGE_CRATER1,
    SMUDGE_CRATER2,
    SMUDGE_CRATER3,
    SMUDGE_CRATER4,
    SMUDGE_CRATER5,
    SMUDGE_CRATER6,
    SMUDGE_SCORCH1,
    SMUDGE_SCORCH2,
    SMUDGE_SCORCH3,
    SMUDGE_SCORCH4,
    SMUDGE_SCORCH5,
    SMUDGE_SCORCH6,
    SMUDGE_BIB1,
    SMUDGE_BIB2,
    SMUDGE_BIB3,

    SMUDGE_COUNT,
    SMUDGE_FIRST = 0
} SmudgeType;

// PG inline SmudgeType operator++(SmudgeType &, int);

/**********************************************************************
**	Animations are enumerated here. Animations are the high speed and
**	short lived effects that occur with explosions and fire.
*/
typedef enum AnimType : char
{
    ANIM_NONE = -1,
    ANIM_FBALL1,        // Large fireball explosion (bulges rightward).
    ANIM_FBALL_FADE,    // Fading fireball puff.
    ANIM_FRAG1,         // Medium fragment throwing explosion -- short decay.
    ANIM_VEH_HIT1,      //	Small fireball explosion (bulges rightward).
    ANIM_VEH_HIT2,      //	Small fragment throwing explosion -- pop & sparkles.
    ANIM_VEH_HIT3,      // Small fragment throwing explosion -- burn/exp mix.
    ANIM_ART_EXP1,      // Large fragment throwing explosion -- many sparkles.
    ANIM_NAPALM1,       // Small napalm burn.
    ANIM_NAPALM2,       // Medium napalm burn.
    ANIM_NAPALM3,       // Large napalm burn.
    ANIM_SMOKE_PUFF,    // Small rocket smoke trail puff.
    ANIM_PIFF,          // Machine gun impact piffs.
    ANIM_PIFFPIFF,      // Chaingun impact piffs.
    ANIM_FIRE_SMALL,    // Small flame animation.
    ANIM_FIRE_MED,      // Medium flame animation.
    ANIM_FIRE_MED2,     // Medium flame animation (oranger).
    ANIM_FIRE_TINY,     // Very tiny flames.
    ANIM_MUZZLE_FLASH,  // Big cannon flash (with translucency).
    ANIM_SMOKE_M,       // Smoke rising from ground.
    ANIM_BURN_SMALL,    // Small combustible fire effect (with trail off).
    ANIM_BURN_MED,      // Medium combustible fire effect (with trail off).
    ANIM_BURN_BIG,      // Large combustible fire effect (with trail off).
    ANIM_ON_FIRE_SMALL, // Burning effect for buildings.
    ANIM_ON_FIRE_MED,   // Burning effect for buildings.
    ANIM_ON_FIRE_BIG,   // Burning effect for buildings.
    ANIM_SAM_N,
    ANIM_SAM_NE,
    ANIM_SAM_E,
    ANIM_SAM_SE,
    ANIM_SAM_S,
    ANIM_SAM_SW,
    ANIM_SAM_W,
    ANIM_SAM_NW,
    ANIM_GUN_N,
    ANIM_GUN_NE,
    ANIM_GUN_E,
    ANIM_GUN_SE,
    ANIM_GUN_S,
    ANIM_GUN_SW,
    ANIM_GUN_W,
    ANIM_GUN_NW,
    ANIM_FLAME_N, // TD flamethrower jet (E4) -- directional muzzle anim, 8 dirs in Dir_Facing order.
    ANIM_FLAME_NE,
    ANIM_FLAME_E,
    ANIM_FLAME_SE,
    ANIM_FLAME_S,
    ANIM_FLAME_SW,
    ANIM_FLAME_W,
    ANIM_FLAME_NW,
    ANIM_CHEM_N, // TD chem-warrior spray jet (E5) -- directional muzzle anim, 8 dirs in Dir_Facing order (kept contiguous after FLAME for the One_Time donor loop).
    ANIM_CHEM_NE,
    ANIM_CHEM_E,
    ANIM_CHEM_SE,
    ANIM_CHEM_S,
    ANIM_CHEM_SW,
    ANIM_CHEM_W,
    ANIM_CHEM_NW,
    ANIM_LZ_SMOKE,
    ANIM_CRATE_DEVIATOR, // Red finned missile.
    ANIM_CRATE_DOLLAR,   // Dollar sign.
    ANIM_CRATE_EARTH,    // Cracked Earth.
    ANIM_CRATE_EMPULSE,  // Plasma ball.
    ANIM_CRATE_INVUN,    // Orange sphere with green rings.
    ANIM_CRATE_MINE,     // Spiked mine.
    ANIM_CRATE_RAPID,    // Red skull.
    ANIM_CRATE_STEALTH,  // Cloaking sphere.
    ANIM_CRATE_MISSILE,  // Green finned missile.
    ANIM_MOVE_FLASH,
    ANIM_OILFIELD_BURN,
    ANIM_ELECT_DIE,     // Electrocution infantryman death from Tesla coil
    ANIM_PARACHUTE,     // Parachute (designed to be attached to object).
    ANIM_DOG_ELECT_DIE, // Electrocution dog death from Tesla coil
    ANIM_CORPSE1,
    ANIM_CORPSE2,
    ANIM_CORPSE3,
    ANIM_SPUTDOOR,
    ANIM_ATOM_BLAST,
    ANIM_CHRONO_BOX,
    ANIM_GPS_BOX,
    ANIM_INVUL_BOX,
    ANIM_PARA_BOX,
    ANIM_SONAR_BOX,
    ANIM_TWINKLE1,
    ANIM_TWINKLE2,
    ANIM_TWINKLE3,
    ANIM_FLAK,
    ANIM_WATER_EXP1,
    ANIM_WATER_EXP2,
    ANIM_WATER_EXP3,
    ANIM_CRATE_ARMOR,
    ANIM_CRATE_SPEED,
    ANIM_CRATE_FPOWER,
    ANIM_CRATE_TQUAKE,
    ANIM_PARA_BOMB,
    ANIM_MINE_EXP1,
    ANIM_FLAG,
    ANIM_BEACON,

    // Tiberian Factions mod anims ported from TD (tiberiandawn/defines.h
    // ANIM_*). Each is the runtime side-effect anim for a TD weapon/super.
    ANIM_TD_ION_CANNON, // TD GDI Ion Cannon beam strike (TDIONSFX shape).
    ANIM_TDFRAG2,       // TD vehicle death frag explosion (FRAG3 shape) -- TD's ANIM_FRAG2, which RA lacks (RA only has ANIM_FRAG1).

    // Tiberian Factions -- Flame Tank (UNIT_TDFTNK) directional muzzle jets. SEPARATE
    // family from the Flamethrower infantry's ANIM_FLAME_* so the sprite anchor can be
    // tuned to the tank's twin nozzles without moving the trooper's flame (they share no
    // art now). Same 8-dir Dir_Facing order + IsFlameThrower behaviour as ANIM_FLAME_*;
    // kept contiguous for the techno.cpp `ANIM_TDFTFLAME_N + Dir_Facing` dispatch and the
    // adata.cpp donor-ImageData loop.
    ANIM_TDFTFLAME_N,
    ANIM_TDFTFLAME_NE,
    ANIM_TDFTFLAME_E,
    ANIM_TDFTFLAME_SE,
    ANIM_TDFTFLAME_S,
    ANIM_TDFTFLAME_SW,
    ANIM_TDFTFLAME_W,
    ANIM_TDFTFLAME_NW,

    // Tiberian Factions -- green "Tiberium fumes" venting from a harvester docked at
    // an RA refinery (reverse cross-dock). Reuses the existing SMOKLAND art (the LZ
    // drop-zone smoke) so it renders in HD, but is its OWN AnimType so it does NOT
    // trigger ANIM_LZ_SMOKE's hardcoded map-reveal (Sight_From) and gets a tuned
    // (non-127) loop count. MUST stay in lockstep with adata.cpp Init_Heap order.
    ANIM_TIB_FUMES,

#ifdef FIXIT_ANTS
    ANIM_ANT1_DEATH,
    ANIM_ANT2_DEATH,
    ANIM_ANT3_DEATH,
#endif

#ifdef REMASTER_BUILD
    ANIM_FIRE_SMALL_VIRTUAL, // Small flame animation.
    ANIM_FIRE_MED_VIRTUAL,   // Medium flame animation.
    ANIM_FIRE_MED2_VIRTUAL,  // Medium flame animation (oranger).
    ANIM_FIRE_TINY_VIRTUAL,  // Very tiny flames.
    ANIM_BEACON_VIRTUAL,     // Beacon (virtual).
#endif

    ANIM_COUNT,
    ANIM_FIRST = 0
} AnimType;

inline AnimType operator++(AnimType&, int);

/****************************************************************************
**	Infantry can be performing various activities. These can range from simple
**	idle animations to physical hand to hand combat.
*/
typedef enum DoType : char
{
    DO_NOTHING = -1, // Not performing any choreographed sequence.
    DO_STAND_READY = 0,
    DO_STAND_GUARD,
    DO_PRONE,
    DO_WALK,
    DO_FIRE_WEAPON,
    DO_LIE_DOWN,
    DO_CRAWL,
    DO_GET_UP,
    DO_FIRE_PRONE,
    DO_IDLE1,
    DO_IDLE2,
    DO_GUN_DEATH,
    DO_EXPLOSION_DEATH,
    DO_EXPLOSION2_DEATH,
    DO_GRENADE_DEATH,
    DO_FIRE_DEATH,
    DO_GESTURE1,
    DO_SALUTE1,
    DO_GESTURE2,
    DO_SALUTE2,
    DO_DOG_MAUL,

    DO_COUNT,
    DO_FIRST = 0
} DoType;

inline DoType operator++(DoType&, int);

/*
**	This structure is associated with each maneuver type. It tells whether the
**	maneuver can be interrupted and the frame rate.
*/
typedef struct
{
    unsigned Interrupt : 1;   // Can it be interrupted?
    unsigned IsMobile : 1;    // Can it move while doing this?
    unsigned RandomStart : 1; // Should animation be "randomized"?
    unsigned char Rate;       // Frame rate.
} DoStruct;

typedef struct
{
    int Frame;           // Starting frame of the animation.
    unsigned char Count; // Number of frames of animation.
    unsigned char Jump;  // Frames to jump between facings.
} DoInfoStruct;

/****************************************************************************
**	These are the various radio message that can be transmitted between
**	units and buildings. Some of these require a response from the receiver
**	and some don't.
*/
typedef enum RadioMessageType : unsigned char
{
    RADIO_STATIC,         // "hisssss" -- non-message
    RADIO_ROGER,          // "Roger."
    RADIO_HELLO,          // "Come in. I wish to talk."
    RADIO_OVER_OUT,       // "Something came up, bye."
    RADIO_PICK_UP,        // "Please pick me up."
    RADIO_ATTACH,         // "Attach to transport."
    RADIO_DELIVERY,       // "I've got a delivery for you."
    RADIO_HOLD_STILL,     // "I'm performing load/unload maneuver. Be careful."
    RADIO_UNLOADED,       // "I'm clear."
    RADIO_UNLOAD,         // "You are clear to unload. Please start driving off now."
    RADIO_NEGATIVE,       // "Am unable to comply."
    RADIO_BUILDING,       // "I'm starting construction now... act busy."
    RADIO_COMPLETE,       // "I've finished construction. You are free."
    RADIO_REDRAW,         // "Oops, sorry. I might have bumped you a little."
    RADIO_DOCKING,        // "I'm trying to load up now."
    RADIO_CAN_LOAD,       // "May I become a passenger?"
    RADIO_ARE_REFINERY,   // "Are you a refinery ready to take shipment?"
    RADIO_TRYING_TO_LOAD, // "Are you trying to become a passenger?"
    RADIO_MOVE_HERE,      // "Move to location X."
    RADIO_NEED_TO_MOVE,   // "Do you need to move somewhere?"
    RADIO_YEA_NOW_WHAT,   // "All right already. Now what?"
    RADIO_IM_IN,          // "I'm a passenger now."
    RADIO_BACKUP_NOW,     // "Begin backup into refinery now."
    RADIO_RUN_AWAY,       // "Run away! Run away!"
    RADIO_TETHER,         // "Establish tether contact."
    RADIO_UNTETHER,       // "Break tether contact."
    RADIO_REPAIR,         // "Repair one step."
    RADIO_PREPARED,       // "Are you prepared to fight?"
    RADIO_ATTACK_THIS,    // "Attack this target please."
    RADIO_RELOAD,         // "Reload one step please."
    RADIO_CANT,           // "Circumstances prevent success."
    RADIO_ALL_DONE,       // "I have completed the task."
    RADIO_NEED_REPAIR,    // "Are you in need of service depot work?"
    RADIO_ON_DEPOT,       // "Are you sitting on a service depot?"
    RADIO_CANCEL,         // "Scratch that." (TF: harvester queue jump, CFE port)

    RADIO_COUNT
} RadioMessageType;

/****************************************************************************
**	Various trigger events and actions require additional data. This enumeration is
**	used to indicate what kind of additional data is required. This is also used
**	for team mission types that might need additional data.
*/
typedef enum NeedType : unsigned char
{
    NEED_NONE,      // No additional data is required.
    NEED_THEME,     // Need a musical theme.
    NEED_MOVIE,     // Need a movie to play.
    NEED_SOUND,     // Sound effect.
    NEED_SPEECH,    // Speech from EVA.
    NEED_INFANTRY,  // Infantry type class.
    NEED_UNIT,      // Unit type class.
    NEED_AIRCRAFT,  // Aircraft type class.
    NEED_STRUCTURE, // Structure type class.
    NEED_WAYPOINT,  // Waypoint letter.
    NEED_NUMBER,    // General number.
    NEED_TRIGGER,   //	Trigger object reference.
    NEED_TEAM,      // Team type class.
    NEED_HOUSE,     // House type number.
    NEED_TIME,      // Time delay value required.
    NEED_QUARRY,    // Quarry type is needed.
    NEED_FORMATION, // A formation type is needed.
    NEED_BOOL,      // Boolean value is needed.
    NEED_SPECIAL,   // Special weapon ability.
    NEED_MISSION,   // General unit mission type.
    NEED_HEX_NUMBER // General number.
} NeedType;

/****************************************************************************
**	There are various target types that teams and special weapons can be
**	assigned to attack. These are general target categories since the actual
**	disposition of potential targets cannot be precisely predicted -- thus these
**	serve as guidelines for the computer AI.
*/
typedef enum QuarryType : unsigned char
{
    QUARRY_NONE,

    QUARRY_ANYTHING,   // Attack any enemy (same as "hunt").
    QUARRY_BUILDINGS,  // Attack buildings (in general).
    QUARRY_HARVESTERS, // Attack harvesters or refineries.
    QUARRY_INFANTRY,   // Attack infantry.
    QUARRY_VEHICLES,   // Attack combat vehicles.
    QUARRY_VESSELS,    // Attach ships.
    QUARRY_FACTORIES,  // Attack factories (all types).
    QUARRY_DEFENSE,    // Attack base defense buildings.
    QUARRY_THREAT,     // Attack enemies near friendly base.
    QUARRY_POWER,      // Attack power facilities.
    QUARRY_FAKES,      // Prefer to attack fake buildings.

    QUARRY_COUNT,
    QUARRY_FIRST = 0
} QuarryType;

/****************************************************************************
**	Teams can be assigned formations. This specifies the various formations that
**	a team can be composed into.
*/
typedef enum FormationType : unsigned char
{
    FORMATION_NONE,

    FORMATION_TIGHT,   // Tight grouping (vulnerable units in center).
    FORMATION_LOOSE,   // Loose grouping (one cell separation between units).
    FORMATION_WEDGE_N, // Wedge shape.
    FORMATION_WEDGE_E, // Wedge shape.
    FORMATION_WEDGE_S, // Wedge shape.
    FORMATION_WEDGE_W, // Wedge shape.
    FORMATION_LINE_NS, // Column formation.
    FORMATION_LINE_EW, // Line formation.

    FORMATION_COUNT,
    FORMATION_FIRST = 0
} FormationType;

/*
** When a unit is not in formation this magic value is used.
*/
#define INVALID_FORMATION 0x80000000

/****************************************************************************
**	Selected units have a special selected unit box around them. These are the
**	defines for the two types of selected unit boxes. One is for infantry and
**	the other is for regular units.
*/
typedef enum SelectEnum : char
{
    SELECT_NONE = -1,
    SELECT_INFANTRY,               // Small infantry selection box.
    SELECT_UNIT,                   // Big unit selection box.
    SELECT_BUILDING = SELECT_UNIT, // Custom box for buildings.
    SELECT_TERRAIN = SELECT_UNIT,  // Custom box for terrain objects.
    SELECT_WRENCH,                 // A building is repairing overlay graphic.

    SELECT_COUNT
} SelectEnum;

/****************************************************************************
**	The pip shapes and text shapes are enumerated according to the following
**	type. These special shapes are drawn over special objects or in other places
**	where shape technology is needed.
*/
typedef enum PipEnum : unsigned char
{
    PIP_EMPTY,    // Empty pip spot.
    PIP_FULL,     // Full pip spot.
    PIP_PRIMARY,  // "Primary" building marker.
    PIP_READY,    // "Ready" construction information tag.
    PIP_HOLDING,  // "Hold"ing construction information tag.
    PIP_ENGINEER, // Full pip with engineer coloring.
    PIP_CIVILIAN, // Full pip with civilian coloring.
    PIP_COMMANDO, // Full pip with commando coloring.
    PIP_NUMBERS,  // digit 0
    PIP_NUMBER1,  // digit 1
    PIP_NUMBER2,  // digit 2
    PIP_NUMBER3,  // digit 3
    PIP_NUMBER4,  // digit 4
    PIP_NUMBER5,  // digit 5
    PIP_NUMBER6,  // digit 6
    PIP_NUMBER7,  // digit 7
    PIP_NUMBER8,  // digit 8
    PIP_NUMBER9,  // digit 9
    PIP_DECOY,    // word "Decoy" for fake buildings
    PIP_LETTERF,  // letter 'F' for signifying in-formation
    PIP_MEDIC,    // Little medic red cross.
    PIP_PRI       // Abbreviated "Primary" for kennel
} PipEnum;

/****************************************************************************
**	The radar map can be in one of several states depending on the presense of
**	certain structures and power levels.
*/
typedef enum RadarEnum : unsigned char
{
    RADAR_NONE, // Radar map doesn't exist at all
    RADAR_OFF,  // Radar map is present, but displayed as off and non-interactive
    RADAR_ON    // Radar map is present, visible, and fully interactive
} RadarEnum;

/****************************************************************************
**	The mouse cursor can be in different states. These states are listed
**	below. Some of these represent animating mouse cursors. The mouse
**	is controlled by passing one of these values to the appropriate
**	MouseClass member function.
*/
typedef enum MouseType : unsigned char
{
    MOUSE_NORMAL,
    MOUSE_N,
    MOUSE_NE,
    MOUSE_E,
    MOUSE_SE,
    MOUSE_S,
    MOUSE_SW,
    MOUSE_W,
    MOUSE_NW,
    MOUSE_NO_N,
    MOUSE_NO_NE,
    MOUSE_NO_E,
    MOUSE_NO_SE,
    MOUSE_NO_S,
    MOUSE_NO_SW,
    MOUSE_NO_W,
    MOUSE_NO_NW,
    MOUSE_NO_MOVE,
    MOUSE_CAN_MOVE,
    MOUSE_ENTER,
    MOUSE_DEPLOY,
    MOUSE_CAN_SELECT,
    MOUSE_CAN_ATTACK,
    MOUSE_SELL_BACK,
    MOUSE_SELL_UNIT,
    MOUSE_REPAIR,
    MOUSE_NO_REPAIR,
    MOUSE_NO_SELL_BACK,
    MOUSE_RADAR_CURSOR,
    MOUSE_NUCLEAR_BOMB,
    MOUSE_AIR_STRIKE,
    MOUSE_DEMOLITIONS,
    MOUSE_AREA_GUARD,
    MOUSE_HEAL,
    MOUSE_DAMAGE,  // Engineer entering building to damage it.
    MOUSE_GREPAIR, // Engineer entering friendly building to heal it.
    MOUSE_STAY_ATTACK,
    MOUSE_NO_DEPLOY,
    MOUSE_NO_ENTER,
    MOUSE_NO_GREPAIR,
    MOUSE_CHRONO_SELECT,
    MOUSE_CHRONO_DEST,

    MOUSE_COUNT
} MouseType;

/**********************************************************************
**	This structure is used to control the box relief style drawn by
**	the Draw_Box() function.
*/
typedef struct
{
    int Filler;    // Center box fill color.
    int Shadow;    // Shadow color (darker).
    int Highlight; // Highlight color (lighter).
    int Corner;    // Corner color (transition).
} BoxStyleType;

typedef enum BoxStyleEnum : unsigned char
{
    BOXSTYLE_DOWN,       // Typical depressed edge border.
    BOXSTYLE_RAISED,     // Typical raised edge border.
    BOXSTYLE_DIS_DOWN,   // Disabled but depressed.
    BOXSTYLE_DIS_RAISED, // Disabled but raised.
    BOXSTYLE_BOX,        // list box.
    BOXSTYLE_BORDER,     // main dialog box.

    BOXSTYLE_COUNT
} BoxStyleEnum;

/**********************************************************************
**	Damage, as inflicted by projectiles, has different characteristics.
**	These are the different "warhead" types that can be assigned to the
**	various projectiles in the game.
*/
typedef enum WarheadType : char
{
    WARHEAD_NONE = -1,

    WARHEAD_SA,           // Small arms -- good against infantry.
    WARHEAD_HE,           //	High explosive -- good against buildings & infantry.
    WARHEAD_AP,           // Armor piercing -- good against armor.
    WARHEAD_FIRE,         // Incendiary -- Good against flammables.
    WARHEAD_HOLLOW_POINT, // Sniper bullet type.
    WARHEAD_TESLA,        // Electrocution warhead for infantrymen
    WARHEAD_DOG,          // Slavering attack beast mauling infantryman
    WARHEAD_NUKE,         // Nuclear missile
#ifdef FIXIT_CSII         //	checked - ajw 9/28/98
    WARHEAD_MECHANICAL,   // repair weapon for vehicles
#endif

    // Tiberian Factions mod warheads ported from TD (tiberiandawn/defines.h
    // WARHEAD_*). Each maps to a [Name] section in rules.ini.
    WARHEAD_LASER, // 100%-vs-all-armor profile (Obelisk of Light).
    WARHEAD_TDHE,  // TD high-explosive armor table (used by BULLET_SSM via TDTowTwo).
    WARHEAD_TDPB,  // Particle beam (TD WARHEAD_PB) — Ion Cannon strike. {1.0, 1.0, 0.75, 0.75, 0.75}.
    WARHEAD_TDSA,  // TD small arms (WARHEAD_SA) — Spread 2, verses {1.0,0.5,0.5625,0.25,0.25}, no destroy.
    WARHEAD_TDAP,  // TD armor-piercing (WARHEAD_AP) — Spread 6, verses {0.25,0.75,0.75,1.0,0.5}, destroys wall+wood (APDS / SAM / Dragon).
    WARHEAD_TDFIRE, // TD incendiary (WARHEAD_FIRE) — Spread 8, verses {0.88,1.0,0.69,0.25,0.5}, destroys wood+tiberium not wall (Flamethrower).
    WARHEAD_TDCHEM, // TD chem spray — HE damage table (== TDHE) but Explosion=0 (TD ClassChem impact = ANIM_NONE). Separate from TDHE so the grenadier keeps its blast.
    WARHEAD_TDHOLLOW, // TD hollow-point (WARHEAD_HOLLOW_POINT) — Commando sniper. Spread 4, verses {1.0,0.03,0.03,0.03,0.03}: one-shots infantry, ~nil vs armor/buildings.
    WARHEAD_TDAGT, // AGT-only warhead, fired from TDTowTwo (the GDI Advanced Guard Tower) ONLY. Verses identical to TDHE today; kept separate so the AGT can be tuned without touching the ~12 other TDHE weapons.

    WARHEAD_COUNT,
    WARHEAD_FIRST = 0
} WarheadType;

/**********************************************************************
**	This enumerates the various weapon types. The weapon is characterized
**	by the projectile it launches, the damage it does, and the rate of
**	fire.
*/
typedef enum WeaponType : char
{
    WEAPON_NONE = -1,

    WEAPON_COLT45,
    WEAPON_ACK_ACK,
    WEAPON_VULCAN,
    WEAPON_MAVERICK,
    WEAPON_CAMERA,
    WEAPON_FIREBALL,
    WEAPON_RIFLE,
    WEAPON_CHAIN_GUN,
    WEAPON_PISTOL,
    WEAPON_M16,
    WEAPON_DRAGON,
    WEAPON_HELLFIRE,
    WEAPON_GRENADE,
    WEAPON_75MM,
    WEAPON_90MM,
    WEAPON_105MM,
    WEAPON_120MM,
    WEAPON_TURRET_GUN,
    WEAPON_MAMMOTH_TUSK,
    WEAPON_155MM,
    WEAPON_M60MG,
    WEAPON_NAPALM,
    WEAPON_TESLA_ZAP,
    WEAPON_NIKE,
    WEAPON_8INCH,
    WEAPON_STINGER,
    WEAPON_TORPEDO,
    WEAPON_2INCH,
    WEAPON_DEPTH_CHARGE,
    WEAPON_PARA_BOMB,
    WEAPON_DOGJAW,
    WEAPON_HEAL,
    WEAPON_SCUD,
    WEAPON_FLAMER,
    WEAPON_REDEYE,

#ifdef FIXIT_ANTS
    WEAPON_MANDIBLE,
#endif

#ifdef FIXIT_CSII //	checked - ajw 9/28/98
    WEAPON_PORTATESLA,
    WEAPON_GOODWRENCH,
    WEAPON_SUBSCUD,
    WEAPON_TTANKZAP,
    WEAPON_APTUSK,
    WEAPON_DEMOCHARGE,
#endif
#ifdef FIXIT_CARRIER //	checked - ajw 9/28/98
    WEAPON_CARRIER,
#endif

    // Tiberian Factions mod weapons ported from TD (tiberiandawn/defines.h
    // WEAPON_*). Each maps to a [Name] section in rules.ini.
    WEAPON_TOW_TWO,        // Advanced Guard Tower missile (anti-armor + AA).
    WEAPON_TD_TURRET_GUN,  // Nod Turret cannon (TD-authentic ROF/range).
    WEAPON_OBELISK_LASER,  // Obelisk of Light beam (data piece only; render in M5).
    WEAPON_TD_CHAIN_GUN,   // GDI Guard Tower chain gun (TD WEAPON_CHAIN_GUN).
    WEAPON_TDNIKE,         // TD SAM Site missile (anti-air only, fires BULLET_TDPATRIOT).
    WEAPON_TDM16,          // TD Minigunner rifle (E1) — Dmg15/ROF20/Range2, BULLET_TDBULLET, WARHEAD_TDSA.
    WEAPON_TDGRENADE,      // TD Grenadier toss (E2) — Dmg50/ROF60/Range3.25, Projectile=Lobbed (RA bomb), WARHEAD_TDHE.
    WEAPON_TDDRAGON,       // TD Rocket Soldier launcher (E3) — Dmg30/ROF60/Range4, BULLET_TDTOW, WARHEAD_TDAP, Report=BAZOOK1.
    WEAPON_TDFLAME,        // TD Flamethrower (E4, Nod) — Dmg35/ROF50/Range2, BULLET_TDFLAME, WARHEAD_TDFIRE, Anim=FLAME-N.
    WEAPON_TDCHEM,         // TD Chem Warrior spray (E5, Nod) — Dmg80/ROF70/Range2, BULLET_TDCHEM, WARHEAD_TDHE (bullet warhead), Report=FLAMER2, Anim=CHEM-N.
    WEAPON_TDRIFLE,        // TD Commando sniper (RMBO) — Dmg125/ROF40/Range5.5, BULLET_TDBULLET, WARHEAD_TDHOLLOW, Report=RAMGUN2.
    WEAPON_TD105MM,        // TD Medium Tank cannon (MTNK) — Dmg30/ROF50/Range4.75, BULLET_TDAPDS (reuse), WARHEAD_TDAP (reuse), Report=TNKFIRE4, Anim=GUNFIRE.
    WEAPON_TD75MM,         // TD Light Tank cannon (LTNK) — Dmg25/ROF60/Range4, BULLET_TDAPDS (reuse), WARHEAD_TDAP (reuse), Report=TNKFIRE3, Anim=GUNFIRE.
    WEAPON_TD120MM,        // TD Mammoth Tank primary cannon (HTNK) — Dmg40/ROF80/Range4.75, BULLET_TDAPDS (reuse), WARHEAD_TDAP (reuse), Report=TNKFIRE6.
    WEAPON_TDTUSK,         // TD Mammoth Tusk AA missiles (HTNK secondary) — Dmg75/ROF80/Range5, Projectile=TDSSM (reuse, AA+AG homing), WARHEAD_TDHE, Report=ROCKET1.
    WEAPON_TDFLAMETONGUE,  // TD Flame Tank cannon (FTNK) — Dmg50/ROF50/Range2, BULLET_TDFLAME (reuse), WARHEAD_TDFIRE (reuse), Anim=TDFLAME-N. The stronger FLAME_TONGUE (vs Flamethrower's 35).
    WEAPON_TDM60MG,        // TD Hum-vee/Buggy MG (JEEP/BGGY) — Dmg15/ROF30/Range4, BULLET_TDBULLET (reuse TD50cal), WARHEAD_TDSA (reuse), Report=MGUN11, Anim=GUN-N. Distinct from RA-vanilla [M60mg] (ROF20/PILLBOX1/MINIGUN).
    WEAPON_TDSTNKDRAGON,   // TD Stealth Tank launcher (STNK) — WEAPON_DRAGON + Burst=2 (TD is_twoshooter). Same TDTOW/TDAP/BAZOOK1 chain as TDDragon; separate weapon so the single-shot E3/Bike keep Burst=1.
    WEAPON_TDMLRS,         // TD Rocket Launcher (MLRS) — Dmg75/ROF80/Range6, BULLET_TDSSM2 homing, WARHEAD_TDHE, Report=ROCKET1, Burst=2. Registered as "TDMlrsRocket" (distinct from the [TDMLRS] unit section).
    WEAPON_TDHONESTJOHN,   // TD SSM Launcher (MSAM) — Dmg100/ROF200/Range10, BULLET_TDMISSILE (non-homing), WARHEAD_TDFIRE, Report=ROCKET1. Registered as "TDHonestJohn".
    WEAPON_TD155MM,        // TD Artillery (ARTY) — Dmg150/ROF65/Range6, BULLET_TDHESHELL (arcing), WARHEAD_TDHE, Report=TNKFIRE2, Anim=GUNFIRE. Registered as "TD155mm".
    WEAPON_TDAPACHEGUN,    // TD Apache chain gun (HELI) — TDChainGun + Burst=2 (TD is_twoshooter). Same TDSpreadfire/TDHE/GUN8 chain as TDChainGun; separate so the single-shot GTWR keeps Burst=1.
    WEAPON_TDTOMAHAWK,     // v4.0: GDI Gunboat primary — TD homing missile (BULLET_TDTOW, AG-only), WARHEAD_TDAP, anti-surface/anti-shore. IsTDPort (raw Speed MPH_ROCKET + AI_TD homing). Registered "TDTomahawk".
    WEAPON_TDOBELISKSUBLASER, // v4.0: Nod Obelisk Attack Sub — TDLaser bolt (clone of the Obelisk's TDOblsLaser, NO Charges since a vessel can't building-charge), short range + slow ROF + high dmg. Registered "TDObeliskSubLaser".
    WEAPON_TDA10NAPALM,    // v4.0: A-10 napalm strafe — TD WEAPON_NAPALM verbatim (Dmg100/ROF20/Range4.5=0x0480, VOC_NONE), BULLET_TDNAPALM. Registered "TDA10Napalm".
    WEAPON_TDFLAMEBUNKER,  // v4.0: Nod Flame Bunker (TDFBNK) — clone of TDFlameTongue with Range 2->4 (static defence must outrange range-3 infantry). BULLET_TDFLAME/WARHEAD_TDFIRE reused. IsTDPort (raw Speed 40). Registered "TDFlameBunker".
    WEAPON_TSHOVERMISSILE, // TS-spike: Hover MLRS missile — TS [HoverMissile] stats (Dmg30/ROF68/Range8/Burst2) on the TDSSM AA+AG homing chain (TDTusk pattern). IsTDPort (raw Speed). Registered "TSHoverMissile".

    WEAPON_COUNT,
    WEAPON_FIRST = 0
} WeaponType;

/**********************************************************************
**	The various armor types are best suited to defend against a limited
**	kind of warheads. The game strategy revolves around proper
**	combination of armor and weaponry. Each vehicle or building has armor
**	rated according to one of the following types.
*/
typedef enum ArmorType : unsigned char
{
    ARMOR_NONE,     // Vulnerable to SA and HE.
    ARMOR_WOOD,     // Vulnerable to HE and Fire.
    ARMOR_ALUMINUM, // Vulnerable to AP and SA.
    ARMOR_STEEL,    // Vulnerable to AP.
    ARMOR_CONCRETE, // Vulnerable to HE and AP.

    ARMOR_COUNT,
    ARMOR_FIRST = 0
} ArmorType;

/**********************************************************************
**	These are the identifiers for the various monochrome debug screens.
*/
typedef enum DMonoType : unsigned char
{
    DMONO_OBJECT,
    DMONO_HOUSE,
    DMONO_STRESS,
    DMONO_EVENTS,

    DMONO_COUNT,
    DMONO_FIRST = 0
} DMonoType;

/*
**	Performance benchmark tracking identifiers.
*/
typedef enum BenchType : unsigned char
{
    BENCH_GAME_FRAME,      // Whole game frame (used for normalizing).
    BENCH_FINDPATH,        // Find path calls.
    BENCH_GREATEST_THREAT, // Greatest threat calculation.
    BENCH_AI,              // Object AI calls.
    BENCH_CELL,            // Cell draw it function.
    BENCH_SIDEBAR,         // Sidebar (just cameo section) drawing.
    BENCH_RADAR,           // Radar map drawing.
    BENCH_TACTICAL,        // Whole tactical map.
    BENCH_PCP,             // Per cell process.
    BENCH_EVAL_OBJECT,     // Evaluate object as potential target.
    BENCH_EVAL_CELL,       // Evaluate entire cell for potential targets.
    BENCH_EVAL_WALL,       // Evaluate wall in cell as potential target.

    BENCH_POWER,          // Power bar drawing.
    BENCH_TABS,           // Tab section (top) drawing.
    BENCH_SHROUD,         // Shroud layer drawing.
    BENCH_ANIMS,          // Animations drawing.
    BENCH_OBJECTS,        // All game object drawing.
    BENCH_PALETTE,        // Color cycling palette adjustments.
    BENCH_GSCREEN_RENDER, // Rendering of the whole map layered system (with blits).
    BENCH_BLIT_DISPLAY,   // DirectX or shadow blit of hidpage to seenpage.
    BENCH_MISSION,        // Mission list processing.

    BENCH_RULES,    // Processing of the rules.ini file.
    BENCH_SCENARIO, // Processing of the scenario.ini file.

    BENCH_COUNT,
    BENCH_FIRST = 0
} BenchType;

#if 0
#define BStart(a)                                                                                                      \
    if (Benches != NULL)                                                                                               \
    Benches[a].Begin()
#define BEnd(a)                                                                                                        \
    if (Benches != NULL)                                                                                               \
    Benches[a].End()
#else
#define BStart(a)
#define BEnd(a)
#endif

/**********************************************************************
**	Working MCGA colors that give a pleasing effect for beveled edges and
**	other purposes.
*/
#define MAGIC_COL_COUNT   13 // Translucent color count.
#define SHADOW_COL_COUNT  4  // Terrain shroud translucent color count.
#define USHADOW_COL_COUNT 1  // Unit shadow special ghost colors.

/**********************************************************************
**	Color cycling range that is used for water effects.
*/
#define CYCLE_COLOR_START (6 * 16)
#define CYCLE_COLOR_COUNT 7

/**********************************************************************
**	Magic color fading pulsing effect limits -- color gun value.
*/
#define CC_PULSE_COLOR 255
#define CC_EMBER_COLOR (CYCLE_COLOR_START + CYCLE_COLOR_COUNT)

/**********************************************************************
**	These are the control flags for Fancy_Text_Print function.
*/
typedef enum TextPrintType : unsigned short
{
    TPF_LASTPOINT = 0x0000,    // Use previous font point value.
    TPF_6POINT = 0x0001,       // Use 6 point font.
    TPF_8POINT = 0x0002,       // Use 8 point font.
    TPF_3POINT = 0x0003,       // Use 3 point font.
    TPF_LED = 0x0004,          // Use LED font.
    TPF_VCR = 0x0005,          // Use VCR font.
    TPF_6PT_GRAD = 0x0006,     // Use 6 point gradient font.
    TPF_MAP = 0x0007,          // Font used for popup help text.
    TPF_METAL12 = 0x0008,      // Use 12 point tab font
    TPF_EFNT = 0x0009,         // Use scenario editor font.
    TPF_TYPE = 0x000A,         // Use teletype font
    TPF_SCORE = 0x000B,        // Use score screen font.
    TPF_LASTSHADOW = 0x0000,   // Use previous font palette.
    TPF_NOSHADOW = 0x0010,     // Don't have any shadow.
    TPF_DROPSHADOW = 0x0020,   //	Use a simple drop shadow.
    TPF_FULLSHADOW = 0x0040,   // Use a full outline shadow.
    TPF_LIGHTSHADOW = 0x0080,  // Use engraved drop 'shadow' color.
    TPF_CENTER = 0x0100,       // Center about the X axis.
    TPF_RIGHT = 0x0200,        // Right justify text.
    TPF_MEDIUM_COLOR = 0x1000, // Use medium color for all text gradient
    TPF_BRIGHT_COLOR = 0x2000, // Use bright color for all text gradient
    TPF_USE_GRAD_PAL = 0x4000  // Use a gradient palette based on fore color
} TextPrintType;

// PG
// inline TextPrintType operator |(TextPrintType, TextPrintType);
// inline TextPrintType operator &(TextPrintType, TextPrintType);
// inline TextPrintType operator ~(TextPrintType);

inline TextPrintType operator|(TextPrintType a, TextPrintType b)
{
    return static_cast<TextPrintType>(static_cast<int>(a) | static_cast<int>(b));
}

inline TextPrintType operator&(TextPrintType a, TextPrintType b)
{
    return static_cast<TextPrintType>(static_cast<int>(a) & static_cast<int>(b));
}

inline TextPrintType operator~(TextPrintType a)
{
    return static_cast<TextPrintType>(~static_cast<int>(a));
}

// Standard button text print flags.
#define TPF_BUTTON  (TPF_CENTER | TPF_6PT_GRAD | TPF_NOSHADOW)
#define TPF_EBUTTON (TPF_CENTER | TPF_EFNT | TPF_NOSHADOW)
#define TPF_TEXT    (TPF_6PT_GRAD | TPF_NOSHADOW)

/**********************************************************************
**	These control the maximum number of objects in the game. Make sure that these
**	maximums never exceed the maximum value for the "ID" element in the
**	object class.
*/
#define BUILDING_MAX 500               // Lasts for hours.
#define HOUSE_MAX    (HOUSE_COUNT + 1) // Lasts entire scenario.
#define INFANTRY_MAX 500               // Lasts for minutes.
#define UNIT_MAX     500               // Lasts for minutes.
#define VESSEL_MAX   100               // Lasts for minutes.
#define TEAMTYPE_MAX 60                // Lasts forever.

// Save filename description.
#define DESCRIP_MAX 44 // 40 chars + CR + LF + CTRL-Z + NULL

#define CONQUER_PATH_MAX 12 // Number of cells to look ahead for movement.

#define EACH_INFANTRY_MAX (INFANTRY_MAX / 5) // Default maximum any one player can have.
#define EACH_UNIT_MAX     (UNIT_MAX / 5)     // Default maximum any one player can have.
#define EACH_BUILDING_MAX (BUILDING_MAX / 5) // Default maximum any one player can build.
#define EACH_VESSEL_MAX   (VESSEL_MAX / 5)   // Default maximum any one player can build.

/**********************************************************************
**	Terrain can be of these different classes. At any point in the game
**	a particular piece of ground must fall under one of these classifications.
**	This is true, even if it is undergoing a temporary transition.
*/
typedef enum LandType : char
{
    LAND_CLEAR,    // "Clear" terrain.
    LAND_ROAD,     // Road terrain.
    LAND_WATER,    // Water.
    LAND_ROCK,     // Impassable rock.
    LAND_WALL,     // Wall (blocks movement).
    LAND_TIBERIUM, // Tiberium field.
    LAND_BEACH,    //	Beach terrain.
    LAND_ROUGH,    // Rocky terrain.
    LAND_RIVER,    // Rocky riverbed.

    LAND_COUNT,
    LAND_NONE = -1,
    LAND_FIRST = 0
} LandType;

/**********************************************************************
**	The theaters of operation are as follows.
*/
typedef enum TheaterType : char
{
    THEATER_NONE = -1,
    THEATER_TEMPERATE,
    THEATER_SNOW,
    THEATER_INTERIOR,

    THEATER_COUNT,
    THEATER_FIRST = 0
} TheaterType;

// inline TheaterType operator++(TheaterType &, int);
inline TheaterType operator++(TheaterType& n)
{
    n = (TheaterType)(((int)n) + 1);
    return n;
}

#define THEATERF_TEMPERATE (1 << THEATER_TEMPERATE)
#define THEATERF_SNOW      (1 << THEATER_SNOW)
#define THEATERF_INTERIOR  (1 << THEATER_INTERIOR)

typedef struct
{
    char Name[16];
    char Root[10];
    char Suffix[4];
} TheaterDataType;

/**********************************************************************
**	Each building has a predetermined size. These are the size numbers.
**	The trailing number is this define is the width and height (respectively)
**	of the building in cells.
*/
typedef enum BSizeType : char
{
    BSIZE_NONE = -1,
    BSIZE_11 = 0,
    BSIZE_21,
    BSIZE_12,
    BSIZE_22,
    BSIZE_23,
    BSIZE_32,
    BSIZE_33,
    BSIZE_42,
    BSIZE_55,

    BSIZE_COUNT
} BSizeType;

inline BSizeType operator++(BSizeType&, int);

/**********************************************************************
** When objects are manipulated on the map that are marked as being
**	removed (up), placed down (down), or just to be redrawn (change);
** or when an object's rendering (not logical) size changes, due to
** its being selected or having an animation attached (overlap up/down).
*/
typedef enum MarkType : unsigned char
{
    MARK_UP,            //	Removed from the map.
    MARK_DOWN,          //	Placed on the map.
    MARK_CHANGE,        //	Altered in place on the map.
    MARK_CHANGE_REDRAW, //	Redraw because of animation change.
    MARK_OVERLAP_DOWN,  // Mark overlap cells on the map
    MARK_OVERLAP_UP     // Clear overlap cells on the map
} MarkType;

/****************************************************************************
**	Window number definition list. Each window should be referred to by
**	the value given in this list.
*/
// Allow window number enums to be passed to library functions.
typedef enum WindowNumberType : unsigned char
{
    WINDOW_MAIN,     // Full screen window.
    WINDOW_ERROR,    // Library error window.
    WINDOW_TACTICAL, // Tactical map window.
    WINDOW_MENU,     // Main selection menu.
    WINDOW_SIDEBAR,  // Sidebar (buildable list) window.
    WINDOW_EDITOR,   // Scenario editor window.
    WINDOW_PARTIAL,  // Partial object draw sub-window.
    WINDOW_CUSTOM,   // Window that can be altered depending on circumstances
    WINDOW_VIRTUAL // Window that is used when we want to capture rendering information without actually rendering. ST -
                   // 1/15/2019 3:03PM
} WindowNumberType;

/****************************************************************************
**	For every cell there are 8 adjacent cells. Use these direction numbers
**	when referring to adjacent cells. This comes into play when moving
**	between cells and in the Desired_Facing() algorithm.
*/
typedef enum FacingType : char
{
    FACING_NONE = -1,
    FACING_N,  // North
    FACING_NE, // North-East
    FACING_E,  // East
    FACING_SE, // South-East
    FACING_S,  // South
    FACING_SW, // South-West
    FACING_W,  // West
    FACING_NW, // North-West

    FACING_COUNT, // Total of 8 directions (0..7).
    FACING_FIRST = 0
} FacingType;

// inline FacingType operator++(FacingType &, int);
inline FacingType operator+(FacingType f1, FacingType f2)
{
    return (FacingType)(((int)f1 + (int)f2) & 0x07);
}
inline FacingType operator+(FacingType f1, int f2)
{
    return (FacingType)(((int)f1 + (int)f2) & 0x07);
}

inline FacingType operator-(FacingType f1, FacingType f2)
{
    return (FacingType)(((int)f1 - (int)f2) & 0x07);
}
inline FacingType operator-(FacingType f1, int f2)
{
    return (FacingType)(((int)f1 - (int)f2) & 0x07);
}

inline FacingType operator+=(FacingType& f1, FacingType f2)
{
    f1 = (FacingType)(((int)f1 + (int)f2) & 0x07);
    return (f1);
}
inline FacingType operator+=(FacingType& f1, int f2)
{
    f1 = (FacingType)(((int)f1 + (int)f2) & 0x07);
    return (f1);
}

inline int operator*(FacingType f1, FacingType f2)
{
    return ((int)f1 * (int)f2);
}

#ifdef NEVER
typedef enum DirType
{
    DIR_MIN = 0,
    DIR_N = 0,
    DIR_NE = 1 << 5,
    DIR_E = 2 << 5,
    DIR_SE = 3 << 5,
    DIR_S = 4 << 5,
    DIR_SW = 5 << 5,
    DIR_SW_X1 = (5 << 5) - 8,  // Direction of harvester while unloading.
    DIR_SW_X2 = (5 << 5) - 16, // Direction of harvester while unloading.
    DIR_W = 6 << 5,
    DIR_NW = 7 << 5,
    DIR_MAX = 255
} DirType;
inline DirType operator+(DirType f1, DirType f2)
{
    return (DirType)(((int)f1 + (int)f2) & 0x00FF);
}
inline DirType operator+(DirType f1, int f2)
{
    return (DirType)(((int)f1 + (int)f2) & 0x00FF);
}
#endif
#define DIR_SW_X1 DirType((5 << 5) - 8)
#define DIR_SW_X2 DirType((5 << 5) - 16)

/****************************************************************************
**	Timer constants. These are used when setting the countdown timer.
**	Note that this is based upon a timer that ticks every 60th of a second.
*/
#define TIMER_SECOND 60
#define TIMER_MINUTE (TIMER_SECOND * 60)

#define FADE_PALETTE_FAST   (TIMER_SECOND / 8)
#define FADE_PALETTE_MEDIUM (TIMER_SECOND / 4)
#define FADE_PALETTE_SLOW   (TIMER_SECOND / 2)

#define TICKS_PER_SECOND 15
#define TICKS_PER_MINUTE (TICKS_PER_SECOND * 60)
#define TICKS_PER_HOUR   (TICKS_PER_MINUTE * 60)

#define GRAYFADETIME (1 * TICKS_PER_SECOND)

/****************************************************************************
** Each vehicle is give a speed rating. This is a combination of not only
**	its physical speed, but the means by which it travels (wheels, tracks,
**	wings, etc). This is used to determine the movement table.
*/
typedef enum SpeedType : char
{
    SPEED_NONE = -1,

    SPEED_FOOT,   // Bipedal.
    SPEED_TRACK,  // Tracked locomotion.
    SPEED_WHEEL,  // Balloon tires.
    SPEED_WINGED, // Lifter's, 'thopters, and rockets.
    SPEED_FLOAT,  // Ships.
    SPEED_HOVER,  // Hover craft (TS-spike): amphibious ground locomotor — passable on land AND water, blocked by rock/wall. TD had this slot; RA dropped it. Appended so existing indices keep their values.

    SPEED_COUNT,
    SPEED_FIRST = SPEED_FOOT
} SpeedType;

/**********************************************************************
**	These are the sound effect digitized sample file names.
*/
typedef enum VocType : short
{
    VOC_NONE = -1,

    VOC_GIRL_OKAY, // "okay"
    VOC_GIRL_YEAH, // "yeah?"
    VOC_GUY_OKAY,  //	"okay"
    VOC_GUY_YEAH,  // "yeah?"

    VOC_MINELAY1,   // mine layer sound
    VOC_ACKNOWL,    //	"acknowledged"
    VOC_AFFIRM,     //	"affirmative"
    VOC_AWAIT,      //	"awaiting orders"
    VOC_ENG_AFFIRM, // Engineer: "affirmative"
    VOC_ENG_ENG,    // Engineer: "engineering"
    VOC_NO_PROB,    //	"not a problem"
    VOC_READY,      //	"ready and waiting"
    VOC_REPORT,     //	"reporting"
    VOC_RIGHT_AWAY, //	"right away sir"
    VOC_ROGER,      //	"roger"
    VOC_UGOTIT,     //	"you got it"
    VOC_VEHIC,      //	"vehicle reporting"
    VOC_YESSIR,     //	"yes sir"

    VOC_SCREAM1,  //	short infantry scream
    VOC_SCREAM3,  //	short infantry scream
    VOC_SCREAM4,  //	short infantry scream
    VOC_SCREAM5,  //	short infantry scream
    VOC_SCREAM6,  //	short infantry scream
    VOC_SCREAM7,  //	short infantry scream
    VOC_SCREAM10, //	short infantry scream
    VOC_SCREAM11, //	short infantry scream
    VOC_YELL1,    //	long infantry scream

    VOC_CHRONO,  //	Chronosphere sound.
    VOC_CANNON1, // Cannon sound (medium).
    VOC_CANNON2, // Cannon sound (short).
    VOC_IRON1,
    VOC_ENG_MOVEOUT, // Engineer: "movin' out"
    VOC_SONAR,       // sonar pulse
    VOC_SANDBAG,     // sand bag crunch
    VOC_MINEBLOW,
    VOC_CHUTE1,       // wind swoosh sound
    VOC_DOG_BARK,     // dog bark
    VOC_DOG_WHINE,    // dog whine
    VOC_DOG_GROWL2,   // strong dog growl
    VOC_FIRE_LAUNCH,  // fireball launch sound
    VOC_FIRE_EXPLODE, // fireball explode sound
    VOC_GRENADE_TOSS, // grenade toss
    VOC_GUN_5,        // 5 round gun burst (slow).
    VOC_GUN_7,        // 7 round gun burst (fast).
    VOC_ENG_YES,      // Engineer: "yes sir"
    VOC_GUN_RIFLE,    // Rifle shot.
    VOC_HEAL,         // Healing effect.
    VOC_DOOR,         // Hyrdrolic door.
    VOC_INVULNERABLE, // Invulnerability effect.
    VOC_KABOOM1,      // Long explosion (muffled).
    VOC_KABOOM12,     // Very long explosion (muffled).
    VOC_KABOOM15,     // Very long explosion (muffled).
    VOC_SPLASH,       // Water splash
    VOC_KABOOM22,     // Long explosion (sharp).
    VOC_AACANON3,     // AA-Cannon
    VOC_TANYA_DIE,    // Tanya: scream
    VOC_GUN_5F,       // 5 round gun burst (fast).
    VOC_MISSILE_1,    // Missile with high tech effect.
    VOC_MISSILE_2,    // Long missile launch.
    VOC_MISSILE_3,    // Short missile launch.
    VOC_x6,
    VOC_GUN_5R,              // 5 round gun burst (rattles).
    VOC_BEEP,                // Generic beep sound.
    VOC_CLICK,               //	Generic click sound.
    VOC_SILENCER,            // Silencer.
    VOC_CANNON6,             // Long muffled cannon shot.
    VOC_CANNON7,             // Sharp mechanical cannon fire.
    VOC_TORPEDO,             // Torpedo launch.
    VOC_CANNON8,             // Sharp cannon fire.
    VOC_TESLA_POWER_UP,      // Hum charge up.
    VOC_TESLA_ZAP,           // Tesla zap effect.
    VOC_SQUISH,              // Squish effect.
    VOC_SCOLD,               // Scold bleep.
    VOC_RADAR_ON,            // Powering up electronics.
    VOC_RADAR_OFF,           // B movie power down effect.
    VOC_PLACE_BUILDING_DOWN, // Building slam down sound.
    VOC_KABOOM30,            // Short explosion (HE).
    VOC_KABOOM25,            // Short growling explosion.
    VOC_x7,
    VOC_DOG_HURT,         //	Dog whine.
    VOC_DOG_YES,          // Dog 'yes sir'.
    VOC_CRUMBLE,          // Building crumble.
    VOC_MONEY_UP,         // Rising money tick.
    VOC_MONEY_DOWN,       // Falling money tick.
    VOC_CONSTRUCTION,     // Building construction sound.
    VOC_GAME_CLOSED,      // Long bleep.
    VOC_INCOMING_MESSAGE, // Soft happy warble.
    VOC_SYS_ERROR,        // Sharp soft warble.
    VOC_OPTIONS_CHANGED,  // Mid range soft warble.
    VOC_GAME_FORMING,     // Long warble.
    VOC_PLAYER_LEFT,      // Chirp sequence.
    VOC_PLAYER_JOINED,    // Reverse chirp sequence.
    VOC_DEPTH_CHARGE,     // Distant explosion sound.
    VOC_CASHTURN,         // Airbrake.

    VOC_TANYA_CHEW,  // Tanya: "Chew on this"
    VOC_TANYA_ROCK,  // Tanya: "Let's rock"
    VOC_TANYA_LAUGH, // Tanya: "ha ha ha"
    VOC_TANYA_SHAKE, // Tanya: "Shake it baby"
    VOC_TANYA_CHING, // Tanya: "Cha Ching"
    VOC_TANYA_GOT,   // Tanya: "That's all you got"
    VOC_TANYA_KISS,  // Tanya: "Kiss it bye bye"
    VOC_TANYA_THERE, // Tanya: "I'm there"
    VOC_TANYA_GIVE,  // Tanya: "Give it to me"
    VOC_TANYA_YEA,   // Tanya: "Yea?"
    VOC_TANYA_YES,   // Tanya: "Yes sir?"
    VOC_TANYA_WHATS, // Tanya: "What's up."
    VOC_WALLKILL2,   // Crushing wall sound.
    VOC_x8,
    VOC_TRIPLE_SHOT, // Three quick shots in succession.
    VOC_SUBSHOW,     // Submarine surfacing.
    VOC_E_AH,        // Einstein "ah"
    VOC_E_OK,        // Einstein "ok"
    VOC_E_YES,       // Einstein "yes"
    VOC_TRIP_MINE,   // mine explosion sound

    VOC_SPY_COMMANDER, // Spy: "commander?"
    VOC_SPY_YESSIR,    // Spy: "yes sir"
    VOC_SPY_INDEED,    // Spy: "indeed"
    VOC_SPY_ONWAY,     // Spy: "on my way"
    VOC_SPY_KING,      // Spy: "for king and country"
    VOC_MED_REPORTING, // Medic: "reporting"
    VOC_MED_YESSIR,    // Medic: "yes sir"
    VOC_MED_AFFIRM,    // Medic: "affirmative"
    VOC_MED_MOVEOUT,   // Medic: "movin' out"
    VOC_BEEP_SELECT,   // map selection beep

    VOC_THIEF_YEA, // Thief: "yea?"

#ifdef FIXIT_ANTS
    VOC_ANTDIE,
    VOC_ANTBITE,
#else
    VOC_x9,
    VOC_x10,
#endif

    VOC_THIEF_MOVEOUT, // Thief: "movin' out"
    VOC_THIEF_OKAY,    // Thief: "ok"
    VOC_x11,
    VOC_THIEF_WHAT,   // Thief: "what"
    VOC_THIEF_AFFIRM, // Thief: "affirmative"

    VOC_STAVCMDR,
    VOC_STAVCRSE,
    VOC_STAVYES,
    VOC_STAVMOV,
    VOC_BUZZY1,
    VOC_RAMBO1,
    VOC_RAMBO2,
    VOC_RAMBO3,

#ifdef FIXIT_CSII //	checked - ajw 9/28/98
    VOC_MECHYES1,
    VOC_MECHHOWDY1,
    VOC_MECHRISE1,
    VOC_MECHHUH1,
    VOC_MECHHEAR1,
    VOC_MECHLAFF1,
    VOC_MECHBOSS1,
    VOC_MECHYEEHAW1,
    VOC_MECHHOTDIG1,
    VOC_MECHWRENCH1,
    VOC_STBURN1,
    VOC_STCHRGE1,
    VOC_STCRISP1,
    VOC_STDANCE1,
    VOC_STJUICE1,
    VOC_STJUMP1,
    VOC_STLIGHT1,
    VOC_STPOWER1,
    VOC_STSHOCK1,
    VOC_STYES1,

    VOC_CHRONOTANK1,
    VOC_MECH_FIXIT1,
    VOC_MAD_CHARGE,
    VOC_MAD_EXPLODE,
    VOC_SHOCK_TROOP1,

    VOC_BEACON,

#endif

    // Tiberian Factions mod sounds — TD assets re-registered under TD-prefixed
    // VOC enum values so we never alias vanilla RA Report= references. Each
    // maps to a TD .AUD asset name in SoundEffectName[] (audio.cpp).
    VOC_TD_ROCKET2,      // TD rocket launch (light, for TOW_TWO / TOMAHAWK / NIKE)
    VOC_TD_TANK4,        // TD big gun tank fire (TURRET_GUN / 120MM)
    VOC_TD_LASER,        // Obelisk humming laser beam
    VOC_TD_LASER_POWER,  // Obelisk laser warming-up sound
    VOC_TD_CONSTRUCTION, // TD building construction loop (CONSTRU2.AUD)
    VOC_TD_MINI,         // TD chain-gun burst (GUN8 — CHAIN_GUN / TDGTWR)
    VOC_TD_ION1,         // TD Ion Cannon beam-strike SFX (ION1 — ANIM_TD_ION_CANNON)
    VOC_TD_MOVEOUT,      // TD infantry "movin' out" (MOVOUT1) — GDI/Nod move-order voice
    VOC_TD_UNIT1,        // TD "unit reporting" (UNIT1) — GDI/Nod vehicle select voice (radio take)
    VOC_TD_PLACE_BUILDING_DOWN, // TD building slam-down (HVYDOOR1) — GDI/Nod placement, replaces RA's PLACBLDG
    VOC_TD_M16,          // TD Minigunner M-16 triple burst (MGUN2) — WEAPON_TDM16 Report=
    VOC_TD_TOSS,         // TD grenade toss (TOSS1) — WEAPON_TDGRENADE Report=
    VOC_TD_BAZOOKA,      // TD Rocket Soldier launch (BAZOOK1) — WEAPON_TDDRAGON Report=
    VOC_TD_FLAMER,       // TD Flamethrower (FLAMER2) — WEAPON_TDFLAME Report= (TD VOC_FLAMER1 maps to file FLAMER2)
    VOC_TD_SNIPER,       // TD Commando silenced rifle (RAMGUN2) — WEAPON_TDRIFLE Report=
    // TD Commando (RMBO) one-liners — single-take CMD voices (IN_NOVAR), routed via
    // RAC/RAR_SFX_TD<NAME> in SFXEVENTSLOCALIZED.XML -> base TDC/TDR_SFX_CMD_<NAME>_EN-US.
    // Fired by InfantryClass::Response_Select/Move/Attack for INFANTRY_TDRMBO.
    VOC_TD_CMD_BOMBIT,   // "I've got a present for ya" (BOMBIT1)
    VOC_TD_CMD_CMON,     // "c'mon" (CMON1)
    VOC_TD_CMD_GOTIT,    // "you got it" (GOTIT1)
    VOC_TD_CMD_KEEPEM,   // "keep 'em comin'" (KEEPEM1)
    VOC_TD_CMD_LAUGH,    // "hahaha" (LAUGH1)
    VOC_TD_CMD_LEFTY,    // "that was left handed" (LEFTY1)
    VOC_TD_CMD_NOPROB,   // "no problem" (NOPRBLM1)
    VOC_TD_CMD_ONIT,     // "I'm on it" (ONIT1)
    VOC_TD_CMD_YELL,     // "ahhhhh" (RAMYELL1)
    VOC_TD_CMD_ROCK,     // "time to rock and roll" (ROKROLL1)
    VOC_TD_CMD_TUFF,     // "real tough guy" (TUFFGUY1)
    VOC_TD_CMD_YEAH,     // "yea" (YEAH1)
    VOC_TD_CMD_YES,      // "yes" (YES1)
    VOC_TD_CMD_YO,       // "yo" (YO1)
    VOC_TD_TANK3,        // TD sharp tank fire (TNKFIRE4) — WEAPON_TD105MM Report= (Medium Tank cannon)
    VOC_TD_XPLOBIG6,     // TD big explosion (XPLOBIG6) — ANIM_TDFRAG2 detonation sound
    VOC_TD_TANK2,        // TD sharp tank fire (TNKFIRE3) — WEAPON_TD75MM Report= (Light Tank cannon)
    VOC_TD_ROCKET1,      // TD rocket launch #1 (ROCKET1) — WEAPON_TDTUSK Report= (Mammoth Tusk AA missiles)
    VOC_TD_MGUN11,       // TD heavy machine gun (MGUN11) — WEAPON_TDM60MG Report= (Hum-vee/Buggy); routed via RAC/RAR_SFX_MGUN11
    VOC_TD_CLOAK,        // TD Stealth Tank cloak/decloak (TRANS1) — TD VOC_CLOAK; played by Do_Cloak/Do_Uncloak for TD-prefix units instead of RA's VOC_IRON1. Routed via RAC/RAR_SFX_TRANS1.
    VOC_TD_TANK1,        // TD Artillery 155mm fire (TNKFIRE2) — WEAPON_TD155MM Report= (VOC_TANK1 "sharp tank fire with recoil"). Routed via RAC/RAR_SFX_TNKFIRE2.
    VOC_TS_HOVRMIS1,     // TS Hover MLRS missile launch (HOVRMIS1, decoded from TS SOUNDS.MIX AUD) — WEAPON_TSHOVERMISSILE Report=. Routed via RAC/RAR_SFX_HOVRMIS1 + bundled TSHOVRMIS1.WAV.

    VOC_COUNT,
    VOC_FIRST = 0
} VocType;

/*
**	EVA voices are specified by these identifiers.
*/
// Tiberian Factions: backing type bumped char -> short so we can hold the
// extra VOX_TD_* entries (TD EVA bulk port pushes the enum past 127).
typedef enum VoxType : short
{
    VOX_NONE = -1,
    VOX_ACCOMPLISHED,        //	mission accomplished
    VOX_FAIL,                //	your mission has failed
    VOX_NO_FACTORY,          //	unable to comply, building in progress
    VOX_CONSTRUCTION,        //	construction complete
    VOX_UNIT_READY,          // unit ready
    VOX_NEW_CONSTRUCT,       //	new construction options
    VOX_DEPLOY,              //	cannot deploy here
    VOX_STRUCTURE_DESTROYED, // structure destroyed
    VOX_INSUFFICIENT_POWER,  // insufficient power
    VOX_NO_CASH,             //	insufficient funds
    VOX_CONTROL_EXIT,        //	battle control terminated
    VOX_REINFORCEMENTS,      //	reinforcements have arrived
    VOX_CANCELED,            //	canceled
    VOX_BUILDING,            //	building
    VOX_LOW_POWER,           //	low power
    VOX_NEED_MO_MONEY,       //	need more funds
    VOX_BASE_UNDER_ATTACK,   //	our base is under attack
    VOX_UNABLE_TO_BUILD,     //	unable to build more
    VOX_PRIMARY_SELECTED,    //	primary building selected
#ifdef ENGLISH
    VOX_MADTANK_DEPLOYED, // M.A.D. Tank Deployed
#else
    VOX_none3,
#endif
    VOX_none4,
    VOX_UNIT_LOST,        //	unit lost
    VOX_SELECT_TARGET,    // select target
    VOX_PREPARE,          //	enemy approaching
    VOX_NEED_MO_CAPACITY, //	silos needed
    VOX_SUSPENDED,        //	on hold
    VOX_REPAIRING,        //	repairing
    VOX_none5,
    VOX_none6,
    VOX_AIRCRAFT_LOST,
    VOX_none7,
    VOX_ALLIED_FORCES_APPROACHING,
    VOX_ALLIED_APPROACHING,
    VOX_none8,
    VOX_none9,
    VOX_BUILDING_INFILTRATED,
    VOX_CHRONO_CHARGING,
    VOX_CHRONO_READY,
    VOX_CHRONO_TEST,
    VOX_HQ_UNDER_ATTACK,
    VOX_CENTER_DEACTIVATED,
    VOX_CONVOY_APPROACHING,
    VOX_CONVOY_UNIT_LOST,
    VOX_EXPLOSIVE_PLACED,
    VOX_MONEY_STOLEN,
    VOX_SHIP_LOST,
    VOX_SATALITE_LAUNCHED,
    VOX_SONAR_AVAILABLE,
    VOX_none10,
    VOX_SOVIET_FORCES_APPROACHING,
    VOX_SOVIET_REINFORCEMENTS,
    VOX_TRAINING,
    VOX_ABOMB_READY,
    VOX_ABOMB_LAUNCH,
    VOX_ALLIES_N,
    VOX_ALLIES_S,
    VOX_ALLIES_E,
    VOX_ALLIES_W,
    VOX_OBJECTIVE1,
    VOX_OBJECTIVE2,
    VOX_OBJECTIVE3,
    VOX_IRON_CHARGING,
    VOX_IRON_READY,
    VOX_RESCUED,
    VOX_OBJECTIVE_NOT,
    VOX_SIGNAL_N,
    VOX_SIGNAL_S,
    VOX_SIGNAL_E,
    VOX_SIGNAL_W,
    VOX_SPY_PLANE,
    VOX_FREED,
    VOX_UPGRADE_ARMOR,
    VOX_UPGRADE_FIREPOWER,
    VOX_UPGRADE_SPEED,
    VOX_MISSION_TIMER,
    VOX_UNIT_FULL,
    VOX_UNIT_REPAIRED,
    VOX_TIME_40,
    VOX_TIME_30,
    VOX_TIME_20,
    VOX_TIME_10,
    VOX_TIME_5,
    VOX_TIME_4,
    VOX_TIME_3,
    VOX_TIME_2,
    VOX_TIME_1,
    VOX_TIME_STOP,
    VOX_UNIT_SOLD,
    VOX_TIMER_STARTED,
    VOX_TARGET_RESCUED,
    VOX_TARGET_FREED,
    VOX_TANYA_RESCUED,
    VOX_STRUCTURE_SOLD,
    VOX_SOVIET_FORCES_FALLEN,
    VOX_SOVIET_SELECTED,
    VOX_SOVIET_EMPIRE_FALLEN,
    VOX_OPERATION_TERMINATED,
    VOX_OBJECTIVE_REACHED,
    VOX_OBJECTIVE_NOT_REACHED,
    VOX_OBJECTIVE_MET,
    VOX_MERCENARY_RESCUED,
    VOX_MERCENARY_FREED,
    VOX_KOSOYGEN_FREED,
    VOX_FLARE_DETECTED,
    VOX_COMMANDO_RESCUED,
    VOX_COMMANDO_FREED,
    VOX_BUILDING_IN_PROGRESS,
    VOX_ATOM_PREPPING,
    VOX_ALLIED_SELECTED,
    VOX_ABOMB_PREPPING,
    VOX_ATOM_LAUNCHED,
    VOX_ALLIED_FORCES_FALLEN,
    VOX_ABOMB_AVAILABLE,
    VOX_ALLIED_REINFORCEMENTS,
    VOX_SAVE1,
    VOX_LOAD1,

    // Tiberian Factions mod — TD EVA voices. Routing pattern (validated
    // by pilot 2026-05-26): TD-prefixed engine name (e.g. "TDIONCHRG1") is
    // sent via On_Speech; mod-side SFXEVENTSLOCALIZED.XML registers
    // RAC_SFX_TD<NAME> / RAR_SFX_TD<NAME> -> TDC_SFX_EVA_<NAME>_EN-US.MP3 /
    // TDR_SFX_EVA_<NAME>_EN-US.MP3 (existing assets in SFX2D_EN-US.MEG).
    //
    // The VOX_TD_* entries below are for TD-only events that have no RA
    // semantic equivalent — they're invoked directly by TD-port code
    // (e.g. TDEYE -> Speak(VOX_TD_ION_CHARGING)). Shared semantic events
    // (CONSTRUCTION, UNIT_READY, etc.) keep their existing VOX_* slot
    // and swap to TD via the SpeechTD[] side-conditional table in
    // audio.cpp + dllinterface.cpp On_Speech dispatch.
    //
    // Per session 2026-05-26: GDI + Nod share TD EVA for now; structure
    // leaves room for a separate Nod voice via a parallel SpeechNOD[]
    // table when needed.
    VOX_TD_DEAD_GDI,
    VOX_TD_DEAD_NOD,
    VOX_TD_DEAD_CIV,
    VOX_TD_INCOMING_MISSILE,
    VOX_TD_ENEMY_PLANES,
    VOX_TD_INCOMING_NUKE,
    VOX_TD_NOD_CAPTURED,
    VOX_TD_GDI_CAPTURED,
    VOX_TD_ION_CHARGING,
    VOX_TD_ION_READY,
    VOX_TD_NUKE_AVAILABLE,
    VOX_TD_NUKE_LAUNCHED,
    VOX_TD_STRUCTURE_LOST,
    VOX_TD_NEED_HARVESTER,
    VOX_TD_AIRSTRIKE_READY,
    VOX_TD_NOT_READY,
    VOX_TD_ENEMY_STRUCTURE,
    VOX_TD_GDI_STRUCTURE,
    VOX_TD_NOD_STRUCTURE,
    VOX_TD_ENEMY_UNIT,

    VOX_COUNT,
    VOX_FIRST = 0
} VoxType;

/****************************************************************************
**	Game reinforcements are each controlled by the following structure. The
**	data originates in the scenario INI file but is then carried throughout
**	any saved games.
*/
typedef enum SourceType : char
{
    SOURCE_NONE = -1, // No defined source (error condition).
    SOURCE_NORTH,     // From north edge.
    SOURCE_EAST,      // From east edge.
    SOURCE_SOUTH,     // From south edge.
    SOURCE_WEST,      // From west edge.
    SOURCE_AIR,       // Dropped by air (someplace).

    SOURCE_COUNT,
    SOURCE_FIRST = 0
} SourceType;

#include "common/remapcontrol.h"

/****************************************************************************
**	Each type of terrain has certain characteristics. These are indicated
**	by the structure below. For every element of terrain there is a
**	corresponding GroundType structure.
*/
typedef struct
{
    fixed Cost[SPEED_COUNT]; // Terrain effect cost (normal).
    bool Build;              // Can build on this terrain?
} GroundType;

/**************************************************************************
**	Find_Path returns with a pointer to this structure.
*/
typedef struct
{
    CELL Start;            // Starting cell number.
    int Cost;              // Accumulated terrain cost.
    int Length;            // Command string length.
    FacingType* Command;   // Pointer to command string.
    unsigned int* Overlap; // Pointer to overlap list
    CELL LastOverlap;      // stores position of last overlap
    CELL LastFixup;        // stores position of last overlap
} PathType;

/**********************************************************************
** These are special indices into the Waypoint array; slots 0-25 are
** reserved for letter-designated Waypoints, the others are special.
*/
typedef enum WaypointEnum : unsigned char
{
    WAYPT_HOME = 98, // Home-cell for this scenario
    WAYPT_REINF,     // cell where reinforcements arrive
    WAYPT_SPECIAL,   // Used by special airdrop reinforcements.
    WAYPT_COUNT
} WaypointType;

/****************************************************************************
**	This is the max number of events supported on one frame.
*/
#define MAX_EVENTS 256

/*
** New Config structure for .CFG files
*/
typedef struct
{
    unsigned DigitCard;     // SoundCardType.
    unsigned Port;          // SoundCardType.
    unsigned IRQ;           // SoundCardType.
    unsigned DMA;           // SoundCardType.
    unsigned BitsPerSample; // bits per sound sample
    unsigned Channels;      // stereo/mono sound card
    unsigned Speed;         // stereo/mono sound card
    bool Reverse;           // Reverse left/right speakers
    char Language[4];
} NewConfigType;

/****************************************************************************
**	These are the types of dialogs that can pop up outside of the main loop,
** an call the game in the background.
*/
typedef enum : unsigned char
{
    SDLG_NONE,
    SDLG_OPTIONS,
    SDLG_SURRENDER,
    SDLG_SPECIAL
} SpecialDialogType;

typedef enum : unsigned char
{
    CC_MOUSE_COLOR = 16
} CCPaletteType;

/****************************************************************************
**	These specify the shape numbers in the OPTIONS.SHP file. These shapes
**	are used to dress up the dialog boxes. Many of these shapes come in pairs.
**	For dialog box shapes, they are left image / right image paired. For buttons,
**	they are up / down paired.
*/
typedef enum OptionControlType : char
{
    OPTION_NONE = -1,         // No fancy shmancy shape.
    OPTION_DIALOG = 0,        // Small dialog boxes.
    OPTION_CONTROLS = 2,      // Large dialog boxes, game controls.
    OPTION_DELETE = 4,        // Delete,Load,Save game.
    OPTION_SERIAL = 6,        // Serial dialog.
    OPTION_PHONE = 8,         // Phone dialog.
    OPTION_VISUAL = 10,       // Visual dialog.
    OPTION_NETWORK = 12,      // Network dialog.
    OPTION_JOIN_NETWORK = 14, // Join network dialog.
    OPTION_SOUND = 16,        // Sound controls.

    OPTION_COUNT
} OptionControlType;

/****************************************************************************
**	Used to store firing data for a unit.
*/
typedef struct
{
    COORDINATE Center;
    int Distance;
} FireDataType;

#define size_of(typ, id) sizeof(((typ*)0)->id)

#define MAX_LOG_LEVEL 10

// Maximum number of multi players possible.
#define MAX_PLAYERS 8 // max # of players we can have

// Maximum number of teams
#define MAX_TEAMS 10

#endif