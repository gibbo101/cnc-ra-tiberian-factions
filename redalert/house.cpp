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

// The AI house IQ for a lobby difficulty; difficulty changes only IQ-gated behaviour. Every AI keeps MaxIQ
// until a lobby difficulty has arrived, so a silent client can't demote it.
bool TFLobbyAIDifficultySet = false;

int TF_AI_IQ_From_Difficulty(DiffType diff)
{
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
    // TF: GDI and Nod houses act like Greece and the USSR, so ActLike-gated code treats them as Allied and
    // Soviet until Init_Data gives a multiplayer house its own.
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
    , IsFirestormLive(false)
    , IsFirestormPowerLow(false)
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
    , TFDropBayTimer(0)
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
    , DropFactories(0)
    , VesselFactories(0)
    , Power(0)
    , Drain(0)
    , AircraftFactory(-1)
    , InfantryFactory(-1)
    , UnitFactory(-1)
    , BuildingFactory(-1)
    , DropFactory(-1)
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
    , TFEMPDest(0)
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

    // TF: GDI Ion Cannon. TD's 10-minute recharge (ION_CANNON_GONE_TIME); powered, so low power suspends it.
    new (&SuperWeapon[SPC_TD_ION_CANNON]) SuperClass(TICKS_PER_MINUTE * 10,
                                                     true,
                                                     VOX_TD_ION_CHARGING,
                                                     VOX_TD_ION_READY,
                                                     VOX_NOT_READY,
                                                     VOX_INSUFFICIENT_POWER);

    // TF: TS Ion Cannon, from the uplink plug. Its own slot, so a house holding both ion cannons fields both;
    // TS's 10-minute recharge and the TD cannon's charge voices (the same EVA wording).
    new (&SuperWeapon[SPC_TS_ION_CANNON]) SuperClass(TICKS_PER_MINUTE * 10,
                                                     true,
                                                     VOX_TD_ION_CHARGING,
                                                     VOX_TD_ION_READY,
                                                     VOX_NOT_READY,
                                                     VOX_INSUFFICIENT_POWER);

    // TF: TS Drop Pods (the TSPODS plug). Orbital, so unpowered like the paratroop drops.
    new (&SuperWeapon[SPC_TS_DROPPODS])
        SuperClass(TICKS_PER_MINUTE * 5, false, VOX_NONE, VOX_NONE, VOX_NOT_READY, VOX_NOT_READY);

    // TF: TS Hunter Seeker (TSSEEK plug). TS rules.ini
    // [HuntSeekSpecial]: RechargeTime=12, IsPowered=true, no voices.
    new (&SuperWeapon[SPC_TS_HUNTSEEK])
        SuperClass(TICKS_PER_MINUTE * 12, true, VOX_NONE, VOX_NONE, VOX_NOT_READY, VOX_INSUFFICIENT_POWER);

    // TF: TS E.M. Pulse (EMP Cannon). TS [EMPulseSpecial] RechargeTime=4.5, IsPowered=true. TS recorded only
    // the ready line, so every other moment stays silent rather than borrow another era's announcer.
    new (&SuperWeapon[SPC_TS_EMP])
        SuperClass(TICKS_PER_MINUTE * 9 / 2, true, VOX_NONE, VOX_TS_EMP_READY, VOX_NONE, VOX_NONE);

    // TF: TS Firestorm Defense (Firestorm Generator). TS rules.ini
    // [FirestormSpecial]: RechargeTime=3, IsPowered, UseChargeDrain, RechargeVoice=00-I162.
    new (&SuperWeapon[SPC_TS_FIRESTORM])
        SuperClass(TICKS_PER_MINUTE * 3, true, VOX_NONE, VOX_TS_FIRESTORM_READY, VOX_NONE, VOX_NONE);

    // TF: Nod Nuclear Strike. TD's 14-minute recharge (NUKE_GONE_TIME); TD has no charging line for the nuke,
    // so only the ready line plays.
    new (&SuperWeapon[SPC_TD_NUKE]) SuperClass(TICKS_PER_MINUTE * 14,
                                               true,
                                               VOX_NONE,
                                               VOX_TD_NUKE_AVAILABLE,
                                               VOX_NOT_READY,
                                               VOX_INSUFFICIENT_POWER);

    // TF: Nod paratroops. Same cadence and voice handling as the RA paratroop drop it splits from.
    new (&SuperWeapon[SPC_TD_PARA_INFANTRY])
        SuperClass(TICKS_PER_MINUTE * Rule.ParaInfantryTime, false, VOX_NONE, VOX_NONE, VOX_NOT_READY, VOX_NOT_READY);

    // TF: Nod recon flight, split from the Soviet spy plane so each era's airstrip carries its own
    // single-badged special.
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

// The house's live building with the given addon plug installed, or NULL. Plugs never stand on the map, so
// Has_Building_Active can't see them: they live in their host's UpgradeTypes.
BuildingClass* TF_House_Plug_Host(HouseClass const* house, StructType plug)
{
    for (int i = 0; i < Buildings.Count(); i++) {
        BuildingClass* b = Buildings.Ptr(i);
        if (b != NULL && b->IsActive && !b->IsInLimbo && b->House == house && b->Strength > 0) {
            for (int u = 0; u < b->UpgradeLevel; u++) {
                if (b->UpgradeTypes[u] == plug) {
                    return (b);
                }
            }
        }
    }
    return (NULL);
}

bool TF_House_Has_Plug(HouseClass const* house, StructType plug)
{
    return (TF_House_Plug_Host(house, plug) != NULL);
}

// True when Prerequisite= names a TS-tree building: the TS yard, the TS power plant or the TS enum block.
// Can_Build's faction-yard gate skips these types (the TS yard gates them) and the sidebar badges them TS GDI.
bool TF_Is_TS_Tree_Type(TechnoTypeClass const* type)
{
    if (type == NULL) {
        return false;
    }
    int const* pre = type->Prerequisite;
    for (int i = 0; i < PREREQUISITE_MAX; i++) {
        int t = pre[i];
        if (t < 0) {
            break;
        }
        if (t == STRUCT_TSFACT || t == STRUCT_TSPOWR
            || (t >= STRUCT_TS_TREE_FIRST && t <= STRUCT_TS_TREE_LAST)) {
            return true;
        }
    }
    return false;
}

// Every unit the dropship bay delivers: the one list the factory binding, order gates, sidebar and countdown
// cameo consult. The delivery cooldown is the bay's, shared by everything it sends.
bool TF_Is_Dropship_Delivered(UnitTypeClass const* type)
{
    return (type != NULL && (type->Type == UNIT_TSHMEC || type->Type == UNIT_TSMDIV));
}

/*
**	Whether the house has a radar building that an E.M. Pulse has not stunned.
*/
bool HouseClass::Has_Working_Radar(void) const
{
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass const* b = Buildings.Ptr(index);
        if (b != NULL && b->House == this && !b->IsInLimbo && !b->Is_Immobilized()
            && (TF_Building_Scan_Bit(b->Class->Type) & STRUCTF_RADAR)) {
            return (true);
        }
    }
    return (false);
}

// The house's nearest built, powered and unstunned EMP Cannon with the cell in reach, or NULL. TS
// [EMPulseWeapon] Range=40 cells, measured on cell deltas as TS does (OpenTS suprtype.cpp).
BuildingClass* TF_EMP_Launch_Site(HouseClass const* house, CELL cell)
{
    enum { EMP_RANGE_CELLS = 40 };
    if (house == NULL || cell <= 0 || house->Power_Fraction() < 1) {
        return (NULL);
    }
    BuildingClass* best = NULL;
    int bestdist = 0;
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass* b = Buildings.Ptr(index);
        if (b == NULL || *b != STRUCT_TSPULS || b->House != house || b->IsInLimbo || b->Strength <= 0
            || b->BState == BSTATE_CONSTRUCTION || b->Is_Immobilized()) {
            continue;
        }
        CELL bc = Coord_Cell(b->Center_Coord());
        int dx = Cell_X(cell) - Cell_X(bc);
        int dy = Cell_Y(cell) - Cell_Y(bc);
        int dist = dx * dx + dy * dy;
        if (dist < EMP_RANGE_CELLS * EMP_RANGE_CELLS && (best == NULL || dist < bestdist)) {
            best = b;
            bestdist = dist;
        }
    }
    return (best);
}

// The E.M. Pulse at a cell (OpenTS empulse.cpp Create): within spread cells low-flying aircraft crash, Limpet
// Mines die, and buildings, vehicles and grounded aircraft are stunned; infantry and the source are spared.
void TF_EMPulse(CELL center, TechnoClass* source, int spread, int duration)
{
    enum
    {
        EMP_AIRCRAFT_HEIGHT = 104 // TS one height level: an aircraft below it is not yet flying
    };
    int const spread_sq = spread * spread;
    int crashed = 0;
    int stunned_buildings = 0;
    int stunned_vehicles = 0;
    int stunned_aircraft = 0;
    int stunned_underground = 0;

    for (int index = Aircraft.Count() - 1; index >= 0; index--) {
        AircraftClass* aircraft = Aircraft.Ptr(index);
        if (aircraft != NULL && aircraft->IsActive && !aircraft->IsInLimbo && aircraft->Strength > 0
            && aircraft->Height > 0 && aircraft->Height < EMP_AIRCRAFT_HEIGHT
            && ::Distance(aircraft->Center_Coord(), Cell_Coord(center)) < spread * CELL_LEPTON_W) {
            int damage = aircraft->Strength;
            aircraft->Take_Damage(damage, 0, WARHEAD_HE, source, true);
            crashed++;
        }
    }

    for (int y = -spread; y <= spread; y++) {
        for (int x = -spread; x <= spread; x++) {
            if (x * x + y * y > spread_sq) {
                continue;
            }
            int cx = Cell_X(center) + x;
            int cy = Cell_Y(center) + y;
            if (cx < 0 || cx >= MAP_CELL_W || cy < 0 || cy >= MAP_CELL_H) {
                continue;
            }
            CELL cell = XY_Cell(cx, cy);
            if (!Map.In_Radar(cell)) {
                continue;
            }
            CellClass& cellptr = Map[cell];

            BuildingClass* building = cellptr.Cell_Building();
            if (building != NULL) {
                if (building->IsActive && !building->IsInLimbo && building->Strength > 0
                    && Coord_Cell(building->Center_Coord()) == cell) {
                    if (*building == STRUCT_TSDLIMP) {
                        int damage = building->Strength;
                        building->Take_Damage(damage, 0, WARHEAD_HE, source, true);
                    } else {
                        if (!building->Is_Immobilized() && building->Class->Is_Construction_Yard()) {
                            COORDINATE coord = Coord_Add(building->Center_Coord(), XY_Coord(CELL_LEPTON_W / 4, CELL_LEPTON_H / 4));
                            AnimClass* sparks = new AnimClass(ANIM_TS_EMPFX, coord, Random_Pick(0, 25));
                            if (sparks != NULL) {
                                sparks->Attach_To(building);
                            }
                        }
                        building->EMP_Stun(duration);
                        stunned_buildings++;
                    }
                }
                continue;
            }

            for (ObjectClass* obj = cellptr.Cell_Occupier(); obj != NULL; obj = obj->Next) {
                RTTIType rtti = obj->What_Am_I();
                if (rtti == RTTI_AIRCRAFT) {
                    AircraftClass* aircraft = (AircraftClass*)obj;
                    if (aircraft != source && aircraft->IsActive && !aircraft->IsInLimbo && aircraft->Strength > 0
                        && aircraft->Height == 0) {
                        if (!aircraft->Is_Immobilized()) {
                            AnimClass* sparks = new AnimClass(ANIM_TS_EMPFX, aircraft->Center_Coord(), Random_Pick(0, 25));
                            if (sparks != NULL) {
                                sparks->Attach_To(aircraft);
                            }
                        }
                        aircraft->EMP_Stun(duration);
                        stunned_aircraft++;
                    }
                    continue;
                }
                if (rtti != RTTI_UNIT && rtti != RTTI_VESSEL) {
                    continue;
                }
                DriveClass* vehicle = (DriveClass*)obj;
                if (vehicle == source || !vehicle->IsActive || vehicle->IsInLimbo || vehicle->Strength <= 0
                    || vehicle->Is_Tunneling()) {
                    continue;
                }
                if (!vehicle->Is_Immobilized()) {
                    AnimClass* sparks = new AnimClass(ANIM_TS_EMPFX, vehicle->Center_Coord(), Random_Pick(0, 25));
                    if (sparks != NULL) {
                        sparks->Attach_To(vehicle);
                    }
                }
                vehicle->EMP_Stun(duration);
                vehicle->NavCom = TARGET_NONE;
                vehicle->Path[0] = FACING_NONE;
                vehicle->Clear_Navigation_List();
                if (rtti == RTTI_UNIT && ((UnitClass*)vehicle)->Is_In_Tunnel_Cycle()) {
                    ((UnitClass*)vehicle)->Tunnel_Stop();
                }
                stunned_vehicles++;
            }
        }
    }

    for (int index = Units.Count() - 1; index >= 0; index--) {
        UnitClass* unit = Units.Ptr(index);
        if (unit == NULL || unit == source || !unit->IsActive || unit->IsInLimbo || unit->Strength <= 0
            || !unit->Is_Tunneling()) {
            continue;
        }
        CELL cell = Coord_Cell(unit->Coord);
        int dx = Cell_X(cell) - Cell_X(center);
        int dy = Cell_Y(cell) - Cell_Y(center);
        if (dx * dx + dy * dy < spread_sq) {
            unit->EMP_Stun(duration);
            unit->Tunnel_Stop();
            stunned_underground++;
        }
    }

#if TF_DEV_BUILD
    const char* up = getenv("USERPROFILE");
    char path[512];
    snprintf(path, sizeof(path), "%s/Documents/CnCRemastered/tf_emp.log", up ? up : ".");
    FILE* lf = fopen(path, "a");
    if (lf != NULL) {
        fprintf(lf,
                "frame=%d PULSE cell=%d,%d stunned buildings=%d vehicles=%d underground=%d aircraft=%d crashed aircraft=%d\n",
                (int)Frame,
                Cell_X(center),
                Cell_Y(center),
                stunned_buildings,
                stunned_vehicles,
                stunned_underground,
                stunned_aircraft,
                crashed);
        fclose(lf);
    }
#endif
}

// Whether an order goes to the dropship bay's own factory slot, so a human's bay and war factory build side
// by side. Computer houses need no slot: each of their factory buildings holds its own production.
bool TF_Bay_Order(RTTIType type, int id)
{
    return ((type == RTTI_UNITTYPE || type == RTTI_UNIT) && id >= 0 && id < UNIT_COUNT
            && TF_Is_Dropship_Delivered(&UnitTypeClass::As_Reference((UnitType)id)));
}

// How many Mammoth Mk. IIs a house may field at once, counted off the Units heap (a Mk. II in a delivery pod
// counts): the CSII quantity fold aliases mod units onto vanilla UQuantity slots.
int const TF_MK2_CAP = 1;

bool TF_Mk2_At_Cap(HouseClass const* house)
{
    int count = 0;
    for (int index = 0; index < Units.Count(); index++) {
        UnitClass const* unit = Units.Ptr(index);
        if (unit != NULL && unit->House == house && unit->Class->Type == UNIT_TSHMEC) {
            count++;
            if (count >= TF_MK2_CAP) {
                return (true);
            }
        }
    }
    return (false);
}

/*
**	The Ghost Stalker is a hero: a house fields one at a time (TS BuildLimit=1). One alive
**	anywhere, riding a transport or still on the barracks floor, holds the cap.
*/
bool TF_Ghost_At_Cap(HouseClass const* house)
{
    for (int index = 0; index < Infantry.Count(); index++) {
        InfantryClass const* inf = Infantry.Ptr(index);
        if (inf != NULL && inf->IsActive && inf->House == house && *inf == INFANTRY_TSGHOST) {
            return (true);
        }
    }
    return (false);
}

/*
**	A house fields one Mobile War Factory at a time (FS BuildLimit=1), deployed or not.
*/
bool TF_Mwar_At_Cap(HouseClass const* house)
{
    for (int index = 0; index < Units.Count(); index++) {
        UnitClass const* unit = Units.Ptr(index);
        if (unit != NULL && unit->IsActive && unit->House == house && *unit == UNIT_TSMWAR) {
            return (true);
        }
    }
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass const* building = Buildings.Ptr(index);
        if (building != NULL && building->IsActive && building->House == house && *building == STRUCT_TSDWEAP) {
            return (true);
        }
    }
    return (false);
}


// True once the house has an Upgrade Center standing: one per house. One still in production does not count.
bool TF_Plug_At_Cap(HouseClass const* house)
{
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass const* building = Buildings.Ptr(index);
        if (building != NULL && building->IsActive && !building->IsInLimbo && building->House == house
            && *building == STRUCT_TSPLUG) {
            return (true);
        }
    }
    return (false);
}

// True for sandbags, the shared wall a TS construction yard builds beside the TS tree's own walls. A standing
// TS yard satisfies Can_Build's ownership test for them, whoever holds it.
bool TF_Is_TS_Yard_Wall(ObjectTypeClass const* type)
{
    if (type == NULL || type->What_Am_I() != RTTI_BUILDINGTYPE) {
        return (false);
    }
    return (((BuildingTypeClass const*)type)->Type == STRUCT_SANDBAG_WALL);
}

// Line fill (the TS and RA2 wall rule): a section placed within this many cells in line of one of the house's
// own sections of its type fills the cells between, if all are clear to build and the house can pay for all.
static const int TF_WALL_FILL_RANGE = 5;

/*
**	The overlay a wall-type building becomes when placed (BuildingClass::Mark), or OVERLAY_NONE
**	for a line-fill type that stays a building.
*/
static OverlayType TF_Wall_Overlay(StructType type)
{
    switch (type) {
    case STRUCT_BRICK_WALL:
        return (OVERLAY_BRICK_WALL);
    case STRUCT_BARBWIRE_WALL:
        return (OVERLAY_BARBWIRE_WALL);
    case STRUCT_SANDBAG_WALL:
        return (OVERLAY_SANDBAG_WALL);
    case STRUCT_WOOD_WALL:
        return (OVERLAY_WOOD_WALL);
    case STRUCT_CYCLONE_WALL:
        return (OVERLAY_CYCLONE_WALL);
    case STRUCT_FENCE:
        return (OVERLAY_FENCE);
    case STRUCT_TSWALL:
        return (OVERLAY_TSWALL);
    case STRUCT_TSNWALL:
        return (OVERLAY_TSNWALL);
    default:
        return (OVERLAY_NONE);
    }
}

bool TF_Is_Line_Fill_Type(BuildingTypeClass const* type)
{
    return (type != NULL
            && ((type->IsWall && TF_Wall_Overlay(type->Type) != OVERLAY_NONE) || type->Type == STRUCT_TSFSDF));
}

static bool TF_Is_Own_Wall_Section(HouseClass const* house, StructType type, CELL cell)
{
    CellClass const& c = Map[cell];
    OverlayType overlay = TF_Wall_Overlay(type);
    if (overlay != OVERLAY_NONE) {
        return (c.Overlay == overlay && c.Owner == house->Class->House);
    }
    BuildingClass const* b = c.Cell_Building();
    return (b != NULL && *b == type && b->House == house);
}

/*
**	Raises or drops the house's Firestorm: every section it owns turns into the live wall or
**	back into a walkable pad, and is redrawn. Dropping it is announced to its owner.
*/
void TF_Firestorm_Set(HouseClass* house, bool on)
{
    if (house == NULL || (bool)house->IsFirestormLive == on) {
        return;
    }
    house->IsFirestormLive = on;
    for (int i = 0; i < Buildings.Count(); i++) {
        BuildingClass* b = Buildings.Ptr(i);
        if (b != NULL && b->IsActive && !b->IsInLimbo && *b == STRUCT_TSFSDF && b->House == house) {
            b->Mark(MARK_CHANGE);
        }
    }
    if (!on && house == PlayerPtr) {
        Speak(VOX_TS_FIRESTORM_OFFLINE);
    }
}

/*
**	The live Firestorm Wall Section in `cell`, or NULL. `shooter` names a house whose own fire
**	passes its own field (TS); pass NULL to find any live section.
*/
BuildingClass* TF_Firestorm_Wall_At(CELL cell, HouseClass const* shooter)
{
    if (!Map.In_Radar(cell)) {
        return (NULL);
    }
    BuildingClass* b = Map[cell].Cell_Building();
    if (b != NULL && *b == STRUCT_TSFSDF && !b->IsInLimbo && b->House->IsFirestormLive && (HouseClass const*)b->House != shooter) {
        return (b);
    }
    return (NULL);
}

/*
**	The first cell on the straight line from `from` to `to` holding a live section that stops
**	`shooter`'s fire, or 0 when the line is clear.
*/
COORDINATE TF_Firestorm_On_Path(COORDINATE from, COORDINATE to, HouseClass const* shooter)
{
    int dist = ::Distance(from, to);
    DirType dir = ::Direction(from, to);
    CELL last = -1;
    for (int d = 0; d <= dist; d += CELL_LEPTON_W / 4) {
        COORDINATE c = Coord_Move(from, dir, d);
        CELL cell = Coord_Cell(c);
        if (cell != last) {
            last = cell;
            if (TF_Firestorm_Wall_At(cell, shooter) != NULL) {
                return (Cell_Coord(cell));
            }
        }
    }
    return (TF_Firestorm_Wall_At(Coord_Cell(to), shooter) != NULL ? Cell_Coord(Coord_Cell(to)) : 0);
}

// The flare and sound of the field killing something: an air burst at the victim's height when it flies,
// a ground burst on the wall otherwise.
void TF_Firestorm_Flare(COORDINATE wall, COORDINATE victim, int height)
{
    Sound_Effect(VOC_TS_FIRSTRM1, wall);
    if (height > 100) {
        new AnimClass(ANIM_TS_FSAIR, Coord_Move(victim, DIR_N, height));
    } else {
        new AnimClass(ANIM_TS_FSGRND, wall);
    }
}

// What a live field does each frame: anything on one of the house's sections dies, its own units too (TS),
// as does any aircraft over one at any height, except the Hunter Seeker.
static void TF_Firestorm_Burn(HouseClass* house)
{
    for (int i = 0; i < Buildings.Count(); i++) {
        BuildingClass* b = Buildings.Ptr(i);
        if (b == NULL || !b->IsActive || b->IsInLimbo || *b != STRUCT_TSFSDF || !(b->House == house)) {
            continue;
        }
        CELL cell = Coord_Cell(b->Coord);

        if ((Frame % 8) == 0 && Random_Pick(0, 15) == 0) {
            int joins = b->Shape_Number() & 15;
            if (joins != 5 && joins != 10) {
                new AnimClass(ANIM_TS_FSIDLE, b->Center_Coord());
                Sound_Effect(VOC_TS_FIRSTRM1, b->Center_Coord());
            }
        }
        /*
        **	A death can take neighbours with it, so the chain is re-read after every kill.
        */
        for (int guard = 0; guard < 16; guard++) {
            ObjectClass* victim = NULL;
            for (ObjectClass* o = Map[cell].Cell_Occupier(); o != NULL; o = o->Next) {
                RTTIType rtti = o->What_Am_I();
                if (o->IsActive && o->Strength > 0
                    && (rtti == RTTI_UNIT || rtti == RTTI_INFANTRY || rtti == RTTI_VESSEL)) {
                    victim = o;
                    break;
                }
            }
            if (victim == NULL) {
                break;
            }
            TF_Firestorm_Flare(b->Center_Coord(), victim->Center_Coord(), victim->Height);
            int damage = victim->Strength;
            victim->Take_Damage(damage, 0, WARHEAD_TSFLAMEHIT, NULL, true);
        }
    }
    for (int i = 0; i < Aircraft.Count(); i++) {
        AircraftClass* a = Aircraft.Ptr(i);
        if (a == NULL || !a->IsActive || a->IsInLimbo || a->Strength <= 0 || *a == AIRCRAFT_TSHUNT) {
            continue;
        }
        BuildingClass* wall = TF_Firestorm_Wall_At(Coord_Cell(a->Coord), NULL);
        if (wall != NULL && wall->House == house) {
            TF_Firestorm_Flare(wall->Center_Coord(), a->Center_Coord(), a->Height);
            int damage = a->Strength * 2; // AircraftClass::Take_Damage halves damage while airborne
            a->Take_Damage(damage, 0, WARHEAD_TSFLAMEHIT, NULL, true);
        }
    }
}

// Applies the line fill to a section of `type` just placed at `cell`, charging each filled section as a build.
void TF_Wall_Line_Fill(HouseClass* house, StructType type, CELL cell)
{
    BuildingTypeClass const& btype = BuildingTypeClass::As_Reference(type);
    int const cost = btype.Cost_Of() * house->CostBias;
    static FacingType const _dirs[] = {FACING_N, FACING_E, FACING_S, FACING_W};

    for (int d = 0; d < (int)ARRAY_SIZE(_dirs); d++) {
        CELL c = cell;
        int reach = 0;
        for (int step = 1; step <= TF_WALL_FILL_RANGE; step++) {
            c = Adjacent_Cell(c, _dirs[d]);
            if (!Map.In_Radar(c)) {
                break;
            }
            if (TF_Is_Own_Wall_Section(house, type, c)) {
                reach = step;
                break;
            }
        }
        if (reach < 2) {
            continue;
        }

        bool clear = true;
        c = cell;
        for (int step = 1; step < reach; step++) {
            c = Adjacent_Cell(c, _dirs[d]);
            if (!Map[c].Is_Clear_To_Build(btype.Speed)) {
                clear = false;
                break;
            }
        }
        if (!clear) {
            continue;
        }
        if (house->Available_Money() < cost * (reach - 1)) {
            if (house == PlayerPtr) {
                Speak(VOX_NO_CASH);
            }
            continue;
        }

        c = cell;
        for (int step = 1; step < reach; step++) {
            c = Adjacent_Cell(c, _dirs[d]);
            BuildingClass* section = new BuildingClass(type, house->Class->House);
            if (section == NULL) {
                return;
            }
            /*
            **	A wall converts itself to its overlay and deletes the building inside Unlimbo,
            **	so the object is never touched after a successful call.
            */
            if (section->Unlimbo(Cell_Coord(c))) {
                house->Spend_Money(cost);
            } else {
                delete section;
                break;
            }
        }
    }
}

// Returns the HOUSEF_ bits of every faction construction yard the house has standing.
// A yard grants its faction's tree to whoever holds it, so Can_Build tests Owner= against this.
int HouseClass::Yard_Factions(void) const
{
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
    // HOUSEF_TSGDI is empty when TF_TS_GDI_FACTION is 0. Never fall back to the Germany bit: Germany
    // is Allied in that build, so a TS yard would unlock the whole Allied tree.
    if (Has_Building_Active(STRUCT_TSFACT)) {
        yards |= HOUSEF_TSGDI;
    }
    return (yards);
}

// True when a capped order would be refused: the dropship bay is reloading, or the house is at its Mk. II,
// Ghost Stalker, Mobile War Factory or Upgrade Center cap. Sidebar clicks ask first so EVA never acknowledges a refused order.
bool TF_Delivery_Order_Refused(HouseClass const* house, RTTIType type, int id)
{
    if (house == NULL) {
        return (false);
    }
    if (type == RTTI_INFANTRYTYPE) {
        InfantryTypeClass const* itype = (InfantryTypeClass const*)Fetch_Techno_Type(type, id);
        return (itype != NULL && itype->Type == INFANTRY_TSGHOST && TF_Ghost_At_Cap(house));
    }
    if (type == RTTI_BUILDINGTYPE) {
        BuildingTypeClass const* btype = (BuildingTypeClass const*)Fetch_Techno_Type(type, id);
        return (btype != NULL && btype->Type == STRUCT_TSPLUG && TF_Plug_At_Cap(house));
    }
    if (type != RTTI_UNITTYPE) {
        return (false);
    }
    UnitTypeClass const* utype = (UnitTypeClass const*)Fetch_Techno_Type(type, id);
    if (utype == NULL) {
        return (false);
    }
    if (TF_Is_Dropship_Delivered(utype) && house->TFDropBayTimer != 0) {
        return (true);
    }
    if (utype->Type == UNIT_TSMWAR) {
        return (TF_Mwar_At_Cap(house));
    }
    return (utype->Type == UNIT_TSHMEC && TF_Mk2_At_Cap(house));
}

bool HouseClass::Can_Build(ObjectTypeClass const* type, HousesType house) const
{
    assert(Houses.ID(this) == ID);
    assert(type != NULL);

    // TF: caps and delivery cooldowns never refuse here. This is the sidebar's offer test, so a refusal
    // hides the cameo rather than greying it; TF_Delivery_Order_Refused refuses the order instead.

    // TF: an addon plug is offered only while its host building stands. Prerequisite tokens can't say
    // this: the era rule lets another era's building satisfy a token, and a plug needs its real host.
    if (type->What_Am_I() == RTTI_BUILDINGTYPE) {
        BuildingTypeClass const* btype = (BuildingTypeClass const*)type;
        if (btype->PowersUpBuilding != STRUCT_NONE && !Has_Building_Active(btype->PowersUpBuilding)) {
            return (false);
        }
    }

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
    bool log_td = (type->IniName[0] == 'T' && (type->IniName[1] == 'D' || type->IniName[1] == 'S'));
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
    // TF: a construction yard grants its faction's tree to whoever holds it, so holding a yard listed in
    // Owner= also passes. A standing TS yard passes for sandbags even when TF_TS_GDI_FACTION is 0.
    bool yard_grants = ((own & Yard_Factions()) != 0);
    if (TF_Is_TS_Yard_Wall(type) && Has_Building_Active(STRUCT_TSFACT)) {
        yard_grants = true;
    }
    if (((1L << house) & own) == 0 && !yard_grants) {
        return (false);
    }

    // TF: skirmish builds the faction MCVs and the campaigns build the vanilla pair, never both.
    if (type->What_Am_I() == RTTI_UNITTYPE && ((UnitTypeClass const*)type)->Is_MCV()) {
        UnitType ut = ((UnitTypeClass const*)type)->Type;
        bool vanilla = (ut == UNIT_MCV || ut == UNIT_TDMCV);
        if (vanilla == (Session.Type != GAME_NORMAL)) {
            return (false);
        }
    }

    // TF: the same split for war factories and helipads: faction ones in skirmish, vanilla in campaigns.
    if (type->What_Am_I() == RTTI_BUILDINGTYPE) {
        StructType st = (StructType)((BuildingTypeClass const*)type)->Type;
        bool vanilla_b = (st == STRUCT_WEAP || st == STRUCT_HELIPAD || st == STRUCT_TDHPAD);
        bool faction_b = (st == STRUCT_AWEAP || st == STRUCT_SWEAP || st == STRUCT_AHPAD || st == STRUCT_SHPAD
                          || st == STRUCT_TDGHPAD || st == STRUCT_TDNHPAD);
        if ((vanilla_b && Session.Type != GAME_NORMAL) || (faction_b && Session.Type == GAME_NORMAL)) {
            return (false);
        }
    }

    // TF: in skirmish a building needs a standing yard of a faction in its Owner=. The TS yard gates TS-tree
    // buildings instead, and sandbags pass while one stands. rules.ini can't say this: prereqs are AND-only.
    if (type->What_Am_I() == RTTI_BUILDINGTYPE && Session.Type != GAME_NORMAL) {
        BuildingTypeClass const* btype = (BuildingTypeClass const*)type;
        if (!btype->Is_Construction_Yard()) {
            // One dropship bay per house, counting standing bays only. Get_Quantity also counts a bay in
            // production, and the sidebar would then evict the cameo from its own factory, stranding the bay.
            if (btype->Type == STRUCT_TSDROP && Has_Building_Active(STRUCT_TSDROP)) {
                return (false);
            }

            bool ts_tree = TF_Is_TS_Tree_Type((TechnoTypeClass const*)type);

            bool ts_walls = TF_Is_TS_Yard_Wall(type) && Has_Building_Active(STRUCT_TSFACT);

            int const factions = HOUSEF_GDI | HOUSEF_NOD | HOUSEF_ALLIES | HOUSEF_SOVIET | HOUSEF_TSGDI;
            int ownable = type->Get_Ownable();
            if (!ts_tree && !ts_walls && (ownable & factions) != 0) {
                int yards = Yard_Factions();
                if ((ownable & yards) == 0) {
                    return (false);
                }
            }
        }
    }

    // TF: every TS building needs the house's TS yard standing, in every game type. Otherwise shared
    // prerequisites (a TD refinery for TSPROC) let other yards build and extend a TS base.
    if (type->What_Am_I() == RTTI_BUILDINGTYPE && !((BuildingTypeClass const*)type)->Is_Construction_Yard()) {
        StructType const st = ((BuildingTypeClass const*)type)->Type;
        bool const ts_building = (st == STRUCT_TSPOWR || (st >= STRUCT_TS_TREE_FIRST && st <= STRUCT_TS_TREE_LAST));
        if (ts_building && !Has_Building_Active(STRUCT_TSFACT)) {
            return (false);
        }
    }

    // TF: prerequisites are checked per type with Has_Building_Active, because mod building types run
    // past the 32 bits of ActiveBScan.
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
        */
        if (t == STRUCT_POWER && Has_Building_Active(STRUCT_ADVANCED_POWER))
            continue;
        // TF: tech centres are faction identity: neither stands in for the other, unlike vanilla multiplayer.
        // The Missile Silo is the exception, since it names only the Soviet one but both RA sides own it.
        if (t == STRUCT_SOVIET_TECH && type->What_Am_I() == RTTI_BUILDINGTYPE
            && ((BuildingTypeClass const*)type)->Type == STRUCT_MSLO && (Yard_Factions() & HOUSEF_ALLIES) != 0
            && Has_Building_Active(STRUCT_ADVANCED_TECH))
            continue;
        // TF: a deployed Mobile War Factory counts as a war factory, as in TS Firestorm.
        if (t == STRUCT_TSWEAP && Has_Building_Active(STRUCT_TSDWEAP))
            continue;
        // TF: any faction yard satisfies the vanilla 'fact' token. Houses own faction yards, never
        // STRUCT_CONST, so without this the whole tree stops at the power plant.
        if (t == STRUCT_CONST
            && (Has_Building_Active(STRUCT_AFACT) || Has_Building_Active(STRUCT_SFACT)
                || Has_Building_Active(STRUCT_TDFACT) || Has_Building_Active(STRUCT_TDGFACT)
                || Has_Building_Active(STRUCT_TDNFACT)))
            continue;
        // TF: other eras' and factions' buildings satisfy vanilla tokens: production tokens within one faction,
        // power and refinery across eras. Radar never substitutes; tech centres only for TD types on 'atek'.
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
            if (t == STRUCT_TENT && (own & HOUSEF_GDI) && tdpyle_type >= 0 && Has_Building_Active(tdpyle_type))
                continue;
            if (t == STRUCT_BARRACKS && (own & HOUSEF_NOD) && tdhand_type >= 0 && Has_Building_Active(tdhand_type))
                continue;
            if (tdpyle_type >= 0 && tdhand_type >= 0 && (own & HOUSEF_GDI) && (own & HOUSEF_NOD)) {
                if (t == tdpyle_type && Has_Building_Active(tdhand_type))
                    continue;
                if (t == tdhand_type && Has_Building_Active(tdpyle_type))
                    continue;
            }
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
            if (t == STRUCT_HELIPAD) {
                if ((own & (HOUSEF_GDI | HOUSEF_NOD)) && tdhpad_type >= 0 && Has_Building_Active(tdhpad_type))
                    continue;
                if ((own & HOUSEF_ALLIES) && Has_Building_Active(STRUCT_AHPAD))
                    continue;
                if ((own & HOUSEF_SOVIET) && Has_Building_Active(STRUCT_SHPAD))
                    continue;
                if ((own & HOUSEF_GDI) && Has_Building_Active(STRUCT_TDGHPAD))
                    continue;
                if ((own & HOUSEF_NOD) && Has_Building_Active(STRUCT_TDNHPAD))
                    continue;
            }
            if (t == STRUCT_REFINERY) {
                if (tdproc_type >= 0 && Has_Building_Active(tdproc_type))
                    continue;
                if (Has_Building_Active(STRUCT_TSPROC))
                    continue;
            }
            if (t == STRUCT_ADVANCED_TECH && type->IniName[0] == 'T' && type->IniName[1] == 'D') {
                if (tdeye_type >= 0 && Has_Building_Active(tdeye_type))
                    continue;
                if (tdtmpl_type >= 0 && Has_Building_Active(tdtmpl_type))
                    continue;
            }
            if (t == STRUCT_REPAIR) {
                if (tdfix_type >= 0 && Has_Building_Active(tdfix_type))
                    continue;
                if (Has_Building_Active(STRUCT_TSDEPT))
                    continue;
            }
            if (t == STRUCT_POWER) {
                if (tdnuke_type >= 0 && Has_Building_Active(tdnuke_type))
                    continue;
                if (tdnuk2_type >= 0 && Has_Building_Active(tdnuk2_type))
                    continue;
                if (Has_Building_Active(STRUCT_TSPOWR))
                    continue;
            }
            if (t == STRUCT_SHIP_YARD && (own & HOUSEF_GDI) && tdgyard_type >= 0 && Has_Building_Active(tdgyard_type))
                continue;
            if (t == STRUCT_SUB_PEN && (own & HOUSEF_NOD) && tdnpen_type >= 0 && Has_Building_Active(tdnpen_type))
                continue;
            if (t == STRUCT_AIRSTRIP && (own & HOUSEF_GDI) && tdgafld_type >= 0 && Has_Building_Active(tdgafld_type))
                continue;
            if (t == tdnuke_type
                && (Has_Building_Active(STRUCT_POWER) || Has_Building_Active(STRUCT_ADVANCED_POWER)
                    || (tdnuk2_type >= 0 && Has_Building_Active(tdnuk2_type))
                    || Has_Building_Active(STRUCT_TSPOWR)))
                continue;
            if (t == tdproc_type && (Has_Building_Active(STRUCT_REFINERY) || Has_Building_Active(STRUCT_TSPROC)))
                continue;
            if (t == STRUCT_TSPOWR
                && (Has_Building_Active(STRUCT_POWER) || Has_Building_Active(STRUCT_ADVANCED_POWER)
                    || (tdnuke_type >= 0 && Has_Building_Active(tdnuke_type))
                    || (tdnuk2_type >= 0 && Has_Building_Active(tdnuk2_type))))
                continue;
            if (t == STRUCT_TSPROC
                && (Has_Building_Active(STRUCT_REFINERY) || (tdproc_type >= 0 && Has_Building_Active(tdproc_type))))
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

    extern void TF_Skirmish_Naval_Reset(void);
    TF_Skirmish_Naval_Reset();
    extern void TF_Wave_Reset(void);
    TF_Wave_Reset();
    extern void TF_AI_Clocks_Reset(void);
    TF_AI_Clocks_Reset();
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
    */
    // TF: skirmish base-builds from rules.ini's lowered IQProduction so Easy AIs build; campaigns keep vanilla's
    // MaxIQ threshold so the scripted enemies EA meant to sit still wait for their trigger.
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
            && UnitFactories + DropFactories + BuildingFactories + InfantryFactories > 0) {
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
                    if (*building == STRUCT_RADAR || *building == STRUCT_TDHQ || *building == STRUCT_TDEYE
                        || *building == STRUCT_TSRADR) {
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
                if ((Power_Fraction() < 1 || !Has_Working_Radar()) && !IsGPSActive) {
                    Map.Radar_Activate(0);
                }
            } else {
                if (!IsGPSActive) {
                    Map.Radar_Activate(0);
                }
            }

        } else {
            if (IsGPSActive || (ActiveBScan & STRUCTF_RADAR)) {
                if ((Power_Fraction() >= 1 && Has_Working_Radar()) || IsGPSActive) {
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
        // TF: the radar on/off sting for the human house, from a heap count of working radar buildings and the
        // power, debounced; never from the scan bits (docs/launcher-vs-dll-ownership.md).
        if (IsHuman) {
            int radar_count = 0;
            for (int ri = 0; ri < Buildings.Count(); ri++) {
                BuildingClass* rb = Buildings.Ptr(ri);
                if (rb != NULL && !rb->IsInLimbo && rb->House == PlayerPtr && !rb->Is_Immobilized()
                    && (*rb == STRUCT_RADAR || *rb == STRUCT_TDHQ || *rb == STRUCT_TDEYE || *rb == STRUCT_TSRADR)) {
                    radar_count++;
                }
            }
            bool functional = (radar_count > 0 || IsGPSActive) && (IsGPSActive || Power_Fraction() >= 1);

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

#if TF_DEV_BUILD
            // TF: dev cheat: a human house's superweapons recharge in 5 seconds and still announce ready.
            // tf_dev_off.flag turns it off with the other dev cheats.
            if (TF_Dev_Cheats() && IsHuman && !super->Is_Ready()) {
                super->Cap_Recharge(TICKS_PER_SECOND * 5);
            }
#endif

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
            if (!super->Is_Ready() && super->Is_Powered() && !super->Is_One_Time() && !super->Is_Draining()) {
                super->Suspend(Power_Fraction() < 1);
            }
        }
    }

    // TF: GDI's Advanced Comm Centre (TDEYE) grants the GPS as the Allied tech centre does, tested by type since
    // it lies past the 32-bit BScan mask. The Temple of Nod grants none.
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

            // TF: the satellite's reveal is shared with allies (ShareAllyVisibility), so it is taken from them too,
            // except from those whose own GPS is still up.
            if (ShareAllyVisibility) {
                for (int i = 0; i < Session.Players.Count(); i++) {
                    HouseClass* ally = HouseClass::As_Pointer(Session.Players[i]->Player.ID);
                    if (ally != NULL && ally != this && ally->IsActive && ally->IsHuman && Is_Ally(ally)
                        && !ally->IsGPSActive) {
                        Map.Shroud_The_Map(ally);
                    }
                }
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
                    // TF: the Advanced Comm Centre launches the satellite too; without HasFired the GPS is re-granted.
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

            // TF: the Advanced Comm Centre grants the GPS as well (see has_gps_techcenter).
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

    // TF: GDI Ion Cannon, granted while the house holds an Advanced Comm Centre (TDEYE), on the nuke's pattern.
    // TDEYE lies past the 32-bit BScan mask, so it is tested by type.
    bool ion_host = Has_Building_Active(STRUCT_TDEYE);
    if (SuperWeapon[SPC_TD_ION_CANNON].Is_Present()) {
        if ((!ion_host && !SuperWeapon[SPC_TD_ION_CANNON].Is_One_Time()) || IsDefeated) {
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
        if (ion_host && (IsHuman || IQ >= Rule.IQSuperWeapons)) {
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

    // TF: TS Ion Cannon, granted by the uplink plug (TSPION in a TSPLUG), on its own timer beside the TD one.
    bool ts_ion_host = TF_House_Has_Plug(this, STRUCT_TSPION);
    if (SuperWeapon[SPC_TS_ION_CANNON].Is_Present()) {
        if ((!ts_ion_host && !SuperWeapon[SPC_TS_ION_CANNON].Is_One_Time()) || IsDefeated) {
            if (SuperWeapon[SPC_TS_ION_CANNON].Remove()) {
                if (this == PlayerPtr) {
                    if (Map.IsTargettingMode == SPC_TS_ION_CANNON) {
                        Map.IsTargettingMode = SPC_NONE;
                    }
                    Map.Column[1].Flag_To_Redraw();
                }
                IsRecalcNeeded = true;
            }
        } else {
            if (SuperWeapon[SPC_TS_ION_CANNON].Is_Ready() && !IsHuman) {
                Special_Weapon_AI(SPC_TS_ION_CANNON);
            }
        }
    } else {
        if (ts_ion_host && (IsHuman || IQ >= Rule.IQSuperWeapons)) {
            SuperWeapon[SPC_TS_ION_CANNON].Enable(false, this == PlayerPtr, Power_Fraction() < 1);
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_TS_ION_CANNON, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_TS_ION_CANNON);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    // TF: TS E.M. Pulse, granted while an EMP Cannon of the house stands (one in production doesn't count); range and
    // power are checked when it fires.
    bool ts_emp_host = Has_Building_Active(STRUCT_TSPULS);
    if (SuperWeapon[SPC_TS_EMP].Is_Present()) {
        if ((!ts_emp_host && !SuperWeapon[SPC_TS_EMP].Is_One_Time()) || IsDefeated) {
            if (SuperWeapon[SPC_TS_EMP].Remove()) {
                if (this == PlayerPtr) {
                    if (Map.IsTargettingMode == SPC_TS_EMP) {
                        Map.IsTargettingMode = SPC_NONE;
                    }
                    Map.Column[1].Flag_To_Redraw();
                }
                IsRecalcNeeded = true;
            }
        } else {
            if (SuperWeapon[SPC_TS_EMP].Is_Ready() && !IsHuman) {
                Special_Weapon_AI(SPC_TS_EMP);
            }
        }
    } else {
        if (ts_emp_host && (IsHuman || IQ >= Rule.IQSuperWeapons)) {
            SuperWeapon[SPC_TS_EMP].Enable(false, this == PlayerPtr, Power_Fraction() < 1);
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_TS_EMP, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_TS_EMP);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    // TF: TS Firestorm Defense, granted while a Firestorm Generator of the house stands. The field drops when its
    // drain runs out, power falls short or the last generator goes; low power restarts a charge from zero (TS).
    bool ts_fs_host = Has_Building_Active(STRUCT_TSFGEN);
    SuperClass& firestorm = SuperWeapon[SPC_TS_FIRESTORM];
    if (IsFirestormLive && (!ts_fs_host || Power_Fraction() < 1 || firestorm.Drain_Expired() || IsDefeated)) {
        TF_Firestorm_Set(this, false);
        firestorm.End_Drain(this == PlayerPtr);
        if (this == PlayerPtr) {
            Map.Column[1].Flag_To_Redraw();
        }
    }
    if (IsFirestormLive) {
        TF_Firestorm_Burn(this);
    }
    if (firestorm.Is_Present() && !firestorm.Is_Draining() && !firestorm.Is_Ready()) {
        if (Power_Fraction() < 1) {
            IsFirestormPowerLow = true;
        } else if (IsFirestormPowerLow) {
            IsFirestormPowerLow = false;
            firestorm.Restart_Charge();
        }
    }
    if (firestorm.Is_Present()) {
        if ((!ts_fs_host && !firestorm.Is_One_Time()) || IsDefeated) {
            if (firestorm.Remove()) {
                if (this == PlayerPtr) {
                    if (Map.IsTargettingMode == SPC_TS_FIRESTORM) {
                        Map.IsTargettingMode = SPC_NONE;
                    }
                    Map.Column[1].Flag_To_Redraw();
                }
                IsRecalcNeeded = true;
            }
        }
    } else {
        if (ts_fs_host && (IsHuman || IQ >= Rule.IQSuperWeapons)) {
            firestorm.Enable(false, this == PlayerPtr, Power_Fraction() < 1);
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_TS_FIRESTORM, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_TS_FIRESTORM);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    // TF: TS Drop Pods, granted by the Drop Pod Node plug (TSPODS in a TSPLUG).
    bool ts_pods_host = TF_House_Has_Plug(this, STRUCT_TSPODS);
    if (SuperWeapon[SPC_TS_DROPPODS].Is_Present()) {
        if ((!ts_pods_host && !SuperWeapon[SPC_TS_DROPPODS].Is_One_Time()) || IsDefeated) {
            if (SuperWeapon[SPC_TS_DROPPODS].Remove()) {
                if (this == PlayerPtr) {
                    if (Map.IsTargettingMode == SPC_TS_DROPPODS) {
                        Map.IsTargettingMode = SPC_NONE;
                    }
                    Map.Column[1].Flag_To_Redraw();
                }
                IsRecalcNeeded = true;
            }
        } else {
            if (SuperWeapon[SPC_TS_DROPPODS].Is_Ready() && !IsHuman) {
                Special_Weapon_AI(SPC_TS_DROPPODS);
            }
        }
    } else {
        if (ts_pods_host && (IsHuman || IQ >= Rule.IQSuperWeapons)) {
            SuperWeapon[SPC_TS_DROPPODS].Enable(false, this == PlayerPtr, false);
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_TS_DROPPODS, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_TS_DROPPODS);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    // TF: TS Hunter Seeker, granted by the Seeker Control plug (TSSEEK in a TSPLUG). The droid picks its own
    // victim: a computer house launches it once charged, a human with one click on the cameo.
    bool ts_seek_host = TF_House_Has_Plug(this, STRUCT_TSSEEK);
    if (SuperWeapon[SPC_TS_HUNTSEEK].Is_Present()) {
        if ((!ts_seek_host && !SuperWeapon[SPC_TS_HUNTSEEK].Is_One_Time()) || IsDefeated) {
            if (SuperWeapon[SPC_TS_HUNTSEEK].Remove()) {
                if (this == PlayerPtr) {
                    if (Map.IsTargettingMode == SPC_TS_HUNTSEEK) {
                        Map.IsTargettingMode = SPC_NONE;
                    }
                    Map.Column[1].Flag_To_Redraw();
                }
                IsRecalcNeeded = true;
            }
        } else {
            if (!IsHuman && SuperWeapon[SPC_TS_HUNTSEEK].Is_Ready()) {
                Place_Special_Blast(SPC_TS_HUNTSEEK, 0);
            }
        }
    } else {
        if (ts_seek_host && (IsHuman || IQ >= Rule.IQSuperWeapons)) {
            SuperWeapon[SPC_TS_HUNTSEEK].Enable(false, this == PlayerPtr, false);
            if (Session.Type == GAME_GLYPHX_MULTIPLAYER) {
                if (IsHuman) {
#ifdef REMASTER_BUILD
                    Sidebar_Glyphx_Add(RTTI_SPECIAL, SPC_TS_HUNTSEEK, this);
#endif
                }
            } else {
                if (this == PlayerPtr) {
                    Map.Add(RTTI_SPECIAL, SPC_TS_HUNTSEEK);
                    Map.Column[1].Flag_To_Redraw();
                }
            }
        }
    }

    // TF: Nod Nuclear Strike, granted while the house holds a Temple of Nod (TDTMPL), tested by type since it
    // lies past the 32-bit BScan mask.
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

    // TF: the spy plane is per era: the Soviet airfield grants it and the Nod airstrip its own recon flight. Both
    // test the real building, since the TD airfields shadow STRUCTF_AIRSTRIP in the scan.
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

    // TF: parabombs are the Soviet airfield's power in every session type, not just campaigns. It tests the real
    // building, since the TD airfields shadow STRUCTF_AIRSTRIP in the scan.
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

    // TF: paratroops are per era: the Soviet airfield grants the RA drop, the Nod airstrip and Hand of Nod the TD
    // drop. Both test the real buildings, since the TD airfields shadow STRUCTF_AIRSTRIP in the scan.
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
    bool bay = TF_Bay_Order(type, id);

    fptr = Fetch_Factory(type, bay);

    // TF: capped orders and dropship bay reloads are refused here, where every player production order
    // arrives, because Can_Build keeps offering their cameos rather than hiding them.
    if (TF_Delivery_Order_Refused(this, type, id)) {
        return (PROD_CANT);
    }

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
        Set_Factory(type, fptr, bay);
        result = fptr->Set(*tech, *this);
        initial_start = true;

        /*
        ** If set failed, we probably reached the production cap. Don't let the factory linger, preventing further
        *production attempts.
        ** ST - 3/17/2020 2:03PM
        */
        if (!result) {
            Set_Factory(type, NULL, bay);
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
ProdFailType HouseClass::Suspend_Production(RTTIType type, bool bay)
{
    assert(Houses.ID(this) == ID);

    FactoryClass* fptr = Fetch_Factory(type, bay);

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
ProdFailType HouseClass::Abandon_Production(RTTIType type, bool bay)
{
    assert(Houses.ID(this) == ID);

    FactoryClass* fptr = Fetch_Factory(type, bay);

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
    Set_Factory(type, NULL, bay);
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

            // TF: in skirmish a computer house aims only at buildings it has discovered; no house aims at a
            // cloaked building, and the E.M. Pulse only at what one of its EMP Cannons can reach.
            if (!IsHuman && Session.Type != GAME_NORMAL && !b->Is_Discovered_By_Player(this)) {
                continue;
            }

            if (b->Is_Cloaked(this)) {
                continue;
            }

            if (id == SPC_TS_EMP && TF_EMP_Launch_Site(this, Coord_Cell(b->Center_Coord())) == NULL) {
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
        // TF: with no discovered target, recon specials probe the start position the house's blind scouts
        // would take next, so plane and scouts share one rotation. Destructive specials never fire blind.
        CELL cell = TF_Scout_Destination(Coord_Cell(Center));
        if (cell > 0) {
            Place_Special_Blast(id, cell);
        }
    }
}

// True once this house has discovered a standing enemy building. Blind-scout dispatch runs until then,
// and an Easy house's hunters stop probing start positions.
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

// Picks the start-position waypoint a blind scout probes next: unmapped first, then least recently probed,
// then nearest, skipping any within 12 cells of home. Returns -1 when none qualifies.
CELL HouseClass::TF_Scout_Destination(CELL from)
{
    const int TF_HOME_RADIUS_LEPTONS = CELL_LEPTON_W * 12;

    // Probe stamps live here, not in HouseClass, so the savegame layout is untouched. A stamp later than
    // Frame is left from an earlier match and counts as never probed.
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

    // TF: TD's Ion Cannon strikes the cell from orbit at once, with no launch site; the anim's Middle()
    // in anim.cpp deals the damage.
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

    // TF: the nearest powered EMP Cannon in range lobs the pulse (BuildingClass::Mission_Missile). With
    // none the order is refused and the special stays ready; EVA speaks only when power is low.
    case SPC_TS_EMP:
        if (SuperWeapon[SPC_TS_EMP].Is_Ready()) {
            BuildingClass* cannon = TF_EMP_Launch_Site(this, cell);
#if TF_DEV_BUILD
            /*
            **	Why an E.M. Pulse order fired or was refused: power, and the nearest cannon's reach.
            */
            {
                int nearest = -1;
                for (int bi = 0; bi < Buildings.Count(); bi++) {
                    BuildingClass* b = Buildings.Ptr(bi);
                    if (b != NULL && *b == STRUCT_TSPULS && b->House == this && !b->IsInLimbo) {
                        int d = ::Distance(Cell_Coord(cell), b->Center_Coord()) / CELL_LEPTON_W;
                        if (nearest < 0 || d < nearest) {
                            nearest = d;
                        }
                    }
                }
                const char* up = getenv("USERPROFILE");
                char path[512];
                snprintf(path, sizeof(path), "%s/Documents/CnCRemastered/tf_emp.log", up ? up : ".");
                FILE* lf = fopen(path, "a");
                if (lf != NULL) {
                    fprintf(lf, "frame=%d EMP order cell=(%d,%d) power=%d/%d nearest_cannon=%d cells -> %s\n", (int)Frame,
                            Cell_X(cell), Cell_Y(cell), Power, Drain, nearest, cannon != NULL ? "FIRE" : "REFUSED");
                    fclose(lf);
                }
            }
#endif
            if (cannon != NULL) {
                TFEMPDest = cell;
                cannon->Assign_Mission(MISSION_MISSILE);
                cannon->Commence();
                SuperWeapon[SPC_TS_EMP].Discharged(this == PlayerPtr);
                IsRecalcNeeded = true;
                fired = true;
                what = "TS_EMP";
            } else if (this == PlayerPtr && Power_Fraction() < 1) {
                Speak(VOX_INSUFFICIENT_POWER);
            }
            if (this == PlayerPtr) {
                Map.Column[1].Flag_To_Redraw();
                Map.IsTargettingMode = SPC_NONE;
            }
        }
        break;

    // TF: one order raises the Firestorm field and the next drops it; the cell is unused. The field lasts
    // a third of the charge held, and dropping it early refunds three times what is left.
    case SPC_TS_FIRESTORM:
        if (SuperWeapon[SPC_TS_FIRESTORM].Is_Draining()) {
            SuperWeapon[SPC_TS_FIRESTORM].Stop_Drain(3);
            TF_Firestorm_Set(this, false);
            IsRecalcNeeded = true;
        } else if (Power_Fraction() >= 1
                   && SuperWeapon[SPC_TS_FIRESTORM].Start_Drain(SuperWeapon[SPC_TS_FIRESTORM].Charge() / 3)) {
            TF_Firestorm_Set(this, true);
            IsRecalcNeeded = true;
            fired = true;
            what = "TS_FIRESTORM";
        } else if (this == PlayerPtr && Power_Fraction() < 1) {
            Speak(VOX_INSUFFICIENT_POWER);
        }
        if (this == PlayerPtr) {
            Map.Column[1].Flag_To_Redraw();
            Map.IsTargettingMode = SPC_NONE;
        }
        break;

    // TF: the uplink's TS Ion Cannon. The beam's Middle() in anim.cpp deals the TD strike's damage at the
    // cell and half to the eight around it; the RING1 flash is visual only.
    case SPC_TS_ION_CANNON:
        if (SuperWeapon[SPC_TS_ION_CANNON].Is_Ready()) {
            AnimClass* ts_ion_anim = new AnimClass(ANIM_TS_ION_BEAM, Cell_Coord(cell), 0, 1);
            if (ts_ion_anim != NULL) {
                ts_ion_anim->Set_Owner(Class->House);
            }
            AnimClass* ts_ring_anim = new AnimClass(ANIM_TS_ION_RING, Cell_Coord(cell), 0, 1);
            if (ts_ring_anim != NULL) {
                ts_ring_anim->Set_Owner(Class->House);
            }
            SuperWeapon[SPC_TS_ION_CANNON].Discharged(this == PlayerPtr);
            IsRecalcNeeded = true;
            fired = true;
            what = "TS_ION_CANNON";
            if (this == PlayerPtr) {
                Map.Column[1].Flag_To_Redraw();
                Map.IsTargettingMode = SPC_NONE;
            }
        }
        break;

    // TF: five pods (three Light Infantry, two Disc Throwers) streak in from the east or west, the only
    // approaches that read as a 45-degree fall, each starting higher so they land in turn.
    case SPC_TS_DROPPODS:
        if (SuperWeapon[SPC_TS_DROPPODS].Is_Ready()) {
            int launched = 0;
            for (int pd = 0; pd < 5; pd++) {
                CELL podcell = cell;
                if (pd > 0) {
                    CELL scatter = Coord_Cell(Coord_Scatter(Cell_Coord(cell), CELL_LEPTON_W * 2, false));
                    if (Map.In_Radar(scatter)) {
                        podcell = scatter;
                    }
                }
                COORDINATE lz = Cell_Coord(podcell);
                DirType approach = Random_Pick(0, 1) ? DIR_E : DIR_W;
                int drop_h = BulletClass::TF_POD_DROP_HEIGHT + pd * 160;
                COORDINATE spawn = Coord_Move(lz, (DirType)((unsigned char)(approach + DIR_S)), drop_h);

                BulletClass* pod = new BulletClass(BULLET_TSPODDROP, ::As_Target(podcell), NULL, 0, WARHEAD_NONE, MPH_MEDIUM_FAST);
                if (pod != NULL) {
                    pod->TFPodHouse = Class->House;
                    pod->TFPodApproach = approach;
                    pod->TFPodType = (pd < 3) ? INFANTRY_TSE1 : INFANTRY_TSE2;
                    if (pod->Unlimbo(spawn, DIR_S)) {
                        Map.Remove(pod, pod->In_Which_Layer());
                        pod->Height = drop_h;
                        Map.Submit(pod, pod->In_Which_Layer());
                        new AnimClass(ANIM_TS_PODRING, Coord_Move(spawn, DIR_N, drop_h));
                        Sound_Effect(VOC_TS_METEOR, lz);
                        launched++;
                    } else {
                        delete pod;
                    }
                }
            }
            if (launched == 0) {
                break;
            }
            SuperWeapon[SPC_TS_DROPPODS].Discharged(this == PlayerPtr);
            IsRecalcNeeded = true;
            fired = true;
            what = "TS_DROPPODS";
            if (this == PlayerPtr) {
                Map.Column[1].Flag_To_Redraw();
                Map.IsTargettingMode = SPC_NONE;
            }
        }
        break;

    // TF: the Hunter Seeker (OpenTS SUPER_HUNTER_SEEKER) appears at flight level beside the Upgrade Centre
    // carrying the Seeker Control plug and hunts on its own. TS fires it untargeted, so the click only releases it.
    case SPC_TS_HUNTSEEK:
        if (SuperWeapon[SPC_TS_HUNTSEEK].Is_Ready()) {
            bool launched = false;
            BuildingClass* host = TF_House_Plug_Host(this, STRUCT_TSSEEK);
            if (host != NULL) {
                CELL spawn = Map.Nearby_Location(Coord_Cell(host->Center_Coord()), SPEED_FOOT);
                if (spawn > 0 && Map.In_Radar(spawn)) {
                    AircraftClass* droid = new AircraftClass(AIRCRAFT_TSHUNT, Class->House);
                    if (droid != NULL) {
                        droid->Assign_Target(TF_Hunter_Seeker_Acquire(this));
                        if (droid->Unlimbo(Cell_Coord(spawn), DIR_E)) {
                            droid->Assign_Mission(MISSION_ATTACK);
                            droid->Commence();
                            launched = true;
                        } else {
                            delete droid;
                        }
                    }
                }
            }
            if (!launched) {
                break;
            }
            SuperWeapon[SPC_TS_HUNTSEEK].Discharged(this == PlayerPtr);
            IsRecalcNeeded = true;
            fired = true;
            what = "TS_HUNTSEEK";
            if (this == PlayerPtr) {
                Map.Column[1].Flag_To_Redraw();
                Map.IsTargettingMode = SPC_NONE;
            }
        }
        break;

    // TF: the Temple of Nod launches at House->NukeDest like the Missile Silo; TD's single-cycle launch
    // runs in BuildingClass::Mission_Missile.
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
                // TF: the special fired, not the house, picks the drop: TD's sends Minigunners in the C-17, RA's
                // Rifle Infantry in the Badger. Set on every fire, as the @PINF team is cached and shared.
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

    // TF: both eras' recon specials fly the same U2 flyover (TD has no recon plane to port); the split
    // gives each airstrip's special its own timer and badge.
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

    // TF: a unit finished at the dropship bay arrives with the TF_PLACE_BAY cell, naming the bay's own
    // factory slot; it then exits like any finished unit.
    bool bay = (cell == TF_PLACE_BAY);
    if (bay) {
        cell = -1;
    }

    TechnoClass* tech = 0;
    FactoryClass* factory = Fetch_Factory(type, bay);

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
                */
                TechnoClass* builder = pending->Who_Can_Build_Me(false, false);
                if (builder == NULL && pending->What_Am_I() == RTTI_AIRCRAFT
                    && !((AircraftClass*)pending)->Class->IsFixedWing) {
                    builder = pending->Who_Can_Build_Me(true, false);
                }
                // TF: while the house has a TD airstrip, vehicles retry in theory as helicopters do: the airstrip stays
                // in radio contact with its cargo plane in flight, and queued deliveries must not wait for it.
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
                // TF: while the house has a TD airstrip, vehicles retry in theory as helicopters do: the airstrip stays
                // in radio contact with its cargo plane in flight, and queued deliveries must not wait for it.
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
                // TF: only 2 means the object left. 1 is a temporary blockage that leaves it in the factory, so it
                // retries as a failed exit does; counting it as done lost the unit.
                int tf_exit = (builder != NULL) ? builder->Exit_Object(pending) : 0;
#if TF_DEV_BUILD
                if (builder != NULL && builder->What_Am_I() == RTTI_BUILDING
                    && ((BuildingClass*)builder)->Is_TS_War_Factory()) {
                    TF_WF_Log((BuildingClass*)builder, "player product %s#%d: Exit_Object=%d -> %s",
                              pending->Class_Of().IniName, pending->ID, tf_exit,
                              (tf_exit == 2) ? "production marked done" : "kept, retry");
                }
#endif
                if (tf_exit == 2) {

                    /*
                    **	Since the object has left the factory under its own power, delete
                    **	the production manager tied to this slot in the sidebar. Its job
                    **	has been completed.
                    */
                    factory->Set_Is_Blocked(false);
                    factory->Completed();
                    Abandon_Production(type, bay);
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
                    // TF: each era's buildings land with their own sound, and walls fill their line.
                    // Read all three before Unlimbo: a wall deletes itself in there, so tech is freed afterwards.
                    bool td_bldg = (tech->What_Am_I() == RTTI_BUILDING
                                    && ((BuildingClass*)tech)->Class->Is_Tiberian_Era());
                    bool ts_bldg = (tech->What_Am_I() == RTTI_BUILDING
                                    && ((BuildingClass*)tech)->Class->Is_TS_Era());
                    StructType const fill = (tech->What_Am_I() == RTTI_BUILDING
                                             && TF_Is_Line_Fill_Type(((BuildingClass*)tech)->Class))
                                                ? ((BuildingClass*)tech)->Class->Type
                                                : STRUCT_NONE;
                    if (tech->Unlimbo(Cell_Coord(cell))) {
                        factory->Completed();
                        Abandon_Production(type, bay);
                        if (fill != STRUCT_NONE) {
                            TF_Wall_Line_Fill(this, fill, cell);
                        }

                        if (PlayerPtr == this) {
                            Sound_Effect(ts_bldg ? VOC_TS_PLACE_BUILDING_DOWN
                                                : (td_bldg ? VOC_TD_PLACE_BUILDING_DOWN
                                                           : VOC_PLACE_BUILDING_DOWN));
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

                case OVERLAY_TSWALL:
                    btype = &BuildingTypeClass::As_Reference(STRUCT_TSWALL);
                    break;

                case OVERLAY_TSNWALL:
                    btype = &BuildingTypeClass::As_Reference(STRUCT_TSNWALL);
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

// A standing building of this house that the addon plug would install into (Can_Upgrade), or NULL.
static BuildingClass* TF_Plug_Host(HouseClass const* house, BuildingTypeClass const* plug)
{
    if (plug == NULL || plug->PowersUpBuilding == STRUCT_NONE) {
        return (NULL);
    }
    for (int i = 0; i < Buildings.Count(); i++) {
        BuildingClass* b = Buildings.Ptr(i);
        if (b != NULL && b->IsActive && !b->IsInLimbo && b->Strength > 0 && b->House == house
            && b->Can_Upgrade(plug, house)) {
            return (b);
        }
    }
    return (NULL);
}

// Counts one building this house has chosen or has in production against a host type's slots: a host
// on its way adds its slots, a plug for that host takes one.
static void TF_Plug_Commitment(StructType type, StructType host, int slots, int& room)
{
    if (type == host) {
        room += slots;
    } else if (type != STRUCT_NONE && BuildingTypeClass::As_Reference(type).PowersUpBuilding == host) {
        room--;
    }
}

// How many more of this plug the house has room for: free slots on standing hosts, plus the slots of
// hosts chosen or in production, less the plugs for that host type chosen or in production.
static int TF_Plug_Room(HouseClass const* house, BuildingTypeClass const* plug)
{
    StructType host = plug->PowersUpBuilding;
    int slots = BuildingTypeClass::As_Reference(host).UpgradesMax;
    int room = 0;
    TF_Plug_Commitment(house->BuildStructure, host, slots, room);
    for (int i = 0; i < Buildings.Count(); i++) {
        BuildingClass* bld = Buildings.Ptr(i);
        if (bld == NULL || !bld->IsActive || bld->House != house) {
            continue;
        }
        if (!bld->IsInLimbo && bld->Strength > 0 && *bld == host) {
            room += bld->Class->UpgradesMax - bld->UpgradeLevel;
        }
        if (bld->Factory.Is_Valid()) {
            TechnoClass const* obj = bld->Factory->Get_Object();
            if (obj != NULL && obj->What_Am_I() == RTTI_BUILDING) {
                TF_Plug_Commitment(((BuildingClass const*)obj)->Class->Type, host, slots, room);
            }
        }
    }
    return (room);
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

    // TF: an addon plug goes onto a building of its host type, never onto open ground.
    if (building->Class->PowersUpBuilding != STRUCT_NONE) {
        BuildingClass const* host = TF_Plug_Host(this, building->Class);
        if (host != NULL) {
            CELL origin = Coord_Cell(host->Coord);
            for (short const* list = host->Class->Occupy_List(); *list != REFRESH_EOL; list++) {
                if (Map[(CELL)(origin + *list)].Cell_Building() == host) {
                    return (Cell_Coord((CELL)(origin + *list)));
                }
            }
        }
        return (0);
    }

    // TF: water-bound buildings go on the assessed water. The defence zones are land rings around the base
    // centre, and on most maps no legal coastal cell lies inside them.
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
            return (Cell_Coord(zcell)); // TF: a coordinate, as the preferred-zone return above.
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
// Index of the yard in yards[] nearest pos: a building belongs to the cluster around its nearest yard.
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

        // TF: with yards far apart, only the heaviest cluster around one yard is the base. Averaging every
        // building would put Center between the bases and collapse the zone rings for both.
        COORDINATE yardpos[8];
        int yardcount = 0;
        for (index = 0; index < Buildings.Count() && yardcount < 8; index++) {
            BuildingClass const* b = Buildings.Ptr(index);
            if (b != NULL && !b->IsInLimbo && (HouseClass*)b->House == this && b->Strength > 0
                && b->Class->Is_Construction_Yard()) {
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
        **	relates to the center of the base.
        */
        // TF: the radius is a plain mean over buildings; divided by the cost-weighted count it comes out too
        // small for Which_Zone to admit build sites (docs/ai-upgrade-plan.md).
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

// Per-house fleet rally: once the enemy coast is known, warships mass where the first one stands and sail
// as one hunting wave. The rally clears on release so each wave gathers fresh.
static int const TF_NAVAL_WAVE_MIN = 3;     // smallest fleet worth releasing as a wave.
static int const TF_NAVAL_RALLY_RADIUS = 4; // cells; counts as massed at the rally.
static CELL _tf_fleet_rally[HOUSE_COUNT];
#if TF_DEV_BUILD // TF_AI_DIAG
static int _tf_naval_idle_due[HOUSE_COUNT]; // rate limit for the stuck-warship tracer.
#endif

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

    // TF: while a house has sighted no enemy building, keep two armed units hunting so Mission_Hunt's blind
    // probe finds the enemy. MCVs (a hunt order deploys them) and harvesters never scout.
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

    // TF: idle warships patrol their own water zone while blind and mass into one wave once the enemy coast
    // is known. Never send a ship to a land cell such as a hunt waypoint: it can never arrive.
    if (Session.Type != GAME_NORMAL && IsStarted && Vessels.Count() > 0) {
        int pzone = 0;
        int psize = 0;
        bool pcoastal = false;
        if (TF_Naval_Assessment(pzone, psize, pcoastal)) {
            int fhidx = (int)Class->House;
            int massed = 0;
            if (pcoastal && fhidx >= 0 && fhidx < HOUSE_COUNT && _tf_fleet_rally[fhidx] != 0) {
                for (int vindex = 0; vindex < Vessels.Count(); vindex++) {
                    VesselClass const* v = Vessels.Ptr(vindex);
                    if (v != NULL && !v->IsInLimbo && (HouseClass const*)v->House == this && v->Strength > 0
                        && v->Is_Weapon_Equipped()
                        && (v->Mission == MISSION_GUARD || v->Mission == MISSION_GUARD_AREA)
                        && ::Distance(v->Center_Coord(), Cell_Coord(_tf_fleet_rally[fhidx]))
                               <= TF_NAVAL_RALLY_RADIUS * CELL_LEPTON_W) {
                        massed++;
                    }
                }
            }
            int fenavy = 0;
            int fcap = TF_Naval_Fleet_Cap(pcoastal, &fenavy);
            int fwave = (fcap * 3) / 4;
            if (fwave < TF_NAVAL_WAVE_MIN) {
                fwave = TF_NAVAL_WAVE_MIN;
            }
            bool frelease = pcoastal && massed >= fwave;
#if TF_DEV_BUILD // TF_AI_DIAG
            if (frelease) {
                extern FILE* TF_AI_Diag_File(void);
                FILE* _tfdbg = TF_AI_Diag_File();
                if (_tfdbg != NULL) {
                    fprintf(_tfdbg, "F%ld H%d AL%d NAVAL-WAVE release massed=%d wave=%d cap=%d\n", (long)Frame,
                            (int)Class->House, (int)ActLike, massed, fwave, fcap);
                    fflush(_tfdbg);
                }
            }
#endif
            for (int vindex = 0; vindex < Vessels.Count(); vindex++) {
                VesselClass* v = Vessels.Ptr(vindex);
                if (v == NULL || v->IsInLimbo || !(v->House == this) || v->Strength == 0 || !v->Is_Weapon_Equipped()) {
                    continue;
                }
                bool vidle = (v->Mission == MISSION_GUARD || v->Mission == MISSION_GUARD_AREA);
                bool vzone = (Map[Coord_Cell(v->Center_Coord())].Zones[MZONE_WATER] == pzone);
                if (!vidle || !vzone) {
                    // MISSION_HUNT never ends on its own: a hunter that can't reach or hit its target parks for good.
                    if (v->Mission == MISSION_HUNT && !v->IsDriving
                        && (!Target_Legal(v->TarCom)
                            || !v->In_Range(v->TarCom, v->What_Weapon_Should_I_Use(v->TarCom)))) {
                        v->Assign_Mission(MISSION_GUARD);
                        v->Assign_Destination(TARGET_NONE);
                        continue;
                    }
#if TF_DEV_BUILD // TF_AI_DIAG -- a warship the dispatcher can't see: idle-but-off-zone
                 // (invisible forever) or stalled inside some other mission. One line per
                 // house per ~minute; a healthy moving fleet stays quiet.
                    if ((vidle && !vzone) || (!vidle && !v->IsDriving)) {
                        int dhidx = (int)Class->House;
                        if (dhidx >= 0 && dhidx < HOUSE_COUNT && (int)Frame >= _tf_naval_idle_due[dhidx]) {
                            _tf_naval_idle_due[dhidx] = (int)Frame + 900;
                            extern FILE* TF_AI_Diag_File(void);
                            FILE* _tfdbg = TF_AI_Diag_File();
                            if (_tfdbg != NULL) {
                                fprintf(_tfdbg,
                                        "F%ld H%d AL%d NAVAL-IDLE %s#%d mission=%d cell=(%d,%d) zone=%d/%d "
                                        "radio=%d tarcom=%d navcom=%d\n",
                                        (long)Frame, (int)Class->House, (int)ActLike, v->Class->IniName, (int)v->ID,
                                        (int)v->Mission, (int)Cell_X(Coord_Cell(v->Center_Coord())),
                                        (int)Cell_Y(Coord_Cell(v->Center_Coord())),
                                        (int)Map[Coord_Cell(v->Center_Coord())].Zones[MZONE_WATER], pzone,
                                        v->In_Radio_Contact() ? 1 : 0, Target_Legal(v->TarCom) ? 1 : 0,
                                        Target_Legal(v->NavCom) ? 1 : 0);
                                fflush(_tfdbg);
                            }
                        }
                    }
#endif
                    continue;
                }
                {
                    // Never re-order an engaged ship: a NavCom makes Can_Fire return FIRE_MOVING on turretless hulls.
                    if (Target_Legal(v->TarCom) || v->Target_Something_Nearby(THREAT_RANGE)) {
                        continue;
                    }
                    if (!pcoastal) {
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
                        continue;
                    }
                    if (fhidx < 0 || fhidx >= HOUSE_COUNT) {
                        continue;
                    }
                    if (frelease) {
                        v->Assign_Mission(MISSION_HUNT);
#if TF_DEV_BUILD // TF_AI_DIAG -- one line per hull per wave; hunts that then stall show
                 // up as NAVAL-IDLE lines (not driving, mission!=guard) right after these.
                        {
                            extern FILE* TF_AI_Diag_File(void);
                            FILE* _tfdbg = TF_AI_Diag_File();
                            if (_tfdbg != NULL) {
                                fprintf(_tfdbg, "F%ld H%d AL%d NAVAL-HUNT %s#%d\n", (long)Frame, (int)Class->House,
                                        (int)ActLike, v->Class->IniName, (int)v->ID);
                                fflush(_tfdbg);
                            }
                        }
#endif
                        continue;
                    }
                    if (_tf_fleet_rally[fhidx] == 0) {
                        _tf_fleet_rally[fhidx] = Coord_Cell(v->Center_Coord());
#if TF_DEV_BUILD // TF_AI_DIAG
                        {
                            extern FILE* TF_AI_Diag_File(void);
                            FILE* _tfdbg = TF_AI_Diag_File();
                            if (_tfdbg != NULL) {
                                fprintf(_tfdbg, "F%ld H%d AL%d NAVAL-MASS rally=(%d,%d) wave=%d\n", (long)Frame,
                                        (int)Class->House, (int)ActLike, (int)Cell_X(_tf_fleet_rally[fhidx]),
                                        (int)Cell_Y(_tf_fleet_rally[fhidx]), fwave);
                                fflush(_tfdbg);
                            }
                        }
#endif
                    } else if (::Distance(v->Center_Coord(), Cell_Coord(_tf_fleet_rally[fhidx]))
                               > TF_NAVAL_RALLY_RADIUS * CELL_LEPTON_W) {
                        v->Assign_Mission(MISSION_MOVE);
                        v->Assign_Destination(::As_Target(_tf_fleet_rally[fhidx]));
                    }
                }
            }
            if (frelease && fhidx >= 0 && fhidx < HOUSE_COUNT) {
                _tf_fleet_rally[fhidx] = 0;
            }
        }
    }

    // TF: ferry ground forces by sea: always when the enemy is across water, and on Hard as a second
    // front once the enemy is known to share our sea.
    TF_Ferry_AI();

    // TF: tick the attack wave: release it once gathered, then shepherd its strike.
    TF_Wave_AI();

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
        **	When under attack and there is a need for power in defense,
        **	then consider power building a higher priority.
        */
        // TF: only while the house owns an armed building that needs power to fire.
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

// Counts the armed units, infantry and aircraft this house could commit to an attack wave (no harvesters,
// MCVs or engineers); value, if given, receives that army's worth at list cost.
int HouseClass::TF_Committable_Army(int* value) const
{
    assert(Houses.ID(this) == ID);

    int army = 0;
    int worth = 0;
    int index;

    for (index = 0; index < Units.Count(); index++) {
        UnitClass const* u = Units.Ptr(index);
        if (u != NULL && !u->IsInLimbo && u->House == this && u->Strength > 0 && u->Is_Weapon_Equipped()
            && !u->Class->IsToHarvest && !u->Class->Is_MCV()) {
            army++;
            worth += u->Class->Cost;
        }
    }
    for (index = 0; index < Infantry.Count(); index++) {
        InfantryClass const* i = Infantry.Ptr(index);
        if (i != NULL && !i->IsInLimbo && i->House == this && i->Strength > 0 && i->Is_Weapon_Equipped()) {
            army++;
            worth += i->Class->Cost;
        }
    }
    for (index = 0; index < Aircraft.Count(); index++) {
        AircraftClass const* a = Aircraft.Ptr(index);
        if (a != NULL && !a->IsInLimbo && a->House == this && a->Strength > 0 && a->Is_Weapon_Equipped()) {
            army++;
            worth += a->Class->Cost;
        }
    }

    if (value != NULL) {
        *value = worth;
    }
    return (army);
}

static unsigned TF_Role_Quantity(unsigned const* bquantity, StructType ra);
static int TF_House_Landmass(COORDINATE center);

// Counts this house's harvesters of every lineage on the Units heap; the per-type UQuantity counters fold
// mod units onto vanilla slots and can't be trusted for them.
int HouseClass::TF_Harvesters_Owned(void) const
{
    assert(Houses.ID(this) == ID);

    int owned = 0;
    for (int index = 0; index < Units.Count(); index++) {
        UnitClass const* u = Units.Ptr(index);
        if (u != NULL && (HouseClass const*)u->House == this
            && (*u == UNIT_TDHARV || *u == UNIT_HARVESTER || *u == UNIT_TSHARV)) {
            owned++;
        }
    }
    return (owned);
}

// Refineries this house should have by this point in the match, capped at RefineryLimit. AI_Building
// takes the larger of this and the vanilla RefineryRatio target.
int HouseClass::TF_Eco_Refinery_Target(void) const
{
    assert(Houses.ID(this) == ID);

    int want = 1;
    if (Frame >= (TICKS_PER_MINUTE * 5) / 2) {
        want = 2;
    }
    if (Frame >= TICKS_PER_MINUTE * 6) {
        want = 3;
    }
    if (Frame >= TICKS_PER_MINUTE * 10) {
        want = 4;
    }
    if (want > Rule.RefineryLimit) {
        want = Rule.RefineryLimit;
    }
    return (want);
}

// Harvesters to field for this many refineries: two each on Hard, one and a half on Medium, one on Easy.
int HouseClass::TF_Eco_Harvester_Target(int refineries) const
{
    assert(Houses.ID(this) == ID);

    if (IQ >= 5) {
        return (refineries * 2);
    }
    if (IQ == 4) {
        return ((refineries * 3) / 2);
    }
    return (refineries);
}

// Per-match AI clocks, cleared on every scenario load (TF_AI_Clocks_Reset): when each house's eco hold began
// and whether it is spent, and since when each base-builder candidate has lost its tie.
static long _tf_eco_hold_since[HOUSE_COUNT];
static bool _tf_eco_hold_spent[HOUSE_COUNT];
static int _tf_waiting_since[HOUSE_COUNT][STRUCT_COUNT];

// Clears the per-match AI clocks; frame numbers restart each match, so stale ones would never expire.
void TF_AI_Clocks_Reset(void)
{
    memset(_tf_eco_hold_since, 0, sizeof(_tf_eco_hold_since));
    memset(_tf_eco_hold_spent, 0, sizeof(_tf_eco_hold_spent));
    memset(_tf_waiting_since, 0, sizeof(_tf_waiting_since));
}

// True while the house is below its refinery or harvester target and ore remains, so combat production
// yields to the economy. A hit in the last two minutes lifts the hold; an unbroken hold lapses at four.
bool HouseClass::TF_Eco_Below_Target(int* refwant, int* harvwant, int* refhave) const
{
    assert(Houses.ID(this) == ID);

    int refq = (int)TF_Role_Quantity(BQuantity, STRUCT_REFINERY);
    int rwant = TF_Eco_Refinery_Target();
    int hwant = TF_Eco_Harvester_Target(refq);
    if (refwant != NULL) {
        *refwant = rwant;
    }
    if (harvwant != NULL) {
        *harvwant = hwant;
    }
    if (refhave != NULL) {
        *refhave = refq;
    }
    if (IsTiberiumShort) {
        return (false);
    }
    if (LATime != 0 && (long)Frame - (long)LATime < TICKS_PER_MINUTE * 2) {
        return (false);
    }
    bool below = (refq < rwant || TF_Harvesters_Owned() < hwant);

    enum
    {
        TF_ECO_HOLD_MAX = TICKS_PER_MINUTE * 4
    };
    int hidx = (int)Class->House;
    if (hidx < 0 || hidx >= HOUSE_COUNT) {
        return (below);
    }
    if (!below) {
        _tf_eco_hold_since[hidx] = 0;
        _tf_eco_hold_spent[hidx] = false;
        return (false);
    }
    if (_tf_eco_hold_spent[hidx]) {
        return (false);
    }
    if (_tf_eco_hold_since[hidx] == 0) {
        _tf_eco_hold_since[hidx] = (long)Frame;
    } else if ((long)Frame - _tf_eco_hold_since[hidx] > TF_ECO_HOLD_MAX) {
        _tf_eco_hold_spent[hidx] = true;
        return (false);
    }
    return (true);
}

// Attack-wave staging: committed units march to a cell short of the nearest known enemy building, gather
// and are released together. Per-house state lives in file statics, cleared on every scenario load.
enum
{
    TF_WAVE_MAX = 96,                                 // roster capacity per house
    TF_WAVE_STAGE_BACK = 9,                           // cells short of the known enemy building
    TF_WAVE_GATHER_RADIUS = 5,                        // cells; "arrived" at the staging cell
    TF_WAVE_GATHER_MIN_PCT = 70,                      // release once this share has arrived...
    TF_WAVE_GATHER_TIMEOUT = TICKS_PER_MINUTE * 4     // ...or when the stragglers are taking too long
};
struct TFWaveStruct
{
    TARGET Roster[TF_WAVE_MAX];
    int Count;
    CELL Stage;
    long Deadline;
    bool Gathering;
    bool Striking;   // released on attack-move; members that arrive convert to hunt
    long StrikeUntil;
};
enum
{
    TF_WAVE_STRIKE_TIMEOUT = TICKS_PER_MINUTE * 6 // stop shepherding a released wave after this
};
static TFWaveStruct _tf_wave[HOUSE_COUNT];

// True when f is on the roster of the house's gathering or striking attack wave.
static bool TF_Wave_Member(FootClass const* f, HouseClass const* house)
{
    if (f == NULL || house == NULL) {
        return (false);
    }
    int hidx = (int)house->Class->House;
    if (hidx < 0 || hidx >= HOUSE_COUNT) {
        return (false);
    }
    TFWaveStruct const& wave = _tf_wave[hidx];
    if (!wave.Gathering && !wave.Striking) {
        return (false);
    }
    TARGET me = f->As_Target();
    for (int i = 0; i < wave.Count; i++) {
        if (wave.Roster[i] == me) {
            return (true);
        }
    }
    return (false);
}

// Clears every house's attack wave.
void TF_Wave_Reset(void)
{
    for (int h = 0; h < HOUSE_COUNT; h++) {
        _tf_wave[h].Count = 0;
        _tf_wave[h].Stage = 0;
        _tf_wave[h].Deadline = 0;
        _tf_wave[h].Gathering = false;
        _tf_wave[h].Striking = false;
        _tf_wave[h].StrikeUntil = 0;
    }
}

// The discovered enemy building nearest this house's base centre, or 0 while the house has seen none.
COORDINATE HouseClass::TF_Wave_Known_Enemy_Coord(void) const
{
    assert(Houses.ID(this) == ID);

    COORDINATE best = 0;
    int bestdist = 0;
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass const* b = Buildings.Ptr(index);
        if (b != NULL && !b->IsInLimbo && b->Strength > 0 && !Is_Ally(b) && b->House->Class->House != HOUSE_NEUTRAL
            && b->Is_Discovered_By_Player((HouseClass*)this)) {
            int dist = ::Distance(Center, b->Center_Coord());
            if (best == 0 || dist < bestdist) {
                best = b->Center_Coord();
                bestdist = dist;
            }
        }
    }
    return (best);
}

// Where the wave gathers: TF_WAVE_STAGE_BACK cells short of the nearest known enemy building (halfway if
// nearer), on our own landmass. 0 when there is nothing to stage against or the enemy is across water.
CELL HouseClass::TF_Wave_Stage_Cell(void) const
{
    assert(Houses.ID(this) == ID);

    COORDINATE enemy = TF_Wave_Known_Enemy_Coord();
    if (enemy == 0 || Center == 0) {
        return (0);
    }
    int dx = Coord_X(enemy) - Coord_X(Center);
    int dy = Coord_Y(enemy) - Coord_Y(Center);
    int dist = ::Distance(Center, enemy);
    if (dist <= 0) {
        return (0);
    }
    int back = TF_WAVE_STAGE_BACK * CELL_LEPTON_W;
    int along = dist - back;
    if (along < dist / 2) {
        along = dist / 2;
    }
    int ourland = TF_House_Landmass(Center);
    CELL ecell = Coord_Cell(enemy);
    if (ourland <= 0 || ecell <= 0 || !Map.In_Radar(ecell) || Map[ecell].Zones[MZONE_NORMAL] != ourland) {
        return (0);
    }
    COORDINATE stage = XY_Coord(Coord_X(Center) + (dx * along) / dist, Coord_Y(Center) + (dy * along) / dist);
    CELL cell = Coord_Cell(stage);
    cell = Map.Nearby_Location(cell, SPEED_TRACK, ourland, MZONE_NORMAL);
    if (cell <= 0 || !Map.In_Radar(cell) || Map[cell].Zones[MZONE_NORMAL] != ourland) {
        return (0);
    }
    return (cell);
}

// Ticks the attack wave: releases a gathering wave once TF_WAVE_GATHER_MIN_PCT has arrived or time runs
// out, then turns a striking wave's members to hunt as their attack-move ends.
void HouseClass::TF_Wave_AI(void)
{
    assert(Houses.ID(this) == ID);

    int hidx = (int)Class->House;
    if (hidx < 0 || hidx >= HOUSE_COUNT) {
        return;
    }
    TFWaveStruct& wave = _tf_wave[hidx];

    if (wave.Striking) {
        int living = 0;
        int converted = 0;
        for (int i = 0; i < wave.Count; i++) {
            TechnoClass* t = As_Techno(wave.Roster[i]);
            if (t == NULL || t->IsInLimbo || t->Strength == 0 || (HouseClass const*)t->House != this) {
                continue;
            }
            living++;
            if (!t->AttackMove && t->Mission != MISSION_HUNT && t->Mission != MISSION_ATTACK
                && t->Mission != MISSION_CAPTURE) {
                t->Assign_Mission(MISSION_HUNT);
                converted++;
            }
        }
#if TF_DEV_BUILD // TF_AI_DIAG
        if (converted > 0) {
            extern FILE* TF_AI_Diag_File(void);
            FILE* _tfdbg = TF_AI_Diag_File();
            if (_tfdbg != NULL) {
                fprintf(_tfdbg, "F%ld H%d AL%d WAVE-STRIKE hunt=%d living=%d\n", (long)Frame, (int)Class->House,
                        (int)ActLike, converted, living);
                fflush(_tfdbg);
            }
        }
#endif
        if (living == 0 || (long)Frame >= wave.StrikeUntil) {
            wave.Striking = false;
            wave.Count = 0;
        }
        return;
    }

    if (!wave.Gathering) {
        return;
    }
    int alive = 0;
    int arrived = 0;
    for (int i = 0; i < wave.Count; i++) {
        TechnoClass* t = As_Techno(wave.Roster[i]);
        if (t == NULL || t->IsInLimbo || t->Strength == 0 || (HouseClass const*)t->House != this) {
            continue;
        }
        alive++;
        if (wave.Stage != 0 && t->Distance(Cell_Coord(wave.Stage)) <= TF_WAVE_GATHER_RADIUS * CELL_LEPTON_W) {
            arrived++;
        }
    }
    bool release = false;
    char const* why = "";
    if (alive == 0) {
        release = true;
        why = "dead";
    } else if (arrived * 100 >= alive * TF_WAVE_GATHER_MIN_PCT) {
        release = true;
        why = "gathered";
    } else if ((long)Frame >= wave.Deadline) {
        release = true;
        why = "timeout";
    }
    if (!release) {
        return;
    }

    COORDINATE objective = (IQ >= 5) ? TF_Wave_Known_Enemy_Coord() : 0;
    TARGET objtarget = (objective != 0) ? ::As_Target(Coord_Cell(objective)) : TARGET_NONE;
    for (int i = 0; i < wave.Count; i++) {
        TechnoClass* t = As_Techno(wave.Roster[i]);
        if (t == NULL || t->IsInLimbo || t->Strength == 0 || (HouseClass const*)t->House != this) {
            continue;
        }
        if (objtarget != TARGET_NONE && t->Is_Foot()) {
            t->Assign_Target(TARGET_NONE);
            t->Assign_Mission(MISSION_MOVE);
            t->AttackMove = 1;
            t->RememberedNavCom = objtarget;
            ((FootClass*)t)->Assign_Destination(objtarget);
        } else {
            t->Assign_Mission(MISSION_HUNT);
        }
    }
#if TF_DEV_BUILD // TF_AI_DIAG
    {
        extern FILE* TF_AI_Diag_File(void);
        FILE* _tfdbg = TF_AI_Diag_File();
        if (_tfdbg != NULL) {
            fprintf(_tfdbg,
                    "F%ld H%d AL%d WAVE-RELEASE why=%s mode=%s alive=%d arrived=%d roster=%d stage=%d objective=%d\n",
                    (long)Frame,
                    (int)Class->House,
                    (int)ActLike,
                    why,
                    objtarget != TARGET_NONE ? "attack-move" : "hunt",
                    alive,
                    arrived,
                    wave.Count,
                    (int)wave.Stage,
                    (int)Coord_Cell(objective));
            fflush(_tfdbg);
        }
    }
#endif
    wave.Stage = 0;
    wave.Gathering = false;
    if (objtarget != TARGET_NONE && alive > 0) {
        wave.Striking = true;
        wave.StrikeUntil = (long)Frame + TF_WAVE_STRIKE_TIMEOUT;
    } else {
        wave.Count = 0;
    }
}

struct TFWaveDialsStruct
{
    int Floor;         // Never launch below this many committable units.
    int FloorValue;    // ...nor below this much army at list cost.
    int Ceiling;       // Always launch at or above this many units.
    int CeilingValue;  // ...or at or above this much army at list cost.
    int MidChance;     // Percent chance of launching between the two.
    int Recheck;       // Frames to wait after declining.
    int IntervalScale; // Percent scale on the post-launch interval.
};

// Attack-wave pacing by IQ (Easy 3, Medium 4, Hard 5). Difficulty moves frequency only; the floors are the
// same at every tier, since a token wave just dies in detail (docs/ai-upgrade-plan.md).
static TFWaveDialsStruct TF_Wave_Dials(int iq)
{
    TFWaveDialsStruct dials;

    if (iq <= 3) {
        dials.Floor = 10;
        dials.FloorValue = 8000;
        dials.Ceiling = 32;
        dials.CeilingValue = 26000;
        dials.MidChance = 25;
        dials.Recheck = TICKS_PER_SECOND * 90;
        dials.IntervalScale = 133;
    } else if (iq == 4) {
        dials.Floor = 10;
        dials.FloorValue = 8000;
        dials.Ceiling = 30;
        dials.CeilingValue = 22000;
        dials.MidChance = 40;
        dials.Recheck = TICKS_PER_SECOND * 60;
        dials.IntervalScale = 100;
    } else {
        dials.Floor = 10;
        dials.FloorValue = 8000;
        dials.Ceiling = 26;
        dials.CeilingValue = 18000;
        dials.MidChance = 60;
        dials.Recheck = TICKS_PER_SECOND * 30;
        dials.IntervalScale = 67;
    }

    return (dials);
}

bool HouseClass::AI_Attack(UrgencyType)
{
    assert(Houses.ID(this) == ID);

    // TF: launch on army size and worth rather than a flat roll: hold below the floor, commit at the ceiling,
    // roll between, and recheck a decline sooner than a launch (docs/ai-upgrade-plan.md).
    TFWaveDialsStruct dials = TF_Wave_Dials(IQ);
    int worth = 0;
    int army = TF_Committable_Army(&worth);

    bool has_factory = (TF_Role_Quantity(ActiveBQuantity, STRUCT_WEAP) > 0);

    enum
    {
        TF_WAVE_FLOOR_MIN = 4,
        TF_WAVE_FLOOR_DECAY_START = TICKS_PER_MINUTE * 20,
        TF_WAVE_FLOOR_DECAY_PERIOD = TICKS_PER_MINUTE * 2
    };
    int floor = dials.Floor;
    int floorvalue = dials.FloorValue;
    bool strangled = (IsTiberiumShort || TF_Role_Quantity(BQuantity, STRUCT_REFINERY) < 2
                      || TF_Harvesters_Owned() < 2);
    if (strangled && Frame > TF_WAVE_FLOOR_DECAY_START) {
        int steps = (int)((Frame - TF_WAVE_FLOOR_DECAY_START) / TF_WAVE_FLOOR_DECAY_PERIOD);
        floor -= steps;
        if (floor < TF_WAVE_FLOOR_MIN) {
            floor = TF_WAVE_FLOOR_MIN;
        }
        floorvalue = (dials.FloorValue * floor) / dials.Floor;
    }

    bool wave_gathering = false;
    {
        int whidx = (int)Class->House;
        if (whidx >= 0 && whidx < HOUSE_COUNT) {
            wave_gathering = _tf_wave[whidx].Gathering;
        }
    }

    char const* reason;
    bool launch;
    if (Frame > TICKS_PER_MINUTE && !CurBuildings) {
        launch = true;
        reason = "desperation";
    } else if (wave_gathering) {
        launch = false;
        reason = "staging";
    } else if (!has_factory && CurBuildings) {
        launch = false;
        reason = "no-factory";
    } else if (worth >= dials.CeilingValue || (army >= dials.Ceiling && worth >= floorvalue)) {
        launch = true;
        reason = "ceiling";
    } else if (army < floor) {
        launch = false;
        reason = "massing";
    } else if (worth < floorvalue) {
        launch = false;
        reason = "massing-value";
    } else {
        launch = Percent_Chance(dials.MidChance);
        reason = launch ? "roll" : "roll-declined";
    }
    bool shuffle = !launch;
    bool forced = (CurBuildings == 0);

    // TF: idle guards reposition about every two minutes, however short the recheck.
    bool reposition = launch || Percent_Chance((dials.Recheck * 100) / (TICKS_PER_SECOND * 120));

    // TF: the share of the army sent grows with the base's armed buildings (AI Boost 3.2's send percentage).
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
                    "F%ld H%d AL%d WAVE-%s why=%s army=%d floor=%d ceiling=%d value=%d floorvalue=%d ceilingvalue=%d "
                    "iq=%d defences=%d sendpercent=%d forced=%d\n",
                    (long)Frame,
                    (int)Class->House,
                    (int)ActLike,
                    shuffle ? "SHUFFLE (nothing sent)" : "LAUNCH",
                    reason,
                    army,
                    floor,
                    dials.Ceiling,
                    worth,
                    floorvalue,
                    dials.CeilingValue,
                    IQ,
                    defences,
                    sendpercent,
                    (int)forced);
            fflush(_tfdbg);
        }
    }
#endif

    // TF: a launch gathers its ground units at a staging cell for TF_Wave_AI to release together. Without
    // one, a Hard house attack-moves on a known enemy building on its own landmass; the rest hunt.
    CELL stage = 0;
    TFWaveStruct* wave = NULL;
    TARGET direct = TARGET_NONE; // Hard, no staging cell: attack-move from home
    if (launch) {
        int hidx = (int)Class->House;
        if (hidx >= 0 && hidx < HOUSE_COUNT) {
            stage = TF_Wave_Stage_Cell();
            wave = &_tf_wave[hidx];
            wave->Count = 0;
            wave->Striking = false;
            wave->Gathering = false;
            wave->Stage = 0;
            if (stage != 0) {
                wave->Stage = stage;
                wave->Deadline = (long)Frame + TF_WAVE_GATHER_TIMEOUT;
                wave->Gathering = true;
            } else if (IQ >= 5) {
                COORDINATE objective = TF_Wave_Known_Enemy_Coord();
                CELL ocell = (objective != 0) ? Coord_Cell(objective) : 0;
                int ourland = TF_House_Landmass(Center);
                if (ocell > 0 && Map.In_Radar(ocell) && ourland > 0 && Map[ocell].Zones[MZONE_NORMAL] == ourland) {
                    direct = ::As_Target(ocell);
                    wave->Striking = true;
                    wave->StrikeUntil = (long)Frame + TF_WAVE_STRIKE_TIMEOUT;
                }
            }
            if (!wave->Gathering && !wave->Striking) {
                wave = NULL;
            }
        }
    }

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

            // TF: a unit already attack-moving or hunting stays on its wave rather than return to a staging cell.
            if (!shuffle && (u->AttackMove || u->Mission == MISSION_HUNT || u->Mission == MISSION_ATTACK)) {
                continue;
            }

            // TF: scatter on launch frees units wedged in the base (AI Boost 3.2). Never harvesters: a scatter
            // can pull one off its dock approach mid-sequence.
            if (!shuffle && !u->Class->IsToHarvest) {
                u->Scatter(0, true, true);
            }
            if (!shuffle && u->Is_Weapon_Equipped() && (forced || Percent_Chance(sendpercent))) {
                if (wave != NULL && wave->Count < TF_WAVE_MAX && stage != 0) {
                    u->Assign_Mission(MISSION_MOVE);
                    u->Assign_Destination(::As_Target(stage));
                    wave->Roster[wave->Count++] = u->As_Target();
                } else if (wave != NULL && wave->Count < TF_WAVE_MAX && direct != TARGET_NONE) {
                    u->Assign_Target(TARGET_NONE);
                    u->Assign_Mission(MISSION_MOVE);
                    u->AttackMove = 1;
                    u->RememberedNavCom = direct;
                    u->Assign_Destination(direct);
                    wave->Roster[wave->Count++] = u->As_Target();
                } else {
                    u->Assign_Mission(MISSION_HUNT);
                }
            } else if (!shuffle && u->Is_Weapon_Equipped()) {

                // TF: armed units left out of the wave stand home guard.
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
            // TF: as for vehicles: wave members stay on their wave, and a launch scatters the rest.
            if (!shuffle && (i->AttackMove || i->Mission == MISSION_HUNT || i->Mission == MISSION_ATTACK)) {
                continue;
            }
            if (!shuffle) {
                i->Scatter(0, true, true);
            }

            // TF: the TD and TS engineers join the wave like RENOVATOR, so Mission_Hunt can send them to capture.
            if (!shuffle
                && (i->Is_Weapon_Equipped() || *i == INFANTRY_RENOVATOR || *i == INFANTRY_TDE6
                    || *i == INFANTRY_TSENGINEER)
                && (forced || Percent_Chance(sendpercent))) {
                if (wave != NULL && wave->Count < TF_WAVE_MAX && stage != 0) {
                    i->Assign_Mission(MISSION_MOVE);
                    i->Assign_Destination(::As_Target(stage));
                    wave->Roster[wave->Count++] = i->As_Target();
                } else if (wave != NULL && wave->Count < TF_WAVE_MAX && direct != TARGET_NONE) {
                    i->Assign_Target(TARGET_NONE);
                    i->Assign_Mission(MISSION_MOVE);
                    i->AttackMove = 1;
                    i->RememberedNavCom = direct;
                    i->Assign_Destination(direct);
                    wave->Roster[wave->Count++] = i->As_Target();
                } else {
                    i->Assign_Mission(MISSION_HUNT);
                }
            } else if (!shuffle && i->Is_Weapon_Equipped()) {

                // TF: armed infantry left out of the wave stand home guard.
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
#if TF_DEV_BUILD // TF_AI_DIAG
    if (launch) {
        extern FILE* TF_AI_Diag_File(void);
        FILE* _tfdbg = TF_AI_Diag_File();
        if (_tfdbg != NULL) {
            fprintf(_tfdbg,
                    "F%ld H%d AL%d WAVE-STAGE stage=%d roster=%d mode=%s\n",
                    (long)Frame,
                    (int)Class->House,
                    (int)ActLike,
                    (int)stage,
                    wave != NULL ? wave->Count : 0,
                    stage != 0 ? "gather" : (direct != TARGET_NONE ? "direct-attack-move" : "hunt"));
            fflush(_tfdbg);
        }
    }
#endif
    if (wave != NULL && wave->Count == 0) {
        wave->Gathering = false;
        wave->Striking = false;
        wave->Stage = 0;
    }

    // TF: a launch waits the rules.ini AttackInterval scaled by difficulty; a decline is rechecked sooner.
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
                  // TF: naval yards are production buildings, so only a power emergency under attack sells them,
                  // not every mild dip.
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
                  // TF: the base builder rebuilds naval yards, tech centres and the repair bay, so they sell only
                  // when broke with no income. At LOW they would be sold and rebuilt between harvester dumps.
                  {STRUCT_SHIP_YARD, URGENCY_MEDIUM},
                  {STRUCT_SUB_PEN, URGENCY_MEDIUM},
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

// Skirmish base-builder substitution: AI_Building names vanilla RA buildings for each base role, and these
// helpers swap in the building of the house's own faction (docs/ai-upgrade-plan.md).

// The TS GDI tree's building for a base role, or NULL where it has none (navy, fixed-wing airfield). Defence
// roles name the armed tower plug (TF_AI_Tower_Step) and advanced power the turbine addon (TF_AI_Plug_Fits).
static BuildingTypeClass const* TF_TS_Equivalent(StructType ra)
{
    StructType ts = STRUCT_NONE;
    switch (ra) {
    case STRUCT_POWER:
        ts = STRUCT_TSPOWR;
        break;
    case STRUCT_ADVANCED_POWER:
        ts = STRUCT_TSTURB;
        break;
    case STRUCT_REFINERY:
        ts = STRUCT_TSPROC;
        break;
    case STRUCT_BARRACKS:
    case STRUCT_TENT:
        ts = STRUCT_TSPILE;
        break;
    case STRUCT_WEAP:
        ts = STRUCT_TSWEAP;
        break;
    case STRUCT_PILLBOX: // light base defence
    case STRUCT_CAMOPILLBOX:
    case STRUCT_TURRET:
    case STRUCT_FLAME_TURRET:
        ts = STRUCT_TSVULC;
        break;
    case STRUCT_TESLA: // advanced base defence
        ts = STRUCT_TSROCK;
        break;
    case STRUCT_SAM: // dedicated AA
    case STRUCT_AAGUN:
        ts = STRUCT_TSCSAM;
        break;
    case STRUCT_RADAR:
        ts = STRUCT_TSRADR;
        break;
    case STRUCT_ADVANCED_TECH:
    case STRUCT_SOVIET_TECH:
        ts = STRUCT_TSTECH;
        break;
    case STRUCT_HELIPAD:
        ts = STRUCT_TSHPAD;
        break;
    case STRUCT_REPAIR:
        ts = STRUCT_TSDEPT;
        break;
    case STRUCT_CONST:
        ts = STRUCT_TSFACT;
        break;
    default:
        break;
    }
    return (ts != STRUCT_NONE) ? &BuildingTypeClass::As_Reference(ts) : NULL;
}

// The house's own faction building for a vanilla base role, or NULL to keep the vanilla pick. RA houses
// swap only their side's war factory, helipad, yard and naval yard.
static BuildingTypeClass const* TF_Skirmish_Equivalent(StructType ra, HousesType actlike)
{
    if (Is_TS_GDI(actlike)) {
        return (TF_TS_Equivalent(ra));
    }

    if (actlike != HOUSE_GOOD && actlike != HOUSE_BAD) {
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
        return (gdi ? &BuildingTypeClass::As_Reference(STRUCT_TDGHPAD)
                    : &BuildingTypeClass::As_Reference(STRUCT_TDNHPAD));
    case STRUCT_AIRSTRIP: // GDI fixed-wing airfield (the A-10 host); Nod flies helis only
        return (gdi ? c_gafld : NULL);
    case STRUCT_REPAIR:
        return (c_fix);
    case STRUCT_SHIP_YARD: // naval yard role
    case STRUCT_SUB_PEN:
        return (gdi ? c_gyard : c_npen);
    case STRUCT_CONST:
        return (gdi ? &BuildingTypeClass::As_Reference(STRUCT_TDGFACT)
                    : &BuildingTypeClass::As_Reference(STRUCT_TDNFACT));
    default:
        return (NULL);
    }
}

// The building the skirmish AI queues for a base role: the house's own faction equivalent, else the vanilla
// RA structure. Can_Build still has the final say.
static BuildingTypeClass const* TF_Skirmish_Pick(StructType ra, HousesType actlike)
{
    BuildingTypeClass const* sub = TF_Skirmish_Equivalent(ra, actlike);
    return (sub != NULL) ? sub : &BuildingTypeClass::As_Reference(ra);
}

/*
**	True when the builder can use this building now: always for an ordinary building, and for
**	an addon plug only while a host slot is free and unclaimed.
*/
static bool TF_AI_Plug_Fits(HouseClass const* house, BuildingTypeClass const* b)
{
    return (b == NULL || b->PowersUpBuilding == STRUCT_NONE || TF_Plug_Room(house, b) > 0);
}

// For a component tower plug: the plug while a bare tower is free, else the bare tower, so the builder lays
// a tower on one pass and arms it on a later one. Any other building passes through.
static BuildingTypeClass const* TF_AI_Tower_Step(HouseClass const* house, BuildingTypeClass const* b)
{
    if (b == NULL || b->PowersUpBuilding != STRUCT_TSCTWR || TF_AI_Plug_Fits(house, b)) {
        return (b);
    }
    return (&BuildingTypeClass::As_Reference(STRUCT_TSCTWR));
}

/*
**	True when this house has the given building chosen next or on a factory's line.
*/
static bool TF_AI_Building_Pending(HouseClass const* house, StructType type)
{
    if (house->BuildStructure == type) {
        return (true);
    }
    for (int i = 0; i < Buildings.Count(); i++) {
        BuildingClass const* bld = Buildings.Ptr(i);
        if (bld != NULL && bld->IsActive && bld->House == house && bld->Factory.Is_Valid()) {
            TechnoClass const* obj = bld->Factory->Get_Object();
            if (obj != NULL && obj->What_Am_I() == RTTI_BUILDING && ((BuildingClass const*)obj)->Class->Type == type) {
                return (true);
            }
        }
    }
    return (false);
}

// The next TS Upgrade Centre plug this house wants, or STRUCT_NONE: the Ion Cannon Uplink, then the Drop
// Pod Node or Seeker Control, rolled per house from Seed. Never one installed or on its way.
static StructType TF_AI_Upgrade_Plug(HouseClass const* house)
{
    unsigned roll = (unsigned)Seed * 2654435761u + (unsigned)house->Class->House * 40503u;
    StructType const order[2] = {STRUCT_TSPION, ((roll >> 16) & 1) ? STRUCT_TSPODS : STRUCT_TSSEEK};
    for (int i = 0; i < 2; i++) {
        if (TF_House_Has_Plug(house, order[i])) {
            continue;
        }
        return (TF_AI_Building_Pending(house, order[i]) ? STRUCT_NONE : order[i]);
    }
    return (STRUCT_NONE);
}

// Type of the house's faction equivalent for a base role, or -1 when the vanilla pick stands. Callers add
// its BQuantity to the vanilla slot's so "do I have one?" gates see the faction's own buildings.
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

// Buildings filling a capacity role, counted across every faction lineage: a captured factory builds too.
// Never call it for an unlock role (tech centre, radar); docs/ai-upgrade-plan.md has the counting rules.
static unsigned TF_Role_Quantity(unsigned const* bquantity, StructType ra)
{
    static const HousesType _lineages[] = {HOUSE_GOOD, HOUSE_BAD, HOUSE_ENGLAND, HOUSE_USSR, HOUSE_GERMANY};

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

// True while the house can expect credits: a refinery, Tiberium on the map and a live harvester. Harvesters
// are counted off the Units heap because UQuantity folds mod unit types onto vanilla slots.
bool HouseClass::TF_Has_Income(void) const
{
    assert(Houses.ID(this) == ID);

    if (IsTiberiumShort || TF_Role_Quantity(BQuantity, STRUCT_REFINERY) == 0) {
        return (false);
    }
    for (int index = 0; index < Units.Count(); index++) {
        UnitClass const* u = Units.Ptr(index);
        if (u != NULL && (HouseClass*)u->House == this
            && (*u == UNIT_TDHARV || *u == UNIT_HARVESTER || *u == UNIT_TSHARV)) {
            return (true);
        }
    }
    return (false);
}

// Naval tuning: the AI builds a navy only on water of at least TF_NAVAL_POND_MIN cells within
// TF_NAVAL_COAST_RADIUS of its base. TF_Naval_Fleet_Cap sizes the fleet from the patrol, floor and max.
static int const TF_NAVAL_COAST_RADIUS = 20;
static int const TF_NAVAL_POND_MIN = 80;
static int const TF_NAVAL_PATROL_CAP = 2;
static int const TF_NAVAL_FLEET_FLOOR = 4;
static int const TF_NAVAL_FLEET_MAX = 12;

// The largest water zone in reach of the base worth a navy, and whether a discovered enemy building is on
// its shore. False with size = -(largest pond) when none is. Reads deterministic state only: lockstep-safe.
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

// Vessels to hold: a patrol until an enemy shore is known, then the strongest single enemy navy this house
// has seen (a scouted yard counts as a patrol), kept between floor and max. enemy_navy gets that size.
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

// Sea-transport ferrying: up to TF_FERRY_OPS_MAX transports per house carry loads of at least
// TF_FERRY_MIN_LOAD units to one beachhead, where they mass and attack as a wave.
static int const TF_FERRY_ROSTER_MAX = 5;
static int const TF_FERRY_MIN_LOAD = 3;
static int const TF_FERRY_TIMEOUT = 4500;      // pickup / load / unload stall limit (~5 min).
static int const TF_FERRY_SAIL_TIMEOUT = 9000; // crossing limit before the op re-plans.
static int const TF_FERRY_SAIL_REPATH = 300;   // no closing on the landing for ~20s -> fresh path.
static int const TF_FERRY_OPS_MAX = 4;         // concurrent transports per house -- the convoy.
static int const TF_FERRY_ESCORTS = 3;         // warships sent ahead to suppress the beach.
static int const TF_FERRY_THREAT_RANGE = 8;    // cells; a defended stretch of coast scores worse.
static int const TF_FERRY_WAVE_MIN = 15;       // beachhead strength that releases the attack wave.
static int const TF_FERRY_WAVE_STALL = 3000;   // no fresh delivery for this long forces a release...
static int const TF_FERRY_WAVE_STALL_MIN = 5;  // ...provided at least this many made it ashore.
static int const TF_FERRY_SECOND_FRONT_MIN = 18; // surplus idle army before opening a second front.
static int const TF_FERRY_BEACH_RADIUS = 10;   // cells; beachhead membership on a SHARED landmass.

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
    int BestDist;   // closest approach to the landing so far (SAIL progress watchdog).
    int BestFrame;  // when that closest approach was set.
    int StallFrame; // first frame seen parked mid-move (the patient-queue signature).
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

#if TF_DEV_BUILD // TF_AI_DIAG
/*
**	TFF_IDLE holds an op back for one of four reasons, and every one of them used
**	to break SILENTLY -- an LST parked against the pen for a whole match was
**	unattributable from the log. One rate-limited line per house names the gate.
*/
static int _tf_ferry_wait_due[HOUSE_COUNT];
static void TF_Ferry_Wait_Diag(HouseClass const* h, char const* reason, int a, int b)
{
    extern FILE* TF_AI_Diag_File(void);
    int hidx = (int)h->Class->House;
    if (hidx < 0 || hidx >= HOUSE_COUNT || (int)Frame < _tf_ferry_wait_due[hidx]) {
        return;
    }
    _tf_ferry_wait_due[hidx] = (int)Frame + 900;
    FILE* _tfdbg = TF_AI_Diag_File();
    if (_tfdbg != NULL) {
        fprintf(_tfdbg, "F%ld H%d AL%d FERRY-WAIT %s a=%d b=%d\n", (long)Frame, (int)h->Class->House,
                (int)h->ActLike, reason, a, b);
        fflush(_tfdbg);
    }
}
#endif

// Clears the ferry, beachhead and fleet-rally statics; HouseClass::Init calls it on every scenario load, as
// a stale beach rally would satisfy the expansion-MCV gate on a map with no beachhead.
void TF_Skirmish_Naval_Reset(void)
{
    for (int h = 0; h < HOUSE_COUNT; h++) {
        for (int o = 0; o < TF_FERRY_OPS_MAX; o++) {
            _tf_ferry[h][o] = TFFerryOpStruct();
        }
        _tf_beach_rally[h] = 0;
        _tf_beach_delivered[h] = 0;
        _tf_fleet_rally[h] = 0;
#if TF_DEV_BUILD // TF_AI_DIAG
        _tf_ferry_wait_due[h] = 0;
        _tf_naval_idle_due[h] = 0;
#endif
    }
}

// How far the ferry may draft: SPARE takes teamless guards, STAGING also team units on guard, and DOOMED
// (blocked route only) also units on hunt or move orders, whose land orders can never arrive.
enum
{
    TF_DRAFT_SPARE,
    TF_DRAFT_STAGING,
    TF_DRAFT_DOOMED
};
static bool TF_Wave_Member(FootClass const* f, HouseClass const* house);

// True when f may join a ferry roster from landmass ourland at this draft level. Never a wave member.
static bool TF_Ferry_Eligible(FootClass const* f, HouseClass const* house, int ourland, int draft = TF_DRAFT_SPARE)
{
    if (f == NULL || (HouseClass const*)f->House != house || f->IsInLimbo || f->Strength == 0
        || !f->Is_Weapon_Equipped() || Map[Coord_Cell(f->Center_Coord())].Zones[MZONE_NORMAL] != ourland) {
        return (false);
    }
    if (TF_Wave_Member(f, house)) {
        return (false);
    }
    if (!f->Team.Is_Valid() && f->Mission == MISSION_GUARD) {
        return (true);
    }
    if (draft >= TF_DRAFT_STAGING && (f->Mission == MISSION_GUARD || f->Mission == MISSION_GUARD_AREA)) {
        return (true);
    }
    if (draft >= TF_DRAFT_DOOMED && (f->Mission == MISSION_HUNT || f->Mission == MISSION_MOVE)) {
        return (true);
    }
    return (false);
}

/*
**	Pulls a drafted unit out of its team and parks it so it stands by for
**	boarding instead of resuming the doomed land order it was conscripted from.
*/
static void TF_Ferry_Draft(FootClass* f)
{
    if (f->Team.Is_Valid()) {
        f->Team->Remove(f);
    }
    if (f->Mission != MISSION_GUARD) {
        f->Assign_Mission(MISSION_GUARD);
        f->Assign_Destination(TARGET_NONE);
        f->Assign_Target(TARGET_NONE);
    }
}

// The ground zone a house's army stands on. Center often falls on water or under a building, where there is
// no ground zone, so this searches up to six cells outward for the nearest cell that has one.
static int TF_House_Landmass(COORDINATE center)
{
    CELL c = Coord_Cell(center);
    if (c <= 0) {
        return (0);
    }
    int z = Map[c].Zones[MZONE_NORMAL];
    if (z > 0) {
        return (z);
    }
    for (int r = 1; r <= 6; r++) {
        for (int dy = -r; dy <= r; dy++) {
            for (int dx = -r; dx <= r; dx++) {
                if (ABS(dx) != r && ABS(dy) != r) {
                    continue;
                }
                CELL c2 = XY_Cell(Cell_X(c) + dx, Cell_Y(c) + dy);
                if (Map.In_Radar(c2)) {
                    z = Map[c2].Zones[MZONE_NORMAL];
                    if (z > 0) {
                        return (z);
                    }
                }
            }
        }
    }
    return (0);
}

// The water cell of wzone touching landzone nearest to nearto, skipping cells near avoid. Given a house,
// coast in range of its discovered armed enemy buildings scores worse, so landings seek weak beaches.
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

// True for every MCV hull of every lineage.
static bool TF_Is_MCV(UnitClass const* u)
{
    return (*u == UNIT_MCV || *u == UNIT_TDMCV || *u == UNIT_AMCV || *u == UNIT_SMCV || *u == UNIT_TDGMCV
            || *u == UNIT_TDNMCV || *u == UNIT_TSMCV);
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

// Sends up to TF_FERRY_ESCORTS idle armed vessels on the landing's water ahead to the beach to engage its
// defences. The naval dispatcher in Expert_AI takes them back once idle, so no state is kept.
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

// True when the designated enemy's base stands on another ground landmass, so no land wave can reach it.
// Writes that landmass's zone to enemyland when given.
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

// Whether to run amphibious ops and which landmass to invade: always when the enemy is across water, and on
// a shared landmass (our own) only at Hard, against a discovered coastal enemy with a surplus idle army.
bool HouseClass::TF_Ferry_Assault(int& targetland, bool& second_front) const
{
    assert(Houses.ID(this) == ID);

    targetland = 0;
    second_front = false;
    if (Session.Type == GAME_NORMAL) {
        return (false);
    }
    if (TF_Ferry_Route_Blocked(&targetland)) {
        return (true);
    }
    if (IQ < Rule.MaxIQ) {
        return (false);
    }
    HouseClass const* ehp = (Enemy != HOUSE_NONE) ? HouseClass::As_Pointer(Enemy) : NULL;
    if (ehp == NULL || !ehp->IsActive || ehp->IsDefeated) {
        return (false);
    }
    CELL myc = Coord_Cell(Center);
    if (myc <= 0) {
        return (false);
    }
    int ourland = TF_House_Landmass(Center);
    if (ourland <= 0) {
        return (false);
    }
    int azone = 0;
    int asize = 0;
    bool acoastal = false;
    if (!TF_Naval_Assessment(azone, asize, acoastal) || !acoastal) {
        return (false);
    }
    int waiting = 0;
    for (int heap = 0; heap < 2; heap++) {
        int count = heap ? Infantry.Count() : Units.Count();
        for (int index = 0; index < count; index++) {
            FootClass const* f = heap ? (FootClass const*)Infantry.Ptr(index) : (FootClass const*)Units.Ptr(index);
            if (TF_Ferry_Eligible(f, this, ourland, TF_DRAFT_STAGING)) {
                waiting++;
            }
        }
    }
    if (waiting < TF_FERRY_SECOND_FRONT_MIN) {
        return (false);
    }
    targetland = ourland;
    second_front = true;
    return (true);
}

// True when AI_Vessel should queue a transport: an amphibious op is wanted and the house has fewer than one
// hull per full load of waiting passengers, capped at TF_FERRY_OPS_MAX.
bool HouseClass::TF_Ferry_Wants_Transport(void) const
{
    assert(Houses.ID(this) == ID);

    int tland = 0;
    bool sfront = false;
    if (!TF_Ferry_Assault(tland, sfront)) {
        return (false);
    }
    CELL myc = Coord_Cell(Center);
    if (myc <= 0) {
        return (false);
    }
    int ourland = TF_House_Landmass(Center);
    int waiting = 0;
    for (int heap = 0; heap < 2; heap++) {
        int count = heap ? Infantry.Count() : Units.Count();
        for (int index = 0; index < count; index++) {
            FootClass const* f = heap ? (FootClass const*)Infantry.Ptr(index) : (FootClass const*)Units.Ptr(index);
            if (TF_Ferry_Eligible(f, this, ourland, sfront ? TF_DRAFT_STAGING : TF_DRAFT_DOOMED)) {
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

// The first faction MCV this house can build, or UNIT_NONE (no war factory or tech yet).
UnitType HouseClass::TF_Ferry_MCV_Type(void) const
{
    assert(Houses.ID(this) == ID);

    static UnitType const _mcvs[] = {UNIT_AMCV, UNIT_SMCV, UNIT_TDGMCV, UNIT_TDNMCV, UNIT_TSMCV};
    for (int i = 0; i < (int)ARRAY_SIZE(_mcvs); i++) {
        if (Can_Build(&UnitTypeClass::As_Reference(_mcvs[i]), ActLike)) {
            return (_mcvs[i]);
        }
    }
    return (UNIT_NONE);
}

// True when AI_Unit should queue an expansion MCV: a load has landed, the house has no MCV (one aboard
// counts) and no yard at the target. The next ferry carries it and the beach sweep deploys it at the rally.
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
    int targetland = 0;
    bool second_front = false;
    if (!TF_Ferry_Assault(targetland, second_front)) {
        return (false);
    }
    for (int index = 0; index < Units.Count(); index++) {
        UnitClass const* u = Units.Ptr(index);
        if (u != NULL && (HouseClass const*)u->House == this && u->Strength > 0 && TF_Is_MCV(u)) {
            return (false);
        }
    }
    for (int index = 0; index < Buildings.Count(); index++) {
        BuildingClass const* b = Buildings.Ptr(index);
        if (b != NULL && !b->IsInLimbo && (HouseClass const*)b->House == this && b->Strength > 0) {
            if (b->Class->Is_Construction_Yard()) {
                if (second_front) {
                    if (::Distance(b->Center_Coord(), Cell_Coord(_tf_beach_rally[hidx]))
                        <= TF_FERRY_BEACH_RADIUS * CELL_LEPTON_W) {
                        return (false);
                    }
                } else if (Map[Coord_Cell(b->Center_Coord())].Zones[MZONE_NORMAL] == targetland) {
                    return (false);
                }
            }
        }
    }
    return (TF_Ferry_MCV_Type() != UNIT_NONE);
}

// Runs the house's ferry convoy each Expert_AI pass: rosters, boarding one unit per pass as TMission_Load
// does, sailing and unloading, then masses landed units at the beachhead and releases them as one wave.
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

    CELL myc = Coord_Cell(Center);
    int ourland = TF_House_Landmass(Center);
    int enemyland = 0;
    bool second_front = false;
    bool assault = TF_Ferry_Assault(enemyland, second_front);
    CELL rally = _tf_beach_rally[hidx];
    if (myc > 0 && ourland > 0 && enemyland > 0) {
        int beach = 0;
        for (int heap = 0; heap < 2; heap++) {
            int count = heap ? Infantry.Count() : Units.Count();
            for (int index = 0; index < count; index++) {
                FootClass const* f = heap ? (FootClass const*)Infantry.Ptr(index) : (FootClass const*)Units.Ptr(index);
                if (f == NULL || (HouseClass const*)f->House != this || f->IsInLimbo || f->Strength == 0
                    || !f->Is_Weapon_Equipped()) {
                    continue;
                }
                if (second_front) {
                    if (rally == 0
                        || ::Distance(f->Center_Coord(), Cell_Coord(rally)) > TF_FERRY_BEACH_RADIUS * CELL_LEPTON_W) {
                        continue;
                    }
                } else if (Map[Coord_Cell(f->Center_Coord())].Zones[MZONE_NORMAL] != enemyland) {
                    continue;
                }
                beach++;
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
        for (int heap = 0; heap < 2; heap++) {
            int count = heap ? Infantry.Count() : Units.Count();
            for (int index = 0; index < count; index++) {
                FootClass* f = heap ? (FootClass*)Infantry.Ptr(index) : (FootClass*)Units.Ptr(index);
                if (f == NULL || (HouseClass*)f->House != this || f->IsInLimbo || f->Strength == 0
                    || f->Team.Is_Valid()) {
                    continue;
                }
                if (second_front) {
                    if (rally == 0
                        || ::Distance(f->Center_Coord(), Cell_Coord(rally)) > TF_FERRY_BEACH_RADIUS * CELL_LEPTON_W) {
                        continue;
                    }
                } else if (Map[Coord_Cell(f->Center_Coord())].Zones[MZONE_NORMAL] != enemyland) {
                    continue;
                }
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

    for (int oi = 0; oi < TF_FERRY_OPS_MAX; oi++) {
        TFFerryOpStruct& op = _tf_ferry[hidx][oi];

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
            if (!assault || ourland <= 0) {
#if TF_DEV_BUILD // TF_AI_DIAG -- only interesting when a transport exists to strand.
                for (int index = 0; index < Vessels.Count(); index++) {
                    VesselClass const* v = Vessels.Ptr(index);
                    if (v != NULL && (HouseClass const*)v->House == this && !v->IsInLimbo
                        && *v == VESSEL_TRANSPORT && v->Strength > 0) {
                        TF_Ferry_Wait_Diag(this, "no-assault", assault ? 1 : 0, ourland);
                        break;
                    }
                }
#endif
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
#if TF_DEV_BUILD // TF_AI_DIAG
                TF_Ferry_Wait_Diag(this, "no-idle-lst", 0, 0);
#endif
                break;
            }
            CELL pick = TF_Ferry_Shore_Cell(pzone, ourland, Center, 0, NULL);
            CELL land = 0;
            for (int o2 = 0; o2 < TF_FERRY_OPS_MAX; o2++) {
                TFFerryOpStruct const& other = _tf_ferry[hidx][o2];
                if (o2 != oi && other.State != TFF_IDLE && other.Landing != 0) {
                    land = other.Landing;
                    break;
                }
            }
            if (land == 0) {
                COORDINATE lnear = Center;
                if (second_front) {
                    HouseClass const* ehp = HouseClass::As_Pointer(Enemy);
                    if (ehp != NULL && ehp->IsActive) {
                        lnear = ehp->Center;
                    }
                }
                land = TF_Ferry_Shore_Cell(pzone, enemyland, lnear, 0, this);
            }
            if (pick == 0 || land == 0) {
#if TF_DEV_BUILD // TF_AI_DIAG
                TF_Ferry_Wait_Diag(this, "no-shore", (int)pick, (int)land);
#endif
                break;
            }
            op.RosterCount = 0;
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
            {
                CELL stage = 0;
                for (FacingType face = FACING_N; face < FACING_COUNT; face++) {
                    CELL adj = Adjacent_Cell(pick, face);
                    if (Map.In_Radar(adj) && Map[adj].Zones[MZONE_NORMAL] == ourland) {
                        stage = adj;
                        break;
                    }
                }
                FootClass* cand[48];
                int ncand = 0;
                for (int heap = 0; heap < 2 && ncand < 48; heap++) {
                    int count = heap ? Infantry.Count() : Units.Count();
                    for (int index = 0; index < count && ncand < 48; index++) {
                        FootClass* f = heap ? (FootClass*)Infantry.Ptr(index) : (FootClass*)Units.Ptr(index);
                        if (TF_Ferry_Eligible(f, this, ourland, second_front ? TF_DRAFT_STAGING : TF_DRAFT_DOOMED)
                            && !TF_Ferry_Claimed(hidx, oi, f->As_Target())) {
                            cand[ncand++] = f;
                        }
                    }
                }
                while (op.RosterCount < TF_FERRY_ROSTER_MAX && ncand > 0) {
                    int best = 0;
                    for (int i = 1; i < ncand; i++) {
                        if (cand[i]->Distance(Cell_Coord(pick)) < cand[best]->Distance(Cell_Coord(pick))) {
                            best = i;
                        }
                    }
                    TF_Ferry_Draft(cand[best]);
                    if (stage != 0) {
                        cand[best]->Assign_Mission(MISSION_MOVE);
                        cand[best]->Assign_Destination(::As_Target(stage));
                    }
                    op.Roster[op.RosterCount++] = cand[best]->As_Target();
                    cand[best] = cand[--ncand];
                }
            }
            if (op.RosterCount < TF_FERRY_MIN_LOAD) {
#if TF_DEV_BUILD // TF_AI_DIAG
                TF_Ferry_Wait_Diag(this, "roster", op.RosterCount, TF_FERRY_MIN_LOAD);
#endif
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
            if (trans->Distance(Cell_Coord(op.Pickup)) <= 2 * CELL_LEPTON_W) {
                op.State = TFF_LOAD;
                op.Since = (int)Frame;
                op.StallFrame = 0;
            } else if (trans->Mission == MISSION_GUARD || (!trans->IsDriving && trans->Mission == MISSION_MOVE)) {
                if (op.StallFrame == 0) {
                    op.StallFrame = (int)Frame;
                } else if ((int)Frame - op.StallFrame > 60) {
                    trans->Assign_Mission(MISSION_MOVE);
                    trans->Assign_Destination(::As_Target(op.Pickup));
                    op.StallFrame = 0;
#if TF_DEV_BUILD // TF_AI_DIAG
                    {
                        FILE* _tfdbg = TF_AI_Diag_File();
                        if (_tfdbg != NULL) {
                            fprintf(_tfdbg, "F%ld H%d AL%d FERRY-REPATH pickup dist=%d\n", (long)Frame,
                                    (int)Class->House, (int)ActLike,
                                    trans->Distance(Cell_Coord(op.Pickup)) / CELL_LEPTON_W);
                            fflush(_tfdbg);
                        }
                    }
#endif
                }
            } else {
                op.StallFrame = 0;
            }
            if ((int)Frame - op.Since > TF_FERRY_TIMEOUT) {
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
                int stalldist = trans->Distance(Cell_Coord(op.Pickup)) / CELL_LEPTON_W;
                op = TFFerryOpStruct();
#if TF_DEV_BUILD // TF_AI_DIAG -- aboard/outside/dist tell WHICH half failed: hull never
                 // reached the shore (dist high) or troops never reached the hull.
                {
                    FILE* _tfdbg = TF_AI_Diag_File();
                    if (_tfdbg != NULL) {
                        fprintf(_tfdbg, "F%ld H%d AL%d FERRY-ABORT load-stall aboard=%d outside=%d dist=%d\n",
                                (long)Frame, (int)Class->House, (int)ActLike, aboard, outside, stalldist);
                        fflush(_tfdbg);
                    }
                }
#endif
            }
            break;
        }

        case TFF_SAIL:
            // Unload only on arrival: MISSION_UNLOAD drops cargo onto cells next to the hull and does nothing
            // when none is beach, so a transport switched early parks offshore forever with its cargo.
            if (trans->Distance(Cell_Coord(op.Landing)) <= 1 * CELL_LEPTON_W || trans->Mission == MISSION_GUARD) {
                trans->Assign_Mission(MISSION_UNLOAD);
                op.State = TFF_UNLOAD;
                op.Since = (int)Frame;
                op.BestDist = 0;
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
            } else {
                if (!trans->IsDriving && trans->Mission == MISSION_MOVE) {
                    if (op.StallFrame == 0) {
                        op.StallFrame = (int)Frame;
                    } else if ((int)Frame - op.StallFrame > 60) {
                        trans->Assign_Mission(MISSION_MOVE);
                        trans->Assign_Destination(::As_Target(op.Landing));
                        op.StallFrame = 0;
#if TF_DEV_BUILD // TF_AI_DIAG
                        {
                            FILE* _tfdbg = TF_AI_Diag_File();
                            if (_tfdbg != NULL) {
                                fprintf(_tfdbg, "F%ld H%d AL%d FERRY-REPATH parked dist=%d\n", (long)Frame,
                                        (int)Class->House, (int)ActLike,
                                        trans->Distance(Cell_Coord(op.Landing)) / CELL_LEPTON_W);
                                fflush(_tfdbg);
                            }
                        }
#endif
                        break;
                    }
                } else {
                    op.StallFrame = 0;
                }
                int d = trans->Distance(Cell_Coord(op.Landing));
                if (op.BestDist == 0 || d < op.BestDist) {
                    op.BestDist = d;
                    op.BestFrame = (int)Frame;
                } else if ((int)Frame - op.BestFrame > TF_FERRY_SAIL_REPATH) {
                    trans->Assign_Mission(MISSION_MOVE);
                    trans->Assign_Destination(::As_Target(op.Landing));
                    op.BestFrame = (int)Frame;
#if TF_DEV_BUILD // TF_AI_DIAG
                    {
                        FILE* _tfdbg = TF_AI_Diag_File();
                        if (_tfdbg != NULL) {
                            fprintf(_tfdbg, "F%ld H%d AL%d FERRY-REPATH dist=%d\n", (long)Frame, (int)Class->House,
                                    (int)ActLike, d / CELL_LEPTON_W);
                            fflush(_tfdbg);
                        }
                    }
#endif
                }
                if ((int)Frame - op.Since > TF_FERRY_SAIL_TIMEOUT) {
                    trans->Assign_Mission(MISSION_MOVE);
                    trans->Assign_Destination(::As_Target(op.Landing));
                    op.Since = (int)Frame;
                }
            }
            break;

        case TFF_UNLOAD:
            if (trans->How_Many() == 0 && trans->Mission != MISSION_UNLOAD) {
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
        // TF: the economy gate that radar, the repair bay, GDI/Nod tech, air and naval builds wait for: two
        // refineries and a war factory. A tiberium-short map counts as ready, as no more refineries are built there.
        unsigned tf_weapqty = TF_Role_Quantity(BQuantity, STRUCT_WEAP);
        bool tf_economy_ready = ((tf_refqty >= 2 || IsTiberiumShort) && tf_weapqty >= 1);
        // TF: harvesters are counted through the Units heap. UQuantity can't count TD or TS harvesters: types
        // past UNIT_RA_COUNT fold onto vanilla slots, and UQuantity has only UNIT_RA_COUNT - 3 entries.
        int tf_harv_count = 0;
        for (int hindex = 0; hindex < Units.Count(); hindex++) {
            UnitClass const* hu = Units.Ptr(hindex);
            if (hu != NULL && (HouseClass*)hu->House == this
                && (*hu == UNIT_TDHARV || *hu == UNIT_HARVESTER || *hu == UNIT_TSHARV)) {
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

        // TF: the air-structure cap follows the strongest single non-allied opponent, humans included, not just
        // Enemy. The maximum, not a sum, so the house can draw level with it.
        int enemy_airstrips = 0;
        int enemy_helipads = 0;
        for (HousesType eh = HOUSE_FIRST; eh < HOUSE_COUNT; eh++) {
            HouseClass const* ehp = HouseClass::As_Pointer(eh);
            if (ehp != NULL && ehp->IsActive && !ehp->IsDefeated && !Is_Ally(ehp)) {
                int afld = ehp->BQuantity[STRUCT_AIRSTRIP] + ehp->BQuantity[STRUCT_TDGAFLD];
                int hpad = ehp->BQuantity[STRUCT_HELIPAD] + ehp->BQuantity[STRUCT_TDHPAD]
                           + ehp->BQuantity[STRUCT_AHPAD] + ehp->BQuantity[STRUCT_SHPAD]
                           + ehp->BQuantity[STRUCT_TDGHPAD] + ehp->BQuantity[STRUCT_TDNHPAD]
                           + ehp->BQuantity[STRUCT_TSHPAD];
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
        if (Can_Build(b, ActLike) && TF_AI_Plug_Fits(this, b) && Power <= Drain + Rule.PowerSurplus && (b->Cost_Of() < money || hasincome)) {
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
        // TF: the refinery target is the larger of the ratio rule and the match-time pace, and a house below the
        // pace asks at HIGH.
        unsigned int current = tf_refqty;
        unsigned tf_refwant = Round_Up(Rule.RefineryRatio * fixed(CurBuildings));
        unsigned tf_reftime = (unsigned)TF_Eco_Refinery_Target();
        if (tf_reftime > tf_refwant) {
            tf_refwant = tf_reftime;
        }
        if (!IsTiberiumShort && current < tf_refwant && current < (unsigned)Rule.RefineryLimit) {
            b = TF_Skirmish_Pick(STRUCT_REFINERY, ActLike);
            if (Can_Build(b, ActLike) && (money > b->Cost_Of() || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(
                        (tf_refqty == 0 || current < tf_reftime) ? URGENCY_HIGH : URGENCY_MEDIUM, b->Type);
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

        // TF: Nod builds one Stealth Generator in its own slot, as the gap generator slot above is Allied.
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

        // TF: every faction builds radar once the economy gate passes. It gates GDI/Nod tech and RA air, and the
        // air-defence branch below asks for it only once an enemy flies.
        {
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
        }

        {
            // TF: every faction builds a service depot once the economy gate passes. It gates the GDI Mammoth (TDFIX)
            // and the RA MCV (FIX), so GDI asks at HIGH.
            current = TF_Role_Quantity(BQuantity, STRUCT_REPAIR);
            if (current < 1 && tf_economy_ready && Power_Fraction() >= 1) {
                b = TF_Skirmish_Pick(STRUCT_REPAIR, ActLike);
                if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                    choiceptr = BuildChoice.Alloc();
                    if (choiceptr != NULL) {
                        *choiceptr = BuildChoiceClass(ActLike == HOUSE_GOOD ? URGENCY_HIGH : URGENCY_MEDIUM, b->Type);
                    }
                }
            }
        }

        /*
        **	Always build up some base defense.
        */
        // TF: the ratio counts the base without its defences, a base under half its wanted defence asks at HIGH,
        // and Nod alternates its Turret and Flame Bunker.
        int tf_def = TF_Skirmish_Type(STRUCT_FLAME_TURRET, ActLike);
        current = BQuantity[STRUCT_PILLBOX] + BQuantity[STRUCT_CAMOPILLBOX] + BQuantity[STRUCT_TURRET]
                  + BQuantity[STRUCT_FLAME_TURRET] + BQuantity[STRUCT_TDFBNK] + (tf_def >= 0 ? BQuantity[tf_def] : 0);
        unsigned tf_defbase = (CurBuildings > current) ? (CurBuildings - current) : 0;
        unsigned tf_defwant = Round_Up(Rule.DefenseRatio * fixed(tf_defbase));
        if (current < tf_defwant && current < (unsigned)Rule.DefenseLimit) {
            UrgencyType tf_defurg = (current * 2 < tf_defwant) ? URGENCY_HIGH : URGENCY_MEDIUM;
            b = NULL;
            if (ActLike == HOUSE_BAD && tf_def >= 0
                && (unsigned)BQuantity[STRUCT_TDFBNK] < (unsigned)BQuantity[tf_def]) {
                BuildingTypeClass const* fb = &BuildingTypeClass::As_Reference(STRUCT_TDFBNK);
                if (Can_Build(fb, ActLike)) {
                    b = fb;
                }
            }
            if (b == NULL) {
                b = TF_AI_Tower_Step(this, TF_Skirmish_Pick(STRUCT_FLAME_TURRET, ActLike));
            }
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(tf_defurg, b->Type);
                }
            } else {
                if (Percent_Chance(50)) {
                    b = &BuildingTypeClass::As_Reference(STRUCT_PILLBOX);
                    if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                        choiceptr = BuildChoice.Alloc();
                        if (choiceptr != NULL) {
                            *choiceptr = BuildChoiceClass(tf_defurg, b->Type);
                        }
                    }
                } else {
                    b = &BuildingTypeClass::As_Reference(STRUCT_TURRET);
                    if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                        choiceptr = BuildChoice.Alloc();
                        if (choiceptr != NULL) {
                            *choiceptr = BuildChoiceClass(tf_defurg, b->Type);
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

                b = TF_AI_Tower_Step(this, TF_Skirmish_Pick(STRUCT_SAM, ActLike));
                if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                    choiceptr = BuildChoice.Alloc();
                    if (choiceptr != NULL) {
                        *choiceptr = BuildChoiceClass(
                            (current < (unsigned)threat_quantity) ? URGENCY_HIGH : URGENCY_MEDIUM, b->Type);
                    }
                } else {
                    b = TF_AI_Tower_Step(this, TF_Skirmish_Pick(STRUCT_AAGUN, ActLike));
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
            b = TF_AI_Tower_Step(this, TF_Skirmish_Pick(STRUCT_TESLA, ActLike));
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome) && Power_Fraction() >= 1) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                }
            }
        }

        /*
        **	Build a tech center as soon as possible.
        */
        // TF: counts and picks the faction's own tech centre. GDI and Nod also wait for the economy gate.
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
                    // TF: LOW until the economy gate passes, then MEDIUM. Power, refinery and defence always offer a
                    // MEDIUM candidate, so a permanent LOW would never win and the house would field no aircraft.
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
                    // TF: the same escalation as the helipad above.
                    *choiceptr = BuildChoiceClass(tf_economy_ready ? URGENCY_MEDIUM : URGENCY_LOW, b->Type);
                }
            }
        }

        // TF: the dropship bay delivers the Mammoth Mk. II and the Mech Division. BQuantity counts a bay from
        // production start, so a second is never queued while the first is on the yard's line.
        if (BQuantity[STRUCT_TSDROP] == 0) {
            b = &BuildingTypeClass::As_Reference(STRUCT_TSDROP);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(tf_economy_ready ? URGENCY_MEDIUM : URGENCY_LOW, b->Type);
                }
            }
        }

        // TF: with superweapon IQ, the TS Upgrade Centre once, then one plug at a time from TF_AI_Upgrade_Plug.
        // A plug queued before its centre stands fails Can_Build and waits a pass.
        if (IQ >= Rule.IQSuperWeapons) {
            if (BQuantity[STRUCT_TSPLUG] == 0) {
                b = &BuildingTypeClass::As_Reference(STRUCT_TSPLUG);
            } else {
                StructType plug = TF_AI_Upgrade_Plug(this);
                b = (plug != STRUCT_NONE) ? &BuildingTypeClass::As_Reference(plug) : NULL;
            }
            if (b != NULL && Can_Build(b, ActLike) && TF_AI_Plug_Fits(this, b) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(tf_economy_ready ? URGENCY_MEDIUM : URGENCY_LOW, b->Type);
                }
            }
        }

        // TF: a naval yard once the economy gate passes and the water evaluation says a navy matters here. Not
        // gated on discovery: on a water-split map the patrol it enables is how the enemy gets found.
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
        **	Pick the choice that is the most urgent.
        */
        // TF: ties go to the earliest candidate, as scan order is the intended build order. A candidate that has
        // waited STARVE_FRAMES since it first lost a tie jumps the queue once, so nothing starves.
        enum
        {
            STARVE_FRAMES = 7500
        };
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
                if (track && s >= 0 && s < STRUCT_COUNT && _tf_waiting_since[hidx][s] > 0) {
                    int waited = (int)Frame - _tf_waiting_since[hidx][s];
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
                        _tf_waiting_since[hidx][s] = 0; // built, stop the clock
                    } else if (_tf_waiting_since[hidx][s] == 0) {
                        _tf_waiting_since[hidx][s] = (int)Frame; // start the clock
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
/*
**	Garrison kept while the economy holds combat production: enough to see off a
**	scout and hold the bunkers, not an army.
*/
enum
{
    TF_ECO_GARRISON_VEHICLES = 2,
    TF_ECO_GARRISON_INFANTRY = 4
};
// The garrison grows with the match: one more soldier a minute, one more vehicle every two minutes.
static int TF_Eco_Garrison_Infantry(void)
{
    return (TF_ECO_GARRISON_INFANTRY + (int)(Frame / TICKS_PER_MINUTE));
}
static int TF_Eco_Garrison_Vehicles(void)
{
    return (TF_ECO_GARRISON_VEHICLES + (int)(Frame / (TICKS_PER_MINUTE * 2)));
}

/*
**	Diagnostic: one ECO-HOLD line per house per ~minute while production yields to
**	the economy, naming the targets it is waiting on.
*/
static void TF_Eco_Hold_Diag(HouseClass const* house, char const* what)
{
#if TF_DEV_BUILD // TF_AI_DIAG
    extern FILE* TF_AI_Diag_File(void);
    static long _last[HOUSE_COUNT] = {0};
    int hidx = (int)house->Class->House;
    if (hidx < 0 || hidx >= HOUSE_COUNT || (long)Frame - _last[hidx] < TICKS_PER_MINUTE) {
        return;
    }
    _last[hidx] = (long)Frame;
    int refwant = 0;
    int harvwant = 0;
    int refhave = 0;
    house->TF_Eco_Below_Target(&refwant, &harvwant, &refhave);
    FILE* _tfdbg = TF_AI_Diag_File();
    if (_tfdbg != NULL) {
        fprintf(_tfdbg,
                "F%ld H%d AL%d ECO-HOLD %s ref=%d/%d harv=%d/%d $%d\n",
                (long)Frame,
                (int)house->Class->House,
                (int)house->ActLike,
                what,
                refhave,
                refwant,
                house->TF_Harvesters_Owned(),
                harvwant,
                house->Available_Money());
        fflush(_tfdbg);
    }
#else
    (void)house;
    (void)what;
#endif
}

int HouseClass::AI_Unit(void)
{
    assert(Houses.ID(this) == ID);

    // TF: a dropship delivery with no bay, or one the bay would refuse, is dropped: every unit factory declines
    // it, so unit production would stall behind it.
    if (BuildUnit != UNIT_NONE && TF_Is_Dropship_Delivered(&UnitTypeClass::As_Reference(BuildUnit))
        && (!Has_Building_Active(STRUCT_TSDROP) || TF_Delivery_Order_Refused(this, RTTI_UNITTYPE, BuildUnit))) {
        BuildUnit = UNIT_NONE;
    }

    if (BuildUnit != UNIT_NONE)
        return (TICKS_PER_SECOND);
    if (CurUnits >= Control.MaxUnit)
        return (TICKS_PER_SECOND);

    /*
    **	A computer controlled house will try to build a replacement
    **	harvester if possible.
    */
    // TF: builds the faction's own harvester up to the tier's fleet target, counted through the Units heap
    // (TF_Harvesters_Owned): UQuantity folds types past UNIT_RA_COUNT onto vanilla slots, so can't count them.
    int tf_proc_t = TF_Skirmish_Type(STRUCT_REFINERY, ActLike);
    unsigned tf_refq = BQuantity[STRUCT_REFINERY] + (tf_proc_t >= 0 ? BQuantity[tf_proc_t] : 0);
    UnitType tf_harv = Is_TS_GDI(ActLike) ? UNIT_TSHARV : ((tf_proc_t >= 0) ? UNIT_TDHARV : UNIT_HARVESTER);
    int tf_harv_owned = TF_Harvesters_Owned();
    if (IQ >= Rule.IQHarvester && !IsTiberiumShort && !IsHuman && TF_Eco_Harvester_Target((int)tf_refq) > tf_harv_owned
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

        // TF: economy first. Past the garrison, combat vehicles wait while the house is below its refinery or
        // harvester target.
        if (Session.Type != GAME_NORMAL && CurUnits - tf_harv_owned >= TF_Eco_Garrison_Vehicles()
            && TF_Eco_Below_Target()) {
            TF_Eco_Hold_Diag(this, "vehicle");
            return (TICKS_PER_SECOND * 2);
        }

        // TF: a holding beachhead gets an expansion MCV ahead of the combat pick; the ferry carries it first.
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
            // TF: harvesters and the units the AI cannot use (Mobile EM-Pulse, Sensor Array, War Factory, Limpet
            // Drone) stay out of the combat pick. Dropship deliveries weigh as armed: the Mech Division lands mechs.
            if (Can_Build(utype, ActLike) && utype->Type != UNIT_HARVESTER
                && utype->Type != UNIT_TDHARV && utype->Type != UNIT_TSHARV && utype->Type != UNIT_TSMEMP
                && utype->Type != UNIT_TSLPST && utype->Type != UNIT_TSMWAR && utype->Type != UNIT_TSLIMP
                && !TF_Delivery_Order_Refused(this, RTTI_UNITTYPE, utype->Type)) {
                if (utype->PrimaryWeapon != NULL || TF_Is_Dropship_Delivered(utype)) {
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

        // TF: once the water evaluation passes, skirmish builds the ferry's transport when it asks for one, else a
        // random armed vessel while armed hulls, transports never counted, are under TF_Naval_Fleet_Cap.
        if (Session.Type != GAME_NORMAL && TF_Role_Quantity(BQuantity, STRUCT_SHIP_YARD) > 0) {
            int tzone = 0;
            int tsize = 0;
            bool tcoastal = false;
            int tenavy = 0;
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
            } else if (tok) {
                int armedv = 0;
                for (int avi = 0; avi < Vessels.Count(); avi++) {
                    VesselClass const* av = Vessels.Ptr(avi);
                    if (av != NULL && !av->IsInLimbo && (HouseClass const*)av->House == this && av->Strength > 0
                        && av->Is_Weapon_Equipped()) {
                        armedv++;
                    }
                }
                if (armedv >= TF_Naval_Fleet_Cap(tcoastal, &tenavy)) {
                    return (TICKS_PER_SECOND);
                }
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
        // TF: economy first, as in AI_Unit: past the garrison, infantry waits for the refinery and harvester
        // targets.
        if (Session.Type != GAME_NORMAL && CurInfantry >= TF_Eco_Garrison_Infantry() && TF_Eco_Below_Target()) {
            TF_Eco_Hold_Diag(this, "infantry");
            return (TICKS_PER_SECOND * 2);
        }

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

                    // TF: TD and TS infantry take the weight of their nearest RA analog. Count them with QuantityI():
                    // IQuantity[] is sized for RA infantry, so indexing it with these types reads past its end.
                    case INFANTRY_TDE1:
                    case INFANTRY_TSE1:
                        typetrack[count].Value = 3;
                        break;

                    case INFANTRY_TDE2:
                    case INFANTRY_TSE2:
                        typetrack[count].Value = 5;
                        break;

                    case INFANTRY_TDE3:
                    case INFANTRY_TSJUMPJET:
                        typetrack[count].Value = 2;
                        break;

                    case INFANTRY_TSMEDIC:
                        if (CurInfantry > 5) {
                            typetrack[count].Value = 2 - max(QuantityI(index), 0);
                        }
                        break;

                    case INFANTRY_TDE4:
                        typetrack[count].Value = 5;
                        break;

                    case INFANTRY_TDE5:
                        typetrack[count].Value = 5;
                        break;

                    case INFANTRY_TDE6:
                    case INFANTRY_TSENGINEER:
                        if (CurInfantry > 5) {
                            typetrack[count].Value = 1 - max(QuantityI(index), 0);
                        }
                        break;

                    case INFANTRY_TDRMBO:
                        typetrack[count].Value = 1 - max(QuantityI(index), 0);
                        break;

                    case INFANTRY_TSGHOST:
                        typetrack[count].Value = TF_Ghost_At_Cap(this) ? 0 : 1;
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

        // TF: GDI and Nod fly the Orca and Apache, TS GDI the Orca Fighter and Bomber (every third slot), and
        // GDI the A-10 from its airfield; one airframe per pad or airfield, as in the RA cases below.
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

        if (Can_Build(&AircraftTypeClass::As_Reference(AIRCRAFT_TSORCA), ActLike)
            && AircraftTypeClass::As_Reference(AIRCRAFT_TSORCA).Level <= (unsigned)Control.TechLevel
            && BQuantity[STRUCT_TSHPAD] > AQuantity[AIRCRAFT_TSORCA] + AQuantity[AIRCRAFT_TSORCAB]) {
            bool bomber = Can_Build(&AircraftTypeClass::As_Reference(AIRCRAFT_TSORCAB), ActLike)
                          && AircraftTypeClass::As_Reference(AIRCRAFT_TSORCAB).Level <= (unsigned)Control.TechLevel
                          && (AQuantity[AIRCRAFT_TSORCA] + AQuantity[AIRCRAFT_TSORCAB]) % 3 == 2;
            BuildAircraft = bomber ? AIRCRAFT_TSORCAB : AIRCRAFT_TSORCA;
            return (TICKS_PER_SECOND);
        }
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
        AScan |= TF_Type_Scan_Bit(aircraft); // TF: no bit past 31
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
            IScan |= TF_Type_Scan_Bit(infantry); // TF: no bit past 31
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
        UScan |= TF_Type_Scan_Bit(unit); // TF: no bit past 31
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
        VScan |= TF_Type_Scan_Bit(vessel); // TF: no bit past 31
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
int* HouseClass::Factory_Counter(RTTIType rtti, bool bay)
{
    switch (rtti) {
    case RTTI_UNITTYPE:
    case RTTI_UNIT:
        return (bay ? &DropFactories : &UnitFactories);

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
        int* fptr = Factory_Counter(((BuildingClass*)techno)->Class->ToBuild, *((BuildingClass*)techno) == STRUCT_TSDROP);
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
        int* fptr = Factory_Counter(((BuildingClass*)techno)->Class->ToBuild, *((BuildingClass*)techno) == STRUCT_TSDROP);
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
    // TF: scan bits through TF_Type_Scan_Bit, so a type past 31 sets none rather than another type's.
    for (index = 0; index < Units.Count(); index++) {
        UnitClass const* unit = Units.Ptr(index);
        unit->House->UScan |= TF_Type_Scan_Bit(unit->Class->Type);
        if (unit->IsLocked && (Session.Type != GAME_NORMAL || !unit->House->IsHuman || unit->IsDiscoveredByPlayer)) {
            if (!unit->IsInLimbo) {
                unit->House->ActiveUScan |= TF_Type_Scan_Bit(unit->Class->Type);
            }
        }
    }
    for (index = 0; index < Infantry.Count(); index++) {
        InfantryClass const* infantry = Infantry.Ptr(index);
        infantry->House->IScan |= TF_Type_Scan_Bit(infantry->Class->Type);
        if (infantry->IsLocked
            && (Session.Type != GAME_NORMAL || !infantry->House->IsHuman || infantry->IsDiscoveredByPlayer)) {
            if (!infantry->IsInLimbo) {
                infantry->House->ActiveIScan |= TF_Type_Scan_Bit(infantry->Class->Type);
                infantry->House->OldIScan |= TF_Type_Scan_Bit(infantry->Class->Type);
            }
        }
    }
    for (index = 0; index < Aircraft.Count(); index++) {
        AircraftClass const* aircraft = Aircraft.Ptr(index);
        aircraft->House->AScan |= TF_Type_Scan_Bit(aircraft->Class->Type);
        if (aircraft->IsLocked
            && (Session.Type != GAME_NORMAL || !aircraft->House->IsHuman || aircraft->IsDiscoveredByPlayer)) {
            if (!aircraft->IsInLimbo) {
                aircraft->House->ActiveAScan |= TF_Type_Scan_Bit(aircraft->Class->Type);
                aircraft->House->OldAScan |= TF_Type_Scan_Bit(aircraft->Class->Type);
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
        vessel->House->VScan |= TF_Type_Scan_Bit(vessel->Class->Type);
        if (vessel->IsLocked
            && (Session.Type != GAME_NORMAL || !vessel->House->IsHuman || vessel->IsDiscoveredByPlayer)) {
            if (!vessel->IsInLimbo) {
                vessel->House->ActiveVScan |= TF_Type_Scan_Bit(vessel->Class->Type);
                vessel->House->OldVScan |= TF_Type_Scan_Bit(vessel->Class->Type);
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

            if (*unit == UNIT_HARVESTER || *unit == UNIT_TDHARV || *unit == UNIT_TSHARV)
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
FactoryClass* HouseClass::Fetch_Factory(RTTIType rtti, bool bay) const
{
    int factory_index = -1;

    switch (rtti) {
    case RTTI_INFANTRY:
    case RTTI_INFANTRYTYPE:
        factory_index = InfantryFactory;
        break;

    case RTTI_UNIT:
    case RTTI_UNITTYPE:
        factory_index = bay ? DropFactory : UnitFactory;
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
void HouseClass::Set_Factory(RTTIType rtti, FactoryClass* factory, bool bay)
{
    int* factory_index = 0;

    assert(rtti != RTTI_NONE);

    switch (rtti) {
    case RTTI_UNIT:
    case RTTI_UNITTYPE:
        factory_index = bay ? &DropFactory : &UnitFactory;
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
int HouseClass::Factory_Count(RTTIType rtti, bool bay) const
{
    int const* ptr = ((HouseClass*)this)->Factory_Counter(rtti, bay);
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
        // TF: only cells in the requested zone, so a building lands in the zone the defence rating chose and each
        // pass of the any-zone fallback searches new ground.
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

// Returns the legal placement cell nearest the base centre for a water-bound building, preferring the water
// zone the naval assessment chose; pond cells never qualify. 0 when no cell does.
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

// Returns a random radar cell of water zone wzone, or 0. Every ship on that zone can reach it, so a patrol
// order never sends a ship at an unreachable cell.
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
            if (!b->Class->IsWall && *b != STRUCT_APMINE && *b != STRUCT_AVMINE && *b != STRUCT_TSDLIMP
                && *b != STRUCT_TSFSDF) {
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
