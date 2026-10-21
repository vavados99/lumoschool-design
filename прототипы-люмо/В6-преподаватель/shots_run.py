"""Кадры и замеры В6-преподаватель. Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_run.py"""
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

def scroll_to(page, sec):
    page.evaluate("(id) => { const el = document.getElementById(id); window.scrollTo({top: el.getBoundingClientRect().top + scrollY - (innerWidth <= 820 ? 70 : 70), behavior: 'instant'}); }", sec)
    page.wait_for_timeout(500)

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
    def sw(tag):
        s = page.evaluate("() => [document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth, document.documentElement.scrollHeight]")
        mf = min_font(page)
        ok = 'OK' if s[0] == s[2] and s[1] <= s[2] else 'ПЛОХО'
        P(f'  [{tag}] scrollWidth {s[0]} / body {s[1]} vs окно {s[2]} {ok}; высота {s[3]}; мин.шрифт {mf[0]}px ({mf[1]!r})')
    # 1 вход открыт (по умолчанию)
    shot(page, f'{dev}-{lang}-1-open-full'); shot(page, f'{dev}-{lang}-1-open-view', full=False)
    sw('open')
    cp = contrast_pixels(page)
    P(f'  контраст текста (пиксели): мин {cp[0][0]:.2f} ({cp[0][1]!r}, {cp[0][2]}, {cp[0][3]}); ниже 4.5: {sum(1 for c in cp if c[0] < 4.5)} из {len(cp)}')
    for c in cp[:4]: P(f'    худшие: {c[0]:.2f} {c[1]!r} {c[2]} {c[3]}')
    # 2 нажатие «Войти»
    page.click('#enter'); page.wait_for_timeout(500); shot(page, f'{dev}-{lang}-2-entered-view', full=False)
    emo = page.evaluate("document.querySelector('#page').dataset.emo"); en_ = page.inner_text('#enterNote')
    P(f'  [вход] эмоция {emo}; заметка: {en_!r}')
    HAS_ERR = "!!document.querySelector('#noteErr .err')"; N_SAVED = "document.querySelectorAll('.saved li').length"
    # 3 рано: кнопка заблокирована
    page.click('[data-demo=early]'); page.wait_for_timeout(500)
    dis = page.evaluate("document.querySelector('#enter').disabled")
    P(f'  [рано 16:20] кнопка «Войти» заблокирована: {dis}')
    shot(page, f'{dev}-{lang}-3-early-view', full=False)
    # 4 урок идёт
    page.click('[data-demo=live]'); page.wait_for_timeout(500)
    shot(page, f'{dev}-{lang}-4-live-view', full=False)
    page.click('[data-demo=open]'); page.wait_for_timeout(300)
    # 5 неделя: только Киев
    scroll_to(page, 'week'); shot(page, f'{dev}-{lang}-5-week-both-view', full=False)
    page.evaluate("window.scrollTo(0,0)"); page.click('[data-tz=kyiv]'); page.wait_for_timeout(300)
    scroll_to(page, 'week'); shot(page, f'{dev}-{lang}-5-week-kyiv-view', full=False)
    kt = page.evaluate("document.querySelector('#lessonCard .lc-time b').textContent")
    P(f'  [пояс Киев] время ближайшего урока в карточке: {kt}')
    page.evaluate("window.scrollTo(0,0)"); page.click('[data-tz=both]'); page.wait_for_timeout(300)
    # 6 группы
    scroll_to(page, 'groups'); shot(page, f'{dev}-{lang}-6-groups-view', full=False)
    page.click('[data-grp=owls]'); page.wait_for_timeout(300); shot(page, f'{dev}-{lang}-6-groups-owls-view', full=False)
    # 7 план
    scroll_to(page, 'plan'); page.click('[data-chk="0"]'); page.wait_for_timeout(200); shot(page, f'{dev}-{lang}-7-plan-view', full=False)
    # 8 заметки: плохая и хорошая
    scroll_to(page, 'notes')
    page.fill('#noteText', 'Call parent +48 600 100 200'); page.click('#noteForm button[type=submit]'); page.wait_for_timeout(300)
    a_, b_ = page.evaluate(HAS_ERR), page.evaluate(N_SAVED)
    P(f'  [заметки] контакт-подобный текст отклонён: {a_}; записей в списке: {b_}')
    shot(page, f'{dev}-{lang}-8-notes-blocked-view', full=False)
    page.fill('#noteText', 'Topic understood. Review apple, bread.'); page.click('#noteForm button[type=submit]'); page.wait_for_timeout(300)
    c_ = page.evaluate(N_SAVED)
    P(f'  [заметки] нормальная заметка сохранена: записей {c_}')
    for bad in ('mail me a@b.co', 'https://example.org/x', 'мій телеграм'):
        page.fill('#noteText', bad); page.click('#noteForm button[type=submit]'); page.wait_for_timeout(100)
        d_ = page.evaluate(HAS_ERR)
        P(f'  [заметки] {bad!r} отклонено: {d_}')
    page.fill('#noteText', '')
    shot(page, f'{dev}-{lang}-8-notes-saved-view', full=False)
    # 9 замена
    scroll_to(page, 'swap'); shot(page, f'{dev}-{lang}-9-swap-view', full=False)
    page.click('input[value=l7]'); page.click('#swapForm button[type=submit]'); page.wait_for_timeout(400)
    shot(page, f'{dev}-{lang}-9-swap-sent-view', full=False)
    sst = page.inner_text('#swap .st')
    P(f'  [замена] после отправки статус: {sst!r}')
    sw('final')
    # навигация
    page.evaluate('window.scrollTo(0,0)'); page.wait_for_timeout(300)
    cur = []
    for s in ('today', 'week', 'groups', 'plan', 'notes', 'swap'):
        scroll_to(page, s); page.wait_for_timeout(250)
        cur.append(page.evaluate("document.querySelector('#nav a[aria-current=true]')?.dataset.sec"))
    P(f'  активный пункт навигации при скролле: {cur}')
    # видимый DOM-текст: контакты
    txt = page.evaluate("document.body.innerText")
    hits = re.findall(r'@|\+\d{2,}|https?:|\b\d{3}[ -]\d{3}[ -]\d{3}\b', txt)
    P(f'  контакты в видимом тексте страницы: {hits}')
    cls = page.evaluate('window.__cls'); P(f'  CLS за сценарий: {cls:.4f}')
    P(f'  ошибки/предупреждения консоли: {len(console)} {console[:3]}; внешние запросы: {len(ext)} {ext[:3]}')
    br.close()

with sync_playwright() as pw:
    for dev in ('desktop', 'phone'):
        for lang in ('uk', 'en'):
            run(pw, dev, lang)

P('== пары цветов (WCAG) ==')
pairs = [('ink on panel', '#FBEFDF', '#2A1A31', 4.5), ('ink on panel2', '#FBEFDF', '#35223C', 4.5), ('ink2 on panel', '#D6C3CE', '#2A1A31', 4.5), ('ink2 on page bg', '#D6C3CE', '#1E1424', 4.5),
 ('ink2 on panel2', '#D6C3CE', '#35223C', 4.5), ('accent on panel', '#FF7A45', '#2A1A31', 4.5), ('accent on dark card', '#FF7A45', '#1E1424', 4.5),
 ('button text on accent', '#2A1A2E', '#FF7A45', 4.5), ('segment active text', '#2A1A2E', '#FBEFDF', 4.5),
 ('[не текст] ink2 border vs panel', '#D6C3CE', '#2A1A31', 3.0), ('[не текст] accent vs panel', '#FF7A45', '#2A1A31', 3.0)]
bad = 0
for n, a, b, need in pairs:
    c = cr(hx(a), hx(b)); ok = c >= need; bad += (not ok)
    P(f'  {c:5.2f}:1 {"OK " if ok else "ПЛОХО"} (нужно {need}) {n}')
P(f'  пар ниже порога: {bad}')
open(os.path.join(SHOTS, 'metrics.txt'), 'w').write('\n'.join(out) + '\n')
