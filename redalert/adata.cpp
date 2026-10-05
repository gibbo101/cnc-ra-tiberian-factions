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

/* $Header: /CounterStrike/ADATA.CPP 3     3/07/97 4:27p Joe_bostic $ */
/***********************************************************************************************
 ***              C O N F I D E N T I A L  ---  W E S T W O O D  S T U D I O S               ***
 ***********************************************************************************************
 *                                                                                             *
 *                 Project Name : Command & Conquer                                            *
 *                                                                                             *
 *                    File Name : ADATA.CPP                                                    *
 *                                                                                             *
 *                   Programmer : Joe L. Bostic                                                *
 *                                                                                             *
 *                   Start Date : May 30, 1994                                                 *
 *                                                                                             *
 *                  Last Update : July 9, 1996 [JLB]                                           *
 *                                                                                             *
 *---------------------------------------------------------------------------------------------*
 * Functions:                                                                                  *
 *   AnimTypeClass::AnimTypeClass -- Constructor for animation types.                          *
 *   AnimTypeClass::One_Time -- Performs one time action for animation types.                  *
 *   AnimTypeClass::Init -- Load any animation artwork that is theater specific.               *
 *   Anim_Name -- Fetches the ASCII name of the animation type specified.                      *
 *   AnimTypeClass::As_Reference -- Fetch a reference to the animation type specified.         *
 *   AnimTypeClass::Init_Heap -- Initialize the animation type system.                         *
 *   AnimTypeClass::operator new -- Allocate an animation type object from private pool.       *
 *   AnimTypeClass::operator delete -- Returns an anim type class object back to the pool.     *
 * - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

#include "function.h"

// TD Ion Cannon beam (ANIM_TD_ION_CANNON), ported from TD's ANIM_ION_CANNON. AnimClass::Middle deals its 600 damage
// and spawns ART_EXP1 on that frame, rather than chaining the blast to the end of the anim.
static AnimTypeClass const TdIonCannon(ANIM_TD_ION_CANNON, // Animation number.
                                       "TDIONSFX",         // Data name of animation.
                                       48,                 // Maximum dimension of animation.
                                       11,                 // Biggest animation stage.
                                       false,              // Theater specific art imagery?
                                       false,              // Normalized animation rate? (TD-source false)
                                       false,              // Uses white translucent table?
                                       true,               // Scorches the ground?
                                       true,               // Forms a crater?
                                       false,              // Sticks to unit in square?
                                       false,              // Ground level animation?
                                       false,              // Translucent colors?
                                       false,              // Flame thrower animation?
                                       0x0000,             // Damage per tick (Middle() deals the strike's damage).
                                       1,                  // Delay between frames.
                                       0,                  // Starting frame.
                                       0,                  // Loop start.
                                       0,                  // Loop end.
                                       15,                 // Number of stages.
                                       0,                  // Loops.
                                       VOC_TD_ION1,        // Sound (routed to TDC/TDR_SFX_TDION1).
                                       ANIM_NONE,          // ChainTo (Middle() spawns ART_EXP1 with the damage).
                                       32,                 // Virtual stages.
                                       0x200               // Virtual scale.
);

// TD vehicle frag explosion (ANIM_TDFRAG2), ported from TD's ANIM_FRAG2, whose art is FRAG3; RA ships only FRAG1.
// TD's Medium Tank, APC, Stealth Tank and Mobile SAM die with it.
static AnimTypeClass const TdFrag2(ANIM_TDFRAG2, // Animation number.
                                   "TDFRAG3",     // Data name (TD ANIM_FRAG2 SHP = "FRAG3"; TD-prefixed).
                                   41,            // Maximum dimension of animation (TD FRAG2).
                                   3,             // Biggest animation stage (TD FRAG2).
                                   false,         // Theater specific art imagery?
                                   true,          // Normalized animation rate? (TD-source true)
                                   false,         // Uses white translucent table?
                                   false,         // Scorches the ground? (TD FRAG2: no)
                                   true,          // Forms a crater? (TD FRAG2)
                                   false,         // Sticks to unit in square? (TD FRAG2: no)
                                   true,          // Ground level animation? (TD FRAG2)
                                   false,         // Translucent colors in this animation?
                                   false,         // Is this a flame thrower animation?
                                   0x0000,        // Damage to apply per tick.
                                   1,             // Delay between frames.
                                   0,             // Starting frame number.
                                   0,             // Loop start frame number.
                                   -1,            // Ending frame of loop back.
                                   -1,            // Number of animation stages.
                                   1,             // Number of times the animation loops.
                                   VOC_TD_XPLOBIG6, // Sound (TD VOC_XPLOBIG6; routed RAC/RAR_SFX_XPLOBIG6).
                                   ANIM_NONE,     // ChainTo.
                                   29             // Virtual stages (TD FRAG2).
);

static AnimTypeClass const AtomBomb(ANIM_ATOM_BLAST, // Animation number.
                                    "ATOMSFX",       // Data name of animation.
                                    72,              // Maximum dimension of animation.
                                    19,              // Biggest animation stage.
                                    false,           // Theater specific art imagery?
                                    false,           // Normalized animation rate?
                                    false,           // Uses white translucent table?
                                    true,            // Scorches the ground?
                                    true,            // Forms a crater?
                                    false,           // Sticks to unit in square?
                                    false,           // Ground level animation?
                                    false,           // Translucent colors in this animation?
                                    false,           // Is this a flame thrower animation?
                                    0,               // Damage to apply per tick (fixed point).
                                    1,               // Delay between frames.
                                    0,               // Starting frame number.
                                    0,               // Loop start frame number.
                                    0,               // Ending frame of loop back.
                                    -1,              // Number of animation stages.
                                    0,               // Number of times the animation loops.
                                    VOC_NONE,        // Sound effect to play.
                                    ANIM_NONE,
                                    75,   // Virtual stages
                                    0x300 // Virtual scale
);

static AnimTypeClass const SputDoor(ANIM_SPUTDOOR, // Animation number.
                                    "SPUTDOOR",    // Data name of animation.
                                    42,            // Maximum dimension of animation.
                                    1,             // Biggest animation stage.
                                    false,         // Theater specific art imagery?
                                    true,          // Normalized animation rate?
                                    false,         // Uses white translucent table?
                                    false,         // Scorches the ground?
                                    false,         // Forms a crater?
                                    false,         // Sticks to unit in square?
                                    false,         // Ground level animation?
                                    false,         // Translucent colors in this animation?
                                    false,         // Is this a flame thrower animation?
                                    0,             // Damage to apply per tick (fixed point).
                                    1,             // Delay between frames.
                                    0,             // Starting frame number.
                                    0,             // Loop start frame number.
                                    -1,            // Ending frame of loop back.
                                    -1,            // Number of animation stages.
                                    1,             // Number of times the animation loops.
                                    VOC_NONE,      // Sound effect to play.
                                    ANIM_NONE);

// Electrocution death anim from Tesla coil
static AnimTypeClass const ElectricDie(ANIM_ELECT_DIE, // Animation number.
                                       "ELECTRO",      // Data name of animation.
                                       16,             // Maximum dimension of animation.
                                       0,              // Biggest animation stage.
                                       true,           // Theater specific art imagery?
                                       false,          // Normalized animation rate?
                                       false,          // Uses white translucent table?
                                       true,           // Scorches the ground?
                                       false,          // Forms a crater?
                                       false,          // Sticks to unit in square?
                                       true,           // Ground level animation?
                                       false,          // Translucent colors in this animation?
                                       false,          // Is this a flame thrower animation?
                                       0,              // Damage to apply per tick (fixed point).
                                       1,              // Delay between frames.
                                       0,              // Starting frame number.
                                       0,              // Loop start frame number.
                                       3,              // Ending frame of loop back.
                                       -1,             // Number of animation stages.
                                       5,              // Number of times the animation loops.
                                       VOC_NONE,       // Sound effect to play.
                                       ANIM_FIRE_MED);

// Electrocution death anim from Tesla coil for dog
static AnimTypeClass const DogElectricDie(ANIM_DOG_ELECT_DIE, // Animation number.
                                          "ELECTDOG",         // Data name of animation.
                                          17,                 // Maximum dimension of animation.
                                          0,                  // Biggest animation stage.
                                          false,              // Theater specific art imagery?
                                          false,              // Normalized animation rate?
                                          false,              // Uses white translucent table?
                                          true,               // Scorches the ground?
                                          false,              // Forms a crater?
                                          false,              // Sticks to unit in square?
                                          true,               // Ground level animation?
                                          false,              // Translucent colors in this animation?
                                          false,              // Is this a flame thrower animation?
                                          0,                  // Damage to apply per tick (fixed point).
                                          1,                  // Delay between frames.
                                          0,                  // Starting frame number.
                                          0,                  // Loop start frame number.
                                          3,                  // Ending frame of loop back.
                                          -1,                 // Number of animation stages.
                                          5,                  // Number of times the animation loops.
                                          VOC_NONE,           // Sound effect to play.
                                          ANIM_FIRE_MED);

static AnimTypeClass const SAMN(ANIM_SAM_N, // Animation number.
                                "SAMFIRE",  // Data name of animation.
                                55,         // Maximum dimension of animation.
                                4,          // Biggest animation stage.
                                false,      // Theater specific art imagery?
                                false,      // Normalized animation rate?
                                false,      // Uses white translucent table?
                                false,      // Scorches the ground?
                                false,      // Forms a crater?
                                false,      // Sticks to unit in square?
                                false,      // Ground level animation?
                                false,      // Translucent colors in this animation?
                                false,      // Is this a flame thrower animation?
                                0,          // Damage to apply per tick (fixed point).
                                1,          // Delay between frames.
                                18 * 0,     // Starting frame number.
                                0,          // Loop start frame number.
                                0,          // Ending frame of loop back.
                                18,         // Number of animation stages.
                                0,          // Number of times the animation loops.
                                VOC_NONE,   // Sound effect to play.
                                ANIM_NONE);
static AnimTypeClass const SAMNW(ANIM_SAM_NW, // Animation number.
                                 "SAMFIRE",   // Data name of animation.
                                 55,          // Maximum dimension of animation.
                                 22,          // Biggest animation stage.
                                 false,       // Theater specific art imagery?
                                 false,       // Normalized animation rate?
                                 false,       // Uses white translucent table?
                                 false,       // Scorches the ground?
                                 false,       // Forms a crater?
                                 false,       // Sticks to unit in square?
                                 false,       // Ground level animation?
                                 false,       // Translucent colors in this animation?
                                 false,       // Is this a flame thrower animation?
                                 0,           // Damage to apply per tick (fixed point).
                                 1,           // Delay between frames.
                                 18 * 1,      // Starting frame number.
                                 0,           // Loop start frame number.
                                 0,           // Ending frame of loop back.
                                 18,          // Number of animation stages.
                                 0,           // Number of times the animation loops.
                                 VOC_NONE,    // Sound effect to play.
                                 ANIM_NONE);
static AnimTypeClass const SAMW(ANIM_SAM_W, // Animation number.
                                "SAMFIRE",  // Data name of animation.
                                55,         // Maximum dimension of animation.
                                40,         // Biggest animation stage.
                                false,      // Theater specific art imagery?
                                false,      // Normalized animation rate?
                                false,      // Uses white translucent table?
                                false,      // Scorches the ground?
                                false,      // Forms a crater?
                                false,      // Sticks to unit in square?
                                false,      // Ground level animation?
                                false,      // Translucent colors in this animation?
                                false,      // Is this a flame thrower animation?
                                0,          // Damage to apply per tick (fixed point).
                                1,          // Delay between frames.
                                18 * 2,     // Starting frame number.
                                0,          // Loop start frame number.
                                0,          // Ending frame of loop back.
                                18,         // Number of animation stages.
                                0,          // Number of times the animation loops.
                                VOC_NONE,   // Sound effect to play.
                                ANIM_NONE);
static AnimTypeClass const SAMSW(ANIM_SAM_SW, // Animation number.
                                 "SAMFIRE",   // Data name of animation.
                                 55,          // Maximum dimension of animation.
                                 58,          // Biggest animation stage.
                                 false,       // Theater specific art imagery?
                                 false,       // Normalized animation rate?
                                 false,       // Uses white translucent table?
                                 false,       // Scorches the ground?
                                 false,       // Forms a crater?
                                 false,       // Sticks to unit in square?
                                 false,       // Ground level animation?
                                 false,       // Translucent colors in this animation?
                                 false,       // Is this a flame thrower animation?
                                 0,           // Damage to apply per tick (fixed point).
                                 1,           // Delay between frames.
                                 18 * 3,      // Starting frame number.
                                 0,           // Loop start frame number.
                                 0,           // Ending frame of loop back.
                                 18,          // Number of animation stages.
                                 0,           // Number of times the animation loops.
                                 VOC_NONE,    // Sound effect to play.
                                 ANIM_NONE);
static AnimTypeClass const SAMS(ANIM_SAM_S, // Animation number.
                                "SAMFIRE",  // Data name of animation.
                                55,         // Maximum dimension of animation.
                                76,         // Biggest animation stage.
                                false,      // Theater specific art imagery?
                                false,      // Normalized animation rate?
                                false,      // Uses white translucent table?
                                false,      // Scorches the ground?
                                false,      // Forms a crater?
                                false,      // Sticks to unit in square?
                                false,      // Ground level animation?
                                false,      // Translucent colors in this animation?
                                false,      // Is this a flame thrower animation?
                                0,          // Damage to apply per tick (fixed point).
                                1,          // Delay between frames.
                                18 * 4,     // Starting frame number.
                                0,          // Loop start frame number.
                                0,          // Ending frame of loop back.
                                18,         // Number of animation stages.
                                0,          // Number of times the animation loops.
                                VOC_NONE,   // Sound effect to play.
                                ANIM_NONE);
static AnimTypeClass const SAMSE(ANIM_SAM_SE, // Animation number.
                                 "SAMFIRE",   // Data name of animation.
                                 55,          // Maximum dimension of animation.
                                 94,          // Biggest animation stage.
                                 false,       // Theater specific art imagery?
                                 false,       // Normalized animation rate?
                                 false,       // Uses white translucent table?
                                 false,       // Scorches the ground?
                                 false,       // Forms a crater?
                                 false,       // Sticks to unit in square?
                                 false,       // Ground level animation?
                                 false,       // Translucent colors in this animation?
                                 false,       // Is this a flame thrower animation?
                                 0,           // Damage to apply per tick (fixed point).
                                 1,           // Delay between frames.
                                 18 * 5,      // Starting frame number.
                                 0,           // Loop start frame number.
                                 0,           // Ending frame of loop back.
                                 18,          // Number of animation stages.
                                 0,           // Number of times the animation loops.
                                 VOC_NONE,    // Sound effect to play.
                                 ANIM_NONE);
static AnimTypeClass const SAME(ANIM_SAM_E, // Animation number.
                                "SAMFIRE",  // Data name of animation.
                                55,         // Maximum dimension of animation.
                                112,        // Biggest animation stage.
                                false,      // Theater specific art imagery?
                                false,      // Normalized animation rate?
                                false,      // Uses white translucent table?
                                false,      // Scorches the ground?
                                false,      // Forms a crater?
                                false,      // Sticks to unit in square?
                                false,      // Ground level animation?
                                false,      // Translucent colors in this animation?
                                false,      // Is this a flame thrower animation?
                                0,          // Damage to apply per tick (fixed point).
                                1,          // Delay between frames.
                                18 * 6,     // Starting frame number.
                                0,          // Loop start frame number.
                                0,          // Ending frame of loop back.
                                18,         // Number of animation stages.
                                0,          // Number of times the animation loops.
                                VOC_NONE,   // Sound effect to play.
                                ANIM_NONE);
static AnimTypeClass const SAMNE(ANIM_SAM_NE, // Animation number.
                                 "SAMFIRE",   // Data name of animation.
                                 55,          // Maximum dimension of animation.
                                 130,         // Biggest animation stage.
                                 false,       // Theater specific art imagery?
                                 false,       // Normalized animation rate?
                                 false,       // Uses white translucent table?
                                 false,       // Scorches the ground?
                                 false,       // Forms a crater?
                                 false,       // Sticks to unit in square?
                                 false,       // Ground level animation?
                                 false,       // Translucent colors in this animation?
                                 false,       // Is this a flame thrower animation?
                                 0,           // Damage to apply per tick (fixed point).
                                 1,           // Delay between frames.
                                 18 * 7,      // Starting frame number.
                                 0,           // Loop start frame number.
                                 0,           // Ending frame of loop back.
                                 18,          // Number of animation stages.
                                 0,           // Number of times the animation loops.
                                 VOC_NONE,    // Sound effect to play.
                                 ANIM_NONE);

static AnimTypeClass const LZSmoke(ANIM_LZ_SMOKE, // Animation number.
                                   "SMOKLAND",    // Data name of animation.
                                   32,            // Maximum dimension of animation.
                                   72,            // Biggest animation stage.
                                   false,         // Theater specific art imagery?
                                   true,          // Normalized animation rate?
                                   false,         // Uses white translucent table?
                                   false,         // Scorches the ground?
                                   false,         // Forms a crater?
                                   false,         // Sticks to unit in square?
                                   true,          // Ground level animation?
                                   false,         // Translucent colors in this animation?
                                   false,         // Is this a flame thrower animation?
                                   0,             // Damage to apply per tick (fixed point).
                                   2,             // Delay between frames.
                                   0,             // Starting frame number.
                                   72,            // Loop start frame number.
                                   91,            // Ending frame of loop back.
                                   -1,            // Number of animation stages.
                                   127,           // Number of times the animation loops.
                                   VOC_NONE,      // Sound effect to play.
                                   ANIM_NONE);

/*
**	Flammable object burning animations. Primarily used on trees and buildings.
*/
static AnimTypeClass const BurnSmall(ANIM_BURN_SMALL, // Animation number.
                                     "BURN-S",        // Data name of animation.
                                     11,              // Maximum dimension of animation.
                                     13,              // Biggest animation stage.
                                     false,           // Theater specific art imagery?
                                     false,           // Normalized animation rate?
                                     false,           // Uses white translucent table?
                                     false,           // Scorches the ground?
                                     false,           // Forms a crater?
                                     false,           // Sticks to unit in square?
                                     true,            // Ground level animation?
                                     false,           // Translucent colors in this animation?
                                     false,           // Is this a flame thrower animation?
                                     fixed(1, 32),    // Damage to apply per tick (fixed point).
                                     2,               // Delay between frames.
                                     0,               // Starting frame number.
                                     30,              // Loop start frame number.
                                     62,              // Ending frame of loop back.
                                     -1,              // Number of animation stages.
                                     4,               // Number of times the animation loops.
                                     VOC_NONE,        // Sound effect to play.
                                     ANIM_NONE);
static AnimTypeClass const BurnMed(ANIM_BURN_MED, // Animation number.
                                   "BURN-M",      // Data name of animation.
                                   14,            // Maximum dimension of animation.
                                   13,            // Biggest animation stage.
                                   false,         // Theater specific art imagery?
                                   false,         // Normalized animation rate?
                                   false,         // Uses white translucent table?
                                   false,         // Scorches the ground?
                                   false,         // Forms a crater?
                                   false,         // Sticks to unit in square?
                                   true,          // Ground level animation?
                                   false,         // Translucent colors in this animation?
                                   false,         // Is this a flame thrower animation?
                                   fixed(1, 16),  // Damage to apply per tick (fixed point).
                                   2,             // Delay between frames.
                                   0,             // Starting frame number.
                                   30,            // Loop start frame number.
                                   62,            // Ending frame of loop back.
                                   -1,            // Number of animation stages.
                                   4,             // Number of times the animation loops.
                                   VOC_NONE,      // Sound effect to play.
                                   ANIM_NONE);
static AnimTypeClass const BurnBig(ANIM_BURN_BIG, // Animation number.
                                   "BURN-L",      // Data name of animation.
                                   23,            // Maximum dimension of animation.
                                   13,            // Biggest animation stage.
                                   false,         // Theater specific art imagery?
                                   false,         // Normalized animation rate?
                                   false,         // Uses white translucent table?
                                   true,          // Scorches the ground?
                                   false,         // Forms a crater?
                                   false,         // Sticks to unit in square?
                                   true,          // Ground level animation?
                                   false,         // Translucent colors in this animation?
                                   false,         // Is this a flame thrower animation?
                                   fixed(1, 10),  // Damage to apply per tick (fixed point).
                                   2,             // Delay between frames.
                                   0,             // Starting frame number.
                                   30,            // Loop start frame number.
                                   62,            // Ending frame of loop back.
                                   -1,            // Number of animation stages.
                                   4,             // Number of times the animation loops.
                                   VOC_NONE,      // Sound effect to play.
                                   ANIM_NONE);

/*
**	Flammable object burning animations that trail into smoke. Used for
**	buildings and the gunboat.
*/
static AnimTypeClass const OnFireSmall(ANIM_ON_FIRE_SMALL, // Animation number.
                                       "BURN-S",           // Data name of animation.
                                       11,                 // Maximum dimension of animation.
                                       13,                 // Biggest animation stage.
                                       false,              // Theater specific art imagery?
                                       false,              // Normalized animation rate?
                                       false,              // Uses white translucent table?
                                       false,              // Scorches the ground?
                                       false,              // Forms a crater?
                                       false,              // Sticks to unit in square?
                                       true,               // Ground level animation?
                                       false,              // Translucent colors in this animation?
                                       false,              // Is this a flame thrower animation?
                                       fixed(1, 32),       // Damage to apply per tick (fixed point).
                                       2,                  // Delay between frames.
                                       0,                  // Starting frame number.
                                       30,                 // Loop start frame number.
                                       62,                 // Ending frame of loop back.
                                       -1,                 // Number of animation stages.
                                       4,                  // Number of times the animation loops.
                                       VOC_NONE,           // Sound effect to play.
                                       ANIM_SMOKE_M);
static AnimTypeClass const OnFireMed(ANIM_ON_FIRE_MED, // Animation number.
                                     "BURN-M",         // Data name of animation.
                                     14,               // Maximum dimension of animation.
                                     13,               // Biggest animation stage.
                                     false,            // Theater specific art imagery?
                                     false,            // Normalized animation rate?
                                     false,            // Uses white translucent table?
                                     false,            // Scorches the ground?
                                     false,            // Forms a crater?
                                     false,            // Sticks to unit in square?
                                     true,             // Ground level animation?
                                     false,            // Translucent colors in this animation?
                                     false,            // Is this a flame thrower animation?
                                     fixed(1, 16),     // Damage to apply per tick (fixed point).
                                     2,                // Delay between frames.
                                     0,                // Starting frame number.
                                     30,               // Loop start frame number.
                                     62,               // Ending frame of loop back.
                                     -1,               // Number of animation stages.
                                     4,                // Number of times the animation loops.
                                     VOC_NONE,         // Sound effect to play.
                                     ANIM_ON_FIRE_SMALL);
static AnimTypeClass const OnFireBig(ANIM_ON_FIRE_BIG, // Animation number.
                                     "BURN-L",         // Data name of animation.
                                     23,               // Maximum dimension of animation.
                                     13,               // Biggest animation stage.
                                     false,            // Theater specific art imagery?
                                     false,            // Normalized animation rate?
                                     false,            // Uses white translucent table?
                                     true,             // Scorches the ground?
                                     false,            // Forms a crater?
                                     false,            // Sticks to unit in square?
                                     true,             // Ground level animation?
                                     false,            // Translucent colors in this animation?
                                     false,            // Is this a flame thrower animation?
                                     fixed(1, 10),     // Damage to apply per tick (fixed point).
                                     2,                // Delay between frames.
                                     0,                // Starting frame number.
                                     30,               // Loop start frame number.
                                     62,               // Ending frame of loop back.
                                     -1,               // Number of animation stages.
                                     4,                // Number of times the animation loops.
                                     VOC_NONE,         // Sound effect to play.
                                     ANIM_ON_FIRE_MED);
static AnimTypeClass const Parachute(ANIM_PARACHUTE, // Animation number.
                                     "PARACH",       // Data name of animation.
                                     32,             // Maximum dimension of animation.
                                     15,             // Biggest animation stage.
                                     false,          // Theater specific art imagery?
                                     false,          // Normalized animation rate?
                                     false,          // Uses white translucent table?
                                     false,          // Scorches the ground?
                                     false,          // Forms a crater?
                                     false,          // Sticks to unit in square?
                                     false,          // Ground level animation?
                                     false,          // Translucent colors in this animation?
                                     false,          // Is this a flame thrower animation?
                                     0,              // Damage to apply per tick (fixed point).
                                     4,              // Delay between frames.
                                     0,              // Starting frame number.
                                     7,              // Loop start frame number.
                                     -1,             // Loopback frame number.
                                     -1,             // Number of animation stages.
                                     15,             // Number of times the animation loops.
                                     VOC_NONE,       // Sound effect to play.
                                     ANIM_NONE);
static AnimTypeClass const ParaBomb(ANIM_PARA_BOMB, // Animation number.
                                    "PARABOMB",     // Data name of animation.
                                    32,             // Maximum dimension of animation.
                                    8,              // Biggest animation stage.
                                    false,          // Theater specific art imagery?
                                    false,          // Normalized animation rate?
                                    false,          // Uses white translucent table?
                                    false,          // Scorches the ground?
                                    false,          // Forms a crater?
                                    false,          // Sticks to unit in square?
                                    false,          // Ground level animation?
                                    false,          // Translucent colors in this animation?
                                    false,          // Is this a flame thrower animation?
                                    0,              // Damage to apply per tick (fixed point).
                                    4,              // Delay between frames.
                                    0,              // Starting frame number.
                                    7,              // Loop start frame number.
                                    -1,             // Loopback frame number.
                                    -1,             // Number of animation stages.
                                    15,             // Number of times the animation loops.
                                    VOC_NONE,       // Sound effect to play.
                                    ANIM_NONE);

static AnimTypeClass const FBall1(ANIM_FBALL1,  // Animation number.
                                  "FBALL1",     // Data name of animation.
                                  67,           // Maximum dimension of animation.
                                  6,            // Biggest animation stage.
                                  false,        // Theater specific art imagery?
                                  true,         // Normalized animation rate?
                                  false,        // Uses white translucent table?
                                  false,        // Scorches the ground?
                                  true,         // Forms a crater?
                                  false,        // Sticks to unit in square?
                                  false,        // Ground level animation?
                                  false,        // Translucent colors in this animation?
                                  false,        // Is this a flame thrower animation?
                                  0,            // Damage to apply per tick (fixed point).
                                  1,            // Delay between frames.
                                  0,            // Starting frame number.
                                  0,            // Loop start frame number.
                                  -1,           // Ending frame of loop back.
                                  -1,           // Number of animation stages.
                                  1,            // Number of times the animation loops.
                                  VOC_KABOOM25, // Sound effect to play.
                                  ANIM_NONE);

static AnimTypeClass const Frag1(ANIM_FRAG1,   // Animation number.
                                 "FRAG1",      // Data name of animation.
                                 45,           // Maximum dimension of animation.
                                 3,            // Biggest animation stage.
                                 false,        // Theater specific art imagery?
                                 true,         // Normalized animation rate?
                                 false,        // Uses white translucent table?
                                 false,        // Scorches the ground?
                                 true,         // Forms a crater?
                                 true,         // Sticks to unit in square?
                                 true,         // Ground level animation?
                                 false,        // Translucent colors in this animation?
                                 false,        // Is this a flame thrower animation?
                                 0,            // Damage to apply per tick (fixed point).
                                 1,            // Delay between frames.
                                 0,            // Starting frame number.
                                 0,            // Loop start frame number.
                                 -1,           // Ending frame of loop back.
                                 -1,           // Number of animation stages.
                                 1,            // Number of times the animation loops.
                                 VOC_KABOOM30, // Sound effect to play.
                                 ANIM_NONE,
                                 29 // Virtual stages
);

static AnimTypeClass const VehHit1(ANIM_VEH_HIT1, // Animation number.
                                   "VEH-HIT1",    // Data name of animation.
                                   30,            // Maximum dimension of animation.
                                   4,             // Biggest animation stage.
                                   false,         // Theater specific art imagery?
                                   true,          // Normalized animation rate?
                                   false,         // Uses white translucent table?
                                   false,         // Scorches the ground?
                                   true,          // Forms a crater?
                                   true,          // Sticks to unit in square?
                                   false,         // Ground level animation?
                                   false,         // Translucent colors in this animation?
                                   false,         // Is this a flame thrower animation?
                                   0,             // Damage to apply per tick (fixed point).
                                   1,             // Delay between frames.
                                   0,             // Starting frame number.
                                   0,             // Loop start frame number.
                                   -1,            // Ending frame of loop back.
                                   -1,            // Number of animation stages.
                                   1,             // Number of times the animation loops.
                                   VOC_KABOOM25,  // Sound effect to play.
                                   ANIM_NONE);

static AnimTypeClass const VehHit2(ANIM_VEH_HIT2, // Animation number.
                                   "VEH-HIT2",    // Data name of animation.
                                   21,            // Maximum dimension of animation.
                                   1,             // Biggest animation stage.
                                   false,         // Theater specific art imagery?
                                   true,          // Normalized animation rate?
                                   false,         // Uses white translucent table?
                                   false,         // Scorches the ground?
                                   true,          // Forms a crater?
                                   true,          // Sticks to unit in square?
                                   false,         // Ground level animation?
                                   false,         // Translucent colors in this animation?
                                   false,         // Is this a flame thrower animation?
                                   0,             // Damage to apply per tick (fixed point).
                                   1,             // Delay between frames.
                                   0,             // Starting frame number.
                                   0,             // Loop start frame number.
                                   -1,            // Ending frame of loop back.
                                   -1,            // Number of animation stages.
                                   1,             // Number of times the animation loops.
                                   VOC_KABOOM12,  // Sound effect to play.
                                   ANIM_NONE);

static AnimTypeClass const VehHit3(ANIM_VEH_HIT3, // Animation number.
                                   "VEH-HIT3",    // Data name of animation.
                                   19,            // Maximum dimension of animation.
                                   3,             // Biggest animation stage.
                                   false,         // Theater specific art imagery?
                                   true,          // Normalized animation rate?
                                   false,         // Uses white translucent table?
                                   false,         // Scorches the ground?
                                   false,         // Forms a crater?
                                   true,          // Sticks to unit in square?
                                   false,         // Ground level animation?
                                   false,         // Translucent colors in this animation?
                                   false,         // Is this a flame thrower animation?
                                   0,             // Damage to apply per tick (fixed point).
                                   1,             // Delay between frames.
                                   0,             // Starting frame number.
                                   0,             // Loop start frame number.
                                   -1,            // Ending frame of loop back.
                                   -1,            // Number of animation stages.
                                   1,             // Number of times the animation loops.
                                   VOC_KABOOM12,  // Sound effect to play.
                                   ANIM_NONE);

static AnimTypeClass const ArtExp1(ANIM_ART_EXP1, // Animation number.
                                   "ART-EXP1",    // Data name of animation.
                                   41,            // Maximum dimension of animation.
                                   1,             // Biggest animation stage.
                                   false,         // Theater specific art imagery?
                                   true,          // Normalized animation rate?
                                   false,         // Uses white translucent table?
                                   false,         // Scorches the ground?
                                   true,          // Forms a crater?
                                   false,         // Sticks to unit in square?
                                   false,         // Ground level animation?
                                   false,         // Translucent colors in this animation?
                                   false,         // Is this a flame thrower animation?
                                   0,             // Damage to apply per tick (fixed point).
                                   1,             // Delay between frames.
                                   0,             // Starting frame number.
                                   0,             // Loop start frame number.
                                   -1,            // Ending frame of loop back.
                                   -1,            // Number of animation stages.
                                   1,             // Number of times the animation loops.
                                   VOC_KABOOM22,  // Sound effect to play.
                                   ANIM_NONE);

static AnimTypeClass const Napalm1(ANIM_NAPALM1,     // Animation number.
                                   "NAPALM1",        // Data name of animation.
                                   21,               // Maximum dimension of animation.
                                   5,                // Biggest animation stage.
                                   false,            // Theater specific art imagery?
                                   false,            // Normalized animation rate?
                                   false,            // Uses white translucent table?
                                   true,             // Scorches the ground?
                                   false,            // Forms a crater?
                                   false,            // Sticks to unit in square?
                                   false,            // Ground level animation?
                                   false,            // Translucent colors in this animation?
                                   false,            // Is this a flame thrower animation?
                                   0,                // Damage to apply per tick (fixed point).
                                   1,                // Delay between frames.
                                   0,                // Starting frame number.
                                   0,                // Loop start frame number.
                                   -1,               // Ending frame of loop back.
                                   -1,               // Number of animation stages.
                                   1,                // Number of times the animation loops.
                                   VOC_FIRE_EXPLODE, // Sound effect to play.
                                   ANIM_NONE);

static AnimTypeClass const Napalm2(ANIM_NAPALM2,     // Animation number.
                                   "NAPALM2",        // Data name of animation.
                                   41,               // Maximum dimension of animation.
                                   5,                // Biggest animation stage.
                                   false,            // Theater specific art imagery?
                                   false,            // Normalized animation rate?
                                   false,            // Uses white translucent table?
                                   true,             // Scorches the ground?
                                   false,            // Forms a crater?
                                   false,            // Sticks to unit in square?
                                   false,            // Ground level animation?
                                   false,            // Translucent colors in this animation?
                                   false,            // Is this a flame thrower animation?
                                   0,                // Damage to apply per tick (fixed point).
                                   1,                // Delay between frames.
                                   0,                // Starting frame number.
                                   0,                // Loop start frame number.
                                   -1,               // Ending frame of loop back.
                                   -1,               // Number of animation stages.
                                   1,                // Number of times the animation loops.
                                   VOC_FIRE_EXPLODE, // Sound effect to play.
                                   ANIM_NONE);

static AnimTypeClass const Napalm3(ANIM_NAPALM3,    // Animation number.
                                   "NAPALM3",       // Data name of animation.
                                   78,              // Maximum dimension of animation.
                                   5,               // Biggest animation stage.
                                   false,           // Theater specific art imagery?
                                   false,           // Normalized animation rate?
                                   false,           // Uses white translucent table?
                                   true,            // Scorches the ground?
                                   false,           // Forms a crater?
                                   false,           // Sticks to unit in square?
                                   false,           // Ground level animation?
                                   false,           // Translucent colors in this animation?
                                   false,           // Is this a flame thrower animation?
                                   0,               // Damage to apply per tick (fixed point).
                                   1,               // Delay between frames.
                                   0,               // Starting frame number.
                                   0,               // Loop start frame number.
                                   -1,              // Ending frame of loop back.
                                   -1,              // Number of animation stages.
                                   1,               // Number of times the animation loops.
                                   VOC_FIRE_LAUNCH, // Sound effect to play.
                                   ANIM_NONE);

static AnimTypeClass const SmokePuff(ANIM_SMOKE_PUFF, // Animation number.
                                     "SMOKEY",        // Data name of animation.
                                     24,              // Maximum dimension of animation.
                                     2,               // Biggest animation stage.
                                     false,           // Theater specific art imagery?
                                     true,            // Normalized animation rate?
                                     false,           // Uses white translucent table?
                                     false,           // Scorches the ground?
                                     false,           // Forms a crater?
                                     false,           // Sticks to unit in square?
                                     false,           // Ground level animation?
                                     true,            // Translucent colors in this animation?
                                     false,           // Is this a flame thrower animation?
                                     0,               // Damage to apply per tick (fixed point).
                                     1,               // Delay between frames.
                                     0,               // Starting frame number.
                                     0,               // Loop start frame number.
                                     -1,              // Ending frame of loop back.
                                     -1,              // Number of animation stages.
                                     1,               // Number of times the animation loops.
                                     VOC_NONE,        // Sound effect to play.
                                     ANIM_NONE);

static AnimTypeClass const FireBallFade(ANIM_FBALL_FADE, // Animation number.
                                        "FB2",           // Data name of animation.
                                        24,              // Maximum dimension of animation.
                                        1,               // Biggest animation stage.
                                        false,           // Theater specific art imagery?
                                        true,            // Normalized animation rate?
                                        false,           // Uses white translucent table?
                                        false,           // Scorches the ground?
                                        false,           // Forms a crater?
                                        false,           // Sticks to unit in square?
                                        false,           // Ground level animation?
                                        false,           // Translucent colors in this animation?
                                        false,           // Is this a flame thrower animation?
                                        0,               // Damage to apply per tick (fixed point).
                                        1,               // Delay between frames.
                                        0,               // Starting frame number.
                                        0,               // Loop start frame number.
                                        -1,              // Ending frame of loop back.
                                        -1,              // Number of animation stages.
                                        1,               // Number of times the animation loops.
                                        VOC_NONE,        // Sound effect to play.
                                        ANIM_NONE);

static AnimTypeClass const Piff(ANIM_PIFF, // Animation number.
                                "PIFF",    // Data name of animation.
                                13,        // Maximum dimension of animation.
                                1,         // Biggest animation stage.
                                false,     // Theater specific art imagery?
                                true,      // Normalized animation rate?
                                false,     // Uses white translucent table?
                                false,     // Scorches the ground?
                                false,     // Forms a crater?
                                false,     // Sticks to unit in square?
                                false,     // Ground level animation?
                                false,     // Translucent colors in this animation?
                                false,     // Is this a flame thrower animation?
                                0,         // Damage to apply per tick (fixed point).
                                1,         // Delay between frames.
                                0,         // Starting frame number.
                                0,         // Loop start frame number.
                                -1,        // Ending frame of loop back.
                                -1,        // Number of animation stages.
                                1,         // Number of times the animation loops.
                                VOC_NONE,  // Sound effect to play.
                                ANIM_NONE);

static AnimTypeClass const PiffPiff(ANIM_PIFFPIFF, // Animation number.
                                    "PIFFPIFF",    // Data name of animation.
                                    20,            // Maximum dimension of animation.
                                    2,             // Biggest animation stage.
                                    false,         // Theater specific art imagery?
                                    true,          // Normalized animation rate?
                                    false,         // Uses white translucent table?
                                    false,         // Scorches the ground?
                                    false,         // Forms a crater?
                                    false,         // Sticks to unit in square?
                                    false,         // Ground level animation?
                                    false,         // Translucent colors in this animation?
                                    false,         // Is this a flame thrower animation?
                                    0,             // Damage to apply per tick (fixed point).
                                    1,             // Delay between frames.
                                    0,             // Starting frame number.
                                    0,             // Loop start frame number.
                                    -1,            // Ending frame of loop back.
                                    -1,            // Number of animation stages.
                                    1,             // Number of times the animation loops.
                                    VOC_NONE,      // Sound effect to play.
                                    ANIM_NONE);

static AnimTypeClass const Fire3(ANIM_FIRE_SMALL, // Animation number.
                                 "FIRE3",         // Data name of animation.
                                 23,              // Maximum dimension of animation.
                                 0,               // Biggest animation stage.
                                 false,           // Theater specific art imagery?
                                 false,           // Normalized animation rate?
                                 false,           // Uses white translucent table?
                                 false,           // Scorches the ground?
                                 false,           // Forms a crater?
                                 false,           // Sticks to unit in square?
                                 true,            // Ground level animation?
                                 false,           // Translucent colors in this animation?
                                 false,           // Is this a flame thrower animation?
                                 fixed(1, 32),    // Damage to apply per tick (fixed point).
                                 1,               // Delay between frames.
                                 0,               // Starting frame number.
                                 0,               // Loop start frame number.
                                 -1,              // Ending frame of loop back.
                                 -1,              // Number of animation stages.
                                 2,               // Number of times the animation loops.
                                 VOC_NONE,        // Sound effect to play.
                                 ANIM_NONE
#ifdef REMASTER_BUILD
                                 ,
                                 -1,                     // Virtual stages
                                 0x100,                  // Virtual scale
                                 NULL,                   // Virtual name
                                 ANIM_FIRE_SMALL_VIRTUAL // Virtual anim
#endif
);

#ifdef REMASTER_BUILD
static AnimTypeClass const Fire3Virtual(ANIM_FIRE_SMALL_VIRTUAL, // Animation number.
                                        "FIRE3",                 // Data name of animation.
                                        23,                      // Maximum dimension of animation.
                                        0,                       // Biggest animation stage.
                                        false,                   // Theater specific art imagery?
                                        false,                   // Normalized animation rate?
                                        false,                   // Uses white translucent table?
                                        false,                   // Scorches the ground?
                                        false,                   // Forms a crater?
                                        false,                   // Sticks to unit in square?
                                        true,                    // Ground level animation?
                                        false,                   // Translucent colors in this animation?
                                        false,                   // Is this a flame thrower animation?
                                        0,                       // Damage to apply per tick (fixed point).
                                        1,                       // Delay between frames.
                                        0,                       // Starting frame number.
                                        10,                      // Loop start frame number.
                                        21,                      // Ending frame of loop back.
                                        29,                      // Number of animation stages.
                                        2,                       // Number of times the animation loops.
                                        VOC_NONE,                // Sound effect to play.
                                        ANIM_NONE);
#endif

static AnimTypeClass const Fire1(ANIM_FIRE_MED2, // Animation number.
                                 "FIRE1",        // Data name of animation.
                                 23,             // Maximum dimension of animation.
                                 0,              // Biggest animation stage.
                                 false,          // Theater specific art imagery?
                                 false,          // Normalized animation rate?
                                 false,          // Uses white translucent table?
                                 true,           // Scorches the ground?
                                 false,          // Forms a crater?
                                 false,          // Sticks to unit in square?
                                 true,           // Ground level animation?
                                 false,          // Translucent colors in this animation?
                                 false,          // Is this a flame thrower animation?
                                 fixed(1, 16),   // Damage to apply per tick (fixed point).
                                 1,              // Delay between frames.
                                 0,              // Starting frame number.
                                 0,              // Loop start frame number.
                                 -1,             // Ending frame of loop back.
                                 -1,             // Number of animation stages.
                                 3,              // Number of times the animation loops.
                                 VOC_NONE,       // Sound effect to play.
                                 ANIM_NONE
#ifdef REMASTER_BUILD
                                 ,
                                 -1,                    // Virtual stages
                                 0x100,                 // Virtual scale
                                 NULL,                  // Virtual name
                                 ANIM_FIRE_MED2_VIRTUAL // Virtual anim
#endif
);

#ifdef REMASTER_BUILD
static AnimTypeClass const Fire1Virtual(ANIM_FIRE_MED2_VIRTUAL, // Animation number.
                                        "FIRE1",                // Data name of animation.
                                        23,                     // Maximum dimension of animation.
                                        0,                      // Biggest animation stage.
                                        false,                  // Theater specific art imagery?
                                        false,                  // Normalized animation rate?
                                        false,                  // Uses white translucent table?
                                        true,                   // Scorches the ground?
                                        false,                  // Forms a crater?
                                        false,                  // Sticks to unit in square?
                                        true,                   // Ground level animation?
                                        false,                  // Translucent colors in this animation?
                                        false,                  // Is this a flame thrower animation?
                                        0,                      // Damage to apply per tick (fixed point).
                                        1,                      // Delay between frames.
                                        0,                      // Starting frame number.
                                        10,                     // Loop start frame number.
                                        21,                     // Ending frame of loop back.
                                        29,                     // Number of animation stages.
                                        3,                      // Number of times the animation loops.
                                        VOC_NONE,               // Sound effect to play.
                                        ANIM_NONE);
#endif

static AnimTypeClass const Fire4(ANIM_FIRE_TINY, // Animation number.
                                 "FIRE4",        // Data name of animation.
                                 7,              // Maximum dimension of animation.
                                 0,              // Biggest animation stage.
                                 false,          // Theater specific art imagery?
                                 false,          // Normalized animation rate?
                                 false,          // Uses white translucent table?
                                 false,          // Scorches the ground?
                                 false,          // Forms a crater?
                                 false,          // Sticks to unit in square?
                                 true,           // Ground level animation?
                                 false,          // Translucent colors in this animation?
                                 false,          // Is this a flame thrower animation?
                                 fixed(1, 32),   // Damage to apply per tick (fixed point).
                                 1,              // Delay between frames.
                                 0,              // Starting frame number.
                                 0,              // Loop start frame number.
                                 -1,             // Ending frame of loop back.
                                 -1,             // Number of animation stages.
                                 3,              // Number of times the animation loops.
                                 VOC_NONE,       // Sound effect to play.
                                 ANIM_NONE
#ifdef REMASTER_BUILD
                                 ,
                                 -1,                    // Virtual stages
                                 0x100,                 // Virtual scale
                                 NULL,                  // Virtual name
                                 ANIM_FIRE_TINY_VIRTUAL // Virtual anim
#endif
);

#ifdef REMASTER_BUILD
static AnimTypeClass const Fire4Virtual(ANIM_FIRE_TINY_VIRTUAL, // Animation number.
                                        "FIRE4",                // Data name of animation.
                                        7,                      // Maximum dimension of animation.
                                        0,                      // Biggest animation stage.
                                        false,                  // Theater specific art imagery?
                                        false,                  // Normalized animation rate?
                                        false,                  // Uses white translucent table?
                                        false,                  // Scorches the ground?
                                        false,                  // Forms a crater?
                                        false,                  // Sticks to unit in square?
                                        true,                   // Ground level animation?
                                        false,                  // Translucent colors in this animation?
                                        false,                  // Is this a flame thrower animation?
                                        0,                      // Damage to apply per tick (fixed point).
                                        1,                      // Delay between frames.
                                        0,                      // Starting frame number.
                                        10,                     // Loop start frame number.
                                        21,                     // Ending frame of loop back.
                                        29,                     // Number of animation stages.
                                        3,                      // Number of times the animation loops.
                                        VOC_NONE,               // Sound effect to play.
                                        ANIM_NONE);
#endif

static AnimTypeClass const Fire2(ANIM_FIRE_MED, // Animation number.
                                 "FIRE2",       // Data name of animation.
                                 23,            // Maximum dimension of animation.
                                 0,             // Biggest animation stage.
                                 false,         // Theater specific art imagery?
                                 false,         // Normalized animation rate?
                                 false,         // Uses white translucent table?
                                 true,          // Scorches the ground?
                                 false,         // Forms a crater?
                                 false,         // Sticks to unit in square?
                                 true,          // Ground level animation?
                                 false,         // Translucent colors in this animation?
                                 false,         // Is this a flame thrower animation?
                                 fixed(1, 16),  // Damage to apply per tick (fixed point).
                                 1,             // Delay between frames.
                                 0,             // Starting frame number.
                                 0,             // Loop start frame number.
                                 -1,            // Ending frame of loop back.
                                 -1,            // Number of animation stages.
                                 3,             // Number of times the animation loops.
                                 VOC_NONE,      // Sound effect to play.
                                 ANIM_NONE
#ifdef REMASTER_BUILD
                                 ,
                                 -1,                   // Virtual stages
                                 0x100,                // Virtual scale
                                 NULL,                 // Virtual name
                                 ANIM_FIRE_MED_VIRTUAL // Virtual anim
#endif
);

#ifdef REMASTER_BUILD
static AnimTypeClass const Fire2Virtual(ANIM_FIRE_MED_VIRTUAL, // Animation number.
                                        "FIRE2",               // Data name of animation.
                                        23,                    // Maximum dimension of animation.
                                        0,                     // Biggest animation stage.
                                        false,                 // Theater specific art imagery?
                                        false,                 // Normalized animation rate?
                                        false,                 // Uses white translucent table?
                                        true,                  // Scorches the ground?
                                        false,                 // Forms a crater?
                                        false,                 // Sticks to unit in square?
                                        true,                  // Ground level animation?
                                        false,                 // Translucent colors in this animation?
                                        false,                 // Is this a flame thrower animation?
                                        0,                     // Damage to apply per tick (fixed point).
                                        1,                     // Delay between frames.
                                        0,                     // Starting frame number.
                                        10,                    // Loop start frame number.
                                        21,                    // Ending frame of loop back.
                                        29,                    // Number of animation stages.
                                        3,                     // Number of times the animation loops.
                                        VOC_NONE,              // Sound effect to play.
                                        ANIM_NONE);
#endif

static AnimTypeClass const OilFieldBurn(ANIM_OILFIELD_BURN, // Animation number.
                                        "FLMSPT",           // Data name of animation.
                                        42,                 // Maximum dimension of animation.
                                        58,                 // Biggest animation stage.
                                        false,              // Theater specific art imagery?
                                        true,               // Normalized animation rate?
                                        false,              // Uses white translucent table?
                                        false,              // Scorches the ground?
                                        false,              // Forms a crater?
                                        false,              // Sticks to unit in square?
                                        true,               // Ground level animation?
                                        false,              // Translucent colors in this animation?
                                        false,              // Is this a flame thrower animation?
                                        0,                  // Damage to apply per tick (fixed point).
                                        1,                  // Delay between frames.
                                        0,                  // Starting frame number.
                                        33,                 // Loop start frame number.
                                        99,                 // Ending frame of loop back.
                                        66,                 // Number of animation stages.
                                        127,                // Number of times the animation loops.
                                        VOC_NONE,           // Sound effect to play.
                                        ANIM_NONE);

static AnimTypeClass const Gunfire(ANIM_MUZZLE_FLASH, // Animation number.
                                   "GUNFIRE",         // Data name of animation.
                                   16,                // Maximum dimension of animation.
                                   0,                 // Biggest animation stage.
                                   false,             // Theater specific art imagery?
                                   false,             // Normalized animation rate?
                                   false,             // Uses white translucent table?
                                   false,             // Scorches the ground?
                                   false,             // Forms a crater?
                                   false,             // Sticks to unit in square?
                                   true,              // Ground level animation?
                                   true,              // Translucent colors in this animation?
                                   false,             // Is this a flame thrower animation?
                                   0,                 // Damage to apply per tick (fixed point).
                                   1,                 // Delay between frames.
                                   0,                 // Starting frame number.
                                   0,                 // Loop start frame number.
                                   0,                 // Number of times the animation loops.
                                   1,                 // Number of animation stages.
                                   1,                 // Ending frame of loop back.
                                   VOC_NONE,          // Sound effect to play.
                                   ANIM_NONE,
                                   10 // Virtual stages
);

static AnimTypeClass const SmokeM(ANIM_SMOKE_M, // Animation number.
                                  "SMOKE_M",    // Data name of animation.
                                  28,           // Maximum dimension of animation.
                                  30,           // Biggest animation stage.
                                  false,        // Theater specific art imagery?
                                  true,         // Normalized animation rate?
                                  false,        // Uses white translucent table?
                                  false,        // Scorches the ground?
                                  false,        // Forms a crater?
                                  false,        // Sticks to unit in square?
                                  true,         // Ground level animation?
                                  false,        // Translucent colors in this animation?
                                  false,        // Is this a flame thrower animation?
                                  0,            // Damage to apply per tick (fixed point).
                                  1,            // Delay between frames.
                                  0,            // Starting frame number.
                                  67,           // Loop start frame number.
                                  -1,           // Loopback frame number.
                                  -1,           // Number of animation stages.
                                  6,            // Number of times the animation loops.
                                  VOC_NONE,     // Sound effect to play.
                                  ANIM_NONE,
                                  105 // Virtual stages
);

/*
**	Mini-gun fire effect -- used by guard towers.
*/
static AnimTypeClass const GUNN(ANIM_GUN_N, // Animation number.
                                "MINIGUN",  // Data name of animation.
                                18,         // Maximum dimension of animation.
                                0,          // Biggest animation stage.
                                false,      // Theater specific art imagery?
                                false,      // Normalized animation rate?
                                false,      // Uses white translucent table?
                                false,      // Scorches the ground?
                                false,      // Forms a crater?
                                false,      // Sticks to unit in square?
                                false,      // Ground level animation?
                                false,      // Translucent colors in this animation?
                                false,      // Is this a flame thrower animation?
                                0,          // Damage to apply per tick (fixed point).
                                1,          // Delay between frames.
                                0,          // Starting frame number.
                                0,          // Loop start frame number.
                                0,          // Number of times the animation loops.
                                6,          // Number of animation stages.
                                0,          // Ending frame of loop back.
                                VOC_NONE,   // Sound effect to play.
                                ANIM_NONE);
static AnimTypeClass const GUNNW(ANIM_GUN_NW, // Animation number.
                                 "MINIGUN",   // Data name of animation.
                                 18,          // Maximum dimension of animation.
                                 0,           // Biggest animation stage.
                                 false,       // Theater specific art imagery?
                                 false,       // Normalized animation rate?
                                 false,       // Uses white translucent table?
                                 false,       // Scorches the ground?
                                 false,       // Forms a crater?
                                 false,       // Sticks to unit in square?
                                 false,       // Ground level animation?
                                 false,       // Translucent colors in this animation?
                                 false,       // Is this a flame thrower animation?
                                 0,           // Damage to apply per tick (fixed point).
                                 1,           // Delay between frames.
                                 6,           // Starting frame number.
                                 0,           // Loop start frame number.
                                 0,           // Number of times the animation loops.
                                 6,           // Number of animation stages.
                                 0,           // Ending frame of loop back.
                                 VOC_NONE,    // Sound effect to play.
                                 ANIM_NONE);
static AnimTypeClass const GUNW(ANIM_GUN_W, // Animation number.
                                "MINIGUN",  // Data name of animation.
                                18,         // Maximum dimension of animation.
                                0,          // Biggest animation stage.
                                false,      // Theater specific art imagery?
                                false,      // Normalized animation rate?
                                false,      // Uses white translucent table?
                                false,      // Scorches the ground?
                                false,      // Forms a crater?
                                false,      // Sticks to unit in square?
                                false,      // Ground level animation?
                                false,      // Translucent colors in this animation?
                                false,      // Is this a flame thrower animation?
                                0,          // Damage to apply per tick (fixed point).
                                1,          // Delay between frames.
                                12,         // Starting frame number.
                                0,          // Loop start frame number.
                                0,          // Number of times the animation loops.
                                6,          // Number of animation stages.
                                0,          // Ending frame of loop back.
                                VOC_NONE,   // Sound effect to play.
                                ANIM_NONE);
static AnimTypeClass const GUNSW(ANIM_GUN_SW, // Animation number.
                                 "MINIGUN",   // Data name of animation.
                                 18,          // Maximum dimension of animation.
                                 0,           // Biggest animation stage.
                                 false,       // Theater specific art imagery?
                                 false,       // Normalized animation rate?
                                 false,       // Uses white translucent table?
                                 false,       // Scorches the ground?
                                 false,       // Forms a crater?
                                 false,       // Sticks to unit in square?
                                 false,       // Ground level animation?
                                 false,       // Translucent colors in this animation?
                                 false,       // Is this a flame thrower animation?
                                 0,           // Damage to apply per tick (fixed point).
                                 1,           // Delay between frames.
                                 18,          // Starting frame number.
                                 0,           // Loop start frame number.
                                 0,           // Number of times the animation loops.
                                 6,           // Number of animation stages.
                                 0,           // Ending frame of loop back.
                                 VOC_NONE,    // Sound effect to play.
                                 ANIM_NONE);
static AnimTypeClass const GUNS(ANIM_GUN_S, // Animation number.
                                "MINIGUN",  // Data name of animation.
                                18,         // Maximum dimension of animation.
                                0,          // Biggest animation stage.
                                false,      // Theater specific art imagery?
                                false,      // Normalized animation rate?
                                false,      // Uses white translucent table?
                                false,      // Scorches the ground?
                                false,      // Forms a crater?
                                false,      // Sticks to unit in square?
                                false,      // Ground level animation?
                                false,      // Translucent colors in this animation?
                                false,      // Is this a flame thrower animation?
                                0,          // Damage to apply per tick (fixed point).
                                1,          // Delay between frames.
                                24,         // Starting frame number.
                                0,          // Loop start frame number.
                                0,          // Number of times the animation loops.
                                6,          // Number of animation stages.
                                0,          // Ending frame of loop back.
                                VOC_NONE,   // Sound effect to play.
                                ANIM_NONE);
static AnimTypeClass const GUNSE(ANIM_GUN_SE, // Animation number.
                                 "MINIGUN",   // Data name of animation.
                                 18,          // Maximum dimension of animation.
                                 0,           // Biggest animation stage.
                                 false,       // Theater specific art imagery?
                                 false,       // Normalized animation rate?
                                 false,       // Uses white translucent table?
                                 false,       // Scorches the ground?
                                 false,       // Forms a crater?
                                 false,       // Sticks to unit in square?
                                 false,       // Ground level animation?
                                 false,       // Translucent colors in this animation?
                                 false,       // Is this a flame thrower animation?
                                 0,           // Damage to apply per tick (fixed point).
                                 1,           // Delay between frames.
                                 30,          // Starting frame number.
                                 0,           // Loop start frame number.
                                 0,           // Number of times the animation loops.
                                 6,           // Number of animation stages.
                                 0,           // Ending frame of loop back.
                                 VOC_NONE,    // Sound effect to play.
                                 ANIM_NONE);
static AnimTypeClass const GUNE(ANIM_GUN_E, // Animation number.
                                "MINIGUN",  // Data name of animation.
                                18,         // Maximum dimension of animation.
                                0,          // Biggest animation stage.
                                false,      // Theater specific art imagery?
                                false,      // Normalized animation rate?
                                false,      // Uses white translucent table?
                                false,      // Scorches the ground?
                                false,      // Forms a crater?
                                false,      // Sticks to unit in square?
                                false,      // Ground level animation?
                                false,      // Translucent colors in this animation?
                                false,      // Is this a flame thrower animation?
                                0,          // Damage to apply per tick (fixed point).
                                1,          // Delay between frames.
                                36,         // Starting frame number.
                                0,          // Loop start frame number.
                                0,          // Number of times the animation loops.
                                6,          // Number of animation stages.
                                0,          // Ending frame of loop back.
                                VOC_NONE,   // Sound effect to play.
                                ANIM_NONE);
static AnimTypeClass const GUNNE(ANIM_GUN_NE, // Animation number.
                                 "MINIGUN",   // Data name of animation.
                                 18,          // Maximum dimension of animation.
                                 0,           // Biggest animation stage.
                                 false,       // Theater specific art imagery?
                                 false,       // Normalized animation rate?
                                 false,       // Uses white translucent table?
                                 false,       // Scorches the ground?
                                 false,       // Forms a crater?
                                 false,       // Sticks to unit in square?
                                 false,       // Ground level animation?
                                 false,       // Translucent colors in this animation?
                                 false,       // Is this a flame thrower animation?
                                 0,           // Damage to apply per tick (fixed point).
                                 1,           // Delay between frames.
                                 42,          // Starting frame number.
                                 0,           // Loop start frame number.
                                 0,           // Number of times the animation loops.
                                 6,           // Number of animation stages.
                                 0,           // Ending frame of loop back.
                                 VOC_NONE,    // Sound effect to play.
                                 ANIM_NONE);
static AnimTypeClass const CDeviator(ANIM_CRATE_DEVIATOR, // Animation number.
                                     "DEVIATOR",          // Data name of animation.
                                     48,                  // Maximum dimension of animation.
                                     0,                   // Biggest animation stage.
                                     false,               // Theater specific art imagery?
                                     true,                // Normalized animation rate?
                                     false,               // Uses white translucent table?
                                     false,               // Scorches the ground?
                                     false,               // Forms a crater?
                                     false,               // Sticks to unit in square?
                                     false,               // Ground level animation?
                                     false,               // Translucent colors in this animation?
                                     false,               // Is this a flame thrower animation?
                                     0,                   // Damage to apply per tick (fixed point).
                                     2,                   // Delay between frames.
                                     0,                   // Starting frame number.
                                     0,                   // Loop start frame number.
                                     0,                   // Ending frame of loop back.
                                     -1,                  // Number of animation stages.
                                     0,                   // Number of times the animation loops.
                                     VOC_NONE,            // Sound effect to play.
                                     ANIM_NONE            // Follow up animation.
);

static AnimTypeClass const CrateArmor(ANIM_CRATE_ARMOR, // Animation number.
                                      "ARMOR",          // Data name of animation.
                                      48,               // Maximum dimension of animation.
                                      0,                // Biggest animation stage.
                                      false,            // Theater specific art imagery?
                                      true,             // Normalized animation rate?
                                      false,            // Uses white translucent table?
                                      false,            // Scorches the ground?
                                      false,            // Forms a crater?
                                      false,            // Sticks to unit in square?
                                      false,            // Ground level animation?
                                      false,            // Translucent colors in this animation?
                                      false,            // Is this a flame thrower animation?
                                      0,                // Damage to apply per tick (fixed point).
                                      2,                // Delay between frames.
                                      0,                // Starting frame number.
                                      0,                // Loop start frame number.
                                      0,                // Ending frame of loop back.
                                      -1,               // Number of animation stages.
                                      0,                // Number of times the animation loops.
                                      VOC_NONE,         // Sound effect to play.
                                      ANIM_NONE         // Follow up animation.
);
static AnimTypeClass const CrateSpeed(ANIM_CRATE_SPEED, // Animation number.
                                      "SPEED",          // Data name of animation.
                                      48,               // Maximum dimension of animation.
                                      0,                // Biggest animation stage.
                                      false,            // Theater specific art imagery?
                                      true,             // Normalized animation rate?
                                      false,            // Uses white translucent table?
                                      false,            // Scorches the ground?
                                      false,            // Forms a crater?
                                      false,            // Sticks to unit in square?
                                      false,            // Ground level animation?
                                      false,            // Translucent colors in this animation?
                                      false,            // Is this a flame thrower animation?
                                      0,                // Damage to apply per tick (fixed point).
                                      2,                // Delay between frames.
                                      0,                // Starting frame number.
                                      0,                // Loop start frame number.
                                      0,                // Ending frame of loop back.
                                      -1,               // Number of animation stages.
                                      0,                // Number of times the animation loops.
                                      VOC_NONE,         // Sound effect to play.
                                      ANIM_NONE         // Follow up animation.
);

static AnimTypeClass const CrateFPower(ANIM_CRATE_FPOWER, // Animation number.
                                       "FPOWER",          // Data name of animation.
                                       48,                // Maximum dimension of animation.
                                       0,                 // Biggest animation stage.
                                       false,             // Theater specific art imagery?
                                       true,              // Normalized animation rate?
                                       false,             // Uses white translucent table?
                                       false,             // Scorches the ground?
                                       false,             // Forms a crater?
                                       false,             // Sticks to unit in square?
                                       false,             // Ground level animation?
                                       false,             // Translucent colors in this animation?
                                       false,             // Is this a flame thrower animation?
                                       0,                 // Damage to apply per tick (fixed point).
                                       2,                 // Delay between frames.
                                       0,                 // Starting frame number.
                                       0,                 // Loop start frame number.
                                       0,                 // Ending frame of loop back.
                                       -1,                // Number of animation stages.
                                       0,                 // Number of times the animation loops.
                                       VOC_NONE,          // Sound effect to play.
                                       ANIM_NONE          // Follow up animation.
);
static AnimTypeClass const CrateTQuake(ANIM_CRATE_TQUAKE, // Animation number.
                                       "TQUAKE",          // Data name of animation.
                                       48,                // Maximum dimension of animation.
                                       0,                 // Biggest animation stage.
                                       false,             // Theater specific art imagery?
                                       true,              // Normalized animation rate?
                                       false,             // Uses white translucent table?
                                       false,             // Scorches the ground?
                                       false,             // Forms a crater?
                                       false,             // Sticks to unit in square?
                                       false,             // Ground level animation?
                                       false,             // Translucent colors in this animation?
                                       false,             // Is this a flame thrower animation?
                                       0,                 // Damage to apply per tick (fixed point).
                                       2,                 // Delay between frames.
                                       0,                 // Starting frame number.
                                       0,                 // Loop start frame number.
                                       0,                 // Ending frame of loop back.
                                       -1,                // Number of animation stages.
                                       0,                 // Number of times the animation loops.
                                       VOC_NONE,          // Sound effect to play.
                                       ANIM_NONE          // Follow up animation.
);

static AnimTypeClass const CDollar(ANIM_CRATE_DOLLAR, // Animation number.
                                   "DOLLAR",          // Data name of animation.
                                   48,                // Maximum dimension of animation.
                                   0,                 // Biggest animation stage.
                                   false,             // Theater specific art imagery?
                                   true,              // Normalized animation rate?
                                   false,             // Uses white translucent table?
                                   false,             // Scorches the ground?
                                   false,             // Forms a crater?
                                   false,             // Sticks to unit in square?
                                   false,             // Ground level animation?
                                   false,             // Translucent colors in this animation?
                                   false,             // Is this a flame thrower animation?
                                   0,                 // Damage to apply per tick (fixed point).
                                   2,                 // Delay between frames.
                                   0,                 // Starting frame number.
                                   0,                 // Loop start frame number.
                                   0,                 // Ending frame of loop back.
                                   -1,                // Number of animation stages.
                                   0,                 // Number of times the animation loops.
                                   VOC_NONE,          // Sound effect to play.
                                   ANIM_NONE          // Follow up animation.
);
static AnimTypeClass const CEarth(ANIM_CRATE_EARTH, // Animation number.
                                  "EARTH",          // Data name of animation.
                                  48,               // Maximum dimension of animation.
                                  0,                // Biggest animation stage.
                                  false,            // Theater specific art imagery?
                                  true,             // Normalized animation rate?
                                  false,            // Uses white translucent table?
                                  false,            // Scorches the ground?
                                  false,            // Forms a crater?
                                  false,            // Sticks to unit in square?
                                  false,            // Ground level animation?
                                  false,            // Translucent colors in this animation?
                                  false,            // Is this a flame thrower animation?
                                  0,                // Damage to apply per tick (fixed point).
                                  2,                // Delay between frames.
                                  0,                // Starting frame number.
                                  0,                // Loop start frame number.
                                  0,                // Ending frame of loop back.
                                  -1,               // Number of animation stages.
                                  0,                // Number of times the animation loops.
                                  VOC_NONE,         // Sound effect to play.
                                  ANIM_NONE         // Follow up animation.
);
static AnimTypeClass const CEmpulse(ANIM_CRATE_EMPULSE, // Animation number.
                                    "EMPULSE",          // Data name of animation.
                                    48,                 // Maximum dimension of animation.
                                    0,                  // Biggest animation stage.
                                    false,              // Theater specific art imagery?
                                    true,               // Normalized animation rate?
                                    false,              // Uses white translucent table?
                                    false,              // Scorches the ground?
                                    false,              // Forms a crater?
                                    false,              // Sticks to unit in square?
                                    false,              // Ground level animation?
                                    false,              // Translucent colors in this animation?
                                    false,              // Is this a flame thrower animation?
                                    0,                  // Damage to apply per tick (fixed point).
                                    2,                  // Delay between frames.
                                    0,                  // Starting frame number.
                                    0,                  // Loop start frame number.
                                    0,                  // Ending frame of loop back.
                                    -1,                 // Number of animation stages.
                                    0,                  // Number of times the animation loops.
                                    VOC_NONE,           // Sound effect to play.
                                    ANIM_NONE           // Follow up animation.
);
static AnimTypeClass const CInvun(ANIM_CRATE_INVUN, // Animation number.
                                  "INVUN",          // Data name of animation.
                                  48,               // Maximum dimension of animation.
                                  0,                // Biggest animation stage.
                                  false,            // Theater specific art imagery?
                                  true,             // Normalized animation rate?
                                  false,            // Uses white translucent table?
                                  false,            // Scorches the ground?
                                  false,            // Forms a crater?
                                  false,            // Sticks to unit in square?
                                  false,            // Ground level animation?
                                  false,            // Translucent colors in this animation?
                                  false,            // Is this a flame thrower animation?
                                  0,                // Damage to apply per tick (fixed point).
                                  2,                // Delay between frames.
                                  0,                // Starting frame number.
                                  0,                // Loop start frame number.
                                  0,                // Ending frame of loop back.
                                  -1,               // Number of animation stages.
                                  0,                // Number of times the animation loops.
                                  VOC_NONE,         // Sound effect to play.
                                  ANIM_NONE         // Follow up animation.
);
static AnimTypeClass const CMine(ANIM_CRATE_MINE, // Animation number.
                                 "MINE",          // Data name of animation.
                                 48,              // Maximum dimension of animation.
                                 0,               // Biggest animation stage.
                                 false,           // Theater specific art imagery?
                                 true,            // Normalized animation rate?
                                 false,           // Uses white translucent table?
                                 false,           // Scorches the ground?
                                 false,           // Forms a crater?
                                 false,           // Sticks to unit in square?
                                 false,           // Ground level animation?
                                 false,           // Translucent colors in this animation?
                                 false,           // Is this a flame thrower animation?
                                 0,               // Damage to apply per tick (fixed point).
                                 2,               // Delay between frames.
                                 0,               // Starting frame number.
                                 0,               // Loop start frame number.
                                 0,               // Ending frame of loop back.
                                 -1,              // Number of animation stages.
                                 0,               // Number of times the animation loops.
                                 VOC_NONE,        // Sound effect to play.
                                 ANIM_NONE        // Follow up animation.
);
static AnimTypeClass const CRapid(ANIM_CRATE_RAPID, // Animation number.
                                  "RAPID",          // Data name of animation.
                                  48,               // Maximum dimension of animation.
                                  0,                // Biggest animation stage.
                                  false,            // Theater specific art imagery?
                                  true,             // Normalized animation rate?
                                  false,            // Uses white translucent table?
                                  false,            // Scorches the ground?
                                  false,            // Forms a crater?
                                  false,            // Sticks to unit in square?
                                  false,            // Ground level animation?
                                  false,            // Translucent colors in this animation?
                                  false,            // Is this a flame thrower animation?
                                  0,                // Damage to apply per tick (fixed point).
                                  2,                // Delay between frames.
                                  0,                // Starting frame number.
                                  0,                // Loop start frame number.
                                  0,                // Ending frame of loop back.
                                  -1,               // Number of animation stages.
                                  0,                // Number of times the animation loops.
                                  VOC_NONE,         // Sound effect to play.
                                  ANIM_NONE         // Follow up animation.
);
static AnimTypeClass const CStealth(ANIM_CRATE_STEALTH, // Animation number.
                                    "STEALTH2",         // Data name of animation.
                                    48,                 // Maximum dimension of animation.
                                    0,                  // Biggest animation stage.
                                    false,              // Theater specific art imagery?
                                    true,               // Normalized animation rate?
                                    false,              // Uses white translucent table?
                                    false,              // Scorches the ground?
                                    false,              // Forms a crater?
                                    false,              // Sticks to unit in square?
                                    false,              // Ground level animation?
                                    false,              // Translucent colors in this animation?
                                    false,              // Is this a flame thrower animation?
                                    0,                  // Damage to apply per tick (fixed point).
                                    2,                  // Delay between frames.
                                    0,                  // Starting frame number.
                                    0,                  // Loop start frame number.
                                    0,                  // Ending frame of loop back.
                                    -1,                 // Number of animation stages.
                                    0,                  // Number of times the animation loops.
                                    VOC_NONE,           // Sound effect to play.
                                    ANIM_NONE           // Follow up animation.
);
static AnimTypeClass const ChronoBox(ANIM_CHRONO_BOX, // Animation number.
                                     "CHRONBOX",      // Data name of animation.
                                     48,              // Maximum dimension of animation.
                                     0,               // Biggest animation stage.
                                     false,           // Theater specific art imagery?
                                     true,            // Normalized animation rate?
                                     false,           // Uses white translucent table?
                                     false,           // Scorches the ground?
                                     false,           // Forms a crater?
                                     false,           // Sticks to unit in square?
                                     false,           // Ground level animation?
                                     false,           // Translucent colors in this animation?
                                     false,           // Is this a flame thrower animation?
                                     0,               // Damage to apply per tick (fixed point).
                                     2,               // Delay between frames.
                                     0,               // Starting frame number.
                                     0,               // Loop start frame number.
                                     0,               // Ending frame of loop back.
                                     -1,              // Number of animation stages.
                                     0,               // Number of times the animation loops.
                                     VOC_NONE,        // Sound effect to play.
                                     ANIM_NONE        // Follow up animation.
);
static AnimTypeClass const GPSBox(ANIM_GPS_BOX, // Animation number.
                                  "GPSBOX",     // Data name of animation.
                                  48,           // Maximum dimension of animation.
                                  0,            // Biggest animation stage.
                                  false,        // Theater specific art imagery?
                                  true,         // Normalized animation rate?
                                  false,        // Uses white translucent table?
                                  false,        // Scorches the ground?
                                  false,        // Forms a crater?
                                  false,        // Sticks to unit in square?
                                  false,        // Ground level animation?
                                  false,        // Translucent colors in this animation?
                                  false,        // Is this a flame thrower animation?
                                  0,            // Damage to apply per tick (fixed point).
                                  2,            // Delay between frames.
                                  0,            // Starting frame number.
                                  0,            // Loop start frame number.
                                  0,            // Ending frame of loop back.
                                  -1,           // Number of animation stages.
                                  0,            // Number of times the animation loops.
                                  VOC_NONE,     // Sound effect to play.
                                  ANIM_NONE     // Follow up animation.
);
static AnimTypeClass const InvulBox(ANIM_INVUL_BOX, // Animation number.
                                    "INVULBOX",     // Data name of animation.
                                    48,             // Maximum dimension of animation.
                                    0,              // Biggest animation stage.
                                    false,          // Theater specific art imagery?
                                    true,           // Normalized animation rate?
                                    false,          // Uses white translucent table?
                                    false,          // Scorches the ground?
                                    false,          // Forms a crater?
                                    false,          // Sticks to unit in square?
                                    false,          // Ground level animation?
                                    false,          // Translucent colors in this animation?
                                    false,          // Is this a flame thrower animation?
                                    0,              // Damage to apply per tick (fixed point).
                                    2,              // Delay between frames.
                                    0,              // Starting frame number.
                                    0,              // Loop start frame number.
                                    0,              // Ending frame of loop back.
                                    -1,             // Number of animation stages.
                                    0,              // Number of times the animation loops.
                                    VOC_NONE,       // Sound effect to play.
                                    ANIM_NONE       // Follow up animation.
);
static AnimTypeClass const ParaBox(ANIM_PARA_BOX, // Animation number.
                                   "PARABOX",     // Data name of animation.
                                   48,            // Maximum dimension of animation.
                                   0,             // Biggest animation stage.
                                   false,         // Theater specific art imagery?
                                   true,          // Normalized animation rate?
                                   false,         // Uses white translucent table?
                                   false,         // Scorches the ground?
                                   false,         // Forms a crater?
                                   false,         // Sticks to unit in square?
                                   false,         // Ground level animation?
                                   false,         // Translucent colors in this animation?
                                   false,         // Is this a flame thrower animation?
                                   0,             // Damage to apply per tick (fixed point).
                                   2,             // Delay between frames.
                                   0,             // Starting frame number.
                                   0,             // Loop start frame number.
                                   0,             // Ending frame of loop back.
                                   -1,            // Number of animation stages.
                                   0,             // Number of times the animation loops.
                                   VOC_NONE,      // Sound effect to play.
                                   ANIM_NONE      // Follow up animation.
);
static AnimTypeClass const SonarBox(ANIM_SONAR_BOX, // Animation number.
                                    "SONARBOX",     // Data name of animation.
                                    48,             // Maximum dimension of animation.
                                    0,              // Biggest animation stage.
                                    false,          // Theater specific art imagery?
                                    true,           // Normalized animation rate?
                                    false,          // Uses white translucent table?
                                    false,          // Scorches the ground?
                                    false,          // Forms a crater?
                                    false,          // Sticks to unit in square?
                                    false,          // Ground level animation?
                                    false,          // Translucent colors in this animation?
                                    false,          // Is this a flame thrower animation?
                                    0,              // Damage to apply per tick (fixed point).
                                    2,              // Delay between frames.
                                    0,              // Starting frame number.
                                    0,              // Loop start frame number.
                                    0,              // Ending frame of loop back.
                                    -1,             // Number of animation stages.
                                    0,              // Number of times the animation loops.
                                    VOC_NONE,       // Sound effect to play.
                                    ANIM_NONE       // Follow up animation.
);

static AnimTypeClass const CMissile(ANIM_CRATE_MISSILE, // Animation number.
                                    "MISSILE2",         // Data name of animation.
                                    48,                 // Maximum dimension of animation.
                                    0,                  // Biggest animation stage.
                                    false,              // Theater specific art imagery?
                                    true,               // Normalized animation rate?
                                    false,              // Uses white translucent table?
                                    false,              // Scorches the ground?
                                    false,              // Forms a crater?
                                    false,              // Sticks to unit in square?
                                    false,              // Ground level animation?
                                    false,              // Translucent colors in this animation?
                                    false,              // Is this a flame thrower animation?
                                    0,                  // Damage to apply per tick (fixed point).
                                    2,                  // Delay between frames.
                                    0,                  // Starting frame number.
                                    0,                  // Loop start frame number.
                                    0,                  // Ending frame of loop back.
                                    -1,                 // Number of animation stages.
                                    0,                  // Number of times the animation loops.
                                    VOC_NONE,           // Sound effect to play.
                                    ANIM_NONE           // Follow up animation.
);

static AnimTypeClass const MoveFlash(ANIM_MOVE_FLASH, // Animation number.
                                     "MOVEFLSH",      // Data name of animation.
                                     24,              // Maximum dimension of animation.
                                     0,               // Biggest animation stage.
                                     true,            // Theater specific art imagery?
                                     true,            // Normalized animation rate?
                                     true,            // Uses white translucent table?
                                     false,           // Scorches the ground?
                                     false,           // Forms a crater?
                                     false,           // Sticks to unit in square?
                                     true,            // Ground level animation?
                                     false,           // Translucent colors in this animation?
                                     false,           // Is this a flame thrower animation?
                                     0,               // Damage to apply per tick (fixed point).
                                     1,               // Delay between frames.
                                     0,               // Starting frame number.
                                     0,               // Loop start frame number.
                                     0,               // Ending frame of loop back.
                                     -1,              // Number of animation stages.
                                     0,               // Number of times the animation loops.
                                     VOC_NONE,        // Sound effect to play.
                                     ANIM_NONE        // Follow up animation.
);

static AnimTypeClass const Corpse1(ANIM_CORPSE1, // Animation number.
                                   "CORPSE1",    // Data name of animation.
                                   24,           // Maximum dimension of animation.
                                   1,            // Biggest animation stage.
                                   true,         // Theater specific art imagery?
                                   true,         // Normalized animation rate?
                                   false,        // Uses white translucent table?
                                   false,        // Scorches the ground?
                                   false,        // Forms a crater?
                                   false,        // Sticks to unit in square?
                                   true,         // Ground level animation?
                                   true,         // Translucent colors in this animation?
                                   false,        // Is this a flame thrower animation?
                                   0,            // Damage to apply per tick (fixed point).
                                   15,           // Delay between frames.
                                   0,            // Starting frame number.
                                   0,            // Loop start frame number.
                                   0,            // Ending frame of loop back.
                                   -1,           // Number of animation stages.
                                   0,            // Number of times the animation loops.
                                   VOC_NONE,     // Sound effect to play.
                                   ANIM_NONE);

static AnimTypeClass const Corpse2(ANIM_CORPSE2, // Animation number.
                                   "CORPSE2",    // Data name of animation.
                                   24,           // Maximum dimension of animation.
                                   1,            // Biggest animation stage.
                                   true,         // Theater specific art imagery?
                                   true,         // Normalized animation rate?
                                   false,        // Uses white translucent table?
                                   false,        // Scorches the ground?
                                   false,        // Forms a crater?
                                   false,        // Sticks to unit in square?
                                   true,         // Ground level animation?
                                   true,         // Translucent colors in this animation?
                                   false,        // Is this a flame thrower animation?
                                   0,            // Damage to apply per tick (fixed point).
                                   15,           // Delay between frames.
                                   0,            // Starting frame number.
                                   0,            // Loop start frame number.
                                   0,            // Ending frame of loop back.
                                   -1,           // Number of animation stages.
                                   0,            // Number of times the animation loops.
                                   VOC_NONE,     // Sound effect to play.
                                   ANIM_NONE);

static AnimTypeClass const Corpse3(ANIM_CORPSE3, // Animation number.
                                   "CORPSE3",    // Data name of animation.
                                   24,           // Maximum dimension of animation.
                                   1,            // Biggest animation stage.
                                   true,         // Theater specific art imagery?
                                   true,         // Normalized animation rate?
                                   false,        // Uses white translucent table?
                                   false,        // Scorches the ground?
                                   false,        // Forms a crater?
                                   false,        // Sticks to unit in square?
                                   true,         // Ground level animation?
                                   true,         // Translucent colors in this animation?
                                   false,        // Is this a flame thrower animation?
                                   0,            // Damage to apply per tick (fixed point).
                                   15,           // Delay between frames.
                                   0,            // Starting frame number.
                                   0,            // Loop start frame number.
                                   0,            // Ending frame of loop back.
                                   -1,           // Number of animation stages.
                                   0,            // Number of times the animation loops.
                                   VOC_NONE,     // Sound effect to play.
                                   ANIM_NONE);

static AnimTypeClass const Twinkle1(ANIM_TWINKLE1, // Animation number.
                                    "TWINKLE1",    // Data name of animation.
                                    8,             // Maximum dimension of animation.
                                    1,             // Biggest animation stage.
                                    false,         // Theater specific art imagery?
                                    true,          // Normalized animation rate?
                                    false,         // Uses white translucent table?
                                    false,         // Scorches the ground?
                                    false,         // Forms a crater?
                                    false,         // Sticks to unit in square?
                                    false,         // Ground level animation?
                                    false,         // Translucent colors in this animation?
                                    false,         // Is this a flame thrower animation?
                                    0,             // Damage to apply per tick (fixed point).
                                    1,             // Delay between frames.
                                    0,             // Starting frame number.
                                    0,             // Loop start frame number.
                                    -1,            // Ending frame of loop back.
                                    -1,            // Number of animation stages.
                                    1,             // Number of times the animation loops.
                                    VOC_NONE,      // Sound effect to play.
                                    ANIM_NONE);
static AnimTypeClass const Twinkle2(ANIM_TWINKLE2, // Animation number.
                                    "TWINKLE2",    // Data name of animation.
                                    8,             // Maximum dimension of animation.
                                    1,             // Biggest animation stage.
                                    false,         // Theater specific art imagery?
                                    true,          // Normalized animation rate?
                                    false,         // Uses white translucent table?
                                    false,         // Scorches the ground?
                                    false,         // Forms a crater?
                                    false,         // Sticks to unit in square?
                                    false,         // Ground level animation?
                                    false,         // Translucent colors in this animation?
                                    false,         // Is this a flame thrower animation?
                                    0,             // Damage to apply per tick (fixed point).
                                    1,             // Delay between frames.
                                    0,             // Starting frame number.
                                    0,             // Loop start frame number.
                                    -1,            // Ending frame of loop back.
                                    -1,            // Number of animation stages.
                                    1,             // Number of times the animation loops.
                                    VOC_NONE,      // Sound effect to play.
                                    ANIM_NONE);
static AnimTypeClass const Twinkle3(ANIM_TWINKLE3, // Animation number.
                                    "TWINKLE3",    // Data name of animation.
                                    8,             // Maximum dimension of animation.
                                    1,             // Biggest animation stage.
                                    false,         // Theater specific art imagery?
                                    true,          // Normalized animation rate?
                                    false,         // Uses white translucent table?
                                    false,         // Scorches the ground?
                                    false,         // Forms a crater?
                                    false,         // Sticks to unit in square?
                                    false,         // Ground level animation?
                                    false,         // Translucent colors in this animation?
                                    false,         // Is this a flame thrower animation?
                                    0,             // Damage to apply per tick (fixed point).
                                    1,             // Delay between frames.
                                    0,             // Starting frame number.
                                    0,             // Loop start frame number.
                                    -1,            // Ending frame of loop back.
                                    -1,            // Number of animation stages.
                                    1,             // Number of times the animation loops.
                                    VOC_NONE,      // Sound effect to play.
                                    ANIM_NONE);
static AnimTypeClass const Flak(ANIM_FLAK, // Animation number.
                                "FLAK",    // Data name of animation.
                                8,         // Maximum dimension of animation.
                                7,         // Biggest animation stage.
                                false,     // Theater specific art imagery?
                                true,      // Normalized animation rate?
                                false,     // Uses white translucent table?
                                false,     // Scorches the ground?
                                false,     // Forms a crater?
                                false,     // Sticks to unit in square?
                                false,     // Ground level animation?
                                false,     // Translucent colors in this animation?
                                false,     // Is this a flame thrower animation?
                                0,         // Damage to apply per tick (fixed point).
                                1,         // Delay between frames.
                                0,         // Starting frame number.
                                0,         // Loop start frame number.
                                -1,        // Ending frame of loop back.
                                -1,        // Number of animation stages.
                                1,         // Number of times the animation loops.
                                VOC_NONE,  // Sound effect to play.
                                ANIM_NONE,
                                17 // Virtual stages
);
static AnimTypeClass const WaterExp1(ANIM_WATER_EXP1, // Animation number.
                                     "H2O_EXP1",      // Data name of animation.
                                     64,              // Maximum dimension of animation.
                                     3,               // Biggest animation stage.
                                     false,           // Theater specific art imagery?
                                     true,            // Normalized animation rate?
                                     false,           // Uses white translucent table?
                                     false,           // Scorches the ground?
                                     false,           // Forms a crater?
                                     false,           // Sticks to unit in square?
                                     true,            // Ground level animation?
                                     false,           // Translucent colors in this animation?
                                     false,           // Is this a flame thrower animation?
                                     0,               // Damage to apply per tick (fixed point).
                                     1,               // Delay between frames.
                                     0,               // Starting frame number.
                                     0,               // Loop start frame number.
                                     -1,              // Ending frame of loop back.
                                     -1,              // Number of animation stages.
                                     1,               // Number of times the animation loops.
                                     VOC_SPLASH,      // Sound effect to play.
                                     ANIM_NONE);
static AnimTypeClass const WaterExp2(ANIM_WATER_EXP2, // Animation number.
                                     "H2O_EXP2",      // Data name of animation.
                                     40,              // Maximum dimension of animation.
                                     3,               // Biggest animation stage.
                                     false,           // Theater specific art imagery?
                                     true,            // Normalized animation rate?
                                     false,           // Uses white translucent table?
                                     false,           // Scorches the ground?
                                     false,           // Forms a crater?
                                     false,           // Sticks to unit in square?
                                     true,            // Ground level animation?
                                     false,           // Translucent colors in this animation?
                                     false,           // Is this a flame thrower animation?
                                     0,               // Damage to apply per tick (fixed point).
                                     1,               // Delay between frames.
                                     0,               // Starting frame number.
                                     0,               // Loop start frame number.
                                     -1,              // Ending frame of loop back.
                                     -1,              // Number of animation stages.
                                     1,               // Number of times the animation loops.
                                     VOC_SPLASH,      // Sound effect to play.
                                     ANIM_NONE);
static AnimTypeClass const WaterExp3(ANIM_WATER_EXP3, // Animation number.
                                     "H2O_EXP3",      // Data name of animation.
                                     32,              // Maximum dimension of animation.
                                     3,               // Biggest animation stage.
                                     false,           // Theater specific art imagery?
                                     true,            // Normalized animation rate?
                                     false,           // Uses white translucent table?
                                     false,           // Scorches the ground?
                                     false,           // Forms a crater?
                                     false,           // Sticks to unit in square?
                                     true,            // Ground level animation?
                                     false,           // Translucent colors in this animation?
                                     false,           // Is this a flame thrower animation?
                                     0,               // Damage to apply per tick (fixed point).
                                     1,               // Delay between frames.
                                     0,               // Starting frame number.
                                     0,               // Loop start frame number.
                                     -1,              // Ending frame of loop back.
                                     -1,              // Number of animation stages.
                                     1,               // Number of times the animation loops.
                                     VOC_SPLASH,      // Sound effect to play.
                                     ANIM_NONE);

static AnimTypeClass const MineExp1(ANIM_MINE_EXP1, // Animation number.
                                    "VEH-HIT2",     // Data name of animation.
                                    21,             // Maximum dimension of animation.
                                    1,              // Biggest animation stage.
                                    false,          // Theater specific art imagery?
                                    true,           // Normalized animation rate?
                                    false,          // Uses white translucent table?
                                    false,          // Scorches the ground?
                                    true,           // Forms a crater?
                                    false,          // Sticks to unit in square?
                                    false,          // Ground level animation?
                                    false,          // Translucent colors in this animation?
                                    false,          // Is this a flame thrower animation?
                                    0,              // Damage to apply per tick (fixed point).
                                    1,              // Delay between frames.
                                    0,              // Starting frame number.
                                    0,              // Loop start frame number.
                                    -1,             // Ending frame of loop back.
                                    -1,             // Number of animation stages.
                                    1,              // Number of times the animation loops.
                                    VOC_MINEBLOW,   // Sound effect to play.
                                    ANIM_NONE);

static AnimTypeClass const Flag(ANIM_FLAG, // Animation number.
                                "FLAGFLY", // Data name of animation.
                                21,        // Maximum dimension of animation.
                                0,         // Biggest animation stage.
                                false,     // Theater specific art imagery?
                                false,     // Normalized animation rate?
                                false,     // Uses white translucent table?
                                false,     // Scorches the ground?
                                false,     // Forms a crater?
                                false,     // Sticks to unit in square?
                                false,     // Ground level animation?
                                false,     // Translucent colors in this animation?
                                false,     // Is this a flame thrower animation?
                                0,         // Damage to apply per tick (fixed point).
                                1,         // Delay between frames.
                                0,         // Starting frame number.
                                0,         // Loop start frame number.
                                -1,        // Ending frame of loop back.
                                -1,        // Number of animation stages.
                                -1,        // Number of times the animation loops.
                                VOC_NONE,  // Sound effect to play.
                                ANIM_NONE);

static AnimTypeClass const Beacon(ANIM_BEACON, // Animation number.
                                  "MOVEFLSH",  // Data name of animation.
                                  21,          // Maximum dimension of animation.
                                  0,           // Biggest animation stage.
                                  true,        // Theater specific art imagery?
                                  false,       // Normalized animation rate?
                                  false,       // Uses white translucent table?
                                  false,       // Scorches the ground?
                                  false,       // Forms a crater?
                                  false,       // Sticks to unit in square?
                                  false,       // Ground level animation?
                                  false,       // Translucent colors in this animation?
                                  false,       // Is this a flame thrower animation?
                                  0,           // Damage to apply per tick (fixed point).
                                  1,           // Delay between frames.
                                  0,           // Starting frame number.
                                  0,           // Loop start frame number.
                                  -1,          // Ending frame of loop back.
                                  1,           // Number of animation stages.
                                  -1,          // Number of times the animation loops.
                                  VOC_NONE,    // Sound effect to play.
                                  ANIM_NONE
#ifdef REMASTER_BUILD
                                  ,
                                  -1,                 // Virtual stages
                                  0x100,              // Virtual scale
                                  NULL,               // Virtual name
                                  ANIM_BEACON_VIRTUAL // Virtual anim
#endif
);

#ifdef REMASTER_BUILD
static AnimTypeClass const BeaconVirtual(ANIM_BEACON_VIRTUAL, // Animation number.
                                         "BEACON",            // Data name of animation.
                                         21,                  // Maximum dimension of animation.
                                         0,                   // Biggest animation stage.
                                         false,               // Theater specific art imagery?
                                         false,               // Normalized animation rate?
                                         false,               // Uses white translucent table?
                                         false,               // Scorches the ground?
                                         false,               // Forms a crater?
                                         false,               // Sticks to unit in square?
                                         false,               // Ground level animation?
                                         false,               // Translucent colors in this animation?
                                         false,               // Is this a flame thrower animation?
                                         0,                   // Damage to apply per tick (fixed point).
                                         1,                   // Delay between frames.
                                         0,                   // Starting frame number.
                                         0,                   // Loop start frame number.
                                         -1,                  // Ending frame of loop back.
                                         1,                   // Number of animation stages.
                                         -1,                  // Number of times the animation loops.
                                         VOC_NONE,            // Sound effect to play.
                                         ANIM_NONE);
#endif

#ifdef FIXIT_ANTS
static AnimTypeClass const Ant1Death(ANIM_ANT1_DEATH, // Animation number.
                                     "ANTDIE",        // Data name of animation.
                                     28,              // Maximum dimension of animation.
                                     1,               // Biggest animation stage.
                                     false,           // Theater specific art imagery?
                                     true,            // Normalized animation rate?
                                     false,           // Uses white translucent table?
                                     false,           // Scorches the ground?
                                     false,           // Forms a crater?
                                     false,           // Sticks to unit in square?
                                     true,            // Ground level animation?
                                     true,            // Translucent colors in this animation?
                                     false,           // Is this a flame thrower animation?
                                     0,               // Damage to apply per tick (fixed point).
                                     4,               // Delay between frames.
                                     0,               // Starting frame number.
                                     0,               // Loop start frame number.
                                     -1,              // Ending frame of loop back.
                                     -1,              // Number of animation stages.
                                     1,               // Number of times the animation loops.
                                     VOC_ANTDIE,      // Sound effect to play.
                                     ANIM_NONE,
                                     -1,
                                     0x100,
                                     "ANTDIE1");

static AnimTypeClass const Ant2Death(ANIM_ANT2_DEATH, // Animation number.
                                     "ANTDIE",        // Data name of animation.
                                     28,              // Maximum dimension of animation.
                                     1,               // Biggest animation stage.
                                     false,           // Theater specific art imagery?
                                     true,            // Normalized animation rate?
                                     false,           // Uses white translucent table?
                                     false,           // Scorches the ground?
                                     false,           // Forms a crater?
                                     false,           // Sticks to unit in square?
                                     true,            // Ground level animation?
                                     true,            // Translucent colors in this animation?
                                     false,           // Is this a flame thrower animation?
                                     0,               // Damage to apply per tick (fixed point).
                                     4,               // Delay between frames.
                                     0,               // Starting frame number.
                                     0,               // Loop start frame number.
                                     -1,              // Ending frame of loop back.
                                     -1,              // Number of animation stages.
                                     1,               // Number of times the animation loops.
                                     VOC_ANTDIE,      // Sound effect to play.
                                     ANIM_NONE,
                                     -1,
                                     0x100,
                                     "ANTDIE2");

static AnimTypeClass const Ant3Death(ANIM_ANT3_DEATH, // Animation number.
                                     "ANTDIE",        // Data name of animation.
                                     28,              // Maximum dimension of animation.
                                     1,               // Biggest animation stage.
                                     false,           // Theater specific art imagery?
                                     true,            // Normalized animation rate?
                                     false,           // Uses white translucent table?
                                     false,           // Scorches the ground?
                                     false,           // Forms a crater?
                                     false,           // Sticks to unit in square?
                                     true,            // Ground level animation?
                                     true,            // Translucent colors in this animation?
                                     false,           // Is this a flame thrower animation?
                                     0,               // Damage to apply per tick (fixed point).
                                     4,               // Delay between frames.
                                     0,               // Starting frame number.
                                     0,               // Loop start frame number.
                                     -1,              // Ending frame of loop back.
                                     -1,              // Number of animation stages.
                                     1,               // Number of times the animation loops.
                                     VOC_ANTDIE,      // Sound effect to play.
                                     ANIM_NONE,
                                     -1,
                                     0x100,
                                     "ANTDIE3");
#endif

/***********************************************************************************************
 * AnimTypeClass::AnimTypeClass -- Constructor for animation types.                            *
 *                                                                                             *
 *    This is the constructor for static objects that elaborate the various animation types    *
 *    allowed in the game. Each animation in the game is of one of these types.                *
 *                                                                                             *
 * INPUT:   see below...                                                                       *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   08/23/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
AnimTypeClass::AnimTypeClass(AnimType anim,
                             char const* name,
                             int size,
                             int biggest,
                             bool istheater,
                             bool isnormal,
                             bool iswhitetrans,
                             bool isscorcher,
                             bool iscrater,
                             bool issticky,
                             bool ground,
                             bool istrans,
                             bool isflame,
                             fixed damage,
                             int delaytime,
                             int start,
                             int loopstart,
                             int loopend,
                             int stages,
                             int loops,
                             VocType soundid,
                             AnimType chainto,
                             int virtualstages,
                             int virtualscale,
                             char const* virtualname,
                             AnimType virtualanim)
    : ObjectTypeClass(RTTI_ANIMTYPE, int(anim), true, true, false, false, true, true, false, TXT_NONE, name)
    , IsNormalized(isnormal)
    , IsGroundLayer(ground)
    , IsTranslucent(istrans)
    , IsWhiteTrans(iswhitetrans)
    , IsFlameThrower(isflame)
    , IsScorcher(isscorcher)
    , IsCraterForming(iscrater)
    , IsSticky(issticky)
    , IsTheater(istheater)
    , Type(anim)
    , Size(size)
    , Biggest(biggest)
    , Damage(damage)
    , Delay(delaytime)
    , Start(start)
    , LoopStart(loopstart)
    , LoopEnd(loopend)
    , Stages(stages)
    , Loops(loops)
    , Sound(soundid)
    , ChainTo(chainto)
    , VirtualStages(virtualstages)
    , VirtualScale(virtualscale)
    , VirtualName(virtualname)
    , VirtualAnim(virtualanim)
{
}

/***********************************************************************************************
 * AnimTypeClass::operator new -- Allocate an animation type object from private pool.         *
 *                                                                                             *
 *    This routine will allocate an animation type class object.                               *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the newly allocated anim type object. If no anim type    *
 *          could be allocated, then NULL is returned.                                         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void* AnimTypeClass::operator new(size_t) noexcept
{
    return (AnimTypes.Alloc());
}

/***********************************************************************************************
 * AnimTypeClass::operator delete -- Returns an anim type class object back to the pool.       *
 *                                                                                             *
 *    This will return the anim type class object back to the memory pool from whence it was   *
 *    previously allocated.                                                                    *
 *                                                                                             *
 * INPUT:   pointer  -- Pointer to the anim type class object to return to the memory pool.    *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void AnimTypeClass::operator delete(void* pointer)
{
    AnimTypes.Free((AnimTypeClass*)pointer);
}

/***********************************************************************************************
 * AnimTypeClass::Init_Heap -- Initialize the animation type system.                           *
 *                                                                                             *
 *    This routine is called to initialize the animation type class heap. It allocates all     *
 *    known animation types.                                                                   *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/09/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
// TD Flamethrower muzzle jets (ANIM_FLAME_*), ported from TD's FlameN..: eight in Dir_Facing order, as techno.cpp
// spawns ANIM_FLAME_N + Dir_Facing. They draw TD's FLAME-<dir> art through the RA_VFX.XML tiles.
static AnimTypeClass const FlameN(ANIM_FLAME_N, "TDFLAME-N", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const FlameNE(ANIM_FLAME_NE, "TDFLAME-NE", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const FlameE(ANIM_FLAME_E, "TDFLAME-E", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const FlameSE(ANIM_FLAME_SE, "TDFLAME-SE", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const FlameS(ANIM_FLAME_S, "TDFLAME-S", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const FlameSW(ANIM_FLAME_SW, "TDFLAME-SW", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const FlameW(ANIM_FLAME_W, "TDFLAME-W", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const FlameNW(ANIM_FLAME_NW, "TDFLAME-NW", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);

// TD Flame Tank muzzle jets (ANIM_TDFTFLAME_*): the Flamethrower's jets with their own FTFLAME-<dir> art, seated on
// the tank's twin nozzles (RA_VFX.XML tiles), so the tank's flame is placed apart from the trooper's.
static AnimTypeClass const TdftFlameN(ANIM_TDFTFLAME_N, "FTFLAME-N", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const TdftFlameNE(ANIM_TDFTFLAME_NE, "FTFLAME-NE", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const TdftFlameE(ANIM_TDFTFLAME_E, "FTFLAME-E", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const TdftFlameSE(ANIM_TDFTFLAME_SE, "FTFLAME-SE", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const TdftFlameS(ANIM_TDFTFLAME_S, "FTFLAME-S", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const TdftFlameSW(ANIM_TDFTFLAME_SW, "FTFLAME-SW", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const TdftFlameW(ANIM_TDFTFLAME_W, "FTFLAME-W", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const TdftFlameNW(ANIM_TDFTFLAME_NW, "FTFLAME-NW", 48, 9, false, false, false, false, false, false, false, false, true, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);

// Green Tiberium fumes over an RA refinery while a TD or TS harvester offloads: the LZ smoke art as its own type, so
// it skips ANIM_LZ_SMOKE's map reveal, looping 15 times for about one unload.
static AnimTypeClass const TibFumes(ANIM_TIB_FUMES, // Animation number.
                                    "SMOKLAND",     // Data name of animation (green LZ smoke art).
                                    32,             // Maximum dimension of animation.
                                    72,             // Biggest animation stage.
                                    false,          // Theater specific art imagery?
                                    true,           // Normalized animation rate?
                                    false,          // Uses white translucent table?
                                    false,          // Scorches the ground?
                                    false,          // Forms a crater?
                                    false,          // Sticks to unit in square?
                                    false,          // Ground level animation?
                                    false,          // Translucent colors in this animation?
                                    false,          // Is this a flame thrower animation?
                                    0,              // Damage to apply per tick (fixed point).
                                    2,              // Delay between frames.
                                    0,              // Starting frame number.
                                    72,             // Loop start frame number.
                                    91,             // Ending frame of loop back.
                                    -1,             // Number of animation stages.
                                    15,             // Number of times the animation loops (~one full unload).
                                    VOC_NONE,       // Sound effect to play.
                                    ANIM_NONE);

// TD Chem Warrior spray jets (ANIM_CHEM_*), ported from TD's ChemN..: the flame jets with IsFlameThrower false, as in
// TD. They draw the bundled TDCHEM-<dir> tiles through One_Time's donor ImageData.
static AnimTypeClass const ChemN(ANIM_CHEM_N, "TDCHEM-N", 48, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const ChemNE(ANIM_CHEM_NE, "TDCHEM-NE", 48, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const ChemE(ANIM_CHEM_E, "TDCHEM-E", 48, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const ChemSE(ANIM_CHEM_SE, "TDCHEM-SE", 48, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const ChemS(ANIM_CHEM_S, "TDCHEM-S", 48, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const ChemSW(ANIM_CHEM_SW, "TDCHEM-SW", 48, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const ChemW(ANIM_CHEM_W, "TDCHEM-W", 48, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);
static AnimTypeClass const ChemNW(ANIM_CHEM_NW, "TDCHEM-NW", 48, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x200);

// TS railgun spark (ANIM_RAILFX), a [LargeRailgunPart] particle of the Mk. II's coil: TF_Railgun_Coil lays it and
// AnimClass::Rail_Spark_AI moves, stages and ends it. Art from scripts/ts_gen_railfx.py, blue fading to grey.
static AnimTypeClass const RailFx(ANIM_RAILFX, "RAILFX", 24, 3, false, false, false, false, false, false, false, false, false, 0, 4, 0, 0, 0, 12, 0, VOC_NONE, ANIM_NONE, 12, 0x100);

// TS light railgun spark (ANIM_TS_RAILFXS), the Ghost Stalker's coil: a [SmallRailgunPart] particle run like RAILFX,
// (200,200,200) fading to (150,150,150). Art from scripts/ts_gen_railfx.py.
static AnimTypeClass const TsRailFxS(ANIM_TS_RAILFXS, "TSRAILFXS", 24, 3, false, false, false, false, false, false, false, false, false, 0, 4, 0, 0, 0, 12, 0, VOC_NONE, ANIM_NONE, 12, 0x100);

// TS S_BANG34 (ANIM_TS_SBANG34), TS [General] InfantryExplode: the burst of a jumpjet shot down in the air.
// art.ini [S_BANG34]: Normalized, Translucent, Crater, Scorch, Report=EXPNEW10.
static AnimTypeClass const TsSBang34(ANIM_TS_SBANG34, "TSBANG34", 17, 5, false, true, false, true, true, false, false, true, false, 0, 2, 0, 0, 0, 13, 0, VOC_TS_EXPNEW10, ANIM_NONE, 13, 0x100);
// The EMP Cannon's E.M. Pulse (docs/emp-cannon-design.md): TSPULSBL charges at the barrel, and TSPULSF1 or TSPULSF2,
// picked at random as TS does, lies flat at the landing. Art from scripts/ts_pack_emp.py.
static AnimTypeClass const TsPulsBall(ANIM_TS_PULSBALL, "TSPULSBL", 8, 4, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 23, 0, VOC_NONE, ANIM_NONE, 23, 0x100);
static AnimTypeClass const TsFsIdle(ANIM_TS_FSIDLE, "TSFSIDLE", 136, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 19, 0, VOC_NONE, ANIM_NONE, 19, 0x100);
static AnimTypeClass const TsFsGrnd(ANIM_TS_FSGRND, "TSFSGRND", 66, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 19, 0, VOC_NONE, ANIM_NONE, 19, 0x100);
static AnimTypeClass const TsFsAir(ANIM_TS_FSAIR, "TSFSAIR", 28, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 19, 0, VOC_NONE, ANIM_NONE, 19, 0x100);
static AnimTypeClass const TsMEmpFx(ANIM_TS_MEMPFX, "TSMEMPFX", 144, 6, false, false, false, false, false, false, true, false, false, 0, 1, 0, 0, 0, 12, 0, VOC_NONE, ANIM_NONE, 12, 0x100);
static AnimTypeClass const TsPulseFx1(ANIM_TS_PULSEFX1, "TSPULSF1", 152, 44, false, false, false, false, false, false, true, false, false, 0, 1, 0, 0, 0, 21, 0, VOC_NONE, ANIM_NONE, 21, 0x100);
static AnimTypeClass const TsPulseFx2(ANIM_TS_PULSEFX2, "TSPULSF2", 152, 44, false, false, false, false, false, false, true, false, false, 0, 1, 0, 0, 0, 15, 0, VOC_NONE, ANIM_NONE, 15, 0x100);
static AnimTypeClass const TsEmpFx(ANIM_TS_EMPFX, "TSEMPFX", 20, 9, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 27, 27, -1, VOC_NONE, ANIM_NONE, 27, 0x100);

// TS subterranean dig mound (ANIM_TS_DIG), TS [AudioVisual] Dig=DIG, thrown up as a vehicle digs in and surfaces.
// Not ground-layer: it draws over the hull so the mound swallows the nose (docs/subterranean-design.md).
static AnimTypeClass const TsDig(ANIM_TS_DIG, "TSDIG", 64, 18, false, false, false, false, false, false, false, false, false, 0, 1, 0, 0, 0, 37, 0, VOC_NONE, ANIM_NONE, 37, 0x100);

// TS Ion Cannon strike (SPC_TS_ION_CANNON): the beam deals all its damage (AnimClass::Middle); the ring is TS's
// IonBlast=RING1 flash. Art from scripts/ts_pack_ion.py, the beam pre-tiled, as the launcher can't tile anims.
static AnimTypeClass const TsIonBeam(ANIM_TS_ION_BEAM, "TSIONBM", 48, 11, false, false, false, true, true, false, false, false, false, 0, 2, 0, 0, 0, 15, 0, VOC_TS_ION1, ANIM_NONE, 15, 0x100);
static AnimTypeClass const TsIonRing(ANIM_TS_ION_RING, "TSIONRNG", 48, 7, false, false, false, false, false, false, true, false, false, 0, 1, 0, 0, 0, 15, 0, VOC_NONE, ANIM_NONE, 15, 0x100);

// TS Drop Pod strike (SPC_TS_DROPPODS, OpenTS droppod.cpp), art from scripts/ts_pack_pods.py. The husks lie on the
// ground layer for 5 loops, so the trooper walks over its pod; the falling pod lays SMOKEY every 6 frames.
static AnimTypeClass const TsDropPod1(ANIM_TS_DROPPOD1, "TSDPOD1", 24, 4, false, false, false, false, false, false, true, false, false, 0, 4, 0, 0, 0, 8, 5, VOC_NONE, ANIM_NONE, 8, 0x100);
static AnimTypeClass const TsDropPod2(ANIM_TS_DROPPOD2, "TSDPOD2", 24, 4, false, false, false, false, false, false, true, false, false, 0, 4, 0, 0, 0, 8, 5, VOC_NONE, ANIM_NONE, 8, 0x100);
static AnimTypeClass const TsDropExp(ANIM_TS_DROPEXP, "TSDRPEXP", 50, 6, false, false, false, false, false, false, false, false, false, 0, 2, 0, 0, 0, 12, 0, VOC_NONE, ANIM_NONE, 12, 0x100);
static AnimTypeClass const TsPodRing(ANIM_TS_PODRING, "TSPODRNG", 50, 10, false, false, false, false, false, false, true, false, false, 0, 1, 0, 0, 0, 20, 0, VOC_NONE, ANIM_NONE, 20, 0x100);
static AnimTypeClass const TsSmokey(ANIM_TS_SMOKEY, "TSSMOKEY", 16, 5, false, false, false, false, false, false, false, false, false, 0, 2, 0, 0, 0, 11, 0, VOC_NONE, ANIM_NONE, 11, 0x100);

// TS component tower weapon art (scripts/ts_pack_towerfx.py): the Vulcan's MGUN flash per facing, the tower
// warheads' impacts with art.ini's flags and Report= sounds, and the SAM missile's SMOKEY2 trail.
static AnimTypeClass const TsMgunN(ANIM_TS_MGUN_N, "TSMGUNN", 9, 0, false, false, false, false, false, false, false, false, false, 0, 2, 0, 0, 0, 3, 0, VOC_NONE, ANIM_NONE, 3, 0x100);
static AnimTypeClass const TsMgunNE(ANIM_TS_MGUN_NE, "TSMGUNNE", 9, 0, false, false, false, false, false, false, false, false, false, 0, 2, 0, 0, 0, 3, 0, VOC_NONE, ANIM_NONE, 3, 0x100);
static AnimTypeClass const TsMgunE(ANIM_TS_MGUN_E, "TSMGUNE", 9, 1, false, false, false, false, false, false, false, false, false, 0, 2, 0, 0, 0, 3, 0, VOC_NONE, ANIM_NONE, 3, 0x100);
static AnimTypeClass const TsMgunSE(ANIM_TS_MGUN_SE, "TSMGUNSE", 9, 1, false, false, false, false, false, false, false, false, false, 0, 2, 0, 0, 0, 3, 0, VOC_NONE, ANIM_NONE, 3, 0x100);
static AnimTypeClass const TsMgunS(ANIM_TS_MGUN_S, "TSMGUNS", 9, 1, false, false, false, false, false, false, false, false, false, 0, 2, 0, 0, 0, 3, 0, VOC_NONE, ANIM_NONE, 3, 0x100);
static AnimTypeClass const TsMgunSW(ANIM_TS_MGUN_SW, "TSMGUNSW", 9, 1, false, false, false, false, false, false, false, false, false, 0, 2, 0, 0, 0, 3, 0, VOC_NONE, ANIM_NONE, 3, 0x100);
static AnimTypeClass const TsMgunW(ANIM_TS_MGUN_W, "TSMGUNW", 9, 1, false, false, false, false, false, false, false, false, false, 0, 2, 0, 0, 0, 3, 0, VOC_NONE, ANIM_NONE, 3, 0x100);
static AnimTypeClass const TsMgunNW(ANIM_TS_MGUN_NW, "TSMGUNNW", 9, 0, false, false, false, false, false, false, false, false, false, 0, 2, 0, 0, 0, 3, 0, VOC_NONE, ANIM_NONE, 3, 0x100);
static AnimTypeClass const TsPiffPiff(ANIM_TS_PIFFPIFF, "TSPIFF", 30, 6, false, false, false, false, false, false, false, false, false, 0, 2, 0, 0, 0, 12, 0, VOC_NONE, ANIM_NONE, 12, 0x100);
static AnimTypeClass const TsClsn16(ANIM_TS_CLSN16, "TSCLSN16", 16, 6, false, true, false, false, true, false, false, true, false, 0, 2, 0, 0, 0, 13, 0, VOC_TS_EXPNEW14, ANIM_NONE, 13, 0x100);
static AnimTypeClass const TsClsn22(ANIM_TS_CLSN22, "TSCLSN22", 22, 6, false, true, false, false, true, false, false, true, false, 0, 2, 0, 0, 0, 13, 0, VOC_TS_EXPNEW14, ANIM_NONE, 13, 0x100);
static AnimTypeClass const TsClsn30(ANIM_TS_CLSN30, "TSCLSN30", 31, 9, false, true, false, false, true, false, false, true, false, 0, 2, 0, 0, 0, 18, 0, VOC_TS_EXPNEW14, ANIM_NONE, 18, 0x100);
static AnimTypeClass const TsClsn42(ANIM_TS_CLSN42, "TSCLSN42", 44, 9, false, true, false, false, true, false, false, true, false, 0, 2, 0, 0, 0, 18, 0, VOC_TS_EXPNEW14, ANIM_NONE, 18, 0x100);
static AnimTypeClass const TsClsn58(ANIM_TS_CLSN58, "TSCLSN58", 62, 9, false, true, false, false, true, false, false, true, false, 0, 2, 0, 0, 0, 18, 0, VOC_TS_EXPNEW14, ANIM_NONE, 18, 0x100);
static AnimTypeClass const TsXgrySml1(ANIM_TS_XGRYSML1, "TSXGRY1", 10, 2, false, false, false, false, false, false, false, true, false, 0, 2, 0, 0, 0, 15, 0, VOC_TS_EXPNEW13, ANIM_NONE, 15, 0x100);
static AnimTypeClass const TsXgrySml2(ANIM_TS_XGRYSML2, "TSXGRY2", 18, 5, false, false, false, false, false, false, false, true, false, 0, 2, 0, 0, 0, 13, 0, VOC_TS_EXPNEW13, ANIM_NONE, 13, 0x100);
static AnimTypeClass const TsExploSml(ANIM_TS_EXPLOSML, "TSEXPSML", 14, 2, false, false, false, true, true, false, false, true, false, 0, 2, 0, 0, 0, 14, 0, VOC_TS_EXPNEW13, ANIM_NONE, 14, 0x100);
static AnimTypeClass const TsSmokey2(ANIM_TS_SMOKEY2, "TSSMOKY2", 8, 7, false, false, false, false, false, false, false, true, false, 0, 2, 0, 0, 0, 11, 0, VOC_NONE, ANIM_NONE, 11, 0x100);

// TS Disruptor sonic wave (ANIM_TS_SONICWAVE), our art (scripts/ts_gen_sonicwave.py), as TS distorts the screen live.
// Never IsNormalized: its damage rides the stages, so they must keep to the game's frames.
static AnimTypeClass const TsSonicWave(ANIM_TS_SONICWAVE, "TSSONICW", 24, 7, false, false, false, false, false, false, false, false, false, 0, 5, 0, 0, 0, 25, 0, VOC_NONE, ANIM_NONE, 25, 0x100);

// TS GUNFIRE muzzle flash (ANIM_TS_GUNFIRE), TS [MechRailgun] Anim=GUNFIRE, art.ini Translucent=yes: TS's
// gunfire.shp scaled x4. Fire_At attaches it to the firer through the weapon's Anim=, as any RA muzzle anim.
static AnimTypeClass const TsGunfire(ANIM_TS_GUNFIRE, "TSGUNFIRE", 16, 1, false, false, false, false, false, false, false, true, false, 0, 2, 0, 0, 0, 3, 0, VOC_NONE, ANIM_NONE, 3, 0x100);

// TS Disruptor ripple disc (ANIM_TS_SONICPULSE): nothing spawns it. It stays registered so the enum and the heap
// keep their order (docs/ts-gdi-tree-plan.md).
static AnimTypeClass const TsSonicPulse(ANIM_TS_SONICPULSE, "TSSONICP", 24, 7, false, false, false, false, false, false, false, false, false, 0, 5, 0, 0, 0, 13, 0, VOC_NONE, ANIM_NONE, 13, 0x100);

void AnimTypeClass::Init_Heap(void)
{
    /*
    **	These anim type class objects must be allocated in the exact order that they
    **	are specified in the AnimType enumeration. This is necessary because the heap
    **	allocation block index serves double duty as the type number index.
    */
    new AnimTypeClass(FBall1);
    new AnimTypeClass(FireBallFade);
    new AnimTypeClass(Frag1);
    new AnimTypeClass(VehHit1);
    new AnimTypeClass(VehHit2);
    new AnimTypeClass(VehHit3);
    new AnimTypeClass(ArtExp1);
    new AnimTypeClass(Napalm1);
    new AnimTypeClass(Napalm2);
    new AnimTypeClass(Napalm3);
    new AnimTypeClass(SmokePuff);
    new AnimTypeClass(Piff);
    new AnimTypeClass(PiffPiff);
    new AnimTypeClass(Fire3);
    new AnimTypeClass(Fire2);
    new AnimTypeClass(Fire1);
    new AnimTypeClass(Fire4);
    new AnimTypeClass(Gunfire);
    new AnimTypeClass(SmokeM);
    new AnimTypeClass(BurnSmall);
    new AnimTypeClass(BurnMed);
    new AnimTypeClass(BurnBig);
    new AnimTypeClass(OnFireSmall);
    new AnimTypeClass(OnFireMed);
    new AnimTypeClass(OnFireBig);
    new AnimTypeClass(SAMN);
    new AnimTypeClass(SAMNE);
    new AnimTypeClass(SAME);
    new AnimTypeClass(SAMSE);
    new AnimTypeClass(SAMS);
    new AnimTypeClass(SAMSW);
    new AnimTypeClass(SAMW);
    new AnimTypeClass(SAMNW);
    new AnimTypeClass(GUNN);
    new AnimTypeClass(GUNNE);
    new AnimTypeClass(GUNE);
    new AnimTypeClass(GUNSE);
    new AnimTypeClass(GUNS);
    new AnimTypeClass(GUNSW);
    new AnimTypeClass(GUNW);
    new AnimTypeClass(GUNNW);
    new AnimTypeClass(FlameN);
    new AnimTypeClass(FlameNE);
    new AnimTypeClass(FlameE);
    new AnimTypeClass(FlameSE);
    new AnimTypeClass(FlameS);
    new AnimTypeClass(FlameSW);
    new AnimTypeClass(FlameW);
    new AnimTypeClass(FlameNW);
    new AnimTypeClass(ChemN);
    new AnimTypeClass(ChemNE);
    new AnimTypeClass(ChemE);
    new AnimTypeClass(ChemSE);
    new AnimTypeClass(ChemS);
    new AnimTypeClass(ChemSW);
    new AnimTypeClass(ChemW);
    new AnimTypeClass(ChemNW);
    new AnimTypeClass(LZSmoke);
    new AnimTypeClass(CDeviator);
    new AnimTypeClass(CDollar);
    new AnimTypeClass(CEarth);
    new AnimTypeClass(CEmpulse);
    new AnimTypeClass(CInvun);
    new AnimTypeClass(CMine);
    new AnimTypeClass(CRapid);
    new AnimTypeClass(CStealth);
    new AnimTypeClass(CMissile);
    new AnimTypeClass(MoveFlash);
    new AnimTypeClass(OilFieldBurn);
    new AnimTypeClass(ElectricDie);
    new AnimTypeClass(Parachute);
    new AnimTypeClass(DogElectricDie);
    new AnimTypeClass(Corpse1);
    new AnimTypeClass(Corpse2);
    new AnimTypeClass(Corpse3);
    new AnimTypeClass(SputDoor);
    new AnimTypeClass(AtomBomb);
    new AnimTypeClass(ChronoBox);
    new AnimTypeClass(GPSBox);
    new AnimTypeClass(InvulBox);
    new AnimTypeClass(ParaBox);
    new AnimTypeClass(SonarBox);
    new AnimTypeClass(Twinkle1);
    new AnimTypeClass(Twinkle2);
    new AnimTypeClass(Twinkle3);
    new AnimTypeClass(Flak);
    new AnimTypeClass(WaterExp1);
    new AnimTypeClass(WaterExp2);
    new AnimTypeClass(WaterExp3);
    new AnimTypeClass(CrateArmor);
    new AnimTypeClass(CrateSpeed);
    new AnimTypeClass(CrateFPower);
    new AnimTypeClass(CrateTQuake);
    new AnimTypeClass(ParaBomb);
    new AnimTypeClass(MineExp1);
    new AnimTypeClass(Flag);
    new AnimTypeClass(Beacon);

    // TF: ours register in their enum order, as the heap ID is the registration order.
    new AnimTypeClass(TdIonCannon); // ANIM_TD_ION_CANNON (Ion Cannon strike)
    new AnimTypeClass(TdFrag2);     // ANIM_TDFRAG2 (TD vehicle death frag explosion)
    // The eight Flame Tank jets follow ANIM_TDFRAG2 in the enum; out of place, every later anim resolves to the
    // wrong type.
    new AnimTypeClass(TdftFlameN);
    new AnimTypeClass(TdftFlameNE);
    new AnimTypeClass(TdftFlameE);
    new AnimTypeClass(TdftFlameSE);
    new AnimTypeClass(TdftFlameS);
    new AnimTypeClass(TdftFlameSW);
    new AnimTypeClass(TdftFlameW);
    new AnimTypeClass(TdftFlameNW);

    // Tiberium fumes (harvester dock at an RA refinery). MUST stay immediately after the
    // TDFTFLAME block to match the ANIM_TIB_FUMES enum slot (heap ID == registration order).
    new AnimTypeClass(TibFumes);

#ifdef FIXIT_ANTS
    new AnimTypeClass(Ant1Death);
    new AnimTypeClass(Ant2Death);
    new AnimTypeClass(Ant3Death);
#endif
#ifdef REMASTER_BUILD
    new AnimTypeClass(Fire3Virtual);
    new AnimTypeClass(Fire2Virtual);
    new AnimTypeClass(Fire1Virtual);
    new AnimTypeClass(Fire4Virtual);
    new AnimTypeClass(BeaconVirtual);
#endif

    // MUST stay last and in this order: these fill the enum slots after the virtual anims, from ANIM_RAILFX on, and
    // the heap ID is the registration order.
    new AnimTypeClass(RailFx);
    new AnimTypeClass(TsSonicWave);
    new AnimTypeClass(TsSonicPulse);
    new AnimTypeClass(TsGunfire);
    new AnimTypeClass(TsDig);
    new AnimTypeClass(TsIonBeam);
    new AnimTypeClass(TsIonRing);
    new AnimTypeClass(TsDropPod1);
    new AnimTypeClass(TsDropPod2);
    new AnimTypeClass(TsDropExp);
    new AnimTypeClass(TsPodRing);
    new AnimTypeClass(TsSmokey);
    new AnimTypeClass(TsMgunN);
    new AnimTypeClass(TsMgunNE);
    new AnimTypeClass(TsMgunE);
    new AnimTypeClass(TsMgunSE);
    new AnimTypeClass(TsMgunS);
    new AnimTypeClass(TsMgunSW);
    new AnimTypeClass(TsMgunW);
    new AnimTypeClass(TsMgunNW);
    new AnimTypeClass(TsPiffPiff);
    new AnimTypeClass(TsClsn16);
    new AnimTypeClass(TsClsn22);
    new AnimTypeClass(TsClsn30);
    new AnimTypeClass(TsClsn42);
    new AnimTypeClass(TsClsn58);
    new AnimTypeClass(TsXgrySml1);
    new AnimTypeClass(TsXgrySml2);
    new AnimTypeClass(TsExploSml);
    new AnimTypeClass(TsSmokey2);
    new AnimTypeClass(TsRailFxS);
    new AnimTypeClass(TsSBang34);
    new AnimTypeClass(TsPulsBall);
    new AnimTypeClass(TsPulseFx1);
    new AnimTypeClass(TsPulseFx2);
    new AnimTypeClass(TsEmpFx);
    new AnimTypeClass(TsMEmpFx);
    new AnimTypeClass(TsFsIdle);
    new AnimTypeClass(TsFsGrnd);
    new AnimTypeClass(TsFsAir);
}

/***********************************************************************************************
 * AnimTypeClass::One_Time -- Performs one time action for animation types.                    *
 *                                                                                             *
 *    This will load the animation shape data. It is called by the game initialization         *
 *    process.                                                                                 *
 *                                                                                             *
 * INPUT:   none                                                                               *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   This routine should be called ONLY once.                                        *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   06/02/1994 JLB : Created.                                                                 *
 *=============================================================================================*/
void AnimTypeClass::One_Time(void)
{
    for (int index = ANIM_FIRST; index < ANIM_COUNT; index++) {
        char fullname[_MAX_FNAME + _MAX_EXT];

        AnimTypeClass const& anim = As_Reference((AnimType)index);

        if (!anim.IsTheater) {

            _makepath(fullname, NULL, NULL, As_Reference((AnimType)index).IniName, ".SHP");

#ifndef NDEBUG
            RawFileClass file(fullname);
            if (file.Is_Available()) {
                ((void const*&)As_Reference((AnimType)index).ImageData) = Load_Alloc_Data(file);
            } else {
                ((void const*&)As_Reference((AnimType)index).ImageData) = MFCD::Retrieve(fullname);
            }
#else
            ((void const*&)As_Reference((AnimType)index).ImageData) = MFCD::Retrieve(fullname);
#endif
        }
    }

#ifdef REMASTER_BUILD
    // TF: the TD Flamethrower, Chem Warrior and Flame Tank jets are HD tiles with no classic SHP, so they borrow
    // FBALL1's ImageData to pass Draw_It's NULL guard; the overlay then draws the real tile by IniName.
    {
        void const* flame_donor = As_Reference(ANIM_FBALL1).ImageData;
        for (int fa = ANIM_FLAME_N; fa <= ANIM_CHEM_NW; fa++) {
            if (As_Reference((AnimType)fa).ImageData == NULL) {
                ((void const*&)As_Reference((AnimType)fa).ImageData) = flame_donor;
            }
        }
        for (int fa = ANIM_TDFTFLAME_N; fa <= ANIM_TDFTFLAME_NW; fa++) {
            if (As_Reference((AnimType)fa).ImageData == NULL) {
                ((void const*&)As_Reference((AnimType)fa).ImageData) = flame_donor;
            }
        }
    }
#endif
}

/***********************************************************************************************
 * AnimTypeClass::Init -- Load any animation artwork that is theater specific.                 *
 *                                                                                             *
 *    This routine will examine all the animation types and for any that are theater           *
 *    specific, it will fetch a pointer to the artwork appropriate for the theater specified.  *
 *                                                                                             *
 * INPUT:   theater  -- The theater to align the animation artwork with.                       *
 *                                                                                             *
 * OUTPUT:  none                                                                               *
 *                                                                                             *
 * WARNINGS:   Call this routine when the theater changes.                                     *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/06/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
void AnimTypeClass::Init(TheaterType theater)
{
    if (theater != LastTheater) {
        for (int index = ANIM_FIRST; index < ANIM_COUNT; index++) {
            AnimTypeClass const& anim = As_Reference((AnimType)index);

            if (anim.IsTheater) {
                char fullname[_MAX_FNAME + _MAX_EXT]; // Fully constructed iconset name.
                _makepath(fullname, NULL, NULL, anim.IniName, Theaters[theater].Suffix);
                ((void const*&)anim.ImageData) = MFCD::Retrieve(fullname);
            }
        }

#ifdef REMASTER_BUILD
        // Set up beacon image data manually since they're new animations only available in the virtual renderer
        ((void const*&)As_Reference(ANIM_BEACON_VIRTUAL).ImageData) = As_Reference(ANIM_BEACON).ImageData;
#endif
    }
}

/***********************************************************************************************
 * Anim_Name -- Fetches the ASCII name of the animation type specified.                        *
 *                                                                                             *
 *    This will convert the animation type specified into a text name. This name can be used   *
 *    for uniquely identifying the animation.                                                  *
 *                                                                                             *
 * INPUT:   anim  -- The anim type to convert to a text string.                                *
 *                                                                                             *
 * OUTPUT:  Returns with a pointer to the ASCII string that identifies this animation.         *
 *                                                                                             *
 * WARNINGS:   none                                                                            *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/06/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
char const* Anim_Name(AnimType anim)
{
    if (anim == ANIM_NONE)
        return ("");

    return (AnimTypeClass::As_Reference(anim).IniName);
}

/***********************************************************************************************
 * AnimTypeClass::As_Reference -- Fetch a reference to the animation type specified.           *
 *                                                                                             *
 *    This routine will convert the animation type specified into a reference to the           *
 *    animation type class object.                                                             *
 *                                                                                             *
 * INPUT:   type  -- The animation type to convert into a reference.                           *
 *                                                                                             *
 * OUTPUT:  Returns with a reference to the animation type class object.                       *
 *                                                                                             *
 * WARNINGS:   Be sure that the animation type specified is legal. If it isn't then the        *
 *             results of this routine are undefined.                                          *
 *                                                                                             *
 * HISTORY:                                                                                    *
 *   07/06/1996 JLB : Created.                                                                 *
 *=============================================================================================*/
AnimTypeClass& AnimTypeClass::As_Reference(AnimType type)
{
    return (*AnimTypes.Ptr(type));
}
