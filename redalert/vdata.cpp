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

/* $Header: /CounterStrike/VDATA.CPP 1     3/03/97 10:26a Joe_bostic $ */
/***********************************************************************************************
 ***              C O N F I D E N T I A L  ---  W E S T W O O D  S T U D I O S               ***
 ***********************************************************************************************
 *                                                                                             *
 *                 Project Name : Command & Conquer                                            *
 *                                                                                             *
 *                    File Name : VDATA.CPP                                                    *
 *                                                                                             *
 *                   Programmer : Joe L. Bostic                                                *
 *                                                                                             *
 *                   Start Date : 03/13/96                                                     *
 *                                                                                             *
 *                  Last Update : July 9, 1996 [JLB]                                           *
 *                                                                                             *
 *---------------------------------------------------------------------------------------------*
 * Functions:                                                                                  *
 *   VesselTypeClass::As_Reference -- Converts a vessel type into a VesselTypeClass reference. *
 *   VesselTypeClass::Create_And_Place -- Creates a vessel and places it at location.          *
 *   VesselTypeClass::Create_One_Of -- Creates a vessel object that matches this vessel type.  *
 *   VesselTypeClass::Dimensions -- Fetches the pixel width and height of this vessel type.    *
 *   VesselTypeClass::Display -- Displays a generic representation of this vessel type.        *
 *   VesselTypeClass::From_Name -- Converts a name into a vessel type.                         *
 *   VesselTypeClass::Init_Heap -- Initialize the vessel heap.                                 *
 *   VesselTypeClass::One_Time -- Performs one time initialization for vessel types.           *
 *   VesselTypeClass::Overlap_List -- Figures the overlap list for the vessel type.            *
 *   VesselTypeClass::Prep_For_Add -- Adds vessel types to the scenario editor object list.    *
 *   VesselTypeClass::Turret_Adjust -- Adjust turret offset according to facing specified.     *
 *   VesselTypeClass::VesselTypeClass -- Constructor for naval vessel types.                   *
 *   VesselTypeClass::Who_Can_Build_Me -- Fetches pointer to available factory for this vessel.*
 *   VesselTypeClass::operator delete -- Returns a vessel type object back to the memory pool. *
 *   VesselTypeClass::operator new -- Allocate a vessel type object from the special memory poo*
 * - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

#include "function.h"

// Submarine
static VesselTypeClass const VesselSubmarine(VESSEL_SS,
                                             TXT_SS,      // NAME:			Text name of this unit type.
                                             "SS",        // NAME:			Text name of this unit type.
                                             ANIM_FBALL1, // EXPLOSION:	Type of explosion when destroyed.
                                             0x0000,      //	Vertical offset.
                                             0x0000,      // Primary weapon offset along turret centerline.
                                             0x0000,      // Primary weapon lateral offset along turret centerline.
                                             0x0000,      // Secondary weapon offset along turret centerline.
                                             0x0000,      // Secondary weapon lateral offset along turret centerling.
                                             false,       // Only has eight facings?
                                             true,        // Always use the given name for the vehicle?
                                             false,       // Is it equipped with a combat turret?
                                             8,           // Rotation stages.
                                             14           // Turret center offset along body centerline.
);

// Destroyer
static VesselTypeClass const VesselDestroyer(VESSEL_DD,
                                             TXT_DD,      // NAME:			Text name of this unit type.
                                             "DD",        // NAME:			Text name of this unit type.
                                             ANIM_FBALL1, // EXPLOSION:	Type of explosion when destroyed.
                                             0x0000,      //	Vertical offset.
                                             0x0000,      // Primary weapon offset along turret centerline.
                                             0x0000,      // Primary weapon lateral offset along turret centerline.
                                             0x0000,      // Secondary weapon offset along turret centerline.
                                             0x0000,      // Secondary weapon lateral offset along turret centerling.
                                             false,       // Only has eight facings?
                                             true,        // Always use the given name for the vehicle?
                                             true,        // Is it equipped with a combat turret?
                                             8,           // Rotation stages.
                                             14           // Turret center offset along body centerline.
);

// Cruiser
static VesselTypeClass const VesselCruiser(VESSEL_CA,
                                           TXT_CA,      // NAME:			Text name of this unit type.
                                           "CA",        // NAME:			Text name of this unit type.
                                           ANIM_FBALL1, // EXPLOSION:	Type of explosion when destroyed.
                                           0x0000,      //	Vertical offset.
                                           0x0000,      // Primary weapon offset along turret centerline.
                                           0x0000,      // Primary weapon lateral offset along turret centerline.
                                           0x0000,      // Secondary weapon offset along turret centerline.
                                           0x0000,      // Secondary weapon lateral offset along turret centerling.
                                           false,       // Only has eight facings?
                                           true,        // Always use the given name for the vehicle?
                                           true,        // Is it equipped with a combat turret?
                                           8,           // Rotation stages.
                                           14           // Turret center offset along body centerline.
);

// Transport
static VesselTypeClass const VesselTransport(VESSEL_TRANSPORT,
                                             TXT_TRANSPORT, // NAME:			Text name of this unit type.
                                             "LST",         // NAME:			Text name of this unit type.
                                             ANIM_FBALL1,   // EXPLOSION:	Type of explosion when destroyed.
                                             0x0000,        //	Vertical offset.
                                             0x0000,        // Primary weapon offset along turret centerline.
                                             0x0000,        // Primary weapon lateral offset along turret centerline.
                                             0x0000,        // Secondary weapon offset along turret centerline.
                                             0x0000,        // Secondary weapon lateral offset along turret centerling.
                                             false,         // Only has eight facings?
                                             true,          // Always use the given name for the vehicle?
                                             false,         // Is it equipped with a combat turret?
                                             0,             // Rotation stages.
                                             0              // Turret center offset along body centerline.
);

// Gun Boat
static VesselTypeClass const VesselPTBoat(VESSEL_PT,
                                          TXT_PT,      // NAME:			Text name of this unit type.
                                          "PT",        // NAME:			Text name of this unit type.
                                          ANIM_FBALL1, // EXPLOSION:	Type of explosion when destroyed.
                                          0x0000,      //	Vertical offset.
                                          0x0000,      // Primary weapon offset along turret centerline.
                                          0x0000,      // Primary weapon lateral offset along turret centerline.
                                          0x0000,      // Secondary weapon offset along turret centerline.
                                          0x0000,      // Secondary weapon lateral offset along turret centerling.
                                          false,       // Only has eight facings?
                                          true,        // Always use the given name for the vehicle?
                                          true,        // Is it equipped with a combat turret?
                                          8,           // Rotation stages.
                                          14           // Turret center offset along body centerline.
);

#ifdef FIXIT_CSII //	checked - ajw 9/28/98
// Missile Submarine
static VesselTypeClass const VesselMissileSubmarine(VESSEL_MISSILESUB,
                                                    TXT_MISSILESUB, // NAME:			Text name of this unit type.
                                                    "MSUB",         // NAME:			Text name of this unit type.
                                                    ANIM_FBALL1,    // EXPLOSION:	Type of explosion when destroyed.
                                                    0x0000,         //	Vertical offset.
                                                    0x0000,         // Primary weapon offset along turret centerline.
                                                    0x0000, // Primary weapon lateral offset along turret centerline.
                                                    0x0000, // Secondary weapon offset along turret centerline.
                                                    0x0000, // Secondary weapon lateral offset along turret centerling.
                                                    false,  // Only has eight facings?
                                                    true,   // Always use the given name for the vehicle?
                                                    false,  // Is it equipped with a combat turret?
                                                    8,      // Rotation stages.
                                                    14      // Turret center offset along body centerline.
);
#endif

#ifdef FIXIT_CARRIER //	checked - ajw 9/28/98
// Transport
static VesselTypeClass const VesselCarrier(VESSEL_CARRIER,
                                           TXT_CARRIER, // NAME:			Text name of this unit type.
                                           "CARR",      // NAME:			Text name of this unit type.
                                           ANIM_FBALL1, // EXPLOSION:	Type of explosion when destroyed.
                                           0x0000,      //	Vertical offset.
                                           0x0000,      // Primary weapon offset along turret centerline.
                                           0x0000,      // Primary weapon lateral offset along turret centerline.
                                           0x0000,      // Secondary weapon offset along turret centerline.
                                           0x0000,      // Secondary weapon lateral offset along turret centerling.
                                           false,       // Only has eight facings?
                                           true,        // Always use the given name for the vehicle?
                                           false,       // Is it equipped with a combat turret?
                                           0,           // Rotation stages.
                                           0            // Turret center offset along body centerline.
);
#endif

// Nod Missile Sub (VESSEL_TDMSUB) -- clone of the Soviet MSUB (Aftermath), Nod's shore-bombardment
// sub (SubSCUD), Temple-gated, from the Nod Sub Pen. Own art copy (tdmsub tileset). "Nod navy =
// the Soviet one" (Luke 2026-07-03). All params mirror VesselMissileSubmarine exactly.
static VesselTypeClass const VesselTdMSub(VESSEL_TDMSUB,
                                          TXT_MISSILESUB, // Text name (placeholder -- HD name via rules.ini Name=).
                                          "TDMSUB",       // INI name (own art: tdmsub frames).
                                          ANIM_FBALL1,    // Explosion when destroyed.
                                          0x0000,         // Vertical offset.
                                          0x0000,         // Primary weapon offset.
                                          0x0000,         // Primary weapon lateral offset.
                                          0x0000,         // Secondary weapon offset.
                                          0x0000,         // Secondary weapon lateral offset.
                                          false,          // Only has eight facings?
                                          true,           // Always use the given name?
                                          false,          // Combat turret equipped? (no -- sub)
                                          8,              // Rotation stages.
                                          14              // Turret center offset.
);

// Tiberian Factions (v4.0) -- TD Gunboat (VESSEL_TDGUNBOAT), GDI surface combatant. Its OWN vessel
// type (NOT RA's PT/DD reskinned), ported from TD's scripted-only UNIT_GUNBOAT. Turret-equipped like
// the PT/DD. Fires TDTomahawk (a TD homing missile, BULLET_TDTOW + WARHEAD_TDAP) as its anti-surface/
// anti-shore punch + a DepthCharge ASW secondary (the Allied Destroyer's anti-sub weapon, per Luke)
// + Sensors so it detects/hunts Nod's cloaked subs. Art = TDBOAT (TD-Assets). Built from the
// owner-opened Allied Shipyard. Donor ImageData = VESSEL_PT (NULL-guard). See docs/navy-4.0-design.md.
static VesselTypeClass const VesselTdGunBoat(VESSEL_TDGUNBOAT,
                                             TXT_PT,      // Text name (placeholder -- HD name via rules.ini Name=).
                                             "TDBOAT",    // INI name (TD-prefixed; matches the TDBOAT tileset).
                                             ANIM_FBALL1, // Explosion when destroyed.
                                             0x0000,      // Vertical offset.
                                             0x0000,      // Primary weapon offset along turret centerline.
                                             0x0000,      // Primary weapon lateral offset.
                                             0x0000,      // Secondary weapon offset.
                                             0x0000,      // Secondary weapon lateral offset.
                                             false,       // Only has eight facings?
                                             true,        // Always use the given name?
                                             true,        // Combat turret equipped? ON (Luke,
                                                          //   2026-07-03): wears the RA SSAM missile
                                                          //   box (Draw_It), seated on the dot-marked
                                                          //   foredeck mount, firing TDTomahawk.
                                             8,           // Rotation stages.
                                             14           // Turret center offset (overridden by the
                                                          //   explicit VESSEL_TDGUNBOAT Turret_Adjust case).
);

// Tiberian Factions (v4.0) -- TD Hovercraft transport (VESSEL_TDLST), shared GDI+Nod amphibious
// transport. Its OWN vessel type (NOT RA's LST reskinned), TD's UNIT_HOVER. Modeled on
// VesselTransport (no turret, rotation 0 -- faces one way like the RA LST). Carries 5. Art = TDLST
// (TD-Assets). Donor ImageData = VESSEL_TRANSPORT (NULL-guard). See docs/navy-4.0-design.md.
static VesselTypeClass const VesselTdLST(VESSEL_TDLST,
                                         TXT_TRANSPORT, // Text name (placeholder -- HD name via rules.ini Name=).
                                         "TDLST",       // INI name (TD-prefixed; matches the TDLST tileset).
                                         ANIM_FBALL1,   // Explosion when destroyed.
                                         0x0000,        // Vertical offset.
                                         0x0000,        // Primary weapon offset.
                                         0x0000,        // Primary weapon lateral offset.
                                         0x0000,        // Secondary weapon offset.
                                         0x0000,        // Secondary weapon lateral offset.
                                         false,         // Only has eight facings?
                                         true,          // Always use the given name?
                                         false,         // Combat turret equipped? (no -- transport)
                                         0,             // Rotation stages (0 -- like the RA transport).
                                         0              // Turret center offset.
);

// Tiberian Factions (v4.0) -- Nod Obelisk Attack Sub (VESSEL_TDOBLISUB). Its OWN vessel type: a
// cloakable sub that surfaces and fires the TD Obelisk laser (close-range, slow ROF, high per-shot
// damage -- "deadly but has to commit"). Temple-gated. No turret. Uses the RA MISSILE-SUB hull art
// (TDOBLISUB.ZIP = a renamed copy of MSUB frames) -- the missile-pod deck reads as the armed laser
// emitter (the obelisk-tip turret approach was dropped). The Obelisk laser fires from the pod area.
// Donor ImageData = VESSEL_SS (NULL-guard fallback). See docs/navy-4.0-design.md.
static VesselTypeClass const VesselTdObeliskSub(VESSEL_TDOBLISUB,
                                                TXT_SS,      // Text name (placeholder -- HD name via rules.ini Name=).
                                                "TDOBLISUB", // INI name.
                                                ANIM_FBALL1, // Explosion when destroyed.
                                                0x0000,      // Vertical offset.
                                                0x0000,      // Primary weapon offset.
                                                0x0000,      // Primary weapon lateral offset.
                                                0x0000,      // Secondary weapon offset.
                                                0x0000,      // Secondary weapon lateral offset.
                                                false,       // Only has eight facings?
                                                true,        // Always use the given name?
                                                false,       // Combat turret equipped? (no -- sub)
                                                8,           // Rotation stages.
                                                14           // Turret center offset.
);

// Tiberian Factions (v4.0) -- Nod Submarine (VESSEL_TDNSUB). Its OWN vessel type (clone of the
// Soviet SS, NOT the SS owner-opened), so it has its own art copy and is independently reskinnable.
// Same hull/weapon as the Soviet sub (TorpTube, cloakable) per the accepted RA-sub-hull decision;
// Nod's distinction is the Obelisk Sub. Owner=BadGuy (rules.ini). Donor ImageData = VESSEL_SS.
static VesselTypeClass const VesselTdNodSub(VESSEL_TDNSUB,
                                            TXT_SS,      // Text name (placeholder -- HD name via rules.ini Name=).
                                            "TDNSUB",    // INI name (own art: tdnsub frames).
                                            ANIM_FBALL1, // Explosion when destroyed.
                                            0x0000,      // Vertical offset.
                                            0x0000,      // Primary weapon offset.
                                            0x0000,      // Primary weapon lateral offset.
                                            0x0000,      // Secondary weapon offset.
                                            0x0000,      // Secondary weapon lateral offset.
                                            false,       // Only has eight facings?
                                            true,        // Always use the given name?
                                            false,       // Combat turret equipped? (no -- sub)
                                            8,           // Rotation stages.
                                            14           // Turret center offset.
);

// Tiberian Factions (v4.0) -- GDI surface fleet: fully-separated CLONES of the three Allied ships
// (PT/DD/CA), Owner=GoodGuy, built from the GDI Naval Yard. KEEP IsTurretEquipped=true so each
// renders the native spinning turret (Draw_It draws MGUN/SSAM/TURR by name -- the turret art is a
// global launcher resource, NOT part of the hull ZIP, so the clones get spinning turrets for free).
// Own copied hull art (TDPT/TDDD/TDCA tilesets); donor ImageData = the RA original (NULL-guard).
// All other params mirror the templated RA ship exactly. See docs/naval-art-3d-pipeline-handover.md.

// GDI Gunboat (clone of RA PT -- light, MGUN turret).
static VesselTypeClass const VesselTdPT(VESSEL_TDPT,
                                        TXT_PT,      // Text name (placeholder -- real name via ModText.csv later).
                                        "TDPT",      // INI name (own art: tdpt frames).
                                        ANIM_FBALL1, // Explosion when destroyed.
                                        0x0000,      // Vertical offset.
                                        0x0000,      // Primary weapon offset.
                                        0x0000,      // Primary weapon lateral offset.
                                        0x0000,      // Secondary weapon offset.
                                        0x0000,      // Secondary weapon lateral offset.
                                        false,       // Only has eight facings?
                                        true,        // Always use the given name?
                                        true,        // Combat turret equipped? YES -- native MGUN turret.
                                        8,           // Rotation stages.
                                        14           // Turret center offset.
);

// GDI Destroyer (clone of RA DD -- medium, SSAM turret).
static VesselTypeClass const VesselTdDD(VESSEL_TDDD,
                                        TXT_DD,      // Text name (placeholder -- real name via ModText.csv later).
                                        "TDDD",      // INI name (own art: tddd frames).
                                        ANIM_FBALL1, // Explosion when destroyed.
                                        0x0000,      // Vertical offset.
                                        0x0000,      // Primary weapon offset.
                                        0x0000,      // Primary weapon lateral offset.
                                        0x0000,      // Secondary weapon offset.
                                        0x0000,      // Secondary weapon lateral offset.
                                        false,       // Only has eight facings?
                                        true,        // Always use the given name?
                                        true,        // Combat turret equipped? YES -- native SSAM turret.
                                        8,           // Rotation stages.
                                        14           // Turret center offset.
);

// GDI Cruiser (clone of RA CA -- heavy, TURR twin-gun turret).
static VesselTypeClass const VesselTdCA(VESSEL_TDCA,
                                        TXT_CA,      // Text name (placeholder -- real name via ModText.csv later).
                                        "TDCA",      // INI name (own art: tdca frames).
                                        ANIM_FBALL1, // Explosion when destroyed.
                                        0x0000,      // Vertical offset.
                                        0x0000,      // Primary weapon offset.
                                        0x0000,      // Primary weapon lateral offset.
                                        0x0000,      // Secondary weapon offset.
                                        0x0000,      // Secondary weapon lateral offset.
                                        false,       // Only has eight facings?
                                        true,        // Always use the given name?
                                        true,        // Combat turret equipped? YES -- native TURR turret.
                                        8,           // Rotation stages.
                                        14           // Turret center offset.
);

/***********************************************************************************************
 * VesselTypeClass::VesselTypeClass -- Constructor for unit types.                             *
 *                                                                                             *
 *    This is the constructor for the vessel static data. Each vessels is assign a specific    *
 *    variation. This class elaborates what the variation actually is.                         *
 *                                                                                             *
 * INPUT:   bla bla bla... see below                                                           *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/14/1996 JLB : Created                                                                  *
 *=============================================================================================*/
VesselTypeClass::VesselTypeClass(VesselType type,
                                 int name,
                                 char const* ininame,
                                 AnimType exp,
                                 int verticaloffset,
                                 int primaryoffset,
                                 int primarylateral,
                                 int secondaryoffset,
                                 int secondarylateral,
                                 bool is_eight,
                                 bool is_nominal,
                                 bool is_turret_equipped,
                                 int rotation,
                                 int toffset)
    : TechnoTypeClass(RTTI_VESSELTYPE,
                      int(type),
                      name,
                      ininame,
                      REMAP_NORMAL,
                      verticaloffset,
                      primaryoffset,
                      primarylateral,
                      secondaryoffset,
                      secondarylateral,
                      is_nominal,
                      false,
                      true,
                      true,
                      false,
                      false,
                      false,
                      is_turret_equipped,
                      true,
                      true,
                      rotation,
                      SPEED_FLOAT)
    , IsPieceOfEight(is_eight)
    , Type(type)
    , TurretOffset(toffset)
    , Mission(MISSION_GUARD)
    , Explosion(exp)
    , MaxSize(0)
{
    /*
    **	Forced vessel overrides from the default.
    */
    IsCrew = false;
    Speed = SPEED_FLOAT;
    IsScanner = true;
}

/***********************************************************************************************
 * VesselTypeClass::operator new -- Allocate a vessel type object from the special memory pool *
 *                                                                                             *
 *    This will allocate a vessel type class object from the memory pool.                      *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the allocated vessel type class object. If memory in the *
 *          special heap has been exhaused, then NULL will be returned.                        *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void* VesselTypeClass::operator new(size_t) noexcept
{
    return (VesselTypes.Alloc());
}

/***********************************************************************************************
 * VesselTypeClass::operator delete -- Returns a vessel type object back to the memory pool.   *
 *                                                                                             *
 *    This will return a previously allocated vessel object back to the special pool from      *
 *    whence it was originally allocated.                                                      *
 *                                                                                             *
 * INPUT:   pointer  -- Pointer to the vessel type object to return to the pool.               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void VesselTypeClass::operator delete(void* pointer)
{
    VesselTypes.Free((VesselTypeClass*)pointer);
}

/***********************************************************************************************
 * VesselTypeClass::Init_Heap -- Initialize the vessel heap.                                   *
 *                                                                                             *
 *    This will pre-allocate all the vessel types required.                                    *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Only call this routine once and do so before processing the rules.ini file.     *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void VesselTypeClass::Init_Heap(void)
{
    /*
    **	These vessel type class objects must be allocated in the exact order that they
    **	are specified in the VesselType enumeration. This is necessary because the heap
    **	allocation block index serves double duty as the type number index.
    */
    new VesselTypeClass(VesselSubmarine);        //	VESSEL_SS
    new VesselTypeClass(VesselDestroyer);        //	VESSEL_DD
    new VesselTypeClass(VesselCruiser);          // VESSEL_CA
    new VesselTypeClass(VesselTransport);        // VESSEL_TRANSPORT
    new VesselTypeClass(VesselPTBoat);           // VESSEL_PT
#ifdef FIXIT_CSII                                //	checked - ajw 9/28/98
    new VesselTypeClass(VesselMissileSubmarine); // VESSEL_MISSILESUB
#endif
#ifdef FIXIT_CARRIER                    //	checked - ajw 9/28/98
    new VesselTypeClass(VesselCarrier); // VESSEL_CARRIER
#endif
    new VesselTypeClass(VesselTdGunBoat); // VESSEL_TDGUNBOAT (MUST follow carrier to match the enum slot)
    new VesselTypeClass(VesselTdLST);       // VESSEL_TDLST (enum order)
    new VesselTypeClass(VesselTdObeliskSub); // VESSEL_TDOBLISUB (enum order)
    new VesselTypeClass(VesselTdNodSub);     // VESSEL_TDNSUB (enum order)
    new VesselTypeClass(VesselTdPT);         // VESSEL_TDPT  (enum order -- GDI gunboat clone)
    new VesselTypeClass(VesselTdDD);         // VESSEL_TDDD  (enum order -- GDI destroyer clone)
    new VesselTypeClass(VesselTdCA);         // VESSEL_TDCA  (enum order -- GDI cruiser clone)
    new VesselTypeClass(VesselTdMSub);       // VESSEL_TDMSUB (enum order -- Nod missile sub clone)
}

/***********************************************************************************************
 * VesselTypeClass::As_Reference -- Converts a vessel type into a VesselTypeClass reference.   *
 *                                                                                             *
 *    This routine will fetch a reference to the vessel type that corresponds to the vessel    *
 *    type specified.                                                                          *
 *                                                                                             *
 * INPUT:   type  -- The vessel type number to convert.                                        *
 *                                                                                             *
 * OUTPUT:  Returns with a reference to the vessel type class that corresponds to the vessel   *
 *          type specified.                                                                    *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
VesselTypeClass& VesselTypeClass::As_Reference(VesselType type)
{
    return (*VesselTypes.Ptr(type));
}

#ifdef NEVER
/***********************************************************************************************
 * VesselTypeClass::Who_Can_Build_Me -- Fetches pointer to available factory for this vessel.  *
 *                                                                                             *
 *    Use this routine to fetch a pointer to the vessel factory that can build this vessel     *
 *    type.                                                                                    *
 *                                                                                             *
 * INPUT:   intheory -- If true, then this indicates that if the factory is currently          *
 *                      busy doing other things, this won't make in ineligible for searching. *
 *                      Typical use of this is by the sidebar logic which needs only to know   *
 *                      if theoretical production is allowed.                                  *
 *                                                                                             *
 *          legal    -- If true, then the buildings are checked for specific legality when     *
 *                      being scanned. For building placement, this is usually false, for      *
 *                      sidebar button adding, this is usually true.                           *
 *                                                                                             *
 *          house    -- The owner of the unit to be produced. This has an effect of legality.  *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the factory (building) that can produce this vessel type.*
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
BuildingClass* VesselTypeClass::Who_Can_Build_Me(bool intheory, bool legal, HousesType house) const
{
    BuildingClass* anybuilding = NULL;

    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass* building = Buildings.Ptr(index);
        assert(building != NULL);

        if (!building->IsInLimbo && building->House->Class->House == house
            && building->Class->ToBuild == RTTI_VESSELTYPE && building->Mission != MISSION_DECONSTRUCTION
            && ((1L << building->ActLike) & Ownable) && (!legal || building->House->Can_Build(Type, building->ActLike))
            && (intheory || !building->In_Radio_Contact())) {

            if (building->IsLeader)
                return (building);
            anybuilding = building;
        }
    }
    return (anybuilding);
}
#endif

/***********************************************************************************************
 * VesselTypeClass::Display -- Displays a generic representation of this vessel type.          *
 *                                                                                             *
 *    This routine is used by the scenario editor to display a representation of this          *
 *    vessel type in the object placement dialog.                                              *
 *                                                                                             *
 * INPUT:   x,y      -- Pixel coordinate to render the center of this vessel type to.          *
 *                                                                                             *
 *          window   -- The window to clip the shape to. The pixel coordinates are relative    *
 *                      to this window.                                                        *
 *                                                                                             *
 *          house    -- The owner of the vessel. This is used to give the vessel its color.    *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
#ifdef SCENARIO_EDITOR
void VesselTypeClass::Display(int x, int y, WindowNumberType window, HousesType) const
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
 * VesselTypeClass::Prep_For_Add -- Adds vessel types to the scenario editor object list.      *
 *                                                                                             *
 *    This routine is called when the scenario editor needs to obtain a list of the            *
 *    vessel object that can be placed down. It will submit all the vessel types that can      *
 *    be placed down.                                                                          *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void VesselTypeClass::Prep_For_Add(void)
{
    for (VesselType index = VESSEL_FIRST; index < VESSEL_COUNT; index++) {
        if (As_Reference(index).Get_Image_Data() != NULL) {
            Map.Add_To_List(&As_Reference(index));
        }
    }
}
#endif // SCENARIO_EDITOR

/***********************************************************************************************
 * VesselTypeClass::Create_One_Of -- Creates a vessel object that matches this vessel type.    *
 *                                                                                             *
 *    This routine is called when the type of vessel is known (by way of a VesselTypeClass)    *
 *    and a corresponding vessel object needs to be created.                                   *
 *                                                                                             *
 * INPUT:   house -- Pointer to the owner that this vessel will be assigned to.                *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the vessel object created. If no vessel could be         *
 *          created, then NULL is returned.                                                    *
 *                                                                                             *
 * WARNINGS:   The vessel is created in a limbo state. It must first be placed down upon       *
 *             the map before it starts to function.                                           *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
ObjectClass* VesselTypeClass::Create_One_Of(HouseClass* house) const
{
    return (new VesselClass(Type, house->Class->House));
}

/***********************************************************************************************
 * VesselTypeClass::Create_And_Place -- Creates a vessel and places it at location.            *
 *                                                                                             *
 *    This routine is used to create a vessel and then place it down upon the                  *
 *    map.                                                                                     *
 *                                                                                             *
 * INPUT:   cell  -- The location to place this vessel down upon.                              *
 *                                                                                             *
 *          house -- The house to assign this vessel's ownership to.                           *
 *                                                                                             *
 * OUTPUT:  bool; Was the vessel successfully created and placed down upon the map?            *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
bool VesselTypeClass::Create_And_Place(CELL cell, HousesType house) const
{
    VesselClass* unit = new VesselClass(Type, house);
    if (unit != NULL) {
        return (unit->Unlimbo(Cell_Coord(cell), Random_Pick(DIR_N, DIR_MAX)));
    }
    delete unit;
    return (false);
}

/***********************************************************************************************
 * VesselTypeClass::Dimensions -- Fetches the pixel width and height of this vessel type.      *
 *                                                                                             *
 *    This routine is used to fetch the width and height of this vessel type. These dimensions *
 *    are not specific to any particular facing. Rather, they are only for the generic vessel  *
 *    size.                                                                                    *
 *                                                                                             *
 * INPUT:   width, height  -- Reference to the integers that are to be initialized with the    *
 *                            pixel width and height of this vessel type.                      *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void VesselTypeClass::Dimensions(int& width, int& height) const
{
    width = 48;
    height = 48;
}

/***********************************************************************************************
 * VesselTypeClass::One_Time -- Performs one time initialization for vessel types.             *
 *                                                                                             *
 *    This routine will load in the vessel shape data. It should be called only once at the    *
 *    beginning of the game.                                                                   *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Only call this once.                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void VesselTypeClass::One_Time(void)
{
    for (VesselType index = VESSEL_FIRST; index < VESSEL_COUNT; index++) {
        char fullname[_MAX_FNAME + _MAX_EXT];
        char buffer[_MAX_FNAME + 4];
        VesselTypeClass const& uclass = As_Reference(index);
#ifdef FIXIT_CARRIER //	checked - ajw 9/28/98
        if (uclass.Level != -1 || index == VESSEL_CARRIER) {
#else
        if (uclass.Level != -1) {
#endif
            //		if (uclass.IsBuildable) {

            /*
            **	Fetch the supporting data files for the unit.
            */
            sprintf(buffer, "%sICON", uclass.Graphic_Name());
            _makepath(fullname, NULL, NULL, buffer, ".SHP");
            ((void const*&)uclass.CameoData) = MFCD::Retrieve(fullname);
        }

        /*
        **	Fetch a pointer to the unit's shape data.
        */
        _makepath(fullname, NULL, NULL, uclass.Graphic_Name(), ".SHP");
        ((void const*&)uclass.ImageData) = MFCD::Retrieve(fullname);

        ((int&)uclass.MaxSize) = 26;
    }

    // TD Gunboat (VESSEL_TDGUNBOAT): TGA-only TD art (TDBOAT) -> NULL ImageData from the loop above.
    // Donor = VESSEL_PT (RA's gunboat hull) so Draw_It doesn't bail; the launcher overlay resolves
    // the real "TDBOAT" sprite by IniName. CameoData falls back to PT's until the cameo is bundled.
    VesselTypeClass& tdboat = As_Reference(VESSEL_TDGUNBOAT);
    if (tdboat.ImageData == NULL) {
        ((void const*&)tdboat.ImageData) = As_Reference(VESSEL_PT).ImageData;
    }
    if (tdboat.CameoData == NULL) {
        ((void const*&)tdboat.CameoData) = As_Reference(VESSEL_PT).CameoData;
    }

    // TD Hovercraft (VESSEL_TDLST): TGA-only TD art -> NULL ImageData. Donor = VESSEL_TRANSPORT.
    VesselTypeClass& tdlst = As_Reference(VESSEL_TDLST);
    if (tdlst.ImageData == NULL) {
        ((void const*&)tdlst.ImageData) = As_Reference(VESSEL_TRANSPORT).ImageData;
    }
    if (tdlst.CameoData == NULL) {
        ((void const*&)tdlst.CameoData) = As_Reference(VESSEL_TRANSPORT).CameoData;
    }

    // Nod Obelisk Sub (VESSEL_TDOBLISUB): reuses the RA submarine art -> donor = VESSEL_SS for BOTH
    // ImageData and the launcher overlay (its RA_UNITS.XML tileset is cloned from SS, pointing at the
    // ss\ frames, so it renders as the sub hull). CameoData from SS too.
    VesselTypeClass& tdoblisub = As_Reference(VESSEL_TDOBLISUB);
    if (tdoblisub.ImageData == NULL) {
        ((void const*&)tdoblisub.ImageData) = As_Reference(VESSEL_SS).ImageData;
    }
    if (tdoblisub.CameoData == NULL) {
        ((void const*&)tdoblisub.CameoData) = As_Reference(VESSEL_SS).CameoData;
    }

    // Nod Submarine (VESSEL_TDNSUB): own art copy (tdnsub tileset); SS donor = NULL-guard only.
    VesselTypeClass& tdnsub = As_Reference(VESSEL_TDNSUB);
    if (tdnsub.ImageData == NULL) {
        ((void const*&)tdnsub.ImageData) = As_Reference(VESSEL_SS).ImageData;
    }
    if (tdnsub.CameoData == NULL) {
        ((void const*&)tdnsub.CameoData) = As_Reference(VESSEL_SS).CameoData;
    }

    // GDI surface fleet clones (VESSEL_TDPT/TDDD/TDCA): own HD hull tilesets (tdpt/tddd/tdca frames,
    // TGA-only -> NULL ImageData from the loop). Donor ImageData/CameoData = the RA original each clones
    // (PT/DD/CA) so Draw_It doesn't bail; the launcher overlay resolves the real cloned hull by IniName.
    VesselTypeClass& tdpt = As_Reference(VESSEL_TDPT);
    if (tdpt.ImageData == NULL) {
        ((void const*&)tdpt.ImageData) = As_Reference(VESSEL_PT).ImageData;
    }
    if (tdpt.CameoData == NULL) {
        ((void const*&)tdpt.CameoData) = As_Reference(VESSEL_PT).CameoData;
    }
    VesselTypeClass& tddd = As_Reference(VESSEL_TDDD);
    if (tddd.ImageData == NULL) {
        ((void const*&)tddd.ImageData) = As_Reference(VESSEL_DD).ImageData;
    }
    if (tddd.CameoData == NULL) {
        ((void const*&)tddd.CameoData) = As_Reference(VESSEL_DD).CameoData;
    }
    VesselTypeClass& tdca = As_Reference(VESSEL_TDCA);
    if (tdca.ImageData == NULL) {
        ((void const*&)tdca.ImageData) = As_Reference(VESSEL_CA).ImageData;
    }
    if (tdca.CameoData == NULL) {
        ((void const*&)tdca.CameoData) = As_Reference(VESSEL_CA).CameoData;
    }

    // Nod Missile Sub (VESSEL_TDMSUB): own art copy (tdmsub tileset); MSUB donor = NULL-guard only.
    VesselTypeClass& tdmsub = As_Reference(VESSEL_TDMSUB);
    if (tdmsub.ImageData == NULL) {
        ((void const*&)tdmsub.ImageData) = As_Reference(VESSEL_MISSILESUB).ImageData;
    }
    if (tdmsub.CameoData == NULL) {
        ((void const*&)tdmsub.CameoData) = As_Reference(VESSEL_MISSILESUB).CameoData;
    }

#ifdef FIXIT_CARRIER
    // v4.0: GDI Helicarrier made buildable (rules.ini [CARR] Owner=GoodGuy). Its HD hull art exists
    // (base CARR.ZIP + CARR tileset in RA_STRUCTURES.XML) so ImageData normally loads; NULL-guard the
    // cameo against the launcher's NULL-OverrideDisplayName CTD class (donor = CA) just in case.
    VesselTypeClass& carr = As_Reference(VESSEL_CARRIER);
    if (carr.CameoData == NULL) {
        ((void const*&)carr.CameoData) = As_Reference(VESSEL_CA).CameoData;
    }
#endif
}

/***********************************************************************************************
 * VesselTypeClass::Turret_Adjust -- Adjust turret offset according to facing specified.       *
 *                                                                                             *
 *    This routine will determine the pixel adjustment necessary for a turret. The direction   *
 *    specified is what the vessel body is facing.                                             *
 *                                                                                             *
 * INPUT:   dir   -- The presumed direction of the body facing for the vessel.                 *
 *                                                                                             *
 *          x,y   -- The center pixel position for the vessel. These values should be          *
 *                   adjusted (they are references) to match the adjusted offset for the       *
 *                   turret.                                                                   *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void VesselTypeClass::Turret_Adjust(DirType dir, int& x, int& y) const
{
    short xx = x;
    short yy = y;

    switch (Type) {
    // VESSEL_TDGUNBOAT: the gun sits on the foredeck, ahead of the bridge. Per-facing seat
    // table baked from Luke's dot marks on the hull renders (scripts/bake_turret_seats.py,
    // 2026-07-03): mount orbit fitted from N/NE/E marks, render px -> pack 0.652 -> classic px.
    case VESSEL_TDGUNBOAT: {
        static const signed char _tdboat_seat[16][2] = {
            {0, -9},  {4, -8},   {8, -6},   {11, -3},  {12, 1},   {11, 5},  {8, 8},   {5, 10},
            {0, 11},  {-4, 10},  {-8, 8},   {-11, 5},  {-12, 1},  {-11, -3}, {-8, -6}, {-5, -8},
        };
        int f = Dir_To_16(dir);
        x = xx + _tdboat_seat[f][0];
        y = yy + _tdboat_seat[f][1];
        break;
    }

    case VESSEL_TDCA: // = CA (native turrets, native seats -- Luke 2026-07-03)
    case VESSEL_CA:
        Normal_Move_Point(xx, yy, dir, 22);
        x = xx;
        y = yy - 4;
        break;


    case VESSEL_TDPT: // = PT
    case VESSEL_PT:
        Normal_Move_Point(xx, yy, dir, 14);
        x = xx;
        y = yy + 1;
        break;

    // TDDD wears the DD's SSAM turret but at Luke's dot-marked FORE mount ("keep the TDDD
    // mount position", 2026-07-03) -- not the vanilla DD's aft seat. TDPT/TDCA = RA originals.
    case VESSEL_TDDD: {
        static const signed char _tddd_seat[16][2] = {
            {0, -10},  {6, -10},  {10, -8},  {13, -5},  {14, -1},  {13, 3},  {10, 6},  {6, 8},
            {0, 8},    {-6, 8},   {-10, 6},  {-13, 3},  {-14, -1}, {-13, -5}, {-10, -8}, {-6, -10},
        };
        int f = Dir_To_16(dir);
        x = xx + _tddd_seat[f][0];
        y = yy + _tddd_seat[f][1];
        break;
    }

    case VESSEL_DD:
        Normal_Move_Point(xx, yy, dir + DIR_S, 8);
        x = xx;
        y = yy - 4;
        break;
    }
}

/***********************************************************************************************
 * VesselTypeClass::Overlap_List -- Figures the overlap list for the vessel type.              *
 *                                                                                             *
 *    This routine will return the overlap list for a vessel that is sitting still in the      *
 *    center of a cell.                                                                        *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the overlap list that this vessel would use.             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
short const* VesselTypeClass::Overlap_List(void) const
{
    static short const _ship[] = {-3,
                                  -2,
                                  -1,
                                  1,
                                  2,
                                  3,
                                  -MAP_CELL_W,
                                  -(MAP_CELL_W + 1),
                                  -(MAP_CELL_W - 1),
                                  -(MAP_CELL_W + 2),
                                  -(MAP_CELL_W - 2),
                                  +MAP_CELL_W,
                                  +(MAP_CELL_W + 1),
                                  +(MAP_CELL_W - 1),
                                  +(MAP_CELL_W + 2),
                                  +(MAP_CELL_W - 2),
                                  REFRESH_EOL};
    //	static short const _ship[] = {-1, 1,
    //		-MAP_CELL_W, -(MAP_CELL_W+1), -(MAP_CELL_W-1),
    //		+MAP_CELL_W, +(MAP_CELL_W+1), +(MAP_CELL_W-1),
    //		REFRESH_EOL};

    return (&_ship[0]);
}

/***********************************************************************************************
 * VesselTypeClass::From_Name -- Converts a name into a vessel type.                           *
 *                                                                                             *
 *    Use this routine to convert an ASCII version of a vessel type into the corresponding     *
 *    VesselType id value. Typical use of this would be to parse the INI file.                 *
 *                                                                                             *
 * INPUT:   name  -- Pointer to the ASCII name to be converted into a vessel type.             *
 *                                                                                             *
 * OUTPUT:  Returns with the vessel type number that matches the string specified.             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
VesselType VesselTypeClass::From_Name(char const* name)
{
    if (name != NULL) {
        for (VesselType classid = VESSEL_FIRST; classid < VESSEL_COUNT; classid++) {
            if (stricmp(As_Reference(classid).IniName, name) == 0) {
                return (classid);
            }
        }
    }
    return (VESSEL_NONE);
}

/***********************************************************************************************
 * VesselTypeClass::Max_Pips -- Fetches the maximum pips allowed for this vessel.              *
 *                                                                                             *
 *    This routine will determine the number of pips (maximum) allowed for this unit type.     *
 *    Typically, this is the number of passengers allowed.												  *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the maximum number of pips allowed for this vessel type.              *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/01/1996 BWG : Created.                                                                 *
 *=============================================================================================*/
int VesselTypeClass::Max_Pips(void) const
{
    return (Max_Passengers());
}
