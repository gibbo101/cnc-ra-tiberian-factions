# Navy for GDI & Nod — v4.0 design (faction additions)

**Status:** DESIGN LOCKED (2026-06-19), no code yet. Part of the **v4.0 "balance + faction
additions"** milestone. Navy is the first addition designed. Balance numbers are deliberately
provisional — "tweak as we go" once it's in skirmish.

> **⭐ DECISION 2026-06-19 (Luke): RA sub hulls ACCEPTED for Nod.** TD never had any submarine
> (zero sub art — confirmed: TD-Assets has `TDBOAT`/`TDLST` only, no sub), so Nod's subsurface fleet
> CANNOT be a TD port. Per [[feedback-ra-only-when-no-alternative]] this is the explicit no-TD-
> alternative exception: Nod Submarine = the Soviet `SS` owner-opened; Obelisk Attack Sub = the RA
> `MSUB` hull + the TD Obelisk laser. The GDI surface fleet (`TDBOAT` Gunboat + `TDLST` Hovercraft)
> ARE genuine TD types (art present). This is the ONE place the "own TD type, never an RA unit dressed
> up" rule is waived, and only because no TD source exists.
>
> **Implementation status (2026-06-19):**
> - ✅ **(1) GDI Gunboat `VESSEL_TDGUNBOAT` — ENGINE SIDE DONE, compiles clean (art pending).** First
>   vessel port. `defines.h` VesselType enum + `WEAPON_TDTOMAHAWK`; `vdata.cpp` `VesselTdGunBoat` ctor
>   (turret, template VesselPTBoat) + Init_Heap (after VesselCarrier) + One_Time donor (VESSEL_PT
>   NULL-guard); `rules.cpp` registers `TDTomahawk` (IsTDPort); `rules.ini` `[TDBOAT]` (700hp/heavy/
>   Sensors=Yes, Primary=`[TDTomahawk]` = BULLET_TDTOW AG-only homing missile + WARHEAD_TDAP,
>   Secondary=`DepthCharge` = the Allied Destroyer's anti-sub weapon, Prereq=syrd, Owner=GoodGuy);
>   `[SYRD] Owner=allies,GoodGuy`. **`house.cpp` Can_Build: added `powr→TDNUKE/TDNUK2` equivalence** so
>   GDI (which never builds RA POWR/APWR) can satisfy SYRD's `Prerequisite=powr`. **✅ Art-bundle DONE:**
>   `bundle_unit.py BOAT TDBOAT --tileset-donor E2 --build-icon BuildIcon_RA_Gunboat ...` → `TDBOAT.ZIP`
>   (192 frames) + 192 `<TDBOAT>` tiles + `RA_TDBOAT` cameo (validated). Cameo `BuildIcon_RA_Gunboat`
>   (RA's gunboat icon — good fit); text is a placeholder (proper name via CONFIG.MEG later).
>   ⚠ **Playtest-tune:** RA vessels are 16-frame tilesets at `Rotation=8`, but TDBOAT is 192 frames —
>   if facings render wrong, bump the `VesselTdGunBoat` ctor `Rotation` (8→32). **Gunboat = engine +
>   art COMPLETE, ready for the Deck test.** VesselMax=9999, Weapon=100 (rules.ini Maximums) = room.
> - ✅ **(2) Hovercraft `VESSEL_TDLST`** — own vessel type (template VesselTransport, rotation 0),
>   `[TDLST]` (350hp, 5 passengers, Owner=GoodGuy,BadGuy), art bundled (`LST`→TDLST, 4 frames,
>   `BuildIcon_RA_Transport`). Built from either yard.
> - ✅ **(3) Nod Submarine** — `[SS] Owner=soviet,BadGuy` (data-only owner-open; RA hull, accepted).
> - ✅ **(4) Nod Obelisk Sub `VESSEL_TDOBLISUB`** — own vessel type, cloakable SS-hull, Temple-gated
>   (`spen,atek`). **Dedicated clone weapon `[TDObeliskSubLaser]`** (NOT the building's `TDOblsLaser`
>   — independently tunable for balance, Luke 2026-06-19; new `WEAPON_TDOBELISKSUBLASER`). Art = the
>   RA submarine sprite (SS tileset cloned to TDOBLISUB keeping `ss\` frames; `BuildIcon_RA_Submarine`).
>   **⭐ CHARGE WIND-UP IMPLEMENTED** (Luke's ask): the sub surfaces, plays the Obelisk power-up hum
>   (`VOC_TD_LASER_POWER`), and is **vulnerable for ~3s** before the laser fires. Engine-driven in
>   `VesselClass::AI` + gated in `VesselClass::Can_Fire` (new `ObeliskCharge` timer + `IsObeliskCharging`
>   flag on VesselClass) — the building `Charging_AI`/`IsCharging` is BuildingClass-only, so this is the
>   vessel equivalent. `Arm` auto-resets the wind-up per shot. **Needs Deck playtest** (timing/feel).
> - ✅ **(5) `[SPEN] Owner=soviet,BadGuy`** — Nod's `powr` prereq covered by the same `powr→TDNUKE`
>   `house.cpp` equivalence added for the GDI Shipyard.
>
> **ALL navy units engine + art COMPLETE, build green, staged in build/remaster. Ready for the Deck.**

**Why this exists / the divergence:** TD only ever had naval units in *scripted missions*
(`UNIT_GUNBOAT`, `UNIT_HOVER`, neither player-buildable). But Allies and Soviets have full
buildable navies, and the v5.0 AI upgrade will have the skirmish AI *build* a navy — so GDI/Nod
need their own buildable fleets or they're crippled on water maps. This is the deliberate point
where we extend past TD-authentic. Luke's call, 2026-06-19.

---

## Locked roster

| Faction | Production building | Fleet |
|---|---|---|
| **Allies** | Shipyard (`SYRD`) | DD, CA, PT, Transport — *unchanged* |
| **Soviet** | Sub Pen (`SPEN`) | SS, MSUB, Transport — *unchanged* |
| **GDI** | **Allied Shipyard** (`SYRD`, owner-opened) | **TD Gunboat** (`TDBOAT`), **Hovercraft transport** (`TDLST`) |
| **Nod** | **Soviet Sub Pen** (`SPEN`, owner-opened) | **Submarine** (= Soviet `SS`), **Obelisk Attack Sub**, **Hovercraft transport** (`TDLST`) |

The **Hovercraft (`TDLST`) is the shared GDI/Nod transport** — both factions build it from their
naval yard, exactly as RA's Transport (`LST`) is buildable by both Allies and Soviets. Nod needs it
to move land units across water; subs can't transport.

**Doctrine split (mirrors the land game):** GDI = durable **surface** fleet; Nod = **subsurface**
stealth/ambush. GDI gunboat is a destroyer-equivalent with a TD signature weapon; Nod's Obelisk
Sub is a glass-cannon ambusher.

---

## Unit specs

### GDI — TD Gunboat (`TDBOAT`)
Port the TD Gunboat as a **new RA vessel** `VESSEL_TDGUNBOAT` (RA split naval into `RTTI_VESSEL`;
that's the natural home for a surface combat ship, not a floating `RTTI_UNIT`).

- **Art:** TD-Assets `TDBOAT` (XML tileset + HD SRGB ZIP) — confirmed present.
- **From TD `UDATA.CPP`:** 700 HP, Steel armor, slow, ROT 1 (turns like a real boat), turret +
  burst fire, default `WEAPON_TOMAHAWK`.
- **Primary weapon:** keep its **unique TD Tomahawk missile** as the anti-surface / anti-shore punch.
- **Add (ASW parity with the Allied DD/PT):** `Sensors=Yes` + a `DepthCharge` secondary. WITHOUT
  both, a surface ship can neither detect nor hit a cloaked sub — so without this the GDI gunboat is
  **hard-countered** by Nod's subs (and GDI's only combat ship). This is the one non-negotiable
  balance fix in the plan.
- **Net identity:** a GDI destroyer-equivalent — Allied-grade ASW, but a TD missile and TD looks.
- **Build:** flip player-construct ON, give a TechLevel + sidebar cameo, prereq = GDI shipyard.

### GDI + Nod — Hovercraft transport (`TDLST`) — SHARED
TD's Hovercraft *is* an LST — mechanically identical to RA's existing `VESSEL_TRANSPORT`. **Shared
by both GDI and Nod**, built from each faction's naval yard (GDI Shipyard / Nod Sub Pen), mirroring
RA's both-sides Transport. Two impl options: (a) just open RA Transport to GDI+Nod, or (b) port
`TDLST` art so the transport looks TD (art is present). **Defaulting to (b)** for the TD look; (a) is
a valid shortcut.

### Nod — Submarine (= Soviet `SS`)
Owner-open the Soviet sub to Nod (120 HP light, `TorpTube`, `Cloakable=yes`). Deliberately
identical to the Soviet sub — Nod's distinction comes from the Obelisk Sub, not this hull. Reskin
to a Nod look is a future polish item.

### Nod — Obelisk Attack Sub
**Just the Soviet Missile Sub (`MSUB`: 150 HP light, `Cloakable=yes`) with the Obelisk laser bolted
on** (reuse the existing TDOBLI laser weapon — no new weapon code, same chassis, same MSUB art).
Maximally simple by design (Luke, 2026-06-19).

- **Role shift is intentional:** the Soviet MSUB's `SubSCUD` is a long-range base-bombardment
  weapon; the Obelisk laser is short-range, direct-fire, line-of-sight. So this is NOT a missile sub
  — it's a **close-range ambush brawler**: surface next to the target, hit *hard*, vanish.
- **Tuning intent (Luke):** short range, **slow rate of fire**, high per-shot damage. Deadly but
  has to commit.
- **Tech gate:** **Temple of Nod** (same gate as the SSM Launcher) — NOT the Soviet `stek`. Makes it
  a tier-3 Nod payoff, superweapon-flavoured.
- **Implementation nuance (so Soviets keep their missiles):** `MSUB` is one `VesselType`, so we
  can't just edit `[MSUB]`'s weapon globally or the Soviet sub becomes an Obelisk sub too. Two clean
  ways to keep Soviet=missiles / Nod=Obelisk: (a) a new vessel slot that **reuses MSUB art** but has
  its own Obelisk weapon + Nod owner (same art, ~copied stats — the heavier option but cleanest), or
  (b) an **owner-conditional weapon** on the shared `MSUB` type (Nod fires Obelisk, Soviet fires
  SCUD — lighter, data/DLL hook). Decide at implementation; (b) is likely the smaller change.

---

## Buildings
- **GDI → Allied Shipyard (`SYRD`):** add `gdi` to `Owner=`. **Nod → Soviet Sub Pen (`SPEN`):** add
  `nod` to `Owner=`.
- These are RA-art buildings; GDI/Nod using them is a mild visual fidelity leak. **Deferred polish:**
  reskin to TD-style naval yards later. Accepted divergence for v4.0 (Luke OK with it).

---

## Effort / reuse
Contained for the content it adds:
- **One genuinely new vessel** — `VESSEL_TDGUNBOAT` (enum + `vdata.cpp` entry + art register + cameo).
- **GDI transport** — `TDLST` art port or RA Transport reuse.
- **Nod = mostly data:** owner-opens (`SS`, `SPEN`) + one weapon swap (MSUB → Obelisk laser) +
  Temple prereq. **Obelisk laser weapon already exists** (TDOBLI) — reuse, not new code.

## Open / to verify before coding
1. **MSUB availability in our skirmish ruleset** — it's an Aftermath unit (`aftrmath.ini`,
   prereq `stek`); confirm it's live in our skirmish rules before basing the Obelisk Sub on it.
2. **Obelisk laser fired from a mobile vessel** — the laser is a *building* weapon with a charge /
   `Set_Rate` cadence (we hardcoded TDOBLI's). Verify the charge/beam-draw behaves on a moving,
   surfacing firer; the "slow rate of fire" intent maps onto its recharge.
3. **Sub surfacing vs a laser** — subs surface to fire (`VOC_SUBSHOW`); confirm the surface→fire→
   submerge cycle reads right with a beam instead of a missile.
4. **v5.0 AI hook** — set Owner/prereq/Points now so the v5.0 base-builder can field these; actual
   naval AI build logic is a v5.0 task.

## References
- TD source: `SOURCECODE/TIBERIANDAWN/UDATA.CPP` (`UnitGunBoat`, `UnitHover`), `DEFINES.H`.
- RA naval data: `resources/remaster_mods/Vanilla_RA/CCDATA/rules.ini` ([SS][DD][CA][PT][SYRD][SPEN]),
  `aftrmath.ini` ([MSUB]).
- Port pattern: `docs/td-vehicle-port-recipe.md`, `docs/td-port-playbook.md`. Obelisk weapon:
  `docs/td-obli-verification.md`. Vessel-vs-unit split: `redalert/defines.h` (`VesselType`).
