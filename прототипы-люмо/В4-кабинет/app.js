/* LUMOSCHOOL · В4 «Кабінет». Без мережі: усе в пам'яті сторінки, дані вигадані.
   Час поясу рахує Intl (Europe/Warsaw, Europe/Kyiv), «зараз» — зафіксована демо-дата. */
const i18n = {
  uk: {
    loc: 'uk-UA', tzAria: 'Часовий пояс', langAria: 'Мова інтерфейсу', tzW: 'Варшава', tzK: 'Київ',
    lumoAria: 'Люмо. Натисніть, щоб змінити стан (демо)', demoAria: 'Стан Люмо (демо)', demoDay: 'День', demoEmo: 'Люмо',
    dFar: 'Урок за 2 год', dNear: 'Урок за 8 хв', eRest: 'Відпочиває', eWait: 'Чекає урок', eJoy: 'Радіє', eThink: 'Думає',
    hello: n => `Добрий вечір, <em>${n}</em>`, name: 'Аню',
    subFar: 'Сьогодні у вас один урок. До нього ще є час: можна записатися на наступні чи переглянути матеріали.',
    subNear: 'Урок ось-ось почнеться. Люмо вже чекає біля дверей кімнати.',
    nextH: 'Найближчий урок', untilStart: 'до початку', started: 'урок іде', inRoom: 'Урок у кімнаті',
    enter: 'Увійти в кімнату', enterClosed: 'Кімната ще зачинена',
    noteClosed: t => `Кнопка стане активною за 10 хвилин до початку, о ${t}.`, noteOpen: 'Кімната відчинена. Можна заходити.',
    groupWord: 'Група', with: 'викладач', 
    stRest: 'Люмо відпочиває', subRest: 'Урок ще не скоро. Світить тихо, нікуди не поспішає.',
    stWait: 'Люмо чекає урок', subWaitC: 'Світло росте. Кімната відчиниться за 10 хвилин до початку.', subWaitO: 'Кімната відчинена. Люмо чекає вас там.',
    stJoy: 'Люмо радіє', subJoy: 'Вас записано. Світла стало більше.',
    stThink: 'Люмо думає', subThink: 'Не поспішайте, подумайте.',
    bookH: 'Запис на урок', bookNote: z => `Час показано за поясом: <b>${z}</b>. Перемкнути можна вгорі.`,
    seatsOf: (a, b) => `Вільних місць: ${a} з ${b}`, full: 'Місць немає', book: 'Записатися', booked: 'Ви записані', bookFull: 'Заповнено',
    mineH: 'Мої записи', rule: 'Безкоштовно скасувати можна не пізніше ніж за 12 годин до початку. Пізніше урок вважається проведеним.',
    cancelUntil: t => `Скасувати можна до ${t}`, cancelLate: 'Скасувати вже не можна: до початку менше 12 годин.',
    cancel: 'Скасувати запис', ask: 'Скасувати цей запис?', askNote: t => `Місце звільниться для інших учнів. Безкоштовно скасувати можна до ${t}, пізніше урок вважається проведеним.`, yes: 'Так, скасувати', keep: 'Залишити',
    statBooked: 'Запис додано. Він у списку нижче.', statCancel: 'Запис скасовано. Місце знову вільне.', empty: 'Записів немає. Оберіть урок у списку вище.',
    matsH: 'Матеріали до уроків', hw: 'Домашнє завдання', due: 'здати до', open: 'Відкрити', submit: 'Здати', done: 'Здано', todo: 'Не здано', doneOn: 'здано', lesson: 'Урок',
    progH: 'Прогрес', levelK: 'Ваш рівень', levelW: 'початок B1 · середній рівень', doneH: 'Що вже виходить', nextUp: 'Що далі',
    progNote: 'Нотатки оновлює викладач після кожного місяця занять.',
    done1: ['Розповідаєте про свій день і плани простими реченнями', 'Розумієте повільну розмову на знайомі теми', 'Пишете коротке повідомлення без грубих помилок'],
    next1: ['Говорити про минуле з Present Perfect', 'Розуміти розмову в звичайному темпі', 'Розповідати історію зв’язно, без довгих пауз'],
    privacy: 'Тут видно лише ваші дані. Інших учнів і контакти викладачів ви не бачите: у викладача відображається тільки ім’я та роль.',
    roleT: 'викладач', roleTf: 'викладачка',
    cefr: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'], cefrNow: 'зараз'
  },
  en: {
    loc: 'en-GB', tzAria: 'Time zone', langAria: 'Interface language', tzW: 'Warsaw', tzK: 'Kyiv',
    lumoAria: 'Lumo. Press to change the state (demo)', demoAria: 'Lumo state (demo)', demoDay: 'Day', demoEmo: 'Lumo',
    dFar: 'Lesson in 2 h', dNear: 'Lesson in 8 min', eRest: 'Resting', eWait: 'Waiting for lesson', eJoy: 'Delighted', eThink: 'Thinking',
    hello: n => `Good evening, <em>${n}</em>`, name: 'Anya',
    subFar: 'You have one lesson today. There is time before it: book the next ones or look through your materials.',
    subNear: 'Your lesson is about to start. Lumo is already waiting by the door of the room.',
    nextH: 'Next lesson', untilStart: 'until it starts', started: 'lesson in progress', inRoom: 'Lesson in the room',
    enter: 'Enter the room', enterClosed: 'The room is still closed',
    noteClosed: t => `The button becomes active 10 minutes before the start, at ${t}.`, noteOpen: 'The room is open. You can go in.',
    groupWord: 'Group', with: 'teacher',
    stRest: 'Lumo is resting', subRest: 'The lesson is a while away. Glowing quietly, in no hurry.',
    stWait: 'Lumo is waiting', subWaitC: 'The light grows. The room opens 10 minutes before the start.', subWaitO: 'The room is open. Lumo is waiting for you there.',
    stJoy: 'Lumo is delighted', subJoy: 'You are booked. The light got brighter.',
    stThink: 'Lumo is thinking', subThink: 'Take your time, think it over.',
    bookH: 'Book a lesson', bookNote: z => `Times are shown in: <b>${z}</b>. Switch it at the top.`,
    seatsOf: (a, b) => `Free seats: ${a} of ${b}`, full: 'No seats left', book: 'Book', booked: 'You are booked', bookFull: 'Full',
    mineH: 'My bookings', rule: 'You can cancel for free up to 12 hours before the start. After that the lesson counts as taken.',
    cancelUntil: t => `You can cancel until ${t}`, cancelLate: 'Too late to cancel: less than 12 hours to the start.',
    cancel: 'Cancel booking', ask: 'Cancel this booking?', askNote: t => `The seat will be freed for other students. Free cancellation is possible until ${t}; after that the lesson counts as taken.`, yes: 'Yes, cancel', keep: 'Keep it',
    statBooked: 'Booked. It is in the list below.', statCancel: 'Booking cancelled. The seat is free again.', empty: 'No bookings. Pick a lesson from the list.',
    matsH: 'Lesson materials', hw: 'Homework', due: 'due', open: 'Open', submit: 'Hand in', done: 'Handed in', todo: 'Not handed in', doneOn: 'handed in', lesson: 'Lesson',
    progH: 'Progress', levelK: 'Your level', levelW: 'early B1 · intermediate', doneH: 'What you can do now', nextUp: 'What is next',
    progNote: 'Your teacher updates these notes after every month of lessons.',
    done1: ['Tell about your day and plans in simple sentences', 'Follow a slow conversation on familiar topics', 'Write a short message without rough mistakes'],
    next1: ['Talk about the past with the Present Perfect', 'Follow a conversation at normal speed', 'Tell a story smoothly, without long pauses'],
    privacy: 'You only see your own data here. Other students and teachers’ contacts are not shown: a teacher appears with a name and a role only.',
    roleT: 'teacher', roleTf: 'teacher',
    cefr: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'], cefrNow: 'now'
  }
};
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const page = $('#page');
const H = 3600e3, M = 60e3;
const LESSON0 = Date.UTC(2026, 9, 19, 18, 0); // пн 19 жовт, 18:00 UTC = 20:00 Варшава
const SLOT = (id, d, h, mi, group, teacher, left, total) => ({ id, at: Date.UTC(2026, 9, d, h, mi), group, teacher, left, total });
const TEACH = { o: { n: { uk: 'Олена К.', en: 'Olena K.' }, f: 1 }, t: { n: { uk: 'Тарас М.', en: 'Taras M.' }, f: 0 }, i: { n: { uk: 'Іванна Д.', en: 'Ivanna D.' }, f: 1 } };
let slots = [
  SLOT('s1', 20, 16, 0, 'B1 · Conversation', 'i', 4, 6),
  SLOT('s2', 21, 9, 0, 'B1 · Reading', 't', 0, 6),
  SLOT('s3', 21, 17, 30, 'B1 · Speaking', 'o', 2, 6),
  SLOT('s4', 22, 17, 0, 'B1 · Grammar', 't', 2, 6),
  SLOT('s5', 23, 15, 0, 'B1 · Listening', 't', 5, 6),
  SLOT('s6', 24, 9, 0, 'B1 · Speaking club', 'o', 1, 6)
];
let bookings = [
  { id: 'L0', at: LESSON0, group: 'B1 · Speaking', teacher: 'o' },
  { id: 's4', at: Date.UTC(2026, 9, 22, 17, 0), group: 'B1 · Grammar', teacher: 't' }
];
const mats = [
  { at: Date.UTC(2026, 9, 15, 17, 0), title: { uk: 'Present Perfect: вступ', en: 'Present Perfect: intro' }, file: 'present-perfect-intro.pdf',
    hw: { uk: 'Вправи 1–4, речення про свій тиждень', en: 'Exercises 1–4, sentences about your week' }, due: Date.UTC(2026, 9, 18, 18, 0), done: true },
  { at: Date.UTC(2026, 9, 12, 17, 0), title: { uk: 'Подорожі та плани', en: 'Travel and plans' }, file: 'travel-vocabulary.pdf',
    hw: { uk: 'Голосове повідомлення на 1 хвилину', en: 'A one-minute voice note' }, due: Date.UTC(2026, 9, 14, 18, 0), done: true },
  { at: Date.UTC(2026, 9, 8, 17, 0), title: { uk: 'Розмова в кав’ярні', en: 'A conversation at the café' }, file: 'cafe-dialogues.pdf',
    hw: { uk: 'Діалог на 8 реплік', en: 'A dialogue of 8 lines' }, due: Date.UTC(2026, 9, 11, 18, 0), done: false },
  { at: Date.UTC(2026, 9, 5, 17, 0), title: { uk: 'Минулий простий час', en: 'Past Simple review' }, file: 'past-simple-review.pdf',
    hw: { uk: 'Тест із 10 питань', en: 'A 10-question quiz' }, due: Date.UTC(2026, 9, 7, 18, 0), done: true }
];

let lang = 'uk', tz = 'Europe/Warsaw', day = 'far', emo = 'rest', ask = null, status = '', timer = 0, openedRoom = false;
let nowBase = LESSON0 - (2 * H + 14 * M + 5e3), t0 = performance.now();
const now = () => nowBase + (performance.now() - t0);
const t = k => i18n[lang][k];
const teacherName = id => TEACH[id].n[lang];
const role = id => TEACH[id].f ? t('roleTf') : t('roleT');
const fmt = (ms, o) => new Intl.DateTimeFormat(t('loc'), { timeZone: tz, ...o }).format(ms);
const fTime = ms => fmt(ms, { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' });
const fDay = ms => fmt(ms, { weekday: 'short', day: 'numeric', month: 'short' });
const fDayLong = ms => fmt(ms, { weekday: 'long', day: 'numeric', month: 'long' });
const zoneName = () => (tz === 'Europe/Warsaw' ? t('tzW') : t('tzK')) + ' (UTC' + fmt(now(), { timeZoneName: 'shortOffset' }).split('GMT')[1] + ')';
const baseEmo = () => day === 'near' ? 'wait' : 'rest';
const canEnter = () => bookings.length && bookings[0].at - now() <= 10 * M;

/* ---- Люмо ---- */
const EK = { rest: 'Rest', wait: 'Wait', joy: 'Joy', think: 'Think' };
function setEmo(e, hold) {
  emo = e; page.dataset.emo = e;
  const sub = e === 'wait' ? (canEnter() ? 'subWaitO' : 'subWaitC') : 'sub' + EK[e];
  $('#lampState').textContent = t('st' + EK[e]); $('#lampSub').textContent = t(sub);
  $$('#demo [data-emo]').forEach(b => b.setAttribute('aria-pressed', b.dataset.emo === e));
  clearTimeout(timer);
  if (hold) timer = setTimeout(() => setEmo(baseEmo()), hold);
}
function placeLight() { // ядро Люмо = центр света (cx 103/200, cy 78/250), считаем от нерухомого боксу кнопки
  const r = $('#lumoBtn').getBoundingClientRect(), pr = page.getBoundingClientRect();
  const k = r.width / 200, cx = r.left + 103 * k, cy = r.top + 78 * k;
  page.style.setProperty('--lx', (cx - pr.left) + 'px'); page.style.setProperty('--ly', (cy - pr.top) + 'px');
  const n = $('#next').getBoundingClientRect(); // отсвет на карточку урока
  page.style.setProperty('--nx', (cx - n.left) + 'px'); page.style.setProperty('--ny', (cy - n.top) + 'px');
  const en = $('#enter').getBoundingClientRect(), ex = r.left + 100 * k, ey = r.top + 148 * k; // Люмо дивиться на «Увійти»
  const dx = en.left + en.width / 2 - ex, dy = en.top + en.height / 2 - ey, d = Math.hypot(dx, dy) || 1, L = $('#lumo');
  L.style.setProperty('--gx', (dx / d * 5).toFixed(2) + 'px'); L.style.setProperty('--gy', (dy / d * 6).toFixed(2) + 'px');
}
addEventListener('resize', placeLight);
/* круг 5: близость курсора к Люмо → мягкий свет на границе и фоне карточки урока */
let proxT = 0;
addEventListener('pointermove', e => {
  if (e.pointerType === 'touch' || proxT) return;
  proxT = requestAnimationFrame(() => { proxT = 0;
    const r = $('#lumoBtn').getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height * .4;
    const d = Math.hypot(e.clientX - cx, e.clientY - cy), p = Math.max(0, 1 - d / 900);
    page.style.setProperty('--prox', (p * p).toFixed(3)); });
});
/* круг 5: радость в точке клика — вспышка света + искры, до 800 мс */
function burstAt(x, y) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const b = document.createElement('div'); b.className = 'burst'; b.setAttribute('aria-hidden', 'true');
  b.style.left = x + 'px'; b.style.top = y + 'px';
  b.innerHTML = '<i class="glow"></i>' + [0, 1, 2, 3, 4, 5].map(k => `<i class="sp" style="--a:${k * 60 + 20}deg"></i>`).join('');
  document.body.appendChild(b); setTimeout(() => b.remove(), 800);
}
const FACE = '<svg class="face-mini" width="24" height="24" viewBox="0 0 22 22" aria-hidden="true"><path d="M12 1.5c1.6 2.3 5 6 6.6 9.7 1.8 4.2-.3 9-6.6 9-6.3 0-8.4-4.8-6.6-9C7 7.5 10 4 12 1.5z" fill="#F5767C"/><path d="M6.5 12q1.6-2.2 3.2 0M12.3 12q1.6-2.2 3.2 0" fill="none" stroke="#3A1A45" stroke-width="1.6" stroke-linecap="round"/><path d="M8 15.2q3.5 3.6 7 0z" fill="#3A1A45"/></svg>';
function markBooked(id) { // смена лица: на кнопке «Ви записані» маленький Люмо с радостными глазами, пока он радуется
  const bt = $(`[data-book="${id}"]`); if (!bt) return;
  bt.insertAdjacentHTML('afterbegin', FACE); bt.closest('.slot').classList.add('just');
  setTimeout(() => { bt.querySelector('.face-mini')?.remove(); bt.closest('.slot')?.classList.remove('just'); }, 3500);
}
const demo = $('#demo');
$('#lumoBtn').addEventListener('click', () => { demo.hidden = !demo.hidden; $('#lumoBtn').setAttribute('aria-expanded', String(!demo.hidden)); });
function closeDemo() { demo.hidden = true; $('#lumoBtn').setAttribute('aria-expanded', 'false'); }
$$('#demo [data-emo]').forEach(b => b.addEventListener('click', () => { setEmo(b.dataset.emo); closeDemo(); }));
$$('#demo [data-day]').forEach(b => b.addEventListener('click', () => {
  day = b.dataset.day; t0 = performance.now();
  nowBase = LESSON0 - (day === 'near' ? 8 * M + 40e3 : 2 * H + 14 * M + 5e3);
  $$('#demo [data-day]').forEach(x => x.setAttribute('aria-pressed', x === b));
  closeDemo(); renderAll(); setEmo(baseEmo());
}));
addEventListener('keydown', e => { if (e.key === 'Escape' && !demo.hidden) { closeDemo(); $('#lumoBtn').focus(); } });

/* ---- рендер ---- */
const ICO_OK = '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M3 9.5l4 4 8-9" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const ICO_NO = '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="3 3"/></svg>';
const sortB = () => bookings.sort((a, b) => a.at - b.at);

function renderStatic() {
  document.documentElement.lang = lang;
  $$('[data-i]').forEach(el => { const v = t(el.dataset.i); if (typeof v === 'string') el.textContent = v; });
  $$('[data-i-aria]').forEach(el => el.setAttribute('aria-label', t(el.dataset.iAria)));
  $('title').textContent = 'LUMOSCHOOL · ' + (lang === 'uk' ? 'Кабінет' : 'Student area');
  $('#hello').innerHTML = t('hello')(t('name'));
  $('#levelW').textContent = t('levelW');
  $('#cefr').innerHTML = t('cefr').map((c, i) => `<li class="${i < 2 ? 'past' : ''}${i === 2 ? ' now' : ''}"${i === 2 ? ' aria-current="step"' : ''}>${c}</li>`).join('');
  $('#doneL').innerHTML = t('done1').map(x => `<li>${x}</li>`).join('');
  $('#nextL').innerHTML = t('next1').map(x => `<li>${x}</li>`).join('');
  $$('.seg [data-lang]').forEach(b => b.setAttribute('aria-pressed', b.dataset.lang === lang));
  $$('.seg [data-tz]').forEach(b => b.setAttribute('aria-pressed', b.dataset.tz === tz));
}
function renderNext() {
  const b = sortB()[0];
  $('#heroSub').textContent = t(day === 'near' ? 'subNear' : 'subFar');
  $('#dateLine').textContent = fDayLong(now()) + ' · ' + fTime(now());
  const en = $('#enter');
  if (!b) { $('#nextTitle').textContent = '—'; $('#nextMeta').textContent = ''; en.textContent = t('enterClosed'); $('#enterNote').textContent = ''; return; }
  $('#nextTitle').textContent = b.group;
  $('#nextMeta').textContent = `${fDay(b.at)}, ${fTime(b.at)} · ${teacherName(b.teacher)}, ${role(b.teacher)}`;
  const open = canEnter();
  en.setAttribute('aria-disabled', String(!open)); en.tabIndex = open ? 0 : -1;
  en.textContent = open ? t('enter') : t('enterClosed');
  $('#enterNote').textContent = open ? t('noteOpen') : t('noteClosed')(fTime(b.at - 10 * M));
  const e2 = $('#enter2'); e2.setAttribute('aria-disabled', String(!open)); e2.tabIndex = open ? 0 : -1; e2.textContent = en.textContent;
  $('#stTitle').textContent = b.group; $('#stWhen').textContent = fDay(b.at) + ', ' + fTime(b.at);
  tick();
}
/* круг 5: липкая плашка «Увійти» — появляется, когда карточка урока ушла за экран */
new IntersectionObserver(([en]) => { $('#sticky').hidden = en.isIntersecting; }, { threshold: 0 }).observe($('#next'));
function tick() {
  const b = bookings[0]; if (!b) return;
  const left = Math.max(0, b.at - now()), s = Math.floor(left / 1e3);
  const p = n => String(n).padStart(2, '0');
  $('#count').textContent = `${p(Math.floor(s / 3600))}:${p(Math.floor(s / 60) % 60)}:${p(s % 60)}`;
  $('#countCap').textContent = left > 0 ? t('untilStart') : t('started');
  const open = canEnter();
  if (open !== openedRoom) { openedRoom = open; renderNext(); renderSlots(); placeLight(); if (emo === 'wait') setEmo('wait'); }
}
function renderSlots() {
  // единственная оранжевая кнопка: «Увійти», когда комната открыта; иначе — первый свободный слот
  const first = slots.find(x => x.left > 0 && !bookings.some(b => b.id === x.id)); const primaryId = !canEnter() && first ? first.id : null;
  $('#bookNote').innerHTML = t('bookNote')(zoneName());
  $('#slots').innerHTML = slots.map(s => {
    const mine = bookings.some(b => b.id === s.id), full = s.left === 0 && !mine;
    return `<li class="slot${mine ? ' is-mine' : ''}">
      <div><span class="t-day">${fDay(s.at)}</span> <time class="t-time" datetime="${new Date(s.at).toISOString()}">${fTime(s.at)}</time></div>
      <div><p class="s-group">${t('groupWord')} ${s.group}</p><p class="s-teach">${teacherName(s.teacher)}, ${role(s.teacher)}</p></div>
      <div class="s-end"><span class="seats${s.left > 0 && s.left <= 2 ? ' low' : ''}">${full ? t('full') : t('seatsOf')(s.left, s.total)}</span>
      <button type="button" class="btn-sm${s.id === primaryId ? ' primary' : ''}" data-book="${s.id}"${mine || full ? ' disabled' : ''}>${mine ? t('booked') : full ? t('bookFull') : t('book')}</button></div></li>`;
  }).join('');
}
function renderMine() {
  $('#status').textContent = status;
  const list = sortB();
  $('#mine-list').innerHTML = list.length ? list.map(b => {
    const dl = b.at - 12 * H, late = now() > dl, asking = ask === b.id;
    return `<li class="bk">
      <p class="bk-t">${t('groupWord')} ${b.group}</p>
      <p class="bk-when">${fDay(b.at)}, <b>${fTime(b.at)}</b></p>
      <p class="bk-who">${teacherName(b.teacher)}, ${role(b.teacher)}</p>
      <p class="bk-win${late ? ' late' : ''}">${late ? t('cancelLate') : t('cancelUntil')(fDay(dl) + ', ' + fTime(dl))}</p>
      ${asking ? `<div class="bk-ask-wrap"><div class="bk-ask" role="alertdialog" aria-modal="true" aria-labelledby="askQ" aria-describedby="askN"><p id="askQ" class="ask-q">${t('ask')}</p><p id="askN" class="ask-n">${t('askNote')(fDay(dl) + ', ' + fTime(dl))}</p><div class="bk-act"><button type="button" class="btn-sm" data-keep>${t('keep')}</button><button type="button" class="btn-line btn-neutral" data-yes="${b.id}">${t('yes')}</button></div></div></div>`
        : `<div class="bk-act"><button type="button" class="btn-line" data-cancel="${b.id}"${late ? ' disabled' : ''}>${t('cancel')}</button></div>`}
    </li>`;
  }).join('') : `<li class="empty">${t('empty')}</li>`;
}
function renderMats() {
  $('#mats-list').innerHTML = mats.map((m, i) => `<li class="mat">
    <p class="mat-l">${t('lesson')} · ${fDay(m.at)}</p>
    <p class="mat-t">${m.title[lang]}</p>
    <p class="mat-f">${m.file}</p>
    <p class="mat-hw"><b>${t('hw')}:</b> ${m.hw[lang]} <span class="mat-l">(${t('due')} ${fDay(m.due)})</span></p>
    <div class="mat-foot"><span class="chip ${m.done ? 'done' : 'todo'}">${m.done ? ICO_OK : ICO_NO}${m.done ? t('done') : t('todo')}</span>
    ${m.done ? '' : `<button type="button" class="btn-line" data-submit="${i}">${t('submit')}</button>`}</div></li>`).join('');
}
function renderAll() { renderStatic(); renderNext(); renderSlots(); renderMine(); renderMats(); placeLight(); }

/* ---- действия ---- */
document.addEventListener('click', e => {
  const q = a => e.target.closest(a);
  let el;
  if ((el = q('[data-book]'))) {
    const s = slots.find(x => x.id === el.dataset.book); if (!s || s.left < 1) return;
    const r0 = el.getBoundingClientRect(), bx = e.clientX || r0.left + r0.width / 2, by = e.clientY || r0.top + r0.height / 2;
    s.left--; bookings.push({ id: s.id, at: s.at, group: s.group, teacher: s.teacher });
    status = t('statBooked'); renderSlots(); renderMine(); renderNext(); setEmo('joy', 3500);
    burstAt(bx, by); markBooked(s.id);
  } else if ((el = q('[data-cancel]'))) { ask = el.dataset.cancel; renderMine(); setEmo('think'); $('[data-keep]').focus(); }
  else if (q('[data-keep]') || (e.target.classList && e.target.classList.contains('bk-ask-wrap'))) { const id = ask; ask = null; renderMine(); setEmo(baseEmo()); $(`[data-cancel="${id}"]`)?.focus(); }
  else if ((el = q('[data-yes]'))) {
    const id = el.dataset.yes; bookings = bookings.filter(b => b.id !== id); const s = slots.find(x => x.id === id); if (s) s.left++;
    ask = null; status = t('statCancel'); renderSlots(); renderMine(); renderNext(); setEmo(baseEmo()); $('#status').focus?.();
  } else if ((el = q('[data-submit]'))) { mats[+el.dataset.submit].done = true; renderMats(); }
  else if ((el = q('[data-lang]'))) { lang = el.dataset.lang; renderAll(); setEmo(emo); }
  else if ((el = q('[data-tz]'))) { tz = el.dataset.tz; renderAll(); }
  else if ((q('#enter') && $('#enter').getAttribute('aria-disabled') === 'true') || (q('#enter2') && $('#enter2').getAttribute('aria-disabled') === 'true')) e.preventDefault();
  else if (!q('#lamp') && !demo.hidden) closeDemo();
});
renderAll(); setEmo('rest');
document.fonts && document.fonts.ready.then(placeLight);
setInterval(tick, 1000);
document.addEventListener('keydown', e => { if (e.key === 'Escape' && ask) $('[data-keep]')?.click(); });
