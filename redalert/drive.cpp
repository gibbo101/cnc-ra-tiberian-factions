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

/* $Header: /CounterStrike/DRIVE.CPP 1     3/03/97 10:24a Joe_bostic $ */
/***********************************************************************************************
 ***              C O N F I D E N T I A L  ---  W E S T W O O D  S T U D I O S               ***
 ***********************************************************************************************
 *                                                                                             *
 *                 Project Name : Command & Conquer                                            *
 *                                                                                             *
 *                    File Name : DRIVE.CPP                                                    *
 *                                                                                             *
 *                   Programmer : Joe L. Bostic                                                *
 *                                                                                             *
 *                   Start Date : April 22, 1994                                               *
 *                                                                                             *
 *                  Last Update : October 31, 1996 [JLB]                                       *
 *                                                                                             *
 *---------------------------------------------------------------------------------------------*
 * Functions:                                                                                  *
 *   DriveClass::AI -- Processes unit movement and rotation.                                   *
 *   DriveClass::Approach_Target -- Handles approaching the target in order to attack it.      *
 *   DriveClass::Assign_Destination -- Set the unit's NavCom.                                  *
 *   DriveClass::Class_Of -- Fetches a reference to the class type for this object.            *
 *   DriveClass::Debug_Dump -- Displays status information to monochrome screen.               *
 *   DriveClass::Do_Turn -- Tries to turn the vehicle to the specified direction.              *
 *   DriveClass::DriveClass -- Constructor for drive class object.                             *
 *   DriveClass::Fixup_Path -- Adds smooth start path to normal movement path.                 *
 *   DriveClass::Force_Track -- Forces the unit to use the indicated track.                    *
 *   DriveClass::Lay_Track -- Handles track laying logic for the unit.                         *
 *   DriveClass::Limbo -- Prepares vehicle and then limbos it.                                 *
 *   DriveClass::Mark_Track -- Marks the midpoint of the track as occupied.                    *
 *   DriveClass::Ok_To_Move -- Checks to see if this object can begin moving.                  *
 *   DriveClass::Per_Cell_Process -- Handles when unit finishes movement into a cell.          *
 *   DriveClass::Response_Attack -- Voice feedback when ordering the unit to attack a target.  *
 *   DriveClass::Response_Move -- Voice feedback when ordering the unit to move.               *
 *   DriveClass::Response_Select -- Voice feedback when selecting the unit.                    *
 *   DriveClass::Scatter -- Causes the unit to travel to a nearby safe cell.                   *
 *   DriveClass::Smooth_Turn -- Handles the low level coord calc for smooth turn logic.        *
 *   DriveClass::Start_Of_Move -- Tries to get a unit to advance toward cell.                  *
 *   DriveClass::Stop_Driver -- Handles removing occupation bits when driving stops.           *
 *   DriveClass::Teleport_To -- Teleport object to specified location.                         *
 *   DriveClass::While_Moving -- Processes unit movement.                                      *
 * - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

#include "function.h"

#ifdef NEVER
void test(void)
{
    enum nums
    {
        one,
        two,
        three
    };

    nums x;
    nums* ptr;

    ptr = &x;
}
#endif

/***********************************************************************************************
 * DriveClass::Response_Select -- Voice feedback when selecting the unit.                      *
 *                                                                                             *
 *    This is the voice to play when the unit is selected.                                     *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   12/30/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void DriveClass::Response_Select(void)
{
    assert(IsActive);

    static VocType _response[] = {VOC_VEHIC, VOC_REPORT, VOC_YESSIR, VOC_YESSIR, VOC_YESSIR, VOC_AWAIT};
    VocType response = _response[Sim_Random_Pick(0, ARRAY_SIZE(_response) - 1)];
    if (AllowVoice) {
        Sound_Effect(response, fixed(1), -(ID + 1));
    }
}

/***********************************************************************************************
 * DriveClass::Response_Move -- Voice feedback when ordering the unit to move.                 *
 *                                                                                             *
 *    This plays the audio feedback when ordering this unit to move to a new destination.      *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   12/30/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void DriveClass::Response_Move(void)
{
    assert(IsActive);

    static VocType _response[] = {
        VOC_ACKNOWL,
        VOC_AFFIRM,
    };
    VocType response = _response[Sim_Random_Pick(0, ARRAY_SIZE(_response) - 1)];
    if (AllowVoice) {
        Sound_Effect(response, fixed(1), -(ID + 1));
    }
}

/***********************************************************************************************
 * DriveClass::Response_Attack -- Voice feedback when ordering the unit to attack a target.    *
 *                                                                                             *
 *    This plays the audio feedback when ordering this unit to attack.                         *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   12/30/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void DriveClass::Response_Attack(void)
{
    assert(IsActive);

    static VocType _response[] = {VOC_AFFIRM, VOC_ACKNOWL};
    VocType response = _response[Sim_Random_Pick(0, ARRAY_SIZE(_response) - 1)];
    if (AllowVoice) {
        Sound_Effect(response, fixed(1), -(ID + 1));
    }
}

/***********************************************************************************************
 * DriveClass::Scatter -- Causes the unit to travel to a nearby safe cell.                     *
 *                                                                                             *
 *    This routine is called when the unit discovers that it should get out of the "hot seat"  *
 *    and move to an adjacent cell. Since the safety of the adjacent cell is not determined    *
 *    before the move begins, it will appear that the unit is just scattering (which it        *
 *    should).                                                                                 *
 *                                                                                             *
 * INPUT:   threat   -- The coordinate of the source of the threat. The unit will try to move  *
 *                      roughly away from the threat.                                          *
 *                                                                                             *
 *          forced   -- The threat is real and a serious effort to scatter should be made.     *
 *                                                                                             *
 *          nokidding-- The scatter should affect the player's infantry even if it otherwise   *
 *                      wouldn't have.                                                         *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/25/1994 JLB : Created.                                                                 *
 *   09/27/1995 JLB : Revised to never scatter if already moving.                              *
 *   07/09/1996 JLB : Moved to DriveClass so that ships will scatter too.                      *
 *   08/02/1996 JLB : Added the "nokidding" parameter.                                         *
 *=============================================================================================*/
void DriveClass::Scatter(COORDINATE threat, bool forced, bool nokidding)
{
    assert(IsActive);

    /*
    **	Certain missions prevent scattering regardless of whether it would be
    **	a good idea or not.
    */
    if (MissionControl[Mission].IsParalyzed)
        return;

    if ((What_Am_I() != RTTI_UNIT || !((UnitClass*)this)->IsDumping)
        && (!Target_Legal(NavCom) || (nokidding && !IsRotating))) {
        if (!Target_Legal(TarCom) || forced || Random_Pick(1, 4) == 1) {
            FacingType toface;
            FacingType newface;
            CELL newcell;

            if (threat != 0) {
                toface = Dir_Facing(Direction8(threat, Coord));
                toface = toface + FacingType(Random_Pick(0, 2) - 1);
            } else {
                toface = Dir_Facing(PrimaryFacing.Current());
                toface = toface + FacingType(Random_Pick(0, 2) - 1);
            }

            for (FacingType face = FACING_N; face < FACING_COUNT; face++) {
                newface = toface + face;
                newcell = Adjacent_Cell(Coord_Cell(Coord), newface);

                if (Map.In_Radar(newcell) && Can_Enter_Cell(newcell) == MOVE_OK) {
                    Assign_Destination(::As_Target(newcell));
                }
            }
        }
    }
}

/***********************************************************************************************
 * DriveClass::Limbo -- Prepares vehicle and then limbos it.                                   *
 *                                                                                             *
 *    This routine removes the occupation bits for the vehicle and also handles cleaning up    *
 *    any vehicle reservation bits. After this, it then proceeds with limboing the unit.       *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  bool; Was the vehicle limboed?                                                     *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   12/22/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
bool DriveClass::Limbo(void)
{
    if (!IsInLimbo) {
        Stop_Driver();
        TrackNumber = -1;
    }
    return (FootClass::Limbo());
}

/***********************************************************************************************
 * DriveClass::Stop_Driver -- Handles removing occupation bits when driving stops.             *
 *                                                                                             *
 *    This routine will remove the "reservation" flag (if present) when the vehicle is         *
 *    required to stop movement.                                                               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  bool; Was the vehicle stopped?                                                     *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   12/22/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
bool DriveClass::Stop_Driver(void)
{
    assert(IsActive);

    /*
    ** We only need to do something if the vehicle is actually going
    ** somewhere.
    */
    if (Head_To_Coord()) {

        /*
        ** Safe off whether the vehicle is down or not so we know whether
        ** we have to put it back down.
        */
        int temp = IsDown;

        /*
        ** If the vehicle is down, pick it up so it doesn't interfere with
        ** our flags.
        */
        if (temp) {
            Mark(MARK_UP);
        }

        /*
        ** Call the drive class function which will let us release the
        ** reserved track.
        */
        Mark_Track(Head_To_Coord(), MARK_UP);

        /*
        ** If it was down it should be down when we are done.
        */
        if (temp) {
            Mark(MARK_DOWN);
        }
    }
    return (FootClass::Stop_Driver());
}

/***********************************************************************************************
 * DriveClass::Do_Turn -- Tries to turn the vehicle to the specified direction.                *
 *                                                                                             *
 *    This routine will set the vehicle to rotate to the direction specified. For tracked      *
 *    vehicles, it is just a simple rotation. For wheeled vehicles, it performs a series       *
 *    of short drives (three point turn) to face the desired direction.                        *
 *                                                                                             *
 * INPUT:   dir   -- The direction that this vehicle should face.                              *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void DriveClass::Do_Turn(DirType dir)
{
    assert(IsActive);

    if (dir != PrimaryFacing) {

#ifdef TOFIX
        /*
        **	Special rotation track is needed for units that
        **	cannot rotate in place.
        */
        if (Special.IsThreePoint && TrackNumber == -1 && Techno_Type_Class()->Speed == SPEED_WHEEL) {
            int facediff;    // Signed difference between current and desired facing.
            FacingType face; // Current facing (ordinal value).

            facediff = PrimaryFacing.Difference(dir) >> 5;
            facediff = Bound(facediff, -2, 2);
            if (facediff) {
                face = Dir_Facing(PrimaryFacing);

                IsOnShortTrack = true;
                Force_Track(face * FACING_COUNT + (face + facediff), Coord);

                Path[0] = FACING_NONE;
                Set_Speed(0xFF); // Full speed.
            }
        } else {
            PrimaryFacing.Set_Desired(dir);
        }
#else
        PrimaryFacing.Set_Desired(dir);
//			IsRotating = true;
#endif
    }
}

/***********************************************************************************************
 * DriveClass::Teleport_To -- Teleport object to specified location.                           *
 *                                                                                             *
 *    This will teleport the object to the specified location or as close as possible to it    *
 *    if the destination is blocked.                                                           *
 *                                                                                             *
 * INPUT:   cell  -- The desired destination cell to teleport to.                              *
 *                                                                                             *
 * OUTPUT:  bool; Was the teleport successful?                                                 *
 *                                                                                             *
 * WARNINGS:   All current activity of this object will be terminated by the teleport. It will *
 *             arrive at the destination in static guard mode.                                 *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/21/1996 JLB : Created.                                                                 *
 *   10/31/1996 JLB : Handles flag teleport case.                                              *
 *=============================================================================================*/
bool DriveClass::Teleport_To(CELL cell)
{
    /*
    **	All cargo gets destroyed.
    */
    if (Rule.IsChronoKill) {
        Kill_Cargo(NULL);
    }

    Stop_Driver();
    Force_Track(-1, 0);
    PrimaryFacing.Set_Current(PrimaryFacing.Desired());
    Transmit_Message(RADIO_OVER_OUT);
    /*
    **	Attack-move (CFE port): end attack-move on teleport so the unit doesn't
    **	drive back off to its prior destination. Unconditional for us -- the
    **	chronotank attack-move path in TechnoClass::AI saves and restores the
    **	state across the teleport when there's still queued movement (CFE used a
    **	SkipNavQueueUpdate flag here instead, which we did not port).
    */
    ResetAttackMove();
    Assign_Destination(TARGET_NONE);
    Assign_Target(TARGET_NONE);
    Assign_Mission(MISSION_NONE);
    Commence();
    Mark(MARK_UP);

    /*
    **	A teleported unit will drop the flag right where it's at.
    */
    if (What_Am_I() == RTTI_UNIT && ((UnitClass*)this)->Flagged != HOUSE_NONE) {
        HouseClass::As_Pointer(((UnitClass*)this)->Flagged)->Flag_Attach(Coord_Cell(Coord));
    }

    if (Can_Enter_Cell(cell) != MOVE_OK) {
        cell = Map.Nearby_Location(cell, Techno_Type_Class()->Speed);
    }
    Coord = Cell_Coord(cell);
    Mark(MARK_DOWN);
    Look(false);
    Per_Cell_Process(PCP_END);
    return (true);
}

/***********************************************************************************************
 * DriveClass::Force_Track -- Forces the unit to use the indicated track.                      *
 *                                                                                             *
 *    This override (nuclear bomb) style routine is to be used when a unit needs to start      *
 *    on a movement track but is outside the normal movement system. This occurs when a        *
 *    harvester starts driving off of a refinery.                                              *
 *                                                                                             *
 * INPUT:   track -- The track number to start on.                                             *
 *                                                                                             *
 *          coord -- The coordinate that the unit will end up at when the movement track       *
 *                   is completed.                                                             *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/17/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void DriveClass::Force_Track(int track, COORDINATE coord)
{
    assert(IsActive);

    TrackNumber = track;
    TrackIndex = 0;
    if (coord != 0) {
        Start_Driver(coord);
    }
}

/***********************************************************************************************
 * DriveClass::DriveClass -- Constructor for drive class object.                               *
 *                                                                                             *
 *    This will initialize the drive class to its default state. It is called as a result      *
 *    of creating a unit.                                                                      *
 *                                                                                             *
 * INPUT:   classid  -- The unit's ID class. It is passed on to the foot class constructor.    *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/13/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
DriveClass::DriveClass(RTTIType rtti, int id, HousesType house)
    : FootClass(rtti, id, house)
    , IsMoebius(false)
    , IsHarvesting(false)
    , IsTurretLockedDown(false)
    , IsOnShortTrack(false)
    , SpeedAccum(0)
    , MoebiusCountDown(0)
    , MoebiusCell(0)
    , TrackNumber(-1)
    , TrackIndex(0)
    , LastClaimCell(-1)
    , StuckFrames(0)
{
}

#ifdef CHEAT_KEYS
/***********************************************************************************************
 * DriveClass::Debug_Dump -- Displays status information to monochrome screen.                 *
 *                                                                                             *
 *    This debug utility function will display the status of the drive class to the mono       *
 *    screen. It is through this information that bugs can be tracked down.                    *
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
void DriveClass::Debug_Dump(MonoClass* mono) const
{
    assert(IsActive);

    mono->Fill_Attrib(66, 14, 12, 1, IsMoebius ? MonoClass::INVERSE : MonoClass::NORMAL);
    FootClass::Debug_Dump(mono);
}
#endif

/***********************************************************************************************
 * DriveClass::Smooth_Turn -- Handles the low level coord calc for smooth turn logic.          *
 *                                                                                             *
 *    This routine calculates the new coordinate value needed for the                          *
 *    smooth turn logic. The adjustment and flag values must be                                *
 *    determined prior to entering this routine.                                               *
 *                                                                                             *
 * INPUT:   adj      -- The adjustment coordinate as lifted from the                           *
 *                      correct smooth turn table.                                             *
 *                                                                                             *
 *          dir      -- Pointer to dir for possible modification                               *
 *                      according to the flag bits.                                            *
 *                                                                                             *
 * OUTPUT:  Returns with the coordinate the unit should positioned to.                         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   03/14/1994 JLB : Created.                                                                 *
 *   07/13/1994 JLB : Converted to member function.                                            *
 *=============================================================================================*/
COORDINATE DriveClass::Smooth_Turn(COORDINATE adj, DirType& dir)
{
    assert(IsActive);

    DirType workdir = dir;
    int x, y;
    int temp;
    TrackControlType flags = TrackControl[TrackNumber].Flag;

    x = Coord_X(adj);
    y = Coord_Y(adj);

    if (flags & F_T) {
        temp = x;
        x = y;
        y = temp;
        workdir = (DirType)(DIR_W - workdir);
    }

    if (flags & F_X) {
        x = -x;
        workdir = (DirType)-workdir;
    }

    if (flags & F_Y) {
        y = -y;
        workdir = (DirType)(DIR_S - workdir);
    }

    dir = workdir;

    return (XY_Coord((LEPTON)(Coord_X(Head_To_Coord()) + x), (LEPTON)(Coord_Y(Head_To_Coord()) + y)));
}

/***********************************************************************************************
 * DriveClass::Assign_Destination -- Set the unit's NavCom.                                    *
 *                                                                                             *
 *    This routine is used to set the unit's navigation computer to the                        *
 *    specified target. Once the navigation computer is set, the unit                          *
 *    will start planning and moving toward the destination.                                   *
 *                                                                                             *
 * INPUT:   target   -- The destination target for the unit to head to.                        *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/07/1992 JLB : Created.                                                                 *
 *   04/15/1994 JLB : Converted to member function.                                            *
 *=============================================================================================*/
void DriveClass::Assign_Destination(TARGET target)
{
    assert(IsActive);

    /*
    **	Abort early if there is anything wrong with the parameters
    **	or the unit already is assigned the specified destination.
    */
    if (target == NavCom)
        return;

    /*
    **	For harvesting type vehicles, it might go into a dock and unload procedure
    **	when the harvester is full and an empty refinery is selected as a target.
    */
    BuildingClass* b = As_Building(target);

    /*
    **	If the player clicked on refinery but it is not busy, then assign
    **	it to unload at the refinery.
    */
    if (b != NULL && (*b == STRUCT_REFINERY || *b == STRUCT_TDPROC) && What_Am_I() == RTTI_UNIT
        && ((UnitTypeClass*)Techno_Type_Class())->IsToHarvest) {
        if (Contact_With_Whom() != b && !b->In_Radio_Contact()) {
            /*
            **	Establish radio contact protocol. If the facility responds correctly,
            **	then remain in radio contact and proceed toward the desired destination.
            */
            if (Transmit_Message(RADIO_HELLO, b) == RADIO_ROGER) {
                if (Mission != MISSION_ENTER && Mission != MISSION_HARVEST) {
                    Assign_Mission(MISSION_ENTER);
                    target = TARGET_NONE;
                } else {
                    //					target = TARGET_NONE;
                }
            } else {
                //				target = TARGET_NONE;
            }
        } else {
            //			target = TARGET_NONE;
        }
    }

    /*
    **	Set the unit's navigation computer.
    */
    FootClass::Assign_Destination(target);

    Path[0] = FACING_NONE; // Force recalculation of path.
    if (!IsDriving && Mission != MISSION_UNLOAD) {
        Start_Of_Move();
    }
}

/***********************************************************************************************
 * DriveClass::While_Moving -- Processes unit movement.                                        *
 *                                                                                             *
 *    This routine is used to process movement for the units as they move.                     *
 *    It is called many times for each cell's worth of movement.   This                        *
 *    routine only applies after the next cell HeadTo has been determined.                     *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  true/false; Should this routine be called again?                                   *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   02/02/1992 JLB : Created.                                                                 *
 *   04/15/1994 JLB : Converted to member function.                                            *
 *=============================================================================================*/
bool DriveClass::While_Moving(void)
{
    assert(IsActive);

    /*
    **	Perform quick legality checks.
    */
    if (!IsDriving || TrackNumber == -1 || (IsRotating && !Techno_Type_Class()->IsTurretEquipped)) {
        SpeedAccum = 0; // Kludge?  No speed should accumulate if movement is on hold.
        return (false);
    }

    /*
    **	If enough movement has accumulated so that the unit can
    **	visibly move on the map, then process accordingly.
    ** Slow the unit down if he's carrying a flag.
    */
    MPHType maxspeed =
        MPHType(min(Techno_Type_Class()->MaxSpeed * SpeedBias * House->GroundspeedBias, (int)MPH_LIGHT_SPEED));
    if (IsFormationMove)
        maxspeed = FormationMaxSpeed;

    int actual; // Working movement addition value.
    if (((UnitClass*)this)->Flagged != HOUSE_NONE) {
        actual = SpeedAccum + ((int)maxspeed / 2) * fixed(Speed, 256);
    } else {
        actual = SpeedAccum + maxspeed * fixed(Speed, 256);
    }

    if (actual > PIXEL_LEPTON_W) {
        TurnTrackType const* track; // Track control pointer.
        TrackType const* ptr;       // Pointer to coord offset values.
        int tracknum;               // The track number being processed.
        FacingType nextface;        // Next facing queued in path.
        bool adj;                   // Is a turn coming up?

        track = &TrackControl[TrackNumber];
        if (IsOnShortTrack) {
            tracknum = track->StartTrack;
        } else {
            tracknum = track->Track;
        }
        ptr = RawTracks[tracknum - 1].Track;
        nextface = Path[0];

        /*
        **	Determine if there is a turn coming up. If there is
        **	a turn, then track jumping might occur.
        */
        adj = false;
        if (nextface != FACING_NONE && Dir_Facing(track->Facing) != nextface) {
            adj = true;
        }

        /*
        **	Skip ahead the number of track steps required (limited only
        **	by track length). Set the unit to the new position and
        **	flag the unit accordingly.
        */
        Mark(MARK_UP);
        while (actual > PIXEL_LEPTON_W) {
            COORDINATE offset;
            DirType dir;

            actual -= PIXEL_LEPTON_W;

            offset = ptr[TrackIndex].Offset;
            if (offset || !TrackIndex) {
                dir = ptr[TrackIndex].Facing;
                COORDINATE prev_coord_diag = Coord;
                Coord = Smooth_Turn(offset, dir);

                /*
                **  TEMPORARY DEV DIAGNOSTIC — log per-tick Coord for vehicles
                **  emerging from a TDWEAP. The first few logged lines should
                **  show small smooth increments; a big jump would indicate
                **  the engine's track snap is producing the visible shift the
                **  user reports on TDWEAP exit. Per [[feedback-keep-diagnostics-until-v1]].
                */
                if ((TrackNumber == DriveClass::OUT_OF_WEAPON_FACTORY
                     || TrackNumber == DriveClass::OUT_OF_WEAPON_FACTORY_TD)
                    && In_Radio_Contact()
                    && Contact_With_Whom()
                    && Contact_With_Whom()->What_Am_I() == RTTI_BUILDING) {
                    BuildingClass const* bldg =
                        (BuildingClass const*)Contact_With_Whom();
                    if (*bldg == STRUCT_TDWEAP) {
                        static FILE* s_track = NULL;
                        if (s_track == NULL) {
                            char p[512];
                            const char* up = getenv("USERPROFILE");
                            if (up) snprintf(p, sizeof(p), "%s/Documents/CnCRemastered/tf_weap_track.log", up);
                            else strcpy(p, "tf_weap_track.log");
                            s_track = NULL; // TF DIAG OFF for release (was fopen; restore to re-enable)
                        }
                        if (s_track) {
                            fprintf(s_track,
                                "tick: idx=%d prev=(%u,%u) new=(%u,%u) "
                                "delta=(%d,%d) offset=(%u,%u) dir=%d head=(%u,%u)\n",
                                TrackIndex,
                                Coord_X(prev_coord_diag), Coord_Y(prev_coord_diag),
                                Coord_X(Coord), Coord_Y(Coord),
                                (int)Coord_X(Coord) - (int)Coord_X(prev_coord_diag),
                                (int)Coord_Y(Coord) - (int)Coord_Y(prev_coord_diag),
                                Coord_X(offset), Coord_Y(offset),
                                (int)dir,
                                Coord_X(Head_To_Coord()), Coord_Y(Head_To_Coord()));
                            fflush(s_track);
                        }
                    }
                }

                PrimaryFacing.Set(dir);

                /*
                **	See if "per cell" processing is necessary.
                */
                if (TrackIndex && RawTracks[tracknum - 1].Cell == TrackIndex) {
                    Mark(MARK_DOWN);
                    Per_Cell_Process(PCP_DURING);
                    if (!IsActive) {
                        return (false);
                    }
                    Mark(MARK_UP);
                }

                /*
                **	The unit could "jump tracks". Check to see if the unit should
                **	do so.
                */
                if (/**this != UNIT_GUNBOAT &&*/ nextface != FACING_NONE && adj
                    && RawTracks[tracknum - 1].Jump == TrackIndex && TrackIndex) {
                    TurnTrackType const* newtrack; // Proposed jump-to track.
                    int tnum;

                    tnum = (int)(Dir_Facing(track->Facing) * FACING_COUNT) + (int)nextface;
                    newtrack = &TrackControl[tnum];
                    if (newtrack->Track && RawTracks[newtrack->Track - 1].Entry) {
                        COORDINATE c = Head_To_Coord();
                        int oldspeed = Speed;

                        c = Adjacent_Cell(c, nextface);

                        switch (Can_Enter_Cell(Coord_Cell(c), nextface)) {
                        case MOVE_OK:
                            IsOnShortTrack = false; // Shouldn't be necessary, but...
                            TrackNumber = tnum;
                            track = newtrack;

                            tracknum = track->Track;
                            TrackIndex = RawTracks[tracknum - 1].Entry - 1; // Anticipate increment.
                            ptr = RawTracks[tracknum - 1].Track;
                            adj = false;

                            Stop_Driver();
                            IsDriving = true;
                            Per_Cell_Process(PCP_END);
                            IsDriving = false;
                            if (!IsActive)
                                return (false);
                            if (Start_Driver(c)) {
                                Set_Speed(oldspeed);
                                memmove((char*)&Path[0], (char*)&Path[1], CONQUER_PATH_MAX - 1);
                                Path[CONQUER_PATH_MAX - 1] = FACING_NONE;
                            } else {
                                Path[0] = FACING_NONE;
                                TrackNumber = -1;
                                actual = 0;
                            }
                            break;

                        case MOVE_CLOAK:
                            Map[c].Shimmer();
                            break;

                        case MOVE_TEMP:
#ifdef TOFIX
                            if (*this == UNIT_HARVESTER || *this == UNIT_TDHARV || !House->IsHuman) {
#else
                            if (!House->IsHuman) {
#endif
                                Map[c].Incoming(0, true, true);
                            }
                            break;
                        }
                    }
                }
                TrackIndex++;

            } else {
                actual = 0;
                Coord = Head_To_Coord();
                Stop_Driver();
                TrackNumber = -1;
                TrackIndex = 0;

                /*
                **	Perform "per cell" activities.
                */
                Mark(MARK_DOWN);
                Per_Cell_Process(PCP_END);
                if (!IsActive)
                    return (false);
                Mark(MARK_UP);

                break;
            }
        }
        if (IsActive) {
            Mark(MARK_DOWN);
        }
    }

    /*
    **	Replace any remainder back into the unit's movement
    **	accumulator to be processed next pass.
    */
    SpeedAccum = actual;
    return (true);
}

/***********************************************************************************************
 * DriveClass::Per_Cell_Process -- Handles when unit finishes movement into a cell.            *
 *                                                                                             *
 *    This routine is called when a unit has mostly or completely                              *
 *    entered a cell. The unit might be in the middle of a movement track                      *
 *    when this routine is called. It's primary purpose is to perform                          *
 *    sighting and other "per cell" activities.                                                *
 *                                                                                             *
 * INPUT:   why   -- Specifies the circumstances under which this routine was called.          *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   11/03/1993 JLB : Created.                                                                 *
 *   03/30/1994 JLB : Revamped for track system.                                               *
 *   04/15/1994 JLB : Converted to member function.                                            *
 *   06/18/1994 JLB : Converted to virtual function.                                           *
 *   06/18/1994 JLB : Distinguishes between center and near-center conditions.                 *
 *=============================================================================================*/
void DriveClass::Per_Cell_Process(PCPType why)
{
    assert(IsActive);

    if (why == PCP_END) {
        CELL cell = Coord_Cell(Coord);

        /*
        **	Check to see if it has reached its destination. If so, then clear the NavCom
        **	regardless of the remaining path list.
        */
        if (As_Cell(NavCom) == cell) {
            IsTurretLockedDown = false;
            NavCom = TARGET_NONE;
            Path[0] = FACING_NONE;
        }

        Lay_Track();
    }

    FootClass::Per_Cell_Process(why);
}

/***********************************************************************************************
 * DriveClass::Find_Give_Way_Cell -- Nearest free cell to clear a head-on chokepoint deadlock. *
 *                                                                                             *
 *    Part of the v2.2.3 1-wide-bridge give-way fix. When two allied vehicles deadlock         *
 *    nose-to-nose on a chokepoint, the deterministic loser calls this to find a cell to       *
 *    divert to so the winner can pass. We only accept a genuinely FREE (MOVE_OK) cell that    *
 *    moves us AWAY from the oncoming unit -- this is what avoids the earlier reverted          *
 *    attempt's failure mode, where backing straight off the bridge rammed the unit into its   *
 *    own follower. If nothing free is found (we're boxed in), return 0 and the caller just     *
 *    holds and retries instead of churning.                                                   *
 *                                                                                             *
 * INPUT:   blocker -- the oncoming allied vehicle we are deadlocked against.                  *
 *                                                                                             *
 * OUTPUT:  A reachable free cell to divert to, or 0 if none.                                  *
 *                                                                                             *
 * WARNINGS:   Must stay deterministic (no Random_Pick) -- runs in the lockstep sim.           *
 *=============================================================================================*/
CELL DriveClass::Find_Give_Way_Cell(TechnoClass const* blocker) const
{
    if (blocker == NULL) {
        return (0);
    }

    const int GIVEWAY_MAX_RADIUS = 3;
    CELL here = Coord_Cell(Center_Coord());
    int here_dist = ::Distance(Cell_Coord(here), blocker->Center_Coord());

    CELL best = 0;
    int best_dist = here_dist; // candidate must beat this (strictly move away from the blocker)

    for (int radius = 1; radius <= GIVEWAY_MAX_RADIUS && best == 0; radius++) {
        for (FacingType face = FACING_N; face < FACING_COUNT; face++) {

            /*
            **	Walk 'radius' cells along this facing, bailing if we leave the map.
            */
            CELL c = here;
            bool ok = true;
            for (int step = 0; step < radius; step++) {
                CELL nc = Adjacent_Cell(c, face);
                if (!Map.In_Radar(nc)) {
                    ok = false;
                    break;
                }
                c = nc;
            }
            if (!ok) {
                continue;
            }

            /*
            **	Only a truly empty cell counts -- never divert onto a friendly (that is the
            **	follower-ramming trap). And it must take us further from the oncoming unit so
            **	we actually clear its path rather than sidestep into it.
            */
            if (Can_Enter_Cell(c, face) != MOVE_OK) {
                continue;
            }
            int d = ::Distance(Cell_Coord(c), blocker->Center_Coord());
            if (d > best_dist) {
                best_dist = d;
                best = c;
            }
        }
    }

    return (best);
}

/***********************************************************************************************
 * DriveClass::Give_Way_Decision -- How should this vehicle yield a 1-wide chokepoint?         *
 *                                                                                             *
 *    Heart of the v2.2.3 give-way fix. Looks ahead along the route to NavCom and finds the    *
 *    1-wide (terrain-pinched) corridor we are about to traverse, then decides via two layers: *
 *      1. RESERVATION (authoritative): when a vehicle commits to the corridor it stamps every  *
 *         corridor cell with its travel direction + the current Frame (CellClass::ChokeClaim*).*
 *         An oncoming vehicle that reads an ACTIVE claim in the opposing direction yields BEFORE*
 *         it enters -- corridor-wide, sticky ownership that the per-tick heuristic lacked, which*
 *         is what fixes near-simultaneous entry (both leads commit before either is the owner). *
 *         The claim ages out on its own ~TTL frames after the last unit clears (no refcount to  *
 *         miscount, no pointer to code/decode, all int -> lockstep-deterministic).             *
 *      2. LIVE-UNIT id tiebreak (pre-claim fallback): if no claim exists yet, a HIGHER-id      *
 *         oncoming allied vehicle makes the lower-id unit yield. Synced total order, so exactly *
 *         one side stamps first; the claim then reinforces the same winner.                     *
 *                                                                                             *
 *    The yield FORM depends on where we are, which is what the first (frozen-in-lane) cut got *
 *    wrong: holding only clears the winner's path if we are NOT in the winner's lane.         *
 *      - On wide ground (we have not entered the pinch): HOLD here -- waiting is harmless and  *
 *        keeps us (and the column behind us) off the bridge until the winner passes.          *
 *      - Already inside the pinch (we ARE blocking the winner): RETREAT -- back out toward our *
 *        own side so the lane frees; once we reach wide ground this flips to HOLD.             *
 *                                                                                             *
 * INPUT:   winner_out -- if non-NULL, receives the oncoming unit we are yielding to.          *
 *                                                                                             *
 * OUTPUT:  0 = proceed (no conflict), 1 = hold in place, 2 = retreat to clear the lane.       *
 *                                                                                             *
 * WARNINGS:   Must stay deterministic (no Random_Pick) -- runs in the lockstep sim.           *
 *=============================================================================================*/
int DriveClass::Give_Way_Decision(TechnoClass** winner_out) const
{
    if (winner_out != NULL) {
        *winner_out = NULL;
    }
    if (!Target_Legal(NavCom)) {
        return (0);
    }

    CELL here = Coord_Cell(Center_Coord());

    /*
    **	Two distinct directions, and conflating them caused a retreat storm:
    **	  - navcell/myface: where we are ACTUALLY heading right now (current NavCom). The corridor
    **	    scan and narrow tests use this, so a unit mid-retreat scans toward its back-off cell and
    **	    the retreat actually executes (instead of re-deciding "retreat" in place forever).
    **	  - myintentface: the direction of our REAL queued order (NavQueue[0] while on a give-way
    **	    detour). Only the opposing-direction test uses this, so a unit that has reversed to yield
    **	    doesn't misread its own same-direction followers as oncoming traffic (the wedge bug).
    */
    CELL navcell = As_Cell(NavCom);
    if (here == navcell) {
        return (0);
    }
    TARGET my_intent = Target_Legal(NavQueue[0]) ? NavQueue[0] : NavCom;

    const int SCAN_MAX = 28;         // scan far enough to read a claim ACROSS a long single-file lane
    const int COMMIT_DIST = 18;      // claim the corridor from well out, so ANY owning-direction unit still
                                     // on the lane keeps the lock alive -- the corridor stays locked to one
                                     // direction until that WHOLE column has cleared, then hands over. This
                                     // is the prevention that stops the other column butting in mid-column.
    const int CHOKE_CLAIM_TTL = 75;  // claim stays active this many frames after its last assertion, so a
                                     // lagging straggler does not drop the lock mid-column (it hands over a
                                     // beat after the whole column clears, not between every spaced unit)
    FacingType myface = Dir_Facing(::Direction(Cell_Coord(here), Cell_Coord(navcell)));
    FacingType myintentface = (my_intent != NavCom && Target_Legal(my_intent))
                                  ? Dir_Facing(::Direction(Cell_Coord(here), Cell_Coord(As_Cell(my_intent))))
                                  : myface;

    /*
    **	Are we ourselves standing in a 1-wide pinch right now? Decided up front because it drives
    **	both the yield FORM (hold on open ground vs retreat from inside the lane) and whether a
    **	rival merely poised at the far mouth can make us yield (it can't once we already own the
    **	corridor by being inside it).
    */
    CELL lh = Adjacent_Cell(here, (FacingType)((myface - 2) & 0x07));
    CELL rh = Adjacent_Cell(here, (FacingType)((myface + 2) & 0x07));
    bool here_narrow = (!Map.In_Radar(lh) || Can_Enter_Cell(lh) == MOVE_NO)
                       && (!Map.In_Radar(rh) || Can_Enter_Cell(rh) == MOVE_NO);

    /*
    **	Is an opposing-facing vehicle directly in the cell we are about to move into? This is the
    **	"we are physically blocking the winner head-on" signal, used twice below: (a) the
    **	both-leads-inside tiebreak, and (b) the yield FORM -- a unit that merely STOPS on the winner's
    **	exit cell still blocks it, so when we are nose-to-nose with the winner we must STEP ASIDE
    **	(retreat) to clear the lane, not just halt, even on open ground.
    */
    CELL ahead_cell = Adjacent_Cell(here, myface);
    TechnoClass* front_unit = Map.In_Radar(ahead_cell) ? Map[ahead_cell].Cell_Techno() : NULL;
    bool head_on_ahead = false;
    if (front_unit != NULL && front_unit != this && front_unit->What_Am_I() == RTTI_UNIT
        && House->Is_Ally(front_unit)) {
        FootClass const* ff = (FootClass const*)front_unit;
        TARGET fi = Target_Legal(ff->NavQueue[0]) ? ff->NavQueue[0] : ff->NavCom;
        if (Target_Legal(fi)) {
            FacingType frontface = Dir_Facing(::Direction(ff->Center_Coord(), As_Coord(fi)));
            int fdiff = (myintentface - frontface) & 0x07;
            head_on_ahead = (fdiff >= 3 && fdiff <= 5);
        }
    }

    /*
    **	Walk the route ahead, find the 1-wide corridor we are about to traverse, and decide whether
    **	an opposing column is laying claim to it -- crucially including rivals still on the FAR
    **	APPROACH, so we stand down before either group reaches the bridge rather than nose-to-nose
    **	on it. corridor_start is our distance to the near mouth; corridor_end is the far mouth.
    */
    CELL c = here;
    int corridor_start = -1; // scan index where the narrow run begins (~ our distance to the near mouth)
    int corridor_end = -1;   // scan index of the first open cell after the narrow run (the far mouth)
    TechnoClass* yield_to = NULL;
    bool yield = false;
    bool opposing_claim = false;      // an active reservation is held against us by an oncoming column
    bool own_claim = false;           // our own column already owns this corridor -- claim is authoritative

    CELL corridor_cells[SCAN_MAX];        // the narrow cells on our route, to stamp our claim onto
    FacingType corridor_faces[SCAN_MAX];  // the LOCAL step direction through each (handles a bent pinch)
    int corridor_count = 0;

    /*
    **	The claim direction is the TRAVERSAL direction THROUGH each pinch cell -- the local step we
    **	take into it -- NOT the direction to our final destination. Those differ when the goal is off
    **	the pinch axis: every unit funnelling through an N-S pinch toward a western goal has
    **	intentface = west, so a uniform per-corridor "west" stamp would make two opposing columns
    **	invisible to each other. Stamping the LOCAL step per cell is inherently the traversal direction
    **	and also follows a bent corridor (a lake corner) where the flow direction changes along it.
    */

    const int FAR_APPROACH = 6; // how far past the corridor to keep watching for a rival heading in

    for (int i = 0; i < SCAN_MAX; i++) {
        /*
        **	Follow the unit's ACTUAL planned path through the terrain when we have one, instead of a
        **	straight line to the destination. A route to an off-axis goal (e.g. an inland spread
        **	cell) often bends down a 1-wide corridor first; a straight-line scan walks diagonally
        **	off the corridor and misses the pinch entirely. Past the end of the stored path we fall
        **	back to the straight-line heading.
        */
        FacingType f = (i < (int)ARRAY_SIZE(Path) && Path[i] != FACING_NONE)
                           ? Path[i]
                           : Dir_Facing(::Direction(Cell_Coord(c), Cell_Coord(navcell)));
        CELL nc = Adjacent_Cell(c, f);
        if (!Map.In_Radar(nc)) {
            break;
        }

        /*
        **	Narrow (terrain pinch) test: both cells perpendicular to travel are impassable terrain,
        **	so two units can't pass abreast. Friendly occupancy reads MOVE_TEMP, not MOVE_NO, so
        **	this keys on geography, not transient traffic.
        */
        CELL lc = Adjacent_Cell(nc, (FacingType)((f - 2) & 0x07));
        CELL rc = Adjacent_Cell(nc, (FacingType)((f + 2) & 0x07));
        bool narrow = (!Map.In_Radar(lc) || Can_Enter_Cell(lc) == MOVE_NO)
                      && (!Map.In_Radar(rc) || Can_Enter_Cell(rc) == MOVE_NO);
        if (narrow && corridor_start < 0) {
            corridor_start = i;
        }
        if (!narrow && corridor_start >= 0 && corridor_end < 0) {
            corridor_end = i; // first open cell after the narrow run = far mouth
        }

        /*
        **	Chokepoint reservation (v2.2.3). Record each narrow cell so we can stamp our claim on the
        **	whole corridor below, and -- crucially -- READ any existing claim here. An ACTIVE claim
        **	(asserted within CHOKE_CLAIM_TTL frames) whose travel direction opposes ours (3-5 eighths
        **	apart) means an oncoming column already owns the lane: we yield before we ever reach the
        **	pinch. This is the atomic, corridor-wide, race-free ownership the per-tick live-unit
        **	heuristic below cannot provide on near-simultaneous entry. A same-direction claim is our
        **	own column and is ignored.
        */
        if (narrow && corridor_count < SCAN_MAX) {
            corridor_cells[corridor_count] = nc;
            corridor_faces[corridor_count] = f; // local step direction through this pinch cell
            corridor_count++;
        }
        /*
        **	Read any claim on THIS cell -- the 1-wide pinch OR a reserved MOUTH cell just outside it
        **	(stamped below). Reading the mouths is what makes an opposing column halt one cell back from
        **	the entrance/exit instead of parking on it. Generic: a cell only carries a claim if it is a
        **	pinch-or-mouth cell of some corridor.
        */
        {
            CellClass const& ccell = Map[nc];
            int age = Frame - (int)ccell.ChokeClaimFrame;
            if (ccell.ChokeClaimFrame != 0 && age >= 0 && age <= CHOKE_CLAIM_TTL) {
                int cdiff = (f - (FacingType)ccell.ChokeClaimDir) & 0x07;
                if (cdiff >= 3 && cdiff <= 5) {
                    if (here_narrow) {
                        /*
                        **	We are physically INSIDE the pinch and an opposing claim lies ahead. Default:
                        **	the unit already in the lane has priority to EXIT, so push through (own_claim)
                        **	and the opposing column -- still back at the mouth -- waits. This rescues a unit
                        **	that nosed in before the claim went up.
                        **
                        **	EXCEPTION: if an opposing-facing vehicle is RIGHT IN FRONT of us, then both
                        **	columns' LEADS are inside head-on and exactly one must give -- if both push,
                        **	neither moves (the deadlock this exception fixes). Tiebreak by id (synced,
                        **	total order): the HIGHER id pushes through, the LOWER id backs out one cell so
                        **	the higher can pass, then re-enters. The cell behind the loser is normally free
                        **	(its column funnels in from a wider mouth), so Find_Give_Way_Cell succeeds.
                        */
                        if (head_on_ahead && As_Target() < front_unit->As_Target()) {
                            opposing_claim = true; // we lose the tiebreak -> back out so the higher id passes
                            yield_to = front_unit;
                            break;
                        }
                        own_claim = true;
                    } else {
                        opposing_claim = true;
                        TechnoClass* owner = Map[nc].Cell_Techno();
                        if (owner != NULL && owner != this && owner->What_Am_I() == RTTI_UNIT
                            && House->Is_Ally(owner)) {
                            yield_to = owner; // best-effort blocker for the retreat back-off target
                        }
                        break;
                    }
                }
                if (cdiff <= 1 || cdiff == 7) {
                    /*
                    **	A SAME-direction claim (within 1 eighth): our own column already owns this lane.
                    **	The claim is authoritative, so we PROCEED and must IGNORE the live-unit id-tiebreak
                    **	below. Without this, interleaved id ranges (two groups built alternately, so a
                    **	column's units do NOT share a contiguous id block) make the id-rule and the claim
                    **	pick OPPOSITE winners -- the owning column's front units yield to the oncoming
                    **	column by id while the oncoming column yields to the claim, and every unit holds =
                    **	stalemate. Keep scanning (do not break) so the whole corridor is re-stamped below.
                    */
                    own_claim = true;
                }
            }
        }

        /*
        **	Is there an opposing allied vehicle here? "Opposing" = heading toward its own queued
        **	destination roughly opposite ours (facing difference of 3-5 eighths, > 135 degrees). Skipped
        **	entirely once we own an active claim on this corridor -- the claim is authoritative and the
        **	id-tiebreak must not be allowed to contradict it (the interleaved-id stalemate).
        */
        TechnoClass* t = own_claim ? NULL : Map[nc].Cell_Techno();
        if (t != NULL && t != this && t->What_Am_I() == RTTI_UNIT && House->Is_Ally(t)) {
            FootClass const* ft = (FootClass const*)t;
            TARGET t_intent = Target_Legal(ft->NavQueue[0]) ? ft->NavQueue[0] : ft->NavCom;
            if (Target_Legal(t_intent)) {
                FacingType tf = Dir_Facing(::Direction(ft->Center_Coord(), As_Coord(t_intent)));
                int diff = (myintentface - tf) & 0x07;
                bool opposing = (diff >= 3 && diff <= 5);
                if (opposing && narrow) {
                    /*
                    **	A rival is INSIDE the corridor. We yield. When we are also inside (a head-on
                    **	in the pinch) this means BOTH sides back out -- which proved more robust than
                    **	"only the lower id backs out": both columns reverse together and separate,
                    **	whereas one-sided yielding just wedges a boxed-in loser while the winner shoves.
                    */
                    yield = true;
                    yield_to = t;
                    break;
                }
                if (opposing && corridor_end >= 0) {
                    /*
                    **	A rival is on the FAR approach, heading for the same corridor from the other
                    **	side, and nobody is inside yet. The lower id stands down so the other side
                    **	claims it. Id is used here ON PURPOSE rather than "who's closer": a distance
                    **	test flaps every tick as the columns jostle (a unit yields, edges forward,
                    **	thinks it's now closer, re-clashes, yields again -- the advance/backtrack
                    **	churn). Ids don't change, so the owner is STABLE; and because each group's
                    **	units share a contiguous id range, a whole column yields together. Once a
                    **	leader actually enters, the occupancy rule above takes over.
                    */
                    if (As_Target() < t->As_Target()) {
                        yield = true;
                        yield_to = t;
                    }
                    break; // the nearest far-side rival settles it
                }
            }
        }

        if ((corridor_end >= 0 && (i - corridor_end) >= FAR_APPROACH) || nc == navcell) {
            break; // looked far enough past the corridor, or arrived
        }
        c = nc;
    }

    /*
    **	An ACTIVE opposing claim is authoritative -- an oncoming column owns the lane, so yield. The
    **	live-unit test above (occupancy + stable-id tiebreak) remains as the pre-claim fallback for
    **	the brief approach window before anyone has stamped, and for the already-working
    **	one-column-enters-first case. Either way the FORM is the same.
    */
    if (opposing_claim || (yield && !own_claim)) {
        /*
        **	If we are nose-to-nose with the winner (head_on_ahead) we are sitting on the cell it must
        **	move into, so a plain HOLD would keep blocking it. Hand Find_Give_Way_Cell that unit so we
        **	step aside instead. Fall back to the claim/live owner otherwise.
        */
        if (head_on_ahead && front_unit != NULL) {
            yield_to = front_unit;
        }
        if (winner_out != NULL) {
            *winner_out = yield_to;
        }
#if TF_DEV_BUILD
        if (House && House->IsHuman) {
            static FILE* tf_hold_log = NULL;
            static bool tf_hold_tried = false;
            if (!tf_hold_tried) {
                tf_hold_tried = true;
                const char* h = getenv("USERPROFILE");
                if (h == NULL)
                    h = getenv("HOME");
                if (h != NULL) {
                    char hp[512];
                    snprintf(hp, sizeof(hp), "%s/Documents/CnCRemastered/tf_astar.log", h);
                    tf_hold_log = fopen(hp, "a");
                }
            }
            if (tf_hold_log != NULL) {
                CELL mypos = Coord_Cell(Center_Coord());
                const char* me =
                    (Techno_Type_Class() && Techno_Type_Class()->IniName) ? Techno_Type_Class()->IniName : "<?>";
                fprintf(tf_hold_log, "%s: %s pos=(%d,%d) intentface=%d here_narrow=%d myid=%d\n",
                        opposing_claim ? "HOLD-claim" : "HOLD-unit", me, (int)Cell_X(mypos), (int)Cell_Y(mypos),
                        (int)myintentface, (int)here_narrow, (int)As_Target());
                fflush(tf_hold_log);
            }
        }
#endif
        /*
        **	HOLD STILL while waiting: a unit yielding to a claim that is NOT physically blocking the
        **	lane just stops and waits its turn -- no shuffling. Only STEP ASIDE (retreat) when we are
        **	actually in the way: inside the pinch (here_narrow) or nose-to-nose with the winner
        **	(head_on_ahead), where a plain stop would keep blocking it. Prevention (claim the whole
        **	lane from well out) is what keeps the losing column from ever entering and getting boxed,
        **	so the heavy whole-column cascade is no longer needed for the common case.
        */
        return ((here_narrow || head_on_ahead) ? 2 : 1);
    }

    /*
    **	General head-on backstop (covers what the corridor reservation does not): if we are nose-to-
    **	nose with an opposing-facing ally on OPEN ground -- the approach-funnel collision where a unit
    **	EXITING the pinch meets one ENTERING, or any two units wanting the same cell head-on -- the
    **	corridor logic never engages (neither is in a 1-wide cell), so without this both just ram and
    **	MOVE_NO-lock. The lower id steps aside so the higher proceeds; strict id compare => exactly one
    **	gives, no mutual jitter. Corridor OWNERS (own_claim) are exempt -- they hold their lane and the
    **	opponent is the one that gives.
    */
    if (head_on_ahead && !own_claim && front_unit != NULL && As_Target() < front_unit->As_Target()) {
        if (winner_out != NULL) {
            *winner_out = front_unit;
        }
#if TF_DEV_BUILD
        if (House && House->IsHuman) {
            static FILE* tf_so_log = NULL;
            static bool tf_so_tried = false;
            if (!tf_so_tried) {
                tf_so_tried = true;
                const char* h = getenv("USERPROFILE");
                if (h == NULL)
                    h = getenv("HOME");
                if (h != NULL) {
                    char sp[512];
                    snprintf(sp, sizeof(sp), "%s/Documents/CnCRemastered/tf_astar.log", h);
                    tf_so_log = fopen(sp, "a");
                }
            }
            if (tf_so_log != NULL) {
                CELL mypos = Coord_Cell(Center_Coord());
                const char* me =
                    (Techno_Type_Class() && Techno_Type_Class()->IniName) ? Techno_Type_Class()->IniName : "<?>";
                fprintf(tf_so_log, "SIDESTEP-headon: %s pos=(%d,%d) intentface=%d myid=%d vsid=%d\n", me,
                        (int)Cell_X(mypos), (int)Cell_Y(mypos), (int)myintentface, (int)As_Target(),
                        (int)front_unit->As_Target());
                fflush(tf_so_log);
            }
        }
#endif
        return (2); // step aside so the higher-id unit can pass, then resume our route
    }

    /*
    **	No conflict: commit. Stamp our travel direction onto every corridor cell (Frame-tagged) so an
    **	oncoming column reads the claim and yields before it enters. Gated on COMMIT_DIST so a unit
    **	still far from the mouth does not lock a corridor it will not reach for a while; a unit already
    **	inside (here_narrow) always re-asserts, since it owns the lane it is traversing. Writing to the
    **	global Map from this const method is fine -- it is shared deterministic cell state, not *this.
    **
    **	CROSSING GATE (v2.2.3 fix): only (re)stamp when we have actually moved into a NEW cell since our
    **	last stamp. Start_Of_Move is called every tick while a unit is trying to advance, so a unit that
    **	is STALLED (no path, blocked, waiting on dest contention) used to re-assert its claim every tick,
    **	keeping it alive forever -- CHOKE_CLAIM_TTL never expired and the whole column behind it locked up
    **	permanently. By stamping only on a real cell-crossing, a moving column keeps the lane locked (it
    **	crosses cells well within the TTL) while a HALTED unit's claim ages out and the queue recovers.
    */
    if (corridor_count > 0
        && here != LastClaimCell
        && (here_narrow || own_claim || (corridor_start >= 0 && corridor_start <= COMMIT_DIST))) {
        LastClaimCell = here;
        for (int k = 0; k < corridor_count; k++) {
            Map[corridor_cells[k]].ChokeClaimFrame = (unsigned int)Frame;
            Map[corridor_cells[k]].ChokeClaimDir = (unsigned char)corridor_faces[k];
        }
        /*
        **	Also reserve the two MOUTH cells -- one cell before the entrance, one after the exit --
        **	derived generically from the ends of whatever narrow run we found (any length, any shape).
        **	Stamped with the flow direction at that end, so an opposing column reads the mouth and halts
        **	a cell back rather than parking ON the entrance/exit and blocking it (the lead-on-the-mouth
        **	jam). The reading loop above now consults every scanned cell, so these are honoured.
        */
        CELL near_mouth = Adjacent_Cell(corridor_cells[0], (FacingType)((corridor_faces[0] + 4) & 0x07));
        if (Map.In_Radar(near_mouth)) {
            Map[near_mouth].ChokeClaimFrame = (unsigned int)Frame;
            Map[near_mouth].ChokeClaimDir = (unsigned char)corridor_faces[0];
        }
        CELL exit_mouth = Adjacent_Cell(corridor_cells[corridor_count - 1], corridor_faces[corridor_count - 1]);
        if (Map.In_Radar(exit_mouth)) {
            Map[exit_mouth].ChokeClaimFrame = (unsigned int)Frame;
            Map[exit_mouth].ChokeClaimDir = (unsigned char)corridor_faces[corridor_count - 1];
        }
#if TF_DEV_BUILD
        if (House && House->IsHuman) {
            static FILE* tf_claim_log = NULL;
            static bool tf_claim_tried = false;
            if (!tf_claim_tried) {
                tf_claim_tried = true;
                const char* h = getenv("USERPROFILE");
                if (h == NULL)
                    h = getenv("HOME");
                if (h != NULL) {
                    char cp[512];
                    snprintf(cp, sizeof(cp), "%s/Documents/CnCRemastered/tf_astar.log", h);
                    tf_claim_log = fopen(cp, "a");
                }
            }
            if (tf_claim_log != NULL) {
                const char* me =
                    (Techno_Type_Class() && Techno_Type_Class()->IniName) ? Techno_Type_Class()->IniName : "<?>";
                fprintf(tf_claim_log, "CLAIM: %s cells=%d dir0=%d dirN=%d frame=%d start=%d own=%d myid=%d\n", me,
                        corridor_count, (int)(corridor_count > 0 ? corridor_faces[0] : 0),
                        (int)(corridor_count > 0 ? corridor_faces[corridor_count - 1] : 0), (int)Frame,
                        corridor_start, (int)own_claim, (int)As_Target());
                fflush(tf_claim_log);
            }
        }
#endif
    }
    return (0);
}

/***********************************************************************************************
 * DriveClass::Start_Of_Move -- Tries to get a unit to advance toward cell.                    *
 *                                                                                             *
 *    This will try to start a unit advancing toward the cell it is                            *
 *    facing. It will check for and handle legality and reserving of the                       *
 *    necessary cell.                                                                          *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  true/false; Should this routine be called again because                            *
 *                      initial start operation is temporarily delayed?                        *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   02/02/1992 JLB : Created.                                                                 *
 *   10/18/1993 JLB : This should be called repeatedly until HeadTo is not NULL.               *
 *   03/16/1994 JLB : Revamped for track logic.                                                *
 *   04/15/1994 JLB : Converted to member function.                                            *
 *   06/19/1995 JLB : Fixed so that it won't fire on ground unnecessarily.                     *
 *   07/13/1995 JLB : Handles bumping into cloaked objects.                                    *
 *   09/22/1995 JLB : Breaks out of hopeless hunt mode.                                        *
 *   07/10/1996 JLB : Sets scan limit if necessary.                                            *
 *=============================================================================================*/
bool DriveClass::Start_Of_Move(void)
{
    assert(IsActive);

    FacingType facing; // Direction movement will commence.
    DirType dir;       // Desired actual facing toward destination.
    int facediff;      // Difference between current and desired facing.
    int speed;         // Speed of unit.
    CELL destcell;     // Cell of destination.
    LandType ground;   // Ground unit is entering.
    COORDINATE dest;   // Destination coordinate.

    facing = Path[0];

    if (!Target_Legal(NavCom) && facing == FACING_NONE) {
        IsTurretLockedDown = false;
        Stop_Driver();
        if (Mission == MISSION_MOVE) {
            Enter_Idle_Mode();
        }
        return (false); // Why is it calling this routine!?!
    }

    /*
    **	Give-way (v2.2.3): if a higher-id allied vehicle is coming the other way through a 1-wide
    **	stretch ahead, the lower-id unit yields until the whole oncoming column has passed, then
    **	advances in one clean run. Stateless and re-checked each tick, so no ping-pong and no
    **	savegame growth. HOLD if we are still on open ground (stay off the bridge); RETREAT if we
    **	are already inside the pinch and blocking the winner's lane (back out to free it -- once
    **	on open ground the decision flips to HOLD and we wait there).
    */
    if (Target_Legal(NavCom)) {
        TechnoClass* gw_winner = NULL;
        int gw = Give_Way_Decision(&gw_winner);
        if (gw == 1) {
            Stop_Driver();
            return (false);
        }
        if (gw == 2) {
            CELL back = Find_Give_Way_Cell(gw_winner);
            if (back != 0) {
                TARGET original = NavCom;
#if TF_DEV_BUILD
                if (House && House->IsHuman) {
                    static FILE* tf_give_log = NULL;
                    static bool tf_give_tried = false;
                    if (!tf_give_tried) {
                        tf_give_tried = true;
                        const char* h = getenv("USERPROFILE");
                        if (h == NULL)
                            h = getenv("HOME");
                        if (h != NULL) {
                            char gp[512];
                            snprintf(gp, sizeof(gp), "%s/Documents/CnCRemastered/tf_astar.log", h);
                            tf_give_log = fopen(gp, "a");
                        }
                    }
                    if (tf_give_log != NULL) {
                        CELL mypos = Coord_Cell(Center_Coord());
                        const char* me = (Techno_Type_Class() && Techno_Type_Class()->IniName)
                                             ? Techno_Type_Class()->IniName
                                             : "<?>";
                        fprintf(tf_give_log, "GIVEWAY-retreat: loser=%s pos=(%d,%d) -> back=(%d,%d) myid=%d theirid=%d\n",
                                me, (int)Cell_X(mypos), (int)Cell_Y(mypos), (int)Cell_X(back), (int)Cell_Y(back),
                                (int)As_Target(), (int)gw_winner->As_Target());
                        fflush(tf_give_log);
                    }
                }
#endif
                Assign_Destination(::As_Target(back));
                Queue_Navigation_List(original);
            }
            Stop_Driver();
            return (false);
        }
    }

    /*
    **	Reduce the path length if the target is a unit and the
    **	range to the unit is less than the precalculated path steps.
    */
    if (facing != FACING_NONE) {
        int dist;

        if (Is_Target_Vessel(NavCom) || Is_Target_Unit(NavCom) || Is_Target_Infantry(NavCom)) {
            dist = Lepton_To_Cell((LEPTON)Distance(NavCom));

            if (dist < ARRAY_SIZE(Path)) {
                Path[dist] = FACING_NONE;
                facing = Path[0]; // Maybe needed.
            }
        }
    }

    /*
    **	If the path is invalid at this point, then generate one. If
    **	generating a new path fails, then abort NavCom.
    */
    if (facing == FACING_NONE) {

        /*
        **	If after a path search, there is still no valid path, then set the
        **	NavCom to null and let the script take care of assigning a new
        **	navigation target.
        */
        if (PathDelay != 0) {
            return (false);
        }

        if (!Basic_Path()) {

#if TF_DEV_BUILD
            /*
            ** TF DEV: patient-queue chokepoint diagnostic (v2.2.3 investigation). Logs every time a
            ** HUMAN move unit hits the no-path branch: which sub-branch will fire, Distance(NavCom)
            ** vs Rule.CloseEnoughDistance, and the Can_Enter_Cell type of the cell toward the
            ** destination AND straight ahead. Key discriminator for the choke jam:
            **   MOVE_TEMP (4)         = a STOPPED friendly is in the way (won't clear on its own)
            **   MOVE_MOVING_BLOCK (2) = a MOVING friendly (will clear; A* already routes through it)
            **   MOVE_NO (5)           = terrain / permanent block
            ** Appends to the same tf_astar.log stream as the A* fallback tally. Compiled out of
            ** release builds (TF_DEV_BUILD=0). Read NavCom BEFORE any Assign_Destination below.
            */
            if (House && House->IsHuman) {
                static FILE* tf_choke_log = NULL;
                static bool tf_choke_tried = false;
                if (!tf_choke_tried) {
                    tf_choke_tried = true;
                    const char* h = getenv("USERPROFILE");
                    if (h == NULL)
                        h = getenv("HOME");
                    if (h != NULL) {
                        char p[512];
                        snprintf(p, sizeof(p), "%s/Documents/CnCRemastered/tf_astar.log", h);
                        tf_choke_log = fopen(p, "a");
                    }
                }
                if (tf_choke_log != NULL) {
                    static const char* const move_names[MOVE_COUNT] = {
                        "OK", "CLOAK", "MOVING_BLOCK", "DESTROYABLE", "TEMP", "NO"};
                    CELL here = Coord_Cell(Center_Coord());
                    CELL navcell = As_Cell(NavCom);
                    int distlep = (int)Distance(NavCom);
                    int distcell = Lepton_To_Cell((LEPTON)Distance(NavCom));
                    FacingType navface = Dir_Facing(Direction(NavCom));
                    CELL towardnav = Adjacent_Cell(here, navface);
                    MoveType navmove = Map.In_Radar(towardnav) ? Can_Enter_Cell(towardnav, navface) : MOVE_NO;
                    FacingType aheadface = Dir_Facing(PrimaryFacing);
                    CELL ahead = Adjacent_Cell(here, aheadface);
                    MoveType aheadmove = Map.In_Radar(ahead) ? Can_Enter_Cell(ahead, aheadface) : MOVE_NO;
                    bool closeMove = (!Is_On_Priority_Mission() && Distance(NavCom) < Rule.CloseEnoughDistance
                                      && (Mission == MISSION_MOVE || Mission == MISSION_GUARD_AREA));
                    const char* branch =
                        closeMove ? "ABANDON-close" : (TryTryAgain > 0 ? "RETRY" : "ABANDON-giveup");
                    const char* who = (Techno_Type_Class() && Techno_Type_Class()->IniName)
                                          ? Techno_Type_Class()->IniName
                                          : "<?>";
                    fprintf(tf_choke_log,
                            "CHOKE: unit=%s pos=(%d,%d) nav=(%d,%d) dist=%d(cell %d) closeenough=%d "
                            "towardNav=%s aheadFacing=%s try=%d -> %s\n",
                            who, (int)Cell_X(here), (int)Cell_Y(here), (int)Cell_X(navcell), (int)Cell_Y(navcell),
                            distlep, distcell, (int)Rule.CloseEnoughDistance, move_names[navmove],
                            move_names[aheadmove], TryTryAgain, branch);
                    fflush(tf_choke_log);
                }
            }
#endif

            /*
            **	Give-way (v2.2.3): break a 1-wide head-on deadlock. Basic_Path just failed. If the
            **	cell toward our destination is held by an ONCOMING allied vehicle (the head-on
            **	MOVE_NO case in UnitClass::Can_Enter_Cell), the deterministic loser -- the unit with
            **	the lower As_Target() id, which is synced so exactly one side yields and it's
            **	lockstep-safe -- diverts to a free cell to let the winner pass, then auto-resumes its
            **	original order via the nav queue. The winner does NOT move; it keeps retrying below
            **	and flows through the instant the loser clears. Requiring a MOVE_OK divert cell (see
            **	Find_Give_Way_Cell) is what keeps this from repeating the reverted back-off attempt
            **	that rammed units into their own followers: a boxed-in loser finds nothing here and
            **	falls through to hold/retry. Vehicles only (this is DriveClass; infantry stack
            **	sub-cell and don't deadlock).
            */
            if (Target_Legal(NavCom)) {
                FacingType navface = Dir_Facing(Direction(NavCom));
                CELL aheadcell = Adjacent_Cell(Coord_Cell(Center_Coord()), navface);
                if (Map.In_Radar(aheadcell) && Can_Enter_Cell(aheadcell, navface) == MOVE_NO) {
                    TechnoClass* blocker = Map[aheadcell].Cell_Techno();
                    if (blocker != NULL && blocker->What_Am_I() == RTTI_UNIT && House->Is_Ally(blocker)
                        && As_Target() < blocker->As_Target()) {
                        /*
                        **	Only give way to genuinely OPPOSING traffic, never a same-direction
                        **	follower -- judged by each unit's queued destination, not its momentary
                        **	heading. Same guard as Give_Way_Decision; without it a yielding unit can
                        **	hand the lane to the unit queued right behind it and wedge the bridge.
                        */
                        FootClass const* bf = (FootClass const*)blocker;
                        TARGET my_intent = Target_Legal(NavQueue[0]) ? NavQueue[0] : NavCom;
                        TARGET b_intent = Target_Legal(bf->NavQueue[0]) ? bf->NavQueue[0] : bf->NavCom;
                        int diff = (Target_Legal(my_intent) && Target_Legal(b_intent))
                                       ? ((Dir_Facing(Direction(my_intent))
                                           - Dir_Facing(::Direction(bf->Center_Coord(), As_Coord(b_intent))))
                                          & 0x07)
                                       : 0;
                        bool opposing = (diff >= 3 && diff <= 5);
                        CELL giveway = opposing ? Find_Give_Way_Cell(blocker) : 0;
                        if (giveway != 0) {
                            TARGET original = NavCom;
#if TF_DEV_BUILD
                            if (House && House->IsHuman) {
                                static FILE* tf_give_log = NULL;
                                static bool tf_give_tried = false;
                                if (!tf_give_tried) {
                                    tf_give_tried = true;
                                    const char* h = getenv("USERPROFILE");
                                    if (h == NULL)
                                        h = getenv("HOME");
                                    if (h != NULL) {
                                        char gp[512];
                                        snprintf(gp, sizeof(gp), "%s/Documents/CnCRemastered/tf_astar.log", h);
                                        tf_give_log = fopen(gp, "a");
                                    }
                                }
                                if (tf_give_log != NULL) {
                                    CELL mypos = Coord_Cell(Center_Coord());
                                    CELL bpos = Coord_Cell(blocker->Center_Coord());
                                    const char* me = (Techno_Type_Class() && Techno_Type_Class()->IniName)
                                                         ? Techno_Type_Class()->IniName
                                                         : "<?>";
                                    fprintf(tf_give_log,
                                            "GIVEWAY: loser=%s pos=(%d,%d) -> yield=(%d,%d) winnerpos=(%d,%d) "
                                            "myid=%d theirid=%d\n",
                                            me, (int)Cell_X(mypos), (int)Cell_Y(mypos), (int)Cell_X(giveway),
                                            (int)Cell_Y(giveway), (int)Cell_X(bpos), (int)Cell_Y(bpos),
                                            (int)As_Target(), (int)blocker->As_Target());
                                    fflush(tf_give_log);
                                }
                            }
#endif
                            Assign_Destination(::As_Target(giveway));
                            Queue_Navigation_List(original);
                            Stop_Driver();
                            TrackNumber = -1;
                            return (false);
                        }
                    }
                }
            }

            /*
            **	If the unit is close enough to the target then just stop
            **	driving now. This prevents the fidgeting that would occur
            **	if they mindlessly kept trying to get to the exact location
            **	desired. This is quite necessary since it is typical to move
            **	several units with the same mouse click.
            */
            if (!Is_On_Priority_Mission() && Distance(NavCom) < Rule.CloseEnoughDistance
                && (Mission == MISSION_MOVE || Mission == MISSION_GUARD_AREA)) {
                Assign_Destination(TARGET_NONE);
                if (!IsActive)
                    return (false);
            } else {
                /*
                **	If a basic path could not be found, but the immediate move destination is
                **	blocked by a friendly temporary blockage, then cause that blockage
                **	to scatter.
                */
                CELL cell = Adjacent_Cell(Coord_Cell(Center_Coord()), PrimaryFacing.Current());
                if (Map.In_Radar(cell)) {
                    MoveType ok = Can_Enter_Cell(cell);
                    if (ok == MOVE_TEMP) {
                        CellClass* cellptr = &Map[cell];
                        TechnoClass* blockage = cellptr->Cell_Techno();
                        if (blockage && House->Is_Ally(blockage)) {

                            /*
                            **	If the target can be told to get out of the way, only bother
                            **	to do so if we aren't very close to the target and this
                            **	object can just say "good enough" and stop here.
                            */
                            if (Distance(NavCom) < Rule.CloseEnoughDistance && !In_Radio_Contact()) {
                                Assign_Destination(TARGET_NONE);
                                return (false);
                            } else {
                                cellptr->Incoming(0, true, false);
                                //								cellptr->Incoming(0, true, true);
                            }
                        }
                    }
                }

                if (TryTryAgain > 0) {
                    TryTryAgain--;
                } else {
                    /*
                    **	Patient queue (v2.2.3): before abandoning the move, check WHY the path failed.
                    **	If our route ahead is blocked only by TEMPORARY traffic -- a stopped friendly
                    **	(MOVE_TEMP, which the scatter poke above is already nudging) or oncoming allied
                    **	traffic at a chokepoint (MOVE_NO held by an ally) -- the lane WILL clear, so we
                    **	stay patient and keep retrying instead of giving up. Giving up here is the
                    **	"unit drives off to a cliff-trace detour / scolds and stops" behaviour: a unit
                    **	queued behind a busy 1-wide pinch should just wait its turn. Only a genuinely
                    **	path-less block (permanent terrain, no traffic to explain it) still abandons.
                    */
                    bool traffic_blocked = false;
                    {
                        /*
                        **	Scan all 8 neighbours, not just the cell toward the goal: for an off-axis
                        **	destination the toward-goal cell can be terrain (the lake) while the real
                        **	obstacle -- a busy/claimed pinch -- is off to the side. We stay patient if any
                        **	neighbour carries an ACTIVE chokepoint claim (we are queued behind a pinch that
                        **	WILL clear) or holds a stopped friendly (MOVE_TEMP) / oncoming allied traffic.
                        */
                        CELL hc = Coord_Cell(Center_Coord());
                        for (FacingType nf = FACING_N; nf < FACING_COUNT && !traffic_blocked; nf++) {
                            CELL ncell = Adjacent_Cell(hc, nf);
                            if (!Map.In_Radar(ncell)) {
                                continue;
                            }
                            CellClass const& nce = Map[ncell];
                            int cage = Frame - (int)nce.ChokeClaimFrame;
                            if (nce.ChokeClaimFrame != 0 && cage >= 0 && cage <= 40) {
                                traffic_blocked = true; // queued behind an active pinch claim
                                break;
                            }
                            MoveType nm = Can_Enter_Cell(ncell, nf);
                            if (nm == MOVE_TEMP) {
                                traffic_blocked = true;
                            } else if (nm == MOVE_NO) {
                                TechnoClass* occ = nce.Cell_Techno();
                                if (occ != NULL && occ != this && occ->What_Am_I() == RTTI_UNIT
                                    && House->Is_Ally(occ)) {
                                    traffic_blocked = true;
                                }
                            }
                        }
                    }
                    if (traffic_blocked) {
                        TryTryAgain = PATH_RETRY; // wait its turn at the pinch; do not abandon

                        /*
                        **	Deadlock-breaker (v2.2.3). Patient-waiting is correct for a unit queued
                        **	behind a pinch that WILL clear -- but a SYMMETRIC deadlock the give-way
                        **	resolver never matched (a clump of units packed at a base, a stationary
                        **	friendly parked on our only path, two units nose-to-nose that both wait)
                        **	would wait FOREVER: nobody breaks the symmetry. The head-on log proves it
                        **	-- ~25k MOVE_NO blocks vs ~36 resolver hits. So once we have been blocked
                        **	for STUCK_SCATTER_TRIES straight retry cycles, force a scatter into ANY
                        **	free adjacent cell, then auto-resume the original order via the nav queue
                        **	(the same proven pattern as the give-way divert above). The neighbour scan
                        **	is rotated by our unit id so two units boxed against each other pick
                        **	DIFFERENT escape directions -- that asymmetry is what unwedges the clump,
                        **	with no RNG (lockstep-safe). StuckFrames resets to 0 the instant we advance
                        **	a cell (success path below), so a flowing or genuinely-clearing queue never
                        **	reaches the threshold.
                        */
                        const int STUCK_SCATTER_TRIES = 8;
                        if (StuckFrames < 0xFFFF) {
                            StuckFrames++;
                        }
                        if (StuckFrames >= STUCK_SCATTER_TRIES && Target_Legal(NavCom)) {
                            CELL hc = Coord_Cell(Center_Coord());
                            CELL escape = 0;
                            int seed = As_Target() & 0x07;
                            for (int n = 0; n < FACING_COUNT; n++) {
                                FacingType nf = (FacingType)((seed + n) & 0x07);
                                CELL ncell = Adjacent_Cell(hc, nf);
                                if (Map.In_Radar(ncell) && Can_Enter_Cell(ncell, nf) == MOVE_OK) {
                                    escape = ncell;
                                    break;
                                }
                            }
                            if (escape != 0) {
                                TARGET original = NavCom;
#if TF_DEV_BUILD
                                if (House && House->IsHuman) {
                                    static FILE* tf_scatter_log = NULL;
                                    static bool tf_scatter_tried = false;
                                    if (!tf_scatter_tried) {
                                        tf_scatter_tried = true;
                                        const char* h = getenv("USERPROFILE");
                                        if (h == NULL)
                                            h = getenv("HOME");
                                        if (h != NULL) {
                                            char sp[512];
                                            snprintf(sp, sizeof(sp), "%s/Documents/CnCRemastered/tf_astar.log", h);
                                            tf_scatter_log = fopen(sp, "a");
                                        }
                                    }
                                    if (tf_scatter_log != NULL) {
                                        const char* me = (Techno_Type_Class() && Techno_Type_Class()->IniName)
                                                             ? Techno_Type_Class()->IniName
                                                             : "<?>";
                                        fprintf(tf_scatter_log,
                                                "SCATTER-deadlock: %s pos=(%d,%d) -> escape=(%d,%d) "
                                                "stuck=%d myid=%d\n",
                                                me, (int)Cell_X(hc), (int)Cell_Y(hc), (int)Cell_X(escape),
                                                (int)Cell_Y(escape), (int)StuckFrames, (int)As_Target());
                                        fflush(tf_scatter_log);
                                    }
                                }
#endif
                                Assign_Destination(::As_Target(escape));
                                Queue_Navigation_List(original);
                                StuckFrames = 0;
                                Stop_Driver();
                                TrackNumber = -1;
                                return (false);
                            }
                        }
                    } else {
                        Assign_Destination(TARGET_NONE);
                        if (!IsActive)
                            return (false);
                        if (IsNewNavCom)
                            Sound_Effect(VOC_SCOLD);
                        IsNewNavCom = false;
                    }
                }
            }

            /*
            **	Since the path was blocked, check to make sure that it was completely
            **	blocked. If so and it has a valid TarCom and it is out of range of the
            **	TarCom, then give this unit a range limit so that it might not pick
            **	a "can't reach" target again.
            */
            if (!Target_Legal(NavCom) && Target_Legal(TarCom) && !In_Range(TarCom)) {
                IsScanLimited = true;
                if (Team.Is_Valid())
                    Team->Scan_Limit();
                Assign_Target(TARGET_NONE);
            }

            /*
            **	Stop the movement, for now, and let the subsequent logic in later game
            **	frames resume movement as appropriate.
            */
            Stop_Driver();
            TrackNumber = -1;
            IsTurretLockedDown = false;
            return (false);
        }

        /*
        **	If a basic path could be found, but the immediate move destination is
        **	blocked by a friendly temporary blockage, then cause that blockage
        **	to scatter.
        */
        CELL cell = Adjacent_Cell(Coord_Cell(Center_Coord()), Path[0]);
        if (Map.In_Radar(cell)) {
            MoveType ok = Can_Enter_Cell(cell);
            if (ok == MOVE_TEMP) {
                CellClass* cellptr = &Map[cell];
                TechnoClass* blockage = cellptr->Cell_Techno();
                if (blockage && House->Is_Ally(blockage)) {

                    /*
                    **	If the target can be told to get out of the way, only bother
                    **	to do so if we aren't very close to the target and this
                    **	object can just say "good enough" and stop here.
                    */
                    if (Distance(NavCom) < Rule.CloseEnoughDistance && !In_Radio_Contact()) {
                        Assign_Destination(TARGET_NONE);
                        return (false);
                    } else {
                        cellptr->Incoming(0, true, false);
                        //						cellptr->Incoming(0, true, true);
                    }
                }
            }
        }

        TryTryAgain = PATH_RETRY;
        facing = Path[0];
    }

    /*
    **	Determine the coordinate of the next cell to move into.
    */
    dest = Adjacent_Cell(Coord, facing);
    dir = Facing_Dir(facing);

    /*
    **	Set the facing correctly if it isn't already correct. This
    **	means starting a rotation track if necessary.
    */
    facediff = PrimaryFacing.Difference(dir);
    if (facediff) {

        /*
        **	Request a change of facing.
        */
        Do_Turn(dir);
        return (true);

    } else {

        /* NOTE:  Beyond this point, actual track assignment can begin.
        **
        **	If the cell to move into is impassable (probably for some unexpected
        **	reason), then abort the path list and set the speed to zero. The
        ** next time this routine is called, a new path will be generated.
        */
        destcell = Coord_Cell(dest);
        Mark(MARK_UP);
        MoveType cando = Can_Enter_Cell(destcell, facing);
        Mark(MARK_DOWN);

        if (cando != MOVE_OK) {

            if (Mission == MISSION_MOVE /*KO&& House->IsHuman */ && Distance(NavCom) < Rule.CloseEnoughDistance) {
                Assign_Destination(TARGET_NONE);
                if (!IsActive)
                    return (false); // BG
            }

            /*
            **	If a temporary friendly object is blocking the path, then cause it to
            **	get out of the way.
            */
            if (cando == MOVE_TEMP) {
                Map[destcell].Incoming(0, true, true);
            }

            /*
            **	If a cloaked object is blocking, then shimmer the cell.
            */
            if (cando == MOVE_CLOAK) {
                Map[destcell].Shimmer();
            }

            Stop_Driver();
            if (cando != MOVE_MOVING_BLOCK) {
                Path[0] = FACING_NONE; // Path is blocked!
            }

            /*
            ** If blocked by a moving block then just exit start of move and
            ** try again next tick.
            */
            if (cando == MOVE_DESTROYABLE) {
                if (Map[destcell].Cell_Object()) {
                    if (!House->Is_Ally(Map[destcell].Cell_Object())) {
                        Override_Mission(MISSION_ATTACK, Map[destcell].Cell_Object()->As_Target(), TARGET_NONE);
                    }
                } else {
                    if (Map[destcell].Overlay != OVERLAY_NONE
                        && OverlayTypeClass::As_Reference(Map[destcell].Overlay).IsWall) {
                        Override_Mission(MISSION_ATTACK, ::As_Target(destcell), TARGET_NONE);
                    }
                }
            } else {
                if (IsNewNavCom)
                    Sound_Effect(VOC_SCOLD);
            }
            IsNewNavCom = false;
            TrackNumber = -1;
            return (true);
        }

        /*
        **	We are committing to enter the next cell (cando == MOVE_OK) -- real forward progress, so
        **	clear the deadlock-breaker counter. Only a unit that has made NO progress for
        **	STUCK_SCATTER_TRIES straight retry cycles ever force-scatters.
        */
        StuckFrames = 0;

        /*
        **	Determine the speed that the unit can travel to the desired square.
        */
        ground = Map[destcell].Land_Type();
        speed = Ground[ground].Cost[Techno_Type_Class()->Speed] * 255;

        /* change speed if it's related to a team move */
        if (IsFormationMove)
            speed = Ground[ground].Cost[FormationSpeed] * 255;
        if (!speed)
            speed = 128;

#ifdef NEVER
        /*
        **	Set the jiggle flag if the terrain would cause the unit
        **	to jiggle when travelled over.
        */
        BaseF &= ~BASEF_JIGGLE;
        if (Ground[ground].Jiggle) {
            BaseF |= BASEF_JIGGLE;
        }
#endif

        /*
        **	A damaged unit has a reduced speed.
        */
        if (Health_Ratio() <= Rule.ConditionYellow /*(Techno_Type_Class()->MaxStrength>>1) > Strength*/) {
            speed -= (speed / 4); // Three quarters speed.
        }
        if ((speed != Speed) /* || !SpeedAdd*/) {
            Set_Speed(speed); // Full speed.
        }

        /*
        **	Reserve the destination cell so that it won't become
        **	occupied AS this unit is moving into it.
        */
        if (cando != MOVE_OK) {
            Path[0] = FACING_NONE; // Path is blocked!
            TrackNumber = -1;
            dest = 0;
        } else {

            Overrun_Square(Coord_Cell(dest), true);

            /*
            **	Determine which track to use (based on recorded path).
            */
            FacingType nextface = Path[1];
            if (nextface == FACING_NONE)
                nextface = facing;

            IsOnShortTrack = false;
            TrackNumber = facing * FACING_COUNT + (int)nextface;
            if (TrackControl[TrackNumber].Track == 0) {
                Path[0] = FACING_NONE;
                TrackNumber = -1;
                return (true);
            } else {
                if (TrackControl[TrackNumber].Flag & F_D) {
                    /*
                    **	If the middle cell of a two cell track contains a crate,
                    **	the check for goodies before movement starts.
                    */
                    if (!Map[destcell].Goodie_Check(this)) {
                        cando = MOVE_NO;
                        if (!IsActive)
                            return (false);
                    } else {
                        if (!IsActive)
                            return (false);
                        dest = Adjacent_Cell(dest, nextface);
                        destcell = Coord_Cell(dest);
                        cando = Can_Enter_Cell(destcell);
                    }
                    if (!IsActive)
                        return (false);

                    if (cando != MOVE_OK) {

                        /*
                        **	If a temporary friendly object is blocking the path, then cause it to
                        **	get out of the way.
                        */
                        if (cando == MOVE_TEMP) {
                            Map[destcell].Incoming(0, true, true);
                        }

                        /*
                        **	If a cloaked object is blocking, then shimmer the cell.
                        */
                        if (cando == MOVE_CLOAK) {
                            Map[destcell].Shimmer();
                        }

                        Path[0] = FACING_NONE; // Path is blocked!
                        TrackNumber = -1;
                        dest = 0;
                        if (cando == MOVE_DESTROYABLE) {

                            if (Map[destcell].Cell_Object()) {
                                if (!House->Is_Ally(Map[destcell].Cell_Object())) {
                                    Override_Mission(
                                        MISSION_ATTACK, Map[destcell].Cell_Object()->As_Target(), TARGET_NONE);
                                }
                            } else {
                                if (Map[destcell].Overlay != OVERLAY_NONE
                                    && OverlayTypeClass::As_Reference(Map[destcell].Overlay).IsWall) {
                                    Override_Mission(MISSION_ATTACK, ::As_Target(destcell), TARGET_NONE);
                                }
                            }
                            IsNewNavCom = false;
                            TrackIndex = 0;
                            return (true);
                        }
                    } else {
                        memmove((char*)&Path[0], (char*)&Path[2], CONQUER_PATH_MAX - 2);
                        Path[CONQUER_PATH_MAX - 2] = FACING_NONE;
                        IsPlanningToLook = true;
                    }
                } else {
                    memmove((char*)&Path[0], (char*)&Path[1], CONQUER_PATH_MAX - 1);
                }
                Path[CONQUER_PATH_MAX - 1] = FACING_NONE;
            }
        }

        IsNewNavCom = false;
        TrackIndex = 0;
        if (!Start_Driver(dest)) {
            TrackNumber = -1;
            Path[0] = FACING_NONE;
            Set_Speed(0);
        }
    }
    return (false);
}

/***********************************************************************************************
 * DriveClass::AI -- Processes unit movement and rotation.                                     *
 *                                                                                             *
 *    This routine is used to process unit movement and rotation. It                           *
 *    functions autonomously from the script system. Thus, once a unit                         *
 *    is give rotation command or movement path, it will follow this                           *
 *    until specifically instructed to stop. The advantage of this                             *
 *    method is that it allows smooth movement of units, faster game                           *
 *    execution, and reduced script complexity (since actual movement                          *
 *    dynamics need not be controlled directly by the scripts).                                *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   This routine relies on the process control bits for the                         *
 *             specified unit (for speed reasons). Thus, only setting                          *
 *             movement, rotation, or path list will the unit perform                          *
 *             any physics.                                                                    *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/26/1993 JLB : Created.                                                                 *
 *   04/15/1994 JLB : Converted to member function.                                            *
 *=============================================================================================*/
void DriveClass::AI(void)
{
    assert(IsActive);

    FootClass::AI();
    if (!IsActive || Height > 0)
        return;

    /*
    ** Is this a unit that's been teleported using the chronosphere, and if so,
    ** has his timer expired such that he needs to teleport back?
    */
    if (IsMoebius) {
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
        if (What_Am_I() != RTTI_UNIT || ((UnitClass*)this)->Class->Type != UNIT_CHRONOTANK) {
#endif
            if (MoebiusCountDown == 0) {
                IsMoebius = false;
                Teleport_To(MoebiusCell);
                MoebiusCell = 0;
            }
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
        }
#endif
    }

    /*
    **	If the unit is following a track, then continue
    **	to do so -- mindlessly.
    */
    if (TrackNumber != -1) {

        /*
        **	Perform the movement accumulation.
        */
        While_Moving();
        if (!IsActive)
            return;
        if (TrackNumber == -1 && (Target_Legal(NavCom) || Path[0] != FACING_NONE)
            && (What_Am_I() != RTTI_UNIT || !((UnitClass*)this)->IsDumping)) {
            Start_Of_Move();
            if (!IsActive)
                return;
            While_Moving();
            if (!IsActive)
                return;
        }

    } else {

        /*
        **	For tracked units that are rotating in place, perform the rotation now.
        */
#ifdef TOFIX
        if ((Class->Speed == SPEED_FLOAT || Class->Speed == SPEED_HOVER || Class->Speed == SPEED_TRACK
             || (Class->Speed == SPEED_WHEEL && !Special.IsThreePoint))
            && PrimaryFacing.Is_Rotating()) {
            if (PrimaryFacing.Rotation_Adjust(Class->ROT)) {
                Mark(MARK_CHANGE);
            }
#else
        if (PrimaryFacing.Is_Rotating()) {
            Mark(MARK_CHANGE_REDRAW);
            if (PrimaryFacing.Rotation_Adjust(Techno_Type_Class()->ROT * House->GroundspeedBias)) {
                Mark(MARK_CHANGE_REDRAW);
            }
#endif
            if (!IsRotating) {
                Per_Cell_Process(PCP_ROTATION);
                if (!IsActive)
                    return;
            }

        } else {

            /*
            **	The unit has no track to follow, but if there
            **	is a navigation target or a remaining path,
            **	then start on a new track.
            */
            if ((Mission != MISSION_GUARD || Target_Legal(NavCom)) && Mission != MISSION_UNLOAD) {
                if (Target_Legal(NavCom) || Path[0] != FACING_NONE) {

                    /*
                    **	Double check to make sure that the movement destination is
                    **	in a zone that this unit can travel to. If not, then abort
                    **	the navigation target. Exception is to allow units to leave
                    **	impassable cells regardless of zone checks.
                    */
                    LandType land = LAND_NONE;
                    if (What_Am_I() == RTTI_INFANTRY || What_Am_I() == RTTI_UNIT) {
                        land = Map[Center_Coord()].Land_Type();
                    }
                    if (IsLocked && Mission != MISSION_ENTER && Target_Legal(NavCom)
                        && !Is_In_Same_Zone(As_Cell(NavCom)) && land != LAND_ROCK && land != LAND_WATER
                        && land != LAND_RIVER && !Team) {
                        Stop_Driver();
                        Assign_Destination(TARGET_NONE);
                    } else {
                        Start_Of_Move();
                        if (!IsActive)
                            return;
                        While_Moving();
                        if (!IsActive)
                            return;
                    }
                } else {
                    Stop_Driver();
                }
            }
        }
    }
}

/***********************************************************************************************
 * DriveClass::Fixup_Path -- Adds smooth start path to normal movement path.                   *
 *                                                                                             *
 *    This routine modifies the path of the specified unit so that it                          *
 *    will not start out with a rotation. This is necessary for those                          *
 *    vehicles that have difficulty with rotating in place. Typically,                         *
 *    this includes wheeled vehicles.                                                          *
 *                                                                                             *
 * INPUT:   unit  -- Pointer to the unit to adjust.                                            *
 *                                                                                             *
 *          path  -- Pointer to path structure.                                                *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Only units that require a fixup get modified. The                               *
 *             modification only occurs, if there is a legal path to                           *
 *             do so.                                                                          *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   04/03/1994 JLB : Created.                                                                 *
 *   04/06/1994 JLB : Uses path structure.                                                     *
 *   04/10/1994 JLB : Diagonal smooth turn added.                                              *
 *   04/15/1994 JLB : Converted to member function.                                            *
 *=============================================================================================*/
void DriveClass::Fixup_Path(PathType* path)
{
    assert(IsActive);

    FacingType stage[6] = {FACING_N, FACING_N, FACING_N, FACING_N, FACING_N, FACING_N}; // Prefix path elements.
    int facediff; // The facing difference value (0..4 | 0..-4).
    static FacingType _path[4][6] = {
        {(FacingType)2, (FacingType)0, (FacingType)2, (FacingType)0, (FacingType)0, (FacingType)0},
        {(FacingType)3, (FacingType)0, (FacingType)2, (FacingType)2, (FacingType)0, (FacingType)0},
        {(FacingType)4, (FacingType)0, (FacingType)2, (FacingType)2, (FacingType)0, (FacingType)0},
        {(FacingType)4, (FacingType)0, (FacingType)2, (FacingType)2, (FacingType)1, (FacingType)0}};
    static FacingType _dpath[4][6] = {
        {(FacingType)0, (FacingType)0, (FacingType)0, (FacingType)0, (FacingType)0, (FacingType)0},
        {(FacingType)3, (FacingType)0, (FacingType)2, (FacingType)2, (FacingType)0, (FacingType)0},
        {(FacingType)4, (FacingType)0, (FacingType)2, (FacingType)2, (FacingType)1, (FacingType)0},
        {(FacingType)5, (FacingType)0, (FacingType)2, (FacingType)2, (FacingType)1, (FacingType)0}};

    int index;
    int counter;         // Path addition
    FacingType* ptr;     // Path list pointer.
    FacingType* ptr2;    // Copy of new path list pointer.
    FacingType nextpath; // Next path value.
    CELL cell;           // Working cell value.
    bool ok;

    /*
    **	Verify that the unit is valid and there is a path problem to resolve.
    */
    if (!path || path->Command[0] == FACING_NONE) {
        return;
    }

    /*
    **	Only wheeled vehicles need a path fixup -- to avoid 3 point turns.
    */
#ifdef TOFIX
    if (!Special.IsThreePoint || Class->Speed != SPEED_WHEEL) {
#else
    if (What_Am_I() == RTTI_UNIT || What_Am_I() == RTTI_VESSEL) {
//	if (What_Am_I() == RTTI_UNIT) {
#endif
        return;
    }

    /*
    **	If the original path starts in the same direction as the unit, then
    **	there is no problem to resolve -- abort.
    */
    facediff = PrimaryFacing.Difference((DirType)(path->Command[0] << 5)) >> 5;

    if (!facediff)
        return;

    if (Dir_Facing(PrimaryFacing) & FACING_NE) {
        ptr = &_dpath[(FacingType)ABS((int)facediff) - FACING_NE][1];         // Pointer to path adjust list.
        counter = (int)_dpath[(FacingType)ABS((int)facediff) - FACING_NE][0]; // Number of path adjusts.
    } else {
        ptr = &_path[(FacingType)ABS((int)facediff) - FACING_NE][1];         // Pointer to path adjust list.
        counter = (int)_path[(FacingType)ABS((int)facediff) - FACING_NE][0]; // Number of path adjusts.
    }
    ptr2 = ptr;

    ok = true;                            // Presume adjustment is all ok.
    cell = Coord_Cell(Coord);             // Starting cell.
    nextpath = Dir_Facing(PrimaryFacing); // Starting path.
    for (index = 0; index < counter; index++) {

        /*
        **	Determine next path element and add it to the
        **	working path list.
        */
        if (facediff > 0) {
            nextpath = nextpath + *ptr++;
        } else {
            nextpath = nextpath - *ptr++;
        }
        stage[index] = nextpath;
        cell = Adjacent_Cell(cell, nextpath);
        // cell = Coord_Cell(Adjacent_Cell(Cell_Coord(cell), nextpath));

        /*
        **	If it can't enter this cell, then abort the path
        **	building operation without adjusting the unit's
        **	path.
        */
        if (Can_Enter_Cell(cell, nextpath) != MOVE_OK) {
            ok = false;
            break;
        }
    }

    /*
    **	If veering to the left was not successful, then try veering
    **	to the right. This only makes sense if the vehicle is trying
    **	to turn 180 degrees.
    */
    if (!ok && ABS(facediff) == 4) {
        ptr = ptr2; // Pointer to path adjust list.
        facediff = -facediff;
        ok = true;                            // Presume adjustment is all ok.
        cell = Coord_Cell(Coord);             // Starting cell.
        nextpath = Dir_Facing(PrimaryFacing); // Starting path.
        for (index = 0; index < counter; index++) {

            /*
            **	Determine next path element and add it to the
            **	working path list.
            */
            if (facediff > 0) {
                nextpath = nextpath + *ptr++;
            } else {
                nextpath = nextpath - *ptr++;
            }
            stage[index] = nextpath;
            cell = Coord_Cell(Adjacent_Cell(Cell_Coord(cell), nextpath));

            /*
            **	If it can't enter this cell, then abort the path
            **	building operation without adjusting the unit's
            **	path.
            */
            if (Can_Enter_Cell(cell, nextpath) != MOVE_OK) {
                ok = false;
                break;
            }
        }
    }

    /*
    **	If a legal path addition was created, then install it in place
    **	of the first path value. The initial path entry is to be replaced
    **	with a sequence of path entries that create smooth turning.
    */
    if (ok) {
        if (path->Length <= 1) {
            memmove((char*)&stage[0], (char*)path->Command, max(counter, 1));
            path->Length = counter;
        } else {

            /*
            **	Optimize the transition path step from the smooth turn
            **	first part as it joins with the rest of the normal
            **	path. The normal prefix path steps are NOT to be optimized.
            */
            if (counter) {
                counter--;
                path->Command[0] = stage[counter];
                Optimize_Moves(path, MOVE_OK);
            }

            /*
            **	If there is more than one prefix path element, then
            **	insert the rest now.
            */
            if (counter) {
                memmove((char*)&path->Command[0], (char*)&path->Command[counter], 40 - counter);
                memmove((char*)&stage[0], (char*)&path->Command[0], counter);
                path->Length += counter;
            }
        }
        path->Command[path->Length] = FACING_NONE;
    }
}

/***********************************************************************************************
 * DriveClass::Lay_Track -- Handles track laying logic for the unit.                           *
 *                                                                                             *
 *    This routine handles the track laying for the unit. This entails examining the unit's    *
 *    current location as well as the direction and whether this unit is allowed to lay        *
 *    tracks in the first place.                                                               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/28/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void DriveClass::Lay_Track(void)
{
    assert(IsActive);

#ifdef NEVER
    static IconCommandType* _trackdirs[8] = {
        TrackN_S, TrackNE_SW, TrackE_W, TrackNW_SE, TrackN_S, TrackNE_SW, TrackE_W, TrackNW_SE};

    if (!(ClassF & CLASSF_TRACKS))
        return;

    Icon_Install(Coord_Cell(Coord), _trackdirs[Facing_To_8(BodyFacing)]);
#endif
}

/***********************************************************************************************
 * DriveClass::Mark_Track -- Marks the midpoint of the track as occupied.                      *
 *                                                                                             *
 *    This routine will ensure that the midpoint (if any) of the track that the unit is        *
 *    following, will be marked according to the mark type specified.                          *
 *                                                                                             *
 * INPUT:   headto   -- The head to coordinate.                                                *
 *                                                                                             *
 *          type     -- The type of marking to perform.                                        *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/30/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void DriveClass::Mark_Track(COORDINATE headto, MarkType type)
{
    assert(IsActive);

    int value;

    if (type == MARK_UP) {
        value = false;
    } else {
        value = true;
    }

    if (headto) {
        if (!IsOnShortTrack && TrackNumber != -1) {

            /*
            ** If we have not passed the per cell process point we need
            ** to deal with it.
            */
            int tracknum = TrackControl[TrackNumber].Track;
            if (tracknum) {
                TrackType const* ptr = RawTracks[tracknum - 1].Track;
                int cellidx = RawTracks[tracknum - 1].Cell;
                if (cellidx > -1) {
                    DirType dir = ptr[cellidx].Facing;

                    if (TrackIndex < cellidx && cellidx != -1) {
                        COORDINATE offset = Smooth_Turn(ptr[cellidx].Offset, dir);
                        Map[offset].Flag.Occupy.Vehicle = value;
                    }
                }
            }
        }
        Map[headto].Flag.Occupy.Vehicle = value;
    }
}

/***********************************************************************************************
 * DriveClass::Ok_To_Move -- Checks to see if this object can begin moving.                    *
 *                                                                                             *
 *    This routine is used to verify that this object is allowed to move. Some objects can     *
 *    be temporarily occupied and thus cannot move until the situation permits.                *
 *                                                                                             *
 * INPUT:   direction   -- The direction that movement would be desired.                       *
 *                                                                                             *
 * OUTPUT:  Can the unit move in the direction specified?                                      *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool DriveClass::Ok_To_Move(DirType) const
{
    assert(IsActive);

    return true;
}

/***************************************************************************
**	Smooth turn track tables. These are coordinate offsets from the center
**	of the destination cell. These are the raw tracks that are modified
**	by negating the X and Y portions as necessary. Also for reverse travelling
**	direction, the track list can be processed backward.
**
**	Track 1 = N
**	Track 2 = NE
**	Track 3 = N->NE 45 deg (double path consumption)
**	Track 4 = N->E 90 deg (double path consumption)
**	Track 5 = NE->SE 90 deg (double path consumption)
** Track 6 = NE->N 45 deg (double path consumption)
**	Track 7 = N->NE (facing change only)
**	Track 8 = NE->E (facing change only)
**	Track 9 = N->E (facing change only)
**	Track 10= NE->SE (facing change only)
**	Track 11= back up into refinery
**	Track 12= drive out of refinery
*/
//#pragma warn -ias
DriveClass::TrackType const DriveClass::Track1[24] = {
    {0x00F50000L, (DirType)0}, {0x00EA0000L, (DirType)0}, {0x00DF0000L, (DirType)0},
    {0x00D40000L, (DirType)0}, {0x00C90000L, (DirType)0}, {0x00BE0000L, (DirType)0},
    {0x00B30000L, (DirType)0}, {0x00A80000L, (DirType)0}, {0x009D0000L, (DirType)0},
    {0x00920000L, (DirType)0}, {0x00870000L, (DirType)0}, {0x007C0000L, (DirType)0}, // Track jump check here.
    {0x00710000L, (DirType)0}, {0x00660000L, (DirType)0}, {0x005B0000L, (DirType)0},
    {0x00500000L, (DirType)0}, {0x00450000L, (DirType)0}, {0x003A0000L, (DirType)0},
    {0x002F0000L, (DirType)0}, {0x00240000L, (DirType)0}, {0x00190000L, (DirType)0},
    {0x000E0000L, (DirType)0}, {0x00030000L, (DirType)0}, {0x00000000L, (DirType)0}};

DriveClass::TrackType const DriveClass::Track2[] = {
    {0x00F8FF08L, (DirType)32}, {0x00F0FF10L, (DirType)32}, {0x00E8FF18L, (DirType)32},
    {0x00E0FF20L, (DirType)32}, {0x00D8FF28L, (DirType)32}, {0x00D0FF30L, (DirType)32},
    {0x00C8FF38L, (DirType)32}, {0x00C0FF40L, (DirType)32}, {0x00B8FF48L, (DirType)32},
    {0x00B0FF50L, (DirType)32}, {0x00A8FF58L, (DirType)32}, {0x00A0FF60L, (DirType)32},
    {0x0098FF68L, (DirType)32}, {0x0090FF70L, (DirType)32}, {0x0088FF78L, (DirType)32},
    {0x0080FF80L, (DirType)32}, // Track jump check here.
    {0x0078FF88L, (DirType)32}, {0x0070FF90L, (DirType)32}, {0x0068FF98L, (DirType)32},
    {0x0060FFA0L, (DirType)32}, {0x0058FFA8L, (DirType)32}, {0x0050FFB0L, (DirType)32},
    {0x0048FFB8L, (DirType)32}, {0x0040FFC0L, (DirType)32}, {0x0038FFC8L, (DirType)32},
    {0x0030FFD0L, (DirType)32}, {0x0028FFD8L, (DirType)32}, {0x0020FFE0L, (DirType)32},
    {0x0018FFE8L, (DirType)32}, {0x0010FFF0L, (DirType)32}, {0x0008FFF8L, (DirType)32},
    {0x00000000L, (DirType)32}};

DriveClass::TrackType const DriveClass::Track3[] = {
    {0x01F5FF00L, (DirType)0},  {0x01EAFF00L, (DirType)0},  {0x01DFFF00L, (DirType)0},  {0x01D4FF00L, (DirType)0},
    {0x01C9FF00L, (DirType)0},  {0x01BEFF00L, (DirType)0},  {0x01B3FF00L, (DirType)0},  {0x01A8FF00L, (DirType)0},
    {0x019DFF00L, (DirType)0},  {0x0192FF00L, (DirType)0},  {0x0187FF00L, (DirType)0},  {0x0180FF00L, (DirType)0},
    {0x0175FF00L, (DirType)0}, // Jump entry point here.
    {0x016BFF00L, (DirType)0},  {0x0160FF02L, (DirType)1},  {0x0155FF04L, (DirType)3},  {0x014CFF06L, (DirType)4},
    {0x0141FF08L, (DirType)5},  {0x0137FF0BL, (DirType)7},  {0x012EFF0FL, (DirType)8},  {0x0124FF13L, (DirType)9},
    {0x011AFF17L, (DirType)11}, {0x0110FF1BL, (DirType)12}, {0x0107FF1FL, (DirType)13}, // Center cell processing here.
    {0x00FCFF24L, (DirType)15}, {0x00F3FF28L, (DirType)16}, {0x00ECFF2CL, (DirType)17}, {0x00E0FF32L, (DirType)19},
    {0x00D7FF36L, (DirType)20}, {0x00CFFF3DL, (DirType)21}, {0x00C6FF42L, (DirType)23}, {0x00BAFF49L, (DirType)24},
    {0x00B0FF4DL, (DirType)25}, {0x00A8FF58L, (DirType)27}, {0x00A0FF60L, (DirType)28}, {0x0098FF68L, (DirType)29},
    {0x0090FF70L, (DirType)31}, {0x0088FF78L, (DirType)32}, {0x0080FF80L, (DirType)32}, // Track jump check here.
    {0x0078FF88L, (DirType)32}, {0x0070FF90L, (DirType)32}, {0x0068FF98L, (DirType)32}, {0x0060FFA0L, (DirType)32},
    {0x0058FFA8L, (DirType)32}, {0x0050FFB0L, (DirType)32}, {0x0048FFB8L, (DirType)32}, {0x0040FFC0L, (DirType)32},
    {0x0038FFC8L, (DirType)32}, {0x0030FFD0L, (DirType)32}, {0x0028FFD8L, (DirType)32}, {0x0020FFE0L, (DirType)32},
    {0x0018FFE8L, (DirType)32}, {0x0010FFF0L, (DirType)32}, {0x0008FFF8L, (DirType)32}, {0x00000000L, (DirType)32}};

DriveClass::TrackType const DriveClass::Track4[] = {
    {0x00F5FF00L, (DirType)0},  {0x00EBFF00L, (DirType)0},  {0x00E0FF00L, (DirType)0},
    {0x00D5FF00L, (DirType)0},  {0x00CBFF01L, (DirType)0},  {0x00C0FF03L, (DirType)0},
    {0x00B5FF05L, (DirType)1},  {0x00ABFF07L, (DirType)1},  {0x00A0FF0AL, (DirType)2},
    {0x0095FF0DL, (DirType)3},  {0x008BFF10L, (DirType)4},  {0x0080FF14L, (DirType)5}, // Track entry here.
    {0x0075FF18L, (DirType)8},  {0x006DFF1CL, (DirType)12}, {0x0063FF22L, (DirType)16},
    {0x005AFF25L, (DirType)20}, {0x0052FF2BL, (DirType)23}, {0x0048FF32L, (DirType)27},
    {0x0040FF37L, (DirType)32}, {0x0038FF3DL, (DirType)36}, {0x0030FF46L, (DirType)39},
    {0x002BFF4FL, (DirType)43}, {0x0024FF58L, (DirType)47}, {0x0020FF60L, (DirType)51},
    {0x001BFF6DL, (DirType)54}, {0x0017FF79L, (DirType)57}, {0x0014FF82L, (DirType)60}, // Track jump here.
    {0x0011FF8FL, (DirType)62}, {0x000DFF98L, (DirType)63}, {0x0009FFA2L, (DirType)64},
    {0x0006FFACL, (DirType)64}, {0x0004FFB5L, (DirType)66}, {0x0003FFC0L, (DirType)64},
    {0x0002FFCBL, (DirType)64}, {0x0001FFD5L, (DirType)64}, {0x0000FFE0L, (DirType)64},
    {0x0000FFEBL, (DirType)64}, {0x0000FFF5L, (DirType)64}, {0x00000000L, (DirType)64}};

DriveClass::TrackType const DriveClass::Track5[] = {
    {0xFFF8FE08L, (DirType)32}, {0xFFF0FE10L, (DirType)32}, {0xFFE8FE18L, (DirType)32},
    {0xFFE0FE20L, (DirType)32}, {0xFFD8FE28L, (DirType)32}, {0xFFD0FE30L, (DirType)32},
    {0xFFC8FE38L, (DirType)32}, {0xFFC0FE40L, (DirType)32}, {0xFFB8FE48L, (DirType)32},
    {0xFFB0FE50L, (DirType)32}, {0xFFA8FE58L, (DirType)32}, {0xFFA0FE60L, (DirType)32},
    {0xFF98FE68L, (DirType)32}, {0xFF90FE70L, (DirType)32}, {0xFF88FE78L, (DirType)32},
    {0xFF80FE80L, (DirType)32}, // Track entry here.
    {0xFF78FE88L, (DirType)32}, {0xFF71FE90L, (DirType)32}, {0xFF6AFE97L, (DirType)32},
    {0xFF62FE9FL, (DirType)32}, {0xFF5AFEA8L, (DirType)32}, {0xFF53FEB0L, (DirType)35},
    {0xFF4BFEB7L, (DirType)38}, {0xFF44FEBEL, (DirType)41}, {0xFF3EFEC4L, (DirType)44},
    {0xFF39FECEL, (DirType)47}, {0xFF34FED8L, (DirType)50}, {0xFF30FEE0L, (DirType)53},
    {0xFF2DFEEBL, (DirType)56}, {0xFF2CFEF5L, (DirType)59}, {0xFF2BFF00L, (DirType)62},
    {0xFF2CFF0BL, (DirType)66}, {0xFF2DFF15L, (DirType)69}, {0xFF30FF1FL, (DirType)72},
    {0xFF34FF28L, (DirType)75}, {0xFF39FF30L, (DirType)78}, {0xFF3EFF3AL, (DirType)81},
    {0xFF44FF44L, (DirType)84}, {0xFF4BFF4BL, (DirType)87}, {0xFF53FF50L, (DirType)90},
    {0xFF5AFF58L, (DirType)93}, {0xFF62FF60L, (DirType)96}, {0xFF6AFF68L, (DirType)96},
    {0xFF71FF70L, (DirType)96}, {0xFF78FF78L, (DirType)96}, {0xFF80FF80L, (DirType)96}, // Track jump check here.
    {0xFF88FF88L, (DirType)96}, {0xFF90FF90L, (DirType)96}, {0xFF98FF98L, (DirType)96},
    {0xFFA0FFA0L, (DirType)96}, {0xFFA8FFA8L, (DirType)96}, {0xFFB0FFB0L, (DirType)96},
    {0xFFB8FFB8L, (DirType)96}, {0xFFC0FFC0L, (DirType)96}, {0xFFC8FFC8L, (DirType)96},
    {0xFFD0FFD0L, (DirType)96}, {0xFFD8FFD8L, (DirType)96}, {0xFFE0FFE0L, (DirType)96},
    {0xFFE8FFE8L, (DirType)96}, {0xFFF0FFF0L, (DirType)96}, {0xFFF8FFF8L, (DirType)96},
    {0x00000000L, (DirType)96}};

DriveClass::TrackType const DriveClass::Track6[] = {
    {0x0100FE00L, (DirType)32}, {0x00F8FE08L, (DirType)32}, {0x00F0FE10L, (DirType)32},
    {0x00E8FE18L, (DirType)32}, {0x00E0FE20L, (DirType)32}, {0x00D8FE28L, (DirType)32},
    {0x00D0FE30L, (DirType)32}, {0x00C8FE38L, (DirType)32}, {0x00C0FE40L, (DirType)32},
    {0x00B8FE48L, (DirType)32}, {0x00B0FE50L, (DirType)32}, {0x00A8FE58L, (DirType)32},
    {0x00A0FE60L, (DirType)32}, {0x0098FE68L, (DirType)32}, {0x0090FE70L, (DirType)32},
    {0x0088FE78L, (DirType)32}, {0x0080FE80L, (DirType)32}, // Jump entry point here.
    {0x0078FE88L, (DirType)32}, {0x0070FE90L, (DirType)32}, {0x0068FE98L, (DirType)32},
    {0x0060FEA0L, (DirType)32}, {0x0058FEA8L, (DirType)32}, {0x0055FEAEL, (DirType)32},
    {0x004EFEB8L, (DirType)35}, {0x0048FEC0L, (DirType)37}, {0x0042FEC9L, (DirType)40},
    {0x003BFED2L, (DirType)43}, {0x0037FEDAL, (DirType)45}, {0x0032FEE3L, (DirType)48},
    {0x002BFEEBL, (DirType)51}, {0x0026FEF5L, (DirType)53}, {0x0022FEFEL, (DirType)56},
    {0x001CFF08L, (DirType)59}, {0x0019FF12L, (DirType)61}, {0x0015FF1BL, (DirType)64},
    {0x0011FF26L, (DirType)64}, {0x000EFF30L, (DirType)64}, {0x000BFF39L, (DirType)64},
    {0x0009FF43L, (DirType)64}, {0x0007FF4EL, (DirType)64}, {0x0005FF57L, (DirType)64},
    {0x0003FF62L, (DirType)64}, {0x0001FF6DL, (DirType)64}, {0x0000FF77L, (DirType)64},
    {0x0000FF80L, (DirType)64}, // Track jump check here.
    {0x0000FF8BL, (DirType)64}, {0x0000FF95L, (DirType)64}, {0x0000FFA0L, (DirType)64},
    {0x0000FFABL, (DirType)64}, {0x0000FFB5L, (DirType)64}, {0x0000FFC0L, (DirType)64},
    {0x0000FFCBL, (DirType)64}, {0x0000FFD5L, (DirType)64}, {0x0000FFE0L, (DirType)64},
    {0x0000FFEBL, (DirType)64}, {0x0000FFF5L, (DirType)64}, {0x00000000L, (DirType)64}};

DriveClass::TrackType const DriveClass::Track7[] = {
    {0x0006FFFFL, (DirType)0},  {0x000CFFFEL, (DirType)4},  {0x0011FFFCL, (DirType)8},  {0x0018FFFAL, (DirType)12},
    {0x001FFFF6L, (DirType)16}, {0x0024FFF3L, (DirType)19}, {0x002BFFF0L, (DirType)22}, {0x0030FFFDL, (DirType)23},
    {0x0035FFEBL, (DirType)24}, {0x0038FFE8L, (DirType)25}, {0x003CFFE6L, (DirType)26}, {0x0040FFE3L, (DirType)27},
    {0x0043FFE0L, (DirType)28}, {0x0046FFDDL, (DirType)29}, {0x0043FFDFL, (DirType)30}, {0x0040FFE1L, (DirType)30},
    {0x003CFFE3L, (DirType)30}, {0x0038FFE5L, (DirType)30}, {0x0035FFE7L, (DirType)31}, {0x0030FFE9L, (DirType)31},
    {0x002BFFEBL, (DirType)31}, {0x0024FFEDL, (DirType)31}, {0x001FFFF1L, (DirType)31}, {0x0018FFF4L, (DirType)32},
    {0x0011FFF7L, (DirType)32}, {0x000CFFFAL, (DirType)32}, {0x0006FFFDL, (DirType)32}, {0x00000000L, (DirType)32}};

DriveClass::TrackType const DriveClass::Track8[] = {
    {0x0003FFFCL, (DirType)32}, {0x0006FFF7L, (DirType)36}, {0x000AFFF1L, (DirType)40}, {0x000CFFEBL, (DirType)44},
    {0x000DFFE4L, (DirType)46}, {0x000EFFDCL, (DirType)48}, {0x000FFFD5L, (DirType)50}, {0x0010FFD0L, (DirType)52},
    {0x0011FFC9L, (DirType)54}, {0x0012FFC2L, (DirType)56}, {0x0011FFC0L, (DirType)58}, {0x0010FFC2L, (DirType)60},
    {0x000EFFC9L, (DirType)62}, {0x000CFFCFL, (DirType)64}, {0x000AFFD5L, (DirType)64}, {0x0008FFDAL, (DirType)64},
    {0x0006FFE2L, (DirType)64}, {0x0004FFE9L, (DirType)64}, {0x0002FFEFL, (DirType)64}, {0x0001FFF5L, (DirType)64},
    {0x0000FFF9L, (DirType)64}, {0x00000000L, (DirType)64}};

DriveClass::TrackType const DriveClass::Track9[] = {
    {0xFFF50002L, (DirType)0},  {0xFFEB0004L, (DirType)2},  {0xFFE00006L, (DirType)4},  {0xFFD50009L, (DirType)6},
    {0xFFCE000CL, (DirType)9},  {0xFFC8000FL, (DirType)11}, {0xFFC00012L, (DirType)13}, {0xFFB80015L, (DirType)16},
    {0xFFC00012L, (DirType)18}, {0xFFC8000EL, (DirType)20}, {0xFFCE000AL, (DirType)22}, {0xFFD50004L, (DirType)24},
    {0xFFDE0000L, (DirType)26}, {0xFFE9FFF8L, (DirType)28}, {0xFFEEFFF2L, (DirType)30}, {0xFFF5FFEBL, (DirType)32},
    {0xFFFDFFE1L, (DirType)34}, {0x0002FFD8L, (DirType)36}, {0x0007FFD2L, (DirType)39}, {0x000BFFCBL, (DirType)41},
    {0x0010FFC5L, (DirType)43}, {0x0013FFBEL, (DirType)45}, {0x0015FFB7L, (DirType)48}, {0x0013FFBEL, (DirType)50},
    {0x0011FFC5L, (DirType)52}, {0x000BFFCCL, (DirType)54}, {0x0008FFD4L, (DirType)56}, {0x0005FFDFL, (DirType)58},
    {0x0003FFEBL, (DirType)62}, {0x0001FFF5L, (DirType)64}, {0x00000000L, (DirType)64}};

DriveClass::TrackType const DriveClass::Track10[] = {
    {0xFFF6000BL, (DirType)32}, {0xFFF00015L, (DirType)37}, {0xFFEB0020L, (DirType)42}, {0xFFE9002BL, (DirType)47},
    {0xFFE50032L, (DirType)52}, {0xFFE30038L, (DirType)57}, {0xFFE00040L, (DirType)60}, {0xFFE20038L, (DirType)62},
    {0xFFE40032L, (DirType)64}, {0xFFE5002AL, (DirType)68}, {0xFFE6001EL, (DirType)70}, {0xFFE70015L, (DirType)72},
    {0xFFE8000BL, (DirType)74}, {0xFFE90000L, (DirType)76}, {0xFFE8FFF5L, (DirType)78}, {0xFFE7FFEBL, (DirType)80},
    {0xFFE6FFE0L, (DirType)82}, {0xFFE5FFD5L, (DirType)84}, {0xFFE4FFCEL, (DirType)86}, {0xFFE2FFC5L, (DirType)88},
    {0xFFE0FFC0L, (DirType)90}, {0xFFE3FFC5L, (DirType)92}, {0xFFE5FFCEL, (DirType)94}, {0xFFE9FFD5L, (DirType)95},
    {0xFFEBFFE0L, (DirType)96}, {0xFFF0FFEBL, (DirType)96}, {0xFFF6FFF5L, (DirType)96}, {0x00000000L, (DirType)96}};

DriveClass::TrackType const DriveClass::Track11[] = {{0x01000000L, DIR_SW},
                                                     {0x00F30008L, DIR_SW},
                                                     {0x00E50010L, DIR_SW_X1},
                                                     {0x00D60018L, DIR_SW_X1},
                                                     {0x00C80020L, DIR_SW_X1},
                                                     {0x00B90028L, DIR_SW_X1},
                                                     {0x00AB0030L, DIR_SW_X2},
                                                     {0x009C0038L, DIR_SW_X2},
                                                     {0x008D0040L, DIR_SW_X2},
                                                     {0x007F0048L, DIR_SW_X2},
                                                     {0x00710050L, DIR_SW_X2},
                                                     {0x00640058L, DIR_SW_X2},
                                                     {0x00550060L, DIR_SW_X2},

                                                     {0x00000000L, DIR_SW_X2}};

DriveClass::TrackType const DriveClass::Track12[] = {{0xFF550060L, DIR_SW_X2},
                                                     {0xFF640058L, DIR_SW_X2},
                                                     {0xFF710050L, DIR_SW_X2},
                                                     {0xFF7F0048L, DIR_SW_X2},
                                                     {0xFF8D0040L, DIR_SW_X2},
                                                     {0xFF9C0038L, DIR_SW_X2},
                                                     {0xFFAB0030L, DIR_SW_X2},
                                                     {0xFFB90028L, DIR_SW_X1},
                                                     {0xFFC80020L, DIR_SW_X1},
                                                     {0xFFD60018L, DIR_SW_X1},
                                                     {0xFFE50010L, DIR_SW_X1},
                                                     {0xFFF30008L, DIR_SW},

                                                     {0x00000000L, DIR_SW}};

// Track13 = pure-south WEAP exit (vanilla RA Allied War Factory's authored
// design). Kept active so vanilla Allied AI tanks exit south as they always
// have. TD entries use the separate SW-direction Track14 below — see
// docs/adding-td-buildings.md gotcha #14 for the full story.
#if (1)
/*
**	Drive out of weapon's factory.
*/
DriveClass::TrackType const DriveClass::Track13[] = {
    {XYP_COORD(0, -35), DIR_S}, {XYP_COORD(0, -34), DIR_S}, {XYP_COORD(0, -33), DIR_S}, {XYP_COORD(0, -32), DIR_S},
    {XYP_COORD(0, -31), DIR_S}, {XYP_COORD(0, -30), DIR_S}, {XYP_COORD(0, -29), DIR_S}, {XYP_COORD(0, -28), DIR_S},
    {XYP_COORD(0, -27), DIR_S}, {XYP_COORD(0, -26), DIR_S}, {XYP_COORD(0, -25), DIR_S}, {XYP_COORD(0, -24), DIR_S},
    {XYP_COORD(0, -23), DIR_S}, {XYP_COORD(0, -22), DIR_S}, {XYP_COORD(0, -21), DIR_S}, {XYP_COORD(0, -20), DIR_S},
    {XYP_COORD(0, -19), DIR_S}, {XYP_COORD(0, -18), DIR_S}, {XYP_COORD(0, -17), DIR_S}, {XYP_COORD(0, -16), DIR_S},
    {XYP_COORD(0, -15), DIR_S}, {XYP_COORD(0, -14), DIR_S}, {XYP_COORD(0, -13), DIR_S}, {XYP_COORD(0, -12), DIR_S},
    {XYP_COORD(0, -11), DIR_S}, {XYP_COORD(0, -10), DIR_S}, {XYP_COORD(0, -9), DIR_S},  {XYP_COORD(0, -8), DIR_S},
    {XYP_COORD(0, -7), DIR_S},  {XYP_COORD(0, -6), DIR_S},  {XYP_COORD(0, -5), DIR_S},  {XYP_COORD(0, -4), DIR_S},
    {XYP_COORD(0, -3), DIR_S},  {XYP_COORD(0, -2), DIR_S},  {XYP_COORD(0, -1), DIR_S},

    {0x00000000L, DIR_S}};
#else
/*
**	Drive out of weapon's factory.
*/
DriveClass::TrackType const DriveClass::Track13[] = {{XYP_COORD(10, -21), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(10, -21), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(10, -20), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(10, -20), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(9, -18), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(9, -18), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(9, -17), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(8, -16), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(8, -15), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(7, -14), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(7, -13), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(6, -12), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(6, -11), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(5, -10), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(5, -9), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(4, -8), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(4, -7), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(3, -6), (DirType)(DIR_SW - 10)},
                                                     {XYP_COORD(3, -5), (DirType)(DIR_SW - 9)},
                                                     {XYP_COORD(2, -4), (DirType)(DIR_SW - 7)},
                                                     {XYP_COORD(2, -3), (DirType)(DIR_SW - 5)},
                                                     {XYP_COORD(1, -2), (DirType)(DIR_SW - 3)},
                                                     {XYP_COORD(1, -1), (DirType)(DIR_SW - 1)},

                                                     {0x00000000L, DIR_SW}};
#endif

/*
**  Tiberian Factions mod: Track14 = TD-authentic south-west WEAP exit.
**  Replicates the SW Track13 above (under #if (0)) so we don't disturb
**  vanilla Allied War Factory exit motion (Track13 stays pure-south).
**  Used by TD-prefixed buildings (Logic=WEAP) via TrackControl[67] —
**  OUT_OF_WEAPON_FACTORY_TD. See docs/adding-td-buildings.md gotcha #14.
*/
DriveClass::TrackType const DriveClass::Track14[] = {
    {XYP_COORD(10, -21), (DirType)(DIR_SW - 10)}, {XYP_COORD(10, -21), (DirType)(DIR_SW - 10)},
    {XYP_COORD(10, -20), (DirType)(DIR_SW - 10)}, {XYP_COORD(10, -20), (DirType)(DIR_SW - 10)},
    {XYP_COORD(9, -18), (DirType)(DIR_SW - 10)},  {XYP_COORD(9, -18), (DirType)(DIR_SW - 10)},
    {XYP_COORD(9, -17), (DirType)(DIR_SW - 10)},  {XYP_COORD(8, -16), (DirType)(DIR_SW - 10)},
    {XYP_COORD(8, -15), (DirType)(DIR_SW - 10)},  {XYP_COORD(7, -14), (DirType)(DIR_SW - 10)},
    {XYP_COORD(7, -13), (DirType)(DIR_SW - 10)},  {XYP_COORD(6, -12), (DirType)(DIR_SW - 10)},
    {XYP_COORD(6, -11), (DirType)(DIR_SW - 10)},  {XYP_COORD(5, -10), (DirType)(DIR_SW - 10)},
    {XYP_COORD(5, -9), (DirType)(DIR_SW - 10)},   {XYP_COORD(4, -8), (DirType)(DIR_SW - 10)},
    {XYP_COORD(4, -7), (DirType)(DIR_SW - 10)},   {XYP_COORD(3, -6), (DirType)(DIR_SW - 10)},
    {XYP_COORD(3, -5), (DirType)(DIR_SW - 9)},    {XYP_COORD(2, -4), (DirType)(DIR_SW - 7)},
    {XYP_COORD(2, -3), (DirType)(DIR_SW - 5)},    {XYP_COORD(1, -2), (DirType)(DIR_SW - 3)},
    {XYP_COORD(1, -1), (DirType)(DIR_SW - 1)},    {0x00000000L, DIR_SW}};

/*
**	There are a limited basic number of tracks that a vehicle can follow. These
**	are they. Each track can be interpreted differently but this is controlled
**	by the TrackControl structure elaborated elsewhere.
*/
DriveClass::RawTrackType const DriveClass::RawTracks[14] = {{Track1, -1, 0, -1},
                                                            {Track2, -1, 0, -1},
                                                            {Track3, 37, 12, 22},
                                                            {Track4, 26, 11, 19},
                                                            {Track5, 45, 15, 31},
                                                            {Track6, 44, 16, 27},
                                                            {Track7, -1, 0, -1},
                                                            {Track8, -1, 0, -1},
                                                            {Track9, -1, 0, -1},
                                                            {Track10, -1, 0, -1},
                                                            {Track11, -1, 0, -1},
                                                            {Track12, -1, 0, -1},
                                                            {Track13, -1, 0, -1},
                                                            {Track14, -1, 0, -1}};

/***************************************************************************
**	Smooth turning control table. Given two directions in a path list, this
**	table determines which track to use and what modifying operations need
**	be performed on the track data.
*/
DriveClass::TurnTrackType const DriveClass::TrackControl[68] = {
    {1, 0, DIR_N, F_},                                                      //	0-0
    {3, 7, DIR_NE, F_D},                                                    //	0-1 (raw chart)
    {4, 9, DIR_E, F_D},                                                     //	0-2 (raw chart)
    {0, 0, DIR_SE, F_},                                                     //	0-3 !
    {0, 0, DIR_S, F_},                                                      //	0-4 !
    {0, 0, DIR_SW, F_},                                                     //	0-5 !
    {4, 9, DIR_W, (DriveClass::TrackControlType)(F_X | F_D)},               //	0-6
    {3, 7, DIR_NW, (DriveClass::TrackControlType)(F_X | F_D)},              //	0-7
    {6, 8, DIR_N, (DriveClass::TrackControlType)(F_T | F_X | F_Y | F_D)},   //	1-0
    {2, 0, DIR_NE, F_},                                                     //	1-1 (raw chart)
    {6, 8, DIR_E, F_D},                                                     //	1-2 (raw chart)
    {5, 10, DIR_SE, F_D},                                                   //	1-3 (raw chart)
    {0, 0, DIR_S, F_},                                                      //	1-4 !
    {0, 0, DIR_SW, F_},                                                     //	1-5 !
    {0, 0, DIR_W, F_},                                                      //	1-6 !
    {5, 10, DIR_NW, (DriveClass::TrackControlType)(F_T | F_X | F_Y | F_D)}, //	1-7
    {4, 9, DIR_N, (DriveClass::TrackControlType)(F_T | F_X | F_Y | F_D)},   //	2-0
    {3, 7, DIR_NE, (DriveClass::TrackControlType)(F_T | F_X | F_Y | F_D)},  //	2-1
    {1, 0, DIR_E, (DriveClass::TrackControlType)(F_T | F_X)},               //	2-2
    {3, 7, DIR_SE, (DriveClass::TrackControlType)(F_T | F_X | F_D)},        //	2-3
    {4, 9, DIR_S, (DriveClass::TrackControlType)(F_T | F_X | F_D)},         //	2-4
    {0, 0, DIR_SW, F_},                                                     //	2-5 !
    {0, 0, DIR_W, F_},                                                      //	2-6 !
    {0, 0, DIR_NW, F_},                                                     //	2-7 !
    {0, 0, DIR_N, F_},                                                      //	3-0 !
    {5, 10, DIR_NE, (DriveClass::TrackControlType)(F_Y | F_D)},             //	3-1
    {6, 8, DIR_E, (DriveClass::TrackControlType)(F_Y | F_D)},               //	3-2
    {2, 0, DIR_SE, F_Y},                                                    //	3-3
    {6, 8, DIR_S, (DriveClass::TrackControlType)(F_T | F_X | F_D)},         //	3-4
    {5, 10, DIR_SW, (DriveClass::TrackControlType)(F_T | F_X | F_D)},       //	3-5
    {0, 0, DIR_W, F_},                                                      //	3-6 !
    {0, 0, DIR_NW, F_},                                                     //	3-7 !
    {0, 0, DIR_N, F_},                                                      //	4-0 !
    {0, 0, DIR_NE, F_},                                                     //	4-1 !
    {4, 9, DIR_E, (DriveClass::TrackControlType)(F_Y | F_D)},               //	4-2
    {3, 7, DIR_SE, (DriveClass::TrackControlType)(F_Y | F_D)},              //	4-3
    {1, 0, DIR_S, F_Y},                                                     //	4-4
    {3, 7, DIR_SW, (DriveClass::TrackControlType)(F_X | F_Y | F_D)},        //	4-5
    {4, 9, DIR_W, (DriveClass::TrackControlType)(F_X | F_Y | F_D)},         //	4-6
    {0, 0, DIR_NW, F_},                                                     //	4-7 !
    {0, 0, DIR_N, F_},                                                      //	5-0 !
    {0, 0, DIR_NE, F_},                                                     //	5-1 !
    {0, 0, DIR_E, F_},                                                      //	5-2 !
    {5, 10, DIR_SE, (DriveClass::TrackControlType)(F_T | F_D)},             //	5-3
    {6, 8, DIR_S, (DriveClass::TrackControlType)(F_T | F_D)},               //	5-4
    {2, 0, DIR_SW, F_T},                                                    //	5-5
    {6, 8, DIR_W, (DriveClass::TrackControlType)(F_X | F_Y | F_D)},         //	5-6
    {5, 10, DIR_NW, (DriveClass::TrackControlType)(F_X | F_Y | F_D)},       //	5-7
    {4, 9, DIR_N, (DriveClass::TrackControlType)(F_T | F_Y | F_D)},         //	6-0
    {0, 0, DIR_NE, F_},                                                     //	6-1 !
    {0, 0, DIR_E, F_},                                                      //	6-2 !
    {0, 0, DIR_SE, F_},                                                     //	6-3 !
    {4, 9, DIR_S, (DriveClass::TrackControlType)(F_T | F_D)},               //	6-4
    {3, 7, DIR_SW, (DriveClass::TrackControlType)(F_T | F_D)},              //	6-5
    {1, 0, DIR_W, F_T},                                                     //	6-6
    {3, 7, DIR_NW, (DriveClass::TrackControlType)(F_T | F_Y | F_D)},        //	6-7
    {6, 8, DIR_N, (DriveClass::TrackControlType)(F_T | F_Y | F_D)},         //	7-0
    {5, 10, DIR_NE, (DriveClass::TrackControlType)(F_T | F_Y | F_D)},       //	7-1
    {0, 0, DIR_E, F_},                                                      //	7-2 !
    {0, 0, DIR_SE, F_},                                                     //	7-3 !
    {0, 0, DIR_S, F_},                                                      //	7-4 !
    {5, 10, DIR_SW, (DriveClass::TrackControlType)(F_X | F_D)},             //	7-5
    {6, 8, DIR_W, (DriveClass::TrackControlType)(F_X | F_D)},               //	7-6
    {2, 0, DIR_NW, F_X},                                                    //	7-7

    {11, 11, DIR_SW, F_},    // Backup harvester into refinery.
    {12, 12, DIR_SW_X2, F_}, // Drive back into refinery.
    {13, 13, DIR_SW, F_},    // Drive out of weapons factory (vanilla RA, south motion).
    {14, 14, DIR_SW, F_}     // Drive out of weapons factory (TD-authentic, south-west motion).
};
