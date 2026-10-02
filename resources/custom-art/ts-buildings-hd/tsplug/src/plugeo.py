"""TS camera helpers for the Upgrade Center (GTPLUG: a 2x3 building in a 144x120 frame, ground centre (60, 90))."""
import tsgeo as G
G.GX, G.GY = 60.0, 90.0
G.TSDIR = '/home/claude/work/ts/ts-buildings-hd-handoff/12-TSPLUG/ts-original/'
from tsgeo import proj, unproj_z, unproj_x, unproj_y, load, wire, box3, KZ
