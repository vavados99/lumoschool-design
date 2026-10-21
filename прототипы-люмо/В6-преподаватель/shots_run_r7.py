"""Круг 7: кадры r7-* и замеры В6-преподаватель -> shots/r7-metrics.txt.
Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_run_r7.py
Тёплые точки — тот же пиксельный замер, что в В5 (shots_r6.py): HSV тон ≤52°/≥345°, насыщ ≥0,45, яркость ≥0,6; слияние ≤12 px; области ≥40 px."""
import os, io, re, colorsys, itertools
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(HERE, 'index.html')
SH = os.path.join(HERE, 'shots'); os.makedirs(SH, exist_ok=True)
DEV = {'desktop': (1440, 900), 'phone': (390, 844)}
out = []
QUIET = False
def P(*a):
    s = ' '.join(str(x) for x in a)
    if QUIET and not ('тёплые точки' in s or s.startswith('==')): return
    print(s); out.append(s)

# ---------- контраст ----------
def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def Lm(rgb): return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])
def cr(a, b):
    la, lb = Lm(a), Lm(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

INIT = """window.__cls = 0;
new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({type:'layout-shift', buffered:true});"""

TEXT_JS = """() => {
  const res = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const n = w.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || el.closest('script,style,svg') || el.closest('details:not([open])')) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
    if (b.width < 1 || b.height < 1) continue;
    res.push({t: n.textContent.trim().slice(0, 30), fs: parseFloat(cs.fontSize), color: cs.color, x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height, tag: el.tagName.toLowerCase(), fixed: !!el.closest('.lc-row')});
  }
  return res; }"""

DOM_WARM_JS = """() => {
 const res=[]; const vw=innerWidth, vh=innerHeight;
 const parse=c=>{const m=c.match(/[\\d.]+/g); if(!m)return null; const a=m.length>3?parseFloat(m[3]):1; return {r:+m[0],g:+m[1],b:+m[2],a}};
 for(const el of document.querySelectorAll('body *')){
  if(el.closest('svg')&&!el.matches('svg'))continue;
  const r=el.getBoundingClientRect(); if(r.width<2||r.height<2||r.bottom<0||r.top>vh||r.right<0||r.left>vw)continue;
  const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden')continue;
  const props=[['color',cs.color,[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())],['bg',cs.backgroundColor,true],['border',cs.borderTopColor,parseFloat(cs.borderTopWidth)>0&&cs.borderTopStyle!=='none']];
  for(const [k,c,use] of props){ if(!use)continue; const p=parse(c); if(p&&p.a>=.3) res.push({k,tag:el.tagName.toLowerCase(),cls:String(el.className&&el.className.baseVal===undefined?el.className:'').slice(0,24),c:[p.r,p.g,p.b],txt:(el.textContent||'').trim().slice(0,16)});}
 }
 return res;}"""

def warm_hsv(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255); h *= 360
    return (h <= 52 or h >= 345) and s >= .45 and v >= .6

def pixel_points(png, blk=6):
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float) / 255
    mx, mn = im.max(2), im.min(2); v = mx; s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    d = np.maximum(mx - mn, 1e-9); r, g, b = im[..., 0], im[..., 1], im[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    m = ((h <= 52) | (h >= 345)) & (s >= .45) & (v >= .6) & (mx - mn > 0)
    H, W = m.shape; hb, wb = H // blk, W // blk
    cnt = m[:hb * blk, :wb * blk].reshape(hb, blk, wb, blk).sum((1, 3))
    grid = cnt >= 6
    g2 = grid.copy()
    for dy, dx in itertools.product(range(-2, 3), repeat=2):
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
        comps.append((px, min(xs) * blk, min(ys) * blk, (max(xs) + 1) * blk, (max(ys) + 1) * blk))
    return sorted([c for c in comps if c[0] >= 40], reverse=True)

def parse(c): return [float(x) for x in re.findall(r'[\d.]+', c)[:4]]

def contrast_pixels(page):
    page.mouse.move(0, 0); page.evaluate("() => { document.activeElement && document.activeElement.blur(); document.documentElement.style.scrollBehavior = 'auto'; scrollTo(0, 0); }"); page.wait_for_timeout(600)
    items = page.evaluate(TEXT_JS)
    page.add_style_tag(content='*{color:transparent !important;-webkit-text-fill-color:transparent !important;text-shadow:none !important; transition:none !important; animation:none !important} svg{opacity:0 !important} .lesson-card .lc-row{visibility:hidden !important}')
    page.wait_for_timeout(500)
    png = page.screenshot(full_page=True)
    page.evaluate("() => [...document.querySelectorAll('style')].pop().remove()")
    im = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
    worst = []
    for it in items:
        if it['fixed']: continue   # фиксированная панель на полной странице стоит внизу, пиксели не те
        x0, y0 = int(it['x']), int(it['y']); x1, y1 = int(it['x'] + it['w']) + 1, int(it['y'] + it['h']) + 1
        reg = im[max(0, y0):y1, max(0, x0):x1]
        if reg.size == 0: continue
        lum = 0.2126 * ((reg[..., 0] / 255) ** 2.2) + 0.7152 * ((reg[..., 1] / 255) ** 2.2) + 0.0722 * ((reg[..., 2] / 255) ** 2.2)
        col = parse(it['color'])[:3]; c_min = 99
        for fn in (np.argmax, np.argmin):
            yy, xx = np.unravel_index(fn(lum), lum.shape)
            c_min = min(c_min, cr(col, reg[yy, xx]))
        worst.append((c_min, it['t'], it['tag'], tuple(int(v) for v in col)))
    worst.sort()
    return worst

def min_font(page):
    items = page.evaluate(TEXT_JS); m = min(items, key=lambda i: i['fs']); return m['fs'], m['t']

def run(pw, dev, lang, gray=False):
    w, h = DEV[dev]; ph = dev == 'phone'
    br = pw.chromium.launch(args=['--disable-lcd-text'] if gray else [])
    ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=ph)
    ctx.add_init_script(INIT)
    page = ctx.new_page(); console = []; ext = []
    page.on('console', lambda m: console.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: console.append(('pageerror', str(e))))
    page.on('requestfailed', lambda r: console.append(('reqfail', r.url)))
    page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:')) else None)
    sfx = '?lang=en' if lang == 'en' else ''
    def go(extra=''):
        q = (sfx + ('&' if sfx else '?') + extra) if extra else sfx
        page.goto(URL + q); page.wait_for_timeout(900)
    def frame(n, name, full=False):
        png = page.screenshot()
        if lang == 'uk' and not gray:
            open(os.path.join(SH, f'r7-{dev}-{n}-{name}-view.png'), 'wb').write(png)
            if full: page.screenshot(path=os.path.join(SH, f'r7-{dev}-{n}-{name}-full.png'), full_page=True)
        comps = pixel_points(png)
        ok = 'OK(≤4)' if len(comps) <= 4 else 'ПЛОХО(>4)'
        P(f'  [тёплые точки {n}-{name}] {len(comps)} {ok}: ' + '; '.join(f'{c[0]}px x{c[1]}–{c[3]} y{c[2]}–{c[4]}' for c in comps))
        return len(comps)
    def sw(tag):
        s = page.evaluate("() => [document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth, document.documentElement.scrollHeight]")
        mf = min_font(page); ok = 'OK' if s[0] == s[2] and s[1] <= s[2] else 'ПЛОХО'
        P(f'  [{tag}] scrollWidth {s[0]} / body {s[1]} vs окно {s[2]} {ok}; высота {s[3]}; мин.шрифт {mf[0]}px ({mf[1]!r})')
    def anchor(sec):
        page.click(f'#nav a[data-sec={sec}]'); page.wait_for_timeout(1100)
    def anchor_gap(sec):
        return page.evaluate("""(id) => { const nb = document.getElementById('nav').getBoundingClientRect().bottom;
          const hd = document.querySelector('#' + id + ' h1, #' + id + ' h2'); return Math.round(hd.getBoundingClientRect().top - nb); }""", sec)
    P(f'== {dev} {w}x{h} {lang}' + (' (серое сглаживание текста --disable-lcd-text)' if gray else ' (обычный запуск, как в В5)') + ' ==')
    # --- 1 покой (рано) ---
    go('demo=early'); frame(1, 'rest')
    P(f'  [рано 16:20] кнопка заблокирована: {page.evaluate("document.querySelector(`#enter`).disabled")}; Люмо emo: {page.evaluate("document.querySelector(`#page`).dataset.emo")}')
    ct = page.evaluate("document.querySelector('#lessonCard').getBoundingClientRect().top")
    P(f'  y верха карточки урока (rest): {ct:.0f}')
    # --- 2 вход открыт ---
    go(); frame(2, 'open', full=True)
    sw('open')
    cp = contrast_pixels(page)
    P(f'  контраст текста (пиксели, open): мин {cp[0][0]:.2f} ({cp[0][1]!r}, {cp[0][2]}, {cp[0][3]}); ниже 4.5: {sum(1 for c in cp if c[0] < 4.5)} из {len(cp)}')
    for c in cp[:3]: P(f'    худшие: {c[0]:.2f} {c[1]!r} {c[2]} {c[3]}')
    g = page.evaluate("""() => { const q = s => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
      return {card: q('#lessonCard'), lumo: q('.lumo-wrap'), btn: q('#enter'), nav: q('#nav'), say: q('#say'), H: innerHeight}; }""")
    P(f'  карточка {g["card"]}; Люмо {g["lumo"]}; кнопка входа {g["btn"]}; реплика {g["say"]}; нав {g["nav"]}')
    P(f'  y верха карточки урока (open): {g["card"][1]}')
    lw = g['lumo']; P(f'  Люмо целиком в окне: {lw[1] >= 0 and lw[3] <= g["H"]}')
    if ph:
        pb = page.evaluate("""() => { const r = document.querySelector('.lesson-card .lc-row'); const cs = getComputedStyle(r); const b = document.querySelector('#enter').getBoundingClientRect();
          return {pad: cs.paddingBottom, pos: cs.position, btnBottom: Math.round(b.bottom), H: innerHeight, barTop: Math.round(r.getBoundingClientRect().top)}; }""")
        P(f'  липкая кнопка: position {pb["pos"]}, padding-bottom {pb["pad"]}, низ кнопки y {pb["btnBottom"]} при окне {pb["H"]} -> отступ до низа {pb["H"] - pb["btnBottom"]} px; панель с y {pb["barTop"]}')
        nv = page.evaluate("""() => { const n = document.getElementById('nav'); const cs = getComputedStyle(n); return {h: Math.round(n.getBoundingClientRect().height), bg: cs.backgroundColor, pos: cs.position}; }""")
        P(f'  липкая шапка (вкладки): position {nv["pos"]}, высота подложки {nv["h"]} px, фон {nv["bg"]}')
    sm = page.evaluate("() => ['today','week','groups','plan','notes','swap'].map(i => getComputedStyle(document.getElementById(i)).scrollMarginTop)")
    P(f'  scroll-margin-top разделов: {sm}')
    kn = page.evaluate("() => { const t = document.body.innerText; return [(t.match(/Київ|Kyiv/g) || []).length, (document.getElementById('week').innerText.match(/Київ|Kyiv/g) || []).length, (document.getElementById('day').innerText.match(/Київ|Kyiv/g) || []).length]; }")
    P(f'  повторы «Київ/Kyiv» в видимом тексте (вся страница / неделя / ваш день): {kn[0]} / {kn[1]} / {kn[2]}')
    ages = re.findall(r'(?:Сови|Owls) · [^\n]*', page.inner_text('#week'))[:2]
    P(f'  возраст в неделе: {ages}')
    wd = page.evaluate("() => [...document.querySelectorAll('.wd')].map(e => Math.round(e.getBoundingClientRect().height))")
    P(f'  высоты колонок недели (без фикс. min-height): {wd}; min-height css: {page.evaluate("getComputedStyle(document.querySelector(`.wd`)).minHeight")}')
    # --- меню за аватаром (телефон) ---
    if ph:
        vis = page.evaluate("() => [['#tzSeg','tz'], ['[data-lang=uk]','lang']].map(([s, n]) => [n, document.querySelector(s).getBoundingClientRect().width > 0])")
        P(f'  телефон: до открытия меню видны (ширина>0): {vis}')
        page.focus('#avatarBtn'); page.keyboard.press('Enter'); page.wait_for_timeout(300)
        ex = page.evaluate("[document.getElementById('avatarBtn').getAttribute('aria-expanded'), document.getElementById('menu').getBoundingClientRect().width > 0]")
        P(f'  меню с клавиатуры (Enter на аватаре): aria-expanded {ex[0]}, меню видно {ex[1]}')
        frame(10, 'menu')
        page.keyboard.press('Tab'); foc = page.evaluate("document.activeElement.textContent.trim().slice(0,16)")
        page.click('[data-tz=kyiv]'); page.wait_for_timeout(300)
        P(f'  первый Tab из аватара -> {foc!r}; после «Київ» время в карточке: {page.evaluate("document.querySelector(`#lessonCard .lc-time b`).textContent")}')
        page.click('[data-tz=both]'); page.wait_for_timeout(200)
        page.keyboard.press('Escape'); page.wait_for_timeout(200)
        P(f'  Esc закрывает меню: {page.evaluate("document.getElementById(`avatarBtn`).getAttribute(`aria-expanded`)") == "false"}; фокус вернулся на аватар: {page.evaluate("document.activeElement.id") == "avatarBtn"}')
    # --- 3 вход нажат ---
    page.click('#enter'); page.wait_for_timeout(500)
    frame(3, 'entered')
    P(f'  [вход] emo {page.evaluate("document.querySelector(`#page`).dataset.emo")}; заметка: {page.inner_text("#enterNote")!r}')
    # --- 4 live ---
    go('demo=live'); frame(4, 'live', full=True)
    txt = page.inner_text('#lessonCard')
    P(f'  [live] карточка: «Зараз/Now…» есть: {bool(re.search(r"Зараз · лишилось 33 хв|Now · 33 min left", txt))}; «Найближчий/Next lesson» нет: {not re.search(r"Найближчий|Next lesson", txt)}; «Вхід відкрито/Entry is open» нет: {not re.search(r"Вхід відкрито|Entry is open|open from", txt)}')
    P(f'  [live] реплика Люмо: {page.inner_text("#say")!r}; emo {page.evaluate("document.querySelector(`#page`).dataset.emo")}; рот видим: {page.evaluate("getComputedStyle(document.querySelector(`.lumo .mouth`)).opacity")}; искры opacity: {page.evaluate("getComputedStyle(document.querySelector(`.lumo .sparks`)).opacity")}')
    lm = page.evaluate("() => { const r = document.querySelector('.lumo-wrap').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom), Math.round(r.width), innerHeight]; }")
    P(f'  [live] Люмо x {lm[0]}–{lm[2]}, y {lm[1]}–{lm[3]}, размер {lm[4]} px; в окне: {lm[1] >= 0 and lm[3] <= lm[5]}; y верха карточки: {page.evaluate("Math.round(document.querySelector(`#lessonCard`).getBoundingClientRect().top)")}')
    dm = page.evaluate(DOM_WARM_JS)
    wl = [d for d in dm if warm_hsv(*d['c']) and not d['cls'].startswith('lumo')]
    P(f'  [live] тёплые элементы по CSS (цвет/фон/рамка в окне, без SVG): {[(d["tag"], d["k"], d["cls"], d["txt"]) for d in wl]}')
    P(f'  [live] заливок оранжевым фоном: {sum(1 for d in wl if d["k"] == "bg")}')
    cpl = contrast_pixels(page)
    P(f'  контраст текста (пиксели, live): мин {cpl[0][0]:.2f} ({cpl[0][1]!r}); ниже 4.5: {sum(1 for c in cpl if c[0] < 4.5)} из {len(cpl)}')
    if ph:
        for s_ in ('week', 'notes'):
            anchor(s_); P(f'  [якорь {s_} на телефоне] зазор заголовок−низ вкладок: {anchor_gap(s_)} px (≥0 = не прячется)')
    # --- 5 неделя ---
    go(); anchor('week'); frame(5, 'week')
    P(f'  [якорь week] зазор заголовок−низ вкладок: {anchor_gap("week")} px')
    go('tz=kyiv'); P(f'  [пояс Киев] время в карточке: {page.evaluate("document.querySelector(`#lessonCard .lc-time b`).textContent")}'); go()
    # --- группы, план ---
    anchor('groups'); frame(7, 'groups'); P(f'  [якорь groups] зазор: {anchor_gap("groups")} px')
    page.click('[data-grp=owls]'); page.wait_for_timeout(200)
    anchor('plan'); P(f'  [якорь plan] зазор: {anchor_gap("plan")} px'); page.click('[data-chk="0"]'); page.wait_for_timeout(200); frame(8, 'plan')
    # --- заметки: ошибка ---
    anchor('notes'); P(f'  [якорь notes] зазор: {anchor_gap("notes")} px')
    page.fill('#noteText', 'Call parent +48 600 100 200'); page.click('#noteForm button[type=submit]'); page.wait_for_timeout(300)
    ev = page.evaluate("""() => { const e = document.querySelector('#noteErr .err'); const m = e && e.querySelector('mark'); const b = document.querySelector('#noteForm button[type=submit]');
      const bs = getComputedStyle(b); return {err: !!e, mark: m ? m.textContent : null, why: e ? e.querySelector('b').textContent : null, col: e ? getComputedStyle(e.querySelector('b')).color : null, border: e ? getComputedStyle(e).borderTopColor : null,
        btnCls: b.className, btnBg: bs.backgroundColor, btnShadow: bs.boxShadow, saved: document.querySelectorAll('.saved li').length}; }""")
    P(f'  [ошибка] показана: {ev["err"]}; подсвечено mark: {ev["mark"]!r}; фраза «чому»: {ev["why"]!r}; цвет заголовка {ev["col"]}, рамка {ev["border"]}')
    P(f'  [ошибка] кнопка «Зберегти»: class={ev["btnCls"]!r}, фон {ev["btnBg"]}, тень {ev["btnShadow"]}; записей в списке (не должно прибавиться): {ev["saved"]}')
    page.evaluate("document.querySelector('#noteForm button[type=submit]').scrollIntoView({block: 'center'})"); page.wait_for_timeout(1400)
    frame(6, 'notes-error')
    cpe = contrast_pixels(page)
    P(f'  контраст текста (пиксели, ошибка): мин {cpe[0][0]:.2f} ({cpe[0][1]!r}); ниже 4.5: {sum(1 for c in cpe if c[0] < 4.5)} из {len(cpe)}')
    page.fill('#noteText', 'Topic understood. Review apple, bread.'); page.click('#noteForm button[type=submit]'); page.wait_for_timeout(300)
    P(f'  [заметки] нормальная заметка сохранена: записей {page.evaluate("document.querySelectorAll(`.saved li`).length")}')
    for bad in ('mail me a@b.co', 'https://example.org/x', 'мій телеграм'):
        page.fill('#noteText', bad); page.click('#noteForm button[type=submit]'); page.wait_for_timeout(100)
        P(f'  [заметки] {bad!r} отклонено: {page.evaluate("!!document.querySelector(`#noteErr .err`)")}')
    page.fill('#noteText', '')
    # --- замена ---
    anchor('swap'); frame(9, 'swap'); P(f'  [якорь swap] зазор: {anchor_gap("swap")} px')
    page.click('input[value=l7]'); page.click('#swapForm button[type=submit]'); page.wait_for_timeout(400)
    P(f'  [замена] статус после отправки: {page.inner_text("#swap .st")!r}')
    sw('final')
    cur = []
    for s_ in ('today', 'week', 'groups', 'plan', 'notes', 'swap'):
        anchor(s_); cur.append(page.evaluate("document.querySelector('#nav a[aria-current=true]')?.dataset.sec"))
    P(f'  активный пункт навигации при переходе по якорям: {cur}')
    hits = re.findall(r'@|\+\d{2,}|https?:|\b\d{3}[ -]\d{3}[ -]\d{3}\b', page.evaluate("document.body.innerText"))
    P(f'  контакты в видимом тексте страницы: {hits}')
    P(f'  CLS за сценарий: {page.evaluate("window.__cls"):.4f}')
    P(f'  ошибки/предупреждения консоли: {len(console)} {console[:3]}; внешние запросы: {len(ext)} {ext[:3]}')
    br.close()

with sync_playwright() as pw:
    for dev in ('desktop', 'phone'):
        for lang in ('uk', 'en'):
            run(pw, dev, lang)
    QUIET = True
    for dev in ('desktop', 'phone'):
        for lang in ('uk', 'en'):
            run(pw, dev, lang, gray=True)
QUIET = False

P('== пары цветов (WCAG) ==')
pairs = [('ink on panel', '#FBEFDF', '#2A1A31', 4.5), ('ink on panel2', '#FBEFDF', '#35223C', 4.5), ('ink2 on panel', '#D6C3CE', '#2A1A31', 4.5), ('ink2 on page bg', '#D6C3CE', '#1E1424', 4.5),
 ('ink2 on panel2', '#D6C3CE', '#35223C', 4.5), ('кнопка: тёмный текст на #FF7A45', '#2A1A2E', '#FF7A45', 4.5),
 ('ошибка: розовый #FF8FA3 на panel', '#FF8FA3', '#2A1A31', 4.5), ('ошибка: розовый на textarea #1E1424', '#FF8FA3', '#1E1424', 4.5),
 ('ошибка: ink на mark (≈#4B3046)', '#FBEFDF', '#4B3046', 4.5), ('[не текст] розовая рамка vs panel', '#FF8FA3', '#2A1A31', 3.0), ('[не текст] ink2 border vs panel', '#D6C3CE', '#2A1A31', 3.0)]
bad = 0
for n, a, b, need in pairs:
    c = cr(hx(a), hx(b)); ok = c >= need; bad += (not ok)
    P(f'  {c:5.2f}:1 {"OK " if ok else "ПЛОХО"} (нужно {need}) {n}')
P(f'  пар ниже порога: {bad}')
open(os.path.join(SH, 'r7-metrics.txt'), 'w').write('\n'.join(out) + '\n')
