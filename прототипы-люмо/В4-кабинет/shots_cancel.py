"""Кадры и замеры диалога отмены В4. Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_cancel.py"""
import os, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(HERE, 'index.html')
SH = os.path.join(HERE, 'shots'); os.makedirs(SH, exist_ok=True)
DEV = {'desktop': (1440, 900), 'phone': (390, 844)}
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)
INFO = """() => { const a = document.activeElement; const r = e => { const b = e.getBoundingClientRect(); return [Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height)]; };
  const keep = document.querySelector('[data-keep]'), yes = document.querySelector('[data-yes]'), dlg = document.querySelector('.bk-ask');
  const cs = e => { const c = getComputedStyle(e); return {bg: c.backgroundColor, color: c.color, border: c.borderTopColor, fs: c.fontSize}; };
  return {focus: a.textContent.trim(), focusIsKeep: a === keep, bookings: document.querySelectorAll('.bk').length,
    keep: keep && {rect: r(keep), ...cs(keep)}, yes: yes && {rect: r(yes), ...cs(yes)}, dlg: dlg && r(dlg),
    note: document.querySelector('#askN')?.textContent, emo: document.querySelector('#page').dataset.emo,
    sw: [document.documentElement.scrollWidth, innerWidth], inView: dlg ? (dlg.getBoundingClientRect().bottom <= innerHeight + 1 && dlg.getBoundingClientRect().top >= 0) : null}; }"""
INIT = "window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});"
with sync_playwright() as pw:
    for dev, (w, h) in DEV.items():
        for lang in ('uk', 'en'):
            br = pw.chromium.launch()
            ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=(dev == 'phone'))
            ctx.add_init_script(INIT)
            pg = ctx.new_page(); con = []
            pg.on('console', lambda m: con.append(m.text) if m.type in ('error', 'warning') else None)
            pg.on('pageerror', lambda e: con.append(str(e)))
            pg.goto(URL); pg.wait_for_timeout(600)
            if lang == 'en': pg.click('[data-lang=en]'); pg.wait_for_timeout(200)
            P(f'== {dev} {w}x{h} {lang} ==')
            pg.locator('[data-cancel]:not([disabled])').first.scroll_into_view_if_needed()
            pg.click('[data-cancel]:not([disabled])'); pg.wait_for_timeout(700)
            info = pg.evaluate(INFO)
            P(' диалог открыт:', json.dumps(info, ensure_ascii=False))
            pg.screenshot(path=f'{SH}/cancel-{dev}-{lang}-1-dialog.png')  # видимая область
            # Enter по умолчанию
            pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
            after = pg.evaluate("() => ({bookings: document.querySelectorAll('.bk').length, dialog: !!document.querySelector('.bk-ask'), focus: document.activeElement.textContent.trim()})")
            P(' после Enter:', after)
            pg.screenshot(path=f'{SH}/cancel-{dev}-{lang}-2-after-enter.png')
            # Escape тоже оставляет
            pg.click('[data-cancel]:not([disabled])'); pg.wait_for_timeout(300); pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
            P(' после Escape: броней', pg.evaluate("() => document.querySelectorAll('.bk').length"), 'диалог', pg.evaluate("() => !!document.querySelector('.bk-ask')"))
            # Tab: от «Залишити» вперёд -> «Скасувати»; явное «Скасувати» работает
            pg.click('[data-cancel]:not([disabled])'); pg.wait_for_timeout(300); pg.keyboard.press('Tab')
            P(' Tab с «Залишити» ->', pg.evaluate("() => document.activeElement.textContent.trim()"))
            pg.click('[data-yes]'); pg.wait_for_timeout(500)
            P(' явный клик «Скасувати»: броней', pg.evaluate("() => document.querySelectorAll('.bk').length"))
            P(f' CLS {pg.evaluate("() => window.__cls"):.4f}; ошибок консоли {len(con)} {con[:3]}')
            br.close()
open(os.path.join(SH, 'cancel-metrics.txt'), 'w').write('\n'.join(out) + '\n')
