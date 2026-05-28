# MIX & MEG archive formats — reference + asset inventory

**Status:** Mapped & verified 2026-05-28. All format details below were confirmed by round-tripping our own tooling against the real game archives on disk; all asset inventories were produced with 100% (or near-100%) filename resolution via the XCC name database. This is the canonical reference for every archive operation in this mod — extracting TD art for ports, pulling palettes for the classic-mode remap, reading scenario INIs, and packing `TFASSETS.MIX`.

Tooling lives in `scripts/` (Python) and `tools/mixtool/` (C++, from Vanilla Conquer).

---

## 1. The formats at a glance

| | Classic MIX | Extended MIX | MEG |
|---|---|---|---|
| Used by | Tiberian Dawn; inner (nested) RA mixes | Red Alert outer mixes | Remastered Collection bundles |
| Keys files by | CRC of filename | CRC of filename | **real filename** (string table) |
| Encryption | none | optional (Blowfish + RSA key) | none |
| Checksum | none | optional (20-byte SHA1 trailer) | none |
| Our reader | `mix_tools.py` (R+W) | `ra_mix_extract.py` (R) | `meg_extract.py` (R) |
| Example | `CONQUER.MIX` | `REDALERT.MIX`, `MAIN.MIX`, `EXPAND2.MIX` | `CONFIG.MEG`, `SFX3D.MEG` |

The defining difference between MIX and MEG: **MIX entries are keyed by a hash of the filename** (the name itself is not stored), whereas **MEG stores real paths**. That single fact is why MIX listings need the name database in §5 to be human-readable, and MEG listings don't.

---

## 2. Classic (TD) MIX format

Authoritative structs: `tools/mixtool/mixcreate.h` (`FileHeader`, `SubBlock`); reader `scripts/mix_tools.py:read_mix`.

```
offset  size  field
0       2     int16  count        # number of files
2       4     int32  size         # total bytes of the data section
6       12*N  SubBlock[count]     # the index, sorted ascending by signed CRC
6+12N   ...   data section        # raw file bytes, concatenated

SubBlock (12 bytes):
  int32 CRC      # ww_crc(UPPERCASE filename)  — see §4
  int32 Offset   # from start of data section
  int32 Size
```

- The index is **sorted by signed CRC** because the engine binary-searches it. Our `pack` honors this (`mix_tools.py:cmd_pack`).
- No header magic — a classic mix is identified positionally (and, in our extended-format detector, by `first != 0`; see §3).

---

## 3. Extended (RA) MIX format

Red Alert wraps the classic layout with a flags header and optional encryption. Reader: `scripts/ra_mix_extract.py`. Crypto chain mirrors VC's `common/mixfile.h` + `pk.cpp` + `blowfish.cpp`.

### 3.1 The 4-byte flags header

Read as two `int16` little-endian: `(first, second)`.
- **`first == 0` signals the extended format.** (A classic mix's first 2 bytes are a nonzero file count.)
- `second` holds the flag bits. The full 32-bit flag word (`mixcreate.h:MixFlags`):

```
HAS_CHECKSUM = 0x00010000   # 20-byte SHA1 appended at end of file
IS_ENCRYPTED = 0x00020000   # header (index) is Blowfish-encrypted
```

So a `second` of `0x0002` ⇒ `IS_ENCRYPTED`. **Every RA archive shipped with the Remastered Collection is encrypted** (`REDALERT/MAIN/EXPAND/EXPAND2.MIX` all read `0x0002`).

### 3.2 PK (RSA) block → Blowfish key

If encrypted, the next **80 bytes** are an RSA-style block encrypted with Westwood's public key:
- Public exponent `65537`; 320-bit modulus from `redalert/const.cpp Keys[]`.
- Block sizes: `Crypt_Block_Size = 40`, `Plain_Block_Size = 39` ⇒ 2 blocks ⇒ 78 plaintext bytes.
- **First 56 plaintext bytes = the Blowfish key.**

### 3.3 Blowfish index header

Blowfish-ECB (standard, big-endian words) decrypt of the index, which is the classic layout minus the count's int16/int32 split:
```
u16 count + u32 datasize + count * SubBlock(12)
```
The encrypted span is `roundup8(6 + count*12)` (Blowfish works on whole 8-byte blocks). Decrypt one block first to learn `count`, then the full span.

### 3.4 Data section

Plaintext, starting immediately after the (padded) encrypted header — i.e. at `4 + 80 + span`. **Only the index is encrypted; file bytes are not.**

> **Known tooling gap (benign):** `ra_mix_extract.py` handles *encrypted* extended mixes and *classic* mixes, but not the rare *extended-but-unencrypted* variant (flags header, no Blowfish). No Remastered RA archive uses that combination, so this has never bitten us. Fix if a future archive needs it.

---

## 4. The filename hash (`ww_crc` / CRCEngine)

The `SubBlock.CRC` is Westwood's `CRCEngine` hash of the **uppercased ASCII** filename. Implemented and validated in `scripts/mix_tools.py:ww_crc`:

```
crc = 0
for each 4-byte chunk of UPPER(name):     # final partial chunk zero-padded
    crc = lrotl32(crc, 1) + le32(chunk)   # 32-bit wrap, kept signed
```

- TD **and** RA (and the Remastered repacks of both) use this same hash — what the name DB calls `HASH_RACRC`. Validated: `ww_crc("00-0000.aud") == 0x1D597662`, the DB's `ra_crc`, and 266/266 of `CONQUER.MIX` resolve.
- Tiberian Sun / RA2 use a *different* finalization (`ts_crc` in the DB) — not relevant to this mod, but it's why the DB carries two CRC columns per file.

---

## 5. CRC → filename resolution (the name database)

Because MIX stores hashes, a raw listing is opaque. `tools/mixtool/mixnamedb_data.cpp` is a **29,075-entry** table — `{file_name, file_desc, ra_crc, ts_crc}`, derived from the XCC mix database (+ tomsons26). Its `ra_crc` column is exactly our `ww_crc`.

`scripts/mix_namedb.py` (added 2026-05-28) parses that table into `{crc → (name, desc)}` and exposes `resolve(crc)`. After dropping zero-CRC rows it yields **11,798 RA names / 17,436 TS names**. Both `mix_tools.py list` and `ra_mix_extract.py list` now print resolved filenames automatically (soft import — they degrade to raw CRCs if the DB is unavailable).

```
scripts/mix_namedb.py --stats          # entry counts
scripts/mix_namedb.py 0x1D597662       # -> 00-0000.aud
```

---

## 6. Nesting (mix-in-mix)

An outer mix can contain inner mixes as ordinary entries. The Remastered RA bundles use this heavily — the encrypted outer mix holds (usually classic, unencrypted) inner mixes:
- `MAIN.MIX` → **12 nested `.mix`** (~454 MB: theater + movie bundles).
- `REDALERT.MIX` → **6 nested `.mix`** (~25 MB).

`ra_mix_extract.py:find_in_mix` recurses automatically on extract (anything >64 bytes is a recursion candidate); `/tmp`-style inventory walks recurse into entries whose resolved name ends in `.mix`.

---

## 7. MEG (Remastered bundles) — brief

Different lineage, name-based. Reader `scripts/meg_extract.py` (format from `SOURCECODE/CnCTDRAMapEditor/Utility/Megafile.cs`): optional 8-byte magic (`0xFFFFFFFF`/`0x8FFFFFFF` + version), then `num_files / num_strings / string_table_size`, a uint16-length-prefixed string table, a fixed 20-byte-per-entry file table, then blobs at absolute offsets. `CONFIG.MEG` holds the launcher's XML (e.g. `RABUILDABLES.XML`, `SFXEVENTSNONLOCALIZED.XML`); `SFX3D.MEG` holds the remastered WAVs we route TD audio through.

---

## 8. Tooling map

| Tool | Lang | Formats | R/W | Names | Notes |
|---|---|---|---|---|---|
| `scripts/mix_tools.py` | Py | classic | **R+W** | resolves | packs `TFASSETS.MIX`; `ww_crc` lives here |
| `scripts/ra_mix_extract.py` | Py | encrypted + classic | R | resolves | recursive extract; needs `cryptography` |
| `scripts/mix_namedb.py` | Py | — | resolver | — | parses the 29k XCC table |
| `scripts/meg_extract.py` | Py | MEG | R | native | Remastered bundles |
| `tools/mixtool/` | C++ | both, **incl. encrypted writer** | R+W | uses DB | has private key + `RandomStraw` to author encrypted mixes |

**We ship our own mixes (e.g. `TFASSETS.MIX`) as *classic / unencrypted*** — the engine reads them fine and `mix_tools.py` can write them. Authoring an *encrypted* mix would require the C++ `tools/mixtool` path; we have no reason to.

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

## 10. Asset inventories (the four deep dives, 2026-05-28)

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

- **RA campaign** lives in `MAIN.MIX`: 68 INIs — `scg01ea…scg14ea` (Allied) and `scm01ea…scm17ea` (Soviet), plus `mission.ini`. Naming: `sc` + side (`g`=Allied, `m`=Soviet) + mission## + variant.
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
