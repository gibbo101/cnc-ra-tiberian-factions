"""dshptab.py - the Dropship's tab on the units review page, from its package's previews: the tab (in its old place)
with the previews.  Prints the files map for the publish.

    python3 dshptab.py PKG version shape_game final_f0
"""
import json, os, sys
sys.path.insert(0, os.environ.get('REVIEW', 'units-review'))
import addtab

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = ['gif/dshp-facings-turn-v2.gif', 'img/dshp-closeups-v2.png', 'img/dshp-cockpit-v2.png', 'img/dshp-facings-v2.png',
       'img/dshp-scale-v2.png', 'img/dshp-shape-v2.png', 'img/dshp-ship-v2.png']


if __name__ == '__main__':
    pkg, ver, shape_game, final_f0 = sys.argv[1:5]
    pv = pkg + '/previews'
    note = open(os.path.join(HERE, 'tab_note.txt')).read().strip()
    figs = [
        ('The ship', 'in-mod · v2 · %s · overlap %s' % (ver, final_f0),
         "Frame 0, side-on and level facing west, as the game draws it: the mod's frame now, v2 (GDI's gold) and %s "
         "(house colour where TS has it)." % ver,
         pv + '/ship.png', 'dshp-ship-%s.png' % ver, "The TS Dropship facing west: the mod's frame, v2 and %s" % ver),
        ('The cockpit', '%s · beside the FMV' % ver,
         "One window the shape of Westwood's FMV's, on a flat plate in the nose's front above TS's lower lip, the "
         "housing carrying the plate up square and running smoothly into the nose; the FMV's slits either side. It "
         "faces forward, so frame 0 shows it as a sliver.", pv + '/cockpit.png', 'dshp-cockpit-%s.png' % ver,
         "The TS Dropship %s's cockpit beside Westwood's FMV" % ver),
        ('Close-ups', 'in-mod · %s · 3x' % ver,
         "The nose, the middle and the tail of frame 0: the mod's frame beside %s." % ver, pv + '/closeups.png',
         'dshp-closeups-%s.png' % ver, "The TS Dropship's nose, middle and tail at 3x: the mod's frame and %s" % ver),
        ('All 32 directions', '%s · 120 ms' % ver, 'The ship turning about the canvas centre, where the game puts the '
         'unit.', pv + '/facings-turn.gif', 'dshp-facings-turn-%s.gif' % ver,
         'The TS Dropship %s turning through its 32 directions' % ver),
        ('8 directions', 'every fourth facing', 'Counter-clockwise from north, as your other units: 0 N, 8 W, 16 S, '
         '24 E.', pv + '/facings.png', 'dshp-facings-%s.png' % ver, 'The TS Dropship %s in 8 directions' % ver),
        ('Shape against TS', 'overlap %s flat' % shape_game,
         "TS's voxels and the model drawn flat: red is TS's only, blue the model's only. The game's angle, the side, "
         "the top, the front and the back.", pv + '/shape.png', 'dshp-shape-%s.png' % ver,
         "TS's voxels against the TS Dropship %s model drawn flat" % ver),
        ('Scale', 'as the game draws them', "Next to EA's C-17 and Badger.", pv + '/scale.png',
         'dshp-scale-%s.png' % ver, "The TS Dropship %s beside EA's C-17 and Badger" % ver),
    ]
    added = addtab.add('dshp', 'Dropship', 'DSHP.VXL · TSDSHP in the mod', note, figs, status=ver, chg=ver,
                       keep_place=True)
    files = {p: os.environ.get('REVIEW', 'units-review') + '/' + p for p in added}
    for p in OLD:
        files[p] = None
    print(json.dumps(files, indent=1))
