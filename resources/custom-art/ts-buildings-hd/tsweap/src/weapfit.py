"""Fit check for the war factory: render the model in TS's own camera over TS's 192x168 frame at x`scale`, flat
colours (lit), and compare with GTWEAP 00: TS | model / model outline on TS | TS green on model, plus IoU.
    python3 weapfit.py [out.png] [scale 4] [frame: GTWEAP/00]"""
import sys, time, importlib
import numpy as np
from PIL import Image
import procfit as PF

TS = '/home/claude/work/ts/ts-buildings-hd-handoff/06-TSWEAP/ts-original/'

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/scratch/weap/fit.png'
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    fr = sys.argv[3] if len(sys.argv) > 3 else 'GTWEAP/00'
    mod = importlib.import_module('weap')
    t = time.time()
    img, r = PF.flat(mod, scale)
    iou, giou = PF.compare(img, TS + fr.split('/')[0] + '/frames/' + fr.split('/')[1] + '.png', out, scale,
                           crop=(28 * scale, 60 * scale, 180 * scale, 160 * scale))
    print('render %.1fs  silhouette %.3f  green %.3f' % (time.time() - t, iou, giou))
