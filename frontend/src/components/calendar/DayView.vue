<template>
  <div class="day-calendar">
    <div class="day-header">
      <div class="day-header-content">
        <div class="day-info">
          <h1 class="day-weekday">{{ currentDay.format('dddd') }}</h1>
          <h2 class="day-date">{{ currentDay.format('D MMMM YYYY') }}</h2>
        </div>
        <div class="day-nav">
          <button class="nav-btn1" @click="$emit('prev-day')"><</button>
          <button class="today-btn" @click="$emit('go-today')">Сегодня</button>
          <button class="nav-btn1" @click="$emit('next-day')">></button>
          <button
            class="focus-btn"
            :class="{ active: focusMode }"
            @click="toggleFocusMode"
            title="Режим фокуса"
          >
            🎯
          </button>
        </div>
      </div>
    </div>
    
    <div class="day-scroll-container" ref="scrollContainerRef">
      <div class="day-grid" @mousedown="startSelection" @dragover="handleGridDragOver" @drop="handleGridDrop">
        <div 
          v-for="hour in hours" 
          :key="hour"
          class="day-hour-row"
          :style="{ minHeight: hourHeight + 'px' }"
        >
          <div class="hour-label">{{ hour.toString().padStart(2, '0') }}:00</div>
          <div class="hour-events" @click="handleRowClick(hour)"></div>
        </div>
        
        <div class="events-container" :style="{ minHeight: calendarHeight + 'px' }">
          <!-- Sleep gap markers -->
          <div v-for="gap in sleepGaps" :key="'gap-' + gap.sleepStart" class="sleep-gap-marker" :style="{ top: gap.top + 'px' }">
            <div class="sleep-gap-line"></div>
            <span class="sleep-gap-text">{{ String(gap.sleepStart).padStart(2, '0') }}:00 — {{ String(gap.sleepEnd).padStart(2, '0') }}:00</span>
            <div class="sleep-gap-line"></div>
          </div>
          <div
            v-for="event in events"
            :key="event.id"
            class="day-event"
            :class="{ 'dragging': draggedEvent?.id === event.id, 'is-resizing': isResizing(event.id) }"
            :style="getEventStyle(event)"
            :data-event-id="event.id"
            draggable="true"
            @click.stop="handleEventClick(event)"
            @dragstart="handleDragStart($event, event)"
            @drag="handleDrag($event)"
            @dragend="handleDragEnd"
            @dragover="handleTaskDragOver($event)"
            @drop="handleTaskDrop($event)"
            @mouseenter="hoveredEventId = event.id"
            @mouseleave="hoveredEventId = hoveredEventId === event.id ? null : hoveredEventId"
          >
            <div
              class="event-resize-handle event-resize-handle--top"
              @mousedown.stop.prevent="startResize($event, event, 'top')"
            ></div>
            <div class="event-indicator"></div>
            <div class="event-content">
              <div class="event-title">
                <template v-if="eventAccentMode">
                  <div
                    v-if="event.tagIcon && getTagIconPath(event.tagIcon) && editingTitleEventId !== event.id"
                    class="event-tag-icon-wrapper"
                    :style="{ backgroundColor: event.color || '#4a5568' }"
                    @click.stop="$emit('toggle-tags-panel')"
                  >
                    <img
                      :src="getTagIconPath(event.tagIcon)"
                      class="event-tag-icon"
                    />
                  </div>
                </template>
                <template v-else>
                  <img
                    v-if="event.tagIcon && getTagIconPath(event.tagIcon) && editingTitleEventId !== event.id"
                    :src="getTagIconPath(event.tagIcon)"
                    class="event-tag-icon"
                    @click.stop="$emit('toggle-tags-panel')"
                  />
                </template>
                <template v-if="editingTitleEventId === event.id">
                  <input
                    ref="titleInputRef"
                    v-model="editingTitleValue"
                    class="event-title-input"
                    draggable="true"
                    @mousedown="onTitleInputMouseDown($event, event)"
                    @keydown.enter="saveTitle(event)"
                    @keydown.escape="cancelTitleEdit"
                    @blur="saveTitle(event)"
                  />
                </template>
                <template v-else>
                  <span @click.stop="startEditTitle(event)" class="event-title-text">{{ event.title }}</span>
                </template>
                <div v-if="tagPickerEventId === event.id" class="tag-picker-dropdown" @click.stop>
                  <div class="tag-picker-option" @click="selectTag(event, null)">— нет тега</div>
                  <div
                    v-for="tag in tagsStore.tags"
                    :key="tag.id"
                    class="tag-picker-option"
                    :class="{ active: event.tag_id === tag.id }"
                    @click="selectTag(event, tag.id)"
                  >
                    <span class="tag-picker-color" :style="{ backgroundColor: tag.color }"></span>
                    {{ tag.name }}
                  </div>
                </div>
              </div>
              <div class="event-time">
                <img src="@/assets/icon-clock.svg" alt="clock" class="event-time-icon" />
                {{ formatEventTime(event) }}
              </div>
              <div v-if="event.description" class="event-description">
                <template v-if="editingDescEventId === event.id">
                  <input
                    v-model="editingDescValue"
                    class="event-desc-input"
                    @keydown.enter="saveDesc(event)"
                    @keydown.escape="cancelDescEdit"
                    @blur="saveDesc(event)"
                  />
                </template>
                <template v-else>
                  <span @dblclick.stop="startEditDesc(event)">{{ event.description }}</span>
                </template>
              </div>
              <template v-for="ti in [getVisibleTaskInfo(event)]" :key="'ti'">
              <div v-if="(ti.visible > 0 || (event.eventTasks?.length ?? 0) > 0 || (hoveredEventId === event.id && canShowAddTask(event))) && quickAddEventId !== event.id">
                <div v-if="ti.visible === 0 && (event.eventTasks?.length ?? 0) > 0" class="event-tasks-indicator" @click.stop="$emit('open-event-tasks', event)">
                  <span class="tasks-icon">•</span>
                  <span class="tasks-count">{{ event.completed_task_count || 0 }}/{{ event.eventTasks?.length ?? 0 }} {{ getTaskWord(event.eventTasks?.length ?? 0) }}</span>
                </div>
                <template v-if="ti.visible > 0">
                  <div class="event-tasks-inline">
                    <div v-for="t in (event.eventTasks ?? []).slice(0, ti.visible)" :key="t.id" class="event-task-item">
                      <span class="event-task-checkbox" :class="{ checked: t.completed }" @click.stop="toggleTaskInline(t, event)">
                        <span v-if="t.completed">✓</span>
                      </span>
                      <span class="event-task-title" :class="{ done: t.completed }">{{ t.title }}</span>
                    </div>
                  </div>
                  <div v-if="ti.remaining > 0" class="event-tasks-more" @click.stop="$emit('open-event-tasks', event)">
                    +{{ ti.remaining }}
                  </div>
                  <div v-if="ti.remaining === 0 && canShowProgressBar(event)" class="event-tasks-progress">
                    <div class="event-progress-bar-bg">
                      <div class="event-progress-bar-fill" :style="{ width: getProgressPercent(event) + '%' }"></div>
                    </div>
                  </div>
                </template>
                <div v-if="(hoveredEventId === event.id || activeAddTaskEventId === event.id) && canShowAddTask(event)" class="event-add-task" @click.stop>
                  <input
                    v-model="addTaskTitle"
                    class="event-add-task-input"
                    placeholder="+ задача"
                    @focus="activeAddTaskEventId = event.id"
                    @keydown.enter="submitAddTask(event)"
                    @keydown.escape="cancelAddTask"
                    @blur="handleAddTaskBlur"
                  />
                </div>
              </div>
              <div v-if="quickAddEventId === event.id" class="event-quick-add" @click.stop>
                <input
                  v-model="quickAddTitle"
                  class="event-quick-add-input"
                  placeholder="+ задача"
                  @keydown.enter="submitQuickAdd(event)"
                  @keydown.escape="cancelQuickAdd"
                  @blur="cancelQuickAdd"
                />
              </div>
              </template>
            </div>
            <span 
              v-if="showTaskBadge(event)" 
              class="event-task-badge" 
              @click.stop="$emit('open-event-tasks', event)"
              :title="'Задачи: ' + (event.eventTasks?.length ?? 0)"
            >
              {{ event.eventTasks?.length ?? 0 }}
            </span>
            <button 
              v-show="editingTitleEventId !== event.id"
              class="event-star-btn"
              :class="{ 'is-important': event.is_important }"
              @click.stop="$emit('event-toggle-important', event)"
              :title="event.is_important ? 'Убрать важность' : 'Отметить как важное'"
            >
              {{ event.is_important ? '★' : '☆' }}
            </button>
            <button
              v-show="editingTitleEventId !== event.id"
              class="event-quick-add-btn"
              @click.stop="toggleQuickAdd(event)"
              title="Добавить задачу"
            >+</button>
            <div
              class="event-resize-handle event-resize-handle--bottom"
              @mousedown.stop.prevent="startResize($event, event, 'bottom')"
            ></div>
          </div>
          
          <!-- Selection overlay for drag-to-create -->
          <div
            v-if="selHeight > 0"
            class="selection-overlay"
            :style="{ top: selTop + 'px', height: selHeight + 'px' }"
            @mousedown.stop
          >
            <input
              v-if="showCreateInput"
              ref="createTitleInput"
              v-model="createTitle"
              class="create-event-input"
              placeholder="Название события"
              @keydown.enter="createEvent"
              @keydown.escape="cancelSelection"
              @blur="submitCreate"
              @click.stop
            />
          </div>

          <!-- Current Time Line (only for today) -->
          <div 
            v-if="isCurrentDay()"
            class="current-time-line"
            :style="currentTimeLineStyle"
          >
            <div class="current-time-dot"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import { getContrastColors } from '@/utils/color'
import { useTagsStore } from '@/stores/tags'
const tagsStore = useTagsStore()

dayjs.locale('ru')

const iconModules = import.meta.glob<{ default: string }>('../../assets/icon/*.svg', { query: '?url', import: 'default', eager: true })

const getTagIconPath = (iconName: string): string => {
  for (const [path, url] of Object.entries(iconModules)) {
    if (path.includes(`/${iconName}.svg`) || path.includes(`/${iconName}`)) {
      return (url as unknown as string)
    }
  }
  return ''
}

interface EventTask {
  id: string
  title: string
  description?: string
  completed: boolean
}

interface CalendarEvent {
  id: string | number
  title: string
  description?: string
  start: string
  end: string
  location?: string
  priority?: string
  color?: string
  tagIcon?: string
  tag_id?: string
  task_ids?: string[]
  task_count?: number
  completed_task_count?: number
  is_important?: boolean
  eventTasks?: EventTask[]
}

const props = defineProps<{
  currentDay: dayjs.Dayjs
  events: CalendarEvent[]
  dayStartHour: number
  dayEndHour: number
  eventAccentMode: boolean
  hourHeight: number
  sleepMode: boolean
  sleepStartHour: number
  sleepEndHour: number
}>()

const emit = defineEmits<{
  (e: 'prev-day'): void
  (e: 'next-day'): void
  (e: 'go-today'): void
  (e: 'hour-click', data: { hour: number; date: dayjs.Dayjs }): void
  (e: 'open-event', event: CalendarEvent): void
  (e: 'open-event-tasks', event: CalendarEvent): void
  (e: 'event-move-to-next-week', event: CalendarEvent): void
  (e: 'event-drop', data: { event: CalendarEvent; newDate: string; newStart: string; newEnd: string }): void
  (e: 'event-copy', data: { event: CalendarEvent; newDate: string; newStart: string; newEnd: string }): void
  (e: 'task-drop-to-event', data: { task: any; event: CalendarEvent }): void
  (e: 'tag-drop-to-event', data: { tag: any; event: CalendarEvent }): void
  (e: 'task-drop-to-day', data: { task: any; time: dayjs.Dayjs }): void
  (e: 'category-drop-to-day', data: { categoryId: string; categoryTitle: string; time: dayjs.Dayjs }): void
  (e: 'event-toggle-important', event: CalendarEvent): void
  (e: 'create-event', data: { date: string; startTime: string; endTime: string; title: string }): void
  (e: 'event-update', data: { event: CalendarEvent; changes: Partial<CalendarEvent> }): void
  (e: 'add-task-to-event', data: { event: CalendarEvent; title: string }): void
  (e: 'toggle-tags-panel'): void
}>()

// Focus mode state
const focusMode = ref(false)

const toggleFocusMode = () => {
  focusMode.value = !focusMode.value
}

// Drag and drop state
const draggedEvent = ref<CalendarEvent | null>(null)
const dragGhost = ref<HTMLElement | null>(null)
const dragOffsetX = ref(0)
const dragOffsetY = ref(0)
const isAltPressed = ref(false)

// Resize state
const resizingEventId = ref<string | number | null>(null)
const resizeStartY = ref(0)
const resizeDirection = ref<'bottom' | 'top' | null>(null)
const resizeOriginalEnd = ref<dayjs.Dayjs | null>(null)
const resizeNewEnd = ref<dayjs.Dayjs | null>(null)
const resizeOriginalStart = ref<dayjs.Dayjs | null>(null)
const resizeNewStart = ref<dayjs.Dayjs | null>(null)
const resizeEvent = ref<CalendarEvent | null>(null)

const isResizing = (eventId: string | number) => resizingEventId.value === eventId

// Hover and add-task state
const hoveredEventId = ref<string | number | null>(null)
const addTaskTitle = ref('')
const activeAddTaskEventId = ref<string | number | null>(null)

// Quick add state
const quickAddEventId = ref<string | number | null>(null)
const quickAddTitle = ref('')

const startResize = (e: MouseEvent, event: CalendarEvent, direction: 'bottom' | 'top') => {
  e.stopPropagation()
  e.preventDefault()

  resizingEventId.value = event.id
  resizeStartY.value = e.clientY
  resizeDirection.value = direction
  resizeOriginalEnd.value = dayjs(event.end)
  resizeOriginalStart.value = dayjs(event.start)
  resizeEvent.value = event

  document.addEventListener('pointermove', onResizeMove)
  document.addEventListener('pointerup', onResizeEnd)
}

const onResizeMove = (e: PointerEvent) => {
  if (!resizeEvent.value) return

  const deltaY = e.clientY - resizeStartY.value
  const deltaMinutes = (deltaY / props.hourHeight) * 60

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

const onResizeEnd = () => {
  document.removeEventListener('pointermove', onResizeMove)
  document.removeEventListener('pointerup', onResizeEnd)

  if (resizeEvent.value) {
    const event = resizeEvent.value
    if (resizeDirection.value === 'top' && resizeNewStart.value) {
      const startISO = resizeNewStart.value.toISOString()
      const dayStart = dayjs(event.start).startOf('day')
      emit('event-drop', {
        event,
        newDate: dayStart.format('YYYY-MM-DD'),
        newStart: startISO,
        newEnd: event.end
      })
    } else if (resizeDirection.value === 'bottom' && resizeNewEnd.value) {
      const endISO = resizeNewEnd.value.toISOString()
      const dayStart = dayjs(event.start).startOf('day')
      emit('event-drop', {
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
const scrollContainerRef = ref<HTMLElement | null>(null)

// Auto-scroll during drag
const SCROLL_THRESHOLD = 60
const SCROLL_SPEED = 15
let autoScrollInterval: ReturnType<typeof setInterval> | null = null
let currentScrollDir: 'up' | 'down' | null = null

// ========== Drag-to-create selection ==========
const selTop = ref(0)
const selHeight = ref(0)
const isDragging = ref(false)
const hasMoved = ref(false)
const showCreateInput = ref(false)
const createTitle = ref('')
let selStartY = 0
const createTitleInput = ref<HTMLInputElement | null>(null)

let removeMouseListeners: (() => void) | null = null

// Current time for red line
const currentTime = ref(dayjs())
let timeInterval: ReturnType<typeof setInterval> | null = null

const hours = computed(() => {
  if (props.sleepMode) {
    return Array.from({ length: 24 }, (_, i) => i).filter(h => h < props.sleepStartHour || h >= props.sleepEndHour)
  }
  return Array.from({ length: props.dayEndHour - props.dayStartHour }, (_, i) => i + props.dayStartHour)
})

const calendarHeight = computed(() => {
  if (props.sleepMode) {
    return (24 - (props.sleepEndHour - props.sleepStartHour)) * props.hourHeight
  }
  const totalHours = props.dayEndHour - props.dayStartHour
  return totalHours * props.hourHeight
})

const sleepGaps = computed(() => {
  if (!props.sleepMode) return []
  const h = hours.value
  const gaps = []
  for (let i = 1; i < h.length; i++) {
    if (h[i] - h[i-1] > 1) {
      gaps.push({
        sleepStart: h[i-1] + 1,
        sleepEnd: h[i],
        top: i * props.hourHeight
      })
    }
  }
  return gaps
})

const toVisibleMinutes = (minutes: number): number => {
  if (!props.sleepMode) return minutes
  const sleepStartMin = props.sleepStartHour * 60
  const sleepDuration = (props.sleepEndHour - props.sleepStartHour) * 60
  if (minutes <= sleepStartMin) return minutes
  if (minutes >= props.sleepEndHour * 60) return minutes - sleepDuration
  return sleepStartMin
}

const handleRowClick = (hour: number) => {
  emit('hour-click', { hour, date: props.currentDay })
}

const handleDragStart = (event: DragEvent, calendarEvent: CalendarEvent) => {
  draggedEvent.value = calendarEvent
  isAltPressed.value = event.altKey

  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = event.altKey ? 'copy' : 'move'
    event.dataTransfer.setData('text/plain', JSON.stringify(calendarEvent))
    event.dataTransfer.setData('application/x-alt-drag', String(event.altKey))

    const transparentImg = new Image()
    transparentImg.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
    event.dataTransfer.setDragImage(transparentImg, 0, 0)
  }

  const target = event.target as HTMLElement
  const eventBlock = target.closest('.day-event') as HTMLElement
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

const handleDrag = (event: DragEvent) => {
  if (dragGhost.value) {
    dragGhost.value.style.left = (event.clientX - dragOffsetX.value) + 'px'
    dragGhost.value.style.top = (event.clientY - dragOffsetY.value) + 'px'
  }
}

const handleDragEnd = () => {
  draggedEvent.value = null
  isAltPressed.value = false
  dragOffsetX.value = 0
  dragOffsetY.value = 0

  if (dragGhost.value) {
    dragGhost.value.remove()
    dragGhost.value = null
  }
}

const handleTaskDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

const handleTaskDrop = (event: DragEvent) => {
  event.preventDefault()
  if (draggedEvent.value) return
  event.stopPropagation()

  try {
    const droppedData = JSON.parse(event.dataTransfer?.getData('text/plain') || '{}')
    
    if (droppedData._tag) {
      const targetElement = event.target as HTMLElement
      const eventBlock = targetElement.closest('.day-event')
      
      if (eventBlock) {
        const eventId = eventBlock.getAttribute('data-event-id')
        const targetEvent = props.events.find(e => String(e.id) === eventId)
        
        if (targetEvent) {
          emit('tag-drop-to-event', { tag: droppedData, event: targetEvent })
        }
      }
    } else if (droppedData.id && droppedData.title) {
      const targetElement = event.target as HTMLElement
      const eventBlock = targetElement.closest('.day-event')
      
      if (eventBlock) {
        const eventId = eventBlock.getAttribute('data-event-id')
        const targetEvent = props.events.find(e => String(e.id) === eventId)
        
        if (targetEvent) {
          emit('task-drop-to-event', { task: droppedData, event: targetEvent })
        }
      }
    }
  } catch (error) {
    console.error('Error parsing task data:', error)
  }
}

// ========== Grid-level drag over/drop for event movement ==========
const getCalendarGrid = (): HTMLElement | null => {
  return scrollContainerRef.value
}

const startAutoScroll = (dir: 'up' | 'down') => {
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

const stopAutoScroll = () => {
  if (autoScrollInterval) {
    clearInterval(autoScrollInterval)
    autoScrollInterval = null
  }
}

const handleGridDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = draggedEvent.value ? 'move' : 'copy'
  }

  const grid = getCalendarGrid()
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

const handleGridDrop = (event: DragEvent) => {
  event.preventDefault()
  stopAutoScroll()
  currentScrollDir = null

  const grid = getCalendarGrid()
  if (!grid) return
  const rect = grid.getBoundingClientRect()
  const dropY = event.clientY - rect.top
  const slotIndex = Math.floor(dropY / props.hourHeight)
  const rawMinutes = Math.floor((dropY % props.hourHeight) / props.hourHeight * 60)
  const minutes = Math.round(rawMinutes / 10) * 10

  let hour: number
  if (props.sleepMode) {
    const visibleHours = Array.from({ length: 24 }, (_, i) => i).filter(h => h < props.sleepStartHour || h >= props.sleepEndHour)
    hour = visibleHours[slotIndex] ?? 0
  } else {
    hour = slotIndex + props.dayStartHour
  }
  const dropTime = props.currentDay.hour(hour).minute(minutes)

  if (draggedEvent.value) {
    const eventData = draggedEvent.value
    const isCopy = event.altKey || isAltPressed.value

    const originalStart = dayjs(eventData.start)
    const originalEnd = dayjs(eventData.end)
    const duration = originalEnd.diff(originalStart, 'minute')

    const newStart = dropTime
    const newEnd = newStart.add(duration, 'minute')

    if (isCopy) {
      emit('event-copy', {
        event: eventData,
        newDate: props.currentDay.format('YYYY-MM-DD'),
        newStart: newStart.toISOString(),
        newEnd: newEnd.toISOString()
      })
    } else {
      emit('event-drop', {
        event: eventData,
        newDate: props.currentDay.format('YYYY-MM-DD'),
        newStart: newStart.toISOString(),
        newEnd: newEnd.toISOString()
      })
    }
  } else {
    try {
      const droppedData = JSON.parse(event.dataTransfer?.getData('text/plain') || '{}')
      if (droppedData.type === 'category') {
        emit('category-drop-to-day', {
          categoryId: droppedData.categoryId,
          categoryTitle: droppedData.categoryTitle,
          time: dropTime
        })
      } else if (droppedData.id && droppedData.title) {
        emit('task-drop-to-day', {
          task: droppedData,
          time: dropTime
        })
      }
    } catch {
      // ignore
    }
  }

  draggedEvent.value = null
  isAltPressed.value = false
}

// ========== Drag-to-create selection ==========
const addMouseListeners = () => {
  const onMove = (e: MouseEvent) => {
    if (!isDragging.value) return
    hasMoved.value = true

    const grid = getCalendarGrid()
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

const removeListeners = () => {
  if (removeMouseListeners) {
    removeMouseListeners()
    removeMouseListeners = null
  }
}

const startSelection = (event: MouseEvent) => {
  if ((event.target as HTMLElement).closest('.day-event')) return
  if ((event.target as HTMLElement).closest('.event-star-btn')) return
  const grid = getCalendarGrid()
  if (!grid) return
  const rect = grid.getBoundingClientRect()
  selStartY = Math.max(0, Math.min(event.clientY - rect.top, rect.height - 1))

  isDragging.value = true
  hasMoved.value = false
  showCreateInput.value = false
  createTitle.value = ''
  selTop.value = selStartY
  selHeight.value = 0

  addMouseListeners()
}

const getTimeFromPixel = (pixelY: number): { hour: number; minute: number } => {
  const slotIndex = Math.floor(pixelY / props.hourHeight)
  const offsetMin = Math.round(((pixelY % props.hourHeight) / props.hourHeight) * 60 / 10) * 10

  if (props.sleepMode) {
    const visibleHours = Array.from({ length: 24 }, (_, i) => i).filter(h => h < props.sleepStartHour || h >= props.sleepEndHour)
    const hour = visibleHours[slotIndex] ?? 0
    return { hour, minute: offsetMin }
  }

  const hour = slotIndex + props.dayStartHour
  return { hour, minute: offsetMin }
}

const createEvent = () => {
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

  emit('create-event', {
    date: props.currentDay.format('YYYY-MM-DD'),
    startTime: fmt(startTime.hour, startTime.minute),
    endTime: fmt(endHour, endMin),
    title: createTitle.value.trim()
  })

  cancelSelection()
}

const cancelSelection = () => {
  selTop.value = 0
  selHeight.value = 0
  showCreateInput.value = false
  createTitle.value = ''
}

const submitCreate = () => {
  if (createTitle.value.trim()) {
    createEvent()
  } else {
    cancelSelection()
  }
}

// Get correct word form for task count
const getTaskWord = (count: number): string => {
  const lastTwo = count % 100
  const lastOne = count % 10
  
  if (lastTwo >= 11 && lastTwo <= 14) return 'задач'
  if (lastOne === 1) return 'задача'
  if (lastOne >= 2 && lastOne <= 4) return 'задачи'
  return 'задач'
}

const EVENT_PADDING = 16
const TITLE_H = 26
const TIME_H = 24
const DESC_H = 28
const TASK_H = 26
const TASK_GAP = 2

const PROGRESS_BAR_H = 14
const ADD_TASK_H = 28
const MORE_H = 22

const getCurrentEventTimes = (event: CalendarEvent) => {
  const start = isResizing(event.id) && resizeNewStart.value ? resizeNewStart.value : dayjs(event.start)
  const end = isResizing(event.id) && resizeNewEnd.value ? resizeNewEnd.value : dayjs(event.end)
  return { start, end }
}

const getVisibleTaskInfo = (event: CalendarEvent) => {
  const tasks = event.eventTasks
  if (!tasks || tasks.length === 0) return { visible: 0, remaining: 0, eventHeight: 0 }

  const { start, end } = getCurrentEventTimes(event)
  const duration = end.diff(start, 'minute')
  const eventHeight = Math.max((duration / 60) * props.hourHeight, 30)

  let usedHeight = EVENT_PADDING + TITLE_H + TIME_H
  if (event.description) usedHeight += DESC_H

  const available = eventHeight - usedHeight
  const taskHeight = TASK_H + TASK_GAP
  const availableForTasks = available - MORE_H
  const visible = Math.max(0, Math.floor(availableForTasks / taskHeight))
  const remaining = Math.max(0, tasks.length - visible)

  return { visible, remaining, eventHeight }
}

const canShowProgressBar = (event: CalendarEvent): boolean => {
  const info = getVisibleTaskInfo(event)
  if (info.remaining > 0 || !event.eventTasks?.length || event.eventTasks.length < 5) return false
  const taskHeight = TASK_H + TASK_GAP
  const allTasksHeight = event.eventTasks.length * taskHeight - TASK_GAP
  let usedHeight = EVENT_PADDING + TITLE_H + TIME_H
  if (event.description) usedHeight += DESC_H
  usedHeight += allTasksHeight + MORE_H
  return info.eventHeight - usedHeight >= PROGRESS_BAR_H
}

const showTaskBadge = (event: CalendarEvent): boolean => {
  const info = getVisibleTaskInfo(event)
  return (event.eventTasks?.length ?? 0) > 0 && info.visible === 0
}

const canShowAddTask = (event: CalendarEvent): boolean => {
  const info = getVisibleTaskInfo(event)
  const taskHeight = TASK_H + TASK_GAP
  const visibleTasksHeight = info.visible * taskHeight
  let usedHeight = EVENT_PADDING + TITLE_H + TIME_H
  if (event.description) usedHeight += DESC_H
  usedHeight += visibleTasksHeight + MORE_H
  const remaining = info.eventHeight - usedHeight
  if (info.visible > 0 && info.remaining === 0) {
    return remaining >= PROGRESS_BAR_H + ADD_TASK_H
  }
  return remaining >= ADD_TASK_H
}

const getProgressPercent = (event: CalendarEvent): number => {
  if (!event.eventTasks || event.eventTasks.length === 0) return 0
  const completed = event.eventTasks.filter(t => t.completed).length
  return Math.round((completed / event.eventTasks.length) * 100)
}

const submitAddTask = (event: CalendarEvent) => {
  const title = addTaskTitle.value.trim()
  if (!title) return
  emit('add-task-to-event', { event, title })
  addTaskTitle.value = ''
}

const cancelAddTask = () => {
  addTaskTitle.value = ''
  activeAddTaskEventId.value = null
}

const handleAddTaskBlur = () => {
  if (!addTaskTitle.value.trim()) {
    activeAddTaskEventId.value = null
  }
}

const toggleQuickAdd = (event: CalendarEvent) => {
  if (quickAddEventId.value === event.id) {
    cancelQuickAdd()
  } else {
    quickAddEventId.value = event.id
    quickAddTitle.value = ''
    nextTick(() => {
      const el = document.querySelector('.event-quick-add-input') as HTMLInputElement
      el?.focus()
    })
  }
}

const submitQuickAdd = (event: CalendarEvent) => {
  const title = quickAddTitle.value.trim()
  if (!title) return
  emit('add-task-to-event', { event, title })
  quickAddEventId.value = null
  quickAddTitle.value = ''
}

const cancelQuickAdd = () => {
  quickAddEventId.value = null
  quickAddTitle.value = ''
}

const toggleTaskInline = async (task: EventTask, calendarEvent: CalendarEvent) => {
  try {
    const res = await fetch(`/api/v1/tasks/${task.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed: !task.completed })
    })
    if (res.ok) {
      task.completed = !task.completed
      if (calendarEvent.eventTasks) {
        calendarEvent.completed_task_count = calendarEvent.eventTasks.filter(t => t.completed).length
      }
    }
  } catch (e) {
    console.error('Failed to toggle task:', e)
  }
}

// Check if current day is today
const isCurrentDay = () => {
  return dayjs().isSame(props.currentDay, 'day')
}

// Calculate the position of the current time line
const currentTimeLineStyle = computed(() => {
  const hours = currentTime.value.hour()
  const minutes = currentTime.value.minute()
  const nowMinutes = hours * 60 + minutes

  if (props.sleepMode) {
    const sleepStartMin = props.sleepStartHour * 60
    const sleepEndMin = props.sleepEndHour * 60
    if (nowMinutes >= sleepStartMin && nowMinutes < sleepEndMin) {
      return { display: 'none' }
    }
    const visMin = toVisibleMinutes(nowMinutes)
    const top = (visMin / 60) * props.hourHeight
    return { top: `${top}px` }
  }
  
  const totalMinutes = (hours - props.dayStartHour) * 60 + minutes
  const top = (totalMinutes / 60) * props.hourHeight
  
  return {
    top: `${top}px`
  }
})

// Inline editing state
const editingTitleEventId = ref<string | number | null>(null)
const editingTitleValue = ref('')
const editingDescEventId = ref<string | number | null>(null)
const editingDescValue = ref('')
const tagPickerEventId = ref<string | number | null>(null)
const titleInputRef = ref<HTMLInputElement | null>(null)

const startEditTitle = (event: CalendarEvent) => {
  editingTitleValue.value = event.title
  editingTitleEventId.value = event.id
  nextTick(() => {
    titleInputRef.value?.focus()
    document.addEventListener('mousedown', onDocumentMouseDown)
  })
}

const onDocumentMouseDown = (e: MouseEvent) => {
  if (!editingTitleEventId.value) {
    document.removeEventListener('mousedown', onDocumentMouseDown)
    return
  }
  const input = titleInputRef.value
  if (input && !input.contains(e.target as Node)) {
    cancelTitleEdit()
    document.removeEventListener('mousedown', onDocumentMouseDown)
  }
}

const saveTitle = (event: CalendarEvent) => {
  const val = editingTitleValue.value.trim()
  if (val && val !== event.title) {
    emit('event-update', { event, changes: { title: val } })
  }
  editingTitleEventId.value = null
  document.removeEventListener('mousedown', onDocumentMouseDown)
}

const cancelTitleEdit = () => {
  editingTitleEventId.value = null
  document.removeEventListener('mousedown', onDocumentMouseDown)
}

const onTitleInputMouseDown = (e: MouseEvent, event: CalendarEvent) => {
  if (editingTitleEventId.value !== event.id) return
  const startX = e.clientX
  const startY = e.clientY
  const onMove = (e: MouseEvent) => {
    if (Math.abs(e.clientX - startX) > 3 || Math.abs(e.clientY - startY) > 3) {
      saveTitle(event)
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
    }
  }
  const onUp = () => {
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
  }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

const startEditDesc = (event: CalendarEvent) => {
  editingDescValue.value = event.description || ''
  editingDescEventId.value = event.id
}

const saveDesc = (event: CalendarEvent) => {
  const val = editingDescValue.value.trim()
  if (val !== event.description) {
    emit('event-update', { event, changes: { description: val || '' } })
  }
  editingDescEventId.value = null
}

const cancelDescEdit = () => {
  editingDescEventId.value = null
}

const selectTag = (event: CalendarEvent, tagId: string | null) => {
  const curTagId = event.tag_id || ''
  if (tagId !== curTagId) {
    const tag = tagId ? tagsStore.tags.find(t => t.id === tagId) : null
    emit('event-update', { event, changes: { tag_id: tag?.id || '', color: tag?.color || '' } })
  }
  tagPickerEventId.value = null
}

// Handle event click
const handleEventClick = (_event?: CalendarEvent) => {
  // Modal access removed - inline editing via dblclick
}

const getEventStyle = (event: CalendarEvent) => {
  const start = isResizing(event.id) && resizeNewStart.value ? resizeNewStart.value : dayjs(event.start)
  const end = isResizing(event.id) && resizeNewEnd.value ? resizeNewEnd.value : dayjs(event.end)
  const dayStart = props.currentDay.startOf('day')
  
  let startMinutes = start.diff(dayStart, 'minute')
  const duration = end.diff(start, 'minute')

  if (props.sleepMode) {
    const sleepStartMin = props.sleepStartHour * 60
    const sleepEndMin = props.sleepEndHour * 60
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
    const eventBg = props.eventAccentMode ? '#1a1a1a' : eventColor
    const { text: eventTextColor, textMuted: eventTextMuted, iconFilter: eventIconFilter } = getContrastColors(eventBg)
    const eventStyleExtra: Record<string, string> = {
      '--event-text-color': eventTextColor,
      '--event-text-muted': eventTextMuted,
      '--event-icon-filter': eventIconFilter
    }
    if (props.eventAccentMode) {
      eventStyleExtra['--event-color'] = eventColor
    }

    const totalVisibleHours = 24 - (props.sleepEndHour - props.sleepStartHour)
    const top = (visStart / 60) * props.hourHeight
    const height = Math.max((visDuration / 60) * props.hourHeight, 30)
    const maxTop = totalVisibleHours * props.hourHeight
    const clampedTop = Math.max(0, Math.min(top, maxTop))
    const clampedHeight = Math.min(height, maxTop - clampedTop)

    if (clampedTop >= maxTop || clampedHeight <= 0) {
      return { display: 'none' }
    }

    if (focusMode.value) {
      return {
        top: `${clampedTop}px`,
        height: `${clampedHeight}px`,
        backgroundColor: eventBg,
        position: 'absolute' as const,
        left: '37.5%',
        width: '25%',
        right: 'auto',
        zIndex: 10,
        ...eventStyleExtra
      }
    }

    return {
      top: `${clampedTop}px`,
      height: `${clampedHeight}px`,
      backgroundColor: eventBg,
      position: 'absolute' as const,
      left: '2px',
      right: '2px',
      zIndex: 10,
      ...eventStyleExtra
    }
  }
  
  const eventColor = event.color || '#4a5568'
  const eventBg = props.eventAccentMode ? '#1a1a1a' : eventColor
  const { text: eventTextColor, textMuted: eventTextMuted, iconFilter: eventIconFilter } = getContrastColors(eventBg)
  const eventStyleExtra: Record<string, string> = {
    '--event-text-color': eventTextColor,
    '--event-text-muted': eventTextMuted,
    '--event-icon-filter': eventIconFilter
  }
  if (props.eventAccentMode) {
    eventStyleExtra['--event-color'] = eventColor
  }
  
  const totalDisplayHours = props.dayEndHour - props.dayStartHour
  const offsetMinutes = props.dayStartHour * 60

  if (totalDisplayHours < 24) {
    if (startMinutes < offsetMinutes) {
      startMinutes = offsetMinutes
    } else if (startMinutes >= props.dayEndHour * 60) {
      return { display: 'none' }
    }

    const top = ((startMinutes - offsetMinutes) / 60) * props.hourHeight
    const height = Math.max((duration / 60) * props.hourHeight, 30)
    
    const maxTop = totalDisplayHours * props.hourHeight
    const clampedTop = Math.max(0, Math.min(top, maxTop))
    const clampedHeight = Math.min(height, maxTop - clampedTop)
    
    if (clampedTop >= maxTop || clampedHeight <= 0) {
      return { display: 'none' }
    }
    
    if (focusMode.value) {
      return {
        top: `${clampedTop}px`,
        height: `${clampedHeight}px`,
        backgroundColor: eventBg,
        position: 'absolute' as const,
        left: '37.5%',
        width: '25%',
        right: 'auto',
        zIndex: 10,
        ...eventStyleExtra
      }
    }
    
    return {
      top: `${clampedTop}px`,
      height: `${clampedHeight}px`,
      backgroundColor: eventBg,
      position: 'absolute' as const,
      left: '2px',
      right: '2px',
      zIndex: 10,
      ...eventStyleExtra
    }
  }

  const top = (startMinutes / 60) * props.hourHeight
  const height = Math.max((duration / 60) * props.hourHeight, 30)
  
  const maxTop = 24 * props.hourHeight
  const clampedTop = Math.max(0, Math.min(top, maxTop))
  const clampedHeight = Math.min(height, maxTop - clampedTop)
  
  if (clampedTop >= maxTop || clampedHeight <= 0) {
    return { display: 'none' }
  }
  
  if (focusMode.value) {
    return {
      top: `${clampedTop}px`,
      height: `${clampedHeight}px`,
      backgroundColor: eventBg,
      position: 'absolute' as const,
      left: '37.5%',
      width: '25%',
      right: 'auto',
      zIndex: 10,
      ...eventStyleExtra
    }
  }
  
  return {
    top: `${clampedTop}px`,
    height: `${clampedHeight}px`,
    backgroundColor: eventBg,
    position: 'absolute' as const,
    left: '2px',
    right: '2px',
    zIndex: 10,
    ...eventStyleExtra
  }
}

const formatEventTime = (event: CalendarEvent) => {
  const start = isResizing(event.id) && resizeNewStart.value ? resizeNewStart.value : dayjs(event.start)
  const end = isResizing(event.id) && resizeNewEnd.value ? resizeNewEnd.value : dayjs(event.end)
  return `${start.format('HH:mm')} - ${end.format('HH:mm')}`
}

// Lifecycle hooks
onMounted(() => {
  timeInterval = setInterval(() => {
    currentTime.value = dayjs()
  }, 60000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  stopAutoScroll()
  currentScrollDir = null
  removeListeners()
})
</script>

<style scoped>
.day-calendar {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.day-header {
  padding: 20px;
  border-bottom: 1px solid #80808021;
  flex-shrink: 0;
  background-color: var(--bg-primary);
  z-index: 10;
}

.day-scroll-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.day-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.day-info {
  display: flex;
  flex-direction: column;
}

.day-weekday {
  font-size: 38px;
  font-weight: bold;
  margin: 0;
  text-transform: capitalize;
}

.day-date {
  font-size: 19px;
  color: #888;
  margin: 5px 0 0;
  font-weight: 400;
}

.day-nav {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-btn1 {
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 32px;
  cursor: pointer;
  font-weight: bold;
  padding: 5px 15px;
}

.today-btn {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 6px;
  transition: background 0.2s;
}

.today-btn:hover {
  background: #2a2a2a;
}

.focus-btn {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s;
}

.focus-btn:hover {
  background: #2a2a2a;
}

.focus-btn.active {
  background: #4a5568;
  border-color: #4a5568;
}

.day-grid {
  display: flex;
  flex-direction: column;
  position: relative;
}

.day-hour-row {
  display: flex;
  border-bottom: 1px solid var(--bg-tertiary);
}

.hour-label {
  width: 60px;
  padding: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #666;
  flex-shrink: 0;
  border-right: 1px solid var(--bg-tertiary);
}

.hour-events {
  flex: 1;
  cursor: pointer;
}

.hour-events:hover {
  background-color: rgba(255,255,255, 0.03);
}

.events-container {
  position: absolute;
  top: 0;
  left: 60px;
  right: 0;
  pointer-events: none;
  z-index: 1;
}

.day-event {
  position: absolute;
  left: 2px;
  right: 2px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--event-text-color, #ffffff);
  overflow: hidden;
  pointer-events: auto;
  display: flex;
  transition: transform 0.1s;
}

.day-event:hover {
  transform: scale(1.02);
}

.day-event.is-resizing {
  transition: top 0.08s ease, height 0.08s ease;
  transform: none;
}

.day-event.dragging {
  cursor: grabbing;
  z-index: 100;
}

.event-indicator {
  width: 6px;
  border-radius: 10px;
  background-color: var(--event-text-muted, rgba(255, 255, 255, 0.7));
  margin: 1px 8px 1px 0;
  flex-shrink: 0;
  opacity: 0.9;
}

.event-content {
  flex: 1;
  overflow: visible;
  pointer-events: none;
}

.event-title,
.event-time {
  padding-right: 0;
}

.event-content * {
  pointer-events: none;
}

.event-time {
  font-size: 18px;
  font-weight: 500;
  color: var(--event-text-muted, rgba(255, 255, 255, 0.8));
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-time-icon {
  width: 20px;
  height: 20px;
  filter: var(--event-icon-filter, none);
}

.event-title {
  font-size: 20px;
  font-weight: 600;
  position: relative;
}

.event-tag-icon-wrapper,
.event-tag-icon {
  float: left;
  margin-left: -3px;
  margin-right: 8px;
  margin-top: 3px;
  flex-shrink: 0;
  pointer-events: auto;
}

.event-title-text {
  cursor: text;
  pointer-events: auto;
  min-width: 0;
}

.event-tag-icon-wrapper,
.event-tag-icon {
  flex-shrink: 0;
  margin-top: 3px;
  pointer-events: auto;
}

.event-tag-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  filter: var(--event-icon-filter, none);
  pointer-events: auto;
}

.event-description {
  font-size: 16px;
  color: var(--event-text-muted, rgba(255, 255, 255, 0.8));
  margin-top: 6px;
  line-height: 1.4;
}

.event-tasks-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
  pointer-events: auto;
}

.event-tasks-indicator:hover {
  background: rgba(0, 0, 0, 0.5);
}

.tasks-icon {
  color: var(--event-text-muted, rgba(255, 255, 255, 0.8));
  font-size: 11px;
  line-height: 1;
}

.tasks-count {
  color: var(--event-text-muted, rgba(255, 255, 255, 0.8));
  font-size: 11px;
  font-weight: 600;
}

.event-tasks-inline {
  margin-top: 4px;
}

.event-task-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  margin-top: 2px;
  cursor: pointer;
  font-size: 16px;
  line-height: 1.4;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}

.event-task-checkbox {
  pointer-events: auto;
}

.event-task-item:first-child {
  margin-top: 0;
}

.event-task-checkbox {
  width: 13px;
  height: 13px;
  border: 1px solid #888;
  border-radius: 3px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: #ffffff;
}

.event-task-checkbox.checked {
  border-color: #ffffff;
}

.event-task-title {
  color: var(--event-text-color, #ffffff);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
}

.event-task-title.done {
  text-decoration: line-through;
  opacity: 0.6;
}

.event-tasks-progress {
  margin-top: 4px;
  padding: 0 6px;
}

.event-progress-bar-bg {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  overflow: hidden;
}

.event-progress-bar-fill {
  height: 100%;
  background: #ffffff;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.event-tasks-more {
  margin-top: 3px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 700;
  color: var(--event-text-muted, rgba(255, 255, 255, 0.7));
  background: rgba(0, 0, 0, 0.25);
  border-radius: 4px;
  cursor: pointer;
  pointer-events: auto;
  text-align: center;
  transition: background 0.2s;
}

.event-tasks-more:hover {
  background: rgba(0, 0, 0, 0.45);
}

.event-add-task {
  margin-top: 3px;
  pointer-events: auto;
}

.event-add-task-input {
  width: 100%;
  padding: 3px 6px;
  font-size: 12px;
  color: var(--event-text-color, #ffffff);
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  outline: none;
  box-sizing: border-box;
  pointer-events: auto;
}

.event-add-task-input::placeholder {
  color: var(--event-text-muted, rgba(255, 255, 255, 0.5));
}

.event-add-task-input:focus {
  border-color: rgba(255, 255, 255, 0.4);
}

/* Event Star Button */
.event-star-btn {
  position: absolute;
  top: 4px;
  right: 6px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  font-size: 20px;
  color: #aaa;
  z-index: 14;
  opacity: 0;
  transition: opacity 0.2s, transform 0.2s;
  pointer-events: auto;
  line-height: 1;
}

.event-star-btn.is-important {
  opacity: 1;
  color: #f59e0b;
}

.day-event:hover .event-star-btn {
  opacity: 1;
}

.event-star-btn:hover {
  opacity: 0.8;
  transform: scale(1.2);
}

/* Event Task Badge */
.event-task-badge {
  position: absolute;
  top: 0px;
  right: 6px;
  min-width: 18px;
  height: 18px;
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
  font-size: 11px;
  font-weight: 700;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 16;
  cursor: pointer;
  pointer-events: auto;
  padding: 0 4px;
  box-sizing: border-box;
  line-height: 1;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.event-task-badge:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: scale(1.15);
}

/* Event Quick Add Button */
.event-quick-add-btn {
  position: absolute;
  top: 30px;
  right: 6px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px 6px;
  font-size: 18px;
  font-weight: 600;
  color: #aaa;
  opacity: 0;
  pointer-events: auto;
  transition: opacity 0.2s, transform 0.2s, color 0.2s;
  z-index: 15;
  line-height: 1;
}

.day-event:hover .event-quick-add-btn {
  opacity: 1;
}

.event-quick-add-btn:hover {
  opacity: 0.8;
  transform: scale(1.3);
  color: #ffffff;
}

/* When badge exists: shift star/plus below badge */
.event-task-badge ~ .event-star-btn {
  top: 20px;
}

.event-task-badge ~ .event-star-btn.is-important {
  opacity: 1;
}

.event-task-badge ~ .event-quick-add-btn {
  top: 46px;
}

/* Event Quick Add Input */
.event-quick-add {
  margin-top: 3px;
  pointer-events: auto;
}

.event-quick-add-input {
  width: 100%;
  padding: 3px 6px;
  font-size: 12px;
  color: var(--event-text-color, #ffffff);
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  outline: none;
  box-sizing: border-box;
  pointer-events: auto;
}

.event-quick-add-input::placeholder {
  color: var(--event-text-muted, rgba(255, 255, 255, 0.5));
}

.event-quick-add-input:focus {
  border-color: rgba(255, 255, 255, 0.4);
}

/* Current Time Line */
.current-time-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #ff4444;
  z-index: 20;
  pointer-events: none;
}

.current-time-dot {
  position: absolute;
  left: -5px;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  background-color: #ff4444;
  border-radius: 50%;
}

/* Selection overlay for drag-to-create */
.selection-overlay {
  position: absolute;
  left: 2px;
  right: 2px;
  z-index: 25;
  background: rgba(255, 255, 255, 0.06);
  border: 2px dashed #888;
  border-radius: 8px;
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  padding: 4px;
}

.create-event-input {
  width: 100%;
  background: #111;
  border: 1px solid #555;
  border-radius: 6px;
  color: #fff;
  font-size: 13px;
  padding: 6px 8px;
  outline: none;
  font-family: inherit;
}

.create-event-input::placeholder {
  color: #666;
}

.create-event-input:focus {
  border-color: #888;
}

.event-resize-handle {
  position: absolute;
  left: 0;
  right: 0;
  height: 10px;
  cursor: ns-resize;
  z-index: 20;
  pointer-events: auto;
}

.event-resize-handle--top {
  top: 0;
}

.event-resize-handle--bottom {
  bottom: 0;
}

.event-tag-icon-wrapper {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.event-tag-icon-wrapper .event-tag-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  filter: var(--event-icon-filter, brightness(0) invert(1));
}

.event-title {
  pointer-events: auto;
}

.event-title-text {
  cursor: text;
  pointer-events: auto;
  flex: 1;
  min-width: 0;
}

.event-title-input {
  pointer-events: auto;
}

.event-desc-input {
  pointer-events: auto;
}

.event-description {
  pointer-events: auto;
}

.event-title-input {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: inherit;
  font: inherit;
  padding: 2px 6px;
  width: 100%;
  outline: none;
}

.event-desc-input {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: inherit;
  font: inherit;
  padding: 2px 6px;
  width: 100%;
  outline: none;
}

.event-title-input:focus,
.event-desc-input:focus {
  border-color: rgba(255, 255, 255, 0.4);
}

.tag-picker-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 50;
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 6px;
  padding: 4px 0;
  max-height: 180px;
  overflow-y: auto;
}

.tag-picker-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 13px;
  color: #ddd;
  transition: background 0.15s;
}

.tag-picker-option:hover {
  background: rgba(255, 255, 255, 0.1);
}

.tag-picker-option.active {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.tag-picker-color {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Sleep gap marker */
.sleep-gap-marker {
  position: absolute;
  left: 0;
  right: 0;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  pointer-events: none;
  z-index: 5;
  margin-top: -14px;
}

.sleep-gap-line {
  flex: 1;
  height: 2px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 1px;
}

.sleep-gap-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.25);
  white-space: nowrap;
  font-weight: 500;
  letter-spacing: 0.3px;
  padding: 0 4px;
}
</style>
