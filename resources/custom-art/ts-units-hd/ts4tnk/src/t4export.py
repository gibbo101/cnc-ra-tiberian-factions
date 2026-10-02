"""the Mammoth Mk. I's 3D model as a .glb: the hull, and the turret with its barrels under a 'turret' node that turns
about the unit's position; the mod's camera.

    python3 t4export.py out.glb
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vexport as VE
import t4render as TR

if __name__ == '__main__':
    H, T = TR.load()
    print(VE.export(sys.argv[1], 'MammothMk1', [('hull', H, 0), ('turret', T, 0)], TR.camera(), TR.CANVAS, TR.PPU))
