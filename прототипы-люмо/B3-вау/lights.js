/* LUMOSCHOOL · B3 · второй экран: «Ліхтарик» + «Три настрої».
   Текст карток видно лише в колі світла Люмо (CSS-маска), коло йде за курсором/пальцем,
   а без руху — само обходить картки. Перемикач «діти / підлітки / дорослі» міняє колір ядра,
   темп дихання і тон репліки (змінні CSS на секції). «Менше руху» — усе видно одразу. */
(() => {
'use strict';
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const sec = $('#lights'); if (!sec) return;
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const field = $('#field'), orb = $('#orb'), lit = $('#cardsLit'), say = $('#lSay');
const cards = $$('.card', lit);
const SAY = {
  kid: 'Привіт! Світімо разом: ти показуєш, я підсвічую.',
  teen: 'Окей, без цирку. Говоримо як є, я просто світитиму поруч.',
  adult: 'Спокійно і по ділу. Я тут, щоб підсвітити, а не відволікати.'
};
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

let W = 0, H = 0, R = 250, boxes = [], pts = [], patI = 0, patAt = 0, lastInput = -1e9;
const tgt = { x: 0, y: 0 };
let age = 'kid', dip = 0;
function setAge(a, first) {
  age = a; sec.dataset.age = a; say.textContent = SAY[a];
  $$('#age button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.age === a)));
  if (!first && !RM) { dip = 1; const i = ['kid', 'teen', 'adult'].indexOf(a); if (pts[i]) { patI = i; patAt = performance.now(); tgt.x = pts[i].x; tgt.y = pts[i].y; lastInput = performance.now() + 1400; } }
}
$$('#age button').forEach(b => b.addEventListener('click', () => setAge(b.dataset.age)));
setAge('kid', true);

const showAll = $('#showAll');
showAll.addEventListener('click', () => { const on = !sec.classList.contains('rm'); sec.classList.toggle('rm', on); showAll.setAttribute('aria-pressed', String(on)); showAll.textContent = on ? 'Повернути світло' : 'Показати всі картки'; });
if (RM) {
  sec.classList.add('rm'); showAll.hidden = true;
  $('#lLead').textContent = 'Картки видно одразу, без ефектів. Перемикач міняє настрій Люмо.';
  return;
}

/* ---- стан світла ---- */
const pos = { x: -999, y: -999 };
let gate = 0, gateOn = false, vis = false, raf = 0, last = 0, started = false, shown = { x: 1e9, y: 1e9, r: -1 };
function measure() {
  const fr = field.getBoundingClientRect(); W = fr.width; H = fr.height;
  R = parseFloat(getComputedStyle(sec).getPropertyValue('--r')) || 250;
  boxes = cards.map(c => { const r = c.getBoundingClientRect(); return { l: r.left - fr.left, t: r.top - fr.top, r: r.right - fr.left, b: r.bottom - fr.top }; });
  pts = cards.map(c => { const r = c.getBoundingClientRect(); return { x: r.left - fr.left + r.width * .5, y: r.top - fr.top + r.height * .42 }; });
  if (!started) { started = true; pos.x = tgt.x = pts[0] ? pts[0].x : W / 2; pos.y = tgt.y = pts[0] ? pts[0].y : H / 2; }
}
function local(e) { const fr = field.getBoundingClientRect(); return { x: clamp(e.clientX - fr.left, 0, fr.width), y: clamp(e.clientY - fr.top, 0, fr.height) }; }
function onMove(e) {
  const p = local(e); if (e.pointerType === 'touch') p.y = Math.max(0, p.y - 70); tgt.x = p.x; tgt.y = p.y; lastInput = performance.now();
  // над карткою світло злегка притягується до її центру — текст читається цілком
  const fr = field.getBoundingClientRect();
  cards.forEach((c, i) => { const r = c.getBoundingClientRect(); if (e.clientX > r.left && e.clientX < r.right && e.clientY > r.top && e.clientY < r.bottom && pts[i]) { tgt.x = p.x + (pts[i].x - p.x) * .4; tgt.y = p.y + (pts[i].y - p.y) * .4; } });
}
sec.addEventListener('pointermove', e => { const fr = field.getBoundingClientRect(); if (e.clientY > fr.top - 120 && e.clientY < fr.bottom + 120) onMove(e); }, { passive: true });
field.addEventListener('pointerdown', onMove, { passive: true });
field.addEventListener('pointerup', () => { lastInput = performance.now(); }, { passive: true });
addEventListener('resize', () => { measure(); });

function frame(now) {
  raf = vis ? requestAnimationFrame(frame) : 0;
  const dt = Math.min(.05, (now - last) / 1000); last = now;
  // автообхід: когось не торкаються — Люмо сам іде від картки до картки
  if (now - lastInput > 1900 && pts.length) {
    if (now - patAt > 2300) { patAt = now; patI = (patI + 1) % pts.length; }
    tgt.x = pts[patI].x; tgt.y = pts[patI].y;
  }
  const k = 1 - Math.exp(-dt / .11);
  pos.x += (tgt.x - pos.x) * k; pos.y += (tgt.y - pos.y) * k;
  if (gateOn) gate = Math.min(1, gate + dt / .9);
  dip = Math.max(0, dip - dt / .7);
  const ease = 1 - Math.pow(1 - gate, 3);
  const r = R * ease * (1 - .88 * Math.sin(Math.min(1, dip) * Math.PI / 1) * (dip > 0 ? 1 : 0));
  if (Math.abs(pos.x - shown.x) > .15 || Math.abs(pos.y - shown.y) > .15 || Math.abs(r - shown.r) > .3) {
    shown = { x: pos.x, y: pos.y, r };
    field.style.setProperty('--mx', pos.x.toFixed(1) + 'px'); field.style.setProperty('--my', pos.y.toFixed(1) + 'px'); field.style.setProperty('--rr', Math.max(0, r).toFixed(1) + 'px'); field.style.setProperty('--sc', (Math.max(0, r) / R).toFixed(3));
    const bob = Math.sin(now / 700) * 4, mob = W < 700, ox = mob ? 105 : 150, oy = mob ? -96 : -50;
    // сусідні картки гаснуть, поки світло далеко від них (без «рваних» фрагментів)
    boxes.forEach((b, i) => { const dx = Math.max(b.l - pos.x, 0, pos.x - b.r), dy = Math.max(b.t - pos.y, 0, pos.y - b.b); const d = Math.hypot(dx, dy); cards[i].style.opacity = clamp(1 - d / (R * .5), 0, 1).toFixed(2); });
    orb.style.transform = `translate(${(pos.x + ox).toFixed(1)}px, ${(pos.y + oy + bob).toFixed(1)}px) scale(${(.6 + .4 * ease).toFixed(3)})`;
    orb.style.opacity = ease.toFixed(2);
  }
}
new IntersectionObserver(es => {
  for (const e of es) {
    vis = e.isIntersecting;
    if (vis) { measure(); if (e.intersectionRatio > .25) gateOn = true; if (!raf) { last = performance.now(); raf = requestAnimationFrame(frame); } }
  }
}, { threshold: [0, .25] }).observe(sec);
measure();
if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);
window.__lights = { setAge, get age() { return age; } };
})();
