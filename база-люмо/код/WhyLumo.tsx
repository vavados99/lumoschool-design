import { getTranslations } from 'next-intl/server';

/**
 * «Почему с Люмо иначе» — короткий ответ сразу после героя.
 *
 * ЗАЧЕМ ЭТА СЕКЦИЯ ПОЯВИЛАСЬ. До неё посетитель с первого экрана падал прямо в
 * ежедневные квесты — то есть в игрушку, ещё не поняв, что вообще за продукт.
 * Родитель, который пришёл выбирать школу ребёнку, видит вторым экраном «погладь
 * Люмо» и закрывает вкладку. Здесь он за пять секунд получает всю суть.
 *
 * ПОЧЕМУ НЕ ТРИ КАРТОЧКИ С ИКОНКАМИ. Три одинаковые карточки — это визуальный
 * шаблон, который читается как «сейчас будет список преимуществ», и глаз его
 * пролистывает. Здесь одна фраза-уравнение: три части складываются в результат,
 * и результат — то, ради чего родитель платит. Читается как предложение, а не
 * как таблица.
 *
 * СЕРВЕРНЫЙ КОМПОНЕНТ НАМЕРЕННО. На витрине 21 клиентский компонент из 24 —
 * это и есть причина, по которой страница тяжёлая. Здесь нет ни одного
 * обработчика: только текст и разметка. Ни байта лишнего кода посетителю.
 */
export async function WhyLumo() {
  const t = await getTranslations('storefront2.whyLumo');

  const parts = [
    { key: 'live', accent: 'var(--action)' },
    { key: 'personal', accent: 'var(--calm)' },
    { key: 'play', accent: 'var(--reward)' },
  ] as const;

  return (
    <section id="why-lumo" className="relative w-full scroll-mt-20 px-4 py-16 sm:px-6 sm:py-24">
      <div className="mx-auto w-full max-w-5xl">
        <p className="mb-6 text-center text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">
          {t('eyebrow')}
        </p>

        {/*
          Уравнение. На широком экране читается в строку — три части и результат.
          На узком складывается в столбик: плюсы превращаются в разделители, и
          порядок чтения сохраняется. Это НЕ сжатая версия десктопа, а своя
          раскладка того же смысла.
        */}
        <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-center sm:gap-2">
          {parts.map((part, index) => (
            <div key={part.key} className="contents">
              {index > 0 && (
                <span
                  aria-hidden
                  className="mx-auto text-2xl font-light leading-none text-[var(--muted)] sm:mx-1"
                >
                  +
                </span>
              )}
              <div
                className="flex flex-1 flex-col gap-1.5 border p-5 text-center"
                style={{
                  borderRadius: 'var(--r-card)',
                  borderColor: 'var(--surface-parent-edge)',
                  background: 'var(--surface-parent)',
                }}
              >
                <span
                  className="text-[11px] font-bold uppercase tracking-[0.18em]"
                  style={{ color: part.accent }}
                >
                  {t(`${part.key}.label`)}
                </span>
                <span
                  className="text-base font-semibold leading-snug text-[var(--text)]"
                  style={{ fontFamily: 'var(--font-display)' }}
                >
                  {t(`${part.key}.title`)}
                </span>
                <span className="text-sm leading-relaxed text-[var(--muted)]">
                  {t(`${part.key}.text`)}
                </span>
              </div>
            </div>
          ))}

          <span
            aria-hidden
            className="mx-auto text-2xl font-light leading-none text-[var(--muted)] sm:mx-1"
          >
            =
          </span>

          {/*
            Результат выделен цветом действия — это единственное место секции,
            где он появляется. Цвет действия обязан значить действие или его
            плод; раскрась им три части — и он перестанет значить что-либо.
          */}
          <div
            className="flex flex-1 flex-col justify-center gap-1.5 border p-5 text-center"
            style={{
              borderRadius: 'var(--r-card)',
              borderColor: 'color-mix(in oklab, var(--action) 34%, transparent)',
              background: 'color-mix(in oklab, var(--action) 8%, var(--surface-parent))',
            }}
          >
            <span
              className="text-lg font-bold leading-snug text-[var(--text)]"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              {t('result.title')}
            </span>
            <span className="text-sm leading-relaxed text-[var(--muted)]">{t('result.text')}</span>
          </div>
        </div>
      </div>
    </section>
  );
}
