"""Знімки і замірі В4-кабінет. Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_run.py"""
import json, os, io, sys
from playwright.sync_api import sync_playwright
try:
    from PIL import Image
    import numpy as np
    HAVE_IMG = True
except Exception as ex:
    HAVE_IMG = False; print('no PIL/numpy', ex)

HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(HERE, 'index.html')
SHOTS = os.path.join(HERE, 'shots'); os.makedirs(SHOTS, exist_ok=True)
DEV = {'desktop': (1440, 900), 'phone': (390, 844)}
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)

def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def L(rgb): return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])
def cr(a, b):
    la, lb = L(a), L(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)

INIT = """
window.__cls = 0;
new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({type:'layout-shift', buffered:true});
"""
TEXT_JS = """() => {
  const res = [];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  while (w.nextNode()) {
    const n = w.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || el.closest('script,style,svg')) continue;
    if (el.closest('[hidden]')) continue;
    { const cx = el.getBoundingClientRect(); const px = cx.left + cx.width / 2, py = cx.top + cx.height / 2; if (py >= 0 && py < innerHeight && px >= 0 && px < innerWidth) { const top = document.elementFromPoint(px, py); if (top && !el.contains(top) && !top.contains(el) && top.closest('#demo')) continue; } }
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
    if (b.width < 1 || b.height < 1) continue;
    res.push({t: n.textContent.trim().slice(0, 28), fs: parseFloat(cs.fontSize), color: cs.color,
      x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height, disabled: !!el.closest('button:disabled'), tag: el.tagName.toLowerCase()});
  }
  return res;
}"""

def parse(c):
    import re
    v = [float(x) for x in re.findall(r'[\d.]+', c)[:4]]
    return v

def contrast_pixels(page, label, tag):
    """скрін без тексту; найяскравіший піксель фону під кожним текстовим вузлом"""
    items = page.evaluate(TEXT_JS)
    page.add_style_tag(content='*{color:transparent !important;text-shadow:none !important;-webkit-text-fill-color:transparent !important} .chip svg,.btn-sm svg{opacity:0}')
    page.wait_for_timeout(150)
    png = page.screenshot(full_page=True)
    page.evaluate("() => { const s=[...document.querySelectorAll('style')].pop(); s.remove(); }")
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
    worst = []
    for it in items:
        x0, y0 = int(it['x']), int(it['y']); x1, y1 = int(it['x'] + it['w']) + 1, int(it['y'] + it['h']) + 1
        reg = im[max(0, y0):y1, max(0, x0):x1]
        if reg.size == 0: continue
        lum = 0.2126 * ((reg[..., 0] / 255) ** 2.2) + 0.7152 * ((reg[..., 1] / 255) ** 2.2) + 0.0722 * ((reg[..., 2] / 255) ** 2.2)
        yy, xx = np.unravel_index(np.argmax(lum), lum.shape)
        bg = reg[yy, xx]
        col = parse(it['color'])[:3]
        worst.append((cr(col, bg), it['t'], it['tag'], tuple(int(v) for v in col), tuple(int(v) for v in bg), it['disabled']))
    worst.sort()
    return worst

def min_font(page):
    return page.evaluate("""() => { let m = 999, who = '';
      for (const it of (%s)()) { if (it.fs < m) { m = it.fs; who = it.t; } } return [m, who]; }""" % TEXT_JS)

def metrics_state(page, name, console):
    sw = page.evaluate("() => [document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth, document.documentElement.scrollHeight]")
    mf = min_font(page)
    P(f'  [{name}] scrollWidth {sw[0]} / body {sw[1]} против окна {sw[2]}; высота страницы {sw[3]}; мин. шрифт {mf[0]} px ({mf[1]!r})')
    return sw, mf

def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, name + '.png'), full_page=True)

def emo_shift(page):
    """сдвиг блока персонажа при смене эмоции: bbox .lumo-btn и .lamp-say, .lamp, и позиции блоков ниже"""
    page.evaluate("() => { document.querySelector('#demo').hidden = true }"); page.evaluate('window.scrollTo(0,0)')
    res = {}
    for e in ['rest', 'wait', 'think', 'joy']:
        page.click('#lumoBtn'); page.click(f'#demo [data-emo={e}]')
        page.wait_for_timeout(50)
        res[e] = page.evaluate("""() => { const q = s => { const r = document.querySelector(s).getBoundingClientRect(); return [r.x, r.y + scrollY, r.width, r.height]; };
          return {btn: q('.lumo-btn'), say: q('.lamp-say'), lamp: q('.lamp'), jump: q('.jump'), next: q('#next')}; }""")
    keys = ['btn', 'say', 'lamp', 'jump', 'next']
    d = {}
    for k in keys:
        base = res['rest'][k]
        d[k] = max(max(abs(res[e][k][i] - base[i]) for i in range(4)) for e in res)
    return d

def run_dev(pw, dev, lang):
    w, h = DEV[dev]
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=(dev == 'phone'), reduced_motion='no-preference')
    ctx.add_init_script(INIT)
    page = ctx.new_page(); console = []; reqs = []
    page.on('console', lambda m: console.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: console.append(('pageerror', str(e))))
    page.on('requestfailed', lambda r: console.append(('reqfail', r.url)))
    page.on('request', lambda r: reqs.append(r.url) if not r.url.startswith(('file:', 'data:')) else None)
    page.goto(URL); page.wait_for_timeout(700)
    P(f'== {dev} {w}x{h} {lang} ==')
    if lang == 'en': page.click('[data-lang=en]'); page.wait_for_timeout(300)
    # 1: день далеко, Люмо отдыхает
    page.wait_for_timeout(1100)
    shot(page, f'{dev}-{lang}-1-rest'); metrics_state(page, 'rest', console)
    cw = contrast_pixels(page, 'rest', f'{dev}-{lang}-rest') if HAVE_IMG else []
    allc = {'rest': cw}
    # меню демо
    page.click('#lumoBtn'); page.wait_for_timeout(250)
    page.screenshot(path=os.path.join(SHOTS, f'{dev}-{lang}-2-demo-menu.png'))
    cwm = contrast_pixels(page, 'menu', '') if HAVE_IMG else []
    allc['menu'] = cwm
    # день близко
    page.click('#demo [data-day=near]'); page.wait_for_timeout(1300)
    shot(page, f'{dev}-{lang}-3-near-enter-open'); metrics_state(page, 'near', console)
    en_state = page.evaluate("() => [document.querySelector('#enter').getAttribute('aria-disabled'), document.querySelector('#enter').textContent]")
    P('  кнопка входа в near:', en_state)
    allc['near'] = contrast_pixels(page, 'near', '') if HAVE_IMG else []
    # день далеко снова: кнопка закрыта
    page.click('#lumoBtn'); page.click('#demo [data-day=far]'); page.wait_for_timeout(1200)
    en_far = page.evaluate("() => [document.querySelector('#enter').getAttribute('aria-disabled'), document.querySelector('#enter').textContent]")
    P('  кнопка входа в far:', en_far)
    # бронь
    page.click('[data-book=s3]'); page.wait_for_timeout(900)
    shot(page, f'{dev}-{lang}-4-booked-joy')
    emo_b = page.evaluate("() => document.querySelector('#page').dataset.emo")
    P('  эмоция после записи:', emo_b)
    allc['joy'] = contrast_pixels(page, 'joy', '') if HAVE_IMG else []
    page.wait_for_timeout(3600)
    # отмена: спросить
    page.click('[data-cancel=s3]'); page.wait_for_timeout(700)
    shot(page, f'{dev}-{lang}-5-cancel-think')
    P('  эмоция при вопросе об отмене:', page.evaluate("() => document.querySelector('#page').dataset.emo"))
    allc['think'] = contrast_pixels(page, 'think', '') if HAVE_IMG else []
    page.click('[data-yes=s3]'); page.wait_for_timeout(700)
    shot(page, f'{dev}-{lang}-6-cancelled')
    P('  после отмены: броней', page.evaluate("() => document.querySelectorAll('.bk').length"), ', эмоция', page.evaluate("() => document.querySelector('#page').dataset.emo"))
    # часовой пояс Киев
    page.click('[data-tz="Europe/Kyiv"]'); page.wait_for_timeout(400)
    first = page.evaluate("() => document.querySelector('.slot .t-time').textContent")
    page.click('[data-tz="Europe/Warsaw"]'); page.wait_for_timeout(200)
    first_w = page.evaluate("() => document.querySelector('.slot .t-time').textContent")
    P(f'  первый слот: Варшава {first_w} / Киев {first}')
    page.click('[data-tz="Europe/Kyiv"]'); page.wait_for_timeout(300)
    shot(page, f'{dev}-{lang}-7-kyiv')
    page.click('[data-tz="Europe/Warsaw"]')
    # сдвиг при смене эмоции
    sh = emo_shift(page)
    P('  сдвиг блока персонажа при смене эмоции (макс. px по x/y/w/h):', json.dumps(sh))
    cls = page.evaluate("() => window.__cls")
    P(f'  CLS за всю сессию (загрузка + все взаимодействия): {cls:.4f}')
    # цели касания
    small = page.evaluate("""() => [...document.querySelectorAll('button,a')].filter(e => !e.closest('[hidden]')).map(e => [e, e.getBoundingClientRect()]).filter(([e, r]) => r.width > 0 && r.height < 44).map(([e, r]) => e.textContent.trim().slice(0, 20) + ':' + Math.round(r.height))""")
    P('  цели касания <44px:', small)
    # контраст
    for k, v in allc.items():
        if not v: continue
        enabled = [x for x in v if not x[5]]
        w0 = enabled[0]
        P(f'  контраст [{k}] худший текст: {w0[0]:.2f}:1 «{w0[1]}» <{w0[2]}> цвет {w0[3]} фон {w0[4]}; элементов {len(v)}; <4.5: {[ (round(x[0],2), x[1]) for x in v if x[0] < 4.5 ]}')
    # текст кнопок по computed (кнопка акцент)
    bc = page.evaluate("""() => [...document.querySelectorAll('.btn-sm:not(:disabled), .btn-main')].slice(0,2).map(b => [getComputedStyle(b).color, getComputedStyle(b).backgroundColor])""")
    for c, b in bc:
        P(f'  кнопка computed: текст {c} на {b}: {cr(parse(c)[:3], parse(b)[:3]):.2f}:1')
    P('  внешних запросов:', len(reqs), reqs[:3])
    P('  консоль/сеть ошибки:', len(console), console[:5])
    br.close()

with sync_playwright() as pw:
    for dev in DEV:
        for lang in ('uk', 'en'):
            run_dev(pw, dev, lang)
open(os.path.join(SHOTS, 'metrics.txt'), 'w').write('\n'.join(out) + '\n')
