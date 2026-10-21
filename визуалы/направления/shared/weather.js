// «Настрої»: один каркас, три характери (приклад на токенах напряму). c.sig(kind) — фірмовий декор напряму.
function weatherStrip(el, c) {
  const f = c.font, bf = c.btnfg || '#111', sig = c.sig || (() => '');
  el.style.cssText = `width:1512px;height:300px;background:${c.bg};padding:0 56px;box-sizing:border-box;color:${c.fg};font-family:'Onest',sans-serif;border-top:1px solid ${c.fg}33;overflow:hidden`;
  const base = `flex:1;position:relative;overflow:hidden;padding:24px 26px;`;
  const kids = `<div style="${base}background:${c.card};border-radius:34px">
    <div style="position:absolute;right:-34px;top:-34px;width:140px;height:140px;border-radius:50%;background:${c.accent}"></div>
    <div style="position:absolute;right:70px;bottom:-46px;width:100px;height:100px;border-radius:50%;background:${c.accent2}"></div>${sig('kids')}
    <span style="position:relative;display:inline-block;background:${c.accent};color:${bf};border-radius:99px;padding:6px 14px;font:700 14px 'Onest'">ДІТИ · 7–10</span>
    <div style="position:relative;font:800 58px/1 '${f}';margin-top:14px;letter-spacing:-.02em">Привіт!</div>
    <div style="position:relative;margin-top:8px;font:500 17px 'Onest';opacity:.9">Урок 25 хв · 3 нові фрази</div>
    <div style="position:relative;margin-top:14px;display:inline-block;background:${c.accent};color:${bf};border-radius:99px;padding:11px 24px;font:700 16px 'Onest'">Почати →</div></div>`;
  const teens = `<div style="${base}background:${c.card};border:3px solid ${c.fg};border-radius:10px;box-shadow:8px 8px 0 ${c.accent}">${sig('teens')}
    <span style="position:relative;display:inline-block;background:${c.fg};color:${c.card};padding:5px 10px;font:700 14px 'JetBrains Mono';transform:rotate(-2deg)">ПІДЛІТКИ · 11–17</span>
    <div style="position:relative;font:900 58px/1 '${f}';margin-top:14px;letter-spacing:-.03em">Hello.</div>
    <div style="position:relative;margin-top:8px;font:500 17px 'Onest';opacity:.9">Урок 45 хв · 7 нових фраз</div>
    <div style="position:relative;margin-top:14px;display:inline-block;background:${c.accent};color:${bf};border:3px solid ${c.fg};padding:8px 22px;font:800 16px 'Onest'">Записатися →</div></div>`;
  const adults = `<div style="${base}background:${c.card};border:1px solid ${c.fg}55;border-radius:2px">${sig('adults')}
    <div style="position:relative;font:500 14px 'JetBrains Mono';letter-spacing:.14em;opacity:.8">ДОРОСЛІ · 18+</div>
    <div style="position:relative;font:400 40px/1.1 '${f}';margin-top:22px;letter-spacing:-.02em">Good evening.</div>
    <div style="position:relative;margin-top:8px;font:400 16px 'Onest';opacity:.85">Група до 8 · 19:00 за київським часом</div>
    <div style="position:relative;margin-top:22px;font:600 16px 'Onest';border-bottom:1px solid ${c.fg};display:inline-block;padding-bottom:3px">До розкладу →</div></div>`;
  el.innerHTML = `<div style="font:500 14px/30px 'JetBrains Mono',monospace;letter-spacing:.14em;padding-top:6px;opacity:.85">ТРИ НАСТРОЇ · ОДИН КАРКАС (приклад)</div><div style="display:flex;gap:20px;height:236px">${kids}${teens}${adults}</div>`;
}
