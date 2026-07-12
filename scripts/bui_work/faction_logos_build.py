#!/usr/bin/env python3
"""
WIP (2026-07-11): build RA_TACTICAL_UI.BUI with 4 distinct per-faction HUD radar
logos (Allied / GDI / Nod / Soviet). See docs/bui-front-end-modding.md
"Per-faction HUD logos" section.

STATUS: builds + fits the size budget, BUT the deployed result makes the WHOLE
IN-GAME SIDEBAR DISAPPEAR (Deck-tested GDI). The game does NOT crash — it renders
the tactical view full-screen with no sidebar. Diagnosis: inserting the two new
widget chunks (+602 bytes) shifts everything after the faction-logo group, and a
PARENT chunk bounds its children by a size/count field that this script does NOT
yet update -> ChunkFile mis-parses the rest of Side_Bar_Group and drops it.

NEXT STEP (the one missing piece): find the parent chunk that encloses the
faction-logo group (candidates: Side_Bar_Group @864, AspectRatio_Group, Tactical_UI)
and update its size/child-count field(s) by the inserted byte count (and likely a
+2 child count). Then re-test. The RE workflow (chunkfile-insertion-format agent)
was rate-limited before finishing — re-run it next session.

WHAT WORKS / IS KNOWN (so we don't re-derive):
- ClientG selects the sidebar logo by widget NAME keyed on the compiled FactionType
  enum, and looks for FIVE names: SideBar_FactionLogo_{GDI,NOD,Allies,Soviet,DINO}.
  RA_TACTICAL_UI.BUI only DEFINES _Allies and _Soviet -> GDI/Nod fall back to the
  generic "COMMAND & CONQUER" wordmark. Populate _GDI/_NOD to fix that.
- The REAL emblems are ALREADY in the mod's shipped in-game atlas: regions
  ui_sidebar_factionlogo_gdi (gold eagle) and _nod (red scorpion). So the new
  widgets just point at them (tint 1,1,1,1) for authentic art -- no new pixels.
- .bui string property layout: [u32 fieldsize = len+2][u16 len][ascii]. Widget
  header = '26 10' + 16 zero bytes + '2b 01 01' + '2c 01 01' + '05 00 00 00'
  (05 = property count). No per-widget total-size field.
- Same-size rule holds: recompress L9 must be <= 11071 (verified 10725), pad member
  to exactly 11107 bytes.
- Retinting the EXISTING _Allies (@4124) / _Soviet (@4439) tints is a safe in-place
  4-float edit (no size change); _Soviet retint is Deck-PROVEN to render.

OPEN PUZZLE (blocks confirming the mapping): in an earlier hide-test, editing the
_Soviet widget changed ONLY the Soviet faction, but editing _Allies changed NOTHING
(not even the Allies faction). So it's unconfirmed that the mod's Allies faction
resolves to _Allies, and whether GDI/Nod resolve to _GDI/_NOD. Couldn't observe it
here because the sidebar didn't render at all. Resolve via the DLL FactionType /
FACTIONS.XML mapping (faction-to-widget-mapping agent) next session.

USAGE (once the parent-size fixup is added): python3 scripts/bui_work/faction_logos_build.py
Deploy/recovery: same as scripts/bui_work/hud_probe_build.py docstring.
"""
import os, sys, zlib, struct, subprocess, shutil

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MOD_MEG = os.path.join(REPO, 'dist', 'workshop-content', 'Vanilla_RA', 'Data', 'CONFIG.MEG')
EXTRACT = os.path.join(REPO, 'scripts', 'meg_extract.py')
PACK    = os.path.join(REPO, 'scripts', 'meg_pack.py')
WORK    = os.path.join(REPO, 'scripts', 'bui_work')
OUT_MEG = os.path.join(WORK, 'CONFIG.4logos.MEG')
MEMBER  = 'RA_TACTICAL_UI.BUI'

# per-faction appearance: (widget-name, texture-region, tint RGBA)
NEW_WIDGETS = [
    (b'SideBar_FactionLogo_GDI', b'ui_sidebar_factionlogo_gdi', (1.0, 1.0, 1.0, 1.0)),  # real gold eagle
    (b'SideBar_FactionLogo_NOD', b'ui_sidebar_factionlogo_nod', (1.0, 1.0, 1.0, 1.0)),  # real red scorpion
]
RETINT = {4124: (0.25, 0.55, 1.0, 1.0),   # existing _Allies -> blue
          4439: (1.0, 0.42, 0.06, 1.0)}   # existing _Soviet -> orange

def find_str_prop(block, s):
    i = block.find(s)
    assert i >= 6 and struct.unpack_from('<H', block, i-2)[0] == len(s) \
        and struct.unpack_from('<I', block, i-6)[0] == len(s)+2, f'bad str prop {s}'
    return i-6, i+len(s)

def make_widget(template, name, tex, tint):
    b = bytearray(template)
    for old, new in ((b'SideBar_FactionLogo_Allies', name), (b'ui_sidebar_factionlogo_allies', tex)):
        s, e = find_str_prop(b, old)
        b[s:e] = struct.pack('<I', len(new)+2) + struct.pack('<H', len(new)) + new
    # tint tag inside the block
    t = b.find(b'\x03\x10')
    struct.pack_into('<4f', b, t+2, *tint)
    return bytes(b)

def main():
    tmp = os.path.join(WORK, '_4logos_tmp'); os.makedirs(tmp, exist_ok=True)
    subprocess.run([sys.executable, EXTRACT, 'extract', MOD_MEG, MEMBER, tmp], capture_output=True)
    src = next(os.path.join(r, f) for r, _, fs in os.walk(tmp) for f in fs if f.upper() == MEMBER)
    d = open(src, 'rb').read(); ORIG = len(d); ORIGC = ORIG - 0x24
    raw = bytearray(zlib.decompress(d[0x24:]))

    template = bytes(raw[3868:4175])                      # the _Allies widget block
    new_blocks = b''.join(make_widget(template, n, t, tint) for n, t, tint in NEW_WIDGETS)
    for off, tint in RETINT.items():
        assert raw[off:off+2] == b'\x03\x10'
        struct.pack_into('<4f', raw, off+2, *tint)

    rm = raw.find(b'RadarMap', 4400)
    ins = raw.rfind(b'\x26\x10', 4175, rm)                # RadarMap's header = insertion point
    newraw = bytes(raw[:ins]) + new_blocks + bytes(raw[ins:])

    # !!! MISSING: update the enclosing parent chunk size/child-count by len(new_blocks) here !!!
    # Without it, the sidebar fails to render (see module docstring).

    comp = zlib.compress(newraw, 9)
    assert len(comp) <= ORIGC, f'overflow {len(comp)} > {ORIGC}'
    hdr = bytearray(d[:0x24]); struct.pack_into('<I', hdr, 0x10, len(comp))
    body = bytes(hdr) + comp
    edited = os.path.join(tmp, 'RA_TACTICAL_UI.4logos.BUI')
    open(edited, 'wb').write(body + b'\x00' * (ORIG - len(body)))

    shutil.copyfile(MOD_MEG, OUT_MEG)
    subprocess.run([sys.executable, PACK, 'repack', OUT_MEG, OUT_MEG + '.tmp', f'{MEMBER}={edited}'], capture_output=True)
    os.replace(OUT_MEG + '.tmp', OUT_MEG)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'wrote {OUT_MEG} (member {ORIG}B, +{len(new_blocks)}B inserted, comp {len(comp)}/{ORIGC})')
    print('WARNING: parent chunk-size fixup NOT applied -> sidebar will not render. WIP.')

if __name__ == '__main__':
    main()
