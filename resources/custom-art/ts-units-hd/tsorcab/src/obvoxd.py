"""orcavox.py - TS's Orca Bomber voxel (ORCAB.VXL, one section) as data: its colours, its occupancy (the shell as TS
stores it) and its solid (the shell's closed hollows filled; the open ducts, the cockpit's pit and the nose's slit stay
open)."""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
from scipy.ndimage import binary_fill_holes

D = os.path.join(HANDOFF, '24-TSORCAB', 'ts-original') + os.sep
SEC = vxl.read_vxl(D + 'ORCAB.VXL')[0]
COL = SEC['col']
SHELL = COL >= 0
# the solid: TS's shell with its closed hollows filled (the ducts, the canopy's inside and the open bays stay as TS has
# them; only silhouettes are compared)
OCC = binary_fill_holes(SHELL)
