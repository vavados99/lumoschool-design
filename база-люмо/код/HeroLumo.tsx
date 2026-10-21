'use client';

import { useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useTranslations } from 'next-intl';
import { Star } from 'lucide-react';
import {
  addStars,
  subscribeGame,
  getGameSnapshot,
  getServerGameSnapshot,
} from '@/lib/game/guest-game';
import { LumoSpirit } from './LumoSpirit';

type FloatKind = 'heart' | 'treat' | 'star' | 'zzz';
type FloatItem = { id: number; kind: FloatKind; dx: number };

let floatIdSeq = 0;

/* Кнопки площадки — органы управления игрушкой, а не главный призыв сайта.
   Раньше каждая несла свой цвет и своё цветное свечение на наведении
   (модификаторы --pet/--feed/--play/--sleep в globals.css): четыре разных
   сигнала там, где смысл один — «потрогай Люмо». Три из четырёх цветов к
   тому же принадлежат другим ролям: бирюза — это спокойствие родительской
   половины (деньги, доверие), коралл — единственное действие сайта.

   Теперь кнопки молчат в покое и красятся цветом действия ровно в тот
   момент, когда на них наводят или ведут с клавиатуры. Так цвет действия
   не лежит на экране постоянно и не спорит с настоящим призывом витрины,
   а подсказка «сюда можно нажать» остаётся.

   Цвета заданы переменными и классами, а не inline-значением: inline-стиль
   перебил бы и наведение, и общий guard «меньше движения». */
const PLAY_BTN_CLASS =
  'lumo-play-btn text-[var(--btn-ink)] enabled:hover:text-[var(--btn-ink-hover)] focus-visible:text-[var(--btn-ink-hover)]';
const PLAY_BTN_STYLE = {
  '--btn-ink': 'var(--text)',
  '--btn-ink-hover': 'var(--action)',
} as React.CSSProperties;

function ActionIcon({ kind }: { kind: 'pet' | 'feed' | 'play' | 'sleep' | 'wake' }) {
  switch (kind) {
    case 'pet':
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <path
            d="M12 21s-7.5-4.6-9.5-9C1 8.5 3 5 6.5 5c2 0 3.5 1.2 4.2 2.4a1.5 1.5 0 0 0 2.6 0C14 6.2 15.5 5 17.5 5 21 5 23 8.5 21.5 12c-2 4.4-9.5 9-9.5 9Z"
            fill="currentColor"
          />
        </svg>
      );
    case 'feed':
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <path
            d="M12 6c-1-2.5-3.5-3-5.5-2C3.6 5.4 2.5 8.7 3.7 12c1.3 3.7 4 7 6.3 7 .7 0 1.3-.3 2-.3s1.3.3 2 .3c2.3 0 5-3.3 6.3-7 1.2-3.3.1-6.6-2.8-8-2-1-4.5-.5-5.5 2Z"
            fill="currentColor"
          />
          <path d="M12 6c0-2 1.2-3.4 3-4" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
      );
    case 'play':
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <path d="M12 1.5 14.3 9 22 12l-7.7 3L12 22.5 9.7 15 2 12l7.7-3L12 1.5Z" fill="currentColor" />
        </svg>
      );
    case 'sleep':
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11Z" fill="currentColor" />
        </svg>
      );
    case 'wake':
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <circle cx="12" cy="12" r="4.5" fill="currentColor" />
          <g stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <path d="M12 2.5v2.4M12 19.1v2.4M2.5 12h2.4M19.1 12h2.4M5.2 5.2l1.7 1.7M17.1 17.1l1.7 1.7M18.8 5.2l-1.7 1.7M6.9 17.1l-1.7 1.7" />
          </g>
        </svg>
      );
  }
}

function FloatGlyph({ kind }: { kind: FloatKind }) {
  // Сон — не награда и не действие: это тихое состояние, поэтому «Z» уходит
  // в приглушённый текст. В общем классе он покрашен цветом действия — то
  // есть обещал нажатие там, где нажимать нечего.
  if (kind === 'zzz')
    return (
      <span className="lumo-play-zzz" style={{ color: 'var(--muted)' }}>
        Z
      </span>
    );
  // Сердечко, угощение и звезда — это ОДНА роль: награда за то, что гость
  // потрогал Люмо. Раньше они несли три разных цвета (фиолет / золото /
  // бирюза), из которых бирюза вообще принадлежит родительской половине
  // (спокойствие, деньги, доверие) и на детской стороне значила ложь.
  return (
    <svg viewBox="0 0 24 24" width="30" height="30" aria-hidden="true" style={{ color: 'var(--reward)' }}>
      {kind === 'heart' ? (
        <path
          d="M12 21s-7.5-4.6-9.5-9C1 8.5 3 5 6.5 5c2 0 3.5 1.2 4.2 2.4a1.5 1.5 0 0 0 2.6 0C14 6.2 15.5 5 17.5 5 21 5 23 8.5 21.5 12c-2 4.4-9.5 9-9.5 9Z"
          fill="currentColor"
        />
      ) : kind === 'treat' ? (
        <path
          d="M12 6c-1-2.5-3.5-3-5.5-2C3.6 5.4 2.5 8.7 3.7 12c1.3 3.7 4 7 6.3 7 .7 0 1.3-.3 2-.3s1.3.3 2 .3c2.3 0 5-3.3 6.3-7 1.2-3.3.1-6.6-2.8-8-2-1-4.5-.5-5.5 2Z"
          fill="currentColor"
        />
      ) : (
        <path d="M12 1.5 14.3 9 22 12l-7.7 3L12 22.5 9.7 15 2 12l7.7-3L12 1.5Z" fill="currentColor" />
      )}
    </svg>
  );
}

/**
 * Живой интерактивный Люмо для геройской секции. Гость гладит/кормит/играет/
 * укладывает спать — Люмо реагирует телом, летят награды, над ним появляется
 * компактный пузырь-реплика (жёстко ограничен по ширине, не вылезает за
 * границы). Начисляет XP в игровое ядро и будит квесты ('lumo:action').
 * СОЗНАТЕЛЬНО без выдуманных счётчиков внутри — дофамин даёт сам персонаж.
 */
export function HeroLumo() {
  const t = useTranslations('storefront2.lumoPlay');
  const hud = useTranslations('storefront2.cosmos.hud');
  const game = useSyncExternalStore(subscribeGame, getGameSnapshot, getServerGameSnapshot);
  const stageRef = useRef<HTMLDivElement>(null);
  const [floats, setFloats] = useState<FloatItem[]>([]);
  const [say, setSay] = useState<string | null>(null);
  const [sleeping, setSleeping] = useState(false);
  const sayTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const reduced = useRef(false);

  useEffect(() => {
    reduced.current = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, []);
  useEffect(() => () => clearTimeout(sayTimer.current), []);

  const lumoRoot = () => stageRef.current?.querySelector<HTMLElement>('.lumo');

  const talk = (line: string) => {
    setSay(line);
    clearTimeout(sayTimer.current);
    sayTimer.current = setTimeout(() => setSay(null), 2600);
  };

  const spawn = (kind: FloatKind) => {
    if (reduced.current) return;
    const item = { id: floatIdSeq++, kind, dx: Math.round(Math.random() * 72 - 36) };
    setFloats((prev) => [...prev, item]);
    setTimeout(() => setFloats((prev) => prev.filter((f) => f.id !== item.id)), 1600);
  };

  const poke = (cls: 'lumo-nudge' | 'lumo-wink') => {
    const el = lumoRoot();
    if (!el || reduced.current) return;
    el.classList.add(cls);
    setTimeout(() => el.classList.remove(cls), 280);
  };

  const act = (kind: 'pet' | 'feed' | 'play' | 'sleep' | 'wake', stars: number) => {
    if (stars > 0) addStars(stars);
    window.dispatchEvent(new CustomEvent('lumo:action', { detail: { kind } }));
  };

  const pet = () => {
    if (sleeping) return;
    poke('lumo-wink');
    poke('lumo-nudge');
    spawn('heart');
    talk(t('toast.pet'));
    act('pet', 5);
  };
  const feed = () => {
    if (sleeping) return;
    poke('lumo-nudge');
    spawn('treat');
    talk(t('toast.feed'));
    act('feed', 10);
  };
  const play = () => {
    if (sleeping) return;
    window.dispatchEvent(new CustomEvent('lumo:celebrate'));
    spawn('star');
    talk(t('toast.play'));
    act('play', 15);
  };
  const toggleSleep = () => {
    const el = lumoRoot();
    if (sleeping) {
      el?.classList.remove('lumo-doze');
      setSleeping(false);
      spawn('star');
      talk(t('toast.wake'));
      act('wake', 5);
    } else {
      el?.classList.add('lumo-doze');
      setSleeping(true);
      spawn('zzz');
      talk(t('toast.sleep'));
      act('sleep', 0);
    }
  };

  const line = say ?? t('idle');

  return (
    <div id="lumo-play" className="hero-gs-lumo">
      <div className="flex flex-col items-center gap-5">
        {/* реплика над Люмо — жёстко ограничена по ширине, с хвостиком вниз */}
        <div className="flex min-h-[52px] items-end">
          {/* Перф-фикс (2026-07-15, волна 0 п.0.6): `initial={false}` на
              AnimatePresence — первая реплика Люмо (статичная t('idle'),
              известна уже на сервере) рендерится сразу видимой вместо
              opacity:0-в-SSR-HTML. Смена реплик дальше по игре (talk())
              анимируется как раньше — initial=false отключает только вход
              ПЕРВОГО ребёнка, не последующие enter/exit. См.
              platform/docs-perf-budget.md. */}
          <AnimatePresence mode="wait" initial={false}>
            <motion.p
              key={line}
              initial={{ opacity: 0, y: 8, scale: 0.94 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -6, scale: 0.94 }}
              transition={{ duration: 0.22 }}
              className="lumo-say"
            >
              {line}
            </motion.p>
          </AnimatePresence>
        </div>

        {/* сцена персонажа + летящие награды */}
        <div ref={stageRef} className="relative">
          <LumoSpirit size={210} sparks premiumLayers className="lumo--hero" />
          {floats.map((f) => (
            <span
              key={f.id}
              className="lumo-play-float"
              style={{ '--fx': `${f.dx}px` } as React.CSSProperties}
            >
              <FloatGlyph kind={f.kind} />
            </span>
          ))}
        </div>

        {/* Счёт гостя — ОДНА плашка и ОДНА валюта.
            Раньше их было три: уровень, XP и звёзды. Уровней и XP в детском
            продукте не существует — сайт учил гостя валюте, которой он внутри
            не найдёт. Осталось только настоящее: звёзды. */}
        <div className="flex items-center gap-2">
          {/* Настоящий счёт гостя — это награда, и здесь подсветка честная:
              --shadow-reward оставлен намеренно, в отличие от декоративных
              свечений, снятых по всей детской половине. Цвет и кромка берутся
              из токена награды, а не из зашитых в общий класс #fcd34d и
              rgba(245,158,11,…), которые молча врали при смене темы.

              Цвет награды несут звезда и подложка, а само число остаётся
              обычным текстом: золото по светлому фону нечитаемо, и в день,
              когда витрина перестанет быть тёмной, счёт не должен пропасть. */}
          <span
            className="lumo-stat"
            style={{
              borderRadius: 'var(--r-pill)',
              border: '1px solid transparent',
              background: 'color-mix(in oklab, var(--reward) 14%, transparent)',
              color: 'var(--text)',
              boxShadow: 'var(--shadow-reward)',
            }}
          >
            <Star className="h-3.5 w-3.5" style={{ color: 'var(--reward)' }} />
            {game.stars} {hud('stars')}
          </span>
        </div>

        {/* кнопки-действия */}
        <div className="flex items-center gap-3 sm:gap-4" role="group" aria-label={t('title')}>
          <button
            type="button"
            onClick={pet}
            disabled={sleeping}
            title={t('actions.pet')}
            aria-label={t('actions.pet')}
            className={PLAY_BTN_CLASS}
            style={PLAY_BTN_STYLE}
          >
            <ActionIcon kind="pet" />
          </button>
          <button
            type="button"
            onClick={feed}
            disabled={sleeping}
            title={t('actions.feed')}
            aria-label={t('actions.feed')}
            className={PLAY_BTN_CLASS}
            style={PLAY_BTN_STYLE}
          >
            <ActionIcon kind="feed" />
          </button>
          <button
            type="button"
            onClick={play}
            disabled={sleeping}
            title={t('actions.play')}
            aria-label={t('actions.play')}
            className={PLAY_BTN_CLASS}
            style={PLAY_BTN_STYLE}
          >
            <ActionIcon kind="play" />
          </button>
          <button
            type="button"
            onClick={toggleSleep}
            title={t(sleeping ? 'actions.wake' : 'actions.sleep')}
            aria-label={t(sleeping ? 'actions.wake' : 'actions.sleep')}
            className={PLAY_BTN_CLASS}
            style={PLAY_BTN_STYLE}
          >
            <ActionIcon kind={sleeping ? 'wake' : 'sleep'} />
          </button>
        </div>
      </div>
    </div>
  );
}
