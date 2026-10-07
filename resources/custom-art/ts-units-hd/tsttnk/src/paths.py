"""where the scripts find things: this folder and the hand-off folder (TS's voxels, the examples).  Set
TS_HANDOFF to the hand-off's root folder (the one holding 03-TTNK/ and examples/)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
HANDOFF = os.environ.get('TS_HANDOFF', os.path.join(HERE, '..', '..', 'ts-nod-units-hd-handoff'))
EA_UNITS = os.environ.get('EA_UNITS', os.path.join(HERE, '..', '..', 'RA + TD HD Units'))
