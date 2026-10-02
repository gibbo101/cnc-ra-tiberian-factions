"""where the scripts find things: this folder and Luke's hand-off folders (TS's sprites and voxel, the mod's frames, the
harvester example).  Set TS_HANDOFF to the hand-off's root folder (the one holding 04-TSJUGG/, 00-TSHARV-example/
and renderer/)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
HANDOFF = os.environ.get('TS_HANDOFF', os.path.join(HERE, '..', '..', 'ts-units-hd-handoff'))
