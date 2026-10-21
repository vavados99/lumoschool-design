#!/usr/bin/env python3
"""Круг 3: замеры -> замеры.json + проверки силуэта (ч/б 64 px). /usr/local/lib/hermes-agent/venv/bin/python measure3.py"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw
import build3 as B
import wordmark3 as WM
import make3 as M
D = B.D
cr = M.cr

def hull(pts):
    pts = sorted(set((round(x, 3), round(y, 3)) for x, y in pts))
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo = []; 
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    up = []
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1]+up[:-1]

# круг-2 капля (без изгиба кончика) для сравнения
OLD_DROP = parse = B.parse("M222 22C238 42 262 98 296 150C338 218 358 292 346 360C334 430 282 478 200 478C118 478 66 430 54 360C42 292 62 218 104 154C140 100 184 66 204 38C210 28 216 20 222 22Z")

def solidity(segs):
    p = B.flat(segs, 40); return B.area(p)/B.area(hull(p))
def mirror_iou(segs, W=400, H=500):
    """совпадение силуэта с зеркальным отражением относительно оси x=200 (1.0 = симметричная капля)"""
    im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).polygon(B.flat(segs, 40), fill=255)
    a = np.array(im) > 0; b = a[:, ::-1]
    return float((a & b).sum()/(a | b).sum())
def min_margin(core, body):
    """минимальный отступ контура сердцевины до контура тела (ед. сетки 400x500)"""
    c = np.array(B.flat(core, 60)); b = np.array(B.flat(body, 60))
    # плотная дискретизация отрезков
    def dense(p):
        out = []
        for i in range(len(p)-1):
            for t in np.linspace(0, 1, 6): out.append(p[i]*(1-t)+p[i+1]*t)
        return np.array(out)
    c = dense(c); b = dense(b)
    return float(np.min(np.sqrt(((c[:, None, :]-b[None, :, :])**2).sum(-1))))

def render_cov(segs_list, px, bg, fg_list):
    pass

res = {}
A_body = B.A_BODY; A_core = B.A_CORE
eye_gap = (B.EYE['cx'][1]-B.EYE['cx'][0]-2*B.EYE['rx'])*B.SC
eye_w = 2*B.EYE['rx']*B.SC; eye_h = 2*B.EYE['ry']*B.SC
tipx, tipy = 276, 18
res['сердцевина'] = {
    'площадь_%_от_контура_знака': round(100*A_core/A_body, 2),
    'площадь_%_от_знака_без_глаз': round(100*A_core/(A_body-B.eye_area()), 2),
    'масштаб_к_эталону_формы': round(B.K_CORE, 3),
    'низ_сердцевины_y_сетка': 316, 'верх_глаз_y_сетка': B.EYE['cy']-B.EYE['ry'], 'центр_глаз_y_сетка': B.EYE['cy'],
    'минимальный_отступ_до_контура_ед_сетки': round(min_margin(B.CORE_S, B.BODY_S), 1),
    'отступ_на_64px_px': round(min_margin(B.CORE_S, B.BODY_S)*B.SC*0.64, 2),
}
res['глаза'] = {
    'зазор_между_глазами_ед_viewBox100': round(eye_gap, 2), 'было_круг2': 6.56,
    'ширина_глаза_ед': round(eye_w, 2), 'высота_глаза_ед': round(eye_h, 2),
    'зазор_на_32px_px': round(eye_gap*0.32, 2), 'зазор_на_64px_px': round(eye_gap*.64, 2),
    'зазор_16px_мастер_px': 2,
    'как_у_героя': 'герой B5-тьма: тёмные глаза #2A1030 (rx31 ry39) + круглый блик ≈20% ширины; в знаке глаза тёмные #2A1030 с бликом (>=64px) / #2A1A2E без блика (<=40px); светлые глаза не взяты: слились бы с кремовой сердцевиной и дали «череп»',
}
res['наклон_кончика_градусы'] = {
    'ось_от_центра_основания_(200,330)_к_вершине': round(math.degrees(math.atan2(tipx-200, 330-tipy)), 1), 'было_круг2': 12.1,
    'касательная_у_самого_кончика_от_вертикали': round(math.degrees(math.atan2(276-260, 40-18)), 1),
    'завиток_правого_верха_250,50->276,18': round(math.degrees(math.atan2(276-250, 50-18)), 1),
}
res['силуэт'] = {
    'выпуклость_solidity_(капля≈0.99)': {'круг3': round(solidity(B.BODY_S), 3), 'круг2_капля_без_изгиба': round(solidity(OLD_DROP), 3)},
    'зеркальное_совпадение_IoU_(1.0=симметрично)': {'круг3': round(mirror_iou(B.BODY_S), 3), 'круг2_капля': round(mirror_iou(OLD_DROP), 3)},
}
# контрасты
BODY = B.BODY_C
res['контраст_WCAG'] = {
    'тело #DF5520 на тёмном #1E1424 (знак)': cr(BODY, B.DARKBG),
    'тело #DF5520 на светлом #FBEFDF (знак)': cr(BODY, B.CREAM),
    'тело #DF5520 на белом': cr(BODY, '#FFFFFF'),
    'сердцевина кремовая на теле #DF5520': cr(B.CREAM, BODY),
    'сердцевина кремовая на #FF7A45 (круг2, не годилось)': cr(B.CREAM, '#FF7A45'),
    'глаза #2A1030 на теле': cr(B.HEROINK, BODY),
    'глаза светлые (кремовые) на теле — отвергнуто': cr(B.CREAM, BODY),
    'простой знак ≤40: #FF7A45 на тёмном': cr(B.ORANGE_D, B.DARKBG),
    'простой знак ≤40: #DF5520 на светлом': cr(B.ORANGE_L, B.CREAM),
    'фавикон 16: #FF7A45 на вкладке тёмной #35363A': cr(B.ORANGE_D, '#35363A'),
    'фавикон 16: #FF7A45 на #202124': cr(B.ORANGE_D, '#202124'),
    'фавикон 16: #D24C16 на вкладке светлой #DEE1E6': cr(M.FAV_L, '#DEE1E6'),
    'фавикон 16: #D24C16 на белой #FFFFFF': cr(M.FAV_L, '#FFFFFF'),
    'фавикон 16: глаза на теле': cr(B.INK, B.ORANGE_D),
    'вордмарк кремовый на тёмном': cr(B.CREAM, B.DARKBG), 'вордмарк чернила на светлом': cr(B.INK, B.CREAM),
}
# пиксели сердцевины на 32 и 64
def core_px(px, ss=16):
    n = px
    def m(segs):
        im = Image.new('L', (n*ss, int(n*ss)), 0); d = ImageDraw.Draw(im)
        d.polygon([(B.T(*p)[0]/100*n*ss, B.T(*p)[1]/100*n*ss) for p in B.flat(segs, 40)], fill=255)
        return np.array(im).reshape(n, ss, n, ss).mean(axis=(1, 3))/255
    c = m(B.CORE_S); b = m(B.BODY_S)
    return {'ядро_px_суммарно(покрытие)': round(float(c.sum()), 1), 'ядро_px_с_покрытием>=0.9': int((c >= .9).sum()), 'тело_px': round(float(b.sum()), 1)}
res['сердцевина_на_размерах'] = {'32px': core_px(32), '64px': core_px(64)}
# кернинг
kp = WM.kern_pairs()[0]
xs0, _ = WM.positions(kp, {}); xs1, _ = WM.positions(kp, WM.MANUAL)
g0 = WM.optical_gaps(xs0); g1 = WM.optical_gaps(xs1)
res['вордмарк'] = {
    'шрифт': 'Golos Text wght 600 (файлы сайта), трекинг -0.02em, GPOS-кернинг снят в Chromium/HarfBuzz при 1000 px, контуры fontTools',
    'GPOS_кернинг_ед_на_1000': {p: dn for p, dn, d0 in kp if dn != 0} or 'нет', 'GPOS_только_L-u': 'в шрифте единственная кернпара в слове: L–u −10; остальные 0',
    'ручная_доводка_ед_на_1000': WM.MANUAL,
    'оптич_зазор_до_{пара,мин,оптич}': g0, 'оптич_зазор_после': g1,
    'мин_зазор_после_L-u_и_c-h': {p: m for p, m, o in g1 if p in ('Lu', 'ch')},
}
json.dump(res, open(D+'/замеры.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))

# ---- ч/б проверка 64 px ----
def silhouette_png(px):
    n = px; ss = 8
    im = Image.new('L', (n*ss, int(n*ss*1.0)), 255); d = ImageDraw.Draw(im)
    d.polygon([(B.T(*p)[0]/100*n*ss, B.T(*p)[1]/100*n*ss) for p in B.flat(B.BODY_S, 40)], fill=0)
    return im.resize((n, n), Image.LANCZOS)
sheet = Image.new('RGB', (64*4*2+60, 64*2*2+40), '#fff')
x = 10
for px in (64, 48, 32, 24):
    s = silhouette_png(px).convert('RGB'); sheet.paste(s.resize((px*2, px*2), Image.NEAREST), (x, 10)); x += px*2+10
sheet.save(D+'/проверка-силуэт-чб.png')
c64 = silhouette_png(64); c64.save(D+'/силуэт-64px-чб.png')
