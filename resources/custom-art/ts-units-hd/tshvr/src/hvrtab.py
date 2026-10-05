"""hvrtab.py - the Hover MLRS's tab on the units review page, from its package: the TS | v1 | vN sheet and the turning
GIFs, then the tab (in its old place) with the package's previews.  Prints the files map for the publish.

    python3 hvrtab.py PKG version shape_hull final_hull
"""
import os
import json, os, sys
sys.path.insert(0, os.environ.get('REVIEW', 'units-review'))
import addtab
import hvrlook
import hvrspec2 as spec
import hvrpkg

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = ['gif/hvr-turn.gif', 'img/hvr-8-facings.png', 'img/hvr-scale.png']


if __name__ == '__main__':
    pkg, ver, shape_hull, final_hull = sys.argv[1:5]
    tmp = os.path.join(HERE, 'logs')
    pv = pkg + '/previews'
    fmt = pkg + '/frames/tshvr-%04d.png'
    hvrlook.sheet(tmp + '/prev-new.png', fmt, [4, 12, 20, 28], 2.5, ver, seat=lambda f: spec.seat(f)[1:])
    hvrpkg.unit_gif(spec, fmt, tmp + '/page-turn.gif', scale=1.0)
    note = open(os.path.join(HERE, 'tab_note.txt')).read().strip()
    figs = [
        ('Turning, all 32 facings', 'in-mod · HD · 120 ms',
         "The mod's frames as they lie on their canvas (its seat tables not applied) beside HD, the rack seated on the "
         "pad.", tmp + '/page-turn.gif', 'hvr-turn-%s.gif' % ver,
         "The Hover MLRS turning through its 32 facings: the mod's frames and HD %s" % ver),
        ('The rack turning on its pad', '%s · hull 28 · rack 32-63 · 120 ms' % ver,
         "The hull still, the rack's 32 frames in turn, seated by the hull's facing: it pivots about the pad's centre. "
         "The pad is the hull's, so it never moves.", pv + '/rack-turn.gif', 'hvr-rack-turn-%s.gif' % ver,
         'The Hover MLRS %s rack turning on its pad' % ver),
        ('The pad', '%s · 5x · four facings' % ver,
         "Hull and rack together: the light grey pad between the yellow sides, centred across the hull, the support on "
         "its step holding the pods up.", pv + '/pad-closeup.png', 'hvr-pad-%s.png' % ver,
         'The Hover MLRS %s pad between the pontoons at 5x' % ver),
        ('The pods', '%s · 5x · four facings' % ver,
         "The pods' dark faces with two rows of four tubes, each with a red-tipped missile; the ochre collars and back "
         "bands, the antennas.", pv + '/rack-closeup.png', 'hvr-pods-%s.png' % ver,
         'The Hover MLRS %s missile pods at 5x' % ver),
        ('TS, v1 and %s' % ver, 'four facings',
         "TS as the mod draws it now and v1, their racks where their frames have them; %s with the rack seated on the "
         "hull's back." % ver, tmp + '/prev-new.png', 'hvr-v1-%s.png' % ver, 'The Hover MLRS: TS, v1 and %s' % ver),
        ('8 facings', 'in-mod · HD', "Every fourth facing, the mod's frames beside the HD frames of the same numbers.",
         pv + '/8-facings.png', 'hvr-8-facings-%s.png' % ver,
         "The Hover MLRS in 8 facings: the mod's frames and HD %s" % ver),
        ('Shape against TS', 'overlap %s flat · %s finished (hull)' % (shape_hull, final_hull),
         "TS's voxels and the model drawn flat in the mod's camera: red is TS's only, blue the model's only. The hull's "
         "and the rack's every eighth facing.", pv + '/shape-8-facings.png', 'hvr-shape-%s.png' % ver,
         "TS's voxels against the Hover MLRS %s model drawn flat" % ver),
        ('Scale', 'as the game draws them', 'Next to the HD harvester on one ground line.',
         pv + '/scale.png', 'hvr-scale-%s.png' % ver, 'The Hover MLRS %s beside the HD harvester' % ver),
    ]
    added = addtab.add('hvr', 'Hover MLRS', 'HVR.VXL + HVRTUR.VXL · TSHVR in the mod', note, figs, status=ver,
                       chg=ver, keep_place=True)
    files = {p: os.environ.get('REVIEW', 'units-review') + '/' + p for p in added}
    for p in OLD:
        files[p] = None
    print(json.dumps(files, indent=1))
