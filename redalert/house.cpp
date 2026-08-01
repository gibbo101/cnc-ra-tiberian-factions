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

/* $Header: /counterstrike/HOUSE.CPP 4     3/13/97 7:11p Steve_tall $ */
/***********************************************************************************************
 ***              C O N F I D E N T I A L  ---  W E S T W O O D  S T U D I O S               ***
 ***********************************************************************************************
 *                                                                                             *
 *                 Project Name : Command & Conquer                                            *
 *                                                                                             *
 *                    File Name : HOUSE.CPP                                                    *
 *                                                                                             *
 *                   Programmer : Joe L. Bostic                                                *
 *                                                                                             *
 *                   Start Date : May 21, 1994                                                 *
 *                                                                                             *
 *                  Last Update : November 4, 1996 [JLB]                                       *
 *                                                                                             *
 *---------------------------------------------------------------------------------------------*
 * Functions:                                                                                  *
 *   HouseClass::AI -- Process house logic.                                                    *
 *   HouseClass::AI_Aircraft -- Determines what aircraft to build next.                        *
 *   HouseClass::AI_Attack -- Handles offensive attack logic.                                  *
 *   HouseClass::AI_Base_Defense -- Handles maintaining a strong base defense.                 *
 *   HouseClass::AI_Building -- Determines what building to build.                             *
 *   HouseClass::AI_Fire_Sale -- Check for and perform a fire sale.                            *
 *   HouseClass::AI_Infantry -- Determines the infantry unit to build.                         *
 *   HouseClass::AI_Money_Check -- Handles money production logic.                             *
 *   HouseClass::AI_Power_Check -- Handle the power situation.                                 *
 *   HouseClass::AI_Unit -- Determines what unit to build next.                                *
 *   HouseClass::Abandon_Production -- Abandons production of item type specified.             *
 *   HouseClass::Active_Add -- Add an object to active duty for this house.                    *
 *   HouseClass::Active_Remove -- Remove this object from active duty for this house.          *
 *   HouseClass::Adjust_Capacity -- Adjusts the house Tiberium storage capacity.               *
 *   HouseClass::Adjust_Drain -- Adjust the power drain value of the house.                    *
 *   HouseClass::Adjust_Power -- Adjust the power value of the house.                          *
 *   HouseClass::Adjust_Threat -- Adjust threat for the region specified.                      *
 *   HouseClass::As_Pointer -- Converts a house number into a house object pointer.            *
 *   HouseClass::Assign_Handicap -- Assigns the specified handicap rating to the house.        *
 *   HouseClass::Attacked -- Lets player know if base is under attack.                         *
 *   HouseClass::Available_Money -- Fetches the total credit worth of the house.               *
 *   HouseClass::Begin_Production -- Starts production of the specified object type.           *
 *   HouseClass::Blowup_All -- blows up everything                                             *
 *   HouseClass::Can_Build -- General purpose build legality checker.                          *
 *   HouseClass::Clobber_All -- removes all objects for this house                             *
 *   HouseClass::Computer_Paranoid -- Cause the computer players to becom paranoid.            *
 *   HouseClass::Debug_Dump -- Dumps the house status data to the mono screen.                 *
 *   HouseClass::Detach -- Removes specified object from house tracking systems.               *
 *   HouseClass::Do_All_To_Hunt -- Send all units to hunt.                                     *
 *   HouseClass::Does_Enemy_Building_Exist -- Checks for enemy building of specified type.     *
 *   HouseClass::Expert_AI -- Handles expert AI processing.                                    *
 *   HouseClass::Factory_Count -- Fetches the number of factories for specified type.          *
 *   HouseClass::Factory_Counter -- Fetches a pointer to the factory counter value.            *
 *   HouseClass::Fetch_Factory -- Finds the factory associated with the object type specified. *
 *   HouseClass::Find_Build_Location -- Finds a suitable building location.                    *
 *   HouseClass::Find_Building -- Finds a building of specified type.                          *
 *   HouseClass::Find_Cell_In_Zone -- Finds a legal placement cell within the zone.            *
 *   HouseClass::Find_Juicy_Target -- Finds a suitable field target.                           *
 *   HouseClass::Fire_Sale -- Cause all buildings to be sold.                                  *
 *   HouseClass::Flag_Attach -- Attach flag to specified cell (or thereabouts).                *
 *   HouseClass::Flag_Attach -- Attaches the house flag the specified unit.                    *
 *   HouseClass::Flag_Remove -- Removes the flag from the specified target.                    *
 *   HouseClass::Flag_To_Die -- Flags the house to blow up soon.                               *
 *   HouseClass::Flag_To_Lose -- Flags the house to die soon.                                  *
 *   HouseClass::Flag_To_Win -- Flags the house to win soon.                                   *
 *   HouseClass::Get_Quantity -- Fetches the total number of aircraft of the specified type.   *
 *   HouseClass::Get_Quantity -- Gets the quantity of the building type specified.             *
 *   HouseClass::Harvested -- Adds Tiberium to the harvest storage.                            *
 *   HouseClass::HouseClass -- Constructor for a house object.                                 *
 *   HouseClass::Init -- init's in preparation for new scenario                                *
 *   HouseClass::Init_Data -- Initializes the multiplayer color data.                          *
 *   HouseClass::Is_Allowed_To_Ally -- Determines if this house is allied to make allies.      *
 *   HouseClass::Is_Ally -- Checks to see if the object is an ally.                            *
 *   HouseClass::Is_Ally -- Determines if the specified house is an ally.                      *
 *   HouseClass::Is_Hack_Prevented -- Is production of the specified type and id prohibted?    *
 *   HouseClass::Is_No_YakMig -- Determines if no more yaks or migs should be allowed.         *
 *   HouseClass::MPlayer_Defeated -- multiplayer; house is defeated                            *
 *   HouseClass::Make_Ally -- Make the specified house an ally.                                *
 *   HouseClass::Make_Enemy -- Make an enemy of the house specified.                           *
 *   HouseClass::Manual_Place -- Inform display system of building placement mode.             *
 *   HouseClass::One_Time -- Handles one time initialization of the house array.               *
 *   HouseClass::Place_Object -- Places the object (building) at location specified.           *
 *   HouseClass::Place_Special_Blast -- Place a special blast effect at location specified.    *
 *   HouseClass::Power_Fraction -- Fetches the current power output rating.                    *
 *   HouseClass::Production_Begun -- Records that production has begun.                        *
 *   HouseClass::Read_INI -- Reads house specific data from INI.                               *
 *   HouseClass::Recalc_Attributes -- Recalcs all houses existence bits.                       *
 *   HouseClass::Recalc_Center -- Recalculates the center point of the base.                   *
 *   HouseClass::Refund_Money -- Refunds money to back to the house.                           *
 *   HouseClass::Remap_Table -- Fetches the remap table for this house object.                 *
 *   HouseClass::Sell_Wall -- Tries to sell the wall at the specified location.                *
 *   HouseClass::Set_Factory -- Assign specified factory to house tracking.                    *
 *   HouseClass::Silo_Redraw_Check -- Flags silos to be redrawn if necessary.                  *
 *   HouseClass::Special_Weapon_AI -- Fires special weapon.                                    *
 *   HouseClass::Spend_Money -- Removes money from the house.                                  *
 *   HouseClass::Suggest_New_Building -- Examines the situation and suggests a building.       *
 *   HouseClass::Suggest_New_Object -- Determine what would the next buildable object be.      *
 *   HouseClass::Suggested_New_Team -- Determine what team should be created.                  *
 *   HouseClass::Super_Weapon_Handler -- Handles the super weapon charge and discharge logic.  *
 *   HouseClass::Suspend_Production -- Temporarily puts production on hold.                    *
 *   HouseClass::Tally_Score -- Fills in the score system for this round                       *
 *   HouseClass::Tiberium_Fraction -- Calculates the tiberium fraction of capacity.            *
 *   HouseClass::Tracking_Add -- Informs house of new inventory item.                          *
 *   HouseClass::Tracking_Remove -- Remove object from house tracking system.                  *
 *   HouseClass::Where_To_Go -- Determines where the object should go and wait.                *
 *   HouseClass::Which_Zone -- Determines what zone a coordinate lies in.                      *
 *   HouseClass::Which_Zone -- Determines which base zone the specified cell lies in.          *
 *   HouseClass::Which_Zone -- Determines which base zone the specified object lies in.        *
 *   HouseClass::Write_INI -- Writes the house data to the INI database.                       *
 *   HouseClass::Zone_Cell -- Finds the cell closest to the center of the zone.                *
 *   HouseClass::delete -- Deallocator function for a house object.                            *
 *   HouseClass::new -- Allocator for a house class.                                           *
 *   HouseClass::operator HousesType -- Conversion to HousesType operator.                     *
 *   HouseClass::~HouseClass -- Default destructor for a house object.                         *
 *   HouseStaticClass::HouseStaticClass -- Default constructor for house static class.         *
 *   HouseClass::AI_Raise_Power -- Try to raise power levels by selling off buildings.         *
 *   HouseClass::AI_Raise_Money -- Raise emergency cash by selling buildings.                  *
 *   HouseClass::Random_Cell_In_Zone -- Find a (technically) legal cell in the zone specified. *
 * - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

#include "function.h"
#include "vortex.h"
#include "rules.h"
#include "utracker.h"

//#include "WolDebug.h"

/*
** New sidebar for GlyphX multiplayer. ST - 8/7/2019 10:10AM
*/
#include "sidebarglyphx.h"

TFixedIHeapClass<HouseClass::BuildChoiceClass> HouseClass::BuildChoice;

template <> int TFixedIHeapClass<HouseClass::BuildChoiceClass>::Save(Pipe&) const
{
    return (true);
}

template <> int TFixedIHeapClass<HouseClass::BuildChoiceClass>::Load(Straw&)
{
    return (0);
}

template <> void TFixedIHeapClass<HouseClass::BuildChoiceClass>::Code_Pointers(void)
{
}

template <> void TFixedIHeapClass<HouseClass::BuildChoiceClass>::Decode_Pointers(void)
{
}

extern bool RedrawOptionsMenu;

/***********************************************************************************************
 * HouseClass::operator HousesType -- Conversion to HousesType operator.                       *
 *                                                                                             *
 *    This operator will automatically convert from a houses class object into the HousesType  *
 *    enumerated value.                                                                        *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the object's HousesType value.                                        *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
HouseClass::operator HousesType(void) const
{
    assert(Houses.ID(this) == ID);

    return (Class->House);
}

/***********************************************************************************************
 * HouseClass::Tiberium_Fraction -- Calculates the tiberium fraction of capacity.              *
 *                                                                                             *
 *    This will calculate the current tiberium (gold) load as a ratio of the maximum storage   *
 *    capacity.                                                                                *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns the current tiberium storage situation as a ratio of load over capacity.   *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/31/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
fixed HouseClass::Tiberium_Fraction(void) const
{
    if (Tiberium == 0) {
        return (0);
    }
    return (fixed(Tiberium, Capacity));
}

/***********************************************************************************************
 * HouseClass::As_Pointer -- Converts a house number into a house object pointer.              *
 *                                                                                             *
 *    Use this routine to convert a house number into the house pointer that it represents.    *
 *    A simple index into the Houses template array is not sufficient, since the array order   *
 *    is arbitrary. An actual scan through the house object is required in order to find the   *
 *    house object desired.                                                                    *
 *                                                                                             *
 * INPUT:   house -- The house type number to look up.                                         *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the house object that the house number represents.       *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
HouseClass* HouseClass::As_Pointer(HousesType house)
{
    if (house != HOUSE_NONE) {
        for (int index = 0; index < Houses.Count(); index++) {
            if (Houses.Ptr(index)->Class->House == house) {
                return (Houses.Ptr(index));
            }
        }
    }
    return (0);
}

/***********************************************************************************************
 * HouseClass::One_Time -- Handles one time initialization of the house array.                 *
 *                                                                                             *
 *    This basically calls the constructor for each of the houses in the game. All other       *
 *    data specific to the house is initialized when the scenario is loaded.                   *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Only call this ONCE at the beginning of the game.                               *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   12/09/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::One_Time(void)
{
    BuildChoice.Set_Heap(STRUCT_COUNT);
}

/***********************************************************************************************
 * HouseClass::Assign_Handicap -- Assigns the specified handicap rating to the house.          *
 *                                                                                             *
 *    The handicap rating will affect combat, movement, and production for the house. It can   *
 *    either make it more or less difficult for the house (controlled by the handicap value).  *
 *                                                                                             *
 * INPUT:   handicap -- The handicap value to assign to this house. The default value for      *
 *                      a house is DIFF_NORMAL.                                                *
 *                                                                                             *
 * OUTPUT:  Returns with the old handicap value.                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *   10/22/1996 JLB : Uses act like value for multiplay only.                                  *
 *=============================================================================================*/
DiffType HouseClass::Assign_Handicap(DiffType handicap)
{
    DiffType old = Difficulty;
    Difficulty = handicap;

    if (Session.Type != GAME_NORMAL) {
        HouseTypeClass const* hptr = &HouseTypeClass::As_Reference(ActLike);
        FirepowerBias = hptr->FirepowerBias * Rule.Diff[handicap].FirepowerBias;
        GroundspeedBias = hptr->GroundspeedBias * Rule.Diff[handicap].GroundspeedBias * Rule.GameSpeedBias;
        AirspeedBias = hptr->AirspeedBias * Rule.Diff[handicap].AirspeedBias * Rule.GameSpeedBias;
        ArmorBias = hptr->ArmorBias * Rule.Diff[handicap].ArmorBias;
        ROFBias = hptr->ROFBias * Rule.Diff[handicap].ROFBias;
        CostBias = hptr->CostBias * Rule.Diff[handicap].CostBias;
        RepairDelay = Rule.Diff[handicap].RepairDelay;
        BuildDelay = Rule.Diff[handicap].BuildDelay;
        BuildSpeedBias = hptr->BuildSpeedBias * Rule.Diff[handicap].BuildSpeedBias * Rule.GameSpeedBias;
    } else {
        FirepowerBias = Rule.Diff[handicap].FirepowerBias;
        GroundspeedBias = Rule.Diff[handicap].GroundspeedBias * Rule.GameSpeedBias;
        AirspeedBias = Rule.Diff[handicap].AirspeedBias * Rule.GameSpeedBias;
        ArmorBias = Rule.Diff[handicap].ArmorBias;
        ROFBias = Rule.Diff[handicap].ROFBias;
        CostBias = Rule.Diff[handicap].CostBias;
        RepairDelay = Rule.Diff[handicap].RepairDelay;
        BuildDelay = Rule.Diff[handicap].BuildDelay;
        BuildSpeedBias = Rule.Diff[handicap].BuildSpeedBias * Rule.GameSpeedBias;
    }

    return (old);
}

/*
**	Lobby AI difficulty -> IQ tier for a computer-controlled house. Difficulty is
**	behavioural only (stat handicaps stay at DIFF_NORMAL's 1.0x biases): the IQ value
**	is the single signal every IQ-gated behaviour keys off. Easy loses the
**	Rule.IQ* >= 4 behaviours (superweapons, aircraft AI, guard-area, content-scan);
**	Hard gets the full Rule.MaxIQ set including MaxIQ-gated smart behaviours.
*/
bool TFLobbyAIDifficultySet = false;

int TF_AI_IQ_From_Difficulty(DiffType diff)
{
    /*
    **	Until the client has actually sent a lobby difficulty this match, keep the
    **	vanilla behaviour (every AI at MaxIQ) so a silent client can't demote the AI.
    */
    if (!TFLobbyAIDifficultySet) {
        return (Rule.MaxIQ);
    }
    switch (diff) {
    case DIFF_EASY:
        return (3);
    case DIFF_HARD:
        return (Rule.MaxIQ);
    default:
        return (4);
    }
}

#ifdef CHEAT_KEYS

void HouseClass::Print_Zone_Stats(int x, int y, ZoneType zone, MonoClass* mono) const
{
    mono->Set_Cursor(x, y);
    mono->Printf(
        "A:%-5d I:%-5d V:%-5d", ZoneInfo[zone].AirDefense, ZoneInfo[zone].InfantryDefense, ZoneInfo[zone].ArmorDefense);
}

/***********************************************************************************************
 * HouseClass::Debug_Dump -- Dumps the house status data to the mono screen.                   *
 *                                                                                             *
 *    This utility function will output the current status of the house class to the mono      *
 *    screen. Through this information bugs may be fixed or detected.                          *
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
void HouseClass::Debug_Dump(MonoClass* mono) const
{
    mono->Set_Cursor(0, 0);
    mono->Print(Text_String(TXT_DEBUG_HOUSE));

    mono->Set_Cursor(1, 1);
    mono->Printf("[%d]%14.14s", Class->House, Name());
    mono->Set_Cursor(20, 1);
    mono->Printf("[%d]%13.13s", ActLike, HouseTypeClass::As_Reference(ActLike).Name());
    mono->Set_Cursor(39, 1);
    mono->Printf("%2d", Control.TechLevel);
    mono->Set_Cursor(45, 1);
    mono->Printf("%2d", Difficulty);
    mono->Set_Cursor(52, 1);
    mono->Printf("%2d", State);
    mono->Set_Cursor(58, 1);
    mono->Printf("%2d", Blockage);
    mono->Set_Cursor(65, 1);
    mono->Printf("%2d", IQ);
    mono->Set_Cursor(72, 1);
    mono->Printf("%5d", (int)RepairTimer);

    mono->Set_Cursor(1, 3);
    mono->Printf("%08X", AScan);
    mono->Set_Cursor(10, 3);
    mono->Printf("%8.8s",
                 (BuildAircraft == AIRCRAFT_NONE) ? " "
                                                  : AircraftTypeClass::As_Reference(BuildAircraft).Graphic_Name());
    mono->Set_Cursor(21, 3);
    mono->Printf("%3d", CurAircraft);
    mono->Set_Cursor(27, 3);
    mono->Printf("%8d", Credits);
    mono->Set_Cursor(37, 3);
    mono->Printf("%5d", Power);
    mono->Set_Cursor(45, 3);
    mono->Printf("%04X", RadarSpied);
    mono->Set_Cursor(52, 3);
    mono->Printf("%5d", PointTotal);
    mono->Set_Cursor(62, 3);
    mono->Printf("%5d", (int)TeamTime);
    mono->Set_Cursor(71, 3);
    mono->Printf("%5d", (int)AlertTime);

    mono->Set_Cursor(1, 5);
    mono->Printf("%08X", BScan);
    mono->Set_Cursor(10, 5);
    mono->Printf("%8.8s",
                 (BuildStructure == STRUCT_NONE) ? " "
                                                 : BuildingTypeClass::As_Reference(BuildStructure).Graphic_Name());
    mono->Set_Cursor(21, 5);
    mono->Printf("%3d", CurBuildings);
    mono->Set_Cursor(27, 5);
    mono->Printf("%8d", Tiberium);
    mono->Set_Cursor(37, 5);
    mono->Printf("%5d", Drain);
    mono->Set_Cursor(44, 5);
    mono->Printf("%16.16s", QuarryName[PreferredTarget]);
    mono->Set_Cursor(62, 5);
    mono->Printf("%5d", (int)TriggerTime);
    mono->Set_Cursor(71, 5);
    mono->Printf("%5d", (int)BorrowedTime);

    mono->Set_Cursor(1, 7);
    mono->Printf("%08X", UScan);
    mono->Set_Cursor(10, 7);
    mono->Printf("%8.8s", (BuildUnit == UNIT_NONE) ? " " : UnitTypeClass::As_Reference(BuildUnit).Graphic_Name());
    mono->Set_Cursor(21, 7);
    mono->Printf("%3d", CurUnits);
    mono->Set_Cursor(27, 7);
    mono->Printf("%8d", Control.InitialCredits);
    mono->Set_Cursor(38, 7);
    mono->Printf("%5d", UnitsLost);
    mono->Set_Cursor(44, 7);
    mono->Printf("%08X", Allies);
    mono->Set_Cursor(71, 7);
    mono->Printf("%5d", (int)Attack);

    mono->Set_Cursor(1, 9);
    mono->Printf("%08X", IScan);
    mono->Set_Cursor(10, 9);
    mono->Printf("%8.8s",
                 (BuildInfantry == INFANTRY_NONE) ? " "
                                                  : InfantryTypeClass::As_Reference(BuildInfantry).Graphic_Name());
    mono->Set_Cursor(21, 9);
    mono->Printf("%3d", CurInfantry);
    mono->Set_Cursor(27, 9);
    mono->Printf("%8d", Capacity);
    mono->Set_Cursor(38, 9);
    mono->Printf("%5d", BuildingsLost);
    mono->Set_Cursor(45, 9);
    mono->Printf("%4d", Radius / CELL_LEPTON_W);
    mono->Set_Cursor(71, 9);
    mono->Printf("%5d", (int)AITimer);

    mono->Set_Cursor(1, 11);
    mono->Printf("%08X", VScan);
    mono->Set_Cursor(10, 11);
    mono->Printf("%8.8s",
                 (BuildVessel == VESSEL_NONE) ? " " : VesselTypeClass::As_Reference(BuildVessel).Graphic_Name());
    mono->Set_Cursor(21, 11);
    mono->Printf("%3d", CurVessels);
    mono->Set_Cursor(54, 11);
    mono->Printf("%04X", Coord_Cell(Center));
    mono->Set_Cursor(71, 11);
    mono->Printf("%5d", (int)DamageTime);

    for (int index = 0; index < ARRAY_SIZE(Scen.GlobalFlags); index++) {
        mono->Set_Cursor(1 + index, 15);
        if (Scen.GlobalFlags[index] != 0) {
            mono->Print("1");
        } else {
            mono->Print("0");
        }
        if (index >= 24)
            break;
    }
    if (Enemy != HOUSE_NONE) {
        char const* name = "";
        name = HouseClass::As_Pointer(Enemy)->Name();
        mono->Set_Cursor(53, 15);
        mono->Printf("[%d]%21.21s", Enemy, HouseTypeClass::As_Reference(Enemy).Name());
    }

    Print_Zone_Stats(27, 11, ZONE_NORTH, mono);
    Print_Zone_Stats(27, 13, ZONE_CORE, mono);
    Print_Zone_Stats(27, 15, ZONE_SOUTH, mono);
    Print_Zone_Stats(1, 13, ZONE_WEST, mono);
    Print_Zone_Stats(53, 13, ZONE_EAST, mono);

    mono->Fill_Attrib(1, 17, 12, 1, IsActive ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(1, 18, 12, 1, IsHuman ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(1, 19, 12, 1, IsPlayerControl ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(1, 20, 12, 1, IsAlerted ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(1, 21, 12, 1, IsDiscovered ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(1, 22, 12, 1, IsMaxedOut ? MonoClass::INVERSE : MonoClass::NORMAL);

    mono->Fill_Attrib(14, 17, 12, 1, IsDefeated ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(14, 18, 12, 1, IsToDie ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(14, 19, 12, 1, IsToWin ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(14, 20, 12, 1, IsToLose ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(14, 21, 12, 1, IsCivEvacuated ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(14, 22, 12, 1, IsRecalcNeeded ? MonoClass::INVERSE : MonoClass::NORMAL);

    mono->Fill_Attrib(27, 17, 12, 1, IsVisionary ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(27, 18, 12, 1, IsTiberiumShort ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(27, 19, 12, 1, IsSpied ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(27, 20, 12, 1, IsThieved ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(27, 21, 12, 1, IsGPSActive ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(27, 22, 12, 1, IsStarted ? MonoClass::INVERSE : MonoClass::NORMAL);

    mono->Fill_Attrib(40, 17, 12, 1, IsResigner ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(40, 18, 12, 1, IsGiverUpper ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(40, 19, 12, 1, IsBuiltSomething ? MonoClass::INVERSE : MonoClass::NORMAL);
    mono->Fill_Attrib(40, 20, 12, 1, IsBaseBuilding ? MonoClass::INVERSE : MonoClass::NORMAL);
}
#endif

/***********************************************************************************************
 * HouseClass::new -- Allocator for a house class.                                             *
 *                                                                                             *
 *    This is the allocator for a house class. Since there can be only                         *
 *    one of each type of house, this is allocator has restricted                              *
 *    functionality. Any attempt to allocate a house structure for a                           *
 *    house that already exists, just returns a pointer to the previously                      *
 *    allocated house.                                                                         *
 *                                                                                             *
 * INPUT:   house -- The house to allocate a class object for.                                 *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the allocated class object.                              *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/22/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void* HouseClass::operator new(size_t) noexcept
{
    void* ptr = Houses.Allocate();
    if (ptr) {
        ((HouseClass*)ptr)->IsActive = true;
    }
    return (ptr);
}

/***********************************************************************************************
 * HouseClass::delete -- Deallocator function for a house object.                              *
 *                                                                                             *
 *    This function marks the house object as "deallocated". Such a                            *
 *    house object is available for reallocation later.                                        *
 *                                                                                             *
 * INPUT:   ptr   -- Pointer to the house object to deallocate.                                *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/22/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::operator delete(void* ptr)
{
    if (ptr) {
        ((HouseClass*)ptr)->IsActive = false;
    }
    Houses.Free((HouseClass*)ptr);
}

/***********************************************************************************************
 * HouseClass::HouseClass -- Constructor for a house object.                                   *
 *                                                                                             *
 *    This function is the constructor and it marks the house object                           *
 *    as being allocated.                                                                      *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/22/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
#define VOX_NOT_READY VOX_NONE
HouseClass::HouseClass(HousesType house)
    : RTTI(RTTI_HOUSE)
    , ID(Houses.ID(this))
    , Class(HouseTypes.Ptr(house))
    , Difficulty(Scen.CDifficulty)
    , FirepowerBias(1)
    , GroundspeedBias(1)
    , AirspeedBias(1)
    , ArmorBias(1)
    , ROFBias(1)
    , CostBias(1)
    , BuildSpeedBias(1)
    , RepairDelay(0)
    , BuildDelay(0)
    // Tiberian Factions: HOUSE_GOOD (GDI) acts like HOUSE_GREECE (canonical
    // Allied house — 'G' campaign prefix); HOUSE_BAD (Nod) acts like
    // HOUSE_USSR (canonical Soviet house). Without this, ActLike-gated code
    // paths (Soviet parabomb spawns, Allied/Soviet infantry voice prefixes,
    // mapsel.cpp side selection, saveload.cpp side persistence) never fire
    // for the new factions, leaving them without their inherited roster.
    , ActLike(Class->House == HOUSE_GOOD ? HOUSE_GREECE
            : Class->House == HOUSE_BAD  ? HOUSE_USSR
            : Class->House)
    , IsHuman(false)
    , WasHuman(false)
    , IsPlayerControl(false)
    , IsStarted(false)
    , IsAlerted(false)
    , IsBaseBuilding(false)
    , IsDiscovered(false)
    , IsMaxedOut(false)
    , IsDefeated(false)
    , IsToDie(false)
    , IsToLose(false)
    , IsToWin(false)
    , IsCivEvacuated(false)
    , IsRecalcNeeded(true)
    , IsVisionary(false)
    , IsTiberiumShort(false)
    , IsSpied(false)
    , IsThieved(false)
    , IsGPSActive(false)
    , IsBuiltSomething(false)
    , IsResigner(false)
    , IsGiverUpper(false)
    , IsParanoid(false)
    , IsToLook(true)
    , IsQueuedMovementToggle(false)
    , DidRepair(false)
    , IQ(Control.IQ)
    , State(STATE_BUILDUP)
    , JustBuiltStructure(STRUCT_NONE)
    , JustBuiltInfantry(INFANTRY_NONE)
    , JustBuiltUnit(UNIT_NONE)
    , JustBuiltAircraft(AIRCRAFT_NONE)
    , JustBuiltVessel(VESSEL_NONE)
    , Blockage(0)
    , RepairTimer(0)
    , AlertTime(0)
    , BorrowedTime(0)
    , BScan(0)
    , ActiveBScan(0)
    , OldBScan(0)
    , UScan(0)
    , ActiveUScan(0)
    , OldUScan(0)
    , IScan(0)
    , ActiveIScan(0)
    , OldIScan(0)
    , AScan(0)
    , ActiveAScan(0)
    , OldAScan(0)
    , VScan(0)
    , ActiveVScan(0)
    , OldVScan(0)
    , CreditsSpent(0)
    , HarvestedCredits(0)
    , StolenBuildingsCredits(0)
    , CurUnits(0)
    , CurBuildings(0)
    , CurInfantry(0)
    , CurVessels(0)
    , CurAircraft(0)
    , Tiberium(0)
    , Credits(0)
    , Capacity(0)
    , AircraftTotals()
    , InfantryTotals()
    , UnitTotals()
    , BuildingTotals()
    , VesselTotals()
    , DestroyedAircraft()
    , DestroyedInfantry()
    , DestroyedUnits()
    , DestroyedBuildings()
    , DestroyedVessels()
    , CapturedBuildings()
    , TotalCrates()
    , AircraftFactories(0)
    , InfantryFactories(0)
    , UnitFactories(0)
    , BuildingFactories(0)
    , VesselFactories(0)
    , Power(0)
    , Drain(0)
    , AircraftFactory(-1)
    , InfantryFactory(-1)
    , UnitFactory(-1)
    , BuildingFactory(-1)
    , VesselFactory(-1)
    , Radar(RADAR_NONE)
    , FlagLocation(TARGET_NONE)
    , FlagHome(0)
    , UnitsLost(0)
    , BuildingsLost(0)
    , WhoLastHurtMe(house)
    , StartLocationOverride(-1)
    , Center(0)
    , Radius(0)
    , LATime(0)
    , LAType(RTTI_NONE)
    , LAZone(ZONE_NONE)
    , LAEnemy(HOUSE_NONE)
    , ToCapture(TARGET_NONE)
    , RadarSpied(0)
    , PointTotal(0)
    , PreferredTarget(QUARRY_ANYTHING)
    , ScreenShakeTime(0)
    , Attack(0)
    , Enemy(HOUSE_NONE)
    , AITimer(0)
    , UnitToTeleport(0)
    , BuildStructure(STRUCT_NONE)
    , BuildUnit(UNIT_NONE)
    , BuildInfantry(INFANTRY_NONE)
    , BuildAircraft(AIRCRAFT_NONE)
    , BuildVessel(VESSEL_NONE)
    , NukeDest(0)
    , Allies(0)
    , DamageTime(TICKS_PER_MINUTE * Rule.DamageDelay)
    , TeamTime(TICKS_PER_MINUTE * Rule.TeamDelay)
    , TriggerTime(0)
    , SpeakAttackDelay(1)
    , SpeakPowerDelay(1)
    , SpeakMoneyDelay(1)
    , SpeakMaxedDelay(1)
    , RemapColor(Class->RemapColor)
    , DebugUnlockBuildables(false)
{
    /*
    **	Explicit in-place construction of the super weapons is
    **	required here because the default constructor for super
    **	weapons must serve as a no-initialization constructor (save/load reasons).
    */
    new (&SuperWeapon[SPC_NUCLEAR_BOMB]) SuperClass(TICKS_PER_MINUTE * Rule.NukeTime,
                                                    true,
                                                    VOX_ABOMB_PREPPING,
                                                    VOX_ABOMB_READY,
                                                    VOX_NOT_READY,
                                                    VOX_INSUFFICIENT_POWER);
    new (&SuperWeapon[SPC_SONAR_PULSE]) SuperClass(
        TICKS_PER_MINUTE * Rule.SonarTime, false, VOX_NONE, VOX_SONAR_AVAILABLE, VOX_NOT_READY, VOX_NOT_READY);
    new (&SuperWeapon[SPC_CHRONOSPHERE]) SuperClass(TICKS_PER_MINUTE * Rule.ChronoTime,
                                                    true,
                                                    VOX_CHRONO_CHARGING,
                                                    VOX_CHRONO_READY,
                                                    VOX_NOT_READY,
                                                    VOX_INSUFFICIENT_POWER);
    new (&SuperWeapon[SPC_PARA_BOMB])
        SuperClass(TICKS_PER_MINUTE * Rule.ParaBombTime, false, VOX_NONE, VOX_NONE, VOX_NOT_READY, VOX_NOT_READY);
    new (&SuperWeapon[SPC_PARA_INFANTRY])
        SuperClass(TICKS_PER_MINUTE * Rule.ParaInfantryTime, false, VOX_NONE, VOX_NONE, VOX_NOT_READY, VOX_NOT_READY);
    new (&SuperWeapon[SPC_SPY_MISSION])
        SuperClass(TICKS_PER_MINUTE * Rule.SpyTime, false, VOX_NONE, VOX_SPY_PLANE, VOX_NOT_READY, VOX_NOT_READY);
    new (&SuperWeapon[SPC_IRON_CURTAIN]) SuperClass(TICKS_PER_MINUTE * Rule.IronCurtainTime,
                                                    true,
                                                    VOX_IRON_CHARGING,
                                                    VOX_IRON_READY,
                                                    VOX_NOT_READY,
                                                    VOX_INSUFFICIENT_POWER);
    new (&SuperWeapon[SPC_GPS])
        SuperClass(TICKS_PER_MINUTE * Rule.GPSTime, true, VOX_NONE, VOX_NONE, VOX_NOT_READY, VOX_INSUFFICIENT_POWER);

    // Tiberian Factions mod — GDI Ion Cannon. TD-authentic 10-minute
    // recharge per tiberiandawn/defines.h ION_CANNON_GONE_TIME
    // (10 * TICKS_PER_MINUTE). Powered = true so a power-starved base
    // suspends the timer (matches RA's nuke / chrono behaviour).
    new (&SuperWeapon[SPC_TD_ION_CANNON]) SuperClass(TICKS_PER_MINUTE * 10,
                                                     true,
                                                     VOX_TD_ION_CHARGING,
                                                     VOX_TD_ION_READY,
                                                     VOX_NOT_READY,
                                                     VOX_INSUFFICIENT_POWER);

    // Tiberian Factions mod — Nod Nuclear Strike. TD-authentic 14-minute
    // recharge per tiberiandawn/defines.h NUKE_GONE_TIME (14 *
    // TICKS_PER_MINUTE). TD has no "charging" voice for the nuke so the
    // charging slot is VOX_NONE; VOX_TD_NUKE_AVAILABLE plays on ready.
    new (&SuperWeapon[SPC_TD_NUKE]) SuperClass(TICKS_PER_MINUTE * 14,
                                               true,
                                               VOX_NONE,
                                               VOX_TD_NUKE_AVAILABLE,
                                               VOX_NOT_READY,
                                               VOX_INSUFFICIENT_POWER);

    // Tiberian Factions mod — Nod paratroops. Same cadence and voice
    // handling as the RA paratroop drop it splits from.
    new (&SuperWeapon[SPC_TD_PARA_INFANTRY])
        SuperClass(TICKS_PER_MINUTE * Rule.ParaInfantryTime, false, VOX_NONE, VOX_NONE, VOX_NOT_READY, VOX_NOT_READY);

    // Tiberian Factions mod — Nod recon flight, split from the Soviet spy
    // plane so each era's airstrip carries its own single-badged special.
    new (&SuperWeapon[SPC_TD_SPY_MISSION])
        SuperClass(TICKS_PER_MINUTE * Rule.SpyTime, false, VOX_NONE, VOX_SPY_PLANE, VOX_NOT_READY, VOX_NOT_READY);

    memset(UnitsKilled, '\0', sizeof(UnitsKilled));
    memset(BuildingsKilled, '\0', sizeof(BuildingsKilled));
    memset(BQuantity, '\0', sizeof(BQuantity));
    memset(ActiveBQuantity, '\0', sizeof(ActiveBQuantity));
    memset(UQuantity, '\0', sizeof(UQuantity));
    memset(IQuantity, '\0', sizeof(IQuantity));
    memset(AQuantity, '\0', sizeof(AQuantity));
    memset(VQuantity, '\0', sizeof(VQuantity));
    strcpy(IniName, Text_String(TXT_COMPUTER)); // Default computer name.
    HouseTriggers[house].Clear();
    memset((void*)&Regions[0], 0x00, sizeof(Regions));
    Make_Ally(house);
    Assign_Handicap(Scen.CDifficulty);

    /*
    **	Set the time of the first AI attack.
    */
    Attack = Rule.AttackDelay * Random_Pick(TICKS_PER_MINUTE / 2, TICKS_PER_MINUTE * 2);

    Init_Unit_Trackers();
}

/***********************************************************************************************
 * HouseClass::~HouseClass -- House class destructor                                           *
 *                                                                                             *
 *                                                                                             *
 *                                                                                             *
 * INPUT:    Nothing                                                                           *
 *                                                                                             *
 * OUTPUT:   Nothing                                                                           *
 *                                                                                             *
 * WARNINGS: None                                                                              *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *    8/6/96 4:48PM ST : Created                                                               *
 *=============================================================================================*/
HouseClass::~HouseClass(void)
{
    Class = 0;
}

/***********************************************************************************************
 * HouseStaticClass::HouseStaticClass -- Default constructor for house static class.           *
 *                                                                                             *
 *    This is the default constructor that initializes all the values to their default         *
 *    settings.                                                                                *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/31/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
HouseStaticClass::HouseStaticClass(void)
    : IQ(0)
    , TechLevel(1)
    , Allies(0)
    , MaxUnit(Rule.UnitMax / 6)
    , MaxBuilding(Rule.BuildingMax / 6)
    , MaxInfantry(Rule.InfantryMax / 6)
    , MaxVessel(Rule.VesselMax / 6)
    , MaxAircraft(Rule.UnitMax / 6)
    , InitialCredits(0)
    , Edge(SOURCE_NORTH)
{
}

/***********************************************************************************************
 * HouseClass::Can_Build -- General purpose build legality checker.                            *
 *                                                                                             *
 *    This routine is called when it needs to be determined if the specified object type can   *
 *    be built by this house. Production and sidebar maintenance use this routine heavily.     *
 *                                                                                             *
 * INPUT:   type  -- Pointer to the type of object that legality is to be checked for.         *
 *                                                                                             *
 *          house -- This is the house to check for legality against. Note that this might     *
 *                   not be 'this' house since the check could be from a captured factory.     *
 *                   Captured factories build what the original owner of them could build.     *
 *                                                                                             *
 * OUTPUT:  Can the specified object be built?                                                 *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/04/1995 JLB : Created.                                                                 *
 *   08/12/1995 JLB : Updated for GDI building sandbag walls in #9.                            *
 *   10/23/1996 JLB : Hack to allow Tanya to both sides in multiplay.                          *
 *   11/04/1996 JLB : Computer uses prerequisite record.                                       *
 *=============================================================================================*/
bool HouseClass::Can_Build(ObjectTypeClass const* type, HousesType house) const
{
    assert(Houses.ID(this) == ID);
    assert(type != NULL);

    // Diagnostic hook 2026-05-19: log Can_Build calls for mod-defined building
    // entries so we can see why a freshly-added TDxxxx might not appear in the
    // sidebar. Filter to TD-prefixed IniNames and rate-limit. Keep in place
    // until v1.0 per [[feedback-keep-diagnostics-until-v1]]. Stub the body
    // under `if (0)` to disable; do not delete.
    //
    // Path resolution: %USERPROFILE%/Documents/CnCRemastered matches the
    // game's own save folder convention and resolves correctly on both real
    // Windows (whatever the user's profile is) and Wine/Proton (where
    // USERPROFILE points to drive_c/users/steamuser). Falls back to CWD if
    // the env var is unset.
    // Capture: TD-prefixed buildings (always) + E-prefix infantry (E1..E9,
    // for the 2026-05-20 GDI roster bring-up where E3 isn't appearing in the
    // sidebar despite Owner=allies,soviet,GoodGuy,BadGuy + Prerequisite=tent
    // + TDPYLE built). Logging RTTI distinguishes the two streams.
    bool log_td = (type->IniName[0] == 'T' && type->IniName[1] == 'D');
    bool log_einf = (type->What_Am_I() == RTTI_INFANTRYTYPE
                     && type->IniName[0] == 'E'
                     && type->IniName[1] >= '0' && type->IniName[1] <= '9');
    // v4.0 navy/air debug: also log ALL vessels + aircraft (so we see why GDI/Nod get the RA
    // rosters from owner-opened SYRD/SPEN/AFLD but not the TD ships/A-10).
    bool log_navair = (type->What_Am_I() == RTTI_VESSELTYPE || type->What_Am_I() == RTTI_AIRCRAFTTYPE);
    if (log_td || log_einf || log_navair) {
        static FILE* s_can_build_log = NULL;
        static int s_log_count = 0;
        if (s_log_count < 400) {
            if (s_can_build_log == NULL) {
                char path[512];
                const char* profile = getenv("USERPROFILE");
                if (profile != NULL && profile[0] != '\0') {
                    snprintf(path, sizeof(path),
                             "%s/Documents/CnCRemastered/MOD_DEBUG_CANBUILD.txt",
                             profile);
                } else {
                    strcpy(path, "MOD_DEBUG_CANBUILD.txt");
                }
                s_can_build_log = NULL; // TF DIAG OFF for release (was fopen; restore to re-enable)
            }
            if (s_can_build_log != NULL) {
                int level = Control.TechLevel;
                int const* pre = ((TechnoTypeClass const*)type)->Prerequisite;
                int own = type->Get_Ownable();
                int level_ok = ((TechnoTypeClass const*)type)->Level <= (unsigned)level;
                int pre_ok = 1;
                for (int i = 0; i < PREREQUISITE_MAX; i++) {
                    int t = pre[i];
                    if (t < 0)
                        break;
                    if (!Has_Building_Active(t)) {
                        pre_ok = 0;
                        break;
                    }
                }
                int own_ok = ((1L << house) & own) != 0;
                fprintf(s_can_build_log,
                        "Can_Build rtti=%d name=%s house=%d level=%d type.Level=%d "
                        "pre=[%d,%d,%d,%d] own=0x%X level_ok=%d pre_ok=%d "
                        "own_ok=%d IsHuman=%d\n",
                        (int)type->What_Am_I(), type->IniName, (int)house, level,
                        ((TechnoTypeClass const*)type)->Level,
                        pre[0], pre[1], pre[2], pre[3],
                        own, level_ok, pre_ok, own_ok, (int)IsHuman);
                fflush(s_can_build_log);
                s_log_count++;
            }
        }
    }

    /*
    **	An object with a prohibited tech level availability will never be allowed, regardless
    **	of who requests it.
    */
    if (((TechnoTypeClass const*)type)->Level == -1)
        return (false);

#ifdef FIXIT_CSII //	checked - ajw 9/28/98
    /*
    ** If this is a CounterStrike II-only unit, and we're playing a multiplayer
    ** game in 'downshifted' mode against CounterStrike or Red Alert, then
    ** don't allow building this unit.
    */
    if (!NewUnitsEnabled) {
        switch (type->What_Am_I()) {
        case RTTI_INFANTRYTYPE:
            if (((InfantryTypeClass*)type)->ID >= INFANTRY_RA_COUNT)
                return (false);
            break;
        case RTTI_UNITTYPE:
            if (((UnitTypeClass*)type)->ID >= UNIT_RA_COUNT)
                return (false);
            break;
        case RTTI_VESSELTYPE:
            if (((VesselTypeClass*)type)->ID >= VESSEL_RA_COUNT)
                return (false);
            break;
        default:
            break;
        }
    }
#endif

    /*
    **	The computer can always build everything.
    */
    if (!IsHuman && Session.Type == GAME_NORMAL)
        return (true);

    /*
    **	Special hack to get certain objects to exist for both sides in the game.
    */
    int own = type->Get_Ownable();

    /*
    **	Check to see if this owner can build the object type specified.
    */
    if (((1L << house) & own) == 0) {
        return (false);
    }

    /*
    **	W2 b3: skirmish/multiplayer builds the four faction MCVs; the vanilla
    **	pair (UNIT_MCV / UNIT_TDMCV) is stock-campaign-only. Gate both
    **	directions on session type so a campaign sidebar never shows a faction
    **	MCV and a skirmish sidebar never shows a vanilla one.
    */
    if (type->What_Am_I() == RTTI_UNITTYPE && ((UnitTypeClass const*)type)->Is_MCV()) {
        UnitType ut = ((UnitTypeClass const*)type)->Type;
        bool vanilla = (ut == UNIT_MCV || ut == UNIT_TDMCV);
        if (vanilla == (Session.Type != GAME_NORMAL)) {
            return (false);
        }
    }

    /*
    **	W2 (c): the same quartet-swap for the war factory — skirmish builds the
    **	faction pair (AWEAP/SWEAP), campaign the shared vanilla WEAP.
    */
    if (type->What_Am_I() == RTTI_BUILDINGTYPE) {
        StructType st = (StructType)((BuildingTypeClass const*)type)->Type;
        bool vanilla_b = (st == STRUCT_WEAP || st == STRUCT_HELIPAD || st == STRUCT_TDHPAD);
        bool faction_b = (st == STRUCT_AWEAP || st == STRUCT_SWEAP || st == STRUCT_AHPAD || st == STRUCT_SHPAD
                          || st == STRUCT_TDGHPAD || st == STRUCT_TDNHPAD);
        if ((vanilla_b && Session.Type != GAME_NORMAL) || (faction_b && Session.Type == GAME_NORMAL)) {
            return (false);
        }
    }

    /*
    **	A house builds from its OWN faction's construction yard. Another lineage's yard does
    **	not unlock this faction's tree -- no prerequisite, no build.
    **
    **	This cannot be expressed in rules.ini. The TD chain roots at TDNUKE, which names no
    **	prerequisite at all, so every TD structure was reachable with nothing but a power
    **	plant; and TDNUKE / TDPROC / TDHQ / TDFIX are shared by GDI and Nod, so an AND-only
    **	token list can never say "GDI yard OR Nod yard". Hence the gate lives here.
    **
    **	It shows in Unholy Alliance, where a house holds a yard of every faction from the
    **	start: a Nod house must wait for its own yard before the Hand of Nod is legal instead
    **	of inheriting the tree from whichever yard deployed first.
    **
    **	Skirmish and multiplayer only -- the stock campaigns own the pre-split shared yards
    **	(STRUCT_CONST, STRUCT_TDFACT) and have to keep teching from them.
    */
    if (type->What_Am_I() == RTTI_BUILDINGTYPE && Session.Type != GAME_NORMAL) {
        BuildingTypeClass const* btype = (BuildingTypeClass const*)type;
        /*
        **	Yards themselves arrive by MCV deploy rather than construction, so exempt them:
        **	gating a yard on owning a yard would be circular.
        */
        if (!btype->Is_Construction_Yard()) {
            /*
            **	A yard opens the tree of the faction it belongs to. So the test is not "do I
            **	own MY yard" but "do I own a yard belonging to a faction that can build this"
            **	-- which lets the shared structures through on either yard while keeping the
            **	faction-exclusive ones shut. [TDNUKE] is Owner=GoodGuy,BadGuy, so a GDI yard
            **	provides the power plant; [TDHAND] is Owner=BadGuy, so it does not provide
            **	the Hand of Nod.
            */
            int const factions = HOUSEF_GDI | HOUSEF_NOD | HOUSEF_ALLIES | HOUSEF_SOVIET;
            int ownable = type->Get_Ownable();
            if ((ownable & factions) != 0) {
                int yards = 0;
                if (Has_Building_Active(STRUCT_TDGFACT)) {
                    yards |= HOUSEF_GDI;
                }
                if (Has_Building_Active(STRUCT_TDNFACT)) {
                    yards |= HOUSEF_NOD;
                }
                if (Has_Building_Active(STRUCT_AFACT)) {
                    yards |= HOUSEF_ALLIES;
                }
                if (Has_Building_Active(STRUCT_SFACT)) {
                    yards |= HOUSEF_SOVIET;
                }
                if ((ownable & yards) == 0) {
                    return (false);
                }
            }
        }
    }

    /*
    **	Prereq satisfaction: every populated slot in Prerequisite[] must
    **	correspond to a building Type the house currently owns (active +
    **	unlimbo'd). ActiveBQuantity is the heap-sized counter that handles
    **	mod IniNames whose Type exceeds the 32-bit ActiveBScan range.
    */
    int const* pre = ((TechnoTypeClass const*)type)->Prerequisite;

    int level = Control.TechLevel;
    bool skip_prereqs = false;
#ifdef CHEAT_KEYS
    if (Debug_Cheat) {
        level = 98;
        skip_prereqs = true;
    }
#endif
    // ST - 8/23/2019 4:53PM
    if (DebugUnlockBuildables) {
        level = 98;
        skip_prereqs = true;
    }

    if (((TechnoTypeClass const*)type)->Level > (unsigned)level) {
        return (false);
    }
    if (skip_prereqs) {
        return (true);
    }

    for (int i = 0; i < PREREQUISITE_MAX; i++) {
        int t = pre[i];
        if (t < 0)
            break;

        if (Has_Building_Active(t))
            continue;

        /*
        **	Advanced power also serves as a prerequisite for normal power.
        **	These vanilla equivalences are due to be replaced with a
        **	BehavesLike= rules.ini field in D2; until then, special-case here.
        **
        **	DELIBERATE VANILLA DEVIATION (Luke, 2026-07-19): the multiplayer
        **	either-tech-center-counts rule (atek<->stek) is REMOVED. Tech
        **	centers are faction identity — Soviet Mammoths need the Soviet
        **	tech center, Chronosphere tech the Allied one. Capture still
        **	works: a captured tech center satisfies its own faction's token.
        */
        if (t == STRUCT_POWER && Has_Building_Active(STRUCT_ADVANCED_POWER))
            continue;
        /*
        **	The vanilla 'fact' token ([POWR]'s Prerequisite=fact). Post-split a house owns
        **	its faction's yard, never STRUCT_CONST, so without a remap the whole tech tree
        **	dies at the power plant.
        **
        **	Only the house's OWN faction yard counts. Another lineage's yard does not unlock
        **	this faction's tree -- no prerequisite, no build. It matters in Unholy Alliance,
        **	where a house holds a yard of every faction from the start: a Nod house must wait
        **	for its Nod yard before the Hand of Nod becomes legal, rather than inheriting the
        **	tree from whichever yard happened to deploy first.
        */
        if (t == STRUCT_CONST
            && (Has_Building_Active(STRUCT_AFACT) || Has_Building_Active(STRUCT_SFACT)
                || Has_Building_Active(STRUCT_TDFACT) || Has_Building_Active(STRUCT_TDGFACT)
                || Has_Building_Active(STRUCT_TDNFACT)))
            continue;
        /*
        **  Tiberian Factions: TD-themed barracks satisfy vanilla barracks
        **  prereqs so HOUSE_GOOD (TDPYLE) and HOUSE_BAD (TDHAND) can build
        **  the inherited Allied / Soviet infantry rosters. Lookup is by
        **  IniName via the heap-aware As_Pointer; Types are cached after
        **  first resolution since they're stable for the rest of the run.
        **  Pre-D2 stopgap — proper fix is a BehavesLike= rules.ini field.
        */
        {
            static int tdpyle_type = -2;  // -2 = unresolved, -1 = absent
            static int tdhand_type = -2;
            static int tdweap_type = -2;
            static int tdafld_type = -2;
            static int tdhpad_type = -2;
            static int tdhq_type   = -2;
            static int tdproc_type = -2;
            static int tdeye_type  = -2;
            static int tdtmpl_type = -2;
            static int tdfix_type  = -2;
            static int tdnuke_type = -2;
            static int tdnuk2_type = -2;
            static int tdgyard_type = -2;
            static int tdnpen_type = -2;
            static int tdgafld_type = -2;
            if (tdgyard_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDGYARD");
                tdgyard_type = p ? p->Type : -1;
            }
            if (tdnpen_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDNPEN");
                tdnpen_type = p ? p->Type : -1;
            }
            if (tdgafld_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDGAFLD");
                tdgafld_type = p ? p->Type : -1;
            }
            if (tdpyle_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDPYLE");
                tdpyle_type = p ? p->Type : -1;
            }
            if (tdhand_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDHAND");
                tdhand_type = p ? p->Type : -1;
            }
            if (tdweap_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDWEAP");
                tdweap_type = p ? p->Type : -1;
            }
            if (tdafld_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDAFLD");
                tdafld_type = p ? p->Type : -1;
            }
            if (tdhpad_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDHPAD");
                tdhpad_type = p ? p->Type : -1;
            }
            if (tdhq_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDHQ");
                tdhq_type = p ? p->Type : -1;
            }
            if (tdproc_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDPROC");
                tdproc_type = p ? p->Type : -1;
            }
            if (tdeye_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDEYE");
                tdeye_type = p ? p->Type : -1;
            }
            if (tdtmpl_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDTMPL");
                tdtmpl_type = p ? p->Type : -1;
            }
            if (tdfix_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDFIX");
                tdfix_type = p ? p->Type : -1;
            }
            if (tdnuke_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDNUKE");
                tdnuke_type = p ? p->Type : -1;
            }
            if (tdnuk2_type == -2) {
                BuildingTypeClass const* p = BuildingTypeClass::As_Pointer("TDNUK2");
                tdnuk2_type = p ? p->Type : -1;
            }
            // PRODUCTION tokens are faction identity (Luke, 2026-07-20): each
            // equivalence below is scoped to entities the substitute's faction
            // can own, so a GDI barracks never satisfies 'tent' for an Allied
            // pillbox, an Allied war factory never satisfies 'weap' for a
            // Tesla coil, and so on. INFRASTRUCTURE tokens (powr/proc/fix/
            // dome) stay cross-era both ways — see the block further down.
            if (t == STRUCT_TENT && (own & HOUSEF_GDI) && tdpyle_type >= 0 && Has_Building_Active(tdpyle_type))
                continue;
            if (t == STRUCT_BARRACKS && (own & HOUSEF_NOD) && tdhand_type >= 0 && Has_Building_Active(tdhand_type))
                continue;
            // TDPYLE ↔ TDHAND mutual equivalence — for SHARED entities only
            // (Luke, 2026-07-20): an entity both TD factions can build (the
            // legacy TDHPAD, Prerequisite=TDPYLE) accepts either barracks; a
            // single-faction entity requires its own (GDI guard tower needs
            // TDPYLE, the Nod turret/SAM/flame bunker TDHAND, the faction
            // helipads their own — the GDI-barracks-unlocks-Nod-helipad leak).
            if (tdpyle_type >= 0 && tdhand_type >= 0 && (own & HOUSEF_GDI) && (own & HOUSEF_NOD)) {
                if (t == tdpyle_type && Has_Building_Active(tdhand_type))
                    continue;
                if (t == tdhand_type && Has_Building_Active(tdpyle_type))
                    continue;
            }
            // STRUCT_WEAP (RA War Factory) — satisfied by TDWEAP (GDI) or
            // TDAFLD (Nod airstrip stopgap). TDAFLD uses Logic=WEAP donor for
            // vehicle-factory behaviour, but its heap Type is past STRUCT_COUNT
            // so it doesn't match STRUCT_WEAP automatically.
            if (t == STRUCT_WEAP) {
                if ((own & HOUSEF_GDI) && tdweap_type >= 0 && Has_Building_Active(tdweap_type))
                    continue;
                if ((own & HOUSEF_NOD) && tdafld_type >= 0 && Has_Building_Active(tdafld_type))
                    continue;
                if ((own & HOUSEF_ALLIES) && Has_Building_Active(STRUCT_AWEAP))
                    continue;
                if ((own & HOUSEF_SOVIET) && Has_Building_Active(STRUCT_SWEAP))
                    continue;
            }
            // STRUCT_HELIPAD — satisfied by TDHPAD (separated TD helipad).
            // RA's Hind/Longbow/etc. all require STRUCTF_HELIPAD; without this
            // equivalence, players who built a TDHPAD can't see helicopters
            // in the sidebar because the prereq check rejects them.
            if (t == STRUCT_HELIPAD) {
                if ((own & (HOUSEF_GDI | HOUSEF_NOD)) && tdhpad_type >= 0 && Has_Building_Active(tdhpad_type))
                    continue;
                // W2 (d): each faction's helipad satisfies 'hpad' for that
                // faction's entities only.
                if ((own & HOUSEF_ALLIES) && Has_Building_Active(STRUCT_AHPAD))
                    continue;
                if ((own & HOUSEF_SOVIET) && Has_Building_Active(STRUCT_SHPAD))
                    continue;
                if ((own & HOUSEF_GDI) && Has_Building_Active(STRUCT_TDGHPAD))
                    continue;
                if ((own & HOUSEF_NOD) && Has_Building_Active(STRUCT_TDNHPAD))
                    continue;
            }
            // STRUCT_RADAR ('dome') and TDHQ are SEPARATE (Luke, 2026-07-20):
            // radar is faction tech like the tech centres, not shared
            // infrastructure — no cross-equivalence in either direction. TD
            // entities carry explicit TDHQ tokens in rules.ini.
            // STRUCT_REFINERY — satisfied by TDPROC (separated TD refinery).
            // RA's harvester (Prerequisite=proc) becomes buildable when a TDPROC
            // is owned (both GDI and Nod build it).
            if (t == STRUCT_REFINERY) {
                if (tdproc_type >= 0 && Has_Building_Active(tdproc_type))
                    continue;
            }
            // STRUCT_ADVANCED_TECH — satisfied by the faction high-tech building:
            // GDI Advanced Comm (TDEYE) or Nod Temple (TDTMPL). TD's UnitMCV
            // requires STRUCTF_EYE; "atek" maps here and these are the per-faction
            // equivalents (basic comm TDHQ does NOT count). NOTE: Has_Building_Active
            // tests ActiveBQuantity[type], not the BScan bitmask — so a per-type
            // remap like this is required; shadowing STRUCTF_ADVANCED_TECH into
            // BScan does nothing for prereq checks.
            // Tech centres are FACTION IDENTITY (Luke, 2026-07-20): 'atek' on an
            // RA entity means the Allied tech centre and nothing else (the GDI
            // Adv Comm satisfying an Allied Cruiser was the reported leak).
            // Single-faction TD entities carry explicit TDEYE/TDTMPL tokens in
            // rules.ini; this equivalence remains ONLY for TD-era entities still
            // on 'atek' (TDRMBO — shared by both TD factions, and a prereq list
            // is AND-only so "either TD tech centre" can't be spelled there).
            if (t == STRUCT_ADVANCED_TECH && type->IniName[0] == 'T' && type->IniName[1] == 'D') {
                if (tdeye_type >= 0 && Has_Building_Active(tdeye_type))
                    continue;
                if (tdtmpl_type >= 0 && Has_Building_Active(tdtmpl_type))
                    continue;
            }
            // STRUCT_REPAIR — satisfied by TDFIX (GDI service depot). TD's Mammoth
            // Tank (Prerequisite=fix) needs the repair bay; TDFIX is the GDI equivalent.
            if (t == STRUCT_REPAIR) {
                if (tdfix_type >= 0 && Has_Building_Active(tdfix_type))
                    continue;
            }
            // STRUCT_POWER — satisfied by the TD power plants (TDNUKE / TDNUK2). GDI/Nod never build
            // RA's POWR/APWR (those are allies,soviet), so RA structures keyed to Prerequisite=powr —
            // e.g. the owner-opened Allied Shipyard (SYRD) for the GDI Gunboat — would otherwise be
            // unbuildable for GDI. v4.0.
            if (t == STRUCT_POWER) {
                if (tdnuke_type >= 0 && Has_Building_Active(tdnuke_type))
                    continue;
                if (tdnuk2_type >= 0 && Has_Building_Active(tdnuk2_type))
                    continue;
            }
            // v4.0 separated naval/air production buildings satisfy the RA-token prereqs of the
            // units they build: syrd->TDGYARD (GDI Gunboat/Hovercraft), spen->TDNPEN (Nod subs/
            // Hovercraft), afld->TDGAFLD (GDI A-10). Same pattern as hpad->TDHPAD etc.
            if (t == STRUCT_SHIP_YARD && (own & HOUSEF_GDI) && tdgyard_type >= 0 && Has_Building_Active(tdgyard_type))
                continue;
            if (t == STRUCT_SUB_PEN && (own & HOUSEF_NOD) && tdnpen_type >= 0 && Has_Building_Active(tdnpen_type))
                continue;
            if (t == STRUCT_AIRSTRIP && (own & HOUSEF_GDI) && tdgafld_type >= 0 && Has_Building_Active(tdgafld_type))
                continue;
            // Cross-era infrastructure equivalence (Luke, 2026-07-19): either
            // era's power plant or refinery satisfies BOTH eras' tokens, so a
            // captured tech tree never demands a duplicate of a basic the
            // house already runs. The RA-token direction (powr/proc ->
            // satisfied by TD buildings) is above; this is the TD-token
            // direction (TDNUKE/TDPROC <- satisfied by RA buildings). The
            // advanced plants count as power on both sides, mirroring the
            // vanilla POWER<-ADVANCED_POWER rule. (Repair bay needs no clause:
            // nothing requires "TDFIX" by name — all repair-bay gating uses
            // the vanilla 'fix' token, remapped above.)
            if (t == tdnuke_type
                && (Has_Building_Active(STRUCT_POWER) || Has_Building_Active(STRUCT_ADVANCED_POWER)
                    || (tdnuk2_type >= 0 && Has_Building_Active(tdnuk2_type))))
                continue;
            if (t == tdproc_type && Has_Building_Active(STRUCT_REFINERY))
                continue;
        }
        return (false);
    }
    return (true);
}

/***************************************************************************
 * HouseClass::Init -- init's in preparation for new scenario              *
 *                                                                         *
 * INPUT:                                                                  *
 *      none.                                                              *
 *                                                                         *
 * OUTPUT:                                                                 *
 *      none.                                                              *
 *                                                                         *
 * WARNINGS:                                                               *
 *      none.                                                              *
 *                                                                         *
 * HISTORY:                                                                *
 *   12/07/1994 BR : Created.                                              *
 *   12/17/1994 JLB : Resets tracker bits.                                 *
 *=========================================================================*/
void HouseClass::Init(void)
{
    Houses.Free_All();

    for (HousesType index = HOUSE_FIRST; index < HOUSE_COUNT; index++) {
        HouseTriggers[index].Clear();
    }
}

// Object selection list is switched with player context for GlyphX. ST - 8/7/2019 10:11AM
extern void Logic_Switch_Player_Context(HouseClass* house);
extern bool MPSuperWeaponDisable;

/***********************************************************************************************
 * HouseClass::AI -- Process house logic.                                                      *
 *                                                                                             *
 *    This handles the AI for the house object. It should be called once per house per game    *
 *    tick. It processes all house global tasks such as low power damage accumulation and      *
 *    house specific trigger events.                                                           *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   12/27/1994 JLB : Created.                                                                 *
 *   07/17/1995 JLB : Limits EVA speaking unless the player can do something.                  *
 *=============================================================================================*/
extern void Recalculate_Placement_Distances();

void HouseClass::AI(void)
{
    assert(Houses.ID(this) == ID);
#ifdef REMASTER_BUILD
    // Set PlayerPtr to be this house. ST - 8/7/2019 10:12AM
    Logic_Switch_Player_Context(this);
#endif
    /*
    **	If base building has been turned on by a trigger, then force the house to begin
    **	production and team creation as well. This is also true if the IQ is high enough to
    **	being base building.
    **
    **	Tiberian Factions: rules.ini lowers IQProduction to 3 so skirmish Easy AIs (IQ 3)
    **	still base-build -- a skirmish/MP tuning only. Stock campaigns are balanced around
    **	vanilla's threshold (MaxIQ), where a scripted enemy with a modest IQ stays static
    **	until a trigger sets IsBaseBuilding. In campaign, use the vanilla threshold so we
    **	don't wake enemies EA meant to sit still (they were producing units and base-
    **	building far too early otherwise).
    */
    int iq_production = (Session.Type == GAME_NORMAL) ? Rule.MaxIQ : Rule.IQProduction;
    if (!IsHuman && (IsBaseBuilding || IQ >= iq_production)) {
        IsBaseBuilding = true;
        IsStarted = true;
        IsAlerted = true;
    }

    /*
    **	Check to see if the house wins.
    */
    if (Session.Type == GAME_NORMAL && IsToWin && BorrowedTime == 0 && Blockage <= 0) {
        IsToWin = false;
        if (this == PlayerPtr) {
            PlayerWins = true;
        } else {
            PlayerLoses = true;
        }
    }

    /*
    **	Check to see if the house loses.
    */
    if (Session.Type == GAME_NORMAL && IsToLose && BorrowedTime == 0) {
        IsToLose = false;
        if (this == PlayerPtr) {
            PlayerLoses = true;
        } else {
            PlayerWins = true;
        }
    }

    /*
    **	Check to see if all objects of this house should be blown up.
    */
    if (IsToDie && BorrowedTime == 0) {
        IsToDie = false;
        Blowup_All();
        if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
            MPlayer_Defeated();
        }
    }

    /*
    **	Double check power values to correct illegal conditions. It is possible to
    **	get a power output of negative (one usually) as a result of damage sustained
    **	and the fixed point fractional math involved with power adjustments. If the
    **	power rating drops below zero, then make it zero.
    */
    Power = max(Power, 0);
    Drain = max(Drain, 0);

    /*
    **	If the base has been alerted to the enemy and should be attacking, then
    **	see if the attack timer has expired. If it has, then create the attack
    **	teams.
    */
    if (IsAlerted && AlertTime == 0) {

        /*
        **	Adjusted to reduce maximum number of teams created.
        */
        int maxteams = Random_Pick(2, (int)(((Control.TechLevel - 1) / 3) + 1));
        for (int index = 0; index < maxteams; index++) {
            TeamTypeClass const* ttype = Suggested_New_Team(true);
            if (ttype != NULL) {
                ScenarioInit++;
                ttype->Create_One_Of();
                ScenarioInit--;
            }
        }
        AlertTime = Rule.AutocreateTime * Random_Pick(TICKS_PER_MINUTE / 2, TICKS_PER_MINUTE * 2);
        //		int mintime = Rule.AutocreateTime * (TICKS_PER_MINUTE/2);
        //		int maxtime = Rule.AutocreateTime * (TICKS_PER_MINUTE*2);
        //		AlertTime = Random_Pick(mintime, maxtime);
    }

    /*
    **	If this house's flag waypoint is a valid cell, see if there's
    **	someone sitting on it.  If so, make the scatter.
    */
    if (FlagHome != 0 && (Frame % TICKS_PER_SECOND) == 0) {

        TechnoClass* techno = Map[FlagHome].Cell_Techno();
        if (techno != NULL) {
            bool moving = false;
            if (techno->Is_Foot()) {
                if (Target_Legal(((FootClass*)techno)->NavCom)) {
                    moving = true;
                }
            }

            if (!moving) {
                techno->Scatter(0, true, true);
            }
        }
    }

    /*
    **	Create teams for this house if necessary.
    ** (Use the same timer for some extra capture-the-flag logic.)
    */
    if (!IsAlerted && !TeamTime) {

        TeamTypeClass const* ttype = Suggested_New_Team(false);
        if (ttype) {
            ttype->Create_One_Of();
        }

        TeamTime = Rule.TeamDelay * TICKS_PER_MINUTE;
    }

    /*
    **	If there is insufficient power, then all buildings that are above
    **	half strength take a little bit of damage.
    */
    if (DamageTime == 0) {

        /*
        **	When the power is below required, then the buildings will take damage over
        **	time.
        */
        if (Power_Fraction() < 1) {
            for (int index = 0; index < Buildings.Count(); index++) {
                BuildingClass& b = *Buildings.Ptr(index);

                if (b.House == this && b.Health_Ratio() > Rule.ConditionYellow) {
                    // BG: Only damage buildings that require power, to keep the
                    //     land mines from blowing up under low-power conditions
                    if (b.Class->Drain) {
                        int damage = 1;
                        b.Take_Damage(damage, 0, WARHEAD_AP, 0);
                    }
                }
            }
        }
        DamageTime = TICKS_PER_MINUTE * Rule.DamageDelay;
    }

    /*
    **	If there are no more buildings to sell, then automatically cancel the
    **	sell mode.
    */
    if (PlayerPtr == this && !ActiveBScan && Map.IsSellMode) {
        Map.Sell_Mode_Control(0);
    }

    /*
    **	Various base conditions may be announced to the player. Typically, this would be
    **	low tiberium capacity or low power.
    */
    if (PlayerPtr == this) {

        if (SpeakMaxedDelay == 0 && Available_Money() < 100
            && UnitFactories + BuildingFactories + InfantryFactories > 0) {
            Speak(VOX_NEED_MO_MONEY);
            Map.Flash_Money();
            SpeakMaxedDelay = Options.Normalize_Delay(TICKS_PER_MINUTE * Rule.SpeakDelay);

            int text_id = TXT_INSUFFICIENT_FUNDS;
            char const* text = Text_String(TXT_INSUFFICIENT_FUNDS);
            if (text != NULL) {
                Session.Messages.Add_Message(NULL,
                                             text_id,
                                             text,
                                             PCOLOR_GREEN,
                                             TPF_6PT_GRAD | TPF_USE_GRAD_PAL | TPF_FULLSHADOW,
                                             Rule.MessageDelay * TICKS_PER_MINUTE);
            }
        }

        if (SpeakMaxedDelay == 0 && IsMaxedOut) {
            IsMaxedOut = false;
            if ((Capacity - Tiberium) < 300 && Capacity > 500 && (ActiveBScan & (STRUCTF_REFINERY | STRUCTF_CONST))) {
                Speak(VOX_NEED_MO_CAPACITY);
                SpeakMaxedDelay = Options.Normalize_Delay(TICKS_PER_MINUTE * Rule.SpeakDelay);
            }
        }
        if (SpeakPowerDelay == 0 && Power_Fraction() < 1) {
            if (ActiveBScan & STRUCTF_CONST) {
                Speak(VOX_LOW_POWER);
                SpeakPowerDelay = Options.Normalize_Delay(TICKS_PER_MINUTE * Rule.SpeakDelay);
                Map.Flash_Power();

                int text_id = -1;
                char const* text = NULL;
                if (BQuantity[STRUCT_AAGUN] > 0) {
                    text = Text_String(TXT_POWER_AAGUN);
                    text_id = TXT_POWER_AAGUN;
                }
                if (BQuantity[STRUCT_TESLA] > 0) {
                    text = Text_String(TXT_POWER_TESLA);
                    text_id = TXT_POWER_TESLA;
                }
                if (text == NULL) {
                    text = Text_String(TXT_LOW_POWER);
                    text_id = TXT_LOW_POWER;
                }
                if (text != NULL) {
                    Session.Messages.Add_Message(NULL,
                                                 text_id,
                                                 text,
                                                 PCOLOR_GREEN,
                                                 TPF_6PT_GRAD | TPF_USE_GRAD_PAL | TPF_FULLSHADOW,
                                                 Rule.MessageDelay * TICKS_PER_MINUTE);
                }
            }
        }
    }

    /*
    **	If there is a flag associated with this house, then mark it to be
    **	redrawn.
    */
    if (Target_Legal(FlagLocation)) {
        UnitClass* unit = As_Unit(FlagLocation);
        if (unit) {
            unit->Mark(MARK_CHANGE);
        } else {
            CELL cell = As_Cell(FlagLocation);
            Map[cell].Flag_Update();
            Map[cell].Redraw_Objects();
        }
    }

    bool is_time = false;

    /*
    **	Triggers are only checked every so often. If the trigger timer has expired,
    **	then set the trigger processing flag.
    */
    if (TriggerTime == 0 || IsBuiltSomething) {
        is_time = true;
        TriggerTime = TICKS_PER_MINUTE / 10;
        IsBuiltSomething = false;
    }

    /*
    **	Process any super weapon logic required.
    */
#ifdef REMASTER_BUILD
    if (Session.Type != GAME_GLYPHX_MULTIPLAYER || !MPSuperWeaponDisable) {
        Super_Weapon_Handler();
    }
#else
    Super_Weapon_Handler();
#endif
#ifdef FIXIT_VERSION_3 //	For endgame auto-sonar pulse.
    if ((Session.Type != GAME_NORMAL || !IsHuman) && Scen.AutoSonarTimer == 0) {
        //	If house has nothing but subs left, do an automatic sonar pulse to reveal them.
        if (VQuantity[VESSEL_SS] > 0) //	Includes count of VESSEL_MISSILESUBs. ajw
        {
            int iCount = 0;
            int i;
            for (i = 0; i != STRUCT_COUNT - 3; ++i) {
                iCount += BQuantity[i];
            }
            if (!iCount) {
                for (i = 0; i != UNIT_RA_COUNT - 3; ++i) {
                    iCount += UQuantity[i];
                }
                if (!iCount) {
                    //	ajw - Found bug - house's civilians are not removed from IQuantity when they die.
                    //	Workaround...
                    for (i = 0; i <= INFANTRY_DOG; ++i) {
                        iCount += IQuantity[i];
                    }
                    if (!iCount) {
                        for (i = 0; i != AIRCRAFT_COUNT; ++i) {
                            iCount += AQuantity[i];
                        }
                        if (!iCount) {
                            for (i = 0; i != VESSEL_RA_COUNT; ++i) {
                                if (i != VESSEL_SS)
                                    iCount += VQuantity[i];
                            }
                            if (!iCount) {
                                //	Do the ping.
                                for (int index = 0; index < Vessels.Count(); index++) {
                                    VesselClass* sub = Vessels.Ptr(index);
                                    if (*sub == VESSEL_SS || *sub == VESSEL_MISSILESUB) {
                                        sub->PulseCountDown = 15 * TICKS_PER_SECOND;
                                        sub->Do_Uncloak();
                                    }
                                }
                                bAutoSonarPulse = true;
                            }
                        }
                    }
                }
            }
        }
    }
#endif

    if (Session.Type != GAME_NORMAL) {
        Check_Pertinent_Structures();
    }

    /*
    ** Special win/lose check for multiplayer games; by-passes the
    ** trigger system.  We must wait for non-zero frame, because init
    ** may not properly set IScan etc for each house; you have to go
    ** through each object's AI before it will be properly set.
    */
    if (Session.Type != GAME_NORMAL && !IsDefeated && !ActiveBScan && !ActiveAScan && !UScan && !ActiveIScan
        && !ActiveVScan && Frame > 0) {
        MPlayer_Defeated();
    }

    /*
    **	Try to spring all events attached to this house. The triggers will check
    **	for themselves if they actually need to be sprung or not.
    */
    for (int index = 0; index < HouseTriggers[Class->House].Count(); index++) {
        if (HouseTriggers[Class->House][index]->Spring() && index > 0) {
            index--;
            continue;
        }
    }

    /*
    **	If a radar facility is not present, but the radar is active, then turn the radar off.
    **	The radar also is turned off when the power gets below 100% capacity.
    */
    if (PlayerPtr == this) {
        bool jammed = true;

#ifndef REMASTER_BUILD
        /*
        ** Undocumented change in Remaster source, should check if radar is active before trying to jam.
        ** OmniBlade - 13/07/2020
        */
        jammed = Map.Is_Radar_Active();
#endif

        /*
        ** Find if there are any radar facilities, and if they're jammed or not
        */

        if (IsGPSActive) {
            jammed = false;
        } else {
            for (int index = 0; index < Buildings.Count(); index++) {
                BuildingClass* building = Buildings.Ptr(index);
#ifdef FIXIT_RADAR_JAMMED
                if (building != NULL && !building->IsInLimbo && building->House == PlayerPtr) {
#else
                if (building && building->House == PlayerPtr) {
#endif
                    if (*building == STRUCT_RADAR || *building == STRUCT_TDHQ || *building == STRUCT_TDEYE) {
                        if (!building->IsJammed) {
                            jammed = false;
                            break;
                        }
                    }
                }
            }
        }

#ifndef REMASTER_BUILD
        if (Map.Get_Jammed(this) != jammed) {
            Map.RadarClass::Flag_To_Redraw(true);
        }
#endif

        Map.Set_Jammed(this, jammed);
        // Need to add in here where we activate it when only GPS is active.
        if (Map.Is_Radar_Active()) {
            if (ActiveBScan & STRUCTF_RADAR) {
                if (Power_Fraction() < 1 && !IsGPSActive) {
                    Map.Radar_Activate(0);
                }
            } else {
                if (!IsGPSActive) {
                    Map.Radar_Activate(0);
                }
            }

        } else {
            if (IsGPSActive || (ActiveBScan & STRUCTF_RADAR)) {
                if (Power_Fraction() >= 1 || IsGPSActive) {
                    Map.Radar_Activate(1);
                }
            } else {
                if (Map.Is_Radar_Existing()) {
                    Map.Radar_Activate(4);
                }
            }
        }
        if (!IsGPSActive && !(ActiveBScan & STRUCTF_RADAR)) {
            Radar = RADAR_NONE;
        } else {
            Radar = (Map.Is_Radar_Active() || Map.Is_Radar_Activating()) ? RADAR_ON : RADAR_OFF;
        }

#ifdef REMASTER_BUILD
        // Tiberian Factions: radar on/off sting for the LOCAL player.
        //
        // Fire on a STABLE "has a powered radar building" signal -- a Buildings-heap
        // count of the player's radar structures (STRUCT_RADAR / STRUCT_TDHQ /
        // STRUCT_TDEYE) AND Power_Fraction() -- NOT the scan bits. This is the crux of
        // the 2026-06-03 radar-loop saga: ActiveBScan/BScan & STRUCTF_RADAR (and the
        // derived `this->Radar` / global Map.IsRadarActive) OSCILLATE 1/0 every single
        // frame at full power -- a Recalc_Attributes rebuild quirk proven by
        // tf_radar.log -- so every edge-detector polled on the scan state looped the
        // sting infinitely. The heap count only changes on a real build/destroy, and
        // Power_Fraction() is steady at steady state, so `functional` below is stable
        // and fires exactly once on radar-online and once on radar-offline (power up /
        // down) -- which is the desired behaviour. A short debounce makes it impossible
        // to machine-gun even if either input ever twitches. The launcher's own
        // hardcoded radar auto-fire stays muted by the silent RADARON2/RADARDN1 stubs;
        // per-faction routing (RAORAD*/TFRADR*) is in dllinterface On_Sound_Effect.
        // Gate on IsHuman, NOT `this == PlayerPtr`: in REMASTER_BUILD HouseClass::AI
        // calls Logic_Switch_Player_Context(this) at its top (line ~1208), so PlayerPtr
        // is reassigned to the current house and `this == PlayerPtr` is ALWAYS true ->
        // the block ran for EVERY house, and radar_count alternated between the human
        // (1 radar) and the AI (0) each frame, thrashing the shared debounce so nothing
        // fired (proven by tf_radar2.log). IsHuman is true only for the human house(s);
        // in skirmish that's the single local player. (Network play with 2+ humans would
        // still thrash the shared static -> no sting, but no loop; gate on the local
        // GlyphX player index if per-client MP radar sound is ever wanted.)
        if (IsHuman) {
            int radar_count = 0;
            for (int ri = 0; ri < Buildings.Count(); ri++) {
                BuildingClass* rb = Buildings.Ptr(ri);
                // Skip !IsInLimbo: a building being produced in the sidebar exists in
                // the Buildings heap in LIMBO before it is placed on the map, so without
                // this guard the sting fired the instant you clicked the radar in the
                // sidebar instead of when you place it (= when it comes online).
                if (rb != NULL && !rb->IsInLimbo && rb->House == PlayerPtr
                    && (*rb == STRUCT_RADAR || *rb == STRUCT_TDHQ || *rb == STRUCT_TDEYE)) {
                    radar_count++;
                }
            }
            bool functional = (radar_count > 0 || IsGPSActive) && (IsGPSActive || Power_Fraction() >= 1);

            // Debounce: only commit (and sound) a state that has held for ~0.5s, so a
            // per-frame twitch in either input can never produce a repeating sting.
            static bool tf_radar_on = false; // last committed/sounded state
            static bool tf_pending = false;  // candidate state being timed
            static int tf_stable = 0;        // frames the candidate has held
            if (functional != tf_pending) {
                tf_pending = functional;
                tf_stable = 0;
            } else if (tf_stable < 8) {
                tf_stable++;
            }
            if (tf_stable >= 8 && tf_pending != tf_radar_on) {
                if (tf_pending) {
                    Sound_Effect(VOC_RADAR_ON);
                } else {
                    Sound_Effect(VOC_RADAR_OFF);
                }
                tf_radar_on = tf_pending;
            }
        }
#endif
    }

    VisibleCredits.AI(false, this, true);

    /*
    **	Perform any expert system AI processing.
    */
    if (IsBaseBuilding && AITimer == 0) {
        AITimer = Expert_AI();
    }

    if (!IsBaseBuilding && State == STATE_ENDGAME) {
        Fire_Sale();
        Do_All_To_Hunt();
    }

    AI_Building();
    AI_Unit();
    AI_Vessel();
    AI_Infantry();
    AI_Aircraft();

    /*
    **	If the production possibilities need to be recalculated, then do so now. This must
    **	occur after the scan bits have been properly updated.
    */
    if (PlayerPtr == this && IsRecalcNeeded) {
        IsRecalcNeeded = false;
        Map.Recalc();

        /*
        **	This placement might affect any prerequisite requirements for construction
        **	lists. Update the buildable options accordingly.
        */
        for (int index = 0; index < Buildings.Count(); index++) {
            BuildingClass* building = Buildings.Ptr(index);
            if (building && building->Strength > 0 && building->Owner() == Class->House
                && building->Mission != MISSION_DECONSTRUCTION && building->MissionQueue != MISSION_DECONSTRUCTION) {

                if (PlayerPtr == building->House) {
                    building->Update_Buildables();
                }
            }
        }
#ifdef REMASTER_BUILD
        Recalculate_Placement_Distances();
#endif
        Check_Pertinent_Structures();
    }

    /*
    ** See if it's time to re-set the can-repair flag
    */
    if (DidRepair && RepairTimer == 0) {
        DidRepair = false;
    }

    if (this == PlayerPtr && IsToLook) {
        IsToLook = false;
        Map.All_To_Look(PlayerPtr);
    }
}

/***********************************************************************************************
 * HouseClass::Super_Weapon_Handler -- Handles the super weapon charge and discharge logic.    *
 *                                                                                             *
 *    This handles any super weapons assigned to this house. It also performs any necessary    *
 *    maintenance that the super weapons require.                                              *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/17/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Super_Weapon_Handler(void)
{
    /*
    **	Perform all super weapon AI processing. This just checks to see if
    **	the graphic needs changing for the special weapon and updates the
    **	sidebar as necessary.
    */
    for (SpecialWeaponType special = SPC_FIRST; special < SPC_COUNT; special++) {
        SuperClass* super = &SuperWeapon[special];

        if (super->Is_Present()) {

            /*
            **	Perform any charge-up logic for the super weapon. If the super
            **	weapon is owned by the player and a graphic change is detected, then
            **	flag the sidebar to be redrawn so the player will see the change.
            */
            if (super->AI(this == PlayerPtr)) {
                if (this == PlayerPtr)
                    Map.Column[1].Flag_To_Redraw();
            }

            /*
            **	Repeating super weapons that require power will be suspended if there
            **	is insufficient power available.
            */
            if (!super->Is_Ready() && super->Is_Powered() && !super->Is_One_Time()) {
                super->Suspend(Power_Fraction() < 1);
            }
        }
    }

    /*
    ** Does this house still own a GPS-granting tech centre? Mirror the grant test below
    ** (~line 1912): Allied Advanced Tech (STRUCTF_ADVANCED_TECH) OR GDI's Eye (TDEYE). TDEYE is
    ** past the 32-bit BScan mask, so the raw STRUCTF_ADVANCED_TECH test never sees it -- without
    ** this, GDI's GPS was revoked and its sidebar icon removed every frame (flicker, no tooltip).
    ** Not TDTMPL: Nod gets the targeted Spy Plane, not full-map GPS.
    */
    bool has_gps_techcenter = ((ActiveBScan & STRUCTF_ADVANCED_TECH) != 0) || Has_Building_Active(STRUCT_TDEYE);

    /*
    ** Check to see if they have launched the GPS, but subsequently lost their
    ** tech center.  If so, remove the GPS, and shroud the map.
    */
    if (IsGPSActive && !has_gps_techcenter) {
        IsGPSActive = false;

        /*
        ** Updated for client/server multiplayer. ST  - 8/12/2019 11:32AM
        */
        if (Session.Type != GAME_GLYPHX_MULTIPLAYER) {
            if (IsPlayerControl) {
                Map.Shroud_The_Map(PlayerPtr);
            }

        } else {

            if (IsHuman) {
                Map.Shroud_The_Map(this);
            }
        }
    }

    /*
    **	Check to see if the GPS Satellite should be removed from the sidebar
    **	because of outside circumstances. The advanced technology facility
    **	being destroyed is a good example of this.  Having fired the satellite
    ** is another good example, because it's a one-shot item.
    */
    if (SuperWeapon[SPC_GPS].Is_Present()) {
        if (!has_gps_techcenter || IsGPSActive || IsDefeated) {
            /*
            **	Remove the missile capability when there is no advanced tech facility.
            */
            if (SuperWeapon[SPC_GPS].Remove()) {
                if (this == PlayerPtr)
                    Map.Column[1].Flag_To_Redraw();
                IsRecalcNeeded = true;
            }
        } else {
            /*
            ** Auto-fire the GPS satellite if it's charged up.
            */
            if (SuperWeapon[SPC_GPS].Is_Ready()) {
                SuperWeapon[SPC_GPS].Discharged(this == PlayerPtr);
                if (SuperWeapon[SPC_GPS].Remove()) {
                    if (this == PlayerPtr)
                        Map.Column[1].Flag_To_Redraw();
                }
                IsRecalcNeeded = true;
                for (int index = 0; index < Buildings.Count(); index++) {
                    BuildingClass* bldg = Buildings.Ptr(index);
                    // GDI's tech centre is TDEYE, not ADVANCED_TECH -- match both, or a GDI GPS
                    // never marks HasFired (so the grant re-enables it next frame -> "began again")
                    // and never gets MISSION_MISSILE (so the satellite never launches -> no reveal).
                    if ((*bldg == STRUCT_ADVANCED_TECH || *bldg == STRUCT_TDEYE) && bldg->House == this) {
                        bldg->HasFired = true;
                        bldg->Assign_Mission(MISSION_MISSILE);
                        break;
                    }
                }
            }
        }
    } else {
        /*
        **	If there is no GPS satellite present, but there is a GPS satellite
        **	facility available, then make the GPS satellite available as well.
        */
        if (((ActiveBScan & STRUCTF_ADVANCED_TECH) != 0 || Has_Building_Active(STRUCT_TDEYE)) && !IsGPSActive
            && Control.TechLevel >= Rule.GPSTechLevel && (IsHuman || IQ >= Rule.IQSuperWeapons)) {

            // GDI GPS: the Advanced Comm (TDEYE) is GDI's tech-centre equivalent, so it grants
            // the GPS satellite exactly as the Allied Tech Center does. TDEYE is past the 32-bit
            // BScan mask, hence the Has_Building_Active gate above rather than a STRUCTF_ flag.
            bool canfire = false;
            for (int index = 0; index < Buildings.Count(); index++) {
                BuildingClass* bldg = Buildings.Ptr(index);
                if ((*bldg == STRUCT_ADVANCED_TECH || *bldg == STRUCT_TDEYE) && bldg->House == this && !bldg->IsInLimbo) {
                    if (!bldg->HasFired) {
                        canfire = true;
                        break;
                    }
                }
            }

            if (canfire) {
                SuperWeapon[SPC_GPS].Enable(false, this == PlayerPtr, Power_Fraction() < 1);

                /*
                **	Flag the sidebar to be redrawn if necessary.
                */
                // Add to Glyphx multiplayer sidebar. ST - 8/7/2019 10:13AM
                if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                    if (IsHuman) {
#ifdef REMASTER_BUILD
                        Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_GPS, this);
#endif
                    }
                } else {
                    if (this == PlayerPtr) {
                        Map.Add(RTTI_SPECIAL, SPC_GPS);
                        Map.Column[1].Flag_To_Redraw();
                    }
                }
            }
        }
    }

    /*
    **	Check to see if the chronosphere should be removed from the sidebar
    **	because of outside circumstances. The chronosphere facility
    **	being destroyed is a good example of this.
    */
    if (SuperWeapon[SPC_CHRONOSPHERE].Is_Present()) {
        if ((!(ActiveBScan & STRUCTF_CHRONOSPHERE) && !SuperWeapon[SPC_CHRONOSPHERE].Is_One_Time()) || IsDefeated) {

            /*
            **	Remove the chronosphere when there is no chronosphere facility.
            **	Note that this will not remove the one time created chronosphere.
            */
            if (SuperWeapon[SPC_CHRONOSPHERE].Remove()) {
                if (this == PlayerPtr) {
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
                    if (Map.IsTargettingMode == SPC_CHRONOSPHERE || Map.IsTargettingMode == SPC_CHRONO2) {
                        if (Map.IsTargettingMode == SPC_CHRONO2) {
                            TechnoClass* tech = (TechnoClass*)::As_Object(UnitToTeleport);
                            if (tech && tech->IsActive && tech->What_Am_I() == RTTI_UNIT
                                && *(UnitClass*)tech == UNIT_CHRONOTANK) {
                            } else {
                                Map.IsTargettingMode = SPC_NONE;
                            }
                        } else {
                            Map.IsTargettingMode = SPC_NONE;
                        }
                    }
#else
                    if (Map.IsTargettingMode == SPC_CHRONOSPHERE || Map.IsTargettingMode == SPC_CHRONO2) {
                        Map.IsTargettingMode = SPC_NONE;
                    }
#endif
                    Map.Column[1].Flag_To_Redraw();
                }
                IsRecalcNeeded = true;
            }
        }
    } else {
        /*
        **	If there is no chronosphere present, but there is a chronosphere
        **	facility available, then make the chronosphere available as well.
        */
        if ((ActiveBScan & STRUCTF_CHRONOSPHERE) &&
            //			(ActLike == HOUSE_GOOD || Session.Type != GAME_NORMAL) &&
            (unsigned)Control.TechLevel >= BuildingTypeClass::As_Reference(STRUCT_CHRONOSPHERE).Level &&
            //			Control.TechLevel >= Rule.ChronoTechLevel &&
            (IsHuman || IQ >= Rule.IQSuperWeapons)) {

            SuperWeapon[SPC_CHRONOSPHERE].Enable(false, this == PlayerPtr, Power_Fraction() < 1);

            /*
            **	Flag the sidebar to be redrawn if necessary.
            */
            // Add to Glyphx multiplayer sidebar. ST - 8/7/2019 10:13AM
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_CHRONOSPHERE, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_CHRONOSPHERE);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    /*
    **	Check to see if the iron curtain should be removed from the sidebar
    **	because of outside circumstances. The iron curtain facility
    **	being destroyed is a good example of this.
    */
    if (SuperWeapon[SPC_IRON_CURTAIN].Is_Present()) {
        if ((!(ActiveBScan & STRUCTF_IRON_CURTAIN) && !SuperWeapon[SPC_IRON_CURTAIN].Is_One_Time()) || IsDefeated) {

            /*
            **	Remove the iron curtain when there is no iron curtain facility.
            **	Note that this will not remove the one time created iron curtain.
            */
            if (SuperWeapon[SPC_IRON_CURTAIN].Remove()) {
                if (this == PlayerPtr) {
                    if (Map.IsTargettingMode == SPC_IRON_CURTAIN) {
                        Map.IsTargettingMode = SPC_NONE;
                    }
                    Map.Column[1].Flag_To_Redraw();
                }
                IsRecalcNeeded = true;
            }
        }
    } else {
        /*
        **	If there is no iron curtain present, but there is an iron curtain
        **	facility available, then make the iron curtain available as well.
        */
        if ((ActiveBScan & STRUCTF_IRON_CURTAIN)
            && (ActLike == HOUSE_USSR || ActLike == HOUSE_UKRAINE || Session.Type != GAME_NORMAL)
            && (IsHuman || IQ >= Rule.IQSuperWeapons)) {

            SuperWeapon[SPC_IRON_CURTAIN].Enable(false, this == PlayerPtr, Power_Fraction() < 1);

            /*
            **	Flag the sidebar to be redrawn if necessary.
            */
            // Add to Glyphx multiplayer sidebar. ST - 8/7/2019 10:13AM
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_IRON_CURTAIN, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_IRON_CURTAIN);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    /*
    **	Check to see if the sonar pulse should be removed from the sidebar
    **	because of outside circumstances. The spied-upon enemy sub pen
    **	being destroyed is a good example of this.
    */
    if (SuperWeapon[SPC_SONAR_PULSE].Is_Present()) {
        int usspy = 1 << (Class->House);
        bool present = false;
        bool powered = false;
        for (int q = 0; q < Buildings.Count() && !powered; q++) {
            BuildingClass* bldg = Buildings.Ptr(q);
            if ((*bldg == STRUCT_SUB_PEN) && (bldg->House->Class->House != Class->House)
                && (bldg->Spied_By() & usspy)) {
                present = true;
                powered = !(bldg->House->Power_Fraction() < 1);
            }
        }
        if ((!present && !SuperWeapon[SPC_SONAR_PULSE].Is_One_Time()) || IsDefeated) {

            /*
            **	Remove the sonar pulse when there is no spied-upon enemy sub pen.
            **	Note that this will not remove the one time created sonar pulse.
            */
            if (SuperWeapon[SPC_SONAR_PULSE].Remove()) {
                if (this == PlayerPtr)
                    Map.Column[1].Flag_To_Redraw();
                IsRecalcNeeded = true;
            }
        }
    }

    /*
    **	Check to see if the nuclear weapon should be removed from the sidebar
    **	because of outside circumstances. The missile silos
    **	being destroyed is a good example of this.
    */
    if (SuperWeapon[SPC_NUCLEAR_BOMB].Is_Present()) {
        if ((!(ActiveBScan & STRUCTF_MSLO) && !SuperWeapon[SPC_NUCLEAR_BOMB].Is_One_Time()) || IsDefeated) {

            /*
            **	Remove the nuke when there is no missile silo.
            **	Note that this will not remove the one time created nuke.
            */
            if (SuperWeapon[SPC_NUCLEAR_BOMB].Remove()) {
                if (this == PlayerPtr) {
                    if (Map.IsTargettingMode == SPC_NUCLEAR_BOMB) {
                        Map.IsTargettingMode = SPC_NONE;
                    }
                    Map.Column[1].Flag_To_Redraw();
                }
                IsRecalcNeeded = true;
            }
        } else {
            /*
            **	Allow the computer to fire the nuclear weapon when the weapon is
            **	ready and the owner is the computer.
            */
            if (SuperWeapon[SPC_NUCLEAR_BOMB].Is_Ready() && !IsHuman) {
                Special_Weapon_AI(SPC_NUCLEAR_BOMB);
            }
        }

    } else {
        /*
        **	If there is no nuclear missile present, but there is a missile
        **	silo available, then make the missile available as well.
        */
        if ((ActiveBScan & STRUCTF_MSLO)
            && ((ActLike != HOUSE_USSR && ActLike != HOUSE_UKRAINE) || Session.Type != GAME_NORMAL)
            && (IsHuman || IQ >= Rule.IQSuperWeapons)) {

            SuperWeapon[SPC_NUCLEAR_BOMB].Enable(false, this == PlayerPtr, Power_Fraction() < 1);

            /*
            **	Flag the sidebar to be redrawn if necessary.
            */
            // Add to Glyphx multiplayer sidebar. ST - 8/7/2019 10:13AM
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_NUCLEAR_BOMB, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_NUCLEAR_BOMB);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    /*
    **  Tiberian Factions mod — GDI Ion Cannon (SPC_TD_ION_CANNON). Mirrors
    **  the SPC_NUCLEAR_BOMB block above, swapped for TDEYE as the host
    **  building. Uses Has_Building_Active(STRUCT_TDEYE) because the heap
    **  type is past 31 (STRUCT_TDEYE can't fit in the 32-bit BScan mask).
    **  No side restriction here — any house with a TDEYE gets the super,
    **  which matches HOUSEF_GOOD ownership on the building itself.
    */
    if (SuperWeapon[SPC_TD_ION_CANNON].Is_Present()) {
        if ((!Has_Building_Active(STRUCT_TDEYE) && !SuperWeapon[SPC_TD_ION_CANNON].Is_One_Time()) || IsDefeated) {
            if (SuperWeapon[SPC_TD_ION_CANNON].Remove()) {
                if (this == PlayerPtr) {
                    if (Map.IsTargettingMode == SPC_TD_ION_CANNON) {
                        Map.IsTargettingMode = SPC_NONE;
                    }
                    Map.Column[1].Flag_To_Redraw();
                }
                IsRecalcNeeded = true;
            }
        } else {
            if (SuperWeapon[SPC_TD_ION_CANNON].Is_Ready() && !IsHuman) {
                Special_Weapon_AI(SPC_TD_ION_CANNON);
            }
        }
    } else {
        if (Has_Building_Active(STRUCT_TDEYE) && (IsHuman || IQ >= Rule.IQSuperWeapons)) {
            SuperWeapon[SPC_TD_ION_CANNON].Enable(false, this == PlayerPtr, Power_Fraction() < 1);
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_TD_ION_CANNON, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_TD_ION_CANNON);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    /*
    **  Tiberian Factions mod — Nod Nuclear Strike (SPC_TD_NUKE). Same shape
    **  as the Ion Cannon block above, swapped for TDTMPL as the host
    **  building. Uses Has_Building_Active(STRUCT_TDTMPL) since heap types
    **  past 31 can't represent themselves in BScan.
    */
    if (SuperWeapon[SPC_TD_NUKE].Is_Present()) {
        if ((!Has_Building_Active(STRUCT_TDTMPL) && !SuperWeapon[SPC_TD_NUKE].Is_One_Time()) || IsDefeated) {
            if (SuperWeapon[SPC_TD_NUKE].Remove()) {
                if (this == PlayerPtr) {
                    if (Map.IsTargettingMode == SPC_TD_NUKE) {
                        Map.IsTargettingMode = SPC_NONE;
                    }
                    Map.Column[1].Flag_To_Redraw();
                }
                IsRecalcNeeded = true;
            }
        } else {
            if (SuperWeapon[SPC_TD_NUKE].Is_Ready() && !IsHuman) {
                Special_Weapon_AI(SPC_TD_NUKE);
            }
        }
    } else {
        if (Has_Building_Active(STRUCT_TDTMPL) && (IsHuman || IQ >= Rule.IQSuperWeapons)) {
            SuperWeapon[SPC_TD_NUKE].Enable(false, this == PlayerPtr, Power_Fraction() < 1);
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_TD_NUKE, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_TD_NUKE);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    // The recon flight is a per-era special like the paratroop drops: the Soviet
    // airfield grants the RA spy plane, the Nod airstrip its own recon flight, and
    // a house holding both flies both on separate timers. Concrete-building tests
    // throughout, since the Nod airstrip shadows STRUCTF_AIRSTRIP in the scan.
    if (SuperWeapon[SPC_SPY_MISSION].Is_Present()) {
        if (!Has_Building_Active(STRUCT_AIRSTRIP)) {
            if (SuperWeapon[SPC_SPY_MISSION].Remove()) {
                if (this == PlayerPtr)
                    Map.Column[1].Flag_To_Redraw();
                IsRecalcNeeded = true;
            }
        } else {
            if (this == PlayerPtr && !SuperWeapon[SPC_SPY_MISSION].Is_Ready()) {
                Map.Column[1].Flag_To_Redraw();
            }
            if (SuperWeapon[SPC_SPY_MISSION].Is_Ready() && !IsHuman) {
                Special_Weapon_AI(SPC_SPY_MISSION);
            }
        }
    } else {
        if (Has_Building_Active(STRUCT_AIRSTRIP) && !Scen.IsNoSpyPlane
            && Control.TechLevel >= Rule.SpyPlaneTechLevel) {
            SuperWeapon[SPC_SPY_MISSION].Enable(false, this == PlayerPtr, false);
            // Add to Glyphx multiplayer sidebar. ST - 8/7/2019 10:13AM
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_SPY_MISSION, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_SPY_MISSION);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    if (SuperWeapon[SPC_TD_SPY_MISSION].Is_Present()) {
        if (!Has_Building_Active(STRUCT_TDAFLD)) {
            if (SuperWeapon[SPC_TD_SPY_MISSION].Remove()) {
                if (this == PlayerPtr)
                    Map.Column[1].Flag_To_Redraw();
                IsRecalcNeeded = true;
            }
        } else {
            if (this == PlayerPtr && !SuperWeapon[SPC_TD_SPY_MISSION].Is_Ready()) {
                Map.Column[1].Flag_To_Redraw();
            }
            if (SuperWeapon[SPC_TD_SPY_MISSION].Is_Ready() && !IsHuman) {
                Special_Weapon_AI(SPC_TD_SPY_MISSION);
            }
        }
    } else {
        if (Has_Building_Active(STRUCT_TDAFLD) && !Scen.IsNoSpyPlane
            && Control.TechLevel >= Rule.SpyPlaneTechLevel) {
            SuperWeapon[SPC_TD_SPY_MISSION].Enable(false, this == PlayerPtr, false);
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_TD_SPY_MISSION, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_TD_SPY_MISSION);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    // Parabombs are the Soviet airfield's support power in every session type, not
    // just campaign (air-additions design: each faction's airstrip is its offensive
    // air hub). The concrete-building test also replaces the STRUCTF_AIRSTRIP scan
    // bit, which the Nod airstrip shadows, so only a real Soviet airfield qualifies.
    if (SuperWeapon[SPC_PARA_BOMB].Is_Present()) {
        if (!Has_Building_Active(STRUCT_AIRSTRIP)) {
            if (SuperWeapon[SPC_PARA_BOMB].Remove()) {
                if (this == PlayerPtr)
                    Map.Column[1].Flag_To_Redraw();
                IsRecalcNeeded = true;
            }
        } else {
            if (SuperWeapon[SPC_PARA_BOMB].Is_Ready() && !IsHuman) {
                Special_Weapon_AI(SPC_PARA_BOMB);
            }
        }
    } else {
        if (Has_Building_Active(STRUCT_AIRSTRIP) && Control.TechLevel >= Rule.ParaBombTechLevel) {
            SuperWeapon[SPC_PARA_BOMB].Enable(false, this == PlayerPtr, false);
            // Add to Glyphx multiplayer sidebar. ST - 8/7/2019 10:13AM
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_PARA_BOMB, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_PARA_BOMB);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    // Paratroops are per-era specials: the Soviet airfield grants the RA drop, the Nod
    // airstrip + Hand of Nod grant the TD drop, and a house holding both eras' buildings
    // fields both. The Nod airstrip (TDAFLD) shadows STRUCTF_AIRSTRIP in the scan, so
    // presence and removal both test the concrete building, never the scan bit.
    if (SuperWeapon[SPC_PARA_INFANTRY].Is_Present()) {
        if (!Has_Building_Active(STRUCT_AIRSTRIP)) {
            if (SuperWeapon[SPC_PARA_INFANTRY].Remove()) {
                if (this == PlayerPtr)
                    Map.Column[1].Flag_To_Redraw();
                IsRecalcNeeded = true;
            }
        } else {
            if (SuperWeapon[SPC_PARA_INFANTRY].Is_Ready() && !IsHuman) {
                Special_Weapon_AI(SPC_PARA_INFANTRY);
            }
        }
    } else {
        if (Has_Building_Active(STRUCT_AIRSTRIP) && Control.TechLevel >= Rule.ParaInfantryTechLevel) {
            SuperWeapon[SPC_PARA_INFANTRY].Enable(false, this == PlayerPtr, false);
            // Add to Glyphx multiplayer sidebar. ST - 8/7/2019 10:13AM
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_PARA_INFANTRY, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_PARA_INFANTRY);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    if (SuperWeapon[SPC_TD_PARA_INFANTRY].Is_Present()) {
        if (!Has_Building_Active(STRUCT_TDAFLD) || !Has_Building_Active(STRUCT_TDHAND)) {
            if (SuperWeapon[SPC_TD_PARA_INFANTRY].Remove()) {
                if (this == PlayerPtr)
                    Map.Column[1].Flag_To_Redraw();
                IsRecalcNeeded = true;
            }
        } else {
            if (SuperWeapon[SPC_TD_PARA_INFANTRY].Is_Ready() && !IsHuman) {
                Special_Weapon_AI(SPC_TD_PARA_INFANTRY);
            }
        }
    } else {
        // The airstrip flies them in; the Hand of Nod supplies the infantry.
        if (Has_Building_Active(STRUCT_TDAFLD) && Has_Building_Active(STRUCT_TDHAND)
            && Control.TechLevel >= Rule.ParaInfantryTechLevel) {
            SuperWeapon[SPC_TD_PARA_INFANTRY].Enable(false, this == PlayerPtr, false);
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_TD_PARA_INFANTRY, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_TD_PARA_INFANTRY);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }
}

/***********************************************************************************************
 * HouseClass::Attacked -- Lets player know if base is under attack.                           *
 *                                                                                             *
 *    Call this function whenever a building is attacked (with malice). This function will     *
 *    then announce to the player that his base is under attack. It checks to make sure that   *
 *    this is referring to the player's house rather than the enemy's.                         *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   12/27/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Attacked(BuildingClass* source)
{
    assert(Houses.ID(this) == ID);

#ifdef FIXIT_BASE_ANNOUNCE
    if (SpeakAttackDelay == 0
        && ((Session.Type == GAME_NORMAL && IsPlayerControl) || PlayerPtr->Class->House == Class->House)) {
#else
    if (SpeakAttackDelay == 0 && PlayerPtr->Class->House == Class->House) {
#endif
        if (Session.Type == GAME_NORMAL) {
            Speak(VOX_BASE_UNDER_ATTACK, NULL, source ? source->Center_Coord() : 0);
        } else {
            Speak(VOX_BASE_UNDER_ATTACK, this);
        }

        // MBL 06.13.2020 - Timing change from 2 minute cooldown, per https://jaas.ea.com/browse/TDRA-6784
        // SpeakAttackDelay = Options.Normalize_Delay(TICKS_PER_MINUTE * Rule.SpeakDelay); // 2 minutes
        // SpeakAttackDelay = Options.Normalize_Delay(TICKS_PER_MINUTE/2); // 30 seconds as requested
        SpeakAttackDelay =
            Options.Normalize_Delay((TICKS_PER_MINUTE / 2) + (TICKS_PER_SECOND * 5)); // Tweaked for accuracy

        /*
        **	If there is a trigger event associated with being attacked, process it
        **	now.
        */
        for (int index = 0; index < HouseTriggers[Class->House].Count(); index++) {
            HouseTriggers[Class->House][index]->Spring(TEVENT_ATTACKED);
        }
    }
}

/***********************************************************************************************
 * HouseClass::Harvested -- Adds Tiberium to the harvest storage.                              *
 *                                                                                             *
 *    Use this routine whenever Tiberium is harvested. The Tiberium is stored equally between  *
 *    all storage capable buildings for the house. Harvested Tiberium adds to the credit       *
 *    value of the house, but only up to the maximum storage capacity that the house can       *
 *    currently maintain.                                                                      *
 *                                                                                             *
 * INPUT:   tiberium -- The number of Tiberium credits to add to the House's total.            *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/25/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Harvested(unsigned tiberium)
{
    assert(Houses.ID(this) == ID);

    int oldtib = Tiberium;

    Tiberium += tiberium;
    if (Tiberium > Capacity) {
        Tiberium = Capacity;
        IsMaxedOut = true;
    }
    HarvestedCredits += tiberium;
    Silo_Redraw_Check(oldtib, Capacity);
}

/***********************************************************************************************
 * HouseClass::Stole -- Accounts for the value of a captured building.								  *
 *                                                                                             *
 *    Use this routine whenever a building is captured.  It keeps track of the cost of the     *
 *    building for use in the scoring routine, because you get an 'economy' boost for the      *
 *    value of the stolen building (but you don't get the credit value for it.)                *
 *                                                                                             *
 * INPUT:   worth -- The worth of the building we captured (stole).            					  *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/05/1996 BWG : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Stole(unsigned worth)
{
    assert(Houses.ID(this) == ID);

    StolenBuildingsCredits += worth;
}

/***********************************************************************************************
 * HouseClass::Available_Money -- Fetches the total credit worth of the house.                 *
 *                                                                                             *
 *    Use this routine to determine the total credit value of the house. This is the sum of    *
 *    the harvested Tiberium in storage and the initial unspent cash reserves.                 *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the total credit value of the house.                                  *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/25/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int HouseClass::Available_Money(void) const
{
    assert(Houses.ID(this) == ID);

    return (Tiberium + Credits);
}

/***********************************************************************************************
 * HouseClass::Spend_Money -- Removes money from the house.                                    *
 *                                                                                             *
 *    Use this routine to extract money from the house. Typically, this is a result of         *
 *    production spending. The money is extracted from available cash reserves first. When     *
 *    cash reserves are exhausted, then Tiberium is consumed.                                  *
 *                                                                                             *
 * INPUT:   money -- The amount of money to spend.                                             *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/25/1995 JLB : Created.                                                                 *
 *   06/20/1995 JLB : Spends Tiberium before spending cash.                                    *
 *=============================================================================================*/
void HouseClass::Spend_Money(unsigned money)
{
    assert(Houses.ID(this) == ID);

    int oldtib = Tiberium;
    if (money > (unsigned)Tiberium) {
        money -= (unsigned)Tiberium;
        Tiberium = 0;
        Credits -= money;
    } else {
        Tiberium -= money;
    }
    Silo_Redraw_Check(oldtib, Capacity);
    CreditsSpent += money;
}

/***********************************************************************************************
 * HouseClass::Refund_Money -- Refunds money to back to the house.                             *
 *                                                                                             *
 *    Use this routine when money needs to be refunded back to the house. This can occur when  *
 *    construction is aborted. At this point, the exact breakdown of Tiberium or initial       *
 *    credits used for the orignal purchase is lost. Presume as much of the money is in the    *
 *    form of Tiberium as storage capacity will allow.                                         *
 *                                                                                             *
 * INPUT:   money -- The number of credits to refund back to the house.                        *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/25/1995 JLB : Created.                                                                 *
 *   06/01/1995 JLB : Refunded money is never lost                                             *
 *=============================================================================================*/
void HouseClass::Refund_Money(unsigned money)
{
    assert(Houses.ID(this) == ID);

    Credits += money;
}

/***********************************************************************************************
 * HouseClass::Adjust_Capacity -- Adjusts the house Tiberium storage capacity.                 *
 *                                                                                             *
 *    Use this routine to adjust the maximum storage capacity for the house. This storage      *
 *    capacity will limit the number of Tiberium credits that can be stored at any one time.   *
 *                                                                                             *
 * INPUT:   adjust   -- The adjustment to the Tiberium storage capacity.                       *
 *                                                                                             *
 *          inanger  -- Is this a forced adjustment to capacity due to some hostile event?     *
 *                                                                                             *
 * OUTPUT:  Returns with the number of Tiberium credits lost.                                  *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   01/25/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int HouseClass::Adjust_Capacity(int adjust, bool inanger)
{
    assert(Houses.ID(this) == ID);

    int oldcap = Capacity;
    int retval = 0;

    Capacity += adjust;
    Capacity = max(Capacity, 0L);
    if (Tiberium > Capacity) {
        retval = Tiberium - Capacity;
        Tiberium = Capacity;
        if (!inanger) {
            Refund_Money(retval);
            retval = 0;
        } else {
            IsMaxedOut = true;
        }
    }
    Silo_Redraw_Check(Tiberium, oldcap);
    return (retval);
}

/***********************************************************************************************
 * HouseClass::Silo_Redraw_Check -- Flags silos to be redrawn if necessary.                    *
 *                                                                                             *
 *    Call this routine when either the capacity or tiberium levels change for a house. This   *
 *    routine will determine if the aggregate tiberium storage level will result in the        *
 *    silos changing their imagery. If this is detected, then all the silos for this house     *
 *    are flagged to be redrawn.                                                               *
 *                                                                                             *
 * INPUT:   oldtib   -- Pre-change tiberium level.                                             *
 *                                                                                             *
 *          oldcap   -- Pre-change tiberium storage capacity.                                  *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   02/02/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Silo_Redraw_Check(int oldtib, int oldcap)
{
    assert(Houses.ID(this) == ID);

    int oldratio = 0;
    if (oldcap)
        oldratio = (oldtib * 5) / oldcap;
    int newratio = 0;
    if (Capacity)
        newratio = (Tiberium * 5) / Capacity;

    if (oldratio != newratio) {
        for (int index = 0; index < Buildings.Count(); index++) {
            BuildingClass* b = Buildings.Ptr(index);
            if (b && !b->IsInLimbo && b->House == this && *b == STRUCT_STORAGE) {
                b->Mark(MARK_CHANGE);
            }
        }
    }
}

/***********************************************************************************************
 * HouseClass::Is_Ally -- Determines if the specified house is an ally.                        *
 *                                                                                             *
 *    This routine will determine if the house number specified is a ally to this house.       *
 *                                                                                             *
 * INPUT:   house -- The house number to check to see if it is an ally.                        *
 *                                                                                             *
 * OUTPUT:  Is the house an ally?                                                              *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Is_Ally(HousesType house) const
{
    assert(Houses.ID(this) == ID);

    if (house != HOUSE_NONE) {
        return (((1 << house) & Allies) != 0);
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::Is_Ally -- Determines if the specified house is an ally.                        *
 *                                                                                             *
 *    This routine will examine the specified house and determine if it is an ally.            *
 *                                                                                             *
 * INPUT:   house -- Pointer to the house object to check for ally relationship.               *
 *                                                                                             *
 * OUTPUT:  Is the specified house an ally?                                                    *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Is_Ally(HouseClass const* house) const
{
    assert(Houses.ID(this) == ID);

    if (house) {
        return (Is_Ally(house->Class->House));
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::Is_Ally -- Checks to see if the object is an ally.                              *
 *                                                                                             *
 *    This routine will examine the specified object and return whether it is an ally or not.  *
 *                                                                                             *
 * INPUT:   object   -- The object to examine to see if it is an ally.                         *
 *                                                                                             *
 * OUTPUT:  Is the specified object an ally?                                                   *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Is_Ally(ObjectClass const* object) const
{
    assert(Houses.ID(this) == ID);

    if (object) {
        return (Is_Ally(object->Owner()));
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::Make_Ally -- Make the specified house an ally.                                  *
 *                                                                                             *
 *    This routine will make the specified house an ally to this house. An allied house will   *
 *    not be considered a threat or potential target.                                          *
 *                                                                                             *
 * INPUT:   house -- The house to make an ally of this house.                                  *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *   08/08/1995 JLB : Breaks off combat when ally commences.                                   *
 *   10/17/1995 JLB : Added reveal base when allied.                                           *
 *=============================================================================================*/
void HouseClass::Make_Ally(HousesType house)
{
    assert(Houses.ID(this) == ID);

    if (Is_Allowed_To_Ally(house)) {

        Allies |= (1L << house);

        /*
        **	Don't consider the newfound ally to be an enemy -- of course.
        */
        if (Enemy == house) {
            Enemy = HOUSE_NONE;
        }

        if (ScenarioInit) {
            Control.Allies |= (1L << house);
        }

        if (Session.Type != GAME_NORMAL && !ScenarioInit) {
            HouseClass* hptr = HouseClass::As_Pointer(house);

            /*
            **	An alliance with another human player will cause the computer
            **	players (if present) to become paranoid.
            */
            if (hptr != NULL && IsHuman && Rule.IsComputerParanoid) {
                //			if (hptr != NULL && hptr->IsHuman) {
                //				if (!hptr->IsHuman) {
                //					hptr->Make_Ally(Class->House);
                //				}
                Computer_Paranoid();
            }

            char buffer[80];

            /*
            **	Sweep through all techno objects and perform a cheeseball tarcom clear to ensure
            **	that fighting will most likely stop when the cease fire begins.
            */
            for (int index = 0; index < Logic.Count(); index++) {
                ObjectClass* object = Logic[index];

                if (object != NULL && object->Is_Techno() && !object->IsInLimbo && object->Owner() == Class->House) {
                    TARGET target = ((TechnoClass*)object)->TarCom;
                    if (Target_Legal(target) && As_Techno(target) != NULL) {
                        if (Is_Ally(As_Techno(target))) {
                            ((TechnoClass*)object)->Assign_Target(TARGET_NONE);
                        }
                    }
                }
            }

            /*
            **	Cause all structures to be revealed to the house that has been
            **	allied with.
            */
            if (Rule.IsAllyReveal && house == PlayerPtr->Class->House) {
                for (int index = 0; index < Buildings.Count(); index++) {
                    BuildingClass const* b = Buildings.Ptr(index);

                    if (b && !b->IsInLimbo && (HouseClass*)b->House == this) {
                        Map.Sight_From(Coord_Cell(b->Center_Coord()), b->Class->SightRange, PlayerPtr, false);
                    }
                }
            }

            if (IsHuman) {
                sprintf(buffer, Text_String(TXT_HAS_ALLIED), IniName, HouseClass::As_Pointer(house)->IniName);
                //				sprintf(buffer, Text_String(TXT_HAS_ALLIED), Session.Players[Class->House -
                //HOUSE_MULTI1]->Name, Session.Players[((HouseClass::As_Pointer(house))->Class->House) -
                //HOUSE_MULTI1]->Name);
                Session.Messages.Add_Message(NULL,
                                             0,
                                             buffer,
                                             RemapColor,
                                             TPF_6PT_GRAD | TPF_USE_GRAD_PAL | TPF_FULLSHADOW,
                                             TICKS_PER_MINUTE * Rule.MessageDelay);
            }

            Map.Flag_To_Redraw(false);
        }
    }
}

/***********************************************************************************************
 * HouseClass::Make_Enemy -- Make an enemy of the house specified.                             *
 *                                                                                             *
 *    This routine will flag the house specified so that it will be an enemy to this house.    *
 *    Enemy houses are legal targets for attack.                                               *
 *                                                                                             *
 * INPUT:   house -- The house to make an enemy of this house.                                 *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *   07/27/1995 JLB : Making war is a bilateral action.                                        *
 *=============================================================================================*/
void HouseClass::Make_Enemy(HousesType house)
{
    assert(Houses.ID(this) == ID);

    if (house != HOUSE_NONE && Is_Ally(house)) {
        HouseClass* enemy = HouseClass::As_Pointer(house);
        Allies &= ~(1L << house);

        if (ScenarioInit) {
            Control.Allies &= !(1L << house);
        }

        /*
        **	Breaking an alliance is a bilateral event.
        */
        if (enemy != NULL && enemy->Is_Ally(this)) {
            enemy->Allies &= ~(1L << Class->House);

            if (ScenarioInit) {
                Control.Allies &= ~(1L << Class->House);
            }
        }

        if ((Debug_Flag || Session.Type != GAME_NORMAL) && !ScenarioInit && IsHuman) {
            char buffer[80];

            sprintf(buffer, Text_String(TXT_AT_WAR), IniName, HouseClass::As_Pointer(house)->IniName);
            //			sprintf(buffer, Text_String(TXT_AT_WAR), Session.Players[Class->House - HOUSE_MULTI1]->Name,
            //Session.Players[enemy->Class->House - HOUSE_MULTI1]->Name);
            Session.Messages.Add_Message(NULL,
                                         0,
                                         buffer,
                                         RemapColor,
                                         TPF_6PT_GRAD | TPF_USE_GRAD_PAL | TPF_FULLSHADOW,
                                         TICKS_PER_MINUTE * Rule.MessageDelay);
            Map.Flag_To_Redraw(false);
        }
    }
}

/***********************************************************************************************
 * HouseClass::Remap_Table -- Fetches the remap table for this house object.                   *
 *                                                                                             *
 *    This routine will return with the remap table to use when displaying an object owned     *
 *    by this house. If the object is blushing (flashing), then the lightening remap table is  *
 *    always used. The "unit" parameter allows proper remap selection for those houses that    *
 *    have a different remap table for buildings or units.                                     *
 *                                                                                             *
 * INPUT:   blushing -- Is the object blushing (flashing)?                                     *
 *                                                                                             *
 *          remap    -- The remap control value to use.                                        *
 *                      REMAP_NONE     No remap pointer returned at all.                       *
 *                      REMAP_NORMAL   Return the remap pointer for this house.                *
 *                      REMAP_ALTERNATE   (Nod solo play only -- forces red remap).            *
 *                                        Multiplay returns same as REMAP_NORMAL               *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the remap table to use when drawing this object.         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *   10/25/1995 JLB : Uses remap control value.                                                *
 *=============================================================================================*/
unsigned char const* HouseClass::Remap_Table(bool blushing, RemapType remap) const
{
    assert(Houses.ID(this) == ID);

    if (blushing)
        return (&Map.FadingLight[0]);

    if (remap == REMAP_NONE)
        return (0);

    return (ColorRemaps[RemapColor].RemapTable);
}

/***********************************************************************************************
 * HouseClass::Suggested_New_Team -- Determine what team should be created.                    *
 *                                                                                             *
 *    This routine examines the house condition and returns with the team that it thinks       *
 *    should be created. The units that are not currently a member of a team are examined      *
 *    to determine the team needed.                                                            *
 *                                                                                             *
 * INPUT:   alertcheck  -- Select from the auto-create team list.                              *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the team type that should be created. If no team should  *
 *          be created, then NULL is returned.                                                 *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
TeamTypeClass const* HouseClass::Suggested_New_Team(bool alertcheck)
{
    assert(Houses.ID(this) == ID);

    return (TeamTypeClass::Suggested_New_Team(this, AScan, UScan, IScan, VScan, alertcheck));
}

/***********************************************************************************************
 * HouseClass::Adjust_Threat -- Adjust threat for the region specified.                        *
 *                                                                                             *
 *    This routine is called when the threat rating for a region needs to change. The region   *
 *    and threat adjustment are provided.                                                      *
 *                                                                                             *
 * INPUT:   region   -- The region that adjustment is to occur on.                             *
 *                                                                                             *
 *          threat   -- The threat adjustment to perform.                                      *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Adjust_Threat(int region, int threat)
{
    assert(Houses.ID(this) == ID);

    static int _val[] = {-MAP_REGION_WIDTH - 1,
                         -MAP_REGION_WIDTH,
                         -MAP_REGION_WIDTH + 1,
                         -1,
                         0,
                         1,
                         MAP_REGION_WIDTH - 1,
                         MAP_REGION_WIDTH,
                         MAP_REGION_WIDTH + 1};
    static int _thr[] = {2, 1, 2, 1, 0, 1, 2, 1, 2};
    int neg;
    int* val = &_val[0];
    int* thr = &_thr[0];

    if (threat < 0) {
        threat = -threat;
        neg = true;
    } else {
        neg = false;
    }

    for (int lp = 0; lp < 9; lp++) {
        Regions[region + *val].Adjust_Threat(threat >> *thr, neg);
        val++;
        thr++;
    }
}

/***********************************************************************************************
 * HouseClass::Begin_Production -- Starts production of the specified object type.             *
 *                                                                                             *
 *    This routine is called from the event system. It will start production for the object    *
 *    type specified. This will be reflected in the sidebar as well as the house factory       *
 *    tracking variables.                                                                      *
 *                                                                                             *
 * INPUT:   type  -- The type of object to begin production on.                                *
 *                                                                                             *
 *          id    -- The subtype of object.                                                    *
 *                                                                                             *
 * OUTPUT:  Returns with the reason why, or why not, production was started.                   *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *   10/21/1996 JLB : Handles max object case.                                                 *
 *=============================================================================================*/
ProdFailType HouseClass::Begin_Production(RTTIType type, int id)
{
    assert(Houses.ID(this) == ID);
    int result = true;
    bool initial_start = false;
    FactoryClass* fptr;
    TechnoTypeClass const* tech = Fetch_Techno_Type(type, id);

    fptr = Fetch_Factory(type);

    /*
    **	If the house is already busy producing the requested object, then
    **	return with this failure code, unless we are restarting production.
    */
    if (fptr != NULL) {
        if (fptr->Is_Building()) {
            return (PROD_CANT);
        }
    } else {
        fptr = new FactoryClass();
        if (!fptr)
            return (PROD_CANT);
        Set_Factory(type, fptr);
        result = fptr->Set(*tech, *this);
        initial_start = true;

        /*
        ** If set failed, we probably reached the production cap. Don't let the factory linger, preventing further
        *production attempts.
        ** ST - 3/17/2020 2:03PM
        */
        if (!result) {
            Set_Factory(type, NULL);
            delete fptr;
            fptr = NULL;
        }
    }

    if (result) {
        fptr->Start();

        /*
        **	Link this factory to the sidebar so that proper graphic feedback
        **	can take place.
        */
        // Handle Glyphx multiplayer sidebar. ST - 8/14/2019 1:26PM
        if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
            if (IsHuman) {
#ifdef REMASTER_BUILD
                Sidebar_Glyphx_Factory_Link(fptr->ID, type, id, this);
#endif
            }
        } else {
            if (PlayerPtr == this) {
                Map.Factory_Link(fptr->ID, type, id);
            }
        }

        return (PROD_OK);
    }

    delete fptr;
    return (PROD_CANT);
}

/***********************************************************************************************
 * HouseClass::Suspend_Production -- Temporarily puts production on hold.                      *
 *                                                                                             *
 *    This routine is called from the event system whenever the production of the specified    *
 *    type needs to be suspended. The suspended production will be reflected in the sidebar    *
 *    as well as in the house control structure.                                               *
 *                                                                                             *
 * INPUT:   type  -- The type of object that production is being suspended for.                *
 *                                                                                             *
 * OUTPUT:  Returns why, or why not, production was suspended.                                 *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
ProdFailType HouseClass::Suspend_Production(RTTIType type)
{
    assert(Houses.ID(this) == ID);

    FactoryClass* fptr = Fetch_Factory(type);

    /*
    **	If the house is already busy producing the requested object, then
    **	return with this failure code.
    */
    if (fptr == NULL)
        return (PROD_CANT);

    /*
    **	Actually suspend the production.
    */
    fptr->Suspend();

    /*
    **	Tell the sidebar that it needs to be redrawn because of this.
    */
    if (PlayerPtr == this) {
        Map.SidebarClass::IsToRedraw = true;
        if (!RunningAsDLL) { // Don't force a redraw when running under GlyphX. PlayerPtr==this will always be true in
                             // this case, and we don't want to force a redraw even for AI players
            Map.Flag_To_Redraw(false);
        }
    }

    return (PROD_OK);
}

/***********************************************************************************************
 * HouseClass::Abandon_Production -- Abandons production of item type specified.               *
 *                                                                                             *
 *    This routine is called from the event system whenever production must be abandoned for   *
 *    the type specified. This will remove the factory and pending object from the sidebar as  *
 *    well as from the house factory record.                                                   *
 *                                                                                             *
 * INPUT:   type  -- The object type that production is being suspended for.                   *
 *                                                                                             *
 * OUTPUT:  Returns the reason why or why not, production was suspended.                       *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/08/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
ProdFailType HouseClass::Abandon_Production(RTTIType type)
{
    assert(Houses.ID(this) == ID);

    FactoryClass* fptr = Fetch_Factory(type);

    /*
    **	If there is no factory to abandon, then return with a failure code.
    */
    if (fptr == NULL)
        return (PROD_CANT);

    /*
    **	Tell the sidebar that it needs to be redrawn because of this.
    */
    // Handle Glyphx multiplayer sidebar. ST - 8/7/2019 10:18AM
    if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
        if (IsHuman) {
#ifdef REMASTER_BUILD
            Sidebar_Glyphx_Abandon_Production(type, fptr->ID, this);
#endif
            // Need to clear pending object here if legacy renderer enabled

            if (type == RTTI_BUILDINGTYPE || type == RTTI_BUILDING && Map.PendingObjectPtr) {
                Map.PendingObjectPtr = 0;
                Map.PendingObject = 0;
                Map.PendingHouse = HOUSE_NONE;
                Map.Set_Cursor_Shape(0);
            }
        }
    } else {
        if (PlayerPtr == this) {
            Map.Abandon_Production(type, fptr->ID);

            if (type == RTTI_BUILDINGTYPE || type == RTTI_BUILDING) {
                Map.PendingObjectPtr = 0;
                Map.PendingObject = 0;
                Map.PendingHouse = HOUSE_NONE;
                Map.Set_Cursor_Shape(0);
            }
        }
    }

    /*
    **	Abandon production of the object.
    */
    fptr->Abandon();
    Set_Factory(type, NULL);
    delete fptr;

    return (PROD_OK);
}

/***********************************************************************************************
 * HouseClass::Special_Weapon_AI -- Fires special weapon.                                      *
 *                                                                                             *
 *    This routine will pick a good target to fire the special weapon specified.               *
 *                                                                                             *
 * INPUT:   id -- The special weapon id to fire.                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/24/1995 PWG : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Special_Weapon_AI(SpecialWeaponType id)
{
    assert(Houses.ID(this) == ID);

    /*
    ** Loop through all of the building objects on the map
    ** and see which ones are available.
    */
    BuildingClass* bestptr = NULL;
    int best = -1;

    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass* b = Buildings.Ptr(index);

        /*
        ** If the building is valid, not in limbo, not in the process of
        ** being destroyed and not our ally, then we can consider it.
        */
        if (b != NULL && !b->IsInLimbo && b->Strength && !Is_Ally(b)) {

            /*
            **	Fair-fog superweapon aiming: a computer house may only aim at buildings
            **	its own house has discovered. Once seen a building stays in the mask,
            **	so striking where a discovered structure was is remembered intel, not
            **	an omniscience cheat.
            */
            if (!IsHuman && Session.Type != GAME_NORMAL && !b->Is_Discovered_By_Player(this)) {
                continue;
            }

            /*
            **	A cloaked building displaces superweapon fire the same way it
            **	displaces direct fire: only what the firing house can currently
            **	see may be struck. Discovery is sticky by design (intel memory);
            **	the cloak is the live veil over it -- a stealth-generator field
            **	protects exactly until a detector or shimmer breaks the cloak.
            */
            if (b->Is_Cloaked(this)) {
                continue;
            }

            if (Percent_Chance(90) && (b->Value() > best || best == -1)) {
                best = b->Value();
                bestptr = b;
            }
        }
    }

    if (bestptr) {
        CELL cell = Coord_Cell(bestptr->Center_Coord());
        Place_Special_Blast(id, cell);
    } else if (id == SPC_SPY_MISSION || id == SPC_TD_SPY_MISSION) {
        /*
        **	Recon powers exist to find the enemy, so a house with nothing
        **	discovered fires them at unexplored start positions -- the same
        **	rotation its blind ground scouts walk -- rather than never firing.
        **	The shared rotation also stamps the probed point, so plane and
        **	scouts naturally divide the map. Destructive specials stay
        **	discovered-targets-only.
        */
        CELL cell = TF_Scout_Destination(Coord_Cell(Center));
        if (cell > 0) {
            Place_Special_Blast(id, cell);
        }
    }
}

/***********************************************************************************************
 * HouseClass::TF_Knows_Any_Enemy_Building -- Has this house discovered any enemy structure?   *
 *                                                                                             *
 *    Feeds the scout-intensity tiers: an Easy computer house stops probing the map once it    *
 *    has found something to fight; higher tiers keep probing whenever they are blind.         *
 *=============================================================================================*/
bool HouseClass::TF_Knows_Any_Enemy_Building(void)
{
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass const* b = Buildings.Ptr(index);
        if (b != NULL && !b->IsInLimbo && b->Strength > 0 && !Is_Ally(b) && b->House->Class->House != HOUSE_NEUTRAL
            && b->Is_Discovered_By_Player(this)) {
            return (true);
        }
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::TF_Scout_Destination -- Pick a map spot worth exploring while hunting blind.    *
 *                                                                                             *
 *    Multiplayer start locations are public map knowledge (any human reads them off the       *
 *    lobby preview), so probing them is fair intel gathering rather than a cheat. Start       *
 *    points this house has not yet mapped are preferred, nearest first; once everything is    *
 *    mapped the nearest start point away from home is re-probed so a blind house keeps        *
 *    looking rather than standing down.                                                       *
 *                                                                                             *
 * INPUT:   from -- The cell the scouting unit currently occupies.                             *
 *                                                                                             *
 * OUTPUT:  Destination cell, or -1 when there is nothing sensible to probe.                   *
 *=============================================================================================*/
CELL HouseClass::TF_Scout_Destination(CELL from)
{
    /*
    **	Start points closer to home than this are considered our own corner of
    **	the map and are not worth probing.
    */
    const int TF_HOME_RADIUS_LEPTONS = CELL_LEPTON_W * 12;

    /*
    **	The frame each start point was last handed to one of this house's scouts.
    **	Every pick stamps its waypoint and later picks prefer the least-recently
    **	probed one, so scouts dispatched together fan out over the start points
    **	instead of all computing the same nearest cell. Distance only breaks
    **	ties. Kept outside the class so the savegame layout is untouched; a
    **	stamp from a previous match reads as newer than the young frame counter
    **	and is treated as never-probed.
    */
    static long _probed[HOUSE_COUNT][26];

    CELL best_unmapped = -1;
    int best_unmapped_dist = -1;
    long best_unmapped_probed = 0;
    int best_unmapped_index = -1;
    CELL best_any = -1;
    int best_any_dist = -1;
    long best_any_probed = 0;
    int best_any_index = -1;

    for (int index = 0; index < 26; index++) {
        CELL waypt = Scen.Waypoint[index];
        if (waypt <= 0 || (unsigned)waypt >= MAP_CELL_TOTAL) {
            continue;
        }
        COORDINATE wcoord = Cell_Coord(waypt);
        if (Center != 0 && ::Distance(wcoord, Center) < TF_HOME_RADIUS_LEPTONS) {
            continue;
        }
        int dist = ::Distance(Cell_Coord(from), wcoord);
        long probed = _probed[Class->House][index];
        if (probed > (long)Frame) {
            probed = 0;
        }
        if (!Map[waypt].Is_Mapped(this)) {
            if (best_unmapped == -1 || probed < best_unmapped_probed
                || (probed == best_unmapped_probed && dist < best_unmapped_dist)) {
                best_unmapped = waypt;
                best_unmapped_dist = dist;
                best_unmapped_probed = probed;
                best_unmapped_index = index;
            }
        }
        if (best_any == -1 || probed < best_any_probed || (probed == best_any_probed && dist < best_any_dist)) {
            best_any = waypt;
            best_any_dist = dist;
            best_any_probed = probed;
            best_any_index = index;
        }
    }

    int chosen = (best_unmapped != -1) ? best_unmapped_index : best_any_index;
    if (chosen != -1) {
        _probed[Class->House][chosen] = (long)Frame;
    }
    return (best_unmapped != -1) ? best_unmapped : best_any;
}

/***********************************************************************************************
 * HouseClass::Place_Special_Blast -- Place a special blast effect at location specified.      *
 *                                                                                             *
 *    This routine will create a blast effect at the cell specified. This is the result of     *
 *    the special weapons.                                                                     *
 *                                                                                             *
 * INPUT:   id    -- The special weapon id number.                                             *
 *                                                                                             *
 *          cell  -- The location where the special weapon attack is to occur.                 *
 *                                                                                             *
 * OUTPUT:  Was the special weapon successfully fired at the location specified?               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/18/1995 JLB : commented.                                                               *
 *   07/25/1995 JLB : Added scatter effect for nuclear bomb.                                   *
 *   07/28/1995 JLB : Revamped to use super weapon class controller.                           *
 *=============================================================================================*/
extern void Logic_Switch_Player_Context(ObjectClass* object);
extern void Logic_Switch_Player_Context(HouseClass* object);
extern void On_Special_Weapon_Targetting(const HouseClass* player_ptr, SpecialWeaponType weapon_type);

bool HouseClass::Place_Special_Blast(SpecialWeaponType id, CELL cell)
{
    assert(Houses.ID(this) == ID);

    // Added. ST - 12/2/2019 11:26AM
    bool fired = false;
    const char* what = NULL;

    BuildingClass* launchsite = 0;
    AnimClass* anim = 0;
    switch (id) {
    case SPC_SONAR_PULSE:
        // Automatically discharge the sonar pulse and uncloak all subs.
        if (SuperWeapon[SPC_SONAR_PULSE].Is_Ready()) {
            SuperWeapon[SPC_SONAR_PULSE].Discharged(this == PlayerPtr);
            if (this == PlayerPtr) {
                Map.Column[1].Flag_To_Redraw();
                Map.Activate_Pulse();
            }
            Sound_Effect(VOC_SONAR);
            IsRecalcNeeded = true;
            fired = true;
            what = "SONAR";
            for (int index = 0; index < Vessels.Count(); index++) {
                VesselClass* sub = Vessels.Ptr(index);
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
                if (*sub == VESSEL_SS || *sub == VESSEL_MISSILESUB) {
#else
                if (*sub == VESSEL_SS) {
#endif
                    sub->PulseCountDown = 15 * TICKS_PER_SECOND;
                    sub->Do_Uncloak();
                }
            }
        }
        break;

    /*
    **  Tiberian Factions mod — GDI Ion Cannon discharge. Spawns
    **  ANIM_TD_ION_CANNON directly at the targeted cell. The anim's
    **  Middle() callback (anim.cpp) handles the 600 / WARHEAD_TDPB
    **  Explosion_Damage at impact. No launch site / missile flight stage
    **  — TD's Ion Cannon strikes instantly from orbit.
    */
    case SPC_TD_ION_CANNON:
        if (SuperWeapon[SPC_TD_ION_CANNON].Is_Ready()) {
            AnimClass* ion_anim = new AnimClass(ANIM_TD_ION_CANNON, Cell_Coord(cell), 0, 1);
            if (ion_anim != NULL) {
                ion_anim->Set_Owner(Class->House);
            }
            SuperWeapon[SPC_TD_ION_CANNON].Discharged(this == PlayerPtr);
            IsRecalcNeeded = true;
            fired = true;
            what = "ION_CANNON";
            if (this == PlayerPtr) {
                Map.Column[1].Flag_To_Redraw();
                Map.IsTargettingMode = SPC_NONE;
            }
        }
        break;

    /*
    **  Tiberian Factions mod — Nod Nuclear Strike discharge. Finds the
    **  firing house's TDTMPL, assigns it MISSION_MISSILE, and stashes the
    **  target on House->NukeDest. The TDTMPL-specific branch in
    **  BuildingClass::Mission_Missile drives the 5-frame BSTATE_ACTIVE
    **  launch anim, spawns BULLET_NUKE_DOWN over the target, and plays
    **  VOX_TD_NUKE_LAUNCHED. Mirrors RA's nuke launchsite pattern but with
    **  the Temple's TD-authentic single-cycle launch (vs MSLO's 4-state
    **  door open / hold / close machine).
    */
    case SPC_TD_NUKE:
        if (SuperWeapon[SPC_TD_NUKE].Is_Ready()) {
            launchsite = Find_Building(STRUCT_TDTMPL);
            if (launchsite) {
                launchsite->Assign_Mission(MISSION_MISSILE);
                launchsite->Commence();
                NukeDest = cell;
            }
            if (this == PlayerPtr) {
                Map.IsTargettingMode = SPC_NONE;
            }
            SuperWeapon[SPC_TD_NUKE].Discharged(this == PlayerPtr);
            IsRecalcNeeded = true;
            fired = true;
            what = "TD_NUKE";
            if (this == PlayerPtr) {
                Map.Column[1].Flag_To_Redraw();
            }
        }
        break;

    case SPC_NUCLEAR_BOMB:
        if (SuperWeapon[SPC_NUCLEAR_BOMB].Is_Ready()) {
            if (SuperWeapon[SPC_NUCLEAR_BOMB].Is_One_Time()) {
                BulletClass* bullet =
                    new BulletClass(BULLET_NUKE_DOWN, ::As_Target(cell), 0, 200, WARHEAD_NUKE, MPH_VERY_FAST);
                if (bullet) {
                    int celly = Cell_Y(cell);
                    celly -= 15;
                    if (celly < 1)
                        celly = 1;
                    COORDINATE start = Cell_Coord(XY_Cell(Cell_X(cell), celly));
                    if (!bullet->Unlimbo(start, DIR_S)) {
                        delete bullet;
                    }
                    SuperWeapon[SPC_NUCLEAR_BOMB].Discharged(this == PlayerPtr);
                    IsRecalcNeeded = true;
                    fired = true;
                    what = "NUKE";
                    if (this == PlayerPtr) {
                        Map.Column[1].Flag_To_Redraw();
                        Map.IsTargettingMode = SPC_NONE;
                    }
                }
            } else {

                /*
                **	Search for a suitable launch site for this missile.
                */
                launchsite = Find_Building(STRUCT_MSLO);

                /*
                **	If a launch site was found, then proceed with the normal launch
                **	sequence.
                */
                if (launchsite) {
                    launchsite->Assign_Mission(MISSION_MISSILE);
                    launchsite->Commence();
                    NukeDest = cell;
                }
                if (this == PlayerPtr) {
                    Map.IsTargettingMode = SPC_NONE;
                }
                SuperWeapon[SPC_NUCLEAR_BOMB].Discharged(this == PlayerPtr);
                IsRecalcNeeded = true;
                fired = true;
                what = "NUKE";
            }
        }
        break;

    case SPC_PARA_INFANTRY:
    case SPC_TD_PARA_INFANTRY:
        if (SuperWeapon[id].Is_Ready()) {

            TeamTypeClass* ttype = TeamTypeClass::As_Pointer("@PINF");
            if (ttype == NULL) {
                ttype = new TeamTypeClass;
                if (ttype != NULL) {
                    strcpy(ttype->IniName, "@PINF");
                    ttype->IsTransient = true;
                    ttype->IsPrebuilt = false;
                    ttype->IsReinforcable = false;
                    ttype->Origin = WAYPT_SPECIAL;
                    ttype->MissionCount = 1;
                    ttype->MissionList[0].Mission = TMISSION_ATT_WAYPT;
                    ttype->MissionList[0].Data.Value = WAYPT_SPECIAL;
                    ttype->ClassCount = 2;
                    ttype->Members[0].Quantity = AircraftTypeClass::As_Reference(AIRCRAFT_BADGER).Max_Passengers();
                    ttype->Members[0].Class = &InfantryTypeClass::As_Reference(INFANTRY_E1);
                    ttype->Members[1].Quantity = 1;
                    ttype->Members[1].Class = &AircraftTypeClass::As_Reference(AIRCRAFT_BADGER);
                }
            }

            if (ttype != NULL) {
                ttype->House = Class->House;
                // Which special fired decides the delivery, not house identity, so a
                // captured cross-era pair drops that era's troops: the TD special drops
                // Minigunners (TDE1) from the targetable TD C-17 (TDC17P), the RA one
                // Rifle Infantry (E1) from the Badger. Set every fire -- the @PINF team
                // is cached and shared. Squad size = the plane's passenger capacity.
                bool td = (id == SPC_TD_PARA_INFANTRY);
                AircraftType para_plane = td ? AIRCRAFT_TDPARADROP : AIRCRAFT_BADGER;
                ttype->Members[0].Class = &InfantryTypeClass::As_Reference(td ? INFANTRY_TDE1 : INFANTRY_E1);
                ttype->Members[0].Quantity = AircraftTypeClass::As_Reference(para_plane).Max_Passengers();
                ttype->Members[1].Class = &AircraftTypeClass::As_Reference(para_plane);
                Scen.Waypoint[WAYPT_SPECIAL] = Map.Nearby_Location(cell, SPEED_FOOT);
                Do_Reinforcements(ttype);
            }

            if (this == PlayerPtr) {
                Map.IsTargettingMode = SPC_NONE;
            }
            SuperWeapon[id].Discharged(this == PlayerPtr);
            IsRecalcNeeded = true;
            fired = true;
            what = (id == SPC_TD_PARA_INFANTRY) ? "TDPARA" : "PARA";
        }
        break;

    // Both eras' recon flights fly the same U2 flyover (TD has no recon plane to
    // port); the split exists so each airstrip's special has its own timer and badge.
    case SPC_SPY_MISSION:
    case SPC_TD_SPY_MISSION:
        if (SuperWeapon[id].Is_Ready()) {
            Create_Air_Reinforcement(this, AIRCRAFT_U2, 1, MISSION_HUNT, ::As_Target(cell), ::As_Target(cell));
            if (this == PlayerPtr) {
                Map.IsTargettingMode = SPC_NONE;
            }
            SuperWeapon[id].Discharged(this == PlayerPtr);
            IsRecalcNeeded = true;
            fired = true;
            what = "SPY";
        }
        break;

    case SPC_PARA_BOMB:
        if (SuperWeapon[SPC_PARA_BOMB].Is_Ready()) {
            Create_Air_Reinforcement(
                this, AIRCRAFT_BADGER, Rule.BadgerBombCount, MISSION_HUNT, ::As_Target(cell), TARGET_NONE);
            if (this == PlayerPtr) {
                Map.IsTargettingMode = SPC_NONE;
            }
            SuperWeapon[SPC_PARA_BOMB].Discharged(this == PlayerPtr);
            IsRecalcNeeded = true;
            fired = true;
            what = "PARABOMB";
        }
        break;

    case SPC_IRON_CURTAIN:
        if (SuperWeapon[SPC_IRON_CURTAIN].Is_Ready()) {
            int x = Keyboard->MouseQX - Map.TacPixelX;
            int y = Keyboard->MouseQY - Map.TacPixelY;
            TechnoClass* tech = Map[cell].Cell_Techno(x, y);
            if (tech) {
                switch (tech->What_Am_I()) {
                case RTTI_UNIT:
                case RTTI_BUILDING:
                case RTTI_VESSEL:
                case RTTI_AIRCRAFT:
                    tech->IronCurtainCountDown = Rule.IronCurtainDuration * TICKS_PER_MINUTE;
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
                    if (tech->What_Am_I() == RTTI_UNIT && *(UnitClass*)tech == UNIT_DEMOTRUCK) {
                        tech->IronCurtainCountDown = Rule.IronCurtainDuration * TICKS_PER_SECOND;
                    }
#endif
                    tech->Mark(MARK_CHANGE);
                    Sound_Effect(VOC_IRON1, tech->Center_Coord());
                    if (this == PlayerPtr) {
                        Map.IsTargettingMode = SPC_NONE;
                    }
                    SuperWeapon[SPC_IRON_CURTAIN].Discharged(this == PlayerPtr);
                    break;
                default:
                    break;
                }
            }

            IsRecalcNeeded = true;
            fired = true;
            what = "IRON";
        }
        break;

    case SPC_CHRONOSPHERE:
        if (SuperWeapon[SPC_CHRONOSPHERE].Is_Ready()) {
            int x = Keyboard->MouseQX - Map.TacPixelX;
            int y = Keyboard->MouseQY - Map.TacPixelY;
            TechnoClass* tech = Map[cell].Cell_Techno(x, y);
            if (tech && Is_Ally(tech)) {
                if (tech->What_Am_I() == RTTI_UNIT || tech->What_Am_I() == RTTI_INFANTRY ||
#ifdef FIXIT_CARRIER //	checked - ajw 9/28/98
                    (tech->What_Am_I() == RTTI_VESSEL
                     && (*((VesselClass*)tech) != VESSEL_TRANSPORT && *((VesselClass*)tech) != VESSEL_CARRIER))) {
#else
                    (tech->What_Am_I() == RTTI_VESSEL && *((VesselClass*)tech) != VESSEL_TRANSPORT)) {
#endif

                    if (tech->What_Am_I() != RTTI_UNIT || !((UnitClass*)tech)->IsDeploying) {
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
                        bool porthim = true;
                        if (tech->What_Am_I() == RTTI_UNIT && ((UnitClass*)tech)->Class->Type == UNIT_CHRONOTANK) {
                            porthim = false;
                        }
                        if (porthim) {
#endif
#ifdef REMASTER_BUILD
                            HouseClass* old_player_ptr = PlayerPtr;
                            Logic_Switch_Player_Context(this);
#endif
                            Map.IsTargettingMode = SPC_CHRONO2;
#ifdef REMASTER_BUILD
                            On_Special_Weapon_Targetting(PlayerPtr, Map.IsTargettingMode);
                            Logic_Switch_Player_Context(old_player_ptr);
#endif
                            UnitToTeleport = tech->As_Target();
                            fired = true;
                            what = "CHRONO";
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
                        }
#endif
                    }
                }
            }
        }
        break;

    case SPC_CHRONO2: {
        TechnoClass* tech = (TechnoClass*)::As_Object(UnitToTeleport);
        CELL oldcell = cell;
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
        if (tech != NULL && tech->IsActive && tech->Is_Foot() && tech->What_Am_I() != RTTI_AIRCRAFT) {
#else
        if (tech != NULL && tech->Is_Foot() && tech->What_Am_I() != RTTI_AIRCRAFT) {
#endif
            /*
            ** Destroy any infantryman that gets teleported
            */
            if (tech->What_Am_I() == RTTI_INFANTRY) {
                InfantryClass* inf = (InfantryClass*)tech;
                inf->Mark(MARK_UP);
                inf->Coord = Cell_Coord(cell);
                inf->Mark(MARK_DOWN);
                int damage = inf->Strength;
                inf->Take_Damage(damage, 0, WARHEAD_FIRE, 0, true);
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
            } else if (tech->What_Am_I() == RTTI_UNIT && *(UnitClass*)tech == UNIT_DEMOTRUCK) {
                tech->Assign_Target(tech->As_Target());
#endif
            } else {
                /*
                **	Warp the unit to the new location.
                */
                DriveClass* drive = (DriveClass*)tech;
                drive->MoebiusCell = Coord_Cell(drive->Coord);
                oldcell = drive->MoebiusCell;
                drive->Teleport_To(cell);
                drive->IsMoebius = true;
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
                if (tech->What_Am_I() == RTTI_UNIT && *(UnitClass*)tech == UNIT_CHRONOTANK) {
                    drive->IsMoebius = false;
                }
                drive->MoebiusCountDown = Rule.ChronoDuration * TICKS_PER_MINUTE;
                if (tech->What_Am_I() == RTTI_UNIT && *(UnitClass*)tech == UNIT_CHRONOTANK) {
                    drive->MoebiusCountDown = ChronoTankDuration * TICKS_PER_MINUTE;
                }
#else
                drive->MoebiusCountDown = Rule.ChronoDuration * TICKS_PER_MINUTE;
#endif
                Scen.Do_BW_Fade();
                Sound_Effect(VOC_CHRONO, drive->Coord);

                /*
                **	Set active animation on Chronospheres.
                */
                for (int index = 0; index < Buildings.Count(); ++index) {
                    BuildingClass* building = Buildings.Ptr(index);
                    if (building != nullptr && building->IsActive && building->Owner() == Class->House
                        && *building == STRUCT_CHRONOSPHERE) {
                        building->Begin_Mode(BSTATE_ACTIVE);
                    }
                }
            }
        }
        UnitToTeleport = TARGET_NONE;
        if (this == PlayerPtr) {
            Map.IsTargettingMode = SPC_NONE;
        }
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
        if (tech && tech->IsActive && (tech->What_Am_I() != RTTI_UNIT || *(UnitClass*)tech != UNIT_CHRONOTANK)) {
#endif
            SuperWeapon[SPC_CHRONOSPHERE].Discharged(this == PlayerPtr);
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
        }
#endif
        IsRecalcNeeded = true;
        fired = true;
        what = "CHRONO2";

        /*
        ** Now set a percentage chance that a time quake will occur.
        */
        if (!TimeQuake) {
            TimeQuake = Percent_Chance(Rule.QuakeChance * 100);
        }

        /*
        ** Now set a percentage chance that a chronal vortex will appear. It
        **	might appear where the object teleported to or it might appear
        **	where it teleported from -- random chance.
        */
#ifdef FIXIT_CSII //	checked - ajw 9/28/98                                                                             \
                  // Don't allow a vortex if the teleportation was due to a chrono tank.
        if (tech && tech->IsActive && (tech->What_Am_I() != RTTI_UNIT || *(UnitClass*)tech != UNIT_CHRONOTANK))
#endif
            if (!ChronalVortex.Is_Active() && Percent_Chance(Rule.VortexChance * 100)) {
                int x = Random_Pick(0, Map.MapCellWidth - 1);
                int y = Random_Pick(0, Map.MapCellHeight - 1);
                ChronalVortex.Appear(Cell_Coord(XY_Cell(Map.MapCellX + x, Map.MapCellY + y)));

                //					if (Percent_Chance(50)) {
                //						ChronalVortex.Appear(Cell_Coord(oldcell));
                //					} else {
                //						ChronalVortex.Appear(Cell_Coord(cell));
                //					}
            }

        break;
    }
    }
#ifdef REMASTER_BUILD
    /*
    ** Maybe trigger an achivement. ST - 12/2/2019 11:25AM
    */
    if (IsHuman && fired && what) {
        On_Achievement_Event(this, "SUPERWEAPON_FIRED", what);
    }
#endif
    return (true);
}

/***********************************************************************************************
 * HouseClass::Place_Object -- Places the object (building) at location specified.             *
 *                                                                                             *
 *    This routine is called when a building has been produced and now must be placed on       *
 *    the map. When the player clicks on the map, this routine is ultimately called when the   *
 *    event passes through the event queue system.                                             *
 *                                                                                             *
 * INPUT:   type  -- The object type to place. The actual object is lifted from the sidebar.   *
 *                                                                                             *
 *                                                                                             *
 *          cell  -- The location to place the object on the map.                              *
 *                                                                                             *
 * OUTPUT:  Was the placement successful?                                                      *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/18/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
extern void On_Ping(const HouseClass* player_ptr, COORDINATE coord);

bool HouseClass::Place_Object(RTTIType type, CELL cell)
{
    assert(Houses.ID(this) == ID);

    TechnoClass* tech = 0;
    FactoryClass* factory = Fetch_Factory(type);

    /*
    **	Only if there is a factory active for this type, can it be "placed".
    **	In the case of a missing factory, then this request is completely bogus --
    **	ignore it. This might occur if, between two events to exit the same
    **	object, the mouse was clicked on the sidebar to start building again.
    **	The second placement event should NOT try to place the object that is
    **	just starting construction.
    */
    if (factory && factory->Has_Completed()) {
        tech = factory->Get_Object();

        if (cell == -1) {
            TechnoClass* pending = factory->Get_Object();
            if (pending != NULL) {

#ifdef FIXIT_HELI_LANDING
                /*
                **	Try to find a place for the object to appear from. For helicopters, it has the
                **	option of finding a nearby helipad if no helipads are free.
                **	Tiberian Factions: vehicles produced at STRUCT_TDAFLD are delivered by
                **	cargo plane — the airstrip is in radio contact with the in-flight plane,
                **	which would normally cause Who_Can_Build_Me to reject it. Retry with
                **	`intheory=true` (same fallback path as helicopters) so back-to-back
                **	queue completions dispatch immediately rather than waiting for plane #1
                **	to deliver and release the tether.
                */
                TechnoClass* builder = pending->Who_Can_Build_Me(false, false);
                if (builder == NULL && pending->What_Am_I() == RTTI_AIRCRAFT
                    && !((AircraftClass*)pending)->Class->IsFixedWing) {
                    builder = pending->Who_Can_Build_Me(true, false);
                }
                if (builder == NULL && pending->What_Am_I() == RTTI_UNIT
                    && Get_Quantity(STRUCT_TDAFLD) > 0) {
                    builder = pending->Who_Can_Build_Me(true, false);
                }
#else
                bool intheory = false;
                if (pending->What_Am_I() == RTTI_AIRCRAFT) {

                    /*
                    ** BG hack - helicopters don't need a specific building to
                    ** emerge from, in fact, they'll land next to a building if
                    ** need be.
                    */
                    if (!((AircraftClass*)pending)->Class->IsFixedWing) {
                        intheory = true;
                    }
                }
                /*
                **  Tiberian Factions: vehicles produced at STRUCT_TDAFLD are
                **  delivered by cargo plane. While the previous plane is in-
                **  flight, TDAFLD is in radio contact with it — which would
                **  normally cause Who_Can_Build_Me to reject the building.
                **  Setting intheory=true bypasses that radio-contact filter
                **  so back-to-back queue completions dispatch immediately
                **  rather than waiting for plane #1 to deliver and release
                **  the tether. Same mechanism the engine already uses for
                **  helicopters when their helipad is busy.
                */
                if (pending->What_Am_I() == RTTI_UNIT && Get_Quantity(STRUCT_TDAFLD) > 0) {
                    intheory = true;
                }
                TechnoClass* builder = pending->Who_Can_Build_Me(intheory, false);
                // TF DIAGNOSTIC 2026-05-27: stubbed after multi-plane convoy
                // verified working. Re-enable (#if 1) to log every Place_Object
                // call (rtti, intheory, builder match, TDAFLD quantity). Useful
                // for diagnosing factory-stall / wrong-builder issues. Per
                // [[feedback-keep-diagnostics-until-v1]].
#if 0
                {
                    static FILE* s_pol = NULL;
                    if (s_pol == NULL) {
                        const char* up = getenv("USERPROFILE");
                        char p[512];
                        if (up) snprintf(p, sizeof(p), "%s/Documents/CnCRemastered/tf_place_object.log", up);
                        else strcpy(p, "tf_place_object.log");
                        s_pol = fopen(p, "a");
                    }
                    if (s_pol) {
                        fprintf(s_pol,
                            "[Place_Object] type=%d pending=%s rtti=%d intheory=%d builder=%s tdafld_qty=%d\n",
                            (int)type,
                            pending ? pending->Class_Of().IniName : "(null)",
                            pending ? (int)pending->What_Am_I() : -1,
                            (int)intheory,
                            builder ? builder->Class_Of().IniName : "(null)",
                            (int)Get_Quantity(STRUCT_TDAFLD));
                        fflush(s_pol);
                    }
                }
#endif
#endif
                TechnoTypeClass const* object_type = pending->Techno_Type_Class();
                if (builder != NULL && builder->Exit_Object(pending)) {

                    /*
                    **	Since the object has left the factory under its own power, delete
                    **	the production manager tied to this slot in the sidebar. Its job
                    **	has been completed.
                    */
                    factory->Set_Is_Blocked(false);
                    factory->Completed();
                    Abandon_Production(type);
#ifdef REMASTER_BUILD
                    /*
                    ** Could be tied to an achievement. ST - 11/11/2019 11:56AM
                    */
                    if (IsHuman) {
                        if (object_type) {
                            On_Achievement_Event(this, "UNIT_CONSTRUCTED", object_type->IniName);
                        }
                        if (pending->IsActive) {
                            On_Ping(this, pending->Center_Coord());
                        }
                    }
#endif
                    switch (pending->What_Am_I()) {
                    case RTTI_UNIT:
                        JustBuiltUnit = ((UnitClass*)pending)->Class->Type;
                        IsBuiltSomething = true;
                        break;

                    case RTTI_VESSEL:
                        JustBuiltVessel = ((VesselClass*)pending)->Class->Type;
                        IsBuiltSomething = true;
                        break;

                    case RTTI_INFANTRY:
                        JustBuiltInfantry = ((InfantryClass*)pending)->Class->Type;
                        IsBuiltSomething = true;
                        break;

                    case RTTI_BUILDING:
                        JustBuiltStructure = ((BuildingClass*)pending)->Class->Type;
                        IsBuiltSomething = true;
                        break;

                    case RTTI_AIRCRAFT:
                        JustBuiltAircraft = ((AircraftClass*)pending)->Class->Type;
                        IsBuiltSomething = true;
                        break;
                    }
                } else {
                    /*
                    **	The object could not leave under it's own power. Just wait
                    **	until the player tries to place the object again.
                    */

                    /*
                    ** Flag that it's blocked so we can re-try the exit later.
                    ** This would have been a bad idea under the old peer-peer code since it would have pumped events
                    *into
                    ** the queue too often. ST - 2/25/2020 11:56AM
                    */
                    factory->Set_Is_Blocked(true);
                    return (false);
                }
            }

        } else {
            if (tech) {
                TechnoClass* builder = tech->Who_Can_Build_Me(false, false);
                if (builder) {

                    builder->Transmit_Message(RADIO_HELLO, tech);
                    // Tiberian Factions mod: TD buildings slam down with TD's
                    // HVYDOOR1 instead of RA's PLACBLDG (mirrors the
                    // VOC_TD_CONSTRUCTION dispatch in building.cpp). This MUST be
                    // computed BEFORE Unlimbo: for wall types, BuildingClass::Unlimbo
                    // converts the building to an overlay and `delete this`-es it
                    // (then returns true) — so dereferencing `tech` afterward is a
                    // use-after-free that CTDs on every wall placement, all factions.
                    bool td_bldg = (tech->What_Am_I() == RTTI_BUILDING
                                    && ((BuildingClass*)tech)->Class->Is_Tiberian_Era());
                    if (tech->Unlimbo(Cell_Coord(cell))) {
                        factory->Completed();
                        Abandon_Production(type);

                        if (PlayerPtr == this) {
                            Sound_Effect(td_bldg ? VOC_TD_PLACE_BUILDING_DOWN : VOC_PLACE_BUILDING_DOWN);
                            Map.Set_Cursor_Shape(0);
                            Map.PendingObjectPtr = 0;
                            Map.PendingObject = 0;
                            Map.PendingHouse = HOUSE_NONE;
                        }
                        return (true);
                    } else {
                        if (this == PlayerPtr) {
                            Speak(VOX_DEPLOY);
                        }
                    }
                    builder->Transmit_Message(RADIO_OVER_OUT);
                }
                return (false);

            } else {

                // Play a bad sound here?
                return (false);
            }
        }
    }

    return (true);
}

/***********************************************************************************************
 * HouseClass::Manual_Place -- Inform display system of building placement mode.               *
 *                                                                                             *
 *    This routine will inform the display system that building placement mode has begun.      *
 *    The cursor will be created that matches the layout of the building shape.                *
 *                                                                                             *
 * INPUT:   builder  -- The factory that is building this object.                              *
 *                                                                                             *
 *          object   -- The building that is going to be placed down on the map.               *
 *                                                                                             *
 * OUTPUT:  Was the building placement mode successfully initiated?                            *
 *                                                                                             *
 * WARNINGS:   This merely adjusts the cursor shape. Nothing that affects networked games      *
 *             is affected.                                                                    *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/04/1995 JLB : Created.                                                                 *
 *   05/30/1995 JLB : Uses the Bib_And_Offset() function to determine bib size.                *
 *=============================================================================================*/
bool HouseClass::Manual_Place(BuildingClass* builder, BuildingClass* object)
{
    assert(Houses.ID(this) == ID);

    if (this == PlayerPtr && !Map.PendingObject && builder && object) {
        /*
        **	Ensures that object selection doesn't remain when
        **	building placement takes place.
        */
        Unselect_All();

        Map.Repair_Mode_Control(0);
        Map.Sell_Mode_Control(0);

        Map.PendingObject = object->Class;
        Map.PendingObjectPtr = object;
        Map.PendingHouse = Class->House;

        Map.Set_Cursor_Shape(object->Occupy_List(true));
        Map.Set_Cursor_Pos(Coord_Cell(builder->Coord));
        builder->Mark(MARK_CHANGE);
        return (true);
    }
    return (false);
}

/***************************************************************************
 * HouseClass::Clobber_All -- removes all objects for this house				*
 *                                                                         *
 * INPUT:                                                                  *
 *      none.                                                              *
 *                                                                         *
 * OUTPUT:                                                                 *
 *      none.                                                              *
 *                                                                         *
 * WARNINGS:                                                               *
 *      This routine removes the house itself, so the multiplayer code		*
 *		  must not rely on there being "empty" houses lying around.				*
 *                                                                         *
 * HISTORY:                                                                *
 *   05/16/1995 BRR : Created.                                             *
 *   06/09/1995 JLB : Handles aircraft.                                    *
 *=========================================================================*/
void HouseClass::Clobber_All(void)
{
    assert(Houses.ID(this) == ID);

    int i;

    for (i = 0; i < ::Aircraft.Count(); i++) {
        if (::Aircraft.Ptr(i)->House == this) {
            delete ::Aircraft.Ptr(i);
            i--;
        }
    }
    for (i = 0; i < ::Units.Count(); i++) {
        if (::Units.Ptr(i)->House == this) {
            delete ::Units.Ptr(i);
            i--;
        }
    }
    for (i = 0; i < ::Vessels.Count(); i++) {
        if (::Vessels.Ptr(i)->House == this) {
            delete ::Vessels.Ptr(i);
            i--;
        }
    }
    for (i = 0; i < Infantry.Count(); i++) {
        if (Infantry.Ptr(i)->House == this) {
            delete Infantry.Ptr(i);
            i--;
        }
    }
    for (i = 0; i < Buildings.Count(); i++) {
        if (Buildings.Ptr(i)->House == this) {
            delete Buildings.Ptr(i);
            i--;
        }
    }
    for (i = 0; i < TeamTypes.Count(); i++) {
        if (TeamTypes.Ptr(i)->House == Class->House) {
            delete TeamTypes.Ptr(i);
            i--;
        }
    }
    for (i = 0; i < Triggers.Count(); i++) {
        if (Triggers.Ptr(i)->Class->House == Class->House) {
            delete Triggers.Ptr(i);
            i--;
        }
    }
    for (i = 0; i < TriggerTypes.Count(); i++) {
        if (TriggerTypes.Ptr(i)->House == Class->House) {
            delete TriggerTypes.Ptr(i);
            i--;
        }
    }

    delete this;
}

/***********************************************************************************************
 * HouseClass::Detach -- Removes specified object from house tracking systems.                 *
 *                                                                                             *
 *    This routine is called when an object is to be removed from the game system. If the      *
 *    specified object is part of the house tracking system, then it will be removed.          *
 *                                                                                             *
 * INPUT:   target   -- The target value of the object that is to be removed from the game.    *
 *                                                                                             *
 *          all      -- Is the target going away for good as opposed to just cloaking/hiding?  *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/18/1995 JLB : commented                                                                *
 *=============================================================================================*/
void HouseClass::Detach(TARGET target, bool)
{
    assert(Houses.ID(this) == ID);

    if (ToCapture == target) {
        ToCapture = TARGET_NONE;
    }

    if (Is_Target_Trigger(target)) {
        HouseTriggers[ID].Delete(As_Trigger(target));
    }
}

/***********************************************************************************************
 * HouseClass::Does_Enemy_Building_Exist -- Checks for enemy building of specified type.       *
 *                                                                                             *
 *    This routine will examine the enemy houses and if there is a building owned by one       *
 *    of those house, true will be returned.                                                   *
 *                                                                                             *
 * INPUT:   btype -- The building type to check for.                                           *
 *                                                                                             *
 * OUTPUT:  Does a building of the specified type exist for one of the enemy houses?           *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Does_Enemy_Building_Exist(StructType btype) const
{
    assert(Houses.ID(this) == ID);

    int bflag = 1L << btype;
    for (HousesType index = HOUSE_FIRST; index < HOUSE_COUNT; index++) {
        HouseClass* house = HouseClass::As_Pointer(index);

        if (house && !Is_Ally(house) && (house->ActiveBScan & bflag) != 0) {
            return (true);
        }
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::Suggest_New_Object -- Determine what would the next buildable object be.        *
 *                                                                                             *
 *    This routine will examine the house status and return with a techno type pointer to      *
 *    the object type that it thinks should be created. The type is restricted to match the    *
 *    type specified. Typical use of this routine is by computer controlled factories.         *
 *                                                                                             *
 * INPUT:   objecttype  -- The type of object to restrict the scan for.                        *
 *                                                                                             *
 *          kennel      -- Is this from a kennel? There are special hacks to ensure that only  *
 *                         dogs can be produced from a kennel.                                 *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to a techno type for the object type that should be         *
 *          created. If no object should be created, then NULL is returned.                    *
 *                                                                                             *
 * WARNINGS:   This is a time consuming routine. Only call when necessary.                     *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
TechnoTypeClass const* HouseClass::Suggest_New_Object(RTTIType objecttype, bool kennel) const
{
    assert(Houses.ID(this) == ID);

    TechnoTypeClass const* techno = NULL;

    switch (objecttype) {
    case RTTI_AIRCRAFT:
    case RTTI_AIRCRAFTTYPE:
        if (BuildAircraft != AIRCRAFT_NONE) {
            return (&AircraftTypeClass::As_Reference(BuildAircraft));
        }
        return (NULL);

    case RTTI_VESSEL:
    case RTTI_VESSELTYPE:
        if (BuildVessel != VESSEL_NONE) {
            return (&VesselTypeClass::As_Reference(BuildVessel));
        }
        return (NULL);

    /*
    **	Unit construction is based on the rule that up to twice the number required
    **	to fill all teams will be created.
    */
    case RTTI_UNIT:
    case RTTI_UNITTYPE:
        if (BuildUnit != UNIT_NONE) {
            return (&UnitTypeClass::As_Reference(BuildUnit));
        }
        return (NULL);

    /*
    **	Infantry construction is based on the rule that up to twice the number required
    **	to fill all teams will be created.
    */
    case RTTI_INFANTRY:
    case RTTI_INFANTRYTYPE:
        if (BuildInfantry != INFANTRY_NONE) {
            if (kennel && BuildInfantry != INFANTRY_DOG)
                return (NULL);
            if (!kennel && BuildInfantry == INFANTRY_DOG)
                return (NULL);
            return (&InfantryTypeClass::As_Reference(BuildInfantry));
        }
        return (NULL);

    /*
    **	Building construction is based upon the preconstruction list.
    */
    case RTTI_BUILDING:
    case RTTI_BUILDINGTYPE:
        if (BuildStructure != STRUCT_NONE) {
            return (&BuildingTypeClass::As_Reference(BuildStructure));
        }
        return (NULL);
    }
    return (techno);
}

/***********************************************************************************************
 * HouseClass::Flag_Remove -- Removes the flag from the specified target.                      *
 *                                                                                             *
 *    This routine will remove the flag attached to the specified target object or cell.       *
 *    Call this routine before placing the object down. This is called inherently by the       *
 *    the Flag_Attach() functions.                                                             *
 *                                                                                             *
 * INPUT:   target   -- The target that the flag was attached to but will be removed from.     *
 *                                                                                             *
 *          set_home -- if true, clears the flag's waypoint designation                        *
 *                                                                                             *
 * OUTPUT:  Was the flag successfully removed from the specified target?                       *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Flag_Remove(TARGET target, bool set_home)
{
    assert(Houses.ID(this) == ID);

    bool rc = false;

    if (Target_Legal(target)) {

        /*
        **	Remove the flag from a unit
        */
        UnitClass* object = As_Unit(target);
        if (object) {
            rc = object->Flag_Remove();
            if (rc && FlagLocation == target) {
                FlagLocation = TARGET_NONE;
            }

        } else {

            /*
            **	Remove the flag from a cell
            */
            CELL cell = As_Cell(target);
            if (Map.In_Radar(cell)) {
                rc = Map[cell].Flag_Remove();
                if (rc && FlagLocation == target) {
                    FlagLocation = TARGET_NONE;
                }
            }
        }

        /*
        **	Handle the flag home cell:
        **	If 'set_home' is set, clear the home value & the cell's overlay
        */
        if (set_home) {
            if (FlagHome != 0) {
                Map[FlagHome].Overlay = OVERLAY_NONE;
                Map.Flag_Cell(FlagHome);
                FlagHome = 0;
            }
        }
    }
    return (rc);
}

/***********************************************************************************************
 * HouseClass::Flag_Attach -- Attach flag to specified cell (or thereabouts).                  *
 *                                                                                             *
 *    This routine will attach the house flag to the location specified. If the location       *
 *    cannot contain the flag, then a suitable nearby location will be selected.               *
 *                                                                                             *
 * INPUT:   cell  -- The desired cell location to place the flag.                              *
 *                                                                                             *
 *          set_home -- if true, resets the flag's waypoint designation                        *
 *                                                                                             *
 * OUTPUT:  Was the flag successfully placed?                                                  *
 *                                                                                             *
 * WARNINGS:   The cell picked for the flag might very likely not be the cell requested.       *
 *             Check the FlagLocation value to determine the final cell resting spot.          *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/23/1995 JLB : Created.                                                                 *
 *   10/08/1996 JLB : Uses map nearby cell scanning handler.                                   *
 *=============================================================================================*/
bool HouseClass::Flag_Attach(CELL cell, bool set_home)
{
    assert(Houses.ID(this) == ID);

    bool rc;
    bool clockwise;

    /*
    **	Randomly decide if we're going to search cells clockwise or counter-
    **	clockwise
    */
    clockwise = Percent_Chance(50);

    /*
    **	Only continue if this cell is a legal placement cell.
    */
    if (Map.In_Radar(cell)) {

        /*
        **	If the flag already exists, then it must be removed from the object
        **	it is attached to.
        */
        Flag_Remove(FlagLocation, set_home);

        /*
        **	Attach the flag to the cell specified. If it can't be placed, then pick
        **	a nearby cell where it can be placed.
        */
        CELL newcell = cell;
        rc = Map[newcell].Flag_Place(Class->House);
        if (!rc) {
            newcell = Map.Nearby_Location(cell, SPEED_TRACK, -1, MZONE_NORMAL, true);
            if (newcell != 0) {
                rc = Map[newcell].Flag_Place(Class->House);
            }

#ifdef OBSOLETE
            /*
            **	Loop for increasing distance from the desired cell.
            **	For each distance, randomly pick a starting direction.  Between
            **	this and the clockwise/counterclockwise random value, the flag
            **	should appear to be placed fairly randomly.
            */
            for (int dist = 1; dist < 32; dist++) {
                FacingType fcounter;
                FacingType rot;

                /*
                **	Clockwise search.
                */
                if (clockwise) {
                    rot = Random_Pick(FACING_N, FACING_NW);
                    for (fcounter = FACING_N; fcounter <= FACING_NW; fcounter++) {
                        newcell = Coord_Cell(Coord_Move(Cell_Coord(cell), Facing_Dir(rot), dist * 256));
                        if (Map.In_Radar(newcell) && Map[newcell].Flag_Place(Class->House)) {
                            dist = 32;
                            rc = true;
                            break;
                        }
                        rot++;
                        if (rot > FACING_NW)
                            rot = FACING_N;
                    }
                } else {

                    /*
                    **	Counter-clockwise search
                    */
                    rot = Random_Pick(FACING_N, FACING_NW);
                    for (fcounter = FACING_NW; fcounter >= FACING_N; fcounter--) {
                        newcell = Coord_Cell(Coord_Move(Cell_Coord(cell), Facing_Dir(rot), dist * 256));
                        if (Map.In_Radar(newcell) && Map[newcell].Flag_Place(Class->House)) {
                            dist = 32;
                            rc = true;
                            break;
                        }
                        rot--;
                        if (rot < FACING_N)
                            rot = FACING_NW;
                    }
                }
            }
#endif
        }

        /*
        **	If we've found a spot for the flag, place the flag at the new cell.
        **	if 'set_home' is set, OR this house has no current flag home cell,
        **	mark that cell as this house's flag home cell. Otherwise fall back
        **	on returning the flag to its home.
        */
        if (rc) {
            FlagLocation = As_Target(newcell);

            if (set_home || FlagHome == 0) {
                Map[newcell].Overlay = OVERLAY_FLAG_SPOT;
                Map[newcell].OverlayData = 0;
                Map[newcell].Recalc_Attributes();
                FlagHome = newcell;
            }
        } else if (FlagHome != 0) {
            rc = Map[FlagHome].Flag_Place(Class->House);
        }

        return (rc);
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::Flag_Attach -- Attaches the house flag the specified unit.                      *
 *                                                                                             *
 *    This routine will attach the house flag to the specified unit. This routine is called    *
 *    when a unit drives over a cell containing a flag.                                        *
 *                                                                                             *
 * INPUT:   object   -- Pointer to the object that the house flag is to be attached to.        *
 *                                                                                             *
 *          set_home -- if true, clears the flag's waypoint designation                        *
 *                                                                                             *
 * OUTPUT:  Was the flag attached successfully?                                                *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/23/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Flag_Attach(UnitClass* object, bool set_home)
{
    assert(Houses.ID(this) == ID);

    if (object && !object->IsInLimbo) {
        Flag_Remove(FlagLocation, set_home);

        /*
        **	Attach the flag to the object.
        */
        object->Flag_Attach(Class->House);
        FlagLocation = object->As_Target();
        return (true);
    }
    return (false);
}

extern void On_Defeated_Message(const char* message, float timeout_seconds);

/***************************************************************************
 * HouseClass::MPlayer_Defeated -- multiplayer; house is defeated          *
 *                                                                         *
 * INPUT:                                                                  *
 *      none.                                                              *
 *                                                                         *
 * OUTPUT:                                                                 *
 *      none.                                                              *
 *                                                                         *
 * WARNINGS:                                                               *
 *      none.                                                              *
 *                                                                         *
 * HISTORY:                                                                *
 *   05/25/1995 BRR : Created.                                             *
 *=========================================================================*/
void HouseClass::MPlayer_Defeated(void)
{
    assert(Houses.ID(this) == ID);

    char txt[80];
    int i, j;
    unsigned char id;
    HouseClass* hptr;
    HouseClass* hptr2;
    int num_alive;
    int num_humans;
    int all_allies;

    /*
    **	Set the defeat flag for this house
    */
    IsDefeated = true;

    /*
    **	If this is a computer controlled house, then all computer controlled
    **	houses become paranoid.
    */
    if (IQ == Rule.MaxIQ && !IsHuman && Rule.IsComputerParanoid) {
        Computer_Paranoid();
    }

    /*
    **	Remove this house's flag & flag home cell
    */
    if (Special.IsCaptureTheFlag) {
        if (FlagLocation) {
            Flag_Remove(FlagLocation, true);
        } else {
            if (FlagHome != 0) {
                Flag_Remove(FlagHome, true);
            }
        }
    }

    /*
    **	Remove any one-time superweapons the player might have.
    */
    for (i = SPC_FIRST; i < SPC_COUNT; i++) {
        SuperWeapon[i].Remove(true);
    }

    /*
    **	If this is me:
    **	- Set MPlayerObiWan, so I can only send messages to all players, and
    **	  not just one (so I can't be obnoxiously omnipotent)
    **	- Reveal the map
    **	- Add my defeat message
    */
    if (PlayerPtr == this) {
        Session.ObiWan = 1;
        HidPage.Clear();
        Map.Flag_To_Redraw(true);

        /*
        **	Pop up a message showing that I was defeated
        */
        sprintf(txt, Text_String(TXT_PLAYER_DEFEATED), IniName);
        if (Session.Type == GAME_NORMAL) {
            Session.Messages.Add_Message(NULL,
                                         0,
                                         txt,
                                         Session.ColorIdx,
                                         TPF_6PT_GRAD | TPF_USE_GRAD_PAL | TPF_FULLSHADOW,
                                         Rule.MessageDelay * TICKS_PER_MINUTE);
        }
        Map.Flag_To_Redraw(false);
#ifdef REMASTER_BUILD
        if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
            int timeout = Rule.MessageDelay * TICKS_PER_MINUTE;
            On_Defeated_Message(txt, timeout * 60.0f / TICKS_PER_MINUTE);
            Sound_Effect(VOC_INCOMING_MESSAGE);
        }
#endif
    } else {

        /*
        **	If it wasn't me, find out who was defeated
        */
        if (IsHuman) {
            sprintf(txt, Text_String(TXT_PLAYER_DEFEATED), IniName);

            // Session.Messages.Add_Message(NULL, 0, txt, RemapColor,
            //	TPF_6PT_GRAD | TPF_USE_GRAD_PAL | TPF_FULLSHADOW, Rule.MessageDelay * TICKS_PER_MINUTE);
            Map.Flag_To_Redraw(false);
            RedrawOptionsMenu = true;
#ifdef REMASTER_BUILD
            int timeout = Rule.MessageDelay * TICKS_PER_MINUTE;
            On_Defeated_Message(txt, timeout * 60.0f / TICKS_PER_MINUTE);
#endif
            Sound_Effect(VOC_INCOMING_MESSAGE);
        }
    }

    /*
    **	Find out how many players are left alive.
    */
    num_alive = 0;
    num_humans = 0;
    for (i = 0; i < Session.MaxPlayers; i++) {
        hptr = HouseClass::As_Pointer((HousesType)(HOUSE_MULTI1 + i));
        if (hptr && !hptr->IsDefeated) {
            if (hptr->IsHuman) {
                num_humans++;
            }
            num_alive++;
        }
    }

    /*
    **	If all the houses left alive are allied with each other, then in reality
    **	there's only one player left:
    */
    all_allies = 1;
    for (i = 0; i < Session.MaxPlayers; i++) {

        /*
        **	Get a pointer to this house
        */
        hptr = HouseClass::As_Pointer((HousesType)(HOUSE_MULTI1 + i));
        if (!hptr || hptr->IsDefeated)
            continue;

        /*
        **	Loop through all houses; if there's one left alive that this house
        **	isn't allied with, then all_allies will be false
        */
        for (j = 0; j < Session.MaxPlayers; j++) {
            hptr2 = HouseClass::As_Pointer((HousesType)(HOUSE_MULTI1 + j));
            if (!hptr2) {
                continue;
            }

            if (!hptr2->IsDefeated && !hptr->Is_Ally(hptr2)) {
                all_allies = 0;
                break;
            }
        }
        if (!all_allies) {
            break;
        }
    }

    /*
    **	If all houses left are allies, set 'num_alive' to 1; game over.
    */
    if (all_allies) {
        num_alive = 1;
    }

    /*
    **	If there's only one human player left or no humans left, the game is over:
    **	- Determine whether this player wins or loses, based on the state of the
    **	  player's IsDefeated flag
    **	- Find all players' indices in the Session.Score array
    **	- Tally up scores for this game
    */
    if (num_alive == 1 || num_humans == 0) {
        if (PlayerPtr->IsDefeated) {
            PlayerLoses = true;
        } else {
            PlayerWins = true;
        }

        /*
        ** Add up the scores
        */
        Tally_Score();

#ifdef NETWORKING
        /*
        **	Destroy all the IPX connections, since we have to go through the rest
        **	of the Main_Loop() before we detect that the game is over, and we'll
        **	end up waiting for frame sync packets from the other machines.
        */
        if (Session.Type == GAME_IPX || Session.Type == GAME_INTERNET) {
            i = 0;
            while (Ipx.Num_Connections() && (i++ < 1000)) {
                id = Ipx.Connection_ID(0);
                Ipx.Delete_Connection(id);
            }
            Session.NumPlayers = 0;
        }
#endif
    }
}

/***************************************************************************
 * HouseClass::Tally_Score -- Fills in the score system for this round     *
 *                                                                         *
 * INPUT:                                                                  *
 *		none.																						*
 *                                                                         *
 * OUTPUT:                                                                 *
 *		none.																						*
 *                                                                         *
 * WARNINGS:                                                               *
 *		none.																						*
 *                                                                         *
 * HISTORY:                                                                *
 *   11/29/1995 BRR : Created.                                             *
 *=========================================================================*/
void HouseClass::Tally_Score(void)
{
    HousesType house;
    HousesType house2;
    HouseClass* hptr;
    int score_index;
    int i, j, k;
    int max_index;
    int max_count;
    int count;

    /*
    ** Loop through all houses, tallying up each player's score
    */
    for (house = HOUSE_FIRST; house < HOUSE_COUNT; house++) {
        hptr = HouseClass::As_Pointer(house);
        /*
        ** Skip this house if it's not human.
        */
        if (!hptr || !hptr->IsHuman) {
            continue;
        }
        /*
        ** Now find out where this player is in the score array
        */
        score_index = -1;
        for (i = 0; i < Session.NumScores; i++) {
            if (!stricmp(hptr->IniName, Session.Score[i].Name)) {
                score_index = i;
                break;
            }
        }

        /*
        **	If the index is still -1, the name wasn't found; add a new entry.
        */
        if (score_index == -1) {
            /*
            ** Just add this player to the end of the array, if there's room
            */
            if (Session.NumScores < MAX_MULTI_NAMES) {
                score_index = Session.NumScores;
                Session.NumScores++;
            }
            /*
            ** If there's not room, we have to remove somebody.
            **	For each player in the scores array, count the # of '-1' entries
            **	from this game backwards; the one with the most is the one that
            **	hasn't played the longest; replace him with this new guy.
            */
            else {
                max_index = 0;
                max_count = 0;
                for (j = 0; j < Session.NumScores; j++) {
                    count = 0;
                    for (k = Session.NumScores - 1; k >= 0; k--) {
                        if (Session.Score[j].Kills[k] == -1) {
                            count++;
                        } else {
                            break;
                        }
                    }
                    if (count > max_count) {
                        max_count = count;
                        max_index = j;
                    }
                }
                score_index = max_index;
            }

            /*
            **	Initialize this new score entry
            */
            Session.Score[score_index].Wins = 0;
            strcpy(Session.Score[score_index].Name, hptr->IniName);
            for (j = 0; j < MAX_MULTI_GAMES; j++)
                Session.Score[score_index].Kills[j] = -1;
        }

        /*
        **	Init this player's Kills to 0 (-1 means he didn't play this round;
        **	0 means he played but got no kills).
        */
        Session.Score[score_index].Kills[Session.CurGame] = 0;

        /*
        **	Init this player's color to his last-used color index
        */
        Session.Score[score_index].Color = hptr->RemapColor;

        /*
        **	If this house was undefeated, it must have been the winner.
        ** (If no human houses are undefeated, the computer won.)
        */
        if (!hptr->IsDefeated) {
            Session.Score[score_index].Wins++;
            Session.Winner = score_index;
        }

        /*
        **	Tally up all kills for this player
        */
        for (house2 = HOUSE_FIRST; house2 < HOUSE_COUNT; house2++) {
            Session.Score[score_index].Kills[Session.CurGame] += hptr->UnitsKilled[house2];
            Session.Score[score_index].Kills[Session.CurGame] += hptr->BuildingsKilled[house2];
        }
    }
}

/***************************************************************************
 * HouseClass::Blowup_All -- blows up everything                           *
 *                                                                         *
 * INPUT:                                                                  *
 *      none.                                                              *
 *                                                                         *
 * OUTPUT:                                                                 *
 *      none.                                                              *
 *                                                                         *
 * WARNINGS:                                                               *
 *      none.                                                              *
 *                                                                         *
 * HISTORY:                                                                *
 *   05/16/1995 BRR : Created.                                             *
 *   06/09/1995 JLB : Handles aircraft.                                    *
 *   05/07/1996 JLB : Handles ships.                                       *
 *=========================================================================*/
void HouseClass::Blowup_All(void)
{
    assert(Houses.ID(this) == ID);

    int i;
    int damage;
    UnitClass* uptr;
    InfantryClass* iptr;
    BuildingClass* bptr;
    int count;
    WarheadType warhead;

    /*
    **	Find everything owned by this house & blast it with a huge amount of damage
    **	at zero range.  Do units before infantry, so the units' drivers are killed
    **	too.  Using Explosion_Damage is like dropping a big bomb right on the
    **	object; it will also damage anything around it.
    */
    for (i = 0; i < ::Units.Count(); i++) {
        if (::Units.Ptr(i)->House == this && !::Units.Ptr(i)->IsInLimbo) {
            uptr = ::Units.Ptr(i);

            /*
            **	Some units can't be killed with one shot, so keep damaging them until
            **	they're gone.  The unit will destroy itself, and put an infantry in
            **	its place.  When the unit destroys itself, decrement 'i' since
            **	its pointer will be removed from the active pointer list.
            */
            count = 0;
            while (::Units.Ptr(i) == uptr && uptr->Strength) {

                // MBL 06.22.2020 RA: Not all aircraft die in this case; See https://jaas.ea.com/browse/TDRA-6840
                // Likely due to damage biasing based on RA factions and/or difficulty settings
                // Applying this to units (vehicles), ships, buildings, and infantry, too
                //
                // damage = uptr->Strength; // Original
                damage = 0x7fff; // Copied from TD

                uptr->Take_Damage(damage, 0, WARHEAD_HE, NULL, true);
                count++;
                if (count > 5 && uptr->IsActive) {
                    delete uptr;
                    break;
                }
            }
            i--;
        }
    }

    /*
    **	Destroy all aircraft owned by this house.
    */
    for (i = 0; i < ::Aircraft.Count(); i++) {
        if (::Aircraft.Ptr(i)->House == this && !::Aircraft.Ptr(i)->IsInLimbo) {
            AircraftClass* aptr = ::Aircraft.Ptr(i);

            // MBL 06.22.2020 RA: Not all aircraft die in this case; See https://jaas.ea.com/browse/TDRA-6840
            // Likely due to damage biasing based on RA factions and/or difficulty settings
            // Applying this to units (vehicles), ships, buildings, and infantry, too
            //
            // damage = aptr->Strength; // Original
            damage = 0x7fff; // Copied from TD

            aptr->Take_Damage(damage, 0, WARHEAD_HE, NULL, true);
            if (!aptr->IsActive) {
                i--;
            }
        }
    }

    /*
    **	Destroy all vessels owned by this house.
    */
    for (i = 0; i < ::Vessels.Count(); i++) {
        if (::Vessels.Ptr(i)->House == this && !::Vessels.Ptr(i)->IsInLimbo) {
            VesselClass* vptr = ::Vessels.Ptr(i);

            // MBL 06.22.2020 RA: Not all aircraft die in this case; See https://jaas.ea.com/browse/TDRA-6840
            // Likely due to damage biasing based on RA factions and/or difficulty settings
            // Applying this to units (vehicles), ships, buildings, and infantry, too
            //
            // damage = vptr->Strength; // Original
            damage = 0x7fff; // Copied from TD

            vptr->Take_Damage(damage, 0, WARHEAD_HE, NULL, true);
            if (!vptr->IsActive) {
                i--;
            }
        }
    }

    /*
    **	Buildings don't delete themselves when they die; they shake the screen
    **	and begin a countdown, so don't decrement 'i' when it's destroyed.
    */
    for (i = 0; i < Buildings.Count(); i++) {
        if (Buildings.Ptr(i)->House == this && !Buildings.Ptr(i)->IsInLimbo) {
            bptr = Buildings.Ptr(i);

            count = 0;
            while (Buildings.Ptr(i) == bptr && bptr->Strength) {

                // MBL 06.22.2020 RA: Not all aircraft die in this case; See https://jaas.ea.com/browse/TDRA-6840
                // Likely due to damage biasing based on RA factions and/or difficulty settings
                // Applying this to units (vehicles), ships, buildings, and infantry, too
                //
                // damage = bptr->Strength; // Original
                damage = 0x7fff; // Copied from TD

                bptr->Take_Damage(damage, 0, WARHEAD_HE, NULL, true);
                count++;
                if (count > 5) {
                    delete bptr;
                    break;
                }
            }
        }
    }

    /*
    **	Infantry don't delete themselves when they die; they go into a death-
    **	animation sequence, so there's no need to decrement 'i' when they die.
    **	Infantry should die by different types of warheads, so their death
    **	anims aren't all synchronized.
    */
    for (i = 0; i < Infantry.Count(); i++) {
        if (Infantry.Ptr(i)->House == this && !Infantry.Ptr(i)->IsInLimbo) {
            iptr = Infantry.Ptr(i);

            count = 0;
            while (Infantry.Ptr(i) == iptr && iptr->Strength) {

                // MBL 06.22.2020 RA: Not all aircraft die in this case; See https://jaas.ea.com/browse/TDRA-6840
                // Likely due to damage biasing based on RA factions and/or difficulty settings
                // Applying this to units (vehicles), ships, buildings, and infantry, too
                //
                // damage = iptr->Strength; // Original
                damage = 0x7fff; // Copied from TD

                warhead = Random_Pick(WARHEAD_SA, WARHEAD_FIRE);
                iptr->Take_Damage(damage, 0, warhead, NULL, true);

                count++;
                if (count > 5) {
                    delete iptr;
                    break;
                }
            }
        }
    }
}

/***********************************************************************************************
 * HouseClass::Flag_To_Die -- Flags the house to blow up soon.                                 *
 *                                                                                             *
 *    When this routine is called, the house will blow up after a period of time. Typically    *
 *    this is called when the flag is captured or the HQ destroyed.                            *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Was the house flagged to blow up?                                                  *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/20/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Flag_To_Die(void)
{
    assert(Houses.ID(this) == ID);

    if (!IsToWin && !IsToDie && !IsToLose) {
        IsToDie = true;
        BorrowedTime = TICKS_PER_MINUTE * Rule.SavourDelay;
    }
    return (IsToDie);
}

/***********************************************************************************************
 * HouseClass::Flag_To_Win -- Flags the house to win soon.                                     *
 *                                                                                             *
 *    When this routine is called, the house will be declared the winner after a period of     *
 *    time.                                                                                    *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Was the house flagged to win?                                                      *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/20/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Flag_To_Win(void)
{
    assert(Houses.ID(this) == ID);

    if (!IsToWin && !IsToDie && !IsToLose) {
        IsToWin = true;
        BorrowedTime = TICKS_PER_MINUTE * Rule.SavourDelay;
    }
    return (IsToWin);
}

/***********************************************************************************************
 * HouseClass::Flag_To_Lose -- Flags the house to die soon.                                    *
 *                                                                                             *
 *    When this routine is called, it will spell the doom of this house. In a short while      *
 *    all of the object owned by this house will explode. Typical use of this routine is when  *
 *    the flag has been captured or the command vehicle has been destroyed.                    *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Has the doom been initiated?                                                       *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/12/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Flag_To_Lose(void)
{
    assert(Houses.ID(this) == ID);

    IsToWin = false;
    if (!IsToDie && !IsToLose) {
        IsToLose = true;
        BorrowedTime = TICKS_PER_MINUTE * Rule.SavourDelay;
    }
    return (IsToLose);
}

/***********************************************************************************************
 * HouseClass::Init_Data -- Initializes the multiplayer color data.                            *
 *                                                                                             *
 *    This routine is called when initializing the color and remap data for this house. The    *
 *    primary user of this routine is the multiplayer version of the game, especially for		  *
 *    saving & loading multiplayer games.																		  *
 *                                                                                             *
 * INPUT:   color    -- The color of this house.                                               *
 *                                                                                             *
 *          house    -- The house that this should act like.                                   *
 *                                                                                             *
 *          credits  -- The initial credits to assign to this house.                           *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
extern bool NowSavingGame; // TEMP MBL: Need to discuss better solution with Steve
void HouseClass::Init_Data(PlayerColorType color, HousesType house, int credits)
{
    assert(Houses.ID(this) == ID);

    Credits = Control.InitialCredits = credits;
    VisibleCredits.Current = Credits;
    RemapColor = color;
    ActLike = house;

    // MBL 03.20.2020
    // Attempt to fix Red Alert credit tick-up bug after saving a game that has had harvesting underway
    // Note that this code gets called with both game loads and saves
    // When this function is called, sometimes credits value has Tiberium (or HarvestedCredits?) variables applied, and
    // sometimes now
    //
    if (NowSavingGame == true) {
        // At this point VisibleCredits.Current (set above) does not have harvested ore/tiberium applied, but
        // VisibleCredits.Credits does
        VisibleCredits.Current = VisibleCredits.Credits;
    }
}

/***********************************************************************************************
 * HouseClass::Power_Fraction -- Fetches the current power output rating.                      *
 *                                                                                             *
 *    Use this routine to fetch the current power output as a fixed point fraction. The        *
 *    value 0x0100 is 100% power.                                                              *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with power rating as a fixed pointer number.                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/22/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
fixed HouseClass::Power_Fraction(void) const
{
    assert(Houses.ID(this) == ID);

    if (Power >= Drain || Drain == 0)
        return (1);

    if (Power) {
        return (fixed(Power, Drain));
    }
    return (0);
}

/***********************************************************************************************
 * HouseClass::Sell_Wall -- Tries to sell the wall at the specified location.                  *
 *                                                                                             *
 *    This routine will try to sell the wall at the specified location. If there is a wall     *
 *    present and it is owned by this house, then it can be sold.                              *
 *                                                                                             *
 * INPUT:   cell  -- The cell that wall selling is desired.                                    *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   08/05/1995 JLB : Created.                                                                 *
 *   11/02/1996 JLB : Checks unsellable bit for wall type.                                     *
 *=============================================================================================*/
void HouseClass::Sell_Wall(CELL cell)
{
    assert(Houses.ID(this) == ID);

    if ((unsigned)cell > 0) {
        OverlayType overlay = Map[cell].Overlay;

        if (overlay != OVERLAY_NONE && Map[cell].Owner == Class->House) {
            OverlayTypeClass const& optr = OverlayTypeClass::As_Reference(overlay);

            if (optr.IsWall) {
                BuildingTypeClass const* btype = NULL;
                switch (overlay) {
                case OVERLAY_SANDBAG_WALL:
                    btype = &BuildingTypeClass::As_Reference(STRUCT_SANDBAG_WALL);
                    break;

                case OVERLAY_CYCLONE_WALL:
                    btype = &BuildingTypeClass::As_Reference(STRUCT_CYCLONE_WALL);
                    break;

                case OVERLAY_BRICK_WALL:
                    btype = &BuildingTypeClass::As_Reference(STRUCT_BRICK_WALL);
                    break;

                case OVERLAY_BARBWIRE_WALL:
                    btype = &BuildingTypeClass::As_Reference(STRUCT_BARBWIRE_WALL);
                    break;

                case OVERLAY_WOOD_WALL:
                    btype = &BuildingTypeClass::As_Reference(STRUCT_WOOD_WALL);
                    break;

                case OVERLAY_FENCE:
                    btype = &BuildingTypeClass::As_Reference(STRUCT_FENCE);
                    break;

                default:
                    break;
                }
                if (btype != NULL && !btype->IsUnsellable) {

                    if (PlayerPtr == this) {
                        Sound_Effect(VOC_CASHTURN);
                    }

                    Refund_Money(btype->Raw_Cost() * Rule.RefundPercent);
                    Map[cell].Overlay = OVERLAY_NONE;
                    Map[cell].OverlayData = 0;
                    Map[cell].Owner = HOUSE_NONE;
                    Map[cell].Wall_Update();
                    CellClass* ncell = Map[cell].Adjacent_Cell(FACING_N);
                    if (ncell)
                        ncell->Wall_Update();
                    CellClass* wcell = Map[cell].Adjacent_Cell(FACING_W);
                    if (wcell)
                        wcell->Wall_Update();
                    CellClass* scell = Map[cell].Adjacent_Cell(FACING_S);
                    if (scell)
                        scell->Wall_Update();
                    CellClass* ecell = Map[cell].Adjacent_Cell(FACING_E);
                    if (ecell)
                        ecell->Wall_Update();
                    Map[cell].Recalc_Attributes();
                    Map[cell].Redraw_Objects();
                    Map.Radar_Pixel(cell);
                    Detach_This_From_All(::As_Target(cell), true);

                    if (optr.IsCrushable) {
                        Map.Zone_Reset(MZONEF_NORMAL | MZONEF_HOVER);
                    } else {
                        Map.Zone_Reset(MZONEF_CRUSHER | MZONEF_NORMAL | MZONEF_HOVER);
                    }
                }
            }
        }
    }
}

/***********************************************************************************************
 * HouseClass::Suggest_New_Building -- Examines the situation and suggests a building.         *
 *                                                                                             *
 *    This routine is called when a construction yard needs to know what to build next. It     *
 *    will either examine the prebuilt base list or try to figure out what to build next       *
 *    based on the current game situation.                                                     *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the building type class to build.                        *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/27/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
BuildingTypeClass const* HouseClass::Suggest_New_Building(void) const
{
    assert(Houses.ID(this) == ID);

    if (BuildStructure != STRUCT_NONE) {
        return (&BuildingTypeClass::As_Reference(BuildStructure));
    }
    return (NULL);
}

/***********************************************************************************************
 * HouseClass::Find_Building -- Finds a building of specified type.                            *
 *                                                                                             *
 *    This routine is used to find a building of the specified type. This is particularly      *
 *    useful for when some event requires a specific building instance. The nuclear missile    *
 *    launch is a good example.                                                                *
 *                                                                                             *
 * INPUT:   type  -- The building type to scan for.                                            *
 *                                                                                             *
 *          zone  -- The zone that the building must be located in. If no zone specific search *
 *                   is desired, then pass ZONE_NONE.                                          *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the building type requested. If there is no building     *
 *          of the type requested, then NULL is returned.                                      *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/27/1995 JLB : Created.                                                                 *
 *   10/02/1995 JLB : Allows for zone specifics.                                               *
 *=============================================================================================*/
BuildingClass* HouseClass::Find_Building(StructType type, ZoneType zone) const
{
    assert(Houses.ID(this) == ID);

    /*
    **	Only scan if we KNOW there is at least one building of the type
    **	requested.
    */
    if (BQuantity[type] > 0) {

        /*
        **	Search for a suitable launch site for this missile.
        */
        for (int index = 0; index < Buildings.Count(); index++) {
            BuildingClass* b = Buildings.Ptr(index);
            if (b && !b->IsInLimbo && b->House == this && *b == type) {
                if (zone == ZONE_NONE || Which_Zone(b) == zone) {
                    return (b);
                }
            }
        }
    }
    return (NULL);
}

/***********************************************************************************************
 * HouseClass::Find_Build_Location -- Finds a suitable building location.                      *
 *                                                                                             *
 *    This routine is used to find a suitable building location for the building specified.    *
 *    The auto base building logic uses this when building the base for the computer.          *
 *                                                                                             *
 * INPUT:   building -- Pointer to the building that needs to be placed down.                  *
 *                                                                                             *
 * OUTPUT:  Returns with the coordinate to place the building at. If there are no suitable     *
 *          locations, then NULL is returned.                                                  *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/27/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
COORDINATE HouseClass::Find_Build_Location(BuildingClass* building) const
{
    assert(Houses.ID(this) == ID);

    /*
    **	Water-bound buildings can't use the defence-zone rings below: the zones are
    **	land rings around the base centre, and on most maps every legal coastal cell
    **	lies outside all of them, so the ring scan fails without saying why. Place
    **	on the assessed water directly instead. W5.1.
    */
    if (building->Class->Speed == SPEED_FLOAT) {
        CELL navalcell = TF_Find_Naval_Cell(building);
        if (navalcell) {
            return (Cell_Coord(navalcell));
        }
        return (0);
    }

    int zonerating[ZONE_COUNT];
    struct
    {
        int AntiAir;      // Average air defense for the base.
        int AntiArmor;    // Average armor defense for the base.
        int AntiInfantry; // Average infantry defense for the base.
    } zoneinfo = {0, 0, 0};
    int antiair = building->Anti_Air();
    int antiarmor = building->Anti_Armor();
    int antiinfantry = building->Anti_Infantry();
    bool adj = true;

    /*
    **	Never place combat buildings adjacent to each other. This is partly
    **	because combat buildings don't have a bib and jamming will occur as well
    **	as because spacing defensive buildings out will yield a better
    **	defense.
    */
    if (antiair || antiarmor || antiinfantry) {
        adj = false;
    }

    /*
    **	Determine the average zone strengths for the base. This value is
    **	used to determine what zones are considered under or over strength.
    */
    ZoneType z;
    for (z = ZONE_NORTH; z < ZONE_COUNT; z++) {
        zoneinfo.AntiAir += ZoneInfo[z].AirDefense;
        zoneinfo.AntiArmor += ZoneInfo[z].ArmorDefense;
        zoneinfo.AntiInfantry += ZoneInfo[z].InfantryDefense;
    }
    zoneinfo.AntiAir /= ZONE_COUNT - ZONE_NORTH;
    zoneinfo.AntiArmor /= ZONE_COUNT - ZONE_NORTH;
    zoneinfo.AntiInfantry /= ZONE_COUNT - ZONE_NORTH;

    /*
    **	Give each zone a rating for value. The higher the value the more desirable
    **	to place the specified building in that zone. Factor the average value of
    **	zone defense such that more weight is given to zones that are very under
    **	defended.
    */
    memset(&zonerating[0], '\0', sizeof(zonerating));
    for (z = ZONE_FIRST; z < ZONE_COUNT; z++) {
        int diff;

        diff = zoneinfo.AntiAir - ZoneInfo[z].AirDefense;
        if (z == ZONE_CORE)
            diff /= 2;
        if (diff > 0) {
            zonerating[z] += min(antiair, diff);
        }

        diff = zoneinfo.AntiArmor - ZoneInfo[z].ArmorDefense;
        if (z == ZONE_CORE)
            diff /= 2;
        if (diff > 0) {
            zonerating[z] += min(antiarmor, diff);
        }

        diff = zoneinfo.AntiInfantry - ZoneInfo[z].InfantryDefense;
        if (z == ZONE_CORE)
            diff /= 2;
        if (diff > 0) {
            zonerating[z] += min(antiinfantry, diff);
        }
    }

    /*
    **	Now that each zone has been given a desirability rating, find the zone
    **	with the greatest value and try to place the building in that zone.
    */
    ZoneType zone = Random_Pick(ZONE_FIRST, ZONE_WEST);
    int largest = 0;
    for (z = ZONE_FIRST; z < ZONE_COUNT; z++) {
        if (zonerating[z] > largest) {
            zone = z;
            largest = zonerating[z];
        }
    }

    CELL zcell = Find_Cell_In_Zone(building, zone);
    if (zcell) {
        return (Cell_Coord(zcell));
    }

    /*
    **	Could not build in preferred zone, so try building in any zone.
    */
    static ZoneType _zones[] = {ZONE_CORE, ZONE_NORTH, ZONE_SOUTH, ZONE_EAST, ZONE_WEST};
    int start = Random_Pick(0, ARRAY_SIZE(_zones) - 1);
    for (int zz = 0; zz < ARRAY_SIZE(_zones); zz++) {
        ZoneType tryzone = _zones[(zz + start) % ARRAY_SIZE(_zones)];
        zcell = Find_Cell_In_Zone(building, tryzone);
        if (zcell)
            return (Cell_Coord(zcell));
    }

    return (0);
}

/***********************************************************************************************
 * HouseClass::Recalc_Center -- Recalculates the center point of the base.                     *
 *                                                                                             *
 *    This routine will average the location of the base and record the center point. The      *
 *    recorded center point is used to determine such things as how far the base is spread     *
 *    out and where to protect the most. This routine should be called whenever a building     *
 *    is created or destroyed.                                                                 *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/28/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
/*
**	W5.3 expansion bases: which of the house's construction yards does a position
**	belong to? A building is a member of the cluster around its nearest yard.
*/
static int TF_Nearest_Yard(COORDINATE pos, COORDINATE const* yards, int count)
{
    int best = 0;
    int bestd = INT_MAX;
    for (int j = 0; j < count; j++) {
        int d = ::Distance(pos, yards[j]);
        if (d < bestd) {
            bestd = d;
            best = j;
        }
    }
    return (best);
}

void HouseClass::Recalc_Center(void)
{
    assert(Houses.ID(this) == ID);

    /*
    **	First presume that there is no base. If there is a base, then these values will be
    **	properly filled in below.
    */
    Center = 0;
    Radius = 0;
    for (ZoneType zone = ZONE_FIRST; zone < ZONE_COUNT; zone++) {
        ZoneInfo[zone].AirDefense = 0;
        ZoneInfo[zone].ArmorDefense = 0;
        ZoneInfo[zone].InfantryDefense = 0;
    }

    /*
    **	Only process the center base size/position calculation if there are buildings to
    **	consider. When no buildings for this house are present, then no processing need
    **	occur.
    */
    if (CurBuildings > 0) {
        int x = 0;
        int y = 0;
        int count = 0;
        int quantity = 0;
        int index;

        /*
        **	W5.3 expansion bases: with construction yards on two landmasses, averaging
        **	EVERY building drags Center into the sea between the bases and the zone
        **	rings collapse for both (the collapsed-geometry class of placement
        **	failure). The base brain therefore tracks only the DOMINANT cluster --
        **	each building belongs to its nearest yard, the heaviest cluster is the
        **	main base, and everything in the other clusters is invisible to Center/
        **	Radius/zone math. A remote yard places its own products around itself
        **	(see the remote-anchor branch in building.cpp).
        */
        COORDINATE yardpos[8];
        int yardcount = 0;
        for (index = 0; index < Buildings.Count() && yardcount < 8; index++) {
            BuildingClass const* b = Buildings.Ptr(index);
            if (b != NULL && !b->IsInLimbo && (HouseClass*)b->House == this && b->Strength > 0
                && (b->Class->Type == STRUCT_CONST || b->Class->Type == STRUCT_AFACT
                    || b->Class->Type == STRUCT_SFACT || b->Class->Type == STRUCT_TDFACT
                    || b->Class->Type == STRUCT_TDGFACT || b->Class->Type == STRUCT_TDNFACT)) {
                yardpos[yardcount++] = b->Center_Coord();
            }
        }
        int dominant = -1;
        if (yardcount > 1) {
            int mass[8] = {0};
            for (index = 0; index < Buildings.Count(); index++) {
                BuildingClass const* b = Buildings.Ptr(index);
                if (b != NULL && !b->IsInLimbo && (HouseClass*)b->House == this && b->Strength > 0) {
                    mass[TF_Nearest_Yard(b->Center_Coord(), yardpos, yardcount)] +=
                        (b->Class->Cost_Of() / 1000) + 1;
                }
            }
            dominant = 0;
            for (int j = 1; j < yardcount; j++) {
                if (mass[j] > mass[dominant]) {
                    dominant = j;
                }
            }
        }

        for (index = 0; index < Buildings.Count(); index++) {
            BuildingClass const* b = Buildings.Ptr(index);

            if (b != NULL && !b->IsInLimbo && (HouseClass*)b->House == this && b->Strength > 0) {
                if (dominant >= 0 && TF_Nearest_Yard(b->Center_Coord(), yardpos, yardcount) != dominant) {
                    continue;
                }

                /*
                **	Give more "weight" to buildings that cost more. The presumption is that cheap
                **	buildings don't affect the base disposition as much as the more expensive
                **	buildings do.
                */
                int weight = (b->Class->Cost_Of() / 1000) + 1;
                for (int i = 0; i < weight; i++) {
                    x += Coord_X(b->Center_Coord());
                    y += Coord_Y(b->Center_Coord());
                    count++;
                }
                quantity++;
            }
        }

        /*
        **	This second check for quantity of buildings is necessary because the first
        **	check against CurBuildings doesn't take into account if the building is in
        **	limbo, but for base calculation, the limbo state disqualifies a building
        **	from being processed. Thus, CurBuildings may indicate a base, but count may
        **	not match.
        */
        if (count > 0) {
            x /= count;
            y /= count;

#ifdef NEVER
            /*
            **	Bias the center of the base away from the edges of the map.
            */
            LEPTON left = Cell_To_Lepton(Map.MapCellX + 10);
            LEPTON top = Cell_To_Lepton(Map.MapCellY + 10);
            LEPTON right = Cell_To_Lepton(Map.MapCellX + Map.MapCellWidth - 10);
            LEPTON bottom = Cell_To_Lepton(Map.MapCellY + Map.MapCellHeight - 10);
            if (x < left)
                x = left;
            if (x > right)
                x = right;
            if (y < top)
                y = top;
            if (y > bottom)
                y = bottom;
#endif

            Center = XY_Coord(x, y);
        }

        /*
        **	If there were any buildings discovered as legal to consider as part of the base,
        **	then figure out the general average radius of the building disposition as it
        **	relates to the center of the base. The cost weighting applies to the center
        **	only — the radius is a plain mean over the buildings, so it is divided by the
        **	building quantity, not the weighted count.
        */
        if (quantity > 1) {
            int radius = 0;

            for (index = 0; index < Buildings.Count(); index++) {
                BuildingClass const* b = Buildings.Ptr(index);

                if (b != NULL && !b->IsInLimbo && (HouseClass*)b->House == this && b->Strength > 0) {
                    if (dominant >= 0 && TF_Nearest_Yard(b->Center_Coord(), yardpos, yardcount) != dominant) {
                        continue;
                    }
                    radius += Distance(Center, b->Center_Coord());
                }
            }
            Radius = max(radius / quantity, 2 * CELL_LEPTON_W);

            /*
            **	Determine the relative strength of each base defense zone.
            */
            for (index = 0; index < Buildings.Count(); index++) {
                BuildingClass const* b = Buildings.Ptr(index);

                if (b != NULL && !b->IsInLimbo && (HouseClass*)b->House == this && b->Strength > 0) {
                    if (dominant >= 0 && TF_Nearest_Yard(b->Center_Coord(), yardpos, yardcount) != dominant) {
                        continue;
                    }
                    ZoneType z = Which_Zone(b);

                    if (z != ZONE_NONE) {
                        ZoneInfo[z].ArmorDefense += b->Anti_Armor();
                        ZoneInfo[z].AirDefense += b->Anti_Air();
                        ZoneInfo[z].InfantryDefense += b->Anti_Infantry();
                    }
                }
            }

        } else {
            Radius = 0x0200;
        }
    }
}

/***********************************************************************************************
 * HouseClass::Expert_AI -- Handles expert AI processing.                                      *
 *                                                                                             *
 *    This routine is called when the computer should perform expert AI processing. This       *
 *    method of AI is categorized as an "Expert System" process.                               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns the number of game frames to delay before calling this routine again.      *
 *                                                                                             *
 * WARNINGS:   This is relatively time consuming -- call periodically.                         *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int HouseClass::Expert_AI(void)
{
    assert(Houses.ID(this) == ID);

    BuildingClass* b = 0;
    bool stop = false;
    int time = TICKS_PER_SECOND * 10;

    /*
    **	If the current enemy no longer has a base or is defeated, then don't consider
    **	that house a threat anymore. Clear out the enemy record and then try
    **	to find a new enemy.
    */
    if (Enemy != HOUSE_NONE) {
        HouseClass* h = HouseClass::As_Pointer(Enemy);

        if (h == NULL || !h->IsActive || h->IsDefeated || Is_Ally(h) || h->BScan == 0) {
            Enemy = HOUSE_NONE;
        }
    }

    /*
    **	Blind-scout dispatcher: with the fair-fog intel layer a house that has
    **	sighted no enemy building would otherwise wait forever -- AI_Attack sends
    **	hunters only rarely (and usually reshuffles instead), and the blind-hunt
    **	probe in Mission_Hunt can't run without hunters. So while blind, keep a
    **	small scout detail on MISSION_HUNT; the probe walks them across the map's
    **	start locations until contact is made, after which the normal attack
    **	pipeline has real targets to work with. MCVs (whose hunt order deploys
    **	the base!) and harvesters never scout.
    */
    if (Session.Type != GAME_NORMAL && IsStarted && !TF_Knows_Any_Enemy_Building()) {
        enum
        {
            TF_SCOUT_DETAIL = 2
        };
        int hunters = 0;
        int index;
        for (index = 0; index < Units.Count() && hunters < TF_SCOUT_DETAIL; index++) {
            UnitClass* u = Units.Ptr(index);
            if (u != NULL && !u->IsInLimbo && u->House == this && u->Strength > 0 && u->Mission == MISSION_HUNT) {
                hunters++;
            }
        }
        for (index = 0; index < Infantry.Count() && hunters < TF_SCOUT_DETAIL; index++) {
            InfantryClass* i = Infantry.Ptr(index);
            if (i != NULL && !i->IsInLimbo && i->House == this && i->Strength > 0 && i->Mission == MISSION_HUNT) {
                hunters++;
            }
        }
        for (index = 0; index < Units.Count() && hunters < TF_SCOUT_DETAIL; index++) {
            UnitClass* u = Units.Ptr(index);
            if (u != NULL && !u->IsInLimbo && u->House == this && u->Strength > 0 && u->Is_Weapon_Equipped()
                && !u->Class->IsToHarvest && !u->Class->Is_MCV()
                && (u->Mission == MISSION_GUARD || u->Mission == MISSION_GUARD_AREA)) {
                u->Assign_Mission(MISSION_HUNT);
                hunters++;
#if TF_DEV_BUILD // TF_AI_DIAG
                {
                    extern FILE* TF_AI_Diag_File(void);
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg,
                                "F%ld H%d AL%d SCOUT-DISPATCH unit %s#%d\n",
                                (long)Frame,
                                (int)Class->House,
                                (int)ActLike,
                                u->Class->IniName,
                                (int)u->ID);
                        fflush(_tfdbg);
                    }
                }
#endif
            }
        }
        for (index = 0; index < Infantry.Count() && hunters < TF_SCOUT_DETAIL; index++) {
            InfantryClass* i = Infantry.Ptr(index);
            if (i != NULL && !i->IsInLimbo && i->House == this && i->Strength > 0 && i->Is_Weapon_Equipped()
                && (i->Mission == MISSION_GUARD || i->Mission == MISSION_GUARD_AREA)) {
                i->Assign_Mission(MISSION_HUNT);
                hunters++;
#if TF_DEV_BUILD // TF_AI_DIAG
                {
                    extern FILE* TF_AI_Diag_File(void);
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg,
                                "F%ld H%d AL%d SCOUT-DISPATCH infantry %s#%d\n",
                                (long)Frame,
                                (int)Class->House,
                                (int)ActLike,
                                i->Class->IniName,
                                (int)i->ID);
                        fflush(_tfdbg);
                    }
                }
#endif
            }
        }
    }

    /*
    **	W5.1 naval patrol dispatcher: idle armed ships sail to random cells of the
    **	assessed water zone -- the naval counterpart of the blind-scout detail
    **	above. While blind it is the mechanism that DISCOVERS the enemy coast on
    **	maps ground scouts can't cross; after discovery it keeps the fleet moving
    **	across contested water, which is what brings guard-mode weapons within
    **	range of enemy hulls and shore targets -- a parked navy never fights.
    **	The land dispatcher's hunt waypoints must never be used here: a ship
    **	ordered to a land cell is a permanently unreachable destination (the
    **	pathfinder-storm profile), while any cell of the ship's own water zone is
    **	reachable by what a zone id means. Ships go idle on arrival, so each
    **	Expert_AI pass deals the next leg. Dedicated naval attack doctrine
    **	(concentrating on the enemy fleet, shore bombardment) is later W5 work.
    */
    if (Session.Type != GAME_NORMAL && IsStarted && Vessels.Count() > 0) {
        int pzone = 0;
        int psize = 0;
        bool pcoastal = false;
        if (TF_Naval_Assessment(pzone, psize, pcoastal)) {
            for (int vindex = 0; vindex < Vessels.Count(); vindex++) {
                VesselClass* v = Vessels.Ptr(vindex);
                if (v != NULL && !v->IsInLimbo && v->House == this && v->Strength > 0 && v->Is_Weapon_Equipped()
                    && (v->Mission == MISSION_GUARD || v->Mission == MISSION_GUARD_AREA)
                    && Map[Coord_Cell(v->Center_Coord())].Zones[MZONE_WATER] == pzone) {
                    CELL pcell = TF_Naval_Patrol_Cell(pzone);
                    if (pcell) {
                        v->Assign_Mission(MISSION_MOVE);
                        v->Assign_Destination(::As_Target(pcell));
#if TF_DEV_BUILD // TF_AI_DIAG
                        {
                            extern FILE* TF_AI_Diag_File(void);
                            FILE* _tfdbg = TF_AI_Diag_File();
                            if (_tfdbg != NULL) {
                                fprintf(_tfdbg, "F%ld H%d AL%d NAVAL-PATROL %s#%d dest=(%d,%d)\n", (long)Frame,
                                        (int)Class->House, (int)ActLike, v->Class->IniName, (int)v->ID,
                                        (int)Cell_X(pcell), (int)Cell_Y(pcell));
                                fflush(_tfdbg);
                            }
                        }
#endif
                    }
                }
            }
        }
    }

    /*
    **	W5.2: the ferry op state machine -- delivers ground force across water when
    **	the designated enemy is land-unreachable. Gates itself on session/type.
    */
    TF_Ferry_AI();

    /*
    **	If there is no enemy assigned to this house, then assign one now. The
    **	enemy that is closest is picked. However, don't pick an enemy if the
    **	base has not been established yet.
    */
    if (ActiveBScan && Center && Attack == 0) {
        int close = 0;
        HousesType enemy = HOUSE_NONE;
        int maxunit = 0;
        int maxinfantry = 0;
        int maxvessel = 0;
        int maxaircraft = 0;
        int maxbuilding = 0;
        int enemycount = 0;

        for (HousesType house = HOUSE_FIRST; house < HOUSE_COUNT; house++) {
            HouseClass* h = HouseClass::As_Pointer(house);
            if (h != NULL && h->IsActive && !h->IsDefeated && !Is_Ally(h)) {

                /*
                **	Perform a special restriction check to ensure that no enemy is chosen if
                **	there is even one enemy that has not established a base yet. This will
                **	ensure an accurate first pick for enemy since the distance to base
                **	value can be determined.
                */
                if (!h->IsStarted) {
                    enemy = HOUSE_NONE;
                    break;
                }

                /*
                **	Keep track of the number of buildings and units owned by the
                **	enemy. This is used to bring up the maximum allowed to match.
                */
                maxunit += h->CurUnits;
                maxbuilding += h->CurBuildings;
                maxinfantry += h->CurInfantry;
                maxvessel += h->CurVessels;
                maxaircraft += h->CurAircraft;
                enemycount++;

                /*
                **	Determine a priority value based on distance to the center of the
                **	candidate base. The higher the value, the better the candidate house
                **	is to becoming the preferred enemy for this house.
                */
                int value = ((MAP_CELL_W * 2) - Distance(Center, h->Center));
                value *= 2;

                /*
                **	In addition to distance, record the number of kills directed
                **	against this house. The enemy that does more damage might be
                **	considered a greater threat.
                */
                value += h->BuildingsKilled[Class->House] * 5;
                value += h->UnitsKilled[Class->House];

                /*
                **	Factor in the relative sizes of the bases. An enemy that has a
                **	larger base will be considered a bigger threat. Conversely, a
                **	smaller base is considered a lesser threat.
                */
                value += h->CurUnits - CurUnits;
                value += h->CurBuildings - CurBuildings;
                value += (h->CurInfantry - CurInfantry) / 4;

                /*
                **	Whoever last attacked is given a little more priority as
                **	a potential designated enemy.
                */
                if (house == LAEnemy) {
                    value += 100;
                }

#ifdef OBSOLETE
                /*
                **	Human players are a given preference as the target.
                */
                if (h->IsHuman) {
                    value *= 2;
                }
#endif

                /*
                **	Compare the calculated value for this candidate house and if it is
                **	greater than the previously recorded maximum, record this house as
                **	the prime candidate for enemy.
                */
                if (value > close) {
                    enemy = house;
                    close = value;
                }
            }
        }

        /*
        **	Record this closest enemy base as the first enemy to attack.
        */
        Enemy = enemy;

        /*
        **	Up the maximum allowed units and buildings to match a rough average
        **	of what the enemies are allowed.
        */
        if (enemycount) {
            maxunit /= enemycount;
            maxbuilding /= enemycount;
            maxinfantry /= enemycount;
            maxvessel /= enemycount;
            maxaircraft /= enemycount;
        }

        if (Control.MaxBuilding < (unsigned)maxbuilding + 10) {
            Control.MaxBuilding = maxbuilding + 10;
        }
        if (Control.MaxUnit < (unsigned)maxunit + 10) {
            Control.MaxUnit = maxunit + 10;
        }
        if (Control.MaxInfantry < (unsigned)maxinfantry + 10) {
            Control.MaxInfantry = maxinfantry + 10;
        }
        if (Control.MaxVessel < (unsigned)maxvessel + 10) {
            Control.MaxVessel = maxvessel + 10;
        }
        if (Control.MaxAircraft < (unsigned)maxaircraft + 10) {
            Control.MaxAircraft = maxaircraft + 10;
        }
    }

    /*
    **	House state transition check occurs here. Transitions that occur here are ones
    **	that relate to general base condition rather than specific combat events.
    **	Typically, this is limited to transitions between normal buildup mode and
    **	broke mode.
    */
    if (State == STATE_ENDGAME) {
        Fire_Sale();
        Do_All_To_Hunt();
    } else {
        if (State == STATE_BUILDUP) {
            if (Available_Money() < 25) {
                State = STATE_BROKE;
            }
        }
        if (State == STATE_BROKE) {
            if (Available_Money() >= 25) {
                State = STATE_BUILDUP;
            }
        }
        if (State == STATE_ATTACKED && LATime + TICKS_PER_MINUTE < Frame) {
            State = STATE_BUILDUP;
        }
        if (State != STATE_ATTACKED && LATime + TICKS_PER_MINUTE > Frame) {
            State = STATE_ATTACKED;
        }
    }

    /*
    **	Records the urgency of all actions possible.
    */
    UrgencyType urgency[STRATEGY_COUNT];
    StrategyType strat;
    for (strat = STRATEGY_FIRST; strat < STRATEGY_COUNT; strat++) {
        urgency[strat] = URGENCY_NONE;

        switch (strat) {
        case STRATEGY_BUILD_POWER:
            urgency[strat] = Check_Build_Power();
            break;

        case STRATEGY_BUILD_DEFENSE:
            urgency[strat] = Check_Build_Defense();
            break;

        case STRATEGY_BUILD_INCOME:
            urgency[strat] = Check_Build_Income();
            break;

        case STRATEGY_FIRE_SALE:
            urgency[strat] = Check_Fire_Sale();
            break;

        case STRATEGY_BUILD_ENGINEER:
            urgency[strat] = Check_Build_Engineer();
            break;

        case STRATEGY_BUILD_OFFENSE:
            urgency[strat] = Check_Build_Offense();
            break;

        case STRATEGY_RAISE_MONEY:
            urgency[strat] = Check_Raise_Money();
            break;

        case STRATEGY_RAISE_POWER:
            urgency[strat] = Check_Raise_Power();
            break;

        case STRATEGY_LOWER_POWER:
            urgency[strat] = Check_Lower_Power();
            break;

        case STRATEGY_ATTACK:
            urgency[strat] = Check_Attack();
            break;

        default:
            urgency[strat] = URGENCY_NONE;
            break;
        }
    }

    /*
    **	Performs the action required for each of the strategies that share
    **	the most urgent category. Stop processing if any strategy at the
    **	highest urgency performed any action. This is because higher urgency
    **	actions tend to greatly affect the lower urgency actions.
    */
    for (UrgencyType u = URGENCY_CRITICAL; u >= URGENCY_LOW; u--) {
        bool acted = false;

        for (strat = STRATEGY_FIRST; strat < STRATEGY_COUNT; strat++) {
            if (urgency[strat] == u) {
                switch (strat) {
                case STRATEGY_BUILD_POWER:
                    acted |= AI_Build_Power(u);
                    break;

                case STRATEGY_BUILD_DEFENSE:
                    acted |= AI_Build_Defense(u);
                    break;

                case STRATEGY_BUILD_INCOME:
                    acted |= AI_Build_Income(u);
                    break;

                case STRATEGY_FIRE_SALE:
                    acted |= AI_Fire_Sale(u);
                    break;

                case STRATEGY_BUILD_ENGINEER:
                    acted |= AI_Build_Engineer(u);
                    break;

                case STRATEGY_BUILD_OFFENSE:
                    acted |= AI_Build_Offense(u);
                    break;

                case STRATEGY_RAISE_MONEY:
                    acted |= AI_Raise_Money(u);
                    break;

                case STRATEGY_RAISE_POWER:
                    acted |= AI_Raise_Power(u);
                    break;

                case STRATEGY_LOWER_POWER:
                    acted |= AI_Lower_Power(u);
                    break;

                case STRATEGY_ATTACK:
                    acted |= AI_Attack(u);
                    break;

                default:
                    break;
                }
            }
        }
    }

    return (TICKS_PER_SECOND * 5 + Random_Pick(1, TICKS_PER_SECOND / 2));
}

UrgencyType HouseClass::Check_Build_Power(void) const
{
    assert(Houses.ID(this) == ID);

    fixed frac = Power_Fraction();
    UrgencyType urgency = URGENCY_NONE;

    if (frac < 1 && Can_Make_Money()) {
        urgency = URGENCY_LOW;

        /*
        **	Very low power condition is considered a higher priority.
        */
        if (frac < fixed::_3_4)
            urgency = URGENCY_MEDIUM;

        /*
        **	When under attack and there is a need for power in defense
        **	(an armed building present that cannot fire without power),
        **	then consider power building a higher priority.
        */
        if (State == STATE_THREATENED || State == STATE_ATTACKED) {
            for (int i = STRUCT_FIRST; i < STRUCT_COUNT; i++) {
                BuildingTypeClass const& btype = BuildingTypeClass::As_Reference((StructType)i);
                if (btype.IsPowered && btype.PrimaryWeapon != NULL && ActiveBQuantity[i] > 0) {
                    urgency = URGENCY_HIGH;
                    break;
                }
            }
        }
    }
    return (urgency);
}

UrgencyType HouseClass::Check_Build_Defense(void) const
{
    assert(Houses.ID(this) == ID);

    /*
    **	This routine determines what urgency level that base defense
    **	should be given. The more vulnerable the base is, the higher
    **	the urgency this routine should return.
    */
    return (URGENCY_NONE);
}

UrgencyType HouseClass::Check_Build_Offense(void) const
{
    assert(Houses.ID(this) == ID);

    /*
    **	This routine determines what urgency level that offensive
    **	weaponry should be given. Surplus money or a very strong
    **	defense will cause the offensive urgency to increase.
    */
    return (URGENCY_NONE);
}

/*
**	Determines what the attack state of the base is. The higher the state,
**	the greater the immediate threat to base defense is.
*/
UrgencyType HouseClass::Check_Attack(void) const
{
    assert(Houses.ID(this) == ID);

    if (Frame > TICKS_PER_MINUTE && Attack == 0) {
        if (State == STATE_ATTACKED) {
            return (URGENCY_LOW);
        }
        return (URGENCY_CRITICAL);
    }
    return (URGENCY_NONE);
}

UrgencyType HouseClass::Check_Build_Income(void) const
{
    assert(Houses.ID(this) == ID);

    /*
    **	This routine should determine if income processing buildings
    **	should be constructed and at what urgency. The lower the money,
    **	the lower the refineries, or recent harvester losses should
    **	cause a greater urgency to be returned.
    */
    return (URGENCY_NONE);
}

UrgencyType HouseClass::Check_Fire_Sale(void) const
{
    assert(Houses.ID(this) == ID);

    /*
    **	If there are no more factories at all, then sell everything off because the game
    **	is basically over at this point.
    */
    if (State != STATE_ATTACKED && CurBuildings
        && !(ActiveBScan
             & (STRUCTF_TENT | STRUCTF_BARRACKS | STRUCTF_CONST | STRUCTF_AIRSTRIP | STRUCTF_WEAP | STRUCTF_HELIPAD))) {
        return (URGENCY_CRITICAL);
    }
    return (URGENCY_NONE);
}

UrgencyType HouseClass::Check_Build_Engineer(void) const
{
    assert(Houses.ID(this) == ID);

    /*
    **	This routine should check to see what urgency that the production of
    **	engineers should be. If a friendly building has been captured or the
    **	enemy has weak defenses, then building an engineer would be a priority.
    */
    return (URGENCY_NONE);
}

/*
**	Checks to see if money is critically low and something must be done
**	to immediately raise cash.
*/
UrgencyType HouseClass::Check_Raise_Money(void) const
{
    assert(Houses.ID(this) == ID);

    UrgencyType urgency = URGENCY_NONE;
    if (Available_Money() < 100) {
        urgency = URGENCY_LOW;
    }
    if (Available_Money() < 2000 && !Can_Make_Money()) {
        urgency++;
    }

    return (urgency);
}

/*
**	Checks to see if power is very low and if so, a greater urgency to
**	build more power is returned.
*/
UrgencyType HouseClass::Check_Lower_Power(void) const
{
    assert(Houses.ID(this) == ID);

    if (Power > Drain + 300) {
        return (URGENCY_LOW);
    }
    return (URGENCY_NONE);
}

/*
**	This routine determines if there is a power emergency. Such an
**	emergency might require selling of structures in order to free
**	up power. This might occur if the base is being attacked and there
**	are defenses that require power, but are just short of having
**	enough.
*/
UrgencyType HouseClass::Check_Raise_Power(void) const
{
    assert(Houses.ID(this) == ID);

    UrgencyType urgency = URGENCY_NONE;

    if (Power_Fraction() < Rule.PowerEmergencyFraction && Power < Drain - 400) {
        //	if (Power_Fraction() < Rule.PowerEmergencyFraction && (BQuantity[STRUCT_CONST] == 0 || Available_Money() <
        //200 || Power < Drain-400)) {
        urgency = URGENCY_MEDIUM;
        if (State == STATE_ATTACKED) {
            urgency++;
        }
    }
    return (urgency);
}

/*
**	Counts the units this house could actually commit to an attack wave: armed
**	ground units, armed infantry and armed aircraft. Harvesters and MCVs are
**	excluded because sending either is never an attack, and engineers are
**	excluded because they carry no combat power even though a launching wave
**	does take them along.
*/
int HouseClass::TF_Committable_Army(void) const
{
    assert(Houses.ID(this) == ID);

    int army = 0;
    int index;

    for (index = 0; index < Units.Count(); index++) {
        UnitClass const* u = Units.Ptr(index);
        if (u != NULL && !u->IsInLimbo && u->House == this && u->Strength > 0 && u->Is_Weapon_Equipped()
            && !u->Class->IsToHarvest && !u->Class->Is_MCV()) {
            army++;
        }
    }
    for (index = 0; index < Infantry.Count(); index++) {
        InfantryClass const* i = Infantry.Ptr(index);
        if (i != NULL && !i->IsInLimbo && i->House == this && i->Strength > 0 && i->Is_Weapon_Equipped()) {
            army++;
        }
    }
    for (index = 0; index < Aircraft.Count(); index++) {
        AircraftClass const* a = Aircraft.Ptr(index);
        if (a != NULL && !a->IsInLimbo && a->House == this && a->Strength > 0 && a->Is_Weapon_Equipped()) {
            army++;
        }
    }

    return (army);
}

/*
**	Attack-wave pacing dials, keyed off the house IQ (Easy 3, Medium 4,
**	Hard 5). Difficulty moves frequency and responsiveness ONLY: a harder AI
**	looks again sooner, commits more readily and rebuilds its wave faster, so
**	it is more aggressive at every stage of the match rather than merely later
**	and bigger. The floor is deliberately NOT a difficulty dial -- attacking
**	with a token force is incompetence rather than mercy, and since IQ does
**	not gate production (rules.ini [IQ] Production=3) every tier reaches a
**	given army size at much the same minute, so a lower floor would only make
**	the easier AI attack FIRST.
*/
struct TFWaveDialsStruct
{
    int Floor;         // Never launch below this many committable units.
    int Ceiling;       // Always launch at or above this many.
    int MidChance;     // Percent chance of launching between the two.
    int Recheck;       // Frames to wait after declining.
    int IntervalScale; // Percent scale on the post-launch interval.
};

static TFWaveDialsStruct TF_Wave_Dials(int iq)
{
    TFWaveDialsStruct dials;

    if (iq <= 3) {
        dials.Floor = 10;
        dials.Ceiling = 32;
        dials.MidChance = 25;
        dials.Recheck = TICKS_PER_SECOND * 90;
        dials.IntervalScale = 133;
    } else if (iq == 4) {
        dials.Floor = 10;
        dials.Ceiling = 30;
        dials.MidChance = 40;
        dials.Recheck = TICKS_PER_SECOND * 60;
        dials.IntervalScale = 100;
    } else {
        dials.Floor = 10;
        dials.Ceiling = 26;
        dials.MidChance = 60;
        dials.Recheck = TICKS_PER_SECOND * 30;
        dials.IntervalScale = 67;
    }

    return (dials);
}

bool HouseClass::AI_Attack(UrgencyType)
{
    assert(Houses.ID(this) == ID);

    /*
    **	Decide whether this opportunity becomes a wave. Vanilla rolled a flat
    **	33% here and, win or lose, then slept for the full attack interval --
    **	so a declined roll cost minutes and the first wave routinely landed
    **	tens of thousands of frames in. The decision is now conditioned on the
    **	size of the army that could actually be committed: below the floor the
    **	house deliberately holds rather than feeding units in piecemeal, at or
    **	above the ceiling it must commit rather than hoard, and only between
    **	the two does the roll decide. A declined opportunity costs seconds
    **	instead of minutes, because it was declined for a reason that will
    **	change shortly.
    */
    TFWaveDialsStruct dials = TF_Wave_Dials(IQ);
    int army = TF_Committable_Army();

    /*
    **	A house whose economy has been crippled might never reach the floor and
    **	would then sit passive for the rest of the match. Past the decay mark
    **	the floor gives way a unit at a time so that whatever force it has left
    **	eventually commits.
    */
    enum
    {
        TF_WAVE_FLOOR_MIN = 4,
        TF_WAVE_FLOOR_DECAY_START = TICKS_PER_MINUTE * 20,
        TF_WAVE_FLOOR_DECAY_PERIOD = TICKS_PER_MINUTE * 2
    };
    int floor = dials.Floor;
    if (Frame > TF_WAVE_FLOOR_DECAY_START) {
        floor -= (int)((Frame - TF_WAVE_FLOOR_DECAY_START) / TF_WAVE_FLOOR_DECAY_PERIOD);
        if (floor < TF_WAVE_FLOOR_MIN) {
            floor = TF_WAVE_FLOOR_MIN;
        }
    }

    char const* reason;
    bool launch;
    if (Frame > TICKS_PER_MINUTE && !CurBuildings) {
        launch = true;
        reason = "desperation";
    } else if (army >= dials.Ceiling) {
        launch = true;
        reason = "ceiling";
    } else if (army < floor) {
        launch = false;
        reason = "massing";
    } else {
        launch = Percent_Chance(dials.MidChance);
        reason = launch ? "roll" : "roll-declined";
    }
    bool shuffle = !launch;
    bool forced = (CurBuildings == 0);

    /*
    **	Declining now costs seconds rather than minutes, so this routine runs
    **	several times more often than it used to. The idle-guard repositioning
    **	below must not speed up with it: it walks Nearby_Location per unit, and
    **	at recheck cadence the home guard would visibly jitter. Gate it so it
    **	keeps happening about every two minutes whatever the recheck period is.
    */
    bool reposition = launch || Percent_Chance((dials.Recheck * 100) / (TICKS_PER_SECOND * 120));

    /*
    **	How much of the army joins the wave scales with how defended the base
    **	is: a lightly-defended base keeps a real home guard on GUARD_AREA, a
    **	well-fortified one commits everything. Defences are counted
    **	generically (any armed building) so all four factions measure
    **	correctly. (AI Boost 3.2 send-percentage, Bast75 & xXMini FrankiXx.)
    */
    enum
    {
        TF_SEND_PERCENT_LOW = 80,
        TF_SEND_PERCENT_HIGH = 95,
        TF_SEND_SWITCH_LOW_TO_HIGH = 4,
        TF_SEND_SWITCH_HIGH_TO_ALL = 8
    };
    int defences = 0;
    for (int s = STRUCT_FIRST; s < STRUCT_COUNT; s++) {
        if (BuildingTypeClass::As_Reference((StructType)s).PrimaryWeapon != NULL) {
            defences += ActiveBQuantity[s];
        }
    }
    int sendpercent = TF_SEND_PERCENT_LOW;
    if (defences > TF_SEND_SWITCH_HIGH_TO_ALL) {
        sendpercent = 100;
        forced = true;
    } else if (defences > TF_SEND_SWITCH_LOW_TO_HIGH) {
        sendpercent = TF_SEND_PERCENT_HIGH;
    }

#if TF_DEV_BUILD // TF_AI_DIAG -- attack-wave launch: home-defence count drives the send percentage.
    {
        extern FILE* TF_AI_Diag_File(void);
        FILE* _tfdbg = TF_AI_Diag_File();
        if (_tfdbg != NULL) {
            fprintf(_tfdbg,
                    "F%ld H%d AL%d WAVE-%s why=%s army=%d floor=%d ceiling=%d iq=%d defences=%d sendpercent=%d "
                    "forced=%d\n",
                    (long)Frame,
                    (int)Class->House,
                    (int)ActLike,
                    shuffle ? "SHUFFLE (nothing sent)" : "LAUNCH",
                    reason,
                    army,
                    floor,
                    dials.Ceiling,
                    IQ,
                    defences,
                    sendpercent,
                    (int)forced);
            fflush(_tfdbg);
        }
    }
#endif

    int index;
    for (index = 0; index < Aircraft.Count(); index++) {
        AircraftClass* a = Aircraft.Ptr(index);

        if (a != NULL && !a->IsInLimbo && a->House == this && a->Strength > 0) {
            if (!shuffle && a->Is_Weapon_Equipped() && (forced || Percent_Chance(sendpercent))) {
                a->Assign_Mission(MISSION_HUNT);
            }
        }
    }
    for (index = 0; index < Units.Count(); index++) {
        UnitClass* u = Units.Ptr(index);

        if (u != NULL && !u->IsInLimbo && u->House == this && u->Strength > 0) {

            /*
            **	Nudge every ground unit as the wave launches so anything wedged
            **	in base congestion breaks free instead of freezing the wave.
            **	Harvesters are exempt: a forced scatter can yank one off the
            **	dock approach mid-choreography, and the harvester recovery
            **	systems already handle their stuck cases.
            **	(AI Boost 3.2 scatter-on-launch.)
            */
            if (!shuffle && !u->Class->IsToHarvest) {
                u->Scatter(0, true, true);
            }
            if (!shuffle && u->Is_Weapon_Equipped() && (forced || Percent_Chance(sendpercent))) {
                u->Assign_Mission(MISSION_HUNT);
            } else if (!shuffle && u->Is_Weapon_Equipped()) {

                /*
                **	Not sent this wave: stand home guard.
                */
                if (u->Mission != MISSION_GUARD_AREA) {
                    u->Assign_Mission(MISSION_GUARD_AREA);
                }
            } else {

                /*
                **	If this unit is guarding the base, then cause it to shuffle
                **	location instead.
                */
                if (reposition && Percent_Chance(20) && u->Mission == MISSION_GUARD_AREA
                    && Which_Zone(u) != ZONE_NONE) {
                    u->ArchiveTarget = ::As_Target(Where_To_Go(u));
                }
            }
        }
    }
    for (index = 0; index < Infantry.Count(); index++) {
        InfantryClass* i = Infantry.Ptr(index);

        if (i != NULL && !i->IsInLimbo && i->House == this && i->Strength > 0) {

            if (!shuffle) {
                i->Scatter(0, true, true);
            }

            /*
            **	Engineers join the wave so Mission_Hunt can dispatch them to
            **	capture: RENOVATOR is vanilla; TDE6 is the GDI/Nod engineer
            **	and belongs in the same clause.
            */
            if (!shuffle && (i->Is_Weapon_Equipped() || *i == INFANTRY_RENOVATOR || *i == INFANTRY_TDE6)
                && (forced || Percent_Chance(sendpercent))) {
                i->Assign_Mission(MISSION_HUNT);
            } else if (!shuffle && i->Is_Weapon_Equipped()) {

                /*
                **	Not sent this wave: stand home guard.
                */
                if (i->Mission != MISSION_GUARD_AREA) {
                    i->Assign_Mission(MISSION_GUARD_AREA);
                }
            } else {

                /*
                **	If this soldier is guarding the base, then cause it to shuffle
                **	location instead.
                */
                if (reposition && Percent_Chance(20) && i->Mission == MISSION_GUARD_AREA
                    && Which_Zone(i) != ZONE_NONE) {
                    i->ArchiveTarget = ::As_Target(Where_To_Go(i));
                }
            }
        }
    }
    /*
    **	A launched wave takes the full interval to rebuild; a declined one is
    **	rechecked shortly, since the army it was waiting on is still growing.
    **	The launch interval stays keyed to Rule.AttackInterval so the rules.ini
    **	value keeps its authority, scaled by difficulty rather than replaced.
    */
    if (launch) {
        int interval = Rule.AttackInterval * Random_Pick(TICKS_PER_MINUTE / 2, TICKS_PER_MINUTE * 2);
        Attack = (interval * dials.IntervalScale) / 100;
    } else {
        Attack = dials.Recheck;
    }
    return (true);
}

/*
**	Given the specified urgency, build a power structure to meet
**	this need.
*/
bool HouseClass::AI_Build_Power(UrgencyType) const
{
    assert(Houses.ID(this) == ID);

    return (false);
}

/*
**	Given the specified urgency, build base defensive structures
**	according to need and according to existing base disposition.
*/
bool HouseClass::AI_Build_Defense(UrgencyType) const
{
    assert(Houses.ID(this) == ID);

    return (false);
}

/*
**	Given the specified urgency, build offensive units according
**	to need and according to the opponents base defenses.
*/
bool HouseClass::AI_Build_Offense(UrgencyType) const
{
    assert(Houses.ID(this) == ID);

    return (false);
}

/*
**	Given the specified urgency, build income producing
**	structures according to need.
*/
bool HouseClass::AI_Build_Income(UrgencyType) const
{
    assert(Houses.ID(this) == ID);

    return (false);
}

bool HouseClass::AI_Fire_Sale(UrgencyType urgency)
{
    assert(Houses.ID(this) == ID);

    if (CurBuildings && urgency == URGENCY_CRITICAL) {
        Fire_Sale();
        Do_All_To_Hunt();
        return (true);
    }
    return (false);
}

/*
**	Given the specified urgency, build an engineer.
*/
bool HouseClass::AI_Build_Engineer(UrgencyType) const
{
    assert(Houses.ID(this) == ID);

    return (false);
}

/*
**	Given the specified urgency, sell of some power since
**	there appears to be excess.
*/
bool HouseClass::AI_Lower_Power(UrgencyType) const
{
    assert(Houses.ID(this) == ID);

    BuildingClass* b = Find_Building(STRUCT_POWER);
    if (b != NULL) {
        b->Sell_Back(1);
        return (true);
    }

    b = Find_Building(STRUCT_ADVANCED_POWER);
    if (b != NULL) {
        b->Sell_Back(1);
        return (true);
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::AI_Raise_Power -- Try to raise power levels by selling off buildings.           *
 *                                                                                             *
 *    This routine is called when the computer needs to raise power by selling off buildings.  *
 *    Usually this occurs because of some catastrophe that has lowered power levels to         *
 *    the danger zone.                                                                         *
 *                                                                                             *
 * INPUT:   urgency  -- The urgency that the power needs to be raised. This controls what      *
 *                      buildings will be sold.                                                *
 *                                                                                             *
 * OUTPUT:  bool; Was a building sold to raise power?                                          *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   11/02/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::AI_Raise_Power(UrgencyType urgency) const
{
    assert(Houses.ID(this) == ID);

    /*
    **	Sell off structures in this order.
    */
    static struct
    {
        StructType Structure;
        UrgencyType Urgency;
    } _types[] = {{STRUCT_CHRONOSPHERE, URGENCY_LOW},
                  // Naval yards LOW -> HIGH: they are production buildings, and the vanilla
                  // table predates any skirmish AI that could build them -- at LOW, every
                  // mild power dip liquidated a working navy for 30 power. HIGH = attacked
                  // during a power emergency, the genuinely desperate case.
                  {STRUCT_SHIP_YARD, URGENCY_HIGH},
                  {STRUCT_SUB_PEN, URGENCY_HIGH},
                  {STRUCT_ADVANCED_TECH, URGENCY_LOW},
                  {STRUCT_FORWARD_COM, URGENCY_LOW},
                  {STRUCT_SOVIET_TECH, URGENCY_LOW},
                  {STRUCT_IRON_CURTAIN, URGENCY_MEDIUM},
                  {STRUCT_RADAR, URGENCY_MEDIUM},
                  {STRUCT_REPAIR, URGENCY_MEDIUM},
                  {STRUCT_TESLA, URGENCY_HIGH}};

    /*
    **	Find a structure to sell and then sell it. Bail from further scanning until
    **	the next time.
    */
    for (int i = 0; i < ARRAY_SIZE(_types); i++) {
        if (urgency >= _types[i].Urgency) {
            BuildingClass* b = Find_Building(_types[i].Structure);
            if (b != NULL) {
#if TF_DEV_BUILD // TF_AI_DIAG -- every Expert_AI emergency sell, so a vanishing building
                 // is attributable from the log alone.
                {
                    extern FILE* TF_AI_Diag_File(void);
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d EXPERT-SELL %s reason=power urgency=%d\n", (long)Frame,
                                (int)Class->House, (int)ActLike, b->Class->IniName, (int)urgency);
                        fflush(_tfdbg);
                    }
                }
#endif
                b->Sell_Back(1);
                return (true);
            }
        }
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::AI_Raise_Money -- Raise emergency cash by selling buildings.                    *
 *                                                                                             *
 *    This routine handles the situation where the computer desperately needs cash but cannot  *
 *    wait for normal harvesting to raise it. Buildings must be sold.                          *
 *                                                                                             *
 * INPUT:   urgency  -- The urgency level that cash must be raised. The greater the urgency,   *
 *                      the more important the buildings that can be sold become.              *
 *                                                                                             *
 * OUTPUT:  bool; Was a building sold to raise cash?                                           *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   11/02/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::AI_Raise_Money(UrgencyType urgency) const
{
    assert(Houses.ID(this) == ID);

    /*
    **	Sell off structures in this order.
    */
    static struct
    {
        StructType Structure;
        UrgencyType Urgency;
    } _types[] = {{STRUCT_CHRONOSPHERE, URGENCY_LOW},
                  // Naval yards LOW -> MEDIUM: LOW fires on any sub-100 cash dip, which a
                  // producing house hits between every harvester dump -- the skirmish AI's
                  // new yard was being built, sold at half price and rebuilt in a loop.
                  // MEDIUM = broke AND unable to make money, the economy-collapse fire
                  // sale, in the same spirit as the war factory/barracks EA commented out
                  // of this table below.
                  {STRUCT_SHIP_YARD, URGENCY_MEDIUM},
                  {STRUCT_SUB_PEN, URGENCY_MEDIUM},
                  // Tech centres and the repair bay share the yards' reasoning: the build
                  // pool REBUILDS all of them, so LOW (any sub-100 cash dip) is a
                  // sell-at-half/rebuy-at-full churn loop -- the first EXPERT-SELL diag
                  // line ever logged was an Allied AI selling its tech centre. Buildings
                  // the pool never rebuilds (Chronosphere, forward com, silo) stay LOW.
                  {STRUCT_ADVANCED_TECH, URGENCY_MEDIUM},
                  {STRUCT_FORWARD_COM, URGENCY_LOW},
                  {STRUCT_SOVIET_TECH, URGENCY_MEDIUM},
                  {STRUCT_STORAGE, URGENCY_LOW},
                  {STRUCT_REPAIR, URGENCY_MEDIUM},
                  {STRUCT_TESLA, URGENCY_MEDIUM},
                  {STRUCT_HELIPAD, URGENCY_MEDIUM},
                  {STRUCT_POWER, URGENCY_HIGH},
                  {STRUCT_AIRSTRIP, URGENCY_HIGH},
                  //		{STRUCT_WEAP,URGENCY_HIGH},
                  //		{STRUCT_BARRACKS,URGENCY_HIGH},
                  //		{STRUCT_TENT,URGENCY_HIGH},
                  {STRUCT_CONST, URGENCY_CRITICAL}};
    BuildingClass* b = 0;

    /*
    **	Find a structure to sell and then sell it. Bail from further scanning until
    **	the next time.
    */
    for (int i = 0; i < ARRAY_SIZE(_types); i++) {
        if (urgency >= _types[i].Urgency) {
            b = Find_Building(_types[i].Structure);
            if (b != NULL) {
#if TF_DEV_BUILD // TF_AI_DIAG -- every Expert_AI emergency sell, so a vanishing building
                 // is attributable from the log alone.
                {
                    extern FILE* TF_AI_Diag_File(void);
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d EXPERT-SELL %s reason=money urgency=%d\n", (long)Frame,
                                (int)Class->House, (int)ActLike, b->Class->IniName, (int)urgency);
                        fflush(_tfdbg);
                    }
                }
#endif
                b->Sell_Back(1);
                return (true);
            }
        }
    }
    return (false);
}

#ifdef NEVER

/***********************************************************************************************
 * HouseClass::AI_Base_Defense -- Handles maintaining a strong base defense.                   *
 *                                                                                             *
 *    This logic is used to maintain a base defense.                                           *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of game frames to delay before calling this routine again. *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int HouseClass::AI_Base_Defense(void)
{
    assert(Houses.ID(this) == ID);

    /*
    **	Check to find if any zone of the base is over defended. Such zones should have
    **	some of their defenses sold off to make better use of the money.
    */

    /*
    **	Make sure that the core defense is only about 1/2 of the perimeter defense average.
    */
    int average = 0;
    for (ZoneType z = ZONE_NORTH; z < ZONE_COUNT; z++) {
        average += ZoneInfo[z].AirDefense;
        average += ZoneInfo[z].ArmorDefense;
        average += ZoneInfo[z].InfantryDefense;
    }
    average /= (ZONE_COUNT - ZONE_NORTH);

    /*
    **	If the core value is greater than the average, then sell off some of the
    **	inner defensive structures.
    */
    int core = ZoneInfo[ZONE_CORE].AirDefense + ZoneInfo[ZONE_CORE].ArmorDefense + ZoneInfo[ZONE_CORE].InfantryDefense;
    if (core >= average) {
        static StructType _stype[] = {
            STRUCT_GTOWER, STRUCT_TURRET, STRUCT_ATOWER, STRUCT_OBELISK, STRUCT_TESLA, STRUCT_SAM};
        BuildingClass* b;

        for (int index = 0; index < sizeof(_stype) / sizeof(_stype[0]); index++) {
            b = Find_Building(_stype[index], ZONE_CORE);
            if (b) {
                b->Sell_Back(1);
                break;
            }
        }
    }

    /*
    **	If the enemy doesn't have any offensive air capability, then sell off any
    **	SAM sites. Only do this when money is moderately low.
    */
    if (Available_Money() < 1000 && (ActiveBScan & STRUCTF_SAM)) {

        /*
        **	Scan to find if ANY human opponents have aircraft or a helipad. If one
        ** is found then consider that opponent to have a valid air threat potential.
        **	Don't sell off SAM sites in that case.
        */
        bool nothreat = true;
        for (HousesType h = HOUSE_FIRST; h < HOUSE_COUNT; h++) {
            HouseClass* house = HouseClass::As_Pointer(h);

            if (house && house->IsActive && house->IsHuman && !Is_Ally(house)) {
                if ((house->ActiveAScan & (AIRCRAFTF_ORCA | AIRCRAFTF_TRANSPORT | AIRCRAFTF_HELICOPTER))
                    || (house->ActiveBScan & STRUCTF_HELIPAD)) {
                    nothreat = false;
                    break;
                }
            }
        }
    }

    return (TICKS_PER_SECOND * 5);
}
#endif

/***********************************************************************************************
 * Tiberian Factions: skirmish base-builder building substitution.                            *
 *                                                                                             *
 *    AI_Building (below) names concrete RA StructTypes for each base role (power, refinery,   *
 *    barracks, war factory, defence, AA, radar, tech, helipad). GDI (HOUSE_GOOD) and Nod      *
 *    (HOUSE_BAD) own the *separated* TD building set instead, so every vanilla pick fails     *
 *    Can_Build and every BQuantity[] presence-count reads an empty RA slot -- the AI plops    *
 *    its conyard, takes its one free TD harvester, then stalls (a one-building base).         *
 *                                                                                             *
 *    These helpers mirror the Allied/Soviet base-build logic onto the faction's TD            *
 *    buildings: identical ratios / urgency / timing, only the building *type* is swapped.     *
 *    Resolution is by IniName via the heap-aware As_Pointer, cached after first lookup (the   *
 *    same idiom as the Can_Build prereq remap earlier in this file). A role with no TD        *
 *    equivalent returns NULL, so the vanilla pick stands and Can_Build harmlessly skips it    *
 *    for GDI/Nod. Pre-D2 stopgap; the clean fix is a role tag in rules.ini.                   *
 *=============================================================================================*/
static BuildingTypeClass const* TF_Skirmish_Equivalent(StructType ra, HousesType actlike)
{
    if (actlike != HOUSE_GOOD && actlike != HOUSE_BAD) {
        /*
        **	W2 (c): Allied/Soviet skirmish AIs build their own faction's war
        **	factory in place of the vanilla shared WEAP (which Can_Build now
        **	gates to campaign). Everything else stays vanilla for RA houses.
        */
        bool sov = (actlike == HOUSE_USSR || actlike == HOUSE_UKRAINE);
        if (ra == STRUCT_WEAP) {
            return (&BuildingTypeClass::As_Reference(sov ? STRUCT_SWEAP : STRUCT_AWEAP));
        }
        if (ra == STRUCT_HELIPAD) {
            return (&BuildingTypeClass::As_Reference(sov ? STRUCT_SHPAD : STRUCT_AHPAD));
        }
        if (ra == STRUCT_CONST) {
            return (&BuildingTypeClass::As_Reference(sov ? STRUCT_SFACT : STRUCT_AFACT));
        }
        if (ra == STRUCT_SHIP_YARD || ra == STRUCT_SUB_PEN) {
            return (&BuildingTypeClass::As_Reference(sov ? STRUCT_SUB_PEN : STRUCT_SHIP_YARD));
        }
        return (NULL);
    }

    static bool resolved = false;
    static BuildingTypeClass const* c_nuke = NULL; // power plant
    static BuildingTypeClass const* c_nuk2 = NULL; // advanced power plant
    static BuildingTypeClass const* c_proc = NULL; // refinery (both factions)
    static BuildingTypeClass const* c_pyle = NULL; // GDI barracks
    static BuildingTypeClass const* c_hand = NULL; // Nod barracks (Hand of Nod)
    static BuildingTypeClass const* c_weap = NULL; // GDI war factory
    static BuildingTypeClass const* c_afld = NULL; // Nod war factory (Airstrip)
    static BuildingTypeClass const* c_gtwr = NULL; // GDI light defence (Guard Tower)
    static BuildingTypeClass const* c_gun = NULL;  // Nod light defence (Gun Turret)
    static BuildingTypeClass const* c_atwr = NULL; // GDI advanced defence (Adv. Guard Tower)
    static BuildingTypeClass const* c_obli = NULL; // Nod advanced defence (Obelisk)
    static BuildingTypeClass const* c_sam = NULL;  // dedicated AA (SAM site)
    static BuildingTypeClass const* c_hq = NULL;   // radar / comms centre
    static BuildingTypeClass const* c_eye = NULL;  // GDI tech (Adv. Comm)
    static BuildingTypeClass const* c_tmpl = NULL; // Nod tech (Temple of Nod)
    static BuildingTypeClass const* c_hpad = NULL; // helipad (both factions)
    static BuildingTypeClass const* c_gafld = NULL; // GDI fixed-wing airfield (A-10 host)
    static BuildingTypeClass const* c_fix = NULL;  // service depot (both factions)
    static BuildingTypeClass const* c_gyard = NULL; // GDI naval yard
    static BuildingTypeClass const* c_npen = NULL;  // Nod sub pen
    if (!resolved) {
        resolved = true;
        c_nuke = BuildingTypeClass::As_Pointer("TDNUKE");
        c_nuk2 = BuildingTypeClass::As_Pointer("TDNUK2");
        c_proc = BuildingTypeClass::As_Pointer("TDPROC");
        c_pyle = BuildingTypeClass::As_Pointer("TDPYLE");
        c_hand = BuildingTypeClass::As_Pointer("TDHAND");
        c_weap = BuildingTypeClass::As_Pointer("TDWEAP");
        c_afld = BuildingTypeClass::As_Pointer("TDAFLD");
        c_gtwr = BuildingTypeClass::As_Pointer("TDGTWR");
        c_gun = BuildingTypeClass::As_Pointer("TDGUN");
        c_atwr = BuildingTypeClass::As_Pointer("TDATWR");
        c_obli = BuildingTypeClass::As_Pointer("TDOBLI");
        c_sam = BuildingTypeClass::As_Pointer("TDSAM");
        c_hq = BuildingTypeClass::As_Pointer("TDHQ");
        c_eye = BuildingTypeClass::As_Pointer("TDEYE");
        c_tmpl = BuildingTypeClass::As_Pointer("TDTMPL");
        c_hpad = BuildingTypeClass::As_Pointer("TDHPAD");
        c_gafld = BuildingTypeClass::As_Pointer("TDGAFLD");
        c_fix = BuildingTypeClass::As_Pointer("TDFIX");
        c_gyard = BuildingTypeClass::As_Pointer("TDGYARD");
        c_npen = BuildingTypeClass::As_Pointer("TDNPEN");
    }

    bool gdi = (actlike == HOUSE_GOOD);

    switch (ra) {
    case STRUCT_POWER:
        return (c_nuke);
    case STRUCT_ADVANCED_POWER:
        return (c_nuk2);
    case STRUCT_REFINERY:
        return (c_proc);
    case STRUCT_BARRACKS: // Soviet barracks
    case STRUCT_TENT:     // Allied barracks
        return (gdi ? c_pyle : c_hand);
    case STRUCT_WEAP:
        return (gdi ? c_weap : c_afld);
    case STRUCT_PILLBOX: // light base defence
    case STRUCT_CAMOPILLBOX:
    case STRUCT_TURRET:
    case STRUCT_FLAME_TURRET:
        return (gdi ? c_gtwr : c_gun);
    case STRUCT_TESLA: // advanced base defence
        return (gdi ? c_atwr : c_obli);
    case STRUCT_SAM: // dedicated AA -- GDI has no SAM (relies on its towers), so NULL -> skip
    case STRUCT_AAGUN:
        return (gdi ? NULL : c_sam);
    case STRUCT_RADAR:
        return (c_hq);
    case STRUCT_ADVANCED_TECH: // Allied tech
    case STRUCT_SOVIET_TECH:   // Soviet tech
        return (gdi ? c_eye : c_tmpl);
    case STRUCT_HELIPAD:
        // W2 (d): each TD faction builds its own pad now.
        return (gdi ? &BuildingTypeClass::As_Reference(STRUCT_TDGHPAD)
                    : &BuildingTypeClass::As_Reference(STRUCT_TDNHPAD));
    case STRUCT_AIRSTRIP: // GDI fixed-wing airfield (the A-10 host); Nod flies helis only
        return (gdi ? c_gafld : NULL);
    case STRUCT_REPAIR:
        return (c_fix);
    case STRUCT_SHIP_YARD: // naval yard role -- W5.1
    case STRUCT_SUB_PEN:
        return (gdi ? c_gyard : c_npen);
    case STRUCT_CONST:
        // The base builder never queues a construction yard, so this exists for the role
        // table: in Unholy Alliance a house owns one yard of every lineage from the start,
        // which makes the yard the one role where cross-lineage ownership is normal.
        return (gdi ? &BuildingTypeClass::As_Reference(STRUCT_TDGFACT)
                    : &BuildingTypeClass::As_Reference(STRUCT_TDNFACT));
    default:
        // kennel, gap, sub-pen, etc. have no GDI/Nod equivalent for the
        // base-builder (Nod's vehicles come from the TDWEAP/TDAFLD war-factory
        // role above). Leave the vanilla pick; Can_Build rejects it for GDI/Nod
        // and the slot is simply skipped.
        return (NULL);
    }
}

/*
**	Returns the building the skirmish AI should actually queue for a base role: the faction's
**	TD equivalent for GDI/Nod, else the vanilla RA structure. Can_Build still has final say.
*/
static BuildingTypeClass const* TF_Skirmish_Pick(StructType ra, HousesType actlike)
{
    BuildingTypeClass const* sub = TF_Skirmish_Equivalent(ra, actlike);
    return (sub != NULL) ? sub : &BuildingTypeClass::As_Reference(ra);
}

/*
**	Heap Type of the faction's TD equivalent for a base role, or -1 for vanilla houses /
**	unmapped roles. The caller adds BQuantity[<this>] to its existing BQuantity[RA-slot]
**	presence count so the "do I already have one?" gates see the AI's own TD buildings.
*/
static int TF_Skirmish_Type(StructType ra, HousesType actlike)
{
    BuildingTypeClass const* sub = TF_Skirmish_Equivalent(ra, actlike);
    return (sub != NULL) ? (int)sub->Type : -1;
}

/*
**	The vanilla RA sibling that fills the same base role as `ra`, where RA splits a role
**	across two structures. STRUCT_NONE when the role is a single vanilla type.
*/
static StructType TF_Role_Vanilla_Sibling(StructType ra)
{
    switch (ra) {
    case STRUCT_BARRACKS:
        return (STRUCT_TENT);
    case STRUCT_TENT:
        return (STRUCT_BARRACKS);
    case STRUCT_ADVANCED_TECH:
        return (STRUCT_SOVIET_TECH);
    case STRUCT_SOVIET_TECH:
        return (STRUCT_ADVANCED_TECH);
    case STRUCT_SHIP_YARD:
        return (STRUCT_SUB_PEN);
    case STRUCT_SUB_PEN:
        return (STRUCT_SHIP_YARD);
    default:
        return (STRUCT_NONE);
    }
}

/*
**	How many buildings this house owns that fill a base ROLE, counted across EVERY faction
**	lineage rather than just its own. A captured enemy war factory is interchangeable
**	production capacity -- Time_To_Build divides by Factory_Count, so three factories really
**	do build faster than two -- and it must therefore count against what the AI builds for
**	itself. Counting only the home faction's type is why an AI that captures a factory
**	cannot see it and queues a redundant one of its own; in Unholy Alliance, where every
**	house starts with all four MCVs, that misread is continuous.
**
**	CAPACITY ROLES ONLY. An unlock role (tech centre, radar) must NOT come through here:
**	prerequisite clauses are side-scoped on the owner mask, so a captured Nod Temple
**	satisfies none of GDI's clauses. Counting it would fill the "tech centre" role and
**	suppress the AI's own Eye for the rest of the match -- a worse bug than the one this
**	fixes. The test for any role is whether a captured copy does the job the AI would have
**	built its own for: throughput yes, unlocking its own tree no.
*/
static unsigned TF_Role_Quantity(unsigned const* bquantity, StructType ra)
{
    /*
    **	One representative ActLike per lineage. TF_Skirmish_Equivalent keys GDI off
    **	HOUSE_GOOD and Nod off HOUSE_BAD, and maps the RA houses onto their own split
    **	types (AWEAP/SWEAP, AHPAD/SHPAD), so these four cover every tree we can own.
    */
    static const HousesType _lineages[] = {HOUSE_GOOD, HOUSE_BAD, HOUSE_ENGLAND, HOUSE_USSR};

    int seen[8];
    int nseen = 0;
    unsigned total = 0;

    seen[nseen++] = (int)ra;
    total += bquantity[ra];

    StructType sibling = TF_Role_Vanilla_Sibling(ra);
    if (sibling != STRUCT_NONE) {
        seen[nseen++] = (int)sibling;
        total += bquantity[sibling];
    }

    for (int i = 0; i < (int)ARRAY_SIZE(_lineages); i++) {
        int type = TF_Skirmish_Type(ra, _lineages[i]);
        if (type < 0) {
            continue;
        }
        // Roles that share one building across factions (refinery, service depot) resolve
        // to the same type for several lineages -- count each distinct type once.
        bool dup = false;
        for (int s = 0; s < nseen; s++) {
            if (seen[s] == type) {
                dup = true;
                break;
            }
        }
        if (!dup && nseen < (int)ARRAY_SIZE(seen)) {
            seen[nseen++] = type;
            total += bquantity[type];
        }
    }
    return (total);
}

/*
**	Whether this house can still expect credits to arrive: a working refinery,
**	tiberium on the map, and at least one live harvester. Harvesters are counted
**	from the Units heap rather than UQuantity because a docked TD harvester is
**	limboed into its refinery as cargo and drops out of the active count while
**	still earning.
*/
bool HouseClass::TF_Has_Income(void) const
{
    assert(Houses.ID(this) == ID);

    if (IsTiberiumShort || TF_Role_Quantity(BQuantity, STRUCT_REFINERY) == 0) {
        return (false);
    }
    for (int index = 0; index < Units.Count(); index++) {
        UnitClass const* u = Units.Ptr(index);
        if (u != NULL && (HouseClass*)u->House == this && (*u == UNIT_TDHARV || *u == UNIT_HARVESTER)) {
            return (true);
        }
    }
    return (false);
}

/*
**	W5.1 naval tuning. A base further than the coast radius from any shore has no
**	business building a navy, and water smaller than the pond minimum is a pond,
**	not a theatre. Fleet size is governed by TF_Naval_Fleet_Cap: a scouting patrol
**	while no enemy shore is known, then a fleet scaled to the strongest observed
**	enemy navy between the floor (enough presence to bombard a navy-less
**	opponent's shoreline) and the ceiling (where a naval arms race stops paying).
*/
static int const TF_NAVAL_COAST_RADIUS = 20;
static int const TF_NAVAL_POND_MIN = 80;
static int const TF_NAVAL_PATROL_CAP = 2;
static int const TF_NAVAL_FLEET_FLOOR = 4;
static int const TF_NAVAL_FLEET_MAX = 12;

/***********************************************************************************************
 * HouseClass::TF_Naval_Assessment -- Is a navy worth building from this base?                 *
 *                                                                                             *
 *    Finds the best water zone within reach of the base: scans a box around the base center   *
 *    for water cells, keeps the largest zone that is big enough to matter (a pond that can    *
 *    hold a couple of gunboats is not a navy theatre), and reports whether a DISCOVERED       *
 *    enemy building sits coastal on that same water -- the fair-fog signal that ships built   *
 *    there can actually reach something worth shooting. All inputs are deterministic          *
 *    (zones, building positions, the discovery mask), so this is lockstep-safe to consult    *
 *    from AI decision code.                                                                   *
 *                                                                                             *
 * OUTPUT:  true if a qualifying zone exists; zone/size/enemy_coastal describe it.             *
 *=============================================================================================*/
bool HouseClass::TF_Naval_Assessment(int& zone, int& size, bool& enemy_coastal) const
{
    assert(Houses.ID(this) == ID);

    zone = 0;
    size = 0;
    enemy_coastal = false;

    CELL center = Coord_Cell(Center);
    if (center <= 0) {
        return (false);
    }
    int cx = Cell_X(center);
    int cy = Cell_Y(center);

    for (int y = cy - TF_NAVAL_COAST_RADIUS; y <= cy + TF_NAVAL_COAST_RADIUS; y++) {
        for (int x = cx - TF_NAVAL_COAST_RADIUS; x <= cx + TF_NAVAL_COAST_RADIUS; x++) {
            CELL cell = XY_Cell(x, y);
            if (!Map.In_Radar(cell)) {
                continue;
            }
            int wz = Map[cell].Zones[MZONE_WATER];
            if (wz > 0 && wz < ARRAY_SIZE(TF_WaterZoneSize) && TF_WaterZoneSize[wz] >= TF_NAVAL_POND_MIN
                && TF_WaterZoneSize[wz] > size) {
                zone = wz;
                size = TF_WaterZoneSize[wz];
            }
        }
    }
    if (zone == 0) {
        /*
        **	No qualifying water in reach. Distinguish "inland base" from "only ponds
        **	nearby" for the caller's diagnostics: report the largest pond seen (if
        **	any) as a negative size so logs can tell the two apart at a glance.
        */
        int pond = 0;
        for (int y = cy - TF_NAVAL_COAST_RADIUS; y <= cy + TF_NAVAL_COAST_RADIUS; y++) {
            for (int x = cx - TF_NAVAL_COAST_RADIUS; x <= cx + TF_NAVAL_COAST_RADIUS; x++) {
                CELL cell = XY_Cell(x, y);
                if (Map.In_Radar(cell)) {
                    int wz = Map[cell].Zones[MZONE_WATER];
                    if (wz > 0 && wz < ARRAY_SIZE(TF_WaterZoneSize) && TF_WaterZoneSize[wz] > pond) {
                        pond = TF_WaterZoneSize[wz];
                    }
                }
            }
        }
        size = -pond;
        return (false);
    }

    /*
    **	Does a discovered enemy building border the chosen water? Check the ring of
    **	cells around each candidate building's foundation for the zone id. Buildings
    **	are few and foundations small, so this stays cheap at the AI's cadence.
    */
    for (int index = 0; index < Buildings.Count() && !enemy_coastal; index++) {
        BuildingClass const* b = Buildings.Ptr(index);
        if (b == NULL || b->IsInLimbo || b->Strength == 0 || Is_Ally(b)
            || b->House->Class->House == HOUSE_NEUTRAL || !b->Is_Discovered_By_Player(this)) {
            continue;
        }
        CELL bcell = Coord_Cell(b->Center_Coord());
        int bx = Cell_X(bcell);
        int by = Cell_Y(bcell);
        for (int y = by - 2; y <= by + 2 && !enemy_coastal; y++) {
            for (int x = bx - 2; x <= bx + 2; x++) {
                CELL cell = XY_Cell(x, y);
                if (Map.In_Radar(cell) && Map[cell].Zones[MZONE_WATER] == zone) {
                    enemy_coastal = true;
                    break;
                }
            }
        }
    }
    return (true);
}

/***********************************************************************************************
 * HouseClass::TF_Naval_Fleet_Cap -- How many vessels this house should keep afloat.           *
 *                                                                                             *
 *    W5.1 step 4, the naval build gate. While no enemy shore is known the fleet stays a       *
 *    scouting patrol. Once the water demonstrably leads to an enemy, the fleet matches the    *
 *    STRONGEST single opponent's navy -- the same shape as the air-structure cap in           *
 *    AI_Building: max rather than sum, so a multi-enemy game never chases an uncatchable      *
 *    combined total, and matching (no margin) settles once drawn level instead of two AIs     *
 *    ratcheting each other to the ceiling. Only vessels and yards this house has actually     *
 *    discovered count (fair fog); a discovered enemy naval yard is treated as a small fleet   *
 *    on the way, so the response starts when the yard is scouted rather than when its ships   *
 *    arrive. Enemy transports count too -- a ferry fleet is an invasion threat and warships   *
 *    are the counter. The floor keeps enough presence for shore bombardment against a         *
 *    navy-less opponent; the ceiling stops a naval war from eating the whole economy.         *
 *                                                                                             *
 * INPUT:   enemy_coastal -- the TF_Naval_Assessment discovery flag for this house's water;    *
 *          enemy_navy    -- optional out: the strongest single opponent's observed strength.  *
 *                                                                                             *
 * OUTPUT:  Maximum vessels to hold at (compare against CurVessels).                           *
 *=============================================================================================*/
int HouseClass::TF_Naval_Fleet_Cap(bool enemy_coastal, int* enemy_navy) const
{
    assert(Houses.ID(this) == ID);

    if (enemy_navy != NULL) {
        *enemy_navy = 0;
    }
    if (!enemy_coastal) {
        return (TF_NAVAL_PATROL_CAP);
    }

    int navy[HOUSE_COUNT];
    bool yard[HOUSE_COUNT];
    memset(navy, 0, sizeof(navy));
    memset(yard, 0, sizeof(yard));

    for (int index = 0; index < Vessels.Count(); index++) {
        VesselClass const* v = Vessels.Ptr(index);
        if (v != NULL && !v->IsInLimbo && v->Strength > 0 && !Is_Ally(v)
            && v->House->Class->House != HOUSE_NEUTRAL && v->Is_Discovered_By_Player(this)) {
            int h = (int)v->House->Class->House;
            if (h >= 0 && h < HOUSE_COUNT) {
                navy[h]++;
            }
        }
    }
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass const* b = Buildings.Ptr(index);
        if (b == NULL || b->IsInLimbo || b->Strength == 0 || Is_Ally(b)
            || b->House->Class->House == HOUSE_NEUTRAL || !b->Is_Discovered_By_Player(this)) {
            continue;
        }
        StructType t = b->Class->Type;
        if (t == STRUCT_SHIP_YARD || t == STRUCT_SUB_PEN || t == STRUCT_TDGYARD || t == STRUCT_TDNPEN) {
            int h = (int)b->House->Class->House;
            if (h >= 0 && h < HOUSE_COUNT) {
                yard[h] = true;
            }
        }
    }

    int biggest = 0;
    for (HousesType eh = HOUSE_FIRST; eh < HOUSE_COUNT; eh++) {
        HouseClass const* ehp = HouseClass::As_Pointer(eh);
        if (ehp == NULL || !ehp->IsActive || ehp->IsDefeated || Is_Ally(ehp)) {
            continue;
        }
        int fleet = navy[(int)eh];
        if (yard[(int)eh] && fleet < TF_NAVAL_PATROL_CAP) {
            fleet = TF_NAVAL_PATROL_CAP;
        }
        if (fleet > biggest) {
            biggest = fleet;
        }
    }

    if (enemy_navy != NULL) {
        *enemy_navy = biggest;
    }
    if (biggest < TF_NAVAL_FLEET_FLOOR) {
        biggest = TF_NAVAL_FLEET_FLOOR;
    }
    if (biggest > TF_NAVAL_FLEET_MAX) {
        biggest = TF_NAVAL_FLEET_MAX;
    }
    return (biggest);
}

/*
**	W5.2 sea-transport ferrying. One op at a time per house: a transport collects a
**	handful of idle combat units at the home shore, sails them to the enemy's landmass
**	and unloads. Ferrying only engages when the designated enemy is land-unreachable
**	(different MZONE_NORMAL zone) -- on connected maps the ordinary attack waves are
**	the delivery mechanism and a ferry would just be a slower wave. Ops are minimum
**	three passengers: shipping one rifleman across is a waste of a transport's life.
*/
static int const TF_FERRY_ROSTER_MAX = 5;
static int const TF_FERRY_MIN_LOAD = 3;
static int const TF_FERRY_TIMEOUT = 4500;      // pickup / load / unload stall limit (~5 min).
static int const TF_FERRY_SAIL_TIMEOUT = 9000; // crossing limit before the op re-plans.
static int const TF_FERRY_OPS_MAX = 4;         // concurrent transports per house -- the convoy.
static int const TF_FERRY_ESCORTS = 3;         // warships sent ahead to suppress the beach.
static int const TF_FERRY_THREAT_RANGE = 8;    // cells; a defended stretch of coast scores worse.
static int const TF_FERRY_WAVE_MIN = 15;       // beachhead strength that releases the attack wave.
static int const TF_FERRY_WAVE_STALL = 3000;   // no fresh delivery for this long forces a release...
static int const TF_FERRY_WAVE_STALL_MIN = 5;  // ...provided at least this many made it ashore.

struct TFFerryOpStruct
{
    TARGET Transport;
    int State;
    CELL Pickup;
    CELL Landing;
    TARGET Roster[5];
    int RosterCount;
    int Since;
    bool Retried;
};
enum
{
    TFF_IDLE,
    TFF_PICKUP,
    TFF_LOAD,
    TFF_SAIL,
    TFF_UNLOAD
};
static TFFerryOpStruct _tf_ferry[HOUSE_COUNT][TF_FERRY_OPS_MAX];

/*
**	Beachhead assembly state: where landed units rally, and when the last load was
**	put ashore (drives the stall-release so a sunk shuttle can't freeze the wave).
*/
static CELL _tf_beach_rally[HOUSE_COUNT];
static int _tf_beach_delivered[HOUSE_COUNT];

/*
**	Roster eligibility, shared by the candidate census, the roster pick and the
**	transport-demand gate so they can never drift apart: an idle, teamless, armed
**	ground fighter standing on the house's own landmass.
*/
static bool TF_Ferry_Eligible(FootClass const* f, HouseClass const* house, int ourland)
{
    return (f != NULL && (HouseClass const*)f->House == house && !f->IsInLimbo && f->Strength > 0
            && f->Is_Weapon_Equipped() && !f->Team.Is_Valid() && f->Mission == MISSION_GUARD
            && Map[Coord_Cell(f->Center_Coord())].Zones[MZONE_NORMAL] == ourland);
}

/*
**	Best water cell of `wzone` that touches land of `landzone`: the shore point a
**	transport can load or unload across. `nearto` picks among candidates (nearest
**	wins); `avoid` rejects cells near a landing that already failed, so a retry
**	actually tries somewhere else. When `house` is given, coast within range of that
**	house's DISCOVERED armed enemy buildings scores heavily worse, so the convoy
**	lands at the weakest stretch of beach it knows about rather than under the guns.
*/
static CELL TF_Ferry_Shore_Cell(int wzone, int landzone, COORDINATE nearto, CELL avoid, HouseClass const* house)
{
    enum
    {
        THREAT_MAX = 32
    };
    COORDINATE threat[THREAT_MAX];
    int threats = 0;
    if (house != NULL) {
        for (int index = 0; index < Buildings.Count() && threats < THREAT_MAX; index++) {
            BuildingClass const* b = Buildings.Ptr(index);
            if (b != NULL && !b->IsInLimbo && b->Strength > 0 && !house->Is_Ally(b)
                && b->House->Class->House != HOUSE_NEUTRAL && b->Class->PrimaryWeapon != NULL
                && b->Is_Discovered_By_Player(house)) {
                threat[threats++] = b->Center_Coord();
            }
        }
    }

    CELL best = 0;
    int bestd = INT_MAX;
    for (CELL cell = 0; cell < MAP_CELL_TOTAL; cell++) {
        if (!Map.In_Radar(cell) || Map[cell].Zones[MZONE_WATER] != wzone) {
            continue;
        }
        if (avoid != 0 && ::Distance(Cell_Coord(cell), Cell_Coord(avoid)) < 6 * CELL_LEPTON_W) {
            continue;
        }
        bool touches = false;
        for (FacingType f = FACING_N; f < FACING_COUNT; f++) {
            CELL adj = Adjacent_Cell(cell, f);
            if (Map.In_Radar(adj) && Map[adj].Zones[MZONE_NORMAL] == landzone) {
                touches = true;
                break;
            }
        }
        if (!touches) {
            continue;
        }
        int d = ::Distance(Cell_Coord(cell), nearto);
        for (int t = 0; t < threats; t++) {
            int td = ::Distance(Cell_Coord(cell), threat[t]);
            if (td < TF_FERRY_THREAT_RANGE * CELL_LEPTON_W) {
                d += (TF_FERRY_THREAT_RANGE * CELL_LEPTON_W - td) * 4;
            }
        }
        if (d < bestd) {
            bestd = d;
            best = cell;
        }
    }
    return (best);
}

/*
**	W5.3: every MCV hull, RA and TD lineages both.
*/
static bool TF_Is_MCV(UnitClass const* u)
{
    return (*u == UNIT_MCV || *u == UNIT_TDMCV || *u == UNIT_AMCV || *u == UNIT_SMCV || *u == UNIT_TDGMCV
            || *u == UNIT_TDNMCV);
}

/*
**	Is this vessel or foot already committed to another of the house's convoy slots?
*/
static bool TF_Ferry_Claimed(int hidx, int oi, TARGET what)
{
    for (int o2 = 0; o2 < TF_FERRY_OPS_MAX; o2++) {
        if (o2 == oi) {
            continue;
        }
        TFFerryOpStruct const& other = _tf_ferry[hidx][o2];
        if (other.State == TFF_IDLE) {
            continue;
        }
        if (other.Transport == what) {
            return (true);
        }
        for (int i = 0; i < other.RosterCount; i++) {
            if (other.Roster[i] == what) {
                return (true);
            }
        }
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::TF_Ferry_Escort -- Sends warships ahead to suppress the landing beach.          *
 *                                                                                             *
 *    Called when a loaded transport starts its crossing. Idle armed vessels on the same       *
 *    water are ordered to the beachhead ahead of the convoy; their guard-mode weapons         *
 *    engage whatever shore defence or fleet is waiting there, so the transport doesn't        *
 *    arrive first and die alone. The lifetime patrol dispatcher re-adopts the escorts once    *
 *    they go idle again -- no state to track.                                                 *
 *=============================================================================================*/
void HouseClass::TF_Ferry_Escort(CELL landing)
{
    assert(Houses.ID(this) == ID);

    static int const _offx[TF_FERRY_ESCORTS] = {2, -2, 0};
    static int const _offy[TF_FERRY_ESCORTS] = {0, 1, -2};
    int lz = Map[landing].Zones[MZONE_WATER];
    int sent = 0;
    for (int index = 0; index < Vessels.Count() && sent < TF_FERRY_ESCORTS; index++) {
        VesselClass* v = Vessels.Ptr(index);
        if (v == NULL || (HouseClass*)v->House != this || v->IsInLimbo || v->Strength == 0 || !v->Is_Weapon_Equipped()
            || (v->Mission != MISSION_GUARD && v->Mission != MISSION_GUARD_AREA)
            || Map[Coord_Cell(v->Center_Coord())].Zones[MZONE_WATER] != lz) {
            continue;
        }
        CELL station = XY_Cell(Cell_X(landing) + _offx[sent], Cell_Y(landing) + _offy[sent]);
        if (!Map.In_Radar(station) || Map[station].Zones[MZONE_WATER] != lz) {
            station = landing;
        }
        v->Assign_Mission(MISSION_MOVE);
        v->Assign_Destination(::As_Target(station));
        sent++;
#if TF_DEV_BUILD // TF_AI_DIAG
        {
            extern FILE* TF_AI_Diag_File(void);
            FILE* _tfdbg = TF_AI_Diag_File();
            if (_tfdbg != NULL) {
                fprintf(_tfdbg, "F%ld H%d AL%d FERRY-ESCORT %s#%d to=(%d,%d)\n", (long)Frame, (int)Class->House,
                        (int)ActLike, v->Class->IniName, (int)v->ID, (int)Cell_X(station), (int)Cell_Y(station));
                fflush(_tfdbg);
            }
        }
#endif
    }
}

/***********************************************************************************************
 * HouseClass::TF_Ferry_Route_Blocked -- Is the designated enemy land-unreachable?             *
 *                                                                                             *
 *    The ferry trigger: true when this house has a designated enemy whose base sits on a      *
 *    different MZONE_NORMAL landmass, so no ground wave can ever arrive -- the exact          *
 *    condition behind the cliff-massing verdict from the livelock closure. Optionally         *
 *    reports the enemy's land zone for landing-site selection.                                *
 *=============================================================================================*/
bool HouseClass::TF_Ferry_Route_Blocked(int* enemyland) const
{
    assert(Houses.ID(this) == ID);

    if (Enemy == HOUSE_NONE) {
        return (false);
    }
    HouseClass const* ehp = HouseClass::As_Pointer(Enemy);
    if (ehp == NULL || !ehp->IsActive || ehp->IsDefeated) {
        return (false);
    }
    CELL mycell = Coord_Cell(Center);
    CELL ecell = Coord_Cell(ehp->Center);
    if (mycell <= 0 || ecell <= 0) {
        return (false);
    }
    int ours = Map[mycell].Zones[MZONE_NORMAL];
    int theirs = Map[ecell].Zones[MZONE_NORMAL];
    if (ours == theirs) {
        return (false);
    }
    if (enemyland != NULL) {
        *enemyland = theirs;
    }
    return (true);
}

/***********************************************************************************************
 * HouseClass::TF_Ferry_Wants_Transport -- Should AI_Vessel queue an LST?                      *
 *                                                                                             *
 *    True when ferrying is the only way to deliver ground force (route blocked) and the       *
 *    house owns fewer transports than the waiting army justifies: one hull per full load of   *
 *    idle eligible passengers, up to the convoy cap. A house with a big idle army raises a    *
 *    whole landing fleet; a house scraping three riflemen together runs a single shuttle.     *
 *=============================================================================================*/
bool HouseClass::TF_Ferry_Wants_Transport(void) const
{
    assert(Houses.ID(this) == ID);

    if (!TF_Ferry_Route_Blocked()) {
        return (false);
    }
    CELL myc = Coord_Cell(Center);
    if (myc <= 0) {
        return (false);
    }
    int ourland = Map[myc].Zones[MZONE_NORMAL];
    int waiting = 0;
    for (int heap = 0; heap < 2; heap++) {
        int count = heap ? Infantry.Count() : Units.Count();
        for (int index = 0; index < count; index++) {
            FootClass const* f = heap ? (FootClass const*)Infantry.Ptr(index) : (FootClass const*)Units.Ptr(index);
            if (TF_Ferry_Eligible(f, this, ourland)) {
                waiting++;
            }
        }
    }
    int want = (waiting + TF_FERRY_ROSTER_MAX - 1) / TF_FERRY_ROSTER_MAX;
    if (want < 1) {
        want = 1;
    }
    if (want > TF_FERRY_OPS_MAX) {
        want = TF_FERRY_OPS_MAX;
    }
    if (VQuantity[VESSEL_TRANSPORT] >= want) {
        return (false);
    }
    return (Can_Build(&VesselTypeClass::As_Reference(VESSEL_TRANSPORT), ActLike));
}

/***********************************************************************************************
 * HouseClass::TF_Ferry_MCV_Type -- Which MCV hull should this house field?                    *
 *                                                                                             *
 *    The W2 split gave every faction its own MCV; Can_Build picks the right one from the      *
 *    house's tech position. UNIT_NONE when the house can't build one at all (no war           *
 *    factory yet, or tech too low) -- the expansion simply waits.                             *
 *=============================================================================================*/
UnitType HouseClass::TF_Ferry_MCV_Type(void) const
{
    assert(Houses.ID(this) == ID);

    static UnitType const _mcvs[] = {UNIT_AMCV, UNIT_SMCV, UNIT_TDGMCV, UNIT_TDNMCV};
    for (int i = 0; i < (int)ARRAY_SIZE(_mcvs); i++) {
        if (Can_Build(&UnitTypeClass::As_Reference(_mcvs[i]), ActLike)) {
            return (_mcvs[i]);
        }
    }
    return (UNIT_NONE);
}

/***********************************************************************************************
 * HouseClass::TF_Ferry_Wants_MCV -- Should AI_Unit queue the expansion MCV?                   *
 *                                                                                             *
 *    W5.3 trigger: force first, base second. Only once a beachhead exists (a load has been    *
 *    put ashore, so the rally is planted) does the house queue ONE MCV; the ferry gives it    *
 *    the first berth on the next ride and the beachhead sweep deploys it at the rally into    *
 *    the yard that turns the lodgement into a defended forward base. Goes quiet as soon as    *
 *    an MCV exists anywhere (including aboard a transport) or the expansion yard is down.     *
 *=============================================================================================*/
bool HouseClass::TF_Ferry_Wants_MCV(void) const
{
    assert(Houses.ID(this) == ID);

    if (Session.Type == GAME_NORMAL || !IsBaseBuilding) {
        return (false);
    }
    int hidx = (int)Class->House;
    if (hidx < 0 || hidx >= HOUSE_COUNT || _tf_beach_rally[hidx] == 0) {
        return (false);
    }
    int enemyland = 0;
    if (!TF_Ferry_Route_Blocked(&enemyland)) {
        return (false);
    }
    /*
    **	An MCV in limbo is one riding a transport -- still ours, still counts.
    */
    for (int index = 0; index < Units.Count(); index++) {
        UnitClass const* u = Units.Ptr(index);
        if (u != NULL && (HouseClass const*)u->House == this && u->Strength > 0 && TF_Is_MCV(u)) {
            return (false);
        }
    }
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass const* b = Buildings.Ptr(index);
        if (b != NULL && !b->IsInLimbo && (HouseClass const*)b->House == this && b->Strength > 0) {
            StructType t = b->Class->Type;
            if ((t == STRUCT_CONST || t == STRUCT_AFACT || t == STRUCT_SFACT || t == STRUCT_TDFACT
                 || t == STRUCT_TDGFACT || t == STRUCT_TDNFACT)
                && Map[Coord_Cell(b->Center_Coord())].Zones[MZONE_NORMAL] == enemyland) {
                return (false);
            }
        }
    }
    return (TF_Ferry_MCV_Type() != UNIT_NONE);
}

/***********************************************************************************************
 * HouseClass::TF_Ferry_AI -- Runs this house's ferry op state machine.                        *
 *                                                                                             *
 *    Called from Expert_AI each pass. Owns one op at a time: pick shore points, gather a      *
 *    roster of idle combat units, board them via the campaign RADIO_DOCKING handshake (one    *
 *    passenger assigned per pass while the transport is out of radio contact, mirroring      *
 *    TMission_Load), sail, unload on the enemy landmass. Landed units are swept into         *
 *    MISSION_HUNT here too -- that sweep also adopts survivors of any earlier op, so a lost   *
 *    transport never strands a beachhead in guard mode.                                       *
 *=============================================================================================*/
void HouseClass::TF_Ferry_AI(void)
{
    assert(Houses.ID(this) == ID);

    if (Session.Type == GAME_NORMAL || !IsStarted) {
        return;
    }
    int hidx = (int)Class->House;
    if (hidx < 0 || hidx >= HOUSE_COUNT) {
        return;
    }
#if TF_DEV_BUILD // TF_AI_DIAG
    extern FILE* TF_AI_Diag_File(void);
#endif

    /*
    **	Beachhead sweep. Landed fighters don't attack piecemeal -- five units a lift
    **	fed one at a time into a defended base just die in detail. They assemble at
    **	the rally point instead (guard-area, so they defend the lodgement) while the
    **	shuttle pipeline keeps delivering, and the WHOLE force releases as one wave
    **	once it reaches wave strength. The stall clause releases a partial wave when
    **	deliveries stop (shuttles sunk) rather than freezing the beachhead forever.
    **	The sweep also adopts survivors of ops whose transport died.
    */
    CELL myc = Coord_Cell(Center);
    int ourland = (myc > 0) ? Map[myc].Zones[MZONE_NORMAL] : 0;
    int enemyland = 0;
    bool blocked = TF_Ferry_Route_Blocked(&enemyland);
    if (myc > 0 && ourland > 0 && enemyland > 0) {
        int beach = 0;
        for (int heap = 0; heap < 2; heap++) {
            int count = heap ? Infantry.Count() : Units.Count();
            for (int index = 0; index < count; index++) {
                FootClass const* f = heap ? (FootClass const*)Infantry.Ptr(index) : (FootClass const*)Units.Ptr(index);
                if (f != NULL && (HouseClass const*)f->House == this && !f->IsInLimbo && f->Strength > 0
                    && f->Is_Weapon_Equipped()
                    && Map[Coord_Cell(f->Center_Coord())].Zones[MZONE_NORMAL] == enemyland) {
                    beach++;
                }
            }
        }
        bool release = (beach >= TF_FERRY_WAVE_MIN)
                       || (beach >= TF_FERRY_WAVE_STALL_MIN && _tf_beach_delivered[hidx] > 0
                           && (int)Frame - _tf_beach_delivered[hidx] > TF_FERRY_WAVE_STALL);
#if TF_DEV_BUILD // TF_AI_DIAG
        if (release && beach > 0) {
            FILE* _tfdbg = TF_AI_Diag_File();
            if (_tfdbg != NULL) {
                fprintf(_tfdbg, "F%ld H%d AL%d FERRY-WAVE release beach=%d\n", (long)Frame, (int)Class->House,
                        (int)ActLike, beach);
                fflush(_tfdbg);
            }
        }
#endif
        CELL rally = _tf_beach_rally[hidx];
        for (int heap = 0; heap < 2; heap++) {
            int count = heap ? Infantry.Count() : Units.Count();
            for (int index = 0; index < count; index++) {
                FootClass* f = heap ? (FootClass*)Infantry.Ptr(index) : (FootClass*)Units.Ptr(index);
                if (f == NULL || (HouseClass*)f->House != this || f->IsInLimbo || f->Strength == 0
                    || f->Team.Is_Valid()) {
                    continue;
                }
                if (Map[Coord_Cell(f->Center_Coord())].Zones[MZONE_NORMAL] != enemyland) {
                    continue;
                }
                /*
                **	W5.3: an MCV ashore drives to the rally and deploys -- the expansion
                **	yard that turns the lodgement into a defended forward base. It never
                **	joins the attack wave.
                */
                if (heap == 0 && TF_Is_MCV((UnitClass*)f)) {
                    if (f->Mission == MISSION_GUARD) {
                        if (rally != 0 && ::Distance(f->Center_Coord(), Cell_Coord(rally)) > 2 * CELL_LEPTON_W) {
                            f->Assign_Mission(MISSION_MOVE);
                            f->Assign_Destination(::As_Target(rally));
                        } else {
                            f->Assign_Mission(MISSION_UNLOAD);
#if TF_DEV_BUILD // TF_AI_DIAG
                            {
                                FILE* _tfdbg = TF_AI_Diag_File();
                                if (_tfdbg != NULL) {
                                    fprintf(_tfdbg, "F%ld H%d AL%d FERRY-DEPLOY %s#%d at=(%d,%d)\n", (long)Frame,
                                            (int)Class->House, (int)ActLike, f->Class_Of().IniName, (int)f->ID,
                                            (int)Cell_X(Coord_Cell(f->Center_Coord())),
                                            (int)Cell_Y(Coord_Cell(f->Center_Coord())));
                                    fflush(_tfdbg);
                                }
                            }
#endif
                        }
                    }
                    continue;
                }
                if (!f->Is_Weapon_Equipped()) {
                    continue;
                }
                if (release) {
                    if (f->Mission != MISSION_HUNT) {
                        f->Assign_Mission(MISSION_HUNT);
                    }
                } else if (f->Mission == MISSION_GUARD) {
                    if (rally != 0 && ::Distance(f->Center_Coord(), Cell_Coord(rally)) > 3 * CELL_LEPTON_W) {
                        f->Assign_Mission(MISSION_MOVE);
                        f->Assign_Destination(::As_Target(rally));
                    } else {
                        f->Assign_Mission(MISSION_GUARD_AREA);
                    }
                }
            }
        }
    }

    /*
    **	Tick every convoy slot. Each op is an independent transport shuttle; the
    **	slots share one beachhead (later ops adopt the first active landing), so a
    **	multi-transport house arrives as a convoy rather than as scattered raids.
    */
    for (int oi = 0; oi < TF_FERRY_OPS_MAX; oi++) {
        TFFerryOpStruct& op = _tf_ferry[hidx][oi];

        /*
        **	A lost transport voids the op wherever it stood; stragglers still walking to
        **	the dock are released back to guard duty.
        */
        VesselClass* trans = As_Vessel(op.Transport);
        if (op.State != TFF_IDLE
            && (trans == NULL || trans->IsInLimbo || trans->Strength == 0 || (HouseClass*)trans->House != this)) {
            for (int i = 0; i < op.RosterCount; i++) {
                FootClass* f = (FootClass*)As_Techno(op.Roster[i]);
                if (f != NULL && !f->IsInLimbo && f->House == this && f->Mission == MISSION_ENTER) {
                    f->Assign_Mission(MISSION_GUARD);
                }
            }
#if TF_DEV_BUILD // TF_AI_DIAG
            {
                FILE* _tfdbg = TF_AI_Diag_File();
                if (_tfdbg != NULL) {
                    fprintf(_tfdbg, "F%ld H%d AL%d FERRY-ABORT transport-lost state=%d\n", (long)Frame,
                            (int)Class->House, (int)ActLike, op.State);
                    fflush(_tfdbg);
                }
            }
#endif
            op = TFFerryOpStruct();
            trans = NULL;
        }

        switch (op.State) {
        default:
        case TFF_IDLE: {
            if (!blocked || ourland <= 0) {
                break;
            }
            int pzone = 0;
            int psize = 0;
            bool pcoastal = false;
            if (!TF_Naval_Assessment(pzone, psize, pcoastal)) {
                break;
            }
            VesselClass* lst = NULL;
            for (int index = 0; index < Vessels.Count(); index++) {
                VesselClass* v = Vessels.Ptr(index);
                if (v != NULL && v->House == this && *v == VESSEL_TRANSPORT && !v->IsInLimbo && v->Strength > 0
                    && !v->In_Radio_Contact() && (v->Mission == MISSION_GUARD || v->Mission == MISSION_GUARD_AREA)
                    && !TF_Ferry_Claimed(hidx, oi, v->As_Target())) {
                    lst = v;
                    break;
                }
            }
            if (lst == NULL) {
                break; // TF_Ferry_Wants_Transport has AI_Vessel queueing one.
            }
            CELL pick = TF_Ferry_Shore_Cell(pzone, ourland, Center, 0, NULL);
            /*
            **	Later convoy slots land where the first active op is landing -- one
            **	beachhead, massed force -- and only a fresh op surveys the coast.
            */
            CELL land = 0;
            for (int o2 = 0; o2 < TF_FERRY_OPS_MAX; o2++) {
                TFFerryOpStruct const& other = _tf_ferry[hidx][o2];
                if (o2 != oi && other.State != TFF_IDLE && other.Landing != 0) {
                    land = other.Landing;
                    break;
                }
            }
            if (land == 0) {
                land = TF_Ferry_Shore_Cell(pzone, enemyland, Center, 0, this);
            }
            if (pick == 0 || land == 0) {
                break; // enemy landmass doesn't touch our water -- no beachhead exists.
            }
            op.RosterCount = 0;
            /*
            **	W5.3: once the beachhead is holding, the next ride carries the base --
            **	the MCV takes the first berth and the rest of the load is its escort.
            */
            if (_tf_beach_rally[hidx] != 0) {
                for (int index = 0; index < Units.Count(); index++) {
                    UnitClass* u = Units.Ptr(index);
                    if (u != NULL && (HouseClass*)u->House == this && !u->IsInLimbo && u->Strength > 0
                        && TF_Is_MCV(u) && !u->Team.Is_Valid() && u->Mission == MISSION_GUARD
                        && Map[Coord_Cell(u->Center_Coord())].Zones[MZONE_NORMAL] == ourland
                        && !TF_Ferry_Claimed(hidx, oi, u->As_Target())) {
                        op.Roster[op.RosterCount++] = u->As_Target();
                        break;
                    }
                }
            }
            for (int heap = 0; heap < 2 && op.RosterCount < TF_FERRY_ROSTER_MAX; heap++) {
                int count = heap ? Infantry.Count() : Units.Count();
                for (int index = 0; index < count && op.RosterCount < TF_FERRY_ROSTER_MAX; index++) {
                    FootClass* f = heap ? (FootClass*)Infantry.Ptr(index) : (FootClass*)Units.Ptr(index);
                    if (TF_Ferry_Eligible(f, this, ourland) && !TF_Ferry_Claimed(hidx, oi, f->As_Target())) {
                        op.Roster[op.RosterCount++] = f->As_Target();
                    }
                }
            }
            if (op.RosterCount < TF_FERRY_MIN_LOAD) {
                op.RosterCount = 0;
                break;
            }
            op.Transport = lst->As_Target();
            op.Pickup = pick;
            op.Landing = land;
            op.Since = (int)Frame;
            op.Retried = false;
            op.State = TFF_PICKUP;
            lst->Assign_Mission(MISSION_MOVE);
            lst->Assign_Destination(::As_Target(pick));
#if TF_DEV_BUILD // TF_AI_DIAG
            {
                FILE* _tfdbg = TF_AI_Diag_File();
                if (_tfdbg != NULL) {
                    fprintf(_tfdbg, "F%ld H%d AL%d FERRY-START roster=%d pickup=(%d,%d) landing=(%d,%d)\n",
                            (long)Frame, (int)Class->House, (int)ActLike, op.RosterCount, (int)Cell_X(pick),
                            (int)Cell_Y(pick), (int)Cell_X(land), (int)Cell_Y(land));
                    fflush(_tfdbg);
                }
            }
#endif
            break;
        }

        case TFF_PICKUP:
            if (trans->Distance(Cell_Coord(op.Pickup)) <= 2 * CELL_LEPTON_W || trans->Mission == MISSION_GUARD) {
                op.State = TFF_LOAD;
                op.Since = (int)Frame;
            } else if ((int)Frame - op.Since > TF_FERRY_TIMEOUT) {
                op = TFFerryOpStruct();
#if TF_DEV_BUILD // TF_AI_DIAG
                {
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d FERRY-ABORT pickup-stall\n", (long)Frame, (int)Class->House,
                                (int)ActLike);
                        fflush(_tfdbg);
                    }
                }
#endif
            }
            break;

        case TFF_LOAD: {
            int outside = 0;
            if (!trans->In_Radio_Contact()) {
                /*
                **	One boarding assignment per pass while the transport's radio is free --
                **	the TMission_Load discipline. The rest of the roster holds until the
                **	dock clears.
                */
                for (int i = 0; i < op.RosterCount; i++) {
                    FootClass* f = (FootClass*)As_Techno(op.Roster[i]);
                    if (f == NULL || f->IsInLimbo || (HouseClass*)f->House != this || f->Strength == 0) {
                        continue;
                    }
                    outside++;
                    if (f->Mission != MISSION_ENTER) {
                        f->Assign_Mission(MISSION_ENTER);
                        f->Assign_Target(TARGET_NONE);
                        f->Assign_Destination(op.Transport);
                        break;
                    }
                }
            } else {
                for (int i = 0; i < op.RosterCount; i++) {
                    FootClass* f = (FootClass*)As_Techno(op.Roster[i]);
                    if (f != NULL && !f->IsInLimbo && f->House == this && f->Strength > 0) {
                        outside++;
                    }
                }
            }
            int aboard = trans->How_Many();
            bool done = (aboard > 0 && outside == 0);
            bool stalled = ((int)Frame - op.Since > TF_FERRY_TIMEOUT);
            if (done || (stalled && aboard >= 1)) {
                for (int i = 0; i < op.RosterCount; i++) {
                    FootClass* f = (FootClass*)As_Techno(op.Roster[i]);
                    if (f != NULL && !f->IsInLimbo && f->House == this && f->Mission == MISSION_ENTER) {
                        f->Assign_Mission(MISSION_GUARD);
                    }
                }
                trans->Assign_Mission(MISSION_MOVE);
                trans->Assign_Destination(::As_Target(op.Landing));
                op.State = TFF_SAIL;
                op.Since = (int)Frame;
                TF_Ferry_Escort(op.Landing);
#if TF_DEV_BUILD // TF_AI_DIAG
                {
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d FERRY-SAIL op=%d aboard=%d stragglers=%d\n", (long)Frame,
                                (int)Class->House, (int)ActLike, oi, aboard, outside);
                        fflush(_tfdbg);
                    }
                }
#endif
            } else if (stalled) {
                op = TFFerryOpStruct();
#if TF_DEV_BUILD // TF_AI_DIAG
                {
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d FERRY-ABORT load-stall\n", (long)Frame, (int)Class->House,
                                (int)ActLike);
                        fflush(_tfdbg);
                    }
                }
#endif
            }
            break;
        }

        case TFF_SAIL:
            if (trans->Distance(Cell_Coord(op.Landing)) <= 3 * CELL_LEPTON_W || trans->Mission == MISSION_GUARD) {
                trans->Assign_Mission(MISSION_UNLOAD);
                op.State = TFF_UNLOAD;
                op.Since = (int)Frame;
#if TF_DEV_BUILD // TF_AI_DIAG
                {
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d FERRY-UNLOAD at=(%d,%d)\n", (long)Frame, (int)Class->House,
                                (int)ActLike, (int)Cell_X(op.Landing), (int)Cell_Y(op.Landing));
                        fflush(_tfdbg);
                    }
                }
#endif
            } else if ((int)Frame - op.Since > TF_FERRY_SAIL_TIMEOUT) {
                trans->Assign_Mission(MISSION_MOVE);
                trans->Assign_Destination(::As_Target(op.Landing));
                op.Since = (int)Frame;
            }
            break;

        case TFF_UNLOAD:
            if (trans->How_Many() == 0 && trans->Mission != MISSION_UNLOAD) {
                /*
                **	Load ashore. Stamp the delivery (feeds the stall-release) and plant
                **	the beachhead rally on the land side of this landing so the sweep
                **	gathers arrivals in one place.
                */
                _tf_beach_delivered[hidx] = (int)Frame;
                for (FacingType face = FACING_N; face < FACING_COUNT; face++) {
                    CELL adj = Adjacent_Cell(op.Landing, face);
                    if (Map.In_Radar(adj) && Map[adj].Zones[MZONE_NORMAL] == enemyland) {
                        _tf_beach_rally[hidx] = adj;
                        break;
                    }
                }
                op = TFFerryOpStruct();
#if TF_DEV_BUILD // TF_AI_DIAG
                {
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d FERRY-DONE\n", (long)Frame, (int)Class->House, (int)ActLike);
                        fflush(_tfdbg);
                    }
                }
#endif
            } else if ((int)Frame - op.Since > TF_FERRY_TIMEOUT) {
                if (!op.Retried) {
                    /*
                    **	Beach blocked (Desired_Load_Dir keeps finding no free cell). Re-plan
                    **	toward the enemy base instead of toward home -- a different metric
                    **	lands a genuinely different stretch of coast -- and steer clear of
                    **	the failed spot.
                    */
                    op.Retried = true;
                    HouseClass const* ehp = HouseClass::As_Pointer(Enemy);
                    COORDINATE nearto = (ehp != NULL && ehp->IsActive) ? ehp->Center : Center;
                    CELL land = TF_Ferry_Shore_Cell(Map[Coord_Cell(trans->Center_Coord())].Zones[MZONE_WATER],
                                                    enemyland, nearto, op.Landing, this);
                    if (land != 0) {
                        op.Landing = land;
                        trans->Assign_Mission(MISSION_MOVE);
                        trans->Assign_Destination(::As_Target(land));
                        op.State = TFF_SAIL;
                        op.Since = (int)Frame;
                        TF_Ferry_Escort(land);
#if TF_DEV_BUILD // TF_AI_DIAG
                        {
                            FILE* _tfdbg = TF_AI_Diag_File();
                            if (_tfdbg != NULL) {
                                fprintf(_tfdbg, "F%ld H%d AL%d FERRY-RELAND to=(%d,%d)\n", (long)Frame,
                                        (int)Class->House, (int)ActLike, (int)Cell_X(land), (int)Cell_Y(land));
                                fflush(_tfdbg);
                            }
                        }
#endif
                        break;
                    }
                }
                trans->Assign_Mission(MISSION_GUARD);
                op = TFFerryOpStruct();
#if TF_DEV_BUILD // TF_AI_DIAG
                {
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d FERRY-ABORT unload-stuck\n", (long)Frame, (int)Class->House,
                                (int)ActLike);
                        fflush(_tfdbg);
                    }
                }
#endif
            }
            break;
        }
    }
}

/***********************************************************************************************
 * HouseClass::AI_Building -- Determines what building to build.                               *
 *                                                                                             *
 *    This routine handles the general case of determining what building to build next.        *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of game frames to delay before calling this routine again. *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/29/1995 JLB : Created.                                                                 *
 *   11/03/1996 JLB : Tries to match aircraft of enemy                                         *
 *=============================================================================================*/
#if TF_DEV_BUILD // TF_AI_DIAG -- shared log file for the AI diagnostics (also used from foot.cpp).
TFPlaceScanStruct TF_PlaceScan = {0, 0, 0, 0, 0, 0, 0};

FILE* TF_AI_Diag_File(void)
{
    static FILE* f = NULL;
    static bool tried = false;
    if (!tried) {
        tried = true;
        const char* up = getenv("USERPROFILE");
        char p[600];
        snprintf(p, sizeof(p), "%s/MOD_DEBUG_AI.txt", up ? up : ".");
        f = fopen(p, "a");
        if (f != NULL) {
            fprintf(f, "=== TF_AI_DIAG v3 (build-choice pool) ===\n");
        }
    }
    return (f);
}
#endif

int HouseClass::AI_Building(void)
{
    assert(Houses.ID(this) == ID);

    if (BuildStructure != STRUCT_NONE)
        return (TICKS_PER_SECOND);

    if (Session.Type == GAME_NORMAL && Base.House == Class->House) {
        BaseNodeClass* node = Base.Next_Buildable();
        if (node) {
            BuildStructure = node->Type;
        }
    }

    if (IsBaseBuilding) {
        /*
        **	Don't suggest anything to build if the base is already big enough.
        */
        unsigned int quant = 0;
        for (HousesType h = HOUSE_FIRST; h < HOUSE_COUNT; h++) {
            HouseClass const* hptr = HouseClass::As_Pointer(h);

            if (hptr != NULL && hptr->IsActive && hptr->IsHuman && quant < hptr->CurBuildings) {
                quant = hptr->CurBuildings;
            }
        }
        quant += Rule.BaseSizeAdd;

        // TCTC -- Should multiply largest player base by some rational number.
        //		if (CurBuildings >= quant) return(TICKS_PER_SECOND);

        BuildChoice.Free_All();
        BuildChoiceClass* choiceptr;
        StructType stype = STRUCT_NONE;
        int money = Available_Money();
        int level = Control.TechLevel;
        bool tf_td = (ActLike == HOUSE_GOOD || ActLike == HOUSE_BAD);
        unsigned tf_refqty = TF_Role_Quantity(BQuantity, STRUCT_REFINERY);
        // GDI/Nod tier-2 economy gate, shared by the comm centre, the tech centre and the
        // repair bay. Each is affordable long before it is affordable *and* worth having,
        // and the vanilla urgencies race them against the war factory, so a house can tech
        // up while still on one harvester's income and never field an army. Requiring an
        // expanded economy first orders the build as refinery -> production -> tech.
        // The refinery branch below is hard-blocked while tiberium is short, so a house on
        // a depleted map can never reach the second refinery. Treat that as satisfying the
        // economy requirement rather than locking the upper tier away for the whole match.
        unsigned tf_weapqty = TF_Role_Quantity(BQuantity, STRUCT_WEAP);
        bool tf_economy_ready = ((tf_refqty >= 2 || IsTiberiumShort) && tf_weapqty >= 1);
        // Tiberian Factions: count harvesters the RELIABLE way. UQuantity reads 0 even
        // with live, earning harvesters because a TD harvester docking at its refinery is
        // Limbo()'d + Attach()'d into the building as cargo (unit.cpp ~1830) -> dropped
        // from the active UQuantity count. But it's still a live object in the Units heap,
        // so we scan that: a docked harvester still counts, while a *destroyed* harvester
        // is gone from the heap and reads 0. So hasincome stays true while harvesters
        // merely dock, but correctly goes false if the faction's harvesters are all wiped
        // out (the UQuantity term couldn't tell those two cases apart -- both read 0).
        int tf_harv_count = 0;
        for (int hindex = 0; hindex < Units.Count(); hindex++) {
            UnitClass const* hu = Units.Ptr(hindex);
            if (hu != NULL && (HouseClass*)hu->House == this && (*hu == UNIT_TDHARV || *hu == UNIT_HARVESTER)) {
                tf_harv_count++;
            }
        }
        bool hasincome = (tf_refqty > 0 && !IsTiberiumShort && tf_harv_count > 0);

#if TF_DEV_BUILD // TF_AI_DIAG -- AI economy decision logging (compiled out of release)
        /*
        **	Sample on a per-house schedule rather than `Frame % 90`. AI_Building runs on its
        **	own returned delay, so a frame-modulo test only fires when the two happen to
        **	coincide -- which yielded 3 samples in a whole match. Track the next due frame
        **	per house so every house reports at a steady interval whatever its call cadence.
        */
        static int _tf_diag_due[HOUSE_COUNT] = {0};
        int _tf_h = (int)Class->House;
        bool _tf_diag_now = tf_td && _tf_h >= 0 && _tf_h < HOUSE_COUNT && (int)Frame >= _tf_diag_due[_tf_h];
        if (_tf_diag_now) {
            _tf_diag_due[_tf_h] = (int)Frame + 450; // ~30s of game time
        }
        if (_tf_diag_now) {
            FILE* _tfdbg = TF_AI_Diag_File();
            if (_tfdbg != NULL) {
                static char const* _bn[9] =
                    {"TDPROC", "TDHAND", "TDWEAP", "TDNUK", "TDNUK2", "TDFACT", "TDTMPL", "TDEYE", "TDSTEAL"};
                fprintf(_tfdbg,
                        "F%ld H%d AL%d base=%d Tech=%d $%d Pow=%d Drain=%d PF<1=%d CurB=%d Rad=%d hasinc=%d refQ=%d "
                        "harvQ=%d tibShort=%d ABScan=%08X | ROLE yard=%d/%d weap=%d/%d barr=%d/%d hpad=%d/%d "
                        "fix=%d/%d |",
                        (long)Frame, (int)Class->House, (int)ActLike, (int)IsBaseBuilding, (int)Control.TechLevel,
                        (int)Available_Money(), (int)Power, (int)Drain, (int)(Power_Fraction() < 1),
                        (int)CurBuildings, (int)Radius, (int)hasincome, (int)tf_refqty, (int)tf_harv_count,
                        (int)IsTiberiumShort, (unsigned)ActiveBScan,
                        /*
                        **	Aggregate role count vs the home-faction-only count it replaced.
                        **	A gap between the two means this house holds a role building from
                        **	another lineage (captured, or an Unholy Alliance start) -- exactly
                        **	the case that used to go unseen and provoke a redundant build.
                        */
                        (int)TF_Role_Quantity(BQuantity, STRUCT_CONST),
                        (int)(BQuantity[STRUCT_CONST]
                              + (TF_Skirmish_Type(STRUCT_CONST, ActLike) >= 0
                                     ? BQuantity[TF_Skirmish_Type(STRUCT_CONST, ActLike)]
                                     : 0)),
                        (int)TF_Role_Quantity(BQuantity, STRUCT_WEAP),
                        (int)(BQuantity[STRUCT_WEAP]
                              + (TF_Skirmish_Type(STRUCT_WEAP, ActLike) >= 0
                                     ? BQuantity[TF_Skirmish_Type(STRUCT_WEAP, ActLike)]
                                     : 0)),
                        (int)TF_Role_Quantity(BQuantity, STRUCT_BARRACKS),
                        (int)(BQuantity[STRUCT_BARRACKS] + BQuantity[STRUCT_TENT]
                              + (TF_Skirmish_Type(STRUCT_BARRACKS, ActLike) >= 0
                                     ? BQuantity[TF_Skirmish_Type(STRUCT_BARRACKS, ActLike)]
                                     : 0)),
                        (int)TF_Role_Quantity(BQuantity, STRUCT_HELIPAD),
                        (int)(BQuantity[STRUCT_HELIPAD]
                              + (TF_Skirmish_Type(STRUCT_HELIPAD, ActLike) >= 0
                                     ? BQuantity[TF_Skirmish_Type(STRUCT_HELIPAD, ActLike)]
                                     : 0)),
                        (int)TF_Role_Quantity(BQuantity, STRUCT_REPAIR),
                        (int)(BQuantity[STRUCT_REPAIR]
                              + (TF_Skirmish_Type(STRUCT_REPAIR, ActLike) >= 0
                                     ? BQuantity[TF_Skirmish_Type(STRUCT_REPAIR, ActLike)]
                                     : 0)));
                for (int _i = 0; _i < 9; _i++) {
                    BuildingTypeClass const* _bt = BuildingTypeClass::As_Pointer(_bn[_i]);
                    fprintf(_tfdbg, " %s(cb=%d,q=%d)", _bn[_i],
                            _bt != NULL ? (int)Can_Build(_bt, ActLike) : -2,
                            _bt != NULL ? (int)BQuantity[_bt->Type] : -2);
                }
                fprintf(_tfdbg, "\n");
                fflush(_tfdbg);
            }
        }

        /*
        **	W5.1 naval groundwork diag: what the water evaluation would tell the
        **	(future) naval production code, on its own 30s schedule and for EVERY
        **	computer house -- the RA factions are the naval-heavy ones, and the
        **	economy diag above is TD-era-gated. Verifies the zone census + coastal
        **	assessment from logs alone, before any behaviour is wired to it.
        */
        {
            static int _tf_nav_due[HOUSE_COUNT] = {0};
            int _tf_nh = (int)Class->House;
            if (!IsHuman && _tf_nh >= 0 && _tf_nh < HOUSE_COUNT && (int)Frame >= _tf_nav_due[_tf_nh]) {
                _tf_nav_due[_tf_nh] = (int)Frame + 450;
                FILE* _tfdbg = TF_AI_Diag_File();
                if (_tfdbg != NULL) {
                    /*
                    **	One census line per match (the DLL reloads per match, so the
                    **	static resets): every water zone's size, to sanity-check the
                    **	histogram against the visible map before trusting ok=0 lines.
                    */
                    static bool _tf_census_done = false;
                    if (!_tf_census_done) {
                        _tf_census_done = true;
                        fprintf(_tfdbg, "NAVAL-CENSUS wzones=%d", (int)TF_WaterZoneCount);
                        for (int _z = 1; _z <= TF_WaterZoneCount && _z < 256; _z++) {
                            fprintf(_tfdbg, " z%d=%d", _z, TF_WaterZoneSize[_z]);
                        }
                        fprintf(_tfdbg, "\n");
                    }
                    int _nz = 0, _nsz = 0;
                    bool _nec = false;
                    bool _nok = TF_Naval_Assessment(_nz, _nsz, _nec);
                    CELL _nc = Coord_Cell(Center);
                    fprintf(_tfdbg,
                            "F%ld H%d AL%d NAVAL ok=%d zone=%d size=%d enemycoastal=%d center=(%d,%d) wzones=%d\n",
                            (long)Frame, (int)Class->House, (int)ActLike, (int)_nok, _nz, _nsz, (int)_nec,
                            (int)Cell_X(_nc), (int)Cell_Y(_nc), (int)TF_WaterZoneCount);
                    fflush(_tfdbg);
                }
            }
        }
#endif
        BuildingTypeClass const* b = NULL;
        HouseClass const* enemy = NULL;
        if (Enemy != HOUSE_NONE) {
            enemy = HouseClass::As_Pointer(Enemy);
        }

        /*
        **	Tiberian Factions: air-build count cap. Vanilla capped the airfield/helipad count off
        **	the single designated Enemy only, so a human (or any non-designated opponent) building
        **	an air force was invisible to it. Scan every non-allied active house (all humans
        **	included) and mirror the STRONGEST single air opponent's air-structure count for the
        **	cap. Max (not a sum) on purpose: summing every enemy's structures would make each AI
        **	chase a combined multi-enemy total it can never catch. Matching the biggest single
        **	opponent settles once drawn level. (Air-build *urgency* is deliberately LOW below, so
        **	this governs the eventual amount, not the priority -- see the helipad/airstrip blocks.)
        */
        int enemy_airstrips = 0;
        int enemy_helipads = 0;
        for (HousesType eh = HOUSE_FIRST; eh < HOUSE_COUNT; eh++) {
            HouseClass const* ehp = HouseClass::As_Pointer(eh);
            if (ehp != NULL && ehp->IsActive && !ehp->IsDefeated && !Is_Ally(ehp)) {
                int afld = ehp->BQuantity[STRUCT_AIRSTRIP] + ehp->BQuantity[STRUCT_TDGAFLD];
                int hpad = ehp->BQuantity[STRUCT_HELIPAD] + ehp->BQuantity[STRUCT_TDHPAD]
                           + ehp->BQuantity[STRUCT_AHPAD] + ehp->BQuantity[STRUCT_SHPAD]
                           + ehp->BQuantity[STRUCT_TDGHPAD] + ehp->BQuantity[STRUCT_TDNHPAD];
                if (afld > enemy_airstrips) enemy_airstrips = afld;
                if (hpad > enemy_helipads) enemy_helipads = hpad;
            }
        }

        level = Control.TechLevel;

        /*
        **	Try to build a power plant if there is insufficient power and there is enough
        **	money available.
        */
        b = TF_Skirmish_Pick(STRUCT_ADVANCED_POWER, ActLike);
        if (Can_Build(b, ActLike) && Power <= Drain + Rule.PowerSurplus && (b->Cost_Of() < money || hasincome)) {
            choiceptr = BuildChoice.Alloc();
            if (choiceptr != NULL) {
                *choiceptr = BuildChoiceClass(tf_refqty == 0 ? URGENCY_LOW : URGENCY_MEDIUM, b->Type);
            }
        } else {
            b = TF_Skirmish_Pick(STRUCT_POWER, ActLike);
            if (Can_Build(b, ActLike) && Power <= Drain + Rule.PowerSurplus && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(tf_refqty == 0 ? URGENCY_LOW : URGENCY_MEDIUM, b->Type);
                }
            }
        }

        /*
        **	Build a refinery if there isn't one already available.
        */
        unsigned int current = tf_refqty;
        if (!IsTiberiumShort && current < Round_Up(Rule.RefineryRatio * fixed(CurBuildings))
            && current < (unsigned)Rule.RefineryLimit) {
            b = TF_Skirmish_Pick(STRUCT_REFINERY, ActLike);
            if (Can_Build(b, ActLike) && (money > b->Cost_Of() || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(tf_refqty == 0 ? URGENCY_HIGH : URGENCY_MEDIUM, b->Type);
                }
            }
        }

        /*
        **	Always make sure there is a barracks available, but only if there
        **	will be sufficient money to train troopers.
        */
        current = TF_Role_Quantity(BQuantity, STRUCT_BARRACKS);
        if (current < Round_Up(Rule.BarracksRatio * fixed(CurBuildings)) && current < (unsigned)Rule.BarracksLimit
            && (money > 300 || hasincome)) {
            b = TF_Skirmish_Pick(STRUCT_BARRACKS, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(current > 0 ? URGENCY_LOW : URGENCY_MEDIUM, b->Type);
                }
            } else {
                b = &BuildingTypeClass::As_Reference(STRUCT_TENT);
                if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                    choiceptr = BuildChoice.Alloc();
                    if (choiceptr != NULL) {
                        *choiceptr = BuildChoiceClass(current > 0 ? URGENCY_LOW : URGENCY_MEDIUM, b->Type);
                    }
                }
            }
        }

        /*
        **	Try to build one dog house.
        */
        current = BQuantity[STRUCT_KENNEL];
        if (current < 1 && (money > 300 || hasincome)) {
            b = &BuildingTypeClass::As_Reference(STRUCT_KENNEL);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                }
            }
        }

        /*
        **	Try to build one gap generator.
        */
        current = BQuantity[STRUCT_GAP];
        if (current < 1 && Power_Fraction() >= 1 && hasincome) {
            b = &BuildingTypeClass::As_Reference(STRUCT_GAP);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                }
            }
        }

        /*
        **	Nod: build one Stealth Generator once the Temple of Nod is up (Can_Build enforces
        **	the TDTMPL prerequisite). The vanilla gap-generator slot above is an Allied building
        **	a Nod house can't build, so our own STRUCT_TDSTEALTH gets its own slot. Gated on full
        **	power and income so cloaking the base never comes at the cost of the economy.
        */
        if (ActLike == HOUSE_BAD) {
            current = BQuantity[STRUCT_TDSTEALTH];
            if (current < 1 && Power_Fraction() >= 1 && hasincome) {
                b = &BuildingTypeClass::As_Reference(STRUCT_TDSTEALTH);
                if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                    choiceptr = BuildChoice.Alloc();
                    if (choiceptr != NULL) {
                        *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                    }
                }
            }
        }

        /*
        **	A source of combat vehicles is always needed, but only if there will
        **	be sufficient money to build vehicles.
        */
        current = TF_Role_Quantity(BQuantity, STRUCT_WEAP);
        if (current < Round_Up(Rule.WarRatio * fixed(CurBuildings)) && current < (unsigned)Rule.WarLimit
            && (money > 2000 || hasincome)) {
            b = TF_Skirmish_Pick(STRUCT_WEAP, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(current > 0 ? URGENCY_LOW : URGENCY_MEDIUM, b->Type);
                }
            }
        }

        /*
        **  Tiberian Factions: GDI/Nod tech gate. TDHQ (radar/comms) is the
        **  prerequisite for advanced defence (TDATWR/TDOBLI) and the tech
        **  centres (TDEYE/TDTMPL), but the vanilla AI builds radar only
        **  reactively under air threat -- so GDI/Nod never tech up, the whole
        **  upper tier (incl. superweapon hosts) stays unreachable, and that
        **  starves CurBuildings and thus every ratio-driven count below. Build
        **  it proactively (GDI/Nod only) once the refinery (TDHQ's own prereq)
        **  and power are up.
        */
        if (tf_td) {
            int tf_hq = TF_Skirmish_Type(STRUCT_RADAR, ActLike);
            current = BQuantity[STRUCT_RADAR] + (tf_hq >= 0 ? BQuantity[tf_hq] : 0);
            if (current < 1 && tf_economy_ready && Power_Fraction() >= 1) {
                b = TF_Skirmish_Pick(STRUCT_RADAR, ActLike);
                if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                    choiceptr = BuildChoice.Alloc();
                    if (choiceptr != NULL) {
                        *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                    }
                }
            }

            /*
            **  Service depot (TDFIX): vehicle repair + prerequisite for the
            **  GDI Mammoth Tank. Vanilla's repair-bay build is #ifdef OLD, so
            **  this is the GDI/Nod-only revival.
            */
            current = TF_Role_Quantity(BQuantity, STRUCT_REPAIR);
            // A repair bay only pays for itself once there are vehicles to repair, so it
            // shares the economy gate above. That gate lives here rather than in the
            // urgency because URGENCY_LOW is never reached at all (the consumer builds one
            // highest-urgency pick per cycle and the defense branch holds MEDIUM), which
            // would strand the GDI Mammoth behind a prerequisite that never gets built.
            if (current < 1 && tf_economy_ready && Power_Fraction() >= 1) {
                b = TF_Skirmish_Pick(STRUCT_REPAIR, ActLike);
                if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                    choiceptr = BuildChoice.Alloc();
                    if (choiceptr != NULL) {
                        // The build-choice consumer (~house.cpp:6715) builds only the single
                        // HIGHEST-urgency pick per cycle, and the defense branch stays MEDIUM
                        // as long as CurBuildings grows -- so URGENCY_LOW was permanently
                        // outranked and the repair bay never got built. For GDI that's fatal:
                        // the Mammoth Tank is prereq-gated on TDFIX, so no repair bay = no
                        // Mammoths ever. Promote it to HIGH for GDI (unlock the tier promptly;
                        // current<1 makes it a one-shot, no spam) and MEDIUM for Nod (gets
                        // built like the radar, but nothing is gated on it).
                        *choiceptr = BuildChoiceClass(ActLike == HOUSE_GOOD ? URGENCY_HIGH : URGENCY_MEDIUM, b->Type);
                    }
                }
            }
        }

        /*
        **	Always build up some base defense.
        */
        int tf_def = TF_Skirmish_Type(STRUCT_FLAME_TURRET, ActLike);
        current = BQuantity[STRUCT_PILLBOX] + BQuantity[STRUCT_CAMOPILLBOX] + BQuantity[STRUCT_TURRET]
                  + BQuantity[STRUCT_FLAME_TURRET] + BQuantity[STRUCT_TDFBNK] + (tf_def >= 0 ? BQuantity[tf_def] : 0);
        if (current < Round_Up(Rule.DefenseRatio * fixed(CurBuildings)) && current < (unsigned)Rule.DefenseLimit) {
            /*
            **  Nod fields BOTH its anti-armor Turret (tf_def -> TDGUN) and its anti-infantry
            **  Flame Bunker. Interleave them: build a Flame Bunker whenever Nod has strictly
            **  fewer bunkers than turrets, so the defence budget alternates turret, bunker,
            **  turret, ... Can_Build enforces the Hand of Nod prerequisite; before it's up (or
            **  for GDI, which can't build the bunker) this falls through to the normal pick.
            */
            b = NULL;
            if (ActLike == HOUSE_BAD && tf_def >= 0
                && (unsigned)BQuantity[STRUCT_TDFBNK] < (unsigned)BQuantity[tf_def]) {
                BuildingTypeClass const* fb = &BuildingTypeClass::As_Reference(STRUCT_TDFBNK);
                if (Can_Build(fb, ActLike)) {
                    b = fb;
                }
            }
            if (b == NULL) {
                b = TF_Skirmish_Pick(STRUCT_FLAME_TURRET, ActLike);
            }
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                }
            } else {
                if (Percent_Chance(50)) {
                    b = &BuildingTypeClass::As_Reference(STRUCT_PILLBOX);
                    if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                        choiceptr = BuildChoice.Alloc();
                        if (choiceptr != NULL) {
                            *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                        }
                    }
                } else {
                    b = &BuildingTypeClass::As_Reference(STRUCT_TURRET);
                    if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                        choiceptr = BuildChoice.Alloc();
                        if (choiceptr != NULL) {
                            *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                        }
                    }
                }
            }
        }

        /*
        **	Build some air defense.
        */
        int tf_aa = TF_Skirmish_Type(STRUCT_SAM, ActLike);
        int tf_radar = TF_Skirmish_Type(STRUCT_RADAR, ActLike);
        current = BQuantity[STRUCT_SAM] + BQuantity[STRUCT_AAGUN] + (tf_aa >= 0 ? BQuantity[tf_aa] : 0);
        if (current < Round_Up(Rule.AARatio * fixed(CurBuildings)) && current < (unsigned)Rule.AALimit) {

            /*
            **	Building air defense only makes sense if the opponent has aircraft
            **	of some kind.
            */
            bool airthreat = false;
            int threat_quantity = 0;
            if (enemy != NULL && enemy->AScan != 0) {
                airthreat = true;
                threat_quantity = enemy->CurAircraft;
            }
            if (!airthreat) {
                for (HousesType house = HOUSE_FIRST; house < HOUSE_COUNT; house++) {
                    HouseClass* h = HouseClass::As_Pointer(house);
                    if (h != NULL && !Is_Ally(house) && h->AScan != 0) {
                        airthreat = true;
                        break;
                    }
                }
            }

            if (airthreat) {

                if ((BQuantity[STRUCT_RADAR] + (tf_radar >= 0 ? BQuantity[tf_radar] : 0)) == 0) {
                    b = TF_Skirmish_Pick(STRUCT_RADAR, ActLike);
                    if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                        choiceptr = BuildChoice.Alloc();
                        if (choiceptr != NULL) {
                            *choiceptr = BuildChoiceClass(URGENCY_HIGH, b->Type);
                        }
                    }
                }

                b = TF_Skirmish_Pick(STRUCT_SAM, ActLike);
                if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                    choiceptr = BuildChoice.Alloc();
                    if (choiceptr != NULL) {
                        *choiceptr = BuildChoiceClass(
                            (current < (unsigned)threat_quantity) ? URGENCY_HIGH : URGENCY_MEDIUM, b->Type);
                    }
                } else {
                    b = TF_Skirmish_Pick(STRUCT_AAGUN, ActLike);
                    if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                        choiceptr = BuildChoice.Alloc();
                        if (choiceptr != NULL) {
                            *choiceptr = BuildChoiceClass(
                                (current < (unsigned)threat_quantity) ? URGENCY_HIGH : URGENCY_MEDIUM, b->Type);
                        }
                    }
                }
            }
        }

        /*
        **	Advanced base defense would be good.
        */
        int tf_adv = TF_Skirmish_Type(STRUCT_TESLA, ActLike);
        current = BQuantity[STRUCT_TESLA] + (tf_adv >= 0 ? BQuantity[tf_adv] : 0);
        if (current < Round_Up(Rule.TeslaRatio * fixed(CurBuildings)) && current < (unsigned)Rule.TeslaLimit) {
            b = TF_Skirmish_Pick(STRUCT_TESLA, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome) && Power_Fraction() >= 1) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                }
            }
        }

        /*
        **	Build a tech center as soon as possible -- but for GDI/Nod, not before the
        **	economy that pays for what the tech unlocks. RA houses keep vanilla timing.
        */
        int tf_tech = TF_Skirmish_Type(STRUCT_ADVANCED_TECH, ActLike);
        current = BQuantity[STRUCT_ADVANCED_TECH] + BQuantity[STRUCT_SOVIET_TECH] + (tf_tech >= 0 ? BQuantity[tf_tech] : 0);
        if (current < 1 && (!tf_td || tf_economy_ready)) {
            b = TF_Skirmish_Pick(STRUCT_ADVANCED_TECH, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome) && Power_Fraction() >= 1) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                }
            } else {
                b = &BuildingTypeClass::As_Reference(STRUCT_SOVIET_TECH);
                if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome) && Power_Fraction() >= 1) {
                    choiceptr = BuildChoice.Alloc();
                    if (choiceptr != NULL) {
                        *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                    }
                }
            }
        }

        /*
        **	A helipad would be good.
        */
        current = TF_Role_Quantity(BQuantity, STRUCT_HELIPAD);
        if (current < Round_Up(Rule.HelipadRatio * fixed(CurBuildings))
            && current < (unsigned)(enemy_helipads > Rule.HelipadLimit ? enemy_helipads : Rule.HelipadLimit)) {
            b = TF_Skirmish_Pick(STRUCT_HELIPAD, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    /*
                    **	Air production holds behind the ground base, then competes normally.
                    **	A pick resolves among the highest urgency present and power, refinery
                    **	and defence keep a MEDIUM candidate available indefinitely, so a
                    **	permanent LOW is never merely deprioritised -- it is unreachable, and
                    **	the house fields no aircraft for the whole match. Staying LOW until the
                    **	refineries and war factory are up is what keeps air from outranking the
                    **	core base; promoting afterwards is what lets it happen at all. The
                    **	count above still caps to the strongest air opponent.
                    */
                    *choiceptr = BuildChoiceClass(tf_economy_ready ? URGENCY_MEDIUM : URGENCY_LOW, b->Type);
                }
            }
        }

        /*
        **	An airstrip would be good.
        */
        current = TF_Role_Quantity(BQuantity, STRUCT_AIRSTRIP);
        if (current < Round_Up(Rule.AirstripRatio * fixed(CurBuildings))
            && current < (unsigned)(enemy_airstrips > Rule.AirstripLimit ? enemy_airstrips : Rule.AirstripLimit)) {
            b = TF_Skirmish_Pick(STRUCT_AIRSTRIP, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    /*
                    **	Same escalation as the helipad above, and for the same reason: the
                    **	ground base comes first, but air has to become reachable once it
                    **	exists. Covers GDI's airfield (STRUCT_AIRSTRIP -> TDGAFLD via
                    **	TF_Skirmish_Pick) as well as the RA airfields.
                    */
                    *choiceptr = BuildChoiceClass(tf_economy_ready ? URGENCY_MEDIUM : URGENCY_LOW, b->Type);
                }
            }
        }

        /*
        **	W5.1: a naval yard, once the water evaluation says a navy can matter here.
        **	Deliberately NOT gated on having discovered an enemy shore: naval presence
        **	is map control a human takes proactively, the patrol the yard enables is
        **	itself the discovery vector on water-split maps, and a discovery gate
        **	would hand recon-special factions (spy plane / recon flight) a standing
        **	naval head start over GPS-era ones. Fleet SIZE scales with discovery
        **	instead -- see AI_Vessel. Economy first for the same reason as air
        **	production above; scan order puts this behind the core base and the
        **	anti-starvation ageing brings it up.
        */
        current = TF_Role_Quantity(BQuantity, STRUCT_SHIP_YARD);
        if (current < 1 && tf_economy_ready) {
            int tf_nzone = 0;
            int tf_nsize = 0;
            bool tf_ncoastal = false;
            if (TF_Naval_Assessment(tf_nzone, tf_nsize, tf_ncoastal)) {
                b = TF_Skirmish_Pick(STRUCT_SHIP_YARD, ActLike);
                if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                    choiceptr = BuildChoice.Alloc();
                    if (choiceptr != NULL) {
                        *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                    }
                }
            }
        }

#ifdef OLD
        /*
        **	Build a repair bay if there isn't one already available.
        */
        current = BQuantity[STRUCT_REPAIR];
        if (current == 0) {
            b = &BuildingTypeClass::As_Reference(STRUCT_REPAIR);
            if (Can_Build(b, ActLike) && b->Cost_Of() < money) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr) {
                    *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                }
            }
        }
#endif

        /*
        **	Pick the most urgent choice. Among equal urgency the EARLIER candidate wins: the
        **	pool is assembled in a deliberate order -- advanced power, power, refinery,
        **	barracks, war factory -- and that scan order is the intended build priority, which
        **	is what produces the familiar opening. Ties are the normal case rather than the
        **	exception here (most branches emit URGENCY_MEDIUM), so resolving them at random
        **	hands the whole opening build order to a coin flip, and a house can open with a
        **	repair bay it has no army to use.
        **
        **	Scan order alone can starve a candidate outright, though -- a temple that always
        **	sits last at the winning urgency never wins, for tens of thousands of frames. So
        **	age the losers: a candidate passed over while it was AT the winning urgency takes
        **	a strike, and once it has taken enough it jumps the queue for one cycle. Ordinary
        **	priority holds, and nothing starves forever.
        */
        /*
        **	Starvation rescue is a LAST RESORT, not a rotation. Measure the wait in frames
        **	rather than decision cycles: with most branches offering URGENCY_MEDIUM there are
        **	half a dozen tied candidates, so a small cycle count lets the late-scan-order
        **	entries -- which is exactly what the defences are -- take turns jumping the queue,
        **	and the house spends its economy on guard towers instead of refineries. The case
        **	this exists for is a temple sitting unbuilt for tens of thousands of frames, so
        **	the threshold belongs on that scale.
        */
        enum
        {
            STARVE_FRAMES = 7500
        };
        static int _waiting_since[HOUSE_COUNT][STRUCT_COUNT] = {{0}};
        int hidx = (int)Class->House;
        bool track = (hidx >= 0 && hidx < HOUSE_COUNT);

        UrgencyType best = URGENCY_NONE;
        for (int index = 0; index < BuildChoice.Count(); index++) {
            UrgencyType u = BuildChoice.Ptr(index)->Urgency;
            if (u > best) {
                best = u;
            }
        }

        int bestindex = -1;
        int winner_age = 0;
        if (best != URGENCY_NONE) {
            int starved = -1;
            int longest = STARVE_FRAMES - 1;
            for (int index = 0; index < BuildChoice.Count(); index++) {
                if (BuildChoice.Ptr(index)->Urgency != best) {
                    continue;
                }
                if (bestindex < 0) {
                    bestindex = index; // scan order is the default priority
                }
                StructType s = BuildChoice.Ptr(index)->Structure;
                if (track && s >= 0 && s < STRUCT_COUNT && _waiting_since[hidx][s] > 0) {
                    int waited = (int)Frame - _waiting_since[hidx][s];
                    if (waited > longest) {
                        longest = waited;
                        starved = index;
                    }
                }
            }
            if (starved >= 0) {
                bestindex = starved;
                winner_age = longest;
            }

            if (track) {
                for (int index = 0; index < BuildChoice.Count(); index++) {
                    if (BuildChoice.Ptr(index)->Urgency != best) {
                        continue;
                    }
                    StructType s = BuildChoice.Ptr(index)->Structure;
                    if (s < 0 || s >= STRUCT_COUNT) {
                        continue;
                    }
                    if (index == bestindex) {
                        _waiting_since[hidx][s] = 0; // built, stop the clock
                    } else if (_waiting_since[hidx][s] == 0) {
                        _waiting_since[hidx][s] = (int)Frame; // start the clock
                    }
                }
            }
        }
        if (best != URGENCY_NONE) {
            BuildStructure = BuildChoice.Ptr(bestindex)->Structure;
        }

#if TF_DEV_BUILD // TF_AI_DIAG -- candidate pool + winner, per decision cycle.
        {
            FILE* _tfdbg = TF_AI_Diag_File();
            if (_tfdbg != NULL && (best != URGENCY_NONE || (tf_td && (Frame % 90) == 0))) {
                fprintf(_tfdbg,
                        "F%ld H%d AL%d POOL(%d):",
                        (long)Frame,
                        (int)Class->House,
                        (int)ActLike,
                        (int)BuildChoice.Count());
                for (int _i = 0; _i < BuildChoice.Count(); _i++) {
                    fprintf(_tfdbg,
                            " %s(u%d)",
                            BuildingTypeClass::As_Reference(BuildChoice.Ptr(_i)->Structure).IniName,
                            (int)BuildChoice.Ptr(_i)->Urgency);
                }
                if (best != URGENCY_NONE) {
                    // strikes = how many cycles the winner had been passed over at the
                    // winning urgency; non-zero means the anti-starvation age let it jump
                    // the scan order rather than winning on priority.
                    fprintf(_tfdbg,
                            " -> WIN %s(u%d aged=%d)\n",
                            BuildingTypeClass::As_Reference(BuildChoice.Ptr(bestindex)->Structure).IniName,
                            (int)best,
                            winner_age);
                } else {
                    fprintf(_tfdbg, " -> none\n");
                }
                fflush(_tfdbg);
            }
        }
#endif
    }

    return (TICKS_PER_SECOND);
}

/***********************************************************************************************
 * HouseClass::AI_Unit -- Determines what unit to build next.                                  *
 *                                                                                             *
 *    This routine handles the general case of determining what units to build next.           *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of games frames to delay before calling this routine again.*
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int HouseClass::AI_Unit(void)
{
    assert(Houses.ID(this) == ID);

    if (BuildUnit != UNIT_NONE)
        return (TICKS_PER_SECOND);
    if (CurUnits >= Control.MaxUnit)
        return (TICKS_PER_SECOND);

    /*
    **	A computer controlled house will try to build a replacement
    **	harvester if possible.
    */
    int tf_proc_t = TF_Skirmish_Type(STRUCT_REFINERY, ActLike);
    unsigned tf_refq = BQuantity[STRUCT_REFINERY] + (tf_proc_t >= 0 ? BQuantity[tf_proc_t] : 0);
    UnitType tf_harv = (tf_proc_t >= 0) ? UNIT_TDHARV : UNIT_HARVESTER;
    // Tiberian Factions: count harvesters via the Units heap, not UQuantity. UQuantity
    // reads 0 for docked TD harvesters (Limbo+Attach into the refinery), so the old
    // `tf_refq > UQuantity[tf_harv]` was ALWAYS true -> the AI spammed harvesters (e.g.
    // 11 for 3 refineries) -> broke -> power-starved -> upper tier blocked. The heap scan
    // counts docked + active (but not destroyed) harvesters, capping production at ~one
    // per refinery and rebuilding only genuine losses.
    int tf_harv_owned = 0;
    for (int hidx = 0; hidx < Units.Count(); hidx++) {
        UnitClass const* hu = Units.Ptr(hidx);
        if (hu != NULL && (HouseClass*)hu->House == this && (*hu == UNIT_TDHARV || *hu == UNIT_HARVESTER)) {
            tf_harv_owned++;
        }
    }
    if (IQ >= Rule.IQHarvester && !IsTiberiumShort && !IsHuman && (int)tf_refq > tf_harv_owned
        && Difficulty != DIFF_HARD) {
        if (UnitTypeClass::As_Reference(tf_harv).Level <= (unsigned)Control.TechLevel) {
            BuildUnit = tf_harv;
            return (TICKS_PER_SECOND);
        }
    }

    if (Session.Type == GAME_NORMAL) {

        int counter[UNIT_COUNT];
        memset(counter, 0x00, sizeof(counter));

        /*
        **	Build a list of the maximum of each type we wish to produce. This will be
        **	twice the number required to fill all teams.
        */
        int index;
        for (index = 0; index < Teams.Count(); index++) {
            TeamClass* tptr = Teams.Ptr(index);
            if (tptr != NULL) {
                TeamTypeClass const* team = tptr->Class;
                if (((team->IsReinforcable && !tptr->IsFullStrength)
                     || (!tptr->IsForcedActive && !tptr->IsHasBeen && !tptr->JustAltered))
                    && team->House == Class->House) {
                    for (int subindex = 0; subindex < team->ClassCount; subindex++) {
                        TechnoTypeClass const* memtype = team->Members[subindex].Class;
                        if (memtype->What_Am_I() == RTTI_UNITTYPE) {
                            counter[((UnitTypeClass const*)memtype)->Type] = 1;
                        }
                    }
                }
            }
        }

        /*
        **	Team types that are flagged as prebuilt, will always try to produce enough
        **	to fill one team of this type regardless of whether there is a team active
        **	of that type.
        */
        for (index = 0; index < TeamTypes.Count(); index++) {
            TeamTypeClass const* team = TeamTypes.Ptr(index);
            if (team != NULL && team->House == Class->House && team->IsPrebuilt && (!team->IsAutocreate || IsAlerted)) {
                for (int subindex = 0; subindex < team->ClassCount; subindex++) {
                    TechnoTypeClass const* memtype = team->Members[subindex].Class;

                    if (memtype->What_Am_I() == RTTI_UNITTYPE) {
                        int subtype = ((UnitTypeClass const*)memtype)->Type;
                        counter[subtype] = max(counter[subtype], team->Members[subindex].Quantity);
                    }
                }
            }
        }

        /*
        **	Reduce the theoretical maximum by the actual number of objects currently
        **	in play.
        */
        for (int uindex = 0; uindex < Units.Count(); uindex++) {
            UnitClass* unit = Units.Ptr(uindex);
            if (unit != NULL && unit->Is_Recruitable(this) && counter[unit->Class->Type] > 0) {
                counter[unit->Class->Type]--;
            }
        }

        /*
        **	Pick to build the most needed object but don't consider those objects that
        **	can't be built because of scenario restrictions or insufficient cash.
        */
        int bestval = -1;
        int bestcount = 0;
        UnitType bestlist[UNIT_COUNT];
        for (UnitType utype = UNIT_FIRST; utype < UNIT_COUNT; utype++) {
            if (counter[utype] > 0 && Can_Build(&UnitTypeClass::As_Reference(utype), Class->House)
                && UnitTypeClass::As_Reference(utype).Cost_Of() <= Available_Money()) {
                if (bestval == -1 || bestval < counter[utype]) {
                    bestval = counter[utype];
                    bestcount = 0;
                }
                bestlist[bestcount++] = utype;
            }
        }

        /*
        **	The unit type to build is now known. Fetch a pointer to the techno type class.
        */
        if (bestcount) {
            BuildUnit = bestlist[Random_Pick(0, bestcount - 1)];
        }
    }

    if (IsBaseBuilding) {

        /*
        **	W5.3: a beachhead that is holding gets a base. The expansion MCV jumps the
        **	ordinary combat pick -- the ferry gives it the first berth on the next ride
        **	and the beachhead sweep deploys it at the rally.
        */
        if (TF_Ferry_Wants_MCV()) {
            UnitType mcv = TF_Ferry_MCV_Type();
            if (mcv != UNIT_NONE) {
                BuildUnit = mcv;
#if TF_DEV_BUILD // TF_AI_DIAG
                {
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d FERRY-MCV queued %s\n", (long)Frame, (int)Class->House,
                                (int)ActLike, UnitTypeClass::As_Reference(mcv).IniName);
                        fflush(_tfdbg);
                    }
                }
#endif
                return (TICKS_PER_SECOND);
            }
        }

        int counter[UNIT_COUNT];
        int total = 0;
        UnitType index;
        for (index = UNIT_FIRST; index < UNIT_COUNT; index++) {
            UnitTypeClass const* utype = &UnitTypeClass::As_Reference(index);
            // Tiberian Factions: exclude the TD harvester too. This Can_Build-driven
            // loop is the skirmish combat-vehicle producer (armed types weighted x20,
            // random pick) and now fields the full TD vehicle roster for GDI/Nod
            // automatically. UNIT_TDHARV must stay excluded or it gets lumped in with
            // combat picks and the AI spams harvesters, burning income. Vanilla only
            // excluded UNIT_HARVESTER.
            if (Can_Build(utype, ActLike) && utype->Type != UNIT_HARVESTER
                && utype->Type != UNIT_TDHARV) {
                if (utype->PrimaryWeapon != NULL) {
                    counter[index] = 20;
                } else {
                    counter[index] = 1;
                }
            } else {
                counter[index] = 0;
            }
            total += counter[index];
        }

        if (total > 0) {
            int choice = Random_Pick(0, total - 1);
            for (index = UNIT_FIRST; index < UNIT_COUNT; index++) {
                if (choice < counter[index]) {
                    BuildUnit = index;
                    break;
                }
                choice -= counter[index];
            }
        }
    }

    return (TICKS_PER_SECOND);
}

int HouseClass::AI_Vessel(void)
{
    assert(Houses.ID(this) == ID);
    if (BuildVessel != VESSEL_NONE)
        return (TICKS_PER_SECOND);

    if (CurVessels >= Control.MaxVessel) {
        return (TICKS_PER_SECOND);
    }

    if (Session.Type == GAME_NORMAL) {

        int counter[VESSEL_COUNT];
        if (Session.Type == GAME_NORMAL) {
            memset(counter, 0x00, sizeof(counter));
        } else {
            for (VesselType index = VESSEL_FIRST; index < VESSEL_COUNT; index++) {
                if (Can_Build(&VesselTypeClass::As_Reference(index), Class->House)
                    && VesselTypeClass::As_Reference(index).Level <= (unsigned)Control.TechLevel) {
                    counter[index] = 16;
                } else {
                    counter[index] = 0;
                }
            }
        }

        /*
        **	Build a list of the maximum of each type we wish to produce. This will be
        **	twice the number required to fill all teams.
        */
        int index;
        for (index = 0; index < Teams.Count(); index++) {
            TeamClass* tptr = Teams.Ptr(index);
            if (tptr) {
                TeamTypeClass const* team = tptr->Class;

                if (((team->IsReinforcable && !tptr->IsFullStrength)
                     || (!tptr->IsForcedActive && !tptr->IsHasBeen && !tptr->JustAltered))
                    && team->House == Class->House) {
                    for (int subindex = 0; subindex < team->ClassCount; subindex++) {
                        if (team->Members[subindex].Class->What_Am_I() == RTTI_VESSELTYPE) {
                            counter[((VesselTypeClass const*)(team->Members[subindex].Class))->Type] = 1;
                        }
                    }
                }
            }
        }

        /*
        **	Team types that are flagged as prebuilt, will always try to produce enough
        **	to fill one team of this type regardless of whether there is a team active
        **	of that type.
        */
        for (index = 0; index < TeamTypes.Count(); index++) {
            TeamTypeClass const* team = TeamTypes.Ptr(index);
            if (team) {
                if (team->House == Class->House && team->IsPrebuilt && (!team->IsAutocreate || IsAlerted)) {
                    for (int subindex = 0; subindex < team->ClassCount; subindex++) {
                        if (team->Members[subindex].Class->What_Am_I() == RTTI_VESSELTYPE) {
                            int subtype = ((VesselTypeClass const*)(team->Members[subindex].Class))->Type;
                            counter[subtype] = max(counter[subtype], team->Members[subindex].Quantity);
                        }
                    }
                }
            }
        }

        /*
        **	Reduce the theoretical maximum by the actual number of objects currently
        **	in play.
        */
        for (int vindex = 0; vindex < Vessels.Count(); vindex++) {
            VesselClass* unit = Vessels.Ptr(vindex);
            if (unit != NULL && unit->Is_Recruitable(this) && counter[unit->Class->Type] > 0) {
                counter[unit->Class->Type]--;
            }
        }

        /*
        **	Pick to build the most needed object but don't consider those object that
        **	can't be built because of scenario restrictions or insufficient cash.
        */
        int bestval = -1;
        int bestcount = 0;
        VesselType bestlist[VESSEL_COUNT];
        for (VesselType utype = VESSEL_FIRST; utype < VESSEL_COUNT; utype++) {
            if (counter[utype] > 0 && Can_Build(&VesselTypeClass::As_Reference(utype), Class->House)
                && VesselTypeClass::As_Reference(utype).Cost_Of() <= Available_Money()) {
                if (bestval == -1 || bestval < counter[utype]) {
                    bestval = counter[utype];
                    bestcount = 0;
                }
                bestlist[bestcount++] = utype;
            }
        }

        /*
        **	The unit type to build is now known. Fetch a pointer to the techno type class.
        */
        if (bestcount) {
            BuildVessel = bestlist[Random_Pick(0, bestcount - 1)];
        }
    }

    if (IsBaseBuilding) {
        BuildVessel = VESSEL_NONE;

        /*
        **	W5.1 step 3: skirmish vessel production. Vanilla unconditionally cleared any
        **	pick here, so a skirmish AI never built a navy at all. Same weighted-random
        **	shape as AI_Unit's combat-vehicle block: every armed vessel Can_Build allows
        **	for the house's faction, picked uniformly. Unarmed transports are excluded
        **	until the ferry controller exists -- an LST with no loading logic just sits
        **	against the yard. Fleet size scales with what the house knows: a small
        **	patrol while no enemy shore has been discovered (the patrol is the
        **	discovery vector -- see the dispatcher in Expert_AI), then a fleet scaled
        **	to the strongest opponent navy this house has actually seen once the
        **	water demonstrably leads somewhere (TF_Naval_Fleet_Cap).
        */
        if (Session.Type != GAME_NORMAL && TF_Role_Quantity(BQuantity, STRUCT_SHIP_YARD) > 0) {
            int tzone = 0;
            int tsize = 0;
            bool tcoastal = false;
            int tenavy = 0;
            /*
            **	W5.2: the ferry transport rides outside the armed-fleet cap -- it is
            **	logistics, not fleet strength, and on a water-split map it is the only
            **	way any ground unit ever reaches the enemy.
            */
            bool tok = TF_Naval_Assessment(tzone, tsize, tcoastal);
            if (tok && TF_Ferry_Wants_Transport()) {
                BuildVessel = VESSEL_TRANSPORT;
#if TF_DEV_BUILD // TF_AI_DIAG
                {
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d NAVAL-PICK LST ferry curV=%d\n", (long)Frame,
                                (int)Class->House, (int)ActLike, (int)CurVessels);
                        fflush(_tfdbg);
                    }
                }
#endif
            } else if (tok && CurVessels < (unsigned)TF_Naval_Fleet_Cap(tcoastal, &tenavy)) {
                int counter[VESSEL_COUNT];
                int total = 0;
                VesselType vtype;
                for (vtype = VESSEL_FIRST; vtype < VESSEL_COUNT; vtype++) {
                    VesselTypeClass const* vt = &VesselTypeClass::As_Reference(vtype);
                    if (Can_Build(vt, ActLike) && vt->PrimaryWeapon != NULL) {
                        counter[vtype] = 1;
                    } else {
                        counter[vtype] = 0;
                    }
                    total += counter[vtype];
                }
                if (total > 0) {
                    int choice = Random_Pick(0, total - 1);
                    for (vtype = VESSEL_FIRST; vtype < VESSEL_COUNT; vtype++) {
                        if (choice < counter[vtype]) {
                            BuildVessel = vtype;
                            break;
                        }
                        choice -= counter[vtype];
                    }
                }
#if TF_DEV_BUILD // TF_AI_DIAG -- one line per vessel pick (the non-NONE early-out above means
                 // this fires once per production start, not per frame).
                if (BuildVessel != VESSEL_NONE) {
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d NAVAL-PICK %s curV=%d cap=%d enavy=%d\n", (long)Frame,
                                (int)Class->House, (int)ActLike,
                                VesselTypeClass::As_Reference(BuildVessel).IniName, (int)CurVessels,
                                TF_Naval_Fleet_Cap(tcoastal), tenavy);
                        fflush(_tfdbg);
                    }
                }
#endif
            }
        }
    }

    return (TICKS_PER_SECOND);
}

/***********************************************************************************************
 * HouseClass::AI_Infantry -- Determines the infantry unit to build.                           *
 *                                                                                             *
 *    This routine handles the general case of determining what infantry unit to build         *
 *    next.                                                                                    *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of game frames to delay before being called again.         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int HouseClass::AI_Infantry(void)
{
    assert(Houses.ID(this) == ID);

    if (BuildInfantry != INFANTRY_NONE)
        return (TICKS_PER_SECOND);
    if (CurInfantry >= Control.MaxInfantry)
        return (TICKS_PER_SECOND);

    if (Session.Type == GAME_NORMAL) {
        TechnoTypeClass const* techno = 0;
        int counter[INFANTRY_COUNT];
        memset(counter, 0x00, sizeof(counter));

        /*
        **	Build a list of the maximum of each type we wish to produce. This will be
        **	twice the number required to fill all teams.
        */
        int index;
        for (index = 0; index < Teams.Count(); index++) {
            TeamClass* tptr = Teams.Ptr(index);
            if (tptr != NULL) {
                TeamTypeClass const* team = tptr->Class;

                if (((team->IsReinforcable && !tptr->IsFullStrength)
                     || (!tptr->IsForcedActive && !tptr->IsHasBeen && !tptr->JustAltered))
                    && team->House == Class->House) {
                    for (int subindex = 0; subindex < team->ClassCount; subindex++) {
                        if (team->Members[subindex].Class->What_Am_I() == RTTI_INFANTRYTYPE) {
                            counter[((InfantryTypeClass const*)(team->Members[subindex].Class))->Type] +=
                                team->Members[subindex].Quantity + (team->IsReinforcable ? 1 : 0);
                        }
                    }
                }
            }
        }

        /*
        **	Team types that are flagged as prebuilt, will always try to produce enough
        **	to fill one team of this type regardless of whether there is a team active
        **	of that type.
        */
        for (index = 0; index < TeamTypes.Count(); index++) {
            TeamTypeClass const* team = TeamTypes.Ptr(index);
            if (team != NULL) {
                if (team->House == Class->House && team->IsPrebuilt && (!team->IsAutocreate || IsAlerted)) {
                    for (int subindex = 0; subindex < team->ClassCount; subindex++) {
                        if (team->Members[subindex].Class->What_Am_I() == RTTI_INFANTRYTYPE) {
                            int subtype = ((InfantryTypeClass const*)(team->Members[subindex].Class))->Type;
                            //									counter[subtype] = 1;
                            counter[subtype] = max(counter[subtype], team->Members[subindex].Quantity);
                            counter[subtype] = min(counter[subtype], 5);
                        }
                    }
                }
            }
        }

        /*
        **	Reduce the theoretical maximum by the actual number of objects currently
        **	in play.
        */
        for (int uindex = 0; uindex < Infantry.Count(); uindex++) {
            InfantryClass* infantry = Infantry.Ptr(uindex);
            if (infantry != NULL && infantry->Is_Recruitable(this) && counter[infantry->Class->Type] > 0) {
                counter[infantry->Class->Type]--;
            }
        }

        /*
        **	Pick to build the most needed object but don't consider those object that
        **	can't be built because of scenario restrictions or insufficient cash.
        */
        int bestval = -1;
        int bestcount = 0;
        InfantryType bestlist[INFANTRY_COUNT];
        for (InfantryType utype = INFANTRY_FIRST; utype < INFANTRY_COUNT; utype++) {

            if (utype != INFANTRY_DOG || !(IScan & INFANTRYF_DOG)) {
                if (counter[utype] > 0 && Can_Build(&InfantryTypeClass::As_Reference(utype), Class->House)
                    && InfantryTypeClass::As_Reference(utype).Cost_Of() <= Available_Money()) {
                    if (bestval == -1 || bestval < counter[utype]) {
                        bestval = counter[utype];
                        bestcount = 0;
                    }
                    bestlist[bestcount++] = utype;
                }
            }
        }

        /*
        **	The infantry type to build is now known. Fetch a pointer to the techno type class.
        */
        if (bestcount) {
            int pick = Random_Pick(0, bestcount - 1);
            BuildInfantry = bestlist[pick];
        }
    }

    if (IsBaseBuilding) {
        HouseClass const* enemy = NULL;
        if (Enemy != HOUSE_NONE) {
            enemy = HouseClass::As_Pointer(Enemy);
        }

        /*
        **	This structure is used to keep track of the list of infantry types that should be
        **	built. The infantry type and the value assigned to it is recorded.
        */
        struct
        {
            InfantryType Type; // Infantry type.
            int Value;         // Relative value assigned.
        } typetrack[INFANTRY_COUNT];
        int count = 0;
        int total = 0;
        for (InfantryType index = INFANTRY_FIRST; index < INFANTRY_COUNT; index++) {
            if (Can_Build(&InfantryTypeClass::As_Reference(index), ActLike)
                && InfantryTypeClass::As_Reference(index).Level <= (unsigned)Control.TechLevel) {
                typetrack[count].Value = 0;
#ifdef FIXIT_CSII //	checked - ajw 9/28/98 This looks like a potential bug. It is prob. for save game format           \
                  //compatibility.
                int clipindex = index;
                if (clipindex >= INFANTRY_RA_COUNT)
                    clipindex -= INFANTRY_RA_COUNT;
                if ((enemy != NULL && enemy->IQuantity[clipindex] > IQuantity[clipindex])
                    || Available_Money() > Rule.InfantryReserve || CurInfantry < CurBuildings * Rule.InfantryBaseMult) {
#else
                if ((enemy != NULL && enemy->IQuantity[index] > IQuantity[index])
                    || Available_Money() > Rule.InfantryReserve || CurInfantry < CurBuildings * Rule.InfantryBaseMult) {
#endif

                    switch (index) {
                    case INFANTRY_E1:
                        typetrack[count].Value = 3;
                        break;

                    case INFANTRY_E2:
                        typetrack[count].Value = 5;
                        break;

                    case INFANTRY_E3:
                        typetrack[count].Value = 2;
                        break;

                    case INFANTRY_E4:
                        typetrack[count].Value = 5;
                        break;

                    case INFANTRY_RENOVATOR:
                        if (CurInfantry > 5) {
                            typetrack[count].Value = 1 - max(IQuantity[index], 0);
                        }
                        break;

                    case INFANTRY_TANYA:
                        typetrack[count].Value = 1 - max(IQuantity[index], 0);
                        break;

                    /*
                    **	Tiberian Factions mod — GDI/Nod can only build the TD infantry
                    **	roster (their TD barracks gate out the RA E1..E4 above), so every
                    **	TD type fell through to the default Value=0 and the weighted picker
                    **	never chose one — the AI fielded tanks but ZERO infantry. Weights
                    **	mirror the closest RA analog so the mix philosophy is unchanged:
                    **	  TDE1 minigunner ~ E1(3), TDE2 grenadier ~ E2(5),
                    **	  TDE3 rocket ~ E3(2), TDE4 flame ~ E4(5), TDE5 chem ~ flame(5),
                    **	  TDE6 engineer ~ RENOVATOR, TDRMBO commando ~ TANYA.
                    **	The engineer/commando "1 - count" build-one heuristic uses the
                    **	clip-safe QuantityI() accessor (raw IQuantity[index] would read
                    **	past INFANTRY_RA_COUNT for the TD slots). Balance of the resulting
                    **	mix is a post-v1.0 item (see docs/balance-v1-notes.md).
                    */
                    case INFANTRY_TDE1:
                        typetrack[count].Value = 3;
                        break;

                    case INFANTRY_TDE2:
                        typetrack[count].Value = 5;
                        break;

                    case INFANTRY_TDE3:
                        typetrack[count].Value = 2;
                        break;

                    case INFANTRY_TDE4:
                        typetrack[count].Value = 5;
                        break;

                    case INFANTRY_TDE5:
                        typetrack[count].Value = 5;
                        break;

                    case INFANTRY_TDE6:
                        if (CurInfantry > 5) {
                            typetrack[count].Value = 1 - max(QuantityI(index), 0);
                        }
                        break;

                    case INFANTRY_TDRMBO:
                        typetrack[count].Value = 1 - max(QuantityI(index), 0);
                        break;

                    default:
                        typetrack[count].Value = 0;
                        break;
                    }
                }

                if (typetrack[count].Value > 0) {
                    typetrack[count].Type = index;
                    total += typetrack[count].Value;
                    count++;
                }
            }
        }

        /*
        **	If there is at least one choice, then pick it. The object picked
        **	is influenced by the weight (value) assigned to it. This is accomplished
        **	by picking a number between 0 and the total weight value. The appropriate
        **	infantry object that matches the number picked is then selected to be built.
        */
        if (count > 0) {
            int pick = Random_Pick(0, total - 1);
            for (int index = 0; index < count; index++) {
                if (pick < typetrack[index].Value) {
                    BuildInfantry = typetrack[index].Type;
                    break;
                }
                pick -= typetrack[index].Value;
            }
        }
    }
    return (TICKS_PER_SECOND);
}

/***********************************************************************************************
 * HouseClass::AI_Aircraft -- Determines what aircraft to build next.                          *
 *                                                                                             *
 *    This routine is used to determine the general case of what aircraft to build next.       *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with the number of frame to delay before calling this routine again.       *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
int HouseClass::AI_Aircraft(void)
{
    assert(Houses.ID(this) == ID);

    if (!IsHuman && IQ >= Rule.IQAircraft) {
        if (BuildAircraft != AIRCRAFT_NONE)
            return (TICKS_PER_SECOND);
        if (CurAircraft >= Control.MaxAircraft)
            return (TICKS_PER_SECOND);

        /*
        **	Tiberian Factions mod — GDI/Nod helicopters. The RA cases below only
        **	know LONGBOW/HIND/MIG/YAK (none of which GDI/Nod can build) and count
        **	the RA STRUCT_HELIPAD they never own, so the TD factions produced ZERO
        **	aircraft. GDI flies the Orca (AIRCRAFT_TDORCA), Nod the Apache
        **	(AIRCRAFT_TDAPACHE); both are built from the TD helipad (STRUCT_TDHPAD).
        **	Cap one airframe per pad, mirroring the RA "pads > built" gate.
        */
        if (Can_Build(&AircraftTypeClass::As_Reference(AIRCRAFT_TDORCA), ActLike)
            && AircraftTypeClass::As_Reference(AIRCRAFT_TDORCA).Level <= (unsigned)Control.TechLevel
            && BQuantity[STRUCT_TDHPAD] + BQuantity[STRUCT_TDGHPAD]
                   > AQuantity[AIRCRAFT_TDORCA] + AQuantity[AIRCRAFT_TDAPACHE]) {
            BuildAircraft = AIRCRAFT_TDORCA;
            return (TICKS_PER_SECOND);
        }

        if (Can_Build(&AircraftTypeClass::As_Reference(AIRCRAFT_TDAPACHE), ActLike)
            && AircraftTypeClass::As_Reference(AIRCRAFT_TDAPACHE).Level <= (unsigned)Control.TechLevel
            && BQuantity[STRUCT_TDHPAD] + BQuantity[STRUCT_TDNHPAD]
                   > AQuantity[AIRCRAFT_TDORCA] + AQuantity[AIRCRAFT_TDAPACHE]) {
            BuildAircraft = AIRCRAFT_TDAPACHE;
            return (TICKS_PER_SECOND);
        }

        /*
        **	GDI A-10 -- the fixed-wing analog of the Orca case above. RA's MiG/Yak cases
        **	key on STRUCT_AIRSTRIP, which GDI never owns, so without this the GDI AI built
        **	no fixed-wing at all. Keyed to the separated GDI Airfield (STRUCT_TDGAFLD);
        **	one A-10 per airfield, mirroring the RA one-per-airstrip gate.
        */
        if (Can_Build(&AircraftTypeClass::As_Reference(AIRCRAFT_TDA10), ActLike)
            && AircraftTypeClass::As_Reference(AIRCRAFT_TDA10).Level <= (unsigned)Control.TechLevel
            && BQuantity[STRUCT_TDGAFLD] > AQuantity[AIRCRAFT_TDA10]) {
            BuildAircraft = AIRCRAFT_TDA10;
            return (TICKS_PER_SECOND);
        }

        if (Can_Build(&AircraftTypeClass::As_Reference(AIRCRAFT_LONGBOW), ActLike)
            && AircraftTypeClass::As_Reference(AIRCRAFT_LONGBOW).Level <= (unsigned)Control.TechLevel
            && BQuantity[STRUCT_HELIPAD] + BQuantity[STRUCT_AHPAD]
                   > AQuantity[AIRCRAFT_LONGBOW] + AQuantity[AIRCRAFT_HIND]) {
            BuildAircraft = AIRCRAFT_LONGBOW;
            return (TICKS_PER_SECOND);
        }

        if (Can_Build(&AircraftTypeClass::As_Reference(AIRCRAFT_HIND), ActLike)
            && AircraftTypeClass::As_Reference(AIRCRAFT_HIND).Level <= (unsigned)Control.TechLevel
            && BQuantity[STRUCT_HELIPAD] + BQuantity[STRUCT_SHPAD]
                   > AQuantity[AIRCRAFT_LONGBOW] + AQuantity[AIRCRAFT_HIND]) {
            BuildAircraft = AIRCRAFT_HIND;
            return (TICKS_PER_SECOND);
        }

        if (Can_Build(&AircraftTypeClass::As_Reference(AIRCRAFT_MIG), ActLike)
            && AircraftTypeClass::As_Reference(AIRCRAFT_MIG).Level <= (unsigned)Control.TechLevel
            && BQuantity[STRUCT_AIRSTRIP] > AQuantity[AIRCRAFT_MIG] + AQuantity[AIRCRAFT_YAK]) {
            BuildAircraft = AIRCRAFT_MIG;
            return (TICKS_PER_SECOND);
        }

        if (Can_Build(&AircraftTypeClass::As_Reference(AIRCRAFT_YAK), ActLike)
            && AircraftTypeClass::As_Reference(AIRCRAFT_YAK).Level <= (unsigned)Control.TechLevel
            && BQuantity[STRUCT_AIRSTRIP] > AQuantity[AIRCRAFT_MIG] + AQuantity[AIRCRAFT_YAK]) {
            BuildAircraft = AIRCRAFT_YAK;
            return (TICKS_PER_SECOND);
        }
    }

    return (TICKS_PER_SECOND);
}

/***********************************************************************************************
 * HouseClass::Production_Begun -- Records that production has begun.                          *
 *                                                                                             *
 *    This routine is used to inform the Expert System that production of the specified object *
 *    has begun. This allows the AI to proceed with picking another object to begin production *
 *    on.                                                                                      *
 *                                                                                             *
 * INPUT:   product  -- Pointer to the object that production has just begun on.               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Production_Begun(TechnoClass const* product)
{
    assert(Houses.ID(this) == ID);

    if (product != NULL) {
        switch (product->What_Am_I()) {
        case RTTI_UNIT:
            if (*((UnitClass*)product) == BuildUnit) {
                BuildUnit = UNIT_NONE;
            }
            break;

        case RTTI_VESSEL:
            if (*((VesselClass*)product) == BuildVessel) {
                BuildVessel = VESSEL_NONE;
            }
            break;

        case RTTI_INFANTRY:
            if (*((InfantryClass*)product) == BuildInfantry) {
                BuildInfantry = INFANTRY_NONE;
            }
            break;

        case RTTI_BUILDING:
            if (*((BuildingClass*)product) == BuildStructure) {
                BuildStructure = STRUCT_NONE;
            }
            break;

        case RTTI_AIRCRAFT:
            if (*((AircraftClass*)product) == BuildAircraft) {
                BuildAircraft = AIRCRAFT_NONE;
            }
            break;

        default:
            break;
        }
    }
}

/***********************************************************************************************
 * HouseClass::Tracking_Remove -- Remove object from house tracking system.                    *
 *                                                                                             *
 *    This routine informs the Expert System that the specified object is no longer part of    *
 *    this house's inventory. This occurs when the object is destroyed or captured.            *
 *                                                                                             *
 * INPUT:   techno   -- Pointer to the object to remove from the tracking systems of this      *
 *                      house.                                                                 *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Tracking_Remove(TechnoClass const* techno)
{
    assert(Houses.ID(this) == ID);

    int type;

    switch (techno->What_Am_I()) {
    case RTTI_BUILDING:
        CurBuildings--;
        BQuantity[((BuildingTypeClass const&)techno->Class_Of()).Type]--;
        break;

    case RTTI_AIRCRAFT:
        CurAircraft--;
        AQuantity[((AircraftTypeClass const&)techno->Class_Of()).Type]--;
        break;

    case RTTI_INFANTRY:
        CurInfantry--;
        if (!((InfantryClass*)techno)->IsTechnician) {
            type = ((InfantryTypeClass const&)techno->Class_Of()).Type;
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
            if (type >= INFANTRY_RA_COUNT)
                type -= INFANTRY_RA_COUNT;
#endif
            IQuantity[type]--;
        }
        break;

    case RTTI_UNIT:
        CurUnits--;
        type = ((UnitTypeClass const&)techno->Class_Of()).Type;
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
        if (type >= UNIT_RA_COUNT)
            type -= UNIT_RA_COUNT;
#endif
        UQuantity[type]--;
        break;

    case RTTI_VESSEL:
        CurVessels--;
        type = ((VesselTypeClass const&)techno->Class_Of()).Type;
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
        if (type >= VESSEL_RA_COUNT)
            type -= VESSEL_RA_COUNT;
#endif
        VQuantity[type]--;
        break;

    default:
        break;
    }
}

/***********************************************************************************************
 * HouseClass::Tracking_Add -- Informs house of new inventory item.                            *
 *                                                                                             *
 *    This function is called when the specified object is now available as part of the house's*
 *    inventory. This occurs when the object is newly produced and also when it is captured    *
 *    by this house.                                                                           *
 *                                                                                             *
 * INPUT:   techno   -- Pointer to the object that is now part of the house inventory.         *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/29/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Tracking_Add(TechnoClass const* techno)
{
    assert(Houses.ID(this) == ID);

    StructType building;
    AircraftType aircraft;
    InfantryType infantry;
    UnitType unit;
    VesselType vessel;
    int quant;

    switch (techno->What_Am_I()) {
    case RTTI_BUILDING:
        CurBuildings++;
        building = ((BuildingTypeClass const&)techno->Class_Of()).Type;
        BQuantity[building]++;
        if ((int)building < 32) {
            BScan |= (1L << building);
        }
        if (Session.Type == GAME_INTERNET) {
            BuildingTotals.Increment_Unit_Total(techno->Class_Of().ID);
        }
        break;

    case RTTI_AIRCRAFT:
        CurAircraft++;
        aircraft = ((AircraftTypeClass const&)techno->Class_Of()).Type;
        AQuantity[aircraft]++;
        AScan |= (1L << aircraft);
        if (Session.Type == GAME_INTERNET) {
            AircraftTotals.Increment_Unit_Total(techno->Class_Of().ID);
        }
        break;

    case RTTI_INFANTRY:
        CurInfantry++;
        infantry = ((InfantryTypeClass const&)techno->Class_Of()).Type;
        if (!((InfantryClass*)techno)->IsTechnician) {
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
            quant = infantry;
            if (quant >= INFANTRY_RA_COUNT)
                quant -= INFANTRY_RA_COUNT;
            IQuantity[quant]++;
#else
            IQuantity[infantry]++;
#endif
            if (!((InfantryTypeClass const&)techno->Class_Of()).IsCivilian && Session.Type == GAME_INTERNET) {
                InfantryTotals.Increment_Unit_Total(techno->Class_Of().ID);
            }
            IScan |= (1L << infantry);
        }
        break;

    case RTTI_UNIT:
        CurUnits++;
        unit = ((UnitTypeClass const&)techno->Class_Of()).Type;
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
        quant = unit;
        if (quant >= UNIT_RA_COUNT)
            quant -= UNIT_RA_COUNT;
        UQuantity[quant]++;
#else
        UQuantity[unit]++;
#endif
        UScan |= (1L << unit);
#ifdef REMASTER_BUILD
        if (Session.Type == GAME_INTERNET) {
            UnitTotals.Increment_Unit_Total(techno->Class_Of().ID);
        }
#endif
        break;

    case RTTI_VESSEL:
        CurVessels++;
        vessel = ((VesselTypeClass const&)techno->Class_Of()).Type;
#ifdef FIXIT_CSII //	checked - ajw 9/28/98
        quant = vessel;
        if (quant >= VESSEL_RA_COUNT)
            quant -= VESSEL_RA_COUNT;
        VQuantity[quant]++;
#else
        VQuantity[vessel]++;
#endif
        VScan |= (1L << vessel);
        if (Session.Type == GAME_INTERNET) {
            VesselTotals.Increment_Unit_Total(techno->Class_Of().ID);
        }
        break;

    default:
        break;
    }
}

/***********************************************************************************************
 * HouseClass::Factory_Counter -- Fetches a pointer to the factory counter value.              *
 *                                                                                             *
 *    Use this routine to fetch a pointer to the variable that holds the number of factories   *
 *    that can produce the specified object type. This is a helper routine used when           *
 *    examining the number of factories as well as adjusting their number.                     *
 *                                                                                             *
 * INPUT:   rtti  -- The RTTI of the object that could be produced.                            *
 *                                                                                             *
 * OUTPUT:  Returns with the number of factories owned by this house that could produce the    *
 *          object of the type specified.                                                      *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/30/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
int* HouseClass::Factory_Counter(RTTIType rtti)
{
    switch (rtti) {
    case RTTI_UNITTYPE:
    case RTTI_UNIT:
        return (&UnitFactories);

    case RTTI_VESSELTYPE:
    case RTTI_VESSEL:
        return (&VesselFactories);

    case RTTI_AIRCRAFTTYPE:
    case RTTI_AIRCRAFT:
        return (&AircraftFactories);

    case RTTI_INFANTRYTYPE:
    case RTTI_INFANTRY:
        return (&InfantryFactories);

    case RTTI_BUILDINGTYPE:
    case RTTI_BUILDING:
        return (&BuildingFactories);

    default:
        break;
    }
    return (NULL);
}

/***********************************************************************************************
 * HouseClass::Active_Remove -- Remove this object from active duty for this house.            *
 *                                                                                             *
 *    This routine will recognize the specified object as having been removed from active      *
 *    duty.                                                                                    *
 *                                                                                             *
 * INPUT:   techno   -- Pointer to the object to remove from active duty.                      *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/16/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Active_Remove(TechnoClass const* techno)
{
    if (techno == NULL)
        return;

    if (techno->What_Am_I() == RTTI_BUILDING) {
        int* fptr = Factory_Counter(((BuildingClass*)techno)->Class->ToBuild);
        if (fptr != NULL) {
            *fptr = *fptr - 1;
        }
    }
}

/***********************************************************************************************
 * HouseClass::Active_Add -- Add an object to active duty for this house.                      *
 *                                                                                             *
 *    This routine will recognize the specified object as having entered active duty. Any      *
 *    abilities granted to the house by that object are now available.                         *
 *                                                                                             *
 * INPUT:   techno   -- Pointer to the object that is entering active duty.                    *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/16/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Active_Add(TechnoClass const* techno)
{
    if (techno == NULL)
        return;

    if (techno->What_Am_I() == RTTI_BUILDING) {
        int* fptr = Factory_Counter(((BuildingClass*)techno)->Class->ToBuild);
        if (fptr != NULL) {
            *fptr = *fptr + 1;
        }
    }
}

/***********************************************************************************************
 * HouseClass::Which_Zone -- Determines what zone a coordinate lies in.                        *
 *                                                                                             *
 *    This routine will determine what zone the specified coordinate lies in with respect to   *
 *    this house's base. A location that is too distant from the base, even though it might    *
 *    be a building, is not considered part of the base and returns ZONE_NONE.                 *
 *                                                                                             *
 * INPUT:   coord -- The coordinate to examine.                                                *
 *                                                                                             *
 * OUTPUT:  Returns with the base zone that the specified coordinate lies in.                  *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/02/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
ZoneType HouseClass::Which_Zone(COORDINATE coord) const
{
    assert(Houses.ID(this) == ID);

    if (coord == 0)
        return (ZONE_NONE);

    int distance = Distance(Center, coord);
    if (distance <= Radius)
        return (ZONE_CORE);
    if (distance > Radius * 4)
        return (ZONE_NONE);

    DirType facing = Direction(Center, coord);
    if (facing < DIR_NE || facing > DIR_NW)
        return (ZONE_NORTH);
    if (facing >= DIR_NE && facing < DIR_SE)
        return (ZONE_EAST);
    if (facing >= DIR_SE && facing < DIR_SW)
        return (ZONE_SOUTH);
    return (ZONE_WEST);
}

/***********************************************************************************************
 * HouseClass::Which_Zone -- Determines which base zone the specified object lies in.          *
 *                                                                                             *
 *    Use this routine to determine what zone the specified object lies in.                    *
 *                                                                                             *
 * INPUT:   object   -- Pointer to the object that will be checked for zone occupation.        *
 *                                                                                             *
 * OUTPUT:  Returns with the base zone that the object lies in. For objects that are too       *
 *          distant from the center of the base, ZONE_NONE is returned.                        *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/02/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
ZoneType HouseClass::Which_Zone(ObjectClass const* object) const
{
    assert(Houses.ID(this) == ID);

    if (!object)
        return (ZONE_NONE);
    return (Which_Zone(object->Center_Coord()));
}

/***********************************************************************************************
 * HouseClass::Which_Zone -- Determines which base zone the specified cell lies in.            *
 *                                                                                             *
 *    This routine is used to determine what base zone the specified cell is in.               *
 *                                                                                             *
 * INPUT:   cell  -- The cell to examine.                                                      *
 *                                                                                             *
 * OUTPUT:  Returns the base zone that the cell lies in or ZONE_NONE if the cell is too far    *
 *          away.                                                                              *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/02/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
ZoneType HouseClass::Which_Zone(CELL cell) const
{
    assert(Houses.ID(this) == ID);

    return (Which_Zone(Cell_Coord(cell)));
}

/***********************************************************************************************
 * HouseClass::Recalc_Attributes -- Recalcs all houses existence bits.                         *
 *                                                                                             *
 *    This routine will go through all game objects and reset the existence bits for the       *
 *    owning house. This method ensures that if the object exists, then the corresponding      *
 *    existence bit is also set.                                                               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/02/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Recalc_Attributes(void)
{
    /*
    **	Clear out all tracking values that will be filled in by this
    **	routine. This allows the filling in process to not worry about
    **	old existing values.
    */
    int index;
    for (index = 0; index < Houses.Count(); index++) {
        HouseClass* house = Houses.Ptr(index);

        if (house != NULL) {
            house->BScan = 0;
            house->ActiveBScan = 0;
            memset(house->ActiveBQuantity, '\0', sizeof(house->ActiveBQuantity));
            house->IScan = 0;
            house->ActiveIScan = 0;
            house->UScan = 0;
            house->ActiveUScan = 0;
            house->AScan = 0;
            house->ActiveAScan = 0;
            house->VScan = 0;
            house->ActiveVScan = 0;
        }
    }

    /*
    **	A second pass through the sentient objects is required so that the appropriate scan
    **	bits will be set for the owner house.
    */
    for (index = 0; index < Units.Count(); index++) {
        UnitClass const* unit = Units.Ptr(index);
        unit->House->UScan |= (1L << unit->Class->Type);
        if (unit->IsLocked && (Session.Type != GAME_NORMAL || !unit->House->IsHuman || unit->IsDiscoveredByPlayer)) {
            if (!unit->IsInLimbo) {
                unit->House->ActiveUScan |= (1L << unit->Class->Type);
            }
        }
    }
    for (index = 0; index < Infantry.Count(); index++) {
        InfantryClass const* infantry = Infantry.Ptr(index);
        infantry->House->IScan |= (1L << infantry->Class->Type);
        if (infantry->IsLocked
            && (Session.Type != GAME_NORMAL || !infantry->House->IsHuman || infantry->IsDiscoveredByPlayer)) {
            if (!infantry->IsInLimbo) {
                infantry->House->ActiveIScan |= (1L << infantry->Class->Type);
                infantry->House->OldIScan |= (1L << infantry->Class->Type);
            }
        }
    }
    for (index = 0; index < Aircraft.Count(); index++) {
        AircraftClass const* aircraft = Aircraft.Ptr(index);
        aircraft->House->AScan |= (1L << aircraft->Class->Type);
        if (aircraft->IsLocked
            && (Session.Type != GAME_NORMAL || !aircraft->House->IsHuman || aircraft->IsDiscoveredByPlayer)) {
            if (!aircraft->IsInLimbo) {
                aircraft->House->ActiveAScan |= (1L << aircraft->Class->Type);
                aircraft->House->OldAScan |= (1L << aircraft->Class->Type);
            }
        }
    }
    for (index = 0; index < Buildings.Count(); index++) {
        BuildingClass const* building = Buildings.Ptr(index);
        int btype = building->Class->Type;
        long scanbit = TF_Building_Scan_Bit(btype);
        building->House->BScan |= scanbit;
        if (building->IsLocked
            && (Session.Type != GAME_NORMAL || !building->House->IsHuman || building->IsDiscoveredByPlayer)) {
            if (!building->IsInLimbo) {
                building->House->ActiveBScan |= scanbit;
                building->House->OldBScan |= scanbit;
                if (btype >= 0 && btype < MAX_BUILDING_TYPES) {
                    building->House->ActiveBQuantity[btype]++;
                }
            }
        }
    }
    for (index = 0; index < Vessels.Count(); index++) {
        VesselClass const* vessel = Vessels.Ptr(index);
        vessel->House->VScan |= (1L << vessel->Class->Type);
        if (vessel->IsLocked
            && (Session.Type != GAME_NORMAL || !vessel->House->IsHuman || vessel->IsDiscoveredByPlayer)) {
            if (!vessel->IsInLimbo) {
                vessel->House->ActiveVScan |= (1L << vessel->Class->Type);
                vessel->House->OldVScan |= (1L << vessel->Class->Type);
            }
        }
    }
}

/***********************************************************************************************
 * HouseClass::Zone_Cell -- Finds the cell closest to the center of the zone.                  *
 *                                                                                             *
 *    This routine is used to find the cell that is closest to the center point of the         *
 *    zone specified. Typical use of this routine is for building and unit placement so that   *
 *    they can "cover" the specified zone.                                                     *
 *                                                                                             *
 * INPUT:   zone  -- The zone that the center point is to be returned.                         *
 *                                                                                             *
 * OUTPUT:  Returns with the cell that is closest to the center point of the zone specified.   *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/02/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
CELL HouseClass::Zone_Cell(ZoneType zone) const
{
    assert(Houses.ID(this) == ID);

    switch (zone) {
    case ZONE_CORE:
        return (Coord_Cell(Center));

    case ZONE_NORTH:
        return (Coord_Cell(Coord_Move(Center, DIR_N, Radius * 3)));

    case ZONE_EAST:
        return (Coord_Cell(Coord_Move(Center, DIR_E, Radius * 3)));

    case ZONE_WEST:
        return (Coord_Cell(Coord_Move(Center, DIR_W, Radius * 3)));

    case ZONE_SOUTH:
        return (Coord_Cell(Coord_Move(Center, DIR_S, Radius * 3)));

    default:
        break;
    }
    return (0);
}

/***********************************************************************************************
 * HouseClass::Where_To_Go -- Determines where the object should go and wait.                  *
 *                                                                                             *
 *    This function is called for every new unit produced or delivered in order to determine   *
 *    where the unit should "hang out" to await further orders. The best area for the          *
 *    unit to loiter is returned as a cell location.                                           *
 *                                                                                             *
 * INPUT:   object   -- Pointer to the object that needs to know where to go.                  *
 *                                                                                             *
 * OUTPUT:  Returns with the cell that the unit should move to.                                *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/02/1995 JLB : Created.                                                                 *
 *   11/04/1996 JLB : Simplified to use helper functions                                       *
 *=============================================================================================*/
CELL HouseClass::Where_To_Go(FootClass const* object) const
{
    assert(Houses.ID(this) == ID);
    assert(object != NULL);

    ZoneType zone; // The zone that the object should go to.
    if (object->Anti_Air() + object->Anti_Armor() + object->Anti_Infantry() == 0) {
        zone = ZONE_CORE;
    } else {
        zone = Random_Pick(ZONE_NORTH, ZONE_WEST);
    }

    CELL cell = Random_Cell_In_Zone(zone);
    assert(cell != 0);

    return (Map.Nearby_Location(cell, SPEED_TRACK, Map[cell].Zones[MZONE_NORMAL], MZONE_NORMAL));
}

/***********************************************************************************************
 * HouseClass::Find_Juicy_Target -- Finds a suitable field target.                             *
 *                                                                                             *
 *    This routine is used to find targets out in the field and away from base defense.        *
 *    Typical of this would be the attack helicopters and the roving attack bands of           *
 *    hunter killers.                                                                          *
 *                                                                                             *
 * INPUT:   coord -- The coordinate of the attacker. Closer targets are given preference.      *
 *                                                                                             *
 * OUTPUT:  Returns with a suitable target to attack.                                          *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/12/1995 JLB : Created.                                                                 *
 *=============================================================================================*/
TARGET HouseClass::Find_Juicy_Target(COORDINATE coord) const
{
    assert(Houses.ID(this) == ID);

    UnitClass* best = 0;
    int value = 0;

    for (int index = 0; index < Units.Count(); index++) {
        UnitClass* unit = Units.Ptr(index);

        if (unit && !unit->IsInLimbo && !Is_Ally(unit) && unit->House->Which_Zone(unit) == ZONE_NONE) {
            int val = Distance(coord, unit->Center_Coord());

            if (unit->Anti_Air())
                val *= 2;

            if (*unit == UNIT_HARVESTER || *unit == UNIT_TDHARV)
                val /= 2;

            if (value == 0 || val < value) {
                value = val;
                best = unit;
            }
        }
    }
    if (best) {
        return (best->As_Target());
    }
    return (TARGET_NONE);
}

/***********************************************************************************************
 * HouseClass::Get_Quantity -- Fetches the total number of aircraft of the specified type.     *
 *                                                                                             *
 *    Call this routine to fetch the total quantity of aircraft of the type specified that is  *
 *    owned by this house.                                                                     *
 *                                                                                             *
 * INPUT:   aircraft -- The aircraft type to check the quantity of.                            *
 *                                                                                             *
 * OUTPUT:  Returns with the total quantity of all aircraft of that type that is owned by this *
 *          house.                                                                             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
int HouseClass::Get_Quantity(AircraftType aircraft)
{
    return (AQuantity[aircraft]);
}

/***********************************************************************************************
 * HouseClass::Fetch_Factory -- Finds the factory associated with the object type specified.   *
 *                                                                                             *
 *    This is the counterpart to the Set_Factory function. It will return with a factory       *
 *    pointer that is associated with the object type specified.                               *
 *                                                                                             *
 * INPUT:   rtti  -- The RTTI of the object type to find the factory for.                      *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the factory (if present) that can manufacture the        *
 *          object type specified.                                                             *
 *                                                                                             *
 * WARNINGS:   If this returns a non-NULL pointer, then the factory is probably already busy   *
 *             producing another unit of that category.                                        *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
FactoryClass* HouseClass::Fetch_Factory(RTTIType rtti) const
{
    int factory_index = -1;

    switch (rtti) {
    case RTTI_INFANTRY:
    case RTTI_INFANTRYTYPE:
        factory_index = InfantryFactory;
        break;

    case RTTI_UNIT:
    case RTTI_UNITTYPE:
        factory_index = UnitFactory;
        break;

    case RTTI_BUILDING:
    case RTTI_BUILDINGTYPE:
        factory_index = BuildingFactory;
        break;

    case RTTI_AIRCRAFT:
    case RTTI_AIRCRAFTTYPE:
        factory_index = AircraftFactory;
        break;

    case RTTI_VESSEL:
    case RTTI_VESSELTYPE:
        factory_index = VesselFactory;
        break;

    default:
        factory_index = -1;
        break;
    }

    /*
    **	Fetch the actual pointer to the factory object. If there is
    **	no object factory that matches the specified rtti type, then
    **	null is returned.
    */
    if (factory_index != -1) {
        return (Factories.Raw_Ptr(factory_index));
    }
    return (NULL);
}

/***********************************************************************************************
 * HouseClass::Set_Factory -- Assign specified factory to house tracking.                      *
 *                                                                                             *
 *    Call this routine when a factory has been created and it now must be passed on to the    *
 *    house for tracking purposes. The house maintains several factory pointers and this       *
 *    routine will ensure that the factory pointer gets stored correctly.                      *
 *                                                                                             *
 * INPUT:   rtti  -- The RTTI of the object the factory it to manufacture.                     *
 *                                                                                             *
 *          factory  -- The factory object pointer.                                            *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Set_Factory(RTTIType rtti, FactoryClass* factory)
{
    int* factory_index = 0;

    assert(rtti != RTTI_NONE);

    switch (rtti) {
    case RTTI_UNIT:
    case RTTI_UNITTYPE:
        factory_index = &UnitFactory;
        break;

    case RTTI_INFANTRY:
    case RTTI_INFANTRYTYPE:
        factory_index = &InfantryFactory;
        break;

    case RTTI_VESSEL:
    case RTTI_VESSELTYPE:
        factory_index = &VesselFactory;
        break;

    case RTTI_BUILDING:
    case RTTI_BUILDINGTYPE:
        factory_index = &BuildingFactory;
        break;

    case RTTI_AIRCRAFT:
    case RTTI_AIRCRAFTTYPE:
        factory_index = &AircraftFactory;
        break;
    }

    assert(factory_index != NULL);

    /*
    **	Assign the factory to the appropriate slot. For the case of clearing
    **	the factory out, then -1 is assigned.
    */
    if (factory != NULL) {
        *factory_index = factory->ID;
    } else {
        *factory_index = -1;
    }
}

/***********************************************************************************************
 * HouseClass::Factory_Count -- Fetches the number of factories for specified type.            *
 *                                                                                             *
 *    This routine will count the number of factories owned by this house that can build       *
 *    objects of the specified type.                                                           *
 *                                                                                             *
 * INPUT:   rtti  -- The type of object (RTTI) that the factories are to be counted for.       *
 *                                                                                             *
 * OUTPUT:  Returns with the number of factories that can build the object type specified.     *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/30/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
int HouseClass::Factory_Count(RTTIType rtti) const
{
    int const* ptr = ((HouseClass*)this)->Factory_Counter(rtti);
    if (ptr != NULL) {
        return (*ptr);
    }
    return (0);
}

/***********************************************************************************************
 * HouseClass::Get_Quantity -- Gets the quantity of the building type specified.               *
 *                                                                                             *
 *    This will return the total number of buildings of that type owned by this house.         *
 *                                                                                             *
 * INPUT:   building -- The building type to check.                                            *
 *                                                                                             *
 * OUTPUT:  Returns with the number of buildings of that type owned by this house.             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
int HouseClass::Get_Quantity(StructType building)
{
    return (BQuantity[building]);
}

/***********************************************************************************************
 * HouseClass::Read_INI -- Reads house specific data from INI.                                 *
 *                                                                                             *
 *    This routine reads the house specific data for a particular                              *
 *    scenario from the scenario INI file. Typical data includes starting                      *
 *    credits, maximum unit count, etc.                                                        *
 *                                                                                             *
 * INPUT:   buffer   -- Pointer to loaded scenario INI file.                                   *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   05/24/1994 JLB : Created.                                                                 *
 *   05/18/1995 JLB : Creates all houses.                                                      *
 *=============================================================================================*/
void HouseClass::Read_INI(CCINIClass& ini)
{
    HouseClass* p;     // Pointer to current player data.
    char const* hname; //	Pointer to house name.

    for (HousesType index = HOUSE_FIRST; index < HOUSE_COUNT; index++) {
        hname = HouseTypeClass::As_Reference(index).IniName;

        p = new HouseClass(index);
        p->Control.TechLevel = ini.Get_Int(hname, "TechLevel", Scen.Scenario);
        p->Control.MaxBuilding = ini.Get_Int(hname, "MaxBuilding", p->Control.MaxBuilding);
        p->Control.MaxUnit = ini.Get_Int(hname, "MaxUnit", p->Control.MaxUnit);
        p->Control.MaxInfantry = ini.Get_Int(hname, "MaxInfantry", p->Control.MaxInfantry);
        p->Control.MaxVessel = ini.Get_Int(hname, "MaxVessel", p->Control.MaxVessel);
        if (p->Control.MaxVessel == 0)
            p->Control.MaxVessel = p->Control.MaxUnit;
        p->Control.InitialCredits = ini.Get_Int(hname, "Credits", 0) * 100;
        p->Credits = p->Control.InitialCredits;

        int iq = ini.Get_Int(hname, "IQ", 0);
        if (iq > Rule.MaxIQ)
            iq = 1;
        p->IQ = p->Control.IQ = iq;

        p->Control.Edge = ini.Get_SourceType(hname, "Edge", SOURCE_NORTH);
        p->IsPlayerControl = ini.Get_Bool(hname, "PlayerControl", false);

        int owners = ini.Get_Owners(hname, "Allies", (1 << HOUSE_NEUTRAL));
        p->Make_Ally(index);
        p->Make_Ally(HOUSE_NEUTRAL);
        for (HousesType h = HOUSE_FIRST; h < HOUSE_COUNT; h++) {
            if ((owners & (1 << h)) != 0) {
                p->Make_Ally(h);
            }
        }
    }
}

/***********************************************************************************************
 * HouseClass::Write_INI -- Writes the house data to the INI database.                         *
 *                                                                                             *
 *    This routine will write out all data necessary to recreate it in anticipation of a       *
 *    new scenario. All houses (that are active) will have their scenario type data written    *
 *    out.                                                                                     *
 *                                                                                             *
 * INPUT:   ini   -- Reference to the INI database to write the data to.                       *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Write_INI(CCINIClass& ini)
{
    /*
    **	The identity house control object. Only if the house value differs from the
    **	identity, will the data be written out.
    */
    HouseStaticClass control;

    for (HousesType i = HOUSE_FIRST; i < HOUSE_COUNT; i++) {
        HouseClass* p = As_Pointer(i);

        if (p != NULL) {
            char const* name = p->Class->IniName;

            ini.Clear(name);
            if (i >= HOUSE_MULTI1)
                continue;

            if (p->Control.InitialCredits != control.InitialCredits) {
                ini.Put_Int(name, "Credits", (int)(p->Control.InitialCredits / 100));
            }

            if (p->Control.Edge != control.Edge) {
                ini.Put_SourceType(name, "Edge", p->Control.Edge);
            }

            if (p->Control.MaxUnit > 0 && p->Control.MaxUnit != control.MaxUnit) {
                ini.Put_Int(name, "MaxUnit", p->Control.MaxUnit);
            }

            if (p->Control.MaxInfantry > 0 && p->Control.MaxInfantry != control.MaxInfantry) {
                ini.Put_Int(name, "MaxInfantry", p->Control.MaxInfantry);
            }

            if (p->Control.MaxBuilding > 0 && p->Control.MaxBuilding != control.MaxBuilding) {
                ini.Put_Int(name, "MaxBuilding", p->Control.MaxBuilding);
            }

            if (p->Control.MaxVessel > 0 && p->Control.MaxVessel != control.MaxVessel) {
                ini.Put_Int(name, "MaxVessel", p->Control.MaxVessel);
            }

            if (p->Control.TechLevel != control.TechLevel) {
                ini.Put_Int(name, "TechLevel", p->Control.TechLevel);
            }

            if (p->Control.IQ != control.IQ) {
                ini.Put_Int(name, "IQ", p->Control.IQ);
            }

            if (p->IsPlayerControl != false && p != PlayerPtr) {
                ini.Put_Bool(name, "PlayerControl", p->IsPlayerControl);
            }

            ini.Put_Owners(name, "Allies", p->Control.Allies & ~((1 << p->Class->House) | (1 << HOUSE_NEUTRAL)));
        }
    }
}

/***********************************************************************************************
 * HouseClass::Is_No_YakMig -- Determines if no more yaks or migs should be allowed.           *
 *                                                                                             *
 *    This routine will examine the current yak and mig situation verses airfields. If there   *
 *    are equal aircraft to airfields, then this routine will return TRUE.                     *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  bool; Are all airfields full and thus no more yaks or migs are allowed?            *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/23/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Is_No_YakMig(void) const
{
    int quantity = AQuantity[AIRCRAFT_YAK] + AQuantity[AIRCRAFT_MIG];

    /*
    **	Adjust the quantity down one if there is an aircraft in production. This will
    **	allow production to resume after being held.
    */
    FactoryClass const* factory = Fetch_Factory(RTTI_AIRCRAFT);
    if (factory != NULL && factory->Get_Object() != NULL) {
        AircraftClass const* air = (AircraftClass const*)factory->Get_Object();
        if (*air == AIRCRAFT_MIG || *air == AIRCRAFT_YAK) {
            quantity -= 1;
        }
    }

    if (quantity >= BQuantity[STRUCT_AIRSTRIP]) {
        return (true);
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::Is_Hack_Prevented -- Is production of the specified type and id prohibted?      *
 *                                                                                             *
 *    This is a special hack check routine to see if the object type and id specified is       *
 *    prevented from being produced. The Yak and the Mig are so prevented if there would be    *
 *    insufficient airfields for them to land upon.                                            *
 *                                                                                             *
 * INPUT:   rtti  -- The RTTI type of the value specified.                                     *
 *                                                                                             *
 *          value -- The type number (according to the RTTI type specified).                   *
 *                                                                                             *
 * OUTPUT:  bool; Is production of this object prohibited?                                     *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/23/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Is_Hack_Prevented(RTTIType rtti, int value) const
{
    if (rtti == RTTI_AIRCRAFTTYPE && (value == AIRCRAFT_MIG || value == AIRCRAFT_YAK)) {
        return (Is_No_YakMig());
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::Fire_Sale -- Cause all buildings to be sold.                                    *
 *                                                                                             *
 *    This routine will sell back all buildings owned by this house.                           *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  bool; Was a fire sale performed?                                                   *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/23/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Fire_Sale(void)
{
    if (CurBuildings > 0) {
        for (int index = 0; index < Buildings.Count(); index++) {
            BuildingClass* b = Buildings.Ptr(index);

            if (b != NULL && !b->IsInLimbo && b->House == this && b->Strength > 0) {
                b->Sell_Back(1);
            }
        }
        return (true);
    }
    return (false);
}

/***********************************************************************************************
 * HouseClass::Do_All_To_Hunt -- Send all units to hunt.                                       *
 *                                                                                             *
 *    This routine will cause all combatants of this house to go into hunt mode. The effect of *
 *    this is to throw everything this house has to muster at the enemies of this house.       *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/23/1996 JLB : Created.                                                                 *
 *   10/02/1996 JLB : Handles aircraft too.                                                    *
 *=============================================================================================*/
void HouseClass::Do_All_To_Hunt(void) const
{
    int index;

    for (index = 0; index < Units.Count(); index++) {
        UnitClass* unit = Units.Ptr(index);

        if (unit->House == this && unit->IsDown && !unit->IsInLimbo) {
            if (unit->Team)
                unit->Team->Remove(unit);
            unit->Assign_Mission(MISSION_HUNT);
        }
    }

    for (index = 0; index < Infantry.Count(); index++) {
        InfantryClass* infantry = Infantry.Ptr(index);

        if (infantry->House == this && infantry->IsDown && !infantry->IsInLimbo) {
            if (infantry->Team)
                infantry->Team->Remove(infantry);
            infantry->Assign_Mission(MISSION_HUNT);
        }
    }

    for (index = 0; index < Vessels.Count(); index++) {
        VesselClass* vessel = Vessels.Ptr(index);

        if (vessel->House == this && vessel->IsDown && !vessel->IsInLimbo) {
            if (vessel->Team)
                vessel->Team->Remove(vessel);
            vessel->Assign_Mission(MISSION_HUNT);
        }
    }

    for (index = 0; index < Aircraft.Count(); index++) {
        AircraftClass* aircraft = Aircraft.Ptr(index);

        if (aircraft->House == this && aircraft->IsDown && !aircraft->IsInLimbo) {
            if (aircraft->Team)
                aircraft->Team->Remove(aircraft);
            aircraft->Assign_Mission(MISSION_HUNT);
        }
    }
}

/***********************************************************************************************
 * HouseClass::Is_Allowed_To_Ally -- Determines if this house is allied to make allies.        *
 *                                                                                             *
 *    Use this routine to determine if this house is legally allowed to ally with the          *
 *    house specified. There are many reason why an alliance is not allowed. Typically, this   *
 *    is when there would be no more opponents left to fight or if this house has been         *
 *    defeated.                                                                                *
 *                                                                                             *
 * INPUT:   house -- The house that alliance with is desired.                                  *
 *                                                                                             *
 * OUTPUT:  bool; Is alliance with the house specified prohibited?                             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/23/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
bool HouseClass::Is_Allowed_To_Ally(HousesType house) const
{
    /*
    **	Is not allowed to ally with a house that is patently invalid, such
    **	as one that is illegally defined.
    */
    if (house == HOUSE_NONE) {
        return (false);
    }

    /*
    **	One cannot ally twice with the same house.
    */
    if (Is_Ally(house)) {
        return (false);
    }

    /*
    **	If the scenario is being set up, then alliances are always
    **	allowed. No further checking is required.
    */
    if (ScenarioInit) {
        return (true);
    }

    /*
    **	Alliances (outside of scneario init time) are allowed only if
    **	this is a multiplayer game. Otherwise, they are prohibited.
    */
    if (Session.Type == GAME_NORMAL) {
        return (false);
    }

    /*
    **	When the house is defeated, it can no longer make alliances.
    */
    if (IsDefeated) {
        return (false);
    }

#ifdef FIXIT_VERSION_3
    // Fix to prevent ally with computer.
    if (!HouseClass::As_Pointer(house)->IsHuman) {
        return (false);
    }
#else //	FIXIT_VERSION_3
#ifdef FIXIT_NO_COMP_ALLY
    // Fix to prevent ally with computer.
    if (PlayingAgainstVersion > VERSION_RED_ALERT_104 && !HouseClass::As_Pointer(house)->IsHuman) {
        return (false);
    }
#endif
#endif //	FIXIT_VERSION_3

    /*
    **	Count the number of active houses in the game as well as the
    **	number of existing allies with this house.
    */
    int housecount = 0;
    int allycount = 0;
    for (HousesType house2 = HOUSE_MULTI1; house2 < HOUSE_COUNT; house2++) {
        HouseClass* hptr = HouseClass::As_Pointer(house2);
        if (hptr != NULL && hptr->IsActive && !hptr->IsDefeated) {
            housecount++;
            if (Is_Ally(hptr)) {
                allycount++;
            }
        }
    }

    /*
    **	Alliance is not allowed if there wouldn't be any enemies left to
    **	fight.
    */
    if (housecount == allycount + 1) {
        return (false);
    }

    return (true);
}

/***********************************************************************************************
 * HouseClass::Computer_Paranoid -- Cause the computer players to becom paranoid.              *
 *                                                                                             *
 *    This routine will cause the computer players to become suspicious of the human           *
 *    players and thus the computer players will band together in order to defeat the          *
 *    human players.                                                                           *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/23/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Computer_Paranoid(void)
{
    if (Session.Type != GAME_GLYPHX_MULTIPLAYER) { // Re-enable this for multiplayer if we support classic team/ally
                                                   // mode. ST - 10/29/2019

        /*
        **	Loop through every computer controlled house and make allies with all other computer
        **	controlled houses and then make enemies with all other human controlled houses.
        */
        for (HousesType house = HOUSE_MULTI1; house < HOUSE_COUNT; house++) {
            HouseClass* hptr = HouseClass::As_Pointer(house);
            if (hptr != NULL && hptr->IsActive && !hptr->IsDefeated && !hptr->IsHuman) {
                hptr->IsParanoid = true;

                /*
                **	Break alliance with every human it is allied with and make friends with
                **	any other computer players.
                */
                for (HousesType house2 = HOUSE_MULTI1; house2 < HOUSE_COUNT; house2++) {
                    HouseClass* hptr2 = HouseClass::As_Pointer(house2);
                    if (hptr2 != NULL && hptr2->IsActive && !hptr2->IsDefeated) {
                        if (hptr2->IsHuman) {
                            hptr->Make_Enemy(house2);
                        } else {
                            hptr->Make_Ally(house2);
                        }
                    }
                }
            }
        }
    }
}

/***********************************************************************************************
 * HouseClass::Adjust_Power -- Adjust the power value of the house.                            *
 *                                                                                             *
 *    This routine will update the power output value of the house. It will cause any buildgins*
 *    that need to be redrawn to do so.                                                        *
 *                                                                                             *
 * INPUT:   adjust   -- The amount to adjust the power output value.                           *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   11/01/1996 BWG : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Adjust_Power(int adjust)
{
    Power += adjust;

    Update_Spied_Power_Plants();
}

/***********************************************************************************************
 * HouseClass::Adjust_Drain -- Adjust the power drain value of the house.                      *
 *                                                                                             *
 *    This routine will update the drain value of the house. It will cause any buildings that  *
 *    need to be redraw to do so.                                                              *
 *                                                                                             *
 * INPUT:   adjust   -- The amount to adjust the drain (positive means more drain).            *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   11/01/1996 BWG : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Adjust_Drain(int adjust)
{
    Drain += adjust;
    Update_Spied_Power_Plants();
}

/***********************************************************************************************
 * HouseClass::Update_Spied_Power_Plants -- Redraw power graphs on spied-upon power plants.    *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   10/11/1996 BWG : Created.                                                                 *
 *=============================================================================================*/
void HouseClass::Update_Spied_Power_Plants(void)
{
    int count = CurrentObject.Count();
    if (count) {
        for (int index = 0; index < count; index++) {
            ObjectClass const* tech = CurrentObject[index];
            if (tech && tech->What_Am_I() == RTTI_BUILDING) {
                BuildingClass* bldg = (BuildingClass*)tech;
                if (!bldg->IsOwnedByPlayer && *bldg == STRUCT_POWER || *bldg == STRUCT_ADVANCED_POWER) {
                    if (bldg->Spied_By() & (1 << (PlayerPtr->Class->House))) {
                        bldg->Mark(MARK_CHANGE);
                    }
                }
            }
        }
    }
}

/***********************************************************************************************
 * HouseClass::Find_Cell_In_Zone -- Finds a legal placement cell within the zone.              *
 *                                                                                             *
 *    Use this routine to determine where the specified object should go if it were to go      *
 *    some random (but legal) location within the zone specified.                              *
 *                                                                                             *
 * INPUT:   techno   -- The object that is desirous of going into the zone specified.          *
 *                                                                                             *
 *          zone     -- The zone to find a location within.                                    *
 *                                                                                             *
 * OUTPUT:  Returns with the cell that the specified object could be placed in the zone. If    *
 *          no valid location could be found, then 0 is returned.                              *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   11/01/1996 JLB : Created.                                                                 *
 *   11/04/1996 JLB : Not so strict on zone requirement.                                       *
 *=============================================================================================*/
CELL HouseClass::Find_Cell_In_Zone(TechnoClass const* techno, ZoneType zone) const
{
    if (techno == NULL)
        return (0);

    int bestval = -1;
    int bestcell = 0;
    TechnoTypeClass const* ttype = techno->Techno_Type_Class();

    /*
    **	Pick a random location within the zone specified.
    */
    CELL trycell = Random_Cell_In_Zone(zone);

    short const* list = NULL;
    if (techno->What_Am_I() == RTTI_BUILDING) {
        list = techno->Occupy_List(true);
    }

#if TF_DEV_BUILD // TF_AI_DIAG -- record which predicate rejected every cell, so a placement
                 // failure says WHY there was nowhere to build rather than just that there was.
    TF_PlaceScan.Radar = 0;
    TF_PlaceScan.Zone = 0;
    TF_PlaceScan.Legal = 0;
    TF_PlaceScan.Proximity = 0;
    TF_PlaceScan.Ok = 0;
    TF_PlaceScan.Center = Center;
    TF_PlaceScan.Radius = Radius;
#endif

    /*
    **	Find a legal placement position as close as possible to the picked location while still
    **	remaining within the zone.
    */
    for (CELL cell = 0; cell < MAP_CELL_TOTAL; cell++) {
        //		if (Map.In_Radar(cell)) {
        if (!Map.In_Radar(cell)) {
#if TF_DEV_BUILD
            TF_PlaceScan.Radar++;
#endif
            continue;
        }
        /*
        **	Restrict the sweep to the requested zone, so the zone the defence
        **	rating picked is where the building actually lands and each pass of
        **	the try-any-zone fallback searches fresh ground instead of
        **	re-scanning one identical candidate set.
        */
        if (Which_Zone(cell) != zone) {
#if TF_DEV_BUILD
            TF_PlaceScan.Zone++;
#endif
            continue;
        }
        {
            bool ok = ttype->Legal_Placement(cell);
#if TF_DEV_BUILD
            if (!ok) {
                TF_PlaceScan.Legal++;
            }
#endif

            /*
            **	Another (adjacency) check is required for buildings.
            */
            if (ok && list != NULL && !Map.Passes_Proximity_Check(ttype, techno->House->Class->House, list, cell)) {
                ok = false;
#if TF_DEV_BUILD
                TF_PlaceScan.Proximity++;
#endif
            }

            if (ok) {
#if TF_DEV_BUILD
                TF_PlaceScan.Ok++;
#endif
                int dist = Distance(Cell_Coord(cell), Cell_Coord(trycell));
                if (bestval == -1 || dist < bestval) {
                    bestval = dist;
                    bestcell = cell;
                }
            }
        }
    }

    /*
    **	Return the best location to move to.
    */
    return (bestcell);
}

/***********************************************************************************************
 * HouseClass::TF_Find_Naval_Cell -- Finds a coastal placement cell for a water-bound building.*
 *                                                                                             *
 *    Visits the whole map with the same legality + proximity predicates as the zone scan and  *
 *    picks the legal cell nearest the base centre, preferring cells on the water zone the     *
 *    naval assessment chose (the water that reaches the enemy) over any other qualifying      *
 *    water. Ponds are never accepted: a yard whose ships can't leave their puddle is dead     *
 *    money however close it is.                                                               *
 *                                                                                             *
 * OUTPUT:  The cell to place at, or 0 if no legal coastal cell exists.                        *
 *=============================================================================================*/
CELL HouseClass::TF_Find_Naval_Cell(BuildingClass const* building) const
{
    assert(Houses.ID(this) == ID);

    if (building == NULL) {
        return (0);
    }
    TechnoTypeClass const* ttype = building->Techno_Type_Class();
    short const* list = building->Occupy_List(true);
    CELL center = Coord_Cell(Center);
    if (center <= 0) {
        return (0);
    }

    int tzone = 0;
    int tsize = 0;
    bool tcoastal = false;
    TF_Naval_Assessment(tzone, tsize, tcoastal);

#if TF_DEV_BUILD // TF_AI_DIAG -- feed the PLACE-FAIL reject counters from this scan too, so a
                 // failed naval placement reports its predicate breakdown like a land one.
    TF_PlaceScan.Radar = 0;
    TF_PlaceScan.Zone = 0; // pond rejects, this scan having no zone-ring predicate
    TF_PlaceScan.Legal = 0;
    TF_PlaceScan.Proximity = 0;
    TF_PlaceScan.Ok = 0;
    TF_PlaceScan.Center = Center;
    TF_PlaceScan.Radius = Radius;
#endif

    CELL bestcell = 0;
    int bestval = -1;
    bool bestontarget = false;
    for (CELL cell = 0; cell < MAP_CELL_TOTAL; cell++) {
        if (!Map.In_Radar(cell)) {
#if TF_DEV_BUILD
            TF_PlaceScan.Radar++;
#endif
            continue;
        }
        if (!ttype->Legal_Placement(cell)) {
#if TF_DEV_BUILD
            TF_PlaceScan.Legal++;
#endif
            continue;
        }
        if (list != NULL && !Map.Passes_Proximity_Check(ttype, Class->House, list, cell)) {
#if TF_DEV_BUILD
            TF_PlaceScan.Proximity++;
#endif
            continue;
        }
        int wz = Map[cell].Zones[MZONE_WATER];
        bool ontarget = (tzone != 0 && wz == tzone);
        if (!ontarget
            && (wz <= 0 || wz >= (int)ARRAY_SIZE(TF_WaterZoneSize) || TF_WaterZoneSize[wz] < TF_NAVAL_POND_MIN)) {
#if TF_DEV_BUILD
            TF_PlaceScan.Zone++;
#endif
            continue;
        }
#if TF_DEV_BUILD
        TF_PlaceScan.Ok++;
#endif
        int dist = Distance(Cell_Coord(cell), Cell_Coord(center));
        if (bestcell == 0 || (ontarget && !bestontarget) || (ontarget == bestontarget && dist < bestval)) {
            bestcell = cell;
            bestval = dist;
            bestontarget = ontarget;
        }
    }

#if TF_DEV_BUILD // TF_AI_DIAG -- one line per naval placement attempt; failures also surface
                 // through the caller's PLACE-FAIL line with the counters set above.
    {
        FILE* _tfdbg = TF_AI_Diag_File();
        if (_tfdbg != NULL) {
            fprintf(_tfdbg, "F%ld H%d NAVAL-PLACE %s cell=(%d,%d) ontarget=%d dist=%d tzone=%d ok=%d\n", (long)Frame,
                    (int)Class->House, building->Class->IniName, (int)Cell_X(bestcell), (int)Cell_Y(bestcell),
                    (int)bestontarget, bestval, tzone, TF_PlaceScan.Ok);
            fflush(_tfdbg);
        }
    }
#endif

    return (bestcell);
}

/***********************************************************************************************
 * HouseClass::TF_Naval_Patrol_Cell -- Picks a random cell of the given water zone.            *
 *                                                                                             *
 *    Destination source for the blind naval patrol: any cell of the zone is reachable by      *
 *    every ship already on that zone (connectedness is what a zone id means), so patrol       *
 *    orders can never feed the unreachable-target pathfinder storm that land waypoints        *
 *    would. Two passes -- count then fetch -- so only one synced random number is consumed.   *
 *                                                                                             *
 * OUTPUT:  A cell of the zone, or 0 if the zone id matches no radar cell.                     *
 *=============================================================================================*/
CELL HouseClass::TF_Naval_Patrol_Cell(int wzone) const
{
    if (wzone <= 0) {
        return (0);
    }
    int count = 0;
    CELL cell;
    for (cell = 0; cell < MAP_CELL_TOTAL; cell++) {
        if (Map.In_Radar(cell) && Map[cell].Zones[MZONE_WATER] == wzone) {
            count++;
        }
    }
    if (count == 0) {
        return (0);
    }
    int want = Random_Pick(0, count - 1);
    for (cell = 0; cell < MAP_CELL_TOTAL; cell++) {
        if (Map.In_Radar(cell) && Map[cell].Zones[MZONE_WATER] == wzone) {
            if (want-- == 0) {
                return (cell);
            }
        }
    }
    return (0);
}

/***********************************************************************************************
 * HouseClass::Random_Cell_In_Zone -- Find a (technically) legal cell in the zone specified.   *
 *                                                                                             *
 *    This routine will pick a random cell within the zone specified. The pick will be         *
 *    clipped to the map edge when necessary.                                                  *
 *                                                                                             *
 * INPUT:   zone  -- The zone to pick a cell from.                                             *
 *                                                                                             *
 * OUTPUT:  Returns with a picked cell within the zone. If the entire zone lies outside of the *
 *          map, then a cell in the core zone is returned instead.                             *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   11/04/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
CELL HouseClass::Random_Cell_In_Zone(ZoneType zone) const
{
    COORDINATE coord = 0;
    int maxdist = 0;
    int distance;
    DirType facing;

    switch (zone) {
    case ZONE_CORE:
        coord = Coord_Scatter(Center, Random_Pick(0, Radius), true);
        break;

    case ZONE_NORTH:
        maxdist = min(Radius * 3, (Coord_Y(Center) - Cell_To_Lepton(Map.MapCellY)) - CELL_LEPTON_H);
        if (maxdist < 0) {
            break;
        }
        distance = Random_Pick(min(Radius * 2, maxdist), min(Radius * 3, maxdist));
        facing = Random_Pick(DIR_N, DIR_E);
        coord = Coord_Move(Center, (DirType)(facing - ((DirType)32)), distance);
        break;

    case ZONE_EAST:
        maxdist = min(Radius * 3, (Cell_To_Lepton(Map.MapCellX + Map.MapCellWidth) - Coord_X(Center)) - CELL_LEPTON_W);
        if (maxdist < 0) {
            break;
        }
        distance = Random_Pick(min(Radius * 2, maxdist), min(Radius * 3, maxdist));
        facing = Random_Pick(DIR_NE, DIR_SE);
        coord = Coord_Move(Center, facing, distance);
        break;

    case ZONE_SOUTH:
        maxdist = min(Radius * 3, (Cell_To_Lepton(Map.MapCellY + Map.MapCellHeight) - Coord_Y(Center)) - CELL_LEPTON_H);
        if (maxdist < 0) {
            break;
        }
        distance = Random_Pick(min(Radius * 2, maxdist), min(Radius * 3, maxdist));
        facing = Random_Pick(DIR_SE, DIR_SW);
        coord = Coord_Move(Center, facing, distance);
        break;

    case ZONE_WEST:
        maxdist = min(Radius * 3, (Coord_X(Center) - Cell_To_Lepton(Map.MapCellX)) - CELL_LEPTON_W);
        if (maxdist < 0) {
            break;
        }
        distance = Random_Pick(min(Radius * 2, maxdist), min(Radius * 3, maxdist));
        facing = Random_Pick(DIR_SW, DIR_NW);
        coord = Coord_Move(Center, facing, distance);
        break;
    }

    /*
    **	Double check that the location is valid and if so, convert it into a cell
    **	number.
    */
    CELL cell;
    if (coord == 0 || !Map.In_Radar(Coord_Cell(coord))) {
        if (zone == ZONE_CORE) {

            /*
            **	Finding a cell within the core failed, so just pick the center
            **	cell. This cell is guaranteed to be valid.
            */
            cell = Coord_Cell(Center);
        } else {

            /*
            **	If the edge fails, then try to find a cell within the core.
            */
            cell = Random_Cell_In_Zone(ZONE_CORE);
        }
    } else {
        cell = Coord_Cell(coord);
    }

    /*
    **	If the randomly picked location is not in the legal map area, then clip it to
    **	the legal map area.
    */
    if (!Map.In_Radar(cell)) {
        int x = Cell_X(cell);
        int y = Cell_Y(cell);

        if (x < Map.MapCellX)
            x = Map.MapCellX;
        if (y < Map.MapCellY)
            y = Map.MapCellY;
        if (x >= Map.MapCellX + Map.MapCellWidth)
            x = Map.MapCellX + Map.MapCellWidth - 1;
        if (y >= Map.MapCellY + Map.MapCellHeight)
            y = Map.MapCellY + Map.MapCellHeight - 1;
        cell = XY_Cell(x, y);
    }
    return (cell);
}

/***********************************************************************************************
 * HouseClass::Get_Ally_Flags --  Get the bit flags denoting the allies this house has.		  *
 *                                                                                             *
 * INPUT:   none *
 *                                                                                             *
 * OUTPUT:  Returns the bit field storing which houses this house is allied with.              *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   09/12/2019 JAS : Created.                                                                 *
 *=============================================================================================*/
unsigned HouseClass::Get_Ally_Flags()
{
    return Allies;
}

/***********************************************************************************************
 * HouseClass::Check_Pertinent_Structures -- See if any useful structures remain               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   1/31/2020 3:34PM ST : Created.                                                            *
 *=============================================================================================*/
void HouseClass::Check_Pertinent_Structures(void)
{
    /*
    ** New default win mode to avoid griefing. ST - 1/31/2020 3:33PM
    **
    ** Game is over when no pertinent structures remain
    */

    if (!Special.IsEarlyWin) {
        return;
    }

    if (IsToDie || IsToWin || IsToLose) {
        return;
    }

    // MBL 07.15.2020 - Prevention of recent issue with constant "player defeated logic" and message to client spamming
    // Per https://jaas.ea.com/browse/TDRA-7433
    //
    if (IsDefeated) {
        return;
    }

    bool any_good_buildings = false;

    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass* b = Buildings.Ptr(index);

        if (b && b->IsActive && b->House == this) {
            if (!b->Class->IsWall && *b != STRUCT_APMINE && *b != STRUCT_AVMINE) {
                if (!Special.ModernBalance
                    || (*b != STRUCT_SHIP_YARD && *b != STRUCT_FAKE_YARD && *b != STRUCT_SUB_PEN
                        && *b != STRUCT_FAKE_PEN && *b != STRUCT_TDGYARD && *b != STRUCT_TDNPEN)) {
                    if (!b->IsInLimbo && b->Strength > 0) {
                        any_good_buildings = true;
                        break;
                    }
                }
            }
        }
    }

    if (!any_good_buildings) {
        for (int index = 0; index < Units.Count(); index++) {
            UnitClass* unit = Units.Ptr(index);

            if (unit && unit->IsActive && unit->Class->Is_MCV() && unit->House == this) {
                if (!unit->IsInLimbo && unit->Strength > 0) {
                    any_good_buildings = true;
                    break;
                }
            }
        }
    }

    if (!any_good_buildings) {
        // TF DIAGNOSTIC 2026-05-27: when Check_Pertinent_Structures decides
        // the player has lost, log a snapshot of the house's building/unit
        // inventory so we can diagnose which check failed (was the TDFACT
        // not in Buildings? Wrong house? IsInLimbo? Strength 0?). Stub
        // under #if 0 once verified per [[feedback-keep-diagnostics-until-v1]].
#if 0 // TF DIAG — OFF for release (was #if 1; flip to 1 to re-enable logging).
        {
            const char* up = getenv("USERPROFILE");
            char p[512];
            if (up) snprintf(p, sizeof(p), "%s/Documents/CnCRemastered/tf_pertinent.log", up);
            else strcpy(p, "tf_pertinent.log");
            FILE* f = fopen(p, "a");
            if (f) {
                fprintf(f, "[Check_Pertinent_Structures] FLAG_TO_DIE house=%d ActLike=%d Buildings=%d Units=%d\n",
                        (int)Class->House, (int)ActLike, Buildings.Count(), Units.Count());
                for (int i = 0; i < Buildings.Count(); i++) {
                    BuildingClass* b = Buildings.Ptr(i);
                    if (b && b->House == this) {
                        fprintf(f, "  b[%d] IniName=%s Type=%d IsActive=%d IsInLimbo=%d Str=%d IsWall=%d\n",
                                i, b->Class->IniName, (int)b->Class->Type, (int)b->IsActive,
                                (int)b->IsInLimbo, (int)b->Strength, (int)b->Class->IsWall);
                    }
                }
                for (int i = 0; i < Units.Count(); i++) {
                    UnitClass* u = Units.Ptr(i);
                    if (u && u->House == this) {
                        fprintf(f, "  u[%d] IniName=%s Type=%d IsActive=%d IsInLimbo=%d Str=%d\n",
                                i, u->Class->IniName, (int)u->Class->Type, (int)u->IsActive,
                                (int)u->IsInLimbo, (int)u->Strength);
                    }
                }
                fclose(f);
            }
        }
#endif
        Flag_To_Die();
    }
}

/***********************************************************************************************
 * HouseClass::Init_Unit_Trackers -- Allocate the unit trackers for the house                  *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   4/23/2020 11:06PM ST : Created.                                                           *
 *=============================================================================================*/
void HouseClass::Init_Unit_Trackers(void)
{
    AircraftTotals.Init();
    InfantryTotals.Init();
    UnitTotals.Init();
    BuildingTotals.Init();
    VesselTotals.Init();

    DestroyedAircraft.Init();
    DestroyedInfantry.Init();
    DestroyedUnits.Init();
    DestroyedBuildings.Init();
    DestroyedVessels.Init();

    CapturedBuildings.Init();
    TotalCrates.Init();
}
