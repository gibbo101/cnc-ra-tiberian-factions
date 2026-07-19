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
static UnitTypeClass const UnitMCV(UNIT_AMCV,
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

/*
**  TDHARV (Tiberian Factions Tiberium Harvester) — verbatim port of TD's
**  UNIT_HARVESTER (tiberiandawn/udata.cpp:585). Behavior identical to
**  RA's UnitHarvester (same IsToHarvest, MISSION_HARVEST default, etc).
**  Only difference is the sprite — TDHARV uses TD's bulkier "Harvy"
**  art. Shared by GDI + Nod (matches TD original). Spawned as the free
**  unit from STRUCT_TDPROC.
*/
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

/*
**  TDMCV (Tiberian Factions Mobile Construction Vehicle) — verbatim port
**  of TD's UNIT_AMCV (tiberiandawn/udata.cpp:638 UnitMCV). RA's UnitTypeClass
**  ctor has 21 params vs TD's 27 (RA elides build_level/cost/strength/armor/
**  weapons/ownable — those come from rules.ini). Field values mirror RA's
**  UnitMCV with one philosophical difference: TDMCV is conceptually shared
**  by HOUSE_GOOD + HOUSE_BAD (matching TD original — both factions use the
**  same MCV sprite), but the rules.ini [TDMCV] Owner= field controls
**  ownability at runtime. Deploy creates STRUCT_TDGFACT (not STRUCT_AFACT)
**  — see UnitClass::Try_To_Deploy per-type extension.
*/
static UnitTypeClass const UnitTdMcv(UNIT_TDGMCV,
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

// Tiberian Factions -- TD Medium Tank (UNIT_TDMTNK), ported from TD's UNIT_MTANK
// (tiberiandawn/udata.cpp:264). GDI-only (TD MTANK = HOUSEF_GOOD). Flags mapped
// from TD source: combat turret, crusher (squashes infantry), gigundo, crate-goodie;
// explosion ANIM_FRAG2; 32 rotation stages; turret-center-offset 0 (TD value).
// Gameplay stats (Strength 400/Sight 3/Cost 800/Armor steel/Speed=MPH_MEDIUM/dmg30/
// ROF50/range4.75) all come from rules.ini [TDMTNK]/[TD105mm], TD-source-derived.
// The vertical/weapon RENDER offsets are RA-only ctor fields (no TD equivalent) --
// a pixel-calibration of the muzzle flash against the TD MTNK turret sprite; started
// from RA's same-size 2TNK and tuned in-game. Fires WEAPON_TD105MM (BULLET_TDAPDS).
static UnitTypeClass const UnitTdMtnk(UNIT_TDMTNK,
                                      TXT_MTANK2,   // NAME: (RA "Medium Tank"; HD display via rules.ini Name=).
                                      "TDMTNK",     // NAME: IniName.
                                      ANIM_TDFRAG2, // EXPLOSION: TD vehicle frag explosion (ported TD ANIM_FRAG2 -> TDFRAG3 / FRAG3 art).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0030,       // Vertical offset (render calibration, ref 2TNK -- tune to TD sprite).
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

// Tiberian Factions -- TD Light Tank (UNIT_TDLTNK), ported from TD's UNIT_LTANK
// (tiberiandawn/udata.cpp:211). NOD-ONLY (TD LTANK = HOUSEF_BAD). Nod's mainline
// tank -- like the GDI Medium Tank but smaller (NOT gigundo) and cheaper. Explosion
// ANIM_FRAG1, which RA has natively (no FRAG port needed, unlike the MTANK). Gameplay
// stats (Strength 300/Sight 3/Cost 600/Speed=MPH_MEDIUM/dmg25/ROF60/range4) come from
// rules.ini [TDLTNK]/[TD75mm], TD-source-derived. Render geometry from RA's same-size
// 1TNK light tank (vert 0x0020, tune to TD sprite). Fires WEAPON_TD75MM (BULLET_TDAPDS).
static UnitTypeClass const UnitTdLtnk(UNIT_TDLTNK,
                                      TXT_LTANK,    // NAME: (RA "Light Tank"; HD display via rules.ini Name=).
                                      "TDLTNK",     // NAME: IniName.
                                      ANIM_FRAG1,   // EXPLOSION: TD LTANK death (ANIM_FRAG1 -- RA has it).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0020,       // Vertical offset (render calibration, ref RA 1TNK -- tune to TD sprite).
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

// Tiberian Factions -- TD Mammoth Tank (UNIT_TDHTNK), ported from TD's UNIT_HTANK
// (tiberiandawn/udata.cpp:317). GDI-ONLY (TD HTANK = HOUSEF_GOOD). The iconic GDI
// heavy: DUAL weapon -- primary TD120mm cannon (anti-ground) + secondary TDTusk AA
// missiles (TDSSM, AA+AG homing). Gigundo, Strength 600, Cost 1500. Explosion
// ANIM_ART_EXP1 (RA has it natively). Stats from rules.ini [TDHTNK]/[TD120mm]/[TDTusk];
// Speed=6 = MPH_MEDIUM_SLOW (MaxSpeed/2). Dual-weapon render geometry from RA's own
// Mammoth 4TNK (primary 0x00C0/0x0028, secondary 0x0008/0x0040 lateral barrels).
// TD's "fires multiple shots" (the double-tap) is replicated via Burst=2 on the
// weapons (rules.ini), since RA has no unit-level two-shooter flag -- same as [TDTowTwo].
static UnitTypeClass const UnitTdHtnk(UNIT_TDHTNK,
                                      TXT_HTANK,    // NAME: (RA "Mammoth Tank"; HD display via rules.ini Name=).
                                      "TDHTNK",     // NAME: IniName.
                                      ANIM_ART_EXP1,// EXPLOSION: TD HTANK death (ANIM_ART_EXP1 -- RA has it).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0020,       // Vertical offset (render calibration, ref RA 4TNK -- tune to TD sprite).
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

// Tiberian Factions -- TD Flame Tank (UNIT_TDFTNK), ported from TD's UNIT_FTANK
// (tiberiandawn/udata.cpp UnitFTank). NOD-ONLY (faction choice, like the Light Tank;
// TD FTANK source ownable includes GOOD|BAD but we assign it to Nod). Turret-LESS
// (is_turret_equipped=false): the weapon is a directional flame jet drawn as an 8-dir
// muzzle anim (ANIM_FLAME_N) in TechnoClass::Fire_At -- same mechanism as the E4
// Flamethrower. No rotating turret, but the muzzle POSITION still comes from Fire_Coord's
// PrimaryOffset/PrimaryLateral = TD FTANK's turret.cpp geometry (0x30 fwd + ±0x20 split),
// so the twin jets seat on the front nozzles. Fires WEAPON_TDFLAMETONGUE
// (the stronger FLAME_TONGUE: Dmg50 vs the Flamethrower's 35). is_crusher (squashes
// infantry). TD's "fires two shots in quick succession" double-jet is replicated via
// Burst=2 on the weapon (rules.ini), as RA has no unit-level two-shooter flag. Explosion
// ANIM_NAPALM3 (RA has it -- a large napalm burst, fitting). Internal name = TXT_LTANK
// (RA has no Flame Tank string); the real "Flame Tank" display comes from rules.ini Name=.
// Stats (Strength 300, Cost 800, Speed=9 = MPH_MEDIUM/2, ROT 5) from rules.ini [TDFTNK].
static UnitTypeClass const UnitTdFtnk(UNIT_TDFTNK,
                                      TXT_LTANK,    // NAME: (RA has no "Flame Tank"; HD display via rules.ini Name=).
                                      "TDFTNK",     // NAME: IniName.
                                      ANIM_NAPALM3, // EXPLOSION: TD FTANK death (ANIM_NAPALM3 -- RA has it).
                                      REMAP_NORMAL, // Sidebar remap logic.
                                      0x0000,       // Vertical offset = 0 (TD FTANK has no DIR_N pre-move; turret.cpp omits the perspective raise -- the jet sits at hull level).
                                      0x0030,       // Primary weapon offset = TD FTANK dist=0x30 (forward along body; turret.cpp:430). Carries the twin jets OUT to the front nozzles -- do NOT zero it (forward offset != lateral; zeroing it drops the jets back onto the hull center).
                                      0x0020,       // Primary weapon lateral = TD FTANK 0x20 (the ±E/W nozzle split; IsSecondShot picks side, turret.cpp:431-435).
                                      0x0030,       // Secondary weapon offset (unused: Burst=2 keeps which=0; mirror primary for safety).
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

// Tiberian Factions -- TD Recon Bike (UNIT_TDBIKE), ported from TD's UNIT_BIKE
// (tiberiandawn/udata.cpp:797 UnitBike). NOD-ONLY (TD BIKE ownable = HOUSEF_BAD|MULTI|JP).
// Wheeled (SPEED_WHEEL -- so NO Tracked= in rules.ini, the authentic 60%/40% terrain mod) and
// turret-LESS, a fast light scout. Fires WEAPON_DRAGON -- which we ALREADY ship as [TDDragon]
// (the E3 Rocket Soldier's launcher: the BULLET_TDTOW homing rocket + WARHEAD_TDAP + Report
// BAZOOK1). So this port REUSES the whole E3 weapon chain verbatim -- zero new weapon/bullet/
// warhead/sound. Explosion ANIM_FRAG1 is TD-authentic (TD's BIKE uses FRAG1, NOT the tank
// FRAG2 -- RA has FRAG1 natively, so no §FRAG anim port). NOT a crusher (TD BIKE squash=false,
// a light bike can't squash) and NOT gigundo. All-zero weapon offsets follow RA's own wheeled-
// rocket V2 Launcher (UnitV2Launcher above): the rocket launches from the hull, there's no
// turret geometry to screenshot-tune. Stats (Strength 160, Cost 500, Speed=16 = MPH_FAST via
// round(40*100/256), ROT 10, Armor wood, TechLevel 2, Sight 2) all come from rules.ini [TDBIKE].
// Internal name TXT_LTANK is a never-shown placeholder (RA has no Recon Bike string, same as the
// Flame Tank); the real "Recon Bike" display name comes from rules.ini Name=.
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

// Tiberian Factions -- TD Hum-vee (UNIT_TDJEEP), ported from TD's UNIT_JEEP
// (tiberiandawn/udata.cpp:691 UnitJeep). GDI-ONLY (TD JEEP ownable = HOUSEF_GOOD | MULTI | JP).
// Wheeled (SPEED_WHEEL -- no Tracked=) light recon car with a small MG TURRET
// (is_turret_equipped=true, unlike the Recon Bike). Fires TDM60mg -- the TD WEAPON_M60MG port
// (BULLET_TD50cal invisible round + WARHEAD_TDSA + Report MGUN11 + directional Anim=GUN-N). The
// turret geometry mirrors RA's OWN small MG car, the Ranger (UnitJeep below): vert 0x30, primary
// 0x30 forward / 0 lateral -- so the muzzle flash seats on the turret barrel with no screenshot
// tuning. NOT a crusher (TD JEEP squash=false) and not gigundo. ANIM_FRAG1 death (TD-authentic --
// RA has it). TD JEEP "lays tracks while moving" (tire marks) has no RA UnitTypeClass param and
// is dropped (cosmetic; it's SPEED_WHEEL so leaves no RA tracks regardless). Internal name TXT_JEEP
// is a placeholder (= RA's "Ranger"); the real "Hum-vee" display comes from rules.ini Name=.
// Stats (Strength 150, Cost 400, Speed=12 = MPH_MEDIUM_FAST, ROT 10, Armor light, TechLevel 2) all
// from rules.ini [TDJEEP].
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
                                      true,         // Is it equipped with a combat turret? (TD JEEP: YES -- small MG turret; Luke confirmed vs TD it rotates, keep visible.)
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

// Tiberian Factions -- TD Nod Buggy (UNIT_TDBGGY), ported from TD's UNIT_BUGGY
// (tiberiandawn/udata.cpp:744 UnitBuggy). NOD-ONLY (TD BGGY ownable = HOUSEF_BAD | MULTI | JP). The
// Nod mirror of the GDI Hum-vee: structurally IDENTICAL ctor (same MG turret, same RA-Ranger
// geometry, same TDM60mg, same ANIM_FRAG1, not crusher/gigundo) -- the only TD-source ctor
// difference is "lays tracks while moving" (Buggy=false vs Jeep=true), which has no RA param, so the
// two ctors are identical here. All the stat differences (Strength 140, Cost 300, TechLevel 4 vs the
// Jeep's 150/400/2) live in rules.ini [TDBGGY]. Internal name TXT_JEEP placeholder; real "Nod Buggy"
// from rules.ini Name=.
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
                                      true,         // Is it equipped with a combat turret? (TD BGGY: YES -- small MG turret; Luke confirmed vs TD it rotates, keep visible.)
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

// Tiberian Factions -- TD APC (UNIT_TDAPC), ported from TD's UNIT_APC
// (tiberiandawn/udata.cpp:907 UnitAPC). GDI-ONLY by faction-canon: TD source sets BOTH
// HOUSEF_GOOD and HOUSEF_BAD (a permissive TD-multiplayer quirk), but the APC is iconically
// GDI in TD gameplay (Nod's mobility roles are the Buggy/Bike/Stealth Tank), so Owner=GoodGuy
// in rules.ini -- consistent with the Medium-Tank(GDI)/Light-Tank(Nod) faction split.
// Tracked transport (SPEED_TRACK), NO turret, can squash infantry, fires TDM60mg (the TD M60
// MG, shared with the Hum-vee/Buggy). Carries 5 (rules.ini Passengers=). Structurally identical
// to RA's own UnitAPC ctor EXCEPT the explosion: TD's APC = ANIM_FRAG2 -> our ported
// ANIM_TDFRAG2 (RA's APC uses ANIM_FRAG1). Transport door-load/unload + AI auto-load are gated
// on the hardcoded UNIT_APC type in unit.cpp/infantry.cpp -- UNIT_TDAPC is added at each of
// those sites (the §3.27 inert-new-type fix) or it would build but never load passengers.
// All stats (Strength 200, Cost 700, TechLevel 4, Speed, Points) live in rules.ini [TDAPC].
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

// Tiberian Factions -- TD Stealth Tank (UNIT_TDSTNK), ported from TD's UNIT_STANK
// (tiberiandawn/udata.cpp UnitSTank). NOD-ONLY (TD STANK ownable = HOUSEF_BAD). The iconic
// Nod cloaking unit. CLOAKING is pure rules.ini (Cloakable=yes) -- RA inherited TD's entire
// cloak system verbatim (TechnoClass::Cloaking_AI / Do_Cloak / Do_Uncloak / the IsScanner
// adjacency-reveal), so NO engine port is needed for the cloak; it decloaks on firing and
// shimmers near an enemy Sensors=yes building (TD-canon defenses). Detection wiring is left at
// the current vanilla state per Luke (2026-06-01) -- not adding Sensors= to the GDI/Nod defenses
// in this pass. Fires TDStnkDragon = TD WEAPON_DRAGON (reused TDTOW homing missile + TDAP) with
// Burst=2 (TD is_twoshooter -- a SEPARATE weapon so the single-shot E3/Bike that share TDDragon
// stay Burst=1). Turret-less (the launcher fires from the hull, all-zero offsets like the Bike /
// V2 Launcher). INVISIBLE-TO-RADAR (ctor param true -- TD STANK doesn't show on the minimap).
// Explosion ANIM_TDFRAG2 (TD STANK = ANIM_FRAG2, same as the tanks). All stats (Strength 110,
// Cost 900, TechLevel 5, Speed 12) in rules.ini [TDSTNK].
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

// Tiberian Factions -- TD Rocket Launcher (UNIT_TDMLRS), ported from TD's UNIT_MLRS
// (tiberiandawn/udata.cpp:854 UnitMLRS, TXT_MLRS = "Rocket Launcher"). GDI-only: TD source sets
// both ownable bits but the prerequisite is STRUCTF_EYE (the GDI Ion-Cannon comm centre), so only
// GDI can build it -> Owner=GoodGuy, a top-tier post-Ion-Cannon siege unit (build level 7).
// TD SOURCE CROSS-WIRING (see docs/td-mlrs-deep-dive.md): UNIT_MLRS renders with the "MSAM" sprite
// (and UNIT_MSAM, the S.S.M. Launcher, renders with "MLRS") -- so this unit bundles the MSAM asset
// despite the TDMLRS IniName. Turreted, with the turret LOCKED forward while moving (TD is_lockturret),
// 2-shooter (Burst=2 on the weapon), tracked. Fires TDMlrsRocket (BULLET_TDSSM2, a long-range homing
// rocket). Death ANIM_ART_EXP1 (TD MLRS = ANIM_ART_EXP1; RA has it natively, no FRAG port). Default
// order MISSION_GUARD (TD MLRS, not HUNT). Stats in rules.ini [TDMLRS]/[TDMlrsRocket]/[TDSSM2].
static UnitTypeClass const UnitTdMlrs(UNIT_TDMLRS,
                                      TXT_LTANK,     // NAME: placeholder (RA has no "Rocket Launcher" string; HD display via rules.ini Name=).
                                      "TDMLRS",      // NAME: IniName (sprite bundled from the MSAM asset -- TD cross-wiring).
                                      ANIM_ART_EXP1, // EXPLOSION: TD MLRS death (ANIM_ART_EXP1 -- RA has it natively).
                                      REMAP_NORMAL,  // Sidebar remap logic.
                                      0x0010,        // Vertical offset (render calibration -- small lift; tune to the MSAM launcher).
                                      0x0000,        // Primary weapon offset along turret centerline (was 0x00C0 = the MTANK gun barrel, far too forward for a rear launcher; spawn at the launcher, screenshot-tune).
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

// Tiberian Factions -- TD SSM Launcher (UNIT_TDMSAM), ported from TD's UNIT_MSAM
// (tiberiandawn/udata.cpp:477 UnitSAM, TXT_MSAM = "S.S.M. Launcher"). NOD-ONLY (HOUSEF_BAD).
// TD SOURCE CROSS-WIRING (docs/td-mlrs-deep-dive.md): UNIT_MSAM renders with the "MLRS" sprite
// (and UNIT_MLRS, the Rocket Launcher, renders with "MSAM") -- so this unit bundles the MLRS
// asset despite the TDMSAM IniName. Turreted, turret LOCKED forward while moving (body rotates
// to fire; the on-stop settle is the same TD-authentic lock-turret transition as the MLRS).
// NOT a two-shooter (single big rocket). Fires TDHonestJohn (BULLET_TDMISSILE -- a fast,
// NON-homing, accurate, long-range (10) napalm rocket with its own TDMISSILE sprite). Death
// ANIM_TDFRAG2. Temple-gated for Nod (Prerequisite=weap,atek -- atek=TDTMPL; mirrors the GDI
// MLRS gated on the Ion Cannon/Eye). Stats in rules.ini [TDMSAM]/[TDHonestJohn]/[TDMissile].
static UnitTypeClass const UnitTdMsam(UNIT_TDMSAM,
                                      TXT_LTANK,     // NAME: placeholder (RA has no "SSM Launcher" string; HD display via rules.ini Name=).
                                      "TDMSAM",      // NAME: IniName (sprite bundled from the MLRS asset -- TD cross-wiring).
                                      ANIM_TDFRAG2,  // EXPLOSION: TD MSAM death (TD ctor = ANIM_FRAG2 -> our ported ANIM_TDFRAG2).
                                      REMAP_NORMAL,  // Sidebar remap logic.
                                      0x0010,        // Vertical offset (small lift; same family as the MLRS launcher, screenshot-tune).
                                      0x0000,        // Primary weapon offset (rear launcher -- spawn at the launcher, not far forward; screenshot-tune).
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

// Tiberian Factions -- TD Artillery (UNIT_TDARTY), ported from TD's UNIT_ARTY
// (tiberiandawn/udata.cpp UnitArty, TXT_ARTY = "Artillery"). NOD-ONLY (HOUSEF_BAD). Named
// "Nod Artillery" (rules.ini) to disambiguate from RA's own [ARTY] "Artillery". TURRET-LESS
// (the body aims; very slow ROT 2). No building prereq beyond the war factory (TD STRUCTF_NONE,
// build level 6). Cheap (450) and fragile (75 HP) but high damage (150) -- a glass-cannon
// bombardment unit. Fires TD155mm (BULLET_TDHESHELL -- an ARCING, faceless 155mm HE shell that
// reuses the 120MM sprite, WARHEAD_TDHE, ANIM_ART_EXP1 impact). Death ANIM_ART_EXP1 (RA-native).
// Turret-less gun offsets follow the Bike pattern (small forward muzzle; screenshot-tune).
// Stats in rules.ini [TDARTY]/[TD155mm]/[TDHEShell].
static UnitTypeClass const UnitTdArty(UNIT_TDARTY,
                                      TXT_LTANK,     // NAME: placeholder (RA's "Artillery" is its own unit; HD display via rules.ini Name=).
                                      "TDARTY",      // NAME: IniName.
                                      ANIM_ART_EXP1, // EXPLOSION: TD ARTY death (ANIM_ART_EXP1 -- RA-native).
                                      REMAP_NORMAL,  // Sidebar remap logic.
                                      0x0010,        // Vertical offset (small; turret-less gun, screenshot-tune).
                                      0x0050,        // Primary weapon offset along body centerline (forward barrel muzzle; screenshot-tune).
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

// Tiberian Factions -- TD Visceroid (UNIT_TDVICE), ported from TD's UNIT_VICE
// (tiberiandawn/udata.cpp UnitVisceroid, TXT_VISCEROID "Visceroid"). NOT a buildable
// faction unit -- it is a Tiberium creature that SPAWNS when an infantry dies in Tiberium
// (see the infantry.cpp tiberium-death hook). Tracked, turret-LESS, squashes infantry,
// INVISIBLE to radar, INSIGNIFICANT (no "unit lost" announce), CONSTANT ANIMATION (a writhing
// blob), MISSION_HUNT (mindlessly attacks everything nearby). Fires WEAPON_TDCHEM -- we already
// ship [TDChemspray] (the E5 Chem Warrior spray), so the visceroid reuses that whole weapon
// chain. HEALS while on a Tiberium cell (unit.cpp AI hook, mirroring TD UNIT.CPP:434). Stats
// (Strength 150, Cost 800, Sight 4, ARMOR_WOOD, MPH_MEDIUM, ROT 5) live in rules.ini [TDVICE].
// Death ANIM_NAPALM2 (TD-authentic).
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

/*
**  Dynamic constructor for mod-defined unit types. Used by the [NewUnits]
**  index in rules.ini — counterpart to BuildingTypeClass's 2-arg constructor
**  at bdata.cpp:2846. Same trick: the heap slot we're being allocated into
**  is Count() - 1 because operator new has already appended us by the time
**  this init list runs. Logic=<vanilla-IniName> in Read_INI then aliases
**  Type + IsXxx flags + ImageData to a vanilla donor.
*/
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

/*
**  Name-based lookup across the full UnitTypes heap, including mod entries
**  past UNIT_COUNT. From_Name only walks the vanilla enum range and can't
**  see [NewUnits] entries. Mirrors BuildingTypeClass::As_Pointer.
*/
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

// TS-spike -- Tiberian Sun Hover MLRS (UNIT_TSHVR), TS rules [HVR]. GDI-only.
// Turreted (the rotating missile rack; TS Turret=yes) but light: NOT a crusher,
// NOT gigundo. Explosion ANIM_FRAG1 (light-vehicle death, RA-native). Render
// geometry starts from the 2TNK reference (vert 0x0030, primary 0x00C0) -- tune
// against the voxel-rendered sprite by screenshot. Art is the first voxel-rendered
// HD tileset (TSHVR.ZIP, 32 body + 32 turret frames); no classic SHP exists, so
// One_Time donors 2TNK's ImageData. Fires WEAPON_TSHOVERMISSILE (TDSSM AA+AG chain).
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

/*
**  SMCV (Soviet MCV) and TDNMCV (Nod MCV) — twins of the Allied and GDI MCVs. Neither source
**  game drew a second MCV sprite, so both take their art from the twin via Image= in
**  rules.ini. They exist as their own types so the MCV carries the faction it will deploy
**  into: an MCV built from a captured enemy factory is that faction's MCV, and deploys that
**  faction's construction yard, which is what carries a captured tech tree forward.
*/
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
    new UnitTypeClass(UnitMCV);         // UNIT_AMCV
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
    // Tiberian Factions mod — fully-separated TD-source unit ports.
    new UnitTypeClass(UnitTdMcv);     // UNIT_TDGMCV
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
    new UnitTypeClass(UnitTsHvr);     // UNIT_TSHVR (TS-spike Hover MLRS)
    new UnitTypeClass(UnitSovietMcv); // UNIT_SMCV  (Soviet MCV)
    new UnitTypeClass(UnitNodMcv);    // UNIT_TDNMCV (Nod MCV)
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

    // TS-spike: TSHVR ships no classic SHP (HD-only, voxel-rendered tileset).
    // A NULL ImageData makes Draw_It bail with width=height=0, so donor 2TNK's
    // pointer; the launcher then renders the real TSHVR frames by IniName from
    // RA_UNITS.XML (the same NULL-guard pattern as bdata's _td_bdonors block).
    {
        UnitTypeClass& hvr = As_Reference(UNIT_TSHVR);
        if (hvr.ImageData == NULL) {
            ((void const*&)hvr.ImageData) = As_Reference(UNIT_MTANK2).ImageData;
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
    if (Type == UNIT_HARVESTER || Type == UNIT_TDHARV) {
        return (7);
    }

    if (Type == UNIT_MINELAYER) {
        return (MaxAmmo);
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
    // Tiberian Factions: the TD Hum-vee/Buggy are small MG cars like RA's Ranger
    // (UNIT_JEEP) -- seat their turret with the same upward nudge so it sits on
    // the hull instead of the body centre. Tune the delta by screenshot if the
    // TD sprite's turret pivot differs from the Ranger's.
    case UNIT_TDJEEP:
    case UNIT_TDBGGY:
        y -= 4;
        break;

    case UNIT_MGG:
    // Tiberian Factions: the _adjust table above is the ORIGINAL TD MLRS/MSAM turret-offset
    // (see this function's header comment) -- it seats a rear-mounted launcher onto the chassis
    // per facing. Our TD Rocket Launcher uses the MSAM sprite, so it wants exactly this table;
    // without it the launcher draws at the body centre (too far forward). Tune by screenshot if
    // the HD sprite's pivot differs from the classic offsets.
    case UNIT_TDMLRS:
    case UNIT_TDMSAM: // TD SSM Launcher uses the MLRS sprite -- also a rear-mounted launcher; same offset table.
        index = Dir_To_32(dir);
        x += _adjust[index].X;
        y += _adjust[index].Y;
        break;

    case UNIT_TSHVR: { // TS Hover MLRS: rack rides aft on the long hover platform.
                       // Geometric seat (the naval turret pattern): push straight
                       // rearward along the hull axis with tilt compensation --
                       // consistent at every facing, unlike the MSAM hand table
                       // (whose lateral components suit the classic chassis only).
        // Precomputed aft push (ground distance 18) projected with the voxel render
        // camera's own foreshortening (13/16 vertical), so the seat is identical
        // relative to the hull at all 32 facings. (Normal_Move_Point's classic
        // vertical halving overshot E/W relative to N/S against this art.)
        static const signed char _aft_x[32] = {0,  -2, -3, -5, -6, -7, -8, -9, -9, -9, -8,
                                               -7, -6, -5, -3, -2, 0,  2,  3,  5,  6,  7,
                                               8,  9,  9,  9,  8,  7,  6,  5,  3,  2};
        static const signed char _aft_y[32] = {7,  7,  7,  6,  5,  4,  3,  1,  0,  -1, -3,
                                               -4, -5, -6, -7, -7, -7, -7, -7, -6, -5, -4,
                                               -3, -1, 0,  1,  3,  4,  5,  6,  7,  7};
        index = Dir_To_32(dir);
        x += _aft_x[index];
        y += _aft_y[index];
        break;
    }

    default:
        break;
    }
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
        Speed = ini.Get_Bool(IniName, "Tracked", (Speed == SPEED_TRACK)) ? SPEED_TRACK : SPEED_WHEEL;
        // TS-spike: Hover=yes overrides the binary Tracked choice with the amphibious
        // hover locomotor (land + water passability from the ground table's Hover= row).
        if (ini.Get_Bool(IniName, "Hover", (Speed == SPEED_HOVER))) {
            Speed = SPEED_HOVER;
        }

        /*
        **  Logic=<vanilla-IniName> aliases this entry's runtime Type discriminant
        **  to a vanilla UnitType. Engine dispatch (Mission_Unload's `case UNIT_AMCV`,
        **  Try_To_Deploy's `*this == UNIT_AMCV`, AI ownership scans, etc.) then
        **  treats this custom unit as the vanilla type. Mirrors the building-side
        **  alias at bdata.cpp:3847. ImageData inheritance is critical for mod
        **  entries — One_Time only loads SHPs for vanilla heap slots, so without
        **  copying the donor's pointer the launcher renders width=height=0.
        */
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
                // Weapon fall-through follows the bdata.cpp pattern: explicit
                // Primary=/Secondary= in this entry's INI section ran during
                // TechnoTypeClass::Read_INI above and already populated these
                // pointers if set. Only fall back to donor when omitted.
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
