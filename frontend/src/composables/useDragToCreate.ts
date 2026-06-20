import { ref, nextTick } from 'vue'
import dayjs from 'dayjs'

export interface DragToCreateConfig {
  hourHeight: import('vue').Ref<number> | number
  dayStartHour: import('vue').Ref<number> | number
  sleepMode: import('vue').Ref<boolean> | boolean
  sleepStartHour: import('vue').Ref<number> | number
  sleepEndHour: import('vue').Ref<number> | number
}

export function useDragToCreate(config: DragToCreateConfig) {
  const selDay = ref<string>('')
  const selTop = ref(0)
  const selHeight = ref(0)
  const isDragging = ref(false)
  const hasMoved = ref(false)
  const showCreateInput = ref(false)
  const createTitle = ref('')
  let selStartY = 0
  let selStartDay = ''
  const createTitleInput = ref<HTMLInputElement | null>(null)

  let removeMouseListeners: (() => void) | null = null

  function getHH(): number {
    return (config.hourHeight as import('vue').Ref<number>).value ?? (config.hourHeight as number)
  }
  function getDayStartHour(): number {
    return (config.dayStartHour as import('vue').Ref<number>).value ?? (config.dayStartHour as number)
  }
  function getSleepMode(): boolean {
    return (config.sleepMode as import('vue').Ref<boolean>).value ?? (config.sleepMode as boolean)
  }
  function getSleepStartHour(): number {
    return (config.sleepStartHour as import('vue').Ref<number>).value ?? (config.sleepStartHour as number)
  }
  function getSleepEndHour(): number {
    return (config.sleepEndHour as import('vue').Ref<number>).value ?? (config.sleepEndHour as number)
  }

  function getTimeFromPixel(pixelY: number): { hour: number; minute: number } {
    const slotIndex = Math.floor(pixelY / getHH())
    const offsetMin = Math.round(((pixelY % getHH()) / getHH()) * 60 / 10) * 10

    if (getSleepMode()) {
      const visibleHours = Array.from({ length: 24 }, (_, i) => i).filter(h => h < getSleepStartHour() || h >= getSleepEndHour())
      const hour = visibleHours[slotIndex] ?? 0
      return { hour, minute: offsetMin }
    }
    const hour = slotIndex + getDayStartHour()
    return { hour, minute: offsetMin }
  }

  function addMouseListeners(
    emitClick: (data: { day: any; dateTime: dayjs.Dayjs }) => void,
    _emitCreate: (data: { date: string; startTime: string; endTime: string; title: string }) => void,
    weekDays?: import('vue').Ref<any[]> | any[],
    _dayDate?: import('vue').Ref<string> | string
  ) {
    const onMove = (e: MouseEvent) => {
      if (!isDragging.value) return
      hasMoved.value = true

      const dayEl = (e.target as HTMLElement).closest('.day-column') as HTMLElement
      if (!dayEl) return

      const rect = dayEl.getBoundingClientRect()
      const currentY = Math.max(0, Math.min(e.clientY - rect.top, rect.height - 1))
      const dayDateStr = dayEl.dataset.dayDate || selStartDay

      selDay.value = dayDateStr
      selTop.value = Math.min(selStartY, currentY)
      selHeight.value = Math.abs(currentY - selStartY)
    }

    const onUp = (e: MouseEvent) => {
      if (!isDragging.value) return
      isDragging.value = false
      removeListeners()

      if (!hasMoved.value) {
        selDay.value = ''
        selTop.value = 0
        selHeight.value = 0

        const dayEl = (e.target as HTMLElement).closest('.day-column') as HTMLElement
        if (dayEl) {
          const rect = dayEl.getBoundingClientRect()
          const clickY = e.clientY - rect.top
          const slotIndex = Math.floor(clickY / getHH())
          const rawMinutes = Math.floor((clickY % getHH()) / getHH() * 60)
          const minutes = Math.round(rawMinutes / 10) * 10
          let hour: number
          if (getSleepMode()) {
            const visibleHours = Array.from({ length: 24 }, (_, i) => i).filter(h => h < getSleepStartHour() || h >= getSleepEndHour())
            hour = visibleHours[slotIndex] ?? 0
          } else {
            hour = slotIndex + getDayStartHour()
          }
          const wd = weekDays
          const days = Array.isArray(wd) ? wd : (wd?.value || [])
          const dayData = days.find((d: any) => d.date === selStartDay)
          if (dayData) {
            const clickedDateTime = dayData.fullDate.hour(hour).minute(minutes)
            emitClick({ day: dayData, dateTime: clickedDateTime })
          }
        }
        return
      }

      showCreateInput.value = true
      createTitle.value = ''
      nextTick(() => {
        const input = document.querySelector('.create-event-input') as HTMLInputElement
        if (input) input.focus()
      })
    }

    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
    removeMouseListeners = () => {
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
    }
  }

  function addMouseListenersDay(
    _emitCreate: (data: { date: string; startTime: string; endTime: string; title: string }) => void,
    gridRef: import('vue').Ref<HTMLElement | null>,
    _currentDay: import('vue').Ref<dayjs.Dayjs> | dayjs.Dayjs
  ) {
    const onMove = (e: MouseEvent) => {
      if (!isDragging.value) return
      hasMoved.value = true

      const grid = gridRef.value
      if (!grid) return

      const rect = grid.getBoundingClientRect()
      const currentY = Math.max(0, Math.min(e.clientY - rect.top, rect.height - 1))

      selTop.value = Math.min(selStartY, currentY)
      selHeight.value = Math.abs(currentY - selStartY)
    }

    const onUp = (_e: MouseEvent) => {
      if (!isDragging.value) return
      isDragging.value = false
      removeListeners()

      if (!hasMoved.value) {
        cancelSelection()
        return
      }

      showCreateInput.value = true
      createTitle.value = ''
      nextTick(() => {
        const input = document.querySelector('.create-event-input') as HTMLInputElement
        if (input) input.focus()
      })
    }

    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
    removeMouseListeners = () => {
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
    }
  }

  function removeListeners() {
    if (removeMouseListeners) {
      removeMouseListeners()
      removeMouseListeners = null
    }
  }

  function startSelection(event: MouseEvent, day?: any) {
    if ((event.target as HTMLElement).closest('.event-block')) return

    const dayEl = (event.currentTarget || event.target) as HTMLElement
    const rect = dayEl.getBoundingClientRect ? dayEl.getBoundingClientRect() : { top: 0, height: 0 }
    selStartY = Math.max(0, Math.min(event.clientY - rect.top, rect.height - 1))
    selStartDay = day?.date || ''

    isDragging.value = true
    hasMoved.value = false
    showCreateInput.value = false
    createTitle.value = ''
    if (day?.date) selDay.value = day.date
    selTop.value = selStartY
    selHeight.value = 0
  }

  function startSelectionDay(event: MouseEvent, gridRef: import('vue').Ref<HTMLElement | null>) {
    if ((event.target as HTMLElement).closest('.day-event')) return
    if ((event.target as HTMLElement).closest('.event-star-btn')) return

    const grid = gridRef.value
    if (!grid) return
    const rect = grid.getBoundingClientRect()
    selStartY = Math.max(0, Math.min(event.clientY - rect.top, rect.height - 1))

    isDragging.value = true
    hasMoved.value = false
    showCreateInput.value = false
    createTitle.value = ''
    selTop.value = selStartY
    selHeight.value = 0
  }

  function createEvent(
    emitFn: (event: string, ...args: any[]) => void,
    dateStr?: string
  ) {
    if (!createTitle.value.trim()) {
      cancelSelection()
      return
    }

    const startTime = getTimeFromPixel(selTop.value)
    const endTime = getTimeFromPixel(selTop.value + selHeight.value)

    let endHour = endTime.hour
    let endMin = endTime.minute
    if (endHour < startTime.hour || (endHour === startTime.hour && endMin <= startTime.minute)) {
      endHour = startTime.hour
      endMin = startTime.minute + 30
      if (endMin >= 60) { endHour += 1; endMin -= 60 }
    }

    const fmt = (h: number, m: number) =>
      `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`

    emitFn('create-event', {
      date: dateStr || selDay.value,
      startTime: fmt(startTime.hour, startTime.minute),
      endTime: fmt(endHour, endMin),
      title: createTitle.value.trim()
    })

    cancelSelection()
  }

  function cancelSelection() {
    selTop.value = 0
    selHeight.value = 0
    showCreateInput.value = false
    createTitle.value = ''
  }

  function submitCreate(
    emitFn: (event: string, ...args: any[]) => void,
    dateStr?: string
  ) {
    if (createTitle.value.trim()) {
      createEvent(emitFn, dateStr)
    } else {
      cancelSelection()
    }
  }

  function cleanupCreate() {
    removeListeners()
  }

  return {
    selDay,
    selTop,
    selHeight,
    isDragging,
    hasMoved,
    showCreateInput,
    createTitle,
    createTitleInput,
    addMouseListeners,
    addMouseListenersDay,
    removeListeners,
    startSelection,
    startSelectionDay,
    createEvent,
    cancelSelection,
    submitCreate,
    getTimeFromPixel,
    cleanupCreate
  }
}
