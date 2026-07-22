# Steam Workshop publish runbook

How to publish or update `cnc-ra-tiberian-factions` on the Steam Workshop (App `1213210`).

The canonical tool is our own Linux-native uploader at `tools/workshop-uploader/`. No Wine, no Windows, no Deck needed.

---

## Step 0 — RESTART STEAM (don't skip)

**This is the rule that took 4 hours to find.** If Steam has been running for a while, the standalone-uploader path silently hangs at "preparing config" — Steam logs `Upload starting` but never progresses. A fresh Steam process clears whatever stale per-app UGC cache causes it.

1. In Steam's menu bar: `Steam → Exit` (full exit, not just close window).
2. Wait ~10 seconds for background helpers to die.
3. Relaunch Steam, log in if prompted.
4. Confirm Steam is up before continuing.

Don't try to skip this. The symptom is silent — no error, just an indefinite hang.

---

## Prerequisites (one-time)

- `.NET 8 SDK` on PATH. If you don't have it: `curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 8.0 --install-dir "$HOME/.dotnet"`, then `export PATH="$HOME/.dotnet:$PATH"`.
- `tools/workshop-uploader/lib/Steamworks.NET.dll` and `tools/workshop-uploader/native/libsteam_api.so` — both extracted from the [Steamworks.NET Standalone release zip](https://github.com/rlabrecque/Steamworks.NET/releases/latest) (`OSX-Linux-x64/` folder). Do not use the NuGet `Steamworks.NET` package — ABI mismatch with current native lib.
- `tools/workshop-uploader/steam_appid.txt` containing the single line `1213210`.

---

## Per-release procedure

### 0. Get the release copy approved — BEFORE anything is published

Luke reviews and OKs the full public text first: the Workshop description changelog block, the
`CHANGELOG.md` section, and the GitHub release notes. Present the actual text, not a summary.

Ask explicitly whether anything should stay **unannounced**. That is not derivable from the
CHANGELOG: easter eggs are meant to stay quiet, and some fixed surfaces are ones he would rather
not draw attention to. The changelog is the engineering record; the listing is the shopfront.

Publishing first and correcting after means editing live on a public page. It happened on 4.1.0
and cost six edits across five re-uploads.

### 1. Build the mod

```bash
# From repo root
CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake \
  VC_CXX_FLAGS="-w;-fpermissive" \
  cmake --workflow --preset remaster
```

Result lands at `build/remaster/Vanilla_RA/` — contains `ccmod.json`, `Data/`, `CCDATA/`.

### 2. Stage the wrapper folder

The Workshop scanner for App 1213210 requires the mod to live in a NAMED SUBFOLDER inside the uploaded content (i.e. `<workshop-item>/Vanilla_RA/ccmod.json`, not `<workshop-item>/ccmod.json`). Subscribers who pull a mod with `ccmod.json` at the root will never see it in the in-game mod list, even though the content downloads correctly.

```bash
./package-for-workshop.sh
```

This creates `dist/workshop-content/Vanilla_RA` as a symlink to `build/remaster/Vanilla_RA/`. Idempotent — run again after every rebuild (the symlink is stable; only the underlying build content changes). SteamUGC follows symlinks during content enumeration, confirmed 2026-05-20.

### 3. Update `tools/workshop-uploader/workshop.json`

Schema (matches EA's original `.workshop.json` format so existing tutorials remain readable):

| Field | What to set |
|---|---|
| `publishedfileid` | Steam-allocated item ID. Leave empty for first publish — the tool calls `CreateItem` and persists the new ID back. |
| `contentfolder` | Path to the built mod folder. Relative paths resolve from the JSON file's directory. `"../../build/remaster/Vanilla_RA"` is the canonical value. |
| `previewfile` | Path to preview JPG/PNG. < 1 MB. `""` or omitted = keep existing preview. |
| `visibility` | `0`=Public, `1`=Friends Only, `2`=Private, `3`=Unlisted. **Use `1` for first publish of each release**, promote to `0` after self-test. |
| `title` | Display title — keep consistent across versions. |
| `description` | Steam BBCode supported: `[b]…[/b]`, `[h2]…[/h2]`, `[list][*]…[/list]`, `[url=…]…[/url]`. |
| `tags` | Array. Valid for App 1213210: `RA`, `RedAlertMod`, `TD`, `TiberianDawnMod`, `FFA`, `1v1`, `2v2`. |
| `metadata` | Leave `""`. |

Change note is NOT persisted in JSON — passed on the command line per submission.

**Changelog heading style in the description:** underline is for **major** releases only.
`[b][u]Version 4.0.0[/u][/b]` for a major, `[b]Version 4.1.0[/b]` for a minor or patch. Getting
this wrong makes a point release read as a milestone in the listing.

**⚠️ The `description` field has a hard 8000-character limit.** Exceed it and the submission
uploads content and preview normally, then fails at the commit step with
`EResult.k_EResultInvalidParam (8)` — the error names no field, so it reads like a content
problem. Steam rejects the whole update rather than truncating. Check before publishing:

```bash
python3 -c "import json;print(len(json.load(open('tools/workshop-uploader/workshop.json'))['description']))"
```

Hit 2026-07-22 on the 4.1.0 publish at 8660 characters. When a new version block pushes it over,
collapse the oldest per-version changelog blocks to a one-line summary each; the listing already
links the full changelog on GitHub.

### 3. (Optional) Refresh preview screenshot

Pull a fresh in-game shot from the Deck:

```bash
ssh deck@steamdeck "ls -t /home/deck/.steam/steam/userdata/42346487/760/remote/1213210/screenshots/*.jpg | head -1" \
  | xargs -I{} scp deck@steamdeck:{} tools/workshop-uploader/preview.jpg
```

Or omit (set `previewfile: ""`) to keep the existing preview unchanged.

### 4. Publish

```bash
cd tools/workshop-uploader
export PATH="$HOME/.dotnet:$PATH"
dotnet build  # if you've changed Program.cs; otherwise skip
dotnet run --no-build -- workshop.json "vX.Y.Z — one-line change summary"
```

Expected output:
```
submitting update...
  [    0s] preparing config
  [    1s] preparing content
  [    1s] uploading content
  [   20s] uploading content       100% 88.1 MB/88.1 MB
  [   21s] committing
SUCCESS — item NNNN updated.
```

Time scales with upload bandwidth. 89 MB takes ~21s on a ~50 Mbit upstream.

### 5. Verify

1. Visit `https://steamcommunity.com/sharedfiles/filedetails/?id=<itemid>` (logged into Steam).
2. Confirm File Size > 0, title/description render correctly, preview displays.
3. Subscribe via Steam and let it sync. Verify the mod folder appears at:
   - **Deck:** `/home/deck/.steam/steam/steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/CnCRemastered/Mods/Red_Alert/<itemid>/`
4. Launch the game (on the Deck), enable the mod, smoke-test the headline feature.
5. If self-test passes: promote visibility to Public via the Workshop website's Owner Controls panel (no need to re-run the uploader for visibility-only changes).

---

## Troubleshooting

### Hang at "preparing config" with no progress

Did you restart Steam? Restart Steam.

If you definitely restarted Steam and still hang: kill the uploader (`pkill -9 -f WorkshopUploader`), tail `~/.local/share/Steam/logs/workshop_log.txt` to see what Steam saw, and check whether your Steam account is currently "playing" the game on another device (Family Sharing / Remote Play / Steam Deck). Exit any such session and retry.

### `Unable to load shared library 'steam_api'`

`tools/workshop-uploader/native/libsteam_api.so` missing or in the wrong place. Re-extract from the [Steamworks.NET Standalone zip](https://github.com/rlabrecque/Steamworks.NET/releases/latest), `OSX-Linux-x64/libsteam_api.so` → `tools/workshop-uploader/native/`. Rebuild.

### `EntryPointNotFoundException` on `SteamAPI_*` calls

Managed/native ABI mismatch. Make sure `tools/workshop-uploader/lib/Steamworks.NET.dll` is from the **same** standalone release as the `libsteam_api.so` in `native/`. Don't mix NuGet managed + standalone native.

### `m_bUserNeedsToAcceptWorkshopLegalAgreement` flag set on result

Visit the item URL in a browser (logged in), accept the Workshop Contributor Agreement banner, retry the upload.

---

## Don't-dos

- Don't re-create the item shell for an existing release — `publishedfileid` is allocated once per item.
- Don't pursue EA's `Uploader.exe` — confirmed bitrotted on Linux (Wine/Proton) AND on Luke's Windows install. Same hang as our tool was hitting pre-restart, but our tool is now easier to diagnose.
- Don't commit `tools/workshop-uploader/preview.jpg` or per-release `workshop.json` if they contain machine-absolute paths or release-specific descriptions; prefer relative paths so the JSON is portable.

---

## Historical context

- 2026-05-20: First Workshop publish for this mod (v0.3.0). EA's `Uploader.exe` ruled out as bitrotted across Windows / Wine / Proton. Built our own C# uploader using `Steamworks.NET`, mirroring the SteamUGC sequence in `~/.steam/steam/steamapps/common/CnCRemastered/SOURCECODE/CnCTDRAMapEditor/Utility/SteamworksUGC.cs` (EA's MapEditor — the only working official Workshop publisher for this app). Spent 4 hours hung on the same "preparing config" symptom EA's tool produces, until a Steam restart cleared it instantly. See memory `reference-workshop-publish-path` for the full rabbit hole.
