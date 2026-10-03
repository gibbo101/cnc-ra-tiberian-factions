"""The Limpet Mine's build-up, TS's DLIMPMK frame for frame (42 frames; the mod's TSDLIMPMAKE has 19):
  00-19  the drone hovers (its ring's foot 48 units up), claws folded in under it; they drop (00-06), stretch out of
         their sleeves and swing out (06-19)
  20-30  it comes down a TS pixel a frame (4.35 units), the claws swinging out flat as it comes, so it lands on its ring
         and its points together (30), the claws drawing back a little into their sleeves
  31-38  the body sinks through the ring a pixel a frame
  38-39  the collar and knob pull in; 39-41 dug in = building-00
All the way down the lamp low on its front cycles amber, red, dark red (one colour a frame, as TS's) and the eye above it
glints white then blue-white every ten frames (03-04, 13-14, 23-24, 33-34), as TS's.
The claws' swing and stretch per frame were fitted to DLIMPMK's frames in TS's camera (0.78-0.92)."""
import numpy as np
import dlimp as M

N = 42
EXPORT_FLY = 19                 # the pose dlimpexport's "limpet-drone" mesh uses
PX = 4.354                      # one TS pixel of height, in units
# fitted (frame: phi, L); between them linear
FIT = {0: (-24.0, 40.0), 3: (-12.0, 40.0), 6: (8.0, 40.0), 9: (18.0, 43.0), 12: (36.0, 46.0), 15: (50.0, 46.0),
       18: (63.0, 46.0), 21: (75.0, 46.0), 24: (85.0, 46.0), 27: (89.0, 45.5), 30: (88.0, 44.0)}


def ring_z(f):
    return 47.9 if f <= 19 else max(0.0, 47.9 - PX * (f - 19))


def sink(f):
    return 0.0 if f <= 30 else min(M.P['settled']['sink'], PX * (f - 30))


def knob(f):
    return 1.0 if f <= 37 else (0.55 if f == 38 else 0.0)


def pose(f):
    fs = sorted(FIT)
    phi = float(np.interp(f, fs, [FIT[k][0] for k in fs]))
    L = float(np.interp(f, fs, [FIT[k][1] for k in fs]))
    if f > 30:
        phi, L = M.P['settled']['phi'], M.P['settled']['L']
    return dict(z=ring_z(f), phi=phi, L=L, sink=sink(f), knob=knob(f))


def state(f):
    if f >= 39:
        return dict(final=True, pose=dict(M.P['settled']))
    lamp = f % 3
    eye = 'w' if f % 10 == 3 else ('b' if f % 10 == 4 else None)
    return dict(pose=pose(f), lamp=lamp, eye=eye)


SEQ = [state(f) for f in range(N)]

if __name__ == '__main__':
    for i, s in enumerate(SEQ):
        print(i, {k: (round(v, 1) if isinstance(v, float) else v) for k, v in s['pose'].items()}, s.get('lamp'), s.get('eye'), s.get('final', ''))
