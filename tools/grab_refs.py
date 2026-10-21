import asyncio, json, re, sys, time
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path("/root/projects/english-school/визуалы/референсы")
OUT.mkdir(parents=True, exist_ok=True)

SITES = [
    ("speak", "https://www.speak.com"),
    ("duolingo", "https://www.duolingo.com"),
    ("preply", "https://preply.com/en"),
    ("lingoda", "https://www.lingoda.com/en"),
    ("babbel", "https://www.babbel.com"),
    ("praktika", "https://praktika.ai"),
    ("italki", "https://www.italki.com/en"),
    ("brilliant", "https://brilliant.org"),
    ("whyzero", "https://why.zero.university"),
    ("sit-campus", "https://www.singaporetech.edu.sg/openhouse/virtual-campus-tour"),
    ("westbourne", "https://www.westbournegrammar.com"),
    ("awwwards-masterclass", "https://awwwards.com/masterclasses"),
    ("linear", "https://linear.app"),
    ("stripe", "https://stripe.com"),
    ("cal", "https://cal.com"),
    ("raycast", "https://www.raycast.com"),
    ("tldraw", "https://tldraw.com"),
    ("notion", "https://www.notion.com"),
    ("masterclass", "https://www.masterclass.com"),
    ("busuu", "https://www.busuu.com/en"),
    ("cambly", "https://www.cambly.com/english"),
    ("memrise", "https://www.memrise.com"),
]

ACCEPT = re.compile(r"^(accept all|accept|allow all|agree|i agree|got it|ok|okay|принять|согласен)", re.I)

async def one(browser, idx, name, url, log):
    rec = {"n": idx, "name": name, "url": url}
    ctx = await browser.new_context(viewport={"width": 1512, "height": 830}, locale="en-US",
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")
    page = await ctx.new_page()
    t0 = time.time()
    try:
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        rec["status"] = resp.status if resp else None
        try:
            await page.wait_for_load_state("networkidle", timeout=12000)
        except Exception:
            pass
        await page.wait_for_timeout(2500)
        try:
            for b in await page.get_by_role("button").all():
                try:
                    txt = (await b.inner_text(timeout=300)).strip()
                except Exception:
                    continue
                if ACCEPT.match(txt):
                    await b.click(timeout=1500)
                    await page.wait_for_timeout(800)
                    break
        except Exception:
            pass
        rec["title"] = await page.title()
        await page.screenshot(path=str(OUT / f"{idx:02d}-{name}-a.png"))
        await page.mouse.wheel(0, 900)
        await page.wait_for_timeout(1800)
        await page.screenshot(path=str(OUT / f"{idx:02d}-{name}-b.png"))
        rec["ok"] = True
    except Exception as e:
        rec["ok"] = False
        rec["error"] = str(e)[:160]
    rec["sec"] = round(time.time() - t0, 1)
    await ctx.close()
    log.append(rec)
    print(json.dumps(rec, ensure_ascii=False), flush=True)

async def main():
    log = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--disable-gpu", "--no-sandbox"])
        for i, (n, u) in enumerate(SITES, 1):
            await one(browser, i, n, u, log)
        await browser.close()
    json.dump(log, open(OUT / "index.json", "w"), ensure_ascii=False, indent=1)
    print("ГОТОВО-REFS ok=%d из %d" % (sum(1 for r in log if r.get("ok")), len(log)), flush=True)

asyncio.run(main())
