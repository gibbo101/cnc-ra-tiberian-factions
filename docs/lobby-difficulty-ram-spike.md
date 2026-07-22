# Per-slot AI difficulty via ClientG RAM — spike record + implementation design

**Status: phase A SHIPPED + LIVE-VERIFIED 2026-07-18 (commit `3e156a0`).** A mixed
Hard/Medium/Easy/Hard lobby produced IQ 5/4/3/5 on the matching houses, confirmed
on-screen and in MOD_DEBUG_AI.txt.

**⭐ PHASE B RESOLVED 2026-07-19 — and the problem it was solving does not exist.**
Two rig measurements collapsed the whole design space:

1. **In a LAN match only the host simulates.** The joiner's client renders streamed
   state and never executes the game DLL at all. Proven by role swap on ONE machine:
   Luke's desktop wrote zero diagnostic bytes across a full 10-minute match as joiner,
   then wrote its first log line within ~10s of hosting. Same mod, same DLL, same
   binary — only the role changed. The sim lives in `InstanceServerG.exe`, a separate
   process from the `ClientG.exe` shell, and on a joiner that process has **no game
   DLL mapped at all**.
2. **The host reads its own live lobby correctly.** With cached values `3,1,2,3` in
   memory, a fresh lobby set to Easy/Hard/Hard/Medium scanned as `s2=1 s3=3 s4=3
   s5=2` — every slot tracked the change.

**Therefore there is nothing to synchronise.** One sim, running on the machine that
owns the lobby, reading the authoritative values directly. No broadcast, no
cross-peer mirroring, no scanner v4, no live-model hex hunt. The `PHASEB-ID` GlyphxID
probe was built to find a live model we did not need.

**LIVE-VERIFIED in LAN MP 2026-07-19.** Lobby Easy/Easy/Easy/Hard with two humans read
`s2=1 s3=1 s4=1 s5=3` and applied IQ 3/3/3/5, each house tagged `[slot n]`, shown
on screen on **both** peers. The multiset `{1,1,1,3}` is not a permutation of the
cached `{1,2,2,3}`, so this is unambiguously a live read rather than a stale one.
(The joiner displaying host-generated messages is itself further confirmation of the
host-only model: its own DLL never ran.)

⭐ **READ TIMING RESOLVED 2026-07-21 — the scan is fine, the moment was wrong.** The client
tears down and rebuilds its `AIPLAYERn` records as a match launches. A scan landing inside
that window finds nothing, or finds a fresh array disagreeing with a not-yet-freed stale one,
and reports failure — so the match falls back to global Hard. This is **not** LAN-specific:
plain solo skirmish hits it from the second match of a session onward. Fix = a deferred
re-scan from `CNC_Advance_Instance` (`TF_Lobby_Difficulty_Retry`, 4 attempts 90 frames apart)
that requires **two consecutive agreeing scans**, because the rebuild passes through
half-written states that are briefly self-consistent (`E M H M` was caught reading `E M M M`).
Evidence and the failure census: `known-issues.md` "Per-slot difficulty goes stale".

**`GlyphxID` cannot discriminate live from stale arrays** — the IDs are fixed per slot index
(slot 1 read `1055504538` in two sessions hours apart), not generated per lobby.

**`tf_ai_difficulty.txt` now applies in multiplayer too.** It was previously solo-only
on the reasoning that a per-machine file would desync peers. Only the host simulates,
so the host's file is the only one that reaches the sim. Not yet live-verified in MP.

**The resulting fix is the removal of a guard, not an implementation:** the
`TF_HumanPlayerCount < 2` gate on `apply_per_slot` was protecting against a
divergence that cannot occur. Since a joiner never executes the DLL, *any* execution
of this code is by definition the host — so per-slot difficulty applies
unconditionally.

**Scope note:** mods load in **LAN games only**, so LAN is the entire modded
multiplayer surface. There is no internet/quickmatch case to cover.

⚠️ **Retracted by this result:** the "phase-A regression — stale apply in 1-human LAN
lobbies" previously recorded here was diagnosed on the assumption that the scanned
array was saved config. That assumption is wrong (measurement 2), so the reasoning
behind that bug does not hold. Re-test before treating it as real.

Companion findings and session narrative: `todo.md` Phase 1 block, `ai-upgrade-plan.md`
§6 Phase 1 STATUS.

**Implementation notes (what shipped, all in `redalert/dllinterface.cpp`):**
- Scanner: `TF_Read_Lobby_AI_Difficulties` + helpers, directly above
  `CNC_Set_Difficulty`. Signature scan per the design below; every validated
  candidate array must agree or the read fails (stale lobby copies exist in memory).
  A failed read arms the deferred re-scan described in the status block.
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
| `CNC_Set_Difficulty` | Client sends `1` unconditionally in skirmish (5 lobbies measured: mixed, all-Easy ×2, all-Hard, campaign-option-Hard) and `-1` in LAN MP. Either way it is disconnected from the picker. |
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

| Record offset | Field | PoC values | Identity (settled 2026-07-22) |
|---|---|---|---|
| `0x00` | `AIPLAYERn\0` name string | AIPLAYER1..4 | unchanged |
| `0x50` | *assumed* slot index int32 | 1, 2, 3, 4 | **team, 0-7, plus 8 = random** |
| `0x54` | house / faction int32 | not read | **ActLike = HousesType + 2, 42 = random** |
| `0x64` | **difficulty int32** | **3, 2, 1, 3** | unchanged, the payload |
| `0x68` | *assumed* slot index again | 1, 2, 3, 4 | **lobby colour 0-7** |

**Difficulty enum: 1 = Easy, 2 = Medium, 3 = Hard** (matched the lobby exactly).
Record stride `0xA8` = 168 bytes. Human players occupy records ahead of the AI ones,
with an empty name and difficulty 0; anchoring the scan on `AIPLAYERn` skips them.

### Field identities

The PoC lobby used default colours, which are handed out in slot order. That made
`0x50`, `0x68` and the slot index numerically identical, so all three read as "the slot
index" and any of them looked usable as a key. They are three different fields.

- **`0x68` is the lobby colour** (DontCryJustDie, 2026-07-21). Changing an AI's colour in
  the lobby breaks any `0x50 == 0x68` test immediately. It is a liveness key rather than
  just a field, because the DLL can independently corroborate it: the colours for the
  current match arrive in `CNC_Set_Multiplayer_Data`, so an array carrying them belongs to
  this match and not to a lobby that has been and gone.
- **`0x50` is the team** (DontCryJustDie, 2026-07-22): 0-7 for a real team, 8 for random.
  It counts from zero and is not a slot identity, which is why AIPLAYER1 reads `0` and a
  three-AI lobby read `0, 1, 1` (two AIs sharing a team). The PoC's tidy `1, 2, 3, 4` was
  a default-team coincidence. Range-check only; the roster's own `Team` is not a safe
  equality test because a random pick resolves before the DLL sees it.
- **`0x54` is the ActLike**, in the client's numbering: **RA HousesType + 2** (so 2-9),
  with 42 meaning the lobby pick was random (DontCryJustDie, 2026-07-22). Both samples we
  had logged decode exactly: an all-Soviet lobby's `4, 4, 4` is `HOUSE_USSR`, and a mixed
  GDI / Nod / Allied lobby's `2, 9, 3` is Spain / Turkey / Greece, our two hijacked country
  slots plus Greece. It is now a **second liveness key** alongside colour, gated against
  `player_info.House` captured in `CNC_Set_Multiplayer_Data` before the Spain/Turkey hijack
  rewrites it. Skipped when the record reads 42 or falls outside 2-9, so an unexpected
  encoding degrades to the colour-only gate instead of failing the read.

**The bug this caused.** The validator's range gate on `+0x50` was `< 1`, so every array's
first record (team 0) was rejected. Validation stops at the first bad record and a candidate must cover the
whole AI roster, so one rejected record discarded the entire array and the read returned
zero slots, silently falling every AI back to the global tier. It appeared intermittent
rather than broken because a single AI, or a first AI at a non-zero index, happened to pass.
The fix is `slot < 1` becoming `slot < 0` in `TF_Validate_Lobby_Records`
(`redalert/dllinterface.cpp`); the read then succeeds on the first scan at frame 0 with no
retries, verified with four AIs and with colours deliberately set to break slot ordering.
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
4. **Signature scan**: find `AIPLAYERn\0` (ASCII) for the roster's lowest AI number.
   Candidate validates iff, for each record at `+0xA8·k`:
   - the name is exactly `AIPLAYER{n}` with n strictly ascending;
   - `+0x64` int32 in [1..3];
   - `+0x50` (team) int32 in [0..8] — **range only**, it is neither 1-based nor an identity;
   - `+0x68` int32 in [0..7] **and equal to the colour `CNC_Set_Multiplayer_Data` gave us
     for that AI**, which is the check that proves the array belongs to this match;
   - `+0x54` (ActLike) **equal to that AI's country + 2**, skipped when it reads 42
     (random) or falls outside 2-9.

   A candidate must cover the whole AI roster. Equality tests against any field whose
   meaning is merely assumed are what broke this twice (`slot == slot2` first, then the
   1-based floor on `+0x50`); colour and country are corroborated from outside the scan,
   which is what makes them safe to gate on. All checks must pass for exactly ONE candidate
   array; ambiguity or zero hits = scan failure.
5. Map `AIPLAYERn` → the n-th AI entry in the `CNC_Set_Multiplayer_Data` player list
   (names match — we log both already), then per-house:
   Easy→IQ 3, Medium→IQ 4, Hard→`Rule.MaxIQ` (existing `TF_AI_IQ_From_Difficulty`,
   note the RAM enum is 1-based vs our DiffType 0-based).
6. **Fallback chain: RAM scan → `tf_ai_difficulty.txt` (global) → default Hard.**
   Log the outcome per house under TF_AI_DIAG.

32/64-bit note: our DLL is 32-bit; all PoC addresses were < 4 GB. If ClientG turns out
to allocate the array above 4 GB on some machines, use `NtWow64ReadVirtualMemory64`.
Check `IsWow64Process` on ClientG during implementation.

### Multiplayer with AI (phase B) — RESOLVED 2026-07-19

Nothing to build. Only the host simulates (see the status block at the top of this
file), so per-slot difficulty applies unconditionally — the fix was removing the
`TF_HumanPlayerCount < 2` guard on `apply_per_slot`.

**Retired, do not rebuild:** host-broadcast EventClass, mirrored-lobby read across
peers, live-model hex hunt / scanner v4, the `PHASEB-ID` GlyphxID probe. Each was
sound reasoning from `queue.cpp` / `Glyphx_Queue_AI` (no DLL-side event transport —
still true), resting on a false premise: that both peers simulate. Measure the role;
do not re-derive MP constraints from transport code.
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
