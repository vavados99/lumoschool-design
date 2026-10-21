import asyncio, json, time
from pathlib import Path
from playwright.async_api import async_playwright
OUT = Path("/root/projects/english-school/визуалы/референсы")

async def shoot(browser, name, url, waits, scroll):
    ctx = await browser.new_context(viewport={"width":1512,"height":830}, locale="en-US",
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")
    page = await ctx.new_page()
    res = {"name":name}
    try:
        r = await page.goto(url, wait_until="domcontentloaded", timeout=40000)
        res["status"] = r.status if r else None
        t = 0
        for i, w in enumerate(waits):
            await page.wait_for_timeout(w*1000)
            t += w
            await page.screenshot(path=str(OUT/f"{name}-t{t}s.png"), timeout=60000)
        for j, s in enumerate(scroll):
            await page.mouse.wheel(0, s)
            await page.wait_for_timeout(2500)
            await page.screenshot(path=str(OUT/f"{name}-s{j+1}.png"), timeout=60000)
        res["ok"] = True
        res["title"] = await page.title()
    except Exception as e:
        res["ok"] = False; res["error"] = str(e)[:160]
    await ctx.close()
    print(json.dumps(res, ensure_ascii=False), flush=True)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--disable-gpu","--no-sandbox","--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        await shoot(b, "whyzero", "https://why.zero.university", [6,8,10], [1000, 1000])
        await shoot(b, "figma", "https://www.figma.com", [5], [])
        await b.close()
    print("ГОТОВО-RETRY", flush=True)
asyncio.run(main())
