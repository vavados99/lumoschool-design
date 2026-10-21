from pathlib import Path
import re
B = Path("/root/projects/english-school/визуалы/направления")
def edit(path, pairs):
    p = Path(path); s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        n = s.count(old); assert n == 1, f"{p.parent.name}: найдено {n} раз: {old[:70]!r}"
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8"); print("ok", p.parent.name, len(pairs))

edit(B/"shared/weather.js", [("height:280px;", "height:300px;"), ("display:flex;gap:20px;height:216px", "display:flex;gap:20px;height:236px")])

# призма
p = B/"1-призма/index.html"; s = p.read_text(encoding="utf-8")
a = s.index("const rays=["); b = s.index("const ox=826")
s = s[:a] + """const rays=[
 {n:'Čeština',c:'#A77BFF',t:'#C4A8FF',y:250},{n:'English',c:'#5B92FF',t:'#8DB4FF',y:350},{n:'Русский',c:'#2CF0BE',t:'#7FF7D6',y:450},
 {n:'Українська',c:'#FFE14D',t:'#FFE14D',y:550,a:1},{n:'Deutsch',c:'#FF9A2E',t:'#FFBE7A',y:650},{n:'Polski',c:'#FF4D5E',t:'#FF8E99',y:750}];
""" + s[b:]
p.write_text(s, encoding="utf-8")
edit(p, [
 (".lead{position:absolute;left:56px;top:510px;", ".lead{position:absolute;left:56px;top:466px;"),
 ('lab+=`<text x="1470" y="${r.y-(r.a?30:24)}"', 'lab+=`<text ${r.a?\'id="actlab" \':\'\'}x="1470" y="${r.y-(r.a?30:24)}"'),
 ('fill="${r.c}" stroke="#0B0A2E" stroke-width="14"', 'fill="${r.t}" stroke="#0B0A2E" stroke-width="14"'),
 ("""
 if(r.a) lab+=`<text x="1470" y="${r.y-84}" text-anchor="end" font-family="JetBrains Mono" font-weight="700" font-size="15" letter-spacing="2" fill="#FFE14D" stroke="#0B0A2E" stroke-width="8" paint-order="stroke">● ОБРАНА МОВА</text>`;""", ""),
 ("${lab}`;\nweatherStrip(", "${lab}`;\n{const bb=document.getElementById('actlab').getBBox(),cy=bb.y+bb.height/2;document.getElementById('s').insertAdjacentHTML('beforeend',`<circle cx=\"${bb.x-34}\" cy=\"${cy}\" r=\"10\" fill=\"#FFE14D\"/><circle cx=\"${bb.x-34}\" cy=\"${cy}\" r=\"20\" fill=\"none\" stroke=\"#FFE14D\" stroke-width=\"2\" opacity=\".7\"/>`)}\nweatherStrip("),
])

edit(B/"2-вирізка/index.html", [
 ('<line x1="40" y1="556" x2="800" y2="556"', '<line x1="40" y1="546" x2="800" y2="546"'),
 ("translate(820 556) rotate(-8)", "translate(820 546) rotate(-8)"),
 ("left:84px;top:566px;font:700 50px/1.05 'Caveat'", "left:84px;top:562px;font:700 50px/1.05 'Caveat'"),
 ("piece({x:84,y:692,w:400,h:92,", "piece({x:84,y:702,w:400,h:92,"),
 ("left:520px;top:716px;font:700 16px", "left:520px;top:726px;font:700 16px"),
 ("[120,700,-18],[460,702,14]", "[120,710,-18],[460,712,14]"),
 ("k==='teens'?'62%':'20%'", "k==='teens'?'62%':'66%'"),
])
edit(B/"3-метро/index.html", [("stroke-opacity=\\\".08\\\"", "stroke-opacity=\\\".05\\\""), ("'#D9680A'", "'#C25A00'")])
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
