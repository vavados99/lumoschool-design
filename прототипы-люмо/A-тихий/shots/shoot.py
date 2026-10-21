import asyncio, json, os
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__)); URL='file://'+os.path.dirname(D)+'/index.html'
async def run(p, name, vp, mobile):
    b=await p.chromium.launch()
    ctx=await b.new_context(viewport=vp, device_scale_factor=2, is_mobile=mobile, has_touch=mobile)
    pg=await ctx.new_page(); errs=[]
    pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.on('pageerror',lambda e: errs.append(str(e)))
    await pg.goto(URL); await pg.wait_for_load_state('networkidle'); await pg.wait_for_timeout(3200)
    if not mobile: await pg.mouse.move(300,700); await pg.wait_for_timeout(500)
    await pg.screenshot(path=f'{D}/{name}.png')
    box=await pg.evaluate("(()=>{const r=document.getElementById('lumo').getBoundingClientRect();return [r.left+r.width*.5,r.top+r.height*.5]})()")
    if mobile: await pg.touchscreen.tap(*box)
    else:
        await pg.mouse.move(box[0]-200,box[1]); await pg.mouse.move(*box,steps=8)
    await pg.wait_for_timeout(350)
    await pg.screenshot(path=f'{D}/reaction-{name}-hover.png' if not mobile else f'{D}/reaction-{name}-tap.png')
    if not mobile:
        await pg.mouse.down(); await pg.mouse.up(); await pg.wait_for_timeout(300)
        await pg.screenshot(path=f'{D}/reaction-{name}-click.png')
    await pg.wait_for_timeout(5000)
    await pg.evaluate("window.scrollTo(0, document.getElementById('steps').getBoundingClientRect().top+scrollY-innerHeight*0.3)")
    await pg.wait_for_timeout(1500)
    await pg.screenshot(path=f'{D}/{name}-lesson.png')
    m=await pg.evaluate("""(()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,
      imgs:[...document.images].map(i=>[i.src.split('/').pop(),i.complete&&i.naturalWidth>0]),
      small:[...document.querySelectorAll('h1,p,a,button,span,b,h2,h3')].filter(e=>e.offsetParent&&e.textContent.trim()&&e.children.length==0&&parseFloat(getComputedStyle(e).fontSize)<16).map(e=>e.textContent.slice(0,20)),
      fonts:[...document.fonts].filter(f=>f.status=='loaded').map(f=>f.family+f.style)}))()""")
    m['errors']=errs; print(name,json.dumps(m,ensure_ascii=False))
    await b.close()
async def main():
    async with async_playwright() as p:
        await run(p,'desktop',{'width':1440,'height':900},False)
        await run(p,'mobile',{'width':390,'height':844},True)
asyncio.run(main())
