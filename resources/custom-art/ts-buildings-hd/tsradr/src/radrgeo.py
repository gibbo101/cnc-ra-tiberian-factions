"""TS camera helpers for the radar (GTRADR: 2x2 in a 144x144 frame; foundation centre at TS px (72, 96)).
Re-exports tsgeo with the radar's origin and folder."""
import tsgeo as G
G.GX, G.GY = 72.0, 96.0
G.TSDIR = '/home/claude/work/ts/ts-buildings-hd-handoff/07-TSRADR/ts-original/'
from tsgeo import proj, unproj_z, unproj_x, unproj_y, load, wire, box3, KZ   # noqa
