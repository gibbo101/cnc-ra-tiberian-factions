#!/usr/bin/env python3
"""Package C&C3 infantry, each as a single soldier and, where C&C3 fields a squad, as a squad at its size: from
Tiberium Wars, GDI's Rifleman (C3RIFLE, C3RIFLESQ), Missile Soldier (C3MISSL, C3MISSLSQ: two), Grenadier (C3GREN,
C3GRENSQ: four), Engineer (C3ENGI), Sniper (C3SNIPE), Zone Trooper (C3ZONE, C3ZONESQ: four) and Commando (C3GCMDO);
Nod's Rocket Militant (C3ROCKT, C3ROCKTSQ: two), Fanatic (C3FANAT, C3FANATSQ: five), Black Hand (C3BHAND,
C3BHANDSQ: six), Shadow (C3SHADW, C3SHADWSQ: four), Saboteur (C3SABOT) and Commando (C3NCMDO); from Kane's Wrath, Nod's Militant (C3MILIT, C3MILITSQ; Kane's Wrath's remade model) and Cyborg (C3CYBORG,
C3CYBORGSQ).

Tileset layout per unit (292 tiles): Tiberian Sun's light infantry (idata.cpp TsE1DoControls, TS art.ini
[E1Sequence]), 8 facings CCW from north where a sequence turns with the soldier:
  0-7 ready, 8-55 walk (6 a facing), 56-70 idle1, 71-84 idle2 (85 repeats its last), 86-133 crawl (6),
  134-148 die1, 149-163 die2, 164-211 fire (6), 212-259 fire prone (6), 260-275 down (2), 276-291 up (2).
Idles and deaths face south, toward the camera. Frames sit on the TS infantry's 267 x 208 canvas with the feet
on TSE1's line, scaled to TF's TS infantry height, each over its own shadow cast along the render light onto the
ground. Each soldier's team colour is raised to the TS infantry's (TEAM_BOOST), and his frames are exposed to their
brightness (TS_LUM_MEAN).

Inputs (set C3_ART_DIR): infantry/<unit>.npz and infantry/<unit>_squad.npz from tools/cnc3/c3_extract_infantry.py
(workspace), cameo/<NAME>.png for each single soldier, and audio/<model>/<C&C3 name>.wav from
tools/cnc3/c3_extract_audio.py. Audio: each soldier's crew voices and gunfire, as the tanks' (c3_pack_tanks.py).
Usage: c3_pack_infantry.py [NAME ...]; with no names, all of them. Renders cache in $C3_ART_DIR/renders/inf_<model>/,
keyed by pose and facing only: delete them after changing the render settings, the light or the posed model. Run
scripts/dedupe_tileset_frames.py afterwards, as for every packer: repeated poses become shared tiles.

License: GPL v3.
"""
import multiprocessing
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_packs  # noqa: E402
import c3_pack_tanks as tanks  # noqa: E402
import c3_render  # noqa: E402

ART = tanks.ART
RENDER_PPU = 12.0
# TF's TS infantry stand about 61 px tall, the C&C3 Rifleman 52 at 4 px a C&C3 unit (the tanks' scale at 128 px
# a cell).
PACK_PPU = 4.7
RENDER_CANVAS = 900
CANVAS = (267, 208)
FEET = (133.5, 103)  # the ground point; the feet's lowest pixels then sit where TSE1's do (about y 109)
# Soldiers too big for the TS infantry canvas, on a larger one with the ground point at the same place from its
# centre (the launcher anchors by the centre), measured over every pose: the Zone Trooper's antenna and death fall,
# the Black Hand's flamer deaths, the wide squads. A model's soldier names it; also the render's.
BIG = {"zonetrooper": ((360, 330), 1200), "blackhand": ((380, 300), 1200), "fanatic": ((300, 220), 1000),
       "shadow": ((320, 220), 1000)}


def canvas_of(model):
    """(pack canvas, render canvas) for a model file: its soldier's BIG entry, or the TS infantry's."""
    return BIG.get(model.split("_")[0], (CANVAS, RENDER_CANVAS))
# The cast shadow's opacity: TF's TS infantry shadows sit at a median alpha of about 90.
SHADOW_ALPHA = 0.36
# Team colour level over the tanks': the TS infantry's team green has a median G of about 120, the C&C3 soldiers'
# 85 at the tanks' level.
TEAM_BOOST = 1.45
SOUTH = 4
# Mean luminance over the body pixels of TF's TS infantry (TSE1, TSE2, TSGHOST), which each soldier's frames are
# exposed to; above KNEE, colour rolls off toward white instead of clipping.
TS_LUM_MEAN = 63.9
KNEE = 200.0

# name, model file, cameo (None: the squad keeps its single soldier's), sound model
INFANTRY = (
    ("C3RIFLE", "rifleman", "C3RIFLE", "rifleman"),
    ("C3RIFLESQ", "rifleman_squad", None, "rifleman"),
    ("C3MILIT", "militant", "C3MILIT", "militant"),
    ("C3MILITSQ", "militant_squad", None, "militant"),
    ("C3CYBORG", "cyborg", "C3CYBORG", "cyborg"),
    ("C3CYBORGSQ", "cyborg_squad", None, "cyborg"),
    ("C3MISSL", "missile", "C3MISSL", "missile"),
    ("C3MISSLSQ", "missile_squad", None, "missile"),
    ("C3GREN", "grenadier", "C3GREN", "grenadier"),
    ("C3GRENSQ", "grenadier_squad", None, "grenadier"),
    ("C3ENGI", "engineer", "C3ENGI", "engineer"),
    ("C3SNIPE", "sniper", "C3SNIPE", "sniper"),
    ("C3ZONE", "zonetrooper", "C3ZONE", "zonetrooper"),
    ("C3ZONESQ", "zonetrooper_squad", None, "zonetrooper"),
    ("C3GCMDO", "commando", "C3GCMDO", "commando"),
    ("C3ROCKT", "rocket", "C3ROCKT", "rocket"),
    ("C3ROCKTSQ", "rocket_squad", None, "rocket"),
    ("C3FANAT", "fanatic", "C3FANAT", "fanatic"),
    ("C3FANATSQ", "fanatic_squad", None, "fanatic"),
    ("C3BHAND", "blackhand", "C3BHAND", "blackhand"),
    ("C3BHANDSQ", "blackhand_squad", None, "blackhand"),
    ("C3SHADW", "shadow", "C3SHADW", "shadow"),
    ("C3SHADWSQ", "shadow_squad", None, "shadow"),
    ("C3SABOT", "saboteur", "C3SABOT", "saboteur"),
    ("C3NCMDO", "nodcommando", "C3NCMDO", "nodcommando"),
)
# (sequence, first shape, poses a facing, directional) in shape order
LAYOUT = (("ready", 0, 1, True), ("walk", 8, 6, True), ("idle1", 56, 15, False), ("idle2", 71, 14, False),
          ("crawl", 86, 6, True), ("die1", 134, 15, False), ("die2", 149, 15, False), ("fire", 164, 6, True),
          ("fireprone", 212, 6, True), ("down", 260, 2, True), ("up", 276, 2, True))
SHAPES = 292



def picks(stem, model, sample, letters):
    """One sound event per take C&C3 ships, lettered from A: C3<stem>A plays <sample><letters[0]>, and so on."""
    return [(f"{stem}{chr(65 + i)}", model, [f"{sample}{c}"]) for i, c in enumerate(letters)]


# VOC stem -> (model, C&C3 sample names), every stem listed in asset_packs.PACK_ONLY_SOUNDS. The squads speak and
# fire with their soldier's sounds.
SOUNDS = (
    tanks.takes("C3LSE", "rifleman", "GURifle_VoiSelect", "ABCDEF")
    + tanks.takes("C3LMO", "rifleman", "GURifle_VoiMove", "ABCDEFGHI")
    + tanks.takes("C3LAT", "rifleman", "GURifle_VoiAttack", "ABCDEFGH")
    + [("C3LGUN", "rifleman", [f"GURifle_gun5Fire{c}" for c in "abcdefghij"])]
    + tanks.takes("C3YSE", "cyborg", "NUCyInf_VoiSelect", "ABCDEFGHIJ")
    + tanks.takes("C3YMO", "cyborg", "NUCyInf_VoiMove", "ABCDEFGHI")
    + tanks.takes("C3YAT", "cyborg", "NUCyInf_VoiAttack", "ABCDEFGHI")
    + [("C3YGUN", "cyborg", [f"NUAwake_gunFire{c}" for c in "abcde"])]
    + tanks.takes("C3NSE", "militant", "NUMilit_VoiSelect", "ABCDEFG")
    + tanks.takes("C3NMO", "militant", "NUMilit_VoiMove", "ABCDEFGHIJK")
    + tanks.takes("C3NAT", "militant", "NUMilit_VoiAttack", "ABCDEFG")
    + [("C3NGUN", "militant", [f"NURifle_gunFire2{c}" for c in "abcdefg"])]
    + picks("C3DMSE", "missile", "GUMissi_VoiSelect", "abcdeg") + picks("C3DMMO", "missile", "GUMissi_VoiMove", "abcdfh")
    + tanks.takes("C3DMAT", "missile", "GUMissi_VoiAttack", "ABCDEFG")
    + [("C3DMGUN", "missile", [f"GUMissi_wea1fire{c}" for c in "abcde"])]
    + tanks.takes("C3DGSE", "grenadier", "GUGrena_VoiSelect", "ABCDEF")
    + tanks.takes("C3DGMO", "grenadier", "GUGrena_VoiMove", "ABCDEF")
    + tanks.takes("C3DGAT", "grenadier", "GUGrena_VoiAttack", "ABCDEFG")
    + tanks.takes("C3DESE", "engineer", "GUEngin_VoiSelect", "ABCDEFG")
    + tanks.takes("C3DEMO", "engineer", "GUEngin_VoiMove", "ABCDEFG")
    + tanks.takes("C3DSSE", "sniper", "GUSnipe_VoiSelect", "ABCDEFG")
    + tanks.takes("C3DSMO", "sniper", "GUSnipe_VoiMove", "ABCDEFG")
    + tanks.takes("C3DSAT", "sniper", "GUSnipe_VoiAttack", "ABCDEFGH")
    + [("C3DSGUN", "sniper", [f"GUSnipe_gunFire2{c}" for c in "abcdefghijklmnopqrstuvw"])]
    + picks("C3DZSE", "zonetrooper", "GUZoneT_VoiSelect", "acdef")
    + picks("C3DZMO", "zonetrooper", "GUZoneT_VoiMove", "acdefghi")
    + tanks.takes("C3DZAT", "zonetrooper", "GUZoneT_VoiAttack", "ABCDEFG")
    + [("C3DZGUN", "zonetrooper", [f"GUZoneT_wea1fire{c}" for c in "abcde"])]
    + tanks.takes("C3DCSE", "commando", "GUComma_VoiSelect", "ABCDEFGH")
    + tanks.takes("C3DCMO", "commando", "GUComma_VoiMove", "ABCDEFGH")
    + tanks.takes("C3DCAT", "commando", "GUComma_VoiAttack", "ABCDEFGHIJK")
    + [("C3DCGUN", "commando", [f"GUComma_wea1fire{c}" for c in "abcdefghi"])]
    + tanks.takes("C3ERSE", "rocket", "NURocke_VoiSelect", "ABCDEF")
    + tanks.takes("C3ERMO", "rocket", "NURocke_VoiMove", "ABCDEFG")
    + tanks.takes("C3ERAT", "rocket", "NURocke_VoiAttack", "ABCDEF")
    + tanks.takes("C3EFSE", "fanatic", "NUFanat_VoiSelect", "ABCDEFG")
    + tanks.takes("C3EFMO", "fanatic", "NUFanat_VoiMove", "ABCDEF")
    + tanks.takes("C3EFAT", "fanatic", "NUFanat_VoiAttack", "ABCDEFGHIJK")
    + [("C3EFHIT", "fanatic", [f"NUVerti_bombExpl{c}" for c in "abcdef"])]
    + tanks.takes("C3EBSE", "blackhand", "NuBlack_VoiSelect", "ABCDEF")
    + tanks.takes("C3EBMO", "blackhand", "NuBlack_VoiMove", "ABCDE")
    + tanks.takes("C3EBAT", "blackhand", "NUBlack_VoiAttack", "ABCDE")
    + [("C3EBGUN", "blackhand", [f"NUBlack_weaFlam1{c}" for c in "abcdefghijklmn"])]
    + tanks.takes("C3ESSE", "shadow", "NUShado_VoiSelect", "ABCDEFG")
    + tanks.takes("C3ESMO", "shadow", "NUShado_VoiMove", "ABCDEFG")
    + tanks.takes("C3ESAT", "shadow", "NUShado_VoiAttack", "ABCDEF")
    + [("C3ESGUN", "shadow", [f"NUShaSq_weapFire{c}" for c in "abcdefg"])]
    + tanks.takes("C3EASE", "saboteur", "NUSabot_VoiSelect", "ABCDEFGHI")
    + tanks.takes("C3EAMO", "saboteur", "NUSabot_VoiMove", "ABCDEFGH")
    + tanks.takes("C3ECSE", "nodcommando", "NUComma_VoiSelect", "ABCDEFGHIJKL")
    + tanks.takes("C3ECMO", "nodcommando", "NUComma_VoiMove", "ABCD")
    + tanks.takes("C3ECAT", "nodcommando", "NUComma_VoiAttack", "ABCDEF")
    + [("C3ECGUN", "nodcommando", [f"NUComma_weapFire{c}" for c in "abcd"])]
)
SFX_BEGIN = "  <!-- BEGIN C&C3 infantry sounds (scripts/c3_pack_infantry.py) -->"
SFX_END = "  <!-- END C&C3 infantry sounds -->"


def shape_jobs(model):
    """(shape, pose, facing) for every shape the layout fills, and the shape 85 repeat."""
    d = np.load(f"{ART}/infantry/{model}.npz")
    start = dict(zip(d["seq_names"], d["seq_start"]))
    jobs = []
    for seq, first, count, directional in LAYOUT:
        for f in range(8 if directional else 1):
            for i in range(count):
                jobs.append((first + f * count + i, int(start[seq]) + i, f if directional else SOUTH))
    return jobs


def bled(body):
    """The sheet with each transparent texel's colour filled from its opaque neighbours, so edges never sample black."""
    out = body.copy()
    solid = out[..., 3] >= 128
    for _ in range(32):
        if solid.all():
            break
        acc = np.zeros(out.shape[:2] + (3,))
        cnt = np.zeros(out.shape[:2])
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            s = np.roll(solid, (dy, dx), (0, 1))
            acc += np.roll(out[..., :3], (dy, dx), (0, 1)) * s[..., None]
            cnt += s
        grow = ~solid & (cnt > 0)
        out[grow, :3] = acc[grow] / cnt[grow, None]
        solid = solid | grow
    return out


def prepared(m):
    """The model with its diffuse sheet bled into its transparent texels and its team colour raised (TEAM_BOOST)."""
    m.set_body(bled(m.body), TEAM_BOOST)
    return m


def render_shape(args):
    """The soldier at a pose and facing, and his shadow cast along the render light onto the ground: two PNG paths."""
    model, pose, facing = args
    path = f"{ART}/renders/inf_{model}/pose{pose:03d}-f{facing}.png"
    shadow = path[:-4] + "-shadow.png"
    if os.path.exists(path) and os.path.exists(shadow):
        return path, shadow
    m = prepared(c3_render.Model(f"{ART}/infantry/{model}.npz"))
    d = np.load(f"{ART}/infantry/{model}.npz")
    m.pos, m.nrm = d["poses_pos"][pose], d["poses_nrm"][pose]
    m.hull_centre = np.zeros(3)
    yaw = 90.0 + facing * 45.0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rc = canvas_of(model)[1]
    body = c3_render.render(m, yaw, "hull", RENDER_PPU, rc, tanks.ELEV_DEG)
    a = np.asarray(body.getchannel("A"))
    if max(a[0].max(), a[-1].max(), a[:, 0].max(), a[:, -1].max()):
        raise SystemExit(f"{path}: the soldier reaches the {rc} px render's edge -- grow it in BIG")
    body.save(path)
    a = np.radians(yaw)
    light = np.array([[np.cos(a), np.sin(a), 0], [-np.sin(a), np.cos(a), 0], [0, 0, 1]]) @ c3_render.LIGHT
    pos = m.pos.copy()
    m.pos = pos - light[None, :] * (np.maximum(pos[:, 2], 0) / light[2])[:, None]
    m.pos[:, 2] = 0.0
    c3_render.render(m, yaw, "hull", RENDER_PPU, rc, tanks.ELEV_DEG).getchannel("A").save(shadow)
    return path, shadow


def placed(path, canvas=CANVAS):
    """The render (or shadow mask) scaled to the pack and placed on the canvas with its feet on the line."""
    im = Image.open(path)
    im = im.convert("RGBA") if im.mode != "L" else Image.merge("RGBA", (im, im, im, im))
    im = tanks.scaled(im, RENDER_PPU, PACK_PPU)
    feet = (FEET[0] + (canvas[0] - CANVAS[0]) / 2, FEET[1] + (canvas[1] - CANVAS[1]) / 2)
    x, y = round(feet[0] - im.width / 2), round(feet[1] - im.height / 2)
    b = im.getbbox()
    if b and (x + b[0] < 0 or y + b[1] < 0 or x + b[2] > canvas[0] or y + b[3] > canvas[1]):
        raise SystemExit(f"{path}: content clipped by the {canvas} canvas")
    fr = Image.new("RGBA", canvas, (0, 0, 0, 0))
    fr.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))
    return fr


def toned(frames, shadows):
    """The frames exposed by one factor that takes the body pixels' mean luminance over every frame to the TS
    infantry's, so darks stay dark and colours keep their saturation; each laid over its cast shadow."""
    arrs = [np.asarray(f).astype(np.float32) for f in frames]
    body = np.concatenate([a[a[..., 3] > 250][:, :3] for a in arrs])
    k = TS_LUM_MEAN / max(float((body @ c3_render.LUMA).mean()), 1.0)
    out = []
    for a, sh in zip(arrs, shadows):
        a = a.copy()
        x = a[..., :3] * k
        x = np.where(x > KNEE, KNEE + (255.0 - KNEE) * (1 - np.exp(-(x - KNEE) / (255.0 - KNEE))), x)
        a[..., :3] = x * (a[..., 3:] > 0)
        under = np.zeros_like(a)
        under[..., 3] = np.asarray(sh)[..., 3].astype(np.float32) * SHADOW_ALPHA
        fr = Image.fromarray(under.astype(np.uint8), "RGBA")
        fr.alpha_composite(Image.fromarray(a.astype(np.uint8), "RGBA"))
        out.append(fr)
    return out


def pack(name, model, cameo):
    jobs = shape_jobs(model)
    with multiprocessing.Pool(tanks.RENDER_WORKERS) as pool:
        paths = pool.map(render_shape, [(model, p, f) for _, p, f in jobs])
    by_shape = dict(zip([s for s, _, _ in jobs], paths))
    numbers = sorted(by_shape)
    canvas = canvas_of(model)[0]
    frames = toned([placed(by_shape[s][0], canvas) for s in numbers], [placed(by_shape[s][1], canvas) for s in numbers])
    tanks.write_zip(asset_packs.art_zip(name, "UNITS"), name.lower(), frames, numbers=numbers)
    sub = name.lower()
    tiles = [f"{sub}\\{sub}-{(s if s in by_shape else s - 1):04d}.tga" for s in range(SHAPES)]
    tanks.patch_tileset(name, SHAPES, tiles)
    if cameo:
        tanks.write_cameo(cameo)


def main(names):
    if not ART:
        raise SystemExit("set C3_ART_DIR (holding infantry/, cameo/)")
    unknown = set(names) - {i[0] for i in INFANTRY}
    if unknown:
        raise SystemExit(f"unknown infantry: {', '.join(sorted(unknown))}")
    for name, model, cameo, _ in INFANTRY:
        if not names or name in names:
            pack(name, model, cameo)
    tanks.write_audio({i[3] for i in INFANTRY if i[0] in names} if names else None, SOUNDS, SFX_BEGIN, SFX_END)


if __name__ == "__main__":
    main(sys.argv[1:])
