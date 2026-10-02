"""the Orca Bomber's 3D model as a .glb (vexport): the hull, the mod's camera.

    python3 orcabexport.py out.glb
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vexport as VE
import orcabrender as R

if __name__ == '__main__':
    print(VE.export(sys.argv[1], 'OrcaBomber', [('hull', R.load(), 0)], R.camera(), R.CANVAS, R.PPU))
