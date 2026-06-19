# Cross-faction balance deep-dive (v1.0 baseline)

**Status:** analysis complete 2026-06-02, against the shipped v1.0 `rules.ini`
(`resources/remaster_mods/Vanilla_RA/CCDATA/rules.ini`). **No changes applied
yet** — this is the data + analysis + proposed plan for the v1.x balance pass.

This document is the analytical companion to `balance-v1-notes.md` (the running
playtest-report log) and operationalises the deferred-balance backlog captured
in `[[project-balance-deferred-to-v1]]`. Read both before touching a stat.

---

## Why now

The standing rule (`[[project-balance-deferred-to-v1]]`) deferred *all* stat
tuning until 1.0 shipped, keeping every unit TD-source-authentic so we had a
known reference point. v1.0.0 is tagged and the **TD unit roster is real, not
RA stand-ins** (full TD vehicle + combat-unit + infantry + aircraft rosters
landed pre-1.0 — `0477d95`, `d879d6c`, TDE1/E2/E3, Orca/Apache). So:

1. The deferral gate is cleared.
2. We're balancing the units that *stay*, not placeholders.
3. The four factions fight **cross-faction** (GDI Mammoth vs Soviet Mammoth,
   Nod Light vs Allied Light) — so TD-vs-RA stat comparisons are the live
   balance question, not academic (`[[project-balance-deferred-to-v1]]`,
   Luke 2026-05-30).

## Guardrails (unchanged)

- **Difficulty stays behavioural** (`[[feedback-difficulty-philosophy]]`): IQ /
  timing / strategy levers only. Never stat-bias multipliers per difficulty.
- **Every deviation from TD-authentic is deliberate and documented here** with
  a reason. TD-authentic was the v1 baseline; moving off it is a balance call,
  not a silent edit.
- **Prefer a single dial.** Where a unit is mis-tuned, change one lever (usually
  `Cost=` or `TechLevel=`) rather than rewriting weapon math. Keeps the unit
  recognisably its TD self.

---

## The four factions in one line each

| Faction | Engine house | Doctrine (as the numbers currently express it) |
|---|---|---|
| **Allies** | RA vanilla (allies) | Fast cheap light tanks, best DPS-per-credit armor, durable air (Longbow 225hp), strong navy. Heavy units tech-gated. |
| **Soviet** | RA vanilla (soviet) | Heavy/Mammoth armor + V2 siege + Hind infantry-shredder. Expensive and late. |
| **GDI** | TD (GoodGuy) | Durable armor available **early** — Medium at TL3, Mammoth at TL5 cheaper than Soviet's. Fragile air, slower (docking) economy. |
| **Nod** | TD (BadGuy) | Cheap fast harass (Buggy/Bike), cloak (Stealth Tank), anti-base flame, SSM/arty. Weak mainline tank, fragile air, slower economy. |

---

## Combat model (how to read the tables)

- **Relative DPS** = `Damage × Burst / ROF`. In this engine **ROF is the reload
  delay in ticks — lower = faster**. So this index is shots-per-tick × damage;
  bigger = more sustained damage. It ignores range/projectile-speed/accuracy,
  so treat it as a first-order screen, not gospel.
- **Effective DPS vs a target** = relative DPS × the warhead's `Verses` % for
  that target's armor class. This is where warheads decide matchups.
- Tanks are `heavy` armor; infantry `none`; light vehicles/aircraft `light`;
  some Nod structures/units `steel` (also maps to heavy-ish). Buildings use
  `wood`/`concrete`.

### Warhead Verses tables (none / wood / light / heavy / concrete)

| Warhead | none | wood | light | heavy | concrete | used by |
|---|---|---|---|---|---|---|
| AP | 30 | 75 | 75 | **100** | 50 | RA tank cannons, missiles |
| TDAP | 25 | 75 | 75 | **100** | 50 | TD tank cannons (TD-authentic) |
| HE | 90 | 75 | 60 | 25 | 100 | RA arty, grenade, Mammoth tusk |
| TDHE | 87 | 75 | 56 | 25 | 100 | TD arty, MLRS, tusk, chaingun |
| SA | 100 | 50 | 60 | 25 | 25 | RA MG/vulcan/chaingun |
| TDSA | 100 | 50 | 56 | 25 | 25 | TD minigun/M60 |
| Fire | 90 | 100 | 60 | 25 | 50 | RA flamethrower |
| TDFire | 88 | 100 | 69 | 25 | 50 | TD flame tank/thrower |
| HollowPoint | 100 | 5 | 5 | 5 | 5 | sniper, Tanya |
| TDLaser | 100 | 100 | 100 | 100 | 100 | Obelisk (building only) |

**Takeaways from the warheads alone:**
- **TDAP ≈ AP, TDHE ≈ HE** — TD warheads are within a few % of their RA
  equivalents (the n/256 rounding). No faction gets a warhead advantage.
- Anti-tank (AP/TDAP) does full damage to `heavy` and is weak vs `none` →
  tanks need infantry/MG support to clear squishies. Symmetric across factions.
- Flame (TDFire) is anti-infantry/anti-building (25% vs heavy) — Nod's Flame
  Tank is *not* an anti-armor unit despite its raw DPS.

---

## Tier-by-tier matchup analysis

### Mainline battle tanks (the core of every cross-faction fight)

| Unit | Faction | Cost | HP | Speed | TL | Weapon | rel-DPS | DPS/cost | HP/cost |
|---|---|---|---|---|---|---|---|---|---|
| 1TNK Light | Allied | 700 | 300 | 9 | 4 | 75mm | 0.63 | 0.89 | 0.43 |
| 2TNK Medium | Allied | 800 | 400 | 8 | 6 | 90mm | 0.60 | 0.75 | 0.50 |
| 3TNK Heavy | Soviet | 950 | 400 | 7 | 4 | 105mm ×2 (double-barrel) | 0.86 | 0.90 | 0.42 |
| 4TNK Mammoth | Soviet | 1700 | 600 | 4 | 10 | 120mm b2 + Tusk | 1.00¹ | 0.59 | 0.35 |
| **TDLTNK Light** | **Nod** | 600 | 300 | 7 | 3 | TD75mm | **0.42** | 0.70 | 0.50 |
| **TDMTNK Medium** | **GDI** | 800 | 400 | 7 | 3 | TD105mm | 0.60 | 0.75 | 0.50 |
| **TDHTNK Mammoth** | **GDI** | 1500 | 600 | 5 | 5 | TD120mm b2 + TDTusk | 1.00¹ | 0.67 | 0.40 |

¹ Mammoth primary-cannon DPS only; the Tusk missiles add a large anti-air /
anti-infantry second weapon on top. Both Mammoths are mechanically identical.

**Findings:**

- **🔴 F1 — GDI Mammoth strictly dominates the Soviet Mammoth.** Same hull,
  same weapons, both SelfHealing — but TDHTNK is **cheaper (1500 vs 1700),
  faster (5 vs 4), and arrives at TL5 vs TL10** behind an easier prereq (`fix`
  vs `weap,stek`). In a cross-faction game GDI fields the best heavy tank for
  less money, half a tech tree earlier. This is the single clearest imbalance.
  Already flagged in `[[project-balance-deferred-to-v1]]`.
  - **DECISION 2026-06-03 (Luke) [SUPERSEDED]: keep TDHTNK Cost at 1500**, on the
    grounds that the cheaper Mammoth offsets the GDI/Nod *economy handicap* (TD
    harvesters dock = bank slower). **This basis is now gone** — v3.0 (2026-06-18)
    equalised the harvester economy (dock times halved + made equal for every
    combination; "both sides' economies in step"). So the economy no longer
    justifies anything. See the economy section.
  - **✅ REVISED DECISION 2026-06-19 (Luke): match Speed to Soviet, keep Cost.**
    - **`Speed` 5 → 4** (match the Soviet 4TNK) — removes the one *gratuitous*
      edge (there was no reason the GDI Mammoth was faster).
    - **`Cost` stays 1500** (cheaper than 4TNK's 1700) — but the justification is
      now **roster depth, not economy**: Soviets have a deep heavy/siege roster
      (Heavy Tank, Mammoth, V2, Tesla Tank) while **GDI's only real heavy hitter
      is the Mammoth** (the MLRS is fragile artillery). The cost edge compensates
      for GDI's shallow top-end.
    - **`TechLevel` stays 5** — early durable armor is GDI's identity.
    - **Net change vs today: Speed 5→4 only.** ⚠ Watch-item: with speed matched +
      cost kept, the Mammoth's remaining edge is the **TL5-vs-TL10 earliness** (a
      600hp Mammoth half a tech tree before Soviets). Fits the compensation logic;
      watch in playtest that the early Mammoth doesn't snowball unanswered.
- **🟠 F2 — GDI's whole armor curve is early.** GDI gets a Medium-tank
  equivalent (TDMTNK) at **TL3** — the Allied Medium (2TNK) is TL6 — and the
  Mammoth at TL5. Combined, GDI has the strongest *armor timing* of the four
  factions. TD-authentic (TD build levels), but in RA's tech pacing it's a
  tempo edge.
- **🟠 F3 — Nod's mainline tank is DPS-starved.** TDLTNK fires at ROF 60
  (0.42 DPS) where the Allied Light fires at ROF 40 (0.63) — ~50% less sustained
  damage for the same 300hp/heavy hull, only 100 credits cheaper. And the Light
  is Nod's *ceiling* — Nod has no Medium or Heavy tank. Nod's armored core is
  weak by design (doctrine: cheap harass + tricks), but the gap vs Allied armor
  is large. TD-authentic.
  - **✅ DECIDED v4.0 (Luke, 2026-06-19): `TD75mm` ROF 60 → 40** (match the
    Allied 75mm). Single dial, **zero collateral** (TD75mm is used by *only*
    TDLTNK). Closes the DPS deficit exactly → even 1v1 vs the Allied Light, after
    which Nod's cheaper cost (600) + earlier tech (TL3) become the deciding edge:
    a strong cheap-early mainline, fitting Nod's doctrine. **Not an overcorrection**
    — Allied keeps mobility (Speed 9 vs 7; TD speed stays per the line-wide pace
    decision) and escalation to the Medium Tank. Deviation from TD-authentic slow
    cannon, justified: this is Nod's mainline with no heavier MBT above it.
  - **"No heavier tank" — leave it.** Nod's armored ceiling is *intentionally* the
    Stealth Tank (cloak ambush) + Flame Tank (anti-base) specialist toolkit, not a
    tonnage MBT — that's the identity. The ROF fix fully resolves the mainline
    problem; a Nod heavy tank is a separate additions call that would dilute the
    cheap-harass doctrine. Not needed.
  - **Roster impact — nothing obsoleted, but ⚠ WATCH THE RECON BIKE.** The Light
    Tank is purely anti-*armor* (AP cannon = 25% vs infantry), so the Buggy
    (anti-inf MG), Flame Tank (anti-soft), Stealth Tank (cloak), and Arty/SSM
    (siege) all keep their niches untouched. **The one unit pushed is the Recon
    Bike (TDBIKE):** pre-buff it actually *out-DPSed* the Light Tank (0.50 vs 0.42,
    TDDragon rockets); post-buff the Light Tank beats it on DPS *and* HP *and*
    armor for +100 credits, leaving the Bike's edge as **purely its Speed 16** (vs
    the Light Tank's 7 — 2× faster) plus earlier tech (TL2 vs TL3) and 100 cheaper.
    So the Bike's identity narrows from "efficient anti-armor" to "pure fast
    harasser." **Net positive** — pre-buff Nod had no *durable* anti-armor line
    (only the fragile Bike + 110hp Stealth Tank); the buffed Light Tank fills that
    hole, making the roles MORE distinct (Light = hold line / Bike = raid-kite /
    Stealth = ambush). **Action: ship the ROF fix as-is; watch the Bike in
    playtest. Do NOT pre-emptively buff it** — if it feels redundant after real
    games, lean into its speed identity, but it likely holds on mobility +
    earliness alone.

### Light / harass vehicles

| Unit | Faction | Cost | HP | Armor | Speed | Weapon | Warhead | Note |
|---|---|---|---|---|---|---|---|---|
| JEEP | Allied | 600 | 150 | light | 10 | M60mg | SA | anti-inf scout |
| TDJEEP Hum-vee | GDI | 400 | 150 | light | 12 | TDM60mg | TDSA | cheaper+faster than RA Jeep |
| TDBGGY Buggy | Nod | 300 | 140 | light | 12 | TDM60mg | TDSA | cheapest harasser, TL4 |
| TDBIKE | Nod | 500 | 160 | wood | 16 | TDDragon (AP) | TDAP | fast anti-tank harass |
| APC | Allied/Sov | 800 | 200 | heavy | 10 | M60mg | SA | transport |
| TDAPC | GDI | 700 | 200 | heavy | 14 | TDM60mg | TDSA | faster, cheaper transport |
| TDSTNK Stealth | Nod | 900 | 110 | light | 12 | TDStnkDragon b2 (AP) | TDAP | **cloaks**, AA+AG missiles, glass |

**Findings:**
- **🟢 F4 — GDI/Nod light vehicles are better per-credit than RA's** (cheaper,
  faster, same HP). Reinforces GDI/Nod as the mobility/harass factions and
  partially offsets their slower economy. Probably *fine* — it's the doctrine —
  but watch Buggy/Bike spam in playtest.
- The Stealth Tank is a unique Nod tool (cloak + can shoot air) but is glass
  (110hp light) — dies instantly once revealed. Self-balancing.

### Artillery / siege

| Unit | Faction | Cost | HP | Weapon | Dmg | ROF | Range | Warhead | Note |
|---|---|---|---|---|---|---|---|---|---|
| ARTY | Allied | 600 | 75 | 155mm | 150 | 65 | 6 | HE | glass cannon |
| TDARTY | Nod | 450 | 75 | TD155mm | 150 | 65 | 6 | TDHE | **cheaper** same output |
| TDMLRS | GDI | 800 | 100 | TDMlrsRocket b2 | 75 | 80 | 6 | TDHE | homing, long, durable |
| TDMSAM SSM | Nod | 750 | 120 | TDHonestJohn | 100 | 200 | **10** | TDFIRE | napalm siege, huge range |
| V2RL | Soviet | 700 | 150 | SCUD | 600 | 400 | 10 | HE | one big hit, slow reload |

- **🟢 F5 — Nod artillery (TDARTY) is a cheaper Allied artillery** (450 vs 600,
  identical weapon). Minor Nod economy win on siege. Likely fine.

### Aircraft

| Unit | Faction | Cost | HP | Weapon | Ammo | Note |
|---|---|---|---|---|---|---|
| HELI Longbow | Allied | 1200 | **225** | Hellfire (AP) | 6 | durable gunship |
| HIND | Soviet | 1200 | **225** | ChainGun (SA, ROF3!) | 12 | infantry shredder |
| TDORCA | GDI | 1200 | **125** | TDStnkDragon b2 (AP) | 6 | fragile |
| TDHELI Apache | Nod | 1200 | **125** | TDApacheGun b2 (TDHE) | 15 | fragile |

- **🟠 F6 — GDI/Nod aircraft are far more fragile than RA's** (125 vs 225 HP at
  the same 1200 cost). Against AA (and the RA SAM/AGUN line), the Orca and
  Apache evaporate roughly twice as fast as the Longbow/Hind. This is the one
  place GDI/Nod are clearly *under*-statted cross-faction. TD-authentic (TD
  aircraft had low HP), but a candidate for a parity bump.
  - **Damage per ammo load is fine** (effective, after Verses): vs heavy —
    Longbow 240 / Orca 180 / Hind 120 / Apache 94; vs infantry — Hind 480 /
    Apache 326 / Longbow 72 / Orca 45. Roles are cleanly differentiated (Orca =
    GDI anti-armor gunship, Apache = Nod infantry shredder) and each TD heli is
    within ~75% of its RA counterpart's specialty. **Firepower is not the
    problem — survivability-at-equal-cost is.** Do NOT buff heli damage.

### Air defense (AA structures) — analysed 2026-06-19

Aircraft (the combat helis) are **`heavy` armor**, which is decisive: TDHE does
only 25% vs heavy. Effective anti-air DPS vs a heavy heli (per ~60 ticks):

| Faction | AA structure | HP | Cost | Tech | AA weapon | DPS vs heli |
|---|---|---|---|---|---|---|
| Allies | AA Gun | 400 | 600 | 5 | ZSU-23 (AP) | **150** |
| Soviet | SAM Site | 400 | 750 | 9 | Nike (AP) | **150** |
| **Nod** | SAM (TDSAM) | **200** | 750 | 6 | TDNike (TDAP, ROF **50**) | **60** |
| **GDI** | Adv. Guard Tower (TDATWR) | 300 | 1000 | 4 | TDTowTwo (**TDHE**, AA+AG) | **45** |

- **🟠 F7 — Nod's SAM is ~40% the air-defense of the RA SAMs**, on half the HP
  (200 vs 400), same 750 cost. Root cause: TD-authentic `ROF=50` on TDNike vs
  the RA Nike's 20 → 60 DPS vs 150. Nod is badly under-defended vs air.
- **🟠 F8 — GDI has no dedicated AA; the AGT is its only answer and is weak vs
  heavy** (TDHE = 25% vs heavy) → 45 DPS vs helis AND 45 vs tanks, despite being
  the priciest defense (1000). **The same 25%-vs-heavy number makes the AGT a
  poor anti-tank tower too** — this is why GDI ground defense feels thin.
  Mitigant: the AGT is **dual-role (air+ground)**, so GDI naturally fields
  *several*, and aggregate AA across 2-3 towers approaches a single RA SAM.

**The compounding problem:** TD factions are weaker on *both* sides of the air
war — fragile attack helis AND weak AA defense. Fix air as one system.

### v4.0 air-balance plan — DECIDED 2026-06-19 (Luke)

Two AA buffs + one heli price-cut + zero weapon-damage changes. All
identity-safe (the "fragile air" pillar is preserved on offense; the buffs are
defensive).

| Item | Fix (single dial) | Numbers |
|---|---|---|
| **F7 Nod SAM** | TDNike `ROF=50 → 20` (RA parity) | 60 → 150 DPS vs heli. Later: HP 200→300 if still too fragile. |
| **F8 GDI AGT** | **Dedicated AGT warhead** cloned from TDHE with **vs-heavy 25% → 50%** | 45 → **90** DPS vs *both* helis and tanks. Fixes AA + the thin ground-defense in one change. Modest ("a little"), not Obelisk-tier. |
| **F6 GDI/Nod helis** | `Cost 1200 → 950` (NOT an HP buff) | HP-per-credit parity with RA helis (225/1200 ≈ 125/950). Keeps 125 HP = "fragile air" identity; fixes the equal-cost-half-HP unfairness as a price correction. |

**Why a dedicated AGT warhead, not bumping TDHE:** TDHE is shared by ~12 weapons
(Apache gun, artillery, SSM, MLRS, grenadiers, flame). Bumping it globally would
buff half the GDI/Nod arsenal. Clone TDHE → an AGT-only warhead so only the
tower changes. GDI keeps **only** the AGT (TD-authentic); the per-tower bump +
its natural dual-role quantity cover both air and ground.

**Why cost-cut not HP-bump on the helis:** "fragile air" is a *documented
intended weakness* for both GDI and Nod (counterweight to GDI early armor / Nod
cheap-cloak harass). Raising HP to 225 erases it; cutting cost makes them
fairly-priced expendable glass cannons and gives the TD factions a distinct
cheap-air doctrine. Hold the HP bump (125→~190) in reserve if playtest shows
they still "feel like wasted money" individually.

### Infantry (summary — not matchup-decisive, cheap & spammed)

- TD infantry are slightly worse: TDE1 Minigunner range 2 vs RA E1 range 3,
  speed 3 vs 4; TDE3 Rocket 25hp vs RA E3 45hp and speed 2 (slowest in game).
- Net: GDI/Nod infantry are marginally outranged/outpaced but cost the same.
  Low priority — infantry trades are dominated by buildings (pillbox/turret)
  and tanks, not 1v1 infantry duels.
- **✅ DECIDED v4.0 (Luke, 2026-06-19): TDE1 Minigunner → match the E1 Rifleman.**
  `TDM16` Range 2→3 and TDE1 Speed 3→4 (everything else already identical:
  50hp/100cr/dmg15/ROF20). The basic backbone rifleman isn't a faction-identity
  piece — it should be at parity, and TDE1 was strictly-dominated (shorter range +
  slower, zero compensation). Documented TD-authentic deviation. **Only the basic
  Minigunner** — specialist TD infantry (TDE3 Rocket etc.) keep their TD stats.

### ⚠ META PRINCIPLE — TechLevel is NOT a balancing lever (Luke, 2026-06-19)

**Skirmish games are played at TechLevel 10**, so "available earlier" (a lower
unit TechLevel) confers **no real advantage** — both factions have everything from
the start. Do NOT use earliness to justify a weaker stat line; that compensation
doesn't exist in the actual meta. **Real levers: Cost, stats (HP/ROF/range/speed),
and prerequisite BUILDINGS** (the prereq chain still has to be built at TL10).
This retroactively tightens several findings (Turret, Mammoth) — see inline.

### Defensive structures — Nod Turret vs Allied Turret (DECIDED 2026-06-19)

**✅ MATCH THE ALLIED: `TDTurretGun` ROF 60 → 50.** HP is already equal (TDGUN's
`Strength=200` doubles to 400 at runtime via `bdata.cpp:4743` = the Allied GUN's
400), as are cost/range/damage **and cloak detection** (both have `Sensors=yes` —
*all* anti-ground defenses on every faction already detect cloak; correcting an
earlier note that implied it was Nod-only). The ONLY remaining gap was ROF (Nod 60
vs Allied 50 = 17% less DPS). At TL10 there is no "earlier" offset (see meta
principle above), so the Nod Turret was simply **600 credits for an inferior
defence** — and it's a defining early structure. Matching ROF makes it true parity.
⚠ **General lesson:** always apply the ×2 TD-building-HP doubling before comparing
any TD structure's HP to an RA one.

### Nod Flame Pillbox — NEW anti-infantry defence (DECIDED 2026-06-19)

**✅ Give Nod a Flame Pillbox** — a Pillbox-chassis bunker firing Nod's TD flame
weapon. **Fills a real, persistent hole:** Nod's only static defence is the anti-
*armor* Turret (TDAP = 25% vs infantry); every other faction has an early anti-
*infantry* emplacement (Allied Pillbox, Soviet Flame Tower, GDI Guard Tower) but Nod
had **none** — and the Obelisk (TL7) is no answer (slow single-target charge, swarmed
by infantry; see `[[project-tdobli-verification]]`).

**Why the pillbox over the Soviet Flame Tower (the rejected alt):** the Pillbox
chassis is compact/cheap (400hp wood, ~400cr) and **neutral-looking** (reads as a
Nod bunker, not an obvious Soviet tower), and using Nod's own flame weapon
(`TDFire` warhead + `TDFLAME-N` anim) is thematically airtight — Flame Tank /
Flamethrower / Chem identity. `TDFire` has **area splash (Spread 8)** = ideal vs
infantry *swarms* (the exact Obelisk weakness).

**Implementation:**
- **Nod-specific structure** — can't re-weapon the shared Allied `PBOX` (would hit
  Allies); needs a cloned Nod pillbox variant (Owner=BadGuy, prereq TDHAND) OR an
  owner-conditional weapon on PBOX. More work than the FTUR owner-open would've
  been, but yields a bespoke Nod structure.
- **Dedicated flame weapon — RANGE IS THE CATCH.** `TDFlameTongue` is **range 2**
  (fine for the mobile Flame Tank, too short for a static defence — buffed range-3
  infantry would outrange it and shoot it for free). Clone it to a flame-bunker
  weapon: keep `TDFire` warhead + flame anim, **bump range to ~3-4** (same
  clone-the-weapon move as the dedicated AGT warhead).
- Cost ~400 (pillbox), TL2, tune later.

Result: Nod gets the anti-armor Turret + anti-infantry Flame Pillbox pair every
other faction has — parity, not power-creep (warheads don't overlap: AP vs Fire).

---

## Cross-cutting: the economy asymmetry

Already documented in `[[project-balance-deferred-to-v1]]`
(`[[project-tdproc-tdharv-shipped]]`): TD harvesters **dock** at the refinery
(full TD plumbing port) while RA harvesters **auto-dump**. RA's income *rate* is
therefore higher → Allied/Soviet economies snowball faster than GDI/Nod's. This
is TD-authentic, not a bug, and it is the **counterweight to F2/F4**: GDI/Nod
get cheaper/earlier/faster units but build them off a slower bank.

Luke's stated lean (2026-05-30): **lean into it** (slower-economy/cheaper-army
as GDI/Nod flavour, tune unit costs to net even) with a touch of harvester
tuning — keep the dock mechanic. Don't auto-dump the TD harvester.

> **⚠ NEW PROPOSAL 2026-06-16 (Luke) — EQUALISE instead of lean-into.** Rather
> than auto-dumping the TD harvester (speed GDI/Nod *up*), make the **RA
> harvester also dock** (slow RA *down*): dwell on the RA harvester's
> tilted-bucket unload frame and drip credits over a matched time `T`, so both
> sides have the same per-cycle dwell. Equalises the economy *and* slightly cools
> RA's famously fast tempo (Luke wants the slower pace). **Balance interaction:**
> this DIRECTLY REMOVES the counterweight above — if the economies are equal,
> GDI/Nod's cheaper/earlier/faster units (F2/F4) and the GDI Mammoth are no longer
> offset by a slower bank, so the unit-cost / Mammoth reasoning in this doc must be
> re-derived if this lands. Decide deliberately. Tracked in the harvester-logic
> workstream — see `docs/chokepoint-reservation-design.md` CHECKPOINT 2026-06-16.

> **✅ SHIPPED in v3.0 (2026-06-18) — the equalise landed.** The harvester docking
> overhaul made every harvester dock + unload visibly, with dock times halved and
> **made equal for every harvester-and-refinery combination** ("both sides'
> economies in step... unit costs comparable across factions"). **So the economy
> counterweight is GONE.** Every GDI/Nod discount that was justified as
> "compensation for a slower economy" must now be re-derived against the equal
> baseline — keep it only if a *different* justification (doctrine, roster depth)
> holds.

### v4.0 cross-faction cost re-derivation (post-v3.0 equal economy)

Going unit-by-unit; the test is "was this discount economy-compensation (now
remove) or genuine doctrine/roster flavour (keep)?":

- **GDI Mammoth (F1) — DECIDED 2026-06-19:** Speed 5→4 (match Soviet); **keep Cost
  1500** — re-justified by *roster depth* (Mammoth is GDI's only real heavy hitter
  vs Soviet's Heavy Tank/V2/Tesla/Mammoth), not economy. See F1 above.
- **GDI APC (TDAPC) — DECIDED 2026-06-19:** **keep Cost 700** (cheaper than Allied
  800) but **Speed 10 → 8** — the cheaper price is now earned by being *slower*
  (Allied APC = pricier+faster; GDI = budget+sluggish). Also resolves the
  long-standing "GDI APC too fast" feel (was 14 → 10 → now 8; still above the TD
  tank line at 7, below the Hum-vee scout at 12). Keep TL4.
- **Remaining F4 set** (Buggy/Bike/Hum-vee/arty) — still to review against the
  equal baseline; mostly low-stakes doctrine discounts, likely keep.

**Pattern emerging:** GDI keeps its *earned* edges (cost where roster-justified,
earliness as identity) but loses *gratuitous* edges (speed advantages with no
rationale). Speed is becoming the preferred dial over cost for these.

---

## Proposed v1.x balance pass — phased

The honest constraint: most of this needs **playtest numbers**, not just
spreadsheet DPS. So the plan front-loads the one change that's unambiguous from
the data, then sets up measured iteration for the rest.

### Phase 0 — instrument (no stat changes)

- Confirm Track A AI fixes are in (the AI must field full armies for matchups to
  be observable). If not, that's a prerequisite — see `ai-improvements.md`.
- Run a batch of cross-faction skirmishes (GDI vs Soviet, Nod vs Allied, mirror
  + cross) and log who wins, when, and on what unit. Use the screenshot/Deck
  loop. Capture reports into `balance-v1-notes.md`.

### Phase 1 — the unambiguous fix (F1) — ✅ CLOSED, no change shipped

**DECISION 2026-06-03 (Luke):** keep TDHTNK at Cost 1500 / Speed 5. The
cheaper-and-faster Mammoth is accepted as the deliberate counterweight to the
GDI/Nod docking-economy handicap (see F1 above + the economy section). The
analysis below is retained for context but the cost/tech bump is **not** being
applied. Revisit only if playtest shows the Mammoth dominating despite the
slower economy.

**GDI Mammoth (TDHTNK):** bring it into line with the Soviet Mammoth it
directly competes with. Recommended single-dial-first:
- `Cost=` 1500 → **1700** (match 4TNK). Removes the cheaper-AND-better problem;
  keeps the faster + SelfHealing identity as GDI's flavour edge.
- If still dominant after playtest, second dial: `TechLevel=` 5 → higher (the
  TL5-vs-TL10 timing gap is arguably the bigger lever than cost). Note this
  deviates from TD build-level authenticity — document the reason.

This is the only change I'd ship *before* playtest data, because it's
provable from the numbers (strictly-better unit, same role, same engine).

### Phase 2 — timing & air parity (needs playtest to confirm magnitude)

- **F2 (GDI armor timing):** if cross-faction games show GDI snowballing on
  early Mediums/Mammoths, nudge `TechLevel` on TDMTNK (3→4/5) and/or TDHTNK.
  Watch the economy counterweight first — slower GDI banking may already
  absorb this.
- **F6/F7/F8 (air parity) — DECIDED for v4.0, see "v4.0 air-balance plan" above.**
  F6 resolved as a **cost-cut** (1200→950), not a Strength bump — keeps the
  fragile-air identity. F7 (Nod SAM ROF 50→20) and F8 (GDI AGT dedicated warhead,
  vs-heavy 25→50) are the two AA buffs. HP bumps held in reserve.

### Phase 3 — doctrine tuning (lowest confidence, most playtest-dependent)

- **F3 (Nod light tank): ✅ DECIDED v4.0 — `TD75mm` ROF 60→40** (see F3 above).
  The text below is the pre-decision framing, retained for context.
- **F3 (Nod light tank) [pre-decision framing]:** decide whether Nod's weak armored ceiling is
  acceptable flavour (cheap harass doctrine + Buggy/Bike/Stealth/Flame toolkit)
  or whether TDLTNK needs a small `Cost` cut / ROF nudge to stay relevant vs
  Allied armor. Lean: leave it, lean on the cheaper toolkit, revisit only if
  Nod loses the armor midgame consistently.
- **Economy net-even pass:** with unit costs as the dial, tune so GDI/Nod's
  cheaper-army offsets their slower-bank across a full game (memory lever #1).
- **F4/F5 (cheap GDI/Nod light vehicles & arty):** likely leave as doctrine;
  only touch if Buggy/Bike/Hum-vee spam proves oppressive.

### Tank pace (carry-over from `balance-v1-notes.md`)

TD tanks run at `Speed=7` (TD MPHType/2) vs the Allied Light's 9. Luke endorsed
keeping TD vehicle speeds at the MPHType-derived values
(`[[project-balance-deferred-to-v1]]`) — at TD's true pace they'd be kited by RA
armour. **Do not reduce TD vehicle speeds.** The open question is line-wide pace
feel, not per-unit; defer to playtest.

---

## One-glance priority list

| # | Finding | Severity | Confidence from data | Lever | Phase |
|---|---|---|---|---|---|
| F1 | GDI Mammoth > Soviet Mammoth (cheaper/faster/earlier) | 🟠 re-derived | high | **Speed 5→4 (match Soviet); keep Cost 1500** (roster-depth, not economy) — Luke 2026-06-19 | 4.0 |
| F2 | GDI armor available too early (TL3 Medium / TL5 Mammoth) | 🟠 med | med | TechLevel | 2 |
| F6 | GDI/Nod aircraft fragile (125 vs 225 HP) | 🟠 med | high | **Cost 1200→950** (v4.0, decided) | 4.0 |
| F7 | Nod SAM weak vs RA SAMs (60 vs 150 DPS, half HP) | 🟠 med | high | **TDNike ROF 50→20** (v4.0, decided) | 4.0 |
| F8 | GDI AGT weak vs heavy (45 DPS air & ground; no dedicated AA) | 🟠 med | high | **dedicated warhead vs-heavy 25→50** (v4.0, decided) | 4.0 |
| F3 | Nod mainline tank DPS-starved | 🟠 med | high | **TD75mm ROF 60→40** (v4.0, decided) | 4.0 |
| Econ | TD-dock vs RA-auto-dump income gap | 🟡 design | high | cost net-even / lean in | 3 |
| F4/F5 | GDI/Nod light vehicles & arty cheaper per credit | 🟢 low | high | leave (doctrine) | watch |

**Bottom line:** the data exposes exactly one provable imbalance worth fixing
pre-playtest (F1, the GDI Mammoth) plus a coherent set of design-level
asymmetries (GDI = durable early armor / fragile air / slow economy; Nod =
cheap harass / weak heavy armor / slow economy) that mostly self-counterbalance
and should be *confirmed by playtest* before tuning. The cross-faction model is
not broken — it's lopsided in one unit and otherwise asymmetric-by-design.
