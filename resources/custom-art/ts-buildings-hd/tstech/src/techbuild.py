"""Build-up for the Tech Center: 24 frames in the order TS's GTTECHMK (20 frames) builds it:
   0- 5  the wedge rises terrace by terrace
   3- 7  the east face's grille; 5-7 the roof and its parapet
   8-11  the first fin is tipped up from lying over the roof to upright, about the line through its feet
  11-14  the second fin, the same
  13-18  the dome's struts go up from its base ring to the top (see-through)
  18-22  its panels go in, green, one by one (23 = the healthy frame)"""
import tech as TC

K = TC.BUILD_KEYS


def _p(**kw):
    d = {k: 0.0 for k in K}
    d.update(kw)
    return d


def ramp(i, a, n):
    """0 before frame a, then up to 1 over n frames."""
    return max(0.0, min(1.0, (i - a + 1) / float(n)))


SEQ = []
for i in range(24):
    SEQ.append(_p(block=ramp(i, 0, 6), east=ramp(i, 3, 5), roof=ramp(i, 5, 3), fin1=ramp(i, 8, 4),
                  fin2=ramp(i, 11, 4), dome=ramp(i, 13, 6), panels=ramp(i, 18, 6)))
SEQ[-1] = dict(TC.DONE)
assert len(SEQ) == 24
