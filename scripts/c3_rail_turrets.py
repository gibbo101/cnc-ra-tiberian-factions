#!/usr/bin/env python3
"""The C&C3 tanks with their railgun upgrade, for the C&C3 pack: C3MK3RAIL and C3PREDRAIL.

C&C3's railgun upgrade shows the UGRAIL meshes and hides nothing: a sleeve round each barrel, a cable over the
turret and a forked tip past the muzzle, on the Mammoth's texture sheet for both tanks. Each RAIL unit is its tank's
shipped tileset (C3MK3, C3PRED: hull 0-95, turret 96-127, scripts/c3_pack_tanks.py) with the 32 turret frames
re-rendered with the rails and a baked glow on their blue conduit (scripts/c3_render.py --rails --glow). Only the
pack carries them: Tiberian Factions has no unit that draws them (asset_packs.PACK_ONLY).

  extract <stream dir>   adds the UGRAIL meshes to model/<model>.npz as model/<model>_rail.npz
  render                 renders the 32 rail turret facings to renders/<model>_rail/
  pack                   writes the RAIL ZIPs and their tiles where scripts/asset_packs.py routes the names

Inputs (set C3_ART_DIR): model/<model>.npz from tools/cnc3/c3_extract_model.py (workspace), and for extract the
C&C3 stream folder that tool reads.
License: GPL v3.
"""
import io
import json
import os
import subprocess
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_packs  # noqa: E402
import c3_pack_tanks as P  # noqa: E402
import c3_render  # noqa: E402

ART = os.environ.get("C3_ART_DIR")
GLOW = 1.0
FACINGS = 32
TURRET = 96  # first turret frame in the tank's tileset
# model -> (tank, rail unit, C&C3 skeleton, container, rail meshes)
TANKS = {
    "mammoth": ("C3MK3", "C3MK3RAIL", "GUMAMM_SKL", "GUMAMM_SKN", ["UGRAIL_01", "UGRAIL_02"]),
    "predator": ("C3PRED", "C3PREDRAIL", "GUPREDTANK_SKL", "GUPREDTANK_SKN", ["UGRAIL_01"]),
}
RAIL_TEXTURES = (("rail_body", "GUMamm"), ("rail_normal", "GUMamm_Nrm"))


def c3_tools():
    """tools/cnc3 in the workspace that holds this repo's main checkout."""
    common = subprocess.run(["git", "-C", HERE, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True, check=True).stdout.strip()
    return os.path.join(os.path.dirname(os.path.dirname(common)), "tools", "cnc3")


def extract(stream_dir):
    """Rails are bound to their own pivots by the container (no skinning): placed by pivot, part 1, material 2."""
    sys.path.insert(0, c3_tools())
    import c3_extract_model as X
    import w3dmesh
    st = X.Streams(stream_dir)
    model_dir = os.path.join(ART, "model")
    for model, (_, _, skl, cont, meshes) in TANKS.items():
        piv = X.parse_hierarchy(st.idata("W3DHierarchy:" + skl))
        bind = X.parse_container(st.idata("W3DContainer:" + cont))
        d = dict(np.load(os.path.join(model_dir, model + ".npz")))
        origin = piv[1]["wt"] - d["pivot_pos"][1]
        vbase = len(d["pos"])
        add = {k: [] for k in ("pos", "nrm", "tan", "bin", "uv", "tris", "part", "mat")}
        for mesh in meshes:
            m = w3dmesh.decode(st.idata(f"W3DMesh:{cont}.{mesh}"))
            f, vc = m["fields"], m["vcount"]
            p = piv[bind[mesh]]
            def turn(a):
                return np.array([X.qrot(p["wq"], v) for v in np.asarray(a, float)])
            add["pos"].append(p["wt"] + turn(f["POSITION"]) - origin)
            add["nrm"].append(turn(f["NORMAL"]))
            add["tan"].append(turn(f["TANGENT"]))
            add["bin"].append(turn(f["BINORMAL"]))
            add["uv"].append(np.asarray(f["TEXCOORD"], float))
            add["tris"].append(np.asarray(m["tris"], np.int64) + vbase)
            add["part"].append(np.ones(vc, np.int64))
            add["mat"].append(np.full(vc, 2, np.int64))
            vbase += vc
        for k, v in add.items():
            d[k] = np.concatenate([d[k]] + v)
        tex = dict(d["textures"])
        for key, name in RAIL_TEXTURES:
            tex[key] = X.save_texture(st, name, model_dir)
        d["textures"] = np.array(list(tex.items()))
        np.savez_compressed(os.path.join(model_dir, model + "_rail.npz"), **d)
        print(f"wrote {model}_rail.npz ({', '.join(meshes)})")


def touches_edge(img):
    b = img.getbbox()
    return b is not None and (b[0] == 0 or b[1] == 0 or b[2] == img.width or b[3] == img.height)


def render_facing(args):
    """A facing on the shipped 1000 px canvas, or on 2000 px where the rail tip reaches the edge."""
    model, f = args
    m = c3_render.Model(os.path.join(ART, "model", model + "_rail.npz"))
    yaw = P.YAW0 + f * 360.0 / FACINGS
    img = c3_render.render(m, yaw, "turret", P.RENDER_PPU, 1000, 32.0, rails=True, glow=GLOW)
    if touches_edge(img):
        img = c3_render.render(m, yaw, "turret", P.RENDER_PPU, 2000, 32.0, rails=True, glow=GLOW)
    out = os.path.join(ART, "renders", model + "_rail")
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, f"frame-{f:04d}.png"))
    return model, f, img.width


def render():
    jobs = [(model, f) for model in TANKS for f in range(FACINGS)]
    with ProcessPoolExecutor() as ex:
        for model, f, size in ex.map(render_facing, jobs):
            print(f"{model} facing {f} ({size} px)", flush=True)


def packed_turret(path, canvas, drop):
    """A render packed as c3_pack_tanks.packed packs a turret, on the 1000 px render's pixel grid at any canvas
    size, then dropped as unit_centring.py drops the shipped frames."""
    im = Image.open(path).convert("RGBA")
    size = round(1000 * P.PACK_PPU / P.RENDER_PPU) * im.width // 1000
    scaled = im.resize((size, size), Image.LANCZOS)
    fr = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    ox, oy = round(canvas / 2 - size / 2), round(canvas / 2 - size / 2)
    fr.alpha_composite(scaled, (max(ox, 0), max(oy, 0)), (max(-ox, 0), max(-oy, 0)))
    out = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    out.paste(fr.crop((0, 0, canvas, canvas - drop)), (0, drop))
    return out


def shipped_frames(tank):
    """The tank's shipped frames as full canvases, in tileset order."""
    frames = []
    with zipfile.ZipFile(asset_packs.art_zip(tank, "UNITS")) as z:
        shapes = asset_packs.shape_frames(tank, "UNITS")
        for tga in (shapes[i] for i in sorted(shapes)):
            meta = json.loads(z.read(tga[:-4] + ".meta"))
            full = Image.new("RGBA", tuple(meta["size"]), (0, 0, 0, 0))
            full.paste(Image.open(io.BytesIO(z.read(tga))).convert("RGBA"), tuple(meta["crop"][:2]))
            frames.append(full)
    return frames


def pack():
    drops = json.load(open(os.path.join(HERE, "unit_art_drop.json")))
    for model, (tank, rail, *_) in TANKS.items():
        frames = shipped_frames(tank)
        canvas = frames[0].width
        for f in range(FACINGS):
            frames[TURRET + f] = packed_turret(os.path.join(ART, "renders", model + "_rail", f"frame-{f:04d}.png"),
                                               canvas, drops[tank])
        P.write_zip(asset_packs.art_zip(rail, "UNITS"), rail.lower(), frames)
        P.patch_tileset(rail, len(frames))


def main(argv):
    if not ART:
        raise SystemExit("set C3_ART_DIR (holding model/)")
    if argv[:1] == ["extract"] and len(argv) == 2:
        extract(argv[1])
    elif argv == ["render"]:
        render()
    elif argv == ["pack"]:
        pack()
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
