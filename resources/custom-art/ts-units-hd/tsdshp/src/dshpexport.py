"""the TS Dropship's 3D model as a .glb (vexport): the hull, the mod's camera.

    python3 dshpexport.py out.glb
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dshpspec as S

if __name__ == '__main__':
    S.GLB(sys.argv[1])
