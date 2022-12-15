# Defines Project Wide Constants

YDS_GRADES_FULL = ['5.0', '5.1', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.7+', '5.8-', '5.8', '5.8+', '5.9-', '5.9', '5.9+',
                   '5.10a', '5.10-', '5.10a/b', '5.10b', '5.10', '5.10b/c', '5.10c', '5.10+', '5.10c/d', '5.10d', '5.11a', '5.11-', '5.11a/b', '5.11b', '5.11', '5.11b/c', '5.11c', '5.11+', '5.11c/d', '5.11d',
                   '5.12a', '5.12-', '5.12a/b', '5.12b', '5.12', '5.12b/c', '5.12c', '5.12+', '5.12c/d', '5.12d', '5.13a', '5.13-', '5.13a/b', '5.13b', '5.13', '5.13b/c', '5.13c', '5.13+', '5.13c/d', '5.13d',
                   '5.14a', '5.14-', '5.14a/b', '5.14b', '5.14', '5.14b/c', '5.14c', '5.14+', '5.14c/d', '5.14d', '5.15a', '5.15-', '5.15a/b', '5.15b', '5.15', '5.15b/c' '5.15c', '5.15+', '5.15c/d', '5.15d']
YDS_GRADES_LETTER = ['5.0', '5.1', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.8', '5.9', '5.10a', '5.10b', '5.10c', '5.10d', '5.11a', '5.11b', '5.11c', '5.11d',
                     '5.12a', '5.12b', '5.12c', '5.12d', '5.13a', '5.13b', '5.13c', '5.13d', '5.14a', '5.14b', '5.14c', '5.14d', '5.15a', '5.15b', '5.15c', '5.15d']
YDS_GRADES_SIGN = ['5.0', '5.1', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.7+', '5.8-', '5.8', '5.8+', '5.9-', '5.9', '5.9+', '5.10-', '5.10', '5.10+',
                   '5.11-', '5.11', '5.11+', '5.12-', '5.12', '5.12+', '5.13-', '5.13', '5.13+', '5.14-', '5.14', '5.14+', '5.15-', '5.15', '5.15+']

V_GRADES_FULL = ['V-easy', 'V0-', 'V0', 'V0+', 'V0-1', 'V1-', 'V1', 'V1+', 'V1-2', 'V2-', 'V2', 'V2+', 'V2-3', 'V3-', 'V3', 'V3+', 'V3-4', 'V4-', 'V4', 'V4+', 'V4-5', 'V5-', 'V5', 'V5+', 'V5-6',
                 'V6-', 'V6', 'V6+', 'V6-7', 'V7-', 'V7', 'V7+', 'V7-8', 'V8-', 'V8', 'V8+', 'V8-9', 'V9-', 'V9', 'V9+', 'V9-10', 'V10-', 'V10', 'V10+', 'V10-11', 'V11-', 'V11', 'V11+', 'V11-12',
                 'V12-', 'V12', 'V12+', 'V12-13', 'V13-', 'V13', 'V13+', 'V13-14', 'V14-', 'V14', 'V14+', 'V14-15', 'V15-', 'V15', 'V15+', 'V15-16', 'V16-', 'V16', 'V16+', 'V16-17', 'V17-', 'V17']
V_GRADES_SIGN = ['V-easy', 'V0-', 'V0', 'V0+', 'V1-', 'V1', 'V1+', 'V2-', 'V2', 'V2+', 'V3-', 'V3', 'V3+', 'V4-', 'V4', 'V4+', 'V5-', 'V5', 'V5+', 'V6-', 'V6', 'V6+', 'V7-', 'V7', 'V7+', 'V8-', 'V8', 'V8+',
                 'V9-', 'V9', 'V9+', 'V10-', 'V10', 'V10+', 'V11-', 'V11', 'V11+', 'V12-', 'V12', 'V12+', 'V13-', 'V13', 'V13+', 'V14-', 'V14', 'V14+', 'V15-', 'V15', 'V15+', 'V16-', 'V16', 'V16+', 'V17-', 'V17']
V_GRADES_FLAT = ['V-easy', 'V0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7',
                 'V8', 'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17']

GRADES_SUPER = YDS_GRADES_FULL + V_GRADES_FULL

RISK_GRADES = ['PG', 'PG13', 'R', 'X']
ROUTE_TYPES = ['Boulder', 'Sport', 'Trad']

CLEAN_SEND = ['Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Send']
CLEAN_SEND_FIRST = ['Onsight', 'Flash']
CLEAN_SEND_WORKED = ['Redpoint', 'Pinkpoint']
TICK_OPTIONS = ['Solo', 'TR', 'Follow', 'Lead', 'Fell/Hung',
                'Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Send', 'Attempt']

# Roped grade homogenization
# Letter
rgrademoderatemap = {'5.6-': '5.6', '5.6+': '5.6', '5.7-': '5.7',
                     '5.7+': '5.7', '5.8-': '5.8', '5.8+': '5.8', '5.9-': '5.9', '5.9+': '5.9'}
rgradedownmap = {'5.10a/b': '5.10a', '5.10-': '5.10a', '5.10b/c': '5.10b', '5.10': '5.10b', '5.10c/d': '5.10c', '5.10+': '5.10c',
                 '5.11a/b': '5.11a', '5.11-': '5.11a', '5.11b/c': '5.11b', '5.11': '5.11b', '5.11c/d': '5.11c', '5.11+': '5.11c',
                 '5.12a/b': '5.12a', '5.12-': '5.12a', '5.12b/c': '5.12b', '5.12': '5.12b', '5.12c/d': '5.12c', '5.12+': '5.12c',
                 '5.13a/b': '5.13a', '5.13-': '5.13a', '5.13b/c': '5.13b', '5.13': '5.13b', '5.13c/d': '5.13c', '5.13+': '5.13c',
                 '5.14a/b': '5.14a', '5.14-': '5.14a', '5.14b/c': '5.14b', '5.14': '5.14b', '5.14c/d': '5.14c', '5.14+': '5.14c',
                 '5.15a/b': '5.15a', '5.15-': '5.15a', '5.15b/c': '5.15b', '5.15': '5.15b', '5.15c/d': '5.15c', '5.15+': '5.15c',
                 }
rgradeupmap = {'5.10a/b': '5.10b', '5.10-': '5.10b', '5.10b/c': '5.10c', '5.10': '5.10c', '5.10c/d': '5.10d', '5.10+': '5.10d',
               '5.11a/b': '5.11b', '5.11-': '5.11b', '5.11b/c': '5.11c', '5.11': '5.11c', '5.11c/d': '5.11d', '5.11+': '5.11d',
               '5.12a/b': '5.12b', '5.12-': '5.12b', '5.12b/c': '5.12c', '5.12': '5.12c', '5.12c/d': '5.12d', '5.12+': '5.12d',
               '5.13a/b': '5.13b', '5.13-': '5.13b', '5.13b/c': '5.13c', '5.13': '5.13c', '5.13c/d': '5.13d', '5.13+': '5.13d',
               '5.14a/b': '5.14b', '5.14-': '5.14b', '5.14b/c': '5.14c', '5.14': '5.14c', '5.14c/d': '5.14d', '5.14+': '5.14d',
               '5.15a/b': '5.15b', '5.15-': '5.15b', '5.15b/c': '5.15c', '5.15': '5.15c', '5.15c/d': '5.15d', '5.15+': '5.15d',
               }

# Sign
rgradecompmap = {'5.10a': '5.10-', '5.10a/b': '5.10-', '5.10b': '5.10', '5.10c': '5.10', '5.10b/c': '5.10', '5.10d': '5.10+', '5.10c/d': '5.10+',
                 '5.11a': '5.11-', '5.11a/b': '5.11-', '5.11b': '5.11', '5.11c': '5.10', '5.11b/c': '5.11', '5.11d': '5.11+', '5.11c/d': '5.11+',
                 '5.12a': '5.12-', '5.12a/b': '5.12-', '5.12b': '5.12', '5.12c': '5.10', '5.12b/c': '5.12', '5.12d': '5.12+', '5.12c/d': '5.12+',
                 '5.13a': '5.13-', '5.13a/b': '5.13-', '5.13b': '5.13', '5.13c': '5.10', '5.130b/c': '5.13', '5.13d': '5.13+', '5.13c/d': '5.13+',
                 '5.14a': '5.14-', '5.14a/b': '5.14-', '5.14b': '5.14', '5.14c': '5.10', '5.14b/c': '5.14', '5.14d': '5.14+', '5.14c/d': '5.14+',
                 }

# Boulder grade homogenization
# Flat
bgradedownmap1 = {'V0-1': 'V0', 'V1-2': 'V1', 'V2-3': 'V2', 'V3-4': 'V3', 'V4-5': 'V4', 'V5-6': 'V5', 'V6-7': 'V6', 'V7-8': 'V7', 'V8-9': 'V8', 'V9-10': 'V9', 'V10-11': 'V10', 'V11-12': 'V11',
                  'V12-13': 'V12', 'V13-14': 'V13', 'V14-15': 'V14', 'V15-16': 'V15', 'V16-17': 'V16'}
bgradeupmap1 = {'V0-1': 'V1', 'V1-2': 'V2', 'V2-3': 'V3', 'V3-4': 'V4', 'V4-5': 'V5', 'V5-6': 'V6', 'V6-7': 'V7', 'V7-8': 'V8', 'V8-9': 'V9', 'V9-10': 'V10', 'V10-11': 'V11', 'V11-12': 'V12',
                'V12-13': 'V13', 'V13-14': 'V14', 'V14-15': 'V15', 'V15-16': 'V16', 'V16-17': 'V17'}
bgradeconmap1 = {'V0-': 'V0', 'V0+': 'V0', 'V1-': 'V1', 'V1+': 'V1', 'V2-': 'V2', 'V2+': 'V2', 'V3-': 'V3', 'V3+': 'V3', 'V4-': 'V4', 'V4+': 'V4', 'V5-': 'V5', 'V5+': 'V5', 'V6-': 'V6', 'V6+': 'V6', 'V7-': 'V7', 'V7+': 'V7', 'V8-': 'V8', 'V8+': 'V8',
                 'V9-': 'V9', 'V9+': 'V9', 'V10-': 'V10', 'V10+': 'V10', 'V11-': 'V11', 'V11+': 'V11', 'V12-': 'V12', 'V12+': 'V12', 'V13-': 'V13', 'V13+': 'V13', 'V14-': 'V14', 'V14+': 'V14', 'V15-': 'V15', 'V15+': 'V15', 'V16-': 'V16', 'V16+': 'V16',
                 'V17-': 'V17', 'V17+': 'V17'}
# Sign
bgradedownmap2 = {'V0-1': 'V0+', 'V1-2': 'V1+', 'V2-3': 'V2+', 'V3-4': 'V3+', 'V4-5': 'V4+', 'V5-6': 'V5+', 'V6-7': 'V6+', 'V7-8': 'V7+', 'V8-9': 'V8+', 'V9-10': 'V9+', 'V10-11': 'V10+', 'V11-12': 'V11+', 'V12-13': 'V12+', 'V13-14': 'V13+',
                  'V14-15': 'V14+', 'V15-16': 'V15+', 'V16-17': 'V16+'}
bgradeupmap2 = {'V0-1': 'V1-', 'V1-2': 'V2-', 'V2-3': 'V3-', 'V3-4': 'V4-', 'V4-5': 'V5-', 'V5-6': 'V6-', 'V6-7': 'V7-', 'V7-8': 'V8-', 'V8-9': 'V9-', 'V9-10-': 'V10', 'V10-11': 'V11-', 'V11-12': 'V12-', 'V12-13': 'V13-', 'V13-14': 'V14-',
                'V14-15': 'V15-', 'V15-16': 'V16-', 'V16-17': 'V17-'}