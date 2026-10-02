"""where the scripts find things: this folder (the model and the renderer) and Luke's hand-off folders (TS's own
art, the mod's current frames, the harvester example).  Set TS_HANDOFF to the hand-off's root folder (the one
holding 02-TSSMEC/ and 00-TSHARV-example/), and TITAN_FRAMES to the Titan package's frames/ for the scale preview."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
HANDOFF = os.environ.get('TS_HANDOFF', os.path.join(HERE, '..', '..', 'ts-units-hd-handoff'))
TITAN_FRAMES = os.environ.get('TITAN_FRAMES', os.path.join(HERE, '..', '..', 'ts-titan-hd', 'frames'))
