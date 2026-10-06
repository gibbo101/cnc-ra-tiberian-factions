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

/* $Header: /CounterStrike/UDATA.CPP 1     3/03/97 10:26a Joe_bostic $ */
/***********************************************************************************************
 ***              C O N F I D E N T I A L  ---  W E S T W O O D  S T U D I O S               ***
 ***********************************************************************************************
 *                                                                                             *
 *                 Project Name : Command & Conquer                                            *
 *                                                                                             *
 *                    File Name : UDATA.CPP                                                    *
 *                                                                                             *
 *                   Programmer : Joe L. Bostic                                                *
 *                                                                                             *
 *                   Start Date : September 10, 1993                                           *
 *                                                                                             *
 *                  Last Update : July 19, 1996 [JLB]                                          *
 *                                                                                             *
 *---------------------------------------------------------------------------------------------*
 * Functions:                                                                                  *
 *   UnitTypeClass::As_Reference -- Fetches a reference to the unit type class specified.      *
 *   UnitTypeClass::Create_And_Place -- Creates and places a unit object onto the map.         *
 *   UnitTypeClass::Create_One_Of -- Creates a unit in limbo.                                  *
 *   UnitTypeClass::Dimensions -- Determines the unit's pixel dimensions.                      *
 *   UnitTypeClass::Display -- Displays a generic unit shape.                                  *
 *   UnitTypeClass::From_Name -- Fetch class pointer from specified name.                      *
 *   UnitTypeClass::Init_Heap -- Initialize the unit type class heap.                          *
 *   UnitTypeClass::Max_Pips -- Fetches the maximum pips allowed for this unit.                *
 *   UnitTypeClass::One_Time -- Performs one time processing for unit type class objects.      *
 *   UnitTypeClass::Prep_For_Add -- Prepares scenario editor to add unit.                      *
 *   UnitTypeClass::Read_INI -- Fetch the unit type data from the INI database.                *
 *   UnitTypeClass::Turret_Adjust -- Turret adjustment routine for MLRS and MSAM units.        *
 *   UnitTypeClass::UnitTypeClass -- Constructor for unit types.                               *
 *   UnitTypeClass::operator delete -- Return a unit type class object back to the pool.       *
 *   UnitTypeClass::operator new -- Allocates an object from the unit type class heap.         *
 * - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

#include "function.h"
#include "keyframe.h"
#include "c3tanks.h"

/*
**	This is the list of animation stages to use when the harvester
**	is to dump its load into the refinery. The offsets are based from the
**	start of the dump animation.
*/
const int UnitTypeClass::Harvester_Dump_List[22] = {0,  1,  2,  3,  4, 5, 6, 7, 8, 9, 10,
                                                    11, 12, 13, 14, 6, 5, 4, 3, 2, 1, 0};
const int UnitTypeClass::Harvester_Load_List[9] = {0, 1, 2, 3, 4, 5, 6, 7, 0};
const int UnitTypeClass::Harvester_Load_Count = 8;

// V2 rocket launcher
static UnitTypeClass const UnitV2Launcher(UNIT_V2_LAUNCHER,
                                          TXT_V2_LAUNCHER, // NAME:			Text name of this unit type.
                                          "V2RL",          // NAME:			Text name of this unit type.
                                          ANIM_FRAG1,      // EXPLOSION:	Type of explosion when destroyed.
                                          REMAP_NORMAL,    // Sidebar remap logic.
                                          0x0000,          //	Vertical offset.
                                          0x0000,          // Primary weapon offset along turret centerline.
                                          0x0000,          // Primary weapon lateral offset along turret centerline.
                                          0x0000,          // Secondary weapon offset along turret centerline.
                                          0x0000,          // Secondary weapon lateral offset along turret centerling.
                                          true,            // Can this be a goodie surprise from a crate?
                                          false,           // Always use the given name for the vehicle?
                                          true,            // Can this unit squash infantry?
                                          false,           // Does this unit harvest Tiberium?
                                          false,           // Is invisible to radar?
                                          false,           // Is it insignificant (won't be announced)?
                                          false,           // Is it equipped with a combat turret?
                                          false,           // Does it have a rotating radar dish?
                                          false,           // Is there an associated firing animation?
                                          false,           // Must the turret be in a locked down position while moving?
                                          true,            // Is this a gigundo-rotund-enormous unit?
                                          false,           // Does the unit have a constant animation?
                                          false,           // Is the unit capable of jamming radar?
                                          false,           // Is the unit a mobile gap generator?
                                          32,              // Rotation stages.
                                          0,               // Turret center offset along body centerline.
                                          MISSION_HUNT     // ORDERS:		Default order to give new unit.
);

// Light tank
static UnitTypeClass const UnitLTank(UNIT_LTANK,
                                     TXT_LTANK,    // NAME:			Text name of this unit type.
                                     "1TNK",       // NAME:			Text name of this unit type.
                                     ANIM_FRAG1,   // EXPLOSION:	Type of explosion when destroyed.
                                     REMAP_NORMAL, // Sidebar remap logic.
                                     0x0020,       //	Vertical offset.
                                     0x00C0,       // Primary weapon offset along turret centerline.
                                     0x0000,       // Primary weapon lateral offset along turret centerline.
                                     0x0000,       // Secondary weapon offset along turret centerline.
                                     0x0000,       // Secondary weapon lateral offset along turret centerling.
                                     true,         // Can this be a goodie surprise from a crate?
                                     false,        // Always use the given name for the vehicle?
                                     true,         // Can this unit squash infantry?
                                     false,        // Does this unit harvest Tiberium?
                                     false,        // Is invisible to radar?
                                     false,        // Is it insignificant (won't be announced)?
                                     true,         // Is it equipped with a combat turret?
                                     false,        // Does it have a rotating radar dish?
                                     false,        // Is there an associated firing animation?
                                     false,        // Must the turret be in a locked down position while moving?
                                     false,        // Is this a gigundo-rotund-enormous unit?
                                     false,        // Does the unit have a constant animation?
                                     false,        // Is the unit capable of jamming radar?
                                     false,        // Is the unit a mobile gap generator?
                                     32,           // Rotation stages.
                                     0,            // Turret center offset along body centerline.
                                     MISSION_HUNT  // ORDERS:		Default order to give new unit.
);

// Heavy tank
static UnitTypeClass const UnitMTank(UNIT_MTANK,
                                     TXT_MTANK,    // NAME:			Text name of this unit type.
                                     "3TNK",       // NAME:			Text name of this unit type.
                                     ANIM_FRAG1,   // EXPLOSION:	Type of explosion when destroyed.
                                     REMAP_NORMAL, // Sidebar remap logic.
                                     0x0040,       //	Vertical offset.
                                     0x0080,       // Primary weapon offset along turret centerline.
                                     0x0018,       // Primary weapon lateral offset along turret centerline.
                                     0x0080,       // Secondary weapon offset along turret centerline.
                                     0x0018,       // Secondary weapon lateral offset along turret centerling.
                                     true,         // Can this be a goodie surprise from a crate?
                                     false,        // Always use the given name for the vehicle?
                                     true,         // Can this unit squash infantry?
                                     false,        // Does this unit harvest Tiberium?
                                     false,        // Is invisible to radar?
                                     false,        // Is it insignificant (won't be announced)?
                                     true,         // Is it equipped with a combat turret?
                                     false,        // Does it have a rotating radar dish?
                                     false,        // Is there an associated firing animation?
                                     false,        // Must the turret be in a locked down position while moving?
                                     true,         // Is this a gigundo-rotund-enormous unit?
                                     false,        // Does the unit have a constant animation?
                                     false,        // Is the unit capable of jamming radar?
                                     false,        // Is the unit a mobile gap generator?
                                     32,           // Rotation stages.
                                     0,            // Turret center offset along body centerline.
                                     MISSION_HUNT  // ORDERS:		Default order to give new unit.
);

// Medium tank
static UnitTypeClass const UnitMTank2(UNIT_MTANK2,
                                      TXT_MTANK2,   // NAME:			Text name of this unit type.
                                      "2TNK",       // NAME:			Text name of this unit type.
                                      ANIM_FRAG1,   // EXPLOSION:	Type of explosion when destroyed.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0030,       //	Vertical offset.
                                      0x00C0,       // Primary weapon offset along turret centerline.
                                      0x0000,       // Primary weapon lateral offset along turret centerline.
                                      0x00C0,       // Secondary weapon offset along turret centerline.
                                      0x0000,       // Secondary weapon lateral offset along turret centerling.
                                      true,         // Can this be a goodie surprise from a crate?
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry?
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret?
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      true,         // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline.
                                      MISSION_HUNT  // ORDERS:		Default order to give new unit.
);

// Mastadon tank
static UnitTypeClass const UnitHTank(UNIT_HTANK,
                                     TXT_HTANK,     // NAME:			Text name of this unit type.
                                     "4TNK",        // NAME:			Text name of this unit type.
                                     ANIM_ART_EXP1, // EXPLOSION:	Type of explosion when destroyed.
                                     REMAP_NORMAL,  // Sidebar remap logic.
                                     0x0020,        //	Vertical offset.
                                     0x00C0,        // Primary weapon offset along turret centerline.
                                     0x0028,        // Primary weapon lateral offset along turret centerline.
                                     0x0008,        // Secondary weapon offset along turret centerline.
                                     0x0040,        // Secondary weapon lateral offset along turret centerling.
                                     true,          // Can this be a goodie surprise from a crate?
                                     false,         // Always use the given name for the vehicle?
                                     true,          // Can this unit squash infantry?
                                     false,         // Does this unit harvest Tiberium?
                                     false,         // Is invisible to radar?
                                     false,         // Is it insignificant (won't be announced)?
                                     true,          // Is it equipped with a combat turret?
                                     false,         // Does it have a rotating radar dish?
                                     false,         // Is there an associated firing animation?
                                     false,         // Must the turret be in a locked down position while moving?
                                     true,          // Is this a gigundo-rotund-enormous unit?
                                     false,         // Does the unit have a constant animation?
                                     false,         // Is the unit capable of jamming radar?
                                     false,         // Is the unit a mobile gap generator?
                                     32,            // Rotation stages.
                                     0,             // Turret center offset along body centerline.
                                     MISSION_HUNT   // ORDERS:		Default order to give new unit.
);

// Mobile Radar Jammer
static UnitTypeClass const UnitMRJammer(UNIT_MRJ,
                                        TXT_MRJ,      // NAME:			Text name of this unit type.
                                        "MRJ",        // NAME:			Text name of this unit type.
                                        ANIM_FRAG1,   // EXPLOSION:	Type of explosion when destroyed.
                                        REMAP_NORMAL, // Sidebar remap logic.
                                        0x0000,       //	Vertical offset.
                                        0x0000,       // Primary weapon offset along turret centerline.
                                        0x0000,       // Primary weapon lateral offset along turret centerline.
                                        0x0000,       // Secondary weapon offset along turret centerline.
                                        0x0000,       // Secondary weapon lateral offset along turret centerling.
                                        false,        // Can this be a goodie surprise from a crate?
                                        false,        // Always use the given name for the vehicle?
                                        true,         // Can this unit squash infantry?
                                        false,        // Does this unit harvest Tiberium?
                                        true,         // Is invisible to radar?
                                        false,        // Is it insignificant (won't be announced)?
                                        false,        // Is it equipped with a combat turret?
                                        true,         // Does it have a rotating radar dish?
                                        false,        // Is there an associated firing animation?
                                        false,        // Must the turret be in a locked down position while moving?
                                        false,        // Is this a gigundo-rotund-enormous unit?
                                        false,        // Does the unit have a constant animation?
                                        true,         // Is the unit capable of jamming radar?
                                        false,        // Is the unit a mobile gap generator?
                                        32,           // Rotation stages.
                                        0,            // Turret center offset along body centerline.
                                        MISSION_HUNT  // ORDERS:		Default order to give new unit.
);

// Mobile Gap Generator
static UnitTypeClass const UnitMGG(UNIT_MGG,
                                   TXT_MGG,      // NAME:			Text name of this unit type.
                                   "MGG",        // NAME:			Text name of this unit type.
                                   ANIM_FRAG1,   // EXPLOSION:	Type of explosion when destroyed.
                                   REMAP_NORMAL, // Sidebar remap logic.
                                   0x0000,       //	Vertical offset.
                                   0x0000,       // Primary weapon offset along turret centerline.
                                   0x0000,       // Primary weapon lateral offset along turret centerline.
                                   0x0000,       // Secondary weapon offset along turret centerline.
                                   0x0000,       // Secondary weapon lateral offset along turret centerling.
                                   false,        // Can this be a goodie surprise from a crate?
                                   false,        // Always use the given name for the vehicle?
                                   true,         // Can this unit squash infantry?
                                   false,        // Does this unit harvest Tiberium?
                                   false,        // Is invisible to radar?
                                   false,        // Is it insignificant (won't be announced)?
                                   false,        // Is it equipped with a combat turret?
                                   true,         // Does it have a rotating radar dish?
                                   false,        // Is there an associated firing animation?
                                   false,        // Must the turret be in a locked down position while moving?
                                   true,         // Is this a gigundo-rotund-enormous unit?
                                   false,        // Does the unit have a constant animation?
                                   false,        // Is the unit capable of jamming radar?
                                   true,         // Is the unit a mobile gap generator?
                                   32,           // Rotation stages.
                                   0,            // Turret center offset along body centerline.
                                   MISSION_HUNT  // ORDERS:		Default order to give new unit.
);

// Artillery
static UnitTypeClass const UnitArty(UNIT_ARTY,
                                    TXT_ARTY,      // NAME:			Text name of this unit type.
                                    "ARTY",        // NAME:			Text name of this unit type.
                                    ANIM_ART_EXP1, // EXPLOSION:	Type of explosion when destroyed.
                                    REMAP_NORMAL,  // Sidebar remap logic.
                                    0x0040,        //	Vertical offset.
                                    0x0060,        // Primary weapon offset along turret centerline.
                                    0x0000,        // Primary weapon lateral offset along turret centerline.
                                    0x0000,        // Secondary weapon offset along turret centerline.
                                    0x0000,        // Secondary weapon lateral offset along turret centerling.
                                    true,          // Can this be a goodie surprise from a crate?
                                    false,         // Always use the given name for the vehicle?
                                    false,         // Can this unit squash infantry?
                                    false,         // Does this unit harvest Tiberium?
                                    false,         // Is invisible to radar?
                                    false,         // Is it insignificant (won't be announced)?
                                    false,         // Is it equipped with a combat turret?
                                    false,         // Does it have a rotating radar dish?
                                    false,         // Is there an associated firing animation?
                                    false,         // Must the turret be in a locked down position while moving?
                                    false,         // Is this a gigundo-rotund-enormous unit?
                                    false,         // Does the unit have a constant animation?
                                    false,         // Is the unit capable of jamming radar?
                                    false,         // Is the unit a mobile gap generator?
                                    32,            // Rotation stages.
                                    0,             // Turret center offset along body centerline.
                                    MISSION_HUNT   // ORDERS:		Default order to give new unit.
);

// Harvester
static UnitTypeClass const UnitHarvester(UNIT_HARVESTER,
                                         TXT_HARVESTER,   // NAME:			Text name of this unit type.
                                         "HARV",          // NAME:			Text name of this unit type.
                                         ANIM_FBALL1,     // EXPLOSION:	Type of explosion when destroyed.
                                         REMAP_ALTERNATE, // Sidebar remap logic.
                                         0x0000,          //	Vertical offset.
                                         0x0000,          // Primary weapon offset along turret centerline.
                                         0x0000,          // Primary weapon lateral offset along turret centerline.
                                         0x0000,          // Secondary weapon offset along turret centerline.
                                         0x0000,          // Secondary weapon lateral offset along turret centerling.
                                         true,            // Can this be a goodie surprise from a crate?
                                         true,            // Always use the given name for the vehicle?
                                         true,            // Can this unit squash infantry?
                                         true,            // Does this unit harvest Tiberium?
                                         false,           // Is invisible to radar?
                                         false,           // Is it insignificant (won't be announced)?
                                         false,           // Is it equipped with a combat turret?
                                         false,           // Does it have a rotating radar dish?
                                         false,           // Is there an associated firing animation?
                                         false,           // Must the turret be in a locked down position while moving?
                                         true,            // Is this a gigundo-rotund-enormous unit?
                                         false,           // Does the unit have a constant animation?
                                         false,           // Is the unit capable of jamming radar?
                                         false,           // Is the unit a mobile gap generator?
                                         32,              // Rotation stages.
                                         0,               // Turret center offset along body centerline.
                                         MISSION_HARVEST  // ORDERS:		Default order to give new unit.
);

// Mobile construction vehicle
static UnitTypeClass const UnitMCV(UNIT_MCV,
                                   TXT_MCV,         // NAME:			Text name of this unit type.
                                   "MCV",           // NAME:			Text name of this unit type.
                                   ANIM_FBALL1,     // EXPLOSION:	Type of explosion when destroyed.
                                   REMAP_ALTERNATE, // Sidebar remap logic.
                                   0x0000,          //	Vertical offset.
                                   0x0000,          // Primary weapon offset along turret centerline.
                                   0x0000,          // Primary weapon lateral offset along turret centerline.
                                   0x0000,          // Secondary weapon offset along turret centerline.
                                   0x0000,          // Secondary weapon lateral offset along turret centerling.
                                   true,            // Can this be a goodie surprise from a crate?
                                   false,           // Always use the given name for the vehicle?
                                   true,            // Can this unit squash infantry?
                                   false,           // Does this unit harvest Tiberium?
                                   false,           // Is invisible to radar?
                                   false,           // Is it insignificant (won't be announced)?
                                   false,           // Is it equipped with a combat turret?
                                   false,           // Does it have a rotating radar dish?
                                   false,           // Is there an associated firing animation?
                                   false,           // Must the turret be in a locked down position while moving?
                                   true,            // Is this a gigundo-rotund-enormous unit?
                                   false,           // Does the unit have a constant animation?
                                   false,           // Is the unit capable of jamming radar?
                                   false,           // Is the unit a mobile gap generator?
                                   32,              // Rotation stages.
                                   0,               // Turret center offset along body centerline.
                                   MISSION_HUNT     // ORDERS:		Default order to give new unit.
);

// TD Harvester (UNIT_TDHARV), ported from TD's UNIT_HARVESTER with TD's art. Shared by GDI and Nod; STRUCT_TDPROC
// delivers one free.
static UnitTypeClass const UnitTdHarv(UNIT_TDHARV,
                                      TXT_HARVESTER,   // NAME:			Text name.
                                      "TDHARV",        // NAME:			IniName.
                                      ANIM_FBALL1,     // EXPLOSION:	Explosion when destroyed.
                                      REMAP_ALTERNATE, // Sidebar remap logic.
                                      0x0000,          //	Vertical offset.
                                      0x0000,          // Primary weapon offset.
                                      0x0000,          // Primary weapon lateral.
                                      0x0000,          // Secondary weapon offset.
                                      0x0000,          // Secondary weapon lateral.
                                      true,            // Can this be a goodie surprise from a crate?
                                      true,            // Always use the given name?
                                      true,            // Can this unit squash infantry?
                                      true,            // Does this unit harvest Tiberium?
                                      false,           // Is invisible to radar?
                                      false,           // Is it insignificant?
                                      false,           // Is it equipped with a combat turret?
                                      false,           // Does it have a rotating radar dish?
                                      false,           // Is there an associated firing animation?
                                      false,           // Must the turret be in a locked down position while moving?
                                      true,            // Is this a gigundo-rotund-enormous unit?
                                      false,           // Does the unit have a constant animation?
                                      false,           // Is the unit capable of jamming radar?
                                      false,           // Is the unit a mobile gap generator?
                                      32,              // Rotation stages.
                                      0,               // Turret center offset along body centerline.
                                      MISSION_HARVEST  // ORDERS:		Default order.
);

// TD MCV (UNIT_TDMCV), ported from TD's UNIT_MCV and shared by GDI and Nod; it deploys STRUCT_TDFACT. The stock
// campaigns build it, skirmish builds the faction MCVs instead.
static UnitTypeClass const UnitTdMcv(UNIT_TDMCV,
                                     TXT_MCV,         // NAME:			Text name of this unit type.
                                     "TDMCV",         // NAME:			IniName.
                                     ANIM_FBALL1,     // EXPLOSION:	Type of explosion when destroyed.
                                     REMAP_ALTERNATE, // Sidebar remap logic.
                                     0x0000,          //	Vertical offset.
                                     0x0000,          // Primary weapon offset along turret centerline.
                                     0x0000,          // Primary weapon lateral offset along turret centerline.
                                     0x0000,          // Secondary weapon offset along turret centerline.
                                     0x0000,          // Secondary weapon lateral offset along turret centerling.
                                     true,            // Can this be a goodie surprise from a crate?
                                     false,           // Always use the given name for the vehicle?
                                     true,            // Can this unit squash infantry?
                                     false,           // Does this unit harvest Tiberium?
                                     false,           // Is invisible to radar?
                                     false,           // Is it insignificant (won't be announced)?
                                     false,           // Is it equipped with a combat turret?
                                     false,           // Does it have a rotating radar dish?
                                     false,           // Is there an associated firing animation?
                                     false,           // Must the turret be in a locked down position while moving?
                                     true,            // Is this a gigundo-rotund-enormous unit?
                                     false,           // Does the unit have a constant animation?
                                     false,           // Is the unit capable of jamming radar?
                                     false,           // Is the unit a mobile gap generator?
                                     32,              // Rotation stages.
                                     0,               // Turret center offset along body centerline.
                                     MISSION_HUNT     // ORDERS:		Default order to give new unit.
);

// TD Medium Tank (UNIT_TDMTNK), ported from TD's UNIT_MTANK; GDI only. The render offsets start from RA's 2TNK; stats
// come from rules.ini [TDMTNK] and [TD105mm].
static UnitTypeClass const UnitTdMtnk(UNIT_TDMTNK,
                                      TXT_MTANK2,   // NAME: (RA "Medium Tank"; HD display via rules.ini Name=).
                                      "TDMTNK",     // NAME: IniName.
                                      ANIM_TDFRAG2, // EXPLOSION: TD vehicle frag explosion (ported TD ANIM_FRAG2 -> TDFRAG3 / FRAG3 art).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0030,       // Vertical offset (render calibration, ref 2TNK).
                                      0x00C0,       // Primary weapon offset along turret centerline (render calibration).
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset (no secondary weapon).
                                      0x0000,       // Secondary weapon lateral offset.
                                      true,         // Can this be a goodie surprise from a crate? (TD: yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (TD: yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret? (TD: yes)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      true,         // Is this a gigundo-rotund-enormous unit? (TD: yes)
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline (TD: 0).
                                      MISSION_HUNT  // ORDERS: Default order (TD MTANK default).
);

// TD Light Tank (UNIT_TDLTNK), ported from TD's UNIT_LTANK: Nod's mainline tank, smaller and cheaper than GDI's
// Medium Tank. The render offsets start from RA's 1TNK; stats come from rules.ini [TDLTNK] and [TD75mm].
static UnitTypeClass const UnitTdLtnk(UNIT_TDLTNK,
                                      TXT_LTANK,    // NAME: (RA "Light Tank"; HD display via rules.ini Name=).
                                      "TDLTNK",     // NAME: IniName.
                                      ANIM_FRAG1,   // EXPLOSION: TD LTANK death (ANIM_FRAG1 -- RA has it).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0020,       // Vertical offset (render calibration, ref RA 1TNK).
                                      0x00C0,       // Primary weapon offset along turret centerline (render calibration).
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset (no secondary weapon).
                                      0x0000,       // Secondary weapon lateral offset.
                                      true,         // Can this be a goodie surprise from a crate? (TD: yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (TD: yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret? (TD: yes)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit? (TD LTANK: no)
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline (TD: 0).
                                      MISSION_HUNT  // ORDERS: Default order (TD LTANK default).
);

// TD Mammoth Tank (UNIT_TDHTNK), ported from TD's UNIT_HTANK; GDI only. A 120mm cannon and Tusk AA missiles, both
// Burst=2 in rules.ini for TD's double shot, on RA's 4TNK barrel offsets.
static UnitTypeClass const UnitTdHtnk(UNIT_TDHTNK,
                                      TXT_HTANK,    // NAME: (RA "Mammoth Tank"; HD display via rules.ini Name=).
                                      "TDHTNK",     // NAME: IniName.
                                      ANIM_ART_EXP1,// EXPLOSION: TD HTANK death (ANIM_ART_EXP1 -- RA has it).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0020,       // Vertical offset (render calibration, ref RA 4TNK).
                                      0x00C0,       // Primary weapon offset along turret centerline.
                                      0x0028,       // Primary weapon lateral offset (left barrel).
                                      0x0008,       // Secondary weapon offset along turret centerline.
                                      0x0040,       // Secondary weapon lateral offset (right barrel / tusk pods).
                                      true,         // Can this be a goodie surprise from a crate? (TD: yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (TD: yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret? (TD: yes)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      true,         // Is this a gigundo-rotund-enormous unit? (TD HTANK: yes)
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline (TD: 0).
                                      MISSION_HUNT  // ORDERS: Default order (TD HTANK default).
);

// TD Flame Tank (UNIT_TDFTNK), ported from TD's UNIT_FTANK; Nod only. Turret-less: [TDFlameTongue] is Burst=2, and
// IsSecondShot alternates its jets between the two front nozzles.
static UnitTypeClass const UnitTdFtnk(UNIT_TDFTNK,
                                      TXT_LTANK,    // NAME: (RA has no "Flame Tank"; HD display via rules.ini Name=).
                                      "TDFTNK",     // NAME: IniName.
                                      ANIM_NAPALM3, // EXPLOSION: TD FTANK death (ANIM_NAPALM3 -- RA has it).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0000,       // Vertical offset = 0 (the jets sit at hull level, as in TD).
                                      0x0030,       // Primary weapon offset = TD FTANK 0x30, out to the front nozzles.
                                      0x0020,       // Primary lateral = TD FTANK 0x20; IsSecondShot picks the side.
                                      0x0030,       // Secondary weapon offset (unused; mirrors primary).
                                      0x0020,       // Secondary weapon lateral (unused; mirror primary).
                                      true,         // Can this be a goodie surprise from a crate? (TD: yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (TD: yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      false,        // Is it equipped with a combat turret? (TD FTANK: NO turret)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit? (TD FTANK: no)
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline (TD: 0).
                                      MISSION_HUNT  // ORDERS: Default order (TD FTANK default).
);

// TD Recon Bike (UNIT_TDBIKE), ported from TD's UNIT_BIKE; Nod only. A wheeled, turret-less scout firing [TDDragon],
// the E3's rocket, from the hull. Stats come from rules.ini [TDBIKE].
static UnitTypeClass const UnitTdBike(UNIT_TDBIKE,
                                      TXT_LTANK,    // NAME: (RA has no "Recon Bike"; HD display via rules.ini Name=).
                                      "TDBIKE",     // NAME: IniName.
                                      ANIM_FRAG1,   // EXPLOSION: TD BIKE death (ANIM_FRAG1 -- RA has it natively).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0000,       // Vertical offset = 0 (hull level).
                                      0x0000,       // Primary weapon offset (V2 Launcher precedent: rocket from hull, no turret geometry).
                                      0x0000,       // Primary weapon lateral.
                                      0x0000,       // Secondary weapon offset (unused: no Secondary weapon).
                                      0x0000,       // Secondary weapon lateral (unused).
                                      true,         // Can this be a goodie surprise from a crate? (TD BIKE: yes)
                                      false,        // Always use the given name for the vehicle?
                                      false,        // Can this unit squash infantry? (TD BIKE: NO -- a light scout bike)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      false,        // Is it equipped with a combat turret? (TD BIKE: NO turret)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit? (TD BIKE: no -- small)
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages (32 facings; TD BIKE eight-facings=false).
                                      0,            // Turret center offset along body centerline (TD: 0).
                                      MISSION_HUNT  // ORDERS: Default order (TD BIKE default).
);

// TD Hum-vee (UNIT_TDJEEP), ported from TD's UNIT_JEEP; GDI only. A wheeled scout with a small MG turret seated like
// RA's Ranger (Turret_Adjust); fires TDM60mg. Stats come from rules.ini [TDJEEP].
static UnitTypeClass const UnitTdJeep(UNIT_TDJEEP,
                                      TXT_JEEP,     // NAME: placeholder (= "Ranger"; HD display via rules.ini Name=).
                                      "TDJEEP",     // NAME: IniName.
                                      ANIM_FRAG1,   // EXPLOSION: TD JEEP death (ANIM_FRAG1 -- RA has it natively).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0030,       // Vertical offset (RA Ranger -- small MG car turret height).
                                      0x0030,       // Primary weapon offset (RA Ranger: muzzle forward on the turret).
                                      0x0000,       // Primary weapon lateral (RA Ranger: centered).
                                      0x0030,       // Secondary weapon offset (no Secondary; mirror primary).
                                      0x0000,       // Secondary weapon lateral.
                                      true,         // Can this be a goodie surprise from a crate? (TD JEEP: yes)
                                      false,        // Always use the given name for the vehicle?
                                      false,        // Can this unit squash infantry? (TD JEEP: NO -- light scout)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret? (TD JEEP: yes, MG turret)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit? (TD JEEP: no)
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages (32 facings; TD JEEP eight-facings=false).
                                      0,            // Turret center offset along body centerline (TD: 0).
                                      MISSION_HUNT  // ORDERS: Default order (TD JEEP default).
);

// TD Nod Buggy (UNIT_TDBGGY), ported from TD's UNIT_BUGGY; Nod only. It shares the Hum-vee's ctor values; its
// differences live in rules.ini [TDBGGY].
static UnitTypeClass const UnitTdBggy(UNIT_TDBGGY,
                                      TXT_JEEP,     // NAME: placeholder (HD display via rules.ini Name="Nod Buggy").
                                      "TDBGGY",     // NAME: IniName.
                                      ANIM_FRAG1,   // EXPLOSION: TD BGGY death (ANIM_FRAG1 -- RA has it natively).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0030,       // Vertical offset (RA Ranger geometry, shared with the Hum-vee).
                                      0x0030,       // Primary weapon offset.
                                      0x0000,       // Primary weapon lateral.
                                      0x0030,       // Secondary weapon offset (no Secondary; mirror primary).
                                      0x0000,       // Secondary weapon lateral.
                                      true,         // Can this be a goodie surprise from a crate? (TD BGGY: yes)
                                      false,        // Always use the given name for the vehicle?
                                      false,        // Can this unit squash infantry? (TD BGGY: NO)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret? (TD BGGY: yes, MG turret)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit? (TD BGGY: no)
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages (32 facings; TD BGGY eight-facings=false).
                                      0,            // Turret center offset along body centerline (TD: 0).
                                      MISSION_HUNT  // ORDERS: Default order (TD BGGY default).
);

// TD APC (UNIT_TDAPC), ported from TD's UNIT_APC; GDI only by rules.ini Owner=. A turret-less transport for 5 firing
// TDM60mg; it joins the UNIT_APC transport sites (docs/td-vehicle-port-recipe.md).
static UnitTypeClass const UnitTdApc(UNIT_TDAPC,
                                     TXT_APC,      // NAME: placeholder (= "APC"; HD display via rules.ini Name=).
                                     "TDAPC",      // NAME: IniName.
                                     ANIM_TDFRAG2, // EXPLOSION: TD APC death (TD ctor = ANIM_FRAG2 -> our ported ANIM_TDFRAG2).
                                     REMAP_NORMAL, // Sidebar remap logic.
                                     0x0030,       // Vertical offset.
                                     0x0030,       // Primary weapon offset along turret centerline.
                                     0x0000,       // Primary weapon lateral offset.
                                     0x0030,       // Secondary weapon offset (no Secondary; mirror primary).
                                     0x0000,       // Secondary weapon lateral offset.
                                     true,         // Can this be a goodie surprise from a crate? (TD APC: yes)
                                     false,        // Always use the given name for the vehicle?
                                     true,         // Can this unit squash infantry? (TD APC: yes)
                                     false,        // Does this unit harvest Tiberium?
                                     false,        // Is invisible to radar?
                                     false,        // Is it insignificant (won't be announced)?
                                     false,        // Is it equipped with a combat turret? (TD APC: NO turret)
                                     false,        // Does it have a rotating radar dish?
                                     false,        // Is there an associated firing animation?
                                     false,        // Must the turret be in a locked down position while moving?
                                     false,        // Is this a gigundo-rotund-enormous unit?
                                     false,        // Does the unit have a constant animation?
                                     false,        // Is the unit capable of jamming radar?
                                     false,        // Is the unit a mobile gap generator?
                                     32,           // Rotation stages (32 facings; TD APC eight-facings=false).
                                     0,            // Turret center offset along body centerline (TD: 0).
                                     MISSION_HUNT  // ORDERS: Default order (TD APC default = MISSION_HUNT).
);

// TD Stealth Tank (UNIT_TDSTNK), ported from TD's UNIT_STANK; Nod only and hidden from radar. Cloaks through rules.ini
// Cloakable=; fires TDStnkDragon, a Burst=2 copy of [TDDragon] so the E3 and Bike keep single shots.
static UnitTypeClass const UnitTdStnk(UNIT_TDSTNK,
                                      TXT_LTANK,    // NAME: placeholder (RA has no Stealth Tank string; HD display via rules.ini Name="Stealth Tank").
                                      "TDSTNK",     // NAME: IniName.
                                      ANIM_TDFRAG2, // EXPLOSION: TD STANK death (TD ctor = ANIM_FRAG2 -> our ported ANIM_TDFRAG2).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0000,       // Vertical offset (turret-less rocket -- launches from hull, like the Bike/V2 Launcher).
                                      0x0000,       // Primary weapon offset.
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset.
                                      0x0000,       // Secondary weapon lateral offset.
                                      true,         // Can this be a goodie surprise from a crate? (TD STANK: yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (TD STANK: yes)
                                      false,        // Does this unit harvest Tiberium?
                                      true,         // Is invisible to radar? (TD STANK: YES -- doesn't show on the minimap)
                                      false,        // Is it insignificant (won't be announced)?
                                      false,        // Is it equipped with a combat turret? (TD STANK: NO turret)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages (32 facings; TD STANK eight-facings=false).
                                      0,            // Turret center offset along body centerline (TD: 0).
                                      MISSION_HUNT  // ORDERS: Default order (TD STANK default = MISSION_HUNT).
);

// TD Rocket Launcher (UNIT_TDMLRS), ported from TD's UNIT_MLRS; GDI only, behind the Eye. TD draws UNIT_MLRS with the
// MSAM sprite and UNIT_MSAM with MLRS, so this unit carries the MSAM art (docs/td-mlrs-deep-dive.md).
static UnitTypeClass const UnitTdMlrs(UNIT_TDMLRS,
                                      TXT_LTANK,     // NAME: placeholder (RA has no "Rocket Launcher" string; HD display via rules.ini Name=).
                                      "TDMLRS",      // NAME: IniName (sprite bundled from the MSAM asset -- TD cross-wiring).
                                      ANIM_ART_EXP1, // EXPLOSION: TD MLRS death (ANIM_ART_EXP1 -- RA has it natively).
                                      REMAP_NORMAL,  // Sidebar remap logic.
                                      0x0010,        // Vertical offset (small lift for the rear launcher).
                                      0x0000,        // Primary weapon offset along turret centerline (rear launcher).
                                      0x0000,        // Primary weapon lateral offset.
                                      0x0000,        // Secondary weapon offset (no secondary weapon).
                                      0x0000,        // Secondary weapon lateral offset.
                                      true,          // Can this be a goodie surprise from a crate? (TD: yes)
                                      false,         // Always use the given name for the vehicle?
                                      false,         // Can this unit squash infantry? (TD MLRS: no)
                                      false,         // Does this unit harvest Tiberium?
                                      false,         // Is invisible to radar?
                                      false,         // Is it insignificant (won't be announced)?
                                      true,          // Is it equipped with a combat turret? (TD MLRS: yes)
                                      false,         // Does it have a rotating radar dish?
                                      false,         // Is there an associated firing animation?
                                      true,          // Must the turret be in a locked down position while moving? (TD MLRS: yes)
                                      false,         // Is this a gigundo-rotund-enormous unit? (TD MLRS: no)
                                      false,         // Does the unit have a constant animation?
                                      false,         // Is the unit capable of jamming radar?
                                      false,         // Is the unit a mobile gap generator?
                                      32,            // Rotation stages.
                                      0,             // Turret center offset along body centerline (TD: 0).
                                      MISSION_GUARD  // ORDERS: Default order (TD MLRS default = MISSION_GUARD).
);

// TD SSM Launcher (UNIT_TDMSAM), ported from TD's UNIT_MSAM; Nod only, behind the Temple. It carries the MLRS art
// (docs/td-mlrs-deep-dive.md) and fires TDHonestJohn, a single long-range napalm rocket.
static UnitTypeClass const UnitTdMsam(UNIT_TDMSAM,
                                      TXT_LTANK,     // NAME: placeholder (RA has no "SSM Launcher" string; HD display via rules.ini Name=).
                                      "TDMSAM",      // NAME: IniName (sprite bundled from the MLRS asset -- TD cross-wiring).
                                      ANIM_TDFRAG2,  // EXPLOSION: TD MSAM death (TD ctor = ANIM_FRAG2 -> our ported ANIM_TDFRAG2).
                                      REMAP_NORMAL,  // Sidebar remap logic.
                                      0x0010,        // Vertical offset (small lift, as the MLRS).
                                      0x0000,        // Primary weapon offset (rear launcher).
                                      0x0000,        // Primary weapon lateral offset.
                                      0x0000,        // Secondary weapon offset (no secondary weapon).
                                      0x0000,        // Secondary weapon lateral offset.
                                      true,          // Can this be a goodie surprise from a crate? (TD: yes)
                                      false,         // Always use the given name for the vehicle?
                                      false,         // Can this unit squash infantry? (TD MSAM: no)
                                      false,         // Does this unit harvest Tiberium?
                                      false,         // Is invisible to radar?
                                      false,         // Is it insignificant (won't be announced)?
                                      true,          // Is it equipped with a combat turret? (TD MSAM: yes)
                                      false,         // Does it have a rotating radar dish?
                                      false,         // Is there an associated firing animation?
                                      true,          // Must the turret be in a locked down position while moving? (TD MSAM: yes)
                                      false,         // Is this a gigundo-rotund-enormous unit? (TD MSAM: no)
                                      false,         // Does the unit have a constant animation?
                                      false,         // Is the unit capable of jamming radar?
                                      false,         // Is the unit a mobile gap generator?
                                      32,            // Rotation stages.
                                      0,             // Turret center offset along body centerline (TD: 0).
                                      MISSION_HUNT   // ORDERS: Default order (TD MSAM default = MISSION_HUNT).
);

// TD Artillery (UNIT_TDARTY), ported from TD's UNIT_ARTY; Nod only, named Nod Artillery in rules.ini. Turret-less, the
// body aims; fires TD155mm, an arcing HE shell.
static UnitTypeClass const UnitTdArty(UNIT_TDARTY,
                                      TXT_LTANK,     // NAME: placeholder (RA's "Artillery" is its own unit; HD display via rules.ini Name=).
                                      "TDARTY",      // NAME: IniName.
                                      ANIM_ART_EXP1, // EXPLOSION: TD ARTY death (ANIM_ART_EXP1 -- RA-native).
                                      REMAP_NORMAL,  // Sidebar remap logic.
                                      0x0010,        // Vertical offset (small; turret-less gun).
                                      0x0050,        // Primary weapon offset along body centerline (barrel muzzle).
                                      0x0000,        // Primary weapon lateral offset.
                                      0x0000,        // Secondary weapon offset (no secondary weapon).
                                      0x0000,        // Secondary weapon lateral offset.
                                      true,          // Can this be a goodie surprise from a crate? (TD: yes)
                                      false,         // Always use the given name for the vehicle?
                                      false,         // Can this unit squash infantry? (TD ARTY: no)
                                      false,         // Does this unit harvest Tiberium?
                                      false,         // Is invisible to radar?
                                      false,         // Is it insignificant (won't be announced)?
                                      false,         // Is it equipped with a combat turret? (TD ARTY: NO -- body aims)
                                      false,         // Does it have a rotating radar dish?
                                      false,         // Is there an associated firing animation?
                                      false,         // Must the turret be in a locked down position while moving?
                                      false,         // Is this a gigundo-rotund-enormous unit? (TD ARTY: no)
                                      false,         // Does the unit have a constant animation?
                                      false,         // Is the unit capable of jamming radar?
                                      false,         // Is the unit a mobile gap generator?
                                      32,            // Rotation stages.
                                      0,             // Turret center offset along body centerline (TD: 0).
                                      MISSION_HUNT   // ORDERS: Default order (TD ARTY default = MISSION_HUNT).
);

// TD Visceroid (UNIT_TDVICE), ported from TD's UNIT_VICE. Never built: it spawns when infantry die in Tiberium
// (infantry.cpp), heals while on Tiberium (unit.cpp) and fires [TDChemspray].
static UnitTypeClass const UnitTdVice(UNIT_TDVICE,
                                      TXT_LTANK,    // NAME: placeholder (RA has no "Visceroid"; HD display via rules.ini Name=).
                                      "TDVICE",     // NAME: IniName.
                                      ANIM_NAPALM2, // EXPLOSION: TD VICE death (ANIM_NAPALM2).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0000,       // Vertical offset (blob at hull level).
                                      0x0000,       // Primary weapon offset (sprays from body centre).
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset (no secondary).
                                      0x0000,       // Secondary weapon lateral offset.
                                      false,        // Can this be a goodie surprise from a crate? (we spawn it explicitly)
                                      true,         // Always use the given name for the vehicle? (TD VICE: yes)
                                      true,         // Can this unit squash infantry? (TD VICE: yes)
                                      false,        // Does this unit harvest Tiberium?
                                      true,         // Is invisible to radar? (TD VICE: yes)
                                      true,         // Is it insignificant (won't be announced)? (TD VICE: yes)
                                      false,        // Is it equipped with a combat turret? (TD VICE: NO)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      true,         // Does the unit have a constant animation? (TD VICE: YES -- writhing blob)
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline (TD: 0).
                                      MISSION_HUNT  // ORDERS: Default order (TD VICE default = MISSION_HUNT).
);

// Jeep (hummer)
static UnitTypeClass const UnitJeep(UNIT_JEEP,
                                    TXT_JEEP,     // NAME:			Text name of this unit type.
                                    "JEEP",       // NAME:			Text name of this unit type.
                                    ANIM_FRAG1,   // EXPLOSION:	Type of explosion when destroyed.
                                    REMAP_NORMAL, // Sidebar remap logic.
                                    0x0030,       //	Vertical offset.
                                    0x0030,       // Primary weapon offset along turret centerline.
                                    0x0000,       // Primary weapon lateral offset along turret centerline.
                                    0x0030,       // Secondary weapon offset along turret centerline.
                                    0x0000,       // Secondary weapon lateral offset along turret centerling.
                                    true,         // Can this be a goodie surprise from a crate?
                                    false,        // Always use the given name for the vehicle?
                                    false,        // Can this unit squash infantry?
                                    false,        // Does this unit harvest Tiberium?
                                    false,        // Is invisible to radar?
                                    false,        // Is it insignificant (won't be announced)?
                                    true,         // Is it equipped with a combat turret?
                                    false,        // Does it have a rotating radar dish?
                                    false,        // Is there an associated firing animation?
                                    false,        // Must the turret be in a locked down position while moving?
                                    false,        // Is this a gigundo-rotund-enormous unit?
                                    false,        // Does the unit have a constant animation?
                                    false,        // Is the unit capable of jamming radar?
                                    false,        // Is the unit a mobile gap generator?
                                    32,           // Rotation stages.
                                    0,            // Turret center offset along body centerline.
                                    MISSION_HUNT  // ORDERS:		Default order to give new unit.
);

// Armored personnel carrier
static UnitTypeClass const UnitAPC(UNIT_APC,
                                   TXT_APC,      // NAME:			Text name of this unit type.
                                   "APC",        // NAME:			Text name of this unit type.
                                   ANIM_FRAG1,   // EXPLOSION:	Type of explosion when destroyed.
                                   REMAP_NORMAL, // Sidebar remap logic.
                                   0x0030,       //	Vertical offset.
                                   0x0030,       // Primary weapon offset along turret centerline.
                                   0x0000,       // Primary weapon lateral offset along turret centerline.
                                   0x0030,       // Secondary weapon offset along turret centerline.
                                   0x0000,       // Secondary weapon lateral offset along turret centerling.
                                   true,         // Can this be a goodie surprise from a crate?
                                   false,        // Always use the given name for the vehicle?
                                   true,         // Can this unit squash infantry?
                                   false,        // Does this unit harvest Tiberium?
                                   false,        // Is invisible to radar?
                                   false,        // Is it insignificant (won't be announced)?
                                   false,        // Is it equipped with a combat turret?
                                   false,        // Does it have a rotating radar dish?
                                   false,        // Is there an associated firing animation?
                                   false,        // Must the turret be in a locked down position while moving?
                                   false,        // Is this a gigundo-rotund-enormous unit?
                                   false,        // Does the unit have a constant animation?
                                   false,        // Is the unit capable of jamming radar?
                                   false,        // Is the unit a mobile gap generator?
                                   32,           // Rotation stages.
                                   0,            // Turret center offset along body centerline.
                                   MISSION_HUNT  // ORDERS:		Default order to give new unit.
);

// Mine laying truck
static UnitTypeClass const UnitMineLayer(UNIT_MINELAYER,
                                         TXT_MINE_LAYER, // NAME:			Text name of this unit type.
                                         "MNLY",         // NAME:			Text name of this unit type.
                                         ANIM_FRAG1,     // EXPLOSION:	Type of explosion when destroyed.
                                         REMAP_NORMAL,   // Sidebar remap logic.
                                         0x0000,         //	Vertical offset.
                                         0x0000,         // Primary weapon offset along turret centerline.
                                         0x0000,         // Primary weapon lateral offset along turret centerline.
                                         0x0000,         // Secondary weapon offset along turret centerline.
                                         0x0000,         // Secondary weapon lateral offset along turret centerling.
                                         true,           // Can this be a goodie surprise from a crate?
                                         false,          // Always use the given name for the vehicle?
                                         true,           // Can this unit squash infantry?
                                         false,          // Does this unit harvest Tiberium?
                                         false,          // Is invisible to radar?
                                         false,          // Is it insignificant (won't be announced)?
                                         false,          // Is it equipped with a combat turret?
                                         false,          // Does it have a rotating radar dish?
                                         false,          // Is there an associated firing animation?
                                         false,          // Must the turret be in a locked down position while moving?
                                         false,          // Is this a gigundo-rotund-enormous unit?
                                         false,          // Does the unit have a constant animation?
                                         false,          // Is the unit capable of jamming radar?
                                         false,          // Is the unit a mobile gap generator?
                                         32,             // Rotation stages.
                                         0,              // Turret center offset along body centerline.
                                         MISSION_HUNT    // ORDERS:		Default order to give new unit.
);

// Convoy Truck
static UnitTypeClass const UnitConvoyTruck(UNIT_TRUCK,
                                           TXT_TRUCK,    // NAME:			Text name of this unit type.
                                           "TRUK",       // NAME:			Text name of this unit type.
                                           ANIM_FRAG1,   // EXPLOSION:	Type of explosion when destroyed.
                                           REMAP_NORMAL, // Sidebar remap logic.
                                           0x0000,       //	Vertical offset.
                                           0x0000,       // Primary weapon offset along turret centerline.
                                           0x0000,       // Primary weapon lateral offset along turret centerline.
                                           0x0000,       // Secondary weapon offset along turret centerline.
                                           0x0000,       // Secondary weapon lateral offset along turret centerling.
                                           false,        // Can this be a goodie surprise from a crate?
                                           false,        // Always use the given name for the vehicle?
                                           false,        // Can this unit squash infantry?
                                           false,        // Does this unit harvest Tiberium?
                                           false,        // Is invisible to radar?
                                           false,        // Is it insignificant (won't be announced)?
                                           false,        // Is it equipped with a combat turret?
                                           false,        // Does it have a rotating radar dish?
                                           false,        // Is there an associated firing animation?
                                           false,        // Must the turret be in a locked down position while moving?
                                           false,        // Is this a gigundo-rotund-enormous unit?
                                           false,        // Does the unit have a constant animation?
                                           false,        // Is the unit capable of jamming radar?
                                           false,        // Is the unit a mobile gap generator?
                                           32,           // Rotation stages.
                                           0,            // Turret center offset along body centerline.
                                           MISSION_GUARD // ORDERS:		Default order to give new unit.
);

#ifdef FIXIT_ANTS
/*
[ANT]
Name=Warrior Ant
Primary=Mandible
Strength=150
Armor=light
TechLevel=-1
Sight=2
Speed=5
Cost=700
Points=40
ROT=5
Tracked=yes
Crewed=no
NoMovingFire=yes

; Ant mandible
[Mandible]
Damage=50
ROF=5
Range=1.5
Projectile=Invisible
Speed=100
Warhead=HollowPoint
Report=none


*/

// Warrior ant
static UnitTypeClass const UnitAnt1(UNIT_ANT1,
                                    TXT_NONE,        // NAME:			Text name of this unit type.
                                    "ANT1",          // NAME:			Text name of this unit type.
                                    ANIM_ANT1_DEATH, // EXPLOSION:	Type of explosion when destroyed.
                                    REMAP_NORMAL,    // Sidebar remap logic.
                                    0x0000,          //	Vertical offset.
                                    0x0000,          // Primary weapon offset along turret centerline.
                                    0x0000,          // Primary weapon lateral offset along turret centerline.
                                    0x0000,          // Secondary weapon offset along turret centerline.
                                    0x0000,          // Secondary weapon lateral offset along turret centerling.
                                    false,           // Can this be a goodie surprise from a crate?
                                    true,            // Always use the given name for the vehicle?
                                    false,           // Can this unit squash infantry?
                                    false,           // Does this unit harvest Tiberium?
                                    false,           // Is invisible to radar?
                                    true,            // Is it insignificant (won't be announced)?
                                    false,           // Is it equipped with a combat turret?
                                    false,           // Does it have a rotating radar dish?
                                    false,           // Is there an associated firing animation?
                                    false,           // Must the turret be in a locked down position while moving?
                                    true,            // Is this a gigundo-rotund-enormous unit?
                                    false,           // Does the unit have a constant animation?
                                    false,           // Is the unit capable of jamming radar?
                                    false,           // Is the unit a mobile gap generator?
                                    8,               // Rotation stages.
                                    0,               // Turret center offset along body centerline.
                                    MISSION_HUNT     // ORDERS:		Default order to give new unit.
);
static UnitTypeClass const UnitAnt2(UNIT_ANT2,
                                    TXT_NONE,        // NAME:			Text name of this unit type.
                                    "ANT2",          // NAME:			Text name of this unit type.
                                    ANIM_ANT2_DEATH, // EXPLOSION:	Type of explosion when destroyed.
                                    REMAP_NORMAL,    // Sidebar remap logic.
                                    0x0000,          //	Vertical offset.
                                    0x0000,          // Primary weapon offset along turret centerline.
                                    0x0000,          // Primary weapon lateral offset along turret centerline.
                                    0x0000,          // Secondary weapon offset along turret centerline.
                                    0x0000,          // Secondary weapon lateral offset along turret centerling.
                                    false,           // Can this be a goodie surprise from a crate?
                                    true,            // Always use the given name for the vehicle?
                                    false,           // Can this unit squash infantry?
                                    false,           // Does this unit harvest Tiberium?
                                    false,           // Is invisible to radar?
                                    true,            // Is it insignificant (won't be announced)?
                                    false,           // Is it equipped with a combat turret?
                                    false,           // Does it have a rotating radar dish?
                                    false,           // Is there an associated firing animation?
                                    false,           // Must the turret be in a locked down position while moving?
                                    true,            // Is this a gigundo-rotund-enormous unit?
                                    false,           // Does the unit have a constant animation?
                                    false,           // Is the unit capable of jamming radar?
                                    false,           // Is the unit a mobile gap generator?
                                    8,               // Rotation stages.
                                    0,               // Turret center offset along body centerline.
                                    MISSION_HUNT     // ORDERS:		Default order to give new unit.
);
static UnitTypeClass const UnitAnt3(UNIT_ANT3,
                                    TXT_NONE,        // NAME:			Text name of this unit type.
                                    "ANT3",          // NAME:			Text name of this unit type.
                                    ANIM_ANT3_DEATH, // EXPLOSION:	Type of explosion when destroyed.
                                    REMAP_NORMAL,    // Sidebar remap logic.
                                    0x0000,          //	Vertical offset.
                                    0x0000,          // Primary weapon offset along turret centerline.
                                    0x0000,          // Primary weapon lateral offset along turret centerline.
                                    0x0000,          // Secondary weapon offset along turret centerline.
                                    0x0000,          // Secondary weapon lateral offset along turret centerling.
                                    false,           // Can this be a goodie surprise from a crate?
                                    true,            // Always use the given name for the vehicle?
                                    false,           // Can this unit squash infantry?
                                    false,           // Does this unit harvest Tiberium?
                                    false,           // Is invisible to radar?
                                    true,            // Is it insignificant (won't be announced)?
                                    false,           // Is it equipped with a combat turret?
                                    false,           // Does it have a rotating radar dish?
                                    false,           // Is there an associated firing animation?
                                    false,           // Must the turret be in a locked down position while moving?
                                    true,            // Is this a gigundo-rotund-enormous unit?
                                    false,           // Does the unit have a constant animation?
                                    false,           // Is the unit capable of jamming radar?
                                    false,           // Is the unit a mobile gap generator?
                                    8,               // Rotation stages.
                                    0,               // Turret center offset along body centerline.
                                    MISSION_HUNT     // ORDERS:		Default order to give new unit.
);
#endif

#ifdef FIXIT_CSII //	checked - ajw 9/28/98
// Chrono Tank
static UnitTypeClass const UnitChrono(UNIT_CHRONOTANK,
                                      TXT_CHRONOTANK, // NAME:			Text name of this unit type.
                                      "CTNK",         // NAME:			Text name of this unit type.
                                      ANIM_FRAG1,     // EXPLOSION:	Type of explosion when destroyed.
                                      REMAP_NORMAL,   // Sidebar remap logic.
                                      0x0000,         //	Vertical offset.
                                      0x0000,         // Primary weapon offset along turret centerline.
                                      0x0000,         // Primary weapon lateral offset along turret centerline.
                                      0x0000,         // Secondary weapon offset along turret centerline.
                                      0x0000,         // Secondary weapon lateral offset along turret centerling.
                                      false,          // Can this be a goodie surprise from a crate?
                                      false,          // Always use the given name for the vehicle?
                                      true,           // Can this unit squash infantry?
                                      false,          // Does this unit harvest Tiberium?
                                      false,          // Is invisible to radar?
                                      false,          // Is it insignificant (won't be announced)?
                                      false,          // Is it equipped with a combat turret?
                                      false,          // Does it have a rotating radar dish?
                                      false,          // Is there an associated firing animation?
                                      false,          // Must the turret be in a locked down position while moving?
                                      true,           // Is this a gigundo-rotund-enormous unit?
                                      false,          // Does the unit have a constant animation?
                                      false,          // Is the unit capable of jamming radar?
                                      false,          // Is the unit a mobile gap generator?
                                      32,             // Rotation stages.
                                      0,              // Turret center offset along body centerline.
                                      MISSION_HUNT    // ORDERS:		Default order to give new unit.
);

// Tesla Tank
static UnitTypeClass const UnitTesla(UNIT_TESLATANK,
                                     TXT_TESLATANK, // NAME:			Text name of this unit type.
                                     "TTNK",        // NAME:			Text name of this unit type.
                                     ANIM_FRAG1,    // EXPLOSION:	Type of explosion when destroyed.
                                     REMAP_NORMAL,  // Sidebar remap logic.
                                     0x0000,        //	Vertical offset.
                                     0x0000,        // Primary weapon offset along turret centerline.
                                     0x0000,        // Primary weapon lateral offset along turret centerline.
                                     0x0000,        // Secondary weapon offset along turret centerline.
                                     0x0000,        // Secondary weapon lateral offset along turret centerling.
                                     false,         // Can this be a goodie surprise from a crate?
                                     false,         // Always use the given name for the vehicle?
                                     true,          // Can this unit squash infantry?
                                     false,         // Does this unit harvest Tiberium?
                                     true,          // Is invisible to radar?
                                     false,         // Is it insignificant (won't be announced)?
                                     false,         // Is it equipped with a combat turret?
                                     true,          // Does it have a rotating radar dish?
                                     false,         // Is there an associated firing animation?
                                     false,         // Must the turret be in a locked down position while moving?
                                     true,          // Is this a gigundo-rotund-enormous unit?
                                     false,         // Does the unit have a constant animation?
                                     true,          // Is the unit capable of jamming radar?
                                     false,         // Is the unit a mobile gap generator?
                                     32,            // Rotation stages.
                                     0,             // Turret center offset along body centerline.
                                     MISSION_HUNT   // ORDERS:		Default order to give new unit.
);

// M.A.D. Tank
static UnitTypeClass const UnitMAD(UNIT_MAD,
                                   TXT_MAD,      // NAME:			Text name of this unit type.
                                   "QTNK",       // NAME:			Text name of this unit type.
                                   ANIM_FRAG1,   // EXPLOSION:	Type of explosion when destroyed.
                                   REMAP_NORMAL, // Sidebar remap logic.
                                   0x0000,       //	Vertical offset.
                                   0x0000,       // Primary weapon offset along turret centerline.
                                   0x0000,       // Primary weapon lateral offset along turret centerline.
                                   0x0000,       // Secondary weapon offset along turret centerline.
                                   0x0000,       // Secondary weapon lateral offset along turret centerling.
                                   false,        // Can this be a goodie surprise from a crate?
                                   false,        // Always use the given name for the vehicle?
                                   true,         // Can this unit squash infantry?
                                   false,        // Does this unit harvest Tiberium?
                                   false,        // Is invisible to radar?
                                   false,        // Is it insignificant (won't be announced)?
                                   false,        // Is it equipped with a combat turret?
                                   false,        // Does it have a rotating radar dish?
                                   false,        // Is there an associated firing animation?
                                   false,        // Must the turret be in a locked down position while moving?
                                   true,         // Is this a gigundo-rotund-enormous unit?
                                   false,        // Does the unit have a constant animation?
                                   false,        // Is the unit capable of jamming radar?
                                   false,        // Is the unit a mobile gap generator?
                                   32,           // Rotation stages.
                                   0,            // Turret center offset along body centerline.
                                   MISSION_HUNT  // ORDERS:		Default order to give new unit.
);

// Demolition Truck
static UnitTypeClass const UnitDemoTruck(UNIT_DEMOTRUCK,
                                         TXT_DEMOTRUCK, // NAME:			Text name of this unit type.
                                         "DTRK",        // NAME:			Text name of this unit type.
                                         ANIM_FRAG1,    // EXPLOSION:	Type of explosion when destroyed.
                                         REMAP_NORMAL,  // Sidebar remap logic.
                                         0x0000,        //	Vertical offset.
                                         0x0000,        // Primary weapon offset along turret centerline.
                                         0x0000,        // Primary weapon lateral offset along turret centerline.
                                         0x0000,        // Secondary weapon offset along turret centerline.
                                         0x0000,        // Secondary weapon lateral offset along turret centerling.
                                         false,         // Can this be a goodie surprise from a crate?
                                         false,         // Always use the given name for the vehicle?
                                         false,         // Can this unit squash infantry?
                                         false,         // Does this unit harvest Tiberium?
                                         false,         // Is invisible to radar?
                                         false,         // Is it insignificant (won't be announced)?
                                         false,         // Is it equipped with a combat turret?
                                         false,         // Does it have a rotating radar dish?
                                         false,         // Is there an associated firing animation?
                                         false,         // Must the turret be in a locked down position while moving?
                                         false,         // Is this a gigundo-rotund-enormous unit?
                                         false,         // Does the unit have a constant animation?
                                         false,         // Is the unit capable of jamming radar?
                                         false,         // Is the unit a mobile gap generator?
                                         32,            // Rotation stages.
                                         0,             // Turret center offset along body centerline.
                                         MISSION_GUARD  // ORDERS:		Default order to give new unit.
);
#ifdef FIXIT_PHASETRANSPORT //	checked - ajw 9/28/98
static UnitTypeClass const UnitPhase(UNIT_PHASE,
                                     TXT_PHASETRANSPORT, // NAME:			Text name of this unit type.
                                     "STNK",             // NAME:			Text name of this unit type.
                                     ANIM_FRAG1,         // EXPLOSION:	Type of explosion when destroyed.
                                     REMAP_NORMAL,       // Sidebar remap logic.
                                     0x0030,             //	Vertical offset.
                                     0x0030,             // Primary weapon offset along turret centerline.
                                     0x0000,             // Primary weapon lateral offset along turret centerline.
                                     0x0030,             // Secondary weapon offset along turret centerline.
                                     0x0000,             // Secondary weapon lateral offset along turret centerling.
                                     false,              // Can this be a goodie surprise from a crate?
                                     false,              // Always use the given name for the vehicle?
                                     true,               // Can this unit squash infantry?
                                     false,              // Does this unit harvest Tiberium?
                                     false,              // Is invisible to radar?
                                     false,              // Is it insignificant (won't be announced)?
                                     true,               // Is it equipped with a combat turret?
                                     false,              // Does it have a rotating radar dish?
                                     false,              // Is there an associated firing animation?
                                     false,              // Must the turret be in a locked down position while moving?
                                     true,               //		false,				// Is this a gigundo-rotund-enormous unit?
                                     false,              // Does the unit have a constant animation?
                                     false,              // Is the unit capable of jamming radar?
                                     false,              // Is the unit a mobile gap generator?
                                     32,                 // Rotation stages.
                                     0,                  // Turret center offset along body centerline.
                                     MISSION_HUNT        // ORDERS:		Default order to give new unit.
);

#endif
#endif

/***********************************************************************************************
 * UnitTypeClass::UnitTypeClass -- Constructor for unit types.                                 *
 *                                                                                             *
 *    This is the constructor for the unit types. It is used to initialize the unit type class *
 *    structure. The unit type class is used to control the behavior of the various types      *
 *    of units in the game. This constructor is called for every unique unit type as it        *
 *    exists in the array of unit types.                                                       *
 *                                                                                             *
 * INPUT:   bla bla bla... see below                                                           *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/20/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
UnitTypeClass::UnitTypeClass(UnitType type,
                             int name,
                             char const* ininame,
                             AnimType exp,
                             RemapType remap,
                             int verticaloffset,
                             int primaryoffset,
                             int primarylateral,
                             int secondaryoffset,
                             int secondarylateral,
                             bool is_goodie,
                             bool is_nominal,
                             bool is_crusher,
                             bool is_harvest,
                             bool is_stealthy,
                             bool is_insignificant,
                             bool is_turret_equipped,
                             bool is_radar_equipped,
                             bool is_fire_anim,
                             bool is_lock_turret,
                             bool is_gigundo,
                             bool is_animating,
                             bool is_jammer,
                             bool is_gapper,
                             int rotation,
                             int toffset,
                             MissionType order)
    : TechnoTypeClass(RTTI_UNITTYPE,
                      int(type),
                      name,
                      ininame,
                      remap,
                      verticaloffset,
                      primaryoffset,
                      primarylateral,
                      secondaryoffset,
                      secondarylateral,
                      is_nominal,
                      is_stealthy,
                      true,
                      true,
                      is_insignificant,
                      false,
                      false,
                      is_turret_equipped,
                      true,
                      true,
                      rotation,
                      SPEED_TRACK)
    , IsCrateGoodie(is_goodie)
    , IsCrusher(is_crusher)
    , IsToHarvest(is_harvest)
    , IsRadarEquipped(is_radar_equipped)
    , IsFireAnim(is_fire_anim)
    , IsLockTurret(is_lock_turret)
    , IsGigundo(is_gigundo)
    , IsAnimating(is_animating)
    , IsJammer(is_jammer)
    , IsGapper(is_gapper)
    , IsNoFireWhileMoving(false)
    , Type(type)
    , TurretOffset(toffset)
    , Mission(order)
    , Explosion(exp)
    , MaxSize(0)
{
    /*
    **	Forced unit overrides form the default.
    */
    Speed = SPEED_WHEEL;
}

/***********************************************************************************************
 * UnitTypeClass::operator new -- Allocates an object from the unit type class heap.           *
 *                                                                                             *
 *    Use this routine to allocate a unit type class object from the special heap that is      *
 *    maintained for this purpose.                                                             *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the newly allocated unit type class object. If there is  *
 *          no more room to allocate another unit type class object, then NULL will be         *
 *          returned.                                                                          *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void* UnitTypeClass::operator new(size_t) noexcept
{
    return (UnitTypes.Alloc());
}

/***********************************************************************************************
 * UnitTypeClass::operator delete -- Return a unit type class object back to the pool.         *
 *                                                                                             *
 *    This will return a previously allocated unit to the memory pool from whence it came.     *
 *                                                                                             *
 * INPUT:   pointer  -- A Pointer to the unit type class object to return to the memory pool.  *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void UnitTypeClass::operator delete(void* pointer)
{
    UnitTypes.Free((UnitTypeClass*)pointer);
}

// Builds a [NewUnits] entry in the heap slot operator new has just appended (Count() - 1); Read_INI's Logic= then
// makes it act as a vanilla unit type.
UnitTypeClass::UnitTypeClass(int /*utype*/, char const* ininame)
    : UnitTypeClass(static_cast<UnitType>(UnitTypes.Count() - 1),
                    TXT_NONE,
                    ininame,
                    ANIM_FBALL1,    // EXPLOSION:	donor will override
                    REMAP_NORMAL,   // Sidebar remap logic.
                    0x0000,         // Vertical offset.
                    0x0000,         // Primary weapon offset.
                    0x0000,         // Primary weapon lateral offset.
                    0x0000,         // Secondary weapon offset.
                    0x0000,         // Secondary weapon lateral offset.
                    false,          // IsGoodie (crate drop)
                    false,          // IsNominal
                    false,          // IsCrusher
                    false,          // IsToHarvest
                    false,          // IsStealthy
                    false,          // IsInsignificant
                    false,          // IsTurretEquipped
                    false,          // IsRadarEquipped
                    false,          // IsFireAnim
                    false,          // IsLockTurret
                    false,          // IsGigundo
                    false,          // IsAnimating
                    false,          // IsJammer
                    false,          // IsGapper
                    32,             // Rotation stages.
                    0,              // TurretOffset
                    MISSION_GUARD)  // Default order
{
}

// Finds a unit type by IniName across the whole heap, [NewUnits] entries included; From_Name stops at UNIT_COUNT.
UnitTypeClass* UnitTypeClass::As_Pointer(char const* name)
{
    if (name == NULL) {
        return NULL;
    }
    for (int index = 0; index < UnitTypes.Count(); index++) {
        UnitTypeClass* utc = UnitTypes.Ptr(index);
        if (utc != NULL && stricmp(utc->IniName, name) == 0) {
            return utc;
        }
    }
    return NULL;
}

// TS Hover MLRS (UNIT_TSHVR), TS rules [HVR]: a hover tank firing TSHoverMissile from a rocket rack that
// Hover_Rack_Seat seats on the pad on its back.
static UnitTypeClass const UnitTsHvr(UNIT_TSHVR,
                                     TXT_LTANK,    // NAME: placeholder (RA has no Hover MLRS string; HD display via rules.ini Name=).
                                     "TSHVR",      // NAME: IniName.
                                     ANIM_FRAG1,   // EXPLOSION: light-vehicle frag (RA-native).
                                     REMAP_NORMAL, // Sidebar remap logic.
                                     0x0030,       // Vertical offset (render calibration, ref 2TNK).
                                     0x0040,       // Primary weapon offset: small forward nudge from the rack (Fire_Coord shifts to the aft rack first).
                                     0x0000,       // Primary weapon lateral offset.
                                     0x0000,       // Secondary weapon offset (no secondary).
                                     0x0000,       // Secondary weapon lateral offset.
                                     true,         // Can this be a goodie surprise from a crate? (TS CrateGoodie=yes)
                                     false,        // Always use the given name for the vehicle?
                                     false,        // Can this unit squash infantry? (TS Crusher=no)
                                     false,        // Does this unit harvest Tiberium?
                                     false,        // Is invisible to radar?
                                     false,        // Is it insignificant (won't be announced)?
                                     true,         // Is it equipped with a combat turret? (TS Turret=yes)
                                     false,        // Does it have a rotating radar dish?
                                     false,        // Is there an associated firing animation?
                                     false,        // Must the turret be in a locked down position while moving?
                                     false,        // Is this a gigundo-rotund-enormous unit?
                                     false,        // Does the unit have a constant animation?
                                     false,        // Is the unit capable of jamming radar?
                                     false,        // Is the unit a mobile gap generator?
                                     32,           // Rotation stages.
                                     0,            // Turret center offset along body centerline.
                                     MISSION_HUNT  // ORDERS: Default order.
);

// TS Titan walker (UNIT_TSTITN), TS rules [MMCH], firing TS120mm. The turret mount is baked into the packed frames
// (scripts/ts_pack_walkers.py), so the turret draws centred with no Turret_Adjust seat.
static UnitTypeClass const UnitTsTitn(UNIT_TSTITN,
                                      TXT_LTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                      "TSTITN",     // NAME: IniName.
                                      ANIM_FBALL1,  // EXPLOSION: big fireball (TS TWLT070-scale death).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0030,       // Vertical offset (render calibration, ref 2TNK).
                                      0x00A8,       // Primary weapon offset: the cannon muzzle (~0.66 cell forward, measured from the packed art).
                                      0x0018,       // Primary weapon lateral offset: cannon rides the right flank (18 HD px).
                                      0x0000,       // Secondary weapon offset (no secondary).
                                      0x0000,       // Secondary weapon lateral offset.
                                      true,         // Can this be a goodie surprise from a crate? (TS CrateGoodie=yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (TS Crusher=yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret? (TS Turret=yes)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline (mount baked into the art).
                                      MISSION_HUNT  // ORDERS: Default order.
);

// TS Juggernaut (UNIT_TSJUGG), Firestorm rules [JUGG]: a walker that sets down to fire
// (DeployToFire) three arcing 90mm shells at long range. Art = the HD rebuild: the walk
// (8 facings x 15) + the deployed piece in 32 facings, at rest and aiming, its barrels
// drawn in + the deploy ladder (scripts/ts_pack_hd_buildings.py).
// The turret is baked into the deployed frames, so IsTurretEquipped only drives the
// turret facing; UnitClass::Draw_It skips the turret draw for DeployToFire units.
static UnitTypeClass const UnitTsJugg(UNIT_TSJUGG,
                                      TXT_LTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                      "TSJUGG",     // NAME: IniName.
                                      ANIM_FBALL1,  // EXPLOSION: big fireball (TS TWLT070-scale death).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0030,       // Vertical offset.
                                      0x0000,       // Primary weapon offset (the shells leave the deployed turret centre).
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset (no secondary).
                                      0x0000,       // Secondary weapon lateral offset.
                                      true,         // Can this be a goodie surprise from a crate? (TS CrateGoodie=yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (TS Crusher=yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret? (the deployed turret turns)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline (baked into the art).
                                      MISSION_HUNT  // ORDERS: Default order.
);

// TS Limpet Drone (UNIT_TSLIMP), Firestorm rules [LIMPET]. Unarmed hover crawler
// that deploys (unit.cpp Try_To_Deploy) into the cloaked STRUCT_TSDLIMP mine on
// its own cell. Art = the HD rebuild of LIMPED.SHP, a ten-frame blink drawn by Shape_Number
// with no facings (scripts/ts_pack_hd_buildings.py). Classic = transparent 24x24 stub.
static UnitTypeClass const UnitTsLimp(UNIT_TSLIMP,
                                      TXT_LTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                      "TSLIMP",     // NAME: IniName.
                                      ANIM_FRAG1,   // EXPLOSION: light-vehicle frag.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0000,       // Vertical offset.
                                      0x0000,       // Primary weapon offset (unarmed).
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset (no secondary).
                                      0x0000,       // Secondary weapon lateral offset.
                                      false,        // Can this be a goodie surprise from a crate? (TS CrateGoodie=no)
                                      false,        // Always use the given name for the vehicle?
                                      false,        // Can this unit squash infantry? (TS Crusher=no)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      false,        // Is it equipped with a combat turret?
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages (the art has none; the locomotor still turns).
                                      0,            // Turret center offset along body centerline.
                                      MISSION_GUARD // ORDERS: Default order.
);

// TS Mammoth Mk. II walker (UNIT_TSHMEC), TS rules [HMEC]: hull-fixed twin railguns, so the walker turns to fire,
// and TSMammothTusk AA missiles.
static UnitTypeClass const UnitTsHmec(UNIT_TSHMEC,
                                      TXT_HTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                      "TSHMEC",     // NAME: IniName.
                                      ANIM_FBALL1,  // EXPLOSION: big fireball.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0030,       // Vertical offset (render calibration).
                                      0x00C0,       // Primary weapon offset: railgun muzzles forward of the hull.
                                      0x0028,       // Primary weapon lateral offset (twin barrels, 4TNK convention).
                                      0x0008,       // Secondary weapon offset (missile pods, aft).
                                      0x0040,       // Secondary weapon lateral offset.
                                      true,         // Can this be a goodie surprise from a crate?
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (TS Crusher=yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      false,        // Is it equipped with a combat turret? (hull-fixed guns)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      true,         // Turret lock: FIRE_FACING turns the body to aim hull-fixed guns.
                                      true,         // Is this a gigundo-rotund-enormous unit? (4TNK-class hulk)
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline.
                                      MISSION_HUNT  // ORDERS: Default order.
);

// TS Harvester (UNIT_TSHARV), TS rules [HARV], with RA harvester mechanics. Its voxel art has no load or dump frames,
// so the draw path skips both.
static UnitTypeClass const UnitTsHarv(UNIT_TSHARV,
                                      TXT_HARVESTER, // NAME: placeholder (HD display via rules.ini Name=).
                                      "TSHARV",      // NAME: IniName.
                                      ANIM_FBALL1,   // EXPLOSION: big fireball (TS TWLT070-scale death).
                                      REMAP_NORMAL,  // Sidebar remap logic.
                                      0x0000,        // Vertical offset.
                                      0x0000,        // Primary weapon offset (unarmed).
                                      0x0000,        // Primary weapon lateral offset.
                                      0x0000,        // Secondary weapon offset.
                                      0x0000,        // Secondary weapon lateral offset.
                                      true,          // Can this be a goodie surprise from a crate? (TS CrateGoodie=yes)
                                      true,          // Always use the given name for the vehicle?
                                      true,          // Can this unit squash infantry? (TS Crusher=yes)
                                      true,          // Does this unit harvest Tiberium?
                                      false,         // Is invisible to radar?
                                      false,         // Is it insignificant (won't be announced)?
                                      false,         // Is it equipped with a combat turret?
                                      false,         // Does it have a rotating radar dish?
                                      false,         // Is there an associated firing animation?
                                      false,         // Must the turret be in a locked down position while moving?
                                      true,          // Is this a gigundo-rotund-enormous unit?
                                      false,         // Does the unit have a constant animation?
                                      false,         // Is the unit capable of jamming radar?
                                      false,         // Is the unit a mobile gap generator?
                                      32,            // Rotation stages.
                                      0,             // Turret center offset along body centerline.
                                      MISSION_HARVEST // ORDERS: Default order.
);

// TS Wolverine (UNIT_TSSMEC), TS rules [SMECH]: a light walker whose hull-fixed guns are drawn in its walk frames;
// fires AssaultCannon, an instant hit.
static UnitTypeClass const UnitTsSmec(UNIT_TSSMEC,
                                      TXT_LTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                      "TSSMEC",     // NAME: IniName.
                                      ANIM_FRAG1,   // EXPLOSION: light-vehicle fragment burst.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0030,       // Vertical offset (render calibration, walker convention).
                                      0x0060,       // Primary weapon offset: arm guns forward of the hull.
                                      0x0010,       // Primary weapon lateral offset (right arm leads the burst).
                                      0x0000,       // Secondary weapon offset (no secondary).
                                      0x0000,       // Secondary weapon lateral offset.
                                      true,         // Can this be a goodie surprise from a crate? (TS CrateGoodie=yes)
                                      false,        // Always use the given name for the vehicle?
                                      false,        // Can this unit squash infantry? (TS Crusher unset — too light)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      false,        // Is it equipped with a combat turret? (TS Turret=no)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      true,         // Must the turret be in a locked down position while moving? (hull-fixed guns: FIRE_FACING turns the body — the TSHMEC convention)
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline.
                                      MISSION_HUNT  // ORDERS: Default order.
);

// TS Disruptor (UNIT_TSSONIC), TS rules [SONIC]: a sonic tank whose turret sits aft of the hull centre
// (Sonic_Turret_Seat). It fires SonicZap, the IsSonic piercing line.
static UnitTypeClass const UnitTsSonic(UNIT_TSSONIC,
                                       TXT_HTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                       "TSSONIC",    // NAME: IniName.
                                       ANIM_FBALL1,  // EXPLOSION: big fireball.
                                       REMAP_NORMAL, // Sidebar remap logic.
                                       0x0030,       // Vertical offset (Fire_Coord ignores it for this unit).
                                       0x0050,       // Primary weapon offset (Fire_Coord ignores it for this unit).
                                       0x0000,       // Primary weapon lateral offset (centerline emitter).
                                       0x0000,       // Secondary weapon offset (no secondary).
                                       0x0000,       // Secondary weapon lateral offset.
                                       true,         // Can this be a goodie surprise from a crate? (TS CrateGoodie=yes)
                                       false,        // Always use the given name for the vehicle?
                                       true,         // Can this unit squash infantry? (TS Crusher=yes)
                                       false,        // Does this unit harvest Tiberium?
                                       false,        // Is invisible to radar?
                                       false,        // Is it insignificant (won't be announced)?
                                       true,         // Is it equipped with a combat turret? (TS Turret=yes)
                                       false,        // Does it have a rotating radar dish?
                                       false,        // Is there an associated firing animation?
                                       false,        // Must the turret be in a locked down position while moving?
                                       false,        // Is this a gigundo-rotund-enormous unit?
                                       false,        // Does the unit have a constant animation?
                                       false,        // Is the unit capable of jamming radar?
                                       false,        // Is the unit a mobile gap generator?
                                       32,           // Rotation stages.
                                       0,            // Turret center offset (unused; see Sonic_Turret_Seat).
                                       MISSION_HUNT  // ORDERS: Default order.
);

// TS Mammoth Tank (UNIT_TS4TNK), TS rules [4TNK], shown as Mammoth Mk. I: twin 120mm cannon and TS4TNKTusk AA
// missiles. TS art gives no TurretOffset, so hull and turret share the voxel origin.
static UnitTypeClass const UnitTs4tnk(UNIT_TS4TNK,
                                      TXT_HTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                      "TS4TNK",     // NAME: IniName.
                                      ANIM_ART_EXP1,// EXPLOSION: big fragment explosion.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0020,       // Vertical offset.
                                      0x00C0,       // Primary weapon offset along turret centerline.
                                      0x0028,       // Primary weapon lateral offset (twin barrels alternate).
                                      0x0008,       // Secondary weapon offset along turret centerline.
                                      0x0040,       // Secondary weapon lateral offset (tusk pods).
                                      true,         // Can this be a goodie surprise from a crate? (TS CrateGoodie=yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (TS Crusher=yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret? (TS Turret=yes)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline.
                                      MISSION_HUNT  // ORDERS: Default order.
);

// RA2 Apocalypse (UNIT_R2APOC), Yuri's Revenge rules [APOC]; found only in crates. Its fire points come from the
// generated r2tanks_muzzle.h (techno.cpp Fire_Coord).
static UnitTypeClass const UnitR2Apoc(UNIT_R2APOC,
                                      TXT_HTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                      "R2APOC",     // NAME: IniName.
                                      ANIM_ART_EXP1,// EXPLOSION: big fragment explosion.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0020,       // Vertical offset.
                                      0x00C0,       // Primary weapon offset along turret centerline.
                                      0x0028,       // Primary weapon lateral offset (twin barrels alternate).
                                      0x0008,       // Secondary weapon offset along turret centerline.
                                      0x0040,       // Secondary weapon lateral offset (tusk pods).
                                      true,         // Can this be a goodie surprise from a crate? (YR CrateGoodie=yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (YR Crusher=yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret? (YR Turret=yes)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline.
                                      MISSION_HUNT  // ORDERS: Default order.
);

// RA2 Prism Tank (UNIT_R2PRIS), Yuri's Revenge rules [SREF]; found only in crates. Its prism beam forks onto nearby
// enemies (techno.cpp IsPrismBeam).
static UnitTypeClass const UnitR2Pris(UNIT_R2PRIS,
                                      TXT_MTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                      "R2PRIS",     // NAME: IniName.
                                      ANIM_FBALL1,  // EXPLOSION: big fireball.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0020,       // Vertical offset.
                                      0x0030,       // Primary weapon offset along turret centerline.
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset (none).
                                      0x0000,       // Secondary weapon lateral offset.
                                      true,         // Can this be a goodie surprise from a crate? (YR CrateGoodie=yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (YR Crusher=yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret? (YR Turret=yes)
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline.
                                      MISSION_HUNT  // ORDERS: Default order.
);

// C&C3 Mammoth Tank Mk. III (UNIT_C3MK3), Tiberium Wars GDIMammoth; found only in unit crates, by any faction. Its
// turret seat and fire points come from the generated c3tanks.h (Turret_Adjust, techno.cpp Fire_Coord).
static UnitTypeClass const UnitC3Mk3(UNIT_C3MK3,
                                     TXT_HTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                     "C3MK3",      // NAME: IniName.
                                     ANIM_ART_EXP1,// EXPLOSION: big fragment explosion.
                                     REMAP_NORMAL, // Sidebar remap logic.
                                     0x0020,       // Vertical offset.
                                     0x00C0,       // Primary weapon offset along turret centerline.
                                     0x0028,       // Primary weapon lateral offset (twin barrels alternate).
                                     0x0008,       // Secondary weapon offset along turret centerline.
                                     0x0040,       // Secondary weapon lateral offset (rocket pods).
                                     true,         // Can this be a goodie surprise from a crate?
                                     false,        // Always use the given name for the vehicle?
                                     true,         // Can this unit squash infantry?
                                     false,        // Does this unit harvest Tiberium?
                                     false,        // Is invisible to radar?
                                     false,        // Is it insignificant (won't be announced)?
                                     true,         // Is it equipped with a combat turret?
                                     false,        // Does it have a rotating radar dish?
                                     false,        // Is there an associated firing animation?
                                     false,        // Must the turret be in a locked down position while moving?
                                     false,        // Is this a gigundo-rotund-enormous unit?
                                     false,        // Does the unit have a constant animation?
                                     false,        // Is the unit capable of jamming radar?
                                     false,        // Is the unit a mobile gap generator?
                                     32,           // Rotation stages.
                                     0,            // Turret center offset along body centerline.
                                     MISSION_HUNT  // ORDERS: Default order.
);

// C&C3 Predator Tank (UNIT_C3PRED), Tiberium Wars GDIPredator; found only in unit crates, by any faction. Same
// generated seat and fire tables as UNIT_C3MK3; its turret sits aft of the hull centre.
static UnitTypeClass const UnitC3Pred(UNIT_C3PRED,
                                      TXT_MTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                      "C3PRED",     // NAME: IniName.
                                      ANIM_FBALL1,  // EXPLOSION: big fireball.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0020,       // Vertical offset.
                                      0x0080,       // Primary weapon offset along turret centerline.
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset (none).
                                      0x0000,       // Secondary weapon lateral offset.
                                      true,         // Can this be a goodie surprise from a crate?
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry?
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      true,         // Is it equipped with a combat turret?
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline.
                                      MISSION_HUNT  // ORDERS: Default order.
);

// TS Mobile EM-Pulse (UNIT_TSMEMP), Firestorm rules [MOBILEMP]: unarmed. It charges while not stunned and deploys to
// set off a small E.M. Pulse itself (UnitClass::EMP_Blast).
static UnitTypeClass const UnitTsMemp(UNIT_TSMEMP,
                                      TXT_APC,      // NAME: placeholder (HD display via rules.ini Name=).
                                      "TSMEMP",     // NAME: IniName.
                                      ANIM_FBALL1,  // EXPLOSION: big fireball.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0000,       // Vertical offset.
                                      0x0000,       // Primary weapon offset (unarmed).
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset.
                                      0x0000,       // Secondary weapon lateral offset.
                                      true,         // Can this be a goodie surprise from a crate? (FS CrateGoodie=yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (FS Crusher=yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      false,        // Is it equipped with a combat turret?
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline.
                                      MISSION_GUARD // ORDERS: Default order.
);

// TS Mobile Sensor Array (UNIT_TSLPST), TS rules [LPST]. No weapon: it turns east and
// deploys into STRUCT_TSDPSA, the sensor. TS: Strength=600, Armor=wood, TechLevel=6, Sight=10,
// Speed=6, Cost=950, Points=30, ROT=5, Crusher=yes, RadarInvisible=yes. Art = LPST.VXL voxel
// render, 32 facings.
static UnitTypeClass const UnitTsLpst(UNIT_TSLPST,
                                      TXT_APC,      // NAME: placeholder (HD display via rules.ini Name=).
                                      "TSLPST",     // NAME: IniName.
                                      ANIM_FBALL1,  // EXPLOSION: big fireball.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0000,       // Vertical offset.
                                      0x0000,       // Primary weapon offset (unarmed).
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset.
                                      0x0000,       // Secondary weapon lateral offset.
                                      false,        // Can this be a goodie surprise from a crate?
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (TS Crusher=yes)
                                      false,        // Does this unit harvest Tiberium?
                                      true,         // Is invisible to radar? (TS RadarInvisible=yes)
                                      false,        // Is it insignificant (won't be announced)?
                                      false,        // Is it equipped with a combat turret?
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline.
                                      MISSION_GUARD // ORDERS: Default order.
);

// TS Mobile War Factory (UNIT_TSMWAR), Firestorm rules [MOBWARG]: unarmed, it deploys into STRUCT_TSDWEAP. One per
// house, deployed or not (TF_Mwar_At_Cap).
static UnitTypeClass const UnitTsMwar(UNIT_TSMWAR,
                                      TXT_APC,      // NAME: placeholder (HD display via rules.ini Name=).
                                      "TSMWAR",     // NAME: IniName.
                                      ANIM_FBALL1,  // EXPLOSION: big fireball.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0000,       // Vertical offset.
                                      0x0000,       // Primary weapon offset (unarmed).
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset.
                                      0x0000,       // Secondary weapon lateral offset.
                                      false,        // Can this be a goodie surprise from a crate? (FS CrateGoodie=no)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (FS Crusher=yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      false,        // Is it equipped with a combat turret?
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline.
                                      MISSION_GUARD // ORDERS: Default order.
);

// TS Amphibious APC (UNIT_TSAPC), TS rules [APC]: an unarmed transport for 5 on SPEED_AMPHIBIOUS (rules.ini
// Amphibious=), a tracked drive that also crosses water. It joins the UNIT_APC unload sites.
static UnitTypeClass const UnitTsApc(UNIT_TSAPC,
                                     TXT_APC,      // NAME: placeholder (HD display via rules.ini Name=).
                                     "TSAPC",      // NAME: IniName.
                                     ANIM_FBALL1,  // EXPLOSION: big fireball.
                                     REMAP_NORMAL, // Sidebar remap logic.
                                     0x0000,       // Vertical offset.
                                     0x0000,       // Primary weapon offset (unarmed).
                                     0x0000,       // Primary weapon lateral offset.
                                     0x0000,       // Secondary weapon offset.
                                     0x0000,       // Secondary weapon lateral offset.
                                     true,         // Can this be a goodie surprise from a crate? (TS CrateGoodie=yes)
                                     false,        // Always use the given name for the vehicle?
                                     true,         // Can this unit squash infantry? (TS Crusher=yes)
                                     false,        // Does this unit harvest Tiberium?
                                     false,        // Is invisible to radar?
                                     false,        // Is it insignificant (won't be announced)?
                                     false,        // Is it equipped with a combat turret?
                                     false,        // Does it have a rotating radar dish?
                                     false,        // Is there an associated firing animation?
                                     false,        // Must the turret be in a locked down position while moving?
                                     false,        // Is this a gigundo-rotund-enormous unit?
                                     false,        // Does the unit have a constant animation?
                                     false,        // Is the unit capable of jamming radar?
                                     false,        // Is the unit a mobile gap generator?
                                     32,           // Rotation stages.
                                     0,            // Turret center offset along body centerline.
                                     MISSION_HUNT  // ORDERS: Default order.
);

// Mech Division (UNIT_TSMDIV): a token ordered at the dropship bay, never a unit on the map. The dropship turns it
// into 3 Titans and 2 Wolverines (bullet.cpp _mech_division), so its stats are inert placeholders.
static UnitTypeClass const UnitTsMdiv(UNIT_TSMDIV,
                                      TXT_HTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                      "TSMDIV",     // NAME: IniName.
                                      ANIM_FBALL1,  // EXPLOSION: unused (never on the map).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0000,       // Vertical offset.
                                      0x0000,       // Primary weapon offset.
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset.
                                      0x0000,       // Secondary weapon lateral offset.
                                      false,        // Crate goodie? Never -- a crate token would strand.
                                      false,        // Always use the given name?
                                      false,        // Can squash infantry?
                                      false,        // Harvests?
                                      false,        // Invisible to radar?
                                      true,         // Insignificant (no announcements for the token).
                                      false,        // Combat turret?
                                      false,        // Radar dish?
                                      false,        // Firing animation?
                                      false,        // Turret locked while moving?
                                      false,        // Gigundo?
                                      false,        // Constant animation?
                                      false,        // Radar jammer?
                                      false,        // Mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset.
                                      MISSION_GUARD // ORDERS: unused.
);

// TS Devil's Tongue (UNIT_TSSUBTANK), TS rules [SUBTANK]: a subterranean flame tank, found only in crates
// (docs/subterranean-design.md). It fires TSFireball, Burst=2 alternating between twin nozzles.
static UnitTypeClass const UnitTsSubTank(UNIT_TSSUBTANK,
                                         TXT_LTANK,    // NAME: placeholder (HD display via rules.ini Name=).
                                         "TSSUBTANK",  // NAME: IniName.
                                         ANIM_NAPALM3, // EXPLOSION: napalm burst (flame-carrier death).
                                         REMAP_NORMAL, // Sidebar remap logic.
                                         0x0000,       // Vertical offset.
                                         0x0080,       // Primary weapon offset = TS PrimaryFireFLH forward 128.
                                         0x0030,       // Primary weapon lateral (±E/W prong split, widened so E/W-facing jets read as two; TS itself fires from the centre).
                                         0x0080,       // Secondary weapon offset (mirror primary).
                                         0x0030,       // Secondary weapon lateral (mirror primary).
                                         true,         // Can this be a goodie surprise from a crate? (TS CrateGoodie=yes)
                                         false,        // Always use the given name for the vehicle?
                                         true,         // Can this unit squash infantry? (TS Crusher=yes)
                                         false,        // Does this unit harvest Tiberium?
                                         false,        // Is invisible to radar?
                                         false,        // Is it insignificant (won't be announced)?
                                         false,        // Is it equipped with a combat turret? (turret-less)
                                         false,        // Does it have a rotating radar dish?
                                         false,        // Is there an associated firing animation?
                                         false,        // Must the turret be in a locked down position while moving?
                                         false,        // Is this a gigundo-rotund-enormous unit?
                                         false,        // Does the unit have a constant animation?
                                         false,        // Is the unit capable of jamming radar?
                                         false,        // Is the unit a mobile gap generator?
                                         32,           // Rotation stages.
                                         0,            // Turret center offset along body centerline.
                                         MISSION_HUNT  // ORDERS: Default order.
);

// TS Subterranean APC (UNIT_TSSAPC), TS rules [SAPC]: an unarmed underground transport for 5, found only in crates
// (docs/subterranean-design.md). It joins the UNIT_APC unload sites.
static UnitTypeClass const UnitTsSapc(UNIT_TSSAPC,
                                      TXT_APC,      // NAME: placeholder (HD display via rules.ini Name=).
                                      "TSSAPC",     // NAME: IniName.
                                      ANIM_FBALL1,  // EXPLOSION: big fireball.
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0000,       // Vertical offset.
                                      0x0000,       // Primary weapon offset (unarmed).
                                      0x0000,       // Primary weapon lateral offset.
                                      0x0000,       // Secondary weapon offset.
                                      0x0000,       // Secondary weapon lateral offset.
                                      true,         // Can this be a goodie surprise from a crate? (TS CrateGoodie=yes)
                                      false,        // Always use the given name for the vehicle?
                                      true,         // Can this unit squash infantry? (TS Crusher=yes)
                                      false,        // Does this unit harvest Tiberium?
                                      false,        // Is invisible to radar?
                                      false,        // Is it insignificant (won't be announced)?
                                      false,        // Is it equipped with a combat turret?
                                      false,        // Does it have a rotating radar dish?
                                      false,        // Is there an associated firing animation?
                                      false,        // Must the turret be in a locked down position while moving?
                                      false,        // Is this a gigundo-rotund-enormous unit?
                                      false,        // Does the unit have a constant animation?
                                      false,        // Is the unit capable of jamming radar?
                                      false,        // Is the unit a mobile gap generator?
                                      32,           // Rotation stages.
                                      0,            // Turret center offset along body centerline.
                                      MISSION_HUNT  // ORDERS: Default order.
);

// The four faction MCVs (AMCV, SMCV, TDGMCV, TDNMCV). Each deploys its own faction's yard (unit.cpp
// MCV_Deploy_Building), and the yard grants that faction's tree to whoever holds it.
static UnitTypeClass const UnitSovietMcv(UNIT_SMCV,
                                         TXT_MCV,         // NAME:			Text name of this unit type.
                                         "SMCV",          // NAME:			IniName.
                                         ANIM_FBALL1,     // EXPLOSION:	Type of explosion when destroyed.
                                         REMAP_ALTERNATE, // Sidebar remap logic.
                                         0x0000,          //	Vertical offset.
                                         0x0000,          // Primary weapon offset along turret centerline.
                                         0x0000,          // Primary weapon lateral offset along turret centerline.
                                         0x0000,          // Secondary weapon offset along turret centerline.
                                         0x0000,          // Secondary weapon lateral offset along turret centerling.
                                         true,            // Can this be a goodie surprise from a crate?
                                         false,           // Always use the given name for the vehicle?
                                         true,            // Can this unit squash infantry?
                                         false,           // Does this unit harvest Tiberium?
                                         false,           // Is invisible to radar?
                                         false,           // Is it insignificant (won't be announced)?
                                         false,           // Is it equipped with a combat turret?
                                         false,           // Does it have a rotating radar dish?
                                         false,           // Is there an associated firing animation?
                                         false,           // Must the turret be in a locked down position while moving?
                                         true,            // Is this a gigundo-rotund-enormous unit?
                                         false,           // Does the unit have a constant animation?
                                         false,           // Is the unit capable of jamming radar?
                                         false,           // Is the unit a mobile gap generator?
                                         32,              // Rotation stages.
                                         0,               // Turret center offset along body centerline.
                                         MISSION_HUNT     // ORDERS:		Default order to give new unit.
);

static UnitTypeClass const UnitNodMcv(UNIT_TDNMCV,
                                      TXT_MCV,         // NAME:			Text name of this unit type.
                                      "TDNMCV",        // NAME:			IniName.
                                      ANIM_FBALL1,     // EXPLOSION:	Type of explosion when destroyed.
                                      REMAP_ALTERNATE, // Sidebar remap logic.
                                      0x0000,          //	Vertical offset.
                                      0x0000,          // Primary weapon offset along turret centerline.
                                      0x0000,          // Primary weapon lateral offset along turret centerline.
                                      0x0000,          // Secondary weapon offset along turret centerline.
                                      0x0000,          // Secondary weapon lateral offset along turret centerling.
                                      true,            // Can this be a goodie surprise from a crate?
                                      false,           // Always use the given name for the vehicle?
                                      true,            // Can this unit squash infantry?
                                      false,           // Does this unit harvest Tiberium?
                                      false,           // Is invisible to radar?
                                      false,           // Is it insignificant (won't be announced)?
                                      false,           // Is it equipped with a combat turret?
                                      false,           // Does it have a rotating radar dish?
                                      false,           // Is there an associated firing animation?
                                      false,           // Must the turret be in a locked down position while moving?
                                      true,            // Is this a gigundo-rotund-enormous unit?
                                      false,           // Does the unit have a constant animation?
                                      false,           // Is the unit capable of jamming radar?
                                      false,           // Is the unit a mobile gap generator?
                                      32,              // Rotation stages.
                                      0,               // Turret center offset along body centerline.
                                      MISSION_HUNT     // ORDERS:		Default order to give new unit.
);

static UnitTypeClass const UnitGdiMcv(UNIT_TDGMCV,
                                      TXT_MCV,         // NAME:			Text name of this unit type.
                                      "TDGMCV",        // NAME:			IniName.
                                      ANIM_FBALL1,     // EXPLOSION:	Type of explosion when destroyed.
                                      REMAP_ALTERNATE, // Sidebar remap logic.
                                      0x0000,          //	Vertical offset.
                                      0x0000,          // Primary weapon offset along turret centerline.
                                      0x0000,          // Primary weapon lateral offset along turret centerline.
                                      0x0000,          // Secondary weapon offset along turret centerline.
                                      0x0000,          // Secondary weapon lateral offset along turret centerling.
                                      true,            // Can this be a goodie surprise from a crate?
                                      false,           // Always use the given name for the vehicle?
                                      true,            // Can this unit squash infantry?
                                      false,           // Does this unit harvest Tiberium?
                                      false,           // Is invisible to radar?
                                      false,           // Is it insignificant (won't be announced)?
                                      false,           // Is it equipped with a combat turret?
                                      false,           // Does it have a rotating radar dish?
                                      false,           // Is there an associated firing animation?
                                      false,           // Must the turret be in a locked down position while moving?
                                      true,            // Is this a gigundo-rotund-enormous unit?
                                      false,           // Does the unit have a constant animation?
                                      false,           // Is the unit capable of jamming radar?
                                      false,           // Is the unit a mobile gap generator?
                                      32,              // Rotation stages.
                                      0,               // Turret center offset along body centerline.
                                      MISSION_HUNT     // ORDERS:		Default order to give new unit.
);

static UnitTypeClass const UnitAlliedMcv(UNIT_AMCV,
                                         TXT_MCV,         // NAME:			Text name of this unit type.
                                         "AMCV",          // NAME:			IniName.
                                         ANIM_FBALL1,     // EXPLOSION:	Type of explosion when destroyed.
                                         REMAP_ALTERNATE, // Sidebar remap logic.
                                         0x0000,          //	Vertical offset.
                                         0x0000,          // Primary weapon offset along turret centerline.
                                         0x0000,          // Primary weapon lateral offset along turret centerline.
                                         0x0000,          // Secondary weapon offset along turret centerline.
                                         0x0000,          // Secondary weapon lateral offset along turret centerling.
                                         true,            // Can this be a goodie surprise from a crate?
                                         false,           // Always use the given name for the vehicle?
                                         true,            // Can this unit squash infantry?
                                         false,           // Does this unit harvest Tiberium?
                                         false,           // Is invisible to radar?
                                         false,           // Is it insignificant (won't be announced)?
                                         false,           // Is it equipped with a combat turret?
                                         false,           // Does it have a rotating radar dish?
                                         false,           // Is there an associated firing animation?
                                         false,           // Must the turret be in a locked down position while moving?
                                         true,            // Is this a gigundo-rotund-enormous unit?
                                         false,           // Does the unit have a constant animation?
                                         false,           // Is the unit capable of jamming radar?
                                         false,           // Is the unit a mobile gap generator?
                                         32,              // Rotation stages.
                                         0,               // Turret center offset along body centerline.
                                         MISSION_HUNT     // ORDERS:		Default order to give new unit.
);

// TS MCV (UNIT_TSMCV), TS rules [MCV]: deploys STRUCT_TSFACT, the yard that gates the TS tree. It comes from unit
// crates, as TS GDI's comeback MCV, or from a TS war factory behind a TS tech centre.
static UnitTypeClass const UnitTsMcv(UNIT_TSMCV,
                                     TXT_MCV,         // NAME:			Text name of this unit type.
                                     "TSMCV",         // NAME:			IniName.
                                     ANIM_FBALL1,     // EXPLOSION:	Type of explosion when destroyed.
                                     REMAP_ALTERNATE, // Sidebar remap logic.
                                     0x0000,          //	Vertical offset.
                                     0x0000,          // Primary weapon offset along turret centerline.
                                     0x0000,          // Primary weapon lateral offset along turret centerline.
                                     0x0000,          // Secondary weapon offset along turret centerline.
                                     0x0000,          // Secondary weapon lateral offset along turret centerling.
                                     true,            // Can this be a goodie surprise from a crate?
                                     false,           // Always use the given name for the vehicle?
                                     true,            // Can this unit squash infantry?
                                     false,           // Does this unit harvest Tiberium?
                                     false,           // Is invisible to radar?
                                     false,           // Is it insignificant (won't be announced)?
                                     false,           // Is it equipped with a combat turret?
                                     false,           // Does it have a rotating radar dish?
                                     false,           // Is there an associated firing animation?
                                     false,           // Must the turret be in a locked down position while moving?
                                     true,            // Is this a gigundo-rotund-enormous unit?
                                     false,           // Does the unit have a constant animation?
                                     false,           // Is the unit capable of jamming radar?
                                     false,           // Is the unit a mobile gap generator?
                                     32,              // Rotation stages.
                                     0,               // Turret center offset along body centerline.
                                     MISSION_HUNT     // ORDERS:		Default order to give new unit.
);

// True for a mobile construction vehicle of any faction: the stock-campaign pair and the five faction MCVs.
bool UnitTypeClass::Is_MCV(void) const
{
    return (Type == UNIT_MCV || Type == UNIT_AMCV || Type == UNIT_SMCV || Type == UNIT_TDMCV
            || Type == UNIT_TDGMCV || Type == UNIT_TDNMCV || Type == UNIT_TSMCV);
}

/***********************************************************************************************
 * UnitTypeClass::Init_Heap -- Initialize the unit type class heap.                            *
 *                                                                                             *
 *    This initializes the unit type class heap by pre-allocated all the known unit types.     *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Only call this once and call it before processing the rules.ini file.           *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void UnitTypeClass::Init_Heap(void)
{
    /*
    **	These unit type class objects must be allocated in the exact order that they
    **	are specified in the UnitType enumeration. This is necessary because the heap
    **	allocation block index serves double duty as the type number index.
    */
    new UnitTypeClass(UnitHTank);       //	UNIT_HTANK
    new UnitTypeClass(UnitMTank);       //	UNIT_MTANK
    new UnitTypeClass(UnitMTank2);      //	UNIT_MTANK2
    new UnitTypeClass(UnitLTank);       //	UNIT_LTANK
    new UnitTypeClass(UnitAPC);         //	UNIT_APC
    new UnitTypeClass(UnitMineLayer);   // UNIT_MINELAYER
    new UnitTypeClass(UnitJeep);        //	UNIT_JEEP
    new UnitTypeClass(UnitHarvester);   //	UNIT_HARVESTER
    new UnitTypeClass(UnitArty);        //	UNIT_ARTY
    new UnitTypeClass(UnitMRJammer);    //	UNIT_MRJ
    new UnitTypeClass(UnitMGG);         //	UNIT_MGG
    new UnitTypeClass(UnitMCV);         // UNIT_MCV
    new UnitTypeClass(UnitV2Launcher);  //	UNIT_V2_LAUNCHER
    new UnitTypeClass(UnitConvoyTruck); // UNIT_TRUCK
#ifdef FIXIT_ANTS
    new UnitTypeClass(UnitAnt1); // UNIT_ANT1
    new UnitTypeClass(UnitAnt2); // UNIT_ANT2
    new UnitTypeClass(UnitAnt3); // UNIT_ANT3
#endif

#ifdef FIXIT_CSII                     //	checked - ajw 9/28/98
    new UnitTypeClass(UnitChrono);    // UNIT_CHRONOTANK
    new UnitTypeClass(UnitTesla);     // UNIT_TESLATANK
    new UnitTypeClass(UnitMAD);       // UNIT_MAD
    new UnitTypeClass(UnitDemoTruck); // UNIT_DEMOTRUCK
#ifdef FIXIT_PHASETRANSPORT           //	checked - ajw 9/28/98
    new UnitTypeClass(UnitPhase);     //	UNIT_PHASETRANSPORT
#endif
#endif
    // TF: the mod's unit types. Each must sit in the heap slot equal to its UnitType value (As_Reference indexes the
    // heap), so they follow the enum's order and new types go at the end.
    new UnitTypeClass(UnitTdMcv);     // UNIT_TDMCV
    new UnitTypeClass(UnitTdHarv);    // UNIT_TDHARV
    new UnitTypeClass(UnitTdMtnk);    // UNIT_TDMTNK
    new UnitTypeClass(UnitTdLtnk);    // UNIT_TDLTNK
    new UnitTypeClass(UnitTdHtnk);    // UNIT_TDHTNK
    new UnitTypeClass(UnitTdFtnk);    // UNIT_TDFTNK
    new UnitTypeClass(UnitTdBike);    // UNIT_TDBIKE
    new UnitTypeClass(UnitTdJeep);    // UNIT_TDJEEP
    new UnitTypeClass(UnitTdBggy);    // UNIT_TDBGGY
    new UnitTypeClass(UnitTdApc);     // UNIT_TDAPC
    new UnitTypeClass(UnitTdStnk);    // UNIT_TDSTNK
    new UnitTypeClass(UnitTdMlrs);    // UNIT_TDMLRS
    new UnitTypeClass(UnitTdMsam);    // UNIT_TDMSAM
    new UnitTypeClass(UnitTdArty);    // UNIT_TDARTY
    new UnitTypeClass(UnitTdVice);    // UNIT_TDVICE
    new UnitTypeClass(UnitTsHvr);     // UNIT_TSHVR (TS Hover MLRS)
    new UnitTypeClass(UnitTsTitn);    // UNIT_TSTITN (TS Titan walker)
    new UnitTypeClass(UnitTsHmec);    // UNIT_TSHMEC (TS Mammoth Mk. II)
    new UnitTypeClass(UnitSovietMcv); // UNIT_SMCV  (Soviet MCV)
    new UnitTypeClass(UnitNodMcv);    // UNIT_TDNMCV (Nod MCV)
    new UnitTypeClass(UnitGdiMcv);    // UNIT_TDGMCV (GDI MCV)
    new UnitTypeClass(UnitAlliedMcv); // UNIT_AMCV  (Allied MCV)
    new UnitTypeClass(UnitTsMcv);     // UNIT_TSMCV (TS MCV)
    new UnitTypeClass(UnitTsHarv);    // UNIT_TSHARV (TS Harvester)
    new UnitTypeClass(UnitTsSmec);    // UNIT_TSSMEC (TS Wolverine)
    new UnitTypeClass(UnitTsSonic);   // UNIT_TSSONIC (TS Disruptor)
    new UnitTypeClass(UnitTsApc);     // UNIT_TSAPC (TS Amphibious APC)
    new UnitTypeClass(UnitTsMdiv);    // UNIT_TSMDIV (Mech Division token)
    new UnitTypeClass(UnitTsSubTank); // UNIT_TSSUBTANK (Devil's Tongue)
    new UnitTypeClass(UnitTsSapc);    // UNIT_TSSAPC (Subterranean APC)
    new UnitTypeClass(UnitTs4tnk);    // UNIT_TS4TNK (the old TS Mammoth Tank)
    new UnitTypeClass(UnitTsJugg);    // UNIT_TSJUGG (Juggernaut)
    new UnitTypeClass(UnitTsLimp);    // UNIT_TSLIMP (Limpet Drone)
    new UnitTypeClass(UnitR2Apoc);    // UNIT_R2APOC (RA2 Apocalypse)
    new UnitTypeClass(UnitR2Pris);    // UNIT_R2PRIS (RA2 Prism Tank)
    new UnitTypeClass(UnitTsMemp);    // UNIT_TSMEMP (Mobile EM-Pulse)
    new UnitTypeClass(UnitTsLpst);    // UNIT_TSLPST (Mobile Sensor Array)
    new UnitTypeClass(UnitTsMwar);    // UNIT_TSMWAR (Mobile War Factory)
    new UnitTypeClass(UnitC3Mk3);     // UNIT_C3MK3 (C&C3 Mammoth Tank Mk. III)
    new UnitTypeClass(UnitC3Pred);    // UNIT_C3PRED (C&C3 Predator Tank)
}

/***********************************************************************************************
 * UnitTypeClass::From_Name -- Fetch class pointer from specified name.                        *
 *                                                                                             *
 *    This routine converts an ASCII representation of a unit class and                        *
 *    converts it into a real unit class number.                                               *
 *                                                                                             *
 * INPUT:   name  -- ASCII name representing a unit class.                                     *
 *                                                                                             *
 * OUTPUT:  Returns with the actual unit class number that the string                          *
 *          represents.                                                                        *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/07/1992 JLB : Created.                                                                 *
 *   05/02/1994 JLB : Converted to member function.                                            *
 *=============================================================================================*/
UnitType UnitTypeClass::From_Name(char const* name)
{
    if (name != NULL) {
        for (UnitType classid = UNIT_FIRST; classid < UNIT_COUNT; classid++) {
            if (stricmp(As_Reference(classid).IniName, name) == 0) {
                return (classid);
            }
        }
    }
    return (UNIT_NONE);
}

#ifdef SCENARIO_EDITOR
/***********************************************************************************************
 * UnitTypeClass::Display -- Displays a generic unit shape.                                    *
 *                                                                                             *
 *    This routine displays a generic representation of a unit of this                         *
 *    type. Typically, it is used when adding objects to the game map.                         *
 *                                                                                             *
 * INPUT:   x,y   -- Coordinate to render the unit shape.                                      *
 *                                                                                             *
 *          window-- Window to render within.                                                  *
 *                                                                                             *
 *          house -- House to render the unit colors.                                          *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/14/1994 JLB : Created.                                                                 *
 *   11/08/1994 JLB : Handles chunky type vehicles now.                                        *
 *=============================================================================================*/
void UnitTypeClass::Display(int x, int y, WindowNumberType window, HousesType) const
{
    int shape = 0;
    void const* ptr = Get_Cameo_Data();
    if (ptr == NULL) {
        ptr = Get_Image_Data();
        shape = Rotation / 6;
    }
    CC_Draw_Shape(ptr, shape, x, y, window, SHAPE_CENTER | SHAPE_WIN_REL);
}

/***********************************************************************************************
 * UnitTypeClass::Prep_For_Add -- Prepares scenario editor to add unit.                        *
 *                                                                                             *
 *    This routine is used to prepare the generic object adder dialog                          *
 *    box so that it will be able to add a unit object.                                        *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/23/1994 JLB : Created.                                                                 *
 *   06/04/1994 JLB : Uses map editing interface functions.                                    *
 *=============================================================================================*/
void UnitTypeClass::Prep_For_Add(void)
{
    for (UnitType index = UNIT_FIRST; index < UNIT_COUNT; index++) {
        if (As_Reference(index).Get_Image_Data() != NULL) {
            Map.Add_To_List(&As_Reference(index));
        }
    }
}
#endif

/***********************************************************************************************
 * UnitTypeClass::One_Time -- Performs one time processing for unit type class objects.        *
 *                                                                                             *
 *    This routine is used to perform the action necessary only once for the unit type class.  *
 *    It loads unit shapes and brain files.   This routine should only be called once.         *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Only call this routine once.                                                    *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/28/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void UnitTypeClass::One_Time(void)
{
    for (UnitType index = UNIT_FIRST; index < UNIT_COUNT; index++) {
        char fullname[_MAX_FNAME + _MAX_EXT];
        char buffer[_MAX_FNAME + 4];
        UnitTypeClass const& uclass = As_Reference(index);
        CCFileClass file;

        void const* ptr; // Shape pointer and set pointer.

        int largest = 0;
        //		if (uclass.Level != -1) {
        //		if (uclass.IsBuildable) {

        /*
        **	Fetch the supporting data files for the unit.
        */
        sprintf(buffer, "%sICON", uclass.Graphic_Name());
        _makepath(fullname, NULL, NULL, buffer, ".SHP");
#ifndef NDEBUG
        RawFileClass datafile(fullname);
        if (datafile.Is_Available()) {
            ((void const*&)uclass.CameoData) = Load_Alloc_Data(datafile);
        } else {
            ((void const*&)uclass.CameoData) = MFCD::Retrieve(fullname);
        }
#else
        ((void const*&)uclass.CameoData) = MFCD::Retrieve(fullname);
#endif
        //		}

        /*
        **	Fetch a pointer to the unit's shape data.
        */
        _makepath(fullname, NULL, NULL, uclass.Graphic_Name(), ".SHP");
#ifndef NDEBUG
        RawFileClass shpfile(fullname);
        if (shpfile.Is_Available()) {
            ptr = Load_Alloc_Data(shpfile);
        } else {
            ptr = MFCD::Retrieve(fullname);
        }
#else
        ptr = MFCD::Retrieve(fullname);
#endif

        ((void const*&)uclass.ImageData) = ptr;
        if (ptr != NULL) {

            largest = max(largest, (int)Get_Build_Frame_Width(ptr));
            largest = max(largest, (int)Get_Build_Frame_Height(ptr));
        }

        ((int&)uclass.MaxSize) = max(largest, 8);
    }

    // TF: HD-only units have no classic SHP: Draw_It bails on a NULL ImageData, and MaxSize stays at its floor of 8.
    // They take a same-size vanilla unit's shapes and size; the launcher draws their real art by IniName.
    {
        static const struct { UnitType hd; UnitType donor; } _hd_udonors[] = {
            {UNIT_TSHVR, UNIT_MTANK2},
            {UNIT_TSTITN, UNIT_MTANK2},
            {UNIT_TSHMEC, UNIT_HTANK},
            {UNIT_AMCV, UNIT_MCV},
            {UNIT_SMCV, UNIT_MCV},
            {UNIT_TDGMCV, UNIT_TDMCV},
            {UNIT_TDNMCV, UNIT_TDMCV},
            {UNIT_TSMCV, UNIT_MCV}, // TS tree: MCV.VXL render under TSMCV keys
        };
        for (int di = 0; di < (int)(sizeof(_hd_udonors) / sizeof(_hd_udonors[0])); di++) {
            UnitTypeClass& u = As_Reference(_hd_udonors[di].hd);
            UnitTypeClass const& d = As_Reference(_hd_udonors[di].donor);
            if (u.ImageData == NULL) {
                ((void const*&)u.ImageData) = d.ImageData;
            }
            if (u.MaxSize <= 8) {
                ((int&)u.MaxSize) = d.MaxSize;
            }
        }
    }

    /*
    **	Load any custom shapes at this time.
    */
    if (WakeShapes == NULL) {
        WakeShapes = MFCD::Retrieve("WAKE.SHP");
    }
    if (TurretShapes == NULL) {
        TurretShapes = MFCD::Retrieve("TURR.SHP");
    }
    if (SamShapes == NULL) {
        SamShapes = MFCD::Retrieve("SSAM.SHP");
    }
    if (MGunShapes == NULL) {
        MGunShapes = MFCD::Retrieve("MGUN.SHP");
    }
}

/***********************************************************************************************
 * UnitTypeClass::Create_And_Place -- Creates and places a unit object onto the map.           *
 *                                                                                             *
 *    This routine is used by the scenario editor to create and place a unit object of this    *
 *    type onto the map.                                                                       *
 *                                                                                             *
 * INPUT:   cell     -- The cell that the unit is to be placed into.                           *
 *                                                                                             *
 *          house    -- The house that the unit belongs to.                                    *
 *                                                                                             *
 * OUTPUT:  bool; Was the unit created and placed successfully?                                *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/28/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
bool UnitTypeClass::Create_And_Place(CELL cell, HousesType house) const
{
    UnitClass* unit = new UnitClass(Type, house);
    if (unit != NULL) {
        return (unit->Unlimbo(Cell_Coord(cell), Random_Pick(DIR_N, DIR_MAX)));
    }
    return (false);
}

/***********************************************************************************************
 * UnitTypeClass::Create_One_Of -- Creates a unit in limbo.                                    *
 *                                                                                             *
 *    This function creates a unit of this type and keeps it in limbo. A pointer to the        *
 *    created unit object is returned. It is presumed that this object will later be           *
 *    unlimboed at the correct time and place.                                                 *
 *                                                                                             *
 * INPUT:   house -- Pointer to the house that is to own the unit.                             *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the created unit object. If the unit object              *
 *          could not be created, then NULL is returned.                                       *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/07/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
ObjectClass* UnitTypeClass::Create_One_Of(HouseClass* house) const
{
    return (new UnitClass(Type, house->Class->House));
}

/***********************************************************************************************
 * UnitTypeClass::As_Reference -- Fetches a reference to the unit type class specified.        *
 *                                                                                             *
 *    Use this routine to return a reference to the UnitTypeClass object as indicated by       *
 *    the unit type number specified.                                                          *
 *                                                                                             *
 * INPUT:   type  -- The unit type number to convert into a UnitTypeClass object reference.    *
 *                                                                                             *
 * OUTPUT:  Returns with a reference to the unit type class object specified.                  *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
UnitTypeClass& UnitTypeClass::As_Reference(UnitType type)
{
    return (*UnitTypes.Ptr(type));
}

/***********************************************************************************************
 * UnitTypeClass::Dimensions -- Determines the unit's pixel dimensions.                        *
 *                                                                                             *
 *    This routine will fill in the width and height for this unit type. This width and        *
 *    height are used to render the selection rectangle and the positioning of the health      *
 *    bargraph.                                                                                *
 *                                                                                             *
 * INPUT:   width    -- Reference to the width of the unit (to be filled in).                  *
 *                                                                                             *
 *          height   -- Reference to the height of the unit (to be filled in).                 *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void UnitTypeClass::Dimensions(int& width, int& height) const
{
    // TF: HD units' boxes in classic px, as wide as the art and twice its reach from the unit's centre so the health
    // bar clears the unit; scripts/unit_centring.py prints them for the vehicles it centres.
    static const struct {
        UnitType type;
        short width;
        short height;
    } _art_boxes[] = {
        {UNIT_R2APOC, 35, 30},
        {UNIT_R2PRIS, 33, 34},
        {UNIT_C3MK3, 53, 33},
        {UNIT_C3PRED, 32, 22},
        {UNIT_TS4TNK, 33, 30},
        {UNIT_TSSONIC, 37, 31},
        {UNIT_TSHMEC, 42, 41},
        {UNIT_TSHARV, 37, 28},
        {UNIT_TSSMEC, 14, 27},
        {UNIT_TSJUGG, 31, 32},
        {UNIT_TSSUBTANK, 36, 26},
        {UNIT_TSSAPC, 28, 20},
        {UNIT_TSHVR, 30, 28},
        {UNIT_TSTITN, 29, 49},
        {UNIT_TSAPC, 30, 21},
        {UNIT_TSMCV, 35, 23},
        {UNIT_TSLIMP, 12, 32},
        {UNIT_TSMEMP, 33, 22},
        {UNIT_TSLPST, 31, 23},
        {UNIT_TSMWAR, 33, 28},
    };
    for (int i = 0; i < (int)ARRAY_SIZE(_art_boxes); i++) {
        if (_art_boxes[i].type == Type) {
            width = _art_boxes[i].width;
            height = _art_boxes[i].height;
            return;
        }
    }
    width = MaxSize - (MaxSize / 4);
    width = min(width, 48);
    height = MaxSize - (MaxSize / 4);
    height = min(height, 48);
}

/***********************************************************************************************
 * UnitTypeClass::Max_Pips -- Fetches the maximum pips allowed for this unit.                  *
 *                                                                                             *
 *    This routine will determine the number of pips (maximum) allowed for this unit type.     *
 *    Typically, this is the number of passengers allowed, but for harvesters, it is the       *
 *    number of credits it holds divided by 100.                                               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the maximum number of pips allowed for this unit type.                *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/26/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int UnitTypeClass::Max_Pips(void) const
{
    if (Type == UNIT_HARVESTER || Type == UNIT_TDHARV || Type == UNIT_TSHARV) {
        return (7);
    }

    if (Type == UNIT_MINELAYER) {
        return (MaxAmmo);
    }

    if (Type == UNIT_TSMEMP) {
        return (5);
    }
    return (Max_Passengers());
}

/***********************************************************************************************
 * UnitTypeClass::Turret_Adjust -- Turret adjustment routine for MLRS and MSAM units.          *
 *                                                                                             *
 *    This routine adjusts the pixel coordinates specified to account for the displacement of  *
 *    the turret on the MLRS and MSAM vehicles.                                                *
 *                                                                                             *
 * INPUT:   dir   -- The direction of the body of the vehicle.                                 *
 *                                                                                             *
 *          x,y   -- References to the turret center pixel position. These will be modified as *
 *                   necessary.                                                                *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void UnitTypeClass::Turret_Adjust(DirType dir, int& x, int& y) const
{
    static struct
    {
        signed char X, Y;
    } _adjust[32] = {{1, 2},                                 // N
                     {-1, 1},  {-2, 0},  {-3, 0},  {-3, 1},  // NW
                     {-4, -1}, {-4, -1}, {-5, -2}, {-5, -3}, // W
                     {-5, -3}, {-3, -3}, {-3, -4}, {-3, -4}, // SW
                     {-3, -5}, {-2, -5}, {-1, -5}, {0, -5},  // S
                     {1, -6},  {2, -5},  {3, -5},  {4, -5},  // SE
                     {6, -4},  {6, -3},  {6, -3},  {6, -3},  // E
                     {5, -1},  {5, -1},  {4, 0},   {3, 0},   // NE
                     {2, 0},   {2, 1},   {1, 2}};

    int index = 0;
    switch (Type) {
    case UNIT_JEEP:
    // TF: the TD Hum-vee and Buggy are small MG cars like the Ranger; their turrets take the same lift.
    case UNIT_TDJEEP:
    case UNIT_TDBGGY:
        y -= 4;
        break;

    case UNIT_MGG:
    // TF: the TD Rocket Launcher and SSM Launcher seat their rear-mounted launchers by this per-facing table.
    case UNIT_TDMLRS:
    case UNIT_TDMSAM:
        index = Dir_To_32(dir);
        x += _adjust[index].X;
        y += _adjust[index].Y;
        break;

    // TF: per-facing turret seats for the HD units.
    case UNIT_TSHVR:
        Hover_Rack_Seat(dir, x, y);
        break;

    case UNIT_TSSONIC:
        Sonic_Turret_Seat(dir, x, y);
        break;

    case UNIT_C3MK3:
        x += _c3mk3_seat_px[TechnoClass::BodyShape[Dir_To_32(dir)]][0];
        y += _c3mk3_seat_px[TechnoClass::BodyShape[Dir_To_32(dir)]][1];
        break;

    case UNIT_C3PRED:
        x += _c3pred_seat_px[TechnoClass::BodyShape[Dir_To_32(dir)]][0];
        y += _c3pred_seat_px[TechnoClass::BodyShape[Dir_To_32(dir)]][1];
        break;

    default:
        break;
    }
}

// Seats the Hover MLRS rack on the pad drawn in its hull frame, 12.54 voxels aft (classic px per hull frame, from
// the HD art's README in resources/custom-art/ts-units-hd/tshvr/). The rack frames turn about their own pivot.
void UnitTypeClass::Hover_Rack_Seat(DirType hull, int& x, int& y) const
{
    static const signed char _seat[32][2] = {
        {0, 5},   {2, 5},   {3, 5},   {5, 4},   {6, 4},   {8, 3},   {8, 2},   {9, 1},
        {9, 0},   {9, -1},  {9, -2},  {8, -3},  {7, -3},  {5, -4},  {4, -4},  {2, -5},
        {0, -5},  {-2, -5}, {-3, -5}, {-5, -4}, {-6, -4}, {-8, -3}, {-8, -2}, {-9, -1},
        {-9, 0},  {-9, 1},  {-9, 2},  {-8, 3},  {-7, 3},  {-5, 4},  {-4, 4},  {-2, 5}};
    int f = TechnoClass::BodyShape[Dir_To_32(hull)];
    x += _seat[f][0];
    y += _seat[f][1];
}

// Seats the Disruptor turret 0.43 cell aft along the hull, on the ground as the art's camera draws it (classic px
// per hull frame, from the HD art's README in resources/custom-art/ts-units-hd/tssonic/).
void UnitTypeClass::Sonic_Turret_Seat(DirType dir, int& x, int& y) const
{
    static const signed char _seat[32][2] = {
        {0, 5},   {2, 5},   {4, 5},   {6, 5},   {7, 4},   {9, 3},   {10, 2},  {10, 1},
        {10, 0},  {10, -1}, {10, -2}, {9, -3},  {7, -4},  {6, -5},  {4, -5},  {2, -5},
        {0, -5},  {-2, -5}, {-4, -5}, {-6, -5}, {-7, -4}, {-9, -3}, {-10, -2}, {-10, -1},
        {-10, 0}, {-10, 1}, {-10, 2}, {-9, 3},  {-7, 4},  {-6, 5},  {-4, 5},  {-2, 5}};
    int f = TechnoClass::BodyShape[Dir_To_32(dir)];
    x += _seat[f][0];
    y += _seat[f][1];
}

/***********************************************************************************************
 * UnitTypeClass::Read_INI -- Fetch the unit type data from the INI database.                  *
 *                                                                                             *
 *    This routine will find the section in the INI database for this unit type object and     *
 *    then fill in the override values specified.                                              *
 *                                                                                             *
 * INPUT:   ini   -- Reference to the INI database that will be examined.                      *
 *                                                                                             *
 * OUTPUT:  bool; Was the section for this unit found in the database and the data extracted?  *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/19/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
bool UnitTypeClass::Read_INI(CCINIClass& ini)
{
    if (TechnoTypeClass::Read_INI(ini)) {
        IsNoFireWhileMoving = ini.Get_Bool(IniName, "NoMovingFire", IsNoFireWhileMoving);
        WalkFrames = ini.Get_Int(IniName, "WalkFrames", WalkFrames);
        WalkFacings = ini.Get_Int(IniName, "WalkFacings", WalkFacings);
        IsDeployToFire = ini.Get_Bool(IniName, "DeployToFire", IsDeployToFire);
        DeployFrames = ini.Get_Int(IniName, "DeployFrames", DeployFrames);
        DeployRate = max(1, ini.Get_Int(IniName, "DeployRate", DeployRate));
        FiringFrames = ini.Get_Int(IniName, "FiringFrames", FiringFrames);
        WalkRate = max(1, ini.Get_Int(IniName, "WalkRate", WalkRate));
        Speed = ini.Get_Bool(IniName, "Tracked", (Speed == SPEED_TRACK)) ? SPEED_TRACK : SPEED_WHEEL;
        // TF: Amphibious= and Hover= replace the Tracked choice with TS's locomotors, which also cross water.
        if (ini.Get_Bool(IniName, "Amphibious", (Speed == SPEED_AMPHIBIOUS))) {
            Speed = SPEED_AMPHIBIOUS; // TS SpeedType=Amphibious
        }
        if (ini.Get_Bool(IniName, "Hover", (Speed == SPEED_HOVER))) {
            Speed = SPEED_HOVER;
        }

        // TF: Logic=<vanilla IniName> runs this entry as that unit type, borrowing its flags and the art One_Time loads
        // only for vanilla slots. Primary= and Secondary= in the entry's own section win over the donor's.
        char buffer[64];
        if (ini.Get_String(IniName, "Logic", "", buffer, sizeof(buffer)) > 0) {
            UnitTypeClass* donor = UnitTypeClass::As_Pointer(buffer);
            if (donor != NULL && donor != this) {
                Type = donor->Type;
                IsCrateGoodie = donor->IsCrateGoodie;
                IsCrusher = donor->IsCrusher;
                IsToHarvest = donor->IsToHarvest;
                IsRadarEquipped = donor->IsRadarEquipped;
                IsFireAnim = donor->IsFireAnim;
                IsLockTurret = donor->IsLockTurret;
                IsGigundo = donor->IsGigundo;
                IsAnimating = donor->IsAnimating;
                IsJammer = donor->IsJammer;
                IsGapper = donor->IsGapper;
                IsNoFireWhileMoving = donor->IsNoFireWhileMoving;
                TurretOffset = donor->TurretOffset;
                Mission = donor->Mission;
                Explosion = donor->Explosion;
                MaxSize = donor->MaxSize;
                Speed = donor->Speed;
                ((void const*&)ImageData) = donor->ImageData;
                if (PrimaryWeapon == NULL) {
                    PrimaryWeapon = donor->PrimaryWeapon;
                }
                if (SecondaryWeapon == NULL) {
                    SecondaryWeapon = donor->SecondaryWeapon;
                }
            }
        }

        /*
        **	If this unit can drive over walls, then mark it as recognizing the crusher zone.
        */
        if (MZone < MZONE_CRUSHER && IsCrusher) {
            MZone = MZONE_CRUSHER;
        }
        return (true);
    }
    return (false);
}
