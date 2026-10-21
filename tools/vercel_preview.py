#!/usr/bin/env python3
"""Закрытый предпросмотр LUMOSCHOOL на Vercel (REST API, токен команды).
Использование: python3 vercel_preview.py <папка-прототипа>
Токен берётся из /root/.hermes/.env (значение не печатается).
Публикуются только html/css/js/шрифты/картинки; shots/ и .md не уезжают.
Проект создаётся с включённой защитой Vercel Authentication (ssoProtection: all).
"""
import base64, json, os, sys, urllib.error, urllib.request

def load_env():
    env = {}
    for line in open("/root/.hermes/.env", encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ENV = load_env()
TOKEN = ENV.get("VERCEL_TOKEN", "")
TEAM = ENV.get("VERCEL_TEAM") or ENV.get("VERCEL_TEAM_ID") or ENV.get("VERCEL_ORG_ID") or ""
PROJECT = "lumoschool-preview"
API = "https://api.vercel.com"

def api(path, payload=None, method=None, ok404=False):
    sep = "&" if "?" in path else "?"
    url = API + path + (f"{sep}teamId={TEAM}" if TEAM else "")
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        if ok404 and e.code == 404:
            return None
        print(f"HTTP {e.code} {path}: {body}")
        sys.exit(1)

def collect(root):
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ("shots", ".git", "node_modules")]
        for f in fn:
            if f.lower().endswith((".html", ".css", ".js", ".woff2", ".woff", ".ttf", ".png", ".jpg", ".jpeg", ".webp", ".svg")):
                out.append(os.path.join(dp, f))
    return out

def main():
    root = sys.argv[1]
    if not TOKEN:
        print("нет VERCEL_TOKEN"); sys.exit(1)
    if api(f"/v9/projects/{PROJECT}", ok404=True) is None:
        api("/v10/projects", {"name": PROJECT, "framework": None,
                              "ssoProtection": {"deploymentType": "all"}})
        print("проект создан")
    # защита включена всегда (на случай уже существующего проекта)
    api(f"/v9/projects/{PROJECT}", {"ssoProtection": {"deploymentType": "all"}}, method="PATCH")
    files = []
    for p in collect(root):
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        files.append({"file": rel, "data": base64.b64encode(open(p, "rb").read()).decode(), "encoding": "base64"})
    dep = api("/v13/deployments?skipAutoDetectionConfirmation=1",
              {"name": PROJECT, "files": files, "target": "production",
               "projectSettings": {"framework": None, "buildCommand": None, "outputDirectory": None}})
    print("deployment:", dep.get("id"), dep.get("url"), dep.get("readyState"))
    proj = api(f"/v9/projects/{PROJECT}")
    print("ssoProtection:", proj.get("ssoProtection"))
    print("aliases:", [a.get("domain") for a in proj.get("alias", [])] or proj.get("targets"))

main()
