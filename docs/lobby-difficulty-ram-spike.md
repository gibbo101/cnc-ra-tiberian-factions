# Per-slot AI difficulty via ClientG RAM

**Status:** Reference; shipped in 4.1.0, the ambiguity resolver in 5.0.0.

Each skirmish AI plays at the difficulty picked for it in the lobby, read from ClientG's `AIPLAYERn` records at match
start. Why memory is the only source, the method, the record layout, the gates and the stale-copy problem are
game-level: see the field manual's
[Per-AI lobby difficulty](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/per-ai-lobby-difficulty.md).
DontCryJustDie suggested reading it from the launcher and identified most of the record's fields. TF's read uses
no hardcoded offset, only the record's shape: addresses change every run.

## How TF runs it

All in `redalert/dllinterface.cpp`:

- **Scanner:** `TF_Read_Lobby_AI_Difficulties` and its helpers, directly above `CNC_Set_Difficulty`, scan and
  validate as the manual's [method](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/per-ai-lobby-difficulty.md#the-method)
  describes (steps 1 to 4). ClientG is found by exe name, since only one runs (ClientLauncherG starts it beside InstanceServerG; see the field manual's [What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#how-to-tell-who-owns-a-behaviour)).
  `TF_Validate_Lobby_Records` stops at the first bad record, and a candidate must cover the whole roster, so one
  over-strict gate drops every AI to the global tier. Gate only on a field whose meaning is measured, never
  assumed: team is range-checked `0..TF_LOBBY_MAX_TEAM` (8, a random team), and a country of 42 (a random faction)
  skips the country test. TF compares the country against `player_info.House`, captured in
  `CNC_Set_Multiplayer_Data` before the Spain/Greece hijack rewrites it.
- **Slot to house** (the manual's method, step 5): `TF_AILobbySlotByHouse`, captured in the assign loop before the
  name is overwritten, reset each match in `CNC_Set_Multiplayer_Data`.
- **Difficulty to IQ:** `TF_AI_IQ_From_Difficulty` (`redalert/house.cpp`): Easy IQ 3, Medium IQ 4, Hard
  `Rule.MaxIQ`. The record's difficulty is 1-based, TF's `DiffType` 0-based. Every AI keeps `MaxIQ` until a lobby
  difficulty has arrived, and under the classic AI.
- **Rebuild window:** a failed read arms `TF_Lobby_Difficulty_Retry` from `CNC_Advance_Instance`: up to four
  re-scans, `TF_LOBBY_RETRY_FRAME_GAP` (90) frames apart. A read applies once two in a row agree, or on the last
  attempt rather than none.
- **Stale copies:** validated candidates that disagree go to `TF_Resolve_Lobby_Ambiguity`
  (`lobby-ambiguity-findings.md`), which fails closed when undecided.
- **Fallback chain:** the RAM read, then `Documents/CnCRemastered/tf_ai_difficulty.txt` (global), then Hard. The
  file applies in LAN too, since only the host simulates, but that is not live-verified.
- **Readout:** `TF_Apply_AI_Difficulties` queues one line per computer house, `Enemy AI: <side> (<colour>) -
  <mode>`, and `CNC_Advance_Instance` shows them on screen through `On_Message` for 30 s from frame 30, in release
  builds too. The line names the mode, not its source, so a global-tier fallback looks the same as a slot read.

Only the LAN host simulates, so the host's read sets every AI and nothing needs synchronising (see the manual's
[LAN games](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/lan-games.md#one-simulation-on-the-host)).
TF measured it by role swap on one machine: no simulation log lines as joiner, the first within about 10 s as
host. `GlyphxID` can't tell a live array from a stale one: the IDs are fixed per slot index.

**Dead routes, do not rebuild:** a host-broadcast EventClass, mirrored lobby reads across peers, a live-model hex
hunt, and the `PHASEB-ID` `GlyphxID` probe. Each assumed both peers simulate. Measure the role; don't derive multiplayer
constraints from transport code.

## Verified in play

- A Hard/Medium/Easy/Hard solo lobby gave IQ 5/4/3/5.
- A fixed lobby (GDI/Nod/Allies/Soviet, Hard/Easy/Medium/Hard, teams 2,2,3,3, colours shuffled out of slot order):
  all four records accepted, every country matching the roster, all four houses `[slot n]`, IQ 5/3/4/5. The read
  succeeds on the first scan at frame 0, with no retries.
- A random lobby (one AI on a random faction, one on a random team): the records read 42 and 8 while the roster had
  resolved them, and both were accepted through their skips.
- A two-human LAN lobby set Easy/Easy/Easy/Hard read `s2=1 s3=1 s4=1 s5=3`, no permutation of the cached values, so
  a live read.
- Re-read mid-match: the array intact and unchanged.

## Reference tooling

`scripts/read_lobby_difficulty.py <pid>` is the host-side reader the in-DLL read reimplements through
`ReadProcessMemory`: it reads `/proc/<pid>/mem` (the same same-user permission `ReadProcessMemory` uses inside the
prefix), with the signature scan, record walk and offsets built in. Get the pid with
`pgrep -f "ClientG.exe GAME_INDEX=0 REDALERT"` while a match is loaded. The first proof-of-concept read searched private writable regions for
`AIPLAYER` in both ASCII and UTF-16; the records are found by the ASCII name, which is all this reader and the DLL
search for.

## What else ClientG's memory holds

Reading surfaces values the launcher computed but doesn't pass the DLL. It can't move a launcher wall, which is
compiled behaviour; writing can (`launcher-vs-dll-ownership.md`). A token survey of a live in-match ClientG (3-AI
skirmish):

| Token | Hits | What it is |
|---|---|---|
| `AIPLAYERn` | array | the per-slot AI record, difficulty at +0x64 |
| `FACTION5` | 21 | a faction-type registry object (`FACTION5\0NTTYPEI` plus index): slot faction picks are readable |
| `Docklands` | 17 | the selected map's name |
| `CASUAL` | 25 | difficulty label strings (the Casual/Normal/Brutal family) |
| `EnableSuperweaponsGroup` | 2 | an asset group name, not the live toggle |
| `FirepowerBias`, `MPlayerCredits`, `UnitCount`, `BRUTAL` | 0 | rule and option values are not string-tagged in memory |

So the lobby's named selections (faction per slot, map, difficulty) are extractable; numeric rule values are not,
and credits and unit count already arrive through `CNC_Set_Multiplayer_Data`. Difficulty was the one real gap.

## Risks

- **Antivirus heuristics on Windows:** a game DLL calling `ReadProcessMemory` on a sibling process is mildly
  heuristic-adjacent. If reports come in, the file fallback remains, and a kill switch for the scanner is one bool.
- **The record shape is empirical**, from one build of a client EA no longer patches. The validating signature makes
  false positives unlikely, and false negatives fall back.
- **Mid-match lobby edits** are not re-read; TF reads once at match start, as the launcher does.
- **32/64-bit:** TF's DLL is 32-bit and every measured address was under 4 GB. If ClientG ever allocates the array
  above 4 GB, read it with `NtWow64ReadVirtualMemory64` after checking `IsWow64Process`; the scanner does neither.
- **Cost:** one pass over ClientG's private read-write regions (hundreds of MB) at match start, plus up to four
  re-scans, in chunked reads, every validated array kept for the resolver.
