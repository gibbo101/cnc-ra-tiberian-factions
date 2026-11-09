# Lobby difficulty: telling a stale copy from the live one

**Status:** Reference; the resolver ships in 5.0.0. It settled all 28 recorded ambiguous reads (none wrong, none
undecided) and 46 of 46 recorded cycles in the compiled harness. Its vector-triple branch has never fired live.
**Open:** one live ambiguous scan on the resolver build, and one observation on native Windows.

The subsystem is `lobby-difficulty-ram-spike.md`. The problem, the five-step order (vector triple, exact pointer,
freshness, strict majority, fail closed) and the routes that don't work are game-level: see the field manual's
[Per-AI lobby difficulty](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/per-ai-lobby-difficulty.md#stale-copies-of-the-lobby),
Stale copies of the lobby. This doc holds TF's implementation and the measurements behind it. Every measurement
was made under Proton, on the dev DLL, reading ClientG only.

## What the ambiguous scans looked like

- Several candidates held the live difficulty (one to three seen) and one held a stale value; no scan had more than
  one stale copy. Samples covered two lobby shapes (three live and one stale; one live and one stale, a tie) and two
  distinct persistent stale copies.
- The 168 record bytes and the 32 before them hold nothing to key on.
- A freshly launched session tends to overwrite every copy in place: changing the difficulty alone (a quick quit and
  change, about 13 single-AI cycles, both scan sites) gave no ambiguity. Ambiguity came reliably only after a match
  had been played and the session held a lingering orphan array, so a player meets it sometimes, not every time.
- The referrer pointers are there only at the first scan (frame 0). By the deferred re-scans (frame 90 on) they are
  gone, so the resolver runs on the first read.

## The resolver

`TF_Resolve_Lobby_Ambiguity` in `redalert/dllinterface.cpp` runs only when full-roster candidates disagree. The
referrer sweep (`TF_Count_Referrers`) is a full address-space scan per candidate, so nothing extra runs on an
unambiguous read. Each branch takes a value only when all its survivors agree:

The anchor is the candidate's record for its first roster AI (the lowest-numbered `AIPLAYERn` in the roster,
`anchor_n` in `TF_Scan_Process_For_Lobby_Difficulty`), since names carry on across lobbies.

1. **V, vector triple.** The sweep looks for pointers to the candidate's array base
   (`anchor − TF_HumanPlayerCount × 168`) and `TF_Read_Vector_Triple` checks each hit: `begin == base`,
   `begin < end <= capacity`, `(end − begin) % 168 == 0`, and `(end − begin) / 168` equal to humans plus roster
   AIs. Any candidate with a valid triple counts as live. DontCryJustDie's replication saw two such triples per
   array; two owning vectors can't share a buffer, so at least one is a copy or a non-owning view.
2. **R, exact referrer** (`refeq`): pointers exactly on the candidate's anchor record. Present in about 20 of
   the 28 ambiguous scans and always on the live copy. The array base sits a stride per human before that record,
   which is likely why `refeq` missed the rest.
3. **F, freshness** (`refwin`): pointers into a window from four strides before the record to two after. The stale
   copy read about 35, the live ones 1 to 13. Candidates at or under `4 × min + 2` survive.
4. **M, plurality** of difficulty vectors over all candidates (not only F's survivors): the most common vector
   wins when no other vector's count reaches it.
5. **U, undecided**: return 0 slots. That arms `TF_Lobby_Difficulty_Retry` (four re-scans, 90 frames apart); by
   then the referrers are gone, so in practice the read ends at the global tier.

Branch split: the Python model over the 28 ambiguous scans gave R 20, F 5, M 3, U 0. The compiled harness over all
46 cycles (28 ambiguous, 18 not) gives R 20, F 10, M 16, V 0; one batch lacks `refwin`, so its cases route through
majority instead of freshness, with the same outcome. The recorded corpus stores only `refeq`/`refwin` counts, so
V cannot fire on it; V rests on DontCryJustDie's replication (about 30 samples) and the fail-safe branch shape.

Dev builds (`TF_DEV_BUILD`) log the raw record bytes (`PRE`/`REC`), and `LOBBYCAND`, `CAND`
(`base=`/`vecref=`/`ntrip=`), `RESOLVE` and one `TRIPLE ref=/begin=/end=/cap=/nplayers=/ok=` line per referrer hit,
rejects included, so a live run shows whether the strict size equality (humans plus roster AIs) is right: TF's
check has never been seen live. The resolver reads none of the record bytes; they are kept so a future ambiguity can be
re-examined offline.

## Evidence and tools

All in `lobby-ambiguity-data/` (its README says how to run each):

- `resolver.py`: an exact port of the resolver; over `batch2`, `batch4` and `batch5` it gives 28 ambiguous, 28 pass.
- `test_resolver.c`: the resolver's C source in a standalone harness, run over every recorded cycle.
- `batchN-results.txt`: the captured scans, with ground truth per cycle.
- `lobby-ambiguity-data/overnight-2026-08-01-results.md`: 43 scripted play, difficulty-only flip and relaunch cycles on the resolver
  build (double flips and flips after a long match included), 43 reads correct and none ambiguous. Scripted single-session cycling does not provoke the ambiguity under
  Proton. One played session did show a stale copy that differed only in the team field: a stale copy can survive
  without differing in difficulty.

## Residual risk

- Native Windows heap behaviour may differ from Proton's. The shape of the signals should hold, the counts may
  not; the exact-referrer branch is the one to trust most across platforms. DontCryJustDie's replication is
  believed to be on Windows, but that is not confirmed.
- The long-batch samples share one persistent orphan, so they are not fully independent. The first reproduction,
  a fresh stale copy, also resolved correctly (by majority).
- The in-DLL resolver is checked by the compiled harness over recorded data, not yet by a live ambiguous scan.
- F and M are empirical, resting on allocator behaviour. No branch can pick a stale copy over a live one, so the
  worst case is the global-tier fallback. The on-screen `Enemy AI:` line names each house's mode but not its source
  (`lobby-difficulty-ram-spike.md`), so a fallback shows only as every AI on the global mode.
