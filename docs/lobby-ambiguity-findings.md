# Lobby difficulty ambiguity — overnight findings (2026-07-23)

**Status: discriminator FOUND and validated over 28 ambiguous reproductions (0 wrong, 0
undecided). Resolver is APPLIED on `main` (2026-07-23) — an ambiguous read now resolves
instead of falling back, with branch U keeping the old fail-closed behaviour. NOT yet
released: it rides the AI milestone release rather than its own patch, because 4.2.0's
on-screen readout already made the fallback visible and the difficulty tiers do not carry
much behavioural weight until W7 lands (Luke, 2026-07-23). That gives it a long local soak
and a Windows confirmation window before it reaches players.**

Companion to `lobby-ambiguity-work-order.md` (the plan) and `lobby-difficulty-ram-spike.md`
(the subsystem). Everything below was measured under Proton on the desktop prefix, dev DLL,
read-only against ClientG.exe. Raw logs + analysis scripts in the session scratchpad.

## The problem (DontCryJustDie was right)

The lobby AIPLAYERn record array exists in several copies in ClientG's heap. Our scanner
corroborates candidates against the roster's colour + country, and fails closed (falls back
to the default difficulty, silently) when full-roster candidates disagree on difficulty. In
DCJD's scenario — change ONLY the difficulty between matches — the stale copy shares colour
and country with the live one, so both pass corroboration and the read is ambiguous.

## Reproduction

- Changing difficulty ALONE does not reproduce it: a quick quit + change overwrites the
  array in place, no stale survives (~13 single-AI cycles, 0 ambiguity, both scan sites).
- Ambiguity needs a real match PLAYED first (heap churn), then the change, then restart —
  exactly DCJD's "plays, loses, comes back and lowers difficulty".
- It is INTERMITTENT and heap-history-dependent. A freshly launched session tends to
  consolidate all copies in place (0 ambiguity over 10+ cycles); ambiguity appeared reliably
  only once the session had accumulated a lingering orphan array. So a player will hit it
  sometimes, not every time.
- Both scan sites (CNC_Set_Multiplayer_Data = DCJD's, and CNC_Set_Difficulty = ours) saw an
  IDENTICAL candidate set every time. Scan-site choice does not dodge the ambiguity.

## Structure of every ambiguous scan

- Several candidates hold the LIVE difficulty; one holds a STALE value (a lone orphan).
- Live-copy count varies (seen 1 to 3). Stale count seen as 1.
- The stale is a PREVIOUSLY-ACTIVE match array: it carries many leftover pointers into its
  neighbourhood (see refwin below); the freshly-allocated live array carries very few.

## Route A — a discriminator byte inside the record: REJECTED

Dumped all 168 record bytes + 32 preceding. Stale vs live differ at ~55 offsets, all heap
pointers or uninitialised tail bytes — no generation counter, no stable semantic field. And
in DCJD's scenario the ONLY thing that legitimately differs between stale and live IS the
difficulty, so there is nothing to key on that we also independently know. Dead.

## Route B — referrer pointers: the useful signal (two variants)

For each candidate we scan ClientG's writable memory for aligned 32-bit pointers.

- **refeq** = pointers landing exactly on the record base. This is the client's live-array
  pointer: when present it was on the LIVE copy in every case, NEVER on a stale. Present in
  ~20/28 ambiguous scans; absent (all zero) in the rest, timing-dependent. Principled.
- **refwin** = pointers into a window around the record. My first idea was that widening
  would catch the array-base pointer more reliably. It does the OPPOSITE of the intuition:
  the STALE copy has the HIGH refwin (~35, leftover from being the active array), the fresh
  live copy has LOW refwin (1–13). So **min-refwin = live, max-refwin = stale**. A freshness
  signal, not a "more referenced = more real" signal. Clean, large gap in every sample.

Note: the referrer pointers are present only at the initial (frame-0) scan; by the deferred
re-scans (frame 90+) they are gone. Fine — identification is needed at the initial scan.

## The resolver (validated 28/28, 0 wrong, 0 undecided)

On disagreement, instead of failing closed, decide in this order — each branch requires its
survivors to agree, so it never picks a stale; the worst case is 'U' == today's fallback:

1. **R — exact referrer**: if a unique difficulty among refeq>0 candidates, that is live.
   (principled; the client's own pointer)  — resolved 20/28.
2. **F — freshness cluster**: drop high-refwin (stale) copies; if the low-refwin survivors
   agree, that is live.  — resolved 5/28.
3. **M — strict majority**: plurality difficulty vector (no other vector ties it). — 3/28.
4. **U — undecided**: fail closed (today's behaviour). — 0/28.

Validated across two lobby structures (3-live-1-stale in one batch; variable incl. 1-live-
1-stale ties in others) and two distinct persistent stales. Offline analysis scripts:
`resolver.py` (exact port of the C logic) + `verdict3.py`. This is strictly safer than today:
today ANY disagreement → silent default; the resolver resolves DCJD's case correctly every
observed time and only ever falls back (never a wrong pick).

**Compiled-C validation.** The actual C source of `TF_Resolve_Lobby_Ambiguity` was extracted
verbatim into a standalone harness (`docs/lobby-ambiguity-data/test_resolver.c`) and run over
every recorded cycle: 46 cycles (28 genuinely ambiguous + 18 no-ambiguity), **PASS=46,
WRONG=0, UNDECIDED=0**. So the compiled logic — not just the Python model — is proven
zero-wrong on all real data. (Ambiguous branch split matches the offline model; the only
difference is batch2's missing refwin field routes its cases through majority instead of
freshness, same outcome.)

## Implementation status

- `redalert/dllinterface.cpp`: the candidate registry, `TF_Count_Referrers()` and
  `TF_Resolve_Lobby_Ambiguity()` all build in release. On an ambiguous read
  `TF_Read_Lobby_AI_Difficulties` counts refeq/refwin per candidate, resolves, and applies
  the resolved vector; branch `U` returns 0 exactly as before.
- The referrer sweep runs **only when the read is actually ambiguous** — it is a full
  address-space scan per candidate, and there is no signal to extract otherwise. In the
  common (unambiguous) case nothing extra runs.
- The raw record dump (`PRE`/`REC` bytes) and the `LOBBYCAND` / `CAND` / `RESOLVE` log
  lines stay `#if TF_DEV_BUILD`. The resolver reads none of those bytes — Route A is dead,
  they are kept only so a future ambiguity can be re-examined offline.
- Both configurations build clean (dev and `-DTF_DEV_BUILD=0`).

## Honesty / residual risk

- All measured under Proton. Native Windows (DCJD's platform) heap/pointer behaviour may
  differ; the SHAPE of the two signals should hold but exact counts are not gospel. The
  exact-referrer (R) branch is the one to trust most cross-platform.
- The long-batch samples share a persistent orphan, so they are not fully independent; the
  first reproduction (a genuinely fresh stale) was also resolved correctly (via majority).
- I could NOT reproduce fresh-stale ambiguity in a clean post-restart session this night, so
  the in-DLL RESOLVE line is validated by CODE REVIEW (faithful port of the 28/28 offline
  logic), not yet by a live ambiguous scan on the resolver build. Worth one confirming run
  when ambiguity next reproduces.
- The freshness (F) and majority (M) branches are empirical (allocator behaviour); the
  fail-closed backstop bounds the risk — the fix is never wrong, only occasionally deferring.

## Outcome

Promoted with all three branches (Luke, 2026-07-23), keeping fail-closed as branch U and
the 4.2.0 on-screen readout surfacing any residual fallback. All-branches rather than
R-only was judged safe because no branch can pick a stale over a live copy — the worst
case is the fallback we already shipped — and because holding the release until the AI
milestone buys a long soak in which a wrong pick would surface locally first.

**Owed before it ships:** one confirming run on a live ambiguous scan (the resolver build
never saw one — the night it was written, sessions stayed clean), and ideally a Windows
observation, since every measurement here is under Proton.
