"""Круг 6: кадры r6-* и замеры для В5-родитель -> прототипы-люмо/замеры-круг6.txt (+ В5-родитель/shots/r6-metrics.txt).
Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_r6.py"""
import os, io, re, colorsys
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(ROOT, 'В5-родитель'); URL = 'file://' + os.path.join(FOLDER, 'index.html'); SH = os.path.join(FOLDER, 'shots')
DEV = {'desktop': (1440, 900), 'phone': (390, 844)}
INIT = "window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});"
out = []
def P(s=''): print(s); out.append(s)

FONT_JS = """() => { const out=[]; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
 while(w.nextNode()){const n=w.currentNode; if(!n.textContent.trim())continue; const el=n.parentElement; if(!el||el.closest('script,style,svg,[hidden],.sr'))continue;
  const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden'||parseFloat(cs.opacity)===0)continue;
  const r=document.createRange(); r.selectNodeContents(n); const b=r.getBoundingClientRect(); if(b.width<1||b.height<1)continue;
  out.push([parseFloat(cs.fontSize), n.textContent.trim().slice(0,28)]);}
 out.sort((a,b)=>a[0]-b[0]); return out.slice(0,3);}"""

# тёплая точка: оранжевый/янтарный/красно-оранжевый, насыщенный и яркий
def warm_hsv(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255); h *= 360
    return (h <= 52 or h >= 345) and s >= .45 and v >= .6
DOM_WARM_JS = """() => {
 const res=[]; const vw=innerWidth, vh=innerHeight;
 const parse=c=>{const m=c.match(/[\\d.]+/g); if(!m)return null; const a=m.length>3?parseFloat(m[3]):1; return {r:+m[0],g:+m[1],b:+m[2],a}};
 for(const el of document.querySelectorAll('body *')){
  if(el.closest('svg')&&!el.matches('svg'))continue;
  const r=el.getBoundingClientRect(); if(r.width<2||r.height<2||r.bottom<0||r.top>vh||r.right<0||r.left>vw)continue;
  if(el.closest('[hidden]'))continue;
  const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden'||parseFloat(cs.opacity)===0)continue;
  const props=[['color',cs.color,!!el.childNodes.length&&[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())],['bg',cs.backgroundColor,true],['border',cs.borderTopColor,parseFloat(cs.borderTopWidth)>0&&cs.borderTopStyle!=='none']];
  for(const [k,c,use] of props){ if(!use)continue; const p=parse(c); if(p&&p.a>=.3) res.push({k,tag:el.tagName.toLowerCase(),cls:(el.className&&el.className.baseVal===undefined?el.className:'').toString().slice(0,30),c:[p.r,p.g,p.b],txt:(el.textContent||'').trim().slice(0,18),svg:!!el.matches('svg'),lumo:!!el.closest('.lumo-card')});}
 }
 return res;}"""

def pixel_points(png, blk=6):
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float) / 255
    mx, mn = im.max(2), im.min(2); v = mx; s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    d = np.maximum(mx - mn, 1e-9); r, g, b = im[..., 0], im[..., 1], im[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    m = ((h <= 52) | (h >= 345)) & (s >= .45) & (v >= .6) & (mx - mn > 0)
    H, W = m.shape; hb, wb = H // blk, W // blk
    cnt = m[:hb * blk, :wb * blk].reshape(hb, blk, wb, blk).sum((1, 3))
    grid = cnt >= 6
    # слияние в пределах 2 блоков (≈12 px)
    from itertools import product
    g2 = grid.copy()
    for dy, dx in product(range(-2, 3), repeat=2):
        g2 |= np.roll(np.roll(grid, dy, 0), dx, 1)
    lab = np.zeros(g2.shape, int); n = 0; comps = []
    for y, x in zip(*np.where(g2)):
        if lab[y, x]: continue
        n += 1; st = [(y, x)]; lab[y, x] = n; cells = []
        while st:
            cy, cx = st.pop(); cells.append((cy, cx))
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < g2.shape[0] and 0 <= nx < g2.shape[1] and g2[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n; st.append((ny, nx))
        ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
        px = int(sum(cnt[c] for c in cells if grid[c]))
        comps.append((px, xs and min(xs) * blk, min(ys) * blk, (max(xs) + 1) * blk, (max(ys) + 1) * blk))
    comps = [c for c in comps if c[0] >= 40]
    return sorted(comps, reverse=True)

def lumi(png, x, y):
    p = Image.open(io.BytesIO(png)).convert('RGB').getpixel((int(x), int(y))); return round(0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2], 1)

BAD_RE = re.compile(r'(закон|відповідно до|гарантуємо|гарантія|законом|без жодних|у будь-який момент|будь-коли|law requires|guarantee|at any time|any time)', re.I)
with sync_playwright() as pw:
    for dev, (w, h) in DEV.items():
        br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=(dev == 'phone')); ctx.add_init_script(INIT)
        pg = ctx.new_page(); cons = []
        pg.on('console', lambda m: cons.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
        pg.on('pageerror', lambda e: cons.append(('pageerror', str(e))))
        pg.on('requestfailed', lambda r: cons.append(('reqfail', r.url)))
        pg.goto(URL); pg.wait_for_timeout(1500)
        def snap(name, full=False): pg.screenshot(path=os.path.join(SH, f'r6-{dev}-{name}.png'), full_page=full)
        P(f'== В5 {dev} {w}x{h} ==')
        snap('1-first'); snap('1-full', True)
        png = pg.screenshot()
        sw = pg.evaluate("[document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth, document.documentElement.scrollHeight]")
        P(f'  ширина страницы: html {sw[0]} / body {sw[1]} против окна {sw[2]} -> {"OK" if sw[0] == sw[2] and sw[1] <= sw[2] else "ПЛОХО"}; высота {sw[3]}')
        mf = pg.evaluate(FONT_JS)
        P(f'  мин. шрифт: {mf[0][0]} px ({mf[0][1]!r}); след.: {mf[1:3]} -> {"OK" if mf[0][0] >= 16 else "ПЛОХО <16"}')
        # --- тёплые точки на первом экране ---
        comps = pixel_points(png)
        P(f'  ТЁПЛЫЕ ТОЧКИ, пиксельный замер (HSV: тон ≤52°/≥345°, насыщ ≥0,45, яркость ≥0,6; слияние ≤12 px; ≥40 px): {len(comps)} -> {"OK (≤4)" if len(comps) <= 4 else "ПЛОХО (>4)"}')
        for c in comps: P(f'     {c[0]:6d} px  область x {c[1]}–{c[3]}, y {c[2]}–{c[4]}')
        dm = pg.evaluate(DOM_WARM_JS)
        wl = [d for d in dm if warm_hsv(*d['c'])]
        lumo_n = [d for d in wl if d['lumo']]; other = [d for d in wl if not d['lumo']]
        P(f'  ТЁПЛЫЕ ЭЛЕМЕНТЫ по CSS (цвет текста/фона/рамки в видимой области, без Люмо и его реплики): {len(other)} {[(d["tag"], d["k"], d["txt"]) for d in other][:8]}; внутри блока Люмо: {len(lumo_n)} (считается как 1 точка); логотип — картинка, 1 точка')
        # --- расположение Люмо и света ---
        g = pg.evaluate("""()=>{const q=s=>{const e=document.querySelector(s); if(!e) return null; const r=e.getBoundingClientRect(); return [r.left,r.top,r.right,r.bottom]};
          return {lumo:q('#lumoBox'), say:q('#say'), card:q('#nextCard'), teacher:q('.teacher'), nav:q('#nav'), kids:q('.kids'), H:innerHeight}}""")
        lb, nc = g['lumo'], g['card']
        if dev == 'desktop':
            gap = nc[0] - lb[2]; cyL = (lb[1] + lb[3]) / 2
            P(f'  Люмо x {lb[0]:.0f}–{lb[2]:.0f}, y {lb[1]:.0f}–{lb[3]:.0f}; главная карточка x {nc[0]:.0f}–{nc[2]:.0f}, y {nc[1]:.0f}–{nc[3]:.0f}; зазор Люмо→карточка {gap:.0f} px (было ≈ 48+150: Люмо внизу под навигацией); центр Люмо по y {cyL:.0f} внутри диапазона карточки: {nc[1] <= cyL <= nc[3]}')
            sy = g['say']; P(f'  реплика Люмо y {sy[1]:.0f}–{sy[3]:.0f} при окне {g["H"]}: {"целиком в окне" if sy[3] <= g["H"] else "ОБРЕЗАНА"}')
            ny = lb[1] + 30
            P(f'  яркость карточки: у ближнего (левого) края на высоте Люмо {lumi(png, nc[0] + 24, ny)} против дальнего (правого) {lumi(png, nc[2] - 24, ny)}')
        else:
            P(f'  Люмо y {lb[1]:.0f}–{lb[3]:.0f}; карточка урока y {nc[1]:.0f}–{nc[3]:.0f}; учитель до y {g["teacher"][3]:.0f} при высоте {g["H"]} -> {"ВИДНО" if g["teacher"][3] <= g["H"] else "не виден"}  (r5: карточка с y 358, учитель до 632)')
            tb = pg.evaluate("document.querySelector('.topbar').getBoundingClientRect().bottom")
            P(f'  реплика Люмо y {g["say"][1]:.0f}–{g["say"][3]:.0f}; детей-чипы y {g["kids"][1]:.0f}–{g["kids"][3]:.0f}; шапка (логотип) до y {tb:.0f}')
        hero = pg.evaluate("document.querySelector('#nextCard .next-meta').textContent")
        P(f'  в карточке урока: «{hero}» (сегодня 21 жовт. -> слово «Сьогодні»: {"Сьогодні" in hero})')
        # --- согласия ---
        pg.evaluate("window.scrollTo({top: document.getElementById('consents').getBoundingClientRect().top + scrollY - (innerWidth<=820?150:90), behavior:'instant'})"); pg.wait_for_timeout(900)
        snap('2-consents')
        cs = pg.evaluate("""()=>{const q=s=>[...document.querySelectorAll(s)];
          const lab=q('.cons .stl').map(e=>({tag:e.tagName,txt:e.textContent.trim(),role:e.getAttribute('role'),tab:e.tabIndex,cur:getComputedStyle(e).cursor,bd:getComputedStyle(e).borderTopWidth,bg:getComputedStyle(e).backgroundColor,col:getComputedStyle(e).color}));
          const btn=q('.cons .btn-eq').map(e=>({txt:e.textContent.trim(),w:Math.round(e.getBoundingClientRect().width),h:Math.round(e.getBoundingClientRect().height),bg:getComputedStyle(e).backgroundColor,bd:getComputedStyle(e).borderTopColor,fs:getComputedStyle(e).fontSize}));
          const law=document.querySelector('.law').getBoundingClientRect(), cards=q('.cons').map(e=>e.getBoundingClientRect());
          return {lab,btn,lawW:Math.round(law.width),cardW:cards.map(c=>Math.round(c.width)),borders:q('.cons').map(e=>getComputedStyle(e).borderTopStyle),
                  cons:q('.cons').map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,200)), txt:document.querySelector('#consents').innerText}}""")
        P(f'  метки статуса: {[(l["tag"], l["txt"]) for l in cs["lab"]]}; кликабельны/фокус: {[l["tab"] for l in cs["lab"]]} (-1 = нет); курсор {set(l["cur"] for l in cs["lab"])}; рамка метки {set(l["bd"] for l in cs["lab"])}, фон {set(l["bg"] for l in cs["lab"])} -> метка, не кнопка: {all(l["tag"] == "SPAN" and l["tab"] == -1 for l in cs["lab"])}')
        P(f'  кнопки в блоке согласий: {[(b["txt"], str(b["w"]) + "x" + str(b["h"])) for b in cs["btn"]]}; одинаковые фон/рамка/шрифт: {len({(b["bg"], b["bd"], b["fs"]) for b in cs["btn"]}) == 1}')
        P(f'  ширина плашки «дитині менше 16» {cs["lawW"]} px против карточек {cs["cardW"]} -> {"равны" if len({cs["lawW"], *cs["cardW"]}) == 1 else "РАЗНЫЕ"}; стиль рамок карточек: {set(cs["borders"])} (пунктира нет: {"dashed" not in cs["borders"]})')
        c0 = cs['cons'][0]
        P(f'  карточка «Дані для навчання»: «{c0}»')
        P(f'  основание «для обучения» = договор: слово «договір» в карточке: {"договір" in c0.lower()}; слово «згода/згоду» в этой карточке в роли основания: {bool(re.search("надано|згод", c0.lower()))}; переключателя/«Відкликати» нет: {"Відкликати" not in c0}')
        P(f'  пометка «Чернетка… юрист» в разделе согласий: {"перевірить юрист" in cs["txt"]}')
        full = pg.evaluate("document.body.innerText")
        bad = sorted(set(m.group(0) for m in BAD_RE.finditer(full)))
        P(f'  юридические обещания в видимом тексте (закон/гарантуємо/«у будь-який момент»/«будь-коли»…): найдено {len(bad)} {bad}')
        # --- диалог ---
        pg.click('[data-revoke=part]'); pg.wait_for_timeout(900); snap('3-revoke-dialog')
        b1 = pg.evaluate("(()=>{const a=document.querySelector('#dlgKeep'), b=document.querySelector('#dlgGo'); const ra=a.getBoundingClientRect(), rb=b.getBoundingClientRect(); const ca=getComputedStyle(a), cb=getComputedStyle(b); const d=document.querySelector('#dlg').getBoundingClientRect(); return {wa:ra.width,ha:ra.height,wb:rb.width,hb:rb.height,same:['fontSize','backgroundColor','borderTopColor','color','fontWeight'].every(k=>ca[k]===cb[k]),ta:a.textContent,tb:b.textContent,H:innerHeight,bot:d.bottom,txt:document.querySelector('#dlg').innerText.replace(/\\s+/g,' ')}})()")
        P(f'  диалог отзыва: «{b1["ta"]}» {b1["wa"]:.0f}x{b1["ha"]:.0f} / «{b1["tb"]}» {b1["wb"]:.0f}x{b1["hb"]:.0f}; одинаковые шрифт/фон/рамка/цвет/жирность: {b1["same"]}; отступ снизу {b1["H"] - b1["bot"]:.0f} px')
        P(f'  диалог, текст: {b1["txt"][:330]}')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
        esc_ok = pg.evaluate("document.getElementById('scrim').hidden")
        P(f'  Esc закрывает диалог: {esc_ok}')
        pg.click('[data-revoke=part]'); pg.wait_for_timeout(300); pg.click('#dlgGo'); pg.wait_for_timeout(1000); snap('4-after-revoke')
        st = pg.evaluate("[...document.querySelectorAll('.cons .stl')].map(e=>e.textContent.trim()+'|'+e.className)")
        P(f'  после отзыва метки: {st}')
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500); snap('5-first-after-revoke')
        cls = pg.evaluate('window.__cls')
        P(f'  CLS сценария: {cls:.4f}; ошибки/предупреждения консоли: {len(cons)} {cons[:3]}')
        br.close()
    # CLS при загрузке, 15 прогонов
    for dev, (w, h) in DEV.items():
        vals = []
        for _ in range(15):
            br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=(dev == 'phone')); ctx.add_init_script(INIT)
            pg = ctx.new_page(); pg.goto(URL); pg.wait_for_timeout(1500); vals.append(pg.evaluate('window.__cls')); br.close()
        P(f'== CLS при загрузке {dev}: 15 прогонов, макс {max(vals):.4f}, среднее {sum(vals)/len(vals):.5f}')
    # EN: базовые проверки
    for dev, (w, h) in DEV.items():
        br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=(dev == 'phone')); pg = ctx.new_page(); cons = []
        pg.on('console', lambda m: cons.append(m.text) if m.type in ('error', 'warning') else None); pg.on('pageerror', lambda e: cons.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(800); pg.click('[data-lang=en]'); pg.wait_for_timeout(800)
        sw = pg.evaluate("[document.documentElement.scrollWidth, innerWidth]"); mf = pg.evaluate(FONT_JS)
        pg.screenshot(path=os.path.join(SH, f'r6-{dev}-en-1-first.png'))
        pg.evaluate("document.getElementById('consents').scrollIntoView()"); pg.wait_for_timeout(500); pg.screenshot(path=os.path.join(SH, f'r6-{dev}-en-2-consents.png'))
        P(f'== EN {dev}: ширина {sw[0]} = окно {sw[1]}: {sw[0] == sw[1]}; мин. шрифт {mf[0][0]} px; консоль {len(cons)} {cons[:2]}')
        br.close()
txt = '\n'.join(out) + '\n'
open(os.path.join(ROOT, 'замеры-круг6.txt'), 'w').write(txt)
open(os.path.join(SH, 'r6-metrics.txt'), 'w').write(txt)
