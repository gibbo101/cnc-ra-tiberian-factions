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

/* $Header: /CounterStrike/BUILDING.CPP 5     3/13/97 5:18p Joe_b $ */
/***********************************************************************************************
 ***              C O N F I D E N T I A L  ---  W E S T W O O D  S T U D I O S               ***
 ***********************************************************************************************
 *                                                                                             *
 *                 Project Name : Command & Conquer                                            *
 *                                                                                             *
 *                    File Name : BUILDING.CPP                                                 *
 *                                                                                             *
 *                   Programmer : Joe L. Bostic                                                *
 *                                                                                             *
 *                   Start Date : September 10, 1993                                           *
 *                                                                                             *
 *                  Last Update : October 27, 1996 [JLB]                                       *
 *                                                                                             *
 *---------------------------------------------------------------------------------------------*
 * Functions:                                                                                  *
 *   BuildingClass::AI -- Handles non-graphic AI processing for buildings.                     *
 *   BuildingClass::Active_Click_With -- Handles cell selection for buildings.                 *
 *   BuildingClass::Animation_AI -- Handles normal building animation processing.              *
 *   BuildingClass::Assign_Target -- Assigns a target to the building.                         *
 *   BuildingClass::Begin_Mode -- Begins an animation mode for the building.                   *
 *   BuildingClass::BuildingClass -- Constructor for buildings.                                *
 *   BuildingClass::Can_Demolish -- Can the player demolish (sell back) the building?          *
 *   BuildingClass::Can_Enter_Cell -- Determines if building can be placed down.               *
 *   BuildingClass::Can_Fire -- Determines if this building can fire.                          *
 *   BuildingClass::Can_Player_Move -- Can this building be moved?                             *
 *   BuildingClass::Captured -- Captures the building.                                         *
 *   BuildingClass::Center_Coord -- Fetches the center coordinate for the building.            *
 *   BuildingClass::Charging_AI -- Handles the special charging logic for Tesla coils.         *
 *   BuildingClass::Check_Point -- Fetches the landing checkpoint for the given flight pattern.*
 *   BuildingClass::Click_With -- Handles clicking on the map while the building is selected.  *
 *   BuildingClass::Crew_Type -- This determines the crew that this object generates.          *
 *   BuildingClass::Death_Announcement -- Announce the death of this building.                 *
 *   BuildingClass::Debug_Dump -- Displays building status to the monochrome screen.           *
 *   BuildingClass::Detach -- Handles target removal from the game system.                     *
 *   BuildingClass::Detach_All -- Possibly abandons production according to factory type.      *
 *   BuildingClass::Docking_Coord -- Fetches the coordinate to use for docking.                *
 *   BuildingClass::Draw_It -- Displays the building at the location specified.                *
 *   BuildingClass::Drop_Debris -- Drops rubble when building is destroyed.                    *
 *   BuildingClass::Enter_Idle_Mode -- The building will enter its idle mode.                  *
 *   BuildingClass::Exit_Coord -- Determines location where object will leave it.              *
 *   BuildingClass::Exit_Object -- Initiates an object to leave the building.                  *
 *   BuildingClass::Factory_AI -- Handle factory production and initiation.                    *
 *   BuildingClass::Find_Exit_Cell -- Find a clear location to exit an object from this buildin*
 *   BuildingClass::Fire_Direction -- Fetches the direction of firing.                         *
 *   BuildingClass::Fire_Out -- Handles when attached animation expires.                       *
 *   BuildingClass::Flush_For_Placement -- Handles clearing a zone for object placement.       *
 *   BuildingClass::Get_Image_Data -- Fetch the image pointer for the building.                *
 *   BuildingClass::Grand_Opening -- Handles construction completed special operations.        *
 *   BuildingClass::Greatest_Threat -- Searches for target that building can fire upon.        *
 *   BuildingClass::How_Many_Survivors -- This determine the maximum number of survivors.      *
 *   BuildingClass::Init -- Initialize the building system to an empty null state.             *
 *   BuildingClass::Limbo -- Handles power adjustment as building goes into limbo.             *
 *   BuildingClass::Mark -- Building interface to map rendering system.                        *
 *   BuildingClass::Mission_Attack -- Handles attack mission for building.                     *
 *   BuildingClass::Mission_Construction -- Handles mission construction.                      *
 *   BuildingClass::Mission_Deconstruction -- Handles building deconstruction.                 *
 *   BuildingClass::Mission_Guard -- Handles guard mission for combat buildings.               *
 *   BuildingClass::Mission_Harvest -- Handles refinery unloading harvesters.                  *
 *   BuildingClass::Mission_Missile -- State machine for nuclear missile launch.               *
 *   BuildingClass::Mission_Repair -- Handles the repair (active) state for building.          *
 *   BuildingClass::Mission_Unload -- Handles the unload mission for a building.               *
 *   BuildingClass::Pip_Count -- Determines "full" pips to display for building.               *
 *   BuildingClass::Power_Output -- Fetches the current power output from this building.       *
 *   BuildingClass::Read_INI -- Reads buildings from INI file.                                 *
 *   BuildingClass::Receive_Message -- Handle an incoming message to the building.             *
 *   BuildingClass::Remap_Table -- Fetches the remap table to use for this building.           *
 *   BuildingClass::Remove_Gap_Effect -- Stop a gap generator from jamming cells               *
 *   BuildingClass::Repair -- Initiates or terminates the repair process.                      *
 *   BuildingClass::Repair_AI -- Handle the repair (and sell) logic for the building.          *
 *   BuildingClass::Revealed -- Reveals the building to the specified house.                   *
 *   BuildingClass::Rotation_AI -- Process any turret rotation required of this building.      *
 *   BuildingClass::Sell_Back -- Controls the sell back (demolish) operation.                  *
 *   BuildingClass::Shape_Number -- Fetch the shape number for this building.                  *
 *   BuildingClass::Sort_Y -- Returns the building coordinate used for sorting.                *
 *   BuildingClass::Take_Damage -- Inflicts damage points upon a building.                     *
 *   BuildingClass::Target_Coord -- Return the coordinate to use when firing on this building. *
 *   BuildingClass::Toggle_Primary -- Toggles the primary factory state.                       *
 *   BuildingClass::Turret_Facing -- Fetches the turret facing for this building.              *
 *   BuildingClass::Unlimbo -- Removes a building from limbo state.                            *
 *   BuildingClass::Update_Buildables -- Informs sidebar of additional construction options.   *
 *   BuildingClass::Value -- Determine the value of this building.                             *
 *   BuildingClass::What_Action -- Determines action to perform if click on specified object.  *
 *   BuildingClass::What_Action -- Determines what action will occur.                          *
 *   BuildingClass::Write_INI -- Write out the building data to the INI file specified.        *
 *   BuildingClass::delete -- Deallocates building object.                                     *
 *   BuildingClass::new -- Allocates a building object from building pool.                     *
 *   BuildingClass::~BuildingClass -- Destructor for building type objects.                    *
 * - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

#include "function.h"
#include "utracker.h"
#include "event.h"
// The TS war factory's door-mouth seats, where a finished vehicle appears.
#include "tsweap_exit_seats.inc"
#include "tspuls_muzzle.h"
#include <cstdio>
#include <cmath>
#include "rules.h"

/*
** New sidebar for GlyphX multiplayer. ST - 8/2/2019 2:35PM
*/
#include "sidebarglyphx.h"

// The vehicle a deployed TS building packs back into on a deploy or move order (the Limpet Mine drone,
// the Mobile Sensor Array, the Mobile War Factory); UNIT_NONE for every other building.
static UnitType TF_Packs_Into(BuildingClass const* building)
{
    if (*building == STRUCT_TSDLIMP) {
        return (UNIT_TSLIMP);
    }
    if (*building == STRUCT_TSDPSA) {
        return (UNIT_TSLPST);
    }
    if (*building == STRUCT_TSDWEAP) {
        return (UNIT_TSMWAR);
    }
    if (*building == STRUCT_TSTICK) {
        return (UNIT_TSTTNK);
    }
    return (UNIT_NONE);
}

// The TS refinery's dock lid stays shut: on the reverse-in seat it would show beside the harvester's hull,
// which TS never does.
static const bool TS_LID_ENABLED = false;

/*
** TF: rally points (CFE Patch Redux port) — draw rally markers directly in
** remastered graphics mode. Defined in conquer.cpp.
*/
extern void DLL_Draw_Intercept(int shape_number,
                               int x,
                               int y,
                               int width,
                               int height,
                               int flags,
                               const ObjectClass* object,
                               DirType rotation,
                               long scale,
                               const char* shape_file_name,
                               char override_owner);

enum SAMState
{
    SAM_READY, // Launcher can be facing any direction tracking targets.
    SAM_FIRING // Stationary while missile is being fired.
};

// TD's SAM states, for STRUCT_TDSAM only. They share the Status byte with SAMState, so every dispatch site
// tests the type first; TDSAM_UNDERGROUND stays 0, the Status a new building starts with.
enum TdSamState
{
    TDSAM_NONE = -1,
    TDSAM_UNDERGROUND, // 0 — hidden, awaiting target
    TDSAM_RISING,      // door anim frames 0-15
    TDSAM_READY,       // up, rotating to face TarCom
    TDSAM_FIRING,      // first shot
    TDSAM_READY2,      // re-rotate after shot 1
    TDSAM_FIRING2,     // second shot
    TDSAM_LOCKING,     // rotating back to DIR_N
    TDSAM_LOWERING,    // door anim frames 48-63
};

/*
**	Whether a SAM site's target is in the air: an aircraft aloft, or a jumpjet flying in the
**	top map layer, which TS counts as an air target too.
*/
static bool TF_SAM_Air_Target(TARGET target)
{
    if (!Target_Legal(target)) {
        return (false);
    }
    if (Is_Target_Aircraft(target)) {
        return (As_Aircraft(target)->Height != 0);
    }
    InfantryClass* inf = As_Infantry(target);
    return (inf != NULL && inf->Is_Airborne_Jumpjet() && inf->In_Which_Layer() != LAYER_GROUND);
}

/***************************************************************************
**	Center of building offset table.
*/
COORDINATE const BuildingClass::CenterOffset[BSIZE_COUNT] = {
    0x00800080L,
    0x008000FFL,
    0x00FF0080L,
    0x00FF00FFL,
    0x018000FFL,
    0x00FF0180L,
    0x01800180L,

    0x00FF0200L,

    0x02800280L,

    0x01800200L, // BSIZE_43 (4x3): x = 2 cells, y = 1.5 cells.

    0x02000200L, // BSIZE_44 (4x4): x = 2 cells, y = 2 cells -- the centre CELL is row 2 col 2,
                 // which for TSPROC is the dock pad itself (an occupy hole).
    0x01800280L, // BSIZE_53 (5x3): x = 2.5 cells, y = 1.5 cells -- centre CELL row 1 col 2 (hangar).
    0x00800180L, // BSIZE_31 (3x1): x = 1.5 cells, y = 0.5 cells.
    0x01800080L, // BSIZE_13 (1x3): x = 0.5 cells, y = 1.5 cells.
    0x02000180L, // BSIZE_34 (3x4): x = 1.5 cells, y = 2 cells -- centre CELL row 2 col 1.
};

/***********************************************************************************************
 * BuildingClass::Receive_Message -- Handle an incoming message to the building.               *
 *                                                                                             *
 *    This routine handles an incoming message to the building. Messages regulate the          *
 *    various cooperative ventures between buildings and units. This might include such        *
 *    actions as coordinating the construction yard animation with the actual building's       *
 *    construction animation.                                                                  *
 *                                                                                             *
 * INPUT:   from     -- The originator of the message received.                                *
 *                                                                                             *
 *          message  -- The radio message received.                                            *
 *                                                                                             *
 *          param    -- Reference to an optional parameter that might be used to return        *
 *                      extra information to the message originator.                           *
 *                                                                                             *
 * OUTPUT:  Returns with the response to the message (typically, this is just RADIO_OK).       *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/09/1994 JLB : Created.                                                                 *
 *   06/26/1995 JLB : Forces refinery load anim to start immediately.                          *
 *   08/13/1995 JLB : Uses ScenarioInit for special loose "CAN_LOAD" check.                    *
 *=============================================================================================*/
RadioMessageType BuildingClass::Receive_Message(RadioClass* from, RadioMessageType message, int& param)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    switch (message) {

    // TF: harvester queue jumping (CFE Patch Redux port): a refinery serving one harvester lets a clearly
    // closer one cut in. A harvester within HARV_QUEUE_JUMP_CUTOFF of the dock is never bumped.
    case RADIO_HELLO:
        // A refinery's attached harvester is in limbo, which breaks radio contact, so the dock looks free. Refuse
        // hellos while one is attached, or a second harvester docks into it and attaches twice.
        if ((Class->Type == STRUCT_REFINERY || Class->Type == STRUCT_TDPROC || Class->Type == STRUCT_TSPROC)
            && Is_Something_Attached()) {
            return (RADIO_NEGATIVE);
        }
        if ((Class->Type == STRUCT_REFINERY || Class->Type == STRUCT_TDPROC || Class->Type == STRUCT_TSPROC)
            && In_Radio_Contact()) {
            if (from != NULL && from->What_Am_I() == RTTI_UNIT && ((UnitClass*)from)->Class->IsToHarvest
                && Contact_With_Whom()->What_Am_I() == RTTI_UNIT) {

                UnitClass& currentHarvy = *static_cast<UnitClass*>(Contact_With_Whom());
                UnitClass& newHarvy = *static_cast<UnitClass*>(from);

                int currentHarvyDistance = currentHarvy.Distance(this);
                int newHarvyDistance = newHarvy.Distance(this);

                if (currentHarvyDistance > HARV_QUEUE_JUMP_CUTOFF && newHarvyDistance < currentHarvyDistance) {
                    Transmit_Message(RADIO_CANCEL, &currentHarvy);
                    return (TechnoClass::Receive_Message(from, message, param));
                }
            }
        }
        break;

    /*
    **	This message is received as a request to attach/load/dock with this building.
    **	Verify that this is allowed and return the appropriate response.
    */
    case RADIO_CAN_LOAD:
        TechnoClass::Receive_Message(from, message, param);
        if (!House->Is_Ally(from))
            return (RADIO_STATIC);
        if (Mission == MISSION_CONSTRUCTION || Mission == MISSION_DECONSTRUCTION || BState == BSTATE_CONSTRUCTION
            || (!ScenarioInit && Class->Type != STRUCT_REFINERY && Class->Type != STRUCT_TDPROC
                && Class->Type != STRUCT_TSPROC && In_Radio_Contact()))
            return (RADIO_NEGATIVE);
        switch (Class->Type) {
        case STRUCT_AIRSTRIP:
        case STRUCT_TDAFLD:    // TD Nod Airstrip — same fixed-wing dock semantics.
        case STRUCT_TDGAFLD:   // GDI Airfield — hosts the buildable A-10 (fixed-wing).
            if (from->What_Am_I() == RTTI_AIRCRAFT && ((AircraftClass const*)from)->Class->IsFixedWing) {
                return (RADIO_ROGER);
            }
            break;

        case STRUCT_HELIPAD:
        case STRUCT_TDHPAD:    // TD Helipad — same rotary-aircraft dock semantics.
        case STRUCT_AHPAD:     // Faction helipads — identical dock semantics.
        case STRUCT_SHPAD:
        case STRUCT_TDGHPAD:
        case STRUCT_TDNHPAD:
        case STRUCT_TSHPAD:    // TS Helipad -- same rotary-aircraft dock semantics.
            if (from->What_Am_I() == RTTI_AIRCRAFT && !((AircraftClass const*)from)->Class->IsFixedWing) {
                return (RADIO_ROGER);
            }
            break;

        case STRUCT_REPAIR:
        case STRUCT_TDFIX:    // TD Service Depot — same vehicle/aircraft repair semantics.
        case STRUCT_TSDEPT:   // TS Service Depot — same repair-bay semantics.
            if (from->What_Am_I() == RTTI_UNIT || (from->What_Am_I() == RTTI_AIRCRAFT)) {
                if (Transmit_Message(RADIO_ON_DEPOT, from) != RADIO_ROGER) {
                    return (RADIO_ROGER);
                }
            }
            return (RADIO_NEGATIVE);

        case STRUCT_REFINERY:
        case STRUCT_TSPROC:   // TS Refinery — same harvester dock semantics.
        case STRUCT_TDPROC: { // TD Refinery — same harvester dock semantics.
            // TF: every refinery accepts every harvester. The unload style follows the harvester and is chosen at
            // RADIO_IM_IN and in Mission_Unload.
            bool right_harvester = false;
            if (from->What_Am_I() == RTTI_UNIT) {
                right_harvester = (*((UnitClass*)from) == UNIT_HARVESTER || *((UnitClass*)from) == UNIT_TDHARV
                                   || *((UnitClass*)from) == UNIT_TSHARV);
            }
            if (right_harvester && (ScenarioInit || !Is_Something_Attached())) {
                return ((Contact_With_Whom() != from) ? RADIO_ROGER : RADIO_NEGATIVE);
            }
            break;
        }

        default:
            break;
        }
        return (RADIO_STATIC);

    /*
    **	This message is received when the object has attached itself to this
    **	building.
    */
    case RADIO_IM_IN:
        if (Mission == MISSION_DECONSTRUCTION) {
            return (RADIO_NEGATIVE);
        }
        switch (Class->Type) {
        case STRUCT_REPAIR:
        case STRUCT_TDFIX:    // TD Service Depot — same RADIO_IM_IN repair-bay handshake.
        case STRUCT_TSDEPT:   // TS Service Depot.
            // TF: a unit already in for repair that reports in again, at the end of its drive onto the TS pad, is
            // acknowledged without restarting the repair.
            if (Contact_With_Whom() == from && (Mission == MISSION_REPAIR || MissionQueue == MISSION_REPAIR)) {
                return (RADIO_ROGER);
            }
            IsReadyToCommence = true;
            Assign_Mission(MISSION_REPAIR);
            from->Assign_Mission(MISSION_SLEEP);
            return (RADIO_ROGER);

        case STRUCT_AIRSTRIP:
        case STRUCT_TDAFLD:    // TD Nod Airstrip — repair-on-dock for cargo plane.
        case STRUCT_TDGAFLD:   // GDI Airfield — repair/rearm-on-dock for the A-10.
        case STRUCT_HELIPAD:
        case STRUCT_TDHPAD:    // TD Helipad — repair-on-dock.
        case STRUCT_AHPAD:     // Faction helipads.
        case STRUCT_SHPAD:
        case STRUCT_TDGHPAD:
        case STRUCT_TDNHPAD:
        case STRUCT_TSHPAD:    // TS Helipad -- repair-on-dock.
            Assign_Mission(MISSION_REPAIR);
            from->Assign_Mission(MISSION_SLEEP);
            return (RADIO_ROGER);

        case STRUCT_TSPROC:
            // TF: every harvester unloads visibly at the TS refinery, parked as at the RA refinery; Mission_Unload
            // picks the unload by harvester type.
        case STRUCT_REFINERY:
            Mark(MARK_CHANGE);
            from->Assign_Mission(MISSION_UNLOAD);
            return (RADIO_ROGER);

        case STRUCT_TDPROC:
            // TF: RA and TS harvesters park and unload visibly at a TD refinery, whose animation draws a TD truck.
            // The TD harvester attaches as cargo, as in TD, and the refinery runs Mission_Harvest.
            if (from != NULL && from->What_Am_I() == RTTI_UNIT
                && (*((UnitClass*)from) == UNIT_HARVESTER || *((UnitClass*)from) == UNIT_TSHARV)) {
                Mark(MARK_CHANGE);
                from->Assign_Mission(MISSION_UNLOAD);
                return (RADIO_ROGER);
            }
            ScenarioInit++;
            Begin_Mode(BSTATE_ACTIVE);
            ScenarioInit--;
            Mark(MARK_CHANGE);
            Assign_Mission(MISSION_HARVEST);
            return (RADIO_ATTACH);

        default:
            break;
        }
        break;

    /*
    **	Docking maneuver maintenance message. See if new order should be given to the
    **	unit trying to dock.
    */
    case RADIO_DOCKING:
        TechnoClass::Receive_Message(from, message, param);

        // TF: a refinery refuses docking from anyone but its customer. A queued unit's polls would otherwise run
        // the coordination below at the customer, restarting its docking and overwriting its destination.
        if ((*this == STRUCT_REFINERY || *this == STRUCT_TDPROC || *this == STRUCT_TSPROC)
            && (Is_Something_Attached() || (In_Radio_Contact() && Contact_With_Whom() != from))) {
            return (RADIO_NEGATIVE);
        }

        /*
        **	When in radio contact for loading, the refinery starts
        **	flashing the lights.
        */
        if ((*this == STRUCT_REFINERY || *this == STRUCT_TDPROC || *this == STRUCT_TSPROC)
            && BState != BSTATE_FULL) {
            Begin_Mode(BSTATE_FULL);
        }

        // TF: once a TS refinery's customer is driving its dock track, parked on the pad or unloading, docking
        // is done. Running the coordination below again would send it back to its line-up cell.
        if (*this == STRUCT_TSPROC && from != NULL && from->What_Am_I() == RTTI_UNIT) {
            UnitClass* customer = (UnitClass*)from;
            if (customer->IsDumping || customer->IsDriving
                || Coord_Cell(customer->Center_Coord()) == Coord_Cell(Center_Coord())) {
                return (RADIO_ROGER);
            }
        }

        /*
        **	If this building is already in radio contact, then it might
        **	be able to satisfy the request to load by bumping off any
        **	preoccupying task.
        */
        if (*this == STRUCT_REPAIR || *this == STRUCT_TDFIX || *this == STRUCT_TSDEPT) {
            if (Contact_With_Whom() != from) {
                if (Transmit_Message(RADIO_ON_DEPOT) == RADIO_ROGER) {
                    if (Transmit_Message(RADIO_NEED_REPAIR) == RADIO_NEGATIVE) {
                        Transmit_Message(RADIO_RUN_AWAY);
                        Transmit_Message(RADIO_OVER_OUT);
                        return (RADIO_ROGER);
                    }
                }

                // TF: while the bay serves a customer, acknowledge a newcomer, which waits in MISSION_ENTER, but skip
                // the coordination below: its transmits would go to the current customer.
                if (In_Radio_Contact() && Contact_With_Whom() != from) {
                    return (RADIO_ROGER);
                }
            }
        }

        /*
        **	Establish contact with the object if this building isn't already in contact
        **	with another.
        */
        if (!In_Radio_Contact()) {
            Transmit_Message(RADIO_HELLO, from);
        }

        if (Transmit_Message(RADIO_NEED_TO_MOVE) == RADIO_ROGER) {
            switch (Class->Type) {
            case STRUCT_AIRSTRIP:
            case STRUCT_TDAFLD:    // TD Nod Airstrip — dock target is the building itself.
            case STRUCT_TDGAFLD:   // GDI Airfield — dock target is the building itself.
                param = As_Target();
                break;

            case STRUCT_HELIPAD:
            case STRUCT_TDHPAD:    // TD Helipad — dock target is the building itself.
            case STRUCT_AHPAD:     // Faction helipads.
            case STRUCT_SHPAD:
            case STRUCT_TDGHPAD:
            case STRUCT_TDNHPAD:
            case STRUCT_TSHPAD:    // TS Helipad -- dock target is the building itself.
                param = As_Target();
                break;

            case STRUCT_REPAIR:
            case STRUCT_TDFIX:    // TD Service Depot — same dock-tether semantics.
            case STRUCT_TSDEPT:   // TS Service Depot.
                Transmit_Message(RADIO_TETHER);
                param = ::As_Target(Coord_Cell(Center_Coord()));
                break;

            case STRUCT_TSPROC:
                /*
                **	Every truck lines up on the plate cell south-east of the
                **	pad, then reverses up the dock lane into its seat.
                */
                param = ::As_Target((CELL)(Coord_Cell(Center_Coord()) + MAP_CELL_W + 1));
                break;

            case STRUCT_REFINERY:
                /*
                **	RA refinery dock pad = DIR_S (the only FREE cell adjacent to the south
                **	face -- the refinery's 3x3 footprint occupies its own DIR_SW/center
                **	cells). A visible (non-Limbo'd) harvester can only stand here, so both
                **	the RA harvester and the TD harvester (pull-up OR backed orientation)
                **	dock on this cell. A true reverse-INTO-the-bay would require Limbo
                **	(harvester disappears), which we don't do for the RA refinery.
                */
                param = ::As_Target(Coord_Cell(Adjacent_Cell(Center_Coord(), DIR_S)));
                break;

            case STRUCT_TDPROC:
                // TF: TD's dock pad is SW of the centre, not RA's S: backing north from it puts the harvester on the SW
                // cell under the intake chute. From S it would stop a cell east of the chute.
                param = ::As_Target(Coord_Cell(Adjacent_Cell(Center_Coord(), DIR_SW)));
                break;
            }

            /*
            **	Tell the harvester to move to the docking pad of the building.
            */
            if (Transmit_Message(RADIO_MOVE_HERE, param) == RADIO_YEA_NOW_WHAT) {

                /*
                **	Since the harvester is already there, tell it to begin the backup
                **	procedure now. If it can't, then tell it to get outta here.
                */
                Transmit_Message(RADIO_TETHER);
                if ((*this == STRUCT_REFINERY || *this == STRUCT_TDPROC || *this == STRUCT_TSPROC)
                    && Transmit_Message(RADIO_BACKUP_NOW, from) != RADIO_ROGER) {
                    from->Scatter(0, true, true);
                }
            }
        }
        return (RADIO_ROGER);

    /*
    **	If a transport or harvester is requesting permission to head toward, dock
    **	and load/unload, check to make sure that this is allowed given the current
    **	state of the building.
    */
    case RADIO_ARE_REFINERY:
        if (Is_Something_Attached() || In_Radio_Contact() || IsInLimbo || House->Class->House != from->Owner()
            || ((*this != STRUCT_REFINERY && *this != STRUCT_TDPROC && *this != STRUCT_TSPROC)
                /* && *this != STRUCT_REPAIR*/)) {
            return (RADIO_NEGATIVE);
        }
        return (RADIO_ROGER);

    /*
    **	Someone is telling us that it is starting construction. This should only
    **	occur if this is a construction yard and a building was just placed on
    **	the map.
    */
    case RADIO_BUILDING:
        Assign_Mission(MISSION_REPAIR);
        TechnoClass::Receive_Message(from, message, param);
        return (RADIO_ROGER);

    /*
    **	Someone is telling us that they have finished construction. This should
    **	only occur if this is a construction yard and the building that was being
    **	constructed has finished. In this case, stop the construction yard
    **	animation.
    */
    case RADIO_COMPLETE:
        if (Mission != MISSION_DECONSTRUCTION) {
            Assign_Mission(MISSION_GUARD);
        }
        TechnoClass::Receive_Message(from, message, param);
        return (RADIO_ROGER);

    /*
    **	This message may occur unexpectedly if the unit in contact with this
    **	building is suddenly destroyed. Handle any cleanup necessary. For example,
    **	a construction yard should stop its construction animation in this case.
    */
    case RADIO_OVER_OUT:
        Begin_Mode(BSTATE_IDLE);
        if (*this == STRUCT_REPAIR || *this == STRUCT_TDFIX || *this == STRUCT_TSDEPT) {
            Assign_Mission(MISSION_GUARD);
        }
        TechnoClass::Receive_Message(from, message, param);
        return (RADIO_ROGER);

    /*
    **	This message is received when an object has completely left
    ** building. Sometimes special cleanup action is required when
    **	this event occurs.
    */
    case RADIO_UNLOADED:
        if (*this == STRUCT_REPAIR || *this == STRUCT_TDFIX || *this == STRUCT_TSDEPT) {
            if (Distance(from) < 0x0180) {
                return (RADIO_ROGER);
            }
        }
        // TF: when the harvester leaves, the refinery's lights go off, as in TD, and the house's queued harvesters
        // re-run refinery selection so the freed dock is considered (CFE Patch Redux port).
        if (*this == STRUCT_REFINERY || *this == STRUCT_TDPROC || *this == STRUCT_TSPROC) {
            Begin_Mode(BSTATE_IDLE);

            if (IsActive && !IsInLimbo && HasOpened) {
                for (int i = 0; i < Units.Count(); ++i) {
                    UnitClass* unit = Units.Ptr(i);
                    if (unit != NULL && unit->IsActive && !unit->IsInLimbo && unit->Class->IsToHarvest
                        && unit->House == House) {
                        unit->ReconsiderRefinery(this); // pass the freed dock for the TF_DEV confirm log
                    }
                }
            }
        }
        TechnoClass::Receive_Message(from, message, param);

        // TF: rally points (CFE Patch Redux port): a unit leaving a factory heads for its rally point, and is
        // then not told to run away.
        if (Can_Have_Rally_Point() && from != NULL && from->Is_Techno()) {
            if (Rally_Unit(*static_cast<TechnoClass*>(from))) {
                return (RADIO_ROGER);
            }
        }

        if (*this == STRUCT_WEAP || *this == STRUCT_AWEAP || *this == STRUCT_SWEAP || *this == STRUCT_AIRSTRIP
            || *this == STRUCT_REPAIR || *this == STRUCT_TDFIX || *this == STRUCT_TSDEPT || *this == STRUCT_TDWEAP
            || *this == STRUCT_TDAFLD || *this == STRUCT_TDGAFLD || Is_TS_War_Factory())
            return (RADIO_RUN_AWAY);
        return (RADIO_ROGER);

    default:
        break;
    }

    /*
    **	Pass along the message to the default message handler in the radio itself.
    */
    return (TechnoClass::Receive_Message(from, message, param));
}

#ifdef CHEAT_KEYS
/***********************************************************************************************
 * BuildingClass::Debug_Dump -- Displays building status to the monochrome screen.             *
 *                                                                                             *
 *    This utility function will output the current status of the building class to the        *
 *    monochrome screen. It is through this data that bugs may be fixed or detected.           *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/31/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Debug_Dump(MonoClass* mono) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    mono->Set_Cursor(0, 0);
    mono->Print(Text_String(TXT_DEBUG_BUILDING));
    mono->Fill_Attrib(66, 13, 12, 1, IsRepairing ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(66, 14, 12, 1, IsToRebuild ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(66, 15, 12, 1, IsAllowedToSell ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(66, 16, 12, 1, IsCharging ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(66, 17, 12, 1, IsCharged ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(66, 18, 12, 1, IsJamming ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(66, 19, 12, 1, IsJammed ? MonoClass::INVERSE : MonoClass::NORMAL);

    mono->Set_Cursor(1, 11);
    if (Factory) {
        mono->Printf("%s %d%%",
                     Factory->Get_Object()->Class_Of().IniName,
                     (100 * Factory->Completion()) / FactoryClass::STEP_COUNT);
    }

    TechnoClass::Debug_Dump(mono);
}
#endif

/***********************************************************************************************
 * BuildingClass::Draw_It -- Displays the building at the location specified.                  *
 *                                                                                             *
 *    This is the low level graphic routine that displays the building at the location         *
 *    specified.                                                                               *
 *                                                                                             *
 * INPUT:   x,y   -- The coordinate to draw the building at.                                   *
 *                                                                                             *
 *          window   -- The clipping window to use.                                            *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/20/1994 JLB : Created.                                                                 *
 *   06/27/1994 JLB : Takes a clipping window parameter.                                       *
 *   07/06/1995 JLB : Handles damaged silos correctly.                                         *
 *=============================================================================================*/
void BuildingClass::Draw_It(int x, int y, WindowNumberType window) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    /*
    **	The shape file to use for rendering depends on whether the building
    **	is undergoing construction or not.
    */
    void const* shapefile = Get_Image_Data();
    if (shapefile == NULL)
        return;

    /*
    **	Actually draw the building shape.
    */
    IsTheaterShape = Class->IsTheater; // Let Build_Frame know if this is a theater specific shape
    Techno_Draw_Object(shapefile, Shape_Number(), x, y, window);
    IsTheaterShape = false;

    /*
    ** Patch for adding overlay onto weapon factory.  Only add the overlay if
    ** the building has more than 1 hp.  Also, if the building's in radio
    ** contact, he must be unloading a constructed vehicle, so draw that
    ** vehicle before drawing the overlay.
    */
    if (BState != BSTATE_CONSTRUCTION) {

        /*
        **	A Tethered object is always rendered AFTER the building.
        */
        if ((*this == STRUCT_WEAP || *this == STRUCT_AWEAP || *this == STRUCT_SWEAP || *this == STRUCT_TDWEAP)
            && IsTethered && In_Radio_Contact() && !Contact_With_Whom()->IsInLimbo
            && Contact_With_Whom()->What_Am_I() != RTTI_BUILDING) {
            TechnoClass* contact = Contact_With_Whom();

            assert(contact->IsActive);
            int xxx = x
                      + ((int)Lepton_To_Pixel((int)Coord_X(contact->Render_Coord()))
                         - (int)Lepton_To_Pixel((int)Coord_X(Render_Coord())));
            int yyy = y
                      + ((int)Lepton_To_Pixel((int)Coord_Y(contact->Render_Coord()))
                         - (int)Lepton_To_Pixel((int)Coord_Y(Render_Coord())));
            contact->Draw_It(xxx, yyy, window);
            contact->IsToDisplay = false;
        }

        /*
        **	Draw the weapon factory custom overlay graphic.
        */
        // TF: TD's weapons factory draws its own TDWEAP2 roof and door overlay rather than RA's WEAP2, and skips it
        // on a building down to 1 strength, as TD does.
        if (*this == STRUCT_TDWEAP && Strength > 1) {
            int shapenum = Door_Stage();
            if (Health_Ratio() <= Rule.ConditionYellow)
                shapenum += 10;
            Techno_Draw_Object_Virtual(Class->WarFactoryOverlayTd, shapenum, x, y, window, DIR_N, 0x0100, "TDWEAP2");
        }

        /*
        **  STRUCT_TSWEAP — TS drives its bay with a 9-stage roll-up shutter
        **  over a static interior (TIBSUN ART.INI: DoorAnim=GAWEAP_D,
        **  DoorStages=9, UnderDoorAnim=GAWEAP_1). The two are composited into
        **  one TSWEAP2 tileset so a single overlay draw covers a stage, the
        **  same scheme RA uses for WEAP2. Damaged buildings take the second
        **  run, which repeats the stages over the wrecked interior — TS ships
        **  no damaged shutter art.
        **
        **  The shape pointer only feeds classic mode, which the TS tree does
        **  not support; the launcher resolves the real art from the "TSWEAP2"
        **  name. TD's overlay stands in so the pointer is never NULL, which
        **  would skip the draw outright.
        */
        /*
        **	TS refinery layers, on the building's own canvas: its front (the building in front of
        **	the dock lane, at the idle phase), which sorts south of a docked truck so the truck
        **	backs in under the deck; the flare stack's fire while a burst plays (its 20 lit frames
        **	serve both states); and the dock lid while it opens and closes (a healthy run, then a
        **	damaged one).
        */
        if (*this == STRUCT_TSPROC && Strength > 1 && BState != BSTATE_CONSTRUCTION) {
            int dmg = (Health_Ratio() <= Rule.ConditionYellow) ? 1 : 0;
            Techno_Draw_Object_Virtual(Class->TsRefineryFront, Shape_Number(), x, y, window, DIR_N, 0x0100, "TSPROCNF");
            if (TsFlameStage >= 0) {
                Techno_Draw_Object_Virtual(Class->TsRefineryFlame, TsFlameStage, x, y, window, DIR_N, 0x0100, "TSPROCFR");
            }
            if (TS_LID_ENABLED && Ts_Lid_Busy()) {
                Techno_Draw_Object_Virtual(
                    Class->TsRefineryLid, TsLidStage + dmg * 5, x, y, window, DIR_N, 0x0100, "TSPROCLD");
            }
        }

        /*
        **	TS war factory (08-28 rebuild): the body is one sprite. The roll-up
        **	shutter (GAWEAP_D, 9 stages + 9 damaged) is a layer sorted south of
        **	the vehicle in the mouth, so it hides it while shut and reveals it
        **	as it rises; the under-door floor (GAWEAP_1) shows while unloading.
        */
        // TF: the EMP cannon's voxel turret rides on the dome, turning with PrimaryFacing. It appears from build-up
        // frame 10 and goes as soon as the building is sold.
        bool tspuls_cannon = BState != BSTATE_CONSTRUCTION
                             || (Mission != MISSION_DECONSTRUCTION && Fetch_Stage() >= 10);
        if (*this == STRUCT_TSPULS && Strength > 0 && tspuls_cannon) {
            static const int TSPULS_TURRET_Y = 10; // classic px: the cannon's seat on the dome
            int tshape = UnitClass::BodyShape[Dir_To_32(PrimaryFacing.Current())];
            Techno_Draw_Object_Virtual(Class->TsPulseTurret, tshape, x, y + TSPULS_TURRET_Y, window, DIR_N, 0x0100, "TSPULST");
        }

        // TF: the dug-in Tick Tank draws its turret over the body, from the frame its turret facing picks (TSTICKT).
        if (*this == STRUCT_TSTICK && Strength > 0 && BState != BSTATE_CONSTRUCTION) {
            Techno_Draw_Object_Virtual(Get_Image_Data(), Shape_Number(), x, y, window, DIR_N, 0x0100, "TSTICKT");
        }

        // TF: a component tower draws its wall ends, links, connectors and couplings over the body, then its
        // turret and, while the house has power, its door lamp. Layer frames: scripts/ts_pack_ctwr_hd.py.
        // The tower stands on its plot's south cell, the north one the head's headroom.
        if (TF_Is_Wall_Tower(Class->Type) && Strength > 0) {
            static const FacingType sides[4] = {FACING_N, FACING_E, FACING_S, FACING_W};
            int dmg = (Health_Ratio() <= Rule.ConditionYellow) ? 1 : 0;
            int kind[4];
            int link[4];
            bool gate_end[4];
            CELL cell = (CELL)(Coord_Cell(Coord) + *Class->Occupy_List());
            for (int i = 0; i < 4; i++) {
                CELL adj = Adjacent_Cell(cell, sides[i]);
                OverlayType o = Map.In_Radar(adj) ? Map[adj].Overlay : OVERLAY_NONE;
                kind[i] = (o == OVERLAY_TSWALL) ? 0 : (o == OVERLAY_TSNWALL) ? 1 : (o == OVERLAY_BRICK_WALL) ? 2 : -1;
                gate_end[i] = Map.In_Radar(adj) && Map[adj].Has_Gate_Along(i == 1 || i == 3);
                link[i] = -1;
                BuildingClass const* other = Map.In_Radar(adj) ? Map[adj].Cell_Building() : NULL;
                if (other != NULL && other != this && other->Strength > 0 && TF_Is_Wall_Tower(other->Class->Type)
                    && other->BState != BSTATE_CONSTRUCTION && other->Mission != MISSION_DECONSTRUCTION) {
                    link[i] = (other->Health_Ratio() <= Rule.ConditionYellow) ? 1 : 0;
                }
            }
            void const* shp = Get_Image_Data();
            if (kind[0] >= 0) {
                Techno_Draw_Object_Virtual(shp, 14 + kind[0] * 2 + dmg, x, y, window, DIR_N, 0x0100, "TSCTWRX");
            }
            for (int i = 0; i < 4; i++) {
                if (link[i] >= 0) {
                    Techno_Draw_Object_Virtual(shp, 26 + i * 4 + dmg * 2 + link[i], x, y, window, DIR_N, 0x0100, "TSCTWRX");
                } else if (gate_end[i]) {
                    Techno_Draw_Object_Virtual(shp, 42 + i * 2 + dmg, x, y, window, DIR_N, 0x0100, "TSCTWRX");
                } else if (kind[i] >= 0) {
                    Techno_Draw_Object_Virtual(shp, i * 2 + dmg, x, y, window, DIR_N, 0x0100, "TSCTWRX");
                }
            }
            if (kind[2] >= 0) {
                Techno_Draw_Object_Virtual(shp, 8 + kind[2] * 2 + dmg, x, y, window, DIR_N, 0x0100, "TSCTWRX");
            }
            char const* turret = (*this == STRUCT_TSVULC) ? "TSVULCT"
                                 : (*this == STRUCT_TSROCK) ? "TSROCKT"
                                 : (*this == STRUCT_TSCSAM) ? "TSCSAMT"
                                 : NULL;
            if (turret != NULL) {
                Techno_Draw_Object_Virtual(shp, Shape_Number(), x, y, window, DIR_N, 0x0100, turret);
            }
            if (House->Power_Fraction() >= 1) {
                Techno_Draw_Object_Virtual(shp, 20 + 1 + (Frame / 4) % 5, x, y, window, DIR_N, 0x0100, "TSCTWRX");
            }
        }

        // TF: a gate draws the end of a wall running into each end, or its part of a finished tower's connector.
        // A north-south gate carries its north end under each gate frame. Layer frames: scripts/ts_pack_gates.py.
        TFGateInfo const* gate = TF_Gate_Info(Class->Type);
        if (gate != NULL && Strength > 0) {
            char layer[16];
            snprintf(layer, sizeof(layer), "%sX", Class->IniName);
            int dmg = (Health_Ratio() <= Rule.ConditionYellow) ? 1 : 0;
            CELL origin = Coord_Cell(Coord);
            CELL ends[2] = {gate->Horizontal ? Adjacent_Cell(origin, FACING_W) : Adjacent_Cell(origin, FACING_N),
                            gate->Horizontal ? (CELL)(origin + 3) : (CELL)(origin + 3 * MAP_CELL_W)};
            void const* shp = Get_Image_Data();
            char tower_layer[16];
            snprintf(tower_layer, sizeof(tower_layer), "%sL", Class->IniName);
            int frames = 2 * gate->Stages + 2 * gate->IdleFrames;
            for (int e = 0; e < 2; e++) {
                if (!Map.In_Radar(ends[e])) {
                    continue;
                }
                BuildingClass const* tower = Map[ends[e]].Cell_Building();
                if (tower != NULL && tower->Strength > 0 && TF_Is_Wall_Tower(tower->Class->Type)
                    && tower->BState != BSTATE_CONSTRUCTION) {
                    int tdmg = (tower->Health_Ratio() <= Rule.ConditionYellow) ? 1 : 0;
                    if (gate->Horizontal) {
                        Techno_Draw_Object_Virtual(shp, e * 2 + tdmg, x, y, window, DIR_N, 0x0100, tower_layer);
                    } else if (e == 0) {
                        Techno_Draw_Object_Virtual(shp, tdmg * frames + Shape_Number(), x, y, window, DIR_N, 0x0100, tower_layer);
                    }
                    continue;
                }
                OverlayType o = Map[ends[e]].Overlay;
                int kind = (o == OVERLAY_TSWALL) ? 0 : (o == OVERLAY_TSNWALL) ? 1 : (o == OVERLAY_BRICK_WALL) ? 2 : -1;
                if (kind < 0) {
                    continue;
                }
                int frame = gate->Horizontal ? (kind * 4 + e * 2 + dmg)
                                             : (e == 0 ? 6 + kind * frames + Shape_Number() : kind * 2 + dmg);
                Techno_Draw_Object_Virtual(shp, frame, x, y, window, DIR_N, 0x0100, layer);
            }
        }

        // TF: a TS Service Depot's pad glows while it repairs (TS [GADEPT] ProductionAnim, AnimActive=0,7,2);
        // a damaged depot plays the cracked pad's run.
        if (*this == STRUCT_TSDEPT && BState == BSTATE_ACTIVE && Strength > 0) {
            int glow = ((int)Frame / 2) % 7 + ((Health_Ratio() <= Rule.ConditionYellow) ? 7 : 0);
            Techno_Draw_Object_Virtual(Get_Image_Data(), glow, x, y, window, DIR_N, 0x0100, "TSDEPTRP");
        }

        // TF: a TS war factory draws, over its body, the under-door floor while unloading, the near face of
        // the hangar in front of a vehicle in the bay, then the shutter.
        if (Is_TS_War_Factory() && Strength > 1) {
            bool mobile = (*this == STRUCT_TSDWEAP);
            int stages = TS_Door_Stages();
            int dmg = (Health_Ratio() <= Rule.ConditionYellow) ? 1 : 0;
            if (Mission == MISSION_UNLOAD) {
                Techno_Draw_Object_Virtual(mobile ? Class->TsDweapUnderDoor : Class->TsWeapUnderDoor, dmg, x, y, window,
                                           DIR_N, 0x0100, mobile ? "TSDWEAPUD" : "TSWEAPUD");
            }
            int stage = Door_Stage();
            if (stage < 0) {
                stage = 0;
            }
            if (stage > stages - 1) {
                stage = stages - 1;
            }
            if (Mission == MISSION_UNLOAD) {
                Techno_Draw_Object_Virtual(mobile ? Class->TsDweapFrontOpen : Class->TsWeapFrontOpen, Shape_Number(), x, y,
                                           window, DIR_N, 0x0100, mobile ? "TSDWEAPNU" : "TSWEAPNU");
            } else {
                Techno_Draw_Object_Virtual(mobile ? Class->TsDweapFront : Class->TsWeapFront, Shape_Number(), x, y, window,
                                           DIR_N, 0x0100, mobile ? "TSDWEAPNF" : "TSWEAPNF");
            }
            Techno_Draw_Object_Virtual(mobile ? Class->TsDweapShutter : Class->TsWeapShutter, stage + dmg * stages, x, y,
                                       window, DIR_N, 0x0100, mobile ? "TSDWEAPDR" : "TSWEAPDR");
        }

        // TF: the faction war factories draw their own AWEAP2 / SWEAP2 door overlays, which the launcher resolves
        // by name; classic mode shares WarFactoryOverlay.
        if (*this == STRUCT_WEAP || *this == STRUCT_FAKEWEAP || *this == STRUCT_AWEAP || *this == STRUCT_SWEAP) {
            int shapenum = Door_Stage();
            if (Health_Ratio() <= Rule.ConditionYellow)
                shapenum += 4;
            const char* overlay_name = "WEAP2";
            if (*this == STRUCT_AWEAP) {
                overlay_name = "AWEAP2";
            } else if (*this == STRUCT_SWEAP) {
                overlay_name = "SWEAP2";
            }
            // Added override shape file name. ST - 8/1/2019 5:24PM
            // Techno_Draw_Object(Class->WarFactoryOverlay, shapenum, x, y, window);
            Techno_Draw_Object_Virtual(Class->WarFactoryOverlay, shapenum, x, y, window, DIR_N, 0x0100, overlay_name);
        }

        /*
        **	Draw any repair feedback graphic required.
        */
        if (IsRepairing && IsWrenchVisible) {
            CC_Draw_Shape(ObjectTypeClass::SelectShapes, SELECT_WRENCH, x, y, window, SHAPE_CENTER | SHAPE_WIN_REL);
        }
    }

    // TF: rally points (CFE Patch Redux port): the owner sees a selected building's rally line, ending in
    // its faction's emblem.
    if (Can_Have_Rally_Point() && Is_Selected_By_Player(House) && RallyPoint && Target_Legal(RallyPoint)) {
        int startX, startY, endX, endY;
        Map.Coord_To_Pixel(Center_Coord(), startX, startY);
        Map.Coord_To_Pixel(As_Coord(RallyPoint), endX, endY);

        if (window == WINDOW_VIRTUAL) {
            int Xdistance = endX - startX;
            bool negativeX = (Xdistance < 0);
            if (negativeX) {
                Xdistance = -Xdistance;
            }
            int Ydistance = endY - startY;
            bool negativeY = (Ydistance < 0);
            if (negativeY) {
                Ydistance = -Ydistance;
            }
            float diagonaldistance = sqrtf((float)((Xdistance * Xdistance) + (Ydistance * Ydistance)));
            int steps = (int)(diagonaldistance / 10.0f);
            if (steps > 0) {
                float deltaX = (float)Xdistance / (float)steps;
                float deltaY = (float)Ydistance / (float)steps;
                for (int i = 0; i < steps; i++) {
                    // A long line skips dots in the middle: too many shapes crash the GlyphX client.
                    if (steps > 32) {
                        int togo = steps - i - 1;
                        if ((i > 16) && (togo > 16) && (i % 2 != 0)) {
                            continue;
                        }
                        if ((i > 32) && (togo > 32) && (i % 4 != 0)) {
                            continue;
                        }
                        if ((i > 64) && (togo > 64) && (i % 8 != 0)) {
                            continue;
                        }
                        if ((i > 128) && (togo > 128) && (i % 16 != 0)) {
                            continue;
                        }
                    }
                    int diffX = (int)((float)i * deltaX);
                    if (negativeX) {
                        diffX = -diffX;
                    }
                    int diffY = (int)((float)i * deltaY);
                    if (negativeY) {
                        diffY = -diffY;
                    }
                    DLL_Draw_Intercept(
                        0, startX + diffX, startY + diffY, 4, 4, SHAPE_WIN_REL | SHAPE_CENTER, this, DIR_N, 0x0100, "DOTSML", HOUSE_NONE);
                }
            }
            const char* enddot;
            if ((Owner() == HOUSE_GOOD) || (House->ActLike == HOUSE_GOOD)) {
                enddot = "DOTGDI";
            } else if ((Owner() == HOUSE_BAD) || (House->ActLike == HOUSE_BAD)) {
                enddot = "DOTNOD";
            } else if ((Owner() == HOUSE_USSR) || (Owner() == HOUSE_UKRAINE) || (House->ActLike == HOUSE_USSR)
                       || (House->ActLike == HOUSE_UKRAINE)) {
                enddot = "DOTUSSR";
            } else {
                enddot = "DOTALLY";
            }
            DLL_Draw_Intercept(0, endX, endY, 8, 8, SHAPE_WIN_REL | SHAPE_CENTER, this, DIR_N, 0x0100, enddot, HOUSE_NONE);
        } else {
            CC_Draw_Line(startX, startY, endX, endY, LTGREEN, 1, window);
        }
    }

    TechnoClass::Draw_It(x, y, window);

    /*
    ** If this is a factory that we're spying on, show what it's producing
    */
    if ((Spied_By() & (1 << (PlayerPtr->Class->House)) && Is_Selected_By_Player())
        || ((window == WINDOW_VIRTUAL) && (Session.Type != GAME_NORMAL))) {

        /*
        **	Fetch the factory that is associate with this building. For computer controlled buildings, the
        **	factory pointer is integral to the building itself. For human controlled buildings, the factory
        **	pointer is part of the house structure and must be retrieved from there.
        */
        FactoryClass* factory = NULL;
        if (House->IsHuman) {
            factory = House->Fetch_Factory(Class->ToBuild, *this == STRUCT_TSDROP);
        } else {
            factory = Factory;
        }

        /*
        **	If there is a factory associated with this building, then fetch any attached
        **	object under production and display its cameo image over the top of this building.
        */
        if (factory != NULL) {
            TechnoClass* obj = factory->Get_Object();
            if (obj != NULL) {
#ifdef FIXIT_CSII
                CC_Draw_Shape(obj,
                              obj->Techno_Type_Class()->Get_Cameo_Data(),
                              0,
                              x,
                              y,
                              window,
                              SHAPE_CENTER | SHAPE_WIN_REL | SHAPE_NORMAL,
                              NULL);
#else
                void const* remapper = obj->House->Remap_Table(false, obj->Techno_Type_Class()->Remap);
                CC_Draw_Shape(obj->Techno_Type_Class()->Get_Cameo_Data(),
                              0,
                              x,
                              y,
                              window,
                              SHAPE_CENTER | SHAPE_WIN_REL | ((remapper != NULL) ? SHAPE_FADING : SHAPE_NORMAL),
                              remapper);
#endif
            }
        }
    }
}

/***********************************************************************************************
 * BuildingClass::Shape_Number -- Fetch the shape number for this building.                    *
 *                                                                                             *
 *    This routine will examine the current state of the building and return with the shape    *
 *    number to use. The shape number is subordinate to the building graphic image data.       *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the shape number to use when rendering this building.                 *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
// An Upgrade Centre plug type's place in the art order: dish (TSPION), dome (TSPODS), node (TSSEEK);
// -1 for any other type.
static int TF_Plug_Type_Index(StructType type)
{
    switch (type) {
    case STRUCT_TSPION:
        return (0);
    case STRUCT_TSPODS:
        return (1);
    case STRUCT_TSSEEK:
        return (2);
    default:
        return (-1);
    }
}

// The Upgrade Centre art block for its plugs: 1-3 for one plug type alone, 4-9 for the ordered distinct
// pairs (first in socket 1). scripts/ts_pack_tree.py packs the blocks in this order.
int TF_Plug_Art_Block(StructType first, StructType second)
{
    int a = TF_Plug_Type_Index(first);
    int b = TF_Plug_Type_Index(second);
    if (a < 0) {
        return (0);
    }
    if (b < 0 || b == a) {
        return (1 + a);
    }
    return (4 + a * 2 + ((b > a) ? (b - 1) : b));
}

// Starts the TS refinery's dock lid opening or closing (NAREFN_A forward or reversed); AI steps it and
// Ts_Lid_Busy reports while it moves. Opening does nothing while TS_LID_ENABLED is false.
void BuildingClass::Ts_Lid_Open(void)
{
    if (!TS_LID_ENABLED) {
        return;
    }
    if (TsLidPhase == 0) {
        TsLidStage = 0;
    }
    if (TsLidPhase == 0 || TsLidPhase == 3) {
        TsLidPhase = 1;
        TsLidTick = 0;
    }
}

void BuildingClass::Ts_Lid_Close(void)
{
    if (TsLidPhase == 1 || TsLidPhase == 2) {
        if (TsLidPhase == 2) {
            TsLidStage = 4;
        }
        TsLidPhase = 3;
        TsLidTick = 0;
    }
}

int BuildingClass::Shape_Number(void) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    int shapenum = Fetch_Stage();

    // TF: the Firestorm generator stands still on low power, as TS's powered anims do: the frames after its loops.
    if (*this == STRUCT_TSFGEN && BState != BSTATE_CONSTRUCTION && House->Power_Fraction() < 1) {
        return (96 + ((Health_Ratio() <= Rule.ConditionYellow) ? 1 : 0));
    }

    // TF: the EMP cannon's body is a static mound, healthy or damaged; Draw_It draws the cannon over it.
    if (*this == STRUCT_TSPULS && BState != BSTATE_CONSTRUCTION) {
        return ((Health_Ratio() <= Rule.ConditionYellow) ? 1 : 0);
    }

    // TF: a gate's frames run its door from shut to open, then the same run damaged, then its idle loops.
    TFGateInfo const* gate = TF_Gate_Info(Class->Type);
    if (gate != NULL && BState != BSTATE_CONSTRUCTION) {
        int damaged = (Health_Ratio() <= Rule.ConditionYellow) ? 1 : 0;
        if (gate->IdleFrames > 0 && Is_Door_Closed()) {
            int step = (Frame / 3) % (gate->IdleFrames + 1);
            if (step > 0) {
                return (2 * gate->Stages + damaged * gate->IdleFrames + step - 1);
            }
        }
        return (Door_Position() + damaged * gate->Stages);
    }

    // TF: a Firestorm wall section's rail reaches towards each neighbouring section of its house
    // (N1 E2 S4 W8), +16 when damaged, +32 while the house's field is up.
    if (*this == STRUCT_TSFSDF) {
        static FacingType const _sides[] = {FACING_N, FACING_E, FACING_S, FACING_W};
        int joins = 0;
        CELL cell = Coord_Cell(Coord);
        for (int i = 0; i < 4; i++) {
            BuildingClass const* n = Map[Adjacent_Cell(cell, _sides[i])].Cell_Building();
            if (n != NULL && *n == STRUCT_TSFSDF && n->House == House && !n->IsInLimbo) {
                joins |= (1 << i);
            }
        }
        if (Health_Ratio() <= Rule.ConditionYellow) {
            joins += 16;
        }
        if (House->IsFirestormLive) {
            joins += 32;
        }
        return (joins);
    }

    /*
    **	The shape file to use for rendering depends on whether the building
    **	is undergoing construction or not.
    */
    if (BState == BSTATE_CONSTRUCTION) {

        /*
        **	If the building is deconstructing, then the display frame progresses
        **	from the end to the beginning. Reverse the shape number accordingly.
        */
        // TF: a deployed TS building packing itself up also runs its build-up backwards.
        if (Mission == MISSION_DECONSTRUCTION || (Mission == MISSION_UNLOAD && TF_Packs_Into(this) != UNIT_NONE)) {
            shapenum = (Class->Anims[BState].Start + Class->Anims[BState].Count - 1) - shapenum;
        }

    } else {

        /*
        **	If this is a camouflaged pill box and it is not owned by the player, then
        **	it is displayed with the MEGA-camouflaged imagery.
        */
        if ((!IsOwnedByPlayer) && (*this == STRUCT_CAMOPILLBOX)) {
            shapenum += 1;
        }

        /*
        **	The Tesla Coil has a stage value that can be overridden by
        **	its current state.
        */
        // TF: the Obelisk charges the same way, through IsCharging / IsCharged and Charging_AI.
        if (*this == STRUCT_TESLA || *this == STRUCT_TDOBLI) {
            if (IsCharged) {
                shapenum = 3;
            } else {
                if (IsCharging) {
                    shapenum = Fetch_Stage();
                } else {
                    shapenum = 0;
                }
            }
        }

        /*
        **	Buildings that contain a turret handle their shape determination
        **	differently than normal buildings. They need to take into consideration
        **	the direction the turret is facing.
        */
        if (Class->IsTurretEquipped) {
            shapenum = UnitClass::BodyShape[Dir_To_32(PrimaryFacing.Current())];

            if (*this == STRUCT_SAM) {

                /*
                **	SAM sites that are free to rotate fetch their animation frame
                **	from the building's turret facing. All other animation stages
                **	fetch their frame from the embedded animation sequencer.
                */
                if (Health_Ratio() <= Rule.ConditionYellow) {
                    shapenum += 35;
                }
            } else if (*this == STRUCT_TDSAM) {

                // TF: TD SAM frames, as in TD: 0-15 rising, 16-47 the 32 raised facings, 48-63 lowering, +64 damaged.
                if (Status == TDSAM_READY || Status == TDSAM_FIRING || Status == TDSAM_READY2
                    || Status == TDSAM_FIRING2 || Status == TDSAM_LOCKING) {
                    shapenum = UnitClass::BodyShape[Dir_To_32(PrimaryFacing.Current())] + 16;
                } else {
                    shapenum = Fetch_Stage();
                }
                if (Health_Ratio() <= Rule.ConditionYellow) {
                    shapenum += 64;
                }
            } else {
                if (IsInRecoilState) {
                    shapenum += 32;
                }
                if (Health_Ratio() <= Rule.ConditionYellow) {
                    shapenum += 64;
                }
            }
        } else {

            /*
            **	If it is a significantly damaged weapons factory, it is shown in
            **	the worst state possible.
            */
            if (*this == STRUCT_WEAP || *this == STRUCT_FAKEWEAP) {
                shapenum = 0;
                if (Health_Ratio() <= Rule.ConditionYellow) {
                    shapenum = 1;
                }

            } else {

                /*
                **	Special render stage for silos. The stage is dependent on the current
                **	Tiberium collected as it relates to Tiberium capacity.
                */
                // TF: the TD silo has the same five fill levels and damaged frames (docs/td-tier1-verification.md).
                if (*this == STRUCT_STORAGE || *this == STRUCT_TDSILO) {

                    int level = 0;
                    if (House->Capacity) {
                        level = (House->Tiberium * 5) / House->Capacity;
                    }

                    shapenum += Bound(level, 0, 4);
                    if (Health_Ratio() <= Rule.ConditionYellow) {
                        shapenum += 5;
                    }

                } else if (*this == STRUCT_TSSILO) {

                    /*
                    **	The TS silo shows its Tiberium through the glass at four levels (empty, a
                    **	third, two thirds, full). Each level is a block of the lamps' idle loop,
                    **	healthy then damaged.
                    */
                    int const loop = Class->Anims[BSTATE_IDLE].Start + Class->Anims[BSTATE_IDLE].Count;
                    int level = 0;
                    if (House->Capacity) {
                        level = (House->Tiberium * 4) / House->Capacity;
                    }
                    shapenum += Bound(level, 0, 3) * 2 * loop;
                    if (Health_Ratio() <= Rule.ConditionYellow) {
                        shapenum += loop;
                    }

                } else {

                    /*
                    **	If below half strenth, then show the damage frames of the
                    **	building.
                    */
                    if (Health_Ratio() <= Rule.ConditionYellow) {
                        if (*this == STRUCT_CHRONOSPHERE) {
                            shapenum += 29;
                        } else {
                            int last1 = Class->Anims[BSTATE_IDLE].Start + Class->Anims[BSTATE_IDLE].Count;
                            int last2 = Class->Anims[BSTATE_ACTIVE].Start + Class->Anims[BSTATE_ACTIVE].Count;
                            int largest = max(last1, last2);
                            last2 = Class->Anims[BSTATE_AUX1].Start + Class->Anims[BSTATE_AUX1].Count;
                            largest = max(largest, last2);
                            last2 = Class->Anims[BSTATE_AUX2].Start + Class->Anims[BSTATE_AUX2].Count;
                            largest = max(largest, last2);
                            shapenum += largest;
                        }
                    }
                }
            }
        }

        // TF: a building with addon plugs draws its upgrade level's block (healthy and damaged per block). The
        // Upgrade Centre's blocks are keyed by plug type instead, so each socket shows the plug it holds.
        if (UpgradeLevel != 0 && (*this == STRUCT_TSPOWR || *this == STRUCT_TSPLUG)) {
            int block = UpgradeLevel;
            if (*this == STRUCT_TSPLUG) {
                block = TF_Plug_Art_Block(UpgradeTypes[0], (UpgradeLevel >= 2) ? UpgradeTypes[1] : STRUCT_NONE);
            }
            shapenum += block * 2 * (Class->Anims[BSTATE_IDLE].Start + Class->Anims[BSTATE_IDLE].Count);
        }
    }
    return (shapenum);
}

/***********************************************************************************************
 * BuildingClass::Mark -- Building interface to map rendering system.                          *
 *                                                                                             *
 *    This routine is used to mark the map cells so that when it renders                       *
 *    the underlying icons will also be updated as necessary.                                  *
 *                                                                                             *
 * INPUT:   mark  -- Type of image change (MARK_UP, _DOWN, _CHANGE)                            *
 *             MARK_UP  -- Building is removed.                                                *
 *             MARK_CHANGE -- Building changes shape.                                          *
 *             MARK_DOWN -- Building is added.                                                 *
 *                                                                                             *
 * OUTPUT:  bool; Did the mark operation succeed? Failure could be the result of marking down  *
 *                when the building is already marked down, or visa versa.                     *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/31/1994 JLB : Created.                                                                 *
 *   04/15/1994 JLB : Converted to member function.                                            *
 *   04/16/1994 JLB : Added health bar tracking.                                               *
 *   12/23/1994 JLB : Calls low level check before proceeding.                                 *
 *   01/27/1995 JLB : Special road spacer template added.                                      *
 *=============================================================================================*/
bool BuildingClass::Mark(MarkType mark)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (TechnoClass::Mark(mark)) {
        short const* offset = Overlap_List();
        short const* occupy = Occupy_List();
        CELL cell = Coord_Cell(Coord);
        SmudgeType bib;

        switch (mark) {
        case MARK_UP:
            Map.Pick_Up(cell, this);
            if (Class->Bib_And_Offset(bib, cell)) {
                SmudgeClass* smudge = new SmudgeClass(bib);
                if (smudge != NULL) {
                    smudge->Disown(cell);
                    delete smudge;
                }
            }
            break;

        case MARK_DOWN:

            /*
            **	Special wall logic is handled here. A building that is really a wall
            **	gets converted into an overlay wall type when it is placed down. The
            **	actual building object itself is destroyed.
            */
            if (Class->IsWall) {
                switch (Class->Type) {
                case STRUCT_BRICK_WALL:
                    new OverlayClass(OVERLAY_BRICK_WALL, cell, House->Class->House);
                    break;

                case STRUCT_BARBWIRE_WALL:
                    new OverlayClass(OVERLAY_BARBWIRE_WALL, cell, House->Class->House);
                    break;

                case STRUCT_SANDBAG_WALL:
                    new OverlayClass(OVERLAY_SANDBAG_WALL, cell, House->Class->House);
                    break;

                case STRUCT_WOOD_WALL:
                    new OverlayClass(OVERLAY_WOOD_WALL, cell, House->Class->House);
                    break;

                case STRUCT_CYCLONE_WALL:
                    new OverlayClass(OVERLAY_CYCLONE_WALL, cell, House->Class->House);
                    break;

                case STRUCT_FENCE:
                    new OverlayClass(OVERLAY_FENCE, cell, House->Class->House);
                    break;

                case STRUCT_TSWALL:
                    new OverlayClass(OVERLAY_TSWALL, cell, House->Class->House);
                    break;

                case STRUCT_TSNWALL:
                    new OverlayClass(OVERLAY_TSNWALL, cell, House->Class->House);
                    break;

                default:
                    break;
                }
                Transmit_Message(RADIO_OVER_OUT);
                delete this;

            } else {
                if (Can_Enter_Cell(cell) == MOVE_OK) {
                    /*
                    **	Determine if a bib is required for this building. If one is, then
                    **	create and place it.
                    */
                    CELL newcell = cell;
                    if (Class->Bib_And_Offset(bib, newcell)) {
                        new SmudgeClass(bib, Cell_Coord(newcell), Class->IsBase ? House->Class->House : HOUSE_NONE);
                    }

                    Map.Place_Down(cell, this);
                } else {
                    return (false);
                }
            }
            break;

        case MARK_CHANGE_REDRAW:
            Map.Refresh_Cells(cell, Overlap_List(true));
            break;

        default:
            Map.Refresh_Cells(cell, Overlap_List(false));
            Map.Refresh_Cells(cell, occupy);
            break;
        }
        return (true);
    }
    return (false);
}

/***********************************************************************************************
 * BuildingClass::AI -- Handles non-graphic AI processing for buildings.                       *
 *                                                                                             *
 *    This function is to handle the AI logic for the building. The graphic logic (facing,     *
 *    firing, and animation) is handled elsewhere.                                             *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/31/1994 JLB : Created.                                                                 *
 *   12/26/1994 JLB : Handles production.                                                      *
 *   06/11/1995 JLB : Revamped.                                                                *
 *=============================================================================================*/
void BuildingClass::AI(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    Gate_AI();

    // TF: the TS refinery's fireball bursts for 20 frames, then pauses at random (TS NAREFN_B, RandomLoopDelay
    // 10..300 TS frames); its dock lid steps through 5 frames.
    if (*this == STRUCT_TSPROC && BState != BSTATE_CONSTRUCTION) {
        if (TsFlameStage >= 0) {
            if (++TsFlameTick >= 3) {
                TsFlameTick = 0;
                if (++TsFlameStage >= 20) {
                    TsFlameStage = -1;
                    TsFlameTimer = (short)Random_Pick(12, 400);
                }
                Mark(MARK_CHANGE_REDRAW);
            }
        } else if (--TsFlameTimer <= 0) {
            TsFlameStage = 0;
            Mark(MARK_CHANGE_REDRAW);
        }
        if (Ts_Lid_Busy() && ++TsLidTick >= 4) {
            TsLidTick = 0;
            if (TsLidPhase == 1) {
                if (++TsLidStage >= 5) {
                    TsLidPhase = 2;
                }
            } else {
                if (TsLidStage == 0) {
                    TsLidPhase = 0;
                } else {
                    TsLidStage--;
                }
            }
            Mark(MARK_CHANGE_REDRAW);
        }
    }

    /*
    **	Process building animation state changes. Transition to a following state
    **	if there is one specified and the current animation sequence has expired.
    **	This process must occur before mission AI since the mission AI relies on
    **	the bstate change to occur immediately before the MissionClass::AI.
    */
    Animation_AI();

    /*
    **	If now is a good time to act on a new mission, then do so. This process occurs
    **	here because some outside event may have requested a mission change for the building.
    **	Such outside requests (player input) must be initiated BEFORE the normal AI process.
    */
    if (IsReadyToCommence && BState != BSTATE_CONSTRUCTION) {

        /*
        **	Clear the commencement flag ONLY if something actually occurred. By acting
        **	this way, a building can set the IsReadyToCommence flag before it goes
        **	to "sleep" knowing that it will wake up as soon as a new mission comes
        **	along.
        */
        if (Commence()) {
            IsReadyToCommence = false;
        }
    }

    /*
    **	Proceed with normal logic processing. This is where the mission processing
    **	occurs. This call must be located after the animation sequence makes the
    **	transition to the next frame (see above) in order for the mission logic to
    **	act at the exact moment of graphic transition BEFORE it has a chance to
    **	be displayed.
    */
    TechnoClass::AI();

    /*
    **	Bail if the object died in the AI routine.
    */
    if (!IsActive) {
        return;
    }

    /*
    **	Building ammo is instantly reloaded.
    */
    if (!Ammo) {
        Ammo = Class->MaxAmmo;
    }

    /*
    **	If now is a good time to act on a new mission, then do so. This occurs here because
    **	some AI event may have requested a mission change (usually from another mission
    **	state machine). This must occur here before it has a chance to render.
    */
    if (IsReadyToCommence) {

        /*
        **	Clear the commencement flag ONLY if something actually occurred. By acting
        **	this way, a building can set the IsReadyToCommence flag before it goes
        **	to "sleep" knowing that it will wake up as soon as a new mission comes
        **	along.
        */
        if (Commence()) {
            IsReadyToCommence = false;
        }
    }

    /*
    **	If a change of animation was requested, then make the change
    **	now. The building animation system acts independently but subordinate
    **	to the mission state machine system. By performing the animation change-up
    **	here, the mission AI system is ensured of immediate visual affect when it
    **	decides to change the animation state of the building.
    */
    if (QueueBState != BSTATE_NONE) {
        if (BState != QueueBState) {
            BState = QueueBState;
            BuildingTypeClass::AnimControlType const* ctrl = Fetch_Anim_Control();
            if (BState == BSTATE_CONSTRUCTION || BState == BSTATE_IDLE) {
                Set_Rate(Options.Normalize_Delay(ctrl->Rate));
            } else {
                Set_Rate(ctrl->Rate);
            }
            Set_Stage(ctrl->Start);
        }
        QueueBState = BSTATE_NONE;
    }

    /*
    **	If the building's strength has changed, then update the power
    **	accordingly.
    */
    if (Strength != LastStrength) {
        int oldpower = Power_Output();
        LastStrength = Strength;
        int newpower = Power_Output();
        House->Adjust_Power(newpower - oldpower);
    }

    /*
    **	Check to see if the destruction countdown timer is active. If so, then decrement it.
    **	When this timer reaches zero, the building is removed from the map. All the explosions
    **	are presumed to be in progress at this time.
    */
    if (Strength == 0) {
        if (CountDown == 0) {
            Limbo();
            Drop_Debris(WhomToRepay);
            delete this;
        }
        return;
    }

    /*
    **	Charging logic.
    */
    Charging_AI();

    /*
    **	Handle any repair process that may be going on.
    */
    Repair_AI();

    /*
    **	For computer controlled buildings, determine what should be produced and start
    **	production accordingly.
    */
    Factory_AI();

    /*
    **	Check for demolition timeout. When timeout has expired, the building explodes.
    */
    if (IsGoingToBlow && CountDown == 0) {
#ifdef REMASTER_BUILD
        /*
        ** Maybe trigger an achivement. ST - 11/14/2019 1:53PM
        */
        TechnoTypeClass const* object_type = Techno_Type_Class();
        if (object_type) {
            TechnoClass* saboteur = As_Techno(WhomToRepay);
            if (saboteur && saboteur->IsActive && saboteur->House && saboteur->House->IsHuman) {
                On_Achievement_Event(saboteur->House, "BUILDING_DESTROYED_C4", object_type->IniName);
            }
        }
#endif
        int damage = Strength;
        Take_Damage(damage, 0, WARHEAD_FIRE, As_Techno(WhomToRepay), true);
        if (!IsActive) {
            return;
        }
        Mark(MARK_CHANGE);
    }

    /*
    **	Turret equiped buildings must handle turret rotation logic here. This entails
    **	rotating the turret to the desired facing as well as figuring out what that
    **	desired facing should be.
    */
    Rotation_AI();

    /*
    ** Gap Generators need to scan if they've just become activated, or if
    ** the power has just come on enough so they can scan.  Also, they need
    ** to un-jam if the power has just dropped off.
    */
    if (*this == STRUCT_GAP) {
        if (Arm == 0) {
            IsJamming = false;
            Arm = TICKS_PER_MINUTE * Rule.GapRegenInterval + Random_Pick(1, TICKS_PER_SECOND);
        }

        if (!IsJamming) {
            if (House->Power_Fraction() >= 1 && !Is_Immobilized()) {
                Map.Jam_From(Coord_Cell(Center_Coord()), Rule.GapShroudRadius, House);
                IsJamming = true;
            }
        } else {
            if (House->Power_Fraction() < 1 || Is_Immobilized()) {
                IsJamming = false;
                Map.UnJam_From(Coord_Cell(Center_Coord()), Rule.GapShroudRadius, House);
            }
        }
    }

    /*
    ** Radar facilities and SAMs need to check for the proximity of a mobile
    ** radar jammer.
    */
    // TF: the TD and TS radars and the TD SAM site are jammed by the same rules.
    if ((*this == STRUCT_RADAR || *this == STRUCT_TDHQ || *this == STRUCT_TDEYE || *this == STRUCT_TSRADR
         || *this == STRUCT_SAM || *this == STRUCT_TDSAM)
        && (Frame % TICKS_PER_SECOND) == 0) {
        IsJammed = false;
        for (int index = 0; index < Units.Count(); index++) {
            UnitClass* obj = Units.Ptr(index);
            if (obj != NULL && !obj->IsInLimbo && !obj->House->Is_Ally(House) && obj->Class->IsJammer
                && Distance(obj) <= Rule.RadarJamRadius) {

                IsJammed = true;
                break;
            }
        }
    }

    /*
    ** Chronosphere active animation control.
    */
    if (*this == STRUCT_CHRONOSPHERE && BState == BSTATE_ACTIVE && QueueBState == BSTATE_NONE && Scen.FadeTimer == 0) {
        Begin_Mode(BSTATE_IDLE);
    }

    // TF: the TD blossom tree is an inert Neutral building, as terrain takes no HD art. It sheds spores twice
    // every 30 s and, when Tiberium grows, grows TIB01 around itself, never the ore or gems beside it.
    if (*this == STRUCT_TDBLOSSOM) {
        enum
        {
            BLOSSOM_IDLE_FRAME = 34, // fully-open mature bloom (the static hold)
            BLOSSOM_SHED_START = 30, // first open-bloom / spore frame
            BLOSSOM_SHED_END = 54,   // last frame of the SPLIT2 sprite
            BLOSSOM_SHED_RATE = 3,   // game frames per sprite frame during the shed
        };
        int const shedlen = (BLOSSOM_SHED_END - BLOSSOM_SHED_START + 1) * BLOSSOM_SHED_RATE;
        int const period = 30 * TICKS_PER_SECOND; // full still->shed->still cycle
        int phase = (int)((Frame + (long)ID * 37) % period); // stagger so blossoms don't pulse in unison
        int targetframe = BLOSSOM_IDLE_FRAME;
        if (phase < shedlen * 2) { // DOUBLE shed at the top of each cycle
            targetframe = BLOSSOM_SHED_START + ((phase % shedlen) / BLOSSOM_SHED_RATE);
        }
        if (Fetch_Stage() != targetframe) {
            Set_Stage(targetframe);
            Mark(MARK_CHANGE);
        }

        if ((Session.Type == GAME_NORMAL || Session.Options.Tiberium)
            && (Frame % (Rule.GrowthRate * TICKS_PER_MINUTE)) == 0) {
            CELL center = Coord_Cell(Center_Coord());
            bool spread = false;
            for (FacingType i = FACING_N; i < FACING_COUNT; i++) {
                CellClass* nc = Map[center].Adjacent_Cell(i);
                if (nc != NULL && nc->Overlay == OVERLAY_TIB01 && nc->Spread_Tiberium(true)) {
                    spread = true;
                    break;
                }
            }
            if (!spread) {
                for (FacingType i = FACING_N; i < FACING_COUNT; i++) {
                    CellClass* nc = Map[center].Adjacent_Cell(i);
                    if (nc != NULL && nc->Can_Tiberium_Germinate()) {
                        new OverlayClass(OVERLAY_TIB01, nc->Cell_Number());
                        nc->OverlayData = 0;
                        break;
                    }
                }
            }
        }
    }
}

// The Nod Stealth Generator's cloak field: covered objects are made cloakable and Cloaking_AI hides them;
// the driver never cloaks, it only reveals and restores. docs/stealth-generator-spec.md.
enum
{
    TF_STEALTH_RADIUS_CELLS = 10, // coverage radius around the generator
    TF_STEALTH_DETECT_CELLS = 3, // how close an enemy detector must be to reveal a covered object
    TF_STEALTH_REVEAL_HOLD = 15  // frames a forced reveal is held before Cloaking_AI may recloak
};

// True when a working Sensor Array of this house or an ally covers the coordinate: cloaked and buried
// objects there are visible to that house and targetable by it.
bool TF_Is_Sensed(HouseClass const* house, COORDINATE coord)
{
    enum
    {
        MAX_SENSORS = 64
    };
    static long gathered = -1;
    static int count = 0;
    static COORDINATE where[MAX_SENSORS];
    static HouseClass const* owner[MAX_SENSORS];

    if (house == NULL) {
        return (false);
    }
    if (gathered != Frame) {
        gathered = Frame;
        count = 0;
        for (int i = 0; i < Buildings.Count() && count < MAX_SENSORS; i++) {
            BuildingClass const* b = Buildings.Ptr(i);
            if (b != NULL && *b == STRUCT_TSDPSA && b->IsActive && !b->IsInLimbo && b->Strength > 0
                && b->BState != BSTATE_CONSTRUCTION && b->Mission != MISSION_UNLOAD) {
                where[count] = b->Center_Coord();
                owner[count] = b->House;
                count++;
            }
        }
    }
    for (int i = 0; i < count; i++) {
        if ((owner[i] == house || owner[i]->Is_Ally(house))
            && ::Distance(where[i], coord) < TF_SENSOR_RADIUS_CELLS * CELL_LEPTON_W) {
            return (true);
        }
    }
    return (false);
}

// Announces each human house's newly sensed cloaked or buried enemies, with a radar ping, twice a second
// (OpenTS Update_Radar_Position); each line plays at most once every 15 seconds.
void TF_Sensor_Tick(void)
{
    enum
    {
        SCAN_FRAMES = TICKS_PER_SECOND / 2,
        QUIET_FRAMES = TICKS_PER_SECOND * 15,
        MAX_TRACKED = 32
    };
    static TARGET seen[HOUSE_COUNT][MAX_TRACKED];
    static int seen_count[HOUSE_COUNT];
    static long quiet_until[HOUSE_COUNT][2];
    static long last_frame = -1;

    if (Frame < last_frame) {
        memset(seen_count, 0, sizeof(seen_count));
        memset(quiet_until, 0, sizeof(quiet_until));
    }
    last_frame = Frame;
    if (Frame % SCAN_FRAMES != 0) {
        return;
    }
    for (int h = 0; h < Houses.Count(); h++) {
        HouseClass* house = Houses.Ptr(h);
        if (house == NULL || !house->IsActive || !house->IsHuman) {
            continue;
        }
        int hid = house->Class->House;
        TARGET now[MAX_TRACKED];
        int now_count = 0;
        for (int layer = 0; layer < 3 && now_count < MAX_TRACKED; layer++) {
            int count = (layer == 0) ? Units.Count() : ((layer == 1) ? Vessels.Count() : Buildings.Count());
            for (int i = 0; i < count && now_count < MAX_TRACKED; i++) {
                TechnoClass* t = (layer == 0) ? (TechnoClass*)Units.Ptr(i)
                                              : ((layer == 1) ? (TechnoClass*)Vessels.Ptr(i) : (TechnoClass*)Buildings.Ptr(i));
                if (t == NULL || !t->IsActive || t->IsInLimbo || t->House->Is_Ally(house)
                    || (t->Cloak != CLOAKED && !t->Is_Tunneling()) || !TF_Is_Sensed(house, t->Center_Coord())) {
                    continue;
                }
                TARGET target = t->As_Target();
                now[now_count++] = target;
                bool known = false;
                for (int k = 0; k < seen_count[hid] && !known; k++) {
                    known = (seen[hid][k] == target);
                }
                int line = t->Is_Tunneling() ? 1 : 0;
                if (!known && Frame >= quiet_until[hid][line]) {
                    Speak(line ? VOX_TS_SUBTERRANEAN_DETECTED : VOX_TS_CLOAKED_DETECTED, house, t->Center_Coord());
                    quiet_until[hid][line] = Frame + QUIET_FRAMES;
                }
            }
        }
        memcpy(seen[hid], now, now_count * sizeof(TARGET));
        seen_count[hid] = now_count;
    }
}

// True when an enemy stealth detector (a techno whose type has IsScanner) is within range of the object;
// a detector building uses its own sight range instead.
static bool TF_Stealth_Detector_In_Range(TechnoClass const* obj, int range)
{
    COORDINATE oc = obj->Center_Coord();
    HouseClass* owner = obj->House;

    for (int i = 0; i < Units.Count(); i++) {
        UnitClass* u = Units.Ptr(i);
        if (u != NULL && u->IsActive && !u->IsInLimbo && !u->House->Is_Ally(owner)
            && u->Techno_Type_Class()->IsScanner && ::Distance(u->Center_Coord(), oc) <= range) {
            return (true);
        }
    }
    for (int i = 0; i < Infantry.Count(); i++) {
        InfantryClass* u = Infantry.Ptr(i);
        if (u != NULL && u->IsActive && !u->IsInLimbo && !u->House->Is_Ally(owner)
            && u->Techno_Type_Class()->IsScanner && ::Distance(u->Center_Coord(), oc) <= range) {
            return (true);
        }
    }
    for (int i = 0; i < Vessels.Count(); i++) {
        VesselClass* u = Vessels.Ptr(i);
        if (u != NULL && u->IsActive && !u->IsInLimbo && !u->House->Is_Ally(owner)
            && u->Techno_Type_Class()->IsScanner && ::Distance(u->Center_Coord(), oc) <= range) {
            return (true);
        }
    }
    for (int i = 0; i < Buildings.Count(); i++) {
        BuildingClass* b = Buildings.Ptr(i);
        if (b != NULL && b->IsActive && !b->IsInLimbo && !b->House->Is_Ally(owner)
            && b->Class->IsScanner
            && ::Distance(b->Center_Coord(), oc) <= b->Class->SightRange * CELL_LEPTON_W) {
            return (true);
        }
    }
    return (false);
}

// Hides or reveals one object for the stealth generators. Returns true while it still carries cloak state
// we gave it, so the restore pass keeps running until its multi-frame uncloak finishes.
static bool TF_Stealth_Drive(TechnoClass* obj, COORDINATE const* gcoord, HouseClass* const* ghouse, int gcount, int radius, int detect)
{
    if (obj == NULL || !obj->IsActive || obj->IsInLimbo || obj->Strength <= 0) {
        return false;
    }

    if (obj->Techno_Type_Class()->IsCloakable) {
        return false;
    }
    if (obj->What_Am_I() == RTTI_BUILDING && *(BuildingClass*)obj == STRUCT_TDSTEALTH) {
        return false;
    }

    bool covered = false;
    COORDINATE oc = obj->Center_Coord();
    for (int g = 0; g < gcount; g++) {
        if (ghouse[g]->Is_Ally(obj->House) && ::Distance(gcoord[g], oc) <= radius) {
            covered = true;
            break;
        }
    }

    if (!covered) {
        if (obj->IsCloakable && !obj->Techno_Type_Class()->IsCloakable) {
            if (obj->Cloak == CLOAKED || obj->Cloak == CLOAKING) {
                obj->Do_Uncloak();
            }
            if (obj->Cloak == UNCLOAKED) {
                obj->IsCloakable = false;
            }
        }
        return (obj->IsCloakable && !obj->Techno_Type_Class()->IsCloakable);
    }

    // A building in radio contact with an inbound unit must not start cloaking: Do_Cloak runs Detach_All,
    // which clears the unit's NavCom and strands it.
    if (obj->What_Am_I() == RTTI_BUILDING && obj->Cloak == UNCLOAKED
        && ((BuildingClass*)obj)->In_Radio_Contact()) {
        TechnoClass* partner = ((BuildingClass*)obj)->Contact_With_Whom();
        bool in_transit = (partner != NULL && partner->Is_Foot() && Target_Legal(((FootClass*)partner)->NavCom));
        if (in_transit) {
            obj->IsCloakable = false;
            return false;
        }
    }

    obj->IsCloakable = true;

    bool reveal = TF_Stealth_Detector_In_Range(obj, detect);

    if (!reveal && obj->What_Am_I() == RTTI_BUILDING) {
        BuildingClass* b = (BuildingClass*)obj;

        if (b->Is_Weapon_Equipped() && Target_Legal(b->TarCom) && b->In_Range(b->TarCom)) {
            reveal = true;
        }
    }

    if (reveal) {
        if (obj->Cloak == CLOAKED || obj->Cloak == CLOAKING) {
            obj->Do_Uncloak();
        }
        obj->CloakDelay = TF_STEALTH_REVEAL_HOLD;
    }

    return (obj->IsCloakable && !obj->Techno_Type_Class()->IsCloakable);
}

#if TF_DEV_BUILD
/*
**	TF DEV diagnostic: dump each computer house's build state once a second to
**	<prefix>/tf_stealth_ai.log, so we can see empirically whether a stealth-generator
**	base is actually building or stalled. Logs building count over time (rising == it IS
**	building), base-build flag, money, power, next queued structure/unit, and how many of
**	the house's buildings are currently cloaked. Compiled out of release.
*/
static void TF_Log_AI_Build_State(void)
{
    if ((Frame % 60) != 0) {
        return;
    }

    const char* up = getenv("USERPROFILE");
    if (up == NULL) {
        return;
    }
    char path[512];
    snprintf(path, sizeof(path), "%s/tf_stealth_ai.log", up);
    FILE* f = fopen(path, "a");
    if (f == NULL) {
        return;
    }

    for (int h = 0; h < Houses.Count(); h++) {
        HouseClass* hptr = Houses.Ptr(h);
        if (hptr == NULL || !hptr->IsActive || hptr->IsHuman) {
            continue;
        }

        int total = 0;
        int cloaked = 0;
        int conyard = 0;
        char names[256];
        names[0] = 0;
        for (int i = 0; i < Buildings.Count(); i++) {
            BuildingClass* b = Buildings.Ptr(i);
            if (b != NULL && b->IsActive && !b->IsInLimbo && b->House == hptr) {
                total++;
                if (b->Cloak == CLOAKED || b->Cloak == CLOAKING) {
                    cloaked++;
                }
                if (b->Class->Is_Construction_Yard()) {
                    conyard++;
                }
                int len = (int)strlen(names);
                if (len < (int)sizeof(names) - 12) {
                    snprintf(names + len, sizeof(names) - len, "%s%s", (len ? "," : ""), b->Class->IniName);
                }
            }
        }

        /*
        **	Unit census: does the AI still have an undeployed MCV (UNIT_MCV) or a harvester?
        **	An MCV that never became a Construction Yard == a stuck base.
        */
        int units = 0;
        int mcv = 0;
        int harv = 0;
        for (int i = 0; i < Units.Count(); i++) {
            UnitClass* u = Units.Ptr(i);
            if (u != NULL && u->IsActive && !u->IsInLimbo && u->House == hptr) {
                units++;
                if (u->Class->Is_MCV()) {
                    mcv++;
                }
                if (u->Class->Type == UNIT_HARVESTER || u->Class->Type == UNIT_TDHARV
                    || u->Class->Type == UNIT_TSHARV) {
                    harv++;
                }
            }
        }

        fprintf(f,
                "frame=%d house=%s actlike=%d basebuild=%d bldgs=%d conyard=%d cloaked=%d/%d "
                "credits=%d pwr=%d/%d pfrac=%d%% nextbldg=%d nextunit=%d units=%d mcv=%d harv=%d [%s]\n",
                Frame, hptr->Class->IniName, (int)hptr->ActLike, (int)hptr->IsBaseBuilding, total, conyard,
                cloaked, total, hptr->Available_Money(), hptr->Power, hptr->Drain,
                (int)(hptr->Power_Fraction() * 100), (int)hptr->BuildStructure, (int)hptr->BuildUnit, units, mcv,
                harv, names);
    }

    fclose(f);
}
#endif

void BuildingClass::Process_Stealth_Generators(void)
{
#if TF_DEV_BUILD
    TF_Log_AI_Build_State();
#endif

    // Set while a generator exists and until every object we cloaked has uncloaked. Cleared sooner, Cloaking_AI
    // re-cloaks them with IsCloakable still set, and the base stays stealthed with no generator.
    static bool _restore_pending = false;

    enum
    {
        MAX_GENS = 64
    };
    COORDINATE gcoord[MAX_GENS];
    HouseClass* ghouse[MAX_GENS];
    int gcount = 0;

    for (int i = 0; i < Buildings.Count() && gcount < MAX_GENS; i++) {
        BuildingClass* gen = Buildings.Ptr(i);
        if (gen != NULL && gen->IsActive && !gen->IsInLimbo && *gen == STRUCT_TDSTEALTH
            && gen->House->Power_Fraction() >= 1 && !gen->Is_Immobilized()) {
            gcoord[gcount] = gen->Center_Coord();
            ghouse[gcount] = gen->House;
            gcount++;
        }
    }

    bool have_gens = (gcount > 0);
    if (have_gens) {
        _restore_pending = true;
    }
    if (!have_gens && !_restore_pending) {
        return;
    }

    int radius = TF_STEALTH_RADIUS_CELLS * CELL_LEPTON_W;
    int detect = TF_STEALTH_DETECT_CELLS * CELL_LEPTON_W;

    bool remaining = false;
    for (int i = 0; i < Buildings.Count(); i++) {
        remaining |= TF_Stealth_Drive(Buildings.Ptr(i), gcoord, ghouse, gcount, radius, detect);
    }
    for (int i = 0; i < Units.Count(); i++) {
        remaining |= TF_Stealth_Drive(Units.Ptr(i), gcoord, ghouse, gcount, radius, detect);
    }
    for (int i = 0; i < Infantry.Count(); i++) {
        remaining |= TF_Stealth_Drive(Infantry.Ptr(i), gcoord, ghouse, gcount, radius, detect);
    }
    for (int i = 0; i < Aircraft.Count(); i++) {
        remaining |= TF_Stealth_Drive(Aircraft.Ptr(i), gcoord, ghouse, gcount, radius, detect);
    }

    if (!have_gens && !remaining) {
        _restore_pending = false;
    }
}

// Set while a component tower plug replaces the bare tower it was placed on, so the turret installs straight
// on instead of the tower building up again. Set and cleared inside one Unlimbo.
static bool TFPlugInstallInProgress = false;

/***********************************************************************************************
 * BuildingClass::Unlimbo -- Removes a building from limbo state.                              *
 *                                                                                             *
 *    Use this routine to transform a building that has been held in limbo                     *
 *    state, into one that really exists on the map. Once a building as                        *
 *    been unlimboed, then it becomes a normal object in the game world.                       *
 *                                                                                             *
 * INPUT:   pos   -- The position to place the building on the map.                            *
 *                                                                                             *
 *          dir (optional) -- not used for this class                                          *
 *                                                                                             *
 * OUTPUT:  bool; Was the unlimbo successful?                                                  *
 *                                                                                             *
 * WARNINGS:   The unlimbo operation might not be successful if the                            *
 *             building could not be placed at the location specified.                         *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   04/16/1994 JLB : Created.                                                                 *
 *   06/07/1994 JLB : Matches virtual function format for base class.                          *
 *   05/09/1995 JLB : Handles wall placement.                                                  *
 *   06/18/1995 JLB : Checks for wall legality before placing down.                            *
 *=============================================================================================*/
bool BuildingClass::Unlimbo(COORDINATE coord, DirType dir)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    /*
    **	If this is a wall type building, then it never gets unlimboed. Instead, it gets
    **	converted to an overlay type.
    */
    if (Class->IsWall) {
        if (Can_Enter_Cell(Coord_Cell(coord), FACING_NONE) == MOVE_OK) {
            OverlayType otype = OVERLAY_NONE;
            switch (Class->Type) {
            case STRUCT_SANDBAG_WALL:
                otype = OVERLAY_SANDBAG_WALL;
                break;

            case STRUCT_CYCLONE_WALL:
                otype = OVERLAY_CYCLONE_WALL;
                break;

            case STRUCT_BRICK_WALL:
                otype = OVERLAY_BRICK_WALL;
                break;

            case STRUCT_BARBWIRE_WALL:
                otype = OVERLAY_BARBWIRE_WALL;
                break;

            case STRUCT_WOOD_WALL:
                otype = OVERLAY_WOOD_WALL;
                break;

            case STRUCT_FENCE:
                otype = OVERLAY_FENCE;
                break;

            case STRUCT_TSWALL:
                otype = OVERLAY_TSWALL;
                break;

            case STRUCT_TSNWALL:
                otype = OVERLAY_TSNWALL;
                break;

            default:
                otype = OVERLAY_NONE;
                break;
            }
            if (otype != OVERLAY_NONE) {
                ObjectClass* o = OverlayTypeClass::As_Reference(otype).Create_One_Of(House);
                if (o && o->Unlimbo(coord)) {
                    Map[coord].Owner = House->Class->House;
                    Transmit_Message(RADIO_OVER_OUT);
                    Map.Sight_From(Coord_Cell(coord), Class->SightRange, House);
                    delete this;
                    return (true);
                }
            }
        }
        return (false);
    }

    // TF: an addon plug installs into the building under it (power, full strength) and deletes itself. A tower
    // plug instead replaces the bare tower, keeping its health ratio, and unlimbos as a normal building.
    bool tf_plug_swap = false;

    if (Class->PowersUpBuilding != STRUCT_NONE) {
        BuildingClass* host = Map[Coord_Cell(coord)].Cell_Building();
        bool swapped = false;
        if (host != NULL && *host == STRUCT_TSCTWR && host->Can_Upgrade(Class, House)) {
            coord = host->Coord;
            fixed ratio = host->Health_Ratio();
            host->Transmit_Message(RADIO_OVER_OUT);
            host->Limbo();
            delete host;
            host = NULL;
            Strength = (int)Class->MaxStrength * ratio;
            if (Strength < 1) {
                Strength = 1;
            }
            swapped = true;
            tf_plug_swap = true;
            TFPlugInstallInProgress = true;
        }
        if (!swapped) {
        if (host != NULL && host->Can_Upgrade(Class, House)) {
            int oldpower = host->Power_Output();
            host->UpgradeTypes[host->UpgradeLevel++] = Class->Type;
            host->House->Adjust_Power(host->Power_Output() - oldpower);
            host->House->Adjust_Drain(Class->Drain);
            host->Strength = host->Class->MaxStrength;
            host->House->IsRecalcNeeded = true;
            host->Mark(MARK_CHANGE);
            // Break the builder's radio link before deleting: Who_Can_Build_Me skips a builder in radio contact,
            // so a dangling link locks the construction yard out of all further placement.
            Transmit_Message(RADIO_OVER_OUT);
            delete this;
            return (true);
        }
        return (false);
        }
    }

    // TF: a component tower or gate placed on walls replaces them. The movement zones are rebuilt so a gate
    // links the zones either side of its wall line, and the wall joins are redrawn once it stands.
    bool joins_walls = (TF_Is_Wall_Tower(Class->Type) || TF_Gate_Info(Class->Type) != NULL);
    if (*this == STRUCT_TSCTWR || TF_Gate_Info(Class->Type) != NULL) {
        bool walls_gone = false;
        short const* offset = Class->Occupy_List();
        while (offset != NULL && *offset != REFRESH_EOL) {
            CellClass& tc = Map[(CELL)(Coord_Cell(coord) + *offset++)];
            if (TF_Is_Tower_Joint_Wall(tc.Overlay)) {
                tc.Overlay = OVERLAY_NONE;
                tc.OverlayData = 0;
                Detach_This_From_All(::As_Target(tc.Cell_Number()), true);
                tc.Recalc_Attributes();
                tc.Redraw_Objects();
                walls_gone = true;
            }
        }
        if (walls_gone) {
            Map.Zone_Reset(MZONEF_CRUSHER | MZONEF_NORMAL | MZONEF_HOVER);
        }
    }

    /*
    **	Normal building unlimbo process.
    */
    if (TechnoClass::Unlimbo(coord, dir)) {

        if (joins_walls) {
            short const* offset = Class->Occupy_List();
            while (offset != NULL && *offset != REFRESH_EOL) {
                Map[(CELL)(Coord_Cell(Coord) + *offset++)].Wall_Update(true);
            }
        }

        /*
        **	Ensure that the owning house knows about the
        **	new object.
        */
        // TF: types past 31 take their vanilla counterpart's scan bit, if any (TF_Building_Scan_Bit); prerequisites
        // count every type in ActiveBQuantity.
        int btype = (int)Class->Type;
        long scanbit = TF_Building_Scan_Bit(btype);
        House->BScan |= scanbit;
        House->ActiveBScan |= scanbit;
        House->Active_Building_Add(btype);

        /*
        **	Recalculate the center point of the house's base.
        */
        House->Recalc_Center();

        /*
        **	Update the total factory type, assuming this building has a factory.
        */
        House->Active_Add(this);

        /*
        **	Possibly the sidebar will be affected by this addition.
        */
        House->IsRecalcNeeded = true;
        LastStrength = 0;

        // Changes to support client/server multiplayer. ST - 8/2/2019 2:36PM
        // if ((!IsDiscoveredByPlayer && Map[coord].IsVisible) || Session.Type != GAME_NORMAL) {
        if ((!Is_Discovered_By_Player(House) && Map[coord].Is_Visible(House)) || Session.Type != GAME_NORMAL) {
            if (House->IsHuman) {
                // Revealed(PlayerPtr);
                Revealed(House);
            }
        }
        if (!House->IsHuman) {
            Revealed(House);
        }

        // Changes to support client/server multiplayer. ST - 8/2/2019 2:36PM
        // if (IsOwnedByPlayer) {
        if (Is_Owned_By_Player()) {
            Map.PowerClass::IsToRedraw = true;
            Map.Flag_To_Redraw(false);
        }

        // TF: a building takes the ActLike of its side, so a captured one offers its own tree. A building both RA
        // sides or both TD factions can own keeps its owner's ActLike.
        int both_ra_sides = HOUSEF_ALLIES | HOUSEF_SOVIET;
        int both_td_sides = HOUSEF_GDI | HOUSEF_NOD;
        if ((Class->Ownable & both_ra_sides) != both_ra_sides
            && (Class->Ownable & both_td_sides) != both_td_sides) {
            if (Class->Ownable & HOUSEF_ALLIES) {
                ActLike = HOUSE_GREECE; // Allied placeholder
            } else if (Class->Ownable & HOUSEF_SOVIET) {
                ActLike = HOUSE_USSR; // Soviet placeholder
            } else if (Class->Ownable & HOUSEF_GDI) {
                ActLike = HOUSE_GOOD; // GDI
            } else if (Class->Ownable & HOUSEF_NOD) {
                ActLike = HOUSE_BAD; // Nod
            }
        }

        // TF: a tower plug installs rather than builds, so it frees its builder and opens here. Who_Can_Build_Me
        // skips a builder in radio contact: a dangling link locks the yard out of all further placement.
        if (tf_plug_swap) {
            Transmit_Message(RADIO_OVER_OUT);
            Grand_Opening();
        }

        return (true);
    }
    return (false);
}

/***********************************************************************************************
 * BuildingClass::Take_Damage -- Inflicts damage points upon a building.                       *
 *                                                                                             *
 *    This routine will inflict damage points upon the specified building.                     *
 *    It will handle the damage animation and building destruction. Use                        *
 *    this routine whenever a building is attacked.                                            *
 *                                                                                             *
 * INPUT:   damage   -- Amount of damage to inflict.                                           *
 *                                                                                             *
 *          distance -- The distance from the damage center point to the object's center point.*
 *                                                                                             *
 *          warhead  -- The kind of damage to inflict.                                         *
 *                                                                                             *
 *          source   -- The source of the damage. This is used to change targeting.            *
 *                                                                                             *
 *          forced   -- Is the damage forced upon the object regardless of whether it          *
 *                      is normally immune?                                                    *
 *                                                                                             *
 * OUTPUT:  true/false; Was the building destroyed?                                            *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/21/1991     : Created.                                                                 *
 *   04/15/1994 JLB : Converted to member function.                                            *
 *   04/16/1994 JLB : Added warhead modifier to damage.                                        *
 *   06/03/1994 JLB : Added source of damage as target value.                                  *
 *   06/20/1994 JLB : Source is a base class pointer.                                          *
 *   11/22/1994 JLB : Shares base damage handler for techno objects.                           *
 *   07/15/1995 JLB : Power ratio gets adjusted.                                               *
 *=============================================================================================*/
ResultType BuildingClass::Take_Damage(int& damage, int distance, WarheadType warhead, TechnoClass* source, bool forced)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    ResultType res = RESULT_NONE;
    int shakes;

    // TF: a blossom tree takes no damage, forced included, as in TD; its art has no damaged frames.
    if (*this == STRUCT_TDBLOSSOM) {
        damage = 0;
        return (RESULT_NONE);
    }

    // TF: a live Firestorm wall section takes no damage; each hit drains the field a tenth of a frame per
    // point (TS DamageToFirestormDamageCoefficient=.1).
    if (*this == STRUCT_TSFSDF && House->IsFirestormLive && !forced) {
        House->SuperWeapon[SPC_TS_FIRESTORM].Drain(damage / 10);
        damage = 0;
        return (RESULT_NONE);
    }

    if (this != source /*&& !Class->IsInsignificant*/) {

        if (source) {
            House->LATime = Frame;
            House->LAType = source->What_Am_I();
            House->LAZone = House->Which_Zone(this);
            House->LAEnemy = source->Owner();

            if (!House->Is_Ally(source)) {
                House->Enemy = source->Owner();
            }

            Base_Is_Attacked(source);
        }

        short const* offset = Occupy_List();

        /*
        ** Memorize who they used to be in radio contact with.
        */
        TechnoClass* tech = Contact_With_Whom();

        // TF: the TD SAM takes half damage while underground, as in TD.
        if (*this == STRUCT_TDSAM && Status == TDSAM_UNDERGROUND) {
            damage /= 2;
            damage++; // Never less than 1.
        }

        /*
        **	Perform the low level damage assessment.
        */
        res = TechnoClass::Take_Damage(damage, distance, warhead, source, forced);
        switch (res) {
        case RESULT_DESTROYED:

            /*
            **	Add the building to the base prebuild list if allowed. This will force
            **	the computer to rebuild this structure if it can.
            */
            if (IsToRebuild && Class->Level != -1 && Base.House == House->Class->House && Base.Get_Node(this) == 0) {
                //				if (IsToRebuild && Class->IsBuildable && Base.House == House->Class->House &&
                //Base.Get_Node(this) == 0) {
                Base.Nodes.Add(BaseNodeClass(Class->Type, Coord_Cell(Coord)));
            }

            /*
            **	Destroy all attached objects.
            */
            while (Attached_Object()) {
                FootClass* obj = Detach_Object();

                Detach_All(true);
                delete obj;
            }

            /*
            ** If we were in contact with a landed plane, blow the plane up too.
            */
            if (tech && tech->IsActive && tech->What_Am_I() == RTTI_AIRCRAFT
                && ((AircraftClass*)tech)->Class->IsFixedWing
                && ((AircraftClass*)tech)->In_Which_Layer() == LAYER_GROUND) {
                int damage = 500;
                tech->Take_Damage(damage, 0, WARHEAD_AP, source, forced);
            }

            Sound_Effect(VOC_KABOOM22, Coord);
            while (*offset != REFRESH_EOL) {
                COORDINATE scatter_coord;
                int delay;
                int loop;
                CELL cell = Coord_Cell(Coord) + *offset++;

                /*
                **	If the building is destroyed, then lots of
                **	explosions occur.
                */
                new SmudgeClass(Random_Pick(SMUDGE_CRATER1, SMUDGE_CRATER6), Cell_Coord(cell));
                if (Percent_Chance(50)) {
                    scatter_coord = Coord_Scatter(Cell_Coord(cell), 0x0080);
                    delay = Random_Pick(0, 7);
                    loop = Random_Pick(1, 3);
                    new AnimClass(ANIM_FIRE_SMALL, scatter_coord, delay, loop);

                    if (Percent_Chance(50)) {
                        scatter_coord = Coord_Scatter(Cell_Coord(cell), 0x0040);
                        delay = Random_Pick(0, 7);
                        loop = Random_Pick(1, 3);
                        new AnimClass(ANIM_FIRE_MED, scatter_coord, delay, loop);
                    }
                }
                scatter_coord = Coord_Scatter(Cell_Coord(cell), 0x0040);
                delay = Random_Pick(0, 3);
                new AnimClass(ANIM_FBALL1, scatter_coord, delay);
            }

            shakes = Class->Cost_Of() / 400;
            if (shakes) {
                Shake_The_Screen(shakes, Owner());
                if (source && Owner() != source->Owner()) {
                    Shake_The_Screen(shakes, source->Owner());
                }
            }
            Sound_Effect(VOC_CRUMBLE, Coord);
            if (Mission == MISSION_DECONSTRUCTION) {
                CountDown = 0;
                Set_Rate(0);
            } else {
                CountDown = 8;
            }

            /*
            **	If it is in radio contact and the object seems to be attached, then tell
            **	it to run away.
            */
            if (In_Radio_Contact() && Transmit_Message(RADIO_NEED_TO_MOVE) == RADIO_ROGER) {
                Transmit_Message(RADIO_RUN_AWAY);
            }

            /*
            **	A force destruction will not generate survivors.
            */
            if (forced || *this == STRUCT_KENNEL) {
                IsSurvivorless = true;
            }

            /*
            ** Destruction of a radar facility or advanced communications
            ** center will cause the spiedby field to change...
            */
            if (SpiedBy) {
                SpiedBy = 0;
                StructType struc = *this;
                if (struc == STRUCT_RADAR || struc == STRUCT_TDHQ || struc == STRUCT_TDEYE || struc == STRUCT_TSRADR) {
                    Update_Radar_Spied();
                }
            }

            /*
            ** Destruction of a gap generator will cause the cells it affects
            ** to stop being jammed.
            */
            if (*this == STRUCT_GAP) {
                Remove_Gap_Effect();
            }

            /*
            ** Destruction of a shipyard or sub pen may cause attached ships
            ** who are repairing themselves to discontinue repairs.
            */
            if (*this == STRUCT_SHIP_YARD || *this == STRUCT_SUB_PEN || *this == STRUCT_TDGYARD
                || *this == STRUCT_TDNPEN) {
                for (int index = 0; index < Vessels.Count(); index++) {
                    VesselClass* obj = Vessels.Ptr(index);
                    if (obj && !obj->IsInLimbo && obj->House == House) {
                        if (obj->IsSelfRepairing) {
                            if (::Distance(Center_Coord(), obj->Center_Coord()) < 0x0200) {
                                obj->IsSelfRepairing = false;
                                obj->IsToSelfRepair = false;
                            }
                        }
                    }
                }
            }

            /*
            ** Destruction of a barrel will cause the surrounding squares to
            ** be hit with damage.
            */
            if (*this == STRUCT_BARREL || *this == STRUCT_BARREL3) {
                COORDINATE center = Center_Coord();
                CELL cellcenter = Coord_Cell(center);

                BulletClass* bullet;

                bullet = new BulletClass(BULLET_INVISIBLE,
                                         ::As_Target(Adjacent_Cell(cellcenter, FACING_N)),
                                         0,
                                         200,
                                         WARHEAD_FIRE,
                                         MPH_MEDIUM_FAST);
                if (bullet) {
                    bullet->Unlimbo(center, DIR_N);
                }

                bullet = new BulletClass(BULLET_INVISIBLE,
                                         ::As_Target(Adjacent_Cell(cellcenter, FACING_E)),
                                         0,
                                         200,
                                         WARHEAD_FIRE,
                                         MPH_MEDIUM_FAST);
                if (bullet) {
                    bullet->Unlimbo(center, DIR_E);
                }

                bullet = new BulletClass(BULLET_INVISIBLE,
                                         ::As_Target(Adjacent_Cell(cellcenter, FACING_S)),
                                         0,
                                         200,
                                         WARHEAD_FIRE,
                                         MPH_MEDIUM_FAST);
                if (bullet) {
                    bullet->Unlimbo(center, DIR_S);
                }

                bullet = new BulletClass(BULLET_INVISIBLE,
                                         ::As_Target(Adjacent_Cell(cellcenter, FACING_W)),
                                         0,
                                         200,
                                         WARHEAD_FIRE,
                                         MPH_MEDIUM_FAST);
                if (bullet) {
                    bullet->Unlimbo(center, DIR_W);
                }
            }

            if (House) {
                House->Check_Pertinent_Structures();
            }

            break;

        case RESULT_HALF:
            if (*this == STRUCT_PUMP) {
                AnimClass* anim = new AnimClass(ANIM_OILFIELD_BURN, Coord_Add(Coord, 0x00400130L), 1);
                if (anim) {
                    anim->Attach_To(this);
                }
            }
            // Fall into next case.

        case RESULT_MAJOR:
            Sound_Effect(VOC_KABOOM1, Coord);
            while (*offset != REFRESH_EOL) {
                CELL cell = Coord_Cell(Coord) + *offset++;
                AnimClass* anim = NULL;

                /*
                **	Show pieces of fire to indicate that a significant change in
                **	damage level has occurred.
                */
                if (warhead == WARHEAD_FIRE) {
                    switch (Random_Pick(0, 5 + Class->Width() + Class->Height())) {
                    case 0:
                        break;

                    case 1:
                    case 2:
                    case 3:
                    case 4:
                    case 5: {
                        COORDINATE scatter_coord = Coord_Scatter(Cell_Coord(cell), 0x0060);
                        int loop = Random_Pick(1, 3);
                        anim = new AnimClass(ANIM_ON_FIRE_SMALL, scatter_coord, 0, loop);
                        break;
                    }

                    case 6:
                    case 7:
                    case 8: {
                        COORDINATE scatter_coord = Coord_Scatter(Cell_Coord(cell), 0x0060);
                        int loop = Random_Pick(1, 3);
                        anim = new AnimClass(ANIM_ON_FIRE_MED, scatter_coord, 0, loop);
                        break;
                    }

                    case 9:
                        anim = new AnimClass(ANIM_ON_FIRE_BIG, Coord_Scatter(Cell_Coord(cell), 0x0060), 0, 1);
                        break;

                    default:
                        break;
                    }
                } else {
                    if (Percent_Chance(50)) {
                        /*
                        ** Building may catch on fire, but only if it wasn't a
                        ** renovator that caused the damage.
                        */
                        if (source == NULL || source->What_Am_I() != RTTI_INFANTRY
                            || *(InfantryClass*)source != INFANTRY_RENOVATOR) {
                            COORDINATE scatter_coord = Coord_Scatter(Cell_Coord(cell), 0x0060);
                            int delay = Random_Pick(0, 7);
                            int loop = Random_Pick(1, 3);
                            anim = new AnimClass(ANIM_FIRE_SMALL, scatter_coord, delay, loop);
                        }
                    }
                }
                /*
                **	If the animation was created, then attach it to the building.
                */
                if (anim) {
                    anim->Attach_To(this);
                }
            }
            break;

        case RESULT_NONE:
            break;

        case RESULT_LIGHT:
            break;
        }

        if (source && res != RESULT_NONE) {

            /*
            **	If any damage occurred, then inform the house of this fact. If it is the player's
            **	house, it might announce this fact.
            */
            if (!Class->IsInsignificant) {
                House->Attacked(this);
            }

            /*
            ** Save the type of the house that's doing the damage, so if the building burns
            ** to death credit can still be given for the kill
            */
            WhoLastHurtMe = source->Owner();

            /*
            **	When certain buildings are hit, they "snap out of it" and
            **	return fire if they are able and allowed.
            */
            // TF: the TD SAM, like the SAM, fires only at aircraft, so it never returns fire on a ground attacker.
            if (*this != STRUCT_SAM && *this != STRUCT_AAGUN && *this != STRUCT_TDSAM && !House->Is_Ally(source) && Class->PrimaryWeapon != NULL
                && (!Target_Legal(TarCom) || !In_Range(TarCom))) {

                if (source->What_Am_I() != RTTI_AIRCRAFT && (!House->IsHuman || Rule.IsSmartDefense)) {
                    Assign_Target(source->As_Target());
                } else {

                    /*
                    **	Generate a random rotation effect since there is nothing else that this
                    **	building can do.
                    */
                    if (!PrimaryFacing.Is_Rotating()) {
                        PrimaryFacing.Set_Desired(Random_Pick(DIR_N, DIR_MAX));
                    }
                }
            }
        }
    }

    return (res);
}

/***********************************************************************************************
 * BuildingClass::new -- Allocates a building object from building pool.                       *
 *                                                                                             *
 *    This routine will allocate a building slot from the building alloc                       *
 *    system.                                                                                  *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the allocated building. If NULL is                       *
 *          returned, then this indicates a failure to allocate.                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   04/11/1994 JLB : Created.                                                                 *
 *   04/21/1994 JLB : Converted to operator new.                                               *
 *   05/17/1994 JLB : Revamped allocation scheme                                               *
 *   07/29/1994 JLB : Simplified.                                                              *
 *=============================================================================================*/
void* BuildingClass::operator new(size_t) noexcept
{
    void* ptr = Buildings.Allocate();
    if (ptr) {
        ((BuildingClass*)ptr)->Set_Active();
    }
    return (ptr);
}

/***********************************************************************************************
 * BuildingClass::delete -- Deallocates building object.                                       *
 *                                                                                             *
 *    This is the memory deallocation operation for a building object.                         *
 *    Since buildings are allocated out of a fixed memory block, all that                      *
 *    is needed is to flag the unit as inactive.                                               *
 *                                                                                             *
 * INPUT:   ptr   -- Pointer to building to deallocate.                                        *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   04/21/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::operator delete(void* ptr)
{
    if (ptr) {
        ((BuildingClass*)ptr)->IsActive = false;
    }
    Buildings.Free((BuildingClass*)ptr);
}

/***********************************************************************************************
 * BuildingClass::BuildingClass -- Constructor for buildings.                                  *
 *                                                                                             *
 *    This routine inserts a building into the object tracking system.                         *
 *    It is placed into a limbo state unless a location is provided for                        *
 *    it to unlimbo at.                                                                        *
 *                                                                                             *
 * INPUT:   type  -- The structure type to make this object.                                   *
 *                                                                                             *
 *          house -- The owner of this building.                                               *
 *                                                                                             *
 *          pos   -- The position to unlimbo the building. If -1 is                            *
 *                   specified, then the building remains in a limbo                           *
 *                   state.                                                                    *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   04/21/1994 JLB : Created.                                                                 *
 *   08/07/1995 JLB : Fixed act like value to match expected value.                            *
 *=============================================================================================*/
BuildingClass::BuildingClass(BuildingTypeClass const* typeptr, HousesType house)
    : TechnoClass(RTTI_BUILDING, Buildings.ID(this), house)
    , Class((BuildingTypeClass*)typeptr)
    , Factory(0)
    , ActLike(House->ActLike)
    , IsToRebuild(false)
    , IsToRepair(false)
    , IsAllowedToSell(true)
    , IsReadyToCommence(false)
    , IsRepairing(false)
    , IsWrenchVisible(false)
    , IsGoingToBlow(false)
    , IsSurvivorless(false)
    , IsCharging(false)
    , IsCharged(false)
    , TsFlameStage(-1)
    , TsFlameTick(0)
    , TsFlameTimer(30)
    , TsLidPhase(0)
    , TsLidStage(0)
    , TsLidTick(0)
    , UpgradeLevel(0)
    , IsCaptured(false)
    , IsJamming(false)
    , IsJammed(false)
    , HasFired(false)
    , HasOpened(false)
    , CountDown(0)
    , BState(BSTATE_NONE)
    , QueueBState(BSTATE_NONE)
    , WhoLastHurtMe(house)
    , WhomToRepay(TARGET_NONE)
    , AnimToTrack(TARGET_NONE)
    , LastStrength(0)
    , PlacementDelay(0)
    , RallyPoint(TARGET_NONE)
    , TFPackNav(TARGET_NONE)
    , GateHold(0)
{
    House->Tracking_Add(this);
    for (int uidx = 0; uidx < (int)(sizeof(UpgradeTypes) / sizeof(UpgradeTypes[0])); uidx++) {
        UpgradeTypes[uidx] = STRUCT_NONE;
    }
    IsSecondShot = !Class->Is_Two_Shooter();
    Strength = Class->MaxStrength;
    Ammo = Class->MaxAmmo;

    // TF: buildings copy their type's Cloakable flag like the other techno classes, for the Stealth Generator.
    IsCloakable = Class->IsCloakable;

    /*
    **	If the building could never be built, then it can never be sold either. This
    **	is due to the lack of buildup animation.
    */
    if (Class->Get_Buildup_Data() != NULL) {
        //	if (!Class->IsBuildable) {
        IsAllowedToSell = false;
    }

    //	if (Session.Type == GAME_INTERNET) {
    //		House->BuildingTotals->Increment_Unit_Total( (int) type);
    //	}
}

// Builds from the type the StructType resolves to. A caller holding the BuildingTypeClass itself passes
// it instead, so Class is that class.
BuildingClass::BuildingClass(StructType type, HousesType house)
    : BuildingClass(BuildingTypes.Ptr((int)type), house)
{
}

/***********************************************************************************************
 * BuildingClass::~BuildingClass -- Destructor for building type objects.                      *
 *                                                                                             *
 *    This destructor for building objects will put the building in limbo if possible.         *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/18/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
BuildingClass::~BuildingClass(void)
{
    if (GameActive && Class) {
        if (House) {
            House->Tracking_Remove(this);
        }
        BuildingClass::Limbo();
    }
    Class = 0;

    delete (FactoryClass*)Factory;
    Factory = 0;
    ID = -1;
}

/***********************************************************************************************
 * BuildingClass::Drop_Debris -- Drops rubble when building is destroyed.                      *
 *                                                                                             *
 *    This routine is called when a building is destroyed. It handles                          *
 *    placing the rubble down.                                                                 *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/14/1994 JLB : Created.                                                                 *
 *   06/13/1995 JLB : Added smoke and normal infantry survivor possibility.                    *
 *   07/16/1995 JLB : Survival rate depends on if captured or sabotaged.                       *
 *=============================================================================================*/
void BuildingClass::Drop_Debris(TARGET source)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    CELL const* offset;
    CELL cell;

    /*
    **	Generate random survivors from the destroyed building.
    */
    cell = Coord_Cell(Coord);
    offset = Occupy_List();
    int odds = 2;
    if (Target_Legal(WhomToRepay))
        odds -= 1;
    if (IsCaptured)
        odds += 6;
    int count = How_Many_Survivors();
    while (*offset != REFRESH_EOL) {
        CELL newcell;

        newcell = cell + *offset++;
        CellClass const* cellptr = &Map[newcell];

        /*
        **	Infantry could run out of a destroyed building.
        */
        if (!House->IsToDie && count > 0) {
            InfantryClass* i = NULL;

            if (Random_Pick(0, odds) == 1) {
                i = NULL;
                InfantryType typ = Crew_Type();
                if (typ != INFANTRY_NONE)
                    i = new InfantryClass(typ, House->Class->House);
                if (i != NULL) {
                    if (Class->Get_Buildup_Data() != NULL && i->Class->IsNominal)
                        i->IsTechnician = true;
                    ScenarioInit++;
                    if (i->Unlimbo(Cell_Coord(newcell), DIR_N)) {
                        count--;
                        i->Strength = Random_Pick(5, (int)i->Class->MaxStrength);
                        i->Scatter(0, true);
                        if (source != TARGET_NONE && !House->Is_Ally(As_Object(source))) {
                            i->Assign_Mission(MISSION_ATTACK);
                            i->Assign_Target(source);
                        } else {
                            if (House->IsHuman) {
                                i->Assign_Mission(MISSION_GUARD);
                            } else {
                                i->Assign_Mission(MISSION_HUNT);
                            }
                        }
                    } else {
                        delete i;
                    }
                    ScenarioInit--;
                }
            }
        }

        /*
        **	Smoke and fire only appear on terrestrail cells. They should not appear on
        **	rivers, clifs, or water cells.
        */
        if (cellptr->Is_Clear_To_Move(SPEED_TRACK, true, true)) {

            /*
            **	Possibly add some smoke rising from the ashes of the building.
            */
            switch (Random_Pick(0, 5)) {
            case 0:
            case 1:
            case 2: {
                COORDINATE scatter_coord = Coord_Scatter(Cell_Coord(newcell), 0x0050, false);
                int delay = Random_Pick(0, 5);
                int loop = Random_Pick(1, 2);
                new AnimClass(ANIM_SMOKE_M, scatter_coord, delay, loop);
                break;
            }

            default:
                break;
            }

            /*
            **	The building always scars the ground in some fashion.
            */
            if (Percent_Chance(25)) {
                new SmudgeClass(Random_Pick(SMUDGE_SCORCH1, SMUDGE_SCORCH6), Cell_Coord(newcell));
            } else {
                SmudgeType type = Random_Pick(SMUDGE_CRATER1, SMUDGE_CRATER6);
                COORDINATE scatter_coord = Coord_Scatter(Cell_Coord(newcell), 0x0080, false);
                new SmudgeClass(type, scatter_coord);
            }
        }
    }
}

/***********************************************************************************************
 * BuildingClass::Active_Click_With -- Handles clicking on the map while the building is selected.*
 *                                                                                             *
 *    This interface routine handles when the player clicks on the map while this building     *
 *    is currently selected. This is used to assign an override target to a turret or          *
 *    guard tower.                                                                             *
 *                                                                                             *
 * INPUT:   target   -- The target that was clicked upon.                                      *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/28/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Active_Click_With(ActionType action, ObjectClass* object)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (action == ACTION_ATTACK && object != NULL) {
        Player_Assign_Mission(MISSION_ATTACK, object->As_Target());
    }

    if (action == ACTION_TOGGLE_PRIMARY && Class->Is_Factory()) {
        OutList.Add(EventClass(EventClass::PRIMARY, TargetClass(this)));
    }

    // TF: a deployed TS building packs up on a deploy order: a click on itself or the deploy key.
    if (action == ACTION_SELF && TF_Packs_Into(this) != UNIT_NONE) {
        Player_Assign_Mission(MISSION_UNLOAD);
    }

    // TF: rally points (CFE Patch Redux port): a force-move click on a unit or building rallies onto it.
    if (action == ACTION_MOVE && object != NULL && Can_Have_Rally_Point()) {
        Player_Set_Rally_Point(object->As_Target());
    }
}

// TF: rally points, ported from CFE Patch Redux (GPL v3). docs/cfe-port-plan.md.

// True for a factory of infantry, vehicles or vessels, and for a repair bay, whose repaired units leave
// for its rally point.
bool BuildingClass::Can_Have_Rally_Point(void) const
{
    if (Class->Type == STRUCT_REPAIR || Class->Type == STRUCT_TDFIX || Class->Type == STRUCT_TSDEPT) {
        return true;
    }

    switch (Class->ToBuild) {
    case RTTI_INFANTRYTYPE:
    case RTTI_UNITTYPE:
    case RTTI_VESSELTYPE:
        return true;

    default:
        return false;
    }
}

void BuildingClass::Set_Unselected_By_Player(HouseClass* player)
{
    TechnoClass::Set_Unselected_By_Player(player);

    if (Can_Have_Rally_Point() && RallyPoint) {
        Map.Flag_To_Redraw(true);
    }
}

// Queues a networked rally point change.
void BuildingClass::Player_Set_Rally_Point(TARGET target)
{
    OutList.Add(EventClass(EventClass::SET_RALLY, TargetClass(As_Target()), TargetClass(target)));
}

// The rally point as a target: a cell resolves to a nearby clear cell for the movement class, an object
// passes through unchanged.
TARGET BuildingClass::Target_For_Rally_Point(const SpeedType speed) const
{
    return Target_Legal(RallyPoint)
               ? (Is_Target_Cell(RallyPoint) ? ::As_Target(Map.Nearby_Location(As_Cell(RallyPoint), speed))
                                             : RallyPoint)
               : TARGET_NONE;
}

// Orders a unit leaving the building to its rally point; true if the unit accepted the move.
bool BuildingClass::Rally_Unit(TechnoClass& unit)
{
    if (Can_Have_Rally_Point() && Target_Legal(RallyPoint)) {
        if (unit.What_Am_I() == RTTI_UNIT && ((UnitClass&)unit).Class->IsToHarvest) {
            return false;
        }

        // Claim success for a fixed-wing plane that found no airstrip: the caller would otherwise kick it out
        // and force a crash.
        if ((*this == STRUCT_REPAIR || *this == STRUCT_TDFIX || *this == STRUCT_TSDEPT)
            && unit.What_Am_I() == RTTI_AIRCRAFT) {
            if (((AircraftClass*)&unit)->DoSmarterRunAway()) {
                return true;
            } else if (((AircraftClass*)&unit)->Class->IsFixedWing) {
                return true;
            }
            return false;
        }

        const TARGET rallyTarget = Target_For_Rally_Point(unit.Techno_Type_Class()->Speed);

        int move_target = (int)(unit.As_Target() != rallyTarget ? rallyTarget : ::As_Target(Nearby_Location()));
        return Target_Legal(move_target) && Transmit_Message(RADIO_MOVE_HERE, move_target, &unit) == RADIO_ROGER;
    }
    return false;
}

/***********************************************************************************************
 * BuildingClass::Active_Click_With -- Handles cell selection for buildings.                   *
 *                                                                                             *
 *    This routine really only serves one purpose -- to allow targeting of the ground for      *
 *    buildings that are equipped with weapons.                                                *
 *                                                                                             *
 * INPUT:   action   -- The requested action to perform.                                       *
 *                                                                                             *
 *          cell     -- The cell location to perform the action upon.                          *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/04/1995 JLB : Created.                                                                 *
 *   10/04/1995 JLB : Handles construction yard undeploy to move logic.                        *
 *=============================================================================================*/
void BuildingClass::Active_Click_With(ActionType action, CELL cell)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (action == ACTION_ATTACK) {
        Player_Assign_Mission(MISSION_ATTACK, ::As_Target(cell));
    }

    if (action == ACTION_MOVE && Class->Is_Construction_Yard()) {
        OutList.Add(EventClass(EventClass::ARCHIVE, TargetClass(this), TargetClass(::As_Target(cell))));
        OutList.Add(EventClass(EventClass::SELL, TargetClass(this)));

        COORDINATE coord = Map.Pixel_To_Coord(Get_Mouse_X(), Get_Mouse_Y());
        OutList.Add(EventClass(ANIM_MOVE_FLASH, PlayerPtr->Class->House, coord, 1 << PlayerPtr->Class->House));
    } else if (action == ACTION_MOVE && TF_Packs_Into(this) != UNIT_NONE && !Is_TS_War_Factory()) {
        // TF: a deployed TS building sent somewhere packs up first, and its vehicle then leaves for the cell.
        Player_Assign_Mission(MISSION_UNLOAD, TARGET_NONE, ::As_Target(cell));
    } else if (action == ACTION_MOVE && Can_Have_Rally_Point()) {
        /*
        **	TF: rally points (CFE Patch Redux port). Click ground to set.
        */
        Player_Set_Rally_Point(::As_Target(cell));
    }
}

/***********************************************************************************************
 * BuildingClass::Assign_Target -- Assigns a target to the building.                           *
 *                                                                                             *
 *    Assigning of a target to a building makes sense if the building is one that can attack.  *
 *    This routine would be used to assign the attack target to a turret or guard tower.       *
 *                                                                                             *
 * INPUT:   target   -- The target that was clicked on while this building was selected.       *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/28/1994 JLB : Created.                                                                 *
 *   11/02/1994 JLB : Checks for range before assigning target.                                *
 *=============================================================================================*/
// Keeps the destination of a deployed TS building, so the vehicle it packs into can be sent there once
// its build-up has run backwards.
void BuildingClass::Assign_Destination(TARGET target)
{
    assert(IsActive);

    if (TF_Packs_Into(this) != UNIT_NONE) {
        TFPackNav = target;
    }
    TechnoClass::Assign_Destination(target);
}

void BuildingClass::Assign_Target(TARGET target)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    // TF: the TD SAM skips the range check like the SAM: it acquires its target as it rises and tracks.
    if (*this != STRUCT_SAM && *this != STRUCT_AAGUN && *this != STRUCT_TDSAM && !In_Range(target, 0)) {
        target = TARGET_NONE;
    }

    TechnoClass::Assign_Target(target);
}

/***********************************************************************************************
 * BuildingClass::Init -- Initialize the building system to an empty null state.               *
 *                                                                                             *
 *    This routine initializes the building system in preparation for a scenario load.         *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/19/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Init(void)
{
    Buildings.Free_All();
}

/***********************************************************************************************
 * BuildingClass::Exit_Object -- Initiates an object to leave the building.                    *
 *                                                                                             *
 *    This function is used to cause an object to exit the building. It is called when a       *
 *    factory produces a vehicle or other mobile object and that object needs to exit the      *
 *    building to join the ranks of a regular unit. Typically, the object is placed down on    *
 *    the map such that it overlaps the building and then it is given a movement order so that *
 *    it will move to an adjacent free cell.                                                   *
 *                                                                                             *
 * INPUT:   base  -- Pointer to the object that is to exit the building.                       *
 *                                                                                             *
 * OUTPUT:  Returns the success rating for the exit attempt;                                   *
 *             0  = complete failure (refund money please)                                     *
 *             1  = temporarily prevented (try again later please)                             *
 *             2  = successful                                                                 *
 *                                                                                             *
 * WARNINGS:   The building is placed in radio contact with the object. The object is in a     *
 *             tethered condition. This condition will be automatically broken when the        *
 *             object reaches the adjacent square.                                             *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   11/28/1994 JLB : Created.                                                                 *
 *   04/10/1995 JLB : Handles building production by computer.                                 *
 *   06/17/1995 JLB : Handles refinery exit.                                                   *
 *=============================================================================================*/
// The legal placement cell nearest a remote construction yard, within 14 cells, for AI expansion bases;
// the zone-ring scan only searches around the house's main base.
static CELL TF_Find_Cell_Near_Yard(BuildingClass const* product, BuildingClass const* yard)
{
    TechnoTypeClass const* ttype = product->Techno_Type_Class();
    short const* list = product->Occupy_List(true);
    COORDINATE anchor = yard->Center_Coord();
    CELL best = 0;
    int bestd = INT_MAX;
    for (CELL cell = 0; cell < MAP_CELL_TOTAL; cell++) {
        if (!Map.In_Radar(cell)) {
            continue;
        }
        int d = ::Distance(Cell_Coord(cell), anchor);
        if (d >= bestd || d > 14 * CELL_LEPTON_W) {
            continue;
        }
        if (!ttype->Legal_Placement(cell)) {
            continue;
        }
        if (list != NULL && !Map.Passes_Proximity_Check(ttype, product->House->Class->House, list, cell)) {
            continue;
        }
        best = cell;
        bestd = d;
    }
    return (best);
}

int BuildingClass::Exit_Object(TechnoClass* base)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (!base)
        return (0);

    TechnoTypeClass const* ttype = (TechnoTypeClass const*)&base->Class_Of();

    /*
    **	A unit exiting a building is always considered to be "locked". That means, it
    **	will be considered as to have legally entered the visible map domain.
    */
    base->IsLocked = true;

    /*
    **	Find a good cell to unload the object to. The object, probably a vehicle
    **	will drive/walk to the adjacent free cell.
    */
    CELL cell = 0;

    switch (base->What_Am_I()) {

    case RTTI_AIRCRAFT:
#if TF_DEV_BUILD
        /*
        **  Logs-first: which exit path an aircraft actually leaves its pad by,
        **  and whether the orbit probe is armed when it does. The probe that
        **  froze the game was hooked in Unlimbo; this site is a different one
        **  and has never been observed to run.
        */
        {
            char dpath[512];
            const char* dprof = getenv("USERPROFILE");
            if (dprof != NULL && dprof[0] != '\0') {
                snprintf(dpath, sizeof(dpath), "%s/Documents/CnCRemastered/MOD_DEBUG_TSUNITS.txt", dprof);
            } else {
                strcpy(dpath, "MOD_DEBUG_TSUNITS.txt");
            }
            FILE* dlog = fopen(dpath, "a");
            if (dlog != NULL) {
                fprintf(dlog, "frame=%d ORBIT-EXIT bldg=%s radio=%s type=%d isorca=%s probe=%s\n", Frame,
                        Class->IniName, In_Radio_Contact() ? "yes" : "no", (int)*((AircraftClass*)base),
                        (*((AircraftClass*)base) == AIRCRAFT_TDORCA) ? "yes" : "no",
                        TF_Orbit_Probe() ? "ARMED" : "off");
                fclose(dlog);
            }
        }
#endif
        if (!In_Radio_Contact()) {
            AircraftClass* air = (AircraftClass*)base;

            air->Height = 0;
            ScenarioInit++;
            if (air->Unlimbo(Docking_Coord(), air->Pose_Dir())) {
                Transmit_Message(RADIO_HELLO, air);
                Transmit_Message(RADIO_TETHER);
#if TF_DEV_BUILD
                /*
                **  PROBE: arrive from orbit rather than appearing on the pad.
                **
                **  This has to happen HERE and not in Unlimbo. The pad sets
                **  Height to 0, unlimbos at the docking coordinate and only
                **  then tethers, so a hook inside Unlimbo runs before there is
                **  any radio contact and before NavCom exists -- which is why
                **  the earlier attempt landed but never docked, and is the
                **  prime suspect for the freeze that followed.
                **
                **  With the pad as NavCom AND as the radio contact, the branch
                **  at the bottom of Landing_Takeoff_AI can complete its
                **  handshake and settle the aircraft into the dock, which is
                **  the state the engine expects an aircraft on a pad to be in.
                **
                **  Armed by Documents/CnCRemastered/tf_orbit.flag, off by
                **  default: it puts aircraft somewhere the engine never
                **  otherwise puts them.
                */
                if (TF_Orbit_Probe() && *air == AIRCRAFT_TDORCA) {
                    air->Height = TF_ORBIT_HEIGHT;
                    air->Assign_Destination(As_Target());
                    air->IsLanding = true;

                    char apath[512];
                    const char* aprof = getenv("USERPROFILE");
                    if (aprof != NULL && aprof[0] != '\0') {
                        snprintf(apath, sizeof(apath), "%s/Documents/CnCRemastered/MOD_DEBUG_TSUNITS.txt", aprof);
                    } else {
                        strcpy(apath, "MOD_DEBUG_TSUNITS.txt");
                    }
                    FILE* alog = fopen(apath, "a");
                    if (alog != NULL) {
                        fprintf(alog, "frame=%d ORBIT-APPLY height=%d door=%s navcom=%08lX\n", Frame,
                                (int)air->Height, air->Is_Door_Closed() ? "closed" : "OPEN",
                                (unsigned long)air->NavCom);
                        fclose(alog);
                    }
                }
#endif
                ScenarioInit--;
                return (2);
            }
            ScenarioInit--;
        } else {
            AircraftClass* air = (AircraftClass*)base;

            if (Cell_X(Coord_Cell(Center_Coord())) - Map.MapCellX < Map.MapCellWidth / 2) {
                cell = XY_Cell(Map.MapCellX - 1, Random_Pick(0, Map.MapCellHeight - 1) + Map.MapCellY);
            } else {
                cell = XY_Cell(Map.MapCellX + Map.MapCellWidth, Random_Pick(0, Map.MapCellHeight - 1) + Map.MapCellY);
            }
            ScenarioInit++;
            if (air->Unlimbo(Cell_Coord(cell), DIR_N)) {
                // BG				air->Assign_Destination(::As_Target(Nearby_Location(air)));
                /*BG*/ air->Assign_Destination(::As_Target(air->Nearby_Location(this)));
                air->Assign_Mission(MISSION_MOVE);
                ScenarioInit--;
                return (2);
            }
            ScenarioInit--;
        }
        break;

    case RTTI_VESSEL:
        switch (Class->Type) {
        case STRUCT_SUB_PEN:
        case STRUCT_SHIP_YARD:
        case STRUCT_TDGYARD: // GDI Naval Yard — same vessel-exit semantics.
        case STRUCT_TDNPEN:  // Nod Sub Pen.
            ScenarioInit++;
            cell = Find_Exit_Cell(base);
            if (cell != 0 && base->Unlimbo(Cell_Coord(cell), Direction(Cell_Coord(cell)))) {
                // TF: rally points (CFE Patch Redux port): a vessel never leaves by RADIO_UNLOADED, so it rallies here.
                if (!Rally_Unit(*static_cast<TechnoClass*>(base))) {
                    base->Assign_Mission(MISSION_GUARD);
                }
                ScenarioInit--;
                return (2);
            }
            ScenarioInit--;

            // TF: a blocked slipway holds the order for the normal retry rather than scrapping a paid-for vessel,
            // and our own ships parked by the yard are told to scatter.
            for (int index = 0; index < Vessels.Count(); index++) {
                VesselClass* v = Vessels.Ptr(index);
                if (v != NULL && !v->IsInLimbo && v->Strength > 0 && v->House == House
                    && ::Distance(Center_Coord(), v->Center_Coord()) < 0x0300) {
                    v->Scatter(0, true);
                }
            }
#if TF_DEV_BUILD // TF_AI_DIAG
            if (!House->IsHuman) {
                extern FILE* TF_AI_Diag_File(void);
                FILE* _tfdbg = TF_AI_Diag_File();
                if (_tfdbg != NULL) {
                    fprintf(_tfdbg, "F%ld H%d AL%d YARD-EXIT blocked %s at %s#%d\n", (long)Frame,
                            (int)House->Class->House, (int)House->ActLike, base->Class_Of().IniName,
                            Class->IniName, (int)ID);
                    fflush(_tfdbg);
                }
            }
#endif
            return (1);

        default:
            break;
        }
        break;

    case RTTI_INFANTRY:
    case RTTI_UNIT:
        switch (Class->Type) {
        case STRUCT_TSDROP: {
            // TF: the dropship bay puts nothing on the map: the finished vehicle rides a drop pod down in limbo and
            // is set down when it lands. The pod sinks straight onto the pad drawn on the deck (BulletClass::AI).
            COORDINATE pad = Coord_Add(Center_Coord(), XY_Coord(0x008B, 0x002B));
            CELL dest = Coord_Cell(pad);

            BulletClass* pod =
                new BulletClass(BULLET_TSDROPPOD, ::As_Target(dest), base, 0, WARHEAD_NONE, MPH_MEDIUM_FAST);
            if (pod != NULL) {
                pod->TFPodHouse = House->Class->House;
                if (pod->Unlimbo(pad, DIR_S)) {
                    // Lift the pod to its ceiling between Remove and Submit: a height change moves it to another
                    // display layer.
                    Map.Remove(pod, pod->In_Which_Layer());
                    pod->Height = BulletClass::TF_POD_CEILING;
                    Map.Submit(pod, pod->In_Which_Layer());

                    House->TFDropBayTimer = HouseClass::TF_DROPBAY_COOLDOWN;
                    return (2);
                }
                delete pod;
            }
            // No pod: return 1, so the vehicle stays in the factory and production retries; it is never lost.
            return (1);
        }

        case STRUCT_TSPROC:
            // TF: a harvester leaving the TS refinery appears seated on the dock ramp, facing SE.
            if (base->What_Am_I() == RTTI_UNIT) {
                UnitClass* unit = (UnitClass*)base;
                cell = Coord_Cell(Center_Coord()); // the dock pad = the 4x4 centre cell
                ScenarioInit++;
                if (unit->Unlimbo(Coord_Add(Cell_Coord(cell), XYP_Coord(5, 7)), DIR_SE)) {
                    unit->PrimaryFacing = DIR_SE;
                    unit->Assign_Mission(MISSION_HARVEST);
                }
                ScenarioInit--;
            } else {
                base->Scatter(0, true);
            }
            break;

        case STRUCT_REFINERY:
            if (base->What_Am_I() == RTTI_UNIT) {
                cell = Coord_Cell(Center_Coord());
                UnitClass* unit = (UnitClass*)base;

                cell = Adjacent_Cell(cell, FACING_SW);
                ScenarioInit++;
                if (unit->Unlimbo(Cell_Coord(Adjacent_Cell(cell, DIR_S)), DIR_SW_X2)) {
                    unit->PrimaryFacing = DIR_S;
                    unit->Assign_Mission(MISSION_HARVEST);
                }
                ScenarioInit--;
            } else {
                base->Scatter(0, true);
            }
            break;

        case STRUCT_TDPROC:
            // TF: TD's refinery exit, as in TD: the harvester reappears where it attached, re-contacts the refinery
            // for its exit track and drives out south-west on OUT_OF_REFINERY.
            if (base->What_Am_I() == RTTI_UNIT) {
                cell = Coord_Cell(Center_Coord());
                UnitClass* unit = (UnitClass*)base;

                cell = Adjacent_Cell(cell, FACING_SW);
                ScenarioInit++;
                if (unit->Unlimbo(Coord_Add(unit->Coord, 0x00550060L), DIR_SW_X2)) {
                    unit->PrimaryFacing = DIR_SW_X2;
                    Transmit_Message(RADIO_HELLO, unit);
                    Transmit_Message(RADIO_TETHER);
                    unit->Assign_Mission(MISSION_HARVEST);
                    unit->Force_Track(DriveClass::OUT_OF_REFINERY, Cell_Coord(cell));
                    unit->Set_Speed(128);
                }
                ScenarioInit--;
            } else {
                base->Scatter(0, true);
            }
            break;

        case STRUCT_TDWEAP:
            // TF: TD's weapons factory exit, as in TD: the vehicle appears at the exit point facing south-west.
            ScenarioInit++;
            if (base->Unlimbo(Exit_Coord(), DIR_SW)) {
                base->Mark(MARK_UP);
                base->Coord = Exit_Coord();
                base->Mark(MARK_DOWN);
                Transmit_Message(RADIO_HELLO, base);
                Transmit_Message(RADIO_TETHER);
                Assign_Mission(MISSION_UNLOAD);
                ScenarioInit--;
                return (2);
            }
            ScenarioInit--;
            break;

        case STRUCT_TSWEAP:
        case STRUCT_TSDWEAP:
            if (Mission == MISSION_UNLOAD) {
#if TF_DEV_BUILD
                TF_WF_Log(this, "exit %s#%d: busy, 1", base->Class_Of().IniName, base->ID);
#endif
                return (1); // busy with the previous vehicle
            }
            ScenarioInit++;
            {
                /*
                **	TS (OpenTS Exit_Object): the vehicle exists from the moment
                **	production completes, seated in the bay behind the shut door,
                **	facing out, hidden by the door and revealed as it rolls up, then rides the
                **	exit rail straight south onto the doorstep.
                */
                bool is_mech = false;
                bool is_titan = false;
                if (base->What_Am_I() == RTTI_UNIT) {
                    UnitType ut = *(UnitClass*)base;
                    is_mech = (ut == UNIT_TSTITN || ut == UNIT_TSSMEC || ut == UNIT_TSHMEC);
                    is_titan = (ut == UNIT_TSTITN);
                }
                COORDINATE seat;
                if (*this == STRUCT_TSWEAP) {
                    seat = Coord_Add(Coord, is_mech ? TSWEAP3_SEAT_MECH : TSWEAP3_SEAT);
                } else {
                    seat = Coord_Add(Coord, is_mech ? TSDWEAP_SEAT_MECH : TSDWEAP_SEAT);
                }
                /*
                **	The deployed Mobile War Factory's lintel sits 18 leptons lower against its
                **	threshold than the War Factory's, so the Titan seats that much further south.
                */
                if (is_titan && *this == STRUCT_TSDWEAP) {
                    seat = Coord_Add(seat, XY_Coord(0, 18));
                }
                // TF: these units' HD art reaches past the shut door from the seat, so they wait deeper, in leptons
                // measured behind the door; the Juggernaut, taller than the bay, shows only its antenna tip.
                if (base->What_Am_I() == RTTI_UNIT) {
                    int pull = 0;
                    switch (((UnitClass*)base)->Class->Type) {
                    case UNIT_TSHARV:
                    case UNIT_TSMWAR:
                        pull = 48;
                        break;
                    case UNIT_TSTITN:
                        pull = (*this == STRUCT_TSDWEAP) ? 90 : 72;
                        break;
                    case UNIT_TSJUGG:
                        pull = 144;
                        break;
                    default:
                        break;
                    }
                    seat = Coord_Add(seat, XY_Coord(0, -pull));
                }
                /*
                **	Facing = the exit rail's own direction (seat -> exit cell), so the
                **	vehicle points exactly along the line it will drive.
                */
                COORDINATE exitc = Cell_Coord((CELL)(Coord_Cell(Coord) + TS_Weap_Exit_Offset()));
                DirType outdir = Desired_Facing256(Coord_X(seat), Coord_Y(seat), Coord_X(exitc), Coord_Y(exitc));
                if (base->Unlimbo(seat, outdir)) {
                    base->Mark(MARK_UP);
                    base->Coord = seat;
                    base->Mark(MARK_DOWN);
                    Transmit_Message(RADIO_HELLO, base);
                    Transmit_Message(RADIO_TETHER);
                    Assign_Mission(MISSION_UNLOAD);
                    ScenarioInit--;
#if TF_DEV_BUILD
                    TF_WF_Log(this, "exit %s#%d: seated at (%d,%d), 2", base->Class_Of().IniName, base->ID,
                              Coord_X(seat), Coord_Y(seat));
#endif
                    return (2);
                }
#if TF_DEV_BUILD
                TF_WF_Log(this, "exit %s#%d: unlimbo at (%d,%d) failed", base->Class_Of().IniName, base->ID,
                          Coord_X(seat), Coord_Y(seat));
#endif
            }
            ScenarioInit--;
            break;
        case STRUCT_TDAFLD:
            // TF: TD's airstrip delivers by cargo plane, as in TD (docs/cargo-plane-port.md). The reinforcement
            // spawns its own copy of the vehicle, so the factory's one is deleted.
            if (Create_Special_Reinforcement(
                    House, &AircraftTypeClass::As_Reference(AIRCRAFT_TDCARGO),
                    ttype, TMISSION_UNLOAD, As_Target())) {
                delete base;
                return (2);
            }
            return (0);

        case STRUCT_WEAP:
        case STRUCT_AWEAP:
        case STRUCT_SWEAP:
            if (Mission == MISSION_UNLOAD) {
                for (int index = 0; index < Buildings.Count(); index++) {
                    BuildingClass* bldg = Buildings.Ptr(index);
                    // TF: a stalled war factory hands its vehicle only to another of its own type, never across
                    // factions.
                    if (bldg->Owner() == Owner() && *bldg == Class->Type && bldg != this
                        && bldg->Mission == MISSION_GUARD && !bldg->Factory) {
                        FactoryClass* temp = Factory;
                        bldg->Factory = Factory;
                        Factory = 0;
                        int retval = (bldg->Exit_Object(base));
                        bldg->Factory = 0;
                        Factory = temp;
                        return (retval);
                    }
                }
                return (1); // fail while we're still unloading previous
            }
            ScenarioInit++;
            if (base->Unlimbo(Exit_Coord(), DIR_S)) {
                base->Mark(MARK_UP);
                base->Coord = Exit_Coord();
                base->Mark(MARK_DOWN);
                Transmit_Message(RADIO_HELLO, base);
                Transmit_Message(RADIO_TETHER);
                Assign_Mission(MISSION_UNLOAD);
                ScenarioInit--;
                return (2);
            }
            ScenarioInit--;
            break;

        case STRUCT_BARRACKS:
        case STRUCT_TENT:
        case STRUCT_KENNEL:
        case STRUCT_TDPYLE:     // TD GDI Barracks — same exit-cell pattern, as in TD.
        case STRUCT_TDHAND:     // TD Hand of Nod — same exit-cell pattern, as in TD.
        case STRUCT_TSPILE:     // TS Barracks: same exit-cell pattern, spawned at its doorway pixel.

            cell = Find_Exit_Cell(base);
            if (cell != 0) {
                DirType dir = Direction(cell);
                COORDINATE start = Exit_Coord();

                ScenarioInit++;
                if (base->Unlimbo(start, dir)) {

                    // TF: a TS Barracks soldier steps out of the door's middle, not the standing spot Unlimbo snapped
                    // it to beside the door.
                    if (*this == STRUCT_TSPILE) {
                        base->Mark(MARK_UP);
                        base->Coord = start;
                        base->Mark(MARK_DOWN);
                    }

                    base->Assign_Mission(MISSION_MOVE);

                    /*
                    **	When disembarking from a transport then guard an area around the
                    **	center of the base.
                    */
                    base->Assign_Destination(::As_Target(cell));
                    if (House->IQ >= Rule.IQGuardArea) {
                        base->Assign_Mission(MISSION_GUARD_AREA);
                        base->ArchiveTarget = ::As_Target(House->Where_To_Go((FootClass*)base));
                    }

                    /*
                    **	Establish radio contact so unload coordination can occur. This
                    **	radio contact should always succeed.
                    */
                    if (Transmit_Message(RADIO_HELLO, base) == RADIO_ROGER) {
                        Transmit_Message(RADIO_UNLOAD);
                    }
                    ScenarioInit--;
                    return (2);
                }
                ScenarioInit--;
            }
            break;

        default:
            cell = Find_Exit_Cell(base);
            if (cell != 0) {
                DirType dir = Direction(cell);
                COORDINATE start = Exit_Coord();

                // Diagnostic 2026-05-20: capture vehicle-exit data for TD-mod
                // buildings (TD-prefixed IniName) so we can see why TDWEAP's
                // tank teleports + faces wrong direction. Logs: building cell,
                // spawn pixel (start), exit cell, dir, plus the unit's actual
                // Coord + PrimaryFacing immediately after Unlimbo. See
                // catalogue.md "TEMPORARY DEV HACKS".
                static FILE* s_exit_log = NULL;
                bool log_this = (Class->IniName[0] == 'T' && Class->IniName[1] == 'D');
                if (log_this) {
                    if (s_exit_log == NULL) {
                        char dpath[512];
                        const char* dprof = getenv("USERPROFILE");
                        if (dprof != NULL && dprof[0] != '\0') {
                            snprintf(dpath, sizeof(dpath),
                                     "%s/Documents/CnCRemastered/tf_exit_object.log", dprof);
                        } else {
                            strcpy(dpath, "tf_exit_object.log");
                        }
                        s_exit_log = NULL; // TF DIAG OFF for release (was fopen; restore to re-enable)
                    }
                    if (s_exit_log != NULL) {
                        CELL b_origin = Coord_Cell(Coord);
                        CELL spawn_cell = Coord_Cell(start);
                        fprintf(s_exit_log,
                                "EXIT %s b_origin=cell(%d,%d) spawn_pixel=(%d,%d) "
                                "spawn_cell=cell(%d,%d) exit_cell=cell(%d,%d) "
                                "exit_rel=(%d,%d) dir=%d\n",
                                Class->IniName,
                                Cell_X(b_origin), Cell_Y(b_origin),
                                Coord_X(start), Coord_Y(start),
                                Cell_X(spawn_cell), Cell_Y(spawn_cell),
                                Cell_X(cell), Cell_Y(cell),
                                Cell_X(cell) - Cell_X(b_origin),
                                Cell_Y(cell) - Cell_Y(b_origin),
                                (int)dir);
                        fflush(s_exit_log);
                    }
                }

                ScenarioInit++;
                if (base->Unlimbo(start, dir)) {

                    if (log_this && s_exit_log != NULL && base->Is_Techno()) {
                        TechnoClass* t = (TechnoClass*)base;
                        fprintf(s_exit_log,
                                "  POST_UNLIMBO base.Coord=(%d,%d) base.PrimaryFacing=%d\n",
                                Coord_X(t->Coord), Coord_Y(t->Coord),
                                (int)t->PrimaryFacing.Current());
                        fflush(s_exit_log);
                    }

                    base->Assign_Mission(MISSION_MOVE);

                    /*
                    **	When disembarking from a transport then guard an area around the
                    **	center of the base.
                    */
                    base->Assign_Destination(::As_Target(cell));
                    if (House->IQ >= Rule.IQGuardArea) {
                        base->Assign_Mission(MISSION_GUARD_AREA);
                        base->ArchiveTarget = ::As_Target(House->Where_To_Go((FootClass*)base));
                    }

                    if (log_this && s_exit_log != NULL && base->Is_Foot()) {
                        FootClass* t = (FootClass*)base;
                        fprintf(s_exit_log,
                                "  POST_MISSION base.Coord=(%d,%d) base.PrimaryFacing=%d Mission=%d NavCom=0x%X\n",
                                Coord_X(t->Coord), Coord_Y(t->Coord),
                                (int)t->PrimaryFacing.Current(),
                                (int)t->Mission, (unsigned)t->NavCom);
                        fflush(s_exit_log);
                    }

                    ScenarioInit--;
                    return (2);
                }
                ScenarioInit--;
            }
            break;
        }
        break;

    case RTTI_BUILDING:

        if (!House->IsHuman) {

            /*
            **	Find the next available spot to place this newly created building. If the
            **	building could be placed at the desired location, fine. If not, then this
            **	routine will return failure. The calling routine will probably abandon this
            **	building in preference to building another.
            */
            // TF: an addon plug installs into its host building, so it takes no base node, remote-yard cell or
            // flush: the host occupies the cell, and a flush would wait on it forever.
            bool plug = (((BuildingClass*)base)->Class->PowersUpBuilding != STRUCT_NONE);
            BaseNodeClass* node = plug ? NULL : Base.Next_Buildable(((BuildingClass*)base)->Class->Type);
            COORDINATE coord = 0;
            if (node) {
                coord = Cell_Coord(node->Cell);
            } else {

                // TF: a construction yard far outside the main base places its products on the nearest legal cell,
                // as the base's zone rings all lie back home. Water-bound products still go to Find_Build_Location.
                if (!plug && House->Center != 0 && ((BuildingClass*)base)->Class->Speed != SPEED_FLOAT
                    && ::Distance(Center_Coord(), House->Center)
                           > House->Radius + 10 * CELL_LEPTON_W) {
                    CELL nearcell = TF_Find_Cell_Near_Yard((BuildingClass*)base, this);
                    if (nearcell != 0) {
                        coord = Cell_Coord(nearcell);
                    }
                }

                /*
                **	Find a suitable new spot to place.
                */
                if (coord == 0) {
                    coord = House->Find_Build_Location((BuildingClass*)base);
                }
            }

            if (coord) {
                if (!plug && Flush_For_Placement(base, Coord_Cell(coord))) {
                    return (1);
                }
                if (base->Unlimbo(coord)) {
                    if (node && ((BuildingClass*)base)->Class->Type == House->BuildStructure) {
                        House->BuildStructure = STRUCT_NONE;
                    }
                    return (2);
                }
            }

#if TF_DEV_BUILD // TF_AI_DIAG -- reaching here means the finished building could not be put
                 // down, and the caller abandons it. Distinguishes "no legal cell was found"
                 // from "a cell was found but Unlimbo refused it".
            if (!House->IsHuman) {
                extern FILE* TF_AI_Diag_File(void);
                FILE* _tfdbg = TF_AI_Diag_File();
                if (_tfdbg != NULL) {
                    fprintf(_tfdbg,
                            "F%ld H%d AL%d PLACE-FAIL %s reason=%s cell=%d | rejects radar=%d zone=%d "
                            "legal=%d prox=%d ok=%d | center=%d radius=%d\n",
                            (long)Frame,
                            (int)House->Class->House,
                            (int)House->ActLike,
                            base->Class_Of().IniName,
                            coord ? "unlimbo-refused" : "no-location",
                            coord ? (int)Coord_Cell(coord) : -1,
                            TF_PlaceScan.Radar,
                            TF_PlaceScan.Zone,
                            TF_PlaceScan.Legal,
                            TF_PlaceScan.Proximity,
                            TF_PlaceScan.Ok,
                            (int)Coord_Cell(TF_PlaceScan.Center),
                            TF_PlaceScan.Radius);
                    fflush(_tfdbg);
                }
            }
#endif
        }
        break;

    default:
        break;
    }

    /*
    **	Failure to exit the object results in a false return value.
    */
    return (0);
}

#ifdef REMASTER_BUILD
/***********************************************************************************************
 * BuildingClass::Update_Buildables -- Informs sidebar of additional construction options.     *
 *                                                                                             *
 *    This routine will tell the sidebar of objects that can be built. The function is called  *
 *    whenever a building matures.                                                             *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   11/11/1994 JLB : Created.                                                                 *
 *   12/23/1994 JLB : Only updates for PLAYER buildings.                                       *
 *=============================================================================================*/
void BuildingClass::Update_Buildables(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    /*
    ** Only do this for real human players. ST - 3/22/2019 1:38PM
    */
    if (PlayerPtr != House) {
        if (Session.Type != GAME_GLYPHX_MULTIPLAYER || House->IsHuman == false) {
            return;
        }
    }

    bool buildable_via_capture = (IsCaptured && ActLike != House->ActLike) ? true : false;

    // Tiberian Factions: Update_Buildables entry log (stubbed). Re-enabled
    // 2026-05-25 to diagnose TDHPAD's missing helicopter cameos. Per
    // [[feedback-keep-diagnostics-until-v1]] stub bodies under #if 0 so the
    // flip is one-line.
#if 0
    {
        bool log_this = (Class->IniName[0] == 'T' && Class->IniName[1] == 'D')
                        || Class->Type == STRUCT_HELIPAD;
        if (log_this) {
            static FILE* s_ub_log = NULL;
            static int s_count = 0;
            if (s_count < 200) {
                if (s_ub_log == NULL) {
                    char path[512];
                    const char* profile = getenv("USERPROFILE");
                    if (profile != NULL && profile[0] != '\0') {
                        snprintf(path, sizeof(path),
                                 "%s/Documents/CnCRemastered/MOD_DEBUG_UPDATE_BUILDABLES.txt",
                                 profile);
                    } else {
                        strcpy(path, "MOD_DEBUG_UPDATE_BUILDABLES.txt");
                    }
                    s_ub_log = fopen(path, "w");
                }
                if (s_ub_log != NULL) {
                    fprintf(s_ub_log,
                            "Update_Buildables name=%s Type=%d ToBuild=%d "
                            "IsInLimbo=%d Discovered=%d session=%d "
                            "PlayerActLike=%d HouseActLike=%d AircraftTypes_n=%d\n",
                            Class->IniName, (int)Class->Type, (int)Class->ToBuild,
                            (int)IsInLimbo, Is_Discovered_By_Player() ? 1 : 0,
                            (int)Session.Type, (int)PlayerPtr->ActLike,
                            (int)House->ActLike, AircraftTypes.Count());
                    fflush(s_ub_log);
                    s_count++;
                }
            }
        }
    }
#endif

    if (!IsInLimbo && Is_Discovered_By_Player()) {
        switch (Class->ToBuild) {
            int i;
            int u;
            int f;
            int a;
            int v;

        case RTTI_VESSELTYPE:
            for (v = 0; v < VesselTypes.Count(); v++) {
                if (PlayerPtr->Can_Build(VesselTypes.Ptr(v), ActLike)) {
                    if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
#ifdef REMASTER_BUILD
                        Sidebar_Glyphx_Add(RTTI_VESSELTYPE, v, House, buildable_via_capture);
#endif
                    } else {
                        Map.Add(RTTI_VESSELTYPE, v, buildable_via_capture);
                    }
                }
            }
            break;

        case RTTI_BUILDINGTYPE:
            // TF: a building is offered only when one of the player's yards could build it, the test the sidebar
            // evicts by; each add-then-evict makes the launcher announce "new construction options".
            for (i = 0; i < BuildingTypes.Count(); i++) {
                if (PlayerPtr->Can_Build(BuildingTypes.Ptr(i), ActLike)
                    && BuildingTypes.Ptr(i)->Who_Can_Build_Me(true, true, PlayerPtr->Class->House) != NULL) {
                    if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
#ifdef REMASTER_BUILD
                        Sidebar_Glyphx_Add(RTTI_BUILDINGTYPE, i, House, buildable_via_capture);
#endif
                    } else {
                        Map.Add(RTTI_BUILDINGTYPE, i, buildable_via_capture);
                    }
                }
            }
            break;

        case RTTI_UNITTYPE:
            for (u = 0; u < UnitTypes.Count(); u++) {
                if (PlayerPtr->Can_Build(UnitTypes.Ptr(u), ActLike)) {
                    if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
#ifdef REMASTER_BUILD
                        Sidebar_Glyphx_Add(RTTI_UNITTYPE, u, House, buildable_via_capture);
#endif
                    } else {
                        Map.Add(RTTI_UNITTYPE, u, buildable_via_capture);
                    }
                }
            }
            break;

        case RTTI_INFANTRYTYPE:
            for (f = 0; f < InfantryTypes.Count(); f++) {
                if (PlayerPtr->Can_Build(InfantryTypes.Ptr(f), ActLike)) {
                    if (InfantryTypes.Ptr(f)->IsDog) {
                        if (*this == STRUCT_KENNEL) {
                            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
#ifdef REMASTER_BUILD
                                Sidebar_Glyphx_Add(RTTI_INFANTRYTYPE, f, House, buildable_via_capture);
#endif
                            } else {
                                Map.Add(RTTI_INFANTRYTYPE, f, buildable_via_capture);
                            }
                        }
                    } else {
                        if (*this != STRUCT_KENNEL) {
                            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
#ifdef REMASTER_BUILD
                                Sidebar_Glyphx_Add(RTTI_INFANTRYTYPE, f, House, buildable_via_capture);
#endif
                            } else {
                                Map.Add(RTTI_INFANTRYTYPE, f, buildable_via_capture);
                            }
                        }
                    }
                }
            }
            break;

        case RTTI_AIRCRAFTTYPE:
            // Tiberian Factions: AIRCRAFTTYPE iteration + Sidebar_Glyphx_Add
            // result logging (stubbed). Re-enabled 2026-05-25 to diagnose
            // TDHPAD's missing helicopter cameos. Root cause turned out to be
            // Who_Can_Build_Me's hardcoded STRUCT_HELIPAD check (object.cpp);
            // see playbook §3.12. Per [[feedback-keep-diagnostics-until-v1]].
#if 0
            {
                static FILE* s_air_log = NULL;
                static int s_count = 0;
                if (s_count < 100) {
                    if (s_air_log == NULL) {
                        char path[512];
                        const char* profile = getenv("USERPROFILE");
                        if (profile != NULL && profile[0] != '\0') {
                            snprintf(path, sizeof(path),
                                     "%s/Documents/CnCRemastered/MOD_DEBUG_AIR_ITER.txt",
                                     profile);
                        } else {
                            strcpy(path, "MOD_DEBUG_AIR_ITER.txt");
                        }
                        s_air_log = fopen(path, "w");
                    }
                    if (s_air_log != NULL) {
                        fprintf(s_air_log,
                                "AirIter from=%s PlayerPtr=%p PlayerActLike=%d "
                                "PlayerIsHuman=%d HouseIsHuman=%d Aircraft_n=%d "
                                "ActLike_used=%d\n",
                                Class->IniName, (void*)PlayerPtr,
                                (int)PlayerPtr->ActLike, PlayerPtr->IsHuman ? 1 : 0,
                                House->IsHuman ? 1 : 0,
                                AircraftTypes.Count(), (int)ActLike);
                        for (int ai = 0; ai < AircraftTypes.Count(); ai++) {
                            bool cb = PlayerPtr->Can_Build(AircraftTypes.Ptr(ai), ActLike);
                            fprintf(s_air_log, "  [%d] %s Can_Build=%d\n",
                                    ai, AircraftTypes.Ptr(ai)->IniName, cb ? 1 : 0);
                        }
                        fflush(s_air_log);
                        s_count++;
                    }
                }
            }
#endif
            for (a = 0; a < AircraftTypes.Count(); a++) {
                if (PlayerPtr->Can_Build(AircraftTypes.Ptr(a), ActLike)) {
                    if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
#ifdef REMASTER_BUILD
                        Sidebar_Glyphx_Add(RTTI_AIRCRAFTTYPE, a, House, buildable_via_capture);
#endif
                    } else {
                        Map.Add(RTTI_AIRCRAFTTYPE, a, buildable_via_capture);
                    }
                }
            }
            break;

        default:
            break;
        }
    }
}

#else // Old code for reference. ST - 8/2/2019 2:41PM
/***********************************************************************************************
 * BuildingClass::Update_Buildables -- Informs sidebar of additional construction options.     *
 *                                                                                             *
 *    This routine will tell the sidebar of objects that can be built. The function is called  *
 *    whenever a building matures.                                                             *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   11/11/1994 JLB : Created.                                                                 *
 *   12/23/1994 JLB : Only updates for PLAYER buildings.                                       *
 *=============================================================================================*/
void BuildingClass::Update_Buildables(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (House == PlayerPtr && !IsInLimbo && IsDiscoveredByPlayer) {
        switch (Class->ToBuild) {
            int i;
            int u;
            int f;
            int a;
            int v;

        case RTTI_VESSELTYPE:
            for (v = VESSEL_FIRST; v < VESSEL_COUNT; v++) {
                if (PlayerPtr->Can_Build(&VesselTypeClass::As_Reference((VesselType)v), ActLike)) {
                    Map.Add(RTTI_VESSELTYPE, v);
                }
            }
            break;

        case RTTI_BUILDINGTYPE:
            for (i = STRUCT_FIRST; i < STRUCT_COUNT; i++) {
                if (PlayerPtr->Can_Build(&BuildingTypeClass::As_Reference((StructType)i), ActLike)
                    && BuildingTypeClass::As_Reference((StructType)i).Who_Can_Build_Me(true, true, PlayerPtr->Class->House)
                           != NULL) {
                    Map.Add(RTTI_BUILDINGTYPE, i);
                }
            }
            break;

        case RTTI_UNITTYPE:
            for (u = UNIT_FIRST; u < UNIT_COUNT; u++) {
                if (PlayerPtr->Can_Build(&UnitTypeClass::As_Reference((UnitType)u), ActLike)) {
                    Map.Add(RTTI_UNITTYPE, u);
                }
            }
            break;

        case RTTI_INFANTRYTYPE:
            for (f = INFANTRY_FIRST; f < INFANTRY_COUNT; f++) {
                if (PlayerPtr->Can_Build(&InfantryTypeClass::As_Reference((InfantryType)f), ActLike)) {
                    if (InfantryTypeClass::As_Reference((InfantryType)f).IsDog) {
                        if (*this == STRUCT_KENNEL) {
                            Map.Add(RTTI_INFANTRYTYPE, f);
                        }
                    } else {
                        if (*this != STRUCT_KENNEL) {
                            Map.Add(RTTI_INFANTRYTYPE, f);
                        }
                    }
                }
            }
            break;

        case RTTI_AIRCRAFTTYPE:
            for (a = AIRCRAFT_FIRST; a < AIRCRAFT_COUNT; a++) {

                if (PlayerPtr->Can_Build(&AircraftTypeClass::As_Reference((AircraftType)a), ActLike)) {
                    if (AircraftTypeClass::As_Reference((AircraftType)a).IsFixedWing) {
                        if (*this == STRUCT_AIRSTRIP || *this == STRUCT_TDAFLD) {
                            Map.Add(RTTI_AIRCRAFTTYPE, a);
                        }
                    } else {
                        if (Class->Is_Helipad()) {
                            Map.Add(RTTI_AIRCRAFTTYPE, a);
                        }
                    }
                }
            }
            break;

        default:
            break;
        }
    }
}
#endif

/***********************************************************************************************
 * BuildingClass::Fire_Out -- Handles when attached animation expires.                         *
 *                                                                                             *
 *    This routine is used to perform any fixups necessary when the attached animation has     *
 *    terminated. This occurs when the fire & smoke animation that a SAM site produces stops.  *
 *    At that point, normal reload procedures can commence.                                    *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   11/30/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Fire_Out(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);
}

/***********************************************************************************************
 * BuildingClass::Limbo -- Handles power adjustment as building goes into limbo.               *
 *                                                                                             *
 *    This routine will handle the power adjustments for the associated house when the         *
 *    building goes into limbo. This means that its power drain or production is subtracted    *
 *    from the house accumulated totals.                                                       *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  bool; Was the building limboed?                                                    *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   12/24/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
bool BuildingClass::Limbo(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (!IsInLimbo) {

        /*
        **	Update the total factory type, assuming this building has a factory.
        */
        House->Active_Remove(this);
        House->IsRecalcNeeded = true;
        House->Recalc_Center();

        /*
        **	Update the power status of the owner's house.
        */
        House->Adjust_Power(-Power_Output());
        House->Adjust_Drain(-(Class->Drain + Upgrade_Drain()));
        House->Adjust_Capacity(-Class->Capacity, true);
        if (House == PlayerPtr) {
            Map.PowerClass::IsToRedraw = true;
            Map.Flag_To_Redraw(false);
        }

        /*
        **	This could be a building that builds. If so, then the sidebar may need adjustment.
        ** Set IsInLimbo to true to "fool" the sidebar into knowing that this building
        ** isn't available.  Set it back to false so the rest of the Limbo code works.
        ** Otherwise, the sidebar won't properly remove non-available buildables.
        */
        //		if (IsOwnedByPlayer && !ScenarioInit) {
        //			IsInLimbo = true;
        //			Map.Recalc();
        //			IsInLimbo = false;
        //		}
    }
    bool joins_walls = (TF_Is_Wall_Tower(Class->Type) || TF_Gate_Info(Class->Type) != NULL);
    CELL cell = Coord_Cell(Coord);
    bool limboed = TechnoClass::Limbo();
    if (limboed && joins_walls) {
        short const* offset = Class->Occupy_List();
        while (offset != NULL && *offset != REFRESH_EOL) {
            Map[(CELL)(cell + *offset++)].Wall_Update(true);
        }
    }
    return (limboed);
}

/***********************************************************************************************
 * BuildingClass::Turret_Facing -- Fetches the turret facing for this building.                *
 *                                                                                             *
 *    This will return the turret facing for this building. Some buildings don't have a        *
 *    visual turret (e.g., pillbox) so they return a turret facing that always faces their     *
 *    current target.                                                                          *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the current facing of the turret.                                     *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
DirType BuildingClass::Turret_Facing(void) const
{
    if (!Class->IsTurretEquipped && Target_Legal(TarCom)) {
        return (::Direction(Center_Coord(), As_Coord(TarCom)));
    }
    return (PrimaryFacing.Current());
}

/***********************************************************************************************
 * BuildingClass::Greatest_Threat -- Searches for target that building can fire upon.          *
 *                                                                                             *
 *    This routine intercepts the Greatest_Threat function so that it can add the ability      *
 *    to search for ground targets, if this isn't a SAM site.                                  *
 *                                                                                             *
 * INPUT:   threat   -- The base threat control value. Typically, it might be THREAT_RANGE     *
 *                      or THREAT_NORMAL.                                                      *
 *                                                                                             *
 * OUTPUT:  Returns with a suitable target. If none could be found, then TARGET_NONE is        *
 *          returned instead.                                                                  *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/01/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
TARGET BuildingClass::Greatest_Threat(ThreatType threat) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    /*
    **	TS Limpet Mine: only a vehicle in reach is worth leaping onto.
    */
    if (*this == STRUCT_TSDLIMP) {
        return (TechnoClass::Greatest_Threat(THREAT_VEHICLES | THREAT_RANGE));
    }

    // TF: the TD SAM scans THREAT_AREA, past its weapon range, so it can rise from the ground while an aircraft
    // is still inbound; acquired at weapon range, it would finish rising after the target had gone.
    if (*this == STRUCT_TDSAM) {
        threat = threat | THREAT_AREA;
        if (Class->PrimaryWeapon != NULL && Class->PrimaryWeapon->Bullet->IsAntiAircraft) {
            threat = threat | THREAT_AIR;
        }
        return (TechnoClass::Greatest_Threat(threat));
    }

    if (Class->PrimaryWeapon != NULL) {
        threat = threat | Class->PrimaryWeapon->Allowed_Threats();
    }
    if (Class->SecondaryWeapon != NULL) {
        threat = threat | Class->SecondaryWeapon->Allowed_Threats();
    }
    if (House->IsHuman) {
        threat = threat & ~THREAT_BUILDINGS;
    }
    threat = threat | THREAT_RANGE;

    //	if (Class->PrimaryWeapon != NULL) {
    //		if (Class->PrimaryWeapon->Bullet->IsAntiAircraft) {
    //			threat = threat | THREAT_AIR;
    //		}
    //		if (Class->PrimaryWeapon->Bullet->IsAntiGround) {
    //			threat = threat | THREAT_BUILDINGS|THREAT_INFANTRY|THREAT_BOATS|THREAT_VEHICLES;
    //		}
    //		threat = threat | THREAT_RANGE;
    //	}
    return (TechnoClass::Greatest_Threat(threat));
}

// Smarter SAMs, from CFE Patch Redux: a SAM that loses its target takes another airborne target before
// lowering. True when TarCom was reassigned.
bool BuildingClass::TDSAM_Try_Reacquire(void)
{
    TARGET newtarget = Greatest_Threat(THREAT_NORMAL);
    if (TF_SAM_Air_Target(newtarget)) {
        Assign_Target(newtarget);
        return (true);
    }
    return (false);
}

/***********************************************************************************************
 * BuildingClass::Grand_Opening -- Handles construction completed special operations.          *
 *                                                                                             *
 *    This routine is called when construction has finished. Typically, this enables           *
 *    new production options for factories.                                                    *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/08/1995 JLB : Created.                                                                 *
 *   06/13/1995 JLB : Added helipad.                                                           *
 *=============================================================================================*/
void BuildingClass::Grand_Opening(bool captured)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (!HasOpened || captured) {
        HasOpened = true;

        /*
        **	Adjust the owning house according to the power, drain, and Tiberium capacity that
        **	this building has.
        */
        // TF: installed addon plugs add their drain too, which matters when a captured building reopens.
        House->Adjust_Drain(Class->Drain + Upgrade_Drain());
        House->Adjust_Capacity(Class->Capacity);
        House->IsRecalcNeeded = true;


        /*	SPECIAL CASE:
        **	Tiberium Refineries get a free harvester. Add a harvester to the
        **	reinforcement list at this time.
        */
        if ((*this == STRUCT_REFINERY || *this == STRUCT_TDPROC || *this == STRUCT_TSPROC) && !ScenarioInit
            && !captured && !Debug_Map
            && (!House->IsHuman || PurchasePrice == 0 || PurchasePrice > Class->Raw_Cost())) {
            /*
            **	TSPROC's free harvester appears on the plate (south-east of the
            **	dock pad, the centre cell) facing out, where a truck stands once it
            **	has unloaded, so it drives away from the dock lane.
            */
            CELL cell = (*this == STRUCT_TSPROC) ? (CELL)(Coord_Cell(Center_Coord()) + MAP_CELL_W + 1)
                                                 : Coord_Cell(Adjacent_Cell(Center_Coord(), DIR_S));

            // Tiberian Factions: STRUCT_TDPROC spawns UNIT_TDHARV (TD-art
            // harvester) instead of RA's UNIT_HARVESTER; STRUCT_TSPROC spawns
            // UNIT_TSHARV. Same mechanics.
            UnitType harv_type = (*this == STRUCT_TDPROC)   ? UNIT_TDHARV
                                 : (*this == STRUCT_TSPROC) ? UNIT_TSHARV
                                                            : UNIT_HARVESTER;
            UnitClass* unit = new UnitClass(harv_type, House->Class->House);
#if TF_DEV_BUILD
            // Logs-first (first TSHARV test): record the TS refinery's free-unit grant.
            if (*this == STRUCT_TSPROC) {
                char dpath[512];
                const char* dprof = getenv("USERPROFILE");
                if (dprof != NULL && dprof[0] != '\0') {
                    snprintf(dpath, sizeof(dpath), "%s/Documents/CnCRemastered/MOD_DEBUG_TSUNITS.txt", dprof);
                } else {
                    strcpy(dpath, "MOD_DEBUG_TSUNITS.txt");
                }
                FILE* dlog = fopen(dpath, "a");
                if (dlog != NULL) {
                    fprintf(dlog, "frame=%d FREE-HARV grant house=%s spawned=%s\n", Frame,
                            House->Class->IniName, (unit != NULL) ? "yes" : "NO (heap)");
                    fclose(dlog);
                }
            }
#endif
            if (unit != NULL) {

                /*
                **	Try to place down the harvesters. If it could not be placed, then try
                **	to place it in a nearby location.
                */
                if (!unit->Unlimbo(Cell_Coord(cell), (*this == STRUCT_TSPROC) ? DIR_SE : DIR_W)) {
                    /*
                    **	Check multiple times for clear locations.
                    */
                    for (int i = 0; i < 10; i++) {
                        cell = unit->Nearby_Location(this, i);
                        if (unit->Unlimbo(Cell_Coord(cell), DIR_SW)) {
                            break;
                        }
                    }

                    /*
                    **	If the harvester could still not be placed, then refund the money
                    **	to the owner and then bail.
                    */
                    if (unit->IsInLimbo) {
                        House->Refund_Money(unit->Class->Cost_Of());
                        delete unit;
                        unit = NULL;
                    }
                }
#if TF_DEV_BUILD
                if (*this == STRUCT_TSPROC) {
                    char dpath[512];
                    const char* dprof = getenv("USERPROFILE");
                    if (dprof != NULL && dprof[0] != '\0') {
                        snprintf(dpath, sizeof(dpath), "%s/Documents/CnCRemastered/MOD_DEBUG_TSUNITS.txt", dprof);
                    } else {
                        strcpy(dpath, "MOD_DEBUG_TSUNITS.txt");
                    }
                    FILE* dlog = fopen(dpath, "a");
                    if (dlog != NULL) {
                        fprintf(dlog, "frame=%d FREE-HARV placed=%s cell=%d pad=%d\n", Frame, (unit != NULL) ? "yes" : "NO (refunded)",
                                (unit != NULL) ? Coord_Cell(unit->Coord) : -1, Coord_Cell(Center_Coord()));
                        fclose(dlog);
                    }
                }
#endif
            } else {

                /*
                **	If the harvester could not be created in the first place, then give
                **	the full refund price to the owning player.
                */
                House->Refund_Money(UnitTypeClass::As_Reference(UNIT_HARVESTER).Cost_Of());
            }
        }

        /*
        **	Helicopter pads get a free attack helicopter.
        */
        if (!Rule.IsSeparate && Class->Is_Helipad() && !captured) {
            ScenarioInit++;
            AircraftClass* air = 0;
            // TF: the free helicopter follows the pad's faction, whoever built it, and a TS pad comes with none;
            // the shared legacy pads pick by the owner's ActLike.
            switch (Class->Type) {
            case STRUCT_TDGHPAD:
                air = new AircraftClass(AIRCRAFT_TDORCA, House->Class->House);
                break;
            case STRUCT_TDNHPAD:
                air = new AircraftClass(AIRCRAFT_TDAPACHE, House->Class->House);
                break;
            case STRUCT_AHPAD:
                air = new AircraftClass(AIRCRAFT_LONGBOW, House->Class->House);
                break;
            case STRUCT_SHPAD:
                air = new AircraftClass(AIRCRAFT_HIND, House->Class->House);
                break;
            case STRUCT_TDHPAD:
                air = new AircraftClass(House->ActLike == HOUSE_BAD ? AIRCRAFT_TDAPACHE : AIRCRAFT_TDORCA,
                                        House->Class->House);
                break;
            case STRUCT_TSHPAD:
                air = NULL;
                break;
            default:
                if (House->ActLike == HOUSE_USSR || House->ActLike == HOUSE_UKRAINE) {
                    air = new AircraftClass(AIRCRAFT_HIND, House->Class->House);
                } else {
                    air = new AircraftClass(AIRCRAFT_LONGBOW, House->Class->House);
                }
                break;
            }
            if (air) {
                air->Height = 0;
                if (air->Unlimbo(Docking_Coord(), air->Pose_Dir())) {
                    air->Assign_Mission(MISSION_GUARD);
                    air->Transmit_Message(RADIO_HELLO, this);
                    Transmit_Message(RADIO_TETHER);
                }
            }
            ScenarioInit--;
        }
    }
}

/***********************************************************************************************
 * BuildingClass::Repair -- Initiates or terminates the repair process.                        *
 *                                                                                             *
 *    This routine will start, stop, or toggle the repair process. When a building repairs, it *
 *    occurs incrementally over time.                                                          *
 *                                                                                             *
 * INPUT:   control  -- Determines how to control the repair process.                          *
 *                      0: Turns repair process off (if it was on).                            *
 *                      1: Turns repair process on (if it was off).                            *
 *                      -1:Toggles repair process to other state.                              *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/08/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Repair(int control)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    switch (control) {
    case -1:
        IsRepairing = (IsRepairing == false);
        break;

    case 1:
        if (IsRepairing)
            return;
        IsRepairing = true;
        break;

    case 0:
        if (!IsRepairing)
            return;
        IsRepairing = false;
        break;

    default:
        break;
    }

    /*
    **	At this point, we know that the repair state has changed. Perform
    **	appropriate action.
    */
    VocType soundid = VOC_NONE;
    if (IsRepairing) {
        if (Strength == Class->MaxStrength) {
            soundid = VOC_SCOLD;
        } else {
            soundid = VOC_CLICK;
            if (House->IsPlayerControl) {
                Clicked_As_Target(
                    PlayerPtr->Class->House); // 2019/09/20 JAS - Added record of who clicked on the object
            }
            IsWrenchVisible = true;
        }
    } else {
        soundid = VOC_CLICK;
    }

    if (House->IsPlayerControl) {
        Sound_Effect(soundid, Coord);
    }
}

/***********************************************************************************************
 * BuildingClass::Sell_Back -- Controls the sell back (demolish) operation.                    *
 *                                                                                             *
 *    This routine will initiate or stop the sell back process for a building. It is called    *
 *    when the player clicks on a building when the sell mode is active.                       *
 *                                                                                             *
 * INPUT:   control  -- The action to perform. 0 = turn deconstruction off, 1 = deconstruct,   *
 *                      -1 = toggle deconstruction state.                                      *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Sell_Back(int control)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    // TF: a Firestorm Wall Section has no build-up to run backwards: sold while its house's field is down, it
    // is removed with no refund, as in TS.
    if (*this == STRUCT_TSFSDF) {
        if (control != 0 && Is_Open_Firestorm_Section()) {
            Limbo();
            delete this;
        }
        return;
    }

    if (Class->Get_Buildup_Data()) {
        bool decon = false;
        switch (control) {
        case -1:
            decon = (Mission != MISSION_DECONSTRUCTION);
            break;

        case 1:
            if (Mission == MISSION_DECONSTRUCTION)
                return;
            if (IsGoingToBlow)
                return;
            decon = true;
            break;

        case 0:
            if (Mission != MISSION_DECONSTRUCTION)
                return;
            decon = false;
            break;

        default:
            break;
        }

        /*
        **	At this point, we know that the repair state has changed. Perform
        **	appropriate action.
        */
        if (decon) {
            Assign_Mission(MISSION_DECONSTRUCTION);
            Commence();
            if (House->IsPlayerControl) {
                Clicked_As_Target(PlayerPtr->Class->House);
            }
        }
        if (House->IsPlayerControl) {
            Sound_Effect(VOC_CLICK);
        }
    }
}

/***********************************************************************************************
 * BuildingClass::What_Action -- Determines action to perform if click on specified object.    *
 *                                                                                             *
 *    This routine will determine what action to perform if the mouse was clicked on the       *
 *    object specified. This determination is used to control the mouse imagery and the        *
 *    function process when the mouse button is pressed.                                       *
 *                                                                                             *
 * INPUT:   object   -- Pointer to the object that, if clicked on, will control what action    *
 *                      is to be performed.                                                    *
 *                                                                                             *
 * OUTPUT:  Returns with the ActionType that will occur if the mouse is clicked over the       *
 *          object specified while the building is currently selected.                         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/18/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
ActionType BuildingClass::What_Action(ObjectClass const* object) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    ActionType action = TechnoClass::What_Action(object);

    // TF: attack-move given to a building becomes a move, the action rally points ride.
    if (action == ACTION_ATTACKMOVE) {
        action = ACTION_MOVE;
    }

    if (action == ACTION_SELF) {
        int index;
        if (Class->Is_Factory() && PlayerPtr == House && *House->Factory_Counter(Class->ToBuild, *this == STRUCT_TSDROP) > 1) {
            switch (Class->ToBuild) {
            case RTTI_INFANTRYTYPE:
            case RTTI_INFANTRY:
                action = ACTION_NONE;
                if (*this == STRUCT_KENNEL) {
                    for (index = 0; index < Buildings.Count(); index++) {
                        BuildingClass* bldg = Buildings.Ptr(index);
                        if (bldg != this && bldg->Owner() == Owner() && *bldg == STRUCT_KENNEL) {
                            action = ACTION_TOGGLE_PRIMARY;
                            break;
                        }
                    }
                } else {
                    for (index = 0; index < Buildings.Count(); index++) {
                        BuildingClass* bldg = Buildings.Ptr(index);
                        if (bldg != this && bldg->Owner() == Owner() && bldg->Class->ToBuild == RTTI_INFANTRYTYPE
                            && *bldg != STRUCT_KENNEL) {
                            action = ACTION_TOGGLE_PRIMARY;
                            break;
                        }
                    }
                }
                break;

            case RTTI_AIRCRAFTTYPE:
            case RTTI_AIRCRAFT:
                action = ACTION_NONE;
                if (*this == STRUCT_AIRSTRIP || *this == STRUCT_TDAFLD || *this == STRUCT_TDGAFLD) {
                    for (index = 0; index < Buildings.Count(); index++) {
                        BuildingClass* bldg = Buildings.Ptr(index);
                        if (bldg != this && bldg->Owner() == Owner() && *bldg == Class->Type) {
                            action = ACTION_TOGGLE_PRIMARY;
                            break;
                        }
                    }
                } else {
                    for (index = 0; index < Buildings.Count(); index++) {
                        BuildingClass* bldg = Buildings.Ptr(index);
                        if (bldg != this && bldg->Owner() == Owner() && bldg->Class->ToBuild == RTTI_AIRCRAFTTYPE
                            && *bldg != STRUCT_AIRSTRIP && *bldg != STRUCT_TDAFLD && *bldg != STRUCT_TDGAFLD) {
                            action = ACTION_TOGGLE_PRIMARY;
                            break;
                        }
                    }
                }
                break;

            case RTTI_UNITTYPE:
            case RTTI_UNIT:
            case RTTI_VESSELTYPE:
            case RTTI_VESSEL:
                action = ACTION_TOGGLE_PRIMARY;
                break;

            case RTTI_NONE:
                action = ACTION_NONE;
                break;

            default:
                break;
            }

        } else if (TF_Packs_Into(this) == UNIT_NONE) {
            action = ACTION_NONE;
        }
    }

    /*
    **	Don't allow targeting of SAM sites, even if the CTRL key
    **	is held down. Also don't allow targeting if the object is too
    **	far away.
    */
    // TF: the TD SAM is barred like the SAM, and an AA gun only while its primary weapon can't hit the ground.
    bool aa_only_aagun = (*this == STRUCT_AAGUN && Class->PrimaryWeapon != NULL
                          && Class->PrimaryWeapon->Bullet != NULL
                          && !Class->PrimaryWeapon->Bullet->IsAntiGround);
    if (action == ACTION_ATTACK && (*this == STRUCT_SAM || *this == STRUCT_TDSAM || aa_only_aagun || !In_Range(object, 0))) {
        action = ACTION_NONE;
    }

    if (action == ACTION_MOVE) {
        action = ACTION_NONE;
    }

    return (action);
}

/***********************************************************************************************
 * BuildingClass::What_Action -- Determines what action will occur.                            *
 *                                                                                             *
 *    This routine examines the cell specified and returns with the action that will be        *
 *    performed if that cell were clicked upon while the building is selected.                 *
 *                                                                                             *
 * INPUT:   cell  -- The cell to examine.                                                      *
 *                                                                                             *
 * OUTPUT:  Returns the ActionType that indicates what should occur if the mouse is clicked    *
 *          on this cell.                                                                      *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/18/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
ActionType BuildingClass::What_Action(CELL cell) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    ActionType action = TechnoClass::What_Action(cell);

    // TF: attack-move given to a building becomes a move, the action rally points ride.
    if (action == ACTION_ATTACKMOVE) {
        action = ACTION_MOVE;
    }

    // TF: a rally-capable factory keeps the move cursor on any cell, even one its footprint couldn't stand on;
    // Target_For_Rally_Point resolves the rally point to a reachable cell.
    if (action == ACTION_NOMOVE && Can_Have_Rally_Point()) {
        action = ACTION_MOVE;
    }
    if (action == ACTION_MOVE && !Can_Have_Rally_Point() && TF_Packs_Into(this) == UNIT_NONE
        && (!Class->Is_Construction_Yard() || !Is_MCV_Deploy())) {
        action = ACTION_NONE;
    }

    /*
    **	A deployed TS building takes a move order anywhere its vehicle could go: the order packs
    **	it up and the vehicle drives off, so cells its own footprint could never sit on qualify.
    */
    if (TF_Packs_Into(this) != UNIT_NONE && !Is_TS_War_Factory() && (action == ACTION_NOMOVE || action == ACTION_NONE)
        && Map.In_Radar(cell)) {
        action = ACTION_MOVE;
    }

    /*
    **	Don't allow targeting of SAM sites, even if the CTRL key
    **	is held down.
    */
    if (action == ACTION_ATTACK && Class->PrimaryWeapon != NULL && !Class->PrimaryWeapon->Bullet->IsAntiGround) {
        //	if (action == ACTION_ATTACK && (*this == STRUCT_SAM || *this == STRUCT_AAGUN)) {
        action = ACTION_NONE;
    }

    return (action);
}

/***********************************************************************************************
 * BuildingClass::Begin_Mode -- Begins an animation mode for the building.                     *
 *                                                                                             *
 *    This routine will start the building animating. This animation will loop indefinitely    *
 *    until explicitly stopped.                                                                *
 *                                                                                             *
 * INPUT:   bstate   -- The animation state to initiate.                                       *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   The building graphic state will reflect the first stage of this animation the   *
 *             very next time it is rendered.                                                  *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *   07/02/1995 JLB : Uses normalize animation rate where applicable.                          *
 *=============================================================================================*/
void BuildingClass::Begin_Mode(BStateType bstate)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    QueueBState = bstate;
    if (BState == BSTATE_NONE || bstate == BSTATE_CONSTRUCTION || ScenarioInit) {
        BState = bstate;
        QueueBState = BSTATE_NONE;
        BuildingTypeClass::AnimControlType const* ctrl = Fetch_Anim_Control();

        int rate = ctrl->Rate;
        if (Class->IsRegulated && bstate != BSTATE_CONSTRUCTION) {
            rate = Options.Normalize_Delay(rate);
        }
        Set_Rate(rate);
        Set_Stage(ctrl->Start);
    }
}

/***********************************************************************************************
 * BuildingClass::Center_Coord -- Fetches the center coordinate for the building.              *
 *                                                                                             *
 *    This routine is used to set the center coordinate for this building.                     *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the coordinate for the center location for the building.              *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/10/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
COORDINATE BuildingClass::Center_Coord(void) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    return (Coord_Add(Coord, CenterOffset[Class->Size]));
}

/***********************************************************************************************
 * BuildingClass::Docking_Coord -- Fetches the coordinate to use for docking.                  *
 *                                                                                             *
 *    This routine will return the coordinate to use when an object wishes to dock with this   *
 *    building. Normally the docking coordinate would be the center of the building.           *
 *    Exceptions to this would be the airfield and helipad. Their docking coordinates are      *
 *    offset to match the building artwork.                                                    *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the coordinate to head to when trying to dock with this building.     *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/21/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
COORDINATE BuildingClass::Docking_Coord(void) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (*this == STRUCT_TSHPAD) {
        /*
        **	The TS pad's landing circle is drawn across the 2x2 plot's middle, the art raised half a
        **	cell: a quarter of a cell above its centre.
        */
        return (Coord_Add(Coord, XY_Coord(256, 192)));
    }
    if (Class->Is_Helipad()) {
        return (Coord_Add(Coord, XYP_COORD(24, 18)));
    }
    if (*this == STRUCT_AIRSTRIP || *this == STRUCT_TDGAFLD) {
        // TDGAFLD is an art clone of AFLD -- same fixed-wing dock spot.
        return (Coord_Add(Coord, XYP_COORD(ICON_PIXEL_W + ICON_PIXEL_W / 2, 28)));
    }
    if (*this == STRUCT_TDAFLD) {
        // TD-authentic offset (tiberiandawn/building.cpp:3469). Cargo plane
        // (TDC17) lands at the centre-front of the 4×2 strip.
        return (Coord_Add(Coord, XYP_COORD(18, 30)));
    }
    if (*this == STRUCT_TSDEPT) {
        return (Coord_Add(Center_Coord(), XY_Coord(TS_DEPOT_SEAT_X_LEP, TS_DEPOT_SEAT_Y_LEP)));
    }
    return (TechnoClass::Docking_Coord());
}

/***********************************************************************************************
 * BuildingClass::Can_Fire -- Determines if this building can fire.                            *
 *                                                                                             *
 *    Use this routine to see if the building can fire its weapon.                             *
 *                                                                                             *
 *                                                                                             *
 * INPUT:   target   -- The target that firing upon is desired.                                *
 *                                                                                             *
 *          which    -- Which weapon to use when firing. 0=primary, 1=secondary.               *
 *                                                                                             *
 * OUTPUT:  Returns with the fire possibility code. If firing is allowed, then FIRE_OK is      *
 *          returned. Other cases will result in appropriate fire code value that indicates    *
 *          why firing is not allowed.                                                         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/03/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
FireErrorType BuildingClass::Can_Fire(TARGET target, int which) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    FireErrorType canfire = TechnoClass::Can_Fire(target, which);

    if (canfire == FIRE_OK) {

        /*
        **	Double check to make sure that the facing is roughly toward
        **	the target. If the difference is too great, then firing is
        **	temporarily postponed.
        */
        if (Class->IsTurretEquipped) {
            int diff = PrimaryFacing.Difference(Direction(TarCom));
            diff = abs(diff);
            // TF: the TD SAM shares the SAM's wide firing arc, so it can fire while still turning.
            if (ABS(diff) > ((*this == STRUCT_SAM || *this == STRUCT_TDSAM) ? 64 : 8)) {
                //			if (ABS(diff) > 8) {
                return (FIRE_FACING);
            }

            /*
            **	If the turret is rotating then firing must be delayed.
            */
            //			if (PrimaryFacing.Is_Rotating()) {
            //				return(FIRE_ROTATING);
            //			}
        }

        /*
        **	Certain buildings cannot fire if there is insufficient power.
        */
        if (Class->IsPowered && House->Power_Fraction() < 1) {
#if TF_DEV_BUILD // TF_AI_DIAG -- powered defence held offline by low power (~30s heartbeat per building).
            if (((Frame + ID) % 450) == 0) {
                extern FILE* TF_AI_Diag_File(void);
                FILE* _tfdbg = TF_AI_Diag_File();
                if (_tfdbg != NULL) {
                    fprintf(_tfdbg,
                            "F%ld H%d DEF-OFFLINE %s#%d (power %d/%d)\n",
                            (long)Frame,
                            (int)House->Class->House,
                            Class->IniName,
                            (int)ID,
                            (int)House->Power,
                            (int)House->Drain);
                    fflush(_tfdbg);
                }
            }
#endif
            return (FIRE_BUSY);
        }

        /*
        ** If an obelisk can fire, check the state of charge.
        */
        if (Class->PrimaryWeapon != NULL && Class->PrimaryWeapon->IsElectric && !IsCharged) {
            return (FIRE_BUSY);
        }
    }
    return (canfire);
}

/***********************************************************************************************
 * BuildingClass::Toggle_Primary -- Toggles the primary factory state.                         *
 *                                                                                             *
 *    This routine will change the primary factory state of this building. The primary         *
 *    factory is the one that units will be produced from (by default).                        *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Is this building NOW the primary factory?                                          *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/03/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool BuildingClass::Toggle_Primary(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (IsLeader) {
        IsLeader = false;
    } else {
        for (int index = 0; index < Buildings.Count(); index++) {
            BuildingClass* building = Buildings.Ptr(index);

            if (!building->IsInLimbo && building->Owner() == Owner() && building->Class->ToBuild == Class->ToBuild) {
                if (Class->ToBuild == RTTI_INFANTRYTYPE) {
                    if (*building == STRUCT_KENNEL && *this == STRUCT_KENNEL) {
                        building->IsLeader = false;
                    } else {
                        if (*building != STRUCT_KENNEL && *this != STRUCT_KENNEL) {
                            building->IsLeader = false;
                        }
                    }
                } else if (Class->ToBuild == RTTI_AIRCRAFTTYPE) {
                    // Fixed-wing strips (AIRSTRIP + the TD ports) form one primary-factory
                    // group; helipads the other.
                    bool this_strip = (*this == STRUCT_AIRSTRIP || *this == STRUCT_TDAFLD
                                       || *this == STRUCT_TDGAFLD);
                    bool that_strip = (*building == STRUCT_AIRSTRIP || *building == STRUCT_TDAFLD
                                       || *building == STRUCT_TDGAFLD);
                    if (that_strip && this_strip) {
                        building->IsLeader = false;
                    } else {
                        if (!that_strip && !this_strip) {
                            building->IsLeader = false;
                        }
                    }
                } else {
                    building->IsLeader = false;
                }
            }
        }
        IsLeader = true;
        //
        // MBL 04.20.2020 - Update so that each player in multiplayer will properly hear this when it applies to them
        //
        // if ((HouseClass *)House == PlayerPtr) {
        // 	Speak(VOX_PRIMARY_SELECTED);
        // }
        if (House->IsHuman) {
            Speak(VOX_PRIMARY_SELECTED, House);
        }
    }
    Mark(MARK_CHANGE);
    return (IsLeader);
}

/***********************************************************************************************
 * BuildingClass::Captured -- Captures the building.                                           *
 *                                                                                             *
 *    This routine will change the owner of the building. It handles updating any related      *
 *    game systems as a result. Factories are the most prone to have great game related        *
 *    consequences when captured. This could also affect the sidebar and building ownership.   *
 *                                                                                             *
 * INPUT:   newowner -- Pointer to the house that is now the new owner.                        *
 *                                                                                             *
 * OUTPUT:  Was the capture attempt successful?                                                *
 *                                                                                             *
 * WARNINGS:   Capturing could fail if the house is already owned by the one specified or      *
 *             the building isn't allowed to be captured.                                      *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/03/1995 JLB : Created.                                                                 *
 *   07/05/1995 JLB : Fixed production problem with capturing enemy buildings.                 *
 *=============================================================================================*/
bool BuildingClass::Captured(HouseClass* newowner)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (Can_Capture() && newowner != House) {
#ifdef TOFIX
        switch (Owner()) {
        case HOUSE_GOOD:
            Speak(VOX_GDI_CAPTURED);
            break;

        case HOUSE_BAD:
            Speak(VOX_NOD_CAPTURED);
            break;
        }
#endif
#ifdef REMASTER_BUILD
        /*
        ** Maybe trigger an achivement. ST - 11/14/2019 1:53PM
        */
        if (newowner->IsHuman) {
            TechnoTypeClass const* object_type = Techno_Type_Class();
            if (object_type) {
                if (newowner->ActLike != House->ActLike) {
                    On_Achievement_Event(newowner, "OPPOSING_BUILDING_CAPTURED", object_type->IniName);
                } else {
                    On_Achievement_Event(newowner, "BUILDING_CAPTURED", object_type->IniName);
                }
            }
        }
#endif
        /*
        ** Make sure the capturer isn't spying on his own building, and if
        ** it was a radar facility, update the target house's RadarSpied field.
        */
        if (SpiedBy & (1 << (newowner->Class->House))) {
            SpiedBy -= (1 << (newowner->Class->House));
            if (*this == STRUCT_RADAR || *this == STRUCT_TDHQ || *this == STRUCT_TDEYE || *this == STRUCT_TSRADR) {
                Update_Radar_Spied();
            }
        }

        if (House == PlayerPtr) {
            Map.PowerClass::IsToRedraw = true;
            Map.Flag_To_Redraw(false);
        }

        if (*this == STRUCT_GAP) {
            Remove_Gap_Effect();
            IsJamming = false;
            Arm = 0;
        }

        /*
        ** Add this building to the list of buildings captured this game. For internet stats purposes.
        */
        if (Session.Type == GAME_INTERNET) {
            newowner->CapturedBuildings.Increment_Unit_Total(Class->Type);
        }

        House->Adjust_Power(-Power_Output());
        LastStrength = 0;
        House->Adjust_Drain(-(Class->Drain + Upgrade_Drain()));
        int booty = House->Adjust_Capacity(-Class->Capacity, true);

        /*
        **	If there is something loaded, then it gets captured as well.
        */
        TechnoClass* tech = Attached_Object();
        if (tech)
            tech->Captured(newowner);

        /*
        **	If something isn't technically attached, but is sitting on this
        **	building for another reason (e.g., helicopter on helipad), then it
        **	gets captured as well.
        */
        tech = Contact_With_Whom();
        if (tech) {
            // TF: a harvester unloading at the refinery (IsDumping) is captured with it, skipping the
            // RADIO_NEED_TO_MOVE test below, which can send a busy harvester away.
            if (tech->What_Am_I() == RTTI_UNIT && ((UnitClass*)tech)->Class->IsToHarvest
                && ((UnitClass*)tech)->IsDumping) {
                tech->Captured(newowner);
            } else if (Transmit_Message(RADIO_NEED_TO_MOVE) == RADIO_ROGER
                && (::Distance(tech->Center_Coord(), Docking_Coord()) < 0x0040
                    || (tech->What_Am_I() == RTTI_AIRCRAFT && ((AircraftClass*)tech)->Class->IsFixedWing
                        && ((AircraftClass*)tech)->In_Which_Layer() == LAYER_GROUND))) {
                tech->Captured(newowner);
            } else {
                Transmit_Message(RADIO_RUN_AWAY);
                Transmit_Message(RADIO_OVER_OUT);
            }
        }

        /*
        **	Abort any computer production in progress.
        */
        if (Factory) {
            delete (FactoryClass*)Factory;
            Factory = 0;
        }

        /*
        **	Decrement the factory counter for the original owner.
        */
        House->Active_Remove(this);

        /*
        **	Flag that both owners now need to update their buildable lists.
        */
        House->IsRecalcNeeded = true;
        newowner->IsRecalcNeeded = true;
        HouseClass* oldowner = House;
        TARGET tocap = As_Target();

        IsCaptured = true;
        TechnoClass::Captured(newowner);

        oldowner->ToCapture = tocap;
        oldowner->Recalc_Center();
        House->Recalc_Center();
        if (House->ToCapture == As_Target()) {
            House->ToCapture = TARGET_NONE;
        }

        SmudgeType bib;
        CELL cell = Coord_Cell(Coord);
        if (Class->Bib_And_Offset(bib, cell)) {
            SmudgeClass* smudge = new SmudgeClass(bib);
            if (smudge) {
                smudge->Disown(cell);
                delete smudge;
            }
#ifdef FIXIT_CAPTURE_BIB
            if (Session.Type == GAME_NORMAL) {
                new SmudgeClass(bib, Cell_Coord(cell), Class->IsBase ? House->Class->House : HOUSE_NONE);
            } else {
                new SmudgeClass(bib, Cell_Coord(cell), House->Class->House);
            }
#else
            new SmudgeClass(bib, Cell_Coord(cell), House->Class->House);
#endif
        }

        House->Stole(Refund_Amount());

        /*
        **	Increment the factory count for the new owner.
        */
        House->Active_Add(this);

        IsRepairing = false;
        Grand_Opening(true);
        House->Harvested(booty);

        Mark(MARK_CHANGE);

        /*
        **	Perform a look operation when captured if it was the player
        **	that performed the capture.
        */
        if (Session.Type == GAME_GLYPHX_MULTIPLAYER && House->IsHuman) {
            Look(false);
        } else {
            if (House == PlayerPtr) {
                Look(false);
            }
        }
        /*
        ** If it was spied upon by the player who just captured it, clear the
        ** spiedby flag for that house.
        */
        if (SpiedBy & (1 << (newowner->Class->House))) {
            SpiedBy &= ~(1 << (newowner->Class->House));
        }

        /*
        ** Update the new building's colors on the radar map.
        */
        short const* offset = Occupy_List();
        while (*offset != REFRESH_EOL) {
            CELL cell = Coord_Cell(Coord) + *offset++;
            Map.Radar_Pixel(cell);
        }

        if (oldowner) {
            oldowner->Check_Pertinent_Structures();
        }

        return (true);
    }
    return (false);
}

/***********************************************************************************************
 * BuildingClass::Sort_Y -- Returns the building coordinate used for sorting.                  *
 *                                                                                             *
 *    The coordinate value returned from this function should be used for sorting purposes.    *
 *    It has special offset adjustment applied so that vehicles don't overlap (as much).       *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with a coordinate value suitable to be used for sorting.                   *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/23/1995 JLB : Created.                                                                 *
 *   06/19/1995 JLB : Handles buildings that come with bibs built-in.                          *
 *=============================================================================================*/
COORDINATE BuildingClass::Sort_Y(void) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (*this == STRUCT_REPAIR || *this == STRUCT_TDFIX || *this == STRUCT_TSDEPT) {
        return (Coord);
    }
    if (Class->Is_Helipad()) {
        return (Center_Coord());
    }
    if (*this == STRUCT_AIRSTRIP || *this == STRUCT_TDGAFLD) {
        return (Center_Coord());
    }
    if (*this == STRUCT_BARRACKS /*|| *this == STRUCT_POWER*/) {
        return (Center_Coord());
    }
    // TF: the TD and TS refineries and TS war factories sort at their centre too, so a vehicle on the apron or
    // in the bay draws over them; DLL_Draw_Intercept sorts the war factory's shutter layers south of this point.
    if ((*this == STRUCT_REFINERY || *this == STRUCT_TDPROC || *this == STRUCT_TSPROC
         || Is_TS_War_Factory())) {
        return (Center_Coord());
    }
    // TF: a mod sprite (ShapeSize=) wider than tall, or 3 cells or more either way, overhangs south and sorts
    // at its centre; smaller ones keep the height-biased sort below (docs/td-port-playbook.md).
    if (Class->ShapeWidth > 0 && Class->ShapeHeight > 0
        && (Class->ShapeWidth > Class->ShapeHeight || Class->ShapeWidth >= 72 || Class->ShapeHeight >= 72)) {
        return (Center_Coord());
    }

    /*
    **	Mines need to bias their sort location such that they are typically drawn
    **	before any objects that might overlap them.
    */
    if (*this == STRUCT_AVMINE || *this == STRUCT_APMINE || *this == STRUCT_TSDLIMP || *this == STRUCT_TSFSDF) {
        return (Coord_Move(Center_Coord(), DIR_N, CELL_LEPTON_H));
    }

    // TF: a component tower sorts as a one-cell building on its south cell, so its links and neighbours layer
    // as walls expect.
    if (TF_Is_Wall_Tower(Class->Type)) {
        return (Coord_Add(Center_Coord(), XY_Coord(0, CELL_LEPTON_H / 2 + CELL_LEPTON_H / 3)));
    }

    /*
    **	A gate sorts just north of its own northern row, so a unit anywhere in the gate draws
    **	over it while a building north of it still draws first.
    */
    if (TF_Gate_Info(Class->Type) != NULL) {
        return (Coord_Move(Center_Coord(), DIR_N, (Class->Height() * CELL_LEPTON_H) / 2 + CELL_LEPTON_H / 4));
    }

    return (Coord_Add(Center_Coord(), XY_Coord(0, (Class->Height() * 256) / 3)));
}

// Gate types. The sliding gates open in about TS's DeployTime=.044 minutes; the energy gates (Soviet Tesla,
// TD Nod laser) switch about four times faster and stand open while their house is short of power.
static TFGateInfo const TFGates[] = {
    {STRUCT_TSGATEH, true, 10, 4, VOC_TS_GATEDWN1, VOC_TS_GATEUP1, false, 0, 'S'},
    {STRUCT_TSGATEV, false, 10, 4, VOC_TS_GATEDWN1, VOC_TS_GATEUP1, false, 0, 'S'},
    {STRUCT_TSNGATEH, true, 7, 7, VOC_TS_GATEDWN1, VOC_TS_GATEUP1, false, 0, 'S'},
    {STRUCT_TSNGATEV, false, 7, 7, VOC_TS_GATEDWN1, VOC_TS_GATEUP1, false, 0, 'S'},
    {STRUCT_ALGATEH, true, 10, 4, VOC_TS_GATEDWN1, VOC_TS_GATEUP1, false, 0, 'R'},
    {STRUCT_ALGATEV, false, 10, 4, VOC_TS_GATEDWN1, VOC_TS_GATEUP1, false, 0, 'R'},
    {STRUCT_SVGATEH, true, 10, 1, VOC_TSLACHG2R, VOC_TESLA_POWER_UP, true, 3, 'R'},
    {STRUCT_SVGATEV, false, 10, 1, VOC_TSLACHG2R, VOC_TESLA_POWER_UP, true, 3, 'R'},
    {STRUCT_TDGGATEH, true, 10, 4, VOC_TS_GATEDWN1, VOC_TS_GATEUP1, false, 0, 'D'},
    {STRUCT_TDGGATEV, false, 10, 4, VOC_TS_GATEDWN1, VOC_TS_GATEUP1, false, 0, 'D'},
    {STRUCT_TDNGATEH, true, 10, 1, VOC_NONE, VOC_NONE, true, 0, 'D'},
    {STRUCT_TDNGATEV, false, 10, 1, VOC_NONE, VOC_NONE, true, 0, 'D'},
};

TFGateInfo const* TF_Gate_Info(StructType t)
{
    for (int i = 0; i < (int)(sizeof(TFGates) / sizeof(TFGates[0])); i++) {
        if (TFGates[i].Type == t) {
            return (&TFGates[i]);
        }
    }
    return (NULL);
}

/*
**	How long an open gate stands once its footprint is clear (TS GateCloseDelay=.2 minutes).
*/
static const int TF_GATE_HOLD = TICKS_PER_MINUTE / 5;

// A friendly unit about to enter asks the gate to open; true only once the door is fully up, so the unit
// waits. A gate being built or sold never opens.
bool BuildingClass::Open_Gate(void)
{
    TFGateInfo const* gate = TF_Gate_Info(Class->Type);
    if (gate == NULL) {
        return (true);
    }
    if (BState == BSTATE_CONSTRUCTION || Mission == MISSION_DECONSTRUCTION) {
        return (false);
    }
    GateHold = TF_GATE_HOLD;
    if (Is_Door_Open()) {
        return (true);
    }
    if ((Reopen_Door() || (Is_Door_Closed() && Open_Door(gate->Rate, gate->Stages))) && gate->OpenSound != VOC_NONE) {
        Sound_Effect(gate->OpenSound, Center_Coord());
    }
    Mark(MARK_CHANGE_REDRAW);
    return (false);
}

// An open gate holds while anything stands in its footprint and closes once the hold runs out. An energy
// gate without power opens and stays open to everyone.
void BuildingClass::Gate_AI(void)
{
    TFGateInfo const* gate = TF_Gate_Info(Class->Type);
    if (gate == NULL || BState == BSTATE_CONSTRUCTION) {
        return;
    }
    if (Is_Door_Opening() || Is_Door_Closing() || (gate->IdleFrames > 0 && Is_Door_Closed())) {
        Mark(MARK_CHANGE_REDRAW);
    }

    if (gate->NeedsPower && House->Power_Fraction() < 1) {
        GateHold = TF_GATE_HOLD;
        if ((Reopen_Door() || (Is_Door_Closed() && Open_Door(gate->Rate, gate->Stages))) && gate->OpenSound != VOC_NONE) {
            Sound_Effect(gate->OpenSound, Center_Coord());
        }
        return;
    }


    if (!Is_Door_Open()) {
        return;
    }
    short const* offset = Class->Occupy_List();
    while (offset != NULL && *offset != REFRESH_EOL) {
        CELL cell = Coord_Cell(Coord) + *offset++;
        for (ObjectClass* obj = Map[cell].Cell_Occupier(); obj != NULL; obj = obj->Next) {
            if (obj != this) {
                GateHold = TF_GATE_HOLD;
                break;
            }
        }
    }
    if (GateHold == 0) {
        Close_Door(gate->Rate, gate->Stages);
        if (gate->CloseSound != VOC_NONE) {
            Sound_Effect(gate->CloseSound, Center_Coord());
        }
        Mark(MARK_CHANGE_REDRAW);
    }
}

// May this unit step into the cell now? A friendly gate there is asked to open and admits it once fully
// open; anyone else gets in only while it stands open. A cell with no gate answers yes.
bool TF_Gate_Lets_Through(FootClass* foot, CELL cell)
{
    if (foot == NULL || !Map.In_Radar(cell)) {
        return (true);
    }
    for (ObjectClass* obj = Map[cell].Cell_Occupier(); obj != NULL; obj = obj->Next) {
        if (obj != foot && obj->What_Am_I() == RTTI_BUILDING) {
            BuildingClass* gate = (BuildingClass*)obj;
            if (TF_Gate_Info(gate->Class->Type) != NULL) {
                if (gate->House->Is_Ally(foot->House)) {
                    return (gate->Open_Gate());
                }
                return (gate->Is_Gate_Open());
            }
        }
    }
    return (true);
}

/***********************************************************************************************
 * Is_TS_Weap_Exit_Cell -- Is this cell a TS war factory's doorstep?                          *
 *                                                                                             *
 *    A vehicle leaving the TS bay rides a rail onto its doorstep before it is free to turn,   *
 *    so that tile has to stay empty. An idle guard or a parked tank standing on it makes the  *
 *    new vehicle path around its own doorway -- the reverse-then-forward jink -- and shoves    *
 *    it back through the building it is trying to leave. Same treatment as the refinery dock  *
 *    pad below: everything except the vehicle currently leaving reads the cell as impassable. *
 *                                                                                             *
 *    The War Factory's doorstep is XYCELL(1,3), the middle of the concrete in front of its    *
 *    door; the deployed Mobile War Factory's is XYCELL(4,3), one row south of its 5x3 plot on *
 *    the eastern column, where its bay points.                                                *
 *=============================================================================================*/
bool Is_TS_Weap_Exit_Cell(CELL cell)
{
    if ((unsigned)cell >= MAP_CELL_TOTAL) {
        return (false);
    }

    /*
    **	Walk back from the candidate to where each war factory's north-west
    **	corner would be, and confirm one of that type stands there, read from a
    **	cell it occupies.
    */
    static const struct
    {
        StructType type;
        int dx, dy;
        int probe;
    } _doorsteps[] = {
        {STRUCT_TSWEAP, 1, 2, 0},
        {STRUCT_TSDWEAP, 1, 2, 0},
    };
    for (int i = 0; i < (int)(sizeof(_doorsteps) / sizeof(_doorsteps[0])); i++) {
        int x = Cell_X(cell) - _doorsteps[i].dx;
        int y = Cell_Y(cell) - _doorsteps[i].dy;
        if (x < 0 || y < 0) {
            continue;
        }
        CELL origin = XY_Cell(x, y);
        BuildingClass const* b = Map[(CELL)(origin + _doorsteps[i].probe)].Cell_Building();
        if (b != NULL && *b == _doorsteps[i].type && Coord_Cell(b->Coord) == origin) {
            return (true);
        }
    }
    return (false);
}

bool Is_Refinery_Dock_Cell(CELL cell)
{
    if ((unsigned)cell >= MAP_CELL_TOTAL) {
        return (false);
    }

    CELL ncell = Adjacent_Cell(cell, FACING_N);
    if ((unsigned)ncell < MAP_CELL_TOTAL) {
        BuildingClass const* b = Map[ncell].Cell_Building();
        if (b != NULL && *b == STRUCT_REFINERY && Coord_Cell(b->Center_Coord()) == ncell) {
            return (true);
        }
    }

    /*
    **	TS refinery: dock pad = the 4x3 foundation's centre cell itself. The
    **	pad is an occupy HOLE (no building in its occupier chain), so the
    **	building pointer is read from the occupied cell to its west; the centre
    **	check then points back at the candidate cell.
    */
    CELL tsncell = Adjacent_Cell(cell, FACING_W);
    if ((unsigned)tsncell < MAP_CELL_TOTAL) {
        BuildingClass const* b = Map[tsncell].Cell_Building();
        if (b != NULL && *b == STRUCT_TSPROC && Coord_Cell(b->Center_Coord()) == cell) {
            return (true);
        }
    }

    CELL necell = Adjacent_Cell(cell, FACING_NE);
    if ((unsigned)necell < MAP_CELL_TOTAL) {
        BuildingClass const* b = Map[necell].Cell_Building();
        if (b != NULL && *b == STRUCT_TDPROC && Coord_Cell(b->Center_Coord()) == necell) {
            return (true);
        }
    }


    return (false);
}

/***********************************************************************************************
 * TS_Refinery_Lane_Owner -- The TS refinery whose dock lane holds this cell.                  *
 *                                                                                             *
 *    The lane is the pad and its east, south and south-east neighbours: the plate the truck   *
 *    lines up on, the cells it reverses across into the seat and drives back out over. The   *
 *    rails in and out don't check who is standing there, so the lane belongs to the truck    *
 *    in radio contact with the refinery and every other unit reads it as impassable.          *
 *=============================================================================================*/
BuildingClass* TS_Refinery_Lane_Owner(CELL cell)
{
    if ((unsigned)cell >= MAP_CELL_TOTAL) {
        return (NULL);
    }
    int const _back[] = {0, 1, MAP_CELL_W, MAP_CELL_W + 1};
    for (int i = 0; i < (int)(sizeof(_back) / sizeof(_back[0])); i++) {
        CELL pad = (CELL)(cell - _back[i]);
        if ((unsigned)pad >= MAP_CELL_TOTAL || Cell_Y(pad) != Cell_Y(cell) - (i >= 2)
            || (unsigned)(pad - 1) >= MAP_CELL_TOTAL) {
            continue;
        }
        BuildingClass* b = Map[(CELL)(pad - 1)].Cell_Building();
        if (b != NULL && *b == STRUCT_TSPROC && Coord_Cell(b->Center_Coord()) == pad) {
            return (b);
        }
    }
    return (NULL);
}

/***********************************************************************************************
 * Is_Refinery_Dock_Busy -- Is this dock pad's refinery mid-attach-unload?                     *
 *                                                                                             *
 *    True while the refinery that owns this dock pad has a harvester ATTACHED (limbo'd,       *
 *    unloading). Used to close the pad to ALL units -- including queued harvesters -- so      *
 *    nothing drives across the baked docked-truck visuals.                                    *
 *=============================================================================================*/
bool Is_Refinery_Dock_Busy(CELL cell)
{
    if ((unsigned)cell >= MAP_CELL_TOTAL) {
        return (false);
    }
    /*
    **	centre_is_pad: TSPROC's centre cell IS its dock pad (an occupy hole),
    **	so the building pointer comes from the occupied cell in `facing`
    **	direction (west of the pad) while the centre check points back at the
    **	pad cell itself.
    */
    struct
    {
        FacingType facing;
        StructType type;
        bool centre_is_pad;
    } const _pads[] = {
        {FACING_N, STRUCT_REFINERY, false}, {FACING_W, STRUCT_TSPROC, true}, {FACING_NE, STRUCT_TDPROC, false}};
    for (int i = 0; i < (int)(sizeof(_pads) / sizeof(_pads[0])); i++) {
        CELL rcell = Adjacent_Cell(cell, _pads[i].facing);
        if ((unsigned)rcell >= MAP_CELL_TOTAL) {
            continue;
        }
        BuildingClass const* b = Map[rcell].Cell_Building();
        if (b != NULL && *b == _pads[i].type && Coord_Cell(b->Center_Coord()) == (_pads[i].centre_is_pad ? cell : rcell)
            && b->Is_Something_Attached()) {
            return (true);
        }
    }
    return (false);
}

// True for the TS aprons: bib-family smudges drawn as ground decoration, which never decide where a
// building may stand (Is_TS_Apron_Cell does).
bool Is_TS_Apron_Smudge(SmudgeType smudge)
{
    return (smudge == SMUDGE_TSWEAPBB || smudge == SMUDGE_TSPROCBB || smudge == SMUDGE_TSDWEAPBB);
}

#if TF_DEV_BUILD
// Logs a TS war factory's hand-offs and unload steps to Documents/CnCRemastered/tf_mwf.log, for the Mobile War
// Factory losing units (docs/todo.md). Capped at 5000 lines a session.
void TF_WF_Log(BuildingClass const* wf, char const* fmt, ...)
{
    static FILE* log = NULL;
    static bool tried = false;
    static int lines = 0;
    if (!tried) {
        tried = true;
        char const* h = getenv("USERPROFILE");
        if (h == NULL) {
            h = getenv("HOME");
        }
        if (h != NULL) {
            char p[512];
            snprintf(p, sizeof(p), "%s/Documents/CnCRemastered/tf_mwf.log", h);
            log = fopen(p, "a");
            if (log != NULL) {
                fprintf(log, "--- session\n");
            }
        }
    }
    if (log == NULL || wf == NULL || lines >= 5000) {
        return;
    }
    lines++;
    TechnoClass const* who = wf->Contact_With_Whom();
    fprintf(log,
            "f=%d %s#%d mission=%s status=%d door=%d tethered=%d contact=",
            (int)Frame,
            wf->Class->IniName,
            wf->ID,
            MissionClass::Mission_Name(wf->Mission),
            wf->Status,
            wf->Door_Stage(),
            wf->IsTethered ? 1 : 0);
    if (who != NULL) {
        fprintf(log, "%s#%d@(%d,%d) ", who->Class_Of().IniName, who->ID, Coord_X(who->Coord), Coord_Y(who->Coord));
    } else {
        fprintf(log, "none ");
    }
    va_list ap;
    va_start(ap, fmt);
    vfprintf(log, fmt, ap);
    va_end(ap);
    fprintf(log, "\n");
    fflush(log);
}
#endif

// True when the cell is a TS building's walkable apron or the Service Depot's empty corner, where
// Is_Clear_To_Build allows no building. The table lists each apron cell as an offset back to its building's centre.
bool Is_TS_Apron_Cell(CELL cell)
{
    if ((unsigned)cell >= MAP_CELL_TOTAL) {
        return (false);
    }

    static struct
    {
        StructType Type;
        short Offset;
    } const _to_centre[] = {
        /*
        **	TSPROC, 4x3: centre = the dock pad, so the pad's own offset is 0.
        */
        {STRUCT_TSPROC, 0},              // the dock pad itself (occupy hole)
        {STRUCT_TSPROC, MAP_CELL_W},     // south row, col 2 (the lane's mouth)
        {STRUCT_TSPROC, MAP_CELL_W + 1}, // south row, col 3 (the plate)
        {STRUCT_TSPROC, 1},              // east col, row 1
        {STRUCT_TSPROC, -2 - MAP_CELL_W}, // north row (headroom under the stacks), cols 0-3
        {STRUCT_TSPROC, -1 - MAP_CELL_W},
        {STRUCT_TSPROC, 0 - MAP_CELL_W},
        {STRUCT_TSPROC, 1 - MAP_CELL_W},

        // The War Factory and the deployed Mobile War Factory, 3x3: centre = row 1 col 1 (the hall).
        // Walkable, never buildable: the concrete in front of the door (row 3, the door's lane down its middle).
        {STRUCT_TSWEAP, MAP_CELL_W - 1},
        {STRUCT_TSWEAP, MAP_CELL_W},
        {STRUCT_TSWEAP, MAP_CELL_W + 1},
        {STRUCT_TSDWEAP, MAP_CELL_W - 1},
        {STRUCT_TSDWEAP, MAP_CELL_W},
        {STRUCT_TSDWEAP, MAP_CELL_W + 1},
    };

    for (int i = 0; i < (int)(sizeof(_to_centre) / sizeof(_to_centre[0])); i++) {
        CELL centre = (CELL)(cell - _to_centre[i].Offset);
        if ((unsigned)centre >= MAP_CELL_TOTAL) {
            continue;
        }

        /*
        **	Resolve the building that would own this apron cell. The war
        **	factory's centre is one of its own solid cells and answers
        **	directly. The refinery's centre is the dock pad, an occupy HOLE
        **	that can never answer -- Cell_Building walks the occupier chain
        **	only, and overlap cells live in a separate array -- so fall back
        **	to the occupied cell directly west of it.
        */
        BuildingClass const* b = Map[centre].Cell_Building();
        if (b == NULL) {
            CELL bcell = (CELL)(centre - 1);
            if ((unsigned)bcell >= MAP_CELL_TOTAL) {
                continue;
            }
            b = Map[bcell].Cell_Building();
        }
        if (b != NULL && *b == _to_centre[i].Type && Coord_Cell(b->Center_Coord()) == centre) {
            return (true);
        }
    }

    /*
    **	The service depot's empty north-east cells (its overlap list). Other tall buildings' headroom rows stay
    **	free ground: another building may stand under the art that reaches over them.
    */
    CellClass const& here = Map[cell];
    for (int i = 0; i < (int)(sizeof(here.Overlapper) / sizeof(here.Overlapper[0])); i++) {
        ObjectClass const* o = here.Overlapper[i];
        if (o == NULL || o->What_Am_I() != RTTI_BUILDING) {
            continue;
        }
        BuildingClass const* b = (BuildingClass const*)o;
        if (*b != STRUCT_TSDEPT) {
            continue;
        }
        short const* list = b->Class->Overlap_List();
        CELL origin = Coord_Cell(b->Coord);
        for (; list != NULL && *list != REFRESH_EOL; list++) {
            if ((CELL)(origin + *list) == cell) {
                return (true);
            }
        }
    }
    return (false);
}

/***********************************************************************************************
 * BuildingClass::Can_Enter_Cell -- Determines if building can be placed down.                 *
 *                                                                                             *
 *    This routine will determine if the building can be placed down at the location           *
 *    specified.                                                                               *
 *                                                                                             *
 * INPUT:   cell  -- The cell to examine. This is usually the cell of the upper left corner    *
 *                   of the building if it were to be placed down.                             *
 *                                                                                             *
 * OUTPUT:  Returns with the move legality value for placement at the location specified. This *
 *          will either be MOVE_OK or MOVE_NO.                                                 *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
MoveType BuildingClass::Can_Enter_Cell(CELL cell, FacingType) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (Class->Is_Construction_Yard() && IsDown) {
        return (Map[cell].Is_Clear_To_Build(Class->Speed) ? MOVE_OK : MOVE_NO);
    }

    if (!Debug_Map && ScenarioInit == 0 && Session.Type == GAME_NORMAL && House->IsPlayerControl
        && !Map[cell].IsMapped) {
        return (MOVE_NO);
    }

    return (Class->Legal_Placement(cell) ? MOVE_OK : MOVE_NO);
}

/***********************************************************************************************
 * BuildingClass::Can_Demolish -- Can the player demolish (sell back) the building?            *
 *                                                                                             *
 *    Determines if the player can sell this building. Selling is possible if the building     *
 *    is not currently in construction or deconstruction animation.                            *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Can the building be demolished at this time?                                       *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *   07/01/1995 JLB : If there is no buildup data, then the building can't be sold.            *
 *   07/17/1995 JLB : Cannot sell a refinery that has a harvester attached.                    *
 *=============================================================================================*/
bool BuildingClass::Can_Demolish(void) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (Class->IsUnsellable)
        return (false);

    if (*this == STRUCT_TSFSDF) {
        return (Is_Open_Firestorm_Section());
    }

    if (Class->Get_Buildup_Data() && BState != BSTATE_CONSTRUCTION && Mission != MISSION_DECONSTRUCTION
        && Mission != MISSION_CONSTRUCTION) {
        if ((*this == STRUCT_REFINERY || *this == STRUCT_TDPROC || *this == STRUCT_TSPROC) && Is_Something_Attached())
            return (false);
        return (true);
    }
    return (false);
}

bool BuildingClass::Can_Demolish_Unit(void) const
{
    return ((*this == STRUCT_REPAIR || *this == STRUCT_TDFIX || *this == STRUCT_TSDEPT
             || *this == STRUCT_AIRSTRIP || *this == STRUCT_TDGAFLD)
            && In_Radio_Contact() && Distance(Contact_With_Whom()) < 0x0080);
}

bool BuildingClass::Can_Capture(void) const
{
    bool can_capture = Class->IsCaptureable && Mission != MISSION_DECONSTRUCTION;

    // Only allow capturing of multiplayer-owned structures
    if (Session.Type != GAME_NORMAL) {
        if (*this == STRUCT_V01) { // Check to fix exploit in specific map 'Tournament Ore Rift'
            can_capture = false;
        }
    }

    return (can_capture);
}

/***********************************************************************************************
 * BuildingClass::Mission_Guard -- Handles guard mission for combat buildings.                 *
 *                                                                                             *
 *    Buildings that can attack are given this mission. They will wait until a suitable target *
 *    comes within range and then launch into the attack mission. Buildings that have no       *
 *    weaponry will just sit in this routine forever.                                          *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of game frames to delay before this routine will be called *
 *          again.                                                                             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingClass::Mission_Guard(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    /*
    **	If this building has a weapon, then search for a target to attack. When
    **	a target is found, switch into attack mode to deal with the threat.
    */
    if (Is_Weapon_Equipped()) {

        /*
        **	Weapon equipped buildings are ALWAYS ready to launch into another mission if
        **	they are sitting around in guard mode.
        */
        IsReadyToCommence = true;

        /*
        **	If there is no target available, then search for one.
        */
        if (!Target_Legal(TarCom)) {
            ThreatType threat = THREAT_NORMAL;
            Assign_Target(Greatest_Threat(threat));
        }

        /*
        **	There is a valid target. Switch into attack mode right away.
        */
        if (Target_Legal(TarCom)) {
            Assign_Mission(MISSION_ATTACK);
            Commence();
            return (1);
        }
    } else {

        /*
        **	This is the very simple state machine that basically does
        **	nothing. This is the mode that non weapon equipped buildings
        **	are normally in.
        */
        enum
        {
            INITIAL_ENTRY,
            IDLE
        };
        switch (Status) {
        case INITIAL_ENTRY:
            Begin_Mode(BSTATE_IDLE);
            Status = IDLE;
            break;

        case IDLE:
            /*
            **	Special case to break out of guard mode if this is a repair
            **	facility and there is a customer waiting at the grease pit.
            */
            if ((*this == STRUCT_REPAIR || *this == STRUCT_TDFIX || *this == STRUCT_TSDEPT)
                && In_Radio_Contact() && Contact_With_Whom()->Is_Techno()
                && ((TechnoClass*)Contact_With_Whom())->Mission == MISSION_ENTER
                && TF_Depot_Reach(Contact_With_Whom()) < 0x0040
                && Transmit_Message(RADIO_NEED_TO_MOVE) == RADIO_ROGER) {

                Assign_Mission(MISSION_REPAIR);
                return (1);
            }
            break;

        default:
            break;
        }

        if (*this == STRUCT_REPAIR || *this == STRUCT_TDFIX || *this == STRUCT_TSDEPT) {
            return (MissionControl[Mission].Normal_Delay() + Random_Pick(0, 2));
        } else {
            return (MissionControl[Mission].Normal_Delay() * 3 + Random_Pick(0, 2));
        }
    }
    return (MissionControl[Mission].AA_Delay() + Random_Pick(0, 2));
}

/***********************************************************************************************
 * BuildingClass::Mission_Construction -- Handles mission construction.                        *
 *                                                                                             *
 *    This routine will handle mission construction. When this mission is complete, the        *
 *    building will begin normal operation.                                                    *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of game frames to delay before calling this routine        *
 *          again.                                                                             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingClass::Mission_Construction(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    enum
    {
        INITIAL,
        DURING
    };
    switch (Status) {
    case INITIAL:
        Begin_Mode(BSTATE_CONSTRUCTION);
        Transmit_Message(RADIO_BUILDING);
        if (House->IsPlayerControl) {
            // TF: TD buildings play TD's construction loop; TS buildings rise in silence, as no TS structure
            // defines a build-up sound.
            if (Class->Is_TS_Era()) {
            } else if (Class->Is_Tiberian_Era()) {
                Sound_Effect(VOC_TD_CONSTRUCTION, Coord);
            } else {
                Sound_Effect(VOC_CONSTRUCTION, Coord);
            }
        }
        Status = DURING;
        break;

    case DURING:
        if (IsReadyToCommence) {

            /*
            **	When construction is complete, then transmit this
            **	to the construction yard so that it can stop its
            **	construction animation.
            */
            Transmit_Message(RADIO_COMPLETE); // "I'm finished."
            Transmit_Message(RADIO_OVER_OUT); // "You're free."
            Begin_Mode(BSTATE_IDLE);
            Grand_Opening();
            Assign_Mission(MISSION_GUARD);
            PrimaryFacing = Class->StartFace;
        }
        break;

    default:
        break;
    }
    return (1);
}

/***********************************************************************************************
 * BuildingClass::Mission_Deconstruction -- Handles building deconstruction.                   *
 *                                                                                             *
 *    This state machine is only used when the building is deconstructing as a result of       *
 *    selling.  When this mission is finished, the building will no longer exist.              *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of game frames to delay before calling this routine again. *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *   08/13/1995 JLB : Enable selling of units on a repair bay.                                 *
 *   08/20/1995 JLB : Scatters infantry from scattered starting points.                        *
 *=============================================================================================*/
int BuildingClass::Mission_Deconstruction(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    /*
    **	Always force repair off.
    */
    Repair(0);

    enum
    {
        INITIAL,
        HOLDING,
        DURING
    };
    switch (Status) {
    case INITIAL:

        /*
        **	Special check for the repair bay which has the ability to sell
        **	whatever is on it. If there is something on the repair bay, then
        **	it will be sold. If there is nothing on the repair bay, then
        **	the repair bay itself will be sold.
        */
        if (Can_Demolish_Unit() && Transmit_Message(RADIO_NEED_TO_MOVE) == RADIO_ROGER) {
            TechnoClass* tech = Contact_With_Whom();
            Transmit_Message(RADIO_OVER_OUT);
            if (IsOwnedByPlayer)
                Speak(VOX_UNIT_SOLD);
            tech->Sell_Back(1);
            Assign_Mission(MISSION_GUARD);
            return (1);
        }

        /*
        ** Selling off a shipyard or sub pen may cause attached ships
        ** who are repairing themselves to discontinue repairs.
        */
        if (*this == STRUCT_SHIP_YARD || *this == STRUCT_SUB_PEN) {
            for (int index = 0; index < Vessels.Count(); index++) {
                VesselClass* obj = Vessels.Ptr(index);
                if (obj && !obj->IsInLimbo && obj->House == House) {
                    if (obj->IsSelfRepairing) {
                        if (::Distance(Center_Coord(), obj->Center_Coord()) < 0x0200) {
                            obj->IsSelfRepairing = false;
                            obj->IsToSelfRepair = false;
                        }
                    }
                }
            }
        }

        IsReadyToCommence = false;
        Transmit_Message(RADIO_RUN_AWAY);
        Status = HOLDING;
        break;

    case HOLDING:
        if (!IsTethered) {

            /*
            **	The crew will evacuate from the building. The number of crew
            **	members leaving is equal to the unrecovered cost of the building
            **	divided by 100 (the typical cost of a minigunner infantryman).
            */
            if (!Target_Legal(ArchiveTarget) || !Is_MCV_Deploy() || !Class->Is_Construction_Yard()) {
                int count = How_Many_Survivors();
                bool engine = false;

                while (count) {

                    /*
                    **	Ensure that the player only gets ONE engineer and not from a captured
                    **	construction yard.
                    */
                    InfantryType typ = Crew_Type();
                    while (typ == INFANTRY_RENOVATOR && engine) {
                        typ = Crew_Type();
                    }
                    if (typ == INFANTRY_RENOVATOR)
                        engine = true;

                    InfantryClass* infantry = 0;
                    if (typ != INFANTRY_NONE)
                        infantry = new InfantryClass(typ, House->Class->House);
                    if (infantry != NULL) {
                        ScenarioInit++;
                        COORDINATE coord = Coord_Add(Center_Coord(), XYP_COORD(0, -12));

                        /* extra check to prevent building crew for Tesla Coil spawning
                           one cell above building foundation */
                        // TF: the Obelisk shares the Tesla Coil's 1x2 footprint.
                        if (*this == STRUCT_TESLA || *this == STRUCT_TDOBLI) {
                            coord = Map[coord].Adjacent_Cell(FACING_S)->Cell_Coord();
                        }
                        coord = Map[coord].Closest_Free_Spot(coord, false);

                        if (infantry->Unlimbo(coord, DIR_N)) {
                            infantry->IsZoneCheat =
                                infantry->Can_Enter_Cell(Coord_Cell(infantry->Center_Coord())) != MOVE_OK;
                            if (infantry->Class->IsNominal)
                                infantry->IsTechnician = true;
                            ScenarioInit--;
                            infantry->Scatter(0, true);
                            ScenarioInit++;
                            infantry->Assign_Mission(MISSION_GUARD_AREA);
                        } else {
                            delete infantry;
                        }
                        ScenarioInit--;
                    }
                    count--;
                }
            }

#ifdef REMASTER_BUILD
            // MBL 07.10.2020 - In 1v1, sometimes both players will hear this SFX, or neither player will hear it
            // Making it so all players hear it positionally in the map;
            Sound_Effect(VOC_CASHTURN, Coord);
#else
            if (House->IsPlayerControl) {
                Sound_Effect(VOC_CASHTURN, Coord);
            }
#endif

            /*
            **	Destroy all attached objects. ST - 4/24/2020 9:38PM
            */
            while (Attached_Object()) {
                FootClass* obj = Detach_Object();

                Detach_All(true);
                delete obj;
            }

            Transmit_Message(RADIO_OVER_OUT);
            Status = DURING;
            Begin_Mode(BSTATE_CONSTRUCTION);
            IsReadyToCommence = false;
            IsSurvivorless = true;
            break;
        }
        Transmit_Message(RADIO_RUN_AWAY);
        break;

    case DURING:
        if (IsReadyToCommence) {
            House->IsRecalcNeeded = true;

// MBL 05.06.2020 - "Structure Sold" is being heard when selecting/moving a redepolyable Con Yard to turn back into an
// MCV (RA only), so moving below
#if 0
				// MBL 04.06.2020: Fix being heard by wrong player
				// if (IsOwnedByPlayer) Speak(VOX_STRUCTURE_SOLD);
				if (IsOwnedByPlayer) {
					if ((HouseClass *)House == PlayerPtr) {
						Speak(VOX_STRUCTURE_SOLD);
					}
				}
#endif
            bool mcv_redeployed = false;

            /*
            **	Construction yards that deconstruct, really just revert back
            **	to an MCV.
            */
            if (Target_Legal(ArchiveTarget) && Class->Is_Construction_Yard() && House->IsHuman && Strength > 0) {
                // TF: each yard undeploys to its own faction's MCV, the inverse of MCV_Deploy_Building; the stock
                // yards keep their vanilla MCVs.
                UnitType mcv_type = UNIT_MCV;
                switch (Class->Type) {
                case STRUCT_AFACT:
                    mcv_type = UNIT_AMCV;
                    break;
                case STRUCT_SFACT:
                    mcv_type = UNIT_SMCV;
                    break;
                case STRUCT_TDGFACT:
                    mcv_type = UNIT_TDGMCV;
                    break;
                case STRUCT_TDNFACT:
                    mcv_type = UNIT_TDNMCV;
                    break;
                case STRUCT_TDFACT:
                    mcv_type = UNIT_TDMCV;
                    break;
                case STRUCT_TSFACT:
                    mcv_type = UNIT_TSMCV;
                    break;
                default:
                    break;
                }
                ScenarioInit++;
                UnitClass* unit = new UnitClass(mcv_type, House->Class->House);
                ScenarioInit--;
                if (unit != NULL) {

                    /*
                    **	Unlimbo the MCV onto the map. The MCV should start in the same
                    **	health condition that the construction yard was in.
                    */
                    fixed ratio = Health_Ratio();
                    int money = Refund_Amount();
                    TARGET arch = ArchiveTarget;
                    COORDINATE place = Coord_Snap(Adjacent_Cell(Coord, DIR_SE));

                    delete this;

                    if (unit->Unlimbo(place, DIR_SW)) {
                        unit->Strength = (int)unit->Class_Of().MaxStrength * ratio; // Cast to (int). ST - 5/8/2019

                        /*
                        **	Lift the move destination from the building and assign
                        **	it to the unit.
                        */
                        if (Target_Legal(arch)) {
                            unit->Assign_Destination(arch);
                            unit->Assign_Mission(MISSION_MOVE);
                        }

                        mcv_redeployed = true;

                    } else {

                        /*
                        **	If, for some strange reason, the MCV could not be placed on the
                        **	map, then give the player some money to compensate.
                        */
                        House->Refund_Money(money);
                    }
                } else {
                    House->Refund_Money(Refund_Amount());
                    delete this;
                }

            } else {

                /*
                ** Selling off a gap generator will cause the cells it affects
                ** to stop being jammed.
                */
                if (*this == STRUCT_GAP) {
                    Remove_Gap_Effect();
                }

                /*
                **	A sold building still counts as a kill, but it just isn't directly
                **	attributed to the enemy.
                */
                WhoLastHurtMe = HOUSE_NONE;
                Record_The_Kill(NULL);

                /*
                **	The player gets part of the money back for the sell.
                */
                House->Refund_Money(Refund_Amount());
                House->Stole(-Refund_Amount());
                Limbo();

                if (House) {
                    House->Check_Pertinent_Structures();
                }

                /*
                **	Finally, delete the building from the game.
                */
                delete this;
            }

// MBL 05.06.2020 - "Structure Sold" was being heard when selecting/moving a redepolyable Con Yard to turn back into an
// MCV (RA only) above, so moved here
#if 1
            if (!mcv_redeployed) {
                if (IsOwnedByPlayer) {
                    if ((HouseClass*)House == PlayerPtr) {
                        Speak(VOX_STRUCTURE_SOLD);
                    }
                }
            }
#endif
        }
        break;

    default:
        break;
    }
    return (1);
}

/***********************************************************************************************
 * BuildingClass::Mission_Attack -- Handles attack mission for building.                       *
 *                                                                                             *
 *    Buildings that can attack are processed by this attack mission state machine.            *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of game frames to delay before calling this routine        *
 *          again.                                                                             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *   02/22/1996 JLB : SAM doesn't lower back into ground.                                      *
 *=============================================================================================*/
int BuildingClass::Mission_Attack(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (*this == STRUCT_SAM) {
        switch (Status) {

        /*
        **	This is the target tracking state of the launcher. It will rotate
        **	to face the current TarCom of the launcher.
        */
        case SAM_READY:
            if ((Class->IsPowered && House->Power_Fraction() < 1) || IsJammed) {
                return (1);
            }
            if (!TF_SAM_Air_Target(TarCom)) {
                Assign_Target(TARGET_NONE);
                Status = SAM_READY;
                Assign_Mission(MISSION_GUARD);
                Commence();
                return (1);
            } else {
                if (!PrimaryFacing.Is_Rotating()) {
                    DirType facing = Direction(TarCom);
                    if (PrimaryFacing.Difference(facing)) {
                        PrimaryFacing.Set_Desired(facing);
                    } else {
                        Status = SAM_FIRING;
                    }
                }
            }
            return (1);

        /*
        **	The launcher is in the process of firing.
        */
        case SAM_FIRING:
            if (!TF_SAM_Air_Target(TarCom)) {
                Assign_Target(TARGET_NONE);
                Status = SAM_READY;
            } else {
                FireErrorType error = Can_Fire(TarCom, 0);
                if (error == FIRE_ILLEGAL || error == FIRE_CANT || error == FIRE_RANGE) {
                    Assign_Target(TARGET_NONE);
                    Status = SAM_READY;
                } else {
                    if (error == FIRE_FACING) {
                        Status = SAM_READY;
                    } else {
                        if (error == FIRE_OK) {
                            Fire_At(TarCom, 0);
                            Fire_At(TarCom, 1);
                            Status = SAM_READY;
                        }
                    }
                }
            }
            return (1);

        default:
            break;
        }
        return (MissionControl[Mission].AA_Delay() + Random_Pick(0, 2));
    }

    // TF: TD's SAM cycle: rise on acquiring a target, fire while an air target remains, then turn north and
    // lower. A launcher that loses its target takes another before lowering (Smarter SAMs, CFE Patch Redux).
    if (*this == STRUCT_TDSAM) {
        switch (Status) {

        case TDSAM_UNDERGROUND:
            IsReadyToCommence = true;
            if (Target_Legal(TarCom)) {
                Set_Rate(2);
                Set_Stage(0);
                Status = TDSAM_RISING;
                return (1);
            } else {
                Assign_Mission(MISSION_GUARD);
            }
            break;

        case TDSAM_RISING:
            if (Fetch_Stage() == 15) {
                Set_Rate(0);
                PrimaryFacing = DIR_N;
                if (!Target_Legal(TarCom)) {
                    Status = TDSAM_LOWERING;
                } else {
                    Status = TDSAM_READY;
                }
            }
            return (1);

        case TDSAM_READY:
            if (!TF_SAM_Air_Target(TarCom)) {
                if (TDSAM_Try_Reacquire()) {
                    Status = TDSAM_READY;
                    return (1);
                }
                Assign_Target(TARGET_NONE);
                Status = TDSAM_LOCKING;
                return (TICKS_PER_SECOND);
            } else {
                if (!PrimaryFacing.Is_Rotating()) {
                    DirType facing = Direction(TarCom);
                    if (PrimaryFacing.Difference(facing)) {
                        PrimaryFacing.Set_Desired(facing);
                    } else {
                        Status = TDSAM_FIRING;
                    }
                }
            }
            return (1);

        case TDSAM_FIRING:
            if (!TF_SAM_Air_Target(TarCom)) {
                if (TDSAM_Try_Reacquire()) {
                    Status = TDSAM_READY;
                    return (1);
                }
                Assign_Target(TARGET_NONE);
                Status = TDSAM_LOCKING;
            } else {
                FireErrorType error = Can_Fire(TarCom, 0);
                if (error == FIRE_ILLEGAL || error == FIRE_CANT || error == FIRE_RANGE) {
                    Assign_Target(TARGET_NONE);
                    Status = TDSAM_LOCKING;
                } else {
                    if (error == FIRE_FACING) {
                        Status = TDSAM_READY;
                    } else {
                        if (error == FIRE_OK) {
                            Fire_At(TarCom, 0);
                            Status = TDSAM_READY2;
                            return (1);
                        }
                    }
                }
            }
            return (1);

        case TDSAM_READY2:
            if (!TF_SAM_Air_Target(TarCom)) {
                if (TDSAM_Try_Reacquire()) {
                    Status = TDSAM_READY2;
                    return (1);
                }
                Assign_Target(TARGET_NONE);
                Status = TDSAM_LOCKING;
                return (TICKS_PER_SECOND);
            } else {
                if (!PrimaryFacing.Is_Rotating()) {
                    DirType facing = Direction(TarCom);
                    if (PrimaryFacing.Difference(facing)) {
                        PrimaryFacing.Set_Desired(facing);
                    } else {
                        Status = TDSAM_FIRING2;
                    }
                }
            }
            return (1);

        case TDSAM_FIRING2:
            if (!TF_SAM_Air_Target(TarCom)) {
                if (TDSAM_Try_Reacquire()) {
                    Status = TDSAM_READY2;
                    return (1);
                }
                Assign_Target(TARGET_NONE);
                Status = TDSAM_LOCKING;
            } else {
                FireErrorType error = Can_Fire(TarCom, 0);
                if (error == FIRE_ILLEGAL || error == FIRE_CANT || error == FIRE_RANGE) {
                    Assign_Target(TARGET_NONE);
                    Status = TDSAM_LOCKING;
                } else {
                    if (error == FIRE_FACING) {
                        Status = TDSAM_READY2;
                    } else {
                        if (error == FIRE_OK) {
                            Fire_At(TarCom, 0);
                            Status = TDSAM_READY;
                            return (1);
                        }
                    }
                }
            }
            return (1);

        case TDSAM_LOCKING:
            if (!PrimaryFacing.Is_Rotating()) {
                if (PrimaryFacing == DIR_N) {
                    Set_Rate(2);
                    Set_Stage(48);
                    Status = TDSAM_LOWERING;
                } else {
                    PrimaryFacing.Set_Desired(DIR_N);
                }
            }
            return (1);

        case TDSAM_LOWERING:
            if (Fetch_Stage() >= 63) {
                Set_Rate(0);
                Set_Stage(0);
                Status = TDSAM_UNDERGROUND;
                return (TICKS_PER_SECOND);
            } else {
                if (Fetch_Rate() == 0) {
                    Set_Rate(2);
                }
            }
            return (1);

        default:
            break;
        }
        return (MissionControl[Mission].AA_Delay() + Random_Pick(0, 2));
    }

    if (!Target_Legal(TarCom)) {
        Assign_Target(TARGET_NONE);
        Assign_Mission(MISSION_GUARD);
        Commence();
        return (1);
    }

    int primary = What_Weapon_Should_I_Use(TarCom);
    IsReadyToCommence = true;
    switch (Can_Fire(TarCom, primary)) {
    case FIRE_ILLEGAL:
    case FIRE_CANT:
    case FIRE_RANGE:
    case FIRE_AMMO:
        Assign_Target(TARGET_NONE);
        Assign_Mission(MISSION_GUARD);
        Commence();
        break;

    case FIRE_FACING:
        PrimaryFacing.Set_Desired(Direction(TarCom));
        return (2);

    case FIRE_REARM:
        PrimaryFacing.Set_Desired(Direction(TarCom));
        return (Arm);

    case FIRE_BUSY:
        return (1);

    case FIRE_CLOAKED:
        Do_Uncloak();
        break;

    case FIRE_OK:
        // TF: a Limpet Mine's shot is the drone leaping onto the vehicle, which spends the mine. A vehicle already
        // carrying this house's drone gets no shot, as in TS; the mine drops it and waits for another.
        if (*this == STRUCT_TSDLIMP) {
            if (TF_Limpet_Attach(this, primary)) {
                delete this;
            } else {
                Assign_Target(TARGET_NONE);
            }
            return (1);
        }
        Fire_At(TarCom, primary);
        return (1);

    default:
        break;
    }
    PrimaryFacing.Set_Desired(Direction(TarCom));
    return (1);
    //	return(MissionControl[Mission].Normal_Delay() + Random_Pick(0, 2));
}

/***********************************************************************************************
 * BuildingClass::Mission_Harvest -- Handles refinery unloading harvesters.                    *
 *                                                                                             *
 *    This state machine handles the refinery when it unloads the harvester.                   *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of game frames to delay before calling this routine        *
 *          again.                                                                             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingClass::Mission_Harvest(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    // TF: the TD refinery runs TD's harvest cycle, which animates the refinery and exits the harvester.
    if (*this == STRUCT_TDPROC) {
        return Mission_Harvest_TD();
    }

    enum
    {
        INITIAL,        // Dock the Tiberium cannister.
        WAIT_FOR_DOCK,  // Waiting for docking to complete.
        MIDDLE,         // Offload "bails" of tiberium.
        WAIT_FOR_UNDOCK // Waiting for undocking to complete.
    };
    switch (Status) {
    case INITIAL:
        Status = WAIT_FOR_DOCK;
        break;

    case WAIT_FOR_DOCK:
        if (IsReadyToCommence) {
            IsReadyToCommence = false;
            Status = MIDDLE;
        }
        break;

    case MIDDLE:
        if (IsReadyToCommence) {
            IsReadyToCommence = false;

            /*
            **	Force any bib squatters to scatter.
            */
            Map[Adjacent_Cell(Coord_Cell(Center_Coord()), DIR_S)].Incoming(0, true, true);

            FootClass* techno = Attached_Object();
            if (techno) {
                // TF: HARV_DOCK_BAILS_PER_CYCLE bails a cycle, the same at every refinery so the economies match.
                for (int b = 0; b < HARV_DOCK_BAILS_PER_CYCLE && techno->Tiberium_Load() > 0; b++) {
                    int bail = techno->Offload_Tiberium_Bail();
                    if (bail) {
                        House->Harvested(bail);
                    }
                }
                if (techno->Tiberium_Load() > 0) {
                    return (1);
                }
            }
            Status = WAIT_FOR_UNDOCK;
        }
        break;

    case WAIT_FOR_UNDOCK:
        if (IsReadyToCommence) {

            /*
            **	Detach harvester and go back into idle state.
            */
            Assign_Mission(MISSION_GUARD);
        }
        break;

    default:
        break;
    }
    return (1);
}

// TD's refinery dock cycle: ACTIVE while the harvester docks, AUX1 while its bails offload, AUX2 at undock,
// then Exit_Object on the harvester. RA's Mission_Harvest neither animates the refinery nor exits it.
int BuildingClass::Mission_Harvest_TD(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    enum
    {
        INITIAL,         // Dock the Tiberium canister.
        WAIT_FOR_DOCK,   // Waiting for docking to complete.
        MIDDLE,          // Offload "bails" of tiberium.
        WAIT_FOR_UNDOCK, // Waiting for undocking to complete.
        EXITING          // Cause the harvester to drive away.
    };
    switch (Status) {
    case INITIAL:
        Begin_Mode(BSTATE_ACTIVE);
        Status = WAIT_FOR_DOCK;
        break;

    case WAIT_FOR_DOCK:
        if (IsReadyToCommence) {
            IsReadyToCommence = false;
            Status = MIDDLE;
            Begin_Mode(BSTATE_AUX1);
        }
        break;

    case MIDDLE:
        if (IsReadyToCommence) {
            IsReadyToCommence = false;

            Map[(*this == STRUCT_TSPROC) ? Coord_Cell(Center_Coord())
                                         : Adjacent_Cell(Coord_Cell(Center_Coord()), DIR_SW)]
                .Incoming(0, true, true);

            FootClass* techno = Attached_Object();
            if (techno) {
                for (int b = 0; b < HARV_DOCK_BAILS_PER_CYCLE && techno->Tiberium_Load() > 0; b++) {
                    int bail = techno->Offload_Tiberium_Bail();
                    if (bail) {
                        House->Harvested(bail);
                    }
                }
                // Keep the explicit > 0: a bare Tiberium_Load() rounds the load fraction to 0 with bails still aboard
                // (docs/td-port-playbook.md).
                if (techno->Tiberium_Load() > 0) {
                    return (1);
                }
            }
            Begin_Mode(BSTATE_AUX2);
            Status = WAIT_FOR_UNDOCK;
        }
        break;

    case WAIT_FOR_UNDOCK:
        if (IsReadyToCommence) {
            Exit_Object(Detach_Object());
            Assign_Mission(MISSION_GUARD);
        }
        break;
    }
    return (1);
}

/***********************************************************************************************
 * BuildingClass::Mission_Repair -- Handles the repair (active) state for building.            *
 *                                                                                             *
 *    This state machine is used when the building is active in some sort of repair or         *
 *    construction mode. The construction yard will animate. The repair facility will repair   *
 *    anything that it docked on it.                                                           *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of game frames to delay before calling this routine again. *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *   06/25/1995 JLB : Handles repair facility                                                  *
 *   07/29/1995 JLB : Repair rate is controlled by power rating.                               *
 *=============================================================================================*/
// How far a repair customer is from where it stops: the building's centre, or at the TS Service Depot the
// nearer of the centre and the pad's seat (Docking_Coord).
int BuildingClass::TF_Depot_Reach(TechnoClass const* customer) const
{
    int reach = Distance(customer);
    if (*this == STRUCT_TSDEPT) {
        int seat = ::Distance(TF_Depot_Seat(customer), customer->Center_Coord());
        if (seat < reach) {
            reach = seat;
        }
    }
    return (reach);
}

// Where a customer stops on the TS Service Depot's pad: the seat, a Titan lifted so its feet stand on the
// pad's centre.
COORDINATE BuildingClass::TF_Depot_Seat(TechnoClass const* customer) const
{
    COORDINATE seat = Docking_Coord();
    if (customer != NULL && customer->What_Am_I() == RTTI_UNIT
        && ((UnitClass const*)customer)->Class->Type == UNIT_TSTITN) {
        seat = Coord_Move(seat, DIR_N, TS_DEPOT_WALKER_LIFT_LEP);
    }
    return (seat);
}

/***********************************************************************************************
 * BuildingClass::TF_Depot_Is_Gantry -- Is this one of the TS Service Depot's gantry cells?    *
 *                                                                                             *
 *    The gantry stands down the plot's west column, in its back two rows; no vehicle drives   *
 *    through it.                                                                              *
 *=============================================================================================*/
bool BuildingClass::TF_Depot_Is_Gantry(CELL cell) const
{
    CELL origin = Coord_Cell(Coord);
    int dx = Cell_X(cell) - Cell_X(origin);
    int dy = Cell_Y(cell) - Cell_Y(origin);
    return (dx == 0 && dy >= 0 && dy < 2);
}

int BuildingClass::Mission_Repair(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (Class->Is_Construction_Yard()) {
        enum
        {
            INITIAL,
            DURING
        };
        switch (Status) {
        case INITIAL:
            Begin_Mode(BSTATE_ACTIVE);
            Status = DURING;
            break;

        case DURING:
            if (!In_Radio_Contact()) {
                Assign_Mission(MISSION_GUARD);
            }
            break;

        default:
            break;
        }
        return (1);
    }

    if (*this == STRUCT_REPAIR || *this == STRUCT_TDFIX || *this == STRUCT_TSDEPT) {
        enum
        {
            INITIAL,
            IDLE,
            DURING
        };
        switch (Status) {
        case INITIAL: {
            if (!In_Radio_Contact()) {
                Begin_Mode(BSTATE_IDLE);
                Assign_Mission(MISSION_GUARD);
                return (1);
            }
            IsReadyToCommence = false;
            int distance = 0x10;
            TechnoClass* tech = Contact_With_Whom();

            /*
            ** BG: If the unit to repair is an aircraft, and the aircraft is
            ** fixed-wing, and it's landed, be much more liberal with the
            ** distance check.  Fixed-wing aircraft are very inaccurate with
            ** their landings.
            */
            if (tech->What_Am_I() == RTTI_AIRCRAFT) {
                if (((AircraftClass*)tech)->Class->IsFixedWing
                    && ((AircraftClass*)tech)->In_Which_Layer() == LAYER_GROUND) {
                    distance = 0x80;
                }
            }
            int reach = TF_Depot_Reach(tech);
            if (Transmit_Message(RADIO_NEED_TO_MOVE) == RADIO_ROGER && reach < distance) {
                Status = IDLE;
                return (TICKS_PER_SECOND / 4);
            }
            break;
        }

        case IDLE:
            if (!In_Radio_Contact()) {
                Assign_Mission(MISSION_GUARD);
                return (1);
            }

            if (Transmit_Message(RADIO_NEED_TO_MOVE) == RADIO_ROGER) {
                TechnoClass* radio = Contact_With_Whom();

                if (((radio->Health_Ratio() < Rule.ConditionGreen)
                     || (radio->What_Am_I() == RTTI_UNIT && *(UnitClass*)radio == UNIT_MINELAYER))
                    && Transmit_Message(RADIO_REPAIR) == RADIO_ROGER) {

                    /*
                    **	If the object over the repair bay is marked as useless, then
                    **	sell it back to get some money.
                    */
                    if (radio->IsUseless) {
                        if (!radio->House->IsHuman) {
                            radio->Sell_Back(1);
                        }
                        Status = INITIAL;
                        IsReadyToCommence = true;
                    } else {

                        //
                        // MBL 04.27.2020: Legacy VOX_REPAIRING seems to be never called in TD, but only in RA.
                        // It is currently supported as a client GUI event when standard repairing begins, with
                        // "REPAIR1" on both TD and RA
                        //
                        // This repairing is in reference to the repair bay
                        // There is a newer bug (https://jaas.ea.com/browse/TDRA-6224) reporting that it is heard in
                        // multiplayer by other players, from this call, so modifiying the original call here:
                        //
                        // if (IsOwnedByPlayer) Speak(VOX_REPAIRING);
                        if (IsOwnedByPlayer)
                            Speak(VOX_REPAIRING, House);

                        Status = DURING;
                        Begin_Mode(BSTATE_ACTIVE);
                        IsReadyToCommence = false;
                    }
                } else {
                    //						Transmit_Message(RADIO_RUN_AWAY);
                    ///*BG*/					if(radio->Health_Ratio() >= Rule.ConditionGreen) {
                    //								Transmit_Message(RADIO_RUN_AWAY);
                    //							}
                }
            }
            break;

        case DURING:
            if (!In_Radio_Contact()) {
                Begin_Mode(BSTATE_IDLE);
                Status = IDLE;
                return (1);
            }

            /*
            **	Check to see if the repair light blink has completed and the attached
            **	unit is not doing something else. If these conditions are favorable,
            **	the repair can proceed another step.
            */
            if (IsReadyToCommence && Transmit_Message(RADIO_NEED_TO_MOVE) == RADIO_ROGER) {
                IsReadyToCommence = false;

                /*
                **	Tell the attached unit to repair one step. It will respond with how
                **	it fared.
                */
                switch (Transmit_Message(RADIO_REPAIR)) {

                /*
                **	The repair step proceeded smoothly. Proceed normally with the
                **	repair process.
                */
                case RADIO_ROGER:
                    break;

                /*
                **	The repair operation was aborted because of some reason. Presume
                **	that the reason is because of low cash.
                */
                case RADIO_CANT:
                    if (IsOwnedByPlayer)
                        Speak(VOX_NO_CASH);
                    Begin_Mode(BSTATE_IDLE);
                    Status = IDLE;
                    break;

                /*
                **	The repair step resulted in a completely repaired unit.
                */
                // TF: a repaired unit heads for the rally point or clears off, and the radio hangs up so it can't
                // re-dock. Ground units are ordered directly, as RADIO_MOVE_HERE ignores a unit sleeping on the pad.
                case RADIO_ALL_DONE: {
                    TechnoClass* customer = Contact_With_Whom();
                    bool sent = false;
                    if (customer != NULL) {
                        if (customer->What_Am_I() == RTTI_AIRCRAFT) {
                            sent = Rally_Unit(*customer);
                        } else if (Can_Have_Rally_Point() && Target_Legal(RallyPoint)) {
                            TARGET rallyTarget = Target_For_Rally_Point(customer->Techno_Type_Class()->Speed);
                            if (Target_Legal(rallyTarget) && customer->As_Target() != rallyTarget) {
                                customer->Assign_Target(TARGET_NONE);
                                customer->Assign_Destination(rallyTarget);
                                customer->Assign_Mission(MISSION_MOVE);
                                sent = true;
                            }
                        }
                    }
                    if (!sent) {
                        Transmit_Message(RADIO_RUN_AWAY);
                    }
                    Transmit_Message(RADIO_OVER_OUT);
                }

                    // MBL 04.27.2020: Make only audible to the correct player
                    // if (IsOwnedByPlayer) Speak(VOX_UNIT_REPAIRED);
                    if (IsOwnedByPlayer)
                        Speak(VOX_UNIT_REPAIRED, House);

                    Begin_Mode(BSTATE_IDLE);
                    Status = IDLE;
                    break;

                /*
                **	The repair step could not be completed because this unit is already
                **	at full strength.
                */
                case RADIO_NEGATIVE:
                default:
                    //							Transmit_Message(RADIO_RUN_AWAY);
                    Begin_Mode(BSTATE_IDLE);
                    Status = IDLE;
                    break;
                }
            }
            return (1);

        default:
            break;
        }
        return (MissionControl[Mission].Normal_Delay());
    }

    if (Class->Is_Helipad() || *this == STRUCT_AIRSTRIP || *this == STRUCT_TDGAFLD) {
        enum
        {
            INITIAL,
            DURING
        };
        switch (Status) {
        case INITIAL:
            if (Transmit_Message(RADIO_NEED_TO_MOVE) == RADIO_ROGER
                && Transmit_Message(RADIO_PREPARED) == RADIO_NEGATIVE) {
                Begin_Mode(BSTATE_ACTIVE);
                Contact_With_Whom()->Assign_Mission(MISSION_SLEEP);
                Status = DURING;
                return (1);
            }
            Assign_Mission(MISSION_GUARD);
            break;

        case DURING:
            if (IsReadyToCommence) {
                if (!In_Radio_Contact() || Transmit_Message(RADIO_NEED_TO_MOVE) == RADIO_NEGATIVE) {
                    Assign_Mission(MISSION_GUARD);
                    return (1);
                }

                if (Transmit_Message(RADIO_PREPARED) == RADIO_ROGER) {
                    Contact_With_Whom()->Assign_Mission(MISSION_GUARD);
                    Assign_Mission(MISSION_GUARD);
                    return (1);
                }

                if (Transmit_Message(RADIO_RELOAD) != RADIO_ROGER) {
                    Assign_Mission(MISSION_GUARD);
                    Contact_With_Whom()->Assign_Mission(MISSION_GUARD);
                    return (1);
                } else {
                    fixed pfrac = Saturate(House->Power_Fraction(), 1);
                    if (pfrac < fixed::_1_2)
                        pfrac = fixed::_1_2;
                    int time = Inverse(pfrac) * Rule.ReloadRate * TICKS_PER_MINUTE;
                    //						int time = Bound((int)(TICKS_PER_SECOND * Saturate(House->Power_Fraction(), 1)), 0,
                    //TICKS_PER_SECOND); 						time = (TICKS_PER_SECOND*3) - time;
                    IsReadyToCommence = false;
                    return (time);
                }
            }
            break;

        default:
            break;
        }
        return (3);
    }
    return (TICKS_PER_SECOND);
}

/***********************************************************************************************
 * BuildingClass::Mission_Missile -- State machine for nuclear missile launch.                 *
 *                                                                                             *
 *    This handles the Temple of Nod launching its nuclear missile.                            *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of frames to delay before calling this routine again.      *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/04/1995 JLB : Commented.                                                               *
 *=============================================================================================*/
int BuildingClass::Mission_Missile(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    // TF: the EMP Cannon (OpenTS Mission_Missile) turns to the target, charges its pulse ball at the barrel
    // for 32 ticks, then lobs it at House->TFEMPDest.
    if (*this == STRUCT_TSPULS) {
        enum
        {
            AIM,
            CHARGE,
            DONE_FIRE
        };
        CELL dest = House->TFEMPDest;
        DirType aim = ::Direction(Center_Coord(), Cell_Coord(dest));
        short const* tip = _tspuls_muzzle[UnitClass::BodyShape[Dir_To_32(PrimaryFacing.Current())]];
        COORDINATE centre = Center_Coord();
        COORDINATE muzzle = XY_Coord((int)Coord_X(centre) + tip[0], (int)Coord_Y(centre) + tip[1]);

        switch (Status) {
        case AIM:
            if (PrimaryFacing.Current() != aim || PrimaryFacing.Is_Rotating()) {
                PrimaryFacing.Set_Desired(aim);
                return (1);
            }
            new AnimClass(ANIM_TS_PULSBALL, muzzle);
            Status = CHARGE;
            return (32);

        case CHARGE: {
            BulletClass* ball = new BulletClass(BULLET_TSPULSBALL, ::As_Target(dest), this, 1, WARHEAD_NONE, MPH_ROCKET);
            if (ball != NULL) {
                if (ball->Unlimbo(muzzle, aim)) {
                    Sound_Effect(VOC_TS_PLSECAN2, muzzle);
                } else {
                    delete ball;
                }
            }
            Status = DONE_FIRE;
            return (1);
        }

        default:
            Assign_Mission(MISSION_GUARD);
            return (1);
        }
    }

    // TF: the Temple of Nod's launch: one ACTIVE animation opens the roof and raises the missile, then after a
    // pause BULLET_NUKE_DOWN falls on House->NukeDest, with no source so the Temple can hit itself.
    if (*this == STRUCT_TDTMPL) {
        enum
        {
            INITIAL,
            ANIM_PLAYING,
            LAUNCH_UP,
            DROPPING,
            DONE_LAUNCH
        };

        switch (Status) {
        case INITIAL:
            IsReadyToCommence = false;
            Begin_Mode(BSTATE_ACTIVE);
            Status = ANIM_PLAYING;
            return (1);

        case ANIM_PLAYING:
            if (IsReadyToCommence) {
                Status = LAUNCH_UP;
            }
            return (1);

        case LAUNCH_UP: {
            CELL center = Coord_Cell(Center_Coord());
            CELL cell_up = XY_Cell(Cell_X(center), 1);
            BulletClass* up = new BulletClass(
                BULLET_NUKE_UP, ::As_Target(cell_up), this, 1, WARHEAD_NONE, MPH_VERY_FAST);
            if (up) {
                COORDINATE launch = Coord_Move(Center_Coord(), DIR_N, 0xA0);
                if (!up->Unlimbo(launch, DIR_N)) {
                    delete up;
                }
            }
            if (House == PlayerPtr) {
                Speak(VOX_TD_NUKE_LAUNCHED);
            }
            Status = DROPPING;
            return (4 * TICKS_PER_SECOND);
        }

        case DROPPING: {
            BulletClass* down = new BulletClass(
                BULLET_NUKE_DOWN, ::As_Target(House->NukeDest), NULL, 200, WARHEAD_NUKE, MPH_VERY_FAST);
            if (down) {
                int celly = Cell_Y(House->NukeDest);
                celly -= 64;
                if (celly < 1)
                    celly = 1;
                COORDINATE start = Cell_Coord(XY_Cell(Cell_X(House->NukeDest), celly));
                if (!down->Unlimbo(start, DIR_S)) {
                    delete down;
                }
            }
            Status = DONE_LAUNCH;
            return (4 * TICKS_PER_SECOND);
        }

        case DONE_LAUNCH:
            Begin_Mode(BSTATE_IDLE);
            Assign_Mission(MISSION_GUARD);
            return (1);
        }
    }

    // GDI's Advanced Comm (TDEYE) launches the GPS satellite exactly as the Allied Tech Center
    // (ADVANCED_TECH) does -- same door/launch/deploy state machine and BULLET_GPS_SATELLITE.
    if (*this == STRUCT_ADVANCED_TECH || *this == STRUCT_TDEYE) {
        enum
        {
            DOOR_OPENING,
            LAUNCH_UP,
            SATELLITE_DEPLOY,
            DONE_LAUNCH
        };

        switch (Status) {

        /*
        ** The initial case is responsible for starting the door
        ** opening on the building, the missile rising, and smoke broiling.
        */
        case DOOR_OPENING: {
#ifdef FIXIT_VERSION_3
            COORDINATE door = Coord_Move(Center_Coord(), (DirType)0xC0, 0x30);
            AnimClass* sput = new AnimClass(ANIM_SPUTDOOR, door);
            if (sput) {
                IsReadyToCommence = false;
                Status = LAUNCH_UP;
                AnimToTrack = sput->As_Target();
            }
#else
            IsReadyToCommence = false;
            COORDINATE door = Coord_Move(Center_Coord(), (DirType)0xC0, 0x30);
            AnimClass* sput = new AnimClass(ANIM_SPUTDOOR, door);
            Status = LAUNCH_UP;
            AnimToTrack = sput->As_Target();
            return (1);
#endif
        }

        /*
        ** Once the smoke has been going for a little while this
        ** actually handles launching the missile into the air.
        */
        case LAUNCH_UP: {
            AnimClass* sput = As_Animation(AnimToTrack);
            if (sput) {
                if (sput->Fetch_Stage() >= 19) {
                    CELL center = Coord_Cell(Center_Coord());
                    CELL cell = XY_Cell(Cell_X(center), 1);
                    TARGET targ = ::As_Target(cell);

                    BulletClass* bullet =
                        new BulletClass(BULLET_GPS_SATELLITE, targ, this, 200, WARHEAD_FIRE, MPH_ROCKET);
                    if (bullet) {
                        COORDINATE launch = Coord_Move(Center_Coord(), (DirType)0xC0, 0x30);
                        if (!bullet->Unlimbo(launch, DIR_N)) {
                            delete bullet;
                            bullet = NULL;
                        }
                    }

                    if (bullet) {
                        // TF: DONE_LAUNCH and the commence gate hand over to GUARD at once; while the switch waits,
                        // LAUNCH_UP would launch another satellite every frame the door animation holds.
                        Status = DONE_LAUNCH;
                        IsReadyToCommence = true;
                        Assign_Mission(MISSION_GUARD);
                    }
                }
            }
        }
            return (1);

        case DONE_LAUNCH:
            // Satellite already away; wait to be switched to MISSION_GUARD without re-launching.
            return (1);
        }
    }

    if (*this == STRUCT_MSLO) {
        enum
        {
            INITIAL,
            DOOR_OPENING,
            LAUNCH_UP,
            DROPPING_NUKE,
            LAUNCH_DOWN,
            DONE_LAUNCH
        };

        switch (Status) {

        /*
        ** The initial case is responsible for starting the door
        ** opening on the building.
        */
        case INITIAL:
            IsReadyToCommence = false;
            Begin_Mode(BSTATE_ACTIVE); // open the door
            Status = DOOR_OPENING;
            return (1);

        /*
        ** This polls for the case when the door is actually open and
        ** then kicks off the missile smoke.
        */
        case DOOR_OPENING:
            if (IsReadyToCommence) {
                Begin_Mode(BSTATE_AUX1); // hold the door open
                Status = LAUNCH_UP;
                return (14);
            }
            return (1);

        /*
        ** Once the smoke has been going for a little while this
        ** actually handles launching the missile into the air.
        */
        // TF: the falling missile is spawned 4 seconds on, in DROPPING_NUKE; spawned together, both missiles show
        // at once when the target is near the map's top edge.
        case LAUNCH_UP: {
            CELL center = Coord_Cell(Center_Coord());
            CELL cell = XY_Cell(Cell_X(center), 1);
            TARGET targ = ::As_Target(cell);
            BulletClass* bullet = new BulletClass(BULLET_NUKE_UP, targ, this, 200, WARHEAD_HE, MPH_VERY_FAST);
            if (bullet) {
                COORDINATE launch = Coord_Move(Center_Coord(), (DirType)28, 0xA0);
                if (!bullet->Unlimbo(launch, DIR_N)) {
                    delete bullet;
                    bullet = NULL;
                }
            }

            if (bullet) {
                Speak(VOX_ABOMB_LAUNCH);
                /*
                ** Hack: If it's the artificial nukes, don't let the bullets come down (as
                ** they're the only ones that blow up).  We know it's artificial if you're
                ** at tech level 10 or below, because you can't build the nuclear silo until
                ** tech level 15 or so.
                */
                if (House->Control.TechLevel <= 10) {
                    Status = LAUNCH_DOWN;
                    return (6);
                }
                Status = DROPPING_NUKE;
                return (4 * TICKS_PER_SECOND);
            }
        }
            return (1);

        /*
        ** Now that the rising missile has cleared the screen, spawn
        ** the descending missile over the target.
        */
        case DROPPING_NUKE: {
            BulletClass* bullet = new BulletClass(
                BULLET_NUKE_DOWN, ::As_Target(House->NukeDest), this, 200, WARHEAD_NUKE, MPH_VERY_FAST);
            if (bullet) {
                int celly = Cell_Y(House->NukeDest);
                celly -= 64;
                if (celly < 1)
                    celly = 1;
                COORDINATE start = Cell_Coord(XY_Cell(Cell_X(House->NukeDest), celly));
                if (!bullet->Unlimbo(start, DIR_S)) {
                    delete bullet;
                }
            }
            Status = LAUNCH_DOWN;
            return (4 * TICKS_PER_SECOND);
        }

        /*
        ** Once the missile is in the air, this handles waiting for
        ** the missile to be off the screen and then launching one down
        ** over the target.
        */
        case LAUNCH_DOWN: {
            Begin_Mode(BSTATE_AUX2); // start the door closing

#ifdef OBSOLETE
            /*
            ** Hack: If it's the artificial nukes, don't let the bullets come down (as
            ** they're the only ones that blow up).  We know it's artificial if you're
            ** at tech level 10 or below, because you can't build the nuclear silo until
            ** tech level 15 or so.
            */
            if (House->Control.TechLevel <= 10) {
                Status = DONE_LAUNCH;
                return (6);
            }
            BulletClass* bullet =
                new BulletClass(BULLET_NUKE_DOWN, ::As_Target(House->NukeDest), this, 200, WARHEAD_NUKE, MPH_VERY_FAST);
            if (bullet) {
                int celly = Cell_Y(House->NukeDest);
                celly -= 15;
                if (celly < 1)
                    celly = 1;
                COORDINATE start = Cell_Coord(XY_Cell(Cell_X(House->NukeDest), celly));
                if (!bullet->Unlimbo(start, DIR_S)) {
                    delete bullet;
                }
            }
            if (bullet) {
#endif
                Status = DONE_LAUNCH;
                return (6);
            }
#ifdef OBSOLETE
        }
            return (1);
#endif

        /*
        ** Once the missile is done launching this handles allowing
        ** the building to sit there with its door closed.
        */
        case DONE_LAUNCH:
            Begin_Mode(BSTATE_IDLE); // keep the door closed.
            Assign_Mission(MISSION_GUARD);
            return (60);
        }
    }
    return (MissionControl[Mission].Normal_Delay());
}

/***********************************************************************************************
 * BuildingClass::Revealed -- Reveals the building to the specified house.                     *
 *                                                                                             *
 *    This routine will reveal the building to the specified house. It will handle updating    *
 *    the sidebar for player owned buildings. A player owned building that hasn't been         *
 *    revealed, is in a state of pseudo-limbo. It cannot be used for any of its special        *
 *    abilities even though it exists on the map for all other purposes.                       *
 *                                                                                             *
 * INPUT:   house -- The house that this building is being revealed to.                        *
 *                                                                                             *
 * OUTPUT:  Was this building revealed by this procedure?                                      *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool BuildingClass::Revealed(HouseClass* house)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (TechnoClass::Revealed(house)) {

        if (!ScenarioInit) {
            House->JustBuiltStructure = Class->Type;
            House->IsBuiltSomething = true;
        }
        House->IsRecalcNeeded = true;

        /*
        **	Perform any grand opening here so that in the scenarios where a player
        **	owned house is not yet revealed, it won't be reflected in the sidebar
        **	selection icons.
        */
        if (!In_Radio_Contact() && House->IsHuman && Mission != MISSION_CONSTRUCTION) {
            Grand_Opening();
        } else {
            if (!In_Radio_Contact() && !House->IsHuman && house == House && Mission != MISSION_CONSTRUCTION) {
                Grand_Opening();
            }
        }

        return (true);
    }
    return (false);
}

/***********************************************************************************************
 * BuildingClass::Enter_Idle_Mode -- The building will enter its idle mode.                    *
 *                                                                                             *
 *    This routine is called when the exact mode of the building isn't known. By examining     *
 *    the building's condition, this routine will assign an appropriate mission.               *
 *                                                                                             *
 * INPUT:   initial  -- This this being called during scenario init?                           *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/25/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Enter_Idle_Mode(bool initial)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    /*
    **	Assign an appropriate mission for the building. If the ScenarioInit flag is true, then
    **	this must be an initial building. Start such buildings in idle state. For other buildings
    **	it indicates that it is being placed during game play and thus it must start in
    **	the "construction" mission.
    */
    MissionType mission = MISSION_GUARD;

    if (!initial || ScenarioInit || Debug_Map || TFPlugInstallInProgress) {
        // TF: a tower plug skips the build-up, where a building takes its starting facing, so it takes it here.
        if (TFPlugInstallInProgress) {
            PrimaryFacing = Class->StartFace;
        }
        TFPlugInstallInProgress = false;
        Begin_Mode(BSTATE_IDLE);
        mission = MISSION_GUARD;
    } else {
        Begin_Mode(BSTATE_CONSTRUCTION);
        mission = MISSION_CONSTRUCTION;
    }
    Assign_Mission(mission);
}

/***********************************************************************************************
 * BuildingClass::Pip_Count -- Determines "full" pips to display for building.                 *
 *                                                                                             *
 *    This routine will determine the number of pips that should be filled in when rendering   *
 *    the building.                                                                            *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns the number of pips to display as filled in.                                *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/28/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingClass::Pip_Count(void) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    return (Class->Max_Pips() * House->Tiberium_Fraction());
}

/***********************************************************************************************
 * BuildingClass::Death_Announcement -- Announce the death of this building.                   *
 *                                                                                             *
 *    This routine is called when the building is destroyed by "unnatural" means. Typically    *
 *    as a result of combat. If the building is known to the player, then it should be         *
 *    announced.                                                                               *
 *                                                                                             *
 * INPUT:   source   -- The object most directly responsible for the building's death.         *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/04/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Death_Announcement(TechnoClass const* source) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (source != NULL && House->IsPlayerControl) {
        Speak(VOX_STRUCTURE_DESTROYED);
    }
}

/***********************************************************************************************
 * BuildingClass::Fire_Direction -- Fetches the direction of firing.                           *
 *                                                                                             *
 *    This routine will return with the default direction to use when firing from this         *
 *    building. This is the facing of the turret except for the case of non-turret equipped    *
 *    buildings that have a weapon (e.g., guard tower).                                        *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the default firing direction for this building.                       *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/04/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
DirType BuildingClass::Fire_Direction(void) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (Class->IsTurretEquipped) {
        return (PrimaryFacing.Current());
    }
    return (Direction(TarCom));
}

/***********************************************************************************************
 * BuildingClass::Remap_Table -- Fetches the remap table to use for this building.             *
 *                                                                                             *
 *    Use this routine to fetch the remap table to use.  This override function is needed      *
 *    because the default remap table for techno objects presumes the object is a unit.        *
 *    Buildings aren't units.                                                                  *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the proper remap table to use for this building.                      *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/08/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void const* BuildingClass::Remap_Table(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    return (House->Remap_Table(IsBlushing, Class->Remap));
}

/***********************************************************************************************
 * BuildingClass::Mission_Unload -- Handles the unload mission for a building.                 *
 *                                                                                             *
 *    This is the unload mission for a building. This really only applies to the weapon's      *
 *    factory, since it needs the sophistication of an unload mission due to the door          *
 *    animation.                                                                               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of game frames to delay before calling this routine        *
 *          again.                                                                             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
// Packs a deployed TS building back into its vehicle on the same cell.
static void TF_Pack_Up(BuildingClass* mine)
{
    CELL cell = Coord_Cell(mine->Coord);
    if (*mine == STRUCT_TSDWEAP) {
        cell += MAP_CELL_W + 1; // the hall's middle cell, where the vehicle deployed
    }
    fixed ratio = mine->Health_Ratio();
    TARGET nav = mine->TFPackNav;
    UnitType type = TF_Packs_Into(mine);
    UnitClass* unit = new UnitClass(type, mine->House->Class->House);
    if (unit == NULL) {
        return;
    }
    DirType facing = (type == UNIT_TSLPST)   ? DIR_E
                     : (type == UNIT_TSMWAR) ? DIR_SW
                     : (type == UNIT_TSTTNK) ? DIR_S
                                             : DIR_N;
    mine->Limbo();
    if (unit->Unlimbo(Cell_Coord(cell), facing)) {
        unit->Strength = max(1, (int)(unit->Class->MaxStrength * ratio));
        if (Target_Legal(nav)) {
            unit->Assign_Mission(MISSION_MOVE);
            unit->Assign_Destination(nav);
        } else {
            unit->Assign_Mission(MISSION_GUARD);
        }
        delete mine;
    } else {
        delete unit;
        mine->Unlimbo(Cell_Coord(cell), DIR_N);
    }
}

int BuildingClass::Mission_Unload(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    // TF: a deployed TS building's deploy order runs its build-up backwards, then packs it up. A war factory
    // also unloads the vehicles it builds; those are in radio contact with it, a pack-up order never is.
    if (TF_Packs_Into(this) != UNIT_NONE
        && (!Is_TS_War_Factory() || (!In_Radio_Contact() && (Status == 0 || BState == BSTATE_CONSTRUCTION)))) {
        if (Status == 0) {
            if (*this != STRUCT_TSDLIMP) {
                Sound_Effect(VOC_TS_PLACE_BUILDING_DOWN, Center_Coord());
            }
            Do_Uncloak();
            Begin_Mode(BSTATE_CONSTRUCTION);
            IsReadyToCommence = false;
            Status = 1;
            return (1);
        }
        if (IsReadyToCommence) {
            TF_Pack_Up(this);
        }
        return (1);
    }

    // TF: the TD war factory runs TD's unload cycle (Mission_Unload_TD).
    if (*this == STRUCT_TDWEAP) {
        return Mission_Unload_TD();
    }

    // TF: the TS war factory's unload cycle, over TS_Door_Stages(); the vehicle leaves its bay seat on Rail_To.
    if (Is_TS_War_Factory()) {
        /*
        **	TS's factory cycle (OpenTS Do_MISSION_UNLOAD): open the shutter, keep
        **	the exit cell clear, when the shutter is fully up put the vehicle on a
        **	rail from its mouth seat straight out onto the exit cell, wait until
        **	it has untethered, shut the door, idle.
        */
        CELL cell = Coord_Cell(Coord) + TS_Weap_Exit_Offset(); // the rail ends on this cell's centre
        COORDINATE coord = Cell_Coord(cell);
        CellClass* cellptr = &Map[cell];
        enum
        {
            INITIAL,
            CLEAR_BIB,
            OPEN,
            LEAVE,
            CLOSE
        };
        int const DOOR_STAGES = TS_Door_Stages();
        enum
        {
            DOOR_RATE = 4 // ticks per stage
        };
        UnitClass* unit;
        switch (Status) {
        case INITIAL:
            unit = (UnitClass*)Contact_With_Whom();
            if (unit) {
                unit->Assign_Mission(MISSION_GUARD);
                unit->Commence();
            }
            Open_Door(DOOR_RATE, DOOR_STAGES);
            Status = CLEAR_BIB;
#if TF_DEV_BUILD
            TF_WF_Log(this, "unload: door opening");
#endif
            break;
        case CLEAR_BIB:
            if (cellptr != NULL && cellptr->Cell_Techno()) {
#if TF_DEV_BUILD
                static long tf_held_logged = -1000;
                if (Frame - tf_held_logged >= 30) {
                    tf_held_logged = Frame;
                    TF_WF_Log(this, "unload: doorstep held by %s#%d", cellptr->Cell_Techno()->Class_Of().IniName,
                              cellptr->Cell_Techno()->ID);
                }
#endif
                cellptr->Incoming(0, true, true);
                for (FacingType f = FACING_FIRST; f < FACING_COUNT; f++) {
                    CellClass* cptr = cellptr->Adjacent_Cell(f);
                    if (cptr && cptr->Cell_Building() == NULL) {
                        cptr->Incoming(coord, true, true);
                    }
                }
            } else {
                Status = OPEN;
#if TF_DEV_BUILD
                TF_WF_Log(this, "unload: doorstep clear");
#endif
            }
            break;
        case OPEN:
            if (Is_Door_Open()) {
                unit = (UnitClass*)Contact_With_Whom();
                if (unit) {
                    unit->Assign_Mission(MISSION_MOVE);
                    if (House->IQ >= Rule.IQGuardArea) {
                        unit->Assign_Mission(MISSION_GUARD_AREA);
                        unit->ArchiveTarget = ::As_Target(House->Where_To_Go(unit));
                    }
                    unit->Rail_To(coord, Desired_Facing256(Coord_X(unit->Coord), Coord_Y(unit->Coord), Coord_X(coord), Coord_Y(coord)));
                    // TF: a player's unit walks on from the rail's end, to the rally point or clear of the doorstep,
                    // so the factory can open for the next one. Harvesters harvest instead.
                    if (House->IsHuman && !unit->Class->IsToHarvest) {
                        TARGET onward = (Can_Have_Rally_Point() && Target_Legal(RallyPoint))
                                            ? Target_For_Rally_Point(unit->Class->Speed)
                                            : ::As_Target(Map.Nearby_Location((CELL)(cell + MAP_CELL_W), unit->Class->Speed));
                        if (Target_Legal(onward)) {
                            unit->Assign_Mission(MISSION_MOVE);
                            unit->Assign_Destination(onward);
                        }
                    }
                    Status = LEAVE;
#if TF_DEV_BUILD
                    TF_WF_Log(this, "unload: rail from (%d,%d) to (%d,%d)", Coord_X(unit->Coord), Coord_Y(unit->Coord),
                              Coord_X(coord), Coord_Y(coord));
#endif
                } else {
                    Close_Door(DOOR_RATE, DOOR_STAGES);
                    Status = CLOSE;
#if TF_DEV_BUILD
                    TF_WF_Log(this, "unload: door open with no vehicle, closing");
#endif
                }
            }
            break;
        case LEAVE:
            if (!IsTethered) {
                Close_Door(DOOR_RATE, DOOR_STAGES);
                Status = CLOSE;
#if TF_DEV_BUILD
                TF_WF_Log(this, "unload: untethered, closing");
#endif
            }
            break;
        case CLOSE:
            if (Is_Door_Closed()) {
#if TF_DEV_BUILD
                TF_WF_Log(this, "unload: door shut, idle");
#endif
                Enter_Idle_Mode();
            }
            break;
        default:
            break;
        }
        return (MissionControl[Mission].Normal_Delay() + Random_Pick(0, 2));
    }
    if (*this == STRUCT_WEAP || *this == STRUCT_AWEAP || *this == STRUCT_SWEAP) {
        CELL cell = Coord_Cell(Coord) + Class->ExitList[0];
        COORDINATE coord = Cell_Coord(cell);
        CellClass* cellptr = &Map[cell];
        enum
        {
            INITIAL,
            CLEAR_BIB,
            OPEN,
            LEAVE,
            CLOSE
        };
        enum
        {
            DOOR_STAGES = 5,
            DOOR_RATE = 8
        };
        UnitClass* unit;
        switch (Status) {
        /*
        **	Start the door opening.
        */
        case INITIAL:
            //				if (cellptr->Cell_Techno()) {
            //					cellptr->Incoming(0, true);
            //				}
            unit = (UnitClass*)Contact_With_Whom();
            if (unit) {
                unit->Assign_Mission(MISSION_GUARD);
                unit->Commence();
            }
            Open_Door(DOOR_RATE, DOOR_STAGES);
            Status = CLEAR_BIB;
            break;

        /*
        **	Now that the occupants can peek out the door, they will tell
        **	everyone that could be blocking the way, that they should
        **	scatter away.
        */
        case CLEAR_BIB:
            if (cellptr->Cell_Techno()) {
                cellptr->Incoming(0, true, true);

                /*
                **	Scatter everything around the weapon's factory door.
                */
                for (FacingType f = FACING_FIRST; f < FACING_COUNT; f++) {
                    CellClass* cptr = cellptr->Adjacent_Cell(f);
                    if (cptr && cptr->Cell_Building() == NULL) {
                        cptr->Incoming(coord, true, true);
                    }
                }
            } else {
                Status = OPEN;
            }
            break;

        /*
        **	When the door is finally open and the way is clear, tell the
        **	unit to drive out.
        */
        case OPEN:
            if (Is_Door_Open()) {
                unit = (UnitClass*)Contact_With_Whom();
                if (unit) {
                    unit->Assign_Mission(MISSION_MOVE);

                    if (House->IQ >= Rule.IQGuardArea) {
                        unit->Assign_Mission(MISSION_GUARD_AREA);
                        unit->ArchiveTarget = ::As_Target(House->Where_To_Go(unit));
                    }
                    unit->Force_Track(DriveClass::OUT_OF_WEAPON_FACTORY, coord);
                    unit->Set_Speed(128);
                    Status = LEAVE;
                } else {
                    Close_Door(DOOR_RATE, DOOR_STAGES);
                    Status = CLOSE;
                }
            }
            break;

        /*
        **	Wait until the unit has completely left the building.
        */
        case LEAVE:
            if (!IsTethered) {
                Close_Door(DOOR_RATE, DOOR_STAGES);
                Status = CLOSE;
            } else {

                //					if (In_Radio_Contact() && !((FootClass *)Contact_With_Whom())->IsDriving) {
                //						Transmit_Message(RADIO_OVER_OUT);
                //					}
            }
            break;

        /*
        **	Wait while the door closes.
        */
        case CLOSE:
            if (Is_Door_Closed()) {
                Enter_Idle_Mode();
            }
            break;

        default:
            break;
        }
        return (MissionControl[Mission].Normal_Delay() + Random_Pick(0, 2));
    }

    Assign_Mission(MISSION_GUARD);
    return (1);
}

// TD's war factory unload cycle for STRUCT_TDWEAP: TD's faster door (11 stages at 2 ticks) and its own
// south-west exit track, OUT_OF_WEAPON_FACTORY_TD, so RA's south exit is untouched.
int BuildingClass::Mission_Unload_TD(void)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    COORDINATE coord = Adjacent_Cell(Center_Coord(), FACING_SW);
    CELL cell = Coord_Cell(coord);
    CellClass* cellptr = &Map[cell];
    enum
    {
        INITIAL,
        CLEAR_BIB,
        OPEN,
        LEAVE,
        CLOSE
    };
    UnitClass* unit;
    switch (Status) {
    case INITIAL:
        unit = (UnitClass*)Contact_With_Whom();
        if (unit) {
            unit->Assign_Mission(MISSION_GUARD);
            unit->Commence();
        }
        Open_Door(2, 11);
        Status = CLEAR_BIB;
        break;

    case CLEAR_BIB:
        unit = (UnitClass*)Contact_With_Whom();
        if (cellptr->Cell_Unit() || cellptr->Cell_Infantry()) {
            cellptr->Incoming(0, true, true);

            for (FacingType f = FACING_FIRST; f < FACING_COUNT; f++) {
                CellClass* cptr = cellptr->Adjacent_Cell(f);
                if (!cptr)
                    continue;
                UnitClass* cellunit = cptr->Cell_Unit();
                if ((cellunit && cellunit != unit) || cptr->Cell_Infantry()) {
                    cptr->Incoming(coord, true, true);
                }
            }
        } else {
            Status = OPEN;
        }
        break;

    case OPEN:
        if (Is_Door_Open()) {
            unit = (UnitClass*)Contact_With_Whom();
            if (unit) {
                unit->Assign_Mission(MISSION_MOVE);
                unit->Force_Track(DriveClass::OUT_OF_WEAPON_FACTORY_TD,
                                  Adjacent_Cell(Center_Coord(), FACING_SW));
                unit->Set_Speed(128);
                Status = LEAVE;
            } else {
                Close_Door(2, 11);
                Status = CLOSE;
            }
        }
        break;

    case LEAVE:
        if (!IsTethered) {
            Close_Door(2, 11);
            Status = CLOSE;
        }
        break;

    case CLOSE:
        if (Is_Door_Closed()) {
            Enter_Idle_Mode();
        }
        break;
    }
    return (TICKS_PER_SECOND / 2);
}

/***********************************************************************************************
 * BuildingClass::Power_Output -- Fetches the current power output from this building.         *
 *                                                                                             *
 *    This routine will return the current power output for this building. The power output    *
 *    is adjusted according to the damage level of the building.                               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns the current power output for this building.                                *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingClass::Power_Output(void) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    int power = Class->Power + Upgrade_Power();
    if (power) {
        return (power * fixed(LastStrength, Class->MaxStrength));
    }
    return (0);
}

/*
**	Total Power contributed by installed addon plugs (TS upgrades). Scales with
**	the host's health via Power_Output like the building's own Power.
*/
int BuildingClass::Upgrade_Power(void) const
{
    int power = 0;
    for (int i = 0; i < UpgradeLevel; i++) {
        if (UpgradeTypes[i] != STRUCT_NONE) {
            power += BuildingTypeClass::As_Reference(UpgradeTypes[i]).Power;
        }
    }
    return (power);
}

// Total power Drain of installed addon plugs, applied wherever the host's own drain is (open, limbo, capture).
int BuildingClass::Upgrade_Drain(void) const
{
    int drain = 0;
    for (int i = 0; i < UpgradeLevel; i++) {
        if (UpgradeTypes[i] != STRUCT_NONE) {
            drain += BuildingTypeClass::As_Reference(UpgradeTypes[i]).Drain;
        }
    }
    return (drain);
}

/*
**	Selling a building also refunds the addon plugs installed in it, each at
**	the same sell-back rate as the building itself.
*/
int BuildingClass::Refund_Amount(void) const
{
    int refund = TechnoClass::Refund_Amount();
    if (Class->PowersUpBuilding == STRUCT_TSCTWR) {
        int cost = BuildingTypeClass::As_Reference(STRUCT_TSCTWR).Raw_Cost() * House->CostBias;
        if (House->IsHuman) {
            cost = cost * Rule.RefundPercent;
        }
        refund += cost;
    }
    for (int i = 0; i < UpgradeLevel; i++) {
        if (UpgradeTypes[i] != STRUCT_NONE) {
            int cost = BuildingTypeClass::As_Reference(UpgradeTypes[i]).Raw_Cost() * House->CostBias;
            if (House->IsHuman) {
                cost = cost * Rule.RefundPercent;
            }
            refund += cost;
        }
    }
    return (refund);
}

// Would placing this addon plug install it here? True only for the plug's host type, same owner, a free
// addon slot, and at most one of each superweapon plug (unlike TS: the superweapon is house-level).
bool BuildingClass::Can_Upgrade(BuildingTypeClass const* plug, HouseClass const* house) const
{
    if (plug == NULL || house != House) {
        return (false);
    }
    if (plug->PowersUpBuilding == STRUCT_NONE || plug->PowersUpBuilding != Class->Type) {
        return (false);
    }
    if (plug->Type == STRUCT_TSPION || plug->Type == STRUCT_TSPODS || plug->Type == STRUCT_TSSEEK) {
        for (int i = 0; i < UpgradeLevel; i++) {
            if (UpgradeTypes[i] == plug->Type) {
                return (false);
            }
        }
    }
    return (UpgradeLevel < Class->UpgradesMax);
}

/***********************************************************************************************
 * BuildingClass::Detach -- Handles target removal from the game system.                       *
 *                                                                                             *
 *    This routine is called when the specified target is about to be removed from the game    *
 *    system.                                                                                  *
 *                                                                                             *
 * INPUT:   target   -- The target to be removed from this building's targeting computer.      *
 *                                                                                             *
 *          all      -- Is the target about to be completely eliminated?                       *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Detach(TARGET target, bool all)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    TechnoClass::Detach(target, all);
    if (target == WhomToRepay) {
        WhomToRepay = TARGET_NONE;
    }
    if (target == AnimToTrack) {
        AnimToTrack = TARGET_NONE;
    }
}

/***********************************************************************************************
 * BuildingClass::Crew_Type -- This determines the crew that this object generates.            *
 *                                                                                             *
 *    When selling very cheap buildings (such as the silo), a technician will pop out since    *
 *    generating minigunners would be overkill -- the player could use this loophole to        *
 *    gain an advantage.                                                                       *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns the infantry type that this building will generate as a survivor.          *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   08/05/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
InfantryType BuildingClass::Crew_Type(void) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    // TF: every faction's construction yard gets the RA yard's 25% Engineer chance (uncaptured, human owner).
    if (Class->Is_Construction_Yard() && !IsCaptured && House->IsHuman && Percent_Chance(25)) {
        return (INFANTRY_RENOVATOR);
    }

    switch (Class->Type) {
    case STRUCT_STORAGE:
        if (Percent_Chance(50)) {
            return (INFANTRY_C1);
        } else {
            return (INFANTRY_C7);
        }

    case STRUCT_KENNEL:
        if (Percent_Chance(50)) {
            return (INFANTRY_DOG);
        } else {
            return (INFANTRY_NONE);
        }

    case STRUCT_TENT:
    case STRUCT_BARRACKS:
        return (INFANTRY_E1);

    default:
        break;
    }

    // TF: TD buildings ("TD" IniName prefix) leave TD Minigunners as crew, TS buildings TS riflemen.
    if (Class->IniName[0] == 'T' && Class->IniName[1] == 'D') {
        return (INFANTRY_TDE1);
    }

    if (Class->IniName[0] == 'T' && Class->IniName[1] == 'S') {
        return (INFANTRY_TSE1);
    }
    return (TechnoClass::Crew_Type());
}

/***********************************************************************************************
 * BuildingClass::Detach_All -- Possibly abandons production according to factory type.        *
 *                                                                                             *
 *    When this routine is called, it indicates that the building is about to be destroyed     *
 *    or captured. In such a case any production it may be doing, must be abandoned.           *
 *                                                                                             *
 * INPUT:   all   -- Is the object about the be completely destroyed?                          *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   08/05/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Detach_All(bool all)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    /*
    **	If it is producing something, then it must be abandoned.
    */
    if (Factory) {
        Factory->Abandon();
        delete (FactoryClass*)Factory;
        Factory = 0;
    }

    /*
    ** If the owner HouseClass is building something, and this building can
    ** build that thing, we may be the last building for that house that can
    ** build that thing; if so, abandon production of it.
    */
    if (House) {
        bool bay = (*this == STRUCT_TSDROP);
        FactoryClass* factory = House->Fetch_Factory(Class->ToBuild, bay);

        /*
        **	If a factory was found, then temporarily disable this building and then
        **	determine if any object that is being produced can still be produced. If
        **	not, then the object being produced must be abandoned.
        */
        if (factory) {
            TechnoClass* object = factory->Get_Object();
            IsInLimbo = true;
            if (object && !object->Techno_Type_Class()->Who_Can_Build_Me(true, false, House->Class->House)) {
                House->Abandon_Production(Class->ToBuild, bay);
            }
            IsInLimbo = false;
        }
    }

    TechnoClass::Detach_All(all);
}

/***********************************************************************************************
 * BuildingClass::Flush_For_Placement -- Handles clearing a zone for object placement.         *
 *                                                                                             *
 *    This routine is used to clear the way for placement of the specified object (usually     *
 *    a building). If there are friendly units blocking the placement area, they are told      *
 *    to scatter. Enemy blocking units are attacked.                                           *
 *                                                                                             *
 * INPUT:   techno   -- Pointer to the object that is desired to be placed.                    *
 *                                                                                             *
 *          cell     -- The cell that placement wants to occur at.                             *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   08/06/1995 JLB : Created.                                                                 *
 *   09/27/1995 JLB : Revised to use type class function.                                      *
 *=============================================================================================*/
bool BuildingClass::Flush_For_Placement(TechnoClass* techno, CELL cell)
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (techno) {
        return (((BuildingTypeClass const&)techno->Class_Of()).Flush_For_Placement(cell, House));
    }
    return (false);
}

/***********************************************************************************************
 * BuildingClass::Find_Exit_Cell -- Find a clear location to exit an object from this building *
 *                                                                                             *
 *    This routine is called when the building needs to discharge a unit. It will find a       *
 *    nearby (adjacent) cell that is clear enough for the specified object to enter. Typical   *
 *    use of this routine is when the airfield disgorges its cargo.                            *
 *                                                                                             *
 * INPUT:   techno   -- Pointer to the object that wishes to exit this building.               *
 *                                                                                             *
 * OUTPUT:  Returns with the cell number to use for object placement. If no free location      *
 *          could be found, then zero (0) is returned.                                         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/21/1995 JLB : Created.                                                                 *
 *   02/20/1996 JLB : Added default case for exit cell calculation.                            *
 *=============================================================================================*/
CELL BuildingClass::Find_Exit_Cell(TechnoClass const* techno) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    CELL const* ptr;
    CELL origin = Coord_Cell(Coord);

    ptr = Class->ExitList;
    if (ptr != NULL) {
        while (*ptr != REFRESH_EOL) {
            CELL cell = origin + *ptr++;
            if (Map.In_Radar(cell) && techno->Can_Enter_Cell(cell) == MOVE_OK) {
                return (cell);
            }
        }
    } else {
        int x1, x2;
        int y1, y2;
        CELL cell;

        y1 = -1;
        y2 = Class->Height();
        for (x1 = -1; x1 <= Class->Width(); x1++) {
            cell = origin + x1 + (y1 * MAP_CELL_W);
            if (Map.In_Radar(cell) && techno->Can_Enter_Cell(cell) == MOVE_OK) {
                return (cell);
            }
            cell = origin + x1 + (y2 * MAP_CELL_W);
            if (Map.In_Radar(cell) && techno->Can_Enter_Cell(cell) == MOVE_OK) {
                return (cell);
            }
        }

        x1 = -1;
        x2 = Class->Width();
        for (y1 = -1; y1 <= Class->Height(); y1++) {
            cell = origin + (y1 * MAP_CELL_W) + x1;
            if (Map.In_Radar(cell) && techno->Can_Enter_Cell(cell) == MOVE_OK) {
                return (cell);
            }
            cell = origin + (y1 * MAP_CELL_W) + x2;
            if (Map.In_Radar(cell) && techno->Can_Enter_Cell(cell) == MOVE_OK) {
                return (cell);
            }
        }
    }
    return (0);
}

/***********************************************************************************************
 * BuildingClass::Can_Player_Move -- Can this building be moved?                               *
 *                                                                                             *
 *    This routine answers the question 'can this building be moved?' Typically, only the      *
 *    construction yard can be moved and it does this by undeploying back into a MCV.          *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Can the building move to a new location under player control?                      *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/04/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool BuildingClass::Can_Player_Move(void) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    // TF: a rally-capable factory answers yes, so What_Action(cell) gives ACTION_MOVE and a ground click sets
    // its rally point.
    if (Is_Immobilized()) {
        return (false);
    }
    return Can_Have_Rally_Point()
           || (Class->Is_Construction_Yard() && (Mission == MISSION_GUARD) && Special.IsMCVDeploy);
}

/***********************************************************************************************
 * BuildingClass::Exit_Coord -- Determines location where object will leave it.                *
 *                                                                                             *
 *    This routine will return the coordinate where an object that wishes to leave the         *
 *    building will exit at.                                                                   *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the coordinate that the object should be created at.                  *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   02/20/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
COORDINATE BuildingClass::Exit_Coord(void) const
{
    assert(Buildings.ID(this) == ID);
    assert(IsActive);

    if (Class->ExitCoordinate) {
        return (Coord_Add(Coord, Class->ExitCoordinate));
    }
    return (TechnoClass::Exit_Coord());
}

/***********************************************************************************************
 * BuildingClass::Check_Point -- Fetches the landing checkpoint for the given flight pattern.  *
 *                                                                                             *
 *    Use this routine to coordinate a landing operation. The specified checkpoint is          *
 *    converted into a cell number. The landing aircraft should fly over that cell and then    *
 *    request the next check point.                                                            *
 *                                                                                             *
 * INPUT:   cp    -- The check point to convert to a cell number.                              *
 *                                                                                             *
 * OUTPUT:  Returns with the cell that the aircraft should fly over in order to complete       *
 *          that portion of the landing pattern.                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/06/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
CELL BuildingClass::Check_Point(CheckPointType cp) const
{
    CELL xoffset = 6; // Downwind offset.
    CELL yoffset = 5; // Crosswind offset.
    CELL cell = Coord_Cell(Center_Coord());

    switch (cp) {
    case CHECK_STACK:
        xoffset = 0;
        break;

    case CHECK_CROSSWIND:
        yoffset = 0;
        break;

    case CHECK_DOWNWIND:
    default:
        break;
    }

    if ((Cell_X(cell) - Map.MapCellX) > Map.MapCellWidth / 2) {
        xoffset = -xoffset;
    }

    if ((Cell_Y(cell) - Map.MapCellY) > Map.MapCellHeight / 2) {
        yoffset = -yoffset;
    }

    return (XY_Cell(Cell_X(cell) + xoffset, Cell_Y(cell) + yoffset));
}

/***********************************************************************************************
 * BuildingClass::Update_Radar_Spied - set house's RadarSpied field appropriately.				  *
 *                                                                                             *
 *    This routine is called when a radar facility is captured or destroyed.  It fills in the  *
 *    RadarSpied field of the house based on whether there's a spied-upon radar facility or not*
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  House->RadarSpied field gets set appropriately.												  *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/22/1996 BWG : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Update_Radar_Spied(void)
{
    House->RadarSpied = 0;
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass* obj = Buildings.Ptr(index);
        if (obj && !obj->IsInLimbo && obj->House == House) {
            if (*obj == STRUCT_RADAR || *obj == STRUCT_TDHQ || *obj == STRUCT_TDEYE || *obj == STRUCT_TSRADR) {
                House->RadarSpied |= obj->Spied_By();
            }
        }
    }
    Map.RadarClass::Flag_To_Redraw(true);
}

/***********************************************************************************************
 * BuildingClass::Read_INI -- Reads buildings from INI file.                                   *
 *                                                                                             *
 *    This is the basic scenario initialization of building function. It                       *
 *    is called when reading the scenario startup INI file and it handles                      *
 *    creation of all specified buildings.                                                     *
 *                                                                                             *
 *    INI entry format:                                                                        *
 *      Housename, Typename, Strength, Cell, Facing, Triggername                               *
 *                                                                                             *
 * INPUT:   buffer   -- Pointer to the loaded INI file data.                                   *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/24/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Read_INI(CCINIClass& ini)
{
    BuildingClass* b;   // Working unit pointer.
    HousesType bhouse;  // Building house.
    StructType classid; // Building type.
    CELL cell;          // Cell of building.
    char buf[128];
    char* trigname; // building's trigger's name

    int len = ini.Entry_Count(INI_Name());
    for (int index = 0; index < len; index++) {
        char const* entry = ini.Get_Entry(INI_Name(), index);

        /*
        **	Get a building entry.
        */
        ini.Get_String(INI_Name(), entry, NULL, buf, sizeof(buf));

        /*
        **	1st token: house name.
        */
        bhouse = HouseTypeClass::From_Name(strtok(buf, ","));

        /*
        **	2nd token: building name.
        */
        classid = BuildingTypeClass::From_Name(strtok(NULL, ","));

        if (bhouse != HOUSE_NONE && classid != STRUCT_NONE) {
            int strength;
            DirType facing;

            /*
            **	3rd token: strength.
            */
            strength = atoi(strtok(NULL, ","));

            /*
            **	4th token: cell #.
            */
            cell = atoi(strtok(NULL, ","));

            /*
            **	5th token: facing.
            */
            facing = (DirType)atoi(strtok(NULL, ","));

            /*
            **	6th token: triggername (can be NULL).
            */
            trigname = strtok(NULL, ",");

            bool sellable = false;
            char* token_pointer = strtok(NULL, ",");
            if (token_pointer) {
                sellable = atoi(token_pointer);
            }

            bool rebuild = false;
            token_pointer = strtok(NULL, ",");
            if (token_pointer) {
                rebuild = atoi(token_pointer);
            }

            if (HouseClass::As_Pointer(bhouse) != NULL) {
                // TF: build from the type pointer, as Create_One_Of does. The StructType constructor leaves a scenario
                // building inactive, so Unlimbo fails and it is deleted (docs/td-port-playbook.md).
                b = new BuildingClass(BuildingTypes.Ptr((int)classid), bhouse);
                if (b) {

                    TriggerTypeClass* tp = TriggerTypeClass::From_Name(trigname);
                    if (tp) {
                        TriggerClass* tt = Find_Or_Make(tp);
                        if (tt) {
                            tt->AttachCount++;
                            b->Trigger = tt;
                        }
                    }
                    b->IsAllowedToSell = sellable;
                    b->IsToRebuild = rebuild;
                    b->IsToRepair = rebuild || b->Class->Is_Construction_Yard();

                    if (b->Unlimbo(Cell_Coord(cell), facing)) {
                        strength = min(strength, 0x100);
                        strength = (int)b->Class->MaxStrength * fixed(strength, 256); // Cast to (int). ST - 5/8/2019
                        b->Strength = strength;
                        if (b->Strength > b->Class->MaxStrength - 3)
                            b->Strength = b->Class->MaxStrength;
                        b->IsALemon = false;
                    } else {

                        /*
                        **	If the building could not be unlimboed on the map, then this indicates
                        **	a serious error. Delete the building.
                        */
                        delete b;
                    }
                }
            }
        }
    }
}

/***********************************************************************************************
 * BuildingClass::Write_INI -- Write out the building data to the INI file specified.          *
 *                                                                                             *
 *    This will store the building data (as it relates to scenario initialization) to the      *
 *    INI database specified.                                                                  *
 *                                                                                             *
 * INPUT:   ini   -- Reference to the INI database that the building data will be stored to.   *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/06/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Write_INI(CCINIClass& ini)
{
    /*
    **	First, clear out all existing building data from the ini file.
    */
    ini.Clear(INI_Name());

    /*
    **	Write the data out.
    */
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass* building = Buildings.Ptr(index);
        if (!building->IsInLimbo) {
            char uname[12];
            char buf[127];

            sprintf(uname, "%d", index);
            sprintf(buf,
                    "%s,%s,%d,%u,%d,%s,%d,%d",
                    building->House->Class->IniName,
                    building->Class->IniName,
                    building->Health_Ratio() * 256,
                    Coord_Cell(building->Coord),
                    building->PrimaryFacing.Current(),
                    building->Trigger.Is_Valid() ? building->Trigger->Class->IniName : "None",
                    building->IsAllowedToSell,
                    building->IsToRebuild);
            ini.Put_String(INI_Name(), uname, buf);
        }
    }
}

/***********************************************************************************************
 * BuildingClass::Target_Coord -- Return the coordinate to use when firing on this building.   *
 *                                                                                             *
 *    This routine will determine the "center" location of this building for purposes of       *
 *    targeting. Usually, this location is somewhere near the foundation of the building.      *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the coordinate to use when firing upon this building (or trying to    *
 *          walk onto it).                                                                     *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/19/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
COORDINATE BuildingClass::Target_Coord(void) const
{
    COORDINATE coord = Center_Coord();

    /*
    **	TS buildings whose plot centre is not real footprint make the default
    **	aim point land on an unoccupied cell -- TSPROC's centre is the dock pad,
    **	and the tall buildings' north row is art spill. A shot resolving
    **	into such a cell damages nothing (the Mk. II railgun sweep collects
    **	victims per crossed cell; splash weapons pay adjacent-cell falloff).
    **	Aim at a cell the building always occupies.
    */
    if (*this == STRUCT_TSPROC) {
        // The occupied cell west of the dock pad (column 1, row 1).
        return XY_Coord(Coord_X(coord) - CELL_LEPTON_W, Coord_Y(coord));
    }
    if (*this == STRUCT_TSPOWR || *this == STRUCT_TSRADR || *this == STRUCT_TSTECH || *this == STRUCT_TSFGEN
        || TF_Is_Wall_Tower(Class->Type)) {
        // The south row is the only real footprint.
        return XY_Coord(Coord_X(coord), Coord_Y(Cell_Coord((CELL)(Coord_Cell(Coord) + MAP_CELL_W))));
    }

    if (Class->FoundationFace != FACING_NONE) {
        return (Adjacent_Cell(coord, Class->FoundationFace));
    }
    return (coord);
}

/***********************************************************************************************
 * BuildingClass::Factory_AI -- Handle factory production and initiation.                      *
 *                                                                                             *
 *    Some building (notably the computer controlled ones) can have a factory object attached. *
 *    This routine handles processing of that factory and also detecting when production       *
 *    should begin in order to initiate production.                                            *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Only call this routine once per building per game logic loop.                   *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Factory_AI(void)
{
    /*
    **	Handle any production tied to this building. Only computer controlled buildings have
    **	production attached to the building itself. The player uses the sidebar interface for
    **	all production control.
    */
    if (Factory.Is_Valid() && Factory->Has_Completed() && PlacementDelay == 0) {
        TechnoClass* product = Factory->Get_Object();
        //		FactoryClass * fact = Factory;

        /*
        **	An addon plug deletes itself as it installs into its host, so what the product is
        **	has to be read before it leaves the factory.
        */
        RTTIType product_rtti = product->What_Am_I();
        StructType product_struct = (product_rtti == RTTI_BUILDING) ? ((BuildingClass*)product)->Class->Type : STRUCT_NONE;

        int tf_exit = Exit_Object(product);
#if TF_DEV_BUILD
        if (Is_TS_War_Factory()) {
            TF_WF_Log(this, "AI product: Exit_Object=%d", tf_exit);
        }
#endif
        switch (tf_exit) {

        /*
        **	If the object could not leave the factory, then either request
        **	a transport, place the (what must be a) building using another method, or
        **	abort the production and refund money.
        */
        case 0:
            Factory->Abandon();
            delete (FactoryClass*)Factory;
            Factory = 0;
            break;

        /*
        **	Exiting this building is prevented by some temporary blockage. Wait
        **	a bit before trying again.
        */
        case 1:
            PlacementDelay = TICKS_PER_SECOND * 3;
            break;

        /*
        **	The object was successfully sent from this factory. Inform the house
        **	tracking logic that the requested object has been produced.
        */
        case 2:
            switch (product_rtti) {
            case RTTI_VESSEL:
                House->JustBuiltVessel = ((VesselClass*)product)->Class->Type;
                House->IsBuiltSomething = true;
                break;

            case RTTI_UNIT:
                House->JustBuiltUnit = ((UnitClass*)product)->Class->Type;
                House->IsBuiltSomething = true;
                break;

            case RTTI_INFANTRY:
                House->JustBuiltInfantry = ((InfantryClass*)product)->Class->Type;
                House->IsBuiltSomething = true;
                break;

            case RTTI_BUILDING:
                House->JustBuiltStructure = product_struct;
                House->IsBuiltSomething = true;
                break;

            case RTTI_AIRCRAFT:
                House->JustBuiltAircraft = ((AircraftClass*)product)->Class->Type;
                House->IsBuiltSomething = true;
                break;

            default:
                break;
            }
            //				fact->Completed();
            Factory->Completed();
            //				delete fact;
            delete (FactoryClass*)Factory;
            Factory = 0;
            break;

        default:
            break;
        }
    }

    /*
    **	Pick something to create for this factory.
    */
    if (House->IsStarted && Mission != MISSION_CONSTRUCTION && Mission != MISSION_DECONSTRUCTION) {

        /*
        **	Buildings that produce other objects have special factory logic handled here.
        */
        if (Class->ToBuild != RTTI_NONE) {
            if (Factory.Is_Valid()) {

                /*
                **	If production has halted, then just abort production and make the
                **	funds available for something else.
                */
                if (PlacementDelay == 0 && !Factory->Is_Building()) {
                    // TF: a computer house holds an order it can't afford yet while it has income, as a human's sidebar
                    // pauses one: Start() refuses what it can't afford this instant, but income soon covers it.
                    if (!House->IsHuman && !Factory->Has_Completed()
                        && (Factory->Start() || House->TF_Has_Income())) {
                        PlacementDelay = TICKS_PER_SECOND * 3;
#if TF_DEV_BUILD // TF_AI_DIAG -- the order survived the stall check: held (or resumed) rather
                 // than scrapped. At most one line per 3-second retry window.
                        extern FILE* TF_AI_Diag_File(void);
                        FILE* _tfdbg = TF_AI_Diag_File();
                        TechnoClass* _obj = Factory->Get_Object();
                        if (_tfdbg != NULL) {
                            fprintf(_tfdbg,
                                    "F%ld H%d AL%d PROD %s %s pct=%d cash=%d at %s#%d\n",
                                    (long)Frame,
                                    (int)House->Class->House,
                                    (int)House->ActLike,
                                    Factory->Is_Building() ? "resume" : "hold",
                                    _obj != NULL ? _obj->Class_Of().IniName : "(none)",
                                    Factory->Completion(),
                                    House->Available_Money(),
                                    Class->IniName,
                                    (int)ID);
                            fflush(_tfdbg);
                        }
#endif
                        return;
                    }
#if TF_DEV_BUILD // TF_AI_DIAG -- a stalled order is scrapped here rather than paused, so an
                 // item that repeatedly reaches PROD start and never appears died on this
                 // line. Records what was lost, how far it got, and whether the house could
                 // actually afford to continue.
                    if (!House->IsHuman) {
                        extern FILE* TF_AI_Diag_File(void);
                        FILE* _tfdbg = TF_AI_Diag_File();
                        TechnoClass* _obj = Factory->Get_Object();
                        if (_tfdbg != NULL) {
                            fprintf(_tfdbg,
                                    "F%ld H%d AL%d PROD abandon %s pct=%d cash=%d completed=%d at %s#%d\n",
                                    (long)Frame,
                                    (int)House->Class->House,
                                    (int)House->ActLike,
                                    _obj != NULL ? _obj->Class_Of().IniName : "(none)",
                                    Factory->Completion(),
                                    House->Available_Money(),
                                    (int)Factory->Has_Completed(),
                                    Class->IniName,
                                    (int)ID);
                            fflush(_tfdbg);
                        }
                    }
#endif
                    Factory->Abandon();
                    delete (FactoryClass*)Factory;
                    Factory = 0;
                }

            } else {

                /*
                **	Only look to start production if there is at least a small amount of
                **	money available. In cases where there is no practical money left, then
                **	production can never complete -- don't bother starting it.
                */
                if (House->IsStarted && House->Available_Money() > 10) {

                    // TF: a computer house runs one order per factory category, as a human does; parallel orders would
                    // compound Time_To_Build's factory divisor and could exhaust the FactoryClass heap.
                    if (!House->IsHuman) {
                        bool category_busy = false;
                        for (int index = 0; index < Buildings.Count(); index++) {
                            BuildingClass const* b = Buildings.Ptr(index);
                            if (b != NULL && b != this && !b->IsInLimbo && b->House == House
                                && b->Class->ToBuild == Class->ToBuild && b->Factory.Is_Valid()) {
                                category_busy = true;
                                break;
                            }
                        }
                        if (category_busy) {
                            return;
                        }
                    }

                    TechnoTypeClass const* techno = House->Suggest_New_Object(Class->ToBuild, *this == STRUCT_KENNEL);

                    // TF: helipads build rotary aircraft and airstrips fixed-wing; the wrong host declines the order,
                    // as the suggestion doesn't know which factory asks and an aircraft built at the wrong one is lost.
                    if (techno != NULL && Class->ToBuild == RTTI_AIRCRAFTTYPE) {
                        bool fixed_wing = ((AircraftTypeClass const*)techno)->IsFixedWing;
                        bool strip_host = (*this == STRUCT_AIRSTRIP || *this == STRUCT_TDAFLD
                                           || *this == STRUCT_TDGAFLD);
                        if (fixed_wing != strip_host) {
                            techno = NULL;
                        }
                    }

                    // TF: only the dropship bay builds its deliveries and it builds nothing else, and no factory takes
                    // an order TF_Delivery_Order_Refused would refuse; the wrong one declines it for the other.
                    if (techno != NULL && Class->ToBuild == RTTI_UNITTYPE) {
                        UnitTypeClass const* ut = (UnitTypeClass const*)techno;
                        if (TF_Is_Dropship_Delivered(ut) != (*this == STRUCT_TSDROP)
                            || TF_Delivery_Order_Refused(House, RTTI_UNITTYPE, ut->Type)) {
                            techno = NULL;
                        }
                    }

                    /*
                    **	If a suitable object type was selected for production, then start
                    **	producing it now.
                    */
                    if (techno != NULL) {
                        Factory = new FactoryClass;
                        if (Factory.Is_Valid()) {
                            if (!Factory->Set(*techno, *House)) {
                                delete (FactoryClass*)Factory;
                                Factory = 0;
                            } else {
                                House->Production_Begun(Factory->Get_Object());
                                Factory->Start();
#if TF_DEV_BUILD // TF_AI_DIAG -- primary-factory: every AI production start, to verify
                                // one-order-per-category cadence from the log timeline alone.
                                if (!House->IsHuman) {
                                    extern FILE* TF_AI_Diag_File(void);
                                    FILE* _tfdbg = TF_AI_Diag_File();
                                    if (_tfdbg != NULL) {
                                        fprintf(_tfdbg,
                                                "F%ld H%d AL%d PROD start %s (cat=%d) at factory %s#%d\n",
                                                (long)Frame,
                                                (int)House->Class->House,
                                                (int)House->ActLike,
                                                techno->IniName,
                                                (int)Class->ToBuild,
                                                Class->IniName,
                                                (int)ID);
                                        fflush(_tfdbg);
                                    }
                                }
#endif
                            }
                        }
                    }
                }
            }
        }
    }
}

/***********************************************************************************************
 * BuildingClass::Rotation_AI -- Process any turret rotation required of this building.        *
 *                                                                                             *
 *    Some buildings have a turret and this routine handles processing the turret rotation.    *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Only call this routine once per building per game logic loop.                   *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1996 JLB : Created.                                                                 *
 *   10/27/1996 JLB : Rotation does not occur if power and no power avail.                     *
 *=============================================================================================*/
void BuildingClass::Rotation_AI(void)
{
    if ((Class->IsTurretEquipped || *this == STRUCT_TSPULS) && Mission != MISSION_CONSTRUCTION
        && Mission != MISSION_DECONSTRUCTION && (!Class->IsPowered || House->Power_Fraction() >= 1)) {

        /*
        **	Rotate turret to match desired facing.
        */
        if (PrimaryFacing.Is_Rotating()) {
            if (PrimaryFacing.Rotation_Adjust(Class->ROT)) {
                Mark(MARK_CHANGE);
            }
        }
    }
}

/***********************************************************************************************
 * BuildingClass::Charging_AI -- Handles the special charging logic for Tesla coils.           *
 *                                                                                             *
 *    This handles the special logic required of the charging tesla coil. It requires special  *
 *    processing since its charge up is dependant upon the target and power surplus of the     *
 *    owning house.                                                                            *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Charging_AI(void)
{
    if (Class->PrimaryWeapon != NULL && Class->PrimaryWeapon->IsElectric && BState != BSTATE_CONSTRUCTION) {
        if (Target_Legal(TarCom) && House->Power_Fraction() >= 1) {
            if (!IsCharged) {
                if (IsCharging) {
                    //					if (stagechange) {
                    Mark(MARK_CHANGE);
                    // TF: the charge completes on the ACTIVE animation's last frame, or one past it for the Obelisk as
                    // in TD; a fixed stage 9 would run the Obelisk's 4-frame charge into its damaged frames.
                    int charge_complete_stage;
                    if (*this == STRUCT_TDOBLI) {
                        charge_complete_stage = Class->Anims[BSTATE_ACTIVE].Count;
                    } else {
                        charge_complete_stage = Class->Anims[BSTATE_ACTIVE].Count - 1;
                    }
                    if (charge_complete_stage < 1) charge_complete_stage = 9;  // safety fallback
                    if (Fetch_Stage() >= charge_complete_stage) {
                        IsCharged = true;
                        IsCharging = false;
                        Set_Rate(0);
                    }
                    //					}
                } else if (!Arm) {
                    IsCharged = false;
                    IsCharging = true;
                    Set_Stage(0);
                    // TF: the Obelisk charges at TD's pace, 15 ticks a stage, with its own power-up sound; the Tesla
                    // Coil keeps RA's 3 ticks and warm-up.
                    if (*this == STRUCT_TDOBLI) {
                        Set_Rate(15);
                    } else {
                        Set_Rate(3);
                    }
                    if (*this == STRUCT_TDOBLI) {
                        Sound_Effect(VOC_TD_LASER_POWER, Coord);
                    } else {
                        Sound_Effect(VOC_TESLA_POWER_UP, Coord);
                    }
                }
            }
        } else {
            if (IsCharging || IsCharged) {
                Mark(MARK_CHANGE);
                IsCharging = false;
                IsCharged = false;
                Set_Stage(0);
                Set_Rate(0);
            }
        }
    }
}

/***********************************************************************************************
 * BuildingClass::Repair_AI -- Handle the repair (and sell) logic for the building.            *
 *                                                                                             *
 *    This routine handle the repair animation and healing logic. It also detects when the     *
 *    (computer controlled) building should begin repair or sell itself.                       *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Only call this routine once per building per game logic loop.                   *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Repair_AI(void)
{
    if (House->IQ >= Rule.IQRepairSell && Mission != MISSION_CONSTRUCTION && Mission != MISSION_DECONSTRUCTION) {
        /*
        **	Possibly start repair process if the building is below half strength.
        */
        //		unsigned ratio = MIN(House->Smartness, 0x00F0);
        if (Can_Repair()) {
            if (House->Available_Money() >= Rule.RepairThreshhold) {
                if (!House->DidRepair) {
                    if (!IsRepairing && (IsCaptured || IsToRepair || House->IsHuman || Session.Type != GAME_NORMAL)) {
                        House->DidRepair = true; // flag that this house did its repair allocation for this frame
                        Repair(1);

                        if (!House->IsHuman) {
                            House->RepairTimer = Random_Pick((int)(House->RepairDelay * (TICKS_PER_MINUTE / 4)),
                                                             (int)(House->RepairDelay * TICKS_PER_MINUTE * 2));
                        }
                    }
                }
            } else {
                if ((Session.Type != GAME_NORMAL || IsAllowedToSell) && IsTickedOff
                    && House->Control.TechLevel >= Rule.IQSellBack && Random_Pick(0, 50) < House->Control.TechLevel
                    && !Trigger.Is_Valid() && !Class->Is_Construction_Yard() && Health_Ratio() < Rule.ConditionRed) {
                    Sell_Back(1);
                }
            }
        }
    }

    /*
    **	If it is repairing, then apply any repair effects as necessary.
    */
    if (IsRepairing && (Frame % (Rule.RepairRate * TICKS_PER_MINUTE)) == 0) {
        IsWrenchVisible = (IsWrenchVisible == false);
        Mark(MARK_CHANGE);
        int cost = Class->Repair_Cost();
        int step = Class->Repair_Step();

        /*
        **	Check for and expend any necessary monies to continue the repair.
        */
        if (House->Available_Money() >= cost) {
            House->Spend_Money(cost);
            Strength += step;

            if (Strength >= Class->MaxStrength) {
                Strength = Class->MaxStrength;
                IsRepairing = false;
            }
        } else {
            IsRepairing = false;
        }
    }
}

/***********************************************************************************************
 * BuildingClass::Animation_AI -- Handles normal building animation processing.                *
 *                                                                                             *
 *    This will process the general building animation mechanism. It detects when the          *
 *    building animation sequence has completed and flags the building to perform mission      *
 *    changes as a result.                                                                     *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Call this routine only once per building per game logic loop.                   *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Animation_AI(void)
{
    bool stagechange = Graphic_Logic();
    bool toloop = false;

    /*
    **	Always refresh the SAM site if it has an animation change.
    */
    // TF: the TD SAM refreshes too, as its rise and lower are drawn from stage changes.
    if ((*this == STRUCT_SAM || *this == STRUCT_TDSAM) && stagechange)
        Mark(MARK_CHANGE);

    if ((!Class->IsTurretEquipped && *this != STRUCT_TESLA && *this != STRUCT_TDOBLI) || Mission == MISSION_CONSTRUCTION
        || Mission == MISSION_DECONSTRUCTION) {
        if (stagechange) {

            /*
            **	Check for animation end or if special case of MCV deconstructing when it is allowed
            **	to convert back into an MCV.
            */
            BuildingTypeClass::AnimControlType const* ctrl = Fetch_Anim_Control();

            /*
            **	When the last frame of the current animation sequence is reached, flag that
            **	a new mission may be started. This must occur before the animation actually
            **	loops so that if a mission change does occur, it will have a chance to change
            **	the building graphic before the last frame is replaced by the first frame of
            **	the loop.
            */
            if (Fetch_Stage() == ctrl->Start + ctrl->Count - 1
                || (!Target_Legal(ArchiveTarget) /*Is_MCV_Deploy()*/ && Class->Is_Construction_Yard()
                    && Mission == MISSION_DECONSTRUCTION && Fetch_Stage() == (42 - 19))) {
                IsReadyToCommence = true;
            }

            /*
            **	If the animation advances beyond the last frame, then start the animation
            **	sequence over from the beginning.
            */
            if (Fetch_Stage() >= ctrl->Start + ctrl->Count) {
                toloop = true;
            }
            Mark(MARK_CHANGE);
        } else {
            if (BState == BSTATE_NONE || Fetch_Rate() == 0) {
                IsReadyToCommence = true;
            }
        }
    }

    /*
    **	If there is a door that is animating, then it might cause this building
    **	to be redrawn. Check for and flag to redraw as necessary.
    */
    if (Time_To_Redraw()) {
        Clear_Redraw_Flag();
        Mark(MARK_CHANGE);
    }

    /*
    **	The animation sequence has looped. Restart it and flag this loop condition.
    **	This is used to tell the mission system that the animation has completed. It
    **	also signals that now is a good time to act on any pending mission.
    */
    if (toloop) {
        BuildingTypeClass::AnimControlType const* ctrl = Fetch_Anim_Control();
        if (BState == BSTATE_CONSTRUCTION || BState == BSTATE_IDLE) {
            Set_Rate(Options.Normalize_Delay(ctrl->Rate));
        } else {
            Set_Rate(ctrl->Rate);
        }
        Set_Stage(ctrl->Start);
        Mark(MARK_CHANGE);
    }
}

/***********************************************************************************************
 * BuildingClass::How_Many_Survivors -- This determine the maximum number of survivors.        *
 *                                                                                             *
 *    This routine is called to determine how many survivors should run from this building     *
 *    when it is either sold or destroyed. Buildings that are captured have fewer survivors.   *
 *    The number of survivors is a portion of the cost of the building divided by the cost     *
 *    of a minigunner.                                                                         *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of soldiers that should run from this building.            *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   08/04/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingClass::How_Many_Survivors(void) const
{
    if (IsSurvivorless || !Class->IsCrew)
        return (0);

    int divisor = InfantryTypeClass::As_Reference(INFANTRY_E1).Raw_Cost();
    if (divisor == 0)
        return (0);
    if (IsCaptured)
        divisor *= 2;
    int count = (Class->Raw_Cost() * Rule.SurvivorFraction) / divisor;
    return (Bound(count, 1, 5));
}

/***********************************************************************************************
 * BuildingClass::Get_Image_Data -- Fetch the image pointer for the building.                  *
 *                                                                                             *
 *    This routine will return with a pointer to the shape data for the building. The shape    *
 *    data is different than normal when the building is undergoing construction and           *
 *    disassembly.                                                                             *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the shape data for this building.                        *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   08/06/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void const* BuildingClass::Get_Image_Data(void) const
{
    if (BState == BSTATE_CONSTRUCTION) {
        return (Class->Get_Buildup_Data());
    }
    return (TechnoClass::Get_Image_Data());
}

/***********************************************************************************************
 * BuildingClass::Value -- Determine the value of this building.                               *
 *                                                                                             *
 *    The value of the building is normally just its ordinary assigned value. However, in the  *
 *    case of fakes, the value is artificially enhanced to match the structure that is         *
 *    being faked.                                                                             *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the point value of the building type.                                 *
 *                                                                                             *
 * WARNINGS:   The point value returned should not be used for scoring, only for target        *
 *             scanning.                                                                       *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/16/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
int BuildingClass::Value(void) const
{
    if (Class->IsFake) {
        switch (Class->Type) {
        case STRUCT_FAKEWEAP:
            return (BuildingTypeClass::As_Reference(STRUCT_WEAP).Reward
                    + BuildingTypeClass::As_Reference(STRUCT_WEAP).Risk);

        case STRUCT_FAKECONST:
            return (BuildingTypeClass::As_Reference(STRUCT_CONST).Reward
                    + BuildingTypeClass::As_Reference(STRUCT_CONST).Risk);

        case STRUCT_FAKE_YARD:
            return (BuildingTypeClass::As_Reference(STRUCT_SHIP_YARD).Reward
                    + BuildingTypeClass::As_Reference(STRUCT_SHIP_YARD).Risk);

        case STRUCT_FAKE_PEN:
            return (BuildingTypeClass::As_Reference(STRUCT_SUB_PEN).Reward
                    + BuildingTypeClass::As_Reference(STRUCT_SUB_PEN).Risk);

        case STRUCT_FAKE_RADAR:
            return (BuildingTypeClass::As_Reference(STRUCT_RADAR).Reward
                    + BuildingTypeClass::As_Reference(STRUCT_RADAR).Risk);

        default:
            break;
        }
    }
    return (TechnoClass::Value());
}

/***********************************************************************************************
 * BuildingClass::Remove_Gap_Effect -- Stop a gap generator from jamming cells.					  *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none *
 *                                                                                             *
 * WARNINGS:   																										  *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/20/1996 BWG : Created.                                                                 *
 *=============================================================================================*/
void BuildingClass::Remove_Gap_Effect(void)
{
    // unjam this one's field...
    Map.UnJam_From(Coord_Cell(Center_Coord()), Rule.GapShroudRadius, House);

    /*
    ** Updated for client/server multiplayer. ST - 8/12/2019 11:14AM
    */
    if (Session.Type != GAME_GLYPHX_MULTIPLAYER) {
        if (!House->IsPlayerControl && PlayerPtr->IsGPSActive) {
            Map.Sight_From(Coord_Cell(Center_Coord()), Rule.GapShroudRadius, PlayerPtr);
        }

    } else {

        for (int i = 0; i < Session.Players.Count(); i++) {
            HouseClass* player_house = HouseClass::As_Pointer(Session.Players[i]->Player.ID);
            if (player_house->IsGPSActive && player_house != House) {
                Map.Sight_From(Coord_Cell(Center_Coord()), Rule.GapShroudRadius, player_house);
            }
        }
    }

    // and rejam any overlapping buildings' fields
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass* obj = Buildings.Ptr(index);
        if (obj && !obj->IsInLimbo && obj->House == House && *obj == STRUCT_GAP && obj != this) {
            obj->IsJamming = false;
            obj->Arm = 0;
            //			Map.Jam_From(Coord_Cell(obj->Center_Coord()), Rule.GapShroudRadius, PlayerPtr);
        }
    }
}

short const* BuildingClass::Overlap_List(bool redraw) const
{
    if ((Spied_By() & (1 << PlayerPtr->Class->House)) != 0 && Is_Selected_By_Player()) {
        if (*this == STRUCT_BARRACKS || *this == STRUCT_TENT) {
            static short const _list[] = {-1, 2, (MAP_CELL_W * 1) - 1, (MAP_CELL_W * 1) + 2, REFRESH_EOL};
            return (_list);
        } else if ((*this == STRUCT_REFINERY || *this == STRUCT_TDPROC)) {
            static short const _list[] = {
                0, 2, (MAP_CELL_W * 2) + 0, (MAP_CELL_W * 2) + 1, (MAP_CELL_W * 2) + 2, REFRESH_EOL};
            return (_list);
        }
    }
    return (TechnoClass::Overlap_List(redraw));
}

unsigned BuildingClass::Spied_By() const
{
    unsigned spiedby = TechnoClass::Spied_By();

    /*
    ** If it's an ore refinery or other such storage-capable building,
    ** loop thru all of their buildings to see if ANY of them are spied
    ** upon, 'cause once you spy any money, you've spied all of it.
    */
    if (Class->Capacity) {
        for (int index = 0; index < Buildings.Count(); index++) {
            BuildingClass* building = Buildings.Ptr(index);
            if (building->House == House && building->Class->Capacity) {
                spiedby |= building->SpiedBy;
            }
        }
    }

    return spiedby;
}
