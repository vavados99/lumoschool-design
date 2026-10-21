"""Круг 13: точечные замеры В6. Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_r13_extra.py  -> shots/metrics-r13-extra.txt"""
import os, io
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); URL = 'file://' + os.path.join(HERE, 'index.html')
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for dev, (w, h) in (('desktop', (1440, 900)), ('phone', (390, 844))):
        for lang in ('uk', 'en'):
            ctx = br.new_context(viewport={'width': w, 'height': h}); page = ctx.new_page()
            page.goto(URL + '?demo=live&clean=1'); page.wait_for_timeout(900)
            if lang == 'en': page.evaluate("document.querySelector('[data-lang=en]').click()"); page.wait_for_timeout(400)
            page.evaluate("document.querySelectorAll('.lumo-wrap, .lumo').forEach(e => e.style.animation='none')")
            P(f'== {dev} {lang} ==')
            m = page.evaluate("""() => { const lw = document.querySelector('.lumo-wrap').getBoundingClientRect(); const cs = getComputedStyle(document.querySelector('.lumo')); const lc = getComputedStyle(document.querySelector('.lesson-card'));
              const rows = [...document.querySelectorAll('.dr:not(.mk)')].map(r => { const dt = r.querySelector('.dt'); const t = document.createTreeWalker(dt, NodeFilter.SHOW_TEXT); let n, left = null; while (n = t.nextNode()) { if (n.textContent.trim()) { const rg = document.createRange(); rg.selectNodeContents(n); left = Math.round(rg.getBoundingClientRect().left * 10) / 10; break; } } return [r.className.replace('dr ', ''), left, getComputedStyle(r).backgroundColor, getComputedStyle(r).boxShadow !== 'none']; });
              const dot = document.querySelector('.dr.live-row .nowdot'); const dr = dot && dot.getBoundingClientRect(), cur = document.querySelector('.dr.live-row').getBoundingClientRect();
              return {lumo: [Math.round(lw.width), Math.round(lw.height)], filter: cs.filter, bgimg: lc.backgroundImage.includes('radial'), rows, dot: dr && [Math.round(dr.left - cur.left), getComputedStyle(dot).backgroundColor]}; }""")
            P(f"  [П1 маскот] {m['lumo'][0]}x{m['lumo'][1]} px; drop-shadow/ореол: {m['filter']}; радиальный ореол на карточке: {m['bgimg']}")
            lefts = {r[1] for r in m['rows']}
            P(f"  [П2 колонка времени] левый край текста времени по строкам: {[(r[0], r[1]) for r in m['rows']]} -> {'ОДИН X' if len(lefts) == 1 else 'ПРЫГАЕТ'}; точка: смещение от края плашки {m['dot'][0]}px, цвет {m['dot'][1]}")
            P(f"  [П2 фон строк] {[(r[0], r[2], 'контур' if r[3] else '') for r in m['rows']]}")
            e = page.evaluate("(() => { const t = document.querySelector('.lesson-card'); const r = t.getBoundingClientRect(); const l = document.querySelector('.lumo-wrap').getBoundingClientRect(); const b = document.querySelector('#enter').getBoundingClientRect(); return {dx: Math.round(l.left - b.right), cardW: Math.round(r.width), lumoCx: Math.round(l.left + l.width / 2 - r.left), btnR: Math.round(b.right - r.left)}; })()")
            P(f"  [П1 центр] зазор кнопка→маскот {e['dx']}px; кнопка заканчивается x={e['btnR']}, центр маскота x={e['lumoCx']}, ширина карточки {e['cardW']}")
            # эмоция: смещение блока персонажа
            def box(): return page.evaluate("(() => { const l = document.querySelector('.lumo-wrap').getBoundingClientRect(); return [l.left, l.top, l.width, l.height]; })()")
            seq = []
            for emo in ('calm', 'joy', 'calm', 'joy'):
                page.evaluate(f"document.querySelector('#page').dataset.emo = '{emo}'"); page.wait_for_timeout(350); seq.append(box())
            mx = max(max(abs(a - b) for a, b in zip(seq[0], s)) for s in seq)
            P(f"  [смена эмоции calm↔joy] макс. смещение/изменение размера блока персонажа: {mx:.2f}px {'OK' if mx < .5 else 'ПЛОХО'}")
            if dev == 'phone':
                d = page.evaluate("(() => { const dock = document.querySelector('.lesson-card .lc-row').getBoundingClientRect(), st = document.querySelector('.dr.live-row .st').getBoundingClientRect(), r = document.querySelector('.dr.live-row').getBoundingClientRect(); const bef = getComputedStyle(document.querySelector('.lesson-card .lc-row'), '::before').display; return {dockTop: Math.round(dock.top), rowBottom: Math.round(r.bottom), stBottom: Math.round(st.bottom), fade: bef, pad: getComputedStyle(document.querySelector('.today')).paddingBottom}; })()")
                P(f"  [П3 «Іде зараз» над панелью] низ плашки {d['rowBottom']}, низ бейджа {d['stBottom']}, верх панели {d['dockTop']} -> зазор {d['dockTop'] - d['rowBottom']}px; затемнение поверх контента: {d['fade']}; padding-bottom страницы {d['pad']}")
                nb = page.evaluate("(() => { const r = document.querySelector('#nav').getBoundingClientRect(); return [r.top, r.bottom]; })()")
                im = np.array(Image.open(io.BytesIO(page.screenshot())).convert('L')).astype(int)[int(nb[0]):int(nb[1])]
                cols = {x: int(im[:, x].max()) for x in range(340, 390, 4)}
                inside = [(x, v) for x, v in cols.items()]
                P(f"  [П3 затухание вкладок] макс. яркость по столбцам x=340..388: {inside}; mask: {page.evaluate('getComputedStyle(document.querySelector(`#navIn`)).webkitMaskImage')}")
            ctx.close()
    # замена: высота плашки при выборе
    for dev, (w, h) in (('desktop', (1440, 900)), ('phone', (390, 844))):
        ctx = br.new_context(viewport={'width': w, 'height': h}); page = ctx.new_page()
        page.goto(URL + '?demo=open&clean=1'); page.wait_for_timeout(800)
        page.evaluate("document.getElementById('swap').scrollIntoView()"); page.wait_for_timeout(300)
        hs = lambda: page.evaluate("[...document.querySelectorAll('.opt')].map(o => [Math.round(o.getBoundingClientRect().height * 100) / 100, Math.round(o.querySelector('span').getBoundingClientRect().top - o.getBoundingClientRect().top)])")
        h0 = hs(); y0 = page.evaluate("document.querySelector('.opts').getBoundingClientRect().height")
        page.click('.opt:nth-child(2)'); page.wait_for_timeout(250); h1 = hs(); y1 = page.evaluate("document.querySelector('.opts').getBoundingClientRect().height")
        page.click('.opt:nth-child(3)'); page.wait_for_timeout(250); h2 = hs()
        P(f"== {dev} замена: [высота плашки, сдвиг текста] до {h0}; выбран №2 {h1}; выбран №3 {h2}; высота списка {y0} → {y1} -> {'БЕЗ СДВИГА' if h0 == h1 == h2 and y0 == y1 else 'СДВИГ'}")
        ctx.close()
    # «Зберегти» и «не передається»
    for dev, (w, h) in (('desktop', (1440, 900)), ('phone', (390, 844))):
        ctx = br.new_context(viewport={'width': w, 'height': h}); page = ctx.new_page(); page.goto(URL + '?demo=open&clean=1'); page.wait_for_timeout(800)
        page.evaluate("document.getElementById('notes').scrollIntoView()"); page.fill('#noteText', 'Call parent +48 600 100 200'); page.click('#noteForm button[type=submit]', force=True); page.wait_for_timeout(900)
        s = page.evaluate("(() => { const b = document.querySelector('#noteForm button[type=submit]'); const cs = getComputedStyle(b); return [b.getAttribute('aria-disabled'), cs.backgroundColor, cs.color, cs.cursor]; })()")
        P(f"== {dev} «Зберегти» при ошибке: aria-disabled={s[0]}, фон {s[1]}, текст {s[2]}, курсор {s[3]}")
        n = page.evaluate("(() => { const e = [...document.querySelectorAll('.how .nw')].find(x => x.getClientRects().length) || document.querySelector('.how .nw'); if (!e.getClientRects().length) document.querySelector('.how-m summary').click(); const cs = getComputedStyle(e); const r = e.getClientRects(); return [cs.whiteSpace, r.length, e.textContent]; })()")
        P(f"== {dev} «не передається»: white-space={n[0]}, прямоугольников (строк) {n[1]} -> {'одна строка, неразрывно' if n[0] == 'nowrap' and n[1] == 1 else 'ПЛОХО'}; «{n[2]}»")
        ctx.close()
    # внешние запросы и консоль одним прогоном
    ctx = br.new_context(viewport={'width': 1440, 'height': 900}); page = ctx.new_page(); ext = []; con = []
    page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:', 'blob:')) else None); page.on('console', lambda m: con.append(m.text) if m.type == 'error' else None); page.on('pageerror', lambda e: con.append(str(e)))
    page.goto(URL + '?demo=live'); page.wait_for_timeout(1200)
    P(f"== сводка (extra): внешние запросы {len(ext)}, ошибки консоли {len(con)}; scrollWidth {page.evaluate('document.documentElement.scrollWidth')} vs окно 1440")
    br.close()
open(os.path.join(HERE, 'shots', 'metrics-r13-extra.txt'), 'w').write('\n'.join(out) + '\n')
