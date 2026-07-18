# Per-slot AI difficulty via ClientG RAM — spike record + implementation design

**Status: phase A SHIPPED + LIVE-VERIFIED 2026-07-18 (commit `3e156a0`).** A mixed
Hard/Medium/Easy/Hard lobby produced IQ 5/4/3/5 on the matching houses, confirmed
on-screen and in MOD_DEBUG_AI.txt. Phase B state after the 2026-07-18 rig night:
host-broadcast DEAD (no DLL-side event transport in GlyphX) AND the scanned records
turned out to be saved skirmish config, not the live lobby — see the phase-B section
for the full verification trail. Next: run probe v3 (deployed both machines) to
locate the live lobby model via AI GlyphxID needles; also fixes a phase-A regression
(stale apply in 1-human LAN lobbies).
Companion findings and session narrative: `todo.md` Phase 1 block, `ai-upgrade-plan.md`
§6 Phase 1 STATUS.

**Implementation notes (what shipped, all in `redalert/dllinterface.cpp`):**
- Scanner: `TF_Read_Lobby_AI_Difficulties` + helpers, directly above
  `CNC_Set_Difficulty`. Signature scan per the design below; every validated
  candidate array must agree or the read fails (stale lobby copies exist in memory).
- **Trap found during GREEN:** the GlyphX house-assign loop renames AI houses'
  `IniName` from `AIPLAYERn` to the "Computer" display name before
  `CNC_Set_Difficulty` runs, and `InitialName` is compiled out (`WOLAPI_INTEGRATION`
  undefined). Slot mapping therefore uses `TF_AILobbySlotByHouse`, captured in the
  assign loop at the moment the name is destroyed (reset each match in
  `CNC_Set_Multiplayer_Data`).
- The TF_AI_DIAG HELLO lines (log + on-screen via the deferred
  `CNC_Advance_Instance` flush) print each house's mode tagged `[slot n]` (RAM) or
  `[global]` (fallback) — the standing per-match verification readout.

## Why RAM

Every other route to the lobby's per-slot AI difficulty is measured dead (2026-07-18):

| Route | Verdict |
|---|---|
| `CNC_Set_Difficulty` | Client sends `1` unconditionally in skirmish (5 lobbies measured: mixed, all-Easy ×2, all-Hard, campaign-option-Hard). `1` = the client's default MEDIUM slot concept, disconnected from the picker. |
| Interface structs | No per-slot difficulty field anywhere; AI `Name` = bare `AIPLAYER1..4` (hex-verified). |
| Persisted settings (`userdata/<id>/1213210/remote/Player_RA_settings_1.bin`) | ChunkFile+zlib TLV; holds map/faction/mode but NO difficulty. The byte that moves at launches (tag 0x31) is a match-start counter. |
| Wine registry / exit-time writes | Nothing difficulty-related. |
| Cross-restart lobby memory | Doesn't exist — lobby resets to one default MEDIUM AI after full game restart. |

The picker state lives **only in ClientG.exe process RAM**, where it demonstrably
persists from lobby into match (the "reverts to last-launched settings" behaviour).
So we read it there. DontCryJustDie suggested this generically ("if you know the
offsets"); our design needs **no hardcoded offsets** (signature scan, below).

## PoC (proven live)

Method: host-side Python reading `/proc/<ClientG pid>/mem` (same-user read of wine
process memory — the same permission model `ReadProcessMemory` uses in-prefix).
Scanned private writable regions for `AIPLAYER` (ASCII + UTF-16).

Lobby under test: slots 2–5 = **Hard / Medium / Easy / Hard**, all-USSR (factions held
constant so only difficulty varies).

Found: a 4-record array (one per AI slot), record stride **0xA8**, each record starting
with the ASCII slot name:

| Record offset | Field | PoC values |
|---|---|---|
| `0x00` | `AIPLAYERn\0` name string | AIPLAYER1..4 |
| `0x50` | slot index int32 | 1, 2, 3, 4 |
| `0x64` | **difficulty int32** | **3, 2, 1, 3** |
| `0x68` | slot index again (team?) | 1, 2, 3, 4 |

**Difficulty enum: 1 = Easy, 2 = Medium, 3 = Hard** (matched the lobby exactly).
Re-read mid-match: array intact, values unchanged — readable at match time, when the
DLL needs it. Addresses are per-run (heap); only the record SHAPE is stable.

Other AIPLAYER hits in memory (log strings, render/debug copies, a TLV message block
with per-slot tags) exist — the scanner must validate candidates, not take the first hit.

## Reference tooling

`scripts/read_lobby_difficulty.py <pid>` — the proven host-side reader (signature scan +
record walk, offsets baked in). Get the stable pid with
`pgrep -f "ClientG.exe GAME_INDEX=0 REDALERT"` while a match is loaded. This is the
reference the in-DLL phase-A read reimplements via ReadProcessMemory.

## Implementation design

### Solo skirmish (phase A)

At match start (`CNC_Set_Multiplayer_Data` gives us the AI slot names + order; the
difficulty read can also run lazily on first AI tick — retro-apply already exists):

1. Find ClientG.exe: `CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS)`, match exe name
   (it is the parent chain of InstanceServerG; name match is sufficient — one instance).
2. `OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION)`.
3. Region walk via `VirtualQueryEx` (private, committed, RW), read with
   `ReadProcessMemory`.
4. **Signature scan**: find `AIPLAYER1\0` (ASCII). Candidate validates iff:
   - `+0x50` int32 == 1 and `+0x68` int32 == 1;
   - `+0x64` int32 in [1..3];
   - records at `+0xA8·k` (k = 1..numAI−1) repeat the pattern with name `AIPLAYER{k+1}`,
     `+0x50` == k+1, difficulty in range.
   All checks must pass for exactly ONE candidate array; ambiguity or zero hits =
   scan failure.
5. Map `AIPLAYERn` → the n-th AI entry in the `CNC_Set_Multiplayer_Data` player list
   (names match — we log both already), then per-house:
   Easy→IQ 3, Medium→IQ 4, Hard→`Rule.MaxIQ` (existing `TF_AI_IQ_From_Difficulty`,
   note the RAM enum is 1-based vs our DiffType 0-based).
6. **Fallback chain: RAM scan → `tf_ai_difficulty.txt` (global) → default Hard.**
   Log the outcome per house under TF_AI_DIAG.

32/64-bit note: our DLL is 32-bit; all PoC addresses were < 4 GB. If ClientG turns out
to allocate the array above 4 GB on some machines, use `NtWow64ReadVirtualMemory64`.
Check `IsWow64Process` on ClientG during implementation.

### Multiplayer with AI (phase B — mirrored-lobby read; broadcast design DEAD)

MP is deterministic lockstep: AI IQ is sim state, so every peer must apply identical
difficulties on the same frame. Per-machine reads (RAM or flag file) would desync —
unless every peer's read provably yields the same values.

**Host-broadcast design VERIFIED DEAD (2026-07-18).** The original plan (host injects a
custom EventClass, peers apply on execution) assumed the GlyphX transport moves DLL
event bytes. It does not:

- In `GAME_GLYPHX_MULTIPLAYER`, `DLLExportClass::Glyphx_Queue_AI` moves `OutList` →
  `DoList` **locally only**; the legacy `Send_Packets`/`Extract_Uncompressed_Events`
  networking in queue.cpp never runs.
- The DLL export table has no packet/event-bytes function, and every DLL→client
  callback (`CALLBACK_EVENT_*`) is local presentation. EventClass bytes never leave
  the machine.
- GlyphX determinism comes from the **client replaying every player's requests**
  (`CNC_Handle_*` tagged with the originating player id) into every peer's DLL at the
  same frame boundary. The DLL has no send channel of any kind. (`SET_RALLY` works in
  MP only because its *triggering request* is replayed on all peers.)

**Mirrored-lobby read, as scanned: ALSO DEAD (2-peer LAN rig, 2026-07-18).** The
`AIPLAYERn` record array phase A reads is each account's **persisted skirmish-lobby
config** (survives client restarts, loaded from disk per account), NOT the live MP
lobby model. Rig evidence, desktop (Luke) + Luke's Deck (daughter aimee101), LAN
lobbies, scanner v2 (roster-name anchor, commit `4f2a1a1`):

- The joiner read its own saved config — the same `1,2,2,3` — in 4 consecutive
  matches regardless of what the host set.
- The host's read contradicted its own lobby UI in the screenshot-verified match
  (UI Med/Easy/Hard/Med vs read Easy/Med/Hard/Easy — different multisets, not an
  ordering artifact).
- Phase A's solo GREEN was the special case where the skirmish config IS the lobby.

**Live-model facts established by the rig:**

- Both host AND joiner UIs render the host's real per-slot difficulties → a **live
  lobby model exists in every peer's client**; it is simply not the record array we
  scan. Finding it revives the no-broadcast design intact.
- `AIPLAYERn` names are per-client local labels (numbering persists per account and
  can differ across peers for the same lobby: 1..4 vs 2..5 observed). AI GlyphxIDs
  are name-hashes — identical across peers **when** names agree, but not a synced
  identity either.
- `CNC_Set_Multiplayer_Data` player lists are peer-relative views: each peer lists
  the remote human at slot[0] with the remote's color normalized differently. Human
  colors/teams in that struct are NOT directly comparable across peers; AI slot
  colors did agree.
- The record's +0x50/+0x68 slot ints renumber positionally (1..4 against names
  AIPLAYER2..5) — v1's `slot==n` check was wrong even solo; v2 keys by name n.

**Probe v3 (commit `c036d59`, build `8ae684f6` — deployed to both rig machines,
NOT yet run):** dumps bounded hex+ascii context around every client-RAM occurrence
of each AI slot GlyphxID (`PHASEB-ID` lines, MP recon only). Next session: one LAN
match, fresh difficulty mix, diff host-vs-joiner dumps → derive the live model's
difficulty-int offset → scanner v4 reads the live model on every peer. Divergence
hazard from the earlier design still applies (peers that fail the scan fall back
differently — bounded empirically, never eliminated).

**Phase-A regression found by the rig (open):** the solo apply gate (`humans < 2`)
also covers 1-human LAN lobbies, where the saved-config records mismatch the live
lobby → stale difficulties actually get applied. Fix rides the v4 live-model read.

Recon plumbing (in tree): dev builds scan in MP but stay log-only (`PHASEB-RECON
roster=… s<n>=…` per peer; 2+ humans guard untouched); release builds skip the MP
scan. `PHASEB-CAND` logs every candidate array raw. Rig traps: the Workshop copy and
the local mod share a display name (local = higher version, 4.1); a game relaunched
during a deploy keeps the old DLL inode (rsync replaces by rename — verify with the
freshness tells: fresh `tf_astar.log` + `MOD_DEBUG_AI.txt` within seconds of match
start).

## RAM reconnaissance — what else is extractable (survey 2026-07-18)

Question posed: is reading ClientG RAM a general "launcher unblocker"? **No — it is a
lobby-SELECTION extraction channel, not a capability unlocker.** The distinction is
read vs write:

- **Reading** ClientG surfaces values the client computed but won't pass the DLL
  (difficulty is the proven case). Good for "the client knows X, the DLL needs X, no
  official pipe."
- The launcher WALLS (5th faction, playable campaign, hotkey classes, front-end
  textures — see `bui-front-end-modding.md`, `front-end-texture-meg-spike.md`) are
  limits of the client's COMPILED BEHAVIOUR, not hidden data. Reading can't change them;
  writing (`WriteProcessMemory`) can't add code paths that don't exist and is the
  fragile/AV-triggering/crash-prone route we deliberately avoid. RAM does NOT move these.

Token survey of a live in-match ClientG (3-AI skirmish):

| Token | Hits | What it is |
|---|---|---|
| `AIPLAYERn` | array | per-slot AI record — difficulty at +0x64 (THE win) |
| `FACTION5` | 21 | faction-type registry object (`FACTION5\0NTTYPEI` + index) — slot faction assignments are readable |
| `Docklands` | 17 | selected map name |
| `CASUAL` | 25 | difficulty label strings (Casual/Normal/Brutal-family UI text) |
| `EnableSuperweaponsGroup` | 2 | asset GROUP NAME, not the live toggle value |
| `FirepowerBias`, `MPlayerCredits`, `UnitCount`, `BRUTAL` | 0 | rules/option VALUES are not string-tagged in RAM (credits/unitcount already arrive via CNC_Set_Multiplayer_Data anyway) |

Takeaway: extractable = lobby's **named selections/definitions** (faction-per-slot, map,
difficulty). NOT extractable as tagged data = numeric rule values (they reach the DLL
legitimately or exist only as raw untagged numbers). So the practical yield beyond
difficulty is thin — most lobby data the DLL needs, it already gets. Difficulty was the
one real gap, and it's solved.

## Risks / caveats

- **AV heuristics (Windows players):** a game DLL calling `ReadProcessMemory` on a
  sibling process is mildly heuristic-adjacent. Read-only, own-game, low risk — but if
  reports surface, the flag-file fallback remains and a config kill-switch for the
  scanner is one bool.
- **Record shape is empirical**, from one build of the frozen (archived Jan 2025)
  client. The validating signature makes false positives unlikely and false negatives
  fall back gracefully.
- **Lobby edits mid-match** (host fiddling a hypothetical UI) are not re-read; we read
  once at match start, matching launcher semantics.
- Scanner cost: one pass over ClientG's private RW regions (~hundreds of MB) at match
  start only. Chunked reads, early-out on first validated array.
