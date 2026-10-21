/* LUMOSCHOOL · B3 «Вау» (основа B2). Ванільний JS без збірки.
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
  uk: { code:'UA', trial:'Пробний урок', trialN:'Пробний урок, {n}', kicker:'Англійська', a:'з другом,', b:'що світиться', lead:'Онлайн-уроки для дітей, підлітків і дорослих.', hint:'Назви себе — і Люмо привітається.', label:'Назви себе, як хочеш', ph:'ім’я або прізвисько', btn:'Привітатись', cue:'Прокрути — він помітить', greet:'Привіт, {n}!', change:'Змінити ім’я', mood:'Настрій', moods:['Спокій','Радість','Цікавість','Роздум','Свято','Сон'], alt:'Люмо — живий друг, що світиться', listLabel:'Мова сайту' },
  pl: { code:'PL', trial:'Lekcja próbna', trialN:'Lekcja próbna, {n}', kicker:'Angielski', a:'z przyjacielem,', b:'który świeci', lead:'Lekcje online dla dzieci, nastolatków i dorosłych.', hint:'Podaj imię — Lumo się przywita.', label:'Przedstaw się, jak chcesz', ph:'imię lub pseudonim', btn:'Przywitaj się', cue:'Przewiń — on to zauważy', greet:'Cześć, {n}!', change:'Zmień imię', mood:'Nastrój', moods:['Spokój','Radość','Ciekawość','Namysł','Święto','Sen'], alt:'Lumo — żywy przyjaciel, który świeci', listLabel:'Język strony' },
  en: { code:'EN', trial:'Trial lesson', trialN:'Trial lesson, {n}', kicker:'English', a:'with a friend', b:'who glows', lead:'Online lessons for kids, teens and adults.', hint:'Tell us your name — Lumo will say hi.', label:'Call yourself whatever you like', ph:'name or nickname', btn:'Say hi', cue:'Scroll — he will notice', greet:'Hi, {n}!', change:'Change name', mood:'Mood', moods:['Calm','Joy','Curious','Thinking','Party','Sleep'], alt:'Lumo — a living friend who glows', listLabel:'Site language' },
  de: { code:'DE', trial:'Probestunde', trialN:'Probestunde, {n}', kicker:'Englisch', a:'mit einem Freund,', b:'der leuchtet', lead:'Online-Unterricht für Kinder, Jugendliche und Erwachsene.', hint:'Nenn deinen Namen — Lumo sagt Hallo.', label:'Nenn dich, wie du willst', ph:'Name oder Spitzname', btn:'Hallo sagen', cue:'Scrolle — er merkt es', greet:'Hallo, {n}!', change:'Namen ändern', mood:'Stimmung', moods:['Ruhe','Freude','Neugier','Nachdenken','Fest','Schlaf'], alt:'Lumo — ein lebendiger Freund, der leuchtet', listLabel:'Sprache' },
  cs: { code:'CS', trial:'Zkušební hodina', trialN:'Zkušební hodina, {n}', kicker:'Angličtina', a:'s kamarádem,', b:'který svítí', lead:'Online lekce pro děti, teenagery i dospělé.', hint:'Řekni své jméno — Lumo tě pozdraví.', label:'Představ se, jak chceš', ph:'jméno nebo přezdívka', btn:'Pozdravit', cue:'Rolluj — všimne si', greet:'Ahoj, {n}!', change:'Změnit jméno', mood:'Nálada', moods:['Klid','Radost','Zvědavost','Přemýšlení','Oslava','Spánek'], alt:'Lumo — živý kamarád, který svítí', listLabel:'Jazyk stránky' },
  ru: { code:'RU', trial:'Пробный урок', trialN:'Пробный урок, {n}', kicker:'Английский', a:'с другом,', b:'который светится', lead:'Онлайн-уроки для детей, подростков и взрослых.', hint:'Назови себя — и Люмо поздоровается.', label:'Назови себя, как хочешь', ph:'имя или прозвище', btn:'Поздороваться', cue:'Прокрути — он заметит', greet:'Привет, {n}!', change:'Сменить имя', mood:'Настроение', moods:['Покой','Радость','Любопытство','Раздумье','Праздник','Сон'], alt:'Люмо — живой друг, который светится', listLabel:'Язык сайта' }
};
const LINES = {
  uk: { stub:'Тут буде запис на пробний урок. Це заглушка.', hello:'Привіт! Я Люмо. Можна мене торкнутись.', joy:'Ой, приємно! Тепло від твоєї руки.', curious:'Ммм, а що там угорі?', think:'Гм… дай подумати.', typing:'Слухаю, як ти друкуєш.', sleepy:'Я трошки задрімав… торкнись — прокинусь.', wake:'О, я тут! Радий знову тебе бачити.', named:'Дуже радий знайомству. Почнемо, коли захочеш.', noname:'Можна й без імені — я просто світитимусь поруч.', celebrate:'Ура! Так весело, що підстрибнув!' },
  pl: { stub:'Tu będzie zapis na lekcję próbną. To makieta.', hello:'Cześć! Jestem Lumo. Możesz mnie dotknąć.', joy:'Ojej, miło! Ciepło od twojej ręki.', curious:'Mmm, co tam jest u góry?', think:'Hm… daj mi pomyśleć.', typing:'Słucham, jak piszesz.', sleepy:'Chwilkę przysnąłem… dotknij — obudzę się.', wake:'O, jestem! Miło cię znowu widzieć.', named:'Bardzo miło cię poznać. Zaczniemy, kiedy zechcesz.', noname:'Można i bez imienia — po prostu będę świecić obok.', celebrate:'Hura! Tak wesoło, że podskoczyłem!' },
  en: { stub:'Trial-lesson booking will live here. Placeholder.', hello:"Hi! I'm Lumo. You can touch me.", joy:'Aw, nice! Your hand is warm.', curious:"Mmm, what's up there?", think:'Hm… let me think.', typing:"I'm listening to you type.", sleepy:"I dozed off a little… touch me — I'll wake up.", wake:"Oh, I'm here! Glad you're back.", named:"So glad we met. I'm ready whenever you are.", noname:'No name is fine too — I will just glow next to you.', celebrate:'Yay! So much fun I jumped!' },
  de: { stub:'Hier kommt die Anmeldung zur Probestunde. Platzhalter.', hello:'Hallo! Ich bin Lumo. Du darfst mich anfassen.', joy:'Oh, wie schön! Deine Hand ist warm.', curious:'Mmm, was ist da oben?', think:'Hm… lass mich überlegen.', typing:'Ich höre dir beim Tippen zu.', sleepy:'Ich bin kurz eingenickt… tipp mich an.', wake:'Oh, ich bin da! Schön, dass du zurück bist.', named:'Schön, dass wir uns kennen. Wir fangen an, wenn du magst.', noname:'Auch ohne Namen — ich leuchte einfach neben dir.', celebrate:'Juhu! So viel Freude, ich musste hüpfen!' },
  cs: { stub:'Tady bude zápis na zkušební hodinu. Zástupný text.', hello:'Ahoj! Jsem Lumo. Můžeš se mě dotknout.', joy:'Jé, to je příjemné! Máš teplou ruku.', curious:'Mmm, co je tam nahoře?', think:'Hm… nech mě přemýšlet.', typing:'Poslouchám, jak píšeš.', sleepy:'Trochu jsem usnul… dotkni se mě.', wake:'Jé, jsem tu! Rád tě zase vidím.', named:'Moc mě těší. Začneme, až budeš chtít.', noname:'I bez jména to jde — budu prostě svítit vedle tebe.', celebrate:'Hurá! Tolik radosti, že jsem vyskočil!' },
  ru: { stub:'Здесь будет запись на пробный урок. Это заглушка.', hello:'Привет! Я Люмо. Меня можно потрогать.', joy:'Ой, приятно! Рука у тебя тёплая.', curious:'Ммм, а что там наверху?', think:'Гм… дай подумать.', typing:'Слушаю, как ты печатаешь.', sleepy:'Я немножко задремал… коснись — проснусь.', wake:'О, я тут! Рад снова тебя видеть.', named:'Очень рад знакомству. Начнём, когда захочешь.', noname:'Можно и без имени — я просто посвечу рядом.', celebrate:'Ура! Так весело, что подпрыгнул!' }
};
let lang = 'uk';
const U = () => UI[lang], L = () => LINES[lang];


/* ================= ЗВАТЕЛЬНИЙ ВІДМІНОК (українська) ================= */
const MALE = `Іван:Іване Петро:Петре Олег:Олегу Андрій:Андрію Сергій:Сергію Юрій:Юрію Василь:Василю Дмитро:Дмитре Олександр:Олександре Максим:Максиме Микола:Миколо Микита:Микито Нікіта:Нікіто Богдан:Богдане Тарас:Тарасе Роман:Романе Назар:Назаре Артем:Артеме Артур:Артуре Антон:Антоне Олексій:Олексію Ілля:Ілле Данило:Даниле Денис:Денисе Євген:Євгене Едуард:Едуарде Ігор:Ігорю Георгій:Георгію Григорій:Григорію Віталій:Віталію Віктор:Вікторе Володимир:Володимире Всеволод:Всеволоде В’ячеслав:В’ячеславе Гліб:Глібе Давид:Давиде Кирило:Кириле Костянтин:Костянтине Леонід:Леоніде Лев:Леве Любомир:Любомире Марк:Марку Марко:Марку Матвій:Матвію Михайло:Михайле Мирослав:Мирославе Мар’ян:Мар’яне Орест:Оресте Остап:Остапе Павло:Павле Пилип:Пилипе Руслан:Руслане Ростислав:Ростиславе Святослав:Святославе Семен:Семене Станіслав:Станіславе Степан:Степане Тимофій:Тимофію Тимур:Тимуре Тихон:Тихоне Устим:Устиме Федір:Федоре Філіп:Філіпе Юліан:Юліане Ярослав:Ярославе Ярема:Яремо Захар:Захаре Ігнат:Ігнате Єгор:Єгоре Лука:Луко Сава:Саво Влад:Владе Владислав:Владиславе Вадим:Вадиме Валентин:Валентине Валерій:Валерію Анатолій:Анатолію Аркадій:Аркадію Борис:Борисе Богуслав:Богуславе Борислав:Бориславе Гнат:Гнате Геннадій:Геннадію Гордій:Гордію Діма:Дімо Саша:Сашо Женя:Женю Льова:Льово Коля:Колю Вова:Вово Петя:Петю Вася:Васю Толя:Толю Сеня:Сеню Льоша:Льошо Макс:Максе Тимко:Тимку Юра:Юро Гриша:Гришо Андрійко:Андрійку Мартин:Мартине Назарій:Назарію Мирон:Мироне Макар:Макаре Климент:Клименте Євгеній:Євгенію Ян:Яне Рустам:Рустаме Стас:Стасе Артемій:Артемію Жора:Жоро Олесь:Олесю Ілько:Ільку Ярик:Ярику Тема:Темо Славко:Славку Назарко:Назарку Левко:Левку Орик:Орику Лаврін:Лавріне Оксен:Оксене Вітя:Вітю Паша:Пашо Миша:Мишо Гена:Гено Слава:Славо Костя:Костю Дмитрик:Дмитрику Ігорьок:Ігорьку Павлик:Павлику Ромко:Ромку Тарасик:Тарасику Єремій:Єремію Адам:Адаме Альберт:Альберте Анатоль:Анатолю Арсен:Арсене Арсеній:Арсенію Вілен:Вілене Еріх:Еріху Максимко:Максимку Олекса:Олексо Ілько:Ільку Кузьма:Кузьмо Нестор:Несторе Омелян:Омеляне Прохор:Прохоре Роберт:Роберте Тео:Тео Юхим:Юхиме Яким:Якиме Якуб:Якубе`.split(/\s+/).reduce((m, p) => { const [a, b] = p.split(':'); m[a.toLowerCase()] = b.toLowerCase(); return m; }, {});
const CYR = /^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ’'ʼ-]+$/;
const VOW = 'аеєиіїоуюя';
function vocWord(w) {
  if (!CYR.test(w)) return w;                      // латиниця, цифри, зміш. — не чіпаємо
  const lw = w.toLowerCase();
  let r;
  if (MALE[lw]) r = MALE[lw];
  else if (/ія$/.test(lw)) r = lw.slice(0, -2) + 'іє';              // Марія → Маріє
  else if (/я$/.test(lw)) r = VOW.includes(lw.slice(-2, -1)) ? lw.slice(0, -1) + 'є' : lw.slice(0, -1) + 'ю';  // Оля → Олю, Зоя → Зоє
  else if (/а$/.test(lw)) r = lw.slice(0, -1) + 'о';                // Ганна → Ганно
  else return w;                                   // невідоме чоловіче/інше — лишаємо
  // повертаємо регістр: ВЕЛИКІ → ВЕЛИКІ, інакше велика перша
  if (w === w.toUpperCase() && w.length > 1) return r.toUpperCase();
  return w[0] + r.slice(1);
}
function vocative(name) {
  if (lang !== 'uk') return name;
  const parts = name.split(' ');
  parts[0] = vocWord(parts[0]);
  return parts.join(' ');
}

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
function fitOne(h) {
  h.style.fontSize = '';
  if (h.hidden) return;
  const mob = matchMedia('(max-width:820px)').matches, hdl = $('.headline'), st = $('#stage');
  const shift = hero.classList.contains('named') && !mob ? 104 : 0;
  const avail = mob ? hdl.clientWidth : st.offsetLeft - shift + st.offsetWidth * .1 - hdl.offsetLeft - 8;
  const w = Math.max(...$$('.ln', h).map(n => n.scrollWidth));
  if (w > avail) h.style.fontSize = (parseFloat(getComputedStyle(h).fontSize) * avail / w * .98).toFixed(1) + 'px';
}
function fitH1() { fitOne(h1); fitOne($('#greetH')); }
function cacheLetters() {
  const hr = hero.getBoundingClientRect();
  letters = $$('.ch', $('.headline')).filter(el => el.offsetParent).map(el => { const r = el.getBoundingClientRect(); return { el, x: r.left + r.width / 2 - hr.left, y: r.top + r.height / 2 - hr.top, glow: !!el.closest('.ln-glow'), nm: el.classList.contains('nmc'), l: -1 }; });
}
const cap = t => t.charAt(0).toUpperCase() + t.slice(1);
function applyText() {
  const u = U();
  document.documentElement.lang = lang;
  split(h1a, u.a); split(h1b, u.b);
  h1.setAttribute('aria-label', u.a + ' ' + u.b);
  $('#kicker').textContent = guest ? cap(u.a + ' ' + u.b) : u.kicker; $('#trialM').textContent = u.trial; $('#leadMain').textContent = nb(u.lead); $('#leadHint').textContent = nb(u.hint); $('#leadHint').hidden = !!guest;
  $('#nameLabel').textContent = u.label; $('#guestName').placeholder = u.ph; $('#nameBtn').textContent = u.btn;
  $('#cueT').textContent = u.cue; $('#changeName').textContent = u.change; $('#moodsL').textContent = u.mood;
  $$('#moods button').forEach((b, i) => b.textContent = u.moods[i]);
  $('#langCode').textContent = u.code; $('#lumo').setAttribute('aria-label', u.alt);
  $('#langBtn').setAttribute('aria-label', u.listLabel); $('#langList').setAttribute('aria-label', u.listLabel);
  $('#trialQ').textContent = u.trial;
  if (guest) { buildGreet(); $('#ctaT').textContent = ctaText(); }
  fitH1(); cacheLetters();
}

/* ================= РИГ ЛЮМО ================= */
const g = id => document.getElementById(id);
const el = { rig:g('rig'), squash:g('squash'), tilt:g('tilt'), face:g('face'), armL:g('armL'), armR:g('armR'),
  browL:g('browL'), browR:g('browR'), eyeL:g('eyeL'), eyeR:g('eyeR'), eyeLin:g('eyeLin'), eyeRin:g('eyeRin'), lidL:g('lidL'), lidR:g('lidR'),
  happyL:g('happyL'), happyR:g('happyR'), mouthFill:g('mouthFill'), mouthLine:g('mouthLine'), mouthClip:g('mouthClipPath'), tongue:g('tongue'), mouthG:g('mouthG'),
  coreG:g('coreG'), coreDisc:g('coreDisc'), innerGlow:g('innerGlow'), innerGlow2:g('innerGlow2'), zzz:g('zzz'),
  stars: [...document.querySelectorAll('.star')], svg:g('lumo'), light:g('light'), pool:g('pool'), contact:g('contact') };
const EYE = { L:[158, 262], R:[248, 262] };

/* Цілі настроїв. gx/gy = null → дивиться за курсором. */
const E = {
  idle:      { lidL:.05, lidR:.05, tiltL:0, tiltR:0, happy:0, gx:null, gy:null, pupil:1,   mw:26, mc:26, mo:0,   mt:0,  ms:0,   bLy:0,  bRy:0,  bLa:0,  bRa:0,  tilt:0,  sy:1,    armL:24, armR:24, core:.85, fl:.04, zzz:0, lp:1,   lift:0, sat:1, star:1, mx:0,},
  joy:       { lidL:.12, lidR:.12, tiltL:0, tiltR:0, happy:0, gx:null, gy:null, pupil:1.06,mw:33, mc:40, mo:.4,  mt:0,  ms:0,   bLy:-9, bRy:-9, bLa:-6, bRa:-6, tilt:-3, sy:1.03, armL:54, armR:54, core:1.15,fl:.05, zzz:0, lp:1.2, lift:0, sat:1.05, star:1, mx:0,},
  curious:   { lidL:0,   lidR:0,   tiltL:0, tiltR:0, happy:0, gx:.32,  gy:-1,   pupil:1.14,mw:13, mc:2,  mo:.34, mt:0,  ms:8,   bLy:-14,bRy:-6, bLa:-8, bRa:-8, tilt:7,  sy:1.04, armL:40, armR:18, core:.95, fl:.04, zzz:0, lp:1.05,lift:0, sat:1, star:1, mx:0,},
  think:     { lidL:.15, lidR:.15, tiltL:0, tiltR:0, happy:0, gx:-1, gy:-1, pupil:.92, mw:10, mc:-9, mo:.22, mt:-5, ms:0, bLy:5, bRy:-22, bLa:9, bRa:-6, tilt:-5, sy:.99, armL:10, armR:88, core:.62, fl:.13, zzz:0, lp:.62, lift:0, mx:12, sat:.85, star:0,},
  celebrate: { lidL:0,   lidR:0,   tiltL:0, tiltR:0, happy:1, gx:0,     gy:0,    pupil:1,   mw:40, mc:44, mo:.85, mt:0,  ms:0,   bLy:-12,bRy:-12,bLa:-6, bRa:6,  tilt:0,  sy:1,    armL:158,armR:150,core:1.5, fl:.06, zzz:0, lp:1.7, lift:0, sat:1.1, star:1, mx:0,},
  sleepy:    { lidL:1,   lidR:1,    tiltL:6, tiltR:-6,happy:0, gx:0,     gy:.55,  pupil:.9,  mw:13, mc:8,  mo:0,   mt:0,  ms:0,   bLy:8,  bRy:8,  bLa:-6, bRa:-6, tilt:-8, sy:.955, armL:14, armR:14,  core:.55, fl:.02, zzz:1, lp:.62, lift:0, sat:0.9, star:1, mx:0,}
};
const KEYS = Object.keys(E.idle);
const cur = {}, tgt = {};
for (const k of KEYS) cur[k] = tgt[k] = E.idle[k] === null ? 0 : E.idle[k];
cur.gx = cur.gy = tgt.gx = tgt.gy = 0;

let emo = 'idle', pinned = false, backT = 0, lastAct = performance.now();
const lay = { jt:-1, ja:0, jx:0, flare:0, kick:0, ember:0, emberT:0, turnC:0, turnT:0, blink:0, wave:0, jumpT:-1, lookX:0, lookY:0, pointerAt:-1e9, px:0, py:0, glanceX:0, glanceY:0, glanceUntil:0, nextGlance:0, startled:0 };

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
let nmShown = '', nmFlash = 0, t0 = performance.now(), lastT = t0, frame = 0, coreXY = { x: 0, y: 0 };
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
      if (now > lay.glanceUntil) { lay.glanceX = lay.homeX || 0; lay.glanceY = lay.homeY || 0; }
      if (!lay.homeAt || now - lay.homeAt > 2500) { lay.homeAt = now; const q2 = (guest ? $('#cta') : input).getBoundingClientRect(), r2 = el.svg.getBoundingClientRect(); const dx = q2.left + q2.width * .4 - (r2.left + r2.width * .5), dy = q2.top + q2.height / 2 - (r2.top + r2.height * .52), dd = Math.hypot(dx, dy) || 1; lay.homeX = dx / dd * .75; lay.homeY = dy / dd * .5; } 
      tgt.gx = lay.glanceX; tgt.gy = lay.glanceY;
    } else { tgt.gx = lay.lookX; tgt.gy = lay.lookY; }
    tgt.gy = clamp(tgt.gy + clamp(scrollY / (innerHeight * .55), 0, 1) * .85, -1, 1);
  }
  for (const key of KEYS) cur[key] += (tgt[key] - cur[key]) * k;

  // дихання (повільне, у сні — глибше й повільніше)
  const sleepy = emo === 'sleepy';
  const br = RM ? 0 : Math.sin(t * Math.PI * 2 / (sleepy ? 6.2 : 4.2));
  const brAmp = sleepy ? .03 : .02;
  let sy = cur.sy * (1 + brAmp * br), y = 0, sxMul = 1;
  // желейна деформація від кліку: згасаюча пружина
  let jelly = 0;
  if (lay.jt >= 0 && !RM) { lay.jt += dt; const e = Math.exp(-lay.jt * 4.4); jelly = e * Math.sin(lay.jt * 21) * lay.ja; if (lay.jt > 1.7) lay.jt = -1; }
  sy *= 1 + jelly * .17;
  lay.flare = Math.max(0, lay.flare - dt / 1.1); lay.kick = Math.max(0, lay.kick - dt / .45);
  lay.ember += (lay.emberT - lay.ember) * (RM || still ? 1 : 1 - Math.exp(-dt / .35));
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
  set(el.squash, 'transform', `translate(200 478) skewX(${(jelly * lay.jx * 8).toFixed(2)}) scale(${sx.toFixed(4)} ${sy.toFixed(4)}) translate(-200 -478)`);
  set(el.rig, 'transform', `translate(${(lay.lookX * 5).toFixed(2)} ${y.toFixed(2)})`);
  lay.turnC += (lay.turnT - lay.turnC) * (RM || still ? 1 : 1 - Math.exp(-dt / .3));
  set(el.tilt, 'transform', `rotate(${(cur.tilt + sway + lean + lay.turnC * 3).toFixed(2)} 200 478)`);

  // моргання
  if (!RM && lay.blink > 0) lay.blink = Math.max(0, lay.blink - dt / .14);
  const bl = lay.blink > 0 ? Math.sin((1 - lay.blink) * Math.PI) : 0;
  // обличчя зсувається слідом за поглядом (псевдо-3D)
  set(el.face, 'transform', `translate(${(cur.gx * 8 + lay.turnC * 24).toFixed(2)} ${(cur.gy * 6).toFixed(2)})`);
  const gx = cur.gx * 12, gy = cur.gy * 11, pu = cur.pupil;
  const eyeOp = clamp(1 - cur.happy * 1.4, 0, 1);
  const kk = clamp(cur.core * .7, 0, 1), lidFill = `rgb(${Math.round(94 + 44 * kk)} ${Math.round(53 + 14 * kk)} ${Math.round(99 - 4 * kk)})`;
  for (const [s, side] of [['L', 'L'], ['R', 'R']]) {
    const [ex, ey] = EYE[s];
    set(el['eye' + s], 'transform', `translate(${(ex + gx).toFixed(2)} ${(ey + gy).toFixed(2)})`);
    set(el['eye' + s + 'in'], 'transform', `scale(${(pu * .94).toFixed(3)} ${(pu * (1 - cur.happy * .3)).toFixed(3)})`);
    set(g('sock' + s), 'transform', `translate(${(ex + gx * .3).toFixed(2)} ${(ey + 4 + gy * .3).toFixed(2)})`);
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
  for (const st of el.stars) st.setAttribute('opacity', clamp(cur.star, 0, 1).toFixed(2));
  // рот
  const w = cur.mw, d = mouthPath(w, cur.mc, cur.mo, cur.mt, cur.ms);
  set(el.mouthLine, 'd', d); set(el.mouthClip, 'd', d); set(el.mouthFill, 'd', d);
  set(el.mouthFill, 'opacity', clamp(cur.mo * 5, 0, 1).toFixed(2));
  set(el.tongue, 'cx', cur.ms.toFixed(1)); set(el.tongue, 'cy', (cur.mc + cur.mo * 118 * .55 + cur.mt * .25 - 4).toFixed(1));
  set(el.tongue, 'rx', (w * .5).toFixed(1)); set(el.tongue, 'ry', (14 * cur.mo + 1).toFixed(1)); set(el.tongue, 'opacity', clamp(cur.mo * 2.4 - .3, 0, 1).toFixed(2));
  set(el.mouthG, 'transform', `translate(${(203 + cur.mx + gx * .35).toFixed(2)} ${(334 + gy * .4).toFixed(2)})`);
  // руки
  lay.wave = Math.max(0, lay.wave - dt / 1.6);
  const wv = Math.sin(t * 13) * 24 * lay.wave;
  const flap = emo === 'celebrate' && !RM ? Math.sin(t * 9) * 12 : 0;
  const fin = RM ? 0 : Math.sin(t * 1.7) * 3.2;
  set(el.armL, 'transform', `translate(66 300) rotate(${(cur.armL + wv + flap + fin).toFixed(1)})`);
  { const k = clamp(-cur.armR / 146, 0, 1); set(el.armR, 'transform', `translate(${(334 - k * 84).toFixed(1)} ${(300 + k * 162).toFixed(1)}) rotate(${(-(cur.armR) - flap - fin * (1 - k * .8)).toFixed(1)}) scale(${(1 + k * .26).toFixed(3)})`); }
  const front = cur.armR < 12; if (front !== lay.armFront) { lay.armFront = front; if (front) el.rig.appendChild(el.armR); else el.rig.insertBefore(el.armR, el.squash); }
  // ядро
  const fl = RM ? 0 : (Math.sin(t * 23) * .5 + Math.sin(t * 37 + 1) * .3 + Math.sin(t * 11.3 + 2) * .2) * cur.fl;
  const pulse = cur.core * (1 + (RM ? 0 : .07 * br) + (emo === 'celebrate' && !RM ? .08 * Math.sin(t * 9) : 0) + fl * .6) + lay.ember * .5 + lay.kick * .35 + lay.flare * .8;
  const fs = .5 + .42 * pulse, fx = RM ? 0 : .045 * Math.sin(t * 7.3) - fl * .5, fy = RM ? 0 : .06 * Math.sin(t * 5.1 + 1) + fl * 1.2;
  set(el.coreG, 'transform', `translate(208 ${(132 + (1 - fs) * 40).toFixed(1)}) rotate(${(fl * 22).toFixed(1)}) scale(${(fs * (1 + fx)).toFixed(3)} ${(fs * (1 + fy)).toFixed(3)})`);
  set(el.coreG, 'opacity', clamp(.55 + pulse * .45, 0, 1).toFixed(2));
  set(g('rim'), 'opacity', clamp(pulse * .38, 0, .7).toFixed(2));
  set(el.innerGlow, 'opacity', clamp(pulse * .95, 0, 1).toFixed(2)); set(g('halo'), 'opacity', clamp(.14 + pulse * .42, 0, .75).toFixed(2));
  set(el.innerGlow2, 'opacity', clamp(pulse * .62, 0, 1).toFixed(2));
  set(g('bounce'), 'opacity', clamp(.3 + pulse * .32, 0, .9).toFixed(2)); set(g('windowHl'), 'opacity', (.62 + .2 * (RM ? 0 : Math.sin(t * .6))).toFixed(2));
  set(g('browGlow'), 'opacity', clamp(pulse * .62, 0, .95).toFixed(2));
    const zy = RM ? 0 : (t * 14) % 22;
  set(el.zzz, 'opacity', clamp(cur.zzz, 0, 1).toFixed(2)); set(el.zzz, 'transform', `translate(0 ${-zy.toFixed(1)})`);

  // світло сцени: від позиції ядра
  const cr = el.coreG.getBoundingClientRect(), hr = hero.getBoundingClientRect();
  const cx = cr.left + cr.width / 2 - hr.left, cy = cr.top + cr.height / 2 - hr.top;
  coreXY.x = cx; coreXY.y = cy;
  const lp = (Math.max(cur.lp, .05) + lay.ember * .3 + lay.flare * .35) * (1 + (RM ? 0 : .05 * br));
  const night = emo === 'sleepy';
  const rs = document.documentElement.style;
  rs.setProperty('--lx', cx.toFixed(0) + 'px'); rs.setProperty('--ly', cy.toFixed(0) + 'px'); rs.setProperty('--glow', lp.toFixed(3)); rs.setProperty('--sat', clamp(cur.sat, .6, 1.3).toFixed(3));
  el.light.style.opacity = clamp(lp * (night ? .36 : .34), 0, .8).toFixed(3);
  el.light.style.transform = `translate(${cx.toFixed(1)}px, ${cy.toFixed(1)}px) scale(${(.5 + lp * .5).toFixed(3)})`;
  // контактна тінь і калюжа світла на підлозі
  const lift = clamp(-y / 40, 0, 1);
  el.contact.style.transform = `scale(${(1 - lift * .32).toFixed(3)}, ${(1 - lift * .3).toFixed(3)})`;
  el.contact.style.opacity = (night ? .3 : .85) * (1 - lift * .5);
  el.pool.style.opacity = clamp(.2 + lp * .5, 0, .95).toFixed(3);
  el.pool.style.transform = `scale(${(.7 + lp * .3).toFixed(3)}, ${(.8 + lp * .2).toFixed(3)})`;

  // підсвічування літер заголовка: спад від відстані до ядра; у «що світиться» — від найближчої літери до найдальшої
  if (still || (frame++ & 1) === 0) {
    nmFlash = Math.max(0, nmFlash - dt / 1.4); { const v = nmFlash.toFixed(2); if (v !== nmShown) { nmShown = v; $('#greetH').style.setProperty('--nf', v); } }
    const R = (night ? 560 : 900) * (.5 + lp * .5);
    let dmin = 1e9, dmax = 0;
    for (const L_ of letters) { L_.d = Math.hypot(L_.x - cx, L_.y - cy); if (L_.glow) { dmin = Math.min(dmin, L_.d); dmax = Math.max(dmax, L_.d); } }
    const span = Math.max(1, dmax - dmin), amp = clamp(lp, 0, 1.25);
    for (const L_ of letters) {
      let l = Math.pow(clamp(1 - L_.d / R, 0, 1), 1.5) * clamp(lp * .9, 0, 1.15);
      if (L_.glow) { const near = 1 - (L_.d - dmin) / span; l = Math.max(l, (.06 + .94 * Math.pow(near, 1.35)) * clamp(amp * .9, 0, 1)); }
      if (L_.nm) l = Math.max(l, clamp(.82 + nmFlash * .18, 0, 1));
      l = Math.round(clamp(l, 0, 1) * 40) / 40;
      if (l !== L_.l) { L_.l = l; L_.el.style.setProperty('--l', l); }
    }
  }
}

function loop(now) {
  const dt = Math.min(.05, (now - lastT) / 1000); lastT = now;
  draw(dt); drawDust(dt);
  requestAnimationFrame(loop);
}

/* ---------- моргання, поведінка в спокої ---------- */
(function blinkLoop() {
  if (RM) return;
  const go = () => {
    if (emo !== 'sleepy' && emo !== 'celebrate') { lay.blink = 1; if (Math.random() < .2) setTimeout(() => lay.blink = 1, 260); }
    setTimeout(go, rnd(3000, 6000));
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
let typeI = 0;
const srSay = $('#srSay');
function say(text, ms = 6000) {
  if (!text) return;
  const t = nb(text);
  clearInterval(typeI);
  bubbleText.innerHTML = '<span class="done"></span><span class="rest"></span>';
  const dn = bubbleText.firstChild, rs = bubbleText.lastChild;
  rs.textContent = t; fitBubble(); srSay.textContent = text;
  bubble.classList.remove('on'); void bubble.offsetWidth; bubble.classList.add('on');
  if (!RM) { let i = 0; typeI = setInterval(() => { i += 1; dn.textContent = t.slice(0, i); rs.textContent = t.slice(i); if (i >= t.length) clearInterval(typeI); }, 24); }
  else { dn.textContent = t; rs.textContent = ''; }
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
addEventListener('pointerdown', e => { aimAt(e.clientX, e.clientY); activity(); if (e.target.closest && e.target.closest('#lumo')) hero.classList.add('touched'); }, { passive: true });
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
el.svg.addEventListener('click', e => {
  activity(); pinned = false; lay.wave = 1; hero.classList.add('touched');
  { const r = el.svg.getBoundingClientRect(); lay.jx = clamp((e.clientX - (r.left + r.width / 2)) / (r.width / 2), -1, 1); lay.ja = 1; lay.jt = 0; lay.flare = 1; }
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
}, { passive: true });

/* ---------- ім’я ---------- */
const form = $('#nameForm'), input = $('#guestName');
let guest = '', typing = false, typeT = 0;
input.addEventListener('input', () => {
  activity();
  $('#nameBtn').disabled = !input.value.trim();
  lay.emberT = Math.min(1, input.value.trim().length / 7); lay.kick = 1;
  if (pinned) return;
  typing = true; if (emo !== 'think') { setEmo('think'); say(L().typing, 0); }
  clearTimeout(typeT); typeT = setTimeout(() => { typing = false; if (emo === 'think' && !pinned) setEmo('idle'); }, 1800);
});
function esc(s) { return s.replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c])); }
function ctaText() { return U().trial; }
function buildGreet() {
  const gh = $('#greetH'), tpl = U().greet, k = tpl.indexOf('{n}');
  const pre = tpl.slice(0, k).trim(), post = tpl.slice(k + 3);
  gh.textContent = '';
  const mk = (txt, cls) => { const f = document.createDocumentFragment(); txt.split(' ').forEach((w, wi) => { if (wi) f.append(' '); const sp = document.createElement('span'); sp.className = 'w'; for (const c of w) { const x = document.createElement('span'); x.className = 'ch' + (cls ? ' ' + cls : ''); x.textContent = c; sp.append(x); } f.append(sp); }); return f; };
  const l1 = document.createElement('span'); l1.className = 'ln'; l1.setAttribute('aria-hidden', 'true'); l1.append(mk(pre));
  const l2 = document.createElement('span'); l2.className = 'ln ln-glow'; l2.setAttribute('aria-hidden', 'true'); l2.append(mk(vocative(guest), 'nmc')); l2.append(mk(post));
  gh.append(l1, l2); gh.setAttribute('aria-label', tpl.replace('{n}', vocative(guest)));
  $('#kicker').textContent = cap(U().a + ' ' + U().b);
  gh.hidden = false; hero.classList.add('named');
  fitH1(); cacheLetters();
}
form.addEventListener('submit', e => {
  e.preventDefault(); activity();
  const name = input.value.replace(/\s+/g, ' ').trim().slice(0, 24);
  typing = false; clearTimeout(typeT); pinned = false;
  if (!name) { setEmo('joy', { hold: 2400 }); say(L().noname); return; }
  guest = name;
  form.hidden = true; $('#leadHint').hidden = true; $('#greet').hidden = false; $('#ctaT').textContent = ctaText();
  buildGreet();
  lay.emberT = 0; lay.flare = 1;
  setEmo('celebrate', { hold: 3400 }); say(L().named, 8000);
  // Люмо розвертається до кнопки і дивиться на неї
  lay.turnT = -1; lay.wave = 1;
  { const b = $('#cta').getBoundingClientRect(); aimAt(b.left + b.width / 2, b.top + b.height / 2); lay.lookX = -.95; lay.lookY = .6; lay.pointerAt = performance.now() + 14000; }
  setTimeout(() => burst(), RM ? 0 : 380);
});
$('#changeName').addEventListener('click', () => {
  guest = ''; hero.classList.remove('named'); $('#greetH').hidden = true; lay.turnT = 0; lay.emberT = 0;
  $('#leadHint').hidden = false; $('#greet').hidden = true; form.hidden = false; input.value = ''; $('#nameBtn').disabled = true; input.focus(); setEmo('idle'); applyText();
});

/* ================= ЧАСТИНКИ (тільки після імені) ================= */
const cv = $('#fx'), cx2 = cv.getContext('2d');
let parts = [], running = false, DPR = 1;
function sizeCanvas() { DPR = Math.min(2, devicePixelRatio || 1); cv.width = hero.clientWidth * DPR; cv.height = hero.clientHeight * DPR; }
/* Частинки-подія: вилітають з Люмо → частина летить до імені й «запалює» його (--l), решта осідає ореолом навколо Люмо. */
function burst() {
  if (RM) { nmFlash = 1; return; }
  sizeCanvas();
  const COLS = ['#FF7A45', '#FF9A66', '#FF5F25', '#FFB27E', '#FFD9A8'];
  const hr = hero.getBoundingClientRect(), sr = el.svg.getBoundingClientRect();
  const x = sr.left - hr.left + sr.width * .5, y = sr.top - hr.top + sr.height * .5, R0 = sr.height * .3;
  const nm = letters.filter(l => l.nm);
  for (let i = 0; i < 70; i++) {
    const a = rnd(0, Math.PI * 2), v = rnd(220, 560), r0 = R0 * rnd(.2, .9);
    const toName = nm.length && i % 5 < 2;
    let tx, ty;
    if (toName) { const l = nm[(Math.random() * nm.length) | 0]; tx = l.x + rnd(-14, 14); ty = l.y + rnd(-18, 18); }
    else { const b = rnd(0, Math.PI * 2), rr = sr.height * rnd(.5, .62); tx = x + Math.cos(b) * rr * .82; ty = y + Math.sin(b) * rr * .95; }
    parts.push({ x: x + Math.cos(a) * r0, y: y + Math.sin(a) * r0, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 90, r: rnd(3, 8), life: 0, burstT: rnd(.35, .6), tx, ty, toName, settled: 0, c: COLS[i % COLS.length], star: i % 5 === 0, rot: rnd(0, 6.28), vr: rnd(-6, 6), tw: rnd(0, 6.28) });
  }
  if (!running) { running = true; lastP = performance.now(); requestAnimationFrame(stepP); }
}
let lastP = 0;
function stepP(now) {
  const dt = Math.min(.04, (now - lastP) / 1000); lastP = now;
  cx2.setTransform(DPR, 0, 0, DPR, 0, 0); cx2.clearRect(0, 0, cv.width, cv.height);
  cx2.save(); cx2.beginPath(); cx2.rect(0, 0, cv.width / DPR, cv.height / DPR);
  { const hr = hero.getBoundingClientRect(); for (const sel of ['#meet', '#bubble']) { const r = $(sel).getBoundingClientRect(); if (!r.width) continue; const pad = 10; cx2.rect(r.left - hr.left - pad, r.top - hr.top - pad, r.width + pad * 2, r.height + pad * 2); } }
  cx2.clip('evenodd');
  parts = parts.filter(p => p.settled < 1);
  for (const p of parts) {
    p.life += dt; p.rot += p.vr * dt;
    let a = 1;
    if (p.life < p.burstT) { p.vx *= 1 - 2.2 * dt; p.vy *= 1 - 2.2 * dt; p.x += p.vx * dt; p.y += p.vy * dt; }
    else {
      const k = 1 - Math.exp(-dt * (p.toName ? 5.5 : 2.6));
      p.x += (p.tx - p.x) * k + p.vx * dt * .2; p.y += (p.ty - p.y) * k + p.vy * dt * .2; p.vx *= 1 - 3 * dt; p.vy *= 1 - 3 * dt;
      const d = Math.hypot(p.tx - p.x, p.ty - p.y);
      if (p.toName) { if (d < 16) { p.settled = 1; nmFlash = Math.min(1, nmFlash + .09); } }
      else { p.settled += dt / 2.6; a = (1 - p.settled) * (.55 + .45 * Math.sin(p.tw + p.life * 5)); p.y -= dt * 4; }
    }
    a = clamp(a, 0, 1);
    cx2.globalAlpha = a; cx2.fillStyle = p.c;
    if (p.star) { cx2.save(); cx2.translate(p.x, p.y); cx2.rotate(p.rot); const s2 = p.r * 1.8; cx2.beginPath(); cx2.moveTo(0, -s2); cx2.lineTo(s2 * .28, -s2 * .28); cx2.lineTo(s2, 0); cx2.lineTo(s2 * .28, s2 * .28); cx2.lineTo(0, s2); cx2.lineTo(-s2 * .28, s2 * .28); cx2.lineTo(-s2, 0); cx2.lineTo(-s2 * .28, -s2 * .28); cx2.closePath(); cx2.fill(); cx2.restore(); }
    else { cx2.beginPath(); cx2.arc(p.x, p.y, p.r * (.5 + a * .5), 0, 6.283); cx2.fill(); }
  }
  cx2.restore();
  if (parts.length) requestAnimationFrame(stepP); else { running = false; cx2.clearRect(0, 0, cv.width, cv.height); }
}

/* ================= ПИЛИНКИ-БОКЕ (над і під Люмо) ================= */
const dB = $('#dustB'), dF = $('#dustF'), dBx = dB.getContext('2d'), dFx = dF.getContext('2d');
const mkSprite = c0 => { const c = document.createElement('canvas'); c.width = c.height = 64; const x = c.getContext('2d'), gr = x.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, `rgba(${c0},1)`); gr.addColorStop(.4, `rgba(${c0},.55)`); gr.addColorStop(1, `rgba(${c0},0)`); x.fillStyle = gr; x.fillRect(0, 0, 64, 64); return c; };
const SPR = [mkSprite('255,236,208'), mkSprite('255,138,70')];
const DUST = Array.from({ length: 24 }, (_, i) => { const front = i < 7; return { x: Math.random(), y: rnd(.18, 1), r: front ? rnd(22, 46) : (i < 14 ? rnd(3, 7) : rnd(10, 22)), a: front ? rnd(.16, .3) : rnd(.45, .85), sp: rnd(5, 14), ph: rnd(0, 6.28), sw: rnd(8, 26), front }; });
let dustT = 0, dustW = 0, dustH = 0;
function sizeDust() { dustW = dB.width = dF.width = Math.round(hero.clientWidth / 2); dustH = dB.height = dF.height = Math.round(hero.clientHeight / 2); }
function drawDust(dt, still) {
  if (!dustW) sizeDust();
  dustT += dt;
  dBx.clearRect(0, 0, dustW, dustH); dFx.clearRect(0, 0, dustW, dustH);
  const night = emo === 'sleepy', dim = night ? .55 : 1;
  for (const p of DUST) {
    if (!RM && !still) { p.y -= p.sp * dt / dustH * 2; if (p.y < .16) { p.y = 1.06; p.x = Math.random(); } }
    const x = p.x * dustW + (RM ? 0 : Math.sin(dustT * .35 + p.ph) * p.sw), y = p.y * dustH;
    const tw = RM ? 1 : .72 + .28 * Math.sin(dustT * 1.1 + p.ph * 3);
    const c = p.front ? dFx : dBx, r = p.r / 2;
    c.globalAlpha = p.a * tw * dim; c.drawImage(SPR[p.front ? 0 : 1], x - r, y - r, r * 2, r * 2);
  }
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

/* ---------- «Пробний урок»: заглушка ---------- */
$$('#trialQ, #cta, #trialM').forEach(a => a.addEventListener('click', e => { e.preventDefault(); activity(); say(L().stub, 5000); }));

/* ================= МОВИ ================= */
const langBtn = $('#langBtn'), langList = $('#langList');
function openLang(o) { hero.classList.toggle('lang-open', o); langList.hidden = !o; langBtn.setAttribute('aria-expanded', String(o)); if (o) { (langList.querySelector('[aria-selected="true"]') || langList.firstElementChild).focus?.(); } }
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
addEventListener('resize', () => { fitH1(); cacheLetters(); sizeCanvas(); sizeDust(); drawDust(0, true); if (RM) draw(0, true); });
applyText(); fitBubble();
if (!(document.fonts && document.fonts.ready)) document.documentElement.classList.add('fonts-ok');
if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { fitBubble(); document.documentElement.classList.add('fonts-ok'); fitH1(); cacheLetters(); if (RM) draw(0, true); });

const q = new URLSearchParams(location.search);
if (q.get('clear') === '1') hero.classList.add('think-clear');
if (q.get('demo') === '1') document.documentElement.classList.add('demo');
const emoQ = q.get('emo');
if (emoQ && E[emoQ]) { setEmo(emoQ, { pin: true }); say(L()[{ idle:'hello', joy:'joy', curious:'curious', think:'think', celebrate:'celebrate', sleepy:'sleepy' }[emoQ]], 0); } else { setEmo('idle'); bubbleText.textContent = nb(L().hello); fitBubble(); bubble.classList.add('on'); }
if (q.get('lang') && UI[q.get('lang')]) { lang = q.get('lang'); applyText(); }
activity();
draw(0, true);
if (!RM) requestAnimationFrame(loop);
drawDust(0, true);
window.__lumo = { setEmo, burst, say, draw: () => draw(0, true), get emo() { return emo; } };
})();
