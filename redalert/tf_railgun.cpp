/*
**	The railguns' shot: C&C3's railgun shot laid along the line as round anims (docs/cnc3-railgun-beam.md).
*/
#include "function.h"

#include <cmath>

// Lays C&C3's railgun shot from (sx, sy) along (dx, dy) in leptons: glow dots on the core line, the muzzle flash
// and the impact, in blue or the Ghost Stalker's orange. Returns the frames a TS railgun holds.
int TF_Railgun_Beam(bool orange, int sx, int sy, int dx, int dy)
{
    enum
    {
        GLOW_STEP = 16, // leptons between the core's glow dots
        HOLD = 75,      // TS's railgun particle life, which sets a TS railgun's rate of fire
    };

    double const dist = sqrt((double)dx * dx + (double)dy * dy);
    if (dist < 1.0) {
        return (0);
    }
    double const ux = dx / dist, uy = dy / dist;
    for (int d = 0; d <= (int)dist; d += GLOW_STEP) {
        int x = sx + (int)(ux * d), y = sy + (int)(uy * d);
        if (x >= 0 && y >= 0) {
            new AnimClass(orange ? ANIM_C3_RAILGLOWO : ANIM_C3_RAILGLOW, XY_Coord(x, y));
        }
    }
    if (sx >= 0 && sy >= 0) {
        new AnimClass(orange ? ANIM_C3_RAILMZO : ANIM_C3_RAILMZ, XY_Coord(sx, sy));
    }
    if (sx + dx >= 0 && sy + dy >= 0) {
        new AnimClass(orange ? ANIM_C3_RAILHITO : ANIM_C3_RAILHIT, XY_Coord(sx + dx, sy + dy));
    }
    return (HOLD);
}
