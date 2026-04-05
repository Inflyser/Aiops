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
    
    <div class="day-scroll-container">
      <div class="day-grid">
        <div 
          v-for="hour in hours" 
          :key="hour"
          class="day-hour-row"
        >
          <div class="hour-label">{{ hour.toString().padStart(2, '0') }}:00</div>
          <div class="hour-events" @click="handleRowClick(hour)"></div>
        </div>
        
        <div class="events-container" :style="{ minHeight: calendarHeight + 'px' }">
          <div
            v-for="event in events"
            :key="event.id"
            class="day-event"
            :style="getEventStyle(event)"
            :data-event-id="event.id"
            draggable="true"
            @click.stop="handleEventClick(event)"
            @dragstart="handleDragStart($event, event)"
            @dragend="handleDragEnd"
            @dragover="handleTaskDragOver($event)"
            @drop="handleTaskDrop($event)"
          >
            <div class="event-indicator"></div>
            <div class="event-content">
              <div class="event-title">
                <img
                  v-if="event.tagIcon && getTagIconPath(event.tagIcon)"
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
                <span class="tasks-count">{{ event.completed_task_count || 0 }}/{{ event.task_count }} {{ getTaskWord(event.task_count) }}</span>
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
  task_count?: number
  completed_task_count?: number
}

const props = defineProps<{
  currentDay: dayjs.Dayjs
  events: CalendarEvent[]
  compactMode: boolean
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
}>()

// Double click detection
const lastClickEvent = ref<{ event: CalendarEvent; time: number } | null>(null)
const clickTimeout = ref<ReturnType<typeof setTimeout> | null>(null)
const DOUBLE_CLICK_DELAY = 300 // ms

// Focus mode state
const focusMode = ref(false)

const toggleFocusMode = () => {
  focusMode.value = !focusMode.value
}

// Drag and drop state
const draggedEvent = ref<CalendarEvent | null>(null)
const isAltPressed = ref(false)

// Current time for red line
const currentTime = ref(dayjs())
let timeInterval: ReturnType<typeof setInterval> | null = null

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
  }
}

const handleDragEnd = () => {
  draggedEvent.value = null
  isAltPressed.value = false
}

const handleTaskDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

const handleTaskDrop = (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()
  
  try {
    const droppedData = JSON.parse(event.dataTransfer?.getData('text/plain') || '{}')
    
    if (droppedData.id && droppedData.title) {
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

// Get correct word form for task count
const getTaskWord = (count: number): string => {
  const lastTwo = count % 100
  const lastOne = count % 10
  
  if (lastTwo >= 11 && lastTwo <= 14) return 'задач'
  if (lastOne === 1) return 'задача'
  if (lastOne >= 2 && lastOne <= 4) return 'задачи'
  return 'задач'
}

// Check if current day is today
const isCurrentDay = () => {
  return dayjs().isSame(props.currentDay, 'day')
}

// Calculate the position of the current time line
const currentTimeLineStyle = computed(() => {
  const hours = currentTime.value.hour()
  const minutes = currentTime.value.minute()
  
  const startHour = props.compactMode ? 7 : 0
  const totalMinutes = (hours - startHour) * 60 + minutes
  
  const top = (totalMinutes / 60) * 120
  
  return {
    top: `${top}px`
  }
})

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

const getEventStyle = (event: CalendarEvent) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  const dayStart = props.currentDay.startOf('day')
  
  let startMinutes = start.diff(dayStart, 'minute')
  const duration = end.diff(start, 'minute')
  
  const eventColor = event.color || '#4a5568'
  
  if (props.compactMode) {
    if (startMinutes < 7 * 60) {
      startMinutes = 7 * 60
    } else if (startMinutes >= 24 * 60) {
      return { display: 'none' }
    }
    
    const offsetMinutes = 7 * 60
    const top = ((startMinutes - offsetMinutes) / 60) * 120
    const height = Math.max((duration / 60) * 120, 30)
    
    const maxTop = 17 * 120
    const clampedTop = Math.max(0, Math.min(top, maxTop))
    const clampedHeight = Math.min(height, maxTop - clampedTop)
    
    if (clampedTop >= maxTop || clampedHeight <= 0) {
      return { display: 'none' }
    }
    
    if (focusMode.value) {
      // Focus mode: 25% width, centered
      return {
        top: `${clampedTop}px`,
        height: `${clampedHeight}px`,
        backgroundColor: eventColor,
        position: 'absolute' as const,
        left: '37.5%', // (100% - 25%) / 2
        width: '25%',
        right: 'auto',
        zIndex: 10
      }
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
  
  const top = (startMinutes / 60) * 120
  const height = Math.max((duration / 60) * 120, 30)
  
  const maxTop = 24 * 120
  const clampedTop = Math.max(0, Math.min(top, maxTop))
  const clampedHeight = Math.min(height, maxTop - clampedTop)
  
  if (clampedTop >= maxTop || clampedHeight <= 0) {
    return { display: 'none' }
  }
  
  if (focusMode.value) {
    // Focus mode: 25% width, centered
    return {
      top: `${clampedTop}px`,
      height: `${clampedHeight}px`,
      backgroundColor: eventColor,
      position: 'absolute' as const,
      left: '37.5%', // (100% - 25%) / 2
      width: '25%',
      right: 'auto',
      zIndex: 10
    }
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

const formatEventTime = (event: CalendarEvent) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
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
  background-color: #050505;
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
  font-size: 48px;
  font-weight: bold;
  margin: 0;
  text-transform: capitalize;
}

.day-date {
  font-size: 24px;
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
  color: #ffffff;
  font-size: 28px;
  cursor: pointer;
  font-weight: bold;
  padding: 5px 15px;
}

.today-btn {
  background: #1a1a1a;
  border: 1px solid #333;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 6px;
  transition: background 0.2s;
}

.today-btn:hover {
  background: #2a2a2a;
}

.focus-btn {
  background: #1a1a1a;
  border: 1px solid #333;
  color: #fff;
  font-size: 16px;
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
  min-height: 120px;
  border-bottom: 1px solid #1a1a1a;
}

.hour-label {
  width: 80px;
  padding: 10px;
  font-size: 18px;
  color: #666;
  flex-shrink: 0;
  border-right: 1px solid #1a1a1a;
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
  left: 80px;
  right: 0;
  pointer-events: none;
}

.day-event {
  position: absolute;
  left: 2px;
  right: 2px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  color: white;
  overflow: hidden;
  pointer-events: auto;
  transition: transform 0.1s;
}

.day-event:hover {
  transform: scale(1.02);
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
  font-size: 16px;
  opacity: 0.8;
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-time-icon {
  width: 20px;
  height: 20px;
}

.event-title {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-tag-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  filter: invert(1);
}

.event-description {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
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
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  line-height: 1;
}

.tasks-count {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 600;
}

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

.day-event:hover .event-menu-btn {
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
