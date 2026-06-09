# GDI / Nod campaign story — "The Inheritance War" (design, 2026-06-10)

Narrative design for the two hijacked-tab campaigns: **GDI = Aftermath tab** (9 missions,
Allied-variant slots), **Nod = Counterstrike tab** (8 missions, Allied-CS-variant slots).
Mechanics live in `coop-missions-design.md` (gates, ActLike houses) and
`campaign-tabs-research.md` / [[project-missionselect-roster-poc]] (hijack delivery).
Lore researched against the EVA Database (cnc.fandom.com), 2026-06-10.

---

## 1. The lore window (and why it's perfect for us)

Verified canon anchors:

- **RA1 is the canonical prequel to Tiberian Dawn** (Westwood FAQs; Adam Isgreen 2006;
  EA's 2007 Kane's Dossier re-canonised it). The **Allied ending is canon** for the
  Tiberium timeline; the Soviet ending (Kane shoots Nadia, "I am the future") is not.
- **Kane was Stalin's "advisor"** — the grey eminence of the USSR. After the Allied
  victory "nobody sought to locate Stalin's mysterious advisor"; the CIA kept a few
  photos that resurface in GDI's TD-era dossier.
- Nadia's line (Soviet path, but suggestive): the Brotherhood would *"tire of the USSR…
  in the early 1990s."*
- **The USSR was defeated (~1953), forced to disarm, and eventually dissolved into 15
  states.** Timing of the dissolution is unspecified — open space.
- **The 1950s→1995 gap is canonically almost empty.** The only official bridges: GDI's
  covert predecessor *Special Operations Group Echo, Black Ops 9* (active "prior to
  1990", TD manual) and the RA1 Allied-mission-5 newscast where the UN votes 281–7 to
  fund "a Global Defense agency."
- **1995:** the Tiber meteor (Italy) brings Tiberium; Dr. Ignatio Mobius credited with
  its discovery — Kane: *"Discovered by the Brotherhood, that is."* **12 Oct 1995:** the
  UN Global Defense Act founds GDI (first supreme commander: Brig. Gen. Mark Sheppard;
  TD's GDI player character James Solomon transfers in the late 1990s).
- **First Tiberium War: ~1997–2003** (wiki-sourced range), opening with the Vienna Grain
  Trade Center bombing. Nod enters TD controlling 49% of the world's Tiberium.
- Developer precedent for our exact premise: Westwood's cancelled **Renegade 2** drafted
  the *Scavengers* — a faction rising from the collapsed USSR's remnants as **the
  predecessor of Nod**. Non-canon, but it's official-developer territory.
- Aftermath/Counterstrike gave us **Volkov** (cyborg commando — the wiki calls him "a
  forerunner of Nod's Cyborg Commandos"), **Dr. Demitri** (Super Tank), the **Phase
  Transport** (Allied cloaking prototype) and the **MAD/Tesla tanks**. Since we are
  literally hijacking the CS/AM mission slots, we honor their cast and tech.

**Flagged as our invention** (canon gives no answer): the dissolution date (~1991, echoing
Nadia's line), the Soviet hardliner remnant (**the Red Vanguard**, Marshal Orlov), and
the rogue Allied command (**Field Marshal Edric Wessler**). "Operation Drop Shot" and
"the Forsaken" are NOT canon — do not use.

## 2. Setting — 1991–1997, "The Inheritance War"

Forty years after the Allied victory, the husk of the USSR — quietly steered by the
Brotherhood since Stalin — is finally allowed to collapse (~1991). Fifteen successor
states emerge; hardliner garrisons that refuse the end of history keep their RA-era
arsenals and become **the Red Vanguard**. The victorious Allied nations have calcified
into national commands jealous of their prototype vaults (Chronosphere, Iron Curtain,
phase tech). Then, in 1995, a meteor falls at the Tiber, and the UN births **GDI** — a
supranational army that the old Allied commands must arm, fund, and obey. Everyone is
fighting over an inheritance: the Soviet arsenal, the Allied vaults, and the new
green gold. Only one player has been planning the estate sale for forty years.

The two campaigns run through the same events from both sides and funnel into TD's
opening newscast. Where they contradict (the finales), the **GDI path is canon** — TD
requires GDI's funding and Ion Cannon to survive, and the Temple rises at Sarajevo anyway.

**Faction casting (engine):** player house Spain/ActLike-GDI or Turkey/ActLike-Nod;
Allies = Greece/England/Germany houses with the vanilla RA roster; Soviets = USSR/Ukraine
houses with the vanilla Soviet roster. Four factions coexist per `coop-missions-design.md`.
GDI/Nod field our TD rosters — in-fiction, GDI's "next-generation" gear is the
consolidated classified prototype programs of the Allies (the Mammoth lineage descends
from RA heavy armor), and Nod's arsenal is Tiberium money spent well.

**Briefing voices:** GDI — Brig. Gen. Sheppard (with a young Lt. Solomon as recurring
field liaison flavor). Nod — **Seth** delivers most briefings (his pre-TD rise), **Kane**
appears only at hinge moments. **Greg Burdette** (WWN, Nod agent) cameos in the
media-op missions. **Mobius** appears in both campaigns.

---

## 3. GDI campaign — "FIRST LIGHT" (Aftermath tab, 9 missions)

Player: an unnamed founding GDI field commander. Arc: GDI is born underfunded and
unwanted, fights all three of the old world's ghosts, and earns the standing it holds
at TD's open — while every victory quietly feeds Kane's design.

| # | Title | Year / locale | Theatre | Enemies | Shape |
|---|---|---|---|---|---|
| 1 | **Stone from the Sky** | 1995, Tiber valley, Italy | temperate | "raiders" (unbranded Nod) | No-base escort: protect Mobius's survey convoy to the meteor crater. Tutorialises Tiberium hazard (infantry damage, first blossom tree). |
| 2 | **The Quiet Inheritance** | 1995, Ukraine | temperate | Soviets | First base mission: UNGDA disarmament — seize a Red Vanguard nuclear depot. Beat: the ledger shows warheads already sold to an unknown buyer. |
| 3 | **Property of the Alliance** | 1996, Bavaria | temperate | Allies | The friction mission: Wessler's command refuses to surrender the Allied prototype vault to GDI custody. Capture the vault *intact*; briefing stresses minimal force against yesterday's comrades. |
| 4 | **Scorpion Rising** | 1996, Carpathians | temperate | Nod | The raiders unify under the scorpion. Destroy the first open Nod base — built around a worked Tiberium field (enemy harvester economy on display). |
| 5 | **The Białystok Rehearsal** | 1996, Poland | snow | Soviets + Nod | Nod fakes a GDI massacre of a remnant enclave; the Vanguard retaliates for real while Burdette films. Survive the assault, then capture the Nod media uplink to expose the op. Foreshadows TD's Białystok scandal. |
| 6 | **Deus Ex Machina** | 1996, Urals | snow | Soviets, then Nod | (Title honors the AM slot it replaces.) Both Nod and the Vanguard converge on the mothballed Volkov cyborg lab. You save the man; Nod escapes with the ReGenesis schematics — the seed of TD's cyborg program. |
| 7 | **The Wessler Defection** | 1996, North Sea coast | temperate | Allies + Nod | Wessler sells the vault and accepts Nod protection: assault an Allied base bristling with Nod tech (an Obelisk on Allied soil; Allied navy offshore). |
| 8 | **Hippocratic Oath** | 1997, Albania | temperate | Nod | Defense: hold Mobius's Tiberium research hospital against waves — creeping Tiberium growth, visceroids from casualties, civilians to keep alive. Sets up TD's hospital arc. |
| 9 | **The Foundation** | 1997, Sarajevo | temperate | Nod | Finale: raze the fortress Nod is raising on the Sarajevo site — the future Temple's foundation — before its earthworks complete. Scripted one-shot **Ion Cannon prototype** unlock. Kane escapes. Stinger: the Vienna Grain Trade Center bombing newscast → TD intro. |

## 4. Nod campaign — "OUT OF THE SHADOWS" (Counterstrike tab, 8 missions)

Player: a rising Nod commander being groomed by Kane (Seth, your superior, takes the
credit — his TD characterisation, earned here). Arc: the Brotherhood liquidates its
Soviet investment, claims Tiberium, arms itself from the old world's vaults, and breaks
GDI's first light. Epigraph (M1 briefing): *"For centuries we have waited to emerge
from the shadows… We estimated the Brotherhood would tire of the USSR by the early
1990s."* — internal memorandum, N. Zelenkov.

| # | Title | Year / locale | Theatre | Enemies | Shape |
|---|---|---|---|---|---|
| 1 | **Tire of the Bear** | 1991, Moscow outskirts | snow | Soviets | The Brotherhood walks out of the state it ran for forty years: extract Nod's assets (bullion convoy, archives, sleeper cadre) from a collapsing army base as hardliners seize it. |
| 2 | **The Tiber Prize** | 1995, Italy | temperate | Allies | Beat the UN survey to the meteor: secure the crater, deploy the Brotherhood's first harvester, bank N credits of Tiberium, exfiltrate before the Allied counterattack. Kane: *"Discovered by the Brotherhood, that is."* |
| 3 | **Seed Money** | 1995, Balkans | temperate | Allies | Economy war: destroy the Allied ore consortium's operations and *seed the valley* — planting blossom trees is an objective. The 49% share starts here. |
| 4 | **Ezekiel's Workshop** | 1996, Bavaria | temperate | Allies (+ late GDI response) | Raid the Allied prototype vault: steal the phase-cloaking prototype (Aftermath's Phase Transport → the seed of the Stealth Tank, "Ezekiel's Wheel"). Thief/engineer mission; first contact with GDI. |
| 5 | **The Sleeping God** | 1996, Urals | snow | Soviets + GDI | The Volkov lab from the other side: take the ReGenesis cyborg data from the Vanguard while GDI interferes mid-mission. (Mirrors GDI M6 — same event, both campaigns.) |
| 6 | **Let Them Hate** | 1996, Poland | snow | Soviets + GDI patrols | The false-flag from the inside: capture GDI armor with engineers, then **only captured GDI units may enter the enclave** to raze it on camera for Burdette's broadcast. The mission GDI M5 cleans up after. Full TD "shake hands with evil" tone. |
| 7 | **Inherit the Iron** | 1997, Caucasus | snow | Soviets | End the Red Vanguard: break Marshal Orlov's fortress and Dr. Demitri's super-heavy arsenal (scripted Iron-Curtained super-tank set pieces), then broadcast Kane's invitation — the Vanguard's soldiers join the Brotherhood. Nod inherits the Soviet arsenal and its manpower. |
| 8 | **First Light, Extinguished** | 1997, Adriatic coast | temperate | GDI + loyal Allies | Finale: destroy GDI's European headquarters and the Ion Cannon ground-control station before the prototype comes online; secure the Sarajevo corridor. Kane: *"For the foreseeable future… I am the future."* Stinger: the same Vienna newscast — both roads lead to Tiberian Dawn. |

## 5. Interlocks and texture

- **Shared events, both sides:** the Tiber crater (G1/N2), the Volkov lab (G6/N5), the
  Poland false-flag (G5/N6), the prototype vault (G3→G7 / N4), Sarajevo (G9/N8).
- **Tech bridges we dramatise:** Phase Transport → Stealth Tank; ReGenesis/Volkov → Nod
  cyborgs; Allied heavy-armor programs → GDI Mammoth; Tiberium wealth → Nod's TD warchest.
- **Mod features as story beats:** Tiberium ecosystem (growth/spread, infantry damage,
  visceroids, blossom trees) debuts in G1/G8/N2/N3; Ion Cannon and the Obelisk get
  scripted hero moments; RA navy appears only in Allied hands (GDI/Nod have none).
- **Difficulty stays behavioural** per [[feedback-difficulty-philosophy]]; no stat-bias
  villains.

## 6. Implementation constraints (recap — don't violate)

- **Hijack only**: re-style existing CS/AM instances; new instances list but cannot
  launch (InstanceServerG resolves from BASE). GDI uses the 9 `Mobius_Aftermath_Allied_Map_Base`
  slots; Nod the 8 `Mobius_Allied_Counterstrike_Map_Base` slots. The USSR-variant groups
  (9 + 8) stay in reserve — bonus missions, interludes, or a second act.
- **CONFIG.MEG same-size rule** for every inner-file edit; compensate bytes via XML
  comments. Mission Select display names = master-text same-length in-place — choose
  titles **no longer than the original mission's name** and pad with spaces. Map each
  title to its slot at implementation time and check lengths then.
- **In-game briefings are free**: the engine reads campaign scenario INIs and the mod's
  CCDATA shadows them by name ([[project-td-skirmish-map-import-findings]]) — all story
  text above fits in `[Briefing]` with no size constraint.
- **Theatres**: temperate + snow only (desert pending the interior-slot swap) — hence no
  Africa missions despite Nod's canon strongholds there; revisit if desert lands.
- **Win/lose/briefing gates**: the 4 confirmed DLL gates (house.cpp:1213/1225,
  scenario.cpp:316/386/394) per `coop-missions-design.md`.
- Authoring: Mobius editor, RA-format `.mpr`/INI scenarios.

## 7. Open questions for Luke

1. GDI player = unnamed commander (briefed by Sheppard) vs. literally young Solomon?
2. Mission count: lock 9/8 as above, or trim to 8/8 for symmetry?
3. Do we want scripted FMV-substitute beats (text crawls / EVA voice) for the stingers,
   or keep everything in briefings?
4. Names "Red Vanguard" / "Marshal Orlov" / "Field Marshal Wessler" — happy, or rename?
