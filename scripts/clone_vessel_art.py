#!/usr/bin/env python3
"""Clone a base RA vessel's hull art + tileset into a TD-named copy.

For the v4.0 GDI surface-fleet clones (VESSEL_TDPT/TDDD/TDCA): take a base
vessel ZIP already extracted from TEXTURES_RA_SRGB.MEG (dd-SHAPE-FRAME.tga +
.meta, 16 facings x 8 anim), rename every inner file SRC->DST, and repack as a
loose DST.ZIP in the mod's UNITS dir. Then emit the 16 RA_UNITS.XML <Tile>
blocks for the clone (copied verbatim from the base unit's blocks, with names
remapped) so the launcher renders the cloned hull by IniName.

The turret (MGUN/SSAM/TURR) is a GLOBAL launcher resource drawn by name in
VesselClass::Draw_It -- it is NOT part of the hull ZIP, so only the hull is
cloned here; the clone gets its spinning turret for free.

Usage:
  clone_vessel_art.py <src_zip> <SRC> <DST> <out_units_dir> <ra_units_xml>

  src_zip       e.g. /tmp/vesselzips/DD.ZIP
  SRC           lowercase base prefix, e.g. dd
  DST           lowercase clone prefix, e.g. tddd
  out_units_dir loose UNITS dir to write DST.ZIP into
  ra_units_xml  RA_UNITS.XML (read-only here; we print the new blocks to stdout)

License: GPL v3.
"""
import sys, os, zipfile, re

src_zip, SRC, DST, out_units_dir, xml_path = sys.argv[1:6]
SRC = SRC.lower()
DST = DST.lower()

# --- 1. repack art: rename SRC-* -> DST-* inside a new loose ZIP ---
out_zip = os.path.join(out_units_dir, DST.upper() + ".ZIP")
n = 0
with zipfile.ZipFile(src_zip, "r") as zin, \
     zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.namelist():
        base = os.path.basename(item)
        if not base.lower().startswith(SRC + "-"):
            print(f"  WARN unexpected entry {item}", file=sys.stderr)
            continue
        newname = DST + base[len(SRC):]          # dd-0000-0000.tga -> tddd-0000-0000.tga
        zout.writestr(newname, zin.read(item))
        n += 1
print(f"  packed {n} entries -> {out_zip}", file=sys.stderr)

# --- 2. emit the 16 tileset <Tile> blocks, transformed from the base unit ---
xml = open(xml_path, encoding="utf-8").read()
# Each block: <Tile> ... <Name>SRC</Name><Shape>k</Shape> ... </Tile>
# Pull every <Tile>...</Tile> whose Key Name is exactly the base unit (upper).
SRCU = SRC.upper()
DSTU = DST.upper()
blocks = []
for m in re.finditer(r"\t*<Tile>.*?</Tile>\n?", xml, re.DOTALL):
    blk = m.group(0)
    if re.search(r"<Name>" + re.escape(SRCU) + r"</Name>", blk):
        # remap: tag name SRCU->DSTU, frame folder/file SRC-> DST
        nb = blk.replace(f"<Name>{SRCU}</Name>", f"<Name>{DSTU}</Name>")
        nb = nb.replace(f"{SRC}\\{SRC}-", f"{DST}\\{DST}-")
        blocks.append(nb)
print(f"  found {len(blocks)} tileset blocks for {SRCU}", file=sys.stderr)
out_xml = out_units_dir.rstrip("/") + f"/_{DSTU}_tiles.xml"
with open(out_xml, "w", encoding="utf-8") as f:
    f.write("".join(blocks))
print(out_xml)
