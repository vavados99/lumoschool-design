"""Круг 9: проба CLS при загрузке (10 раз) + источники сдвигов. Запуск: venv python cls_probe_r9.py [В6|В5] [phone|desktop]"""
import os, sys, json
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__))
app = sys.argv[1] if len(sys.argv) > 1 else 'В6'
dev = sys.argv[2] if len(sys.argv) > 2 else 'phone'
path = {'В6': 'В6-преподаватель', 'В5': 'В5-родитель'}[app]
URL = 'file://' + os.path.join(H, path, 'index.html')
VP = {'phone': (390, 844), 'desktop': (1440, 900)}[dev]
INIT = """window.__cls=0; window.__src=[];
new PerformanceObserver(l=>{for(const e of l.getEntries()){ if(e.hadRecentInput) continue; window.__cls+=e.value;
 window.__src.push({v:+e.value.toFixed(4), t:Math.round(e.startTime), s:(e.sources||[]).map(s=>{const n=s.node; return (n? (n.nodeName+(n.id?'#'+n.id:'')+(n.className&&n.className.baseVal===undefined?'.'+String(n.className).split(' ')[0]:'')):'?')+' '+JSON.stringify([s.previousRect.y|0,s.previousRect.height|0])+'->'+JSON.stringify([s.currentRect.y|0,s.currentRect.height|0])})});}
}).observe({type:'layout-shift',buffered:true});"""
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--disable-lcd-text'])
    res = []
    for i in range(10):
        ctx = br.new_context(viewport={'width': VP[0], 'height': VP[1]}, has_touch=dev == 'phone')
        ctx.add_init_script(INIT)
        p = ctx.new_page(); p.goto(URL); p.wait_for_timeout(1500)
        # прокрутка вниз-вверх не входит: меряем только загрузку
        res.append((p.evaluate('window.__cls'), p.evaluate('window.__src')))
        ctx.close()
    br.close()
for c, s in res: print(f'{c:.4f}', s if c > 0 else '')
print('макс', max(r[0] for r in res), 'сред', sum(r[0] for r in res) / len(res))
