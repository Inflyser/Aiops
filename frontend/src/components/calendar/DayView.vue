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
            <!-- Sleep Events Section -->
            <div v-if="props.sleepMode && sleepEvents.length > 0" class="sleep-events" style="top: 0">
              <div v-for="event in sleepEvents" :key="'sleep-' + event.id" class="sleep-event" @click.stop="$emit('open-event', event)">
                <span class="sleep-event-time">{{ dayjs(event.start).format('HH:mm') }}-{{ dayjs(event.end).format('HH:mm') }}</span>
                <span class="sleep-event-title">{{ event.title }}</span>
              </div>
            </div>
            <div
              v-for="event in visibleEvents"
              :key="event.id"
              class="day-event"
            :class="{ 'dragging': draggedEvent?.id === event.id, 'is-resizing': isResizing(event.id) }"
            :style="getEventStyle(event)"
            :data-event-id="event.id"
            draggable="true"
            @click.stop="handleEventClick($event, event)"
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
              draggable="false"
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
                  />
                </template>
                <template v-if="editingTitleEventId === event.id">
                  <input
                    ref="titleInputRef"
                    v-model="editingTitleValue"
                    class="event-title-input"
                    draggable="false"
                    @mousedown="onTitleInputMouseDown($event, event)"
                    @keydown.enter="saveTitle(event)"
                    @keydown.escape="cancelTitleEdit"
                    @blur="saveTitle(event)"
                  />
                </template>
                <template v-else>
                  <span class="event-title-text" data-edit-title>{{ event.title }}</span>
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
                <img src="@/assets/icon-clock.svg" alt="clock" class="event-time-icon" draggable="false" />
                {{ formatEventTime(event) }}
              </div>
              <div v-if="event.description" class="event-description" draggable="false">
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
                        <span v-if="t.completed" class="checkmark"></span>
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
              draggable="false"
              :class="{ 'is-important': event.is_important }"
              @click.stop="$emit('event-toggle-important', event)"
              :title="event.is_important ? 'Убрать важность' : 'Отметить как важное'"
            >
              {{ event.is_important ? '★' : '☆' }}
            </button>
            <button
              v-show="editingTitleEventId !== event.id"
              class="event-quick-add-btn"
              draggable="false"
              @click.stop="toggleQuickAdd(event)"
              title="Добавить задачу"
            >+</button>
            <div
              class="event-resize-handle event-resize-handle--bottom"
              draggable="false"
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
import { computed, ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import { useTagsStore } from '@/stores/tags'
import { useCalendarTime } from '@/composables/useCalendarTime'
import { useEventResize } from '@/composables/useEventResize'
import { useEventTasks } from '@/composables/useEventTasks'
import { useEventDrag } from '@/composables/useEventDrag'
import { useDragToCreate } from '@/composables/useDragToCreate'

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

const scrollContainerRef = ref<HTMLElement | null>(null)

// --- Composables ---

const {
  hours,
  calendarHeight,
  sleepGaps,
  toVisibleMinutes,
  getEventStyle: getEventStyleRaw,
  formatEventTime: formatEventTimeRaw
} = useCalendarTime({
  dayStartHour: computed(() => props.dayStartHour),
  dayEndHour: computed(() => props.dayEndHour),
  sleepMode: computed(() => props.sleepMode),
  sleepStartHour: computed(() => props.sleepStartHour),
  sleepEndHour: computed(() => props.sleepEndHour),
  hourHeight: computed(() => props.hourHeight),
  eventAccentMode: computed(() => props.eventAccentMode)
})

const {
  resizeNewStart,
  resizeNewEnd,
  isResizing,
  startResize: startResizeRaw,
  cleanupResize
} = useEventResize(computed(() => props.hourHeight))

const startResize = (e: MouseEvent, event: any, direction: 'bottom' | 'top') => {
  startResizeRaw(e, event, direction, (data) => ee('event-drop', data))
}

const DAY_TASK_LAYOUT = {
  EVENT_PADDING: 16, TITLE_H: 26, TIME_H: 24, DESC_H: 28,
  TASK_H: 26, TASK_GAP: 2, PROGRESS_BAR_H: 14, ADD_TASK_H: 28, MORE_H: 22
}

const {
  hoveredEventId,
  addTaskTitle,
  activeAddTaskEventId,
  quickAddEventId,
  quickAddTitle,
  editingTitleEventId,
  editingTitleValue,
  editingDescEventId,
  editingDescValue,
  tagPickerEventId,
  titleInputRef,
  getTaskWord,
  getVisibleTaskInfo: getVisibleTaskInfoRaw,
  canShowProgressBar: canShowProgressBarRaw,
  showTaskBadge: showTaskBadgeRaw,
  canShowAddTask: canShowAddTaskRaw,
  getProgressPercent,
  toggleTaskInline,
  submitAddTask: submitAddTaskRaw,
  cancelAddTask,
  handleAddTaskBlur,
  toggleQuickAdd,
  submitQuickAdd,
  cancelQuickAdd,
  saveTitle: saveTitleRaw,
  cancelTitleEdit,
  onTitleInputMouseDown,
  startEditDesc,
  saveDesc: saveDescRaw,
  cancelDescEdit,
  selectTag: selectTagRaw,
  handleEventClick: handleEventClickRaw
} = useEventTasks(computed(() => props.hourHeight), DAY_TASK_LAYOUT)

const {
  draggedEvent,
  isAltPressed,
  handleDragStart: handleDragStartRaw,
  handleDrag,
  handleDragEnd,
  handleTaskDragOver,
  handleTaskDrop: handleTaskDropRaw
} = useEventDrag({
  hourHeight: computed(() => props.hourHeight),
  dayStartHour: computed(() => props.dayStartHour),
  sleepMode: computed(() => props.sleepMode),
  sleepStartHour: computed(() => props.sleepStartHour),
  sleepEndHour: computed(() => props.sleepEndHour)
})

const {
  selTop,
  selHeight,
  showCreateInput,
  createTitle,
  createTitleInput,
  startSelectionDay,
  createEvent: createEventRaw,
  cancelSelection,
  submitCreate: submitCreateRaw,
  addMouseListenersDay,
  cleanupCreate
} = useDragToCreate({
  hourHeight: computed(() => props.hourHeight),
  dayStartHour: computed(() => props.dayStartHour),
  sleepMode: computed(() => props.sleepMode),
  sleepStartHour: computed(() => props.sleepStartHour),
  sleepEndHour: computed(() => props.sleepEndHour)
})

// --- Adapter functions ---

const ee = (name: string, ...args: any[]) => (emit as any)(name, ...args)

const getEventStyle = (event: CalendarEvent) =>
  getEventStyleRaw(event, props.currentDay.startOf('day'), isResizing, resizeNewStart, resizeNewEnd, focusMode.value)

const formatEventTime = (event: CalendarEvent) =>
  formatEventTimeRaw(event, isResizing, resizeNewStart, resizeNewEnd)

const getVisibleTaskInfo = (event: CalendarEvent) =>
  getVisibleTaskInfoRaw(event, isResizing, resizeNewStart, resizeNewEnd)

const canShowProgressBar = (event: CalendarEvent) =>
  canShowProgressBarRaw(event, isResizing, resizeNewStart, resizeNewEnd)

const showTaskBadge = (event: CalendarEvent) =>
  showTaskBadgeRaw(event, isResizing, resizeNewStart, resizeNewEnd)

const canShowAddTask = (event: CalendarEvent) =>
  canShowAddTaskRaw(event, isResizing, resizeNewStart, resizeNewEnd)

const submitAddTask = (event: CalendarEvent) =>
  submitAddTaskRaw(event, ee)

const saveTitle = (event: CalendarEvent) =>
  saveTitleRaw(event, ee)

const saveDesc = (event: CalendarEvent) =>
  saveDescRaw(event, ee)

const selectTag = (event: CalendarEvent, tagId: string | null) =>
  selectTagRaw(event as any, tagId, tagsStore.tags, ee)

const handleEventClick = (e: MouseEvent, event?: CalendarEvent) =>
  handleEventClickRaw(e, event, ee)

// Drag wrappers (DayView uses .day-event selector and .day-scroll-container grid)
const handleDragStart = (e: DragEvent, event: CalendarEvent) =>
  handleDragStartRaw(e, event, '.day-event')

const handleTaskDrop = (e: DragEvent) =>
  handleTaskDropRaw(e, props.events as any, ee)

// DayView-specific drag-to-create
const startSelection = (e: MouseEvent) =>
  startSelectionDay(e, scrollContainerRef)

const createEvent = () =>
  createEventRaw(ee, props.currentDay.format('YYYY-MM-DD'))

const submitCreate = () =>
  submitCreateRaw(ee, props.currentDay.format('YYYY-MM-DD'))

// --- DayView-specific logic ---

const sleepEvents = computed(() => {
  if (!props.sleepMode) return []
  const sleepStartMin = props.sleepStartHour * 60
  const sleepEndMin = props.sleepEndHour * 60
  return props.events.filter(event => {
    const start = dayjs(event.start)
    const dayStart = props.currentDay.startOf('day')
    const startMinutes = start.diff(dayStart, 'minute')
    const duration = dayjs(event.end).diff(start, 'minute')
    return startMinutes >= sleepStartMin && (startMinutes + duration) <= sleepEndMin
  })
})

const visibleEvents = computed(() => {
  if (!props.sleepMode) return props.events
  const sleepStartMin = props.sleepStartHour * 60
  const sleepEndMin = props.sleepEndHour * 60
  return props.events.filter(event => {
    const start = dayjs(event.start)
    const dayStart = props.currentDay.startOf('day')
    const startMinutes = start.diff(dayStart, 'minute')
    const duration = dayjs(event.end).diff(start, 'minute')
    return !(startMinutes >= sleepStartMin && (startMinutes + duration) <= sleepEndMin)
  })
})

const handleRowClick = (hour: number) => {
  emit('hour-click', { hour, date: props.currentDay })
}

// Grid-level drag over/drop for event movement
const handleGridDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = draggedEvent.value ? 'move' : 'copy'
  }
  const grid = scrollContainerRef.value
  if (!grid) return
  const rect = grid.getBoundingClientRect()
  const relativeY = event.clientY - rect.top

  if (relativeY < 60) {
    grid.scrollTop = Math.max(0, grid.scrollTop - 15)
  } else if (relativeY > rect.height - 60) {
    grid.scrollTop += 15
  }
}

const handleGridDrop = (event: DragEvent) => {
  event.preventDefault()

  const grid = scrollContainerRef.value
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

// Current time for red line
const currentTime = ref(dayjs())
let timeInterval: ReturnType<typeof setInterval> | null = null

const isCurrentDay = () => {
  return dayjs().isSame(props.currentDay, 'day')
}

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

// Lifecycle
onMounted(() => {
  addMouseListenersDay(
    (_data) => {}, // unused
    scrollContainerRef,
    props.currentDay
  )
  timeInterval = setInterval(() => {
    currentTime.value = dayjs()
  }, 60000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  cleanupCreate()
  cleanupResize()
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
  font-size: 30px;
  font-weight: bold;
  margin: 0;
  text-transform: capitalize;
}

.day-date {
  font-size: 17px;
  color: #888;
  margin: 3px 0 0;
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
  font-size: 26px;
  cursor: pointer;
  font-weight: bold;
  padding: 4px 12px;
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
  user-select: none;
  -webkit-user-select: none;
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
  pointer-events: none;
  min-width: 0;
}

.event-tag-icon-wrapper,
.event-tag-icon {
  flex-shrink: 0;
  margin-top: 3px;
  pointer-events: none;
}

.event-tag-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  filter: var(--event-icon-filter, none);
  pointer-events: none;
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
  gap: 8px;
  padding: 2px 6px;
  margin-top: 2px;
  cursor: pointer;
  font-size: 17px;
  line-height: 1.4;
  border-radius: 4px;
  border: 1px solid transparent;
}
.event-task-item:hover {
  border-color: #555;
  background: rgba(0, 0, 0, 0.3);
}

.event-task-checkbox {
  pointer-events: auto;
}

.event-task-item:first-child {
  margin-top: 0;
}

.event-task-checkbox {
  width: 14px;
  height: 14px;
  border: 2px solid var(--event-text-color, #ffffff);
  border-radius: 3px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: var(--event-text-color, #ffffff);
}
.event-task-checkbox.checked {
  border-color: var(--event-text-color, #ffffff);
  background: var(--event-text-color, #ffffff);
}
.event-task-checkbox.checked .checkmark {
  display: block;
  width: 5px;
  height: 9px;
  border: solid var(--event-color, #333);
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  margin-top: -3px;
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
  height: 6px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
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
  color: var(--event-text-muted, rgba(255, 255, 255, 0.7));
  z-index: 14;
  opacity: 0;
  transition: opacity 0.2s, transform 0.2s;
  pointer-events: auto;
  line-height: 1;
}

.event-star-btn.is-important {
  opacity: 1;
  color: var(--event-text-color, #ffffff);
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
  color: var(--event-text-muted, rgba(255, 255, 255, 0.7));
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
  color: var(--event-text-color, #ffffff);
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

.event-title-text {
  cursor: text;
  pointer-events: none;
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
  pointer-events: auto;
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
