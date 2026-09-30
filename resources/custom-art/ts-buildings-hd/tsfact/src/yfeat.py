"""Feature check: where the model's landmarks land in TS's 144x144 frame vs where TS draws them."""
import numpy as np
import yard as Y

TS_PPU = 24 * np.sqrt(2) / 128


def ts_px(x, y, z):
    e, s, zc = x / 128.0, y / 128.0, z / 128.0
    return 72 + 24 * (e - s), 108 + 12 * (e + s) - 29.4 * zc


# measured in GTCNST frame 0 (native px)
MEAS = {
    'lamp0': (63, 92), 'lamp6': (111, 68),
    'fan0': (77.5, 93.3), 'fan1': (92.1, 85.4), 'fan2': (105.8, 78.5),
    'stack_thick_top': (78.5, 57.0), 'stack_thin_top': (70.5, 58.5),
    'arch_foot_w': (21.0, 98.7),
    'swall_top_w': (58.5, 96.0), 'swall_bot_w': (58.5, 119.0),
    'se_corner_bot': (84.0, 131.0),
    'box_back_112': (112.0, 86.5), 'box_front_112': (112.0, 94.5), 'box_foot_112': (112.0, 103.5),
    'kerb_in_112': (112.0, 116.0), 'door_lamp': (60.5, 109.3),
    'kerb_in_88': (88.0, 128.0),
    'crane_base': (68.0, 130.0), 'boom_tip': (37.0, 96.0),
}


def model_feats(p=Y.P):
    step = (p['yS'] - p['yN']) / (p['n_ribs'] - 1)
    rz = lambda x: float(Y.roof_z(np.array([x]), p)[0])
    zc = rz(p['xc'])
    f = {}
    f['lamp0'] = ts_px(p['xc'], p['yS'], zc + p['rib_up'] + 3)
    f['lamp6'] = ts_px(p['xc'], p['yN'], zc + p['rib_up'] + 3)
    fx = p['fan_x']
    for j, fy in enumerate(p['fans_y']):
        f[f'fan{j}'] = ts_px(fx, fy, rz(fx) - 2)
    (sx, sy, sr, sh), (tx, ty, tr, th) = p['stacks']
    f['stack_thick_top'] = ts_px(sx, sy, rz(sx) + sh)
    f['stack_thin_top'] = ts_px(tx, ty, rz(tx) + th)
    f['arch_foot_w'] = ts_px(p['xw'], p['yS'], 2)
    f['swall_top_w'] = ts_px(p['x_open'], p['yS'] - 4, rz(p['x_open']) - p['rib0_depth'])
    f['swall_bot_w'] = ts_px(p['x_open'], p['yS'] - 4, p['pad_h'])
    f['se_corner_bot'] = ts_px(p['diag'][2] + p['kerb_w'], p['yS'], p['kerb_h'])
    b = p['box']
    # N-S lines: place them on the px = const column the TS values were read on
    def on_col(px, x, z):
        y = x - (px - 72) / 0.1875
        return ts_px(x, y, z)
    f['box_back_112'] = on_col(112.0, b['x0'], b['z0'])
    f['box_front_112'] = on_col(112.0, b['x1'], b['z1'])
    f['box_foot_112'] = on_col(112.0, b['xf'], b['zf'])
    f['kerb_in_112'] = on_col(112.0, p['diag'][2], p['kerb_h'])
    f['kerb_in_88'] = on_col(88.0, p['diag'][2], p['kerb_h'])
    f['door_lamp'] = ts_px(p['door_lamp'][0], p['yS'] - 2.5, p['door_lamp'][1])
    cr = p['crane']
    f['crane_base'] = ts_px(cr['base'][0], cr['base'][1], cr['base_h'])
    f['boom_tip'] = ts_px(*cr['tip'])
    return f


def report(p=Y.P):
    f = model_feats(p)
    tot = 0
    for k, (mx, my) in MEAS.items():
        fx, fy = f[k]
        e = np.hypot(fx - mx, fy - my)
        tot += e * e
        print(f'{k:16s} TS ({mx:5.1f},{my:5.1f})  model ({fx:5.1f},{fy:5.1f})  off ({fx - mx:+5.1f},{fy - my:+5.1f})')
    print('rms %.2f px' % np.sqrt(tot / len(MEAS)))


if __name__ == '__main__':
    report()
