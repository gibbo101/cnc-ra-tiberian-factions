TS Nod wall (NAWALL / NTWALL.SHP) rebuilt for Red Alert Remastered (HD, 128x128 per cell, the frame is the cell).
Made the same way as the TS GDI wall (ts-gdi-wall-hd), so the two sit side by side.

frames/nod-wall-NN.png   64 frames, same order as BRIK and the GDI wall:
    0-15  healthy          frame = N*1 + E*2 + S*4 + W*8
    16-31 damaged          (+16)  chipped edges, cracks, scorch, grime - the whole shape still stands
    32-47 heavily damaged  (+32)  chunks out of the tops, buttresses snapped, debris
    48-63 rubble           (+48)  broken stumps where it joins its neighbours (TS's heavily damaged frames);
                                  48 (no neighbours) is empty, like BRIK's
Transparent PNG, shadow baked in at ~75% black like BRIK. Damage colours are greys and browns only.
No house colour: NTWALL has no green/remap pixels, so there is no mask.

The shape (measured from the TS sprites; previews/ts-vs-ra.png shows the 3D rebuild seen from TS's own
camera next to the originals):
  arms      thin dark wedges along each connection, tallest where two cells meet and sloping down to a
            low point at the cell centre (TS shows these as the "boxes" at the front and ramps at the back)
  buttress  on the sides with no connection: a triangular fin peaking at the centre and running down
            to the ground near the cell edge. A straight run gets one at every cell. From RA's
            top-down camera the TS "X" is really a "+".
  corners   one buttress on the diagonal instead; the post and dead ends keep a capped arm, as in TS
  finish    dark grey concrete, pale drips on the faces either side of every joint, seams at the joints
Heights keep TS's proportions, scaled so the joints stand about as tall as the GDI wall's arms.
The south arm of a cell continues into the next cell a little (tall things poke up the screen in RA),
exactly like BRIK and the GDI wall, so the frames join without gaps.

end-pieces/ts-nod-wall/end-nod-{N,E,S,W}-{ok,damaged,destroyed}.png
  Joins any of the six gates (cnc-gates-hd v2) to a Nod wall. Same rules as the other end pieces:
  draw order N piece, gate, then W / E / S pieces; walls next to a gate count the gate's end cell as
  a neighbour. The S piece also draws the start of the wall continuing south.

previews/
  test-maps.png                  ring, T's, runs, post: healthy, mixed damage, and the GDI wall for scale
  ts-vs-ra.png                   TS original / 3D rebuild in TS's view / the RA frame
  all-64-frames.png              every frame
  all-gates-*-nod-wall.png       all six gates joined to the Nod wall

src/  Python 3 with numpy, scipy, Pillow
  python3 nodwall.py          -> nod/out/nod-wall-00..15.png
  python3 noddamage.py 1 2 3  -> nod/out/nod-wall-16..63.png
  python3 nodends.py          -> gates/out2/end-nod-*.png
  Shape and colours are the P dict and constants at the top of nodwall.py. nod/tsview.py, hyp.py and
  fit.py are the TS-view renderer and the fit used to measure the shape.
