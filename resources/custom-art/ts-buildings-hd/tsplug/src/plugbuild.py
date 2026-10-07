"""The Upgrade Center's build-up in GTPLUGMK's order (24 frames; TS draws 17, the mod's TSPLUGMAKE.ZIP has 19):
  00-04   the deck grows out from its middle (TS 00-03), its painted outlines come up (04)
  05-08   the block rises out of the deck with its ramp, the slope's frames bare (TS 05-07)
  06-16   the sockets' collars grow round from their fronts (TS 06-12)
  12-21   the antennas grow up out of the roof (TS 09-15); the dish's post (14), the dish (15)
  16-17   the sockets' plates go in (16), their holes (17; v1 bolts) (TS 12-13)
  20      the pipes (TS 15); the slope's panes grey (TS 15)
  23      the panes go green: the finished building (TS 16)"""


def ramp(i, a, b):
    """0 before frame a, 1 from frame b, linear between."""
    if i <= a:
        return 0.0
    if i >= b:
        return 1.0
    return (i - a) / float(b - a)


def step(i):
    deck = (0.37, 0.55, 0.72, 0.87, 1.0)[i] if i < 5 else 1.0
    return dict(deck=deck,
                marks=1.0 if 4 <= i <= 16 else 0.0,
                block=ramp(i, 4, 8),
                collar=0.06 + 0.94 * ramp(i, 6, 16) if i >= 7 else 0.0,
                plates=0.0 if i < 16 else (0.5 if i == 16 else 1.0),
                dish=0.0 if i < 14 else (0.5 if i == 14 else 1.0),
                ants=ramp(i, 11, 21),
                pipes=1.0 if i >= 20 else 0.0,
                paint=0.0 if i < 20 else (0.5 if i < 23 else 1.0))


N = 24
SEQ = [step(i) for i in range(N)]
# GTPLUGMK frame shown next to each of ours in the previews
TS_OF = [0, 1, 2, 3, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 15, 15, 15, 16]

if __name__ == '__main__':
    for i, s in enumerate(SEQ):
        print(i, TS_OF[i], {k: round(v, 2) for k, v in s.items()})
