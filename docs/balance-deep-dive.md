# Cross-faction balance deep-dive

**Status:** Reference. A stat audit of the four original factions (TS GDI is not covered), the deviations from
TD's values that shipped in 4.0.0 and since, and the playtest log.
**Open:** the Recon Bike after the Light Tank's buff; the light-vehicle and artillery discounts against the equal
economy (F4, F5); the Nod SAM against RA's jets; Nod's cost to defend against GDI's; line-wide tank pace; an early
GDI Mammoth snowballing.

Where this doc and `rules.ini` disagree, `rules.ini` is the truth. Log playtest balance reports in the playtest log
below, and fix fidelity bugs (a stat that differs from TD's source with no deviation listed here) at once.

---

## Guardrails

- **Difficulty stays behavioural:** IQ, timing and strategy levers only, never stat multipliers per difficulty.
- **Every deviation from TD's values is deliberate and listed here** with its reason. TD's values are the
  baseline; moving off one is a balance call, not a silent edit.
- **Prefer a single dial.** Change one lever (usually `Cost=`, a rate of fire or a speed) rather than rewrite
  weapon maths, so the unit stays recognisably TD's.
- **TechLevel is not a lever.** Skirmish is played at TechLevel 10, so a lower `TechLevel` ("available earlier")
  gives no real advantage: every faction has everything from the start. Never justify a weaker stat line by
  earliness. The real levers are cost, stats (strength, ROF, range, speed) and prerequisite buildings, which still
  have to be built.
- **Apply TD's building doubling before comparing.** A TD building's `Strength=` doubles at load
  (`BuildingTypeClass::Read_INI`, `bdata.cpp:6265`; `td-port-playbook.md` §3.21), so compare its doubled
  strength with an RA building's.

---

## The shipped deviations from TD's values

| Unit or weapon | Change (TD's, or stock RA's for RA types, → TF) | Since | Reason |
|---|---|---|---|
| Orca, Apache | 125 → 225 strength, at TD's $1200 | 4.0.0 | Parity with the Longbow and Hind (F6) |
| `TDNike` (Nod SAM) | ROF 50 → 20 | 4.0.0 | RA's Nike rate (F7) |
| `TD75mm` (Nod Light Tank) | ROF 60 → 40 | 4.0.0 | RA's 75mm rate (F3) |
| TDHTNK (GDI Mammoth) | speed 5 → 4, cost kept at 1500 | 4.0.0 | Match the Soviet Mammoth's speed (F1) |
| TDAPC (GDI APC) | speed 14 → 8, cost kept at 700 | 4.0.0 | It felt too fast in play; the cheaper APC is the slower one |
| `TDM16`, TDE1 (Minigunner) | range 2 → 3, speed 3 → 4 | 4.0.0 | Parity with RA's rifleman |
| `TDTurretGun` (Nod Turret) | ROF 60 → 50 | 4.0.0 | Parity with RA's turret |
| `155mm` (stock RA), `TD155mm` (TD) (artillery) | range 6 → 8 | | Range 6 couldn't out-stand base defences |
| `TDMlrsRocket` (GDI MLRS) | range 6 → 7 | | As the artillery, a cell short (playtest log) |
| `TDPatriot` (Nod SAM missile) | ROT 10 → 20 | | RA's `AAMissile` turn rate, to turn onto RA's faster aircraft |
| TDHARV | speed 5 → 6 | | RA's harvester's, so no faction's trucks are slower |
| Every TD building | sight + 3 (`bdata.cpp:6266`) | | TD's sight reads short at RA's scale |
| TDA10 (A-10) | cost 800 → 1500 | | Above the MiG's 1200 for a nine-bomb sortie |
| TDFBNK (Nod Flame Bunker) | new, not TD | | Nod's missing anti-infantry emplacement |
| `[TDSSM]`, `[TDSSM2]` (TD's missiles) | inaccurate → `Inaccurate=no` | | No scatter by type, as RA plays its missiles (commit `c878c0248`); fuelled shots still scatter at infantry and cells |

`[TDAGT]` is `[TDHE]`'s values in a section of its own, named as `[TDTowTwo]`'s warhead, but it does nothing: the
tower fires `[TDSSM]`, an `IsTDPort` bullet, and `AI_TD` deals damage with the bullet's own `Warhead=TDHE`
(`bullet.cpp:1744`, `1755`; playbook §3.38). To tune the tower alone, give `[TDTowTwo]` a bullet of its own (a
`[TDSSM]` copy with `Warhead=TDAGT`); `[TDSSM]` is shared with the Mammoth's `TDTusk`.

---

## The four factions

| Faction | Engine house | Doctrine, as the numbers express it |
|---|---|---|
| **Allies** | RA (allies) | Fast cheap light tanks, the best DPS per credit in armour, durable air, a strong navy. Heavy units tech-gated. |
| **Soviet** | RA (soviet) | Heavy armour and the Mammoth, V2 siege, the Hind against infantry. Expensive and late. |
| **GDI** | TD (GoodGuy) | Durable armour: the Medium at TL3, a Mammoth cheaper than the Soviets'. |
| **Nod** | TD (BadGuy) | Cheap fast harassment (Buggy, Bike), the cloaking Stealth Tank, flame against bases, SSM and artillery siege. A light mainline tank. |

---

## How to read the tables

- **Relative DPS** = `Damage × Burst / ROF`. ROF is the reload delay in ticks, so lower is faster. It ignores
  range, projectile speed and accuracy: a first-order screen.
- **Effective DPS against a target** = relative DPS × the warhead's `Verses` for the target's armour. Warheads
  decide matchups.
- Tanks and the combat helicopters are `heavy`; infantry `none`; light vehicles `light`; some Nod structures
  `steel`, which reads as heavy (TF's `Armor_From_Name`, `weapon.cpp:304-310`, maps TD's `steel` to heavy and
  `aluminum` to light). Buildings are `wood` or `concrete`.

### Warheads (`Verses`: none / wood / light / heavy / concrete)

| Warhead | none | wood | light | heavy | concrete | Used by |
|---|---|---|---|---|---|---|
| AP | 30 | 75 | 75 | **100** | 50 | RA tank cannons, missiles |
| TDAP | 25 | 75 | 75 | **100** | 50 | TD tank cannons |
| HE | 90 | 75 | 60 | 25 | 100 | RA artillery, grenades, the Mammoth's tusks |
| TDHE | 87 | 75 | 56 | 25 | 100 | TD artillery, MLRS, tusks, chain guns |
| SA | 100 | 50 | 60 | 25 | 25 | RA machine guns |
| TDSA | 100 | 50 | 56 | 25 | 25 | TD minigun, M60 |
| Fire | 90 | 100 | 60 | 25 | 50 | RA flamethrower |
| TDFire | 88 | 100 | 69 | 25 | 50 | TD flame tank, flamethrower, Flame Bunker |
| HollowPoint | 100 | 5 | 5 | 5 | 5 | sniper, Tanya |
| TDLaser | 100 | 100 | 100 | 100 | 100 | the Obelisk |

- **TDAP is AP and TDHE is HE,** within a few percent (TD's n/256 rounding). No faction has a warhead advantage.
- Anti-tank warheads are weak against `none`, so tanks need infantry or machine-gun support, on every side.
- TDFire is anti-infantry and anti-building (25% against heavy): Nod's Flame Tank is not an anti-armour unit.

---

## Mainline battle tanks

| Unit | Faction | Cost | Strength | Speed | TL | Weapon | Rel. DPS | DPS/cost | Strength/cost |
|---|---|---|---|---|---|---|---|---|---|
| 1TNK Light | Allied | 700 | 300 | 9 | 4 | 75mm | 0.63 | 0.89 | 0.43 |
| 2TNK Medium | Allied | 800 | 400 | 8 | 6 | 90mm | 0.60 | 0.75 | 0.50 |
| 3TNK Heavy | Soviet | 950 | 400 | 7 | 4 | 105mm ×2 | 0.86 | 0.90 | 0.42 |
| 4TNK Mammoth | Soviet | 1700 | 600 | 4 | 10 | 120mm b2 + Tusk | 1.00¹ | 0.59 | 0.35 |
| **TDLTNK Light** | **Nod** | 600 | 300 | 7 | 3 | TD75mm | 0.63 | 1.04 | 0.50 |
| **TDMTNK Medium** | **GDI** | 800 | 400 | 7 | 3 | TD105mm | 0.60 | 0.75 | 0.50 |
| **TDHTNK Mammoth** | **GDI** | 1500 | 600 | 4 | 5 | TD120mm b2 + TDTusk | 1.00¹ | 0.67 | 0.40 |

¹ The cannon only; the tusk missiles add an anti-air and anti-infantry second weapon. Both Mammoths are
mechanically identical.

- **F1, the GDI Mammoth.** Same hull and weapons as the Soviet Mammoth, both self-healing, behind an easier
  prerequisite (`TDFIX` against `weap,stek`). Its speed matches the Soviets' 4; its cost stays 1500 against 1700
  for roster depth: the Soviets have the Heavy Tank, Mammoth, V2 and Tesla Tank, and GDI's only real heavy hitter
  is the Mammoth (the MLRS is fragile artillery). Watch that an early Mammoth doesn't snowball unanswered.
- **F2, GDI's early armour.** TDMTNK at TL3 against 2TNK's TL6, the Mammoth at TL5. TD's build levels, and not a
  lever at TechLevel 10; the prerequisite chain is what gates it.
- **F3, the Nod Light Tank.** At TD's ROF 60 it had about two-thirds of the Allied Light's sustained damage on the
  same hull, and the Light is Nod's ceiling. `TD75mm` at ROF 40 (used by TDLTNK alone) evens it with the Allied
  Light; Nod's lower cost then decides, and the Allies keep speed (9 against 7) and the Medium above it. Nod gets no
  heavier tank: its ceiling is the Stealth Tank and the Flame Tank, a specialist toolkit. The Light is anti-armour
  only (25% against infantry), so the Buggy, Flame Tank, Stealth Tank and artillery keep their niches. The Recon
  Bike out-damaged TD's Light Tank (0.50 against 0.42); now the Light beats it on damage, strength and armour for
  100 more, and the Bike's place is its speed (16 against 7), as a raider. Watch it in play, and don't buff it
  first.

## Light and harassment vehicles

| Unit | Faction | Cost | Strength | Armour | Speed | Weapon | Warhead | Note |
|---|---|---|---|---|---|---|---|---|
| JEEP | Allied | 600 | 150 | light | 10 | M60mg | SA | anti-infantry scout |
| TDJEEP Hum-vee | GDI | 400 | 150 | light | 12 | TDM60mg | TDSA | cheaper and faster than RA's |
| TDBGGY Buggy | Nod | 300 | 140 | light | 12 | TDM60mg | TDSA | the cheapest harasser |
| TDBIKE | Nod | 500 | 160 | wood | 16 | TDDragon | TDAP | fast anti-tank harasser |
| APC | Allied, Soviet | 800 | 200 | heavy | 10 | M60mg | SA | transport |
| TDAPC | GDI | 700 | 200 | heavy | 8 | TDM60mg | TDSA | cheaper and slower transport |
| TDSTNK Stealth | Nod | 900 | 110 | light | 12 | TDStnkDragon b2 | TDAP | cloaks, hits air and ground, glass |

- **F4.** GDI and Nod light vehicles are better per credit than RA's (cheaper, faster, the same strength): the
  mobility and harassment doctrine. Under review against the equal economy; watch Buggy and Bike spam.
- **The APC.** TDAPC keeps its cheaper price by being slower (8, above the TD tanks' 7 and below the Hum-vee's 12).
- **The Stealth Tank** is Nod's own tool (cloak, and it shoots air) but glass at 110 strength light: once revealed
  it dies fast.

## Artillery and siege

| Unit | Faction | Cost | Strength | Weapon | Damage | ROF | Range | Warhead | Note |
|---|---|---|---|---|---|---|---|---|---|
| ARTY | Allied | 600 | 75 | 155mm | 150 | 65 | 8 | HE | glass cannon |
| TDARTY | Nod | 450 | 75 | TD155mm | 150 | 65 | 8 | TDHE | cheaper, same output |
| TDMLRS | GDI | 800 | 100 | TDMlrsRocket b2 | 75 | 80 | 7 | TDHE | homing, durable |
| TDMSAM SSM | Nod | 750 | 120 | TDHonestJohn | 100 | 200 | 10 | TDFIRE | napalm siege, long range |
| V2RL | Soviet | 700 | 150 | SCUD | 600 | 400 | 10 | HE | one big hit, slow reload |

- **F5.** Nod's artillery is a cheaper Allied artillery (450 against 600, the same weapon). Likely fine.
- **Range.** At TD's and stock RA's 6 the artillery couldn't out-stand base defences. Its `Ballistic` shell is
  `Inaccurate=no` (stock sets `Inaccurate=yes`, which EA's misspelt key never read), so a building shelled at 8
  takes the hit where it is aimed. The MLRS sits a cell lower, at 7: short of the cannon artillery and of the
  Obelisk's 7.5, still outranging the turrets and the Advanced Guard Tower.

## Aircraft and air defence

| Unit | Faction | Cost | Strength | Weapon | Ammo | Role |
|---|---|---|---|---|---|---|
| HELI Longbow | Allied | 1200 | 225 | Hellfire (AP) | 6 | anti-armour |
| HIND | Soviet | 1200 | 225 | ChainGun (SA, ROF 3) | 12 | anti-infantry |
| TDORCA | GDI | 1200 | 225 | TDStnkDragon b2 (TDAP) | 6 | anti-armour |
| TDHELI Apache | Nod | 1200 | 225 | TDApacheGun b2 (TDHE) | 15 | anti-infantry |

- **F6.** At TD's 125 strength for the same 1200, the Orca and Apache died about twice as fast as the Longbow and
  Hind; they now have the RA helicopters' 225. Firepower wasn't the problem and stays TD's: the effective damage of
  one ammunition load against heavy armour is Longbow 240, Orca 180, Hind 120, Apache 94, and against infantry Hind
  480, Apache 326, Longbow 72, Orca 45. The Orca is GDI's anti-armour gunship and the Apache Nod's infantry
  shredder, each within about 75% of its RA counterpart's specialty. Don't buff helicopter damage.

The combat helicopters are `heavy`, so TDHE does 25% against them. Effective anti-air damage against one, per 60
ticks, with strengths as played:

| Faction | Structure | Strength | Cost | AA weapon | Against a helicopter |
|---|---|---|---|---|---|
| Allies | AA Gun | 400 | 600 | ZSU-23 (AP) | 150 |
| Soviet | SAM Site | 400 | 750 | Nike (AP) | 150 |
| Nod | SAM Site (TDSAM) | 400 (200 doubled) | 750 | TDNike (TDAP, ROF 20) | 150 |
| GDI | Advanced Guard Tower (TDATWR) | 600 (300 doubled) | 1000 | TDTowTwo (via `[TDSSM]`'s TDHE, air and ground) | 45 |

- **F7.** At TD's ROF 50 the Nod SAM managed 60; at RA's 20 it matches the RA SAMs.
- **F8.** GDI's only anti-air is the Advanced Guard Tower, and its `TDHE` values do 25% against heavy armour, in
  the air and on the ground. It stays so: for 1000 credits and −20 power it fires `Burst=2` at ground and air
  alike, and GDI fields several: three towers (135) come near one RA SAM (150). Tune it through a bullet of its own
  (above), never `[TDHE]`: six weapon sections name it (`TDTusk`, `TDChainGun`, `TDApacheGun`, `TDGrenade`,
  `TDMlrsRocket`, `TD155mm`), and the `IsTDPort` bullets `[TDSSM]`, `[TDSSM2]` and `[TDSpreadfire]` carry it, which is
  how `TDTowTwo` reaches it.

## Base defences

- **The Nod Turret** matches RA's turret: 400 strength in play (200 doubled), the same cost, range and damage,
  `Sensors=yes` as every anti-ground defence on every faction has, and since 4.0.0 RA's ROF 50. At TD's ROF 60 it
  was 600 credits for a weaker defence.
- **The Nod Flame Bunker** (`[TDFBNK]`) fills Nod's gap in anti-infantry emplacements: every other faction has one
  early (the Allied Pillbox, the Soviet Flame Tower, GDI's Guard Tower), and Nod had only the anti-armour Turret
  (25% against infantry) and the Obelisk, a slow single-target charge that infantry swarm. It is a type of its own
  on RA's pillbox art (`Image=PBOX`, not the shared Allied `PBOX`), `Owner=BadGuy` behind TDHAND, 500 credits, 400
  strength in play on wood, TL2. Its `[TDFlameBunker]` is the Flame Tank's `TDFlameTongue` at range 4, not 2, so
  range-3 infantry can't outrange it, and without its `Burst=2`, so half the tank's damage a cycle; `TDFire`'s spread of 8 suits swarms. Turret and Flame Bunker give Nod the
  anti-armour and anti-infantry pair the others have, with no warhead overlap.
- **The Obelisk's 7.5-cell reach is shorter than the Tesla Coil's 8.5 on purpose:** it hits harder and reaches
  less.
- **Nod pays far more than GDI to defend.** One Advanced Guard Tower covers ground and air for 1000 credits and
  −20 power. Nod needs an Obelisk (1500, −150, ground only) plus a SAM (750, −20): about 2.25 times the cost and 8.5
  times the power. Nod's light vehicles and Apaches are what the tower beats. If a GDI-against-Nod game shows it,
  the levers are the tower's cost or power, or cheaper Nod defences, not its warhead.
- **RA's Tesla Coil does not chain** (one target, `Spread=1`); its crowd-clearing feel is the `Super` warhead
  one-shotting infantry. An arc to nearby targets would be new code, and is parked.

## Infantry

TD's specialists keep TD's stats: TDE3 has 25 strength against RA's E3's 45, and speed 2 against 3. Infantry trades
are decided by buildings and tanks more than by infantry duels. The basic Minigunner is no faction identity, so it
matches RA's rifleman: `TDM16` range 3 and TDE1 speed 4, with 50 strength, 100 credits, 15 damage and ROF 20 as
both already had.

## The economy

In TD harvesters dock at the refinery while RA's dump, so RA's income ran faster. Since 3.0.0 every harvester docks,
with the same dock time at every refinery (`harvester-docking-rework-plan.md`), and the economies are equal. Every
GDI and Nod discount once justified as compensation for a slower economy was re-derived in 4.0.0 and kept only where
another reason holds: the Mammoth's cost (roster depth), the APC's (it is slower). The F4 and F5 discounts are still
to review; they are mostly doctrine and likely stay. Speed is the preferred dial over cost for these: GDI keeps the
edges it earns and loses the ones with no reason.

## Tank pace

TD tanks run at `Speed=7` (TD's `MPH_MEDIUM`) against the Allied Light's 9. TD vehicle speeds stay at their
MPH-derived values: any slower and RA armour kites them. The open question is the pace of the whole line, not of
one unit.

---

## Playtest log

- **Artillery range** (commit `1021b67`): cannon artillery at 8 and the MLRS at 7 felt right in play.
- **The GDI APC** felt too fast in play at TD's 14 and still at 10; it ships at 8.
- **The Nod SAM against RA jets** (after 4.0.0): four Nod SAM sites let a MiG finish three attack runs before it
  died, even at ROF 20. TDSAM was tuned against TD's slow helicopters; RA's MiG and Yak are fast, with stand-off
  missiles. Before tuning, compare projectile speed, ROF and range with RA's SAM and AA gun, and check whether the
  rise-and-lower cycle eats the firing window (`td-sam-deep-dive.md`).
