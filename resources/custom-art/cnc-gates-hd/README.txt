Gates for Red Alert Remastered, HD (128 px per cell). Every gate has plain ends; separate end pieces
join it to a wall, so each gate works with the TS GDI wall and with RA's own concrete wall (BRIK).
v2: the RA Allies, RA Soviets and TD GDI gates have been redesigned from each faction's own building style.
TS GDI, TS Nod and TD Nod are unchanged.

GATES   <gate>-h-NN.png  horizontal, 3x1 cells, 384x128     <gate>-v-NN.png  vertical, 1x3 cells, 128x384
        <gate>-...-trim.png  house-colour mask (white = house colour) for recolouring
  ts-gdi      TS GDI      ribbed panel in a trim frame, slides down into a slot          0-9 open, 10-19 damaged, 20 destroyed
  ts-nod      TS Nod      wall section with a dipped top, lowers into the ground         0-6 open,  7-13 damaged, 14 destroyed
  ra-allies   RA Allies   perimeter gate: a steel panel with house-colour chevrons and   0-9 open, 10-19 damaged, 20 destroyed
                          a hazard-striped top sinks into a concrete trench, between two
                          sensor pylons styled on the Gap Generator (round plinth with a
                          house-colour ring, slim column, white fin). Status lights: solid
                          blue shut, blinking amber while moving, solid green open.
  ra-soviets  RA Soviets  Tesla gate: two Tesla-coil pylons (red-trimmed rust concrete     0-9 open, 10-19 damaged, 20 destroyed
                          bases, copper coils, electrode balls) arc lightning across the
                          gap; the arcs weaken, flicker and die as it opens. Rusty concrete
                          apron with the black/white checker border of the SAM pad.
  td-gdi      TD GDI      a corrugated quonset-style barrier in GDI gold sinks into a     0-9 open, 10-19 damaged, 20 destroyed
                          hazard-striped trench between two white domed silo towers with
                          gold bands, on a rounded concrete pad
  td-nod      TD Nod      laser gate: black emitter pylons, three red beams that         0-9 open, 10-19 damaged, 20 destroyed
                          flicker and power down
  Trim baked in: gold (TS GDI, TS Nod, TD GDI), blue (Allies), red (Soviets, TD Nod). Use the masks to recolour.

  ra-soviets/idle-extra (optional)
    soviet-gate-{h,v}-idle-ok-{1,2,3}.png, soviet-gate-{h,v}-idle-damaged-{1,2,3}.png
    Same shut gate with the arcs re-rolled, so a shut Tesla gate can crackle instead of freezing on one frame:
    loop frame 0 -> idle-ok-1 -> idle-ok-2 -> idle-ok-3 (damaged: frame 10 -> idle-damaged-1..3).
    The house-colour mask for these is the one for frame 0 / frame 10 (the arcs are not house colour).

END PIECES  one cell each, 128x128:  end-pieces/<wall>/end-<wall>-{N,E,S,W}-{ok,damaged,destroyed}.png
  ts-gdi-wall        TS GDI wall stub with the other half of its ochre collar
  ra-concrete-wall   BRIK cut from BRIK's own frames: its straight run plus its own end cap
  Place them on a gate's end cells where a wall is next to that end:
    horizontal gate: W piece on its west cell, E piece on its east cell
    vertical gate:   N piece on its north cell, S piece on its south cell
  Pick the state to match the gate (ok / damaged / destroyed) and the wall type to match the neighbour.
  Draw order: N piece, then the gate, then the W / E / S pieces. No wall at an end: draw nothing there.
  Walls next to a gate need to count the gate's end cell as a neighbour so their arm reaches it.
  RA's vertical concrete wall sits ~14 px west of the cell centre in its own art, so on a vertical gate
  it lines up slightly off the gate's centre line; the wall itself stays continuous.

PREVIEWS  all-gates-{horizontal,vertical,damage}[-ra-wall].png   all six gates on each wall type
          <gate>-gate-opening.gif, <gate>-all-frames-*.png, <gate>-gate-closed[-ra-wall].png

src/  python3 gates2.py gdi|nod h|v|hv [frames]   python3 gates2.py ends   python3 brik_ends.py
      python3 gates3.py tdnod h|v|hv [frames]
      python3 gates4.py allies|soviet|tdgdi h|v|hv [frames]   python3 gates4.py soviet-idle hv
      python3 gatepreview4.py review|all|overview
