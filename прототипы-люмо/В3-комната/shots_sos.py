"""Кадры и замеры SOS В3. Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_sos.py"""
import os, json, re
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(HERE, 'index.html') + '?still=1'
SH = os.path.join(HERE, 'shots'); os.makedirs(SH, exist_ok=True)
DEV = {'desktop': (1440, 900), 'phone': (390, 844)}
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)
def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def L(r): return 0.2126 * lin(r[0]) + 0.7152 * lin(r[1]) + 0.0722 * lin(r[2])
def cr(a, b):
    la, lb = sorted([L(a), L(b)], reverse=True); return (la + 0.05) / (lb + 0.05)
def rgb(s): return [float(x) for x in re.findall(r'[\d.]+', s)[:3]]
INIT = "window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});"
DLG = """() => { const d = document.querySelector('#sosDlg'); const R = e => { const b = e.getBoundingClientRect(); return [Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height)]; };
  const vis = [...d.querySelectorAll('h2,p,button')].filter(e => e.offsetParent !== null && !e.classList.contains('sr'));
  const items = vis.map(e => { const c = getComputedStyle(e); return {t: e.textContent.trim().slice(0, 30), tag: e.tagName, fs: parseFloat(c.fontSize), color: c.color, bg: c.backgroundColor, border: c.borderTopColor, rect: R(e), id: e.id}; });
  const bd = getComputedStyle(d, '::backdrop');
  return {open: d.open, step: d.dataset.step, dlg: R(d), vw: innerWidth, vh: innerHeight, sw: document.documentElement.scrollWidth,
    emo: document.querySelector('#room').dataset.emo, lamp: document.querySelector('#lampState').textContent + ' / ' + document.querySelector('#lampSub').textContent,
    lumo: R(document.querySelector('.lumo-btn')), focus: document.activeElement.id || document.activeElement.textContent.trim(),
    backdrop: [bd.backgroundColor, bd.backdropFilter || bd.webkitBackdropFilter], items, text: d.innerText.replace(/\\n+/g, ' | ')}; }"""
ORANGE = """() => [...document.querySelectorAll('body *')].filter(e => e.offsetParent !== null || e.closest('dialog[open]')).filter(e => { const c = getComputedStyle(e).backgroundColor; const m = c.match(/[\\d.]+/g); return m && +m[0] > 240 && +m[1] > 100 && +m[1] < 140 && +m[2] > 55 && +m[2] < 90 && (m[3] === undefined || +m[3] > .5); }).map(e => (e.id || e.className || e.tagName) + ':' + e.textContent.trim().slice(0, 20))"""
def run(pw, dev, lang):
    w, h = DEV[dev]
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=(dev == 'phone'))
    ctx.add_init_script(INIT); pg = ctx.new_page(); con = []; reqs = []
    pg.on('console', lambda m: con.append(m.text) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: con.append(str(e)))
    pg.on('request', lambda r: reqs.append(r.url) if not r.url.startswith(('file:', 'data:')) else None)
    pg.goto(URL); pg.wait_for_timeout(600)
    if lang == 'en': pg.click('[data-lang=en]'); pg.wait_for_timeout(200)
    P(f'== {dev} {w}x{h} {lang} ==')
    # 0. оранжевая заливка в комнате (без SOS)
    P(' оранжевая заливка вне SOS:', pg.evaluate(ORANGE))
    base = {}
    for emo in ['listen', 'think', 'joy', 'rest']:
        pg.evaluate(f"window.__room.setEmo('{emo}')"); pg.wait_for_timeout(500)
        base[emo] = pg.evaluate("() => { const b = document.querySelector('.lumo-btn').getBoundingClientRect(); return [Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height)]; }")
        pg.click('#sos'); pg.wait_for_timeout(700)
        d = pg.evaluate(DLG)
        sh = max(abs(a - b) for a, b in zip(base[emo], d['lumo']))
        P(f'  из эмоции {emo}: room.emo={d["emo"]}; Люмо: {d["lamp"]}; сдвиг Люмо при входе в SOS {sh:.2f} px; фокус {d["focus"]}')
        if emo == 'joy':   # самая «опасная»
            pg.screenshot(path=f'{SH}/sos-{dev}-{lang}-1-choose-from-joy.png')
        if emo == 'listen':
            pg.screenshot(path=f'{SH}/sos-{dev}-{lang}-1-choose.png'); dd = d
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    # подробный замер экрана А
    P(' экран А:', json.dumps({k: dd[k] for k in ('step', 'dlg', 'vw', 'vh', 'sw', 'backdrop', 'text')}, ensure_ascii=False))
    mf = min(i['fs'] for i in dd['items']); P(f'  мин. шрифт в диалоге: {mf}')
    P(f'  страница: scrollWidth {dd["sw"]} против окна {dd["vw"]}')
    dlg_bg = [0x2A, 0x1A, 0x2E]
    worst = 99
    for i in dd['items']:
        bg = rgb(i['bg']) if not i['bg'].endswith(', 0)') and i['bg'] != 'rgba(0, 0, 0, 0)' else dlg_bg
        c = cr(rgb(i['color']), bg); worst = min(worst, c)
    P(f'  худший контраст текста в диалоге (А): {worst:.2f}:1')
    btn = {i['id'] or i['t']: i for i in dd['items'] if i['tag'] == 'BUTTON'}
    main = btn['sosOwner']; leave = btn['sosLeave']
    P(f'  главная кнопка {main["rect"]} bg {main["bg"]} текст {main["color"]}; «Вийти» {leave["rect"]} bg {leave["bg"]} border {leave["border"]}')
    P(f'  зазор главная→«Вийти»: {leave["rect"][1] - (main["rect"][1] + main["rect"][3])} px; цвет SOS отличается от оранжевого: aqua {main["bg"]} vs акцент rgb(255, 122, 69)')
    if dev == 'phone':
        P(f'  панель снизу: низ {dd["dlg"][1] + dd["dlg"][3]} из {dd["vh"]}, ширина {dd["dlg"][2]} из {dd["vw"]}')
    # выбор причины + звонок
    pg.click('#sos'); pg.wait_for_timeout(500)
    pg.click('[data-r=tech]'); pg.wait_for_timeout(100)
    pg.screenshot(path=f'{SH}/sos-{dev}-{lang}-1b-choose-reason.png')
    # Enter на фокусе = главная кнопка
    pg.keyboard.press('Escape'); pg.click('#sos'); pg.wait_for_timeout(400)
    pg.click('#sosOwner'); pg.wait_for_timeout(700)
    d2 = pg.evaluate(DLG)
    pg.screenshot(path=f'{SH}/sos-{dev}-{lang}-2-called.png')
    P(' экран Б:', json.dumps({k: d2[k] for k in ('step', 'emo', 'lamp', 'text', 'focus', 'dlg', 'sw')}, ensure_ascii=False))
    texts = d2['text'].lower()
    hasdemo = 'demo' in texts or 'демо' in texts
    callvis = pg.evaluate("() => document.querySelector('#sosA').offsetParent !== null")
    P(f'  слово «демо/demo» в диалоге Б: {hasdemo}; экран А (с кнопкой вызова) виден на Б: {callvis}')
    P('  видимые кнопки на Б:', [i['t'] for i in d2['items'] if i['tag'] == 'BUTTON'])
    P(f'  мин. шрифт Б: {min(i["fs"] for i in d2["items"])}')
    worst = 99
    for i in d2['items']:
        bg = rgb(i['bg']) if i['bg'] != 'rgba(0, 0, 0, 0)' else dlg_bg
        worst = min(worst, cr(rgb(i['color']), bg))
    P(f'  худший контраст текста Б: {worst:.2f}:1')
    # SOS перебивает таймер joy: запустить joy и открыть
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    P(' после закрытия: emo', pg.evaluate("() => document.querySelector('#room').dataset.emo"))
    # Люмо во время SOS одинаков по эмоции на ноутбуке/телефоне (сравнится в сводке)
    P(f' CLS {pg.evaluate("() => window.__cls"):.4f}; ошибок консоли {len(con)} {con[:3]}; внешних запросов {len(reqs)}')
    # оранжевая заливка при открытом SOS
    pg.click('#sos'); pg.wait_for_timeout(400)
    P(' оранжевая заливка при открытом SOS (вся страница):', pg.evaluate(ORANGE))
    br.close()
with sync_playwright() as pw:
    for dev in DEV:
        for lang in ('uk', 'en'): run(pw, dev, lang)
open(os.path.join(SH, 'sos-metrics.txt'), 'w').write('\n'.join(out) + '\n')
