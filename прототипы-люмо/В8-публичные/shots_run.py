"""В8 ч.1: кадры + замеры -> shots/*.png, ../замеры-В8-часть1.txt
Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_run.py   (chromium --disable-lcd-text)"""
import os, io, re, sys, colorsys
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(HERE, 'index.html')
SH = os.path.join(HERE, 'shots'); os.makedirs(SH, exist_ok=True)
DEV = {'desktop': (1440, 900), 'phone': (390, 844)}
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)

def lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def Lm(r): return 0.2126 * lin(r[0]) + 0.7152 * lin(r[1]) + 0.0722 * lin(r[2])
def cr(a, b):
    la, lb = Lm(a), Lm(b)
    if la < lb: la, lb = lb, la
    return (la + .05) / (lb + .05)
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

INIT = """window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput){window.__cls+=e.value;(window.__src=window.__src||[]).push([+e.value.toFixed(4),Math.round(e.startTime),(e.sources||[]).map(s=>s.node&&(s.node.nodeName+'.'+(s.node.className||s.node.id||'')))])}}).observe({type:'layout-shift',buffered:true});"""

TXT = """() => { const res=[]; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); const vw=innerWidth, vh=innerHeight;
 while(w.nextNode()){ const n=w.currentNode; if(!n.textContent.trim()) continue; const el=n.parentElement; if(!el||el.closest('[hidden],.vh,script,style')) continue;
  const cs=getComputedStyle(el); if(cs.visibility==='hidden'||cs.display==='none'||cs.opacity==='0') continue;
  const r=document.createRange(); r.selectNodeContents(n); const b=r.getBoundingClientRect(); if(b.width<1||b.height<1) continue;
  if(b.bottom<=0||b.top>=vh||b.right<=0||b.left>=vw) continue;
  const ctr=document.elementFromPoint(Math.min(vw-1,Math.max(0,b.left+b.width/2)),Math.min(vh-1,Math.max(0,b.top+b.height/2))); const hit=!!ctr&&(el.contains(ctr)||ctr.contains(el)); res.push({hit:hit, t:n.textContent.trim().slice(0,30), x:b.left, y:b.top, w:b.width, h:b.height, fs:parseFloat(cs.fontSize), col:cs.color, op:1, tag:el.tagName}); }
 return res; }"""

def parse(c):
    v = [float(x) for x in re.findall(r'[\d.]+', c)]
    return v[:3], (v[3] if len(v) > 3 else 1.0)

def vp_metrics(page, label):
    """Мин. шрифт + контраст по пикселям (текст прозрачный -> фон; сравнение с computed color) для видимых текстов окна."""
    items = page.evaluate(TXT)
    page.add_style_tag(content='*{color:transparent!important;text-shadow:none!important;-webkit-text-fill-color:transparent!important} input::placeholder{color:transparent!important} .grain{display:none!important}')
    page.wait_for_timeout(120)
    png = page.screenshot(); a = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
    page.evaluate("document.querySelectorAll('style').forEach(s=>{if(s.textContent.startsWith('*{color:transparent'))s.remove()})")
    mn = min((i['fs'] for i in items), default=0); worst = (99, '')
    skipped = 0; n = 0
    # перекрытие: elementFromPoint в центре
    ov = page.evaluate("""(pts)=>pts.map(p=>{const e=document.elementFromPoint(p[0],p[1]);return e?1:0})""", [[i['x'] + i['w'] / 2, i['y'] + i['h'] / 2] for i in items])
    ovl = [i['t'] for i in items if not i['hit']]
    items = [i for i in items if i['hit']]
    ov = ov[:len(items)]
    for it, o in zip(items, ov):
        x0, y0 = int(max(0, it['x'])), int(max(0, it['y'])); x1, y1 = int(min(a.shape[1], it['x'] + it['w'])), int(min(a.shape[0], it['y'] + it['h']))
        if x1 - x0 < 2 or y1 - y0 < 2: continue
        reg = a[y0:y1, x0:x1].reshape(-1, 3)
        bg = np.median(reg, axis=0)
        col, al = parse(it['col'])
        fg = [al * c + (1 - al) * b for c, b in zip(col, bg)]
        c = cr(fg, bg); n += 1
        if c < worst[0]: worst = (c, it['t'])
    below = []
    P(f'  [{label}] мин. шрифт {mn:.0f} px ({"OK" if mn >= 16 else "ПЛОХО"}); контраст по пикселям: текстов {n} (перекрыто липкой панелью и не считаю: {len(ovl)}), мин {worst[0]:.2f}:1 («{worst[1]}») -> {"OK" if worst[0] >= 4.5 else "ПЛОХО"}')
    return mn, worst[0]

def warm(png, label):
    from scipy import ndimage  # noqa
def warm_dots(png):
    a = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(float) / 255
    mx = a.max(2); mn = a.min(2); s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    m = ((h <= 52) | (h >= 345)) & (s >= .45) & (mx >= .6)
    B = 6; H_, W_ = m.shape; gh, gw = H_ // B, W_ // B
    mm = m[:gh * B, :gw * B].reshape(gh, B, gw, B)
    g = mm.any(axis=(1, 3)); cnt_px = mm.sum(axis=(1, 3))
    seen = np.zeros_like(g); res = 0
    for y in range(gh):
        for x in range(gw):
            if g[y, x] and not seen[y, x]:
                st_ = [(y, x)]; seen[y, x] = True; tot = 0
                while st_:
                    cy, cx = st_.pop(); tot += cnt_px[cy, cx]
                    for dy in (-2, -1, 0, 1, 2):
                        for dx in (-2, -1, 0, 1, 2):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < gh and 0 <= nx < gw and g[ny, nx] and not seen[ny, nx]: seen[ny, nx] = True; st_.append((ny, nx))
                if tot >= 40: res += 1
    return res

def run(pw, dev, lang):
    w, h = DEV[dev]
    br = pw.chromium.launch(args=['--disable-lcd-text'])
    ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
    page = ctx.new_page(); console = []; ext = []
    page.on('console', lambda m: console.append(m.text) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: console.append('pageerror ' + str(e)))
    def rq(r):
        u = r.url
        if not (u.startswith('file://') or u.startswith('data:') or u.startswith('blob:')): ext.append(u)
    page.on('request', rq)
    page.add_init_script(INIT)
    sfx = '?lang=en' if lang == 'en' else ''
    page.goto(URL + sfx); page.wait_for_timeout(700)
    pre = f'{dev}-{lang}-'
    P(f'\n===== {dev} {w}x{h} · {lang} =====')
    def frame(name, full=False):
        page.wait_for_timeout(250)
        path = os.path.join(SH, f'{pre}{name}.png'); page.screenshot(path=path, full_page=full)
        wd = page.evaluate("[document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth]")
        ok = wd[0] == wd[2] and wd[1] <= wd[2]
        P(f'[{name}] ширина html {wd[0]} / body {wd[1]} vs окно {wd[2]} -> {"OK" if ok else "ПЛОХО"}')
        ovf = page.evaluate("""() => [...document.querySelectorAll('main *, header *')].filter(e => { if (e.closest('[aria-hidden=true],[hidden],.vh') ) return false; const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && cs.visibility !== 'hidden' && (r.right > innerWidth + 0.5 || r.left < -0.5); }).map(e => e.tagName + '.' + (e.className || e.id)).slice(0, 5)""")
        P(f'  элементов, вылезающих за край окна (overflow-x:clip на .page их прячет, поэтому проверяю отдельно): {len(ovf)} {ovf} -> {"OK" if not ovf else "ПЛОХО"}')
        vp_metrics(page, name)
        dots = warm_dots(page.screenshot())
        P(f'  тёплые точки в окне: {dots} {"OK (≤4)" if dots is not None and dots <= 4 else "ПЛОХО"}')
        return ok
    def btns(sel_list, label):
        r = page.evaluate("(s)=>s.map(x=>{const e=document.querySelector(x); if(!e) return [x,null]; const b=e.getBoundingClientRect(); const vis=!e.closest('[hidden]'); return [x,Math.round(b.top),Math.round(b.bottom),Math.round(b.height),vis]})", sel_list)
        for x, *v in r:
            if v[0] is None: P(f'  кнопка {x}: нет'); continue
            P(f'  кнопка {x}: top {v[0]} bottom {v[1]} h {v[2]} при окне {h} -> {"в окне" if v[1] <= h and v[0] >= 0 else "НИЖЕ СГИБА"}')
    # 01 старт
    frame('01-start'); btns(['#v-programs .hero .btn.primary'], 'start')
    page.screenshot(path=os.path.join(SH, f'{pre}01b-start-fullpage.png'), full_page=True)
    P(f'  высота страницы {page.evaluate("document.documentElement.scrollHeight")}; карточек {page.evaluate("document.querySelectorAll(`.card`).length")}')
    # 02 выбор программы
    page.evaluate("document.querySelector('#cards').scrollIntoView()"); page.wait_for_timeout(200)
    page.click('[data-pick=teens]'); page.wait_for_timeout(250)
    frame('02-program-selected'); btns(['#dock .btn.primary'], 'dock')
    # проверка клав. фокуса на карточке
    page.keyboard.press('Tab'); page.wait_for_timeout(100)
    fo = page.evaluate("(()=>{const e=document.activeElement;const c=getComputedStyle(e);return [e.tagName+'.'+e.className.slice(0,20),c.outlineStyle,c.outlineWidth,c.outlineColor]})()")
    P(f'  [фокус клавиатурой] {fo}')
    page.click('#dock .btn.primary'); page.wait_for_timeout(300)
    # шаг 1 взрослый
    page.fill('#name', 'Анна' if lang == 'uk' else 'Anna'); frame('03-step1-adult'); btns(['#bNext'], 's1')
    # ошибка валидации: ребёнок без возраста и имени
    page.fill('#name', ''); page.click('#bNext'); page.wait_for_timeout(250)
    P(f'  [ошибка шаг 1] ошибок {page.evaluate("document.querySelectorAll(`.fe`).length")}; aria-invalid {page.evaluate("document.querySelectorAll(`[aria-invalid]`).length")}; шаг остался: {page.evaluate("document.querySelector(`#stepOf`).textContent")!r}; фокус: {page.evaluate("document.activeElement.id")!r}')
    frame('07-error-validation'); btns(['#bNext'], 'err')
    # ребёнок 11
    page.click('input[name=who][value=child]', force=True); page.wait_for_timeout(200)
    page.fill('#name', 'Марко' if lang == 'uk' else 'Marko'); page.fill('#age', '11'); frame('04-step1-child'); btns(['#bNext'], 's1c')
    page.click('#bNext'); page.wait_for_timeout(300)
    page.click('input[name=goal][value="4"]', force=True); page.click('input[name=level][value="2"]', force=True)
    P(f'  [программа переносится] на шаге 2 выбрана: {page.evaluate("document.querySelector(`#progSel`)?.value")!r} (ожидаем teens)')
    frame('05-step2-goal-level'); btns(['#bNext'], 's2')
    # без выбора -> ошибка шага 2
    page.click('#bNext'); page.wait_for_timeout(200)
    page.click('#bNext'); page.wait_for_timeout(300)
    # шаг 3 время
    P(f'  [шаг] {page.evaluate("document.querySelector(`#stepOf`).textContent")!r}')
    t0 = page.evaluate("document.querySelector('.slot span').textContent")
    page.click('.slot input[value="21-17"]'); page.click('.slot input[value="22-18"]')
    frame('06-step3-time-warsaw'); btns(['#bNext'], 's3')
    page.click('[data-tz="1"]'); page.wait_for_timeout(200)
    t1 = page.evaluate("document.querySelector('.slot span').textContent")
    P(f'  [часовой пояс] первый слот: Варшава {t0} -> Киев {t1} (ожидаем +1 ч); выбранные слоты сохранены: {page.evaluate("document.querySelectorAll(`.slot input:checked`).length")}')
    frame('06b-step3-time-kyiv')
    # шаг 3 -> ошибка слота нет; далее согласие (<16)
    page.click('#bNext'); page.wait_for_timeout(300)
    P(f'  [согласие при возрасте 11] {page.evaluate("document.querySelector(`#stepOf`).textContent")!r}')
    frame('08-consent-under16'); btns(['#bNext'], 'consent')
    page.click('#bNext'); page.wait_for_timeout(300)
    P(f'  [ошибка согласия] ошибок {page.evaluate("document.querySelectorAll(`.fe`).length")} (ожидаем 2: email, согласие)')
    frame('09-consent-error')
    page.fill('#pEmail', 'parent.example@example.com'); page.check('#consent', force=True)
    page.click('#bNext'); page.wait_for_timeout(300)
    frame('10-success-stub')
    # возраст 16 не требует согласия; возраст 15 — требует
    page.click('#bAgain'); page.wait_for_timeout(200)
    page.click('input[name=who][value=child]', force=True); page.fill('#name', 'Іра'); page.fill('#age', '16'); page.click('#bNext'); page.wait_for_timeout(200)
    page.click('input[name=goal][value="0"]', force=True); page.click('input[name=level][value="3"]', force=True); page.click('#bNext'); page.wait_for_timeout(200)
    P(f'  [возраст 16] шагов всего: {page.evaluate("document.querySelector(`#stepOf`).textContent")!r} (ожидаем «з 3»)')
    page.click('.slot input[value="20-16"]'); page.click('#bNext'); page.wait_for_timeout(300)
    P(f'  [возраст 16, шаг 3 -> ] {page.evaluate("document.querySelector(`#trialH`)?.textContent")!r}')
    # клавиатура: Tab-проход, фокус виден на каждом
    page.evaluate("window.__lumo.go('programs')"); page.wait_for_timeout(200)
    bad = []
    for _ in range(14):
        page.keyboard.press('Tab')
        r = page.evaluate("(()=>{const e=document.activeElement;if(!e||e===document.body)return null;const c=getComputedStyle(e);const b=e.getBoundingClientRect();return [e.textContent.trim().slice(0,18)||e.id, e.matches(':focus-visible'), c.outlineStyle, parseFloat(c.outlineWidth), Math.round(b.height)]})()")
        if r and (not r[1] or r[2] == 'none' or r[3] < 2): bad.append(r)
    P(f'  [клавиатура: 14 Tab по экрану «Програми»] без видимого фокуса: {len(bad)} {bad}')
    # размеры целей касания
    small = page.evaluate("[...document.querySelectorAll('button,a,input:not([type=hidden]),select,label.ch,label.slot')].filter(e=>{const b=e.getBoundingClientRect(); return b.width>0&&(b.height<44||b.width<44)&&!e.closest('[hidden]')&&!(e.matches('input[type=checkbox],input[type=radio]'))&&e.className!=='skip'}).map(e=>e.tagName+':'+(e.textContent.trim().slice(0,14))+' '+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height))")
    P(f'  [цели касания <44 px на экране «Програми»] {len(small)} {small[:6]}')
    cls = page.evaluate('window.__cls'); P('  CLS источники: ' + str(page.evaluate('window.__src||[]'))[:600])
    P(f'  CLS за сценарий: {cls:.4f}; ошибки/предупреждения консоли: {len(console)} {console[:3]}; внешние запросы: {len(ext)} {ext[:3]}')
    br.close()

with sync_playwright() as pw:
    devs = ('desktop', 'phone') if len(sys.argv) < 2 else (sys.argv[1],)
    for d in devs:
        for l in ('uk', 'en'):
            run(pw, d, l)

P('\n== пары цветов (WCAG) ==')
pairs = [('ink #FBEFDF на фоне #1E1424', '#FBEFDF', '#1E1424', 4.5), ('ink2 #D6C3CE на фоне #1E1424', '#D6C3CE', '#1E1424', 4.5), ('ink2 на карточке #2A1A31', '#D6C3CE', '#2A1A31', 4.5),
 ('ink2 на карточке (светлый верх #35223C)', '#D6C3CE', '#35223C', 4.5), ('цена кремовая #FFE3B8 на #35223C', '#FFE3B8', '#35223C', 4.5),
 ('кнопка: #2A1A2E на #FF7A45', '#2A1A2E', '#FF7A45', 4.5), ('выбранный чип: #2A1A2E на #FFE3B8', '#2A1A2E', '#FFE3B8', 4.5),
 ('ошибка #FF8FA3 на #2A1A31', '#FF8FA3', '#2A1A31', 4.5), ('placeholder #B7A2B1 на #1E1424', '#B7A2B1', '#1E1424', 4.5),
 ('[не текст] рамка чипа/кнопки/поля (#FBEFDF 55% на #2A1A31 ≈ #A1949B) vs панель', '#A1949B', '#2A1A31', 3.0), ('[не текст] фокус #FBEFDF vs #1E1424', '#FBEFDF', '#1E1424', 3.0)]
bad = 0
for n, a, b, need in pairs:
    c = cr(hx(a), hx(b)); ok = c >= need; bad += (not ok)
    P(f'  {c:5.2f}:1 {"OK " if ok else "ПЛОХО"} (нужно {need}) {n}')
P(f'  пар ниже порога: {bad}')
open(os.path.join(HERE, '..', 'замеры-В8-часть1.txt'), 'w').write(
    'ЗАМЕРЫ В8 ЧАСТЬ 1 (19.10.2026). Chromium --disable-lcd-text; Playwright через venv hermes-agent; ноутбук 1440x900, телефон 390x844; uk и en. Скрипт: В8-публичные/shots_run.py\n' + '\n'.join(out) + '\n')
