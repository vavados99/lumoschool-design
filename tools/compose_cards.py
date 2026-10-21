import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

D = Path("/root/projects/english-school/визуалы/10-концептов")
PICK = {"01":2,"02":1,"03":3,"04":1,"05":1,"06":1,"07":1,"08":1,"09":3,"10":1}
CARDS = {
 "01": ("Одне вікно", "Політ над нічними містами: Київ, Варшава, Берлін, Лондон. У кожному горить одне вікно — і це один і той самий урок. Камера влітає у вікно, і ти вже в класі.", "left"),
 "02": ("Двері в пшениці", "Двері посеред поля. Скрол — це кроки до них. Відчиняєш, і за дверима вже клас.", "left"),
 "03": ("Люди-ліхтарі", "Тисячі вогників складаються в спіраль, і кожен вогник — учень. Торкаєшся — світло біжить до твого міста.", "left"),
 "04": ("Вишивка-світло", "Вишиванка оживає: візерунок стає світловою хвилею твого голосу. Дім, який ти несеш із собою.", "left"),
 "05": ("Вітраж мов", "Шість кольорових променів — шість мов сайту. Ступаєш у промінь, і мова змінюється.", "left"),
 "06": ("Нічна Земля", "Крутиш планету й бачиш, де в тебе вечір. Так обираєш час уроку, а золоті дуги тягнуться до всіх твоїх близьких.", "left"),
 "07": ("Хвиля", "Сторінка зі світлових ліній. Говориш — і лінії підіймаються гірським хребтом із твого голосу.", "left"),
 "08": ("Рідке світло", "Екран — світна рідина. Малюєш пальцем, і з неї спливають слова шістьма мовами.", "left"),
 "09": ("Паперове місто", "Місто з паперу. Одне вікно світиться яскравіше за інші — це твій урок. Торкнись, і воно відчиняється.", "left"),
 "10": ("Дім на всіх", "Будинок у розрізі: кожне вікно — учень в іншій країні. Золоті нитки світла зʼєднують їх в один клас.", "left"),
}
ARCS = """<svg style="position:absolute;inset:0" width="1344" height="768" viewBox="0 0 1344 768">
<defs><filter id="g"><feGaussianBlur stdDeviation="3"/></filter></defs>
<g fill="none" stroke="#FFD76A" stroke-linecap="round">
 <path d="M820 330 Q 760 160 560 190" stroke-width="5" filter="url(#g)"/><path d="M820 330 Q 760 160 560 190" stroke-width="2.6"/>
 <path d="M820 330 Q 700 120 430 250" stroke-width="5" filter="url(#g)"/><path d="M820 330 Q 700 120 430 250" stroke-width="2.6"/>
 <path d="M820 330 Q 640 100 300 330" stroke-width="5" filter="url(#g)"/><path d="M820 330 Q 640 100 300 330" stroke-width="2.6"/>
 <path d="M820 330 Q 900 120 1100 220" stroke-width="5" filter="url(#g)"/><path d="M820 330 Q 900 120 1100 220" stroke-width="2.6"/>
 <path d="M820 330 Q 560 40 120 360" stroke-width="5" filter="url(#g)"/><path d="M820 330 Q 560 40 120 360" stroke-width="2.6"/>
</g><circle cx="820" cy="330" r="9" fill="#FFF3C4"/><circle cx="820" cy="330" r="22" fill="none" stroke="#FFD76A" stroke-width="2" opacity=".7"/>
<g fill="#FFF3C4"><circle cx="560" cy="190" r="4"/><circle cx="430" cy="250" r="4"/><circle cx="300" cy="330" r="4"/><circle cx="1100" cy="220" r="4"/><circle cx="120" cy="360" r="4"/></g></svg>"""

TPL = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700&family=Onest:wght@400;500;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>*{margin:0;box-sizing:border-box}body{width:1344px;height:768px;position:relative;overflow:hidden;background:#000;font-family:'Onest'}
img.bg{position:absolute;inset:0;width:1344px;height:768px;object-fit:cover}
.scrim{position:absolute;left:0;right:0;bottom:0;height:420px;background:linear-gradient(to top,rgba(0,0,0,.86),rgba(0,0,0,.55) 45%,transparent)}
.top{position:absolute;left:44px;right:44px;top:34px;display:flex;justify-content:space-between;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.6)}
.logo{font:700 18px 'Unbounded';letter-spacing:.14em}.num{font:700 16px 'JetBrains Mono';letter-spacing:.16em}
h1{position:absolute;left:44px;bottom:158px;color:#fff;font:700 64px/1.02 'Unbounded';letter-spacing:-.03em;text-shadow:0 4px 24px rgba(0,0,0,.5)}
p{position:absolute;left:44px;bottom:60px;width:860px;color:#F1EEE6;font:500 22px/1.38 'Onest';text-shadow:0 2px 14px rgba(0,0,0,.7)}
.chips{position:absolute;right:44px;bottom:48px;display:flex;gap:8px}.chips span{font:700 13px 'JetBrains Mono';color:#fff;border:1.5px solid rgba(255,255,255,.75);border-radius:99px;padding:6px 11px;background:rgba(0,0,0,.25)}
.chips .on{background:#fff;color:#111}</style></head><body>
<img class="bg" src="__IMG__"><div class="scrim" style="__SC__"></div>__ARCS__
<div class="top"><div class="logo">LUMOSCHOOL</div><div class="num">__NUM__ / 10</div></div>
<h1>__TITLE__</h1><p>__TEXT__</p>
<div class="chips"><span class="on">UA</span><span>PL</span><span>EN</span><span>DE</span><span>CS</span><span>RU</span></div></body></html>"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox","--disable-gpu"])
        for cid, (title, text, _) in CARDS.items():
            html = (TPL.replace("__IMG__", (D / f"{cid}-{PICK[cid]}.jpg").as_uri()).replace("__NUM__", cid)
                    .replace("__TITLE__", title).replace("__TEXT__", text).replace("__ARCS__", ARCS if cid == "06" else "").replace("__SC__", "height:520px;background:linear-gradient(to top,rgba(0,0,0,.96),rgba(0,0,0,.72) 50%,transparent)" if cid in ("02","05") else ""))
            f = D / f"карта-{cid}.html"; f.write_text(html, encoding="utf-8")
            page = await b.new_page(viewport={"width":1344,"height":768})
            await page.goto(f.as_uri(), wait_until="load", timeout=60000)
            try: await page.wait_for_load_state("networkidle", timeout=15000)
            except Exception: pass
            await page.evaluate("document.fonts.ready"); await page.wait_for_timeout(1200)
            await page.screenshot(path=str(D / f"концепт-{cid}.png"))
            print("ok", cid, flush=True); await page.close()
        await b.close()
asyncio.run(main())
