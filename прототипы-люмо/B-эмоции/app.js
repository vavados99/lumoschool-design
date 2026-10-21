/* LUMOSCHOOL · прототип Б «Емоції на дотик». Ванільний JS, без збірки. */
(() => {
'use strict';
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const FINE = matchMedia('(pointer: fine)').matches;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

/* ---------- тексти: реально перекладаємо лише uk / pl / en ---------- */
const UI = {
  uk: { h1a:'Англійська', h1b:'з другом,', h1c:'що світиться', nameLabel:'Назви себе, як хочеш', namePh:"ім’я або прізвисько", nameBtn:'Привітатись',
        cue:'Прокрути — він помітить', thKicker:'Поведінка при прокрутці', thTitle:'Гортай — і він живе поруч',
        st0:'Підводить погляд', st1:'Думає разом із тобою', st2:'Підстрибує від радості', st3:'Тихо засинає на паузі' },
  pl: { h1a:'Angielski', h1b:'z przyjacielem,', h1c:'który świeci', nameLabel:'Przedstaw się, jak chcesz', namePh:'imię lub pseudonim', nameBtn:'Przywitaj się',
        cue:'Przewiń — on to zauważy', thKicker:'Zachowanie przy przewijaniu', thTitle:'Przewijaj — a on jest obok',
        st0:'Unosi wzrok', st1:'Myśli razem z tobą', st2:'Podskakuje z radości', st3:'Cicho zasypia na pauzie' },
  en: { h1a:'English', h1b:'with a friend', h1c:'who glows', nameLabel:'Call yourself whatever you like', namePh:'name or nickname', nameBtn:'Say hi',
        cue:'Scroll — he will notice', thKicker:'How he behaves on scroll', thTitle:'Keep scrolling — he lives right here',
        st0:'Looks up', st1:'Thinks along with you', st2:'Jumps for joy', st3:'Quietly dozes off on a pause' }
};
const LINES = {
  uk: {
    hello:['Привіт! Я Люмо. Можна мене торкнутись.','О, привіт! Я тут — світитимусь для тебе.'],
    touch:['Привіт-привіт!','Ой, приємно! Тепло від твоєї руки.','Ага, це я! Ти мене помітив.','О-го, взмах у відповідь!'],
    hover:['Ти поруч — я бачу.','Підійшов ближче? Мені це подобається.'],
    tickle:['Хі-хі! Лоскотно!','Ой-ой, я зараз розсвічусь від сміху!'],
    celebrate:['Ура! Так весело, що підстрибнув!','Є! Святкуємо — просто тому, що нам добре.'],
    curious:['Ммм, а що там угорі?','Дивись-но, там щось світиться.'],
    think:['Гм… слухаю, як ти друкуєш.','Думаю, як тебе назвати. Не поспішай.'],
    listen:['Напиши як хочеш — навіть вигадане ім’я.'],
    named:['Привіт, {n}! Дуже радий знайомству.','{n} — звучить гарно! Привіт!'],
    noname:['Можна й без імені — я просто світитимусь поруч.'],
    sleepy:['Я трошки задрімав… торкнись — прокинусь.'],
    wake:['О, я тут! Радий, що ти повернувся.','Ммм… о! Привіт знову.'],
    back:['З поверненням! Я нікуди не йшов.'],
    fast:['Оу-у, повільніше — я ледь тримаюсь!','Ух, вітер! Тримаюсь за повітря.'],
    stub:['Цією мовою я поки лише вчусь. Розмовляю трьома: uk, pl, en.'],
    lang:['Добре, говоримо українською!'],
    steps:['Ти почав гортати — я підвів погляд.','Гортаєш повільно — я думаю разом із тобою.','Дійшли до цікавого — я підстрибую від радості.','Ти зупинився — я тихо задрімаю.']
  },
  pl: {
    hello:['Cześć! Jestem Lumo. Możesz mnie dotknąć.','O, cześć! Jestem tu — będę świecić dla ciebie.'],
    touch:['Cześć-cześć!','Ojej, miło! Ciepło od twojej ręki.','Aha, to ja! Zauważyłeś mnie.','O, machnięcie na powitanie!'],
    hover:['Jesteś blisko — widzę cię.','Podszedłeś bliżej? Lubię to.'],
    tickle:['Hi-hi! Łaskocze!','Oj-oj, zaraz rozbłysnę ze śmiechu!'],
    celebrate:['Hura! Tak wesoło, że podskoczyłem!','Jest! Świętujemy — bo nam dobrze.'],
    curious:['Mmm, co tam jest u góry?','Patrz, coś tam świeci.'],
    think:['Hm… słucham, jak piszesz.','Myślę, jak cię nazwać. Nie spiesz się.'],
    listen:['Napisz, jak chcesz — nawet zmyślone imię.'],
    named:['Cześć, {n}! Bardzo miło cię poznać.','{n} — ładnie brzmi! Cześć!'],
    noname:['Można i bez imienia — po prostu będę świecić obok.'],
    sleepy:['Chwilkę przysnąłem… dotknij — obudzę się.'],
    wake:['O, jestem! Cieszę się, że wróciłeś.','Mmm… o! Cześć znowu.'],
    back:['Witaj z powrotem! Nigdzie nie poszedłem.'],
    fast:['Oj, wolniej — ledwo się trzymam!','Uf, wiatr! Trzymam się powietrza.'],
    stub:['Tego języka dopiero się uczę. Mówię w trzech: uk, pl, en.'],
    lang:['Dobrze, mówimy po polsku!'],
    steps:['Zacząłeś przewijać — uniosłem wzrok.','Przewijasz powoli — myślę razem z tobą.','Doszliśmy do ciekawego — podskakuję z radości.','Zatrzymałeś się — cicho zdrzemnę się.']
  },
  en: {
    hello:["Hi! I'm Lumo. You can touch me.","Oh, hello! I'm here — glowing just for you."],
    touch:['Hi-hi!','Aw, nice! Your hand is warm.',"Yep, that's me! You noticed.",'Oh, a wave back!'],
    hover:["You're close — I see you.",'Came closer? I like that.'],
    tickle:['Hee-hee! That tickles!',"Oh-oh, I'm about to glow from giggling!"],
    celebrate:['Yay! So much fun I jumped!',"Woo! We're celebrating — just because it feels good."],
    curious:["Mmm, what's up there?",'Look, something is shining up there.'],
    think:["Hm… I'm listening to you type.","Thinking what to call you. Take your time."],
    listen:['Write whatever you like — even an invented name.'],
    named:["Hi, {n}! So glad to meet you.",'{n} — that sounds lovely! Hi!'],
    noname:['No name is fine too — I will just glow next to you.'],
    sleepy:["I dozed off a little… touch me — I'll wake up."],
    wake:["Oh, I'm here! Glad you're back.",'Mmm… oh! Hi again.'],
    back:["Welcome back! I didn't go anywhere."],
    fast:['Whoa, slower — I can barely hold on!',"Phew, wind! I'm holding on to the air."],
    stub:["I'm still learning this language. I speak three: uk, pl, en."],
    lang:["Okay, we're speaking English!"],
    steps:["You started scrolling — I looked up.","You scroll slowly — I think along with you.","We reached something fun — I'm jumping for joy.","You stopped — I'll quietly doze off."]
  }
};
let lang = 'uk';
const L = () => LINES[LINES[lang] ? lang : 'uk'];
const U = () => UI[UI[lang] ? lang : 'uk'];

/* ---------- Люмо ---------- */
const POSES = ['wave', 'curious', 'think', 'jump'];
const STATE_POSE = { joy:'wave', curious:'curious', think:'think', celebrate:'jump' };
const sparkDots = Array.from({ length: 12 }, (_, i) => {
  const a = (i / 12) * Math.PI * 2 + .3, r = 130 + (i % 3) * 40;
  return `<b style="--x:${Math.cos(a) * r | 0}px;--y:${Math.sin(a) * r * .8 | 0}px;--d:${(i % 4) * 70}ms"></b>`;
}).join('');

function makeLumo(host, bubbleEl, { follow = true } = {}) {
  host.innerHTML = `
  <div class="lumo" data-state="idle" role="img" aria-label="Люмо — жива крапля світла" tabindex="-1">
    <div class="lumo-float">
      <div class="lumo-shadow"></div>
      ${POSES.map(p => `<img class="pose pose-${p}" src="assets/pose-${p}.webp" alt="" draggable="false" decoding="async">`).join('')}
      <div class="layered"><div class="body">
        <img class="art" src="assets/layer-body.webp" alt="" draggable="false" fetchpriority="high">
        <img class="eye l" src="assets/layer-eye.webp" alt="" draggable="false">
        <img class="eye r" src="assets/layer-eye.webp" alt="" draggable="false">
        <img class="smile" src="assets/layer-smile.webp" alt="" draggable="false">
      </div></div>
      <div class="zzz" aria-hidden="true"><i>z</i><i>z</i><i>Z</i></div>
      <div class="sparks" aria-hidden="true">${sparkDots}</div>
    </div>
  </div>`;
  const root = $('.lumo', host), layered = $('.layered', root);
  const bt = $('.bubble-text', bubbleEl);
  let state = 'idle', backTimer = 0, bubTimer = 0, lastLine = '';
  const T = [];
  const later = (fn, ms) => { const t = setTimeout(fn, ms); T.push(t); return t; };

  function setState(s, holdMs) {
    state = s; root.dataset.state = s;
    clearTimeout(backTimer);
    if (holdMs) backTimer = setTimeout(() => { if (state === s) setState('idle'); }, holdMs);
    api.onState && api.onState(s);
  }
  function say(text, ms = 6500) {
    if (!text) return;
    lastLine = text; bt.textContent = text;
    bubbleEl.classList.remove('on'); void bubbleEl.offsetWidth; bubbleEl.classList.add('on');
    clearTimeout(bubTimer);
    if (ms) bubTimer = setTimeout(() => bubbleEl.classList.remove('on'), ms);
  }
  function pick(key, vars) {
    const arr = L()[key]; let t = arr[Math.random() * arr.length | 0];
    if (arr.length > 1 && t === lastLine) t = arr[(arr.indexOf(t) + 1) % arr.length];
    if (vars) for (const k in vars) t = t.replace('{' + k + '}', vars[k]);
    return t;
  }
  function look(x, y) { layered.style.setProperty('--ex', x + 'px'); layered.style.setProperty('--ey', y + 'px'); }
  function anim(cls, ms) { root.classList.remove(cls); void root.offsetWidth; root.classList.add(cls); later(() => root.classList.remove(cls), ms); }
  function blinkLoop() {
    if (RM) return;
    const go = () => {
      if (state === 'idle' || state === 'listen') {
        layered.classList.add('blink'); later(() => layered.classList.remove('blink'), 150);
        if (Math.random() < .2) { later(() => layered.classList.add('blink'), 260); later(() => layered.classList.remove('blink'), 410); }
      }
      later(go, 3800 + Math.random() * 2400);
    };
    later(go, 2200);
  }
  function wink() { if (RM) return; layered.classList.add('wink'); later(() => layered.classList.remove('wink'), 420); }
  blinkLoop();

  const api = { root, setState, say, pick, look, anim, wink, get state() { return state; }, onState: null };
  return api;
}

/* ---------- ГЕРОЙ ---------- */
const hero = $('#hero');
const lumo = makeLumo($('#lumoHero'), $('#bubble'));
const root = lumo.root;
let lastAct = Date.now();
let touchTimes = [];
const poke = () => { lastAct = Date.now(); if (lumo.state === 'sleepy') wake(); };
function wake() { lumo.setState('joy', 2600); lumo.say(lumo.pick('wake')); }

/* привітання: взмах, потім спокій */
setTimeout(() => { lumo.setState('joy', 3000); lumo.say(lumo.pick('hello'), 7000); }, 500);

/* ---- наведення / дотик ---- */
let hoverCool = 0;
root.addEventListener('pointerenter', e => {
  if (e.pointerType === 'touch') return;
  const was = lumo.state === 'sleepy'; poke();
  if (was) return;
  lumo.anim('nudge', 520); lumo.wink();
  if (Date.now() - hoverCool > 9000) { hoverCool = Date.now(); lumo.say(lumo.pick('hover'), 4000); }
});
root.addEventListener('pointerdown', () => {
  const was = lumo.state === 'sleepy'; poke(); if (was) return;
  const now = Date.now();
  touchTimes = touchTimes.filter(t => now - t < 6000); touchTimes.push(now);
  if (touchTimes.length >= 4) { touchTimes = []; lumo.setState('celebrate', 2400); lumo.say(lumo.pick('celebrate')); }
  else { lumo.setState('joy', 2600); lumo.anim('nudge', 520); lumo.say(lumo.pick('touch'), 4500); }
});
/* «лоскіт»: швидке водіння по Люмо */
let sweep = { d: 0, t: 0, x: 0, y: 0 };
root.addEventListener('pointermove', e => {
  const now = performance.now();
  if (now - sweep.t > 1100) sweep = { d: 0, t: now, x: e.clientX, y: e.clientY };
  sweep.d += Math.hypot(e.clientX - sweep.x, e.clientY - sweep.y); sweep.x = e.clientX; sweep.y = e.clientY;
  if (sweep.d > 900 && lumo.state !== 'sleepy') {
    sweep = { d: 0, t: now, x: e.clientX, y: e.clientY };
    lumo.setState('joy', 1800); lumo.anim('giggle', 900); lumo.say(lumo.pick('tickle'), 4200);
  }
});

/* ---- погляд і нахил за курсором (2.5D) ---- */
if (FINE && !RM) {
  addEventListener('pointermove', e => {
    lastAct = Date.now();
    if (lumo.state === 'sleepy') return;
    const r = root.getBoundingClientRect();
    const cx = r.left + r.width / 2, cy = r.top + r.height * .45;
    const dx = e.clientX - cx, dy = e.clientY - cy, d = Math.hypot(dx, dy) || 1, reach = Math.min(1, d / 260);
    lumo.look(((dx / d) * 9 * reach).toFixed(1), ((dy / d) * 7 * reach).toFixed(1));
    root.style.setProperty('--tx', (clamp(dx / innerWidth, -.5, .5) * 22).toFixed(1) + 'px');
    root.style.setProperty('--ty', (clamp(dy / innerHeight, -.5, .5) * 14).toFixed(1) + 'px');
    root.style.setProperty('--rot', (clamp(dx / innerWidth, -.5, .5) * 3).toFixed(2) + 'deg');
  }, { passive: true });
}

/* ---- поле імені ---- */
const form = $('#nameForm'), input = $('#guestName');
let typeTimer = 0;
input.addEventListener('focus', () => {
  poke();
  if (lumo.state === 'idle') { lumo.setState('listen'); lumo.look(0, 9); lumo.say(lumo.pick('listen'), 6000); }
});
input.addEventListener('blur', () => { if (lumo.state === 'listen') lumo.setState('idle'); lumo.look(0, 0); });
input.addEventListener('input', () => {
  poke();
  if (!input.value) { lumo.setState('listen'); return; }
  if (lumo.state !== 'think') { lumo.setState('think'); lumo.say(lumo.pick('think'), 5000); }
  clearTimeout(typeTimer);
  typeTimer = setTimeout(() => { if (lumo.state === 'think') lumo.setState(document.activeElement === input ? 'listen' : 'idle'); }, 1900);
});
form.addEventListener('submit', e => {
  e.preventDefault(); poke(); clearTimeout(typeTimer);
  const n = input.value.trim().replace(/\s+/g, ' ').slice(0, 24);
  if (n) { lumo.setState('celebrate', 2600); lumo.say(lumo.pick('named', { n }), 7500); }
  else { lumo.setState('joy', 2600); lumo.say(lumo.pick('noname'), 6000); }
});

/* ---- мова ---- */
function applyLang(code) {
  const wasStub = !UI[code];
  lang = code; document.documentElement.lang = code;
  const dict = U();
  $$('[data-i18n]').forEach(el => { const k = el.dataset.i18n; if (dict[k]) { const s = el.querySelector('span'); (el.tagName === 'A' && s ? s : el).textContent = dict[k]; } });
  $$('[data-i18n-ph]').forEach(el => el.placeholder = dict[el.dataset.i18nPh]);
  $$('.lang button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.lang === code)));
  return wasStub;
}
$$('.lang button').forEach(b => b.addEventListener('click', () => {
  poke();
  const stub = applyLang(b.dataset.lang);
  lumo.setState('joy', 2600);
  lumo.say(stub ? LINES.uk.stub[0] : lumo.pick('lang'), 6500);
}));

/* ---- прокрутка героя ---- */
let lastY = scrollY, lastT = performance.now(), fastCool = 0, curiousDone = false, raf = 0;
function onScroll() {
  if (raf) return; raf = requestAnimationFrame(() => {
    raf = 0;
    const y = scrollY, now = performance.now();
    const p = clamp(y / innerHeight, 0, 1);
    if (!RM) hero.style.setProperty('--p', p.toFixed(3));
    const v = (y - lastY) / Math.max(1, now - lastT) * 1000; // px/с
    lastY = y; lastT = now;
    if (y < innerHeight * .8) {
      lastAct = Date.now(); if (lumo.state === 'sleepy') wake();
      if (Math.abs(v) > 2600 && now - fastCool > 5000 && !RM) {
        fastCool = now; root.style.setProperty('--lean', (v > 0 ? -7 : 7) + 'deg'); lumo.anim('swoosh', 800); lumo.say(lumo.pick('fast'), 3800);
      } else if (!curiousDone && y > 40 && Math.abs(v) < 1800 && lumo.state === 'idle') {
        curiousDone = true; lumo.setState('curious', 3000); lumo.say(lumo.pick('curious'), 4500);
      }
    }
    theatreUpdate();
  });
}
addEventListener('scroll', onScroll, { passive: true });
addEventListener('resize', onScroll);

/* ---- пауза → сонний; повернення на вкладку ---- */
setInterval(() => {
  const idle = Date.now() - lastAct;
  if (scrollY > innerHeight * .8) return;
  if (idle > 16000 && lumo.state !== 'sleepy' && lumo.state !== 'think') {
    lumo.setState('sleepy'); lumo.look(0, 0); lumo.say(lumo.pick('sleepy'), 0);
  }
}, 1000);
let hiddenAt = 0;
document.addEventListener('visibilitychange', () => {
  if (document.hidden) hiddenAt = Date.now();
  else if (hiddenAt && Date.now() - hiddenAt > 15000) { lastAct = Date.now(); lumo.setState('joy', 2800); lumo.say(lumo.pick('back'), 5000); }
});

/* ---------- ТЕАТР ПРОКРУТКИ ---------- */
const theatre = $('#theatre');
const lumo2 = makeLumo($('#lumoTheatre'), $('#bubble2'));
const steps = $$('.step');
const STEP_STATE = [['curious', 0], ['think', 0], ['celebrate', 0], ['sleepy', 0]];
let curStep = -1;
function theatreUpdate() {
  const r = theatre.getBoundingClientRect();
  const total = r.height - innerHeight;
  const tp = clamp(-r.top / total, 0, 1);
  theatre.style.setProperty('--tp', tp.toFixed(3));
  $('#thBar').parentElement.parentElement.style.setProperty('--tp', tp.toFixed(3));
  if (r.top > innerHeight * .9 || r.bottom < 0) return;
  const idx = clamp(Math.floor(tp * 4), 0, 3);
  if (idx !== curStep) {
    curStep = idx;
    steps.forEach((s, i) => s.classList.toggle('on', i === idx));
    lumo2.setState(STEP_STATE[idx][0]);
    lumo2.say(LINES[LINES[lang] ? lang : 'uk'].steps[idx], 0);
    if (idx === 3 && !RM) lumo2.look(0, 0);
  }
  /* погляд за напрямком прокрутки у кроках 0–1 (шарова капля) */
  if (!RM) lumo2.look(0, ((tp * 4) % 1 - .5) * -8);
}
steps[0].classList.remove('on');
$('#lumoTheatre .lumo').addEventListener('pointerdown', () => { const s = lumo2.state; lumo2.anim('nudge', 520); if (s === 'sleepy') { lumo2.setState('joy', 2400); lumo2.say(lumo2.pick('wake'), 4000); } });

/* відладка/знімки */
window.__lumo = { hero: lumo, theatre: lumo2, applyLang, say: (k) => lumo.say(lumo.pick(k)), theatreUpdate };
onScroll();
})();
