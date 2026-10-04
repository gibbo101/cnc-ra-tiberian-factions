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

### 1. Prepare the release on main, in the main checkout

Package from the **main checkout**, not a worktree: two release files are gitignored and only the
main checkout is guaranteed to hold the current ones.

- **Version:** `resources/remaster_mods/Vanilla_RA/ccmod.json`, `version_high = X`,
  `version_low = Y*10 + Z` (5.0.0 is high 5, low 0). Update its `description` if the headline changed.
- **Copy:** the dated `## [X.Y.Z]` section in `CHANGELOG.md`, the one-line listing entry and any
  feature/limitation changes in `tools/workshop-uploader/workshop.json`'s description,
  `docs/moddb-page-copy.md`, and README.md ("Coming in the next release" folds into the feature list).
- **Gitignored inputs present:** the UI atlas
  `resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/MT_COMMANDBAR_COMMON.TGA` (regenerated
  by the front-end art scripts; compare its md5 with the copy last played) and the startup intro
  `Data/ART/MOVIES/RA/REDINTRO.BK2` (the packager refuses a cut that does not match
  `scripts/intro_work/REDINTRO.md5`).
- **Asset packs clean:** `python3 scripts/asset_packs.py check` prints nothing.

### 2. Build and stage the release: `./package-for-workshop.sh`

The Workshop scanner for App 1213210 requires the mod to live in a NAMED SUBFOLDER inside the uploaded content (i.e. `<workshop-item>/Vanilla_RA/ccmod.json`, not `<workshop-item>/ccmod.json`). Subscribers who pull a mod with `ccmod.json` at the root will never see it in the in-game mod list, even though the content downloads correctly.

```bash
./package-for-workshop.sh
```

It makes the release build itself (`TF_DEV_BUILD=0`: dev cheats compiled out; the fifth
faction ships), stages the mod folder from scratch (the mod's own tree, the asset packs, the DLL)
so files left in `build/` by earlier work cannot ship, mirrors it into
`dist/workshop-content/Vanilla_RA` as a **real folder** (a symlink there broke installs on
2026-05-20: SteamUGC uploads symlinks as symlinks), checks the intro and strips the DLL.

Check the staged package before going further:

```bash
P=dist/workshop-content/Vanilla_RA
grep -E '"version_(high|low)"' $P/ccmod.json             # the release version
strings -a $P/Data/RedAlert.dll | grep -c tf_dev_off.flag  # 0: no dev code
```

Every machine in a LAN test gets **this one package**: the DLL's md5 changes on every relink
(the PE timestamp), so two builds of the same source are not byte-identical.

### 3. Update `tools/workshop-uploader/workshop.json`

Schema (matches EA's original `.workshop.json` format so existing tutorials remain readable):

| Field | What to set |
|---|---|
| `publishedfileid` | Steam-allocated item ID. Leave empty for first publish — the tool calls `CreateItem` and persists the new ID back. |
| `contentfolder` | The folder that holds the named subfolder. Relative paths resolve from the JSON file's directory. `"../../dist/workshop-content"` is the canonical value. |
| `previewfile` | Path to preview JPG/PNG. < 1 MB. `""` or omitted = keep existing preview. |
| `visibility` | `0`=Public, `1`=Friends Only, `2`=Private, `3`=Unlisted. The mod's item is Public, so updates keep `0`. A **new** item (an asset pack) is created at `2` and promoted after a self-test. |
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

### 3b. (Optional) Refresh preview screenshot

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

### 6. Tag, GitHub release, post-release bump

```bash
git tag vX.Y.Z && git push origin vX.Y.Z
(cd dist/workshop-content && zip -qr ../TiberianFactions-vX.Y.Z.zip Vanilla_RA)
gh release create vX.Y.Z dist/TiberianFactions-vX.Y.Z.zip --title "vX.Y.Z" --notes-file <the CHANGELOG section>
```

The zip has `Vanilla_RA/` at its root (ModDB links to it). Then bump the local `ccmod.json`
`version_low` by one patch so the working tree is always ahead of what is published.

---

## Asset packs

Each `asset-packs/<Pack>/` folder is its own Workshop item (`docs/asset-packs.md`).

```bash
python3 scripts/asset_pack_docs.py       # README.md and ccmod.json per pack, from its contents
python3 scripts/asset_pack_workshop.py   # uploads, manifests and previews (one pack: name it)
```

`asset_pack_workshop.py` stages each pack as `dist/asset-pack-uploads/<Pack>/<Pack>/` (the
named-subfolder layout, so a pack also shows in the in-game mod list, as TD-Assets does), writes
`tools/workshop-uploader/packs/<Pack>.json` with a BBCode description built from the pack's
contents, and draws `tools/workshop-uploader/packs/<Pack>.jpg`. A manifest that already exists
keeps its `publishedfileid` and `visibility`; a new one starts Private (`2`).

Publish (Step 0 applies: restart Steam first):

```bash
cd tools/workshop-uploader
dotnet run --no-build -- packs/<Pack>.json "v1.0.0: first release"
```

The first publish creates the item and writes its `publishedfileid` back into the manifest:
commit that. Self-test on the Deck (subscribe, check the files land), then make it Public from
the item's Owner Controls. A pack's own `ccmod.json` version follows the pack, not the mod.

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

## Player crash reports

- **Ask for `<game install>/log/CrashLog.txt`.** It has one line per crash naming the faulting
  process and address, which separates the renderer (`ClientG.exe`) from the sim
  (`InstanceServerG.exe`).
- **A ClientG crash can still be ours.** The DLL imports no d3d11, dxgi or gdi32, so it cannot
  reach the GPU, but it patches ClientG's memory and code, and mod data has crashed ClientG
  before: a wrong-size CONFIG.MEG member, an unreadable WAV, and the EVA cache patch writing over
  heap headers on skirmish load (fixed in 5.0.0). "Video Card Driver Crash Detected!" and
  `DXGI_ERROR_DEVICE_REMOVED` are EA's own dialog text, so a player quoting them has lost the
  D3D11 device; that alone does not clear the mod.
- **There is no graphics or VRAM setting to offer.** `GAMECONSTANTS.XML` has none, and the
  mod's UI atlas is the same size as EA's (about 184 MB).
- **Workshop comments are capped at 1,000 characters.** Draft replies to fit.

---

## Don't-dos

- Don't re-create the item shell for an existing release — `publishedfileid` is allocated once per item.
- Don't pursue EA's `Uploader.exe` — confirmed bitrotted on Linux (Wine/Proton) AND on Luke's Windows install. Same hang as our tool was hitting pre-restart, but our tool is now easier to diagnose.
- Don't commit `tools/workshop-uploader/preview.jpg` or per-release `workshop.json` if they contain machine-absolute paths or release-specific descriptions; prefer relative paths so the JSON is portable.

---

## Historical context

- 2026-05-20: First Workshop publish for this mod (v0.3.0). EA's `Uploader.exe` ruled out as bitrotted across Windows / Wine / Proton. Built our own C# uploader using `Steamworks.NET`, mirroring the SteamUGC sequence in `~/.steam/steam/steamapps/common/CnCRemastered/SOURCECODE/CnCTDRAMapEditor/Utility/SteamworksUGC.cs` (EA's MapEditor — the only working official Workshop publisher for this app). Spent 4 hours hung on the same "preparing config" symptom EA's tool produces, until a Steam restart cleared it instantly. See memory `reference-workshop-publish-path` for the full rabbit hole.
