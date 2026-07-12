#!/usr/bin/env python3
"""
W4 HUD PROBE — proves the .bui edit pipeline generalises from the main menu to
the in-game tactical HUD (docs/bui-front-end-modding.md).

WHAT IT DOES
  Builds a probe CONFIG.MEG (a copy of the mod's shipped CONFIG.MEG) in which
  RA_TACTICAL_UI.BUI has one same-length texture-ref swap:
      ui_sidebar_factionlogo_allies  ->  ui_sidebar_factionlogo_soviet
  Both are existing textures and the same length (29 bytes), so the decompressed
  payload length is unchanged -> zero size risk (cannot crash on the same-size
  rule). It recompresses at zlib L9, keeps the [0x08] header hash stale, and pads
  the member back to its exact original byte size.

EXPECTED RESULT ON THE DECK
  Play a skirmish as GDI (an Allied-based faction): the sidebar faction crest
  shows the SOVIET/Nod logo instead of the Allied/GDI one.
    - visible change  => .bui HUD editing works end-to-end (W4 proven).
    - no change       => wrong member / delivery issue (re-check).
    - boot crash      => size drift (should NOT happen for a same-length edit).
  This is a PROBE, not a feature — revert after observing.

USAGE
  python3 scripts/bui_work/hud_probe_build.py
    -> writes <repo>/scripts/bui_work/CONFIG.hud-probe.MEG

DEPLOY (only when you're at the Deck and ready to test; deploy to YOUR deck):
  scp scripts/bui_work/CONFIG.hud-probe.MEG \
    deck@steamdeck:/home/deck/.steam/steam/steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/CnCRemastered/Mods/Red_Alert/Vanilla_RA/Data/CONFIG.MEG

RECOVERY (restore the real mod CONFIG.MEG):
  scp dist/workshop-content/Vanilla_RA/Data/CONFIG.MEG \
    deck@steamdeck:/home/deck/.steam/steam/steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/CnCRemastered/Mods/Red_Alert/Vanilla_RA/Data/CONFIG.MEG
  (or just redeploy your normal build — the base install is never touched.)
"""
import os, sys, zlib, struct, subprocess, shutil

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MOD_MEG = os.path.join(REPO, 'dist', 'workshop-content', 'Vanilla_RA', 'Data', 'CONFIG.MEG')
EXTRACT = os.path.join(REPO, 'scripts', 'meg_extract.py')
PACK    = os.path.join(REPO, 'scripts', 'meg_pack.py')
WORK    = os.path.join(REPO, 'scripts', 'bui_work')
OUT_MEG = os.path.join(WORK, 'CONFIG.hud-probe.MEG')
MEMBER  = 'RA_TACTICAL_UI.BUI'
A = b'ui_sidebar_factionlogo_allies'
B = b'ui_sidebar_factionlogo_soviet'

def run(*a):
    r = subprocess.run([sys.executable, *a], capture_output=True, text=True)
    if r.returncode: sys.exit(f'command failed: {a}\n{r.stderr}')
    return r.stdout

def main():
    assert len(A) == len(B), 'swap strings must be equal length'
    assert os.path.exists(MOD_MEG), f'mod CONFIG.MEG not found: {MOD_MEG}'
    tmp = os.path.join(WORK, '_hud_probe_tmp'); os.makedirs(tmp, exist_ok=True)

    run(EXTRACT, 'extract', MOD_MEG, MEMBER, tmp)
    src = next(os.path.join(r, f) for r, _, fs in os.walk(tmp) for f in fs if f.upper() == MEMBER)
    d = open(src, 'rb').read(); orig = len(d)
    raw = bytearray(zlib.decompress(d[0x24:])); dlen = len(raw)
    assert raw.count(A) == 1, f'expected 1 {A!r}, found {raw.count(A)} — base BUI changed'
    raw = raw.replace(A, B)
    assert len(raw) == dlen, 'decompressed length changed — abort'
    comp = zlib.compress(bytes(raw), 9)
    assert len(comp) <= orig - 0x24, f'recompressed overflow {len(comp)} > {orig-0x24}'
    hdr = bytearray(d[:0x24]); struct.pack_into('<I', hdr, 0x10, len(comp))  # keep [0x08] hash stale
    body = bytes(hdr) + comp
    edited = os.path.join(tmp, 'RA_TACTICAL_UI.edited.BUI')
    open(edited, 'wb').write(body + b'\x00' * (orig - len(body)))
    assert os.path.getsize(edited) == orig

    shutil.copyfile(MOD_MEG, OUT_MEG)
    run(PACK, 'repack', OUT_MEG, OUT_MEG + '.tmp', f'{MEMBER}={edited}')
    os.replace(OUT_MEG + '.tmp', OUT_MEG)

    # validate
    run(EXTRACT, 'extract', OUT_MEG, MEMBER, tmp + '/verify')
    v = next(os.path.join(r, f) for r, _, fs in os.walk(tmp + '/verify') for f in fs if f.upper() == MEMBER)
    vd = open(v, 'rb').read(); vraw = zlib.decompress(vd[0x24:])
    ok = (os.path.getsize(OUT_MEG) == os.path.getsize(MOD_MEG) and len(vd) == orig
          and len(vraw) == dlen and vraw.count(A) == 0 and vraw.count(B) == 2)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'wrote {OUT_MEG}')
    print(f'  member {MEMBER}: {orig} bytes (unchanged), payload {dlen} bytes (unchanged), swap applied')
    print(f'  probe MEG size == mod MEG size: {os.path.getsize(OUT_MEG) == os.path.getsize(MOD_MEG)}')
    print('VALIDATION:', 'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
