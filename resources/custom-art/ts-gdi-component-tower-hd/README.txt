Tiberian Sun GDI Component Tower (GACTWR) rebuilt for Red Alert Remastered (HD).

CANVAS  every frame is 176x320 px. The cell is the centred 128x128 square (x 24-152, y 96-224) and the
        cell's ground centre is at (88, 160); the tower rises above its cell.
CAMERA  a real (orthographic) camera 32 degrees above the ground, looking north - TS's own view is 30
        degrees looking north-west, so this is the original turned 45 degrees to sit on the square grid.
        Lit and shadowed like the TS GDI wall (shadow baked in at ~75% black, same light, same outline).
COLOUR  green = house colour, kept green. *-trim.png marks it (white = house colour) if you prefer a mask.

tower/component-tower-00.png   healthy
tower/component-tower-01.png   damaged    (a bite out of the top plate and ring, chips, cracks, scorch)
tower/component-tower-02.png   destroyed  (a hollow broken shell, braces snapped, plate and ring in pieces)
    Damage is greys and browns; only the ring's pieces stay green.

couplings/coupling-{N,E,S,W}-{00,01,02}.png
    The generic wall coupling for one side: a khaki sleeve (the tower's paint, a steel lip round its mouth)
    hugging the foot of the tower where the braces come down, the same on all four sides - TS's connectors
    are not extended either - on a low sill, with a short steel beam back into the tower. Its cross-section
    is a trapezoid like the GDI wall's, a little bigger all round than the end of a GDI, Nod or RA concrete
    wall, so whichever wall arrives runs into it.
    Draw it on top of the tower (same position, same canvas) for each side that has a wall next to it -
    any kind of wall on any side. No wall on that side: draw nothing (the tower stands clean). Another
    component tower on that side gets a link instead (links/, below).
    Use the set that matches the tower frame (00 / 01 / 02).
    East and west, the sleeve sits on the cell edge and reaches ~9 px over the end of the wall; north, the
    tower hides the joint. Both rely on RA's usual order: walls (overlays) drawn with the map, buildings on
    top of them. The wall next to the tower has to count the tower as a neighbour, so its arm reaches the
    cell edge.

ends/end-{gdi,nod,brik}-{N,S}-{00,01,02}.png
    North and south, the wall comes into the tower's cell up to the sleeve: these are those bits of wall,
    one set per kind of wall (gdi = TS GDI wall, nod = TS Nod wall, brik = RA concrete), like the gates'
    end pieces. GDI and Nod are rendered like their walls; the concrete ones are cut from BRIK's own HD
    frames, so they match exactly (and sit a little left of centre, as BRIK's north-south run does).
    S: from the cell edge into the sleeve's mouth. Draw it after the couplings, the set matching the wall
       to the south.
    N: from the cell edge to the middle of the sleeve. Draw it before the tower, the set matching the
       wall to the north - the tower hides most of it, but it fills the gap behind the destroyed tower.
    00 / 01 / 02 follow the tower. East and west need none (the sleeve sits on the cell edge).

links/link-{N,E,S,W}-{00,01}-{00,01}.png
    Towers next to towers. Two component towers side by side share one sleeve: each one's wall sleeve runs
    out to the cell edge between them and the two halves are bolted together there with a steel flange; a
    steel beam comes out of each tower into it and a sill runs underneath from pad to pad. No wall between
    them. East-west the towers' own sleeves already sit on that edge, so it is just the coupling's sleeve
    closed at both ends; north-south the sleeves reach further to meet, because the camera foreshortens the
    tower and a cell is deeper than the tower that way.
    link-<side>-<this tower's frame>-<the other tower's frame>.png, <side> = where the other tower is, and
    the frames are RA's two states, 00 healthy and 01 damaged: link-E-00-01 is for a healthy tower with a
    damaged tower to its east.
    Draw it on top of the tower after the couplings, for each side with a finished component tower next to
    it - instead of a coupling on that side, and no end piece.
    Both towers draw it. It is one link, rendered with both towers in their states and cut to each tower's
    canvas, so it doesn't matter which of the two RA draws last (two buildings in the same row can come in
    either order): the last one lays the whole link over the other's frame and shadow, and the two agree
    pixel for pixel where they overlap. The link's outline and shadow are only in the W and N pieces (the east or
    south tower's), cut back where the towers' own shadows already fall, so they come out the same either
    way round.
    While a tower is still building (or being sold), its neighbour treats its cell as empty.

    Per side of each tower, then:
        a wall next to it                       coupling-<side> (+ that wall's end piece, north and south)
        a gate running into it end-on           the same as a TS GDI wall: coupling-<side> (+ end-gdi-N /
                                                end-gdi-S); and the gate counts the tower as a TS GDI wall,
                                                drawing its ts-gdi-wall end piece at that end (cnc-gates-hd)
        a finished component tower next to it   link-<side>-<this tower's frame>-<that tower's frame>
        anything else (the side of a gate too)  nothing

    Gates: east-west, a tower and a gate in the same row can come in either order. Tower last, its sleeve
    covers the start of the gate's wall stub, as with a wall; gate last, the stub's collar sits against the
    end of the sleeve. Joined either way. North-south the order is fixed and it always comes out the same.
    Works with all six gates (preview-towers-and-gates).

build-up/component-tower-build-00..16.png   (+ -trim.png)
    TS's sequence over 17 frames: the pad grows (0-5), the steel frame rises (6-9), the body is clad over
    it (10-12), the top plate goes on (13), it is painted (14-15), the house-colour ring comes on (16).
    Frame 16 is the finished tower (= component-tower-00). Couplings and links go on once it is built.

light/component-tower-light-00..05.png
    The small blinking lamp at the foot of the south-east door (TS's GTCTWR_A), as overlay frames on the
    same canvas, following TS's brightness frame by frame. Play it on top of the tower.

Draw order: walls (overlays) first as usual, then the north end piece, the tower, its couplings,
its links, the south end piece, then the lamp.

The shape was measured from the TS sprites: a 3D rebuild seen from TS's own camera covers ~91% of the
TS tower's outline. Square khaki body with cut corners (dark recesses; a door and the lamp on the
south-east one), eight braces from the top of the corners down beside each coupling (TS's "A" legs), a
round blue-grey top plate with four bolt holes (N/E/S/W) and the green ring where a weapon plug sits.

previews/   the tower on its own, with GDI walls on all four sides, in an L and a T, next to a GDI wall
            run for scale, with different walls on different sides, the three states, the build-up,
            and side by side with TS's own tower and build-up (tower-vs-original, build-up-vs-original)
            Nod and RA concrete walls coming in north and south in the three states (preview-nod-and-concrete)
            towers next to towers: pairs, a block, rows and columns, with walls (preview-towers-linked),
            every pair of states both ways (preview-towers-linked-states), and the links up close, drawn
            in either order (preview-towers-linked-close); next to each of the six gates, east-west both
            ways round and north-south (preview-towers-and-gates)
src/        Python 3 (numpy, scipy, Pillow):  python3 ct_all.py tower | couplings 0 1 2 | ends | build 0 .. 16
            python3 ct_preview.py   (the concrete pieces and previews read RA's BRIK frames from ref/ and
            ref-dmg/, and the previews read the GDI/Nod wall frames from out2/ and nod/out/)
            python3 ct_link.py EW 00 01 10 11   and the same with NS: the links, each argument the two
            towers' frames (west or north one first); reads the tower frames from ctwr/out
            python3 ct_preview.py links   (just the tower-to-tower previews)
            python3 ct_gates_preview.py   (towers next to gates; reads the gate frames from gates/out2-4)
