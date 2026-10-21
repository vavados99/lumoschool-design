type LumoMarkProps = {
  size?: number;
  className?: string;
};

/**
 * Эмблема школы: стеклянная капля-минилого с глазами Люмо.
 * Чистый вектор кодом — тот же знак живёт в иконке вкладки (src/app/icon.svg).
 */
export function LumoMark({ size = 28, className = '' }: LumoMarkProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden="true"
      className={className}
    >
      <defs>
        {/* Градиент знака — это паспорт Люмо, а не акцент интерфейса, поэтому
            он остаётся циан→маджента при любой перекраске сайта. Концы ramp'а
            переведены на --brand-from/--brand-to: цвет теперь берётся из
            одного места, а не живёт третьей копией тех же шестнадцатеричных
            значений. Запасные значения в var() — ровно нынешние цвета, вид не
            меняется. Средняя точка оставлена числом сознательно: она подобрана
            рукой (смещена к голубому, а не лежит на середине между концами),
            токена под неё нет, а вычислять её смешением — значит незаметно
            сдвинуть лицо персонажа. */}
        <linearGradient id="lumo-mark-g" x1="6" y1="4" x2="26" y2="30" gradientUnits="userSpaceOnUse">
          <stop stopColor="var(--brand-from, #4FD8FF)" />
          <stop offset="0.55" stopColor="#78BEFF" />
          <stop offset="1" stopColor="var(--brand-to, #C86BFF)" />
        </linearGradient>
      </defs>
      <path
        d="M16 2.5c5.6 0 10.5 5.4 10.5 13.2 0 7.9-4.7 13.8-10.5 13.8S5.5 23.6 5.5 15.7C5.5 7.9 10.4 2.5 16 2.5Z"
        fill="url(#lumo-mark-g)"
        fillOpacity="0.9"
      />
      <path
        d="M10 7.2c1.6-1.8 3.7-2.9 6-2.9 1.9 0 3.6.7 5 1.9-2-0.7-4.6-.8-7 .1-1.7.6-3 1.6-4 2.7-.2-.7-.2-1.3 0-1.8Z"
        fill="#FFFFFF"
        fillOpacity="0.55"
      />
      <ellipse cx="12.6" cy="15.4" rx="2" ry="2.5" fill="#14243A" />
      <ellipse cx="19.4" cy="15.4" rx="2" ry="2.5" fill="#14243A" />
      <circle cx="12" cy="14.5" r="0.75" fill="#FFFFFF" />
      <circle cx="18.8" cy="14.5" r="0.75" fill="#FFFFFF" />
      <path
        d="M13.4 21.2c1.6 1.4 3.6 1.4 5.2 0"
        stroke="#0A0F1C"
        strokeOpacity="0.6"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}
