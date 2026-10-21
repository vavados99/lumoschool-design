"""Круг 10, В6: дополнительные замеры и кадры (оверлап текстов, панель телефона, фокус, маска, курсив, лента дня).
Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_r10_extra.py -> shots/r10-extra-metrics.txt"""
import os, re, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); SH = os.path.join(HERE, 'shots'); URL = 'file://' + os.path.join(HERE, 'index.html')
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)

OVERLAP_JS = """() => {
  const items = []; let nid = 0; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const n = w.currentNode; if (!n.textContent.trim()) continue; const el = n.parentElement;
    if (!el || el.closest('script,style,svg,[hidden],.skip,.grain,.toast')) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    const cl = el.closest('.vh,.sr'); if (cl) continue;
    const r = document.createRange(); r.selectNodeContents(n); nid++;
    for (const b of r.getClientRects()) { if (b.width < 1 || b.height < 1) continue; if (b.bottom < 0 || b.top > innerHeight) continue;
      /* то, что закрыто липкой панелью/шапкой, не считаем: берём только тексты, которые видны в точке центра */
      const cx = (b.left + b.right) / 2, cy = (b.top + b.bottom) / 2; const top = document.elementFromPoint(Math.min(Math.max(cx, 0), innerWidth - 1), Math.min(Math.max(cy, 0), innerHeight - 1));
      if (!top || !(el.contains(top) || top.contains(el))) continue;
      items.push({nid, t: n.textContent.trim().slice(0, 24), l: b.left, r: b.right, tp: b.top, bt: b.bottom}); } }
  const bad = [];
  for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) { const a = items[i], c = items[j]; if (a.nid === c.nid) continue;
    const ix = Math.min(a.r, c.r) - Math.max(a.l, c.l), iy = Math.min(a.bt, c.bt) - Math.max(a.tp, c.tp);
    if (ix > 1.5 && iy > 3) bad.push(a.t + ' x ' + c.t + ' (' + Math.round(ix) + 'x' + Math.round(iy) + ')'); }
  return {n: items.length, bad: bad.slice(0, 6), nbad: bad.length}; }"""
TOT = {'checks': 0, 'texts': 0, 'bad': 0}
def ov(page, tag):
    r = page.evaluate(OVERLAP_JS); TOT['checks'] += 1; TOT['texts'] += r['n']; TOT['bad'] += r['nbad']
    P(f"  [{tag}] пересечения соседних текстов (bounding boxes, видимые в окне): {r['nbad']} из {r['n']} {r['bad']}")

def run(pw, dev):
    w, h = (1440, 900) if dev == 'desktop' else (390, 844)
    br = pw.chromium.launch(args=['--disable-lcd-text']); ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=dev == 'phone')
    page = ctx.new_page(); errs = []; ext = []
    page.on('console', lambda m: errs.append(m.text) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: errs.append(str(e)))
    page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:')) else None)
    def go(q=''):
        page.goto(URL + q); page.evaluate("document.documentElement.style.scrollBehavior='auto'"); page.wait_for_timeout(900)
    def shot(name, full=False):
        page.mouse.move(0, 0); page.evaluate('document.activeElement && document.activeElement.blur()'); page.wait_for_timeout(150)
        page.screenshot(path=os.path.join(SH, f'r10-x-{dev}-uk-{name}.png'), full_page=full)
    def to(sec): page.evaluate(f"document.getElementById('{sec}').scrollIntoView()"); page.wait_for_timeout(500)
    P(f'== {dev} {w}x{h} ==')
    for st in ('early', 'open', 'live'):
        go('?demo=' + st); ov(page, st + '/today')
        sw = page.evaluate('[document.documentElement.scrollWidth, innerWidth]'); P(f'  [{st}] scrollWidth/окно: {sw}')
        if st == 'live':
            r = page.evaluate("""() => { const t = document.querySelector('.tnum'), b = document.querySelector('.burn i'), bt = document.querySelector('.burn');
              const fs = [...document.querySelectorAll('.lesson-card *')].filter(e => e.children.length === 0 && e.textContent.trim()).map(e => [parseFloat(getComputedStyle(e).fontSize), e.textContent.trim().slice(0, 14)]).sort((a, b) => b[0] - a[0]);
              const btn = document.querySelector('.lc-row .btn').getBoundingClientRect(), tr = t.getBoundingClientRect();
              return {tnum: getComputedStyle(t).fontSize, w: Math.round(b.getBoundingClientRect().width), tw: Math.round(bt.getBoundingClientRect().width), top3: fs.slice(0, 3), sub: document.querySelector('.lc-range').textContent, btn: [Math.round(btn.left), Math.round(btn.top), Math.round(btn.right), Math.round(btn.bottom)], tn: [Math.round(tr.left), Math.round(tr.top), Math.round(tr.right), Math.round(tr.bottom)]} }""")
            P(f"  [live п.2] число таймера {r['tnum']}; полоска {r['w']}/{r['tw']} px = {r['w']/r['tw']*100:.0f}% (33 из 45 мин = 73%); три крупнейших шрифта карточки: {r['top3']}; мелкая строка: «{r['sub']}»; кнопка {r['btn']}, таймер {r['tn']}")
            lst = page.evaluate("[...document.querySelectorAll('.dr')].map(e => [e.className, e.innerText.replace(/\\n/g, ' | ')])")
            P('  [Ваш день п.3] строки: ' + ' // '.join(f'{c}: {t}' for c, t in lst))
            P('  [Ваш день] «Зараз» (маркер) в ленте при идущем уроке: ' + str(page.evaluate("document.querySelectorAll('.nowline').length")) + '; текущий урок одной строкой, высота строки: ' + str(page.evaluate("Math.round(document.querySelector('.dr.cur').getBoundingClientRect().height)")) + ' px')
            ital = page.evaluate("[...document.querySelectorAll('body *')].filter(e => getComputedStyle(e).fontStyle === 'italic' && e.textContent.trim() && getComputedStyle(e).display !== 'none' && e.getBoundingClientRect().width > 0).map(e => e.tagName + '.' + e.className.toString().slice(0, 14) + ':' + e.textContent.trim().slice(0, 18))")
            P(f'  [курсив п.5] элементов с курсивом на «Сьогодні»: {len(ital)} {ital[:6]}')
            shot('live-top')
        if st == 'early': shot('early-top')
        if dev == 'phone' and st in ('open', 'live'):
            for sec in ('today', 'week', 'notes', 'swap'):
                to(sec)
                d = page.evaluate("""() => { const r = document.querySelector('.lesson-card .lc-row'); const cs = getComputedStyle(r); const vis = cs.display !== 'none';
                   const t = document.querySelector('.today'); return {sec: document.getElementById('page').dataset.sec, vis, pos: cs.position, h: vis ? Math.round(r.getBoundingClientRect().height) : 0, bottom: vis ? Math.round(innerHeight - r.getBoundingClientRect().bottom) : null, pad: getComputedStyle(t).paddingBottom, dockvar: getComputedStyle(document.documentElement).getPropertyValue('--dock-h'), pg: getComputedStyle(document.getElementById('page')).paddingBottom} }""")
                P(f"  [{st} док п.1] секция '{d['sec']}': панель видна {d['vis']} ({d['pos']}), высота {d['h']} px; padding-bottom «Сьогодні» {d['pad']} (--dock-h {d['dockvar'].strip()} + 16); padding-bottom страницы {d['pg']}")
                if st == 'live': shot(f'dock-{sec}')
        go('?demo=live'); to('notes')
        page.fill('#noteText', 'Call parent +48 600 100 200 or mail ann@example.org'); page.click('#noteForm button[type=submit]'); page.wait_for_timeout(400)
        e = page.evaluate("""() => ({err: document.querySelector('#noteErr').innerText, mark: document.querySelector('#noteErr mark')?.textContent, btn: document.querySelector('#noteForm button[type=submit]').innerHTML, why: (() => { const w = document.querySelector('#noteWhy'); return [w.hidden, w.textContent, w.getBoundingClientRect().width > 0]; })(), dis: document.querySelector('#noteForm button[type=submit]').getAttribute('aria-disabled'), html: document.documentElement.innerHTML.includes('600 100 200') })""")
        P(f"  [{st}/ошибка п.4] текст ошибки: «{e['err'][:150].replace(chr(10), ' | ')}»; подсвечено: «{e['mark']}»; номер целиком в DOM-тексте ошибки: {'600 100 200' in e['err']}; кнопка svg внутри: {'<svg' in e['btn']}; подпись [hidden, текст, видна]: {e['why']}; aria-disabled {e['dis']}")
        ov(page, st + '/notes-error')
        if st == 'live': shot('notes-error', full=False)
        go('?demo=live'); to('notes'); ov(page, st + '/notes')
        if st == 'live':
            m = page.evaluate("[...document.querySelectorAll('.memo h4, .memo li')].map(e => e.textContent.trim().slice(0, 40))"); P(f'  [notes п.5] памятка: {m}')
            shot('notes')
        go('?demo=live'); to('swap'); ov(page, st + '/swap')
        if st == 'live':
            r = page.evaluate("""() => { const f = document.querySelector('#swapForm').getBoundingClientRect(), hw = document.querySelector('.how').getBoundingClientRect(), l = document.querySelector('.swf-l').getBoundingClientRect(), r = document.querySelector('.swf-r').getBoundingClientRect(); return {how: [Math.round(hw.left), Math.round(hw.top), Math.round(hw.right), Math.round(hw.bottom)], form: [Math.round(f.left), Math.round(f.top), Math.round(f.right), Math.round(f.bottom)], l: [Math.round(l.left), Math.round(l.right)], r: [Math.round(r.left), Math.round(r.right)], items: document.querySelectorAll('.how li').length} }""")
            P(f'  [swap п.5] «Як це працює» полосой: {r["how"]} над формой {r["form"]}; колонки формы: {r["l"]} | {r["r"]}')
            shot('swap')
    # фокус: клавиатура vs мышь
    go('?demo=live'); to('swap')
    fs = lambda: page.evaluate("""() => { const o = [...document.querySelectorAll('.opt')]; return o.map(e => { const cs = getComputedStyle(e), i = e.querySelector('input'), ci = getComputedStyle(i); return [cs.outlineStyle + ' ' + cs.outlineWidth, cs.boxShadow === 'none' ? 'no-shadow' : 'shadow', ci.outlineStyle, cs.borderColor, e.matches(':has(input:focus-visible)')]; }) }""")
    page.click('.opt:nth-child(2)'); page.wait_for_timeout(200)
    P(f'  [фокус п.4] после клика мышью (карточки: outline / тень / outline у input / рамка / focus-visible): {fs()}')
    page.mouse.move(0, 0); page.screenshot(path=os.path.join(SH, f'r10-x-{dev}-uk-focus-mouse.png'), clip={'x': 0, 'y': 0, 'width': w, 'height': h})
    page.keyboard.press('ArrowDown'); page.wait_for_timeout(200)
    st = fs(); P(f'  [фокус п.4] после стрелки с клавиатуры: {st}'); P(f'  [фокус п.4] карточек с :focus-visible: {sum(1 for x in st if x[4])} (должна 1); у input своя рамка-outline: {[x[2] for x in st]}')
    page.screenshot(path=os.path.join(SH, f'r10-x-{dev}-uk-focus-keyboard.png'))
    P(f'  консоль: {len(errs)} {errs[:3]}; внешние запросы: {len(ext)} {ext[:3]}')
    # цели касания и шрифт во всех состояниях
    r = page.evaluate("""() => { const t = [...document.querySelectorAll('button, a, select, textarea, .opt, input:not([type=radio])')].filter(e => e.getBoundingClientRect().width > 0 && getComputedStyle(e).display !== 'none').map(e => [Math.round(e.getBoundingClientRect().height), e.textContent.trim().slice(0, 18) || e.id]).sort((a, b) => a[0] - b[0]); return t.slice(0, 4) }""")
    P(f'  цели касания: наименьшие по высоте (swap, live): {r}')
    br.close()

with sync_playwright() as pw:
    for dev in ('desktop', 'phone'): run(pw, dev)
P(f"== ИТОГ пересечений: проверок {TOT['checks']}, текстов {TOT['texts']}, пересечений {TOT['bad']} ==")
open(os.path.join(SH, 'r10-extra-metrics.txt'), 'w').write('\n'.join(out) + '\n')
