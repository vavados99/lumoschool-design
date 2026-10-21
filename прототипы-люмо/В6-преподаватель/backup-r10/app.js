/* LUMOSCHOOL · В6 «Кабінет викладача». Усі дані вигадані. Без зовнішніх залежностей.
   Приватність: у даних лише ініціали та вікова група. Контактів немає — «Зв'язок лише через платформу». */
(() => {
'use strict';
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const sv = (p, s = 22, sw = 2) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${p}</svg>`;
const I = {
  today: s => sv('<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6L7 7M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"/>', s),
  cal: s => sv('<rect x="3.5" y="5" width="17" height="15" rx="3"/><path d="M8 3v4M16 3v4M3.5 10h17"/>', s),
  group: s => sv('<circle cx="9" cy="8" r="3.2"/><circle cx="17" cy="9.5" r="2.6"/><path d="M3.5 19c.6-3.6 2.8-5.4 5.5-5.4s4.9 1.8 5.5 5.4M15 14.2c2.6-.4 4.7 1 5.5 4.3"/>', s),
  book: s => sv('<path d="M4 5.5C7 4.5 10 5 12 7c2-2 5-2.5 8-1.5V19c-3-1-6-.5-8 1.5C10 18.5 7 18 4 19z"/><path d="M12 7v13.5"/>', s),
  pen: s => sv('<path d="M4 20l1-4L16.5 4.5l3 3L8 19z"/><path d="M14 7l3 3"/>', s),
  swap: s => sv('<path d="M4 8h14M14 4l4 4-4 4M20 16H6M10 12l-4 4 4 4"/>', s),
  shield: s => sv('<path d="M12 3l7.5 3v5.5c0 4.6-3.1 7.8-7.5 9.5-4.4-1.7-7.5-4.9-7.5-9.5V6z"/><path d="M9 12l2.2 2.2L15.5 10"/>', s),
  check: s => sv('<path d="M5 12.5l4.5 4.5L19 7.5"/>', s, 3),
  clock: s => sv('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>', s),
  dot: s => sv('<circle cx="12" cy="12" r="4.5" fill="currentColor"/>', s),
  live: s => sv('<circle cx="12" cy="12" r="3" fill="currentColor"/><path d="M6.5 6.5a7.8 7.8 0 0 0 0 11M17.5 6.5a7.8 7.8 0 0 1 0 11"/>', s),
  warn: s => sv('<path d="M12 3.5l9.5 16.5h-19z"/><path d="M12 10v4.5M12 17.4v.1"/>', s),
  file: s => sv('<path d="M6 3.5h8l4 4V20.5H6z"/><path d="M14 3.5v4h4M9 12h6M9 16h6"/>', s),
  music: s => sv('<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>', s),
  cards: s => sv('<rect x="3.5" y="7" width="11" height="13" rx="2"/><path d="M8 7V5.5A2 2 0 0 1 10 3.5h8a2 2 0 0 1 2 2V15a2 2 0 0 1-2 2h-3.5"/>', s),
  gear: s => sv('<circle cx="12" cy="12" r="3"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>', s),
  door: s => sv('<path d="M6 20.5V4.5h9v16M4 20.5h16M12 12.5v.1"/>', s),
};

/* ---------- дані (вигадані) ---------- */
const TODAY = 2;                         /* середа, 21 жовтня 2026 */
const DAYS = { uk: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд'], en: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] };
const DATES = [19, 20, 21, 22, 23, 24, 25];
const GROUPS = {
  foxes:  { uk: 'Лисенята', en: 'Foxes',  age: '7–8',   lvl: 'A1', stu: [['А. К.', 'A. K.'], ['Б. М.', 'B. M.'], ['Д. Н.', 'D. N.'], ['Є. П.', 'Ye. P.'], ['І. С.', 'I. S.'], ['Л. Т.', 'L. T.']] },
  owls:   { uk: 'Сови',     en: 'Owls',   age: '9–10',  lvl: 'A2', stu: [['О. В.', 'O. V.'], ['М. Г.', 'M. H.'], ['Т. Д.', 'T. D.'], ['Н. Ж.', 'N. Zh.'], ['Р. Ш.', 'R. Sh.']] },
  sparks: { uk: 'Іскри',    en: 'Sparks', age: '11–12', lvl: 'B1', stu: [['К. Б.', 'K. B.'], ['С. Л.', 'S. L.'], ['В. Р.', 'V. R.'], ['Я. Ф.', 'Ya. F.'], ['Г. Ч.', 'H. Ch.'], ['Ю. З.', 'Yu. Z.']] },
};
const LESSONS = [
  { id: 'l1', d: 0, t: '18:00', g: 'owls' },
  { id: 'l2', d: 1, t: '15:30', g: 'sparks' }, { id: 'l3', d: 1, t: '17:00', g: 'foxes' },
  { id: 'l4', d: 2, t: '15:30', g: 'sparks' }, { id: 'l5', d: 2, t: '18:00', g: 'foxes' }, { id: 'l6', d: 2, t: '19:00', g: 'owls' },
  { id: 'l7', d: 3, t: '17:00', g: 'foxes' },
  { id: 'l8', d: 4, t: '15:30', g: 'sparks' },
  { id: 'l9', d: 5, t: '10:00', g: 'owls' },
];
const NEXT = 'l5';
const DEMO = { early: { now: '16:20', emo: 'rest' }, open: { now: '17:52', emo: 'wait' }, live: { now: '18:12', emo: 'joy' } };
const PLAN = [
  { m: 5,  uk: 'Привітання та пісня-розминка', en: 'Greeting and warm-up song' },
  { m: 10, uk: 'Нові слова: 6 карток «Food»', en: 'New words: 6 “Food” cards' },
  { m: 15, uk: 'Робота в парах: «У магазині»', en: 'Pair work: “At the shop”' },
  { m: 10, uk: 'Говоріння: «I like… / I don’t like…»', en: 'Speaking: “I like… / I don’t like…”' },
  { m: 5,  uk: 'Підсумок і домашня вправа', en: 'Wrap-up and a short home task' },
];
const MATS = [
  { ic: 'file', uk: 'Слайди «Food»', en: '“Food” slides', mu: '12 стор. · бібліотека школи', me: '12 pages · school library' },
  { ic: 'cards', uk: 'Картки слів', en: 'Word cards', mu: '6 карток · PDF', me: '6 cards · PDF' },
  { ic: 'music', uk: 'Пісня-розминка', en: 'Warm-up song', mu: 'аудіо · 1 хв 40 с', me: 'audio · 1 min 40 s' },
];
const SEED_NOTES = { owls: [{ w: { uk: 'Вт, 20 жовт.', en: 'Tue, 20 Oct' }, x: { uk: 'Т. Д. та М. Г. добре працюють у парі. Повторити Past Simple на наступному уроці.', en: 'T. D. and M. H. work well in pairs. Review Past Simple next lesson.' } }] };

/* ---------- мова та стан ---------- */
const q = new URLSearchParams(location.search);
const S = { lang: q.get('lang') === 'en' ? 'en' : 'uk', tz: 'both', demo: 'open', grp: 'foxes', ngrp: 'foxes', checks: [false, false, false], notes: JSON.parse(JSON.stringify(SEED_NOTES)), swap: null, entered: false, noteErr: false, swapErr: false, sel: 'l6' };
const L = (uk, en) => S.lang === 'uk' ? uk : en;
const gName = g => GROUPS[g][S.lang];
const shift = t => { const [h, m] = t.split(':').map(Number); return String((h + 1) % 24).padStart(2, '0') + ':' + String(m).padStart(2, '0'); };
const end = t => { const [h, m] = t.split(':').map(Number); const e = h * 60 + m + 45; return String(Math.floor(e / 60)).padStart(2, '0') + ':' + String(e % 60).padStart(2, '0'); };
const TZN = () => ({ waw: L('Варшава', 'Warsaw'), kyiv: L('Київ', 'Kyiv') });
/* час за режимом: основний + підпис другого пояса */
const tmain = t => S.tz === 'kyiv' ? shift(t) : t;
const tsub = t => S.tz === 'both' ? `${TZN().kyiv} ${shift(t)}` : '';
const tzLabel = () => S.tz === 'kyiv' ? TZN().kyiv : TZN().waw;
const dayOf = d => `${DAYS[S.lang][d]}, ${DATES[d]} ${L('жовт.', 'Oct')}`;
const stOf = l => {
  if (l.d < TODAY) return 'done';
  if (l.d > TODAY) return 'later';
  if (l.id === 'l4') return 'done';
  if (l.id === NEXT) return S.demo === 'live' ? 'live' : S.demo === 'early' ? 'later' : 'next';
  if (l.id === 'l6') return S.demo === 'live' ? 'next' : 'later';
  return 'later';
};
const stHtml = k => ({
  done:  `<span class="st st-done">${I.check(18)}${L('Проведено', 'Done')}</span>`,
  next:  `<span class="st st-next">${I.clock(18)}${L('Далі', 'Next')}</span>`,
  live:  `<span class="st st-live">${I.live(18)}${L('Іде зараз', 'In progress')}</span>`,
  later: `<span class="st st-wait">${I.dot(18)}${L('Пізніше', 'Later')}</span>`,
}[k]);
const CONTACTLESS = () => L('Зв’язок лише через платформу', 'Contact only through the platform');

/* перевірка: у нотатках та коментарях не має бути контактів */
const BAD = /\u0040|\bh\u0074tps?:|www\.|\bt\.me\b|\+?\d[\d\s().-]{6,}|(?<![\p{L}])(telegram|viber|whatsapp|signal|instagram|discord|tiktok|телеграм|вайбер|ватсап|інстаграм)(?![\p{L}])/iu;

/* ---------- рендер ---------- */
function setEmo(e) { $('#page').dataset.emo = e; }
function say(h, t) { $('#say').innerHTML = `<b>${esc(h)}</b><br><span>${esc(t)}</span>`; }

const LUMO_SVG = `<svg class="lumo" id="lumo" viewBox="-6 -6 112 112" aria-hidden="true" focusable="false">
  <g class="sparks"><g transform="translate(10 26) scale(.9)"><path d="M0-6L1.6-1.6 6 0 1.6 1.6 0 6-1.6 1.6-6 0-1.6-1.6Z"/></g><g transform="translate(92 16) scale(1.1)"><path d="M0-6L1.6-1.6 6 0 1.6 1.6 0 6-1.6 1.6-6 0-1.6-1.6Z"/></g><g transform="translate(90 70) scale(.8)"><path d="M0-6L1.6-1.6 6 0 1.6 1.6 0 6-1.6 1.6-6 0-1.6-1.6Z"/></g><g transform="translate(8 62) scale(.7)"><path d="M0-6L1.6-1.6 6 0 1.6 1.6 0 6-1.6 1.6-6 0-1.6-1.6Z"/></g></g>
  <path fill="#DF5520" d="M64.54 6C60.71 14.03 54.97 20.92 56.12 31.25C57.27 40.82 72.19 48.47 74.49 69.51C76.02 85.97 67.22 94 50 94C32.78 94 23.98 85.97 25.51 69.51C26.28 59.95 27.43 52.68 28.19 45.79C28.96 39.29 31.63 32.4 42.35 22.45C41.2 30.49 43.5 34.7 46.17 36.61C44.64 27.81 52.68 18.63 59.57 12.12C61.48 10.21 63.39 8.3 64.54 6Z"/>
  <path class="inner" fill="#FFE3B8" d="M54.48 35.39C52.48 41.38 59.8 44.71 60.13 53.36C60.47 59.35 56.47 63.01 51.15 63.01C45.82 63.01 42.5 59.68 42.5 54.69C42.5 50.36 46.49 49.03 48.15 46.04C49.82 43.04 48.49 40.71 50.82 38.38C51.81 37.05 53.81 36.72 54.48 35.39Z"/>
  <g class="eyes"><g transform="translate(-4.4 2.4)"><path fill="#4A1A0E" d="M30.68 68.75A7.27 9.37 0 1 0 45.22 68.75A7.27 9.37 0 1 0 30.68 68.75ZM54.78 68.75A7.27 9.37 0 1 0 69.32 68.75A7.27 9.37 0 1 0 54.78 68.75Z"/><g class="gaze" transform="translate(-6.2 5.6)"><circle class="glint" cx="40.27" cy="65.37" r="1.45" fill="#FFE3B8"/><circle class="glint" cx="64.38" cy="65.37" r="1.45" fill="#FFE3B8"/></g></g></g>
  <path class="mouth" d="M41 84Q50 92 59 84" fill="none" stroke="#4A1A0E" stroke-width="2.8" stroke-linecap="round"/>
</svg>`;
const NB = '\u00a0';
const toMin = t => { const [h, m] = t.split(':').map(Number); return h * 60 + m; };

function renderHead() {
  document.documentElement.lang = S.lang;
  document.title = 'LUMOSCHOOL · ' + L('Кабінет викладача', 'Teacher’s desk');
  $('#who').innerHTML = `${I.shield(20)}<span><b>${L('Марта В.', 'Marta V.')}</b> · ${L('викладач', 'teacher')}</span>`;
  const av = $('#avatarBtn'); av.textContent = L('МВ', 'MV');
  av.setAttribute('aria-label', L('Меню: Марта В., мова та місто', 'Menu: Marta V., language and city'));
  $('#tzLab').textContent = L('Місто (час)', 'City (time)'); $('#lgLab').textContent = L('Мова', 'Language');
  const T = TZN();
  $('#tzSeg').innerHTML = [['both', L('Обидва', 'Both')], ['waw', T.waw], ['kyiv', T.kyiv]].map(([k, n]) => `<button type="button" data-tz="${k}" aria-pressed="${S.tz === k}">${n}</button>`).join('');
  $$('[data-lang]').forEach(b => b.setAttribute('aria-pressed', b.dataset.lang === S.lang));
  $('#devSum').setAttribute('aria-label', L('Стан прототипу: демо-час', 'Prototype state: demo time'));
  $('#devSum').innerHTML = `${I.gear(22)}<span class="devtxt">${L('Стан прототипу', 'Prototype state')}</span>`;
  $('#devLab').textContent = L('Прототип, час', 'Prototype, time');
  $('#devSeg').innerHTML = Object.entries(DEMO).map(([k, v]) => `<button type="button" data-demo="${k}" aria-pressed="${S.demo === k}">${v.now}</button>`).join('');
  const items = [['today', 'today', L('Сьогодні', 'Today'), L('Сьогодні', 'Today')], ['week', 'cal', L('Тиждень', 'Week'), L('Тиждень', 'Week')], ['groups', 'group', L('Мої групи', 'My groups'), L('Групи', 'Groups')], ['plan', 'book', L('План і матеріали', 'Plan & materials'), L('План', 'Plan')], ['notes', 'pen', L('Нотатки', 'Notes'), L('Нотатки', 'Notes')], ['swap', 'swap', L('Заміна', 'Substitution'), L('Заміна', 'Swap')]];
  const cur = $('#nav a[aria-current=true]')?.dataset.sec || 'today';
  $('#navIn').innerHTML = items.map(([id, ic, n, sh]) => `<a href="#${id}" data-sec="${id}" ${id === cur ? 'aria-current="true"' : ''}>${I[ic](20)}<span class="l-full">${n}</span><span class="l-short" aria-hidden="true">${sh}</span></a>`).join('');
}
function menuOpen(on) {
  $('#menu').toggleAttribute('data-open', on);
  $('#avatarBtn').setAttribute('aria-expanded', String(on));
}

function renderToday() {
  const l = LESSONS.find(x => x.id === NEXT), g = GROUPS[l.g], dm = DEMO[S.demo];
  const open = S.demo !== 'early', live = S.demo === 'live';
  const T = TZN();
  const leftMin = toMin(end(l.t)) - toMin(dm.now);          /* до кінця уроку (live) */
  const left = { early: L('Через 1 год 40 хв', 'In 1 h 40 min'), open: L('Через 8 хв', 'In 8 min') }[S.demo];
  const hello = { early: [L('Є час підготуватися', 'Time to prepare'), L('Кімната відкриється за 10 хвилин до початку.', 'The room opens 10 minutes before the start.')],
                  open: [L('Кімната відкрита', 'The room is open'), L('Світло ввімкнено. Можна заходити — діти зайдуть слідом.', 'The light is on. Step in; the children will follow.')],
                  live: [L('Я поруч', 'I’m here'), L('Нотатки — після уроку, у вкладці «Нотатки».', 'Notes come after the lesson, in the “Notes” tab.')] }[S.demo];
  setEmo(S.entered ? 'joy' : dm.emo);
  $('#page').dataset.demo = S.demo;
  const when = live ? '' : S.entered
    ? L('Прототип: тут відкрилася б відеокімната платформи.', 'Prototype: the platform’s video room would open here.')
    : `<b class="count" id="count">${left}</b> ${L('до початку', 'until the start')}`;
  const top = live
    ? `<b class="count">${L('Урок іде', 'Lesson in progress')}</b><span>${dayOf(l.d)}</span>`
    : `<span>${L('Найближчий урок', 'Next lesson')} · ${dayOf(l.d)}</span>`;
  const rangeMain = `${tmain(l.t)}–${tmain(end(l.t))}`;
  const rangeSub = S.tz === 'both' ? `<span class="nw">${T.kyiv} ${shift(l.t)}–${shift(end(l.t))}</span>` : tzLabel();
  const meta = live
    ? `<div class="timer"><b class="tnum">${leftMin}<small>${NB}${L('хв', 'min')}</small></b><span class="tlab">${L('лишилось до кінця уроку', 'left until the end of the lesson')}</span>
        <div class="burn" role="progressbar" aria-valuemin="0" aria-valuemax="45" aria-valuenow="${leftMin}" aria-label="${L('Скільки лишилось від уроку', 'How much of the lesson is left')}"><i style="width:${(leftMin / 45 * 100).toFixed(1)}%"></i></div></div>`
    : `<div class="lc-time"><b>${rangeMain}</b><span>${S.tz === "both" ? T.waw + " · " : ""}${rangeSub}</span></div>`;
  const btnLab = L('Увійти в кімнату', 'Enter the room');
  const btnHtml = open
    ? `<button type="button" class="btn btn-main" id="enter">${I.door(22)}${btnLab}</button>`
    : `<button type="button" class="btn btn-main btn-off" id="enter" disabled aria-disabled="true">${I.door(22)}<span>${btnLab}</span><small>${L('з', 'from')} ${tmain('17:50')}</small></button>`;
  $('#lessonCard').innerHTML = `
    <div class="lc-main">
    <div class="lc-top"><span>${I.clock(20)}</span>${top}</div>
    <h1 id="todayH">${gName(l.g)} · <span class="nw">${g.age}&nbsp;${L('р.', 'y.o.')}</span> · ${g.lvl}</h1>
    <div class="lc-line">
      <div class="lc-meta">${meta}</div>
      <div class="lc-row">${btnHtml}</div>
    </div>
    ${live ? `<p class="lc-range"><span class="nw">${S.tz === 'both' ? T.waw + ' ' : ''}${rangeMain}</span>${S.tz === 'both' ? ' · ' : ' · '}${rangeSub}</p>` : ''}
    ${when ? `<p class="lc-when" id="enterNote" role="status">${when}</p>` : '<p class="lc-when" id="enterNote" role="status" hidden></p>'}
    <div class="lc-foot"><span class="info">${I.group(20)}${g.stu.length} ${L('учнів у групі', 'students in the group')}</span><span class="info">${I.shield(20)}${CONTACTLESS()}</span></div>
    </div>
    <div class="lc-side">
      <div class="lumo-wrap">${LUMO_SVG}</div>
      <p class="say" id="say" role="status" aria-live="polite"></p>
    </div>`;
  say(hello[0], hello[1]);

  const todays = LESSONS.filter(x => x.d === TODAY), tom = LESSONS.filter(x => x.d === TODAY + 1);
  const zl = S.tz === 'both' ? L('Основний час — Варшава, поруч Київ', 'Main time is Warsaw, Kyiv beside it') : `${L('Час', 'Time')}: ${tzLabel()}`;
  const nowM = toMin(dm.now); let nowDone = todays.some(x => stOf(x) === 'live');
  const row = x => {
    const k = stOf(x), cur = x.id === NEXT;
    let mk = '';
    if (!nowDone && toMin(x.t) > nowM) { nowDone = true; mk = `<li class="nowline" aria-label="${L('Зараз', 'Now')} ${tmain(dm.now)}"><span>${L('Зараз', 'Now')} · ${tmain(dm.now)}</span></li>`; }
    const when = `<span class="nw">${tmain(x.t)}–${tmain(end(x.t))}</span>${S.tz === 'both' ? ` · <span class="nw">${T.kyiv} ${shift(x.t)}</span>` : ''}`;
    const what = cur ? L('цей урок — у картці вище', 'this lesson is in the card above') : `${gName(x.g)} · ${GROUPS[x.g].age} ${L('р.', 'y.o.')} · ${GROUPS[x.g].lvl} · ${GROUPS[x.g].stu.length} ${L('учнів', 'students')}`;
    return `${mk}<li class="dr ${k}${cur ? ' cur' : ''}" ${cur ? 'aria-current="true"' : ''}><span class="dt">${when}</span><span class="dg">${what}</span>${stHtml(k)}</li>`;
  };
  const tomRows = tom.map(x => { const k = 'later'; return `<li class="dr later"><span class="dt"><span class="nw">${tmain(x.t)}–${tmain(end(x.t))}</span>${S.tz === 'both' ? ` · <span class="nw">${T.kyiv} ${shift(x.t)}</span>` : ''}</span><span class="dg">${gName(x.g)} · ${GROUPS[x.g].age} ${L('р.', 'y.o.')} · ${GROUPS[x.g].lvl}</span>${stHtml(k)}</li>`; }).join('');
  $('#day').innerHTML = `<div class="day-h"><h2>${L('Ваш день', 'Your day')}</h2><span class="legend">${zl}</span></div><ol class="dlist">${todays.map(row).join('')}${tom.length ? `<li class="dsep">${L('Завтра', 'Tomorrow')} · ${dayOf(TODAY + 1)}</li>${tomRows}` : ''}</ol>`;
}

function renderWeek() {
  const T = TZN();
  $('#week').innerHTML = `<div class="sec-h"><h2 id="weekH">${L('Тиждень', 'This week')}</h2><p>${L('19–25 жовтня. Час: ' + (S.tz === 'both' ? `${T.waw} / ${T.kyiv}` : tzLabel()) + ' (+1 год).', '19–25 October. Time: ' + (S.tz === 'both' ? `${T.waw} / ${T.kyiv}` : tzLabel()) + ' (+1 h).')}</p></div>
  <div class="wk">${DAYS[S.lang].map((dn, d) => { const ls = LESSONS.filter(x => x.d === d); return `<div class="wd" ${d === TODAY ? 'aria-current="date"' : ''}>
    <h3>${dn} <span>${DATES[d]}</span>${d === TODAY ? `<span class="chip" style="min-height:28px;padding:0 10px">${L('сьогодні', 'today')}</span>` : ''}</h3>
    <div class="wls">${ls.length ? ls.map(x => `<div class="wl" role="group" aria-label="${T.waw} ${x.t}, ${T.kyiv} ${shift(x.t)}"><b>${tmain(x.t)}${S.tz === 'both' ? `<small> / ${shift(x.t)}</small>` : ''}</b><span class="gn">${gName(x.g)} · ${GROUPS[x.g].age} ${L('р.', 'y.o.')}</span>${stOf(x) === 'done' ? `<span class="tag" style="color:var(--ink2)">${I.check(16)}${L('Проведено', 'Done')}</span>` : x.id === NEXT ? `<span class="tag">${I.clock(16)}${L('Далі', 'Next')}</span>` : ''}</div>`).join('') : ''}</div>
    ${ls.length ? '' : `<p class="free">${L('Вихідний', 'Day off')}</p>`}</div>`; }).join('')}</div>
  <p class="tz-note">${I.clock(20)}<span>${L('Зараз у Варшаві та Києві різниця — 1 година. Урок записано за часом Варшави.', 'Warsaw and Kyiv are 1 hour apart. Lessons are stored in Warsaw time.')}</span></p>`;
}

function renderGroups() {
  const g = GROUPS[S.grp];
  $('#groups').innerHTML = `<div class="sec-h"><h2 id="groupsH">${L('Мої групи', 'My groups')}</h2><span class="chip safe">${I.shield(18)}${CONTACTLESS()}</span></div>
  <div class="grp"><div class="tabs" role="tablist" aria-label="${L('Групи', 'Groups')}">${Object.keys(GROUPS).map(k => `<button type="button" role="tab" class="tab" data-grp="${k}" aria-selected="${S.grp === k}"><b>${gName(k)}</b><span>${GROUPS[k].age} ${L('р.', 'y.o.')} · ${GROUPS[k].lvl} · ${GROUPS[k].stu.length} ${L('учнів', 'students')}</span></button>`).join('')}</div>
  <div class="panel roster" role="tabpanel"><div class="roster-h"><h3>${gName(S.grp)}</h3><span class="chip">${I.group(18)}${g.age} ${L('р.', 'y.o.')}</span></div>
    <ul class="stu">${g.stu.map(s => `<li><span class="av" aria-hidden="true">${esc(s[S.lang === 'uk' ? 0 : 1].replace(/[^\p{L}]/gu, '').slice(0, 2))}</span><div><b>${esc(s[S.lang === 'uk' ? 0 : 1])}</b><span>${g.age} ${L('р.', 'y.o.')}</span></div></li>`).join('')}</ul>
    <div class="privacy">${I.shield(24)}<div><b>${L('Лише в межах вашого уроку', 'Only within your lesson')}</b><p>${L('Ви бачите ініціали та вікову групу тих, хто в цій групі. Контактів, адрес і даних батьків тут немає. ', 'You see initials and the age group of this group only. There are no contacts, addresses or parent details here. ')}<b>${CONTACTLESS()}.</b></p></div></div>
  </div></div>`;
}

function renderPlan() {
  const l = LESSONS.find(x => x.id === NEXT), done = S.checks.filter(Boolean).length;
  $('#plan').innerHTML = `<div class="sec-h"><h2 id="planH">${L('План уроку та матеріали', 'Lesson plan & materials')}</h2><p>${gName(l.g)} · ${dayOf(l.d)} · ${tmain(l.t)} (${tzLabel()})</p></div>
  <div class="pl"><div class="panel"><h3>${L('Тема: «Моя їжа»', 'Topic: “My food”')}</h3><p class="theme">${L('45 хвилин · 5 кроків', '45 minutes · 5 steps')}</p>
    <ol class="steps">${PLAN.map((s, i) => `<li class="step"><span class="min">${s.m} ${L('хв', 'min')}</span><span class="min" style="color:var(--ink2);font-weight:500">${i + 1}/5</span><div>${s[S.lang]}</div></li>`).join('')}</ol></div>
  <div class="panel"><h3>${L('Матеріали', 'Materials')}</h3><p class="theme">${L('Усе зі шкільної бібліотеки. Файли — лише через платформу.', 'All from the school library. Files go through the platform only.')}</p>
    <ul class="mat">${MATS.map((m, i) => `<li>${I[m.ic](26)}<div><b>${m[S.lang]}</b><span>${S.lang === 'uk' ? m.mu : m.me}</span></div><label class="lab" style="display:flex;align-items:center;gap:10px"><input class="chk" type="checkbox" data-chk="${i}" ${S.checks[i] ? 'checked' : ''}><span style="display:inline;color:var(--ink)">${L('Готово', 'Ready')}</span></label></li>`).join('')}</ul>
    <p class="prog" aria-live="polite">${L('Підготовлено', 'Prepared')}: ${done} / ${MATS.length}</p></div></div>`;
}

function renderNotes() {
  const list = S.notes[S.ngrp] || [];
  $('#notes').innerHTML = `<div class="sec-h"><h2 id="notesH">${L('Нотатки після уроку', 'After-lesson notes')}</h2><p>${L('Коротко: що пройшли, що повторити. Про дітей — лише за ініціалами.', 'Briefly: what we covered, what to review. Refer to children by initials only.')}</p></div>
  <div class="nt"><form class="panel" id="noteForm" novalidate><h3>${L('Нова нотатка', 'New note')}</h3>
    <div class="tags" role="group" aria-label="${L('Група', 'Group')}">${Object.keys(GROUPS).map(k => `<button type="button" class="btn btn-ghost" data-ng="${k}" aria-pressed="${S.ngrp === k}">${gName(k)}</button>`).join('')}</div>
    <div class="field"><label for="noteText">${L('Нотатка', 'Note')}</label><textarea id="noteText" placeholder="${L('Наприклад: тема засвоєна, повторити слова «apple», «bread»…', 'For example: topic understood, review “apple”, “bread”…')}"></textarea></div>
    <div id="noteErr" aria-live="polite"></div>
    <div class="lc-row"><button type="submit" class="btn btn-main" style="min-height:52px" aria-describedby="noteWhy">${L('Зберегти', 'Save')}</button><span class="why" id="noteWhy" hidden>${L('Спершу приберіть контакт', 'Remove the contact first')}</span><span class="chip safe">${I.shield(18)}${CONTACTLESS()}</span></div></form>
  <div class="panel"><h3>${L('Збережені', 'Saved')} · ${gName(S.ngrp)}</h3>
    ${list.length ? `<ul class="saved">${list.map(n => `<li><small>${n.w[S.lang]}</small>${esc(n.x[S.lang])}</li>`).join('')}</ul>` : `<p class="empty">${L('Поки немає нотаток для цієї групи.', 'No notes for this group yet.')}</p>`}
    <div class="memo"><h4>${L('Що можна писати', 'What you can write')}</h4>
      <ul class="okno"><li>${I.check(18)}<span>${L('Що пройшли і що засвоїли', 'What was covered and learned')}</span></li><li>${I.check(18)}<span>${L('Що повторити на наступному уроці', 'What to review next time')}</span></li><li>${I.check(18)}<span>${L('Хто добре працює в парі — за ініціалами', 'Who works well in pairs — by initials')}</span></li></ul>
      <h4>${L('Чого не можна', 'What not to write')}</h4>
      <ul class="nono"><li>${I.warn(18)}<span>${L('Телефони, пошту, посилання, імена в месенджерах', 'Phone numbers, email, links, messenger names')}</span></li><li>${I.warn(18)}<span>${L('Повні імена та прізвища дітей', 'Full names of children')}</span></li></ul></div></div></div>`;
}
/* у повідомленні про помилку контакт не повторюємо: цифри після п'ятої замінюються на *, пошта скорочується */
const maskDigits = t => { let n = 0; return t.replace(/\d/g, c => (++n > 5 ? '*' : c)); };
const maskStr = t => t.replace(/\+?\d[\d\s().-]{6,}/g, maskDigits).replace(/[\p{L}\d._-]+(?=@)/gu, w => w.slice(0, 2) + '***').replace(/@[\p{L}\d.-]+/gu, '@***');
const errBox = (v = '', m = '') => {
  const mv = maskStr(v), mm = m ? maskStr(m.trim()) : '';
  const i = mm ? mv.indexOf(mm) : -1;
  const quote = i >= 0 ? `${esc(mv.slice(0, i))}<mark>${esc(mm)}</mark>${esc(mv.slice(i + mm.length))}` : (v ? esc(mv) : '');
  return `<div class="err" role="alert">${I.warn(22)}<div><b>${L('Контакти поза платформою не передаємо — це правило безпеки для дитини.', 'We don’t pass on contacts outside the platform — it’s a child-safety rule.')}</b>${quote ? `<p class="quote">${quote}</p>` : ''}</div></div>`;
};
function flagErr(form, ta, box, on, v) {
  const m = on ? (BAD.exec(v) || [''])[0] : '';
  /* місце під помилку не згортаємо, коли її виправлено: замість неї той самий блок зі спокійним підтвердженням (без стрибка сторінки) */
  if (on) { box.style.minHeight = ''; box.innerHTML = errBox(v, m); }
  else if (box.querySelector('.err')) { box.style.minHeight = box.offsetHeight + 'px'; box.innerHTML = `<p class="errok">${I.check(20)}<span>${L('Контакт прибрано — тепер можна зберегти.', 'Contact removed — you can save now.')}</span></p>`; }
  else if (!box.querySelector('.errok')) box.innerHTML = '';
  ta.classList.toggle('bad', on); ta.toggleAttribute('aria-invalid', on);
  const b = form.querySelector('button[type=submit]');
  if (on) b.setAttribute('aria-disabled', 'true'); else b.removeAttribute('aria-disabled');
  const why = form.querySelector('.why'); if (why) why.hidden = !on;
}
/* показати помилку в центрі екрана: ні шапка, ні панель не закривають підписи */
function showErr(box) {
  /* підбираємо прокрутку: жоден текст не під липкою шапкою (ні повністю, ні частково), блок помилки у вікні */
  const navB = $('#nav').offsetHeight, vh = innerHeight, maxY = document.documentElement.scrollHeight - vh;
  const sy = scrollY, abs = r => ({ t: r.top + sy, b: r.bottom + sy });
  const eb = abs(box.getBoundingClientRect()), fb = abs(box.closest('form').getBoundingClientRect());
  const bar = document.querySelector('.lesson-card .lc-row'), barH = bar && getComputedStyle(bar).position === 'fixed' ? bar.getBoundingClientRect().height : 0, pad = Math.max(12, barH + 12); /* знизу на телефоні — липка кнопка */
  const txt = []; const w = document.createTreeWalker($('#page'), NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const n = w.currentNode; if (!n.textContent.trim()) continue; const el = n.parentElement;
    if (!el || el.closest('script,style,svg,nav,header,.grain,[hidden]') || getComputedStyle(el).visibility === 'hidden') continue;
    const r = document.createRange(); r.selectNodeContents(n); const q = r.getBoundingClientRect(); if (q.width > 0) txt.push(abs(q));
  }
  const cost = y => txt.reduce((c, q) => c + (q.t - y < navB + 4 && q.b - y > 0 ? 1000 : 0) + (barH && q.b - y > vh - barH - 4 && q.t - y < vh ? 1 : 0), 0);
  const ok = y => eb.t - y >= navB + 12 && eb.b - y <= vh - pad;
  const mid = Math.min(maxY, Math.max(0, Math.round((fb.t + eb.b) / 2 - vh / 2)));
  /* перебираємо всі положення, де помилка видна: перше — нуль текстів під шапкою, друге — менше під кнопкою, третє — ближче до центру */
  let best = null, bc = 1e12;
  for (let y = 0; y <= maxY; y += 2) { if (!ok(y)) continue; const c = cost(y) * 10000 + Math.abs(y - mid); if (c < bc) { bc = c; best = y; } }
  scrollTo({ top: best === null ? mid : best, behavior: 'smooth' });
}

function renderSwap() {
  const up = LESSONS.filter(x => x.id !== 'l1' && (x.d > TODAY || x.id === 'l6'));
  const sent = S.swap;
  $('#swap').innerHTML = `<div class="sec-h"><h2 id="swapH">${L('Запит заміни', 'Substitution request')}</h2><p>${L('Координатор шукає заміну, школа сама повідомляє групу.', 'The coordinator finds a substitute; the school informs the group itself.')}</p></div>
  <ol class="how">${[L('Ви обираєте урок і причину.', 'You choose the lesson and a reason.'), L('Матеріали та план автоматично стають доступні заміні.', 'The plan and materials become available to the substitute automatically.'), L('Ваш особистий контакт нікому не передається.', 'Your personal contact is never shared.')].map((t, i) => `<li><span class="hn">${i + 1}</span><span>${t}</span></li>`).join('')}</ol>
  <div class="sw">${sent ? `<div class="panel sent"><span class="st">${I.clock(18)}${L('На розгляді', 'Under review')}</span><h3>${L('Запит надіслано координатору', 'Request sent to the coordinator')}</h3>
      <p>${esc(sent.name)} · ${esc(sent.when)}</p><p class="empty">${L('Причина', 'Reason')}: ${esc(sent.reason)}</p>
      <ul class="steps-s"><li>${I.check(18)}<span>${L('Запит збережено', 'Request saved')}</span></li><li>${I.clock(18)}<span>${L('Координатор підбирає викладача', 'Coordinator is matching a teacher')}</span></li><li>${I.dot(18)}<span>${L('Школа повідомить групу через платформу', 'The school notifies the group through the platform')}</span></li></ul>
      <div class="lc-row"><button type="button" class="btn btn-ghost" id="swapCancel">${L('Скасувати запит', 'Withdraw request')}</button></div></div>`
    : `<form class="panel swf" id="swapForm" novalidate><div class="swf-l"><h3>${L('Який урок передати', 'Which lesson to hand over')}</h3>
      <div class="opts" role="radiogroup" aria-label="${L('Урок', 'Lesson')}">${up.map(x => `<label class="opt"><input type="radio" name="les" value="${x.id}" ${S.sel === x.id ? 'checked' : ''}><span><b>${dayOf(x.d)} · ${tmain(x.t)}</b><small>${gName(x.g)} · ${GROUPS[x.g].age} ${L('р.', 'y.o.')} · ${tzLabel()}</small></span></label>`).join('')}</div></div>
      <div class="swf-r"><div class="field" style="margin-top:0"><label for="reason">${L('Причина', 'Reason')}</label><select id="reason"><option value="ill">${L('Хвороба', 'Illness')}</option><option value="tech">${L('Технічна причина', 'Technical reason')}</option><option value="other">${L('Інша причина', 'Other reason')}</option></select></div>
      <div class="field"><label for="swapNote">${L('Коментар (необов’язково)', 'Comment (optional)')}</label><textarea id="swapNote" style="min-height:90px" placeholder="${L('Без контактів — лише про урок', 'No contacts — about the lesson only')}"></textarea></div>
      <div id="swapErr" aria-live="polite"></div>
      <div class="lc-row"><button type="submit" class="btn btn-main" style="min-height:52px" aria-describedby="swapWhy">${I.swap(20)}${L('Надіслати запит', 'Send request')}</button><span class="why" id="swapWhy" hidden>${L('Спершу приберіть контакт', 'Remove the contact first')}</span><span class="chip safe">${I.shield(18)}${CONTACTLESS()}</span></div></div></form>`}</div>`;
}

function renderFoot() { $('#foot').innerHTML = `${I.shield(22)}<span>${L('Вигадані дані для прототипу. Ініціали та вікова група — єдине, що видно про дітей. ', 'Fictional prototype data. Initials and age group are all that is shown about children. ')}<b>${CONTACTLESS()}.</b></span>`; }

function dockH() { const r = document.querySelector('.lesson-card .lc-row'); if (r && getComputedStyle(r).position === 'fixed') { const sv = r.style.display; r.style.display = 'flex'; const h = r.getBoundingClientRect().height; r.style.display = sv; document.documentElement.style.setProperty('--dock-h', Math.round(h) + 'px'); } }
function renderAll() { renderHead(); renderToday(); renderWeek(); renderGroups(); renderPlan(); renderNotes(); renderSwap(); renderFoot(); dockH(); if (typeof navEdges === 'function') navEdges(); }

/* ---------- події ---------- */
document.addEventListener('click', e => {
  const t = e.target.closest('button'); if (!t) return;
  if (t.dataset.lang) { S.lang = t.dataset.lang; renderAll(); $('[data-lang="' + S.lang + '"]').focus(); }
  else if (t.dataset.tz) { S.tz = t.dataset.tz; renderAll(); $('[data-tz="' + S.tz + '"]').focus(); }
  else if (t.dataset.demo) { S.demo = t.dataset.demo; S.entered = false; renderAll(); $('[data-demo="' + S.demo + '"]').focus(); }
  else if (t.dataset.grp) { S.grp = t.dataset.grp; renderGroups(); $('[data-grp="' + S.grp + '"]').focus(); }
  else if (t.dataset.ng) { S.ngrp = t.dataset.ng; S.noteErr = false; renderNotes(); $('[data-ng="' + S.ngrp + '"]').focus(); }
  else if (t.id === 'enter' && !t.disabled) { S.entered = true; renderToday(); $('#enter').focus(); }
  else if (t.id === 'avatarBtn') { menuOpen(!$('#menu').hasAttribute('data-open')); }
  else if (t.id === 'swapCancel') { S.swap = null; renderSwap(); }
});
document.addEventListener('change', e => {
  if (e.target.dataset.chk !== undefined) { S.checks[+e.target.dataset.chk] = e.target.checked; const k = S.checks.every(Boolean); renderPlan(); $('[data-chk="' + e.target.dataset.chk + '"]').focus(); if (k) { setEmo('joy'); say(L('Все готово', 'All set'), L('Матеріали підготовлено. Світло горить рівно.', 'Materials are ready. The light burns steadily.')); } }
  if (e.target.name === 'les') S.sel = e.target.value;
});
document.addEventListener('submit', e => {
  e.preventDefault();
  if (e.target.id === 'noteForm') {
    const v = $('#noteText').value.trim(); if (!v) { $('#noteText').focus(); return; }
    if (BAD.test(v)) { S.noteErr = true; flagErr($('#noteForm'), $('#noteText'), $('#noteErr'), true, v); $('#noteText').focus({ preventScroll: true }); showErr($('#noteErr')); return; }
    S.noteErr = false;
    (S.notes[S.ngrp] = S.notes[S.ngrp] || []).unshift({ w: { uk: 'Щойно', en: 'Just now' }, x: { uk: v, en: v } });
    renderNotes(); $('#noteText').focus();
  } else if (e.target.id === 'swapForm') {
    const c = $('#swapNote').value.trim();
    if (BAD.test(c)) { S.swapErr = true; flagErr($('#swapForm'), $('#swapNote'), $('#swapErr'), true, c); $('#swapNote').focus({ preventScroll: true }); showErr($('#swapErr')); return; }
    S.swapErr = false;
    const x = LESSONS.find(y => y.id === S.sel), r = $('#reason');
    S.swap = { name: `${gName(x.g)} · ${GROUPS[x.g].age} ${L('р.', 'y.o.')}`, when: `${dayOf(x.d)} · ${tmain(x.t)} (${tzLabel()})`, reason: r.options[r.selectedIndex].text };
    renderSwap(); $('#swapCancel').focus();
  }
});

/* після виправлення тексту помилка зникає, «Зберегти» знову активна */
document.addEventListener('input', e => {
  const map = { noteText: ['noteForm', 'noteErr', 'noteErr'], swapNote: ['swapForm', 'swapErr', 'swapErr'] };
  const m = map[e.target.id]; if (!m || !S[m[2]]) return;
  const v = e.target.value.trim();
  if (!BAD.test(v)) { S[m[2]] = false; flagErr($('#' + m[0]), e.target, $('#' + m[1]), false, v); }
});
document.addEventListener('keydown', e => { if (e.key === 'Escape' && $('#menu').hasAttribute('data-open')) { menuOpen(false); $('#avatarBtn').focus(); } });
document.addEventListener('click', e => { if ($('#menu').hasAttribute('data-open') && !e.composedPath().some(n => n.id === 'menu' || n.id === 'avatarBtn')) menuOpen(false); });
/* підсвітка активного розділу при прокрутці */
const secs = ['today', 'week', 'groups', 'plan', 'notes', 'swap'];
function spy() {
  let cur = 'today'; const y = innerHeight * .35;
  secs.forEach(id => { if ($('#' + id).getBoundingClientRect().top < y) cur = id; });
  $('#page').dataset.sec = cur;
  $$('#nav a').forEach(a => a.toggleAttribute('aria-current', a.dataset.sec === cur));
  $$('#nav a').forEach(a => { if (a.dataset.sec === cur) a.setAttribute('aria-current', 'true'); });
  if (spy.last !== cur) { spy.last = cur; navFollow(); }
}
addEventListener('scroll', spy, { passive: true });
function navEdges() {
  const n = $('#navIn'), p = $('#nav'); if (!n) return;
  p.toggleAttribute('data-fl', n.scrollLeft > 4); p.toggleAttribute('data-fr', n.scrollLeft + n.clientWidth < n.scrollWidth - 4);
}
$('#navIn').addEventListener('scroll', navEdges, { passive: true });
addEventListener('resize', navEdges);
function navFollow() {
  const n = $('#navIn'), a = $('#nav a[aria-current=true]'); if (!a || n.scrollWidth <= n.clientWidth) return;
  const t = a.offsetLeft - (n.clientWidth - a.offsetWidth) / 2; n.scrollTo({ left: Math.max(0, t), behavior: 'auto' });
}

if (q.get('demo') && DEMO[q.get('demo')]) S.demo = q.get('demo');
if (q.get('tz') && ['both', 'waw', 'kyiv'].includes(q.get('tz'))) S.tz = q.get('tz');
renderAll(); spy(); navEdges(); document.documentElement.classList.add('ready');
})();
