import { ref } from 'vue'

export interface DraggableEvent {
  id: string | number
  title: string
  start: string
  end: string
  color?: string
  tag_id?: string
  tagIcon?: string
  description?: string
  location?: string
  priority?: string
  is_important?: boolean
}

export interface DragConfig {
  hourHeight: import('vue').Ref<number> | number
  dayStartHour: import('vue').Ref<number> | number
  sleepMode: import('vue').Ref<boolean> | boolean
  sleepStartHour: import('vue').Ref<number> | number
  sleepEndHour: import('vue').Ref<number> | number
}

export function useEventDrag(config: DragConfig) {
  const draggedEvent = ref<DraggableEvent | null>(null)
  const dragGhost = ref<HTMLElement | null>(null)
  const dragOffsetX = ref(0)
  const dragOffsetY = ref(0)
  const isAltPressed = ref(false)

  const SCROLL_THRESHOLD = 60
  const SCROLL_SPEED = 15
  let autoScrollInterval: ReturnType<typeof setInterval> | null = null
  let currentScrollDir: 'up' | 'down' | null = null

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

  function getCalendarGrid(selector = '.calendar-grid'): HTMLElement | null {
    return document.querySelector(selector) as HTMLElement
  }

  function startAutoScroll(dir: 'up' | 'down') {
    if (autoScrollInterval) return
    autoScrollInterval = setInterval(() => {
      const grid = getCalendarGrid()
      if (!grid) return
      if (dir === 'up') {
        grid.scrollTop = Math.max(0, grid.scrollTop - SCROLL_SPEED)
      } else {
        grid.scrollTop += SCROLL_SPEED
      }
    }, 16)
  }

  function stopAutoScroll() {
    if (autoScrollInterval) {
      clearInterval(autoScrollInterval)
      autoScrollInterval = null
    }
  }

  function handleDragStart(event: DragEvent, calendarEvent: DraggableEvent, eventBlockSelector = '.event-block') {
    draggedEvent.value = calendarEvent
    isAltPressed.value = event.altKey

    // Safety: ensure cleanup even if dragend doesn't fire on the element
    const onWindowDragEnd = () => {
      draggedEvent.value = null
      isAltPressed.value = false
      dragOffsetX.value = 0
      dragOffsetY.value = 0
    }
    window.addEventListener('dragend', onWindowDragEnd, { once: true })

    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = event.altKey ? 'copy' : 'move'
      event.dataTransfer.setData('text/plain', JSON.stringify(calendarEvent))
      event.dataTransfer.setData('application/x-alt-drag', String(event.altKey))

      const transparentImg = new Image()
      transparentImg.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
      event.dataTransfer.setDragImage(transparentImg, 0, 0)
    }

    const target = event.target as HTMLElement
    const eventBlock = target.closest(eventBlockSelector) as HTMLElement
    if (eventBlock) {
      const rect = eventBlock.getBoundingClientRect()
      const offsetX = event.clientX - rect.left
      const offsetY = event.clientY - rect.top
      const ghost = eventBlock.cloneNode(true) as HTMLElement
      ghost.classList.add('drag-ghost')
      ghost.style.position = 'fixed'
      ghost.style.pointerEvents = 'none'
      ghost.style.zIndex = '9999'
      ghost.style.width = eventBlock.offsetWidth + 'px'
      ghost.style.opacity = '0.85'
      ghost.style.left = (event.clientX - offsetX) + 'px'
      ghost.style.top = (event.clientY - offsetY) + 'px'
      dragOffsetX.value = offsetX
      dragOffsetY.value = offsetY
      document.body.appendChild(ghost)
      dragGhost.value = ghost
    }
  }

  function handleDrag(event: DragEvent, gridSelector = '.calendar-grid') {
    if (dragGhost.value) {
      dragGhost.value.style.left = (event.clientX - dragOffsetX.value) + 'px'
      dragGhost.value.style.top = (event.clientY - dragOffsetY.value) + 'px'
    }

    const grid = getCalendarGrid(gridSelector)
    if (!grid) return
    const rect = grid.getBoundingClientRect()
    const relativeY = event.clientY - rect.top

    if (relativeY < SCROLL_THRESHOLD) {
      if (currentScrollDir !== 'up') {
        stopAutoScroll()
        startAutoScroll('up')
        currentScrollDir = 'up'
      }
    } else if (relativeY > rect.height - SCROLL_THRESHOLD) {
      if (currentScrollDir !== 'down') {
        stopAutoScroll()
        startAutoScroll('down')
        currentScrollDir = 'down'
      }
    } else {
      if (currentScrollDir !== null) {
        stopAutoScroll()
        currentScrollDir = null
      }
    }
  }

  function handleDragEnd() {
    draggedEvent.value = null
    isAltPressed.value = false
    dragOffsetX.value = 0
    dragOffsetY.value = 0

    stopAutoScroll()
    currentScrollDir = null

    if (dragGhost.value) {
      dragGhost.value.remove()
      dragGhost.value = null
    }
  }

  function handleTaskDragOver(event: DragEvent) {
    event.preventDefault()
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'move'
    }
  }

  function handleTaskDrop(
    event: DragEvent,
    events: DraggableEvent[],
    emitFn: (event: string, ...args: any[]) => void
  ) {
    event.preventDefault()

    try {
      const droppedData = JSON.parse(event.dataTransfer?.getData('text/plain') || '{}')

      // If dragging a calendar event (has start/end), skip — it's handled elsewhere
      if (droppedData.start && droppedData.end) return

      event.stopPropagation()

      if (droppedData._tag) {
        const targetElement = event.target as HTMLElement
        const eventBlock = targetElement.closest('.event-block, .day-event')
        if (eventBlock) {
          const eventId = eventBlock.getAttribute('data-event-id')
          const targetEvent = events.find(e => String(e.id) === eventId)
          if (targetEvent) {
            emitFn('tag-drop-to-event', { tag: droppedData, event: targetEvent })
          }
        }
      } else if (droppedData.id && droppedData.title) {
        const targetElement = event.target as HTMLElement
        const eventBlock = targetElement.closest('.event-block, .day-event')
        if (eventBlock) {
          const eventId = eventBlock.getAttribute('data-event-id')
          const targetEvent = events.find(e => String(e.id) === eventId)
          if (targetEvent) {
            emitFn('task-drop-to-event', { task: droppedData, event: targetEvent })
          }
        }
      }
    } catch (error) {
      console.error('Error parsing task data:', error)
    }
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

  function cleanupDrag() {
    stopAutoScroll()
    currentScrollDir = null
    if (dragGhost.value) {
      dragGhost.value.remove()
      dragGhost.value = null
    }
  }

  return {
    draggedEvent,
    dragOffsetX,
    dragOffsetY,
    isAltPressed,
    handleDragStart,
    handleDrag,
    handleDragEnd,
    handleTaskDragOver,
    handleTaskDrop,
    getTimeFromPixel,
    cleanupDrag
  }
}
