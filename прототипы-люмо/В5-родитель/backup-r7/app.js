/* LUMOSCHOOL · В5 «Кабінет батьків». Усі дані вигадані. Без зовнішніх залежностей. */
(() => {
'use strict';
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/* ---------- іконки ---------- */
const sv = (p, s = 24, sw = 2) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${p}</svg>`;
const I = {
  cal: s => sv('<rect x="3.5" y="5" width="17" height="15" rx="3"/><path d="M8 3v4M16 3v4M3.5 10h17"/>', s),
  shield: s => sv('<path d="M12 3l7.5 3v5.5c0 4.6-3.1 7.8-7.5 9.5-4.4-1.7-7.5-4.9-7.5-9.5V6z"/><path d="M9 12l2.2 2.2L15.5 10"/>', s),
  grow: s => sv('<path d="M4 20h16"/><path d="M6 20v-5M12 20v-9M18 20V6"/><path d="M15 8.5l3-3 3 1"/>', s),
  chat: s => sv('<path d="M4 5.5h16v10.5H10l-4.5 3.5V16H4z"/><path d="M8 10h8"/>', s),
  box: s => sv('<rect x="3.5" y="4.5" width="17" height="5" rx="1.5"/><path d="M5 9.5V19h14V9.5M10 13.5h4"/>', s),
  check: s => sv('<path d="M5 12.5l4.5 4.5L19 7.5"/>', s, 3),
  cross: s => sv('<path d="M6 6l12 12M18 6L6 18"/>', s, 3),
  dot: s => sv('<circle cx="12" cy="12" r="4.5" fill="currentColor"/>', s),
  warn: s => sv('<path d="M12 3.5l9.5 16.5h-19z"/><path d="M12 10v4.5M12 17.4v.1"/>', s),
  clock: s => sv('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>', s),
  pause: s => sv('<path d="M9 6v12M15 6v12"/>', s, 3),
  info: s => sv('<circle cx="12" cy="12" r="9"/><path d="M12 11v5.5M12 7.8v.1"/>', s),
  down: s => sv('<path d="M12 4v11M7 11l5 5 5-5M5 20h14"/>', s),
  trash: s => sv('<path d="M5 7h14M10 7V4.5h4V7M7 7l1 13h8l1-13M10 11v6M14 11v6"/>', s),
  eye: s => sv('<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>', s),
  mic: s => sv('<rect x="9" y="3.5" width="6" height="11" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3"/>', s),
  globe: s => sv('<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c3 3.2 3 13.8 0 17M12 3.5c-3 3.2-3 13.8 0 17"/>', s),
  user: s => sv('<circle cx="12" cy="8" r="3.8"/><path d="M4.5 20c.8-4 3.8-6 7.5-6s6.7 2 7.5 6"/>', s),
  star: s => sv('<path d="M12 4l2.4 5 5.4.7-4 3.7 1 5.4L12 16.2 7.2 18.8l1-5.4-4-3.7 5.4-.7z"/>', s),
};

/* ---------- вигадані дані ---------- */
// «Зараз» у демо — вигаданий час за Варшавою: середа, 21 жовтня 2026, 14:05; далі тікає по-справжньому.
const BASE = Date.UTC(2026, 9, 21, 14, 5, 0), T0 = performance.now();
const nowW = () => BASE + (performance.now() - T0);
const wall = (d, h, mi) => Date.UTC(2026, 9, d, h, mi);
const TODAY = { d: 21, m: 9, y: 2026 };

const KIDS = {
  olya: { name: { uk: 'Оля', en: 'Olya' }, gen: { uk: 'Олі', en: 'Olya' }, letter: { uk: 'О', en: 'O' }, age: 9, ageT: { uk: '9 років', en: '9 years old' }, level: 'A1\u00A0→\u00A0A2', teacher: { uk: 'Єва', en: 'Eva' } },
  max: { name: { uk: 'Макс', en: 'Max' }, gen: { uk: 'Макса', en: 'Max' }, letter: { uk: 'М', en: 'M' }, age: 13, ageT: { uk: '13 років', en: '13 years old' }, level: 'A2\u00A0→\u00A0B1', teacher: { uk: 'Тарас', en: 'Taras' } },
};
const LESSONS = {
  olya: [
    { d: 19, h: 17, mi: 0, st: 'passed', topic: { uk: 'Розмова: моя родина', en: 'Speaking: my family' } },
    { d: 21, h: 17, mi: 0, st: 'booked', topic: { uk: 'Читання вголос', en: 'Reading aloud' } },
    { d: 23, h: 17, mi: 0, st: 'booked', topic: { uk: 'Слова: їжа', en: 'Words: food' } },
    { d: 24, h: 11, mi: 0, st: 'cancelled', by: 'parent', topic: { uk: 'Повторення тижня', en: 'Week review' } },
  ],
  max: [
    { d: 20, h: 18, mi: 30, st: 'passed', topic: { uk: 'Минулий час у розповіді', en: 'Past tense in a story' } },
    { d: 22, h: 18, mi: 30, st: 'booked', topic: { uk: 'Розмова: плани на літо', en: 'Speaking: summer plans' } },
    { d: 23, h: 18, mi: 30, st: 'cancelled', by: 'teacher', topic: { uk: 'Читання: стаття про космос', en: 'Reading: a space article' } },
    { d: 25, h: 17, mi: 0, st: 'booked', topic: { uk: 'Письмо: короткий лист', en: 'Writing: a short letter' } },
  ],
};
const CONS = ['data', 'part', 'rec'];
const state = {
  lang: 'uk', kid: 'olya', section: 'schedule', dlg: null, override: null,
  consent: {
    olya: { data: { on: true, date: '2026-09-03' }, part: { on: true, date: '2026-09-03' }, rec: { on: false, date: null } },
    max: { data: { on: true, date: '2026-09-05' }, part: { on: true, date: '2026-09-05' }, rec: { on: false, date: null } },
  },
  msgs: {
    olya: [
      { me: true, d: 12, text: { uk: 'Добрий день! Чи можна додати на уроках більше розмови?', en: 'Hello! Could we add more speaking to the lessons?' } },
      { d: 13, text: { uk: 'Так, з п’ятниці додамо більше розмовної практики, як ви просили.', en: 'Yes, from Friday we will add more speaking practice, as you asked.' } },
      { d: 20, unread: true, text: { uk: 'Сьогодні Оля вперше прочитала короткий текст уголос без підказок. Вдома вистачить 10 хвилин: нехай перекаже мені улюблений епізод з мультика англійською.', en: 'Today Olya read a short text aloud for the first time with no hints. At home 10 minutes is enough: she can retell her favourite cartoon scene to me in English.' } },
    ],
    max: [
      { d: 14, text: { uk: 'Макс добре тримається в розмові. Ще попрацюємо над минулим часом.', en: 'Max holds a conversation well. We will keep working on the past tense.' } },
      { d: 20, unread: true, important: true, text: { uk: 'Мені дуже шкода: у п’ятницю, 23 жовтня, я не зможу провести урок через хворобу. Пропоную перенести на суботу, 24 жовтня, о 11:00 за Варшавою (12:00 за Києвом). Напишіть мені тут, чи підходить.', en: 'I am very sorry: on Friday, 23 October, I cannot teach because I am ill. I suggest moving it to Saturday, 24 October, at 11:00 Warsaw time (12:00 Kyiv). Please write here if that works.' } },
    ],
  },
};

const PROG = {
  olya: {
    title: { uk: 'Оля робить спокійні, стабільні кроки', en: 'Olya is taking calm, steady steps' },
    lead: { uk: 'Вона вже розуміє багато простих фраз і сміливішає в розмові. Читання ще вимагає часу.', en: 'She already understands many simple phrases and is getting braver in conversation. Reading still needs time.' },
    skills: [['listen', 3], ['speak', 2], ['read', 1], ['write', 2]], done: 7,
    now: [{ uk: 'Читати короткі тексти вголос', en: 'Reading short texts aloud' }, { uk: 'Слова про їжу та покупки', en: 'Words about food and shopping' }],
    home: { uk: 'Десять хвилин на день: перекажіть епізод з мультика англійською.', en: 'Ten minutes a day: retell a cartoon scene in English.' },
    att: { uk: 'Відвідано 7 із 8 уроків за вересень і жовтень.', en: 'Attended 7 of 8 lessons in September and October.' },
  },
  max: {
    title: { uk: 'Макс упевнено читає, розмова ще набирає силу', en: 'Max reads with confidence; speaking is still growing' },
    lead: { uk: 'Він добре розуміє статті та інструкції. У розмові іноді плутає минулий час — це нормально для цього рівня.', en: 'He understands articles and instructions well. In speech he sometimes mixes up the past tense, which is normal at this level.' },
    skills: [['listen', 2], ['speak', 1], ['read', 3], ['write', 2]], done: 5,
    now: [{ uk: 'Минулий час у розповіді', en: 'Past tense in a story' }, { uk: 'Розповідати про плани', en: 'Talking about plans' }],
    home: { uk: 'Раз на день: 3 речення про те, що було вчора.', en: 'Once a day: three sentences about what happened yesterday.' },
    att: { uk: 'Відвідано 6 із 7 уроків за вересень і жовтень.', en: 'Attended 6 of 7 lessons in September and October.' },
  },
};

/* ---------- тексти ---------- */
const MON = { uk: ['січ.', 'лют.', 'бер.', 'квіт.', 'трав.', 'черв.', 'лип.', 'серп.', 'вер.', 'жовт.', 'лист.', 'груд.'], en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] };
const DAYS = { uk: ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'], en: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] };
const DAYF = { uk: ['неділя', 'понеділок', 'вівторок', 'середа', 'четвер', 'пʼятниця', 'субота'], en: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'] };
const TX = {
  uk: {
    tzLabel: 'Час', warsaw: 'Варшава', kyiv: 'Київ',
    nav: { schedule: 'Розклад', consents: 'Згоди', progress: 'Прогрес', messages: 'Повідомлення', data: 'Дані' },
    navAria: 'Розділи кабінету', unreadAria: n => `${n} непрочитаних`,
    hi: 'Добрий день! ', h1a: 'Тут усе про навчання ', h1b: 'ваших дітей',
    sub: 'Оберіть дитину — розклад, згоди, прогрес і повідомлення нижче зміняться.',
    pick: 'Оберіть дитину', picked: 'Обрано', nextLess: 'Найближчий урок',
    s1: 'Розклад на тиждень', s1l: 'Понеділок, 19 жовтня — неділя, 25 жовтня. Час подано і за Варшавою, і за Києвом.',
    today: 'Сьогодні', none: 'Занять немає', noNext: 'Найближчих уроків немає', noNextM: 'Усі уроки цього тижня вже пройшли або скасовані.',
    toStart: 'до початку уроку', dH: 'год', dD: 'д', min: 'хв', teacher: 'Викладач',
    st: { booked: 'Записано', passed: 'Пройшов', cancelled: 'Скасовано', paused: 'На паузі' },
    byParent: 'Скасовано вами', byTeacher: 'Скасував викладач', attn: 'Потрібна ваша увага', readMsg: 'Читати повідомлення',
    noRec: 'Без запису уроку', rec: 'Урок записується',
    pausedB: 'Участь в уроках вимкнена.', pausedT: ' Найближчі уроки стоять на паузі, доки ви не повернете згоду нижче.',
    dataB: 'Згоди на обробку даних немає.', dataT: ' Ми не можемо проводити навчання, доки ви не повернете її нижче.',
    s2: 'Згоди', s2l: 'Тут згоди, які ви даєте за дитину. Це рішення можна змінити пізніше.',
    law: 'Дитині менше 16 років, тому рішення про згоди ухвалює батько чи мати.', draft: 'Чернетка тексту, його ще перевірить юрист.', draftTag: 'Чернетка',
    cons: {
      data: { t: 'Дані для навчання', d: 'Імʼя, вік, розклад і результати навчання потрібні, щоб проводити уроки.' },
      part: { t: 'Участь\u00A0в\u00A0уроках', d: 'Дитина підключається до відеоуроків із викладачем.' },
      rec: { t: 'Записи уроків', d: 'Урок записується, щоб ви могли його переглянути. За замовчуванням вимкнено.' },
    },
    contract: 'Підстава: договір про навчання', contractSince: 'Діє з', contractNote: 'Це не згода, а умова договору: без цих даних навчання неможливе. Копію або видалення можна попросити в розділі «Дані».', contractBtn: 'Розділ «Дані»',
    on: 'Увімкнено', off: 'Вимкнено', given: 'Надано', notGiven: 'Не надано', revokedOn: 'Відкликано',
    revoke: 'Відкликати', grant: 'Надати', swAria: (c) => `Згода: ${c}`,
    dlgT: c => `Відкликати згоду «${c}»?`, dlgB: n => `Ви відкликаєте згоду від імені ${n}. Це рішення можна змінити пізніше.`,
    dlgL: { data: ['Ми припинимо обробляти дані дитини.', 'Навчання стане неможливим, доступ буде призупинено.', 'Дані можна видалити окремо в розділі «Дані».'], part: ['Дитина не зможе підключатися до уроків.', 'Найближчі уроки отримають статус «На паузі».', 'Дати згоду знову можна в цьому розділі.'], rec: ['Нові уроки не записуватимуться.', 'Що буде з уже наявними записами, напишемо в умовах (чернетка, перевірить юрист).', 'Дати згоду знову можна в цьому розділі.'] },
    keep: 'Залишити як є', go: 'Відкликати', pauseList: 'Стануть на паузу:',
    revokedSay: 'Згоду відкликано. Налаштування збережено.',
    s3: 'Прогрес', s3l: 'Простими словами, без балів і рейтингів.',
    pLevel: 'Рівень', pSkills: 'Що вже виходить', pPath: 'Шлях рівня', pNow: 'Над чим працюємо', pHome: 'Що можна вдома',
    sk: { listen: 'Розуміє на слух', speak: 'Говорить', read: 'Читає', write: 'Пише' },
    lv: ['', 'Потрібна практика', 'Добре йде', 'Упевнено'],
    pathT: n => `Пройдено ${n} із 10 тем цього рівня.`, attL: 'Відвідуваність',
    s4: 'Повідомлення', s4l: 'Пише викладач — лише вам. Відповісти може тільки батько чи мати; дитині викладач напряму не пише.',
    from: 'Від викладача', you: 'Ви', newB: 'Нове', markRead: 'Позначити прочитаним', imp: 'Важливо',
    cLabel: n => `Написати викладачу (${n})`, cHint: 'Повідомлення бачите лише ви та викладач.', cPh: 'Ваше повідомлення…', send: 'Надіслати', sent: 'Надіслано викладачу (демо).', empty: 'Спочатку напишіть кілька слів.',
    s5: 'Експорт і видалення даних дитини', s5l: 'Це макет: кнопки ще нічого не роблять.',
    exT: n => `Отримати копію даних: ${n}`, exD: 'Файл зі згодами, розкладом, прогресом і повідомленнями.', exB: 'Запросити експорт',
    deT: n => `Видалити дані: ${n}`, deD: 'Ми видалимо дані дитини та її записи. Дію не можна скасувати.', deB: 'Запросити видалення',
    stubEx: 'Заглушка: у справжньому кабінеті тут буде запит на експорт. Зараз нічого не надсилається.',
    stubDe: 'Заглушка: у справжньому кабінеті тут буде підтвердження видалення. Зараз нічого не видаляється.',
    say: {
      attn: n => ['Є одна важлива річ', 'Викладач скасував урок. Загляньте в повідомлення.'], schedule: n => ['Усе гаразд', `${n}: найближчий урок уже в розкладі. Ми про все подбаємо.`], wait: n => ['Скоро урок!', `${n}: до початку менше години. Я вже готовий!`],
      consents: n => ['Рішення за вами', 'Тут вирішуєте ви. Я нікуди не поспішаю.'], progress: n => ['Є чому радіти!', `${n} просувається. Дивіться, що вже виходить.`],
      messages: n => ['Слухаю', 'Тут пише викладач — лише вам. Відповісти можете тільки ви.'], data: n => ['Ваші дані', 'Можна попросити копію або видалення.'],
      dlg: n => ['Не поспішайте', 'Рішення за вами. Його можна змінити пізніше.'], sent: n => ['Надіслано!', 'Викладач отримає повідомлення й відповість вам.'], revoked: n => ['Згоду відкликано', 'Налаштування збережено. Дати знову можна в цьому розділі.'], kid: n => [`Дивимось: ${n}`, 'Усе нижче — про цю дитину.'],
    },
  },
  en: {
    tzLabel: 'Time', warsaw: 'Warsaw', kyiv: 'Kyiv',
    nav: { schedule: 'Schedule', consents: 'Consents', progress: 'Progress', messages: 'Messages', data: 'Data' },
    navAria: 'Dashboard sections', unreadAria: n => `${n} unread`,
    hi: 'Good afternoon! ', h1a: 'Everything about the learning of ', h1b: 'your children',
    sub: 'Pick a child — the schedule, consents, progress and messages below will change.',
    pick: 'Choose a child', picked: 'Selected', nextLess: 'Next lesson',
    s1: 'Schedule for the week', s1l: 'Monday, 19 October — Sunday, 25 October. Times are shown in Warsaw and in Kyiv.',
    today: 'Today', none: 'No lessons', noNext: 'No upcoming lessons', noNextM: 'All lessons this week are done or cancelled.',
    toStart: 'until the lesson starts', dH: 'h', dD: 'd', min: 'min', teacher: 'Teacher',
    st: { booked: 'Booked', passed: 'Done', cancelled: 'Cancelled', paused: 'Paused' },
    byParent: 'Cancelled by you', byTeacher: 'Cancelled by the teacher', attn: 'Needs your attention', readMsg: 'Read the message',
    noRec: 'Lesson is not recorded', rec: 'Lesson is recorded',
    pausedB: 'Lesson participation is off.', pausedT: ' Upcoming lessons are paused until you turn the consent back on below.',
    dataB: 'Data processing consent is off.', dataT: ' We cannot teach until you turn it back on below.',
    s2: 'Consents', s2l: 'These are consents you give for your child. You can change the decision later.',
    law: 'Your child is under 16, so a parent decides about consents.', draft: 'Draft text, a lawyer will still review it.', draftTag: 'Draft',
    cons: {
      data: { t: 'Data for teaching', d: 'Name, age, schedule and learning results are needed to run the lessons.' },
      part: { t: 'Lesson participation', d: 'The child joins video lessons with a teacher.' },
      rec: { t: 'Lesson recordings', d: 'A lesson is recorded so you can watch it later. Off by default.' },
    },
    contract: 'Basis: tuition contract', contractSince: 'In force since', contractNote: 'This is not a consent but a term of the contract: teaching is impossible without this data. You can ask for a copy or deletion in the “Data” section.', contractBtn: '“Data” section',
    on: 'On', off: 'Off', given: 'Given', notGiven: 'Not given', revokedOn: 'Withdrawn',
    revoke: 'Withdraw', grant: 'Give', swAria: c => `Consent: ${c}`,
    dlgT: c => `Withdraw consent “${c}”?`, dlgB: n => `You are withdrawing consent for ${n}. You can change this decision later.`,
    dlgL: { data: ['We will stop processing the child’s data.', 'Learning becomes impossible; access will be paused.', 'Data can be deleted separately in the “Data” section.'], part: ['The child will not be able to join lessons.', 'Upcoming lessons get the status “Paused”.', 'You can give consent again in this section.'], rec: ['New lessons will not be recorded.', 'What happens to existing recordings will be set out in the terms (draft, a lawyer will review).', 'You can give consent again in this section.'] },
    keep: 'Keep as is', go: 'Withdraw', pauseList: 'Will be paused:',
    s3: 'Progress', s3l: 'In plain words — no points, no rankings.',
    pLevel: 'Level', pSkills: 'What already works', pPath: 'Level path', pNow: 'What we are working on', pHome: 'What to try at home',
    sk: { listen: 'Understands by ear', speak: 'Speaks', read: 'Reads', write: 'Writes' },
    lv: ['', 'Needs practice', 'Going well', 'Confident'],
    pathT: n => `${n} of 10 topics of this level covered.`, attL: 'Attendance',
    s4: 'Messages', s4l: 'The teacher writes to you only. Only a parent can reply; the teacher does not write to the child directly.',
    from: 'From the teacher', you: 'You', newB: 'New', markRead: 'Mark as read', imp: 'Important',
    cLabel: n => `Write to the teacher (${n})`, cHint: 'Only you and the teacher see this message.', cPh: 'Your message…', send: 'Send', sent: 'Sent to the teacher (demo).', empty: 'Please write a few words first.',
    s5: 'Export and delete the child’s data', s5l: 'This is a mock-up: the buttons do nothing yet.',
    exT: n => `Get a copy of data: ${n}`, exD: 'A file with consents, schedule, progress and messages.', exB: 'Request export',
    deT: n => `Delete data: ${n}`, deD: 'We will delete the child’s data and recordings. This cannot be undone.', deB: 'Request deletion',
    stubEx: 'Placeholder: the real dashboard will send an export request here. Nothing is sent now.',
    stubDe: 'Placeholder: the real dashboard will ask you to confirm deletion here. Nothing is deleted now.',
    say: {
      attn: n => ['One thing matters', 'The teacher cancelled a lesson. Please check messages.'], schedule: n => ['All is well', `${n}: the next lesson is already in the schedule. We have it covered.`], wait: n => ['Class soon!', `${n}: under an hour to go. I am ready!`],
      consents: n => ['Your decision', 'It is up to you. I am in no hurry.'], progress: n => ['Something to smile about!', `${n} is moving forward. See what already works.`],
      messages: n => ['Listening', 'The teacher writes to you only. Only you can reply.'], data: n => ['Your data is yours', 'Take a copy or ask for deletion.'],
      dlg: n => ['Take your time', 'The decision is yours. You can change it later.'], sent: n => ['Sent!', 'The teacher will get the message and reply to you.'], revoked: n => ['Consent withdrawn', 'Settings saved. You can turn it back on at any time.'], kid: n => [`Looking at: ${n}`, 'Everything below is about this child.'],
    },
  },
};
const t = () => TX[state.lang];
const kn = (k = state.kid) => KIDS[k].name[state.lang];

/* ---------- час ---------- */
const p2 = n => String(n).padStart(2, '0');
const hm = ms => { const d = new Date(ms); return `${p2(d.getUTCHours())}:${p2(d.getUTCMinutes())}`; };
const hms = ms => { const d = new Date(ms); return `${p2(d.getUTCHours())}:${p2(d.getUTCMinutes())}:${p2(d.getUTCSeconds())}`; };
const dateS = (y, m, d) => state.lang === 'uk' ? `${d} ${MON.uk[m]} ${y}` : `${d} ${MON.en[m]} ${y}`;
const isoS = iso => { const [y, m, d] = iso.split('-').map(Number); return dateS(y, m - 1, d); };
const dayInfo = d => { const w = new Date(Date.UTC(2026, 9, d)).getUTCDay(); return { s: DAYS[state.lang][w], f: DAYF[state.lang][w] }; };
const startMs = l => wall(l.d, l.h, l.mi);
const KYIV = 3600000;
const times = ms => `<span>${hm(ms)} ${t().warsaw}</span> · <span>${hm(ms + KYIV)} ${t().kyiv}</span>`;

function nextLesson() {
  if (!state.consent[state.kid].part.on || !state.consent[state.kid].data.on) return null;
  const n = nowW();
  return LESSONS[state.kid].filter(l => l.st === 'booked' && startMs(l) > n).sort((a, b) => startMs(a) - startMs(b))[0] || null;
}
function cdText(ms) {
  const T = t(); let s = Math.max(0, Math.floor(ms / 1000));
  if (s >= 86400) { const d = Math.floor(s / 86400), h = Math.floor((s % 86400) / 3600); return `${d} ${T.dD} ${h} ${T.dH}`; }
  return `${p2(Math.floor(s / 3600))}:${p2(Math.floor(s % 3600 / 60))}:${p2(s % 60)}`;
}

/* ---------- розмітка ---------- */
const unreadCount = () => state.msgs[state.kid].filter(m => m.unread).length;
const SECS = ['schedule', 'consents', 'progress', 'messages', 'data'];
/* круг 7: вымышленные нейтральные портреты-иллюстрации (код, без фото и реальных людей) */
function portrait(kid) {
  const f = kid === 'olya'
    ? '<path d="M18 60C14 36 24 14 48 14s34 22 30 46c-3 14-6 20-8 24H26c-2-4-6-10-8-24Z" fill="#2E2036"/><path d="M14 96c2-14 14-20 34-20s32 6 34 20Z" fill="#7C6A8E"/><rect x="41" y="62" width="14" height="16" rx="6" fill="#B89888"/><ellipse cx="48" cy="46" rx="17" ry="20" fill="#C9A596"/><path d="M30 42c0-14 8-22 20-22 10 0 16 6 17 16-8-2-14-8-17-12-3 8-10 14-20 18Z" fill="#2E2036"/><circle cx="41.5" cy="47" r="1.8" fill="#3A2A3A"/><circle cx="54.5" cy="47" r="1.8" fill="#3A2A3A"/><path d="M43 58h10" stroke="#8A6A66" stroke-width="2" stroke-linecap="round" fill="none"/>'
    : '<path d="M14 96c2-14 14-20 34-20s32 6 34 20Z" fill="#5E6F8E"/><rect x="41" y="62" width="14" height="16" rx="6" fill="#B08C7C"/><ellipse cx="48" cy="46" rx="17" ry="20" fill="#C2A090"/><path d="M30 44c-3-18 6-28 18-28s22 8 18 28c-3-8-6-12-10-14-8 3-18 4-26 14Z" fill="#3A2A3A"/><path d="M36 61c4 5 20 5 24 0-2 8-6 11-12 11s-10-3-12-11Z" fill="#3A2A3A" opacity=".55"/><circle cx="41.5" cy="47" r="1.8" fill="#3A2A3A"/><circle cx="54.5" cy="47" r="1.8" fill="#3A2A3A"/><path d="M43 57h10" stroke="#7A5A56" stroke-width="2" stroke-linecap="round" fill="none"/>';
  return `<svg class="t-photo" viewBox="0 0 96 96" aria-hidden="true" focusable="false"><defs><clipPath id="pc-${kid}"><circle cx="48" cy="48" r="48"/></clipPath><radialGradient id="pg-${kid}" cx="0" cy=".9" r="1"><stop offset="0" stop-color="#FF9A5C" stop-opacity=".42"/><stop offset=".6" stop-color="#FF9A5C" stop-opacity=".08"/><stop offset="1" stop-color="#FF9A5C" stop-opacity="0"/></radialGradient></defs><g clip-path="url(#pc-${kid})"><rect width="96" height="96" fill="#4A3552"/>${f}<rect width="96" height="96" fill="url(#pg-${kid})"/></g></svg>`;
}
const NAVI = { schedule: I.cal, consents: I.shield, progress: I.grow, messages: I.chat, data: I.box };

function renderNav() {
  const T = t(); const u = unreadCount();
  $('#nav').setAttribute('aria-label', T.navAria);
  $('#nav').innerHTML = SECS.map(id => {
    const cur = state.section === id ? ' aria-current="true"' : '';
    const bad = id === 'messages' && u ? `<span class="n-badge" aria-label="${esc(T.unreadAria(u))}">${u}</span>` : '';
    return `<a href="#${id}" data-sec="${id}"${cur}>${NAVI[id](24)}<span>${T.nav[id]}</span>${bad}</a>`;
  }).join('');
}
function renderTz() {
  const T = t(); const n = nowW();
  $('#tz').innerHTML = `${I.globe(20)}<span><b>${T.warsaw}</b> ${hm(n)}</span><span><b>${T.kyiv}</b> ${hm(n + KYIV)}</span>`;
}
function heroNext() {
  const T = t(), K = KIDS[state.kid], nl = nextLesson(), c = state.consent[state.kid];
  if (nl) {
    return `<div class="next" id="nextCard"><div class="next-main"><div class="eyebrow">${T.nextLess} · ${kn()}</div><h1 class="next-title">${esc(nl.topic[state.lang])}</h1><div class="next-meta"><b>${nl.d === TODAY.d ? T.today : dayInfo(nl.d).f}, ${nl.d} ${MON[state.lang][9]}</b></div><div class="next-meta">${times(startMs(nl))} · 45 ${T.min}</div>
      <div class="teacher"><span class="t-av" aria-hidden="true">${portrait(state.kid)}</span><span><span class="t-l">${T.teacher}</span><span class="t-n">${K.teacher[state.lang]}</span></span></div></div>
      <div class="count"><time id="cd">${cdText(startMs(nl) - nowW())}</time><span>${T.toStart}</span></div></div>`;
  }
  const why = !c.data.on ? T.dataB + T.dataT : (!c.part.on ? T.pausedB + T.pausedT : T.noNextM);
  return `<div class="next none" id="nextCard"><div class="next-main"><div class="eyebrow">${T.nextLess} · ${kn()}</div><h1 class="next-title">${T.noNext}</h1><div class="next-meta">${why}</div></div></div>`;
}
function hello() {
  const T = t();
  const kids = Object.keys(KIDS).map(k => {
    const K = KIDS[k], on = state.kid === k;
    return `<button type="button" class="kid" data-kid="${k}" data-fid="kid-${k}" aria-pressed="${on}"><span class="av" aria-hidden="true">${K.letter[state.lang]}</span><span><span class="kid-n">${K.name[state.lang]}</span><span class="kid-m">${K.ageT[state.lang]} · ${K.level}</span></span></button>`;
  }).join('');
  return `<section class="hello" aria-label="${T.pick}"><div class="kids" role="group" aria-label="${T.pick}">${kids}</div>${heroNext()}</section>`;
}
function secHead(n, id, title, lead) {
  return `<div class="sec-h"><span class="sec-n" aria-hidden="true">0${n}</span><h2 class="sec-t" id="h-${id}">${title}</h2></div><p class="sec-lead">${lead}</p>`;
}
function scheduleSec() {
  const T = t(), c = state.consent[state.kid], nl = nextLesson(), K = KIDS[state.kid];
  const nextHtml = '';
  const bans = [];
  if (!c.data.on) bans.push(`<div class="banner" role="note">${I.warn(26)}<div><b>${T.dataB}</b>${T.dataT}</div></div>`);
  else if (!c.part.on) bans.push(`<div class="banner" role="note">${I.warn(26)}<div><b>${T.pausedB}</b>${T.pausedT}</div></div>`);
  const paused = !c.part.on || !c.data.on;
  const days = [];
  for (let d = 19; d <= 25; d++) {
    const ls = LESSONS[state.kid].filter(l => l.d === d), di = dayInfo(d), today = d === TODAY.d;
    const lab = `<div class="d-name">${di.s} ${d}${today ? `<small>${T.today}</small>` : `<small>${di.f}</small>`}</div>`;
    if (!ls.length) { days.push(`<li class="day empty${today ? ' today' : ''}">${lab}<span class="d-node" aria-hidden="true"></span><div class="d-body"><p class="d-none">${T.none}</p></div></li>`); continue; }
    const l = ls[0];
    let st = l.st; if (st === 'booked' && paused) st = 'paused';
    const ico = { booked: I.cal(16), passed: I.check(16), cancelled: I.cross(16), paused: I.pause(16) }[st];
    const nodeIco = { booked: I.cal(16), passed: I.check(16), cancelled: I.cross(16), paused: I.pause(16) }[st];
    const isNext = nl && l === nl;
    const rec = c.rec.on ? T.rec : T.noRec;
    let extra = `<span>${I.user(16)}${T.teacher}: ${K.teacher[state.lang]}</span>`;
    if (l.st === 'booked') extra += `<span>${I.mic(16)}${rec}</span>`;
    let attn = '';
    if (l.st === 'cancelled') {
      attn = l.by === 'teacher'
        ? `<div class="l-attn"><span class="pill pill-cancelled">${I.warn(16)}${T.attn}</span><span>${T.byTeacher}.</span><a href="#messages" data-sec="messages">${T.readMsg}</a></div>`
        : `<div class="l-attn"><span>${T.byParent}.</span></div>`;
    }
    days.push(`<li class="day s-${l.st === 'booked' && paused ? 'booked' : l.st}${today ? ' today' : ''}">${lab}<span class="d-node" aria-hidden="true">${nodeIco}</span><div class="d-body"><div class="lesson${isNext ? ' is-next' : ''}"><div><div class="l-t">${esc(l.topic[state.lang])}</div><div class="l-m">${times(startMs(l))}</div></div><span class="pill pill-${st === 'paused' ? 'paused' : l.st}">${ico}${T.st[st]}</span>${l.st === 'cancelled' ? attn : `<div class="l-x">${extra}</div>`}</div></div></li>`);
  }
  return `<section class="sec" id="schedule" data-s="schedule" aria-labelledby="h-schedule">${secHead(1, 'schedule', T.s1, T.s1l)}${nextHtml}${bans.join('')}<ol class="week">${days.join('')}</ol></section>`;
}
function consentsSec() {
  const T = t(), n = kn();
  const rows = [...CONS.filter(k => k !== 'data'), 'data'].map(k => {
    const c = state.consent[state.kid][k], D = T.cons[k];
    if (k === 'data') {   // основание обработки для обучения = договор, а не согласие (GDPR ст. 7(4)); без переключателя
      return `<li class="cons contract"><div><h3 class="c-t">${D.t}</h3><p class="c-d">${D.d}</p><div class="c-s"><span class="stl con"><i aria-hidden="true"></i>${T.contract}</span><span class="c-date">${T.contractSince}: ${isoS(c.date)}</span></div><p class="c-note">${T.contractNote}</p></div><div class="c-ctl"><button type="button" class="btn-eq btn-sm" data-sec="data" data-fid="cd-data">${T.contractBtn}</button></div></li>`;
    }
    const status = c.on
      ? `<span class="stl on"><i aria-hidden="true"></i>${T.given}</span><span class="c-date">${isoS(c.date)}</span>`
      : `<span class="stl off"><i aria-hidden="true"></i>${c.revoked ? T.revokedOn : T.notGiven}</span>${c.revoked ? `<span class="c-date">${isoS(c.revoked)}</span>` : ''}`;
    const btn = c.on
      ? `<button type="button" class="btn-eq btn-sm" data-revoke="${k}" data-fid="rv-${k}">${I.cross(18)}${T.revoke}</button>`
      : `<button type="button" class="btn-eq btn-sm" data-grant="${k}" data-fid="gr-${k}">${I.check(18)}${T.grant}</button>`;
    return `<li class="cons ${c.on ? 'on' : 'off'}"><div><h3 class="c-t">${D.t}</h3><p class="c-d">${D.d}</p><div class="c-s">${status}</div></div><div class="c-ctl">${btn}</div></li>`;
  }).join('');
  return `<section class="sec" id="consents" data-s="consents" aria-labelledby="h-consents">${secHead(2, 'consents', `${T.s2} · ${n}`, T.s2l)}<div class="law">${I.info(24)}<div><p>${T.law}</p><p class="draft"><span class="draft-tag">${T.draftTag}</span> ${T.draft}</p></div></div><ul class="consents">${rows}</ul></section>`;
}
function progressSec() {
  const T = t(), P = PROG[state.kid], K = KIDS[state.kid], l = state.lang;
  const sk = P.skills.map(([k, v]) => `<li class="skill"><b>${T.sk[k]}</b><span class="lvl"><span class="bars" aria-hidden="true">${[1, 2, 3].map(i => `<i class="${i <= v ? 'f' : ''}"></i>`).join('')}</span>${T.lv[v]}</span></li>`).join('');
  const track = Array.from({ length: 10 }, (_, i) => `<i class="${i < P.done ? 'f' : ''}"></i>`).join('');
  return `<section class="sec" id="progress" data-s="progress" aria-labelledby="h-progress">${secHead(3, 'progress', `${T.s3} · ${kn()}`, T.s3l)}<article class="paper"><h3>${esc(P.title[l])}</h3><p class="p-lead">${esc(P.lead[l])}</p>
  <div class="p-grid"><div><h4 class="p-h">${T.pSkills}</h4><ul class="skills">${sk}</ul></div>
  <div><h4 class="p-h">${T.pLevel} ${K.level}</h4><div class="path"><div class="track" aria-hidden="true">${track}</div><p>${T.pathT(P.done)}</p></div>
  <h4 class="p-h" style="margin-top:22px">${T.pNow}</h4><ul class="p-list">${P.now.map(x => `<li>${I.star(18)}<span>${esc(x[l])}</span></li>`).join('')}</ul></div></div>
  <p class="p-foot"><b>${T.pHome}:</b> ${esc(P.home[l])}<br><b>${T.attL}:</b> ${esc(P.att[l])}</p></article></section>`;
}
function messagesSec() {
  const T = t(), K = KIDS[state.kid], l = state.lang;
  const th = state.msgs[state.kid].map((m, i) => {
    const date = m.date || `${m.d} ${MON[l][9]}`;
    const body = typeof m.text === 'string' ? m.text : m.text[l];
    if (m.me) return `<li class="msg me"><div class="msg-h">${T.you} <time>${date}</time></div><p>${esc(body)}</p></li>`;
    const nw = m.unread ? `<span class="msg-new">${I.dot(12)}${T.newB}</span>` : '';
    const imp = m.important ? `<span class="pill pill-cancelled">${I.warn(16)}${T.imp}</span>` : '';
    const rd = m.unread ? `<button type="button" class="btn-line btn-sm" data-read="${i}" data-fid="rd-${i}">${I.check(18)}${T.markRead}</button>` : '';
    return `<li class="msg${m.unread ? ' unread' : ''}"><div class="msg-h">${T.from}: ${K.teacher[l]} <time>${date}</time>${nw}${imp}</div><p>${esc(body)}</p>${rd}</li>`;
  }).join('');
  return `<section class="sec" id="messages" data-s="messages" aria-labelledby="h-messages">${secHead(4, 'messages', T.s4, T.s4l)}<ul class="thread">${th}</ul>
  <form class="compose" id="compose"><label for="msgText">${T.cLabel(K.teacher[l])}</label><p>${T.cHint}</p><textarea id="msgText" placeholder="${T.cPh}"></textarea><div class="row"><button type="submit" class="btn-main">${I.chat(20)}${T.send}</button><span class="stat" id="msgStat" role="status"></span></div></form></section>`;
}
function dataSec() {
  const T = t(), n = kn();
  return `<section class="sec" id="data" data-s="data" aria-labelledby="h-data">${secHead(5, 'data', T.s5, T.s5l)}<div class="data">
  <div class="dcard"><h3>${T.exT(n)}</h3><p>${T.exD}</p><button type="button" class="btn-main" data-stub="ex" data-fid="ex">${I.down(20)}${T.exB}</button></div>
  <div class="dcard del"><h3>${T.deT(n)}</h3><p>${T.deD}</p><button type="button" class="btn-danger" data-stub="de" data-fid="de">${I.trash(20)}${T.deB}</button></div></div>
  <div class="stub"><p class="stat" id="stubStat" role="status"></p></div></section>`;
}
function render(focusId) {
  document.documentElement.lang = state.lang;
  document.title = state.lang === 'uk' ? 'LUMOSCHOOL · Кабінет батьків' : 'LUMOSCHOOL · Parent dashboard';
  $$('.seg button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.lang === state.lang)));
  renderTz(); renderNav();
  $('#main').innerHTML = hello() + scheduleSec() + consentsSec() + progressSec() + messagesSec() + dataSec();
  applyEmo(); tick();
  if (focusId) { const el = $(`[data-fid="${focusId}"]`); if (el) el.focus({ preventScroll: true }); }
}

/* ---------- Люмо ---------- */
const EMO = { schedule: 'rest', consents: 'wait', progress: 'joy', messages: 'wait', data: 'rest' };
function curEmo() {
  if (state.dlg) return ['rest', 'dlg'];
  if (state.override) return state.override;
  if (state.section === 'schedule') {
    if (LESSONS[state.kid].some(l => l.st === 'cancelled' && l.by === 'teacher')) return ['wait', 'attn'];
    const nl = nextLesson();
    if (nl && startMs(nl) - nowW() < 3600000) return ['wait', 'wait'];
    return ['rest', 'schedule'];
  }
  return [EMO[state.section], state.section];
}
function applyEmo() {
  const [e, key] = curEmo(); const T = t();
  $('#page').dataset.emo = e;
  const [h, tx] = T.say[key](kn());
  if ($('#sayH').textContent !== h) $('#sayH').textContent = h;
  if ($('#sayT').textContent !== tx) $('#sayT').textContent = tx;
}
let ovTimer = 0;
function flash(emo, key, ms = 3200) { state.override = [emo, key]; applyEmo(); clearTimeout(ovTimer); ovTimer = setTimeout(() => { state.override = null; applyEmo(); }, ms); }

/* ---------- діалог ---------- */
let opener = null;
function openDlg(k) {
  const T = t(), D = T.cons[k];
  state.dlg = k; opener = document.activeElement;
  $('#dlgT').textContent = T.dlgT(D.t); $('#dlgB').textContent = T.dlgB(KIDS[state.kid].gen[state.lang]);
  const aff = k === 'part' ? LESSONS[state.kid].filter(l => l.st === 'booked' && startMs(l) > nowW()).map(l => `<span class="aff-i">${esc(l.topic[state.lang])} — <span class="nw">${dayInfo(l.d).s}, ${l.d} ${MON[state.lang][9]}, ${hm(startMs(l))}</span></span>`) : [];
  $('#dlgL').innerHTML = T.dlgL[k].map(x => `<li>${I.dot(14)}<span>${x}</span></li>`).join('') + (aff.length ? `<li class="aff">${I.pause(16)}<span><b>${T.pauseList}</b> ${aff.join('')}</span></li>` : '');
  $('#dlgKeep').textContent = T.keep; $('#dlgGo').textContent = T.go;
  if (!$('#dlgLumo').firstChild) { const c = $('#lumo').cloneNode(true); c.removeAttribute('id'); $('#dlgLumo').appendChild(c); }
  $('#scrim').hidden = false; applyEmo(); $('#dlg').setAttribute('tabindex', '-1'); $('#dlg').focus();
}
function closeDlg(go) {
  const k = state.dlg; state.dlg = null; $('#scrim').hidden = true;
  if (go && k) {
    const c = state.consent[state.kid][k]; c.on = false; c.date = null; c.revoked = `2026-10-21`;
    render(`gr-${k}`); flash('think', 'revoked', 4000);
  } else { applyEmo(); if (opener && document.contains(opener)) opener.focus(); }
}
document.addEventListener('keydown', e => {
  if (!state.dlg) return;
  if (e.key === 'Escape') { closeDlg(false); return; }
  if (e.key === 'Tab') {
    const f = [$('#dlgKeep'), $('#dlgGo')], i = f.indexOf(document.activeElement);
    e.preventDefault(); f[(i + (e.shiftKey ? -1 : 1) + 2) % 2].focus();
  }
});
$('#dlgKeep').addEventListener('click', () => closeDlg(false));
$('#dlgGo').addEventListener('click', () => closeDlg(true));
$('#scrim').addEventListener('click', e => { if (e.target.id === 'scrim') closeDlg(false); });

/* ---------- події ---------- */
document.addEventListener('click', e => {
  const q = s => e.target.closest(s);
  let el;
  if ((el = q('[data-lang]'))) { state.lang = el.dataset.lang; render(); return; }
  if ((el = q('[data-kid]'))) { if (state.kid !== el.dataset.kid) { state.kid = el.dataset.kid; render(`kid-${state.kid}`); flash('joy', 'kid', 1800); } return; }
  if ((el = q('[data-sec]'))) { e.preventDefault(); const s = $('#' + el.dataset.sec); if (s) { s.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' }); history.replaceState(null, '', '#' + el.dataset.sec); } return; }
  if ((el = q('[data-revoke]'))) { openDlg(el.dataset.revoke); return; }
  if ((el = q('[data-sw]'))) { const k = el.dataset.sw, c = state.consent[state.kid][k]; if (c.on) openDlg(k); else { c.on = true; c.date = '2026-10-21'; c.revoked = null; render(`sw-${k}`); } return; }
  if ((el = q('[data-grant]'))) { const k = el.dataset.grant, c = state.consent[state.kid][k]; c.on = true; c.date = '2026-10-21'; c.revoked = null; render(`rv-${k}`); return; }
  if ((el = q('[data-read]'))) { state.msgs[state.kid][+el.dataset.read].unread = false; render(); return; }
  if ((el = q('[data-stub]'))) { $('#stubStat').textContent = el.dataset.stub === 'ex' ? t().stubEx : t().stubDe; return; }
});
document.addEventListener('submit', e => {
  if (e.target.id !== 'compose') return;
  e.preventDefault(); const v = $('#msgText').value.trim();
  if (!v) { $('#msgStat').textContent = t().empty; return; }
  state.msgs[state.kid].push({ me: true, d: 21, text: v, date: `${TODAY.d} ${MON[state.lang][9]}, ${hm(nowW())}` });
  render(); $('#msgStat').textContent = t().sent; flash('joy', 'sent', 3000);
});

/* ---------- активний пункт навігації ---------- */
function spy() {
  const line = innerHeight * (innerWidth <= 820 ? .42 : .38);
  let cur = SECS[0];
  for (const id of SECS) { const el = $('#' + id); if (el && el.getBoundingClientRect().top <= line) cur = id; }
  if (cur !== state.section) {
    state.section = cur;
    $$('#nav a').forEach(a => { if (a.dataset.sec === cur) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
    const a = $(`#nav a[data-sec="${cur}"]`); const nv = $('#nav');
    if (a && nv.scrollWidth > nv.clientWidth) nv.scrollLeft = a.offsetLeft - 8;
    applyEmo();
  }
}
let raf = 0;
addEventListener('scroll', () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(spy); }, { passive: true });
addEventListener('resize', spy);

/* ---------- годинник ---------- */
let lastMin = -1;
function tick() {
  const n = nowW(), nl = nextLesson(), cd = $('#cd');
  if (cd && nl) cd.textContent = cdText(startMs(nl) - n);
  const mi = Math.floor(n / 60000);
  if (mi !== lastMin) { lastMin = mi; renderTz(); if (!state.override && !state.dlg) applyEmo(); }
}
setInterval(tick, 1000);

state.lang = (new URLSearchParams(location.search).get('lang') === 'en') ? 'en' : 'uk';
render(); spy();
})();

/* круг 6: единый источник света = Люмо; положение света берётся из реальной позиции Люмо */
(function () {
  const L = document.querySelector('.light'), box = document.querySelector('#lumoBox'); let q = 0;
  function place() { q = 0; const r = box.getBoundingClientRect(); if (!r.width) return; L.style.setProperty('--lx', (r.left + r.width / 2) + 'px'); L.style.setProperty('--ly', (r.top + r.height * .55) + 'px'); }
  const sched = () => { if (!q) q = requestAnimationFrame(place); };
  addEventListener('scroll', sched, { passive: true }); addEventListener('resize', sched); place(); setTimeout(place, 300); setTimeout(place, 1000);
})();
