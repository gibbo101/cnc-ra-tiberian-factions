"""Flat materials for the Dropship Bay's shape check (gdrop.FLAT colours, the trim band by height); no texture."""
import numpy as np
import gdrop as M


def materials(r, occ=None, **kw):
    alb = np.zeros(r.x.shape + (3,), np.float32) + 128
    for c, rgb in M.FLAT.items():
        alb[r.comp == c] = rgb
    alb = M.flat_extra(r, alb)
    z = np.zeros(r.x.shape, np.float32)
    return alb, (z, z, z), np.zeros(r.x.shape + (3,), np.float32)


def trim_mask(r, alb):
    return r.hitmask & np.isin(r.comp, list(M.HOUSE))
