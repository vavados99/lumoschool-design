"""Круг 4: кадры r4-* и замеры shots/r4-metrics.txt для В3/В4/В5.
Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_r4.py"""
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
            def snap(name, full=False): pg.screenshot(path=os.path.join(shots, f'r4-{dev}-{name}.png'), full_page=full)
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
open(os.path.join(ROOT, 'В5-родитель', 'shots', 'r4-metrics.txt'), 'w').write('\n'.join(out) + '\n')
for f in PROTOS:
    open(os.path.join(ROOT, f, 'shots', 'r4-metrics.txt'), 'w').write('\n'.join(out) + '\n')
