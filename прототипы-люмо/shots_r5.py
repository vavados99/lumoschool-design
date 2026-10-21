"""Круг 5: кадры r5-* и замеры shots/r5-metrics.txt для В3/В4/В5.
Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_r5.py"""
import os, io, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
PROTOS = {'В3-комната': 'v3', 'В4-кабинет': 'v4', 'В5-родитель': 'v5'}
DEV = {'desktop': (1440, 900), 'phone': (390, 844)}
INIT = "window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});"
FONT_JS = """() => { const out=[]; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
 while(w.nextNode()){const n=w.currentNode; if(!n.textContent.trim())continue; const el=n.parentElement; if(!el||el.closest('script,style,svg,[hidden],.sr'))continue;
  const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden')continue;
  const r=document.createRange(); r.selectNodeContents(n); const b=r.getBoundingClientRect(); if(b.width<1||b.height<1)continue;
  if(el.closest('dialog:not([open])'))continue; if(el.closest('[hidden]'))continue;
  if(parseFloat(cs.opacity)===0)continue;
  out.push([parseFloat(cs.fontSize), n.textContent.trim().slice(0,28)]);}
 out.sort((a,b)=>a[0]-b[0]); return out.slice(0,4);}"""
LOGO_JS = """() => { const i=document.querySelector('.brand .logo'); if(!i) return null; const r=i.getBoundingClientRect();
 const h=document.querySelector('header'); const hr=h.getBoundingClientRect();
 const ctl=[...h.querySelectorAll('button,.tz,.nav a')].filter(e=>e.getBoundingClientRect().height>0&&e.getBoundingClientRect().top<hr.bottom+4);
 let cc=null; if(ctl.length){const t=Math.min(...ctl.map(e=>e.getBoundingClientRect().top)), b=Math.max(...ctl.map(e=>e.getBoundingClientRect().bottom)); cc=(t+b)/2;}
 return {x:r.left,y:r.top,w:r.width,h:r.height,cy:r.top+r.height/2,ctlCy:cc,hdrTop:hr.top,hdrBottom:hr.bottom,loaded:i.complete&&i.naturalWidth>0}; }"""
out = []
def P(s): print(s); out.append(s)

with sync_playwright() as pw:
    for folder, tag in PROTOS.items():
        url = 'file://' + os.path.join(ROOT, folder, 'index.html')
        shots = os.path.join(ROOT, folder, 'shots'); os.makedirs(shots, exist_ok=True)
        for dev, (w, h) in DEV.items():
            br = pw.chromium.launch()
            ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=(dev == 'phone'))
            ctx.add_init_script(INIT)
            pg = ctx.new_page(); cons = []
            pg.on('console', lambda m: cons.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
            pg.on('pageerror', lambda e: cons.append(('pageerror', str(e))))
            pg.on('requestfailed', lambda r: cons.append(('reqfail', r.url)))
            pg.goto(url); pg.wait_for_timeout(1200)
            def snap(name, full=False): pg.screenshot(path=os.path.join(shots, f'r5-{dev}-{name}.png'), full_page=full)
            P(f'== {folder} {dev} {w}x{h} ==')
            snap('1-first'); snap('1-full', True)
            sw = pg.evaluate("[document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth, document.documentElement.scrollHeight]")
            P(f'  ширина страницы: html {sw[0]} / body {sw[1]} против окна {sw[2]} -> {"OK" if sw[0] == sw[2] and sw[1] <= sw[2] else "ПЛОХО"}; высота {sw[3]}')
            mf = pg.evaluate(FONT_JS)
            P(f'  мин. шрифт (видимый текст): {mf[0][0]} px ({mf[0][1]!r}); следующие: {[(a, b) for a, b in mf[1:3]]} -> {"OK" if mf[0][0] >= 16 else "ПЛОХО <16"}')
            lg = pg.evaluate(LOGO_JS)
            if lg:
                d = lg['cy'] - lg['ctlCy'] if lg['ctlCy'] else None
                P(f'  логотип: x={lg["x"]:.0f} y={lg["y"]:.0f} {lg["w"]:.0f}x{lg["h"]:.0f}; загружен={lg["loaded"]}; центр лого y={lg["cy"]:.1f}, центр строки контролов шапки y={lg["ctlCy"]}; разница {d if d is None else round(d, 1)} px; в окне: {0 <= lg["x"] and lg["x"] + lg["w"] <= w}')
            else:
                P('  логотип: НЕ НАЙДЕН')
            if tag == 'v5':
                nxt = pg.evaluate("(()=>{const r=document.querySelector('#nextCard').getBoundingClientRect(); const t=document.querySelector('.teacher').getBoundingClientRect(); return {top:r.top,bottom:r.bottom,tBottom:t.bottom,h:innerHeight}})()")
                P(f'  В5 блок «ближайший урок + учитель» на первом экране: карточка y {nxt["top"]:.0f}–{nxt["bottom"]:.0f}, учитель до y={nxt["tBottom"]:.0f} при высоте окна {nxt["h"]:.0f} -> {"ВИДНО ЦЕЛИКОМ" if nxt["bottom"] <= nxt["h"] else ("видно учителя, низ карточки ниже" if nxt["tBottom"] <= nxt["h"] else "УЧИТЕЛЬ НЕ ВИДЕН")}')
                pg.evaluate("window.scrollTo({top: document.getElementById('consents').getBoundingClientRect().top + scrollY - (innerWidth<=820?150:90), behavior:'instant'})"); pg.wait_for_timeout(700)
                snap('2-consents')
                pg.click('[data-revoke=part]'); pg.wait_for_timeout(900); snap('3-revoke-dialog')
                b1 = pg.evaluate("(()=>{const a=document.querySelector('#dlgKeep').getBoundingClientRect(), b=document.querySelector('#dlgGo').getBoundingClientRect(); const ca=getComputedStyle(document.querySelector('#dlgKeep')), cb=getComputedStyle(document.querySelector('#dlgGo')); return {wa:a.width,ha:a.height,wb:b.width,hb:b.height,fsA:ca.fontSize,fsB:cb.fontSize,bgA:ca.backgroundColor,bgB:cb.backgroundColor,brA:ca.borderColor,brB:cb.borderColor,colA:ca.color,colB:cb.color,y:b.bottom,H:innerHeight, top:document.querySelector('#dlg').getBoundingClientRect().top, bot:document.querySelector('#dlg').getBoundingClientRect().bottom}})()")
                same = all(b1[k + 'A'] == b1[k + 'B'] for k in ('fs', 'bg', 'br', 'col'))
                P(f'  диалог отзыва: кнопки {b1["wa"]:.0f}x{b1["ha"]:.0f} / {b1["wb"]:.0f}x{b1["hb"]:.0f}; одинаковые шрифт/фон/рамка/цвет: {same}; окно y {b1["top"]:.0f}–{b1["bot"]:.0f} из {b1["H"]}; отступ снизу {b1["H"] - b1["bot"]:.0f} px')
                mfd = pg.evaluate(FONT_JS.replace("document.body", "document.querySelector('#dlg')")); P(f'  диалог мин. шрифт: {mfd[0][0]} px')
                pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
                esc_ok = pg.evaluate("document.getElementById('scrim').hidden")
                P(f'  Esc закрывает диалог: {esc_ok}')
                pg.click('[data-revoke=part]'); pg.wait_for_timeout(300); pg.click('#dlgGo'); pg.wait_for_timeout(1000); snap('4-after-revoke')
                pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500); snap('5-first-after-revoke')
            cls = pg.evaluate('window.__cls')
            P(f'  CLS: {cls:.4f}; ошибки/предупреждения консоли: {len(cons)} {cons[:3]}')
            br.close()

# ---------- круг 5: дополнительные сценарии и замеры ----------
PROX = lambda: None
def box(pg, sel):
    return pg.evaluate("s=>{const r=document.querySelector(s).getBoundingClientRect();return [r.left,r.top,r.width,r.height]}", sel)
def lum_of(pg, x, y):  # яркость пикселя кадра
    from PIL import Image
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB'); p = im.getpixel((int(x), int(y)))
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]
def cls_runs(pw, folder, dev, n=30):
    w, h = DEV[dev]; vals = []
    for _ in range(n):
        br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=(dev == 'phone')); ctx.add_init_script(INIT)
        pg = ctx.new_page(); pg.goto('file://' + os.path.join(ROOT, folder, 'index.html')); pg.wait_for_timeout(1500)
        vals.append(pg.evaluate('window.__cls')); br.close()
    return vals
with sync_playwright() as pw:
    P('== КРУГ 5: допзамеры ==')
    for folder, tag in (('В4-кабинет', 'v4'),):
        shots = os.path.join(ROOT, folder, 'shots')
        for dev, (w, h) in DEV.items():
            vals = cls_runs(pw, folder, dev, 30)
            P(f'  В4 {dev}: CLS за 30 загрузок: макс {max(vals):.4f}, среднее {sum(vals)/len(vals):.5f}, загрузок с CLS>0.001: {sum(v > 0.001 for v in vals)}; (до правок телефон: 0–0.0983, 4 из 8 загрузок ≈0.098)')
            br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=(dev == 'phone')); ctx.add_init_script(INIT)
            pg = ctx.new_page(); cons = []
            pg.on('console', lambda m: cons.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
            pg.on('pageerror', lambda e: cons.append(('pageerror', str(e))))
            pg.goto('file://' + os.path.join(ROOT, folder, 'index.html')); pg.wait_for_timeout(1200)
            def snap(name, full=False): pg.screenshot(path=os.path.join(shots, f'r5-{dev}-{name}.png'), full_page=full)
            # смещение Люмо при смене эмоции (бокс кнопки и ядро)
            res = []
            base = box(pg, '#lumoBtn'); mx = 0
            for e in ('rest', 'wait', 'think', 'joy', 'rest'):
                pg.evaluate("e=>{document.querySelector('#page').dataset.emo=e}", e); pg.wait_for_timeout(700)
                b = box(pg, '#lumoBtn'); d = max(abs(b[0] - base[0]), abs(b[1] - base[1])); mx = max(mx, d); res.append((e, round(d, 2)))
            P(f'  В4 {dev}: смещение рамки Люмо при смене эмоции (px): {res}; макс {mx:.2f}')
            # свет на карточку урока: яркость ближней и дальней сторон
            pg.evaluate("document.querySelector('#page').dataset.emo='rest'"); pg.wait_for_timeout(800)
            nb = box(pg, '#next'); lb = box(pg, '#lumoBtn')
            if dev == 'desktop':
                pg.mouse.move(lb[0] + lb[2] / 2, lb[1] + lb[3] / 2); pg.wait_for_timeout(900)
                snap('2-near-hover')
                nb2 = box(pg, '#next'); ry = nb2[1] + 60
                PROX = lambda: pg.evaluate("getComputedStyle(document.querySelector('#page')).getPropertyValue('--prox')")
                def edge(): return [round(lum_of(pg, nb2[0] + nb2[2] - 1, ry), 1), round(lum_of(pg, nb2[0] + 1, ry), 1)]
                P(f'  В4 desktop: яркость границы карточки (правый ближний к Люмо / левый дальний), курсор у Люмо: {edge()}, prox={PROX()}')
                pg.mouse.move(5, 880); pg.wait_for_timeout(900)
                P(f'  В4 desktop: то же, курсор вдали: {edge()}, prox={PROX()}')
            for emo in ('rest', 'wait'):
                pg.evaluate("e=>{document.querySelector('#page').dataset.emo=e}", emo); pg.wait_for_timeout(900)
                nb = box(pg, '#next'); y = nb[1] + 40
                near = lum_of(pg, nb[0] + 10, y) if dev == 'desktop' else lum_of(pg, nb[0] + nb[2] - 10, y)
                far = lum_of(pg, nb[0] + nb[2] - 10, y) if dev == 'desktop' else lum_of(pg, nb[0] + 10, y)
                P(f'  В4 {dev} {emo}: яркость края карточки на высоте шапки: левый/правый (десктоп: левый дальний, правый ближний к Люмо) {near:.1f} / {far:.1f}')
            # радость в точке клика
            pg.evaluate("document.querySelector('#page').dataset.emo='rest'")
            pg.evaluate("document.querySelector('#book').scrollIntoView({block:'start'})"); pg.wait_for_timeout(600)
            btn = pg.locator('[data-book]:not([disabled])').first
            bb = btn.bounding_box(); cx, cy = bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2
            before_seats = pg.evaluate("document.querySelector('.slot:has([data-book]:not([disabled])) .seats').textContent")
            pg.mouse.move(cx, cy); pg.mouse.down(); pg.mouse.up(); pg.wait_for_timeout(250)
            snap('3-joy-click')
            st = pg.evaluate("({emo:document.querySelector('#page').dataset.emo, burst:document.querySelectorAll('.burst').length, face:document.querySelectorAll('.face-mini').length, label:document.querySelector('.slot.just button')?.textContent.trim()})")
            P(f'  В4 {dev} клик «Записатися» в точке ({cx:.0f},{cy:.0f}): через 250 мс эмоция={st["emo"]}, вспышек={st["burst"]}, мини-лицо на кнопке={st["face"]}, надпись «{st["label"]}»; места до: {before_seats}')
            pg.wait_for_timeout(1000); st2 = pg.evaluate("document.querySelectorAll('.burst').length"); P(f'  В4 {dev}: вспышка убрана из DOM через 1.25 с: {st2 == 0}')
            # липкая плашка
            pg.evaluate("window.scrollTo(0, 1400)"); pg.wait_for_timeout(600); snap('4-sticky-enter')
            sb = pg.evaluate("(()=>{const s=document.querySelector('#sticky'); if(s.hidden) return null; const r=s.getBoundingClientRect(), a=document.querySelector('#enter2').getBoundingClientRect(); const cs=getComputedStyle(document.querySelector('#enter2')); return {t:r.top,b:r.bottom,w:r.width,h:innerHeight,bh:a.height,bw:a.width,fs:cs.fontSize,bg:cs.backgroundColor,col:cs.color,txt:document.querySelector('#enter2').textContent}})()")
            P(f'  В4 {dev} липкая плашка: {"НЕ ПОКАЗАНА" if not sb else "видна, y %.0f–%.0f из %d, кнопка %.0fx%.0f, шрифт %s, текст «%s», цвет %s на %s" % (sb["t"], sb["b"], sb["h"], sb["bw"], sb["bh"], sb["fs"], sb["txt"], sb["col"], sb["bg"])}')
            pg.evaluate("window.scrollTo(0, 0)"); pg.wait_for_timeout(500)
            hid = pg.evaluate("document.querySelector('#sticky').hidden"); P(f'  В4 {dev}: плашка скрыта, пока карточка на экране: {hid}')
            # состояние «близко»: Люмо + плашка
            pg.evaluate("document.querySelector('[data-day=near]').click()") if False else None
            P(f'  В4 {dev}: консоль {len(cons)} {cons[:3]}')
            br.close()
    # В3: плитки участников
    for dev, (w, h) in DEV.items():
        br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=(dev == 'phone')); pg = ctx.new_page()
        pg.goto('file://' + os.path.join(ROOT, 'В3-комната', 'index.html')); pg.wait_for_timeout(1200)
        res = []
        for sel in ('.arch-t', '.arch-s1', '.arch-s2'):
            r = box(pg, sel); res.append((sel, round(lum_of(pg, r[0] + r[2] / 2, r[1] + 20), 1)))
        P(f'  В3 {dev}: яркость верха плиток (≈20 px от верхушки арки) {res}')
        br.close()
    # В5 телефон: все вкладки в окне
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 390, 'height': 844}, has_touch=True); pg = ctx.new_page()
    pg.goto('file://' + os.path.join(ROOT, 'В5-родитель', 'index.html')); pg.wait_for_timeout(1200)
    nv = pg.evaluate("[...document.querySelectorAll('#nav a')].map(a=>{const r=a.getBoundingClientRect();return [a.textContent.trim(), Math.round(r.left), Math.round(r.right), Math.round(a.scrollWidth - a.clientWidth), Math.round(r.height)]})")
    P(f'  В5 phone вкладки (текст, left, right, переполнение текста px, высота) при окне 390: {nv}; все внутри окна и без обрезки: {all(0 <= a[1] and a[2] <= 390 and a[3] <= 0 for a in nv)}')
    rail = pg.evaluate("document.querySelector('#nav').getBoundingClientRect().height"); P(f'  В5 phone: высота липкой полосы вкладок {rail:.0f} px из 844 (было: весь рейл 209 px)')
    pg.screenshot(path=os.path.join(ROOT, 'В5-родитель', 'shots', 'r5-phone-6-nav.png'))
    br.close()
txt = '\n'.join(out) + '\n'
open(os.path.join(ROOT, 'замеры-круг5.txt'), 'w').write(txt)
open(os.path.join(ROOT, 'В5-родитель', 'shots', 'r5-metrics.txt'), 'w').write(txt)
for f in PROTOS:
    open(os.path.join(ROOT, f, 'shots', 'r5-metrics.txt'), 'w').write('\n'.join(out) + '\n')
