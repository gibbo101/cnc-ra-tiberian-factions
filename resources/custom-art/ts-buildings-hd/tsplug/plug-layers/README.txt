Upgrade Center v6 - plug animation layers (RA grid, 7-8 Oct 2026)

Each plug as its own layer, one per socket, to stack over the building without plugs.

LAYOUT
  plug-layers/<socket>/<plug>/<plug>-<socket>-NN.png   (+ -trim.png beside every frame)
    socket: right (the first plug's socket, east), left (the second's, west)
    plug:   drop-pod-node, seeker-control, ion-cannon-uplink
    NN:     00-14 healthy (TS's 15 frames, as plugs/ has them; the Drop Pod Node is still, so its 15 are the same
            picture), 15 damaged (drawn over the damaged building, as the base -01 frames are)
  Canvas: the building's full RA-grid canvas, 384 x 448. Each plug stands exactly where loop/ra-grid/base/<combo>
  draws it, nothing cropped.

WHAT IS IN A LAYER
  - The plug itself, solid, already cut where the building stands in front of it (the socket's collar in front of
    its foot), with its outline.
  - Its cast shadow on the building and the deck as straight-alpha black (~75% where it is darkest, as the base
    frames bake theirs in). It is see-through, so it darkens whatever is drawn under it: the A-dish / B-lamps /
    C-slot overlays and the other socket's plug.
  - Transparent everywhere else.
  - -trim.png: the plug's house colour only (white = house colour), cut to the layer's pixels.

HOW TO STACK
  base/none (00 healthy / 01 damaged), then A-dish, B-lamps and C-slot, then the plug layers on top (right socket's
  first, then the left's), each plug playing its 15 frames (15 when damaged).

CHECKED (stacked over base/none, against loop/ra-grid/base/<combo>)
  One plug, every plug, healthy and damaged: within 22 levels in any channel, on at most ~25 px (antialiased edges
  where the plug's outline meets its shadow).
  Two plugs, all six pairs: within 22 levels except where the left Ion Cannon Uplink's shadow falls on the right
  plug (up to ~50 levels on 1-19 px). A layer is rendered with only its own plug in place, so that shadow lands
  on the deck there, not on the other plug's body. Not visible at game size.
