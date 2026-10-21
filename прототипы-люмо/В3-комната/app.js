/* LUMOSCHOOL · В3 «Кімната уроку». Без мережі: усе в пам'яті сторінки. */
const i18n = {
  uk: {
    lesson: 'Урок · Present Simple', recOff: 'Запис вимкнено', sos: 'Вийти / покликати власника',
    lumoAria: 'Люмо. Натисни, щоб змінити стан (демо)',
    eListen: 'Слухає', eThink: 'Думає', eJoy: 'Радіє', eRest: 'Чекає', elapsed: 'Іде',
    stListen: 'Люмо слухає', subListen: 'Говорить Олена. Люмо світить тихо.',
    stThink: 'Люмо думає', subThink: 'Дивиться, що ти зробив. Не поспішай.',
    stJoy: 'Люмо радіє', subJoy: 'Це правильно! Світла стало більше.',
    stRest: 'Люмо чекає', subRest: 'Тихо. Можна подумати чи написати в чат.',
    camOff: 'Камера вимкнена', teacher: 'викладачка', muted: 'без звуку',
    boardH: 'Дошка', boardHint: 'Завдання від викладачки · демо',
    ex1t: 'Вибери слово', ex2t: 'Склади речення', check: 'Перевірити', reset: 'Спочатку',
    built: 'Торкайся слів по черзі',
    fbOk1: 'Так! З «she» дієслово отримує -es.', fbBad1: 'Майже. Подумай про «she»: що додаємо до дієслова?',
    fbOk2: 'Чудово, речення складене правильно.', fbBad2: 'Ще не зовсім. Порядок слів: хто, як часто, що робить.', fbEmpty2: 'Спершу склади речення зі слів.',
    chatH: 'Чат уроку', chatNote: 'лише в цій кімнаті', msgLabel: 'Повідомлення', msgPh: 'Повідомлення…', send: 'Надіслати',
    tabBoard: 'Дошка', tabChat: 'Чат', me: 'Ти', now: 'щойно',
    sosH: 'Що трапилось?', sosP: 'Урок для інших триватиме. Дорослий почує тебе одразу.', sosReasonsAria: 'Що трапилось?',
    sosR1: 'Щось не працює', sosR2: 'Мені незручно чи страшно', sosR3: 'Інше',
    sosOwner: 'Покликати дорослого', sosLeave: 'Вийти з уроку', sosStay: 'Залишитись',
    sosH2: 'Тебе почули, дорослий іде', sosP2: 'Лишайся на місці. Урок для інших триває.', sosOk: 'Добре',
    stSos: 'Люмо поруч', subSos: 'Ти не сам. Можна покликати дорослого.', subSos2: 'Дорослий уже йде до тебе.',
    sosCalled: 'Тебе почули, дорослий іде.', sosLeft: 'Ти вийшов з уроку.',
    inc: 'Марко, а ти як думаєш?',
    chat: [['Олена К.', 'teacher', 'Привіт усім! Сьогодні говоримо про щоденні справи.', '18:41'],
           ['Марко Л.', '', 'Hello! Я готовий.', '18:41'],
           ['Софія Р.', '', 'Can I start?', '18:42'],
           ['Олена К.', 'teacher', 'Yes, Sofia. Починай із першої вправи на дошці.', '18:42']]
  },
  en: {
    lesson: 'Lesson · Present Simple', recOff: 'Recording is off', sos: 'Leave / call the school owner',
    lumoAria: 'Lumo. Press to change the state (demo)',
    eListen: 'Listening', eThink: 'Thinking', eJoy: 'Delighted', eRest: 'Waiting', elapsed: 'Elapsed',
    stListen: 'Lumo is listening', subListen: 'Olena is speaking. Lumo glows quietly.',
    stThink: 'Lumo is thinking', subThink: 'Looking at your answer. Take your time.',
    stJoy: 'Lumo is delighted', subJoy: 'That is right! The room got brighter.',
    stRest: 'Lumo is waiting', subRest: 'Quiet. You can think or write in the chat.',
    camOff: 'Camera is off', teacher: 'teacher', muted: 'muted',
    boardH: 'Board', boardHint: 'Tasks from the teacher · demo',
    ex1t: 'Pick the word', ex2t: 'Build the sentence', check: 'Check', reset: 'Start over',
    built: 'Tap the words one by one',
    fbOk1: 'Yes! After “she” the verb takes -es.', fbBad1: 'Almost. Think about “she”: what do we add to the verb?',
    fbOk2: 'Well done, the sentence is correct.', fbBad2: 'Not quite. Word order: who, how often, what they do.', fbEmpty2: 'Build the sentence from the words first.',
    chatH: 'Lesson chat', chatNote: 'only in this room', msgLabel: 'Message', msgPh: 'Message…', send: 'Send',
    tabBoard: 'Board', tabChat: 'Chat', me: 'You', now: 'now',
    sosH: 'What happened?', sosP: 'The lesson goes on for the others. A grown-up will hear you right away.', sosReasonsAria: 'What happened?',
    sosR1: 'Something does not work', sosR2: 'I feel uneasy or scared', sosR3: 'Something else',
    sosOwner: 'Call a grown-up', sosLeave: 'Leave the lesson', sosStay: 'Stay',
    sosH2: 'We heard you, a grown-up is coming', sosP2: 'Stay where you are. The lesson goes on for the others.', sosOk: 'OK',
    stSos: 'Lumo is here', subSos: 'You are not alone. You can call a grown-up.', subSos2: 'A grown-up is on the way.',
    sosCalled: 'We heard you, a grown-up is coming.', sosLeft: 'You left the lesson.',
    inc: 'Marko, what do you think?',
    chat: [['Olena K.', 'teacher', 'Hi everyone! Today we talk about daily routines.', '18:41'],
           ['Marko L.', '', 'Hello! I am ready.', '18:41'],
           ['Sofia R.', '', 'Can I start?', '18:42'],
           ['Olena K.', 'teacher', 'Yes, Sofia. Start with the first exercise on the board.', '18:42']]
  }
};
const names = { uk: { t: 'Олена К.', s1: 'Марко Л.', s2: 'Софія Р.' }, en: { t: 'Olena K.', s1: 'Marko L.', s2: 'Sofia R.' } };
const inits = { uk: ['ОК', 'МЛ', 'СР'], en: ['OK', 'ML', 'SR'] };
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const room = $('#room');
let lang = 'uk', emo = 'listen', unread = 0, built = [], timer = 0;
const msgs = []; // {kind, text, time, seedIdx?, who?}
const t = k => i18n[lang][k];
const WORDS = ['always', 'I', 'breakfast', 'have', 'at eight'];
const ANSWER = 'I always have breakfast at eight';

/* ---- Люмо ---- */
const EMO_KEY = { listen: 'Listen', think: 'Think', joy: 'Joy', rest: 'Rest', sos: 'Sos' };
let sosStep = null; // null | 'choose' | 'called': SOS перебиває будь-яку емоцію
function setEmo(e, hold) {
  emo = e;
  const shown = sosStep ? 'sos' : e; room.dataset.emo = shown;
  const k = EMO_KEY[shown];
  $('#lampState').textContent = t('st' + k);
  $('#lampSub').textContent = shown === 'sos' && sosStep === 'called' ? t('subSos2') : t('sub' + k);
  $$('#demo button').forEach(b => b.setAttribute('aria-pressed', b.dataset.emo === emo));
  clearTimeout(timer);
  if (hold && !sosStep) timer = setTimeout(() => setEmo('listen'), hold);
}
function placeLight() { // джерело світла = ядро Люмо (cx 103/200, cy 78/250 у viewBox; рахуємо від нерухомого боксу кнопки)
  const r = $('#lumoBtn').getBoundingClientRect(), rr = room.getBoundingClientRect();
  const k = r.width / 200, cx = r.left + 103 * k, cy = r.top + 78 * k;
  room.style.setProperty('--lx', (cx - rr.left) + 'px');
  room.style.setProperty('--ly', (cy - rr.top) + 'px');
  gaze(r, k);
}
function gaze(r, k) { // Люмо дивиться на головну дію екрана («Перевірити»)
  const tg = $('#check'); if (!tg || !tg.offsetParent) return;
  const b = tg.getBoundingClientRect(), ex = r.left + 100 * k, ey = r.top + 148 * k;
  const dx = b.left + b.width / 2 - ex, dy = b.top + b.height / 2 - ey, d = Math.hypot(dx, dy) || 1;
  const L = $('#lumo'); L.style.setProperty('--gx', (dx / d * 5).toFixed(2) + 'px'); L.style.setProperty('--gy', (dy / d * 6).toFixed(2) + 'px');
}
addEventListener('resize', placeLight);
$('#lumoBtn').addEventListener('click', () => { const d = $('#demo'); d.hidden = !d.hidden; $('#lumoBtn').setAttribute('aria-expanded', String(!d.hidden)); });
$$('#demo button').forEach(b => b.addEventListener('click', () => { setEmo(b.dataset.emo); $('#demo').hidden = true; $('#lumoBtn').setAttribute('aria-expanded', 'false'); }));

/* ---- мова ---- */
function applyLang(l) {
  lang = l; document.documentElement.lang = l;
  $$('[data-i]').forEach(n => n.textContent = t(n.dataset.i));
  $$('[data-i-ph]').forEach(n => n.placeholder = t(n.dataset.iPh));
  $$('[data-i-aria]').forEach(n => n.setAttribute('aria-label', t(n.dataset.iAria)));
  $$('.langs button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.lang === l)));
  $$('.arch').forEach((a, i) => { $('b', a).textContent = names[l][a.dataset.who]; $('.ini', a).textContent = inits[l][i]; });
  $('#built').dataset.ph = t('built');
  $('#sosRes').textContent = '';
  renderChat(); setEmo(emo);
}
$$('.langs button').forEach(b => b.addEventListener('click', () => applyLang(b.dataset.lang)));

/* ---- вправа 1 ---- */
$$('#opts1 button').forEach(b => b.addEventListener('click', () => {
  const ok = b.dataset.v === 'goes';
  $$('#opts1 button').forEach(x => x.classList.remove('bad'));
  $('#gap1').textContent = b.dataset.v;
  void b.offsetWidth;
  if (ok) { b.classList.add('ok'); $$('#opts1 button').forEach(x => x.disabled = !x.classList.contains('ok')); $('#fb1').textContent = t('fbOk1'); setEmo('joy', 4200); }
  else { b.classList.add('bad'); $('#fb1').textContent = t('fbBad1'); setEmo('think', 2600); }
}));
/* ---- вправа 2 ---- */
function renderWords() {
  const pool = $('#pool'); pool.textContent = '';
  WORDS.forEach(w => { const b = document.createElement('button'); b.type = 'button'; b.textContent = w; b.disabled = built.includes(w);
    b.addEventListener('click', () => { built.push(w); renderWords(); }); pool.append(b); });
  const bl = $('#built'); bl.textContent = '';
  built.forEach((w, i) => { const s = document.createElement('span'); s.textContent = w; s.tabIndex = 0; s.setAttribute('role', 'button');
    const undo = () => { built.splice(i, 1); renderWords(); };
    s.onclick = undo; s.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); undo(); } }; bl.append(s); });
}
$('#reset').addEventListener('click', () => { built = []; $('#fb2').textContent = ''; renderWords(); });
$('#check').addEventListener('click', () => {
  if (!built.length) { $('#fb2').textContent = t('fbEmpty2'); return; }
  if (built.join(' ') === ANSWER) { $('#fb2').textContent = t('fbOk2'); setEmo('joy', 4200); }
  else { $('#fb2').textContent = t('fbBad2'); setEmo('think', 2600); }
  $('#fb2').scrollIntoView({ block: 'nearest' });
});

/* ---- чат (лише в пам'яті сторінки) ---- */
function msgEl(m) {
  const seed = m.seedIdx != null ? t('chat')[m.seedIdx] : null;
  const li = document.createElement('li'); li.className = 'msg ' + (m.kind || '');
  const h = document.createElement('div'); h.className = 'msg-h';
  const b = document.createElement('b'); b.textContent = m.kind === 'me' ? t('me') : seed ? seed[0] : names[lang].t;
  const tm = document.createElement('time'); tm.textContent = m.time === 'now' ? t('now') : m.time;
  h.append(b, tm); const p = document.createElement('p'); p.textContent = seed ? seed[2] : m.inc ? t('inc') : m.text; li.append(h, p); return li;
}
function renderChat() {
  if (!msgs.length) t('chat').forEach((c, i) => msgs.push({ kind: c[1], time: c[3], seedIdx: i }));
  const ol = $('#msgs'); ol.textContent = ''; msgs.forEach(m => ol.append(msgEl(m))); ol.scrollTop = ol.scrollHeight;
}
function push(m) { msgs.push(m); const ol = $('#msgs'); ol.append(msgEl(m)); ol.scrollTop = ol.scrollHeight; }
$('#sendForm').addEventListener('submit', e => {
  e.preventDefault(); const inp = $('#msgIn'), v = inp.value.trim(); if (!v) return;
  push({ kind: 'me', text: v, time: 'now' }); inp.value = ''; setEmo('think', 1800);
});
function incoming() {
  push({ kind: 'teacher', inc: true, time: 'now' });
  if (room.dataset.tab !== 'chat') { unread++; const b = $('#badge'); b.hidden = false; b.textContent = unread; }
}
window.__room = { incoming, setEmo };

/* ---- вкладки (телефон) ---- */
function setTab(tab) {
  room.dataset.tab = tab; $$('.tabs button').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.tab === tab)));
  if (tab === 'chat') { unread = 0; $('#badge').hidden = true; const ol = $('#msgs'); ol.scrollTop = ol.scrollHeight; }
}
$$('.tabs button').forEach(b => b.addEventListener('click', () => setTab(b.dataset.tab)));

/* ---- аварійний аркуш ---- */
const dlg = $('#sosDlg');
function sosShow(step) {
  sosStep = step; dlg.dataset.step = step;
  $('#sosA').hidden = step !== 'choose'; $('#sosB').hidden = step !== 'called';
  dlg.setAttribute('aria-labelledby', step === 'choose' ? 'sosH' : 'sosH2');
  setEmo(emo);
  (step === 'choose' ? $('#sosOwner') : $('#sosOk')).focus();
}
function sosClose() { dlg.close(); }
$('#sos').addEventListener('click', () => { $$('#reasons button').forEach(b => b.setAttribute('aria-pressed', 'false')); $('#sosRes').textContent = ''; dlg.showModal(); sosShow('choose'); });
dlg.addEventListener('close', () => { sosStep = null; setEmo(emo); });
dlg.addEventListener('cancel', () => { /* Esc = «Залишитись» */ });
$$('#reasons button').forEach(b => b.addEventListener('click', () => $$('#reasons button').forEach(x => x.setAttribute('aria-pressed', String(x === b && x.getAttribute('aria-pressed') !== 'true')))));
$('#sosStay').addEventListener('click', sosClose);
$('#sosOk').addEventListener('click', sosClose);
$('#sosOwner').addEventListener('click', () => { sosShow('called'); $('#sosRes').textContent = t('sosCalled'); });
$('#sosLeave').addEventListener('click', () => { $('#sosRes').textContent = t('sosLeft'); emo = 'rest'; sosClose(); });

/* ---- годинник ---- */
let sec = 23 * 60 + 10; const fmt = n => String(n).padStart(2, '0');
setInterval(() => { sec++; $('#clock').textContent = fmt(Math.floor(sec / 60)) + ':' + fmt(sec % 60); }, 1000);
$('#clock').textContent = '23:10';

/* ---- старт ---- */
renderWords(); applyLang('uk');
const q = new URLSearchParams(location.search);
if (q.get('emo')) setEmo(q.get('emo'));
if (q.get('tab')) setTab(q.get('tab'));
document.fonts.ready.then(placeLight); placeLight();
if (!q.get('still')) setTimeout(incoming, 6000);
