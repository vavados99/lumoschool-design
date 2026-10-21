from pathlib import Path
B = Path("/root/projects/english-school/визуалы/направления")
def edit(name, pairs):
    p = B/name/"index.html"; s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{name}: найдено {n} раз: {old[:60]!r}"
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8"); print("ok", name, len(pairs))

# ---- 3 метро
edit("3-метро", [
 (".tag{position:absolute;left:70px;top:104px;", ".tag{position:absolute;left:56px;top:104px;"),
 ("h1{position:absolute;left:66px;top:136px;", "h1{position:absolute;left:56px;top:136px;"),
 (".sub{position:absolute;left:70px;top:372px;", ".sub{position:absolute;left:56px;top:372px;"),
 ("font:500 12px 'JetBrains Mono';letter-spacing:.1em;color:#7A8090;z-index:3}", "font:500 13px 'JetBrains Mono';letter-spacing:.1em;color:#4A5160;z-index:3}"),
 ("const cities=", "const TC=['#C42A21','#D9680A','#9A7000','#0E7A45','#1F6BFF','#6A2BD9'];\nconst cities="),
 ('font-size="22" fill="${C[i]}"', 'font-size="22" fill="${TC[i]}"'),
 ('font-size="13" fill="#7A8090" letter-spacing="2">РІВНІ ВІД A1 ДО C2 — ЩО БІЛЬШЕ СТАНЦІЙ ПРОЙДЕНО, ТИМ ВИЩЕ ТИ</text>', 'font-size="15" fill="#4A5160" letter-spacing="2">РІВНІ A1 → C2 · КОЖНА СТАНЦІЯ — КРОК ВПЕРЕД</text>'),
 ("const lv=['A1'", "for(let i=0;i<6;i++){const x=1010+(i%2)*46,y=T[i];st+=`<rect x=\"${x}\" y=\"${y-13}\" width=\"76\" height=\"26\" rx=\"13\" fill=\"${C[i]}\" stroke=\"#F4F1EA\" stroke-width=\"4\"/>`+[0,1,2].map(k=>`<rect x=\"${x+12+k*20}\" y=\"${y-5}\" width=\"12\" height=\"9\" rx=\"2\" fill=\"#fff\"/>`).join('');}\nconst lv=['A1'"),
 ("document.getElementById('m').innerHTML=d+st+lb;", "const ghost=`<text x=\"1180\" y=\"600\" text-anchor=\"end\" font-family=\"Onest\" font-weight=\"800\" font-size=\"400\" fill=\"none\" stroke=\"#12151C\" stroke-opacity=\".08\" stroke-width=\"2\" letter-spacing=\"-14\">LUMO</text>`;\ndocument.getElementById('m').innerHTML=ghost+d+st+lb;"),
 ("font:'Onest',btnfg:'#fff'});", "font:'Onest',btnfg:'#fff',sig:k=>{const col=k==='kids'?'#E8352B':k==='teens'?'#1F6BFF':'#17A862';return `<div style=\"position:absolute;left:0;top:0;bottom:0;width:10px;background:${col}\"></div><div style=\"position:absolute;left:-2px;top:26px;width:14px;height:14px;border-radius:50%;background:#fff;border:4px solid #12151C\"></div>`}});"),
])

# ---- 4 ефір
edit("4-ефір", [
 (".keys{position:absolute;left:300px;top:240px;display:flex;gap:16px}", ".dial:after{content:'';position:absolute;inset:0;background:linear-gradient(115deg,rgba(255,255,255,.30) 0,rgba(255,255,255,.08) 22%,transparent 42%);pointer-events:none}\n.keys{position:absolute;left:300px;top:246px;display:flex;gap:12px}"),
 (".keys div{width:68px;height:68px;border-radius:50%;", ".keys div{width:64px;height:64px;border-radius:50%;"),
 ("font:800 18px 'Unbounded';box-shadow:0 6px 0 #1A0F0A}", "font:800 17px 'Unbounded';box-shadow:0 6px 0 #1A0F0A}"),
 ('<svg id="dial" width="480" height="170" viewBox="0 0 480 170">', '<svg id="dial" width="470" height="160" viewBox="0 0 470 160">'),
 ("const W=480;", "const W=470;"),
 ("● МОВА САЙТУ: УКРАЇНСЬКА · ПОВЕРНИ РУЧКУ, ЩОБ ЗМІНИТИ", "● МОВА САЙТУ: УКРАЇНСЬКА"),
 (".cap{position:absolute;font:700 14px 'JetBrains Mono';", ".cap{position:absolute;font:700 15px 'JetBrains Mono';"),
 ("background:#F7ECD6;border:6px solid #1A0F0A;border-radius:44px;box-shadow:14px 14px 0 #1A0F0A;z-index:2}", "background:linear-gradient(180deg,#FCF4E2,#EBDCBA);border:6px solid #1A0F0A;border-radius:44px;box-shadow:14px 14px 0 #1A0F0A;z-index:2}"),
 ("<h1>Ти в ефірі.</h1>", "<h1>Ти в ефірі.</h1>\n<div class=\"live\" style=\"left:972px;top:120px\"><div class=\"lamp\"></div>LIVE</div>"),
 ('<div class="radio">', '<svg style="position:absolute;left:0;top:0;z-index:1" width="1512" height="830"><line x1="1030" y1="268" x2="1150" y2="178" stroke="#1A0F0A" stroke-width="7" stroke-linecap="round"/><circle cx="1154" cy="175" r="11" fill="#12C8B0" stroke="#1A0F0A" stroke-width="5"/></svg>\n<div class="radio">'),
 ('<div class="keys">', '<div style="position:absolute;left:300px;top:222px;width:16px;height:16px;border-radius:50%;background:#12C8B0;box-shadow:0 0 10px 3px #12C8B0;border:3px solid #1A0F0A"></div>\n <div class="keys">'),
 ("font:'Unbounded',btnfg:'#fff'});", "font:'Unbounded',btnfg:'#fff',sig:k=>`<div style=\"position:absolute;right:16px;top:${k==='kids'?'auto':'16px'};bottom:${k==='kids'?'16px':'auto'};width:16px;height:16px;border-radius:50%;background:#FF2A1F;box-shadow:0 0 12px 3px rgba(255,40,20,.7);border:3px solid #1A0F0A\"></div>`});"),
])

# ---- 5 вихор
p = B/"5-вихор"/"index.html"; s = p.read_text(encoding="utf-8")
a = s.index("for(let i=0;i<130;i++){"); b = s.index("weatherStrip(")
new_loop = """const placed=[];
function hit(a,b){return a.x1<b.x2+8&&a.x2>b.x1-8&&a.y1<b.y2+6&&a.y2>b.y1-6}
for(let i=0;i<300;i++){
 const lang=order[i%6],ph=L[lang][Math.floor(i/6)%6];
 const ang=i*0.58, r=255+i*5.2+i*i*0.045;
 const x=cx+Math.cos(ang)*r*1.18, y=cy+Math.sin(ang)*r*0.86;
 let fs=Math.min(250,24+(r-255)*0.1); if(lang==='RU')fs*=0.82;
 const serif=i%3===0, w=fs*ph.length*(serif?0.5:0.68);
 const bx={x1:x-w/2,x2:x+w/2,y1:y-fs/2,y2:y+fs/2};
 if(bx.y1<92||bx.y2>845||bx.x2<-40||bx.x1>1552) continue;
 if(bx.x1<470&&bx.y2>760) continue;
 const dx=Math.max(0,Math.abs(x-cx)-w/2),dy=Math.max(0,Math.abs(y-cy)-fs/2); if(Math.hypot(dx,dy)<222) continue;
 if(placed.some(q=>hit(q,bx))) continue; placed.push(bx);
 const el=document.createElement('div');el.className='w';
 el.style.cssText=`left:${x}px;top:${y}px;font:${serif?'italic 900':'600'} ${fs}px '${serif?'Playfair Display':'Unbounded'}';color:${col[lang]};opacity:${lang==='UA'?1:lang==='RU'?.7:.9};transform:translate(-50%,-50%) rotate(${Math.sin(ang*1.3)*9}deg);z-index:${Math.round(10-fs/30)}`;
 el.textContent=ph;h.appendChild(el);
}
"""
s = s[:a] + new_loop + s[b:]
old = "font:'Unbounded',btnfg:'#0A0A14'});"
assert s.count(old)==1
s = s.replace(old, "font:'Unbounded',btnfg:'#0A0A14',sig:k=>`<div style=\"position:absolute;right:16px;bottom:8px;font:italic 900 40px 'Playfair Display';color:#C8FF2E;transform:rotate(-6deg)\">${k==='kids'?'Привіт':k==='teens'?'Cześć':'Hello'}</div>`});")
p.write_text(s, encoding="utf-8"); print("ok 5-вихор")
