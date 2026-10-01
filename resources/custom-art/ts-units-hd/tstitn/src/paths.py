"""where the scripts find things: this folder (the model and the renderer) and Luke's hand-off folders (TS's own
art, the mod's current frames, the reference frames).  Set TITAN_HANDOFF to the hand-off's root folder (the one
holding 01-TSTITN/ and 00-TSHARV-example/)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
HANDOFF = os.environ.get('TITAN_HANDOFF', os.path.join(HERE, '..', '..', 'ts-units-hd-handoff'))
