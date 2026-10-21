import json, sys, time, uuid, urllib.request, urllib.error
from pathlib import Path
sys.path.insert(0, "/root/projects/english-school/tools")
from runware_gen import load_key, balance, download

OUT = Path("/root/projects/english-school/визуалы/прототипы"); OUT.mkdir(parents=True, exist_ok=True)

def call(key, task, timeout=240):
    req = urllib.request.Request("https://api.runware.ai/v1", data=json.dumps([task]).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e: return {"http_error": e.code, "body": e.read().decode()[:400]}
    except Exception as e: return {"error": str(e)[:300]}

PROMPT = """A complete, polished desktop website homepage design mockup for an online English school named LUMOSCHOOL for Ukrainians living abroad, shown as a full-bleed 16:10 screenshot of a real website, Awwwards-level, ultra detailed UI design.
HERO: a vast golden wheat field under a deep blue sky with a freestanding wooden doorway in the middle, the open door glowing with warm light revealing a cozy classroom. Over it, the exact headline in white elegant serif: "Відчини двері до англійської". Below it small text exactly: "Живі уроки з викладачем у малих групах. Для українців у світі." and a warm gold rounded button with exact text "Записатися на пробний урок".
TOP NAV bar, semi-transparent: logo "LUMOSCHOOL" at left, menu items exactly: "Уроки", "Дітям", "Дорослим", "Ціни", "Увійти", and at right a language switcher with six small pills: "UA PL EN DE CS RU" with UA highlighted.
BELOW THE HERO, the start of the next section: a row of three glass cards with headings exactly "Групи до 6 людей", "Уроки наживо", "Розклад у вашому часі". Clean typography, generous whitespace, cinematic warm gold and deep blue palette, high-end editorial web design, crisp readable Ukrainian Cyrillic text."""

MODELS = [
 ("gpt-image-2", "openai:gpt-image@2", {}),
 ("gpt-image-1.5", "openai:4@1", {}),
 ("nano-banana-pro", "google:4@2", {}),
 ("ideogram-4.5", "ideogram:4.5@0", {}),
 ("seedream-5-pro", "bytedance:seedream@5.0-pro", {}),
]
if __name__ == "__main__":
    key = load_key(); b0 = balance(key); print("баланс до:", b0, flush=True)
    only = sys.argv[1:] 
    for name, air, extra in MODELS:
        if only and name not in only: continue
        task = {"taskType": "imageInference", "taskUUID": str(uuid.uuid4()), "positivePrompt": PROMPT, "model": air,
                "width": 1536, "height": 1024, "numberResults": 1, "outputType": "URL", "outputFormat": "PNG", "includeCost": True}
        task.update(extra)
        t = time.time(); res = call(key, task)
        d = (res.get("data") or [{}])[0] if "data" in res else {}
        if d.get("imageURL"):
            f = OUT / f"тест-{name}.png"; download(d["imageURL"], f)
            print(name, "ok | цена $", d.get("cost"), "| сек", round(time.time() - t, 1), "|", f.name, flush=True)
        else:
            print(name, "ОШИБКА:", json.dumps(res, ensure_ascii=False)[:420], flush=True)
    print("баланс после:", balance(key))
