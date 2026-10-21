import json, os
D = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(D + '/замеры.json'))
for k, v in r['читаемость'].items():
    for th in v:
        for s, m in v[th].items():
            print(k[:8], th, s, 'parts', m['parts'], m['main_color'], [(d['px'], d['contrast_vs_main']) for d in m['details']], 'aa', m['antialias_share'])
print(json.dumps(r['контраст_WCAG'], ensure_ascii=False, indent=1))
print(r['диакритика_нет_глифов'])
