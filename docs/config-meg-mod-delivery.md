# CONFIG.MEG mod delivery — front-end launcher data IS moddable + shippable

**Status:** Reference. A mod ships its own `Data/CONFIG.MEG` and the launcher loads it over the
base; every front-end data edit in the mod rides on it.

Proven on the Steam Deck: all CONFIG.MEG-resident front-end data is moddable and ships on the
Workshop, with no edit to the base install.

---

## The governing principle

See the field manual's [Overriding the launcher's data](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#a-replacement-configmeg), A replacement `CONFIG.MEG`, and
[What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#search-in-this-order), Search in this order.
This doc is TF's data-delivery lever; `launcher-vs-dll-ownership.md` is TF's code-ownership map.

---

## The proof (so we never re-litigate it)

1. Extracted `DATA/TEXT/MASTERTEXTFILE_EN-US.LOC` from base `CONFIG.MEG` (`meg_extract.py`).
2. Same-length byte edit: the country-name value `Turkey` → `Nod   ` (UTF-16LE, 12 bytes → 12 bytes, so the inner string-table offsets cannot shift).
3. Repacked with `scripts/meg_pack.py` → output was **44,201,888 bytes, identical to base** (1 file swapped, everything else byte-clean — the MEG format has no checksum/signature/encryption).
4. Shipped the repacked file as `<mod>/Data/CONFIG.MEG` (the **mod folder**, base install untouched), deployed to the Deck, relaunched.
5. **Result:** the skirmish lobby country picker showed **"Nod : No bonus"** and the in-game sidebar label read **"Nod"** — the mod's CONFIG.MEG was loaded.

---

## The recipe

```bash
# 1. extract the inner file you want to change
python3 scripts/meg_extract.py extract <base CONFIG.MEG> <innerPathFragment> /tmp/out/

# 2. edit it, keeping every member at its exact base size (the same-size rule below).
#    XML: pad back to size from comments. .LOC: the file total is fixed, but a string may
#    grow if it takes bytes from another (byte-neutral redistribution, scripts/loc_relabel.py).

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

See the field manual's [MEG and MIX archives](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/formats/meg-and-mix-archives.md#meg), MEG, and [Overriding the launcher's data](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#three-ways-in), Three ways in and Traps.
TF ships the full ~44 MB archive in every release, and loose files beside it (`campaigns-page.md` ships its screens
loose). A repack can't corrupt the base install or trip Steam's verify, but one that changes any member's size crashes the
launcher at boot under the mod (the same-size rule below).

---

## What this unlocks (CONFIG.MEG-resident, therefore now moddable)

- **Faction display names** — `MASTERTEXTFILE` `TEXT_FACTION_NAME_FACTION_*` (proven: Turkey→Nod).
- **Faction colours / lobby icons** — `FACTIONS.XML` (`Faction1=GDI`, `Faction2=Nod`, `Faction3–10`=RA countries; per-faction `UIColor`, `DefaultIcons`, `FactionObjects` (empty in every entry; EA ties it to the structure breakdown screen), and the TD/RA gate `CampaignType`).
- **Mission Select roster** — `INSTANCES.XML` (`ShowOnMissionSelect`, `IsUnlockedAtStart`, `ExternalGameID`) — see `campaign-tabs-research.md`.
- **Any other CONFIG.MEG XML/table** — theatres/tilesets, audio-faction maps, GUI scene lists, etc. *If the data is in CONFIG.MEG, this mechanism reaches it.*

**For a "launcher-locked" feature investigation:** follow the field manual's [What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#search-in-this-order), Search in this order.
List the data with `meg_extract.py list <CONFIG.MEG> | grep -i <feature>`. Not in CONFIG.MEG isn't locked: check the UI
atlas too (`ui-atlas-modding.md`), where the radar crest is `UI_SIDEBAR_FACTIONLOGO_ALLIES`/`_SOVIET`.

---

## ⚠️ THE SAME-SIZE RULE (read before ANY edit — proven 2026-05-30, re-proven the hard way 2026-06-09)

**Every inner file in the mod's CONFIG.MEG must keep its EXACT original byte size.**
Mechanism: the launcher reads the mod MEG's file *data* at the **base archive's offsets**,
ignoring the mod MEG's own (correct) offset table. Grow or shrink any member and every file
after it shifts → the launcher reads some *downstream* file at a stale offset → garbage →
**crash at boot**. Diagnostics for this failure mode:

- ClientG dies at RVA `0x56A539` with `EXCEPTION_ACCESS_VIOLATION`. That address is the
  **generic fatal-assert path**, not a specific subsystem — extract the crash-thread stack
  strings from the minidump (`AppData/Roaming/CnCRemastered/*.dmp`) and you'll find the real
  assert, e.g. `pglib\xml.cpp(1227): error reading xml header from .\Data\XML\GameConstants.xml`.
  The file it names is the innocent *downstream* victim, not the file you edited.
- Recipe: edit in place, then pad back to the exact original size by cannibalizing bytes from
  XML comments (or padding inside one). Verify member size == original AND total MEG == base.
- Consequence: a mod CONFIG.MEG can only **override existing files at their exact size** —
  never grow, shrink, add, or remove members.

## Scope limit: mod CONFIG.MEG feeds the ClientG FRONT-END only

`InstanceServerG` (the match-host process) resolves instance definitions, map files, and the
lobby preview content from **base game data**, not the mod's CONFIG.MEG. Why a new entry lists but
won't start, and the carrier that starts it, are on the field manual's
[New maps in the skirmish Official list](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/new-maps-in-the-skirmish-list.md#why-a-listed-map-wont-start), Why a listed map won't start and Starting it
(TF's tests: the assert at `serveripcmessagehandler.cpp(268)`; a hijacked `Community_2` still loaded `SCMC1EA`).

- The launcher reads `Data/CNCDATA/...` map INIs via CWD-relative paths = **base install
  only**; a mod's `Data/CNCDATA/` is never searched. The game does read a mod's map INIs, from its
  `CCDATA\` (`campaign-tabs-research.md`).

TF launches its new entries through Hastings' `D6` (`td-base-art.md`, "TD maps in the Official list"). Workshop
*map items* (custom-maps tab, native pipeline, previews from the shipped TGA) remain the plain route.

---

## Related

- `campaign-tabs-research.md` — Mission Select display model (its "Open issue #1: Distribution" is **resolved by this doc**).
- `mix-file-format.md` — `meg_extract.py` / `meg_pack.py` tooling + MEG/MIX format detail.
- `launcher-vs-dll-ownership.md` — the **code**-side boundary (what the launcher does autonomously, which this does *not* change).
