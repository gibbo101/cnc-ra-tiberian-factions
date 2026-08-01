# Overnight autonomous run, 2026-07-31 23:00 → 08-01 05:45 — results

Autonomous desktop session (scrot + xdotool): 43 scripted skirmish cycles against the
resolver build. Build under test = the DLL Luke deployed 23:02 (md5 c4b8edf6...), i.e.
main with the V-branch vector-triple resolver, the eb5d6d8 Cell_Coord fix, and the
other session's zone-filter placement work in the shared tree.

## Method

One client session per stretch. Every cycle: play a match (idle human, 3 AIs — GDI,
Nod, USSR across Easy/Medium/Hard), match ends, back to the SAME lobby, change ONLY
the difficulties (factions/colours/teams untouched — DCJD's exact trigger), relaunch,
read the scan block from MOD_DEBUG_AI.txt. Variations: Docklands (7 cycles) and Deep
Six Mega (36), a double-flip (two edit generations before one launch), a post-longest-
match flip, and rosters changed twice (4 AI → 1 AI → 3 AI) early in the night.

## Results — lobby reads

- **43 / 43 reads correct.** Every applied vector (`s1/s2/s3`) matched the lobby
  edit, every HELLO readout matched, faction hijack (Spain→GDI, Turkey→Nod ActLike
  8/9) tracked every reshuffle, junk signature hits were range-rejected every time.
- **0 ambiguous reads.** The client consolidated every copy in place on every edit,
  including the double-flip's intermediate generation and the flip after an
  11,507-frame match. A durable candidate (12038xxx) tracked live values across an
  entire session; heap regions shifted as sessions aged but copies never diverged.
- **Team-field stale copy observed live** (pre-handover, Luke's own session): after a
  teams-only edit, one candidate carried the previous lobby's team values while all
  difficulty vectors agreed — direct proof stale copies survive edits and that only
  the corroborated/read fields decide anything.
- **V branch: zero live firings — still owed.** The scripted single-session
  difficulty cycle does NOT provoke ambiguity under Proton, consistent with DCJD
  ("could not get ambiguity from changing difficulty alone") and the 07-22 finding
  that it needs long-lived heap history. The 43-cycle corpus is a strong base-path
  regression result; the resolver itself remains exercised only by the offline corpus
  (46/46) and DCJD's independent Windows-side replication.

## Results — GDI placement

- **0 PLACE-FAIL lines across all 43 matches**, including an F11,507 Deep Six game
  where GDI (Medium) gathered 22,400 credits with a full base, plus GDI-Hard runs.
  Corroborates the zone-filter verification recorded in known-issues (85883e1,
  verified on the other session's DOCKLANDS run the same evening).
- Observer mode does not exist in the skirmish lobby (host row shows a tooltip only),
  and an idle human dies ~F5-6k, so unattended matches cap there; Deep Six Mega
  stretched one to F11.5k. Deeper late-game GDI evidence still wants a Luke-played game.

## Repo state note (for Luke)

- The V-branch resolver code in `redalert/dllinterface.cpp` was swept into the OTHER
  session's commit `ec3324a` ("Nod paratroops are their own superweapon...") at 23:34
  and pushed — a `commit -am` side-sweep, the hazard `project-workshop-publish-state`
  warns about. The code is correct and tested (harness 46/46), but its commit message
  says nothing about it. Consider a follow-up commit note or amend strategy at your
  discretion.
- Still uncommitted (this session, per the no-commit rule): `test_resolver.c` (V-branch
  mirror), `lobby-ambiguity-findings.md` (addendum), `dcjd-forum-reply-2-draft.md`,
  and this file.
- Ops: GNOME auto-lock was disabled for the run and RESTORED (300s/enabled) at 05:40;
  game exited cleanly; no deploys, no Deck, no pushes from this session.
