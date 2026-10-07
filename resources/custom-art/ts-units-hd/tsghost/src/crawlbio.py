"""
crawlbio.py - the crawl as a soldier really crawls prone (the leopard crawl, the army's low crawl), its posture and
stroke fitted to TS's own crawl frames.

How a body crawls prone (US Army low/high crawl, the leopard crawl): flat and low on his front, propped on his forearms
with the head up to see; an elbow goes forward together with the opposite knee, which is drawn up to the side while the
other leg lies straight back; he pulls on the forearm and pushes with the bent leg, then the other elbow and knee.  So:
  - one phase drives everything: his right forearm reaches ahead (the shoulder forward, the elbow opening) as his left
    knee is drawn up to the side (the hip bent and opened, the knee bending), then the other pair half a cycle later;
    the legs' timing against the arms is fitted (the diagonal pairs, or near it);
  - his body rolls a little toward the drawn-up knee, the shoulders turn with the reaching arm, the head turns a touch;
  - how he lies - how flat, how far the chest is up on the forearms, where the head looks, how far each joint moves -
    is fitted to TS's crawl frames in the facings TS rendered (crawlfit.genuine; the flipped ones get the mirror).
  - a rifle (E1, the Ghost) is pushed ahead and drawn back with each stroke, in both hands; a case (the Engineer's
    toolbox, the Medic's case) stays in his right hand, standing on the ground just ahead of it, square to him.

    python3 crawlbio.py UNIT [iters] [pop]      writes UNIT_crawlfit.json (crawlfit.py's layout: crawlgif.py and the
                                                frames read it)
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ
import crawlfit as CF

N = 6
FREE = ('e2', 'eng', 'medic')
CASE = ('eng', 'medic')
# (name, lo, hi, start)
COMMON = [('pitch0', 82, 98, 90), ('sp0', -28, 4, -12), ('hp0', -85, -20, -50), ('bx', -8, 2, -5), ('dx', -3, 4, 0.7),
          ('dy', 2, 12, 7.5), ('hf0', -10, 35, 8), ('ha0', 0, 30, 12), ('kf0', 0, 70, 25), ('af0', 0, 60, 30),
          ('ht0', -25, 85, 0), ('A_ht', -60, 60, 0),
          ('A_hf', 0, 45, 22), ('A_ha', 0, 35, 15), ('A_kf', 0, 70, 35), ('A_roll', -14, 14, 5), ('A_sy', -18, 18, 6),
          ('A_hy', -15, 15, 0), ('A_by', -1.2, 1.2, 0), ('A_yaw', -10, 10, 0), ('A_bob', -5, 5, 0),
          ('phi0', -180, 180, 0), ('delta', -180, 180, 180)]
# the wriggle (wriggle.py fits these on top of a crawl)
WRIGGLE = [('A_sr', -30, 30, 0), ('ph_sr', -180, 180, 0), ('A_sp', -15, 15, 0), ('ph_sp', -180, 180, 0),
           ('A_hp', -20, 20, 0), ('ph_sy', -180, 180, 0), ('ph_hip', -180, 180, 0), ('ph_hy', -180, 180, 0)]
ARMS = [('sf0', 50, 150, 100), ('ef0', 30, 140, 85), ('sa0', -10, 45, 15), ('st0', -40, 40, 0),
        ('A_sf', 0, 45, 18), ('A_ef', 0, 55, 25)]
RIFLE = [('rgx0', 1.0, 5.5, 3.0), ('rgy0', -2.0, 3.0, 0.4), ('rgz0', -4.0, 4.0, 0.5), ('gp0', 40, 140, 95),
         ('gy0', -35, 35, 0), ('gr0', -35, 35, 0), ('lfx0', 1.0, 5.0, 3.0), ('A_rgx', 0, 1.5, 0.6),
         ('A_rgz', -1.0, 1.0, 0.3)]


def spec(unit):
    return COMMON + (ARMS if unit in FREE else RIFLE)


def pose(unit, base, p, s):
    phi = 2 * np.pi * s / N + np.deg2rad(p['phi0'])
    Q = dict(base)
    # (the wriggle - Luke: "the body stays stiff as a board", TS's "body wriggling": the spine bends to the side
    # (sr) and twists (sy) on its own timing against the hips' swing (yaw, roll), the chest lifts on each pull (sp,
    # twice a cycle) with the head pitching against it to keep looking ahead; every term 0 by default)
    g = lambda k: np.deg2rad(p.get(k, 0.0))
    Q.update(pitch=p['pitch0'] + p['A_bob'] * np.cos(2 * phi),
             sp=p['sp0'] + p.get('A_sp', 0.0) * np.cos(2 * phi + g('ph_sp')),
             hp=p['hp0'] + p.get('A_hp', 0.0) * np.cos(2 * phi + g('ph_sp')), bx=p['bx'], dx=p['dx'],
             dy=p['dy'], by=p['A_by'] * np.sin(phi), roll=p['A_roll'] * np.sin(phi + g('ph_hip')),
             yaw=p['A_yaw'] * np.sin(phi + g('ph_hip')),
             sy=p['A_sy'] * np.sin(phi + g('ph_sy')), sr=p.get('A_sr', 0.0) * np.sin(phi + g('ph_sr')),
             hy=p['A_hy'] * np.sin(phi + g('ph_hy')))
    leg_phase = phi + np.deg2rad(p['delta'])
    for side, sg, ph in (('r', 1.0, 0.0), ('l', -1.0, np.pi)):
        a = leg_phase + ph
        # (a leg drawn up to the side: the hip bending and opening, the knee bending, all together)
        Q[side + 'hf'] = p['hf0'] + p['A_hf'] * np.sin(a)
        Q[side + 'ha'] = p['ha0'] + p['A_ha'] * np.sin(a)
        Q[side + 'kf'] = float(np.clip(p['kf0'] + p['A_kf'] * np.sin(a), 0.0, 150.0))
        Q[side + 'af'] = p['af0']
        # (the thigh turned out as the knee comes up, so the knee bends along the ground and the foot stays down:
        # a prone soldier's knee drawn up to the side, the leg pushing back against the ground - Luke: the Disc
        # Thrower's crawl "isnt kicking their legs against the floor"; at most 25 degrees, every fit stopped there
        # and its knees lifted his feet into the air)
        Q[side + 'ht'] = sg * (p['ht0'] + p.get('A_ht', 0.0) * np.sin(a))
    if unit in FREE:
        Q['ik'] = 0.0
        for side, sg, ph in (('r', 1.0, 0.0), ('l', -1.0, np.pi)):
            a = phi + ph
            # (the forearm reaching ahead: the shoulder forward, the elbow opening)
            Q[side + 'sf'] = p['sf0'] + p['A_sf'] * np.sin(a)
            Q[side + 'ef'] = float(np.clip(p['ef0'] - p['A_ef'] * np.sin(a), 0.0, 150.0))
            Q[side + 'sa'] = p['sa0']
            Q[side + 'st'] = sg * p['st0']
        if unit in CASE:
            Q['tbg'] = 1.0
    else:
        Q['ik'] = 1.0
        Q.update(rgx=p['rgx0'] + p['A_rgx'] * np.sin(phi), rgy=p['rgy0'], rgz=p['rgz0'] + p['A_rgz'] * np.cos(phi),
                 gp=p['gp0'], gy=p['gy0'], gr=p['gr0'], lfx=p['lfx0'], lsw=0.0, rsw=0.0)
    return Q


def main():
    unit = sys.argv[1]
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    pop = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    import infunit; infunit.use(unit)
    js = json.load(open('%s_shape.json' % unit))
    S = dict(F.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    base = dict(js['Q'], bx=0.0, by=0.0)
    sp = spec(unit)
    # BOUNDS='A_sf:18:45,A_ef:20:55': narrower ranges for some parameters
    for item in filter(None, os.environ.get('BOUNDS', '').split(',')):
        k, a, b = item.split(':')
        sp = [(n, float(a), float(b), min(max(c, float(a)), float(b))) if n == k else (n, lo_, hi_, c)
              for n, lo_, hi_, c in sp]
    keys = [k for k, a, b, c in sp]
    lo = np.array([a for k, a, b, c in sp], float); hi = np.array([b for k, a, b, c in sp], float)
    p0 = {k: c for k, a, b, c in sp}
    if os.environ.get('START') and os.path.exists(os.environ['START']):
        p0.update(json.load(open(os.environ['START'])).get('bio', {}))
    gen = CF.genuine(unit)
    frames = SQ.frames_of(unit, 'crawl')
    tgs = [[F.Target(unit, frames[s][1][f], f) for f in gen] for s in range(N)]

    # (LYING=w: he crawls on the ground - his hips, chest, knees and feet down, propped on his forearms - not hovering
    # over it as TS's camera alone allows: Luke, "ours are hovering above the ground with where the shadow is")
    w_lying = float(os.environ.get('LYING', 0) or 0)
    w_chest = bool(int(os.environ.get('CHEST', 0) or 0))

    def lying(Q, f):
        if w_lying <= 0:
            return 0.0
        import ground
        dz = I.grounded(S, Q, I.facing_angle(f))[1]
        # (his hips, knees and feet down, his elbows on the ground; his chest and head as high as his forearms prop
        # them - TS's crawler is up on his forearms with his head up to see)
        # (CHEST=1: his chest down too - the Disc Thrower, whose rucksack TS draws lying along his back)
        return ground.lying(S, Q, f, dz, w=w_lying, head=False, elbows=True, chest=w_chest)

    def loss(p, every=1):
        return float(np.mean([np.mean([F.frame_loss(S, pose(unit, base, p, s), t, ax, y0) +
                                       lying(pose(unit, base, p, s), t.facing) for t in tgs[s][::every]])
                              for s in range(N)]))
    # the stroke's phase and the legs' timing first (coarse), then everything
    best = None
    for ph in (range(-180, 180, 45) if not os.environ.get('KEEP_PHASE') else ()):
        for de in (0, 90, 180, 270):
            l = loss(dict(p0, phi0=float(ph), delta=float(de)), every=2)
            if best is None or l < best[0]:
                best = (l, ph, de)
    if best is not None:
        p0.update(phi0=float(best[1]), delta=float(best[2]))
    print('phase', best, flush=True)
    x0 = np.clip(np.array([p0[k] for k in keys], float), lo, hi)
    res = {}
    out_path = os.environ.get('OUT', '%s_crawlfit.json' % unit)

    def save(p, final=False):
        out = {str(s): dict(Q=pose(unit, base, p, s), frames=frames[s][1]) for s in range(N)}
        out['bio'] = p
        if final:
            if gen != list(range(8)):
                out['mirror_off'] = CF.mirror_offsets(unit, S, js, out)
            for s in range(N):
                out[str(s)]['iou'] = CF.ious(unit, S, js, out[str(s)]['Q'], frames[s][1], out.get('mirror_off'))
                out[str(s)]['f'] = float(np.mean([F.frame_loss(S, out[str(s)]['Q'], t, ax, y0) for t in tgs[s]]))
                io = out[str(s)]['iou']
                print('step', s, 'iou', ' '.join('%.2f' % io[f] for f in range(8)), flush=True)
        json.dump(out, open(out_path, 'w'), default=float)

    def cb(x, fb, it, dt):
        res['x'] = x; res['f'] = fb
        print('it', it, 'f %.4f' % fb, '%.0fs' % dt, flush=True)
        save(dict(p0, **{k: float(v) for k, v in zip(keys, x)}))
    F.cma_fit(lambda x: loss(dict(p0, **{k: float(v) for k, v in zip(keys, x)})), lo, hi, x0, iters, cb,
              sigma=float(os.environ.get('SIGMA', '0.12')), pop=pop, seed=1)
    p = dict(p0, **{k: float(v) for k, v in zip(keys, res['x'])})
    print('fitted', {k: round(v, 2) for k, v in p.items()}, flush=True)
    save(p, final=True)
    print('done', flush=True)


if __name__ == '__main__':
    main()
