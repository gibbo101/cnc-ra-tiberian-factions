/*
**	Vanilla Red Alert's computer-player decisions, kept for the player settings that turn ours off
**	(docs/player-settings.md). Copied from EA's house.cpp; only the names differ. License: GPL v3.
*/
#include "function.h"

/*
**	Vanilla's attack: a third of the time, sends each armed unit to hunt at three-in-four odds, and shuffles some
**	base guards; with no buildings left, sends everything. Picks the next attack time.
*/
bool HouseClass::TF_Classic_AI_Attack(void)
{
    assert(Houses.ID(this) == ID);

    bool shuffle = !((Frame > TICKS_PER_MINUTE && !CurBuildings) || Percent_Chance(33));
    bool forced = (CurBuildings == 0);
    int index;
    for (index = 0; index < Aircraft.Count(); index++) {
        AircraftClass* a = Aircraft.Ptr(index);

        if (a != NULL && !a->IsInLimbo && a->House == this && a->Strength > 0) {
            if (!shuffle && a->Is_Weapon_Equipped() && (forced || Percent_Chance(75))) {
                a->Assign_Mission(MISSION_HUNT);
            }
        }
    }
    for (index = 0; index < Units.Count(); index++) {
        UnitClass* u = Units.Ptr(index);

        if (u != NULL && !u->IsInLimbo && u->House == this && u->Strength > 0) {
            if (!shuffle && u->Is_Weapon_Equipped() && (forced || Percent_Chance(75))) {
                u->Assign_Mission(MISSION_HUNT);
            } else {

                /*
                **	If this unit is guarding the base, then cause it to shuffle
                **	location instead.
                */
                if (Percent_Chance(20) && u->Mission == MISSION_GUARD_AREA && Which_Zone(u) != ZONE_NONE) {
                    u->ArchiveTarget = ::As_Target(Where_To_Go(u));
                }
            }
        }
    }
    for (index = 0; index < Infantry.Count(); index++) {
        InfantryClass* i = Infantry.Ptr(index);

        if (i != NULL && !i->IsInLimbo && i->House == this && i->Strength > 0) {
            if (!shuffle && (i->Is_Weapon_Equipped() || *i == INFANTRY_RENOVATOR) && (forced || Percent_Chance(75))) {
                i->Assign_Mission(MISSION_HUNT);
            } else {

                /*
                **	If this soldier is guarding the base, then cause it to shuffle
                **	location instead.
                */
                if (Percent_Chance(20) && i->Mission == MISSION_GUARD_AREA && Which_Zone(i) != ZONE_NONE) {
                    i->ArchiveTarget = ::As_Target(Where_To_Go(i));
                }
            }
        }
    }
    Attack = Rule.AttackInterval * Random_Pick(TICKS_PER_MINUTE / 2, TICKS_PER_MINUTE * 2);
    return (true);
}
