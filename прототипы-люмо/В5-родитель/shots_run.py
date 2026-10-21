"""Кадры и замеры В5-родитель. Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_run.py"""
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
def L(rgb): return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])
def cr(a, b):
    la, lb = L(a), L(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

INIT = """window.__cls = 0;
new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({type:'layout-shift', buffered:true});"""

TEXT_JS = """(scope) => {
  const root = scope ? document.querySelector(scope) : document.body;
  const res = []; const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const n = w.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || el.closest('script,style,svg')) continue;
    if (el.closest('[hidden]')) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
    if (b.width < 1 || b.height < 1) continue;
    res.push({t: n.textContent.trim().slice(0, 30), fs: parseFloat(cs.fontSize), color: cs.color, x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height, tag: el.tagName.toLowerCase()});
  }
  return res; }"""

def parse(c): return [float(x) for x in re.findall(r'[\d.]+', c)[:4]]

def contrast_pixels(page, scope=None):
    items = page.evaluate(TEXT_JS, scope)
    page.add_style_tag(content='*{color:transparent !important;-webkit-text-fill-color:transparent !important;text-shadow:none !important} svg{opacity:0 !important}' + ('' if scope else ''))
    page.wait_for_timeout(200)
    png = page.screenshot(full_page=(scope is None))
    page.evaluate("() => [...document.querySelectorAll('style')].pop().remove()")
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
    worst = []
    for it in items:
        x0, y0 = int(it['x']), int(it['y']); x1, y1 = int(it['x'] + it['w']) + 1, int(it['y'] + it['h']) + 1
        if scope: y0 -= int(page.evaluate('scrollY')); y1 -= int(page.evaluate('scrollY'))
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

def min_font(page, scope=None):
    items = page.evaluate(TEXT_JS, scope)
    m = min(items, key=lambda i: i['fs'])
    return m['fs'], m['t']

def shot(page, name, full=True):
    page.screenshot(path=os.path.join(SHOTS, name + '.png'), full_page=full)

def rail_rel(page):
    return page.evaluate("""() => { const R = document.querySelector('#rail').getBoundingClientRect();
      const q = s => { const r = document.querySelector(s).getBoundingClientRect(); return [r.left - R.left, r.top - R.top, r.width, r.height].map(v => Math.round(v * 100) / 100); };
      const sv = document.querySelector('#lumo');
      return {box: q('#lumoBox'), say: q('#say'), nav: q('#nav'), emo: document.querySelector('#page').dataset.emo}; }""")

def scroll_to(page, sec):
    page.evaluate("(id) => { const el = document.getElementById(id); window.scrollTo({top: el.getBoundingClientRect().top + scrollY - (innerWidth <= 820 ? 150 : 90), behavior: 'instant'}); }", sec)
    page.wait_for_timeout(500)

def run(pw, dev, lang, state_log):
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
    def sw(tag):
        s = page.evaluate("() => [document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth, document.documentElement.scrollHeight]")
        mf = min_font(page)
        ok = 'OK' if s[0] == s[2] and s[1] <= s[2] else 'ПЛОХО'
        P(f'  [{tag}] scrollWidth {s[0]} / body {s[1]} vs окно {s[2]} {ok}; высота {s[3]}; мин.шрифт {mf[0]}px ({mf[1]!r})')
        return s, mf
    rects = {}
    # 1 покой
    shot(page, f'{dev}-{lang}-1-rest'); shot(page, f'{dev}-{lang}-1-rest-view', full=False)
    sw('rest'); rects['rest'] = rail_rel(page)
    cp = contrast_pixels(page)
    P(f'  контраст текста (пиксели): мин {cp[0][0]:.2f} ({cp[0][1]!r}, {cp[0][2]}, {cp[0][3]}); ниже 4.5: {sum(1 for c in cp if c[0] < 4.5)} из {len(cp)}')
    for c in cp[:4]: P(f'    худшие: {c[0]:.2f} {c[1]!r} {c[2]} {c[3]}')
    # 2 второй ребёнок
    page.click('[data-kid=max]'); page.wait_for_timeout(500)
    shot(page, f'{dev}-{lang}-2-kid2'); shot(page, f'{dev}-{lang}-2-kid2-view', full=False)
    sw('kid2')
    scroll_to(page, 'schedule'); shot(page, f'{dev}-{lang}-2-kid2-schedule-view', full=False)
    # 3 согласия + подтверждение отзыва
    scroll_to(page, 'consents'); page.wait_for_timeout(700)
    rects['consents'] = rail_rel(page); shot(page, f'{dev}-{lang}-3-consents-view', full=False)
    page.click('[data-revoke=part]'); page.wait_for_timeout(900)
    rects['dialog'] = rail_rel(page)
    shot(page, f'{dev}-{lang}-4-revoke-dialog', full=False)
    mfd = min_font(page, '#dlg'); cpd = contrast_pixels(page, '#dlg')
    P(f'  [диалог] мин.шрифт {mfd[0]}px; контраст мин {cpd[0][0]:.2f} ({cpd[0][1]!r}); <4.5: {sum(1 for c in cpd if c[0] < 4.5)} из {len(cpd)}')
    foc = page.evaluate("document.activeElement.id"); P(f'  [диалог] фокус на «Залишити як є»: {foc == "dlgKeep"}')
    page.keyboard.press('Escape'); page.wait_for_timeout(300)
    esc_ok = page.evaluate("document.getElementById('scrim').hidden")
    P(f'  [диалог] Esc закрывает: {esc_ok}')
    page.click('[data-revoke=part]'); page.wait_for_timeout(300); page.click('#dlgGo'); page.wait_for_timeout(1200)
    shot(page, f'{dev}-{lang}-5-after-revoke-view', full=False)
    em = page.evaluate("document.querySelector('#page').dataset.emo")
    ac = page.evaluate("document.querySelector('[data-sw=part]').getAttribute('aria-checked')")
    P(f'  [после отзыва] эмоция {em}; тумблер aria-checked={ac}')
    page.wait_for_timeout(3600)
    scroll_to(page, 'schedule'); shot(page, f'{dev}-{lang}-5-paused-schedule-view', full=False)
    # 4 прогресс — радость
    scroll_to(page, 'progress'); page.wait_for_timeout(900)
    rects['progress'] = rail_rel(page); shot(page, f'{dev}-{lang}-6-progress-joy-view', full=False)
    scroll_to(page, 'messages'); page.wait_for_timeout(500)
    rects['messages'] = rail_rel(page); shot(page, f'{dev}-{lang}-7-messages-view', full=False)
    page.fill('#msgText', 'Hello! Sat 11:00 works for us.' if lang == 'en' else 'Добрий день! Субота о 11:00 нам підходить.')
    page.click('#compose button[type=submit]'); page.wait_for_timeout(600)
    shot(page, f'{dev}-{lang}-7-messages-sent-view', full=False)
    scroll_to(page, 'data'); page.click('[data-stub=de]'); page.wait_for_timeout(400)
    shot(page, f'{dev}-{lang}-8-data-view', full=False)
    sw('final')
    # сдвиг Люмо
    base = rects['rest']; dd = {}
    for k in ('box', 'say', 'nav'):
        dd[k] = max(max(abs(r[k][i] - base[k][i]) for i in range(4)) for r in rects.values())
    emos = ', '.join(k + ':' + r['emo'] for k, r in rects.items())
    P('  сдвиг блока Люмо при смене эмоции (%s): box %s px, say %s px, nav %s px' % (emos, dd['box'], dd['say'], dd['nav']))
    # навигация
    page.evaluate('window.scrollTo(0,0)'); page.wait_for_timeout(300)
    cur = []
    for s in ('schedule', 'consents', 'progress', 'messages', 'data'):
        scroll_to(page, s); page.wait_for_timeout(300)
        cur.append(page.evaluate("document.querySelector('#nav a[aria-current=true]')?.dataset.sec"))
    P(f'  активный пункт навигации при скролле к разделам: {cur}')
    cls = page.evaluate('window.__cls'); P(f'  CLS за сценарий: {cls:.4f}')
    P(f'  ошибки/предупреждения консоли: {len(console)} {console[:3]}; внешние запросы: {len(ext)} {ext[:3]}')
    br.close()

with sync_playwright() as pw:
    for dev in ('desktop', 'phone'):
        for lang in ('uk', 'en'):
            run(pw, dev, lang, None)

P('== пары цветов (WCAG) ==')
pairs = [('ink on panel', '#FBEFDF', '#2A1A31', 4.5), ('ink2 on panel', '#D6C3CE', '#2A1A31', 4.5), ('ink2 on page bg', '#D6C3CE', '#1E1424', 4.5),
 ('ink2 on panel2 (nav/кнопки)', '#D6C3CE', '#35223C', 4.5), ('gold on panel', '#FFD9A8', '#2A1A31', 4.5), ('gold on panel2', '#FFD9A8', '#35223C', 4.5),
 ('button text on accent', '#2A1A2E', '#FF7A45', 4.5), ('button text on gold (UK/EN)', '#2A1A2E', '#FFD9A8', 4.5),
 ('bad on bad-bg', '#FFB3B8', '#4A2030', 4.5), ('bad-ink on bad (значок/пилюля)', '#3A1020', '#FFB3B8', 4.5), ('bad on panel (кнопка «Відкликати»)', '#FFB3B8', '#2A1A31', 4.5),
 ('paper-ink on paper', '#2A1A2E', '#F6E6D0', 4.5), ('paper-ink2 on paper', '#5A4260', '#F6E6D0', 4.5), ('paper accent #8A2F3E on paper', '#8A2F3E', '#F6E6D0', 4.5),
 ('placeholder ink2 on textarea', '#D6C3CE', '#1E1424', 4.5), ('me-bubble date #5A3A3A on gold', '#5A3A3A', '#FFD9A8', 4.5),
 ('[не текст] accent switch vs panel', '#FF7A45', '#2A1A31', 3.0), ('[не текст] ink2 border vs panel', '#D6C3CE', '#2A1A31', 3.0), ('[не текст] gold border vs page', '#FFD9A8', '#1E1424', 3.0)]
bad = 0
for n, a, b, need in pairs:
    c = cr(hx(a), hx(b)); ok = c >= need; bad += (not ok)
    P(f'  {c:5.2f}:1 {"OK " if ok else "ПЛОХО"} (нужно {need}) {n}')
P(f'  пар ниже порога: {bad}')
open(os.path.join(SHOTS, 'metrics.txt'), 'w').write('\n'.join(out) + '\n')
