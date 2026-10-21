// Настроение Люмо в кабинете ребёнка — часть связки «Люмо-сквозной»
// (docs/research/прорывы-синтез.md, часть 4, идея 4). Чистая функция:
// принимает уже загруженные плоские данные (без базы, без сети), решает,
// какую реплику показать. Приоритет строго фиксированный:
//   1) отменённый урок БЕЗ переноса — заботливая реплика + ссылка на /schedule
//      (нужна забота прямо сейчас, обгоняет даже приятные новости)
//   2) капсула вместо коммерческого предложения (мастер-план §5.4, см.
//      trial-capsule-ritual.ts) — у ребёнка 1-2 первых завершённых урока и он
//      ещё НЕ запечатал первую фразу. Обгоняет даже камбэк: это разовое узкое
//      окно (грейс всего 2 урока) сразу после старта, теряется быстрее любого
//      другого настроения — если камбэк перехватит внимание сейчас, окно
//      может закрыться прежде, чем ребёнок вообще увидит приглашение
//   3) камбэк-ритуал (волна Б2, docs/superpowers/specs/2026-07-12-platforma-nomer-1-design.md
//      §3) — ребёнок вернулся после паузы ≥COMEBACK_GAP_DAYS (см. comeback-ritual.ts).
//      Тёплый приём важнее даже урока сегодня и домашки: анти-Duolingo принцип —
//      пауза это встреча, а не вина, и это должно быть первым, что ребёнок видит,
//      иначе тёплый эффект возврата теряется под срочными делами
//   4) урок сегодня/скоро — радостная, но "срочная" новость: актуальна только
//      сегодня, поэтому важнее домашки и пустой дорожки — те никуда не денутся
//      до завтра, а повод порадоваться урокe сегодня — денется
//   5) невыполненная домашка — мягкое напоминание
//   6) дорожка курса пуста (ребёнок ещё не начал программу) — воодушевление
//      на первый шаг приключения; ниже домашки, потому что несданная домашка —
//      более конкретное и срочное дело, чем общий призыв начать
//   7) обычное приветствие
//
// Источник "отменённого урока" в реальной схеме (см. src/db/schema-schedule.ts,
// src/db/schema-class.ts, src/lib/schedule/actions.ts::cancelBooking):
// у bookings НЕТ статуса отмены — отменённая бронь целиком удаляется из
// таблицы, а слот освобождается (кредит копилки не сгорает — это отдельная
// история в billing/ledger.ts). Единственный факт отмены, который остаётся
// в базе — class_sessions.status = 'cancelled' (сессия уже была запланирована,
// потом отменена). Поэтому вход функции — это как раз такие сессии ребёнка,
// подготовленные вызывающим кодом (страница кабинета уже делает похожий отбор
// в loadKidCabinet, здесь только чистая логика выбора реплики).
// "Без переноса" = у ребёнка нет другой забронированной сессии на будущее
// (hasReplacementBooking = false) — иначе перенос уже случился, грустить не о чем.
//
// Источник "урок сегодня" — src/lib/kid/data.ts::loadKidCabinet уже вычисляет
// next.kind === 'booked' + next.scheduledAt (ближайшая забронированная сессия
// класса). "Сегодня" сравнивается по календарному дню в Europe/Warsaw (тот же
// принцип и тот же helper dayKey, что и в src/lib/class/stars.ts — приоритетный
// рынок Польша, "день" не должен зависеть от пояса сервера).
//
// Источник "дорожка пуста" — src/components/kid/JourneyPath.tsx уже показывает
// собственное пустое состояние при journey.length === 0 (нет активной программы
// или в ней ещё нет уроков) — здесь та же проверка, просто отражённая в
// настроении Люмо.

import { dayKey } from '@/lib/class/stars'

export type CancelledLessonInfo = {
  cancelledAt: Date
  /** Есть ли у ребёнка уже новая бронь на будущее взамен отменённой. */
  hasReplacementBooking: boolean
}

export type NextLessonInfo = {
  /** Момент начала ближайшего забронированного урока ребёнка. */
  scheduledAt: Date
}

export type LumoMoodInput = {
  /** Самая свежая отменённая (без переноса) сессия ребёнка, если такая есть. */
  recentCancelledLesson: CancelledLessonInfo | null
  /** Сколько домашек ещё не сданы/не завершены. */
  pendingHomeworkCount: number
  /** Игровое имя ребёнка — для тёплого обращения в приветствии. */
  childName: string
  /** Id ребёнка — нужен только для построения pronunciationHref кейса
   * trial_capsule_pending (`/kid/{childId}/pronunciation`, локаль дописывает
   * рендер, тот же приём, что и scheduleHref у cancelled_lesson). */
  childId: string
  /** Ближайший забронированный урок ребёнка (next.kind==='booked' в loadKidCabinet), либо null. */
  nextLesson?: NextLessonInfo | null
  /** Дорожка курса пуста (journey.length === 0) — ребёнок ещё не начал программу. */
  journeyIsEmpty?: boolean
  /** Текущий момент — явный параметр ради тестируемости сравнения "сегодня" (по умолчанию реальное время). */
  now?: Date
  /** Сколько дней прошло с последней практики ребёнка (см. detectComebackGap
   * в comeback-ritual.ts) — задаётся ТОЛЬКО когда это уже признано камбэком
   * (isComeback === true), иначе null/undefined. Само решение "это камбэк или
   * нет" считает comeback-ritual.ts — сюда приходит уже готовый флаг-число,
   * та же дисциплина, что recentCancelledLesson (вызывающая сторона решает,
   * что показывать, эта функция только расставляет приоритет). */
  comebackGapDays?: number | null
  /** Капсула вместо коммерческого предложения (мастер-план §5.4) — true, только
   * когда computeTrialCapsuleEligibility/detectTrialCapsuleEligibility
   * (trial-capsule-ritual.ts) уже решили, что ребёнок в грейс-периоде первых
   * уроков И ещё не запечатал первую фразу. Та же дисциплина, что comebackGapDays —
   * решение "eligible или нет" принимает вызывающая сторона, эта функция только
   * расставляет приоритет. */
  trialCapsuleEligible?: boolean
}

export type LumoMood =
  | { kind: 'cancelled_lesson'; childName: string; scheduleHref: string }
  | { kind: 'trial_capsule_pending'; childName: string; pronunciationHref: string }
  | { kind: 'comeback'; childName: string; gapDays: number }
  | { kind: 'lesson_today'; childName: string }
  | { kind: 'pending_homework'; childName: string; count: number }
  | { kind: 'empty_journey'; childName: string }
  | { kind: 'greeting'; childName: string }

/**
 * Считает настроение Люмо строго по приоритету (см. описание в шапке файла):
 * отменённый урок без переноса > капсула вместо коммерческого предложения >
 * камбэк-приветствие после паузы > урок сегодня > невыполненная домашка >
 * пустая дорожка > обычное приветствие. Тон всегда заботливый — тексты реплик
 * (не эта функция) не должны звучать как упрёк или давление.
 */
export function computeLumoMood(input: LumoMoodInput): LumoMood {
  const { recentCancelledLesson, pendingHomeworkCount, childName, childId } = input
  const nextLesson = input.nextLesson ?? null
  const journeyIsEmpty = input.journeyIsEmpty ?? false
  const now = input.now ?? new Date()
  const comebackGapDays = input.comebackGapDays ?? null
  const trialCapsuleEligible = input.trialCapsuleEligible ?? false

  if (recentCancelledLesson && !recentCancelledLesson.hasReplacementBooking) {
    return { kind: 'cancelled_lesson', childName, scheduleHref: '/schedule' }
  }

  if (trialCapsuleEligible) {
    return { kind: 'trial_capsule_pending', childName, pronunciationHref: `/kid/${childId}/pronunciation` }
  }

  if (comebackGapDays != null) {
    return { kind: 'comeback', childName, gapDays: comebackGapDays }
  }

  if (nextLesson && dayKey(nextLesson.scheduledAt) === dayKey(now)) {
    return { kind: 'lesson_today', childName }
  }

  if (pendingHomeworkCount > 0) {
    return { kind: 'pending_homework', childName, count: pendingHomeworkCount }
  }

  if (journeyIsEmpty) {
    return { kind: 'empty_journey', childName }
  }

  return { kind: 'greeting', childName }
}
