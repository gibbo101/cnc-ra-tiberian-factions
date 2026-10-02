"""the Mobile EMP Cannon's 3D model as a .glb (vexport): the hull, the mod's camera.

    python3 mempexport.py out.glb
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vexport as VE
import memprender as R

if __name__ == '__main__':
    print(VE.export(sys.argv[1], 'MobileEMP', [('hull', R.load(), 0)], R.camera(), R.CANVAS, R.PPU))
