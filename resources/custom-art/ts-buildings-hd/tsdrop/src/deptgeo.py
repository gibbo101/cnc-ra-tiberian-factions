"""TS camera helpers for the service depot (GTDEPT: 3x3 in a 144x144 frame; foundation centre at TS px (72, 108))."""
import tsgeo as G
G.GX, G.GY = 72.0, 108.0
G.TSDIR = TSDIR = '/home/claude/work/ts/ts-buildings-hd-handoff/10-TSDEPT/ts-original/'
from tsgeo import proj, unproj_z, unproj_x, unproj_y, load, wire, box3, KZ   # noqa
