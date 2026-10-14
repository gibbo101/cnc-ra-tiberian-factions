/*
**	Tiberian Sun's own effects for TS objects: death blasts and debris, damage smoke and sparks,
**	fires, infantry deaths and the burning soldier, after OpenTS. The art is packed by scripts/ts_pack_effects.py.
*/
#include "function.h"
#include "tf_asset_pack.h"
#include "tf_ts_effects.h"

#include <cmath>
#include <cstring>

namespace {

// OpenTS AnimClass::Unlimbo: a Bouncer anim falls at 1.4 leptons per tick per tick.
const double TS_ANIM_GRAVITY = 1.4;

// TS art.ini [DBRIS1LG] and [DBRIS1SM]: launch speeds in leptons per tick, and the burst.
struct ShardType
{
    double MaxXYVel;
    int MinZVel;
    int ZVelSpread;
    int Damage;
};
const ShardType LargeShard = {25.0, 25, 20, 20};
const ShardType SmallShard = {30.0, 20, 15, 10};

// TS MaxDebris for each TS object with metal debris, by its TS rules section (named in rules.ini).
struct DebrisCount
{
    char const* IniName;
    int MaxDebris;
};
const DebrisCount TSDebris[] = {
    {"TSJUGG", 4},     // [JUGG]
    {"TSMEMP", 6},     // [MOBILEMP]
    {"TSTITN", 4},     // [MMCH]
    {"TSSAPC", 4},     // [SAPC]
    {"TSSONIC", 5},    // [SONIC]
    {"TSTTNK", 4},     // [TTNK]
    {"TSTICK", 4},     // [GATICK]
    {"TSHMEC", 6},     // [HMEC]
    {"TSSMEC", 2},     // [SMECH]
    {"TSHVR", 4},      // [HVR]
    {"TSLPST", 3},     // [LPST]
    {"TSSUBTANK", 4},  // [SUBTANK]
    {"TSMWAR", 6},     // [MOBWARG]
    {"TSORCA", 4},     // [ORCA]
    {"TSORCAB", 4},    // [ORCAB]
    {"TSORCATRAN", 4}, // [ORCATRAN]
    {"TSCARRY", 4},    // [TRNSPORT]
    {"TSSILO", 2},     // [GASILO]
    {"TSRADR", 6},     // [GARADR]
    {"TSGATEH", 3},    // [GAGATE_A]
    {"TSGATEV", 2},    // [GAGATE_B]
    {"TSNGATEH", 2},   // [NAGATE_A]
    {"TSNGATEV", 2},   // [NAGATE_B]
    {"TSDPSA", 2},     // [GADPSA]
};

// The emitter ring sits at the bottom of its frame: drawn this far north, it lands on the section's centre.
const int FIRESTORM_RING_LIFT = 85;

// TS [SmallGreySSys] and [SmallGreySmoke]: a puff every SpawnFrames=5 ticks up to ParticleCap=15, which with its
// 20 states at 4-5 ticks each comes to one every 6. It rises at Velocity=9, slowing by Deacc=.05 to 3.
enum
{
    SMOKE_SPAWN_TICKS = 6,
    SMOKE_DRIFT_MAX = 5,
};
const double SMOKE_RISE = 9.0;
const double SMOKE_RISE_MIN = 3.0;
const double SMOKE_DEACC = 0.05;

// TS [General] ConditionYellowSparkingProbability=.01, ConditionRedSparkingProbability=.02, per tick, in percent.
const int SPARK_PERCENT_YELLOW = 1;
const int SPARK_PERCENT_RED = 2;

// TS DamageSmokeOffset in leptons above the ground: Z less the X,Y step down the screen ([MMCH] 100,100,275,
// [HMEC] 300,300,425). Every other TS vehicle and aircraft smokes from its centre.
int Smoke_Lift(TechnoTypeClass const* type)
{
    if (_stricmp(type->IniName, "TSTITN") == 0) {
        return (275 - 100);
    }
    if (_stricmp(type->IniName, "TSHMEC") == 0) {
        return (425 - 300);
    }
    return (0);
}

void Move_To(AnimClass* anim, COORDINATE coord);

// Rises and drifts a smoke puff one tick (OpenTS ParticleClass::Smoke_Behavior_AI).
void Puff_AI(AnimClass* anim)
{
    if (Frame & 1) {
        if (Sim_Random_Pick(0, 3) == 0) {
            int step = Sim_Random_Pick(-1, 1);
            if (Sim_Random_Pick(0, 1) == 0) {
                anim->TFVelX = max(-(double)SMOKE_DRIFT_MAX, min((double)SMOKE_DRIFT_MAX, anim->TFVelX + step));
            } else {
                anim->TFVelY = max(-(double)SMOKE_DRIFT_MAX, min((double)SMOKE_DRIFT_MAX, anim->TFVelY + step));
            }
        }
        anim->TFPosX += anim->TFVelX;
        anim->TFPosY += anim->TFVelY;
    }
    anim->TFPosZ += anim->TFVelZ;
    if (anim->TFVelZ > SMOKE_RISE_MIN) {
        anim->TFVelZ -= SMOKE_DEACC;
    }
    COORDINATE ground = XY_Coord((int)anim->TFPosX, (int)anim->TFPosY);
    Move_To(anim, Coord_Move(ground, DIR_N, (unsigned short)anim->TFPosZ));
}

// TS [FLAMEGUY]: RunningFrames=6 per facing over 8 facings, then the collapse.
enum
{
    FLAMEGUY_RUN_FRAMES = 6,
    FLAMEGUY_COLLAPSE = FLAMEGUY_RUN_FRAMES * 8 + 1,
    FLAMEGUY_STEP = 18,      // leptons a tick, OpenTS Flaming_Guy_AI _max_distance
    FLAMEGUY_MAX_CELLS = 7,  // cells run before he drops, OpenTS _max_tries
    FLAMEGUY_FRAME_DIVISOR = 3,
};

int Max_Debris(TechnoTypeClass const* type)
{
    for (unsigned i = 0; i < sizeof(TSDebris) / sizeof(TSDebris[0]); i++) {
        if (_stricmp(type->IniName, TSDebris[i].IniName) == 0) {
            return (TSDebris[i].MaxDebris);
        }
    }
    return (0);
}

bool Is_Shard(AnimType anim)
{
    return (anim >= ANIM_TS_DBRIS1LG && anim <= ANIM_TS_DBRIS10SM);
}

void Move_To(AnimClass* anim, COORDINATE coord)
{
    anim->Mark(MARK_UP);
    anim->Coord = coord;
    anim->Mark(MARK_DOWN);
}

// Flies a shard one tick; it bursts where it lands, or splashes in water (OpenTS AnimClass::AI).
bool Shard_AI(AnimClass* anim)
{
    bool large = *anim <= ANIM_TS_DBRIS10LG;
    anim->TFVelZ -= TS_ANIM_GRAVITY;
    anim->TFPosX += anim->TFVelX;
    anim->TFPosY += anim->TFVelY;
    anim->TFPosZ += anim->TFVelZ;

    double const edge = (double)(MAP_CELL_W * CELL_LEPTON_W);
    if (anim->TFPosX < 0.0 || anim->TFPosY < 0.0 || anim->TFPosX >= edge || anim->TFPosY >= edge) {
        delete anim;
        return (true);
    }
    COORDINATE ground = XY_Coord((int)anim->TFPosX, (int)anim->TFPosY);
    if (!Map.In_Radar(Coord_Cell(ground))) {
        delete anim;
        return (true);
    }

    if (anim->TFPosZ > 0.0) {
        Move_To(anim, Coord_Move(ground, DIR_N, (unsigned short)anim->TFPosZ));
        return (false);
    }

    LandType land = Map[ground].Land_Type();
    if (land == LAND_WATER || land == LAND_RIVER) {
        new AnimClass(ANIM_TS_H2O_EXP3, ground);
    } else {
        if (large) {
            new AnimClass(ANIM_TS_TWLT036, ground);
        }
        Explosion_Damage(ground, large ? LargeShard.Damage : SmallShard.Damage, NULL, WARHEAD_TSHE);
    }
    delete anim;
    return (true);
}

// A burning soldier may run into a cell that is not rock, wall, a building or a vehicle.
bool Can_Run_To(CELL cell)
{
    if (!Map.In_Radar(cell)) {
        return (false);
    }
    CellClass const& cellptr = Map[cell];
    LandType land = cellptr.Land_Type();
    if (land == LAND_ROCK || land == LAND_WALL) {
        return (false);
    }
    if (cellptr.Overlay != OVERLAY_NONE && OverlayTypeClass::As_Reference(cellptr.Overlay).IsWall) {
        return (false);
    }
    return (cellptr.Cell_Building() == NULL && cellptr.Cell_Unit() == NULL);
}

// The next cell a burning soldier runs to: a step toward water within 5 cells, else any open
// neighbour; 0 when he is boxed in (OpenTS Next_Flaming_Guy_Coord).
COORDINATE Next_Run_Cell(COORDINATE from)
{
    CELL cell = Coord_Cell(from);
    int cx = Cell_X(cell);
    int cy = Cell_Y(cell);
    int best = 10000;
    int bx = -1;
    int by = -1;
    for (int x = cx - 5; x < cx + 5; x++) {
        for (int y = cy - 5; y < cy + 5; y++) {
            if (x < 0 || y < 0 || x >= MAP_CELL_W || y >= MAP_CELL_H) {
                continue;
            }
            CELL c = XY_Cell(x, y);
            if (!Map.In_Radar(c) || Map[c].Land_Type() != LAND_WATER) {
                continue;
            }
            int dist = (c == cell) ? 0 : (int)sqrt((double)((x - cx) * (x - cx) + (y - cy) * (y - cy)));
            if (x > cx || y > cy) {
                dist -= 3;
            }
            if (dist < best) {
                best = dist;
                bx = x;
                by = y;
            }
        }
    }

    if (bx >= 0) {
        int dx = (bx > cx) - (bx < cx);
        int dy = (by > cy) - (by < cy);
        if (Can_Run_To(XY_Cell(cx + dx, cy + dy))) {
            return (Cell_Coord(XY_Cell(cx + dx, cy + dy)));
        }
        if (Can_Run_To(XY_Cell(cx + dx, cy))) {
            return (Cell_Coord(XY_Cell(cx + dx, cy)));
        }
        if (Can_Run_To(XY_Cell(cx, cy + dy))) {
            return (Cell_Coord(XY_Cell(cx, cy + dy)));
        }
    }

    int start = Random_Pick(0, 7);
    for (int i = 0; i < 8; i++) {
        CELL next = Adjacent_Cell(cell, FacingType((start + i) % 8));
        if (Can_Run_To(next)) {
            return (Cell_Coord(next));
        }
    }
    return (0);
}

void Stop_Running(AnimClass* anim)
{
    anim->IsTFRunEnd = true;
    anim->TFRunTo = 0;
    anim->Set_Rate(1);
    anim->Set_Stage(FLAMEGUY_COLLAPSE);
}

// Runs a burning soldier a tick toward his next cell, then lets him collapse and burn out
// (OpenTS AnimClass::Flaming_Guy_AI).
void Flaming_Guy_AI(AnimClass* anim)
{
    if (anim->IsTFRunEnd) {
        return;
    }
    anim->Set_Rate(0);

    if (anim->TFRunTo == 0) {
        anim->TFRunTo = Next_Run_Cell(anim->Coord);
        if (anim->TFRunTo == 0) {
            Stop_Running(anim);
            return;
        }
    } else if (Distance(anim->Coord, anim->TFRunTo) <= FLAMEGUY_STEP) {
        Move_To(anim, anim->TFRunTo);
        bool sunk = Map[anim->Coord].Land_Type() == LAND_WATER;
        COORDINATE next = (sunk || anim->TFRunSteps >= FLAMEGUY_MAX_CELLS) ? 0 : Next_Run_Cell(anim->Coord);
        if (next == 0) {
            Stop_Running(anim);
            return;
        }
        anim->TFRunSteps++;
        anim->TFRunTo = next;
    } else {
        Move_To(anim, Coord_Move(anim->Coord, Direction(anim->Coord, anim->TFRunTo), FLAMEGUY_STEP));
    }

    int facing = InfantryClass::HumanShape[Dir_To_32(Direction(anim->Coord, anim->TFRunTo))];
    anim->Set_Stage(FLAMEGUY_RUN_FRAMES * facing + (Frame / FLAMEGUY_FRAME_DIVISOR) % FLAMEGUY_RUN_FRAMES);
}

} // namespace

bool TF_TS_Effects(TechnoTypeClass const* type)
{
    return (TF_Is_TS_Pack_Type(type) && TF_TS_Pack_Present());
}

bool TF_TS_Effects_Bullet(BulletTypeClass const* type)
{
    return (type != NULL && _strnicmp(type->IniName, "TS", 2) == 0 && TF_TS_Pack_Present());
}

AnimType TF_TS_Death_Anim(void)
{
    static AnimType const _blasts[] = {ANIM_TS_TWLT070, ANIM_TS_BANG48, ANIM_TS_BRNL58, ANIM_TS_CLSN58, ANIM_TS_TUMU60};
    return (_blasts[Random_Pick(0, (int)ARRAY_SIZE(_blasts) - 1)]);
}

AnimType TF_TS_Effect(TechnoTypeClass const* type, AnimType anim)
{
    if (!TF_TS_Effects(type)) {
        return (anim);
    }
    switch (anim) {
    case ANIM_FIRE_SMALL:
    case ANIM_ON_FIRE_SMALL:
        return (ANIM_TS_FIRE3);
    case ANIM_FIRE_MED:
    case ANIM_ON_FIRE_MED:
        return (ANIM_TS_FIRE2);
    case ANIM_ON_FIRE_BIG:
        return (ANIM_TS_FIRE1);
    case ANIM_FBALL1:
    case ANIM_FRAG1:
    case ANIM_ART_EXP1:
    case ANIM_NAPALM3:
        return (TF_TS_Death_Anim());
    default:
        return (anim);
    }
}

void TF_TS_Throw_Debris(TechnoTypeClass const* type, COORDINATE coord)
{
    if (!TF_TS_Effects(type)) {
        return;
    }
    LandType land = Map[coord].Land_Type();
    if (land == LAND_WATER || land == LAND_RIVER) {
        return;
    }
    int count = Random_Pick(0, Max_Debris(type));
    for (int i = 0; i < count; i++) {
        int pick = Random_Pick(0, 19);
        ShardType const& shard = (pick < 10) ? LargeShard : SmallShard;
        AnimClass* anim = new AnimClass(AnimType(ANIM_TS_DBRIS1LG + pick), coord);
        if (anim == NULL) {
            return;
        }
        int spread = (int)(shard.MaxXYVel * 2.0);
        anim->TFPosX = Coord_X(coord);
        anim->TFPosY = Coord_Y(coord);
        anim->TFPosZ = 20.0;
        anim->TFVelX = Random_Pick(0, spread - 1) - shard.MaxXYVel;
        anim->TFVelY = Random_Pick(0, spread - 1) - shard.MaxXYVel;
        anim->TFVelZ = shard.MinZVel + Random_Pick(0, shard.ZVelSpread - 1);
    }
}

AnimType TF_TS_Infantry_Death(int infdeath)
{
    switch (infdeath) {
    case 3:
        return (ANIM_TS_SBANG34);
    case 4:
        return (ANIM_TS_FLAMEGUY);
    case 5:
        return (ANIM_TS_ELECTRO);
    default:
        return (ANIM_NONE);
    }
}

AnimType TF_TS_Dead_Body(void)
{
    return (AnimType(ANIM_TS_DEATH_A + Random_Pick(0, ANIM_TS_DEATH_F - ANIM_TS_DEATH_A)));
}

void TF_TS_Firestorm_Glow(BuildingClass* section, bool lit)
{
    TARGET target = section->As_Target();
    AnimClass* ring = NULL;
    for (int i = 0; i < Anims.Count(); i++) {
        AnimClass* anim = Anims.Ptr(i);
        if (anim != NULL && anim->IsActive && *anim == ANIM_TS_FSDF && anim->xObject == target) {
            ring = anim;
            break;
        }
    }
    int joins = section->Shape_Number() & 15;
    bool post = (joins != 5 && joins != 10);
    if (lit && post && ring == NULL) {
        ring = new AnimClass(ANIM_TS_FSDF, Coord_Move(section->Center_Coord(), DIR_N, FIRESTORM_RING_LIFT));
        if (ring != NULL) {
            ring->Attach_To(section);
        }
    } else if ((!lit || !post) && ring != NULL) {
        delete ring;
    }
}

void TF_TS_Damage_AI(TechnoClass* techno)
{
    TechnoTypeClass const* type = techno->Techno_Type_Class();
    if (techno->IsInLimbo || !TF_TS_Effects(type) || techno->Health_Ratio() > Rule.ConditionYellow) {
        return;
    }
    COORDINATE centre = techno->Center_Coord();
    int lift = techno->Height + Smoke_Lift(type);
    if (((Frame + techno->ID) % SMOKE_SPAWN_TICKS) == 0) {
        AnimClass* puff = new AnimClass(ANIM_TS_SGRYSMK1, Coord_Move(centre, DIR_N, lift));
        if (puff != NULL) {
            puff->TFPosX = Coord_X(centre);
            puff->TFPosY = Coord_Y(centre);
            puff->TFPosZ = lift;
            puff->TFVelZ = SMOKE_RISE;
        }
    }
    int chance = (techno->Health_Ratio() <= Rule.ConditionRed) ? SPARK_PERCENT_RED : SPARK_PERCENT_YELLOW;
    if (Sim_Random_Pick(0, 99) < chance) {
        new AnimClass(ANIM_TS_SPARKS, Coord_Move(centre, DIR_N, lift));
    }
}

bool TF_TS_Anim_AI(AnimClass* anim)
{
    if (Is_Shard(*anim)) {
        return (Shard_AI(anim));
    }
    if (*anim == ANIM_TS_FLAMEGUY) {
        Flaming_Guy_AI(anim);
    }
    if (*anim == ANIM_TS_SGRYSMK1) {
        Puff_AI(anim);
    }
    return (false);
}
