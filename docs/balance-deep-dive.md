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
  - **DECISION 2026-06-03 (Luke): keep TDHTNK Cost at 1500.** The cheaper
    Mammoth is accepted as a deliberate counterweight to the GDI/Nod economy
    handicap. Even after the harvester travel-speed parity fix (`Tracked=yes`
    + `Speed=6`, commit 166478a), TD harvesters still **dock** (dwell time per
    cycle) where RA harvesters auto-dump — so GDI/Nod bank slower over a game.
    The cost edge offsets that. F1 closed without the cost bump; revisit only
    if playtest shows the Mammoth dominating *despite* the slower economy.
    Mammoth Speed also stays at 5 (the "too fast" impression was the wheeled
    harvester, not the Mammoth — see the economy section).
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

### Infantry (summary — not matchup-decisive, cheap & spammed)

- TD infantry are slightly worse: TDE1 Minigunner range 2 vs RA E1 range 3,
  speed 3 vs 4; TDE3 Rocket 25hp vs RA E3 45hp and speed 2 (slowest in game).
- Net: GDI/Nod infantry are marginally outranged/outpaced but cost the same.
  Low priority — infantry trades are dominated by buildings (pillbox/turret)
  and tanks, not 1v1 infantry duels.

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
- **F6 (TD air fragility):** if Orca/Apache feel like wasted money vs AA,
  consider `Strength=` bump toward RA's 225 (or a middle 160–180). This is a
  parity fix *in GDI/Nod's favour*, the opposite direction from most findings.

### Phase 3 — doctrine tuning (lowest confidence, most playtest-dependent)

- **F3 (Nod light tank):** decide whether Nod's weak armored ceiling is
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
| F1 | GDI Mammoth > Soviet Mammoth (cheaper/faster/earlier) | ✅ closed | high | **Keep 1500** — economy counterweight (Luke, 2026-06-03) | — |
| F2 | GDI armor available too early (TL3 Medium / TL5 Mammoth) | 🟠 med | med | TechLevel | 2 |
| F6 | GDI/Nod aircraft fragile (125 vs 225 HP) | 🟠 med | med | Strength bump | 2 |
| F3 | Nod mainline tank DPS-starved + no heavier tank | 🟠 med | med (TD-authentic) | Cost/ROF or leave | 3 |
| Econ | TD-dock vs RA-auto-dump income gap | 🟡 design | high | cost net-even / lean in | 3 |
| F4/F5 | GDI/Nod light vehicles & arty cheaper per credit | 🟢 low | high | leave (doctrine) | watch |

**Bottom line:** the data exposes exactly one provable imbalance worth fixing
pre-playtest (F1, the GDI Mammoth) plus a coherent set of design-level
asymmetries (GDI = durable early armor / fragile air / slow economy; Nod =
cheap harass / weak heavy armor / slow economy) that mostly self-counterbalance
and should be *confirmed by playtest* before tuning. The cross-faction model is
not broken — it's lopsided in one unit and otherwise asymmetric-by-design.
