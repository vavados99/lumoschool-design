/* LUMOSCHOOL · В7 «Дашборд власника». Усі дані вигадані (ініціали, умовні номери). Без зовнішніх залежностей.
   Приватність: контакти приховано; «Показати» → запис у журнал → 10 с видно → знову приховано.
   Контактні рядки збираються лише в момент натискання і не лежать у HTML/даних. */
(() => {
'use strict';
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const NB = '\u00a0';

const S = {
  lang: new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'uk',
  per: 'week', cur: 'PLN', sel: { d: 3, h: 17 }, openSig: 'overlap', done: {}, filt: 'all', sus: {}, reveal: {}, ci: {},
  roles: {}, journal: [], fresh: null
};
const L = (uk, en) => (S.lang === 'en' ? en : uk);
const RATE = 10.4; // умовний курс: 1 PLN = 10,40 UAH
const nf = () => new Intl.NumberFormat(S.lang === 'en' ? 'en-GB' : 'uk-UA', { maximumFractionDigits: 0 }).format;
const nf1 = v => new Intl.NumberFormat(S.lang === 'en' ? 'en-GB' : 'uk-UA', { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(v);
const N = v => nf()(Math.round(v)).replace(/\u202f/g, NB);
const money = pln => N(S.cur === 'UAH' ? pln * RATE : pln) + NB + S.cur;
const short = pln => { const v = S.cur === 'UAH' ? pln * RATE : pln; return v >= 1000 ? nf1(v / 1000).replace(/[,.]0$/, '') + L(NB + 'тис', 'k') : String(Math.round(v)); };

/* ---------- іконки ---------- */
const sv = (p, s = 20, sw = 2) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${p}</svg>`;
const I = {
  up: s => sv('<path d="M12 19V6M6 11l6-6 6 6"/>', s || 16, 2.4),
  down: s => sv('<path d="M12 5v13M6 13l6 6 6-6"/>', s || 16, 2.4),
  eye: s => sv('<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>', s),
  lock: s => sv('<rect x="5" y="10.5" width="14" height="9.5" rx="2.5"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/>', s),
  check: s => sv('<path d="M5 12.5l4.5 4.5L19 7.5"/>', s, 3),
  chev: s => sv('<path d="M6 9l6 6 6-6"/>', s || 18, 2.4),
  warn: s => sv('<path d="M12 3.5l9.5 16.5h-19z"/><path d="M12 10v4.5M12 17.4v.1"/>', s),
  user: s => sv('<circle cx="12" cy="8" r="3.5"/><path d="M5 20c.8-4 3.6-6 7-6s6.2 2 7 6"/>', s),
  doc: s => sv('<path d="M6 3.5h8l4 4V20.5H6z"/><path d="M14 3.5v4h4M9 12h6M9 16h6"/>', s),
  sys: s => sv('<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/>', s)
};

/* ---------- дані (вигадані) ---------- */
let seedv = 7; const rnd = () => (seedv = (seedv * 16807) % 2147483647) / 2147483647;
const gen = (n, base, trend, noise, seed, prof) => { seedv = seed; return Array.from({ length: n }, (_, i) => Math.round(base * (prof ? prof[i % prof.length] : 1) * (1 + trend * i / (n - 1)) * (1 + (rnd() - .5) * noise))); };
const PER = {
  week: { n: 7, days: 7, lab: () => L(['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд'], ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']),
    inc: gen(7, 3100, .05, .06, 11, [1, 1.03, 1.08, 1.12, .97, .66, .55]), prv: gen(7, 2950, .04, .06, 13, [1, 1.03, 1.08, 1.1, .95, .64, .55]),
    att: [92, 91, 93, 90, 89, 86, 88], atp: [91, 90, 91, 90, 88, 85, 86],
    fun: [52, 31, 28, 22], noise: .22, cohorts: 3, rate: 4.71, dist: [168, 54, 12, 5, 2], compl: 3, sh: [34, 21, 18, 16, 11], pTot: 1600 },
  month: { n: 10, days: 30, lab: () => ['1', '4', '7', '10', '13', '16', '19', '22', '25', '28'],
    inc: gen(10, 9700, .07, .08, 21, null), prv: gen(10, 9300, .05, .08, 23, null),
    att: [90, 91, 90, 92, 91, 91, 92, 90, 91, 92], atp: [89, 90, 90, 90, 90, 91, 91, 89, 90, 90],
    fun: [214, 128, 113, 91], noise: .1, cohorts: 4, rate: 4.74, dist: [752, 218, 58, 21, 9], compl: 9, sh: [36, 19, 20, 15, 10], pTot: 6800 },
  quarter: { n: 13, days: 91, lab: () => Array.from({ length: 13 }, (_, i) => L('Т', 'W') + (i + 1)),
    inc: gen(13, 21500, .14, .07, 31, null), prv: gen(13, 20300, .1, .07, 33, null),
    att: [88, 89, 88, 90, 90, 89, 91, 90, 91, 92, 91, 92, 91], atp: [87, 88, 88, 89, 89, 89, 90, 90, 90, 91, 90, 91, 90],
    fun: [640, 395, 348, 276], noise: .05, cohorts: 5, rate: 4.68, dist: [2210, 690, 188, 70, 31], compl: 21, sh: [37, 18, 22, 14, 9], pTot: 20500 }
};
const sum = a => a.reduce((x, y) => x + y, 0), avg = a => sum(a) / a.length;
Object.values(PER).forEach(p => { p.rate = p.dist.reduce((s, c, i) => s + c * (5 - i), 0) / sum(p.dist); });
const REASONS = () => [L('Хвороба', 'Illness'), L('Забули про урок', 'Forgot the lesson'), L('Технічні проблеми', 'Technical issues'), L('Збіг з іншими справами', 'Schedule clash'), L('Інше', 'Other')];
const REASON_ORDER = [0, 1, 2, 3, 4]; // індекси у sh: хвороба, технічні, забули, розклад, інше
const WD = () => L(['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд'], ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);
const WDF = () => L(['понеділок', 'вівторок', 'середа', 'четвер', "п'ятниця", 'субота', 'неділя'], ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']);
const HOURS = Array.from({ length: 14 }, (_, i) => i + 8);
const DPROF = [.8, .82, .86, .84, .76, .5, .34], HPROF = [.2, .26, .4, .36, .3, .3, .46, .64, .86, 1, .98, .9, .6, .3];
const loadAt = (d, h, per) => {
  if (d === 3 && h === 17) return 1;
  if (d === 5 && h === 10) return .04;
  seedv = 100 + d * 17 + h * 3 + (per === 'week' ? 0 : per === 'month' ? 1000 : 2000);
  const n = PER[per].noise; let v = DPROF[d] * HPROF[h - 8] * 1.06 * (1 + (rnd() - .5) * n * 2);
  return Math.max(.05, Math.min(.98, v));
};
const TEACH = [
  { n: 'Олена Т.', i: 'ОТ', g: 4, l: [88, 86, 85], r: 4.9, k: 'o' }, { n: 'Marek W.', i: 'MW', g: 5, l: [104, 97, 94], r: 4.6, k: 'm', flag: 'overlap' },
  { n: 'Катерина Ш.', i: 'КШ', g: 3, l: [72, 74, 70], r: 4.8, k: 'k' }, { n: 'Tomasz R.', i: 'TR', g: 4, l: [81, 79, 83], r: 4.7, k: 't' },
  { n: 'Ніна Б.', i: 'НБ', g: 2, l: [46, 52, 55], r: 4.9, k: 'n' }, { n: 'Julia K.', i: 'JK', g: 3, l: [0, 38, 61], r: 4.5, k: 'j', leave: true }
];
const GROUPS = () => [
  { id: 'g1', n: 'B1 · ' + L('Пн/Ср 18:00', 'Mon/Wed 18:00'), t: 'Олена Т.', f: [9, 10], sig: 'quality', flag: L('Скарги на звук', 'Audio complaints') },
  { id: 'g2', n: 'Pre-A1 · ' + L('Сб 10:00', 'Sat 10:00'), t: 'Ніна Б.', f: [0, 8], sig: 'empty', flag: L('Порожня група', 'Empty group') },
  { id: 'g3', n: 'A2 · ' + L('Чт 17:00', 'Thu 17:00'), t: 'Marek W.', f: [8, 10], sig: 'overlap', flag: L('Перетин викладача', 'Teacher overlap') },
  { id: 'g4', n: 'Kids 8–10 · ' + L('Вт 16:00', 'Tue 16:00'), t: 'Катерина Ш.', f: [7, 8], sig: 'consent', flag: L('Згоди батьків', 'Parent consents') },
  { id: 'g5', n: 'C1 · ' + L('Нд 19:00', 'Sun 19:00'), t: 'Tomasz R.', f: [6, 8] },
  { id: 'g6', n: 'A1 · ' + L('Пт 19:00', 'Fri 19:00'), t: 'Tomasz R.', f: [7, 10] }
];
const ROLES = () => [
  { k: 'owner', n: L('Власник', 'Owner'), lock: true }, { k: 'manager', n: L('Керуючий', 'Manager') }, { k: 'method', n: L('Методист', 'Curriculum lead') },
  { k: 'teacher', n: L('Викладач', 'Teacher') }, { k: 'admin', n: L('Адміністратор', 'Administrator') }, { k: 'acc', n: L('Бухгалтер', 'Accountant') }
];
const PERMS = () => [{ k: 'fin', n: L('Гроші', 'Finance') }, { k: 'ctc', n: L('Контакти', 'Contacts') }, { k: 'sch', n: L('Розклад', 'Schedule') }, { k: 'log', n: L('Журнал', 'Journal') }, { k: 'acl', n: L('Доступи', 'Access') }];
const ROLE0 = { owner: 'fin ctc sch log acl', manager: 'fin sch log', method: 'sch', teacher: 'sch', admin: 'sch ctc', acc: 'fin' };
Object.entries(ROLE0).forEach(([r, v]) => v.split(' ').forEach(p => (S.roles[r + ':' + p] = true)));

const SIGS = () => [
  { id: 'empty', slot: { d: 5, h: 10 }, tag: L('Порожня група', 'Empty group'), title: L('Pre-A1 · Сб 10:00: жодного учня, старт через 3 дні', 'Pre-A1 · Sat 10:00: no students, starts in 3 days'),
    body: L('Група створена 9 днів тому, 2 заявки скасовано. Поруч група Сб 11:00 має 4 вільні місця.', 'Created 9 days ago, 2 applications cancelled. The Sat 11:00 group next to it has 4 free seats.'),
    acts: [{ k: 'merge', t: L("Об'єднати з Сб 11:00", 'Merge with Sat 11:00'), log: L("Власник: групу Pre-A1 Сб 10:00 об'єднано з групою Сб 11:00", 'Owner: group Pre-A1 Sat 10:00 merged into Sat 11:00') },
      { k: 'delay', t: L('Відкласти старт', 'Postpone start'), log: L('Власник: старт групи Pre-A1 Сб 10:00 відкладено на тиждень', 'Owner: group Pre-A1 Sat 10:00 start postponed by a week') }] },
  { id: 'overlap', slot: { d: 3, h: 17 }, tag: L('Перетин в розкладі', 'Schedule overlap'), title: L('Marek W. має два уроки в четвер о 17:00', 'Marek W. has two lessons on Thursday at 17:00'),
    body: L('Група A2 і індивідуальний урок накладаються. Вільні того часу: Tomasz R. і Катерина Ш.', 'Group A2 and a private lesson collide. Free at that time: Tomasz R. and Kateryna Sh.'),
    acts: [{ k: 'sub', t: L('Запропонувати заміну', 'Offer a substitute'), log: L('Власник: Tomasz R. запропоновано на заміну в Чт 17:00', 'Owner: Tomasz R. offered as substitute for Thu 17:00') },
      { k: 'move', t: L('Перенести індивід. урок', 'Move the private lesson'), log: L('Власник: індивідуальний урок Marek W. перенесено на Чт 18:30', "Owner: Marek W.'s private lesson moved to Thu 18:30") }] },
  { id: 'consent', slot: null, tag: L('Згода батьків', 'Parent consent'), title: L('3 родини групи Kids 8–10 не відповіли на згоду вже 6 днів', '3 families of Kids 8–10 have not answered the consent for 6 days'),
    body: L('Без згоди на запис уроку діти бачать урок без запису. Нагадування йде через платформу; контакт можна відкрити лише з записом у журнал.', 'Without the recording consent children join an unrecorded lesson. The reminder goes through the platform; a contact opens only with a journal entry.'),
    fam: [{ k: 'f1', n: L('Родина Д. · дитина 8 р.', 'Family D. · child 8'), tail: '42' }, { k: 'f2', n: L('Родина М. · дитина 10 р.', 'Family M. · child 10'), tail: '17' }, { k: 'f3', n: L('Родина С. · дитина 9 р.', 'Family S. · child 9'), tail: '08' }],
    acts: [{ k: 'remind', t: L('Нагадати через платформу', 'Remind via platform'), log: L('Власник: надіслано нагадування про згоду 3 родинам (Kids 8–10)', 'Owner: consent reminder sent to 3 families (Kids 8–10)') }] },
  { id: 'quality', slot: null, tag: L('Якість', 'Quality'), title: L('Два звернення про звук у групі B1 за тиждень', 'Two audio complaints in group B1 this week'),
    body: L('Обидва в середу ввечері; оцінка уроків B1 впала з 4,8 до 4,5. Схоже на проблему кімнати, а не викладача.', 'Both on Wednesday evening; B1 lesson rating fell from 4.8 to 4.5. Looks like a room problem, not a teacher problem.'),
    acts: [{ k: 'tech', t: L('Передати техпідтримці', 'Send to tech support'), log: L('Власник: скарги на звук B1 передано техпідтримці', 'Owner: B1 audio complaints passed to tech support') }] }
];

const mk = (t, a, uk, en, ty) => ({ t, a, uk, en, ty: ty || 'doc' });
S.journal = [
  mk('09:41', 'sys', 'Система: сформовано щотижневий звіт з відвідуваності', 'System: weekly attendance report generated', 'sys'),
  mk('09:12', 'adm', 'Адмін О.: учня К. додано до групи A1 · Пт 19:00', 'Admin O.: student K. added to group A1 · Fri 19:00'),
  mk('08:57', 'own', 'Власник: змінено ліміт групи C1 · Нд з 6 до 8', 'Owner: capacity of C1 · Sun changed from 6 to 8'),
  mk('вчора 21:20', 'sys', 'Система: згоду на запис уроку відкликала 1 родина', 'System: 1 family withdrew the recording consent', 'sys'),
  mk('вчора 18:05', 'own', 'Власник: переглянуто контакт викладача Tomasz R.', 'Owner: viewed teacher contact Tomasz R.', 'eye'),
  mk('вчора 16:44', 'acc', 'Бухгалтер: сформовано рахунки за жовтень (PL)', 'Accountant: October invoices generated (PL)'),
  mk('вчора 11:30', 'adm', 'Адмін О.: урок Ср 18:00 B1 перенесено на 18:30', 'Admin O.: B1 Wed 18:00 lesson moved to 18:30'),
  mk('нд 17:03', 'sys', 'Система: Julia K. позначена «у відпустці» до 2 листопада', 'System: Julia K. marked on leave until 2 November', 'sys')
].map(e => ({ ...e, en_t: e.t.replace('вчора', 'yesterday').replace('нд', 'Sun') }));
const ACTORS = { sys: ['Система', 'System'], adm: ['Адмін О.', 'Admin O.'], own: ['Власник', 'Owner'], acc: ['Бухгалтер', 'Accountant'] };

/* ---------- графіки: SVG лише для ліній, підписи — HTML ---------- */
const CH = {};
const sm = (pts) => { let d = `M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`; for (let i = 0; i < pts.length - 1; i++) { const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2; d += `C${(p1[0] + (p2[0] - p0[0]) / 6).toFixed(1)} ${(p1[1] + (p2[1] - p0[1]) / 6).toFixed(1)} ${(p2[0] - (p3[0] - p1[0]) / 6).toFixed(1)} ${(p2[1] - (p3[1] - p1[1]) / 6).toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`; } return d; };
function chart(id, cfg) {
  CH[id] = cfg; const { v, p, labels, min, max } = cfg; const n = v.length, W = 1000, H = 200, T = 22, B = 6;
  const X = i => i / (n - 1) * W, Y = x => T + (1 - (x - min) / (max - min)) * (H - T - B);
  const pts = v.map((x, i) => [X(i), Y(x)]), pp = p.map((x, i) => [X(i), Y(x)]);
  const ticks = [0, .5, 1].map(t => min + (max - min) * t);
  const idx = S.ci[id] ?? n - 1; const wide = innerWidth > 700;
  const step = wide ? 1 : Math.ceil(n / 4);
  return `<div class="chart" data-chart="${id}" tabindex="0" role="group" aria-label="${esc(cfg.aria)}"><div class="in">
    <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true" focusable="false">
      <defs><linearGradient id="gr-${id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#FBEFDF" stop-opacity=".30"/><stop offset="1" stop-color="#FBEFDF" stop-opacity="0"/></linearGradient></defs>
      ${ticks.map(t => `<line x1="0" x2="${W}" y1="${Y(t).toFixed(1)}" y2="${Y(t).toFixed(1)}" class="grid"/>`).join('')}
      <path d="${sm(pp)}" class="prev"/><path d="${sm(pts)} L${W} ${H} L0 ${H}Z" fill="url(#gr-${id})" stroke="none"/><path d="${sm(pts)}" class="cur"/>
    </svg>
    ${ticks.map(t => `<span class="yl" style="top:${(Y(t) / H * 100).toFixed(1)}%">${cfg.yfmt(t)}</span>`).join('')}
    <span class="rule" id="${id}-rule" style="left:${(X(idx) / W * 100).toFixed(2)}%"></span><span class="dot" id="${id}-dot" style="left:${(X(idx) / W * 100).toFixed(2)}%;top:${(Y(v[idx]) / H * 100).toFixed(2)}%"></span>
    <div class="xl">${labels.map((l, i) => i % step === 0 || i === n - 1 && step === 1 ? `<span style="left:${(X(i) / W * 100).toFixed(2)}%" class="${i === 0 ? 'first' : i === n - 1 ? 'last' : ''}">${l}</span>` : '').join('')}</div>
  </div></div>`;
}
function scrub(id, idx) {
  const c = CH[id]; if (!c) return; const n = c.v.length; idx = Math.max(0, Math.min(n - 1, idx)); S.ci[id] = idx;
  const H = 200, T = 22, B = 6, Y = x => T + (1 - (x - c.min) / (c.max - c.min)) * (H - T - B);
  const l = (idx / (n - 1) * 100).toFixed(2) + '%';
  $('#' + id + '-rule').style.left = l; const d = $('#' + id + '-dot'); d.style.left = l; d.style.top = (Y(c.v[idx]) / H * 100).toFixed(2) + '%';
  const ro = $('#' + id + '-read'); if (ro) ro.innerHTML = c.read(idx);
}

/* ---------- радіальна карта завантаження ---------- */
const VB = 600, CX = 300, R1 = 262, R0 = 112, RW = (R1 - R0) / 7, SEC = 360 / 15, GAP = 1.1;
const pol = (r, a) => [CX + r * Math.cos(a * Math.PI / 180), CX + r * Math.sin(a * Math.PI / 180)];
const arc = (r0, r1, a0, a1) => { const [x0, y0] = pol(r1, a0), [x1, y1] = pol(r1, a1), [x2, y2] = pol(r0, a1), [x3, y3] = pol(r0, a0); return `M${x0.toFixed(1)} ${y0.toFixed(1)}A${r1} ${r1} 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}L${x2.toFixed(1)} ${y2.toFixed(1)}A${r0} ${r0} 0 0 0 ${x3.toFixed(1)} ${y3.toFixed(1)}Z`; };
const ramp = [[0, [52, 34, 64]], [.3, [92, 66, 116]], [.6, [160, 126, 182]], [.85, [226, 196, 190]], [1, [251, 239, 223]]];
const heat = v => { for (let i = 1; i < ramp.length; i++) if (v <= ramp[i][0]) { const [a, ca] = ramp[i - 1], [b, cb] = ramp[i], t = (v - a) / (b - a); return `rgb(${ca.map((c, k) => Math.round(c + (cb[k] - c) * t)).join(',')})`; } return 'rgb(251,239,223)'; };
const ang = h => -90 + SEC * (h - 7);
const CONFL = [{ d: 3, h: 17, k: 'overlap' }, { d: 5, h: 10, k: 'empty' }];
function radial() {
  const per = S.per; let cells = '', total = 0, cnt = 0;
  for (let d = 0; d < 7; d++) for (const h of HOURS) {
    const v = loadAt(d, h, per); total += v; cnt++;
    const r1 = R1 - d * RW, r0 = r1 - RW + 2.2; const on = S.sel.d === d && S.sel.h === h;
    cells += `<path class="cell${on ? ' on' : ''}${S.day === d ? ' dayon' : ''}" d="${arc(r0, r1, ang(h) + GAP, ang(h) + SEC - GAP)}" fill="${heat(v)}" data-d="${d}" data-h="${h}" tabindex="${on ? 0 : -1}" role="gridcell" aria-label="${WD()[d]} ${h}:00, ${Math.round(v * 100)}%"/>`;
  }
  const mk = CONFL.map(c => { const [x, y] = pol(R1 - c.d * RW - RW / 2, ang(c.h) + SEC / 2); const open = c.k === 'overlap' ? !S.done.overlap : !S.done.empty; return open ? `<circle class="mk ${c.k}" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${c.k === 'overlap' ? 6.5 : 6}"/>` : ''; }).join('');
  const lab = HOURS.filter((h, i) => true).map(h => { const [x, y] = pol(R1 + 20, ang(h) + SEC / 2); return `<span class="hl" style="left:${(x / VB * 100).toFixed(2)}%;top:${(y / VB * 100).toFixed(2)}%">${h}</span>`; }).join('');
  const dl = WD().map((w, d) => { const [x, y] = pol(R1 - d * RW - RW / 2, ang(7) + SEC / 2 + 0); return `<span class="dl" style="left:${(x / VB * 100).toFixed(2)}%;top:${(y / VB * 100).toFixed(2)}%">${w}</span>`; }).join('');
  const lumoSize = R0 * 2 * .8 / VB * 100;
  return { avg: total / cnt, html: `<div class="radial" id="radial">
    <svg viewBox="0 0 ${VB} ${VB}" role="grid" aria-label="${esc(L('Завантаження розкладу: дні тижня — кільця, години — сектори', 'Schedule load: weekdays are rings, hours are sectors'))}" id="radialSvg">${cells}${mk}</svg>
    ${lab}${dl}
    <div class="lumo-wrap" id="lumo" style="width:${lumoSize}%;height:${lumoSize}%"><svg class="lumo" viewBox="-6 -6 112 112" aria-hidden="true" focusable="false">
      <path fill="#DF5520" d="M64.54 6C60.71 14.03 54.97 20.92 56.12 31.25C57.27 40.82 72.19 48.47 74.49 69.51C76.02 85.97 67.22 94 50 94C32.78 94 23.98 85.97 25.51 69.51C26.28 59.95 27.43 52.68 28.19 45.79C29.34 38.9 25.9 25.51 34.31 10.59C35.08 25.51 38.9 34.7 44.64 40.43C43.11 28.57 52.68 18.63 59.57 12.12C61.48 10.21 63.39 8.3 64.54 6Z"/>
      <path fill="#FBEFDF" d="M54.48 35.39C52.48 41.38 59.8 44.71 60.13 53.36C60.47 59.35 56.47 63.01 51.15 63.01C45.82 63.01 42.5 59.68 42.5 54.69C42.5 50.36 46.49 49.03 48.15 46.04C49.82 43.04 48.49 40.71 50.82 38.38C51.81 37.05 53.81 36.72 54.48 35.39Z"/>
      <g class="eyes"><path fill="#2A1030" d="M30.68 68.75A7.27 9.37 0 1 0 45.22 68.75A7.27 9.37 0 1 0 30.68 68.75ZM54.78 68.75A7.27 9.37 0 1 0 69.32 68.75A7.27 9.37 0 1 0 54.78 68.75Z"/><circle cx="40.27" cy="65.37" r="1.45" fill="#FBEFDF"/><circle cx="64.38" cy="65.37" r="1.45" fill="#FBEFDF"/></g></svg></div>
  </div>` };
}
const readout = () => { const { d, h } = S.sel, v = loadAt(d, h, S.per), seats = Math.round(v * 12);
  const c = CONFL.find(x => x.d === d && x.h === h && !S.done[x.k]);
  const note = c ? (c.k === 'overlap' ? L(' · перетин', ' · overlap') : L(' · порожня група', ' · empty group')) : '';
  return `<b>${WD()[d]}, ${h}:00</b> · ${seats}/12 ${L("кімнат", "rooms")} · ${Math.round(v * 100)}%${note}`; };

/* ---------- рендер ---------- */
const delta = (a, b, inv) => { const p = (a - b) / b * 100; const up = p >= 0; return `<span class="dlt ${up !== !!inv ? 'good' : 'bad'}">${up ? I.up() : I.down()}<span>${nf1(Math.abs(p)).replace(',0', ',0')}%</span><i class="vh">${up ? L('більше', 'up') : L('менше', 'down')}</i></span>`; };
const openCount = () => SIGS().filter(s => !S.done[s.id]).length;

function renderHero() {
  const p = PER[S.per], inc = sum(p.inc), incP = sum(p.prv), les = Math.round(inc / 38), lesP = Math.round(incP / 38);
  const att = avg(p.att), attP = avg(p.atp), f = p.fun, ret = f[3] / f[1] * 100;
  const rd = radial(); const open = openCount();
  const sigs = SIGS().map(s => {
    const isOpen = S.openSig === s.id, done = S.done[s.id];
    return `<li class="sig${isOpen ? ' open' : ''}${done ? ' done' : ''}">
      <button type="button" class="sig-h" data-sig="${s.id}" aria-expanded="${isOpen}" aria-controls="sb-${s.id}" data-k="sig-${s.id}">
        <span class="sig-tag">${done ? I.check(16) : ''}${done ? L('Виконано', 'Done') : s.tag}</span>
        <span class="sig-t">${esc(s.title)}</span><span class="sig-c">${I.chev()}</span></button>
      <div class="sig-b" id="sb-${s.id}" ${isOpen ? '' : 'hidden'}>
        <p>${esc(s.body)}</p>
        ${s.fam ? `<ul class="fam">${s.fam.map(m => `<li><span>${esc(m.n)}</span>${contact(m.k, m.tail)}</li>`).join('')}</ul>` : ''}
        ${done ? `<p class="okline">${I.check(16)} ${esc(done)}</p>` : `<div class="acts">${s.acts.map((a, i) => `<button type="button" class="btn${i ? ' ghost' : ''}" data-act="${s.id}:${a.k}" data-k="act-${s.id}-${a.k}">${esc(a.t)}</button>`).join('')}</div>`}
      </div></li>`; }).join('');
  $('#overview').innerHTML = `
    <p class="cmp">${L('Зміни — порівняно з попереднім періодом', 'Changes are versus the previous period')}</p>
    <div class="ribbon" aria-label="${esc(L('Ключові цифри періоду', 'Key figures of the period'))}">
      <div class="fig"><span class="fl">${L('Уроки', 'Lessons')}</span><b>${N(les)}</b>${delta(les, lesP)}</div>
      <div class="fig"><span class="fl">${L('Відвідуваність', 'Attendance')}</span><b>${nf1(att)}%</b>${delta(att, attP)}</div>
      <div class="fig"><span class="fl">${L('Платні через 3 міс.', 'Paid at 3 months')}</span><b>${nf1(ret)}%</b>${delta(ret, ret - 1.6)}</div>
      <div class="fig"><span class="fl">${L('Дохід', 'Income')}</span><b>${money(inc)}</b>${delta(inc, incP)}</div>
      <div class="fig"><span class="fl">${L('Оцінка уроків', 'Lesson rating')}</span><b>${nf1(p.rate)}<small>/5</small></b>${delta(p.rate, 4.66)}</div>
    </div>
    <div class="hero-grid">
      <div class="load">
        <div class="sec-h"><h1 id="h-overview">${L('Завантаження розкладу', 'Schedule load')}</h1></div>
        ${rd.html}
        <p class="read" id="read" aria-live="polite">${readout()}</p>
        <div class="days" role="group" aria-label="${esc(L('Обрати день', 'Pick a day'))}">${WD().map((w, d) => `<button type="button" class="dchip" data-day="${d}" aria-pressed="${S.sel.d === d}" data-k="day-${d}">${w}</button>`).join('')}</div>
        <div class="legend"><span>${L('вільно', 'free')}</span><i class="ramp"></i><span>${L('заповнено', 'full')}</span>${S.done.overlap ? '' : `<span class="lg-mk"><i class="mk-i"></i>${L('перетин', 'overlap')}</span>`}${S.done.empty ? '' : `<span class="lg-mk"><i class="mk-i dash"></i>${L('порожня група', 'empty group')}</span>`}</div>
        <p class="avgline">${L('Кільце — день тижня, сектор — година.', 'Ring = weekday, sector = hour.')} ${L('Середнє завантаження', 'Average load')}: <b>${Math.round(rd.avg * 100)}%</b></p>
      </div>
      <div class="attn" aria-labelledby="h-attn">
        <div class="sec-h"><h2 id="h-attn">${L('Потребує уваги сьогодні', 'Needs attention today')}</h2><span class="badge" aria-label="${open}">${open}</span></div>
        <p class="attn-sub">${open ? L('Відкрийте сигнал — дія з нього потрапить у журнал.', 'Open a signal — the action goes into the journal.') : L('Усе розібрано. Люмо відпочиває.', 'All clear. Lumo can rest.')}</p>
        <ul class="sigs">${sigs}</ul>
        <div class="lastlog"><h3>${L('Останні дії', 'Latest actions')}</h3><ul>${S.journal.slice(0, 3).map(e => `<li class="${e.fresh ? 'fresh' : ''}"><time>${esc(S.lang === 'en' ? (e.en_t || e.t) : e.t)}</time><span>${esc(S.lang === 'en' ? e.en : e.uk)}</span></li>`).join('')}</ul><a class="txt" href="#journal">${L('Увесь журнал', 'Full journal')}</a></div>
      </div>
    </div>`;
}

function contact(k, tail) {
  const vis = S.reveal[k];
  const val = vis ? (k.startsWith('f') ? `+48 555 010 1${tail}` : `${k}.demo@school.example`) : (k.startsWith('f') ? `+48 ••• ••• ••${tail}` : '••••@••••.•••');
  return `<span class="ctc${vis ? ' shown' : ''}"><span class="mask" ${vis ? "" : `aria-label="${esc(L("Контакт приховано", "Contact hidden"))}"`}>${vis ? I.eye(16) : I.lock(16)}${val}</span>
    <button type="button" class="txt" data-reveal="${k}:${tail}" data-k="rev-${k}" ${vis ? 'disabled' : ''}>${vis ? L('Видно 10 с', 'Visible 10 s') : L('Показати', 'Show')}</button></span>`;
}

function renderAtt() {
  const p = PER[S.per], a = avg(p.att), absTot = Math.round(p.pTot * (1 - a / 100));
  const sh = p.sh, order = [...sh.keys()].sort((x, y) => sh[y] - sh[x]), names = REASONS();
  // sh порядок: хвороба, технічні, забули, розклад, інше → у REASONS: 0 хвороба,1 забули,2 тех,3 розклад,4 інше
  const map = [0, 2, 1, 3, 4];
  const rows = order.map(i => `<li><span class="rn">${names[map[i]]}</span><span class="meter"><i style="width:${sh[i] / sh[order[0]] * 100}%"></i></span><b>${sh[i]}%</b></li>`).join('');
  const lab = p.lab();
  const read = i => `<b>${lab[i]}</b> · ${nf1(p.att[i])}% <span class="mut">${L('минулого періоду', 'previous')}: ${nf1(p.atp[i])}%</span>`;
  $('#attendance').innerHTML = `
    <div class="sec-h"><h2 id="h-attendance">${L('Відвідуваність', 'Attendance')}</h2><p>${L('Тримається', 'Holding at')} ${nf1(a)}%${L('; найчастіша причина пропуску — ', '; most common reason for absence: ')}${names[map[order[0]]].toLowerCase()}.</p></div>
    <div class="two">
      <div class="panel-l"><div class="read" id="att-read">${read(p.att.length - 1)}</div>
        ${chart('att', { v: p.att, p: p.atp, labels: lab, min: 82, max: 96, yfmt: t => Math.round(t) + '%', aria: L('Тренд відвідуваності', 'Attendance trend'), read })}
        <p class="key"><i class="k1"></i>${L('цей період', 'this period')} <i class="k2"></i>${L('минулий', 'previous')}</p></div>
      <div class="panel-r"><h3>${L('Чому пропускають', 'Why they miss')}</h3><p class="mut">${L('Пропусків за період', 'Absences in the period')}: ${N(absTot)}</p><ul class="reasons">${rows}</ul></div>
    </div>`;
  scrub('att', S.ci.att ?? p.att.length - 1);
}

function renderRet() {
  const p = PER[S.per], f = p.fun, names = [L('Пробний урок', 'Trial lesson'), L('Став платним', 'Became paying'), L('Залишився 1 міс.', 'Stayed 1 month'), L('Залишився 3 міс.', 'Stayed 3 months')];
  const maxw = f[0];
  const fun = f.map((v, i) => `<li><div class="fshape" style="--w:${(v / maxw * 100).toFixed(1)}%"><i></i></div><div class="ftxt"><span>${names[i]}</span><b>${N(v)}</b>${i ? `<em>${Math.round(v / f[i - 1] * 100)}% ${L('від попереднього', 'of previous')}</em>` : `<em>${L('початок', 'start')}</em>`}</div></li>`).join('');
  const CO = [[L('Чер', 'Jun'), 91, 84, 78], [L('Лип', 'Jul'), 92, 85, 79], [L('Серп', 'Aug'), 90, 83, null], [L('Вер', 'Sep'), 94, null, null], [L('Жов', 'Oct'), null, null, null]];
  const rows = CO.map(r => `<li><span class="cm">${r[0]}</span>${[1, 2, 3].map((m, i) => `<span class="cc">${r[i + 1] == null ? '<i class="na">—</i>' : `<i class="bar2"><u style="width:${r[i + 1]}%"></u></i><b>${r[i + 1]}%</b>`}</span>`).join('')}</li>`).join('');
  $('#retention').innerHTML = `
    <div class="sec-h"><h2 id="h-retention">${L('Утримання учнів', 'Retention')}</h2><p>${L('З пробного до платного — ', 'From trial to paying: ')}${Math.round(f[1] / f[0] * 100)}%; ${L('до 3 місяців доходить ', 'reaching 3 months: ')}${Math.round(f[3] / f[1] * 100)}% ${L('платних', 'of paying')}.</p></div>
    <div class="two">
      <div class="panel-l"><ul class="funnel">${fun}</ul></div>
      <div class="panel-r"><h3>${L('Когорти за місяцем старту', 'Cohorts by start month')}</h3><p class="mut">${L('частка, що лишилась після 1 / 2 / 3 місяців', 'share still active after 1 / 2 / 3 months')}</p>
        <ul class="cohorts"><li class="ch"><span></span><span>1 ${L('міс', 'mo')}</span><span>2 ${L('міс', 'mo')}</span><span>3 ${L('міс', 'mo')}</span></li>${rows}</ul></div>
    </div>`;
}

function renderMoney() {
  const p = PER[S.per], inc = sum(p.inc), incP = sum(p.prv), lab = p.lab(); const dv = S.cur === 'UAH' ? RATE : 1;
  const mx = Math.max(...p.inc, ...p.prv), mn = Math.min(...p.inc, ...p.prv);
  const lo = Math.floor(mn * .92 / 1000) * 1000, hi = Math.ceil(mx * 1.05 / 1000) * 1000;
  const read = i => `<b>${lab[i]}</b> · ${money(p.inc[i])} <span class="mut">${L('минулого', 'previous')}: ${money(p.prv[i])}</span>`;
  const pl = 61, ua = 39;
  $('#money').innerHTML = `
    <div class="sec-h"><h2 id="h-money">${L('Гроші', 'Money')}</h2><p>${money(inc)} ${L('за період', 'in the period')}, ${L('на', 'versus')} ${nf1(Math.abs((inc - incP) / incP * 100))}% ${inc >= incP ? L('більше', 'more') : L('менше', 'less')} ${L('ніж минулого разу.', 'than last time.')}</p></div>
    <div class="two">
      <div class="panel-l"><div class="read" id="inc-read">${read(p.inc.length - 1)}</div>
        ${chart('inc', { v: p.inc, p: p.prv, labels: lab, min: lo, max: hi, yfmt: t => short(t), aria: L('Дохід за період', 'Income over the period'), read })}
        <p class="key"><i class="k1"></i>${L('цей період', 'this period')} <i class="k2"></i>${L('минулий', 'previous')} · ${L('умовний курс', 'illustrative rate')} 1 PLN = ${nf1(RATE).replace('.', S.lang === 'en' ? '.' : ',')}0 UAH</p></div>
      <div class="panel-r"><h3>${L('Звідки гроші', 'Where it comes from')}</h3>
        <div class="split" role="img" aria-label="PL ${pl}%, UA ${ua}%"><i style="width:${pl}%"></i><i style="width:${ua}%"></i></div>
        <ul class="splitl"><li><span class="sw s1"></span><span>${L('Польща', 'Poland')}</span><b>${money(inc * pl / 100)}</b></li><li><span class="sw s2"></span><span>${L('Україна', 'Ukraine')}</span><b>${money(inc * ua / 100)}</b></li></ul>
        <dl class="mini"><div><dt>${L('Середній чек за урок', 'Average per lesson')}</dt><dd>${money(38)}</dd></div><div><dt>${L('Очікує оплати', 'Awaiting payment')}</dt><dd>${money(inc * .062)}</dd></div></dl>
        </div>
    </div>`;
  scrub('inc', S.ci.inc ?? p.inc.length - 1);
}

function renderQuality() {
  const p = PER[S.per], d = p.dist, tot = sum(d), mx = Math.max(...d); p.rate = d.reduce((s, c, i) => s + c * (5 - i), 0) / tot;
  const rows = d.map((c, i) => `<li><span class="st">${5 - i}${I.sv ? '' : ''}<i class="star" aria-hidden="true">★</i></span><span class="meter"><i style="width:${c / mx * 100}%"></i></span><b>${N(c)}</b></li>`).join('');
  const CP = [[L('Звук лунає, учні не чують', 'Echo, students cannot hear'), 'B1 · ' + L('Ср', 'Wed'), L('нова', 'new')], [L('У кімнаті немає звуку 5 хв', 'No sound in the room for 5 min'), 'B1 · ' + L('Ср', 'Wed'), L('нова', 'new')], [L('Урок почався із запізненням 12 хв', 'Lesson started 12 min late'), 'A2 · ' + L('Пн', 'Mon'), L('розглядається', 'in review')], [L('Занадто швидкий темп для дитини', 'Pace too fast for a child'), 'Kids 8–10', L('відповідь надіслана', 'answered')]];
  $('#quality').innerHTML = `
    <div class="sec-h"><h2 id="h-quality">${L('Якість уроків', 'Lesson quality')}</h2><p>${L('Середня оцінка', 'Average rating')} ${nf1(p.rate)} ${L('із 5; відгуків', 'of 5; reviews')}: ${N(tot)}; ${L('скарг за період', 'complaints in the period')}: ${p.compl}.</p></div>
    <div class="two">
      <div class="panel-l"><ul class="dist">${rows}</ul></div>
      <div class="panel-r"><h3>${L('Останні скарги', 'Latest complaints')}</h3><ul class="compl">${CP.map(c => `<li><b>${esc(c[0])}</b><span>${esc(c[1])} · <em>${esc(c[2])}</em></span></li>`).join('')}</ul></div>
    </div>`;
}

function renderManage() {
  const col = S.per === 'week' ? 0 : S.per === 'month' ? 1 : 2; const flt = S.filt;
  const T = TEACH.filter(t => flt === 'all' || t.flag || t.leave).map(t => {
    const sus = S.sus[t.k], ld = t.l[col];
    return `<li class="trow${sus ? ' sus' : ''}"><span class="av" aria-hidden="true">${t.i}</span><span class="tn"><b>${t.n}</b><span class="mut">${L('груп', 'groups')}: ${t.g} · ${t.leave ? L('у відпустці', 'on leave') : sus ? L('доступ призупинено', 'access paused') : t.flag ? L('перетин у розкладі', 'schedule overlap') : L('працює', 'active')}</span></span>
      <span class="tl"><span class="meter"><i style="width:${Math.min(100, ld)}%"></i></span><b>${ld}%</b></span><span class="tr">★ ${nf1(t.r)}</span>
      ${contact(t.k, '00')}
      <button type="button" class="txt" data-sus="${t.k}" data-k="sus-${t.k}" aria-pressed="${!!sus}">${sus ? L('Відновити', 'Restore') : L('Призупинити', 'Pause')}</button></li>`; }).join('');
  const G = GROUPS().filter(g => flt === 'all' || g.flag && !S.done[g.sig]).map(g => `<li class="grow"><span class="gn"><b>${esc(g.n)}</b><span class="mut">${esc(g.t)}</span></span><span class="gf"><span class="pips" aria-hidden="true">${Array.from({ length: g.f[1] }, (_, i) => `<i class="${i < g.f[0] ? 'on' : ''}"></i>`).join('')}</span><b>${g.f[0]}/${g.f[1]}</b></span>${g.flag && !S.done[g.sig] ? `<span class="gflag">${I.warn(16)}${esc(g.flag)}</span>` : `<span class="gflag ok">${I.check(16)}${L('без зауважень', 'no issues')}</span>`}</li>`).join('');
  const roles = ROLES(), perms = PERMS();
  const R = roles.map(r => `<li class="rrow"><span class="rname">${r.n}${r.lock ? `<span class="lk">${I.lock(14)}</span>` : ''}</span><span class="perms">${perms.map(pm => { const on = !!S.roles[r.k + ':' + pm.k]; return `<button type="button" class="perm" data-perm="${r.k}:${pm.k}" aria-pressed="${on}" ${r.lock ? 'disabled' : ''} data-k="perm-${r.k}-${pm.k}">${on ? I.check(14) : ''}<span>${pm.n}</span></button>`; }).join('')}</span></li>`).join('');
  $('#manage').innerHTML = `
    <div class="sec-h"><h2 id="h-manage">${L('Керування', 'Management')}</h2>
      <div class="seg" role="group" aria-label="${esc(L('Фільтр', 'Filter'))}"><button type="button" data-filt="all" aria-pressed="${flt === 'all'}" data-k="f-all">${L('Усі', 'All')}</button><button type="button" data-filt="attn" aria-pressed="${flt === 'attn'}" data-k="f-attn">${L('Потребують уваги', 'Need attention')}</button></div></div>
    <div class="three">
      <div><h3>${L('Викладачі · 6 з 14', 'Teachers · 6 of 14')}</h3><ul class="tlist">${T || `<li class="emp">${L('Немає', 'None')}</li>`}</ul></div>
      <div><h3>${L('Групи · 6 з 38', 'Groups · 6 of 38')}</h3><ul class="glist">${G || `<li class="emp">${L('Немає', 'None')}</li>`}</ul></div>
      <div><h3>${L('Доступи за ролями', 'Access by role')}</h3><p class="mut">${L('Натисніть, щоб увімкнути чи вимкнути. Кожна зміна йде в журнал.', 'Press to turn on or off. Every change goes to the journal.')}</p><ul class="rlist">${R}</ul></div>
    </div>`;
}

function renderJournal() {
  const J = S.journal.slice(0, 8).map(e => { const t = S.lang === 'en' ? (e.en_t || e.t) : e.t; const a = ACTORS[e.a][S.lang === 'en' ? 1 : 0];
    return `<li class="jrow${e.fresh ? ' fresh' : ''}"><time>${esc(t)}</time><span class="jic" aria-hidden="true">${e.ty === 'eye' ? I.eye(16) : e.ty === 'sys' ? I.sys(16) : I.doc(16)}</span><span class="jt">${esc(S.lang === 'en' ? e.en : e.uk)}</span></li>`; }).join('');
  $('#journal').innerHTML = `
    <div class="sec-h"><h2 id="h-journal">${L('Журнал дій', 'Action journal')}</h2><p>${L('Усе, що змінюють люди й система. Перегляд контактів теж записується.', 'Everything people and the system change. Viewing contacts is logged too.')}</p></div>
    <ul class="jlist" aria-live="polite">${J}</ul>`;
}

function renderChrome() {
  document.documentElement.lang = S.lang;
  $('#who').innerHTML = `<span>${L('Власник', 'Owner')}</span> · <b>${L('Анна Л.', 'Anna L.')}</b> <span class="mut">· ${L('пн, 19 жовтня', 'Mon, 19 October')}</span>`;
  $('#curSeg').setAttribute('aria-label', L('Валюта', 'Currency'));
  $('#curSeg').innerHTML = ['PLN', 'UAH'].map(c => `<button type="button" data-cur="${c}" aria-pressed="${S.cur === c}" data-k="cur-${c}">${c}</button>`).join('');
  $('#perSeg').setAttribute('aria-label', L('Період', 'Period'));
  $('#perSeg').innerHTML = [['week', L('Тиждень', 'Week')], ['month', L('Місяць', 'Month')], ['quarter', L('Квартал', 'Quarter')]].map(([k, t]) => `<button type="button" data-per="${k}" aria-pressed="${S.per === k}" data-k="per-${k}">${t}</button>`).join('');
  $$('[data-lang]').forEach(b => b.setAttribute('aria-pressed', b.dataset.lang === S.lang));
  const NAV = [['overview', L('Огляд', 'Overview')], ['attendance', L('Відвідуваність', 'Attendance')], ['retention', L('Утримання', 'Retention')], ['money', L('Гроші', 'Money')], ['quality', L('Якість', 'Quality')], ['manage', L('Керування', 'Management')], ['journal', L('Журнал', 'Journal')]];
  $('#nav').innerHTML = NAV.map(([k, t]) => `<a href="#${k}" data-sec="${k}">${t}</a>`).join('');
  $('#skip').textContent = L('Перейти до змісту', 'Skip to content');
  $('#foot').innerHTML = `<p>${L('Демо-прототип. Усі імена, цифри та контакти вигадані. Курс валют умовний.', 'Demo prototype. All names, numbers and contacts are made up. The exchange rate is illustrative.')}</p>`;
  document.title = L('LUMOSCHOOL · Дашборд власника', 'LUMOSCHOOL · Owner dashboard');
}

function renderAll(only) {
  const act = document.activeElement; const key = act && act.dataset ? act.dataset.k : null;
  const cs = act && act.classList && act.classList.contains('chart') ? act.dataset.chart : null;
  renderChrome(); renderHero(); renderAtt(); renderRet(); renderMoney(); renderQuality(); renderManage(); renderJournal();
  document.getElementById('page').dataset.emo = openCount() ? 'wait' : 'rest';
  if (key) { const el = document.querySelector(`[data-k="${key}"]`); if (el && !el.disabled) el.focus({ preventScroll: true }); }
  if (cs) { const el = $(`[data-chart="${cs}"]`); if (el) el.focus({ preventScroll: true }); }
  placeLight(); nav();
  if (S.fresh) { $$(S.fresh).forEach(e => { e.classList.add('fresh-in'); setTimeout(() => e.classList.remove('fresh-in'), 600); }); S.fresh = null; }
}
function placeLight() {
  const l = $('#lumo'); if (!l) return; const r = l.getBoundingClientRect(), pg = $('#page').getBoundingClientRect();
  const x = r.left + r.width / 2 - pg.left, y = r.top + r.height / 2 - pg.top;
  const el = $('#light'); el.style.left = x + 'px'; el.style.top = y + 'px';
}
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('on'); clearTimeout(toast.h); toast.h = setTimeout(() => t.classList.remove('on'), 2400); }
function log(uk, en, ty) {
  S.journal.unshift({ t: L('щойно', 'just now') === 'щойно' ? 'щойно' : 'щойно', en_t: 'just now', a: 'own', uk, en, ty: ty || 'doc', fresh: true });
  S.journal.slice(1).forEach(e => (e.fresh = false));
  toast(L('Записано в журнал', 'Logged in the journal'));
}
const sigAct = (id, k) => { const s = SIGS().find(x => x.id === id), a = s.acts.find(x => x.k === k); S.done[id] = a.t; const en = SIGS.en; log(S.lang === 'uk' ? a.log : '', '', 'doc'); };

/* ---------- події ---------- */
const sigLogBoth = (id, k) => { const save = S.lang; S.lang = 'uk'; const uk = SIGS().find(x => x.id === id).acts.find(x => x.k === k).log; S.lang = 'en'; const en = SIGS().find(x => x.id === id).acts.find(x => x.k === k).log; S.lang = save; return [uk, en]; };
const permName = (rk, pk) => { const sv = S.lang, o = {}; ['uk', 'en'].forEach(l => { S.lang = l; o[l] = [ROLES().find(r => r.k === rk).n, PERMS().find(p => p.k === pk).n]; }); S.lang = sv; return o; };
document.addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  const d = b.dataset;
  if (d.lang) { S.lang = d.lang; renderAll(); return; }
  if (d.cur) { S.cur = d.cur; S.fresh = '#money .chart,#overview .ribbon'; renderAll(); return; }
  if (d.per) { S.per = d.per; S.ci = {}; S.fresh = '.chart,.radial,.ribbon,.funnel,.reasons'; renderAll(); return; }
  if (d.sig) { S.openSig = S.openSig === d.sig ? null : d.sig; const s = SIGS().find(x => x.id === d.sig); if (S.openSig && s.slot) S.sel = { ...s.slot }; renderAll(); return; }
  if (d.act) { const [id, k] = d.act.split(':'); const [uk, en] = sigLogBoth(id, k); S.done[id] = SIGS().find(x => x.id === id).acts.find(x => x.k === k).t;
    S.journal.forEach(x => (x.fresh = false)); S.journal.unshift({ t: 'щойно', en_t: 'just now', a: 'own', uk, en, ty: 'doc', fresh: true }); toast(L('Записано в журнал', 'Logged in the journal')); S.fresh = '.jrow.fresh'; renderAll(); return; }
  if (d.reveal) { const [k, tail] = d.reveal.split(':'); S.reveal[k] = true;
    const who = k.startsWith('f') ? [L('родини', 'family'), ''] : null; const names = { f1: ['Д.', 'D.'], f2: ['М.', 'M.'], f3: ['С.', 'S.'] };
    const t = TEACH.find(x => x.k === k);
    const uk = t ? `Власник: переглянуто контакт викладача ${t.n} (на 10 с)` : `Власник: переглянуто контакт родини ${names[k][0]} (на 10 с)`, en = t ? `Owner: viewed contact of teacher ${t.n} (for 10 s)` : `Owner: viewed contact of family ${names[k][1]} (for 10 s)`;
    S.journal.forEach(x => (x.fresh = false)); S.journal.unshift({ t: 'щойно', en_t: 'just now', a: 'own', uk, en, ty: 'eye', fresh: true });
    toast(L('Контакт показано · записано в журнал', 'Contact shown · logged in the journal')); renderAll();
    setTimeout(() => { S.reveal[k] = false; renderAll(); }, 10000); return; }
  if (d.filt) { S.filt = d.filt; renderAll(); return; }
  if (d.sus) { const t = TEACH.find(x => x.k === d.sus); S.sus[d.sus] = !S.sus[d.sus]; const on = S.sus[d.sus];
    S.journal.forEach(x => (x.fresh = false)); S.journal.unshift({ t: 'щойно', en_t: 'just now', a: 'own', uk: `Власник: доступ викладача ${t.n} ${on ? 'призупинено' : 'відновлено'}`, en: `Owner: access of ${t.n} ${on ? 'paused' : 'restored'}`, ty: 'doc', fresh: true }); toast(L('Записано в журнал', 'Logged in the journal')); renderAll(); return; }
  if (d.perm) { const [r, p] = d.perm.split(':'); S.roles[d.perm] = !S.roles[d.perm]; const nm = permName(r, p), on = S.roles[d.perm];
    S.journal.forEach(x => (x.fresh = false)); S.journal.unshift({ t: 'щойно', en_t: 'just now', a: 'own', uk: `Власник: роль «${nm.uk[0]}» — доступ «${nm.uk[1]}» ${on ? 'увімкнено' : 'вимкнено'}`, en: `Owner: role "${nm.en[0]}" — "${nm.en[1]}" ${on ? 'turned on' : 'turned off'}`, ty: 'doc', fresh: true }); toast(L('Записано в журнал', 'Logged in the journal')); renderAll(); return; }
  if (d.day != null) { const dd = +d.day; const peak = HOURS.reduce((m, h) => loadAt(dd, h, S.per) > loadAt(dd, m, S.per) ? h : m, 8); S.sel = { d: dd, h: peak }; S.day = null; renderAll(); return; }
});
function selCell(el) { S.sel = { d: +el.dataset.d, h: +el.dataset.h }; $$('.cell').forEach(c => { const on = +c.dataset.d === S.sel.d && +c.dataset.h === S.sel.h; c.classList.toggle('on', on); c.tabIndex = on ? 0 : -1; }); $('#read').innerHTML = readout(); $$('.dchip').forEach(c => c.setAttribute('aria-pressed', +c.dataset.day === S.sel.d)); }
document.addEventListener('pointerdown', e => { const c = e.target.closest('.cell'); if (c) selCell(c); });
document.addEventListener('pointermove', e => { const c = e.target.closest('.chart'); if (c && e.pointerType !== 'touch' || c && e.buttons) { const r = c.querySelector(".in").getBoundingClientRect(); scrub(c.dataset.chart, Math.round((e.clientX - r.left) / r.width * (CH[c.dataset.chart].v.length - 1))); } });
document.addEventListener('pointerdown', e => { const c = e.target.closest('.chart'); if (c) { const r = c.querySelector(".in").getBoundingClientRect(); scrub(c.dataset.chart, Math.round((e.clientX - r.left) / r.width * (CH[c.dataset.chart].v.length - 1))); } });
document.addEventListener('keydown', e => {
  const c = e.target.closest && e.target.closest('.cell');
  if (c) { let d = +c.dataset.d, h = +c.dataset.h; const k = e.key;
    if (k === 'ArrowRight') h++; else if (k === 'ArrowLeft') h--; else if (k === 'ArrowDown') d++; else if (k === 'ArrowUp') d--; else return;
    e.preventDefault(); d = Math.max(0, Math.min(6, d)); h = Math.max(8, Math.min(21, h));
    const n = $(`.cell[data-d="${d}"][data-h="${h}"]`); selCell(n); n.focus(); return; }
  const ch = e.target.closest && e.target.closest('.chart');
  if (ch && ['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) { e.preventDefault(); const id = ch.dataset.chart, n = CH[id].v.length, cur = S.ci[id] ?? n - 1; scrub(id, e.key === 'Home' ? 0 : e.key === 'End' ? n - 1 : cur + (e.key === 'ArrowRight' ? 1 : -1)); }
  if (e.key === 'Escape' && S.openSig) { const k = S.openSig; S.openSig = null; renderAll(); const el = $(`[data-k="sig-${k}"]`); if (el) el.focus(); }
});

/* навігація: активна секція */
function nav() { const ids = ['overview', 'attendance', 'retention', 'money', 'quality', 'manage', 'journal']; let cur = ids[0];
  for (const id of ids) { if ($('#' + id).getBoundingClientRect().top < innerHeight * .4) cur = id; }
  $$('#nav a').forEach(a => a.toggleAttribute('aria-current', a.dataset.sec === cur) || (a.dataset.sec === cur ? a.setAttribute('aria-current', 'true') : a.removeAttribute('aria-current')));
  $$('#nav a').forEach(a => { if (a.dataset.sec === cur) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); }); }
let tk; addEventListener('scroll', () => { if (!tk) tk = requestAnimationFrame(() => { tk = 0; nav(); }); }, { passive: true });
let lw = innerWidth; addEventListener('resize', () => { if (innerWidth !== lw) { lw = innerWidth; renderAll(); } });
(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(placeLight);
renderAll(); (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => { placeLight(); $("#page").classList.add("ready"); });
})();
