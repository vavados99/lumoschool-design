"""Круг 13, В6: кадры r13-* и замеры -> shots/metrics-r13.txt.
Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_r13.py [desktop|phone] [uk|en]
Все кадры снимаются с ?clean=1 (служебный язычок «Стан прототипу» скрыт). Логические проверки (пузырь один раз, переключатели) идут на странице БЕЗ clean.
Для «до/после» (рамки, висячие слова, двойная рамка) страница круга 10 берётся из scratch-копии backup-r10.
"""
import sys, os, io, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m11lib import *   # P, out, helpers: vp_contrast, summarize, pixel_points, cr, hx, INIT, VP_JS
from playwright.sync_api import sync_playwright

OLD = 'file:///root/projects/english-school/прототипы-люмо/В6-преподаватель/backup-r11/index.html'
PFX = 'r13-'
NBSP_ = chr(160)
TOT = {'frames': 0, 'wbad': 0, 'ov': 0, 'lowc': 0, 'minfs': 99, 'cls': [], 'console': 0, 'ext': 0}

OVERLAP_JS = """() => {
  const items = []; let nid = 0; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const n = w.currentNode; if (!n.textContent.trim()) continue; const el = n.parentElement;
    if (!el || el.closest('script,style,svg,[hidden],.grain')) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    const r = document.createRange(); r.selectNodeContents(n); nid++;
    for (const b of r.getClientRects()) { if (b.width < 1 || b.height < 1) continue; if (b.bottom < 0 || b.top > innerHeight) continue;
      const cx = (b.left + b.right) / 2, cy = (b.top + b.bottom) / 2; const top = document.elementFromPoint(Math.min(Math.max(cx, 0), innerWidth - 1), Math.min(Math.max(cy, 0), innerHeight - 1));
      if (!top || !(el.contains(top) || top.contains(el))) continue;
      items.push({nid, t: n.textContent.trim().slice(0, 24), l: b.left, r: b.right, tp: b.top, bt: b.bottom}); } }
  const bad = [];
  for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) { const a = items[i], c = items[j]; if (a.nid === c.nid) continue;
    const ix = Math.min(a.r, c.r) - Math.max(a.l, c.l), iy = Math.min(a.bt, c.bt) - Math.max(a.tp, c.tp);
    if (ix > 1.5 && iy > 3) bad.push(a.t + ' x ' + c.t + ' (' + Math.round(ix) + 'x' + Math.round(iy) + ')'); }
  return {n: items.length, bad: bad.slice(0, 5), nbad: bad.length}; }"""

# базовая линия: нулевой inline-block в конце элемента
BASE_JS = """() => {
  const bl = el => { const s = document.createElement('span'); s.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline'; el.appendChild(s); const y = s.getBoundingClientRect().bottom; s.remove(); return +y.toFixed(1); };
  const n = document.querySelector('.tnum') || document.querySelector('.lc-time b'); const l = document.querySelector('#enter .btn-l') || document.querySelector('#enter > span');
  return {num: bl(n), btn: bl(l)}; }"""

# висячие слова: по строкам каждого слова (Range), последняя строка = одно короткое слово, или «·» в начале/конце строки
HANG_JS = """() => {
  const sel = '.dr .dg, .dr .dt, .tab span, .privacy p, .privacy b, .opt small, .opt b, .tlab, .say span, .how li span, .lc-range, .lc-top span, .info, .lc-when, .tpct, .hint, .tz-note span, .sec-h p, .stu span';
  const res = []; let n = 0;
  document.querySelectorAll(sel).forEach(el => {
    const cs = getComputedStyle(el); if (cs.display === 'none' || el.getBoundingClientRect().width < 1 || el.closest('[hidden]')) return;
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const words = [];
    while (tw.nextNode()) { const t = tw.currentNode; if (t.parentElement.classList.contains('hid')) continue; const re = /[^ \\n]+/g; let m; while ((m = re.exec(t.textContent))) { const r = document.createRange(); r.setStart(t, m.index); r.setEnd(t, m.index + m[0].length); const b = r.getClientRects(); if (b.length) words.push({w: m[0], top: Math.round(b[0].top)}); } }
    if (words.length < 2) return; n++;
    const lines = []; words.forEach(x => { const L = lines[lines.length - 1]; if (L && Math.abs(L.top - x.top) < 6) L.ws.push(x.w); else lines.push({top: x.top, ws: [x.w]}); });
    if (lines.length < 2) return;
    const last = lines[lines.length - 1].ws;
    const strayDot = lines.some((L, i) => (i > 0 && L.ws[0].replace(/\\u00a0/g, ' ').trim().startsWith('·')) || (i < lines.length - 1 && L.ws[L.ws.length - 1].replace(/\\u00a0/g, " ").trim().endsWith("·")));
    const oneShort = last.length === 1 && last[0].length <= 6;
    if (strayDot || oneShort) res.push((strayDot ? '«·» на краю строки' : 'висячее «' + last[0] + '»') + ' в «' + el.textContent.trim().slice(0, 40) + '»');
  });
  return {n, bad: res}; }"""

BORDERS_JS = """() => { let n = 0; const kinds = {};
  document.querySelectorAll('body *').forEach(el => { if (el.closest('svg') && !el.matches('svg')) return; const r = el.getBoundingClientRect(); if (r.width < 4 || r.height < 4) return; const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const vis = s => parseFloat(cs['border' + s + 'Width']) > 0 && cs['border' + s + 'Style'] !== 'none' && !/rgba?\\(\\d+, \\d+, \\d+, 0\\)/.test(cs['border' + s + 'Color']);
    if (['Top', 'Right', 'Bottom', 'Left'].some(vis)) { n++; const k = el.tagName.toLowerCase() + '.' + String(el.className && el.className.baseVal === undefined ? el.className : '').split(' ')[0]; kinds[k] = (kinds[k] || 0) + 1; } });
  return {n, top: Object.entries(kinds).sort((a, b) => b[1] - a[1]).slice(0, 8)}; }"""

WARM_JS = """() => [...document.querySelectorAll('.day *')].filter(e => { const r = e.getBoundingClientRect(); if (r.width < 2) return false; const cs = getComputedStyle(e); const w = c => { const m = c.match(/[\\d.]+/g); if (!m) return false; const [R, G, B] = m.map(Number); const a = m.length > 3 ? m[3] : 1; return a > .3 && R > 200 && G > 80 && G < 170 && B < 120; }; return w(cs.backgroundColor) || (e.childElementCount === 0 && e.textContent.trim() && w(cs.color)) || (parseFloat(cs.borderTopWidth) > 0 && w(cs.borderTopColor)); }).map(e => e.className.toString() || e.tagName)"""

def frame_metrics(page, tag, dev, note=''):
    sw = page.evaluate('[document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth]')
    items = vp_contrast(page)
    s, nov, mn, ncut = summarize(items)
    low = [i for i in items if i['cr'] is not None and not i['off'] and i['cr'] < 4.5]
    minfs = min([i['fs'] for i in items if not i['over']] or [99])
    ov = page.evaluate(OVERLAP_JS)
    shot = page.screenshot(); pts = pixel_points(shot)
    TOT['frames'] += 1; TOT['ov'] += ov['nbad']; TOT['lowc'] += len(low); TOT['minfs'] = min(TOT['minfs'], minfs)
    okw = sw[0] <= sw[2] and sw[1] <= sw[2]
    P(f"  [{tag}] ширина {sw[0]}/{sw[2]} {'OK' if okw else 'ПЛОХО'}; мин.шрифт {minfs:g}px {'OK' if minfs >= 16 else 'ПЛОХО'}; контраст<4.5 (неперекрытые): {len(low)} {[(i['t'], round(i['cr'], 2)) for i in low[:3]]}; мин {mn if mn is None else round(mn, 2)}; перекрыто липкими {nov}; наезд текстов (bbox): {ov['nbad']} из {ov['n']} {ov['bad']}; тёплых пятен {len(pts)}: {pts[:3]} {note}")
    return pts

def run(pw, dev, lang):
    w, h = {'desktop': (1440, 900), 'phone': (390, 844)}[dev]; ph = dev == 'phone'
    br = pw.chromium.launch(args=ARGS)
    ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=ph)
    ctx.add_init_script(INIT)
    page = ctx.new_page(); console = []; ext = []
    page.on('console', lambda m: console.append((m.type, m.text)) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: console.append(('pageerror', str(e))))
    page.on('requestfailed', lambda r: console.append(('reqfail', r.url)))
    page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:')) else None)
    base = 'file://' + os.path.join(HERE, 'index.html')
    def go(q='', url=base, clean=True):
        qq = ('?lang=' + lang + ('&clean=1' if clean else '') + ('&' + q if q else ''))
        page.goto(url + qq); page.evaluate("document.documentElement.style.scrollBehavior='auto'"); page.wait_for_timeout(900)
    def anchor(sec): page.evaluate(f"document.getElementById('{sec}').scrollIntoView()"); page.wait_for_timeout(500)
    def snap(n, name, full=False):
        page.mouse.move(0, 0); page.wait_for_timeout(200)
        page.screenshot(path=os.path.join(SH, f'{PFX}{dev}-{lang}-{n}-{name}-' + ('full' if full else 'view') + '.png'), full_page=full)
    P(f'\n===== {dev} {w}x{h} lang={lang} =====')
    # ---- 1 early / open / live: верх страницы
    for n, st in ((1, 'early'), (2, 'open'), (4, 'live')):
        go('demo=' + st)
        info = page.evaluate("""() => ({say: !!document.querySelector('#say') && !document.querySelector('#say').hidden && getComputedStyle(document.querySelector('#say')).opacity > 0, lumo: document.querySelector('.lumo-wrap').getBoundingClientRect().width, dev: getComputedStyle(document.querySelector('.dev')).display,
          cur: (() => { const e = document.querySelector('.dr.cur'); return e ? Math.round(e.getBoundingClientRect().height) : null })(), nowline: !!document.querySelector('.nowline') })""")
        pts = frame_metrics(page, st + '/верх', dev, f"| Люмо {info['lumo']:g}px; пузырь виден: {info['say']}; .dev display={info['dev']}; высота маркера «цей урок»: {info['cur']}; линия «Зараз»: {info['nowline']}")
        snap(n, st)
        if st == 'live':
            r = page.evaluate("""() => { const t = document.querySelector('.timer').getBoundingClientRect(), b = document.querySelector('.burn').getBoundingClientRect(), f = document.querySelector('.burn i').getBoundingClientRect(); const pb = document.querySelector('.burn');
              return {tw: t.width, bw: b.width, fw: f.width, bl: b.left - t.left, now: pb.getAttribute('aria-valuenow'), vt: pb.getAttribute('aria-valuetext'), pct: document.querySelector('.tpct').textContent, left: document.querySelector('.tnum').textContent.trim()}; }""")
            bs = page.evaluate(BASE_JS)
            P(f"  [П1 таймер] число «{r['left']}»; полоска {r['bw']:.1f}px при ширине блока таймера {r['tw']:.1f}px (равны: {abs(r['bw'] - r['tw']) < 0.6}); заливка {r['fw']:.1f}px = {r['fw'] / r['bw'] * 100:.1f}% (ожидается 12/45 = 26.7%); подпись «{r['pct']}»; aria-valuenow={r['now']} (минуло); aria-valuetext «{r['vt']}»")
            P(f"  [П1 базовая линия] «33» y={bs['num']}, текст кнопки y={bs['btn']}, разница {abs(bs['num'] - bs['btn']):.1f}px {'OK' if abs(bs['num'] - bs['btn']) < 1 else ('n/a на телефоне: кнопка в липкой панели' if ph else 'ПЛОХО')}")
            tl = page.evaluate("""() => { const e = document.querySelector('.tlab'); const tw = document.createTreeWalker(e, NodeFilter.SHOW_TEXT); const t = tw.nextNode(); const r = document.createRange(); r.selectNodeContents(t); return {txt: JSON.stringify(t.textContent), lines: new Set([...r.getClientRects()].map(x => Math.round(x.top))).size}; }""")
            P(f"  [П5 «до кінця уроку»] текст {tl['txt']}; строк {tl['lines']}; пробелы неразрывные: {NBSP_ in json.loads(tl['txt']) and ' до ' not in json.loads(tl['txt'])}")
        if ph and st == 'live':
            hh = page.evaluate("""() => { const b = document.querySelector('#enter').getBoundingClientRect(); const r = document.querySelector('.lesson-card .lc-row'); return {pos: getComputedStyle(r).position, top: Math.round(b.top), h: Math.round(b.height), txt: document.querySelector('#enter').innerText.replace(/\\n/g, ' | ')}; }""")
            P(f"  [П5 липкий вход, телефон] position={hh['pos']}, кнопка y {hh['top']}, высота {hh['h']}px, надпись: «{hh['txt']}»")
        if st == 'open':
            hg = page.evaluate(HANG_JS); TOT['wbad'] += len(hg['bad'])
            P(f"  [П5 висячие слова/«·»] проверено текстов {hg['n']}; найдено {len(hg['bad'])}: {hg['bad'][:5]}")
            if ph:
                nav = page.evaluate("""() => { const n = document.querySelector('#nav'), i = document.querySelector('#navIn'); const cs = getComputedStyle(i); return {fr: n.hasAttribute('data-fr'), fl: n.hasAttribute('data-fl'), mask: (cs.webkitMaskImage || cs.maskImage || '').slice(0, 60), last: (() => { const a = [...i.querySelectorAll('a')].find(a => a.getBoundingClientRect().right > innerWidth - 4); return a ? [a.textContent.trim(), Math.round(a.getBoundingClientRect().left), Math.round(a.getBoundingClientRect().right)] : null })() }; }""")
                P(f"  [П5 вкладки телефона] есть продолжение справа: {nav['fr']}; маска затухания: {nav['mask']!r}; обрезанная вкладка: {nav['last']}")
    # ---- вход нажат
    go('demo=open'); page.click('#enter'); page.wait_for_timeout(500)
    frame_metrics(page, 'вход нажат', dev, f"| пузырь виден: {page.evaluate('!!document.querySelector(`#say`) && !document.querySelector(`#say`).hidden')}"); snap(3, 'entered')
    # ---- неделя / группы / план
    go(); anchor('week'); frame_metrics(page, 'неделя', dev); snap(5, 'week')
    anchor('groups'); frame_metrics(page, 'группы', dev); snap(6, 'groups')
    if ph:
        hg = page.evaluate(HANG_JS); TOT['wbad'] += len(hg['bad']); P(f"  [П5 висячие, группы, телефон] проверено {hg['n']}, найдено {len(hg['bad'])}: {hg['bad'][:5]}")
    anchor('plan'); frame_metrics(page, 'план', dev); snap(7, 'plan')
    # ---- заметки: ошибка
    anchor('notes')
    page.fill('#noteText', 'Call parent +48 600 100 200'); page.click('#noteForm button[type=submit]', force=True); page.wait_for_timeout(1500)
    ef = page.evaluate("""() => { const t = document.querySelector('#noteText'), e = document.querySelector('#noteErr .err'); const cs = getComputedStyle(t), es = e && getComputedStyle(e);
      return {focus: document.activeElement === t, fv: t.matches(':focus-visible'), bad: t.classList.contains('bad'), outline: cs.outlineStyle + ' ' + cs.outlineWidth, border: cs.borderTopWidth + ' ' + cs.borderTopColor, shadow: cs.boxShadow, errBorder: es ? es.borderTopWidth + ' ' + es.borderTopStyle : null, errBg: es ? es.backgroundColor : null}; }""")
    frames = (1 if ef['border'].split()[0] != '0px' else 0) + (1 if not ef['outline'].startswith('none') else 0)
    P(f"  [П5 ошибка: фокус+ошибка] в фокусе {ef['focus']}, focus-visible {ef['fv']}, .bad {ef['bad']}; outline {ef['outline']}; рамка поля {ef['border']}; тень {ef['shadow'][:40]}; рамка блока ошибки {ef['errBorder']}, фон {ef['errBg']} -> рамок вокруг поля: {frames} {'OK' if frames == 1 and ef['errBorder'] and ef['errBorder'].startswith('0px') else 'ПЛОХО'}")
    frame_metrics(page, 'заметки-ошибка', dev); snap(8, 'notes-error')
    # ---- замена
    go(); anchor('swap'); page.wait_for_timeout(300)
    sw0 = page.evaluate("""() => { const nb = document.getElementById('nav').getBoundingClientRect().bottom; const r = document.querySelector('#swapForm .lc-row'); const rr = r.getBoundingClientRect(); const b = document.querySelector('#swapForm button[type=submit]');
      const R = id => { const e = document.querySelector(id); const q = e.getBoundingClientRect(); return [Math.round(q.top), Math.round(q.bottom)]; };
      const dockTop = getComputedStyle(r).position === 'fixed' ? Math.round(rr.top) : innerHeight;
      const sum = document.querySelector('.how-m summary'); const how = [...document.querySelectorAll('.how-wide, .how-m .how')].map(e => e.getBoundingClientRect().height > 0);
      return {nb: Math.round(nb), dockPos: getComputedStyle(r).position, dockTop, btnDisabled: b.getAttribute('aria-disabled'), hint: document.querySelector('#swapHint').textContent, reason: R('#reason'), note: R('#swapNote'), sumTxt: sum ? sum.textContent.trim() : null, sumH: sum ? Math.round(sum.getBoundingClientRect().height) : 0, sumVisible: sum ? sum.getBoundingClientRect().height > 0 : false, howVisible: how, checked: document.querySelectorAll('.opt input:checked').length, secTop: Math.round(document.getElementById('swap').getBoundingClientRect().top), mt: getComputedStyle(document.getElementById('swap')).scrollMarginTop, btnR: (() => { const q = b.getBoundingClientRect(); return [Math.round(q.top), Math.round(q.height)]; })() }; }""")
    inview = lambda r: r[0] >= sw0['nb'] and r[1] <= sw0['dockTop']
    P(f"  [П2 замена, 1-й экран] низ липкой навигации {sw0['nb']}, верх липкой панели {sw0['dockTop']} (position={sw0['dockPos']}); «Причина» y {sw0['reason']} в окне: {inview(sw0['reason'])}; «Коментар» y {sw0['note']} в окне: {inview(sw0['note'])}; кнопка y/высота {sw0['btnR']}; aria-disabled={sw0['btnDisabled']}, подсказка «{sw0['hint']}», выбранных уроков {sw0['checked']}")
    P(f"  [П2 «Як це працює ›»] строка: «{sw0['sumTxt']}» высота {sw0['sumH']}px видна: {sw0['sumVisible']}; три шага видны: {sw0['howVisible']} (телефон: [False, False] — шаги свёрнуты; ноутбук: [True, False])")
    frame_metrics(page, 'замена-пусто', dev); snap(9, 'swap')
    # не отправляется без выбора
    page.click('#swapForm button[type=submit]', force=True); page.wait_for_timeout(300)
    P(f"  [П2 клик по неактивной] запрос отправлен: {page.evaluate('!!document.querySelector(`#swap .sent`)')} (должно False)")
    page.click('.opt:nth-child(2)'); page.wait_for_timeout(200)
    st1 = page.evaluate("[document.querySelector('#swapForm button[type=submit]').getAttribute('aria-disabled'), document.querySelector('#swapHint').textContent]")
    page.select_option('#reason', 'ill'); page.wait_for_timeout(200)
    st2 = page.evaluate("[document.querySelector('#swapForm button[type=submit]').getAttribute('aria-disabled'), document.querySelector('#swapHint').hidden, getComputedStyle(document.querySelector('#swapForm button[type=submit]')).backgroundColor]")
    P(f"  [П2 состояния кнопки] только урок: aria-disabled={st1[0]}, подсказка «{st1[1]}»; урок+причина: aria-disabled={st2[0]}, подсказка скрыта {st2[1]}, фон {st2[2]}")
    frame_metrics(page, 'замена-выбрано', dev); snap(10, 'swap-ready')
    # другая секция: панель замены не должна висеть
    anchor('notes')
    P(f"  [П2 панель «Надіслати» вне раздела] position={page.evaluate('getComputedStyle(document.querySelector(`#swapForm .lc-row`)).position')} на «Нотатки» (фиксирована только на «Заміна»)")
    anchor('swap'); page.click('#swapForm button[type=submit]'); page.wait_for_timeout(400)
    P(f"  [замена] после отправки: {page.evaluate('document.querySelector(`#swap .sent h3`) && document.querySelector(`#swap .sent h3`).textContent')!r}")
    frame_metrics(page, 'замена-отправлена', dev); snap(11, 'swap-sent')
    # ---- scroll-margin: все секции
    go(); rows = []
    for sec in ('today', 'week', 'groups', 'plan', 'notes', 'swap'):
        anchor(sec)
        r = page.evaluate(f"""() => {{ const e = document.getElementById('{sec}'); const nb = document.getElementById('nav').getBoundingClientRect().bottom;
          const orange = [...document.querySelectorAll('.btn-main, .nowdot')].filter(b => {{ const q = b.getBoundingClientRect(); const bg = getComputedStyle(b).backgroundColor; return bg === 'rgb(255, 122, 69)' && q.width > 2 && getComputedStyle(b.closest('.lc-row') || b).position !== 'fixed' && q.bottom > 2 && q.top < nb; }}).map(b => b.textContent.trim().slice(0, 12) || 'dot');
          return [Math.round(e.getBoundingClientRect().top), getComputedStyle(e).scrollMarginTop, orange]; }}""")
        rows.append((sec, *r))
    P('  [П2 scroll-margin-top] ' + '; '.join(f"{s}: margin {m}, верх секции y={t}{'' if s != 'today' else ' (у верха страницы — упирается в 0)'}" for s, t, m, o in rows))
    P(f"  [П2 оранжевое под навигацией] торчащих оранжевых кнопок/точек из-под липкой навигации: {sum(len(o) for *_, o in rows)} {[(s, o) for s, t, m, o in rows if o]}")
    # ---- пузырь один раз, переключатели (без clean)
    go('demo=open', clean=False)
    a = page.evaluate("[!!document.querySelector('#say .say-x'), document.querySelector('#say').hidden]")
    page.click('[data-demo=live]') if page.is_visible('[data-demo=live]') else None
    page.wait_for_timeout(200)
    if not ph:
        page.click('[data-tz=kyiv]'); page.wait_for_timeout(200)
    b = page.evaluate("[document.querySelector('#say').hidden, document.querySelector('#say').textContent.trim().length]")
    P(f"  [П4 пузырь один раз] при открытии показан: {not a[1]} (крестик {a[0]}); после переключения времени/пояса скрыт: {b[0]} (текст {b[1]} симв.)")
    P(f"  [П5 служебный язычок] без clean: .dev display={page.evaluate('getComputedStyle(document.querySelector(`.dev`)).display')}; с ?clean=1 — см. «.dev display» в строках верха")
    if not ph:
        go('demo=live'); sh0 = page.evaluate("document.querySelector('.lesson-card').getBoundingClientRect().height")
        page.evaluate('window.__cls = 0'); page.wait_for_timeout(10500)
        r = page.evaluate("[getComputedStyle(document.querySelector('#say')).opacity, document.querySelector('.lesson-card').getBoundingClientRect().height, window.__cls]")
        P(f"  [П4 пузырь гаснет сам через 9 с, ноутбук] opacity {r[0]}; высота карточки до/после {sh0:.0f}/{r[1]:.0f}px (зсува нет: {abs(sh0 - r[1]) < 1}); CLS за время гашения {r[2]:.4f}")
    # ---- меню телефона
    if ph:
        go('demo=open', clean=True); page.click('#avatarBtn'); page.wait_for_timeout(300)
        P(f"  [меню телефона, clean] «Стан прототипу» в меню виден: {page.evaluate('document.querySelector(`.dev`) && getComputedStyle(document.querySelector(`.dev`)).display !== `none`')}")
        frame_metrics(page, 'меню', dev); snap(12, 'menu')
    cls = page.evaluate('window.__cls'); TOT['cls'].append((dev, lang, round(cls, 4))); TOT['console'] += len(console); TOT['ext'] += len(ext)
    P(f"  CLS за сценарий {cls:.4f}; источники: {str(page.evaluate('window.__src||[]'))[:300]}; консоль {len(console)} {console[:3]}; внешние запросы {len(ext)} {ext[:3]}")
    hits = re.findall(r'@|\+\d{2,}|https?:|\b\d{3}[ -]\d{3}[ -]\d{3}\b', page.evaluate('document.body.innerText'))
    P(f"  контакты в видимом тексте: {hits}")
    br.close()

def before_after(pw):
    P('\n===== ДО/ПОСЛЕ (круг 10 против круга 11) =====')
    br = pw.chromium.launch(args=ARGS)
    for dev, (w, h) in (('desktop', (1440, 900)), ('phone', (390, 844))):
        for name, url in (('r10', OLD), ('r13', 'file://' + os.path.join(HERE, 'index.html'))):
            ctx = br.new_context(viewport={'width': w, 'height': h}); page = ctx.new_page()
            page.goto(url + '?demo=live&clean=1'); page.wait_for_timeout(800)
            b = page.evaluate(BORDERS_JS)
            hg = page.evaluate(HANG_JS)
            # расширенный DOM: все секции отрисованы -> меряем всю страницу
            lm = page.evaluate("[document.querySelector('.lumo-wrap').getBoundingClientRect().width, getComputedStyle(document.querySelector('.lumo')).filter]")
            P(f"  {dev} {name}: элементов с видимой рамкой на странице {b['n']} (топ: {b['top'][:5]}); Люмо {lm[0]:g}px, filter {lm[1][:60]}; висячих (live, верх страницы) {len(hg['bad'])} {hg['bad'][:3]}")
            if name == 'r10': b10 = b['n']
            else: P(f"    -> рамок {b10} -> {b['n']} ({(1 - b['n'] / b10) * 100:.0f}% убрано)")
            ctx.close()
    # двойная рамка в ошибке: до
    for name, url in (('r10', OLD), ('r13', 'file://' + os.path.join(HERE, 'index.html'))):
        ctx = br.new_context(viewport={'width': 1440, 'height': 900}); page = ctx.new_page()
        page.goto(url + '?clean=1'); page.wait_for_timeout(700)
        page.fill('#noteText', 'Call parent +48 600 100 200'); page.click('#noteForm button[type=submit]', force=True); page.wait_for_timeout(1500)
        e = page.evaluate("""() => { const t = document.querySelector('#noteText'), er = document.querySelector('#noteErr .err'); const c = getComputedStyle(t), s = getComputedStyle(er); return [c.outlineStyle + ' ' + c.outlineWidth, c.borderTopWidth, s.borderTopWidth]; }""")
        P(f"  ошибка заметки {name}: outline поля {e[0]}, рамка поля {e[1]}, рамка блока ошибки {e[2]}")
        ctx.close()
    # размер пламени и «второе пятно»
    for dev, (w, h) in (('desktop', (1440, 900)), ('phone', (390, 844))):
        ctx = br.new_context(viewport={'width': w, 'height': h}); page = ctx.new_page(); page.goto('file://' + os.path.join(HERE, 'index.html') + '?demo=live&clean=1'); page.wait_for_timeout(900)
        page.evaluate("document.querySelectorAll('.lumo-wrap, .lumo').forEach(e => e.style.animation='none')")
        btn = page.evaluate("(() => { const b = document.querySelector('#enter').getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height), Math.round(b.width * b.height)] })()")
        lw = page.evaluate("(() => { const b = document.querySelector('.lumo path').getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height)] })()")
        pts = pixel_points(page.screenshot())
        P(f"  {dev}: кнопка входа {btn[0]}x{btn[1]} = {btn[2]} px²; пламя (path) {lw[0]}x{lw[1]}; тёплые компоненты по пикселям (площадь тёплых px, bbox): {pts[:4]}")
        ctx.close()
    br.close()

BA = len(sys.argv) > 1 and sys.argv[1] == 'ba'
DEVS = () if BA else (('desktop', 'phone') if len(sys.argv) < 2 else (sys.argv[1],))
LANGS = ('uk', 'en') if len(sys.argv) < 3 else (sys.argv[2],)
with sync_playwright() as pw:
    for dev in DEVS:
        for lang in LANGS:
            run(pw, dev, lang)
    if BA or len(sys.argv) < 2: before_after(pw)
P(f"\n== ИТОГО ==\nкадров с метриками {TOT['frames']}; наезды текстов {TOT['ov']}; контраст<4.5 {TOT['lowc']}; мин.шрифт {TOT['minfs']:g}; висячих слов/«·» {TOT['wbad']}; CLS по прогонам {TOT['cls']}; консоль {TOT['console']}; внешние запросы {TOT['ext']}")
open(os.path.join(SH, 'metrics-r13.txt' if len(sys.argv) < 2 else 'metrics-r13-part-%s.txt' % '-'.join(sys.argv[1:])), 'w').write('\n'.join(out) + '\n')
