<template>
  <div class="week-view">
    <!-- Calendar Grid -->
    <div class="calendar-grid">
      <div class="time-column">
        <div
          v-for="hour in hours"
          :key="hour"
          class="time-slot"
          :style="{ height: hourHeight + 'px' }"
        >
          {{ formatTime(hour) }}
        </div>
      </div>

      <div class="days-container" :style="{ minHeight: calendarHeight + 'px' }">
        <div
          v-for="day in weekDays"
          :key="day.date"
          class="day-column"
          :class="{
            'current-day': isCurrentDay(day),
            'drag-over': dragOverDay === day.date
          }"
          :data-day-date="day.date"
          :style="{ minHeight: calendarHeight + 'px' }"
          @mousedown="startSelection($event, day)"
          @dragover="handleDragOver($event, day)"
          @dragleave="handleDragLeave"
          @drop="handleDrop($event, day)"
        >
          <div
            v-for="hour in hours"
            :key="hour"
            class="hour-slot"
            :style="{ height: hourHeight + 'px' }"
          ></div>
          
          <!-- Selection overlay for drag-to-create -->
          <div
            v-if="selDay === day.date && selHeight > 0"
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
          <div
            v-for="event in getEventsForDay(day.date)"
            :key="event.id"
            class="event-block"
            :class="{ 'dragging': draggedEvent?.id === event.id, 'is-resizing': isResizing(event.id) }"
            :style="getEventStyle(event, day.date)"
            :data-event-id="event.id"
            draggable="true"
            @click.stop="handleEventClick(event)"
            @dragstart="handleDragStart($event, event)"
            @drag="handleDrag($event)"
            @dragend="handleDragEnd"
            @dragover="handleTaskDragOver($event)"
            @drop="handleTaskDrop($event, day)"
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
                    v-if="event.tagIcon && getTagIconPath(event.tagIcon)"
                    class="event-tag-icon-wrapper"
                    :style="{ backgroundColor: event.color || '#4a5568' }"
                    @dblclick.stop="toggleTagPicker(event)"
                  >
                    <img
                      :src="getTagIconPath(event.tagIcon)"
                      class="event-tag-icon"
                    />
                  </div>
                </template>
                <template v-else>
                  <img
                    v-if="event.tagIcon && getTagIconPath(event.tagIcon)"
                    :src="getTagIconPath(event.tagIcon)"
                    class="event-tag-icon"
                    @dblclick.stop="toggleTagPicker(event)"
                  />
                </template>
                <template v-if="editingTitleEventId === event.id">
                  <input
                    ref="titleInputRef"
                    v-model="editingTitleValue"
                    class="event-title-input"
                    @keydown.enter="saveTitle(event)"
                    @keydown.escape="cancelTitleEdit"
                    @blur="saveTitle(event)"
                  />
                </template>
                <template v-else>
                  <span @dblclick.stop="startEditTitle(event)" class="event-title-text">{{ event.title }}</span>
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
              <template v-for="ti in [getVisibleTaskInfo(event, day.date)]" :key="'ti'">
              <div v-if="(ti.visible > 0 || (event.eventTasks?.length ?? 0) > 0 || (hoveredEventId === event.id && canShowAddTask(event, day.date))) && quickAddEventId !== event.id">
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
                  <div v-if="ti.remaining === 0 && canShowProgressBar(event, day.date)" class="event-tasks-progress">
                    <div class="event-progress-bar-bg">
                      <div class="event-progress-bar-fill" :style="{ width: getProgressPercent(event) + '%' }"></div>
                    </div>
                  </div>
                </template>
                <div v-if="(hoveredEventId === event.id || activeAddTaskEventId === event.id) && canShowAddTask(event, day.date)" class="event-add-task" @click.stop>
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
            <button 
              class="event-star-btn"
              :class="{ 'is-important': event.is_important }"
              @click.stop="$emit('event-toggle-important', event)"
              :title="event.is_important ? 'Убрать важность' : 'Отметить как важное'"
            >
              {{ event.is_important ? '★' : '☆' }}
            </button>
            <button 
              class="event-menu-btn"
              @click.stop="$emit('event-move-to-next-week', event)"
              title="Перенести на следующую неделю"
            >
              <img src="@/assets/three-point.svg" alt="menu" />
            </button>
            <button
              class="event-quick-add-btn"
              @click.stop="toggleQuickAdd(event)"
              title="Добавить задачу"
            >+</button>
            <div
              class="event-resize-handle event-resize-handle--bottom"
              @mousedown.stop.prevent="startResize($event, event, 'bottom')"
            ></div>
          </div>
          
          <!-- Current Time Line (only for today) -->
          <div 
            v-if="isCurrentDay(day)"
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
import { computed, ref, onMounted, onUnmounted, nextTick } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import { getContrastColors } from '@/utils/color'
import { useTagsStore } from '@/stores/tags'
const tagsStore = useTagsStore()

dayjs.locale('ru')

const iconModules = import.meta.glob<{ default: string }>('../../assets/icon/*.svg', { query: '?url', import: 'default', eager: true })

const getTagIconPath = (iconName: string): string => {
  // import.meta.glob возвращает ключи в формате /src/assets/icon/filename.svg
  for (const [path, url] of Object.entries(iconModules)) {
    if (path.includes(`/${iconName}.svg`) || path.includes(`/${iconName}`)) {
      return (url as unknown as string)
    }
  }
  return ''
}

interface WeekDay {
  date: string
  shortName: string
  number: number
  fullDate: dayjs.Dayjs
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
  weekDays: WeekDay[]
  events: CalendarEvent[]
  compactMode: boolean
  eventAccentMode: boolean
  inboxPanelOpen: boolean
  hourHeight: number
}>()

const emit = defineEmits<{
  (e: 'day-click', data: { day: WeekDay; dateTime: dayjs.Dayjs }): void
  (e: 'open-event', event: CalendarEvent): void
  (e: 'open-event-tasks', event: CalendarEvent): void
  (e: 'event-drop', data: { event: CalendarEvent; newDate: string; newStart: string; newEnd: string }): void
  (e: 'event-copy', data: { event: CalendarEvent; newDate: string; newStart: string; newEnd: string }): void
  (e: 'event-move-to-next-week', event: CalendarEvent): void
  (e: 'task-drop-to-event', data: { task: any; event: CalendarEvent }): void
  (e: 'tag-drop-to-event', data: { tag: any; event: CalendarEvent }): void
  (e: 'task-drop-to-day', data: { task: any; time: dayjs.Dayjs }): void
  (e: 'category-drop-to-day', data: { categoryId: string; categoryTitle: string; time: dayjs.Dayjs }): void
  (e: 'event-toggle-important', event: CalendarEvent): void
  (e: 'create-event', data: { date: string; startTime: string; endTime: string; title: string }): void
  (e: 'event-update', data: { event: CalendarEvent; changes: Partial<CalendarEvent> }): void
  (e: 'add-task-to-event', data: { event: CalendarEvent; title: string }): void
}>()

// Drag and drop state
const draggedEvent = ref<CalendarEvent | null>(null)
const dragGhost = ref<HTMLElement | null>(null)
const dragOffsetX = ref(0)
const dragOffsetY = ref(0)
const dragOverDay = ref<string | null>(null)
const dragOverTimeout = ref<ReturnType<typeof setTimeout> | null>(null)

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

// Hover and add-task state
const hoveredEventId = ref<string | number | null>(null)
const addTaskTitle = ref('')
const activeAddTaskEventId = ref<string | number | null>(null)

// Quick add state
const quickAddEventId = ref<string | number | null>(null)
const quickAddTitle = ref('')

const isResizing = (eventId: string | number) => resizingEventId.value === eventId

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

// Auto-scroll during drag
const SCROLL_THRESHOLD = 60
const SCROLL_SPEED = 15
let autoScrollInterval: ReturnType<typeof setInterval> | null = null
let currentScrollDir: 'up' | 'down' | null = null

const getCalendarGrid = (): HTMLElement | null => {
  return document.querySelector('.calendar-grid') as HTMLElement
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

const handleDragStart = (event: DragEvent, calendarEvent: CalendarEvent) => {
  draggedEvent.value = calendarEvent
  isAltPressed.value = event.altKey

  // Подавляем нативный ghost и создаём кастомный с анимацией
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = event.altKey ? 'copy' : 'move'
    event.dataTransfer.setData('text/plain', JSON.stringify(calendarEvent))
    event.dataTransfer.setData('application/x-alt-drag', String(event.altKey))

    // Прозрачное изображение 1x1 для скрытия нативного ghost
    const transparentImg = new Image()
    transparentImg.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
    event.dataTransfer.setDragImage(transparentImg, 0, 0)
  }

  // Создаём кастомный ghost с анимацией
  const target = event.target as HTMLElement
  const eventBlock = target.closest('.event-block') as HTMLElement
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

const handleDragEnd = () => {
  draggedEvent.value = null
  dragOverDay.value = null
  isAltPressed.value = false
  dragOffsetX.value = 0
  dragOffsetY.value = 0
  if (dragOverTimeout.value) clearTimeout(dragOverTimeout.value)

  stopAutoScroll()
  currentScrollDir = null

  // Удаляем кастомный ghost
  if (dragGhost.value) {
    dragGhost.value.remove()
    dragGhost.value = null
  }
}

const handleDragOver = (event: DragEvent, day: WeekDay) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = event.altKey ? 'copy' : 'move'
  }
  dragOverDay.value = day.date
  if (dragOverTimeout.value) clearTimeout(dragOverTimeout.value)
  dragOverTimeout.value = setTimeout(() => {
    dragOverDay.value = null
  }, 1000)
}

const handleDragLeave = () => {
  dragOverDay.value = null
  if (dragOverTimeout.value) clearTimeout(dragOverTimeout.value)
}

const handleDrop = (event: DragEvent, day: WeekDay) => {
  event.preventDefault()
  dragOverDay.value = null
  if (dragOverTimeout.value) clearTimeout(dragOverTimeout.value)
  
  try {
    const droppedData = JSON.parse(event.dataTransfer?.getData('text/plain') || '{}')
    
    // Проверяем, это перетаскивание события календаря или задачи/категории из Inbox
    if (draggedEvent.value) {
      // Перетаскивание события календаря
      const eventData = draggedEvent.value
      const isCopy = event.altKey || isAltPressed.value // Проверяем Alt при сбросе
      
      // Calculate the time offset from the original start
      const originalStart = dayjs(eventData.start)
      const originalEnd = dayjs(eventData.end)
      const duration = originalEnd.diff(originalStart, 'minute')
      
      // Get the time from the drop position (корректируем на половину высоты, т.к. курсор по центру ghost)
      const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
      const dropY = event.clientY - rect.top - dragOffsetY.value
      const slotIndex = Math.floor(dropY / props.hourHeight)
      const rawMinutes = Math.floor((dropY % props.hourHeight) / props.hourHeight * 60)
      const minutes = Math.round(rawMinutes / 10) * 10
      
      const hour = props.compactMode ? slotIndex + 7 : slotIndex
      
      const newStart = day.fullDate.hour(hour).minute(minutes)
      const newEnd = newStart.add(duration, 'minute')
      
      if (isCopy) {
        emit('event-copy', {
          event: eventData,
          newDate: day.date,
          newStart: newStart.toISOString(),
          newEnd: newEnd.toISOString()
        })
      } else {
        emit('event-drop', {
          event: eventData,
          newDate: day.date,
          newStart: newStart.toISOString(),
          newEnd: newEnd.toISOString()
        })
      }
    } else if (droppedData.type === 'category') {
      const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
      const dropY = event.clientY - rect.top
      const slotIndex = Math.floor(dropY / props.hourHeight)
      const rawMinutes = Math.floor((dropY % props.hourHeight) / props.hourHeight * 60)
      const minutes = Math.round(rawMinutes / 10) * 10
      
      const hour = props.compactMode ? slotIndex + 7 : slotIndex
      const dropTime = day.fullDate.hour(hour).minute(minutes)
      
      emit('category-drop-to-day', {
        categoryId: droppedData.categoryId,
        categoryTitle: droppedData.categoryTitle,
        time: dropTime
      })
    } else if (droppedData.id && droppedData.title) {
      const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
      const dropY = event.clientY - rect.top
      const slotIndex = Math.floor(dropY / props.hourHeight)
      const rawMinutes = Math.floor((dropY % props.hourHeight) / props.hourHeight * 60)
      const minutes = Math.round(rawMinutes / 10) * 10
      
      const hour = props.compactMode ? slotIndex + 7 : slotIndex
      const dropTime = day.fullDate.hour(hour).minute(minutes)
      
      emit('task-drop-to-day', {
        task: droppedData,
        time: dropTime
      })
    }
  } catch (error) {
    console.error('Error parsing drop data:', error)
  }
  
  draggedEvent.value = null
  isAltPressed.value = false
}

// Task drag and drop handlers
const handleTaskDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

const handleTaskDrop = (event: DragEvent, _day: WeekDay) => {
  event.preventDefault()
  event.stopPropagation()
  
  try {
    const droppedData = JSON.parse(event.dataTransfer?.getData('text/plain') || '{}')
    
    if (droppedData._tag) {
      const targetElement = event.target as HTMLElement
      const eventBlock = targetElement.closest('.event-block')
      
      if (eventBlock) {
        const eventId = eventBlock.getAttribute('data-event-id')
        const targetEvent = props.events.find(e => String(e.id) === eventId)
        
        if (targetEvent) {
          emit('tag-drop-to-event', { tag: droppedData, event: targetEvent })
        }
      }
    } else if (droppedData.type === 'category') {
      // Находим событие, над которым была сброшена категория
      const targetElement = event.target as HTMLElement
      const eventBlock = targetElement.closest('.event-block')
      
      if (eventBlock) {
        // Находим событие по его ID
        const eventId = eventBlock.getAttribute('data-event-id')
        const targetEvent = props.events.find(e => String(e.id) === eventId)
        
        if (targetEvent) {
          emit('task-drop-to-event', { task: droppedData, event: targetEvent })
        }
      }
    } else if (droppedData.id && droppedData.title) {
      // Находим событие, над которым была сброшена задача
      const targetElement = event.target as HTMLElement
      const eventBlock = targetElement.closest('.event-block')
      
      if (eventBlock) {
        // Находим событие по его ID
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

// Get correct word form for task count
const getTaskWord = (count: number): string => {
  const lastTwo = count % 100
  const lastOne = count % 10
  
  if (lastTwo >= 11 && lastTwo <= 14) return 'задач'
  if (lastOne === 1) return 'задача'
  if (lastOne >= 2 && lastOne <= 4) return 'задачи'
  return 'задач'
}

const EVENT_PADDING = 10
const TITLE_H = 22
const TIME_H = 20
const DESC_H = 20
const TASK_H = 22
const TASK_GAP = 2

const PROGRESS_BAR_H = 14
const ADD_TASK_H = 28
const MORE_H = 22

const getCurrentEventTimes = (event: CalendarEvent) => {
  const start = isResizing(event.id) && resizeNewStart.value ? resizeNewStart.value : dayjs(event.start)
  const end = isResizing(event.id) && resizeNewEnd.value ? resizeNewEnd.value : dayjs(event.end)
  return { start, end }
}

const getVisibleTaskInfo = (event: CalendarEvent, dayDate: string) => {
  const tasks = event.eventTasks
  if (!tasks || tasks.length === 0) return { visible: 0, remaining: 0, eventHeight: 0 }

  const { start, end } = getCurrentEventTimes(event)
  const dayStart = dayjs(dayDate).startOf('day')
  let startMinutes = start.diff(dayStart, 'minute')
  const duration = end.diff(start, 'minute')
  if (props.compactMode && startMinutes < 7 * 60) startMinutes = 7 * 60
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

const canShowProgressBar = (event: CalendarEvent, dayDate: string): boolean => {
  const info = getVisibleTaskInfo(event, dayDate)
  if (info.remaining > 0 || !event.eventTasks?.length || event.eventTasks.length < 5) return false
  const taskHeight = TASK_H + TASK_GAP
  const allTasksHeight = event.eventTasks.length * taskHeight - TASK_GAP
  let usedHeight = EVENT_PADDING + TITLE_H + TIME_H
  if (event.description) usedHeight += DESC_H
  usedHeight += allTasksHeight + MORE_H
  return info.eventHeight - usedHeight >= PROGRESS_BAR_H
}

const canShowAddTask = (event: CalendarEvent, dayDate: string): boolean => {
  const info = getVisibleTaskInfo(event, dayDate)
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
  nextTick(() => titleInputRef.value?.focus())
}

const saveTitle = (event: CalendarEvent) => {
  const val = editingTitleValue.value.trim()
  if (val && val !== event.title) {
    emit('event-update', { event, changes: { title: val } })
  }
  editingTitleEventId.value = null
}

const cancelTitleEdit = () => {
  editingTitleEventId.value = null
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

const toggleTagPicker = (event: CalendarEvent) => {
  tagPickerEventId.value = tagPickerEventId.value === event.id ? null : event.id
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

// Current time for the red line
const currentTime = ref(dayjs())
let timeInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  // Update time every minute
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

// Calculate the position of the current time line
const currentTimeLineStyle = computed(() => {
  const hours = currentTime.value.hour()
  const minutes = currentTime.value.minute()
  
  // Calculate total minutes from start of day (or 7:00 for compact mode)
  const startHour = props.compactMode ? 7 : 0
  const totalMinutes = (hours - startHour) * 60 + minutes
  
  const top = (totalMinutes / 60) * props.hourHeight

  return {
    top: `${top}px`
  }
})

// Check if current day is today
const isCurrentDay = (day: WeekDay) => {
  return dayjs(day.date).isSame(dayjs(), 'day')
}

const hours = computed(() => {
  if (props.compactMode) {
    return Array.from({ length: 17 }, (_, i) => i + 7) // 7:00 to 23:00
  }
  return Array.from({ length: 24 }, (_, i) => i) // 0:00 to 23:00
})

const calendarHeight = computed(() => {
  const totalHours = props.compactMode ? 17 : 24
  return totalHours * props.hourHeight
})

const getEventsForDay = (date: string) => {
  return props.events.filter(event => {
    const eventDate = dayjs(event.start).format('YYYY-MM-DD')
    return eventDate === date
  })
}

const getEventStyle = (event: CalendarEvent, dayDate: string) => {
  const start = isResizing(event.id) && resizeNewStart.value ? resizeNewStart.value : dayjs(event.start)
  const end = isResizing(event.id) && resizeNewEnd.value ? resizeNewEnd.value : dayjs(event.end)
  const dayStart = dayjs(dayDate).startOf('day')

  let startMinutes = start.diff(dayStart, 'minute')
  const duration = end.diff(start, 'minute')

  // Используем цвет события или дефолтный серый цвет
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

  // В компактном режиме (7-24): события раньше 7:00 показываем с 7:00
  // События позже 23:00 скрываем
  if (props.compactMode) {
    if (startMinutes < 7 * 60) {
      // Событие начинается до 7:00 - показываем с 7:00
      startMinutes = 7 * 60
    } else if (startMinutes >= 24 * 60) {
      // Событие начинается после полуночи - скрываем
      return { display: 'none' }
    }
    
    const offsetMinutes = 7 * 60
    const top = ((startMinutes - offsetMinutes) / 60) * props.hourHeight
    const height = Math.max((duration / 60) * props.hourHeight, 30)

    const maxTop = 17 * props.hourHeight
    const clampedTop = Math.max(0, Math.min(top, maxTop))
    const clampedHeight = Math.min(height, maxTop - clampedTop)

    if (clampedTop >= maxTop || clampedHeight <= 0) {
      return { display: 'none' }
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

  // Не компактный режим (0-24)
  const top = (startMinutes / 60) * props.hourHeight
  const height = Math.max((duration / 60) * props.hourHeight, 30)

  const maxTop = 24 * props.hourHeight
  const clampedTop = Math.max(0, Math.min(top, maxTop))
  const clampedHeight = Math.min(height, maxTop - clampedTop)

  if (clampedTop >= maxTop || clampedHeight <= 0) {
    return { display: 'none' }
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

const formatTime = (hour: number) => {
  return `${hour.toString().padStart(2, '0')}:00`
}

const formatEventTime = (event: CalendarEvent) => {
  const start = isResizing(event.id) && resizeNewStart.value ? resizeNewStart.value : dayjs(event.start)
  const end = isResizing(event.id) && resizeNewEnd.value ? resizeNewEnd.value : dayjs(event.end)
  return `${start.format('HH:mm')} - ${end.format('HH:mm')}`
}

// ========== Drag-to-create selection ==========
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

const addMouseListeners = () => {
  const onMove = (e: MouseEvent) => {
    if (!isDragging.value) return
    hasMoved.value = true

    const dayEl = (e.target as HTMLElement).closest('.day-column') as HTMLElement
    if (!dayEl) return

    const rect = dayEl.getBoundingClientRect()
    const currentY = Math.max(0, Math.min(e.clientY - rect.top, rect.height - 1))
    const dayDate = dayEl.dataset.dayDate || selStartDay

    selDay.value = dayDate
    selTop.value = Math.min(selStartY, currentY)
    selHeight.value = Math.abs(currentY - selStartY)
  }

  const onUp = (e: MouseEvent) => {
    if (!isDragging.value) return
    isDragging.value = false
    removeListeners()

    if (!hasMoved.value) {
      // Just a click — emit day-click as before
      selDay.value = ''
      selTop.value = 0
      selHeight.value = 0

      const dayEl = (e.target as HTMLElement).closest('.day-column') as HTMLElement
      if (dayEl) {
        const rect = dayEl.getBoundingClientRect()
        const clickY = e.clientY - rect.top
        const slotIndex = Math.floor(clickY / props.hourHeight)
        const rawMinutes = Math.floor((clickY % props.hourHeight) / props.hourHeight * 60)
        const minutes = Math.round(rawMinutes / 10) * 10
        const hour = props.compactMode ? slotIndex + 7 : slotIndex
        const dayData = props.weekDays.find(d => d.date === selStartDay)
        if (dayData) {
          const clickedDateTime = dayData.fullDate.hour(hour).minute(minutes)
          emit('day-click', { day: dayData, dateTime: clickedDateTime })
        }
      }
      return
    }

    // Selection complete — show input
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

const startSelection = (event: MouseEvent, day: WeekDay) => {
  // Ignore clicks on event blocks
  if ((event.target as HTMLElement).closest('.event-block')) return

  const dayEl = (event.currentTarget as HTMLElement)
  const rect = dayEl.getBoundingClientRect()
  selStartY = Math.max(0, Math.min(event.clientY - rect.top, rect.height - 1))
  selStartDay = day.date

  isDragging.value = true
  hasMoved.value = false
  showCreateInput.value = false
  createTitle.value = ''
  selDay.value = day.date
  selTop.value = selStartY
  selHeight.value = 0

  addMouseListeners()
}

const getTimeFromPixel = (pixelY: number): { hour: number; minute: number } => {
  const slotIndex = Math.floor(pixelY / props.hourHeight)
  const offsetMin = Math.round(((pixelY % props.hourHeight) / props.hourHeight) * 60 / 10) * 10
  const hour = props.compactMode ? slotIndex + 7 : slotIndex
  return { hour, minute: offsetMin }
}

const createEvent = () => {
  if (!createTitle.value.trim()) {
    cancelSelection()
    return
  }

  const startTime = getTimeFromPixel(selTop.value)
  const endTime = getTimeFromPixel(selTop.value + selHeight.value)

  // Ensure minimum 30 min duration, and end after start
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
    date: selDay.value,
    startTime: fmt(startTime.hour, startTime.minute),
    endTime: fmt(endHour, endMin),
    title: createTitle.value.trim()
  })

  cancelSelection()
}

const cancelSelection = () => {
  selDay.value = ''
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
</script>

<style scoped>
.week-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  box-sizing: border-box;
}

.calendar-grid {
  flex: 1;
  display: flex;
  position: relative;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  box-sizing: border-box;
  transition: min-height 0.3s ease;
}

.time-column {
  width: 60px;
  border-right: 1px solid #33333357;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  position: sticky;
  left: 0;
  background-color: #050505;
  z-index: 5;
  box-sizing: border-box;
  min-height: 100%;
}

.time-slot {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 5px;
  font-size: 16px;
  color: #6b6b6b;
  font-weight: bold;
  border-bottom: 1px solid #33333357;
  box-sizing: border-box;
  flex-shrink: 0;
}

.days-container {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  flex: 1;
  position: relative;
  box-sizing: border-box;
  transition: min-height 0.3s ease;
}

.day-column {
  border-right: 1px solid #33333357;
  position: relative;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  transition: min-height 0.3s ease;
}

.hour-slot {
  border-bottom: 1px solid #33333357;
  flex-shrink: 0;
}

.event-block {
  position: absolute;
  left: 2px;
  right: 2px;
  border-radius: 8px;
  padding: 5px 8px;
  cursor: pointer;
  overflow: hidden;
  z-index: 10;
  transition: opacity 0.2s;
  display: flex;
  min-height: 30px;
  color: var(--event-text-color, #ffffff);
}

.event-block:hover {
  opacity: 0.9;
}

.event-block.is-resizing {
  transition: top 0.08s ease, height 0.08s ease;
}

.event-block.dragging {
  cursor: grabbing;
  z-index: 100;
}

/* Drag over state for day column */
.day-column.drag-over {
  background-color: rgba(200, 200, 200, 0.15);
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
  overflow: hidden;
  pointer-events: none;
}

.event-content * {
  pointer-events: none;
}

.event-time {
  font-size: 16px;
  color: var(--event-text-muted, rgba(255, 255, 255, 0.8));
  margin-bottom: 2px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.event-time-icon {
  width: 16px;
  height: 16px;
  filter: var(--event-icon-filter, none);
}

.event-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  gap: 6px;
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

.event-tag-icon {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  filter: var(--event-icon-filter, none);
}

.event-description {
  font-size: 14px;
  color: var(--event-text-muted, rgba(255, 255, 255, 0.8));
  margin-top: 3px;
  line-height: 1.3;
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
  font-size: 13px;
  line-height: 1;
}

.tasks-count {
  color: var(--event-text-muted, rgba(255, 255, 255, 0.8));
  font-size: 11px;
  font-weight: 500;
}

.event-tasks-inline {
  margin-top: 3px;
}

.event-task-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  margin-top: 2px;
  cursor: pointer;
  font-size: 14px;
  line-height: 1.3;
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
  width: 12px;
  height: 12px;
  border: 1px solid #888;
  border-radius: 3px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: #4ade80;
}

.event-task-checkbox.checked {
  border-color: #4ade80;
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
  background: #4ade80;
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

.event-location {
  font-size: 11px;
  color: var(--event-text-muted, rgba(255, 255, 255, 0.7));
  margin-top: 2px;
}

/* Event Star Button */
.event-star-btn {
  position: absolute;
  top: 15px;
  right: 6px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  font-size: 20px;
  color: #888;
  z-index: 14;
  opacity: 0;
  transition: opacity 0.2s, top 0.2s, transform 0.2s;
  pointer-events: auto;
  line-height: 1;
}

.event-star-btn.is-important {
  opacity: 1;
  color: #f59e0b;
}

.event-block:hover .event-star-btn {
  opacity: 1;
}

.event-block:hover .event-star-btn.is-important {
  top: 15px;
  opacity: 1;
}

.event-block:not(:hover) .event-star-btn.is-important {
  top: 4px;
}

.event-star-btn:hover {
  opacity: 0.8 !important;
  transform: scale(1.2);
}

/* Event Menu Button */
.event-menu-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  opacity: 0;
  pointer-events: auto;
  transition: opacity 0.2s;
  z-index: 15;
}

.event-block:hover .event-menu-btn {
  opacity: 1;
}

.event-menu-btn:hover {
  opacity: 0.8 !important;
}

.event-menu-btn img {
  display: block;
  width: 20px;
  height: auto;
}

/* Event Quick Add Button */
.event-quick-add-btn {
  position: absolute;
  top: 4px;
  right: 28px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px 6px;
  font-size: 18px;
  font-weight: 600;
  color: #888;
  opacity: 0;
  pointer-events: auto;
  transition: opacity 0.2s, transform 0.2s, color 0.2s;
  z-index: 15;
  line-height: 1;
}

.event-block:hover .event-quick-add-btn {
  opacity: 1;
}

.event-quick-add-btn:hover {
  opacity: 0.8 !important;
  transform: scale(1.3);
  color: #4ade80;
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

.event-title {
  pointer-events: auto;
}

.event-title-text {
  cursor: text;
  pointer-events: auto;
}

.event-title-input,
.event-desc-input {
  pointer-events: auto;
}

.event-description {
  pointer-events: auto;
}

.event-title-input,
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
</style>
