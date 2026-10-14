#ifndef TF_TS_EFFECTS_H
#define TF_TS_EFFECTS_H

#include "defines.h"

class AnimClass;
class BuildingClass;
class BulletTypeClass;
class TechnoTypeClass;

/*
**	True when this object plays Tiberian Sun's own effects: a TS type with the TS-HD-Assets pack
**	loaded, as the pack carries the art.
*/
bool TF_TS_Effects(TechnoTypeClass const* type);

/*
**	True for a TS projectile (IniName TS*) with the pack loaded: its burst is TS's even after
**	its firer is gone.
*/
bool TF_TS_Effects_Bullet(BulletTypeClass const* type);

/*
**	One of the five blasts a TS object dies in, picked at random
**	(TS Explosion=TWLT070,S_BANG48,S_BRNL58,S_CLSN58,S_TUMU60).
*/
AnimType TF_TS_Death_Anim(void);

/*
**	The TS counterpart of an RA fire or blast that EA code plays for this object: TS's OnFire
**	fires and death blasts. Any other object keeps the RA anim.
*/
AnimType TF_TS_Effect(TechnoTypeClass const* type, AnimType anim);

/*
**	Throws TS's metal shards from a dying TS object, up to its TS MaxDebris. Each flies TS's
**	ballistic arc and bursts where it lands (TF_TS_Anim_AI).
*/
void TF_TS_Throw_Debris(TechnoTypeClass const* type, COORDINATE coord);

/*
**	The anim a TS soldier dies in for a warhead's InfDeath: blown apart (3), running alight (4)
**	or electrocuted (5). ANIM_NONE where the soldier plays his own death sequence.
*/
AnimType TF_TS_Infantry_Death(int infdeath);

/*
**	A TS soldier's body, picked at random from TS's DeadBodies.
*/
AnimType TF_TS_Dead_Body(void);

/*
**	Lights or clears TS's flashing emitter ring (GAFSDF_A) on a Firestorm Wall Section. TS lights
**	it on a live field's posts: every section but the middle of a straight run.
*/
void TF_TS_Firestorm_Glow(BuildingClass* section, bool lit);

/*
**	Moves a debris shard or a burning soldier for this tick. True once the anim has deleted
**	itself, so the caller must not touch it.
*/
bool TF_TS_Anim_AI(AnimClass* anim);

#endif
