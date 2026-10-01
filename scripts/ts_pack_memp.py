#!/usr/bin/env python3
"""Package the TS Mobile EM-Pulse (Firestorm [MOBILEMP]) as TSMEMP.

  TSMEMP.ZIP (units)      32 frames: the M_EMP.VXL hull, one per facing, on a 384 canvas
                          (ShapeSize 48), each render scaled by the TS voxel density 6.4/12
                          around the voxel origin at the canvas centre (the vox_frames recipe
                          in ts_pack_units_wave.py / ts_pack_4tnk.py).
  TSMEMPFX.ZIP (vfx)      12 frames: MEMPFX, the vehicle's pulse blast, at TS scale x4 on a
                          1152x576 canvas (classic stub 144x72), decoded against ANIM.PAL.
  BuildIcon_TS_MobileEMP.tga, the base RA_TSMEMP sidebar entry (in TSBUILDABLES.XML, next to
  RA_TSAPC) and the ModText rows. Art, cameo and XML go to the tree asset_packs.py routes each
  name to (the TS-Graphics-Pack).

Render (the voxel ledger in docs/launcher-render-contracts.md):
  vxl_render.py M_EMP.VXL renders_memp --frames 32 --yaw0 90 --px-per-voxel 12
      --team-green 0,200,0 --elev 32 --hva M_EMP.HVA --canvas 720
Follow with scripts/ts_reshadow.py TSMEMP, then the cameo badge and variant scripts.

Inputs (set TS_ART_DIR): $TS_ART_DIR/renders_memp, $TS_ART_DIR/.raw/{MEMPFX,MEMPICON}.SHP,
ANIM.PAL, CAMEO.PAL. M_EMP.VXL/HVA sit at the top of the TS install's expand01.mix, MEMPFX
and MEMPICON in its ECACHE01.MIX (tools/ts_extract.py).

License: GPL v3.
"""
import os
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_shp
import asset_packs
from ts_pack_pods import ART, RAW, write_zip, patch_tileset

CSV = f"{asset_packs.MOD}/Data/ModText.csv"
CANVAS = 384
F_VOX = 6.4 / 12
FX_SCALE = 4.0
FX_CANVAS = (1152, 576)
TEXT = (
    ("TEXT_UNIT_TSMEMP", "Mobile EMP"),
    ("TEXT_UNIT_TSMEMP_DESC", "Unarmed support vehicle. Charges up, then deploys to disable nearby "
                              "vehicles and buildings for a few seconds, friend and foe alike."),
)


def vox_frames(dirname):
    out = []
    for i in range(32):
        im = Image.open(f"{ART}/{dirname}/frame-{i:04d}.png").convert("RGBA")
        scaled = im.resize((round(im.width * F_VOX), round(im.height * F_VOX)), Image.LANCZOS)
        fr = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        ox, oy = round(CANVAS / 2 - scaled.width / 2), round(CANVAS / 2 - scaled.height / 2)
        b = scaled.getbbox()
        if b and (ox + b[0] < 0 or oy + b[1] < 0 or ox + b[2] > CANVAS or oy + b[3] > CANVAS):
            raise SystemExit(f"{dirname} frame {i}: content clipped -- grow the canvas")
        # A render larger than the canvas lands at a negative offset: crop it so the voxel
        # origin still falls on the canvas centre.
        src = scaled.crop((max(-ox, 0), max(-oy, 0), scaled.width, scaled.height))
        fr.alpha_composite(src, (max(ox, 0), max(oy, 0)))
        out.append(fr)
    return out


def blast_frames():
    pal = ts_shp.load_pal(f"{RAW}/ANIM.PAL")
    (W, H), raw = ts_shp.decode_shp(f"{RAW}/MEMPFX.SHP")
    cw, ch = FX_CANVAS
    out = []
    for f in raw:
        im = ts_shp.frame_to_rgba(f, pal, remap=None)
        scaled = im.resize((round(W * FX_SCALE), round(H * FX_SCALE)), Image.LANCZOS)
        fr = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ox, oy = round(cw / 2 - scaled.width / 2), round(ch / 2 - scaled.height / 2)
        if ox < 0 or oy < 0:
            raise SystemExit(f"MEMPFX: {scaled.size} does not fit the {cw}x{ch} canvas")
        fr.alpha_composite(scaled, (ox, oy))
        out.append(fr)
    return out


def cameo():
    pal = ts_shp.load_pal(f"{RAW}/CAMEO.PAL")
    (_, _), raw = ts_shp.decode_shp(f"{RAW}/MEMPICON.SHP")
    icon = ts_shp.frame_to_rgba(raw[0], pal, remap=None)
    flat = Image.new("RGBA", icon.size, (0, 0, 0, 255))
    flat.alpha_composite(icon)
    big = flat.resize((flat.width * 8, flat.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    path = asset_packs.cameo_tga("BuildIcon_TS_MobileEMP")
    big.save(path)
    print(f"wrote {path}")


def sidebar_entry():
    rab = asset_packs.buildables_xml("BuildIcon_TS_MobileEMP")
    xml = open(rab, encoding="utf-8").read()
    if 'Name="RA_TSMEMP"' in xml:
        return
    anchor = '\t<ObjectTypeClass Name="RA_TSAPC" '
    start = xml.index(anchor)
    end = xml.index("</ObjectTypeClass>\n", start) + len("</ObjectTypeClass>\n")
    entry = ('\t<ObjectTypeClass Name="RA_TSMEMP" Classification="CNCBuildableObject" CanInstantiate="False">\n'
             "\t\t<CNCEncyclopediaComponent>\n"
             "\t\t\t<ObjectNameTextID>TEXT_UNIT_TSMEMP</ObjectNameTextID>\n"
             "\t\t\t<ObjectDescriptionTextID>TEXT_UNIT_TSMEMP_DESC</ObjectDescriptionTextID>\n"
             "\t\t\t<BuildIcon>BuildIcon_TS_MobileEMP</BuildIcon>\n"
             "\t\t</CNCEncyclopediaComponent>\n"
             "\t</ObjectTypeClass>\n")
    open(rab, "w", encoding="utf-8").write(xml[:end] + entry + xml[end:])
    print(f"added RA_TSMEMP to {os.path.basename(rab)}")


def text_rows():
    text = open(CSV, "rb").read().decode("utf-16")
    eol = "\r\n" if "\r\n" in text else "\n"
    sample = next(l for l in text.splitlines() if l.startswith('"TEXT_UNIT_TSAPC"'))
    tail = sample.split('"Amphibious APC"', 1)[1]
    new = ""
    for key, val in TEXT:
        if f'"{key}"' not in text:
            new += f'"{key}",,,"{val}"{tail}{eol}'
    if new:
        if not text.endswith(eol):
            text += eol
        open(CSV, "wb").write((text + new).encode("utf-16"))
        print(f"added {len(TEXT)} ModText rows")


def main():
    frames = vox_frames("renders_memp")
    write_zip(asset_packs.art_zip("TSMEMP", "UNITS"), "tsmemp", frames)
    patch_tileset(asset_packs.tileset_xml("TSMEMP", "UNITS"), "TSMEMP", len(frames))
    fx = blast_frames()
    write_zip(asset_packs.art_zip("TSMEMPFX", "VFX"), "tsmempfx", fx)
    patch_tileset(asset_packs.tileset_xml("TSMEMPFX", "VFX"), "TSMEMPFX", len(fx))
    cameo()
    sidebar_entry()
    text_rows()


if __name__ == "__main__":
    main()
