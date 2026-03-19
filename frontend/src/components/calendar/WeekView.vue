<template>
  <div class="week-view">
    <!-- Calendar Grid -->
    <div class="calendar-grid">
      <div class="time-column">
        <div 
          v-for="hour in hours" 
          :key="hour"
          class="time-slot"
        >
          {{ formatTime(hour) }}
        </div>
      </div>

      <div class="days-container" :style="{ minHeight: calendarHeight + 'px', width: inboxPanelOpen ? 'calc(100% - 400px)' : '100%' }">
        <div
          v-for="day in weekDays"
          :key="day.date"
          class="day-column"
          :class="{
            'current-day': isCurrentDay(day),
            'drag-over': dragOverDay === day.date
          }"
          :style="{ minHeight: calendarHeight + 'px' }"
          @click="handleDayClick($event, day)"
          @dragover="handleDragOver($event, day)"
          @dragleave="handleDragLeave"
          @drop="handleDrop($event, day)"
        >
          <div 
            v-for="hour in hours" 
            :key="hour"
            class="hour-slot"
          ></div>
          <div
            v-for="event in getEventsForDay(day.date)"
            :key="event.id"
            class="event-block"
            :class="{ 'dragging': draggedEvent?.id === event.id, 'bounce': event.bouncing }"
            :style="getEventStyle(event, day.date)"
            :data-event-id="event.id"
            draggable="true"
            @click.stop="handleEventClick(event)"
            @dragstart="handleDragStart($event, event)"
            @dragend="handleDragEnd"
            @dragover="handleTaskDragOver($event)"
            @drop="handleTaskDrop($event, day)"
          >
            <div class="event-indicator"></div>
            <div class="event-content">
              <div class="event-title">
                <img 
                  v-if="event.tagIcon" 
                  :src="getTagIconPath(event.tagIcon)" 
                  class="event-tag-icon" 
                />
                {{ event.title }}
              </div>
              <div class="event-time">
                <img src="@/assets/icon-clock.svg" alt="clock" class="event-time-icon" />
                {{ formatEventTime(event) }}
              </div>
              <div v-if="event.description" class="event-description">{{ event.description }}</div>
              <div v-if="event.task_count && event.task_count > 0" class="event-tasks-indicator" @click.stop="handleEventClick(event)">
                <span class="tasks-icon">•</span>
                <span class="tasks-count">{{ event.task_count }} {{ getTaskWord(event.task_count) }}</span>
              </div>
            </div>
            <button 
              class="event-menu-btn"
              @click.stop="$emit('event-move-to-next-week', event)"
              title="Перенести на следующую неделю"
            >
              <img src="@/assets/three-point.svg" alt="menu" />
            </button>
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
import { computed, ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'

dayjs.locale('ru')

const iconFiles: Record<string, string> = import.meta.glob('@/assets/icon/*.svg', { query: '?url', import: 'default', eager: true }) as any

const getTagIconPath = (iconName: string): string => {
  // import.meta.glob возвращает ключи в формате /src/assets/icon/filename.svg
  for (const [path, url] of Object.entries(iconFiles)) {
    if (path.includes(`/${iconName}.svg`) || path.includes(`/${iconName}`)) {
      return url
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

interface CalendarEvent {
  id: string | number
  title: string
  description?: string
  start: string
  end: string
  priority?: string
  color?: string
  bouncing?: boolean
  tagIcon?: string
  task_ids?: string[]
  task_count?: number
}

const props = defineProps<{
  weekDays: WeekDay[]
  events: CalendarEvent[]
  compactMode: boolean
  inboxPanelOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'day-click', data: { day: WeekDay; dateTime: dayjs.Dayjs }): void
  (e: 'open-event', event: CalendarEvent): void
  (e: 'open-event-tasks', event: CalendarEvent): void
  (e: 'event-drop', data: { event: CalendarEvent; newDate: string; newStart: string; newEnd: string }): void
  (e: 'event-copy', data: { event: CalendarEvent; newDate: string; newStart: string; newEnd: string }): void
  (e: 'event-move-to-next-week', event: CalendarEvent): void
  (e: 'task-drop-to-event', data: { task: any; event: CalendarEvent }): void
}>()

// Drag and drop state
const draggedEvent = ref<CalendarEvent | null>(null)
const dragOverDay = ref<string | null>(null)

const isAltPressed = ref(false)

// Double click detection
const lastClickEvent = ref<{ event: CalendarEvent; time: number } | null>(null)
const clickTimeout = ref<ReturnType<typeof setTimeout> | null>(null)
const DOUBLE_CLICK_DELAY = 300 // ms

const handleDragStart = (event: DragEvent, calendarEvent: CalendarEvent) => {
  draggedEvent.value = calendarEvent
  isAltPressed.value = event.altKey // Проверяем Alt при начале перетаскивания
  
  if (event.dataTransfer) {
    // Если зажат Alt - это копирование, иначе - перемещение
    event.dataTransfer.effectAllowed = event.altKey ? 'copy' : 'move'
    event.dataTransfer.setData('text/plain', JSON.stringify(calendarEvent))
    event.dataTransfer.setData('application/x-alt-drag', String(event.altKey))
  }
}

const handleDragEnd = () => {
  draggedEvent.value = null
  dragOverDay.value = null
  isAltPressed.value = false
}

const handleDragOver = (event: DragEvent, day: WeekDay) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = event.altKey ? 'copy' : 'move'
  }
  dragOverDay.value = day.date
}

const handleDragLeave = () => {
  dragOverDay.value = null
}

const handleDrop = (event: DragEvent, day: WeekDay) => {
  event.preventDefault()
  dragOverDay.value = null
  
  if (draggedEvent.value) {
    const eventData = draggedEvent.value
    const isCopy = event.altKey || isAltPressed.value // Проверяем Alt при сбросе
    
    // Calculate the time offset from the original start
    const originalStart = dayjs(eventData.start)
    const originalEnd = dayjs(eventData.end)
    const duration = originalEnd.diff(originalStart, 'minute')
    
    // Get the time from the drop position
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
    const dropY = event.clientY - rect.top
    const slotIndex = Math.floor(dropY / 120)
    const rawMinutes = Math.floor((dropY % 120) / 120 * 60)
    const minutes = Math.round(rawMinutes / 10) * 10 // Кратно 10
    
    const hour = props.compactMode ? slotIndex + 7 : slotIndex
    
    // Calculate new start and end times
    const newStart = day.fullDate.hour(hour).minute(minutes)
    const newEnd = newStart.add(duration, 'minute')
    
    // Если Alt зажат - это копирование, иначе - перемещение
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
    const taskData = JSON.parse(event.dataTransfer?.getData('text/plain') || '{}')
    
    // Находим событие, над которым была сброшена задача
    const targetElement = event.target as HTMLElement
    const eventBlock = targetElement.closest('.event-block')
    
    if (eventBlock) {
      // Находим событие по его ID
      const eventId = eventBlock.getAttribute('data-event-id')
      const targetEvent = props.events.find(e => String(e.id) === eventId)
      
      if (targetEvent) {
        emit('task-drop-to-event', { task: taskData, event: targetEvent })
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

// Handle event click with double click detection
const handleEventClick = (event: CalendarEvent) => {
  const now = Date.now()
  
  // Clear previous timeout if exists
  if (clickTimeout.value) {
    clearTimeout(clickTimeout.value)
    clickTimeout.value = null
  }
  
  // Check if this is a double click
  if (lastClickEvent.value &&
      lastClickEvent.value.event.id === event.id &&
      now - lastClickEvent.value.time < DOUBLE_CLICK_DELAY) {
    // Double click detected - open event modal for editing
    emit('open-event', event)
    lastClickEvent.value = null
  } else {
    // Store click info and wait to see if it's a single or double click
    lastClickEvent.value = { event, time: now }
    
    // Set timeout to handle single click
    clickTimeout.value = setTimeout(() => {
      // Single click - check if event has tasks
      if (event.task_count && event.task_count > 0) {
        emit('open-event-tasks', event)
      }
      lastClickEvent.value = null
      clickTimeout.value = null
    }, DOUBLE_CLICK_DELAY)
  }
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
})

// Calculate the position of the current time line
const currentTimeLineStyle = computed(() => {
  const hours = currentTime.value.hour()
  const minutes = currentTime.value.minute()
  
  // Calculate total minutes from start of day (or 7:00 for compact mode)
  const startHour = props.compactMode ? 7 : 0
  const totalMinutes = (hours - startHour) * 60 + minutes
  
  // Convert to pixels (120px per hour)
  const top = (totalMinutes / 60) * 120
  
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
  return totalHours * 120
})

const getEventsForDay = (date: string) => {
  return props.events.filter(event => {
    const eventDate = dayjs(event.start).format('YYYY-MM-DD')
    return eventDate === date
  })
}

const getEventStyle = (event: CalendarEvent, dayDate: string) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  const dayStart = dayjs(dayDate).startOf('day')

  let startMinutes = start.diff(dayStart, 'minute')
  const duration = end.diff(start, 'minute')

  // Используем цвет события или дефолтный серый цвет
  const eventColor = event.color || '#4a5568'

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
    
    // В компактном режиме сетка начинается с 7:00, поэтому нужно вычесть 7 часов
    // чтобы событие в 10:00 было на правильной позиции (3-й слот, а не 10-й)
    const offsetMinutes = 7 * 60
    const top = ((startMinutes - offsetMinutes) / 60) * 120
    const height = Math.max((duration / 60) * 120, 30)

    const maxTop = 17 * 120 // 17 часов в компактном режиме
    const clampedTop = Math.max(0, Math.min(top, maxTop))
    const clampedHeight = Math.min(height, maxTop - clampedTop)

    if (clampedTop >= maxTop || clampedHeight <= 0) {
      return { display: 'none' }
    }

    return {
      top: `${clampedTop}px`,
      height: `${clampedHeight}px`,
      backgroundColor: eventColor,
      position: 'absolute' as const,
      left: '2px',
      right: '2px',
      zIndex: 10
    }
  }

  // Не компактный режим (0-24)
  const top = (startMinutes / 60) * 120
  const height = Math.max((duration / 60) * 120, 30)

  const maxTop = 24 * 120
  const clampedTop = Math.max(0, Math.min(top, maxTop))
  const clampedHeight = Math.min(height, maxTop - clampedTop)

  if (clampedTop >= maxTop || clampedHeight <= 0) {
    return { display: 'none' }
  }

  return {
    top: `${clampedTop}px`,
    height: `${clampedHeight}px`,
    backgroundColor: eventColor,
    position: 'absolute' as const,
    left: '2px',
    right: '2px',
    zIndex: 10
  }
}

const formatTime = (hour: number) => {
  return `${hour.toString().padStart(2, '0')}:00`
}

const formatEventTime = (event: CalendarEvent) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  return `${start.format('HH:mm')} - ${end.format('HH:mm')}`
}

const handleDayClick = (event: MouseEvent, day: WeekDay) => {
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const clickY = event.clientY - rect.top
  const slotIndex = Math.floor(clickY / 120)
  const rawMinutes = Math.floor((clickY % 120) / 120 * 60)
  const minutes = Math.round(rawMinutes / 10) * 10 // Кратно 10
  
  // В компактном режиме слот 0 соответствует 7:00, а не 0:00
  const hour = props.compactMode ? slotIndex + 7 : slotIndex
  
  // Передаём вычисленное время вместе с днём
  const clickedDateTime = day.fullDate.hour(hour).minute(minutes)
  
  emit('day-click', { 
    day, 
    dateTime: clickedDateTime 
  })
}
</script>

<style scoped>
.week-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.calendar-grid {
  flex: 1;
  display: flex;
  position: relative;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.time-column {
  width: 90px;
  border-right: 1px solid #33333357;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  position: sticky;
  left: 0;
  background-color: #050505;
  z-index: 5;
}

.time-slot {
  height: 120px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 5px;
  font-size: 20px;
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
}

.day-column {
  border-right: 1px solid #33333357;
  position: relative;
  display: flex;
  flex-direction: column;
}

.hour-slot {
  height: 120px;
  border-bottom: 1px solid #33333357;
  min-height: 120px;
}

.event-block {
  position: absolute;
  left: 2px;
  right: 2px;
  border-radius: 4px;
  padding: 5px 8px;
  cursor: pointer;
  overflow: hidden;
  z-index: 10;
  transition: opacity 0.2s;
  display: flex;
  min-height: 30px;
}

.event-block:hover {
  opacity: 0.9;
}

.event-block.dragging {
  opacity: 0.5;
  cursor: grabbing;
}

/* Bounce animation for dropped events */
.event-block.bounce {
  animation: bounce-in 0.5s ease-out;
}

@keyframes bounce-in {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  30% {
    transform: scale(1.1);
  }
  50% {
    transform: scale(0.95);
  }
  70% {
    transform: scale(1.03);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Drag over state for day column */
.day-column.drag-over {
  background-color: rgba(74, 85, 104, 0.3);
}

.event-indicator {
  width: 7px;
  border-radius: 6px;
  background-color: #ffffff;
  margin-right: 8px;
  flex-shrink: 0;
  opacity: 0.7;
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
  font-size: 20px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.event-time-icon {
  width: 16px;
  height: 16px;
}

.event-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.event-tag-icon {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
}

.event-description {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
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
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  line-height: 1;
}

.tasks-count {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 500;
}

.event-location {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
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
</style>
