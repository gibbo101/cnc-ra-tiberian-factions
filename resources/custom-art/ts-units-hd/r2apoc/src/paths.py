"""where the scripts find things: this folder and Luke's hand-off folders (RA2's voxels, the mod's frames, the harvester
example, EA's reference).  Set TS_HANDOFF to the hand-off's root folder (the one holding 27-R2APOC/, 00-TSHARV-example/ and
renderer/)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
HANDOFF = os.environ.get('TS_HANDOFF', os.path.join(HERE, '..', '..', 'ts-units-hd-handoff'))
