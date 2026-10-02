"""where the scripts find things: this folder (the model and the renderer) and Luke's hand-off folders (TS's own
voxel, the mod's current frames, the harvester example, EA's MCVs).  Set TS_HANDOFF to the hand-off's root folder
(the one holding 11-TSMCV/, 00-TSHARV-example/ and renderer/)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
HANDOFF = os.environ.get('TS_HANDOFF', os.path.join(HERE, '..', '..', 'ts-units-hd-handoff'))
