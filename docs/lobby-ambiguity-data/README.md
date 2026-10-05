# Lobby ambiguity evidence

Data behind `docs/lobby-ambiguity-findings.md`.

- `resolver.py FILE...`: an exact offline port of the DLL's `TF_Resolve_Lobby_Ambiguity`. It prints
  each cycle's branch and PASS / WRONG / UNDECIDED against ground truth, then a tally. Run
  `python3 resolver.py batch2-results.txt batch4-results.txt batch5-results.txt`: 28 ambiguous,
  PASS 28, WRONG 0, UNDECIDED 0.
- `test_resolver.c`: the C harness for the same logic.
- `batchN-results.txt`: captured scans; each ambiguous CAND line is `diff:refs(exact):refwin`, and
  the cycle's `gt=` is the ground truth.
- `overnight-2026-08-01-results.md`: the 2026-08-01 overnight run.
