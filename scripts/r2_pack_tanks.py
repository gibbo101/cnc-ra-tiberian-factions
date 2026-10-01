#!/usr/bin/env python3
"""Package the Red Alert 2 easter-egg tanks: the Apocalypse (R2APOC) and the Prism Tank (R2PRIS).

Both follow the TS voxel units: hull 0-31 + turret 32-63 (the TSSONIC layout), rendered on
the house camera and lighting, each render scaled around the voxel origin at the canvas centre
(ts_pack_4tnk.py's recipe) by the TS voxel density 6.4/12 times RA2's 48/60 cell ratio. The hull frames carry the
baked EA-convention shadow (ts_reshadow.py's drop_shadow); turret frames carry none.

Renders (the voxel ledger in docs/launcher-render-contracts.md), RA2 VXLs from ra2.mix ->
local.mix via tools/ts_extract.py:
  vxl_render.py MTNK.VXL    r2apoc     --frames 32 --yaw0 90 --px-per-voxel 12
      --team-green 0,200,0 --elev 32 --canvas 1200 --hva MTNK.HVA
  vxl_render.py MTNKTUR.VXL r2apoctur  (same) --hva MTNKTUR.HVA
      --attach MTNKBARL.VXL --attach-hva MTNKBARL.HVA
  vxl_render.py SREF.VXL    r2pris     (same) --hva SREF.HVA
  vxl_render.py SREFTUR.VXL r2pristur  (same) --hva SREFTUR.HVA
RA2's VXLs embed unittem.pal (the used indices match it within 2.3/255), so the renders need
no palette override; the TS shading model lifts RA2's dark mastering on its own.

Cameos: RA2's own MTNKICON / SREFICON (language.mix -> cameo.mix), decoded with the real
cameo.pal and flattened opaque (the launcher draws noise under transparent cameo pixels).

Audio: Yuri's Revenge's unit sets (langmd.mix -> audiomd.mix -> audio.bag/idx, decoded to PCM
by tools/ra2_bag_extract.py), re-encoded MS-ADPCM 22050 mono under their own R2 names. Their
sound events are hand-written in the RA2 packs' SFXEVENTSNONLOCALIZED_RA2.XML.

Art ZIPs, tiles, cameos and WAVs land where scripts/asset_packs.py routes each name (the RA2
packs); the build merges the packs into the mod.

Also writes redalert/r2tanks_muzzle.h: RA2's FLHs projected through the render camera per
turret frame, so shells, missiles and the prism beam leave the art's barrel tips.

Inputs (set R2_ART_DIR): renders/<dir>/frame-NNNN.png, raw/<sample>.wav,
ra2/{mtnkicon.shp, sreficon.shp, cameo.pal}.

License: GPL v3.
"""
import io, json, math, os, subprocess, sys, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_shp
from ts_reshadow import drop_shadow, EA_DX, EA_DY
import asset_packs

ART = os.environ.get("R2_ART_DIR")
MUZZLE_H = os.path.join(HERE, "..", "redalert", "r2tanks_muzzle.h")

# The TS voxel density 6.4/12, times RA2's cell ratio: RA2 draws voxels at TS's size onto a
# 60 px cell where TS's is 48, so its units read 0.8 as large beside a cell as TS's do.
F_VOX = 6.4 / 12 * 48 / 60
ELEV = math.radians(32)       # the renders' --elev
PX_PER_VOXEL = 12 * F_VOX     # rendered at 12 px per voxel, packed at F_VOX
LEPTONS_PER_PX = 4 / 3        # unit art: 192 canvas px to the 256-lepton cell

# name, canvas (ShapeSize x 8), hull renders, turret renders, cameo SHP
UNITS = (
    ("R2APOC", 448, "r2apoc", "r2apoctur", "mtnkicon.shp"),
    ("R2PRIS", 384, "r2pris", "r2pristur", "sreficon.shp"),
)

# RA2 fire points in leptons (forward, left, height). The Apocalypse's cannon is art.ini
# [MTNK] PrimaryFireFLH, mirrored for the second barrel; RA2 gives its tusks no FLH, so they
# leave the turret's side pods. The Prism's is [SREF] Weapon1FLH.
APOC_FLH = ((190, 25, 120), (-20, 70, 130))
PRIS_FLH = (48, 0, 184)

# Yuri's Revenge sample -> shipped stem. Each ships as <stem>.WAV.
SAMPLES = (
    "vaposea", "vaposeb", "vaposec", "vaposed", "vaposee",
    "vapomoa", "vapomob", "vapomoc", "vapomod", "vapomoe",
    "vapoata", "vapoatb", "vapoatc", "vapoatd", "vapoate", "vapoatf",
    "vapostaa", "vapostab", "vapostac", "vapoat1a", "vapoat2a", "vapoat2b", "vapoat2c",
    "vprisea", "vpriseb", "vprisec", "vprised", "vprisee",
    "vprimoa", "vprimob", "vprimoc", "vprimod", "vprimoe",
    "vpriata", "vpriatb", "vpriatc", "vpriatd", "vpriate",
    "vpristaa", "vpristab", "vpristac", "vpriatta",
)


def stem(sample):
    return "R2" + sample.upper()


def vox_frames(dirname, canvas, shadow):
    out = []
    for i in range(32):
        im = Image.open(f"{ART}/renders/{dirname}/frame-{i:04d}.png").convert("RGBA")
        scaled = im.resize((round(im.width * F_VOX), round(im.height * F_VOX)), Image.LANCZOS)
        fr = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
        ox, oy = round(canvas / 2 - scaled.width / 2), round(canvas / 2 - scaled.height / 2)
        b = scaled.getbbox()
        if b and (ox + b[0] < 0 or oy + b[1] < 0 or ox + b[2] > canvas or oy + b[3] > canvas - EA_DY):
            raise SystemExit(f"{dirname} frame {i}: content clipped -- grow the canvas")
        # A render larger than the pack canvas lands at a negative offset: crop the source
        # rather than clamp the destination, or the whole frame shifts off-centre.
        fr.alpha_composite(scaled, (max(ox, 0), max(oy, 0)), (max(-ox, 0), max(-oy, 0)))
        out.append(drop_shadow(fr, EA_DX, EA_DY) if shadow else fr)
    return out


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


def patch_tileset(name, count):
    import re
    sub = name.lower()
    units_xml = asset_packs.tileset_xml(name, "UNITS")
    xml = open(units_xml, encoding="utf-8").read()
    xml = re.sub(r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?", "", xml, flags=re.S)
    block = ('\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n'
             '\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n')
    blocks = "".join(block % (name, i, f"{sub}\\{sub}-{i:04d}.tga") for i in range(count))
    idx = xml.rindex("</Tiles>")
    open(units_xml, "w", encoding="utf-8").write(xml[:idx] + blocks + xml[idx:])
    print(f"patched {os.path.basename(units_xml)}: {name} -> {count} tiles")


def write_cameo(name, shp):
    cpal = ts_shp.load_pal(f"{ART}/ra2/cameo.pal")
    _, shp_frames = ts_shp.decode_shp(f"{ART}/ra2/{shp}")
    icon = ts_shp.frame_to_rgba(shp_frames[0], cpal, None, None)
    flat = Image.new("RGBA", icon.size, (0, 0, 0, 255))
    flat.alpha_composite(icon)
    big = flat.resize((flat.width * 8, flat.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    path = asset_packs.cameo_tga(f"BuildIcon_{name}")
    big.save(path)
    print(f"wrote {path}")


def write_audio():
    dirs = set()
    for s in SAMPLES:
        out_wav = asset_packs.sound_wav(stem(s))
        os.makedirs(os.path.dirname(out_wav), exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{ART}/raw/{s}.wav",
                        "-c:a", "adpcm_ms", "-ar", "22050", "-ac", "1", out_wav], check=True)
        dirs.add(os.path.dirname(out_wav))
    print(f"wrote {len(SAMPLES)} samples to {', '.join(sorted(dirs))}")


def project(fwd, lat, hgt):
    """Per-turret-frame (east, south) leptons from the unit centre, for frame f rendered at
    yaw 90 + 11.25 f like the art."""
    rows = []
    f_v, l_v, h_v = fwd / 8.0, lat / 8.0, hgt / 8.0    # leptons to voxels
    for f in range(32):
        yaw = math.radians(90 + f * 11.25)
        rx = f_v * math.cos(yaw) - l_v * math.sin(yaw)
        ry = f_v * math.sin(yaw) + l_v * math.cos(yaw)
        x = rx * PX_PER_VOXEL
        y = -(ry * math.sin(ELEV) + h_v * math.cos(ELEV)) * PX_PER_VOXEL
        rows.append((round(x * LEPTONS_PER_PX), round(y * LEPTONS_PER_PX)))
    return rows


def rows_c(rows):
    return "{" + ", ".join(f"{{{x}, {y}}}" for x, y in rows) + "}"


def write_muzzle_header():
    hdr = "// GENERATED by scripts/r2_pack_tanks.py -- do not hand-edit.\n"
    hdr += "// RA2 tank fire points, leptons east/south of the unit centre, per turret frame.\n"
    hdr += "// Apocalypse: [weapon: cannon, tusks][side: left, right][turret frame][x, y].\n"
    hdr += "static const short _r2apoc_muzzle[2][2][32][2] = {\n"
    for fwd, lat, hgt in APOC_FLH:
        hdr += "    {\n"
        for sign in (1, -1):
            hdr += "        " + rows_c(project(fwd, sign * lat, hgt)) + ",\n"
        hdr += "    },\n"
    hdr += "};\n"
    hdr += "// Prism Tank: [turret frame][x, y].\n"
    hdr += "static const short _r2pris_muzzle[32][2] = " + rows_c(project(*PRIS_FLH)) + ";\n"
    with open(MUZZLE_H, "w") as fh:
        fh.write(hdr)
    print(f"wrote {os.path.normpath(MUZZLE_H)}")


def main():
    if not ART:
        raise SystemExit("set R2_ART_DIR (holding renders/, raw/, ra2/)")
    for name, canvas, hull, turret, cameo in UNITS:
        frames = vox_frames(hull, canvas, True) + vox_frames(turret, canvas, False)
        write_zip(asset_packs.art_zip(name, "UNITS"), name.lower(), frames)
        patch_tileset(name, len(frames))
        write_cameo(name, cameo)
    write_audio()
    write_muzzle_header()


if __name__ == "__main__":
    if sys.argv[1:] == ["muzzle"]:
        write_muzzle_header()
    else:
        main()
