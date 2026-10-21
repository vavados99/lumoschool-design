'use client';

import dynamic from 'next/dynamic';

// О-02: спутник Люмо декоративен (aria-hidden, невидим до прокрутки мимо
// героя) и не нужен для первой отрисовки/LCP — грузится отдельным клиентским
// чанком без серверного рендера. `ssr:false` разрешён только внутри Client
// Component — поэтому обёртка вынесена в свой файл, а не в серверный page.tsx.
// Плейсхолдер не нужен: компонент невидим до прокрутки (visible=false по
// умолчанию), поэтому нулевая высота на старте не двигает вёрстку.
export const LumoCompanionLazy = dynamic(
  () => import('./LumoCompanion').then((mod) => mod.LumoCompanion),
  { ssr: false }
);
