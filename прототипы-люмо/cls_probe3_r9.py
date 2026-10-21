import os, sys
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(H, 'В6-преподаватель', 'index.html')
INIT = """window.__cls=0;window.__src=[];new PerformanceObserver(l=>{for(const e of l.getEntries()){window.__src.push([+e.value.toFixed(4),Math.round(e.startTime),e.hadRecentInput,e.sources.map(s=>s.node&&(s.node.nodeName+'.'+(s.node.className&&s.node.className.baseVal===undefined?s.node.className:''))+JSON.stringify([s.previousRect.y|0,s.previousRect.height|0,s.currentRect.y|0,s.currentRect.height|0]))]); if(!e.hadRecentInput) window.__cls+=e.value}}).observe({type:'layout-shift',buffered:true});"""
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--disable-lcd-text'])
    for w, h, ph in ((390, 844, True), (1440, 900, False)):
        ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=ph); ctx.add_init_script(INIT)
        p = ctx.new_page(); p.goto(URL); p.wait_for_timeout(1000)
        p.evaluate("document.documentElement.style.scrollBehavior='auto'")
        p.click('#nav a[data-sec=swap]'); p.wait_for_timeout(900)
        p.fill('#swapNote', 'write me t.me/abc'); p.click('#swapForm button[type=submit]', force=True); p.wait_for_timeout(1300)
        print(w, p.evaluate('window.__cls'), p.evaluate('window.__src'))
        print('errbox h', p.evaluate("document.querySelector('#swapErr').getBoundingClientRect().height"))
        ctx.close()
