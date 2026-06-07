#!/usr/bin/env python3
"""
PARKED 2026-06-07 — saved for the future Steam Deck testing session.

Repurpose the RA Mission Select page into 4 custom-campaign tabs
(Allies / Soviets / GDI / Nod). This script captures the two CONFIG.MEG edits we
worked out tonight so they can be re-applied and tested properly on the Deck.

STATUS / WHY PARKED
  The ROSTER edits (hide originals / re-tab via Variant) CRASH the DESKTOP
  launcher: EXCEPTION_ACCESS_VIOLATION in ClientG.exe at 0056A539 while building
  Mission Select, deterministically, for ANY ShowOnMissionSelect=false (both the
  territory-map Allied/Soviet tabs and the list Counterstrike/Aftermath tabs).
  meg_pack is proven clean (byte-identical round-trip), and our other CONFIG
  edits load fine, so it's a Deck-vs-desktop divergence (likely campaign-progress
  save state, or a different ClientG build). The research (docs/campaign-tabs-
  research.md) hid 3 missions FINE on the DECK. => retest on the Deck first.
  See memory: project-missionselect-roster-poc.

  The TAB ICONS (GDI/Nod emblems on the tabs) live in frontend_atlas_build.py
  (ENABLE_MISSIONSELECT_TABS flag, also parked). The icon swap itself worked
  in-game; it's parked only so we don't ship faction tabs pointing at the wrong
  (original) missions before the roster is sorted.

WHAT THIS SCRIPT DOES (when run)
  1. TITLES  — rename the campaign-tab title strings in MASTERTEXTFILE_EN-US.LOC
     ("Allied Expansions Campaign" -> "GDI Campaign", "Soviet Expansions
     Campaign" -> "Nod Campaign"). SAME-LENGTH in-place edit (the .LOC is
     size-locked; trailing-pad to keep centring; symmetric pad renders off-centre
     because the launcher keeps leading spaces / trims trailing). This part is
     SAFE and was verified in-game.
  2. ROSTER  — (the crashing part) hide originals + place missions per tab via the
     <Instance> Variant attribute. INSTANCES.XML is NOT size-locked.
       tab -> Variant:  Allied=Mobius_Allied_Campaign_Base,
       Soviet=Mobius_USSR_Campaign_Base, GDI(=Aftermath tab)=
       Mobius_Aftermath_Allied_Map_Base, Nod(=Counterstrike tab)=
       Mobius_*_Counterstrike_Map_Base.
     Visibility=<ShowOnMissionSelect>; always-show=<IsUnlockedAtStart>true.
     NOTE: prefer INJECTING NEW instances over re-tabbing existing ones (research
     proved injection displays; re-tab was never cleanly tested before the hide
     crashed). LAUNCH wiring of a placed mission is still unproven.

USAGE (Deck session)
  python3 scripts/build_missionselect_campaigns.py titles  <in.LOC>  <out.LOC>
  python3 scripts/build_missionselect_campaigns.py roster   <in.XML>  <out.XML>
  then repack into the mod CONFIG.MEG with the FULL inner path to avoid the
  meg_pack suffix gotcha (a bare "INSTANCES.XML" also clobbers AUDIO_INSTANCES.XML):
    python3 scripts/meg_pack.py repack <CONFIG.MEG> <out> \
        "DATA\\XML\\INSTANCES.XML=<edited.XML>"
    python3 scripts/meg_pack.py repack <CONFIG.MEG> <out> \
        "MASTERTEXTFILE_EN-US.LOC=<edited.LOC>"
"""
import sys, re

TITLE_EDITS = [
    # (old 26-char string, new text) -- pad TRAILING only to keep it centred
    ("Allied Expansions Campaign", "GDI Campaign"),
    ("Soviet Expansions Campaign", "Nod Campaign"),
]

# tab -> Variant (the attribute that binds an <Instance> to a Mission Select tab)
TAB_VARIANT = {
    'allied': 'Mobius_Allied_Campaign_Base',
    'soviet': 'Mobius_USSR_Campaign_Base',
    'gdi':    'Mobius_Aftermath_Allied_Map_Base',      # the Aftermath tab (tab 3)
    'nod':    'Mobius_Allied_Counterstrike_Map_Base',  # the Counterstrike tab (tab 4)
}
# all 4-tab variant groups (for hiding originals)
TAB_VARIANT_GROUPS = {
    'Mobius_Allied_Campaign_Base', 'Mobius_USSR_Campaign_Base',
    'Mobius_Aftermath_Allied_Map_Base', 'Mobius_Aftermath_USSR_Map_Base',
    'Mobius_Allied_Counterstrike_Map_Base', 'Mobius_USSR_Counterstrike_Map_Base',
}


def do_titles(src, dst):
    d = bytearray(open(src, 'rb').read()); orig = len(d)
    for old, new in TITLE_EDITS:
        assert len(new) <= len(old)
        newpad = new.ljust(len(old))                 # trailing pad -> stays centred
        ob = old.encode('utf-16-le'); nb = newpad.encode('utf-16-le')
        i = d.find(ob)
        assert i >= 0 and d.find(ob, i + 1) < 0, f'{old!r} not unique/found'
        d[i:i + len(ob)] = nb
        print(f'title: {old!r} -> {newpad!r}')
    assert len(d) == orig, 'LOC size changed (must stay same length!)'
    open(dst, 'wb').write(d)


def do_roster(src, dst, poc=None):
    """poc: dict {InstanceName: target_variant} to place; everything else in the
    4 tab groups is hidden. Default = the 4-mission Allied 1/2/3A/4 POC."""
    if poc is None:
        poc = {
            'Mobius_Allied_Campaign_1_Map':  TAB_VARIANT['allied'],
            'Mobius_Allied_Campaign_2_Map':  TAB_VARIANT['soviet'],
            'Mobius_Allied_Campaign_3A_Map': TAB_VARIANT['gdi'],
            'Mobius_Allied_Campaign_4_Map':  TAB_VARIANT['nod'],
        }
    doc = open(src, encoding='utf-8', errors='ignore').read()
    blocks = re.findall(r'<Instance\b.*?</Instance>', doc, re.S)
    va = lambda b: (re.search(r'<Instance[^>]*\bVariant="([^"]*)"', b) or [None, None])[1]
    na = lambda b: (re.search(r'<Instance[^>]*\bName="([^"]*)"', b) or [None, None])[1]
    def set_show(b, v):
        return re.sub(r'<ShowOnMissionSelect>\s*\w+\s*</ShowOnMissionSelect>',
                      f'<ShowOnMissionSelect>{v}</ShowOnMissionSelect>', b, count=1)
    def set_unlock(b):
        if '<IsUnlockedAtStart>' in b:
            return re.sub(r'<IsUnlockedAtStart>\s*\w+\s*</IsUnlockedAtStart>',
                          '<IsUnlockedAtStart>true</IsUnlockedAtStart>', b, count=1)
        return b.replace('</ShowOnMissionSelect>',
                         '</ShowOnMissionSelect>\n\t\t<IsUnlockedAtStart>true</IsUnlockedAtStart>', 1)
    def set_variant(b, nv):
        return re.sub(r'(<Instance[^>]*\bVariant=")[^"]*(")', rf'\g<1>{nv}\g<2>', b, count=1)
    hid = 0; placed = []
    for b in blocks:
        nb = b
        if va(b) in TAB_VARIANT_GROUPS and '<ShowOnMissionSelect>' in b:
            nb = set_show(nb, 'false'); hid += (nb != b)
        if na(b) in poc:
            nb = set_show(nb, 'true'); nb = set_unlock(nb); nb = set_variant(nb, poc[na(b)])
            placed.append(na(b))
        if nb != b:
            doc = doc.replace(b, nb, 1)
    open(dst, 'w', encoding='utf-8').write(doc)
    print(f'roster: hidden {hid}, placed {placed}')


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'titles':
        do_titles(sys.argv[2], sys.argv[3])
    elif mode == 'roster':
        do_roster(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(1)
