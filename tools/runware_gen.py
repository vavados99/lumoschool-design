import json, os, sys, time, uuid, urllib.request, urllib.error
from pathlib import Path

def load_key():
    for line in open(os.path.expanduser("~/.hermes/.env"), encoding="utf-8"):
        if line.startswith("RUNWARE_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("нет RUNWARE_API_KEY")

def gen(key, prompt, model="runware:101@1", w=1344, h=768, steps=28, cfg=3.5, seed=None):
    task = {"taskType": "imageInference", "taskUUID": str(uuid.uuid4()), "positivePrompt": prompt,
            "model": model, "width": w, "height": h, "numberResults": 1, "outputType": "URL",
            "outputFormat": "JPG", "includeCost": True, "steps": steps, "CFGScale": cfg}
    if seed is not None: task["seed"] = seed
    req = urllib.request.Request("https://api.runware.ai/v1", data=json.dumps([task]).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=170) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:300]}

def balance(key):
    """Остаток на счёте Runware (задача accountManagement/getDetails). Возвращает (сумма, бесплатная часть, валюта) или None."""
    task = {"taskType": "accountManagement", "taskUUID": str(uuid.uuid4()), "operation": "getDetails"}
    req = urllib.request.Request("https://api.runware.ai/v1", data=json.dumps([task]).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            res = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:200]}
    d = (res.get("data") or [{}])[0]
    b = d.get("balance")
    if not b:
        return {"нет_поля_balance": list(d.keys())[:8], "errors": res.get("errors")}
    return b

def download(url, path):
    with urllib.request.urlopen(url, timeout=120) as r:
        Path(path).write_bytes(r.read())

if __name__ == "__main__":
    key = load_key()
    out = Path("/root/projects/english-school/визуалы/10-концептов"); out.mkdir(parents=True, exist_ok=True)
    p = ("Cinematic night photograph of a monumental Soviet-era panel apartment block in a snowy European city, hundreds of dark windows, "
         "exactly one window glowing warm golden, a tiny silhouette of a person at a desk speaking to a laptop, falling snow, deep blue hour sky, "
         "anamorphic lens, atmospheric haze, film grain, Roger Deakins lighting, ultra detailed, 35mm film still, no text")
    t = time.time(); res = gen(key, p, seed=101)
    print("секунд:", round(time.time() - t, 1))
    d = res.get("data", [{}])[0] if "data" in res else None
    if d:
        print("цена, $:", d.get("cost"), "| поля:", sorted(d.keys()))
        if d.get("imageURL"):
            download(d["imageURL"], out / "тест-01-dev.jpg"); print("сохранено, байт:", (out / "тест-01-dev.jpg").stat().st_size)
    else:
        print("ответ:", json.dumps(res, ensure_ascii=False)[:500])
