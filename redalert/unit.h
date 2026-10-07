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

/* $Header: /CounterStrike/UNIT.H 1     3/03/97 10:26a Joe_bostic $ */
/***********************************************************************************************
 ***              C O N F I D E N T I A L  ---  W E S T W O O D  S T U D I O S               ***
 ***********************************************************************************************
 *                                                                                             *
 *                 Project Name : Command & Conquer                                            *
 *                                                                                             *
 *                    File Name : UNIT.H                                                       *
 *                                                                                             *
 *                   Programmer : Joe L. Bostic                                                *
 *                                                                                             *
 *                   Start Date : April 14, 1994                                               *
 *                                                                                             *
 *                  Last Update : April 14, 1994   [JLB]                                       *
 *                                                                                             *
 *---------------------------------------------------------------------------------------------*
 * Functions:                                                                                  *
 * - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

#ifndef UNIT_H
#define UNIT_H

#include "drive.h"
#include "ftimer.h"

// TF: harvester queue-jump and refinery-choice tuning, ported from CFE Patch Redux (GPL v3): CFE's defaults
// in leptons, compared against straight-line distances.
#define HARV_QUEUE_JUMP_CUTOFF  (4 * CELL_LEPTON_W) // closer harvesters than this are never bumped
#define HARV_UNLOAD_WAIT_WEIGHT (6 * CELL_LEPTON_W) // one queued unload ~= this much extra driving
#define HARV_THRASHING_CUTOFF   (5 * CELL_LEPTON_W) // within this range, use the lower wait penalty
#define HARV_THRASHING_WEIGHT   ((HARV_UNLOAD_WAIT_WEIGHT * 2) / 3)
#define HARV_COMMUNALISM_WEIGHT ((HARV_UNLOAD_WAIT_WEIGHT * 9) / 4)

// TF: bails banked per dock cycle, the same for every harvester and refinery pairing so the economies match.
// It divides every dock time and leaves the animation cadence alone (docs/harvester-docking-rework-plan.md).
#define HARV_DOCK_BAILS_PER_CYCLE 2

class BuildingClass;
class BulletClass;
class HouseClass;
class ObjectTypeClass;

/****************************************************************************
**	For each instance of a unit (vehicle) in the game, there is one of
**	these structures. This structure holds information that is specific
**	and dynamic for a particular unit.
*/
class UnitClass : public DriveClass
{
public:
    /*
    **	This points to the static control data that gives 'this' unit its characteristics.
    */
    CCPtr<UnitTypeClass> Class;

    /*
    **	This records the house flag that this object is currently carrying.
    */
    HousesType Flagged;

    /*
    ** This flag is used for when the harvester dumps ore, to track its
    ** special animation.
    */
    unsigned IsDumping : 1;

    /*
    ** This is a count of the # of loads of the various minerals that the
    ** unit has harvested.
    */
    unsigned Gold : 5;
    unsigned Gems : 5;

    /*
    ** This flag tells a unit that, if after reaching its destination, it
    ** should scatter away.  It's meant to help a LST unload its units by
    ** having its previous passengers get out of the way.
    */
    unsigned IsToScatter : 1;

    /*
    **	This records the number of "loads" of Tiberium the unit is carrying. Only
    **	harvesters use this field.
    */
    int Tiberium;

    /*
    ** This is the area where a mobile gap generator stores the previously-held
    ** shroud values for the cells surrounding itself.
    */
    unsigned int ShroudBits;

    /*
    ** This is the center coordinate for the mobile gap generator, as to
    ** what cells should be revealed (according to ShroudBits)
    */
    CELL ShroudCenter;

    /*
    **	This is the timer that controls the reload rate. The MSAM rocket
    **	launcher is the primary user of this.
    */
    CDTimerClass<FrameTimerClass> Reload;

    // TF: TS walker firing-pose countdown, set to FiringFrames * WalkRate on each shot. While it runs the body
    // draws the firing block instead of the gait.
    CDTimerClass<FrameTimerClass> FireAnim;

    /*
    **	This is the facing of the turret. It can be, and usually is,
    **	rotated independently of the body it is attached to.
    */
    FacingClass SecondaryFacing;

    /*
    **	This is the refinery a harvester is interested in unloading at.
    */
    mutable TARGET TiberiumUnloadRefinery;

    // TF: attack-move minelayer state (CFE Patch Redux port, GPL v3): where it started, and whether it reached
    // the ordered destination and switched to laying.
    TARGET MLoriginalposition;
    unsigned char MLattackmovemode;

    // TF: harvester recovery (docs/harvester-recovery-design.md). Zones ignore buildings, so a walled ore field
    // still looks reachable: path failures blacklist the field for a while instead of retrying it forever.
    enum
    {
        HARV_BLACKLIST_MAX = 4
    };
    CELL HarvTargetCell;                    // ore cell currently being pursued (-1 = none)
    int HarvBestDist;                       // best (closest) distance achieved toward it, in leptons
    long HarvStallFrame;                    // Frame when HarvBestDist last improved (no-progress stall timer)
    int HarvReachableResets;                // stall windows forgiven because A* still finds a path (bounded backstop)
    CELL HarvStuckCell;                      // last cell the harvester occupied (anti-stuck watchdog; -1 = unset)
    long HarvStuckFrame;                     // Frame the harvester last moved/worked (position-stagnation timer)
    // Each blacklist slot holds the bounding box of a whole flood-filled ore field, not one cell.
    CELL HarvBadMin[HARV_BLACKLIST_MAX];    // field bbox top-left  (-1 = empty slot)
    CELL HarvBadMax[HARV_BLACKLIST_MAX];    // field bbox bottom-right
    long HarvBadExpiry[HARV_BLACKLIST_MAX]; // Frame each blacklist entry expires

    // TF: subterranean travel (Devil's Tongue, Subterranean APC), TS's TunnelLocomotionClass ported onto the
    // unit (docs/subterranean-design.md).
    enum TunnelStateType : unsigned char
    {
        TUNNEL_IDLE,       // surfaced, an ordinary vehicle
        TUNNEL_TURNING,    // rotating to face the dig destination
        TUNNEL_DIGGING_IN, // dive ladder playing at the surface (TunnelStep 1..5)
        TUNNEL_TUNNELING,  // underground, out of cell occupancy, moving on Coord
        TUNNEL_EMERGING,   // placed at the exit cell; hull hidden (step 0) then emerge ladder 1..5
        TUNNEL_ABORTING    // dig cancelled mid-ladder; levelling back to idle
    };
    unsigned char TunnelState;
    unsigned char TunnelStep;   // ladder step within DIGGING_IN / EMERGING / ABORTING
    unsigned char TunnelTick;   // frames left in the current step
    unsigned char TunnelFacing; // 0..7 facing snapped at dig start (ladder frame block)
    COORDINATE TunnelDest;      // underground destination (0 when idle)

    // TF: TS DeployToFire stance (the Juggernaut): it fires only when set down and packs up before it moves.
    // DeployNav keeps a move ordered while it is set down or mid-ladder.
    enum DeployStateType : unsigned char
    {
        DEPLOY_MOBILE,
        DEPLOY_DEPLOYING,
        DEPLOY_DEPLOYED,
        DEPLOY_UNDEPLOYING
    };
    unsigned char DeployState;
    unsigned char DeployStep;
    unsigned char DeployTick;
    TARGET DeployNav;
    void Deploy_AI(void);
    void Deploy_Begin(bool deploy);

    /*
    **	TF: the Mobile EM-Pulse's charge. It climbs a frame at a time while the vehicle is not
    **	stunned; a full charge lets it deploy to set off its pulse (EMP_Blast).
    */
    enum
    {
        EMP_CHARGE_FRAMES = 1300,   // FS MaxCharge=1800 at TS Medium speed: 87 s
        EMP_MOBILE_SPREAD = 3,      // cells, the span of its MEMPFX blast
        EMP_MOBILE_STUN_FRAMES = 150 // 10 s
    };
    int EMPCharge;
    void EMP_Blast(void);
    StructType TF_Deploys_Into(void) const;
    CELL TF_Deploy_Origin(void) const;
    COORDINATE TF_Pick_Coord(COORDINATE point) const;

    // TF: TS FireballLauncher stream (Devil's Tongue): frames left after a shot, and its target. Fire_Stream_AI
    // spawns a BULLET_TSFIRE particle every 4 frames (TS SpawnFrames).
    int FireStreamTicks;
    TARGET FireStreamTarget;

    /*
    ** Some additional padding in case we need to add data to the class and maintain backwards compatibility for
    *save/load
    */

    /*---------------------------------------------------------------------
    **	Constructors, Destructors, and overloaded operators.
    */
    static void* operator new(size_t size) noexcept;
    static void* operator new(size_t, void* ptr)
    {
        return (ptr);
    };
    static void operator delete(void* ptr);
    static void operator delete(void*, void*)
    {
    }
    UnitClass(UnitType classid, HousesType house);
    UnitClass(NoInitClass const& x)
        : DriveClass(x)
        , Class(x)
        , Reload(x)
        , SecondaryFacing(x){};
    operator UnitType(void) const
    {
        return Class->Type;
    };
    virtual ~UnitClass(void);

    /*---------------------------------------------------------------------
    **	Member function prototypes.
    */
    virtual ObjectTypeClass const& Class_Of(void) const;
    static void Init(void);

    bool Goto_Clear_Spot(void);
    bool Try_To_Deploy(void);
    virtual void Scatter(COORDINATE threat, bool forced = false, bool nokidding = false);

    int Tiberium_Check(CELL& center, int x, int y);
    int Field_Tiberium_Value(CELL seed, int cap) const; // total harvestable value of the field containing seed (early-exits at cap)
    int Field_Threat_Level(CELL seed) const;            // count of armed enemy technos near a field (skirmish-live, not Cell_Threat)
    bool Flag_Attach(HousesType house);
    bool Flag_Remove(void);
    bool Goto_Tiberium(int radius, bool pathcost = false);
    bool Harvesting(void);
    // TF harvester unreachable-target recovery (see member block above).
    bool Is_Harvest_Blacklisted(CELL cell) const;
    bool Has_Active_Harvest_Blacklist(void) const;
    void Blacklist_Harvest_Cell(CELL cell);
    void APC_Close_Door(void);
    void APC_Open_Door(void);

    unsigned int Apply_Temporary_Jamming_Shroud(HouseClass* house_to_apply_for);
    void Unapply_Temporary_Jamming_Shroud(HouseClass* house_to_unapply_for, unsigned int shroud_bits_applied);

    /*
    **	Query functions.
    */
    bool Should_Crush_It(TechnoClass const* it) const;
    int Credit_Load(void) const;
    virtual DirType Turret_Facing(void) const
    {
        if (Class->IsTurretEquipped)
            return (SecondaryFacing.Current());
        return (PrimaryFacing.Current());
    }
    int Shape_Number(void) const;
    virtual int Pip_Count(void) const;
    virtual InfantryType Crew_Type(void) const;
    virtual DirType Fire_Direction(void) const;
    virtual bool Ok_To_Move(DirType facing) const;
    virtual FireErrorType Can_Fire(TARGET target, int which) const;
    virtual fixed Tiberium_Load(void) const;
    virtual BuildingClass* Find_Best_Refinery(void) const;

    /*
    **	TF: harvester QoL (ported from CFE Patch Redux, GPL v3).
    */
    BuildingClass* Tiberium_Unload_Refinery(void) const;
    void ReconsiderRefinery(BuildingClass* freed = NULL);

    /*
    **	TF: smarter repair bay (ported from CFE Patch Redux, GPL v3) —
    **	pick a sensible cell to vacate the repair pad to.
    */
    bool DoSmarterRunAway(void);

    /*
    **	TF: attack-move (CFE port) — minelayer behaviour: lay a mine here, find the
    **	next free spot nearby, or head back to a repair pad / the starting position.
    */
    bool MinelayerPoopTime(void);
    bool MinelayerGoHome(void);
    bool MinelayerFindSpot(void);

    /*
    **	Coordinate inquiry functions. These are used for both display and
    **	combat purposes.
    */
    virtual COORDINATE Sort_Y(void) const;

    /*
    **	Object entry and exit from the game system.
    */
    virtual bool Limbo(void);
    virtual bool Unlimbo(COORDINATE, DirType facing = DIR_N);

    /*
    **	Display and rendering support functionality. Supports imagery and how
    **	object interacts with the map and thus indirectly controls rendering.
    */
    virtual short const* Overlap_List(bool redraw = false) const;
    virtual void Draw_It(int x, int y, WindowNumberType window) const;

    /*
    **	User I/O.
    */
    virtual ActionType What_Action(CELL cell) const;
    virtual ActionType What_Action(ObjectClass const* object) const;
    virtual void Active_Click_With(ActionType action, ObjectClass* object);
    virtual void Active_Click_With(ActionType action, CELL cell);
    virtual void Response_Select(void);
    virtual void Response_Move(void);
    virtual void Response_Attack(void);
    virtual void Player_Assign_Mission(MissionType mission, TARGET target, TARGET destination);

    /*
    **	Combat related.
    */
    virtual ResultType
    Take_Damage(int& damage, int distance, WarheadType warhead, TechnoClass* source = 0, bool forced = false);
    virtual BulletClass* Fire_At(TARGET target, int which = 0);

    /*
    **	Driver control support functions. These are used to control cell
    **	occupation flags and driver instructions.
    */
    virtual bool Start_Driver(COORDINATE& coord);

    /*
    **	AI.
    */
    virtual TARGET Greatest_Threat(ThreatType threat) const;
    virtual DirType Desired_Load_Dir(ObjectClass* passenger, CELL& moveto) const;
    virtual RadioMessageType Receive_Message(RadioClass* from, RadioMessageType message, int& param);
    virtual void AI(void);
    virtual int Mission_Guard_Area(void);
    virtual int Mission_Unload(void);
    virtual int Mission_Guard(void);
    virtual int Mission_Harvest(void);
    virtual int Mission_Hunt(void);
    virtual int Mission_Repair(void);
    virtual int Mission_Move(void);
    virtual int Mission_Enter(void);
    void Rotation_AI(void);
    void Firing_AI(void);
    void Reload_AI(void);
    bool Edge_Of_World_AI(void);

/*
**	Scenario and debug support.
*/
#ifdef CHEAT_KEYS
    virtual void Debug_Dump(MonoClass* mono) const;
#endif

    /*
    **	Movement and animation.
    */
    virtual void Assign_Destination(TARGET target);
    virtual void Overrun_Square(CELL cell, bool threaten = true);
    virtual void Approach_Target(void);
    virtual int Offload_Tiberium_Bail(void);
    virtual void Enter_Idle_Mode(bool initial = false);
    virtual MoveType Can_Enter_Cell(CELL cell, FacingType facing = FACING_NONE) const;

    /*
    **	TF subterranean cycle -- see the TunnelState members above.
    */
    bool Is_Subterranean(void) const;
    virtual bool Is_Tunneling(void) const;
    bool Is_In_Tunnel_Cycle(void) const
    {
        return (TunnelState != TUNNEL_IDLE);
    }
    bool Should_Dig_To(CELL cell) const;
    CELL Find_Emerge_Cell(CELL cell) const;
    void Tunnel_To(COORDINATE dest);
    void Tunnel_Stop(void);
    void Tunnel_AI(void);
    bool Force_Emerge(void);
    void Tunnel_Explode(void);
    void Tunnel_Begin_Emerge(void);
    void Fire_Stream_Begin(TARGET target);
    void Fire_Stream_AI(void);
    virtual bool Mark(MarkType mark = MARK_CHANGE);
    virtual void Per_Cell_Process(PCPType why);
    void Exit_Repair(void);
    void Shroud_Regen(void);

    /*
    **	File I/O.
    */
    static void Read_INI(CCINIClass& ini);
    static void Write_INI(CCINIClass& ini);
    static const char* INI_Name(void)
    {
        return "UNITS";
    };
    bool Load(Straw& file);
    bool Save(Pipe& file) const;
};

#endif
