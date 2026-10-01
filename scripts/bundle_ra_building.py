#!/usr/bin/env python3
'''bundle_ra_building.py — make an INDEPENDENT copy of an RA building's HD art
under a TD-prefixed name, for a separated GDI/Nod production building.

Unlike bundle_assets.py (which sources TD-original buildings from
TEXTURES_TD_SRGB.MEG), this sources an RA building (SYRD/SPEN/AFLD + its MAKE
buildup) from TEXTURES_RA_SRGB.MEG and writes brand-new, separately-editable
ZIPs + tileset blocks. The art is identical to the RA building NOW, but lives in
its own files so a later faction-logo reskin only touches our building, not the
RA one. (v4.0 — GDI Naval Yard / Nod Sub Pen / GDI Airfield.)
The ZIPs and tile blocks land in the tree asset_packs assigns the new name: the
mod's own (RA_STRUCTURES.XML) or an asset pack's (<PREFIX>_STRUCTURES.XML).

Usage:  scripts/bundle_ra_building.py SYRD TDGYARD --build-icon BuildIcon_RA_NavalYard \
            --text-name TEXT_STRUCT_TITLE_GDI_NAVALYARD --text-desc TEXT_STRUCT_DESC_GDI_NAVALYARD
'''
import argparse, re, sys, tempfile, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundle_assets import extract_named_zip, patch_rabuildables_xml  # noqa: E402
import asset_packs  # noqa: E402

RA_MEG = Path.home() / ".steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_RA_SRGB.MEG"


def repack_prefix(src_zip, dst_zip, old, new):
    '''Copy src_zip -> dst_zip, replacing the (case-insensitive) `old` token with
    `new` in every member name. Handles both 2-level idle frames (syrd-S-F.tga)
    and 1-level make frames (syrdmake-N.tga); .meta sidecars come along.'''
    rx = re.compile(re.escape(old), re.IGNORECASE)
    with zipfile.ZipFile(src_zip) as s, zipfile.ZipFile(dst_zip, "w", zipfile.ZIP_DEFLATED) as d:
        for info in s.infolist():
            data = s.read(info.filename)
            ni = zipfile.ZipInfo(rx.sub(new, info.filename), info.date_time)
            ni.external_attr = info.external_attr
            ni.compress_type = zipfile.ZIP_DEFLATED
            d.writestr(ni, data)


def clone_tileset(content, ra, td, source=None):
    '''Clone every <Tile> block named `ra` (found in `source`, default `content`)
    into a `td` block in `content`, repointing the `ra\\ra-` frame path prefix
    to `td\\td-` (so it loads our copied ZIP).'''
    ra_l, td_l = ra.lower(), td.lower()
    content = re.sub(rf"[ \t]*<Tile>\s*<Key>\s*<Name>{td}</Name>.*?</Tile>\n", "", content, flags=re.DOTALL)
    blocks = re.findall(rf"[ \t]*<Tile>\s*<Key>\s*<Name>{ra}</Name>.*?</Tile>\n",
                        content if source is None else source, flags=re.DOTALL)
    if not blocks:
        raise SystemExit(f"no <Name>{ra}</Name> tiles in {Path(asset_packs.tileset_xml(ra, 'STRUCTURES')).name}")
    new = "".join(b.replace(f"<Name>{ra}</Name>", f"<Name>{td}</Name>")
                   .replace(f"{ra_l}\\{ra_l}-", f"{td_l}\\{td_l}-") for b in blocks)
    m = re.search(r"\n[ \t]*</Tiles>", content)
    return content[:m.start()] + "\n" + new.rstrip("\n") + content[m.start():], len(blocks)


def copy_art(ra, td):
    '''Extract <ra>.ZIP from the RA MEG and write <td>.ZIP (renamed) under its tree's STRUCTURES/.'''
    tmp = Path(tempfile.gettempdir()) / f"_ra_{ra}.zip"
    if not extract_named_zip(RA_MEG, f"{ra}.ZIP", tmp):
        raise SystemExit(f"{ra}.ZIP not found in {RA_MEG}")
    dst = Path(asset_packs.art_zip(td, "STRUCTURES"))
    dst.parent.mkdir(parents=True, exist_ok=True)
    repack_prefix(tmp, dst, ra, td)
    tmp.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ra"); ap.add_argument("td")
    ap.add_argument("--build-icon", required=True)
    ap.add_argument("--text-name", required=True)
    ap.add_argument("--text-desc", required=True)
    a = ap.parse_args()
    # idle + MAKE buildup art
    copy_art(a.ra, a.td)
    copy_art(a.ra + "MAKE", a.td + "MAKE")
    # tilesets: the MAKE layer shares its building's tileset XML
    dst = Path(asset_packs.tileset_xml(a.td, "STRUCTURES"))
    src = Path(asset_packs.tileset_xml(a.ra, "STRUCTURES"))
    source = None if src == dst else src.read_text(encoding="utf-8")
    xml = dst.read_text(encoding="utf-8")
    xml, n1 = clone_tileset(xml, a.ra, a.td, source)
    xml, n2 = clone_tileset(xml, a.ra + "MAKE", a.td + "MAKE", source)
    dst.write_text(xml, encoding="utf-8", newline="\n")
    # sidebar cameo + name
    patch_rabuildables_xml(a.td, a.text_name, a.text_desc, a.build_icon)
    print(f"  {a.td}: idle ZIP + {n1} tiles, MAKE ZIP + {n2} tiles, cameo {a.build_icon}")


if __name__ == "__main__":
    main()
