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

⚠️ **Known limitation — only the session's FIRST LAN lobby reads reliably.** A LAN match
cannot be returned to a lobby: when it ends you re-host, and the new lobby starts blank.
Each re-host builds fresh `AIPLAYERn` records while the previous lobby's copies linger in
the process, so the scanner (which requires every validated candidate array to agree)
either takes stale values or bails with `ram_slots=0`. Both observed 2026-07-19 in
re-hosted lobbies; the lobby run immediately after a game launch read correctly.
**Failure is graceful** — it falls back to global Hard, i.e. shipped v4.0 behaviour — so
the worst case is "no per-slot difficulty", never a broken match. Workaround: relaunch
between LAN matches. Real fix: stop demanding unanimity and prefer the newest/most-specific
candidate array; the `PHASEB-CAND` raw dump (removed in `06ca30a`, restore from history)
is the tool for that.

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
