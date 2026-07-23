DRAFT reply to DontCryJustDie (for Luke's review; no em dashes; numbers to finalize)

---

You are right about the ambiguous case, and I spent a session running it down rather than
just arguing it, so here is what I found. It is more hopeful than the four workarounds.

First, reproducing it. I could not get ambiguity from changing difficulty alone. When I quit
straight back to the lobby and change only the difficulty, the client overwrites the array in
place and there is nothing stale to find. The ambiguity only appears when a real match has
been PLAYED first, which is exactly your example (creates a lobby, plays, loses, comes back
and lowers the difficulty). Playing the match churns the heap so the new array lands somewhere
else and the old one is left behind. So your scenario is real and mine could not see it until
I actually played a game between the two starts.

Second, the scan site does not save you. I instrumented both CNC_Set_Multiplayer_Data and
CNC_Set_Difficulty and they saw the identical candidate set every time, so calling it later
does not dodge the ambiguity.

Now the useful part. In every ambiguous scan I recorded, the stale copy is distinguishable
from the live one, by two independent signals:

1. The client keeps a pointer to the LIVE array. If you scan the client's writable memory for
   an aligned 32-bit value pointing at a candidate's record, the live array is referenced and
   the stale copies are not. This is the principled one: it is literally the pointer the client
   is using. It was present in roughly two thirds of my ambiguous scans and never once pointed
   at a stale copy.

2. When that pointer is not captured, the stale copy still gives itself away. A stale array is
   one that was the ACTIVE match's array a moment ago, so it is covered in leftover pointers
   from when it was in use. The freshly allocated live array has almost none yet. Counting
   pointers into a small window around each record, the stale sat at ~35 and the live at 1 to
   13 every time, a clean gap. The freshest (least referenced) array is the live one.

Put together as a rule: prefer the referenced candidate; if none, take the low-pointer-density
(freshest) cluster; if that is somehow tied, majority vote; and only if everything is
undecidable, fall back to a default. Across 28 ambiguous reproductions this picked the correct
difficulty every time (referenced pointer resolved 20 of them, freshness 5, majority 3, zero
wrong, zero left to the fallback), and its worst case is the same fallback you already have, so
it never picks a stale value, it just fails safe. No ini setting, no user instruction.

One more thing worth knowing: I could not make the ambiguity appear on demand. A freshly
launched session kept consolidating every copy in place, no stale to find. It only showed up
once a session had been running a while and left an orphaned array behind, which fits it being
an intermittent report rather than every-time.

Two honest caveats. All of my testing is under Proton on Linux, and heap and pointer behaviour
on native Windows may not match mine, so the exact pointer counts are not gospel, the shape of
the signal is what matters. And I would still keep a default-difficulty fallback as the safety
net for the undecidable case, plus I now print each AI's applied difficulty on screen at match
start so if the fallback ever engages the player sees it rather than filing a mystery report.

If you want to try the referenced-pointer check on Windows I am happy to compare notes, that is
the one I would trust most on your platform.
