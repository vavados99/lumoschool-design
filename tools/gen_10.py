import json, sys, time
from pathlib import Path
sys.path.insert(0, "/root/projects/english-school/tools")
from runware_gen import load_key, gen, download

OUT = Path("/root/projects/english-school/визуалы/10-концептов"); OUT.mkdir(parents=True, exist_ok=True)
STYLE = ", ultra detailed, high dynamic range, professional art direction, no text, no letters, no watermark"
JOBS = [
 ("01", "Одне вікно", "Telephoto cinematic photograph of the dark concrete facade of a vast Soviet-era panel apartment block at night in falling snow, only three windows in frame, two completely dark and ONE single window glowing warm golden amber, a small silhouette of a person leaning toward a laptop inside the glowing window, deep blue hour, volumetric snowfall, anamorphic bokeh, 35mm film still, Roger Deakins lighting"),
 ("02", "Двері в пшениці", "Surreal fine-art photograph: a single freestanding wooden doorway standing alone in the middle of an endless golden wheat field under an enormous deep blue sky, the open door radiates warm glowing light revealing a cozy wooden classroom with a long table inside, golden hour, long shadows, wheat swaying, Magritte meets Gregory Crewdson, cinematic"),
 ("03", "Люди-ліхтарі", "Aerial drone photograph at night of thousands of people standing on a dark hillside each holding a small glowing lantern, together forming a gigantic luminous spiral of golden light against deep indigo darkness, light mist, epic scale, photorealistic, awe-inspiring"),
 ("04", "Вишивка-світло", "Extreme macro photograph of traditional Ukrainian cross-stitch embroidery in red and black thread on white linen, the stitched pattern dissolves into glowing fiber-optic threads and flowing sound-wave lines of cyan and gold light rising off the fabric, luxurious texture, shallow depth of field, 100mm macro lens, studio lighting"),
 ("05", "Вітраж мов", "Interior of an empty grand old wooden classroom, a gigantic stained-glass window with six color zones violet blue emerald yellow orange red casts six distinct colored volumetric light beams across the dark wood floor and old desks, dust motes floating in the light, cinematic god rays, ultra wide architectural photography, dramatic"),
 ("06", "Нічна Земля", "Photorealistic view of planet Earth at night from low orbit, Europe glowing with city lights, thin delicate golden arcs of light connecting one bright point in Eastern Europe to many cities across Europe and North America, aurora on the horizon, atmosphere glow, astronaut photography, ultra sharp"),
 ("07", "Хвиля", "Minimalist graphic artwork on pure black background: dozens of thin glowing white and electric blue parallel wave lines stacked like the Joy Division Unknown Pleasures cover, the peaks rise into a mountain ridge whose silhouette subtly resembles a human face in profile speaking, neon glow with soft bloom, razor sharp lines, high contrast"),
 ("08", "Рідке світло", "Macro abstract high-speed photograph of iridescent liquid ink swirling in dark water, glowing ribbons of magenta cyan gold and violet merging into a flowing wave, volumetric light, oil-slick sheen, deep black background, ultra detailed, luminous"),
 ("09", "Паперове місто", "Handcrafted layered cut-paper diorama of a night city, kirigami buildings in deep blue and teal paper, tiny warm glowing windows lit from behind, one window brighter than the rest, layered depth with soft shadows, tilt-shift macro photograph, tactile paper texture, whimsical but elegant, studio lighting"),
 ("10", "Дім на всіх", "Isometric 3D cutaway render of a tall apartment building like a dollhouse, each room a different cozy interior with one person speaking to a glowing laptop, rooms connected by delicate golden threads of light running between windows, warm night lighting against a dark blue background, Pixar quality, soft global illumination, highly detailed miniatures"),
]
SEEDS = [11, 22, 33, 44]
BUDGET = 0.6
key = load_key(); total = 0.0; log = []
for jid, title, prompt in JOBS:
    for k, seed in enumerate(SEEDS, 1):
        if total > BUDGET: print("БЮДЖЕТ ПРЕВЫШЕН, стоп", flush=True); break
        res = gen(key, prompt + STYLE, seed=seed, steps=32)
        d = res.get("data", [{}])[0] if "data" in res else {}
        if not d.get("imageURL"): print(jid, k, "ОШИБКА", json.dumps(res, ensure_ascii=False)[:200], flush=True); continue
        f = OUT / f"{jid}-{k}.jpg"; download(d["imageURL"], f)
        c = d.get("cost") or 0; total += c; log.append({"id": jid, "n": k, "seed": seed, "cost": c, "file": f.name})
        print(jid, k, "ok", c, flush=True)
json.dump({"total": round(total, 4), "items": log, "titles": {j[0]: j[1] for j in JOBS}}, open(OUT / "log.json", "w"), ensure_ascii=False, indent=1)
print("ГОТОВО-ГЕН итого $", round(total, 4), "картинок", len(log), flush=True)
