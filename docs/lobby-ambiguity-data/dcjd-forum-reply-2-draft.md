# Draft reply to DCJD posts #5 and #6 (2026-07-31)

> Status: DRAFT. Luke edits and posts. No em dashes. Covers: the methodology
> question from #5, the base-pointer refinement, the std::vector finding from
> Update 2, and one question back (platform confirmation).

---

Good news on both updates, and yes on your methodology question: every
reproduction cached the lobby settings at setup time and the resolver's pick
was scored against that cached ground truth, never against itself. The 28
ambiguous cases plus 18 clean cycles were also replayed through the actual
compiled resolver source afterwards, same result, zero wrong.

Your base-pointer refinement explains a gap in my own numbers. I was anchoring
the exact-referrer check on the AIPLAYER1 record, which is one stride past the
true array start once the human record is counted. That is why my exact
referrer only showed up in about two thirds of ambiguous scans and I needed the
freshness fallback for the rest. You aimed at the array base and got
ExactReferrer every time, which fits: the client's canonical pointer points at
the start of the array, not at the first AI record. I will retarget mine.

Update 2 is the real prize. If the stable referrers are vector triples
(begin at +0, end at +4, capacity at +8), the scan stops being a raw value
match and becomes a structural identification: a hit only counts if begin
lands on the candidate base, begin <= end <= capacity, and (end - begin) is an
exact multiple of 168. That kills the false-positive worry you raised in #5,
and (end - begin) / 168 == num_players is a free cross-check against the
roster the DLL is handed in CNC_Set_Multiplayer_Data. It also hands you
human_player_count for the LAN case without any assumptions.

One structural note: two triples aliasing the same buffer cannot both be
owning std::vectors, so at least one is a copy of the triple or a non-owning
view the client keeps. Does not matter for us, the shape is what we key on,
but it might explain why both stay stable.

One timing observation worth having: in my tests the referrers only exist at
the initial scan. By a deferred re-scan about 90 frames in they were gone. So
scanning from CNC_Set_Multiplayer_Data, as you do, is not just convenient, it
is the window where the signal lives.

Last thing: can you confirm your testing is on native Windows? All my numbers
are from Proton on Linux, so your samples independently reproducing the signal
on Windows would close the biggest caveat I had left on this.

---

## Not in the reply (internal)

- IMPLEMENTED same day: resolver branch V (validated triple at array base,
  ahead of the legacy exact-referrer branch), TRIPLE forensics in dev builds,
  harness still 46/46 on the old corpus. Details in
  `docs/lobby-ambiguity-findings.md`, section "2026-07-31 addendum". If Luke
  posts after the overnight runs land a live V resolution, fold that result in.
- If DCJD confirms native Windows, the "Windows observation" owed in
  [[project-lobby-ambiguity-cracked]] is discharged by their replication
  (~30 samples across their two updates, zero failures reported).
