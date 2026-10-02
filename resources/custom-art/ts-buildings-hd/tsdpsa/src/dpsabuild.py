"""The Sensor Array's build-up in GTDPSAMK's order (36 frames, as TS's: the mod's TSDPSAMAKE.ZIP has 19, TS 36):
  00      the Mobile Sensor Array as it drives up: the mast lying along its deck, the outriggers tucked in
  01-06   the east outriggers swing out level
  07-10   the west ones swing out
  11-14   all four come down onto their pads
  15-28   the mast swings up about its pivot (its angle fitted to each of TS's frames: 10 .. 90 degrees)
  28      upright, the head's arm out east
  29-35   the sensor plate unfolds from the arm's end and settles over the mast's top (35 = the finished building)"""
THETA = {15: 10.0, 16: 12.0, 17: 19.0, 18: 23.0, 19: 30.0, 20: 36.0, 21: 44.0, 22: 51.0, 23: 59.0, 24: 64.0, 25: 71.0,
         26: 77.0, 27: 83.0, 28: 90.0}


def step(i):
    le = min(i / 6.0, 1.0) * 0.55 if i <= 10 else 0.55 + 0.45 * min((i - 10) / 4.0, 1.0)
    lw = (0.0 if i <= 6 else min((i - 6) / 4.0, 1.0) * 0.55) if i <= 10 else 0.55 + 0.45 * min((i - 10) / 4.0, 1.0)
    th = 0.0 if i < 15 else THETA.get(i, 90.0)
    un = 0.0 if i <= 28 else min((i - 28) / 7.0, 1.0)
    return dict(legs_e=le, legs_w=lw, theta=th, unfold=un)


N = 36
SEQ = [step(i) for i in range(N)]
