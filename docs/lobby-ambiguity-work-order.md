# Overnight work order — crack the ambiguous-array problem

**Authored 2026-07-22 22:10. Luke's goal: by 08:00 have the ambiguity cracked and a 100%
stable solution.** Companion to `lobby-difficulty-ram-spike.md` (the subsystem record) —
read that first for the record layout and the shipped design.

Work starts on Luke's go (expected ~23:50, after a context reset). Permission granted to
run until 08:00.

---

## The problem, stated precisely

ClientG.exe's heap holds several copies of the AIPLAYERn record array. One is live, the
rest are stale copies from earlier lobby states. Our scanner corroborates candidates
against the roster handed to `CNC_Set_Multiplayer_Data` — colour (+0x68) and country
(+0x54) must match — and requires every full-roster candidate to agree on difficulty.

DontCryJustDie's counter-example defeats that, and it is correct:

> Host a lobby with Hard AIs, play, lose, return to the lobby, change **only** the
> difficulties to Easy, relaunch.

Colour and country are unchanged, so the stale Hard array and the live Easy array both
pass every gate. They disagree on +0x64, the read is flagged ambiguous, and after four
deferred retries the AIs fall back to the global tier (`tf_ai_difficulty.txt`, else Hard).
The player asked for Easy and silently got Hard.

Current behaviour is fail-closed, not wrong-guess. That is the floor we must not regress.

## What is already ruled out — do not re-attempt

- **Any content-based tiebreak between candidates.** Specifically: "remember the
  difficulty vector applied at the previous launch, discard the candidate equal to it."
  It fixes DCJD's scenario but INVERTS on edit-away-then-edit-back (launch Hard, quit, set
  Easy, set back to Hard, launch: the stale copy is Easy, the live one matches last
  launch's Hard, so the rule picks the stale one). Confidently wrong beats safely failed
  only in the cases you thought of. Analysed and rejected 2026-07-22.
- **More corroboration fields from the roster.** Team/colour/country are the only lobby
  fields the DLL is handed, and DCJD's scenario holds all of them constant by construction.
  No amount of extra roster gating can separate the copies.

The conclusion that matters: **a 100% solution cannot come from the record CONTENT we
currently parse. It has to come from positively identifying WHICH copy the client is
actually using.** Both routes below do that.

---

## Route A — the unknown 100 bytes (do this first)

The record stride is 0xA8 = 168 bytes. We parse five fields: name (0x00), team (0x50),
country (0x54), difficulty (0x64), colour (0x68). **Roughly 100 bytes per record have
never been looked at.** A generation counter, a lobby/session id, an "active" flag, a
back-pointer, or a heap cookie in that space would separate live from stale immediately.

Method — this is an empirical diff, not a guess:

1. Extend the dev-build probe to dump **all 168 bytes** of every validated candidate, plus
   the candidate's **base address** and its containing region's base/size/protect.
2. Run the controlled scenario where ground truth is known: launch with a difficulty
   vector you chose, quit to lobby, change ONLY difficulty to a different known vector,
   relaunch. The live array's difficulties are known by construction; any candidate
   carrying the previous vector is known-stale.
3. Diff the full 168 bytes, live vs stale, at every unknown offset.
4. A discriminator qualifies only if it holds across **every repetition and both
   directions** (Hard→Easy and Easy→Hard), and across a 2-AI and a 4-AI lobby.

## Route B — find the referenced instance

The client code that reads the lobby holds a pointer to the live array. Stale copies are
orphaned. So: for each candidate base address, scan ClientG's writable memory for a 4-byte
little-endian value equal to that address (also check base-0x?? in case the pointer targets
a container that embeds the array).

If exactly one candidate is pointed to, that is positive identification and the ambiguity
is solved outright. Log the referrer count per candidate in the same dump as Route A so
both routes are measured in one pass. Note the cost: a full second pass over the address
space per candidate — fine for a once-per-match-start read, and it only needs to run when
candidates actually disagree.

## Route C — fallback if A and B both come up empty

Not a solution, a mitigation, and only if the above fail: keep fail-closed but make the
retry window much longer and adaptive (rescan until the candidate set collapses to one, up
to some seconds), and log how long stale copies actually survive. If they reliably die
within N seconds, deferred scanning becomes near-deterministic and both mods should widen
their windows. This is the "measure it" plan from the earlier draft, demoted to fallback.

---

## Validation bar — what "100% stable" has to mean

A discriminator is not accepted on a handful of runs. Required before it ships:

- **≥30 launches** covering: difficulty-only change (both directions), difficulty +
  colour change, difficulty + country change, random faction present, random team
  present, 2-AI and 4-AI lobbies, and at least a few first-lobby-of-session launches
  (no stale copies at all — must not regress the clean case).
- **Zero wrong identifications.** A wrong pick is worse than the current fallback.
- Ambiguity must be *resolved*, not merely rarer: the log has to show the discriminator
  choosing correctly in runs where candidates genuinely disagreed. If it never sees a
  disagreement, the test did not exercise the bug and does not count.
- Behaviour when the discriminator itself is unavailable: fall back to today's
  fail-closed path. Never guess.

## Constraints and rules for the run

- Dev-build only (`#if TF_DEV_BUILD`). Nothing here ships without Luke's sign-off, and the
  release path must stay byte-identical to 4.2.0 unless a fix is accepted.
- **Never deploy the DLL while the game is running** — pgrep first (mapped-file corruption).
- GNOME auto-lock kills xdotool input after ~5 min: inhibit idle for the session, restore
  it before finishing. Do NOT unlock a locked session without asking.
- Read-only against ClientG. Never write to another process.
- Desktop rig only; the Deck is not part of this.
- Log everything to `tf_astar.log` / `MOD_DEBUG_AI.txt` in the desktop prefix; archive per
  scenario so runs stay separable.

## Deliverables by 08:00

1. A verdict on Route A and Route B, backed by data — either "this offset/pointer is the
   discriminator, validated over N launches, zero misses" or "ruled out, here is the
   evidence."
2. If cracked: the implementation, behind the existing fail-closed fallback, built and
   deployed, with the validation log.
3. An updated forum reply to DCJD carrying the findings — whichever way it goes. A
   negative result stated with real numbers is still a genuine contribution to that
   thread, and it is the honest outcome if the data does not support a fix.
4. This doc updated with what was learned, and dead ends deleted rather than left under a
   superseded banner.

**Do not overclaim in the morning summary.** If the solution is 100% on 30 runs, say
exactly that — not "100% stable". If it is not cracked, say so first, plainly.
