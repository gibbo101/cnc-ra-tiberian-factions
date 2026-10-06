"""orcavox.py - TS's Orca Fighter voxel (ORCA.VXL, one section) as data: its colours, its occupancy (the shell as TS
stores it) and its solid (the shell's closed hollows filled; the open ducts, the cockpit's pit and the nose's slit stay
open)."""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
from scipy.ndimage import binary_fill_holes

D = os.path.join(HANDOFF, '23-TSORCA', 'ts-original') + os.sep
SEC = vxl.read_vxl(D + 'ORCA.VXL')[0]
COL = SEC['col']
SHELL = COL >= 0
# the solid: TS's shell is open in places no camera sees - a slot in each pod's floor by the body (x 26..29) and the
# body's hollow running forward into the cockpit's pit - so those are capped for the fill, the pit (x 32..35, y 11..13)
# and the nose's slit (x 36..38, y 12) then opened again
_cap = SHELL.copy()
_cap[26:30, 7:10, 2] = True
_cap[26:30, 15:18, 2] = True
_cap[31:36, 11:14, 6] = True
_cap[36:39, 12, 5] = True
OCC = binary_fill_holes(_cap)
OCC[32:36, 11:14, 1:] = SHELL[32:36, 11:14, 1:]
OCC[36:39, 12, 3:] = SHELL[36:39, 12, 3:]
HOUSE = (COL >= 16) & (COL <= 31)
