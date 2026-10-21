"""В8 ч.2: Викладачі / Для батьків / Вхід — кадры + замеры -> shots2/*.png, ../замеры-В8-часть2.txt
Запуск: /usr/local/lib/hermes-agent/venv/bin/python shots_run2.py [desktop|phone]   (chromium --disable-lcd-text)
Хелперы (контраст по пикселям, тёплые точки, CLS-обсервер) берутся из shots_run.py (часть 1) — выполняется только его «шапка» до def run."""
import os, io, sys
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, 'shots_run.py'), encoding='utf-8').read()
exec(compile(_src[:_src.index('def run(pw, dev, lang):')], 'shots_run_head', 'exec'), globals())
SH = os.path.join(HERE, 'shots2'); os.makedirs(SH, exist_ok=True)
out.clear()
BASE = 'file://' + HERE + '/'
RES = []  # сводка для итоговых чисел

def run(pw, dev, lang):
    w, h = DEV[dev]
    br = pw.chromium.launch(args=['--disable-lcd-text'])
    P(f'\n===== {dev} {w}x{h} · {lang} =====')
    sfx = '?lang=en' if lang == 'en' else ''
    for pg in ('teachers', 'parents', 'login'):
        ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
        page = ctx.new_page(); console = []; ext = []
        page.on('console', lambda m: console.append(m.text) if m.type in ('error', 'warning') else None)
        page.on('pageerror', lambda e: console.append('pageerror ' + str(e)))
        page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file://', 'data:', 'blob:')) else None)
        page.add_init_script(INIT)
        page.goto(BASE + pg + '.html' + sfx); page.wait_for_timeout(700)
        pre = f'{dev}-{lang}-{pg}-'
        P(f'--- страница {pg} ---')
        def frame(name, full=False):
            page.wait_for_timeout(250)
            page.screenshot(path=os.path.join(SH, f'{pre}{name}.png'), full_page=full)
            wd = page.evaluate("[document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth]")
            ok = wd[0] == wd[2] and wd[1] <= wd[2]
            P(f'[{pg}/{name}] ширина html {wd[0]} / body {wd[1]} vs окно {wd[2]} -> {"OK" if ok else "ПЛОХО"}')
            ovf = page.evaluate("""() => [...document.querySelectorAll('main *, header *')].filter(e => { if (e.closest('[aria-hidden=true],[hidden],.vh')) return false; const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && cs.visibility !== 'hidden' && (r.right > innerWidth + 0.5 || r.left < -0.5); }).map(e => e.tagName + '.' + (e.className || e.id)).slice(0, 5)""")
            P(f'  элементов за краем окна: {len(ovf)} {ovf} -> {"OK" if not ovf else "ПЛОХО"}')
            mn, c = vp_metrics(page, name)
            dots = warm_dots(page.screenshot())
            P(f'  тёплые точки в окне: {dots} {"OK (≤4)" if dots <= 4 else "ПЛОХО"}')
            RES.append((dev, lang, pg, name, ok and not ovf, mn, c, dots))
        def btn(sel):
            r = page.evaluate("(s)=>{const e=document.querySelector(s); if(!e) return null; const b=e.getBoundingClientRect(); return [Math.round(b.top),Math.round(b.bottom),Math.round(b.height)]}", sel)
            if not r: P(f'  кнопка {sel}: нет'); return
            P(f'  кнопка {sel}: top {r[0]} bottom {r[1]} h {r[2]} при окне {h} -> {"в окне" if r[1] <= h and r[0] >= 0 else "НИЖЕ СГИБА"}')
        def height(): P(f'  высота страницы {page.evaluate("document.documentElement.scrollHeight")} px')
        def txt(sel): return page.evaluate("(s)=>{const e=document.querySelector(s);return e?e.textContent.trim().slice(0,90):null}", sel)

        if pg == 'teachers':
            frame('01-all'); height(); btn('#topCta'); btn('.cta-end .btn.primary')
            P(f'  [строк преподавателей] {page.evaluate("document.querySelectorAll(`.tr`).length")}; фото (img в списке): {page.evaluate("document.querySelectorAll(`.roster img`).length")}; ссылок tel:/mailto:/@ в тексте: {page.evaluate("(document.body.innerText.match(/@|tel:|mailto:/g)||[]).length + document.querySelectorAll(`a[href^=tel],a[href^=mailto]`).length")}')
            page.click('[data-f=exam]'); page.wait_for_timeout(200)
            P(f'  [фильтр «Іспити»] видимых строк: {page.evaluate("document.querySelectorAll(`.tr:not([hidden])`).length")} (ожидаем 1); счётчик: {txt("#count")!r}')
            frame('02-filter-exam')
            page.click('[data-f=adults]'); page.wait_for_timeout(200)
            P(f'  [фильтр «Дорослі»] видимых строк: {page.evaluate("document.querySelectorAll(`.tr:not([hidden])`).length")} (ожидаем 2)')
            page.click('[data-f=all]'); page.wait_for_timeout(200)
            page.screenshot(path=os.path.join(SH, f'{pre}03-fullpage.png'), full_page=True)
        elif pg == 'parents':
            frame('01-start'); height(); btn('#topCta')
            pass
            page.click('[data-room=school]'); page.wait_for_timeout(150)
            page.evaluate("document.querySelector('#two').scrollIntoView()"); page.wait_for_timeout(200)
            P(f'  [два взрослых → школа] третья карточка: {page.evaluate("document.querySelectorAll(`.node b`)[2].textContent")!r}')
            frame('02-two-adults-school')
            page.evaluate("document.querySelector('#rec').scrollIntoView()"); page.wait_for_timeout(200)
            P(f'  [запись] по умолчанию switch aria-checked={page.get_attribute("#recSw","aria-checked")} (ожидаем false)')
            frame('03-recording-off')
            page.click('#recSw'); page.wait_for_timeout(200)
            P(f'  [запись] после клика без согласия: switch={page.get_attribute("#recSw","aria-checked")} (ожидаем false), панель согласия открыта: {page.evaluate("!document.querySelector(`#confirm`).hidden")}')
            page.click('#recGo'); page.wait_for_timeout(200)
            P(f'  [запись] «Увімкнути» без галочки: switch={page.get_attribute("#recSw","aria-checked")} (ожидаем false)')
            frame('04-recording-ask')
            page.check('#recOk', force=True); page.click('#recGo'); page.wait_for_timeout(200)
            P(f'  [запись] с галочкой: switch={page.get_attribute("#recSw","aria-checked")} (ожидаем true), метка «идёт запись»: {page.evaluate("!!document.querySelector(`.live`)")}')
            frame('05-recording-on')
            page.click('#recSw'); page.wait_for_timeout(150)
            P(f'  [запись] выключение одним кликом: switch={page.get_attribute("#recSw","aria-checked")} (ожидаем false)')
            page.evaluate("scrollTo(0,0)")
            page.keyboard.press('Tab')
            page.screenshot(path=os.path.join(SH, f'{pre}06-fullpage.png'), full_page=True)
        else:
            frame('01-email'); height(); btn('#go')
            P(f'  [вкладки способов] {page.evaluate("document.querySelectorAll(`[data-m]`).length")} (ожидаем 3)')
            page.click('#go'); page.wait_for_timeout(250)
            P(f'  [ошибка email] ошибок {page.evaluate("document.querySelectorAll(`.fe`).length")}; aria-invalid {page.evaluate("document.querySelectorAll(`[aria-invalid]`).length")}; фокус: {page.evaluate("document.activeElement.id")!r}')
            frame('02-email-error'); btn('#go')
            page.fill('#email', 'anna.example@example.com'); page.click('#go'); page.wait_for_timeout(250)
            P(f'  [email ok] заголовок: {txt("#h1")!r}')
            frame('03-email-sent')
            page.click('#fakeLink'); page.wait_for_timeout(200); P(f'  [ссылка из письма] {txt("#h1")!r}')
            page.click('#again'); page.wait_for_timeout(150)
            page.click('[data-m=pw]'); page.wait_for_timeout(200)
            page.fill('#email', 'anna'); page.fill('#pw', '123'); page.click('#go'); page.wait_for_timeout(250)
            P(f'  [пароль: плохие данные] ошибок {page.evaluate("document.querySelectorAll(`.fe`).length")} (ожидаем 2); сводка: {page.evaluate("!!document.querySelector(`#errsum`)")}')
            frame('04-password-error'); btn('#go')
            page.fill('#email', 'anna.example@example.com'); page.fill('#pw', 'demo-pass-1'); page.click('#showPw'); page.wait_for_timeout(150)
            P(f'  [показать пароль] type={page.get_attribute("#pw","type")} (ожидаем text), значение сохранилось: {page.input_value("#pw")!r}')
            frame('05-password-shown')
            page.click('#go'); page.wait_for_timeout(250); P(f'  [вход паролем] {txt("#body h2")!r}')
            page.click('#again'); page.wait_for_timeout(150)
            page.click('[data-m=code]'); page.wait_for_timeout(200)
            frame('06-code'); btn('#go')
            page.fill('#code', 'lumo-0000'); page.click('#go'); page.wait_for_timeout(250)
            P(f'  [код неверный] ошибок {page.evaluate("document.querySelectorAll(`.fe`).length")}; текст: {txt(".fe")!r}')
            frame('07-code-error'); btn('#go')
            page.fill('#code', 'lumo-7k4q'); page.click('#go'); page.wait_for_timeout(250)
            P(f'  [код верный (регистр не важен)] {txt("#body h2")!r}')
            frame('08-code-ok-child')
            page.click('#again'); page.wait_for_timeout(150)
            page.click('[data-mode=up]'); page.wait_for_timeout(200)
            P(f'  [регистрация + код] {txt("#body h2")!r} (ожидаем «ребёнок не регистрируется сам»)')
            frame('09-signup-code-explain')
            page.click('[data-m=pw]'); page.wait_for_timeout(200)
            page.fill('#email', 'anna.example@example.com'); page.fill('#pw', 'demo-pass-1'); page.fill('#pw2', 'other-pass-2'); page.click('#go'); page.wait_for_timeout(250)
            P(f'  [регистрация: пароли не совпали, нет галочки 16+] ошибок {page.evaluate("document.querySelectorAll(`.fe`).length")} (ожидаем 2)')
            frame('10-signup-errors'); btn('#go')
            # клавиатура
            bad = []
            page.evaluate("document.activeElement.blur(); scrollTo(0,0)")
            for _ in range(12):
                page.keyboard.press('Tab')
                r = page.evaluate("(()=>{const e=document.activeElement;if(!e||e===document.body)return null;const c=getComputedStyle(e);return [(e.textContent.trim().slice(0,18)||e.id), e.matches(':focus-visible'), c.outlineStyle, parseFloat(c.outlineWidth)]})()")
                if r and (not r[1] or r[2] == 'none' or r[3] < 2): bad.append(r)
            P(f'  [клавиатура: 12 Tab] без видимого фокуса: {len(bad)} {bad}')
        # общие проверки страницы
        small = page.evaluate("[...document.querySelectorAll('button,a,input:not([type=hidden]),select')].filter(e=>{const b=e.getBoundingClientRect(); return b.width>0&&(b.height<44)&&!e.closest('[hidden]')&&!(e.matches('input[type=checkbox],input[type=radio]'))&&e.className!=='skip'}).map(e=>e.tagName+':'+(e.textContent.trim().slice(0,14))+' '+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height))")
        P(f'  [цели касания <44 px высотой] {len(small)} {small[:6]}')
        cls = page.evaluate('window.__cls'); P('  CLS источники: ' + str(page.evaluate('window.__src||[]'))[:300])
        P(f'  CLS: {cls:.4f}; ошибки/предупреждения консоли: {len(console)} {console[:3]}; внешние запросы: {len(ext)} {ext[:3]}')
        RES.append((dev, lang, pg, 'TOTAL', cls, len(console), len(ext), 0))
        ctx.close()
    br.close()

with sync_playwright() as pw:
    devs = ('desktop', 'phone') if len(sys.argv) < 2 else (sys.argv[1],)
    for d in devs:
        for l in ('uk', 'en'):
            run(pw, d, l)

P('\n== ИТОГ ==')
fr = [r for r in RES if r[3] != 'TOTAL']; tot = [r for r in RES if r[3] == 'TOTAL']
P(f'кадров с метриками: {len(fr)}; ширина/края не OK: {sum(1 for r in fr if not r[4])}')
P(f'мин. шрифт по всем кадрам: {min(r[5] for r in fr):.0f} px; мин. контраст текстов по пикселям: {min(r[6] for r in fr):.2f}:1; макс. тёплых точек в окне: {max(r[7] for r in fr)}')
P(f'макс. CLS: {max(r[4] for r in tot):.4f}; ошибок консоли всего: {sum(r[5] for r in tot)}; внешних запросов всего: {sum(r[6] for r in tot)}')
open(os.path.join(HERE, '..', 'замеры-В8-часть2.txt'), 'w').write(
    'ЗАМЕРЫ В8 ЧАСТЬ 2 (19.10.2026): Викладачі / Для батьків / Вхід. Chromium --disable-lcd-text; Playwright через venv hermes-agent; ноутбук 1440x900, телефон 390x844; uk и en. Скрипт: В8-публичные/shots_run2.py\n' + '\n'.join(out) + '\n')
