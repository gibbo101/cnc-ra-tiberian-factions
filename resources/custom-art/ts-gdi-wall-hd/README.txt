TS GDI concrete wall rebuilt for Red Alert Remastered (HD, 128x128 per cell, the frame is the cell).

frames/gdi-wall-NN.png   64 frames, same order as BRIK:
    0-15  healthy          frame = N*1 + E*2 + S*4 + W*8
    16-31 damaged          (+16)
    32-47 heavily damaged  (+32)
    48-63 rubble           (+48; 48 is empty, like BRIK's)
Transparent PNG, shadow baked in at ~75% black like BRIK.

src/  the generator (Python 3, numpy, scipy, Pillow)
    python3 walls2.py        -> out2/gdi-wall-00..15.png
    python3 damage.py 1 2 3  -> out2/gdi-wall-16..63.png
    Shape, colours and positions are the P dict and constants at the top of walls2.py.
