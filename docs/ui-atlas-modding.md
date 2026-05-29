# Launcher UI images ARE moddable — the MT_COMMANDBAR atlas (PROVEN 2026-05-29)

**PROVEN on the Steam Deck, 2026-05-29** — placed the `COMMAND & CONQUER` logo into the in-game radar-slot faction crest, vanilla, no EMC.

Companion to `config-meg-mod-delivery.md`: that doc is the front-end **data** lever (CONFIG.MEG → factions/missions/text); this is the **image** lever. Together: the launcher front-end (text, layout-data, *and* images) is moddable and Workshop-shippable without EMC.

---

## TL;DR

The Remastered launcher draws almost all 2D UI from one giant texture atlas — **`MT_COMMANDBAR_COMMON.TGA`** (6871×6716, 32-bit, in `TEXTURES_SRGB.MEG`) — with a sibling **`.MTD`** mapping `region-name → (x,y,w,h)`. **A mod ships a byte-edited copy of that `.TGA` loose in `Data/ART/TEXTURES/SRGB/` and the launcher loads it over the base.** Vanilla. No EMC. No `.MTD`/`.MTM` companions needed.

> ⚠️ **SCOPE (corrected 2026-05-29): this loose override is honored by the IN-GAME renderer only** (the sidebar/radar crest — that's what's PROVEN here). The **front-end shell** (main menu, skirmish lobby, faction picker) does **NOT** read the loose overlay — it renders from the base MEG. Confirmed: a loose atlas with the picker flags repainted never changed after a full restart. Front-end picker icons are instead repointed via `FACTIONS.XML`→`SmallIconName` (in CONFIG.MEG — see `config-meg-mod-delivery.md`), and that only resolves to the `UI_Multiplayer_PlayerSlot_Faction_NN` regions the front-end preloads (any other region → startup crash). Getting *custom pixels* into the front-end needs a MEG-delivery route — see **`front-end-texture-meg-spike.md`**.

---

## The recipe

1. Extract base `MT_COMMANDBAR_COMMON.TGA` + `.MTD` from `TEXTURES_SRGB.MEG` (streaming lister — see `mix-file-format.md`).
2. Find your region in the `.MTD`: locate the `NAME.TGA` bytes, **skip trailing null padding** (1–2 bytes, varies), read 4× little-endian `int32` = `x, y, w, h` (top-left origin).
3. **Byte-edit the `.TGA` pixels in place.** The atlas is 32-bit **BGRA**, **bottom-origin** (`desc=0x00`), 18-byte header, **no footer**. For image pixel `(x,y)` (top-left), the file offset is `18 + (H-1-y)*W*4 + x*4`; write bytes `B,G,R,A`. Preserve the header/footer exactly — don't round-trip through PIL's TGA writer (it appends a footer / flips the descriptor; harmless per the red-herring below, but byte-editing keeps the file format-identical and the rsync delta tiny).
4. Ship the edited `MT_COMMANDBAR_COMMON.TGA` **loose** at `<mod>/Data/ART/TEXTURES/SRGB/`. `.TGA` only. Deploy.

---

## The regions that matter (RA) — **picking the right one is the whole battle**

| UI element | Region(s) | Keying |
|---|---|---|
| **In-game sidebar / radar faction crest** | **`UI_SIDEBAR_FACTIONLOGO_ALLIES` / `_SOVIET`** (794×713) | **per-SIDE** → faction-neutral only |
| Lobby faction-pick big logo | `RA_UI_MULTIPLAYER_ALLIED/SOVIET_LOGO_LARGE_NORMAL`/`_HOVER`/`_SELECTED` (309–311) | per-side |
| Lobby / player-list flag icon | `RA_UI_FLAG_ICON_<COUNTRY>` (SPAIN, TURKEY, … 73×40) | **per-COUNTRY** |
| Small player-list logo | `RA_UI_ALLIED/SOVIET_LOGO_SMALL` | per-side |

We burned ~an afternoon editing `RA_UI_MULTIPLAYER_ALLIED_LOGO_LARGE_*` (the **lobby** logo) and seeing no in-game change. The in-game crest is **`UI_SIDEBAR_FACTIONLOGO_ALLIES`** — a different, 794×713, metallic-backed region. *Always confirm the region.*

Native `UI_SIDEBAR_FACTIONLOGO_GDI`/`_NOD`/`_DINO` regions exist (Tiberian Dawn), but the RA launcher picks `ALLIES`/`SOVIET` for RA players, so they aren't auto-shown in RA.

**Per-side vs per-country is the design constraint:**
- In-game crest is **per-SIDE** → editing it is **faction-neutral** (hits everyone on that side). Great for "one logo for all" (we put the C&C logo). Can't be "GDI's logo only" in-game.
- Flags are **per-COUNTRY** → `RA_UI_FLAG_ICON_SPAIN`→GDI and `_TURKEY`→Nod are **Allied-safe** (England/USSR keep theirs). This is the clean lever for per-faction identity on the faction-SELECT screen.

---

## Two red herrings (cleared)

- **Format was forgiving — the region was the bug.** Reilsss's *working* atlas is `desc=0x08` + a TGA footer (PIL-style); our byte-exact `desc=0x00` also works. Both load. The repeated failures were entirely the **wrong region** (lobby logos), not the format.
- **EMC is NOT required.** Reilsss's mod requires EMC for his *units/INI* content; the loose-atlas texture override itself is **vanilla** — proven by our non-EMC mod. This **corrects** the earlier "needs EMC → textures blocked" / "emblem is a code lock" inferences in `config-meg-mod-delivery.md` and `launcher-vs-dll-ownership.md`.

---

## Why our TD sprites already worked (context)

Our TD building/unit sprites (`Data/ART/TEXTURES/SRGB/RED_ALERT/.../*.ZIP`) render via our **DLL's tileset-XML pipeline** (the MFCD-donor path) — a different mechanism. The UI atlas is launcher-internal and needed the loose-`.TGA` override this doc establishes.

## Payload

The atlas is ~176 MB uncompressed (one loose `.TGA`). A **single** ship covers *all* UI-image edits (crest + flags + buttons + menus). Byte-editing keeps each iteration's rsync delta tiny.

## Related
- `config-meg-mod-delivery.md` — front-end **data** lever (factions/missions/master-text).
- `launcher-vs-dll-ownership.md` — the code boundary (this is the image side of the data lever).
- `mix-file-format.md` — MEG/atlas extract tooling.
