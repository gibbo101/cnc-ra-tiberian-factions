"""where the scripts find Luke's hand-off folders: set TS_HANDOFF to the hand-off's root folder (the one
holding 17-TSE1/, the other units' folders and renderer/)."""
import os
HANDOFF = os.environ.get('TS_HANDOFF', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ts-units-hd-handoff'))
