import { ref } from 'vue'
import dayjs from 'dayjs'

export interface ResizableEvent {
  id: string | number
  start: string
  end: string
}

export function useEventResize(hourHeight: import('vue').Ref<number> | number) {
  const resizingEventId = ref<string | number | null>(null)
  const resizeStartY = ref(0)
  const resizeDirection = ref<'bottom' | 'top' | null>(null)
  const resizeOriginalEnd = ref<dayjs.Dayjs | null>(null)
  const resizeNewEnd = ref<dayjs.Dayjs | null>(null)
  const resizeOriginalStart = ref<dayjs.Dayjs | null>(null)
  const resizeNewStart = ref<dayjs.Dayjs | null>(null)
  const resizeEvent = ref<ResizableEvent | null>(null)

  function isResizing(eventId: string | number): boolean {
    return resizingEventId.value === eventId
  }

  function getHH(): number {
    return (hourHeight as import('vue').Ref<number>).value ?? (hourHeight as number)
  }

  function startResize(e: MouseEvent, event: ResizableEvent, direction: 'bottom' | 'top') {
    e.stopPropagation()
    e.preventDefault()

    resizingEventId.value = event.id
    resizeStartY.value = e.clientY
    resizeDirection.value = direction
    resizeOriginalEnd.value = dayjs(event.end)
    resizeOriginalStart.value = dayjs(event.start)
    resizeEvent.value = event

    document.addEventListener('pointermove', onResizeMove)
    document.addEventListener('pointerup', onPointerUp)
  }

  function onPointerUp() {
    onResizeEnd()
  }

  function onResizeMove(e: PointerEvent) {
    if (!resizeEvent.value) return

    const deltaY = e.clientY - resizeStartY.value
    const deltaMinutes = (deltaY / getHH()) * 60

    if (resizeDirection.value === 'bottom') {
      if (!resizeOriginalEnd.value) return
      const newEnd = resizeOriginalEnd.value.add(deltaMinutes, 'minute')
      const snapMinutes = Math.round(newEnd.minute() / 10) * 10
      const snappedEnd = newEnd.minute(snapMinutes).second(0).millisecond(0)
      const start = dayjs(resizeEvent.value.start)
      const minEnd = start.add(15, 'minute')
      resizeNewEnd.value = snappedEnd.isBefore(minEnd) ? minEnd : snappedEnd
    } else {
      if (!resizeOriginalStart.value) return
      const newStart = resizeOriginalStart.value.add(deltaMinutes, 'minute')
      const snapMinutes = Math.round(newStart.minute() / 10) * 10
      const snappedStart = newStart.minute(snapMinutes).second(0).millisecond(0)
      const end = dayjs(resizeEvent.value.end)
      const maxStart = end.subtract(15, 'minute')
      resizeNewStart.value = snappedStart.isAfter(maxStart) ? maxStart : snappedStart
    }
  }

  type ResizeCallback = (data: {
    event: ResizableEvent
    newDate: string
    newStart: string
    newEnd: string
  }) => void

  function onResizeEnd(callback?: ResizeCallback) {
    document.removeEventListener('pointermove', onResizeMove)
    document.removeEventListener('pointerup', onPointerUp)

    if (resizeEvent.value && callback) {
      const event = resizeEvent.value
      if (resizeDirection.value === 'top' && resizeNewStart.value) {
        const startISO = resizeNewStart.value.toISOString()
        const dayStart = dayjs(event.start).startOf('day')
        callback({
          event,
          newDate: dayStart.format('YYYY-MM-DD'),
          newStart: startISO,
          newEnd: event.end
        })
      } else if (resizeDirection.value === 'bottom' && resizeNewEnd.value) {
        const endISO = resizeNewEnd.value.toISOString()
        const dayStart = dayjs(event.start).startOf('day')
        callback({
          event,
          newDate: dayStart.format('YYYY-MM-DD'),
          newStart: event.start,
          newEnd: endISO
        })
      }
    }

    setTimeout(() => {
      resizingEventId.value = null
      resizeStartY.value = 0
      resizeDirection.value = null
      resizeOriginalEnd.value = null
      resizeNewEnd.value = null
      resizeOriginalStart.value = null
      resizeNewStart.value = null
      resizeEvent.value = null
    }, 60)
  }

  function cleanupResize() {
    document.removeEventListener('pointermove', onResizeMove)
    document.removeEventListener('pointerup', onPointerUp)
  }

  return {
    resizingEventId,
    resizeNewStart,
    resizeNewEnd,
    resizeEvent,
    isResizing,
    startResize,
    onResizeEnd,
    cleanupResize
  }
}
