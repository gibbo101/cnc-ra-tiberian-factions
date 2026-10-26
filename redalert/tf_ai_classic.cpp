/*
**	Vanilla Red Alert's computer-player decisions for Classic AI and the switches that turn ours off
**	(docs/player-settings.md). Copied from EA's house.cpp, each RA building routed to the house's faction.
*/
#include "function.h"

/*
**	How many of these vanilla buildings the house has, its faction's equivalents counted with them once each.
*/
unsigned HouseClass::TF_Classic_Count(StructType a, StructType b, StructType c, StructType d) const
{
    StructType const roles[4] = {a, b, c, d};
    int seen[8];
    int nseen = 0;
    unsigned total = 0;
    for (StructType role : roles) {
        if (role == STRUCT_NONE) {
            continue;
        }
        int const types[2] = {(int)role, TF_Skirmish_Type(role, ActLike)};
        for (int type : types) {
            bool counted = type < 0;
            for (int s = 0; s < nseen && !counted; s++) {
                counted = seen[s] == type;
            }
            if (!counted) {
                seen[nseen++] = type;
                total += BQuantity[type];
            }
        }
    }
    return total;
}

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

/*
**	Vanilla's skirmish base builder: power, refinery, barracks, factory, defences, air defence, tech, air and
**	repair, each when short and affordable, picking the most urgent. Classic AI only.
*/
int HouseClass::TF_Classic_AI_Building(void)
{
    assert(Houses.ID(this) == ID);

    if (BuildStructure != STRUCT_NONE)
        return (TICKS_PER_SECOND);

    if (IsBaseBuilding) {
        BuildChoice.Free_All();
        BuildChoiceClass* choiceptr;
        int money = Available_Money();
        bool hasincome = (TF_Classic_Count(STRUCT_REFINERY) > 0 && !IsTiberiumShort && TF_Harvesters_Owned() > 0);
        BuildingTypeClass const* b = NULL;
        HouseClass const* enemy = NULL;
        if (Enemy != HOUSE_NONE) {
            enemy = HouseClass::As_Pointer(Enemy);
        }

        /*
        **	Try to build a power plant if there is insufficient power and there is enough
        **	money available.
        */
        b = TF_Skirmish_Pick(STRUCT_ADVANCED_POWER, ActLike);
        if (Can_Build(b, ActLike) && Power <= Drain + Rule.PowerSurplus && b->Cost_Of() < money) {
            choiceptr = BuildChoice.Alloc();
            if (choiceptr != NULL) {
                *choiceptr =
                    BuildChoiceClass(TF_Classic_Count(STRUCT_REFINERY) == 0 ? URGENCY_LOW : URGENCY_MEDIUM, b->Type);
            }
        } else {
            b = TF_Skirmish_Pick(STRUCT_POWER, ActLike);
            if (Can_Build(b, ActLike) && Power <= Drain + Rule.PowerSurplus && b->Cost_Of() < money) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr =
                        BuildChoiceClass(TF_Classic_Count(STRUCT_REFINERY) == 0 ? URGENCY_LOW : URGENCY_MEDIUM,
                                         b->Type);
                }
            }
        }

        /*
        **	Build a refinery if there isn't one already available.
        */
        unsigned int current = TF_Classic_Count(STRUCT_REFINERY);
        if (!IsTiberiumShort && current < Round_Up(Rule.RefineryRatio * fixed(CurBuildings))
            && current < (unsigned)Rule.RefineryLimit) {
            b = TF_Skirmish_Pick(STRUCT_REFINERY, ActLike);
            if (Can_Build(b, ActLike) && (money > b->Cost_Of() || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr =
                        BuildChoiceClass(TF_Classic_Count(STRUCT_REFINERY) == 0 ? URGENCY_HIGH : URGENCY_MEDIUM,
                                         b->Type);
                }
            }
        }

        /*
        **	Always make sure there is a barracks available, but only if there
        **	will be sufficient money to train troopers.
        */
        current = TF_Classic_Count(STRUCT_BARRACKS, STRUCT_TENT);
        if (current < Round_Up(Rule.BarracksRatio * fixed(CurBuildings)) && current < (unsigned)Rule.BarracksLimit
            && (money > 300 || hasincome)) {
            b = TF_Skirmish_Pick(STRUCT_BARRACKS, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(current > 0 ? URGENCY_LOW : URGENCY_MEDIUM, b->Type);
                }
            } else {
                b = TF_Skirmish_Pick(STRUCT_TENT, ActLike);
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
        current = TF_Classic_Count(STRUCT_KENNEL);
        if (current < 1 && (money > 300 || hasincome)) {
            b = TF_Skirmish_Pick(STRUCT_KENNEL, ActLike);
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
        current = TF_Classic_Count(STRUCT_GAP);
        if (current < 1 && Power_Fraction() >= 1 && hasincome) {
            b = TF_Skirmish_Pick(STRUCT_GAP, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                }
            }
        }

        /*
        **	A source of combat vehicles is always needed, but only if there will
        **	be sufficient money to build vehicles.
        */
        current = TF_Classic_Count(STRUCT_WEAP);
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
        **	Always build up some base defense.
        */
        current = TF_Classic_Count(STRUCT_PILLBOX, STRUCT_CAMOPILLBOX, STRUCT_TURRET, STRUCT_FLAME_TURRET);
        if (current < Round_Up(Rule.DefenseRatio * fixed(CurBuildings)) && current < (unsigned)Rule.DefenseLimit) {
            b = TF_Skirmish_Pick(STRUCT_FLAME_TURRET, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                }
            } else {
                if (Percent_Chance(50)) {
                    b = TF_Skirmish_Pick(STRUCT_PILLBOX, ActLike);
                    if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                        choiceptr = BuildChoice.Alloc();
                        if (choiceptr != NULL) {
                            *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                        }
                    }
                } else {
                    b = TF_Skirmish_Pick(STRUCT_TURRET, ActLike);
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
        current = TF_Classic_Count(STRUCT_SAM, STRUCT_AAGUN);
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

                if (TF_Classic_Count(STRUCT_RADAR) == 0) {
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
        current = TF_Classic_Count(STRUCT_TESLA);
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
        **	Build a tech center as soon as possible.
        */
        current = TF_Classic_Count(STRUCT_ADVANCED_TECH, STRUCT_SOVIET_TECH);
        if (current < 1) {
            b = TF_Skirmish_Pick(STRUCT_ADVANCED_TECH, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome) && Power_Fraction() >= 1) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    *choiceptr = BuildChoiceClass(URGENCY_MEDIUM, b->Type);
                }
            } else {
                b = TF_Skirmish_Pick(STRUCT_SOVIET_TECH, ActLike);
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
        current = TF_Classic_Count(STRUCT_HELIPAD);
        if (current < Round_Up(Rule.HelipadRatio * fixed(CurBuildings)) && current < (unsigned)Rule.HelipadLimit) {
            b = TF_Skirmish_Pick(STRUCT_HELIPAD, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    int threat_quantity = 0;
                    if (enemy != NULL) {
                        threat_quantity = enemy->CurAircraft;
                    }

                    *choiceptr = BuildChoiceClass(
                        (CurAircraft < (unsigned)threat_quantity) ? URGENCY_HIGH : URGENCY_MEDIUM, b->Type);
                }
            }
        }

        /*
        **	An airstrip would be good.
        */
        current = TF_Classic_Count(STRUCT_AIRSTRIP);
        if (current < Round_Up(Rule.AirstripRatio * fixed(CurBuildings)) && current < (unsigned)Rule.AirstripLimit) {
            b = TF_Skirmish_Pick(STRUCT_AIRSTRIP, ActLike);
            if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
                choiceptr = BuildChoice.Alloc();
                if (choiceptr != NULL) {
                    int threat_quantity = 0;
                    if (enemy != NULL) {
                        threat_quantity = enemy->CurAircraft;
                    }

                    *choiceptr = BuildChoiceClass(
                        (CurAircraft < (unsigned)threat_quantity) ? URGENCY_HIGH : URGENCY_MEDIUM, b->Type);
                }
            }
        }

        /*
        **	Pick the choice that is the most urgent.
        */
        UrgencyType best = URGENCY_NONE;
        int bestindex;
        for (int index = 0; index < BuildChoice.Count(); index++) {
            if (BuildChoice.Ptr(index)->Urgency > best) {
                bestindex = index;
                best = BuildChoice.Ptr(index)->Urgency;
            }
        }
        if (best != URGENCY_NONE) {
            BuildStructure = BuildChoice.Ptr(bestindex)->Structure;
        }
    }

    return (TICKS_PER_SECOND);
}
