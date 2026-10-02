"""the Disruptor's 3D model as a .glb (vexport): the hull and the turret, the mod's camera.

    python3 sonicexport.py out.glb
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vexport as VE
import sonicrender as R

if __name__ == '__main__':
    H, T = R.load()
    print(VE.export(sys.argv[1], 'Disruptor', [('hull', H, 0), ('turret', T, 0)], R.camera(), R.CANVAS, R.PPU))
