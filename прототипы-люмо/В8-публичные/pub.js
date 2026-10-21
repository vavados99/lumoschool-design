/* LUMOSCHOOL · В8 ч.2 · «Викладачі», «Для батьків», «Вхід». Усі імена й дані вигадані; фото й контактів немає.
   Вхід імітується: нічого не надсилається і не зберігається (ні fetch, ні storage, ні cookie). Без зовнішніх запитів. */
(() => {
  'use strict';
  const PAGE = document.body.dataset.page;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let lang = location.search.includes('lang=en') ? 'en' : 'uk';
  const L = (u, e) => (lang === 'en' ? e : u);
  const q = () => (lang === 'en' ? '?lang=en' : '');
  const FLAME = '<figure class="flame mini" aria-hidden="true"><div class="halo"></div><img src="assets/lumo-v5r8-mark.svg" alt="" width="120" height="120"></figure>';

  /* ---------- каркас ---------- */
  const NAV = [['index.html', 'programs', 'Програми', 'Programs'], ['index.html#trial', 'trial', 'Пробний урок', 'Trial lesson'],
    ['teachers.html', 'teachers', 'Викладачі', 'Teachers'], ['parents.html', 'parents', 'Для батьків', 'For parents'], ['login.html', 'login', 'Вхід', 'Sign in']];
  const TITLE = { teachers: ['Викладачі', 'Teachers'], parents: ['Для батьків', 'For parents'], login: ['Вхід', 'Sign in'] };
  function chrome() {
    document.documentElement.lang = lang; document.title = 'LUMOSCHOOL · ' + L(...TITLE[PAGE]);
    $('#skip').textContent = L('До змісту', 'Skip to content');
    $('#brand').href = 'index.html' + q();
    $('#tabs').innerHTML = NAV.map(([h, id, u, e]) => {
      const href = h.includes('#') ? h.replace('#', q() + '#') : h + q();
      return `<a href="${href}" class="${id === 'login' ? 'login-tab' : ''}" ${id === PAGE ? 'aria-current="page"' : ''}>${L(u, e)}</a>`;
    }).join('');
    $('#foot').innerHTML = `<p>${L('LUMOSCHOOL · макет на вигаданих даних · імена, ролі й коди вигадані, фото та контактів немає', 'LUMOSCHOOL · mockup on made-up data · names, roles and codes are invented; no photos, no contacts')}</p>`;
    $$('[data-lang]').forEach(b => b.setAttribute('aria-pressed', b.dataset.lang === lang));
  }

  /* ---------- ВИКЛАДАЧІ ---------- */
  const TEACH = [
    { ini: ['ОК', 'OK'], n: ['Олена К.', 'Olena K.'], role: ['Викладачка · діти 7–12', 'Teacher · kids 7–12'], g: ['kids'], lv: 'A1 → A2',
      what: ['Історії, ігри з карточками й розмова. Говорить українською, англійською, польською.', 'Stories, card games and talking. Speaks Ukrainian, English and Polish.'], ch: ['Документи й досвід з дітьми перевірено', 'Documents and experience with children checked'] },
    { ini: ['МД', 'MD'], n: ['Марко Д.', 'Marko D.'], role: ['Викладач · підлітки 13–17', 'Teacher · teens 13–17'], g: ['teens'], lv: 'A2 → B2',
      what: ['Теми з життя підлітків, шкільна програма, підготовка до виступів.', 'Topics from teens’ lives, school curriculum, getting ready to present.'], ch: ['Документи й досвід з підлітками перевірено', 'Documents and experience with teens checked'] },
    { ini: ['ІВ', 'IV'], n: ['Ірина В.', 'Iryna V.'], role: ['Тренерка з іспитів', 'Exam coach'], g: ['teens', 'exam'], lv: 'B1 → C1',
      what: ['Cambridge та шкільні іспити: пробні тести, розбір помилок, план на тиждень.', 'Cambridge and school exams: practice tests, error review, a weekly plan.'], ch: ['Підтверджена кваліфікація з іспитів', 'Exam qualification confirmed'] },
    { ini: ['ТН', 'TN'], n: ['Томаш Н.', 'Tomasz N.'], role: ['Викладач · бізнес-англійська', 'Teacher · Business English'], g: ['adults'], lv: 'B1 → C1',
      what: ['Мітинги, листи, презентації на матеріалі вашої роботи. Польська й англійська.', 'Meetings, emails and presentations built on your own work. Polish and English.'], ch: ['Підтверджений досвід роботи в компаніях', 'Confirmed company experience'] },
    { ini: ['СЛ', 'SL'], n: ['Софія Л.', 'Sofiia L.'], role: ['Викладачка · розмовна для дорослих', 'Teacher · conversation for adults'], g: ['adults'], lv: 'A2 → C1',
      what: ['Розмова без підручникового присмаку: ситуації, вимова, впевненість.', 'Conversation without the textbook taste: situations, pronunciation, confidence.'], ch: ['Документи перевірено', 'Documents checked'] },
    { ini: ['ГР', 'HR'], n: ['Гелена Р.', 'Helena R.'], role: ['Методистка і відповідальна за безпеку дітей', 'Methodist and child-safety lead'], g: ['kids', 'teens'], lv: '—', nolesson: true,
      what: ['Не веде уроки. Перевіряє плани уроків і розглядає звернення батьків на платформі.', 'Does not teach. Reviews lesson plans and handles parents’ reports on the platform.'], ch: ['Пройшла навчання з безпеки дітей', 'Completed child-safety training'] }
  ];
  const FILT = [['all', 'Усі', 'All'], ['kids', 'Діти 7–12', 'Kids 7–12'], ['teens', 'Підлітки', 'Teens'], ['adults', 'Дорослі', 'Adults'], ['exam', 'Іспити', 'Exams']];
  let tf = 'all';
  function teachers() {
    $('#main').innerHTML = `
      <div class="phead"><div>
        <h1 id="h1">${L('Викладачі', 'Teachers')}</h1>
        <p class="lead">${L('Шестеро людей, які готують і ведуть уроки.', 'Six people who prepare and run the lessons.')}</p>
        <div class="cta-row"><a class="btn primary" id="topCta" href="index.html${q()}#trial">${L('Записатись на пробний урок', 'Book a trial lesson')}</a></div></div>${FLAME}</div>
      <p class="note"><span class="ni" aria-hidden="true">i</span><span><b>${L('Чому без фото і контактів.', 'Why no photos or contacts.')}</b> ${L('Ми показуємо ім’я, роль і що викладач перевірив. Телефони й месенджери викладачів не публікуються, а батьки спілкуються з ними лише в платформі.', 'We show a name, a role and what was checked. Teachers’ phones and messengers are never published, and parents talk to them only inside the platform.')}</span></p>
      <div class="filters" role="group" aria-label="${L('Фільтр за напрямом', 'Filter by program')}"><span class="fl">${L('Показати:', 'Show:')}</span>
        ${FILT.map(([id, u, e]) => `<button type="button" class="chip" data-f="${id}" aria-pressed="${tf === id}">${L(u, e)}</button>`).join('')}</div>
      <p class="count" id="count" role="status" aria-live="polite"></p>
      <ul class="roster" id="roster">${TEACH.map((t, i) => `
        <li class="tr" data-g="${t.g.join(' ')}">
          <div class="mono" aria-hidden="true">${L(...t.ini)}</div>
          <div><h3>${L(...t.n)}</h3><p class="role">${L(...t.role)}</p></div>
          <div><p class="what">${L(...t.what)}</p></div>
          <div><div class="meta">${t.nolesson ? `<span class="tag">${L('без уроків', 'does not teach')}</span>` : `<span class="tag">${t.lv}</span>`}${t.g.map(g => `<span class="tag">${L(...FILT.find(f => f[0] === g).slice(1))}</span>`).join('')}</div>
            <p class="checked"><i aria-hidden="true"></i><span>${L(...t.ch)}</span></p></div>
        </li>`).join('')}</ul>
      <div class="how">
        <div><h3>${L('Двоє дорослих', 'Two adults')}</h3><p>${L('На уроці з дитиною до 16 років завжди є другий дорослий.', 'A lesson with a child under 16 always has a second adult.')}</p></div>
        <div><h3>${L('Лише в платформі', 'Only in the platform')}</h3><p>${L('Викладач не бачить телефону чи пошти родини.', 'A teacher never sees a family’s phone or email.')}</p></div>
        <div><h3>${L('Звернення', 'Reports')}</h3><p>${L('Кнопка «Повідомити» в кабінеті веде до методистки.', 'The “Report” button in the account goes to the methodist.')}</p></div>
      </div>
      <div class="cta-end"><a class="btn primary" href="index.html${q()}#trial">${L('Записатись на пробний урок', 'Book a trial lesson')}</a><a class="link" href="parents.html${q()}">${L('Як ми дбаємо про безпеку', 'How we keep children safe')} <span aria-hidden="true">→</span></a></div>`;
    applyF();
  }
  function applyF() {
    let n = 0;
    $$('.tr').forEach(r => { const ok = tf === 'all' || r.dataset.g.split(' ').includes(tf); r.hidden = !ok; if (ok) n++; });
    $$('.chip').forEach(c => c.setAttribute('aria-pressed', c.dataset.f === tf));
    $('#count').textContent = L(`Показано: ${n} з ${TEACH.length}`, `Showing ${n} of ${TEACH.length}`);
  }

  /* ---------- ДЛЯ БАТЬКІВ ---------- */
  const st = { room: 'parent', rec: false, ask: false };
  const SECT = [['two', 'Двоє дорослих', 'Two adults'], ['consent', 'Згода до 16 років', 'Consent under 16'], ['rec', 'Записи вимкнено', 'Recording is off'], ['inside', 'Зв’язок лише в платформі', 'Contact only in the platform'], ['help', 'Якщо щось не так', 'If something is wrong']];
  function roomHtml() {
    const second = st.room === 'parent'
      ? [L('П', 'P'), L('Батько або мати', 'Parent'), L('сидить поруч або заходить до кімнати', 'sits nearby or joins the room')]
      : [L('Ш', 'S'), L('Спостерігач школи', 'School observer'), L('співробітник, який бачить урок', 'a staff member who watches the lesson')];
    return `<div class="room" aria-live="polite">
      <div class="node"><div class="dot" aria-hidden="true">${L('Д', 'C')}</div><div><b>${L('Дитина', 'Child')}</b><span>${L('до 16 років', 'under 16')}</span></div></div>
      <div class="node"><div class="dot" aria-hidden="true">${L('В', 'T')}</div><div><b>${L('Викладач', 'Teacher')}</b><span>${L('перший дорослий', 'first adult')}</span></div></div>
      <div class="node"><div class="dot" aria-hidden="true">${second[0]}</div><div><b>${second[1]}</b><span>${second[2]}</span></div></div></div>`;
  }
  function recHtml() {
    return `<div class="rec">
      <div class="rec-top"><button type="button" class="sw" role="switch" id="recSw" aria-checked="${st.rec}"><span>${L('Запис уроку', 'Lesson recording')}: ${st.rec ? L('увімкнено', 'on') : L('вимкнено', 'off')}</span><span class="tr_" aria-hidden="true"></span></button>
        ${st.rec ? `<span class="live"><i aria-hidden="true"></i>${L('Іде запис — це видно на екрані всім', 'Recording — everyone sees this on screen')}</span>` : `<span class="off">${L('За замовчуванням вимкнено', 'Off by default')}</span>`}</div>
      <div class="confirm" id="confirm" ${st.ask ? '' : 'hidden'}>
        <label class="agree"><input type="checkbox" id="recOk"><span class="bx" aria-hidden="true"></span><span>${L('Я батько, мати або законний опікун і дозволяю записати цей урок. Запис можна видалити в будь-який час.', 'I am the parent or legal guardian and I allow this lesson to be recorded. The recording can be deleted at any time.')}</span></label>
        <div><button type="button" class="btn ghost" id="recGo">${L('Увімкнути (приклад)', 'Turn on (example)')}</button> <button type="button" class="link" id="recNo" style="background:none;border:0;text-decoration:underline">${L('Скасувати', 'Cancel')}</button></div>
      </div>
      <p>${st.rec ? L('Для макета: запис не йде. У справжній платформі увімкнути його може лише дорослий із кабінету, і лише на один урок.', 'In this mockup nothing is recorded. In a real platform only an adult from the account can turn it on, for one lesson at a time.') : L('Спробуйте: перемикач не вмикається без підтвердження дорослого.', 'Try it: the switch does not turn on without an adult’s confirmation.')}</p></div>`;
  }
  function parents() {
    $('#main').innerHTML = `
      <div class="pwrap">
        <aside class="pside">${FLAME}<h1 id="h1">${L('Для батьків', 'For parents')}</h1>
          <nav class="toc" aria-label="${L('Зміст сторінки', 'On this page')}" id="toc">${SECT.map(([id, u, e], i) => `<a href="#${id}" ${i === 0 ? 'aria-current="true"' : ''}>${L(u, e)}</a>`).join('')}</nav>
          <a class="btn primary side-cta" id="topCta" href="index.html${q()}#trial">${L('Записатись на пробний урок', 'Book a trial lesson')}</a></aside>
        <div class="pbody">
          <section class="rule" id="two" aria-labelledby="t-two"><div class="big" aria-hidden="true">1</div><div><h2 id="t-two">${L('Правило двох дорослих', 'The two-adult rule')}</h2>
            <p class="tx">${L('На кожному уроці з дитиною до 16 років є <b>другий дорослий</b>. Викладач ніколи не залишається з дитиною сам на сам без нагляду. Другим дорослим може бути ви або спостерігач школи — вибираєте ви.', 'Every lesson with a child under 16 has a <b>second adult</b>. A teacher is never alone with a child unobserved. The second adult can be you or a school observer — you choose.')}</p></div>
            <div class="extra"><div class="seg2" role="group" aria-label="${L('Хто другий дорослий', 'Who is the second adult')}"><button type="button" data-room="parent" aria-pressed="${st.room === 'parent'}">${L('Я сам(а)', 'Me')}</button><button type="button" data-room="school" aria-pressed="${st.room === 'school'}">${L('Спостерігач школи', 'School observer')}</button></div><div id="roomBox">${roomHtml()}</div></div></section>
          <section class="rule" id="consent" aria-labelledby="t-consent"><div class="big" aria-hidden="true">2</div><div><h2 id="t-consent">${L('Згода батьків до 16 років', 'Parental consent under 16')}</h2>
            <p class="tx">${L('Школа працює за правилами Польщі: учень до 16 років вчиться <b>лише за згодою</b> батька, матері або законного опікуна. Ми просимо тільки email дорослого. Дитина сама акаунт не створює.', 'The school follows Polish rules: a student under 16 learns <b>only with the consent</b> of a parent or legal guardian. We ask only for the adult’s email. A child never creates an account alone.')}</p></div>
            <div class="extra"><ol class="flow"><li><b>${L('Заявка', 'Request')}</b><span>${L('Ви вказуєте email дорослого.', 'You enter the adult’s email.')}</span></li><li><b>${L('Згода', 'Consent')}</b><span>${L('Лист із посиланням: підтвердити або відмовитись.', 'An email with a link: confirm or decline.')}</span></li><li><b>${L('Код для дитини', 'Child’s code')}</b><span>${L('Після згоди ви отримуєте код для входу дитини.', 'After consent you get a sign-in code for your child.')}</span></li></ol></div></section>
          <section class="rule" id="rec" aria-labelledby="t-rec"><div class="big" aria-hidden="true">3</div><div><h2 id="t-rec">${L('Записи вимкнено за замовчуванням', 'Recording is off by default')}</h2>
            <p class="tx">${L('Уроки <b>не записуються</b>, поки дорослий не дозволив це окремо. Коли запис іде, на екрані видно позначку для всіх.', 'Lessons are <b>not recorded</b> until an adult allows it separately. While recording runs, a marker is visible to everyone on screen.')}</p></div>
            <div class="extra" id="recBox">${recHtml()}</div></section>
          <section class="rule" id="inside" aria-labelledby="t-in"><div class="big" aria-hidden="true">4</div><div><h2 id="t-in">${L('Зв’язок — лише всередині платформи', 'Contact stays inside the platform')}</h2>
            <p class="tx">${L('Викладач і родина пишуть тільки в платформі. Телефонів, месенджерів і пошти один одного вони <b>не бачать</b>: це обмежено на сервері, а не лише в інтерфейсі.', 'Teachers and families write only in the platform. They <b>cannot see</b> each other’s phones, messengers or email: this is restricted on the server, not only in the interface.')}</p></div>
            <div class="extra"><div class="two"><div class="yes"><h3>${L('Можна', 'Allowed')}</h3><ul><li>${L('Повідомлення в чаті платформи', 'Messages in the platform chat')}</li><li>${L('Питання про урок і домашнє', 'Questions about the lesson and homework')}</li><li>${L('Зміна часу уроку в кабінеті', 'Changing a lesson time in the account')}</li></ul></div>
              <div class="no"><h3>${L('Не можна', 'Not allowed')}</h3><ul><li>${L('Обмін номерами й профілями', 'Swapping numbers and profiles')}</li><li>${L('Особисті запитання дитині', 'Personal questions to the child')}</li><li>${L('Просити тримати щось у секреті', 'Asking to keep something secret')}</li></ul></div></div></div></section>
          <section class="rule" id="help" aria-labelledby="t-help"><div class="big" aria-hidden="true">5</div><div><h2 id="t-help">${L('Якщо щось не так', 'If something is wrong')}</h2>
            <p class="tx">${L('У кабінеті є кнопка «Повідомити». Звернення читає методистка з безпеки дітей, викладач його не бачить. Це макет: кнопки й адрес для звернень тут немає.', 'The account has a “Report” button. The child-safety methodist reads the report; the teacher does not see it. This is a mockup: there is no button or address here.')}</p></div>
            <div class="extra cta-end" style="margin-top:24px"><a class="btn primary" href="index.html${q()}#trial">${L('Записатись на пробний урок', 'Book a trial lesson')}</a><a class="link" href="teachers.html${q()}">${L('Хто викладає', 'Who teaches')} <span aria-hidden="true">→</span></a></div></section>
        </div></div>`;
    spy();
  }
  function spy() {
    const links = $$('#toc a'); if (!links.length) return;
    const on = () => {
      let cur = SECT[0][0];
      SECT.forEach(([id]) => { const e = document.getElementById(id); if (e && e.getBoundingClientRect().top < innerHeight * .4) cur = id; });
      links.forEach(a => a.setAttribute('aria-current', a.getAttribute('href') === '#' + cur ? 'true' : 'false'));
    };
    addEventListener('scroll', on, { passive: true }); on();
  }

  /* ---------- ВХІД ---------- */
  const S = { mode: 'in', m: 'email', err: {}, done: null, show: false, v: { email: '', pw: '', pw2: '', code: '', adult: false } };
  const CODE_OK = 'LUMO-7K4Q';
  const M = [['email', 'За посиланням', 'Email link', 'на пошту', 'by email'], ['pw', 'За паролем', 'Password', 'email і пароль', 'email and password'], ['code', 'За кодом', 'Code', 'від батьків, для дитини', 'from a parent, for a child']];
  const FE = (id, m) => `<p class="fe" id="e-${id}"><span class="ei" aria-hidden="true">!</span><span>${m}</span></p>`;
  const emailOk = v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
  function login() {
    const reg = S.mode === 'up';
    const lum = S.done ? '1' : ({ email: '.7', pw: '.8', code: '.9' }[S.m]);
    $('#page').style.setProperty('--lum', lum);
    const err = S.err; const n = Object.keys(err).length;
    const ev = k => err[k] ? ' aria-invalid="true" aria-describedby="e-' + k + '"' : '';
    let body = '';
    if (S.done) body = doneHtml();
    else if (S.m === 'email') body = `<form class="lform" id="f" novalidate>
        <div class="fld"><label for="email">${L('Email', 'Email')}</label><input type="email" id="email" name="email" autocomplete="email" inputmode="email" placeholder="anna.example@example.com" value="${esc(S.v.email)}"${ev('email')}>${err.email ? FE('email', err.email) : `<p class="hint">${reg ? L('Надішлемо посилання, щоб створити акаунт. Пароль не потрібен.', 'We will send a link to create the account. No password needed.') : L('Надішлемо посилання для входу. Пароль не потрібен.', 'We will send a sign-in link. No password needed.')}</p>`}</div>
        ${reg ? adultBox(ev) : ''}
        <button class="btn primary" id="go" type="submit">${L('Надіслати посилання', 'Send the link')}</button></form>`;
    else if (S.m === 'pw') body = `<form class="lform" id="f" novalidate>
        <div class="fld"><label for="email">${L('Email', 'Email')}</label><input type="email" id="email" name="email" autocomplete="email" inputmode="email" placeholder="anna.example@example.com" value="${esc(S.v.email)}"${ev('email')}>${err.email ? FE('email', err.email) : ''}</div>
        <div class="fld"><label for="pw">${L('Пароль', 'Password')}</label><div class="pw"><input type="${S.show ? 'text' : 'password'}" id="pw" name="pw" autocomplete="${reg ? 'new-password' : 'current-password'}" value="${esc(S.v.pw)}"${ev('pw')}><button type="button" id="showPw" aria-pressed="${S.show}">${S.show ? L('Сховати', 'Hide') : L('Показати', 'Show')}</button></div>${err.pw ? FE('pw', err.pw) : `<p class="hint">${L('Для макета: від 8 символів. Справжній пароль не вводьте.', 'For the mockup: 8+ characters. Do not enter a real password.')}</p>`}</div>
        ${reg ? `<div class="fld"><label for="pw2">${L('Повторіть пароль', 'Repeat the password')}</label><input type="${S.show ? 'text' : 'password'}" id="pw2" name="pw2" autocomplete="new-password" value="${esc(S.v.pw2)}"${ev('pw2')}>${err.pw2 ? FE('pw2', err.pw2) : ''}</div>${adultBox(ev)}` : ''}
        <button class="btn primary" id="go" type="submit">${reg ? L('Створити акаунт', 'Create account') : L('Увійти', 'Sign in')}</button></form>`;
    else if (reg) body = `<div class="done"><h2>${L('Дитина не реєструється сама', 'A child does not sign up alone')}</h2><p>${L('Акаунт створює батько або мати. Після цього в кабінеті з’являється код для дитини — його дитина вводить на вкладці «За кодом» у режимі «Вхід».', 'A parent creates the account. Then a code for the child appears in the account — the child enters it on the “Code” tab in “Sign in” mode.')}</p>
        <button class="btn ghost" type="button" id="toParentReg">${L('Створити акаунт дорослого', 'Create an adult account')}</button></div>`;
    else body = `<form class="lform" id="f" novalidate>
        <div class="fld"><label for="code">${L('Код від батьків', 'Code from a parent')}</label><input class="code" type="text" id="code" name="code" autocomplete="off" autocapitalize="characters" spellcheck="false" maxlength="9" placeholder="LUMO-XXXX" value="${esc(S.v.code)}"${ev('code')}>${err.code ? FE('code', err.code) : `<p class="hint">${L('Код дає батько або мати в кабінеті. Приклад для макета: ', 'A parent gives the code from the account. Example for the mockup: ')}<b>${CODE_OK}</b></p>`}</div>
        <button class="btn primary" id="go" type="submit">${L('Увійти за кодом', 'Sign in with the code')}</button></form>`;
    $('#main').innerHTML = `<div class="lwrap">${FLAME}
      <div class="lcard"><h1 id="h1">${S.done === 'email' ? L('Перевірте пошту', 'Check your inbox') : S.done ? L('Готово', 'Done') : reg ? L('Створити акаунт', 'Create an account') : L('Вхід', 'Sign in')}</h1>
        ${S.done ? '' : `<p class="lead">${reg ? L('Для дорослих. Дитину вводить у школу батько або мати.', 'For adults. A parent or guardian adds the child.') : L('Оберіть, як вам зручно увійти.', 'Choose the way that suits you.')}</p>
        <div class="seg2 mode" role="group" aria-label="${L('Режим', 'Mode')}"><button type="button" data-mode="in" aria-pressed="${!reg}">${L('Вхід', 'Sign in')}</button><button type="button" data-mode="up" aria-pressed="${reg}">${L('Реєстрація', 'Sign up')}</button></div>
        <div class="methods" role="tablist" aria-label="${L('Спосіб входу', 'Sign-in method')}">${M.map(([id, u, e, su, se]) => `<button type="button" role="tab" class="m" data-m="${id}" aria-selected="${S.m === id}">${L(u, e)}<span>${L(su, se)}</span></button>`).join('')}</div>`}
        ${n && !S.done ? `<div class="errsum" id="errsum" role="alert" tabindex="-1"><span class="ei" aria-hidden="true">!</span><span><b>${n === 1 ? L('Є одне поле, яке треба виправити', 'One field needs fixing') : L(`Є поля, які треба виправити: ${n}`, `${n} fields need fixing`)}</b></span></div>` : ''}
        <div id="body">${body}</div>
        ${S.done ? '' : `<p class="lnote">${L('Це макет: нічого не надсилається, не зберігається і не перевіряється на сервері. ', 'This is a mockup: nothing is sent, stored or checked on a server. ')}<a class="link" href="parents.html${q()}">${L('Як ми захищаємо дітей', 'How we protect children')}</a></p>`}
      </div></div>`;
  }
  function adultBox(ev) {
    return `<div class="fld"><label class="agree"><input type="checkbox" id="adult" ${S.v.adult ? 'checked' : ''}${ev('adult')}><span class="bx" aria-hidden="true"></span><span>${L('Мені є 16 років або більше, або я батько чи законний опікун учня.', 'I am 16 or older, or I am the student’s parent or legal guardian.')}</span></label>${S.err.adult ? FE('adult', S.err.adult) : ''}</div>`;
  }
  function doneHtml() {
    const d = S.done;
    if (d === 'email') return `<div class="done"><p>${L('Лист надіслано на ', 'An email was sent to ')}<b>${esc(S.v.email)}</b>${L('. Посилання діє 15 хвилин.', '. The link is valid for 15 minutes.')}</p>
      <div class="fakemail"><small>${L('Імітація: листа немає. Натисніть, наче це посилання з листа.', 'Simulated: there is no email. Press it as if it were the link from the email.')}</small><button class="btn primary" type="button" id="fakeLink">${L('Відкрити посилання з листа', 'Open the link from the email')}</button></div>
      <button class="btn ghost" type="button" id="again">${L('Інший email', 'Another email')}</button></div>`;
    if (d === 'ok') return `<div class="done"><h2>${S.mode === 'up' ? L('Акаунт створено (заглушка)', 'Account created (placeholder)') : L('Вхід виконано (заглушка)', 'Signed in (placeholder)')}</h2><p>${L('Тут була б ваша сторінка в кабінеті. Нічого не збережено.', 'Here your account page would open. Nothing was saved.')}</p><button class="btn ghost" type="button" id="again">${L('Спробувати знову', 'Try again')}</button></div>`;
    if (d === 'child') return `<div class="done"><h2>${L('Привіт, Марко!', 'Hi, Marko!')}</h2><p>${L('Код підійшов. Далі Люмо відкрив би твій урок: тут лише два дії — «Почати» і «Спитати дорослого».', 'The code worked. Next Lumo would open your lesson: there are only two actions here — “Start” and “Ask a grown-up”.')}</p>
      <button class="btn primary" type="button" id="again">${L('Почати (приклад)', 'Start (example)')}</button></div>`;
  }
  function submit() {
    const v = S.v; const reg = S.mode === 'up'; const e = {};
    if (S.m === 'code') {
      if (!v.code.trim()) e.code = L('Введіть код від батьків', 'Enter the code from a parent');
      else if (v.code.trim().toUpperCase() !== CODE_OK) e.code = L('Код не підійшов. Перевірте літери або попросіть батьків показати код ще раз.', 'The code did not match. Check the letters or ask a parent to show it again.');
    } else {
      if (!emailOk(v.email)) e.email = L('Вкажіть email у форматі name@example.com', 'Enter an email like name@example.com');
      if (S.m === 'pw') {
        if (v.pw.length < 8) e.pw = L('Пароль має містити щонайменше 8 символів', 'The password needs at least 8 characters');
        if (reg && !e.pw && v.pw2 !== v.pw) e.pw2 = L('Паролі не збігаються', 'The passwords do not match');
        if (reg && !v.pw2 && !e.pw) e.pw2 = L('Повторіть пароль', 'Repeat the password');
      }
      if (reg && !v.adult) e.adult = L('Потрібне підтвердження, щоб продовжити', 'Confirmation is needed to continue');
    }
    S.err = e;
    if (Object.keys(e).length) { login(); const first = Object.keys(e)[0]; const el = document.getElementById(first === 'adult' ? 'adult' : first); const es = $('#errsum'); if (es) es.focus({ preventScroll: true }); if (el) setTimeout(() => el.focus({ preventScroll: false }), 0); return; }
    S.done = S.m === 'email' ? 'email' : S.m === 'code' ? 'child' : 'ok'; login(); const h = $('#h1'); if (h) { h.tabIndex = -1; h.focus({ preventScroll: true }); }
  }

  /* ---------- события ---------- */
  document.addEventListener('click', e => {
    const lg = e.target.closest('[data-lang]');
    if (lg) { lang = lg.dataset.lang; boot(); const b = $(`[data-lang="${lang}"]`); b && b.focus(); return; }
    const f = e.target.closest('[data-f]'); if (f) { tf = f.dataset.f; applyF(); return; }
    const r = e.target.closest('[data-room]'); if (r) { st.room = r.dataset.room; $$('[data-room]').forEach(b => b.setAttribute('aria-pressed', b.dataset.room === st.room)); $('#roomBox').innerHTML = roomHtml(); return; }
    if (e.target.closest('#recSw')) { if (st.rec) { st.rec = false; st.ask = false; } else st.ask = !st.ask; $('#recBox').innerHTML = recHtml(); const b = $('#recSw'); b && b.focus(); return; }
    if (e.target.closest('#recNo')) { st.ask = false; $('#recBox').innerHTML = recHtml(); $('#recSw').focus(); return; }
    if (e.target.closest('#recGo')) { if (!$('#recOk').checked) { $('#recOk').focus(); return; } st.rec = true; st.ask = false; $('#recBox').innerHTML = recHtml(); $('#recSw').focus(); return; }
    const md = e.target.closest('[data-mode]'); if (md) { S.mode = md.dataset.mode; S.err = {}; S.done = null; login(); const b = $(`[data-mode="${S.mode}"]`); b && b.focus(); return; }
    const m = e.target.closest('[data-m]'); if (m) { S.m = m.dataset.m; S.err = {}; S.done = null; login(); const b = $(`[data-m="${S.m}"]`); b && b.focus(); return; }
    if (e.target.closest('#showPw')) { sync(); S.show = !S.show; login(); $('#showPw').focus(); return; }
    if (e.target.closest('#again')) { S.done = null; S.err = {}; login(); const h = $('#email,#code,#h1'); h && h.focus(); return; }
    if (e.target.closest('#fakeLink')) { S.done = 'ok'; login(); const h = $('#h1'); h.tabIndex = -1; h.focus(); return; }
    if (e.target.closest('#toParentReg')) { S.m = 'email'; login(); return; }
  });
  function sync() { ['email', 'pw', 'pw2', 'code'].forEach(k => { const el = document.getElementById(k); if (el) S.v[k] = el.value; }); const a = $('#adult'); if (a) S.v.adult = a.checked; }
  document.addEventListener('submit', e => { if (e.target.id === 'f') { e.preventDefault(); sync(); submit(); } });
  document.addEventListener('input', sync);

  function boot() {
    chrome();
    if (PAGE === 'teachers') teachers(); else if (PAGE === 'parents') parents(); else login();
    const show = () => { document.documentElement.classList.add('ready'); $('#page').classList.add('ready'); };
    if (document.fonts && document.fonts.ready && !document.documentElement.classList.contains('ready')) document.fonts.ready.then(show); else show();
  }
  boot();
  window.__pub = { S, st, boot, get lang() { return lang; } };
})();
