import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright
BASE = Path("/root/projects/english-school/визуалы/направления")
DIRS = ["1-призма","2-вирізка","3-метро","4-ефір","5-вихор"]
FONTS = ["600 20px Unbounded","800 20px Onest","500 14px 'JetBrains Mono'","900 20px 'Playfair Display'"]
TEST = "Привіт ґєії Cześć ąćęłńóśźż Ahoj ěščřžůďťň Hallo äöüß"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox","--disable-gpu"])
        for d in DIRS:
            ctx = await b.new_context(viewport={"width":1512,"height":830}, locale="uk-UA")
            page = await ctx.new_page()
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)[:150]))
            page.on("console", lambda m: errs.append("console:"+m.text[:120]) if m.type=="error" else None)
            await page.goto((BASE/d/"index.html").as_uri(), wait_until="load", timeout=60000)
            try: await page.wait_for_load_state("networkidle", timeout=15000)
            except Exception: pass
            await page.evaluate("document.fonts.ready")
            await page.wait_for_timeout(2500)
            fonts = await page.evaluate("(a)=>a[0].map(f=>[f,document.fonts.check(f,a[1])])", [FONTS, TEST])
            dims = await page.evaluate("({sw:document.documentElement.scrollWidth,sh:document.documentElement.scrollHeight})")
            out = BASE/f"{d}.png"
            await page.screenshot(path=str(out), full_page=True)
            print(d, json.dumps({"fonts":fonts,"dims":dims,"errors":errs[:4]}, ensure_ascii=False), flush=True)
            await ctx.close()
        await b.close()
asyncio.run(main())
