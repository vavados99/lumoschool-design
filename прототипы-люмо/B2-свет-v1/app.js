/* LUMOSCHOOL · B2 «Світло». Ванільний JS без збірки.
   Люмо — вектор (SVG) з власним «ригом»: очі, повіки, брови, рот, руки, стиснення-розтягнення, дихання.
   Усі параметри плавно (300–500 мс) тягнуться до цілі настрою; світло сцени і літери заголовка рахуються від позиції ядра. */
(() => {
'use strict';
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const rnd = (a, b) => a + Math.random() * (b - a);
const hero = $('#hero');

/* ================= ТЕКСТИ ================= */
const UI = {
  uk: { code:'UA', kicker:'Англійська', a:'з другом,', b:'що світиться', lead:'Онлайн-уроки для дітей, підлітків і дорослих.', hint:'Назви себе — і Люмо привітається.', label:'Назви себе, як хочеш', ph:'ім’я або прізвисько', btn:'Привітатись', cue:'Прокрути — він помітить', greet:'Привіт, {n}!', change:'Змінити ім’я', mood:'Настрій', moods:['Спокій','Радість','Цікавість','Роздум','Свято','Сон'], alt:'Люмо — живий друг, що світиться', listLabel:'Мова сайту' },
  pl: { code:'PL', kicker:'Angielski', a:'z przyjacielem,', b:'który świeci', lead:'Lekcje online dla dzieci, nastolatków i dorosłych.', hint:'Podaj imię — Lumo się przywita.', label:'Przedstaw się, jak chcesz', ph:'imię lub pseudonim', btn:'Przywitaj się', cue:'Przewiń — on to zauważy', greet:'Cześć, {n}!', change:'Zmień imię', mood:'Nastrój', moods:['Spokój','Radość','Ciekawość','Namysł','Święto','Sen'], alt:'Lumo — żywy przyjaciel, który świeci', listLabel:'Język strony' },
  en: { code:'EN', kicker:'English', a:'with a friend', b:'who glows', lead:'Online lessons for kids, teens and adults.', hint:'Tell us your name — Lumo will say hi.', label:'Call yourself whatever you like', ph:'name or nickname', btn:'Say hi', cue:'Scroll — he will notice', greet:'Hi, {n}!', change:'Change name', mood:'Mood', moods:['Calm','Joy','Curious','Thinking','Party','Sleep'], alt:'Lumo — a living friend who glows', listLabel:'Site language' },
  de: { code:'DE', kicker:'Englisch', a:'mit einem Freund,', b:'der leuchtet', lead:'Online-Unterricht für Kinder, Jugendliche und Erwachsene.', hint:'Nenn deinen Namen — Lumo sagt Hallo.', label:'Nenn dich, wie du willst', ph:'Name oder Spitzname', btn:'Hallo sagen', cue:'Scrolle — er merkt es', greet:'Hallo, {n}!', change:'Namen ändern', mood:'Stimmung', moods:['Ruhe','Freude','Neugier','Nachdenken','Fest','Schlaf'], alt:'Lumo — ein lebendiger Freund, der leuchtet', listLabel:'Sprache' },
  cs: { code:'CS', kicker:'Angličtina', a:'s kamarádem,', b:'který svítí', lead:'Online lekce pro děti, teenagery i dospělé.', hint:'Řekni své jméno — Lumo tě pozdraví.', label:'Představ se, jak chceš', ph:'jméno nebo přezdívka', btn:'Pozdravit', cue:'Rolluj — všimne si', greet:'Ahoj, {n}!', change:'Změnit jméno', mood:'Nálada', moods:['Klid','Radost','Zvědavost','Přemýšlení','Oslava','Spánek'], alt:'Lumo — živý kamarád, který svítí', listLabel:'Jazyk stránky' },
  ru: { code:'RU', kicker:'Английский', a:'с другом,', b:'который светится', lead:'Онлайн-уроки для детей, подростков и взрослых.', hint:'Назови себя — и Люмо поздоровается.', label:'Назови себя, как хочешь', ph:'имя или прозвище', btn:'Поздороваться', cue:'Прокрути — он заметит', greet:'Привет, {n}!', change:'Сменить имя', mood:'Настроение', moods:['Покой','Радость','Любопытство','Раздумье','Праздник','Сон'], alt:'Люмо — живой друг, который светится', listLabel:'Язык сайта' }
};
const LINES = {
  uk: { hello:'Привіт! Я Люмо. Можна мене торкнутись.', joy:'Ой, приємно! Тепло від твоєї руки.', curious:'Ммм, а що там угорі?', think:'Гм… дай подумати.', typing:'Слухаю, як ти друкуєш.', sleepy:'Я трошки задрімав… торкнись — прокинусь.', wake:'О, я тут! Радий, що ти повернувся.', named:'Привіт, {n}! Дуже радий знайомству.', noname:'Можна й без імені — я просто світитимусь поруч.', celebrate:'Ура! Так весело, що підстрибнув!' },
  pl: { hello:'Cześć! Jestem Lumo. Możesz mnie dotknąć.', joy:'Ojej, miło! Ciepło od twojej ręki.', curious:'Mmm, co tam jest u góry?', think:'Hm… daj mi pomyśleć.', typing:'Słucham, jak piszesz.', sleepy:'Chwilkę przysnąłem… dotknij — obudzę się.', wake:'O, jestem! Cieszę się, że wróciłeś.', named:'Cześć, {n}! Bardzo miło cię poznać.', noname:'Można i bez imienia — po prostu będę świecić obok.', celebrate:'Hura! Tak wesoło, że podskoczyłem!' },
  en: { hello:"Hi! I'm Lumo. You can touch me.", joy:'Aw, nice! Your hand is warm.', curious:"Mmm, what's up there?", think:'Hm… let me think.', typing:"I'm listening to you type.", sleepy:"I dozed off a little… touch me — I'll wake up.", wake:"Oh, I'm here! Glad you're back.", named:'Hi, {n}! So glad to meet you.', noname:'No name is fine too — I will just glow next to you.', celebrate:'Yay! So much fun I jumped!' },
  de: { hello:'Hallo! Ich bin Lumo. Du darfst mich anfassen.', joy:'Oh, wie schön! Deine Hand ist warm.', curious:'Mmm, was ist da oben?', think:'Hm… lass mich überlegen.', typing:'Ich höre dir beim Tippen zu.', sleepy:'Ich bin kurz eingenickt… tipp mich an.', wake:'Oh, ich bin da! Schön, dass du zurück bist.', named:'Hallo, {n}! Freut mich sehr.', noname:'Auch ohne Namen — ich leuchte einfach neben dir.', celebrate:'Juhu! So viel Freude, ich musste hüpfen!' },
  cs: { hello:'Ahoj! Jsem Lumo. Můžeš se mě dotknout.', joy:'Jé, to je příjemné! Máš teplou ruku.', curious:'Mmm, co je tam nahoře?', think:'Hm… nech mě přemýšlet.', typing:'Poslouchám, jak píšeš.', sleepy:'Trochu jsem usnul… dotkni se mě.', wake:'Jé, jsem tu! Rád tě zase vidím.', named:'Ahoj, {n}! Moc mě těší.', noname:'I bez jména to jde — budu prostě svítit vedle tebe.', celebrate:'Hurá! Tolik radosti, že jsem vyskočil!' },
  ru: { hello:'Привет! Я Люмо. Меня можно потрогать.', joy:'Ой, приятно! Рука у тебя тёплая.', curious:'Ммм, а что там наверху?', think:'Гм… дай подумать.', typing:'Слушаю, как ты печатаешь.', sleepy:'Я немножко задремал… коснись — проснусь.', wake:'О, я тут! Рад, что ты вернулся.', named:'Привет, {n}! Очень рад знакомству.', noname:'Можно и без имени — я просто посвечу рядом.', celebrate:'Ура! Так весело, что подпрыгнул!' }
};
let lang = 'uk';
const U = () => UI[lang], L = () => LINES[lang];

/* ================= ЗАГОЛОВОК: літери для підсвічування ================= */
const h1a = $('#h1a'), h1b = $('#h1b'), h1 = $('#h1');
let letters = [];            // {el, x, y}
function split(el, text) {
  el.textContent = '';
  for (const word of text.split(' ')) {
    if (el.childNodes.length) el.append(' ');
    const w = document.createElement('span'); w.className = 'w';
    for (const c of word) { const s = document.createElement('span'); s.className = 'ch'; s.textContent = c; w.append(s); }
    el.append(w);
  }
}
function fitH1() {          // якщо рядок довший за колонку — трохи зменшуємо кегль (для RU/DE)
  h1.style.fontSize = '';
  const mob = matchMedia('(max-width:820px)').matches, hl = $('.headline').getBoundingClientRect(), lr = $('#lumo').getBoundingClientRect();
  const avail = mob ? $('.headline').clientWidth : lr.left + lr.width * .1 - hl.left - 8;
  const w = Math.max(h1a.scrollWidth, h1b.scrollWidth);
  if (w > avail) h1.style.fontSize = (parseFloat(getComputedStyle(h1).fontSize) * avail / w * .98).toFixed(1) + 'px';
}
function cacheLetters() {
  const hr = hero.getBoundingClientRect();
  letters = $$('.ch', h1).map(el => { const r = el.getBoundingClientRect(); return { el, x: r.left + r.width / 2 - hr.left, y: r.top + r.height / 2 - hr.top, glow: !!el.closest('.ln-glow'), l: -1 }; });
}
function applyText() {
  const u = U();
  document.documentElement.lang = lang;
  split(h1a, u.a); split(h1b, u.b);
  h1.setAttribute('aria-label', u.a + ' ' + u.b);
  $('#kicker').textContent = u.kicker; $('#leadMain').textContent = nb(u.lead); $('#leadHint').textContent = nb(u.hint); $('#leadHint').hidden = !!guest;
  $('#nameLabel').textContent = u.label; $('#guestName').placeholder = u.ph; $('#nameBtn').textContent = u.btn;
  $('#cueT').textContent = u.cue; $('#changeName').textContent = u.change; $('#moodsL').textContent = u.mood;
  $$('#moods button').forEach((b, i) => b.textContent = u.moods[i]);
  $('#langCode').textContent = u.code; $('#lumo').setAttribute('aria-label', u.alt);
  $('#langBtn').setAttribute('aria-label', u.listLabel); $('#langList').setAttribute('aria-label', u.listLabel);
  if (guest) $('#greetT').innerHTML = greetHTML();
  fitH1(); cacheLetters();
}

/* ================= РИГ ЛЮМО ================= */
const g = id => document.getElementById(id);
const el = { rig:g('rig'), squash:g('squash'), tilt:g('tilt'), face:g('face'), armL:g('armL'), armR:g('armR'),
  browL:g('browL'), browR:g('browR'), eyeL:g('eyeL'), eyeR:g('eyeR'), eyeLin:g('eyeLin'), eyeRin:g('eyeRin'), lidL:g('lidL'), lidR:g('lidR'),
  happyL:g('happyL'), happyR:g('happyR'), mouthFill:g('mouthFill'), mouthLine:g('mouthLine'), mouthClip:g('mouthClipPath'), tongue:g('tongue'), mouthG:g('mouthG'),
  coreG:g('coreG'), coreDisc:g('coreDisc'), innerGlow:g('innerGlow'), innerGlow2:g('innerGlow2'), spark:g('spark'), zzz:g('zzz'),
  svg:g('lumo'), light:g('light'), pool:g('pool'), contact:g('contact') };
const EYE = { L:[154, 262], R:[252, 262] };

/* Цілі настроїв. gx/gy = null → дивиться за курсором. */
const E = {
  idle:      { lidL:.05, lidR:.05, tiltL:0, tiltR:0, happy:0, gx:null, gy:null, pupil:1,   mw:26, mc:26, mo:0,   mt:0,  ms:0,   bLy:0,  bRy:0,  bLa:0,  bRa:0,  tilt:0,  sy:1,    armL:34, armR:10, core:.85, spark:0, zzz:0, lp:1,   lift:0 },
  joy:       { lidL:.12, lidR:.12, tiltL:0, tiltR:0, happy:0, gx:null, gy:null, pupil:1.06,mw:33, mc:40, mo:.4,  mt:0,  ms:0,   bLy:-9, bRy:-9, bLa:-6, bRa:-6, tilt:-3, sy:1.03, armL:62, armR:36, core:1.15,spark:0, zzz:0, lp:1.3, lift:0 },
  curious:   { lidL:0,   lidR:0,   tiltL:0, tiltR:0, happy:0, gx:.32,  gy:-1,   pupil:1.14,mw:13, mc:2,  mo:.34, mt:0,  ms:8,   bLy:-14,bRy:-6, bLa:-8, bRa:-8, tilt:7,  sy:1.04, armL:40, armR:18, core:.95, spark:0, zzz:0, lp:1.05,lift:0 },
  think:     { lidL:.14, lidR:.04,  tiltL:-8, tiltR:6, happy:0, gx:-.9,  gy:-.85, pupil:.94,mw:10, mc:0,  mo:.3,  mt:0,  ms:-17, bLy:5,  bRy:-15,bLa:16, bRa:-8, tilt:-6, sy:.99,  armL:14, armR:6,  core:.32, spark:1, zzz:0, lp:.28,  lift:0 },
  celebrate: { lidL:0,   lidR:0,   tiltL:0, tiltR:0, happy:1, gx:0,     gy:0,    pupil:1,   mw:40, mc:44, mo:.85, mt:0,  ms:0,   bLy:-12,bRy:-12,bLa:-6, bRa:6,  tilt:0,  sy:1,    armL:158,armR:150,core:1.5, spark:0, zzz:0, lp:1.7, lift:0 },
  sleepy:    { lidL:1,   lidR:1,    tiltL:6, tiltR:-6,happy:0, gx:0,     gy:.55,  pupil:.9,  mw:13, mc:8,  mo:0,   mt:0,  ms:0,   bLy:8,  bRy:8,  bLa:-6, bRa:-6, tilt:-8, sy:.955, armL:14, armR:14,  core:.55, spark:0, zzz:1, lp:.62, lift:0 }
};
const KEYS = Object.keys(E.idle);
const cur = {}, tgt = {};
for (const k of KEYS) cur[k] = tgt[k] = E.idle[k] === null ? 0 : E.idle[k];
cur.gx = cur.gy = tgt.gx = tgt.gy = 0;

let emo = 'idle', pinned = false, backT = 0, lastAct = performance.now();
const lay = { blink:0, wave:0, jumpT:-1, lookX:0, lookY:0, pointerAt:-1e9, px:0, py:0, glanceX:0, glanceY:0, glanceUntil:0, nextGlance:0, startled:0 };

function setEmo(name, { hold = 0, pin = false } = {}) {
  if (!E[name]) return;
  clearTimeout(backT);
  emo = name; hero.dataset.emo = name; pinned = pin;
  Object.assign(tgt, E[name]);
  if (E[name].gx === null) { tgt.gx = lay.lookX; tgt.gy = lay.lookY; }
  if (name === 'celebrate') lay.jumpT = 0;
  $$('#moods button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.emo === name)));
  if (hold) backT = setTimeout(() => setEmo(name === 'celebrate' ? 'joy' : 'idle', name === 'celebrate' ? { hold: 2200 } : {}), hold);
  if (RM) { Object.assign(cur, tgt); lay.jumpT = -1; draw(0, true); }
}

/* --- рот: квадратичні криві. mo — наскільки відкритий. --- */
function mouthPath(w, mc, mo, mt, ms) {
  const top = mc, bot = mc + mo * 118;
  return `M${-w} 0Q${ms} ${top} ${w} ${mt}Q${ms} ${bot} ${-w} 0Z`;
}
const set = (n, a, v) => n.setAttribute(a, v);

/* --- кадр --- */
let t0 = performance.now(), lastT = t0, frame = 0, coreXY = { x: 0, y: 0 };
function draw(dt, still) {
  const now = performance.now(), t = (now - t0) / 1000;
  // згладжування: стала часу 0.12 c → ≈ 95 % за 360 мс
  const k = RM || still ? 1 : 1 - Math.exp(-dt / .12);
  // живий погляд, якщо настрій не фіксує очі
  const follow = E[emo].gx === null;
  if (follow) {
    const recent = now - lay.pointerAt < 4500;
    if (!recent && !RM) {
      if (now > lay.nextGlance) { lay.glanceX = rnd(-.9, .9); lay.glanceY = rnd(-.5, .4); lay.glanceUntil = now + rnd(900, 1700); lay.nextGlance = now + rnd(3200, 6500); }
      if (now > lay.glanceUntil) { lay.glanceX = 0; lay.glanceY = 0; }
      tgt.gx = lay.glanceX; tgt.gy = lay.glanceY;
    } else { tgt.gx = lay.lookX; tgt.gy = lay.lookY; }
  }
  for (const key of KEYS) cur[key] += (tgt[key] - cur[key]) * k;

  // дихання (повільне, у сні — глибше й повільніше)
  const sleepy = emo === 'sleepy';
  const br = RM ? 0 : Math.sin(t * Math.PI * 2 / (sleepy ? 6.2 : 4.2));
  const brAmp = sleepy ? .03 : .02;
  let sy = cur.sy * (1 + brAmp * br), y = 0, sxMul = 1;
  // стрибок (свято): присідання → розтягнення → приземлення
  if (lay.jumpT >= 0 && !RM) {
    lay.jumpT += dt;
    const P = 1.15, p = (lay.jumpT % P) / P;
    if (lay.jumpT > 3.4) lay.jumpT = -1;
    else if (p < .18) { const q = p / .18; sy *= 1 - .13 * Math.sin(q * Math.PI / 2); }
    else if (p < .72) { const q = (p - .18) / .54; y = -Math.sin(q * Math.PI) * 40; sy *= 1 + .1 * Math.sin(q * Math.PI); }
    else if (p < .86) { const q = (p - .72) / .14; sy *= 1 - .11 * Math.sin(q * Math.PI); }
  }
  const sx = (1 / Math.sqrt(sy)) * sxMul;
  const sway = RM ? 0 : Math.sin(t * .9) * .7;
  const lean = lay.lookX * 3.2;
  set(el.squash, 'transform', `translate(200 478) scale(${sx.toFixed(4)} ${sy.toFixed(4)}) translate(-200 -478)`);
  set(el.rig, 'transform', `translate(${(lay.lookX * 5).toFixed(2)} ${y.toFixed(2)})`);
  set(el.tilt, 'transform', `rotate(${(cur.tilt + sway + lean).toFixed(2)} 200 478)`);

  // моргання
  if (!RM && lay.blink > 0) lay.blink = Math.max(0, lay.blink - dt / .14);
  const bl = lay.blink > 0 ? Math.sin((1 - lay.blink) * Math.PI) : 0;
  // обличчя зсувається слідом за поглядом (псевдо-3D)
  set(el.face, 'transform', `translate(${(cur.gx * 8).toFixed(2)} ${(cur.gy * 6).toFixed(2)})`);
  const gx = cur.gx * 12, gy = cur.gy * 11, pu = cur.pupil;
  const eyeOp = clamp(1 - cur.happy * 1.4, 0, 1);
  const kk = clamp(cur.core * .7, 0, 1), lidFill = `rgb(${Math.round(94 + 44 * kk)} ${Math.round(53 + 14 * kk)} ${Math.round(99 - 4 * kk)})`;
  for (const [s, side] of [['L', 'L'], ['R', 'R']]) {
    const [ex, ey] = EYE[s];
    set(el['eye' + s], 'transform', `translate(${(ex + gx).toFixed(2)} ${(ey + gy).toFixed(2)})`);
    set(el['eye' + s + 'in'], 'transform', `scale(${pu.toFixed(3)} ${(pu * (1 - cur.happy * .3)).toFixed(3)})`);
    const lidv = clamp(Math.max(cur['lid' + s], bl), 0, 1), shut = clamp((lidv - .72) / .22, 0, 1);
    set(el['eye' + s], 'opacity', (eyeOp * (1 - shut)).toFixed(3));
    const sp = g('sleep' + s); set(sp, 'transform', `translate(${ex + gx * .6} ${ey + 4 + gy * .5})`); set(sp, 'opacity', (shut * (1 - cur.happy)).toFixed(3));
    set(g('iris' + s), 'transform', `translate(${(cur.gx * 9).toFixed(2)} ${(cur.gy * 12).toFixed(2)})`);
    const lid = clamp(Math.max(cur['lid' + s], bl), 0, 1);
    // кришка повіки: від -62 (відкрито) до +36 (закрито), з нахилом
    set(el['lid' + s].firstElementChild, 'fill', lidFill); set(el['lid' + s], 'transform', `translate(0 ${(-56 + lid * 96).toFixed(2)}) rotate(${(cur['tilt' + s] * (s === 'L' ? 1 : -1)).toFixed(1)})`);
    const hp = el['happy' + s]; set(hp, 'transform', `translate(${ex + gx * .6} ${ey + 8 + gy * .5})`); set(hp, 'opacity', clamp(cur.happy * 1.2 - .1, 0, 1).toFixed(3));
    const br_ = el['brow' + s]; const by = cur['b' + s + 'y'], ba = cur['b' + s + 'a'];
    set(br_, 'transform', `translate(${ex + gx * .5} ${ey - 57 + by + gy * .4}) rotate(${(s === 'L' ? ba : -ba).toFixed(1)})`);
  }
  // рот
  const w = cur.mw, d = mouthPath(w, cur.mc, cur.mo, cur.mt, cur.ms);
  set(el.mouthLine, 'd', d); set(el.mouthClip, 'd', d); set(el.mouthFill, 'd', d);
  set(el.mouthFill, 'opacity', clamp(cur.mo * 5, 0, 1).toFixed(2));
  set(el.tongue, 'cx', cur.ms.toFixed(1)); set(el.tongue, 'cy', (cur.mc + cur.mo * 118 * .55 + cur.mt * .25 - 4).toFixed(1));
  set(el.tongue, 'rx', (w * .5).toFixed(1)); set(el.tongue, 'ry', (14 * cur.mo + 1).toFixed(1)); set(el.tongue, 'opacity', clamp(cur.mo * 2.4 - .3, 0, 1).toFixed(2));
  set(el.mouthG, 'transform', `translate(${(203 + gx * .35).toFixed(2)} ${(334 + gy * .4).toFixed(2)})`);
  // руки
  lay.wave = Math.max(0, lay.wave - dt / 1.6);
  const wv = Math.sin(t * 13) * 24 * lay.wave;
  const flap = emo === 'celebrate' && !RM ? Math.sin(t * 9) * 12 : 0;
  set(el.armL, 'transform', `translate(66 300) rotate(${(cur.armL + wv + flap).toFixed(1)})`);
  set(el.armR, 'transform', `translate(338 300) rotate(${(-(cur.armR) - flap).toFixed(1)})`);
  // ядро
  const pulse = cur.core * (1 + (RM ? 0 : .07 * br) + (emo === 'celebrate' && !RM ? .08 * Math.sin(t * 9) : 0));
  const fs = .5 + .42 * pulse, fx = RM ? 0 : .045 * Math.sin(t * 7.3), fy = RM ? 0 : .06 * Math.sin(t * 5.1 + 1);
  set(el.coreG, 'transform', `translate(208 ${(132 + (1 - fs) * 40).toFixed(1)}) scale(${(fs * (1 + fx)).toFixed(3)} ${(fs * (1 + fy)).toFixed(3)})`);
  set(el.coreG, 'opacity', clamp(.55 + pulse * .45, 0, 1).toFixed(2));
  set(g('rim'), 'opacity', clamp(pulse * .38, 0, .7).toFixed(2));
  set(el.innerGlow, 'opacity', clamp(pulse * .8, 0, 1).toFixed(2)); set(g('halo'), 'opacity', clamp(.08 + pulse * .34, 0, .6).toFixed(2));
  set(el.innerGlow2, 'opacity', clamp(pulse * .62, 0, 1).toFixed(2));
  set(el.spark, 'opacity', clamp(cur.spark * (.75 + (RM ? 0 : .25 * Math.sin(t * 3))), 0, 1).toFixed(2));
  const zy = RM ? 0 : (t * 14) % 22;
  set(el.zzz, 'opacity', clamp(cur.zzz, 0, 1).toFixed(2)); set(el.zzz, 'transform', `translate(0 ${-zy.toFixed(1)})`);

  // світло сцени: від позиції ядра
  const cr = el.coreG.getBoundingClientRect(), hr = hero.getBoundingClientRect();
  const cx = cr.left + cr.width / 2 - hr.left, cy = cr.top + cr.height / 2 - hr.top;
  coreXY.x = cx; coreXY.y = cy;
  const lp = Math.max(cur.lp, .05) * (1 + (RM ? 0 : .05 * br));
  const night = emo === 'sleepy';
  el.light.style.opacity = clamp(lp * (night ? .62 : .34), 0, .8).toFixed(3);
  el.light.style.transform = `translate(${cx.toFixed(1)}px, ${cy.toFixed(1)}px) scale(${(.5 + lp * .5).toFixed(3)})`;
  // контактна тінь і калюжа світла на підлозі
  const lift = clamp(-y / 40, 0, 1);
  el.contact.style.transform = `scale(${(1 - lift * .32).toFixed(3)}, ${(1 - lift * .3).toFixed(3)})`;
  el.contact.style.opacity = (night ? .3 : .85) * (1 - lift * .5);
  el.pool.style.opacity = clamp(.05 + lp * .22, 0, .6).toFixed(3);
  el.pool.style.transform = `scale(${(.7 + lp * .3).toFixed(3)}, ${(.8 + lp * .2).toFixed(3)})`;

  // підсвічування літер заголовка: чим ближче до ядра, тим тепліше
  if (still || (frame++ & 1) === 0) {
    const R = (night ? 520 : 780) * (.45 + lp * .55);
    for (const L_ of letters) {
      const dx = L_.x - cx, dy = L_.y - cy, dist = Math.hypot(dx, dy);
      let l = Math.pow(clamp(1 - dist / R, 0, 1), 1.5) * clamp(lp * .9, 0, 1.15);
      if (L_.glow) l = clamp(Math.max(l, .28 + lp * .22), 0, 1);
      l = Math.round(clamp(l, 0, 1) * 40) / 40;
      if (l !== L_.l) { L_.l = l; L_.el.style.setProperty('--l', l); }
    }
  }
}

function loop(now) {
  const dt = Math.min(.05, (now - lastT) / 1000); lastT = now;
  draw(dt);
  requestAnimationFrame(loop);
}

/* ---------- моргання, поведінка в спокої ---------- */
(function blinkLoop() {
  if (RM) return;
  const go = () => {
    if (emo !== 'sleepy' && emo !== 'celebrate') { lay.blink = 1; if (Math.random() < .2) setTimeout(() => lay.blink = 1, 260); }
    setTimeout(go, rnd(3200, 5800));
  };
  setTimeout(go, 2400);
})();

/* ---------- репліки ---------- */
const bubble = $('#bubble'), bubbleText = $('#bubbleText');
let bubT = 0;
const nb = s => s.replace(/(^|\s)(\p{L}{1,2}|—)\s/gu, '$1$2\u00A0');
function fitBubble() {
  bubble.style.width = '';
  const r = document.createRange(); r.selectNodeContents(bubbleText);
  const sc = bubble.getBoundingClientRect().width / (bubble.offsetWidth || 1) || 1;
  const w = Math.max(...[...r.getClientRects()].map(q => q.width)) / sc;
  if (isFinite(w) && w > 0) bubble.style.width = Math.ceil(w + 42) + 'px';
}
function say(text, ms = 6000) {
  if (!text) return;
  bubbleText.textContent = nb(text); fitBubble();
  bubble.classList.remove('on'); void bubble.offsetWidth; bubble.classList.add('on');
  clearTimeout(bubT); if (ms) bubT = setTimeout(() => bubble.classList.remove('on'), ms);
}

/* ---------- погляд: курсор / дотик ---------- */
function aimAt(px, py) {
  const r = el.svg.getBoundingClientRect();
  const ex = r.left + r.width * (200 / 400), ey = r.top + r.height * (262 / 500);
  const dx = px - ex, dy = py - ey, dist = Math.hypot(dx, dy) || 1;
  const s = clamp(dist / (r.height * .55), 0, 1);
  lay.lookX = dx / dist * s; lay.lookY = dy / dist * s;
  lay.pointerAt = performance.now();
}
addEventListener('pointermove', e => { aimAt(e.clientX, e.clientY); activity(); hoverTop(e); }, { passive: true });
addEventListener('pointerdown', e => { aimAt(e.clientX, e.clientY); activity(); }, { passive: true });
addEventListener('touchmove', e => { const t = e.touches[0]; if (t) aimAt(t.clientX, t.clientY); }, { passive: true });
if (RM) addEventListener('pointermove', () => draw(0, true), { passive: true });

/* ---------- активність / сон ---------- */
let sleepT = 0;
function activity() {
  lastAct = performance.now();
  clearTimeout(sleepT);
  if (!pinned) sleepT = setTimeout(() => { if (!pinned && !typing) { setEmo('sleepy'); say(L().sleepy, 0); } }, 24000);
  if (emo === 'sleepy' && !pinned) { setEmo('joy', { hold: 1800 }); say(L().wake); }
}

/* ---------- дотик по Люмо: радість + помах ---------- */
el.svg.addEventListener('click', () => {
  activity(); pinned = false; lay.wave = 1;
  setEmo('joy', { hold: 2400 }); say(L().joy);
});

/* ---------- цікавість: курсор угорі екрана / початок прокрутки ---------- */
let topHold = 0;
function hoverTop(e) {
  if (pinned || typing || emo === 'celebrate' || emo === 'sleepy') return;
  if (matchMedia('(pointer: coarse)').matches) return;
  if (e.clientY < innerHeight * .16 && e.clientY > 90) {
    if (emo !== 'curious') { setEmo('curious'); say(L().curious); }
    clearTimeout(topHold); topHold = setTimeout(() => { if (emo === 'curious' && !pinned) setEmo('idle'); }, 1600);
  }
}
let scrollCuriousAt = 0;
addEventListener('scroll', () => {
  activity();
  if (pinned || typing || emo === 'celebrate') return;
  if (scrollY > 24 && performance.now() - scrollCuriousAt > 4000) { scrollCuriousAt = performance.now(); setEmo('curious', { hold: 2200 }); say(L().curious); }
}, { passive: true });

/* ---------- ім’я ---------- */
const form = $('#nameForm'), input = $('#guestName');
let guest = '', typing = false, typeT = 0;
input.addEventListener('input', () => {
  activity();
  if (pinned) return;
  typing = true; if (emo !== 'think') { setEmo('think'); say(L().typing, 0); }
  clearTimeout(typeT); typeT = setTimeout(() => { typing = false; if (emo === 'think' && !pinned) setEmo('idle'); }, 1800);
});
function esc(s) { return s.replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c])); }
function greetHTML() { return esc(U().greet).replace('{n}', `<span class="nm">${esc(guest)}</span>`); }
form.addEventListener('submit', e => {
  e.preventDefault(); activity();
  const name = input.value.replace(/\s+/g, ' ').trim().slice(0, 24);
  typing = false; clearTimeout(typeT); pinned = false;
  if (!name) { setEmo('joy', { hold: 2400 }); say(L().noname); return; }
  guest = name;
  form.hidden = true; $('#leadHint').hidden = true; $('#greet').hidden = false; $('#greetT').innerHTML = greetHTML();
  setEmo('celebrate', { hold: 3400 }); say(L().named.replace('{n}', name), 7000);
  setTimeout(() => burst(), RM ? 0 : 380);
});
$('#changeName').addEventListener('click', () => {
  guest = ''; $('#leadHint').hidden = false; $('#greet').hidden = true; form.hidden = false; input.value = ''; input.focus(); setEmo('idle');
});

/* ================= ЧАСТИНКИ (тільки після імені) ================= */
const cv = $('#fx'), cx2 = cv.getContext('2d');
let parts = [], running = false, DPR = 1;
function sizeCanvas() { DPR = Math.min(2, devicePixelRatio || 1); cv.width = hero.clientWidth * DPR; cv.height = hero.clientHeight * DPR; }
function burst() {
  if (RM) return;
  sizeCanvas();
  const COLS = ['#FF7A45', '#FF9A66', '#FF5F25', '#FFB27E', '#FFD9A8'];
  const hr = hero.getBoundingClientRect(), sr = el.svg.getBoundingClientRect();
  const x = sr.left - hr.left + sr.width * .5, y = sr.top - hr.top + sr.height * .52, R0 = sr.height * .36;
  for (let i = 0; i < 72; i++) {
    const a = rnd(0, Math.PI * 2), v = rnd(260, 680), r0 = R0 * rnd(.75, 1.05);
    parts.push({ x: x + Math.cos(a) * r0 * .85, y: y + Math.sin(a) * r0, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 120, r: rnd(3, 8), life: 0, max: rnd(1.1, 1.9), c: COLS[i % COLS.length], star: i % 5 === 0, rot: rnd(0, 6.28), vr: rnd(-6, 6) });
  }
  if (!running) { running = true; lastP = performance.now(); requestAnimationFrame(stepP); }
}
let lastP = 0;
function stepP(now) {
  const dt = Math.min(.04, (now - lastP) / 1000); lastP = now;
  cx2.setTransform(DPR, 0, 0, DPR, 0, 0); cx2.clearRect(0, 0, cv.width, cv.height);
  parts = parts.filter(p => p.life < p.max);
  for (const p of parts) {
    p.life += dt; p.vy += 420 * dt; p.vx *= 1 - 1.8 * dt; p.vy *= 1 - .9 * dt; p.x += p.vx * dt; p.y += p.vy * dt; p.rot += p.vr * dt;
    const a = clamp(1 - p.life / p.max, 0, 1);
    cx2.globalAlpha = a; cx2.fillStyle = p.c;
    if (p.star) { cx2.save(); cx2.translate(p.x, p.y); cx2.rotate(p.rot); const s = p.r * 1.8; cx2.beginPath(); cx2.moveTo(0, -s); cx2.lineTo(s * .28, -s * .28); cx2.lineTo(s, 0); cx2.lineTo(s * .28, s * .28); cx2.lineTo(0, s); cx2.lineTo(-s * .28, s * .28); cx2.lineTo(-s, 0); cx2.lineTo(-s * .28, -s * .28); cx2.closePath(); cx2.fill(); cx2.restore(); }
    else { cx2.beginPath(); cx2.arc(p.x, p.y, p.r * (.5 + a * .5), 0, 6.283); cx2.fill(); }
  }
  if (parts.length) requestAnimationFrame(stepP); else { running = false; cx2.clearRect(0, 0, cv.width, cv.height); }
}

/* ================= ПЕРЕМИКАЧ НАСТРОЮ (для перегляду прототипу) ================= */
$$('#moods button').forEach(b => b.addEventListener('click', () => {
  const name = b.dataset.emo; lastAct = performance.now(); clearTimeout(sleepT);
  setEmo(name, { pin: name !== 'idle' });
  const key = { idle:'hello', joy:'joy', curious:'curious', think:'think', celebrate:'celebrate', sleepy:'sleepy' }[name];
  say(L()[key], name === 'sleepy' ? 0 : 6000);
  if (name === 'celebrate') setTimeout(() => burst(), 380);
  if (name === 'idle') { pinned = false; activity(); }
}));

/* ================= МОВИ ================= */
const langBtn = $('#langBtn'), langList = $('#langList');
function openLang(o) { langList.hidden = !o; langBtn.setAttribute('aria-expanded', String(o)); if (o) { (langList.querySelector('[aria-selected="true"]') || langList.firstElementChild).focus?.(); } }
$$('#langList li').forEach(li => { li.tabIndex = -1; });
langBtn.addEventListener('click', () => openLang(langList.hidden));
langList.addEventListener('click', e => { const li = e.target.closest('li'); if (li) pickLang(li.dataset.lang); });
langList.addEventListener('keydown', e => {
  const items = $$('#langList li'), i = items.indexOf(document.activeElement);
  if (e.key === 'ArrowDown') { e.preventDefault(); items[(i + 1) % items.length].focus(); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
  else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); if (i >= 0) pickLang(items[i].dataset.lang); }
  else if (e.key === 'Escape') { openLang(false); langBtn.focus(); }
});
document.addEventListener('click', e => { if (!e.target.closest('#lang')) openLang(false); });
function pickLang(l) {
  lang = l; $$('#langList li').forEach(li => li.setAttribute('aria-selected', String(li.dataset.lang === l)));
  openLang(false); langBtn.focus(); applyText(); say(L().hello);
  if (RM) draw(0, true);
}

/* ================= СТАРТ ================= */
addEventListener('resize', () => { fitH1(); cacheLetters(); sizeCanvas(); if (RM) draw(0, true); });
applyText(); fitBubble();
if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { fitBubble(); fitH1(); cacheLetters(); if (RM) draw(0, true); });

const q = new URLSearchParams(location.search);
const emoQ = q.get('emo');
if (emoQ && E[emoQ]) { setEmo(emoQ, { pin: true }); say(L()[{ idle:'hello', joy:'joy', curious:'curious', think:'think', celebrate:'celebrate', sleepy:'sleepy' }[emoQ]], 0); } else { setEmo('idle'); bubbleText.textContent = nb(L().hello); fitBubble(); }
if (q.get('lang') && UI[q.get('lang')]) { lang = q.get('lang'); applyText(); }
activity();
draw(0, true);
if (!RM) requestAnimationFrame(loop);
window.__lumo = { setEmo, burst, say, draw: () => draw(0, true), get emo() { return emo; } };
})();
