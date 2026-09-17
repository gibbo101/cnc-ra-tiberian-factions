#!/usr/bin/env python3
"""TS Hunter Seeker droid art + cameo + sound (the Seeker Control plug's special).

Reads the raw TS members extracted by ts_rebuild_art.sh ($TS_ART_DIR/.raw, or
$TS_RAW_DIR):
- GGHUNT.SHP  (CONQUER.MIX, UNITTEM.PAL, house remap 16-31): frames 0-7 are the
  droid's single-facing 8-frame spin, 8-15 its shadow. Only the body ships --
  the engine draws an aircraft's shadow itself. Scaled x4 (hq4x, the TS cell
  48 -> HD cell 192 contract) onto a 192 canvas = classic stub 24x24 (canvas
  / 8, the units coupling), 8 frames, AircraftClass::Shape_Number cycles them.
- DETNICON.SHP (CAMEO.PAL): [HuntSeekSpecial] SidebarImage= -> BuildIcon_SW_TSHUNT
  + the TS-tree badged BuildIcon_SG_TSHUNT (tsgdi emblem, cameo_badge_build layout).
- HUNTER2.AUD (SOUNDS.MIX): the SuicideBomb report -> TSHUNTR2.WAV, MS-ADPCM,
  under its own name.
"""
import io, json, os, re, subprocess, sys, zipfile
from PIL import Image
import hqx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_shp

ART = os.environ.get("TS_ART_DIR")
RAW = os.environ.get("TS_RAW_DIR") or (f"{ART}/.raw" if ART else None)
if not RAW:
    raise SystemExit("set TS_ART_DIR (holding .raw/) or TS_RAW_DIR")
MOD = os.path.abspath(os.path.join(HERE, "..", "resources", "remaster_mods", "Vanilla_RA", "Data"))
UNITS_DIR = f"{MOD}/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
ICON_DIR = f"{MOD}/ART/TEXTURES/SRGB"
XML = f"{MOD}/XML/TILESETS/RA_UNITS.XML"
EMBLEM = os.path.join(HERE, "tab_emblems", "tsgdi.png")
CANVAS = 384
SCALE = 4
BIG_MULT = 1  # native TS size, same as every other TS unit pack (3x was a bullet-era hack; as an aircraft it drew 3x too big)


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def write_zip(path, name, frames):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            W, H = img.width, img.height
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0 = min(bb[0], W - bb[2])
            y0 = min(bb[1], H - bb[3])
            b = (x0, y0, W - x0, H - y0)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps({"size": [W, H], "crop": list(b)}))
    print(f"wrote {path} ({len(frames)} frames)")


def patch_tileset(xml_path, name, count):
    sub = name.lower()
    xml = open(xml_path, encoding="utf-8").read()
    xml = re.sub(r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?", "", xml, flags=re.S)
    block = ('\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n'
             '\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n')
    blocks = "".join(block % (name, i, f"{sub}\\{sub}-{i:04d}.tga") for i in range(count))
    idx = xml.rindex("</Tiles>")
    open(xml_path, "w", encoding="utf-8").write(xml[:idx] + blocks + xml[idx:])
    print(f"patched {os.path.basename(xml_path)}: {name} -> {count} tiles")


def decode(shp, pal, remap=None, team=None):
    (W, H), raw = ts_shp.decode_shp(f"{RAW}/{shp}")
    return [ts_shp.frame_to_rgba(f, pal, remap=remap, team=team) for f in raw]


def main():
    unit_pal = ts_shp.load_pal(f"{RAW}/UNITTEM.PAL")
    body = decode("GGHUNT.SHP", unit_pal, remap=(16, 31), team=(165, 170, 185))[:8]  # steel, not the green house placeholder (bullets are not house-tinted)
    # One crop box for the whole spin so the droid never jitters between frames.
    boxes = [f.getbbox() for f in body]
    box = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
    frames = []
    for f in body:
        seg = f.crop(box)
        rgb = seg.convert("RGB")
        big = hqx.hq4x(rgb).convert("RGBA")
        alpha = seg.split()[3].resize((seg.width * SCALE, seg.height * SCALE), Image.NEAREST)
        big.putalpha(alpha)
        if BIG_MULT != 1:
            big = big.resize((big.width * BIG_MULT, big.height * BIG_MULT), Image.LANCZOS)
        canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        canvas.alpha_composite(big, ((CANVAS - big.width) // 2, (CANVAS - big.height) // 2))
        frames.append(canvas)
    write_zip(f"{UNITS_DIR}/TSHUNT.ZIP", "tshunt", frames)
    patch_tileset(XML, "TSHUNT", len(frames))

    cameo_pal = ts_shp.load_pal(f"{RAW}/CAMEO.PAL")
    icon = decode("DETNICON.SHP", cameo_pal)[0]
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(f"{ICON_DIR}/BuildIcon_SW_TSHUNT.tga")
    print(f"wrote {ICON_DIR}/BuildIcon_SW_TSHUNT.tga")
    # TS-tree badge (the 'G' digit key): cameo_badge_build's emblem layout.
    badged = big.convert("RGBA")
    emblem = Image.open(EMBLEM).convert("RGBA").resize((90, 90), Image.LANCZOS)
    badged.alpha_composite(emblem, (12, 12))
    badged.save(f"{ICON_DIR}/BuildIcon_SG_TSHUNT.tga")
    print(f"wrote {ICON_DIR}/BuildIcon_SG_TSHUNT.tga")

    out_wav = f"{MOD}/AUDIO/TSHUNTR2.WAV"
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
