"""where the scripts find things: this folder and Luke's hand-off folders (TS's voxel, the mod's frames, the
harvester example, EA's Mammoth) and the Titan package (for the scale preview).  Set TS_HANDOFF to the hand-off's root
folder (the one holding 03-TSHMEC/, 00-TSHARV-example/ and renderer/) and TITAN_FRAMES to the Titan package's frames/."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
HANDOFF = os.environ.get('TS_HANDOFF', os.path.join(HERE, '..', '..', 'ts-units-hd-handoff'))
TITAN_FRAMES = os.environ.get('TITAN_FRAMES', os.path.join(HERE, '..', '..', 'ts-titan-hd', 'frames'))
