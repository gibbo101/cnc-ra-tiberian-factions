#!/usr/bin/env python3
"""Package the TS Drop Pod strike art (anims + bullet sprite + cameo + sound).

TS drops infantry in pods that streak in at DropPodAngle (0.79 rad), trailing
SMOKEY puffs and strafing the LZ with DropPodWeapon, then leave a DROPPOD /
DROPPOD2 husk mark with a DROPEXP puff on touchdown; PODRING flashes at
atmosphere entry (TS RULES.INI [General] DropPod* keys; OpenTS droppod.cpp).
The engine port drives the descent as BULLET_TSPODDROP, so the pod body ships
as a one-frame bullet sprite (TSPODBLT) and every effect as its own anim.

Decoded against ANIM.PAL with NO team remap, scaled x4 (TS cell 48 px -> RA
cell 192 canvas px, the TSDIG contract), canvas = classic stub x 8
(build_tfassets.sh: TSDPOD1/TSDPOD2/TSPODBLT 24x24, TSDRPEXP 50x34,
TSPODRNG 50x26, TSSMOKEY 16x15).

Also emits:
- BuildIcon_SW_TSPODS.tga — TS's PODSICON (CAMEO.PAL) for the specials column
  (AssetName "SW_TSPods").
- Data/AUDIO/TSGUN4.WAV — the Vulcan2 strafe report under its OWN sample name
  (ffmpeg: Westwood AUD -> MS-ADPCM WAV, the proven novel-name format rules).

Inputs (set TS_ART_DIR): $TS_ART_DIR/.raw/{DROPPOD.SHP,DROPPOD2.SHP,
DROPEXP.SHP,PODRING.SHP,SMOKEY.SHP,ANIM.PAL,CAMEO.PAL,TSGUN4.AUD} —
extracted by scripts/ts_rebuild_art.sh.

License: GPL v3.
"""
import io, json, os, re, subprocess, sys, zipfile
from PIL import Image

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR (holding .raw/ from ts_rebuild_art.sh)")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_shp

MOD = os.path.abspath(os.path.join(HERE, "..", "resources", "remaster_mods", "Vanilla_RA", "Data"))
VFX_DIR = f"{MOD}/ART/TEXTURES/SRGB/RED_ALERT/VFX"
ICON_DIR = f"{MOD}/ART/TEXTURES/SRGB"
XML = f"{MOD}/XML/TILESETS/RA_VFX.XML"
RAW = f"{ART}/.raw"
SCALE = 4.0


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
    print(f"patched RA_VFX.XML: {name} -> {count} tiles")


def decode(shp, pal, remap=None):
    (W, H), raw = ts_shp.decode_shp(f"{RAW}/{shp}")
    return [(W, H, ts_shp.frame_to_rgba(f, pal, remap=remap)) for f in raw]


def pack_anim(shp, name, canvas_w, canvas_h, pal, frames=None):
    out = []
    for idx, (W, H, im) in enumerate(decode(shp, pal)):
        if frames is not None and idx not in frames:
            continue
        seg = im.resize((round(W * SCALE), round(H * SCALE)), Image.LANCZOS)
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        canvas.alpha_composite(seg, (round(canvas_w / 2 - seg.width / 2),
                                     round(canvas_h / 2 - seg.height / 2)))
        out.append(canvas)
    write_zip(f"{VFX_DIR}/{name}.ZIP", name.lower(), out)
    patch_tileset(XML, name, len(out))
    return len(out)


def main():
    anim_pal = ts_shp.load_pal(f"{RAW}/ANIM.PAL")

    # Husk marks (the pod after it lands) + touchdown puff + entry ring + trail.
    pack_anim("DROPPOD.SHP", "TSDPOD1", 192, 192, anim_pal)
    pack_anim("DROPPOD2.SHP", "TSDPOD2", 192, 192, anim_pal)
    pack_anim("DROPEXP.SHP", "TSDRPEXP", 400, 272, anim_pal)
    pack_anim("PODRING.SHP", "TSPODRNG", 400, 208, anim_pal)
    pack_anim("SMOKEY.SHP", "TSSMOKEY", 128, 120, anim_pal)

    # The falling pod body: one frame (the hot pod) for BULLET_TSPODDROP.
    pack_anim("DROPPOD.SHP", "TSPODBLT", 192, 192, anim_pal, frames={0})

    # The TS drop-pods cameo for the plug-granted special.
    cameo_pal = ts_shp.load_pal(f"{RAW}/CAMEO.PAL")
    _, _, icon = decode("PODSICON.SHP", cameo_pal)[0]
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(f"{ICON_DIR}/BuildIcon_SW_TSPODS.tga")
    print(f"wrote {ICON_DIR}/BuildIcon_SW_TSPODS.tga")

    # The Vulcan2 strafe report under its own sample name (novel-name path).
    out_wav = f"{MOD}/AUDIO/TSGUN4.WAV"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{RAW}/TSGUN4.AUD",
                    "-acodec", "adpcm_ms", out_wav], check=True)
    print(f"wrote {out_wav}")


if __name__ == "__main__":
    main()
