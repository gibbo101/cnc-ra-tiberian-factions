#!/usr/bin/env python3
"""TS Hunter Seeker cameo + sound (the Seeker Control plug's special). The droid's art (TSHUNT: its
single-facing 8-frame spin on a 384 canvas, no shadow, as the engine draws an aircraft's shadow
itself) is the HD rebuild's, packed by scripts/ts_pack_hd_buildings.py.

Reads the raw TS members extracted by ts_rebuild_art.sh ($TS_ART_DIR/.raw, or
$TS_RAW_DIR):
- DETNICON.SHP (CAMEO.PAL): [HuntSeekSpecial] SidebarImage= -> BuildIcon_SW_TSHUNT
  + the TS-tree badged BuildIcon_SG_TSHUNT (tsgdi emblem, cameo_badge_build layout).
- HUNTER2.AUD (SOUNDS.MIX): the SuicideBomb report -> TSHUNTR2.WAV, MS-ADPCM,
  under its own name.
Also records the droid's classic stub (canvas / 8, the units coupling) in ts_stub_dims.json.
Each file goes to the tree asset_packs.py routes its name to: the sound to the TS-SFX-Pack, the
SW_/SG_ superweapon cameos to the mod's own tree.
"""
import json, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_packs
import ts_shp

ART = os.environ.get("TS_ART_DIR")
RAW = os.environ.get("TS_RAW_DIR") or (f"{ART}/.raw" if ART else None)
if not RAW:
    raise SystemExit("set TS_ART_DIR (holding .raw/) or TS_RAW_DIR")
EMBLEM = os.path.join(HERE, "tab_emblems", "tsgdi.png")
CANVAS = 384


def decode(shp, pal, remap=None, team=None):
    (W, H), raw = ts_shp.decode_shp(f"{RAW}/{shp}")
    return [ts_shp.frame_to_rgba(f, pal, remap=remap, team=team) for f in raw]


def main():
    cameo_pal = ts_shp.load_pal(f"{RAW}/CAMEO.PAL")
    icon = decode("DETNICON.SHP", cameo_pal)[0]
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(asset_packs.cameo_tga("BuildIcon_SW_TSHUNT"))
    print(f"wrote {asset_packs.cameo_tga('BuildIcon_SW_TSHUNT')}")
    # TS-tree badge (the 'G' digit key): cameo_badge_build's emblem layout.
    badged = big.convert("RGBA")
    emblem = Image.open(EMBLEM).convert("RGBA").resize((90, 90), Image.LANCZOS)
    badged.alpha_composite(emblem, (12, 12))
    badged.save(asset_packs.cameo_tga("BuildIcon_SG_TSHUNT"))
    print(f"wrote {asset_packs.cameo_tga('BuildIcon_SG_TSHUNT')}")

    out_wav = asset_packs.sound_wav("TSHUNTR2")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{RAW}/HUNTER2.AUD",
                    "-acodec", "adpcm_ms", out_wav], check=True)
    print(f"wrote {out_wav}")

    stub_manifest = os.path.join(HERE, "ts_stub_dims.json")
    dims = json.load(open(stub_manifest))
    dims["TSHUNT"] = [CANVAS // 8, CANVAS // 8]  # 48x48 now
    with open(stub_manifest, "w") as f:
        json.dump(dims, f, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
