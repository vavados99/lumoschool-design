#!/usr/bin/env python3
"""Настоящий расход Claude у всего Хермеса: токены из state.db × цены Anthropic.

Встроенный счётчик Hermes для моделей 5.5 занижает в десятки раз, поэтому считаем сами.
Счётчики токенов в сессиях накопительные, поэтому храним снимок и считаем прирост.
Одноразовые запуски (hermes -z) и помощники пишутся в ту же таблицу и тоже попадают в счёт.

  python3 claude_spend.py          — посчитать прирост с прошлого замера, записать в журнал трат
  python3 claude_spend.py --peek   — то же, но ничего не записывать (проверка посреди работы)
"""
import datetime
import fcntl
import json
import os
import pathlib
import sqlite3
import sys
import time
from zoneinfo import ZoneInfo

DB = "/root/.hermes/state.db"
HERE = pathlib.Path(__file__).resolve().parent
SNAP = HERE / ".spend-snapshot.json"
LEDGER = HERE / "spend-ledger.jsonl"
LOCK = HERE / ".spend.lock"
TZ = ZoneInfo("Europe/Kyiv")
MONTH_BUDGET = 200.0
DAY_CAP = 50.0

# $ за 1M токенов: вход, выход, чтение кэша (0.1× входа), запись кэша.
# Запись кэша — по тарифу 1 час (2× входа): режим auto ставит его живой переписке, так оценка сверху.
PRICES = {
    "haiku": (0.10, 0.50, 0.01, 0.20),
    "sonnet": (2.0, 10.0, 0.20, 4.0),
    "opus": (4.0, 20.0, 0.40, 8.0),
}
FIELDS = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens")


def family(model):
    m = (model or "").lower()
    return next((k for k in PRICES if k in m), None)


def local(ts):
    return datetime.datetime.fromtimestamp(ts, TZ)


def read_ledger():
    entries, bad = [], 0
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            try:
                entries.append(json.loads(line))
            except ValueError:
                bad += 1
    return entries, bad


def write_atomic(path, text):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def main():
    peek = "--peek" in sys.argv
    now = time.time()
    with open(LOCK, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # пульс и ручной вызов не посчитают одну дельту дважды

        con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        rows = con.execute(f"select id, model, {', '.join(FIELDS)} from sessions").fetchall()
        cur = {r[0]: [r[1]] + [int(x or 0) for x in r[2:]] for r in rows}

        if not SNAP.exists():
            if not peek:
                write_atomic(SNAP, json.dumps({"ts": now, "sessions": cur}))
            print("Первый замер: база сохранена. Расход считается с этой минуты; что было раньше — только в консоли Anthropic.")
            return

        try:
            snap = json.loads(SNAP.read_text())
        except ValueError:
            print("Снимок расхода повреждён. Удали .spend-snapshot.json и запусти заново, это начнёт счёт с нуля.")
            return
        prev = snap["sessions"]
        new_snap = {}
        by_family = {k: 0.0 for k in PRICES}
        unknown = set()
        for sid, (model, *vals) in cur.items():
            old = prev.get(sid, [model, 0, 0, 0, 0])
            # Счётчик уменьшился (сброс сессии) — считаем текущее значение целиком.
            delta = [v - o if v >= o else v for v, o in zip(vals, old[1:])]
            fam = family(model)
            if fam is None and any(delta):
                unknown.add(model)
                new_snap[sid] = old  # не продвигаем: трата без цены не должна пропасть молча
                continue
            new_snap[sid] = [model] + vals
            if fam:
                by_family[fam] += sum(d * p for d, p in zip(delta, PRICES[fam])) / 1e6
        spent = sum(by_family.values())

        entries, bad = read_ledger()
        if not peek:
            entry = {"from": snap["ts"], "to": now, "usd": round(spent, 4),
                     "by": {k: round(v, 4) for k, v in by_family.items()}}
            with LEDGER.open("a") as f:
                f.write(json.dumps(entry) + "\n")
            write_atomic(SNAP, json.dumps({"ts": now, "sessions": new_snap}))
            entries.append(entry)
        else:
            entries.append({"from": snap["ts"], "to": now, "usd": spent})

    today, month = local(now).date(), local(now).strftime("%Y-%m")
    day_total = sum(e["usd"] for e in entries if local(e["to"]).date() == today)
    month_entries = [e for e in entries if local(e["to"]).strftime("%Y-%m") == month]
    month_total = sum(e["usd"] for e in month_entries)
    first = min((e["from"] for e in month_entries), default=snap["ts"])

    fmt = lambda ts: local(ts).strftime("%d.%m %H:%M")
    parts = " · ".join(f"{k.capitalize()} ${v:.2f}" for k, v in by_family.items() if v >= 0.005)
    print(f"Весь Хермес, Claude с {fmt(snap['ts'])} по {fmt(now)}: ${spent:.2f}" + (f" ({parts})" if parts else ""))
    print(f"Сегодня: ${day_total:.2f} из потолка ${DAY_CAP:.0f}" + ("  ⛔ ПОТОЛОК ДОСТИГНУТ" if day_total >= DAY_CAP else ""))
    print(f"С начала месяца (замер с {fmt(first)}): ${month_total:.2f} из ${MONTH_BUDGET:.0f}" + ("  ⛔ МЕСЯЦ ИСЧЕРПАН" if month_total >= MONTH_BUDGET else ""))
    left = max(0.0, min(DAY_CAP - day_total, MONTH_BUDGET - month_total))
    print(f"Запас сейчас: ${left:.2f} (меньшее из остатка суток и месяца)")
    if unknown:
        print("Без цены, не посчитаны: " + ", ".join(sorted(m or "?" for m in unknown)))
    if bad:
        print(f"В журнале трат {bad} битых строк пропущено.")


if __name__ == "__main__":
    main()
