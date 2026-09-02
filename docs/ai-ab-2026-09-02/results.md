# A/B 2026-09-02, Keep off the Grass, Luke GDI vs 1 Nod AI Hard, 1v1, no cheats

## Game 1: TF A/B 4.0.0 (public release 07-16, no fair fog)
- 21:53 start, ended 16:28 game time, Luke wins.
- Score: Luke gathered 48,516 / killed 101 / razed 13. AI gathered 30,056 / killed 26 / razed 0.
- ~10 min: Nod base visible = airstrip, refinery, 2 power, hand, a few defences. Luke's 11 medium tanks at its door.
- No AI log in this build.
note: game 2 first attempt was Medium (lobby diff=2), aborted ~2 min in; log copied

## Game 2: TF A/B 15 Aug LAN build (ts-units 2c83f4dc), Hard confirmed (IQ=5, slot read diff=3)
- 22:17 start, ended 9:04 game time, Luke wins. Log: g2-hard.txt (frames ~33/s of game time).
- Score: Luke gathered 35,400 / killed 72 / razed 10. AI gathered 16,400 / killed 20 / razed 1.
- AI income ~1.8k/min in BOTH games (4.0.0: 30k/16.5min; 15Aug: 16.4k/9min) -> economy identical, 2 refineries, 3 harvesters.
- Build order: 2x power, refinery, hand, airstrip, gun (F1541), refinery#2 (F3540), HQ (F4135), adv power x2 (F5962, F7737), repair bay (F8494), flame bank, hand#2, refinery#3.
- Cash pinned at $13-$58 from F5963 (~3 min) onward. Only 1 PROD hold (HQ, 45 frames) -> hold theory dead.
- Production: 30 infantry (13 TDE4, 9 TDE1, 6 TDE3, 2 TDE6) vs 12 vehicles (4 LTNK, 4 FTNK, 4 BGGY) + 1 harvester.
- Defences: ONE gun turret all game. Build POOL after F1541 never offered TDGUN/TDSAM again; only TDOBLI (unaffordable).
- Waves: LAUNCH F8340 (~4:12) army=18 (roll), LAUNCH F9975 (~5:02) army=15 (roll). Then army 0-5 for the rest of the game (13 SHUFFLE massing).
- Scouts: 3 infantry dispatched F1741-F2601.
- Luke: "Enemy base had less units, less defences, less harvesters" / "felt like it was vs an easy enemy".

## Game 3: fix build 1 (ai-regression worktree, DLL 9e4f89de = main + value/stage wave floor + defence HIGH claim), Hard confirmed
- ~22:50 start, AI base gone ~F18700 (~9.5 min). Luke wins. Log: g3-fix1-hard.txt.
- Waves: held "no-factory" until the airstrip, then "massing-value" from F3897 to F11980 (army 15->26, value 2700->7850);
  ONE LAUNCH at F12457 army=27 value=8450 (count ceiling + value floor). Wave died (army 13 -> 3 by F15880). No second wave.
- Defences: bunker won HIGH at F3540 (CurB 7), gun HIGH at F8194 (CurB 11) -> 3 defences by F10557 (vs 1 all game before).
- Economy: 2nd refinery F4622, 3rd F10510 (CurB 13). harvQ up to 4. Cash pinned $38-$506 as before. Income unchanged (~1.8k/min).
- Production: 41 infantry (19 TDE4, 5 TDE3, 5 TDE1, 1 TDE6) vs 19 vehicles (6 bikes, 6 arty, 3 LTNK, 2 FTNK, 2 buggies) + 1 heli.
- Read: the mechanics work as designed, but the outcome barely moved. The wave still arrives as a per-unit HUNT trickle and
  27 tier-1 units die to ~11 medium tanks; the AI's ceiling is its income and Nod's one-plane airstrip delivery.
  Next lever = economy (W3): refinery/harvester targets by time, not by building-count ratio; then staging (b).
