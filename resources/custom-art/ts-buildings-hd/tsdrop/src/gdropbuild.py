"""The Dropship Bay's build-up in GTDROPMK's order: 19 frames, as the mod's TSDROPMAKE.ZIP has (TS draws 17, plain
until its last frame):
  00-03   the deck grows out from its middle (TS 00-03)
  04      its painted outlines, the rail along its edge, the pad's markings (TS 04)
  05-07   the house's walls rise (TS 05); the east block rises out of the deck with its ramp (TS 05-07)
  06-08   the house's roof goes up (TS 06-07); the lean-to (TS 07)
  08-10   the antennas grow up (TS 08-09)
  10-11   the dish's post (10), the dish (11) (TS 10-11)
  11-13   the blast wall rises (TS 11-12)
  10      the jet blast guard's slot is cut in the deck (TS 09: its outline)
  13-15   the ramp reaches out from the deck to the ground (TS 13); the jet blast guard rises out of its slot (TS 14)
  15      the guard's ribs (TS 14)
  16      the pipes (TS 15); the panes and the bay's house-colour parts grey (16-17)
  18      the house colour goes on: the finished building (TS 16)
The dish stands at its A frame 00 angle throughout (gdropfinal.build), so the last frame is the healthy building + A 00."""


def ramp(i, a, b):
    """0 before frame a, 1 from frame b, linear between."""
    if i <= a:
        return 0.0
    if i >= b:
        return 1.0
    return (i - a) / float(b - a)


def step(i):
    deck = (0.37, 0.55, 0.72, 0.87)[i] if i < 4 else 1.0
    paint = 0.0 if i < 16 else (0.5 if i < 18 else 1.0)
    return dict(deck=deck,
                marks=1.0 if 4 <= i <= 10 else 0.0,
                rail=1.0 if i >= 4 else 0.0,
                padm=1.0 if i >= 4 else 0.0,
                block=ramp(i, 4, 7),
                collar=0.0, plates=0.0,
                house=ramp(i, 4, 6),
                hroof=ramp(i, 5, 8),
                lean=ramp(i, 7, 8),
                bants=ramp(i, 7, 10),
                ants=0.0,
                dish=0.0 if i < 10 else (0.5 if i == 10 else 1.0),
                wall=ramp(i, 11, 13),
                ramp=ramp(i, 12, 14),
                grille=1.0 if i >= 15 else 0.0,
                guard=0.0 if i < 10 else (0.2 if i < 13 else ramp(i, 12, 15)),
                pipes=1.0 if i >= 16 else 0.0,
                paint=paint, bpaint=paint)


N = 19
SEQ = [step(i) for i in range(N)]
# GTDROPMK frame shown next to each of ours in the previews
TS_OF = [0, 1, 2, 3, 4, 5, 6, 6, 7, 8, 9, 10, 11, 12, 13, 13, 14, 15, 16]

if __name__ == '__main__':
    for i, s in enumerate(SEQ):
        print(i, TS_OF[i], {k: round(v, 2) for k, v in s.items()})
