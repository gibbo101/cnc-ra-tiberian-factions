#!/usr/bin/env python3
"""Package EA's own HD infantry frames to fit TS infantry animations against: per unit, every frame as a PNG
with its META, a contact sheet, a strip per sequence and SEQUENCES.txt quoted from EA's released source.

Reads the game's texture MEGs and the EA source clone; touches nothing else. The frames are EA's TGAs as
shipped (cropped, house colour untouched); only the check images place them on the META canvas.

Usage: ea_infantry_extract.py [OUTDIR]   (default ~/Desktop/Tiberian Factions/ea-infantry-hd)
License: GPL v3.
"""
import io
import json
import os
import re
import sys
import textwrap
import zipfile

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meg_extract import read_member  # noqa: E402

GAME_DATA = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data")
EA_SOURCE = os.path.expanduser("~/Documents/development/CnC_Remastered_Collection")
DEFAULT_OUT = os.path.expanduser("~/Desktop/Tiberian Factions/ea-infantry-hd")
ZIP_LIMIT = 30 * 1024 * 1024
FACINGS = ("N", "NW", "W", "SW", "S", "SE", "E", "NE")
GREEN = (72, 140, 72, 255)

# (game, unit, MEG, path inside it, source file, the table the HD (GlyphX) client draws from)
UNITS = (
    ("ra", "E1", "TEXTURES_RA_SRGB.MEG", r"DATA\ART\TEXTURES\SRGB\RED_ALERT\UNITS\E1.ZIP", "REDALERT/IDATA.CPP", "E1DoControlsVirtual"),
    ("ra", "E2", "TEXTURES_RA_SRGB.MEG", r"DATA\ART\TEXTURES\SRGB\RED_ALERT\UNITS\E2.ZIP", "REDALERT/IDATA.CPP", "E2DoControlsVirtual"),
    ("ra", "E6", "TEXTURES_RA_SRGB.MEG", r"DATA\ART\TEXTURES\SRGB\RED_ALERT\UNITS\E6.ZIP", "REDALERT/IDATA.CPP", "E6DoControls"),
    ("ra", "MEDI", "TEXTURES_RA_SRGB.MEG", r"DATA\ART\TEXTURES\SRGB\RED_ALERT\UNITS\MEDI.ZIP", "REDALERT/IDATA.CPP", "MedicDoControls"),
    ("td", "E1", "TEXTURES_TD_SRGB.MEG", r"DATA\ART\TEXTURES\SRGB\TIBERIAN_DAWN\UNITS\E1.ZIP", "TIBERIANDAWN/IDATA.CPP", "MiniGunnerDos"),
    ("td", "E2", "TEXTURES_TD_SRGB.MEG", r"DATA\ART\TEXTURES\SRGB\TIBERIAN_DAWN\UNITS\E2.ZIP", "TIBERIANDAWN/IDATA.CPP", "GrenadierDos"),
    ("td", "RMBO", "TEXTURES_TD_SRGB.MEG", r"DATA\ART\TEXTURES\SRGB\TIBERIAN_DAWN\UNITS\RMBO.ZIP", "TIBERIANDAWN/IDATA.CPP", "CommandoDos"),
)

# What the strips show where EA's table and its frames disagree, read by eye: (game, unit) -> notes.
EYEBALLED = {
    ("ra", "E6"): ("DO_LIE_DOWN looks one frame late in EA's table: in strips/do_lie_down.png each row pairs a "
                   "facing's crouch with the next facing's standing frame, and NE ends on the prone N frame (82). "
                   "The frames read as 66-81, two per facing (66-67 N .. 80-81 NE); 64-65 belong to no sequence. "
                   "RA plays the table as written."),
    ("ra", "MEDI"): ("Frames 84-113 look like more of the kneeling heal (DO_FIRE_WEAPON plays 56-83). Frame 201 "
                     "(standing, kit flying) looks like the first frame of the blood-splat death 202-209, and frame "
                     "217, where DO_EXPLOSION_DEATH and DO_GRENADE_DEATH meet, is a lying-down end frame: the "
                     "grenade death's own frames look like 218-228."),
    ("td", "E1"): ("DO_ON_GUARD to DO_READY_WEAPON (the hand-to-hand set, 288-334) are in TD's table but TD never "
                   "triggers them in play; RA's 21-action table drops them."),
    ("td", "E2"): ("DO_ON_GUARD to DO_READY_WEAPON (the hand-to-hand set) are in TD's table but TD never "
                   "triggers them in play; RA's 21-action table drops them."),
    ("td", "RMBO"): ("DO_ON_GUARD to DO_READY_WEAPON (the hand-to-hand set) are in TD's table but TD never "
                     "triggers them in play; RA's 21-action table drops them."),
}

# The source lines that say how a frame is picked, quoted in every SEQUENCES.txt: (file, pattern).
FRAME_RULE = {
    "ra": (("REDALERT/INFANTRY.CPP", r"InfantryClass::HumanShape\[32\] ="),
           ("REDALERT/INFANTRY.CPP", r"do_controls = \(window == WINDOW_VIRTUAL\)"),
           ("REDALERT/INFANTRY.CPP", r"int shapenum = Fetch_Stage\(\)"),
           ("REDALERT/INFANTRY.CPP", r"shapenum \+= HumanShape\[Dir_To_32"),
           ("REDALERT/IDATA.CPP", r"For the virtual do controls"),
           ("REDALERT/DEFINES.H", r"int\s+Frame;\s+// Starting frame"),
           ("REDALERT/DEFINES.H", r"unsigned char\s+Count;"),
           ("REDALERT/DEFINES.H", r"unsigned char\s+Jump;")),
    "td": (("TIBERIANDAWN/INFANTRY.CPP", r"InfantryClass::HumanShape\[32\] ="),
           ("TIBERIANDAWN/INFANTRY.CPP", r"facenum = HumanShape\[facing\]"),
           ("TIBERIANDAWN/INFANTRY.CPP", r"shapenum = Fetch_Stage\(\) % MAX"),
           ("TIBERIANDAWN/INFANTRY.CPP", r"shapenum \+= facenum \* Class->DoControls"),
           ("TIBERIANDAWN/INFANTRY.CPP", r"shapenum \+= Class->DoControls\[doit\]\.Frame"),
           ("TIBERIANDAWN/DEFINES.H", r"int\s+Frame;\s+// Starting frame"),
           ("TIBERIANDAWN/DEFINES.H", r"unsigned char\s+Count;"),
           ("TIBERIANDAWN/DEFINES.H", r"unsigned char\s+Jump;")),
}


def source_lines(rel):
    with open(os.path.join(EA_SOURCE, rel), encoding="latin-1") as f:
        return f.read().splitlines()


def quote(rel, pattern):
    """The first source line matching pattern, as 'file:line: text'."""
    for n, line in enumerate(source_lines(rel), 1):
        if re.search(pattern, line):
            return f"{rel}:{n}: {line.strip()}"
    raise SystemExit(f"{rel}: no line matches {pattern}")


def read_table(rel, name):
    """EA's sequence table: [(sequence, first, count, jump, n/a, 'file:line: text')]."""
    lines = source_lines(rel)
    start = next(i for i, l in enumerate(lines) if re.search(rf"\b{name}\s*\[DO_COUNT\]", l))
    rows = []
    for i in range(start + 1, len(lines)):
        line = lines[i]
        if line.strip().startswith("};"):
            break
        m = re.search(r"(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\}?\s*,?\s*//\s*(DO_\w+)", line)
        if m:
            rows.append((m.group(4), int(m.group(1)), int(m.group(2)), int(m.group(3)), "N/A" in line,
                         f"{rel}:{i + 1}: {line.strip()}"))
    return start + 1, lines[start].strip(), rows


def table_users(rel, unit, name):
    """The lines of the unit's constructor that hand it the table, quoted."""
    lines = source_lines(rel)
    ini = next(i for i, l in enumerate(lines) if re.search(rf'^\s*"{unit}",', l))
    out = [f"{rel}:{ini + 1}: {lines[ini].strip()}"]
    for i in range(ini, min(ini + 40, len(lines))):
        if re.search(rf"\b{name}\b", lines[i]):
            out.append(f"{rel}:{i + 1}: {lines[i].strip()}")
    return out


def frames_of(first, count, jump):
    """Each facing's frames (one row when the sequence ignores facing)."""
    if jump:
        return [[first + f * jump + s for s in range(count)] for f in range(8)]
    return [[first + s for s in range(count)]]


def ranges(nums):
    nums = sorted(set(nums))
    out, run = [], []
    for n in nums:
        if run and n != run[-1] + 1:
            out.append(run)
            run = []
        run.append(n)
    if run:
        out.append(run)
    return ", ".join(f"{r[0]}" if len(r) == 1 else f"{r[0]}-{r[-1]}" for r in out)


def label(img, xy, text):
    d = ImageDraw.Draw(img)
    x, y = xy
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((x + dx, y + dy), text, fill=(0, 0, 0, 255))
    d.text((x, y), text, fill=(255, 255, 255, 255))


def pack_unit(game, unit, meg, inner, src, table, out):
    blob = read_member(os.path.join(GAME_DATA, meg), inner)
    zf = zipfile.ZipFile(io.BytesIO(blob))
    names = sorted(n for n in zf.namelist() if n.lower().endswith(".tga"))
    frames, metas = {}, {}
    for n in names:
        num = int(re.search(r"-(\d+)\.tga$", n, re.I).group(1))
        frames[num] = Image.open(io.BytesIO(zf.read(n))).convert("RGBA")
        meta_name = n[:-4] + ".meta"
        metas[num] = zf.read(meta_name) if meta_name in zf.namelist() else None
    count = max(frames) + 1
    missing = [n for n in range(count) if n not in frames]
    empty = [n for n, im in frames.items() if im.getchannel("A").getbbox() is None]
    parsed = {n: json.loads(m) for n, m in metas.items() if m}
    canvases = {tuple(m["size"]) for m in parsed.values()}
    crop_ok = all((m["crop"][2] - m["crop"][0], m["crop"][3] - m["crop"][1]) == frames[n].size for n, m in parsed.items())
    canvas = canvases.pop() if len(canvases) == 1 else None

    # The check images place each frame on its META canvas, cut to the box every frame fits in.
    x0 = min(m["crop"][0] for m in parsed.values())
    y0 = min(m["crop"][1] for m in parsed.values())
    x1 = max(m["crop"][2] for m in parsed.values())
    y1 = max(m["crop"][3] for m in parsed.values())
    box = (x0, y0, x1, y1)

    def placed(n):
        c = Image.new("RGBA", canvas, (0, 0, 0, 0))
        c.paste(frames[n], tuple(parsed[n]["crop"][:2]))
        return c.crop(box)

    root = f"{unit}"
    files = {}
    low = unit.lower()
    for n in sorted(frames):
        b = io.BytesIO()
        frames[n].save(b, "PNG", optimize=True)
        files[f"{root}/frames/{low}-{n:04d}.png"] = b.getvalue()
        if metas[n] is not None:
            files[f"{root}/frames/{low}-{n:04d}.meta"] = metas[n]

    bw, bh = x1 - x0, y1 - y0
    tw, th, cols = bw // 2, bh // 2 + 14, 20
    sheet = Image.new("RGBA", (cols * tw, ((len(frames) + cols - 1) // cols) * th), GREEN)
    for i, n in enumerate(sorted(frames)):
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.alpha_composite(placed(n).resize((tw, bh // 2), Image.LANCZOS), (x, y))
        label(sheet, (x + 2, y + bh // 2), str(n))
    b = io.BytesIO()
    sheet.save(b, "PNG", optimize=True)
    files[f"{root}/sheet.png"] = b.getvalue()

    start_line, header, rows = read_table(src, table)
    used, flags, seq_text = {}, [], []
    for seq, first, cnt, jump, na, line in rows:
        if na or cnt == 0:
            seq_text.append(f"{seq:<22} not used ({'N/A' if na else 'count 0'})\n    {line}")
            continue
        grid = frames_of(first, cnt, jump)
        flat = [f for row in grid for f in row]
        beyond = [f for f in flat if f >= count]
        if beyond:
            flags.append(f"{seq}: frames {ranges(beyond)} are beyond the last frame ({count - 1})")
        if jump and jump < cnt:
            flags.append(f"{seq}: Jump {jump} is less than Count {cnt}, so facings share frames")
        for f in flat:
            used.setdefault(f, set()).add((seq, first, cnt, jump))
        if jump:
            per = "\n".join(f"      {FACINGS[i]:<2} {r[0]}-{r[-1]}" if len(r) > 1 else f"      {FACINGS[i]:<2} {r[0]}"
                            for i, r in enumerate(grid))
            desc = f"first {first}, {cnt} frame(s) per facing, jump {jump} between facings\n{per}"
        else:
            desc = f"first {first}, {cnt} frame(s), facing ignored (jump 0): {first}-{first + cnt - 1}"
        seq_text.append(f"{seq:<22} {desc}\n    {line}")

        cell_w, cell_h = bw, bh + 14
        strip = Image.new("RGBA", (36 + cnt * cell_w, len(grid) * cell_h), GREEN)
        for r, row in enumerate(grid):
            label(strip, (4, r * cell_h + bh // 2), FACINGS[r] if jump else "-")
            for c, f in enumerate(row):
                x, y = 36 + c * cell_w, r * cell_h
                if f < count:
                    strip.alpha_composite(placed(f), (x, y))
                label(strip, (x + 2, y + bh), str(f))
        b = io.BytesIO()
        strip.save(b, "PNG", optimize=True)
        files[f"{root}/strips/{seq.lower()}.png"] = b.getvalue()

    shared = {}
    for f, seqs in used.items():
        if len({(s[1], s[2], s[3]) for s in seqs}) > 1:
            shared.setdefault(tuple(sorted(s[0] for s in seqs)), []).append(f)
    for seqs, fs in sorted(shared.items()):
        flags.append(f"{' and '.join(seqs)} share frame(s) {ranges(fs)}")
    unused = [n for n in range(count) if n not in used]

    rule = "\n".join(quote(f, p) for f, p in FRAME_RULE[game])
    seq_doc = "\n".join([
        f"{game.upper()} {unit}: EA's infantry sequence table for the HD (GlyphX) client",
        "",
        "How a frame is picked (EA's source, file:line):",
        rule,
        "So: frame = Frame + (stage % Count) + facing * Jump, the facing index from HumanShape: 0 N, 1 NW, 2 W,",
        "3 SW, 4 S, 5 SE, 6 E, 7 NE (Dir_To_32 counts clockwise from north). Jump 0 = the sequence ignores facing.",
        "",
        "The table, and where the unit is handed it:",
        f"{src}:{start_line}: {header}",
        *table_users(src, unit, table),
        "",
        "Sequences (Frame, Count, Jump as quoted under each):",
        *seq_text,
        "",
        "Frames no sequence uses: " + (ranges(unused) if unused else "none"),
        "Flags: " + ("none" if not flags else ""),
        *[f"  - {x}" for x in flags],
        "",
    ])
    files[f"{root}/SEQUENCES.txt"] = seq_doc.encode()

    info = dict(game=game, unit=unit, meg=meg, inner=inner, count=count, canvas=canvas, missing=missing,
                empty=empty, crop_ok=crop_ok, box=box, flags=flags, unused=unused, table=table, src=src,
                metas=sum(1 for m in metas.values() if m))
    return files, info


def readme(info):
    i = info
    return "\n".join([
        f"EA's HD {i['game'].upper()} {i['unit']} infantry frames, from the C&C Remastered Collection install.",
        "",
        f"Source: {i['meg']} (the sRGB textures), member {i['inner']}.",
        "No game file was changed; the MEG was only read.",
        f"Frames: {i['count']} ({i['unit'].lower()}-0000 to -{i['count'] - 1:04d}), numbered as in EA's file names.",
        f"Missing frame numbers: {ranges(i['missing']) if i['missing'] else 'none'}. "
        f"Empty (fully transparent) frames: {ranges(i['empty']) if i['empty'] else 'none'}.",
        "",
        "META (kept next to each frame, as shipped): {\"size\":[w,h],\"crop\":[x0,y0,x1,y1]}.",
        f"  Every frame's canvas is {i['canvas'][0]}x{i['canvas'][1]}. EA ships each TGA cropped to its pixels:",
        "  'crop' is where that TGA sits on the canvas (x0, y0 its top-left; x1-x0, y1-y0 its size, which",
        f"  matches every TGA: {'yes' if i['crop_ok'] else 'NO, see the frames'}). So the frames do move on the canvas, frame",
        "  by frame. The PNGs here are the TGAs as shipped, NOT placed on the canvas: to line frames up, paste",
        "  each at (x0, y0) on a canvas of 'size'. The canvas centre is the unit's position in game.",
        f"  The check images (sheet.png, strips/) do place them, cut to {i['box']} (x0, y0, x1, y1), the box",
        "  every frame fits in.",
        "House colour: as EA ships it (not recoloured).",
        "",
        "Facing order (EA's HumanShape table): 0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE, 6 E, 7 NE; frame =",
        "Frame + stage + facing * Jump. SEQUENCES.txt quotes the source lines.",
        f"Sequence table: {i['table']} in {i['src']}"
        + (" (the 'Virtual' table: RA's HD client draws infantry from TD's frame numbers)." if "Virtual" in i["table"] else "."),
        "",
        "How the ranges were checked: every sequence's frames were worked out from the table and checked to",
        "exist (none past the last frame, none empty), facings checked not to share frames, and sequences",
        "checked for frames they share; strips/<sequence>.png draws each, one row per facing, with frame",
        "numbers, for eyeballing.",
        "Flags: " + ("none" if not i["flags"] else ""),
        *[f"  - {x}" for x in i["flags"]],
        f"Frames no sequence uses: {ranges(i['unused']) if i['unused'] else 'none'}.",
        "Most flags are EA's design: a prone fire starts on the prone frame, and idles or gestures share",
        "frames on purpose.",
        *(["", "Read by eye from the strips:", *textwrap.wrap(EYEBALLED[(i['game'], i['unit'])], 104)]
          if (i['game'], i['unit']) in EYEBALLED else []),
        "",
        "Layout: <UNIT>/frames/*.png (+ .meta), <UNIT>/sheet.png, <UNIT>/strips/*.png, <UNIT>/SEQUENCES.txt.",
        "",
    ])


def write_zips(out, files, info):
    name = f"ea-{info['game']}-{info['unit'].lower()}-hd"
    text = readme(info).encode()
    parts, part, size = [], {}, 0
    for path, data in files.items():
        if part and size + len(data) > ZIP_LIMIT - 1024 * 1024:
            parts.append(part)
            part, size = {}, 0
        part[path] = data
        size += len(data)
    parts.append(part)
    written = []
    for k, p in enumerate(parts, 1):
        zname = f"{name}.zip" if len(parts) == 1 else f"{name}-part{k}.zip"
        zpath = os.path.join(out, zname)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("README.txt", text)
            for path, data in p.items():
                z.writestr(path, data)
        written.append((zname, os.path.getsize(zpath)))
    return written


def main(argv):
    out = argv[0] if argv else DEFAULT_OUT
    os.makedirs(out, exist_ok=True)
    report = []
    for game, unit, meg, inner, src, table in UNITS:
        files, info = pack_unit(game, unit, meg, inner, src, table, out)
        for zname, size in write_zips(out, files, info):
            report.append(f"{zname}  {size / 1048576:.1f} MiB")
            print(f"{zname}  {size / 1048576:.1f} MiB, {info['count']} frames, flags {len(info['flags'])}")
    with open(os.path.join(out, "ZIPS.txt"), "w") as f:
        f.write("\n".join(report) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
