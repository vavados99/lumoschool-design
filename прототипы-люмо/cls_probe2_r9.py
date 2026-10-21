import os, sys
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(H, 'В6-преподаватель', 'index.html')
INIT = "window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});"
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--disable-lcd-text'])
    for mode in ('none', 'full', 'scroll'):
        ctx = br.new_context(viewport={'width': 390, 'height': 844}, has_touch=True); ctx.add_init_script(INIT)
        p = ctx.new_page(); p.goto(URL); p.wait_for_timeout(1000)
        a = p.evaluate('window.__cls')
        if mode == 'full': p.screenshot(path='/root/.hermes/cache/scratch/x.png', full_page=True)
        if mode == 'scroll':
            for y in (300, 900, 1800, 0): p.evaluate(f'scrollTo(0,{y})'); p.wait_for_timeout(300)
        p.wait_for_timeout(500)
        print(mode, a, p.evaluate('window.__cls'))
        ctx.close()
