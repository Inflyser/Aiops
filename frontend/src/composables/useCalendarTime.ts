import { computed } from 'vue'
import dayjs from 'dayjs'
import { getContrastColors } from '@/utils/color'

export interface CalendarEventBase {
  id: string | number
  title: string
  description?: string
  start: string
  end: string
  color?: string
  tagIcon?: string
  tag_id?: string
  is_important?: boolean
  eventTasks?: any[]
  completed_task_count?: number
}

export interface TimeConfig {
  dayStartHour: number
  dayEndHour: number
  sleepMode: boolean
  sleepStartHour: number
  sleepEndHour: number
  hourHeight: number
  eventAccentMode: boolean
}

export function useCalendarTime(config: {
  dayStartHour: import('vue').Ref<number> | number
  dayEndHour: import('vue').Ref<number> | number
  sleepMode: import('vue').Ref<boolean> | boolean
  sleepStartHour: import('vue').Ref<number> | number
  sleepEndHour: import('vue').Ref<number> | number
  hourHeight: import('vue').Ref<number> | number
  eventAccentMode: import('vue').Ref<boolean> | boolean
}) {
  const hours = computed(() => {
    const sleepMode = unrefVal(config.sleepMode)
    const dayStartHour = unrefVal(config.dayStartHour)
    const dayEndHour = unrefVal(config.dayEndHour)
    const sleepStartHour = unrefVal(config.sleepStartHour)
    const sleepEndHour = unrefVal(config.sleepEndHour)
    if (sleepMode) {
      return Array.from({ length: 24 }, (_, i) => i).filter(h => h < sleepStartHour || h >= sleepEndHour)
    }
    return Array.from({ length: dayEndHour - dayStartHour }, (_, i) => i + dayStartHour)
  })

  const calendarHeight = computed(() => {
    const sleepMode = unrefVal(config.sleepMode)
    const dayStartHour = unrefVal(config.dayStartHour)
    const dayEndHour = unrefVal(config.dayEndHour)
    const sleepStartHour = unrefVal(config.sleepStartHour)
    const sleepEndHour = unrefVal(config.sleepEndHour)
    const hourHeight = unrefVal(config.hourHeight)
    if (sleepMode) {
      return (24 - (sleepEndHour - sleepStartHour)) * hourHeight
    }
    return (dayEndHour - dayStartHour) * hourHeight
  })

  const sleepGaps = computed(() => {
    const sleepMode = unrefVal(config.sleepMode)
    const hourHeight = unrefVal(config.hourHeight)
    if (!sleepMode) return []
    const h = hours.value
    const gaps: { sleepStart: number; sleepEnd: number; top: number }[] = []
    if (h.length > 0 && h[0] > 0) {
      gaps.push({ sleepStart: 0, sleepEnd: h[0], top: 0 })
    }
    for (let i = 1; i < h.length; i++) {
      if (h[i] - h[i - 1] > 1) {
        gaps.push({
          sleepStart: h[i - 1] + 1,
          sleepEnd: h[i],
          top: i * hourHeight
        })
      }
    }
    return gaps
  })

  function toVisibleMinutes(minutes: number): number {
    const sleepMode = unrefVal(config.sleepMode)
    const sleepStartHour = unrefVal(config.sleepStartHour)
    const sleepEndHour = unrefVal(config.sleepEndHour)
    if (!sleepMode) return minutes
    const sleepStartMin = sleepStartHour * 60
    const sleepDuration = (sleepEndHour - sleepStartHour) * 60
    if (minutes <= sleepStartMin) return minutes
    if (minutes >= sleepEndHour * 60) return minutes - sleepDuration
    return sleepStartMin
  }

  function formatTime(hour: number): string {
    return `${hour.toString().padStart(2, '0')}:00`
  }

  function getEventStyle(
    event: CalendarEventBase,
    dayStart: dayjs.Dayjs,
    isResizingFn: (id: string | number) => boolean,
    resizeNewStart: import('vue').Ref<dayjs.Dayjs | null>,
    resizeNewEnd: import('vue').Ref<dayjs.Dayjs | null>,
    focusMode?: boolean
  ): Record<string, string | number> {
    const hourHeight = unrefVal(config.hourHeight)
    const sleepMode = unrefVal(config.sleepMode)
    const sleepStartHour = unrefVal(config.sleepStartHour)
    const sleepEndHour = unrefVal(config.sleepEndHour)
    const dayStartHour = unrefVal(config.dayStartHour)
    const dayEndHour = unrefVal(config.dayEndHour)
    const eventAccentMode = unrefVal(config.eventAccentMode)

    const start = isResizingFn(event.id) && resizeNewStart.value ? resizeNewStart.value : dayjs(event.start)
    const end = isResizingFn(event.id) && resizeNewEnd.value ? resizeNewEnd.value : dayjs(event.end)

    let startMinutes = start.diff(dayStart, 'minute')
    const duration = end.diff(start, 'minute')

    if (sleepMode) {
      const sleepStartMin = sleepStartHour * 60
      const sleepEndMin = sleepEndHour * 60
      const eventStartMin = startMinutes
      const eventEndMin = startMinutes + duration

      if (eventStartMin >= sleepStartMin && eventEndMin <= sleepEndMin) {
        return { display: 'none' }
      }

      let visibleStart = eventStartMin
      let visibleEnd = eventEndMin

      if (visibleStart < sleepStartMin && visibleEnd > sleepStartMin && visibleEnd <= sleepEndMin) {
        visibleEnd = sleepStartMin
      } else if (visibleStart >= sleepStartMin && visibleStart < sleepEndMin) {
        visibleStart = sleepEndMin
      }

      const visStart = toVisibleMinutes(visibleStart)
      const visEnd = toVisibleMinutes(visibleEnd)
      const visDuration = visEnd - visStart

      const eventColor = event.color || '#4a5568'
      const eventBg = eventAccentMode ? '#1a1a1a' : eventColor
      const { text: eventTextColor, textMuted: eventTextMuted, iconFilter: eventIconFilter } = getContrastColors(eventBg)
      const eventStyleExtra: Record<string, string> = {
        '--event-text-color': eventTextColor,
        '--event-text-muted': eventTextMuted,
        '--event-icon-filter': eventIconFilter
      }
      eventStyleExtra['--event-color'] = eventColor

      const totalVisibleHours = 24 - (sleepEndHour - sleepStartHour)
      const top = (visStart / 60) * hourHeight
      const height = Math.max((visDuration / 60) * hourHeight, 30)
      const maxTop = totalVisibleHours * hourHeight
      const clampedTop = Math.max(0, Math.min(top, maxTop))
      const clampedHeight = Math.min(height, maxTop - clampedTop)

      if (clampedTop >= maxTop || clampedHeight <= 0) {
        return { display: 'none' }
      }

      const base: Record<string, string | number> = {
        top: `${clampedTop}px`,
        height: `${clampedHeight}px`,
        backgroundColor: eventBg,
        position: 'absolute' as const,
        left: focusMode ? '37.5%' : '2px',
        width: focusMode ? '25%' : undefined as any,
        right: focusMode ? 'auto' : '2px',
        zIndex: 10,
        ...eventStyleExtra
      }
      if (focusMode && base.width === undefined) delete base.width
      return base
    }

    const eventColor = event.color || '#4a5568'
    const eventBg = eventAccentMode ? '#1a1a1a' : eventColor
    const { text: eventTextColor, textMuted: eventTextMuted, iconFilter: eventIconFilter } = getContrastColors(eventBg)
    const eventStyleExtra: Record<string, string> = {
      '--event-text-color': eventTextColor,
      '--event-text-muted': eventTextMuted,
      '--event-icon-filter': eventIconFilter
    }
    eventStyleExtra['--event-color'] = eventColor

    const totalDisplayHours = dayEndHour - dayStartHour
    const offsetMinutes = dayStartHour * 60

    if (totalDisplayHours < 24) {
      if (startMinutes < offsetMinutes) {
        startMinutes = offsetMinutes
      } else if (startMinutes >= dayEndHour * 60) {
        return { display: 'none' }
      }

      const top = ((startMinutes - offsetMinutes) / 60) * hourHeight
      const height = Math.max((duration / 60) * hourHeight, 30)
      const maxTop = totalDisplayHours * hourHeight
      const clampedTop = Math.max(0, Math.min(top, maxTop))
      const clampedHeight = Math.min(height, maxTop - clampedTop)

      if (clampedTop >= maxTop || clampedHeight <= 0) {
        return { display: 'none' }
      }

      const base: Record<string, string | number> = {
        top: `${clampedTop}px`,
        height: `${clampedHeight}px`,
        backgroundColor: eventBg,
        position: 'absolute' as const,
        left: focusMode ? '37.5%' : '2px',
        width: focusMode ? '25%' : undefined as any,
        right: focusMode ? 'auto' : '2px',
        zIndex: 10,
        ...eventStyleExtra
      }
      if (focusMode && base.width === undefined) delete base.width
      return base
    }

    const top = (startMinutes / 60) * hourHeight
    const height = Math.max((duration / 60) * hourHeight, 30)
    const maxTop = 24 * hourHeight
    const clampedTop = Math.max(0, Math.min(top, maxTop))
    const clampedHeight = Math.min(height, maxTop - clampedTop)

    if (clampedTop >= maxTop || clampedHeight <= 0) {
      return { display: 'none' }
    }

    const base: Record<string, string | number> = {
      top: `${clampedTop}px`,
      height: `${clampedHeight}px`,
      backgroundColor: eventBg,
      position: 'absolute' as const,
      left: focusMode ? '37.5%' : '2px',
      width: focusMode ? '25%' : undefined as any,
      right: focusMode ? 'auto' : '2px',
      zIndex: 10,
      ...eventStyleExtra
    }
    if (focusMode && base.width === undefined) delete base.width
    return base
  }

  function formatEventTime(
    event: CalendarEventBase,
    isResizingFn: (id: string | number) => boolean,
    resizeNewStart: import('vue').Ref<dayjs.Dayjs | null>,
    resizeNewEnd: import('vue').Ref<dayjs.Dayjs | null>
  ): string {
    const start = isResizingFn(event.id) && resizeNewStart.value ? resizeNewStart.value : dayjs(event.start)
    const end = isResizingFn(event.id) && resizeNewEnd.value ? resizeNewEnd.value : dayjs(event.end)
    return `${start.format('HH:mm')} - ${end.format('HH:mm')}`
  }

  return {
    hours,
    calendarHeight,
    sleepGaps,
    toVisibleMinutes,
    getEventStyle,
    formatEventTime,
    formatTime
  }
}

function unrefVal<T>(val: import('vue').Ref<T> | T): T {
  return (val as any).__v_isRef ? (val as import('vue').Ref<T>).value : (val as T)
}
