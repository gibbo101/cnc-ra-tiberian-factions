#!/usr/bin/env python3
"""The sidebar side of Tiberian Sun infantry: cameo, sidebar entry and text, plus the projectiles,
effects and sounds a unit brings. Their art is the HD rebuilds', packed by scripts/ts_pack_hd_buildings.py.

Writes, per unit: BuildIcon_TS_<Name>.tga from the TS cameo, the base RA_<INI> TSBUILDABLES.XML
entry and the ModText rows; cameos, sounds and XML go to the tree asset_packs.py routes each name
to (the TS packs). The TS-badged _G variant comes from the TS-tree badge tooling, not from here.
Other packers share the cameo, sidebar entry and ModText helpers.

Inputs (set TS_ART_DIR): shp_<cameo> decoded against CAMEO.PAL (scripts/ts_shp.py), and the
projectile, effect and sound sources in .raw.

  ts_pack_infantry.py [INI ...]      default: every unit in UNITS

License: GPL v3.
"""
import os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_packs

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the extracted/rendered TS art directory")
MOD = os.environ.get("TF_MOD_DIR", asset_packs.MOD)
CSV = f"{MOD}/Data/ModText.csv"

# ini -> (cameo stem, icon name, display name, description)
UNITS = {
    "TSE1": ("e1icon", "BuildIcon_TS_E1", "Light Infantry",
             "Basic GDI infantry armed with a minigun."),
    "TSE2": ("e2icon", "BuildIcon_TS_E2", "Disc Thrower",
             "GDI infantry that lobs explosive discs over walls and cover."),
    "TSENGINEER": ("engnicon", "BuildIcon_TS_Engineer", "Engineer",
                   "Captures enemy structures outright and restores friendly ones to full strength."),
    "TSMEDIC": ("mediicon", "BuildIcon_TS_Medic", "Medic",
                "Heals nearby friendly infantry."),
    "TSGHOST": ("gosticon", "BuildIcon_TS_Ghost", "Ghost Stalker",
                "Elite commando. His railgun pierces a line of troops, he plants C4 on "
                "structures and heals in Tiberium. One at a time."),
    "TSJUMPJET": ("jjeticon", "BuildIcon_TS_Jumpjet", "Jumpjet Infantry",
                  "Airborne GDI infantry. Flies over terrain on jump jets and fires from the air."),
}

# ini -> TS anims the unit brings with it: (SHP in $TS_ART_DIR/.raw, VFX tileset name), decoded
# against ANIM.PAL; each needs its classic stub in build_tfassets.sh.
EFFECTS = {
    "TSJUMPJET": (("S_BANG34.SHP", "TSBANG34"),),  # [General] InfantryExplode: shot down in flight
}

# ini -> TS sounds the unit brings with it, each shipped as AUDIO/TS<name>.WAV in its pack.
SOUNDS = {
    "TSJUMPJET": ("JUMPJET1", "EXPNEW10"),  # [JumpCannon] Report, [S_BANG34] Report
}

# ini -> (TS projectile SHP in $TS_ART_DIR/.raw, VFX tileset name). The projectile ships as
# a full 32-tile set, its frames cycled round, so any shape index the launcher asks for
# has a tile (the RPG tower canister's contract); its classic stub is in build_tfassets.sh.
PROJECTILES = {
    "TSE2": ("DISCUS.SHP", "TSDISCUS"),
}


def cameo(stem, icon):
    icon_img = Image.open(f"{ART}/shp_{stem}/frame-0000.png").convert("RGBA")
    big = icon_img.resize((icon_img.width * 8, icon_img.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    asset_packs.save_classic_cameo(big, icon)


HAND_END = "\t<!-- END hand-written TS-tree base cameo entries -->"


def add_entry(key, icon, entry):
    """Add a base sidebar entry to the buildables XML of its cameo's tree, unless it is there:
    in the hand-written TS-tree block when the file has one, otherwise at the end of a pack's
    file, whose entries are listed loose."""
    rab = asset_packs.buildables_xml(icon)
    xml = open(rab, encoding="utf-8").read()
    if f'"{key}"' in xml:
        return
    end = HAND_END
    if end not in xml and asset_packs.cameo_pack(icon):
        end = "</ObjectTypeList>"
    if end not in xml:
        raise SystemExit(f"{os.path.basename(rab)} has no hand-written TS-tree block; place the entry by hand")
    open(rab, "w", encoding="utf-8").write(xml.replace(end, entry + end, 1))
    print(f"patched {os.path.basename(rab)}: {key}")


def sidebar(ini, icon, kind="UNIT"):
    """The base RA_<INI> entry naming the pristine cameo and its TEXT_<kind>_<INI> rows (add_entry). Variants:
    list the type in cameo_work/faction_masks.txt, run cameo_badge_build.py <INI>, then cameo_variants_build.py."""
    key = f"RA_{ini}"
    entry = ('\t<ObjectTypeClass Name="%s" Classification="CNCBuildableObject" CanInstantiate="False">\n'
             "\t\t<CNCEncyclopediaComponent>\n"
             "\t\t\t<ObjectNameTextID>TEXT_%s_%s</ObjectNameTextID>\n"
             "\t\t\t<ObjectDescriptionTextID>TEXT_%s_%s_DESC</ObjectDescriptionTextID>\n"
             "\t\t\t<BuildIcon>%s</BuildIcon>\n"
             "\t\t</CNCEncyclopediaComponent>\n"
             "\t</ObjectTypeClass>\n" % (key, kind, ini, kind, ini, icon))
    add_entry(key, icon, entry)


def text_rows(ini, display, desc, kind="UNIT"):
    """The TEXT_<kind>_<INI> name and description rows in ModText.csv, unless they are there."""
    raw = open(CSV, "rb").read()
    text = raw.decode("utf-16")
    eol = "\r\n" if "\r\n" in text else "\n"
    sample = next(l for l in text.splitlines() if l.startswith('"TEXT_UNIT_TDA10"'))
    tail = sample.split('"A-10 Warthog"', 1)[1]
    new = ""
    for key, val in ((f"TEXT_{kind}_{ini}", display), (f"TEXT_{kind}_{ini}_DESC", desc)):
        if f'"{key}"' not in text:
            new += f'"{key}",,,"{val}"{tail}{eol}'
    if new:
        if not text.endswith(eol):
            text += eol
        open(CSV, "wb").write((text + new).encode("utf-16"))
        print(f"patched ModText.csv: TEXT_{kind}_{ini}")


def pack(ini):
    cameo_stem, icon, display, desc = UNITS[ini]
    cameo(cameo_stem, icon)
    sidebar(ini, icon)
    text_rows(ini, display, desc)
    if ini in PROJECTILES:
        import ts_pack_towerfx, ts_shp
        shp, name = PROJECTILES[ini]
        pal = ts_shp.load_pal(f"{ART}/.raw/UNITTEM.PAL")
        ts_pack_towerfx.pack(shp, name, pal, order=lambda k, n: k % n, count=32)
    if ini in EFFECTS:
        import ts_pack_towerfx, ts_shp
        pal = ts_shp.load_pal(f"{ART}/.raw/ANIM.PAL")
        for shp, name in EFFECTS[ini]:
            ts_pack_towerfx.pack(shp, name, pal)
    for aud in SOUNDS.get(ini, ()):
        import subprocess
        pcm = f"{ART}/.raw/{aud}.pcm.wav"
        subprocess.run([sys.executable, f"{HERE}/ts_aud_decode.py", f"{ART}/.raw/{aud}.AUD", pcm],
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pcm, "-c:a", "adpcm_ms",
                        "-ar", "22050", "-ac", "1", asset_packs.sound_wav(f"TS{aud}")], check=True)
        print(f"wrote TS{aud}.WAV")


if __name__ == "__main__":
    for ini in (sys.argv[1:] or list(UNITS)):
        pack(ini)
