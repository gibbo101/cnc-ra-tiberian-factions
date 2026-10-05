#!/usr/bin/env python3
"""Package the TS Ion Cannon strike anims (TSIONBM.ZIP + TSIONRNG.ZIP) and the
strike's cameo/audio companions.

TS fires its ion cannon as two anims at the impact cell (OpenTS ionblast.cpp):
IonBeam=IONBEAM (a 29x120 vertical beam SEGMENT the TS engine tiles to sky
height, art.ini Tiled=yes) and IonBlast=RING1 (a flat expanding ground ring).
The launcher cannot tile an anim, so the beam ships PRE-TILED: the segment
stacked vertically (it wrap-tiles cleanly, that is what Tiled=yes means).

Decoded against ANIM.PAL with NO team remap, scaled x4 (TS cell 48 px -> RA
cell 192 canvas px, the TSDIG contract), canvas = classic stub x 8
(build_tfassets.sh: TSIONBM 15x480, TSIONRNG 104x51).

Also emits:
- BuildIcon_SW_TSION.tga — the TS satellite cameo (IONCICON, CAMEO.PAL) for
  the specials column when the uplink is the grantor (AssetName "SW_TSIon"), in the
  mod's own tree.
- AUDIO/TSION1.WAV — TS's ION1 strike sound under its OWN sample name
  (ffmpeg: Westwood AUD -> MS-ADPCM WAV, the proven novel-name format rules).
Anims, their TS_VFX.XML tile runs and the sound go to the tree asset_packs.py routes each
name to (the TS packs).

Inputs (set TS_ART_DIR): $TS_ART_DIR/.raw/{IONBEAM.SHP,RING1.SHP,ANIM.PAL,
CAMEO.PAL,ION1.AUD} — extracted by scripts/ts_rebuild_art.sh.

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
import asset_packs

RAW = f"{ART}/.raw"
SCALE = 4.0
# 8 x 480 = 3840 canvas px. The TD beam's art is 2038px but renders at VirtualScale 0x200 (adata.cpp) = ~4076
# virtual px; ours draws at 0x100 to keep the narrow TS column width, so the height must be tiled in at pack time
# (the TD beam enters from the top of the screen; the TS one must too).
BEAM_SEGMENTS = 8


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


def decode(shp, pal, remap=None):
    (W, H), raw = ts_shp.decode_shp(f"{RAW}/{shp}")
    return [(W, H, ts_shp.frame_to_rgba(f, pal, remap=remap)) for f in raw]


def main():
    anim_pal = ts_shp.load_pal(f"{RAW}/ANIM.PAL")

    # Beam: each frame's 29x120 segment stacked BEAM_SEGMENTS high, x4.
    beam = []
    for W, H, im in decode("IONBEAM.SHP", anim_pal):
        seg = im.resize((round(W * SCALE), round(H * SCALE)), Image.LANCZOS)
        canvas = Image.new("RGBA", (120, seg.height * BEAM_SEGMENTS), (0, 0, 0, 0))
        x = round(canvas.width / 2 - seg.width / 2)
        for s in range(BEAM_SEGMENTS):
            canvas.alpha_composite(seg, (x, canvas.height - (s + 1) * seg.height))
        beam.append(canvas)
    write_zip(asset_packs.art_zip("TSIONBM", "VFX"), "tsionbm", beam)
    patch_tileset(asset_packs.tileset_xml("TSIONBM", "VFX"), "TSIONBM", len(beam))

    # Ring: centred, x4.
    ring = []
    for W, H, im in decode("RING1.SHP", anim_pal):
        scaled = im.resize((round(W * SCALE), round(H * SCALE)), Image.LANCZOS)
        canvas = Image.new("RGBA", (832, 408), (0, 0, 0, 0))
        canvas.alpha_composite(scaled, (round(canvas.width / 2 - scaled.width / 2),
                                        round(canvas.height / 2 - scaled.height / 2)))
        ring.append(canvas)
    write_zip(asset_packs.art_zip("TSIONRNG", "VFX"), "tsionrng", ring)
    patch_tileset(asset_packs.tileset_xml("TSIONRNG", "VFX"), "TSIONRNG", len(ring))

    # The TS satellite cameo for the uplink-granted special.
    cameo_pal = ts_shp.load_pal(f"{RAW}/CAMEO.PAL")
    _, _, icon = decode("IONCICON.SHP", cameo_pal)[0]
    big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    big.save(asset_packs.cameo_tga("BuildIcon_SW_TSION"))
    print(f"wrote {asset_packs.cameo_tga('BuildIcon_SW_TSION')}")

    # TS ION1 strike sound under its own sample name (novel-name path).
    out_wav = asset_packs.sound_wav("TSION1.WAV")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{RAW}/ION1.AUD",
                    "-acodec", "adpcm_ms", out_wav], check=True)
    print(f"wrote {out_wav}")


if __name__ == "__main__":
    main()
