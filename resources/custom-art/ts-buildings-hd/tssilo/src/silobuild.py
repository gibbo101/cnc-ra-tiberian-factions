"""Build-up for the Silo: 24 frames in the order TS's GTSILOMK builds it:
   0- 4  the earth ring; the lid unfolds on the ground from its middle out to full size, its first blade on it
         (as in TS, before what carries it)
   5- 7  the drum rises under it, lifting it
   7-13  the other four blades go on one by one
  15-19  the pump housing at the front, then the vent box
  20-23  the finished silo (23 = the healthy frame)"""
import silo as SL

K = SL.BUILD_KEYS


def _p(**kw):
    d = {k: 0.0 for k in K}
    d.update(kw)
    return d


F = 1.0
# the first blade (north-east) comes with the lid, as in TS; the other four go on one by one
fins = {7: 2 / 5, 8: 2 / 5, 9: 3 / 5, 10: 3 / 5, 11: 4 / 5, 12: 4 / 5, 13: F, 14: F}
SEQ = []
for i in range(24):
    d = dict(pad=min(F, 0.3 + 0.35 * i), lid=min(F, 0.1 + 0.225 * i), fins=1 / 5)
    if i >= 5:
        d['skirt'] = min(F, (i - 4) / 3.0)
    if i >= 7:
        d['fins'] = fins.get(i, F if i > 14 else 1 / 5)
    if i >= 15:
        d['pump'] = min(F, (i - 14) / 3.0)
    if i >= 17:
        d['vent'] = min(F, (i - 16) / 3.0)
    SEQ.append(_p(**d))
SEQ[-1] = dict(SL.DONE)
assert len(SEQ) == 24
