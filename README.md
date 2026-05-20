# Tiberian Factions for Red Alert

A mod for **Command & Conquer: Red Alert Remastered** that adds GDI and Nod as new playable factions alongside Allies and Soviets.

> ⚠️ **Pre-release / under active development.** v0.3.0 is playable end-to-end in skirmish — four sides on one map — but content differentiation (TD-themed rosters, superweapons, AI) is still being filled in. Not yet published to Steam Workshop.

This repository is a **fork of [Vanilla Conquer](https://github.com/TheAssemblyArmada/Vanilla-Conquer)**, which provides the DLL build base. The original Vanilla Conquer README is preserved as [`README-VANILLA-CONQUER.md`](./README-VANILLA-CONQUER.md).

## Goal

Add `HOUSE_GDI` and `HOUSE_NOD` as new playable houses (sides) in Red Alert Remastered's engine, with their own unit rosters, structures, superweapons (Ion Cannon, Nuke), and AI. The end state is four-faction skirmish: **Allies vs Soviets vs GDI vs Nod**, on the same map, in the same match.

## Status

- v0.0.x — ✅ scaffolding, Linux mingw cross-compile + Steam Deck deploy pipeline.
- v0.1.0 — ✅ engine extension: `HOUSE_GOOD`/`HOUSE_BAD` selectable as cloned-from-Allies/Soviets variants.
- v0.2.0 — ✅ engine decoupling: `HOUSE_GOOD`/`HOUSE_BAD` detached from `HOUSEF_ALLIES`/`HOUSEF_SOVIET`; 4-side-aware Unlimbo dispatch; France→`HOUSE_GOOD` launcher swap.
- v0.3.0 — 🚧 in progress: TD-themed GDI/Nod building catalogues (TDFACT, TDNUKE/NUK2, TDPYLE, TDSILO, TDWEAP, TDMCV…), INI-driven mod-entry registration, asset pipeline (manifest → ZIP repack → rsync to Deck), TD-authentic build times. Playable in skirmish.
- v0.4.0+ — planned: TD-themed unit rosters, superweapons (Ion Cannon, Nuke), faction-specific AI.

See [`CHANGELOG.md`](./CHANGELOG.md) for detailed progress.

## Building & deploying (for developers)

This project builds on Linux via mingw-w64 cross-compile.

```bash
# Install build dependencies (Ubuntu 24.04+):
sudo apt install -y cmake g++-mingw-w64 mingw-w64-tools ninja-build

# Build + deploy to a Steam Deck (over Tailscale, passwordless SSH):
./deploy.sh
```

The `deploy.sh` script builds the DLL and SCPs the resulting mod folder to `deck@steamdeck`'s Proton mod path. Override the SSH target with `DECK_HOST=user@hostname ./deploy.sh` if your Deck isn't named `steamdeck` on your Tailnet.

To build without deploying:

```bash
CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake \
  VC_CXX_FLAGS="-w;-fpermissive" \
  cmake --workflow --preset remaster
```

The resulting mod folder lands at `build/remaster/Vanilla_RA/`.

## Installing (for players)

_(Once published.)_ Subscribe via Steam Workshop, then enable "Tiberian Factions for Red Alert" from C&C Remastered's mod list when launching Red Alert. Or download the release zip from GitHub and extract into `Documents/CnCRemastered/Mods/Red_Alert/`.

## Dependencies

- **[Vanilla Conquer](https://github.com/TheAssemblyArmada/Vanilla-Conquer)** — engine base (this repository is a fork).

## Compatibility

- **CFE Patch Redux**: incompatible — both ship a custom `RedAlert.dll`. Disable CFE when running this mod.

## License

**GPL v3**, inherited from Vanilla Conquer (which inherited from EA's 2020 source release). See [`License.txt`](./License.txt).

## Credits

- **EA / Petroglyph** — original Tiberian Dawn (1995) and Red Alert (1996), and the 2020 Remastered Collection.
- **[The Assembly Armada](https://github.com/TheAssemblyArmada)** — Vanilla Conquer maintainers.

This mod is not endorsed by or affiliated with Electronic Arts.

## Acknowledgements & Inspiration

This project doesn't bundle these mods, but their work shaped how we approached the engine. Thanks to:

- **Reilsss** — [Reilsss's Command & Conquer in Red Alert](https://steamcommunity.com/sharedfiles/filedetails/?id=2853520457) — asset-replacement approach for reimagining RA factions as GDI/Nod.
- **DontCryJustDie** — [TD-Assets](https://steamcommunity.com/sharedfiles/filedetails/?id=3003163891) — TD art and audio surfaced into the RA engine; reference for the `TD`-prefixed naming convention.
- **JohnnyJigglez** — [EMC (Enhanced Modding Capabilities)](https://www.nexusmods.com/commandandconquerremastered/mods/21) — INI-driven custom buildings/vehicles patterns informed our extensibility approach.
- **ChthonVII** — [CFE Patch Redux](https://steamcommunity.com/sharedfiles/filedetails/?id=2268301299) — engine-fix reference.
