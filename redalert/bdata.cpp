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
static short const List1100[] = {0, 1, REFRESH_EOL};
static short const List1101[] = {0, 1, (MCW * 1) + 1, REFRESH_EOL};
static short const List11[] = {0, 1, REFRESH_EOL};
static short const List12[] = {MCW, REFRESH_EOL};
static short const List1[] = {0, REFRESH_EOL};
static short const List21[] = {0, 1, REFRESH_EOL};
static short const List22[] = {0, 1, MCW, MCW + 1, REFRESH_EOL};
static short const List22_0011[] = {MCW, MCW + 1, REFRESH_EOL};
static short const List22_1100[] = {0, 1, REFRESH_EOL};
static short const List2[] = {0, 1, MCW + 1, MCW, REFRESH_EOL};
static short const List32[] = {0, 1, 2, MCW, MCW + 1, MCW + 2, REFRESH_EOL};
// static short const List42[] = {0, 1, 2, 3, MCW, MCW+1, MCW+2, MCW+3, REFRESH_EOL};
static short const ListFix[] = {1, MCW, MCW + 1, MCW + 2, MCW + MCW + 1, REFRESH_EOL};
static short const ListWeap[] = {0, 1, 2, (MCW * 1), (MCW * 1) + 1, (MCW * 1) + 2, REFRESH_EOL};
static short const ListWestwood[] = {1, 2, 3, MCW + 1, MCW + 2, MCW + 3, REFRESH_EOL};
static short const OListSAM[] = {-MCW, -(MCW - 1), REFRESH_EOL};

// Tiberian Factions mod — TDHAND (Nod Hand of Nod) foundation. Copied
// verbatim from tiberiandawn/bdata.cpp:137 (ListHand) and :157 (OListHand).
// Building proper is 2×2 with the bottom-left corner cut (the L-shape
// "thumb" sits at bottom-right); the bib renders in row 3 underneath,
// making the visual placement footprint 2×3 cells. Occupy = middle row
// both cells + bottom-right thumb (3 cells). Overlap = top row + bottom-
// left + middle-left (the sprite extends up into row 0 but no foundation).
static short const ListHand[]  = {MCW, MCW + 1, MCW * 2 + 1, REFRESH_EOL};
static short const OListHand[] = {0, 1, MCW * 2, MCW, REFRESH_EOL};

// TDHAND exit cells — copied verbatim from tiberiandawn/bdata.cpp:77
// (TD's ExitHand). Twelve cells fanning out around the 2×3 footprint so
// infantry spawn on the perimeter, not inside the building.
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

/*
**  Tiberian Factions mod: Nod Obelisk of Light (STRUCT_TDOBLI).
**
**  First fully-separated TD building (2026-05-21). All data and behavior
**  state lives in this own BuildingTypeClass instance — no Logic= alias
**  inheritance from any RA donor. Footprint matches TD's authentic 1x2
**  vertical shape (BSIZE_12), same as RA Tesla Coil (which is why TSLA
**  was the v0.3-era alias donor). Anims defaults set up by constructor
**  are overridden via the [TDOBLI] rules.ini section's IdleAnim* /
**  ActiveAnim* fields plus the One_Time _anims[] table below.
**
**  Stats (Cost, Power, Strength, etc) are read from rules.ini via
**  Read_INI and override the constructor defaults — the constructor's
**  job is only to wire up Type/IniName/footprint/initial-bool-flags.
**
**  See docs/building-separation-plan.md for the M1-M6 plan that this
**  entry kicks off, and docs/td-building-separation-recipe.md (in
**  progress) for the per-building recipe distilled from this work.
*/
/*
**  Tiberian Factions mod — M2 Tier 1 buildings (pure data ports).
**
**  TDNUKE (GDI/Nod Power Plant) — modeled on ClassPower (POWR), 2x2.
**  TDNUK2 (GDI/Nod Advanced Power Plant) — modeled on ClassPower, **2x2 not 3x3**.
**    Vanilla RA's APWR is a 3x3 L-shape; TD's Advanced Power Plant footprint
**    is the same 2x2 as the basic power plant. We use the POWR base instead
**    of ClassAdvancedPower to get the correct foundation; rules.ini's
**    Footprint=NUK2 preset confirms the 2x2 shape.
**  TDPYLE (GDI Barracks) — modeled on ClassTent (TENT), 2x2 infantry factory.
**    TENT's exit-coord (24,47) is fine; ExitPyle exit list is shared.
**  TDSILO (Tiberium Silo) — modeled on ClassStorage (SILO), 2x1 footprint.
*/
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

/*
**  Tiberian Factions mod — M3 Tier 2 defensive turrets.
**
**  TDGTWR (GDI Guard Tower) — 1x1 infantry-firing tower, no rotating
**    turret (frame-cycle hidden). Modeled on ClassPillbox (PBOX).
**  TDATWR (GDI Advanced Guard Tower) — 1x2 missile tower, rotating turret.
**    Modeled on ClassAAGun (AGUN); TOW-style missiles fire on ground and
**    air (Primary=TDTowTwo, dual-role).
**  TDGUN (Nod Cannon Turret) — 1x1 rotating turret. Modeled on RA's
**    ClassTurret (GUN), Primary=TDTurretGun.
**  TDSAM (Nod SAM Site) — 1x2 rotating launcher, AA-only. Wholesale port of
**    TD's ClassSAM: dedicated TdSamState enum + 8-state Mission_Attack +
**    Status-aware Shape_Number + underground half-damage + [TDNike]/[TDPatriot]
**    weapon stack. NOT modeled on RA's ClassSAM. Engine dispatch sites for
**    STRUCT_TDSAM live in building.cpp (positive ORs split, negative
**    exclusions aliased with explanatory comments). See docs/td-sam-deep-dive.md.
*/
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

// TDATWR is a wholesale port of TD's STRUCT_ATOWER — a 1x2 GDI defensive
// tower with a FIXED missile rack (not a rotating turret). The launched
// BULLET_SSM missiles home after launch; the rack itself does not pivot.
// IsTurretEquipped=false is load-bearing: with =true the engine would
// query 32-frame rotation shapes that TDATWR.ZIP doesn't provide, and
// Can_Fire would gate on PrimaryFacing-vs-target match that never resolves.
// See docs/td-atwr-deep-dive.md for the full TD-source citation.
static BuildingTypeClass const ClassTdAtwr(STRUCT_TDATWR,
                                           TXT_NONE,
                                           "TDATWR",
                                           FACING_S,
                                           XYP_COORD(0, 0),
                                           REMAP_ALTERNATE,
                                           0x0030,          // VerticalOffset — TD ClassATower Fire_Coord (was 0x0000).
                                           0x0040,          // PrimaryOffset — TD ClassATower Fire_Coord (was 0x0000).
                                           0x0000,
                                           false,
                                           false,
                                           false,
                                           false,
                                           true,            // IsSimpleDamage — TD ClassATower (was false).
                                           false,
                                           true,
                                           true,
                                           false,
                                           false,
                                           false,           // IsTurretEquipped — TD ClassATower fixed missile rack (was true, load-bearing bug).
                                           true,
                                           RTTI_NONE,
                                           DIR_N,           // Initial facing — TD ClassATower (was DIR_NE).
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

/*
**  Tiberian Factions mod — M4 Tier 3 production buildings.
**
**  TDHAND (Nod Hand of Nod) — infantry factory, ARMOR_WOOD, capturable.
**    Wholesale port of TD's STRUCT_HAND per tiberiandawn/bdata.cpp:1148
**    (ClassHand). The constructor flags match the TD source verbatim: bib,
**    regulated animation, factory, capturable, simple damage, selectable,
**    legal target, repairable, has crew, RTTI_INFANTRYTYPE. BSIZE_23 cell
**    grid: building proper is 2×2 (L-shape thumb at bottom-right, bottom-
**    left clipped) plus bib in row 3. ExitCoordinate is TD's XYP_COORD(36,
**    63) — door at the thumb cell so infantry spawn outside the building.
*/
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

/*
**  TDHPAD (Helipad) — 2×2 aircraft factory, ARMOR_WOOD, capturable.
**    Wholesale port of TD's STRUCT_HELIPAD per tiberiandawn/bdata.cpp:688
**    (ClassHelipad). Factory of RTTI_AIRCRAFTTYPE; no exit cells (helicopter
**    docks on the pad itself). TD's HELIPAD has Crew=false, Repair=true,
**    Capturable=true. ARMOR_WOOD + Strength=400 are TD-authentic; RA's
**    vanilla HELIPAD has Strength=800 which leaked through the Logic=HPAD
**    alias era — corrected here.
*/
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

/*
**  TDFIX (Service Depot) — 3×3 vehicle/aircraft repair bay, ARMOR_WOOD,
**    capturable. Wholesale port of TD's STRUCT_REPAIR per
**    tiberiandawn/bdata.cpp:1250 (ClassRepair). Not a factory
**    (ToBuild=RTTI_NONE). ListFix/OListFix file-scope arrays already
**    exist (used by RA's ClassRepair) — the cross-shape foundation:
**    occupy {1, MCW, MCW+1, MCW+2, MCW*2+1} = top-centre + middle row
**    + bottom-centre. Strength=400 (TD-authentic; RA's REPAIR has 800
**    which leaked through the Logic=FIX alias era).
*/
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

/*
**  TDWEAP (Weapons Factory) — 3×3 vehicle factory, ARMOR_ALUMINUM,
**    capturable, crewed. Wholesale port of TD's STRUCT_WEAP per
**    tiberiandawn/bdata.cpp:265 (ClassWeapon). RTTI_UNITTYPE factory;
**    vehicles exit SW (TD-authentic via Track14 + Exit_Coord).
**
**    Footprint mirrors TD source exactly (NOT RA's 3×2 WEAP shape — that
**    leak was caught and reverted 2026-05-27): BSIZE_33 with bottom 6
**    cells occupied (TdListWeap = rows 1+2) and top row overlap
**    (TdOListWeap = row 0, sprite extends upward into row 0 but
**    pathfinding treats it as walkable). TdExitWeap is TD's exit-cell
**    preference list — vehicles emerge from the south side of row 2.
**    Image=TDWEAP layered via launcher tileset; door overlay shape comes
**    from TDWEAP2.ZIP (see building.cpp Draw_It overlay swap).
*/
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

/*
**  TDPROC (Tiberium Refinery) — 3×3 building, ARMOR_WOOD, capturable, crewed.
**    Wholesale port of TD's STRUCT_REFINERY per tiberiandawn/bdata.cpp:585
**    (ClassRefinery). Capacity=1000, Power=+10/drain=40 (TD-authentic;
**    RA's STRUCT_REFINERY has the same baseline but rules.ini can override).
**
**    Footprint mirrors TD source exactly (NOT RA's STRUCT_REFINERY shape):
**    TdListProc = {row 0 middle, row 1 entire} occupy cells.
**    TdOListProc = {row 0 corners, row 2 entire} overlap (sprite extends
**    here but pathfinding allows passage). RA's PROC uses List010111100 +
**    List101000011 which is a different shape — donor parity trap per
**    playbook §3.13.
**
**    Harvester dock state machine (5 BStates): IDLE 0-5 → ACTIVE 12-18
**    (docking) → AUX1 19-23 (siphoning tiberium) → AUX2 24-29 (undocking).
**    BSTATE_FULL 6-11 plays when Capacity is reached (flashing lights).
*/
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

/*
**  TDFACT (Construction Yard) — 3×2 building, ARMOR_WOOD, capturable, crewed.
**    Wholesale port of TD's STRUCT_CONST per tiberiandawn/bdata.cpp:534
**    (ClassConst). NOT a unit factory — RTTI_BUILDINGTYPE (produces other
**    buildings, not vehicles). Shared by HOUSE_GOOD + HOUSE_BAD, matching
**    TD's original (one MCV/ConYard type for both factions).
**
**    Footprint mirrors TD source exactly: BSIZE_32 + List32 (3×2 = 6 cells,
**    no overlap row). RA's STRUCT_CONST is BSIZE_33 with ListFactory (3×3,
**    9 cells) — a different shape per playbook §3.13 donor-parity trap.
**    Worked example of why "copy donor verbatim" fails for buildings whose
**    TD/RA donor footprints diverge.
*/
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

/*
**  TDAFLD (Nod Airstrip) — 4×2 flat tile, ARMOR_STEEL, capturable, crewed.
**    Wholesale port of TD's STRUCT_AIRSTRIP per tiberiandawn/bdata.cpp:841
**    (ClassAirStrip). RTTI_UNITTYPE factory; vehicles delivered via cargo
**    plane (AIRCRAFT_TDCARGO) using TD's Create_Special_Reinforcement
**    pattern in Exit_Object — see building.cpp case STRUCT_TDAFLD.
**
**    Footprint mirrors TD source: TdList42 occupies all 8 cells of a 4×2
**    flat foundation (no overlap row — TDAFLD is single-layer art, unlike
**    TDWEAP's 3×3 with row-0 overhang). TdExitAirstrip is TD's 16-cell
**    exit preference list — wraps around all 4 sides of the strip so
**    delivered vehicles can disembark to any adjacent cell.
*/
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

/*
**  TDHQ (Communications Center / Radar) — 2×2 radar dome, ARMOR_WOOD,
**    capturable, crewed. Wholesale port of TD's STRUCT_RADAR per
**    tiberiandawn/bdata.cpp:739 (ClassCommand). Not a factory
**    (ToBuild=RTTI_NONE); provides minimap + reveals cloaked units
**    (cloak-detection handled via the BScan STRUCTF_RADAR equivalence
**    set in BuildingClass::Unlimbo). Sight=10 (largest in the catalogue
**    after Comms-tier buildings). Reuses RA's ComList + OComList — same
**    foundation pattern as TD's HQ.
*/
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

/*
**  TDEYE (Advanced Communications Center / Eye of Kane) — 2×2, ARMOR_WOOD,
**    non-capturable, crewed, no turret. Verbatim port of TD's STRUCT_EYE
**    per tiberiandawn/bdata.cpp:213 (ClassEye). Not a factory
**    (ToBuild=RTTI_NONE); hosts the Ion Cannon superweapon (wired in
**    Phase E3 — building separation alone in Phase E1 grants no super).
**    Starting idle frame DirType(160) matches TD source. Reuses RA's
**    ComList/OComList for the 2x2 foundation pattern (same as TDHQ).
*/
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

/*
**  TDTMPL (Temple of Nod) — 3×3, ARMOR_ALUMINUM, non-capturable, crewed,
**  no turret. Verbatim port of TD's STRUCT_TEMPLE per
**  tiberiandawn/bdata.cpp:162 (ClassTemple). Not a factory; hosts the
**  Nuclear Strike superweapon (wired in Phase T2). Simple damage imagery
**  per TD source (line 176, single damaged frame rather than per-frame
**  damage variants). Reuses RA's List000111111 + OListTmpl — same
**  3×3-with-top-row-overlap pattern as TD's ListTmpl/OListTmpl.
*/
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

// Tiberian Factions mod: Nod Stealth Generator (STRUCT_TDSTEALTH). Reuses the RA Gap
// Generator sprite/footprint (Image=GAP in rules.ini) but drops the gap-shroud behaviour
// (that logic is keyed on `*this == STRUCT_GAP`, which this type never matches). Instead it
// hosts a cloak driver that hides friendly buildings+units in radius (see docs/todo.md
// stealth-gen spec). Modeled verbatim on ClassGapGenerator.
static BuildingTypeClass const ClassTdStealth(STRUCT_TDSTEALTH,
                      TXT_NONE,               // Display name token; rules.ini Name= overrides.
                      "TDSTEAL",              // IniName (art aliases GAP tiles / Image=GAP).
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
                      BSIZE_21,               // SIZE: 2x1 building; the bib completes a 2x2
                                              // concrete pad (matches the Tiberium Silo).
                      NULL,                   // Preferred exit cell list.
                      (short const*)List11,      // OCCUPYLIST: 2-wide single row {0,1}.
                      (short const*)List22_1100  // OVERLAPLIST: top row {0,1} (dome overhang).
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

// v4.0 separated faction naval/air production buildings. Clones of the RA SYRD/SPEN/AFLD (same
// stats + foundation), but OWN STRUCT types so each yields only its faction's roster (the proven
// TDHPAD pattern) and gives clean capture semantics. Art = independent TD-prefixed copies of the RA
// sprites (scripts/bundle_ra_building.py); faction-logo reskins later. Owner set in rules.ini.
// GDI Naval Yard (clone of ClassShipYard).
static BuildingTypeClass const ClassTdGYard(
    STRUCT_TDGYARD,
    TXT_SHIP_YARD, // placeholder name (rules.ini Name= overrides).
    "TDGYARD",     // IniName (also the Graphic_Name -> loads TDGYARD.SHP/.ZIP, its own art).
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

/*
**  Dynamic constructor for mod-defined building types. Used by the [NewBuildings]
**  index in rules.ini to register a heap entry whose only initial state is its
**  IniName; Read_INI fills in the rest, and a Logic=<vanilla type> field aliases
**  the runtime Type discriminant to a vanilla StructType for engine dispatch.
**
**  The first param (StructType) is passed both to Type and to AbstractTypeClass::ID.
**  Vanilla entries use their StructType enum value, which equals their heap slot
**  because Init_Heap allocates in enum order. For mod-defined entries we must use
**  the actual heap slot we're being allocated into — not the [NewBuildings] key —
**  because CCPtr<BuildingTypeClass>(this) stores ptr->ID and on deref returns
**  BuildingTypes[ID]. If ID collides with a vanilla StructType, Class lookups for
**  this instance silently resolve to the vanilla entry at that index. The slot is
**  BuildingTypes.Count() - 1 because operator new (Alloc) has already appended us
**  to ActivePointers by the time the init list runs.
*/
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

/*
**  Name-based lookup across the full BuildingTypes heap, including mod-defined
**  entries past STRUCT_COUNT. From_Name(char const*) only walks the vanilla
**  enum range and therefore can't see mod-defined types.
*/
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

// Tiberian Factions -- TD blossom tree rendered as a 1x1 BUILDING (terrain objects
// can't take custom HD art on our stack; buildings render via the loose RA_STRUCTURES
// ZIP pipeline like every other TD building). Unselectable + not-a-legal-target +
// insignificant; the rest of its "harmless scenery" identity (Neutral owner,
// Unsellable, uncapturable, immune, TechLevel=-1, idle bloom anim, huge HP) is set in
// rules.ini [TDBLOSSOM]. Art "TDBLOSSOM" = SPLIT2. Seeds Tiberium via BuildingClass::AI.
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

    // Tiberian Factions mod buildings — append after vanilla entries in
    // exact STRUCT_TD* enum order (per the constraint at the top of this
    // function: heap allocation block index == StructType enum value).
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
        {STRUCT_FAKEWEAP, BSTATE_ACTIVE, 0, 1, 0},
        {STRUCT_FAKEWEAP, BSTATE_IDLE, 0, 1, 0},
        {STRUCT_IRON_CURTAIN, BSTATE_ACTIVE, 0, 11, 3},
        {STRUCT_TESLA, BSTATE_ACTIVE, 0, 10, 2},
#ifdef REMASTER_BUILD
        {STRUCT_AIRSTRIP, BSTATE_IDLE, 0, 8, 3},
#endif
        // Tiberian Factions mod: TDOBLI 4-frame charge cycle at rate 15
        // ticks/frame — TD-authentic OBELISK_ANIMATION_RATE per
        // tiberiandawn/defines.h:323. Cycle plays during BSTATE_ACTIVE
        // (target acquired + firing). Future: separate BSTATE_AUX1 for
        // warmup-then-fire sequencing per TD's original (currently both
        // OBELPOWR + OBELRAY1 trigger on BSTATE_ACTIVE entry).
        {STRUCT_TDOBLI, BSTATE_ACTIVE, 0, 4, 15},
        // M2 Tier 1 — values lifted verbatim from tiberiandawn/bdata.cpp _anims[].
        // POWER + ADVANCED_POWER: 4-frame blinking-generator idle at rate 15.
        // BARRACKS (PYLE in TD): 10-frame cycle on both IDLE and ACTIVE.
        // STORAGE (SILO): no entry — static sprite.
        {STRUCT_TDNUKE, BSTATE_IDLE, 0, 4, 15},
        {STRUCT_TDNUK2, BSTATE_IDLE, 0, 4, 15},
        {STRUCT_TDPYLE, BSTATE_ACTIVE, 0, 10, 3},
        {STRUCT_TDPYLE, BSTATE_IDLE, 0, 10, 3},
        // M4 Tier 3 — TDHPAD rotor-pad cycle (TD-authentic per
        // tiberiandawn/bdata.cpp:3795-3796).
        {STRUCT_TDHPAD, BSTATE_ACTIVE, 0, 7, 4},
        {STRUCT_TDHPAD, BSTATE_IDLE, 0, 0, 0},
        // M4 Tier 3 — TDFIX repair-bay cycle (TD-authentic per
        // tiberiandawn/bdata.cpp:3806-3807).
        {STRUCT_TDFIX, BSTATE_ACTIVE, 0, 7, 2},
        {STRUCT_TDFIX, BSTATE_IDLE, 0, 1, 0},
        // M4 Tier 3 — TDHQ radar-dish rotation (TD-authentic per
        // tiberiandawn/bdata.cpp:3800).
        {STRUCT_TDHQ, BSTATE_IDLE, 0, 16, 4},
        // M4 Tier 3 — TDWEAP body is a static sprite (door animation is the
        // TDWEAP2 overlay layered by the launcher tileset, not via _anims).
        // Values lifted verbatim from tiberiandawn/bdata.cpp:3813-3814.
        {STRUCT_TDWEAP, BSTATE_ACTIVE, 0, 1, 0},
        {STRUCT_TDWEAP, BSTATE_IDLE, 0, 1, 0},
        // M4 Tier 3 — TDAFLD 16-frame idle cycle (radar dish rotation on
        // the strip). TD-authentic per tiberiandawn/bdata.cpp:3789.
        {STRUCT_TDAFLD, BSTATE_IDLE, 0, 16, 3},
        {STRUCT_TDAFLD, BSTATE_AUX1, 0, 8, 3},
        // M4 Tier 3 — TDFACT 20-frame deploy/active cycle + 4-frame idle.
        // TD-authentic per tiberiandawn/bdata.cpp:3792-3793.
        {STRUCT_TDFACT, BSTATE_ACTIVE, 4, 20, 3},
        {STRUCT_TDFACT, BSTATE_IDLE, 0, 4, 3},
        // M4 Tier 3 — TDPROC harvester dock state machine. TD-authentic per
        // tiberiandawn/bdata.cpp:3801-3805. IDLE 0-5 normal; FULL 6-11 plays
        // when Capacity is reached (flashing lights); ACTIVE 12-18 (docking);
        // AUX1 19-23 (siphoning tiberium); AUX2 24-29 (undocking).
        {STRUCT_TDPROC, BSTATE_ACTIVE, 12, 7, 4},
        {STRUCT_TDPROC, BSTATE_AUX1, 19, 5, 4},
        {STRUCT_TDPROC, BSTATE_AUX2, 24, 6, 4},
        {STRUCT_TDPROC, BSTATE_IDLE, 0, 6, 4},
        {STRUCT_TDPROC, BSTATE_FULL, 6, 6, 4},
        // M5 Tier 4 — TDEYE 16-frame idle cycle (TD-authentic per
        // tiberiandawn/bdata.cpp:3794). Ion Cannon visual + super wiring
        // lands in Phase E2/E3; this is the structural building only.
        {STRUCT_TDEYE, BSTATE_IDLE, 0, 16, 4},
        // M5 Tier 4 — TDTMPL idle is a single static frame; BSTATE_ACTIVE
        // is the 5-frame missile-launch sequence (roof opens, missile rises)
        // when the Nuclear Strike fires. Values lifted verbatim from
        // tiberiandawn/bdata.cpp:3808 + :3815.
        {STRUCT_TDTMPL, BSTATE_IDLE, 0, 1, 0},
        {STRUCT_TDTMPL, BSTATE_ACTIVE, 0, 5, 1},
        // v4.0 — GDI Airfield (clone of RA AFLD art, 16-frame rotating radar
        // dish). Mirror STRUCT_AIRSTRIP exactly so it animates identically to
        // the RA airfield. STRUCT_SHIP_YARD / STRUCT_SUB_PEN have NO _anims
        // entries in RA (2-frame static buildings: healthy + damaged), so the
        // GDI Shipyard (TDGYARD) and Nod Sub Pen (TDNPEN) correctly stay static
        // — there is no RA animation to clone for those two.
        {STRUCT_TDGAFLD, BSTATE_IDLE, 0, 0, 0},
        {STRUCT_TDGAFLD, BSTATE_AUX1, 0, 8, 3},
#ifdef REMASTER_BUILD
        {STRUCT_TDGAFLD, BSTATE_IDLE, 0, 8, 3},
#endif
        // Nod Stealth Generator: same 32-frame idle cycle as the Gap Generator sprite.
        {STRUCT_TDSTEALTH, BSTATE_IDLE, 0, 32, 3},
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

        /*
        **  Tiberian Factions mod: TFASSETS.MIX (registered in init.cpp ahead
        **  of LOCAL.MIX) ships TD-origin SHPs renamed with TD-prefix
        **  (TDOBLI.SHP / TDOBLIMAKE.SHP etc.) so the MFCD::Retrieve calls
        **  above resolve them directly. No more borrowing TSLA's ImageData
        **  pointer as a stub — classic-mode rendering now shows our actual
        **  TD SHPs, and Remastered-mode keeps using the TGA tileset XML via
        **  the launcher's Draw_It intercept (which keys on IniName, not on
        **  the ImageData pointer value).
        */
    }

    // Try to load weap2.shp and tesla coil's lightning shapes
    char fullname[_MAX_FNAME + _MAX_EXT];
    _makepath(fullname, NULL, NULL, (char const*)"WEAP2", ".SHP");
    WarFactoryOverlay = MFCD::Retrieve(fullname);
    // TD's WEAP2 (door panel) packed as TDWEAP2.SHP in TFASSETS.MIX. Drawn
    // on STRUCT_TDWEAP only; classic-mode fallback when the launcher's TGA
    // overlay isn't used.
    _makepath(fullname, NULL, NULL, (char const*)"TDWEAP2", ".SHP");
    WarFactoryOverlayTd = MFCD::Retrieve(fullname);
    _makepath(fullname, NULL, NULL, (char const*)"LITNING", ".SHP");
    LightningShapes = MFCD::Retrieve(fullname);

    /*
    **	Install all the special animation sequences for the different building types.
    */
    for (unsigned index = 0; index < (sizeof(_anims) / sizeof(_anims[0])); index++) {
        As_Reference(_anims[index].Class)
            .Init_Anim(_anims[index].Stage, _anims[index].Start, _anims[index].Length, _anims[index].Rate);
    }

    /*
    **  D1 decouple — per-entry asset load for mod-defined building types
    **  past STRUCT_COUNT. These entries were created from [NewBuildings]
    **  during Rule.Process before One_Time ran; the vanilla loop above
    **  skipped them, leaving ImageData=NULL (Draw_It early-returns) and
    **  Get_Build_Frame_Width/Height(ImageData) reading donor dimensions via
    **  the Logic= inheritance — which is what leaks APWR's 3x3 scale onto
    **  TDNUK2's 2x2 footprint. Loading each entry's own SHP keyed by
    **  Graphic_Name() (Image= rules.ini field, fallback IniName) gives the
    **  launcher's CNCObjectStruct.Width/Height the right per-entry pixel
    **  dimensions and lets Draw_It find a real shapefile.
    */
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

    // v4.0 separated naval/air buildings (TDGYARD/TDNPEN/TDGAFLD): no classic TD*.SHP is shipped
    // (HD-only, rendered from the bundled TD* tilesets), so the MFCD::Retrieve calls above returned
    // NULL -> donor the RA building's ImageData/BuildupData/CameoData as the Draw_It NULL-guard.
    {
        static const struct { StructType td; StructType ra; } _td_bdonors[] = {
            {STRUCT_TDGYARD, STRUCT_SHIP_YARD},
            {STRUCT_TDNPEN, STRUCT_SUB_PEN},
            {STRUCT_TDGAFLD, STRUCT_AIRSTRIP},
        };
        for (int di = 0; di < (int)(sizeof(_td_bdonors) / sizeof(_td_bdonors[0])); di++) {
            BuildingTypeClass& b = As_Reference(_td_bdonors[di].td);
            BuildingTypeClass const& d = As_Reference(_td_bdonors[di].ra);
            if (b.ImageData == NULL)
                ((void const*&)b.ImageData) = d.ImageData;
            if (b.BuildupData == NULL)
                ((void const*&)b.BuildupData) = d.BuildupData;
            if (b.CameoData == NULL)
                ((void const*&)b.CameoData) = d.CameoData;

            // Buildup (construction-placement) animation. The STRUCT_FIRST..
            // STRUCT_COUNT loop above only calls Init_Anim(BSTATE_CONSTRUCTION)
            // when "<TDname>MAKE.SHP" resolves in the mixfiles — but these
            // buildings have no classic TD*MAKE.SHP (HD-only, rendered from the
            // bundled TD*MAKE tileset by IniName). So that loop left their
            // Anims[BSTATE_CONSTRUCTION] at {0,0,0}, which makes the building
            // pop in with NO assembly animation on placement. The donor's
            // construction anim was loaded from its own (identical, cloned)
            // MAKE art, so copy it across — the launcher then cycles the
            // TD*MAKE-#### TGA frames as the building assembles.
            b.Init_Anim(BSTATE_CONSTRUCTION,
                        d.Anims[BSTATE_CONSTRUCTION].Start,
                        d.Anims[BSTATE_CONSTRUCTION].Count,
                        d.Anims[BSTATE_CONSTRUCTION].Rate);
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

        /*
        **  Logic=-aliased mod entries (heap slots past STRUCT_COUNT) inherit
        **  their donor's ImageData/BuildupData at Read_INI time. For donors
        **  that are theater-specific (e.g. MSLO → TDEYE), those pointers were
        **  NULL at Read_INI because Init(theater) hadn't run yet. Now that the
        **  donor has just been refreshed above, re-copy the pointers to any
        **  mod entry whose Type matches a vanilla StructType — the Logic=
        **  block sets Type = donor->Type, so this is the alias relationship.
        */
        for (int sindex = STRUCT_COUNT; sindex < BuildingTypes.Count(); sindex++) {
            BuildingTypeClass const* modptr = &(*BuildingTypes.Ptr(sindex));
            if (modptr->Type >= STRUCT_FIRST && modptr->Type < STRUCT_COUNT) {
                BuildingTypeClass const* donor = &As_Reference(modptr->Type);
                if (donor->IsTheater) {
                    ((void const*&)modptr->ImageData)   = donor->ImageData;
                    ((void const*&)modptr->BuildupData) = donor->BuildupData;
                    // Donor's Anims[BSTATE_CONSTRUCTION] was {0,1,0} at the
                    // Read_INI alias-copy time because Init_Anim only runs
                    // here in Init(theater) for theater-specific donors. Now
                    // that the donor's buildup count/rate is finalized, copy
                    // it to the mod entry so the buildup animation plays the
                    // full frame range instead of completing in one tick.
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
    static int width[BSIZE_COUNT] = {1, 2, 1, 2, 2, 3, 3, 4, 5};
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
    static int height[BSIZE_COUNT] = {1, 1, 2, 2, 3, 2, 3, 2, 5};
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

    if ((Type == STRUCT_HELIPAD || Type == STRUCT_TDHPAD) && !Rule.IsSeparate) {
        cost -=
            (AircraftTypeClass::As_Reference(AIRCRAFT_HIND).Cost + AircraftTypeClass::As_Reference(AIRCRAFT_HIND).Cost)
            / 2;
    }
    if (Type == STRUCT_REFINERY) {
        cost -= UnitTypeClass::As_Reference(UNIT_HARVESTER).Cost;
    }
    if (Type == STRUCT_TDPROC) {
        // TDPROC spawns UNIT_TDHARV via building.cpp's free-harvester block.
        cost -= UnitTypeClass::As_Reference(UNIT_TDHARV).Cost;
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
    if (Rule.IsSeparate && Type == STRUCT_HELIPAD) {
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
        /*
        **  TD buildings carry DOUBLE their listed hit points. TD's
        **  BuildingTypeClass ctor passes strength*2 to TechnoTypeClass
        **  (tiberiandawn/bdata.cpp:3706) — a doubling RA's engine does not have,
        **  and it applies to buildings only (TD units/infantry/aircraft are not
        **  doubled). Our rules.ini holds the verbatim TD-source STRNTH, so
        **  replicate the doubling here for TD-port buildings, identified by the
        **  "TD" IniName-prefix convention. Scoped to BuildingTypeClass::Read_INI,
        **  so TD units/aircraft (TDMCV/TDHARV/TDC17) correctly stay single-HP.
        */
        if (Name()[0] == 'T' && Name()[1] == 'D') {
            MaxStrength *= 2;
            /*
            **  Tiberian Factions mod — +3 sight range on every TD building. TD's
            **  building Sight values are tuned for TD's tighter engagement
            **  distances and read too short on RA's scale (map reveal, radar
            **  footprint, defensive-structure acquisition). A flat +3-cell bump
            **  brings them in line with RA expectations (playtest 2026-06-03:
            **  +2 still read a touch short, nudged to +3). SightRange was already
            **  parsed from rules.ini "Sight=" by the TechnoTypeClass::Read_INI
            **  call above, so this layers on top of the per-building value.
            */
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

        /*
        **  Logic=<vanilla-IniName> aliases this entry's runtime Type discriminant
        **  to a vanilla StructType. Engine dispatch (factory placement, sidebar,
        **  AI heuristics) then treats this custom building as the vanilla type.
        **  Also inherits the donor's physical footprint (Size + occupy/overlap
        **  lists) so placement preview, blocking, and adjacency match the donor.
        **  Only honoured for mod-defined entries; vanilla entries override their
        **  own Type by re-resolving to themselves, which is harmless.
        */
        char buffer[64];
        if (ini.Get_String(Name(), "Logic", "", buffer, sizeof(buffer)) > 0) {
            BuildingTypeClass* donor = BuildingTypeClass::As_Pointer(buffer);
            if (donor != NULL && donor != this) {
                Type = donor->Type;
                Size = donor->Size;
                OccupyList = donor->OccupyList;
                OverlapList = donor->OverlapList;
                // Animation + placement state — placement validation and the
                // buildup/idle/active visual states all key on these. Without
                // them, Logic-aliased entries build at the wrong tick rate and
                // Unlimbo() fails because the buildup data is NULL.
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
                // ImageData is the post-buildup idle SHP. One_Time() only
                // loads it for vanilla heap entries; mod entries past
                // STRUCT_COUNT never get a chance, leaving ImageData=NULL and
                // the engine drawing with width=height=0 (invisible). Inherit
                // donor's pointer — Logic= aliases mean engine dispatch is
                // donor-keyed anyway, so reusing the donor's image is correct.
                ((void const*&)ImageData) = donor->ImageData;
                // Weapon pointers — TechnoTypeClass::Read_INI runs before this
                // block, so an explicit Primary=/Secondary= in the mod entry's
                // INI section will already have populated these. Only fall
                // back to the donor when the entry didn't mention the key AT
                // ALL — Is_Present(section, key) distinguishes "absent"
                // (inherit donor) from "present but parsed to NULL"
                // (explicit clear, don't inherit).
                //
                // Without this Is_Present check, setting Primary=TowTwo
                // overrides Primary correctly but Secondary= (unmentioned)
                // still inherits the donor's secondary weapon — e.g. TDATWR
                // with Logic=AGUN got AGUN's Secondary=ZSU-23 silently
                // bound to its secondary slot, and Which_Weapon would prefer
                // ZSU-23 over TowTwo for any AA-relevant target. Discovered
                // 2026-05-21 via tf_primary_parse.log diagnostic; user
                // playtest showed TDATWR firing ZSU-23 despite the parse log
                // confirming PrimaryWeapon=TowTwo was set correctly.
                if (PrimaryWeapon == NULL && !ini.Is_Present(Name(), "Primary")) {
                    PrimaryWeapon = donor->PrimaryWeapon;
                }
                if (SecondaryWeapon == NULL && !ini.Is_Present(Name(), "Secondary")) {
                    SecondaryWeapon = donor->SecondaryWeapon;
                }
                // Do NOT copy IsTurretEquipped from the donor. AGUN/SAM/TURR
                // donors render turret rotation via PrimaryFacing which the
                // engine's AI rotates toward targets — but for our TD mod
                // entries, enabling the flag causes the firing logic to gate
                // on PrimaryFacing.Current() == direction-to-target (which
                // is never satisfied since nothing rotates PrimaryFacing in
                // our setup), so the turret renders rotating-capable but
                // never actually fires. Without the flag, Turret_Facing()
                // falls back to Direction(TarCom) (building.cpp:2685) — the
                // weapon fires correctly aimed at the target; the visual
                // just doesn't rotate. Wiring proper rotation needs the
                // turret-tracking AI tied in, deferred to the TD-specific
                // weapons work alongside TDOBLI/TDSAM polish.
            }
        }

        /*
        **  Footprint= INI field overrides the inherited donor footprint with a
        **  named TD-style preset. Lets a Logic-aliased building (engine behaves
        **  like POWR) place with a different physical footprint (the actual TD
        **  building's shape, not POWR's L-shape). Required because vanilla
        **  RA's POWR is 2x3 with a specific OccupyList, while TD buildings have
        **  their own footprints that don't match RA's.
        */
        static short const List_NUK2_OCCUPY[]  = {0, MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL};
        static short const List_NUK2_OVERLAP[] = {1, REFRESH_EOL};
        // PYLE (GDI Barracks) — 2x2 footprint matching tiberiandawn/bdata.cpp's
        // ClassBarracks. Top-row occupy + bottom-row overlap follows TD's
        // List22_1100 / List22_0011 pattern.
        //
        // NOTE on footprint vs visual: the placement preview includes the
        // cracked-dirt bib rendered below any `Bib=yes` building (true for
        // both vanilla RA and TD), so a 2x2 structure with a bib can *look*
        // like a 3-row footprint. Trust the source's BSIZE_* declaration
        // over visual impression when sizing entries; the bib is decorative.
        static short const List_PYLE_OCCUPY[]  = {0, 1, REFRESH_EOL};
        static short const List_PYLE_OVERLAP[] = {MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL};
        // WEAP (TD GDI Weapons Factory) — 3×3 footprint, mirroring TD's
        // ListWeap/OListWeap in tiberiandawn/bdata.cpp:74,103. Bottom 6 cells
        // (rows 1+2) are the physical foundation; top row (row 0) is overlap
        // only (visual roof/walls extending up). RA's WEAP donor is 3×2 with
        // all cells fully occupied — Logic=WEAP alone inherits that, but the
        // TD sprite's vertical extent is 3 cells, so the foundation overflows
        // below the cells. Override with this preset gives TD-authentic shape.
        static short const List_WEAP_OCCUPY[]  = {
            (MAP_CELL_W * 1), (MAP_CELL_W * 1) + 1, (MAP_CELL_W * 1) + 2,
            (MAP_CELL_W * 2), (MAP_CELL_W * 2) + 1, (MAP_CELL_W * 2) + 2,
            REFRESH_EOL
        };
        static short const List_WEAP_OVERLAP[] = {0, 1, 2, REFRESH_EOL};
        // SILO (TD Ore Silo) — TD-authentic BSIZE_21 (2 wide × 1 tall),
        // both cells occupied, no overlap. Matches tiberiandawn/bdata.cpp:682
        // ClassStorage + StoreList = {0, 1}. With Bib=yes the placement
        // preview shows 2×2 (top row foundation, bottom row bib decoration).
        static short const List_SILO_OCCUPY[] = {0, 1, REFRESH_EOL};
        // HAND (TD Hand of Nod) — 2 wide × 3 tall L-shape, copied verbatim from
        // tiberiandawn/bdata.cpp:143 (ListHand) and :163 (OListHand). Occupy
        // covers the middle row and bottom-right "thumb"; overlap is the top
        // row, bottom-left, and middle-left (the overlap-on-middle-left mirrors
        // a quirk of TD's data and is harmless — occupy wins for placement).
        static short const List_HAND_OCCUPY[]  = {MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W * 2 + 1, REFRESH_EOL};
        static short const List_HAND_OVERLAP[] = {0, 1, MAP_CELL_W * 2, MAP_CELL_W, REFRESH_EOL};
        // HAND exit cells — copied verbatim from tiberiandawn/bdata.cpp:77
        // (TD's ExitHand). Twelve cells fanning out around the 2×3 footprint
        // so infantry can spawn on any of the building's perimeter tiles.
        static short const Exit_HAND[] = {
            XYCELL(2, 3),  XYCELL(1, 3),  XYCELL(0, 3),  XYCELL(2, 2),
            XYCELL(-1, 3), XYCELL(-1, 2), XYCELL(0, 0),  XYCELL(1, 0),
            XYCELL(-1, 0), XYCELL(2, 0),  XYCELL(2, 1),  XYCELL(-1, 1),
            REFRESH_EOL
        };
        // AFLD (TD Nod Airstrip) — 4 wide × 2 tall, fully occupied (no overlap).
        // Copied verbatim from tiberiandawn/bdata.cpp:136 (List42).
        static short const List_AFLD_OCCUPY[]  = {
            0, 1, 2, 3,
            MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2, MAP_CELL_W + 3,
            REFRESH_EOL
        };
        // AFLD exit cells — copied verbatim from tiberiandawn/bdata.cpp:109
        // (TD's ExitAirstrip). 16 cells around the 4×2 perimeter so vehicles
        // can drive off in any direction. Order is the TD source order; first
        // slot is the preferred exit (top-left corner outside).
        static short const Exit_AFLD[] = {
            XYCELL(-1, -1), XYCELL(-1, 0),  XYCELL(-1, 1), XYCELL(-1, 2),
            XYCELL(0, -1),  XYCELL(0, 2),
            XYCELL(1, -1),  XYCELL(1, 2),
            XYCELL(2, -1),  XYCELL(2, 2),
            XYCELL(3, -1),  XYCELL(3, 2),
            XYCELL(4, -1),  XYCELL(4, 0),   XYCELL(4, 1),  XYCELL(4, 2),
            REFRESH_EOL
        };
        // TMPL (TD Temple of Nod) — 3 wide × 3 tall with overlap on top row,
        // copied verbatim from tiberiandawn/bdata.cpp:144 (ListTmpl, bottom
        // 2 rows occupied) and :164 (OListTmpl, top row overlap). Same
        // shape pattern as TDFACT/TDWEAP construction-yard-style buildings.
        static short const List_TMPL_OCCUPY[]  = {
            MAP_CELL_W,     MAP_CELL_W + 1, MAP_CELL_W + 2,
            MAP_CELL_W * 2, MAP_CELL_W * 2 + 1, MAP_CELL_W * 2 + 2,
            REFRESH_EOL
        };
        static short const List_TMPL_OVERLAP[] = {0, 1, 2, REFRESH_EOL};
        // WEAP exit cells — copied verbatim from tiberiandawn/bdata.cpp:89
        // (TD's ExitWeap array). Order matters: first slot is the preferred
        // exit cell. The commented-out cells in the TD source (row 0
        // entries) are not included here either — TD shipped without them
        // and so do we.
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
            short const* exit_list;   // NULL = keep donor's (Logic= alias copy)
            COORDINATE   exit_coord;  // 0 = keep donor's
        };
        static FootprintPreset const _presets[] = {
            // TD building footprints — copied from tiberiandawn/bdata.cpp.
            // Add new entries as we expand the GDI/Nod catalogue.
            {"NUKE", BSIZE_22, List_NUK2_OCCUPY, List_NUK2_OVERLAP, NULL, 0},   // shares NUK2's 2x2 L-shape
            {"NUK2", BSIZE_22, List_NUK2_OCCUPY, List_NUK2_OVERLAP, NULL, 0},
            {"EYE",  BSIZE_22, List_NUK2_OCCUPY, List_NUK2_OVERLAP, NULL, 0},   // TD ComList/OComList = NUK2 L-shape
            {"PYLE", BSIZE_22, List_PYLE_OCCUPY, List_PYLE_OVERLAP, NULL, 0},
            // HAND: 2x3 L-shape. ExitCoordinate copied verbatim from TD's
            // ClassHand constructor (tiberiandawn/bdata.cpp:1242) — pixel
            // (36, 63) in a 48x72 px building footprint, placing the spawn
            // at the bottom-right "thumb" cell where the door is. Without
            // this override, BARR's 2x2-shaped ExitCoordinate gets inherited
            // and infantry spawn inside the foundation.
            {"HAND", BSIZE_23, List_HAND_OCCUPY, List_HAND_OVERLAP, Exit_HAND, XYP_COORD(36, 63)},
            // AFLD: 4x2 Nod Airstrip. Stopgap reuses WEAP donor; vehicles emerge
            // via WEAP's TD-SW exit track (gotchas #14-15) since RA has no
            // native airstrip mechanic. Cargo-plane choreography is a separate
            // engine slice deferred to its own session.
            {"AFLD", BSIZE_42, List_AFLD_OCCUPY, NULL,              Exit_AFLD, 0},
            {"TMPL", BSIZE_33, List_TMPL_OCCUPY, List_TMPL_OVERLAP, NULL, 0},   // Temple of Nod, 3x3 (top row overlap)
            {"SILO", BSIZE_21, List_SILO_OCCUPY, NULL,              NULL, 0},   // 2x1 + bib (TD-authentic)
            {"HQ",   BSIZE_22, List_NUK2_OCCUPY, List_NUK2_OVERLAP, NULL, 0},   // TD ComList/OComList = NUK2 L-shape
            // WEAP: ExitCoordinate copied verbatim from TD's ClassWeapon
            // constructor in tiberiandawn/bdata.cpp:266 — pixel (22, 39) in
            // a 3×3 (72×72 px) building footprint, placing the spawn at the
            // upper-left interior near the door. If RA's pathfinder ends up
            // snapping this to the first ExitList cell instead of animating,
            // the fix belongs in the engine's vehicle-exit code path, not in
            // these data values.
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

        /*
        **  ShapeSize=W,H — EMC-style explicit pixel dimensions for the
        **  launcher-rendered sprite. Without this, the legacy SHP path
        **  passes width=height=0 to DLL_Draw_Intercept (because the mod
        **  entry's SHP isn't in the mixfile registry), and the Remastered
        **  launcher falls back to TGA-native pixel size — which varies
        **  per asset since TD-Assets's TGAs were drawn with different
        **  building-to-canvas ratios. Setting explicit W,H here gives the
        **  launcher a concrete dim to scale the TGA to, normalising scale
        **  across the catalogue. Convention: W = Width()*24, H = Height()*24
        **  to match the legacy ICON_PIXEL_W/H tile size.
        */
        if (ini.Get_String(Name(), "ShapeSize", "", buffer, sizeof(buffer)) > 0) {
            int sw = 0, sh = 0;
            if (sscanf(buffer, "%d,%d", &sw, &sh) == 2 && sw > 0 && sh > 0) {
                ShapeWidth  = sw;
                ShapeHeight = sh;
            }
        }

        /*
        **  Per-building per-BSTATE animation override. Two directions:
        **  (a) TURN ON cycling — TD passive animations (e.g. NUKE blinking
        **      generator) require Anims[BSTATE_IDLE] to cycle multiple
        **      frames, but Logic= aliasing inherits the donor's Anims which
        **      may be static (POWR has no idle anim entry in _anims[]).
        **  (b) TURN OFF / CLAMP cycling — TD-Assets sprite packs sometimes
        **      collapse N+1 SHP frames to 3 TGAs (e.g. HAND.ZIP has 1 idle
        **      + 1 damaged + 1 destroyed = 3 frames), but the donor's anim
        **      cycles 10. Without a clamp the engine renders frames past
        **      the end of the TGA list, producing a sprite that flickers
        **      between idle / damaged / destroyed / blank.
        **  Setting IdleAnim or ActiveAnim with Count > 0 fires the override.
        **  ActiveAnim covers the BSTATE_ACTIVE branch used while the building
        **  is producing (matters for BARR/TENT-class entries where _anims[]
        **  sets ACTIVE the same way as IDLE).
        */
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
        // BSTATE_CONSTRUCTION (buildup) override. Required for mod entries
        // whose TD-Assets MAKE.ZIP has a different frame count than their
        // Logic= donor's MAKE.SHP. One_Time() can't auto-init these because
        // MFCD::Retrieve("TDxxxxMAKE.SHP") returns NULL — the SHP isn't in
        // REDALERT.MIX. So the donor's BSTATE_CONSTRUCTION is inherited
        // wholesale, and if the donor has fewer MAKE frames than our actual
        // TGA pack, the buildup plays only the early frames before snapping
        // to idle (verified 2026-05-21 on TDTMPL: MSLO donor's ~14-frame
        // buildup truncated our 35-frame temple assembly to just the
        // fragment-scatter early phase). BuildupAnimRate convention: ~2
        // ticks/frame matches Rule.BuildupTime * TICKS_PER_MINUTE / count
        // for typical 20-35 frame MAKE packs.
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
