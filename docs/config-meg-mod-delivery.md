# CONFIG.MEG mod delivery — front-end launcher data IS moddable + shippable

**PROVEN on the Steam Deck, 2026-05-28.** This resolves the long-standing "distribution"
unknown that `campaign-tabs-research.md` and `reference-config-meg-campaign-display`
both flagged as open. It is the breakthrough that turns *all* CONFIG.MEG-resident
front-end data from "editable only by hacking the base install" into "moddable **and**
Workshop-distributable."

---

## TL;DR — the governing principle

**A mod can ship its own `Data/CONFIG.MEG`, and the launcher loads it over the base copy.**

So the real question for *any* launcher-locked feature becomes:

> Is the lock enforced by **CONFIG.MEG data** (an XML/`.LOC`/table the launcher reads) —
> or by **`ClientG.exe` code** (a hardcoded branch / hashed asset lookup)?

- **CONFIG.MEG data → now moddable + shippable** via this mechanism.
- **`ClientG.exe` code → still not mod-controllable** (would need binary patching; not Workshop-clean, breaks EAC/online). See `launcher-vs-dll-ownership.md` for the code-side boundary.

This doc is the **data-delivery** lever. `launcher-vs-dll-ownership.md` is the **code-ownership** map. They are complementary: the launcher's *autonomous behaviour* isn't ours, but the *data it reads* is.

---

## The proof (so we never re-litigate it)

1. Extracted `DATA/TEXT/MASTERTEXTFILE_EN-US.LOC` from base `CONFIG.MEG` (`meg_extract.py`).
2. Same-length byte edit: the country-name value `Turkey` → `Nod   ` (UTF-16LE, 12 bytes → 12 bytes, so the inner string-table offsets cannot shift).
3. Repacked with `scripts/meg_pack.py` → output was **44,201,888 bytes, identical to base** (1 file swapped, everything else byte-clean — the MEG format has no checksum/signature/encryption).
4. Shipped the repacked file as `<mod>/Data/CONFIG.MEG` (the **mod folder**, base install untouched), deployed to the Deck, relaunched.
5. **Result:** the skirmish lobby country picker showed **"Nod : No bonus"** and the in-game sidebar label read **"Nod"** — the mod's CONFIG.MEG was loaded. The loose `Data/` overlay had previously *failed* to reach this same front-end data, confirming the whole-MEG ship is what works.

---

## The recipe

```bash
# 1. extract the inner file you want to change
python3 scripts/meg_extract.py extract <base CONFIG.MEG> <innerPathFragment> /tmp/out/

# 2. edit it. For binary inner files (.LOC string tables) keep edits BYTE-LENGTH-IDENTICAL
#    (pad with spaces / same-width chars) so the inner format's offsets stay valid. Plain
#    XML inner files (FACTIONS.XML, INSTANCES.XML) can change length freely — meg_pack
#    recomputes the OUTER offsets; only the inner file's own internal offsets matter.

# 3. repack (replaces the inner file whose stored path ENDS WITH the given suffix)
python3 scripts/meg_pack.py repack <base CONFIG.MEG> /tmp/CONFIG.MEG \
    "<innerSuffix>=/tmp/edited_file"

# 4. ship it in the MOD folder (NOT the base install), then deploy
cp /tmp/CONFIG.MEG build/remaster/Vanilla_RA/Data/CONFIG.MEG
./deploy.sh --no-build --yes
```

`meg_pack.py verify a.meg b.meg` confirms identical file tables (name/size) — use it to sanity-check a repack.

---

## Facts & caveats

- **No integrity check.** The MEG reader (`Megafile.cs`) validates nothing — looks files up by path string, returns raw bytes. A faithful repack always loads.
- **Mod CONFIG.MEG SHADOWS the base** — it is *replaced*, not merged. So you ship the **full** repacked archive (~44 MB) with your one change, not a delta. Budget ~44 MB per release. (EA stopped patching the Collection, so base-drift/staleness is a non-issue.)
- **Mod-scoped.** The override only applies while the mod is active — the player's vanilla TD/RA front-end is untouched. This removes the "editing shared FACTIONS.XML breaks the user's TD" worry: it only breaks nothing, because it's only live under the mod.
- **Loose `Data/` overlay does NOT reach front-end data.** Audio SFXEvent XML *is* loose-overridable, but factions/campaign/master-text are not — they require the whole-MEG ship. (That asymmetry is why this took so long to pin down.)
- **Safe to test.** Because you ship into the mod folder and never touch the base install, a bad repack at worst does nothing (launcher ignores it) — it can't corrupt the base or trip Steam "verify."

---

## What this unlocks (CONFIG.MEG-resident, therefore now moddable)

- **Faction display names** — `MASTERTEXTFILE` `TEXT_FACTION_NAME_FACTION_*` (proven: Turkey→Nod).
- **Faction colours / lobby icons / buildable grid** — `FACTIONS.XML` (`Faction1=GDI`, `Faction2=Nod`, `Faction3–10`=RA countries; per-faction `UIColor`, `DefaultIcons`, `FactionObjects`, and the TD/RA gate `CampaignType`).
- **Mission Select roster** — `INSTANCES.XML` (`ShowOnMissionSelect`, `IsUnlockedAtStart`, `ExternalGameID`) — see `campaign-tabs-research.md`.
- **Any other CONFIG.MEG XML/table** — theatres/tilesets, audio-faction maps, GUI scene lists, etc. *If the data is in CONFIG.MEG, this mechanism reaches it.*

**For a "launcher-locked" feature investigation (e.g. theatres):** first locate where the limit/enum lives — there are **three** buckets, not two: (a) a **CONFIG.MEG XML** → moddable by this recipe (`meg_extract.py list <CONFIG.MEG> | grep -i <feature>`); (b) a **texture-atlas image** (e.g. a region in `MT_COMMANDBAR_COMMON.TGA`) → moddable via the loose-atlas override, see **`ui-atlas-modding.md`**; (c) **hardcoded in `ClientG.exe`** (`strings ClientG.exe`) → a true code lock, not reachable. ⚠️ The in-game sidebar **emblem** was first mis-filed as (c) — it's actually (b): `UI_SIDEBAR_FACTIONLOGO_ALLIES`/`_SOVIET` in the atlas, **moddable** (proven 2026-05-29). So "not in CONFIG.MEG" ≠ "locked" — check the atlas before concluding code-lock.

---

## Related

- `campaign-tabs-research.md` — Mission Select display model (its "Open issue #1: Distribution" is **resolved by this doc**).
- `mix-file-format.md` — `meg_extract.py` / `meg_pack.py` tooling + MEG/MIX format detail.
- `launcher-vs-dll-ownership.md` — the **code**-side boundary (what the launcher does autonomously, which this does *not* change).
