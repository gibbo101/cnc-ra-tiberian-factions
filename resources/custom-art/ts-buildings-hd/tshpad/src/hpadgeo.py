"""TS camera helpers for the helipad (GTHPAD: 2x2 in a 96x96 frame; foundation centre at TS px (48, 72))."""
import tsgeo as G
G.GX, G.GY = 48.0, 72.0
G.TSDIR = '/home/claude/work/ts/ts-buildings-hd-handoff/08-TSHPAD/ts-original/'
from tsgeo import proj, unproj_z, unproj_x, unproj_y, load, wire, box3, KZ   # noqa
