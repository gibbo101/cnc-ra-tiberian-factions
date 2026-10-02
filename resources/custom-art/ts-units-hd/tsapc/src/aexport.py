"""the Amphibious APC's 3D model as a .glb: the land hull and the water hull (TS swaps them), the mod's camera.

    python3 aexport.py out.glb
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vexport as VE
import arender as AR

if __name__ == '__main__':
    land, water = AR.load()
    print(VE.export(sys.argv[1], 'AmphibiousAPC', [('land_hull', land, 0)], AR.camera(), AR.CANVAS, AR.PPU))
    print(VE.export(sys.argv[1].replace('.glb', '-water.glb'), 'AmphibiousAPC_water', [('water_hull', water, 0)],
                    AR.camera(AR.ORIGIN_WATER), AR.CANVAS, AR.PPU))
