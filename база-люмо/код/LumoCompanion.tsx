'use client';

import { useEffect, useState } from 'react';
import { useLocale } from 'next-intl';
import { speak as speakVoice } from '@/lib/voice/speak';
import { toVoiceLocale } from '@/lib/voice/types';
import { LumoSpirit } from './LumoSpirit';

/**
 * Маленький Люмо-спутник в углу: появляется после героя и меняет реплику,
 * когда очередная секция с data-lumo-line проходит через середину экрана.
 * Полностью декоративен — клики проходят сквозь него.
 */
export function LumoCompanion() {
  const [line, setLine] = useState('');
  const [visible, setVisible] = useState(false);
  const [nearForm, setNearForm] = useState(false);
  const [bubbleAwake, setBubbleAwake] = useState(false);
  const rawLocale = useLocale();
  const voiceLocale = toVoiceLocale(rawLocale);

  // «Просыпается» сразу при смене реплики — правка состояния прямо во время
  // рендера (React-эскейп-хэтч "adjusting state when a prop changes"), без
  // лишнего прохода через эффект.
  const [prevLine, setPrevLine] = useState(line);
  if (line !== prevLine) {
    setPrevLine(line);
    if (line) setBubbleAwake(true);
  }

  // Пузырь живёт несколько секунд после смены реплики и «засыпает»,
  // чтобы не перекрывать карточки в правом нижнем углу при долгом чтении.
  useEffect(() => {
    if (!line) return;
    const nap = setTimeout(() => setBubbleAwake(false), 5200);
    return () => clearTimeout(nap);
  }, [line]);

  // Озвучиваем новую реплику голосом Люмо (Piper/Kokoro → Web Speech — честная
  // деградация внутри speak.ts). Тихая деградация: движок ничего не смог —
  // текст пузыря остаётся как есть, никакой индикации ошибки гостю.
  useEffect(() => {
    if (!line) return;
    const controller = new AbortController();
    void speakVoice(line, voiceLocale, { mode: 'ui', signal: controller.signal });
    return () => controller.abort();
  }, [line, voiceLocale]);

  useEffect(() => {
    const sections = Array.from(document.querySelectorAll<HTMLElement>('[data-lumo-line]'));
    if (sections.length === 0) return;

    const speak = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const text = (entry.target as HTMLElement).dataset.lumoLine;
            if (text) setLine(text);
          }
        }
      },
      { rootMargin: '-40% 0px -40% 0px' }
    );
    sections.forEach((s) => speak.observe(s));

    const hero = document.getElementById('hero');
    let heroWatch: IntersectionObserver | undefined;
    if (hero) {
      heroWatch = new IntersectionObserver(
        ([entry]) => setVisible(!entry.isIntersecting),
        { threshold: 0.05 }
      );
      heroWatch.observe(hero);
    }

    // У формы пробника спутник умолкает и уходит: там его реплика уже написана,
    // а угол экрана нужен кнопке отправки.
    const form = document.getElementById('trial-form');
    let formWatch: IntersectionObserver | undefined;
    if (form) {
      formWatch = new IntersectionObserver(
        ([entry]) => setNearForm(entry.isIntersecting),
        { threshold: 0.05 }
      );
      formWatch.observe(form);
    }

    return () => {
      speak.disconnect();
      heroWatch?.disconnect();
      formWatch?.disconnect();
    };
  }, []);

  return (
    <div
      aria-hidden="true"
      className={`lumo-companion ${visible && !nearForm && line ? 'lumo-companion--visible' : ''}`}
    >
      {line && (
        <p
          key={line}
          className={`lumo-bubble lumo-bubble--in mb-6 max-w-[220px] text-[13px] ${
            bubbleAwake ? '' : 'lumo-bubble--sleep'
          }`}
        >
          {line}
        </p>
      )}
      <LumoSpirit size={56} />
    </div>
  );
}
