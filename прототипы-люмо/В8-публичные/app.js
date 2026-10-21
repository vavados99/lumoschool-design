/* LUMOSCHOOL · В8 (ч.1) · «Програми» + «Запис на пробний урок». Усі дані вигадані. Нічого не надсилається і не зберігається
   (ні fetch, ні storage, ні cookie): стан живе лише в пам'яті сторінки. Без зовнішніх запитів. */
(() => {
  'use strict';
  const T = {
    uk: {
      title: ['LUMOSCHOOL · Програми', 'LUMOSCHOOL · Запис на пробний урок'],
      skip: 'До змісту', tabs: ['Програми', 'Пробний урок'],
      eyebrow: 'Онлайн-школа англійської · Варшава і&nbsp;Київ',
      h1: 'Англійська, яку хочеться говорити', lead: 'Невеликі групи або один на один. Пробний урок 25 хвилин: познайомимось, визначимо рівень і підберемо програму.',
      cta: 'Записатись на пробний урок', ctaSub: 'Безкоштовно · без зобов’язань', see: 'Дивитись програми',
      progH: 'Програми', progLead: 'Обирайте за віком і метою. Рівні від A1 до C1, урок 55 хвилин.',
      demo: 'Усі ціни та дані на цій сторінці — приклад, вигадані для макета.',
      example: 'приклад', per: 'за урок', from: 'від',
      fGroup: 'Група', fInd: 'Індивідуально', fTeam: 'Команда',
      choose: 'Обрати', chosen: 'Обрано', pick: 'Обрано програму:', pickNone: 'Оберіть програму або запишіться без вибору',
      goTrial: 'Записатись на пробний', fmtN: n => `до ${n} осіб`,
      none: 'немає',
      stepOf: (a, b) => `Крок ${a} з ${b}`, steps: { who: 'Хто навчається', goal: 'Мета і рівень', time: 'Зручний час', consent: 'Згода батьків' },
      trialH: 'Запис на пробний урок', trialLead: 'Кілька коротких кроків. Нічого не надсилається: це макет.',
      back: 'Назад', next: 'Далі', send: 'Надіслати заявку', toProg: 'До програм',
      who: 'Хто навчатиметься?', adult: 'Дорослий', child: 'Дитина або підліток',
      nameA: 'Ваше ім’я', nameC: 'Ім’я учня', age: 'Вік учня', ageHint: 'Від 5 до 17 років',
      goalQ: 'Для чого вам англійська?', goals: ['Говорити вільно', 'Іспит', 'Робота', 'Школа', 'Подорожі'],
      levelQ: 'Ваш рівень зараз', levels: ['Не знаю', 'A1', 'A2', 'B1', 'B2', 'C1'], levelHint: 'Не страшно, якщо не знаєте: визначимо на уроці.',
      progQ: 'Програма', progAny: 'Допоможіть обрати',
      tzQ: 'Часовий пояс', tz: ['Варшава', 'Київ'], tzNote: 'Київ на годину попереду Варшави. Час у списку змінюється разом із поясом.',
      slotsQ: 'Оберіть зручні слоти (можна кілька)', week: 'Найближчий тиждень',
      emailA: 'Email для підтвердження', emailHint: 'anna.example@example.com',
      cH: 'Потрібна згода батьків', cText: 'Учням до 16 років ми проводимо пробний урок лише за згодою батька, матері або законного опікуна. Ми попросимо лише email дорослого, щоб надіслати підтвердження й посилання на урок. Дані дитини — ім’я та вік — потрібні тільки для підбору групи.',
      cMake: 'Батьківський email', cMakeHint: 'parent.example@example.com', cCheck: 'Я батько, мати або законний опікун і погоджуюсь на пробний урок для дитини.',
      cNote: 'У цьому макеті нічого не надсилається і не зберігається.',
      errTitle: n => n === 1 ? 'Є одне поле, яке треба виправити' : `Є поля, які треба виправити: ${n}`,
      e: { name: 'Вкажіть ім’я', age: 'Вкажіть вік від 5 до 17', goal: 'Оберіть мету', level: 'Оберіть рівень', slots: 'Оберіть хоча б один слот',
        email: 'Вкажіть email у форматі name@example.com', consent: 'Потрібна ваша згода, щоб продовжити' },
      okH: 'Заявку прийнято (заглушка)', okText: 'Це макет: нічого не надіслано і не збережено. Ось що побачила б школа:',
      sum: { who: 'Учень', prog: 'Програма', goal: 'Мета', level: 'Рівень', time: 'Слоти', contact: 'Контакт' },
      again: 'Заповнити ще раз', years: n => `${n} р.`, tzShort: ['Варшава', 'Київ'],
      days: ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'], dayFmt: (w, d) => `${w} ${d}.10`,
      foot: 'LUMOSCHOOL · макет на вигаданих даних · ціни умовні', progShort: ''
    },
    en: {
      title: ['LUMOSCHOOL · Programs', 'LUMOSCHOOL · Book a trial lesson'],
      skip: 'Skip to content', tabs: ['Programs', 'Trial lesson'],
      eyebrow: 'Online English school · Warsaw and&nbsp;Kyiv',
      h1: 'English you actually want to speak', lead: 'Small groups or one to one. A 25-minute trial lesson: we meet, find your level and match a program.',
      cta: 'Book a trial lesson', ctaSub: 'Free · no commitment', see: 'See programs',
      progH: 'Programs', progLead: 'Pick by age and goal. Levels A1 to C1, 55-minute lessons.',
      demo: 'All prices and data on this page are examples made up for the mockup.',
      example: 'example', per: 'per lesson', from: 'from',
      fGroup: 'Group', fInd: 'One to one', fTeam: 'Team',
      choose: 'Choose', chosen: 'Chosen', pick: 'Program chosen:', pickNone: 'Pick a program or book without one',
      goTrial: 'Book a trial', fmtN: n => `up to ${n} people`,
      none: 'none',
      stepOf: (a, b) => `Step ${a} of ${b}`, steps: { who: 'Who is learning', goal: 'Goal and level', time: 'Convenient time', consent: 'Parent consent' },
      trialH: 'Book a trial lesson', trialLead: 'A few short steps. Nothing is sent: this is a mockup.',
      back: 'Back', next: 'Next', send: 'Send request', toProg: 'Back to programs',
      who: 'Who will be learning?', adult: 'Adult', child: 'Child or teen',
      nameA: 'Your name', nameC: 'Student’s name', age: 'Student’s age', ageHint: 'From 5 to 17 years',
      goalQ: 'What do you need English for?', goals: ['Speak freely', 'An exam', 'Work', 'School', 'Travel'],
      levelQ: 'Your level now', levels: ['Not sure', 'A1', 'A2', 'B1', 'B2', 'C1'], levelHint: 'No worries if you don’t know: we’ll find out in the lesson.',
      progQ: 'Program', progAny: 'Help me choose',
      tzQ: 'Time zone', tz: ['Warsaw', 'Kyiv'], tzNote: 'Kyiv is one hour ahead of Warsaw. Times below change with the zone.',
      slotsQ: 'Pick convenient slots (several allowed)', week: 'Next week',
      emailA: 'Email for confirmation', emailHint: 'anna.example@example.com',
      cH: 'A parent’s consent is needed', cText: 'For students under 16 we run the trial lesson only with the consent of a parent or legal guardian. We ask only for the adult’s email, to send the confirmation and the lesson link. The child’s name and age are used only to choose a group.',
      cMake: 'Parent’s email', cMakeHint: 'parent.example@example.com', cCheck: 'I am the child’s parent or legal guardian and I agree to a trial lesson.',
      cNote: 'Nothing is sent or stored in this mockup.',
      errTitle: n => n === 1 ? 'One field needs fixing' : `${n} fields need fixing`,
      e: { name: 'Enter a name', age: 'Enter an age from 5 to 17', goal: 'Pick a goal', level: 'Pick a level', slots: 'Pick at least one slot',
        email: 'Enter an email like name@example.com', consent: 'Your consent is needed to continue' },
      okH: 'Request received (placeholder)', okText: 'This is a mockup: nothing was sent or saved. Here is what the school would see:',
      sum: { who: 'Student', prog: 'Program', goal: 'Goal', level: 'Level', time: 'Slots', contact: 'Contact' },
      again: 'Fill in again', years: n => `${n} y.o.`, tzShort: ['Warsaw', 'Kyiv'],
      days: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], dayFmt: (w, d) => `${w} ${d} Oct`,
      foot: 'LUMOSCHOOL · mockup on made-up data · prices are illustrative', progShort: ''
    }
  };
  // Вигадані програми. Ціни — за урок 55 хв, PLN і UAH (приклад).
  const PROGS = [
    { id: 'speak', age: { uk: 'Від 16 років', en: 'Ages 16+' }, lvl: 'A2 → C1',
      name: { uk: 'Розмовний', en: 'Speaking' }, d: { uk: 'Жива мова без підручникового присмаку: діалоги, ситуації, вимова.', en: 'Real speech without the textbook taste: dialogues, situations, pronunciation.' },
      fm: [['g', 6, 69, 690], ['i', 0, 139, 1390]] },
    { id: 'kids', age: { uk: 'Діти 7–12', en: 'Kids 7–12' }, lvl: 'A1 → A2',
      name: { uk: 'Англійська для дітей', en: 'English for kids' }, d: { uk: 'Короткі активності, історії і розмова. Урок без зубріння.', en: 'Short activities, stories and talking. A lesson without cramming.' },
      fm: [['g', 5, 55, 550], ['i', 0, 119, 1190]] },
    { id: 'teens', age: { uk: 'Підлітки 13–17', en: 'Teens 13–17' }, lvl: 'A2 → B2',
      name: { uk: 'Англійська для підлітків', en: 'English for teens' }, d: { uk: 'Теми, які цікаві самим підліткам, і підтримка шкільної програми.', en: 'Topics teens care about, plus support for the school curriculum.' },
      fm: [['g', 6, 59, 590], ['i', 0, 125, 1250]] },
    { id: 'exam', age: { uk: 'Від 14 років', en: 'Ages 14+' }, lvl: 'B1 → C1',
      name: { uk: 'Підготовка до іспитів', en: 'Exam preparation' }, d: { uk: 'Cambridge, IELTS, іспити в школі: пробні тести і розбір помилок.', en: 'Cambridge, IELTS, school exams: practice tests and error review.' },
      fm: [['g', 6, 79, 790], ['i', 0, 149, 1490]] },
    { id: 'biz', age: { uk: 'Дорослі', en: 'Adults' }, lvl: 'B1 → C1',
      name: { uk: 'Бізнес-англійська', en: 'Business English' }, d: { uk: 'Мітинги, листи, презентації і перемовини на матеріалі вашої роботи.', en: 'Meetings, emails, presentations and negotiations on your own work material.' },
      fm: [['t', 6, 99, 990], ['i', 0, 169, 1690]] }
  ];
  const DAYS = [20, 21, 22, 23, 24];       // вт–сб, жовтень 2026
  { const ord = ['kids', 'teens', 'speak', 'exam', 'biz']; PROGS.sort((a, b) => ord.indexOf(a.id) - ord.indexOf(b.id)); }
  const HOURS = [16, 17, 18, 19];           // час у Варшаві; у Києві +1
  const NUM = { pl: new Intl.NumberFormat('uk-UA') };

  const $ = (s, r = document) => r.querySelector(s);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const st = {
    lang: 'uk', view: 'programs', prog: null,
    step: 0, who: 'adult', name: '', age: '', goal: -1, level: -1, progSel: '', tz: 0, slots: [], email: '', pEmail: '', consent: false,
    errors: {}, done: false
  };
  const t = () => T[st.lang];
  const isU16 = () => st.who === 'child' && st.age !== '' && Number(st.age) < 16;
  const steps = () => ['who', 'goal', 'time'].concat(isU16() ? ['consent'] : []);
  const pname = id => { const p = PROGS.find(x => x.id === id); return p ? p.name[st.lang] : T[st.lang].progAny; };
  const hh = h => String(h).padStart(2, '0') + ':00';
  const slotLabel = (d, h) => { const w = new Date(2026, 9, d).getDay(); return { day: t().dayFmt(t().days[w], d), time: hh(h + st.tz) }; };

  function fmtRow(f, p) {
    const T_ = t(); const kind = f[0] === 'g' ? T_.fGroup : f[0] === 't' ? T_.fTeam : T_.fInd;
    const sub = f[1] ? T_.fmtN(f[1]) : '1 : 1';
    return `<li class="fm"><div class="fm-n"><b>${kind}</b><span>${sub}</span></div>
      <div class="fm-p"><span class="pr"><b>${f[2]}</b> PLN</span><span class="pr alt"><b>${NUM.pl.format(f[3])}</b> UAH</span></div></li>`;
  }
  function viewPrograms() {
    const T_ = t();
    $('#v-programs').innerHTML = `
      <div class="hero">
        <div class="hero-txt">
          <p class="eyebrow">${T_.eyebrow}</p>
          <h1 id="progH">${T_.h1}</h1>
          <p class="lead">${T_.lead}</p>
          <div class="cta-row"><button type="button" class="btn primary" data-go="trial">${T_.cta}</button><a class="link" href="#cards" id="seeLink">${T_.see} <span aria-hidden="true">↓</span></a></div>
          <p class="cta-sub">${T_.ctaSub}</p>
        </div>
        <figure class="flame" aria-hidden="true"><div class="halo"></div><img src="assets/lumo-v5r8-mark.svg" alt="" width="240" height="240"></figure>
      </div>
      <div class="sec-head" id="cards"><h2>${T_.progH}</h2><p>${T_.progLead}</p><p class="demo"><span class="tag">${T_.example}</span> ${T_.demo}</p></div>
      <ul class="cards" id="cardList">${PROGS.map(p => `
        <li class="card" data-id="${p.id}" data-sel="${st.prog === p.id}">
          <div class="card-top"><span class="age">${p.age[st.lang]}</span><span class="lv">${p.lvl}</span></div>
          <h3>${p.name[st.lang]}</h3>
          <p class="cd">${p.d[st.lang]}</p>
          <ul class="fms" aria-label="${T_.per}">${p.fm.map(f => fmtRow(f, p)).join('')}</ul>
          <p class="per">${T_.per} · 55 хв <span class="tag">${T_.example}</span></p>
          <button type="button" class="btn ghost pick" data-pick="${p.id}" aria-pressed="${st.prog === p.id}"><span class="ck" aria-hidden="true"></span>${st.prog === p.id ? T_.chosen : T_.choose}<span class="vh"> — ${p.name[st.lang]}</span></button>
        </li>`).join('')}
      </ul>
      <div class="dock" id="dock" ${st.prog ? '' : 'hidden'}>
        <p class="dock-t"><span>${T_.pick}</span> <b>${st.prog ? pname(st.prog) : ''}</b></p>
        <button type="button" class="btn primary" data-go="trial">${T_.goTrial}</button>
      </div>`;
    $('#v-programs .per').closest('ul') && document.querySelectorAll('#v-programs .per').forEach(e => { e.innerHTML = `${T_.per} · ${st.lang === 'uk' ? '55 хв' : '55 min'} <span class="tag">${T_.example}</span>`; });
    lightCards();
  }
  // Єдине джерело світла — Люмо: яскравість верхньої грані картки залежить від відстані до полум'я
  function lightCards() {
    const fl = $('#v-programs .flame'); if (!fl || $('#v-programs').hidden) return;
    const fr = fl.getBoundingClientRect(); const cx = fr.left + fr.width / 2 + scrollX, cy = fr.top + fr.height / 2 + scrollY;
    document.querySelectorAll('.card').forEach(c => {
      const r = c.getBoundingClientRect(); const x = r.left + r.width / 2 + scrollX, y = r.top + r.height / 2 + scrollY;
      const d = Math.hypot(x - cx, y - cy); const lit = Math.max(.25, 1 - d / 1500);
      c.style.setProperty('--lit', lit.toFixed(2));
      c.style.setProperty('--dx', Math.round(Math.max(-100, Math.min(200, (cx - r.left - scrollX) / r.width * 100))) + '%');
    });
  }

  /* ---------- Форма ---------- */
  function errBox(keys) {
    const n = keys.length; if (!n) return '';
    return `<div class="errsum" role="alert" id="errsum"><span class="ei" aria-hidden="true">!</span><div><b>${t().errTitle(n)}</b></div></div>`;
  }
  const fe = k => st.errors[k] ? `<p class="fe" id="fe-${k}"><span class="ei" aria-hidden="true">!</span>${t().e[k]}</p>` : '';
  const inv = k => st.errors[k] ? ' aria-invalid="true"' : '';
  const dsc = (k, hint) => ` aria-describedby="${[st.errors[k] ? 'fe-' + k : '', hint || ''].filter(Boolean).join(' ')}"`;

  function stepBody(key) {
    const T_ = t();
    if (key === 'who') return `
      <fieldset class="fs"><legend>${T_.who}</legend>
        <div class="choices two">
          <label class="ch"><input type="radio" name="who" value="adult" ${st.who === 'adult' ? 'checked' : ''}><span>${T_.adult}</span></label>
          <label class="ch"><input type="radio" name="who" value="child" ${st.who === 'child' ? 'checked' : ''}><span>${T_.child}</span></label>
        </div></fieldset>
      <div class="fld"><label for="name">${st.who === 'child' ? T_.nameC : T_.nameA}</label>
        <input id="name" type="text" autocomplete="off" value="${esc(st.name)}" placeholder="${st.who === 'child' ? 'Марко' : 'Анна'}"${inv('name')}${dsc('name')}>${fe('name')}</div>
      ${st.who === 'child' ? `<div class="fld sm"><label for="age">${T_.age}</label>
        <input id="age" type="number" inputmode="numeric" min="5" max="17" value="${esc(st.age)}" placeholder="11"${inv('age')}${dsc('age', 'ageh')}>
        <p class="hint" id="ageh">${T_.ageHint}</p>${fe('age')}</div>` : ''}`;
    if (key === 'goal') return `
      <fieldset class="fs"${inv('goal')}><legend>${T_.goalQ}</legend>
        <div class="choices wrap">${T_.goals.map((g, i) => `<label class="ch"><input type="radio" name="goal" value="${i}" ${st.goal === i ? 'checked' : ''}><span>${g}</span></label>`).join('')}</div>${fe('goal')}</fieldset>
      <fieldset class="fs"><legend>${T_.levelQ}</legend>
        <div class="choices wrap">${T_.levels.map((g, i) => `<label class="ch sq"><input type="radio" name="level" value="${i}" ${st.level === i ? 'checked' : ''}><span>${g}</span></label>`).join('')}</div>
        <p class="hint">${T_.levelHint}</p>${fe('level')}</fieldset>
      <div class="fld"><label for="progSel">${T_.progQ}</label>
        <select id="progSel"><option value="">${T_.progAny}</option>${PROGS.map(p => `<option value="${p.id}" ${st.progSel === p.id ? 'selected' : ''}>${p.name[st.lang]}</option>`).join('')}</select></div>`;
    if (key === 'time') return `
      <fieldset class="fs"><legend>${T_.tzQ}</legend>
        <div class="seg tzseg" role="group" id="tzSeg">${T_.tz.map((z, i) => `<button type="button" data-tz="${i}" aria-pressed="${st.tz === i}">${z}</button>`).join('')}</div>
        <p class="hint">${T_.tzNote}</p></fieldset>
      <fieldset class="fs"${inv('slots')}><legend>${T_.slotsQ}</legend>
        <div class="days">${DAYS.map(d => { const l0 = slotLabel(d, HOURS[0]); return `<div class="day"><span class="dn">${l0.day}</span><div class="slots">${HOURS.map(h => `
          <label class="slot"><input type="checkbox" value="${d}-${h}" ${st.slots.includes(d + '-' + h) ? 'checked' : ''}><span data-h="${h}">${hh(h + st.tz)}</span></label>`).join('')}</div></div>`; }).join('')}</div>${fe('slots')}</fieldset>
      ${st.who === 'adult' ? `<div class="fld"><label for="email">${T_.emailA}</label>
        <input id="email" type="email" autocomplete="off" value="${esc(st.email)}" placeholder="name@example.com"${inv('email')}${dsc('email', 'emh')}>
        <p class="hint" id="emh"><span class="tag">${T_.example}</span> ${T_.emailHint}</p>${fe('email')}</div>` : ''}`;
    if (key === 'consent') return `
      <div class="consent"><h3 id="cH">${T_.cH}</h3><p>${T_.cText}</p></div>
      <div class="fld"><label for="pEmail">${T_.cMake}</label>
        <input id="pEmail" type="email" autocomplete="off" value="${esc(st.pEmail)}" placeholder="parent@example.com"${inv('email')}${dsc('email', 'pemh')}>
        <p class="hint" id="pemh"><span class="tag">${T_.example}</span> ${T_.cMakeHint}</p>${fe('email')}</div>
      <label class="agree"><input type="checkbox" id="consent" ${st.consent ? 'checked' : ''}${inv('consent')}${dsc('consent')}><span class="bx" aria-hidden="true"></span><span>${T_.cCheck}</span></label>${fe('consent')}
      <p class="hint">${T_.cNote}</p>`;
    return '';
  }

  function viewTrial() {
    const T_ = t(); const el = $('#v-trial');
    if (st.done) return viewDone();
    const S = steps(); const key = S[st.step]; const n = S.length;
    const errKeys = Object.keys(st.errors);
    const last = st.step === n - 1;
    el.innerHTML = `
      <div class="trial">
        <aside class="side">
          <figure class="flame sm" aria-hidden="true"><div class="halo"></div><img src="assets/lumo-v5r8-mark.svg" alt="" width="120" height="120"></figure>
          <h1 id="trialH">${T_.trialH}</h1>
          <p class="lead">${T_.trialLead}</p>
          <ol class="rail" aria-label="${T_.stepOf(st.step + 1, n)}">${S.map((k, i) => `<li ${i === st.step ? 'aria-current="step"' : ''} data-s="${i < st.step ? 'done' : i === st.step ? 'now' : 'next'}"><span class="rn">${i < st.step ? '✓' : i + 1}</span><span>${T_.steps[k]}</span></li>`).join('')}</ol>
        </aside>
        <form class="formcard" id="trialForm" novalidate>
          <div class="prog" aria-hidden="true"><i style="width:${Math.round((st.step + 1) / n * 100)}%"></i></div>
          <p class="stepof" id="stepOf">${T_.stepOf(st.step + 1, n)} · ${T_.steps[key]}</p>
          <div id="errhost">${errBox(errKeys)}</div>
          <div class="stepbody" id="stepBody">${stepBody(key)}</div>
          <div class="actions">
            ${st.step > 0 ? `<button type="button" class="btn ghost" id="bBack">${T_.back}</button>` : '<span></span>'}
            <button type="submit" class="btn primary" id="bNext">${last ? T_.send : T_.next}</button>
          </div>
        </form>
      </div>`;
    $('#page').style.setProperty('--lum', (0.55 + 0.4 * st.step / Math.max(1, n - 1)).toFixed(2));
    bindForm();
  }
  function viewDone() {
    const T_ = t(); const s = st; const sl = s.slots.map(v => { const [d, h] = v.split('-').map(Number); const l = slotLabel(d, h); return `${l.day} ${l.time}`; });
    $('#v-trial').innerHTML = `
      <div class="trial done">
        <aside class="side"><figure class="flame sm" aria-hidden="true"><div class="halo"></div><img src="assets/lumo-v5r8-mark.svg" alt="" width="120" height="120"></figure></aside>
        <div class="formcard">
          <div class="prog" aria-hidden="true"><i style="width:100%"></i></div>
          <h1 id="trialH" tabindex="-1">${T_.okH}</h1>
          <p class="lead">${T_.okText}</p>
          <dl class="sum">
            <div><dt>${T_.sum.who}</dt><dd>${esc(s.name)}, ${s.who === 'child' ? T_.years(s.age) : T_.adult}</dd></div>
            <div><dt>${T_.sum.prog}</dt><dd>${esc(pname(s.progSel))}</dd></div>
            <div><dt>${T_.sum.goal}</dt><dd>${T_.goals[s.goal]}</dd></div>
            <div><dt>${T_.sum.level}</dt><dd>${T_.levels[s.level]}</dd></div>
            <div><dt>${T_.sum.time}</dt><dd>${sl.join(' · ')} (${T_.tzShort[s.tz]})</dd></div>
            <div><dt>${T_.sum.contact}</dt><dd>${esc(isU16() || s.who === 'child' ? (s.pEmail || '—') : (s.email || '—'))}</dd></div>
          </dl>
          <div class="actions"><button type="button" class="btn ghost" id="bAgain">${T_.again}</button><button type="button" class="btn primary" data-go="programs">${T_.toProg}</button></div>
        </div>
      </div>`;
    $('#page').style.setProperty('--lum', '1');
    $('#bAgain').onclick = () => { Object.assign(st, { step: 0, who: 'adult', name: '', age: '', goal: -1, level: -1, tz: 0, slots: [], email: '', pEmail: '', consent: false, errors: {}, done: false }); st.progSel = st.prog || ''; render(true); };
    const h = $('#trialH'); h && h.focus({ preventScroll: true });
  }

  function clearErr(k) { if (st.errors[k]) { delete st.errors[k]; const f = document.getElementById('fe-' + k); f && f.remove(); document.querySelectorAll('[aria-invalid]').forEach(x => x.removeAttribute('aria-invalid'));
    $('#errhost').innerHTML = errBox(Object.keys(st.errors)); } }
  function bindForm() {
    const f = $('#trialForm'); if (!f) return;
    f.onsubmit = e => { e.preventDefault(); next(); };
    const b = $('#bBack'); if (b) b.onclick = () => { st.step--; st.errors = {}; viewTrial(); focusStep(); };
    f.querySelectorAll('input[name=who]').forEach(i => i.onchange = () => { st.who = i.value; st.errors = {}; if (st.who === 'adult') st.age = ''; viewTrial(); const a = $('input[name=who]:checked'); a && a.focus(); });
    const nm = $('#name'); if (nm) nm.oninput = () => { st.name = nm.value; clearErr('name'); };
    const ag = $('#age'); if (ag) ag.oninput = () => { st.age = ag.value; clearErr('age'); };
    f.querySelectorAll('input[name=goal]').forEach(i => i.onchange = () => { st.goal = +i.value; clearErr('goal'); });
    f.querySelectorAll('input[name=level]').forEach(i => i.onchange = () => { st.level = +i.value; clearErr('level'); });
    const ps = $('#progSel'); if (ps) ps.onchange = () => { st.progSel = ps.value; };
    f.querySelectorAll('[data-tz]').forEach(x => x.onclick = () => { st.tz = +x.dataset.tz; f.querySelectorAll('[data-tz]').forEach(y => y.setAttribute('aria-pressed', y === x));
      f.querySelectorAll('.slot span').forEach(s => { s.textContent = hh(+s.dataset.h + st.tz); }); });
    f.querySelectorAll('.slot input').forEach(i => i.onchange = () => { st.slots = [...f.querySelectorAll('.slot input:checked')].map(x => x.value); clearErr('slots'); });
    const em = $('#email'); if (em) em.oninput = () => { st.email = em.value; clearErr('email'); };
    const pe = $('#pEmail'); if (pe) pe.oninput = () => { st.pEmail = pe.value; clearErr('email'); };
    const cs = $('#consent'); if (cs) cs.onchange = () => { st.consent = cs.checked; clearErr('consent'); };
  }
  const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  function validate(key) {
    const e = {};
    if (key === 'who') { if (!st.name.trim()) e.name = 1; if (st.who === 'child') { const a = Number(st.age); if (st.age === '' || !(a >= 5 && a <= 17) || !Number.isInteger(a)) e.age = 1; } }
    if (key === 'goal') { if (st.goal < 0) e.goal = 1; if (st.level < 0) e.level = 1; }
    if (key === 'time') { if (!st.slots.length) e.slots = 1; if (st.who === 'adult' && !EMAIL.test(st.email.trim())) e.email = 1; }
    if (key === 'consent') { if (!EMAIL.test(st.pEmail.trim())) e.email = 1; if (!st.consent) e.consent = 1; }
    return e;
  }
  const FIRST = { name: '#name', age: '#age', goal: 'input[name=goal]', level: 'input[name=level]', slots: '.slot input', email: '#email,#pEmail', consent: '#consent' };
  function next() {
    const S = steps(); const key = S[st.step]; st.errors = validate(key); const ks = Object.keys(st.errors);
    if (ks.length) { viewTrial(); const first = ['name', 'age', 'goal', 'level', 'slots', 'email', 'consent'].find(k => st.errors[k]); const el = first && $(FIRST[first]); el && el.focus({ preventScroll: false });
      const es = $('#errsum'); es && es.scrollIntoView && 0; return; }
    if (st.step === S.length - 1) { st.done = true; viewTrial(); scrollTo(0, 0); return; }
    st.step++; st.errors = {}; viewTrial(); focusStep();
  }
  function focusStep() { const s = $('#stepOf'); if (s) { s.setAttribute('tabindex', '-1'); s.focus({ preventScroll: true }); } scrollTo(0, 0); }

  /* ---------- Каркас ---------- */
  function renderChrome() {
    const T_ = t(); document.documentElement.lang = st.lang; document.title = T_.title[st.view === 'trial' ? 1 : 0];
    $('#skip').textContent = T_.skip; $('#foot').innerHTML = `<p>${T_.foot}</p>`;
    $('#tabs').innerHTML = ['programs', 'trial'].map((v, i) => `<a href="#${v}" ${st.view === v ? 'aria-current="page"' : ''}>${T_.tabs[i]}</a>`).join('');
    document.querySelectorAll('[data-lang]').forEach(b => b.setAttribute('aria-pressed', b.dataset.lang === st.lang));
  }
  function render(top) {
    $('#v-programs').hidden = st.view !== 'programs'; $('#v-trial').hidden = st.view !== 'trial';
    renderChrome();
    if (st.view === 'programs') { viewPrograms(); $('#page').style.setProperty('--lum', '.8'); } else { viewTrial(); }
    if (top) scrollTo(0, 0);
    document.getElementById('page').classList.add('ready'); document.documentElement.classList.add('ready');
  }
  function go(v) { if (v === 'trial' && st.view !== 'trial') { if (!st.progSel && st.prog) st.progSel = st.prog; else if (st.prog) st.progSel = st.prog; } st.view = v; if (location.hash !== '#' + v) history.pushState(null, '', '#' + v); render(true);
    const h = $(v === 'trial' ? '#trialH' : '#progH'); if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); } }

  document.addEventListener('click', e => {
    const g = e.target.closest('[data-go]'); if (g) { go(g.dataset.go); return; }
    const p = e.target.closest('[data-pick]'); if (p) { st.prog = st.prog === p.dataset.pick ? null : p.dataset.pick; const y = scrollY; viewPrograms(); scrollTo(0, y); const nb = $(`[data-pick="${p.dataset.pick}"]`); nb && nb.focus({ preventScroll: true }); return; }
    const l = e.target.closest('[data-lang]'); if (l) { st.lang = l.dataset.lang; const y = scrollY; const ae = document.activeElement && document.activeElement.id; render(false); scrollTo(0, y); l.focus({ preventScroll: true }); return; }
    const a = e.target.closest('a[href^="#"]'); if (a) { const v = a.getAttribute('href').slice(1);
      if (v === 'programs' || v === 'trial') { e.preventDefault(); go(v); } else if (v === 'cards') { e.preventDefault(); $('#cards').scrollIntoView({ behavior: 'auto' }); } else if (v === 'main') { e.preventDefault(); $('#main').focus(); } }
  });
  addEventListener('popstate', () => { st.view = location.hash === '#trial' ? 'trial' : 'programs'; render(true); });
  addEventListener('resize', () => lightCards());
  st.view = location.hash === '#trial' ? 'trial' : 'programs';
  if (location.search.includes('lang=en')) st.lang = 'en';
  render(false);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(lightCards);
  window.__lumo = { st, go, render };
})();
