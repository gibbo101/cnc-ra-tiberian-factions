"""otvoxd.py - TS's Orca Transport voxel (ORCATRAN.VXL, one section) as data: its colours, its occupancy (the shell as TS
stores it) and its solid (the shell's closed hollows filled; the open fan ducts stay open)."""
import os, sys
from paths import HANDOFF, OT_D
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
from scipy.ndimage import binary_fill_holes

D = OT_D
SEC = vxl.read_vxl(D + 'ORCATRAN.VXL')[0]
COL = SEC['col']
SHELL = COL >= 0
# the solid: TS's shell with its closed hollows filled (the ducts stay as TS has them; only silhouettes are compared)
OCC = binary_fill_holes(SHELL)
