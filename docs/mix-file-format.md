# MIX & MEG archive formats — reference + asset inventory

**Status:** Reference. The MIX and MEG formats, the tooling, and the asset inventories, verified by
round-tripping the game's own archives with our tools.

Tooling lives in `scripts/` (Python) and `tools/mixtool/` (C++, from Vanilla Conquer).

---

## 1. The formats at a glance

See the field manual's [MEG and MIX archives](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/formats/meg-and-mix-archives.md#when-you-need-this) for the three formats side by side.
MIX entries are keyed by a hash of the filename, which is why MIX listings need the name database in §5.

---

## 2. Classic (TD) MIX format

Authoritative structs: `tools/mixtool/mixcreate.h` (`FileHeader`, `SubBlock`); reader `scripts/mix_tools.py:read_mix`.

The layout, the signed-CRC order and the missing magic are in the field manual's
[MEG and MIX archives](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/formats/meg-and-mix-archives.md#classic-mix), classic MIX. Our `pack` honours the order
(`mix_tools.py:cmd_pack`), and our extended-format detector tells the two apart by `first != 0` (§3).

---

## 3. Extended (RA) MIX format

Red Alert wraps the classic layout with a flags header and optional encryption. Reader: `scripts/ra_mix_extract.py`. Crypto chain mirrors VC's `common/mixfile.h` + `pk.cpp` + `blowfish.cpp`.

The flags header, the flags each archive carries, the key block and the encrypted index are in the field manual's
[MEG and MIX archives](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/formats/meg-and-mix-archives.md#red-alerts-outer-mix), Red Alert's outer MIX. The flag words are
`mixcreate.h:MixFlags`, and the index cipher is standard Blowfish-ECB with big-endian words.

> **Tooling split:** `ra_mix_extract.py` handles *encrypted* extended mixes and *classic* mixes, but not the *extended-but-unencrypted* variant (flags header, no Blowfish). The Aftermath and Counterstrike `MAIN.MIX` use that combination; `mix_plain_alt.py` reads them (§8.1).

---

## 4. The filename hash (`ww_crc` / CRCEngine)

The `SubBlock.CRC` is Westwood's `CRCEngine` hash, in the field manual's
[MEG and MIX archives](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/formats/meg-and-mix-archives.md#the-filename-hash). Ours is `scripts/mix_tools.py:ww_crc`; the name DB calls it
`HASH_RACRC`, and carries a second column, `ts_crc`, for Tiberian Sun and RA2's different hash.

---

## 5. CRC → filename resolution (the name database)

Because MIX stores hashes, a raw listing is opaque. `tools/mixtool/mixnamedb_data.cpp` is a **29,075-entry** table — `{file_name, file_desc, ra_crc, ts_crc}`, derived from the XCC mix database (+ tomsons26). Its `ra_crc` column is exactly our `ww_crc`.

`scripts/mix_namedb.py` parses that table into `{crc → (name, desc)}` and exposes `resolve(crc)`. After dropping zero-CRC rows it yields **11,798 RA names / 17,436 TS names**. Both `mix_tools.py list` and `ra_mix_extract.py list` now print resolved filenames automatically (soft import — they degrade to raw CRCs if the DB is unavailable).

```
scripts/mix_namedb.py --stats          # entry counts
scripts/mix_namedb.py 0x1D597662       # -> 00-0000.aud
```

---

## 6. Nesting (mix-in-mix)

Outer mixes hold inner mixes as ordinary entries: see the field manual's
[MEG and MIX archives](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/formats/meg-and-mix-archives.md#where-red-alerts-files-are) for what each holds. `REDALERT.MIX`'s 6 nested mixes total
about 25 MB.

`ra_mix_extract.py:find_in_mix` recurses automatically on extract (anything >64 bytes is a recursion candidate); `/tmp`-style inventory walks recurse into entries whose resolved name ends in `.mix`.

---

## 7. MEG (Remastered bundles) — brief

Reader `scripts/meg_extract.py`, repacker `scripts/meg_pack.py`. The 8-byte magic (`0xFFFFFFFF`/`0x8FFFFFFF` +
version) is optional: EA's reader accepts its absence. The layout, and why a repack loads (nothing is
checked, and a no-change repack is byte-identical), are in the field manual's [MEG and MIX archives](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/formats/meg-and-mix-archives.md#meg).
Editing the base archive is reverted by Steam's verify. TF ships its `INSTANCES.XML` loose (`campaigns-page.md`);
on the Deck, a broken mission def killed that mission's launch. The campaign model is `campaign-tabs-research.md`,
and a shipped `CONFIG.MEG` is `config-meg-mod-delivery.md`.

---

## 8. Tooling map

| Tool | Lang | Formats | R/W | Names | Notes |
|---|---|---|---|---|---|
| `scripts/mix_tools.py` | Py | classic | **R+W** | resolves | packs `TFASSETS.MIX`; `ww_crc` lives here |
| `scripts/ra_mix_extract.py` | Py | encrypted + classic | R | resolves | recursive extract; needs `cryptography` |
| `scripts/mix_plain_alt.py` | Py | **alt header, unencrypted** | R | resolves | the third flavour — see the note below; how RA campaign scenario INIs come out |
| `scripts/mix_namedb.py` | Py | — | resolver | — | parses the 29k XCC table |
| `scripts/meg_extract.py` | Py | MEG | R | native | Remastered bundles |
| `scripts/meg_pack.py` | Py | MEG | **R+W** | preserves | byte-identical round-trip; repack `CONFIG.MEG` with edited XML (no integrity check → game accepts it) |
| `tools/mixtool/` | C++ | both, **incl. encrypted writer** | R+W | uses DB | has private key + `RandomStraw` to author encrypted mixes |

**We ship our own mixes (e.g. `TFASSETS.MIX`) as *classic / unencrypted*** — the engine reads them fine and `mix_tools.py` can write them. Authoring an *encrypted* mix would require the C++ `tools/mixtool` path; we have no reason to.

### 8.1 The third flavour: alt header with the encryption bit clear

| Shape | Header | Reader |
|---|---|---|
| classic | count first, no flag word | `mix_tools.py` |
| **alt header, plaintext** | `first=0`, flags **without** `0x02` | **`mix_plain_alt.py`** |
| alt header, encrypted | `first=0`, flags **with** `0x02` | `ra_mix_extract.py` |

The Aftermath and Counterstrike `MAIN.MIX` are the middle shape (field manual,
[MEG and MIX archives](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/formats/meg-and-mix-archives.md#traps), traps). On them `mix_tools.py` reports `0 files` and `ra_mix_extract.py` says
"could not parse as a mix (encrypted or classic)"; neither means the archive is broken.

Campaign scenario INIs come out of those archives this way, the extraction path for hijacking a
Counterstrike/Aftermath slot (`campaign-tabs-research.md`), so this tool is a campaign-work dependency.

---

## 9. Cookbook

```bash
# List with filenames (classic)
scripts/mix_tools.py list  .../TIBERIAN_DAWN/CD1/CONQUER.MIX

# List with filenames (encrypted; also reads classic)
scripts/ra_mix_extract.py list  .../RED_ALERT/CD1/EXPAND2.MIX

# Extract one file by name (hashes the name, searches recursively through nesting)
scripts/ra_mix_extract.py extract  .../EXPAND2.MIX  ctnk.shp  out/

# Pack a classic mix (optionally rename entries on the way in)
scripts/mix_tools.py pack  TFASSETS.MIX  tdobli.shp  hvydoor1.aud:slam.aud

# Resolve an unknown CRC seen in a listing
scripts/mix_namedb.py 0xe6e4fbb4        # -> ctnk.shp
```

---

## 10. Asset inventories (the four deep dives)

Names/sizes only — we do **not** bulk-commit extracted EA bytes (see §11).

### 10.1 Tiberian Dawn (the TD-port source)

| Archive | Entries | Highlights |
|---|---|---|
| `CONQUER.MIX` | 266 (100%) | 262 SHP — the entire TD unit/building/cameo sprite set (`*icon.shp` cameos, structures, infantry, vehicles). The well we draw from for every TD port. |
| `GENERAL.MIX` | 165 | **73 mission INIs** (`scg*`=GDI, `scb*`=Nod/Brotherhood) + 72 map `.bin` + 9 WSA + 6 CPS + 4 PAL. |
| `DESERT/TEMPERAT/WINTER.MIX` | ~220 each | theater shapes (`.des`/`.tem`/`.win`), **11 MRF remap/fade tables**, 1 theater PAL each. |
| `AUD.MIX` | 32 | music tracks. |
| `SOUNDS.MIX` | 148 | 108 SFX `.aud` + **unit-voice takes `.v00`–`.v03`** (the infantry/vehicle acknowledgments we route for GDI/Nod). |
| `SPEECH.MIX` | 44 | EVA speech `.aud`. |

### 10.2 RA expansions (Counterstrike & Aftermath)

| Archive | Entries | Unit SHPs & data |
|---|---|---|
| `EXPAND.MIX` (Counterstrike) | 27 | Giant-Ant mission: `ant1/2/3.shp`, `lar1/2.shp` (larvae), `quee.shp` (queen), `antdie.shp`; `rambo*`/`stav*` voices; `mission.ini`, `tutorial.ini`. |
| `EXPAND2.MIX` (Aftermath) | 32 (100%) | **New units:** `ctnk` (Chrono Tank), `ttnk` (Tesla Tank), `qtnk` (MAD Tank), `stnk` (Phase Transport), `dtrk` (Demo Truck), `msub` (Missile Sub), `carr` (Carrier) + the ant set. **`aftrmath.ini`, `mplayer.ini`, `mission.ini`, `tutorial.ini`**, `conquer.eng`. |

### 10.3 Scenario / mission INIs (co-op data side)

- **RA campaign** lives in `MAIN.MIX` → `general.mix`: `scg01ea…` (Allied) and `scu01ea…scu14ea` (Soviet), beside the `scm01ea…scm24ea` multiplayer maps, plus `mission.ini`. Naming: `sc` + the house prefix (`g`=Allied, `u`=Soviet, as `SCU31EA` in EA's `EXPAND.CPP`; `m`=multiplayer) + mission## + direction + variant.
- **TD campaign** lives in `GENERAL.MIX`: `scg*` (GDI) / `scb*` (Nod).
- These single-player `.ini` scenarios are the adaptation source for the post-v1 co-op arc (`CNC_Start_Custom_Instance` + `.mpr`); `EXPAND2.MIX:mplayer.ini` is the multiplayer config reference.

### 10.4 Palettes & remap tables (classic-mode remap source)

- **RA** (`REDALERT.MIX`): `egopal.pal`, `interior.pal`, `snow.pal`, `temperat.pal` + 48 `.lut` color lookup tables. Also note **`rules.ini` (≈60 KB) lives here** — the canonical RA rules.
- **TD** (theater mixes): `desert.pal`, `temperat.pal`, `winter.pal` + the `.mrf` fade/remap tables.
- These are the RA-vs-TD palette pair behind `classic-mode-palette-remap.md` (the TD-176-191 → RA-80-95 remap).

> ~100% of all entries resolved; the only misses were 1 entry in `MAIN.MIX` and 2 in `REDALERT.MIX` not present in the XCC DB (likely Remastered-era additions).

---

## 11. Licensing & guardrails

- **Filenames are fine to catalogue.** The name DB itself is GPL v3 (ships in VC); listing names/sizes is reconnaissance, not redistribution.
- **Do not bulk-commit extracted EA asset bytes.** Extract only what the mod actually ships, and only when needed (the selective TD SHPs in `TFASSETS.MIX` are the model). The inventories above are name listings, not dumps.
- **Don't broadly mine `REDALERT.MIX`** — target specific files (palettes, `rules.ini`) rather than extracting the whole sprite set.
- The crypto here is for *interop*, exactly as Vanilla Conquer (GPL) implements it; reading our legally-owned archives for modding is the intended use.
