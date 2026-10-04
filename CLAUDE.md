# Tiberian Factions: code rules

A fork of Vanilla Conquer (`upstream`) with our code interleaved into EA's and VC's. These
rules keep ours easy to find, easy to read and easy to merge. Machine, deploy and doc-map
notes live in the workspace `../CLAUDE.md`.

## Ours and theirs
- EA and VC code and comments are never edited for tidiness. Touch them only for a
  behaviour change the mod needs, with the smallest diff. `git merge-base HEAD
  upstream/vanilla` and `git blame` tell the two apart.
- Every change inside EA or VC code carries a `// TF:` comment saying why. One marker form,
  so `git grep "TF:"` finds them all.
- A new subsystem that isn't a method of an EA class goes in its own
  `redalert/tf_<topic>.cpp` / `.h` (listed in `redalert/CMakeLists.txt`). The EA file gets
  a marked call.

## Comments (C++, rules.ini, scripts)
- A function or method gets a comment on what it is meant to do: two lines at most.
- Inside a function, only two kinds of comment, two lines at most:
  - the `// TF:` marker on our change to EA or VC code;
  - a trap warning, where changing the line would crash the game or corrupt state.
- Anything longer goes in a doc, and the comment names the doc by file name only
  (`docs/firestorm-design.md`), never a section or line.
- No personal names in code or comments. A port of third-party code may name the project
  it came from.
- No dates, history ("was / now / fixed / reverted"), test narration, restating the code,
  or apology. History goes in the commit message.
- rules.ini entries and script docstrings keep to two lines too. Reference values from the
  source game are data: `TS [RedEye2] Damage=33`.
- Change the code, change its comment in the same commit. Older comments are not a style
  to copy.

## Conventions
- C++ follows the repo's `.clang-format` (Vanilla Conquer's, clang-format 14). Format only
  the lines you changed (`git clang-format`); never reformat EA or VC lines.
- Naming follows the surrounding code: `Class::Method_Name`, `IsX` / `HasX` members, `TF_`
  on our free functions and globals. Python follows PEP 8.
- DRY within our code: use an existing helper before writing one, and two TF blocks doing
  the same job share a helper. EA and VC duplication stays as it is.

## Dead code
- No commented-out code and no `#if 0` blocks in our code. Delete it; git keeps it.
- When a feature goes, its helpers, statics, `tf_*.flag` checks and log files go in the
  same change. Before deleting, confirm no caller in `redalert/` and no reference in
  `scripts/`, data or docs.

## Diagnostics
- A diagnostic (log, probe, counter) compiles only under `#if TF_DEV_BUILD`, so the
  Workshop build has none.
- It lives only while its feature or bug is open, and is deleted in the branch that ships
  the feature or fixes the bug.
- It writes `Documents/CnCRemastered/tf_<topic>.log` and is rate-limited. Heavy work runs
  off the game thread. It never reads an object after `Take_Damage`: a kill deletes it.
- Dev toggles and flags (`TF_DEV_BUILD`, `tf_dev_off.flag`, any `#if` dev switch) change
  only with the maintainer's OK.

## Scripts
- Scripts live in the repo, never only in a scratch folder.
- `scripts/` holds tools. A doc, a build script or another script names each one, so its
  purpose can be found.
- Probes and previews for open work go in `scripts/probes/` and are deleted when that work
  ships or the bug is fixed, like diagnostics. A probe worth keeping moves to `scripts/`,
  and a doc names it.

## Review and testing
- `tests/` holds Vanilla Conquer's renderer tests. Game logic is verified by a build and a
  play test, so a review doesn't ask for unit tests.
- Every branch gets `/dev-code-review` before it merges to main, and each finding is fixed
  or answered.

## Commits
- One kind of change per commit: comments, dead code, or behaviour. Never mix a tidy-up
  with a behaviour change.
- Comment-only commits touch no code line (check the diff) and still build green.
- Parallel branches collide in `defines.h`, `bdata.cpp`, `udata.cpp`, `house.cpp`,
  `dllinterface.cpp` and `rules.ini`. Changes to those go in their own commits.
