"""TS camera helpers for the Sensor Array (GTDPSA: a 1x1 building in a 96x96 frame, ground centre (48, 60))."""
import tsgeo as G
G.GX, G.GY = 48.0, 60.0
G.TSDIR = '/home/claude/work/ts/ts-buildings-hd-handoff/14-TSDPSA/ts-original/'
from tsgeo import proj, unproj_z, unproj_x, unproj_y, load, wire, box3, KZ
