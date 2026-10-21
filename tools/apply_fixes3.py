from pathlib import Path
import re
B = Path("/root/projects/english-school/визуалы/направления")
def edit(path, pairs):
    p = Path(path); s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        n = s.count(old); assert n == 1, f"{p.parent.name}: найдено {n} раз: {old[:70]!r}"
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8"); print("ok", p.parent.name, len(pairs))

edit(B/"3-метро/index.html", [('stroke-opacity=".08"', 'stroke-opacity=".05"'), ("'#D9680A'", "'#C25A00'")])
edit(B/"4-ефір/index.html", [
 ("""y="54" text-anchor="middle" font-family="Unbounded" font-weight="800" font-size="${i?20:26}\"""", """y="78" text-anchor="middle" font-family="Unbounded" font-weight="800" font-size="${i?20:26}\""""),
 ('<line x1="90" y1="14" x2="90" y2="160" stroke="#FF2A1F" stroke-width="3"/><circle cx="90" cy="14" r="6" fill="#FF2A1F"/><text x="20" y="78"', '<line x1="90" y1="88" x2="90" y2="158" stroke="#FF2A1F" stroke-width="3"/><circle cx="90" cy="88" r="6" fill="#FF2A1F"/><text x="20" y="30"'),
 ("rgba(255,255,255,.30) 0,rgba(255,255,255,.08) 22%,transparent 42%", "rgba(255,255,255,.5) 0,rgba(255,255,255,.12) 26%,transparent 46%"),
])
edit(B/"5-вихор/index.html", [
 ("bx.y2>845", "bx.y2>800"),
 ("a.x1<b.x2+8&&a.x2>b.x1-8&&a.y1<b.y2+6&&a.y2>b.y1-6", "a.x1<b.x2+16&&a.x2>b.x1-16&&a.y1<b.y2+12&&a.y2>b.y1-12"),
 ("font:500 13px 'JetBrains Mono';letter-spacing:.14em;z-index:6;background:#0A0A14", "font:500 14px 'JetBrains Mono';letter-spacing:.14em;z-index:6;background:#0A0A14"),
])
