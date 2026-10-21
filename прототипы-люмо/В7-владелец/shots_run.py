"""Кадры и замеры В7-владелец. Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_run.py"""
import os, io, re
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

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
def L_(rgb): return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])
def cr(a, b):
    la, lb = L_(a), L_(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

INIT = """window.__cls = 0;
new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({type:'layout-shift', buffered:true});"""

TEXT_JS = """() => {
  const res = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const n = w.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || el.closest('script,style,svg')) continue;
    if (el.closest('[hidden]')) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    if (el.closest('.vh') || el.closest('.skip')) continue;
    const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
    if (b.width < 1 || b.height < 1) continue;
    res.push({t: n.textContent.trim().slice(0, 30), fs: parseFloat(cs.fontSize), color: cs.color, x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height, tag: el.tagName.toLowerCase()});
  }
  return res; }"""

def parse(c): return [float(x) for x in re.findall(r'[\d.]+', c)[:4]]

def contrast_pixels(page):
    items = page.evaluate(TEXT_JS)
    page.add_style_tag(content='*{color:transparent !important;-webkit-text-fill-color:transparent !important;text-shadow:none !important} svg{opacity:0 !important}')
    page.wait_for_timeout(200)
    png = page.screenshot(full_page=True)
    page.evaluate("() => [...document.querySelectorAll('style')].pop().remove()")
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
    worst = []
    for it in items:
        x0, y0 = int(it['x']), int(it['y']); x1, y1 = int(it['x'] + it['w']) + 1, int(it['y'] + it['h']) + 1
        reg = im[max(0, y0):y1, max(0, x0):x1]
        if reg.size == 0: continue
        lum = 0.2126 * ((reg[..., 0] / 255) ** 2.2) + 0.7152 * ((reg[..., 1] / 255) ** 2.2) + 0.0722 * ((reg[..., 2] / 255) ** 2.2)
        col = parse(it['color'])[:3]
        c_min = 99
        for fn in (np.argmax, np.argmin):
            yy, xx = np.unravel_index(fn(lum), lum.shape)
            c_min = min(c_min, cr(col, reg[yy, xx]))
        worst.append((c_min, it['t'], it['tag'], tuple(int(v) for v in col)))
    worst.sort()
    return worst

def min_font(page):
    items = page.evaluate(TEXT_JS)
    m = min(items, key=lambda i: i['fs'])
    return m['fs'], m['t']

def shot(page, name, full=False):
    page.screenshot(path=os.path.join(SHOTS, name + '.png'), full_page=full)

def goto_sec(page, sec):
    page.evaluate("(id) => { const el = document.getElementById(id); window.scrollTo({top: el.getBoundingClientRect().top + scrollY - 84, behavior: 'instant'}); }", sec)
    page.wait_for_timeout(400)

CLIP_JS = """() => { const bad = []; const vw = innerWidth;
  for (const el of document.querySelectorAll('main *, header *, .sbar *')) {
    if (el.closest('svg') || el.closest('[hidden]') || el.closest('.nav') || el.closest('.vh') || el.closest('.cmp')) continue;
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect(); if (r.width < 1) continue;
    if (r.right > vw + 1 || r.left < -1) bad.push('вне окна: ' + el.tagName + '.' + el.className + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
    if (el.children.length === 0 && el.scrollWidth > el.clientWidth + 1 && cs.overflow !== 'visible') bad.push('обрезан текст: ' + el.tagName + '.' + el.className);
  } return bad.slice(0, 8); }"""
TARGET_JS = """() => [...document.querySelectorAll('button, a.btn, .nav a')].filter(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && cs.display !== 'none' && !e.closest('[hidden]') && (r.height < 44 - .5) }).map(e => e.tagName + '.' + e.className + ' ' + Math.round(e.getBoundingClientRect().height) + 'px ' + e.textContent.trim().slice(0, 16))"""
WARM_JS = """() => { // тёплые точки в первом экране: элементы с заливкой/обводкой акцента + Люмо
  const vh = innerHeight, res = [];
  for (const el of document.querySelectorAll('#page *')) {
    const cs = getComputedStyle(el); const r = el.getBoundingClientRect(); if (r.width < 1 || r.top > vh || r.bottom < 0) continue;
    const isAcc = c => /rgb\\(255, 122, 69\\)/.test(c);
    if (isAcc(cs.backgroundColor) || isAcc(cs.color) || isAcc(cs.borderTopColor) && parseFloat(cs.borderTopWidth) > 0 || (el.tagName === 'circle' && isAcc(cs.fill)) || (el.tagName === 'circle' && el.getAttribute('class') && el.getAttribute('class').includes('overlap'))) res.push(el.tagName + '.' + (el.getAttribute('class') || ''));
  }
  if (document.getElementById('lumo') && document.getElementById('lumo').getBoundingClientRect().top < vh) res.push('LUMO');
  return res; }"""

def run(pw, dev, lang):
    w, h = DEV[dev]
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=(dev == 'phone'))
    ctx.add_init_script(INIT)
    page = ctx.new_page(); console = []; ext = []
    page.on('console', lambda m: console.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: console.append(('pageerror', str(e))))
    page.on('requestfailed', lambda r: console.append(('reqfail', r.url)))
    page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:')) else None)
    page.goto(URL + ('?lang=en' if lang == 'en' else '')); page.wait_for_timeout(900)
    P(f'== {dev} {w}x{h} {lang} ==')
    pre = f'{dev}-{lang}-'
    def sw(tag):
        s = page.evaluate("() => [document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth, document.documentElement.scrollHeight]")
        mf = min_font(page)
        ok = 'OK' if s[0] == s[2] and s[1] <= s[2] else 'ПЛОХО'
        P(f'  [{tag}] scrollWidth {s[0]} / body {s[1]} vs окно {s[2]} {ok}; высота страницы {s[3]}; мин.шрифт {mf[0]}px ({mf[1]!r})')
        cl = page.evaluate(CLIP_JS); P(f'  [{tag}] выход за окно / обрезанный текст: {len(cl)} {cl[:3]}')
    heights = {}
    # 1 первый экран
    shot(page, pre + '1-first'); shot(page, pre + '1-full', full=True)
    sw('first')
    warm = page.evaluate(WARM_JS); P(f'  тёплых точек в первом экране: {len(warm)} {warm}')
    cp = contrast_pixels(page)
    P(f'  контраст текста (пиксели): мин {cp[0][0]:.2f} ({cp[0][1]!r}, {cp[0][2]}, {cp[0][3]}); ниже 4.5: {sum(1 for c in cp if c[0] < 4.5)} из {len(cp)}')
    for c in cp[:4]: P(f'    худшие: {c[0]:.2f} {c[1]!r} {c[2]} {c[3]}')
    tg = page.evaluate(TARGET_JS); P(f'  кнопки ниже 44 px по высоте: {len(tg)} {tg[:3]}')
    # поиск контактов в открытом виде
    txt = page.evaluate("document.body.innerText"); hits = re.findall(r'@[a-z]|\+\d{2}[ \d]*\d{3}|\b\d{3}[ -]\d{3}[ -]\d{3}\b', txt)
    P(f'  открытые контакты в тексте страницы: {hits}')
    # 2 период: числа меняются
    h0 = page.evaluate("document.documentElement.scrollHeight"); fig0 = page.inner_text('.ribbon')
    page.click('[data-per=quarter]'); page.wait_for_timeout(500)
    fig1 = page.inner_text('.ribbon'); h1 = page.evaluate("document.documentElement.scrollHeight")
    P(f'  [период квартал] ленты различаются: {fig0 != fig1}; высота страницы неделя→квартал: {h0}→{h1}')
    shot(page, pre + '2-quarter')
    page.click('[data-per=month]'); page.wait_for_timeout(300); h2 = page.evaluate("document.documentElement.scrollHeight"); P(f'  [период месяц] высота {h2}')
    page.click('[data-per=quarter]'); page.wait_for_timeout(300)
    goto_sec(page, 'money'); shot(page, pre + '2-quarter-money')
    # 3 валюта
    inc_pln = page.inner_text('#money .sec-h p'); page.click('[data-cur=UAH]'); page.wait_for_timeout(400)
    inc_uah = page.inner_text('#money .sec-h p'); P(f'  [валюта] PLN: {inc_pln[:34]!r} → UAH: {inc_uah[:34]!r}')
    shot(page, pre + '3-uah-money'); page.evaluate('window.scrollTo(0,0)'); page.wait_for_timeout(200); shot(page, pre + '3-uah-first')
    page.click('[data-cur=PLN]'); page.click('[data-per=week]'); page.wait_for_timeout(300)
    # 4 радиальная карта: клавиатура
    page.evaluate('window.scrollTo(0,0)')
    page.focus('.cell.on'); before = page.inner_text('#read')
    page.keyboard.press('ArrowRight'); page.keyboard.press('ArrowDown'); after = page.inner_text('#read')
    foc = page.evaluate("document.activeElement.className.baseVal || document.activeElement.className")
    P(f'  [карта, клавиатура] {before!r} → {after!r}; фокус на: {foc}')
    page.click('[data-day="5"]'); page.wait_for_timeout(200); P(f'  [чип дня Сб] {page.inner_text("#read")!r}')
    # 5 сигнал раскрыт, действие, журнал
    page.evaluate('window.scrollTo(0,0)'); page.click('[data-sig=consent]'); page.wait_for_timeout(400)
    shot(page, pre + '4-signal-open')
    page.click('[data-reveal^="f1:"]'); page.wait_for_timeout(300)
    vis = page.inner_text('.fam li:first-child'); P(f'  [показать контакт] после клика: {vis!r}')
    shot(page, pre + '4-signal-reveal')
    nj = page.evaluate("document.querySelectorAll('.jrow').length"); first = page.inner_text('.jrow:first-child')
    P(f'  [журнал] первая запись после «Показати»: {first!r}')
    page.click('[data-act="consent:remind"]'); page.wait_for_timeout(400)
    first2 = page.inner_text('.jrow:first-child'); P(f'  [действие из сигнала] первая запись журнала: {first2!r}; счётчик сигналов: {page.inner_text(".badge")}')
    page.wait_for_timeout(10200)
    vis2 = page.inner_text('.fam li:first-child') if page.query_selector('.fam') else ''
    P(f'  [повторное скрытие через 10 с] {vis2!r}')
    page.click('[data-sig=consent]'); page.click('[data-sig=empty]'); page.wait_for_timeout(300)
    page.click('[data-act="empty:merge"]'); page.wait_for_timeout(300)
    emo = page.evaluate("document.querySelector('#page').dataset.emo"); bdg = page.inner_text('.badge')
    P(f'  [счётчик сигналов после 2 действий] {bdg}; Люмо: {emo}')
    # 6 фильтр и доступы
    goto_sec(page, 'manage'); shot(page, pre + '5-manage')
    n_all = page.evaluate("document.querySelectorAll('.trow, .grow').length"); page.click('[data-filt=attn]'); page.wait_for_timeout(300)
    n_f = page.evaluate("document.querySelectorAll('.trow, .grow').length"); P(f'  [фильтр «потребують уваги»] строк: {n_all} → {n_f}')
    page.click('[data-filt=all]'); page.click('[data-perm="manager:fin"]'); page.wait_for_timeout(200)
    pr = page.get_attribute('[data-perm="manager:fin"]', 'aria-pressed'); P(f'  [доступ manager:fin] aria-pressed={pr}; запись: {page.inner_text(".jrow:first-child")!r}')
    own_dis = page.evaluate("document.querySelector('[data-perm=\"owner:fin\"]').disabled")
    P(f'  [доступ владельца] кнопка заблокирована: {own_dis}')
    goto_sec(page, 'journal'); shot(page, pre + '6-journal')
    # 7 фокус
    page.evaluate('window.scrollTo(0,0)'); page.keyboard.press('Tab')
    foc2 = page.evaluate("(() => { const a = document.activeElement; const cs = getComputedStyle(a); return a.tagName + ' ' + (a.textContent||'').trim().slice(0,20) + ' outline ' + cs.outlineStyle + ' ' + cs.outlineWidth })()")
    P(f'  [Tab] фокус: {foc2}')
    sw('final')
    # 8 переключение языка без смещений
    page.evaluate('window.scrollTo(0,0)'); h_a = page.evaluate('document.documentElement.scrollHeight')
    page.click('[data-lang=en]' if lang == 'uk' else '[data-lang=uk]'); page.wait_for_timeout(400); h_b = page.evaluate('document.documentElement.scrollHeight')
    sw_now = page.evaluate("document.documentElement.scrollWidth")
    P(f'  [смена языка] высота страницы {h_a} → {h_b}; scrollWidth {sw_now} vs {w}')
    cls = page.evaluate('window.__cls'); P(f'  CLS за весь сценарий (загрузка, периоды, валюта, язык, действия): {cls:.4f}')
    P(f'  ошибки/предупреждения консоли: {len(console)} {console[:3]}; внешние запросы: {len(ext)} {ext[:3]}')
    br.close()

def fresh_shots(pw):
    # чистые кадры (без прошлых действий): первый экран en, сигнал, журнал
    for dev in ('desktop', 'phone'):
        w, h = DEV[dev]
        br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=(dev == 'phone')); page = ctx.new_page()
        page.goto(URL + '?lang=en'); page.wait_for_timeout(800)
        shot(page, f'{dev}-en-0-first'); shot(page, f'{dev}-en-0-full', full=True)
        page.click('[data-per=quarter]'); page.click('[data-cur=UAH]'); page.wait_for_timeout(400); shot(page, f'{dev}-en-0-quarter-uah')
        br.close()
    P('== reduced-motion ==')
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce'); page = ctx.new_page()
    page.goto(URL); page.wait_for_timeout(500)
    an = page.evaluate("[...document.querySelectorAll('*')].filter(e => getComputedStyle(e).animationName !== 'none').length")
    P(f'  при prefers-reduced-motion элементов с анимацией: {an}')
    br.close()

with sync_playwright() as pw:
    for dev in ('desktop', 'phone'):
        for lang in ('uk', 'en'):
            run(pw, dev, lang)
    fresh_shots(pw)

P('== пары цветов (WCAG) ==')
pairs = [('ink on page bg', '#FBEFDF', '#1E1424', 4.5), ('ink on panel', '#FBEFDF', '#2A1A31', 4.5), ('ink2 on page bg', '#D6C3CE', '#1E1424', 4.5), ('ink2 on panel', '#D6C3CE', '#2A1A31', 4.5),
 ('ink2 on panel2', '#D6C3CE', '#35223C', 4.5), ('ink на активной вкладке (panel2)', '#FBEFDF', '#35223C', 4.5), ('текст кнопки на ink', '#2A1A2E', '#FBEFDF', 4.5), ('текст бейджа на акценте', '#2A1A2E', '#FF7A45', 4.5),
 ('[не текст] маркер перетину vs фон', '#FF7A45', '#1E1424', 3.0), ('[не текст] линия графика vs фон', '#FBEFDF', '#1E1424', 3.0), ('[не текст] ячейка 100% vs ячейка 85%', '#FBEFDF', '#E2C4BE', 1.1)]
bad = 0
for n, a, b, need in pairs:
    c = cr(hx(a), hx(b)); ok = c >= need; bad += (not ok)
    P(f'  {c:5.2f}:1 {"OK " if ok else "ПЛОХО"} (нужно {need}) {n}')
P(f'  пар ниже порога: {bad}')
open(os.path.join(SHOTS, 'metrics.txt'), 'w').write('\n'.join(out) + '\n')
