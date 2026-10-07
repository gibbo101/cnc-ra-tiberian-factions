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

/* $Header: /CounterStrike/BDATA.CPP 2     3/03/97 10:37p Joe_bostic $ */
/***********************************************************************************************
 ***              C O N F I D E N T I A L  ---  W E S T W O O D  S T U D I O S               ***
 ***********************************************************************************************
 *                                                                                             *
 *                 Project Name : Command & Conquer                                            *
 *                                                                                             *
 *                    File Name : BDATA.CPP                                                    *
 *                                                                                             *
 *                   Programmer : Joe L. Bostic                                                *
 *                                                                                             *
 *                   Start Date : September 10, 1993                                           *
 *                                                                                             *
 *                  Last Update : October 2, 1996 [JLB]                                        *
 *                                                                                             *
 *---------------------------------------------------------------------------------------------*
 * Functions:                                                                                  *
 *   BuildingTypeClass::As_Reference -- Fetches reference to the building type specified.      *
 *   BuildingTypeClass::Bib_And_Offset -- Determines the bib and appropriate cell offset.      *
 *   BuildingTypeClass::BuildingTypeClass -- This is the constructor for the building types.   *
 *   BuildingTypeClass::Coord_Fixup -- Adjusts coordinate to be legal for assignment.          *
 *   BuildingTypeClass::Cost_Of -- Fetches the cost of this building.                          *
 *   BuildingTypeClass::Create_And_Place -- Creates and places a building object onto the map. *
 *   BuildingTypeClass::Create_One_Of -- Creates a building of this type.                      *
 *   BuildingTypeClass::Dimensions -- Fetches the pixel dimensions of the building.            *
 *   BuildingTypeClass::Display -- Renders a generic view of building.                         *
 *   BuildingTypeClass::Flush_For_Placement -- Tries to clear placement area for this building *
 *   BuildingTypeClass::Full_Name -- Fetches the name to give this building.                   *
 *   BuildingTypeClass::Height -- Determines the height of the building in icons.              *
 *   BuildingTypeClass::Init -- Performs theater specific initialization.                      *
 *   BuildingTypeClass::Init_Anim -- Initialize an animation control for a building.           *
 *   BuildingTypeClass::Init_Heap -- Initialize the heap as necessary for the building type obj*
 *   BuildingTypeClass::Max_Pips -- Determines the maximum pips to display.                    *
 *   BuildingTypeClass::Occupy_List -- Fetches the occupy list for the building.               *
 *   BuildingTypeClass::One_Time -- Performs special one time action for buildings.            *
 *   BuildingTypeClass::Overlap_List -- Fetches the overlap list for the building.             *
 *   BuildingTypeClass::Prep_For_Add -- Prepares scenario editor for adding an object.         *
 *   BuildingTypeClass::Raw_Cost -- Fetches the raw (base) cost of this building type.         *
 *   BuildingTypeClass::Read_INI -- Fetch building type data from the INI database.            *
 *   BuildingTypeClass::Width -- Determines width of building in icons.                        *
 *   BuildingTypeClass::operator delete -- Deletes a building type object from the special heap*
 *   BuildingTypeClass::operator new -- Allocates a building type object from the special heap.*
 * - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

#include "function.h"
#include "keyframe.h"

#define FATSHIP

#define MCW MAP_CELL_W

#define XYCELL(x, y) (y * MAP_CELL_W + x)
// TS war factory door seats (ClassTsWeap, ClassTsDweap).
#include "tsweap_exit_seats.inc"
static short const ExitPyle[] = {XYCELL(1, 2),
                                 XYCELL(2, 2),
                                 XYCELL(0, 2),
                                 XYCELL(-1, 2),
                                 XYCELL(-1, -1),
                                 XYCELL(0, -1),
                                 XYCELL(1, -1),
                                 XYCELL(2, -1),
                                 XYCELL(2, -1),
                                 XYCELL(-1, 0),
                                 XYCELL(2, 0),
                                 XYCELL(2, 1),
                                 XYCELL(-1, 1),
                                 REFRESH_EOL};

// TS Barracks: the entrance steps come down the east column's south face, so a soldier
// walks straight out into the cell two rows down before trying the neighbours.
static short const ExitTsPile[] = {XYCELL(1, 2),
                                   XYCELL(0, 2),
                                   XYCELL(2, 2),
                                   XYCELL(-1, 2),
                                   XYCELL(-1, 1),
                                   XYCELL(2, 1),
                                   XYCELL(-1, 0),
                                   XYCELL(2, 0),
                                   XYCELL(0, -1),
                                   XYCELL(1, -1),
                                   XYCELL(-1, -1),
                                   XYCELL(2, -1),
                                   REFRESH_EOL};

static short const ExitSub[] = {XYCELL(0, 2), XYCELL(2, 2), XYCELL(-1, 2), XYCELL(1, 2), XYCELL(3, 2)};

static short const ExitWeap[] =
    {XYCELL(1, 2), XYCELL(-1, 3), XYCELL(0, 3), XYCELL(1, 3), XYCELL(-2, 3), XYCELL(2, 3), REFRESH_EOL};

static short const ComList[] = {0, 1, MCW, MCW + 1, REFRESH_EOL};
static short const List000111111[] =
    {(MCW * 1), (MCW * 1) + 1, (MCW * 1) + 2, (MCW * 2), (MCW * 2) + 1, (MCW * 2) + 2, REFRESH_EOL};
static short const List0010[] = {MCW, REFRESH_EOL};
static short const List0011[] = {(MCW * 1), (MCW * 1) + 1, REFRESH_EOL};
static short const List010111100[] = {1, (MCW * 1), (MCW * 1) + 1, (MCW * 1) + 2, (MCW * 2), REFRESH_EOL};
static short const List0111[] = {1, (MCW * 1), (MCW * 1) + 1, REFRESH_EOL};
static short const List1000[] = {0, REFRESH_EOL};
static short const List101000011[] = {0, 2, (MCW * 2) + 1, (MCW * 2) + 2, REFRESH_EOL};
/* TSPROC (4x3): the umbrella stands on the west half of the south two rows, so those four cells block.
** The north row is headroom units walk behind (the stacks and the back of the deck rise into it); the dock
** pad (2,1), the east column and the lane mouth (2,2) stay open for the harvesters. The placement list
** (Occupy_List with placement) still claims the whole 4x3. */
static short const TsProcList[] = {(MCW * 1), (MCW * 1) + 1, (MCW * 2), (MCW * 2) + 1, REFRESH_EOL};
static short const TsProcOList[] = {
    0, 1, 2, 3, MCW + 2, MCW + 3, (MCW * 2) + 2, (MCW * 2) + 3, REFRESH_EOL};
/*
**	The TS war factories, 3x3: RA's war factory slot. The hall fills rows 0-1 and row 2 is walkable concrete
**	with the door's lane down its middle. The art reaches a little past the slot (the shadow east, debris
**	west when damaged, the roof and the build-up's raised poles into the row behind), and over row 2.
*/
static short const TsWeap3List[] = {0, 1, 2, MCW, MCW + 1, MCW + 2, REFRESH_EOL};
static short const TsWeap3OList[] = {-MCW - 1, -MCW, -MCW + 1, -MCW + 2, -MCW + 3,
                                     -1, 3, MCW - 1, MCW + 3,
                                     (MCW * 2) - 1, (MCW * 2), (MCW * 2) + 1, (MCW * 2) + 2, (MCW * 2) + 3,
                                     REFRESH_EOL};
/*
**	Units leave straight south down the lane to the bottom-middle cell, then spread across the row
**	south of the plot.
*/
static short const TsWeap3Exit[] = {XYCELL(1, 2), XYCELL(1, 3), XYCELL(0, 3), XYCELL(2, 3),
                                    XYCELL(0, 2), XYCELL(2, 2), REFRESH_EOL};

static short const List1100[] = {0, 1, REFRESH_EOL};
static short const List1101[] = {0, 1, (MCW * 1) + 1, REFRESH_EOL};
static short const List11[] = {0, 1, REFRESH_EOL};
static short const List12[] = {MCW, REFRESH_EOL};
static short const List1[] = {0, REFRESH_EOL};
static short const List21[] = {0, 1, REFRESH_EOL};
static short const List31[] = {0, 1, 2, REFRESH_EOL};
static short const List13[] = {0, MCW, MCW * 2, REFRESH_EOL};
static short const List22[] = {0, 1, MCW, MCW + 1, REFRESH_EOL};
static short const List22_0011[] = {MCW, MCW + 1, REFRESH_EOL};
static short const List22_1100[] = {0, 1, REFRESH_EOL};
static short const List2[] = {0, 1, MCW + 1, MCW, REFRESH_EOL};
static short const List32[] = {0, 1, 2, MCW, MCW + 1, MCW + 2, REFRESH_EOL};
static short const List32_000111[] = {MCW, MCW + 1, MCW + 2, REFRESH_EOL};
// static short const List42[] = {0, 1, 2, 3, MCW, MCW+1, MCW+2, MCW+3, REFRESH_EOL};
static short const ListFix[] = {1, MCW, MCW + 1, MCW + 2, MCW + MCW + 1, REFRESH_EOL};
// Full 3x3 slab, no passable corners: the dropship bay's deck art fills its
// whole foundation, so the placement grid must too (TS placement rule: art
// matches grid, no holes).
static short const TsList33[] = {0,       1,           2,
                                 MCW,     MCW + 1,     MCW + 2,
                                 MCW * 2, MCW * 2 + 1, MCW * 2 + 2, REFRESH_EOL};
static short const ListWeap[] = {0, 1, 2, (MCW * 1), (MCW * 1) + 1, (MCW * 1) + 2, REFRESH_EOL};
static short const TsDeptList[] = {0, MCW, MCW + 1, MCW + 2, MCW * 2, MCW * 2 + 1, MCW * 2 + 2, REFRESH_EOL};
static short const TsDeptOList[] = {1, 2, REFRESH_EOL};
static short const ListWestwood[] = {1, 2, 3, MCW + 1, MCW + 2, MCW + 3, REFRESH_EOL};
static short const OListSAM[] = {-MCW, -(MCW - 1), REFRESH_EOL};

// Hand of Nod foundation, TD's ListHand/OListHand: it occupies the middle row and the bottom-right thumb;
// the art also covers the top row and the bottom-left cell.
static short const ListHand[]  = {MCW, MCW + 1, MCW * 2 + 1, REFRESH_EOL};
static short const OListHand[] = {0, 1, MCW * 2, MCW, REFRESH_EOL};

// Hand of Nod exit cells, TD's ExitHand: twelve cells round the 2x3 plot, so infantry appear outside it.
static short const ExitHand[] = {
    XYCELL(2, 3),  XYCELL(1, 3),  XYCELL(0, 3),  XYCELL(2, 2),
    XYCELL(-1, 3), XYCELL(-1, 2), XYCELL(0, 0),  XYCELL(1, 0),
    XYCELL(-1, 0), XYCELL(2, 0),  XYCELL(2, 1),  XYCELL(-1, 1),
    REFRESH_EOL
};
#ifdef FATSHIP
static short const ListSPen[] = {0, 1, 2, MCW, MCW + 1, MCW + 2, MCW + MCW, MCW + MCW + 1, MCW + MCW + 2, REFRESH_EOL};
static short const OListSPen[] = {REFRESH_EOL};
#else
static short const ListSPen[] = {1, MCW, MCW + 1, MCW + 2, MCW + MCW + 1, REFRESH_EOL};
static short const OListSPen[] = {0, 2, MCW + MCW, MCW + MCW + 2, REFRESH_EOL};
#endif
static short const OListWestwood[] = {0, MCW, REFRESH_EOL};
static short const StoreList[] = {0, REFRESH_EOL};

static short const ListFactory[] =
    {0, 1, 2, (MCW * 1), (MCW * 1) + 1, (MCW * 1) + 2, (MCW * 2), (MCW * 2) + 1, (MCW * 2) + 2, REFRESH_EOL};

static short const OListFix[] = {0, 2, MCW + MCW, MCW + MCW + 2, REFRESH_EOL};
static short const OListWeap[] = {REFRESH_EOL};
static short const OComList[] = {1, REFRESH_EOL};
static short const OList12[] = {0, REFRESH_EOL};
static short const OListTmpl[] = {0, 1, 2, REFRESH_EOL};

/***************************************************************************
 */
static BuildingTypeClass const ClassBarrel(STRUCT_BARREL,
                                           TXT_BARREL,      // NAME:			Short name of the structure.
                                           "BARL",          // NAME:			Short name of the structure.
                                           FACING_NONE,     // Foundation direction from center of building.
                                           XYP_COORD(0, 0), // Exit point for produced units.
                                           REMAP_ALTERNATE, // Sidebar remap logic.
                                           0x0000,          //	Vertical offset.
                                           0x0000,          // Primary weapon offset along turret centerline.
                                           0x0000,          // Primary weapon lateral offset along turret centerline.
                                           false,           // Is this building a fake (decoy?)
                                           false,           // Animation rate is regulated for constant speed?
                                           true,            // Always use the given name for the building?
                                           false,           // Is this a wall type structure?
                                           true,            // Simple (one frame) damage imagery?
                                           true,            // Is it invisible to radar?
                                           true,            // Can the player select this?
                                           true,            // Is this a legal target for attack or move?
                                           true,            // Is this an insignificant building?
                                           false,           // Theater specific graphic image?
                                           false,           // Does it have a rotating turret?
                                           false,           // Can the building be color remapped to indicate owner?
                                           RTTI_NONE,       // The object type produced at this factory.
                                           DIR_N,           // Starting idle frame to match construction.
                                           BSIZE_11,        // SIZE:			Building size.
                                           NULL,            // Preferred exit cell list.
                                           (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                           (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassBarrel3(STRUCT_BARREL3,
                                            TXT_BARREL,      // NAME:			Short name of the structure.
                                            "BRL3",          // NAME:			Short name of the structure.
                                            FACING_NONE,     // Foundation direction from center of building.
                                            XYP_COORD(0, 0), // Exit point for produced units.
                                            REMAP_ALTERNATE, // Sidebar remap logic.
                                            0x0000,          //	Vertical offset.
                                            0x0000,          // Primary weapon offset along turret centerline.
                                            0x0000,          // Primary weapon lateral offset along turret centerline.
                                            false,           // Is this building a fake (decoy?)
                                            false,           // Animation rate is regulated for constant speed?
                                            true,            // Always use the given name for the building?
                                            false,           // Is this a wall type structure?
                                            true,            // Simple (one frame) damage imagery?
                                            true,            // Is it invisible to radar?
                                            false,           // Can the player select this?
                                            true,            // Is this a legal target for attack or move?
                                            true,            // Is this an insignificant building?
                                            false,           // Theater specific graphic image?
                                            false,           // Does it have a rotating turret?
                                            false,           // Can the building be color remapped to indicate owner?
                                            RTTI_NONE,       // The object type produced at this factory.
                                            DIR_N,           // Starting idle frame to match construction.
                                            BSIZE_11,        // SIZE:			Building size.
                                            NULL,            // Preferred exit cell list.
                                            (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                            (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassAVMine(STRUCT_AVMINE,
                                           TXT_AVMINE,      // NAME:			Short name of the structure.
                                           "MINV",          // NAME:			Short name of the structure.
                                           FACING_NONE,     // Foundation direction from center of building.
                                           XYP_COORD(0, 0), // Exit point for produced units.
                                           REMAP_NORMAL,    // Sidebar remap logic.
                                           0x0000,          //	Vertical offset.
                                           0x0000,          // Primary weapon offset along turret centerline.
                                           0x0000,          // Primary weapon lateral offset along turret centerline.
                                           false,           // Is this building a fake (decoy?)
                                           false,           // Animation rate is regulated for constant speed?
                                           false,           // Always use the given name for the building?
                                           false,           // Is this a wall type structure?
                                           true,            // Simple (one frame) damage imagery?
                                           true,            // Is it invisible to radar?
                                           false,           // Can the player select this?
                                           false,           // Is this a legal target for attack or move?
                                           true,            // Is this an insignificant building?
                                           false,           // Theater specific graphic image?
                                           false,           // Does it have a rotating turret?
                                           true,            // Can the building be color remapped to indicate owner?
                                           RTTI_NONE,       // The object type produced at this factory.
                                           DIR_N,           // Starting idle frame to match construction.
                                           BSIZE_11,        // SIZE:			Building size.
                                           NULL,            // Preferred exit cell list.
                                           (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                           (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassAPMine(STRUCT_APMINE,
                                           TXT_APMINE,      // NAME:			Short name of the structure.
                                           "MINP",          // NAME:			Short name of the structure.
                                           FACING_NONE,     // Foundation direction from center of building.
                                           XYP_COORD(0, 0), // Exit point for produced units.
                                           REMAP_NORMAL,    // Sidebar remap logic.
                                           0x0000,          //	Vertical offset.
                                           0x0000,          // Primary weapon offset along turret centerline.
                                           0x0000,          // Primary weapon lateral offset along turret centerline.
                                           false,           // Is this building a fake (decoy?)
                                           false,           // Animation rate is regulated for constant speed?
                                           false,           // Always use the given name for the building?
                                           false,           // Is this a wall type structure?
                                           true,            // Simple (one frame) damage imagery?
                                           true,            // Is it invisible to radar?
                                           false,           // Can the player select this?
                                           false,           // Is this a legal target for attack or move?
                                           true,            // Is this an insignificant building?
                                           false,           // Theater specific graphic image?
                                           false,           // Does it have a rotating turret?
                                           true,            // Can the building be color remapped to indicate owner?
                                           RTTI_NONE,       // The object type produced at this factory.
                                           DIR_N,           // Starting idle frame to match construction.
                                           BSIZE_11,        // SIZE:			Building size.
                                           NULL,            // Preferred exit cell list.
                                           (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                           (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const
    ClassIronCurtain(STRUCT_IRON_CURTAIN,
                     TXT_IRON_CURTAIN,          // NAME:			Short name of the structure.
                     "IRON",                    // NAME:			Short name of the structure.
                     FACING_S,                  // Foundation direction from center of building.
                     XYP_COORD(0, 0),           // Exit point for produced units.
                     REMAP_ALTERNATE,           // Sidebar remap logic.
                     0x0000,                    //	Vertical offset.
                     0x0000,                    // Primary weapon offset along turret centerline.
                     0x0000,                    // Primary weapon lateral offset along turret centerline.
                     false,                     // Is this building a fake (decoy?)
                     true,                      // Animation rate is regulated for constant speed?
                     false,                     // Always use the given name for the building?
                     false,                     // Is this a wall type structure?
                     true,                      // Simple (one frame) damage imagery?
                     false,                     // Is it invisible to radar?
                     true,                      // Can the player select this?
                     true,                      // Is this a legal target for attack or move?
                     false,                     // Is this an insignificant building?
                     false,                     // Theater specific graphic image?
                     false,                     // Does it have a rotating turret?
                     true,                      // Can the building be color remapped to indicate owner?
                     RTTI_NONE,                 // The object type produced at this factory.
                     DIR_N,                     // Starting idle frame to match construction.
                     BSIZE_22,                  // SIZE:			Building size.
                     NULL,                      // Preferred exit cell list.
                     (short const*)List22_0011, // OCCUPYLIST:	List of active foundation squares.
                     (short const*)List22_1100  // OVERLAPLIST:List of overlap cell offset.
    );

static BuildingTypeClass const
    ClassForwardCom(STRUCT_FORWARD_COM,
                    TXT_FORWARD_COM,           // NAME:			Short name of the structure.
                    "FCOM",                    // NAME:			Short name of the structure.
                    FACING_S,                  // Foundation direction from center of building.
                    XYP_COORD(0, 0),           // Exit point for produced units.
                    REMAP_ALTERNATE,           // Sidebar remap logic.
                    0x0000,                    //	Vertical offset.
                    0x0000,                    // Primary weapon offset along turret centerline.
                    0x0000,                    // Primary weapon lateral offset along turret centerline.
                    false,                     // Is this building a fake (decoy?)
                    true,                      // Animation rate is regulated for constant speed?
                    false,                     // Always use the given name for the building?
                    false,                     // Is this a wall type structure?
                    true,                      // Simple (one frame) damage imagery?
                    false,                     // Is it invisible to radar?
                    true,                      // Can the player select this?
                    true,                      // Is this a legal target for attack or move?
                    false,                     // Is this an insignificant building?
                    false,                     // Theater specific graphic image?
                    false,                     // Does it have a rotating turret?
                    true,                      // Can the building be color remapped to indicate owner?
                    RTTI_NONE,                 // The object type produced at this factory.
                    DIR_N,                     // Starting idle frame to match construction.
                    BSIZE_22,                  // SIZE:			Building size.
                    NULL,                      // Preferred exit cell list.
                    (short const*)List22_0011, // OCCUPYLIST:	List of active foundation squares.
                    (short const*)List22_1100  // OVERLAPLIST:List of overlap cell offset.
    );

static BuildingTypeClass const
    ClassAdvancedTech(STRUCT_ADVANCED_TECH,
                      TXT_ADVANCED_TECH,    // NAME:			Short name of the structure.
                      "ATEK",               // NAME:			Short name of the structure.
                      FACING_NONE,          // Foundation direction from center of building.
                      XYP_COORD(0, 0),      // Exit point for produced units.
                      REMAP_ALTERNATE,      // Sidebar remap logic.
                      0x0000,               //	Vertical offset.
                      0x0000,               // Primary weapon offset along turret centerline.
                      0x0000,               // Primary weapon lateral offset along turret centerline.
                      false,                // Is this building a fake (decoy?)
                      true,                 // Animation rate is regulated for constant speed?
                      false,                // Always use the given name for the building?
                      false,                // Is this a wall type structure?
                      true,                 // Simple (one frame) damage imagery?
                      false,                // Is it invisible to radar?
                      true,                 // Can the player select this?
                      true,                 // Is this a legal target for attack or move?
                      false,                // Is this an insignificant building?
                      false,                // Theater specific graphic image?
                      false,                // Does it have a rotating turret?
                      true,                 // Can the building be color remapped to indicate owner?
                      RTTI_NONE,            // The object type produced at this factory.
                      DIR_N,                // Starting idle frame to match construction.
                      BSIZE_22,             // SIZE:			Building size.
                      NULL,                 // Preferred exit cell list.
                      (short const*)List22, // OCCUPYLIST:	List of active foundation squares.
                      (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
    );

static BuildingTypeClass const
    ClassChronosphere(STRUCT_CHRONOSPHERE,
                      TXT_CHRONOSPHERE,     // NAME:			Short name of the structure.
                      "PDOX",               // NAME:			Short name of the structure.
                      FACING_NONE,          // Foundation direction from center of building.
                      XYP_COORD(0, 0),      // Exit point for produced units.
                      REMAP_ALTERNATE,      // Sidebar remap logic.
                      0x0000,               //	Vertical offset.
                      0x0000,               // Primary weapon offset along turret centerline.
                      0x0000,               // Primary weapon lateral offset along turret centerline.
                      false,                // Is this building a fake (decoy?)
                      true,                 // Animation rate is regulated for constant speed?
                      false,                // Always use the given name for the building?
                      false,                // Is this a wall type structure?
                      true,                 // Simple (one frame) damage imagery?
                      false,                // Is it invisible to radar?
                      true,                 // Can the player select this?
                      true,                 // Is this a legal target for attack or move?
                      false,                // Is this an insignificant building?
                      false,                // Theater specific graphic image?
                      false,                // Does it have a rotating turret?
                      true,                 // Can the building be color remapped to indicate owner?
                      RTTI_NONE,            // The object type produced at this factory.
                      DIR_N,                // Starting idle frame to match construction.
                      BSIZE_22,             // SIZE:			Building size.
                      NULL,                 // Preferred exit cell list.
                      (short const*)List22, // OCCUPYLIST:	List of active foundation squares.
                      (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
    );

static BuildingTypeClass const ClassWeapon(STRUCT_WEAP,
                                           TXT_WEAPON_FACTORY, // NAME:			Short name of the structure.
                                           "WEAP",             // NAME:			Short name of the structure.
                                           FACING_NONE,        // Foundation direction from center of building.
                                           XY_Coord(CELL_LEPTON_W + (CELL_LEPTON_W / 2),
                                                    CELL_LEPTON_H), // Exit point for produced units.
                                           REMAP_ALTERNATE,         // Sidebar remap logic.
                                           0x0000,                  //	Vertical offset.
                                           0x0000,                  // Primary weapon offset along turret centerline.
                                           0x0000,        // Primary weapon lateral offset along turret centerline.
                                           false,         // Is this building a fake (decoy?)
                                           false,         // Animation rate is regulated for constant speed?
                                           false,         // Always use the given name for the building?
                                           false,         // Is this a wall type structure?
                                           false,         // Simple (one frame) damage imagery?
                                           false,         // Is it invisible to radar?
                                           true,          // Can the player select this?
                                           true,          // Is this a legal target for attack or move?
                                           false,         // Is this an insignificant building?
                                           false,         // Theater specific graphic image?
                                           false,         // Does it have a rotating turret?
                                           true,          // Can the building be color remapped to indicate owner?
                                           RTTI_UNITTYPE, // The object type produced at this factory.
                                           DIR_N,         // Starting idle frame to match construction.
                                           BSIZE_32,      // SIZE:			Building size.
                                           (short const*)ExitWeap, // Preferred exit cell list.
                                           (short const*)ListWeap, // OCCUPYLIST:	List of active foundation squares.
                                           (short const*)OListWeap // OVERLAPLIST:List of overlap cell offset.
);

// Allied and Soviet war factories: RA's war factory split so the building carries its faction (ActLike, set
// from Owner= at Unlimbo). One built from a captured yard produces that faction's units, its MCV included.
static BuildingTypeClass const ClassAlliedWeapon(STRUCT_AWEAP,
                                                 TXT_NONE, // Display name (rules.ini Name= overrides).
                                                 "AWEAP",  // IniName.
                                                 FACING_NONE, // Foundation direction from center of building.
                                                 XY_Coord(CELL_LEPTON_W + (CELL_LEPTON_W / 2),
                                                          CELL_LEPTON_H), // Exit point for produced units.
                                                 REMAP_ALTERNATE,         // Sidebar remap logic.
                                                 0x0000,                  //	Vertical offset.
                                                 0x0000,        // Primary weapon offset along turret centerline.
                                                 0x0000,        // Primary weapon lateral offset along turret centerline.
                                                 false,         // Is this building a fake (decoy?)
                                                 false,         // Animation rate is regulated for constant speed?
                                                 false,         // Always use the given name for the building?
                                                 false,         // Is this a wall type structure?
                                                 false,         // Simple (one frame) damage imagery?
                                                 false,         // Is it invisible to radar?
                                                 true,          // Can the player select this?
                                                 true,          // Is this a legal target for attack or move?
                                                 false,         // Is this an insignificant building?
                                                 false,         // Theater specific graphic image?
                                                 false,         // Does it have a rotating turret?
                                                 true,          // Can the building be color remapped to indicate owner?
                                                 RTTI_UNITTYPE, // The object type produced at this factory.
                                                 DIR_N,         // Starting idle frame to match construction.
                                                 BSIZE_32,      // SIZE:			Building size.
                                                 (short const*)ExitWeap, // Preferred exit cell list.
                                                 (short const*)ListWeap, // OCCUPYLIST:	List of active foundation squares.
                                                 (short const*)OListWeap // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassSovietWeapon(STRUCT_SWEAP,
                                                 TXT_NONE, // Display name (rules.ini Name= overrides).
                                                 "SWEAP",  // IniName.
                                                 FACING_NONE, // Foundation direction from center of building.
                                                 XY_Coord(CELL_LEPTON_W + (CELL_LEPTON_W / 2),
                                                          CELL_LEPTON_H), // Exit point for produced units.
                                                 REMAP_ALTERNATE,         // Sidebar remap logic.
                                                 0x0000,                  //	Vertical offset.
                                                 0x0000,        // Primary weapon offset along turret centerline.
                                                 0x0000,        // Primary weapon lateral offset along turret centerline.
                                                 false,         // Is this building a fake (decoy?)
                                                 false,         // Animation rate is regulated for constant speed?
                                                 false,         // Always use the given name for the building?
                                                 false,         // Is this a wall type structure?
                                                 false,         // Simple (one frame) damage imagery?
                                                 false,         // Is it invisible to radar?
                                                 true,          // Can the player select this?
                                                 true,          // Is this a legal target for attack or move?
                                                 false,         // Is this an insignificant building?
                                                 false,         // Theater specific graphic image?
                                                 false,         // Does it have a rotating turret?
                                                 true,          // Can the building be color remapped to indicate owner?
                                                 RTTI_UNITTYPE, // The object type produced at this factory.
                                                 DIR_N,         // Starting idle frame to match construction.
                                                 BSIZE_32,      // SIZE:			Building size.
                                                 (short const*)ExitWeap, // Preferred exit cell list.
                                                 (short const*)ListWeap, // OCCUPYLIST:	List of active foundation squares.
                                                 (short const*)OListWeap // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassShipYard(
    STRUCT_SHIP_YARD,
    TXT_SHIP_YARD, // NAME:			Short name of the structure.
    "SYRD",        // NAME:			Short name of the structure.
    FACING_NONE,   // Foundation direction from center of building.
    XYP_COORD(22 + (CELL_PIXEL_W / 2), ((CELL_PIXEL_H * 2) - (CELL_PIXEL_H / 2))), // Exit point for produced units.
    REMAP_ALTERNATE,                                                               // Sidebar remap logic.
    0x0000,                                                                        //	Vertical offset.
    0x0000,                 // Primary weapon offset along turret centerline.
    0x0000,                 // Primary weapon lateral offset along turret centerline.
    false,                  // Is this building a fake (decoy?)
    false,                  // Animation rate is regulated for constant speed?
    false,                  // Always use the given name for the building?
    false,                  // Is this a wall type structure?
    false,                  // Simple (one frame) damage imagery?
    false,                  // Is it invisible to radar?
    true,                   // Can the player select this?
    true,                   // Is this a legal target for attack or move?
    false,                  // Is this an insignificant building?
    false,                  // Theater specific graphic image?
    false,                  // Does it have a rotating turret?
    true,                   // Can the building be color remapped to indicate owner?
    RTTI_VESSELTYPE,        // The object type produced at this factory.
    DIR_N,                  // Starting idle frame to match construction.
    BSIZE_33,               // SIZE:			Building size.
    NULL,                   // Preferred exit cell list.
    (short const*)ListSPen, // OCCUPYLIST:	List of active foundation squares.
    (short const*)OListSPen // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassSubPen(
    STRUCT_SUB_PEN,
    TXT_SUB_PEN, // NAME:			Short name of the structure.
    "SPEN",      // NAME:			Short name of the structure.
    FACING_NONE, // Foundation direction from center of building.
    XYP_COORD(22 + (CELL_PIXEL_W / 2), ((CELL_PIXEL_H * 2) - (CELL_PIXEL_H / 2))), // Exit point for produced units.
    REMAP_ALTERNATE,                                                               // Sidebar remap logic.
    0x0000,                                                                        //	Vertical offset.
    0x0000,                 // Primary weapon offset along turret centerline.
    0x0000,                 // Primary weapon lateral offset along turret centerline.
    false,                  // Is this building a fake (decoy?)
    false,                  // Animation rate is regulated for constant speed?
    false,                  // Always use the given name for the building?
    false,                  // Is this a wall type structure?
    false,                  // Simple (one frame) damage imagery?
    false,                  // Is it invisible to radar?
    true,                   // Can the player select this?
    true,                   // Is this a legal target for attack or move?
    false,                  // Is this an insignificant building?
    false,                  // Theater specific graphic image?
    false,                  // Does it have a rotating turret?
    true,                   // Can the building be color remapped to indicate owner?
    RTTI_VESSELTYPE,        // The object type produced at this factory.
    DIR_N,                  // Starting idle frame to match construction.
    BSIZE_33,               // SIZE:			Building size.
    (short const*)ExitSub,  // Preferred exit cell list.
    (short const*)ListSPen, // OCCUPYLIST:	List of active foundation squares.
    (short const*)OListSPen // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassPillbox(STRUCT_PILLBOX,
                                            TXT_PILLBOX,     // NAME:			Short name of the structure.
                                            "PBOX",          // NAME:			Short name of the structure.
                                            FACING_NONE,     // Foundation direction from center of building.
                                            XYP_COORD(0, 0), // Exit point for produced units.
                                            REMAP_ALTERNATE, // Sidebar remap logic.
                                            0x0010,          //	Vertical offset.
                                            0x0040,          // Primary weapon offset along turret centerline.
                                            0x0000,          // Primary weapon lateral offset along turret centerline.
                                            false,           // Is this building a fake (decoy?)
                                            false,           // Animation rate is regulated for constant speed?
                                            false,           // Always use the given name for the building?
                                            false,           // Is this a wall type structure?
                                            true,            // Simple (one frame) damage imagery?
                                            false,           // Is it invisible to radar?
                                            true,            // Can the player select this?
                                            true,            // Is this a legal target for attack or move?
                                            false,           // Is this an insignificant building?
                                            false,           // Theater specific graphic image?
                                            false,           // Does it have a rotating turret?
                                            true,            // Can the building be color remapped to indicate owner?
                                            RTTI_NONE,       // The object type produced at this factory.
                                            DIR_N,           // Starting idle frame to match construction.
                                            BSIZE_11,        // SIZE:			Building size.
                                            NULL,            // Preferred exit cell list.
                                            (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                            (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassCamoPillbox(STRUCT_CAMOPILLBOX,
                                                TXT_CAMOPILLBOX, // NAME:			Short name of the structure.
                                                "HBOX",          // NAME:			Short name of the structure.
                                                FACING_NONE,     // Foundation direction from center of building.
                                                XYP_COORD(0, 0), // Exit point for produced units.
                                                REMAP_ALTERNATE, // Sidebar remap logic.
                                                0x0010,          //	Vertical offset.
                                                0x0040,          // Primary weapon offset along turret centerline.
                                                0x0000,    // Primary weapon lateral offset along turret centerline.
                                                false,     // Is this building a fake (decoy?)
                                                false,     // Animation rate is regulated for constant speed?
                                                false,     // Always use the given name for the building?
                                                false,     // Is this a wall type structure?
                                                true,      // Simple (one frame) damage imagery?
                                                false,     // Is it invisible to radar?
                                                true,      // Can the player select this?
                                                true,      // Is this a legal target for attack or move?
                                                false,     // Is this an insignificant building?
                                                true,      // Theater specific graphic image?
                                                false,     // Does it have a rotating turret?
                                                true,      // Can the building be color remapped to indicate owner?
                                                RTTI_NONE, // The object type produced at this factory.
                                                DIR_N,     // Starting idle frame to match construction.
                                                BSIZE_11,  // SIZE:			Building size.
                                                NULL,      // Preferred exit cell list.
                                                (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                                (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassTesla(STRUCT_TESLA,
                                          TXT_TESLA,       // NAME:			Short name of the structure.
                                          "TSLA",          // NAME:			Short name of the structure.
                                          FACING_S,        // Foundation direction from center of building.
                                          XYP_COORD(0, 0), // Exit point for produced units.
                                          REMAP_ALTERNATE, // Sidebar remap logic.
                                          0x00C8,          //	Vertical offset.
                                          0x0000,          // Primary weapon offset along turret centerline.
                                          0x0000,          // Primary weapon lateral offset along turret centerline.
                                          false,           // Is this building a fake (decoy?)
                                          false,           // Animation rate is regulated for constant speed?
                                          false,           // Always use the given name for the building?
                                          false,           // Is this a wall type structure?
                                          false,           // Simple (one frame) damage imagery?
                                          false,           // Is it invisible to radar?
                                          true,            // Can the player select this?
                                          true,            // Is this a legal target for attack or move?
                                          false,           // Is this an insignificant building?
                                          false,           // Theater specific graphic image?
                                          false,           // Does it have a rotating turret?
                                          true,            // Can the building be color remapped to indicate owner?
                                          RTTI_NONE,       // The object type produced at this factory.
                                          DIR_N,           // Starting idle frame to match construction.
                                          BSIZE_12,        // SIZE:			Building size.
                                          NULL,            // Preferred exit cell list.
                                          (short const*)List12, // OCCUPYLIST:	List of active foundation squares.
                                          (short const*)OList12 // OVERLAPLIST:List of overlap cell offset.
);

// TD power plant, advanced power plant, barracks and silo. The advanced plant is TD's 2x2, not APWR's 3x3;
// the barracks exits at TENT's exit point.
static BuildingTypeClass const ClassTdNuke(STRUCT_TDNUKE,
                                           TXT_NONE,        // rules.ini Name= overrides
                                           "TDNUKE",        // IniName.
                                           FACING_S,        // Foundation direction.
                                           XYP_COORD(0, 0), // Exit point (no production).
                                           REMAP_ALTERNATE,
                                           0x0000,          // Vertical offset.
                                           0x0000,          // Primary weapon offset.
                                           0x0000,          // Primary weapon lateral offset.
                                           false,           // Fake?
                                           true,            // Animation rate regulated?
                                           false,           // Always use given name?
                                           false,           // Wall?
                                           true,            // Simple damage imagery?
                                           false,           // Invisible to radar?
                                           true,            // Selectable?
                                           true,            // Legal target?
                                           false,           // Insignificant?
                                           false,           // Theater specific?
                                           false,           // Rotating turret?
                                           true,            // Color remappable?
                                           RTTI_NONE,       // Produces.
                                           DIR_N,           // Starting idle frame.
                                           BSIZE_22,        // 2x2.
                                           NULL,            // Exit cell list.
                                           (short const*)List22,     // OCCUPYLIST.
                                           (short const*)List22_1100 // OVERLAPLIST.
);

static BuildingTypeClass const ClassTdNuk2(STRUCT_TDNUK2,
                                           TXT_NONE,
                                           "TDNUK2",
                                           FACING_S,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000,
                                           0x0000,
                                           0x0000,
                                           false,
                                           true,
                                           false,
                                           false,
                                           true,
                                           false,
                                           true,
                                           true,
                                           false,
                                           false,
                                           false,
                                           true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_22,        // TD-authentic: 2x2 (not APWR's 3x3).
                                           NULL,
                                           (short const*)List22,
                                           (short const*)List22_1100
);

static BuildingTypeClass const ClassTdPyle(STRUCT_TDPYLE,
                                           TXT_NONE,
                                           "TDPYLE",
                                           FACING_NONE,
                                           XYP_COORD(24, 47), // Match TENT.
                                           REMAP_ALTERNATE,
                                           0x0000,
                                           0x0000,
                                           0x0000,
                                           false,
                                           true,
                                           false,
                                           false,
                                           false,
                                           false,
                                           true,
                                           true,
                                           false,
                                           false,
                                           false,
                                           true,
                                           RTTI_INFANTRYTYPE, // Infantry factory.
                                           DIR_N,
                                           BSIZE_22,
                                           (short const*)ExitPyle,
                                           (short const*)List22,
                                           NULL
);

static BuildingTypeClass const ClassTdSilo(STRUCT_TDSILO,
                                           TXT_NONE,
                                           "TDSILO",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000,
                                           0x0000,
                                           0x0000,
                                           false,
                                           false,
                                           false,
                                           false,
                                           true,
                                           false,
                                           true,
                                           true,
                                           false,
                                           false,
                                           false,
                                           true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_21,        // TD-authentic: 2x1 (matches Footprint=SILO preset).
                                           NULL,
                                           (short const*)StoreList,
                                           (short const*)NULL
);

// TD defences: Guard Tower, Advanced Guard Tower, Nod Turret and SAM Site. The SAM is a port of TD's own
// SAM states, not RA's (docs/td-sam-deep-dive.md).
static BuildingTypeClass const ClassTdGtwr(STRUCT_TDGTWR,
                                           TXT_NONE,
                                           "TDGTWR",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0030,          // VerticalOffset — TD ClassGTower Fire_Coord +0x30 DIR_N (docs/td-gtwr-gun-verification.md).
                                           0x0040,          // PrimaryOffset — TD ClassGTower Fire_Coord +0x40 forward.
                                           0x0000,
                                           false,
                                           false,
                                           false,
                                           false,
                                           true,            // Simple damage imagery.
                                           false,
                                           true,
                                           true,
                                           false,
                                           false,
                                           false,           // No rotating turret.
                                           true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_11,
                                           NULL,
                                           (short const*)List1,
                                           (short const*)NULL
);

// GDI Advanced Guard Tower, ported from TD's ATOWER: a fixed missile rack whose missiles home after launch.
// IsTurretEquipped stays false: the art has no rotation frames (docs/td-atwr-deep-dive.md).
static BuildingTypeClass const ClassTdAtwr(STRUCT_TDATWR,
                                           TXT_NONE,
                                           "TDATWR",
                                           FACING_S,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0030,          // VerticalOffset: TD ClassATower Fire_Coord.
                                           0x0040,          // PrimaryOffset: TD ClassATower Fire_Coord.
                                           0x0000,
                                           false,
                                           false,
                                           false,
                                           false,
                                           true,            // IsSimpleDamage, as TD's ClassATower.
                                           false,
                                           true,
                                           true,
                                           false,
                                           false,
                                           false,           // IsTurretEquipped: a fixed missile rack.
                                           true,
                                           RTTI_NONE,
                                           DIR_N,           // Initial facing, as TD's ClassATower.
                                           BSIZE_12,
                                           NULL,
                                           (short const*)List12,
                                           (short const*)OList12
);

static BuildingTypeClass const ClassTdGun(STRUCT_TDGUN,
                                          TXT_NONE,
                                          "TDGUN",
                                          FACING_NONE,
                                          XYP_COORD(0, 0),
                                          REMAP_ALTERNATE,
                                          0x0030,          // Vertical offset matches TURRET.
                                          0x0080,          // Primary weapon offset matches TURRET.
                                          0x0000,
                                          false,
                                          false,
                                          false,
                                          false,
                                          false,
                                          false,
                                          true,
                                          true,
                                          false,
                                          false,
                                          true,            // Rotating turret.
                                          true,
                                          RTTI_NONE,
                                          (DirType)208,    // Match TURRET starting facing.
                                          BSIZE_11,
                                          NULL,
                                          (short const*)List1,
                                          (short const*)NULL
);

static BuildingTypeClass const ClassTdSam(STRUCT_TDSAM,
                                          TXT_NONE,
                                          "TDSAM",
                                          FACING_NONE,
                                          XYP_COORD(0, 0),
                                          REMAP_ALTERNATE,
                                          0x0030,          // Match SAM.
                                          0x0080,          // Match SAM.
                                          0x0000,
                                          false,
                                          false,
                                          false,
                                          false,
                                          false,
                                          false,
                                          true,
                                          true,
                                          false,
                                          false,
                                          true,            // Rotating turret (launcher rotates to target).
                                          true,
                                          RTTI_NONE,
                                          DIR_N,
                                          BSIZE_21,
                                          NULL,
                                          (short const*)List21,
                                          (short const*)OListSAM
);

// Hand of Nod, ported from TD's ClassHand: an infantry factory on TD's 2x3 plot. Infantry leave by the door
// at the bottom-right thumb.
static BuildingTypeClass const ClassTdHand(STRUCT_TDHAND,
                                           TXT_NONE,           // Display name (rules.ini Name= overrides).
                                           "TDHAND",           // IniName.
                                           FACING_NONE,        // Foundation direction from center.
                                           XYP_COORD(36, 63),  // Door at the thumb cell — TD-authentic exit.
                                           REMAP_ALTERNATE,    // Sidebar remap logic.
                                           0x0000,             // Vertical offset (no turret).
                                           0x0000,             // Primary weapon offset (no weapon).
                                           0x0000,             // Primary weapon lateral offset (no weapon).
                                           false,              // Is this building a fake (decoy?)
                                           true,               // Animation rate regulated for constant speed?
                                           false,              // Always use the given name for the building?
                                           false,              // Is this a wall type structure?
                                           true,               // Simple (one frame) damage imagery?
                                           false,              // Is it invisible to radar?
                                           true,               // Can the player select this?
                                           true,               // Is this a legal target for attack or move?
                                           false,              // Is this an insignificant building?
                                           false,              // Theater specific graphic image?
                                           false,              // Does it have a rotating turret?
                                           true,               // Can the building be color remapped?
                                           RTTI_INFANTRYTYPE,  // Infantry factory.
                                           DIR_N,              // Starting idle frame.
                                           BSIZE_23,           // 2x3 footprint (TD-authentic).
                                           (short const*)ExitHand,
                                           (short const*)ListHand,
                                           (short const*)OListHand
);

// TD helipads (GDI, Nod and the campaigns' shared pad), ported from TD's ClassHelipad: 2x2 aircraft
// factories with no exit cells, since the helicopter lands on the pad.
static BuildingTypeClass const ClassTdGdiHpad(STRUCT_TDGHPAD,
                                              TXT_NONE,           // Display name (rules.ini Name= overrides).
                                              "TDGHPAD",          // IniName.
                                              FACING_NONE,        // Foundation direction from center.
                                              XYP_COORD(0, 0),    // No exit list — helicopter docks on the pad.
                                              REMAP_ALTERNATE,    // Sidebar remap logic.
                                              0x0000,             // Vertical offset.
                                              0x0000,             // Primary weapon offset.
                                              0x0000,             // Primary weapon lateral offset.
                                              false,              // Is this building a fake (decoy?)
                                              false,              // Animation rate regulated for constant speed?
                                              false,              // Always use the given name?
                                              false,              // Is this a wall type structure?
                                              false,              // Simple (one frame) damage imagery?
                                              false,              // Is it invisible to radar?
                                              true,               // Can the player select this?
                                              true,               // Is this a legal target?
                                              false,              // Is this an insignificant building?
                                              false,              // Theater specific graphic image?
                                              false,              // Does it have a rotating turret?
                                              true,               // Can the building be color remapped?
                                              RTTI_AIRCRAFTTYPE,  // Aircraft factory.
                                              DIR_N,              // Starting idle frame.
                                              BSIZE_22,           // 2x2 footprint (TD-authentic).
                                              NULL,               // No preferred exit cell.
                                              (short const*)List2,
                                              (short const*)NULL
);

static BuildingTypeClass const ClassTdNodHpad(STRUCT_TDNHPAD,
                                              TXT_NONE,           // Display name (rules.ini Name= overrides).
                                              "TDNHPAD",          // IniName.
                                              FACING_NONE,        // Foundation direction from center.
                                              XYP_COORD(0, 0),    // No exit list — helicopter docks on the pad.
                                              REMAP_ALTERNATE,    // Sidebar remap logic.
                                              0x0000,             // Vertical offset.
                                              0x0000,             // Primary weapon offset.
                                              0x0000,             // Primary weapon lateral offset.
                                              false,              // Is this building a fake (decoy?)
                                              false,              // Animation rate regulated for constant speed?
                                              false,              // Always use the given name?
                                              false,              // Is this a wall type structure?
                                              false,              // Simple (one frame) damage imagery?
                                              false,              // Is it invisible to radar?
                                              true,               // Can the player select this?
                                              true,               // Is this a legal target?
                                              false,              // Is this an insignificant building?
                                              false,              // Theater specific graphic image?
                                              false,              // Does it have a rotating turret?
                                              true,               // Can the building be color remapped?
                                              RTTI_AIRCRAFTTYPE,  // Aircraft factory.
                                              DIR_N,              // Starting idle frame.
                                              BSIZE_22,           // 2x2 footprint (TD-authentic).
                                              NULL,               // No preferred exit cell.
                                              (short const*)List2,
                                              (short const*)NULL
);

static BuildingTypeClass const ClassTdHpad(STRUCT_TDHPAD,
                                           TXT_NONE,           // Display name (rules.ini Name= overrides).
                                           "TDHPAD",           // IniName.
                                           FACING_NONE,        // Foundation direction from center.
                                           XYP_COORD(0, 0),    // No exit list — helicopter docks on the pad.
                                           REMAP_ALTERNATE,    // Sidebar remap logic.
                                           0x0000,             // Vertical offset.
                                           0x0000,             // Primary weapon offset.
                                           0x0000,             // Primary weapon lateral offset.
                                           false,              // Is this building a fake (decoy?)
                                           false,              // Animation rate regulated for constant speed?
                                           false,              // Always use the given name?
                                           false,              // Is this a wall type structure?
                                           false,              // Simple (one frame) damage imagery?
                                           false,              // Is it invisible to radar?
                                           true,               // Can the player select this?
                                           true,               // Is this a legal target?
                                           false,              // Is this an insignificant building?
                                           false,              // Theater specific graphic image?
                                           false,              // Does it have a rotating turret?
                                           true,               // Can the building be color remapped?
                                           RTTI_AIRCRAFTTYPE,  // Aircraft factory.
                                           DIR_N,              // Starting idle frame.
                                           BSIZE_22,           // 2x2 footprint (TD-authentic).
                                           NULL,               // No preferred exit cell.
                                           (short const*)List2,
                                           (short const*)NULL
);

// TD Service Depot, ported from TD's ClassRepair: a 3x3 repair bay on the cross-shaped ListFix foundation.
static BuildingTypeClass const ClassTdFix(STRUCT_TDFIX,
                                          TXT_NONE,           // Display name (rules.ini Name= overrides).
                                          "TDFIX",            // IniName.
                                          FACING_NONE,        // Foundation direction.
                                          XYP_COORD(0, 0),    // No produced-unit exit (non-factory).
                                          REMAP_ALTERNATE,    // Sidebar remap logic.
                                          0x0000,             // Vertical offset.
                                          0x0000,             // Primary weapon offset.
                                          0x0000,             // Primary weapon lateral offset.
                                          false,              // Is this building a fake?
                                          true,               // Animation rate regulated for constant speed?
                                          false,              // Always use the given name?
                                          false,              // Is this a wall type structure?
                                          false,              // Simple (one frame) damage imagery?
                                          false,              // Is it invisible to radar?
                                          true,               // Can the player select this?
                                          true,               // Is this a legal target?
                                          false,              // Is this an insignificant building?
                                          false,              // Theater specific graphic image?
                                          false,              // Does it have a rotating turret?
                                          true,               // Can the building be color remapped?
                                          RTTI_NONE,          // Not a factory.
                                          DIR_N,              // Starting idle frame.
                                          BSIZE_33,           // 3x3 footprint (TD-authentic).
                                          NULL,               // No preferred exit cell.
                                          (short const*)ListFix,
                                          (short const*)OListFix
);

// TD Weapons Factory, ported from TD's ClassWeapon on its 3x3 plot: the bottom two rows are foundation and
// the roof overhangs the top row. Its door is the TDWEAP2 overlay (BuildingClass::Draw_It).
static short const TdExitWeap[] = {XYCELL(-1, 3), XYCELL(0, 3), XYCELL(-1, 2),
                                   XYCELL(1, 3), XYCELL(-1, 1), XYCELL(3, 1),
                                   XYCELL(3, 2), XYCELL(3, 3), XYCELL(2, 3),
                                   REFRESH_EOL};
static short const TdListWeap[] = {(MCW * 1), (MCW * 1) + 1, (MCW * 1) + 2,
                                   (MCW * 2), (MCW * 2) + 1, (MCW * 2) + 2,
                                   REFRESH_EOL};
static short const TdOListWeap[] = {0, 1, 2, REFRESH_EOL};

static BuildingTypeClass const ClassTdWeap(STRUCT_TDWEAP,
                                           TXT_NONE,           // Display name (rules.ini Name= overrides).
                                           "TDWEAP",           // IniName.
                                           FACING_NONE,        // Foundation direction.
                                           XYP_COORD(10 + (CELL_PIXEL_W / 2),
                                                     ((CELL_PIXEL_H * 3) - (CELL_PIXEL_H / 2)) - 21), // TD-authentic Exit_Coord (tiberiandawn/bdata.cpp:268-269).
                                           REMAP_ALTERNATE,    // Sidebar remap logic.
                                           0x0000,             // Vertical offset.
                                           0x0000,             // Primary weapon offset.
                                           0x0000,             // Primary weapon lateral offset.
                                           false,              // Is this building a fake?
                                           false,              // Animation rate regulated for constant speed?
                                           false,              // Always use the given name?
                                           false,              // Is this a wall type structure?
                                           false,              // Simple (one frame) damage imagery?
                                           false,              // Is it invisible to radar?
                                           true,               // Can the player select this?
                                           true,               // Is this a legal target?
                                           false,              // Is this an insignificant building?
                                           false,              // Theater specific graphic image?
                                           false,              // Does it have a rotating turret?
                                           true,               // Can the building be color remapped?
                                           RTTI_UNITTYPE,      // Vehicle factory.
                                           DIR_N,              // Starting idle frame.
                                           BSIZE_33,           // 3x3 footprint (TD-authentic — NOT RA's 3x2).
                                           (short const*)TdExitWeap,
                                           (short const*)TdListWeap,
                                           (short const*)TdOListWeap
);

// TD Tiberium Refinery, ported from TD's ClassRefinery on TD's footprint, not RA's. Its dock animation
// states are in One_Time's _anims table.
static short const TdListProc[] = {1, (MCW * 1), (MCW * 1) + 1, (MCW * 1) + 2, REFRESH_EOL};
static short const TdOListProc[] = {0, 2, (MCW * 2), (MCW * 2) + 1, (MCW * 2) + 2, REFRESH_EOL};

static BuildingTypeClass const ClassTdProc(STRUCT_TDPROC,
                                           TXT_NONE,           // Display name (rules.ini Name= overrides).
                                           "TDPROC",           // IniName.
                                           FACING_NONE,        // Foundation direction.
                                           XYP_COORD(0, 0),    // Exit point unused (refinery doesn't produce units).
                                           REMAP_ALTERNATE,    // Sidebar remap logic.
                                           0x0000,             // Vertical offset.
                                           0x0000,             // Primary weapon offset.
                                           0x0000,             // Primary weapon lateral offset.
                                           false,              // Is this building a fake?
                                           false,              // Animation rate regulated for constant speed?
                                           false,              // Always use the given name?
                                           false,              // Is this a wall type structure?
                                           false,              // Simple (one frame) damage imagery?
                                           false,              // Is it invisible to radar?
                                           true,               // Can the player select this?
                                           true,               // Is this a legal target?
                                           false,              // Is this an insignificant building?
                                           false,              // Theater specific graphic image?
                                           false,              // Does it have a rotating turret?
                                           true,               // Can the building be color remapped?
                                           RTTI_NONE,          // Not a factory — engine grants free harvester at build time.
                                           DIR_N,              // Starting idle frame.
                                           BSIZE_33,           // 3x3 footprint (TD-authentic).
                                           NULL,               // No preferred exit cell.
                                           (short const*)TdListProc,
                                           (short const*)TdOListProc
);

// TD Construction Yard, ported from TD's ClassConst on TD's 3x2 plot (RA's is 3x3). UNIT_TDMCV deploys
// it in the campaigns; skirmish uses the faction yards TDNFACT and TDGFACT.
static BuildingTypeClass const ClassTdFact(STRUCT_TDFACT,
                                           TXT_NONE,           // Display name (rules.ini Name= overrides).
                                           "TDFACT",           // IniName.
                                           FACING_NONE,        // Foundation direction.
                                           XYP_COORD(0, 0),    // Exit point unused (not a vehicle factory).
                                           REMAP_ALTERNATE,    // Sidebar remap logic.
                                           0x0000,             // Vertical offset.
                                           0x0000,             // Primary weapon offset.
                                           0x0000,             // Primary weapon lateral offset.
                                           false,              // Is this building a fake?
                                           false,              // Animation rate regulated for constant speed?
                                           false,              // Always use the given name?
                                           false,              // Is this a wall type structure?
                                           false,              // Simple (one frame) damage imagery?
                                           false,              // Is it invisible to radar?
                                           true,               // Can the player select this?
                                           true,               // Is this a legal target?
                                           false,              // Is this an insignificant building?
                                           false,              // Theater specific graphic image?
                                           false,              // Does it have a rotating turret?
                                           true,               // Can the building be color remapped?
                                           RTTI_BUILDINGTYPE,  // Produces buildings (TD-authentic line 561).
                                           DIR_N,              // Starting idle frame.
                                           BSIZE_32,           // 3x2 footprint (TD-authentic — NOT RA's 3x3).
                                           NULL,               // No preferred exit cell.
                                           (short const*)List32,
                                           (short const*)NULL  // No overlap row.
);

// Nod and GDI construction yards: TD's one yard split so the building carries its faction. The sidebar
// offers the tree of the building's ActLike, so a captured yard keeps offering its own faction's tree.
static BuildingTypeClass const ClassTdNodFact(STRUCT_TDNFACT,
                                              TXT_NONE,           // Display name (rules.ini Name= overrides).
                                              "TDNFACT",          // IniName.
                                              FACING_NONE,        // Foundation direction.
                                              XYP_COORD(0, 0),    // Exit point unused (not a vehicle factory).
                                              REMAP_ALTERNATE,    // Sidebar remap logic.
                                              0x0000,             // Vertical offset.
                                              0x0000,             // Primary weapon offset.
                                              0x0000,             // Primary weapon lateral offset.
                                              false,              // Is this building a fake?
                                              false,              // Animation rate regulated for constant speed?
                                              false,              // Always use the given name?
                                              false,              // Is this a wall type structure?
                                              false,              // Simple (one frame) damage imagery?
                                              false,              // Is it invisible to radar?
                                              true,               // Can the player select this?
                                              true,               // Is this a legal target?
                                              false,              // Is this an insignificant building?
                                              false,              // Theater specific graphic image?
                                              false,              // Does it have a rotating turret?
                                              true,               // Can the building be color remapped?
                                              RTTI_BUILDINGTYPE,  // Produces buildings.
                                              DIR_N,              // Starting idle frame.
                                              BSIZE_32,           // 3x2 footprint (TD-authentic — NOT RA's 3x3).
                                              NULL,               // No preferred exit cell.
                                              (short const*)List32,
                                              (short const*)NULL  // No overlap row.
);

static BuildingTypeClass const ClassTdGdiFact(STRUCT_TDGFACT,
                                              TXT_NONE,           // Display name (rules.ini Name= overrides).
                                              "TDGFACT",          // IniName.
                                              FACING_NONE,        // Foundation direction.
                                              XYP_COORD(0, 0),    // Exit point unused (not a vehicle factory).
                                              REMAP_ALTERNATE,    // Sidebar remap logic.
                                              0x0000,             // Vertical offset.
                                              0x0000,             // Primary weapon offset.
                                              0x0000,             // Primary weapon lateral offset.
                                              false,              // Is this building a fake?
                                              false,              // Animation rate regulated for constant speed?
                                              false,              // Always use the given name?
                                              false,              // Is this a wall type structure?
                                              false,              // Simple (one frame) damage imagery?
                                              false,              // Is it invisible to radar?
                                              true,               // Can the player select this?
                                              true,               // Is this a legal target?
                                              false,              // Is this an insignificant building?
                                              false,              // Theater specific graphic image?
                                              false,              // Does it have a rotating turret?
                                              true,               // Can the building be color remapped?
                                              RTTI_BUILDINGTYPE,  // Produces buildings.
                                              DIR_N,              // Starting idle frame.
                                              BSIZE_32,           // 3x2 footprint (TD-authentic — NOT RA's 3x3).
                                              NULL,               // No preferred exit cell.
                                              (short const*)List32,
                                              (short const*)NULL  // No overlap row.
);

// TS Construction Yard ([GACNST]): deployed from UNIT_TSMCV, never built from the sidebar. A standing one
// gates the TS tree (docs/ts-gdi-tree-plan.md).
static BuildingTypeClass const ClassTsFact(STRUCT_TSFACT,
                                           TXT_NONE,           // Display name (rules.ini Name= overrides).
                                           "TSFACT",           // IniName.
                                           FACING_NONE,        // Foundation direction.
                                           XYP_COORD(0, 0),    // Exit point unused (not a vehicle factory).
                                           REMAP_ALTERNATE,    // Sidebar remap logic.
                                           0x0000,             // Vertical offset.
                                           0x0000,             // Primary weapon offset.
                                           0x0000,             // Primary weapon lateral offset.
                                           false,              // Is this building a fake?
                                           false,              // Animation rate regulated for constant speed?
                                           false,              // Always use the given name?
                                           false,              // Is this a wall type structure?
                                           false,              // Simple (one frame) damage imagery?
                                           false,              // Is it invisible to radar?
                                           true,               // Can the player select this?
                                           true,               // Is this a legal target?
                                           false,              // Is this an insignificant building?
                                           false,              // Theater specific graphic image?
                                           false,              // Does it have a rotating turret?
                                           true,               // Can the building be color remapped?
                                           RTTI_BUILDINGTYPE,  // Produces buildings.
                                           DIR_N,              // Starting idle frame.
                                           BSIZE_32,           // 3x2 like TDFACT, the size of its art: the launcher
                                                               // centres the selection box on this plot.
                                           NULL,               // No preferred exit cell.
                                           (short const*)List32,
                                           (short const*)NULL);

// TS GDI tree buildings: TS stats in rules.ini, composited TS art under TS* tileset keys. One_Time's
// _td_bdonors lends each the classic dims and construction anim of a TD counterpart.

static BuildingTypeClass const ClassTsPile(STRUCT_TSPILE,
                                           TXT_NONE,
                                           "TSPILE",
                                           FACING_NONE,
                                           // The foot of the entrance steps, classic px from the plot's top-left corner: in the
                                           // row in front, as infantry snap to their cell's nearest free spot.
                                           XYP_COORD(32, 26),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,              // fake
                                           true,               // anim regulated
                                           false, false, false, false,
                                           true, true, false, false, false, true,
                                           RTTI_INFANTRYTYPE,  // Infantry factory.
                                           DIR_N,
                                           BSIZE_21,           // 2x1: the bunkers stand on the plot row with the bib row
                                                                // in front; the masts and the flag rise into the row behind.
                                           (short const*)ExitTsPile,
                                           (short const*)List21,
                                           NULL);

static BuildingTypeClass const ClassTsProc(STRUCT_TSPROC,
                                           TXT_NONE,
                                           "TSPROC",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           false,              // anim regulated
                                           false, false, false, false,
                                           true, true, false, false, false, true,
                                           RTTI_NONE,          // Engine grants free harvester at build time.
                                           DIR_N,
                                           BSIZE_43,           // 4 wide x 3 high: 2 building rows + the south apron row
                                                               // as real footprint (no cliff drape). The tall art
                                                               // overhangs the row NORTH of the plot (radar treatment),
                                                               // so units can walk behind it. Centre CELL = the dock pad.
                                           NULL,
                                           (short const*)TsProcList,   // Blocking: the umbrella's 2x2 in the south-west.
                                           (short const*)TsProcOList); // Overlap: the north row, the pad, the east column and the lane mouth.

static BuildingTypeClass const ClassTsSilo(STRUCT_TSSILO,
                                           TXT_NONE,
                                           "TSSILO",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           false,
                                           false, false,
                                           true,               // simple damage imagery
                                           false,
                                           true, true, false, false, false, true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_21,           // 2x1 with the bib row in front, like the TD silo:
                                                                // the silo stands on the plot row.
                                           NULL,
                                           (short const*)List21,
                                           (short const*)NULL);

static BuildingTypeClass const ClassTsWeap(STRUCT_TSWEAP,
                                           TXT_NONE,
                                           "TSWEAP",
                                           FACING_NONE,
                                           // A vehicle's seat in the bay; walkers seat deeper
                                           // (Exit_Object).
                                           TSWEAP3_SEAT,
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           false,
                                           false, false, false, false,
                                           true, true, false, false, false, true,
                                           RTTI_UNITTYPE,      // Vehicle factory.
                                           DIR_N,
                                           BSIZE_33,           // the hall on rows 0-1, walkable concrete on row 2.
                                           (short const*)TsWeap3Exit,
                                           (short const*)TsWeap3List,
                                           (short const*)TsWeap3OList);

// TS Firestorm Generator ([GAFIRE]): the Firestorm Defense's host, on the Tech Center's 3x2 plot and footprint.
static BuildingTypeClass const ClassTsFgen(STRUCT_TSFGEN,
                                           TXT_NONE,
                                           "TSFGEN",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           true,               // anim regulated
                                           false, false, false, false,
                                           true, true, false, false, false, true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_32,           // The south row is footprint and the bib row lies in
                                           NULL,               // front; the north row is headroom, as the Tech Center's.
                                           (short const*)List32_000111, // OCCUPYLIST: south row only.
                                           (short const*)List31);       // OVERLAPLIST: north art row.

// TS Firestorm Wall Section ([GAFSDF]): a flat 1x1 pad, not selectable and insignificant as in TS,
// with no build-up. BuildingClass::Shape_Number picks the frame from its neighbours.
static BuildingTypeClass const ClassTsFsdf(STRUCT_TSFSDF,
                                           TXT_NONE,
                                           "TSFSDF",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,               // fake
                                           false,               // regulated anim
                                           false,               // always use the given name
                                           false,               // IsWall
                                           false,               // simple damage imagery
                                           false,               // invisible to radar
                                           false,               // selectable
                                           true,                // legal target
                                           true,                // insignificant
                                           false,               // theater specific
                                           false,               // turret
                                           true,                // remappable
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_11,
                                           NULL,
                                           (short const*)List1,
                                           (short const*)NULL);

// The Mobile War Factory deployed (Firestorm DGWEAP): a TS war factory on TSWEAP's 3x3 plot and exits, its
// door 20 leptons deeper. Never built from the sidebar; the deploy order packs it into UNIT_TSMWAR.
static BuildingTypeClass const ClassTsDweap(STRUCT_TSDWEAP,
                                            TXT_NONE,
                                            "TSDWEAP",
                                            FACING_NONE,
                                            TSDWEAP_SEAT,
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,
                                            false,
                                            false, false, false, false,
                                            true, true, false, false, false, true,
                                            RTTI_UNITTYPE,      // Vehicle factory.
                                            DIR_N,
                                            BSIZE_33,
                                            (short const*)TsWeap3Exit,
                                            (short const*)TsWeap3List,
                                            (short const*)TsWeap3OList);

static BuildingTypeClass const ClassTsRadr(STRUCT_TSRADR,
                                           TXT_NONE,
                                           "TSRADR",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           true,               // anim regulated (dish loop)
                                           false, false, false, false,
                                           true, true, false, false, false, true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_22,           // 2x2 as in TS. The south row is the footprint; the
                                                               // north row is walkable art spill.
                                           NULL,
                                           (short const*)List22_0011,
                                           (short const*)List22_1100);

static BuildingTypeClass const ClassTsHpad(STRUCT_TSHPAD,
                                           TXT_NONE,
                                           "TSHPAD",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),    // Helicopter docks on the pad.
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           false,
                                           false, false, false, false,
                                           true, true, false, false, false, true,
                                           RTTI_AIRCRAFTTYPE,  // Aircraft factory.
                                           DIR_N,
                                           BSIZE_22,           // The whole 2x2 is footprint, the bib row in front: the art
                                           NULL,               // is raised half a cell so the pad sits over the plot.
                                           (short const*)List22,
                                           (short const*)NULL);

static BuildingTypeClass const ClassTsTech(STRUCT_TSTECH,
                                           TXT_NONE,
                                           "TSTECH",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           true,               // anim regulated
                                           false, false, false, false,
                                           true, true, false, false, false, true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_32,           // TS's wedge its own way round on the south row, the bib
                                                                // row in front. Only the south row is footprint; the
                                                                // fins and dome stand in the north row, headroom units
                                                                // walk behind (the radar height trick, as the power plant).
                                           NULL,
                                           (short const*)List32_000111, // OCCUPYLIST: south row only.
                                           (short const*)List31);       // OVERLAPLIST: north art row.

static BuildingTypeClass const ClassTsDept(STRUCT_TSDEPT,
                                           TXT_NONE,
                                           "TSDEPT",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           true,               // anim regulated
                                           false, false, false, false,
                                           true, true, false, false, false, true,
                                           RTTI_NONE,          // Repair bay (not a factory).
                                           DIR_N,
                                           BSIZE_33,           // TS Foundation=3x3, drawn at TS's angle: the two
                                           NULL,               // north-east cells hold only shadow, so units pass.
                                           (short const*)TsDeptList,
                                           (short const*)TsDeptOList);

// TS Dropship Bay (Westwood's cut GADROP): a vehicle factory whose orders land by drop pod on its deck.
// Deliberately not a helipad, which would grant a free helicopter (docs/ts-gdi-tree-plan.md).
static BuildingTypeClass const ClassTsDrop(STRUCT_TSDROP,
                                           TXT_NONE,
                                           "TSDROP",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),    // Dropship sets down on the pad centre.
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           true,               // anim regulated (dish and pad lights)
                                           false, false, false, false,
                                           true, true, false, false, false, true,
                                           RTTI_UNITTYPE,      // Vehicle factory: orders arrive by drop pod.
                                           DIR_N,
                                           BSIZE_32,           // The deck's 3x2 (its 3x3 art's north row is
                                                               // antennas); the cargo comes down the ramp below it.
                                           NULL,
                                           (short const*)ListWeap, // BLOCKING footprint = the deck's 3x2 = the plot.
                                           NULL);

/*
**  TSTURB (TS Power Turbine, GAPOWRUP) — a building ADDON, not a structure.
**    Built from the sidebar like any building, but placement installs it into
**    an already-placed TSPOWR (PowersUpBuilding wired in Init_Heap) instead of
**    unlimboing: the plug object is consumed and the host's Power_Output rises
**    by the plug's Power. The 1x1 footprint only shapes the placement ghost;
**    it never occupies map cells. Stats in rules.ini [TSTURB] (TS [GAPOWRUP]).
*/
static BuildingTypeClass const ClassTsTurb(STRUCT_TSTURB,
                                           TXT_NONE,
                                           "TSTURB",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           false,
                                           false, false,
                                           true,               // simple damage imagery (single-frame art)
                                           false,
                                           true, true, false, false, false, true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_11,
                                           NULL,
                                           (short const*)List1,
                                           (short const*)NULL);

// TS Component Tower ([GACTWR]): the bare, unarmed wall joint, with one plug slot. TSVULC is both its
// Vulcan plug and the armed tower: installing the plug swaps the bare tower for that building in place.
static BuildingTypeClass const ClassTsCtwr(STRUCT_TSCTWR,
                                           TXT_NONE,
                                           "TSCTWR",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,               // fake
                                           false,               // regulated anim
                                           false,               // always use the given name
                                           false,               // IsWall
                                           true,                // simple damage imagery (frame 1 = damaged)
                                           false,               // invisible to radar
                                           true,                // selectable
                                           true,                // legal target
                                           false,               // insignificant
                                           false,               // theater specific
                                           false,               // turret
                                           true,                // remappable
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_12,            // The tower's cell, headroom above it, as a fitted
                                           NULL,                // tower's, so both carry the same box.
                                           (short const*)List12,
                                           (short const*)OList12);

static BuildingTypeClass const ClassTsVulc(STRUCT_TSVULC,
                                           TXT_NONE,
                                           "TSVULC",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0030,              // Vertical offset -- matches TURRET/TDGUN.
                                           0x0080,              // Primary weapon offset -- matches TURRET/TDGUN.
                                           0x0000,
                                           false,               // fake
                                           false,               // regulated anim
                                           false,               // always use the given name
                                           false,               // IsWall
                                           false,               // simple damage imagery
                                           false,               // invisible to radar
                                           true,                // selectable
                                           true,                // legal target
                                           false,               // insignificant
                                           false,               // theater specific
                                           true,                // rotating turret
                                           true,                // remappable
                                           RTTI_NONE,
                                           DIR_SE,              // Faces south-east when placed.
                                           BSIZE_12,            // The tower's cell, the head's headroom above it
                                           NULL,                // (as the Tesla Coil), so the box takes in the head.
                                           (short const*)List12,
                                           (short const*)OList12);

// TSROCK / TSCSAM: the RPG and SAM plugs, same shape as TSVULC (docs above).
static BuildingTypeClass const ClassTsRock(STRUCT_TSROCK,
                                           TXT_NONE,
                                           "TSROCK",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0030,              // Vertical offset -- matches TURRET/TDGUN.
                                           0x0080,              // Primary weapon offset -- matches TURRET/TDGUN.
                                           0x0000,
                                           false,               // fake
                                           false,               // regulated anim
                                           false,               // always use the given name
                                           false,               // IsWall
                                           false,               // simple damage imagery
                                           false,               // invisible to radar
                                           true,                // selectable
                                           true,                // legal target
                                           false,               // insignificant
                                           false,               // theater specific
                                           true,                // rotating turret
                                           true,                // remappable
                                           RTTI_NONE,
                                           DIR_SE,              // Faces south-east when placed.
                                           BSIZE_12,            // The tower's cell, the head's headroom above it
                                           NULL,                // (as the Tesla Coil), so the box takes in the head.
                                           (short const*)List12,
                                           (short const*)OList12);

static BuildingTypeClass const ClassTsCsam(STRUCT_TSCSAM,
                                           TXT_NONE,
                                           "TSCSAM",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0030,              // Vertical offset -- matches TURRET/TDGUN.
                                           0x0080,              // Primary weapon offset -- matches TURRET/TDGUN.
                                           0x0000,
                                           false,               // fake
                                           false,               // regulated anim
                                           false,               // always use the given name
                                           false,               // IsWall
                                           false,               // simple damage imagery
                                           false,               // invisible to radar
                                           true,                // selectable
                                           true,                // legal target
                                           false,               // insignificant
                                           false,               // theater specific
                                           true,                // rotating turret
                                           true,                // remappable
                                           RTTI_NONE,
                                           DIR_SE,              // Faces south-east when placed.
                                           BSIZE_12,            // The tower's cell, the head's headroom above it
                                           NULL,                // (as the Tesla Coil), so the box takes in the head.
                                           (short const*)List12,
                                           (short const*)OList12);

// TS GDI Concrete Wall ([GAWALL]): a wall type like BRIK. It never stands on the map: placing it lays
// OVERLAY_TSWALL in the cell.
static BuildingTypeClass const ClassTsWall(STRUCT_TSWALL,
                                           TXT_BRICK_WALL,
                                           "TSWALL",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_NONE,
                                           0x0000, 0x0000, 0x0000,
                                           false,               // fake
                                           false,               // regulated anim
                                           true,                // always use the given name
                                           true,                // IsWall
                                           false,               // simple damage imagery
                                           false,               // invisible to radar
                                           false,               // selectable
                                           true,                // legal target
                                           true,                // insignificant
                                           false,               // theater specific
                                           false,               // turret
                                           false,               // remappable
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_11,
                                           NULL,
                                           (short const*)List1,
                                           (short const*)NULL);

/*
**  TSNWALL (TS Nod Wall, NAWALL) -- TSWALL's twin for the Nod tree: placement converts it
**    to OVERLAY_TSNWALL. Stats in rules.ini [TSNWALL] (TS [NAWALL] matches GAWALL).
*/
static BuildingTypeClass const ClassTsNwall(STRUCT_TSNWALL,
                                            TXT_BRICK_WALL,
                                            "TSNWALL",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_NONE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            true,                // always use the given name
                                            true,                // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            false,               // selectable
                                            true,                // legal target
                                            true,                // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            false,               // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_11,
                                            NULL,
                                            (short const*)List1,
                                            (short const*)NULL);

// TS GDI gates ([GAGATE_A] east-west, [GAGATE_B] north-south): buildings in a wall line that open for
// their owner and allies and close once their footprint is clear (BuildingClass::Open_Gate, Gate_AI).
static BuildingTypeClass const ClassTsGateH(STRUCT_TSGATEH,
                                            TXT_NONE,
                                            "TSGATEH",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_31,
                                            NULL,
                                            (short const*)List31,
                                            (short const*)NULL);

static BuildingTypeClass const ClassTsGateV(STRUCT_TSGATEV,
                                            TXT_NONE,
                                            "TSGATEV",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_13,
                                            NULL,
                                            (short const*)List13,
                                            (short const*)NULL);

/*
**  The other gates: TSGATEH/V's twins with their own art and door timing (building.cpp TFGates).
*/
static BuildingTypeClass const ClassTSNGATEH(STRUCT_TSNGATEH,
                                            TXT_NONE,
                                            "TSNGATEH",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_31,
                                            NULL,
                                            (short const*)List31,
                                            (short const*)NULL);

static BuildingTypeClass const ClassTSNGATEV(STRUCT_TSNGATEV,
                                            TXT_NONE,
                                            "TSNGATEV",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_13,
                                            NULL,
                                            (short const*)List13,
                                            (short const*)NULL);

static BuildingTypeClass const ClassALGATEH(STRUCT_ALGATEH,
                                            TXT_NONE,
                                            "ALGATEH",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_31,
                                            NULL,
                                            (short const*)List31,
                                            (short const*)NULL);

static BuildingTypeClass const ClassALGATEV(STRUCT_ALGATEV,
                                            TXT_NONE,
                                            "ALGATEV",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_13,
                                            NULL,
                                            (short const*)List13,
                                            (short const*)NULL);

static BuildingTypeClass const ClassSVGATEH(STRUCT_SVGATEH,
                                            TXT_NONE,
                                            "SVGATEH",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_31,
                                            NULL,
                                            (short const*)List31,
                                            (short const*)NULL);

static BuildingTypeClass const ClassSVGATEV(STRUCT_SVGATEV,
                                            TXT_NONE,
                                            "SVGATEV",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_13,
                                            NULL,
                                            (short const*)List13,
                                            (short const*)NULL);

static BuildingTypeClass const ClassTDGGATEH(STRUCT_TDGGATEH,
                                            TXT_NONE,
                                            "TDGGATEH",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_31,
                                            NULL,
                                            (short const*)List31,
                                            (short const*)NULL);

static BuildingTypeClass const ClassTDGGATEV(STRUCT_TDGGATEV,
                                            TXT_NONE,
                                            "TDGGATEV",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_13,
                                            NULL,
                                            (short const*)List13,
                                            (short const*)NULL);

static BuildingTypeClass const ClassTDNGATEH(STRUCT_TDNGATEH,
                                            TXT_NONE,
                                            "TDNGATEH",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_31,
                                            NULL,
                                            (short const*)List31,
                                            (short const*)NULL);

static BuildingTypeClass const ClassTDNGATEV(STRUCT_TDNGATEV,
                                            TXT_NONE,
                                            "TDNGATEV",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_ALTERNATE,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            false,               // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            false,               // insignificant
                                            false,               // theater specific
                                            false,               // turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_13,
                                            NULL,
                                            (short const*)List13,
                                            (short const*)NULL);


// TS Upgrade Centre ([GAPLUG]): the two-slot host for the Ion Cannon, Drop Pod and Seeker plugs, on a 2x2 plot
// with a bib row (TS's 2x3), sockets to the south. A scanner, as in TS: it detects cloaked units in its sight range.
static BuildingTypeClass const ClassTsPlug(STRUCT_TSPLUG,
                                           TXT_NONE,
                                           "TSPLUG",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           true,               // anim regulated (masts/lights cycle)
                                           false, false, false, false,
                                           true, true, false, false, false, true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_22,
                                           NULL,
                                           (short const*)List22,
                                           NULL);

// Ion Cannon Uplink ([GAPLUG3]): a TSPLUG plug that never stands on the map. While one is installed the
// house has the TS Ion Cannon (SPC_TS_ION_CANNON).
static BuildingTypeClass const ClassTsPion(STRUCT_TSPION,
                                           TXT_NONE,
                                           "TSPION",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           false,
                                           false, false,
                                           true,               // simple damage imagery (ghost art)
                                           false,
                                           true, true, false, false, false, true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_11,
                                           NULL,
                                           (short const*)List1,
                                           (short const*)NULL);

// Drop Pod Node: our own TSPLUG plug, since TS grants drop pods only by script. It never stands on the map;
// while one is installed the house has the TS Drop Pods (SPC_TS_DROPPODS).
static BuildingTypeClass const ClassTsPods(STRUCT_TSPODS,
                                           TXT_NONE,
                                           "TSPODS",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           false,
                                           false, false,
                                           true,               // simple damage imagery (ghost art)
                                           false,
                                           true, true, false, false, false, true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_11,
                                           NULL,
                                           (short const*)List1,
                                           (short const*)NULL);

// Seeker Control ([GAPLUG2]): a TSPLUG plug that never stands on the map. While one is installed the house
// has the Hunter Seeker (SPC_TS_HUNTSEEK).
static BuildingTypeClass const ClassTsSeek(STRUCT_TSSEEK,
                                           TXT_NONE,
                                           "TSSEEK",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0000, 0x0000, 0x0000,
                                           false,
                                           false,
                                           false, false,
                                           true,               // simple damage imagery (ghost art)
                                           false,
                                           true, true, false, false, false, true,
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_11,
                                           NULL,
                                           (short const*)List1,
                                           (short const*)NULL);

// Nod Airstrip, ported from TD's ClassAirStrip: a 4x2 vehicle factory whose orders a cargo plane delivers
// (docs/cargo-plane-port.md). TdExitAirstrip rings the strip, so vehicles can leave on any side.
static short const TdExitAirstrip[] = {XYCELL(-1, -1), XYCELL(-1, 0), XYCELL(-1, 1), XYCELL(-1, 2),
                                       XYCELL(0, -1), XYCELL(0, 2),
                                       XYCELL(1, -1), XYCELL(1, 2),
                                       XYCELL(2, -1), XYCELL(2, 2),
                                       XYCELL(3, -1), XYCELL(3, 2),
                                       XYCELL(4, -1), XYCELL(4, 0), XYCELL(4, 1), XYCELL(4, 2),
                                       REFRESH_EOL};
static short const TdList42[] = {0, 1, 2, 3, MCW, MCW + 1, MCW + 2, MCW + 3, REFRESH_EOL};

static BuildingTypeClass const ClassTdAfld(STRUCT_TDAFLD,
                                           TXT_NONE,           // Display name (rules.ini Name= overrides).
                                           "TDAFLD",           // IniName.
                                           FACING_NONE,        // Foundation direction.
                                           XYP_COORD(0, 0),    // Exit point unused — cargo plane delivery.
                                           REMAP_ALTERNATE,    // Sidebar remap logic.
                                           0x0000,             // Vertical offset.
                                           0x0000,             // Primary weapon offset.
                                           0x0000,             // Primary weapon lateral offset.
                                           false,              // Is this building a fake?
                                           true,               // Animation rate regulated for constant speed (TD ClassAirStrip).
                                           false,              // Always use the given name?
                                           false,              // Is this a wall type structure?
                                           false,              // Simple (one frame) damage imagery?
                                           false,              // Is it invisible to radar?
                                           true,               // Can the player select this?
                                           true,               // Is this a legal target?
                                           false,              // Is this an insignificant building?
                                           false,              // Theater specific graphic image?
                                           false,              // Does it have a rotating turret?
                                           true,               // Can the building be color remapped?
                                           RTTI_UNITTYPE,      // Vehicle factory — TD-authentic (TD source line 868). Cargo plane is just the delivery mechanism, not the produced item.
                                           DIR_N,              // Starting idle frame.
                                           BSIZE_42,           // 4x2 footprint (TD-authentic).
                                           (short const*)TdExitAirstrip,
                                           (short const*)TdList42,
                                           (short const*)NULL  // No overlap row.
);

// TS Limpet Mine ([DLIMPET]): the Limpet Drone deployed, never built from the sidebar. Cloaked; its shot
// attaches the drone to a passing vehicle instead of doing damage (TF_Limpet_Attach), spending the mine.
static BuildingTypeClass const ClassTsDlimp(STRUCT_TSDLIMP,
                                            TXT_NONE,
                                            "TSDLIMP",
                                            FACING_NONE,
                                            XYP_COORD(0, 0),
                                            REMAP_NORMAL,
                                            0x0000, 0x0000, 0x0000,
                                            false,               // fake
                                            false,               // regulated anim
                                            false,               // always use the given name
                                            false,               // IsWall
                                            false,               // simple damage imagery
                                            true,                // invisible to radar
                                            true,                // selectable
                                            true,                // legal target
                                            true,                // insignificant (never announced, never a base)
                                            false,               // theater specific
                                            false,               // rotating turret
                                            true,                // remappable
                                            RTTI_NONE,
                                            DIR_N,
                                            BSIZE_11,
                                            NULL,
                                            (short const*)List1,
                                            (short const*)NULL);

// TS Sensor Array (STRUCT_TSDPSA), TS [GADPSA]: the Mobile Sensor Array deployed. Never built
// from the sidebar (the vehicle deploys into it, and the deploy order packs it back into
// UNIT_TSLPST). Its owner sees cloaked and buried enemies in range (TF_Is_Sensed).
// Art = its HD rebuild: the body under the head's flash (5 healthy, then 5 damaged and unlit), 36 build-up frames.
static BuildingTypeClass const ClassTsDpsa(STRUCT_TSDPSA,
                                           TXT_NONE,
                                           "TSDPSA",
                                           FACING_NONE,
                                           XYP_COORD(0, 0),
                                           REMAP_NORMAL,
                                           0x0000, 0x0000, 0x0000,
                                           false,               // fake
                                           false,               // regulated anim
                                           false,               // always use the given name
                                           false,               // IsWall
                                           false,               // simple damage imagery
                                           false,               // invisible to radar
                                           true,                // selectable
                                           true,                // legal target
                                           false,               // insignificant
                                           false,               // theater specific
                                           false,               // rotating turret
                                           true,                // remappable
                                           RTTI_NONE,
                                           DIR_N,
                                           BSIZE_11,
                                           NULL,
                                           (short const*)List1,
                                           (short const*)NULL);

// TD Communications Center, ported from TD's ClassCommand: the 2x2 radar.
static BuildingTypeClass const ClassTdHq(STRUCT_TDHQ,
                                         TXT_NONE,           // Display name (rules.ini Name= overrides).
                                         "TDHQ",             // IniName.
                                         FACING_NONE,        // Foundation direction.
                                         XYP_COORD(0, 0),    // No produced-unit exit.
                                         REMAP_ALTERNATE,    // Sidebar remap logic.
                                         0x0000,             // Vertical offset.
                                         0x0000,             // Primary weapon offset.
                                         0x0000,             // Primary weapon lateral offset.
                                         false,              // Is this building a fake?
                                         true,               // Animation rate regulated for constant speed?
                                         false,              // Always use the given name?
                                         false,              // Is this a wall type structure?
                                         false,              // Simple (one frame) damage imagery?
                                         false,              // Is it invisible to radar?
                                         true,               // Can the player select this?
                                         true,               // Is this a legal target?
                                         false,              // Is this an insignificant building?
                                         false,              // Theater specific graphic image?
                                         false,              // Does it have a rotating turret?
                                         true,               // Can the building be color remapped?
                                         RTTI_NONE,          // Not a factory.
                                         DIR_N,              // Starting idle frame.
                                         BSIZE_22,           // 2x2 footprint (TD-authentic).
                                         NULL,               // No preferred exit cell.
                                         (short const*)ComList,
                                         (short const*)OComList
);

// Advanced Communications Center, ported from TD's ClassEye: the 2x2 host of the Ion Cannon.
static BuildingTypeClass const ClassTdEye(STRUCT_TDEYE,
                                          TXT_NONE,           // Display name token; rules.ini Name= overrides.
                                          "TDEYE",            // IniName.
                                          FACING_NONE,        // Foundation direction.
                                          XYP_COORD(0, 0),    // No produced-unit exit.
                                          REMAP_ALTERNATE,    // Sidebar remap logic.
                                          0x0000,             // Vertical offset.
                                          0x0000,             // Primary weapon offset.
                                          0x0000,             // Primary weapon lateral offset.
                                          false,              // Is this building a fake?
                                          true,               // Animation rate regulated for constant speed?
                                          false,              // Always use the given name?
                                          false,              // Is this a wall type structure?
                                          false,              // Simple (one frame) damage imagery?
                                          false,              // Is it invisible to radar?
                                          true,               // Can the player select this?
                                          true,               // Is this a legal target?
                                          false,              // Is this an insignificant building?
                                          false,              // Theater specific graphic image?
                                          false,              // Does it have a rotating turret?
                                          true,               // Can the building be color remapped?
                                          RTTI_NONE,          // Not a factory.
                                          (DirType)160,       // Starting idle frame (TD-authentic).
                                          BSIZE_22,           // 2x2 footprint (TD-authentic).
                                          NULL,               // No preferred exit cell.
                                          (short const*)ComList,
                                          (short const*)OComList
);

// Temple of Nod, ported from TD's ClassTemple: the 3x3 host of the Nuclear Strike, its top row overlap only.
static BuildingTypeClass const ClassTdTmpl(STRUCT_TDTMPL,
                                           TXT_NONE,           // Display name token; rules.ini Name= overrides.
                                           "TDTMPL",           // IniName.
                                           FACING_NONE,        // Foundation direction.
                                           XYP_COORD(0, 0),    // No produced-unit exit.
                                           REMAP_ALTERNATE,    // Sidebar remap logic.
                                           0x0000,             // Vertical offset.
                                           0x0000,             // Primary weapon offset.
                                           0x0000,             // Primary weapon lateral offset.
                                           false,              // Is this building a fake?
                                           false,              // Animation rate regulated? (TD-source false)
                                           false,              // Always use the given name?
                                           false,              // Is this a wall type structure?
                                           true,               // Simple (one frame) damage imagery (TD-authentic).
                                           false,              // Is it invisible to radar?
                                           true,               // Can the player select this?
                                           true,               // Is this a legal target?
                                           false,              // Is this an insignificant building?
                                           false,              // Theater specific graphic image?
                                           false,              // Does it have a rotating turret?
                                           true,               // Can the building be color remapped?
                                           RTTI_NONE,          // Not a factory.
                                           DIR_N,              // Starting idle frame.
                                           BSIZE_33,           // 3x3 footprint (TD-authentic).
                                           NULL,               // No preferred exit cell.
                                           (short const*)List000111111,
                                           (short const*)OListTmpl
);

static BuildingTypeClass const ClassObelisk(STRUCT_TDOBLI,
                                            TXT_NONE,        // Display name token; rules.ini Name= overrides.
                                            "TDOBLI",        // IniName.
                                            FACING_S,        // Foundation direction from center of building.
                                            XYP_COORD(0, 0), // Exit point for produced units.
                                            REMAP_ALTERNATE, // Sidebar remap logic.
                                            0x00C8,          // Vertical offset (same as TSLA — tall structure).
                                            0x0000,          // Primary weapon offset along turret centerline.
                                            0x0000,          // Primary weapon lateral offset along turret centerline.
                                            false,           // Is this building a fake (decoy?)
                                            false,           // Animation rate regulated for constant speed?
                                            false,           // Always use the given name for the building?
                                            false,           // Is this a wall type structure?
                                            false,           // Simple (one frame) damage imagery?
                                            false,           // Is it invisible to radar?
                                            true,            // Can the player select this?
                                            true,            // Is this a legal target for attack or move?
                                            false,           // Is this an insignificant building?
                                            false,           // Theater specific graphic image?
                                            false,           // Does it have a rotating turret? (Obelisk fires straight)
                                            true,            // Can the building be color remapped to indicate owner?
                                            RTTI_NONE,       // The object type produced at this factory.
                                            DIR_N,           // Starting idle frame to match construction.
                                            BSIZE_12,        // SIZE: 1x2, TD-authentic Obelisk footprint.
                                            NULL,            // Preferred exit cell list.
                                            (short const*)List12, // OCCUPYLIST.
                                            (short const*)OList12 // OVERLAPLIST.
);

// Nod Stealth Generator: TS NASTLH art under TDSTEAL, on a 2x1 plot. It cloaks friendly buildings and
// units in its radius (docs/stealth-generator-spec.md).
static BuildingTypeClass const ClassTdStealth(STRUCT_TDSTEALTH,
                      TXT_NONE,               // Display name token; rules.ini Name= overrides.
                      "TDSTEAL",              // IniName (own TS NASTLH-derived art: TDSTEAL tileset).
                      FACING_NONE,            // Foundation direction: NONE, so attackers aim at the true centre.
                      XYP_COORD(0, 0),        // Exit point for produced units.
                      REMAP_ALTERNATE,        // Sidebar remap logic.
                      0x0000,                 //	Vertical offset.
                      0x0000,                 // Primary weapon offset along turret centerline.
                      0x0000,                 // Primary weapon lateral offset along turret centerline.
                      false,                  // Is this building a fake (decoy?)
                      true,                   // Animation rate is regulated for constant speed?
                      false,                  // Always use the given name for the building?
                      false,                  // Is this a wall type structure?
                      false,                  // Simple (one frame) damage imagery?
                      false,                  // Is it invisible to radar?
                      true,                   // Can the player select this?
                      true,                   // Is this a legal target for attack or move?
                      false,                  // Is this an insignificant building?
                      false,                  // Theater specific graphic image?
                      false,                  // Does it have a rotating turret?
                      true,                   // Can the building be color remapped to indicate owner?
                      RTTI_NONE,              // The object type produced at this factory.
                      DIR_N,                  // Starting idle frame to match construction.
                      BSIZE_21,               // SIZE: 2x1, silo-shaped.
                      NULL,                   // Preferred exit cell list.
                      (short const*)List21,   // OCCUPYLIST: both cells of the 2x1 strip.
                      (short const*)NULL      // OVERLAPLIST:List of overlap cell offset.
);

// Nod Flame Bunker: an anti-infantry pillbox firing a flame weapon, drawn with the RA pillbox art
// (Image=PBOX). A type of its own, so the Allied pillbox keeps its weapon.
static BuildingTypeClass const ClassFlameBunker(STRUCT_TDFBNK,
                                            TXT_NONE,        // Display name token; rules.ini Name= overrides.
                                            "TDFBNK",        // IniName (art aliases PBOX via Image=PBOX).
                                            FACING_NONE,     // Foundation direction from center of building.
                                            XYP_COORD(0, 0), // Exit point for produced units.
                                            REMAP_ALTERNATE, // Sidebar remap logic.
                                            0x0010,          //	Vertical offset.
                                            0x0040,          // Primary weapon offset along turret centerline.
                                            0x0000,          // Primary weapon lateral offset along turret centerline.
                                            false,           // Is this building a fake (decoy?)
                                            false,           // Animation rate is regulated for constant speed?
                                            false,           // Always use the given name for the building?
                                            false,           // Is this a wall type structure?
                                            true,            // Simple (one frame) damage imagery?
                                            false,           // Is it invisible to radar?
                                            true,            // Can the player select this?
                                            true,            // Is this a legal target for attack or move?
                                            false,           // Is this an insignificant building?
                                            false,           // Theater specific graphic image?
                                            false,           // Does it have a rotating turret?
                                            true,            // Can the building be color remapped to indicate owner?
                                            RTTI_NONE,       // The object type produced at this factory.
                                            DIR_N,           // Starting idle frame to match construction.
                                            BSIZE_11,        // SIZE:			Building size.
                                            NULL,            // Preferred exit cell list.
                                            (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                            (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassTurret(STRUCT_TURRET,
                                           TXT_TURRET,      // NAME:			Short name of the structure.
                                           "GUN",           // NAME:			Short name of the structure.
                                           FACING_NONE,     // Foundation direction from center of building.
                                           XYP_COORD(0, 0), // Exit point for produced units.
                                           REMAP_ALTERNATE, // Sidebar remap logic.
                                           0x0030,          //	Vertical offset.
                                           0x0080,          // Primary weapon offset along turret centerline.
                                           0x0000,          // Primary weapon lateral offset along turret centerline.
                                           false,           // Is this building a fake (decoy?)
                                           false,           // Animation rate is regulated for constant speed?
                                           false,           // Always use the given name for the building?
                                           false,           // Is this a wall type structure?
                                           false,           // Simple (one frame) damage imagery?
                                           false,           // Is it invisible to radar?
                                           true,            // Can the player select this?
                                           true,            // Is this a legal target for attack or move?
                                           false,           // Is this an insignificant building?
                                           false,           // Theater specific graphic image?
                                           true,            // Does it have a rotating turret?
                                           true,            // Can the building be color remapped to indicate owner?
                                           RTTI_NONE,       // The object type produced at this factory.
                                           (DirType)208,    // Starting idle frame to match construction.
                                           BSIZE_11,        // SIZE:			Building size.
                                           NULL,            // Preferred exit cell list.
                                           (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                           (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassAAGun(STRUCT_AAGUN,
                                          TXT_AAGUN,       // NAME:			Short name of the structure.
                                          "AGUN",          // NAME:			Short name of the structure.
                                          FACING_S,        // Foundation direction from center of building.
                                          XYP_COORD(0, 0), // Exit point for produced units.
                                          REMAP_ALTERNATE, // Sidebar remap logic.
                                          0x0000,          //	Vertical offset.
                                          0x0000,          // Primary weapon offset along turret centerline.
                                          0x0000,          // Primary weapon lateral offset along turret centerline.
                                          false,           // Is this building a fake (decoy?)
                                          false,           // Animation rate is regulated for constant speed?
                                          false,           // Always use the given name for the building?
                                          false,           // Is this a wall type structure?
                                          false,           // Simple (one frame) damage imagery?
                                          false,           // Is it invisible to radar?
                                          true,            // Can the player select this?
                                          true,            // Is this a legal target for attack or move?
                                          false,           // Is this an insignificant building?
                                          false,           // Theater specific graphic image?
                                          true,            // Does it have a rotating turret?
                                          true,            // Can the building be color remapped to indicate owner?
                                          RTTI_NONE,       // The object type produced at this factory.
                                          DIR_NE,          // Starting idle frame to match construction.
                                          BSIZE_12,        // SIZE:			Building size.
                                          NULL,            // Preferred exit cell list.
                                          (short const*)List12, // OCCUPYLIST:	List of active foundation squares.
                                          (short const*)OList12 // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassFlameTurret(STRUCT_FLAME_TURRET,
                                                TXT_FLAME_TURRET, // NAME:			Short name of the structure.
                                                "FTUR",           // NAME:			Short name of the structure.
                                                FACING_NONE,      // Foundation direction from center of building.
                                                XYP_COORD(0, 0),  // Exit point for produced units.
                                                REMAP_ALTERNATE,  // Sidebar remap logic.
                                                0x0000,           //	Vertical offset.
                                                0x0000,           // Primary weapon offset along turret centerline.
                                                0x0000,    // Primary weapon lateral offset along turret centerline.
                                                false,     // Is this building a fake (decoy?)
                                                false,     // Animation rate is regulated for constant speed?
                                                false,     // Always use the given name for the building?
                                                false,     // Is this a wall type structure?
                                                true,      // Simple (one frame) damage imagery?
                                                false,     // Is it invisible to radar?
                                                true,      // Can the player select this?
                                                true,      // Is this a legal target for attack or move?
                                                false,     // Is this an insignificant building?
                                                false,     // Theater specific graphic image?
                                                false,     // Does it have a rotating turret?
                                                true,      // Can the building be color remapped to indicate owner?
                                                RTTI_NONE, // The object type produced at this factory.
                                                DIR_N,     // Starting idle frame to match construction.
                                                BSIZE_11,  // SIZE:			Building size.
                                                NULL,      // Preferred exit cell list.
                                                (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                                (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassConst(STRUCT_CONST,
                                          TXT_CONST_YARD,    // NAME:			Short name of the structure.
                                          "FACT",            // NAME:			Short name of the structure.
                                          FACING_NONE,       // Foundation direction from center of building.
                                          XYP_COORD(0, 0),   // Exit point for produced units.
                                          REMAP_ALTERNATE,   // Sidebar remap logic.
                                          0x0000,            //	Vertical offset.
                                          0x0000,            // Primary weapon offset along turret centerline.
                                          0x0000,            // Primary weapon lateral offset along turret centerline.
                                          false,             // Is this building a fake (decoy?)
                                          false,             // Animation rate is regulated for constant speed?
                                          false,             // Always use the given name for the building?
                                          false,             // Is this a wall type structure?
                                          false,             // Simple (one frame) damage imagery?
                                          false,             // Is it invisible to radar?
                                          true,              // Can the player select this?
                                          true,              // Is this a legal target for attack or move?
                                          false,             // Is this an insignificant building?
                                          false,             // Theater specific graphic image?
                                          false,             // Does it have a rotating turret?
                                          true,              // Can the building be color remapped to indicate owner?
                                          RTTI_BUILDINGTYPE, // The object type produced at this factory.
                                          DIR_N,             // Starting idle frame to match construction.
                                          BSIZE_33,          // SIZE:			Building size.
                                          NULL,              // Preferred exit cell list.
                                          (short const*)ListFactory, // OCCUPYLIST:	List of active foundation squares.
                                          (short const*)NULL         // OVERLAPLIST:List of overlap cell offset.
);

// Soviet and Allied construction yards: RA's one yard split so the building carries its faction, as with
// TDNFACT and TDGFACT. Each has its own art under its IniName.
static BuildingTypeClass const ClassSovietFact(STRUCT_SFACT,
                                               TXT_NONE,          // Display name (rules.ini Name= overrides).
                                               "SFACT",           // IniName.
                                               FACING_NONE,       // Foundation direction from center of building.
                                               XYP_COORD(0, 0),   // Exit point for produced units.
                                               REMAP_ALTERNATE,   // Sidebar remap logic.
                                               0x0000,            //	Vertical offset.
                                               0x0000,            // Primary weapon offset along turret centerline.
                                               0x0000,            // Primary weapon lateral offset along turret centerline.
                                               false,             // Is this building a fake (decoy?)
                                               false,             // Animation rate is regulated for constant speed?
                                               false,             // Always use the given name for the building?
                                               false,             // Is this a wall type structure?
                                               false,             // Simple (one frame) damage imagery?
                                               false,             // Is it invisible to radar?
                                               true,              // Can the player select this?
                                               true,              // Is this a legal target for attack or move?
                                               false,             // Is this an insignificant building?
                                               false,             // Theater specific graphic image?
                                               false,             // Does it have a rotating turret?
                                               true,              // Can the building be color remapped to indicate owner?
                                               RTTI_BUILDINGTYPE, // The object type produced at this factory.
                                               DIR_N,             // Starting idle frame to match construction.
                                               BSIZE_33,          // SIZE:			Building size.
                                               NULL,              // Preferred exit cell list.
                                               (short const*)ListFactory, // OCCUPYLIST:	List of active foundation squares.
                                               (short const*)NULL         // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassAlliedFact(STRUCT_AFACT,
                                               TXT_NONE,          // Display name (rules.ini Name= overrides).
                                               "AFACT",           // IniName.
                                               FACING_NONE,       // Foundation direction from center of building.
                                               XYP_COORD(0, 0),   // Exit point for produced units.
                                               REMAP_ALTERNATE,   // Sidebar remap logic.
                                               0x0000,            //	Vertical offset.
                                               0x0000,            // Primary weapon offset along turret centerline.
                                               0x0000,            // Primary weapon lateral offset along turret centerline.
                                               false,             // Is this building a fake (decoy?)
                                               false,             // Animation rate is regulated for constant speed?
                                               false,             // Always use the given name for the building?
                                               false,             // Is this a wall type structure?
                                               false,             // Simple (one frame) damage imagery?
                                               false,             // Is it invisible to radar?
                                               true,              // Can the player select this?
                                               true,              // Is this a legal target for attack or move?
                                               false,             // Is this an insignificant building?
                                               false,             // Theater specific graphic image?
                                               false,             // Does it have a rotating turret?
                                               true,              // Can the building be color remapped to indicate owner?
                                               RTTI_BUILDINGTYPE, // The object type produced at this factory.
                                               DIR_N,             // Starting idle frame to match construction.
                                               BSIZE_33,          // SIZE:			Building size.
                                               NULL,              // Preferred exit cell list.
                                               (short const*)ListFactory, // OCCUPYLIST:	List of active foundation squares.
                                               (short const*)NULL         // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const
    ClassFakeConst(STRUCT_FAKECONST,
                   TXT_FAKE_CONST,            // NAME:			Short name of the structure.
                   "FACF",                    // NAME:			Short name of the structure.
                   FACING_NONE,               // Foundation direction from center of building.
                   XYP_COORD(0, 0),           // Exit point for produced units.
                   REMAP_ALTERNATE,           // Sidebar remap logic.
                   0x0000,                    //	Vertical offset.
                   0x0000,                    // Primary weapon offset along turret centerline.
                   0x0000,                    // Primary weapon lateral offset along turret centerline.
                   true,                      // Is this building a fake (decoy?)
                   false,                     // Animation rate is regulated for constant speed?
                   false,                     // Always use the given name for the building?
                   false,                     // Is this a wall type structure?
                   false,                     // Simple (one frame) damage imagery?
                   false,                     // Is it invisible to radar?
                   true,                      // Can the player select this?
                   true,                      // Is this a legal target for attack or move?
                   false,                     // Is this an insignificant building?
                   false,                     // Theater specific graphic image?
                   false,                     // Does it have a rotating turret?
                   true,                      // Can the building be color remapped to indicate owner?
                   RTTI_NONE,                 // The object type produced at this factory.
                   DIR_N,                     // Starting idle frame to match construction.
                   BSIZE_33,                  // SIZE:			Building size.
                   NULL,                      // Preferred exit cell list.
                   (short const*)ListFactory, // OCCUPYLIST:	List of active foundation squares.
                   (short const*)NULL         // OVERLAPLIST:List of overlap cell offset.
    );

static BuildingTypeClass const
    ClassFakeWeapon(STRUCT_FAKEWEAP,
                    TXT_FAKE_WEAP, // NAME:			Short name of the structure.
                    "WEAF",        // NAME:			Short name of the structure.
                    FACING_NONE,   // Foundation direction from center of building.
                    XYP_COORD(10 + (CELL_PIXEL_W / 2),
                              ((CELL_PIXEL_H * 3) - (CELL_PIXEL_H / 2)) - 21), // Exit point for produced units.
                    REMAP_ALTERNATE,                                           // Sidebar remap logic.
                    0x0000,                                                    //	Vertical offset.
                    0x0000,                 // Primary weapon offset along turret centerline.
                    0x0000,                 // Primary weapon lateral offset along turret centerline.
                    true,                   // Is this building a fake (decoy?)
                    false,                  // Animation rate is regulated for constant speed?
                    false,                  // Always use the given name for the building?
                    false,                  // Is this a wall type structure?
                    false,                  // Simple (one frame) damage imagery?
                    false,                  // Is it invisible to radar?
                    true,                   // Can the player select this?
                    true,                   // Is this a legal target for attack or move?
                    false,                  // Is this an insignificant building?
                    false,                  // Theater specific graphic image?
                    false,                  // Does it have a rotating turret?
                    true,                   // Can the building be color remapped to indicate owner?
                    RTTI_NONE,              // The object type produced at this factory.
                    DIR_N,                  // Starting idle frame to match construction.
                    BSIZE_32,               // SIZE:			Building size.
                    (short const*)ExitWeap, // Preferred exit cell list.
                    (short const*)ListWeap, // OCCUPYLIST:	List of active foundation squares.
                    (short const*)OListWeap // OVERLAPLIST:List of overlap cell offset.
    );

static BuildingTypeClass const
    ClassRefinery(STRUCT_REFINERY,
                  TXT_REFINERY,                // NAME:			Short name of the structure.
                  "PROC",                      // NAME:			Short name of the structure.
                  FACING_NONE,                 // Foundation direction from center of building.
                  XYP_COORD(0, 0),             // Exit point for produced units.
                  REMAP_ALTERNATE,             // Sidebar remap logic.
                  0x0000,                      //	Vertical offset.
                  0x0000,                      // Primary weapon offset along turret centerline.
                  0x0000,                      // Primary weapon lateral offset along turret centerline.
                  false,                       // Is this building a fake (decoy?)
                  false,                       // Animation rate is regulated for constant speed?
                  false,                       // Always use the given name for the building?
                  false,                       // Is this a wall type structure?
                  false,                       // Simple (one frame) damage imagery?
                  false,                       // Is it invisible to radar?
                  true,                        // Can the player select this?
                  true,                        // Is this a legal target for attack or move?
                  false,                       // Is this an insignificant building?
                  false,                       // Theater specific graphic image?
                  false,                       // Does it have a rotating turret?
                  true,                        // Can the building be color remapped to indicate owner?
                  RTTI_NONE,                   // The object type produced at this factory.
                  DIR_N,                       // Starting idle frame to match construction.
                  BSIZE_33,                    // SIZE:			Building size.
                  NULL,                        // Preferred exit cell list.
                  (short const*)List010111100, // OCCUPYLIST:	List of active foundation squares.
                  (short const*)List101000011  // OVERLAPLIST:List of overlap cell offset.
    );

static BuildingTypeClass const ClassStorage(STRUCT_STORAGE,
                                            TXT_STORAGE,     // NAME:			Short name of the structure.
                                            "SILO",          // NAME:			Short name of the structure.
                                            FACING_NONE,     // Foundation direction from center of building.
                                            XYP_COORD(0, 0), // Exit point for produced units.
                                            REMAP_ALTERNATE, // Sidebar remap logic.
                                            0x0000,          //	Vertical offset.
                                            0x0000,          // Primary weapon offset along turret centerline.
                                            0x0000,          // Primary weapon lateral offset along turret centerline.
                                            false,           // Is this building a fake (decoy?)
                                            false,           // Animation rate is regulated for constant speed?
                                            false,           // Always use the given name for the building?
                                            false,           // Is this a wall type structure?
                                            true,            // Simple (one frame) damage imagery?
                                            false,           // Is it invisible to radar?
                                            true,            // Can the player select this?
                                            true,            // Is this a legal target for attack or move?
                                            false,           // Is this an insignificant building?
                                            false,           // Theater specific graphic image?
                                            false,           // Does it have a rotating turret?
                                            true,            // Can the building be color remapped to indicate owner?
                                            RTTI_NONE,       // The object type produced at this factory.
                                            DIR_N,           // Starting idle frame to match construction.
                                            BSIZE_11,        // SIZE:			Building size.
                                            NULL,            // Preferred exit cell list.
                                            (short const*)StoreList, // OCCUPYLIST:	List of active foundation squares.
                                            (short const*)NULL       // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassHelipad(STRUCT_HELIPAD,
                                            TXT_HELIPAD,       // NAME:			Short name of the structure.
                                            "HPAD",            // NAME:			Short name of the structure.
                                            FACING_NONE,       // Foundation direction from center of building.
                                            XYP_COORD(0, 0),   // Exit point for produced units.
                                            REMAP_ALTERNATE,   // Sidebar remap logic.
                                            0x0000,            //	Vertical offset.
                                            0x0000,            // Primary weapon offset along turret centerline.
                                            0x0000,            // Primary weapon lateral offset along turret centerline.
                                            false,             // Is this building a fake (decoy?)
                                            false,             // Animation rate is regulated for constant speed?
                                            false,             // Always use the given name for the building?
                                            false,             // Is this a wall type structure?
                                            false,             // Simple (one frame) damage imagery?
                                            false,             // Is it invisible to radar?
                                            true,              // Can the player select this?
                                            true,              // Is this a legal target for attack or move?
                                            false,             // Is this an insignificant building?
                                            false,             // Theater specific graphic image?
                                            false,             // Does it have a rotating turret?
                                            true,              // Can the building be color remapped to indicate owner?
                                            RTTI_AIRCRAFTTYPE, // The object type produced at this factory.
                                            DIR_N,             // Starting idle frame to match construction.
                                            BSIZE_22,          // SIZE:			Building size.
                                            NULL,              // Preferred exit cell list.
                                            (short const*)List2, // OCCUPYLIST:	List of active foundation squares.
                                            (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

// Allied and Soviet helipads: RA's helipad split so the building carries its faction. Each pad's free
// helicopter and roster follow the pad's type, not its owner.
static BuildingTypeClass const ClassAlliedHelipad(STRUCT_AHPAD,
                                                  TXT_NONE,          // Display name (rules.ini Name= overrides).
                                                  "AHPAD",           // IniName.
                                                  FACING_NONE,       // Foundation direction from center of building.
                                                  XYP_COORD(0, 0),   // Exit point for produced units.
                                                  REMAP_ALTERNATE,   // Sidebar remap logic.
                                                  0x0000,            //	Vertical offset.
                                                  0x0000,            // Primary weapon offset along turret centerline.
                                                  0x0000,            // Primary weapon lateral offset along turret centerline.
                                                  false,             // Is this building a fake (decoy?)
                                                  false,             // Animation rate is regulated for constant speed?
                                                  false,             // Always use the given name for the building?
                                                  false,             // Is this a wall type structure?
                                                  false,             // Simple (one frame) damage imagery?
                                                  false,             // Is it invisible to radar?
                                                  true,              // Can the player select this?
                                                  true,              // Is this a legal target for attack or move?
                                                  false,             // Is this an insignificant building?
                                                  false,             // Theater specific graphic image?
                                                  false,             // Does it have a rotating turret?
                                                  true,              // Can the building be color remapped to indicate owner?
                                                  RTTI_AIRCRAFTTYPE, // The object type produced at this factory.
                                                  DIR_N,             // Starting idle frame to match construction.
                                                  BSIZE_22,          // SIZE:			Building size.
                                                  NULL,              // Preferred exit cell list.
                                                  (short const*)List2, // OCCUPYLIST:	List of active foundation squares.
                                                  (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassSovietHelipad(STRUCT_SHPAD,
                                                  TXT_NONE,          // Display name (rules.ini Name= overrides).
                                                  "SHPAD",           // IniName.
                                                  FACING_NONE,       // Foundation direction from center of building.
                                                  XYP_COORD(0, 0),   // Exit point for produced units.
                                                  REMAP_ALTERNATE,   // Sidebar remap logic.
                                                  0x0000,            //	Vertical offset.
                                                  0x0000,            // Primary weapon offset along turret centerline.
                                                  0x0000,            // Primary weapon lateral offset along turret centerline.
                                                  false,             // Is this building a fake (decoy?)
                                                  false,             // Animation rate is regulated for constant speed?
                                                  false,             // Always use the given name for the building?
                                                  false,             // Is this a wall type structure?
                                                  false,             // Simple (one frame) damage imagery?
                                                  false,             // Is it invisible to radar?
                                                  true,              // Can the player select this?
                                                  true,              // Is this a legal target for attack or move?
                                                  false,             // Is this an insignificant building?
                                                  false,             // Theater specific graphic image?
                                                  false,             // Does it have a rotating turret?
                                                  true,              // Can the building be color remapped to indicate owner?
                                                  RTTI_AIRCRAFTTYPE, // The object type produced at this factory.
                                                  DIR_N,             // Starting idle frame to match construction.
                                                  BSIZE_22,          // SIZE:			Building size.
                                                  NULL,              // Preferred exit cell list.
                                                  (short const*)List2, // OCCUPYLIST:	List of active foundation squares.
                                                  (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassCommand(STRUCT_RADAR,
                                            TXT_COMMAND,     // NAME:			Short name of the structure.
                                            "DOME",          // NAME:			Short name of the structure.
                                            FACING_NONE,     // Foundation direction from center of building.
                                            XYP_COORD(0, 0), // Exit point for produced units.
                                            REMAP_ALTERNATE, // Sidebar remap logic.
                                            0x0000,          //	Vertical offset.
                                            0x0000,          // Primary weapon offset along turret centerline.
                                            0x0000,          // Primary weapon lateral offset along turret centerline.
                                            false,           // Is this building a fake (decoy?)
                                            true,            // Animation rate is regulated for constant speed?
                                            false,           // Always use the given name for the building?
                                            false,           // Is this a wall type structure?
                                            false,           // Simple (one frame) damage imagery?
                                            false,           // Is it invisible to radar?
                                            true,            // Can the player select this?
                                            true,            // Is this a legal target for attack or move?
                                            false,           // Is this an insignificant building?
                                            false,           // Theater specific graphic image?
                                            false,           // Does it have a rotating turret?
                                            true,            // Can the building be color remapped to indicate owner?
                                            RTTI_NONE,       // The object type produced at this factory.
                                            DIR_N,           // Starting idle frame to match construction.
                                            BSIZE_22,        // SIZE:			Building size.
                                            NULL,            // Preferred exit cell list.
                                            (short const*)ComList, // OCCUPYLIST:	List of active foundation squares.
                                            (short const*)NULL     // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const
    ClassGapGenerator(STRUCT_GAP,
                      TXT_GAP_GENERATOR,      // NAME:			Short name of the structure.
                      "GAP",                  // NAME:			Short name of the structure.
                      FACING_S,               // Foundation direction from center of building.
                      XYP_COORD(0, 0),        // Exit point for produced units.
                      REMAP_ALTERNATE,        // Sidebar remap logic.
                      0x0000,                 //	Vertical offset.
                      0x0000,                 // Primary weapon offset along turret centerline.
                      0x0000,                 // Primary weapon lateral offset along turret centerline.
                      false,                  // Is this building a fake (decoy?)
                      true,                   // Animation rate is regulated for constant speed?
                      false,                  // Always use the given name for the building?
                      false,                  // Is this a wall type structure?
                      false,                  // Simple (one frame) damage imagery?
                      false,                  // Is it invisible to radar?
                      true,                   // Can the player select this?
                      true,                   // Is this a legal target for attack or move?
                      false,                  // Is this an insignificant building?
                      false,                  // Theater specific graphic image?
                      false,                  // Does it have a rotating turret?
                      true,                   // Can the building be color remapped to indicate owner?
                      RTTI_NONE,              // The object type produced at this factory.
                      DIR_N,                  // Starting idle frame to match construction.
                      BSIZE_12,               // SIZE:			Building size.
                      NULL,                   // Preferred exit cell list.
                      (short const*)List0010, // OCCUPYLIST:	List of active foundation squares.
                      (short const*)List1     // OVERLAPLIST:List of overlap cell offset.
    );

static BuildingTypeClass const ClassSAM(STRUCT_SAM,
                                        TXT_SAM,               // NAME:			Short name of the structure.
                                        "SAM",                 // NAME:			Short name of the structure.
                                        FACING_NONE,           // Foundation direction from center of building.
                                        XYP_COORD(0, 0),       // Exit point for produced units.
                                        REMAP_ALTERNATE,       // Sidebar remap logic.
                                        0x0030,                //	Vertical offset.
                                        0x0080,                // Primary weapon offset along turret centerline.
                                        0x0000,                // Primary weapon lateral offset along turret centerline.
                                        false,                 // Is this building a fake (decoy?)
                                        false,                 // Animation rate is regulated for constant speed?
                                        false,                 // Always use the given name for the building?
                                        false,                 // Is this a wall type structure?
                                        false,                 // Simple (one frame) damage imagery?
                                        false,                 // Is it invisible to radar?
                                        true,                  // Can the player select this?
                                        true,                  // Is this a legal target for attack or move?
                                        false,                 // Is this an insignificant building?
                                        false,                 // Theater specific graphic image?
                                        true,                  // Does it have a rotating turret?
                                        true,                  // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,             // The object type produced at this factory.
                                        DIR_N,                 // Starting idle frame to match construction.
                                        BSIZE_21,              // SIZE:			Building size.
                                        NULL,                  // Preferred exit cell list.
                                        (short const*)List21,  // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)OListSAM // OVERLAPLIST:List of overlap cell offset.
);

// clang-format off
static BuildingTypeClass const ClassMissileSilo(STRUCT_MSLO,
                                                TXT_MSLO,        // NAME:			Short name of the structure.
                                                "MSLO",          // NAME:			Short name of the structure.
                                                FACING_NONE,     // Foundation direction from center of building.
                                                XYP_COORD(0, 0), // Exit point for produced units.
                                                REMAP_ALTERNATE, // Sidebar remap logic.
                                                0x0000,          //	Vertical offset.
                                                0x0000,          // Primary weapon offset along turret centerline.
                                                0x0000,    // Primary weapon lateral offset along turret centerline.
                                                false,     // Is this building a fake (decoy?)
                                                true,      // Animation rate is regulated for constant speed?
                                                false,     // Always use the given name for the building?
                                                false,     // Is this a wall type structure?
                                                false,     // Simple (one frame) damage imagery?
                                                false,     // Is it invisible to radar?
                                                true,      // Can the player select this?
                                                true,      // Is this a legal target for attack or move?
                                                false,     // Is this an insignificant building?
                                                true,      // Theater specific graphic image?
                                                false,     // Does it have a rotating turret?
                                                true,      // Can the building be color remapped to indicate owner?
                                                RTTI_NONE, // The object type produced at this factory.
                                                DIR_N,     // Starting idle frame to match construction.
                                                BSIZE_21,  // SIZE:			Building size.
                                                NULL,      // Preferred exit cell list.
                                                (short const*)List21,  // OCCUPYLIST:	List of active foundation squares.
                                                (short const*)OListSAM // OVERLAPLIST:List of overlap cell offset.
);
// clang-format on

static BuildingTypeClass const ClassAirStrip(STRUCT_AIRSTRIP,
                                             TXT_AIRSTRIP,    // NAME:			Short name of the structure.
                                             "AFLD",          // NAME:			Short name of the structure.
                                             FACING_S,        // Foundation direction from center of building.
                                             XYP_COORD(0, 0), // Exit point for produced units.
                                             REMAP_ALTERNATE, // Sidebar remap logic.
                                             0x0000,          //	Vertical offset.
                                             0x0000,          // Primary weapon offset along turret centerline.
                                             0x0000,          // Primary weapon lateral offset along turret centerline.
                                             false,           // Is this building a fake (decoy?)
                                             true,            // Animation rate is regulated for constant speed?
                                             false,           // Always use the given name for the building?
                                             false,           // Is this a wall type structure?
                                             false,           // Simple (one frame) damage imagery?
                                             false,           // Is it invisible to radar?
                                             true,            // Can the player select this?
                                             true,            // Is this a legal target for attack or move?
                                             false,           // Is this an insignificant building?
                                             false,           // Theater specific graphic image?
                                             false,           // Does it have a rotating turret?
                                             true,            // Can the building be color remapped to indicate owner?
                                             RTTI_AIRCRAFTTYPE,    // The object type produced at this factory.
                                             DIR_N,                // Starting idle frame to match construction.
                                             BSIZE_32,             // SIZE:			Building size.
                                             NULL,                 // Preferred exit cell list.
                                             (short const*)List32, // OCCUPYLIST:	List of active foundation squares.
                                             (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
);

// GDI naval yard, Nod sub pen and GDI airfield: clones of RA's SYRD, SPEN and AFLD as types of their own,
// so each offers only its faction's roster. Art: TD-prefixed copies of RA's (scripts/bundle_ra_building.py).
// GDI Naval Yard (clone of ClassShipYard).
static BuildingTypeClass const ClassTdGYard(
    STRUCT_TDGYARD,
    TXT_SHIP_YARD, // placeholder name (rules.ini Name= overrides).
    "TDGYARD",     // IniName, also its art's tileset key.
    FACING_NONE,
    XYP_COORD(22 + (CELL_PIXEL_W / 2), ((CELL_PIXEL_H * 2) - (CELL_PIXEL_H / 2))),
    REMAP_ALTERNATE,
    0x0000, 0x0000, 0x0000,
    false, false, false, false, false, false,
    true, true, false, false, false, true,
    RTTI_VESSELTYPE,
    DIR_N, BSIZE_33,
    NULL,
    (short const*)ListSPen, (short const*)OListSPen);

// Nod Sub Pen (clone of ClassSubPen).
static BuildingTypeClass const ClassTdNPen(
    STRUCT_TDNPEN,
    TXT_SUB_PEN,
    "TDNPEN",
    FACING_NONE,
    XYP_COORD(22 + (CELL_PIXEL_W / 2), ((CELL_PIXEL_H * 2) - (CELL_PIXEL_H / 2))),
    REMAP_ALTERNATE,
    0x0000, 0x0000, 0x0000,
    false, false, false, false, false, false,
    true, true, false, false, false, true,
    RTTI_VESSELTYPE,
    DIR_N, BSIZE_33,
    (short const*)ExitSub,
    (short const*)ListSPen, (short const*)OListSPen);

// GDI Airfield (clone of ClassAirStrip).
static BuildingTypeClass const ClassTdGAfld(
    STRUCT_TDGAFLD,
    TXT_AIRSTRIP,
    "TDGAFLD",
    FACING_S,
    XYP_COORD(0, 0),
    REMAP_ALTERNATE,
    0x0000, 0x0000, 0x0000,
    false, true, false, false, false, false,
    true, true, false, false, false, true,
    RTTI_AIRCRAFTTYPE,
    DIR_N, BSIZE_32,
    NULL,
    (short const*)List32, (short const*)NULL);

// TS GDI Power Plant ([GAPOWR]): a clone of ClassPower with HD art only, so One_Time's _td_bdonors lends
// it POWR's classic dims and construction anim. Stats are TS's, in rules.ini.
static BuildingTypeClass const ClassTsPowr(STRUCT_TSPOWR,
                                           TXT_POWER,       // NAME: placeholder (rules.ini Name= overrides).
                                           "TSPOWR",        // NAME: IniName (launcher tileset key).
                                           FACING_S,        // Foundation direction from center of building.
                                           XYP_COORD(0, 0), // Exit point for produced units.
                                           REMAP_ALTERNATE, // Sidebar remap logic.
                                           0x0000,          // Vertical offset.
                                           0x0000,          // Primary weapon offset along turret centerline.
                                           0x0000,          // Primary weapon lateral offset along turret centerline.
                                           false,           // Is this building a fake (decoy?)
                                           true,            // Animation rate is regulated for constant speed?
                                           false,           // Always use the given name for the building?
                                           false,           // Is this a wall type structure?
                                           true,            // Simple (one frame) damage imagery?
                                           false,           // Is it invisible to radar?
                                           true,            // Can the player select this?
                                           true,            // Is this a legal target for attack or move?
                                           false,           // Is this an insignificant building?
                                           false,           // Theater specific graphic image?
                                           false,           // Does it have a rotating turret?
                                           true,            // Can the building be color remapped to indicate owner?
                                           RTTI_NONE,       // The object type produced at this factory.
                                           DIR_N,           // Starting idle frame to match construction.
                                           BSIZE_22,        // TS-authentic 2x2 box; only the south row is footprint:
                                                            // the north row is art headroom that units walk behind
                                                            // and buildings place on, and the bib below completes
                                                            // a 2x2 total plot (the radar height trick).
                                           NULL,            // Preferred exit cell list.
                                           (short const*)List22_0011, // OCCUPYLIST: south row only.
                                           (short const*)List22_1100  // OVERLAPLIST: north art row.
);

// TS EMP Pulse Cannon (STRUCT_TSPULS, TS rules [NAPULS]) -- docs/emp-cannon-design.md.
// 2x2 like the power plant, but squat (a rock mound with the cannon head on its
// dome), so it occupies the whole plot. No engine turret: the head's rotation is
// baked into the building tileset (shapes 0-60), Shape_Number picks the facing.
static BuildingTypeClass const ClassTsPuls(STRUCT_TSPULS,
                                           TXT_POWER,       // NAME: placeholder (rules.ini Name= overrides).
                                           "TSPULS",        // NAME: IniName (launcher tileset key).
                                           FACING_S,        // Foundation direction from center of building.
                                           XYP_COORD(0, 0), // Exit point for produced units.
                                           REMAP_ALTERNATE, // Sidebar remap logic.
                                           0x0000,          // Vertical offset.
                                           0x0000,          // Primary weapon offset along turret centerline.
                                           0x0000,          // Primary weapon lateral offset along turret centerline.
                                           false,           // Is this building a fake (decoy?)
                                           true,            // Animation rate is regulated for constant speed?
                                           false,           // Always use the given name for the building?
                                           false,           // Is this a wall type structure?
                                           true,            // Simple (one frame) damage imagery?
                                           false,           // Is it invisible to radar?
                                           true,            // Can the player select this?
                                           true,            // Is this a legal target for attack or move?
                                           false,           // Is this an insignificant building?
                                           false,           // Theater specific graphic image?
                                           false,           // Does it have a rotating turret? (baked into the shapes)
                                           true,            // Can the building be color remapped to indicate owner?
                                           RTTI_NONE,       // The object type produced at this factory.
                                           DIR_N,           // Starting idle frame to match construction.
                                           BSIZE_22,        // 2x2, whole plot occupied.
                                           NULL,            // Preferred exit cell list.
                                           (short const*)List22,     // OCCUPYLIST: all four cells.
                                           (short const*)List22_1100 // OVERLAPLIST: north art-spill row.
);

static BuildingTypeClass const ClassPower(STRUCT_POWER,
                                          TXT_POWER,       // NAME:			Short name of the structure.
                                          "POWR",          // NAME:			Short name of the structure.
                                          FACING_S,        // Foundation direction from center of building.
                                          XYP_COORD(0, 0), // Exit point for produced units.
                                          REMAP_ALTERNATE, // Sidebar remap logic.
                                          0x0000,          //	Vertical offset.
                                          0x0000,          // Primary weapon offset along turret centerline.
                                          0x0000,          // Primary weapon lateral offset along turret centerline.
                                          false,           // Is this building a fake (decoy?)
                                          true,            // Animation rate is regulated for constant speed?
                                          false,           // Always use the given name for the building?
                                          false,           // Is this a wall type structure?
                                          true,            // Simple (one frame) damage imagery?
                                          false,           // Is it invisible to radar?
                                          true,            // Can the player select this?
                                          true,            // Is this a legal target for attack or move?
                                          false,           // Is this an insignificant building?
                                          false,           // Theater specific graphic image?
                                          false,           // Does it have a rotating turret?
                                          true,            // Can the building be color remapped to indicate owner?
                                          RTTI_NONE,       // The object type produced at this factory.
                                          DIR_N,           // Starting idle frame to match construction.
                                          BSIZE_22,        // SIZE:			Building size.
                                          NULL,            // Preferred exit cell list.
                                          (short const*)List22,     // OCCUPYLIST:	List of active foundation squares.
                                          (short const*)List22_1100 // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const
    ClassAdvancedPower(STRUCT_ADVANCED_POWER,
                       TXT_ADVANCED_POWER,          // NAME:			Short name of the structure.
                       "APWR",                      // NAME:			Short name of the structure.
                       FACING_S,                    // Foundation direction from center of building.
                       XYP_COORD(0, 0),             // Exit point for produced units.
                       REMAP_ALTERNATE,             // Sidebar remap logic.
                       0x0000,                      //	Vertical offset.
                       0x0000,                      // Primary weapon offset along turret centerline.
                       0x0000,                      // Primary weapon lateral offset along turret centerline.
                       false,                       // Is this building a fake (decoy?)
                       true,                        // Animation rate is regulated for constant speed?
                       false,                       // Always use the given name for the building?
                       false,                       // Is this a wall type structure?
                       true,                        // Simple (one frame) damage imagery?
                       false,                       // Is it invisible to radar?
                       true,                        // Can the player select this?
                       true,                        // Is this a legal target for attack or move?
                       false,                       // Is this an insignificant building?
                       false,                       // Theater specific graphic image?
                       false,                       // Does it have a rotating turret?
                       true,                        // Can the building be color remapped to indicate owner?
                       RTTI_NONE,                   // The object type produced at this factory.
                       DIR_N,                       // Starting idle frame to match construction.
                       BSIZE_33,                    // SIZE:			Building size.
                       NULL,                        // Preferred exit cell list.
                       (short const*)List000111111, // OCCUPYLIST:	List of active foundation squares.
                       (short const*)OListTmpl      // OVERLAPLIST:List of overlap cell offset.
    );

static BuildingTypeClass const
    ClassSovietTech(STRUCT_SOVIET_TECH,
                    TXT_SOVIET_TECH,             // NAME:			Short name of the structure.
                    "STEK",                      // NAME:			Short name of the structure.
                    FACING_S,                    // Foundation direction from center of building.
                    XYP_COORD(0, 0),             // Exit point for produced units.
                    REMAP_ALTERNATE,             // Sidebar remap logic.
                    0x0000,                      //	Vertical offset.
                    0x0000,                      // Primary weapon offset along turret centerline.
                    0x0000,                      // Primary weapon lateral offset along turret centerline.
                    false,                       // Is this building a fake (decoy?)
                    true,                        // Animation rate is regulated for constant speed?
                    false,                       // Always use the given name for the building?
                    false,                       // Is this a wall type structure?
                    true,                        // Simple (one frame) damage imagery?
                    false,                       // Is it invisible to radar?
                    true,                        // Can the player select this?
                    true,                        // Is this a legal target for attack or move?
                    false,                       // Is this an insignificant building?
                    false,                       // Theater specific graphic image?
                    false,                       // Does it have a rotating turret?
                    true,                        // Can the building be color remapped to indicate owner?
                    RTTI_NONE,                   // The object type produced at this factory.
                    DIR_N,                       // Starting idle frame to match construction.
                    BSIZE_33,                    // SIZE:			Building size.
                    NULL,                        // Preferred exit cell list.
                    (short const*)List000111111, // OCCUPYLIST:	List of active foundation squares.
                    (short const*)OListTmpl      // OVERLAPLIST:List of overlap cell offset.
    );

static BuildingTypeClass const ClassHospital(STRUCT_HOSPITAL,
                                             TXT_HOSPITAL,    // NAME:			Short name of the structure.
                                             "HOSP",          // NAME:			Short name of the structure.
                                             FACING_NONE,     // Foundation direction from center of building.
                                             XYP_COORD(0, 0), // Exit point for produced units.
                                             REMAP_ALTERNATE, // Sidebar remap logic.
                                             0x0000,          //	Vertical offset.
                                             0x0000,          // Primary weapon offset along turret centerline.
                                             0x0000,          // Primary weapon lateral offset along turret centerline.
                                             false,           // Is this building a fake (decoy?)
                                             true,            // Animation rate is regulated for constant speed?
                                             false,           // Always use the given name for the building?
                                             false,           // Is this a wall type structure?
                                             false,           // Simple (one frame) damage imagery?
                                             false,           // Is it invisible to radar?
                                             true,            // Can the player select this?
                                             true,            // Is this a legal target for attack or move?
                                             false,           // Is this an insignificant building?
                                             false,           // Theater specific graphic image?
                                             false,           // Does it have a rotating turret?
                                             true,            // Can the building be color remapped to indicate owner?
                                             RTTI_NONE,       // The object type produced at this factory.
                                             DIR_N,           // Starting idle frame to match construction.
                                             BSIZE_22,        // SIZE:			Building size.
                                             NULL,            // Preferred exit cell list.
                                             (short const*)List2, // OCCUPYLIST:	List of active foundation squares.
                                             (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassBioLab(STRUCT_BIO_LAB,
                                           TXT_BIO_LAB,     // NAME:			Short name of the structure.
                                           "BIO",           // NAME:			Short name of the structure.
                                           FACING_NONE,     // Foundation direction from center of building.
                                           XYP_COORD(0, 0), // Exit point for produced units.
                                           REMAP_ALTERNATE, // Sidebar remap logic.
                                           0x0000,          //	Vertical offset.
                                           0x0000,          // Primary weapon offset along turret centerline.
                                           0x0000,          // Primary weapon lateral offset along turret centerline.
                                           false,           // Is this building a fake (decoy?)
                                           true,            // Animation rate is regulated for constant speed?
                                           true,            // Always use the given name for the building?
                                           false,           // Is this a wall type structure?
                                           false,           // Simple (one frame) damage imagery?
                                           false,           // Is it invisible to radar?
                                           true,            // Can the player select this?
                                           true,            // Is this a legal target for attack or move?
                                           false,           // Is this an insignificant building?
                                           false,           // Theater specific graphic image?
                                           false,           // Does it have a rotating turret?
                                           true,            // Can the building be color remapped to indicate owner?
                                           RTTI_NONE,       // The object type produced at this factory.
                                           DIR_N,           // Starting idle frame to match construction.
                                           BSIZE_22,        // SIZE:			Building size.
                                           NULL,            // Preferred exit cell list.
                                           (short const*)List2, // OCCUPYLIST:	List of active foundation squares.
                                           (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassBarracks(STRUCT_BARRACKS,
                                             TXT_BARRACKS, // NAME:			Short name of the structure.
                                             "BARR",       // NAME:			Short name of the structure.
                                             FACING_NONE,  // Foundation direction from center of building.
                                                           //	XYP_COORD(24,47),				// Exit point for produced units.
                                             XYP_COORD(18, 47), // Exit point for produced units.
                                             REMAP_ALTERNATE,   // Sidebar remap logic.
                                             0x0000,            //	Vertical offset.
                                             0x0000,            // Primary weapon offset along turret centerline.
                                             0x0000, // Primary weapon lateral offset along turret centerline.
                                             false,  // Is this building a fake (decoy?)
                                             true,   // Animation rate is regulated for constant speed?
                                             false,  // Always use the given name for the building?
                                             false,  // Is this a wall type structure?
                                             false,  // Simple (one frame) damage imagery?
                                             false,  // Is it invisible to radar?
                                             true,   // Can the player select this?
                                             true,   // Is this a legal target for attack or move?
                                             false,  // Is this an insignificant building?
                                             false,  // Theater specific graphic image?
                                             false,  // Does it have a rotating turret?
                                             true,   // Can the building be color remapped to indicate owner?
                                             RTTI_INFANTRYTYPE,      // The object type produced at this factory.
                                             DIR_N,                  // Starting idle frame to match construction.
                                             BSIZE_22,               // SIZE:			Building size.
                                             (short const*)ExitPyle, // Preferred exit cell list.
                                             (short const*)List22,   // OCCUPYLIST:	List of active foundation squares.
                                             NULL                    // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassTent(STRUCT_TENT,
                                         TXT_BARRACKS,      // NAME:			Short name of the structure.
                                         "TENT",            // NAME:			Short name of the structure.
                                         FACING_NONE,       // Foundation direction from center of building.
                                         XYP_COORD(24, 47), // Exit point for produced units.
                                         REMAP_ALTERNATE,   // Sidebar remap logic.
                                         0x0000,            //	Vertical offset.
                                         0x0000,            // Primary weapon offset along turret centerline.
                                         0x0000,            // Primary weapon lateral offset along turret centerline.
                                         false,             // Is this building a fake (decoy?)
                                         true,              // Animation rate is regulated for constant speed?
                                         false,             // Always use the given name for the building?
                                         false,             // Is this a wall type structure?
                                         false,             // Simple (one frame) damage imagery?
                                         false,             // Is it invisible to radar?
                                         true,              // Can the player select this?
                                         true,              // Is this a legal target for attack or move?
                                         false,             // Is this an insignificant building?
                                         false,             // Theater specific graphic image?
                                         false,             // Does it have a rotating turret?
                                         true,              // Can the building be color remapped to indicate owner?
                                         RTTI_INFANTRYTYPE, // The object type produced at this factory.
                                         DIR_N,             // Starting idle frame to match construction.
                                         BSIZE_22,          // SIZE:			Building size.
                                         (short const*)ExitPyle, // Preferred exit cell list.
                                         (short const*)List22,   // OCCUPYLIST:	List of active foundation squares.
                                         NULL                    // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassKennel(STRUCT_KENNEL,
                                           TXT_KENNEL,        // NAME:			Short name of the structure.
                                           "KENN",            // NAME:			Short name of the structure.
                                           FACING_NONE,       // Foundation direction from center of building.
                                           XYP_COORD(8, 16),  // Exit point for produced units.
                                           REMAP_ALTERNATE,   // Sidebar remap logic.
                                           0x0000,            //	Vertical offset.
                                           0x0000,            // Primary weapon offset along turret centerline.
                                           0x0000,            // Primary weapon lateral offset along turret centerline.
                                           false,             // Is this building a fake (decoy?)
                                           true,              // Animation rate is regulated for constant speed?
                                           false,             // Always use the given name for the building?
                                           false,             // Is this a wall type structure?
                                           false,             // Simple (one frame) damage imagery?
                                           false,             // Is it invisible to radar?
                                           true,              // Can the player select this?
                                           true,              // Is this a legal target for attack or move?
                                           false,             // Is this an insignificant building?
                                           false,             // Theater specific graphic image?
                                           false,             // Does it have a rotating turret?
                                           true,              // Can the building be color remapped to indicate owner?
                                           RTTI_INFANTRYTYPE, // The object type produced at this factory.
                                           DIR_N,             // Starting idle frame to match construction.
                                           BSIZE_11,          // SIZE:			Building size.
                                           NULL,              // Preferred exit cell list.
                                                              //	(short const *)ExitPyle,	// Preferred exit cell list.
                                           (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                           NULL                 // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassFakeShipYard(
    STRUCT_FAKE_YARD,
    TXT_FAKE_YARD, // NAME:			Short name of the structure.
    "SYRF",        // NAME:			Short name of the structure.
    FACING_NONE,   // Foundation direction from center of building.
    XYP_COORD(22 + (CELL_PIXEL_W / 2), ((CELL_PIXEL_H * 2) - (CELL_PIXEL_H / 2))), // Exit point for produced units.
    REMAP_ALTERNATE,                                                               // Sidebar remap logic.
    0x0000,                                                                        //	Vertical offset.
    0x0000,                 // Primary weapon offset along turret centerline.
    0x0000,                 // Primary weapon lateral offset along turret centerline.
    true,                   // Is this building a fake (decoy?)
    false,                  // Animation rate is regulated for constant speed?
    false,                  // Always use the given name for the building?
    false,                  // Is this a wall type structure?
    false,                  // Simple (one frame) damage imagery?
    false,                  // Is it invisible to radar?
    true,                   // Can the player select this?
    true,                   // Is this a legal target for attack or move?
    false,                  // Is this an insignificant building?
    false,                  // Theater specific graphic image?
    false,                  // Does it have a rotating turret?
    true,                   // Can the building be color remapped to indicate owner?
    RTTI_NONE,              // The object type produced at this factory.
    DIR_N,                  // Starting idle frame to match construction.
    BSIZE_33,               // SIZE:			Building size.
    (short const*)ExitWeap, // Preferred exit cell list.
    (short const*)ListSPen, // OCCUPYLIST:	List of active foundation squares.
    (short const*)OListSPen // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassFakeSubPen(
    STRUCT_FAKE_PEN,
    TXT_FAKE_PEN, // NAME:			Short name of the structure.
    "SPEF",       // NAME:			Short name of the structure.
    FACING_NONE,  // Foundation direction from center of building.
    XYP_COORD(22 + (CELL_PIXEL_W / 2), ((CELL_PIXEL_H * 2) - (CELL_PIXEL_H / 2))), // Exit point for produced units.
    REMAP_ALTERNATE,                                                               // Sidebar remap logic.
    0x0000,                                                                        //	Vertical offset.
    0x0000,                 // Primary weapon offset along turret centerline.
    0x0000,                 // Primary weapon lateral offset along turret centerline.
    true,                   // Is this building a fake (decoy?)
    false,                  // Animation rate is regulated for constant speed?
    false,                  // Always use the given name for the building?
    false,                  // Is this a wall type structure?
    false,                  // Simple (one frame) damage imagery?
    false,                  // Is it invisible to radar?
    true,                   // Can the player select this?
    true,                   // Is this a legal target for attack or move?
    false,                  // Is this an insignificant building?
    false,                  // Theater specific graphic image?
    false,                  // Does it have a rotating turret?
    true,                   // Can the building be color remapped to indicate owner?
    RTTI_NONE,              // The object type produced at this factory.
    DIR_N,                  // Starting idle frame to match construction.
    BSIZE_33,               // SIZE:			Building size.
    (short const*)ExitSub,  // Preferred exit cell list.
    (short const*)ListSPen, // OCCUPYLIST:	List of active foundation squares.
    (short const*)OListSPen // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const
    ClassFakeCommand(STRUCT_FAKE_RADAR,
                     TXT_FAKE_RADAR,        // NAME:			Short name of the structure.
                     "DOMF",                // NAME:			Short name of the structure.
                     FACING_NONE,           // Foundation direction from center of building.
                     XYP_COORD(0, 0),       // Exit point for produced units.
                     REMAP_ALTERNATE,       // Sidebar remap logic.
                     0x0000,                //	Vertical offset.
                     0x0000,                // Primary weapon offset along turret centerline.
                     0x0000,                // Primary weapon lateral offset along turret centerline.
                     true,                  // Is this building a fake (decoy?)
                     true,                  // Animation rate is regulated for constant speed?
                     false,                 // Always use the given name for the building?
                     false,                 // Is this a wall type structure?
                     false,                 // Simple (one frame) damage imagery?
                     false,                 // Is it invisible to radar?
                     true,                  // Can the player select this?
                     true,                  // Is this a legal target for attack or move?
                     false,                 // Is this an insignificant building?
                     false,                 // Theater specific graphic image?
                     false,                 // Does it have a rotating turret?
                     true,                  // Can the building be color remapped to indicate owner?
                     RTTI_NONE,             // The object type produced at this factory.
                     DIR_N,                 // Starting idle frame to match construction.
                     BSIZE_22,              // SIZE:			Building size.
                     NULL,                  // Preferred exit cell list.
                     (short const*)ComList, // OCCUPYLIST:	List of active foundation squares.
                     (short const*)OComList // OVERLAPLIST:List of overlap cell offset.
    );

static BuildingTypeClass const ClassRepair(STRUCT_REPAIR,
                                           TXT_FIX_IT,      // NAME:			Short name of the structure.
                                           "FIX",           // NAME:			Short name of the structure.
                                           FACING_NONE,     // Foundation direction from center of building.
                                           XYP_COORD(0, 0), // Exit point for produced units.
                                           REMAP_ALTERNATE, // Sidebar remap logic.
                                           0x0000,          //	Vertical offset.
                                           0x0000,          // Primary weapon offset along turret centerline.
                                           0x0000,          // Primary weapon lateral offset along turret centerline.
                                           false,           // Is this building a fake (decoy?)
                                           true,            // Animation rate is regulated for constant speed?
                                           false,           // Always use the given name for the building?
                                           false,           // Is this a wall type structure?
                                           false,           // Simple (one frame) damage imagery?
                                           false,           // Is it invisible to radar?
                                           true,            // Can the player select this?
                                           true,            // Is this a legal target for attack or move?
                                           false,           // Is this an insignificant building?
                                           false,           // Theater specific graphic image?
                                           false,           // Does it have a rotating turret?
                                           true,            // Can the building be color remapped to indicate owner?
                                           RTTI_NONE,       // The object type produced at this factory.
                                           DIR_N,           // Starting idle frame to match construction.
                                           BSIZE_33,        // SIZE:			Building size.
                                           NULL,            // Preferred exit cell list.
                                           (short const*)ListFix, // OCCUPYLIST:	List of active foundation squares.
                                           (short const*)OListFix // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV01(STRUCT_V01,
                                        TXT_CIV1,        // NAME:			Short name of the structure.
                                        "V01",           // NAME:			Short name of the structure.
                                        FACING_S,        // Foundation direction from center of building.
                                        XYP_COORD(0, 0), // Exit point for produced units.
                                        REMAP_ALTERNATE, // Sidebar remap logic.
                                        0x0000,          //	Vertical offset.
                                        0x0000,          // Primary weapon offset along turret centerline.
                                        0x0000,          // Primary weapon lateral offset along turret centerline.
                                        false,           // Is this building a fake (decoy?)
                                        true,            // Animation rate is regulated for constant speed?
                                        true,            // Always use the given name for the building?
                                        false,           // Is this a wall type structure?
                                        true,            // Simple (one frame) damage imagery?
                                        true,            // Is it invisible to radar?
                                        true,            // Can the player select this?
                                        true,            // Is this a legal target for attack or move?
                                        true,            // Is this an insignificant building?
                                        true,            // Theater specific graphic image?
                                        false,           // Does it have a rotating turret?
                                        false,           // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,       // The object type produced at this factory.
                                        DIR_N,           // Starting idle frame to match construction.
                                        BSIZE_22,        // SIZE: Building size.
                                        NULL,            // Preferred exit cell list.
                                        (short const*)List0011, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)List1100  // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV02(STRUCT_V02,
                                        TXT_CIV2,        // NAME:			Short name of the structure.
                                        "V02",           // NAME:			Short name of the structure.
                                        FACING_S,        // Foundation direction from center of building.
                                        XYP_COORD(0, 0), // Exit point for produced units.
                                        REMAP_ALTERNATE, // Sidebar remap logic.
                                        0x0000,          //	Vertical offset.
                                        0x0000,          // Primary weapon offset along turret centerline.
                                        0x0000,          // Primary weapon lateral offset along turret centerline.
                                        false,           // Is this building a fake (decoy?)
                                        true,            // Animation rate is regulated for constant speed?
                                        true,            // Always use the given name for the building?
                                        false,           // Is this a wall type structure?
                                        true,            // Simple (one frame) damage imagery?
                                        true,            // Is it invisible to radar?
                                        true,            // Can the player select this?
                                        true,            // Is this a legal target for attack or move?
                                        true,            // Is this an insignificant building?
                                        true,            // Theater specific graphic image?
                                        false,           // Does it have a rotating turret?
                                        false,           // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,       // The object type produced at this factory.
                                        DIR_N,           // Starting idle frame to match construction.
                                        BSIZE_22,        // SIZE:			Building size.
                                        NULL,            // Preferred exit cell list.
                                        (short const*)List0011, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)List1100  // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV03(STRUCT_V03,
                                        TXT_CIV3,        // NAME:			Short name of the structure.
                                        "V03",           // NAME:			Short name of the structure.
                                        FACING_S,        // Foundation direction from center of building.
                                        XYP_COORD(0, 0), // Exit point for produced units.
                                        REMAP_ALTERNATE, // Sidebar remap logic.
                                        0x0000,          //	Vertical offset.
                                        0x0000,          // Primary weapon offset along turret centerline.
                                        0x0000,          // Primary weapon lateral offset along turret centerline.
                                        false,           // Is this building a fake (decoy?)
                                        true,            // Animation rate is regulated for constant speed?
                                        true,            // Always use the given name for the building?
                                        false,           // Is this a wall type structure?
                                        true,            // Simple (one frame) damage imagery?
                                        true,            // Is it invisible to radar?
                                        true,            // Can the player select this?
                                        true,            // Is this a legal target for attack or move?
                                        true,            // Is this an insignificant building?
                                        true,            // Theater specific graphic image?
                                        false,           // Does it have a rotating turret?
                                        false,           // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,       // The object type produced at this factory.
                                        DIR_N,           // Starting idle frame to match construction.
                                        BSIZE_22,        // SIZE:			Building size.
                                        NULL,            // Preferred exit cell list.
                                        (short const*)List0111, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)List1000  // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV04(STRUCT_V04,
                                        TXT_CIV4,        // NAME:			Short name of the structure.
                                        "V04",           // NAME:			Short name of the structure.
                                        FACING_S,        // Foundation direction from center of building.
                                        XYP_COORD(0, 0), // Exit point for produced units.
                                        REMAP_ALTERNATE, // Sidebar remap logic.
                                        0x0000,          //	Vertical offset.
                                        0x0000,          // Primary weapon offset along turret centerline.
                                        0x0000,          // Primary weapon lateral offset along turret centerline.
                                        false,           // Is this building a fake (decoy?)
                                        true,            // Animation rate is regulated for constant speed?
                                        true,            // Always use the given name for the building?
                                        false,           // Is this a wall type structure?
                                        true,            // Simple (one frame) damage imagery?
                                        true,            // Is it invisible to radar?
                                        true,            // Can the player select this?
                                        true,            // Is this a legal target for attack or move?
                                        true,            // Is this an insignificant building?
                                        true,            // Theater specific graphic image?
                                        false,           // Does it have a rotating turret?
                                        false,           // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,       // The object type produced at this factory.
                                        DIR_N,           // Starting idle frame to match construction.
                                        BSIZE_22,        // SIZE:			Building size.
                                        NULL,            // Preferred exit cell list.
                                        (short const*)List0011, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)List1100  // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV05(STRUCT_V05,
                                        TXT_CIV5,             // NAME:			Short name of the structure.
                                        "V05",                // NAME:			Short name of the structure.
                                        FACING_NONE,          // Foundation direction from center of building.
                                        XYP_COORD(0, 0),      // Exit point for produced units.
                                        REMAP_ALTERNATE,      // Sidebar remap logic.
                                        0x0000,               //	Vertical offset.
                                        0x0000,               // Primary weapon offset along turret centerline.
                                        0x0000,               // Primary weapon lateral offset along turret centerline.
                                        false,                // Is this building a fake (decoy?)
                                        true,                 // Animation rate is regulated for constant speed?
                                        true,                 // Always use the given name for the building?
                                        false,                // Is this a wall type structure?
                                        true,                 // Simple (one frame) damage imagery?
                                        true,                 // Is it invisible to radar?
                                        true,                 // Can the player select this?
                                        true,                 // Is this a legal target for attack or move?
                                        true,                 // Is this an insignificant building?
                                        true,                 // Theater specific graphic image?
                                        false,                // Does it have a rotating turret?
                                        false,                // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,            // The object type produced at this factory.
                                        DIR_N,                // Starting idle frame to match construction.
                                        BSIZE_21,             // SIZE:			Building size.
                                        NULL,                 // Preferred exit cell list.
                                        (short const*)List11, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV06(STRUCT_V06,
                                        TXT_CIV6,             // NAME:			Short name of the structure.
                                        "V06",                // NAME:			Short name of the structure.
                                        FACING_NONE,          // Foundation direction from center of building.
                                        XYP_COORD(0, 0),      // Exit point for produced units.
                                        REMAP_ALTERNATE,      // Sidebar remap logic.
                                        0x0000,               //	Vertical offset.
                                        0x0000,               // Primary weapon offset along turret centerline.
                                        0x0000,               // Primary weapon lateral offset along turret centerline.
                                        false,                // Is this building a fake (decoy?)
                                        true,                 // Animation rate is regulated for constant speed?
                                        true,                 // Always use the given name for the building?
                                        false,                // Is this a wall type structure?
                                        true,                 // Simple (one frame) damage imagery?
                                        true,                 // Is it invisible to radar?
                                        true,                 // Can the player select this?
                                        true,                 // Is this a legal target for attack or move?
                                        true,                 // Is this an insignificant building?
                                        true,                 // Theater specific graphic image?
                                        false,                // Does it have a rotating turret?
                                        false,                // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,            // The object type produced at this factory.
                                        DIR_N,                // Starting idle frame to match construction.
                                        BSIZE_21,             // SIZE:			Building size.
                                        NULL,                 // Preferred exit cell list.
                                        (short const*)List11, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV07(STRUCT_V07,
                                        TXT_CIV7,             // NAME:			Short name of the structure.
                                        "V07",                // NAME:			Short name of the structure.
                                        FACING_NONE,          // Foundation direction from center of building.
                                        XYP_COORD(0, 0),      // Exit point for produced units.
                                        REMAP_ALTERNATE,      // Sidebar remap logic.
                                        0x0000,               //	Vertical offset.
                                        0x0000,               // Primary weapon offset along turret centerline.
                                        0x0000,               // Primary weapon lateral offset along turret centerline.
                                        false,                // Is this building a fake (decoy?)
                                        true,                 // Animation rate is regulated for constant speed?
                                        true,                 // Always use the given name for the building?
                                        false,                // Is this a wall type structure?
                                        true,                 // Simple (one frame) damage imagery?
                                        true,                 // Is it invisible to radar?
                                        true,                 // Can the player select this?
                                        true,                 // Is this a legal target for attack or move?
                                        true,                 // Is this an insignificant building?
                                        true,                 // Theater specific graphic image?
                                        false,                // Does it have a rotating turret?
                                        false,                // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,            // The object type produced at this factory.
                                        DIR_N,                // Starting idle frame to match construction.
                                        BSIZE_21,             // SIZE:			Building size.
                                        NULL,                 // Preferred exit cell list.
                                        (short const*)List11, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV08(STRUCT_V08,
                                        TXT_CIV8,            // NAME:			Short name of the structure.
                                        "V08",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        true,                // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV09(STRUCT_V09,
                                        TXT_CIV9,            // NAME:			Short name of the structure.
                                        "V09",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        true,                // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV10(STRUCT_V10,
                                        TXT_CIV10,           // NAME:			Short name of the structure.
                                        "V10",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        true,                // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV11(STRUCT_V11,
                                        TXT_CIV11,           // NAME:			Short name of the structure.
                                        "V11",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        true,                // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV12(STRUCT_V12,
                                        TXT_CIV12,           // NAME:			Short name of the structure.
                                        "V12",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        true,                // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV13(STRUCT_V13,
                                        TXT_CIV13,           // NAME:			Short name of the structure.
                                        "V13",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        true,                // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV14(STRUCT_V14,
                                        TXT_CIV14,           // NAME:			Short name of the structure.
                                        "V14",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        true,                // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV15(STRUCT_V15,
                                        TXT_CIV15,           // NAME:			Short name of the structure.
                                        "V15",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        true,                // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV16(STRUCT_V16,
                                        TXT_CIV16,           // NAME:			Short name of the structure.
                                        "V16",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        true,                // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV17(STRUCT_V17,
                                        TXT_CIV17,           // NAME:			Short name of the structure.
                                        "V17",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        true,                // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV18(STRUCT_V18,
                                        TXT_CIV18,           // NAME:			Short name of the structure.
                                        "V18",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        true,                // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV19(STRUCT_PUMP,
                                        TXT_PUMP,            // NAME:			Short name of the structure.
                                        "V19",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        false,               // Simple (one frame) damage imagery?
                                        false,               // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        false,               // Is this an insignificant building?
                                        false,               // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV20(STRUCT_V20,
                                        TXT_CIV20,       // NAME:			Short name of the structure.
                                        "V20",           // NAME:			Short name of the structure.
                                        FACING_S,        // Foundation direction from center of building.
                                        XYP_COORD(0, 0), // Exit point for produced units.
                                        REMAP_ALTERNATE, // Sidebar remap logic.
                                        0x0000,          //	Vertical offset.
                                        0x0000,          // Primary weapon offset along turret centerline.
                                        0x0000,          // Primary weapon lateral offset along turret centerline.
                                        false,           // Is this building a fake (decoy?)
                                        true,            // Animation rate is regulated for constant speed?
                                        true,            // Always use the given name for the building?
                                        false,           // Is this a wall type structure?
                                        false,           // Simple (one frame) damage imagery?
                                        false,           // Is it invisible to radar?
                                        true,            // Can the player select this?
                                        true,            // Is this a legal target for attack or move?
                                        false,           // Is this an insignificant building?
                                        true,            // Theater specific graphic image?
                                        false,           // Does it have a rotating turret?
                                        false,           // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,       // The object type produced at this factory.
                                        DIR_N,           // Starting idle frame to match construction.
                                        BSIZE_22,        // SIZE:			Building size.
                                        NULL,            // Preferred exit cell list.
                                        (short const*)List0011, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)List1100  // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV21(STRUCT_V21,
                                        TXT_CIV21,       // NAME:			Short name of the structure.
                                        "V21",           // NAME:			Short name of the structure.
                                        FACING_NONE,     // Foundation direction from center of building.
                                        XYP_COORD(0, 0), // Exit point for produced units.
                                        REMAP_ALTERNATE, // Sidebar remap logic.
                                        0x0000,          //	Vertical offset.
                                        0x0000,          // Primary weapon offset along turret centerline.
                                        0x0000,          // Primary weapon lateral offset along turret centerline.
                                        false,           // Is this building a fake (decoy?)
                                        true,            // Animation rate is regulated for constant speed?
                                        true,            // Always use the given name for the building?
                                        false,           // Is this a wall type structure?
                                        false,           // Simple (one frame) damage imagery?
                                        false,           // Is it invisible to radar?
                                        true,            // Can the player select this?
                                        true,            // Is this a legal target for attack or move?
                                        false,           // Is this an insignificant building?
                                        true,            // Theater specific graphic image?
                                        false,           // Does it have a rotating turret?
                                        false,           // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,       // The object type produced at this factory.
                                        DIR_N,           // Starting idle frame to match construction.
                                        BSIZE_22,        // SIZE:			Building size.
                                        NULL,            // Preferred exit cell list.
                                        (short const*)List1101, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)List0010  // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV22(STRUCT_V22,
                                        TXT_CIV22,            // NAME:			Short name of the structure.
                                        "V22",                // NAME:			Short name of the structure.
                                        FACING_NONE,          // Foundation direction from center of building.
                                        XYP_COORD(0, 0),      // Exit point for produced units.
                                        REMAP_ALTERNATE,      // Sidebar remap logic.
                                        0x0000,               //	Vertical offset.
                                        0x0000,               // Primary weapon offset along turret centerline.
                                        0x0000,               // Primary weapon lateral offset along turret centerline.
                                        false,                // Is this building a fake (decoy?)
                                        true,                 // Animation rate is regulated for constant speed?
                                        true,                 // Always use the given name for the building?
                                        false,                // Is this a wall type structure?
                                        false,                // Simple (one frame) damage imagery?
                                        false,                // Is it invisible to radar?
                                        true,                 // Can the player select this?
                                        true,                 // Is this a legal target for attack or move?
                                        false,                // Is this an insignificant building?
                                        true,                 // Theater specific graphic image?
                                        false,                // Does it have a rotating turret?
                                        false,                // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,            // The object type produced at this factory.
                                        DIR_N,                // Starting idle frame to match construction.
                                        BSIZE_21,             // SIZE:			Building size.
                                        NULL,                 // Preferred exit cell list.
                                        (short const*)List11, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV23(STRUCT_V23,
                                        TXT_CIV23,           // NAME:			Short name of the structure.
                                        "V23",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        false,               // Simple (one frame) damage imagery?
                                        false,               // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        false,               // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV24(STRUCT_V24,
                                        TXT_CIV24,       // NAME:			Short name of the structure.
                                        "V24",           // NAME:			Short name of the structure.
                                        FACING_S,        // Foundation direction from center of building.
                                        XYP_COORD(0, 0), // Exit point for produced units.
                                        REMAP_ALTERNATE, // Sidebar remap logic.
                                        0x0000,          //	Vertical offset.
                                        0x0000,          // Primary weapon offset along turret centerline.
                                        0x0000,          // Primary weapon lateral offset along turret centerline.
                                        false,           // Is this building a fake (decoy?)
                                        true,            // Animation rate is regulated for constant speed?
                                        true,            // Always use the given name for the building?
                                        false,           // Is this a wall type structure?
                                        true,            // Simple (one frame) damage imagery?
                                        false,           // Is it invisible to radar?
                                        true,            // Can the player select this?
                                        true,            // Is this a legal target for attack or move?
                                        false,           // Is this an insignificant building?
                                        true,            // Theater specific graphic image?
                                        false,           // Does it have a rotating turret?
                                        false,           // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,       // The object type produced at this factory.
                                        DIR_N,           // Starting idle frame to match construction.
                                        BSIZE_22,        // SIZE:			Building size.
                                        NULL,            // Preferred exit cell list.
                                        (short const*)List0011, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)List1100  // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV25(STRUCT_V25,
                                        TXT_CIV25,       // NAME:			Short name of the structure.
                                        "V25",           // NAME:			Short name of the structure.
                                        FACING_S,        // Foundation direction from center of building.
                                        XYP_COORD(0, 0), // Exit point for produced units.
                                        REMAP_ALTERNATE, // Sidebar remap logic.
                                        0x0000,          //	Vertical offset.
                                        0x0000,          // Primary weapon offset along turret centerline.
                                        0x0000,          // Primary weapon lateral offset along turret centerline.
                                        false,           // Is this building a fake (decoy?)
                                        true,            // Animation rate is regulated for constant speed?
                                        true,            // Always use the given name for the building?
                                        false,           // Is this a wall type structure?
                                        true,            // Simple (one frame) damage imagery?
                                        false,           // Is it invisible to radar?
                                        true,            // Can the player select this?
                                        true,            // Is this a legal target for attack or move?
                                        false,           // Is this an insignificant building?
                                        true,            // Theater specific graphic image?
                                        false,           // Does it have a rotating turret?
                                        false,           // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,       // The object type produced at this factory.
                                        DIR_N,           // Starting idle frame to match construction.
                                        BSIZE_22,        // SIZE:			Building size.
                                        NULL,            // Preferred exit cell list.
                                        (short const*)List0111, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)List1000  // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV26(STRUCT_V26,
                                        TXT_CIV26,            // NAME:			Short name of the structure.
                                        "V26",                // NAME:			Short name of the structure.
                                        FACING_NONE,          // Foundation direction from center of building.
                                        XYP_COORD(0, 0),      // Exit point for produced units.
                                        REMAP_ALTERNATE,      // Sidebar remap logic.
                                        0x0000,               //	Vertical offset.
                                        0x0000,               // Primary weapon offset along turret centerline.
                                        0x0000,               // Primary weapon lateral offset along turret centerline.
                                        false,                // Is this building a fake (decoy?)
                                        true,                 // Animation rate is regulated for constant speed?
                                        true,                 // Always use the given name for the building?
                                        false,                // Is this a wall type structure?
                                        true,                 // Simple (one frame) damage imagery?
                                        false,                // Is it invisible to radar?
                                        true,                 // Can the player select this?
                                        true,                 // Is this a legal target for attack or move?
                                        false,                // Is this an insignificant building?
                                        true,                 // Theater specific graphic image?
                                        false,                // Does it have a rotating turret?
                                        false,                // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,            // The object type produced at this factory.
                                        DIR_N,                // Starting idle frame to match construction.
                                        BSIZE_21,             // SIZE:			Building size.
                                        NULL,                 // Preferred exit cell list.
                                        (short const*)List11, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV27(STRUCT_V27,
                                        TXT_CIV27,           // NAME:			Short name of the structure.
                                        "V27",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        false,               // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        false,               // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV28(STRUCT_V28,
                                        TXT_CIV28,           // NAME:			Short name of the structure.
                                        "V28",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        false,               // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        false,               // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV29(STRUCT_V29,
                                        TXT_CIV29,           // NAME:			Short name of the structure.
                                        "V29",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        false,               // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        false,               // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV30(STRUCT_V30,
                                        TXT_CIV30,            // NAME:			Short name of the structure.
                                        "V30",                // NAME:			Short name of the structure.
                                        FACING_NONE,          // Foundation direction from center of building.
                                        XYP_COORD(0, 0),      // Exit point for produced units.
                                        REMAP_ALTERNATE,      // Sidebar remap logic.
                                        0x0000,               //	Vertical offset.
                                        0x0000,               // Primary weapon offset along turret centerline.
                                        0x0000,               // Primary weapon lateral offset along turret centerline.
                                        false,                // Is this building a fake (decoy?)
                                        true,                 // Animation rate is regulated for constant speed?
                                        true,                 // Always use the given name for the building?
                                        false,                // Is this a wall type structure?
                                        true,                 // Simple (one frame) damage imagery?
                                        false,                // Is it invisible to radar?
                                        true,                 // Can the player select this?
                                        true,                 // Is this a legal target for attack or move?
                                        false,                // Is this an insignificant building?
                                        true,                 // Theater specific graphic image?
                                        false,                // Does it have a rotating turret?
                                        false,                // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,            // The object type produced at this factory.
                                        DIR_N,                // Starting idle frame to match construction.
                                        BSIZE_21,             // SIZE:			Building size.
                                        NULL,                 // Preferred exit cell list.
                                        (short const*)List11, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV31(STRUCT_V31,
                                        TXT_CIV31,            // NAME:			Short name of the structure.
                                        "V31",                // NAME:			Short name of the structure.
                                        FACING_NONE,          // Foundation direction from center of building.
                                        XYP_COORD(0, 0),      // Exit point for produced units.
                                        REMAP_ALTERNATE,      // Sidebar remap logic.
                                        0x0000,               //	Vertical offset.
                                        0x0000,               // Primary weapon offset along turret centerline.
                                        0x0000,               // Primary weapon lateral offset along turret centerline.
                                        false,                // Is this building a fake (decoy?)
                                        true,                 // Animation rate is regulated for constant speed?
                                        true,                 // Always use the given name for the building?
                                        false,                // Is this a wall type structure?
                                        true,                 // Simple (one frame) damage imagery?
                                        false,                // Is it invisible to radar?
                                        true,                 // Can the player select this?
                                        true,                 // Is this a legal target for attack or move?
                                        false,                // Is this an insignificant building?
                                        true,                 // Theater specific graphic image?
                                        false,                // Does it have a rotating turret?
                                        false,                // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,            // The object type produced at this factory.
                                        DIR_N,                // Starting idle frame to match construction.
                                        BSIZE_21,             // SIZE:			Building size.
                                        NULL,                 // Preferred exit cell list.
                                        (short const*)List11, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV32(STRUCT_V32,
                                        TXT_CIV32,            // NAME:			Short name of the structure.
                                        "V32",                // NAME:			Short name of the structure.
                                        FACING_NONE,          // Foundation direction from center of building.
                                        XYP_COORD(0, 0),      // Exit point for produced units.
                                        REMAP_ALTERNATE,      // Sidebar remap logic.
                                        0x0000,               //	Vertical offset.
                                        0x0000,               // Primary weapon offset along turret centerline.
                                        0x0000,               // Primary weapon lateral offset along turret centerline.
                                        false,                // Is this building a fake (decoy?)
                                        true,                 // Animation rate is regulated for constant speed?
                                        true,                 // Always use the given name for the building?
                                        false,                // Is this a wall type structure?
                                        true,                 // Simple (one frame) damage imagery?
                                        false,                // Is it invisible to radar?
                                        true,                 // Can the player select this?
                                        true,                 // Is this a legal target for attack or move?
                                        false,                // Is this an insignificant building?
                                        true,                 // Theater specific graphic image?
                                        false,                // Does it have a rotating turret?
                                        false,                // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,            // The object type produced at this factory.
                                        DIR_N,                // Starting idle frame to match construction.
                                        BSIZE_21,             // SIZE:			Building size.
                                        NULL,                 // Preferred exit cell list.
                                        (short const*)List11, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV33(STRUCT_V33,
                                        TXT_CIV33,            // NAME:			Short name of the structure.
                                        "V33",                // NAME:			Short name of the structure.
                                        FACING_NONE,          // Foundation direction from center of building.
                                        XYP_COORD(0, 0),      // Exit point for produced units.
                                        REMAP_ALTERNATE,      // Sidebar remap logic.
                                        0x0000,               //	Vertical offset.
                                        0x0000,               // Primary weapon offset along turret centerline.
                                        0x0000,               // Primary weapon lateral offset along turret centerline.
                                        false,                // Is this building a fake (decoy?)
                                        true,                 // Animation rate is regulated for constant speed?
                                        true,                 // Always use the given name for the building?
                                        false,                // Is this a wall type structure?
                                        true,                 // Simple (one frame) damage imagery?
                                        false,                // Is it invisible to radar?
                                        true,                 // Can the player select this?
                                        true,                 // Is this a legal target for attack or move?
                                        false,                // Is this an insignificant building?
                                        true,                 // Theater specific graphic image?
                                        false,                // Does it have a rotating turret?
                                        false,                // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,            // The object type produced at this factory.
                                        DIR_N,                // Starting idle frame to match construction.
                                        BSIZE_21,             // SIZE:			Building size.
                                        NULL,                 // Preferred exit cell list.
                                        (short const*)List11, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV34(STRUCT_V34,
                                        TXT_CIV34,           // NAME:			Short name of the structure.
                                        "V34",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        false,               // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        false,               // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV35(STRUCT_V35,
                                        TXT_CIV35,           // NAME:			Short name of the structure.
                                        "V35",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        false,               // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        false,               // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

static BuildingTypeClass const ClassV36(STRUCT_V36,
                                        TXT_CIV36,           // NAME:			Short name of the structure.
                                        "V36",               // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_ALTERNATE,     // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        true,                // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        false,               // Is this a wall type structure?
                                        true,                // Simple (one frame) damage imagery?
                                        false,               // Is it invisible to radar?
                                        true,                // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        false,               // Is this an insignificant building?
                                        true,                // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);
static BuildingTypeClass const ClassV37(STRUCT_V37,
                                        TXT_CIV37,       // NAME:			Short name of the structure.
                                        "V37",           // NAME:			Short name of the structure.
                                        FACING_NONE,     // Foundation direction from center of building.
                                        XYP_COORD(0, 0), // Exit point for produced units.
                                        REMAP_ALTERNATE, // Sidebar remap logic.
                                        0x0000,          //	Vertical offset.
                                        0x0000,          // Primary weapon offset along turret centerline.
                                        0x0000,          // Primary weapon lateral offset along turret centerline.
                                        false,           // Is this building a fake (decoy?)
                                        true,            // Animation rate is regulated for constant speed?
                                        true,            // Always use the given name for the building?
                                        false,           // Is this a wall type structure?
                                        true,            // Simple (one frame) damage imagery?
                                        false,           // Is it invisible to radar?
                                        true,            // Can the player select this?
                                        true,            // Is this a legal target for attack or move?
                                        false,           // Is this an insignificant building?
                                        true,            // Theater specific graphic image?
                                        false,           // Does it have a rotating turret?
                                        false,           // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,       // The object type produced at this factory.
                                        DIR_N,           // Starting idle frame to match construction.
                                        BSIZE_42,        // SIZE:			Building size.
                                        NULL,            // Preferred exit cell list.
                                        (short const*)ListWestwood, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)OListWestwood // OVERLAPLIST:List of overlap cell offset.
);
static BuildingTypeClass const ClassMission(STRUCT_MISSION,
                                            TXT_CIVMISS,     // NAME:			Short name of the structure.
                                            "MISS",          // NAME:			Short name of the structure.
                                            FACING_NONE,     // Foundation direction from center of building.
                                            XYP_COORD(0, 0), // Exit point for produced units.
                                            REMAP_ALTERNATE, // Sidebar remap logic.
                                            0x0000,          //	Vertical offset.
                                            0x0000,          // Primary weapon offset along turret centerline.
                                            0x0000,          // Primary weapon lateral offset along turret centerline.
                                            false,           // Is this building a fake (decoy?)
                                            true,            // Animation rate is regulated for constant speed?
                                            true,            // Always use the given name for the building?
                                            false,           // Is this a wall type structure?
                                            true,            // Simple (one frame) damage imagery?
                                            false,           // Is it invisible to radar?
                                            true,            // Can the player select this?
                                            true,            // Is this a legal target for attack or move?
                                            false,           // Is this an insignificant building?
                                            false,           // Theater specific graphic image?
                                            false,           // Does it have a rotating turret?
                                            true,            // Can the building be color remapped to indicate owner?
                                            RTTI_NONE,       // The object type produced at this factory.
                                            DIR_N,           // Starting idle frame to match construction.
                                            BSIZE_32,        // SIZE:			Building size.
                                            NULL,            // Preferred exit cell list.
                                            (short const*)List32, // OCCUPYLIST:	List of active foundation squares.
                                            (short const*)NULL    // OVERLAPLIST:List of overlap cell offset.
);

// Sandbag wall
static BuildingTypeClass const Sandbag(STRUCT_SANDBAG_WALL,
                                       TXT_SANDBAG_WALL,    // NAME:			Short name of the structure.
                                       "SBAG",              // NAME:			Short name of the structure.
                                       FACING_NONE,         // Foundation direction from center of building.
                                       XYP_COORD(0, 0),     // Exit point for produced units.
                                       REMAP_NONE,          // Sidebar remap logic.
                                       0x0000,              //	Vertical offset.
                                       0x0000,              // Primary weapon offset along turret centerline.
                                       0x0000,              // Primary weapon lateral offset along turret centerline.
                                       false,               // Is this building a fake (decoy?)
                                       false,               // Animation rate is regulated for constant speed?
                                       true,                // Always use the given name for the building?
                                       true,                // Is this a wall type structure?
                                       false,               // Simple (one frame) damage imagery?
                                       false,               // Is it invisible to radar?
                                       false,               // Can the player select this?
                                       true,                // Is this a legal target for attack or move?
                                       true,                // Is this an insignificant building?
                                       false,               // Theater specific graphic image?
                                       false,               // Does it have a rotating turret?
                                       false,               // Can the building be color remapped to indicate owner?
                                       RTTI_NONE,           // The object type produced at this factory.
                                       DIR_N,               // Starting idle frame to match construction.
                                       BSIZE_11,            // SIZE:			Building size.
                                       NULL,                // Preferred exit cell list.
                                       (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                       (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);
// Cyclone fence
static BuildingTypeClass const Cyclone(STRUCT_CYCLONE_WALL,
                                       TXT_CYCLONE_WALL,    // NAME:			Short name of the structure.
                                       "CYCL",              // NAME:			Short name of the structure.
                                       FACING_NONE,         // Foundation direction from center of building.
                                       XYP_COORD(0, 0),     // Exit point for produced units.
                                       REMAP_NONE,          // Sidebar remap logic.
                                       0x0000,              //	Vertical offset.
                                       0x0000,              // Primary weapon offset along turret centerline.
                                       0x0000,              // Primary weapon lateral offset along turret centerline.
                                       false,               // Is this building a fake (decoy?)
                                       false,               // Animation rate is regulated for constant speed?
                                       true,                // Always use the given name for the building?
                                       true,                // Is this a wall type structure?
                                       false,               // Simple (one frame) damage imagery?
                                       false,               // Is it invisible to radar?
                                       false,               // Can the player select this?
                                       true,                // Is this a legal target for attack or move?
                                       true,                // Is this an insignificant building?
                                       false,               // Theater specific graphic image?
                                       false,               // Does it have a rotating turret?
                                       false,               // Can the building be color remapped to indicate owner?
                                       RTTI_NONE,           // The object type produced at this factory.
                                       DIR_N,               // Starting idle frame to match construction.
                                       BSIZE_11,            // SIZE:			Building size.
                                       NULL,                // Preferred exit cell list.
                                       (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                       (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);
// Brick wall
static BuildingTypeClass const Brick(STRUCT_BRICK_WALL,
                                     TXT_BRICK_WALL,      // NAME:			Short name of the structure.
                                     "BRIK",              // NAME:			Short name of the structure.
                                     FACING_NONE,         // Foundation direction from center of building.
                                     XYP_COORD(0, 0),     // Exit point for produced units.
                                     REMAP_NONE,          // Sidebar remap logic.
                                     0x0000,              //	Vertical offset.
                                     0x0000,              // Primary weapon offset along turret centerline.
                                     0x0000,              // Primary weapon lateral offset along turret centerline.
                                     false,               // Is this building a fake (decoy?)
                                     false,               // Animation rate is regulated for constant speed?
                                     true,                // Always use the given name for the building?
                                     true,                // Is this a wall type structure?
                                     false,               // Simple (one frame) damage imagery?
                                     false,               // Is it invisible to radar?
                                     false,               // Can the player select this?
                                     true,                // Is this a legal target for attack or move?
                                     true,                // Is this an insignificant building?
                                     false,               // Theater specific graphic image?
                                     false,               // Does it have a rotating turret?
                                     false,               // Can the building be color remapped to indicate owner?
                                     RTTI_NONE,           // The object type produced at this factory.
                                     DIR_N,               // Starting idle frame to match construction.
                                     BSIZE_11,            // SIZE:			Building size.
                                     NULL,                // Preferred exit cell list.
                                     (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                     (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);
// Barbwire wall
static BuildingTypeClass const Barbwire(STRUCT_BARBWIRE_WALL,
                                        TXT_BARBWIRE_WALL,   // NAME:			Short name of the structure.
                                        "BARB",              // NAME:			Short name of the structure.
                                        FACING_NONE,         // Foundation direction from center of building.
                                        XYP_COORD(0, 0),     // Exit point for produced units.
                                        REMAP_NONE,          // Sidebar remap logic.
                                        0x0000,              //	Vertical offset.
                                        0x0000,              // Primary weapon offset along turret centerline.
                                        0x0000,              // Primary weapon lateral offset along turret centerline.
                                        false,               // Is this building a fake (decoy?)
                                        false,               // Animation rate is regulated for constant speed?
                                        true,                // Always use the given name for the building?
                                        true,                // Is this a wall type structure?
                                        false,               // Simple (one frame) damage imagery?
                                        false,               // Is it invisible to radar?
                                        false,               // Can the player select this?
                                        true,                // Is this a legal target for attack or move?
                                        true,                // Is this an insignificant building?
                                        false,               // Theater specific graphic image?
                                        false,               // Does it have a rotating turret?
                                        false,               // Can the building be color remapped to indicate owner?
                                        RTTI_NONE,           // The object type produced at this factory.
                                        DIR_N,               // Starting idle frame to match construction.
                                        BSIZE_11,            // SIZE:			Building size.
                                        NULL,                // Preferred exit cell list.
                                        (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                        (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);
// Wood wall
static BuildingTypeClass const Wood(STRUCT_WOOD_WALL,
                                    TXT_WOOD_WALL,       // NAME:			Short name of the structure.
                                    "WOOD",              // NAME:			Short name of the structure.
                                    FACING_NONE,         // Foundation direction from center of building.
                                    XYP_COORD(0, 0),     // Exit point for produced units.
                                    REMAP_NONE,          // Sidebar remap logic.
                                    0x0000,              //	Vertical offset.
                                    0x0000,              // Primary weapon offset along turret centerline.
                                    0x0000,              // Primary weapon lateral offset along turret centerline.
                                    false,               // Is this building a fake (decoy?)
                                    false,               // Animation rate is regulated for constant speed?
                                    true,                // Always use the given name for the building?
                                    true,                // Is this a wall type structure?
                                    false,               // Simple (one frame) damage imagery?
                                    false,               // Is it invisible to radar?
                                    false,               // Can the player select this?
                                    true,                // Is this a legal target for attack or move?
                                    true,                // Is this an insignificant building?
                                    false,               // Theater specific graphic image?
                                    false,               // Does it have a rotating turret?
                                    false,               // Can the building be color remapped to indicate owner?
                                    RTTI_NONE,           // The object type produced at this factory.
                                    DIR_N,               // Starting idle frame to match construction.
                                    BSIZE_11,            // SIZE:			Building size.
                                    NULL,                // Preferred exit cell list.
                                    (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                    (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);
static BuildingTypeClass const Fence(STRUCT_FENCE,
                                     TXT_FENCE,           // NAME:			Short name of the structure.
                                     "FENC",              // NAME:			Short name of the structure.
                                     FACING_NONE,         // Foundation direction from center of building.
                                     XYP_COORD(0, 0),     // Exit point for produced units.
                                     REMAP_NONE,          // Sidebar remap logic.
                                     0x0000,              //	Vertical offset.
                                     0x0000,              // Primary weapon offset along turret centerline.
                                     0x0000,              // Primary weapon lateral offset along turret centerline.
                                     false,               // Is this building a fake (decoy?)
                                     false,               // Animation rate is regulated for constant speed?
                                     true,                // Always use the given name for the building?
                                     true,                // Is this a wall type structure?
                                     false,               // Simple (one frame) damage imagery?
                                     false,               // Is it invisible to radar?
                                     false,               // Can the player select this?
                                     true,                // Is this a legal target for attack or move?
                                     true,                // Is this an insignificant building?
                                     false,               // Theater specific graphic image?
                                     false,               // Does it have a rotating turret?
                                     false,               // Can the building be color remapped to indicate owner?
                                     RTTI_NONE,           // The object type produced at this factory.
                                     DIR_N,               // Starting idle frame to match construction.
                                     BSIZE_11,            // SIZE:			Building size.
                                     NULL,                // Preferred exit cell list.
                                     (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                     (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);

#ifdef FIXIT_ANTS
static BuildingTypeClass const ClassQueen(STRUCT_QUEEN,
                                          TXT_NONE,          // NAME:			Short name of the structure.
                                          "QUEE",            // NAME:			Short name of the structure.
                                          FACING_NONE,       // Foundation direction from center of building.
                                          XYP_COORD(24, 47), // Exit point for produced units.
                                          REMAP_ALTERNATE,   // Sidebar remap logic.
                                          0x0000,            //	Vertical offset.
                                          0x0000,            // Primary weapon offset along turret centerline.
                                          0x0000,            // Primary weapon lateral offset along turret centerline.
                                          false,             // Is this building a fake (decoy?)
                                          true,              // Animation rate is regulated for constant speed?
                                          true,              // Always use the given name for the building?
                                          false,             // Is this a wall type structure?
                                          false,             // Simple (one frame) damage imagery?
                                          false,             // Is it invisible to radar?
                                          true,              // Can the player select this?
                                          true,              // Is this a legal target for attack or move?
                                          false,             // Is this an insignificant building?
                                          false,             // Theater specific graphic image?
                                          false,             // Does it have a rotating turret?
                                          true,              // Can the building be color remapped to indicate owner?
                                          RTTI_NONE,         // The object type produced at this factory.
                                          DIR_N,             // Starting idle frame to match construction.
                                          BSIZE_21,          // SIZE:			Building size.
                                          NULL,              // Preferred exit cell list.
                                          (short const*)List11, // OCCUPYLIST:	List of active foundation squares.
                                          NULL                  // OVERLAPLIST:List of overlap cell offset.
);
static BuildingTypeClass const ClassLarva1(STRUCT_LARVA1,
                                           TXT_NONE,        // NAME:			Short name of the structure.
                                           "LAR1",          // NAME:			Short name of the structure.
                                           FACING_NONE,     // Foundation direction from center of building.
                                           XYP_COORD(0, 0), // Exit point for produced units.
                                           REMAP_ALTERNATE, // Sidebar remap logic.
                                           0x0000,          //	Vertical offset.
                                           0x0000,          // Primary weapon offset along turret centerline.
                                           0x0000,          // Primary weapon lateral offset along turret centerline.
                                           false,           // Is this building a fake (decoy?)
                                           false,           // Animation rate is regulated for constant speed?
                                           true,            // Always use the given name for the building?
                                           false,           // Is this a wall type structure?
                                           true,            // Simple (one frame) damage imagery?
                                           true,            // Is it invisible to radar?
                                           true,            // Can the player select this?
                                           true,            // Is this a legal target for attack or move?
                                           true,            // Is this an insignificant building?
                                           false,           // Theater specific graphic image?
                                           false,           // Does it have a rotating turret?
                                           false,           // Can the building be color remapped to indicate owner?
                                           RTTI_NONE,       // The object type produced at this factory.
                                           DIR_N,           // Starting idle frame to match construction.
                                           BSIZE_11,        // SIZE:			Building size.
                                           NULL,            // Preferred exit cell list.
                                           (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                           (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);
static BuildingTypeClass const ClassLarva2(STRUCT_LARVA2,
                                           TXT_NONE,        // NAME:			Short name of the structure.
                                           "LAR2",          // NAME:			Short name of the structure.
                                           FACING_NONE,     // Foundation direction from center of building.
                                           XYP_COORD(0, 0), // Exit point for produced units.
                                           REMAP_ALTERNATE, // Sidebar remap logic.
                                           0x0000,          //	Vertical offset.
                                           0x0000,          // Primary weapon offset along turret centerline.
                                           0x0000,          // Primary weapon lateral offset along turret centerline.
                                           false,           // Is this building a fake (decoy?)
                                           false,           // Animation rate is regulated for constant speed?
                                           true,            // Always use the given name for the building?
                                           false,           // Is this a wall type structure?
                                           true,            // Simple (one frame) damage imagery?
                                           true,            // Is it invisible to radar?
                                           true,            // Can the player select this?
                                           true,            // Is this a legal target for attack or move?
                                           true,            // Is this an insignificant building?
                                           false,           // Theater specific graphic image?
                                           false,           // Does it have a rotating turret?
                                           false,           // Can the building be color remapped to indicate owner?
                                           RTTI_NONE,       // The object type produced at this factory.
                                           DIR_N,           // Starting idle frame to match construction.
                                           BSIZE_11,        // SIZE:			Building size.
                                           NULL,            // Preferred exit cell list.
                                           (short const*)List1, // OCCUPYLIST:	List of active foundation squares.
                                           (short const*)NULL   // OVERLAPLIST:List of overlap cell offset.
);
#endif
void const* BuildingTypeClass::WarFactoryOverlay;
void const* BuildingTypeClass::WarFactoryOverlayTd;
void const* BuildingTypeClass::WarFactoryOverlayTs;
void const* BuildingTypeClass::TsWeapShutter;
void const* BuildingTypeClass::TsWeapUnderDoor;
void const* BuildingTypeClass::TsWeapFront;
void const* BuildingTypeClass::TsWeapFrontOpen;
void const* BuildingTypeClass::TsDweapShutter;
void const* BuildingTypeClass::TsDweapUnderDoor;
void const* BuildingTypeClass::TsDweapFront;
void const* BuildingTypeClass::TsDweapFrontOpen;
void const* BuildingTypeClass::TsRefineryFlame;
void const* BuildingTypeClass::TsPulseTurret;
void const* BuildingTypeClass::TsRefineryLid;
void const* BuildingTypeClass::TsRefineryFront;
void const* LightningShapes;

/***********************************************************************************************
 * BuildingTypeClass::BuildingTypeClass -- This is the constructor for the building types.     *
 *                                                                                             *
 *    This is the constructor used to create the building types.                               *
 *                                                                                             *
 * INPUT:   see below...                                                                       *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
BuildingTypeClass::BuildingTypeClass(StructType type,
                                     int name,
                                     char const* ininame,
                                     FacingType foundation,
                                     COORDINATE exitpoint,
                                     RemapType remap,
                                     int verticaloffset,
                                     int primaryoffset,
                                     int primarylateral,
                                     bool is_fake,
                                     bool is_regulated,
                                     bool is_nominal,
                                     bool is_wall,
                                     bool is_simpledamage,
                                     bool is_stealthy,
                                     bool is_selectable,
                                     bool is_legal_target,
                                     bool is_insignificant,
                                     bool is_theater,
                                     bool is_turret_equipped,
                                     bool is_remappable,
                                     RTTIType tobuild,
                                     DirType sframe,
                                     BSizeType size,
                                     short const* exitlist,
                                     short const* sizelist,
                                     short const* overlap)
    : TechnoTypeClass(RTTI_BUILDINGTYPE,
                      int(type),
                      name,
                      ininame,
                      remap,
                      verticaloffset,
                      primaryoffset,
                      primarylateral,
                      primaryoffset,
                      primarylateral,
                      is_nominal,
                      is_stealthy,
                      is_selectable,
                      is_legal_target,
                      is_insignificant,
                      false,
                      is_theater,
                      is_turret_equipped,
                      is_remappable,
                      true,
                      (is_turret_equipped ? 32 : 1),
                      SPEED_NONE)
    , IsBase(true)
    , IsFake(is_fake)
    , IsBibbed(false)
    , IsWall(is_wall)
    , IsSimpleDamage(is_simpledamage)
    , IsCaptureable(false)
    , IsRegulated(is_regulated)
    , IsPowered(false)
    , IsUnsellable(false)
    , FoundationFace(foundation)
    , Adjacent(1)
    , ToBuild(tobuild)
    , ExitCoordinate(exitpoint)
    , ExitList(exitlist)
    , Type(type)
    , StartFace(sframe)
    , Capacity(0)
    , Power(0)
    , Drain(0)
    , PowersUpBuilding(STRUCT_NONE)
    , UpgradesMax(0)
    , Size(size)
    , ShapeWidth(0)
    , ShapeHeight(0)
    , OccupyList(sizelist)
    , OverlapList(overlap)
    , BuildupData(0)
{

    Anims[BSTATE_CONSTRUCTION].Start = 0;
    Anims[BSTATE_CONSTRUCTION].Count = 1;
    Anims[BSTATE_CONSTRUCTION].Rate = 0;

    Anims[BSTATE_IDLE].Start = 0;
    Anims[BSTATE_IDLE].Count = 1;
    Anims[BSTATE_IDLE].Rate = 0;

    Anims[BSTATE_ACTIVE].Start = 0;
    Anims[BSTATE_ACTIVE].Count = 1;
    Anims[BSTATE_ACTIVE].Rate = 0;

    Anims[BSTATE_AUX1].Start = 0;
    Anims[BSTATE_AUX1].Count = 1;
    Anims[BSTATE_AUX1].Rate = 0;

    Anims[BSTATE_AUX2].Start = 0;
    Anims[BSTATE_AUX2].Count = 1;
    Anims[BSTATE_AUX2].Rate = 0;
}

/***********************************************************************************************
 * BuildingTypeClass::operator new -- Allocates a building type object from the special heap.  *
 *                                                                                             *
 *    This routine will allocate a building type object from the special heap used just for    *
 *    allocation of object of this type.                                                       *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the newly allocated object. If the allocation could not  *
 *          succeed, then NULL will be returned.                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/06/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void* BuildingTypeClass::operator new(size_t) noexcept
{
    return (BuildingTypes.Alloc());
}

/***********************************************************************************************
 * BuildingTypeClass::operator delete -- Deletes a building type object from the special heap. *
 *                                                                                             *
 *    This will delete a previously allocated building type object. The memory is returned     *
 *    to the special heap that is used for that purpose.                                       *
 *                                                                                             *
 * INPUT:   ptr   -- Pointer to the building type object to return to the special heap.        *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/06/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingTypeClass::operator delete(void* ptr)
{
    BuildingTypes.Free((BuildingTypeClass*)ptr);
}

// Registers a mod-defined building type from [NewBuildings] by IniName; Read_INI fills in the rest. Its ID
// must be the heap slot it lands in: CCPtr resolves by ID, so a vanilla StructType would alias that type.
BuildingTypeClass::BuildingTypeClass(int /*btype*/, char const* ininame)
    : BuildingTypeClass(static_cast<StructType>(BuildingTypes.Count() - 1),
                        TXT_NONE,
                        ininame,
                        FACING_NONE,
                        XYP_COORD(0, 0),
                        REMAP_NORMAL,
                        0x0000,
                        0x0000,
                        0x0000,
                        false,
                        false,
                        false,
                        false,
                        true,
                        false,
                        true,
                        true,
                        false,
                        false,
                        false,
                        true,
                        RTTI_NONE,
                        DIR_N,
                        BSIZE_11,
                        NULL,
                        NULL,
                        NULL)
{
}

// Finds a building type by IniName across the whole heap, including mod-defined types past STRUCT_COUNT,
// which From_Name does not search.
BuildingTypeClass* BuildingTypeClass::As_Pointer(char const* name)
{
    if (name == NULL)
        return (NULL);
    for (int index = 0; index < BuildingTypes.Count(); index++) {
        BuildingTypeClass* btc = BuildingTypes.Ptr(index);
        if (btc != NULL && stricmp(btc->IniName, name) == 0) {
            return (btc);
        }
    }
    return (NULL);
}

/***********************************************************************************************
 * BuildingTypeClass::Init_Heap -- Initialize the heap as necessary for the building type obje *
 *                                                                                             *
 *    This routine performs the necessary heap initializations. Since we know exactly what     *
 *    building type objects will be needed, they are pre-allocated at this time.               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Call this routine only once.                                                    *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/06/1996 JLB : Created.                                                                 *
 *=============================================================================================*/

// TD blossom tree as a 1x1 building, since terrain objects can't take custom HD art. It seeds Tiberium
// round it (BuildingClass::AI); rules.ini [TDBLOSSOM] makes it neutral, unsellable scenery.
static BuildingTypeClass const ClassTdBlossom(STRUCT_TDBLOSSOM,
                                              TXT_NONE,
                                              "TDBLOSSOM",
                                              FACING_NONE,
                                              XYP_COORD(0, 0),
                                              REMAP_NORMAL,
                                              0x0000, // Vertical offset.
                                              0x0000, // Primary weapon offset (none).
                                              0x0000, // Primary weapon lateral (none).
                                              false,  // Is fake?
                                              false,  // Is regulated (power)?
                                              false,  // Is nominal?
                                              false,  // Is a wall?
                                              false,  // Is simple damage?
                                              false,  // Is stealthy?
                                              false,  // Is selectable? NO -- harmless scenery.
                                              false,  // Is a legal target? NO -- can't be attacked.
                                              true,   // Is insignificant? YES -- no "lost"/announce.
                                              false,  // Is theater-specific art?
                                              false,  // Is turret equipped?
                                              false,  // Is remappable (house colour)? NO -- neutral scenery.
                                              RTTI_NONE,
                                              DIR_N,
                                              BSIZE_11, // 1x1 footprint.
                                              NULL,
                                              (short const*)List1,
                                              (short const*)NULL
);

// True for every construction yard an MCV deploys into; the fake yard is not one (see type.h).
bool BuildingTypeClass::Is_Construction_Yard(void) const
{
    return (Type == STRUCT_CONST || Type == STRUCT_AFACT || Type == STRUCT_SFACT || Type == STRUCT_TDFACT
            || Type == STRUCT_TDGFACT || Type == STRUCT_TDNFACT || Type == STRUCT_TSFACT);
}

// True for every helicopter pad: the shared, faction and TS pads. Fixed-wing factories are not pads.
bool BuildingTypeClass::Is_Helipad(void) const
{
    return (Type == STRUCT_HELIPAD || Type == STRUCT_TDHPAD || Type == STRUCT_AHPAD || Type == STRUCT_SHPAD
            || Type == STRUCT_TDGHPAD || Type == STRUCT_TDNHPAD || Type == STRUCT_TSHPAD);
}

// True for TD and TS buildings, and for TD and TS gates. Tested on enum runs bounded by markers, never by
// IniName (see STRUCT_TIBERIAN_LAST in defines.h).
bool BuildingTypeClass::Is_Tiberian_Era(void) const
{
    TFGateInfo const* gate = TF_Gate_Info(Type);
    if (gate != NULL) {
        return (gate->Era != 'R');
    }
    return (Type >= STRUCT_TDOBLI && Type <= STRUCT_TIBERIAN_LAST)
           || (Type >= STRUCT_TS_TREE_FIRST && Type <= STRUCT_TS_TREE_LAST);
}

// True for the TS buildings, gates included. Their placement sounds differ: a PLACE2 slam, then a silent rise
// (OpenTS). Keyed on the building, so a TS yard sounds like one whoever holds it.
bool BuildingTypeClass::Is_TS_Era(void) const
{
    TFGateInfo const* gate = TF_Gate_Info(Type);
    if (gate != NULL) {
        return (gate->Era == 'S');
    }
    return (Type == STRUCT_TSPOWR)
           || (Type >= STRUCT_TS_TREE_FIRST && Type <= STRUCT_TS_TREE_LAST);
}

// The house scan-mask bit a building type sets. Types past bit 31 set their vanilla equivalent's bit, or
// none; prerequisites count those through ActiveBQuantity (Has_Building_Active).
long TF_Building_Scan_Bit(int btype)
{
    if (btype >= 0 && btype < 32) {
        return (1L << btype);
    }

    switch (btype) {
    case STRUCT_TDHQ:
    case STRUCT_TDEYE:
    case STRUCT_TSRADR:
    case STRUCT_TSTECH:
        return (STRUCTF_RADAR);

    case STRUCT_TDFACT:
    case STRUCT_TDNFACT:
    case STRUCT_TDGFACT:
    case STRUCT_SFACT:
    case STRUCT_AFACT:
    case STRUCT_TSFACT:
        return (STRUCTF_CONST);

    case STRUCT_TDPROC:
    case STRUCT_TSPROC:
        return (STRUCTF_REFINERY);

    case STRUCT_TDWEAP:
    case STRUCT_AWEAP:
    case STRUCT_SWEAP:
    case STRUCT_TSWEAP:
    case STRUCT_TSDWEAP:
        return (STRUCTF_WEAP);

    case STRUCT_TDAFLD:
    case STRUCT_TDGAFLD:
        return (STRUCTF_AIRSTRIP);

    case STRUCT_TDHPAD:
    case STRUCT_TDGHPAD:
    case STRUCT_TDNHPAD:
    case STRUCT_AHPAD:
    case STRUCT_SHPAD:
    case STRUCT_TSHPAD:
        return (STRUCTF_HELIPAD);

    case STRUCT_TDFIX:
    case STRUCT_TSDEPT:
        return (STRUCTF_REPAIR);

    case STRUCT_TDPYLE:
    case STRUCT_TDHAND:
    case STRUCT_TSPILE:
        return (STRUCTF_BARRACKS);

    default:
        return (0);
    }
}

void BuildingTypeClass::Init_Heap(void)
{
    /*
    **	These building type class objects must be allocated in the exact order that they
    **	are specified in the StructType enumeration. This is necessary because the heap
    **	allocation block index serves double duty as the type number index.
    */
    new BuildingTypeClass(ClassAdvancedTech);  // STRUCT_ADVANCED_TECH
    new BuildingTypeClass(ClassIronCurtain);   // STRUCT_IRON_CURTAIN
    new BuildingTypeClass(ClassWeapon);        //	STRUCT_WEAP
    new BuildingTypeClass(ClassChronosphere);  // STRUCT_CHRONOSPHERE
    new BuildingTypeClass(ClassPillbox);       //	STRUCT_PILLBOX
    new BuildingTypeClass(ClassCamoPillbox);   //	STRUCT_CAMOPILLBOX
    new BuildingTypeClass(ClassCommand);       //	STRUCT_RADAR
    new BuildingTypeClass(ClassGapGenerator);  // STRUCT_GAP
    new BuildingTypeClass(ClassTurret);        //	STRUCT_TURRET
    new BuildingTypeClass(ClassAAGun);         // STRUCT_AAGUN
    new BuildingTypeClass(ClassFlameTurret);   //	STRUCT_FLAME_TURRET
    new BuildingTypeClass(ClassConst);         //	STRUCT_CONST
    new BuildingTypeClass(ClassRefinery);      //	STRUCT_REFINERY
    new BuildingTypeClass(ClassStorage);       //	STRUCT_STORAGE
    new BuildingTypeClass(ClassHelipad);       //	STRUCT_HELIPAD
    new BuildingTypeClass(ClassSAM);           //	STRUCT_SAM
    new BuildingTypeClass(ClassAirStrip);      //	STRUCT_AIRSTRIP
    new BuildingTypeClass(ClassPower);         //	STRUCT_POWER
    new BuildingTypeClass(ClassAdvancedPower); //	STRUCT_ADVANCED_POWER
    new BuildingTypeClass(ClassSovietTech);    // STRUCT_SOVIET_TECH
    new BuildingTypeClass(ClassHospital);      //	STRUCT_HOSPITAL
    new BuildingTypeClass(ClassBarracks);      //	STRUCT_BARRACKS
    new BuildingTypeClass(ClassTent);          //	STRUCT_TENT
    new BuildingTypeClass(ClassKennel);        // STRUCT_KENNEL
    new BuildingTypeClass(ClassRepair);        //	STRUCT_REPAIR
    new BuildingTypeClass(ClassBioLab);        //	STRUCT_BIO_LAB
    new BuildingTypeClass(ClassMission);       //	STRUCT_MISSION
    new BuildingTypeClass(ClassShipYard);      //	STRUCT_SHIP_YARD
    new BuildingTypeClass(ClassSubPen);        //	STRUCT_SUB_PEN
    new BuildingTypeClass(ClassMissileSilo);   // STRUCT_MSLO
    new BuildingTypeClass(ClassForwardCom);    // STRUCT_FORWARD_COM
    new BuildingTypeClass(ClassTesla);         //	STRUCT_TESLA
    new BuildingTypeClass(ClassFakeWeapon);    // STRUCT_FAKEWEAP
    new BuildingTypeClass(ClassFakeConst);     // STRUCT_FAKECONST
    new BuildingTypeClass(ClassFakeShipYard);  // STRUCT_FAKE_YARD
    new BuildingTypeClass(ClassFakeSubPen);    // STRUCT_FAKE_PEN
    new BuildingTypeClass(ClassFakeCommand);   // STRUCT_FAKE_RADAR
    new BuildingTypeClass(Sandbag);            // STRUCT_SANDBAG_WALL
    new BuildingTypeClass(Cyclone);            //	STRUCT_CYCLONE_WALL
    new BuildingTypeClass(Brick);              // STRUCT_BRICK_WALL
    new BuildingTypeClass(Barbwire);           // STRUCT_BARBWIRE_WALL
    new BuildingTypeClass(Wood);               //	STRUCT_WOOD_WALL
    new BuildingTypeClass(Fence);              // STRUCT_FENCE
    new BuildingTypeClass(ClassAVMine);        // STRUCT_AVMINE
    new BuildingTypeClass(ClassAPMine);        // STRUCT_APMINE
    new BuildingTypeClass(ClassV01);           //	STRUCT_V1
    new BuildingTypeClass(ClassV02);           //	STRUCT_V2
    new BuildingTypeClass(ClassV03);           //	STRUCT_V3
    new BuildingTypeClass(ClassV04);           //	STRUCT_V4
    new BuildingTypeClass(ClassV05);           //	STRUCT_V5
    new BuildingTypeClass(ClassV06);           //	STRUCT_V6
    new BuildingTypeClass(ClassV07);           //	STRUCT_V7
    new BuildingTypeClass(ClassV08);           //	STRUCT_V8
    new BuildingTypeClass(ClassV09);           //	STRUCT_V9
    new BuildingTypeClass(ClassV10);           //	STRUCT_V10
    new BuildingTypeClass(ClassV11);           //	STRUCT_V11
    new BuildingTypeClass(ClassV12);           //	STRUCT_V12
    new BuildingTypeClass(ClassV13);           //	STRUCT_V13
    new BuildingTypeClass(ClassV14);           //	STRUCT_V14
    new BuildingTypeClass(ClassV15);           //	STRUCT_V15
    new BuildingTypeClass(ClassV16);           //	STRUCT_V16
    new BuildingTypeClass(ClassV17);           //	STRUCT_V17
    new BuildingTypeClass(ClassV18);           //	STRUCT_V18
    new BuildingTypeClass(ClassV19);           //	STRUCT_PUMP
    new BuildingTypeClass(ClassV20);           //	STRUCT_V20
    new BuildingTypeClass(ClassV21);           //	STRUCT_V21
    new BuildingTypeClass(ClassV22);           //	STRUCT_V22
    new BuildingTypeClass(ClassV23);           //	STRUCT_V23
    new BuildingTypeClass(ClassV24);           //	STRUCT_V24
    new BuildingTypeClass(ClassV25);           //	STRUCT_V25
    new BuildingTypeClass(ClassV26);           //	STRUCT_V26
    new BuildingTypeClass(ClassV27);           //	STRUCT_V27
    new BuildingTypeClass(ClassV28);           //	STRUCT_V28
    new BuildingTypeClass(ClassV29);           //	STRUCT_V29
    new BuildingTypeClass(ClassV30);           //	STRUCT_V30
    new BuildingTypeClass(ClassV31);           //	STRUCT_V31
    new BuildingTypeClass(ClassV32);           //	STRUCT_V32
    new BuildingTypeClass(ClassV33);           //	STRUCT_V33
    new BuildingTypeClass(ClassV34);           //	STRUCT_V34
    new BuildingTypeClass(ClassV35);           //	STRUCT_V35
    new BuildingTypeClass(ClassV36);           //	STRUCT_V36
    new BuildingTypeClass(ClassV37);           //	STRUCT_V37
    new BuildingTypeClass(ClassBarrel);        // STRUCT_BARREL
    new BuildingTypeClass(ClassBarrel3);       // STRUCT_BARREL3

#ifdef FIXIT_ANTS
    new BuildingTypeClass(ClassQueen);  // STRUCT_QUEEN
    new BuildingTypeClass(ClassLarva1); // STRUCT_LARVA1
    new BuildingTypeClass(ClassLarva2); // STRUCT_LARVA2
#endif

    // TF: the mod's buildings, appended in StructType enum order like the rest.
    new BuildingTypeClass(ClassObelisk); // STRUCT_TDOBLI (Nod Obelisk of Light)
    new BuildingTypeClass(ClassTdNuke);  // STRUCT_TDNUKE  (Power Plant)
    new BuildingTypeClass(ClassTdNuk2);  // STRUCT_TDNUK2  (Advanced Power Plant)
    new BuildingTypeClass(ClassTdPyle);  // STRUCT_TDPYLE  (GDI Barracks)
    new BuildingTypeClass(ClassTdSilo);  // STRUCT_TDSILO  (Tiberium Silo)
    new BuildingTypeClass(ClassTdGtwr);  // STRUCT_TDGTWR  (Guard Tower)
    new BuildingTypeClass(ClassTdAtwr);  // STRUCT_TDATWR  (Advanced Guard Tower)
    new BuildingTypeClass(ClassTdGun);   // STRUCT_TDGUN   (Nod Turret)
    new BuildingTypeClass(ClassTdSam);   // STRUCT_TDSAM   (SAM Site)
    new BuildingTypeClass(ClassTdHand);  // STRUCT_TDHAND  (Hand of Nod)
    new BuildingTypeClass(ClassTdHpad);  // STRUCT_TDHPAD  (Helipad)
    new BuildingTypeClass(ClassTdFix);   // STRUCT_TDFIX   (Service Depot)
    new BuildingTypeClass(ClassTdHq);    // STRUCT_TDHQ    (Communications Center)
    new BuildingTypeClass(ClassTdWeap);  // STRUCT_TDWEAP  (Weapons Factory)
    new BuildingTypeClass(ClassTdAfld);  // STRUCT_TDAFLD  (Nod Airstrip)
    new BuildingTypeClass(ClassTdFact);  // STRUCT_TDFACT  (Construction Yard)
    new BuildingTypeClass(ClassTdProc);  // STRUCT_TDPROC  (Tiberium Refinery)
    new BuildingTypeClass(ClassTdEye);   // STRUCT_TDEYE   (Advanced Communications Center)
    new BuildingTypeClass(ClassTdTmpl);  // STRUCT_TDTMPL  (Temple of Nod)
    new BuildingTypeClass(ClassTdBlossom); // STRUCT_TDBLOSSOM (blossom tree as a building)
    new BuildingTypeClass(ClassTdGYard);   // STRUCT_TDGYARD  (GDI Naval Yard)   — enum order
    new BuildingTypeClass(ClassTdNPen);    // STRUCT_TDNPEN   (Nod Sub Pen)
    new BuildingTypeClass(ClassTdGAfld);   // STRUCT_TDGAFLD  (GDI Airfield)
    new BuildingTypeClass(ClassTdStealth); // STRUCT_TDSTEALTH (Nod Stealth Generator)
    new BuildingTypeClass(ClassFlameBunker); // STRUCT_TDFBNK (Nod Flame Bunker)
    new BuildingTypeClass(ClassTsPowr);      // STRUCT_TSPOWR (TS GDI Power Plant)
    new BuildingTypeClass(ClassTdNodFact);   // STRUCT_TDNFACT (Nod Construction Yard)
    new BuildingTypeClass(ClassTdGdiFact);   // STRUCT_TDGFACT (GDI Construction Yard)
    new BuildingTypeClass(ClassTdGdiHpad);   // STRUCT_TDGHPAD (GDI Helipad)
    new BuildingTypeClass(ClassTdNodHpad);   // STRUCT_TDNHPAD (Nod Helipad)
    new BuildingTypeClass(ClassSovietFact);  // STRUCT_SFACT   (Soviet Construction Yard)
    new BuildingTypeClass(ClassAlliedFact);  // STRUCT_AFACT   (Allied Construction Yard)
    new BuildingTypeClass(ClassAlliedWeapon); // STRUCT_AWEAP  (Allied War Factory)
    new BuildingTypeClass(ClassSovietWeapon); // STRUCT_SWEAP  (Soviet War Factory)
    new BuildingTypeClass(ClassAlliedHelipad); // STRUCT_AHPAD (Allied Helipad)
    new BuildingTypeClass(ClassSovietHelipad); // STRUCT_SHPAD (Soviet Helipad)
    // Heap slot index must equal the Type enum value (As_Reference indexes the
    // heap directly) -- register strictly in enum order, append new types HERE.
    new BuildingTypeClass(ClassTsFact);        // STRUCT_TSFACT (TS Construction Yard)
    new BuildingTypeClass(ClassTsPile);        // STRUCT_TSPILE (TS Barracks)
    new BuildingTypeClass(ClassTsProc);        // STRUCT_TSPROC (TS Refinery)
    new BuildingTypeClass(ClassTsSilo);        // STRUCT_TSSILO (TS Silo)
    new BuildingTypeClass(ClassTsWeap);        // STRUCT_TSWEAP (TS War Factory)
    new BuildingTypeClass(ClassTsRadr);        // STRUCT_TSRADR (TS Radar)
    new BuildingTypeClass(ClassTsHpad);        // STRUCT_TSHPAD (TS Helipad)
    new BuildingTypeClass(ClassTsTech);        // STRUCT_TSTECH (TS Tech Center)
    new BuildingTypeClass(ClassTsDept);        // STRUCT_TSDEPT (TS Service Depot)
    new BuildingTypeClass(ClassTsDrop);        // STRUCT_TSDROP (TS Dropship Bay)
    new BuildingTypeClass(ClassTsTurb);        // STRUCT_TSTURB (TS Power Turbine addon)
    new BuildingTypeClass(ClassTsPlug);        // STRUCT_TSPLUG (TS Upgrade Centre, addon host)
    new BuildingTypeClass(ClassTsPion);        // STRUCT_TSPION (Ion Cannon Uplink addon)
    new BuildingTypeClass(ClassTsPods);        // STRUCT_TSPODS (Drop Pod Node addon)
    new BuildingTypeClass(ClassTsSeek);        // STRUCT_TSSEEK (Seeker Control addon)
    new BuildingTypeClass(ClassTsWall);        // STRUCT_TSWALL (TS concrete wall, overlay on placement)
    new BuildingTypeClass(ClassTsCtwr);        // STRUCT_TSCTWR (TS component tower, bare wall joint)
    new BuildingTypeClass(ClassTsVulc);        // STRUCT_TSVULC (TS Vulcan tower = the Vulcan plug)
    new BuildingTypeClass(ClassTsRock);        // STRUCT_TSROCK (TS RPG tower = the RPG plug)
    new BuildingTypeClass(ClassTsCsam);        // STRUCT_TSCSAM (TS SAM tower = the SAM plug)
    new BuildingTypeClass(ClassTsDlimp);       // STRUCT_TSDLIMP (TS Limpet Mine)

    new BuildingTypeClass(ClassTsPuls);        // STRUCT_TSPULS (TS EMP Pulse Cannon)
    new BuildingTypeClass(ClassTsDpsa);        // STRUCT_TSDPSA (TS Sensor Array)
    new BuildingTypeClass(ClassTsDweap);       // STRUCT_TSDWEAP (Mobile War Factory deployed)
    new BuildingTypeClass(ClassTsFgen);        // STRUCT_TSFGEN (TS Firestorm Generator)
    new BuildingTypeClass(ClassTsFsdf);        // STRUCT_TSFSDF (TS Firestorm Wall Section)
    new BuildingTypeClass(ClassTsNwall);       // STRUCT_TSNWALL (TS Nod wall, overlay on placement)
    new BuildingTypeClass(ClassTsGateH);       // STRUCT_TSGATEH (TS GDI gate, east-west)
    new BuildingTypeClass(ClassTsGateV);       // STRUCT_TSGATEV (TS GDI gate, north-south)
    new BuildingTypeClass(ClassTSNGATEH);
    new BuildingTypeClass(ClassTSNGATEV);
    new BuildingTypeClass(ClassALGATEH);
    new BuildingTypeClass(ClassALGATEV);
    new BuildingTypeClass(ClassSVGATEH);
    new BuildingTypeClass(ClassSVGATEV);
    new BuildingTypeClass(ClassTDGGATEH);
    new BuildingTypeClass(ClassTDGGATEV);
    new BuildingTypeClass(ClassTDNGATEH);
    new BuildingTypeClass(ClassTDNGATEV);

    // TF: addon wiring (TS PowersUpBuilding= and Upgrades=). The statics are const, so it is set on the heap
    // copies.
    As_Reference(STRUCT_TSPOWR).UpgradesMax = 2;                     // TS [GAPOWR] Upgrades=2
    As_Reference(STRUCT_TSTURB).PowersUpBuilding = STRUCT_TSPOWR;    // TS [GAPOWRUP]
    As_Reference(STRUCT_TSPLUG).UpgradesMax = 2;                     // TS [GAPLUG] Upgrades=2
    As_Reference(STRUCT_TSPLUG).IsScanner = true;                    // TS Sensors=yes: cloak detector
    As_Reference(STRUCT_TSPION).PowersUpBuilding = STRUCT_TSPLUG;    // TS [GAPLUG3]
    As_Reference(STRUCT_TSPODS).PowersUpBuilding = STRUCT_TSPLUG;    // our Firestorm-style pod node
    As_Reference(STRUCT_TSSEEK).PowersUpBuilding = STRUCT_TSPLUG;    // TS [GAPLUG2]
    As_Reference(STRUCT_TSCTWR).UpgradesMax = 1;                     // TS [GACTWR]: one plug per tower
    As_Reference(STRUCT_TSCTWR).IsScanner = true;                    // TS Sensors=yes
    As_Reference(STRUCT_TSVULC).PowersUpBuilding = STRUCT_TSCTWR;    // TS [GAVULC] PowersUpBuilding=gactwr
    As_Reference(STRUCT_TSVULC).IsScanner = true;                    // the tower's sensor survives the swap
    As_Reference(STRUCT_TSROCK).PowersUpBuilding = STRUCT_TSCTWR;    // TS [GAROCK]
    As_Reference(STRUCT_TSROCK).IsScanner = true;
    As_Reference(STRUCT_TSCSAM).PowersUpBuilding = STRUCT_TSCTWR;    // TS [GACSAM]
    As_Reference(STRUCT_TSCSAM).IsScanner = true;
}

/***********************************************************************************************
 * BuildingTypeClass::One_Time -- Performs special one time action for buildings.              *
 *                                                                                             *
 *    This routine is used to do the one time action necessary to handle building type class   *
 *    objects. This entails loading of the building shapes and the brain file used by          *
 *    buildings.                                                                               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   This routine should only be called ONCE.                                        *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/28/1994 JLB : Created.                                                                 *
 *   06/11/1994 JLB : Updated construction time and frame count logic.                         *
 *=============================================================================================*/
void BuildingTypeClass::One_Time(void)
{
    static const struct
    {
        StructType Class; // Building class number.
        BStateType Stage; // Animation sequence to assign animation range to.
        int Start;        // Starting frame number.
        int Length;       // Number of frames (-1 means use all frames).
        int Rate;         // Rate of animation.
    } _anims[] = {
        {STRUCT_CHRONOSPHERE, BSTATE_IDLE, 0, 4, 3},    // idling
        {STRUCT_CHRONOSPHERE, BSTATE_ACTIVE, 4, 16, 3}, // charging up and activating
        {STRUCT_MSLO, BSTATE_IDLE, 0, 0, 0},
        {STRUCT_MSLO, BSTATE_ACTIVE, 0, 5, 2}, // door opening
        {STRUCT_MSLO, BSTATE_AUX1, 4, 1, 0},   // door held open
        {STRUCT_MSLO, BSTATE_AUX2, 5, 3, 2},   // door closing
        {STRUCT_CAMOPILLBOX, BSTATE_ACTIVE, 0, 2, 1},
        {STRUCT_GAP, BSTATE_IDLE, 0, 32, 3},
        {STRUCT_AIRSTRIP, BSTATE_IDLE, 0, 0, 0},
        {STRUCT_AIRSTRIP, BSTATE_AUX1, 0, 8, 3},
        {STRUCT_BARRACKS, BSTATE_ACTIVE, 0, 10, 3},
        {STRUCT_BARRACKS, BSTATE_IDLE, 0, 10, 3},
        {STRUCT_TENT, BSTATE_ACTIVE, 0, 10, 3},
        {STRUCT_TENT, BSTATE_IDLE, 0, 10, 3},
#ifdef FIXIT_ANTS
        {STRUCT_QUEEN, BSTATE_IDLE, 0, 10, 3},
#endif
        {STRUCT_CONST, BSTATE_ACTIVE, 0, 26, 3},
        {STRUCT_FAKECONST, BSTATE_ACTIVE, 0, 26, 3},
        {STRUCT_HELIPAD, BSTATE_ACTIVE, 0, 7, 4},
        {STRUCT_HELIPAD, BSTATE_IDLE, 0, 0, 0},
        {STRUCT_HOSPITAL, BSTATE_IDLE, 0, 4, 3},
        {STRUCT_PUMP, BSTATE_IDLE, 0, 14, 4},
        {STRUCT_REPAIR, BSTATE_ACTIVE, 0, 7, 2},
        {STRUCT_REPAIR, BSTATE_IDLE, 0, 1, 0},
        {STRUCT_V20, BSTATE_IDLE, 0, 3, 3},
        {STRUCT_V21, BSTATE_IDLE, 0, 3, 3},
        {STRUCT_V22, BSTATE_IDLE, 0, 3, 3},
        {STRUCT_V23, BSTATE_IDLE, 0, 3, 3},
        {STRUCT_WEAP, BSTATE_ACTIVE, 0, 1, 0},
        {STRUCT_WEAP, BSTATE_IDLE, 0, 1, 0},
        {STRUCT_AWEAP, BSTATE_ACTIVE, 0, 1, 0},
        {STRUCT_AWEAP, BSTATE_IDLE, 0, 1, 0},
        {STRUCT_SWEAP, BSTATE_ACTIVE, 0, 1, 0},
        {STRUCT_SWEAP, BSTATE_IDLE, 0, 1, 0},
        {STRUCT_FAKEWEAP, BSTATE_ACTIVE, 0, 1, 0},
        {STRUCT_FAKEWEAP, BSTATE_IDLE, 0, 1, 0},
        {STRUCT_IRON_CURTAIN, BSTATE_ACTIVE, 0, 11, 3},
        {STRUCT_TESLA, BSTATE_ACTIVE, 0, 10, 2},
#ifdef REMASTER_BUILD
        {STRUCT_AIRSTRIP, BSTATE_IDLE, 0, 8, 3},
#endif
        // TF: the mod's buildings, TD ones on TD's own _anims timings. The Obelisk charges while it fires.
        {STRUCT_TDOBLI, BSTATE_ACTIVE, 0, 4, 15},
        {STRUCT_TDNUKE, BSTATE_IDLE, 0, 4, 15},
        {STRUCT_TDNUK2, BSTATE_IDLE, 0, 4, 15},
        {STRUCT_TDPYLE, BSTATE_ACTIVE, 0, 10, 3},
        {STRUCT_TDPYLE, BSTATE_IDLE, 0, 10, 3},
        {STRUCT_TDHPAD, BSTATE_ACTIVE, 0, 7, 4},
        {STRUCT_TDHPAD, BSTATE_IDLE, 0, 0, 0},
        {STRUCT_TDGHPAD, BSTATE_ACTIVE, 0, 7, 4},
        {STRUCT_TDGHPAD, BSTATE_IDLE, 0, 0, 0},
        {STRUCT_TDNHPAD, BSTATE_ACTIVE, 0, 7, 4},
        {STRUCT_TDNHPAD, BSTATE_IDLE, 0, 0, 0},
        {STRUCT_AHPAD, BSTATE_ACTIVE, 0, 7, 4},
        {STRUCT_AHPAD, BSTATE_IDLE, 0, 0, 0},
        {STRUCT_SHPAD, BSTATE_ACTIVE, 0, 7, 4},
        {STRUCT_SHPAD, BSTATE_IDLE, 0, 0, 0},
        {STRUCT_TDFIX, BSTATE_ACTIVE, 0, 7, 2},
        {STRUCT_TDFIX, BSTATE_IDLE, 0, 1, 0},
        {STRUCT_TDHQ, BSTATE_IDLE, 0, 16, 4},
        // TDWEAP's body is static: its door is the TDWEAP2 overlay, not an animation.
        {STRUCT_TDWEAP, BSTATE_ACTIVE, 0, 1, 0},
        {STRUCT_TDWEAP, BSTATE_IDLE, 0, 1, 0},
        // TDAFLD: TD's idle cycle plus RA's airstrip AUX1 cycle.
        {STRUCT_TDAFLD, BSTATE_IDLE, 0, 16, 3},
        {STRUCT_TDAFLD, BSTATE_AUX1, 0, 8, 3},
        {STRUCT_TDFACT, BSTATE_ACTIVE, 4, 20, 3},
        {STRUCT_TDFACT, BSTATE_IDLE, 0, 4, 3},
        {STRUCT_TDNFACT, BSTATE_ACTIVE, 4, 20, 3},
        {STRUCT_TDNFACT, BSTATE_IDLE, 0, 4, 3},
        {STRUCT_TDGFACT, BSTATE_ACTIVE, 4, 20, 3},
        {STRUCT_TDGFACT, BSTATE_IDLE, 0, 4, 3},
        {STRUCT_SFACT, BSTATE_ACTIVE, 0, 26, 3},
        {STRUCT_AFACT, BSTATE_ACTIVE, 0, 26, 3},
        // TDPROC: IDLE, FULL (flashing), ACTIVE docking, AUX1 unloading, AUX2 undocking.
        {STRUCT_TDPROC, BSTATE_ACTIVE, 12, 7, 4},
        {STRUCT_TDPROC, BSTATE_AUX1, 19, 5, 4},
        {STRUCT_TDPROC, BSTATE_AUX2, 24, 6, 4},
        {STRUCT_TDPROC, BSTATE_IDLE, 0, 6, 4},
        {STRUCT_TDPROC, BSTATE_FULL, 6, 6, 4},
        {STRUCT_TDEYE, BSTATE_IDLE, 0, 16, 4},
        // TDTMPL: a static idle; ACTIVE is the five-frame launch, the roof opening and the missile rising.
        {STRUCT_TDTMPL, BSTATE_IDLE, 0, 1, 0},
        {STRUCT_TDTMPL, BSTATE_ACTIVE, 0, 5, 1},
        // TDGAFLD mirrors AIRSTRIP. The naval yard and sub pen have no entries, like RA's.
        {STRUCT_TDGAFLD, BSTATE_IDLE, 0, 0, 0},
        {STRUCT_TDGAFLD, BSTATE_AUX1, 0, 8, 3},
#ifdef REMASTER_BUILD
        {STRUCT_TDGAFLD, BSTATE_IDLE, 0, 8, 3},
#endif
        // Nod Stealth Generator: 16-frame TS NASTLH_A ring animation (composited into
        // the TDSTEAL tileset; frames 16-31 are the damaged-state run).
        {STRUCT_TDSTEALTH, BSTATE_IDLE, 0, 16, 3},
        // TS tree (Stealth Recipe): composited TS active anims; damaged run =
        // second half of the tileset (generic +largest offset in Shape_Number).
        // TSFACT (HD yard): idle 0-29 = fans(10) x roof lamps(15); active 30-49 = the hangar
        // producing while a placed building goes up (Mission_Repair); damaged block at +50.
        {STRUCT_TSFACT, BSTATE_IDLE, 0, 30, 4},
        {STRUCT_TSFACT, BSTATE_ACTIVE, 30, 20, 3},
        {STRUCT_TSSILO, BSTATE_IDLE, 0, 16, 4},  // HD silo: the blades' lamps; one 32-frame block per fill level
        {STRUCT_TSPOWR, BSTATE_IDLE, 0, 12, 4},  // HD plant: tower lights + pods turning; one 24-frame block per turbine level
        {STRUCT_TSPILE, BSTATE_IDLE, 0, 56, 4},  // HD barracks: flag (7) x entrance lamps and beacon (8)
        {STRUCT_TSPROC, BSTATE_IDLE, 0, 16, 3}, // NAREFN _C deck lights (fireball + lid are event layers)
        {STRUCT_TSPROC, BSTATE_FULL, 0, 16, 3}, // customer approaching: lights keep cycling
        {STRUCT_TSDWEAP, BSTATE_IDLE, 0, 120, 3}, // MWAR _A fans (5) + _B lights (12) + _C lamps (8) -> LCM 120
        {STRUCT_TSWEAP, BSTATE_IDLE, 0, 32, 3},  // GAWEAP _A/_B (Rate 400) + _C (Rate 800) baked at 32 steps  // GAWEAP halved windows _A(8)+_B(4)+_C(2) -> LCM 8, swept fwd+back (ping-pong, packer order)
        {STRUCT_TSRADR, BSTATE_IDLE, 0, 28, 3},  // GARADR _A dish: 15-frame half-sweep baked as fwd+reverse ping-pong (28); damaged = torn-dish run at +28
        {STRUCT_TSHPAD, BSTATE_IDLE, 0, 8, 3},   // GAHPAD _A halved (8 healthy + 8 damaged)
        {STRUCT_TSDLIMP, BSTATE_IDLE, 0, 10, 3}, // DLIMP_A blink halved (10 healthy + 10 damaged)
        {STRUCT_TSDPSA, BSTATE_IDLE, 0, 5, 4},   // HD sensor: the head's flash (5 healthy + 5 damaged, unlit)
        {STRUCT_TSTECH, BSTATE_IDLE, 0, 8, 4},   // HD tech centre: the dome's panels pulse (8 healthy + 8 damaged)
        {STRUCT_TSFGEN, BSTATE_IDLE, 0, 48, 2},  // GAFIRE _B (16) every step + _C (6) every 2nd step -> 48, TS's rates; damaged = anims stopped
        {STRUCT_TSDEPT, BSTATE_IDLE, 0, 35, 3},  // GADEPT _A halved(5)+_B whole(7, odd=no damaged half) -> LCM 35
        {STRUCT_TSDEPT, BSTATE_ACTIVE, 0, 35, 3}, // repairing: the same lights, the pad glow on top (TSDEPTRP)
        {STRUCT_TSPLUG, BSTATE_IDLE, 0, 40, 3},  // GAPLUG windows _A(10)+_B(8)+_C(4) -> LCM 40
        {STRUCT_TSDROP, BSTATE_IDLE, 0, 20, 3},  // GTDROP _A dish + _B pad lights (20 healthy + 20 damaged)
        // TSSILO is static (no TS idle anim): shape 0 healthy, 1 damaged.
    };

    for (int sindex = STRUCT_FIRST; sindex < STRUCT_COUNT; sindex++) {
        char fullname[_MAX_FNAME + _MAX_EXT];
        char buffer[_MAX_FNAME + 4];
        BuildingTypeClass const& building = As_Reference((StructType)sindex);
        /*
        **	Fetch the sidebar cameo image for this building.
        */
        if (building.Level != -1) {
            //		if (building.IsBuildable) {
            sprintf(buffer, "%sICON", building.Graphic_Name());

            if (building.IsFake) {
                buffer[3] = 'F';
            }

            _makepath(fullname, NULL, NULL, buffer, ".SHP");
            ((void const*&)building.CameoData) = MFCD::Retrieve(fullname);
        }

        /*
        **	Fetch the construction animation for this building.
        */
        sprintf(buffer, "%sMAKE", building.Graphic_Name());
        _makepath(fullname, NULL, NULL, buffer, ".SHP");
        void const* dataptr;
        dataptr = MFCD::Retrieve(fullname);
        ((void const*&)building.BuildupData) = dataptr;
        if (dataptr != NULL) {
            int timedelay = 1;
            int count = Get_Build_Frame_Count(dataptr);
            if (count > 0) {
                timedelay = (Rule.BuildupTime * TICKS_PER_MINUTE) / count;
            }
            building.Init_Anim(BSTATE_CONSTRUCTION, 0, count, timedelay);
        }

        /*
        **	Fetch the normal game shape for this building.
        */
        _makepath(fullname, NULL, NULL, building.Graphic_Name(), ".SHP");
        ((void const*&)building.ImageData) = MFCD::Retrieve(fullname);
    }

    // Try to load weap2.shp and tesla coil's lightning shapes
    char fullname[_MAX_FNAME + _MAX_EXT];
    _makepath(fullname, NULL, NULL, (char const*)"WEAP2", ".SHP");
    WarFactoryOverlay = MFCD::Retrieve(fullname);
    // TF: door overlays for the TD war factory (TD's WEAP2), the TS war factory and the Mobile War Factory,
    // the TS sets sized to their buildings' stubs.
    _makepath(fullname, NULL, NULL, (char const*)"TDWEAP2", ".SHP");
    WarFactoryOverlayTd = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"TSWEAPDR", ".SHP");
    TsWeapShutter = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"TSWEAPUD", ".SHP");
    TsWeapUnderDoor = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"TSWEAPNF", ".SHP");
    TsWeapFront = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"TSWEAPNU", ".SHP");
    TsWeapFrontOpen = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"TSDWEAPDR", ".SHP");
    TsDweapShutter = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"TSDWEAPUD", ".SHP");
    TsDweapUnderDoor = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"TSDWEAPNF", ".SHP");
    TsDweapFront = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"TSDWEAPNU", ".SHP");
    TsDweapFrontOpen = MFCD::Retrieve(fullname);
    // TS refinery event layers (fireball burst, dock lid), sized to its stub.
    _makepath(fullname, NULL, NULL, (char const*)"TSPROCFR", ".SHP");
    TsRefineryFlame = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"TSPULST", ".SHP");
    TsPulseTurret = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"TSPROCLD", ".SHP");
    TsRefineryLid = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"TSPROCNF", ".SHP");
    TsRefineryFront = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"LITNING", ".SHP");
    LightningShapes = MFCD::Retrieve(fullname);

    /*
    **	Install all the special animation sequences for the different building types.
    */
    for (unsigned index = 0; index < (sizeof(_anims) / sizeof(_anims[0])); index++) {
        As_Reference(_anims[index].Class)
            .Init_Anim(_anims[index].Stage, _anims[index].Start, _anims[index].Length, _anims[index].Rate);
    }

    // TF: types made from [NewBuildings] sit past STRUCT_COUNT, beyond the loop above, so their art loads here
    // by Graphic_Name.
    /*
    **  Diagnostic — log what MFCD::Retrieve returns for each mod entry's
    **  asset lookups. Tells us whether NUK2.SHP / NUKEMAKE.SHP etc. are
    **  resolvable in the mixfile registry, or coming back NULL.
    */
    FILE* mod_log = NULL;
    {
        char mpath[512];
        const char* mprof = getenv("USERPROFILE");
        if (mprof != NULL && mprof[0] != '\0') {
            snprintf(mpath, sizeof(mpath),
                     "%s/Documents/CnCRemastered/tf_mod_one_time.log", mprof);
        } else {
            strcpy(mpath, "tf_mod_one_time.log");
        }
        mod_log = NULL; // TF DIAG OFF for release (was fopen; restore to re-enable)
        if (mod_log != NULL) {
            fprintf(mod_log, "BuildingTypes.Count()=%d STRUCT_COUNT=%d\n",
                    BuildingTypes.Count(), STRUCT_COUNT);
            fflush(mod_log);
        }
    }

    for (int sindex = STRUCT_COUNT; sindex < BuildingTypes.Count(); sindex++) {
        BuildingTypeClass& building = *BuildingTypes.Ptr(sindex);
        char fullname[_MAX_FNAME + _MAX_EXT];
        char buffer[_MAX_FNAME + 4];

        void const* cameo_before = building.CameoData;
        void const* buildup_before = building.BuildupData;
        void const* image_before = building.ImageData;

        if (building.Level != -1) {
            sprintf(buffer, "%sICON", building.Graphic_Name());
            if (building.IsFake) {
                buffer[3] = 'F';
            }
            _makepath(fullname, NULL, NULL, buffer, ".SHP");
            ((void const*&)building.CameoData) = MFCD::Retrieve(fullname);
        }

        sprintf(buffer, "%sMAKE", building.Graphic_Name());
        _makepath(fullname, NULL, NULL, buffer, ".SHP");
        void const* dataptr = MFCD::Retrieve(fullname);
        ((void const*&)building.BuildupData) = dataptr;
        if (dataptr != NULL) {
            int timedelay = 1;
            int count = Get_Build_Frame_Count(dataptr);
            if (count > 0) {
                timedelay = (Rule.BuildupTime * TICKS_PER_MINUTE) / count;
            }
            building.Init_Anim(BSTATE_CONSTRUCTION, 0, count, timedelay);
        }

        _makepath(fullname, NULL, NULL, building.Graphic_Name(), ".SHP");
        ((void const*&)building.ImageData) = MFCD::Retrieve(fullname);

        if (mod_log != NULL) {
            fprintf(mod_log,
                    "[%d] IniName=%s GraphicName=%s Type=%d Size=%d "
                    "ImageData: before=%p after=%p (looking for %s.SHP) | "
                    "BuildupData: before=%p after=%p (looking for %sMAKE.SHP) | "
                    "CameoData: before=%p after=%p\n",
                    sindex, building.IniName, building.Graphic_Name(),
                    (int)building.Type, (int)building.Size,
                    image_before, building.ImageData, building.Graphic_Name(),
                    buildup_before, building.BuildupData, building.Graphic_Name(),
                    cameo_before, building.CameoData);
            fflush(mod_log);
        }
    }

    // TF: HD-only buildings ship no classic SHP, so each borrows a counterpart's classic shape, cameo and
    // construction anim. One with its own MAKE stub keeps its anim: a donor's longer count runs past its tiles.
    {
        static const struct { StructType td; StructType ra; } _td_bdonors[] = {
            {STRUCT_TDGYARD, STRUCT_SHIP_YARD},
            {STRUCT_TDNPEN, STRUCT_SUB_PEN},
            {STRUCT_TDGAFLD, STRUCT_AIRSTRIP},
            {STRUCT_TSPOWR, STRUCT_POWER}, // TS power plant (HD-only art)
            {STRUCT_TDSTEALTH, STRUCT_TDSILO}, // Stealth Generator: TS NASTLH art, 2x1 silo-shaped -> TDSILO's classic dims (48x24) + its full TDSILOMAKE construction anim
            // Faction yards, war factories and helipads borrow their era's shared building.
            {STRUCT_AFACT, STRUCT_CONST},
            {STRUCT_SFACT, STRUCT_CONST},
            {STRUCT_TDGFACT, STRUCT_TDFACT},
            {STRUCT_TDNFACT, STRUCT_TDFACT},
            {STRUCT_AWEAP, STRUCT_WEAP},
            {STRUCT_SWEAP, STRUCT_WEAP},
            {STRUCT_AHPAD, STRUCT_HELIPAD},
            {STRUCT_SHPAD, STRUCT_HELIPAD},
            {STRUCT_TDGHPAD, STRUCT_TDHPAD},
            {STRUCT_TDNHPAD, STRUCT_TDHPAD},
            // TS buildings borrow their TD counterpart.
            {STRUCT_TSFACT, STRUCT_TDFACT},
            {STRUCT_TSPILE, STRUCT_TDPYLE},
            {STRUCT_TSPROC, STRUCT_TDPROC},
            {STRUCT_TSSILO, STRUCT_TDSILO},
            {STRUCT_TSWEAP, STRUCT_TDWEAP},
            {STRUCT_TSDWEAP, STRUCT_TDWEAP},
            {STRUCT_TSRADR, STRUCT_TDHQ},
            {STRUCT_TSHPAD, STRUCT_TDHPAD},
            {STRUCT_TSTECH, STRUCT_TDEYE},
            {STRUCT_TSFGEN, STRUCT_TDEYE},
            {STRUCT_TSDEPT, STRUCT_TDFIX},
            {STRUCT_TSDROP, STRUCT_TDFIX},
            {STRUCT_TSPULS, STRUCT_POWER}, // TS EMP cannon: 2x2 donor for ImageData/BuildupData
        };
        for (int di = 0; di < (int)(sizeof(_td_bdonors) / sizeof(_td_bdonors[0])); di++) {
            BuildingTypeClass& b = As_Reference(_td_bdonors[di].td);
            BuildingTypeClass const& d = As_Reference(_td_bdonors[di].ra);
            bool had_own_buildup = (b.BuildupData != NULL);
            if (b.ImageData == NULL)
                ((void const*&)b.ImageData) = d.ImageData;
            if (b.BuildupData == NULL)
                ((void const*&)b.BuildupData) = d.BuildupData;
            if (b.CameoData == NULL)
                ((void const*&)b.CameoData) = d.CameoData;

            if (!had_own_buildup) {
                b.Init_Anim(BSTATE_CONSTRUCTION,
                            d.Anims[BSTATE_CONSTRUCTION].Start,
                            d.Anims[BSTATE_CONSTRUCTION].Count,
                            d.Anims[BSTATE_CONSTRUCTION].Rate);
            }
        }

    }

    if (mod_log != NULL) {
        fclose(mod_log);
    }
}

/***********************************************************************************************
 * Struct_From_Name -- Find BData structure from its name.                                     *
 *                                                                                             *
 *    This routine will convert an ASCII name for a building class into                        *
 *    the actual building class it represents.                                                 *
 *                                                                                             *
 * INPUT:   name  -- ASCII representation of a building class.                                 *
 *                                                                                             *
 * OUTPUT:  Returns with the actual building class number that the string                      *
 *          represents.                                                                        *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/07/1992 JLB : Created.                                                                 *
 *   05/02/1994 JLB : Converted to member function.                                            *
 *=============================================================================================*/
StructType BuildingTypeClass::From_Name(char const* name)
{
    if (name != NULL) {
        for (int classid = STRUCT_FIRST; classid < STRUCT_COUNT; classid++) {
            if (stricmp(As_Reference((StructType)classid).IniName, name) == 0) {
                return ((StructType)classid);
            }
        }
    }
    return (STRUCT_NONE);
}

#ifdef SCENARIO_EDITOR
/***********************************************************************************************
 * BuildingTypeClass::Display -- Renders a generic view of building.                           *
 *                                                                                             *
 *    This routine is used to display a generic representation of the                          *
 *    building. Typical use of this occurs with the scenario editor.                           *
 *                                                                                             *
 * INPUT:   x,y      -- Coordinate to display the building (centered).                         *
 *                                                                                             *
 *          window   -- The window the building should be rendered                             *
 *                      relative to.                                                           *
 *                                                                                             *
 *          house    -- The house color to use for the building.                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/23/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingTypeClass::Display(int x, int y, WindowNumberType window, HousesType) const
{
    void const* ptr = Get_Cameo_Data();
    if (ptr == NULL) {
        IsTheaterShape = IsTheater;
        ptr = Get_Image_Data();
    }
    CC_Draw_Shape(ptr, 0, x, y, window, SHAPE_CENTER | SHAPE_WIN_REL);
    IsTheaterShape = false;
}

/***********************************************************************************************
 * BuildingTypeClass::Prep_For_Add -- Prepares scenario editor for adding a                    *
 *                                                                                             *
 *    This routine is used to prepare the scenario editor for the addition                     *
 *    of a building object to the game.                                                        *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/23/1994 JLB : Created.                                                                 *
 *   06/04/1994 JLB : Uses map editing interface routines.                                     *
 *=============================================================================================*/
void BuildingTypeClass::Prep_For_Add(void)
{
    for (StructType index = STRUCT_FIRST; index < STRUCT_COUNT; index++) {
        if (As_Reference(index).Get_Image_Data()) {
            Map.Add_To_List(&As_Reference(index));
        }
    }
}
#endif

/***********************************************************************************************
 * BuildingTypeClass::Create_And_Place -- Creates and places a building object onto the map.   *
 *                                                                                             *
 *    This routine is used by the scenario editor to create and place buildings on the map.    *
 *                                                                                             *
 * INPUT:   cell     -- The cell that the building is to be placed upon.                       *
 *                                                                                             *
 *          house    -- The owner of the building.                                             *
 *                                                                                             *
 * OUTPUT:  bool; Was the building successfully created and placed on the map?                 *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/28/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
bool BuildingTypeClass::Create_And_Place(CELL cell, HousesType house) const
{
    BuildingClass* ptr;

    ptr = new BuildingClass(this, house);
    if (ptr != NULL) {
        return (ptr->Unlimbo(Cell_Coord(cell), DIR_N));
    }
    return (false);
}

/***********************************************************************************************
 * BuildingTypeClass::Create_One_Of -- Creates a building of this type.                        *
 *                                                                                             *
 *    This routine will create a building object of this type. The building object is in a     *
 *    limbo state. It is presumed that the building object will be unlimboed at the correct    *
 *    place and time. Typical use is when the building is created in a factory situation       *
 *    and will be placed on the map when construction completes.                               *
 *                                                                                             *
 * INPUT:   house -- Pointer to the house that is to be the owner of the building.             *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the building. If the building could not be created       *
 *          then a NULL is returned.                                                           *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/07/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
ObjectClass* BuildingTypeClass::Create_One_Of(HouseClass* house) const
{
    HousesType htype = HOUSE_NEUTRAL;
    if (house != NULL) {
        htype = house->Class->House;
    }
    return (new BuildingClass(this, htype));
}

/***********************************************************************************************
 * BuildingTypeClass::Init_Anim -- Initialize an animation control for a building.             *
 *                                                                                             *
 *    This routine will initialize one animation control element for a                         *
 *    specified building. This modifies a "const" class and thus must                          *
 *    perform some strategic casting to get away with this.                                    *
 *                                                                                             *
 * INPUT:   state -- The animation state to apply these data values to.                        *
 *                                                                                             *
 *          start -- Starting frame for the building's animation.                              *
 *                                                                                             *
 *          count -- The number of frames in this animation.                                   *
 *                                                                                             *
 *          rate  -- The countdown timer between animation frames.                             *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   04/18/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingTypeClass::Init_Anim(BStateType state, int start, int count, int rate) const
{
    ((int&)Anims[state].Start) = start;
    ((int&)Anims[state].Count) = count;
    ((int&)Anims[state].Rate) = rate;
}

/***********************************************************************************************
 * BuildingTypeClass::Init -- Performs theater specific initialization.                        *
 *                                                                                             *
 *    This routine is used to perform any initialization that is custom per theater.           *
 *    Typically, this is fetching the building shape data for those building types that have   *
 *    theater specific art.                                                                    *
 *                                                                                             *
 * INPUT:   theater  -- The theater to base this initialization on.                            *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/21/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingTypeClass::Init(TheaterType theater)
{
    if (theater != LastTheater) {
        char fullname[_MAX_FNAME + _MAX_EXT];

        for (int sindex = STRUCT_FIRST; sindex < STRUCT_COUNT; sindex++) {
            BuildingTypeClass const* classptr = &As_Reference((StructType)sindex);

            if (classptr->IsTheater) {
                _makepath(fullname, NULL, NULL, classptr->Graphic_Name(), Theaters[theater].Suffix);
                ((void const*&)classptr->ImageData) = MFCD::Retrieve(fullname);

                /*
                **	Buildup data is probably theater specific as well. Fetch a pointer to the
                **	data at this time as well.
                */
                sprintf(fullname, "%sMAKE.%s", classptr->Graphic_Name(), Theaters[theater].Suffix);
                ((void const*&)classptr->BuildupData) = MFCD::Retrieve(fullname);
                if (classptr->BuildupData) {
                    int timedelay = 1;
                    int count = Get_Build_Frame_Count(classptr->BuildupData);
                    if (count != 0) {
                        timedelay = (5 * TICKS_PER_SECOND) / count;
                    }
                    classptr->Init_Anim(BSTATE_CONSTRUCTION, 0, count, timedelay);
                }
            }
        }

        // TF: a Logic= aliased mod type copied its donor's art at Read_INI, before a theater-specific donor had
        // loaded it, so the art and construction anim are copied again now.
        for (int sindex = STRUCT_COUNT; sindex < BuildingTypes.Count(); sindex++) {
            BuildingTypeClass const* modptr = &(*BuildingTypes.Ptr(sindex));
            if (modptr->Type >= STRUCT_FIRST && modptr->Type < STRUCT_COUNT) {
                BuildingTypeClass const* donor = &As_Reference(modptr->Type);
                if (donor->IsTheater) {
                    ((void const*&)modptr->ImageData)   = donor->ImageData;
                    ((void const*&)modptr->BuildupData) = donor->BuildupData;
                    modptr->Anims[BSTATE_CONSTRUCTION] = donor->Anims[BSTATE_CONSTRUCTION];
                }
            }
        }
    }
}

/***********************************************************************************************
 * BuildingTypeClass::Dimensions -- Fetches the pixel dimensions of the building.              *
 *                                                                                             *
 *    This routine will fetch the dimensions of the building (in pixels). These dimensions are *
 *    used to render the selection rectangle and the health bar.                               *
 *                                                                                             *
 * INPUT:   width    -- Reference to the pixel width (to be filled in).                        *
 *                                                                                             *
 *          height   -- Reference to the pixel height (to be filled in).                       *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingTypeClass::Dimensions(int& width, int& height) const
{
    width = Width() * ICON_PIXEL_W;
    width -= (width / 5);
    height = Height() * ICON_PIXEL_H;
    height -= (height / 5);
}

/***********************************************************************************************
 * BuildingTypeClass::As_Reference -- Fetches reference to the building type specified.        *
 *                                                                                             *
 *    This routine will fetch a reference to the BuildingTypeClass as indicated by the         *
 *    building type number specified.                                                          *
 *                                                                                             *
 * INPUT:   type  -- The building type number to convert into a BuildingTypeClass reference.   *
 *                                                                                             *
 * OUTPUT:  Returns with a reference to the building type class as indicated by the            *
 *          parameter.                                                                         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
BuildingTypeClass& BuildingTypeClass::As_Reference(StructType type)
{
    return (*BuildingTypes.Ptr(type));
}

/***********************************************************************************************
 * BuildingTypeClass::Occupy_List -- Fetches the occupy list for the building.                 *
 *                                                                                             *
 *    Use this routine to fetch the occupy list pointer for the building. The occupy list is   *
 *    used to determine what cells the building occupies and thus precludes other buildings    *
 *    or objects from using.                                                                   *
 *                                                                                             *
 * INPUT:   placement   -- Is this for placement legality checking only? The normal condition  *
 *                         is for marking occupation flags.                                    *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to a cell offset list to be used to determine what cells    *
 *          this building occupies.                                                            *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
short const* BuildingTypeClass::Occupy_List(bool placement) const
{
    // TF: TS refinery and war factory placement spans their concrete aprons too, so no apron drapes over a
    // cliff; their blocking lists leave the dock pad and the bay approach walkable.
    if (placement && Type == STRUCT_TSPROC) {
        static short const _ts_proc_place[] = {0,
                                               1,
                                               2,
                                               3,
                                               MAP_CELL_W,
                                               MAP_CELL_W + 1,
                                               MAP_CELL_W + 2,
                                               MAP_CELL_W + 3,
                                               MAP_CELL_W * 2,
                                               MAP_CELL_W * 2 + 1,
                                               MAP_CELL_W * 2 + 2,
                                               MAP_CELL_W * 2 + 3,
                                               REFRESH_EOL};
        return (_ts_proc_place);
    }
    if (placement && (Type == STRUCT_TSWEAP || Type == STRUCT_TSDWEAP)) {
        // The ghost covers the hall and the concrete in front of it.
        static short const _ts_weap3_place[] = {0, 1, 2, MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2,
                                                MAP_CELL_W * 2, MAP_CELL_W * 2 + 1, MAP_CELL_W * 2 + 2, REFRESH_EOL};
        return (_ts_weap3_place);
    }

    /*
    **	The tall buildings (power plant, radar, tech centre) occupy only their south row;
    **	the north row is art headroom units walk behind. Their PLACEMENT list
    **	still spans the full declared box: the launcher anchors the placement
    **	cursor on the BSIZE origin, so a south-row-only ghost draws one cell
    **	below the cursor and the pair could anchor a row higher than any
    **	other building at the map's top edge. Ghost = the whole box, cursor
    **	on its top row, and the headroom row is demanded clear at placement
    **	(the radar height trick); blocking stays south-row-only.
    */
    if (placement && (Type == STRUCT_TSPOWR || Type == STRUCT_TSRADR)) {
        /*
        **	Legality spans headroom + pads + bib: three rows from the plot
        **	origin. The GHOST the launcher draws is only the two ground rows
        **	(pads + bib, like the barracks' 2x1 + bib) -- see
        **	Placement_Ghost_Rows_Above(): the sidebar export drops the headroom
        **	row and Place() re-anchors the plot one row above the ghost.
        */
        static short const _ts_tall22_place[] = {0, 1, MAP_CELL_W, MAP_CELL_W + 1,
                                                  MAP_CELL_W * 2, MAP_CELL_W * 2 + 1, REFRESH_EOL};
        return (_ts_tall22_place);
    }
    // TF: a weapon plug is placed on the tower it fits, one cell; it unlimbos with its headroom above.
    if (placement && (Type == STRUCT_TSVULC || Type == STRUCT_TSROCK || Type == STRUCT_TSCSAM)) {
        return (List1);
    }
    // TF: the TS Service Depot's ghost is its whole 3x3, the free north-east cells included.
    if (placement && Type == STRUCT_TSDEPT) {
        return (TsList33);
    }
    if (placement && (Type == STRUCT_TSTECH || Type == STRUCT_TSFGEN)) {
        static short const _ts_tall32_place[] = {0, 1, 2, MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2,
                                                  MAP_CELL_W * 2, MAP_CELL_W * 2 + 1, MAP_CELL_W * 2 + 2, REFRESH_EOL};
        return (_ts_tall32_place);
    }

    SmudgeType bib = SMUDGE_NONE;
    CELL cell = 0;

    if (placement && Bib_And_Offset(bib, cell)) {

        SmudgeTypeClass const& smudge = SmudgeTypeClass::As_Reference(bib);
        static short _list[50];
        short* dest = &_list[0];

        /*
        **	Copy the bib overlap list into the working buffer.
        */
        short const* src = smudge.Occupy_List();
        while (*src != REFRESH_EOL) {
            *dest++ = (*src++) + cell;
        }

        /*
        **	Append the building occupy list to this working buffer.
        */
        src = OccupyList;
        while (src && *src != REFRESH_EOL) {
            *dest++ = *src++;
        }
        *dest = REFRESH_EOL;

        return (&_list[0]);
    }

    if (OccupyList != NULL) {
        return (OccupyList);
    }

    static short const _templap[] = {REFRESH_EOL};
    return (&_templap[0]);
}

/***********************************************************************************************
 * BuildingTypeClass::Overlap_List -- Fetches the overlap list for the building.               *
 *                                                                                             *
 *    This routine will fetch the overlap list for the building. The overlap list is used      *
 *    to determine what cells the building's graphics cover, but is not considered to occupy   *
 *    for movement purposes.                                                                   *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the cell offset list that is used to determine the       *
 *          cells that this building overlaps.                                                 *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
short const* BuildingTypeClass::Overlap_List(void) const
{
    if (OverlapList != NULL) {
        return (OverlapList);
    }

    static short const _templap[] = {REFRESH_EOL};
    return (&_templap[0]);
}

/***********************************************************************************************
 * BuildingTypeClass::Width -- Determines width of building in icons.                          *
 *                                                                                             *
 *    Use this routine to determine the width of the building type in icons.                   *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the building width in icons.                                          *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   02/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingTypeClass::Width(void) const
{
    static int width[BSIZE_COUNT] = {1, 2, 1, 2, 2, 3, 3, 4, 5, 4, 4, 5, 3, 1, 3};
    return (width[Size]);
}

/***********************************************************************************************
 * BuildingTypeClass::Height -- Determines the height of the building in icons.                *
 *                                                                                             *
 *    Use this routine to find the height of the building in icons.                            *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the building height in icons.                                         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   02/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingTypeClass::Height(bool bib) const
{
    static int height[BSIZE_COUNT] = {1, 1, 2, 2, 3, 2, 3, 2, 5, 3, 4, 3, 1, 3, 4};
    return (height[Size] + ((bib && IsBibbed) ? 1 : 0));
}

/***********************************************************************************************
 * BuildingTypeClass::Bib_And_Offset -- Determines the bib and appropriate cell offset.        *
 *                                                                                             *
 *    This routine is used to determine what (if any) bib should be used for this building     *
 *    and also the cell offset for the upper left corner of the bib smudge type.               *
 *                                                                                             *
 * INPUT:   bib   -- Reference to the bib that should be used for this building.               *
 *                                                                                             *
 *          cell  -- The cell offset for the upper left corner of the bib. This offset is      *
 *                   relative to the upper left corner of the building.                        *
 *                                                                                             *
 * OUTPUT:  Is a bib required for this building? If the result is true, then the correct       *
 *          bib and cell offset will be filled in.                                             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
/*
**	Rows of the placement list that are art headroom above the ground the
**	player aims: the launcher draws those cells as ghost too, so the sidebar
**	export drops them and Place() anchors the plot that many rows north of
**	the cell the launcher sends. Only the tall buildings have any.
*/
int BuildingTypeClass::Placement_Ghost_Rows_Above(void) const
{
    if (Type == STRUCT_TSPOWR || Type == STRUCT_TSRADR || Type == STRUCT_TSTECH || Type == STRUCT_TSFGEN
        || Type == STRUCT_TSCTWR) {
        return (1);
    }
    return (0);
}


bool BuildingTypeClass::Bib_And_Offset(SmudgeType& bib, CELL& cell) const
{
    bib = SMUDGE_NONE;

    if (IsBibbed) {
        switch (Width()) {
        case 2:
            bib = SMUDGE_BIB3;
            break;

        case 3:
            bib = SMUDGE_BIB2;
            break;

        case 4:
            bib = SMUDGE_BIB1;
            break;

        default:
            bib = SMUDGE_NONE;
            break;
        }

        /*
        **	Adjust the bib position for special buildings that have the bib as part
        **	of the building art itself.
        */
        if (bib != SMUDGE_NONE) {
            cell += ((Height() - 1) * MAP_CELL_W);
        }
    }
    return (bib != SMUDGE_NONE);
}

/***********************************************************************************************
 * BuildingTypeClass::Max_Pips -- Determines the maximum pips to display.                      *
 *                                                                                             *
 *    Use this routine to determine the maximum number of pips to display on this building     *
 *    when it is rendered. Typically, this is the tiberium capacity divided by 100.            *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of pips to display on this building when selected.         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingTypeClass::Max_Pips(void) const
{
    int maxpips = (Width() * ICON_PIXEL_W) / 4;
    return (Bound((int)(Capacity / 100), 0, maxpips));
}

/***********************************************************************************************
 * BuildingTypeClass::Raw_Cost -- Fetches the raw (base) cost of this building type.           *
 *                                                                                             *
 *    This routine is used to fetch the real raw base cost of the building. The raw cost       *
 *    is the cost of the building less any free unit that would come with the building         *
 *    if it were built in the normal fashion. Specifically, the helicopter cost is subtracted  *
 *    from the helipad and the harvester cost is subtracted from the refinery. This cost       *
 *    is used for refunding.                                                                   *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns the raw (base) cost to build the building of this type.                    *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/21/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingTypeClass::Raw_Cost(void) const
{
    int cost = TechnoTypeClass::Raw_Cost();

    if (Is_Helipad() && !Rule.IsSeparate) {
        cost -=
            (AircraftTypeClass::As_Reference(AIRCRAFT_HIND).Cost + AircraftTypeClass::As_Reference(AIRCRAFT_HIND).Cost)
            / 2;
    }
    if (Type == STRUCT_REFINERY) {
        cost -= UnitTypeClass::As_Reference(UNIT_HARVESTER).Cost;
    }
    // TF: the TD and TS refineries come with free harvesters of their own.
    if (Type == STRUCT_TDPROC) {
        cost -= UnitTypeClass::As_Reference(UNIT_TDHARV).Cost;
    }
    if (Type == STRUCT_TSPROC) {
        cost -= UnitTypeClass::As_Reference(UNIT_TSHARV).Cost;
    }
    return (cost);
}

/***********************************************************************************************
 * BuildingTypeClass::Cost_Of -- Fetches the cost of this building.                            *
 *                                                                                             *
 *    This routine will fetch the cost to build the building of this type.                     *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the cost to produce this building.                                    *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/21/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingTypeClass::Cost_Of(void) const
{
    if (Rule.IsSeparate && Is_Helipad()) {
        return (Raw_Cost());
    }
    return (TechnoTypeClass::Cost_Of());
}

/***********************************************************************************************
 * BuildingTypeClass::Flush_For_Placement -- Tries to clear placement area for this building t *
 *                                                                                             *
 *    This routine is called when a clear space for placement is desired at the cell location  *
 *    specified. Typical use of this routine is by the computer when it wants to build up      *
 *    its base.                                                                                *
 *                                                                                             *
 * INPUT:   cell  -- The cell that the building of this type would like to be placed down at.  *
 *                                                                                             *
 *          house -- Pointer to the house that want to clear the foundation zone.              *
 *                                                                                             *
 * OUTPUT:  Placement is temporarily blocked, please try again later?                          *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/27/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool BuildingTypeClass::Flush_For_Placement(CELL cell, HouseClass* house) const
{
    bool again = false;
    if (cell > 0) {
        short const* list = Occupy_List(true);

        while (*list != REFRESH_EOL) {
            CELL newcell = cell + *list++;

            if (Map.In_Radar(newcell)) {
                TechnoClass* occupier = Map[newcell].Cell_Techno();
                if (occupier != NULL) {
                    again = true;
                    if (occupier->House->Is_Ally(house) && occupier->Is_Foot()
                        && !Target_Legal(((FootClass*)occupier)->NavCom)) {
                        Map[newcell].Incoming(0, true);
                    } else {
                        //						Base_Is_Attacked(occupier);
                    }
                }
            }
        }
    }
    return (again);
}

/***********************************************************************************************
 * BuildingTypeClass::Read_INI -- Fetch building type data from the INI database.              *
 *                                                                                             *
 *    This routine will fetch the building type class data from the INI database file.         *
 *                                                                                             *
 * INPUT:   ini   -- Reference to the INI database that will be examined.                      *
 *                                                                                             *
 * OUTPUT:  bool; Was the building entry found and the data extracted?                         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/19/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
bool BuildingTypeClass::Read_INI(CCINIClass& ini)
{
    if (TechnoTypeClass::Read_INI(ini)) {
        // TF: the blossom tree is immune to combat damage, as TD's is; its Take_Damage refuses forced damage too.
        if (Type == STRUCT_TDBLOSSOM) {
            IsImmune = true;
        }

        // TF: a building whose IniName starts with TD gets double its listed strength, as TD's own buildings do,
        // and three more cells of sight, since TD's sight ranges read short at RA's scale.
        if (Name()[0] == 'T' && Name()[1] == 'D') {
            MaxStrength *= 2;
            SightRange += 3;
        }
        Speed = ini.Get_Bool(Name(), "WaterBound", (Speed == SPEED_FLOAT)) ? SPEED_FLOAT : SPEED_NONE;
        Capacity = ini.Get_Int(Name(), "Storage", Capacity);
        Adjacent = ini.Get_Int(Name(), "Adjacent", Adjacent);
        IsCaptureable = ini.Get_Bool(Name(), "Capturable", IsCaptureable);
        IsPowered = ini.Get_Bool(Name(), "Powered", IsPowered);
        IsBibbed = ini.Get_Bool(Name(), "Bib", IsBibbed);
        IsUnsellable = ini.Get_Bool(Name(), "Unsellable", IsUnsellable);
        IsBase = ini.Get_Bool(Name(), "BaseNormal", IsBase);
        Power = ini.Get_Int(Name(), "Power", (Power > 0) ? Power : -Drain);

        // TF: Logic=<IniName> makes this type behave as that building: it takes the donor's Type, footprint,
        // exits, anims and art, and the donor's weapons unless its own section names them.
        char buffer[64];
        if (ini.Get_String(Name(), "Logic", "", buffer, sizeof(buffer)) > 0) {
            BuildingTypeClass* donor = BuildingTypeClass::As_Pointer(buffer);
            if (donor != NULL && donor != this) {
                Type = donor->Type;
                Size = donor->Size;
                OccupyList = donor->OccupyList;
                OverlapList = donor->OverlapList;
                BuildupData = donor->BuildupData;
                for (int s = 0; s < BSTATE_COUNT; s++) {
                    Anims[s] = donor->Anims[s];
                }
                FoundationFace = donor->FoundationFace;
                StartFace = donor->StartFace;
                ExitCoordinate = donor->ExitCoordinate;
                ExitList = donor->ExitList;
                ToBuild = donor->ToBuild;
                Adjacent = donor->Adjacent;
                Capacity = donor->Capacity;
                ((void const*&)ImageData) = donor->ImageData;
                if (PrimaryWeapon == NULL && !ini.Is_Present(Name(), "Primary")) {
                    PrimaryWeapon = donor->PrimaryWeapon;
                }
                if (SecondaryWeapon == NULL && !ini.Is_Present(Name(), "Secondary")) {
                    SecondaryWeapon = donor->SecondaryWeapon;
                }
            }
        }

        // TF: Footprint=<preset> gives a TD building TD's own footprint and, for HAND and WEAP, TD's exits.
        static short const List_NUK2_OCCUPY[]  = {0, MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL};
        static short const List_NUK2_OVERLAP[] = {1, REFRESH_EOL};
        static short const List_PYLE_OCCUPY[]  = {0, 1, REFRESH_EOL};
        static short const List_PYLE_OVERLAP[] = {MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL};
        static short const List_WEAP_OCCUPY[]  = {
            (MAP_CELL_W * 1), (MAP_CELL_W * 1) + 1, (MAP_CELL_W * 1) + 2,
            (MAP_CELL_W * 2), (MAP_CELL_W * 2) + 1, (MAP_CELL_W * 2) + 2,
            REFRESH_EOL
        };
        static short const List_WEAP_OVERLAP[] = {0, 1, 2, REFRESH_EOL};
        static short const List_SILO_OCCUPY[] = {0, 1, REFRESH_EOL};
        static short const List_HAND_OCCUPY[]  = {MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W * 2 + 1, REFRESH_EOL};
        static short const List_HAND_OVERLAP[] = {0, 1, MAP_CELL_W * 2, MAP_CELL_W, REFRESH_EOL};
        static short const Exit_HAND[] = {
            XYCELL(2, 3),  XYCELL(1, 3),  XYCELL(0, 3),  XYCELL(2, 2),
            XYCELL(-1, 3), XYCELL(-1, 2), XYCELL(0, 0),  XYCELL(1, 0),
            XYCELL(-1, 0), XYCELL(2, 0),  XYCELL(2, 1),  XYCELL(-1, 1),
            REFRESH_EOL
        };
        static short const List_AFLD_OCCUPY[]  = {
            0, 1, 2, 3,
            MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2, MAP_CELL_W + 3,
            REFRESH_EOL
        };
        static short const Exit_AFLD[] = {
            XYCELL(-1, -1), XYCELL(-1, 0),  XYCELL(-1, 1), XYCELL(-1, 2),
            XYCELL(0, -1),  XYCELL(0, 2),
            XYCELL(1, -1),  XYCELL(1, 2),
            XYCELL(2, -1),  XYCELL(2, 2),
            XYCELL(3, -1),  XYCELL(3, 2),
            XYCELL(4, -1),  XYCELL(4, 0),   XYCELL(4, 1),  XYCELL(4, 2),
            REFRESH_EOL
        };
        static short const List_TMPL_OCCUPY[]  = {
            MAP_CELL_W,     MAP_CELL_W + 1, MAP_CELL_W + 2,
            MAP_CELL_W * 2, MAP_CELL_W * 2 + 1, MAP_CELL_W * 2 + 2,
            REFRESH_EOL
        };
        static short const List_TMPL_OVERLAP[] = {0, 1, 2, REFRESH_EOL};
        static short const Exit_WEAP[] = {
            XYCELL(-1, 3), XYCELL(0, 3), XYCELL(-1, 2), XYCELL(1, 3),
            XYCELL(-1, 1), XYCELL(3, 1),
            REFRESH_EOL
        };

        struct FootprintPreset
        {
            char const* name;
            BSizeType   size;
            short const* occupy;
            short const* overlap;
            short const* exit_list;   // NULL = keep the current exit list
            COORDINATE   exit_coord;  // 0 = keep the current exit point
        };
        static FootprintPreset const _presets[] = {
            {"NUKE", BSIZE_22, List_NUK2_OCCUPY, List_NUK2_OVERLAP, NULL, 0},   // shares NUK2's 2x2 L-shape
            {"NUK2", BSIZE_22, List_NUK2_OCCUPY, List_NUK2_OVERLAP, NULL, 0},
            {"EYE",  BSIZE_22, List_NUK2_OCCUPY, List_NUK2_OVERLAP, NULL, 0},   // TD ComList/OComList = NUK2 L-shape
            {"PYLE", BSIZE_22, List_PYLE_OCCUPY, List_PYLE_OVERLAP, NULL, 0},
            {"HAND", BSIZE_23, List_HAND_OCCUPY, List_HAND_OVERLAP, Exit_HAND, XYP_COORD(36, 63)},
            {"AFLD", BSIZE_42, List_AFLD_OCCUPY, NULL,              Exit_AFLD, 0},
            {"TMPL", BSIZE_33, List_TMPL_OCCUPY, List_TMPL_OVERLAP, NULL, 0},   // Temple of Nod, 3x3 (top row overlap)
            {"SILO", BSIZE_21, List_SILO_OCCUPY, NULL,              NULL, 0},   // 2x1 + bib (TD-authentic)
            {"HQ",   BSIZE_22, List_NUK2_OCCUPY, List_NUK2_OVERLAP, NULL, 0},   // TD ComList/OComList = NUK2 L-shape
            {"WEAP", BSIZE_33, List_WEAP_OCCUPY, List_WEAP_OVERLAP, Exit_WEAP,
             XYP_COORD(10 + (CELL_PIXEL_W / 2),
                       ((CELL_PIXEL_H * 3) - (CELL_PIXEL_H / 2)) - 21)},
        };

        if (ini.Get_String(Name(), "Footprint", "", buffer, sizeof(buffer)) > 0) {
            for (unsigned int i = 0; i < sizeof(_presets) / sizeof(_presets[0]); i++) {
                if (stricmp(_presets[i].name, buffer) == 0) {
                    Size        = _presets[i].size;
                    OccupyList  = _presets[i].occupy;
                    OverlapList = _presets[i].overlap;
                    if (_presets[i].exit_list != NULL) {
                        ExitList = _presets[i].exit_list;
                    }
                    if (_presets[i].exit_coord != 0) {
                        ExitCoordinate = _presets[i].exit_coord;
                    }
                    break;
                }
            }
        }

        // TF: ShapeSize=W,H is the pixel size the launcher scales a building's HD art to (24 px a cell by
        // convention); it also decides how the building sorts against units.
        if (ini.Get_String(Name(), "ShapeSize", "", buffer, sizeof(buffer)) > 0) {
            int sw = 0, sh = 0;
            if (sscanf(buffer, "%d,%d", &sw, &sh) == 2 && sw > 0 && sh > 0) {
                ShapeWidth  = sw;
                ShapeHeight = sh;
            }
        }

        // TF: IdleAnim*, ActiveAnim* and BuildupAnim* set animation ranges from rules.ini, to cycle an anim the type
        // lacks or to clamp one that would run past the frames its HD art ships.
        int idle_count = ini.Get_Int(Name(), "IdleAnimCount", -1);
        if (idle_count > 0) {
            int idle_start = ini.Get_Int(Name(), "IdleAnimStart", 0);
            int idle_rate  = ini.Get_Int(Name(), "IdleAnimRate", 4);
            Init_Anim(BSTATE_IDLE, idle_start, idle_count, idle_rate);
        }
        int active_count = ini.Get_Int(Name(), "ActiveAnimCount", -1);
        if (active_count > 0) {
            int active_start = ini.Get_Int(Name(), "ActiveAnimStart", 0);
            int active_rate  = ini.Get_Int(Name(), "ActiveAnimRate", 4);
            Init_Anim(BSTATE_ACTIVE, active_start, active_count, active_rate);
        }
        int buildup_count = ini.Get_Int(Name(), "BuildupAnimCount", -1);
        if (buildup_count > 0) {
            int buildup_start = ini.Get_Int(Name(), "BuildupAnimStart", 0);
            int buildup_rate  = ini.Get_Int(Name(), "BuildupAnimRate", 2);
            Init_Anim(BSTATE_CONSTRUCTION, buildup_start, buildup_count, buildup_rate);
        }

        if (Power < 0) {
            Drain = -Power;
            Power = 0;
        }
        return (true);
    }
    return (false);
}

/***********************************************************************************************
 * BuildingTypeClass::Coord_Fixup -- Adjusts coordinate to be legal for assignment.            *
 *                                                                                             *
 *    This routine will adjust the specified coordinate so that it will be legal for assignment*
 *    to this building. All buildings are given a coordinate that is in the upper left corner  *
 *    of a cell. This routine will drop the fractional component of the coordinate.            *
 *                                                                                             *
 * INPUT:   coord -- The coordinate to fixup into a legal to assign value.                     *
 *                                                                                             *
 * OUTPUT:  Returns with a coordinate that can be assigned to the building.                    *
 *                                                                                             *
 * WARNINGS:   The coordinate is not examined to see if the cell is legal for placing the      *
 *             building. It merely adjusts the coordinate so that is legal at first glance.    *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   08/14/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
COORDINATE BuildingTypeClass::Coord_Fixup(COORDINATE coord) const
{
    return Coord_Whole(coord);
}

/***********************************************************************************************
 * BuildingTypeClass::Full_Name -- Fetches the name to give this building.                     *
 *                                                                                             *
 *    This routine will return the displayable given name for this building type. Normally,    *
 *    this is the official name as well, however in the case of civilian buildings, the        *
 *    name will just be "Civilian Building" unless special options are in place.               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the text number of the building type.                                 *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/02/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingTypeClass::Full_Name(void) const
{
    if (Debug_Map || Rule.IsNamed || *this < STRUCT_V01 || *this > STRUCT_V37) {
        return (TechnoTypeClass::Full_Name());
    }
    return (TXT_CIVILIAN_BUILDING);
}
