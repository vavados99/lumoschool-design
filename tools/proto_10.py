import json, sys, time, uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "/root/projects/english-school/tools")
from bakeoff import call
from runware_gen import load_key, balance, download

OUT = Path("/root/projects/english-school/визуалы/прототипы")
BASE = ("A complete, polished desktop website design prototype for an online English school named LUMOSCHOOL for Ukrainians living abroad, "
        "shown as a flat 16:10 web page screenshot without browser chrome. Awwwards-winning, art-directed, NOT a template: bold unexpected composition, "
        "ultra detailed UI design, real typography, generous whitespace. All visible text must be correct Ukrainian Cyrillic spelled exactly as quoted in double quotes, "
        "keep all other text minimal and real. Top navigation: logo \"LUMOSCHOOL\", items \"Уроки\", \"Дітям\", \"Дорослим\", \"Ціни\", \"Увійти\", and a language switcher with six small pills \"UA PL EN DE CS RU\" with UA active. ")

C = {
 "01": ("Одне-вікно",
  "SCREEN: hero. Cinematic night scene: a monumental snowy concrete apartment block, one single window glowing warm gold with a tiny silhouette at a laptop; the language switcher is styled as six tiny glowing windows. Headline in large elegant serif: \"Де б ти не був — ти в одному класі\". Subline: \"Одне вікно. Один урок. Усі наші міста.\" Gold button: \"Зайти на урок\". Palette deep blue night, warm gold.",
  "SCREEN: the next section of the same page. A horizontal night skyline strip with city labels \"Київ\", \"Варшава\", \"Берлін\", \"Лондон\", \"Торонто\" each with one lit window and the time \"19:00\", \"18:00\", \"18:00\", \"17:00\", \"12:00\". Section title: \"Один урок — у твоєму часі\". Below it a large glass card previewing a lesson room window with a teacher and four students in a video grid and a button \"Приєднатися\". Palette deep blue night, warm gold."),
 "02": ("Двері-в-пшениці",
  "SCREEN: hero. Surreal full-bleed photo: a freestanding wooden doorway in a golden wheat field under a huge deep-blue sky, the open door glows revealing a cozy classroom. Asymmetric layout with oversized serif headline: \"Відчини двері до англійської\", subline \"Живі уроки з викладачем у малих групах.\", gold button \"Записатися на пробний урок\". Palette wheat gold, deep blue.",
  "SCREEN: the next section of the same page, light cream background with wheat texture. Title: \"Три кроки до дверей\". Three large step cards with golden line icons and exact headings: \"Обери мову\", \"Знайди свій час\", \"Відчини двері\". Below them a teachers row with three portrait cards and names \"Анна\", \"Марк\", \"Софія\" and a footer with logo. Palette wheat gold, deep blue."),
 "03": ("Люди-ліхтарі",
  "SCREEN: hero. Epic aerial night photo: thousands of people on a dark hillside with lanterns forming a giant golden spiral of light. Headline in huge white bold type: \"Тисячі вогників. Одна мова.\", subline \"Вчи англійську разом з українцями в усьому світі.\", gold button \"Запалити свій вогник\". Palette indigo night, gold.",
  "SCREEN: the next section of the same page. A dark interactive world map with glowing gold dots and curved light lines, city labels \"Київ\", \"Варшава\", \"Берлін\", \"Прага\", \"Лондон\", \"Торонто\". Title: \"Де світиться твій клас\". A side panel card: \"Твоє місто: Варшава\" and a button \"Обрати час уроку\". Palette indigo night, gold."),
 "04": ("Вишивка-світло",
  "SCREEN: hero. Luxurious macro of Ukrainian red-and-black cross-stitch embroidery on white linen that turns into glowing sound-wave threads of gold and cyan light. Headline in refined serif: \"Мова — це наш дім у дорозі\", subline \"Англійська для тих, хто несе Україну з собою.\", gold button \"Почати навчання\". Palette linen white, red, black, gold.",
  "SCREEN: the next section of the same page. Three tall cards each framed by a different embroidery pattern border, exact headings: \"Для дітей\", \"Для підлітків\", \"Для дорослих\", each with a short line and a button \"Дізнатися більше\". Elegant, rich, craft-meets-tech. Palette linen white, red, black, gold."),
 "05": ("Вітраж-мов",
  "SCREEN: hero. Grand empty wooden classroom, a gigantic stained-glass window casting six distinct colored light beams (violet, blue, emerald, yellow, orange, red) onto the floor; each beam has a small label \"UA\", \"PL\", \"EN\", \"DE\", \"CS\", \"RU\" and UA beam is brightest. Headline: \"Шість мов. Одне світло.\", subline \"Обери мову сайту — і промінь ляже на твій шлях.\", gold button \"Почати\". Palette warm wood, jewel tones.",
  "SCREEN: the next section of the same page. Title: \"Для кожного віку — своє світло\". Three stained-glass-framed cards with exact headings \"Діти 7–10\", \"Підлітки 11–17\", \"Дорослі 18+\", each with a colored glow and a short line, plus a button \"Обрати групу\". Palette warm wood, jewel tones."),
 "06": ("Нічна-Земля",
  "SCREEN: hero. A photoreal Earth at night on the right, Europe glowing, golden arcs of light connecting cities. Left: headline \"Знайди свій час на карті світла\", subline \"Обери місто — і ми покажемо, коли в тебе вечірній урок.\", gold button \"Обрати місто\". Palette space black, gold, deep blue.",
  "SCREEN: the next section of the same page, a scheduling UI. A city dropdown showing \"Варшава\", a week calendar Пн–Нд with highlighted lesson slots, and a list of lessons with exact lines \"Пн 18:00 · Група B1\", \"Ср 18:00 · Розмовний клуб\", \"Пт 17:30 · Група A2\", and a button \"Записатися\". Palette space black, gold, deep blue."),
 "07": ("Хвиля",
  "SCREEN: hero. Minimalist black page with dozens of glowing white and electric-blue wave lines forming a mountain ridge, Joy Division style. Enormous headline: \"Говори.\", subline \"Англійська, яку чути.\", button \"Спробувати голос\". Extreme minimalism, huge type. Palette black, white, electric blue.",
  "SCREEN: the next section of the same page. A voice practice UI card: waveform, phrase \"How are you today?\", a round microphone button, a line \"Скажи фразу вголос\" and below a feedback line \"Чудово! Ще раз?\". Minimal, black, glowing blue. Palette black, white, electric blue."),
 "08": ("Рідке-світло",
  "SCREEN: hero. Black page filled with iridescent glowing liquid ink in magenta, cyan, gold and violet flowing across the screen like a wave. Headline: \"Мова тече.\", subline \"Малюй світлом — слова з'являються шістьма мовами.\", button \"Торкнутись світла\". Palette black, iridescent neon.",
  "SCREEN: the next section of the same page. A grid of big glowing word bubbles floating in dark liquid: \"Привіт\", \"Cześć\", \"Hello\", \"Hallo\", \"Ahoj\", \"Привет\", each in a different neon color, with title \"Одне слово — шість мов\". Palette black, iridescent neon."),
 "09": ("Паперове-місто",
  "SCREEN: hero. A handcrafted layered cut-paper night city diorama in blue and teal paper with tiny warm glowing windows and one brighter window. Headline in playful serif: \"Місто, де світиться твій урок\", subline \"Знайди своє вікно й відчини його.\", gold paper button \"Знайти вікно\". Palette paper blue, teal, warm gold.",
  "SCREEN: the next section of the same page, built from layered cut-paper. Three paper cards exact headings \"Групи до 6 людей\", \"Уроки наживо\", \"Розклад у вашому часі\", and a row of paper-cut teacher portraits with names \"Анна\", \"Марк\", \"Софія\". Palette paper blue, teal, warm gold."),
 "10": ("Дім-на-всіх",
  "SCREEN: hero. A tall isometric cutaway apartment building like a dollhouse, each room a cozy interior with one person at a laptop, golden threads of light connecting the rooms. Headline: \"Один дім. Усі вікна світу.\", subline \"Кожне вікно — учень з іншої країни. Разом — один клас.\", gold button \"Знайти своє вікно\". Palette warm night, gold, deep blue.",
  "SCREEN: the next section of the same page. A large lesson room preview inside a glowing window: teacher video, four student tiles, a whiteboard and a chat panel, title \"Так виглядає урок\", button \"Подивитися урок\". Palette warm night, gold, deep blue."),
}

def job(args):
    key, cid, name, which, text = args
    f = OUT / f"{cid}-{name}-{which}.png"
    prompt = BASE + text
    for attempt in range(2):
        task = {"taskType": "imageInference", "taskUUID": str(uuid.uuid4()), "positivePrompt": prompt, "model": "openai:gpt-image@2",
                "width": 1536, "height": 1024, "numberResults": 1, "outputType": "URL", "outputFormat": "PNG", "includeCost": True}
        res = call(key, task)
        d = (res.get("data") or [{}])[0] if "data" in res else {}
        if d.get("imageURL"):
            download(d["imageURL"], f); print(cid, which, "ok", d.get("cost"), flush=True); return (cid, which, d.get("cost") or 0, f.name)
        print(cid, which, "попытка", attempt + 1, "ошибка", json.dumps(res, ensure_ascii=False)[:160], flush=True)
    return (cid, which, 0, None)

if __name__ == "__main__":
    key = load_key(); b0 = balance(key); print("баланс до:", b0, flush=True)
    only = set(sys.argv[1:])
    jobs = []
    for cid, (name, a, b) in C.items():
        if only and cid not in only: continue
        jobs += [(key, cid, name, "A", a), (key, cid, name, "B", b)]
    with ThreadPoolExecutor(4) as ex: res = list(ex.map(job, jobs))
    total = round(sum(r[2] for r in res), 4); ok = sum(1 for r in res if r[3])
    time.sleep(6); b1 = balance(key)
    print("ГОТОВО-ПРОТО картинок", ok, "из", len(res), "| сумма по includeCost $", total, "| баланс до", b0, "после", b1, "| списано по балансу", round(b0 - b1, 4), flush=True)
    json.dump({"items": res, "total": total, "balance_before": b0, "balance_after": b1}, open(OUT / "лог-прототипов.json", "w"), ensure_ascii=False, indent=1)
