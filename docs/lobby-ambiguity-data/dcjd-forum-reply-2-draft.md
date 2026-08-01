# Reply to DCJD posts #5 and #6 — POSTED 2026-08-01 (Luke's edit)

> Final posted text below. The original longer draft is in git history
> (b7e089d); internal follow-ups tracked in overnight-2026-08-01-results.md.

Yes, every test was scored against cached lobby settings, never against itself.

Your array-base find explains my missing third: I was anchoring on AIPLAYER1,
one stride past where the pointer actually lands. Retargeted, and adopted the
vector triple as a structural check ((end - begin) / 168 must match the
roster), which also solves your false-positive worry.

Probably an obvious answer but you are testing on Windows? If so between us
that covers everything but Mac (which I believe isn't supported anyway?).

## Watch for in their answer
- Native Windows confirmed = the owed "Windows observation" in
  [[project-lobby-ambiguity-cracked]] is discharged by their ~30 samples.
