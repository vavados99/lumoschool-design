'use client';

import { useEffect, useRef, useState } from 'react';

type LumoSpiritProps = {
  /** Диаметр капли в пикселях (высота считается сама). */
  size?: number;
  /** Слот под будущий арт из генераций: если задан — рисованная капля заменяется картинкой. */
  artSrc?: string;
  /** Искры вокруг капли (для крупной сцены героя). */
  sparks?: boolean;
  /**
   * Пилотный режим «2.5D-слои»: тело/глаза/улыбка рисуются премиум-PNG
   * (public/images/lumo/lumo-layer-*.webp) вместо CSS-градиентов, но остаются
   * на тех же классах (.lumo-eye/.lumo-smile) — вся JS-анимация (--ex/--ey,
   * моргание, wink/nudge/swoosh/cheer) продолжает работать без изменений.
   * По умолчанию выключен — существующее поведение НЕ меняется нигде,
   * кроме мест, где проп явно передан true.
   */
  premiumLayers?: boolean;
  className?: string;
};

let burstIdSeq = 0;

/**
 * Люмо — дух живого стекла. Капля с внутренним свечением циан→маджента,
 * глаза следят за курсором (на телефоне — за прокруткой), моргает раз в несколько секунд,
 * иногда моргает дважды подряд, слегка покачивается в простое, подмигивает при
 * наведении/тапе, «сносится» на быстрой прокрутке и празднует ритуалом успеха
 * (window-событие 'lumo:celebrate') — редко и метко, не на каждую мелочь.
 * При «меньше движения» — полностью статичен, включая новые эффекты.
 */
export function LumoSpirit({
  size = 200,
  artSrc,
  sparks = false,
  premiumLayers = false,
  className = '',
}: LumoSpiritProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [cheerSparks, setCheerSparks] = useState<{ id: number; x: number; y: number; angle: number }[]>([]);

  // Глаза: курсор на десктопе, прокрутка на тач-экранах.
  useEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    let raf = 0;

    if (window.matchMedia('(pointer: fine)').matches) {
      let lastMoveAt = Date.now();
      const onMove = (e: PointerEvent) => {
        lastMoveAt = Date.now();
        if (raf) return;
        raf = requestAnimationFrame(() => {
          raf = 0;
          const r = el.getBoundingClientRect();
          const cx = r.left + r.width / 2;
          const cy = r.top + r.height * 0.42;
          const dx = e.clientX - cx;
          const dy = e.clientY - cy;
          const d = Math.hypot(dx, dy) || 1;
          const reach = Math.min(1, d / 240);
          el.style.setProperty('--ex', `${((dx / d) * 4 * reach).toFixed(2)}px`);
          el.style.setProperty('--ey', `${((dy / d) * 3 * reach).toFixed(2)}px`);
        });
      };
      window.addEventListener('pointermove', onMove, { passive: true });

      // Простой (idle fidget): мышь не двигалась ≥5с — Люмо сам «поглядывает
      // по сторонам», чтобы не превращаться в статичную картинку. Как только
      // курсор снова живёт — onMove тут же перехватывает --ex/--ey обратно.
      const glance = () => {
        if (Date.now() - lastMoveAt >= 4800) {
          const angle = Math.random() * Math.PI * 2;
          el.style.setProperty('--ex', `${(Math.cos(angle) * 3.2).toFixed(2)}px`);
          el.style.setProperty('--ey', `${(Math.sin(angle) * 2.2).toFixed(2)}px`);
          setTimeout(() => {
            // Не затирать взгляд, если за это время вернулась мышь.
            if (Date.now() - lastMoveAt >= 700) {
              el.style.setProperty('--ex', '0px');
              el.style.setProperty('--ey', '0px');
            }
          }, 650);
        }
      };
      const idleTimer = setInterval(glance, 5200 + Math.random() * 2000);

      return () => {
        window.removeEventListener('pointermove', onMove);
        clearInterval(idleTimer);
        if (raf) cancelAnimationFrame(raf);
      };
    }

    // Тач: зрачки чуть уходят за направлением прокрутки и возвращаются.
    let lastY = window.scrollY;
    let settle: ReturnType<typeof setTimeout> | undefined;
    const onScroll = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        const y = window.scrollY;
        const dy = Math.max(-3, Math.min(3, (y - lastY) * 0.08));
        lastY = y;
        el.style.setProperty('--ey', `${dy.toFixed(2)}px`);
        clearTimeout(settle);
        settle = setTimeout(() => el.style.setProperty('--ey', '0px'), 350);
      });
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', onScroll);
      clearTimeout(settle);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  // Моргание раз в 4–6 секунд; примерно раз в 5 раз — двойное моргание
  // (как у живых существ), чтобы таймер не ощущался как метроном.
  useEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const timers: ReturnType<typeof setTimeout>[] = [];
    const closeOpen = (delay: number) => {
      timers.push(setTimeout(() => el.classList.add('lumo-blink'), delay));
      timers.push(setTimeout(() => el.classList.remove('lumo-blink'), delay + 160));
    };
    const blink = () => {
      closeOpen(0);
      if (Math.random() < 0.2) closeOpen(220);
      timers.push(setTimeout(blink, 4000 + Math.random() * 2000));
    };
    timers.push(setTimeout(blink, 2600));
    return () => timers.forEach(clearTimeout);
  }, []);

  // Тактильность: наведение/тап по самому Люмо — короткое подмигивание +
  // «нырок навстречу». Реагирует раз на каждый заход курсора/тап, не на
  // каждое микро-движение внутри — чтобы не суетиться.
  useEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    let winkTimer: ReturnType<typeof setTimeout>;
    let nudgeTimer: ReturnType<typeof setTimeout>;
    const notice = () => {
      el.classList.add('lumo-wink', 'lumo-nudge');
      clearTimeout(winkTimer);
      clearTimeout(nudgeTimer);
      winkTimer = setTimeout(() => el.classList.remove('lumo-wink'), 200);
      nudgeTimer = setTimeout(() => el.classList.remove('lumo-nudge'), 280);
    };
    el.addEventListener('pointerenter', notice);
    el.addEventListener('pointerdown', notice);
    return () => {
      el.removeEventListener('pointerenter', notice);
      el.removeEventListener('pointerdown', notice);
      clearTimeout(winkTimer);
      clearTimeout(nudgeTimer);
    };
  }, []);

  // Скорость скролла — материал живёт под рукой: на резком прокруте Люмо
  // на мгновение слегка «сносит», на спокойном чтении — тишина.
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    let raf = 0;
    let lastY = window.scrollY;
    let lastT = performance.now();
    let cooldown = 0;
    const onScroll = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        const el = rootRef.current;
        const now = performance.now();
        const y = window.scrollY;
        const dt = Math.max(1, now - lastT);
        const velocity = Math.abs(y - lastY) / dt; // px/ms
        lastY = y;
        lastT = now;
        if (el && velocity > 1.8 && now > cooldown) {
          cooldown = now + 260;
          el.classList.add('lumo-swoosh');
          setTimeout(() => el.classList.remove('lumo-swoosh'), 220);
        }
      });
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  // Ритуал успеха: любое место платформы может дать Люмо знать о крупной
  // вехе через window.dispatchEvent(new CustomEvent('lumo:celebrate')) —
  // например «домашка сдана» или «дневная звёздная веха». Специально НЕ
  // вешаем на каждый мелкий верный ответ — редко и метко, иначе праздник
  // обесценится. При «меньше движения» — событие принимается тихо, без
  // прыжка/искр (см. CSS: animation:none на .lumo-cheer*).
  useEffect(() => {
    const el = rootRef.current;
    const onCelebrate = () => {
      if (!el) return;
      el.classList.add('lumo-cheer');
      setTimeout(() => el.classList.remove('lumo-cheer'), 650);
      if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const burst = Array.from({ length: 5 }, (_, i) => {
          const angle = (Math.PI * 2 * i) / 5 + Math.random() * 0.4;
          return { id: burstIdSeq++, x: Math.cos(angle) * 34, y: Math.sin(angle) * 34 - 12, angle };
        });
        setCheerSparks((prev) => [...prev, ...burst]);
        setTimeout(() => {
          const ids = new Set(burst.map((b) => b.id));
          setCheerSparks((prev) => prev.filter((s) => !ids.has(s.id)));
        }, 750);
      }
    };
    window.addEventListener('lumo:celebrate', onCelebrate);
    return () => window.removeEventListener('lumo:celebrate', onCelebrate);
  }, []);

  return (
    <div
      ref={rootRef}
      aria-hidden="true"
      className={`lumo ${className}`}
      style={{ '--lumo-w': `${size}px` } as React.CSSProperties}
    >
      {artSrc ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={artSrc} alt="" className="lumo-art" />
      ) : premiumLayers ? (
        <div className="lumo-body lumo-body--premium">
          {/* fetchPriority="high" — это тело Люмо, самый крупный элемент первого
              экрана. Без подсказки браузер ставит его в общую очередь и начинает
              качать позже, чем мог бы: замер до правки показывал 5.1 секунды до
              появления самого крупного элемента при норме 2.5. */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/images/lumo/lumo-layer-body.webp"
            alt=""
            className="lumo-body-art"
            draggable={false}
            fetchPriority="high"
            decoding="async"
          />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/images/lumo/lumo-layer-eye.webp" alt="" className="lumo-eye lumo-eye-img l" draggable={false} />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/images/lumo/lumo-layer-eye.webp" alt="" className="lumo-eye lumo-eye-img r" draggable={false} />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/images/lumo/lumo-layer-smile.webp" alt="" className="lumo-smile lumo-smile-img" draggable={false} />
        </div>
      ) : (
        <div className="lumo-body">
          <span className="lumo-gloss" />
          <div className="lumo-eye l" />
          <div className="lumo-eye r" />
          <span className="lumo-cheek l" />
          <span className="lumo-cheek r" />
          <div className="lumo-smile" />
        </div>
      )}
      {sparks && (
        <>
          <span className="lumo-spark" style={{ top: '12%', left: '4%' }} />
          <span className="lumo-spark" style={{ top: '68%', left: '96%', animationDelay: '0.4s' }} />
          <span className="lumo-spark" style={{ top: '88%', left: '10%', animationDelay: '0.8s' }} />
        </>
      )}
      {cheerSparks.map((s) => (
        <span
          key={s.id}
          className="lumo-cheer-spark"
          style={
            {
              top: '46%',
              left: '50%',
              marginLeft: '-3px',
              marginTop: '-3px',
              '--sx': `${s.x.toFixed(1)}px`,
              '--sy': `${s.y.toFixed(1)}px`,
            } as React.CSSProperties
          }
        />
      ))}
    </div>
  );
}
