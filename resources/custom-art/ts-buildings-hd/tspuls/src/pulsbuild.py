"""The EMP Pulse Cannon's build-up in NAPULSMK's order (24 frames; TS draws 20, the mod's TSPULSMAKE.ZIP has 13). TS's
snow goes on over its frames 13-18; this art has no snow, so the arms take those frames to rise instead:
  00-04   the collar grows round as an arc from its back, rising to its full height (TS 00-03)
  04-08   the cone comes up round it, the crater floor inside (TS 04-06); the drum's top shows on that floor (05-)
  07-10   the drum rises out of the crater (TS 07)
  10-19   the four arms rise out of the ground (TS 08-12, and the snow's 13-18)
  21      the lamp at the drum's foot (TS 19)
  23      the finished building (no head: the head is its own set, as in the mod)"""


def ramp(i, a, b):
    """0 up to frame a, 1 from frame b, linear between."""
    if i <= a:
        return 0.0
    if i >= b:
        return 1.0
    return (i - a) / float(b - a)


def step(i):
    ring = (0.55, 0.68, 0.8, 0.91, 1.0)[i] if i < 5 else 1.0
    drum = 0.0 if i < 5 else max(0.02, ramp(i, 7, 10))
    return dict(ring=ring, ringh=ramp(i, -1, 4), cone=ramp(i, 3, 8), arms=ramp(i, 10, 19), drum=drum, snow=0.0,
                light=1.0 if i >= 21 else 0.0)


N = 24
SEQ = [step(i) for i in range(N)]
# NAPULSMK frame shown next to each of ours in the previews
TS_OF = [0, 1, 2, 3, 3, 4, 5, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 18, 19, 19, 19]

if __name__ == '__main__':
    for i, s in enumerate(SEQ):
        print(i, TS_OF[i], {k: round(v, 2) for k, v in s.items()})
