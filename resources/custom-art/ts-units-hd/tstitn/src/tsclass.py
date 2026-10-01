import numpy as np
from tspal import load, index_map
CLS_COL = {0: (0, 0, 0), 1: (230, 170, 40), 2: (110, 110, 110), 3: (90, 110, 40), 4: (60, 80, 220), 5: (255, 0, 255), 6: (0, 200, 0)}
def classes(f):
    a = load(f); im, _ = index_map(a)
    c = np.zeros(im.shape, int)
    gold = ((im >= 128) & (im <= 167)) | ((im >= 176) & (im <= 185))
    grey = ((im >= 45) & (im <= 62)) | (im == 13) | (im == 0)
    olive = ((im >= 68) & (im <= 79)) | ((im >= 112) & (im <= 127)) | (im == 220)
    blue = ((im >= 88) & (im <= 95)) | ((im >= 195) & (im <= 199))
    house = im >= 1000
    c[gold] = 1; c[grey] = 2; c[olive] = 3; c[blue] = 4; c[house] = 6
    other = (im >= 0) & (c == 0); c[other] = 5
    c[im < 0] = 0
    return c, a
