"""
infunit.py - each infantry unit's own data, switched in before a script works on that unit (use(unit)): where its
frames are and how the mod scales them, the colour classes its TS frames are read in, the parts it carries and their
fitting classes, its shape's free sizes, the standing pose its fit starts from, and its HD colours.

    import infunit; infunit.use('e2')
"""
import numpy as np
import inf as I
import inffit as F
import infrender as R
import infseq as SQ

UNITS = {
    'e1': dict(dir='17-TSE1', name='E1', K=3.068, DX=38.06, DY=10.57, title='Light Infantry', model='LightInfantry',
               ref='RA_E1', ref_name="EA's Minigunner", vis=1.08 * 60.6 / 63.125),
    'e2': dict(dir='18-TSE2', name='E2', K=3.071, DX=38.68, DY=10.60, title='Disc Thrower', model='DiscThrower',
               ref='RA_E2', ref_name="EA's Grenadier", vis=1.08 * 63.1 / 68.2),
    # (K, DX, DY: the mod's placement of TS's frames, from infmap.py)
    'eng': dict(dir='19-TSENGINEER', name='ENGINEER', K=3.0755, DX=37.91, DY=10.46, title='Engineer', model='Engineer',
                ref='RA_E6', ref_name="EA's Engineer", vis=1.08 * 64.8 / 63.0),
    'ghost': dict(dir='20-TSGHOST', name='GHOST', K=3.0769, DX=37.70, DY=10.86, title='Ghost Stalker',
                  model='GhostStalker', ref='TD_RMBO', ref_name="EA's Commando"),
    'jj': dict(dir='21-TSJUMPJET', name='JUMPJET', K=3.116, DX=36.93, DY=9.54, title='Jumpjet Infantry',
               model='JumpjetInfantry', ref='RA_E1', ref_name="EA's Minigunner"),
    'medic': dict(dir='22-TSMEDIC', name='MEDIC', K=3.085, DX=37.53, DY=11.06, title='Medic', model='Medic',
                  ref='RA_MEDI', ref_name="EA's Field Medic"),
}

# ---------------------------------------------------------------------------------------------------- Nod's infantry
# (no in-mod frames for them: the mirror hand-off draws TS's sprite at E1's placement, K 3.068 at (38.06, 10.57) for
# TS's 61 x 61 sprites, the Cyborg Commando's 51 x 69 centred the same - tools/mirror.py)
UNITS.update({
    'e3': dict(dir='12-TSE3', name='E3', K=3.068, DX=38.06, DY=10.57, title='Rocket Infantry', model='RocketInfantry',
               ref='RA_E3', ref_name="EA's Rocket Soldier"),
    'cyborg': dict(dir='13-TSCYBORG', name='CYBORG', K=3.068, DX=38.06, DY=10.57, title='Cyborg', model='Cyborg',
                   ref='TD_E1', ref_name="EA's TD Minigunner"),
    'cyc2': dict(dir='14-TSCYC2', name='CYC2', K=3.068, DX=53.40, DY=-1.70, title='Cyborg Commando',
                 model='CyborgCommando', ref='TD_RMBO', ref_name="EA's Commando"),
    'mhijack': dict(dir='15-TSMHIJACK', name='MHIJACK', K=3.068, DX=38.06, DY=10.57, title='Mutant Hijacker',
                    model='MutantHijacker', ref='RA_THF', ref_name="EA's Thief"),
    'chamspy': dict(dir='16-TSCHAMSPY', name='CHAMSPY', K=3.068, DX=38.06, DY=10.57, title='Chameleon Spy',
                    model='ChameleonSpy', ref='RA_SPY', ref_name="EA's Spy"),
    'elcad': dict(dir='17-TSELCAD', name='ELCAD', K=3.068, DX=38.06, DY=10.57, title='Elite Cadre', model='EliteCadre',
                  ref='RA_E1', ref_name="EA's Rifle Infantry"),
    'umagon': dict(dir='19-TSUMAGON', name='UMAGON', K=3.068, DX=38.06, DY=10.57, title='Umagon', model='Umagon',
                   ref='RA_E7', ref_name="EA's Tanya"),
})

# fitting classes per component (on top of inf.CLASS, E1's)
CLASSES = {
    'e1': {},
    # E2: TS's armour dark all over, the helmet navy with the light-blue visor; green shoulder pads, arms, hips and
    # thighs; the magazines blue-grey; orange knee pads and pouch
    'e2': {I.CHEST: I.DARK, I.VEST: I.DARK, I.ABDOMEN: I.DARK, I.SHIN: I.DARK, I.KNEE: I.ORANGE, I.POUCH: I.ORANGE,
           I.BELT: I.DARK, I.HAND: I.DARK, I.TUBE: I.NAVY, I.PLATE: I.DARK, I.DISC: I.GREY},
    # the Engineer: a yellow hood with a light grey faceplate, a yellow pack, the torso and hips dark, a light grey
    # belt; green shoulder pads, upper arms and thighs; yellow forearms and gloves, shins; dark boots; the toolbox
    # yellow with a light grey lid
    'eng': {I.HELMET: I.YELLOW, I.VISOR: I.GREY, I.FACE: I.GREY, I.CHEST: I.DARK, I.VEST: I.DARK, I.ABDOMEN: I.DARK,
            I.PELVIS: I.DARK, I.BELT: I.GREY, I.UARM: I.GREEN, I.FARM: I.YELLOW, I.HAND: I.YELLOW, I.THIGH: I.GREEN,
            I.KNEE: I.YELLOW, I.SHIN: I.YELLOW, I.BOOT: I.DARK, I.PACK: I.YELLOW, I.PAD: I.GREEN, I.JAW: I.DARK,
            I.TOOLBOX: I.YELLOW, I.LID: I.GREY},
    # the Ghost Stalker: black clothes (TS: near-black with grey highlights on the legs), a blue-grey hood, his face and
    # bare arms skin; house green on the shoulders and the railgun only (TS's remap colours: his top is TS's olive and
    # natural greens, not remap)
    'ghost': {I.HELMET: I.NAVY, I.VISOR: I.SKIN, I.FACE: I.SKIN, I.JAW: I.SKIN, I.CHEST: I.DARK, I.VEST: I.DARK,
              I.ABDOMEN: I.DARK, I.PELVIS: I.DARK, I.BELT: I.DARK, I.UARM: I.SKIN, I.FARM: I.SKIN, I.HAND: I.SKIN,
              I.THIGH: I.DARK, I.KNEE: I.DARK, I.SHIN: I.DARK, I.BOOT: I.DARK, I.PAD: I.GREEN, I.RIFLE: I.GREEN,
              I.RIFLE_DARK: I.GREEN},
    # the Jumpjet: a dark grey helmet with the light-blue visor, grey armour and jetpack, light grey nozzles; house
    # green wings, thighs and shins; dark boots, hands and rifle
    'jj': {I.HELMET: I.DARK, I.CHEST: I.GREY, I.VEST: I.GREY, I.ABDOMEN: I.DARK, I.PELVIS: I.DARK, I.BELT: I.DARK,
           I.UARM: I.GREY, I.FARM: I.GREY, I.HAND: I.DARK, I.PAD: I.GREY, I.THIGH: I.GREEN, I.KNEE: I.GREEN,
           I.SHIN: I.GREEN, I.BOOT: I.DARK, I.PACK: I.GREY, I.NOZZLE: I.GREY, I.WING: I.GREEN},
    # the Medic: light grey armour and helmet, a dark glass faceplate; house green shoulder pads and thigh fronts;
    # orange armbands, knee pads, hips and thigh backs (POUCH); the grey case in his right hand, red crosses (left out)
    'medic': {I.HELMET: I.GREY, I.VISOR: I.DARK, I.FACE: I.DARK, I.JAW: I.GREY, I.CHEST: I.GREY, I.VEST: I.DARK,
              I.ABDOMEN: I.DARK, I.PELVIS: I.DARK, I.BELT: I.DARK, I.UARM: I.ORANGE, I.FARM: I.DARK, I.HAND: I.GREY,
              I.PAD: I.GREEN, I.THIGH: I.GREEN, I.KNEE: I.ORANGE, I.SHIN: I.GREY, I.BOOT: I.GREY, I.POUCH: I.ORANGE,
              I.MEDKIT: I.GREY, I.CROSS: 6},
}
# warm colours in TS's frames: E1's are its muzzle flash and blood (left out); E2's orange is his knee pads and
# pouch (a class of its own), only pure red (blood) left out
WARM = {'e1': 'fx', 'e2': 'orange', 'eng': 'yellow', 'ghost': 'skin', 'jj': 'fx', 'medic': 'medic'}

# the shape's free sizes: the shared ones (inffit.SSPEC, TSPEC) less the kit it doesn't carry, plus its own
SSPEC_DROP = {'e1': (), 'e2': ('gl', 'gt', 'gg', 'gs', 'vt'), 'eng': ('gl', 'gt', 'gg', 'gs', 'vt', 'hw', 'lsr'),
              'ghost': ('gl', 'gt', 'gg', 'gs', 'vt', 'hw', 'rs', 'lsp', 'fva', 'fe0', 'fe1', 'fd', 'fj', 'pdz', 'rt',
                        'ru', 'rf'), 'jj': ('hw',), 'medic': ('fe0', 'fe1')}
# (the plate kept short enough and the pouch big enough that the orange pouch shows under the magazines, as TS's back
# view has it)
SSPEC_ADD = {'e1': [], 'e2': [('tr', 1.0, 2.0), ('tl', 3.0, 5.0), ('tz1', 0.0, 3.5), ('tz2', -3.0, -0.5),
                              ('tx', 0.2, 1.0), ('bpz', -1.0, 1.5), ('bbz', -3.0, 0.5),
                              ('bbx', 0.4, 1.4), ('bbo', -0.5, 2.0),
                              # (the rucksack: its height on his back, how far it stands proud; the orange backs)
                              ('rkz', -1.5, 3.5), ('rko', -1.0, 1.0), ('psp', -0.9, 0.7), ('tsp', -0.8, 0.8),
                              ('tsl', -1.5, 2.2), ('rkd', 1.0, 3.2), ('rkw', 2.5, 5.0), ('rkh', 3.0, 6.5),
                              ('rkt', 0.0, 30.0)],
             # the Engineer's suit is bulkier than the soldiers' armour (a fit in their ranges stopped at the widest
             # hips, head and body): wider hips, shorter shins allowed
             'eng': [('tbz', -0.5, 1.0), ('hw', 0.9, 2.2), ('lsr', 0.7, 1.05), ('gaz', 15.0, 42.0),
                     ('gva', 6.0, 20.0), ('ge0', -25.0, 15.0), ('gh', 10.0, 35.0)],
             # the Ghost: broad and heavy (a fit in the soldiers' ranges stopped at the widest hips, shins and face);
             # his railgun's size is TS's (S0_GHOST), not fitted: TS holds it a different way in every facing
             'ghost': [('hw', 0.9, 2.2), ('rs', 0.75, 1.6), ('lsp', 4.0, 8.4), ('pdz', -0.2, 2.0),
                       ('rt', 1.0, 2.0), ('ru', 0.6, 1.5), ('rf', 0.55, 1.4),
                       # his hood and face (inf.S0_GHOST), the roll across his back
                       ('hcut', -0.8, 1.0), ('hzc', -0.6, 1.0), ('fw', 0.45, 0.95), ('fdx', 0.0, 0.8),
                       ('rl', 3.0, 6.0), ('rr', 0.6, 1.5), ('rb', 0.8, 3.5), ('rz', 0.5, 3.5), ('re', 0.25, 1.2)],
             # the Jumpjet: his jetpack's place and nozzles, his wings' size and set (inf.S0_JJ)
             # the Medic: his case's hang, where his hips' and thighs' orange backs begin (the cross on his back is
             # placed on TS's red, not fitted: the fit drops it to his waist)
             # (his faceplate across the upper front of his helmet: TS's dark row under the crown, his chin lighter)
             'medic': [('mkz', -0.5, 1.0), ('psp', -0.8, 0.7), ('tsp', -0.7, 0.7),
                       ('fe0', -25.0, 10.0), ('fe1', 15.0, 50.0)],
             'jj': [('hw', 0.9, 2.2), ('jz', -4.5, 0.5), ('nr', 0.3, 0.8), ('nl', 1.0, 4.0), ('nz', 3.0, 9.0),
                    ('wc', 2.5, 11.0), ('ws', 4.0, 13.0), ('wt', 0.4, 6.0), ('wle', -0.4, 0.6), ('wsw', -20.0, 70.0),
                    ('wdh', -50.0, 50.0), ('wtw', -100.0, 60.0), ('wth', 0.25, 1.2), ('wzr', -0.5, 4.0),
                    ('wxr', -1.5, 6.5)]}
TSPEC_DROP = {'e1': (), 'e2': ('pk', 'po'), 'eng': ('po', 'pr', 'cr', 'ar', 'hr', 'pk', 'pd'),
              'ghost': ('pk', 'po', 'pr', 'cr', 'ar', 'pd'), 'jj': ('pk', 'po'), 'medic': ('pk', 'po')}
TSPEC_ADD = {'e1': [], 'e2': [('bp', 0.6, 1.05), ('bb', 0.8, 2.6), ('rk', 0.6, 1.6)],
             'ghost': [('pr', 0.8, 1.45), ('cr', 0.8, 1.4), ('ar', 0.8, 1.45), ('pd', 0.6, 1.7)],
             'eng': [('tb', 0.6, 1.5), ('pr', 0.8, 1.45), ('cr', 0.8, 1.4), ('ar', 0.8, 1.45), ('hr', 0.85, 1.45),
                     ('pk', 0.5, 2.2), ('pd', 0.6, 1.7)],
             'jj': [('jp', 0.5, 1.6)], 'medic': [('mk', 0.6, 1.5)]}

# the ready stance each fit starts from
STAND_Q = {'e1': dict(F.STAND_Q) if hasattr(F, 'STAND_Q') else None,
           'e2': dict(I.Q0, ik=0.0, lsf=10.0, lsa=14.0, lef=25.0, rsf=10.0, rsa=14.0, ref=25.0, lha=5.0, rha=5.0,
                      lhf=4.0, rhf=-4.0, lkf=6.0, rkf=4.0),
           # the Ghost Stalker: the railgun held low at his hip, pointing ahead and down (TS's side views)
           'ghost': dict(F.STAND_Q, gp=-25.0, rgz=-4.5, rgx=2.0, lfx=4.0, lhf=8.0, rhf=-6.0),
           # the Medic: arms hanging, the case at his right side
           'medic': dict(I.Q0, ik=0.0, lsf=5.0, lsa=10.0, lef=15.0, rsf=0.0, rsa=12.0, ref=5.0, lha=4.0, rha=4.0,
                         lhf=4.0, rhf=-4.0, lkf=6.0, rkf=4.0),
           # the Engineer: arms hanging, the toolbox at his right side
           'eng': dict(I.Q0, ik=0.0, lsf=5.0, lsa=10.0, lef=15.0, rsf=0.0, rsa=12.0, ref=5.0, lha=4.0, rha=4.0,
                       lhf=4.0, rhf=-4.0, lkf=6.0, rkf=4.0)}

# HD colours (lit as TS draws them, read from its frames), house parts, parts with no camera fill
MAT = {
    'e1': dict(list(R.MAT.items()) + list({740: (96, 96, 104), 741: (52, 52, 56), 742: (56, 56, 60), 743: (52, 52, 66),
                         744: (34, 34, 36), 745: (204, 204, 206), 746: (44, 44, 48), 750: (150, 150, 152)}.items())),
    # (inflook.py's parts: chest/back plates, webbing and pouches, the dark elbows and forearm suit, the ear pieces,
    # the boots' soles, the greaves, the magazine and sight, the pack's flap)
    # E2's read off TS's standing frames (infcalib.py: each part as light as TS draws it under the HD light, in TS's
    # hue; the orange parts face away from the light, so they're as bright an orange as there is)
    'e2': {I.HELMET: (93, 93, 126), I.VISOR: (158, 158, 238), I.FACE: (158, 158, 238), I.CHEST: (38, 38, 38),
           I.VEST: (41, 41, 41), I.ABDOMEN: (92, 92, 92), I.BELT: (44, 44, 48), I.HAND: (44, 44, 48),
           I.KNEE: (173, 67, 5), I.SHIN: (99, 99, 99), I.BOOT: (97, 97, 97), I.POUCH: (203, 108, 18),
           I.JAW: (36, 36, 44), I.TUBE: (82, 82, 118), I.PLATE: (42, 42, 42), I.DISC: (150, 150, 156)},
}
# E2's makeover (inflook_e2.py: 760 chest and belly plates, 761 gauntlets, 762 knee pads, 763 drums, 764 their caps,
# 765 the antenna, 766 the respirator and hose, 767 ear pieces, 768 greaves, 769 soles, 770 thigh plates (house),
# 771 shoulder lames (house), 772 the backs of the legs, 773 the buckle, 774 straps, 775 the elbows' suit): TS's
# darks, its orange ramp for the drums and knee pads, the helmet's navy for the ear pieces
MAT['e2'].update({760: (72, 72, 78), 761: (40, 40, 44), 762: (173, 67, 5), 763: (203, 108, 18), 764: (137, 40, 0),
                  765: (30, 30, 34), 766: (74, 74, 100), 767: (62, 62, 88), 768: (118, 118, 120), 769: (30, 30, 32),
                  772: (44, 44, 46), 773: (70, 70, 74), 774: (36, 36, 38), 775: (34, 34, 36)})
CLASSES['e2'].update({760: I.DARK, 761: I.DARK, 762: I.ORANGE, 763: I.ORANGE, 764: I.ORANGE, 765: 6, 766: I.DARK,
                      767: I.NAVY, 768: I.DARK, 769: I.DARK, 770: I.GREEN, 771: I.GREEN, 772: I.DARK, 773: I.DARK,
                      774: I.DARK, 775: I.DARK})
# (E1: + inflook's thigh plates, shoulder lames and bracers)
HOUSE = {'e1': tuple(R.HOUSE) + (747, 748, 749), 'e2': (I.PAD, I.PELVIS, I.UARM, I.FARM, I.THIGH, 770, 771), 'eng': (I.PAD, I.UARM, I.THIGH, 782, 783),
         'ghost': (I.PAD, I.RIFLE, I.RIFLE_DARK), 'jj': (I.WING, I.THIGH, I.KNEE, I.SHIN), 'medic': (I.PAD, I.THIGH)}
# the Engineer's colours (to be read off TS's frames once his shape is fitted: infcalib.py)
MAT['eng'] = {I.HELMET: (250, 205, 90), I.VISOR: (255, 255, 255), I.FACE: (210, 210, 210), I.CHEST: (75, 75, 75),
              I.VEST: (102, 102, 102), I.ABDOMEN: (60, 60, 60), I.PELVIS: (112, 112, 112), I.BELT: (170, 170, 170),
              I.FARM: (250, 199, 88), I.HAND: (246, 187, 81), I.KNEE: (250, 213, 93), I.SHIN: (254, 225, 100),
              I.BOOT: (44, 44, 44), I.PACK: (246, 187, 81), I.JAW: (36, 36, 36), I.TOOLBOX: (248, 200, 87),
              I.LID: (198, 198, 198), I.GOGGLE: (26, 26, 30)}
# the Engineer's makeover (inflook_eng.py: 780 the vest's padding, 781 pouches, 782 shoulder plates (house), 783 thigh
# plates (house), 784 the face panel, 785 goggle lenses, 786 their rims, 787 the respirator, 788 its filter, 789 the
# collar, 790 handles, 791 latches and buckle, 792 straps, 793 soles, 794 cuffs, 795 the elbows' suit)
MAT['eng'].update({780: (88, 88, 92), 781: (62, 62, 66), 784: (38, 38, 40), 785: (24, 24, 30), 786: (60, 60, 62),
                   787: (198, 198, 198), 788: (150, 150, 154), 789: (44, 44, 46), 790: (176, 176, 178),
                   791: (52, 52, 54), 792: (52, 52, 54), 793: (26, 26, 28), 794: (48, 48, 50), 795: (48, 48, 50)})
CLASSES['eng'].update({780: I.DARK, 781: I.DARK, 782: I.GREEN, 783: I.GREEN, 784: I.DARK, 785: I.DARK, 786: I.DARK,
                       787: I.GREY, 788: I.GREY, 789: I.DARK, 790: I.GREY, 791: I.DARK, 792: I.DARK, 793: I.DARK,
                       794: I.DARK, 795: I.DARK})
# the Jumpjet's colours (first guesses from TS's frames; infcalib.py reads them once his shape is fitted)
# (infcalib.py on his standing frames: the rifle 11, its receiver 82; the upper arms and hips sit in the wings' and
# body's shadow under the HD light, so they read as light as TS's from a lighter grey.  The jetpack is TS's grey column
# (85-178 between dark edges), narrower than a free fit made it: the free fit filled TS's black outlines between the
# wings with a wide dark pack)
MAT['jj'] = {I.HELMET: (48, 48, 48), I.VISOR: (158, 158, 238), I.FACE: (158, 158, 238), I.JAW: (36, 36, 40),
             I.CHEST: (120, 120, 120), I.VEST: (128, 128, 128), I.ABDOMEN: (52, 52, 52), I.PELVIS: (70, 70, 70),
             I.BELT: (48, 48, 48), I.UARM: (170, 170, 170), I.FARM: (110, 110, 110), I.HAND: (40, 40, 40),
             I.PAD: (110, 110, 110), I.BOOT: (36, 36, 36), I.PACK: (120, 120, 120), I.NOZZLE: (168, 168, 168),
             I.RIFLE: (11, 11, 11), I.RIFLE_DARK: (82, 82, 82)}
# the Medic's colours, read off TS's standing frames (infcalib.py, NEUTRAL_ALL: each grey part against all TS's grey and
# dark pixels on it - TS shades the front of his armour dark); his faceplate dark glass (TS: dark grey looking ahead);
# his armbands, knee pads, hips and thigh backs on TS's orange ramp (below)
MAT['medic'] = {I.HELMET: (153, 153, 153), I.VISOR: (62, 62, 72), I.FACE: (62, 62, 72), I.JAW: (153, 153, 153),
                I.CHEST: (175, 175, 175), I.VEST: (132, 132, 132), I.ABDOMEN: (177, 177, 177), I.PELVIS: (175, 175, 175),
                I.BELT: (52, 52, 52), I.UARM: (214, 121, 16), I.FARM: (95, 95, 95), I.HAND: (100, 100, 100),
                I.KNEE: (214, 121, 16), I.SHIN: (201, 201, 201), I.BOOT: (200, 200, 200), I.POUCH: (214, 121, 16),
                I.MEDKIT: (184, 184, 184), I.CROSS: (235, 28, 28)}
# the Ghost's colours, read off TS's standing frames (infcalib.py); his skin on TS's flesh ramp (below)
MAT['ghost'] = {I.HELMET: (90, 90, 124), I.VISOR: (202, 153, 137), I.FACE: (202, 153, 137), I.JAW: (190, 141, 125),
                I.CHEST: (54, 72, 31), I.VEST: (54, 72, 31), I.ABDOMEN: (28, 28, 24), I.PELVIS: (26, 26, 21), I.BELT: (36, 36, 36),
                I.UARM: (202, 153, 137), I.FARM: (202, 153, 137), I.HAND: (196, 147, 131), I.THIGH: (50, 50, 49),
                I.KNEE: (131, 131, 127), I.SHIN: (92, 92, 92), I.BOOT: (64, 64, 64), I.ROLL: (40, 40, 42),
                I.ROLL_END: (104, 104, 104)}
# parts drawn on TS's palette ramp (infrender.RAMP): E2's orange pouch and knee pads, on TS's orange ramp (its frames'
# eleven oranges, dark red-orange to light yellow-orange), as light on average as TS draws them (infcalib: the HD
# light leaves the pouch on his back in shadow, so no plain orange could be as light as TS's and stay orange; G is
# the luminance at full light).  MAT keeps TS's mean colours for them (the 3D model's albedo)
ORANGE_RAMP = [(137, 24, 0), (153, 40, 0), (165, 56, 0), (182, 72, 0), (198, 97, 0), (214, 121, 16), (230, 149, 48),
               (238, 174, 72), (246, 182, 80), (255, 194, 89), (255, 210, 97)]
# (the pouch: TS draws it about as light standing, running and crawling, whichever way it faces the HD light, so it
# keeps half its HD shading, gamma 0.5: fitted on TS's standing, run and crawl frames together)
RAMP = {'e1': {}, 'e2': {I.POUCH: (ORANGE_RAMP, 185.0, 0.5), I.KNEE: (ORANGE_RAMP, 175.0),
                         # (the makeover's knee pads as the old ones; the drums as the pouch, their caps darker)
                         762: (ORANGE_RAMP, 150.0), 763: (ORANGE_RAMP, 190.0, 0.85), 764: (ORANGE_RAMP, 100.0, 0.7)}}
# E2's rucksack on TS's own colours for it (its back view: dark navy, blue-greys and, where lit, its bright blues - the
# lavender it was drawn in read as a light flat board, Luke: "nowhere near as thick")
PACK_RAMP = [(20, 20, 30), (40, 40, 64), (52, 52, 76), (76, 76, 101), (89, 89, 113), (101, 101, 125), (105, 105, 182),
             (125, 125, 206), (149, 149, 230)]
RAMP['e2'][I.TUBE] = (PACK_RAMP, float(__import__('os').environ.get('PACK_G', 110.0)),
                      float(__import__('os').environ.get('PACK_GAMMA', 1.0)))
# the pack's tones mapped onto TS's own (TS's back views: half its pack near black, a quarter bright lavender -
# quantiles 10/25/50/75/90 of 20, 28, 44, 104, 116 against our shading's; it was all one mid grey-blue, Luke: "all
# looking good except the disc thrower", then "pack is good!" on these); PACK_LUT=0 for the plain ramp
if __import__('os').environ.get('PACK_LUT', '1') != '0':
    RAMP['e2'][I.TUBE] = (PACK_RAMP, 110.0, 1.0, ([0.555, 0.645, 0.709, 0.773, 0.818], [20.0, 28.0, 44.0, 104.0, 116.0]))
# the Engineer's yellow: TS's frames' ten yellows (its darkest still a light orange-yellow: TS shades the suit with
# its dark outline pixels, not darker yellows)
YELLOW_RAMP = [(230, 149, 48), (238, 174, 72), (246, 182, 80), (255, 194, 89), (255, 210, 97), (255, 218, 97),
               (255, 226, 101), (255, 234, 105), (255, 246, 109), (255, 255, 113)]
# each part as light on average as TS draws it (infcalib: its standing frames; the shins and knees face the HD light
# least, TS draws them lightest)
# the Ghost's skin: TS's sixteen flesh tones, dark red-brown to light pink
SKIN_RAMP = [(52, 4, 0), (68, 20, 4), (80, 32, 16), (93, 44, 28), (105, 56, 40), (117, 68, 52), (129, 80, 64),
             (141, 93, 76), (153, 105, 89), (165, 117, 101), (178, 129, 113), (190, 141, 125), (202, 153, 137),
             (214, 165, 149), (226, 178, 161), (238, 190, 174)]
# (each part as light on average as TS draws it on his standing frames: TS's forearms are its darkest flesh tones)
RAMP['ghost'] = {I.VISOR: (SKIN_RAMP, 265.0), I.FACE: (SKIN_RAMP, 265.0), I.JAW: (SKIN_RAMP, 265.0),
                 # (his forearms and hands as his upper arms: TS's darker pixels there are its shading, and drawn that
                 # dark in HD the forearms vanished against his black clothes - Luke: "looks like he's an amputee")
                 I.UARM: (SKIN_RAMP, 199.0), I.FARM: (SKIN_RAMP, 199.0), I.HAND: (SKIN_RAMP, 180.0)}
# (his makeover: off TS's bright yellow - Luke: "depart from the bright yellow" - onto the Reborn engineer's dark
# ochre, the GDI ochre of the HD buildings' collars (214, 166, 70) at its lightest, browner as it darkens)
OCHRE_RAMP = [(40, 30, 14), (62, 47, 22), (86, 65, 30), (110, 84, 40), (134, 103, 48), (158, 122, 56), (182, 141, 63),
              (204, 158, 68), (220, 176, 88), (232, 196, 116)]
RAMP_ENG_LOOK2 = {I.HELMET: (OCHRE_RAMP, 175.0), I.FARM: (OCHRE_RAMP, 175.0), I.KNEE: (OCHRE_RAMP, 185.0),
                  I.SHIN: (OCHRE_RAMP, 185.0), I.PACK: (OCHRE_RAMP, 165.0), 782: (OCHRE_RAMP, 180.0),
                  797: (OCHRE_RAMP, 175.0)}
# (the rest of the makeover's colours: the Reborn engineer's dark suit and gloves, the dark case with its light grey
# lid and handle, the glowing blue visor as the soldiers'; house green: the stripes and the thigh plates)
MAT_ENG_LOOK2 = {I.VISOR: (158, 158, 238), I.FACE: (158, 158, 238), I.HAND: (44, 44, 46), I.TOOLBOX: (46, 46, 50),
                 I.LID: (176, 176, 178), I.HELMET: (182, 141, 63), I.FARM: (182, 141, 63), I.KNEE: (182, 141, 63),
                 I.SHIN: (182, 141, 63), I.PACK: (170, 131, 59), 782: (182, 141, 63), 797: (182, 141, 63),
                 796: (0, 214, 0), 798: (190, 190, 186), 799: (20, 20, 22), 800: (30, 30, 34), 801: (132, 132, 136), 786: (56, 56, 60),
                 802: (160, 160, 164), I.CHEST: (52, 52, 56), I.VEST: (56, 56, 60), I.ABDOMEN: (48, 48, 52),
                 I.PELVIS: (54, 54, 58), I.BELT: (36, 36, 38), I.BOOT: (40, 40, 42)}
HOUSE_ENG_LOOK2 = (I.PAD, I.UARM, I.THIGH, 783, 796)
# the Medic's makeover (inflook_medic.py: 810 his light grey plates, 811 pouches, 812 shoulder plates (house), 813 thigh
# plates (house), 814 the faceplate's frame, 815 ear pieces, 816 the orange armbands, 817 bracers, 818 greaves, 819 soles,
# 820 the case's handle, 821 its band, 822 the dark suit): TS's light greys, his orange on TS's ramp
MAT_MEDIC_LOOK2 = {I.HELMET: (228, 228, 228), I.VISOR: (158, 158, 238), I.FACE: (158, 158, 238), I.MEDKIT: (232, 232, 230),
                   810: (186, 186, 186), 811: (120, 120, 122), 814: (40, 40, 44), 815: (130, 130, 132),
                   816: (230, 46, 40), 817: (176, 176, 176), 818: (196, 196, 196), 819: (36, 36, 38), 820: (52, 52, 54),
                   821: (60, 60, 62), 822: (50, 50, 54)}
HOUSE_MEDIC_LOOK2 = (I.PAD, I.THIGH, 812, 813)
# the Rocket Infantry's makeover (inflook_e3.py: 830 dark plates, 831 the suit, 832/833 house shoulder and thigh plates,
# 834 light grey knee plates, 835 house chevrons, 836 greaves, 837 soles, 838 pouches, 839 the visor frame, 840 ear pieces,
# 841 the antenna, 842 the crown lamp (house), 843 the launcher's yellow band, 844 its sight, 845 the pack flap, 846 the
# holster): TS's darks and light greys; the concept's red visor
MAT_E3_LOOK2 = {830: (64, 64, 68), 831: (30, 30, 32), 834: (177, 177, 177), 836: (181, 181, 181), 837: (24, 24, 26),
                838: (44, 44, 48), 839: (30, 30, 32), 840: (40, 40, 44), 841: (24, 24, 26), 843: (232, 186, 40),
                844: (34, 34, 36), 845: (38, 38, 40), 846: (34, 34, 36), I.HELMET: (30, 30, 32),
                I.VISOR: (236, 40, 36), I.FACE: (236, 40, 36)}
HOUSE_E3_LOOK2 = (I.PAD, I.UARM, I.THIGH, 832, 833, 835, 842)
# (his visor is the soldiers' generic light-blue glass, as TS draws it - Luke: "Lets stay ts accurate"; E3_VISOR=red
# gives the concept's red glass)
E3_VISOR = __import__('os').environ.get('E3_VISOR', 'blue')
if E3_VISOR == 'blue':
    MAT_E3_LOOK2.update({I.VISOR: (158, 158, 238), I.FACE: (158, 158, 238)})
RAMP_MEDIC_LOOK2 = {}
RAMP['eng'] = {I.HELMET: (YELLOW_RAMP, 314.0), I.FARM: (YELLOW_RAMP, 364.0), I.HAND: (YELLOW_RAMP, 327.0),
               I.KNEE: (YELLOW_RAMP, 436.0), I.SHIN: (YELLOW_RAMP, 473.0), I.PACK: (YELLOW_RAMP, 310.0),
               I.TOOLBOX: (YELLOW_RAMP, 355.0)}
# (the Medic's: each as light on average as TS draws it on his standing frames; his orange hips and thigh backs keep
# half their HD shading, as E2's pouch)
RAMP['medic'] = {I.UARM: (ORANGE_RAMP, 201.0), I.KNEE: (ORANGE_RAMP, 172.0), I.POUCH: (ORANGE_RAMP, 158.0, 0.5)}
# colour classes that count more in the fit's colour term: E2's orange (the pouch below his pack, the knee pads) is a
# few pixels a frame but plain to see in TS's back views
CLASS_W = {'e1': {}, 'e2': {I.ORANGE: 3.0}, 'elcad': {I.SKIN: 2.0}, 'umagon': {I.SKIN: 1.5}}


# ---------------------------------------------------------------------------------------------------- Nod: E3
# the Rocket Infantry (TS's E3): E1's soldier, all dark (a black helmet with the light-blue visor and its glint, dark
# armour), house green on the shoulder pads, upper arms and thighs; light grey knees and shins; the launcher light grey
# with black ends on his right shoulder
CLASSES['e3'] = {I.HELMET: I.DARK, I.PACK: I.DARK, I.POUCH: I.DARK, I.PELVIS: I.DARK, I.FARM: I.DARK, I.KNEE: I.GREY,
                 I.TUBE: I.DARK}
WARM['e3'] = 'fx'
# (the launcher: longer and thicker than a rifle; lz how far its tube sits above the hands)
SSPEC_DROP['e3'] = ('gl', 'gt', 'gg', 'gs')
SSPEC_ADD['e3'] = [('gl', 10.0, 16.0), ('gt', 1.3, 2.6), ('gg', 3.0, 7.0), ('lz', 0.8, 2.0)]
TSPEC_DROP['e3'] = ()
TSPEC_ADD['e3'] = []
# the ready stance: the launcher on his right shoulder, level, pointing ahead; the right hand under it in front of the
# shoulder, the left hand forward along it
STAND_Q['e3'] = dict(F.STAND_Q, gp=0.0, rgx=1.2, rgy=2.2, rgz=-1.6, lfx=3.2)
# (infcalib.py on the fitted standing frames: each part as light as TS draws it under the HD light; the launcher
# needs white to read as TS's light grey 195)
MAT['e3'] = {I.HELMET: (14, 14, 14), I.VISOR: (158, 158, 238), I.FACE: (158, 158, 238), I.CHEST: (70, 70, 70),
             I.VEST: (56, 56, 60), I.PACK: (47, 47, 47), I.ABDOMEN: (60, 60, 64), I.PELVIS: (79, 79, 79),
             I.BELT: (44, 44, 48), I.FARM: (55, 55, 55), I.HAND: (80, 80, 80), I.KNEE: (177, 177, 177),
             I.SHIN: (181, 181, 181), I.BOOT: (83, 83, 83), I.RIFLE_DARK: (24, 24, 26), I.POUCH: (56, 56, 60),
             I.JAW: (36, 36, 40), I.LAUNCHER: (250, 250, 250), I.LAUNCHER_RIM: (30, 30, 32)}
HOUSE['e3'] = (I.PAD, I.UARM, I.THIGH)


# ---------------------------------------------------------------------------------------------------- Nod: Elite Cadre
# Slavik's sprite (TS's ELCAD): a light grey hood over his head, his bare face; a house-green jacket (shoulders, arms -
# TS's front and side views) open on his bare chest (TS's flesh tones: his chest, his face, his hands); dark trousers
# with green fronts to the thighs, the lower legs in TS's flesh browns (boots); his back dark; the rifle light grey
CLASSES['elcad'] = {I.HELMET: I.GREY, I.VISOR: I.SKIN, I.FACE: I.SKIN, I.JAW: I.SKIN, I.CHEST: I.DARK, I.VEST: I.SKIN,
                    I.ABDOMEN: I.SKIN, I.PACK: I.DARK, I.PELVIS: I.DARK, I.BELT: I.DARK, I.UARM: I.GREEN,
                    I.FARM: I.SKIN, I.HAND: I.SKIN, I.PAD: I.GREEN, I.THIGH: I.GREEN, I.POUCH: I.DARK, I.KNEE: I.SKIN,
                    I.SHIN: I.DARK, I.BOOT: I.GREY, I.RIFLE: I.GREY, I.RIFLE_DARK: I.DARK}
WARM['elcad'] = 'skin'
SSPEC_DROP['elcad'] = ('fva', 'fe0', 'fe1', 'fd', 'fj')
SSPEC_ADD['elcad'] = [('hcut', -0.8, 1.0), ('hzc', -0.6, 1.2), ('fw', 0.45, 0.95), ('fdx', 0.0, 0.8),
                      ('tsp', -0.7, 0.7), ('asp', -0.6, 0.6)]
TSPEC_DROP['elcad'] = ()
TSPEC_ADD['elcad'] = []
# (TS: the rifle at his hip, pointing ahead)
STAND_Q['elcad'] = dict(F.STAND_Q, rgz=-4.2, rgx=2.0, gp=-2.0)
# (infcalib.py: each part as light as TS draws it; the skin on TS's flesh ramp, as dark as TS's - his chest's brown)
MAT['elcad'] = {I.HELMET: (255, 255, 255), I.VISOR: (178, 129, 113), I.FACE: (178, 129, 113), I.JAW: (178, 129, 113),
                I.CHEST: (54, 54, 54), I.VEST: (153, 105, 89), I.ABDOMEN: (140, 92, 76), I.PELVIS: (33, 33, 33),
                I.BELT: (36, 36, 38), I.FARM: (153, 105, 89), I.HAND: (165, 117, 101), I.KNEE: (117, 68, 52),
                I.SHIN: (69, 69, 69), I.BOOT: (120, 120, 122), I.PACK: (79, 79, 79), I.POUCH: (67, 67, 67),
                I.RIFLE: (255, 255, 255), I.RIFLE_DARK: (37, 37, 37)}
HOUSE['elcad'] = (I.PAD, I.UARM, I.FARM, I.THIGH)
RAMP['elcad'] = {I.VISOR: (SKIN_RAMP, 200.0), I.FACE: (SKIN_RAMP, 200.0), I.JAW: (SKIN_RAMP, 200.0),
                 I.VEST: (SKIN_RAMP, 128.0), I.ABDOMEN: (SKIN_RAMP, 128.0), I.HAND: (SKIN_RAMP, 180.0),
                 I.FARM: (SKIN_RAMP, 174.0), I.KNEE: (SKIN_RAMP, 130.0)}
GLINT_ADD = {'elcad': 0}
NO_GLOW_ADD = ('elcad',)
VISOR_ADD = {'elcad': ((0, 0, 0), (0, 0, 0), (225, 225, 228))}

# ---------------------------------------------------------------------------------------------------- Nod: Umagon
# TS's UMAGON: her dark hair (TS's darkest flesh tones, near black red-brown) over her head and down her back, her face
# and bare arms in TS's flesh tones; a house-green top and trousers; grey lower legs, dark boots; a long black rifle
CLASSES['umagon'] = {I.HELMET: I.DARK, I.HAIR: I.DARK, I.VISOR: I.SKIN, I.FACE: I.SKIN, I.JAW: I.SKIN,
                     I.CHEST: I.GREEN, I.VEST: I.GREY, I.ABDOMEN: I.GREY, I.PELVIS: I.DARK, I.BELT: I.DARK,
                     I.UARM: I.SKIN, I.FARM: I.SKIN, I.HAND: I.SKIN, I.PAD: I.GREEN, I.THIGH: I.GREEN, I.POUCH: I.DARK,
                     I.KNEE: I.DARK, I.SHIN: I.GREY, I.BOOT: I.DARK, I.RIFLE: I.DARK, I.RIFLE_DARK: I.DARK}
WARM['umagon'] = 'skin_hair'
HAIR_DARK = 52.0
SSPEC_DROP['umagon'] = ('fva', 'fe0', 'fe1', 'fd', 'fj', 'vt')
SSPEC_ADD['umagon'] = [('hcut', -0.8, 1.0), ('hzc', -0.6, 1.0), ('fw', 0.45, 0.95), ('fdx', 0.0, 0.8),
                       ('hl', 0.5, 4.5), ('hb', 0.8, 2.0), ('tsp', -0.7, 0.7)]
TSPEC_DROP['umagon'] = ('pk', 'po')
TSPEC_ADD['umagon'] = [('hrr', 0.6, 1.5)]
STAND_Q['umagon'] = dict(F.STAND_Q, rgz=-3.8, rgx=2.2, gp=-2.0)
# (infcalib.py: each part as light as TS draws it; the skin and hair on TS's flesh ramp)
MAT['umagon'] = {I.HELMET: (60, 20, 8), I.HAIR: (60, 20, 8), I.VISOR: (214, 165, 149), I.FACE: (214, 165, 149),
                 I.JAW: (214, 165, 149), I.VEST: (150, 182, 125), I.ABDOMEN: (150, 182, 125), I.PELVIS: (24, 24, 26),
                 I.BELT: (24, 24, 26), I.UARM: (202, 153, 137), I.FARM: (202, 153, 137), I.HAND: (202, 153, 137),
                 I.POUCH: (42, 42, 42), I.KNEE: (44, 44, 46), I.SHIN: (230, 230, 230), I.BOOT: (96, 96, 96),
                 I.RIFLE: (14, 14, 16), I.RIFLE_DARK: (45, 43, 29)}
HOUSE['umagon'] = (I.CHEST, I.PAD, I.THIGH)
RAMP['umagon'] = {I.VISOR: (SKIN_RAMP, 250.0), I.FACE: (SKIN_RAMP, 250.0), I.JAW: (SKIN_RAMP, 250.0),
                  I.UARM: (SKIN_RAMP, 220.0), I.FARM: (SKIN_RAMP, 220.0), I.HAND: (SKIN_RAMP, 210.0),
                  I.HELMET: (SKIN_RAMP, 35.0), I.HAIR: (SKIN_RAMP, 35.0)}
GLINT_ADD['umagon'] = 0
NO_GLOW_ADD = NO_GLOW_ADD + ('umagon',)
VISOR_ADD['umagon'] = ((0, 0, 0), (0, 0, 0), (120, 70, 50))


# ---------------------------------------------------------------------------------------------------- Nod: Chameleon Spy
# TS's CHAMSPY: a light grey hood-helmet, orange goggles across his face, dark under them; a near-black suit, house green
# on the shoulders, upper arms and thighs, TS's pale non-remap greens (camouflage) on the forearms and shins; a lavender
# band round the back of his belt; unarmed
CLASSES['chamspy'] = {I.HELMET: I.GREY, I.VISOR: I.ORANGE, I.FACE: I.ORANGE, I.JAW: I.DARK, I.CHEST: I.DARK,
                      I.VEST: I.DARK, I.ABDOMEN: I.DARK, I.PELVIS: I.DARK, I.BELT: I.DARK, I.PAD: I.GREEN,
                      I.UARM: I.GREEN, I.FARM: I.GREY, I.HAND: I.DARK, I.THIGH: I.GREEN, I.KNEE: I.DARK, I.SHIN: I.GREY,
                      I.BOOT: I.DARK, I.POUCH: I.NAVY}
WARM['chamspy'] = 'orange'
SSPEC_DROP['chamspy'] = ('gl', 'gt', 'gg', 'gs', 'vt')
SSPEC_ADD['chamspy'] = []
TSPEC_DROP['chamspy'] = ('pk',)
TSPEC_ADD['chamspy'] = []
STAND_Q['chamspy'] = dict(I.Q0, ik=0.0, lsf=5.0, lsa=10.0, lef=15.0, rsf=0.0, rsa=12.0, ref=5.0, lha=4.0, rha=4.0,
                          lhf=4.0, rhf=-4.0, lkf=6.0, rkf=4.0)
# (infcalib.py: each part as light as TS draws it)
MAT['chamspy'] = {I.HELMET: (214, 214, 214), I.VISOR: (214, 121, 16), I.FACE: (214, 121, 16), I.JAW: (40, 40, 42),
                  I.CHEST: (60, 67, 58), I.VEST: (28, 47, 21), I.ABDOMEN: (30, 30, 32), I.PELVIS: (22, 22, 22),
                  I.BELT: (28, 28, 30), I.FARM: (172, 255, 142), I.HAND: (36, 36, 38), I.KNEE: (69, 69, 69),
                  I.SHIN: (169, 255, 140), I.BOOT: (37, 37, 37), I.POUCH: (150, 150, 255)}
HOUSE['chamspy'] = (I.PAD, I.UARM, I.THIGH)
GLINT_ADD['chamspy'] = 0
VISOR_ADD['chamspy'] = ((240, 140, 30), (190, 95, 15), (230, 230, 232))

# ---------------------------------------------------------------------------------------------------- Nod: Hijacker
# TS's MHIJACK: a bald head (TS's flesh tones, its crown too), an olive hood down round it; a long olive coat (TS's
# olive darks and greys) over his body and arms down past the knees, house green shoulder pads; his bare hands; dark
# trousers, grey lower legs, dark boots; unarmed
CLASSES['mhijack'] = {I.HELMET: I.DARK, I.FACE: I.SKIN, I.CHEST: I.DARK, I.VEST: I.DARK, I.ABDOMEN: I.DARK,
                      I.PELVIS: I.DARK, I.BELT: I.DARK, I.PAD: I.GREEN, I.UARM: I.DARK, I.FARM: I.DARK,
                      I.HAND: I.SKIN, I.THIGH: I.DARK, I.COAT: I.DARK, I.KNEE: I.DARK, I.SHIN: I.GREY,
                      I.BOOT: I.DARK}
WARM['mhijack'] = 'skin_olive'
SSPEC_DROP['mhijack'] = ('gl', 'gt', 'gg', 'gs', 'vt', 'fva', 'fe0', 'fe1', 'fd', 'fj')
SSPEC_ADD['mhijack'] = [('hcut', -0.6, 1.4), ('htc', -0.6, 1.4), ('cfx', 1.0, 2.4), ('cfo', 0.0, 1.2),
                        ('cff', 0.0, 1.6), ('cl', -1.0, 2.2)]
TSPEC_DROP['mhijack'] = ('pk', 'po')
TSPEC_ADD['mhijack'] = []
STAND_Q['mhijack'] = dict(I.Q0, ik=0.0, lsf=5.0, lsa=10.0, lef=15.0, rsf=0.0, rsa=12.0, ref=5.0, lha=4.0, rha=4.0,
                          lhf=4.0, rhf=-4.0, lkf=6.0, rkf=4.0)
# (infcalib.py: each part as light as TS draws it - the coat one olive over the body, its sleeves lighter as TS's are)
MAT['mhijack'] = {I.HELMET: (71, 71, 40), I.FACE: (190, 141, 125), I.CHEST: (124, 123, 84), I.VEST: (124, 123, 84),
                  I.ABDOMEN: (124, 123, 84), I.PELVIS: (124, 123, 84), I.BELT: (52, 52, 28), I.UARM: (151, 150, 107),
                  I.FARM: (165, 165, 120), I.HAND: (190, 141, 125), I.THIGH: (64, 64, 40), I.COAT: (119, 119, 84),
                  I.KNEE: (40, 40, 40), I.SHIN: (207, 207, 207), I.BOOT: (88, 88, 88)}
HOUSE['mhijack'] = (I.PAD,)
RAMP['mhijack'] = {I.FACE: (SKIN_RAMP, 207.0), I.HAND: (SKIN_RAMP, 207.0)}
GLINT_ADD['mhijack'] = 0
NO_GLOW_ADD = NO_GLOW_ADD + ('mhijack',)
VISOR_ADD['mhijack'] = ((0, 0, 0), (0, 0, 0), (120, 70, 50))


# ---------------------------------------------------------------------------------------------------- Nod: Cyborg
# TS's CYBORG: a bone-pale skull, its face dark; a house green plate over the chest and back, big green shoulder pads, a
# grey plate on the chest's front, a dark waist; grey metal arms, the gun in the right forearm; house green thighs, grey
# metal shins, dark feet; TS's dark red lights at the knees and ankles (left out of the fit with TS's other effects)
CLASSES['cyborg'] = {I.HELMET: I.GREY, I.VISOR: I.DARK, I.FACE: I.DARK, I.JAW: I.GREY, I.CHEST: I.GREEN, I.VEST: I.GREY,
                     I.ABDOMEN: I.DARK, I.PELVIS: I.DARK, I.BELT: I.DARK, I.PAD: I.GREEN, I.UARM: I.GREY,
                     I.FARM: I.GREY, I.HAND: I.DARK, I.THIGH: I.GREEN, I.POUCH: I.DARK, I.KNEE: I.GREY, I.SHIN: I.GREY,
                     I.BOOT: I.DARK, I.RIFLE: I.GREY, I.RIFLE_DARK: I.DARK}
WARM['cyborg'] = 'fx'
# (a third bigger than the soldiers all over: their ranges scaled up; the gun's own)
_BIG = ('hw', 'lt', 'rt', 'rs', 'ah', 'bl', 'bw', 'bh', 'lsp', 'sw', 'lu', 'lf', 'ru', 'rf', 'rh', 'ln', 'pdz')
SSPEC_DROP['cyborg'] = _BIG + ('gl', 'gt', 'gg', 'gs')
SSPEC_ADD['cyborg'] = ([(k, lo * 1.35, hi * 1.35) for k, lo, hi in F.SSPEC if k in _BIG] +
                       [('gl', 4.0, 11.0), ('gt', 1.0, 2.6), ('gg', 0.5, 4.5), ('tsp', -0.7, 0.7)])
TSPEC_DROP['cyborg'] = ('pk', 'po')
TSPEC_ADD['cyborg'] = []
# (standing: the arms hanging, the gun arm a little forward - TS's side views)
STAND_Q['cyborg'] = dict(I.Q0, ik=0.0, garm=1.0, lsf=5.0, lsa=12.0, lst=0.0, lef=15.0, rsf=15.0, rsa=10.0, rst=0.0,
                         ref=25.0, lha=5.0, rha=5.0, lhf=4.0, rhf=-4.0, lkf=6.0, rkf=4.0)
# (infcalib.py: each part as light as TS draws it; the gun as its forearm)
# (infcalib.py, NEUTRAL_ALL: each part as light as TS draws it, against all of TS's greys and darks on it - TS shades
# its metal dark, and matched to the light greys alone it came out near white; the gun as its forearm, a little lighter)
MAT['cyborg'] = {I.HELMET: (176, 176, 143), I.VISOR: (150, 150, 109), I.FACE: (52, 52, 40), I.JAW: (161, 161, 137),
                 I.VEST: (107, 107, 106), I.ABDOMEN: (44, 44, 44), I.PELVIS: (100, 99, 98), I.BELT: (28, 28, 28),
                 I.UARM: (100, 100, 99), I.FARM: (127, 127, 125), I.HAND: (44, 44, 44), I.KNEE: (235, 235, 235),
                 I.SHIN: (155, 155, 155), I.BOOT: (139, 139, 139), I.RIFLE: (150, 150, 150), I.RIFLE_DARK: (28, 28, 28),
                 I.LIGHT: (220, 40, 16), I.POUCH: (99, 99, 98)}
HOUSE['cyborg'] = (I.PAD, I.CHEST, I.THIGH)
GLINT_ADD['cyborg'] = 0
NO_GLOW_ADD = NO_GLOW_ADD + ('cyborg',)
VISOR_ADD['cyborg'] = ((0, 0, 0), (0, 0, 0), (225, 220, 196))


# ---------------------------------------------------------------------------------------------------- Nod: Cyborg Commando
# TS's CYC2: a dark grey helmet, a light grey faceplate; house green (TS's darker remap greens) over the shoulders,
# chest and belly; dark grey metal arms and legs, lighter grey shins; the plasma cannon (dark) in its right forearm.
# Its deaths crackle with TS's blue-white arcs and burst in its flash colours: effects, left out of the fit
CLASSES['cyc2'] = {I.HELMET: I.DARK, I.VISOR: I.GREY, I.FACE: I.GREY, I.JAW: I.DARK, I.CHEST: I.GREEN, I.VEST: I.DARK,
                   I.ABDOMEN: I.GREEN, I.PELVIS: I.DARK, I.BELT: I.DARK, I.PAD: I.GREEN, I.UARM: I.DARK,
                   I.FARM: I.DARK, I.HAND: I.DARK, I.THIGH: I.DARK, I.POUCH: I.DARK, I.KNEE: I.GREY, I.SHIN: I.GREY,
                   I.BOOT: I.DARK, I.RIFLE: I.DARK, I.RIFLE_DARK: I.DARK}
WARM['cyc2'] = 'arcs'
SSPEC_DROP['cyc2'] = SSPEC_DROP['cyborg']
SSPEC_ADD['cyc2'] = ([(k, lo * 1.35, hi * 1.35) for k, lo, hi in F.SSPEC if k in _BIG] +
                     [('gl', 6.0, 13.0), ('gt', 1.6, 3.6), ('gg', 0.5, 5.0), ('ttp', 0.4, 1.0), ('stp', 0.55, 1.1)])
TSPEC_DROP['cyc2'] = ('pk', 'po')
TSPEC_ADD['cyc2'] = []
# (standing: the cannon held level ahead at its chest - TS's side views - the left arm hanging)
STAND_Q['cyc2'] = dict(I.Q0, ik=0.0, garm=1.0, lsf=5.0, lsa=12.0, lst=0.0, lef=15.0, rsf=15.0, rsa=10.0, rst=0.0,
                       ref=75.0, lha=4.0, rha=4.0, lhf=4.0, rhf=-4.0, lkf=6.0, rkf=4.0)
# (infcalib.py, NEUTRAL_ALL: each part as light as TS draws it, against all of TS's greys and darks on it)
MAT['cyc2'] = {I.HELMET: (90, 90, 90), I.VISOR: (34, 34, 34), I.FACE: (161, 161, 161), I.JAW: (44, 44, 44),
               I.VEST: (26, 26, 26), I.PELVIS: (120, 120, 120), I.BELT: (28, 28, 28), I.UARM: (88, 88, 88),
               I.FARM: (82, 82, 82), I.HAND: (36, 36, 36), I.THIGH: (63, 63, 63), I.POUCH: (75, 75, 75),
               I.KNEE: (97, 97, 97), I.SHIN: (72, 72, 72), I.BOOT: (80, 80, 80), I.RIFLE: (151, 151, 151),
               I.RIFLE_DARK: (77, 77, 77)}
HOUSE['cyc2'] = (I.PAD, I.CHEST, I.ABDOMEN)
GLINT_ADD['cyc2'] = 0
VISOR_ADD['cyc2'] = ((200, 200, 205), (130, 130, 135), (210, 210, 215))

_BASE = dict(CLASS=dict(I.CLASS), SSPEC=list(F.SSPEC), TSPEC=list(F.TSPEC), MAT=dict(R.MAT), HOUSE=R.HOUSE,
             ts_classes=F.ts_classes)
CURRENT = [None]


def ts_classes_for(unit):
    base = _BASE['ts_classes']
    if WARM.get(unit, 'fx') == 'fx':
        return base

    def classes(a):
        c = base(a)
        r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
        warm = c == F.FX
        red = (r == 255) & (g == 0) & (b == 0)
        if WARM[unit] == 'medic':
            # the Medic: his skin (TS's flesh tones keep their blue) and his orange (TS's orange ramp, little blue); the
            # red crosses' pure red left out
            skin = warm & ~red & (b > 0.45 * r)
            c = np.where(skin, I.SKIN, np.where(warm & ~red, I.ORANGE, c))
            return c
        if WARM[unit] == 'arcs':
            # (the Cyborg Commando: TS's blue-white arcs - its blue-tinted greys, pure blue and pure white - are effects,
            # as its flash colours; nothing of it is blue)
            rf, gf, bf = r.astype(float), g.astype(float), b.astype(float)
            arcs = (al > 0) & ((bf > rf + 30) | ((r == 255) & (g == 255) & (b == 255)))
            return np.where(arcs | (warm & ~red) | red, F.FX, c)
        if WARM[unit] == 'skin_olive':
            # (the Hijacker: his skin is TS's flesh ramp - red well above green; the coat's olive yellows (red and green
            # level) are its darks and greys)
            rf, gf, bf = r.astype(float), g.astype(float), b.astype(float)
            w = warm & ~red
            skin = w & (rf - gf > 25)
            # (every olive pixel - red and green level, blue well under them, dark or light - is the coat: one class,
            # so its mottling doesn't read as two materials; TS's neutral greys are his lower legs)
            olive = (al > 0) & ~skin & (np.abs(rf - gf) < 14) & (rf - bf > 14) & (c != F.FX) | (w & ~skin)
            return np.where(skin, I.SKIN, np.where(olive, I.DARK, c))
        if WARM[unit] in ('skin', 'skin_hair'):
            # the Ghost: his skin is warm; the railgun's flash (TS's three flash yellows) stays an effect
            import infx
            flash = (g == 0) & (b == 0) & (r > 120)        # the flash's red edge (and blood)
            for col in infx.WEIGHT:
                flash |= (r == col[0]) & (g == col[1]) & (b == col[2])
            w = warm & ~red & ~flash
            if WARM[unit] == 'skin_hair':
                # (Umagon: her hair is TS's darkest flesh tones - near black red-brown - her skin the lighter ones)
                mean = (r.astype(float) + g + b) / 3.0
                return np.where(w & (mean < HAIR_DARK), I.DARK, np.where(w, I.SKIN, c))
            return np.where(w, I.SKIN, c)
        c = np.where(warm & ~red, I.YELLOW if WARM[unit] == 'yellow' else I.ORANGE, c)
        return c
    return classes


# units whose edge pixels the fit counts as dark: TS drew its sprites on black, so the edge pixels of a bright part
# come out dark (E1 and E2 are dark all round; the Engineer is bright yellow)
EDGE_DARK = ('eng',) + (('jj',) if __import__('os').environ.get('JJ_EDGE') else ())
# steps a cycle in the run and crawl (TS's CyborgSequence: 9)
CYCLE_N = {'cyc2': 9}
# units the mod never had (Nod - Luke: "Nod never made it into my mod"): no in-mod frames, so no TS shadow to fit to
NO_TS_SHADOW = ('e3', 'cyborg', 'cyc2', 'mhijack', 'chamspy', 'elcad', 'umagon')
def mod_label(unit, long=False):
    """what the previews call the frame beside TS's: the mod's own (GDI), or - Nod, never in the mod - TS's sprite
    scaled onto the canvas where the mod puts the GDI units'."""
    if unit in NO_TS_SHADOW:
        return "TS's sprite scaled onto the canvas" if long else 'TS x3.07'
    return 'as the mod has it' if long else 'in-mod'


# the colour class TS draws a unit's long gun in (gunline/infsmooth: the longest straight run of it is TS's gun)
# (None: no gun line - Umagon's black rifle can't be told from her dark clothes and TS's black outlines frame by frame
# ('black', TS's pure black, finds it in most frames but not all), and the cyborgs' guns are built into forearms the
# same grey (dark grey) as their metal limbs, so the longest straight run of that colour is a leg as often as the gun;
# their guns are placed by the silhouette and colours alone)
GUN_CLASS = {'e3': I.GREY, 'cyborg': None, 'cyc2': None, 'elcad': I.GREY, 'umagon': None}
# the class TS draws the helmet's glint in (E1, E2: its light blue; the Engineer's yellow hood: no glint class)
GLINT = {'eng': 0, 'ghost': 0, 'medic': 0}
# the faceplate's glow (facing the camera, at its edge) and the helmet's glint colour
VISOR = {'e1': ((160, 160, 240), (104, 104, 180), (170, 170, 240)),
         'eng': ((226, 226, 226), (150, 150, 150), (255, 248, 210)),
         'ghost': ((0, 0, 0), (0, 0, 0), (88, 88, 120)),
         'medic': ((0, 0, 0), (0, 0, 0), (225, 225, 225))}
# units whose faceplate glows (the soldiers' visors); the Ghost's is his bare face, the Medic's is dark glass
NO_GLOW = ('ghost', 'medic')
# a dark glass faceplate's sky: TS draws the Medic's faceplate dark grey looking ahead (85, 60) and blue-grey lying face
# up (149,149,174; 137,137,161; 174,174,198): it shows this colour as it turns to the sky
VISOR_SKY = {'medic': (149, 149, 174)}
# (the Nod units' entries, set with their colours above)
GLINT.update(GLINT_ADD)
NO_GLOW = NO_GLOW + NO_GLOW_ADD
VISOR.update(VISOR_ADD)


# units drawn in their makeover's colours (the Engineer's ochre); on from the start when the unit's shape file has
# look 2, or set by set_look()
LOOK2 = {}


def set_look(unit, on=True):
    LOOK2[unit] = bool(on)
    if CURRENT[0] == unit:
        use(unit)


def _shape_look(unit):
    try:
        import json
        return json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '%s_shape.json' % unit)))['S'].get('look', 1) >= 2
    except Exception:
        return False


def use(unit):
    if unit not in LOOK2:
        LOOK2[unit] = _shape_look(unit)
    """switch the shared modules to this unit."""
    u = UNITS[unit]
    for k, v in UNITS.items():
        F.UNITS[k] = (v['dir'], v['name'])
    I.CLASS.clear(); I.CLASS.update(_BASE['CLASS']); I.CLASS.update(CLASSES.get(unit, {}))
    F.ts_classes = ts_classes_for(unit)
    F.SSPEC[:] = [t for t in _BASE['SSPEC'] if t[0] not in SSPEC_DROP.get(unit, ())] + SSPEC_ADD.get(unit, [])
    F.TSPEC[:] = [t for t in _BASE['TSPEC'] if t[0] not in TSPEC_DROP.get(unit, ())] + TSPEC_ADD.get(unit, [])
    if STAND_Q.get(unit):
        F.STAND_Q = dict(STAND_Q[unit])
    F.S0 = s0(unit)
    F.CW[:] = 1.0
    for c, w in CLASS_W.get(unit, {}).items():
        F.CW[c] = w
    R.K, R.DX, R.DY = u['K'], u['DX'], u['DY']
    R.PPU = u['K']                     # HD's scale follows the mod's (canvas px per TS px)
    # (how much bigger HD draws the fitted soldier than TS's sprite: 1.08 made him as tall as the mod's frames; a unit
    # with 'vis' is drawn as tall as its EA counterpart instead - Luke: the Light Infantry must match TD's and RA's
    # infantry sizes; EA's rifleman stands 60.6 px in both)
    R.VIS = u.get('vis', 1.08)
    R.MAT = dict(MAT.get(unit, _BASE['MAT']))
    R.HOUSE = HOUSE.get(unit, _BASE['HOUSE'])
    R.RAMP = dict(RAMP.get(unit, {}))
    if unit == 'e3' and LOOK2.get('e3'):
        R.MAT.update(MAT_E3_LOOK2)
        R.HOUSE = HOUSE_E3_LOOK2
        I.CLASS.update({830: I.DARK, 831: I.DARK, 832: I.GREEN, 833: I.GREEN, 834: I.GREY, 835: I.GREEN, 836: I.GREY,
                        837: I.DARK, 838: I.DARK, 839: I.DARK, 840: I.DARK, 841: 6, 842: I.GREEN, 843: 6, 844: I.DARK,
                        845: I.DARK, 846: I.DARK})
    if unit == 'medic' and LOOK2.get('medic'):
        R.RAMP.update(RAMP_MEDIC_LOOK2)
        R.MAT.update(MAT_MEDIC_LOOK2)
        R.HOUSE = HOUSE_MEDIC_LOOK2
        I.CLASS.update({810: I.GREY, 811: I.GREY, 812: I.GREEN, 813: I.GREEN, 814: I.DARK, 815: I.GREY, 816: I.ORANGE,
                        817: I.GREY, 818: I.GREY, 819: I.DARK, 820: I.DARK, 821: I.DARK, 822: I.DARK})
    if unit == 'eng' and LOOK2.get('eng'):
        R.RAMP = dict(RAMP_ENG_LOOK2)
        R.MAT.update(MAT_ENG_LOOK2)
        R.HOUSE = HOUSE_ENG_LOOK2
        I.CLASS.update({796: I.GREEN, 797: I.YELLOW, 798: I.GREY, 799: I.DARK, 800: 6, 801: I.DARK, 802: I.GREY,
                        782: I.YELLOW, I.HAND: I.DARK, I.TOOLBOX: I.DARK, I.VISOR: I.LBLUE})
    F.GLINT_CLASS = GLINT.get(unit, I.LBLUE)
    F.EDGE_DARK = unit in EDGE_DARK
    F.TS_SHADOW = unit not in NO_TS_SHADOW
    R.VISOR_SHOW, R.VISOR_EDGE, R.HELMET_GLINT = [np.asarray(v, float) for v in VISOR.get(unit, VISOR['e1'])]
    if unit == 'eng' and LOOK2.get('eng'):
        R.VISOR_SHOW, R.VISOR_EDGE = [np.asarray(v, float) for v in VISOR['e1'][:2]]
        R.HELMET_GLINT = np.array([236.0, 214.0, 150.0])
    R.VISOR_GLOW = unit not in NO_GLOW
    R.VISOR_SKY = None if unit not in VISOR_SKY else np.asarray(VISOR_SKY[unit], float)
    if unit == 'e3' and LOOK2.get('e3'):
        # (his makeover's visor: the concept's red glass, glowing as the soldiers' blue does)
        R.VISOR_GLOW = True
        R.VISOR_SHOW, R.VISOR_EDGE = np.array([240.0, 60.0, 50.0]), np.array([150.0, 24.0, 20.0])
        if E3_VISOR == 'blue':
            R.VISOR_SHOW, R.VISOR_EDGE = [np.asarray(v, float) for v in VISOR['e1'][:2]]
        R.HELMET_GLINT = np.array([150.0, 150.0, 160.0])
    if unit == 'medic' and LOOK2.get('medic'):
        # (his makeover's visor: the references' blue glass, glowing as the soldiers')
        R.VISOR_GLOW, R.VISOR_SKY = True, None
        R.VISOR_SHOW, R.VISOR_EDGE = [np.asarray(v, float) for v in VISOR['e1'][:2]]
        R.HELMET_GLINT = np.array([250.0, 250.0, 250.0])
    if unit not in SQ.SEQ:
        SQ.SEQ[unit] = dict(SQ.SEQ['e1'])
    CURRENT[0] = unit
    import sys as _sys
    if 'infcycle' in _sys.modules:                  # (its steps a cycle: 9 for the Cyborg Commando)
        _sys.modules['infcycle'].N = CYCLE_N.get(unit, 6)
    return u


def s0(unit):
    return dict({'e2': I.S0_E2, 'eng': I.S0_ENG, 'ghost': I.S0_GHOST, 'jj': I.S0_JJ, 'medic': I.S0_MEDIC,
                 'e3': I.S0_E3, 'elcad': I.S0_ELCAD, 'umagon': I.S0_UMAGON, 'chamspy': I.S0_CHAMSPY,
                 'mhijack': I.S0_MHIJACK, 'cyborg': I.S0_CYBORG, 'cyc2': I.S0_CYC2}.get(unit, I.S0))
