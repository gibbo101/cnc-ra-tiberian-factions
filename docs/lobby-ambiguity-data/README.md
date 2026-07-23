# Lobby ambiguity — overnight evidence (2026-07-23)

UNCOMMITTED working data for `docs/lobby-ambiguity-findings.md`. Safe to delete.

- `resolver.py FILE...` — exact offline port of the in-DLL `TF_Resolve_Lobby_Ambiguity`.
  Prints per-cycle branch + PASS/WRONG/UNDECIDED vs ground truth, and a tally.
  Run: `python3 resolver.py batch2-results.txt batch4-results.txt batch5-results.txt`
  Result: 28 ambiguous, PASS=28 WRONG=0 UNDECIDED=0 (branches R=20 F=5 M=3).
- `verdict3.py` — compares individual rules (majority / maxRefs / minRefwin / combined).
- `analyze.py` — Route-A byte-diff of candidate records (shows the ~55 differing offsets).
- `batchN-results.txt` — captured scans: each ambiguous CAND line is `diff:refs(exact):refwin`.
  Ground truth is the cycle's `gt=` (row2 difficulty + fixed Hard row3).
- `first-ambiguity-full-records.log` — the first reproduction with full 168-byte record dumps.
- `dcjd-forum-reply-draft.md` — draft reply, pending Luke's review.
