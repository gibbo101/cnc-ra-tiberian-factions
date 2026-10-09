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

/* $Header: /CounterStrike/BULLET.CPP 1     3/03/97 10:24a Joe_bostic $ */
/***********************************************************************************************
 ***              C O N F I D E N T I A L  ---  W E S T W O O D  S T U D I O S               ***
 ***********************************************************************************************
 *                                                                                             *
 *                 Project Name : Command & Conquer                                            *
 *                                                                                             *
 *                    File Name : BULLET.CPP                                                   *
 *                                                                                             *
 *                   Programmer : Joe L. Bostic                                                *
 *                                                                                             *
 *                   Start Date : April 23, 1994                                               *
 *                                                                                             *
 *                  Last Update : October 10, 1996 [JLB]                                       *
 *                                                                                             *
 *---------------------------------------------------------------------------------------------*
 * Functions:                                                                                  *
 *   BulletClass::AI -- Logic processing for bullet.                                           *
 *   BulletClass::BulletClass -- Bullet constructor.                                           *
 *   BulletClass::Bullet_Explodes -- Performs bullet explosion logic.                          *
 *   BulletClass::Detach -- Removes specified target from this bullet's targeting system.      *
 *   BulletClass::Draw_It -- Displays the bullet at location specified.                        *
 *   BulletClass::In_Which_Layer -- Fetches the layer that the bullet resides in.              *
 *   BulletClass::Init -- Clears the bullets array for scenario preparation.                   *
 *   BulletClass::Is_Forced_To_Explode -- Checks if bullet should explode NOW.                 *
 *   BulletClass::Mark -- Performs related map refreshing under bullet.                        *
 *   BulletClass::Occupy_List -- Determines the bullet occupation list.                        *
 *   BulletClass::Shape_Number -- Fetches the shape number for the bullet object.              *
 *   BulletClass::Sort_Y -- Sort coordinate for bullet rendering.                              *
 *   BulletClass::Target_Coord -- Fetches coordinate to use when firing on this object.        *
 *   BulletClass::Unlimbo -- Transitions a bullet object into the game render/logic system.    *
 *   BulletClass::delete -- Bullet memory delete.                                              *
 *   BulletClass::new -- Allocates memory for bullet object.                                   *
 *   BulletClass::~BulletClass -- Destructor for bullet objects.                               *
 * - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

#include "function.h"
#include <math.h>

/***********************************************************************************************
 * BulletClass::BulletClass -- Bullet constructor.                                             *
 *                                                                                             *
 *    This is the constructor for the bullet class. It handles all                             *
 *    initialization of the bullet and starting it in motion toward its                        *
 *    target.                                                                                  *
 *                                                                                             *
 * INPUT:   id       -- The type of bullet this is (could be missile).                         *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/02/1994 JLB : Created.                                                                 *
 *   06/20/1994 JLB : Firer is a base class pointer.                                           *
 *   12/10/1994 JLB : Auto calculate range optional.                                           *
 *   12/12/1994 JLB : Handles small arms as an instantaneous effect.                           *
 *   12/23/1994 JLB : Fixed scatter algorithm for non-homing projectiles.                      *
 *   12/31/1994 JLB : Removed range parameter (not needed).                                    *
 *=============================================================================================*/
BulletClass::BulletClass(BulletType id,
                         TARGET target,
                         TechnoClass* payback,
                         int strength,
                         WarheadType warhead,
                         int speed)
    : ObjectClass(RTTI_BULLET, Bullets.ID(this))
    , Class(BulletTypes.Ptr((int)id))
    , Payback(payback)
    , PrimaryFacing(DIR_N)
    , TFStage(0)
    , TFDwell(0)
    , TFUnloaded(0)
    , TFPodHouse(HOUSE_NONE)
    , TFPodApproach(DIR_N)
    , TFPodType(INFANTRY_TDE1)
    , TFBounces(0)
    , TFVelX(0.0)
    , TFVelY(0.0)
    , TFVelZ(0.0)
    , TFPosX(0.0)
    , TFPosY(0.0)
    , TFPosZ(0.0)
    , IsInaccurate(false)
    , IsToAnimate(false)
    , IsLocked(true)
    , TarCom(target)
    , MaxSpeed(speed)
    , Warhead(warhead)
{
    Strength = strength;
    Height = FLIGHT_LEVEL;
}

/***********************************************************************************************
 * BulletClass::~BulletClass -- Destructor for bullet objects.                                 *
 *                                                                                             *
 *    The bullet destructor must detect if a dog has been attached to this bullet. If so,      *
 *    then the attached dog must be unlimboed back onto the map. This operation is necessary   *
 *    because, unlike other objects, the dog flies with the bullet it fires.                   *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/06/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
/*
**	The Mech Division manifest: what the TSMDIV token stands for, disembarked in
**	this order (armour first, escorts last).
*/
static UnitType const _mech_division[] = {UNIT_TSTITN, UNIT_TSTITN, UNIT_TSTITN, UNIT_TSSMEC, UNIT_TSSMEC};
int const MECH_DIVISION_COUNT = (int)(sizeof(_mech_division) / sizeof(_mech_division[0]));

// Where a dropship bay's cargo sets down: the foot of the bay's ramp, on the row south of its plot.
static COORDINATE TF_Bay_Ramp_Foot(BuildingClass const* deck)
{
    return Coord_Add(deck->Center_Coord(), XY_Coord(0x0072, 0x014C));
}

// Spawns one unit at the landed dropship's exit, the foot of the bay's ramp, and walks it to the bay's rally point
// or two rows clear. The paced Mech Division unload and Deliver_Cargo both use it.
void BulletClass::TF_Disembark(HouseClass* owner, UnitType type)
{
    if (owner == NULL) {
        return;
    }
    UnitClass* member = new UnitClass(type, owner->Class->House);
    if (member == NULL) {
        return;
    }

    CELL wcell = Coord_Cell(Coord);
    BuildingClass* deck = Map[wcell].Cell_Building();
    COORDINATE spot = Coord;
    if (deck != NULL && *deck == STRUCT_TSDROP) {
        spot = TF_Bay_Ramp_Foot(deck);
    }
    if (member->Can_Enter_Cell(Coord_Cell(spot)) != MOVE_OK) {
        spot = Cell_Coord(Map.Nearby_Location(Coord_Cell(spot), member->Class->Speed));
    }
    if (member->Unlimbo(spot, DIR_S)) {
        if (deck == NULL || !deck->Rally_Unit(*static_cast<TechnoClass*>(member))) {
            CELL clear = Map.Nearby_Location((CELL)(Coord_Cell(spot) + MAP_CELL_W * 2), member->Class->Speed);
            member->Assign_Destination(::As_Target(clear));
            member->Assign_Mission(MISSION_MOVE);
        }
    } else {
        delete member;
    }
}

// Sets a dropship pod's cargo down at the foot of the bay's ramp and walks it clear; never on the deck, as a unit
// on building cells can't path off them. Safe to call more than once: only the first call delivers.
void BulletClass::Deliver_Cargo(void)
{
    if (Payback == NULL || Payback->What_Am_I() != RTTI_UNIT || !Payback->IsInLimbo) {
        return;
    }

    UnitClass* cargo = (UnitClass*)Payback;
    Payback = NULL; // the pod no longer owns it, whatever happens below

    HouseClass* owner = cargo->House;
    COORDINATE where = Coord;
    CELL wcell = Coord_Cell(where);
    BuildingClass* deck = Map[wcell].Cell_Building();
    if (deck != NULL && *deck == STRUCT_TSDROP) {
        where = TF_Bay_Ramp_Foot(deck);
    }
    // The Mech Division token is an order, never a unit: it must not reach the map. TFUnloaded stops this backstop
    // and the paced unload in AI from delivering a member twice.
    if (cargo->Class->Type == UNIT_TSMDIV) {
        delete cargo;
        cargo = NULL;
        while (TFUnloaded < MECH_DIVISION_COUNT) {
            TF_Disembark(owner, _mech_division[TFUnloaded]);
            TFUnloaded++;
        }
        if (owner != NULL && owner->TFDropBayTimer == 0) {
            owner->TFDropBayTimer = HouseClass::TF_DROPBAY_COOLDOWN;
        }
        return;
    }

    if (cargo->Can_Enter_Cell(Coord_Cell(where)) != MOVE_OK) {
        where = Cell_Coord(Map.Nearby_Location(Coord_Cell(where), cargo->Class->Speed));
    }
    if (cargo->Unlimbo(where, DIR_S)) {
        if (deck == NULL || !deck->Rally_Unit(*static_cast<TechnoClass*>(cargo))) {
            CELL clear = Map.Nearby_Location((CELL)(Coord_Cell(where) + MAP_CELL_W * 2), cargo->Class->Speed);
            cargo->Assign_Destination(::As_Target(clear));
            cargo->Assign_Mission(MISSION_MOVE);
        }
    } else {
        delete cargo;
        cargo = NULL;
    }

    if (owner != NULL && owner->TFDropBayTimer == 0) {
        owner->TFDropBayTimer = HouseClass::TF_DROPBAY_COOLDOWN;
    }
}

BulletClass::~BulletClass(void)
{
    if (GameActive) {

        // TF: a dropship pod's cargo rides it in limbo, as the dog rides its bullet. Delivering it here means no way of
        // destroying the pod strands the vehicle in limbo.
        if (*this == BULLET_TSDROPPOD) {
            Deliver_Cargo();
        }

        /*
        **	SPECIAL CASE:
        **	The dog is attached to the dog bullet in a limbo state. When the bullet is
        **	destroyed, the dog must come back out of limbo at the closest location possible to
        **	the bullet.
        */
        if (Payback != NULL && Payback->What_Am_I() == RTTI_INFANTRY && ((InfantryClass*)Payback)->Class->IsDog) {

            InfantryClass* dog = (InfantryClass*)Payback;
            if (dog) {
                bool unlimbo = false;
                DirType dogface = dog->PrimaryFacing;
                COORDINATE newcoord = Coord;

                /*
                **	Ensure that the coordinate, that the dog is to appear at, is legal. If not,
                **	then find a nearby legal location.
                */
                if (Can_Enter_Cell(newcoord) != MOVE_OK) {
                    newcoord = Map.Nearby_Location(Coord_Cell(newcoord), dog->Class->Speed);
                }

                // TF: unlimboing the dog runs Enter_Idle_Mode, which drops attack-move (CFE port); restored below.
                unsigned int resumeattackmove = dog->AttackMove;
                TARGET resumerememberednavcom = dog->RememberedNavCom;

                /*
                ** Try to put the dog down where the target impacted.  If we can't
                ** put it in that cell, then scan through the adjacent cells,
                ** starting with our current heading, until we find a place where
                ** we can put him down.  If all 8 adjacent cell checks fail, then
                ** just delete the dog.
                */
                for (int i = -1; i < 8; i++) {
                    if (i != -1) {
                        newcoord = Adjacent_Cell(Coord, FacingType(i));
                    }
                    ScenarioInit++;
                    if (dog->Unlimbo(newcoord, dog->PrimaryFacing)) {
                        dog->Mark(MARK_DOWN);
                        dog->Do_Action(DO_DOG_MAUL, true);
                        if (dog->WasSelected) {
                            dog->Select();
                        }
                        ScenarioInit--;

                        unlimbo = true;
                        // TF: restore the dog's attack-move (CFE port).
                        if (resumeattackmove) {
                            dog->AttackMove = 1;
                            dog->RememberedNavCom = resumerememberednavcom;
                            dog->AttackMoveEnterMoveMode();
                        }
                        break;
                    }
                    ScenarioInit--;
                }

                Payback = 0;

                if (!unlimbo) {
                    delete dog;
                }
            }
        }
        BulletClass::Limbo();
    }

    Class = 0;
    Payback = 0;
}

/***********************************************************************************************
 * BulletClass::new -- Allocates memory for bullet object.                                     *
 *                                                                                             *
 *    This function will "allocate" a block of memory for a bullet object.                     *
 *    This memory block is merely lifted from a fixed pool of blocks.                          *
 *                                                                                             *
 * INPUT:   size  -- The size of the memory block needed.                                      *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to an available bullet object block.                        *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/02/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void* BulletClass::operator new(size_t) noexcept
{
    void* ptr = Bullets.Allocate();
    if (ptr) {
        ((BulletClass*)ptr)->Set_Active();
    }
    return (ptr);
}

/***********************************************************************************************
 * BulletClass::delete -- Bullet memory delete.                                                *
 *                                                                                             *
 *    Since bullets memory is merely "allocated" out of a pool, it never                       *
 *    actually gets deleted.                                                                   *
 *                                                                                             *
 * INPUT:   ptr   -- Generic pointer to bullet object.                                         *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/02/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BulletClass::operator delete(void* ptr)
{
    if (ptr) {
        ((BulletClass*)ptr)->IsActive = false;
    }
    Bullets.Free((BulletClass*)ptr);
}

/***********************************************************************************************
 * BulletClass::Occupy_List -- Determines the bullet occupation list.                          *
 *                                                                                             *
 *    This function will determine the cell occupation list and return a pointer to it. Most   *
 *    bullets are small and the list is usually short, but on occasion, it can be a list that  *
 *    rivals the size of regular vehicles.                                                     *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the cell offset list that covers all the cells a bullet  *
 *          is over.                                                                           *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/20/1994 JLB : Created.                                                                 *
 *   01/05/1995 JLB : Handles projectiles with altitude.                                       *
 *=============================================================================================*/
short const* BulletClass::Occupy_List(bool) const
{
    assert(Bullets.ID(this) == ID);
    assert(IsActive);

    /*
    **	Super-gigundo units use the >= 64 coord spillage list logic.
    */
    if (Class->IsGigundo) {
        static short _list[] = {-1,
                                0,
                                1,
                                MAP_CELL_W * 1 - 1,
                                MAP_CELL_W * 1,
                                MAP_CELL_W * 1 + 1,
                                -MAP_CELL_W * 1 - 1,
                                -MAP_CELL_W * 1,
                                -MAP_CELL_W * 1 + 1,
                                MAP_CELL_W * 2 - 1,
                                MAP_CELL_W * 2,
                                MAP_CELL_W * 2 + 1,
                                -MAP_CELL_W * 2 - 1,
                                -MAP_CELL_W * 2,
                                -MAP_CELL_W * 2 + 1,
                                -MAP_CELL_W * 3 - 1,
                                -MAP_CELL_W * 3,
                                -MAP_CELL_W * 3 + 1,
                                REFRESH_EOL};
        return (_list);
        //		return(Coord_Spillage_List(Coord, 64));
    }

    /*
    **	Flying units need a special adjustment to the spillage list to take into account
    **	that the bullet imagery and the shadow are widely separated.
    */
    if (Height > 0) {
        static short _list[25];
        const short* ptr = Coord_Spillage_List(Coord, 5);
        int index = 0;
        CELL cell1 = Coord_Cell(Coord);

        while (ptr[index] != REFRESH_EOL) {
            _list[index] = ptr[index];
            index++;
        }

        COORDINATE coord = Coord_Move(Coord, DIR_N, Height);
        CELL cell2 = Coord_Cell(coord);
        ptr = Coord_Spillage_List(coord, 5);
        while (*ptr != REFRESH_EOL) {
            _list[index++] = *ptr + (cell2 - cell1);
            ptr++;
        }
        _list[index] = REFRESH_EOL;
        return (_list);
    }

    return (Coord_Spillage_List(Coord, 10));
}

/***********************************************************************************************
 * BulletClass::Mark -- Performs related map refreshing under bullet.                          *
 *                                                                                             *
 *    This routine marks the objects under the bullet so that they will                        *
 *    be redrawn. This is necessary as the bullet moves -- objects under                       *
 *    its path need to be restored.                                                            *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/02/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
bool BulletClass::Mark(MarkType mark)
{
    assert(Bullets.ID(this) == ID);
    assert(IsActive);

    if (ObjectClass::Mark(mark)) {
        if (!Class->IsInvisible) {
            Map.Refresh_Cells(Coord_Cell(Coord), Occupy_List());
        }
        return (true);
    }
    return (false);
}

/*
**	The jumpjet a bullet is aimed at, if it is flying in the top map layer. Like an aircraft
**	aloft it is off the cell lists, so a blast cannot find it; it takes its damage directly.
*/
static InfantryClass* TF_Airborne_Jumpjet(TARGET target)
{
    InfantryClass* inf = As_Infantry(target);
    if (inf != NULL && inf->Is_Airborne_Jumpjet() && inf->In_Which_Layer() != LAYER_GROUND) {
        return (inf);
    }
    return (NULL);
}

// The Disc Thrower's disc falls at TS's [General] Gravity=6, halved for a Floater.
static double const TS_FLOATER_GRAVITY = 3.0;

/*
**	The widest a Juggernaut shell strays from its aim point, in leptons: a third of a cell,
**	the range over which the artillery warhead still does most of its damage.
*/
static int const TS_JUGG_SCATTER = 85;

// TS's BulletTypeClass default Elasticity for the disc's bounce, and the band above the ground in which a ballistic
// shot strikes a building, a wall or (once skipping) a cliff.
static double const TS_DISC_ELASTICITY = 0.75;
static int const TS_OBSTACLE_BAND = 150;

// TS's launch angle for a lobbed shot at this speed and gravity across a distance to a height difference (OpenTS
// combat.cpp Calculate_Projectile_Angle). high_arc picks the lobbed answer over the flat one; false when none exists.
static bool TS_Projectile_Angle(bool high_arc, double speed, double distance, double height, double gravity, double& angle)
{
    double dx2 = (distance < 1.0) ? 1.0 : distance * distance;
    double vsq = speed * speed;
    double value = vsq * vsq - 2.0 * vsq * height * gravity - gravity * gravity * dx2;
    if (value < 0.0) {
        return (false);
    }
    double base = vsq - height * gravity;
    double numerator = high_arc ? base - sqrt(value) : base + sqrt(value);
    double cos2 = numerator / (((height * height) / dx2 + 1.0) * 2.0);
    if (cos2 < 0.0) {
        return (false);
    }
    double ratio = sqrt(cos2) / speed;
    angle = acos(ratio > 1.0 ? 1.0 : ratio);
    return (true);
}

// Throws the Disc Thrower's disc as TS throws [Lobbed] (OpenTS TechnoClass::Fire_At), leading a moving vehicle by
// the ground it covers in flight. Returns false, throwing nothing, when no arc reaches the aim point.
bool BulletClass::TS_Disc_Launch(COORDINATE coord)
{
    int lift = 0;
    int range = CELL_LEPTON_W * 9 / 2;
    if (Payback != NULL) {
        TechnoTypeClass const* tclass = Payback->Techno_Type_Class();
        lift = tclass->VerticalOffset;
        coord = Coord_Move(coord, DIR_S, lift);
        for (int which = 0; which < 2; which++) {
            WeaponTypeClass const* weapon = (which == 0) ? tclass->PrimaryWeapon : tclass->SecondaryWeapon;
            if (weapon != NULL && weapon->Bullet != NULL && weapon->Bullet->Type == BULLET_TSLOBBED) {
                range = weapon->Range;
                break;
            }
        }
    }
    int speed = (int)sqrt((double)range * TS_FLOATER_GRAVITY * 1.2);

    COORDINATE tcoord = As_Coord(TarCom);
    int theight = 0;
    TechnoClass const* victim = As_Techno(TarCom);
    if (victim != NULL) {
        theight = victim->Height;
        if (victim->What_Am_I() == RTTI_UNIT && ((UnitClass const*)victim)->IsDriving) {
            UnitClass const* unit = (UnitClass const*)victim;
            int maxspeed = min(unit->Class->MaxSpeed * unit->SpeedBias * unit->House->GroundspeedBias, (int)MPH_LIGHT_SPEED);
            if (unit->IsFormationMove) {
                maxspeed = unit->FormationMaxSpeed;
            }
            if (unit->Flagged != HOUSE_NONE) {
                maxspeed /= 2;
            }
            int ground = maxspeed * fixed(unit->Speed, 256);
            int travel = (int)(::Distance(coord, tcoord) / (speed * 0.9) * ground);
            tcoord = Coord_Move(tcoord, unit->PrimaryFacing.Current(), travel);
        }
    }

    double dx = (double)Coord_X(tcoord) - (double)Coord_X(coord);
    double dy = (double)Coord_Y(tcoord) - (double)Coord_Y(coord);
    double dz = (double)(theight - lift);
    double planar = sqrt(dx * dx + dy * dy);
    double length = sqrt(planar * planar + dz * dz);
    if (speed > length / 2) {
        speed = (int)(length / 2);
    }

    bool high = (dz > 0.0 && planar < dz);
    double angle = 0.0;
    if (speed <= 0 || !TS_Projectile_Angle(high, speed, planar, dz, TS_FLOATER_GRAVITY, angle)) {
        return (false);
    }
    if (!high) {
        double test = angle;
        TS_Projectile_Angle(false, speed, planar + 1.0, dz, TS_FLOATER_GRAVITY, test);
        if (test < angle) {
            angle = -angle;
        }
    }

    Height = 0;
    if (!ObjectClass::Unlimbo(coord)) {
        return (false);
    }
    Map.Remove(this, In_Which_Layer());

    double horizontal = speed * cos(angle);
    TFVelX = (planar > 0.0) ? horizontal * dx / planar : 0.0;
    TFVelY = (planar > 0.0) ? horizontal * dy / planar : 0.0;
    TFVelZ = speed * sin(angle);
    TFPosX = Coord_X(coord);
    TFPosY = Coord_Y(coord);
    TFPosZ = lift;
    TFBounces = 0;
    Height = lift;
    IsFalling = false;
    Riser = 0;
    PrimaryFacing = ::Direction(coord, tcoord);

    Map.Submit(this, In_Which_Layer());
    return (true);
}

// Flies the Disc Thrower's disc on TS's ballistic step for a Bouncy Floater (OpenTS BulletClass::AI). It bounces at
// three quarters speed and goes off on an enemy, water, a cliff, its third touchdown, or once it slows to a crawl.
void BulletClass::TS_Disc_AI(void)
{
    ObjectClass::AI();
    if (!IsActive) {
        return;
    }

    COORDINATE const from = Coord;
    bool forced = false;
    bool collided = false;

    TFVelZ -= TS_FLOATER_GRAVITY;
    double x = TFPosX + TFVelX;
    double y = TFPosY + TFVelY;
    double z = TFPosZ + TFVelZ;

    double const edge = (double)(MAP_CELL_W * CELL_LEPTON_W);
    if (x < 0.0 || y < 0.0 || x >= edge || y >= edge || !Map.In_Radar(Coord_Cell(XY_Coord((int)x, (int)y)))) {
        Mark();
        delete this;
        return;
    }
    COORDINATE coord = XY_Coord((int)x, (int)y);
    CellClass& cell = Map[coord];
    bool const low = (z >= 0.0 && z < TS_OBSTACLE_BAND);

    bool obstacle = false;
    if (low) {
        BuildingClass* building = cell.Cell_Building();
        if (building != NULL) {
            obstacle = (building != Payback && (Payback == NULL || !Payback->House->Is_Ally(building)));
        } else if (cell.Overlay != OVERLAY_NONE && OverlayTypeClass::As_Reference(cell.Overlay).IsWall) {
            obstacle = true;
        }
    }

    if (z < 0.0 || obstacle) {
        z = 0.0;
        TFVelX *= TS_DISC_ELASTICITY;
        TFVelY *= TS_DISC_ELASTICITY;
        TFVelZ *= -TS_DISC_ELASTICITY;

        CELL fromcell = Coord_Cell(from);
        TechnoClass* techno = Map[fromcell].Cell_Techno();
        if ((Payback != NULL && fromcell == Coord_Cell(Payback->Center_Coord()))
            || (techno != NULL && Payback != NULL && Payback->House->Is_Ally(techno))) {
            techno = NULL;
        }
        if (techno != NULL && techno != Payback) {
            forced = true;
            collided = true;
        }

        LandType land = cell.Land_Type();
        if (land == LAND_WATER || land == LAND_RIVER || land == LAND_ROCK) {
            forced = true;
        }

        TFBounces++;
        if (TFBounces >= 3) {
            forced = true;
        }
    } else if (TFBounces > 0 && low && cell.Land_Type() == LAND_ROCK) {
        forced = true;
    }

    if (!forced) {
        TechnoClass* techno = cell.Cell_Techno();
        if (techno != NULL && techno != Payback && (Payback == NULL || !Payback->House->Is_Ally(techno))) {
            COORDINATE hit = techno->Center_Coord();
            double hx = (double)Coord_X(hit) - x;
            double hy = (double)Coord_Y(hit) - y;
            double hz = (double)techno->Height - z;
            if (sqrt(hx * hx + hy * hy + hz * hz) < CELL_LEPTON_W / 2) {
                forced = true;
                coord = hit;
                x = Coord_X(hit);
                y = Coord_Y(hit);
                z = techno->Height;
            }
        }
    }

    double speed = sqrt(TFVelX * TFVelX + TFVelY * TFVelY + TFVelZ * TFVelZ);
    if (speed < 10.0 && Height < 10) {
        forced = true;
    }

    Mark();
    LayerType layer = In_Which_Layer();
    Coord = coord;
    Height = (int)z;
    TFPosX = x;
    TFPosY = y;
    TFPosZ = z;
    if (In_Which_Layer() != layer) {
        Map.Remove(this, layer);
        Map.Submit(this, In_Which_Layer());
    }

    if (forced) {
        if (collided && Target_Legal(TarCom)) {
            COORDINATE tcoord = As_Coord(TarCom);
            ObjectClass const* tobj = As_Object(TarCom);
            double tz = (tobj != NULL) ? (double)tobj->Height : 0.0;
            double mx = (double)Coord_X(tcoord) - x;
            double my = (double)Coord_Y(tcoord) - y;
            double mz = (z + tz) / 2.0 - tz;
            double reach = (speed * 2.0 > CELL_LEPTON_W / 2) ? speed * 2.0 : (double)(CELL_LEPTON_W / 2);
            if (sqrt(mx * mx + my * my + mz * mz) / 3.0 <= reach) {
                Coord = tcoord;
            }
        }
        Bullet_Explodes(true);
        delete this;
    }
}

/***********************************************************************************************
 * BulletClass::AI -- Logic processing for bullet.                                             *
 *                                                                                             *
 *    This routine will perform all logic (flight) logic on the bullet.                        *
 *    Primarily this is motion, fuse tracking, and detonation logic. Call                      *
 *    this routine no more than once per bullet per game tick.                                 *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/02/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BulletClass::AI(void)
{
    assert(Bullets.ID(this) == ID);
    assert(IsActive);

    // TF: the TS SAM missile trails SMOKEY2 puffs (TS art.ini [DRAGON] Trailer=SMOKEY2), each drawn where the
    // missile appears: screen-up is map-north, so it sits north by its height.
    if (*this == BULLET_TSAAHEATSEEKER && !IsInLimbo && (Frame % 3) == 0) {
        new AnimClass(ANIM_TS_SMOKEY2, Coord_Move(Coord, DIR_N, Height));
    }

    // TF: a projectile flying into a live Firestorm is consumed by it, unless the field is its shooter's own (TS).
    if (!IsInLimbo) {
        BuildingClass* wall = TF_Firestorm_Wall_At(Coord_Cell(Coord), Payback != NULL ? Payback->House : NULL);
        if (wall != NULL) {
            TF_Firestorm_Flare(wall->Center_Coord(), Coord, Height);
            delete this;
            return;
        }
    }

    // TF: TD-ported bullets run TD's own AI, and the Disc Thrower's disc flies its own ballistic step.
    if (Class->IsTDPort) {
        AI_TD();
        return;
    }

    if (*this == BULLET_TSLOBBED) {
        TS_Disc_AI();
        return;
    }

    // TF: TS fire-stream particle (OpenTS ParticleClass::Fire_Behavior_AI): it ages a state every TFDwell frames,
    // burns its cell every 3 frames up to state 14 and dies at 19. At its target it burns out instead of exploding.
    if (*this == BULLET_TSFIRE) {
        if (TFDwell <= 0) {
            if (!Target_Legal(TarCom)) {
                TFDwell = 1;
            } else {
                int frames = ::Distance(Coord, ::As_Coord(TarCom)) / max(1, MaxSpeed);
                TFDwell = frames / 15 + 1; // TS: min_time / (FinalDamageState + 1) + 1
            }
        }
        TFStage++;
        int state = TFStage / TFDwell;
        if (state >= 19) {
            delete this;
            return;
        }
        if ((TFStage % 3) == 0 && state <= 14) {
            // A burn can kill, and a death can take neighbours with it, so the cell chain is re-read after every kill,
            // never walked through a saved Next pointer. burnt[] keeps the re-read from burning anything twice.
            ObjectClass* burnt[16];
            int nburnt = 0;
            bool again = true;
            while (again) {
                again = false;
                ObjectClass* optr = Map[Coord_Cell(Coord)].Cell_Occupier();
                while (optr != NULL) {
                    bool seen = false;
                    for (int b = 0; b < nburnt; b++) {
                        if (burnt[b] == optr) {
                            seen = true;
                        }
                    }
                    if (seen || !optr->IsActive || optr->Strength <= 0 || optr == (ObjectClass*)Payback) {
                        optr = optr->Next;
                        continue;
                    }
                    if (nburnt < 16) {
                        burnt[nburnt++] = optr;
                    }
                    WarheadTypeClass const* wh = WarheadTypeClass::As_Pointer(Warhead);
                    int dist = ::Distance(Coord, optr->Center_Coord()) / 10;
                    int modified = Strength * wh->Modifier[optr->Class_Of().Armor];
                    int damage = modified ? modified : 1;
                    int scaled = dist / (wh->SpreadFactor ? wh->SpreadFactor * 1 : 1);
                    scaled = Bound(scaled, 0, 16);
                    if (scaled) {
                        damage = damage / scaled;
                    }
                    if (scaled < 4) {
                        damage = max(damage, Rule.MinDamage);
                    }
                    damage = min(damage, Rule.MaxDamage);
                    ResultType res = RESULT_NONE;
                    if (damage > 0) {
                        res = optr->Take_Damage(damage, 0, WARHEAD_TSFLAMEHIT, Payback);
                    }
                    if (res == RESULT_DESTROYED) {
                        again = true;
                        break;
                    }
                    optr = optr->Next;
                }
            }
        }
        Mark(MARK_CHANGE);
    }

    // TF: the dropship-bay pod flies a VTOL profile over a fixed Coord: down onto the deck, a dwell while the cargo
    // rolls out, then straight up and gone. The fuse and Physics never run for it.
    if (*this == BULLET_TSDROPPOD) {
        ObjectClass::AI();
        if (!IsActive) {
            return;
        }
        Mark(MARK_CHANGE);
        LayerType layer = In_Which_Layer();
        switch (TFStage) {
        case 0:
            if (Height > 3) {
                Height -= max(3, Height / 20);
            } else {
                Height = 0;
                TFStage = 1;
                TFDwell = TICKS_PER_SECOND * 4;
                Sound_Effect(VOC_TS_DROPDWN1, Coord); // TS's own "dropship lands"
            }
            break;

        case 1: {
            TFDwell--;
            bool group = (Payback != NULL && Payback->What_Am_I() == RTTI_UNIT
                          && ((UnitClass*)Payback)->Class->Type == UNIT_TSMDIV);
            if (group) {
                if (TFDwell <= TICKS_PER_SECOND * 3 && TFUnloaded < MECH_DIVISION_COUNT
                    && (TICKS_PER_SECOND * 3 - TFDwell) % 9 == 0) {
                    TF_Disembark(Payback->House, _mech_division[TFUnloaded]);
                    TFUnloaded++;
                    if (TFUnloaded >= MECH_DIVISION_COUNT) {
                        UnitClass* token = (UnitClass*)Payback;
                        Payback = NULL;
                        delete token;
                    }
                }
            } else if (TFDwell == TICKS_PER_SECOND * 2) {
                Deliver_Cargo();
            }
            if (TFDwell <= 0) {
                TFStage = 2;
                Sound_Effect(VOC_TS_DROPUP1, Coord); // TS's own "dropship takes off"
            }
            break;
        }

        default:
            Height += max(8, Height / 12);
            if (Height >= TF_POD_DEPART_CEILING) {
                delete this;
                return;
            }
            break;
        }
        if (In_Which_Layer() != layer) {
            Map.Remove(this, layer);
            Map.Submit(this, In_Which_Layer());
        }
        return;
    }

    // TF: BULLET_TSHUNTER homes on a random enemy from TF_Hunter_Seeker_Acquire, re-acquiring when its victim dies,
    // and kills it on contact. TFPodHouse carries the firing house.
    if (*this == BULLET_TSHUNTER) {
        ObjectClass::AI();
        if (!IsActive) {
            return;
        }
        Mark(MARK_CHANGE);
        LayerType layer = In_Which_Layer();

        enum
        {
            HUNT_SPEED = 42,
            HUNT_DETONATE = 160
        };

        if (!Target_Legal(TarCom)) {
            HouseClass* hptr = (TFPodHouse != HOUSE_NONE) ? HouseClass::As_Pointer(TFPodHouse) : NULL;
            TarCom = (hptr != NULL) ? TF_Hunter_Seeker_Acquire(hptr) : TARGET_NONE;
        }

        if (Target_Legal(TarCom)) {
            COORDINATE tcoord = ::As_Coord(TarCom);
            int dist = Distance(tcoord);
            DirType dir = ::Direction(Coord, tcoord);
            PrimaryFacing.Set(dir);

            if (dist < HUNT_DETONATE) {
                TechnoClass* victim = As_Techno(TarCom);
                Sound_Effect(VOC_TS_HUNTER2, Coord);
                if (victim != NULL && victim->IsActive) {
                    int dmg = victim->Strength + 1000;
                    victim->Take_Damage(dmg, 0, WARHEAD_HE, NULL, true);
                }
                Explosion_Damage(tcoord, 400, NULL, WARHEAD_HE);
                new AnimClass(ANIM_FBALL1, tcoord);
                delete this;
                return;
            }

            Coord = Coord_Move(Coord, dir, HUNT_SPEED);
        }

        if (In_Which_Layer() != layer) {
            Map.Remove(this, layer);
            Map.Submit(this, In_Which_Layer());
        }
        return;
    }

    // TF: the infantry drop pod (OpenTS droppod.cpp) streaks in at TS's 45-degree DropPodAngle, strafing a held LZ,
    // and lands its trooper, or blasts the cell when the trooper can't land. The fuse and Physics never run for it.
    if (*this == BULLET_TSPODDROP) {
        ObjectClass::AI();
        if (!IsActive) {
            return;
        }
        Mark(MARK_CHANGE);
        LayerType layer = In_Which_Layer();
        TFDwell++;

        COORDINATE lz = ::As_Coord(TarCom);

        if (Height > 0) {
            Height -= TF_POD_FALL_SPEED;
            Coord = Coord_Move(Coord, TFPodApproach, TF_POD_FALL_SPEED);

            if (TFDwell % 6 == 0) {
                new AnimClass(ANIM_TS_SMOKEY, Coord_Move(Coord, DIR_N, Height));
            }
            if (TFDwell % 3 == 0) {
                TechnoClass* holder = Map[Coord_Cell(lz)].Cell_Techno();
                HouseClass* hptr = (TFPodHouse != HOUSE_NONE) ? HouseClass::As_Pointer(TFPodHouse) : NULL;
                if (holder != NULL && hptr != NULL && !hptr->Is_Ally(holder)) {
                    COORDINATE hit = Coord_Scatter(lz, CELL_LEPTON_W / 3, false);
                    Sound_Effect(VOC_TS_GUN4, Coord);
                    Explosion_Damage(hit, 2 * TF_POD_STRAFE_DAMAGE, NULL, WARHEAD_SA);
                    new AnimClass(ANIM_PIFFPIFF, hit);
                }
            }
        } else {
            Height = 0;
            Coord = lz;

            InfantryClass* trooper = new InfantryClass(TFPodType, TFPodHouse);
            bool landed = (trooper != NULL) && trooper->Unlimbo(Coord, DIR_S);
            if (landed) {
                new AnimClass((Frame & 1) ? ANIM_TS_DROPPOD2 : ANIM_TS_DROPPOD1, Coord);
                new AnimClass(ANIM_TS_DROPEXP, Coord);
                trooper->Scatter(0, true);
            } else {
                if (trooper != NULL) {
                    delete trooper;
                }
                Explosion_Damage(Coord, 100, NULL, WARHEAD_HE);
                new AnimClass(ANIM_FBALL1, Coord);
            }
            delete this;
            return;
        }

        if (In_Which_Layer() != layer) {
            Map.Remove(this, layer);
            Map.Submit(this, In_Which_Layer());
        }
        return;
    }

    COORDINATE coord;

    ObjectClass::AI();

    if (!IsActive)
        return;

    // TF: the TS SAM missile climbs from the muzzle to flight level, rising half as fast as it flies. Its layer
    // follows its height so Limbo removes it from the right list.
    if (*this == BULLET_TSAAHEATSEEKER && Height < FLIGHT_LEVEL) {
        LayerType layer = In_Which_Layer();
        Height = min(Height + max((int)MaxSpeed / 2, 16), (int)FLIGHT_LEVEL);
        if (In_Which_Layer() != layer) {
            Map.Remove(this, layer);
            Map.Submit(this, In_Which_Layer());
        }
    }

    /*
    **	Ballistic objects are handled here.
    */
    bool forced = false; // Forced explosion.
    if ((Class->IsArcing || Class->IsDropping) && !IsFalling) {
        forced = true;
    }

    /*
    **	Homing projectiles constantly change facing to face toward the target but
    **	they only do so every other game frame (improves game speed and makes
    **	missiles not so deadly).
    */
    if ((Frame & 0x01) && Class->ROT != 0 && Target_Legal(TarCom)) {
        PrimaryFacing.Set_Desired(Direction256(Coord, ::As_Coord(TarCom)));
    }

    /*
    **	Move the projectile forward according to its speed
    **	and direction.
    */
    coord = Coord;
    if (Class->IsFlameEquipped) {
        if (IsToAnimate) {
            if (stricmp(Class->GraphicName, "FB1") == 0) {
                new AnimClass(ANIM_FBALL_FADE, coord, 1);
            } else {
                new AnimClass(ANIM_SMOKE_PUFF, coord, 1);
            }
        }
        IsToAnimate = !IsToAnimate;
    }

    /*
    **	Handle any body rotation at this time. This process must
    **	occur every game fame in order to achieve smooth rotation.
    */
    if (PrimaryFacing.Is_Rotating()) {
        PrimaryFacing.Rotation_Adjust(Class->ROT);
    }
    switch (Physics(coord, PrimaryFacing)) {
    /*
    **	When a projectile reaches the edge of the world, it
    **	vanishes from existence -- presumed to explode off
    **	map.
    */
    case IMPACT_EDGE:
        Mark();
        if (Payback != NULL && Class->Type == BULLET_GPS_SATELLITE) {

            bool reveal = false;
            if (Session.Type != GAME_GLYPHX_MULTIPLAYER) {
                if (Payback->House == PlayerPtr) {
                    reveal = true;
                }
            } else {
                if (Payback->House->IsHuman) {
                    reveal = true;
                }
            }
            if (reveal) {
                if (!Map.Is_Radar_Active()) {
                    Map.Radar_Activate(1);
                }
                for (CELL cell = 0; cell < MAP_CELL_TOTAL; cell++) {
                    Map.Map_Cell(cell, Payback->House);
                }
                Map.RadarClass::Flag_To_Redraw(true);
            }
            Payback->House->IsGPSActive = true;
            Payback->House->IsVisionary = true;
        }
#ifdef OBSOLETE
        /*
        ** Hack: If it's the artificial nukes, don't let the bullets come down (as
        ** they're the only ones that blow up).  We know it's artificial if you're
        ** at tech level 10 or below, because you can't build the nuclear silo until
        ** tech level 15 or so.
        */
        if (Payback != NULL && Class->Type == BULLET_NUKE_UP && Payback->House->Control.TechLevel <= 10) {
            BulletClass* bullet = new BulletClass(
                BULLET_NUKE_DOWN, ::As_Target(Payback->House->NukeDest), Payback, 200, WARHEAD_NUKE, MPH_VERY_FAST);
            if (bullet) {
                int celly = Cell_Y(Payback->House->NukeDest);
                celly -= 15;
                if (celly < 1)
                    celly = 1;
                COORDINATE start = Cell_Coord(XY_Cell(Cell_X(Payback->House->NukeDest), celly));
                if (!bullet->Unlimbo(start, DIR_S)) {
                    delete bullet;
                }
            }
        }
#endif
        delete this;
        break;

    default:
    case IMPACT_NONE:

    /*
    **	The projectile has moved. Check its fuse. If detonation
    **	is signaled, then do so. Otherwise, just move.
    */
    case IMPACT_NORMAL:
        Mark();
        //			if(Class->Type == BULLET_NUKE_DOWN) {
        //				Render(true);
        //			}
        if (Class->Type == BULLET_NUKE_UP) {
            if (Payback != NULL) {
                if (Distance(Payback->As_Target()) > 0x0C00) {
                    delete this;
                    return;
                }
            }
        }
        Coord = coord;

        /*
        **	See if the bullet should be forced to explode now in spite of what
        **	the fuse would otherwise indicate. Maybe the bullet hit a wall?
        */
        if (!forced) {
            forced = Is_Forced_To_Explode(Coord);
        }

        /*
        **	If the bullet is not to explode, then perform normal flight
        **	maintenance (usually nothing). Otherwise, explode and then
        **	delete the bullet.
        */
        // TF: the TS shells (Juggernaut, Tick Tank) and the EMP pulse ball have no proximity fuse: only the arc's end
        // brings them down.
        if (!forced
            && (Class->IsDropping || *this == BULLET_TSBALLISTIC2 || *this == BULLET_TSCANNON || *this == BULLET_TSPULSBALL
                || !Fuse_Checkup(Coord))) {
            /*
            **	Certain projectiles lose strength when they travel.
            */
            if (Class->IsDegenerate && Strength > 5) {
                Strength--;
            }

        } else if (*this == BULLET_TSFIRE) {
            // TF: a fire particle passes through its target; its state, not the fuse, ends it.
        } else {
            Bullet_Explodes(forced);
            delete this;
        }
        break;
    }
}

/***********************************************************************************************
 * BulletClass::Shape_Number -- Fetches the shape number for the bullet object.                *
 *                                                                                             *
 *    Use this routine to fetch a shape number to use for this bullet object.                  *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the shape number to use when drawing this bullet.                     *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   08/06/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
int BulletClass::Shape_Number(void) const
{
    int shapenum = 0;

    // TF: BULLET_TSHUNTER cycles 8 frames; FLAMEALL is 4 axis sets (N/S, NE/SW, E/W, NW/SE) x 19 ageing states.
    if (*this == BULLET_TSHUNTER) {
        return ((Frame / 3) & 7);
    }

    if (*this == BULLET_TSFIRE) {
        int state = TFStage / max(1, TFDwell);
        if (state > 18) {
            state = 18;
        }
        return ((Dir_Facing(PrimaryFacing.Current()) % 4) * 19 + state);
    }

    if (!Class->IsFaceless) {
        shapenum = UnitClass::BodyShape[Dir_To_32(PrimaryFacing)];
    }

    /*
    **	For tumbling projectiles, fetch offset stage.
    */
    if (Class->Tumble > 0) {
        shapenum += Frame % Class->Tumble;
    }

    return (shapenum);
}

/***********************************************************************************************
 * BulletClass::Draw_It -- Displays the bullet at location specified.                          *
 *                                                                                             *
 *    This routine displays the bullet visual at the location specified.                       *
 *                                                                                             *
 * INPUT:   x,y   -- The center coordinate to render the bullet at.                            *
 *                                                                                             *
 *          window   -- The window to clip to.                                                 *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/20/1994 JLB : Created.                                                                 *
 *   06/27/1994 JLB : Takes a window clipping parameter.                                       *
 *   01/08/1995 JLB : Handles translucent colors if necessary.                                 *
 *=============================================================================================*/
void BulletClass::Draw_It(int x, int y, WindowNumberType window) const
{
    assert(Bullets.ID(this) == ID);
    assert(IsActive);

    /*
    **	Certain projectiles aren't visible. This includes small bullets (which are actually
    **	invisible) and flame thrower flames (which are rendered as an animation instead of a projectile).
    */
    if (Class->IsInvisible)
        return;

    /*
    **	If there is no shape loaded for this object, then
    **	it obviously can't be rendered -- just bail.
    */
    void const* shapeptr = Get_Image_Data();
    if (shapeptr == NULL)
        return;

    /*
    **	Get the basic shape number for this projectile.
    */
    int shapenum = Shape_Number();

    /*
    **	For flying projectiles, draw the shadow and adjust the actual projectile body
    **	render position.
    */
    if (Height > 0 && Class->IsShadow) {

        if (Class->IsParachuted) {
            // Add 'this' parameter to call new shape draw intercept. ST - 5/22/2019
            CC_Draw_Shape(this,
                          AnimTypeClass::As_Reference(ANIM_PARA_BOMB).Get_Image_Data(),
                          1,
                          x + Lepton_To_Pixel(Height / 2),
                          y + 10,
                          window,
                          SHAPE_PREDATOR | SHAPE_CENTER | SHAPE_WIN_REL | SHAPE_FADING,
                          NULL,
                          DisplayClass::UnitShadow);
        } else {
            // TF: the dropship's shadow grows as it sinks. A shadow is the body sprite redrawn dark and can't scale, so
            // TSDSHP shapes 1-3 are the silhouette pre-scaled to 55/70/85%, bucketed by height.
            int shadownum = shapenum;
            if (*this == BULLET_TSDROPPOD) {
                if (Height > 960) {
                    shadownum = 1;
                } else if (Height > 640) {
                    shadownum = 2;
                } else if (Height > 320) {
                    shadownum = 3;
                }
            }
            // Add 'this' parameter to call new shape draw intercept. ST - 5/22/2019
            CC_Draw_Shape(this,
                          shapeptr,
                          shadownum,
                          x,
                          y,
                          window,
                          SHAPE_PREDATOR | SHAPE_CENTER | SHAPE_WIN_REL | SHAPE_FADING,
                          NULL,
                          DisplayClass::UnitShadow);
        }
        y -= Lepton_To_Pixel(Height);
    }

    /*
    **	Draw the main body of the projectile.
    */
    ShapeFlags_Type flags = SHAPE_NORMAL;
    if (Class->IsTranslucent) {
        flags = SHAPE_GHOST;
    }
    if (Class->IsSubSurface) {
        // Add 'this' parameter to call new shape draw intercept. ST - 5/22/2019
        CC_Draw_Shape(this,
                      shapeptr,
                      shapenum,
                      x,
                      y,
                      window,
                      flags | SHAPE_PREDATOR | SHAPE_CENTER | SHAPE_WIN_REL | SHAPE_FADING,
                      NULL,
                      DisplayClass::FadingShade);
    } else {
        // Add 'this' parameter to call new shape draw intercept. ST - 5/22/2019
        CC_Draw_Shape(this,
                      shapeptr,
                      shapenum,
                      x,
                      y,
                      window,
                      flags | SHAPE_CENTER | SHAPE_WIN_REL,
                      NULL,
                      DisplayClass::UnitShadow);
    }
}

/***********************************************************************************************
 * BulletClass::Init -- Clears the bullets array for scenario preparation.                     *
 *                                                                                             *
 *    This routine will zero out the bullet tracking list and object array in preparation for  *
 *    the start of a new scenario. All bullets cease to exists after this function is          *
 *    called.                                                                                  *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   08/15/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BulletClass::Init(void)
{
    Bullets.Free_All();
}

/***********************************************************************************************
 * BulletClass::Detach -- Removes specified target from this bullet's targeting system.        *
 *                                                                                             *
 *    When an object is removed from the game system, it must be removed all targeting and     *
 *    tracking systems as well. This routine is used to remove the specified object from the   *
 *    bullet. If the object isn't part of this bullet's tracking system, then no action is     *
 *    performed.                                                                               *
 *                                                                                             *
 * INPUT:   target   -- The target to remove from this tracking system.                        *
 *                                                                                             *
 *          all      -- Is the target going away for good as opposed to just cloaking/hiding?  *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/24/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void BulletClass::Detach(TARGET target, bool all)
{
    assert(Bullets.ID(this) == ID);
    assert(IsActive);

    ObjectClass* obj = As_Object(target);
    if (Payback != NULL && obj == Payback) {

        /*
        ** If we're being called as a result of the dog that fired us being put
        ** in limbo, then don't detach.  If for any other reason, detach.
        */
        if (Payback->What_Am_I() != RTTI_INFANTRY || !((InfantryClass*)Payback)->Class->IsDog) {
            Payback = 0;
        }
    }

    if (all && target == TarCom) {
        TarCom = TARGET_NONE;
    }
}

/***********************************************************************************************
 * BulletClass::Unlimbo -- Transitions a bullet object into the game render/logic system.      *
 *                                                                                             *
 *    This routine is used to take a bullet object that is in limbo and transition it to the   *
 *    game system. A bullet object so transitioned, will be drawn and logic processing         *
 *    performed. In effect, it comes into existence.                                           *
 *                                                                                             *
 * INPUT:   coord -- The location where the bullet object is to appear.                        *
 *                                                                                             *
 *          dir   -- The initial facing for the bullet object.                                 *
 *                                                                                             *
 * OUTPUT:  bool; Was the unlimbo successful?                                                  *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/10/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool BulletClass::Unlimbo(COORDINATE coord, DirType dir)
{
    assert(Bullets.ID(this) == ID);
    assert(IsActive);

    // TF: TD-ported bullets run TD's own Unlimbo, and the Disc Thrower's disc launches on its own arc.
    if (Class->IsTDPort) {
        return (Unlimbo_TD(coord, dir));
    }

    if (*this == BULLET_TSLOBBED) {
        return (TS_Disc_Launch(coord));
    }

    /*
    **	Try to unlimbo the bullet as far as the base class is concerned. Use the already
    **	set direction and strength if the "punt" values were passed in. This allows a bullet
    **	to be setup prior to being launched.
    */
    // TF: the TS SAM missile leaves the launcher at the muzzle and climbs to flight level in AI.
    if (!Class->IsHigh || *this == BULLET_TSAAHEATSEEKER) {
        Height = 0;
    }
    if (ObjectClass::Unlimbo(coord)) {
        Map.Remove(this, In_Which_Layer());

        COORDINATE tcoord = As_Coord(TarCom);

        /*
        **	Homing projectiles (missiles) do NOT override facing. They just fire in the
        **	direction specified and let the chips fall where they may.
        */
        if (Class->ROT == 0 && !Class->IsDropping) {
            dir = Direction(tcoord);
        }

        // TF: the Juggernaut's shell lands within TS_JUGG_SCATTER of its aim point, rolled afresh each shot. The
        // smaller of two rolls keeps the cluster tight, so a fair share of shells land dead on.
        if (*this == BULLET_TSBALLISTIC2) {
            int scatter = min(Random_Pick(0, TS_JUGG_SCATTER), Random_Pick(0, TS_JUGG_SCATTER));
            tcoord = Coord_Move(tcoord, (DirType)Random_Pick(0, 255), scatter);
            dir = Direction(tcoord);
        }

        /*
        **	Possibly adjust the target if this projectile is inaccurate. This occurs whenever
        **	certain weapons are trained upon targets they were never designed to attack. Example: when
        **	turrets or anti-tank missiles are fired at infantry. Indirect
        **	fire is inherently inaccurate.
        */
        if (IsInaccurate || Class->IsInaccurate
            || ((Is_Target_Cell(TarCom) || Is_Target_Infantry(TarCom)) && (Warhead == WARHEAD_AP || Class->IsFueled))) {

            /*
            **	Inaccuracy for low velocity or homing projectiles manifests itself as a standard
            **	Circular Error of Probability (CEP) algorithm. High speed projectiles usually
            **	just overshoot the target by extending the straight line flight.
            */
            if (/*Class->ROT != 0 ||*/ Class->IsArcing) {
                int scatterdist = (::Distance(coord, tcoord) / 16) - 0x0040;
                scatterdist = min(scatterdist, Rule.HomingScatter);
                scatterdist = max(scatterdist, 0);

                dir = (DirType)((dir + (Random_Pick(0, 10) - 5)) & 0x00FF);
                tcoord = Coord_Scatter(tcoord, Random_Pick(0, scatterdist));
            } else {
                int scatterdist = (::Distance(coord, tcoord) / 16) - 0x0040;
                scatterdist = min(scatterdist, Rule.BallisticScatter);
                scatterdist = max(scatterdist, 0);
                tcoord = Coord_Move(tcoord, dir, Random_Pick(0, scatterdist));
            }
        }

        /*
        **	For very fast and invisible projectiles, just make the projectile exist at the target
        **	location and dispense with the actual flight.
        */
        if (MaxSpeed == MPH_LIGHT_SPEED && Class->IsInvisible) {
            // TF: an instant shot stops at the first live Firestorm on its path, which consumes it next frame.
            COORDINATE wall = TF_Firestorm_On_Path(Coord, tcoord, Payback != NULL ? Payback->House : NULL);
            Coord = (wall != 0) ? wall : tcoord;
        }

        /*
        **	Set the range equal to either the class defined range or the calculated
        **	number of game frames it would take for the projectile to reach the target.
        */
        int range = 0xFF;
        if (!Class->IsDropping) {
            range = (::Distance(tcoord, Coord) / MaxSpeed) + 4;
        }

        /*
        **	Projectile speed is usually the default value for that projectile, but
        **	certain projectiles alter speed according to the distance to the
        **	target.
        */
        int speed = MaxSpeed;
        if (speed == MPH_LIGHT_SPEED)
            speed = MPH_IMMOBILE;
        if (Class->IsArcing) {
            speed = MaxSpeed + (Distance(tcoord) / 32);

            /*
            **	Set minimum speed (i.e., distance) for arcing projectiles.
            */
            speed = max(speed, 25);
        }
        if (!Class->IsDropping) {
            Fly_Speed(255, (MPHType)speed);
        }

        /*
        **	Arm the fuse.
        */
        Arm_Fuse(Coord, tcoord, range, ((As_Aircraft(TarCom) != 0) ? 0 : Class->Arming));

        /*
        **	Projectiles that make a ballistic flight to impact point must determine a
        **	vertical component for the projectile launch. This is crudely simulated
        **	by biasing ground speed according to target distance and then giving
        **	enough vertical velocity to keep the projectile airborne for the
        **	desired amount of time. The mathematically correct solution would be to
        **	calculate launch angle (given fixed projectile velocity) and then derive
        **	the vertical and horizontal components. That solution would require a
        **	square root and an arcsine lookup table. OUCH!
        */
        Riser = 0;
        if (Class->IsArcing) {
            IsFalling = true;
            Height = 1;
            Riser = ((Distance(tcoord) / 2) / (speed + 1)) * Rule.Gravity;
            Riser = max(Riser, 10);

            // TF: the TS shells (Juggernaut, Tick Tank) and the EMP pulse ball fly the true distance to their aim in
            // whole frames and land on the last. The stock arithmetic and ::Distance's diagonal overstatement land wide.
            if (*this == BULLET_TSBALLISTIC2 || *this == BULLET_TSCANNON || *this == BULLET_TSPULSBALL) {
                double adx = (double)((int)Coord_X(tcoord) - (int)Coord_X(Coord));
                double ady = (double)((int)Coord_Y(tcoord) - (int)Coord_Y(Coord));
                int dist = (int)(sqrt(adx * adx + ady * ady) + 0.5);
                int frames = max(4, (dist + speed - 1) / speed);
                speed = max(1, (dist + frames - 1) / frames);
                Fly_Speed(255, (MPHType)speed);
                Riser = max(1, (Rule.Gravity * (frames - 1)) / 2 - 1);
#if TF_DEV_BUILD
                if (*this == BULLET_TSBALLISTIC2) {
                    const char* prof = getenv("USERPROFILE");
                    char path[512];
                    snprintf(path, sizeof(path), "%s/Documents/CnCRemastered/MOD_DEBUG_TSUNITS.txt", prof ? prof : ".");
                    FILE* lf = fopen(path, "a");
                    if (lf != NULL) {
                        fprintf(lf, "frame=%d JUGG-LAUNCH from=(%d,%d) aim=(%d,%d) target=(%d,%d) dist=%d frames=%d speed=%d riser=%d dir=%d\n",
                                (int)Frame, (int)Coord_X(Coord), (int)Coord_Y(Coord), (int)Coord_X(tcoord), (int)Coord_Y(tcoord),
                                (int)Coord_X(As_Coord(TarCom)), (int)Coord_Y(As_Coord(TarCom)), dist, frames, speed,
                                (int)Riser, (int)dir);
                        fclose(lf);
                    }
                }
#endif
            }
        }
        if (Class->IsDropping) {
            IsFalling = true;
            Height = FLIGHT_LEVEL;
            //			Height = Pixel_To_Lepton(24);
            Riser = 0;
            if (Class->IsParachuted) {
                AnimClass* anim = new AnimClass(ANIM_PARA_BOMB, Target_Coord());
                //				AnimClass * anim = new AnimClass(ANIM_PARACHUTE, Target_Coord());
                if (anim) {
                    anim->Attach_To(this);
                }
            }
        }
        Map.Submit(this, In_Which_Layer());

        PrimaryFacing = dir;
        return (true);
    }
    return (false);
}

// TD's BulletClass::Unlimbo, ported for TD-port bullets with RA's layer bookkeeping (docs/td-atwr-deep-dive.md).
// IsFalling stays clear: AI_TD integrates the fall itself, and ObjectClass::AI would integrate it a second time.
bool BulletClass::Unlimbo_TD(COORDINATE coord, DirType dir)
{
    assert(Bullets.ID(this) == ID);
    assert(IsActive);

    if (!Class->IsHigh) {
        Height = 0;
    }

    if (ObjectClass::Unlimbo(coord)) {
        Map.Remove(this, In_Which_Layer());

        COORDINATE tcoord = As_Coord(TarCom);

        if (!Class->IsHoming && !Class->IsDropping) {
            dir = Direction(tcoord);
        }

        if (IsInaccurate || Class->IsInaccurate
            || ((Is_Target_Cell(TarCom) || Is_Target_Infantry(TarCom))
                && (Class->ClassWarhead == WARHEAD_AP || Class->IsFueled))) {

            if (Class->IsHoming || Class->IsArcing) {
                int scatterdist = ::Distance(coord, tcoord) / 3;
                scatterdist = min(scatterdist, 0x0200);

                // TD's BULLET_GRENADE special-case (Unlimbo:669-672) — narrower
                // scatter for grenades. No TD grenade port yet; kept as note.
                // if (*this == BULLET_GRENADE) {
                //     scatterdist = ::Distance(coord, tcoord) / 4;
                //     scatterdist = min(scatterdist, 0x0080);
                // }

                dir = (DirType)((dir + (Random_Pick(0, 10) - 5)) & 0x00FF);
                tcoord = Coord_Scatter(tcoord, Random_Pick(0, scatterdist));
            } else {
                tcoord = Coord_Move(tcoord, dir, Random_Pick(0, 0x0100));
            }

            if (Payback) {
                if (!Payback->In_Range(tcoord, 0) && !Payback->In_Range(tcoord, 1)) {
                    tcoord = Coord_Move(tcoord,
                                        ::Direction(tcoord, Coord),
                                        Distance(tcoord) - max(Payback->Weapon_Range(0), Payback->Weapon_Range(1)));
                }
            }
        }

        if (MaxSpeed == MPH_LIGHT_SPEED && Class->IsInvisible) {
            COORDINATE wall = TF_Firestorm_On_Path(Coord, tcoord, Payback != NULL ? Payback->House : NULL);
            Coord = (wall != 0) ? wall : tcoord;
        }

        int range = 0xFF;
        if (!Class->BulletRange) {
            if (!Class->IsDropping) {
                range = (::Distance(tcoord, Coord) / MaxSpeed) + 4;
            }
        } else {
            range = Class->BulletRange;
        }

        int speed = MaxSpeed;
        if (speed == MPH_LIGHT_SPEED)
            speed = MPH_IMMOBILE;
        if (Class->IsArcing) {
            speed = MaxSpeed + (Distance(tcoord) >> 5);
            speed = max(speed, 25);
        }
        if (!Class->IsDropping) {
            Fly_Speed(255, (MPHType)speed);
        }

        Arm_Fuse(Coord, tcoord, range, ((As_Aircraft(TarCom) != 0) ? 0 : Class->Arming));

        Riser = 0;
        if (Class->IsArcing) {
            Height = 1;
            Riser = ((Distance(tcoord) / 2) / (speed + 1)) * Rule.Gravity;
            Riser = max(Riser, 10);
        }
        if (Class->IsDropping) {
            Height = FLIGHT_LEVEL;
            Riser = 0;
            if (Class->IsParachuted) {
                AnimClass* anim = new AnimClass(ANIM_PARA_BOMB, Target_Coord());
                if (anim) {
                    anim->Attach_To(this);
                }
            }
        }

        Map.Submit(this, In_Which_Layer());

        PrimaryFacing = dir;

        return (true);
    }
    return (false);
}

// TD's BulletClass::AI, ported for TD-port bullets (docs/td-atwr-deep-dive.md). It alone integrates their ballistic
// fall: IsFalling stays clear, so ObjectClass::AI doesn't integrate it a second time.
void BulletClass::AI_TD(void)
{
    assert(Bullets.ID(this) == ID);
    assert(IsActive);

    COORDINATE coord;

    ObjectClass::AI();

    bool forced = false; // Forced explosion.
    LayerType startlayer = In_Which_Layer();
    if (Class->IsArcing) {
        Height += Riser;
        if (Height <= 0) {
            forced = true;
        }
        if (Riser > -100) {
            Riser -= Rule.Gravity;
        }
    }
    if (Class->IsDropping) {
        Height += Riser;
        if (Height <= 0) {
            forced = true;
        }
        if (Riser > -100) {
            Riser -= 1;
        }
    }

    // Limbo removes the bullet from In_Which_Layer(), so its layer must follow Height as it falls, or the removal
    // misses and the layer keeps a deleted bullet.
    if ((Class->IsArcing || Class->IsDropping) && In_Which_Layer() != startlayer) {
        Map.Remove(this, startlayer);
        Map.Submit(this, In_Which_Layer());
    }

    if ((Frame & 0x01) && Class->IsHoming && Target_Legal(TarCom)) {
        PrimaryFacing.Set_Desired(Direction256(Coord, ::As_Coord(TarCom)));
    }

    coord = Coord;
    if (Class->IsFlameEquipped) {
        if (IsToAnimate) {
            new AnimClass(ANIM_SMOKE_PUFF, coord, 1);
        }
        IsToAnimate = !IsToAnimate;
    }

    if (PrimaryFacing.Is_Rotating()) {
        PrimaryFacing.Rotation_Adjust(Class->ROT);
    }

    switch (Physics(coord, PrimaryFacing)) {
    case IMPACT_EDGE:
        Mark();
        delete this;
        break;

    default:
    case IMPACT_NONE:
    case IMPACT_NORMAL:
        Mark();
        if (!Class->IsHigh) {
            CellClass* cellptr = &Map[Coord_Cell(coord)];
            if (cellptr->Overlay != OVERLAY_NONE && OverlayTypeClass::As_Reference(cellptr->Overlay).IsHigh) {
                forced = true;
                Coord = coord = Cell_Coord(Coord_Cell(coord));
            }
        }

        if (Class->IsAntiAircraft && (As_Aircraft(TarCom) || TF_Airborne_Jumpjet(TarCom)) && Distance(TarCom) < 0x0080) {
            forced = true;
            if (*this == BULLET_SSM) {  // TD: BULLET_TOW
                Strength += Strength / 3;
            } else {
                Strength += Strength / 2;
            }
        }

        if (!forced && (Class->IsDropping || !Fuse_Checkup(coord))) {
            Coord = coord;
            Mark();

            /*
            **	TD's BULLET_BULLET branch — strength decay during flight for the
            **	small-arms invisible bullet. No TD small-arms port yet; kept as note.
            **	if (*this == BULLET_BULLET) { if (Strength > 5) Strength--; }
            */

        } else {

            Mark();
            if (!forced && !Class->IsArcing && !Class->IsHoming && Fuse_Target()) {
                Coord = Fuse_Target();
            }
            if ((!Is_Target_Aircraft(TarCom) || As_Aircraft(TarCom)->In_Which_Layer() == LAYER_GROUND)
                && TF_Airborne_Jumpjet(TarCom) == NULL) {
                Explosion_Damage(Coord, Strength, Payback, Class->ClassWarhead);
            } else {

                if (Distance(TarCom) < 0x0080) {
                    TechnoClass* object = As_Aircraft(TarCom);
                    if (object == NULL) {
                        object = TF_Airborne_Jumpjet(TarCom);
                    }

                    int str = Strength;
                    if (object)
                        object->Take_Damage(str, 0, Class->ClassWarhead, Payback);
                }
            }

            if (Class->IsInvisible) {
                Coord = Coord_Scatter(Coord, 0x0020);
            }
            if (Class->ImpactAnim != ANIM_NONE) {
                AnimClass* newanim = new AnimClass(Class->ImpactAnim, Coord);
                if (newanim) {
                    newanim->Sort_Above(TarCom);
                }

                if (newanim && Class->ImpactAnim == ANIM_ATOM_BLAST && newanim->Owner() == HOUSE_NONE) {
                    if (Payback && Payback->House && Payback->House->Class) {
                        newanim->Set_Owner(Payback->House->Class->House);
                    }
                }
            }
            delete this;
            return;
        }
        break;
    }
}

/***********************************************************************************************
 * BulletClass::Target_Coord -- Fetches coordinate to use when firing on this object.          *
 *                                                                                             *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the coordinate that should be used when firing at the object.         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/21/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
COORDINATE BulletClass::Target_Coord(void) const
{
    assert(Bullets.ID(this) == ID);
    assert(IsActive);

    return (Coord_Add(XY_Coord(0, -Height), Coord));
}

/***********************************************************************************************
 * BulletClass::Sort_Y -- Sort coordinate for bullet rendering.                                *
 *                                                                                             *
 *    This will return the coordinate to use when sorting this bullet in the display list.     *
 *    Typically, this only occurs for bullets in the ground layer. Since bullets are to be     *
 *    seen a bit more than the normal sorting order would otherwise imply, bias the sort       *
 *    value such that bullets will tend to be drawn on top of the objects.                     *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the coordinate to use when sorting this bullet in the display list.   *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/02/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
COORDINATE BulletClass::Sort_Y(void) const
{
    assert(this != 0);
    assert(IsActive);

    // TF: the landed dropship pod sits over its bay in the ground layer, and a building's sort band reaches its
    // south edge. Three cells of bias clears the pad's south edge, so the pad never draws over the ship.
    if (*this == BULLET_TSDROPPOD) {
        return (Coord_Move(Coord, DIR_S, CELL_LEPTON_H * 3));
    }

    return (Coord_Move(Coord, DIR_S, CELL_LEPTON_H / 2));
}

/***********************************************************************************************
 * BulletClass::In_Which_Layer -- Fetches the layer that the bullet resides in.                *
 *                                                                                             *
 *    This examines the bullet to determine what rendering layer it should be in. The          *
 *    normal logic applies unless this is a torpedo. A torpedo is always in the surface        *
 *    layer.                                                                                   *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the render layer that this bullet should reside in.                   *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/10/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
LayerType BulletClass::In_Which_Layer(void) const
{
    if (Class->IsSubSurface) {
        return (LAYER_SURFACE);
    }
    return (ObjectClass::In_Which_Layer());
}

/***********************************************************************************************
 * BulletClass::Is_Forced_To_Explode -- Checks if bullet should explode NOW.                   *
 *                                                                                             *
 *    This routine will examine the bullet and where it is travelling in order to determine    *
 *    if it should prematurely explode. Typical of this would be when a bullet hits a wall     *
 *    or a torpedo hits a ship -- regardless of where the projectile was originally aimed.     *
 *                                                                                             *
 * INPUT:   coord -- The new coordinate to place the bullet at presuming it is forced to       *
 *                   explode and a modification of the bullet's coordinate is needed.          *
 *                   Otherwise, the coordinate is not modified.                                *
 *                                                                                             *
 * OUTPUT:  bool; Should the bullet explode now?                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/10/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
bool BulletClass::Is_Forced_To_Explode(COORDINATE& coord) const
{
    coord = Coord;
    CellClass const* cellptr = &Map[coord];

    /*
    **	Check for impact on a wall or other high obstacle.
    */
    if (!Class->IsHigh && cellptr->Overlay != OVERLAY_NONE && OverlayTypeClass::As_Reference(cellptr->Overlay).IsHigh) {
        coord = Cell_Coord(Coord_Cell(coord));
        return (true);
    }

    /*
    **	Check to make sure that underwater projectiles (torpedoes) will not
    **	travel in anything but water.
    */
    if (Class->IsSubSurface) {
        int d = ::Distance(Coord_Fraction(coord), XY_Coord(CELL_LEPTON_W / 2, CELL_LEPTON_W / 2));
        if (cellptr->Land_Type() != LAND_WATER
            || (d < CELL_LEPTON_W / 3 && cellptr->Cell_Techno() != NULL && cellptr->Cell_Techno() != Payback)) {

            /*
            **	Force explosion to be at center of techno object if one is present.
            */
            if (cellptr->Cell_Techno() != NULL) {
                coord = cellptr->Cell_Techno()->Target_Coord();
            }

            /*
            **	However, if the torpedo was blocked by a bridge, then force the
            **	torpedo to explode on top of that bridge cell.
            */
            if (cellptr->Is_Bridge_Here()) {
                coord = Coord_Snap(coord);
            }

            return (true);
        }
    }

    /*
    **	Bullets are generally more effective when they are fired at aircraft.
    */
    if (Class->IsAntiAircraft && (As_Aircraft(TarCom) || TF_Airborne_Jumpjet(TarCom)) && Distance(TarCom) < 0x0080) {
        return (true);
    }

    /*
    **	No reason for forced explosion was detected, so return 'false' to
    **	indicate that no forced explosion is required.
    */
    return (false);
}

/***********************************************************************************************
 * BulletClass::Bullet_Explodes -- Performs bullet explosion logic.                            *
 *                                                                                             *
 *    This handles the exploding bullet action. It will generate the animation and the         *
 *    damage as necessary.                                                                     *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   The bullet should be deleted after this routine is called.                      *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/10/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void BulletClass::Bullet_Explodes(bool forced)
{
    // TF: the TS shells (Juggernaut, Tick Tank) and the EMP pulse ball burst on their aim point when the arc ends within
    // a cell of it, so the flight's rounding never moves the burst (for the Juggernaut, the point its scatter rolled).
    if ((*this == BULLET_TSBALLISTIC2 || *this == BULLET_TSCANNON || *this == BULLET_TSPULSBALL) && forced
        && Fuse_Target() != 0
        && ::Distance(Coord, Fuse_Target()) < CELL_LEPTON_W) {
        Coord = Fuse_Target();
    }
#if TF_DEV_BUILD
    if (*this == BULLET_TSBALLISTIC2) {
        const char* prof = getenv("USERPROFILE");
        char path[512];
        snprintf(path, sizeof(path), "%s/Documents/CnCRemastered/MOD_DEBUG_TSUNITS.txt", prof ? prof : ".");
        FILE* lf = fopen(path, "a");
        if (lf != NULL) {
            COORDINATE tc = Target_Legal(TarCom) ? As_Coord(TarCom) : 0;
            fprintf(lf, "frame=%d JUGG-SHELL impact at=(%d,%d) off=(%d,%d) target=%s dist=%d aimoff=(%d,%d) forced=%d height=%d\n", (int)Frame,
                    (int)Coord_X(Coord), (int)Coord_Y(Coord), (int)Coord_X(Coord) - (int)Coord_X(tc), (int)Coord_Y(Coord) - (int)Coord_Y(tc),
                    Target_Legal(TarCom) ? "yes" : "none", tc ? (int)::Distance(Coord, tc) : -1,
                    (int)Coord_X(Coord) - (int)Coord_X(Fuse_Target()), (int)Coord_Y(Coord) - (int)Coord_Y(Fuse_Target()), (int)forced, (int)Height);
            fclose(lf);
        }
    }
#endif
    // TF: a delivery pod arrives rather than detonating: no damage, and the destructor sets its cargo down. It is a
    // projectile so no aircraft radio or docking handshake is involved; a wrong handshake freezes the game.
    if (*this == BULLET_TSDROPPOD) {
        return;
    }

    // TF: the EMP Cannon's pulse ball does no damage: it plays one of TS's two pulse impacts at random and sets off
    // a pulse reaching 3 cells, the span of the impact ring (docs/emp-cannon-design.md).
    if (*this == BULLET_TSPULSBALL) {
        enum { EMP_CANNON_SPREAD = 3 };
        new AnimClass(Random_Pick(0, 1) ? ANIM_TS_PULSEFX2 : ANIM_TS_PULSEFX1, Coord);
        TF_EMPulse(Coord_Cell(Coord), Payback, EMP_CANNON_SPREAD, TechnoClass::EMP_STUN_FRAMES);
        return;
    }

    /*
    **	When the target is reached, explode and do the damage
    **	required of it. For homing objects, don't force the explosion to
    **	match the target position. Non-homing projectiles adjust position so
    **	that they hit the target. This compensates for the error in line of
    **	flight logic.
    */
    if ((Payback != NULL && Payback->What_Am_I() == RTTI_INFANTRY && ((InfantryClass*)Payback)->Class->IsDog)
        || (!forced && !Class->IsArcing && Class->ROT == 0 && Fuse_Target())) {
        Coord = Fuse_Target();
    }

    // TF: the RPG tower's canister goes off on its target's centre when it lands near it, by TS's rule: a third of
    // the landing distance within the greater of half a cell and two frames' flight.
    if (*this == BULLET_TSLOBBED2) {
        TechnoClass* victim = As_Techno(TarCom);
        if (victim != NULL && victim->IsActive && !victim->IsInLimbo) {
            COORDINATE vcoord = victim->Center_Coord();
            if (::Distance(Coord, vcoord) / 3 <= max(CELL_LEPTON_W / 2, (int)MaxSpeed * 2)) {
                Coord = vcoord;
            }
        }
    }

    /*
    **	Non-aircraft targets apply damage to the ground.
    */
    if ((!Is_Target_Aircraft(TarCom) || As_Aircraft(TarCom)->In_Which_Layer() == LAYER_GROUND)
        && TF_Airborne_Jumpjet(TarCom) == NULL) {
        Explosion_Damage(Coord, Strength, Payback, Warhead);
        if (!IsActive)
            return;

    } else {

        /*
        **	Special damage apply for SAM missiles. This is the only way that missile
        **	damage affects the aircraft target.
        */
        // TF: an airborne jumpjet takes this damage too, as an aircraft aloft does.
        if (Distance(TarCom) < 0x0080) {
            TechnoClass* object = As_Aircraft(TarCom);
            if (object == NULL) {
                object = TF_Airborne_Jumpjet(TarCom);
            }

            int str = Strength;
            if (object)
                object->Take_Damage(str, 0, Warhead, Payback);
        }
    }

    /*
    **	For projectiles that are invisible while travelling toward the target,
    **	allow scatter effect for the impact animation.
    */
    if (Class->IsInvisible) {
        Coord = Coord_Scatter(Coord, 0x0020);
    }

    /*
    **	Fetch the land type that the explosion will be upon. Special case for
    **	flying aircraft targets, their land type will be LAND_NONE.
    */
    CellClass const* cellptr = &Map[Coord];
    LandType land = cellptr->Land_Type();
    if ((Is_Target_Aircraft(TarCom) && As_Aircraft(TarCom)->In_Which_Layer() == LAYER_TOP)
        || TF_Airborne_Jumpjet(TarCom) != NULL) {
        land = LAND_NONE;
    }

    AnimType anim = Combat_Anim(Strength, Warhead, land);

    /*
    ** If it's a water explosion that's going to play, don't play it
    ** if its cell is the same as the center cell of the target ship.
    */
    if (anim >= ANIM_WATER_EXP1 && anim <= ANIM_WATER_EXP3 && Is_Target_Vessel(TarCom)) {
        if (Coord_Cell(Coord) == Coord_Cell(As_Vessel(TarCom)->Center_Coord())) {
            anim = (AnimType)(ANIM_VEH_HIT1 + (anim - ANIM_WATER_EXP1));
        }
    }

    if (anim != ANIM_NONE) {
        AnimClass* aptr = new AnimClass(anim, Coord);
        if (aptr) {
            aptr->Sort_Above(TarCom);
        }
        /*
        ** Special case trap: if they're making the nuclear explosion,
        ** and no anim is available, force the nuclear damage anyway
        ** because nuke damage is done in the middle of the animation
        ** and if there's no animation, there won't be any damage.
        */
        if (!aptr && anim == ANIM_ATOM_BLAST) {
            GlyphX_Debug_Print("FAILED to create ANIM_ATOM_BLAST");
            HousesType house = HOUSE_NONE;
            if (Payback) {
                house = Payback->House->Class->House;
            }
            AnimClass::Do_Atom_Damage(house, Coord_Cell(Coord));
        }

        // MBL 05.20.2020
        // Fix for Nuke or Atom Bomb killing structures and units during animation sequence and not getting kills
        // tracked Per https://jaas.ea.com/browse/TDRA-6610
        //
        else if (aptr && anim == ANIM_ATOM_BLAST && aptr->OwnerHouse == HOUSE_NONE) {
            if (Payback && Payback->House && Payback->House->Class) {
                aptr->Set_Owner(Payback->House->Class->House);
            }
        }
    }

    //				if (Payback && Payback->House == PlayerPtr && stricmp(Class->Name(), "GPSSATELLITE") == 0) {
    if (Payback && Class->Type == BULLET_GPS_SATELLITE) {

        bool reveal = false;
        if (Session.Type != GAME_GLYPHX_MULTIPLAYER) {
            if (Payback->House == PlayerPtr) {
                reveal = true;
            }
        } else {
            if (Payback->House->IsHuman) {
                reveal = true;
            }
        }

        if (reveal) {
            if (!Map.Is_Radar_Active()) {
                Map.Radar_Activate(1);
            }
            for (CELL cell = 0; cell < MAP_CELL_TOTAL; cell++) {
                Map.Map_Cell(cell, Payback->House);
            }
            Map.RadarClass::Flag_To_Redraw(true);
        }
        //					Sound_Effect(VOC_SATTACT2);
        Payback->House->IsGPSActive = true;
        Payback->House->IsVisionary = true;
    }
}
