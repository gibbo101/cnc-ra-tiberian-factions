"""Previews, README, muzzle.txt, src and zips for the dug-in Tick Tank: nodeliver.py with this folder's modules first
(the units chat's renderer, not the buildings' copies of the same names).
    python3 tickdeliver.py previews | readme | muzzle | src | zip | all"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [p for p in (os.path.join(HERE, 'src'), HERE) if os.path.isdir(p)]
if os.path.isdir('/home/claude/work/r'):
    sys.path.append('/home/claude/work/r')            # nodeliver.py, bdeliver.py, ypreview.py
import nodeliver as ND
import tickspec as S

if __name__ == '__main__':
    what = sys.argv[1]
    pk = ND.NodPack(S.SPEC)
    if what in ('previews', 'all'):
        pk.previews()
    if what in ('readme', 'all'):
        pk.readme()
    if what in ('muzzle', 'all', 'readme'):
        S.write_muzzle()
    if what in ('src', 'all'):
        pk.src()
    if what in ('zip', 'all'):
        pk.zipit()
